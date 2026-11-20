import {tr} from './i18n';
type Row = Record<string, any>;
export function FieldSchemaEditor({
  fields,
  onChange,
  testOnly = false
}: {
  fields: Row[];
  onChange: (v: Row[]) => void;
  testOnly?: boolean;
}) {
  const edit = (i: number, k: string, v: any) => onChange(fields.map((f, j) => (j === i ? {...f, [k]: v} : f)));
  return (
    <section>
      <h3>{tr('Campi aggiuntivi facoltativi')}</h3>
      <p className="hint">
        {tr(
          'Dichiara significato, tipo e unità. I campi vuoti rimangono non rilevati; non vengono introdotte formule automatiche.'
        )}
      </p>
      {fields.map((f, i) => (
        <fieldset key={i}>
          <legend>
            {tr('Campo')} {i + 1}
          </legend>
          <div className="form-grid">
            <label>
              {tr('Identificatore')}
              <input
                required
                pattern="[a-z][a-z0-9_]{0,49}"
                value={f.key}
                onChange={e => edit(i, 'key', e.target.value)}
              />
            </label>
            <label>
              {tr('Nome leggibile')}
              <input required value={f.label} onChange={e => edit(i, 'label', e.target.value)} />
            </label>
            <label>
              {tr('Tipo')}
              <select
                value={f.type}
                onChange={e =>
                  onChange(
                    fields.map((r, j) =>
                      j === i ? {...r, type: e.target.value, choices: [], minimum: null, maximum: null} : r
                    )
                  )
                }
              >
                {Object.entries({
                  number: 'Numero',
                  text: 'Testo',
                  boolean: 'Sì / no',
                  date: 'Data',
                  choice: 'Scelta da elenco'
                }).map(([k, v]) => (
                  <option key={k} value={k}>
                    {tr(v)}
                  </option>
                ))}
              </select>
            </label>
            {!testOnly && (
              <label>
                {tr('Compilazione')}
                <select value={f.scope} onChange={e => edit(i, 'scope', e.target.value)}>
                  <option value="test">{tr('In ogni prova')}</option>
                  <option value="protocol">{tr('Nella definizione del protocollo')}</option>
                </select>
              </label>
            )}
            <label>
              {tr('Unità (facoltativa)')}
              <input value={f.unit || ''} onChange={e => edit(i, 'unit', e.target.value)} />
            </label>
            {f.type === 'number' &&
              ['minimum', 'maximum'].map(k => (
                <label key={k}>
                  {tr(k === 'minimum' ? 'Minimo' : 'Massimo')}
                  <input
                    type="number"
                    step="any"
                    value={f[k] ?? ''}
                    onChange={e => edit(i, k, e.target.value === '' ? null : Number(e.target.value))}
                  />
                </label>
              ))}
            {f.type === 'choice' && (
              <label>
                {tr('Scelte (separate da ;)')}
                <input
                  value={(f.choices || []).join(';')}
                  onChange={e => edit(i, 'choices', e.target.value.split(';'))}
                />
              </label>
            )}
          </div>
          <button type="button" onClick={() => onChange(fields.filter((_, j) => j !== i))}>
            {tr('Rimuovi campo')}
          </button>
        </fieldset>
      ))}
      <button
        type="button"
        disabled={fields.length >= 50}
        onClick={() =>
          onChange([
            ...fields,
            {key: '', label: '', type: 'number', scope: 'test', unit: '', choices: [], minimum: null, maximum: null}
          ])
        }
      >
        {tr('Aggiungi campo facoltativo')}
      </button>
    </section>
  );
}
export function FieldValues({
  fields,
  values,
  onChange,
  scope = 'test'
}: {
  fields: Row[];
  values: Row;
  onChange: (v: Row) => void;
  scope?: string;
}) {
  const edit = (k: string, v: any) => {
    const next = {...values};
    if (v === null || v === '') delete next[k];
    else next[k] = v;
    onChange(next);
  };
  return (
    <div className="form-grid">
      {fields
        .filter(f => f.scope === scope)
        .map(f => (
          <label key={f.key}>
            {f.label || tr('Nome del campo')}
            {f.unit ? ' · ' + f.unit : ''}
            <small>{tr('Facoltativo')}</small>
            {['boolean', 'choice'].includes(f.type) ? (
              <select
                value={values[f.key] == null ? '' : String(values[f.key])}
                onChange={e =>
                  edit(
                    f.key,
                    f.type === 'boolean' ? (e.target.value === '' ? null : e.target.value === 'true') : e.target.value
                  )
                }
              >
                <option value="">{tr('Non rilevato')}</option>
                {f.type === 'boolean' ? (
                  <>
                    <option value="true">{tr('Sì')}</option>
                    <option value="false">No</option>
                  </>
                ) : (
                  (f.choices || []).map((c: string) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))
                )}
              </select>
            ) : (
              <input
                type={f.type === 'number' ? 'number' : f.type === 'date' ? 'date' : 'text'}
                min={f.minimum ?? undefined}
                max={f.maximum ?? undefined}
                step="any"
                value={values[f.key] ?? ''}
                onChange={e =>
                  edit(
                    f.key,
                    f.type === 'number' ? (e.target.value === '' ? null : Number(e.target.value)) : e.target.value
                  )
                }
              />
            )}
          </label>
        ))}
    </div>
  );
}
export function TestExtensions({
  protocol,
  values,
  onChange,
  extraFields,
  onFieldsChange
}: {
  protocol?: Row;
  values: Row;
  onChange: any;
  extraFields: Row[];
  onFieldsChange: any;
}) {
  return (
    <details>
      <summary>{tr('Campi facoltativi e osservazioni aggiuntive')}</summary>
      <FieldValues fields={[...(protocol?.custom_fields || []), ...extraFields]} values={values} onChange={onChange} />
      <FieldSchemaEditor
        testOnly
        fields={extraFields}
        onChange={(next: Row[]) => {
          onFieldsChange(next);
          const keys = new Set([...(protocol?.custom_fields || []), ...next].map(f => f.key));
          onChange(Object.fromEntries(Object.entries(values).filter(([k]) => keys.has(k))));
        }}
      />
    </details>
  );
}
export function CustomValuesDisplay({analysis}: {analysis: Row}) {
  const fields = analysis.custom_fields || [];
  return fields.length ? (
    <section>
      <h3>{tr('Campi personalizzati')}</h3>
      <table>
        <tbody>
          {fields.map((f: Row) => {
            const v = (f.scope === 'protocol' ? analysis.protocol_custom_values : analysis.custom_values)?.[f.key];
            return (
              <tr key={f.key}>
                <th>
                  {f.scope === 'protocol' ? tr('Protocollo') + ' · ' : ''}
                  {f.label}
                  {f.unit ? ' · ' + f.unit : ''}
                </th>
                <td>{v == null ? tr('Non rilevato') : v === true ? tr('Sì') : v === false ? tr('No') : String(v)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  ) : null;
}
