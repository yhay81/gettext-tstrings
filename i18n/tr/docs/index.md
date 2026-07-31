---
description: "Tam t-string mesajlarını gettext ve Babel üzerinden çevirin; biçimlendirme katalogdan uzak tutulur."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Cümleyi bir kez yaz.<br>Bütün olarak çevir.

Python 3.14+ t-string'leri için güvenli gettext ve Babel entegrasyonu — değer
yerinde kalır, katalog ise mesajın tamamını görür:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Öğreticiye başla :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Neden t-string?](comparison.md){ .md-button }

Bu site belgelediğini bizzat uygular: her dil sürümü — gezinme,
etiketler ve çoğula duyarlı derleme raporu —
[`gettext-tstrings`'in kendisi](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
tarafından PO kataloglarından render edilir.
{ .home-hero-note }

</div>

Katalog, `Hello {name}` cümlesinin tamamını alır. Bir çeviri `{name}` yer
tutucusunu yeniden sıralayabilir ya da yineleyebilir; onu atamaz, yenisini
uyduramaz ve kendi biçimlendirmesini ekleyemez — bu kütüphane bunu denetler ve
bozuk bir katalog çökmek yerine kaynak metne geri düşer.

!!! note "gettext'e yeni misiniz? Tüm iş akışı dört cümlede"

    **gettext**, Python'da ve çok ötesinde, yazılımın çevrilmesinin standart
    yoludur. Kodunuz çevrilebilir dizgileri işaretler; bir *çıkarıcı* onları
    bir şablon dosyasında (`.pot`) toplar; çoğunlukla programcı olmayan bir
    çevirmen dil başına bir katalog dosyasını (`.po`) doldurur; bu dosya da
    uygulamanızın çalışma zamanında yüklediği ikili bir `.mo` dosyasına
    derlenir. Çeviri işlevinin geleneksel adı `_` olduğundan
    `_(t"Hello {name}")` "bu cümleyi çevir" diye okunur.
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

## Yaptığı seçim { #the-choice-it-makes }

- Cümle parçalarını değil, her zaman tam mesajları çevir.
- Yalnızca `{name}` gibi yalın değişken adlarını kabul et.
- `!r` ve `:.2f` gibi biçimlendirmeyi uygulamanın denetiminde, katalogdan
  uzakta tut.
- Çevirmenler bilinen yer tutucuları yeniden sıralayabilsin ve
  yineleyebilsin — ama öznitelik çağıramasın ve biçimlendirme davranışı
  ekleyemesin.
- Sıradan POT, PO ve MO dosyalarını ve onları zaten okuyan araçları yeniden
  kullan.

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

Buraya üç tür okur gelir: ilk programını çeviren biri, gerçek bir projeye
çeviri bağlayan biri ve mekanizmanın neden tam da bu biçimde olduğunu bilmek
isteyen biri. Her birinin bir yolu var.

**Öğrenmek için** — gettext deneyimi varsayılmaz:

<div class="grid cards" markdown>

- **[Öğretici](tutorial.md)** — buradan başlayın: boş bir dizinden çalışan bir
  Japonca çeviriye beş adımda, her komut çıktısıyla birlikte gösterilir.
- **[Neden t-string?](comparison.md)** — aynı mesajın dört farklı yazımı ve
  `%(name)s`, `.format()` ile `$`-dizgilerinin her birinin kataloğa neyi
  teslim ettiği.
- **[Arka Plan](background.md)** — bu kütüphanenin var olma nedeni: otuz
  yıllık gettext, iki PEP ve yanıtsız kapanan stdlib tartışması.

</div>

**Ciddi biçimde kullanmak için** — çalışma referansları:

<div class="grid cards" markdown>

- **[Kılavuz](guide.md)** — çalışma zamanı API'si: çoğullar, istek başına
  diller, ertelenmiş dizgiler ve bir katalog yanlış olduğunda olanlar.
- **[Çıkarma](extraction.md)** — `pybabel` referansı: yapılandırma, özel işlev
  adları ve elinizdeki araçların bu katalogları bedavaya nasıl doğruladığı.
- **[Üretimde](workflow.md)** — döngünün bir ekip tarafından işletilişi:
  güncelleme çevrimi, fuzzy girdiler, CI kapıları, çeviri platformları ve bir
  web uygulamasında istek başına diller.
- **[API](api.md)** — paketin dışa aktardığı her şey, tek sayfada.

</div>

**Anlamak için** — ilkelerden gerçekleştirime:

<div class="grid cards" markdown>

- **[Nasıl Çalışır](internals.md)** — PEP 750'nin template nesnesinden render
  edilmiş dizgiye ve denetimi ucuz kılan önbelleklere.
- **[Belirtim](spec.md)** — t-string ↔ msgid uzlaşımı; kararlı, sürümlenmiş
  bir sözleşme olarak, makine tarafından okunabilir bir uyumluluk paketiyle
  birlikte.

</div>

## Durum { #status }

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
