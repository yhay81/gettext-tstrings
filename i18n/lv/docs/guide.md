---
description: "Izpildlaika API: kuru ieejas punktu lietot, kataloga piesaiste, valodas katram pieprasījumam, atliktās virknes, lokāli ievērojošas vērtības un tas, kā tiek ziņots par sabojātu tulkojumu."
---

# Ceļvedis

Šī lapa ir izpildlaika uzziņa: viss, ko ar šo bibliotēku dara jūsu *lietotnes
kods*, tiklīdz katalogi pastāv. Ja vēl neesat redzējuši visu ciklu — atzīmēt,
ekstrahēt, iztulkot, kompilēt, palaist —, [pamācība](tutorial.md) to izstaigā
vienreiz piecās minūtēs; katalogu izveidošana un validēšana ir aprakstīta
[Ekstrakcijā](extraction.md), bet tas, kā komanda tur ciklu griežamies —
atjaunināšanas cikli, CI, tulkošanas platformas —, ir lapā
[Produkcijā](workflow.md).

## Kuru ieejas punktu lietot? { #which-entry-point-should-i-use }

Pakotne eksportē vairākus veidus, kā iztulkot ziņojumu, jo lietotnes valodu
piesaista vairākos dažādos veidos. Izvēlieties pēc tā, kā jūsu programma
izlemj, kurā valodā tā ir:

| Jūsu situācija | Lietojiet |
| --- | --- |
| Viena valoda visam procesam — CLI, darbvirsmas lietotne, skripts | `Translator`, izsaukts kā `_` |
| Viena valoda katram pieprasījumam vai asinhronajam uzdevumam — tīmekļa lietotne | `use_translations()` ap darbu, tad `tr()` |
| Ziņojums, definēts importa laikā — formas uzraksts, enum, konstante | `lazy_gettext()` vai `lazy_pgettext()` |
| Formulējumu izlemj skaits | `ngettext()` / `npgettext()` jebkurā no augšminētajām formām |
| Raksta renderēšana bez jebkāda kataloga | `compile_template()` |

Viss tālāk ir šie pieci, tieši šādā secībā.

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
    name = request.user.display_name
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

## Vairākas valodas vienlaikus { #several-languages-at-once }

Vienam pieprasījumam bieži vajag vairāk nekā vienu valodu: lapu, kas renderēta
lasītājam un kas turklāt ierindo paziņojumu kontam, kuram iestatīta cita, vai
kopsavilkumu, kas katru dalībnieku citē viņa paša valodā. Piesaistes iegulst
viena otrā, un iekšējā bloka atstāšana atjauno ārējo.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Ejot cauri adresātu sarakstam, darbu paveic atliktās virknes: ziņojums ir
uzrakstīts vienreiz, importēšanas laikā, un renderējas vienreiz katrā valodā.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Piesaiste ir `ContextVar`, nevis steks, kas turēts uz koplietota objekta, tāpēc
pieprasījumi, kas pārklājas, nevar pārņemt cits cita valodu — arī tajā
gadījumā, kad tie savus blokus *atstāj* tādā secībā, kādā tajos iegāja, un
tieši šo pārklāšanos steks izdara nepareizi. Ielādēt katalogu katrai valodai ir
lēti: `gettext.translation()` parsē katru `.mo` vienreiz un izsniedz kopijas,
kas dala parsēto katalogu.

!!! warning "Vai darba pavediens manto piesaisti, ir atkarīgs no būvējuma"

    Kails `threading.Thread` vai `ThreadPoolExecutor.submit` sākas vai nu ar
    izsaucēja konteksta kopiju, vai ar tukšu, un to, kurš no tiem, nosaka
    `sys.flags.thread_inherit_context` — pēc noklusējuma patiess brīvpavedienu
    būvējumos un aplams visur citur. Tāpēc viens un tas pats kods uz 3.14t
    renderē piesaistīto valodu, bet uz 3.14 — procesa globālo katalogu.
    Padodiet kontekstu, nevis paļaujieties uz noklusējumu:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` to jūsu vietā jau dara.

## Lokāli ievērojošas vērtības { #locale-aware-values }

Šī bibliotēka izlemj, *kur* vērtība parādās iztulkotā ziņojumā. Tā nelokalizē
pašu vērtību. `{amount:,.2f}` ir Python formāta specifikācija ar fiksētu
uzvedību — komats ik pēc trim cipariem un punkts pirms decimāldaļas —, un tā
rada tās pašas rakstzīmes neatkarīgi no ziņojuma valodas:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Vācu valodā šo skaitli raksta `1.234,50`, franču valodā `1 234,50`, bet hindi
`1234567` grupē kā `12,34,567`, nevis `1,234,567`. Skaitļi, valūtas, datumi,
laiki un mērvienības pieder [Babel][babel-numbers]. Vispirms noformatējiet
vērtību, tad ielieciet gatavo virkni:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

Skaitāmā ziņojumā skaitlis dara divus darbus — tas izvēlas daudzskaitļa formu
un parādās tekstā —, un lokalizēts tiek tikai otrais. Paturiet neapstrādāto
skaitu izvēlei un padodiet noformatēto virkni attēlošanai:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Formatēšana pirms izsaukuma ir arī tas, kas notur formāta specifikāciju ārpus
kataloga: tulkotājs redz gatavu teksta gabalu, nevis skaitli plus norādījumus,
kā to renderēt.

## Kas notiek, kad katalogs ir kļūdains { #what-happens-when-a-catalog-is-wrong }

Ja tulkojuma vietturi neatbilst avotam — trūkstošs, nezināms vai
pārformatēts lauks, kas paslīdējis garām validācijai, no ar roku rediģēta MO,
piegādātāja kataloga vai konveijera, kas izlaiž pārbaudītāju —, noklusējums ir
renderēt avota ziņojumu, nevis izraisīt kļūdu. Tas atspoguļo paša gettext
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

Šie ziņojumi ir rakstīti tam, kurš var rīkoties, un kataloga problēmas
gadījumā tas biežāk ir tulkotājs, nevis programmētājs — tāpēc tur, kur vietturis
izskatās klāt esošs, bet nav, ziņojums paskaidro, kāpēc, nevis atkārto, ka tā
trūkst. Pilnplatuma figūriekavas, dubultots `{{name}}`, neredzama nedalāmā
atstarpe, kirilicas burts latīņu burtu vidū: katram no tiem ir savs
formulējums, un tie kopā ar piemēriem ir uzskaitīti lapā
[Tulkotājiem](translators.md#reading-a-failure-message). Tā lapa ir rakstīta
tā, lai to varētu iedot cilvēkam, kurš rediģē `.po`.

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

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
