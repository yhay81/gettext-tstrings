---
description: "Traduci messaggi t-string completi tramite gettext e Babel, tenendo la formattazione fuori dal catalogo."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Scrivi la frase una volta sola.<br>Traducila per intero.

Integrazione sicura di gettext e Babel per le t-string di Python 3.14+ — il
valore resta al suo posto e il catalogo vede il messaggio per intero:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Inizia il tutorial :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Perché le t-string](comparison.md){ .md-button }

Questo sito mette in pratica ciò che documenta: ogni edizione linguistica —
navigazione, etichette e il report di build con le forme plurali — è generata
dai cataloghi PO da
[`gettext-tstrings` stessa](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Il catalogo riceve la frase completa `Hello {name}`. Una traduzione può
riordinare o ripetere `{name}`; non può eliminarlo, inventarne uno nuovo o
aggiungere formattazione propria — questa libreria lo verifica, e un catalogo
danneggiato ripiega sul testo sorgente invece di andare in crash.

!!! note "Nuovo a gettext? L'intero flusso di lavoro in quattro frasi"

    **gettext** è il modo standard in cui il software viene tradotto, in
    Python e ben oltre. Il tuo codice marca le stringhe traducibili; un
    *estrattore* le raccoglie in un file template (`.pot`); un traduttore — di
    solito non un programmatore — compila un file di catalogo (`.po`) per
    lingua, che viene compilato in un `.mo` binario caricato dall'applicazione
    a runtime. Il nome convenzionale della funzione di traduzione è `_`, così
    `_(t"Hello {name}")` si legge come "traduci questa frase". Il
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

## La scelta che compie { #the-choice-it-makes }

- Tradurre messaggi completi, mai frammenti di frase.
- Accettare soltanto nomi di variabile semplici come `{name}`.
- Tenere `!r` e `:.2f` sotto il controllo dell'applicazione, fuori dal
  catalogo.
- Lasciare che i traduttori riordinino e ripetano i segnaposto noti — ma
  senza accedere ad attributi e senza aggiungere comportamenti di
  formattazione.
- Riutilizzare i normali file POT, PO e MO, e gli strumenti che già li leggono.

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

Qui arrivano tre tipi di lettori: chi traduce il suo primo programma, chi
integra la traduzione in un progetto reale e chi vuole sapere esattamente
perché il meccanismo ha questa forma. Ognuno ha il suo percorso.

**Impararla** — nessuna esperienza con gettext richiesta:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — inizia da qui: da una directory vuota a una
  traduzione giapponese funzionante in cinque passi, ogni comando mostrato con
  il suo output.
- **[Perché le t-string](comparison.md)** — lo stesso messaggio scritto in
  quattro modi, e che cosa `%(name)s`, `.format()` e le `$`-string consegnano
  ciascuno al catalogo.
- **[Contesto](background.md)** — perché questa libreria esiste: trent'anni di
  gettext, due PEP e la discussione sulla stdlib chiusa senza una risposta.

</div>

**Usarla sul serio** — i riferimenti di lavoro:

<div class="grid cards" markdown>

- **[Guida](guide.md)** — l'API a runtime: plurali, lingue per richiesta,
  stringhe differite e che cosa succede quando un catalogo è sbagliato.
- **[Estrazione](extraction.md)** — il riferimento per `pybabel`:
  configurazione, nomi di funzione personalizzati e come gli strumenti
  esistenti validano questi cataloghi gratis.
- **[In produzione](workflow.md)** — il ciclo come lo conduce un team: il
  ciclo di aggiornamento, le voci fuzzy, i controlli in CI, le piattaforme di
  traduzione e le lingue per richiesta in un'applicazione web.
- **[API](api.md)** — tutto ciò che il pacchetto esporta, in una sola pagina.

</div>

**Capirla** — dai principi all'implementazione:

<div class="grid cards" markdown>

- **[Come funziona](internals.md)** — dall'oggetto template della PEP 750 alla
  stringa finale, e le cache che rendono economico il controllo.
- **[Specifica](spec.md)** — la convenzione t-string ↔ msgid come contratto
  stabile e versionato, con una suite di conformità leggibile dalle macchine.

</div>

## Stato { #status }

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
