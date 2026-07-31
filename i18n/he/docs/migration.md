---
description: "אימוץ מחרוזות-t בפרויקט שכבר יש בו קטלוגי gettext: מה שורד ללא נגיעה, מה הופך ל-fuzzy, ואיך לעבור אתר קריאה אחד בכל פעם."
---

# מעבר מקיים

אם הפרויקט שלכם כבר משתמש ב-gettext, השאלות שמכריעות אם הספרייה הזו
ניתנת לאימוץ הן שאלות צרות: האם היא פוסלת את הקטלוגים שכבר יש לכם, האם
היא יכולה לחיות לצד הקוד שאינכם מוכנים לשנות, וכמה מהמהלך חייב לקרות
בבת אחת. התשובות, מהקצרה ואילך:

| שאלה | תשובה |
| --- | --- |
| האם קובצי `.po` ו-`.mo` קיימים ממשיכים לעבוד? | כן. אותם קבצים, אותם כלים. |
| האם קריאות ישנות וחדשות יכולות לחיות בקובץ אחד? | כן, ומיפוי מחלץ אחד מכסה את שתיהן. |
| האם ה-msgid משתנה? | לא מ-`.format()`. כן מ-`%`-format. |
| האם כל הפרויקט חייב לעבור בבת אחת? | לא. אתר קריאה אחד הוא שינוי תקף. |
| ומה עם Jinja, תבניות Django, JavaScript? | ללא נגיעה, אותם קטלוגים. |

שאר העמוד הזה הוא הפירוט מאחורי כל אחת מהתשובות האלה.

## מ-`.format()`: ה-msgid אינו משתנה { #from-format-the-msgid-does-not-change }

זהו המקרה שבו המעבר כמעט אינו עולה דבר. הודעת `str.format` והודעת
מחרוזת-t גוזרות את *אותו* מפתח קטלוג, מפני שהמפתח הוא הטקסט שבתוכו
`{name}` נשאר על מקומו בשתי הדרכים:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

לכן התרגום הקיים נשאר מחובר. אם מתחילים מקטלוג שמכיל

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

שנו את הקריאה, חלצו מחדש, ועדכנו:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

הרשומה שחוזרת נבדלת בשתי שורות של מטא-נתונים ותו לא — הערת סימון
שמזהה אותה כהודעת מחרוזת-t, ומספר שורה במקור:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

