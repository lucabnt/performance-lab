# Wheel native Android

Le wheel non vengono prese da repository binari non verificati. Questa directory riceve gli artefatti di un builder Linux/macOS autorizzato e il relativo `SHA256.json` (mappa nome file → digest SHA256).

Gate iniziale: `pydantic_core==2.41.4` e `cryptography==50.0.2`, Python 3.13, ABI `arm64-v8a` e `x86_64`, API minima compatibile con minSdk 26. Le versioni pronte nel repository Chaquopy sono state verificate: Pydantic Core assente; Cryptography solo 42.0.8 per cp313. Non viene effettuato un downgrade della crittografia per ottenere un APK.

Per compilare pacchetti Python 3.13+, Chaquopy raccomanda [cibuildwheel Android](https://cibuildwheel.pypa.io/en/stable/platforms/#android), su **Linux x86_64 o macOS**, con SDK/NDK. Le estensioni Rust richiedono i target Android e Cryptography anche OpenSSL compilato per la stessa ABI: non basta rinominare una wheel manylinux/Windows. La procedura della singola libreria va completata e collaudata sul builder, compresa la compatibilità delle pagine di memoria da 16 KB.

NumPy 1.26.2 e Matplotlib 3.8.4 hanno wheel cp313 nel repository ufficiale Chaquopy. La loro presenza non certifica il caricamento su tutti i dispositivi né la compatibilità 16 KB. Il gate finale comprende tutte le dipendenze native transitive e il collaudo nell'app, non soltanto le due wheel sopra.

Eseguire dalla radice `python scripts/build_android.py --check`. Finché il controllo segnala prerequisiti mancanti, non esiste un APK funzionante di questa revisione. Il sorgente della shell e il contratto ASGI sono presenti e testati separatamente; TD-57 rimane aperto.
