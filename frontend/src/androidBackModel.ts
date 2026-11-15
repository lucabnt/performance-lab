export type Screen = {page: string; selected: string; scroll: number};
export function previousScreen(current: Screen, history: Screen[]): Screen | null {
  const prior = history.at(-1);
  if (prior) return prior;
  if (current.selected) return {...current, selected: '', scroll: 0};
  if (current.page !== 'athletes') return {page: 'athletes', selected: '', scroll: 0};
  return null;
}
