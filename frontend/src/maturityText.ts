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
  'Età non disponibile': 'Age unavailable',
  'Calo di statura o velocità anomala a ridosso della finestra del picco: verificare le misure.':
    'Height decrease or anomalous velocity close to the peak window: verify the measurements.',
  'HV: velocità media di crescita nell’intervallo; PHV/APHV: picco ed età al picco. Le equazioni di Moore/Mirwald stimano offset/APHV, non misurano il picco. %PAH: percentuale della statura adulta prevista.':
    'HV: mean growth velocity over the interval; PHV/APHV: peak and age at peak. Moore/Mirwald equations estimate offset/APHV and do not measure the peak. %PAH: percentage of predicted adult height.',
  'Il massimo osservato confina con un calo di statura o una velocità anomala: verificare le misure.':
    'The observed maximum borders a height decrease or anomalous velocity: verify the measurements.',
  'Lo snapshot conserva i dati disponibili al momento del calcolo; non viene ricalcolato nel report. Misure successive o corrette richiedono una nuova analisi.':
    'The snapshot keeps the data available at calculation time and is not recalculated in reports. Later or corrected measurements require a new analysis.',
  'Massimo delle velocità medie osservate finora; non è il PHV e non conferma il picco.':
    'Highest mean velocity observed so far; it is not PHV and does not confirm the peak.',
  'Meno di 90 giorni dalla statura precedente usata: saltata, non bloccante.':
    'Less than 90 days after the previous used height: skipped, not blocking.',
  'Misure o profilo modificati: ricalcolare l’anteprima prima di salvare.':
    'Measurements or profile changed: recalculate the preview before saving.',
  'Nessun intervallo individuale validato; sensibilità a frequenza e precisione delle misure.':
    'No validated individual interval; sensitive to measurement frequency and precision.',
  'Ricostruzione longitudinale esplorativa, non misura istantanea del PHV.':
    'Exploratory longitudinal reconstruction, not an instantaneous PHV measurement.',
  'SEE della popolazione di sviluppo; non intervallo di confidenza individuale.':
    'SEE of the development population; not an individual confidence interval.',
  'Serve almeno un intervallo di 90–400 giorni tra due stature misurate e valide.':
    'At least one 90–400 day interval between two valid measured heights is required.',
  'Statura non misurata o qualità non confermata: non usata.': 'Height not measured or quality unconfirmed: not used.',
  'Valutabile da 18 anni con almeno tre stature misurate valide su un anno; non prova la fine della crescita.':
    'Assessable from age 18 with at least three valid measured heights over one year; it does not prove growth has ended.',
  'Variazione contenuta (≤0,5 cm nel periodo osservato), senza garanzia di crescita conclusa.':
    'Small change (≤0.5 cm over the observed period), with no guarantee that growth has ended.',
  'Variazione superiore a 0,5 cm nel periodo: documentare l’andamento.':
    'Change above 0.5 cm in the period: document the trend.'
};
export const maturityText = (text?: string) => (text ? (language === 'en' ? messages[text] || text : text) : '');
