"""Pure analysis: elapsed-time windows, no implicit gap filling or threshold estimates."""
import math

ENGINE_VERSION = "0.1.0"
MAX_GAP_S = 5.0


def valid_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def window(samples, field, start, end):
    total = covered = 0.0
    for row, following in zip(samples, samples[1:]):
        dt = following["t"] - row["t"]
        value = row.get(field)
        if not valid_number(value) or not 0 < dt <= MAX_GAP_S or row.get("paused", False):
            continue
        width = max(0, min(end, following["t"]) - max(start, row["t"]))
        total += value * width
        covered += width
    return {"mean": round(total / covered, 2) if covered else None,
            "coverage": round(covered / (end - start), 4) if end > start else 0,
            "integral": total}


def analyze(samples: list, protocol: dict, settings: dict) -> dict:
    if len(samples) < 2:
        raise ValueError("Servono almeno due campioni temporali.")
    if any(not valid_number(r.get("t")) for r in samples):
        raise ValueError("Timestamp non valido.")
    if any(b["t"] <= a["t"] for a, b in zip(samples, samples[1:])):
        raise ValueError("Timestamp duplicati o non ordinati: correggere il tracciato.")
    offset = settings.get("offset_s", 0)
    end = settings["end_s"]
    if offset < samples[0]["t"] or end <= offset or end > samples[-1]["t"]:
        raise ValueError("Inizio/fine sforzo fuori dal tracciato.")
    weight = settings.get("weight_kg")
    rows, warnings = [], []
    for index, segment in enumerate(protocol["segments"]):
        start = offset + segment["start_s"]
        planned_end = offset + segment["end_s"]
        if start >= end:
            break
        stop = min(end, planned_end)
        power = window(samples, "power", start, stop)
        hr = window(samples, "hr", max(start, stop - 30), stop)
        cadence = window(samples, "cadence", start, stop)
        covered = power["coverage"] >= .95
        complete = stop >= planned_end and covered
        rows.append({**segment, "number": index + 1, "actual_s": stop-start,
                     "complete": complete, "power": power, "hr": hr, "cadence": cadence})
        if not covered:
            warnings.append(f"Step {index+1}: copertura potenza inferiore al 95%.")
    increments = [r for r in rows if r["phase"] == "increment"]
    # Do not call a later stage completed if an earlier required stage lacks coverage.
    completed = []
    for r in increments:
        if not r["complete"]:
            break
        completed.append(r)
    last = completed[-1] if completed else None
    map_w = last["end_w"] if last and last["start_w"] == last["end_w"] else None
    if any(r["start_w"] != r["end_w"] for r in increments):
        map_w = None
        warnings.append("Protocollo a rampa: MAP per step costanti non applicabile.")
    alt = None
    if map_w is not None and len(completed) < len(increments):
        partial = increments[len(completed)]
        if partial["power"]["coverage"] >= .95 and not partial["complete"] and partial["actual_s"] < partial["end_s"]-partial["start_s"] and partial["start_w"] == partial["end_w"] and partial["end_w"] > map_w:
            alt = round(map_w + (partial["end_w"]-map_w) * partial["actual_s"] / (partial["end_s"]-partial["start_s"]), 2)
    if map_w is None:
        warnings.append("Nessuno step incrementale completo e valido: MAP non disponibile.")
    effort = [r for r in samples if offset <= r["t"] <= end and not r.get("paused")]
    hrs = [r["hr"] for r in effort if valid_number(r.get("hr"))]
    recovery = []
    reference = window(samples, "hr", max(offset, end-5), end)
    for t in (60, 90, 120):
        measured = window(samples, "hr", end+t-2, end+t+3)
        value = measured["mean"] if measured["coverage"] >= .8 else None
        recovery.append({"after_s": t, "hr_bpm": value,
                         "hrr_bpm": round(reference["mean"]-value, 1) if value is not None and reference["coverage"] >= .8 else None})
    power = window(samples, "power", offset, end)
    if not hrs:
        warnings.append("Canale FC assente durante lo sforzo.")
    if any(s.get("paused") for s in effort) or any(s.get("paused") for s in samples if offset <= s["t"] <= end):
        warnings.append("Pause timer presenti: asse temporale trascorso; verificare allineamento del protocollo.")
    return {"engine": ENGINE_VERSION, "steps": rows, "map_w": map_w, "map_alt_w": alt,
            "map_wkg": round(map_w/weight, 2) if map_w is not None and weight else None,
            "fc_max_test_bpm": max(hrs) if hrs else None, "duration_s": end-offset,
            "power_mean_w": power["mean"], "work_kj": round(power["integral"]/1000, 2),
            "power_coverage": power["coverage"], "recovery": recovery,
            "warnings": warnings, "method": "Ultimo step incrementale costante completo; copertura potenza ≥95%. Nessuna verifica automatica di aderenza al target."}
