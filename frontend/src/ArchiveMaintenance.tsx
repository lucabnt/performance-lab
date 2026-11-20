import {useState} from 'react';
import {language, tr} from './i18n';
type Row = Record<string, any>;

export function ArchiveMaintenance({
  api,
  run,
  download,
  refresh,
  activate
}: {
  api: any;
  run: any;
  download: any;
  refresh: any;
  activate: any;
}) {
  const en = language === 'en';
  const [path, setPath] = useState(''),
    [note, setNote] = useState(''),
    [plan, setPlan] = useState<Row | null>(null),
    [org, setOrg] = useState(''),
    [operator, setOperator] = useState(''),
    [working, setWorking] = useState(false),
    [protect, setProtect] = useState(false),
    [secret, setSecret] = useState(''),
    [confirmSecret, setConfirmSecret] = useState('');
  // Mirrors the server rule; the server validates again.
  const secretProblem = !protect
    ? ''
    : secret.length < 12
      ? en
        ? 'Use a password of at least 12 characters.'
        : 'Usa una password di almeno 12 caratteri.'
      : secret !== confirmSecret
        ? en
          ? 'The two passwords do not match.'
          : 'Le due password non coincidono.'
        : '';
  const backupName = protect ? 'fuorigiri-backup-v3.fgbak' : 'fuorigiri-backup-v3.zip';
  const downloadScalable = () =>
    protect
      ? download('backup/scalable/encrypted', backupName, {password: secret})
      : download('backup/scalable', backupName);
  const execute = (task: () => Promise<void>) =>
    run(async () => {
      setWorking(true);
      try {
        await task();
      } finally {
        setWorking(false);
      }
    });
  return (
    <>
      <fieldset className="backup-protection">
        <label className="checkbox">
          <input type="checkbox" checked={protect} onChange={e => setProtect(e.target.checked)} />
          {en ? 'Protect with password' : 'Proteggi con password'}
        </label>
        {protect && (
          <>
            <p className="hint" role="note">
              {en
                ? 'The backup is encrypted with this password. Without it the backup cannot be restored by anyone, including the developer: keep it in a password manager.'
                : 'Il backup viene cifrato con questa password. Senza la password nessuno potrà ripristinarlo, nemmeno lo sviluppatore: conservala in un gestore di password.'}
            </p>
            <label>
              {en ? 'Backup password' : 'Password del backup'}
              <input
                type="password"
                autoComplete="new-password"
                minLength={12}
                value={secret}
                onChange={e => setSecret(e.target.value)}
              />
            </label>
            <label>
              {en ? 'Repeat password' : 'Ripeti la password'}
              <input
                type="password"
                autoComplete="new-password"
                value={confirmSecret}
                onChange={e => setConfirmSecret(e.target.value)}
              />
            </label>
            {secretProblem && <small role="alert">{secretProblem}</small>}
          </>
        )}
      </fieldset>
      <div className="actions">
        <button disabled={working || !!secretProblem} onClick={() => execute(downloadScalable)}>
          {protect
            ? en
              ? 'Download protected backup · v3'
              : 'Scarica backup protetto · v3'
            : en
              ? 'Download scalable backup · v3'
              : 'Scarica backup scalabile · v3'}
        </button>
        <button disabled={working} onClick={() => execute(() => download('backup', 'fuorigiri-backup-legacy.zip'))}>
          {en ? 'Legacy backup · v2' : 'Backup precedente · v2'}
        </button>
      </div>
      <p>
        {en
          ? 'The v3 format streams files and supports large archives. Use an updated app to restore it. Without a password the backup is not encrypted; access recovery is exported separately.'
          : 'Il formato v3 elabora i file progressivamente e supporta archivi grandi. Per ripristinarlo serve l’app aggiornata. Senza password il backup non è cifrato; il recupero accessi si esporta separatamente.'}
      </p>
      {!(window as any).FuorigiriNative && (
        <details>
          <summary>
            {en
              ? 'Save directly to disk (large desktop archives)'
              : 'Salva direttamente su disco (archivi desktop grandi)'}
          </summary>
          <p>
            {en
              ? 'Avoids buffering the entire download in the browser. Enter a new ZIP file outside the society data folder.'
              : 'Evita di accumulare l’intero download nel browser. Indica un nuovo file ZIP fuori dalla cartella dati della società.'}
          </p>
          <form
            onSubmit={e => {
              e.preventDefault();
              execute(async () => {
                const r = await api('backup/scalable/save', protect ? {path, password: secret} : {path});
                setNote(r.note + ' ' + r.path);
              });
            }}
          >
            <label>
              {en ? 'Full ZIP file path' : 'Percorso completo del file ZIP'}
              <input
                required
                value={path}
                onChange={e => setPath(e.target.value)}
                placeholder={
                  protect
                    ? en
                      ? 'Full path ending in .fgbak'
                      : 'Percorso assoluto con estensione .fgbak'
                    : en
                      ? 'Full path ending in .zip'
                      : 'Percorso assoluto con estensione .zip'
                }
              />
            </label>
            <button disabled={working || !!secretProblem}>{en ? 'Create backup file' : 'Crea file di backup'}</button>
          </form>
        </details>
      )}
      {note && <p role="status">{note}</p>}
      <details>
        <summary>{en ? 'Separate a legacy society archive' : 'Separa una società da un archivio precedente'}</summary>
        <p>
          {en
            ? 'Creates an independent archive with new keys and founder. Keeps all revisions and related files; the original stays intact. Collaborators need new invitations.'
            : 'Crea un archivio indipendente con nuove chiavi e fondatore. Conserva revisioni e file collegati; l’originale rimane intatto. Ai collaboratori serviranno nuovi inviti.'}
        </p>
        <button
          disabled={working}
          onClick={() =>
            execute(async () => {
              const p = await api('workspaces/split/preview', {});
              setPlan(p);
              setOrg(p.organizations[0]?.id || '');
            })
          }
        >
          {en ? 'Analyse current archive' : 'Analizza archivio aperto'}
        </button>
        {plan && (
          <>
            {!!(plan.problems.length + plan.unassigned.length) && (
              <div className="hint" role="alert">
                <p>
                  {en
                    ? 'Resolve ambiguous links or records without a society before extraction. No records will be silently omitted.'
                    : 'Prima dell’estrazione risolvi collegamenti incoerenti o record senza società. Nessun record verrà escluso silenziosamente.'}
                </p>
                {[...plan.problems, ...plan.unassigned].map((p: Row) => (
                  <p key={p.record_id}>
                    {p.kind} · {p.record_id} · {p.reason}
                  </p>
                ))}
              </div>
            )}
            <form
              onSubmit={e => {
                e.preventDefault();
                execute(async () => {
                  const entry = await api('workspaces/split', {
                    organization_id: org,
                    source_hash: plan.source_hash,
                    operator
                  });
                  setPlan(null);
                  await refresh();
                  await activate(entry);
                });
              }}
            >
              <label>
                {en ? 'Society to extract' : 'Società da estrarre'}
                <select required value={org} onChange={e => setOrg(e.target.value)}>
                  {plan.organizations.map((o: Row) => (
                    <option key={o.id} value={o.id}>
                      {o.name} · {o.records} {tr('record')}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {en ? 'New founder name' : 'Nome del nuovo fondatore'}
                <input required value={operator} onChange={e => setOperator(e.target.value)} />
              </label>
              <button disabled={working || !org || !!plan.problems.length || !!plan.unassigned.length}>
                {en ? 'Create independent society' : 'Crea società indipendente'}
              </button>
            </form>
          </>
        )}
      </details>
    </>
  );
}
