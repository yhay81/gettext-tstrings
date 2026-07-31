---
description: "Prevzemanje t-nizov v projektu, ki gettextove kataloge že ima: kaj ostane nedotaknjeno, kaj postane ohlapno in kako se premikati po eno klicno mesto naenkrat."
---

# Migracija

Če vaš projekt gettext že uporablja, so vprašanja, ki odločijo, ali je to
knjižnico mogoče prevzeti, ozka: ali razveljavi kataloge, ki jih imate, ali
lahko sobiva s kodo, ki je še niste pripravljeni spremeniti, in koliko selitve
se mora zgoditi naenkrat. Odgovori, najkrajši najprej:

| Vprašanje | Odgovor |
| --- | --- |
| Ali obstoječe datoteke `.po` in `.mo` še delujejo? | Da. Iste datoteke, ista orodja. |
| Ali lahko stari in novi klici živijo v eni datoteki? | Da, in ena preslikava ekstraktorja pokrije oboje. |
| Ali se msgid spremeni? | Iz `.format()` ne. Iz `%`-oblikovanja da. |
| Ali se mora ves projekt preseliti naenkrat? | Ne. Eno klicno mesto je veljavna sprememba. |
| Kaj pa Jinja, Djangove predloge, JavaScript? | Nedotaknjeni, isti katalogi. |

Preostanek te strani so podrobnosti za vsakim od teh odgovorov.

## Iz `.format()`: msgid se ne spremeni { #from-format-the-msgid-does-not-change }

To je primer, pri katerem migracija ne stane skoraj nič. Sporočilo iz
`str.format` in sporočilo iz t-niza izpeljeta *isti* katalogni ključ, saj je
ključ v obeh primerih besedilo, v katerem ostane `{name}`:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Obstoječi prevod torej ostane pripet. Če izhajate iz kataloga, ki vsebuje

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

spremenite klic, znova izvlecite in posodobite:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Vnos, ki se vrne, se razlikuje v dveh vrsticah metapodatkov in v ničemer
drugem — v označevalnem komentarju, ki ga prepozna kot sporočilo iz t-niza, in
v številki izvorne vrstice:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Nobene zastavice `fuzzy`, nobenega ponovnega prevajanja, v nobenem jeziku.
Sporočilo se izriše takoj:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` bo kataloge javil kot zastarele"

    Tisti označevalni komentar in premaknjene številke vrstic zadoščajo, da
    `pybabel update --check` pove, da je treba katalog obnoviti, saj primerja
    celoten vnos in ne le prevoda. Resnični `pybabel update` poženite v istem
    commitu kot spremembo kode in kataloge commitajte skupaj z njo — ista
    navada, kot jo [zaščita v CI](workflow.md#what-ci-gates) zahteva že
    zdaj.

## Iz `%`-oblikovanja: msgid se spremeni, zato prevodi postanejo ohlapni { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Sintaksa printf živi *znotraj* sporočila, zato njena zamenjava prepiše
katalogni ključ. Tega ni mogoče zaobiti in to je poštena cena slovesa od
`%(name)s`:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` novo sporočilo prepozna kot bližnjega sorodnika
odstranjenega in stari prevod prenese s sabo, označen kot ohlapen:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

O tem stanju je treba vedeti troje:

