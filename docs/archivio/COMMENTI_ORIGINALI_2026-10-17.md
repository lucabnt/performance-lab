# Commenti originali del 17 ottobre 2026

> Documento storico: conserva decisioni e osservazioni dell’epoca. Per stato e priorità attuali consultare [indice](../README.md), [requisiti](../REQUISITI_E_TODO.md) e [roadmap](../PROSSIMI_PASSI.md).

Nota editoriale 0.4.1: per richiesta dell’utente il nome storico del prodotto è stato normalizzato in **Fuorigiri** anche nelle citazioni sottostanti; per questo il testo non è più una trascrizione letterale del nome originario. Il resto dei commenti conserva la funzione di fonte storica, non di requisito ancora da decidere.


Trascrizione della sezione To-Do, conservata per tracciabilità. La versione operativa riscritta è in [REQUISITI_E_TODO.md](../REQUISITI_E_TODO.md).

## To-Do 
- per tutte le to-do, se già presenti e completamente implementate, fallo presente
- schema colori: colori di Progetto Ciclismo, mantenendo lo stesso apparenza piacevole con colori poco impattanti
- Logo progetto ciclismo in app (nella parte bassa, non invasiva) e sito web https://www.asdprogettociclismorodengosaiano.it/ e mio nome: Luca Bontempi e sito web https://lucabontempi.com/, allegato
- aggragazioni interno dei gruppi e per anno e per gruppo per anno > calcolo aggragati storici, vedi allegati
- pagina atleta: grafico map alternativo con tasto a grafico ftp assoluta e w/kg, grafico atronponometria con peso e altezza
- multilingua: italiano e inglese
- possibilità import storico e antroponometria atleti con .csv
- definizione protocollo, possibilità di taggare riscaldamento e riconoscimento automatico degli step, definzione codice del protocollo (eg. AER-RULLO-ESO) oltre nome figurativo
- possibilità di archiviare atleta non più attivo o di eliminarlo. Archivio: viene considerato per storico, eliminato non viene più considerato nello storico
- possibilità di archiviare o eliminare protocolli
- possibilità di creazione e edit del protollo direttamente nell'interfaccia e di export dell'erg file, con versioning
- possibilità di ordinare tabelle per ogni colonna
- gruppo dovrebbe avere gli anni al di sotto, in modo da avere un solo gruppo allievi con sottogruppi per anno
- possibilità di modificare il profilo atleta direttamente in interfaccia, possibilità di input antroponometria non solo con import csv ma anche in interfaccia
- nell'importare file fit o csv del test, deve chiedere dati non misurati direttamente nel file: eg. chiedere mmol se misurate, in alternativa chiedere che coefficiente applicare per calcolare la soglia, cosi come chiedere frequenze a riposo dopo tot sec, antroponomentria aggiornata > fornire default ultima misurazione. Input manuali devono poter essere modificabili anche successivamente
- possibilità export storico atleta e storico categoria o anno categoria in md o pdf
- possibilità di confronto tra i gruppi, per anno o storico
- calcolo statistiche sulla crescita, vedi allegato
- possibilità di indirizzi file system diversi per società diverse, così che società diverse possano essere condivise con persone diverse
- gestione utenti: admin che può modificare, visualizzatore che può solo visualizzare ma senza modificare
- richiesta di fc a riposo dopo tempo standard (60, 90, 120) con possibilità di registrarne di ulteriori custom nell'import di un test fit o csv
- RPE da 1 a 10 tra input manuali import test
- se nessuno storico dei dati manuali import avere medio default per altezza, peso etc
- creazione atleta, chiedi data di nascita non solo anno, ma non bloccante
- nome soluzione Fuorigiri PERFORMANCE LAB: performance lab va bene, cerchiamo un nome simpatico legato alla cultura ciclistica italiana al posto di Fuorigiri
- nella parte bassa: Fuorigiri Strumenti aperti per osservare la progressione > Strumenti aperti a supporto del ciclismo giovanile
- verificare quali sono i principali software concorrenti, open o closed e elencare le principali funzionalità che potrebbero essere implementate
- report del test dovrebbe riportare anche zone per frequenza e per watt, da definire in modo custom in termini di percentuale rispetto a FC max o FC soglia e MAP o watt soglia all'import del test, vedi allegato per provare a definire dei default
- input manuali sul test dovrebbero essere modificabili anche dopo import, uno potrebbe non sapere prima di vedere il grafico il momento di fine dello sforzo per esempio

