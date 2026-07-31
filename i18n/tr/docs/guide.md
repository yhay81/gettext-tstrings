---
description: "Çalışma zamanı API'si: bir katalog bağlamak, istek başına diller, ertelenmiş dizgiler ve bozuk bir çevirinin nasıl raporlandığı."
---

# Kılavuz

Bu sayfa çalışma zamanı referansıdır: kataloglar var olduktan sonra *uygulama
kodunuzun* bu kütüphaneyle yaptığı her şey. Döngünün tamamını — işaretle,
çıkar, çevir, derle, çalıştır — henüz görmediyseniz, [öğretici](tutorial.md)
onu beş dakikada bir kez yürür; katalogların oluşturulması ve doğrulanması
[Çıkarma](extraction.md) sayfasında, bir ekibin döngüyü nasıl döndürdüğü —
güncelleme çevrimleri, CI, çeviri platformları — ise
[Üretimde](workflow.md) sayfasındadır.

## Bir katalog bağlamak { #binding-a-catalog }

Önerilen biçim, gettext'in sınıf tabanlı kullanımını yansıtır: standart bir
çeviri nesnesini bir kez bağlayın ve çağrılabilir işlemciyi `_` olarak
kullanın.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

Modül düzeyindeki işlevler, standart kütüphanenin adlarını ve yalnızca
konumsal çağrı uzlaşımını izler:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` ve `ntr`, `gettext` ile `ngettext`in birebir takma adlarıdır.

## İstek başına dil { #per-request-language }

Bir web çatısı dili istek başına seçer. İsteğin çevirilerini geçerli bağlama
bağlayın; modül düzeyindeki her çağrı, eşzamanlı istekler arasında güvenli
biçimde o dile çözülür:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)`, istek yaşam döngüsünü kendisi yöneten
çatılar için `with` bloğu olmadan bağlar; `get_translations()` geçerli
bağlamayı okur. Açık bir `translations=` argümanı her zaman bağlamın önüne
geçer ve bağlanmamış bir bağlam, standart kütüphanenin küresel olarak kurulu
gettext işlevlerine geri düşer. Flask ve ASGI ara katmanı için işlenmiş
örnekler [Üretimde](workflow.md#binding-a-language-at-runtime) sayfasındadır.

## Ertelenmiş çeviri { #deferred-translation }

Bir t-string değerlerini hevesle yakalar; bu, içe aktarma anında tanımlanan —
bir form etiketi, bir enum değeri, bir modül sabiti — ve *kullanıldığı* anda
etkin olan dilde render edilmesi gereken bir dizgi için yanlıştır.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

Bir `LazyString`, `str()`, `format()` ve f-string'ler üzerinden render edilir
ve render edilmiş metniyle eşit karşılaştırılır.

!!! note "Bilerek hash'lenemez"

    Bir `LazyString`'in metni etkin dile bağlıdır; dolayısıyla bir hash, dil
    değişiminde değişir ve onu tutan her set ya da dict'i sessizce bozardı.
    Bir anahtara ihtiyacınız varsa önce `str()` çağırın.

Çoğul biçimler çalışma zamanındaki bir sayıya bağlıdır; onları, sayının
bilindiği yerde `ngettext` ile hevesle render edin.

## Bir katalog yanlış olduğunda ne olur { #what-happens-when-a-catalog-is-wrong }

Bir çevirinin yer tutucuları kaynağa uymuyorsa — doğrulamadan sıyrılmış
eksik, bilinmeyen ya da yeniden biçimlendirilmiş bir alan; elle düzenlenmiş
bir MO'dan, bir tedarikçi kataloğundan ya da denetleyiciyi atlayan bir boru
hattından — varsayılan davranış, hata fırlatmak yerine kaynak metni yeniden
üretmektir. Bu, gettext'in kötü bir kataloğun uygulamayı asla bozmayacağı
yolundaki kendi sözleşmesini yansıtır.

`Hello {name}` mesajı `こんにちは {nombre}` olarak çevrilmişse render başarılı
olur ve `gettext_tstrings` günlükçüsüne bir uyarı düşer:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Uyarı her render'da değil, mesaj ve desen başına bir kez ateşlenir; böylece
bozuk bir katalog girdisi günlüğü boğmaz.

Testler ve CI için yüksek sesle başarısız olmayı tercih edin:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Aynı arama bu kez, "using source text" yarısı olmadan aynı cümleyi taşıyarak
hata fırlatır:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Bir hata mesajını okumak { #reading-a-failure-message }

Bu mesajlar, onlara müdahale edebilecek kişi için yazılmıştır; bu da bir
katalog sorununda çoğunlukla bir programcıdan çok bir çevirmendir. Okur o
karakterleri gözünün önünde görebiliyorken yalnızca `{name}` eksik demek
çıkmaz sokaktır; bu yüzden bir yer tutucu var gibi görünüp de yoksa, mesaj
nedenini söyler. `Hello {name}` kaynağı karşısında, aşağıdakilerin her biri
`translation does not match the source placeholders:` başlığı altında
raporlanır:

| Çeviri şöyle diyor | Verdiği gerekçe |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Görülemeyen karakterler kendi muamelesini görür. Ayraçların içindeki
bölünmesiz boşluk, bir giriş yönteminin ürettiği ve hiçbir editörün
göstermediği bir şeydir; bu yüzden mesaj, okurun bulamayacağı bir karakteri
adlandırmak yerine onu kod noktasıyla yazdırır:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Harfleri yazı sistemlerini karıştıran bir ad — Kiril `а` harfinin Latin
olanından ayırt edilemediği homoglif durumu — iki kez gösterilir: bir kez
okunur biçimde, bir kez kaçışlanmış olarak; ikisini birbirinden ayıran tek
biçim budur:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Aynı belirsizlik giderme, tamamı tek bir yazı sistemiyle yazılmış Yunanca ya
da Kiril bir adın ASCII bir kaynak adla çakıştığı durumda da uygulanır; tek
harflik Latin `a` / Kiril `а` durumu dahil.

## Katalogsuz bir deseni render etmek { #rendering-a-pattern-without-a-catalog }

`compile_template`, aynı mekanizmayı bir kat aşağıda açığa çıkarır: bir
t-string'i msgid'sine ve bağlı bir değer kümesine dönüştürür ve ona
verdiğiniz herhangi bir deseni render eder.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` aynı kurallarla doğrular ve bir uyuşmazlıkta **her zaman hata
fırlatır**. Burada hoşgörülü bir kip yoktur: hoşgörü, bir *katalog*
aramasının kaynak metne inebilmesi için vardır; kendi elinizle verdiğiniz bir
desenin inebileceği bir yer yoktur.

## Güvenlik ve kapsam { #safety-and-scope }

Bu geçerlidir:

```python
tr(t"Hello {name}")
```

Bunlar bilerek reddedilir:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Önce anlamlı bir değer hesaplayın:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Bu kısıtlama kararlı katalog anahtarları üretir, çevirmenlere işe yarar adlar
verir ve çevrilmiş bir dizginin bir ifade diline dönüşmesini engeller.

Güvence, *yapı ve biçimlendirmeyle* sınırlıdır: bir çeviri asla
değerlendirilmez ve asla öznitelik erişimi, çağrı, dönüşüm ya da biçim
belirtimi ekleyemez. İki şey, tıpkı stdlib gettext'te olduğu gibi, çağıranın
sorumluluğunda kalır — render edilmiş çıktıyı gideceği yere (HTML, kabuk,
terminal) göre **kaçışlamak** ve **katalog bütünlüğü**; çünkü düşmanca bir
katalog, çıktı boyutunu şişirmek için bir yer tutucuyu yineleyebilir; bu da
yer tutucu tabanlı her i18n'in doğasında vardır.
