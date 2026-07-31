---
description: "Lo stesso messaggio traducibile scritto con %-format, .format(), le $-string di flufl.i18n e una t-string, incluso come ciascuno lega i valori e gestisce un catalogo danneggiato."
---

# Perché le t-string

Quattro modi di mettere un valore in un messaggio traducibile, confrontati
sulla stessa frase. La versione breve:

- Con il **%-format**, un traduttore che cancella una lettera diventa un
  crash in produzione.
- Con **str.format**, una traduzione può leggere gli attributi degli oggetti
  che il tuo codice passa — segreti inclusi.
- Con le **$-string** (flufl.i18n), i valori vengono presi implicitamente
  dalle variabili della funzione chiamante, e i segnaposto con il punto
  raggiungono anche gli attributi.
- Con le **t-string**, la formattazione resta nel tuo codice, le traduzioni
  vengono verificate a runtime, e un catalogo danneggiato ripiega sul testo
  sorgente invece di andare in crash.

Il resto di questa pagina è la prova, un metodo alla volta.

!!! note "Tre parti toccano ogni messaggio tradotto"

    Un **catalogo** è il file delle traduzioni — `.po` finché lo modificano
    gli esseri umani, compilato in `.mo` perché l'applicazione lo carichi (il
    [tutorial](tutorial.md) li percorre entrambi). Tre parti toccano ogni
    messaggio: lo **sviluppatore** scrive la stringa sorgente, un
    **traduttore** modifica il catalogo — spesso su una piattaforma esterna,
    lontano da qualunque code review — e l'**applicazione** rende i due
    insieme a runtime. Ogni stile di formattazione qui sotto risponde in modo
    diverso alla stessa domanda: *quanta parte del linguaggio di formato può
    controllare il catalogo?* Negli esempi, `_` è il nome convenzionale della
    funzione di traduzione, e `tr` è quello di questa libreria.

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Che cosa può andare storto: una lettera cancellata in una traduzione manda in
crash il rendering.

La stringa nel catalogo trasporta sintassi printf, inclusa una lettera di
tipo finale — la `s` di `%(name)s` — facile da trascurare e facile da
danneggiare:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Una modifica di un carattere in un editor PO diventa un traceback in
produzione. GNU `msgfmt --check-format` la intercetta, sì, ma solo per i
messaggi marcati `python-format`, e solo se il catalogo passa davvero per
msgfmt nel suo tragitto verso l'applicazione.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Elimina la lettera di tipo finale mantenendo un segnaposto con nome,
liberamente riordinabile. Ciò che può andare storto si sposta sull'altro lato
dello scambio: la traduzione acquista potere sui tuoi oggetti.

`str.format` è un piccolo linguaggio di espressioni, e chiamarlo su una
stringa significa consegnare a quella stringa il diritto di usarlo:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Ora sostituisci quelle stringhe letterali con qualunque cosa restituisca
`_()`. Se una traduzione di `Hello {name}` torna come `{conf.api_key}`,
renderla stampa la tua chiave API — è stato il catalogo, non il tuo codice, a
decidere che cosa leggere. Un catalogo non è codice, ma viaggia come dati: va
verso una piattaforma di traduzione, passa per molte mani, torna come `.po`,
viene compilato in `.mo`, a volte è vendorizzato interamente da fuori del tuo
progetto. `.format()` dà a ogni tappa di quel viaggio l'accesso agli
attributi degli oggetti che passi.

## Le `$`-string e flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

Il [`string.Template`][stdlib-template] della libreria standard fornisce il
linguaggio di interpolazione `$name`, ma non è di per sé un'API di
traduzione. [`flufl.i18n`][flufl-i18n] combina quello stile con la ricerca
nei cataloghi gettext. Nota che il valore non viene mai passato: flufl.i18n
costruisce lo spazio dei nomi di sostituzione dai globali e dai locali del
chiamante — qualunque variabile esista nel punto di chiamata è disponibile al
messaggio. Un mapping `extras` opzionale ha precedenza su entrambi. La sua
sintassi rivolta al traduttore non ha lettera di tipo finale né specifica di
formato, e i segnaposto restano liberamente riordinabili.

