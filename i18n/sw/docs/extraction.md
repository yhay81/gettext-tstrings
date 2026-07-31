---
description: "Kutoa jumbe za t-string kwa pybabel, na jinsi msgfmt pamoja na kikaguzi cha Babel kilichoambatishwa vinavyothibitisha katalogi."
---

# Utoaji

Utoaji ndiyo hatua inayokusanya kila ujumbe uliowekewa alama kutoka kwenye
msimbo wako chanzo hadi kiolezo cha `.pot` kwa ajili ya wafasiri — hatua ya 3
ya mzunguko wa [mafunzo](tutorial.md). Ukurasa huu ni marejeo ya hatua hiyo:
usanidi, majina maalum ya vitendakazi, hali kali ya CI, na ukaguzi unaolinda
katalogi zako baadaye.

Utoaji unahitaji nyongeza ya `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Mtiririko wa kazi { #the-workflow }

Tengeneza `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Kisha tumia amri za kawaida za Babel:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` huendeshwa mara moja kwa kila lugha; baada ya hapo, `pybabel update`
huingiza kila kiolezo kipya ndani ya katalogi zilizopo. Mzunguko huo unaojirudia
— na maana ya maingizo yake ya `fuzzy` kwa toleo — umepitiwa katika
[Katika uzalishaji](workflow.md#the-cycle-after-the-first-translation).

Kitoaji cha `gettext_tstrings` pia hushughulikia miito ya kawaida ya `_()`,
`gettext()`, na `ngettext()`, hivyo ramani moja hufunika msimbo mchanganyiko.
Hutambua `_()`, majina manne sanifu ya gettext, visawe vya `tr()` / `ntr()`, na
`lazy_gettext()` / `lazy_pgettext()` zilizoahirishwa.

!!! warning "Wezesha maoni ya wafasiri kwa `-c`"

    `pybabel extract` hukusanya maoni ya wafasiri tu unapopitisha
    `-c "Translators:"`, sawasawa na inavyofanya kwa miito ya kawaida ya
    gettext. Ukiiacha, utoaji bado hufanya kazi — maoni tu hayafiki kamwe
    kwenye katalogi, ambako ndiyo [kigezo cha ubora chenye gharama ndogo
    kuliko vyote](workflow.md#working-with-translators-and-platforms) katika
    mtiririko mzima wa kazi.

## Kusajili majina yako mwenyewe ya vitendakazi { #registering-your-own-function-names }

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

Faili la ini hutoa mfuatano mmoja, ramani ya TOML hutoa orodha, na ndani ya
mfuatano ama nafasi tupu ama koma hutenganisha majina. Namna zote nne hufanya
kazi.

Machaguo ni `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions`, na `npgettext_functions`.

!!! danger "`-k` haifiki t-string"

    Msaidizi maalum kama `mytr(t"…")` lazima atajwe katika mojawapo ya machaguo
    hapo juu. Mfumo wa `--keyword` wa Babel hauwezi kusoma tungo halisi ya
    t-string, hivyo `pybabel extract -k mytr` haipati chochote na haisemi
    chochote — jumbe hazipo tu ndani ya POT. `-k` huendelea kufanya kazi kwa
    miito ya kawaida ya gettext inayotolewa pamoja nazo.

    Mpangilio sanifu tu wa hoja unaungwa mkono: ujumbe kwanza, muktadha kisha
    ujumbe kwa `pgettext`, muktadha kisha umoja kisha wingi kwa `npgettext`.

## Legevu ndani ya kompyuta yako, kali katika CI { #lenient-locally-strict-in-ci }

Kwa chaguo-msingi faili moja bovu halikomeshi mzunguko mzima:

- t-string ambayo kitoaji hukikataa — ufikiaji wa sifa, usemi, hoja isiyo
  sahihi — huripotiwa kama onyo na kurukwa.
- Faili ambalo halitachanganuliwa hurukwa kwa namna ileile.
- Vivyo hivyo faili ambalo `tokenize` pekee hulikataa huku `ast` ikilikubali,
  ambalo pasipo hivyo pitio la Babel lenyewe lingelisimamisha.

Hilo ni la kufaa unapokuwa unahariri nalo ni hatari usipokuwa: ujumbe
uliorukwa **haupo tu ndani ya POT**, hivyo hautafsiriwi kamwe na hakuna
kinachosema hivyo. Weka `strict = true` katika machaguo ya ramani mahali popote
ambapo utoaji hautazamwi na binadamu:

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

Kila onyo lililo hapo juu ndipo hugeuka kuwa kushindwa kabisa. Chukulia hili
kama mpangilio wa uzalishaji nacho chaguo-msingi kama cha ndani ya kompyuta
yako.

## Zana zako zilizopo huthibitisha katalogi hizi { #your-existing-toolchain-validates-these-catalogs }

Babel huweka alama kwenye kila ujumbe uliotolewa kwa bendera sanifu, na mstari
huo mmoja ndio unaowasha ukaguzi wa vishika nafasi katika zana ambazo tayari
unaziendesha:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Itafsiri kama `こんにちは {nombre}` na kosa hukamatwa bila usanidi wowote:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate huandika ukaguzi uleule kama [Python brace format][weblate-checks], na
majukwaa ya kibiashara yana QA yao ya vishika nafasi inayotegemea bendera
ileile. Tabia ya kila jukwaa ni yake lenyewe; zana mbili zilizo hapa chini ndizo
zilizothibitishwa hapa.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Zaidi ya hapo, kifurushi husajili **kikaguzi** cha Babel, hivyo
`pybabel compile` hutumia kanuni za ainisho kwa kila ujumbe unaobeba maoni ya
alama ya `gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Kwa ujumbe wa wingi kiashiria hutaja umbo, kwa sababu nambari ya mstari ambayo
Babel huiripoti ni ya msgid nacho kizuizi cha Kirusi kina `msgstr` tatu chini yake:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` bado huandika `.mo`"

    Hitilafu iliyo hapo juu huripotiwa, hali ya kutoka ni `1` — na katalogi
    bovu hukusanywa hata hivyo. Ni hali hiyo ya kutoka pekee inayoweza kuzuia
    mkondo usiisafirishe; [Kile CI inachozuia](workflow.md#what-ci-gates)
    huonyesha hatua ya ujenzi inayoiwezesha.

Ukaguzi huo wa aina mbili haurudufiani. Kikaguzi cha kifurushi ni kikali zaidi
katika angalau visa viwili:

- msgid ambayo mabano yake pekee yamekwepwa (`Config {{raw}} only`) haipati
  kamwe bendera ya `python-brace-format`, hivyo hakuna zana ya nje inayoithibitisha
  hata kidogo.
- Maumbo ya wingi hukaguliwa moja baada ya jingine. `msgfmt --check-format`
  husoma faili lilelile lililo hapo juu na hutoka kwa `0`; umbo linaloacha
  kishika nafasi ambacho ndugu zake huhifadhi hukubaliwa huko na hukataliwa
  hapa.

`msgfmt` hukagua tu majina ya vishika nafasi ambayo inaweza kuyachanganua kama
umbizo la mabano la Python, hivyo majina ya ASCII huifanya kila zana katika
mnyororo iweze kuthibitisha ujumbe. Maktaba yenyewe hukubali jina lolote lenye
`str.isidentifier()`.

## Violezo na zana nyingine { #templates-and-other-tools }

t-strings ni sintaksia ya Python, hivyo maktaba hii hufunika msimbo chanzo wa
Python. Lugha za violezo huendelea kutumia i18n yao — `{% trans %}` ya Jinja2,
lebo za violezo za Django — pamoja na vitoaji vya Babel kwa ajili yao. Kila
kitu hulisha katalogi ileile ya PO, hivyo mtiririko mmoja wa tafsiri bado
hufunika msimbo mchanganyiko.

`pygettext` haiwezi kuchanganua t-strings leo, ndiyo maana utoaji hupitia
Babel. Makubaliano yameandikwa katika [ainisho](spec.md) ili kitoaji kingine,
au `pygettext` ya siku zijazo, kiweze kuyalenga.
