---
description: "Che cosa rompe davvero la traduzione di un piccolo sito in trentacinque lingue, quali di quei problemi la libreria può intercettare per te e quali no."
---

# Insidie

Questo sito è tradotto in trentacinque lingue, e ognuna di esse è stata
prodotta eseguendo il ciclo che questa documentazione insegna. Per gli
standard del settore è un corpus piccolo, ed è bastato comunque a incappare
nella maggior parte delle trappole che rendono l'i18n più difficile di quanto
sembri.

Ogni sezione qui sotto è qualcosa che è andato davvero storto qui, come si
presentava all'epoca e dove passa il confine tra ciò che la libreria controlla
per te e ciò che resta un tuo giudizio.

## Rinominare una variabile fa ritradurre una frase { #renaming-a-variable-retranslates-a-sentence }

Il msgid è la chiave del catalogo, e un nome interpolato sta *dentro* di essa.
Spostare una costante a livello di modulo e scriverla in maiuscolo come chiede
lo stile di Python — da `author` ad `AUTHOR` — ha trasformato
`Copyright © 2026 {author} · MIT License` in un messaggio che nessun catalogo
aveva mai visto. Ogni traduzione di quella riga sarebbe ripassata per il ciclo
delle voci fuzzy, in ogni lingua, per una rinomina che non cambiava nulla di
visibile a un lettore.

