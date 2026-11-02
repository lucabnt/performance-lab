"""ZIP64 schema 3: streamed objects, on-disk inventory and validated SQLite.

No uploaded SQL schema is ever executed. Limits bound disk consumption, while
payload memory is bounded by chunks and individual records. ZIP central directory
metadata still grows with the file count (bounded separately).
"""
from contextlib import contextmanager
from collections.abc import Mapping
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import json
import re
import shutil
import sqlite3
import tempfile
import zipfile
from .store import encoded,KINDS

CHUNK=1_048_576
MAX_COMPRESSED=64_000_000_000
MAX_EXPANDED=256_000_000_000
MAX_FILES=1_000_000
HASH=re.compile('[0-9a-f]{64}')


@contextmanager
def connection(*args,**kwargs):
    db=sqlite3.connect(*args,**kwargs)
    try:
        with db:yield db
    finally:db.close()


def digest_file(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def write_backup(store,destination):
    """Destination must be new; publish a complete ZIP by atomic rename."""
    destination=Path(destination)
    if destination.exists():raise ValueError('Il file di destinazione esiste già: nessun backup sovrascritto.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.fuorigiri-backup-',dir=destination.parent) as tmp:
        stage=Path(tmp);snapshot=stage/'archive.sqlite';inventory=stage/'inventory.jsonl'
        with connection(snapshot) as target:
            with store.connect() as source:source.backup(target)
        manifest={'schema':3,'created_at':datetime.now(timezone.utc).isoformat(),
                  'organizations':[{'id':o['id'],'name':o['name']} for o in store.list('organization')],
                  'warning':'Backup dati non cifrato, senza credenziali; recupero accessi separato.'}
        if hasattr(store,'identity') and not store.identity.get('snapshot'):
            manifest.update(workspace=store.identity['workspace'],authority_public=store.identity['authority_public'])
            for name in ('access.json','revocations.json'):
                if (store.root/name).exists():manifest[name]=json.loads((store.root/name).read_text(encoding='utf-8'))
        total=count=0
        inventory_db=stage/'inventory.sqlite'
        with connection(inventory_db) as inventory_index,zipfile.ZipFile(stage/'backup.zip','w',zipfile.ZIP_DEFLATED,allowZip64=True) as z,inventory.open('w',encoding='utf-8',newline='\n') as index:
            inventory_index.execute('CREATE TABLE files(name TEXT PRIMARY KEY,size INTEGER,sha TEXT)')
            def add(path,name):
                nonlocal total,count
                if path.is_symlink():raise ValueError('Allegato simbolico non consentito.')
                count+=1;total+=path.stat().st_size
                if count>MAX_FILES or total>MAX_EXPANDED:raise ValueError('Backup oltre il limite di sicurezza ZIP64.')
                sha=hashlib.sha256();size=0
                with path.open('rb') as source,z.open(name,'w',force_zip64=True) as target:
                    while raw:=source.read(CHUNK):
                        size+=len(raw);sha.update(raw);target.write(raw)
                digest=sha.hexdigest()
                if name.startswith('objects/') and digest!=path.name:raise ValueError('Allegato corrotto: backup non pubblicato.')
                index.write(encoded({'name':name,'size':size,'sha256':digest})+'\n')
                inventory_index.execute('INSERT INTO files VALUES(?,?,?)',(name,size,digest))
                if (stage/'backup.zip').stat().st_size>MAX_COMPRESSED:raise ValueError('Backup oltre 64 GB compressi.')
            add(snapshot,'archive.sqlite')
            for path in (store.root/'objects').iterdir():
                if HASH.fullmatch(path.name):add(path,'objects/'+path.name)
        validate_database(snapshot,Files(stage,inventory_db))
        # Inventory is written after closing its file, without loading it in RAM.
        with zipfile.ZipFile(stage/'backup.zip','a',zipfile.ZIP_DEFLATED,allowZip64=True) as z:
            z.write(inventory,'inventory.jsonl')
            manifest.update(inventory_sha256=digest_file(inventory),file_count=count,expanded_bytes=total)
            z.writestr('manifest.json',encoded(manifest))
        if (stage/'backup.zip').stat().st_size>MAX_COMPRESSED:raise ValueError('Backup oltre 64 GB compressi.')
        # Never replace another writer's file, including concurrent publication.
        import os
        if os.name=='nt':(stage/'backup.zip').rename(destination)
        else:os.link(stage/'backup.zip',destination)
    return destination


class Rows(Mapping):
    def __init__(self,path):self.path=path
    def __iter__(self):return iter(('records','changes','conflicts','config'))
    def __len__(self):return 4
    def __getitem__(self,table):
        from .recovery import TABLES
        if table not in TABLES:raise KeyError(table)
        def iterate():
            with connection(self.path.as_uri()+'?mode=ro',uri=True) as db:
                db.execute('PRAGMA trusted_schema=OFF')
                yield from db.execute(f'SELECT {",".join(TABLES[table])} FROM {table} ORDER BY rowid')
        return iterate()


class Events(Mapping):
    def __init__(self,rows):self.rows=rows
    def __iter__(self):return (r[0] for r in self.rows['changes'])
    def __len__(self):return sum(1 for _ in self.rows['changes'])
    def __getitem__(self,key):
        with connection(self.rows.path.as_uri()+'?mode=ro',uri=True) as db:
            row=db.execute('SELECT body FROM changes WHERE id=?',(key,)).fetchone()
        if not row:raise KeyError(key)
        return json.loads(row[0])
    def values(self):return (json.loads(r[1]) for r in self.rows['changes'])


class Records:
    def __init__(self,rows):self.rows=rows
    def __iter__(self):return (json.loads(r[3]) for r in self.rows['records'])


class Files(Mapping):
    def __init__(self,root,index):self.root=root;self.index=index
    def __iter__(self):
        with connection(self.index) as db:
            for row in db.execute('SELECT name FROM files'):yield row[0]
    def __len__(self):
        with connection(self.index) as db:return db.execute('SELECT count(*) FROM files').fetchone()[0]
    def __getitem__(self,key):
        with connection(self.index) as db:
            if not db.execute('SELECT 1 FROM files WHERE name=?',(key,)).fetchone():raise KeyError(key)
        return self.root/key


def validate_database(path,files):
    from .recovery import TABLES,OPTIONAL_TABLES
    rows=Rows(path)
    with connection(path.as_uri()+'?mode=ro',uri=True) as db:
        db.execute('PRAGMA trusted_schema=OFF')
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Database danneggiato.')
        if db.execute('PRAGMA user_version').fetchone()[0]>3:raise ValueError('Database di versione successiva.')
        schema=db.execute("SELECT name,type,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").fetchall()
        if any(kind not in ('table','index') or kind=='table' and (name not in TABLES and name not in OPTIONAL_TABLES or not sql.upper().startswith('CREATE TABLE')) for name,kind,sql in schema):raise ValueError('Schema non consentito.')
        if not set(TABLES)<={n for n,k,_ in schema if k=='table'}:raise ValueError('Tabelle mancanti.')
        for name,columns in {**TABLES,**OPTIONAL_TABLES}.items():
            if any(n==name for n,k,_ in schema) and tuple(r[1] for r in db.execute(f'PRAGMA table_info({name})'))!=columns:raise ValueError('Colonne non consentite.')
        for id,body in rows['changes']:
            event=json.loads(body);record=event['record']
            if event['schema']!=1 or event['id']!=id or record['revision']!=id or record['kind'] not in KINDS:raise ValueError('Revisione incoerente.')
            if any(parent and not db.execute('SELECT 1 FROM changes WHERE id=?',(parent,)).fetchone() for parent in event.get('parents',[event['base']])):raise ValueError('Storico incompleto.')
            for digest in record.get('objects',[]):
                if not isinstance(digest,str) or not HASH.fullmatch(digest) or 'objects/'+digest not in files:raise ValueError('Allegato storico mancante.')
        for id,kind,revision,body in rows['records']:
            record=json.loads(body);event=db.execute('SELECT body FROM changes WHERE id=?',(revision,)).fetchone()
            if kind not in KINDS or (record['id'],record['kind'],record['revision'])!=(id,kind,revision) or not event or encoded(json.loads(event[0])['record'])!=encoded(record):raise ValueError('Record incoerente.')
        for id,body in rows['conflicts']:
            event=db.execute('SELECT body FROM changes WHERE id=?',(id,)).fetchone()
            if not event or encoded(json.loads(body))!=encoded(json.loads(event[0])):raise ValueError('Conflitto incoerente.')
    return rows


@contextmanager
def inspect_file(path):
    path=Path(path).resolve()
    try:
        if path.stat().st_size>MAX_COMPRESSED:raise ValueError('Backup oltre 64 GB.')
        with zipfile.ZipFile(path) as z:
            from .recovery import validate_zip_members
            validate_zip_members(z)
            if z.getinfo('manifest.json').file_size>4_000_000:raise ValueError('Manifest troppo grande.')
            manifest=json.loads(z.read('manifest.json'))
            if manifest.get('schema') in (1,2):
                from .recovery import inspect_backup
                from .recovery import MAX_UPLOAD
                if path.stat().st_size>MAX_UPLOAD:raise ValueError('Backup legacy oltre il limite; produrre un backup v3 dalla versione aggiornata.')
                yield inspect_backup(path.read_bytes());return
            if manifest.get('schema')!=3:raise ValueError('Formato backup non supportato.')
            infos=z.infolist();names={i.filename for i in infos}
            total=sum(i.file_size for i in infos)
            if len(names)!=len(infos) or len(names)>MAX_FILES+2 or total>MAX_EXPANDED:raise ValueError('Backup troppo grande o duplicato.')
            if any(not (n in ('archive.sqlite','manifest.json','inventory.jsonl') or re.fullmatch('objects/[0-9a-f]{64}',n)) for n in names):raise ValueError('Percorsi backup non consentiti.')
            if not {'archive.sqlite','manifest.json','inventory.jsonl'}<=names:raise ValueError('Backup incompleto.')
            with tempfile.TemporaryDirectory(prefix='fuorigiri-verify-') as temp:
                root=Path(temp);index=root/'index.sqlite'
                if shutil.disk_usage(root).free<total+64_000_000:raise ValueError('Spazio temporaneo insufficiente per verificare il backup.')
                with connection(index) as db:
                    db.execute('CREATE TABLE files(name TEXT PRIMARY KEY,size INTEGER,sha TEXT)')
                    sha=hashlib.sha256();count=0
                    with z.open('inventory.jsonl') as stream:
                        while line:=stream.readline(1025):
                            if len(line)>1024:raise ValueError('Inventario non valido.')
                            sha.update(line);item=json.loads(line);name=item['name'];size=item['size'];digest=item['sha256'];count+=1
                            if count>MAX_FILES or name not in names or name in ('manifest.json','inventory.jsonl') or type(size) is not int or size<0 or not HASH.fullmatch(digest):raise ValueError('Voce inventario non valida.')
                            if name.startswith('objects/') and digest!=name[8:]:raise ValueError('Hash allegato non valido.')
                            db.execute('INSERT INTO files VALUES(?,?,?)',(name,size,digest))
                    if sha.hexdigest()!=manifest['inventory_sha256'] or count!=manifest['file_count'] or count!=len(names)-2:raise ValueError('Inventario incompleto o alterato.')
                    for name,size,digest in db.execute('SELECT name,size,sha FROM files'):
                        if z.getinfo(name).file_size!=size:raise ValueError('Dimensione non valida.')
                        target=root/name;target.parent.mkdir(exist_ok=True);actual=hashlib.sha256()
                        with z.open(name) as source,target.open('xb') as out:
                            while raw:=source.read(CHUNK):actual.update(raw);out.write(raw)
                        if actual.hexdigest()!=digest:raise ValueError('Checksum backup non valido.')
                files=Files(root,index);rows=validate_database(root/'archive.sqlite',files)
                records=Records(rows)
                if not any(r['kind']=='organization' for r in records):raise ValueError('Società mancante.')
                yield {'manifest':manifest,'rows':rows,'records':records,'changes':Events(rows),'files':files}
    except (zipfile.BadZipFile,sqlite3.DatabaseError,UnicodeError,KeyError,TypeError,AttributeError,RecursionError,json.JSONDecodeError) as exc:
        raise ValueError('Backup non valido o danneggiato.') from exc
