import {tr} from './i18n';
type Row = Record<string, any>;
export function IntervalsSettings({
  organization,
  canEdit,
  api,
  run,
  refresh
}: {
  organization?: Row;
  canEdit: boolean;
  api: any;
  run: any;
  refresh: any;
}) {
  if (!organization) return null;
  return (
    <section className="panel">
      <h2>{tr('Collegamenti a Intervals.icu')}</h2>
      <label className="choice">
        <input
          type="checkbox"
          disabled={!canEdit}
          checked={!!organization.intervals_icu_enabled}
          onChange={e => {
            const enabled = e.target.checked;
            run(async () => {
              await api(
                `organizations/${organization.id}/integrations`,
                {base: organization.revision, intervals_icu_enabled: enabled},
                'PUT'
              );
              await refresh();
            });
          }}
        />
        {tr('Abilita collegamenti a Intervals.icu')}
      </label>
      <p className="hint">
        {tr(
          'Impostazione della società condivisa fra dispositivi. Gli ID restano conservati quando disattivi la funzione. Il collegamento apre il sito, senza importare attività o richiedere credenziali in Fuorigiri.'
        )}
      </p>
    </section>
  );
}
export function IntervalsField({id}: {id?: string}) {
  return (
    <label>
      {tr('ID atleta Intervals.icu')}
      <input name="intervals_icu_id" defaultValue={id || ''} placeholder="i…" pattern="i[0-9]+" maxLength={40} />
      <small>{tr('Facoltativo: i seguito dalle cifre del tuo ID.')}</small>
    </label>
  );
}
export function IntervalsLink({enabled, id}: {enabled: boolean; id?: string}) {
  return enabled && id && /^i[0-9]+$/.test(id) ? (
    <button
      type="button"
      onClick={() => {
        const link = document.createElement('a');
        link.href = `https://intervals.icu/athlete/${id}/activities`;
        if (!(window as any).FuorigiriNative) link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.click();
      }}
    >
      {tr('Vedi su Intervals.icu')}
    </button>
  ) : null;
}
