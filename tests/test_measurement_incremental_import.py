import pytest
from test_features import client, post


def setup(tmp_path):
    c = client(tmp_path)
    org = post(c, 'organizations', {'name': 'DEMO incrementale'})
    a = post(c, 'athletes', {'organization_id': org['id'], 'name': 'Andrea', 'surname': 'DEMO'})

    def preview(rows, header='atleta_id,data,peso_kg,statura_cm,altezza_perineale_cm,peso_fonte,origine'):
        raw = (header + '\n' + '\n'.join(a['id'] + ',' + row for row in rows) + '\n').encode()
        r = c.post(
            '/api/v1/import/preview',
            data={'organization_id': org['id'], 'profile': 'antropometria'},
            files={'file': ('synthetic.csv', raw)},
        )
        assert r.status_code == 200, r.text
        return r.json()

    def commit(p):
        return c.post(
            '/api/v1/import/commit',
            json={
                'organization_id': org['id'],
                'profile': 'antropometria',
                'staged_hash': p['staged_hash'],
                'plan_hash': p['plan_hash'],
            },
        )

    return c, a, preview, commit


def test_incremental_preserves_identity_history_and_all_other_fields(tmp_path):
    c, a, preview, commit = setup(tmp_path)
    first = preview(['2026-01-01,,160,,misurato,QA'])
    assert commit(first).status_code == 200
    m = c.get('/api/v1/state').json()['measurement'][0]
    from cycling_test.api import Measurement

    body = {k: v for k, v in m.items() if k in Measurement.model_fields}
    r = c.put(
        '/api/v1/measurements/' + m['id'],
        json={
            'base': m['revision'],
            'reason': 'Dati avanzati QA',
            'measurement': {**body, 'notes': 'Conservare', 'sitting_height_cm': 84, 'quality': 'uncertain'},
        },
    )
    assert r.status_code == 200
    old = r.json()
    # Omitted provenance preserves that of the original; empty cells never clear.
    p = preview(['2026-01-01,,,76,,'])
    assert not p['errors'] and p['ready'] == 1
    assert p['preview'][0]['id'] == old['id']
    assert p['preview'][0]['import_action'] == 'integrate'
    assert p['preview'][0]['added_fields'] == ['perineal_height_cm']
    assert commit(p).json()['integrated'] == 1
    rows = c.get('/api/v1/state').json()['measurement']
    assert len(rows) == 1
    new = rows[0]
    assert new['revision'] != old['revision']
    for k in ('id', 'height_cm', 'weight_kg', 'source', 'origin', 'notes', 'sitting_height_cm', 'quality'):
        assert new[k] == old[k]
    assert new['perineal_height_cm'] == 76
    history = c.get('/api/v1/records/' + old['id'] + '/revisions').json()
    assert len(history) == 3
    assert preview(['2026-01-01,,,76,,'])['skipped'] == 1
    assert preview(['2026-01-01,,160,,misurato,QA'])['skipped'] == 1


def test_batch_merges_complementary_rows_and_is_idempotent(tmp_path):
    c, a, preview, commit = setup(tmp_path)
    rows = ['2026-01-01,,160,,misurato,QA', '2026-01-01,,,76,misurato,QA', '2026-01-01,50,,,misurato,QA']
    p = preview(rows)
    assert not p['errors'] and p['ready'] == 1
    assert p['preview'][0]['import_action'] == 'create'
    assert commit(p).status_code == 200
    m = c.get('/api/v1/state').json()['measurement']
    assert len(m) == 1 and m[0]['height_cm'] == 160 and m[0]['perineal_height_cm'] == 76 and m[0]['weight_kg'] == 50
    assert preview(rows)['skipped'] == 3


@pytest.mark.parametrize(
    'row',
    [
        '2026-01-01,,161,76,misurato,QA',
        '2026-01-01,,,170,,',
    ],
)
def test_conflicts_block_entire_batch_without_writes(tmp_path, row):
    c, a, preview, commit = setup(tmp_path)
    old = post(
        c,
        'measurements',
        {'athlete_id': a['id'], 'date': '2026-01-01', 'height_cm': 160, 'source': 'misurato', 'origin': 'QA'},
    )
    p = preview(['2026-02-01,,165,,misurato,QA', row])
    assert p['errors']
    assert commit(p).status_code == 422
    assert c.get('/api/v1/state').json()['measurement'] == [old]


