# Componenti di terze parti

Il codice originale di Fuorigiri è GPL-3.0-or-later. Le dipendenze mantengono le proprie licenze e i relativi avvisi.

Principali componenti: Python, FastAPI, Uvicorn, Pydantic, NumPy, Matplotlib, ReportLab, fitdecode, cryptography, React, TypeScript, Vite, Plotly.js, Lucide, PySide6/Qt e PyInstaller.

fitdecode: MIT, https://github.com/polyvertex/fitdecode/blob/master/LICENSE.txt. Lo SDK Garmin non è una dipendenza del progetto.

PySide6/Qt e Qt WebEngine includono condizioni e componenti di terzi: conservare gli avvisi e fornire le modalità richieste per accedere ai relativi sorgenti. Il pacchetto di sviluppo non è un installer firmato né una release pubblica pronta alla distribuzione. Prima di pubblicarlo completare l'inventario delle licenze, includere i testi delle dipendenze e gli adempimenti relativi a Qt/Chromium.

Le versioni risolte sono registrate in `requirements-lock-windows.txt` e `frontend/package-lock.json`. Il lock Python Windows è un riferimento della macchina di verifica, non un lock portabile a Linux (contiene dipendenze specifiche del sistema).
# Marchio e logo della società

`frontend/public/branding/progetto-ciclismo.png` è il logo fornito da Luca Bontempi per l'inclusione nel software sviluppato per Progetto Ciclismo - Rodengo Saiano A.S.D. Il marchio è distinto dal codice GPL; la distribuzione del sorgente non concede automaticamente diritti ulteriori sul marchio. L'asset originale è conservato senza modifiche e incluso localmente nel bundle e nei report.


## Aggiunte 0.6

Keyring 25.7.0 e relative dipendenze: conservare licenze/metadati delle wheel nel pacchetto; Windows Credential Manager e Linux Secret Service. Android: Kotlin, AndroidX Activity/WebKit/WorkManager, Chaquopy e runtime Python, più le dipendenze native scientifiche/critto elencate in android/requirements.txt. La matrice nativa e la raccolta completa degli avvisi devono essere verificate sul builder Android prima di distribuire un APK.

Inno Setup è uno strumento di build con propria licenza, non una dipendenza da installare sul PC destinatario. Flatpak e i runtime mantengono le proprie licenze. Le pipeline e i checksum non costituiscono una firma del prodotto o un audit legale completo.

La nuova icona Fuorigiri (`fuorigiri.svg` e derivate) è opera del progetto e segue GPL-3.0-or-later. Il logo societario originale e la sua attribuzione rimangono invariati.

Android 0.7: Google Play services Auth 22.0.0 dichiarato come dipendenza Gradle, soggetto alle condizioni Google Play services; non incluso nei sorgenti e non redistribuito in un APK in questa consegna. Le API cloud sono chiamate HTTP, senza SDK proprietari aggiunti al runtime Python.
