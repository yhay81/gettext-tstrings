---
description: "Pesan terjemahan yang sama ditulis dengan %-format, .format(), $-string flufl.i18n, dan t-string, dibandingkan pada kesalahan penerjemah, kewenangan katalog, dan biaya integrasi."
---

# Mengapa t-string

Empat cara memasukkan sebuah nilai ke dalam pesan yang dapat diterjemahkan,
dibandingkan pada pesan yang sama. Keempatnya memberi nama pada placeholder-nya
dan membiarkan seorang penerjemah mengurutkannya ulang; keempatnya berbeda
dalam apa yang terjadi ketika sebuah terjemahan salah, dalam seberapa jauh
katalog dapat menjangkau program Anda, dan dalam biaya mengadopsinya.

Tabelnya datang lebih dulu, sehingga Anda dapat menemukan baris yang Anda
pedulikan dan hanya membaca bagian di baliknya.

!!! note "Tiga pihak menyentuh setiap pesan terjemahan"

    Sebuah **katalog** adalah berkas terjemahan — `.po` selagi disunting
    manusia, dikompilasi menjadi `.mo` untuk dimuat aplikasi
    ([tutorial](tutorial.md) menempuh keduanya). Tiga pihak menyentuh setiap
    pesan: **pengembang** menulis string sumber, seorang **penerjemah**
    menyunting katalog — sering di platform eksternal, jauh dari tinjauan kode
    mana pun — dan **aplikasi** merender keduanya bersama saat runtime. Setiap
    gaya pemformatan di bawah menjawab pertanyaan yang sama secara berbeda:
    *seberapa besar bahasa format yang boleh dikendalikan katalog?* Dalam
    contoh-contohnya, `_` adalah nama konvensional untuk fungsi penerjemah,
    dan `tr` adalah milik pustaka ini.

## Berdampingan { #side-by-side }

