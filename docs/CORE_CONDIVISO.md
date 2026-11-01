# Runtime comune — 20 ottobre 2026

Fuorigiri consuma `cycling-suite-core` 0.1.2, wheel locale sotto `vendor`, installata da `requirements-common.txt` incluso nei lockfile. I moduli `credentials.py`, `transports.py` e `instance.py` sono adattatori al codice comune; `desktop.py` conserva lifecycle, server e percorsi del prodotto e usa la finestra Qt condivisa.

Conservati i servizi vault WebDAV/Cloud, `_mobile` per Keystore Android, directory di canale legacy/current, User-Agent e nome del lock. Nessun database, protocollo scientifico, chiave o journal è migrato da questa estrazione. La UI 0.2.2 resta invariata.

Dal repository common: `python scripts/sync-core.py --app ../club-lab --app ../performance-lab --install`, poi la stessa chiamata con `--check`. Dal clone Fuorigiri: `python -m pip install -r requirements-common.txt` e `python scripts/verify_core.py`; non serve il clone common per avvio, test o build. La wheel contiene sorgenti, GPL e provenienza; non editarla a mano.

Il packaging Windows controlla il core prima della build. Predisposti l'inclusione della wheel in Chaquopy e nella wheelhouse Flatpak; nessuna build Android/Linux eseguita, come da perimetro concordato. Gli esiti di regressione e le prove desktop effettive sono in VERIFICA.
