---
description: "Hâlihazırda gettext katalogları olan bir projede t-string'leri benimsemek: neler dokunulmadan kalır, neler fuzzy olur ve nasıl her seferinde bir çağrı noktası taşınır."
---

# Geçiş

Projeniz zaten gettext kullanıyorsa, bu kütüphanenin benimsenebilir olup
olmadığına karar veren sorular dardır: elinizdeki katalogları geçersiz kılıyor
mu, değiştirmeye hazır olmadığınız kodla bir arada yaşayabilir mi ve taşınmanın
ne kadarı aynı anda olmak zorunda. Yanıtlar, en kısasından başlayarak:

| Soru | Yanıt |
| --- | --- |
| Var olan `.po` ve `.mo` dosyaları hâlâ çalışıyor mu? | Evet. Aynı dosyalar, aynı araçlar. |
| Eski ve yeni çağrılar tek bir dosyada yaşayabilir mi? | Evet; tek bir çıkarıcı eşlemesi ikisini de kapsar. |
| msgid değişiyor mu? | `.format()`ten geçişte hayır. `%`-formattan geçişte evet. |
| Tüm proje aynı anda taşınmak zorunda mı? | Hayır. Tek bir çağrı noktası geçerli bir değişikliktir. |
| Peki Jinja, Django şablonları, JavaScript? | Dokunulmadan kalır, aynı kataloglar. |

Sayfanın geri kalanı, bunların her birinin ardındaki ayrıntıdır.

## `.format()`ten: msgid değişmez { #from-format-the-msgid-does-not-change }

Geçişin neredeyse hiçbir bedeli olmadığı durum budur. Bir `str.format` mesajı
ile bir t-string mesajı *aynı* katalog anahtarını türetir; çünkü anahtar, her
iki durumda da içinde `{name}` bırakılmış metindir:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Böylece var olan çeviri bağlı kalır. Şunu tutan bir katalogdan başlayarak

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

çağrıyı değiştirin, yeniden çıkarın ve güncelleyin:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Geri gelen girdi, iki satırlık üstveride ayrışır ve başka hiçbir yerde değil —
onu bir t-string mesajı olarak tanımlayan bir işaret yorumu ve bir kaynak satır
numarası:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Hiçbir dilde ne `fuzzy` bayrağı ne de yeniden çeviri. Mesaj anında render
edilir:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` katalogları güncel değil diye raporlayacak"

    O işaret yorumu ve kayan satır numaraları, `pybabel update --check`in bir
    kataloğun yeniden üretilmesi gerektiğini söylemesine yeter; çünkü yalnızca
    çeviriyi değil, girdinin tamamını karşılaştırır. Gerçek `pybabel update`
    komutunu kod değişikliğiyle aynı commit'te çalıştırın ve katalogları onunla
    birlikte commit'leyin — bu, [CI kapısının](workflow.md#what-ci-gates)
    zaten istediği alışkanlığın aynısıdır.

## `%`-formattan: msgid değişir, çeviriler fuzzy olur { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Printf sözdizimi mesajın *içinde* yaşar; dolayısıyla onu değiştirmek katalog
anahtarını yeniden yazar. Bunun etrafından dolaşmanın yolu yoktur ve
`%(name)s`i geride bırakmanın dürüst bedeli budur:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update`, yeni mesajı kaldırılan mesajın yakın akrabası olarak tanır ve
eski çeviriyi fuzzy işaretiyle karşıya taşır:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Bu durum hakkında bilinmesi gereken üç şey:

