"""ERG is an import format; the resulting version is the durable protocol."""

import math


def parse_erg(content: str) -> dict:
    points, metadata = [], {}
    in_data = False
    units = False
    for number, raw in enumerate(content.splitlines(), 1):
        line = raw.strip().lstrip("\ufeff")
        upper = line.upper()
        if not line or line.startswith((";", "#")):
            continue
        if upper == "[COURSE DATA]":
            in_data = True
            continue
        if upper == "[END COURSE DATA]":
            in_data = False
            continue
        if upper == "MINUTES WATTS":
            units = True
        if not in_data:
            if "=" in line:
                key, value = line.split("=", 1)
                metadata[key.strip().upper()] = value.strip()
            continue
        try:
            minutes, watts = map(float, line.split())
        except ValueError as exc:
            raise ValueError(f"Riga ERG {number}: attesi minuti e watt.") from exc
        if not all(math.isfinite(v) for v in (minutes, watts)) or minutes < 0 or watts < 0:
            raise ValueError(f"Riga ERG {number}: valori non validi.")
        t = round(minutes * 60, 6)
        if points and t < points[-1][0]:
            raise ValueError("I tempi ERG devono essere in ordine crescente.")
        points.append([t, watts])
    if not units:
        raise ValueError("Supportato ERG con intestazione MINUTES WATTS.")
    if len(points) < 2 or points[0][0] != 0:
        raise ValueError("Il protocollo deve iniziare a 0 e contenere almeno due punti.")
    segments = []
    for a, b in zip(points, points[1:]):
        if b[0] == a[0]:
            continue  # Retain repeated points; they define discontinuities.
        if (
            segments
            and segments[-1]["end_s"] == a[0]
            and segments[-1]["start_w"] == segments[-1]["end_w"] == a[1] == b[1]
        ):
            segments[-1]["end_s"] = b[0]
        else:
            segments.append({"start_s": a[0], "end_s": b[0], "start_w": a[1], "end_w": b[1], "phase": "increment"})
    if not segments:
        raise ValueError("Durata ERG nulla.")
    return {
        "points": points,
        "segments": segments,
        "description": metadata.get("DESCRIPTION", ""),
        "duration_s": points[-1][0],
    }
