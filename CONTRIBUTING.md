# Contribuire a Fuorigiri

> **In English.** Bug reports, ideas and pull requests are welcome, in Italian or English. Use the issue forms, never attach real athlete data, and report security problems privately as described in [SECURITY.md](SECURITY.md). Contributions are accepted under GPL-3.0-or-later.

Grazie dell'interesse. Fuorigiri è in fase alpha e viene sviluppato per l'uso nelle società di ciclismo giovanile: prima di proporre modifiche ampie apri una issue per discuterne.

## Segnalazioni e proposte

- **Problemi:** apri una issue con il modulo «Segnala un problema».
- **Nuove funzioni:** apri una issue con il modulo «Proponi una funzione». Indica a chi serve e come si fa oggi.
- **Vulnerabilità:** non aprire issue pubbliche, segui [SECURITY.md](SECURITY.md).

Lingua: italiano o inglese.

## Dati personali

Non allegare a issue o pull request dati reali di atleti (anche minorenni), file FIT personali, archivi, backup, inviti, `identity.json`, token o credenziali. Per riprodurre un problema usa il [corpus sintetico](docs/DATI_SINTETICI.md) o dati inventati. Anche le schermate devono mostrare solo dati sintetici.

## Ambiente di sviluppo

La [guida di avvio e collaudo](docs/TESTARE_IL_PROGETTO.md) descrive dipendenze Python/Node, avvio della GUI e dati dimostrativi. Usa sempre cartelle dati nuove e dedicate alle prove.

Prima di aprire una pull request, dalla radice:

```powershell
.venv/Scripts/python.exe scripts/verify.py
```

Il comando esegue test Python e frontend, build, linter e controllo del formato. Per formattare:

```powershell
.venv/Scripts/python.exe -m ruff format .
npm --prefix frontend run format
```

Non mescolare riformattazioni estese e modifiche di comportamento nello stesso commit.

## Regole del progetto

Le regole complete sono in [AGENTS.md](AGENTS.md), valide anche per gli assistenti di programmazione. Le più importanti:

- **Metodi scientifici:** separa valori misurati, dichiarati, calcolati e stimati; nessun ricalcolo silenzioso degli storici, nessun coefficiente universale implicito. Un nuovo metodo richiede fonti primarie, dominio di validità e vettori numerici di prova.
- **Dati e formati:** conserva compatibilità con archivi, backup e pacchetti di scambio esistenti; non cancellare revisioni o pacchetti per risparmiare spazio.
- **Interfaccia:** etichette comprensibili con unità esplicite, traduzioni italiane e inglesi, accessibilità. I componenti comuni (tema, finestre, liste, tempi) arrivano da `cycling-suite-common`: le modifiche vanno proposte là.
- **Dipendenze Python:** dopo una modifica a `requirements-lock-windows.txt` rigenera gli hash con `scripts/lock_hashes.py --write`.
- **Documentazione:** aggiorna [CHANGELOG.md](CHANGELOG.md) e, se cambiano requisiti o stato verificato, [REQUISITI_E_TODO.md](docs/REQUISITI_E_TODO.md) e [VERIFICA.md](docs/VERIFICA.md).
- **Branding:** logo e attribuzione della società sono fissi; non renderli configurabili.

## Licenza

Inviando un contributo accetti che sia distribuito con la stessa licenza del progetto, [GPL-3.0-or-later](LICENSE). Non includere codice, dati o immagini di terzi senza indicarne licenza e provenienza in [THIRD_PARTY.md](THIRD_PARTY.md).
