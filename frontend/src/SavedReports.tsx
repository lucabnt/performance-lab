import {useEffect, useState} from 'react';
import {RecordCards} from '@cycling-suite/ui';
import {language, tr} from './i18n';
type Row = Record<string, any>;

export function SavedReports({api, run, download, workspace}: {api: any; run: any; download: any; workspace: string}) {
  const [reports, setReports] = useState<Row[]>([]),
    [search, setSearch] = useState(''),
    [format, setFormat] = useState(''),
    [loading, setLoading] = useState(true);
  const en = language === 'en';
  useEffect(() => {
    let current = true;
    setReports([]);
    setSearch('');
    setFormat('');
    setLoading(true);
    run(async () => {
      try {
        const rows = await api('reports');
        if (current) setReports(rows);
      } finally {
        if (current) setLoading(false);
      }
    });
    return () => {
      current = false;
    };
  }, [workspace]);
  const items = reports
    .map(r => {
      const c = r.context || {},
        title =
          [c.organization, c.group, c.season && (en ? 'Season ' : 'Stagione ') + c.season, c.athlete, c.test_date]
            .filter(Boolean)
            .join(' · ') || (r.test_id ? (en ? 'Individual test' : 'Test individuale') : tr('Storico aggregato'));
      const date = r.saved_at ? new Date(r.saved_at) : null;
      return {
        id: r.id,
        title,
        subtitle: r.format.toUpperCase(),
        details: [
          {
            label: en ? 'Created' : 'Creato il',
            value: date && !isNaN(date.getTime()) ? date.toLocaleString(en ? 'en-GB' : 'it-IT') : '—'
          },
          {label: en ? 'Report reference' : 'Riferimento report', value: r.id.slice(0, 8)}
        ],
        format: r.format
      };
    })
    .filter(
      r =>
        (!format || r.format === format) &&
        `${r.title} ${r.subtitle} ${r.id} ${r.details[0].value}`
          .toLocaleLowerCase()
          .includes(search.trim().toLocaleLowerCase())
    );
  return (
    <details className="panel protocol" aria-busy={loading}>
      <summary>{tr('Report conservati')}</summary>
      <p>{en ? 'Newest first · 5 reports per page.' : 'Dal più recente · 5 report per pagina.'}</p>
      <div className="form-grid">
        <label>
          {en ? 'Search saved reports' : 'Cerca nei report conservati'}
          <input type="search" value={search} onChange={e => setSearch(e.target.value)} />
        </label>
        <label>
          {en ? 'Format' : 'Formato'}
          <select value={format} onChange={e => setFormat(e.target.value)}>
            <option value="">{tr('Tutti')}</option>
            {Array.from(new Set(reports.map(r => String(r.format))))
              .sort()
              .map(f => (
                <option key={f} value={f}>
                  {f.toUpperCase()}
                </option>
              ))}
          </select>
        </label>
      </div>
      {loading ? (
        <p role="status">
          <span className="suite-spinner" aria-hidden="true" />
          {en ? 'Loading reports…' : 'Caricamento report…'}
        </p>
      ) : (
        <>
          <p role="status">
            {items.length} / {reports.length} {en ? 'reports' : 'report'}
          </p>
          {!items.length && (
            <p>
              {reports.length
                ? en
                  ? 'No reports match these filters.'
                  : 'Nessun report corrisponde ai filtri.'
                : tr('I report esportati saranno disponibili anche qui.')}
            </p>
          )}
          <RecordCards
            items={items}
            pageSize={5}
            resetKey={JSON.stringify([workspace, search, format])}
            locale={en ? 'en' : 'it'}
            actionLabel={tr('Scarica')}
            onOpen={id => {
              const r = reports.find(r => r.id === id);
              if (r)
                run(() =>
                  download(
                    `reports/${id}/download`,
                    `report-${id.slice(0, 8)}.${r.format === 'pdf' ? 'pdf' : r.format === 'json' ? 'json' : 'zip'}`
                  )
                );
            }}
          />
        </>
      )}
    </details>
  );
}
