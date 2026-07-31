---
description: "API runtime: titik masuk mana yang dipakai, mengikat katalog, bahasa per permintaan, string tertunda, nilai yang sadar locale, dan bagaimana terjemahan yang rusak dilaporkan."
---

# Panduan

Halaman ini adalah referensi runtime: semua yang dilakukan *kode aplikasi*
Anda dengan pustaka ini setelah katalog ada. Jika Anda belum melihat putaran
lengkapnya — tandai, ekstrak, terjemahkan, kompilasi, jalankan —
[tutorial](tutorial.md) menempuhnya sekali dalam lima menit; membuat dan
memvalidasi katalog dibahas di [Ekstraksi](extraction.md), dan bagaimana
sebuah tim menjaga putaran itu terus berputar — siklus pembaruan, CI, platform
penerjemahan — ada di [Dalam produksi](workflow.md).

## Titik masuk mana yang sebaiknya saya pakai? { #which-entry-point-should-i-use }

Paket ini mengekspor beberapa cara untuk menerjemahkan sebuah pesan karena
aplikasi mengikat bahasa dengan beberapa cara berbeda. Pilih berdasarkan
bagaimana program Anda memutuskan sedang berada di bahasa apa:

| Situasi Anda | Pakai |
| --- | --- |
| Satu bahasa untuk seluruh proses — sebuah CLI, aplikasi desktop, skrip | `Translator`, dipanggil sebagai `_` |
| Satu bahasa per permintaan atau per task async — sebuah aplikasi web | `use_translations()` mengelilingi pekerjaannya, lalu `tr()` |
| Sebuah pesan yang didefinisikan saat impor — label formulir, enum, konstanta | `lazy_gettext()` atau `lazy_pgettext()` |
| Sebuah hitungan menentukan kata-katanya | `ngettext()` / `npgettext()`, dalam bentuk mana pun di atas |
| Merender sebuah pattern tanpa katalog terlibat | `compile_template()` |

Semua di bawah ini adalah kelima hal itu, dalam urutan itu.

## Mengikat sebuah katalog { #binding-a-catalog }

Bentuk yang direkomendasikan mencerminkan penggunaan berbasis kelas gettext:
ikat sebuah objek terjemahan standar sekali dan gunakan prosesor callable-nya
sebagai `_`.

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

