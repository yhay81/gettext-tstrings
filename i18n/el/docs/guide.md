---
description: "Το API χρόνου εκτέλεσης: δέσιμο ενός καταλόγου, γλώσσες ανά αίτημα, αναβαλλόμενες συμβολοσειρές, και πώς αναφέρεται μια χαλασμένη μετάφραση."
---

# Οδηγός

Αυτή η σελίδα είναι η αναφορά του χρόνου εκτέλεσης: όλα όσα κάνει ο *κώδικας
της εφαρμογής σας* με αυτή τη βιβλιοθήκη αφού πια υπάρχουν κατάλογοι. Αν δεν
έχετε δει ακόμη τον πλήρη βρόχο — επισήμανση, εξαγωγή, μετάφραση,
μεταγλώττιση, εκτέλεση — η [εκμάθηση](tutorial.md) τον διατρέχει μία φορά σε
πέντε λεπτά· η δημιουργία και η επικύρωση καταλόγων καλύπτεται στην
[Εξαγωγή](extraction.md), και το πώς μια ομάδα κρατά τον βρόχο σε κίνηση —
κύκλοι ενημέρωσης, CI, πλατφόρμες μετάφρασης — είναι το
[Στην παραγωγή](workflow.md).

## Δέσιμο ενός καταλόγου { #binding-a-catalog }