Una sostituzione non disponibile non solleva eccezioni. Con `name = "Ada"` e
nessun `nombre` nello spazio dei nomi del chiamante, una traduzione da
catalogo di `Hello $nombre` viene resa come `Hello $nombre`: il segnaposto
non risolto rimane visibile. Quel [comportamento documentato][documented behavior]
preserva il resto del messaggio tradotto invece di far fallire la chiamata.
Le eccezioni sollevate risolvendo un attributo o convertendo un valore
possono comunque propagarsi.

`flufl.i18n` è più capace di un semplice `string.Template` in un modo qui
rilevante. Il suo [Template personalizzato][custom Template] accetta
segnaposto con il punto come `$settings.api_key`, e il suo
[translator][translator] risolve quei percorsi contro i valori del
chiamante. Un segnaposto tradotto può nominare qualunque locale o globale
disponibile del chiamante e, con la sintassi puntata, attraversarne gli
attributi. È comodo quando un messaggio ha bisogno di un attributo, ma rende
anche il frame del chiamante parte dello spazio dei nomi di sostituzione del
catalogo. Il confronto qui sotto descrive `flufl.i18n` 6.0.0, non ogni
possibile uso di `string.Template`.

Risponde anche a una domanda che gli altri due stili di formattazione lasciano
interamente all'applicazione: *quale* lingua è quella corrente, e come
cambiarla. Un [oggetto applicazione][application object] mantiene uno stack di
lingue, `_.push(code)` e `_.pop()` lo muovono, `with _.using(code):` annida, e
una [strategia][strategy] trova il catalogo per un codice di lingua, così che
l'applicazione non maneggi mai oggetti catalogo. Un server che deve produrre
testo in più di una lingua nel corso di una sola unità di lavoro — una pagina
per chi legge, una notifica per qualcuno il cui account è impostato
diversamente — è il caso per cui questo esiste.

Lo stack vive su quell'oggetto applicazione, che l'intero processo condivide.
Due richieste sovrapposte condividono quindi un unico stack, e i blocchi che
non sono strettamente annidati *nel tempo* si passano l'un l'altro la lingua
sbagliata:

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

