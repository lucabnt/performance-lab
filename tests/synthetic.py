"""Synthetic fixtures only. No real athlete data."""

import math
import struct

ERG = """[COURSE HEADER]
VERSION = 2
MINUTES WATTS
[END COURSE HEADER]
[COURSE DATA]
0 60
10 60
10 80
14 80
14 100
18 100
18 120
22 120
22 140
26 140
26 160
30 160
[END COURSE DATA]
"""


def samples(end=1440):
    result = []
    for t in range(end + 121):
        power = 60 if t < 600 else 80 + 20 * ((t - 600) // 240)
        if t >= end:
            power = 0
        hr = 90 + t * 0.045 if t < end else 90 + end * 0.045 - (t - end) * 0.3
        result.append(
            {
                "t": t,
                "power": round(power + 2 * math.sin(t / 12)) if power else 0,
                "hr": round(hr),
                "cadence": 90 if power else 0,
            }
        )
    return result


def crc(data):
    value = 0
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ (0xA001 if value & 1 else 0)
    return value


def fit_bytes():
    # Record definition: timestamp uint32, power uint16, HR/cadence uint8.
    body = bytes([0x40, 0, 0]) + struct.pack('<H', 20) + bytes([4, 253, 4, 0x86, 7, 2, 0x84, 3, 1, 2, 4, 1, 2])
    for r in samples():
        body += bytes([0]) + struct.pack('<IHBB', 1_100_000_000 + r['t'], r['power'], r['hr'], r['cadence'])
    header = struct.pack('<BBHI4s', 12, 0x10, 100, len(body), b'.FIT')
    content = header + body
    return content + struct.pack('<H', crc(content))
