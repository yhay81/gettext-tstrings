---
description: "Mengekstrak pesan t-string dengan pybabel, dan bagaimana msgfmt serta pemeriksa Babel bawaan memvalidasi katalognya."
---

# Ekstraksi

Ekstraksi adalah langkah yang mengumpulkan setiap pesan bertanda keluar dari
kode sumber Anda ke dalam sebuah templat `.pot` untuk penerjemah — langkah 3
dari putaran [tutorial](tutorial.md). Halaman ini adalah referensi untuk
langkah itu: konfigurasi, nama fungsi kustom, mode CI ketat, dan pemeriksaan
yang menjaga katalog Anda sesudahnya.

Ekstraksi membutuhkan extra `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Alur kerjanya { #the-workflow }

Buat `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Lalu gunakan perintah-perintah Babel biasa:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` berjalan sekali per bahasa; setelah itu, `pybabel update` melipat
setiap templat segar ke dalam katalog yang sudah ada. Siklus berulang itu —
dan apa arti entri `fuzzy`-nya bagi sebuah rilis — ditempuh di
[Dalam produksi](workflow.md#the-cycle-after-the-first-translation).

Ekstraktor `gettext_tstrings` juga menangani pemanggilan `_()`, `gettext()`,
dan `ngettext()` biasa, sehingga satu pemetaan mencakup basis kode campuran.
Ia mengenali `_()`, empat nama gettext standar, alias `tr()` / `ntr()`, dan
`lazy_gettext()` / `lazy_pgettext()` yang tertunda.

!!! warning "`-c` bukan pilihan"

    `pybabel extract` hanya mengumpulkan komentar penerjemah ketika Anda
    melewatkan `-c "Translators:"`, persis seperti pada pemanggilan gettext
    biasa.

## Mendaftarkan nama fungsi Anda sendiri { #registering-your-own-function-names }

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

Berkas INI memberi satu string, pemetaan TOML memberi sebuah list, dan di
dalam string, spasi atau koma memisahkan nama-namanya. Keempat penulisan itu
berfungsi.

Opsinya adalah `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions`, dan `npgettext_functions`.

!!! danger "`-k` tidak menjangkau sebuah t-string"

    Helper kustom seperti `mytr(t"…")` harus disebut di salah satu opsi di
    atas. Mesin `--keyword` Babel tidak dapat membaca literal t-string, jadi
    `pybabel extract -k mytr` tidak menemukan apa pun dan tidak berkata apa
    pun — pesan-pesannya begitu saja absen dari POT. `-k` tetap berfungsi
    untuk pemanggilan gettext biasa yang diekstrak berdampingan.

    Hanya urutan argumen standar yang didukung: pesan lebih dulu, konteks lalu
    pesan untuk `pgettext`, konteks lalu tunggal lalu jamak untuk `npgettext`.

## Tangguh secara bawaan { #robust-by-default }

Satu berkas buruk tidak mengakhiri jalannya proses:

- Sebuah t-string yang ditolak ekstraktor — akses atribut, sebuah ekspresi,
  argumen yang keliru — dilaporkan sebagai peringatan dan dilewati.
- Berkas yang tidak dapat di-parse dilewati dengan cara yang sama.
- Begitu pula berkas yang hanya ditolak `tokenize` sementara `ast`
  menerimanya, yang akan membuat lintasan Babel sendiri berhenti.

Setel `strict = true` di opsi pemetaan untuk mengubah setiap kasus itu menjadi
kegagalan keras, yang adalah yang Anda inginkan di CI.

## Toolchain Anda yang sudah ada memvalidasi katalog ini { #your-existing-toolchain-validates-these-catalogs }

Babel menandai setiap pesan yang diekstrak dengan sebuah flag standar, dan
satu baris itulah yang mengaktifkan pemeriksaan placeholder di perkakas yang
sudah Anda jalankan:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Terjemahkan sebagai `こんにちは {nombre}` dan kesalahannya tertangkap tanpa
konfigurasi apa pun:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate mendokumentasikan pemeriksaan yang sama sebagai
[Python brace format][weblate-checks], dan platform komersial punya QA
placeholder mereka sendiri yang bertumpu pada flag yang sama. Perilaku mereka
adalah milik mereka; dua perkakas di bawah adalah yang diverifikasi di sini.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Di atas itu, paket ini mendaftarkan sebuah **checker** Babel, sehingga
`pybabel compile` menerapkan aturan-aturan spesifikasi ke setiap pesan yang
membawa komentar penanda `gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Untuk pesan jamak, penunjuknya menyebut bentuknya, karena nomor baris yang
dilaporkan Babel adalah milik msgid dan sebuah blok Rusia punya tiga `msgstr`
di bawahnya:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` tetap menulis `.mo`-nya"

    Galat di atas dilaporkan, status keluarnya `1` — dan katalog yang rusak
    tetap saja dikompilasi. Hanya status keluar itu yang dapat menghentikan
    pipeline mengirimkannya;
    [Apa yang dijaga CI](workflow.md#what-ci-gates) menunjukkan langkah build
    yang membiarkannya bekerja.

Kedua pemeriksaan itu tidak berlebihan. Checker yang disertakan adalah pihak
yang lebih ketat setidaknya di dua tempat:

- Sebuah msgid yang satu-satunya kurung kurawalnya di-escape
  (`Config {{raw}} only`) tidak pernah mendapat flag `python-brace-format`,
  sehingga tidak ada perkakas eksternal yang memvalidasinya sama sekali.
- Bentuk jamak diperiksa satu per satu. `msgfmt --check-format` membaca
  berkas persis di atas dan keluar dengan `0`; sebuah bentuk yang
  menghilangkan placeholder yang dijaga saudara-saudaranya diterima di sana
  dan ditolak di sini.

`msgfmt` hanya memeriksa nama placeholder yang dapat ia parse sebagai Python
brace format, jadi nama ASCII menjaga setiap perkakas di rantainya tetap dapat
memvalidasi pesan. Pustaka ini sendiri menerima nama `str.isidentifier()` apa
pun.

## Templat dan perkakas lain { #templates-and-other-tools }

t-string adalah sintaks Python, jadi pustaka ini mencakup sumber Python.
Bahasa templat tetap memakai i18n mereka sendiri — `{% trans %}` milik Jinja2,
tag templat Django — dan ekstraktor Babel untuk mereka. Semuanya mengalir ke
katalog PO yang sama, sehingga satu alur kerja penerjemahan tetap mencakup
basis kode campuran.

`pygettext` belum dapat mem-parse t-string hari ini, itulah sebabnya ekstraksi
berjalan melalui Babel. Konvensinya dituliskan di [spesifikasi](spec.md) agar
ekstraktor lain, atau `pygettext` masa depan, dapat menyasarnya.