@pytest.mark.parametrize('source', ['derivato', 'sconosciuto'])
def test_metadata_differences_warn_but_do_not_block_or_overwrite(tmp_path, source):
    c, a, preview, commit = setup(tmp_path)
    old = post(
        c,
        'measurements',
        {'athlete_id': a['id'], 'date': '2026-01-01', 'height_cm': 160, 'source': 'misurato', 'origin': 'Originale'},
    )
    p = preview([f'2026-01-01,,,76,{source},Altra origine', '2026-02-01,,165,,misurato,QA'])
    assert not p['errors'] and p['ready'] == 2
    assert [(w['column'], w['previous'], w['incoming']) for w in p['warnings']] == [
        ('peso_fonte', 'misurato', source),
        ('origine', 'Originale', 'Altra origine'),
    ]
    assert all(
        w['row'] == 2 and w['athlete_external_id'] == a['id'] and w['date'] == '2026-01-01' for w in p['warnings']
    )
    assert commit(p).status_code == 200
    rows = c.get('/api/v1/state').json()['measurement']
    assert len(rows) == 2
    saved = next(m for m in rows if m['id'] == old['id'])
    assert saved['source'] == 'misurato' and saved['origin'] == 'Originale' and saved['perineal_height_cm'] == 76
    again = preview([f'2026-01-01,,,76,{source},Altra origine'])
    assert not again['errors'] and again['skipped'] == 1 and len(again['warnings']) == 2


def test_same_measures_different_sources_are_skipped_without_ambiguity(tmp_path):
    c, a, preview, commit = setup(tmp_path)
    for source in ('dichiarato', 'derivato'):
        post(
            c,
            'measurements',
            {'athlete_id': a['id'], 'date': '2026-01-01', 'weight_kg': 70, 'source': source, 'origin': 'da test'},
        )
    p = preview(['2026-01-01,70,,,derivato,da test'])
    assert not p['errors'] and not p['warnings'] and p['skipped'] == 1 and p['ready'] == 0
    before = c.get('/api/v1/state').json()['measurement']
    assert commit(p).status_code == 200
    assert c.get('/api/v1/state').json()['measurement'] == before


def test_metadata_can_disambiguate_an_actual_addition(tmp_path):
    c, a, preview, commit = setup(tmp_path)
    records = {
        source: post(
            c,
            'measurements',
            {'athlete_id': a['id'], 'date': '2026-01-01', 'height_cm': 160, 'source': source, 'origin': 'QA'},
        )
        for source in ('dichiarato', 'derivato')
    }
    p = preview(['2026-01-01,,160,76,derivato,QA'])
    assert not p['errors'] and not p['warnings'] and p['preview'][0]['id'] == records['derivato']['id']
    assert commit(p).status_code == 200
    rows = c.get('/api/v1/state').json()['measurement']
    assert next(m for m in rows if m['source'] == 'dichiarato')['perineal_height_cm'] is None
    assert next(m for m in rows if m['source'] == 'derivato')['perineal_height_cm'] == 76


def test_covered_row_is_skipped_even_without_matching_metadata(tmp_path):
    c, a, preview, commit = setup(tmp_path)
    for source in ('misurato', 'dichiarato'):
        post(c, 'measurements', {'athlete_id': a['id'], 'date': '2026-01-01', 'weight_kg': 70, 'source': source})
    p = preview(['2026-01-01,70,,,derivato,da test'])
    assert not p['errors'] and p['skipped'] == 1 and len(p['warnings']) == 2
    assert commit(p).status_code == 200


def test_ambiguity_and_deleted_records_are_not_merged(tmp_path):
    c, a, preview, commit = setup(tmp_path)
    old = post(c, 'measurements', {'athlete_id': a['id'], 'date': '2026-01-01', 'height_cm': 160})
    other = post(c, 'measurements', {'athlete_id': a['id'], 'date': '2026-01-01', 'height_cm': 162})
    assert preview(['2026-01-01,,,76,,'])['errors']
    # A shared height resolves the match without touching the other record.
    p = preview(['2026-01-01,,160,76,,'])
    assert not p['errors'] and p['preview'][0]['id'] == old['id']
    assert commit(p).status_code == 200
    post(c, 'records/' + other['id'] + '/status', {'base': other['revision'], 'status': 'deleted'})
    assert preview(['2026-01-01,,162,77,,'])['errors']


