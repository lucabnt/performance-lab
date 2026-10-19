# Prossimi passi — architettura 1.2

## Aggiornamento operativo — osservazioni del 19 ottobre 2026

**Attuazione successiva:** TD-83–97 sviluppati nei sorgenti con i limiti e le verifiche del [registro](REQUISITI_E_TODO.md) e di [MATURAZIONE.md](MATURAZIONE.md). Non ripartire dalla sola analisi: le priorità residue sono sync v2/backup scalabili/migrazione legacy, qualificazione su dati scientifici reali e distribuzione/OAuth collaudati. Khamis–Roche automatico resta un eventuale metodo futuro distinto dopo verifica delle tabelle corrette; gli indici %PAH/residuo usano ora una previsione esterna tracciata.

Le sezioni successive conservano la pianificazione storica e non descrivono lo stato più recente di tutte le funzioni. Stato e priorità correnti nella [revisione generale](REVISIONE_GENERALE_2026-10-19.md); nuovi requisiti TD-83–97 e motivazioni nell'[analisi dei commenti manuali](ANALISI_TODO_MANUALI_2026-10-19.md).

Le osservazioni aggiungono una revisione coerente del dettaglio test (editor, chiusura persistente, tempi, soglie/zone, glossario e campi custom), trasparenza di collegamento cloud/licenza e una fase nuova crescita/maturazione. Per quest'ultima: prima dati antropometrici e HV qualificata; poi specifica e validazione dei singoli modelli, infine PHV longitudinale e integrazione completa degli output. Dati genitoriali/braccia/arti rimangono opzionali e secondari. Nessuno sviluppo avviato da questa acquisizione.

Restano priorità infrastrutturali sync v2, backup scalabili e migrazione legacy per società. Collaudo provider reali e Windows pulito precedono le relative promesse di rilascio; build Fedora/Android rimangono rimandate come concordato. Le nuove richieste UI possono essere affrontate come blocco coerente mentre si prepara il consolidamento, senza modificare contemporaneamente formule e formato sync.

**Consegna concordata il 18 ottobre 2026:** Windows e sorgenti; l’utente ha rimandato le build Linux/Android. I gate e i collaudi sotto restano documentati, senza avviare CI o pubblicazioni.

## Stato operativo dopo la 0.6 — non ripetere i blocchi già sviluppati

Step 5 sviluppato e verificato localmente per trasporti/controlli/rotazione e distribuzione Windows. Restano il collaudo Nextcloud con account reali, macchina Windows pulita, build/collaudo Fedora, firma di prodotto e avvisi completi delle dipendenze.

Step 6 avviato: shell Android e bridge al backend reale nel sorgente, SAF/Keystore/WorkManager e layout adattato. Prima attività bloccante: costruire wheel aggiornate Pydantic Core/Cryptography su Linux/macOS, preparare SDK/JDK/Gradle, produrre un APK e collaudarlo su emulatore/telefono. Questo ambiente Windows non ha Linux/WSL o toolchain Android; [Android](ANDROID.md) e `scripts/build_android.py --check` rendono verificabile lo stato. Non trattare il sorgente come app già rilasciata.

L’ordine successivo rimane Android completo e collaudato → Sprint breve → Wingate 30 s → Wingate 15 s. Le vecchie liste sotto sono cronologia; [consolidamento 0.6](CONSOLIDAMENTO_DISTRIBUZIONE_06.md) è il riferimento attuale.

**Stato dopo la 0.5:** sviluppati i blocchi autorizzati di preset/migrazione, motore, interfaccia/report, import e metodi specialistici; vedere [implementazione e limiti](IMPLEMENTAZIONE_INCREMENTALE_05.md). La lista sottostante conserva il piano precedente: il lavoro non riparte da zero. Restano corpus reale/validazione esterna, consolidamento operativo e WebDAV, poi Android e nuovi motori nell’ordine confermato.


17 ottobre 2026. Software attuale 0.4.1. Passi già svolti: prima iterazione società/ripristino/accessi (con lacune operative ancora aperte), definizione dei metodi incrementali costanti e ricerca delle API cloud. WebDAV confermato per Windows/Fedora e Android. Il piano seguente ordina il lavoro ancora da eseguire; non dichiara completate le funzioni pianificate.

