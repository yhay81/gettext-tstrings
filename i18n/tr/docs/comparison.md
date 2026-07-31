---
description: "Aynı çevrilebilir mesajın %-format, .format(), flufl.i18n $-dizgileri ve bir t-string ile yazılışı; her birinin değerleri nasıl bağladığı ve hasarlı bir katalogla nasıl başa çıktığı dahil."
---

# Neden t-string?

Çevrilebilir bir mesaja değer yerleştirmenin dört yolu, aynı cümle üzerinde
karşılaştırıldı. Kısa özet:

- **%-format** ile, bir çevirmenin tek bir harfi silmesi üretimde çökmeye
  dönüşür.
- **str.format** ile, bir çeviri kodunuzun aktardığı nesnelerin
  özniteliklerini — sırlar dahil — okuyabilir.
- **$-dizgileri** (flufl.i18n) ile, değerler çağıran işlevin değişkenlerinden
  örtük olarak çekilir ve noktalı yer tutucular da özniteliklere uzanır.
- **t-string'ler** ile, biçimlendirme kodunuzda kalır, çeviriler çalışma
  zamanında denetlenir ve bozuk bir katalog çökmek yerine kaynak metne geri
  düşer.

Sayfanın geri kalanı, her yöntemi tek tek ele alan kanıtlardır.

!!! note "Çevrilen her mesaja üç taraf dokunur"

    **Katalog**, çevirilerin dosyasıdır — insanlar düzenlerken `.po`,
    uygulamanın yüklemesi için `.mo` biçimine derlenir
    ([öğretici](tutorial.md) ikisini de adım adım gösterir). Her mesaja üç
    taraf dokunur: **geliştirici** kaynak dizgiyi yazar, bir **çevirmen**
    kataloğu düzenler — çoğu zaman her tür kod incelemesinden uzakta, harici
    bir platformda — ve **uygulama** ikisini çalışma zamanında birlikte render
    eder. Aşağıdaki her biçimlendirme tarzı aynı soruyu farklı yanıtlar:
    *biçim dilinin ne kadarını kataloğun denetlemesine izin verilir?*
    Örneklerde `_` çeviri işlevinin geleneksel adıdır; `tr` ise bu
    kütüphaneninki.

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Ne ters gidebilir: bir çeviride silinen tek bir harf render'ı çökertir.

Katalog dizgisi, printf sözdizimini taşır; buna gözden kaçırması ve zarar
vermesi kolay olan sondaki tür harfi — `%(name)s` içindeki `s` — da dahildir:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Bir PO editöründe yapılan tek karakterlik düzenleme, üretimde bir traceback'e
dönüşür. GNU `msgfmt --check-format` bunu yakalar, ama yalnızca
`python-format` işaretli mesajlar için ve yalnızca katalog uygulamanıza giden
yolda gerçekten msgfmt'ten geçiyorsa.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Bu yöntem, adlandırılmış ve serbestçe yeniden sıralanabilir bir yer tutucuyu
korurken sondaki tür harfini kaldırır. Ters gidebilecek olan şey, alışverişin
öbür tarafına geçer: çeviri, nesneleriniz üzerinde güç kazanır.

`str.format` küçük bir ifade dilidir ve onu bir dizgi üzerinde çağırmak, o
dizgiye bu dili kullanma hakkını vermek demektir:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Şimdi bu değişmez dizgilerin yerine `_()` işlevinin döndürdüğü herhangi bir
şeyi koyun. `Hello {name}` mesajının çevirisi `{conf.api_key}` olarak geri
gelirse, onu render etmek API anahtarınızı yazdırır — neyin okunacağına
kodunuz değil, katalog karar vermiştir. Bir katalog kod değildir, ama veri
gibi yolculuk eder: bir çeviri platformuna gider, birkaç elden geçer, `.po`
olarak döner, `.mo` biçimine derlenir, bazen tamamen projenizin dışından
vendor'lanır. `.format()`, bu yolculuğun her aşamasına, aktardığınız nesneler
üzerinde öznitelik erişimi verir.

## `$`-dizgileri ve flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

`$name` interpolasyon dilini standart kütüphanenin
[`string.Template`][stdlib-template] sınıfı sağlar, ama bu sınıf kendi başına
bir çeviri API'si değildir. [`flufl.i18n`][flufl-i18n], o tarzı gettext
katalog aramasıyla birleştirir. Değerin hiçbir zaman içeri aktarılmadığına
dikkat edin: flufl.i18n, yerine koyma ad alanını çağıranın global ve yerel
değişkenlerinden kurar — çağrı noktasında var olan değişkenler mesajın
kullanımına açıktır. İsteğe bağlı bir `extras` eşlemesi her ikisinin de önüne
geçer. Çevirmene dönük sözdiziminde sonda tür harfi ya da biçim belirteci
yoktur ve yer tutucular serbestçe yeniden sıralanabilir.

