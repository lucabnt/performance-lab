import {tr, trBackend} from './i18n';
import {FormActions} from '@cycling-suite/ui';
import {useState} from 'react';
import {ProtocolEditor} from './features';
import {anaerobicTypes} from './anaerobic';
import {FieldSchemaEditor, FieldValues, CustomValuesDisplay} from './customFields';
import {TraceImporter} from './analysis';
type Row = Record<string, any>;
export const protocolType = (p: Row) =>
  tr(p.test_type === 'custom' ? 'Personalizzato' : anaerobicTypes[p.test_type] || 'Incrementale');
export function ProtocolDesigner({
  org,
  original,
  api,
  run,
  done
}: {
  org: string;
  original?: Row;
  api: any;
  run: any;
  done: any;
}) {
  const [kind, setKind] = useState(original?.test_type || 'incremental');
  return (
    <>
      <h2>{tr(original ? 'Nuova versione di protocollo' : 'Crea protocollo')}</h2>
      <label>
        {tr('Famiglia di test')}
        <select disabled={!!original} value={kind} onChange={e => setKind(e.target.value)}>
          <option value="incremental">{tr('Incrementale aerobico')}</option>
          {Object.entries(anaerobicTypes).map(([k, v]) => (
            <option key={k} value={k}>
              {tr(String(v))}
            </option>
          ))}
          <option value="custom">{tr('Personalizzato · senza calcoli fisiologici automatici')}</option>
        </select>
      </label>
      {kind === 'incremental' ? (
        <ProtocolEditor key={kind} original={original} {...{org, api, run, done}} />
      ) : (
        <SpecialProtocol key={kind} kind={kind} original={original} {...{org, api, run, done}} />
      )}
    </>
  );
}
function SpecialProtocol({
  kind,
  org,
  original,
  api,
  run,
  done
}: {
  kind: string;
  org: string;
  original?: Row;
  api: any;
  run: any;
  done: any;
}) {
  const custom = kind === 'custom';
  const [draft, setDraft] = useState<Row>({
    name: original?.name || (custom ? '' : anaerobicTypes[kind]),
    reason: '',
    description: original?.description || '',
    duration_s: kind === 'sprint' ? 6 : kind === 'wingate30' ? 30 : 15,
    torque_nm_kg: kind === 'wingate15' ? 0.7 : null,
    start: 'unknown',
    position: 'unknown',
    device: '',
    warmup: '',
    load_description: '',
    peak_window_s: 1,
    end_window_s: 1,
    max_gap_s: 2,
    coverage_min: 0.95,
    ...original?.anaerobic_spec,
    family: original?.family || kind,
    version: '',
    custom_fields: original?.custom_fields || [],
    custom_values: original?.custom_values || {}
  });
  const edit = (k: string, v: any) => setDraft(d => ({...d, [k]: v}));
  return (
    <form
      onSubmit={e => {
        e.preventDefault();
        run(async () => {
          const common = {
            organization_id: org,
            name: draft.name,
            family: draft.family,
            version: draft.version,
            parent_id: original?.id || null,
            reason: draft.reason,
            custom_fields: draft.custom_fields,
            custom_values: draft.custom_values
          };
          await api(
            custom ? 'custom/protocols' : 'anaerobic/protocols',
            custom
              ? {...common, description: draft.description}
              : {
                  ...common,
                  code: draft.family,
                  family: kind,
                  ...Object.fromEntries(
                    [
                      'duration_s',
                      'torque_nm_kg',
                      'start',
                      'position',
                      'device',
                      'warmup',
                      'load_description',
                      'peak_window_s',
                      'end_window_s',
                      'max_gap_s',
                      'coverage_min'
                    ].map(k => [k, draft[k]])
                  )
                }
          );
          await done();
        });
      }}
    >
      <div className="form-grid">
        {[
          ['name', 'Nome del protocollo'],
          ['family', 'Codice'],
          ['version', 'Nuova versione'],
          ['reason', 'Motivo / descrizione modifica']
        ].map(([k, label]) => (
          <label key={k}>
            {tr(label)}
            <input required={k !== 'reason' || !!original} value={draft[k]} onChange={e => edit(k, e.target.value)} />
          </label>
        ))}
      </div>
      {custom ? (
        <label>
          {tr('Metodo e istruzioni')}
          <textarea value={draft.description} onChange={e => edit('description', e.target.value)} />
        </label>
      ) : (
        <>
          <div className="form-grid">
            {[
              ['duration_s', 'Durata · s'],
              ['torque_nm_kg', 'Coppia frenante · N·m/kg (facoltativa)'],
              ['peak_window_s', 'Finestra picco · s'],
              ['end_window_s', 'Finestra finale · s'],
              ['max_gap_s', 'Intervallo massimo campioni · s']
            ].map(([k, label]) => (
              <label key={k}>
                {tr(label)}
                <input
                  type="number"
                  step="any"
                  disabled={k === 'duration_s' && kind !== 'sprint'}
                  value={draft[k] ?? ''}
                  onChange={e => edit(k, e.target.value === '' ? null : Number(e.target.value))}
                />
              </label>
            ))}
            <label>
              {tr('Partenza')}
              <select value={draft.start} onChange={e => edit('start', e.target.value)}>
                <option value="unknown">{tr('Non documentata')}</option>
                <option value="stationary">{tr('Da fermo')}</option>
                <option value="flying">{tr('Lanciata')}</option>
              </select>
            </label>
            <label>
              {tr('Posizione')}
              <select value={draft.position} onChange={e => edit('position', e.target.value)}>
                <option value="unknown">{tr('Non documentata')}</option>
                <option value="seated">{tr('Seduto')}</option>
                <option value="standing">{tr('In piedi')}</option>
                <option value="mixed">{tr('Mista')}</option>
              </select>
            </label>
            {[
              ['device', 'Dispositivo'],
              ['warmup', 'Riscaldamento'],
              ['load_description', 'Modalità di applicazione del carico']
            ].map(([k, label]) => (
              <label key={k}>
                {tr(label)}
                <input value={draft[k]} onChange={e => edit(k, e.target.value)} />
              </label>
            ))}
          </div>
          <p className="hint">
            {tr(
              'Le finestre e le condizioni fanno parte della versione. Cambiarle crea un metodo distinto nei confronti.'
            )}
          </p>
        </>
      )}
      <FieldSchemaEditor
        fields={draft.custom_fields}
        onChange={v => {
          edit('custom_fields', v);
          edit(
            'custom_values',
            Object.fromEntries(
              Object.entries(draft.custom_values).filter(([k]) => v.some(f => f.key === k && f.scope === 'protocol'))
            )
          );
        }}
      />
      <FieldValues
        fields={draft.custom_fields}
        values={draft.custom_values}
        onChange={v => edit('custom_values', v)}
        scope="protocol"
      />
      <FormActions>
        <button className="primary">{tr('Pubblica versione immutabile')}</button>
      </FormActions>
    </form>
  );
}
export function NewTestChoice({
  org,
  state,
  selected,
  onChoose,
  onProtocols
}: {
  org: string;
  state: Row;
  selected: string;
  onChoose: any;
  onProtocols: any;
}) {
  const protocols = state.protocol.filter(
    (p: Row) =>
      (p.status || 'active') === 'active' && (!p.organization_id || p.organization_id === org) && !p.historical
  );
  const [id, setId] = useState(protocols[0]?.id || '');
  const p = protocols.find((p: Row) => p.id === id);
  return (
    <>
      <h2>{tr('Registra una prova')}</h2>
      <p>{tr('Scegli un protocollo già definito. Per creare o modificare un protocollo usa la pagina Protocolli.')}</p>
      {!protocols.length ? (
        <p className="hint">{tr('Nessun protocollo attivo: definiscine uno, anche manualmente e senza ERG.')}</p>
      ) : (
        <>
          <label>
            {tr('Protocollo e versione')}
            <select value={id} onChange={e => setId(e.target.value)}>
              {protocols.map((p: Row) => (
                <option key={p.id} value={p.id}>
                  {protocolType(p)} · {p.name} · {p.version}
                </option>
              ))}
            </select>
          </label>
          {p && (
            <p>
              {protocolType(p)}
              {p.test_type === 'custom'
                ? ' · ' + tr('osservazioni e campi definiti dall’operatore, senza formule automatiche.')
                : p.anaerobic_spec
                  ? ' · ' + tr('durata') + ' ' + p.anaerobic_spec.duration_s + ' s.'
                  : !p.definition.segments.length
                    ? ' · ' + tr('solo scheda, inserimento manuale.')
                    : ''}
            </p>
          )}
          <div className="actions">
            <button className="primary" disabled={!p} onClick={() => onChoose(p, 'manual', selected)}>
              {tr('Inserisci risultati manuali')}
            </button>
            <button
              disabled={!p || (!p.test_type && !p.definition.segments.length)}
              onClick={() => onChoose(p, 'trace', selected)}
            >
              {tr('Importa FIT / CSV')}
            </button>
          </div>
        </>
      )}
      <button onClick={onProtocols}>{tr('Vai ai protocolli')}</button>
    </>
  );
}
export function CustomTestEditor({
  org,
  state,
  protocol,
  api,
  run,
  done,
  Plot,
  original,
  mode = 'manual',
  selected = ''
}: {
  org: string;
  state: Row;
  protocol: Row;
  api: any;
  run: any;
  done: any;
  Plot: any;
  original?: Row;
  mode?: string;
  selected?: string;
}) {
  const [draft, setDraft] = useState<Row>({
    athlete_id:
      original?.athlete_id ||
      selected ||
      state.athlete.find((a: Row) => a.organization_id === org && a.status !== 'archived' && a.status !== 'deleted')
        ?.id ||
      '',
    date: original?.date || new Date().toLocaleDateString('en-CA'),
    settings: {offset_s: 0, end_s: null, custom_values: {}, extra_fields: [], ...original?.settings},
    notes: original?.notes || '',
    reason: ''
  });
  const [pick, setPick] = useState('');
  const [trace, setTrace] = useState<Row | null>(
      original?.trace_hash ? {hash: original.trace_hash, samples: original.samples} : null
    ),
    [source, setSource] = useState(original?.trace_hash ? 'trace' : mode),
    [preview, setPreview] = useState<Row | null>(null);
  const edit = (k: string, v: any) => {
    setDraft(d => ({...d, [k]: v}));
    setPreview(null);
  };
  const setting = (k: string, v: any) => edit('settings', {...draft.settings, [k]: v});
  const payload = () => ({
    athlete_id: draft.athlete_id,
    protocol_id: protocol.id,
    date: draft.date,
    settings: draft.settings,
    trace_hash: source === 'trace' ? trace?.hash || null : null,
    notes: draft.notes,
    reason: draft.reason,
    revision: original?.revision || null
  });
  return (
    <form
      onSubmit={e => {
        e.preventDefault();
        run(async () => setPreview(await api('custom/preview', payload())));
      }}
    >
      <h2>
        {protocol.name} · {protocol.version}
      </h2>
      <p className="hint">
        {protocol.description ||
          tr('Protocollo personalizzato. Nessun risultato fisiologico viene dedotto automaticamente dal tracciato.')}
      </p>
      <div className="form-grid">
        <label>
          {tr('Atleta')}
          <select disabled={!!original} value={draft.athlete_id} onChange={e => edit('athlete_id', e.target.value)}>
            {state.athlete
              .filter((a: Row) => a.organization_id === org && a.status !== 'deleted')
              .map((a: Row) => (
                <option key={a.id} value={a.id}>
                  {a.surname} {a.name}
                </option>
              ))}
          </select>
        </label>
        <label>
          {tr('Data')}
          <input type="date" required value={draft.date} onChange={e => edit('date', e.target.value)} />
        </label>
        <label>
          {tr('Origine')}
          <select
            value={source}
            onChange={e => {
              setSource(e.target.value);
              setPreview(null);
            }}
          >
            <option value="manual">{tr('Manuale')}</option>
            <option value="trace">{tr('Tracciato FIT / CSV')}</option>
          </select>
        </label>
      </div>
      {source === 'trace' && (
        <>
          <TraceImporter
            {...{api, run}}
            disabled={!!original}
            done={(r: Row) => {
              setTrace(r);
              setting('end_s', r.duration_s);
            }}
          />
          {trace && (
            <>
              <p>{tr('Seleziona l’inizio o la fine nel grafico, poi verifica i secondi prima di confermare.')}</p>
              <label>
                {tr('Selezione sul grafico')}
                <select value={pick} onChange={e => setPick(e.target.value)}>
                  <option value="">{tr('Solo navigazione')}</option>
                  <option value="offset_s">{tr('Imposta inizio')}</option>
                  <option value="end_s">{tr('Imposta fine')}</option>
                </select>
              </label>
              <TestSignals
                test={{samples: trace.samples, settings: draft.settings}}
                Plot={Plot}
                onPick={t => {
                  if (pick) setting(pick, Number(t.toFixed(3)));
                }}
              />
            </>
          )}
          <div className="form-grid">
            <TimeInput
              label={tr('Inizio dal file')}
              value={draft.settings.offset_s}
              onChange={v => setting('offset_s', v)}
            />
            <TimeInput label={tr('Fine dal file')} value={draft.settings.end_s} onChange={v => setting('end_s', v)} />
          </div>
        </>
      )}
      <label>
        {tr('Note')}
        <textarea value={draft.notes} onChange={e => edit('notes', e.target.value)} />
      </label>
      {original && (
        <label>
          {tr('Motivo correzione')}
          <input required value={draft.reason} onChange={e => edit('reason', e.target.value)} />
        </label>
      )}{' '}
      <FieldValues
        fields={protocol.custom_fields || []}
        values={draft.settings.custom_values}
        onChange={v => setting('custom_values', v)}
      />
      <details>
        <summary>{tr('Aggiungi osservazioni facoltative a questa prova')}</summary>
        <FieldSchemaEditor
          testOnly
          fields={draft.settings.extra_fields}
          onChange={v =>
            edit('settings', {
              ...draft.settings,
              extra_fields: v,
              custom_values: Object.fromEntries(
                Object.entries(draft.settings.custom_values).filter(
                  ([k]) => (protocol.custom_fields || []).some((f: Row) => f.key === k) || v.some(f => f.key === k)
                )
              )
            })
          }
        />
        <FieldValues
          fields={draft.settings.extra_fields}
          values={draft.settings.custom_values}
          onChange={v => setting('custom_values', v)}
        />
      </details>
      <FormActions>
        {!preview && (
          <button disabled={!draft.athlete_id || (source === 'trace' && !trace)}>{tr('Verifica anteprima')}</button>
        )}
      </FormActions>
      {preview && (
        <>
          <CustomValuesDisplay analysis={preview} />
          <p>{trBackend(preview.method)}</p>
          <FormActions>
            <button
              type="button"
              className="primary"
              onClick={e => {
                if (!validTimes(e.currentTarget)) return;
                run(async () =>
                  done(
                    await api(
                      original ? 'custom/tests/' + original.id : 'custom/tests',
                      payload(),
                      original ? 'PUT' : 'POST'
                    )
                  )
                );
              }}
            >
              {tr('Conferma e archivia')}
            </button>
          </FormActions>
        </>
      )}
    </form>
  );
}
import {TimeInput, validTimes} from './time';
import {TestSignals} from './TestSignals';
