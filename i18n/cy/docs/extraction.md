---
description: "Echdynnu negeseuon llinyn-t gyda pybabel, a sut y mae msgfmt a'r gwiriwr Babel cynwysedig yn dilysu'r catalogau."
---

# Echdynnu

Echdynnu yw'r cam sy'n casglu pob neges wedi'i nodi allan o'ch cod ffynhonnell
i mewn i dempled `.pot` ar gyfer cyfieithwyr — cam 3 o ddolen y
[tiwtorial](tutorial.md). Y dudalen hon yw'r cyfeirlyfr ar gyfer y cam hwnnw:
ffurfweddu, enwau ffwythiannau pwrpasol, modd CI llym, a'r gwiriadau sy'n
gwarchod eich catalogau wedyn.

Mae angen yr ychwanegyn `babel` ar echdynnu:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Y llif gwaith { #the-workflow }

Crëwch `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Yna defnyddiwch y gorchmynion Babel arferol:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

Mae `init` yn rhedeg unwaith fesul iaith; ar ôl hynny, mae `pybabel update` yn
plygu pob templed ffres i mewn i'r catalogau sy'n bodoli. Cerddir drwy'r cylch
cylchol hwnnw — a'r hyn y mae ei gofnodion `fuzzy` yn ei olygu i ryddhad — yn
[Mewn cynhyrchu](workflow.md#the-cycle-after-the-first-translation).

Mae'r echdynnwr `gettext_tstrings` hefyd yn trin galwadau `_()`, `gettext()` ac
`ngettext()` cyffredin, felly mae un mapio'n ymdrin â chodfas gymysg. Mae'n
adnabod `_()`, y pedwar enw gettext safonol, yr enwau eraill `tr()` / `ntr()`,
a'r rhai gohiriedig `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "Galluogwch sylwadau i gyfieithwyr â `-c`"

    Nid yw `pybabel extract` yn casglu sylwadau i gyfieithwyr oni bo chi'n
    pasio `-c "Translators:"`, yn union fel y mae'n ei wneud ar gyfer galwadau
    gettext cyffredin. Gadewch ef allan ac mae'r echdynnu'n dal i weithio — nid
    yw'r sylwadau'n cyrraedd y catalog, dyna i gyd, lle maent
    [y lifer ansawdd rhataf](workflow.md#working-with-translators-and-platforms)
    yn y llif gwaith cyfan.

## Cofrestru eich enwau ffwythiant eich hun { #registering-your-own-function-names }

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

Mae ffeil ini yn rhoi un llinyn, mae mapio TOML yn rhoi rhestr, ac o fewn llinyn
mae naill ai bylchau neu atalnodau yn gwahanu'r enwau. Mae'r pedwar sillafiad
yn gweithio.

Yr opsiynau yw `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions`, a `npgettext_functions`.

!!! danger "Nid yw `-k` yn cyrraedd llinyn-t"

    Rhaid enwi cynorthwyydd pwrpasol megis `mytr(t"…")` yn un o'r opsiynau
    uchod. Ni all peirianwaith `--keyword` Babel ddarllen llythrennyn llinyn-t,
    felly nid yw `pybabel extract -k mytr` yn canfod dim ac nid yw'n dweud dim
    — mae'r negeseuon yn syml absennol o'r POT. Mae `-k` yn dal i weithio ar
    gyfer y galwadau gettext cyffredin a echdynnir ochr yn ochr.

    Dim ond y drefn ymresymiadau safonol a gefnogir: neges yn gyntaf, cyd-destun
    ac wedyn neges ar gyfer `pgettext`, cyd-destun ac wedyn unigol ac wedyn
    lluosog ar gyfer `npgettext`.

## Goddefgar yn lleol, llym mewn CI { #lenient-locally-strict-in-ci }

Yn ddiofyn nid yw un ffeil ddrwg yn terfynu'r rhediad:

- Caiff llinyn-t y mae'r echdynnwr yn ei wrthod — galw priodoledd, ymadrodd,
  ymresymiad anghywir — ei adrodd fel rhybudd a'i hepgor.
- Caiff ffeil na fydd yn parsio ei hepgor yr un ffordd.
- Felly hefyd ffeil y mae `tokenize` yn unig yn ei gwrthod tra bo `ast` yn ei
  derbyn, sef un y byddai pas Babel ei hun fel arall yn erthylu arni.

Mae hynny'n gyfleus tra byddwch yn golygu ac yn beryglus pan na fyddwch:
mae neges a hepgorwyd yn syml **absennol o'r POT**, felly ni chaiff byth ei
chyfieithu ac nid oes dim yn dweud hynny. Gosodwch `strict = true` yn opsiynau'r
mapio ym mhob man lle nad oes dynol yn gwylio'r echdynnu:

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

Yna daw pob rhybudd uchod yn fethiant caled. Trafodwch hwn fel y gosodiad
cynhyrchu a'r diofyn fel yr un lleol.

## Mae eich cadwyn offer bresennol yn dilysu'r catalogau hyn { #your-existing-toolchain-validates-these-catalogs }

Mae Babel yn nodi pob neges a echdynnir â baner safonol, a'r un llinell honno
sy'n gweithredu gwirio dalwyr lle yn yr offer yr ydych eisoes yn eu rhedeg:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Cyfieithwch ef fel `こんにちは {nombre}` a chaiff y camgymeriad ei ddal heb
unrhyw ffurfweddu:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Mae Weblate yn dogfennu'r un gwiriad fel [Python brace format][weblate-checks],
ac mae gan y llwyfannau masnachol eu QA dalwyr lle eu hunain wedi'i allweddu ar
yr un faner. Eiddo pob llwyfan ei hun yw ei ymddygiad; y ddau offeryn isod yw'r
rhai a wiriwyd yma.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Ar ben hynny, mae'r pecyn yn cofrestru **gwiriwr** Babel, felly mae
`pybabel compile` yn cymhwyso rheolau'r fanyleb i bob neges sy'n cario'r sylw
marciwr `gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Ar gyfer neges luosog mae'r pwyntydd yn enwi'r ffurf, am mai rhif llinell y
msgid a adroddir gan Babel ac mae gan floc Rwsieg dri `msgstr` oddi tano:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "Mae `pybabel compile` yn dal i ysgrifennu'r `.mo`"

    Caiff y gwall uchod ei adrodd, `1` yw'r statws ymadael — ac mae'r catalog
    toredig yn cael ei grynhoi beth bynnag. Dim ond y statws ymadael hwnnw a
    all atal piblinell rhag ei gludo; mae [Yr hyn y mae CI yn ei
    gatio](workflow.md#what-ci-gates) yn dangos y cam adeiladu sy'n gadael
    iddo wneud hynny.

Nid yw'r ddau wiriad yn ddiangen. Mae gwiriwr y pecyn yn llymach mewn o leiaf
ddau achos:

- Nid yw msgid nad oes ganddo ond bracedi wedi'u dianc (`Config {{raw}} only`)
  byth yn cael y faner `python-brace-format`, felly nid oes unrhyw offeryn
  allanol yn ei ddilysu o gwbl.
- Caiff ffurfiau lluosog eu gwirio fesul un. Mae `msgfmt --check-format` yn
  darllen yr union ffeil uchod ac yn ymadael â `0`; caiff ffurf sy'n gollwng
  daliwr lle y mae ei chwiorydd yn ei gadw ei derbyn yno a'i gwrthod yma.

Nid yw `msgfmt` ond yn gwirio enwau dalwyr lle y gall eu parsio fel fformat
braced Python, felly mae enwau ASCII yn cadw pob offeryn yn y gadwyn yn gallu
dilysu'r neges. Mae'r llyfrgell ei hun yn derbyn unrhyw enw
`str.isidentifier()`.

## Templedi ac offer eraill { #templates-and-other-tools }

Cystrawen Python yw llinynnau-t, felly mae'r llyfrgell hon yn ymdrin â ffynhonnell
Python. Mae ieithoedd templedi'n dal i ddefnyddio eu i18n eu hunain — `{% trans %}`
Jinja2, tagiau templed Django — ac echdynwyr Babel ar eu cyfer. Mae popeth yn
bwydo'r un catalog PO, felly mae un llif gwaith cyfieithu'n dal i ymdrin â
chodfas gymysg.

Ni all `pygettext` barsio llinynnau-t heddiw, a dyna pam y mae echdynnu'n mynd
drwy Babel. Ysgrifennwyd y confensiwn i lawr yn y [fanyleb](spec.md) fel y gall
echdynnwr arall, neu `pygettext` y dyfodol, anelu ato.
