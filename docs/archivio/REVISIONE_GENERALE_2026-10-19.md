# Revisione generale e prossimi passi — 19 ottobre 2026

> Documento storico: conserva decisioni e osservazioni dell’epoca. Per stato e priorità attuali consultare [indice](../README.md), [requisiti](../REQUISITI_E_TODO.md) e [roadmap](../PROSSIMI_PASSI.md).

## Esito e perimetro

Revisione dei sorgenti, regressioni numeriche e funzionali, flussi UI sul corpus sintetico, avvio desktop dai sorgenti, coerenza dipendenze/libreria comune, separazione e costi della sync. Non è una certificazione di assenza di errori: non comprende un audit di sicurezza indipendente, una scansione CVE completa, test cloud con account reali né esecuzione su un PC privo di dipendenze. Build/VM Linux e Android restano rinviate.

Le modifiche preesistenti nel working tree sono state conservate. Nessun commit, push, pubblicazione o rigenerazione dell'archivio demo principale.

## Problemi corretti

| ID | Problema verificato | Intervento |
|---|---|---|
| R01 | Testi come `21fasi`, `90min previsti`, `Versione1`, etichette/unità e conteggi import adiacenti | Spazi espliciti, formattazione numerica e gap fra etichette e select; controllo statico delle espressioni JSX adiacenti e verifica visiva |
| R02 | Protocolli senza scaletta ERG presentati con metadati di fasi/minuti non significativi | Sprint/Wingate mostrano durata dello sforzo; custom/schede mostrano la natura descrittiva; stato leggibile anziché codice DB |
| R03 | Progressione nel profilo con serie vuote e origini soglia diverse nella stessa curva | Serie separate per protocollo/metodo/origine; selezione fino a quattro; W/kg con peso stimato esclusi; lacune conservate |
| R04 | Confronto fra stagioni poteva sollevare TypeError ordinando origini soglia `None` e stringhe | Normalizzazione dell'origine non specificata senza unirla a quella dichiarata; regressione riprodotta prima del fix |
| R05 | Delta W/kg calcolati con peso stimato, pur escluso dagli aggregati | Stessa esclusione per progressioni e confronti appaiati; metriche dinamiche di lattato incluse nei delta |
| R06 | Selezione archivio non persistita completamente e risposte precedenti potenzialmente applicate dopo un cambio | Memorizzazione società/archivio, inventario indipendente dall'ID vecchio, invalidazione richieste superate e selettore bloccato durante il caricamento |
| R07 | Nome Flatpak fissato a 0.6.0 e test frontend non inclusi nel job Windows | Versione letta dal progetto; test Node aggiunti al workflow manuale, senza avviare build remote |
| R08 | Legacy/backup con più società avrebbero pubblicato tutto lo storico come un unico canale | Scambio, configurazione e inviti bloccati per multi-società; identità legata all'ID società, record estranei respinti anche se firmati nello stesso workspace |
| R09 | Ogni sync riscaricava tutti i pacchetti già acquisiti | Sync gestita ordinaria incrementale sui pacchetti sconosciuti; pulsante Verifica completa per rileggere tutto; controlli accessi/revoche sempre acquisiti |
| R10 | Export ZIP poteva produrre un backup oltre i limiti accettati dal ripristino | Export rifiutato esplicitamente oltre i limiti ripristinabili, senza scaricare un file inutilizzabile; serve ancora backup scalabile |

R08 e R10 sono protezioni, non migrazioni automatiche: gli archivi multi-società restano consultabili e i dati originali non vengono modificati. La separazione assistita di un vecchio backup in società indipendenti è il prossimo lavoro, non una funzione dichiarata completata.

## Verifiche