Η προτεινόμενη μορφή αντικατοπτρίζει τη χρήση του gettext με κλάσεις: δέστε
ένα τυπικό αντικείμενο μετάφρασης μία φορά και χρησιμοποιήστε τον καλέσιμο
επεξεργαστή ως `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

Οι συναρτήσεις επιπέδου αρθρώματος ακολουθούν τα ονόματα της τυπικής
βιβλιοθήκης και τη σύμβαση κλήσης της με ορίσματα μόνο κατά θέση:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

Οι `tr` και `ntr` είναι ακριβή ψευδώνυμα των `gettext` και `ngettext`.

## Γλώσσα ανά αίτημα { #per-request-language }

Ένα πλαίσιο ιστού επιλέγει γλώσσα ανά αίτημα. Δέστε τις μεταφράσεις του
αιτήματος στο τρέχον συγκείμενο και κάθε κλήση επιπέδου αρθρώματος επιλύεται
σε αυτή τη γλώσσα, με ασφάλεια ανάμεσα σε ταυτόχρονα αιτήματα:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

Η `set_translations(translations)` δένει χωρίς μπλοκ `with`, για πλαίσια που
διαχειρίζονται μόνα τους τον κύκλο ζωής του αιτήματος· η
`get_translations()` διαβάζει το τρέχον δέσιμο. Ένα ρητό όρισμα
`translations=` υπερισχύει πάντα του συγκειμένου, και ένα αδέσμευτο
συγκείμενο υποχωρεί στις καθολικά εγκατεστημένες συναρτήσεις gettext της
τυπικής βιβλιοθήκης. Ολοκληρωμένα παραδείγματα για Flask και ενδιάμεσο
λογισμικό ASGI υπάρχουν στη σελίδα
[Στην παραγωγή](workflow.md#binding-a-language-at-runtime).

## Αναβαλλόμενη μετάφραση { #deferred-translation }

Ένα t-string αιχμαλωτίζει τις τιμές του άπληστα, πράγμα λάθος για μια
συμβολοσειρά που ορίζεται κατά την εισαγωγή — μια ετικέτα φόρμας, μια τιμή
enum, μια σταθερά αρθρώματος — και πρέπει να αποδοθεί σε όποια γλώσσα είναι
ενεργή όταν *χρησιμοποιείται*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

Μια `LazyString` αποδίδεται μέσω `str()`, `format()` και f-strings, και
συγκρίνεται ίση με το αποδιδόμενο κείμενό της.

!!! note "Σκόπιμα μη κατακερματίσιμη"

    Το κείμενο μιας `LazyString` εξαρτάται από την ενεργή γλώσσα, οπότε ένα
    hash θα άλλαζε με κάθε εναλλαγή γλώσσας και θα αλλοίωνε αθόρυβα κάθε set
    ή dict που την κρατά. Καλέστε πρώτα `str()` αν χρειάζεστε κλειδί.

Το `strict` αποφασίζεται εκεί όπου *γράφεται* το μήνυμα, όχι εκεί όπου
αποδίδεται:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Μια αναβαλλόμενη συμβολοσειρά αποδίδεται όπου τελικά χρησιμοποιείται — μέσα
σε ένα πρότυπο, μια φόρμα, μια γραμμή καταγραφής — και αυτό το σημείο σπάνια
γνωρίζει αν πρόκειται για εκτέλεση δοκιμών ή για παραγωγή. Το πέρασμα
`strict=True` κατά τον ορισμό είναι που επιτρέπει να ισχύσει η ίδια επιλογή
[θορυβώδης στο CI, επιεικής στην παραγωγή](#what-happens-when-a-catalog-is-wrong)
και για μια συμβολοσειρά που δεν αποδίδεται στο σημείο κλήσης της.

Οι μορφές πληθυντικού εξαρτώνται από ένα πλήθος γνωστό στον χρόνο εκτέλεσης,
οπότε αποδώστε τες άπληστα με την `ngettext` εκεί όπου το πλήθος είναι
γνωστό.

## Τι συμβαίνει όταν ένας κατάλογος είναι λανθασμένος { #what-happens-when-a-catalog-is-wrong }

Αν τα σύμβολα κράτησης θέσης μιας μετάφρασης δεν ταιριάζουν με την πηγή —
ένα πεδίο που λείπει, είναι άγνωστο ή έχει αλλαγμένη μορφοποίηση και ξέφυγε
από την επικύρωση, από ένα χειροποίητο MO, έναν κατάλογο προμηθευτή ή μια
γραμμή παραγωγής που παραλείπει τον ελεγκτή — η προεπιλογή είναι να
αναπαραχθεί το πηγαίο κείμενο αντί να εγερθεί εξαίρεση. Αυτό αντικατοπτρίζει
το ίδιο το συμβόλαιο του gettext ότι ένας κακός κατάλογος δεν σπάει ποτέ την
εφαρμογή.

Με το `Hello {name}` μεταφρασμένο ως `こんにちは {nombre}`, η απόδοση
επιτυγχάνει και μία προειδοποίηση πηγαίνει στον καταγραφέα
`gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Η προειδοποίηση εκπέμπεται μία φορά ανά μήνυμα και μοτίβο, όχι μία φορά ανά
απόδοση, ώστε μια χαλασμένη καταχώριση καταλόγου να μην πλημμυρίζει ένα
αρχείο καταγραφής.

