---
description: "Otuz yıllık gettext, on yıl arayla iki PEP ve 'planlanmadı' diye kapanan stdlib tartışması: bu kütüphanenin var olma nedeni, kaynaklara bağlantılarla."
---

# Arka Plan

Bu kütüphane, iki uzun hikâyenin — biri yazılımın nasıl çevrildiği, öteki
Python'un dizgileri nasıl interpolasyona uğrattığı hakkında — kesişme
noktasında durur; iki hikâye nihayet 2025'te kesişti ve tam da küçük, özenli
bir uzlaşımın gerektiği noktada durakladı. Bu sayfa iki hikâyeyi de
kaynaklara bağlantılarla anlatır, çünkü bu sitedeki tasarım kararları,
yanıtladıkları soruları görebildiğinizde daha kolay değerlendirilir.

## gettext ekosistemi { #the-gettext-ecosystem }

[GNU gettext], 1990'ların ortasından beri özgür yazılımın çevrilme biçimidir:
dizgileri kodda işaretle, bir şablona çıkar, çevirmenlere dil başına bir
katalog dosyası ver, derle, çalışma zamanında yükle. Bu döngünün çevresinde
koca bir ekosistem büyüdü — hepsi aynı dosya formatını konuşan PO editörleri,
inceleme iş akışları ve çeviri platformları — ve Python, yirmi yılı aşkın
süredir standart kütüphanesinde bir [`gettext` modülü][stdlib-gettext]
barındırıyor. Çevirinin çalışma zamanı yarısı hiçbir zaman sorun olmadı.

