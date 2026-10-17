"""Presentation names; never use storage keys as chart labels."""
LABELS={
 'map_w':('MAP operativa (W)','Operational MAP (W)'), 'map_wkg':('MAP relativa (W/kg)','Relative MAP (W/kg)'),
 'threshold_w':('Watt Soglia (W)','Threshold power (W)'), 'threshold_wkg':('Soglia relativa (W/kg)','Relative threshold (W/kg)'),
 'ftp_w':('FTP dichiarata (W)','Declared FTP (W)'), 'ftp_wkg':('FTP relativa (W/kg)','Relative FTP (W/kg)'),
 'weight_kg':('Peso (kg)','Weight (kg)'), 'height_cm':('Statura (cm)','Height (cm)'),
 'fthr_bpm':('FC di soglia (bpm)','Threshold HR (bpm)'), 'fc_max_test_bpm':('FC massima osservata (bpm)','Observed maximum HR (bpm)'),
 'fc_max_reference_bpm':('FC massima riferimento (bpm)','Reference maximum HR (bpm)'),
 'dichiarato':('Dichiarata','Declared'),'stimata_da_map':('Stimata dalla MAP','Estimated from MAP')}
def metric_label(key,language='it'):
    return LABELS.get(key,(str(key).replace('_',' '),)*2)[language=='en']