- **Med izvajanjem se ne pokvari nič.** Ohlapni vnosi so izključeni iz
  kompiliranega `.mo`, zato aplikacija izrisuje izvorno sporočilo, dokler par
  ne potrdi človek — [ista poslabšava](workflow.md#the-cycle-after-the-first-translation),
  skozi katero gre vsako preoblikovano sporočilo.
- **CI ostane zelen, dokler so ohlapni.** Preverjevalnik ograd ohlapne vnose
  preskoči, natanko kot `msgfmt --check-format`, ker vnos, ki ne more doseči
  izvajanja, ne sme podreti gradnje. V trenutku, ko prevajalec zastavico
  izbriše, je vnos preverjen kot vsak drug — tako se `%(name)s`, pozabljen v
  potrjenem prevodu, ujame prav takrat, ko bi se sicer začel izrisovati.
- **Stara zastavica `python-format` potuje zraven** in jo je treba izbrisati
  skupaj z zastavico `fuzzy`, sicer bo `msgfmt --check-format` na sporočilo z
  zavitimi oklepaji še naprej uporabljal pravila printf.

Pri imenovanih ogradah printf je urejanje mehansko — `%(name)s` postane
`{name}` in nič drugega se ne premakne —, zato je velik katalog en skriptni
prehod, ki mu sledi prevajalčev pregled, in ne ponovno prevajanje. Pozicijski
`%s` ni mehanski: nima imena, ki bi ga prenesli, in prav izbira tega imena je
bistvo spremembe.

Migracija lahko zato napreduje s hitrostjo, ki jo dopušča pregled: nepretvorjen
ohlapen vnos je viden kos dela v katalogu, ne pokvarjena gradnja.

## Stari in novi klici sobivajo { #old-and-new-calls-coexist }

Ekstraktor, ki bere t-nize, bere tudi običajne klice gettexta, zato ena
preslikava pokrije datoteko sredi migracije:

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

Obe sporočili pristaneta v isti predlogi in le tisto iz t-niza nosi
označevalni komentar, ki vklopi dodatno preverjanje te knjižnice:

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

Prepozna `_()`, štiri standardna imena gettexta, vzdevka `tr()` / `ntr()` in
odložena `lazy_gettext()` / `lazy_pgettext()`. Lastnega pomočnika je treba
[imenovati v preslikavi](extraction.md#registering-your-own-function-names).

Med izvajanjem sta sloga enako neodvisna: `gettext.translation()` vrne en
prevodni objekt, iz njega pa berejo tako `_` kot vstopne točke te knjižnice.

## Kaj se ne premakne { #what-does-not-move }

- **Predlogni jeziki.** Jinja2 `{% trans %}`, Djangove predlogne značke in
  njihovi Babelovi ekstraktorji delujejo nespremenjeni naprej in še vedno
  polnijo iste kataloge PO. T-nizi so pythonska sintaksa; veljajo za pythonsko
  izvorno kodo.
- **Vaše katalogne datoteke.** Nobene spremembe formata, nobene nove datoteke,
  nobenega koraka pretvorbe.
- **Vaša prevajalska platforma.** Izmenjava prek `.po` je enaka, zastavica
  `python-brace-format`, ki jo nosi sporočilo iz t-niza, pa je ista zastavica,
  kot jo nosi sporočilo iz `.format()` — zato nadzor kakovosti ograd deluje
  naprej.
- **Koda, ki ni pythonska.** Katalog za JavaScript ali C v istem projektu
  ostane neprizadet.

## Kontrolni seznam za migracijo { #a-migration-checklist }

1. Dodajte dodatek `babel` tam, kjer teče `pybabel`, in preslikavo `python` v
   `babel.cfg` spremenite v metodo `gettext_tstrings` — ena preslikava tedaj
   pokrije oba sloga, `-k` pa za običajne klice deluje naprej.
2. Najprej pretvorite klicna mesta z `.format()`. Znova izvlecite, poženite
   `pybabel update` in kataloge commitajte skupaj s kodo; ohlapnih vnosov ne
   pričakujte.
3. Klicna mesta z `%`-oblikovanjem pretvarjajte v svežnjih, ki jih zmorete
   spraviti skozi pregled, pri čemer prenesene ograde prepišete ter zastavici
   `fuzzy` in `python-format` izbrišete.
4. Popravite, kar omejitev zavrne: interpolacija mora biti preprosto ime, zato
   `t"Hello {user.name}"` najprej postane lokalna spremenljivka. To je
   urejanje klicnega mesta, ne kataloga.
5. Ko je pometanje končano, v preslikavi ekstraktorja vklopite `strict = true`,
   da sporočilo, ki ga ni mogoče izvleči, podre
   [gradnjo](extraction.md#lenient-locally-strict-in-ci), namesto da bi izginilo
   iz predloge.
6. Dodajte preverjanje med izvajanjem iz [V produkciji](workflow.md#what-ci-gates):
   po eno sporočilo na odpremljeni jezik izrišite skozi strogi `Translator`.

Koraka 2 in 3 sta običajna commita. Nič na tem seznamu ne potrebuje enega
samega velikega preklopnega dne.
