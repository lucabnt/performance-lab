from cycling_test.history import paired_comparison,summarize
from cycling_test.store import Store


def records(tmp_path):
    s=Store(tmp_path)
    org=s.save('organization',{'name':'QA'})
    athlete=s.save('athlete',{'organization_id':org['id'],'name':'QA','surname':'Atleta'})
    protocol=s.save('protocol',{'name':'Protocollo QA','version':'1'})
    return s,org,athlete,protocol


def save_test(s,org,athlete,protocol,year,source,weight_source='misurato'):
    return s.save('test',{'organization_id':org['id'],'athlete_id':athlete['id'],'protocol_id':protocol['id'],
        'date':year+'-06-01','settings':{'weight_source':weight_source,'weight_kg':50},
        'analysis':{'engine':'manual-1','threshold_source':source,'map_w':200 if year=='2025' else 220,
                    'map_wkg':4 if year=='2025' else 4.4,'lactate_3p5_hr_bpm':150 if year=='2025' else 155}})


def test_paired_sources_without_threshold_and_declared_do_not_crash(tmp_path):
    s,org,a,p=records(tmp_path)
    for year in ('2025','2026'):
        for source in (None,'dichiarato'):save_test(s,org,a,p,year,source)
    result=paired_comparison(s,org['id'],'2025','2026')
    assert result['n_pairs']==2
    assert all(r['map_w_delta']==20 for r in result['pairs'])


def test_paired_estimated_weight_is_excluded_but_power_and_dynamic_metrics_remain(tmp_path):
    s,org,a,p=records(tmp_path)
    save_test(s,org,a,p,'2025',None,'stimato');save_test(s,org,a,p,'2026',None)
    result=paired_comparison(s,org['id'],'2025','2026')['pairs'][0]
    assert result['map_w_delta']==20
    assert result['map_wkg_delta'] is None and result['map_wkg_pct'] is None
    assert result['lactate_3p5_hr_bpm_delta']==5


def test_progression_deltas_also_exclude_estimated_weight(tmp_path):
    s,org,a,p=records(tmp_path)
    save_test(s,org,a,p,'2025',None,'stimato');save_test(s,org,a,p,'2026',None)
    last=summarize(s,org['id'])['changes'][-1]
    assert last['map_w_delta']==20 and last['map_wkg_delta'] is None
