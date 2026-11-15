type Row = Record<string, any>;
export const localToday = () => new Date().toLocaleDateString('en-CA');
export function seasonPeriod(season: unknown, today = localToday()) {
  const year = String(season ?? '').trim();
  return /^\d{4}$/.test(year) ? {start: `${year}-01-01`, end: `${year}-12-31`} : {start: today, end: ''};
}
// A season on a legacy root keeps its original ID and memberships. Only its
// presentation changes; category selection still includes all child groups.
export function groupSeasons(parent: Row, groups: Row[], memberships: Row[]) {
  const children = groups.filter(g => g.parent_id === parent.id && g.status !== 'deleted');
  const own =
    parent.season_status !== 'deleted' &&
    (parent.season || memberships.some(m => m.group_id === parent.id && m.status !== 'deleted'));
  return [...(own ? [parent] : []), ...children].sort((a, b) =>
    String(a.season || '').localeCompare(String(b.season || ''))
  );
}
export function matchesGroupMembership(m: Row, filter: string, groups: Row[], today = localToday()) {
  if (m.status === 'deleted') return false;
  const direct = filter.startsWith('season:');
  const id = direct ? filter.slice(7) : filter;
  const group = groups.find(g => g.id === id);
  if (!group || group.status === 'deleted' || (direct && group.season_status === 'deleted')) return false;
  const period = direct ? seasonPeriod(group.season, today) : {start: today, end: today};
  return (
    ((m.group_id === id && group.season_status !== 'deleted') ||
      (!direct && groups.some(g => g.id === m.group_id && g.parent_id === id && g.status !== 'deleted'))) &&
    m.start <= (period.end || period.start) &&
    (!m.end || m.end >= period.start)
  );
}
export function groupFilterLabel(filter: string, groups: Row[]) {
  const direct = filter.startsWith('season:');
  const g = groups.find(g => g.id === (direct ? filter.slice(7) : filter));
  if (!g) return '';
  const name = groups.find(p => p.id === g.parent_id)?.name || g.name;
  return direct ? [name, g.season].filter(Boolean).join(' · ') : name;
}