בלי דגל `fuzzy`, בלי תרגום מחדש, באף שפה. ההודעה מרונדרת מיד:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "‏`update --check` ידווח שהקטלוגים אינם מעודכנים"

    הערת הסימון הזו ומספרי השורות שזזו מספיקים כדי ש-`pybabel update
    --check` יאמר שקטלוג זקוק לייצור מחדש, מפני שהוא משווה את הרשומה
    כולה ולא רק את התרגום. הריצו את `pybabel update` האמיתי באותו commit
    שבו נמצא שינוי הקוד, וכללו איתו את הקטלוגים — אותו הרגל ש[שער
    ה-CI](workflow.md#what-ci-gates) כבר מבקש.

## מ-`%`-format: ה-msgid משתנה, ולכן התרגומים הופכים ל-fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

תחביר printf חי *בתוך* ההודעה, ולכן החלפתו משכתבת את מפתח הקטלוג. אין
דרך לעקוף את זה, וזו העלות הכנה של פרידה מ-`%(name)s`:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

‏`pybabel update` מזהה את ההודעה החדשה כקרובת משפחה של זו שהוסרה ומעביר
את התרגום הישן, מסומן כ-fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

שלושה דברים שכדאי לדעת על המצב הזה:

- **שום דבר אינו נשבר בזמן ריצה.** רשומות fuzzy מוחרגות מן ה-`.mo`
  המהודר, ולכן היישום מרנדר את הודעת המקור עד שאדם יאשר את הצמד —
  [אותה הידרדרות](workflow.md#the-cycle-after-the-first-translation)
  שכל הודעה שנוסחה מחדש עוברת.
- **ה-CI נשאר ירוק כל עוד הן fuzzy.** בודק מצייני המקום מדלג על רשומות
  fuzzy, בדיוק כפי ש-`msgfmt --check-format` עושה, מפני שרשומה שאינה
  יכולה להגיע לזמן הריצה אינה צריכה להכשיל בנייה. ברגע שמתרגם מסיר את
  הדגל, הרשומה נבדקת ככל רשומה אחרת — ולכן `%(name)s` שנשאר בתרגום
  מאושר נתפס אז, בדיוק בנקודה שבה אחרת הוא היה מתחיל להיות מרונדר.
- **דגל ה-`python-format` הישן נוסע איתה** וכדאי למחוק אותו יחד עם דגל
  ה-`fuzzy`, אחרת `msgfmt --check-format` ימשיך להחיל כללי printf על
  הודעת brace-format.

עבור מצייני מקום של printf בעלי שם העריכה מכנית — `%(name)s` הופך
ל-`{name}` ושום דבר אחר אינו זז — ולכן קטלוג גדול הוא מעבר סקריפטי
ואחריו סקירה של מתרגם, ולא תרגום מחדש. ‏`%s` פוזיציוני אינו מכני: אין
לו שם להעביר, ובחירת שם היא כל תכלית השינוי.

לפיכך המעבר יכול להתקדם בכל קצב שהסקירה מאפשרת: רשומת fuzzy שלא הומרה
היא פיסת עבודה גלויה בקטלוג, לא בנייה שבורה.

## קריאות ישנות וחדשות חיות זו לצד זו { #old-and-new-calls-coexist }

המחלץ שקורא מחרוזות-t קורא גם קריאות gettext רגילות, ולכן מיפוי אחד
מכסה קובץ שנמצא באמצע המעבר:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

שתי ההודעות נוחתות באותה תבנית, ורק זו של מחרוזת-t נושאת את הערת
הסימון שמפעילה את הבדיקה הנוספת של הספרייה הזו:

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

הוא מזהה את `_()`, את ארבעת שמות gettext הסטנדרטיים, את הכינויים
`tr()` / `ntr()`, ואת הגרסאות הדחויות `lazy_gettext()` /
`lazy_pgettext()`. פונקציית עזר משלכם חייבת להיות
[מוזכרת במיפוי](extraction.md#registering-your-own-function-names).

בזמן ריצה שני הסגנונות עצמאיים באותה מידה: `gettext.translation()`
מחזירה אובייקט תרגומים אחד, וגם `_` וגם נקודות הכניסה של הספרייה הזו
קוראות ממנו.

## מה שאינו זז { #what-does-not-move }

- **שפות תבניות.** ‏`{% trans %}` של Jinja2, תגי התבנית של Django
  והמחלצים שלהם ב-Babel ממשיכים לעבוד ללא שינוי וממשיכים להזין את אותם
  קטלוגי PO. מחרוזות-t הן תחביר של Python; הן חלות על קוד Python.
- **קובצי הקטלוג שלכם.** בלי שינוי פורמט, בלי קובץ חדש, בלי שלב המרה.
- **פלטפורמת התרגום שלכם.** מבנה החליפין של `.po` זהה, ודגל
  ה-`python-brace-format` שהודעת מחרוזת-t נושאת הוא אותו דגל שהודעת
  `.format()` נושאת — ולכן בקרת האיכות של מצייני המקום ממשיכה לעבוד.
- **קוד שאינו Python.** קטלוג JavaScript או C באותו פרויקט אינו מושפע.

## רשימת תיוג למעבר { #a-migration-checklist }

1. הוסיפו את התוספת `babel` בכל מקום שבו `pybabel` רץ, ושנו את מיפוי
   ה-`python` ב-`babel.cfg` לשיטת `gettext_tstrings` — מיפוי אחד מכסה
   אז את שני הסגנונות, ו-`-k` ממשיך לעבוד עבור הקריאות הרגילות.
2. המירו תחילה את אתרי הקריאה של `.format()`. חלצו מחדש, הריצו
   `pybabel update`, וכללו את הקטלוגים יחד עם הקוד; אל תצפו לרשומות
   fuzzy.
3. המירו את אתרי הקריאה של `%`-format במנות שאפשר להעביר בסקירה, תוך
   שכתוב מצייני המקום שהועברו והסרת הדגלים `fuzzy` ו-`python-format`.
4. תקנו את מה שההגבלה דוחה: אינטרפולציה חייבת להיות שם פשוט, ולכן
   `t"Hello {user.name}"` הופך תחילה למשתנה לוקלי. זו עריכה באתר
   הקריאה, לא בקטלוג.
5. הפעילו `strict = true` במיפוי המחלץ ברגע שהסריקה הסתיימה, כדי
   שהודעה שאי אפשר לחלץ תכשיל את
   [הבנייה](extraction.md#lenient-locally-strict-in-ci) במקום להיעלם
   מהתבנית.
6. הוסיפו את בדיקת זמן הריצה מתוך
   [בסביבת ייצור](workflow.md#what-ci-gates): רנדרו הודעה אחת לכל שפה
   נשלחת דרך `Translator` קפדני.

שלבים 2 ו-3 הם commits רגילים. שום דבר ברשימה הזו אינו דורש יום מעבר
אחד גדול.
