# Zone FC e watt nei test e nel profilo

25 ottobre 2026 — ZONE-02. Gli intervalli delle zone non richiedono un file FIT: servono lo schema percentuale e un valore di riferimento valido. Il FIT/CSV temporale serve invece per calcolare il tempo trascorso in ciascuna zona. In assenza di campioni i secondi rimangono non disponibili, senza inventare una distribuzione dalla durata o dalle medie.

## Test aerobici, compresi gli import storici

Il dettaglio aerobico mostra gli intervalli FC e watt. Gli schemi e i risultati delle zone già salvati nel test hanno precedenza e non vengono ricalcolati. Se le zone mancano, vengono ricavati in lettura dai riferimenti salvati; per un canale senza schema si usa il preset PCRS-SOGLIA-5Z nella versione mostrata. La schermata distingue questi intervalli derivati dai risultati archiviati. I nuovi import CSV conservano anche lo snapshot delle zone nel nuovo test.

Il preset FC usa FTHR; quello watt usa la potenza di soglia. Se il riferimento richiesto manca, il canale resta visibile con una spiegazione. La MAP non diventa automaticamente potenza di soglia e FC massima non diventa automaticamente FTHR. Non vengono introdotti coefficienti universali o reinterpretati i dati storici.

Anche il report individuale PDF/Markdown usa questa lettura compatibile: renderer `0.10-training-zones-1`, nuovo cache key e report precedenti conservati. Nessuna modifica ai risultati scientifici o alle revisioni originali per riempire le zone mancanti.

## Scelta sul profilo

Apri il profilo e usa **Zone di allenamento del profilo → Scegli zone**.

Dal 26 ottobre l'editor si apre in una finestra immediatamente visibile. Per cambiare le percentuali scegli **Zone personalizzate** e modifica **Limite superiore %** nelle tabelle FC/potenza, poi i valori di riferimento in bpm/W. Gli intervalli adottati mostrano anche la colonna **% del riferimento**. Il riepilogo del profilo resta compatto; apri **Intervalli e percentuali FC/potenza** per le tabelle complete. Il grafico **MAP storiche** segue subito il riepilogo delle zone e parte dalla MAP, indipendentemente dalla metrica usata negli altri storici.

- **Ultime zone disponibili**, scelta iniziale: per ciascun canale viene usato il test aerobico non eliminato più recente, in ordine di data, che dispone del riferimento. FC e watt possono provenire da due test diversi: data e revisione sono riportate accanto al canale. Una correzione del test o un nuovo test può aggiornare questa vista automatica.
- **Zone adottate da un test:** scegli il test dalla data/protocollo, esamina l'anteprima e salva. Il profilo conserva uno snapshot della revisione scelta, compresi riferimento, schema e intervalli. Correzioni o eliminazione successiva del test non sostituiscono automaticamente questa scelta; per aggiornare occorre adottare di nuovo una revisione oppure tornare alla modalità automatica.
- **Zone personalizzate:** definisci nome degli schemi, riferimento FC/watt, valore del riferimento e limiti superiori percentuali delle zone. Puoi aggiungere o rimuovere zone e scegliere inclusività dei confini; l'ultima zona resta aperta. Ogni salvataggio assegna una nuova versione custom, distinta da quella del preset iniziale. Il profilo mostra gli intervalli in bpm/W risultanti.

Le zone del profilo sono definizioni di allenamento: non riportano il tempo di permanenza di un test e non riscrivono i test passati. I canali senza riferimento rimangono non disponibili, anche quando l'altro canale è completo. Per le zone custom sono necessari entrambi i riferimenti scelti, positivi e validi.

## Versioni e condivisione

La scelta è nel record atleta `training_zone_selection`, con nuova revisione e data di salvataggio, mode e provenienza. Per adottare un test devono corrispondere atleta, società e revisione esaminata; il controllo base dell'atleta previene sovrascritture concorrenti. La modifica anagrafica conserva la scelta delle zone. Le revisioni precedenti restano nello storico.

La scelta viaggia nei normali pacchetti firmati e nei backup societari; non è una preferenza del solo browser. Admin dati può modificarla, il visualizzatore può leggerla. Aggiornare le app sui dispositivi coinvolti per poter usare e modificare questa nuova impostazione del profilo. Non cambia il formato dei pacchetti di sincronizzazione.
