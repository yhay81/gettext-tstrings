---
description: "Att införa t-strings i ett projekt som redan har gettext-kataloger: vad som förblir orört, vad som blir fuzzy, och hur du flyttar ett anropsställe i taget."
---

# Migrering

Om ditt projekt redan använder gettext är frågorna som avgör om det här
biblioteket går att införa smala: ogiltigförklarar det katalogerna du har, kan
det samexistera med koden du inte är redo att ändra, och hur mycket av flytten
måste ske på en gång. Svaren, det kortaste först:

| Fråga | Svar |
| --- | --- |
| Fungerar befintliga `.po`- och `.mo`-filer fortfarande? | Ja. Samma filer, samma verktyg. |
| Kan gamla och nya anrop bo i samma fil? | Ja, och en enda extraktormappning täcker båda. |
| Ändras msgid:n? | Inte från `.format()`. Ja från `%`-format. |
| Måste hela projektet flytta på en gång? | Nej. Ett anropsställe är en giltig ändring. |
| Vad händer med Jinja, Django-mallar, JavaScript? | Orörda, samma kataloger. |

Resten av den här sidan är detaljerna bakom var och en av dem.

## Från `.format()`: msgid:n ändras inte { #from-format-the-msgid-does-not-change }

Det här är fallet där migreringen nästan inte kostar något. Ett
`str.format`-meddelande och ett t-string-meddelande härleder *samma*
katalognyckel, eftersom nyckeln är texten med `{name}` kvar i sig i båda
fallen:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Så den befintliga översättningen sitter kvar. Utgå från en katalog som
innehåller

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

ändra anropet, extrahera om, och uppdatera:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Posten som kommer tillbaka skiljer sig på två metadatarader och ingenting
annat — en markörkommentar som identifierar den som ett t-string-meddelande,
och ett radnummer i källkoden:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Ingen `fuzzy`-flagga, ingen omöversättning, på något språk. Meddelandet
renderas omedelbart:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` kommer att rapportera katalogerna som inaktuella"

    Den markörkommentaren och de flyttade radnumren räcker för att
    `pybabel update --check` ska säga att en katalog behöver genereras om,
    eftersom den jämför hela posten och inte bara översättningen. Kör den
    riktiga `pybabel update` i samma commit som kodändringen, och committa
    katalogerna med den — samma vana som
    [CI-grinden](workflow.md#what-ci-gates) redan ber om.

## Från `%`-format: msgid:n ändras, så översättningar blir fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Printf-syntax bor *inuti* meddelandet, så att ersätta den skriver om
katalognyckeln. Det går inte att komma runt, och det är den ärliga kostnaden
för att lämna `%(name)s` bakom sig:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` känner igen det nya meddelandet som en nära släkting till det
borttagna och bär över den gamla översättningen, märkt fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Tre saker att veta om det tillståndet:

- **Ingenting går sönder vid körning.** Fuzzy-poster utesluts ur den
  kompilerade `.mo`-filen, så applikationen renderar källmeddelandet tills en
  människa bekräftar paret — [samma degradering](workflow.md#the-cycle-after-the-first-translation)
  som varje omformulerat meddelande går igenom.
- **`pybabel compile` rapporterar var och en**, eftersom det överförda
  `%(name)s` inte är en giltig klammerplatshållare, och avslutar med nollskild
  status. Den listan är din arbetskö, inte ett falsklarm; posterna i den
  behöver verkligen redigeras.
- **Den gamla `python-format`-flaggan följer med** och bör raderas tillsammans
  med `fuzzy`-flaggan, annars fortsätter `msgfmt --check-format` att tillämpa
  printf-regler på ett brace-format-meddelande.

För namngivna printf-platshållare är redigeringen mekanisk — `%(name)s` blir
`{name}` och ingenting annat rör sig — så en stor katalog är en skriptad
genomgång följd av en översättares granskning, snarare än en omöversättning.
Positionella `%s` är inte mekaniska: de har inget namn att bära över, och att
välja ett är hela poängen med ändringen.

Därför är den praktiska ordningen att migrera `%`-format-meddelanden medvetet
— en modul, en release, ett språk i taget — snarare än i ett svep som gör varje
katalog röd på en gång.

## Gamla och nya anrop samexisterar { #old-and-new-calls-coexist }

Extraktorn som läser t-strings läser också vanliga gettext-anrop, så en enda
mappning täcker en fil mitt i migreringen:

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

Båda meddelandena hamnar i samma mall, och bara t-string-meddelandet bär
markörkommentaren som slår på det här bibliotekets extra kontroller:

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

Den känner igen `_()`, de fyra standardnamnen i gettext, aliasen `tr()` /
`ntr()` och de uppskjutna `lazy_gettext()` / `lazy_pgettext()`. En egen
hjälpfunktion måste [namnges i mappningen](extraction.md#registering-your-own-function-names).

Vid körning är de två stilarna lika oberoende: `gettext.translation()`
returnerar ett översättningsobjekt, och både `_` och det här bibliotekets
ingångar läser ur det.

## Vad som inte flyttar { #what-does-not-move }

- **Mallspråk.** Jinja2:s `{% trans %}`, Djangos malltaggar och deras
  Babel-extraktorer fortsätter fungera oförändrade och fortsätter mata samma
  PO-kataloger. t-strings är Python-syntax; de gäller Python-källkod.
- **Dina katalogfiler.** Ingen formatändring, ingen ny fil, inget
  konverteringssteg.
- **Din översättningsplattform.** Utbytet via `.po` är identiskt, och flaggan
  `python-brace-format` som ett t-string-meddelande bär är samma flagga som ett
  `.format()`-meddelande bär — så platshållar-QA fortsätter fungera.
- **Kod som inte är Python.** En JavaScript- eller C-katalog i samma projekt
  påverkas inte.

## En migreringschecklista { #a-migration-checklist }

1. Lägg till extrat `babel` där `pybabel` körs, och byt `python`-mappningen i
   `babel.cfg` till metoden `gettext_tstrings` — en mappning täcker då båda
   stilarna, och `-k` fortsätter fungera för de vanliga anropen.
2. Konvertera `.format()`-anropsställena först. Extrahera om, kör
   `pybabel update`, och committa katalogerna med koden; räkna med noll
   fuzzy-poster.
3. Konvertera `%`-format-anropsställena i satser du hinner få granskade, skriv
   om de överförda platshållarna och rensa flaggorna `fuzzy` och
   `python-format`.
4. Åtgärda det som begränsningen avvisar: en interpolation måste vara ett rent
   namn, så `t"Hello {user.name}"` blir en lokal variabel först. Det är en
   ändring på anropsstället, inte i katalogen.
5. Slå på `strict = true` i extraktormappningen när svepet är klart, så att ett
   meddelande som inte går att extrahera fäller
   [bygget](extraction.md#lenient-locally-strict-in-ci) i stället för att
   försvinna ur mallen.
6. Lägg till körningskontrollen från [I produktion](workflow.md#what-ci-gates):
   rendera ett meddelande per levererat språk genom en strikt `Translator`.

Steg 2 och 3 är vanliga commits. Ingenting i den här listan behöver en
omställningsdag.