Επιλέξτε τη θορυβώδη αποτυχία για δοκιμές και CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Η ίδια αναζήτηση τότε εγείρει εξαίρεση, κουβαλώντας την ίδια πρόταση χωρίς
το μισό «using source text»:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Πώς διαβάζεται ένα μήνυμα αποτυχίας { #reading-a-failure-message }

Αυτά τα μηνύματα γράφονται για όποιον μπορεί να ενεργήσει πάνω τους, που για
ένα πρόβλημα καταλόγου είναι συχνότερα μεταφραστής παρά προγραμματιστής. Το
να αναφέρεις μόνο ότι το `{name}` λείπει είναι αδιέξοδο όταν ο αναγνώστης
βλέπει αυτούς τους χαρακτήρες μπροστά του, οπότε όπου ένα σύμβολο κράτησης
θέσης μοιάζει παρόν αλλά δεν είναι, το μήνυμα εξηγεί γιατί. Απέναντι στην
πηγή `Hello {name}`, καθένα από αυτά αναφέρεται κάτω από το
`translation does not match the source placeholders:`

| Η μετάφραση λέει | Ο λόγος που δίνει |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Οι χαρακτήρες που δεν φαίνονται έχουν τη δική τους μεταχείριση. Ένα διάστημα
χωρίς αλλαγή γραμμής μέσα στα άγκιστρα είναι κάτι που παράγει μια μέθοδος
εισαγωγής και δεν δείχνει κανένας επεξεργαστής, οπότε το μήνυμα το τυπώνει
με το σημείο κώδικά του αντί να κατονομάσει έναν χαρακτήρα που ο αναγνώστης
δεν μπορεί να βρει:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Ένα όνομα του οποίου τα γράμματα αναμειγνύουν συστήματα γραφής — η περίπτωση
των ομοιόγλυφων, όπου ένα κυριλλικό `а` είναι αδιάκριτο από ένα λατινικό —
εμφανίζεται δύο φορές, μία ευανάγνωστα και μία με διαφυγή, που είναι η μόνη
μορφή που ξεχωρίζει τα δύο:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Η ίδια αποσαφήνιση ισχύει όταν ένα ελληνικό ή κυριλλικό όνομα γραμμένο
εξ ολοκλήρου σε ένα σύστημα γραφής συγκρούεται με ένα πηγαίο όνομα ASCII,
συμπεριλαμβανομένης της περίπτωσης του ενός γράμματος λατινικό `a` /
κυριλλικό `а`.

## Απόδοση ενός μοτίβου χωρίς κατάλογο { #rendering-a-pattern-without-a-catalog }

Η `compile_template` εκθέτει τον ίδιο μηχανισμό ένα επίπεδο πιο κάτω:
μετατρέπει ένα t-string στο msgid του συν ένα δεμένο σύνολο τιμών, και
αποδίδει όποιο μοτίβο της δώσετε.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

Η `render` επικυρώνει με τους ίδιους κανόνες και **εγείρει πάντα** εξαίρεση
σε αναντιστοιχία. Εδώ δεν υπάρχει επιεικής λειτουργία: η επιείκεια υπάρχει
για να μπορεί μια αναζήτηση *καταλόγου* να υποβαθμιστεί στο πηγαίο κείμενο,
και ένα μοτίβο που περάσατε εσείς οι ίδιοι δεν έχει από πού να υποβαθμιστεί.

## Ασφάλεια και εμβέλεια { #safety-and-scope }

Αυτό είναι έγκυρο:

```python
tr(t"Hello {name}")
```

Αυτά απορρίπτονται σκόπιμα:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Υπολογίστε πρώτα μια ουσιαστική τιμή:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Ο περιορισμός παράγει σταθερά κλειδιά καταλόγου, δίνει στους μεταφραστές
χρήσιμα ονόματα, και εμποδίζει μια μεταφρασμένη συμβολοσειρά να γίνει γλώσσα
εκφράσεων.

Η εγγύηση περιορίζεται σε *δομή και μορφοποίηση*: μια μετάφραση δεν
αποτιμάται ποτέ, και δεν μπορεί ποτέ να προσθέσει πρόσβαση σε ιδιότητες,
κλήσεις, μετατροπές ή προδιαγραφές μορφοποίησης. Δύο πράγματα παραμένουν
ευθύνη του καλούντος, ακριβώς όπως και με το gettext της τυπικής βιβλιοθήκης
— η **διαφυγή** της αποδιδόμενης εξόδου για τον προορισμό της (HTML, φλοιός,
τερματικό), και η **ακεραιότητα του καταλόγου**, αφού ένας εχθρικός
κατάλογος μπορεί να επαναλάβει ένα σύμβολο κράτησης θέσης για να
πολλαπλασιάσει το μέγεθος της εξόδου, κάτι εγγενές σε κάθε i18n βασισμένο σε
σύμβολα κράτησης θέσης.
