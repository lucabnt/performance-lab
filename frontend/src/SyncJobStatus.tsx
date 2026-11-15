import {language} from './i18n';
type Row = Record<string, any>;
export function SyncJobStatus({sync, compact = false}: {sync: Row; compact?: boolean}) {
  const {job, error} = sync,
    en = language === 'en';
  if (!job || job.status === 'idle')
    return error ? (
      <p className="hint" role="alert">
        {error}
      </p>
    ) : null;
  const phases: Row = {
    preparing: en ? 'Preparing exchange' : 'Preparazione dello scambio',
    inventory: en ? 'Checking remote inventory' : 'Controllo inventario remoto',
    receiving: en ? 'Reading and checking files' : 'Lettura e verifica dei file',
    publishing: en ? 'Publishing and checking files' : 'Pubblicazione e verifica dei file'
  };
  const result = job.result,
    problem = result && (result.errors?.length || result.pending),
    conflicts = result?.conflicts;
  const outcome =
    job.status === 'interrupted'
      ? en
        ? 'Synchronization interrupted'
        : 'Sincronizzazione interrotta'
      : job.status === 'failed'
        ? en
          ? 'Synchronization failed'
          : 'Sincronizzazione non riuscita'
        : problem
          ? en
            ? 'Exchange requires attention'
            : 'Scambio da completare'
          : conflicts
            ? en
              ? 'Exchange finished with conflicts'
              : 'Scambio terminato con conflitti'
            : en
              ? 'Synchronization completed'
              : 'Sincronizzazione completata';
  const details = (
    <>
      <p>
        {job.full_verification
          ? en
            ? 'Full verification: existing packets are read again.'
            : 'Verifica completa: rilettura anche dei pacchetti già acquisiti.'
          : en
            ? 'Incremental exchange: already acquired packets are skipped. The remote inventory and signed access controls are still checked.'
            : 'Scambio incrementale: i pacchetti già acquisiti vengono saltati. Inventario remoto e controlli firmati degli accessi vengono comunque verificati.'}
      </p>
      {result && (
        <p>
          {result.published} {en ? 'published' : 'pubblicati'} · {result.received}{' '}
          {en ? 'revisions received' : 'revisioni ricevute'} · {result.downloaded_packets ?? 0}{' '}
          {en ? 'packets read' : 'pacchetti letti'} · {result.known_packets_skipped ?? 0}{' '}
          {en ? 'already known, skipped' : 'già noti, saltati'} · {result.pending} {en ? 'pending' : 'in attesa'} ·{' '}
          {result.conflicts} {en ? 'conflicts' : 'conflitti'}
        </p>
      )}
      {job.error && <p role="alert">{job.error}</p>}
    </>
  );
  if (sync.running)
    return (
      <div className="hint" role="status" aria-live="polite">
        <span className="suite-spinner" aria-hidden="true" />
        <strong>
          {en ? 'Synchronization in progress' : 'Sincronizzazione in corso'} · {phases[job.phase] || ''}
        </strong>
        <p>
          {Math.floor(job.elapsed_s || 0)} s · {job.reads || 0} {en ? 'files read' : 'file letti'} · {job.writes || 0}{' '}
          {en ? 'new files written' : 'nuovi file scritti'}
        </p>
        {!compact && details}
        {error && (
          <p>
            {en
              ? 'Status temporarily unavailable; checking again.'
              : 'Stato momentaneamente non disponibile; nuovo controllo in corso.'}
          </p>
        )}
      </div>
    );
  return compact ? (
    <details className="hint">
      <summary>
        {outcome} · {job.elapsed_s ?? 0} s
      </summary>
      {details}
    </details>
  ) : (
    <div role="status">
      <strong>
        {outcome} · {job.elapsed_s ?? 0} s
      </strong>
      {details}
    </div>
  );
}
