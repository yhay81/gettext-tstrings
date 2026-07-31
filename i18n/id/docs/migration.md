---
description: "Mengadopsi t-string di proyek yang sudah punya katalog gettext: apa yang selamat tanpa disentuh, apa yang menjadi fuzzy, dan bagaimana berpindah satu titik panggilan sekali jalan."
---

# Migrasi

Jika proyek Anda sudah memakai gettext, pertanyaan yang menentukan apakah
pustaka ini layak diadopsi bersifat sempit: apakah ia membatalkan katalog yang
sudah Anda punya, dapatkah ia berdampingan dengan kode yang belum siap Anda
ubah, dan seberapa banyak perpindahannya harus terjadi sekaligus. Jawabannya,
yang terpendek lebih dulu:

| Pertanyaan | Jawaban |
| --- | --- |
| Apakah berkas `.po` dan `.mo` yang ada tetap berfungsi? | Ya. Berkas yang sama, perkakas yang sama. |
| Bisakah panggilan lama dan baru hidup dalam satu berkas? | Bisa, dan satu pemetaan ekstraktor mencakup keduanya. |
| Apakah msgid-nya berubah? | Tidak, dari `.format()`. Ya, dari `%`-format. |
| Haruskah seluruh proyek berpindah sekaligus? | Tidak. Satu titik panggilan sudah merupakan perubahan yang sah. |
| Bagaimana dengan Jinja, templat Django, JavaScript? | Tak tersentuh, katalog yang sama. |

Sisa halaman ini adalah rinciannya, satu per satu.

## Dari `.format()`: msgid-nya tidak berubah { #from-format-the-msgid-does-not-change }

Ini kasus di mana migrasinya nyaris tanpa biaya. Sebuah pesan `str.format` dan
sebuah pesan t-string menurunkan kunci katalog yang *sama*, karena kuncinya
adalah teksnya dengan `{name}` tetap berada di dalamnya, dengan cara mana pun:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Jadi terjemahan yang ada tetap melekat. Berangkat dari katalog yang memuat

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

ubah panggilannya, ekstrak ulang, dan perbarui:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Entri yang kembali berbeda dalam dua baris metadata dan tidak lebih dari itu —
sebuah komentar penanda yang mengidentifikasinya sebagai pesan t-string, dan
sebuah nomor baris sumber:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Tanpa flag `fuzzy`, tanpa penerjemahan ulang, dalam bahasa mana pun. Pesannya
langsung dirender:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` akan melaporkan katalognya sudah kedaluwarsa"

    Komentar penanda itu dan nomor baris yang bergeser sudah cukup bagi
    `pybabel update --check` untuk mengatakan sebuah katalog perlu dibuat
    ulang, karena ia membandingkan seluruh entrinya dan bukan hanya
    terjemahannya. Jalankan `pybabel update` yang sebenarnya dalam commit yang
    sama dengan perubahan kodenya, dan commit katalognya bersama itu —
    kebiasaan yang sama yang sudah diminta
    [gerbang CI](workflow.md#what-ci-gates).

## Dari `%`-format: msgid-nya berubah, jadi terjemahannya menjadi fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Sintaks printf hidup *di dalam* pesannya, jadi menggantinya berarti menulis
ulang kunci katalognya. Tidak ada jalan memutar untuk itu, dan itulah biaya
jujur dari meninggalkan `%(name)s`:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` mengenali pesan baru itu sebagai kerabat dekat pesan yang
dihapus dan membawa terjemahan lamanya menyeberang, ditandai fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Tiga hal yang perlu diketahui tentang keadaan itu:

