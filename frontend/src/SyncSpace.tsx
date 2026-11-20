import {useEffect, useState} from 'react';
import {language, trBackend} from './i18n';
type Row = Record<string, any>;

// SYNC-SPAZIO-01 phase 0: read-only analysis of the exchange destination.
export function SyncSpace({api, disabled}: {api: any; disabled: boolean}) {
  const en = language === 'en';
  const [job, setJob] = useState<Row>({status: 'idle'}),
    [error, setError] = useState('');
  const running = job.status === 'running';
  const refresh = async () => {
    try {
      setJob(await api('sync/space/job'));
      setError('');
    } catch (e: any) {
      setError(e?.message || String(e));
    }
  };
  useEffect(() => {
    refresh();
  }, []);
  useEffect(() => {
    if (!running) return;
    const timer = setTimeout(refresh, 1500);
    return () => clearTimeout(timer);
  }, [running, job.reads, job.elapsed_s]);
  const start = async () => {
    try {
      setJob(await api('sync/space/start', {}));
      setError('');
    } catch (e: any) {
      setError(e?.message || String(e));
    }
  };
  const size = (bytes: number) => {
    const format = (value: number, unit: string) =>
      `${value.toLocaleString(en ? 'en' : 'it', {maximumFractionDigits: 1})} ${unit}`;
    return bytes >= 1_000_000
      ? format(bytes / 1_000_000, 'MB')
      : bytes >= 1000
        ? format(bytes / 1000, 'KB')
        : format(bytes || 0, 'B');
  };
  const labels: Row = {
    v1_events: en ? 'v1 packets (one per revision)' : 'Pacchetti v1 (uno per revisione)',
    v2_pages: en ? 'v2 pages' : 'Pagine v2',
    v2_catalogues: en ? 'v2 catalogues' : 'Cataloghi v2',
    v2_chunks: en ? 'v2 file chunks (traces, attachments)' : 'Blocchi v2 (tracciati, allegati)',
    controls: en ? 'Access controls and notices' : 'Controlli di accesso e avvisi'
  };
  const r = job.status === 'completed' ? job.result : null;
  return (
    <details>
      <summary>{en ? 'Space used by the exchange' : 'Spazio occupato dallo scambio'}</summary>
      <p>
        {en
          ? 'Reads and decrypts every file of the saved destination to show what occupies space. Nothing is written or deleted. It downloads the whole channel once, so it can take time and data traffic.'
          : 'Legge e decifra tutti i file della destinazione salvata per mostrare cosa occupa spazio. Non scrive e non cancella nulla. Scarica una volta l’intero canale: può richiedere tempo e traffico dati.'}
      </p>
      <button type="button" disabled={disabled || running} onClick={start}>
        {en ? 'Analyse space' : 'Analizza lo spazio'}
      </button>
      {running && (
        <p className="hint" role="status" aria-live="polite">
          <span className="suite-spinner" aria-hidden="true" />
          {en ? 'Analysis in progress' : 'Analisi in corso'} · {Math.floor(job.elapsed_s || 0)} s · {job.reads || 0}{' '}
          {en ? 'files read' : 'file letti'}
        </p>
      )}
      {(job.status === 'failed' || job.status === 'interrupted') && (
        <p className="hint" role="alert">
          {trBackend(job.error)}
        </p>
      )}
      {error && (
        <p className="hint" role="alert">
          {error}
        </p>
      )}
      {r && (
        <div role="status">
          <p>
            <strong>
              {size(r.bytes)} · {r.files} {en ? 'files' : 'file'}
            </strong>{' '}
            · {en ? 'format' : 'formato'} v{r.protocol}
          </p>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th scope="col">{en ? 'Content' : 'Contenuto'}</th>
                  <th scope="col">{en ? 'Files' : 'File'}</th>
                  <th scope="col">{en ? 'Size' : 'Dimensione'}</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(r.categories as Row)
                  .filter(([, value]) => value.files)
                  .map(([name, value]) => (
                    <tr key={name}>
                      <th scope="row">{labels[name] || name}</th>
                      <td>{value.files}</td>
                      <td>{size(value.bytes)}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
          {r.v1.events > 0 && (
            <>
              <p>
                {en
                  ? `v1: ${r.v1.events} revisions, of which ${r.v1.covered_by_v2.files} (${size(r.v1.covered_by_v2.bytes)}) are also in v2 pages.` +
                    (r.v1.attachment_base64_bytes
                      ? ` Attachments inside v1 packets: ${size(r.v1.attachment_base64_bytes)} before encryption.`
                      : '')
                  : `v1: ${r.v1.events} revisioni, di cui ${r.v1.covered_by_v2.files} (${size(r.v1.covered_by_v2.bytes)}) presenti anche nelle pagine v2.` +
                    (r.v1.attachment_base64_bytes
                      ? ` Allegati dentro i pacchetti v1: ${size(r.v1.attachment_base64_bytes)} prima della cifratura.`
                      : '')}
              </p>
              <p className="muted">
                {(en ? 'v1 by record type: ' : 'v1 per tipo di record: ') +
                  Object.entries(r.v1.by_kind as Row)
                    .map(([kind, value]) => `${kind} ${value.files} · ${size(value.bytes)}`)
                    .join('; ')}
              </p>
            </>
          )}
          {r.v2.event_copies > 0 && (
            <>
              <p>
                {en
                  ? `v2: ${r.v2.distinct_events} distinct revisions stored as ${r.v2.event_copies} copies. A consolidated copy would need about ${size(r.v2.consolidated_bytes)} in ${r.v2.consolidated_pages} pages.`
                  : `v2: ${r.v2.distinct_events} revisioni distinte salvate in ${r.v2.event_copies} copie. Una copia consolidata occuperebbe circa ${size(r.v2.consolidated_bytes)} in ${r.v2.consolidated_pages} pagine.`}
              </p>
              <p className="muted">
                {(en ? 'Pages by publishing device: ' : 'Pagine per dispositivo che le ha pubblicate: ') +
                  (r.v2.publishers as Row[])
                    .map(p => `${p.name} ${p.pages} · ${p.events} ${en ? 'revisions' : 'revisioni'} · ${size(p.bytes)}`)
                    .join('; ')}
              </p>
            </>
          )}
          <p>
            {en
              ? `Redundant space (duplicate pages, older catalogues, unused chunks): about ${size(r.reclaimable_bytes)}. Nothing is removed automatically: a consolidation command is not yet available.`
              : `Spazio ridondante (pagine duplicate, cataloghi precedenti, blocchi non usati): circa ${size(r.reclaimable_bytes)}. Nulla viene rimosso automaticamente: il comando di consolidamento non è ancora disponibile.`}
          </p>
          {(r.unreadable > 0 || r.v2.missing_chunks > 0) && (
            <p className="hint">
              {en
                ? `${r.unreadable} unreadable or altered files and ${r.v2.missing_chunks} missing chunks. Use Full channel verification to check them.`
                : `${r.unreadable} file illeggibili o alterati e ${r.v2.missing_chunks} blocchi mancanti. Usa Verifica completa del canale per controllarli.`}
            </p>
          )}
          <p className="muted">
            {en
              ? 'Read-only analysis: signatures are not verified and remote files are not changed.'
              : 'Analisi in sola lettura: le firme non vengono verificate e i file remoti non vengono modificati.'}
          </p>
        </div>
      )}
    </details>
  );
}
