---
description: "Tiga puluh tahun gettext, dua PEP berjarak sepuluh tahun, dan diskusi stdlib yang ditutup sebagai not-planned: mengapa pustaka ini ada, dengan tautan ke sumbernya."
---

# Latar belakang

Pustaka ini berdiri di titik temu dua cerita panjang — satu tentang bagaimana
perangkat lunak diterjemahkan, satu tentang bagaimana Python menginterpolasi
string — yang akhirnya bersilangan pada 2025 lalu terhenti tepat di titik
tempat sebuah konvensi kecil yang cermat dibutuhkan. Halaman ini menceritakan
kedua cerita itu, dengan tautan ke sumbernya, karena keputusan desain di situs
ini lebih mudah dinilai ketika Anda dapat melihat pertanyaan yang dijawabnya.

## Ekosistem gettext { #the-gettext-ecosystem }

[GNU gettext] telah menjadi cara perangkat lunak bebas diterjemahkan sejak
pertengahan 1990-an: tandai string di kode, ekstrak ke sebuah templat, beri
penerjemah satu berkas katalog per bahasa, kompilasi, muat saat runtime. Di
sekeliling putaran itu tumbuh seluruh ekosistem — editor PO, alur kerja
tinjauan, dan platform penerjemahan yang semuanya berbicara format berkas yang
sama — dan Python telah menyertakan [modul `gettext`][stdlib-gettext] di
pustaka standarnya selama lebih dari dua dasawarsa. Paruh runtime dari
penerjemahan tidak pernah menjadi masalahnya.

