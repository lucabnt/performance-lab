from datetime import datetime
import io
import fitdecode


def decode_fit(data: bytes, session_index=None, overview=False, duplicate_policy='reject', correction_reason='') -> dict:
    messages = {}
    try:
        with fitdecode.FitReader(io.BytesIO(data),check_crc=fitdecode.CrcCheck.RAISE,error_handling=fitdecode.ErrorHandling.RAISE) as reader:
            for frame in reader:
                if isinstance(frame,fitdecode.FitDataMessage):
                    messages.setdefault(frame.name + "_mesgs",[]).append({f.name:f.value for f in frame.fields})
    except Exception as exc:
        raise ValueError("FIT non valido o decodifica incompleta: " + str(exc)) from exc
    sessions = messages.get("session_mesgs", [])
    metadata=[{'index':i,'start':str(s.get('start_time','')),'end':str(s.get('timestamp','')),'sport':str(s.get('sport',''))} for i,s in enumerate(sessions)]
    if overview:return {'sessions':metadata or [{'index':0,'start':'','end':'','sport':''}]}
    if len(sessions) > 1 and session_index is None:
        raise ValueError('FIT con più sessioni: selezionare esplicitamente la sessione da importare.')
    records = [r for r in messages.get("record_mesgs", []) if isinstance(r.get("timestamp"), datetime)]
    if sessions and session_index is not None:
        if not 0<=session_index<len(sessions):raise ValueError('Sessione non valida.')
        selected=sessions[session_index]
        if not all(isinstance(selected.get(k),datetime) for k in ('start_time','timestamp')):raise ValueError('Limiti sessione mancanti: richiede revisione.')
        records=[r for r in records if selected['start_time']<=r['timestamp']<=selected['timestamp']]
    if duplicate_policy not in ('reject','keep_last'):raise ValueError('Politica duplicati non valida.')
    if duplicate_policy=='keep_last':
        if not correction_reason.strip():raise ValueError('Indicare il motivo della correzione duplicati.')
        records=list({r['timestamp']:r for r in records}.values())
    if len(records) < 2:
        raise ValueError("FIT privo di un tracciato temporale utilizzabile.")
    if len(records) > 100_000:
        raise ValueError("Il tracciato supera 100.000 campioni: selezionare il solo test prima dell'importazione.")
    ordered=all(a['timestamp']<=b['timestamp'] for a,b in zip(records,records[1:]))
    if not ordered and duplicate_policy=='reject':raise ValueError('Timestamp non ordinati: richiede correzione esplicita con motivo.')
    records.sort(key=lambda r: r["timestamp"])
    epoch = records[0]["timestamp"]
    events = sorted([r for r in messages.get("event_mesgs", []) if r.get("event") == "timer" and isinstance(r.get("timestamp"), datetime)], key=lambda r: r["timestamp"])
    samples, paused, event_index = [], False, 0
    previous_time=None
    for r in records:
        while event_index < len(events) and events[event_index]["timestamp"] <= r["timestamp"]:
            event_time=(events[event_index]['timestamp']-epoch).total_seconds()
            kind = events[event_index].get("event_type")
            new_paused=True if kind in ('stop','stop_all','stop_disable','stop_disable_all') else False if kind=='start' else paused
            # Split only a genuinely observed interval; never fill a long gap.
            if previous_time is not None and previous_time<events[event_index]['timestamp']<r['timestamp'] and (r['timestamp']-previous_time).total_seconds()<=5 and samples and event_time>samples[-1]['t']:
                samples.append({**samples[-1],'t':event_time,'paused':new_paused,'timer_boundary':True})
            elif samples and samples[-1].get('timer_boundary') and event_time==samples[-1]['t']:
                samples[-1]['paused']=new_paused
            kind = events[event_index].get("event_type")
            if kind in ("stop", "stop_all", "stop_disable", "stop_disable_all"):
                paused = True
            elif kind == "start":
                paused = False
            event_index += 1
        samples.append({"t": (r["timestamp"]-epoch).total_seconds(), "power": r.get("power"), "hr": r.get("heart_rate"), "cadence": r.get("cadence"), "paused": paused})
        previous_time=r['timestamp']
    if any(a["t"] == b["t"] for a,b in zip(samples, samples[1:])):
        raise ValueError("FIT con timestamp duplicati: richiede revisione prima dell'analisi.")
    return {"samples": samples, "started_at": epoch.isoformat(), "duration_s": samples[-1]["t"],
            'decoder':'fitdecode-strict/2','session_index':session_index or 0,'sessions':metadata,
            'corrections':{'duplicate_policy':duplicate_policy,'reason':correction_reason,'input_ordered':ordered},
            'laps':[{'start':str(r.get('start_time','')),'end':str(r.get('timestamp',''))} for r in messages.get('lap_mesgs',[])],
            "warnings": ["Confermare manualmente fine sforzo e offset. Il termine del file può includere recupero o defaticamento."]}
