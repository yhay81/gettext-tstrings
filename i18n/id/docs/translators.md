---
description: "Kontrak placeholder untuk siapa pun yang menyunting berkas .po: apa yang boleh Anda ubah, apa yang harus Anda biarkan, dan cara membaca galatnya."
---

# Untuk penerjemah

Halaman ini untuk orang yang menyunting katalog, bukan orang yang menulis
kode. Ia sengaja dibuat pendek, dan dimaksudkan untuk ditautkan atau disalin
ke instruksi penerjemah milik sebuah proyek.

Tidak ada di sini yang menuntut Anda membaca Python. Semua di sini tentang satu
hal: bagian-bagian sebuah pesan yang berada di dalam kurung kurawal.

## Apa itu placeholder { #what-a-placeholder-is }

Sebuah pesan di dalam katalog bisa memuat nama di dalam kurung kurawal:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` adalah sebuah **placeholder**. Ketika program menampilkan pesan ini,
ia mengganti `{name}` dengan sebuah nilai yang disediakannya — nama seseorang,
nama berkas, sebuah angka. Placeholder bukan kata untuk diterjemahkan; ia
sebuah slot.

Terjemahan Anda masuk ke `msgstr`, dan terjemahan itu harus mempertahankan slot
tersebut:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Apa yang boleh Anda ubah, dan apa yang tidak { #what-you-may-change-and-what-you-may-not }

Anda **boleh**:

- **Memindahkan sebuah placeholder** ke mana pun tata bahasa bahasa sasaran
  menginginkannya, termasuk ke depan pesan.
- **Mengulang sebuah placeholder** jika bahasanya membutuhkan nilai itu dua
  kali.
- **Menulis ulang setiap kata lain**, termasuk tanda baca, spasi, dan urutan
  kalimat.

Anda **tidak boleh**:

- **Menerjemahkan nama di dalam kurung kurawal.** `{name}` tetap `{name}`,
  bahkan dalam bahasa yang tidak menulis apa pun selainnya dengan huruf Latin.
- **Menghapus kurung kurawalnya**, atau menulis namanya tanpa kurung kurawal.
- **Mengganti kurung kurawal ASCII `{` `}` dengan `｛` `｝` lebar penuh.**
  Banyak metode input menghasilkan bentuk lebar penuh; keduanya tampak nyaris
  sama dan tidak bekerja.
- **Menambahkan pemformatan**, seperti `{name!r}` atau `{amount:.2f}`.
  Bagaimana sebuah nilai ditampilkan diputuskan di dalam program, bukan di
  dalam katalog.
- **Mengarang sebuah placeholder** yang tidak ada di `msgid`.

Jika sebuah pesan membutuhkan nilai yang tidak ditawarkan aslinya, itu pesan
yang harus diubah oleh pengembangnya. Katakan demikian alih-alih mengakalinya.

## Bentuk jamak { #plural-forms }

Sebuah pesan berhitungan datang dengan satu slot `msgstr` per bentuk jamak
dalam bahasa Anda, dan bahasa Anda sendirilah yang menentukan berapa
jumlahnya — satu untuk bahasa Jepang, dua untuk Jerman, tiga untuk Rusia, enam
untuk Arab. Isi setiap slot yang diberikan katalog kepada Anda.

Dua aturan yang sering menjebak orang:

- **Slot-slot itu bukan "tunggal, jamak, lebih jamak".** Setiap indeks berarti
  apa pun yang dikatakan aturan jamak bahasa Anda. Bentuk ketiga bahasa Latvia
  khusus untuk nol saja; bentuk kedua bahasa Slovenia untuk tepat dua; bahasa
  Wales menaruh kasus umumnya di indeks 0 dan bentuk tunggalnya di indeks 1.
- **Dua slot boleh secara sah memuat teks yang sama.** Dalam bahasa Turki,
  Hungaria, Persia, dan Bengali sebuah kata benda tetap tunggal setelah
  numeral, sehingga kedua bentuk sebuah pesan berhitungan adalah string yang
  sama. Itu benar, bukan keteledoran salin-tempel.

Aturan placeholder di atas berlaku untuk setiap bentuk secara terpisah.

## Entri fuzzy { #fuzzy-entries }

Sebuah entri yang ditandai `fuzzy` adalah tebakan mesin: pengembangnya mengubah
pesan aslinya, dan perkakasnya memasangkan teks baru itu dengan terjemahan lama
Anda agar Anda punya titik awal.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Entri fuzzy **tidak dipakai oleh program** — ia menampilkan teks asli yang
belum diterjemahkan — sampai seseorang merevisi teksnya dan menghapus penanda
`fuzzy`. Sebagian besar editor PO punya tombol untuk persis hal itu.

## Membaca pesan kegagalan { #reading-a-failure-message }

Perkakasnya memeriksa placeholder ketika katalog dikompilasi, dan pesannya
ditulis untuk Anda alih-alih untuk seorang programmer. Melaporkan hanya bahwa
`{name}` hilang adalah jalan buntu ketika Anda dapat melihat karakter-karakter
itu di depan Anda, jadi di tempat sebuah placeholder tampak ada padahal tidak,
pesannya menjelaskan mengapa. Terhadap teks asli `Hello {name}`, masing-masing
di bawah dilaporkan di bawah
`translation does not match the source placeholders:`

| Terjemahan Anda berkata | Alasan yang diberikannya |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Karakter yang tidak dapat terlihat mendapat perlakuannya sendiri. Sebuah
no-break space di dalam kurung kurawal adalah sesuatu yang dihasilkan metode
input dan tidak ditampilkan editor mana pun, jadi pesannya mencetaknya sebagai
titik kode alih-alih menyebut karakter yang tidak akan pernah dapat Anda
temukan:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Sebuah nama yang huruf-hurufnya mencampur sistem tulisan — kasus homoglif, di
mana `а` Kiril tak terbedakan dari yang Latin — ditampilkan dua kali, sekali
terbaca dan sekali di-escape, yang merupakan satu-satunya bentuk yang
membedakan keduanya:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Disambiguasi yang sama berlaku ketika sebuah nama Yunani atau Kiril yang
ditulis seluruhnya dalam satu aksara berkonflik dengan nama sumber ASCII,
termasuk kasus satu huruf `a` Latin / `а` Kiril.

Jika Anda menemui salah satunya dan perbaikannya tidak jelas, langkah amannya
adalah menghapus placeholder yang Anda ketik dan menyalin yang ada di `msgid`.

## Apa yang tidak dapat dilakukan pemeriksaannya { #what-the-checks-cannot-do }

Perkakasnya memverifikasi bahwa placeholder Anda utuh. Ia tidak dapat
menentukan apakah terjemahannya akurat, wajar, atau tepat untuk konteksnya —
itu sepenuhnya tetap di tangan Anda.

Dua hal yang lebih membantu daripada pemeriksaan mana pun:

- **Baca komentar penerjemah.** Sebuah baris yang diawali `#.` di atas pesannya
  adalah pengembang yang memberi tahu Anda di mana pesan itu muncul dan apa
  artinya.
- **Tanyakan tentang `msgctxt`.** Ketika kata yang sama muncul dua kali dengan
  konteks berbeda, itu karena keduanya perlu diterjemahkan secara berbeda —
  "Open" sang tombol dan "Open" sang keadaan, misalnya.
