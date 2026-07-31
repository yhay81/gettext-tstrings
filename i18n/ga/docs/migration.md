---
description: "Glacadh le t-strings i dtionscadal a bhfuil catalóga gettext aige cheana: cad a mhaireann gan teagmháil, cad a théann fuzzy, agus conas bogadh láithreán glaonna amháin sa turas."
---

# Aistriú anonn

Má úsáideann do thionscadal gettext cheana féin, is ceisteanna cúnga iad na
cinn a shocraíonn an féidir glacadh leis an leabharlann seo: an gcuireann sí
na catalóga atá agat ó bhail, an féidir léi maireachtáil taobh leis an gcód
nach bhfuil tú réidh lena athrú, agus cé mhéad den bhogadh a chaithfidh
tarlú ag an am céanna. Na freagraí, an ceann is giorra ar dtús:

| Ceist | Freagra |
| --- | --- |
| An oibríonn na comhaid `.po` agus `.mo` atá ann cheana fós? | Oibríonn. Na comhaid chéanna, na huirlisí céanna. |
| An féidir le seanghlaonna agus glaonna nua maireachtáil in aon chomhad amháin? | Is féidir, agus clúdaíonn mapáil eastóscóra amháin an dá cheann. |
| An athraíonn an msgid? | Ní athraíonn ó `.format()`. Athraíonn ó `%`-format. |
| An gcaithfidh an tionscadal ar fad bogadh ag an am céanna? | Ní chaithfidh. Is athrú bailí é láithreán glaonna amháin. |
| Cad faoi Jinja, teimpléid Django, JavaScript? | Gan teagmháil, na catalóga céanna. |

Is é an chuid eile den leathanach seo an mionsonra taobh thiar de gach ceann
díobh sin.

## Ó `.format()`: ní athraíonn an msgid { #from-format-the-msgid-does-not-change }

Seo an cás nach gcosnaíonn an t-aistriú beagnach faic. Díorthaíonn
teachtaireacht `str.format` agus teachtaireacht t-string an eochair chatalóige
*chéanna*, mar gurb é an téacs agus `{name}` fágtha ann atá san eochair sa dá
chás:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Mar sin fanann an t-aistriúchán atá ann ceangailte leis. Ag tosú ó chatalóg
ina bhfuil

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

