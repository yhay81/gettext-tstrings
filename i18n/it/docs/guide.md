---
description: "L'API a runtime: legare un catalogo, lingue per richiesta, stringhe differite e come viene segnalata una traduzione danneggiata."
---

# Guida

Questa pagina è il riferimento a runtime: tutto ciò che il *codice
applicativo* fa con questa libreria una volta che i cataloghi esistono. Se
non hai ancora visto il ciclo completo — marcare, estrarre, tradurre,
compilare, eseguire — il [tutorial](tutorial.md) lo percorre una volta in
cinque minuti; la creazione e la validazione dei cataloghi sono coperte in
[Estrazione](extraction.md), e come un team tiene in moto il ciclo — cicli di
aggiornamento, CI, piattaforme di traduzione — è [In produzione](workflow.md).

## Legare un catalogo { #binding-a-catalog }

La forma raccomandata rispecchia l'uso a classi di gettext: lega una volta un
normale oggetto di traduzione e usa il processore chiamabile come `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

Le funzioni a livello di modulo seguono i nomi della libreria standard e la
sua convenzione di chiamata con soli argomenti posizionali:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` e `ntr` sono alias esatti di `gettext` e `ngettext`.

## Lingua per richiesta { #per-request-language }

Un framework web sceglie una lingua per ogni richiesta. Lega le traduzioni
della richiesta al contesto corrente e ogni chiamata a livello di modulo si
risolve in quella lingua, in sicurezza anche tra richieste concorrenti:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` lega senza un blocco `with`, per i framework
che gestiscono da soli il ciclo di vita della richiesta; `get_translations()`
legge il binding corrente. Un argomento esplicito `translations=` vince
sempre sul contesto, e un contesto non legato ripiega sulle funzioni gettext
installate globalmente dalla libreria standard. Esempi svolti per Flask e per
un middleware ASGI sono nella pagina
[In produzione](workflow.md#binding-a-language-at-runtime).

## Traduzione differita { #deferred-translation }

Una t-string cattura i suoi valori subito, il che è sbagliato per una stringa
definita al momento dell'import — l'etichetta di un form, il valore di un
enum, una costante di modulo — che deve essere resa in qualunque lingua sia
attiva quando viene *usata*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

Una `LazyString` si rende attraverso `str()`, `format()` e le f-string, e
risulta uguale al suo testo reso nei confronti.

!!! note "Deliberatamente non hashabile"

    Il testo di una `LazyString` dipende dalla lingua attiva, quindi un hash
    cambierebbe a ogni cambio di lingua e corromperebbe in silenzio qualunque
    set o dict la contenga. Chiama prima `str()` se ti serve una chiave.

`strict` si decide dove il messaggio viene scritto, non dove viene reso:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Una stringa differita viene resa dovunque finisca per essere usata — dentro un
template, un form, una riga di log — e quel punto raramente sa se si tratta di
un'esecuzione di test o della produzione. Passare `strict=True` alla
definizione è ciò che permette di applicare la stessa scelta
[rumorosa in CI, tollerante in produzione](#what-happens-when-a-catalog-is-wrong)
anche a una stringa che non viene resa nel punto in cui è chiamata.

Le forme plurali dipendono da un conteggio a runtime, quindi rendile subito
con `ngettext` dove il conteggio è noto.

## Più lingue insieme { #several-languages-at-once }

Una sola richiesta ha spesso bisogno di più di una lingua: una pagina resa per
chi legge che accoda anche una notifica a un account impostato su un'altra, o
un digest che cita ogni partecipante nella propria. I binding si annidano, e
uscire dal blocco interno ripristina quello esterno.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Su una lista di destinatari sono le stringhe differite a fare il lavoro: il
messaggio si scrive una volta sola, all'import, e viene reso una volta per
lingua.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Il binding è una `ContextVar`, non uno stack tenuto su un oggetto condiviso,
quindi richieste che si sovrappongono non possono prendere l'una la lingua
dell'altra — compreso il caso in cui *escano* dai loro blocchi nello stesso
ordine in cui vi sono entrate, che è l'intreccio sbagliato da uno stack a
pila. Caricare un catalogo per lingua costa poco: `gettext.translation()`
analizza ogni `.mo` una sola volta e restituisce copie che condividono il
catalogo già analizzato.

!!! warning "Un thread di lavoro parte non legato"

    Un semplice `threading.Thread`, o `ThreadPoolExecutor.submit`, comincia con
    un contesto nuovo e non eredita il binding — la chiamata ripiega sul
    catalogo gettext globale del processo. Portati dietro il contesto in modo
    esplicito:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` lo fa già per te.

