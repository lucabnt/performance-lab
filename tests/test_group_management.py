from fastapi.testclient import TestClient
from cycling_test.api import create_app


def post(c, path, payload):
    r = c.post('/api/v1/' + path, json=payload)
    assert r.status_code == 200, r.text
    return r.json()


def setup(tmp_path):
    c = TestClient(create_app(tmp_path, token='test'))
    c.headers['X-Fuorigiri-Token'] = 'test'
    org = post(c, 'organizations', {'name': 'Societa DEMO'})
    root = post(c, 'groups', {'organization_id': org['id'], 'name': 'Allievi', 'season': '2026'})
    child = post(c, 'groups', {'organization_id': org['id'], 'name': '', 'season': '2027', 'parent_id': root['id']})
    athlete = post(c, 'athletes', {'organization_id': org['id'], 'name': 'Alfa', 'surname': 'DEMO'})
    for g in [root, child]:
        post(c, 'memberships', {'group_id': g['id'], 'athlete_id': athlete['id'], 'start': g['season'] + '-01-01'})
    return c, org, root, child, athlete


def lifecycle(c, g, status, scope='group'):
    return post(c, f"groups/{g['id']}/lifecycle", {'base': g['revision'], 'status': status, 'scope': scope})


def test_delete_restore_season_preserves_athletes_memberships_tests_and_revisions(tmp_path):
    c, _, _, child, _ = setup(tmp_path)
    before = c.get('/api/v1/state').json()
    deleted = lifecycle(c, child, 'deleted')
    after = c.get('/api/v1/state').json()
    for kind in ['athlete', 'membership', 'test', 'measurement']:
        assert after[kind] == before[kind]
    assert deleted['status'] == 'deleted'
    history = c.get(f"/api/v1/records/{child['id']}/revisions").json()
    assert history[0] == child and len(history) == 2
    restored = lifecycle(c, deleted, 'active')
    assert restored['id'] == child['id'] and restored['season'] == '2027'


def test_legacy_root_season_can_be_removed_without_removing_category_or_child(tmp_path):
    c, _, root, child, _ = setup(tmp_path)
    before = c.get('/api/v1/state').json()
    deleted = lifecycle(c, root, 'deleted', 'season')
    assert deleted['season'] == '2026' and deleted['season_status'] == 'deleted'
    after = c.get('/api/v1/state').json()
    assert next(g for g in after['group'] if g['id'] == child['id']) == child
    assert after['membership'] == before['membership']
    assert deleted.get('status', 'active') == 'active'
    assert lifecycle(c, deleted, 'active', 'season')['season_status'] == 'active'


def test_category_requires_children_removed_and_restore_parent_first(tmp_path):
    c, _, root, child, _ = setup(tmp_path)
    payload = {'base': root['revision'], 'status': 'deleted'}
    assert c.post(f"/api/v1/groups/{root['id']}/lifecycle", json=payload).status_code == 422
    removed_child = lifecycle(c, child, 'deleted')
    removed_root = lifecycle(c, root, 'deleted')
    assert (
        c.post(
            f"/api/v1/groups/{child['id']}/lifecycle", json={'base': removed_child['revision'], 'status': 'active'}
        ).status_code
        == 422
    )
    lifecycle(c, removed_root, 'active')
    lifecycle(c, removed_child, 'active')


def test_edit_and_move_season_changes_only_group_and_rejects_stale_revision(tmp_path):
    c, org, root, child, _ = setup(tmp_path)
    other = post(c, 'groups', {'organization_id': org['id'], 'name': 'Esordienti'})
    before = c.get('/api/v1/state').json()
    payload = {
        'base': child['revision'],
        'organization_id': org['id'],
        'name': 'Rosa futura',
        'season': '2028',
        'parent_id': other['id'],
    }
    r = c.put(f"/api/v1/groups/{child['id']}", json=payload)
    assert r.status_code == 200, r.text
    assert r.json()['parent_id'] == other['id'] and r.json()['season'] == '2028'
    assert c.put(f"/api/v1/groups/{child['id']}", json=payload).status_code == 409
    assert c.get('/api/v1/state').json()['membership'] == before['membership']
    assert c.get('/api/v1/state').json()['athlete'] == before['athlete']


def test_reject_cycles_foreign_organization_and_deleted_parents(tmp_path):
    c, org, root, child, _ = setup(tmp_path)
    payload = {
        'base': root['revision'],
        'organization_id': org['id'],
        'name': root['name'],
        'season': '2026',
        'parent_id': root['id'],
    }
    assert c.put(f"/api/v1/groups/{root['id']}", json=payload).status_code == 422
    payload['parent_id'] = child['id']
    assert c.put(f"/api/v1/groups/{root['id']}", json=payload).status_code == 422
    foreign = post(c, 'organizations', {'name': 'Altra DEMO'})
    payload.update(parent_id=None, organization_id=foreign['id'])
    assert c.put(f"/api/v1/groups/{root['id']}", json=payload).status_code == 422
    removed = lifecycle(c, child, 'deleted')
    payload.update(base=removed['revision'], organization_id=org['id'])
    assert c.put(f"/api/v1/groups/{child['id']}", json=payload).status_code == 422


def test_deleted_group_and_legacy_season_reject_new_memberships(tmp_path):
    c, _, root, child, athlete = setup(tmp_path)
    lifecycle(c, child, 'deleted')
    lifecycle(c, root, 'deleted', 'season')
    for g in [root, child]:
        body = {'group_id': g['id'], 'athlete_id': athlete['id'], 'start': '2028-01-01'}
        assert c.post('/api/v1/memberships', json=body).status_code == 422
        body.pop('athlete_id')
        body['athlete_ids'] = [athlete['id']]
        assert c.post('/api/v1/memberships/batch', json=body).status_code == 422
    assert (
        c.post(
            '/api/v1/groups',
            json={'organization_id': root['organization_id'], 'parent_id': child['id'], 'season': '2028'},
        ).status_code
        == 422
    )
