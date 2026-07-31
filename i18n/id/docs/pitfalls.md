---
description: "Apa yang sebenarnya rusak ketika satu situs kecil diterjemahkan ke tiga puluh lima bahasa, mana di antaranya yang dapat ditangkap pustaka ini untuk Anda, dan mana yang tidak."
---

# Jebakan umum

Situs ini diterjemahkan ke tiga puluh lima bahasa, dan setiap edisinya
dihasilkan dengan menjalankan putaran yang diajarkan dokumentasi ini. Itu
korpus yang kecil menurut ukuran industri, dan tetap saja cukup untuk menabrak
sebagian besar jebakan yang membuat i18n lebih sulit daripada tampaknya.

Setiap bagian di bawah adalah sesuatu yang benar-benar salah di sini, seperti
apa tampaknya saat itu, dan di mana garis batasnya jatuh antara apa yang
diperiksa pustaka ini untuk Anda dan apa yang tetap memerlukan pertimbangan
manusia.

## Mengganti nama variabel menerjemahkan ulang sebuah kalimat { #renaming-a-variable-retranslates-a-sentence }

msgid adalah kunci katalog, dan sebuah nama yang diinterpolasi berada *di
dalamnya*. Memindahkan satu konstanta ke lingkup modul dan menuliskannya dengan
huruf kapital sebagaimana diminta gaya Python — `author` menjadi `AUTHOR` —
mengubah `Copyright © 2026 {author} · MIT License` menjadi sebuah pesan yang
belum pernah dilihat katalog mana pun. Setiap terjemahan baris itu akan kembali
melewati siklus fuzzy, di setiap bahasa, demi penggantian nama yang tidak
mengubah apa pun yang dapat dilihat pembaca.

