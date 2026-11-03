# Revisione tecnica prima alpha

Verifica del **2 novembre 2026**, requisito **ALPHA-REVIEW-01**, prodotto **0.10.0**. Esito: correzioni nei sorgenti e nell'ambiente Windows; **il candidato `alpha-prep-20261102-01` richiede un successore e la risoluzione dei punti Android sotto**. Artefatti precedenti conservati.

**Successore Windows prodotto:** `windows-alpha-review-20261102-01`, nuove build bundle/installer, regressioni e smoke riusciti; [riscontri](VERIFICA.md). Non è una pubblicazione o prova Windows pulito. Android rimane separato: candidato Pillow esistente e kit sorgenti native 16 KB ancora da eseguire su Fedora, senza nuove wheel/APK di quest'ultima fase.

## Problemi e correzioni

| Area | Riscontro | Intervento |
|---|---|---|
| Ripristino backup | ZIP cifrati o con compressione sconosciuta causavano RuntimeError/NotImplementedError | Controllo dei membri prima della lettura, condiviso fra legacy e v3; risposta 422, staging eliminato, nessun archivio registrato |
| Sviluppo frontend | Vite 6.4.4 segnalato da npm audit | Patch 6.4.5; minimo e lockfile allineati |
| Ambiente Windows | Avvisi PyPI per certifi 2026.7.22, Pillow 12.3.0, pypdf 6.21.2 e setuptools 84.0.0 | Installati certifi 2026.10.19, Pillow 13.0.0, pypdf 6.21.4 e setuptools 84.1.0; lock aggiornato, pypdf prima assente aggiunto; minimi setuptools/pypdf nel progetto |
| Multipart Android | L'APK contiene python-multipart 0.0.20 con avvisi noti | Requisito Android aggiornato a 0.0.32, già verificato nella suite Windows; minimo condiviso nel progetto. Nessun nuovo APK prodotto |