- **Çalışma zamanında hiçbir şey bozulmaz.** Fuzzy girdiler derlenmiş `.mo`
  dosyasının dışında bırakılır; böylece bir insan çifti onaylayana dek uygulama
  kaynak mesajı render eder — yeniden yazılmış her mesajın geçtiği
  [aynı alçalma](workflow.md#the-cycle-after-the-first-translation).
- **Onlar fuzzy'yken CI yeşil kalır.** Yer tutucu denetleyicisi, tıpkı
  `msgfmt --check-format` gibi fuzzy girdileri atlar; çünkü çalışma zamanına
  ulaşamayan bir girdi bir derlemeyi düşürmemelidir. Bir çevirmen bayrağı
  temizlediği anda girdi diğerleri gibi denetlenir — yani onaylanmış bir
  çeviride kalmış bir `%(name)s` tam o noktada yakalanır; zaten render edilmeye
  başlayacağı nokta da orasıdır.
- **Eski `python-format` bayrağı da yolculuk eder** ve `fuzzy` bayrağıyla
  birlikte silinmelidir; yoksa `msgfmt --check-format` brace-format bir mesaja
  printf kurallarını uygulamayı sürdürür.

Adlandırılmış printf yer tutucularında düzenleme mekaniktir — `%(name)s`,
`{name}` olur ve başka hiçbir şey kımıldamaz — dolayısıyla büyük bir katalog,
bir yeniden çeviri değil, betikle yapılan bir geçiş ve ardından bir çevirmen
incelemesidir. Konumsal `%s` mekanik değildir: taşınacak bir adı yoktur ve bir
ad seçmek, değişikliğin ta kendisidir.

Geçiş bu yüzden incelemenin izin verdiği hızda ilerleyebilir: dönüştürülmemiş
bir fuzzy girdi, bozuk bir derleme değil, katalogda görünen bir iş parçasıdır.

## Eski ve yeni çağrılar bir arada yaşar { #old-and-new-calls-coexist }

t-string okuyan çıkarıcı, sıradan gettext çağrılarını da okur; dolayısıyla tek
bir eşleme, geçişin ortasındaki bir dosyayı kapsar:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

Her iki mesaj da aynı şablona iner ve yalnızca t-string olanı, bu kütüphanenin
ek denetimini açan işaret yorumunu taşır:

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

`_()` işlevini, dört standart gettext adını, `tr()` / `ntr()` takma adlarını ve
ertelenmiş `lazy_gettext()` / `lazy_pgettext()` işlevlerini tanır. Kendi
yardımcınızın
[eşlemede adlandırılması](extraction.md#registering-your-own-function-names)
gerekir.

Çalışma zamanında iki tarz eşit ölçüde bağımsızdır: `gettext.translation()` tek
bir çeviri nesnesi döndürür ve hem `_` hem de bu kütüphanenin giriş noktaları
ondan okur.

## Taşınmayanlar { #what-does-not-move }

- **Şablon dilleri.** Jinja2'nin `{% trans %}` yapısı, Django'nun şablon
  etiketleri ve onların Babel çıkarıcıları değişmeden çalışmayı sürdürür ve aynı
  PO kataloglarını beslemeye devam eder. t-string'ler Python sözdizimidir;
  Python kaynağına uygulanırlar.
- **Katalog dosyalarınız.** Biçim değişikliği yok, yeni dosya yok, dönüştürme
  adımı yok.
- **Çeviri platformunuz.** `.po` alışverişi birebir aynıdır ve bir t-string
  mesajının taşıdığı `python-brace-format` bayrağı, bir `.format()` mesajının
  taşıdığı bayrağın aynısıdır — dolayısıyla yer tutucu QA'sı çalışmayı sürdürür.
- **Python olmayan kod.** Aynı projedeki bir JavaScript ya da C kataloğu
  etkilenmez.

## Bir geçiş kontrol listesi { #a-migration-checklist }

1. `pybabel`ın çalıştığı yere `babel` ekstrasını ekleyin ve `babel.cfg`
   içindeki `python` eşlemesini `gettext_tstrings` yöntemine çevirin — o zaman
   tek bir eşleme her iki tarzı da kapsar ve `-k`, sıradan çağrılar için
   çalışmayı sürdürür.
2. Önce `.format()` çağrı noktalarını dönüştürün. Yeniden çıkarın,
   `pybabel update` çalıştırın ve katalogları kodla birlikte commit'leyin;
   fuzzy girdi beklemeyin.
3. `%`-format çağrı noktalarını, inceletebileceğiniz gruplar hâlinde
   dönüştürün; karşıya taşınan yer tutucuları yeniden yazın ve `fuzzy` ile
   `python-format` bayraklarını temizleyin.
4. Kısıtlamanın reddettiklerini düzeltin: bir interpolasyon yalın bir ad olmak
   zorundadır; yani `t"Hello {user.name}"` önce bir yerel değişkene dönüşür. Bu,
   bir katalog düzenlemesi değil, bir çağrı noktası düzenlemesidir.
5. Süpürme bittiğinde çıkarıcı eşlemesinde `strict = true` ayarını açın;
   böylece çıkarılamayan bir mesaj şablondan yok olmak yerine
   [derlemeyi](extraction.md#lenient-locally-strict-in-ci) düşürür.
6. [Üretimde](workflow.md#what-ci-gates) sayfasındaki çalışma zamanı denetimini
   ekleyin: sevk edilen her dil için bir mesajı katı bir `Translator` üzerinden
   render edin.

2. ve 3. adımlar sıradan commit'lerdir. Bu listedeki hiçbir şey bir bayrak günü
gerektirmez.
