---
description: "Traduci messaggi t-string completi tramite gettext e Babel, tenendo i valori e la formattazione fuori dal catalogo."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Traduci messaggi completi<br>con le t-string di Python

`gettext-tstrings` collega le t-string di Python 3.14+ ai normali cataloghi
gettext e agli strumenti di Babel. Valori e formattazione restano nel codice
applicativo; i traduttori lavorano con messaggi completi e semplici
segnaposto `{name}`:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Il catalogo contiene `Hello {name}`. Una traduzione può spostare o ripetere
`{name}`. Se lo elimina, lo rinomina o ne cambia la formattazione, la
validazione del catalogo segnala l'errore. Se una voce non valida arriva
comunque in produzione, la libreria registra un avviso e rende il messaggio
sorgente invece di andare in crash.

[Inizia il tutorial di cinque minuti :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Confronta le alternative](comparison.md){ .md-button }

Alpha · Python 3.14+ · cataloghi PO/MO standard · nessuna dipendenza a runtime di terze parti
{ .home-facts }

Questo sito mette in pratica ciò che documenta: ogni edizione linguistica —
navigazione, etichette e il report di build con le forme plurali — è generata
dai cataloghi PO da
[`gettext-tstrings` stessa](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Fa per te? { #is-this-for-you }

**Va bene già oggi se** la tua applicazione gira su Python 3.14 o più recente;
usi già gettext e Babel, oppure vuoi adottare il loro flusso di lavoro PO/MO;
e vuoi la sintassi delle t-string con segnaposto nominati che vengono
verificati prima di essere resi.

**Non fa ancora per te se** ti serve Python 3.13 o precedente; ti serve
un'API Python stabile — questa è una alpha, e la [specifica](spec.md) ne è la
parte che si è assestata; oppure quasi tutto il tuo testo traducibile vive in
un linguaggio di template anziché nel sorgente Python.

Hai già dei cataloghi? Continuano a funzionare.
`_("Hello {name}").format(name=name)` e `tr(t"Hello {name}")` producono lo
stesso msgid, quindi le traduzioni esistenti sopravvivono al cambio —
[Migrazione](migration.md) percorre l'intero passaggio.

## Che cosa può dire il catalogo { #what-the-catalog-may-say }

**Una traduzione non può cambiare la struttura del messaggio che traduce.**
Questa è tutta la promessa, e il resto di questo sito ne discende. Una
traduzione può riordinare o ripetere `{name}`, e può riscrivere ogni altra
parola attorno a esso. Non può eliminare il segnaposto, inventarne uno nuovo,
passarci attraverso per arrivare ai tuoi oggetti o aggiungere formattazione
propria.

La libreria lo verifica all'ingresso — quando i cataloghi vengono compilati —
e di nuovo al momento del rendering, che è la differenza tra un errore trovato
in revisione e un errore trovato da un utente.

!!! note "Nuovo a gettext? L'intero flusso di lavoro in quattro frasi"

    **gettext** è il modo standard in cui il software viene tradotto, in
    Python e ben oltre. Il tuo codice marca i messaggi traducibili; un
    *estrattore* li raccoglie in un file template (`.pot`); un traduttore — di
    solito non un programmatore — compila un file di catalogo (`.po`) per
    lingua, che viene compilato in un `.mo` binario caricato dall'applicazione
    a runtime. Il nome convenzionale della funzione di traduzione è `_`, così
    `_(t"Hello {name}")` si legge come "traduci questo messaggio". Il
    **[tutorial](tutorial.md)** percorre l'intero cammino — marcare,
    estrarre, tradurre, compilare, eseguire — in circa cinque minuti.

## Il problema che risolve { #the-problem-it-solves }

Una f-string è già interpolata prima che una libreria possa vederla —
`f"Hello {name}"` è ormai diventata `"Hello Ada"`, e tradurre i frammenti
attorno a un valore rompe la grammatica della maggior parte delle lingue. Una
t-string ([PEP 750]) mantiene separati il testo statico, i valori valutati, le
espressioni sorgente, le conversioni e le specifiche di formato — che è
esattamente la separazione di cui un catalogo di messaggi ha bisogno.
[Che cosa cambia](comparison.md), rispetto a `%(name)s`, `.format()` e alle
`$`-string.

Nulla in gettext o Babel dice però come una t-string diventi un messaggio.
Questa libreria compie quella scelta, la mette per iscritto in una
[specifica versionata](spec.md) e distribuisce la
[suite di conformità](spec.md#conformance) per verificarla.

## Le regole di progetto { #the-design-rules }

- Tradurre messaggi completi, mai frammenti di frase.
- Accettare soltanto nomi di variabile semplici come `{name}`.
- Tenere `!r` e `:.2f` sotto il controllo dell'applicazione, fuori dal
  catalogo.
- Permettere alle traduzioni di riordinare e ripetere i segnaposto noti,
  impedendo loro al tempo stesso di arrivare agli attributi o di aggiungere
  formattazione.
- Riutilizzare i normali file POT, PO e MO, e gli strumenti che già li leggono.

E l'elenco corrispondente di ciò che lascia deliberatamente stare: non
localizza numeri, valute o date — [formattali prima](guide.md#locale-aware-values),
con Babel; non fa l'escaping dell'output reso per l'HTML, una shell o un
terminale; e non sa giudicare se una traduzione sia *corretta*, ma solo se i
suoi segnaposto sono intatti.

## Installazione { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 o più recente. **Il rendering non ha dipendenze** — usa il modulo
`gettext` della libreria standard e nient'altro.

L'estrazione e la validazione dei cataloghi passano per [Babel]: installa
quell'extra ovunque giri `pybabel`, di solito un ambiente di sviluppo o CI e
non un'immagine di produzione:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Dove andare adesso { #where-to-go-next }

**Inizia da qui** — nessuna esperienza con gettext richiesta:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — da una directory vuota a una traduzione
  giapponese funzionante in cinque passi, ogni comando mostrato con il suo
  output.
- **[Perché le t-string](comparison.md)** — lo stesso messaggio scritto in
  quattro modi, e che cosa `%(name)s`, `.format()` e le `$`-string consegnano
  ciascuno al catalogo.

</div>

**Usala** — i riferimenti di lavoro:

<div class="grid cards" markdown>

- **[Guida](guide.md)** — l'API a runtime: quale entry point usare, plurali,
  lingue per richiesta, stringhe differite e che cosa succede quando un
  catalogo è sbagliato.
- **[Estrazione](extraction.md)** — il riferimento per `pybabel`:
  configurazione, nomi di funzione personalizzati e come gli strumenti
  esistenti validano questi cataloghi gratis.
- **[In produzione](workflow.md)** — il ciclo come lo conduce un team: il
  ciclo di aggiornamento, le voci fuzzy, i controlli in CI, le piattaforme di
  traduzione e la distribuzione.
- **[Migrazione](migration.md)** — adottarla in un progetto che ha già
  cataloghi, un punto di chiamata alla volta.
- **[Per i traduttori](translators.md)** — una pagina sola da consegnare a chi
  modifica i file `.po`.

</div>

**Capiscila** — dalla storia all'implementazione:

<div class="grid cards" markdown>

- **[Contesto](background.md)** — perché questa libreria esiste: trent'anni di
  gettext, due PEP e la discussione sulla stdlib chiusa senza una risposta.
- **[Insidie](pitfalls.md)** — che cosa ha rotto davvero la traduzione di
  questo sito in trentacinque lingue, e quale metà uno strumento può
  intercettare.
- **[Come funziona](internals.md)** — dall'oggetto template della PEP 750 alla
  stringa finale, e le cache che rendono economico il controllo.

</div>

**Riferimento** — i contratti:

<div class="grid cards" markdown>

- **[API](api.md)** — tutto ciò che il pacchetto esporta, in una sola pagina.
- **[Specifica](spec.md)** — la convenzione t-string ↔ msgid come contratto
  stabile e versionato, con una suite di conformità leggibile dalle macchine.

</div>

## Stato { #status }

| | |
| --- | --- |
| Versione del pacchetto | 0.1.0a8 |
| Stabilità dell'API | alpha — l'API Python può ancora cambiare |
| [Specifica](spec.md) | v1, con una [suite di conformità](spec.md#conformance) |
| Python | 3.14 e successive; testata su 3.14, 3.14t (free-threaded) e 3.15 |
| Babel | 2.18 o successiva, e solo dove gira `pybabel` |
| Dipendenze a runtime | nessuna — il `gettext` della libreria standard |
| Formato dei cataloghi | POT, PO e MO ordinari |
| Modifiche | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Una alpha. Il contratto è piccolo di proposito e la [specifica](spec.md) ne è
la parte stabile; l'API Python può ancora muoversi. Prima di una release
stabile servono fixture per più lingue, un tracciamento costante delle
prestazioni, revisioni dell'API da parte di chi usa gettext e Babel sul serio,
e test di compatibilità su ogni versione supportata di Python e Babel.

[Issue e pull request](https://github.com/yhay81/gettext-tstrings/issues) sono
benvenute — una alpha è esattamente il momento in cui vale ancora la pena
discutere dell'interfaccia.

## Unisciti alla comunità { #join-the-community }

- Scegli una
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  per un contributo delimitato.
- Fai domande d'uso nelle
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Porta flussi gettext di produzione e idee sull'API nelle
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Leggi la
  [guida alla contribuzione](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  prima di aprire una pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
