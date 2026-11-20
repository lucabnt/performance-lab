"""Protocols, traces, incremental tests and their single-test report."""

import json
from typing import Annotated, Literal

from fastapi import Form, UploadFile

from .access import viewer_allowed
from .analysis import analyze
from .api import TestInput
from .erg import parse_erg
from .fit import decode_fit


def install(app, store, require, download):
    @app.post("/api/v1/protocols")
    def protocol(
        file: UploadFile,
        name: Annotated[str, Form()],
        family: Annotated[str, Form()],
        version: Annotated[str, Form()],
        warmup_s: Annotated[float, Form()] = 600,
        parent_id: Annotated[str, Form()] = "",
        reason: Annotated[str, Form()] = "",
        organization_id: Annotated[str | None, Form()] = None,
    ):
        if organization_id:
            require(organization_id, 'organization')
        raw = file.file.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("ERG troppo grande.")
        if not name.strip() or not family.strip() or not version.strip():
            raise ValueError("Nome, codice e versione sono obbligatori.")
        definition = parse_erg(raw.decode("utf-8-sig"))
        boundaries = {s["start_s"] for s in definition["segments"]} | {definition["duration_s"]}
        if warmup_s not in boundaries or warmup_s == definition["duration_s"]:
            raise ValueError(
                "Il termine del riscaldamento deve coincidere con un confine degli step e lasciare almeno uno step incrementale."
            )
        for s in definition["segments"]:
            s["phase"] = "warmup" if s["end_s"] <= warmup_s else "increment"
        siblings = [
            p
            for p in store.list("protocol")
            if p["family"] == family.strip() and p.get("organization_id") == organization_id
        ]
        if any(p["version"] == version.strip() for p in siblings):
            raise ValueError("Questa versione esiste già. Scegliere un nuovo identificatore.")
        if siblings and not parent_id:
            raise ValueError("Selezionare la versione precedente per documentare l'evoluzione.")
        if parent_id and require(parent_id, "protocol")["family"] != family:
            raise ValueError("La versione precedente appartiene a un'altra famiglia.")
        digest = store.object(raw)
        return store.save(
            "protocol",
            {
                "organization_id": organization_id,
                "name": name.strip(),
                "family": family.strip(),
                "version": version.strip(),
                "parent_id": parent_id or None,
                "reason": reason,
                "definition": definition,
                "objects": [digest],
            },
        )

    @app.post("/api/v1/traces")
    def trace(
        file: UploadFile,
        session_index: Annotated[int | None, Form()] = None,
        duplicate_policy: Annotated[str, Form()] = 'reject',
        correction_reason: Annotated[str, Form()] = '',
    ):
        raw = file.file.read(30_000_001)
        if len(raw) > 30_000_000:
            raise ValueError("FIT oltre il limite di 30 MB.")
        if (file.filename or '').lower().endswith('.csv'):
            from .csv_import import decode_trace_csv

            decoded = decode_trace_csv(raw)
        else:
            decoded = decode_fit(
                raw, session_index=session_index, duplicate_policy=duplicate_policy, correction_reason=correction_reason
            )
        original = store.object(raw)
        normalized = store.object(json.dumps({**decoded, "original_hash": original}, allow_nan=False).encode())
        return {**decoded, "hash": normalized}

    @app.post('/api/v1/traces/inspect')
    def inspect_trace(file: UploadFile):
        raw = file.file.read(30_000_001)
        if len(raw) > 30_000_000:
            raise ValueError('FIT oltre 30 MB.')
        return decode_fit(raw, overview=True)

    @app.post("/api/v1/tests/preview")
    @viewer_allowed
    def preview(data: TestInput):
        athlete = require(data.athlete_id, "athlete")
        protocol = require(data.protocol_id, "protocol")
        if protocol.get("organization_id") and protocol["organization_id"] != athlete["organization_id"]:
            raise ValueError("Protocollo esterno alla società.")
        if protocol.get('test_type') in ('custom', 'sprint', 'wingate15', 'wingate30'):
            raise ValueError('Usare il modulo della famiglia di test selezionata.')
        if not protocol['definition']['segments']:
            raise ValueError(
                'Protocollo senza step: usare l’inserimento manuale oppure creare una versione con carichi.'
            )
        trace = json.loads(store.read_object(data.trace_hash))
        from .observations import enrich

        settings = data.settings.model_dump()
        from .methods import resolve
        from .store import encoded
        import hashlib

        analysis = analyze(
            trace['samples'], protocol['definition'], settings, resolve(store, settings.get('preset_id'))
        )
        analysis['protocol_snapshot'] = {
            'id': protocol['id'],
            'version': protocol['version'],
            'hash': hashlib.sha256(encoded(protocol['definition']).encode()).hexdigest(),
        }
        analysis['input_provenance'] = {
            'trace_hash': data.trace_hash,
            'original_hash': trace.get('original_hash'),
            'decoder': trace.get('decoder', 'legacy_unknown'),
            'session': trace.get('session_index', 0),
            'exclusions': settings['excluded_intervals'],
            'alignment': settings['alignment_markers'],
        }
        from .specialist import attach_gas

        gas = None
        if settings.get('gas_hash'):
            gas = json.loads(store.read_object(settings['gas_hash']))
            if gas.get('kind') != 'gas':
                raise ValueError('Allegato gas non valido.')
        attach_gas(analysis, trace['samples'], settings, gas)
        from .custom_fields import attach

        return attach(enrich(analysis, trace['samples'], settings), protocol, settings)

    @app.post("/api/v1/tests")
    def save_test(data: TestInput):
        if (
            require(data.athlete_id, 'athlete').get('status', 'active') != 'active'
            or require(data.protocol_id, 'protocol').get('status', 'active') != 'active'
        ):
            raise ValueError('Ripristinare atleta e protocollo prima di creare nuovi test.')
        analysis = preview(data)
        trace = json.loads(store.read_object(data.trace_hash))
        if any(t["trace_hash"] == data.trace_hash and t["athlete_id"] == data.athlete_id for t in store.list("test")):
            raise ValueError("Tracciato già associato a questo atleta.")
        a = require(data.athlete_id, "athlete")
        objects = [data.trace_hash, trace['original_hash']]
        if data.settings.gas_hash:
            gas = json.loads(store.read_object(data.settings.gas_hash))
            objects += [data.settings.gas_hash, gas['original_hash']]
        memberships = [
            m["group_id"]
            for m in store.list("membership")
            if m["athlete_id"] == a["id"]
            and m["start"] <= data.date.isoformat()
            and (not m.get("end") or m["end"] >= data.date.isoformat())
        ]
        return store.save(
            "test",
            {
                **data.model_dump(mode="json"),
                "organization_id": a["organization_id"],
                "athlete_snapshot": a,
                "group_ids": memberships,
                "samples": trace["samples"],
                "analysis": analysis,
                "objects": objects,
            },
        )

    @app.get("/api/v1/tests/{id}")
    def test(id: str):
        t = require(id, "test")
        # Older records may keep samples only in the immutable trace object.
        # Rehydrate for display without rewriting the stored analysis/revision.
        if not t.get('samples') and t.get('trace_hash'):
            trace = json.loads(store.read_object(t['trace_hash']))
            return {**t, 'samples': trace.get('samples', [])}
        return {**t, 'samples': t.get('samples', [])}

    @app.get("/api/v1/tests/{id}/report/{format}")
    def test_report(id: str, format: Literal["pdf", "md"], language: Literal['it', 'en'] = 'it'):
        from .reports import report, RENDERER_VERSION

        t = require(id, "test")
        cached = next(
            (
                r
                for r in store.list('report')
                if r.get('renderer_version') == RENDERER_VERSION
                and r.get('test_revision') == t['revision']
                and r.get('format') == format
                and r.get('language', 'it') == language
            ),
            None,
        )
        from .store import report_file

        body = report_file(store, cached) if cached else None
        if body is None:
            body = report(
                t,
                t.get('athlete_snapshot') or require(t["athlete_id"], "athlete"),
                require(t["protocol_id"], "protocol"),
                format,
                language,
            )
            from .store import save_report

            save_report(
                store,
                {
                    'organization_id': t['organization_id'],
                    'test_id': id,
                    'renderer_version': RENDERER_VERSION,
                    'test_revision': t['revision'],
                    'format': format,
                    'language': language,
                },
                body,
            )
        return download(
            body,
            "application/pdf" if format == "pdf" else "application/zip",
            f"test-{id}." + ("pdf" if format == "pdf" else "zip"),
        )

    return preview
