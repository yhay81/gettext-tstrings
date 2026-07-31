---
description: "Terjemahkan pesan t-string secara utuh melalui gettext dan Babel, dengan pemformatan yang dijaga tetap di luar katalog."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Tulis kalimatnya sekali.<br>Terjemahkan seutuhnya.

Integrasi gettext dan Babel yang aman untuk t-string Python 3.14+ — nilainya
tetap di tempat, dan katalog melihat pesan seutuhnya:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Mulai tutorial :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Mengapa t-string](comparison.md){ .md-button }

Situs ini mempraktikkan apa yang didokumentasikannya: setiap edisi bahasa —
navigasi, label, dan laporan build yang sadar bentuk jamak — dirender dari
katalog PO oleh
[`gettext-tstrings` itu sendiri](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Katalog menerima kalimat lengkap `Hello {name}`. Sebuah terjemahan boleh
mengurutkan ulang atau mengulang `{name}`; ia tidak boleh menghilangkannya,
mengarang yang baru, atau menambahkan pemformatan sendiri — pustaka ini
memeriksanya, dan katalog yang rusak kembali ke teks sumber alih-alih membuat
aplikasi crash.

!!! note "Baru mengenal gettext? Seluruh alur kerjanya dalam empat kalimat"

    **gettext** adalah cara standar perangkat lunak diterjemahkan, di Python
    dan jauh di luarnya. Kode Anda menandai string yang dapat diterjemahkan;
    sebuah *ekstraktor* mengumpulkannya ke dalam berkas templat (`.pot`);
    seorang penerjemah — biasanya bukan programmer — mengisi satu berkas
    katalog (`.po`) per bahasa, yang dikompilasi menjadi `.mo` biner yang
    dimuat aplikasi Anda saat runtime. Nama konvensional untuk fungsi
    penerjemah adalah `_`, sehingga `_(t"Hello {name}")` terbaca sebagai
    "terjemahkan kalimat ini". **[Tutorial](tutorial.md)** menempuh seluruh
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

## Pilihan yang diambilnya { #the-choice-it-makes }

- Menerjemahkan pesan secara utuh, tidak pernah penggalan kalimat.
- Hanya menerima nama variabel sederhana seperti `{name}`.
- Menjaga `!r` dan `:.2f` di bawah kendali aplikasi, di luar katalog.
- Membiarkan penerjemah mengurutkan ulang dan mengulang placeholder yang
  dikenal — tetapi tidak memanggil atribut, dan tidak menambahkan perilaku
  pemformatan.
- Menggunakan kembali berkas POT, PO, dan MO biasa, serta perkakas yang sudah
  membacanya.

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

Tiga jenis pembaca tiba di sini: orang yang menerjemahkan program pertamanya,
orang yang memasang penerjemahan ke proyek nyata, dan orang yang ingin tahu
persis mengapa mesinnya berbentuk seperti ini. Masing-masing punya jalurnya.

**Mempelajarinya** — tanpa mengandaikan pengalaman gettext:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — mulai di sini: dari direktori kosong ke
  terjemahan bahasa Jepang yang berjalan dalam lima langkah, setiap perintah
  ditampilkan dengan keluarannya.
- **[Mengapa t-string](comparison.md)** — pesan yang sama ditulis empat cara,
  dan apa yang `%(name)s`, `.format()`, serta `$`-string masing-masing serahkan
  ke katalog.
- **[Latar belakang](background.md)** — mengapa pustaka ini ada: tiga puluh
  tahun gettext, dua PEP, dan diskusi stdlib yang ditutup tanpa jawaban.

</div>

**Menggunakannya secara serius** — referensi kerjanya:

<div class="grid cards" markdown>

- **[Panduan](guide.md)** — API runtime: bentuk jamak, bahasa per permintaan,
  string tertunda, dan apa yang terjadi ketika sebuah katalog salah.
- **[Ekstraksi](extraction.md)** — referensi `pybabel`: konfigurasi, nama
  fungsi kustom, dan bagaimana perkakas yang sudah ada memvalidasi katalog ini
  secara cuma-cuma.
- **[Dalam produksi](workflow.md)** — putaran itu sebagaimana dijalankan
  sebuah tim: siklus pembaruan, entri fuzzy, gerbang CI, platform
  penerjemahan, dan bahasa per permintaan di aplikasi web.
- **[API](api.md)** — semua yang diekspor paket ini, dalam satu halaman.

</div>

**Memahaminya** — dari prinsip hingga implementasi:

<div class="grid cards" markdown>

- **[Cara kerjanya](internals.md)** — dari objek template PEP 750 hingga
  string yang dirender, dan cache yang membuat pemeriksaannya murah.
- **[Spesifikasi](spec.md)** — konvensi t-string ↔ msgid sebagai kontrak yang
  stabil dan berversi, dengan suite konformans yang terbaca mesin.

</div>

## Status { #status }

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