athraigh an glao, ath-eastósc, agus nuashonraigh:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Níl an iontráil a thagann ar ais difriúil ach in dhá líne meiteashonraí agus
faic eile — nóta tráchta marcála a aithníonn í mar theachtaireacht t-string,
agus uimhir líne foinse:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Gan bhratach `fuzzy`, gan athaistriúchán, in aon teanga. Rindreáiltear an
teachtaireacht láithreach:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "Tuairisceoidh `update --check` na catalóga mar chinn atá as dáta"

    Is leor an nóta tráchta marcála sin agus na huimhreacha líne a bhog le go
    ndéarfadh `pybabel update --check` go bhfuil catalóg le hathghiniúint,
    mar go gcuireann sé an iontráil iomlán i gcomparáid agus ní hé an
    t-aistriúchán amháin. Rith an fíor-`pybabel update` sa tiomantas céanna
    leis an athrú cóid, agus tiomantaigh na catalóga leis — an nós céanna a
    iarrann an [geata CI](workflow.md#what-ci-gates) cheana féin.

## Ó `%`-format: athraíonn an msgid, mar sin téann na haistriúcháin fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Tá comhréir printf ina cónaí *taobh istigh* den teachtaireacht, mar sin
athscríobhann é a ionadú eochair na catalóige. Níl aon bhealach timpeall air
sin, agus is é costas macánta `%(name)s` a fhágáil i do dhiaidh é:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

Aithníonn `pybabel update` gur gaol gairid don cheann a baineadh amach an
teachtaireacht nua agus iompraíonn sé an seanaistriúchán trasna, marcáilte
fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Trí rud is fiú a bheith ar eolas faoin staid sin:

- **Ní bhriseann faic ag am rite.** Fágtar iontrálacha fuzzy amach as an `.mo`
  thiomsaithe, mar sin rindreáileann an feidhmchlár an teachtaireacht
  fhoinseach go dtí go ndeimhníonn duine an péire —
  [an dul in olcas céanna](workflow.md#the-cycle-after-the-first-translation)
  a théann aon teachtaireacht athfhoclaithe tríd.
- **Fanann CI glas fad is atá siad fuzzy.** Scipeálann seiceálaí na
  sealbhóirí ionaid iontrálacha fuzzy, díreach mar a dhéanann
  `msgfmt --check-format`, mar nár cheart d'iontráil nach féidir léi an t-am
  rite a shroicheadh teip a chur ar thógáil. An nóiméad a ghlanann
  aistritheoir an bhratach, seiceáiltear an iontráil mar aon cheann eile —
  mar sin beirtear ansin ar `%(name)s` a fágadh in aistriúchán deimhnithe,
  agus sin an pointe ag a dtosódh sé ag rindreáil murach sin.
- **Marcálann an seanbhratach `python-format` leis** agus ba chóir í a
  scriosadh in éineacht leis an mbratach `fuzzy`, nó leanfaidh
  `msgfmt --check-format` de rialacha printf a chur i bhfeidhm ar
  theachtaireacht i bhformáid lúibíní.

I gcás sealbhóirí ionaid printf a bhfuil ainm orthu is eagarthóireacht
mheicniúil atá ann — éiríonn `{name}` as `%(name)s` agus ní bhogann faic eile
— mar sin is pas scriptithe agus athbhreithniú aistritheora ina dhiaidh atá i
gcatalóg mhór, seachas athaistriúchán. Níl `%s` suímh meicniúil: níl ainm
aige le hiompar trasna, agus is é ceann a roghnú pointe an athraithe.

Is féidir leis an aistriú dul ar aghaidh dá bhrí sin ar cibé luas a
cheadaíonn an t-athbhreithniú: is píosa oibre atá le feiceáil sa chatalóg í
iontráil fuzzy nach bhfuil tiontaithe, ní tógáil bhriste.

## Maireann seanghlaonna agus glaonna nua le chéile { #old-and-new-calls-coexist }

Léann an t-eastóscóir a léann t-strings gnáthghlaonna gettext freisin, mar sin
clúdaíonn mapáil amháin comhad atá i lár an aistrithe:

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

Tuirlingíonn an dá theachtaireacht sa teimpléad céanna, agus níl an nóta
tráchta marcála a chuireann seiceáil bhreise na leabharlainne seo ar siúl ach
ar cheann an t-string:

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

Aithníonn sé `_()`, na ceithre ainm chaighdeánacha gettext, na leasainmneacha
`tr()` / `ntr()`, agus na cinn iarchurtha `lazy_gettext()` /
`lazy_pgettext()`. Caithfear cúntóir de do chuid féin a
[ainmniú sa mhapáil](extraction.md#registering-your-own-function-names).

Ag am rite tá an dá stíl chomh neamhspleách céanna: filleann
`gettext.translation()` oibiacht aistriúchán amháin, agus léann `_` agus
pointí iontrála na leabharlainne seo araon uaithi.

## Cad nach mbogann { #what-does-not-move }

- **Teangacha teimpléid.** Leanann `{% trans %}` Jinja2, clibeanna teimpléid
  Django, agus a n-eastóscóirí Babel ag obair gan athrú agus ag beathú na
  gcatalóg PO céanna. Is comhréir Python iad na t-strings; baineann siad le
  foinse Python.
- **Do chomhaid chatalóige.** Gan athrú formáide, gan chomhad nua, gan chéim
  tiontaithe.
- **D'ardán aistriúcháin.** Tá an malartú `.po` mar an gcéanna, agus is í an
  bhratach `python-brace-format` a iompraíonn teachtaireacht t-string an
  bhratach chéanna a iompraíonn teachtaireacht `.format()` — mar sin leanann
  dearbhú cáilíochta na sealbhóirí ionaid ag obair.
- **Cód nach Python é.** Ní chuirtear isteach ar chatalóg JavaScript ná C sa
  tionscadal céanna.

## Seicliosta aistrithe { #a-migration-checklist }

1. Cuir an breiseán `babel` leis san áit a ritheann `pybabel`, agus athraigh
   an mhapáil `python` in `babel.cfg` go dtí an modh `gettext_tstrings` —
   clúdaíonn mapáil amháin an dá stíl ansin, agus leanann `-k` ag obair do na
   gnáthghlaonna.
2. Tiontaigh láithreáin ghlaonna `.format()` ar dtús. Ath-eastósc, rith
   `pybabel update`, agus tiomantaigh na catalóga leis an gcód; ná bíodh
   coinne agat le hiontrálacha fuzzy.
3. Tiontaigh láithreáin ghlaonna `%`-format i mbaisceanna is féidir leat a
   chur faoi athbhreithniú, agus athscríobh na sealbhóirí ionaid a iompraíodh
   trasna agus glan na bratacha `fuzzy` agus `python-format`.
4. Ceartaigh an rud a ndiúltaíonn an srian dó: caithfidh idirshuíomh a bheith
   ina ainm lom, mar sin éiríonn athróg áitiúil as `t"Hello {user.name}"` ar
   dtús. Is eagarthóireacht láithreáin ghlaonna é seo, ní ceann catalóige.
5. Cuir `strict = true` ar siúl i mapáil an eastóscóra a luaithe is atá an
   scuabadh déanta, ionas go gcuirfeadh teachtaireacht nach féidir a
   eastóscadh teip ar [an tógáil](extraction.md#lenient-locally-strict-in-ci)
   seachas imeacht as an teimpléad.
6. Cuir an tseiceáil ama rite ó [I dtáirgeadh](workflow.md#what-ci-gates)
   leis: rindreáil teachtaireacht amháin in aghaidh gach teanga a sheoltar trí
   `Translator` dian.

Is gnáth-thiomantais iad céimeanna 2 agus 3. Níl lá brataí ag teastáil ó aon
rud ar an liosta seo.
