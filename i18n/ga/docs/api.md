---
description: "Gach ainm a easpórtálann gettext_tstrings: feidhmeanna, an Translator, ceangal comhthéacs, teaghráin leisciúla, agus na hearráidí."
---

# API

Easpórtáiltear gach rud thíos ó `gettext_tstrings`. Níl aon rud eile poiblí.
Is é an leathanach seo an tagairt do na sínithe; le haghaidh samplaí oibrithe
de gach feidhm, féach ar an [treoir](guide.md).

## Ag aistriú { #translating }

Tógann gach feidhm a t-string de réir suímh agus glacann sí le dhá argóint
eochairfhocail: `translations` (a thiteann ar ais ar cheangal an chomhthéacs,
agus ansin ar fheidhmeanna domhanda na leabharlainne caighdeánaí) agus
`strict` (féach ar an [Treoir](guide.md#what-happens-when-a-catalog-is-wrong)).

| Feidhm | Síniú |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | leasainm ar `gettext` |
| `ntr` | leasainm ar `ngettext` |

### `Translator`

Sonrarang reoite a cheanglaíonn oibiacht aistriúcháin amháin, ionas nach
n-athdhéanann láithreacha glao é.

```python
Translator(translations, strict=False)
```

Tá sé inghairthe (`_(t"…")`) agus iompraíonn sé `gettext`, `ngettext`,
`pgettext`, `npgettext`, agus na leasainmneacha `tr` / `ntr`.

## Ceangal comhthéacs { #context-binding }

| Ainm | Cuspóir |
| --- | --- |
| `use_translations(translations)` | Ceangail ar feadh ré bhloc `with`, agus athchóirigh ansin. |
| `set_translations(translations)` | Ceangail gan bhloc, do thimthriallta saoil atá á mbainistiú ag creat. |
| `get_translations()` | Léigh an ceangal reatha, nó `None`. |

Is `ContextVar` é an ceangal, mar sin baineann sé le gach comhthéacs ar leith
agus tá sé sábháilte faoi chomhuainíocht.

## Teaghráin iarchurtha { #deferred-strings }

| Ainm | Cuspóir |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Cuir an t-aistriúchán ar athló go dtí gach rindreáil. |
| `lazy_pgettext(context, template, /, *, strict=False)` | An fhoirm chomhthéacsúil. |
| `LazyString` | An rud a fhilleann an dá cheann. Rindreáileann sé trí `str()` agus `format()` sa teanga atá ceangailte ag an nóiméad sin, bíonn sé cothrom lena théacs rindreáilte i gcomparáid, agus níl hais air d'aon ghnó. |

Tá samplaí oibrithe, lena n-áirítear an chúis a mbaineann `strict` leis an
sainmhíniú, faoi [Aistriúchán iarchurtha](guide.md#deferred-translation).

## Leibhéal níos ísle { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Tiomsaigh t-string, ag athúsáid a phlean stataigh atá i dtaisce.

### `CompiledTemplate`

| Ball | Brí |
| --- | --- |
| `.msgid` | Aitheantóir cobhsaí na teachtaireachta gettext. |
| `.placeholders` | Ainmneacha na sealbhóirí ionaid in ord an chéad tarlaithe. |
| `.render(pattern)` | Bailíochtaigh patrún amháin agus rindreáil é. **Ardaíonn sé eisceacht i gcónaí** nuair nach meaitseálann rud. |

## Cineálacha agus earráidí { #types-and-errors }

### `Translations`

`Protocol` `runtime_checkable` do na ceithre mhodh chaighdeánacha, iad ar fad
suímh amháin:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

Sásaíonn `gettext.NullTranslations`, `gettext.GNUTranslations`, agus
`Translations` Babel é.

### Eisceachtaí

| Rang | Ardaítear é nuair |
| --- | --- |
| `TStringError` | Bunrang don dá cheann thíos. |
| `InvalidTemplateError` | Briseann an t-string **foinseach** an coinbhinsiún — idirshuíomh casta, nó ainm athdhéanta le formáidiú difriúil. |
| `InvalidTranslationError` | Briseann an **t-aistriúchán** é. Faoin mód bog réamhshocraithe logáiltear é seo agus rindreáiltear an téacs foinseach ina áit. |

## Pointí iontrála eastósctha { #extraction-entry-points }

Cláraítear go huathoibríoch iad ag am suiteála; tagraíonn tú dóibh de réir
ainm, ní trí iompórtáil.

| Grúpa | Ainm | Á úsáid ag |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | An `method` i `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, go huathoibríoch. |

## Feidhmíocht { #performance }

Tá an cuntas iomlán — cad a chuirtear i dtaisce, cad ar a n-eochraíonn na
taiscí, agus na huimhreacha tomhaiste — in
[An cosán te](internals.md#the-hot-path). An leagan gearr: cuirtear an
bailíochtú i dtaisce, ní scipeáiltear riamh é, agus ní chosnaíonn an rindreáil
ar fad ach codán de mhicreashoicind. Rith an tagarmharc ar do sprioc féin:

```console
uv run python benchmarks/runtime.py
```