Questa libreria conserva la stessa capacità — i binding si annidano e si
sciolgono allo stesso modo — dentro una `ContextVar` invece che in uno stack
condiviso, così l'intreccio qui sopra si risolve per task. Gli equivalenti
sono su [Più lingue insieme](guide.md#several-languages-at-once). Ciò che non
fornisce è la ricerca dal codice di lingua al catalogo: passi un oggetto
translations, che nel caso comune è una sola chiamata a
`gettext.translation()`, e la libreria standard mette in cache il catalogo già
analizzato.

## t-string { #t-strings }

```python
tr(t"Hello {name}")
```

Il catalogo vede sempre `Hello {name}` e rimane un normale catalogo PO/MO. La
differenza è che cosa una traduzione *può dire*, e chi lo verifica.

Questa libreria valida ogni traduzione contro i segnaposto del messaggio
sorgente prima del rendering, e accetta nomi semplici e nient'altro. Contro
`t"Hello {name}"`:

| Una traduzione che contiene | viene rifiutata con |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Rifiutata non significa crash: per impostazione predefinita la libreria
registra un avviso nel log e rende il testo sorgente, così un catalogo
danneggiato non abbatte mai l'applicazione —
[lo stesso contratto che gettext stesso mantiene](guide.md#what-happens-when-a-catalog-is-wrong).

La formattazione resta dov'era scritta, nel codice:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` non raggiunge mai il catalogo, quindi nessuna traduzione può
cambiarlo, e nessun traduttore deve guardarlo.

Un'altra differenza è il tooling: le t-string sono sintassi nuova, quindi
estrarle in un `.pot` richiede al momento un estrattore che le comprenda,
come quello che questo pacchetto [fornisce per Babel](extraction.md).

## Fianco a fianco { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Il segnaposto ha un nome? | sì | sì | sì | sì |
| Un traduttore può riordinare i segnaposto? | sì | sì | sì | sì |
| Da dove vengono i valori? | un mapping esplicito | argomenti espliciti | le variabili locali e globali del chiamante, più l'`extras` opzionale | i valori catturati dentro la t-string |
| Il catalogo può cambiare come un valore è formattato? | sì | sì | no | no |
| Il catalogo può entrare negli oggetti (accesso agli attributi)? | no | sì | sì, con i nomi puntati | no |
| Una traduzione *elimina* un segnaposto — che cosa viene reso? | il valore sparisce in silenzio | il valore sparisce in silenzio | il valore sparisce in silenzio | il testo sorgente, con un avviso ([per impostazione predefinita](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Una traduzione *aggiunge* un segnaposto sconosciuto — che cosa viene reso? | un'eccezione | un'eccezione | il segnaposto resta visibile come testo | il testo sorgente, con un avviso ([per impostazione predefinita](guide.md#what-happens-when-a-catalog-is-wrong)) |
| I segnaposto sono verificati al momento del rendering? | no | no | no | sì (vedi sotto) |
| Quale flag PO inferisce Babel, perché gli strumenti esistenti validino? | `python-format` | `python-brace-format` | nessuno | `python-brace-format` |
| Usa normali cataloghi PO/MO? | sì | sì | sì | sì |
| Serve un estrattore di sorgenti dedicato? | no | no | no | sì, per ora |
| Dove vive "la lingua corrente"? | dove la mette l'applicazione | dove la mette l'applicazione | uno stack di codici di lingua sull'oggetto applicazione condiviso | una `ContextVar`, per task o per richiesta |

Sul controllo a tempo di rendering: i messaggi singolari sono verificati per
una corrispondenza esatta dei segnaposto. Anche i messaggi plurali sono
verificati, contro la [regola unione/intersezione](spec.md) che permette alle
forme plurali di una lingua di destinazione di differire da quelle della
sorgente; il controllo più severo, forma per forma, avviene alla compilazione
dei cataloghi ([Estrazione](extraction.md)).

La riga sul flag di formato riguarda la validazione consapevole dei
segnaposto, non la compatibilità dei cataloghi. `nessuno` significa che gli
strumenti gettext standard leggono e compilano comunque il messaggio, ma
`msgfmt --check-format` non ha una grammatica di segnaposto `$` da applicare.

## Che cosa costa { #what-it-costs }

Una f-string non si può usare affatto in questo modo — quando una libreria ne
vede una è già una stringa finita, quindi tradurla significa tradurre un
frammento. Le t-string ([PEP 750]) mantengono separati il testo statico e i
valori conservando una sintassi simile alle f-string e il legame esplicito
dei valori. Le `$`-string offrono già un'alternativa concisa con un modello
diverso di legame e di fallimento. `flufl.i18n` è un pacchetto maturo che
gira su Python 3.10 e successivi; `gettext-tstrings` è attualmente una alpha
e, poiché le t-string sono sintassi nuova, richiede Python 3.14 o più
recente.

L'altro costo è la restrizione stessa: un'interpolazione deve essere un nome
semplice.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

È un vincolo reale. Insieme al legame dei valori sul lato sorgente e al
controllo dei segnaposto a runtime, impedisce alle stringhe di catalogo di
valutare espressioni e mantiene significativi i nomi dei segnaposto.

Come Python sia arrivato a questo bivio — due PEP a dieci anni di distanza e
la discussione sulla stdlib chiusa senza una risposta — è raccontato con le
fonti in [Contesto](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