- **Tidak ada yang rusak saat runtime.** Entri fuzzy dikecualikan dari `.mo`
  hasil kompilasi, jadi aplikasi merender pesan sumbernya sampai seorang
  manusia mengonfirmasi pasangan itu — [degradasi yang sama](workflow.md#the-cycle-after-the-first-translation)
  yang dilalui setiap pesan yang kata-katanya diubah.
- **`pybabel compile` melaporkan setiap entrinya**, karena `%(name)s` yang
  terbawa bukan placeholder brace yang valid, dan ia keluar dengan status
  bukan nol. Daftar itu adalah antrean kerja Anda, bukan alarm palsu; entri di
  dalamnya memang benar-benar perlu disunting.
- **Flag `python-format` lama ikut menumpang** dan sebaiknya dihapus bersama
  flag `fuzzy`, atau `msgfmt --check-format` akan terus menerapkan aturan
  printf pada pesan brace-format.

Untuk placeholder printf bernama, suntingannya bersifat mekanis — `%(name)s`
menjadi `{name}` dan tidak ada lagi yang bergeser — sehingga katalog besar
berarti satu jalannya skrip diikuti tinjauan seorang penerjemah, alih-alih
penerjemahan ulang. `%s` posisional tidak mekanis: ia tidak punya nama untuk
dibawa menyeberang, dan memilih nama itulah inti perubahannya.

Karena itu, urutan praktisnya adalah memigrasikan pesan `%`-format secara
terencana — satu modul, satu rilis, satu bahasa pada satu waktu — alih-alih
dalam satu sapuan yang membuat setiap katalog merah sekaligus.

## Panggilan lama dan baru berdampingan { #old-and-new-calls-coexist }

Ekstraktor yang membaca t-string juga membaca panggilan gettext biasa, jadi
satu pemetaan mencakup sebuah berkas yang sedang di tengah migrasi:

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

Kedua pesan mendarat di templat yang sama, dan hanya yang t-string yang membawa
komentar penanda yang menyalakan pemeriksaan ekstra pustaka ini:

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

Ia mengenali `_()`, keempat nama gettext standar, alias `tr()` / `ntr()`, serta
`lazy_gettext()` / `lazy_pgettext()` yang tertunda. Sebuah helper milik Anda
sendiri harus [disebutkan di pemetaannya](extraction.md#registering-your-own-function-names).

Saat runtime kedua gaya itu sama-sama mandiri: `gettext.translation()`
mengembalikan satu objek terjemahan, dan baik `_` maupun titik masuk pustaka
ini membaca dari objek tersebut.

## Apa yang tidak berpindah { #what-does-not-move }

- **Bahasa templat.** `{% trans %}` milik Jinja2, tag templat Django, dan
  ekstraktor Babel mereka tetap bekerja tanpa perubahan dan tetap memasok
  katalog PO yang sama. t-string adalah sintaks Python; ia berlaku untuk kode
  sumber Python.
- **Berkas katalog Anda.** Tanpa perubahan format, tanpa berkas baru, tanpa
  langkah konversi.
- **Platform penerjemahan Anda.** Pertukaran `.po`-nya identik, dan flag
  `python-brace-format` yang dibawa pesan t-string adalah flag yang sama yang
  dibawa pesan `.format()` — jadi QA placeholder tetap berfungsi.
- **Kode non-Python.** Katalog JavaScript atau C di proyek yang sama tidak
  terpengaruh.

## Daftar periksa migrasi { #a-migration-checklist }

1. Tambahkan extra `babel` di tempat `pybabel` berjalan, dan ubah pemetaan
   `python` di `babel.cfg` menjadi metode `gettext_tstrings` — satu pemetaan
   kemudian mencakup kedua gaya, dan `-k` tetap berfungsi untuk panggilan
   biasanya.
2. Konversikan titik panggilan `.format()` lebih dulu. Ekstrak ulang, jalankan
   `pybabel update`, dan commit katalognya bersama kodenya; jangan harapkan
   ada entri fuzzy.
3. Konversikan titik panggilan `%`-format dalam kelompok yang dapat Anda
   tinjaukan, sambil menulis ulang placeholder yang terbawa dan membersihkan
   flag `fuzzy` serta `python-format`.
4. Perbaiki apa yang ditolak pembatasannya: sebuah interpolasi harus berupa
   nama polos, jadi `t"Hello {user.name}"` menjadi variabel lokal lebih dulu.
   Ini suntingan di titik panggilan, bukan di katalog.
5. Nyalakan `strict = true` di pemetaan ekstraktor setelah sapuannya selesai,
   sehingga pesan yang tidak dapat diekstrak menggagalkan
   [build-nya](extraction.md#lenient-locally-strict-in-ci) alih-alih lenyap
   dari templat.
6. Tambahkan pemeriksaan runtime dari [Dalam produksi](workflow.md#what-ci-gates):
   render satu pesan per bahasa yang dikirim melalui `Translator` yang strict.

Langkah 2 dan 3 adalah commit biasa. Tidak ada apa pun dalam daftar ini yang
membutuhkan hari-H.
