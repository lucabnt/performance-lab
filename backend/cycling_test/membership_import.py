"""Preview historical memberships and missing groups without changing records."""

import csv
import hashlib
import io
from uuid import NAMESPACE_URL, uuid5

COLUMNS = [
    'atleta_id',
    'nome',
    'cognome',
    'data_inizio',
    'data_fine',
    'gruppo',
    'sottogruppo',
    'anno_categoria',
    'note',
]
RULE = 'ID esterno, nome e cognome devono corrispondere all’anagrafica. Date AAAA-MM-GG; fine vuota = in corso. Gruppo = categoria, sottogruppo = stagione (es. 2024). Categorie e stagioni mancanti sono proposte in anteprima.'


def sample_csv():
    stream = io.StringIO(newline='')
    writer = csv.writer(stream)
    writer.writerow(COLUMNS)
    writer.writerows(
        [
            [
                'DEMO-001',
                'Giulia',
                'Riva',
                '2024-01-01',
                '2024-12-31',
                'Esordienti',
                '2024',
                '2',
                'Esempio sintetico: sostituire con il proprio ID esterno',
            ],
            [
                'DEMO-001',
                'Giulia',
                'Riva',
                '2025-01-01',
                '2025-12-31',
                'Allievi',
                '2025',
                '1',
                'Passaggio di categoria',
            ],
            ['DEMO-001', 'Giulia', 'Riva', '2026-01-01', '2026-12-31', 'Allievi', '2026', '2', 'Stagione corrente'],
            ['DEMO-002', 'Marco', 'Demo', '2027-01-01', '2027-12-31', 'Allievi', '2027', '1', 'Pianificazione futura'],
        ]
    )
    return stream.getvalue().encode('utf-8-sig')


def normalized(value):
    return ' '.join(str(value or '').split()).casefold()


def plan_memberships(store, org, raw):
    from .api import Membership
    from .csv_import import read

    rows = read(raw)
    text = raw.decode('utf-8-sig')
    delimiter = ';' if text.splitlines()[0].count(';') > text.splitlines()[0].count(',') else ','
    headers = next(csv.reader(io.StringIO(text), delimiter=delimiter))
    required = {'atleta_id', 'nome', 'cognome', 'data_inizio', 'gruppo'}
    if required - set(headers):
        raise ValueError('Colonne obbligatorie mancanti: ' + ', '.join(sorted(required - set(headers))))
    if len(rows) > 100000:
        raise ValueError('Troppe righe nel lotto.')
    athletes = [a for a in store.list('athlete') if a['organization_id'] == org]
    groups = [g for g in store.list('group') if g['organization_id'] == org]
    memberships = store.list('membership')
    entries, errors, skipped = [], [], 0
    batch = hashlib.sha256(raw).hexdigest()

    def new_group(name, season='', parent=None):
        identity = org + '|membership-import-group|' + (parent or '') + '|' + normalized(season or name)
        group = {
            'id': str(uuid5(NAMESPACE_URL, identity)),
            'organization_id': org,
            'name': name,
            'season': season,
            'parent_id': parent,
            'import_hash': batch,
        }
        groups.append(group)
        entries.append(('group', group))
        return group

    def unique(candidates, label):
        if len(candidates) > 1:
            raise ValueError(label + ' ambiguo: correggere prima i duplicati nell’archivio.')
        if candidates and candidates[0].get('status') == 'deleted':
            raise ValueError(label + ' eliminato: ripristinarlo prima dell’importazione.')
        return candidates[0] if candidates else None

    for i, row in enumerate(rows, 2):
        try:
            external = row['atleta_id'].strip()
            candidates = [a for a in athletes if external and external in (a.get('external_id'), a['id'])]
            athlete = unique(candidates, 'Atleta')
            if not athlete:
                raise ValueError('ID atleta non riconciliato: importare prima le anagrafiche della società.')
            if (
                not normalized(row['nome'])
                or not normalized(row['cognome'])
                or normalized(row['nome']) != normalized(athlete['name'])
                or normalized(row['cognome']) != normalized(athlete['surname'])
            ):
                raise ValueError('Nome o cognome non corrispondono all’ID atleta.')
            name = row['gruppo'].strip()
            season = row.get('sottogruppo', '').strip()
            if not name or len(name) > 300 or len(season) > 300:
                raise ValueError('Indicare gruppo e sottogruppo validi (massimo 300 caratteri).')
            # Validate dates before proposing any groups; never infer them from a season.
            payload = Membership(
                athlete_id=athlete['id'],
                group_id='pending',
                start=row['data_inizio'],
                end=row.get('data_fine', '').strip() or None,
                category_year=int(row['anno_categoria']) if row.get('anno_categoria', '').strip() else None,
            ).model_dump(mode='json')
            parent = unique(
                [g for g in groups if not g.get('parent_id') and normalized(g['name']) == normalized(name)], 'Categoria'
            )
            parent = parent or new_group(name)
            if season:
                matches = [
                    g
                    for g in groups
                    if g.get('parent_id') == parent['id'] and normalized(g.get('season')) == normalized(season)
                ]
                if normalized(parent.get('season')) == normalized(season):
                    matches.append(parent)
                target = unique(matches, 'Stagione')
                if target and target.get('season_status') == 'deleted':
                    raise ValueError('Stagione eliminata: ripristinarla prima dell’importazione.')
                target = target or new_group(parent['name'], season, parent['id'])
            else:
                if parent.get('season'):
                    raise ValueError('La categoria contiene una stagione preesistente: indicarla in sottogruppo.')
                target = parent
            payload['group_id'] = target['id']
            overlaps = [
                m
                for m in memberships
                if m.get('status') != 'deleted'
                and m['athlete_id'] == athlete['id']
                and m['group_id'] == target['id']
                and m['start'] <= (payload['end'] or '9999-12-31')
                and (not m.get('end') or m['end'] >= payload['start'])
            ]
            if overlaps:
                if all(all(m.get(k) == payload.get(k) for k in ('start', 'end', 'category_year')) for m in overlaps):
                    skipped += 1
                    continue
                raise ValueError(
                    'Periodo sovrapposto a un’altra appartenenza nello stesso gruppo: riconciliare le date.'
                )
            identity = '|'.join(
                str(payload.get(k) or '') for k in ('athlete_id', 'group_id', 'start', 'end', 'category_year')
            )
            payload.update(
                id=str(uuid5(NAMESPACE_URL, org + '|historical-membership|' + identity)),
                notes=row.get('note', ''),
                import_hash=batch,
            )
            # A deleted record is never silently recreated by an import.
            if any(m['id'] == payload['id'] for m in memberships):
                raise ValueError('Appartenenza già eliminata: riconciliare lo storico prima di reimportarla.')
            entries.append(('membership', payload))
            memberships.append(payload)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append({'row': i, 'error': str(exc)})
    return {'entries': entries, 'errors': errors, 'skipped': skipped, 'rows': len(rows), 'hash': batch}
