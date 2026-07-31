---
description: "Teachtaireachtaí t-string a eastóscadh le pybabel, agus an chaoi a mbailíochtaíonn msgfmt agus seiceálaí Babel an phacáiste na catalóga."
---

# Eastóscadh

Is é an t-eastóscadh an chéim a bhailíonn gach teachtaireacht mharcáilte amach
as do chód foinseach isteach i dteimpléad `.pot` do na haistritheoirí — céim 3
de lúb an [ranga teagaisc](tutorial.md). Is é an leathanach seo an tagairt don
chéim sin: cumraíocht, ainmneacha feidhme saincheaptha, mód dian CI, agus na
seiceálacha a chosnaíonn do chatalóga ina dhiaidh sin.

Teastaíonn an breiseán `babel` ón eastóscadh:

```console
python -m pip install "gettext-tstrings[babel]"
```

## An sreabhadh oibre { #the-workflow }

Cruthaigh `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Ansin úsáid gnáthorduithe Babel:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

Ritheann `init` uair amháin in aghaidh na teanga; ina dhiaidh sin, filleann
`pybabel update` gach teimpléad úr isteach sna catalóga atá ann cheana.
Siúltar tríd an timthriall athfhillteach sin — agus tríd an méid a chiallaíonn
a chuid iontrálacha `fuzzy` d'eisiúint — in
[I dtáirgeadh](workflow.md#the-cycle-after-the-first-translation).

Láimhseálann eastóscóir `gettext_tstrings` gnáthghlaonna `_()`, `gettext()`
agus `ngettext()` freisin, mar sin clúdaíonn mapáil amháin bunachar cóid
measctha. Aithníonn sé `_()`, na ceithre ainm chaighdeánacha gettext, na
leasainmneacha `tr()` / `ntr()`, agus na cinn iarchurtha `lazy_gettext()` /
`lazy_pgettext()`.

!!! warning "Níl `-c` roghnach"

    Ní bhailíonn `pybabel extract` nótaí tráchta d'aistritheoirí ach nuair a
    chuireann tú `-c "Translators:"` isteach, díreach mar a dhéanann sé do
    ghnáthghlaonna gettext.

## Do chuid ainmneacha feidhme féin a chlárú { #registering-your-own-function-names }

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

Tugann comhad ini teaghrán amháin, tugann mapáil TOML liosta, agus laistigh de
theaghrán scarann spás bán nó camóga na hainmneacha. Oibríonn na ceithre
litriú go léir.

Is iad na roghanna `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` agus `npgettext_functions`.

!!! danger "Ní shroicheann `-k` t-string"

    Caithfear cúntóir saincheaptha ar nós `mytr(t"…")` a ainmniú i gceann de
    na roghanna thuas. Ní féidir le hinneall `--keyword` Babel litriúil
    t-string a léamh, mar sin ní aimsíonn `pybabel extract -k mytr` faic agus
    ní deir sé faic — níl na teachtaireachtaí sa POT, sin uile. Leanann `-k`
    ag obair do na gnáthghlaonna gettext a eastósctar taobh leo.

    Ní thacaítear ach leis an ord caighdeánach argóintí: an teachtaireacht ar
    dtús, an comhthéacs agus ansin an teachtaireacht do `pgettext`, an
    comhthéacs agus ansin an t-uatha agus ansin an t-iolra do `npgettext`.

## Stóinsithe de réir réamhshocraithe { #robust-by-default }

Ní chuireann drochchomhad amháin deireadh leis an rith:

- Tuairiscítear t-string a ndiúltaíonn an t-eastóscóir dó — rochtain ar
  thréith, slonn, argóint mhícheart — mar rabhadh agus scipeáiltear é.
- Scipeáiltear comhad nach bparsálfaidh ar an gcaoi chéanna.
- Mar an gcéanna le comhad nach ndiúltaíonn ach `tokenize` dó agus a nglacann
  `ast` leis, rud a chuirfeadh deireadh le pas Babel féin murach sin.

Socraigh `strict = true` i roghanna na mapála chun gach ceann díobh sin a
iompú ina chrua-theip ina áit sin, agus sin an rud is mian leat i CI.

## Bailíochtaíonn do shlabhra uirlisí atá ann cheana na catalóga seo { #your-existing-toolchain-validates-these-catalogs }

Marcálann Babel gach teachtaireacht eastósctha le bratach chaighdeánach, agus
is í an líne amháin sin a chuireann seiceáil na sealbhóirí ionaid ar siúl sna
huirlisí a ritheann tú cheana:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Aistrigh mar `こんにちは {nombre}` é agus beirtear ar an mbotún gan aon
chumraíocht:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Doiciméadaíonn Weblate an tseiceáil chéanna mar
[Python brace format][weblate-checks], agus tá a ndearbhú cáilíochta
sealbhóirí ionaid féin ag na hardáin thráchtála bunaithe ar an mbratach
chéanna. Is leo féin a n-iompar; is iad an dá uirlis thíos na cinn atá
fíoraithe anseo.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Anuas air sin, cláraíonn an pacáiste **seiceálaí** Babel, mar sin cuireann
`pybabel compile` rialacha na sonraíochta i bhfeidhm ar gach teachtaireacht a
bhfuil an nóta marcála `gettext-tstrings` uirthi:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

I gcás teachtaireachta iolra ainmníonn an pointeoir an fhoirm, mar gurb é
uimhir líne an msgid a thuairiscíonn Babel agus go bhfuil trí `msgstr` faoi
bhloc Rúisise:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "Scríobhann `pybabel compile` an `.mo` mar sin féin"

    Tuairiscítear an earráid thuas, is é `1` an stádas scortha — agus
    tiomsaítear an chatalóg lochtach ar aon nós. Níl ann ach an stádas
    scortha sin a chuirfidh cosc ar phíblíne í a sheoladh; taispeánann
    [Cad a gheataíonn CI](workflow.md#what-ci-gates) an chéim tógála a
    cheadaíonn é sin.

Níl an dá sheiceáil iomarcach. Is é an seiceálaí a sheoltar leis an bpacáiste
an páirtí is déine in dhá áit ar a laghad:

- Ní fhaigheann msgid nach bhfuil ann ach lúibíní éalaithe
  (`Config {{raw}} only`) an bhratach `python-brace-format` riamh, mar sin ní
  bhailíochtaíonn aon uirlis sheachtrach ar chor ar bith é.
- Seiceáiltear na foirmeacha iolra ceann ar cheann. Léann
  `msgfmt --check-format` an comhad díreach thuas agus scoireann sé le `0`;
  glactar ansin le foirm a fhágann sealbhóir ionaid ar lár a choinníonn a
  deirfiúracha, agus diúltaítear di anseo.

Ní sheiceálann `msgfmt` ach ainmneacha sealbhóirí ionaid is féidir leis a
pharsáil mar fhormáid lúibíní Python, mar sin fágann ainmneacha ASCII gach
uirlis sa slabhra in ann an teachtaireacht a bhailíochtú. Glacann an
leabharlann féin le haon ainm a shásaíonn `str.isidentifier()`.

## Teimpléid agus uirlisí eile { #templates-and-other-tools }

Is comhréir Python iad na t-strings, mar sin clúdaíonn an leabharlann seo
foinse Python. Leanann teangacha teimpléid dá n-i18n féin — `{% trans %}`
Jinja2, clibeanna teimpléid Django — agus d'eastóscóirí Babel dóibh. Cothaíonn
gach rud an chatalóg PO chéanna, mar sin clúdaíonn sreabhadh oibre
aistriúcháin amháin bunachar cóid measctha fós.

Ní féidir le `pygettext` t-strings a pharsáil inniu, agus sin an fáth a
dtéann an t-eastóscadh trí Babel. Tá an coinbhinsiún scríofa síos sa
[tsonraíocht](spec.md) ionas go bhféadfadh eastóscóir eile, nó `pygettext`
amach anseo, é a spriocdhíriú.