Çözülemeyen bir yerine koyma hata fırlatmaz. `name = "Ada"` varken ve
çağıranın ad alanında `nombre` yokken, katalogdaki `Hello $nombre` çevirisi
`Hello $nombre` olarak render edilir: çözülmemiş yer tutucu görünür kalır. Bu
[belgelenmiş davranış][documented behavior], çağrıyı başarısız kılmak yerine
çevrilen mesajın geri kalanını korur. Bir özniteliği çözerken ya da bir değeri
dönüştürürken fırlatılan istisnalar yine de yayılabilir.

`flufl.i18n`, konumuzla ilgili bir noktada yalın bir `string.Template`'ten
daha yeteneklidir. [Özel Template][custom Template] sınıfı
`$settings.api_key` gibi noktalı yer tutucuları kabul eder ve
[translator][translator] bileşeni bu yolları çağıranın değerleri üzerinde
çözer. Çevrilmiş bir yer tutucu, erişilebilir herhangi bir çağıran yerel ya da
global değişkenini adlandırabilir ve noktalı sözdizimiyle onun
özniteliklerinde gezinebilir. Bu, bir mesajın bir özniteliğe ihtiyaç duyduğu
durumda kullanışlıdır; ama aynı zamanda çağıranın çerçevesini kataloğun
yerine koyma ad alanının parçası yapar. Aşağıdaki karşılaştırma
`flufl.i18n` 6.0.0'ı anlatır, `string.Template`'in olası her kullanımını
değil.

Ayrıca diğer iki biçimlendirme tarzının tümüyle uygulamaya bıraktığı bir
soruyu da yanıtlar: *hangi* dil geçerlidir ve nasıl değiştirilir. Bir
[uygulama nesnesi][application object] bir diller yığını tutar; `_.push(code)`
ile `_.pop()` yığını hareket ettirir, `with _.using(code):` iç içe geçmeyi
sağlar ve bir [strateji][strategy] bir dil koduna karşılık gelen kataloğu
bulur; böylece uygulama katalog nesneleriyle kendisi hiç uğraşmaz. Tek bir iş
birimi içinde birden fazla dilde metin üretmek zorunda olan bir sunucu — okur
için bir sayfa, dili farklı ayarlanmış birinin hesabı için bir bildirim — bu
düzeneğin var oluş nedenidir.

Yığın, tüm sürecin paylaştığı o uygulama nesnesinin üzerinde durur.
Dolayısıyla üst üste binen iki istek tek bir yığını paylaşır ve *zaman
içinde* tam olarak iç içe geçmeyen bloklar birbirine yanlış dili devreder:

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

