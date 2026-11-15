import {useState} from 'react';
import {Dialog} from './Dialog';
import {language} from './i18n';
export function Legal({api}: {api: any}) {
  const [open, setOpen] = useState(false),
    [data, setData] = useState<any>(null),
    [error, setError] = useState('');
  const en = language === 'en';
  return (
    <>
      <p className="legal-notice">
        GPL-3.0-or-later ·{' '}
        {en
          ? 'Provided without warranty, to the extent permitted by law. Data preservation is not guaranteed.'
          : 'Fornito senza garanzia, nei limiti di legge. La conservazione dei dati non è garantita.'}{' '}
        <button
          className="text-button"
          onClick={() => {
            setOpen(true);
            api('legal')
              .then(setData)
              .catch((e: Error) => setError(e.message));
          }}
        >
          {en ? 'License, limitations and backups' : 'Licenza, limiti e backup'}
        </button>
      </p>
      {open && (
        <Dialog title={en ? 'License and limitations' : 'Licenza e limiti'} onClose={() => setOpen(false)}>
          <h2>Fuorigiri Performance Lab · {data?.version || '…'}</h2>
          <p>
            {en
              ? 'Provided as is without warranty, to the extent permitted by applicable law. No guarantee against data loss, corruption or unavailability.'
              : 'Software fornito così com’è, senza garanzia nei limiti della legge applicabile. Non si garantisce l’assenza di perdita, corruzione o indisponibilità dei dati.'}
          </p>
          <p>
            {en
              ? 'Keep independent backups and test restoration. Sync is not a backup. Legacy ZIP backups remain limited to 100 MB compressed, 1 GB expanded and 10,000 attachments. Scalable v3 ZIP64 backups use disk streaming, with safety limits of 64 GB compressed, 256 GB expanded and 1,000,000 data files; available disk space also applies.'
              : 'Conserva copie indipendenti e prova il ripristino. La sincronizzazione non è un backup. I backup ZIP precedenti mantengono i limiti di 100 MB compressi, 1 GB espanso e 10.000 allegati. Il formato v3 ZIP64 elabora i dati su disco, con limiti di sicurezza di 64 GB compressi, 256 GB espansi e 1.000.000 di file dati; serve spazio disponibile sufficiente.'}
          </p>
          <p>
            {en
              ? 'Athlete data, often of minors, are stored unencrypted in the local archive and in ZIP backups. Turn on device encryption (BitLocker or Device encryption on Windows; on Android set a screen lock), protect the account with a password and keep backups on encrypted or access-controlled storage.'
              : 'I dati degli atleti, spesso minorenni, sono salvati senza cifratura nell’archivio locale e nei backup ZIP. Attiva la cifratura del dispositivo (BitLocker o Crittografia dispositivo su Windows; su Android imposta un blocco schermo), proteggi l’account con una password e conserva i backup su supporti cifrati o ad accesso controllato.'}
          </p>
          <p>
            {en
              ? 'Estimates depend on methods and data quality; they do not constitute a medical diagnosis. Mandatory legal rights remain unaffected.'
              : 'Le stime dipendono da metodo e qualità dei dati; non costituiscono una diagnosi medica. Restano salvi i diritti inderogabili previsti dalla legge.'}
          </p>
          {error && <p role="alert">{error}</p>}
          {data && (
            <>
              <details>
                <summary>GNU GPL v3</summary>
                <pre className="license-text">{data.license}</pre>
              </details>
              <details>
                <summary>{en ? 'Third-party notices' : 'Avvisi delle dipendenze'}</summary>
                <pre className="license-text">{data.third_party}</pre>
              </details>
            </>
          )}
        </Dialog>
      )}
    </>
  );
}