def test_changed_plan_requires_new_preview(tmp_path):
    c, a, preview, commit = setup(tmp_path)
    old = post(c, 'measurements', {'athlete_id': a['id'], 'date': '2026-01-01', 'height_cm': 160})
    p = preview(['2026-01-01,,,76,,'])
    from cycling_test.api import Measurement

    body = {k: v for k, v in old.items() if k in Measurement.model_fields}
    r = c.put(
        '/api/v1/measurements/' + old['id'],
        json={
            'base': old['revision'],
            'reason': 'Modifica concorrente',
            'measurement': {**body, 'notes': 'Nuova nota'},
        },
    )
    assert r.status_code == 200
    assert commit(p).status_code == 409
    current = c.get('/api/v1/state').json()['measurement'][0]
    assert current['revision'] == r.json()['revision'] and current['perineal_height_cm'] is None
    assert commit(preview(['2026-01-01,,,76,,'])).status_code == 200


def test_atomic_batch_rolls_back_if_a_revision_changes_after_planning(tmp_path):
    from cycling_test.store import Store, ConflictError

    store = Store(tmp_path)
    first = store.save('measurement', {'athlete_id': 'a', 'date': '2026-01-01', 'height_cm': 160})
    second = store.save('measurement', {'athlete_id': 'a', 'date': '2026-01-02', 'height_cm': 162})
    store.save('measurement', {**second, 'notes': 'Concorrente'}, id=second['id'], base=second['revision'])
    with pytest.raises(ConflictError):
        store.save_batch(
            [
                ('measurement', {**first, 'perineal_height_cm': 76}),
                ('measurement', {**second, 'perineal_height_cm': 77}),
            ],
            bases={first['id']: first['revision'], second['id']: second['revision']},
        )
    assert store.get(first['id']) == first


def test_incremental_revision_is_signed_and_syncs_to_viewer(tmp_path):
    from cycling_test.store import Store
    from cycling_test.workspaces import Workspaces, invitation, join
    from cycling_test.sync import exchange
    from cycling_test.csv_import import plan_import

    owner = Workspaces(tmp_path / 'owner', Store(tmp_path / 'owner'))
    entry = owner.create('DEMO', 'Owner')
    source = owner.get(entry['id'])
    org = entry['organization_id']
    a = source.save('athlete', {'organization_id': org, 'name': 'Andrea', 'surname': 'DEMO'})
    old = source.save(
        'measurement',
        {'organization_id': org, 'athlete_id': a['id'], 'date': '2026-01-01', 'height_cm': 160, 'source': 'misurato'},
    )
    viewer = Workspaces(tmp_path / 'viewer', Store(tmp_path / 'viewer'))
    joined = join(viewer, invitation(source, 'Reader', 'viewer', 'long-password-123'), 'long-password-123')
    target = viewer.get(joined['id'])
    folder = tmp_path / 'cloud'
    folder.mkdir()

    def sync():
        exchange(source, folder, source.identity['sync_key'])
        exchange(target, folder, target.identity['sync_key'])

    sync()
    raw = f"atleta_id,data,altezza_perineale_cm\n{a['id']},2026-01-01,76\n".encode()
    p = plan_import(source, org, 'antropometria', raw)
    assert not p['errors'] and p['bases'] == {old['id']: old['revision']}
    new = source.save_batch(p['entries'], bases=p['bases'])[0]
    sync()
    assert target.get(old['id']) == new
    assert len(source.history(old['id'])) == 2
    import json

    with source.connect() as db:
        change = json.loads(db.execute('SELECT body FROM changes WHERE id=?', (new['revision'],)).fetchone()[0])
    assert change['base'] == old['revision']
    target.verify_change(change)
    with pytest.raises(ValueError, match='Visualizzatore'):
        target.save_batch([('measurement', {**new, 'weight_kg': 50})], bases={new['id']: new['revision']})
    assert target.get(old['id']) == new
