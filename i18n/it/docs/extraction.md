---
description: "Estrarre i messaggi t-string con pybabel, e come msgfmt e il checker Babel incluso validano i cataloghi."
---

# Estrazione

L'estrazione è il passo che raccoglie ogni messaggio marcato dal tuo codice
sorgente in un template `.pot` per i traduttori — il passo 3 del ciclo del
[tutorial](tutorial.md). Questa pagina è il riferimento per quel passo:
configurazione, nomi di funzione personalizzati, modalità strict per la CI e
i controlli che proteggono i tuoi cataloghi in seguito.

L'estrazione richiede l'extra `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Il flusso di lavoro { #the-workflow }

Crea `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Poi usa i normali comandi Babel:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` si esegue una volta per lingua; da lì in poi, `pybabel update` fonde
ogni nuovo template nei cataloghi esistenti. Quel ciclo ricorrente — e che
cosa significano le sue voci `fuzzy` per una release — è percorso in
[In produzione](workflow.md#the-cycle-after-the-first-translation).

L'estrattore `gettext_tstrings` gestisce anche le normali chiamate `_()`,
`gettext()` e `ngettext()`, così una sola mappatura copre una base di codice
mista. Riconosce `_()`, i quattro nomi gettext standard, gli alias `tr()` /
`ntr()` e le funzioni differite `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "Abilita i commenti per i traduttori con `-c`"

    `pybabel extract` raccoglie i commenti per i traduttori solo quando passi
    `-c "Translators:"`, esattamente come per le normali chiamate gettext.
    Ometterlo non impedisce l'estrazione — semplicemente i commenti non
    arrivano mai nel catalogo, dove sono
    [la leva di qualità più economica](workflow.md#working-with-translators-and-platforms)
    di tutto il flusso di lavoro.

## Registrare i tuoi nomi di funzione { #registering-your-own-function-names }

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

Un file ini fornisce una stringa, una mappatura TOML fornisce una lista, e
dentro una stringa i nomi sono separati da spazi o da virgole. Tutte e
quattro le scritture funzionano.

Le opzioni sono `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` e `npgettext_functions`.

!!! danger "`-k` non raggiunge una t-string"

    Un helper personalizzato come `mytr(t"…")` deve essere nominato in una
    delle opzioni qui sopra. Il meccanismo `--keyword` di Babel non sa
    leggere un letterale t-string, quindi `pybabel extract -k mytr` non trova
    nulla e non dice nulla — i messaggi sono semplicemente assenti dal POT.
    `-k` continua a funzionare per le normali chiamate gettext estratte
    accanto.

    È supportato solo l'ordine standard degli argomenti: prima il messaggio,
    contesto poi messaggio per `pgettext`, contesto poi singolare poi plurale
    per `npgettext`.

## Permissivo in locale, severo in CI { #lenient-locally-strict-in-ci }

Per impostazione predefinita un file danneggiato non interrompe l'esecuzione:

- Una t-string che l'estrattore rifiuta — accesso a un attributo,
  un'espressione, un argomento sbagliato — viene segnalata come avviso e
  saltata.
- Un file che non si lascia analizzare viene saltato allo stesso modo.
- Lo stesso vale per un file che solo `tokenize` rifiuta mentre `ast` lo
  accetta, sul quale il passaggio di Babel stesso altrimenti abortirebbe.

Il che è comodo mentre stai lavorando al codice e pericoloso quando non lo
stai facendo: un messaggio saltato è semplicemente **assente dal POT**, quindi
non viene mai tradotto e nessuno lo dice. Imposta `strict = true` nelle opzioni
della mappatura ovunque l'estrazione non sia sorvegliata da una persona:

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    encoding = utf-8
    strict = true
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    strict = true
    ```

Ognuno degli avvisi qui sopra diventa allora un fallimento duro. Considera
questa l'impostazione di produzione e quella predefinita come l'impostazione
locale.

## La tua toolchain esistente valida questi cataloghi { #your-existing-toolchain-validates-these-catalogs }

Babel marca ogni messaggio estratto con un flag standard, e quella singola
riga è ciò che attiva il controllo dei segnaposto negli strumenti che già
esegui:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Traducilo come `こんにちは {nombre}` e l'errore viene colto senza alcuna
configurazione:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate documenta lo stesso controllo come
[Python brace format][weblate-checks], e le piattaforme commerciali hanno la
loro QA sui segnaposto agganciata allo stesso flag. Il comportamento di
ciascuna piattaforma è cosa sua; i due strumenti qui sotto sono quelli
verificati in questa sede.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

In aggiunta, il pacchetto registra un **checker** Babel, così
`pybabel compile` applica le regole della specifica a ogni messaggio che
porta il commento marcatore `gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Per un messaggio plurale il puntatore nomina la forma, perché il numero di
riga che Babel riporta è quello del msgid e un blocco russo ha tre `msgstr`
sotto di esso:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` scrive comunque il `.mo`"

    L'errore qui sopra viene riportato, lo stato di uscita è `1` — e il
    catalogo danneggiato viene compilato lo stesso. Solo quello stato di
    uscita può impedire a una pipeline di distribuirlo;
    [Che cosa controlla la CI](workflow.md#what-ci-gates) mostra il passo di
    build che glielo permette.

I due controlli non sono ridondanti. Il checker del pacchetto è più severo in
almeno due casi:

- Un msgid le cui uniche graffe sono escapate (`Config {{raw}} only`) non
  riceve mai il flag `python-brace-format`, quindi nessuno strumento esterno
  lo valida affatto.
- Le forme plurali sono verificate una per una. `msgfmt --check-format` legge
  proprio il file qui sopra ed esce con `0`; una forma che perde un
  segnaposto conservato dalle sue sorelle lì è accettata e qui è rifiutata.

`msgfmt` controlla solo i nomi di segnaposto che riesce ad analizzare come
Python brace format, quindi i nomi ASCII mantengono ogni strumento della
catena in grado di validare il messaggio. La libreria di per sé accetta
qualunque nome per cui `str.isidentifier()` è vero.

## Template e altri strumenti { #templates-and-other-tools }

Le t-string sono sintassi Python, quindi questa libreria copre il sorgente
Python. I linguaggi di template continuano a usare la propria i18n — il
`{% trans %}` di Jinja2, i template tag di Django — e gli estrattori Babel
per essi. Tutto alimenta lo stesso catalogo PO, così un unico flusso di
traduzione copre comunque una base di codice mista.

`pygettext` oggi non sa analizzare le t-string, ed è per questo che
l'estrazione passa per Babel. La convenzione è messa per iscritto nella
[specifica](spec.md) perché un altro estrattore, o un futuro `pygettext`,
possa prenderla di mira.
