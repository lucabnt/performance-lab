import {useState, useEffect} from 'react';
import {DataTable} from '@cycling-suite/ui';
import {anaerobicMetrics} from './anaerobic';
import {metricLabel, numberText} from './metrics';
import {tr} from './i18n';
import {historySeries, historyTraces, initialHistorySelection, historyCategories} from './historyChartModel';
type Row = Record<string, any>;

export function HistoryPanel({
  org,
  state,
  api,
  download,
  run,
  Plot
}: {
  org: string;
  state: Row;
  api: any;
  download: any;
  run: any;
  Plot: any;
}) {
  const [filters, setFilters] = useState<Row>({
    mode: 'athlete',
    dimension: 'season',
    season: '',
    group: '',
    athlete: '',
    protocol: ''
  });
  const [data, setData] = useState<Row | null>(null),
    [metric, setMetric] = useState('map_w'),
    [statistic, setStatistic] = useState('median');
  const [selection, setSelection] = useState<string[] | null>(null);
  const query = new URLSearchParams(filters).toString();
  useEffect(() => {
    let current = true;
    setData(null);
    run(async () => {
      const next = await api(`history/${org}?${query}`);
      if (current) setData(next);
    });
    return () => {
      current = false;
    };
  }, [org, query]);
  useEffect(() => {
    setSelection(null);
  }, [org, query, metric]);
  // Backend labels are needed for custom fields; built-in metrics use the localized frontend labels.
  const label = (m: string) => (m.startsWith('custom:') && data?.metric_labels?.[m]) || metricLabel(m);
  const change = (k: string, v: string) => setFilters(f => ({...f, [k]: v}));
  const protocols = state.protocol.filter((p: Row) => !p.organization_id || p.organization_id === org);
  const series = historySeries(data?.groups || [], protocols, metric);
  const selected = initialHistorySelection(series, selection),
    shown = series.filter(s => selected.includes(s.id));
  const metricOptions = [
    ...new Set([
      'map_w',
      'map_wkg',
      'threshold_w',
      'threshold_wkg',
      'ftp_w',
      'ftp_wkg',
      'weight_kg',
      'height_cm',
      'fthr_bpm',
      'fc_max_test_bpm',
      'lactate_2_w',
      'lactate_4_w',
      'vo2peak_l_min',
      'vo2peak_ml_kg_min',
      ...anaerobicMetrics,
      ...Object.keys(data?.metric_labels || {}).filter(
        m => !m.startsWith('custom:') || !filters.protocol || m.split(':')[1] === filters.protocol
      )
    ])
  ];
  const rows = shown.flatMap(s =>
    s.groups.map((g: Row) => ({...g, series: s.code, protocol: s.title, ...g.metrics[metric]}))
  );
  const columns = [
    {key: 'series', label: tr('Serie')},
    {key: 'label', label: tr('Gruppo')},
    {key: 'athletes', label: tr('Atleti')},
    {key: 'tests_selected', label: tr('Test')},
    ...['mean', 'median', 'min', 'max'].map(k => ({
      key: k,
      label: ({mean: tr('Media'), median: tr('Mediana'), min: 'Min', max: 'Max'} as Row)[k],
      render: (r: Row) => numberText(r[k])
    })),
    {key: 'n', label: tr('Validi')},
    {key: 'missing', label: tr('Mancanti')}
  ];
  return (
    <>
      <section className="panel protocol">
        <h2>{tr('Storici e confronti')}</h2>
        <div className="form-grid">
          <label>
            {tr('Metrica')}
            <select value={metric} onChange={e => setMetric(e.target.value)}>
              {metricOptions.map(m => (
                <option key={m} value={m}>
                  {label(m)}
                  {m.startsWith('custom:') ? ' · ' + protocols.find((p: Row) => p.id === m.split(':')[1])?.name : ''}
                  {data ? ' · ' + (data.coverage[m]?.valid || 0) + ' ' + tr('valori') : ''}
                </option>
              ))}
            </select>
          </label>
          <label>
            {tr('Protocollo e versione')}
            <select value={filters.protocol} onChange={e => change('protocol', e.target.value)}>
              <option value="">{tr('Tutti · scegli le serie sotto')}</option>
              {protocols.map((p: Row) => (
                <option key={p.id} value={p.id}>
                  {p.name} · {p.version}
                </option>
              ))}
            </select>
          </label>
          <label>
            {tr('Vista')}
            <select value={filters.dimension} onChange={e => change('dimension', e.target.value)}>
              {Object.entries({
                season: tr('Stagione'),
                category: tr('Categoria storica'),
                category_season: tr('Categoria / stagione'),
                category_year: tr('Anno di categoria'),
                category_year_season: tr('Anno categoria / stagione'),
                age: tr('Anno di età'),
                age_season: tr('Età / stagione'),
                cohort: tr('Coorte di nascita'),
                cohort_season: tr('Coorte / stagione'),
                athlete: tr('Atleta'),
                all: tr('Totale')
              }).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </label>
          <label>
            {tr('Statistica nel grafico')}
            <select value={statistic} onChange={e => setStatistic(e.target.value)}>
              <option value="median">{tr('Mediana')}</option>
              <option value="mean">{tr('Media')}</option>
            </select>
          </label>
        </div>
        <details>
          <summary>
            {tr('Filtra atleti, categorie e stagioni')}
            {filters.athlete || filters.group || filters.season || filters.mode !== 'athlete'
              ? ' · ' + tr('filtri attivi')
              : ''}
          </summary>
          <div className="form-grid">
            <label>
              {tr('Selezione')}
              <select value={filters.mode} onChange={e => change('mode', e.target.value)}>
                <option value="athlete">{tr('Ultimo test per atleta')}</option>
                <option value="tests">{tr('Tutti i test')}</option>
              </select>
            </label>
            <label>
              {tr('Stagione')}
              <input
                value={filters.season}
                onChange={e => change('season', e.target.value)}
                placeholder={tr('Tutte')}
              />
            </label>
            <label>
              {tr('Categoria')}
              <select value={filters.group} onChange={e => change('group', e.target.value)}>
                <option value="">{tr('Tutte')}</option>
                {state.group
                  .filter((g: Row) => g.organization_id === org)
                  .map((g: Row) => (
                    <option key={g.id} value={g.id}>
                      {g.name} {g.season}
                    </option>
                  ))}
              </select>
            </label>
            <label>
              {tr('Atleta')}
              <select value={filters.athlete} onChange={e => change('athlete', e.target.value)}>
                <option value="">{tr('Tutti')}</option>
                {state.athlete
                  .filter((a: Row) => a.organization_id === org && a.status !== 'deleted')
                  .map((a: Row) => (
                    <option key={a.id} value={a.id}>
                      {a.surname} {a.name}
                    </option>
                  ))}
              </select>
            </label>
          </div>
        </details>
      </section>
      {!data ? (
        <p role="status">{tr('Caricamento degli storici…')}</p>
      ) : !series.length ? (
        <section className="panel">
          <h3>{tr('Nessun valore per questa metrica')}</h3>
          <p>
            {tr(
              'Prova un’altra metrica o modifica i filtri. I protocolli senza valori utilizzabili non generano serie vuote.'
            )}
          </p>
        </section>
      ) : (
        <>
          <section className="panel protocol history-chart">
            <h3>
              {label(metric)} · {statistic === 'median' ? 'Mediana' : 'Media'}
            </h3>
            <p>
              {shown.length} / {series.length}{' '}
              {tr('serie visualizzate. All’apertura viene scelta la serie con più valori validi.')}
            </p>
            <details>
              <summary>
                {tr('Scegli le serie da confrontare (')}
                {selected.length}/4)
              </summary>
              <p>
                {tr(
                  'Ogni serie mantiene separati protocollo, versione, metodo, condizioni e origine della soglia. Seleziona fino a quattro serie per un confronto descrittivo; i risultati non vengono uniti.'
                )}
              </p>
              <div className="history-series" role="group" aria-label={tr('Serie del confronto')}>
                {series.map(s => (
                  <label className="history-series-option" key={s.id}>
                    <input
                      type="checkbox"
                      checked={selected.includes(s.id)}
                      disabled={selected.length >= 4 && !selected.includes(s.id)}
                      onChange={e =>
                        setSelection(e.target.checked ? [...selected, s.id] : selected.filter(id => id !== s.id))
                      }
                    />
                    <span>
                      <strong>
                        {s.code} · {s.title}
                      </strong>
                      <small>
                        {tr(s.method)} {tr('· origine soglia:')} {label(s.threshold_source)} · {s.valid} {tr('valori')}
                      </small>
                    </span>
                  </label>
                ))}
              </div>
              <button onClick={() => setSelection(null)}>{tr('Mostra solo la serie principale')}</button>
            </details>
            {shown.length > 0 ? (
              <>
                {new Set(shown.map(s => s.protocol_id)).size > 1 && (
                  <p className="hint">
                    {tr(
                      'Stai affiancando protocolli diversi: la stessa unità di misura non garantisce condizioni equivalenti. Medie e mediane restano separate per serie; verifica protocollo e metodo prima di interpretare le differenze.'
                    )}
                  </p>
                )}
                <Plot
                  data={historyTraces(shown, metric, statistic, filters.dimension)}
                  layout={{
                    height: 380,
                    margin: {l: 65, r: 25, t: 25, b: 95},
                    legend: {orientation: 'h', y: -0.25},
                    hovermode: 'closest',
                    yaxis: {title: {text: label(metric)}},
                    xaxis: {
                      type: 'category',
                      categoryorder: 'array',
                      categoryarray: historyCategories(shown),
                      title: {text: tr('Aggregazione selezionata')}
                    }
                  }}
                />
                <div className="history-series-key">
                  {shown.map(s => (
                    <p key={s.id}>
                      <strong>
                        {s.code} · {s.title}
                      </strong>
                      <small>
                        {tr(s.method)} {tr('· origine soglia:')} {label(s.threshold_source)}
                      </small>
                    </p>
                  ))}
                </div>
                <h3>{tr('Dati delle serie visualizzate')}</h3>
                <DataTable rows={rows} columns={columns} />
              </>
            ) : (
              <p className="hint">{tr('Seleziona almeno una serie per visualizzare il confronto.')}</p>
            )}
          </section>
        </>
      )}
      {data && (
        <details className="panel protocol">
          <summary>{tr('Copertura dati ed esportazione dell’archivio filtrato')}</summary>
          <DataTable
            rows={Object.entries(data.coverage).map(([key, v]: any) => ({key, ...v, missing: v.total - v.valid}))}
            columns={[
              {key: 'key', label: tr('Campo'), render: (r: Row) => label(r.key)},
              {key: 'valid', label: tr('Presenti')},
              {key: 'missing', label: tr('Mancanti')},
              {key: 'total', label: tr('Test')}
            ]}
          />
          <p>
            {tr(
              'I report includono tutti i protocolli dei filtri sopra, anche quelli non selezionati nel grafico. La selezione delle quattro serie riguarda il confronto interattivo.'
            )}
          </p>
          <div className="actions">
            {['md', 'pdf'].map(f => (
              <button
                key={f}
                onClick={() =>
                  run(() =>
                    download(
                      `history/${org}/report/${f}?${query}&metric=${encodeURIComponent(metric)}&statistic=${statistic}`,
                      `storico.${f === 'md' ? 'zip' : 'pdf'}`
                    )
                  )
                }
              >
                {tr('Esporta archivio filtrato ·')} {f.toUpperCase()}
              </button>
            ))}
          </div>
        </details>
      )}
    </>
  );
}
