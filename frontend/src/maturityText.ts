import {language} from './i18n';
const messages: Record<string, string> = {
  'Stima da misura non misurata o qualità non confermata: verificare i dati.':
    'Estimate from non-measured data or unconfirmed quality: verify the inputs.',
  'Misura esclusa dal calcolo.': 'Measurement excluded from calculation.',
  'Misura non misurata o qualità non confermata.': 'Measurement is not measured or its quality is unconfirmed.',
  'Serve la data di nascita completa e non futura rispetto alla misura.':
    'A complete birth date no later than the measurement is required.',
  'Parametro M/F per l’equazione non disponibile; non viene inferito.':
    'The M/F model parameter is unavailable and will not be inferred.',
  'Età fuori dal dominio prudenziale del preset.': 'Age is outside the preset’s conservative application range.',
  'Statura mancante.': 'Height is missing.',
  'Servono statura seduta e massa nella stessa rilevazione.':
    'Sitting height and body mass in the same measurement are required.',
  'Statura seduta incoerente.': 'Sitting height is inconsistent.',
  'Serve una previsione adulta esterna con metodo e fonte.':
    'An external adult-height prediction with method and source is required.',
  'Previsione adulta inferiore alla statura rilevata o statura mancante.':
    'Predicted adult height is below measured height, or height is missing.',
  'Misure specifiche mancanti.': 'Specific measurements are missing.',
  'Usare due misure confermate come misurate e valide.':
    'Two measurements confirmed as measured and valid are required.',
  'Intervallo inferiore a 90 giorni o stessa data; annualizzazione non utilizzabile.':
    'Interval below 90 days or same date; annualized velocity is not usable.',
  'Intervallo superiore a 400 giorni; serie troppo rada.': 'Interval above 400 days; the series is too sparse.',
  'Statura diminuita: verificare le misure.': 'Height decreased: verify the measurements.',
  'Velocità oltre il controllo prudenziale del preset: verificare le misure.':
    'Velocity exceeds the preset’s conservative check: verify measurements.',
  'Servono almeno 7 stature con intervalli validi e senza discontinuità.':
    'At least seven heights with valid intervals and no discontinuities are required.',
  'Servono almeno due anni di osservazioni attorno al picco.':
    'At least two years of observations around the peak are required.',
  'Picco al bordo o senza due intervalli di supporto per lato.':
    'Peak is at the edge or lacks two supporting intervals on each side.',
  'Nessun massimo interno della curva locale.': 'The local curve has no internal maximum.',
  'Massimo locale fuori dalla finestra o non valido.': 'Local maximum is outside the window or invalid.',
  'Copertura insufficiente prima/dopo il massimo locale (180 giorni per lato).':
    'Insufficient support before/after the local maximum (180 days each side).',
  'Servono due misure specifiche valide distanziate di 90–400 giorni.':
    'Two valid specific measurements 90–400 days apart are required.',
  'Convenzioni di qualità del prodotto, non criteri diagnostici.':
    'Product quality conventions, not diagnostic criteria.',
  'Le stime antropometriche possono essere inaccurate nel singolo atleta; non sono PHV osservato.':
    'Anthropometric estimates may be inaccurate for an individual athlete; they are not observed PHV.',
  'La %PAH dipende da una previsione adulta esterna dichiarata. Nessun coefficiente Khamis–Roche non verificato è incorporato.':
    '%PAH depends on a declared external adult-height prediction. No unverified Khamis–Roche coefficients are included.',
  'Età non disponibile': 'Age unavailable'
};
export const maturityText = (text?: string) => (text ? (language === 'en' ? messages[text] || text : text) : '');