Bu kütüphane aynı yeteneği korur — bağlamalar aynı şekilde iç içe geçer ve
geri sarılır — ama onu paylaşılan bir yığında değil bir `ContextVar` içinde
tutar; böylece yukarıdaki geçişme görev başına çözülür. Eşdeğerleri
[Aynı anda birden fazla dil](guide.md#several-languages-at-once) başlığında.
Sağlamadığı şey, dil kodundan kataloğa uzanan aramadır: bir çeviri nesnesi
geçirirsiniz — yaygın durumda bu tek bir `gettext.translation()` çağrısıdır —
ve ayrıştırılmış kataloğu standart kütüphane önbelleğe alır.

## t-string'ler { #t-strings }

```python
tr(t"Hello {name}")
```

Katalog yine `Hello {name}` görür ve sıradan bir PO/MO kataloğu olarak kalır.
Fark, bir çevirinin *ne söylemesine izin verildiği* ve bunu kimin
denetlediğidir.

Bu kütüphane her çeviriyi render'dan önce kaynak mesajın yer tutucularına
karşı doğrular ve yalın adlar dışında hiçbir şeyi kabul etmez.
`t"Hello {name}"` karşısında:

| Şunu içeren bir çeviri | şu gerekçeyle reddedilir |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Reddedilmek çökmek demek değildir: kütüphane varsayılan olarak bir uyarı
günlükler ve kaynak metni render eder; böylece kötü bir katalog uygulamayı
asla düşürmez —
[gettext'in kendi tuttuğu sözleşmenin aynısı](guide.md#what-happens-when-a-catalog-is-wrong).

Biçimlendirme, yazıldığı yerde, kodda kalır:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` kataloğa asla ulaşmaz; dolayısıyla hiçbir çeviri onu değiştiremez ve
hiçbir çevirmen ona bakmak zorunda kalmaz.

Bir fark daha araç desteğindedir: t-string'ler yeni bir sözdizimi olduğundan,
onları bir `.pot` dosyasına çıkarmak şimdilik t-string'lerden anlayan bir
çıkarıcı gerektirir; bu paketin [Babel için sağladığı](extraction.md) gibi.

## Yan yana { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Yer tutucu adlandırılmış mı? | evet | evet | evet | evet |
| Çevirmen yer tutucuları yeniden sıralayabilir mi? | evet | evet | evet | evet |
| Değerler nereden gelir? | açık bir eşlemeden | açık argümanlardan | çağıranın yerel ve global değişkenlerinden, artı isteğe bağlı `extras` | t-string içinde yakalanan değerlerden |
| Katalog bir değerin nasıl biçimlendirileceğini değiştirebilir mi? | evet | evet | hayır | hayır |
| Katalog nesnelerin içine uzanabilir mi (öznitelik erişimi)? | hayır | evet | evet, noktalı adlarla | hayır |
| Bir çeviri bir yer tutucuyu *düşürürse* — ne render edilir? | değer sessizce kaybolur | değer sessizce kaybolur | değer sessizce kaybolur | kaynak metin, bir uyarıyla ([varsayılan olarak](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Bir çeviri bilinmeyen bir yer tutucu *eklerse* — ne render edilir? | bir istisna | bir istisna | yer tutucu metin olarak görünür kalır | kaynak metin, bir uyarıyla ([varsayılan olarak](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Yer tutucular render anında denetlenir mi? | hayır | hayır | hayır | evet (aşağıya bakın) |
| Babel hangi PO bayrağını çıkarsar, mevcut araçlar doğrulasın diye? | `python-format` | `python-brace-format` | hiçbiri | `python-brace-format` |
| Sıradan PO/MO katalogları kullanır mı? | evet | evet | evet | evet |
| Özel bir kaynak çıkarıcı gerekir mi? | hayır | hayır | hayır | evet, şimdilik |
| "Geçerli dil" nerede durur? | uygulama nereye koyarsa orada | uygulama nereye koyarsa orada | paylaşılan uygulama nesnesi üzerindeki bir dil kodu yığınında | bir `ContextVar` içinde, görev ya da istek başına |

Render anındaki denetim üzerine: tekil mesajlar yer tutucuların birebir
eşleşmesi bakımından denetlenir. Çoğul mesajlar da denetlenir; hedef dilin
çoğul biçimlerinin kaynağınkinden farklı olmasına izin veren
[birleşim/kesişim kuralına](spec.md) karşı. Biçim başına daha katı denetim ise
kataloglar derlenirken çalışır ([Çıkarma](extraction.md)).

Biçim bayrağı satırı, katalog uyumluluğunu değil, yer tutuculardan haberdar
doğrulamayı anlatır. `hiçbiri`, standart gettext araçlarının mesajı yine de
okuyup derlediği, ama `msgfmt --check-format`ın uygulayacak bir
`$`-yer-tutucu dil bilgisi olmadığı anlamına gelir.

## Bedeli { #what-it-costs }

Bir f-string bu şekilde hiç kullanılamaz — herhangi bir kütüphane onu
gördüğünde çoktan bitmiş bir dizgidir; dolayısıyla onu çevirmek bir parçayı
çevirmek demektir. t-string'ler ([PEP 750]) f-string benzeri sözdizimini ve
açık değer bağlamayı korurken statik metinle değerleri ayrı tutar.
`$`-dizgileri, farklı bir bağlama ve hata modeliyle zaten kısa ve öz bir
alternatif sunar. `flufl.i18n`, Python 3.10 ve sonrasında çalışan olgun bir
pakettir; `gettext-tstrings` şu anda bir alfadır ve t-string'ler yeni bir
sözdizimi olduğundan Python 3.14 veya daha yenisini gerektirir.

Diğer bedel, kısıtlamanın kendisidir: bir interpolasyon yalın bir ad olmak
zorundadır.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Bu gerçek bir kısıttır. Kaynak tarafında değer bağlama ve çalışma zamanında
yer tutucu denetimiyle birlikte, katalog dizgilerinin ifade değerlendirmesini
engeller ve yer tutucu adlarını anlamlı tutar.

Python'un bu yol ayrımına nasıl geldiği — on yıl arayla iki PEP ve yanıtsız
kapanan stdlib tartışması — kaynaklarıyla birlikte
[Arka Plan](background.md) sayfasında anlatılıyor.

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
