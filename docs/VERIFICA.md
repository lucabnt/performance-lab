# Verifica locale della prima implementazione

Ambiente: Windows, Python 3.14, Node.js 24. Versioni risolte nei lockfile.

- 14 test automatici: salti e validazione ERG, entrambi i protocolli forniti, step parziale, recupero, gap senza interpolazione, FC assente, CRC FIT, protezione da aggiornamenti persi, scambio duplicato e conflitto, percorso API completo.
- `npm run build`: controllo TypeScript e build di produzione riusciti. Plotly produce un bundle ampio, da ottimizzare nel consolidamento.
- Interfaccia verificata nel browser locale con archivio sintetico: elenco atleti, profilo, storico e dettaglio test.
- PDF dimostrativo renderizzato con Poppler e ispezionato su entrambe le pagine; corretto il titolo del recupero rimasto isolato a fondo pagina.
- Nessun FIT reale di GoldenCheetah/MyWhoosh/Zwift disponibile. Nessuna prova su Fedora o client cloud reali eseguita.
- Lo scambio simulato testa il trasporto filesystem fra due archivi locali. Non dimostra sincronizzazione affidabile fra due PC tramite un provider cloud.

I test descrivono l'implementazione attuale e non validano fisiologicamente il metodo. La regola provvisoria di step completo richiede durata prevista e almeno 95% di copertura potenza, senza verifica dell'aderenza al target.
