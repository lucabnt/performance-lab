"""Read-only archive size and v1 sync amplification estimate. No keys are read."""
import argparse
import json
import math
import re
import sqlite3
from pathlib import Path
from statistics import median


def encrypted_size(length):
    padded=(length//16+1)*16
    return 4*math.ceil((57+padded)/3)  # Fernet: header, timestamp, IV, HMAC, AES padding.


def measure(root):
    root=Path(root).resolve()
    db_path=root/'archive.sqlite'
    if not db_path.is_file():raise ValueError('Indicare la cartella della singola società con archive.sqlite.')
    objects={p.name:p.stat().st_size for p in (root/'objects').iterdir() if p.is_file() and not p.is_symlink() and re.fullmatch('[0-9a-f]{64}',p.name)}
    db=sqlite3.connect(db_path.as_uri()+'?mode=ro',uri=True)
    packets=[];trace_packets=[];manual_packets=[];missing=set();samples=[];groups={}
    try:
        counts=dict(db.execute('SELECT kind,count(*) FROM records GROUP BY kind'))
        changes_count=0;logical_change_bytes=0
        for (body,) in db.execute('SELECT body FROM changes'):
            changes_count+=1;logical_change_bytes+=len(body.encode())
            event=json.loads(body);record=event['record'];refs=list(dict.fromkeys(record.get('objects',[])))
            skeleton=json.dumps({'change':event,'objects':{h:'' for h in refs}},ensure_ascii=False,sort_keys=True,allow_nan=False,separators=(',',':')).encode()
            for h in refs:
                if h not in objects:missing.add(h)
            length=len(skeleton)+sum(4*math.ceil(objects.get(h,0)/3) for h in refs)
            size=encrypted_size(length);packets.append(size)
            if record['kind']=='test':
                label=(record.get('test_type') or 'incremental')+('-trace' if record.get('samples') or record.get('trace_hash') else '-manual')
                groups.setdefault(label,[]).append(size)
                (trace_packets if record.get('samples') or record.get('trace_hash') else manual_packets).append(size)
        for (body,) in db.execute("SELECT data FROM records WHERE kind='test'"):
            row=json.loads(body)
            if row.get('samples'):samples.append(len(row['samples']))
    finally:db.close()
    return {'schema':1,'records':counts,'test_records_with_inline_samples':len(samples),'sample_count_median':median(samples) if samples else None,
            'sqlite_bytes':db_path.stat().st_size,'objects_count':len(objects),'objects_bytes':sum(objects.values()),
            'archive_bytes':sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink()),
            'changes':changes_count,'changes_json_bytes':logical_change_bytes,'v1_sync_packets':len(packets),
            'v1_sync_estimated_bytes':sum(packets),'v1_sync_packet_max_bytes':max(packets,default=0),'v1_packets_over_80mb':sum(v>80_000_000 for v in packets),
            'v1_trace_revision_median_bytes':median(trace_packets) if trace_packets else None,
            'v1_trace_revision_max_bytes':max(trace_packets,default=0),'v1_manual_revision_median_bytes':median(manual_packets) if manual_packets else None,
            'test_revision_groups':{k:{'revisions':len(v),'median_bytes':median(v),'max_bytes':max(v)} for k,v in groups.items()},
            'missing_object_count':len(missing),'notes':['Stima esatta del formato v1 a oggetti presenti, escluse versioni cloud, canali ruotati e controlli accessi.',
            'Nessuna chiave letta; database aperto in sola lettura. Le revisioni, non solo i test correnti, determinano lo spazio del canale.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--data',type=Path,required=True);parser.add_argument('--out',type=Path)
    args=parser.parse_args();result=measure(args.data);text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(text,encoding='utf-8')
    print(text)


if __name__=='__main__':main()
