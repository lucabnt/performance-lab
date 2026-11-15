# Backup protetto da password

Formato approvato il 15 novembre 2026 (revisione tecnica, RT-11, blocco 4). Implementazione: `backend/cycling_test/backup_crypto.py`. Il backup v3 in chiaro resta il formato predefinito, leggibile e producibile.

## Uso

- **Creazione** in Archivio e scambio, con l'opzione «Proteggi con password», disattivata di default. La password va inserita due volte e deve avere almeno 12 caratteri. Il pulsante scarica `fuorigiri-backup-v3.fgbak`. Su desktop, anche «Salva direttamente su disco» accetta la password: in quel caso il percorso deve terminare con `.fgbak`.
- **Ripristino** da Gestisci società → Ripristina da backup. Il selettore accetta `.zip` e `.fgbak`. Per un `.fgbak` l'interfaccia chiede la password e poi mostra la stessa anteprima e le stesse modalità di ripristino del v3.
- **Password persa**: senza la password il backup non è recuperabile da nessuno. Va conservata separatamente, per esempio in un gestore di password. Il recupero accessi resta un file separato, protetto dalla propria password.
- **Disponibilità**: l'opzione compare dove è già disponibile lo scaricamento del backup v3, quindi anche nella WebView Android. Non è stato ancora provato su emulatore o telefono.

## Formato (versione 1)

```text
"FGBAKENC" | u32 lunghezza intestazione | intestazione JSON | blocco*
blocco = u32 lunghezza cifrato | cifrato AES-256-GCM (testo ≤ 1 MiB + tag 16 byte)
```

Intestazione JSON canonica:

```json
{"chunk_size":1048576,"cipher":"AES-256-GCM","content":"backup-v3-zip","format":"fuorigiri-backup-encrypted",
 "kdf":{"n":131072,"name":"scrypt","p":1,"r":8,"salt":"<16 byte base64>"},"version":1}
```

- **Contenuto**: il backup v3 ZIP64 esistente, invariato. Dopo la decifratura passa per le stesse verifiche di integrità del v3.
- **Chiave**: scrypt sulla password UTF-8, con sale casuale di 16 byte e parametri scritti nell'intestazione (n = 2^17, r = 8, p = 1, circa 128 MB di memoria e circa 0,3 s su PC di sviluppo). In lettura si accettano soltanto n tra 2^14 e 2^20, potenza di due, con r = 8 e p = 1, così che un file manipolato non possa richiedere memoria eccessiva. Un aumento futuro dei parametri non toglie la lettura dei file precedenti.
- **Blocchi**: nonce = indice del blocco su 12 byte; la chiave è unica per file grazie al sale. I dati associati sono `SHA-256(intestazione) | u64 indice | u8 ultimo`. Un file vuoto produce comunque un blocco finale.
- **Integrità**: troncamento, blocchi riordinati, duplicati o aggiunti, byte alterati e intestazione modificata vengono rifiutati. Un errore sul primo blocco viene presentato come «password errata o backup alterato». In caso di errore il file di uscita parziale viene rimosso; un file di destinazione già esistente non viene mai sovrascritto.
- **Versione**: una versione dell'intestazione diversa da 1 viene rifiutata con l'invito ad aggiornare Fuorigiri.
- **Dipendenze**: nessuna nuova; si usa soltanto `cryptography`, già richiesta.

## Cosa protegge e cosa no

| Protegge | Non protegge |
|---|---|
| Contenuto del backup copiato su chiavetta, cloud o disco esterno | Password debole o riutilizzata: scrypt rallenta, ma non impedisce, i tentativi offline |
| Modifiche e troncamenti del file (rilevati) | Archivio aperto sul dispositivo, che resta non cifrato: vedi [Proteggere i dati sul dispositivo](SOCIETA_BACKUP_E_ACCESSI.md) |
| | Copia decifrata nell'area `restore-staging` tra anteprima e ripristino (rimossa al ripristino o dopo 24 ore) |
| | Nome e dimensione del file |

## Flusso tecnico

- **Download**: `POST /api/v1/backup/scalable/encrypted` con `{"password": …}` nel corpo, mai nell'URL. Il backup v3 viene scritto in una cartella temporanea, cifrato a blocchi su disco, e il v3 in chiaro viene rimosso prima dell'invio. L'operazione è consentita anche ai visualizzatori, come lo scaricamento del v3.
- **Salvataggio su disco**: `POST /api/v1/backup/scalable/save` accetta il campo facoltativo `password`. Con la password scrive un `.fgbak` accanto alla destinazione e lo pubblica senza sovrascrivere.
- **Anteprima**: `POST /api/v1/workspaces/restore/preview` accetta il campo facoltativo `backup_password`. Il formato si riconosce dalla firma iniziale, non dall'estensione. Il file viene decifrato su disco e l'area temporanea conserva solo lo ZIP decifrato, identificato dal suo SHA-256. Ripristino e controlli restano quelli del v3. La risposta contiene `encrypted`.

## Prove

- **Test automatici** in `tests/test_backup_crypto.py`:
  - andata e ritorno ai confini dei blocchi (0, 1 byte, 1 MiB ± 1, 2 MiB);
  - password errata o assente;
  - cinque tipi di danneggiamento;
  - limiti dell'intestazione;
  - nessuna sovrascrittura;
  - ripristino reale via API con verifica di storico e allegati;
  - v3 in chiaro ancora producibile e ripristinabile.
- **Prova GUI** del 15 novembre in [VERIFICA.md](VERIFICA.md).
