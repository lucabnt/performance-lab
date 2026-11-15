"""Presentation names; never use storage keys as chart labels."""

LABELS = {
    'map_w': ('MAP operativa (W)', 'Operational MAP (W)'),
    'map_wkg': ('MAP relativa (W/kg)', 'Relative MAP (W/kg)'),
    'threshold_w': ('Watt Soglia (W)', 'Threshold power (W)'),
    'threshold_wkg': ('Soglia relativa (W/kg)', 'Relative threshold (W/kg)'),
    'ftp_w': ('FTP dichiarata (W)', 'Declared FTP (W)'),
    'ftp_wkg': ('FTP relativa (W/kg)', 'Relative FTP (W/kg)'),
    'weight_kg': ('Peso (kg)', 'Weight (kg)'),
    'height_cm': ('Statura (cm)', 'Height (cm)'),
    'fthr_bpm': ('FC di soglia (bpm)', 'Threshold HR (bpm)'),
    'fc_max_test_bpm': ('FC massima osservata (bpm)', 'Observed maximum HR (bpm)'),
    'fc_max_reference_bpm': ('FC massima riferimento (bpm)', 'Reference maximum HR (bpm)'),
    'dichiarato': ('Dichiarata', 'Declared'),
    'stimata_da_map': ('Stimata dalla MAP', 'Estimated from MAP'),
    'lactate_2_w': ('Potenza a 2 mmol/L (W)', 'Power at 2 mmol/L (W)'),
    'lactate_4_w': ('Potenza a 4 mmol/L (W)', 'Power at 4 mmol/L (W)'),
    'vo2peak_l_min': ('VO2peak (L/min)', 'VO2peak (L/min)'),
    'vo2peak_ml_kg_min': ('VO2peak (mL/kg/min)', 'VO2peak (mL/kg/min)'),
    'rest_hr': ('FC a riposo (bpm)', 'Resting HR (bpm)'),
    'rest_after_s': ('Tempo di riposo prima della misura (s)', 'Rest duration (s)'),
    'rpe': ('RPE', 'RPE'),
    'rpe_scale': ('Scala RPE', 'RPE scale'),
    'threshold_coefficient': ('Coefficiente MAP/soglia', 'MAP/threshold coefficient'),
    'map_alt_w': ('Interpolazione separata (W)', 'Separate interpolation (W)'),
    'duration_s': ('Durata sforzo (s)', 'Effort duration (s)'),
    'duration_incremental_s': ('Durata fase incrementale (s)', 'Incremental phase duration (s)'),
    'power_mean_w': ('Potenza media osservata (W)', 'Observed mean power (W)'),
    'work_kj': ('Lavoro osservato (kJ)', 'Observed work (kJ)'),
    'power_coverage': ('Copertura potenza (0-1)', 'Power coverage (0-1)'),
    'terminal_target_w': ('Target terminale rampa/discontinuo (W)', 'Terminal target (W)'),
    'terminal_mean_w': ('Media terminale osservata (W)', 'Observed terminal mean (W)'),
    'lattato_2mmol_w': ('Potenza a 2 mmol/L (W)', 'Power at 2 mmol/L (W)'),
    'lattato_4mmol_w': ('Potenza a 4 mmol/L (W)', 'Power at 4 mmol/L (W)'),
    'lavoro_battito_j': ('Lavoro per battito (J)', 'Work per beat (J)'),
    'lavoro_battito_max_j': ('Lavoro massimo per battito (J)', 'Maximum work per beat (J)'),
    'cadenza_media_rpm': ('Cadenza media (rpm)', 'Mean cadence (rpm)'),
    'cadenza_max_rpm': ('Cadenza massima (rpm)', 'Maximum cadence (rpm)'),
    'rapporto_trasm_m': ('Sviluppo metrico (m)', 'Rollout (m)'),
    'pedivella_m': ('Lunghezza pedivella (m)', 'Crank length (m)'),
}


def metric_label(key, language='it'):
    from .lactate_levels import metric_label as lactate_label

    if lactate_label(str(key), language):
        return lactate_label(str(key), language)
    return LABELS.get(key, (str(key).replace('_', ' '),) * 2)[language == 'en']


from .anaerobic import LABELS as ANAEROBIC_LABELS, METRIC_MAP

LABELS.update({key: (value, value) for key, value in ANAEROBIC_LABELS.items()})
LABELS.update(
    {
        key: (
            ANAEROBIC_LABELS.get(value, LABELS.get(value, (key, key))[0]),
            ANAEROBIC_LABELS.get(value, LABELS.get(value, (key, key))[1]),
        )
        for key, value in METRIC_MAP.items()
    }
)
