---
description: "pybabel ile t-string mesajlarını çıkarmak ve msgfmt ile paketle gelen Babel denetleyicisinin katalogları nasıl doğruladığı."
---

# Çıkarma

Çıkarma, işaretlenmiş her mesajı kaynak kodunuzdan çevirmenler için bir
`.pot` şablonuna toplayan adımdır — [öğreticinin](tutorial.md) döngüsündeki
3. adım. Bu sayfa o adımın referansıdır: yapılandırma, özel işlev adları,
katı CI kipi ve sonrasında kataloglarınızı koruyan denetimler.

Çıkarma, `babel` ekstrasına ihtiyaç duyar:

```console
python -m pip install "gettext-tstrings[babel]"
```

## İş akışı { #the-workflow }

`babel.cfg` dosyasını oluşturun:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Sonra sıradan Babel komutlarını kullanın:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` her dil için bir kez çalışır; ondan sonra `pybabel update` her taze
şablonu mevcut katalogların içine katlar. Bu yinelenen çevrim — ve `fuzzy`
girdilerinin bir sürüm için ne anlama geldiği —
[Üretimde](workflow.md#the-cycle-after-the-first-translation) sayfasında adım
adım anlatılır.

`gettext_tstrings` çıkarıcısı sıradan `_()`, `gettext()` ve `ngettext()`
çağrılarını da işler; böylece tek bir eşleme karışık bir kod tabanını kapsar.
`_()` işlevini, dört standart gettext adını, `tr()` / `ntr()` takma adlarını
ve ertelenmiş `lazy_gettext()` / `lazy_pgettext()` işlevlerini tanır.

!!! warning "`-c` isteğe bağlı değildir"

    `pybabel extract`, çevirmen yorumlarını yalnızca `-c "Translators:"`
    verdiğinizde toplar; tıpkı sıradan gettext çağrılarında olduğu gibi.

## Kendi işlev adlarınızı kaydetmek { #registering-your-own-function-names }

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

Bir ini dosyası tek bir dizgi verir, bir TOML eşlemesi bir liste verir ve bir
dizginin içinde adları boşluk ya da virgül ayırır. Dört yazım da çalışır.

Seçenekler şunlardır: `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` ve `npgettext_functions`.

!!! danger "`-k` bir t-string'e ulaşmaz"

    `mytr(t"…")` gibi özel bir yardımcının, yukarıdaki seçeneklerden birinde
    adlandırılması gerekir. Babel'in `--keyword` mekanizması bir t-string
    değişmezini okuyamaz; bu yüzden `pybabel extract -k mytr` hiçbir şey
    bulmaz ve hiçbir şey söylemez — mesajlar POT'tan düpedüz eksik kalır.
    `-k`, yanı sıra çıkarılan sıradan gettext çağrıları için çalışmaya devam
    eder.

    Yalnızca standart argüman sırası desteklenir: önce mesaj; `pgettext` için
    bağlam sonra mesaj; `npgettext` için bağlam, sonra tekil, sonra çoğul.

## Varsayılan olarak dayanıklı { #robust-by-default }

Tek bir kötü dosya çalıştırmayı sonlandırmaz:

- Çıkarıcının reddettiği bir t-string — öznitelik erişimi, bir ifade, yanlış
  bir argüman — uyarı olarak raporlanır ve atlanır.
- Ayrıştırılamayan bir dosya aynı şekilde atlanır.
- `ast` kabul ederken yalnızca `tokenize`ın reddettiği bir dosya da öyle —
  Babel'in kendi geçişi aksi halde bunda iptal olurdu.

Eşleme seçeneklerinde `strict = true` ayarlayarak bunların her birini sert
bir hataya çevirin; CI'da istediğiniz budur.

## Mevcut araç zinciriniz bu katalogları doğrular { #your-existing-toolchain-validates-these-catalogs }

Babel, çıkarılan her mesajı standart bir bayrakla işaretler ve zaten
çalıştırdığınız araçlarda yer tutucu denetimini etkinleştiren şey o tek
satırdır:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Bunu `こんにちは {nombre}` olarak çevirin; hata hiçbir yapılandırma olmadan
yakalanır:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate aynı denetimi [Python brace format][weblate-checks] adıyla belgeler
ve ticari platformların aynı bayrağa dayanan kendi yer tutucu QA'ları vardır.
Onların davranışı kendilerine aittir; burada doğrulanan, aşağıdaki iki
araçtır.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Bunun üzerine paket bir Babel **denetleyicisi** kaydeder; böylece
`pybabel compile`, `gettext-tstrings` işaret yorumunu taşıyan her mesaja
belirtimin kurallarını uygular:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Çoğul bir mesaj için işaretçi biçimin adını verir, çünkü Babel'in raporladığı
satır numarası msgid'ninkidir ve bir Rusça blokta onun altında üç `msgstr`
vardır:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` yine de `.mo` dosyasını yazar"

    Yukarıdaki hata raporlanır, çıkış durumu `1` olur — ve bozuk katalog yine
    de derlenir. Bir boru hattının onu sevk etmesini yalnızca o çıkış durumu
    durdurabilir; [CI'ın neyi kapıladığı](workflow.md#what-ci-gates), buna
    izin veren derleme adımını gösterir.

İki denetim birbirinin yedeği değildir. Paketle gelen denetleyici en az iki
noktada daha katı taraftır:

- Tek ayraçları kaçışlanmış olan bir msgid (`Config {{raw}} only`)
  `python-brace-format` bayrağını hiç almaz; dolayısıyla hiçbir harici araç
  onu doğrulamaz.
- Çoğul biçimler tek tek denetlenir. `msgfmt --check-format` tam da
  yukarıdaki dosyayı okur ve `0` ile çıkar; kardeşlerinin koruduğu bir yer
  tutucuyu düşüren bir biçim orada kabul edilir, burada reddedilir.

`msgfmt`, yalnızca Python brace format olarak ayrıştırabildiği yer tutucu
adlarını denetler; bu yüzden ASCII adlar, zincirdeki her aracın mesajı
doğrulayabilmesini sağlar. Kütüphanenin kendisi `str.isidentifier()` doğru
olan her adı kabul eder.

## Şablonlar ve diğer araçlar { #templates-and-other-tools }

t-string'ler Python sözdizimidir; dolayısıyla bu kütüphane Python kaynağını
kapsar. Şablon dilleri kendi i18n'lerini — Jinja2'nin `{% trans %}` etiketi,
Django'nun şablon etiketleri — ve Babel'in onlar için çıkarıcılarını
kullanmaya devam eder. Her şey aynı PO kataloğunu besler; böylece tek bir
çeviri iş akışı karışık bir kod tabanını yine kapsar.

`pygettext` bugün t-string'leri ayrıştıramaz; çıkarmanın Babel üzerinden
gitmesinin nedeni budur. Uzlaşım [belirtimde](spec.md) yazılıdır; böylece
başka bir çıkarıcı ya da gelecekteki bir `pygettext` onu hedefleyebilir.
