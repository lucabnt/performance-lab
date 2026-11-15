import React, {useState} from 'react';
import {FormActions} from '@cycling-suite/ui';
import {Dialog} from './Dialog';
import {GroupEditor} from './GroupEditor';
import {GroupTree} from './features';
import {tr} from './i18n';
type Row = Record<string, any>;
type Target = {record: Row; scope: 'group' | 'season'};
export function GroupManager({
  groups,
  memberships,
  onSelect,
  onAdd,
  onAddSeason,
  canEdit,
  api,
  run,
  busy,
  onChanged
}: {
  groups: Row[];
  memberships: Row[];
  onSelect: (id: string) => void;
  onAdd: (id: string) => void;
  onAddSeason: (id: string) => void;
  canEdit: boolean;
  api: any;
  run: any;
  busy: boolean;
  onChanged: () => Promise<void>;
}) {
  const [edit, setEdit] = useState<Target | null>(null),
    [remove, setRemove] = useState<Target | null>(null),
    [showRemoved, setShowRemoved] = useState(false);
  const label = ({record: g, scope}: Target) =>
    scope === 'season' || g.parent_id
      ? `${groups.find(p => p.id === g.parent_id)?.name || g.name} · ${g.season || g.name}`
      : g.name;
  const removed = groups.flatMap<Target>(g =>
    g.status === 'deleted'
      ? [{record: g, scope: 'group'}]
      : g.season_status === 'deleted'
        ? [{record: g, scope: 'season'}]
        : []
  );
  const blocked =
    remove?.scope === 'group' && groups.some(g => g.parent_id === remove.record.id && g.status !== 'deleted');
  const lifecycle = (target: Target, status: string) =>
    run(async () => {
      await api(`groups/${target.record.id}/lifecycle`, {base: target.record.revision, status, scope: target.scope});
      await onChanged();
      setRemove(null);
    });
  return (
    <>
      <GroupTree
        groups={groups}
        memberships={memberships}
        canEdit={canEdit}
        onSelect={onSelect}
        onAdd={onAdd}
        onAddSeason={onAddSeason}
        onEdit={(record, scope) => setEdit({record, scope})}
        onRemove={(record, scope) => setRemove({record, scope})}
      />
      {!!removed.length && (
        <>
          <label className="choice">
            <input type="checkbox" checked={showRemoved} onChange={e => setShowRemoved(e.target.checked)} />
            {tr('Mostra gruppi e stagioni eliminati')}
          </label>
          {showRemoved && (
            <section className="panel">
              <h2>{tr('Gruppi e stagioni eliminati')}</h2>
              {removed.map(target => (
                <div className="list-row" key={`${target.scope}:${target.record.id}`}>
                  <strong>{label(target)}</strong>
                  <button
                    disabled={
                      !canEdit ||
                      busy ||
                      (!!target.record.parent_id &&
                        groups.some(g => g.id === target.record.parent_id && g.status === 'deleted'))
                    }
                    onClick={() => lifecycle(target, 'active')}
                  >
                    {tr('Ripristina')}
                  </button>
                </div>
              ))}
              <p>{tr('Se la categoria è eliminata, ripristinala prima delle sue stagioni.')}</p>
            </section>
          )}
        </>
      )}
      {edit && (
        <Dialog title={tr('Modifica gruppo o stagione')} editor busy={busy} onClose={() => setEdit(null)}>
          <GroupEditor
            original={edit.record}
            scope={edit.scope}
            groups={groups}
            busy={busy}
            onSubmit={e => {
              e.preventDefault();
              const f = new FormData(e.currentTarget);
              run(async () => {
                const old = edit.record,
                  legacy = edit.scope === 'season' && !old.parent_id;
                await api(
                  `groups/${old.id}`,
                  {
                    base: old.revision,
                    organization_id: old.organization_id,
                    name: legacy ? old.name : f.get('name'),
                    season: old.parent_id || legacy ? f.get('season') : old.season || '',
                    parent_id: old.parent_id ? f.get('parent_id') : null
                  },
                  'PUT'
                );
                await onChanged();
                setEdit(null);
              });
            }}
          />
        </Dialog>
      )}
      {remove && (
        <Dialog title={tr('Elimina gruppo o stagione')} busy={busy} onClose={() => setRemove(null)}>
          <h2>{label(remove)}</h2>
          <p>
            {tr(
              'Verrà rimosso dalle scelte attive. Atleti, test e appartenenze storiche restano conservati. Potrai ripristinarlo.'
            )}
          </p>
          {blocked && <p role="status">{tr('Sposta o elimina prima le stagioni attive della categoria.')}</p>}
          <FormActions>
            <button disabled={busy} onClick={() => setRemove(null)}>
              {tr('Annulla')}
            </button>
            <button disabled={!canEdit || busy || !!blocked} onClick={() => lifecycle(remove, 'deleted')}>
              {tr('Conferma eliminazione')}
            </button>
          </FormActions>
        </Dialog>
      )}
    </>
  );
}
