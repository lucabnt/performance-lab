from datetime import datetime
import io
import fitdecode


def decode_fit(data: bytes) -> dict:
    messages = {}
    try:
        with fitdecode.FitReader(io.BytesIO(data),check_crc=fitdecode.CrcCheck.RAISE,error_handling=fitdecode.ErrorHandling.RAISE) as reader:
            for frame in reader:
                if isinstance(frame,fitdecode.FitDataMessage):
                    messages.setdefault(frame.name + "_mesgs",[]).append({f.name:f.value for f in frame.fields})
    except Exception as exc:
        raise ValueError("FIT non valido o decodifica incompleta: " + str(exc)) from exc
    sessions = messages.get("session_mesgs", [])
    if len(sessions) > 1:
        raise ValueError("FIT con più sessioni: separare le sessioni prima dell'importazione in questa versione.")
    records = [r for r in messages.get("record_mesgs", []) if isinstance(r.get("timestamp"), datetime)]
    if len(records) < 2:
        raise ValueError("FIT privo di un tracciato temporale utilizzabile.")
    if len(records) > 100_000:
        raise ValueError("Il tracciato supera 100.000 campioni: selezionare il solo test prima dell'importazione.")
    records.sort(key=lambda r: r["timestamp"])
    epoch = records[0]["timestamp"]
    events = sorted([r for r in messages.get("event_mesgs", []) if r.get("event") == "timer" and isinstance(r.get("timestamp"), datetime)], key=lambda r: r["timestamp"])
    samples, paused, event_index = [], False, 0
    for r in records:
        while event_index < len(events) and events[event_index]["timestamp"] <= r["timestamp"]:
            kind = events[event_index].get("event_type")
            if kind in ("stop", "stop_all", "stop_disable", "stop_disable_all"):
                paused = True
            elif kind == "start":
                paused = False
            event_index += 1
        samples.append({"t": (r["timestamp"]-epoch).total_seconds(), "power": r.get("power"), "hr": r.get("heart_rate"), "cadence": r.get("cadence"), "paused": paused})
    if any(a["t"] == b["t"] for a,b in zip(samples, samples[1:])):
        raise ValueError("FIT con timestamp duplicati: richiede revisione prima dell'analisi.")
    return {"samples": samples, "started_at": epoch.isoformat(), "duration_s": samples[-1]["t"],
            "warnings": ["Confermare manualmente fine sforzo e offset. Il termine del file può includere recupero o defaticamento."]}