Fonti: [Vite](https://github.com/advisories/GHSA-8g5g-mxqh-grgj), [certifi](https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2), [Pillow 13](https://github.com/python-pillow/Pillow/releases/tag/13.0.0), [pypdf 6.21.4](https://github.com/py-pdf/pypdf/releases/tag/6.21.4), [setuptools](https://github.com/pypa/setuptools/security/advisories/GHSA-xmj3-9gf7-h52w), [multipart](https://github.com/Kludex/python-multipart/security/advisories/GHSA-wp53-j4wj-2cfg). Consultati anche gli avvisi dell'API JSON PyPI per le versioni installate. Gli alias GHSA/PYSEC/CVE non sono vulnerabilità indipendenti.

Vite riguarda il server di sviluppo esposto in rete; Fuorigiri distribuisce asset statici e lo sviluppo locale usa loopback. Setuptools riguarda installazione legacy di wheel; pypdf è una dipendenza di test. Una dipendenza segnalata non dimostra che ogni percorso degli avvisi sia raggiungibile nell'app.

## Punto aperto Android

**Seguito native 16 KB:** auditor completo di tutte le `.imy` conferma sei moduli non qualificati su 222 ELF (il precedente conteggio 106 non includeva la stdlib). Sorgenti candidati e builder Fedora preparati in [ANDROID_NATIVE_16KB.md](ANDROID_NATIVE_16KB.md); libpng 1.6.59 scelta anche per la correzione CVE-2026-46675 dichiarata upstream. Non è una nuova build nativa riuscita, né un audit di sicurezza completo; adozione, APK e runtime attendono i binari.

**Aggiornamento dopo il builder Fedora:** ricevute Pillow 13.0.0 ARM64/x86_64, verificate localmente integrità, RECORD, architetture, DT_NEEDED e LOAD 16 KB; pin/gate/provenienza e avvisi nativi integrati. [Registro build e runtime corrente](VERIFICA.md). Le nuove librerie statiche Pillow non sostituiscono chaquopy-freetype 2.9.1 e libpng 1.6.34 ancora richieste separatamente da Matplotlib: l'audit nativo globale rimane un gate. Le descrizioni sotto del vecchio candidato restano storiche.

**Aggiornamento operativo del 2 novembre:** completata l'interrogazione degli indici e preparato un kit sorgenti Pillow 13.0.0/libjpeg-turbo 3.2.0/FreeType 2.14.3, con builder Fedora sperimentale. L'utente eseguirà i comandi sulla Toolbox; nessuna nuova wheel o APK prodotto. [Comandi, provenienza e gate](ANDROID_PILLOW.md). I pin e i digest dell'app restano invariati in attesa delle prove.

L'inventario CONTENTS.json del candidato contiene **Pillow 11.0.0** per debug e release, con avvisi di sicurezza. L'[indice Chaquopy consultato](https://chaquo.com/pypi-13.1/pillow/) offre ancora 11.0.0 per Python 3.13; non è stata trovata una wheel 13.0.0 nelle due ABI richieste. Non inserire un pin irrisolvibile né usare wheel Windows/Linux come sostituto.

Prima della distribuzione occorre produrre/ottenere wheel corrette ARM64 e x86_64, oppure backport verificati con provenienza, digest e test, poi ricompilare e collaudare immagini/report sull'app. Il codice report esaminato usa logo fisso e figure generate localmente; non è emerso un endpoint di caricamento immagini arbitrarie. Questo limita la superficie osservata, ma non qualifica la vecchia libreria. Nessun binario nativo o relativo hash modificato.

I sei pacchetti chaquopy-* dell'inventario non sono verificabili mediante PyPI: servono verifiche delle librerie native incorporate. L'audit non copre integralmente AndroidX, Qt/Chromium, librerie di sistema o dipendenze native transitive.

## Copertura e risultati

- Ispezionati autenticazione HTTP/host/origine, workspace e ruoli, validazione/ripristino ZIP e SQLite, OAuth, bridge Android e WebView; eseguite regressioni esistenti su sync, firme, conflitti, backup, isolamento e metodi scientifici. Formule e snapshot invariati.
- Suite iniziale: 263 passati, 1 skip. Dopo aggiornamenti e correzione backup: **265 passati, 1 skip**, 2 warning, 111,68 s. Poi estesa la regressione ZIP dal manifest al database: **4 casi mirati passati**. Skip per symlink non disponibili all'account Windows; warning Starlette/httpx e duplicato ZIP intenzionale.
- **37 test frontend passati**, build TypeScript/Vite 6.4.5 riuscita. I 19 file frontend sono byte-identici all'inventario del candidato; resta il warning noto sul chunk Plotly differito. Nessuna modifica UI o nuovo collaudo grafico completo.
- pip check, verify_versions.py, verify_core.py, verify_suite_ui.py e git diff --check riusciti. Smoke desktop dai sorgenti su archivio QA nuovo: import, logo e backend HTTP riusciti; non è uno smoke di un nuovo EXE.
- Audit npm dopo aggiornamento: zero avvisi. Nuova interrogazione PyPI sulle 62 distribuzioni locali: nessun avviso nelle versioni pubbliche risolte; Fuorigiri/core sono locali, il vecchio metadato ciclo-test 0.1.0 non risolve su PyPI e non è stato cancellato. Non equivale ad assenza di vulnerabilità.
- EPERM iniziale sulla licenza generata: build autorizzata fuori sandbox riuscita, senza modificare manualmente le risorse legali.

## Prima della pubblicazione

1. Risolvere Pillow e completare l'audit nativo Android; verificare multipart nella nuova build e nel runtime mobile.
2. Generare un nuovo candidato Windows/Android con dipendenze corrette, inventario, checksum e smoke. I vecchi EXE/APK non vengono aggiornati dal checkout.
3. Completare i gate pertinenti di [COLLAUDO_PILOT.md](COLLAUDO_PILOT.md): firma Android del titolare, installazione/aggiornamento Windows pulito e telefono ARM64, backup/ripristino e flussi operativi; provider/due account reali se inclusi nell'alpha.

Nessuna pubblicazione, firma, nuova build EXE/APK, prova su telefono o qualifica provider reale effettuata. Modifiche documentali preesistenti conservate.
