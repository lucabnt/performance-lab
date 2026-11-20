# Sicurezza

> **In English.** Please report vulnerabilities privately through GitHub: *Security → Report a vulnerability* on this repository. Do not open a public issue and do not attach real athlete data, backups, invites, `identity.json` files, tokens or passwords. Reports in English are welcome.

## Come segnalare una vulnerabilità

Usa la segnalazione privata di GitHub: scheda **Security → Report a vulnerability** di questa repository. La segnalazione resta visibile solo a te e al manutentore finché non viene pubblicato un avviso.

Non aprire una issue pubblica per problemi di sicurezza e non descriverli in discussioni o pull request.

Nella segnalazione indica:

- versione (in **Info** nell'app) e piattaforma: installer o portabile Windows, Android, sorgenti;
- componente coinvolto, ad esempio sincronizzazione, inviti e ruoli, backup, API locale, import CSV/FIT, report;
- passi per riprodurre il problema con **dati sintetici** e impatto concreto (lettura, modifica o perdita di dati, aggiramento dei ruoli, esecuzione di codice).

## Cosa non inviare

Anche nella segnalazione privata non allegare:

- dati reali di atleti, file FIT personali, archivi `archive.sqlite` o backup (`.zip`, `.fgbak`);
- `identity.json`, inviti, file di recupero accessi, chiavi o password di backup;
- credenziali WebDAV o cloud, token dell'URL locale (`#token=…`);
- `server.log` senza averlo prima riletto ed eventualmente ridotto.

Se serve un archivio di esempio, crealo con il [corpus sintetico](docs/DATI_SINTETICI.md).

## Versioni coperte

| Versione | Correzioni di sicurezza |
|---|---|
| Ultima pre-release pubblicata (attualmente `0.10.0-alpha.1`) e ramo `main` | Sì |
| Candidati e build precedenti non pubblicati | No |

Fuorigiri è in fase alpha ed è mantenuto da una sola persona: le segnalazioni vengono esaminate appena possibile, senza tempi di risposta garantiti. Le correzioni arrivano in una nuova release; una modifica ai sorgenti non aggiorna un EXE o un APK già installato.

## Ambito

Rientrano in particolare:

- firme, cifratura, revoche e rotazione della chiave nello scambio fra dispositivi (cartella, WebDAV e provider cloud sperimentali);
- inviti, ruoli (fondatore, admin dati, visualizzatore) e recupero accessi;
- backup protetti da password e ripristino;
- API locale, token di sessione e Content Security Policy dell'interfaccia;
- import di file (CSV, FIT, backup) ed export CSV.

Non sono vulnerabilità del progetto:

- i rilevamenti antivirus delle build non firmate: vedi [WINDOWS_DEFENDER.md](docs/WINDOWS_DEFENDER.md);
- un accesso già ottenuto all'account o alla cartella dati del dispositivo;
- i problemi dei servizi esterni (server WebDAV, Google Drive, Dropbox, OneDrive) che non dipendono da Fuorigiri.

Per i limiti noti dello scambio e dei backup vedi [SYNC_V2_E_BACKUP.md](docs/SYNC_V2_E_BACKUP.md) e [BACKUP_CIFRATO.md](docs/BACKUP_CIFRATO.md).