Paruh yang tak pernah tuntas selalu *seperti apa rupa string katalognya*.
Sebuah pesan `%(name)s` menyerahkan sintaks printf kepada penerjemah yang satu
huruf terhapusnya berubah menjadi crash produksi; sebuah pesan `.format()`
menyerahkan akses atribut pada objek hidup kepada katalog.
([Mengapa t-string](comparison.md) menelusuri keduanya, dengan kegagalannya
dipertontonkan.) Dan f-string — sintaks yang kini paling disukai kode Python —
sama sekali tidak dapat ikut serta: pada saat pustaka mana pun melihatnya, ia
sudah menjadi string jadi. Orang tetap saja mencoba, cukup sering hingga
pelacak issue Babel mengumpulkan percobaan-percobaannya
([#594][babel-594], [#715][babel-715]); kegagalannya struktural, bukan fitur
yang hilang.

## Dua PEP, berjarak sepuluh tahun { #two-peps-ten-years-apart }

Pada 2015, Alyssa Coghlan dan Nick Humrich menulis [PEP 501], mengusulkan
templat interpolasi yang motivasi pertama tertulisnya adalah i18n —
"providing a cleaner syntax for i18n translation", dalam kata-kata PEP itu
sendiri. Usulan itu ditangguhkan, sebagian karena diskusi menunjukkan kasus
i18n membawa pertimbangan tambahan yang signifikan yang tidak dimiliki kasus
penggunaan yang lebih sederhana.

Sepuluh tahun kemudian, [PEP 750] — oleh Jim Baker, Guido van Rossum, Paul
Everitt, Koudai Aono, Lysandros Nikolaou, dan Dave Peck — menghidupkan kembali
gagasan itu sebagai t-string, [diterima pada April 2025][sc-resolution], dan
hadir di [Python 3.14] pada Oktober 2025. PEP 501 lalu ditarik demi PEP itu.
Satu detail penting untuk halaman ini: i18n *tidak* termasuk motivasi tertulis
PEP 750. PEP itu menggeneralisasi mekanismenya — sebuah tipe template yang
dapat dikonsumsi pustaka mana pun — dan meninggalkan pertanyaan penerjemahan
persis di tempat PEP 501 memarkirnya sepuluh tahun sebelumnya: terbuka.

Jadi per Python 3.14, bahasa ini memiliki tepat struktur data yang dibutuhkan
sebuah katalog pesan, dan tanpa konvensi untuk memakainya sebagai itu.

## Diskusi stdlib { #the-stdlib-discussion }

Dua bulan sebelum 3.14 rilis, Adrian Mönnich (ThiefMaster, salah satu
pemelihara proyek Indico) mengusulkan menutup celah itu di pustaka standar
sendiri: utas [Support t-strings in gettext][discuss-thread] di
discuss.python.org, dibuka pada Agustus 2025, datang dengan
[pull request][cpython-pr] yang berfungsi, menambahkan dukungan t-string ke
`gettext` sekaligus `pygettext`.

Utas itu layak dibaca seutuhnya, karena ia memunculkan setiap pertanyaan sulit
yang belakangan harus dijawab pustaka ini:

- **Apa yang boleh menjadi sebuah interpolasi?** Nama sederhana saja, atau
  atribut dan pemanggilan dengan nama placeholder turunan? Setiap jawaban
  menukar kenyamanan dengan stabilitas msgid dan keamanan katalog.
- **Apa yang dituntut bentuk jamak,** ketika sistem jamak bahasa sasaran
  berbeda dari bahasa sumber?
- **Apakah gettext bahkan sasaran yang tepat?** Barry Warsaw — yang selama
  pengembangan PEP 750 berargumen bahwa t-string bukan pasangan yang baik
  untuk i18n — menunjuk ke [`flufl.i18n`][flufl-i18n] miliknya dan gaya
  `$`-string-nya sebagai perkakas yang lebih ramah; yang lain berargumen untuk
  meninggalkan gettext sama sekali demi sistem yang lebih baru seperti
  [Fluent].
- **Dan pertanyaan-metanya:** apa pun yang dirilis pustaka standar, pada
  dasarnya tidak pernah bisa berubah. Konvensi dengan sebanyak ini pilihan
  terbuka adalah hal yang berisiko untuk dibekukan pada percobaan pertama.

Tidak ada konsensus yang terbentuk. Issue CPython
[ditutup sebagai "not planned"][cpython-issue] dan pull request-nya ditutup
tanpa di-merge pada Oktober 2025, beberapa hari setelah rilis 3.14.
Kemampuannya ada di bahasa; konvensinya tak punya rumah.

## Mengapa sebuah paket, lebih dulu { #why-a-package-first }

Itulah celah yang dipilih proyek ini untuk diisi dari luar pustaka standar,
atas sebuah taruhan yang disengaja: sebuah konvensi lebih cepat matang di
tempat ia bisa berversi dengan bebas dan meraih adopsi kasus demi kasus, dan
pustaka standar — yang harus benar sejak percobaan pertama — adalah tempat
sebuah konvensi seharusnya *berakhir*, bukan tempat ia digodok.

Konkretnya, setiap pertanyaan yang diperdebatkan di utas itu punya jawaban
tertulis di sini, masing-masing di halamannya sendiri:

- Interpolasi adalah **nama sederhana saja**, sehingga msgid tetap stabil dan
  bermakna — [panduan](guide.md#safety-and-scope) menunjukkan aturannya,
  [Cara kerjanya](internals.md#from-template-to-msgid) alasannya.
- **Pemformatan tetap di luar katalog** sepenuhnya
  ([Mengapa t-string](comparison.md)).
- **Bentuk jamak** mengikuti aturan union/interseksi yang membiarkan sistem
  jamak bahasa sasaran berbeda dari bahasa sumber ([spec §4](spec.md)).
- Katalog yang rusak **kembali ke teks sumber alih-alih crash**, menjaga
  kontrak gettext sendiri
  ([panduan](guide.md#what-happens-when-a-catalog-is-wrong)).
- Dan seluruh konvensinya adalah [spesifikasi berversi](spec.md) dengan suite
  konformans terbaca mesin — ditulis agar implementasi lain, termasuk
  implementasi pustaka standar di masa depan, dapat mengadopsinya tanpa
  perubahan dan saling beroperasi.

Diskusinya belum berakhir, dan proyek ini adalah peserta di dalamnya, bukan
vonis atasnya. Jika Anda punya pengalaman gettext produksi yang relevan dengan
pilihan-pilihan ini, [utas yang sama][discuss-thread] dan
[Discussions][gh-discussions] repositori ini adalah tempat diskusinya
berlanjut.

## Linimasa { #timeline }

| Kapan | Apa yang terjadi |
| --- | --- |
| pertengahan 1990-an | GNU gettext menetapkan alur kerja PO/POT/MO yang masih dipakai penerjemah dan platform. |
| 2015 | [PEP 501] mengusulkan templat interpolasi, dengan i18n sebagai motivasi pertamanya; ditangguhkan. |
| 2016 | f-string hadir di Python 3.6 — interpolasi mendapatkan sintaksnya, dan penerjemahan tidak dapat memakainya. |
| Jul 2024 | [PEP 750] mengusulkan t-string. |
| Apr 2025 | PEP 750 [diterima][sc-resolution]; PEP 501 ditarik demi PEP itu. |
| Agu 2025 | Utas [Support t-strings in gettext][discuss-thread] dibuka, dengan sebuah [pull request][cpython-pr] stdlib. |
| Okt 2025 | [Python 3.14] menghadirkan t-string; issue stdlib ditutup sebagai [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` rilis sebagai alpha, dengan [spec v1](spec.md) dan suite konformansnya. |

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
