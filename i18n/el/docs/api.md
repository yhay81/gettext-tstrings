---
description: "Κάθε όνομα που εξάγει το gettext_tstrings: οι συναρτήσεις, ο Translator, το δέσιμο συγκειμένου, οι αναβαλλόμενες συμβολοσειρές και τα σφάλματα."
---

# API

Όλα όσα ακολουθούν εξάγονται από το `gettext_tstrings`. Τίποτε άλλο δεν είναι
δημόσιο. Αυτή η σελίδα είναι η αναφορά των υπογραφών· για λυμένα παραδείγματα
κάθε συνάρτησης, δείτε τον [οδηγό](guide.md).

## Μετάφραση { #translating }

Κάθε συνάρτηση παίρνει το t-string της κατά θέση και δέχεται δύο ορίσματα με
λέξη-κλειδί: το `translations` (που υποχωρεί στο δέσιμο συγκειμένου, και μετά
στις καθολικές συναρτήσεις της τυπικής βιβλιοθήκης) και το `strict` (δείτε
τον [Οδηγό](guide.md#what-happens-when-a-catalog-is-wrong)).

| Συνάρτηση | Υπογραφή |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | ψευδώνυμο της `gettext` |
| `ntr` | ψευδώνυμο της `ngettext` |

### `Translator`

Μια παγωμένη dataclass που δένει ένα αντικείμενο μετάφρασης, ώστε τα σημεία
κλήσης να μην το επαναλαμβάνουν.

```python
Translator(translations, strict=False)
```

Είναι καλέσιμη (`_(t"…")`) και φέρει τις `gettext`, `ngettext`, `pgettext`,
`npgettext` και τα ψευδώνυμα `tr` / `ntr`.

## Δέσιμο συγκειμένου { #context-binding }

| Όνομα | Σκοπός |
| --- | --- |
| `use_translations(translations)` | Δένει για τη διάρκεια ενός μπλοκ `with`, και μετά αποκαθιστά. |
| `set_translations(translations)` | Δένει χωρίς μπλοκ, για κύκλους ζωής που διαχειρίζεται το πλαίσιο. |
| `get_translations()` | Διαβάζει το τρέχον δέσιμο, ή `None`. |

Το δέσιμο είναι ένα `ContextVar`, οπότε είναι ανά συγκείμενο και ασφαλές υπό
ταυτοχρονία.

## Αναβαλλόμενες συμβολοσειρές { #deferred-strings }

| Όνομα | Σκοπός |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Αναβάλλει μια μετάφραση ώς την πρώτη χρήση. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Η μορφή με συγκείμενο. |
| `LazyString` | Αυτό που επιστρέφουν και οι δύο. Αποδίδεται μέσω `str()` και `format()`, συγκρίνεται ίση με το κείμενό της, και είναι σκόπιμα μη κατακερματίσιμη. |

## Χαμηλότερο επίπεδο { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Μεταγλωττίζει ένα t-string, επαναχρησιμοποιώντας το στατικό του σχέδιο από
την κρυφή μνήμη.

### `CompiledTemplate`

| Μέλος | Σημασία |
| --- | --- |
| `.msgid` | Το σταθερό αναγνωριστικό μηνύματος του gettext. |
| `.placeholders` | Τα ονόματα των συμβόλων κράτησης θέσης με σειρά πρώτης εμφάνισης. |
| `.render(pattern)` | Επικυρώνει ένα μοτίβο και το αποδίδει. **Εγείρει πάντα** εξαίρεση σε αναντιστοιχία. |

## Τύποι και σφάλματα { #types-and-errors }

### `Translations`

Ένα `runtime_checkable` `Protocol` για τις τέσσερις τυπικές μεθόδους, όλες με
ορίσματα μόνο κατά θέση:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

Οι `gettext.NullTranslations`, `gettext.GNUTranslations` και η `Translations`
του Babel το ικανοποιούν όλες.

### Εξαιρέσεις

| Κλάση | Εγείρεται όταν |
| --- | --- |
| `TStringError` | Βασική κλάση και για τις δύο παρακάτω. |
| `InvalidTemplateError` | Το **πηγαίο** t-string παραβιάζει τη σύμβαση — μια σύνθετη παρεμβολή, ή ένα επαναλαμβανόμενο όνομα με διαφορετική μορφοποίηση. |
| `InvalidTranslationError` | Την παραβιάζει η **μετάφραση**. Στην προεπιλεγμένη επιεική λειτουργία αυτό καταγράφεται και αποδίδεται στη θέση της το πηγαίο κείμενο. |

## Σημεία εισόδου εξαγωγής { #extraction-entry-points }

Καταχωρίζονται αυτόματα κατά την εγκατάσταση· αναφέρεστε σε αυτά με το όνομά
τους, όχι με import.

| Ομάδα | Όνομα | Χρησιμοποιείται από |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | Τη `method` στο `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | Το `pybabel compile`, αυτόματα. |

## Επιδόσεις { #performance }

Ο πλήρης απολογισμός — τι μπαίνει στην κρυφή μνήμη, με τι κλειδί, και οι
μετρημένοι αριθμοί — είναι η
[Θερμή διαδρομή](internals.md#the-hot-path). Η σύντομη εκδοχή: η επικύρωση
μπαίνει στην κρυφή μνήμη, δεν παραλείπεται ποτέ, και ολόκληρη η απόδοση
κοστίζει κλάσμα του μικροδευτερολέπτου. Τρέξτε το benchmark στον δικό σας
στόχο:

```console
uv run python benchmarks/runtime.py
```
