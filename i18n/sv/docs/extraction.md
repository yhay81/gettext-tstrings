---
description: "Extrahera t-string-meddelanden med pybabel, och hur msgfmt och den medföljande Babel-kontrollen validerar katalogerna."
---

# Extrahering

Extrahering är steget som samlar varje markerat meddelande ur din källkod
till en `.pot`-mall för översättare — steg 3 i [handledningens](tutorial.md)
kretslopp. Den här sidan är referensen för det steget: konfiguration, egna
funktionsnamn, strikt CI-läge, och kontrollerna som vaktar dina kataloger
efteråt.

Extrahering behöver extrat `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Arbetsflödet { #the-workflow }

Skapa `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Använd sedan de vanliga Babel-kommandona:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` körs en gång per språk; därefter viker `pybabel update` in varje
färsk mall i de befintliga katalogerna. Den återkommande cykeln — och vad
dess `fuzzy`-poster betyder för en release — gås igenom i
[I produktion](workflow.md#the-cycle-after-the-first-translation).

Extraktorn `gettext_tstrings` hanterar också vanliga `_()`-, `gettext()`- och
`ngettext()`-anrop, så en enda mappning täcker en blandad kodbas. Den känner
igen `_()`, de fyra standardnamnen i gettext, aliasen `tr()` / `ntr()` och de
uppskjutna `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "`-c` är inte valfritt"

    `pybabel extract` samlar bara in översättarkommentarer när du skickar
    `-c "Translators:"`, precis som för vanliga gettext-anrop.

## Registrera dina egna funktionsnamn { #registering-your-own-function-names }

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

En ini-fil ger en sträng, en TOML-mappning ger en lista, och inom en sträng
avgränsar antingen blanksteg eller kommatecken namnen. Alla fyra
skrivsätten fungerar.

Alternativen är `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` och `npgettext_functions`.

!!! danger "`-k` når inte en t-string"

    En egen hjälpfunktion som `mytr(t"…")` måste namnges i något av
    alternativen ovan. Babels `--keyword`-maskineri kan inte läsa en
    t-string-literal, så `pybabel extract -k mytr` hittar ingenting och
    säger ingenting — meddelandena är helt enkelt frånvarande ur POT-filen.
    `-k` fortsätter fungera för de vanliga gettext-anrop som extraheras vid
    sidan av.

    Endast standardargumentordningen stöds: meddelandet först, kontext sedan
    meddelande för `pgettext`, kontext sedan singular sedan plural för
    `npgettext`.

## Robust som standard { #robust-by-default }

En dålig fil avslutar inte körningen:

- En t-string som extraktorn avvisar — attributåtkomst, ett uttryck, ett
  felaktigt argument — rapporteras som en varning och hoppas över.
- En fil som inte går att parsa hoppas över på samma sätt.
- Likaså en fil som bara `tokenize` vägrar medan `ast` accepterar den, som
  Babels egen genomgång annars skulle avbryta på.

Sätt `strict = true` i mappningsalternativen för att i stället göra vart och
ett av dessa till ett hårt fel, vilket är vad du vill ha i CI.

## Din befintliga verktygskedja validerar dessa kataloger { #your-existing-toolchain-validates-these-catalogs }

Babel markerar varje extraherat meddelande med en standardflagga, och den
enda raden är vad som aktiverar platshållarkontroll i verktygen du redan kör:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Översätt det som `こんにちは {nombre}` och misstaget fångas utan någon
konfiguration:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate dokumenterar samma kontroll som
[Python brace format][weblate-checks], och de kommersiella plattformarna har
sin egen platshållar-QA nycklad på samma flagga. Deras beteende är deras
eget; de två verktygen nedan är de som verifieras här.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Utöver det registrerar paketet en Babel-**kontroll** (checker), så att
`pybabel compile` tillämpar specifikationens regler på varje meddelande som
bär markörkommentaren `gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

För ett pluralmeddelande namnger hänvisningen formen, eftersom radnumret
Babel rapporterar är msgid:ns och ett ryskt block har tre `msgstr` under sig:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` skriver ändå `.mo`-filen"

    Felet ovan rapporteras, avslutsstatusen är `1` — och den trasiga
    katalogen kompileras i alla fall. Endast den avslutsstatusen kan hindra
    en pipeline från att leverera den;
    [Vad CI ska grinda](workflow.md#what-ci-gates) visar byggsteget som
    låter den göra det.

De två kontrollerna är inte överflödiga sida vid sida. Den medföljande
kontrollen är den strängare parten på minst två punkter:

- En msgid vars enda klamrar är escapade (`Config {{raw}} only`) får aldrig
  flaggan `python-brace-format`, så inget externt verktyg validerar den alls.
- Pluralformer kontrolleras en och en. `msgfmt --check-format` läser exakt
  filen ovan och avslutar med `0`; en form som tappar en platshållare som
  dess syskon behåller accepteras där och avvisas här.

`msgfmt` kontrollerar bara platshållarnamn det kan parsa som Python brace
format, så ASCII-namn håller varje verktyg i kedjan kapabelt att validera
meddelandet. Biblioteket självt accepterar vilket
`str.isidentifier()`-namn som helst.

## Mallar och andra verktyg { #templates-and-other-tools }

t-strings är Python-syntax, så det här biblioteket täcker Python-källkod.
Mallspråk fortsätter använda sin egen i18n — Jinja2:s `{% trans %}`, Djangos
malltaggar — och Babels extraktorer för dem. Allt matar samma PO-katalog, så
ett enda översättningsarbetsflöde täcker fortfarande en blandad kodbas.

`pygettext` kan inte parsa t-strings i dag, vilket är varför extraheringen
går genom Babel. Konventionen är nedskriven i [specifikationen](spec.md) så
att en annan extraktor, eller en framtida `pygettext`, kan rikta in sig på
den.
