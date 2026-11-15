"""Three deterministic simulated all-out FIT files; no actual athletes/exporters."""

import csv
import io
import json
import math
from pathlib import Path
from generate_examples import fit_bytes
from cycling_test.anaerobic import CSV_HEADER


def generate():
    root = Path(__file__).resolve().parents[1] / 'examples/synthetic'
    manifest = []
    historical = []
    for family, duration in [('sprint', 6), ('wingate30', 30), ('wingate15', 15)]:
        rows = []
        for t in range(60 + duration + 91):
            elapsed = t - 60
            power = (
                130
                if elapsed < 0
                else 80
                if elapsed >= duration
                else 1050 * (1 - math.exp(-(elapsed + 1) / 0.75)) * math.exp(-elapsed / (duration * 1.4))
            )
            rows.append(
                {
                    't': t,
                    'power': round(power),
                    'hr': round(100 + 60 * (1 - math.exp(-max(0, t - 50) / 40))),
                    'cadence': round(80 if elapsed < 0 or elapsed >= duration else 145 - 40 * elapsed / duration),
                }
            )
        filename = 'SIM-ANA-' + family + '.fit'
        (root / filename).write_bytes(fit_bytes(rows, '2026-07-01T09:00:00+00:00'))
        manifest.append(
            {
                'file': filename,
                'test_type': family,
                'duration_s': duration,
                'offset_s': 60,
                'weight_kg': 60,
                'synthetic': True,
            }
        )
    for i in (1, 2):
        row = dict.fromkeys(CSV_HEADER.split(','), '')
        row.update(
            test_id=f'SIM-ANA-CSV-{i}',
            atleta_id='SIM-ANA-01',
            data=f'2026-0{i + 1}-15',
            protocollo_id='ANA-15-070',
            peso_kg=60,
            peso_fonte='misurato',
            picco_w=950 + i * 30,
            media_w=750 + i * 20,
            lavoro_kj=(750 + i * 20) * 0.015,
            note='SIMULAZIONE: valori dichiarati, formula storica non documentata.',
        )
        historical.append(row)
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=CSV_HEADER.split(','))
    writer.writeheader()
    writer.writerows(historical)
    (root / 'test_anaerobico.csv').write_text(out.getvalue(), encoding='utf-8')
    (root / 'atleti_anaerobico.csv').write_text(
        'atleta_id,cognome,nome,anno_nascita,attivo,note\nSIM-ANA-01,Simulazione,Anaerobico,2000,si,Dati sintetici\n',
        encoding='utf-8',
    )
    (root / 'manifest_anaerobico.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    print(json.dumps(generate(), indent=2))