Çözülmemiş yarı, her zaman *katalog dizgisinin neye benzediğiydi*. Bir
`%(name)s` mesajı çevirmenlere printf sözdizimi teslim eder; silinen tek bir
harf onu üretim çökmesine çevirir. Bir `.format()` mesajı ise kataloğa canlı
nesneler üzerinde öznitelik erişimi teslim eder.
([Neden t-string?](comparison.md) ikisini de, hataları göstererek anlatır.)
Ve f-string'ler — bugün çoğu Python kodunun tercih ettiği sözdizimi — hiç
katılamaz: herhangi bir kütüphane birini gördüğünde, o çoktan bitmiş bir
dizgidir. İnsanlar yine de deniyor; öyle sık ki Babel'in issue takipçisi bu
girişimleri biriktiriyor ([#594][babel-594], [#715][babel-715]); başarısızlık
yapısaldır, eksik bir özellik değildir.

## On yıl arayla iki PEP { #two-peps-ten-years-apart }

2015'te Alyssa Coghlan ve Nick Humrich, belirtilen ilk motivasyonu i18n olan
— PEP'in kendi sözleriyle "i18n çevirisi için daha temiz bir sözdizimi
sağlamak" — interpolasyon şablonlarını öneren [PEP 501]'i yazdı. Öneri
ertelendi; kısmen, tartışmanın i18n durumunun daha basit kullanım
senaryolarının taşımadığı önemli ek kaygılar taşıdığını göstermesi yüzünden.

On yıl sonra, [PEP 750] — Jim Baker, Guido van Rossum, Paul Everitt, Koudai
Aono, Lysandros Nikolaou ve Dave Peck imzasıyla — fikri t-string'ler olarak
canlandırdı, [Nisan 2025'te kabul edildi][sc-resolution] ve Ekim 2025'te
[Python 3.14] ile yayımlandı. PEP 501 bunun üzerine onun lehine geri
çekildi. Bu sayfa için bir ayrıntı önemli: i18n, PEP 750'nin belirtilen
motivasyonları arasında *değildir*. PEP mekanizmayı genelleştirdi — her
kütüphanenin tüketebileceği bir template türü — ve çeviri sorusunu tam olarak
PEP 501'in on yıl önce bıraktığı yerde bıraktı: açıkta.

Yani Python 3.14 itibarıyla dil, bir mesaj kataloğunun ihtiyaç duyduğu veri
yapısının tam kendisine sahipti — ve onu öyle kullanmak için hiçbir uzlaşıma.

## Stdlib tartışması { #the-stdlib-discussion }

3.14 çıkmadan iki ay önce, Adrian Mönnich (ThiefMaster, Indico projesinin bir
bakımcısı) bu boşluğu standart kütüphanenin kendisinde kapatmayı önerdi:
discuss.python.org'daki [Support t-strings in gettext][discuss-thread]
başlığı, Ağustos 2025'te, hem `gettext`e hem `pygettext`e t-string desteği
ekleyen çalışır bir [pull request][cpython-pr] ile birlikte açıldı.

Başlık baştan sona okunmaya değer, çünkü bu kütüphanenin daha sonra
yanıtlamak zorunda kaldığı her zor soruyu su yüzüne çıkarır:

- **Bir interpolasyon ne olabilir?** Yalnızca yalın bir ad mı, yoksa türetilen
  bir yer tutucu adıyla öznitelikler ve çağrılar mı? Her yanıt, kullanışlılığı
  msgid kararlılığı ve katalog güvenliğiyle takas eder.
- **Çoğul biçimler ne gerektirir,** hedef dilin çoğul sistemi kaynağınkinden
  farklı olduğunda?
- **gettext doğru hedef mi ki?** PEP 750'nin geliştirilmesi sırasında
  t-string'lerin i18n için iyi bir uyum olmadığını savunmuş olan Barry
  Warsaw, daha dostane araç olarak kendi [`flufl.i18n`][flufl-i18n] paketini
  ve `$`-dizgi tarzını gösterdi; başkaları gettext'i tamamen geride bırakıp
  [Fluent] gibi daha yeni sistemlere geçmeyi savundu.
- **Ve üst-soru:** standart kütüphane ne yayımlarsa yayımlasın, o esasen bir
  daha asla değişemez. Bu kadar açık seçeneği olan bir uzlaşımı ilk denemede
  dondurmak riskli bir iştir.

Uzlaşı oluşmadı. CPython issue'su
["planlanmadı" olarak kapatıldı][cpython-issue] ve pull request, 3.14'ün
yayımlanmasından günler sonra, Ekim 2025'te birleştirilmeden kapatıldı.
Yetenek dilde vardı; uzlaşımın ise bir yuvası yoktu.

## Neden önce bir paket { #why-a-package-first }

Bu projenin standart kütüphanenin dışından doldurmayı seçtiği boşluk işte bu;
bilinçli bir bahisle: bir uzlaşım, serbestçe sürümlenebildiği ve benimsenmeyi
vaka vaka kazanabildiği yerde daha hızlı olgunlaşır ve ilk seferde doğru
olmak zorunda olan standart kütüphane, bir uzlaşımın *varması gereken* yerdir
— üzerinde çalışılacağı yer değil.

Somut olarak, başlıktaki her tartışmalı sorunun burada yazıya dökülmüş bir
yanıtı var, her biri kendi sayfasında:

- İnterpolasyonlar **yalnızca yalın adlardır**; böylece msgid'ler kararlı ve
  anlamlı kalır — [kılavuz](guide.md#safety-and-scope) kuralı gösterir,
  [Nasıl Çalışır](internals.md#from-template-to-msgid) nedenlerini.
- **Biçimlendirme katalogdan tamamen uzak durur**
  ([Neden t-string?](comparison.md)).
- **Çoğullar**, hedef dilin çoğul sisteminin kaynağınkinden farklı olmasına
  izin veren bir birleşim/kesişim kuralını izler ([spec §4](spec.md)).
- Bozuk bir katalog, gettext'in kendi sözleşmesini koruyarak **çökmek yerine
  geri düşer** ([kılavuz](guide.md#what-happens-when-a-catalog-is-wrong)).
- Ve uzlaşımın tamamı, makine tarafından okunabilir bir uyumluluk paketiyle
  birlikte [sürümlenmiş bir belirtimdir](spec.md) — öyle yazılmıştır ki başka
  bir gerçekleştirim, gelecekteki bir standart kütüphane gerçekleştirimi
  dahil, onu değiştirmeden benimseyip birlikte çalışabilsin.

Tartışma bitmedi ve bu proje onun bir katılımcısıdır, hakkında verilmiş bir
hüküm değil. Bu seçimleri ilgilendiren üretim gettext deneyiminiz varsa,
[aynı başlık][discuss-thread] ve bu deponun
[Discussions][gh-discussions] bölümü, tartışmanın yürütüldüğü yerlerdir.

## Zaman çizelgesi { #timeline }

| Ne zaman | Ne oldu |
| --- | --- |
| 1990'ların ortası | GNU gettext, çevirmenlerin ve platformların bugün hâlâ konuştuğu PO/POT/MO iş akışını kurar. |
| 2015 | [PEP 501], ilk motivasyonu i18n olan interpolasyon şablonlarını önerir; ertelenir. |
| 2016 | f-string'ler Python 3.6 ile çıkar — interpolasyon sözdizimine kavuşur ve çeviri onu kullanamaz. |
| Tem 2024 | [PEP 750] t-string'leri önerir. |
| Nis 2025 | PEP 750 [kabul edilir][sc-resolution]; PEP 501 onun lehine geri çekilir. |
| Ağu 2025 | [Support t-strings in gettext][discuss-thread] başlığı, bir stdlib [pull request'i][cpython-pr] ile açılır. |
| Eki 2025 | [Python 3.14] t-string'leri yayımlar; stdlib issue'su [planlanmadı][cpython-issue] olarak kapanır. |
| 2026 | `gettext-tstrings`, [spec v1](spec.md) ve uyumluluk paketiyle alfa olarak yayımlanır. |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
