---
description: "Konvensi t-string ke msgid sebagai kontrak kecil yang berversi, dengan suite konformans yang terbaca mesin."
---

# Spesifikasi

Anda dapat memakai pustaka ini tanpa membaca halaman ini —
[tutorial](tutorial.md) dan [panduan](guide.md) mencakup penggunaan
sehari-hari. Halaman ini untuk para pembuat perkakas: konvensi yang
diimplementasikan pustaka ini dituliskan sebagai kontrak kecil yang stabil
sehingga implementasi lain — sebuah ekstraktor, IDE, type checker, atau
`pygettext` masa depan — dapat menyasarnya dan saling beroperasi. Untuk aturan
yang sama dijelaskan beserta alasannya, dan bagaimana implementasi referensi
menjalankannya, baca [Cara kerjanya](internals.md) lebih dulu.

[Baca spec v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Aturannya dalam satu layar { #the-rules-in-one-screen }

**Sebuah msgid** adalah penyambungan, dalam urutan sumber, dari
segmen-segmen literal dan satu token `{name}` per interpolasi. Kurung kurawal
literal di-escape (`{` menjadi `{{`). Sebuah nama harus berupa nama
placeholder sederhana — `str.isidentifier()` bernilai benar dan ia bukan kata
kunci Python. Conversion dan format spec **bukan** bagian dari msgid; mereka
tetap di bawah kendali aplikasi.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *ditolak — bukan nama sederhana* |

**Sebuah terjemahan** valid ketika ia hanya berisi placeholder `{name}` polos,
setiap nama yang diwajibkan muncul setidaknya sekali, dan tidak ada nama di
luar himpunan yang diizinkan muncul. Pengurutan ulang dan pengulangan sengaja
dibiarkan bebas: keduanya bisa diperlukan secara tata bahasa di bahasa
sasaran.

Untuk bentuk jamak, *diizinkan* adalah union nama-nama kedua cabang dan
*diwajibkan* adalah interseksinya — sehingga `t"One file"` melawan
`t"{n} files"` membiarkan `n` tersedia bagi penerjemah salah satu bentuk
tetapi tidak diwajibkan pada keduanya, dan aturan jamak bahasa sasaran boleh
berbeda dari milik sumber.

**Msgid kosong** tidak pernah dicari, karena gettext mencadangkannya untuk
header metadata sebuah katalog.

## Konformans { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
adalah dokumen yang sama dalam bentuk terbaca mesin: kasus-kasus yang
memetakan struktur statis sebuah t-string ke sebuah msgid, dan sebuah msgid
plus pattern katalog ke string hasil render atau sebuah penolakan.

Sebuah implementasi **konforman terhadap spec v1** ketika ia mereproduksi
setiap kasus. Kasus-kasusnya hanya menyebut apa yang didefinisikan
spesifikasi — msgid turunan, pattern yang diterima dan ditolak, keluaran
render — dan tidak pernah sebuah pesan galat atau tipe eksepsi, sehingga
implementasi di bahasa lain dapat menjalankannya tanpa perubahan.

Interpolasi dideskripsikan secara struktural, tidak pernah sebagai sumber
Python:

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

Implementasi referensi menjalankan suite ini sebagai bagian dari suite
pengujiannya sendiri, sehingga prosa dan kodenya tidak dapat saling menjauh
dalam diam.

## Pemversian { #versioning }

Ini spec v1. Perubahan yang tidak kompatibel ke belakang pada derivasi msgid
atau pada validasi terjemahan menaikkan versinya dan mengirimkan
`conformance/vN.json` baru di samping yang sudah ada. Klarifikasi aditif yang
tidak mengubah msgid turunan maupun pattern yang diterima tidak.
