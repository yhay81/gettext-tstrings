---
description: ".po dosyalarını düzenleyen kişi için yer tutucu sözleşmesi: neyi değiştirebilirsiniz, neye dokunmamalısınız ve hataları nasıl okursunuz."
---

# Çevirmenler için

Bu sayfa, kodu yazan kişi için değil, kataloğu düzenleyen kişi içindir. Bilerek
kısadır ve bir projenin kendi çevirmen yönergelerine bağlanmak ya da
kopyalanmak üzere düşünülmüştür.

Buradaki hiçbir şey Python okumanızı gerektirmez. Buradaki her şey tek bir
konuyla ilgilidir: bir mesajın küme ayraçları içindeki parçaları.

## Yer tutucu nedir { #what-a-placeholder-is }

Bir katalogdaki mesaj, küme ayraçları içinde adlar taşıyabilir:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` bir **yer tutucudur**. Program bu mesajı gösterirken `{name}` yerine
kendi sağladığı bir değeri koyar — bir kişi adı, bir dosya adı, bir sayı. Yer
tutucu çevrilecek bir sözcük değildir; bir yuvadır.

Çeviriniz `msgstr` içine gider ve o yuvayı korumak zorundadır:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Neyi değiştirebilirsiniz, neyi değiştiremezsiniz { #what-you-may-change-and-what-you-may-not }

Şunları **yapabilirsiniz**:

- **Bir yer tutucuyu taşımak**: hedef dilin dil bilgisi nereyi istiyorsa oraya,
  mesajın en başı dahil.
- **Bir yer tutucuyu yinelemek**: dil değeri iki kez gerektiriyorsa.
- **Diğer her sözcüğü yeniden yazmak**: noktalama, boşluk ve cümle sırası dahil.

Şunları **yapmamalısınız**:

- **Ayraçların içindeki adı çevirmek.** `{name}`, başka hiçbir şeyi Latin
  harfleriyle yazmayan bir dilde bile `{name}` olarak kalır.
- **Ayraçları kaldırmak** ya da adı onlarsız yazmak.
- **ASCII `{` `}` ayraçlarını tam genişlikli `｛` `｝` ile değiştirmek.** Birçok
  giriş yöntemi tam genişlikli biçimleri üretir; neredeyse birebir aynı
  görünürler ve çalışmazlar.
- **Biçimlendirme eklemek**, örneğin `{name!r}` ya da `{amount:.2f}`. Bir
  değerin nasıl gösterileceğine katalogda değil, programda karar verilir.
- **`msgid` içinde olmayan bir yer tutucu uydurmak.**

Bir mesaj, aslının sunmadığı bir değere ihtiyaç duyuyorsa, bu geliştiricinin
değiştirmesi gereken bir mesajdır. Etrafından dolaşmak yerine bunu söyleyin.

## Çoğul biçimler { #plural-forms }

Sayılı bir mesaj, dilinizdeki her çoğul biçim için bir `msgstr` yuvasıyla gelir
ve bunun kaç tane olduğuna diliniz karar verir — Japoncada bir, Almancada iki,
Rusçada üç, Arapçada altı. Kataloğun size verdiği her yuvayı doldurun.

İnsanları yanıltan iki kural:

- **Yuvalar "tekil, çoğul, daha çoğul" değildir.** Her indeks, dilinizin çoğul
  kuralı ne diyorsa onu ifade eder. Letoncanın üçüncü biçimi yalnızca sıfır
  içindir; Slovencenin ikincisi tam olarak iki içindir; Galce genel durumu 0.
  indekse, tekili 1. indekse koyar.
- **İki yuva haklı olarak aynı metni tutabilir.** Türkçede, Macarcada, Farsçada
  ve Bengalcede bir ad, sayıdan sonra tekil kalır; dolayısıyla sayılı bir
  mesajın her iki biçimi de aynı dizgidir. Bu doğrudur, bir kopyala-yapıştır
  hatası değil.

Yukarıdaki yer tutucu kuralları her biçime ayrı ayrı uygulanır.

## Fuzzy girdiler { #fuzzy-entries }

`fuzzy` işaretli bir girdi, bir makinenin tahminidir: geliştirici özgün mesajı
değiştirmiş ve araçlar, başlayacak bir yeriniz olsun diye yeni metni eski
çevirinizle eşleştirmiştir.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Fuzzy bir girdi, biri metni gözden geçirip `fuzzy` işaretini kaldırana dek
**program tarafından kullanılmaz** — onun yerine çevrilmemiş özgün metin
gösterilir. Çoğu PO editöründe tam olarak bunun için bir düğme vardır.

## Bir hata mesajını okumak { #reading-a-failure-message }

Araçlar, katalog derlenirken yer tutucuları denetler ve mesaj bir programcı
için değil, sizin için yazılmıştır. O karakterleri gözünüzün önünde
görebiliyorken yalnızca `{name}` eksik demek çıkmaz sokaktır; bu yüzden bir yer
tutucu var gibi görünüp de yoksa, mesaj nedenini söyler. `Hello {name}` özgün
metni karşısında, aşağıdakilerin her biri
`translation does not match the source placeholders:` başlığı altında
raporlanır:

| Çeviriniz şöyle diyor | Verdiği gerekçe |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Görülemeyen karakterler kendi muamelesini görür. Ayraçların içindeki bölünmesiz
boşluk, bir giriş yönteminin ürettiği ve hiçbir editörün göstermediği bir
şeydir; bu yüzden mesaj, asla bulamayacağınız bir karakteri adlandırmak yerine
onu kod noktasıyla yazdırır:

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

Aynı belirsizlik giderme, tamamı tek bir yazı sistemiyle yazılmış Yunanca ya da
Kiril bir adın ASCII bir kaynak adla çakıştığı durumda da uygulanır; tek
harflik Latin `a` / Kiril `а` durumu dahil.

Bunlardan biriyle karşılaşırsanız ve düzeltmesi apaçık değilse, güvenli hamle
yazdığınız yer tutucuyu silip `msgid` içindekini kopyalamaktır.

## Denetimlerin yapamadıkları { #what-the-checks-cannot-do }

Araçlar, yer tutucularınızın sağlam olduğunu doğrular. Çevirinin doğru, akıcı
ya da bağlama uygun olup olmadığını söyleyemezler — o tamamen size kalır.

Her denetimden çok işe yarayan iki şey:

- **Çevirmen yorumunu okuyun.** Mesajın üstünde `#.` ile başlayan bir satır,
  geliştiricinin size mesajın nerede göründüğünü ve ne anlama geldiğini
  anlatmasıdır.
- **`msgctxt` hakkında soru sorun.** Aynı sözcük farklı bağlamlarla iki kez
  görünüyorsa, bunun nedeni ikisinin farklı çevrilmesi gerektiğidir — örneğin
  düğme olan "Open" ile durum olan "Open".
