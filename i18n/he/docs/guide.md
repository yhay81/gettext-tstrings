---
description: "ה-API של זמן הריצה: באיזו נקודת כניסה להשתמש, קשירת קטלוג, שפה לכל בקשה, מחרוזות דחויות, ערכים תלויי שפה, ואיך מדווח תרגום שבור."
---

# מדריך

עמוד זה הוא מסמך העיון של זמן הריצה: כל מה ש*קוד היישום* שלכם עושה עם
הספרייה הזו לאחר שהקטלוגים קיימים. אם עדיין לא ראיתם את הלולאה המלאה
— סימון, חילוץ, תרגום, קומפילציה, הרצה — [מדריך המבוא](tutorial.md) עובר
עליה פעם אחת בחמש דקות; יצירת קטלוגים ואימותם מכוסים בעמוד
[חילוץ](extraction.md), ואיך צוות שומר על הלולאה בתנועה — מחזורי עדכון,
CI, פלטפורמות תרגום — נמצא בעמוד [בסביבת ייצור](workflow.md).

## באיזו נקודת כניסה כדאי להשתמש? { #which-entry-point-should-i-use }

החבילה מייצאת כמה דרכים לתרגם הודעה מפני שיישומים קושרים שפה בכמה
דרכים שונות. בחרו לפי האופן שבו התוכנית שלכם מחליטה באיזו שפה היא
נמצאת:

| המצב שלכם | מה להשתמש |
| --- | --- |
| שפה אחת לכל התהליך — CLI, יישום שולחני, סקריפט | `Translator`, בקריאה בשם `_` |
| שפה אחת לכל בקשה או לכל משימת async — יישום ווב | `use_translations()` סביב העבודה, ואז `tr()` |
| הודעה שמוגדרת בזמן ייבוא — תווית טופס, enum, קבוע | `lazy_gettext()` או `lazy_pgettext()` |
| מונה מכריע את הניסוח | `ngettext()` / `npgettext()`, בכל אחת מהצורות שלעיל |
| רינדור דפוס בלי שום קטלוג מעורב | `compile_template()` |

כל מה שלהלן הוא חמשת אלה, בסדר הזה.

## קשירת קטלוג { #binding-a-catalog }

הצורה המומלצת משקפת את השימוש מבוסס-המחלקות של gettext: קושרים אובייקט
תרגום סטנדרטי פעם אחת ומשתמשים במעבד הניתן לקריאה בתור `_`.

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

