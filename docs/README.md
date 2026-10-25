# Documentazione di Fuorigiri Performance Lab

Indice aggiornato al **25 ottobre 2026**, sorgenti **0.10.0**. Le guide descrivono i sorgenti attuali; i pacchetti già compilati possono essere precedenti. Per le prove effettive consultare il registro verifiche.

## Uso, avvio e distribuzione

- [Importazione CSV e modelli vuoti](IMPORT_CSV.md): cinque profili, comprese le appartenenze storiche e future.
- [Primo collegamento Google Drive](GOOGLE_DRIVE_PRIMO_COLLEGAMENTO.md): progetto OAuth, cartella, collegamento dei dispositivi e collaudo prima dei dati operativi.

- [Collaudo candidato pilot](COLLAUDO_PILOT.md): operazioni, risultati attesi, check di completamento e verbale Windows/Android.
- [Firma Android](FIRMA_ANDROID.md): creazione/custodia chiave a cura del titolare e firma/verifica della copia release.

- [Testare il progetto e l’interfaccia](TESTARE_IL_PROGETTO.md): ambiente di sviluppo, desktop/browser, demo, reset e checklist.
- [Dati sintetici](DATI_SINTETICI.md): composizione del corpus, scenari e risultati attesi.
- [Galleria dell’interfaccia](screenshots/README.md): viste del README e procedura per mantenerle aggiornate con dati sintetici.
- [Società, backup e accessi](SOCIETA_BACKUP_E_ACCESSI.md): creazione, inviti, ruoli e ripristino.
- [Sync v2, backup v3 e separazione società](SYNC_V2_E_BACKUP.md): attivazione, compatibilità, flussi GUI/CLI e limiti.
- [Configurare la sincronizzazione](CONFIGURARE_LA_SINCRONIZZAZIONE.md): cartelle, WebDAV, Drive, Dropbox, OneDrive e prerequisiti OAuth.
- [Distribuzione](DISTRIBUZIONE.md): bundle Windows, dipendenze incluse, installer e prerequisiti Fedora/Android.

## Protocolli e metodi

- [Protocolli e campi personalizzati](PROTOCOLLI_E_CAMPI_CUSTOM.md).
- [Metodi dell’incrementale](METODI_INCREMENTALE.md).
- [Sprint e Wingate](TEST_ANAEROBICI.md).
- [Crescita e maturazione](MATURAZIONE.md).

Le specifiche conservano fonte, versione e limiti: una stima non diventa una misura osservata e protocolli differenti non diventano automaticamente confrontabili.

## Sviluppo e stato del prodotto

- [Requisiti e to-do](REQUISITI_E_TODO.md): registro con ID e tracciabilità; gli aggiornamenti più recenti prevalgono sulle sezioni storiche.
- [Prossimi passi](PROSSIMI_PASSI.md): priorità attuali, dipendenze e criteri di completamento.
- [Verifiche](VERIFICA.md): prove eseguite e limiti, in ordine cronologico inverso.
- [Architettura generale](../ARCHITETTURA_PROPOSTA.md): decisioni di backend, UI, dati e distribuzione; documento evolutivo con sezioni datate.
- [Dimensioni e scalabilità della sincronizzazione](SYNC_DIMENSIONI_E_SCALABILITA.md).
- [Pratiche Android riutilizzabili nella suite](ANDROID_PRATICHE_SUITE.md): componenti comuni, navigazione/persistenza, elenchi/moduli e gate.
- [Android](ANDROID.md): architettura e gate di build/dispositivo ancora aperti.
- [Wheel Android su Fedora Kinoite](ANDROID_WHEEL_FEDORA.md): procedura consolidata Toolbox, dipendenze native, hook, checksum e trasferimento Windows.
- [Suite condivisa con Ammiraglia](SUITE_CONDIVISA.md).
- [Changelog](../CHANGELOG.md) e [istruzioni della repository](../AGENTS.md).

## Come mantenere la documentazione

Le istruzioni operative appartengono alla guida del relativo tema; formule e limiti alla specifica del metodo; stato e accettazione al registro requisiti; risultati al registro verifiche. La roadmap riassume il lavoro residuo senza duplicare la cronologia. I documenti correnti hanno nomi indipendenti dalla release che li ha introdotti.

Analisi iniziali, commenti originali, revisioni e piani superati sono conservati in [archivio](archivio/README.md). Mantengono le motivazioni e gli ID storici, senza prescrivere lo stato corrente. Non cancellare le fonti originali né presentare una build predisposta come collaudata.
