---
description: "gettext_tstrings'in dışa aktardığı her ad: işlevler, Translator, bağlam bağlama, tembel dizgiler ve hatalar."
---

# API

Aşağıdaki her şey `gettext_tstrings` paketinden dışa aktarılır. Başka hiçbir
şey herkese açık değildir. Bu sayfa imza referansıdır; her işlevin işlenmiş
örnekleri için [kılavuza](guide.md) bakın.

## Çevirmek { #translating }

Her işlev t-string'ini konumsal olarak alır ve iki anahtar sözcük argümanı
kabul eder: `translations` (önce bağlam bağlamasına, sonra standart
kütüphanenin küresel işlevlerine geri düşer) ve `strict`
(bkz. [Kılavuz](guide.md#what-happens-when-a-catalog-is-wrong)).

| İşlev | İmza |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | `gettext`in takma adı |
| `ntr` | `ngettext`in takma adı |

### `Translator`

Tek bir çeviri nesnesini bağlayan dondurulmuş bir dataclass; böylece çağrı
noktaları onu yinelemez.

```python
Translator(translations, strict=False)
```

Çağrılabilirdir (`_(t"…")`) ve `gettext`, `ngettext`, `pgettext`,
`npgettext` ile `tr` / `ntr` takma adlarını taşır.

## Bağlam bağlama { #context-binding }

| Ad | Amaç |
| --- | --- |
| `use_translations(translations)` | Bir `with` bloğu süresince bağla, sonra eski durumuna döndür. |
| `set_translations(translations)` | Yaşam döngüsünü çatının yönettiği durumlar için bloksuz bağla. |
| `get_translations()` | Geçerli bağlamayı ya da `None` döndür. |

Bağlama bir `ContextVar`dır; dolayısıyla bağlam başınadır ve eşzamanlılık
altında güvenlidir.

## Ertelenmiş dizgiler { #deferred-strings }

| Ad | Amaç |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Çeviriyi her render'a kadar ertele. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Bağlamlı biçimi. |
| `LazyString` | İkisinin de döndürdüğü şey. `str()` ve `format()` üzerinden, o anda hangi dil bağlıysa o dilde render edilir, render edilmiş metniyle eşit karşılaştırılır ve bilerek hash'lenemez. |

`strict`in neden tanımın yanına ait olduğu da dahil olmak üzere işlenmiş
örnekler [Ertelenmiş çeviri](guide.md#deferred-translation) başlığı altındadır.

## Daha alt düzey { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Bir t-string'i, önbellekteki statik planını yeniden kullanarak derle.

### `CompiledTemplate`

| Üye | Anlamı |
| --- | --- |
| `.msgid` | Kararlı gettext mesaj tanımlayıcısı. |
| `.placeholders` | İlk görülme sırasıyla yer tutucu adları. |
| `.render(pattern)` | Tek bir deseni doğrula ve render et. Bir uyuşmazlıkta **her zaman hata fırlatır**. |

## Türler ve hatalar { #types-and-errors }

### `Translations`

Dört standart metot için, tümü yalnızca konumsal, `runtime_checkable` bir
`Protocol`:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` ve Babel'in
`Translations` sınıfı, hepsi bunu karşılar.

### İstisnalar

| Sınıf | Ne zaman fırlatılır |
| --- | --- |
| `TStringError` | Aşağıdaki ikisinin taban sınıfı. |
| `InvalidTemplateError` | **Kaynak** t-string uzlaşımı bozduğunda — karmaşık bir interpolasyon ya da farklı biçimlendirmeyle yinelenen bir ad. |
| `InvalidTranslationError` | **Çeviri** bozduğunda. Varsayılan hoşgörülü kipte bu günlüklenir ve yerine kaynak metin render edilir. |

## Çıkarma entry point'leri { #extraction-entry-points }

Kurulumda otomatik olarak kaydedilir; onlara import ile değil, adla
başvurursunuz.

| Grup | Ad | Kullanan |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `babel.cfg` içindeki `method`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, otomatik olarak. |

## Performans { #performance }

Tam anlatım — neyin önbelleğe alındığı, önbelleklerin neye anahtarlandığı ve
ölçülen sayılar — [Sıcak yol](internals.md#the-hot-path) bölümündedir. Kısa
sürümü: doğrulama önbelleğe alınır, asla atlanmaz ve render'ın tamamı
mikrosaniyenin kesri kadar sürer. Kıyaslamayı kendi hedefinizde çalıştırın:

```console
uv run python benchmarks/runtime.py
```
