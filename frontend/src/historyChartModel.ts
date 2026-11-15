type Row = Record<string, any>;
const finite = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);

/** Retain the backend's exact boundaries: no pooling across methods or versions. */
export function historySeries(groups: Row[], protocols: Row[], metric: string): Row[] {
  const buckets = new Map<string, Row>();
  for (const g of groups) {
    const id = JSON.stringify([g.protocol_id, g.method_key, g.threshold_source]);
    const p = protocols.find(p => p.id === g.protocol_id);
    if (!buckets.has(id))
      buckets.set(id, {
        id,
        protocol_id: g.protocol_id,
        title: (p?.name || 'Protocollo non disponibile') + ' · ' + (p?.version || '?'),
        method: g.method_label,
        threshold_source: g.threshold_source,
        groups: [],
        valid: 0
      });
    const series = buckets.get(id)!;
    series.groups.push(g);
    series.valid += g.metrics[metric]?.n || 0;
  }
  return [...buckets.values()]
    .filter(s => s.valid > 0)
    .sort((a, b) => b.valid - a.valid || a.title.localeCompare(b.title) || a.id.localeCompare(b.id))
    .map((s, i) => ({
      ...s,
      code: 'S' + (i + 1),
      groups: s.groups.sort((a: Row, b: Row) => a.label.localeCompare(b.label, undefined, {numeric: true}))
    }));
}

export function historyTraces(series: Row[], metric: string, statistic: string, dimension: string) {
  const colors = ['#1a62b7', '#bf523e', '#248777', '#7952a3', '#ad7419', '#63734b'];
  return series.map(s => ({
    x: s.groups.map((g: Row) => g.label),
    y: s.groups.map((g: Row) => (finite(g.metrics[metric]?.[statistic]) ? g.metrics[metric][statistic] : null)),
    name: s.code + ' · ' + (s.title.length > 48 ? s.title.slice(0, 45) + '…' : s.title),
    text: s.groups.map((g: Row) => s.title + '<br>' + s.method + '<br>n = ' + (g.metrics[metric]?.n || 0)),
    hovertemplate: '%{x}<br>%{y:.2f}<br>%{text}<extra></extra>',
    type: 'scatter',
    mode: ['season', 'age', 'cohort'].includes(dimension) ? 'lines+markers' : 'markers',
    marker: {size: 9, color: colors[(Number(s.code.slice(1)) - 1) % colors.length]},
    line: {color: colors[(Number(s.code.slice(1)) - 1) % colors.length]},
    connectgaps: false
  }));
}

export const historyCategories = (series: Row[]) =>
  [...new Set<string>(series.flatMap(s => s.groups.map((g: Row) => g.label)))].sort((a, b) =>
    a.localeCompare(b, undefined, {numeric: true})
  );

export function initialHistorySelection(series: Row[], selection: string[] | null) {
  return selection === null
    ? series.slice(0, 1).map(s => s.id)
    : selection.filter(id => series.some(s => s.id === id)).slice(0, 4);
}
