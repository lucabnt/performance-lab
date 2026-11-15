"""Typed, optional extensions. Values never become executable formulae."""

import math
import hashlib
from .store import encoded
from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class FieldDefinition(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    key: str = Field(pattern=r'^[a-z][a-z0-9_]{0,49}$')
    label: str = Field(min_length=1, max_length=120)
    type: Literal['number', 'text', 'boolean', 'date', 'choice'] = 'text'
    scope: Literal['protocol', 'test'] = 'test'
    unit: str = Field(default='', max_length=40)
    choices: list[str] = Field(default_factory=list, max_length=50)
    minimum: float | None = None
    maximum: float | None = None

    @model_validator(mode='after')
    def limits(self):
        if not self.label.strip():
            raise ValueError('Nome campo vuoto.')
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError('Limiti campo invertiti.')
        if self.type == 'choice' and (
            not self.choices
            or len(set(self.choices)) != len(self.choices)
            or any(not c.strip() or len(c) > 120 for c in self.choices)
        ):
            raise ValueError('Scelte vuote, duplicate o troppo lunghe.')
        if self.type != 'number' and (self.minimum is not None or self.maximum is not None):
            raise ValueError('Limiti ammessi solo per numeri.')
        return self


def definitions(fields):
    result = [FieldDefinition.model_validate(f).model_dump() for f in fields]
    if len(result) > 50 or len({f['key'] for f in result}) != len(result):
        raise ValueError('Massimo 50 campi, con identificatori distinti.')
    return result


def values(fields, data, scope):
    allowed = {f['key']: f for f in fields if f['scope'] == scope}
    if set(data) - set(allowed):
        raise ValueError('Campo aggiuntivo non definito o destinato a un’altra scheda.')
    result = {}
    for key, value in data.items():
        if value is None:
            continue
        f = allowed[key]
        kind = f['type']
        if kind == 'number':
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f"{f['label']}: numero finito richiesto.")
            if (
                f.get('minimum') is not None
                and value < f['minimum']
                or f.get('maximum') is not None
                and value > f['maximum']
            ):
                raise ValueError(f"{f['label']}: valore fuori dai limiti.")
        elif kind == 'boolean':
            if type(value) is not bool:
                raise ValueError(f"{f['label']}: scegliere sì o no.")
        else:
            if not isinstance(value, str) or len(value) > 3000:
                raise ValueError(f"{f['label']}: testo non valido.")
            if kind == 'choice' and value not in f['choices']:
                raise ValueError(f"{f['label']}: scelta non disponibile.")
            if kind == 'date':
                date.fromisoformat(value)
        result[key] = value
    return result


def protocol_metadata(data):
    fields = definitions(data.get('custom_fields', []))
    return {'custom_fields': fields, 'custom_values': values(fields, data.get('custom_values', {}), 'protocol')}


def metric_key(protocol_id, field):
    return 'custom:' + protocol_id + ':' + field['key'] + ':' + hashlib.sha256(encoded(field).encode()).hexdigest()[:12]


def attach(analysis, protocol, settings):
    for key in [k for k in analysis if k.startswith('custom:')]:
        analysis.pop(key)
    fields = definitions(protocol.get('custom_fields', []) + settings.get('extra_fields', []))
    if any(f['scope'] != 'test' for f in settings.get('extra_fields', [])):
        raise ValueError('I campi aggiunti alla prova devono appartenere al test.')
    data = values(fields, settings.get('custom_values', {}), 'test')
    analysis.update(custom_fields=fields, custom_values=data, protocol_custom_values=protocol.get('custom_values', {}))
    for f in fields:
        if f['scope'] == 'test' and f['type'] == 'number':
            analysis[metric_key(protocol['id'], f)] = data.get(f['key'])
    from .methods import comparison_key

    analysis['comparison_key'] = (
        protocol['id']
        + '|'
        + comparison_key(
            {
                'analysis': analysis,
                'settings': settings,
                'protocol_id': protocol['id'],
                'test_type': protocol.get('test_type'),
            }
        )
    )
    return analysis


def display_rows(test):
    a = test['analysis']
    rows = []
    for f in a.get('custom_fields', []):
        data = a.get('protocol_custom_values', {}) if f['scope'] == 'protocol' else a.get('custom_values', {})
        v = data.get(f['key'])
        label = f['label'] + (' (' + f['unit'] + ')' if f.get('unit') else '')
        rows.append(
            (
                ('Protocollo - ' if f['scope'] == 'protocol' else '') + label,
                'Non rilevato' if v is None else 'Sì' if v is True else 'No' if v is False else str(v),
            )
        )
    return rows
