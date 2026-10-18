import json
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces
from cycling_test.api import create_app
from cycling_test.fit import decode_fit
from cycling_test.sync_service import run_sync
from cycling_test.csv_import import plan_import
from cycling_test.history import summarize
from cycling_test.recovery import inspect_backup

sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from demo_suite import generate,PASSWORD,export_portable

def test_acceptance_corpus_and_replicas(tmp_path):
    root=tmp_path/'demo';manifest=generate(root,small=True)
    assert len(manifest['organizations'])==2
    manager=Workspaces(root,Store(root));main=manager.get(manifest['organizations'][0]['id'])
    assert len(main.list('test'))>=20
    assert {'custom','sprint','wingate15','wingate30'} <= {t.get('test_type') for t in main.list('test')}
    assert any(len(main.history(t['id']))>1 for t in main.list('test'))
    assert any(t['settings'].get('zone_schemes') and len(t['settings']['zone_schemes'][0]['zones'])==7 for t in main.list('test'))
    assert any(t['analysis'].get('gas') for t in main.list('test'))
    assert any(t['analysis'].get('lactate_analysis') for t in main.list('test'))
    fixtures=root/'fixtures'
    assert len(decode_fit((fixtures/'fit-due-sessioni.fit').read_bytes(),overview=True)['sessions'])==2
    with pytest.raises(ValueError):decode_fit((fixtures/'fit-due-sessioni.fit').read_bytes())
    with pytest.raises(ValueError):decode_fit((fixtures/'fit-crc-corrotto.fit').read_bytes())
    with pytest.raises(ValueError):decode_fit((fixtures/'fit-timestamp-duplicati.fit').read_bytes())
    assert decode_fit((fixtures/'fit-timestamp-duplicati.fit').read_bytes(),duplicate_policy='keep_last',correction_reason='Fixture simulata')['samples']
    org=manifest['organizations'][0]['organization_id'];plan=plan_import(main,org,'test_aerobico',(fixtures/'import-errori.csv').read_bytes());assert len(plan['errors'])==2
    summary=summarize(main,org);assert summary['metric_labels']
    assert inspect_backup((root/'backup-SOLO-DEMO.zip').read_bytes())
    viewer_root=root/'repliche/viewer';viewer_manager=Workspaces(viewer_root,Store(viewer_root));viewer=viewer_manager.get(manifest['organizations'][0]['id'])
    assert viewer.identity['certificate']['role']=='viewer'
    with pytest.raises(ValueError):viewer.save('athlete',{'name':'Forbidden'})
    admin_root=root/'repliche/admin';admin_manager=Workspaces(admin_root,Store(admin_root));admin=admin_manager.get(manifest['organizations'][0]['id'])
    assert run_sync(admin)['errors']==[]
    result=run_sync(main);assert result['conflicts']>=1
    assert main.revocations()
    c=TestClient(create_app(root,token='t'));c.headers.update({'X-Fuorigiri-Token':'t','X-Fuorigiri-Workspace':manifest['organizations'][0]['id']})
    state=c.get('/api/v1/state');assert state.status_code==200 and state.json()['test']
    with pytest.raises(ValueError):generate(root,small=True)

    # Independent constants make the corpus useful for manual numerical checks.
    from cycling_test.anaerobic import Protocol,Settings as AnaSettings,analyze as ana
    from cycling_test.analysis import analyze
    from cycling_test.api import Settings
    from cycling_test.erg import parse_erg
    from cycling_test.csv_import import decode_trace_csv
    oracle=json.loads((root/'oracoli-numerici.json').read_text(encoding='utf-8'))
    spec=Protocol(organization_id=org,name='Oracle',family='wingate15').model_dump()
    a=ana(decode_trace_csv((fixtures/oracle['wingate15']['file']).read_bytes())['samples'],spec,AnaSettings(weight_kg=50).model_dump())
    for k,v in oracle['wingate15']['expected'].items():assert a[k]==pytest.approx(v)
    a=analyze(decode_trace_csv((fixtures/oracle['incremental']['file']).read_bytes())['samples'],parse_erg((fixtures/oracle['incremental']['erg']).read_text()),Settings(end_s=150,weight_kg=50).model_dump())
    for k,v in oracle['incremental']['expected'].items():assert a[k]==pytest.approx(v)
    import zipfile
    portable=export_portable(root,tmp_path/'portable.zip')
    with zipfile.ZipFile(portable) as z:
        assert len([n for n in z.namelist() if n.startswith('backups/')])==2
        assert not any(n.endswith('identity.json') for n in z.namelist())
        raw=z.read('backups/societa-1-SOLO-DEMO.zip');assert inspect_backup(raw)
        from cycling_test.recovery import restore
        target=tmp_path/'restored';manager2=Workspaces(target,Store(target));entry=restore(manager2,raw,'independent',operator='Demo restore');copy=manager2.get(entry['id'])
        original=next(t for t in main.list('test') if t.get('test_type')=='custom')
        assert copy.get(original['id'])['analysis']==original['analysis']
        assert len(copy.history(original['id']))==len(main.history(original['id']))
