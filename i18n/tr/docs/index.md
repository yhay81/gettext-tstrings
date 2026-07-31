---
description: "Tam t-string mesajlarını gettext ve Babel üzerinden çevirin; değerler de biçimlendirme de katalogdan uzak tutulur."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Eksiksiz mesajları<br>Python t-string'leriyle çevirin

`gettext-tstrings`, Python 3.14+ t-string'lerini standart gettext kataloglarına
ve Babel araçlarına bağlar. Değerler ve biçimlendirme uygulama kodunda kalır;
çevirmenler ise eksiksiz mesajlarla ve yalın `{name}` yer tutucularıyla çalışır:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Katalog `Hello {name}` mesajını tutar. Bir çeviri `{name}` yer tutucusunu
taşıyabilir ya da yineleyebilir. Onu atarsa, adını değiştirirse ya da yeniden
biçimlendirirse, katalog doğrulaması hatayı bildirir. Geçersiz bir girdi yine de
üretime ulaşırsa, kütüphane bir uyarı kaydeder ve çökmek yerine kaynak mesajı
render eder.

[Beş dakikalık öğreticiye başla :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Alternatifleri karşılaştır](comparison.md){ .md-button }

Alfa · Python 3.14+ · standart PO/MO katalogları · üçüncü taraf çalışma zamanı bağımlılığı yok
{ .home-facts }

