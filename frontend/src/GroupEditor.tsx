import React, {useState, type FormEvent} from 'react';
import {Field, FormActions} from '@cycling-suite/ui';
import {tr} from './i18n';
type Row = Record<string, any>;
export function GroupEditor({
  groups,
  parentId = '',
  onSubmit,
  busy,
  original,
  scope = 'group'
}: {
  groups: Row[];
  parentId?: string;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
  busy: boolean;
  original?: Row;
  scope?: string;
}) {
  const legacy = !!original && !original.parent_id && scope === 'season';
  const category = !!original && !original.parent_id && !legacy;
  const [parent, setParent] = useState(legacy ? original!.id : original?.parent_id || parentId);
  return (
    <form onSubmit={onSubmit}>
      <h2>{tr('Categoria o stagione')}</h2>
      {!category && (
        <Field label={tr('Categoria padre')}>
          <select name="parent_id" disabled={legacy} value={parent} onChange={e => setParent(e.target.value)}>
            {!original && <option value="">{tr('Categoria principale')}</option>}
            {groups
              .filter(g => !g.parent_id && g.status !== 'deleted')
              .map(g => (
                <option key={g.id} value={g.id}>
                  {g.name}
                </option>
              ))}
          </select>
        </Field>
      )}
      {!legacy && (
        <Field label={tr('Nome categoria o gruppo')}>
          <input
            name="name"
            defaultValue={original?.name || ''}
            required={!parent}
            autoFocus
            placeholder={parent ? tr('Facoltativo per una stagione: usa il nome della categoria') : ''}
          />
        </Field>
      )}
      {parent ? (
        <Field label={tr('Stagione')}>
          <input
            name="season"
            required
            inputMode="numeric"
            pattern={original ? undefined : '[0-9]{4}'}
            defaultValue={original?.season || new Date().getFullYear()}
          />
        </Field>
      ) : (
        !original && <p>{tr('Crea la categoria, poi aggiungi le sue stagioni.')}</p>
      )}
      <FormActions>
        <button type="submit" className="primary" disabled={busy}>
          {tr('Salva')}
        </button>
      </FormActions>
    </form>
  );
}
