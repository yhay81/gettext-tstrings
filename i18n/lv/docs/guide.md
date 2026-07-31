---
description: "Izpildlaika API: kataloga piesaiste, valodas katram pieprasījumam, atliktās virknes un tas, kā tiek ziņots par sabojātu tulkojumu."
---

# Ceļvedis

Šī lapa ir izpildlaika uzziņa: viss, ko ar šo bibliotēku dara jūsu *lietotnes
kods*, tiklīdz katalogi pastāv. Ja vēl neesat redzējuši visu ciklu — atzīmēt,
ekstrahēt, iztulkot, kompilēt, palaist —, [pamācība](tutorial.md) to izstaigā
vienreiz piecās minūtēs; katalogu izveidošana un validēšana ir aprakstīta
[Ekstrakcijā](extraction.md), bet tas, kā komanda tur ciklu griežamies —
atjaunināšanas cikli, CI, tulkošanas platformas —, ir lapā
[Produkcijā](workflow.md).

## Kataloga piesaiste { #binding-a-catalog }

Ieteicamā forma atspoguļo gettext klašu balstīto lietojumu: piesaistiet
standarta tulkojumu objektu vienreiz un lietojiet izsaucamo procesoru kā `_`.

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

Moduļa līmeņa funkcijas seko standarta bibliotēkas nosaukumiem un tās tikai
pozicionālo argumentu izsaukšanas konvencijai:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` un `ntr` ir precīzi `gettext` un `ngettext` aizstājvārdi.

## Valoda katram pieprasījumam { #per-request-language }

Tīmekļa ietvars izvēlas valodu katram pieprasījumam. Piesaistiet pieprasījuma
tulkojumus tekošajam kontekstam, un katrs moduļa līmeņa izsaukums atrisināsies
uz šo valodu, droši arī vienlaicīgu pieprasījumu apstākļos:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` piesaista bez `with` bloka — ietvariem, kas
paši pārvalda pieprasījuma dzīves ciklu; `get_translations()` nolasa tekošo
piesaisti. Skaidri norādīts arguments `translations=` vienmēr uzvar pār
kontekstu, bet nepiesaistīts konteksts atkāpjas uz standarta bibliotēkas
globāli instalētajām gettext funkcijām. Izstrādāti Flask un ASGI starpprogrammu
piemēri ir lapā [Produkcijā](workflow.md#binding-a-language-at-runtime).

## Atliktā tulkošana { #deferred-translation }

T-virkne notver savas vērtības nekavējoties, un tas ir nepareizi virknei, kas
definēta importa laikā — formas uzrakstam, enum vērtībai, moduļa konstantei —,
kurai jārenderējas tajā valodā, kas ir aktīva brīdī, kad to *lieto*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` renderējas caur `str()`, `format()` un f-virknēm, un salīdzinājumā
ir vienāds ar savu renderēto tekstu.

!!! note "Apzināti nehešojams"

    `LazyString` teksts ir atkarīgs no aktīvās valodas, tāpēc hešs mainītos
    līdz ar valodas pārslēgšanu un klusējot sabojātu jebkuru kopu vai vārdnīcu,
    kas to tur. Ja jums vajadzīga atslēga, vispirms izsauciet `str()`.

`strict` tiek izlemts tur, kur ziņojums ir uzrakstīts, nevis tur, kur tas
renderējas:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Atliktā virkne renderējas tur, kur tā galu galā tiek lietota — šablonā, formā,
žurnāla rindā —, un šī vieta reti zina, vai tas ir testa izpildījums vai
produkcija. Tieši `strict=True` padošana definīcijā ļauj to pašu izvēli —
[skaļi CI, iecietīgi produkcijā](#what-happens-when-a-catalog-is-wrong) —
attiecināt uz virkni, kas netiek renderēta savā izsaukuma vietā.

Daudzskaitļa formas ir atkarīgas no izpildlaika skaita, tāpēc renderējiet tās
nekavējoties ar `ngettext` tur, kur skaits ir zināms.

## Kas notiek, kad katalogs ir kļūdains { #what-happens-when-a-catalog-is-wrong }

Ja tulkojuma vietturi neatbilst avotam — trūkstošs, nezināms vai
pārformatēts lauks, kas paslīdējis garām validācijai, no ar roku rediģēta MO,
piegādātāja kataloga vai konveijera, kas izlaiž pārbaudītāju —, noklusējums ir
atveidot avota tekstu, nevis izraisīt kļūdu. Tas atspoguļo paša gettext
kontraktu, ka slikts katalogs nekad nesalauž lietotni.

Ja `Hello {name}` ir iztulkots kā `こんにちは {nombre}`, renderēšana izdodas un
uz `gettext_tstrings` žurnalizētāju aiziet viens brīdinājums:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Brīdinājums nostrādā vienreiz katram ziņojumam un rakstam, nevis vienreiz
katrā renderēšanā, tāpēc sabojāts kataloga ieraksts nepārpludina žurnālu.

Testiem un CI varat izvēlēties skaļu kļūmi:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Tā pati meklēšana tad izraisa kļūdu, nesot to pašu teikumu bez puses par
“using source text”:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Kā lasīt kļūmes ziņojumu { #reading-a-failure-message }

Šie ziņojumi ir rakstīti tam, kurš var rīkoties, un kataloga problēmas
gadījumā tas biežāk ir tulkotājs, nevis programmētājs. Ziņot tikai to, ka
`{name}` trūkst, ir strupceļš, ja lasītājs šīs rakstzīmes redz sev priekšā,
tāpēc tur, kur vietturis izskatās klāt esošs, bet nav, ziņojums pasaka, kāpēc.
Pret avotu `Hello {name}` katrs no šiem tiek ziņots zem
`translation does not match the source placeholders:`

| Tulkojumā rakstīts | Norādītais iemesls |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (figūriekavas ap to nav ASCII `{` un `}`) |
| `こんにちは {{name}}` | `{name}` is missing (tas rakstīts kā `{{name}}`, un tā tiek atsoļota literāla figūriekava) |
| `こんにちは name` | `{name}` is missing (nosaukums parādās, bet ne figūriekavās) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Rakstzīmes, kas nav redzamas, saņem savu apstrādi. Nedalāmā atstarpe
figūriekavās ir tas, ko rada ievades metode un ko neviens redaktors neparāda,
tāpēc ziņojums to izdrukā pēc koda punkta, nevis nosauc rakstzīmi, ko lasītājs
nespēj atrast:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Nosaukums, kura burti sajauc rakstības sistēmas — homoglifu gadījums, kad
kirilicas `а` nav atšķirama no latīņu burta —, tiek parādīts divreiz: vienreiz
lasāmi un vienreiz atsoļots, un tā ir vienīgā forma, kas abus izšķir:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Tā pati atšķiršana notiek, kad grieķu vai kirilicas nosaukums, kas pilnībā
rakstīts vienā rakstībā, konfliktē ar ASCII avota nosaukumu, arī viena burta
gadījumā ar latīņu `a` un kirilicas `а`.

## Raksta renderēšana bez kataloga { #rendering-a-pattern-without-a-catalog }

`compile_template` atklāj to pašu mehānismu vienu līmeni zemāk: tas pārvērš
t-virkni par tās msgid plus piesaistītu vērtību kopu un renderē jebkuru rakstu,
ko tam padodat.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` validē pēc tiem pašiem likumiem un neatbilstības gadījumā **vienmēr
izraisa kļūdu**. Šeit nav iecietīgā režīma: iecietība pastāv tāpēc, lai
*kataloga* meklēšana varētu degradēties uz avota tekstu, bet rakstam, ko esat
padevuši paši, nav no kā degradēties.

## Drošība un tvērums { #safety-and-scope }

Šis ir derīgs:

```python
tr(t"Hello {name}")
```

Šie tiek noraidīti ar nolūku:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Vispirms aprēķiniet jēgpilnu vērtību:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Ierobežojums rada stabilas kataloga atslēgas, dod tulkotājiem noderīgus
nosaukumus un neļauj iztulkotai virknei kļūt par izteiksmju valodu.

Garantija attiecas uz *struktūru un formatējumu*: tulkojums nekad netiek
izvērtēts un nekad nevar pievienot piekļuvi atribūtiem, izsaukumus,
konversijas vai formāta specifikācijas. Divas lietas paliek izsaucēja atbildībā
tieši tāpat kā ar standarta bibliotēkas gettext — renderētās izvades
**atsoļošana** tās saņēmējam (HTML, čaula, terminālis) un **kataloga
integritāte**, jo naidīgs katalogs var atkārtot vietturi, lai uzpūstu izvades
apjomu, un tas ir raksturīgi jebkurai uz vietturiem balstītai i18n.
