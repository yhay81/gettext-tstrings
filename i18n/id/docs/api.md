---
description: "Setiap nama yang diekspor gettext_tstrings: fungsi-fungsi, Translator, pengikatan konteks, string lazy, dan galat-galatnya."
---

# API

Semua di bawah ini diekspor dari `gettext_tstrings`. Tidak ada yang lain yang
publik. Halaman ini adalah referensi signature; untuk contoh terperinci setiap
fungsi, lihat [panduan](guide.md).

## Menerjemahkan { #translating }

Setiap fungsi menerima t-string-nya secara posisional dan menerima dua argumen
kata kunci: `translations` (kembali ke ikatan konteks, lalu ke fungsi global
pustaka standar) dan `strict` (lihat
[Panduan](guide.md#what-happens-when-a-catalog-is-wrong)).

| Fungsi | Signature |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias dari `gettext` |
| `ntr` | alias dari `ngettext` |

### `Translator`

Dataclass beku yang mengikat satu objek terjemahan, sehingga tempat-tempat
pemanggilan tidak mengulanginya.

```python
Translator(translations, strict=False)
```

Ia callable (`_(t"…")`) dan membawa `gettext`, `ngettext`, `pgettext`,
`npgettext`, serta alias `tr` / `ntr`.

## Pengikatan konteks { #context-binding }

| Nama | Kegunaan |
| --- | --- |
| `use_translations(translations)` | Mengikat selama sebuah blok `with`, lalu memulihkan. |
| `set_translations(translations)` | Mengikat tanpa blok, untuk siklus hidup yang dikelola framework. |
| `get_translations()` | Membaca ikatan saat ini, atau `None`. |

Ikatannya adalah sebuah `ContextVar`, sehingga per konteks dan aman di bawah
konkurensi.

## String tertunda { #deferred-strings }

| Nama | Kegunaan |
| --- | --- |
| `lazy_gettext(template, /)` | Menunda terjemahan hingga penggunaan pertama. |
| `lazy_pgettext(context, template, /)` | Bentuk kontekstualnya. |
| `LazyString` | Yang dikembalikan keduanya. Merender melalui `str()` dan `format()`, membandingkan sama dengan teksnya, dan sengaja tidak dapat di-hash. |

## Tingkat lebih rendah { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Mengompilasi sebuah t-string, memakai kembali rencana statis ter-cache-nya.

### `CompiledTemplate`

| Anggota | Arti |
| --- | --- |
| `.msgid` | Pengenal pesan gettext yang stabil. |
| `.placeholders` | Nama-nama placeholder dalam urutan kemunculan pertama. |
| `.render(pattern)` | Memvalidasi satu pattern dan merendernya. **Selalu melempar galat** pada ketidakcocokan. |

## Tipe dan galat { #types-and-errors }

### `Translations`

Sebuah `Protocol` `runtime_checkable` untuk empat metode standar, semuanya
positional-only:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations`, dan `Translations`
milik Babel semuanya memenuhinya.

### Eksepsi

| Kelas | Dilempar ketika |
| --- | --- |
| `TStringError` | Kelas dasar untuk kedua di bawah. |
| `InvalidTemplateError` | T-string **sumber** melanggar konvensinya — interpolasi kompleks, atau nama berulang dengan pemformatan berbeda. |
| `InvalidTranslationError` | **Terjemahannya** yang melanggar. Di bawah mode longgar bawaan, ini dicatat dan teks sumber dirender sebagai gantinya. |

## Titik masuk ekstraksi { #extraction-entry-points }

Terdaftar otomatis saat instalasi; Anda merujuknya dengan nama, bukan dengan
impor.

| Grup | Nama | Dipakai oleh |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` di `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, otomatis. |

## Performa { #performance }

Penjelasan lengkapnya — apa yang di-cache, apa kunci cache-nya, dan
angka-angka terukurnya — ada di [Jalur panas](internals.md#the-hot-path).
Versi singkatnya: validasi di-cache, tidak pernah dilewati, dan seluruh render
berbiaya sepersekian mikrodetik. Jalankan benchmark-nya pada sasaran Anda
sendiri:

```console
uv run python benchmarks/runtime.py
```