## Prossima iterazione: metodi versionati e motore costante

1. **Registro dei preset e migrazione dell’archivio.** Separare protocollo, metodo e revisione del risultato; conservare parametri risolti e provenienza. Test preesistenti senza preset classificati come legacy, senza ricalcolo automatico. Migrazione testata anche su errore e riapertura di backup precedente.
2. **Attuare la specifica incrementale costante.** Copertura senza arrotondamento prima delle soglie, finestre temporali, controlli dei canali, FC/recupero e valori mancanti, interpolazione separata, aderenza descrittiva. Nessun coefficiente universale di soglia. Vettori numerici della specifica trasformati in test; nuova versione del motore, risultati storici preservati.
3. **Portare il contratto in UI e report.** Metodo/versione, completezza distinta dall’aderenza, qualità per metrica e fonti leggibili. Confronto esplicito fra revisione precedente e nuova; aggregati separati quando i metodi non sono confrontabili.

Questo è il **prossimo blocco da implementare**: rende operativa la definizione già concordata, senza dipendere da account cloud o file di laboratorio ancora mancanti. Accettazione: risultati sintetici attesi, migrazione reversibile tramite backup verificato, GUI/report coerenti e nessuna modifica silenziosa ai test preesistenti.

## Iterazioni successive dell’incrementale desktop

4. **Allineamento e FIT reali, INC-01/03/06/10.** Marker visuali, fine sforzo e pause/esclusioni con motivo; dispositivi/condizioni strutturati, provenienza e riconciliazione storica. Corpus autorizzato da GoldenCheetah/MyWhoosh/Zwift con casi temporali e risultati di riferimento. I FIT sintetici restano test utili, non certificazione degli esportatori.
5. **Completare i metodi specialistici, INC-04/05/08/09.** Rampe/discontinui, lattato, scambi gassosi e ripetibilità. Prima dei rispettivi motori acquisire varianti/formule del laboratorio, esempi di dati e risultati attesi: non inventare un Dmax o criteri VO₂max dal solo nome. Il nucleo costante non attende questi materiali.
6. **Consolidare archivio e scambio, INC-11/TD-50/58/59.** Estrarre il trasporto cartella dietro un’interfaccia comune; implementare **WebDAV desktop**, credenziali nel portachiavi, ripresa e conflitti/controlli firmati. Proporre Nextcloud come server iniziale di collaudo; definire esplicitamente gli altri server supportati. Spike Drive con due account in un’attività indipendente, poi adapter Drive/Dropbox secondo esito e priorità. Completare rotazione/recupero, audit e migrazioni: WebDAV da solo non chiude la sicurezza o l’intero INC-11.
7. **Rilascio desktop collaudato.** Windows e Fedora puliti, installazione/aggiornamento/ripristino, localizzazione completa, report, sincronizzazione con interruzioni e procedura di distribuzione. Distinguere build locale da rilascio operativo validato.

L’estrazione dei trasporti e la fattibilità WebDAV/Drive possono avanzare durante le altre iterazioni; il numero non impone di attendere il completamento dei gas per iniziare la sincronizzazione. Per il collaudo remoto serviranno un server e account di test: questo piano non presume accesso a servizi o credenziali dell’utente.

## Android e nuovi test

8. **Android, TD-57/AND-01–05.** Spike React/Capacitor/Python incorporato preparabile durante il consolidamento; sviluppo completo dopo la copertura incrementale desktop. Archivio autonomo offline, import, grafici, report e **WebDAV mobile confermato**, con prove di scambio Windows/Fedora/Android; adapter Drive/Dropbox quando effettivamente disponibili. Il solo visualizzatore o import/export manuale non chiude il requisito.
9. **Altri test, nell’ordine confermato:** Sprint breve / potenza neuromuscolare → Wingate 30 s → Wingate 15 s. Definire i protocolli e recuperare quello storico 15 s prima del suo motore, mantenendo metodi e confronti separati. Gli altri candidati restano distinti.

Riferimenti: [metodi incrementali](METODI_INCREMENTALE.md), [copertura completa INC](COPERTURA_TEST_E_ROADMAP.md), [trasporti cloud e WebDAV](SINCRONIZZAZIONE_CLOUD_API.md), [Android](ANDROID.md), [registro requisiti](REQUISITI_E_TODO.md).
