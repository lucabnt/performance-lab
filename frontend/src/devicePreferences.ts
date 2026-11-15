export type Preferences = {language?: 'it' | 'en' | null; time_zone?: 'local' | 'Europe/Rome' | 'UTC'};
export async function rememberedLanguage(load: () => Promise<Preferences>, fallback: string) {
  const saved = await load();
  return saved.language === 'en' || saved.language === 'it' ? saved.language : fallback === 'en' ? 'en' : 'it';
}
export function syncTime(value: string, zone = 'local', locale = 'it') {
  if (!value) return '—';
  // Never silently interpret an old timestamp without its UTC offset.
  if (!/(Z|[+-]\d\d:\d\d)$/i.test(value))
    return value + ' · ' + (locale === 'en' ? 'time zone unspecified' : 'fuso non indicato');
  const date = new Date(value);
  if (isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(locale === 'en' ? 'en-GB' : 'it-IT', {
    timeZone: zone === 'local' ? undefined : zone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hourCycle: 'h23',
    timeZoneName: 'short'
  }).format(date);
}
