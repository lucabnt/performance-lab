"""Stable keys and validation for configurable fixed lactate concentrations."""

import math
import re

DEFAULT_LEVELS = [2.0, 3.0, 4.0]
PATTERN = re.compile(r'^lactate_(\d+(?:p\d+)?)_(w|wkg|hr_bpm)$')


def validate_levels(levels):
    if not isinstance(levels, list) or not 1 <= len(levels) <= 20:
        raise ValueError('Specificare da 1 a 20 livelli di lattato.')
    if any(
        isinstance(v, bool)
        or not isinstance(v, (float, int))
        or not math.isfinite(v)
        or not 0 < v <= 40
        or round(v, 3) != v
        for v in levels
    ):
        raise ValueError('Livelli di lattato: valori positivi fino a 40 mmol/L, massimo tre decimali.')
    if len(set(levels)) != len(levels):
        raise ValueError('Livelli di lattato duplicati.')
    return sorted(float(v) for v in levels)


def token(level):
    return format(level, '.10g').replace('.', 'p')


def metric_key(level, channel):
    return f'lactate_{token(level)}_{channel}'


def metric_label(key, language='it'):
    match = PATTERN.fullmatch(key)
    if not match:
        return None
    level, channel = match.groups()
    name = (
        {'w': 'Potenza', 'wkg': 'Potenza relativa', 'hr_bpm': 'FC'}
        if language == 'it'
        else {'w': 'Power', 'wkg': 'Relative power', 'hr_bpm': 'HR'}
    )[channel]
    unit = {'w': 'W', 'wkg': 'W/kg', 'hr_bpm': 'bpm'}[channel]
    return (
        f'{name} a {level.replace("p", ".")} mmol/L ({unit})'
        if language == 'it'
        else f'{name} at {level.replace("p", ".")} mmol/L ({unit})'
    )