- Suite finale: 156 test backend passati, uno saltato per i permessi symlink Windows; warning Starlette/httpx preesistente. Include isolamento di due società, firme, multi-società bloccate prima del trasporto, skip/verifica completa, stima dimensionale verificata rispetto ai file effettivi e limiti backup simmetrici.
- 18 test Node passati per modelli grafici e selezione archivi; TypeScript/Vite compilato. Rimane il chunk Plotly di circa 5,3 MB minificati / 1,6 MB gzip.
- `pip check`: nessuna dipendenza incoerente. `verify_suite_ui.py`: artefatto UI comune, lockfile, licenza e branding coerenti.
- Smoke desktop dai sorgenti riuscito, compilazione sintattica backend/scripts riuscita. Non equivale a provare l'installer su macchina pulita.
- UI: spazi nei protocolli, durate senza ERG, profilo con serie selezionabili, ritorno in cima dopo navigazione e società conservata al ricaricamento. Screenshot locali sotto `output/`.
- Misure riproducibili della società sintetica e modelli di registrazione 1 h + 3 min di recupero, a 1/5 Hz. Risultati e limiti in [SYNC_DIMENSIONI_E_SCALABILITA.md](../SYNC_DIMENSIONI_E_SCALABILITA.md).

## Rischi e limiti ancora aperti

1. Sync v1 duplica campioni nel record/revisioni e allegati nei pacchetti di ogni revisione. Lo skip riduce il download ripetuto, non lo spazio storico nel cloud né l'inventario completo.
2. Pacchetti singoli limitati a 80 MB; inventario a 100.000 file. Backup importabile: 100 MB ZIP, 1 GB espanso e 10.000 allegati. Sono limiti effettivi da superare con un formato e uno streaming adeguati, non semplicemente con numeri più grandi in RAM.
3. Separazione assistita dei vecchi archivi multi-società ancora da implementare. Filtrare la UI o escludere alcuni record dalla sync non risolve cronologia, dipendenze, revoche e permessi.
4. API cloud/OAuth e connessioni interrotte richiedono collaudo con account reali distinti e permessi del provider. I test locali non dimostrano la configurazione delle ACL cloud dell'utente.
5. Traduzione inglese incompleta nei moduli recenti e collaudo sistematico di accessibilità/touch ancora da completare. Il codice principale React rimane ampio: utile estrarre flussi e stato dopo avere i test di navigazione.
6. Installer distribuito precedente ai nuovi sorgenti. Nessun nuovo pacchetto Windows/Linux/Android pubblicato o firmato in questa revisione.

## Prossimi passi, in ordine

1. **Consolidare archivio/sync v2 senza cambiare le formule:** campioni fuori dai record, allegati cifrati identificati da hash e caricati una sola volta, manifest/cursori e snapshot per un nuovo dispositivo. Prove automatiche di compatibilità v1/v2, interruzioni e conflitti. Non eliminare vecchi pacchetti o revisioni senza una politica per dispositivi offline e recupero.
2. **Backup grandi e separazione assistita per società:** export/import in streaming o in parti, verifica integrità e ripristino reale; estrazione di una società con tutte le sue dipendenze e cronologia, nuove chiavi/inviti e vecchio archivio conservato. Questo lavoro può essere sviluppato e testato sul PC attuale.
3. **Collaudo end-to-end ripetibile:** oltre ai modelli puri, navigazione GUI da archivio vuoto → import → revisione → report → backup/ripristino → seconda replica. Aggiungere alcuni FIT reali anonimizzati di GoldenCheetah/MyWhoosh/Zwift come vettori di compatibilità, con risultati di riferimento controllati.
4. **Candidato Windows e prova su VM pulita:** dipendenze incluse, installazione/aggiornamento/disinstallazione, recupero dati e firma quando disponibile. Misurare avvio e grafici; introdurre caricamento differito Plotly se confermato utile.
5. **Riprendere Linux/Fedora e Android quando il builder è disponibile:** compilare dipendenze native e collaudare offline, file, report e sync su dispositivi reali. I sorgenti Kotlin/Python presenti non bastano a dichiarare Android pronto.
