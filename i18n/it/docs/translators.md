---
description: "Il contratto sui segnaposto per chi modifica i file .po: che cosa puoi cambiare, che cosa devi lasciare stare e come leggere gli errori."
---

# Per i traduttori

Questa pagina è per chi modifica il catalogo, non per chi scrive il codice. È
breve di proposito, ed è pensata per essere collegata o copiata dentro le
istruzioni per i traduttori di un progetto.

Niente qui richiede di saper leggere Python. Tutto qui riguarda una cosa sola:
i pezzi di un messaggio racchiusi tra parentesi graffe.

## Che cos'è un segnaposto { #what-a-placeholder-is }

Un messaggio in un catalogo può contenere nomi tra parentesi graffe:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` è un **segnaposto**. Quando il programma mostra questo messaggio,
sostituisce `{name}` con un valore che fornisce lui — il nome di una persona,
il nome di un file, un numero. Il segnaposto non è una parola da tradurre; è
uno spazio da riempire.

La tua traduzione va nel `msgstr`, e deve conservare quello spazio:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Che cosa puoi cambiare e che cosa no { #what-you-may-change-and-what-you-may-not }

**Puoi**:

- **Spostare un segnaposto** dovunque lo voglia la grammatica della lingua di
  destinazione, anche all'inizio del messaggio.
- **Ripetere un segnaposto** se la lingua ha bisogno del valore due volte.
- **Riscrivere ogni altra parola**, punteggiatura, spaziatura e ordine della
  frase compresi.

**Non devi**:

- **Tradurre il nome dentro le graffe.** `{name}` resta `{name}`, anche in una
  lingua che non scrive nient'altro in caratteri latini.
- **Togliere le graffe**, né scrivere il nome senza di esse.
- **Sostituire le graffe ASCII `{` `}` con quelle a larghezza intera `｛`
  `｝`.** Molti metodi di input producono le forme a larghezza intera; sono
  quasi identiche a vedersi e non funzionano.
- **Aggiungere formattazione**, come `{name!r}` o `{amount:.2f}`. Come un
  valore viene mostrato si decide nel programma, non nel catalogo.
- **Inventare un segnaposto** che non è nel `msgid`.

Se un messaggio ha bisogno di un valore che l'originale non offre, è un
messaggio che deve cambiare chi sviluppa. Dillo, invece di aggirare
l'ostacolo.

## Forme plurali { #plural-forms }

Un messaggio con conteggio arriva con uno spazio `msgstr` per ogni forma
plurale della tua lingua, ed è la tua lingua a decidere quante sono: una per
il giapponese, due per il tedesco, tre per il russo, sei per l'arabo. Riempi
ogni spazio che il catalogo ti dà.

Due regole che colgono in fallo:

- **Gli spazi non sono "singolare, plurale, plurale di più".** Ogni indice
  significa quello che dice la regola di plurale della tua lingua. La terza
  forma del lettone è solo per lo zero; la seconda dello sloveno è per il due
  esatto; il gallese mette il caso generale all'indice 0 e il singolare
  all'indice 1.
- **Due spazi possono legittimamente contenere lo stesso testo.** In turco,
  ungherese, persiano e bengalese un sostantivo resta al singolare dopo un
  numerale, quindi entrambe le forme di un messaggio con conteggio sono la
  stessa stringa. È corretto, non una svista da copia e incolla.

Le regole sui segnaposto qui sopra valgono per ogni forma indipendentemente.

## Voci fuzzy { #fuzzy-entries }

Una voce marcata `fuzzy` è l'ipotesi di una macchina: chi sviluppa ha cambiato
il messaggio originale, e gli strumenti hanno accoppiato il nuovo testo con la
tua vecchia traduzione, così hai da dove partire.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Una voce fuzzy **non viene usata dal programma** — al suo posto mostra
l'originale non tradotto — finché qualcuno non ne rivede il testo e non toglie
il marcatore `fuzzy`. Quasi tutti gli editor PO hanno un pulsante apposta.

## Leggere un messaggio di errore { #reading-a-failure-message }

Gli strumenti verificano i segnaposto quando il catalogo viene compilato, e il
messaggio è scritto per te e non per chi programma. Riferire soltanto che
`{name}` manca è un vicolo cieco quando puoi vedere quei caratteri davanti a
te, quindi dove un segnaposto sembra presente ma non lo è, il messaggio dice
perché. Contro l'originale `Hello {name}`, ciascuno di questi è riportato sotto
`translation does not match the source placeholders:`

| La tua traduzione dice | La ragione che riporta |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

I caratteri che non si possono vedere ricevono un trattamento a parte. Uno
spazio unificatore dentro le graffe è qualcosa che un metodo di input produce
e nessun editor mostra, quindi il messaggio lo stampa per punto di codice
invece di nominare un carattere che non potresti mai trovare:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Un nome le cui lettere mescolano sistemi di scrittura — il caso degli
omoglifi, dove una `а` cirillica è indistinguibile da una latina — viene
mostrato due volte, una in forma leggibile e una in forma escapata, che è
l'unica forma che distingue le due:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

La stessa disambiguazione si applica quando un nome greco o cirillico scritto
interamente in un solo alfabeto entra in conflitto con un nome sorgente
ASCII, incluso il caso a una lettera `a` latina / `а` cirillica.

Se incontri uno di questi casi e la soluzione non è ovvia, la mossa sicura è
cancellare il segnaposto che hai scritto e copiare quello dal `msgid`.

## Che cosa i controlli non possono fare { #what-the-checks-cannot-do }

Gli strumenti verificano che i tuoi segnaposto siano intatti. Non sanno dire
se la traduzione sia accurata, naturale o adatta al contesto — quello resta
interamente a te.

Due cose aiutano più di qualunque controllo:

- **Leggi il commento per il traduttore.** Una riga che inizia con `#.` sopra
  il messaggio è chi sviluppa che ti dice dove compare e che cosa significa.
- **Chiedi del `msgctxt`.** Quando la stessa parola compare due volte con
  contesti diversi, è perché le due vanno tradotte in modo diverso — "Open" il
  pulsante e "Open" lo stato, per esempio.
