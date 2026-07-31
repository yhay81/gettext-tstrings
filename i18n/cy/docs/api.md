---
description: "Pob enw y mae gettext_tstrings yn ei allforio: ffwythiannau, y Translator, rhwymo cyd-destun, llinynnau gohiriedig, a'r gwallau."
---

# API

Caiff popeth isod ei allforio o `gettext_tstrings`. Nid oes dim arall yn
gyhoeddus. Y dudalen hon yw'r cyfeirlyfr llofnodion; am enghreifftiau wedi'u
gweithio o bob ffwythiant, gweler y [canllaw](guide.md).

## Cyfieithu { #translating }

Mae pob ffwythiant yn cymryd ei linyn-t yn safleol ac yn derbyn dau ymresymiad
allweddair: `translations` (sy'n cwympo'n ôl i rwymiad y cyd-destun, ac wedyn i
ffwythiannau global y llyfrgell safonol) a `strict` (gweler
[Canllaw](guide.md#what-happens-when-a-catalog-is-wrong)).

| Ffwythiant | Llofnod |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | enw arall ar `gettext` |
| `ntr` | enw arall ar `ngettext` |

### `Translator`

Dosbarth data wedi'i rewi sy'n rhwymo un gwrthrych cyfieithu, fel nad oes
rhaid i safleoedd galw ei ailadrodd.

```python
Translator(translations, strict=False)
```

Mae'n alwadwy (`_(t"…")`) ac mae'n cario `gettext`, `ngettext`, `pgettext`,
`npgettext`, a'r enwau eraill `tr` / `ntr`.

## Rhwymo cyd-destun { #context-binding }

| Enw | Pwrpas |
| --- | --- |
| `use_translations(translations)` | Rhwymo am hyd bloc `with`, ac adfer wedyn. |
| `set_translations(translations)` | Rhwymo heb floc, ar gyfer cylchoedd bywyd a reolir gan fframwaith. |
| `get_translations()` | Darllen y rhwymiad presennol, neu `None`. |

`ContextVar` yw'r rhwymiad, felly mae'n perthyn i'r cyd-destun ac yn ddiogel
dan gydredoldeb.

## Llinynnau gohiriedig { #deferred-strings }

| Enw | Pwrpas |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Gohirio'r cyfieithu tan bob rendrad. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Y ffurf gyd-destunol. |
| `LazyString` | Yr hyn y mae'r ddau yn ei ddychwelyd. Mae'n rendro drwy `str()` a `format()` yn yr iaith sydd wedi'i rhwymo ar y foment honno, yn cymharu'n gyfartal â'i destun wedi'i rendro, ac yn fwriadol anhashadwy. |

Mae enghreifftiau ymarferol, gan gynnwys pam mae `strict` yn perthyn i'r
diffiniad, o dan [Cyfieithu gohiriedig](guide.md#deferred-translation).

## Lefel is { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Crynhoi llinyn-t, gan ailddefnyddio ei gynllun statig cachedig.

### `CompiledTemplate`

| Aelod | Ystyr |
| --- | --- |
| `.msgid` | Y dynodydd neges gettext sefydlog. |
| `.placeholders` | Enwau'r dalwyr lle yn nhrefn eu hymddangosiad cyntaf. |
| `.render(pattern)` | Dilysu un patrwm a'i rendro. **Bob amser yn codi** gwall os oes anghysondeb. |

## Mathau a gwallau { #types-and-errors }

### `Translations`

`Protocol` `runtime_checkable` ar gyfer y pedwar dull safonol, pob un yn
safleol yn unig:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

Mae `gettext.NullTranslations`, `gettext.GNUTranslations`, a `Translations`
Babel oll yn ei fodloni.

### Eithriadau

| Dosbarth | Yn codi pan |
| --- | --- |
| `TStringError` | Y dosbarth sylfaen ar gyfer y ddau isod. |
| `InvalidTemplateError` | Mae'r llinyn-t **ffynhonnell** yn torri'r confensiwn — rhyngosodiad cymhleth, neu enw a ailadroddir â fformatio gwahanol. |
| `InvalidTranslationError` | Mae'r **cyfieithiad** yn gwneud hynny. Dan y modd goddefgar rhagosodedig caiff hyn ei gofnodi a rendrir y testun ffynhonnell yn ei le. |

## Pwyntiau mynediad echdynnu { #extraction-entry-points }

Cânt eu cofrestru'n awtomatig wrth osod; cyfeiriwch atynt wrth eu henwau, nid
drwy fewnforio.

| Grŵp | Enw | Defnyddir gan |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | Y `method` yn `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, yn awtomatig. |

## Perfformiad { #performance }

Mae'r hanes llawn — beth a gaiff ei gachu, ar beth y mae'r cachau'n allweddu,
a'r rhifau a fesurwyd — yn [Y llwybr poeth](internals.md#the-hot-path). Y
fersiwn fer: caiff y dilysu ei gachu, ni chaiff byth ei hepgor, ac mae'r rendro
cyfan yn costio ffracsiwn o ficrosecond. Rhedwch y meincnod ar eich targed eich
hun:

```console
uv run python benchmarks/runtime.py
```
