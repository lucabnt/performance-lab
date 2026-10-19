"""Human-readable scientific statuses; identifiers remain in manifests."""
REASONS={
 'stage_hr_unavailable':'FC di fine step non disponibile o copertura insufficiente',
 'weight_missing_or_estimated':'Peso assente o solo stimato',
 'maximum_not_verified':'Massimo non verificato: riportato solo VO2peak',
 'insufficient_window':'Finestra non sufficientemente coperta',
 'no_crossing':'Concentrazione non attraversata: nessuna estrapolazione',
 'ambiguous_crossing':'Attraversamento ambiguo o curva non monotona',
 'at_least_five_distinct_loads_required':'Richiesti almeno cinque carichi distinti e curva non decrescente',
 'no_interior_positive_maximum':'Nessun massimo interno valido della distanza',
 'no_valid_0_4_rise_anchor':'Ancora per Dmax modificato non identificabile',
 'at_least_ten_valid_30s_bins_required':'Servono almeno dieci intervalli validi da 30 secondi',
 'no_positive_slope_change':'Nessun incremento di pendenza valido',
 'confirm_with_equivalents_and_end_tidal':'Da confermare con equivalenti ventilatori e gas end-tidal',
}
METHODS={'fixed_2':'Potenza a 2 mmol/L','fixed_4':'Potenza a 4 mmol/L','dmax':'Dmax cubico','modified_dmax':'Dmax modificato cubico'}

def reason(value):return REASONS.get(value,str(value or ''))
