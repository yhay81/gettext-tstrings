---
description: "Terjemahkan pesan t-string secara utuh melalui gettext dan Babel, dengan nilai dan pemformatan yang dijaga tetap di luar katalog."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Terjemahkan pesan lengkap<br>dengan t-string Python

`gettext-tstrings` menghubungkan t-string Python 3.14+ ke katalog gettext
standar dan perkakas Babel. Nilai dan pemformatan tetap di kode aplikasi;
penerjemah bekerja dengan pesan lengkap dan placeholder `{name}` yang
sederhana:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Katalog memuat `Hello {name}`. Sebuah terjemahan boleh memindahkan atau
mengulang `{name}`. Bila ia menghilangkan, mengganti nama, atau mengubah
pemformatan placeholder itu, validasi katalog melaporkan kesalahannya. Bila
sebuah entri tak sah tetap sampai ke produksi, pustaka ini mencatat sebuah
peringatan dan merender pesan sumbernya alih-alih membuat aplikasi crash.

[Mulai tutorial lima menit :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Bandingkan alternatifnya](comparison.md){ .md-button }

Alpha · Python 3.14+ · katalog PO/MO standar · tanpa dependensi runtime pihak ketiga
{ .home-facts }

Situs ini mempraktikkan apa yang didokumentasikannya: setiap edisi bahasa —
navigasi, label, dan laporan build yang sadar bentuk jamak — dirender dari
katalog PO oleh
[`gettext-tstrings` itu sendiri](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Apakah ini untuk Anda? { #is-this-for-you }

**Cocok hari ini bila** aplikasi Anda berjalan di Python 3.14 atau lebih baru;
Anda sudah memakai gettext dan Babel, atau ingin mengadopsi alur kerja PO/MO
mereka; dan Anda menginginkan sintaks t-string dengan placeholder bernama yang
diperiksa sebelum dirender.

**Belum cocok bila** Anda membutuhkan Python 3.13 atau lebih lama; Anda
menuntut API Python yang stabil — ini sebuah alpha, dan
[spesifikasinya](spec.md) adalah bagian yang sudah mengendap; atau hampir
seluruh teks Anda yang dapat diterjemahkan berada di bahasa templat alih-alih
di sumber Python.

Sudah punya katalog? Katalog itu tetap bekerja.
`_("Hello {name}").format(name=name)` dan `tr(t"Hello {name}")` menghasilkan
msgid yang sama, sehingga terjemahan yang ada selamat melewati peralihannya —
[Migrasi](migration.md) menempuh keseluruhan perpindahannya.

## Apa yang boleh dikatakan katalog { #what-the-catalog-may-say }

**Sebuah terjemahan tidak dapat mengubah struktur pesan yang
diterjemahkannya.** Itulah keseluruhan janjinya, dan selebihnya situs ini
mengikuti darinya. Sebuah terjemahan boleh mengurutkan ulang atau mengulang
`{name}`, dan boleh menulis ulang setiap kata lain di sekelilingnya. Ia tidak
boleh menghilangkan placeholder-nya, mengarang yang baru, menjangkau lewat
placeholder itu ke dalam objek Anda, atau menambahkan pemformatan sendiri.

Pustaka ini memeriksanya saat masuk — ketika katalog dikompilasi — dan sekali
lagi saat perenderan, dan itulah bedanya antara kekeliruan yang ditemukan di
peninjauan dan kekeliruan yang ditemukan oleh seorang pengguna.

!!! note "Baru mengenal gettext? Seluruh alur kerjanya dalam empat kalimat"

    **gettext** adalah cara standar perangkat lunak diterjemahkan, di Python
    dan jauh di luarnya. Kode Anda menandai pesan yang dapat diterjemahkan;
    sebuah *ekstraktor* mengumpulkannya ke dalam berkas templat (`.pot`);
    seorang penerjemah — biasanya bukan programmer — mengisi satu berkas
    katalog (`.po`) per bahasa, yang dikompilasi menjadi `.mo` biner yang
    dimuat aplikasi Anda saat runtime. Nama konvensional untuk fungsi
    penerjemah adalah `_`, sehingga `_(t"Hello {name}")` terbaca sebagai
    "terjemahkan pesan ini". **[Tutorial](tutorial.md)** menempuh seluruh
    jalurnya — tandai, ekstrak, terjemahkan, kompilasi, jalankan — dalam
    sekitar lima menit.

## Masalah yang dipecahkannya { #the-problem-it-solves }

Sebuah f-string sudah terinterpolasi pada saat pustaka mana pun melihatnya —
`f"Hello {name}"` telah menjadi `"Hello Ada"`, dan menerjemahkan
penggalan-penggalan di sekeliling sebuah nilai merusak tata bahasa sebagian
besar bahasa. Sebuah t-string ([PEP 750]) menjaga teks statis, nilai yang
telah dievaluasi, ekspresi sumber, konversi, dan format spec tetap terpisah —
tepat pemisahan yang dibutuhkan sebuah katalog pesan.
[Apa yang berubah karenanya](comparison.md), dibandingkan dengan `%(name)s`,
`.format()`, dan `$`-string.

Namun tidak ada apa pun dalam gettext atau Babel yang menetapkan bagaimana
sebuah t-string menjadi sebuah pesan. Pustaka ini mengambil pilihan itu,
menuliskannya sebagai [spesifikasi berversi](spec.md), dan menyertakan
[suite konformans](spec.md#conformance) untuk memeriksanya.

## Aturan desainnya { #the-design-rules }

- Menerjemahkan pesan secara utuh, tidak pernah penggalan kalimat.
- Hanya menerima nama variabel sederhana seperti `{name}`.
- Menjaga `!r` dan `:.2f` di bawah kendali aplikasi, di luar katalog.
- Mengizinkan terjemahan mengurutkan ulang dan mengulang placeholder yang
  dikenal, sekaligus mencegahnya menjangkau atribut atau menambahkan
  pemformatan.
- Menggunakan kembali berkas POT, PO, dan MO biasa, serta perkakas yang sudah
  membacanya.

Dan daftar penyandingnya, apa yang sengaja tidak disentuhnya: ia tidak
melokalkan angka, mata uang, atau tanggal —
[format semua itu lebih dulu](guide.md#locale-aware-values) dengan Babel; ia
tidak meng-escape keluaran yang dirender untuk HTML, shell, atau terminal; dan
ia tidak dapat menilai apakah sebuah terjemahan *benar*, hanya apakah
placeholder-nya utuh.

## Instalasi { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 atau lebih baru. **Rendering tidak memiliki dependensi** — ia
menggunakan `gettext` dari pustaka standar dan tidak yang lain.

Ekstraksi dan validasi katalog berjalan melalui [Babel], jadi pasang extra itu
di mana pun `pybabel` berjalan, yang biasanya lingkungan pengembangan atau CI
dan bukan image produksi:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Ke mana selanjutnya { #where-to-go-next }

**Mulai di sini** — tanpa mengandaikan pengalaman gettext:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — dari direktori kosong ke terjemahan bahasa
  Jepang yang berjalan dalam lima langkah, setiap perintah ditampilkan dengan
  keluarannya.
- **[Mengapa t-string](comparison.md)** — pesan yang sama ditulis empat cara,
  dan apa yang `%(name)s`, `.format()`, serta `$`-string masing-masing serahkan
  ke katalog.

</div>

**Menggunakannya** — referensi kerjanya:

<div class="grid cards" markdown>

- **[Panduan](guide.md)** — API runtime: titik masuk mana yang dipakai, bentuk
  jamak, bahasa per permintaan, string tertunda, dan apa yang terjadi ketika
  sebuah katalog salah.
- **[Ekstraksi](extraction.md)** — referensi `pybabel`: konfigurasi, nama
  fungsi kustom, dan bagaimana perkakas yang sudah ada memvalidasi katalog ini
  secara cuma-cuma.
- **[Dalam produksi](workflow.md)** — putaran itu sebagaimana dijalankan
  sebuah tim: siklus pembaruan, entri fuzzy, gerbang CI, platform
  penerjemahan, dan pengiriman.
- **[Migrasi](migration.md)** — mengadopsi ini di proyek yang sudah punya
  katalog, satu tempat pemanggilan pada satu waktu.
- **[Untuk penerjemah](translators.md)** — satu halaman untuk diserahkan
  kepada siapa pun yang menyunting berkas `.po`.

</div>

**Memahaminya** — dari sejarah hingga implementasi:

<div class="grid cards" markdown>

- **[Latar belakang](background.md)** — mengapa pustaka ini ada: tiga puluh
  tahun gettext, dua PEP, dan diskusi stdlib yang ditutup tanpa jawaban.
- **[Jebakan umum](pitfalls.md)** — apa yang benar-benar rusak ketika situs ini
  diterjemahkan ke tiga puluh lima bahasa, dan separuh mana yang dapat
  ditangkap sebuah perkakas.
- **[Cara kerjanya](internals.md)** — dari objek template PEP 750 hingga
  string yang dirender, dan cache yang membuat pemeriksaannya murah.

</div>

**Referensi** — kontraknya:

<div class="grid cards" markdown>

- **[API](api.md)** — semua yang diekspor paket ini, dalam satu halaman.
- **[Spesifikasi](spec.md)** — konvensi t-string ↔ msgid sebagai kontrak yang
  stabil dan berversi, dengan suite konformans yang terbaca mesin.

</div>

## Status { #status }

| | |
| --- | --- |
| Versi paket | 0.1.0a8 |
| Stabilitas API | alpha — API Python-nya masih mungkin berubah |
| [Spesifikasi](spec.md) | v1, dengan [suite konformans](spec.md#conformance) |
| Python | 3.14 dan yang lebih baru; diuji pada 3.14, 3.14t (free-threaded), dan 3.15 |
| Babel | 2.18 atau yang lebih baru, dan hanya di tempat `pybabel` dijalankan |
| Dependensi runtime | tidak ada — `gettext` dari pustaka standar |
| Format katalog | POT, PO, dan MO biasa |
| Perubahan | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Sebuah alpha. Kontraknya sengaja dibuat kecil dan [spesifikasi](spec.md)
adalah bagiannya yang stabil; API Python-nya masih mungkin bergerak. Sebelum
rilis stabil, proyek ini membutuhkan fixture bahasa yang lebih luas, pelacakan
performa berkelanjutan, tinjauan API dari orang-orang yang menggunakan gettext
dan Babel secara serius, serta pengujian kompatibilitas di setiap rilis Python
dan Babel yang didukung.

[Issue dan pull request](https://github.com/yhay81/gettext-tstrings/issues)
disambut baik — alpha justru saat antarmuka masih layak diperdebatkan.

## Bergabung dengan komunitas { #join-the-community }

- Pilih sebuah
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  untuk kontribusi yang terbatas jelas.
- Ajukan pertanyaan penggunaan di
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Bawa alur kerja gettext produksi dan ide API ke
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Baca
  [panduan kontribusi](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  sebelum membuka pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