Fungsi-fungsi tingkat modul mengikuti nama pustaka standar dan konvensi
pemanggilan positional-only-nya:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` dan `ntr` adalah alias persis dari `gettext` dan `ngettext`.

## Bahasa per permintaan { #per-request-language }

Sebuah framework web memilih bahasa per permintaan. Ikat terjemahan
permintaan itu ke konteks saat ini dan setiap pemanggilan tingkat modul
terselesaikan ke bahasa itu, dengan aman di antara permintaan-permintaan yang
berjalan bersamaan:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` mengikat tanpa blok `with`, untuk framework
yang mengelola siklus hidup permintaannya sendiri; `get_translations()`
membaca ikatan saat ini. Argumen `translations=` eksplisit selalu menang atas
konteks, dan konteks yang tak terikat kembali ke fungsi gettext yang dipasang
global oleh pustaka standar. Contoh lengkap untuk Flask dan middleware ASGI
ada di halaman [Dalam produksi](workflow.md#binding-a-language-at-runtime).

## Terjemahan tertunda { #deferred-translation }

Sebuah t-string menangkap nilainya dengan segera, yang keliru untuk string
yang didefinisikan saat impor — label formulir, nilai enum, konstanta modul —
yang harus dirender dalam bahasa apa pun yang aktif ketika ia *digunakan*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

Sebuah `LazyString` merender melalui `str()`, `format()`, dan f-string, serta
membandingkan sama dengan teks hasil rendernya.

!!! note "Sengaja tidak dapat di-hash"

    Teks sebuah `LazyString` bergantung pada bahasa yang aktif, sehingga
    sebuah hash akan berubah saat pergantian bahasa dan diam-diam merusak set
    atau dict mana pun yang menyimpannya. Panggil `str()` lebih dulu jika Anda
    memerlukan sebuah kunci.

`strict` ditentukan di tempat pesan itu ditulis, bukan di tempat ia dirender:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Sebuah string tertunda dirender di mana pun ia akhirnya dipakai — di dalam
sebuah templat, sebuah formulir, sebuah baris log — dan tempat itu jarang tahu
apakah ini sebuah jalannya pengujian atau produksi. Meneruskan `strict=True`
pada definisinya adalah yang membuat pilihan yang sama —
[lantang di CI, longgar di produksi](#what-happens-when-a-catalog-is-wrong) —
berlaku untuk string yang tidak dirender di tempat pemanggilannya.

Bentuk jamak bergantung pada hitungan saat runtime, jadi render itu secara
langsung dengan `ngettext` di tempat hitungannya diketahui.

## Beberapa bahasa sekaligus { #several-languages-at-once }

Satu permintaan kerap membutuhkan lebih dari satu bahasa: sebuah halaman yang
dirender untuk pembacanya sekaligus mengantrekan notifikasi ke akun yang
disetel ke bahasa lain, atau sebuah ringkasan yang mengutip tiap peserta dalam
bahasanya masing-masing. Ikatan bersarang, dan meninggalkan blok dalam
memulihkan blok luarnya.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Untuk sebuah daftar penerima, string tertunda yang mengerjakannya: pesannya
ditulis sekali, saat impor, dan dirender sekali per bahasa.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Ikatannya adalah sebuah `ContextVar`, bukan tumpukan yang dipegang sebuah objek
bersama, sehingga permintaan yang tumpang-tindih tidak bisa mengambil bahasa
satu sama lain — termasuk kasus ketika mereka *meninggalkan* bloknya dengan
urutan yang sama seperti saat memasukinya, yaitu jalinan yang disalahpahami
sebuah tumpukan pushdown. Memuat sebuah katalog per bahasa itu murah:
`gettext.translation()` mengurai tiap `.mo` sekali dan membagikan salinan yang
berbagi katalog terurai itu.

!!! warning "Apakah sebuah thread pekerja mewarisi ikatannya bergantung pada build-nya"

    Sebuah `threading.Thread` telanjang, atau `ThreadPoolExecutor.submit`,
    bermula entah dari salinan konteks pemanggilnya atau dari konteks yang
    kosong, dan mana di antara keduanya itulah
    `sys.flags.thread_inherit_context` — benar secara bawaan pada build
    free-threaded, salah di tempat lain mana pun. Maka kode yang sama merender
    bahasa yang terikat pada 3.14t dan katalog global proses pada 3.14. Oper
    konteksnya alih-alih bergantung pada nilai bawaannya:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` sudah melakukan ini untuk Anda.

## Nilai yang sadar locale { #locale-aware-values }

Pustaka ini memutuskan *di mana* sebuah nilai muncul dalam pesan yang
diterjemahkan. Ia tidak melokalkan nilainya sendiri. `{amount:,.2f}` adalah
format spec Python dengan perilaku tetap — sebuah koma setiap tiga digit dan
sebuah titik sebelum desimalnya — dan ia menghasilkan karakter yang sama apa
pun bahasa pesannya:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Bahasa Jerman menulis angka itu `1.234,50`, Prancis `1 234,50`, dan Hindi
mengelompokkan `1234567` sebagai `12,34,567` alih-alih `1,234,567`. Angka, mata
uang, tanggal, waktu, dan satuan adalah urusan [Babel][babel-numbers]. Format
nilainya lebih dulu, lalu tempatkan string yang sudah jadi:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

Untuk pesan berhitungan, angkanya melakukan dua tugas — ia memilih bentuk
jamaknya dan ia muncul di teksnya — dan hanya yang kedua yang dilokalkan.
Simpan hitungan mentahnya untuk pemilihan itu dan oper string yang sudah
diformat untuk ditampilkan:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Memformat sebelum pemanggilannya juga yang menjaga format spec tetap di luar
katalog: yang dilihat penerjemah adalah sepotong teks yang sudah jadi, bukan
sebuah angka ditambah instruksi untuk merendernya.

## Apa yang terjadi ketika sebuah katalog salah { #what-happens-when-a-catalog-is-wrong }

Jika placeholder sebuah terjemahan tidak cocok dengan sumbernya — sebuah field
yang hilang, tak dikenal, atau diformat ulang yang lolos dari validasi, dari
MO yang disunting tangan, katalog vendor, atau pipeline yang melewatkan
pemeriksanya — perilaku bawaannya adalah merender pesan sumbernya alih-alih
melempar galat. Ini mencerminkan kontrak gettext sendiri bahwa katalog yang
buruk tidak pernah merusak aplikasi.

Dengan `Hello {name}` diterjemahkan sebagai `こんにちは {nombre}`, render
berhasil dan satu peringatan pergi ke logger `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Peringatan itu terbit sekali per pesan dan pattern, bukan sekali per render,
sehingga satu entri katalog yang rusak tidak membanjiri log.

Pilih untuk gagal dengan lantang untuk pengujian dan CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Pencarian yang sama kemudian melempar galat, membawa kalimat yang sama tanpa
paruh "using source text"-nya:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Pesan-pesan ini ditulis untuk siapa pun yang dapat menindaklanjutinya, yang
untuk masalah katalog lebih sering berarti penerjemah ketimbang programmer —
jadi di tempat sebuah placeholder tampak ada padahal tidak, pesannya
menjelaskan mengapa alih-alih mengulang bahwa placeholder itu hilang. Kurung
kurawal lebar penuh, `{{name}}` yang berganda, no-break space yang tak
terlihat, sebuah huruf Kiril di antara huruf-huruf Latin: masing-masing punya
kata-katanya sendiri, didaftar beserta contohnya di
[Untuk penerjemah](translators.md#reading-a-failure-message). Halaman itu
ditulis untuk diserahkan kepada orang yang menyunting `.po`.

## Merender pattern tanpa katalog { #rendering-a-pattern-without-a-catalog }

`compile_template` memaparkan mesin yang sama satu tingkat di bawahnya: ia
mengubah sebuah t-string menjadi msgid-nya plus sekumpulan nilai yang terikat,
dan merender pattern apa pun yang Anda serahkan.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` memvalidasi dengan aturan yang sama dan **selalu melempar galat**
pada ketidakcocokan. Tidak ada mode longgar di sini: kelonggaran ada agar
pencarian *katalog* dapat terdegradasi ke teks sumber, dan pattern yang Anda
serahkan sendiri tidak punya apa pun untuk didegradasi.

## Keamanan dan cakupan { #safety-and-scope }

Ini valid:

```python
tr(t"Hello {name}")
```

Ini ditolak dengan sengaja:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Hitung dulu sebuah nilai yang bermakna:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Pembatasan ini menghasilkan kunci katalog yang stabil, memberi penerjemah nama
yang berguna, dan menjaga string terjemahan tidak menjadi bahasa ekspresi.

Jaminannya tercakup pada *struktur dan pemformatan*: sebuah terjemahan tidak
pernah dievaluasi, dan tidak pernah bisa menambahkan akses atribut,
pemanggilan, konversi, atau format spec. Dua hal tetap menjadi tanggung jawab
pemanggil, persis seperti pada gettext stdlib — **escaping** keluaran render
untuk tujuannya (HTML, shell, terminal), dan **integritas katalog**, karena
katalog jahat bisa mengulang sebuah placeholder untuk memperbesar ukuran
keluaran, yang melekat pada i18n berbasis placeholder mana pun.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