Pustaka ini tidak akan menghentikan Anda: kedua penulisan itu adalah nama
placeholder yang sah. Yang ia lakukan adalah membuat nama itu *layak*
dilindungi — sebuah interpolasi harus berupa
[nama polos](internals.md#from-template-to-msgid), sehingga yang ada di kunci
katalog adalah kata yang dapat dibaca seorang penerjemah, bukan sebuah
ekspresi.

Kasus cerminnya aman secara konstruksi. Conversion dan format spec bukan bagian
dari msgid, jadi memperketat `{amount:,.2f}` menjadi `{amount:,.0f}` tidak
mengubah kunci apa pun dan tidak membatalkan terjemahan mana pun di mana pun.

## `nplurals=2` tidak berarti dua string yang berbeda { #nplurals-2-does-not-mean-two-different-strings }

Bahasa Turki, Hungaria, Persia, dan Bengali semuanya mendeklarasikan dua bentuk
jamak, dan di keempatnya kedua bentuk sebuah pesan berhitungan secara sah
adalah *string yang sama* — nominanya tetap tunggal setelah kata bilangan,
sehingga `{n} sayfa` benar untuk satu halaman maupun untuk sepuluh. Seorang
pemeriksa yang "memperbaiki" duplikasi itu justru merusak terjemahannya.

Kesalahan sebaliknya sama mudahnya. Bentuk ketiga bahasa Latvia ada untuk
**nol saja**; bentuk kedua bahasa Slovenia adalah **dual**, untuk tepat dua;
bentuk terakhir bahasa Rumania memerlukan kata `de` yang justru tidak boleh ada
di dua bentuk pertamanya. Mengisi slot-slot itu dengan sebuah bentuk tunggal
dan sebuah bentuk jamak menghasilkan katalog yang salah hanya untuk hitungan
yang tidak diuji siapa pun.

Lebih buruk lagi, *urutan* slotnya tidak bersifat semantis. Bahasa Wales
mengindeks kelima bentuknya sehingga `msgstr[0]` adalah kasus umum dan
`msgstr[1]` adalah bentuk tunggal. Mengisinya menurut urutan yang tampak jelas
menempatkan bentuk tunggal tepat di tempat yang akan ditemukan setiap pesan
tanpa hitungan.

Pustaka ini tidak mengambil satu pun dari itu ke pundaknya, dan justru itulah
intinya: aturan jamak bahasa sasaran tinggal di header katalognya sendiri, dan
[aturan union/interseksi](spec.md) membiarkan sebuah terjemahan memiliki lebih
banyak bentuk, atau lebih sedikit, daripada sumbernya. Yang ia periksa adalah
satu-satunya hal yang dapat ia periksa tanpa mengetahui bahasanya — bahwa
setiap bentuk mempertahankan placeholder yang dibutuhkannya.

## Dua bentuk bisa identik karena suatu alasan { #two-forms-can-be-identical-for-a-reason }

Bahasa Irlandia punya lima bentuk jamak, dan di laporan build situs ini
beberapa di antaranya dieja sama persis. Itu bukan keteledoran salin-tempel:
*leathanach* diawali `l`, dan tak satu pun dari kedua mutasi awal yang dipicu
kata bilangan Irlandia ditulis pada `l`. Bentuk-bentuk itu tetap melakukan
kerja nyata — batang katanya berganti-ganti antara *leathanach* dan
*leathanaigh*, dan hitungan di atas sepuluh kembali ke bentuk tunggal — tetapi
tidak ada nomina yang berarti "halaman" yang akan memperlihatkan kontrasnya.

Pemeriksaan apa pun yang menandai bentuk duplikat sebagai mencurigakan akan
menandai bahasa Irlandia yang benar. Manusia yang menguasai bahasanya adalah
satu-satunya pemeriksa untuk hal ini.

## Sebuah pesan hanya dapat menyesuaikan diri dengan satu hitungan { #a-message-can-only-agree-with-one-count }

Laporan build situs ini menyebutkan berapa banyak halaman yang dirender dan
berapa lama waktunya. Menuliskannya sebagai "Rendered {n} pages in {seconds}
seconds" tampak tidak berbahaya, dan sebenarnya tidak dapat diterjemahkan:
gettext memilih satu bentuk dari satu hitungan, dan hitungan itu adalah `n`.
Kata *seconds* harus menyesuaikan diri dengan sebuah angka yang tidak pernah
dilihat mesin jamaknya.

Perbaikannya adalah menjadikan kuantitas kedua sebuah simbol satuan alih-alih
sebuah kata, dan simbol satuan itu sendiri pun dilokalkan: katalog situs ini
membawa `s`, `с`, `ث`, `שנ׳`, dan `mp`, sementara tipografi Prancis, Spanyol,
dan Swedia menghendaki spasi sebelum simbolnya, yang tidak dikehendaki bahasa
Inggris. Tak satu pun dari itu urusan pustaka ini — tetapi menyadari bahwa
sebuah pesan membutuhkan *dua* penyesuaian adalah urusan Anda, dan satu-satunya
alat untuk itu adalah menuliskan pesannya secara berbeda.

## Menyunting kalimat bahasa Inggris berarti menyunting tata bahasa asing { #editing-an-english-sentence-edits-foreign-grammar }

Halaman beranda dulu berbunyi "all ten language editions". Menghapus angkanya —
sebuah suntingan satu kata dalam bahasa Inggris, dilakukan karena angka itu
terus basi — mengubah subjek jamak menjadi tunggal. Bahasa Spanyol, Italia,
Portugis, Rusia, Ukraina, Yunani, Belanda, dan Ibrani semuanya harus
menyesuaikan ulang verbanya; beberapa juga perlu mengubah partisipnya.

Sebuah suntingan sumber yang terbaca sepele dalam bahasa Inggris tidaklah
sepele di hilir. Menandainya fuzzy, yang persis dilakukan `pybabel update`,
adalah mekanisme yang memberi setiap penerjemah kesempatan untuk menyadarinya.

## Perbedaan tak terlihat selamat dari setiap salin-tempel { #invisible-differences-survive-every-copy-paste }

Panduan mengutip sebuah diagnostik yang memuat `(nаme)` — sebuah escape yang
disengaja, karena karakter yang dinamainya adalah `а` Kiril yang tak dapat
dibedakan pembaca mana pun dari yang Latin. Para penerjemah situs ini mengubah
escape itu menjadi karakter yang sebenarnya **lima kali terpisah**, di lima
bahasa yang berbeda, setiap kali menghasilkan halaman yang tampak benar dan
sebenarnya salah.

Yang ini memang ditangkap pustaka ini, dan itulah alasan diagnostiknya dibentuk
sebagaimana adanya: sebuah placeholder yang huruf-hurufnya mencampur sistem
tulisan [dilaporkan dua kali](internals.md#diagnostics-are-part-of-the-design),
sekali terbaca dan sekali di-escape, karena bentuk escape adalah satu-satunya
penulisan yang membedakan keduanya. Sebuah no-break space di dalam kurung
kurawal dicetak dengan titik kodenya karena alasan yang sama. Pemeriksa katalog
menolak pesannya sebelum ia sempat terkirim.

## Tidak kosong bukan berarti diterjemahkan { #non-empty-is-not-translated }

Sebuah katalog yang dirangka dengan msgid-nya disalin ke msgstr-nya lolos
setiap pemeriksaan naif: tidak ada yang kosong, tidak ada yang fuzzy, himpunan
pesannya cocok persis. Satu edisi situs ini terkirim seperti itu selama
beberapa jam. Begitu pula delapan halaman edisi lain yang merupakan salinan
identik-byte dari sumber bahasa Inggrisnya — yang lolos pemeriksaan yang
membandingkan blok kode di antara keduanya, karena keduanya adalah berkas yang
sama.

Tak satu pun dari keduanya dapat dilihat sebuah pustaka penerjemahan. Keduanya
murah untuk diuji, tetapi bukan dengan mengharuskan setiap entri berbeda dari
sumbernya: `OK`, nama produk, nama orang, akronim, dan pengidentifikasi kode
semuanya menerjemahkan diri menjadi dirinya sendiri, dan pemeriksaan yang
melarang itu menghasilkan positif palsu selamanya.

Ukurlah *rasionya* sebagai gantinya, atas seluruh katalog atau seluruh
halaman, lalu kirimkan pencilannya ke seorang manusia. Pengujian situs ini
melakukan persis itu — ia membandingkan baris-baris prosa setiap edisi dengan
sumber bahasa Inggrisnya dan gagal di atas 25% identik. Edisi palsu itu berada
di 87%; setiap terjemahan asli berada di antara 4% dan 8%, yang merupakan ekor
kecil berisi baris-baris yang secara sah kebetulan sama, seperti URL dan
keluaran program yang dikutip. Kedua populasi itu cukup berjauhan sehingga
ambangnya tidak perlu presisi.

## Katalog bukan satu-satunya yang diterjemahkan { #the-catalog-is-not-the-only-translated-thing }

Dua kegagalan di sini sama sekali tidak berkaitan dengan gettext.

Menerjemahkan sebuah judul mengubah jangkar yang dihasilkan darinya, sehingga
setiap tautan antarhalaman menuju bagian itu rusak — diam-diam, hanya di bahasa
tersebut. Situs ini memakukan jangkar bahasa Inggris pada setiap judul, dan
sebuah pengujian menurunkan daftar yang diharapkan dari halaman bahasa
Inggrisnya.

Dan generator situs ini mengirimkan terjemahan antarmuka untuk enam puluh
delapan bahasa, yang tidak mencakup bahasa Swahili atau Irlandia. Tanpa salah
satunya, build tidak terdegradasi ke bahasa Inggris; include templatnya gagal
dan edisi itu sama sekali tidak dapat dibangun. Dua berkas milik repositori ini
sendiri ada untuk menambal celah itu.

## Alat Anda pun punya bug { #your-tools-have-bugs-too }

Langkah CI yang direkomendasikan dokumentasi ini untuk menangkap katalog basi,
`pybabel update --check`, tidak dapat melakukan tugas itu untuk proyek mana pun
yang memakai `pgettext` atau `npgettext`. Pada Babel 2.18.0 ia melaporkan setiap
katalog yang memiliki `msgctxt` sebagai kedaluwarsa, pada setiap jalannya.
Pembandingannya berjalan lewat `Catalog.is_identical`, yang mencari setiap pesan
dengan kunci tempat pesan itu disimpan — dan untuk pesan kontekstual kunci itu
adalah pasangan `(id, context)`, yang tidak diterima oleh `Catalog.get`.
Pencariannya tidak mengembalikan apa pun, dan katalognya tidak pernah
dibandingkan sama:

```pycon
>>> from babel.messages.catalog import Catalog
>>> c = Catalog(locale="ja")
>>> c.add("Guide", "ガイド", context="navigation")
<Message 'Guide' (flags: [])>
>>> c.is_identical(c)
False
```

Itu ditemukan di sini dengan mencoba memakainya, dilaporkan ke hulu, dan
pemeriksaan penggantinya ada [di halaman produksi](workflow.md#what-ci-gates).

Pelajaran umumnya adalah yang tidak nyaman: gerbang yang selalu merah lebih
buruk daripada tidak ada gerbang sama sekali, karena sebuah tim akan
mematikannya. Pastikan pemeriksaan CI Anda benar-benar dapat lolos sebelum Anda
memercayainya untuk gagal.

## Untuk apa pustaka ini ada, dalam satu baris { #what-the-library-is-for-in-one-line }

Sebagian besar halaman ini adalah pertimbangan yang tidak dapat diambil alih
alat mana pun. Yang *dapat* dilakukan sebuah alat adalah menjamin bahwa sebuah
terjemahan tidak dapat mengubah struktur kalimat yang diterjemahkannya — tidak
dapat menghilangkan sebuah nilai, mengarang satu, memformat ulang satu, atau
menjangkau ke dalam objek Anda — dan dapat mengatakannya dalam kalimat yang
dapat ditindaklanjuti orang yang harus memperbaikinya. Itulah keseluruhan yang
dijanjikan pustaka ini, dan sisa situs ini adalah bagaimana ia menepatinya.