**Ketika seorang penerjemah membuat kesalahan.** Sebuah katalog bepergian
melewati banyak tangan, dan sebagian besar yang salah di dalamnya bersifat tak
sengaja:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Sebuah terjemahan *menghilangkan* placeholder — apa yang dirender? | nilainya lenyap diam-diam | nilainya lenyap diam-diam | nilainya lenyap diam-diam | pesan sumbernya, dengan peringatan ([secara bawaan](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Sebuah terjemahan *menambahkan* placeholder tak dikenal — apa yang dirender? | eksepsi | eksepsi | placeholder tetap terlihat sebagai teks | pesan sumbernya, dengan peringatan ([secara bawaan](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Sebuah terjemahan *memformat ulang* placeholder — apa yang dirender? | apa yang diminta katalog, atau sebuah eksepsi jika huruf tipenya tidak lagi cocok dengan nilainya | apa yang diminta katalog | tidak dapat diungkapkan dalam `$`-string | pesan sumbernya, dengan peringatan |
| Apakah placeholder diperiksa saat render? | tidak | tidak | tidak | ya (lihat di bawah) |

**Kewenangan apa yang dimiliki katalog.** Sebuah terjemahan adalah data dari
luar repositori Anda, dan setiap gaya menyerahkan kuasa dalam takaran yang
berbeda kepadanya:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Dari mana nilai berasal? | pemetaan eksplisit | argumen eksplisit | variabel local dan global pemanggil, ditambah `extras` opsional | nilai yang ditangkap di dalam t-string |
| Bisakah katalog mengubah cara sebuah nilai diformat? | ya | ya | tidak | tidak |
| Bisakah katalog menjangkau ke dalam objek (akses atribut)? | tidak | ya | ya, dengan nama bertitik | tidak |
| Di mana "bahasa saat ini" berada? | di mana pun aplikasi menaruhnya | di mana pun aplikasi menaruhnya | sebuah tumpukan kode bahasa pada objek aplikasi bersama | sebuah `ContextVar`, per task atau permintaan |

**Berapa biaya mengintegrasikannya.** Semua di atas gratis jika perkakasnya
cocok; di sinilah ia mungkin tidak:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Python minimum | apa saja | apa saja | 3.10 | **3.14** |
| Kematangan | pustaka standar | pustaka standar | rilis stabil | **alpha** |
| Menggunakan katalog PO/MO biasa? | ya | ya | ya | ya |
| Membutuhkan ekstraktor sumber kustom? | tidak | tidak | tidak | ya, saat ini |
| Flag PO mana yang disimpulkan Babel, untuk divalidasi perkakas yang sudah ada? | `python-format` | `python-brace-format` | tidak ada | `python-brace-format` |

Tentang pemeriksaan saat render: pesan tunggal diperiksa untuk kecocokan
placeholder yang tepat. Pesan jamak juga diperiksa, terhadap
[aturan union/interseksi](spec.md) yang membiarkan bentuk jamak bahasa sasaran
berbeda dari bahasa sumber; pemeriksaan per bentuk yang lebih ketat berjalan
saat katalog dikompilasi ([Ekstraksi](extraction.md)).

Baris flag format adalah soal validasi yang sadar placeholder, bukan
kompatibilitas katalog. `tidak ada` berarti perkakas gettext standar tetap
membaca dan mengompilasi pesannya, tetapi `msgfmt --check-format` tidak punya
tata bahasa placeholder `$` untuk diterapkan.

## Kompatibilitas dan kematangan { #compatibility-and-maturity }

Dua baris pertama tabel terakhir adalah yang menentukan adopsi, jadi keduanya
layak dinyatakan terang-terangan alih-alih sebagai sel tabel.

`%`-format dan `.format()` tertanam di dalam Python dan sama sekali tidak
membutuhkan dependensi. [`flufl.i18n`][flufl-i18n] adalah paket matang, sudah
dirilis dan dipakai di produksi, yang berjalan di Python 3.10 dan yang lebih
baru. `gettext-tstrings` adalah sebuah **alpha** dan membutuhkan **Python 3.14
atau lebih baru**, karena t-string adalah sintaks baru di 3.14 — tidak ada
back-port dan tidak mungkin ada. [Spesifikasinya](spec.md) adalah bagiannya
yang stabil; API Python-nya masih mungkin bergerak sebelum 1.0.

Yang tidak dibebankan satu pun di antaranya adalah kompatibilitas katalog.
Keempatnya menghasilkan berkas POT/PO/MO biasa yang sudah dibaca setiap editor
PO, platform penerjemahan, dan perkakas GNU gettext, sehingga pilihan di bawah
dapat dibalik dengan cara yang tidak dimiliki perubahan *format* katalog.
[Migrasi](migration.md) membahas pemindahan proyek yang sudah ada.

Bagian-bagian di bawah menunjukkan setiap pertukarannya secara rinci, satu
metode pada satu waktu.

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Apa yang bisa salah: sebuah placeholder yang rusak menjadi eksepsi saat
runtime, kecuali validasi katalog menangkapnya lebih dulu.

String katalognya membawa sintaks printf, termasuk huruf tipe di ekornya —
`s` pada `%(name)s` — yang mudah terlewat dan mudah rusak:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Suntingan satu karakter di editor PO menjadi eksepsi saat runtime kecuali
validasi katalog menangkapnya lebih dulu. GNU `msgfmt --check-format` memang
menangkap yang satu ini, tetapi hanya untuk pesan yang diberi flag
`python-format`, dan hanya jika katalognya benar-benar melewati msgfmt dalam
perjalanannya ke aplikasi Anda.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Ia menghapus huruf tipe di ekor sambil mempertahankan placeholder bernama yang
bebas diurutkan ulang. Apa yang bisa salah berpindah ke sisi lain pertukaran:
terjemahan memperoleh kuasa atas objek-objek Anda.

`str.format` adalah bahasa ekspresi kecil, dan memanggilnya pada sebuah string
berarti menyerahkan hak memakai bahasa itu kepada string tersebut:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Sekarang gantilah string literal itu dengan apa pun yang dikembalikan `_()`.
Jika terjemahan `Hello {name}` kembali sebagai `{conf.api_key}`, merendernya
mencetak API key Anda — katalog, bukan kode Anda, yang menentukan apa yang
terbaca. Sebuah katalog bukan kode, tetapi ia bepergian layaknya data: keluar
ke platform penerjemahan, melewati beberapa tangan, kembali sebagai `.po`,
dikompilasi menjadi `.mo`, kadang di-vendor dari luar proyek Anda sama sekali.
`.format()` memberi setiap tahap perjalanan itu akses atribut pada objek yang
Anda lewatkan.

## `$`-string dan flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

[`string.Template`][stdlib-template] milik pustaka standar menyediakan bahasa
interpolasi `$name`, tetapi bukan API penerjemahan itu sendiri.
[`flufl.i18n`][flufl-i18n] menggabungkan gaya itu dengan pencarian katalog
gettext. Perhatikan bahwa nilainya tidak pernah dilewatkan: flufl.i18n
membangun ruang nama substitusi dari globals dan locals pemanggil — variabel
apa pun yang ada di tempat pemanggilan tersedia bagi pesan. Sebuah pemetaan
`extras` opsional diutamakan atas keduanya. Sintaks yang menghadap
penerjemahnya tidak memiliki huruf tipe di ekor atau penentu format, dan
placeholder tetap bebas diurutkan ulang.

Substitusi yang tidak tersedia tidak melempar galat. Dengan `name = "Ada"` dan
tanpa `nombre` di ruang nama pemanggil, terjemahan katalog `Hello $nombre`
dirender sebagai `Hello $nombre`: placeholder yang tak terselesaikan tetap
terlihat. [Perilaku terdokumentasi][documented behavior] itu mempertahankan
sisa pesan terjemahan alih-alih menggagalkan pemanggilan. Eksepsi yang muncul
saat menyelesaikan sebuah atribut atau mengonversi sebuah nilai masih bisa
merambat.

`flufl.i18n` lebih mampu daripada `string.Template` polos dalam satu hal yang
relevan. [Template kustomnya][custom Template] menerima placeholder bertitik
seperti `$settings.api_key`, dan [translator-nya][translator] menyelesaikan
jalur-jalur itu terhadap nilai-nilai pemanggil. Sebuah placeholder terjemahan
boleh menyebut local atau global pemanggil mana pun yang tersedia dan, dengan
sintaks bertitik, menelusuri atribut-atributnya. Itu praktis ketika sebuah
pesan membutuhkan atribut, sekaligus menjadikan frame pemanggil bagian dari
ruang nama substitusi katalog. Perbandingan di sini menggambarkan
`flufl.i18n` 6.0.0, bukan setiap kemungkinan penggunaan `string.Template`.

Ia juga menjawab sebuah pertanyaan yang oleh dua gaya pemformatan lainnya
diserahkan sepenuhnya kepada aplikasi: bahasa *mana* yang sedang berlaku, dan
bagaimana menggantinya. Sebuah [objek aplikasi][application object] menyimpan
tumpukan bahasa, `_.push(code)` dan `_.pop()` menggerakkannya,
`with _.using(code):` bersarang, dan sebuah [strategi][strategy] mencari
katalog untuk sebuah kode bahasa sehingga aplikasi tidak pernah menangani objek
katalog sendiri. Sebuah server yang harus menghasilkan teks dalam lebih dari
satu bahasa selama satu satuan kerja — sebuah halaman untuk pembacanya, sebuah
notifikasi untuk seseorang yang akunnya disetel berbeda — adalah kasus yang
melatarbelakangi keberadaannya.

Tumpukan itu hidup pada objek aplikasi tersebut, yang dipakai bersama oleh
seluruh proses. Dua permintaan yang tumpang-tindih karenanya berbagi satu
tumpukan, dan blok-blok yang tidak bersarang secara ketat *dalam waktu* saling
menyerahkan bahasa yang keliru:

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

Pustaka ini mempertahankan kemampuan yang sama — ikatan bersarang dan terurai
dengan cara yang sama — di dalam sebuah `ContextVar` alih-alih tumpukan yang
dipakai bersama, sehingga jalinan di atas terselesaikan per task. Padanannya
ada di [Beberapa bahasa sekaligus](guide.md#several-languages-at-once). Yang
tidak disediakannya adalah pencarian dari kode bahasa ke katalog: Anda
melewatkan sebuah objek terjemahan, yang untuk kasus umumnya adalah satu
panggilan `gettext.translation()`, dan pustaka standar menyimpan katalog yang
sudah diurai di cache.

## t-string { #t-strings }

```python
tr(t"Hello {name}")
```

Katalog tetap melihat `Hello {name}` dan tetap menjadi katalog PO/MO biasa.
Bedanya adalah apa yang *boleh dikatakan* sebuah terjemahan, dan siapa yang
memeriksanya.

Pustaka ini memvalidasi setiap terjemahan terhadap placeholder pesan sumber
sebelum merender, dan ia menerima nama polos dan tidak yang lain. Terhadap
`t"Hello {name}"`:

| Terjemahan yang berisi | ditolak dengan |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Ditolak tidak berarti crash: secara bawaan pustaka mencatat sebuah peringatan
dan merender pesan sumbernya, sehingga katalog yang buruk tidak pernah menjatuhkan
aplikasi —
[kontrak yang sama yang dijaga gettext sendiri](guide.md#what-happens-when-a-catalog-is-wrong).

Pemformatan tetap di tempat ia ditulis, di dalam kode:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` tidak pernah sampai ke katalog, jadi tidak ada terjemahan yang bisa
mengubahnya, dan tidak ada penerjemah yang harus melihatnya. Namun itu format
yang *tetap*, bukan yang terlokalkan — memilih digit dan pemisah per bahasa
adalah [urusan Babel, sebelum pemanggilannya](guide.md#locale-aware-values).

Satu perbedaan lagi adalah perkakas: t-string adalah sintaks baru, jadi
mengekstraknya ke `.pot` saat ini membutuhkan ekstraktor yang sadar t-string,
seperti yang [disediakan paket ini untuk Babel](extraction.md).

## Biaya pembatasannya { #the-cost-of-the-restriction }

Di luar persyaratan Python-nya, harga dari semua ini adalah satu aturan: sebuah
interpolasi harus berupa nama polos.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Itu batasan yang nyata, dan itu pula batasan yang menghasilkan jaminan-jaminan
di atas. Bersama pengikatan nilai di sisi sumber dan pemeriksaan placeholder
saat runtime, ia mencegah string katalog mengevaluasi ekspresi dan menjaga nama
placeholder tetap bermakna bagi orang yang menerjemahkannya.

Sebuah f-string sama sekali tidak dapat dipakai seperti ini — pada saat pustaka
mana pun melihatnya, ia sudah menjadi string jadi, sehingga menerjemahkannya
berarti menerjemahkan penggalan. t-string ([PEP 750]) menjaga teks statis dan
nilai tetap terpisah sambil mempertahankan sintaks mirip f-string dan
pengikatan nilai eksplisit.

Bagaimana Python tiba di sini — dua PEP berjarak sepuluh tahun,
dan diskusi stdlib yang ditutup tanpa jawaban — diceritakan beserta sumbernya
di [Latar belakang](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
