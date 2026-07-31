---
description: "Adottare le t-string in un progetto che ha già cataloghi gettext: che cosa resta intatto, che cosa diventa fuzzy e come spostarsi un punto di chiamata alla volta."
---

# Migrazione

Se il tuo progetto usa già gettext, le domande che decidono se questa libreria
sia adottabile sono poche e precise: invalida i cataloghi che hai, può
convivere con il codice che non sei pronto a cambiare, e quanta parte dello
spostamento deve avvenire tutta insieme. Le risposte, dalla più breve:

| Domanda | Risposta |
| --- | --- |
| I file `.po` e `.mo` esistenti funzionano ancora? | Sì. Stessi file, stessi strumenti. |
| Chiamate vecchie e nuove possono stare in un solo file? | Sì, e una sola mappatura dell'estrattore le copre entrambe. |
| Il msgid cambia? | Non partendo da `.format()`. Sì partendo dal `%`-format. |
| Tutto il progetto deve spostarsi in una volta? | No. Un solo punto di chiamata è una modifica valida. |
| E Jinja, i template Django, JavaScript? | Intoccati, stessi cataloghi. |

Il resto di questa pagina è il dettaglio dietro ciascuna di quelle risposte.

## Da `.format()`: il msgid non cambia { #from-format-the-msgid-does-not-change }

È il caso in cui la migrazione non costa quasi nulla. Un messaggio
`str.format` e un messaggio t-string derivano la *stessa* chiave di catalogo,
perché la chiave è comunque il testo con dentro `{name}`:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Quindi la traduzione esistente resta attaccata. Partendo da un catalogo che
contiene

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

cambia la chiamata, riestrai e aggiorna:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

La voce che torna indietro differisce in due righe di metadati e in nient'altro
— un commento marcatore che la identifica come messaggio t-string e un numero
di riga sorgente:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Nessun flag `fuzzy`, nessuna ritraduzione, in nessuna lingua. Il messaggio
viene reso subito:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` segnalerà i cataloghi come non aggiornati"

    Quel commento marcatore e i numeri di riga spostati bastano perché
    `pybabel update --check` dica che un catalogo va rigenerato, dato che
    confronta l'intera voce e non solo la traduzione. Esegui il vero
    `pybabel update` nello stesso commit della modifica al codice, e committa i
    cataloghi insieme a essa — la stessa abitudine che il
    [controllo in CI](workflow.md#what-ci-gates) già richiede.

## Dal `%`-format: il msgid cambia, quindi le traduzioni diventano fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

La sintassi printf vive *dentro* il messaggio, quindi sostituirla riscrive la
chiave del catalogo. Non c'è modo di evitarlo, ed è il costo onesto di
lasciarsi alle spalle `%(name)s`:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` riconosce nel nuovo messaggio uno stretto parente di quello
rimosso e porta avanti la vecchia traduzione, marcandola fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Tre cose da sapere su quello stato:

- **Niente si rompe a runtime.** Le voci fuzzy sono escluse dal `.mo`
  compilato, quindi l'applicazione rende il messaggio sorgente finché una
  persona non conferma la coppia —
  [lo stesso degrado](workflow.md#the-cycle-after-the-first-translation) che
  attraversa qualunque messaggio riformulato.
- **`pybabel compile` le segnala una per una**, perché il `%(name)s` portato
  avanti non è un segnaposto brace valido, ed esce con codice diverso da zero.
  Quell'elenco è la tua lista di lavoro, non un falso allarme; le voci che
  contiene hanno davvero bisogno di essere modificate.
- **Il vecchio flag `python-format` viaggia con loro** e va cancellato insieme
  al flag `fuzzy`, altrimenti `msgfmt --check-format` continuerà ad applicare
  le regole di printf a un messaggio in formato brace.

Per i segnaposto printf con nome la modifica è meccanica — `%(name)s` diventa
`{name}` e nient'altro si muove — quindi un catalogo grande è una passata
scriptata seguita da una revisione del traduttore, e non una ritraduzione. Il
`%s` posizionale non è meccanico: non ha nessun nome da portare avanti, e
sceglierne uno è il punto stesso della modifica.

Per questo l'ordine pratico è migrare i messaggi in `%`-format con
deliberazione — un modulo, una release, una lingua alla volta — invece che in
una sola passata che fa diventare rossi tutti i cataloghi insieme.

## Chiamate vecchie e nuove convivono { #old-and-new-calls-coexist }

L'estrattore che legge le t-string legge anche le normali chiamate gettext,
quindi una sola mappatura copre un file a metà migrazione:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

Entrambi i messaggi finiscono nello stesso template, e solo quello t-string
porta il commento marcatore che attiva i controlli aggiuntivi di questa
libreria:

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Riconosce `_()`, i quattro nomi gettext standard, gli alias `tr()` / `ntr()` e
le funzioni differite `lazy_gettext()` / `lazy_pgettext()`. Un helper tuo deve
essere [nominato nella mappatura](extraction.md#registering-your-own-function-names).

A runtime i due stili sono altrettanto indipendenti: `gettext.translation()`
restituisce un solo oggetto translations, e sia `_` sia gli entry point di
questa libreria leggono da lì.

## Che cosa non si sposta { #what-does-not-move }

- **I linguaggi di template.** Il `{% trans %}` di Jinja2, i tag di template
  di Django e i loro estrattori Babel continuano a funzionare immutati e
  continuano ad alimentare gli stessi cataloghi PO. Le t-string sono sintassi
  Python; valgono per il sorgente Python.
- **I tuoi file di catalogo.** Nessun cambio di formato, nessun file nuovo,
  nessun passo di conversione.
- **La tua piattaforma di traduzione.** L'interscambio in `.po` è identico, e
  il flag `python-brace-format` che porta un messaggio t-string è lo stesso
  flag che porta un messaggio `.format()` — quindi la QA sui segnaposto
  continua a funzionare.
- **Il codice non Python.** Un catalogo JavaScript o C nello stesso progetto
  non ne risente.

## Una checklist di migrazione { #a-migration-checklist }

1. Aggiungi l'extra `babel` dove gira `pybabel`, e cambia la mappatura
   `python` in `babel.cfg` con il metodo `gettext_tstrings` — una sola
   mappatura copre allora entrambi gli stili, e `-k` continua a funzionare per
   le chiamate ordinarie.
2. Converti per primi i punti di chiamata con `.format()`. Riestrai, esegui
   `pybabel update` e committa i cataloghi insieme al codice; non aspettarti
   nessuna voce fuzzy.
3. Converti i punti di chiamata in `%`-format a lotti che riesci a far
   revisionare, riscrivendo i segnaposto portati avanti e cancellando i flag
   `fuzzy` e `python-format`.
4. Sistema ciò che la restrizione rifiuta: un'interpolazione deve essere un
   nome semplice, quindi `t"Hello {user.name}"` diventa prima una variabile
   locale. È una modifica al punto di chiamata, non al catalogo.
5. Attiva `strict = true` nella mappatura dell'estrattore una volta finita la
   passata, così un messaggio che non si riesce a estrarre fa fallire
   [la build](extraction.md#lenient-locally-strict-in-ci) invece di sparire
   dal template.
6. Aggiungi il controllo a runtime da [In produzione](workflow.md#what-ci-gates):
   rendi un messaggio per ogni lingua distribuita attraverso un `Translator`
   strict.

I passi 2 e 3 sono commit ordinari. Niente in questo elenco richiede un giorno
di fermo generale.
