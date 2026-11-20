import {FormActions} from '@cycling-suite/ui';
import {maturityText} from './maturityText';
import {useEffect, useState} from 'react';
import {language, tr} from './i18n';
import {numberText} from './metrics';
type Row = Record<string, any>;
const optional: Record<string, string> = {
  sitting_height_cm: 'Statura seduta · cm',
  arm_span_cm: 'Apertura braccia · cm',
  lower_limb_cm: 'Lunghezza arti inferiori · cm',
  mother_height_cm: 'Statura madre biologica · cm',
  father_height_cm: 'Statura padre biologico · cm',
  adult_height_cm: 'Statura adulta prevista esternamente · cm',
  adult_height_error_cm: 'Incertezza esterna della previsione · cm'
};
const enOptional: Record<string, string> = {
  sitting_height_cm: 'Sitting height · cm',
  arm_span_cm: 'Arm span · cm',
  lower_limb_cm: 'Lower limb length · cm',
  mother_height_cm: 'Biological mother height · cm',
  father_height_cm: 'Biological father height · cm',
  adult_height_cm: 'Externally predicted adult height · cm',
  adult_height_error_cm: 'External prediction uncertainty · cm'
};
export function MeasurementEditor({
  athlete,
  original,
  api,
  done,
  run
}: {
  athlete: string;
  original?: Row;
  api: any;
  done: any;
  run: any;
}) {
  const en = language === 'en';
  const [draft, setDraft] = useState<Row>({
      date: new Date().toLocaleDateString('en-CA'),
      source: 'misurato',
      quality: 'valid',
      precision_cm: 0.1,
      ...original
    }),
    [reason, setReason] = useState('');
  const field = (k: string, label: string) => (
    <label key={k}>
      {label}
      <input
        type="number"
        min="0.001"
        step="any"
        value={draft[k] ?? ''}
        onChange={e => setDraft(d => ({...d, [k]: e.target.value === '' ? null : Number(e.target.value)}))}
      />
    </label>
  );
  return (
    <form
      onSubmit={e => {
        e.preventDefault();
        run(async () => {
          const keys = [
            'date',
            'weight_kg',
            'height_cm',
            'perineal_height_cm',
            'source',
            'origin',
            'quality',
            'precision_cm',
            'model_sex',
            ...Object.keys(optional),
            'adult_height_method',
            'adult_height_source',
            'notes'
          ];
          const measurement = {
            athlete_id: athlete,
            ...Object.fromEntries(keys.filter(k => draft[k] != null && draft[k] !== '').map(k => [k, draft[k]]))
          };
          const r = await api(
            original ? 'measurements/' + original.id : 'measurements',
            original ? {measurement, base: original.revision, reason} : measurement,
            original ? 'PUT' : 'POST'
          );
          await done(r);
        });
      }}
    >
      <h2>{en ? 'Anthropometric measurement' : 'Rilevazione antropometrica'}</h2>
      <div className="form-grid">
        <label>
          {en ? 'Date' : 'Data'}
          <input
            required
            type="date"
            value={draft.date}
            onChange={e => setDraft(d => ({...d, date: e.target.value}))}
          />
        </label>
        {field('weight_kg', en ? 'Body mass · kg' : 'Massa corporea · kg')}
        {field('height_cm', en ? 'Height · cm' : 'Statura · cm')}
        {field('perineal_height_cm', en ? 'Perineal height (inseam) · cm' : 'Altezza perineale (cavallo) · cm')}
        <label>
          {en ? 'Source' : 'Fonte'}
          <select value={draft.source} onChange={e => setDraft(d => ({...d, source: e.target.value}))}>
            {['misurato', 'arrotondato', 'dichiarato', 'derivato', 'stimato'].map((v, i) => (
              <option key={v} value={v}>
                {en ? ['Measured', 'Rounded', 'Declared', 'Derived', 'Estimated'][i] : v}
              </option>
            ))}
          </select>
        </label>
        <label>
          {en ? 'Origin' : 'Origine'}
          <input value={draft.origin || ''} onChange={e => setDraft(d => ({...d, origin: e.target.value}))} />
        </label>
        <label>
          {en ? 'Quality' : 'Qualità'}
          <select value={draft.quality} onChange={e => setDraft(d => ({...d, quality: e.target.value}))}>
            {['valid', 'uncertain', 'excluded'].map((v, i) => (
              <option key={v} value={v}>
                {
                  (en
                    ? ['Confirmed', 'To verify', 'Exclude from growth models']
                    : ['Confermata', 'Da verificare', 'Escludi dai modelli di crescita'])[i]
                }
              </option>
            ))}
          </select>
        </label>
        {field('precision_cm', en ? 'Height reading precision · cm' : 'Precisione di lettura statura · cm')}
      </div>
      <details>
        <summary>
          {en
            ? 'Optional advanced measurements and external prediction'
            : 'Misure avanzate facoltative e previsione esterna'}
        </summary>
        <p>
          {en
            ? 'These fields are optional. Parent heights alone do not activate an unverified adult-height equation.'
            : 'Questi dati sono facoltativi. Le stature dei genitori da sole non attivano una formula di previsione adulta non verificata.'}
        </p>
        <div className="form-grid">
          {Object.entries(optional).map(([k, label]) => field(k, en ? enOptional[k] : label))}
          <label>
            {en
              ? 'M/F parameter for the model (otherwise profile sex)'
              : 'Parametro M/F per il modello (altrimenti sesso nel profilo)'}
            <select value={draft.model_sex || ''} onChange={e => setDraft(d => ({...d, model_sex: e.target.value}))}>
              <option value="">{en ? 'Use profile if available' : 'Usa il profilo, se disponibile'}</option>
              <option>M</option>
              <option>F</option>
            </select>
          </label>
          {['adult_height_method', 'adult_height_source'].map((k, i) => (
            <label key={k}>
              {en
                ? ['External prediction method', 'External prediction source'][i]
                : ['Metodo della previsione esterna', 'Fonte della previsione esterna'][i]}
              <input value={draft[k] || ''} onChange={e => setDraft(d => ({...d, [k]: e.target.value}))} />
            </label>
          ))}
        </div>
      </details>
      <label>
        {en ? 'Notes' : 'Note'}
        <textarea value={draft.notes || ''} onChange={e => setDraft(d => ({...d, notes: e.target.value}))} />
      </label>
      {original && (
        <label>
          {en ? 'Reason for revision' : 'Motivo della revisione'}
          <input required minLength={3} value={reason} onChange={e => setReason(e.target.value)} />
        </label>
      )}
      <FormActions>
        <button type="submit" className="primary">
          {en ? 'Save measurement' : 'Salva rilevazione'}
        </button>
      </FormActions>
    </form>
  );
}
function phvStatusText(phv: Row, en: boolean) {
  const p = phv.progress || {};
  const texts: Record<string, [string, string]> = {
    insufficient: [
      `Servono almeno ${p.required_statures} stature misurate valide consecutive a 90–400 giorni.`,
      `At least ${p.required_statures} consecutive valid measured heights 90–400 days apart are required.`
    ],
    not_confirmed: [
      'Picco non ancora confermato: il massimo è negli ultimi intervalli.',
      'Peak not yet confirmed: the maximum is in the latest intervals.'
    ],
    before_data: [
      'Il massimo è nei primi intervalli: il picco potrebbe precedere le misure disponibili.',
      'The maximum is in the first intervals: the peak may precede the available measurements.'
    ],
    anomaly: [
      'Calo di statura o velocità anomala vicino al massimo: verificare le misure.',
      'Height decrease or anomalous velocity near the maximum: verify the measurements.'
    ]
  };
  const t = texts[phv.status];
  return t ? t[en ? 1 : 0] : maturityText(phv.reason);
}
function phvProgressText(p: Row, en: boolean) {
  const statures = en
    ? `Valid stretch: ${p.statures} heights (minimum ${p.required_statures})`
    : `Tratto valido: ${p.statures} stature (minimo ${p.required_statures})`;
  if (p.before_peak == null) return statures;
  return en
    ? `${statures} · ${p.before_peak} intervals before and ${p.after_peak} after the maximum (${p.required_each_side} needed on each side)`
    : `${statures} · ${p.before_peak} intervalli prima e ${p.after_peak} dopo il massimo (ne servono ${p.required_each_side} per lato)`;
}
function excludedText(e: Row, en: boolean) {
  const texts: Record<string, [string, string]> = {
    not_measured: [
      'statura non misurata o qualità non confermata, non usata.',
      'height not measured or quality unconfirmed, not used.'
    ],
    close: [
      `a ${e.days} giorni dalla statura precedente usata (${e.after}): saltata, non bloccante.`,
      `${e.days} days after the previous used height (${e.after}): skipped, not blocking.`
    ],
    gap: ['intervallo oltre 400 giorni: la serie viene divisa.', 'interval over 400 days: the series is split.'],
    decrease: ['statura diminuita: verificare le misure.', 'height decreased: verify the measurements.'],
    velocity: [
      'velocità oltre il controllo prudenziale: verificare le misure.',
      'velocity above the conservative check: verify the measurements.'
    ]
  };
  const t = texts[e.cause];
  return t ? t[en ? 1 : 0] : e.reason;
}
function Value({r, unit = ''}: {r?: Row; unit?: string}) {
  return (
    <span title={maturityText(r?.reason || r?.uncertainty)}>
      {numberText(r?.value)} {r?.value != null ? unit : ''}
      {r?.reason && <small className="maturity-note"> · {maturityText(r.reason)}</small>}
    </span>
  );
}
export function MaturationPanel({
  athlete,
  revisionKey,
  api,
  run,
  canEdit,
  Plot
}: {
  athlete: Row;
  revisionKey: string;
  api: any;
  run: any;
  canEdit: boolean;
  Plot: any;
}) {
  const en = language === 'en';
  const [on, setOn] = useState(new Date().toLocaleDateString('en-CA')),
    [response, setResponse] = useState<Row | null>(null),
    [view, setView] = useState('preview'),
    [reason, setReason] = useState(''),
    [error, setError] = useState('');
  const load = () => api(`athletes/${athlete.id}/maturation?on=${on}`);
  useEffect(() => {
    let cancelled = false;
    setResponse(null);
    setError('');
    load()
      .then((r: Row) => {
        if (!cancelled) setResponse(r);
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, [athlete.id, athlete.revision, revisionKey, on]);
  const a = view === 'preview' ? response?.preview : response?.history.find((r: Row) => r.id === view)?.analysis;
  const latest = a?.series.filter((s: Row) => s.height_cm != null).at(-1);
  const hv = a?.hv.at(-1),
    offset = latest?.models.moore;
  return (
    <section className="panel protocol maturity-section">
      <h2>{en ? 'Growth and maturation' : 'Crescita e maturazione'}</h2>
      <p>
        {en
          ? 'Current preview is separate from saved analyses. Save an explicit snapshot to preserve methods and inputs in reports and exports.'
          : 'L’anteprima corrente è distinta dalle analisi conservate. Salva uno snapshot esplicito per conservare metodi e dati nei report e negli export.'}
      </p>
      <div className="form-grid">
        <label>
          {en ? 'Reference date' : 'Data di riferimento'}
          <input
            type="date"
            value={on}
            onChange={e => {
              setOn(e.target.value);
              setView('preview');
            }}
          />
        </label>
        <label>
          {en ? 'Analysis to display' : 'Analisi da visualizzare'}
          <select value={view} onChange={e => setView(e.target.value)}>
            <option value="preview">{en ? 'Current preview (not saved)' : 'Anteprima corrente (non salvata)'}</option>
            {response?.history.map((r: Row) => (
              <option key={r.id} value={r.id}>
                {r.analysis.on} · {r.created_at.slice(0, 16)} · {r.reason}
              </option>
            ))}
          </select>
        </label>
      </div>
      {error && <p role="alert">{error}</p>}
      {!a && !error && <p>{en ? 'Loading…' : 'Caricamento…'}</p>}
      {a && (
        <>
          <p>
            {en ? 'Chronological age band' : 'Fascia di età cronologica'}: <strong>{maturityText(a.age_band)}</strong> ·{' '}
            {en
              ? 'This guides display priority, not biological classification.'
              : 'Orienta la priorità di lettura, non classifica la maturazione biologica.'}
          </p>
          <div className="stats">
            <div className="stat">
              <small>HV</small>
              <strong>
                {numberText(hv?.value)} {tr('cm/anno')}
              </strong>
              <span>
                {hv
                  ? `${hv.from} → ${hv.to} · ${hv.days} ${en ? 'days' : 'giorni'}`
                  : en
                    ? 'At least two dated heights needed'
                    : 'Servono almeno due stature datate'}
              </span>
              {hv?.reason && <p>{maturityText(hv.reason)}</p>}
            </div>
            {a.age_years != null && a.age_years < 16 && (
              <div className="stat">
                <small>{en ? 'Estimated maturity offset (Moore)' : 'Maturity offset stimato (Moore)'}</small>
                <strong>
                  {numberText(offset?.value)} {en ? 'years' : 'anni'}
                </strong>
                <span>{latest?.date}</span>
                <p>
                  {maturityText(offset?.reason) ||
                    (en
                      ? 'Anthropometric estimate; no individual confidence interval.'
                      : 'Stima antropometrica; nessun intervallo individuale validato.')}
                </p>
              </div>
            )}
            <div className="stat">
              <small>{en ? 'Longitudinal exploratory PHV' : 'PHV longitudinale esplorativo'}</small>
              <strong>
                {numberText(a.phv.value)} {tr('cm/anno')}
              </strong>
              <span>{a.phv.date || (a.phv.status ? phvStatusText(a.phv, en) : maturityText(a.phv.reason))}</span>
              {a.phv.aphv_years != null && (
                <p>
                  APHV {numberText(a.phv.aphv_years)} {en ? 'years' : 'anni'}
                </p>
              )}
              {a.phv.progress && <p>{phvProgressText(a.phv.progress, en)}</p>}
            </div>
            {a.hv_max_observed && (
              <div className="stat">
                <small>{en ? 'Highest observed HV' : 'HV massima osservata'}</small>
                <strong>
                  {numberText(a.hv_max_observed.value)} {tr('cm/anno')}
                </strong>
                <span>
                  {a.hv_max_observed.value != null
                    ? `${a.hv_max_observed.from} → ${a.hv_max_observed.to}`
                    : en
                      ? 'Needs one 90–400 day interval between valid measured heights'
                      : 'Serve un intervallo di 90–400 giorni tra stature misurate e valide'}
                </span>
                {a.hv_max_observed.value != null && (
                  <p>
                    {en
                      ? 'Highest mean velocity observed so far; it is not PHV and does not confirm the peak.'
                      : 'Massimo delle velocità medie osservate finora; non è il PHV e non conferma il picco.'}
                  </p>
                )}
              </div>
            )}
          </div>
          {a.phv.status && a.phv.status !== 'available' && (
            <p className="hint">
              {en
                ? 'To follow the growth peak, measure height every 3–4 months with the same procedure (source “measured”, quality confirmed). PHV is only recognised once the velocity has started to decrease.'
                : 'Per seguire il picco di crescita misurare la statura ogni 3–4 mesi con la stessa procedura (fonte «misurato», qualità confermata). Il PHV si riconosce solo dopo che la velocità ha iniziato a diminuire.'}
            </p>
          )}
          {a.phv.excluded?.length > 0 && (
            <details>
              <summary>
                {en
                  ? `Heights not used for PHV (${a.phv.excluded.length})`
                  : `Stature non usate per il PHV (${a.phv.excluded.length})`}
              </summary>
              <ul>
                {a.phv.excluded.map((e: Row, i: number) => (
                  <li key={i}>
                    {e.date || `${e.from} → ${e.to}`}: {excludedText(e, en)}
                  </li>
                ))}
              </ul>
            </details>
          )}
          {a.age_years >= 18 && a.stability && (
            <p className="hint">{a.stability.interpretation || a.stability.reason}</p>
          )}
          <Plot
            data={[
              {
                x: a.hv.map((r: Row) => r.mid_date),
                y: a.hv.map((r: Row) => r.value),
                name: tr('HV · cm/anno'),
                type: 'scatter',
                mode: 'lines+markers',
                connectgaps: false
              }
            ]}
            layout={{
              xaxis: {title: {text: en ? 'Interval midpoint' : 'Centro dell’intervallo'}},
              yaxis: {title: {text: tr('cm/anno')}}
            }}
          />
          <h3>{en ? 'All dated estimates' : 'Tutte le stime datate'}</h3>
          <div className="maturity-table">
            <table>
              <thead>
                <tr>
                  {(en
                    ? ['Date', 'Age', 'Height cm', 'Moore offset / APHV (years)', 'Mirwald offset / APHV (years)']
                    : ['Data', 'Età', 'Statura cm', 'Moore offset / APHV (anni)', 'Mirwald offset / APHV (anni)']
                  ).map(v => (
                    <th key={v}>{v}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[...a.series]
                  .sort((x: Row, y: Row) => y.date.localeCompare(x.date))
                  .map((r: Row) => (
                    <tr key={r.revision}>
                      <td>{r.date}</td>
                      <td>{numberText(r.age_years)}</td>
                      <td>{numberText(r.height_cm)}</td>
                      {['moore', 'mirwald'].map(k => (
                        <td key={k}>
                          <Value r={r.models[k]} />
                          {r.models[k].aphv_years != null && <> / {numberText(r.models[k].aphv_years)}</>}
                        </td>
                      ))}
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
          <details>
            <summary>
              {en
                ? 'Optional indices and proportions (not priority)'
                : 'Indici facoltativi e proporzioni (non prioritari)'}
            </summary>
            <div className="maturity-table">
              <table>
                <thead>
                  <tr>
                    {(en
                      ? [
                          'Date',
                          '%PAH',
                          'Residual cm',
                          'Sitting/height %',
                          'Arm span/height %',
                          'Leg/height %',
                          'Leg velocity cm/year'
                        ]
                      : [
                          'Data',
                          '%PAH',
                          'Residuo cm',
                          'Seduta/statura %',
                          'Braccia/statura %',
                          'Arti/statura %',
                          'Crescita arti cm/anno'
                        ]
                    ).map(v => (
                      <th key={v}>{v}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {[...a.series]
                    .sort((x: Row, y: Row) => y.date.localeCompare(x.date))
                    .map((r: Row) => (
                      <tr key={r.revision}>
                        <td>{r.date}</td>
                        {[
                          'pah',
                          'residual',
                          'sitting_height_pct',
                          'arm_span_pct',
                          'lower_limb_pct',
                          'limb_velocity'
                        ].map(k => (
                          <td key={k}>
                            <Value r={r.optional[k]} />
                          </td>
                        ))}
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </details>
          <details>
            <summary>{en ? 'Methods, quality and limitations' : 'Metodi, qualità e limiti'}</summary>
            <p>
              {tr('Moore: statura/età,')} {en ? 'age domain' : 'dominio di età'}{' '}
              {tr('M 10–16 / F 9–14. Mirwald: statura, massa e statura seduta, M 12–16 / F 9–14.')}{' '}
              {en
                ? 'Product gates, not diagnostic ranges.'
                : 'Limiti prudenziali del prodotto, non intervalli diagnostici.'}
            </p>
            <p>
              {tr('HV: 90–400')} {en ? 'days between valid measured heights' : 'giorni tra stature misurate e valide'}.{' '}
              {a.phv.method_id === 'phv-local-quadratic/2'
                ? en
                  ? 'PHV: at least 6 consecutive valid measured heights in the stretch containing the maximum, two intervals on each side; heights closer than 90 days or not measured are skipped, gaps over 400 days split the series, a decrease or anomalous velocity touching the window blocks it. Local quadratic fit to five interval velocities with at least 180 days support on each side. No interpolation.'
                  : 'PHV: almeno 6 stature misurate valide consecutive nel tratto del massimo, due intervalli per lato; stature a meno di 90 giorni o non misurate vengono saltate, buchi oltre 400 giorni dividono la serie, un calo o una velocità anomala a ridosso della finestra la bloccano. Fit quadratico locale su cinque velocità con supporto di almeno 180 giorni per lato. Nessuna interpolazione.'
                : en
                  ? 'PHV (earlier version): ≥7 heights, ≥2 years; local quadratic fit to five interval velocities and at least 180 days support on each side.'
                  : 'PHV (versione precedente): ≥7 stature, ≥2 anni; fit quadratico locale su cinque velocità con supporto di almeno 180 giorni per lato.'}
            </p>
            {a.warnings.map((w: string) => (
              <p key={w}>{maturityText(w)}</p>
            ))}
            <p>
              {en ? 'Reference' : 'Riferimento'}:{' '}
              <a href="https://doi.org/10.1007/s40279-017-0750-y" target="_blank" rel="noreferrer">
                {tr('Kozieł & Malina — validation of maturity equations')}
              </a>
              . {a.engine}
            </p>
          </details>
          {view === 'preview' && canEdit && (
            <>
              <label>
                {en ? 'Reason for saving this analysis' : 'Motivo di conservazione dell’analisi'}
                <input value={reason} minLength={3} onChange={e => setReason(e.target.value)} />
              </label>
              <button
                disabled={reason.trim().length < 3}
                onClick={() =>
                  run(async () => {
                    const r = await api(`athletes/${athlete.id}/maturation`, {
                      on,
                      input_hash: a.input_hash,
                      reason: reason.trim()
                    });
                    setResponse(await load());
                    setView(r.id);
                    setReason('');
                  })
                }
              >
                {en ? 'Save analysis snapshot' : 'Conserva analisi con metodo e dati'}
              </button>
            </>
          )}
        </>
      )}
    </section>
  );
}