## Che cosa succede quando un catalogo è sbagliato { #what-happens-when-a-catalog-is-wrong }

Se i segnaposto di una traduzione non corrispondono alla sorgente — un campo
mancante, sconosciuto o riformattato che è sfuggito alla validazione, da un
MO modificato a mano, un catalogo di terze parti o una pipeline che salta il
checker — il comportamento predefinito è riprodurre il testo sorgente invece
di sollevare un'eccezione. Questo rispecchia il contratto di gettext stesso:
un catalogo danneggiato non rompe mai l'applicazione.

Con `Hello {name}` tradotto come `こんにちは {nombre}`, il rendering riesce e
un avviso va al logger `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

L'avviso scatta una volta per messaggio e pattern, non una volta per
rendering, così una voce di catalogo danneggiata non inonda un log.

Scegli di fallire rumorosamente per i test e la CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

La stessa ricerca allora solleva un'eccezione, portando la stessa frase senza
la metà "using source text":

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Leggere un messaggio di errore { #reading-a-failure-message }

Questi messaggi sono scritti per chi può agire su di essi, che per un
problema di catalogo è più spesso un traduttore che un programmatore.
Riferire soltanto che `{name}` manca è un vicolo cieco quando il lettore può
vedere quei caratteri davanti a sé, quindi dove un segnaposto sembra presente
ma non lo è, il messaggio dice perché. Contro la sorgente `Hello {name}`,
ciascuno di questi è riportato sotto
`translation does not match the source placeholders:`

| La traduzione dice | La ragione che riporta |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

I caratteri che non si possono vedere ricevono un trattamento a parte. Uno
spazio unificatore dentro le graffe è qualcosa che un metodo di input produce
e nessun editor mostra, quindi il messaggio lo stampa per punto di codice
invece di nominare un carattere che il lettore non può trovare:

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

## Rendere un pattern senza un catalogo { #rendering-a-pattern-without-a-catalog }

`compile_template` espone lo stesso meccanismo un livello più in basso:
trasforma una t-string nel suo msgid più un insieme di valori legati, e rende
qualunque pattern tu gli passi.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` valida con le stesse regole e **solleva sempre** su una mancata
corrispondenza. Qui non esiste una modalità permissiva: la permissività
esiste perché una ricerca in un *catalogo* possa degradare al testo sorgente,
e un pattern che hai passato tu stesso non ha nulla da cui degradare.

## Sicurezza e ambito { #safety-and-scope }

Questo è valido:

```python
tr(t"Hello {name}")
```

Questi sono rifiutati di proposito:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Calcola prima un valore significativo:

```python
name = user.display_name()
tr(t"Hello {name}")
```

La restrizione produce chiavi di catalogo stabili, dà ai traduttori nomi
utili e impedisce a una stringa tradotta di diventare un linguaggio di
espressioni.

La garanzia è limitata a *struttura e formattazione*: una traduzione non
viene mai valutata, e non può mai aggiungere accesso agli attributi,
chiamate, conversioni o specifiche di formato. Due cose restano
responsabilità del chiamante, esattamente come con il gettext della stdlib —
l'**escaping** dell'output reso per la sua destinazione (HTML, shell,
terminale), e l'**integrità del catalogo**, dato che un catalogo ostile può
ripetere un segnaposto per amplificare la dimensione dell'output, cosa
inerente a qualunque i18n basata su segnaposto.
