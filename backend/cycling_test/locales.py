"""Presentation translations; never translate athlete data or scientific identifiers."""
LABELS={
 'Data':'Date','Protocollo':'Protocol','Peso (kg)':'Weight (kg)','Statura (cm)':'Height (cm)',
 'Ultimo step completo / MAP operativa (W)':'Last completed stage / operational MAP (W)',
 'Interpolazione separata (W)':'Separate interpolation (W)','MAP / peso (W/kg)':'MAP / weight (W/kg)',
 'FC massima osservata (bpm)':'Maximum observed HR (bpm)','FC a riposo (bpm)':'Resting HR (bpm)',
 'Durata riposo prima della misura (s)':'Rest duration before measurement (s)','Durata sforzo (s)':'Effort duration (s)',
 'Copertura potenza':'Power coverage','Nascita':'Birth','Stato nascita':'Birth confirmation','confermato':'confirmed','da confermare':'unconfirmed',
 'Watt Soglia':'Threshold watts','Origine soglia':'Threshold source','Coefficiente MAP':'MAP coefficient','FTP dichiarata (W)':'Declared FTP (W)',
 'Fonte peso':'Weight source','Report test incrementale':'Incremental test report','Tracciato del test':'Test recording',
 'Durata s':'Duration s','Media W':'Mean W','FC bpm':'HR bpm','Completo':'Complete','Recupero':'Recovery','Metodo e qualità':'Method and quality',
 'Note':'Notes','Riferimento':'Reference','Zona':'Zone','Limiti assoluti':'Absolute limits','Secondi':'Seconds','Zone':'Zones',
 'CICLO TEST / REPORT INCREMENTALE':'CICLO TEST / INCREMENTAL REPORT','Step del protocollo':'Protocol stages','Nessuna nota.':'No notes.',
 'Risultato storico: tracciato non disponibile':'Historical result: recording unavailable','Potenza (W)':'Power (W)','FC (bpm)':'HR (bpm)',
 'Cadenza (rpm)':'Cadence (rpm)','Tempo trascorso (min)':'Elapsed time (min)','Storico dei test':'Test history',
 'Gruppo / protocollo':'Group / protocol','Atleti':'Athletes','Soglia W':'Threshold W','MAP W - mediana':'MAP W - median',
 'n.d.':'n/a','Riferimento assente':'Missing reference','Si':'Yes','No':'No'
}

def tr(value, language='it'):
    return LABELS.get(value,value) if language=='en' else value
