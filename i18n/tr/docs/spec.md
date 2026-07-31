---
description: "t-string'den msgid'ye uzlaşım, makine tarafından okunabilir bir uyumluluk paketiyle birlikte küçük, sürümlenmiş bir sözleşme olarak."
---

# Belirtim

Bu kütüphaneyi bu sayfayı okumadan kullanabilirsiniz — günlük kullanımı
[öğretici](tutorial.md) ve [kılavuz](guide.md) karşılar. Bu sayfa araç
yazarları içindir: kütüphanenin gerçekleştirdiği uzlaşım, küçük ve kararlı
bir sözleşme olarak yazıya dökülmüştür; böylece başka bir gerçekleştirim —
bir çıkarıcı, bir IDE, bir tür denetleyicisi ya da gelecekteki bir
`pygettext` — onu hedefleyip birlikte çalışabilir. Aynı kuralların
gerekçeleriyle açıklanışı ve referans gerçekleştirimin onları nasıl yürüttüğü
için önce [Nasıl Çalışır](internals.md) sayfasını okuyun.

[Spec v1'i oku :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Kurallar tek ekranda { #the-rules-in-one-screen }

**Bir msgid**, değişmez parçaların ve interpolasyon başına bir `{name}`
belirtecinin kaynak sırasındaki birleşimidir. Değişmez ayraçlar kaçışlanır
(`{`, `{{` olur). Bir ad, yalın bir yer tutucu adı olmalıdır —
`str.isidentifier()` doğrudur ve bir Python anahtar sözcüğü değildir.
Dönüşümler ve biçim belirtimleri msgid'nin parçası **değildir**; uygulamanın
denetiminde kalırlar.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *reddedilir — yalın bir ad değil* |

**Bir çeviri**, yalnızca yalın `{name}` yer tutucuları içerdiğinde, zorunlu
her ad en az bir kez göründüğünde ve izin verilen kümenin dışında hiçbir ad
görünmediğinde geçerlidir. Yeniden sıralama ve yineleme bilerek serbesttir:
ikisi de hedef dilde dil bilgisi gereği olabilir.

Çoğullarda *izin verilen*, dalların adlarının birleşimi; *zorunlu* ise
kesişimleridir — böylece `t"One file"` ile `t"{n} files"` karşısında `n`, iki
biçimin de çevirmenine açık ama ikisinde de zorunlu değildir ve hedef dilin
çoğul kuralları kaynağınkinden farklı olabilir.

**Boş bir msgid** asla aranmaz, çünkü gettext onu kataloğun üstveri başlığı
için ayırır.

## Uyumluluk { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json),
aynı belgenin makine tarafından okunabilir biçimidir: bir t-string'in statik
yapısını bir msgid'ye ve bir msgid ile bir katalog desenini render edilmiş
bir dizgiye ya da bir redde eşleyen durumlar.

Bir gerçekleştirim, her durumu yeniden ürettiğinde **spec v1'e uyar**.
Durumlar yalnızca belirtimin tanımladığı şeyleri adlandırır — türetilmiş
msgid'ler, kabul ve ret gören desenler, render edilmiş çıktı — ve asla bir
hata mesajını ya da bir istisna türünü adlandırmaz; böylece başka bir dildeki
bir gerçekleştirim onları değiştirmeden çalıştırabilir.

İnterpolasyonlar, Python kaynağı olarak değil, her zaman yapısal olarak
betimlenir:

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

Referans gerçekleştirim, paketi kendi test paketinin bir parçası olarak
çalıştırır; böylece düzyazı ile kod sessizce birbirinden uzaklaşamaz.

## Sürümleme { #versioning }

Bu, spec v1'dir. msgid türetmede ya da çeviri doğrulamada geriye dönük uyumsuz
bir değişiklik sürümü artırır ve mevcutun yanına yeni bir
`conformance/vN.json` yayımlar. Ne türetilmiş msgid'leri ne de kabul edilen
desenleri değiştiren, ekleme niteliğindeki netleştirmeler bunu yapmaz.