הפונקציות ברמת המודול עוקבות אחר השמות של הספרייה הסטנדרטית ואחר
מוסכמת הקריאה הפוזיציונלית-בלבד שלה:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` ו-`ntr` הם כינויים מדויקים של `gettext` ו-`ngettext`.

## שפה לכל בקשה { #per-request-language }

מסגרת ווב בוחרת שפה לכל בקשה. קשרו את התרגומים של הבקשה להקשר הנוכחי,
וכל קריאה ברמת המודול תיפתר לאותה שפה, באופן בטוח גם בין בקשות
מקביליות:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` קושרת ללא בלוק `with`, עבור מסגרות
שמנהלות בעצמן את מחזור החיים של הבקשה; `get_translations()` קוראת את
הקשירה הנוכחית. ארגומנט `translations=` מפורש תמיד גובר על ההקשר, והקשר
שאינו קשור מבצע נסיגה לפונקציות gettext הגלובליות המותקנות של הספרייה
הסטנדרטית. דוגמאות מלאות ל-Flask ולתווך ASGI נמצאות בעמוד
[בסביבת ייצור](workflow.md#binding-a-language-at-runtime).

## תרגום דחוי { #deferred-translation }

מחרוזת-t לוכדת את ערכיה באופן מיידי, וזה שגוי עבור מחרוזת המוגדרת בזמן
הייבוא — תווית של טופס, ערך enum, קבוע של מודול — שצריכה לעבור רינדור
בשפה הפעילה ברגע שבו היא נמצאת *בשימוש*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` עוברת רינדור דרך `str()`, דרך `format()` ודרך מחרוזות-f,
ונחשבת שווה בהשוואה לטקסט המרונדר שלה.

!!! note "בלתי ניתנת לגיבוב בכוונה"

    הטקסט של `LazyString` תלוי בשפה הפעילה, ולכן ערך גיבוב היה משתנה
    עם החלפת שפה ומשחית בשקט כל set או dict שמחזיקים אותה. קראו תחילה
    ל-`str()` אם אתם זקוקים למפתח.

`strict` נקבע במקום שבו ההודעה נכתבת, לא במקום שבו היא מרונדרת:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

מחרוזת דחויה מרונדרת בכל מקום שבו היא נצרכת בסופו של דבר — בתוך תבנית,
בטופס, בשורת יומן — ולמקום הזה כמעט אף פעם אין מושג אם מדובר בהרצת בדיקות
או בסביבת ייצור. העברת `strict=True` בהגדרה היא מה שמאפשר להחיל את אותה
בחירה של [רועש ב-CI, סלחני בייצור](#what-happens-when-a-catalog-is-wrong)
גם על מחרוזת שאינה מרונדרת באתר הקריאה שלה.

צורות ריבוי תלויות במונה של זמן ריצה, ולכן רנדרו אותן מיידית עם
`ngettext` במקום שבו המונה ידוע.

## כמה שפות בבת אחת { #several-languages-at-once }

בקשה אחת זקוקה לא פעם ליותר משפה אחת: עמוד המרונדר עבור הקורא, שגם מציב בתור
התראה לחשבון המוגדר לשפה אחרת, או תקציר המצטט כל משתתף בשפתו שלו. הקשירות
מקננות, ויציאה מהבלוק הפנימי משיבה את החיצוני.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

על פני רשימת נמענים, מחרוזות דחויות עושות את העבודה: ההודעה נכתבת פעם אחת,
בזמן הייבוא, ומרונדרת פעם אחת לכל שפה.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

הקשירה היא `ContextVar`, לא מחסנית המוחזקת על אובייקט משותף, ולכן בקשות
חופפות אינן יכולות לקלוט זו את שפתה של זו — כולל המקרה שבו הן *יוצאות*
מהבלוקים שלהן בסדר שבו נכנסו אליהם, שהוא בדיוק השזירה שמחסנית דחיפה שוגה בה.
טעינת קטלוג לכל שפה היא זולה: `gettext.translation()` מפענחת כל `.mo` פעם
אחת ומחלקת עותקים החולקים את הקטלוג המפוענח.

!!! warning "השאלה אם תהליכון עובד יורש את הקשירה תלויה בבנייה"

    `threading.Thread` חשוף, או `ThreadPoolExecutor.submit`, מתחיל או מעותק
    של ההקשר של הקורא או מהקשר ריק, ואיזו משתי האפשרויות תתקיים נקבע בידי
    `sys.flags.thread_inherit_context` — אמת כברירת מחדל בבניות free-threaded,
    שקר בכל מקום אחר. אותו קוד עצמו מציג אפוא את השפה הקשורה ב-3.14t ואת
    קטלוג gettext הגלובלי של התהליך ב-3.14. העבירו את ההקשר במקום להסתמך על
    ברירת המחדל:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` כבר עושה זאת עבורכם.

## ערכים תלויי שפה { #locale-aware-values }

הספרייה הזו מחליטה *היכן* ערך מופיע בהודעה מתורגמת. היא אינה מתאימה את
הערך עצמו לשפה. `{amount:,.2f}` הוא מפרט פורמט של Python בעל התנהגות
קבועה — פסיק בכל שלוש ספרות ונקודה לפני השבר — והוא מפיק את אותם תווים
בכל שפה שההודעה נמצאת בה:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

בגרמנית כותבים את המספר הזה `1.234,50`, בצרפתית `1 234,50`, ובהינדית
מקבצים את `1234567` כ-`12,34,567` ולא כ-`1,234,567`. מספרים, מטבעות,
תאריכים, שעות ויחידות שייכים ל-[Babel][babel-numbers]. עצבו את הערך
תחילה, ורק אז הציבו את המחרוזת המוכנה:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

בהודעה עם מונה המספר עושה שתי עבודות — הוא בוחר את צורת הריבוי והוא
מופיע בטקסט — ורק השנייה מותאמת לשפה. שמרו את המונה הגולמי לצורך
הבחירה והעבירו את המחרוזת המעוצבת לצורך התצוגה:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

עיצוב לפני הקריאה הוא גם מה ששומר מפרט פורמט מחוץ לקטלוג: מה שהמתרגם
רואה הוא פיסת טקסט מוגמרת, לא מספר בצירוף הוראות לרינדור שלו.

## מה קורה כשקטלוג שגוי { #what-happens-when-a-catalog-is-wrong }

אם מצייני המקום של תרגום אינם תואמים את המקור — שדה חסר, לא מוכר או
מעוצב מחדש שחמק מהאימות, מקובץ MO שנערך ידנית, מקטלוג של ספק, או
מצינור עבודה שמדלג על הבודק — ברירת המחדל היא לרנדר את הודעת המקור
במקום להעלות חריגה. הדבר משקף את החוזה של gettext עצמו, שלפיו קטלוג
פגום לעולם אינו שובר את היישום.

כאשר `Hello {name}` מתורגם בתור `こんにちは {nombre}`, הרינדור מצליח
ואזהרה אחת נשלחת ל-logger בשם `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

האזהרה נורית פעם אחת לכל הודעה ודפוס, לא פעם אחת לכל רינדור, כך
שרשומת קטלוג שבורה אינה מציפה את היומן.

בחרו להיכשל בקול רם עבור בדיקות ו-CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

אותו חיפוש מעלה אז חריגה, הנושאת את אותו משפט ללא המחצית של
"using source text":

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

ההודעות הללו נכתבות עבור מי שיכול לפעול לפיהן, ובבעיית קטלוג זהו לרוב
מתרגם יותר מאשר מתכנת — ולכן במקום שבו מציין מקום נראה קיים אך אינו
כזה, ההודעה מסבירה מדוע במקום לחזור ולומר שהוא חסר. סוגריים מסולסלים
ברוחב מלא, `{{name}}` כפול, רווח קשיח בלתי נראה, אות קירילית בין
לטיניות: לכל אחד מהם ניסוח משלו, המפורט עם דוגמאות בעמוד
[למתרגמים](translators.md#reading-a-failure-message). העמוד ההוא נכתב
כדי שאפשר יהיה למסור אותו למי שעורך את ה-`.po`.

## רינדור דפוס ללא קטלוג { #rendering-a-pattern-without-a-catalog }

`compile_template` חושפת את אותו מנגנון ברמה אחת למטה: היא הופכת
מחרוזת-t ל-msgid שלה בצירוף קבוצת ערכים קשורה, ומרנדרת כל דפוס
שתמסרו לה.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` מאמתת לפי אותם כללים ו**תמיד מעלה חריגה** על אי-התאמה. אין
כאן מצב סלחני: הסלחנות קיימת כדי שחיפוש ב*קטלוג* יוכל לבצע נסיגה
לטקסט המקור, ולדפוס שמסרתם בעצמכם אין ממה לסגת.

## בטיחות והיקף { #safety-and-scope }

זה תקין:

```python
tr(t"Hello {name}")
```

אלה נדחים בכוונה:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

חשבו תחילה ערך בעל משמעות:

```python
name = user.display_name()
tr(t"Hello {name}")
```

ההגבלה מייצרת מפתחות קטלוג יציבים, נותנת למתרגמים שמות שימושיים,
ומונעת ממחרוזת מתורגמת להפוך לשפת ביטויים.

הערובה תחומה ל*מבנה ולעיצוב*: תרגום לעולם אינו מוערך כקוד, ולעולם
אינו יכול להוסיף גישה לתכונות, קריאות לפונקציות, המרות או מפרטי
פורמט. שני דברים נשארים באחריות הקורא לפונקציה, בדיוק כמו עם gettext
של הספרייה הסטנדרטית — **בריחת תווים (escaping)** של הפלט המרונדר
בהתאם ליעדו (HTML, מעטפת, מסוף), ו**שלמות הקטלוג**, שכן קטלוג עוין
יכול לחזור על מציין מקום כדי להגדיל את נפח הפלט — דבר הטבוע בכל
מנגנון i18n מבוסס מצייני מקום.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