Bu site belgelediğini bizzat uygular: her dil sürümü — gezinme,
etiketler ve çoğula duyarlı derleme raporu —
[`gettext-tstrings`'in kendisi](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
tarafından PO kataloglarından render edilir.
{ .home-hero-note }

</div>

## Bu size göre mi? { #is-this-for-you }

**Bugün uygun bir seçim:** uygulamanız Python 3.14 ya da daha yenisinde
çalışıyorsa; gettext ile Babel'i zaten kullanıyor ya da onların PO/MO iş
akışını benimsemek istiyorsanız; ve render edilmeden önce denetlenen
adlandırılmış yer tutucularıyla t-string sözdizimi istiyorsanız.

**Henüz uygun değil:** Python 3.13 ya da daha eskisine ihtiyacınız varsa;
kararlı bir Python API'si gerekiyorsa — bu bir alfa ve [belirtim](spec.md)
onun oturmuş olan parçası; ya da çevrilebilir metninizin neredeyse tamamı
Python kaynağında değil bir şablon dilinde yaşıyorsa.

Elinizde zaten katalog var mı? Çalışmaya devam ederler.
`_("Hello {name}").format(name=name)` ile `tr(t"Hello {name}")` aynı msgid'yi
üretir; yani geçişte mevcut çeviriler korunur — [Geçiş](migration.md)
taşınmanın tamamını adım adım anlatır.

## Kataloğun söyleyebilecekleri { #what-the-catalog-may-say }

**Bir çeviri, çevirdiği mesajın yapısını değiştiremez.** Verilen söz bundan
ibaret ve bu sitenin geri kalanı ondan çıkar. Bir çeviri `{name}` yer tutucusunu
yeniden sıralayabilir ya da yineleyebilir ve çevresindeki her sözcüğü yeniden
yazabilir. Yer tutucuyu atamaz, yenisini uyduramaz, onun üzerinden
nesnelerinize uzanamaz ve kendi biçimlendirmesini iliştiremez.

Kütüphane bunu girişte — kataloglar derlenirken — ve bir kez daha render anında
denetler; incelemede yakalanan bir hata ile kullanıcının yakaladığı bir hata
arasındaki fark da budur.

!!! note "gettext'e yeni misiniz? Tüm iş akışı dört cümlede"

    **gettext**, Python'da ve çok ötesinde, yazılımın çevrilmesinin standart
    yoludur. Kodunuz çevrilebilir mesajları işaretler; bir *çıkarıcı* onları
    bir şablon dosyasında (`.pot`) toplar; çoğunlukla programcı olmayan bir
    çevirmen dil başına bir katalog dosyasını (`.po`) doldurur; bu dosya da
    uygulamanızın çalışma zamanında yüklediği ikili bir `.mo` dosyasına
    derlenir. Çeviri işlevinin geleneksel adı `_` olduğundan
    `_(t"Hello {name}")` "bu mesajı çevir" diye okunur.
    **[Öğretici](tutorial.md)** tüm yolu — işaretle, çıkar, çevir, derle,
    çalıştır — yaklaşık beş dakikada baştan sona yürür.

## Çözdüğü problem { #the-problem-it-solves }

Bir f-string, herhangi bir kütüphane onu görmeden önce çoktan interpolasyona
uğramıştır — `f"Hello {name}"` artık `"Hello Ada"` olmuştur ve bir değerin
çevresindeki parçaları tek tek çevirmek çoğu dilin dil bilgisini bozar. Bir
t-string ([PEP 750]) statik metni, hesaplanan değerleri, kaynak ifadeleri,
dönüşümleri ve biçim belirtimlerini ayrı tutar — bu da tam olarak bir mesaj
kataloğunun ihtiyaç duyduğu ayrımdır.
`%(name)s`, `.format()` ve `$`-dizgileriyle karşılaştırıldığında
[bunun neyi değiştirdiği](comparison.md).

Ne var ki gettext'te de Babel'de de bir t-string'in nasıl mesaja dönüşeceğini
söyleyen hiçbir şey yoktur. Bu kütüphane o seçimi yapar, onu
[sürümlenmiş bir belirtim](spec.md) olarak yazıya döker ve denetlemek için
[uyumluluk paketini](spec.md#conformance) birlikte sunar.

## Tasarım kuralları { #the-design-rules }

- Cümle parçalarını değil, her zaman tam mesajları çevir.
- Yalnızca `{name}` gibi yalın değişken adlarını kabul et.
- `!r` ve `:.2f` gibi biçimlendirmeyi uygulamanın denetiminde, katalogdan
  uzakta tut.
- Çeviriler bilinen yer tutucuları yeniden sıralayabilsin ve
  yineleyebilsin — ama özniteliklere uzanamasın ve biçimlendirme ekleyemesin.
- Sıradan POT, PO ve MO dosyalarını ve onları zaten okuyan araçları yeniden
  kullan.

Ve bilerek dokunmadığı şeylerin listesi: sayıları, para birimlerini ya da
tarihleri yerelleştirmez — [önce onları biçimlendirin](guide.md#locale-aware-values),
Babel ile; render edilen çıktıyı HTML, kabuk ya da terminal için kaçışlamaz;
ve bir çevirinin *doğru* olup olmadığına karar veremez, yalnızca yer
tutucularının sağlam olup olmadığına.

## Kurulum { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 veya daha yenisi. **Render'ın hiçbir bağımlılığı yoktur** —
standart kütüphanenin `gettext` modülünü kullanır, başka hiçbir şey kullanmaz.

Çıkarma ve katalog doğrulaması [Babel] üzerinden yürür; bu yüzden o ekstrayı
`pybabel`in çalıştığı yere kurun — bu da genellikle üretim imajı değil, bir
geliştirme ya da CI ortamıdır:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Sonraki adımlar { #where-to-go-next }

**Buradan başlayın** — gettext deneyimi varsayılmaz:

<div class="grid cards" markdown>

- **[Öğretici](tutorial.md)** — boş bir dizinden çalışan bir Japonca çeviriye
  beş adımda, her komut çıktısıyla birlikte gösterilir.
- **[Neden t-string?](comparison.md)** — aynı mesajın dört farklı yazımı ve
  `%(name)s`, `.format()` ile `$`-dizgilerinin her birinin kataloğa neyi
  teslim ettiği.

</div>

**Kullanın** — çalışma referansları:

<div class="grid cards" markdown>

- **[Kılavuz](guide.md)** — çalışma zamanı API'si: hangi giriş noktasını
  seçeceğiniz, çoğullar, istek başına diller, ertelenmiş dizgiler ve bir
  katalog yanlış olduğunda olanlar.
- **[Çıkarma](extraction.md)** — `pybabel` referansı: yapılandırma, özel işlev
  adları ve elinizdeki araçların bu katalogları bedavaya nasıl doğruladığı.
- **[Üretimde](workflow.md)** — döngünün bir ekip tarafından işletilişi:
  güncelleme çevrimi, fuzzy girdiler, CI kapıları, çeviri platformları ve
  sevkiyat.
- **[Geçiş](migration.md)** — bunu, elinde zaten katalog bulunan bir projede,
  çağrı noktası çağrı noktası benimsemek.
- **[Çevirmenler için](translators.md)** — `.po` dosyalarını dolduran kişiye
  uzatılacak tek sayfa.

</div>

**Anlayın** — tarihten gerçekleştirime:

<div class="grid cards" markdown>

- **[Arka Plan](background.md)** — bu kütüphanenin var olma nedeni: otuz
  yıllık gettext, iki PEP ve yanıtsız kapanan stdlib tartışması.
- **[Tuzaklar](pitfalls.md)** — bu siteyi otuz beş dile çevirmenin gerçekte
  neleri bozduğu ve bunların hangi yarısını bir araç yakalayabiliyor.
- **[Nasıl Çalışır](internals.md)** — PEP 750'nin template nesnesinden render
  edilmiş dizgiye ve denetimi ucuz kılan önbelleklere.

</div>

**Başvuru** — sözleşmeler:

<div class="grid cards" markdown>

- **[API](api.md)** — paketin dışa aktardığı her şey, tek sayfada.
- **[Belirtim](spec.md)** — t-string ↔ msgid uzlaşımı; kararlı, sürümlenmiş
  bir sözleşme olarak, makine tarafından okunabilir bir uyumluluk paketiyle
  birlikte.

</div>

## Durum { #status }

| | |
| --- | --- |
| Paket sürümü | 0.1.0a8 |
| API kararlılığı | alfa — Python API'si henüz değişebilir |
| [Belirtim](spec.md) | v1, bir [uyumluluk paketi](spec.md#conformance) ile |
| Python | 3.14 ve üstü; 3.14, 3.14t (serbest iş parçacıklı) ve 3.15 üzerinde test edildi |
| Babel | 2.18 ya da üstü, ve yalnızca `pybabel`ın çalıştığı yerde |
| Çalışma zamanı bağımlılıkları | yok — standart kütüphanenin `gettext`i |
| Katalog biçimi | sıradan POT, PO ve MO |
| Değişiklikler | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Bir alfa. Sözleşme bilerek küçük tutuldu ve [belirtim](spec.md) onun kararlı
parçası; Python API'si henüz değişebilir. Kararlı bir sürümden önce daha geniş
dil fikstürleri, sürekli performans takibi, gettext ve Babel'i ciddi biçimde
kullananlardan API incelemesi ve desteklenen her Python ve Babel sürümüyle
uyumluluk testleri gerekiyor.

[Issue'lar ve pull request'ler](https://github.com/yhay81/gettext-tstrings/issues)
memnuniyetle karşılanır — arayüz üzerine tartışmanın hâlâ değerli olduğu dönem
tam da alfa dönemidir.

## Topluluğa katılın { #join-the-community }

- Sınırları belli bir katkı için bir
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  seçin.
- Kullanım sorularını
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a)
  bölümünde sorun.
- Üretimdeki gettext iş akışlarınızı ve API fikirlerinizi
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas)
  bölümüne getirin.
- Pull request açmadan önce
  [katkı kılavuzunu](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  okuyun.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
