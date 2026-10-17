# Componenti di terze parti

Il codice originale di Ciclo Test è GPL-3.0-or-later. Le dipendenze mantengono le proprie licenze e i relativi avvisi.

Principali componenti: Python, FastAPI, Uvicorn, Pydantic, NumPy, Matplotlib, ReportLab, fitdecode, cryptography, React, TypeScript, Vite, Plotly.js, Lucide, PySide6/Qt e PyInstaller.

fitdecode: MIT, https://github.com/polyvertex/fitdecode/blob/master/LICENSE.txt. Lo SDK Garmin non è una dipendenza del progetto.

PySide6/Qt e Qt WebEngine includono condizioni e componenti di terzi: conservare gli avvisi e fornire le modalità richieste per accedere ai relativi sorgenti. Il pacchetto di sviluppo non è un installer firmato né una release pubblica pronta alla distribuzione. Prima di pubblicarlo completare l'inventario delle licenze, includere i testi delle dipendenze e gli adempimenti relativi a Qt/Chromium.

Le versioni risolte sono registrate in `requirements-lock-windows.txt` e `frontend/package-lock.json`. Il lock Python Windows è un riferimento della macchina di verifica, non un lock portabile a Linux (contiene dipendenze specifiche del sistema).