La libreria non ti fermerà: entrambe le grafie sono nomi di segnaposto validi.
Quello che fa è rendere il nome *degno* di essere protetto — un'interpolazione
deve essere un [nome semplice](internals.md#from-template-to-msgid), così ciò
che sta nella chiave del catalogo è una parola che un traduttore può leggere,
non un'espressione.

Il caso speculare è sicuro per costruzione. Le conversioni e le specifiche di
formato non fanno parte del msgid, quindi stringere `{amount:,.2f}` in
`{amount:,.0f}` non cambia nessuna chiave e non invalida nessuna traduzione da
nessuna parte.

## `nplurals=2` non significa due stringhe diverse { #nplurals-2-does-not-mean-two-different-strings }

Turco, ungherese, persiano e bengalese dichiarano tutti due forme plurali, e
in tutte e quattro le due forme di un messaggio con conteggio sono
legittimamente la *stessa stringa* — il sostantivo resta al singolare dopo un
numerale, quindi `{n} sayfa` va bene per una pagina come per dieci. Un
revisore che "corregge" la duplicazione rompe la traduzione.

L'errore opposto è altrettanto facile. La terza forma del lettone esiste per
**il solo zero**; la seconda dello sloveno è un **duale**, per esattamente
due; l'ultima forma del rumeno richiede la parola `de` che le prime due non
devono avere. Riempire quelle caselle con un singolare e un plurale produce un
catalogo sbagliato solo per i conteggi che nessuno prova.

Peggio, l'*ordine* delle caselle non è semantico. Il gallese indicizza le sue
cinque forme in modo che `msgstr[0]` sia il caso generale e `msgstr[1]` il
singolare. Riempirle nella sequenza ovvia mette il singolare proprio dove lo
troverà ogni messaggio senza conteggio.

La libreria non si assume nulla di tutto questo, ed è proprio il punto: la
regola dei plurali della lingua di destinazione vive nell'intestazione del suo
catalogo, e la [regola di unione/intersezione](spec.md) permette a una
traduzione di avere più forme, o meno, della sorgente. Ciò che controlla è
l'unica cosa che può controllare senza conoscere la lingua — che ogni forma
mantenga i segnaposto che le servono.

## Due forme possono essere identiche per un motivo { #two-forms-can-be-identical-for-a-reason }

L'irlandese ha cinque forme plurali, e nel report di build di questo sito
diverse di esse si scrivono allo stesso modo. Non è una svista da
copia-incolla: *leathanach* inizia per `l`, e nessuna delle due mutazioni
iniziali che i numerali irlandesi innescano si scrive su `l`. Le forme fanno
comunque un lavoro reale — il tema alterna tra *leathanach* e *leathanaigh*, e
i conteggi sopra il dieci tornano al singolare — ma nessun sostantivo che
significhi "pagina" mostrerebbe il contrasto.

Qualunque controllo che segnali come sospette le forme duplicate segnalerà un
irlandese corretto. Una persona che conosce la lingua è l'unico revisore
possibile per questo.

## Un messaggio può concordare con un solo conteggio { #a-message-can-only-agree-with-one-count }

Il report di build di questo sito dice quante pagine sono state renderizzate e
quanto tempo ci è voluto. Scriverlo come
"Rendered {n} pages in {seconds} seconds" sembra innocuo e non è traducibile:
gettext seleziona una forma a partire da un conteggio, e quel conteggio è `n`.
La parola *seconds* dovrebbe
concordare con un numero che il meccanismo dei plurali non vede mai.

La soluzione è rendere la seconda quantità un simbolo di unità invece di una
parola, e i simboli di unità sono a loro volta localizzati: i cataloghi di
questo sito portano `s`, `с`, `ث`, `שנ׳` e `mp`, e la tipografia francese,
spagnola e svedese vuole uno spazio prima del simbolo dove l'inglese non lo
mette. Niente di tutto ciò riguarda la libreria — ma accorgersi che un
messaggio ha bisogno di *due* concordanze sì, e l'unico strumento per farlo è
scrivere il messaggio in modo diverso.

## Modificare una frase inglese modifica la grammatica altrui { #editing-an-english-sentence-edits-foreign-grammar }

La home page diceva "all ten language editions". Togliere il numero — una
modifica inglese di una sola parola, fatta perché il numero continuava a
diventare obsoleto — ha reso singolare un soggetto plurale. Spagnolo,
italiano, portoghese, russo, ucraino, greco, olandese ed ebraico hanno tutti
dovuto riaccordare il verbo; in diversi casi è servito cambiare anche il
participio.

Una modifica alla sorgente che in inglese sembra banale non è banale a valle.
Marcarla come fuzzy, che è quello che fa `pybabel update`, è il meccanismo che
dà a ogni traduttore la possibilità di accorgersene.

## Le differenze invisibili sopravvivono a ogni copia-incolla { #invisible-differences-survive-every-copy-paste }

La guida cita un messaggio diagnostico che contiene `(nаme)` — un escape
deliberato, perché il carattere che nomina è una `а` cirillica che nessun
lettore riesce a distinguere da quella latina. I traduttori di questo sito
hanno convertito quell'escape nel carattere vero e proprio **cinque volte
distinte**, in cinque lingue diverse, ogni volta producendo una pagina che
sembrava corretta ed era sbagliata.

Questa la libreria la intercetta davvero, ed è il motivo per cui i messaggi
diagnostici hanno la forma che hanno: un segnaposto le cui lettere mescolano
sistemi di scrittura viene
[segnalato due volte](internals.md#diagnostics-are-part-of-the-design), una
volta in forma leggibile e una con escape, perché la forma con escape è
l'unica grafia che le distingue. Uno spazio unificatore dentro le graffe viene
stampato per punto di codice per lo stesso motivo. Il checker dei cataloghi
rifiuta il messaggio prima che possa essere distribuito.

## Non vuoto non vuol dire tradotto { #non-empty-is-not-translated }

Un catalogo impalcato copiando i suoi msgid dentro i msgstr supera ogni
controllo ingenuo: niente è vuoto, niente è fuzzy, l'insieme dei messaggi
corrisponde esattamente. Un'edizione di questo sito è stata pubblicata così
per diverse ore. Lo stesso vale per otto pagine di un'altra edizione che erano
copie byte per byte della sorgente inglese — cosa che supera un controllo che
confronta i blocchi di codice tra le due, perché sono lo stesso file.

Nessuno dei due è qualcosa che una libreria di traduzione possa vedere.
Entrambi sono facili da testare una volta che sai di doverlo fare: confronta
con la sorgente e pretendi una differenza.

## Il catalogo non è l'unica cosa tradotta { #the-catalog-is-not-the-only-translated-thing }

Due fallimenti qui non avevano nulla a che fare con gettext.

Tradurre un titolo cambia l'ancora generata da esso, quindi ogni collegamento
da un'altra pagina verso quella sezione si rompe — in silenzio, e solo in
quella lingua. Questo sito fissa l'ancora inglese su ogni titolo, e un test
ricava l'elenco atteso dalla pagina inglese.

E il generatore del sito distribuisce le traduzioni dell'interfaccia per
sessantotto lingue, tra cui non ci sono lo swahili e l'irlandese. Senza una di
esse la build non ripiega sull'inglese; l'include del template fallisce e
l'edizione non si può costruire affatto. Due file di questo stesso repository
esistono per colmare quella lacuna.

## Anche i tuoi strumenti hanno bug { #your-tools-have-bugs-too }

Il passo di CI che questa documentazione consiglia per intercettare i cataloghi
obsoleti, `pybabel update --check`, non può svolgere quel compito per nessun
progetto che usi `pgettext` o `npgettext` — segnala come non aggiornato ogni
catalogo che contenga un `msgctxt`, a ogni esecuzione, per via di un bug nel
modo in cui il confronto cerca i messaggi. È stato scoperto qui provando a
usarlo, segnalato a monte ed è
[descritto per intero, con la soluzione alternativa](workflow.md#what-ci-gates).

La lezione generale è quella scomoda: una barriera sempre rossa è peggio di
nessuna barriera, perché una squadra la disattiva. Verifica che il tuo
controllo di CI possa davvero passare, prima di fidarti che fallisca.

## A che cosa serve la libreria, in una riga { #what-the-library-is-for-in-one-line }

La maggior parte di questa pagina è giudizio che nessuno strumento può
prendere in carico. Ciò che uno strumento *può* fare è garantire che una
traduzione non possa cambiare la struttura della frase che traduce — non possa
perdere un valore, inventarne uno, riformattarne uno o mettere le mani nei
tuoi oggetti — e dirlo in una frase su cui la persona che deve rimediare può
agire. È tutto ciò che questa libreria promette, e il resto di questo sito è
come lo mantiene.
