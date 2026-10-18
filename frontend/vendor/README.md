# UI della suite — artefatto versionato

`cycling-suite-ui-0.1.0.tgz` proviene dalla repository autonoma `cycling-suite-common`. Non è una seconda copia di lavoro da modificare: la sorgente autorevole e il tag sono registrati in `suite-ui-provenance.json`, insieme allo SHA256.

Il tarball comprende codice ESM, dichiarazioni, CSS, logo originale, sorgenti TypeScript e script di build, licenza e avvisi. `npm ci` lo installa senza richiedere il clone della repository comune. La dipendenza React è fornita dall’app.

Aggiornamento: produrre una nuova versione nella repository comune, copiarne l’artefatto qui, aggiornare la provenienza, eseguire `npm install ./vendor/<nuovo-pacchetto>.tgz --save-exact` dal frontend, quindi `python scripts/verify_suite_ui.py` dalla radice e compilare/verificare l’app. Non modificare un artefatto già consegnato mantenendo la stessa versione.

[Decisioni e guida](../../docs/SUITE_CONDIVISA.md).
