---
description: "חילוץ הודעות מחרוזת-t באמצעות pybabel, וכיצד msgfmt ובודק Babel המצורף מאמתים את הקטלוגים."
---

# חילוץ

חילוץ הוא השלב שאוסף כל הודעה מסומנת מקוד המקור שלכם אל תבנית `.pot`
עבור המתרגמים — שלב 3 בלולאה של [מדריך המבוא](tutorial.md). עמוד זה הוא
חומר העזר לשלב הזה: תצורה, שמות פונקציות מותאמים אישית, מצב קפדני
ב-CI, והבדיקות ששומרות על הקטלוגים שלכם לאחר מכן.

החילוץ דורש את התוסף `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## תהליך העבודה { #the-workflow }

צרו `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

לאחר מכן השתמשו בפקודות Babel הרגילות:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` רץ פעם אחת לכל שפה; לאחר מכן `pybabel update` ממזג כל תבנית
טרייה אל תוך הקטלוגים הקיימים. המחזור החוזר הזה — ומה שרשומות ה-`fuzzy`
שבו אומרות לגבי שחרור גרסה — מוסבר צעד אחר צעד בעמוד
[בסביבת ייצור](workflow.md#the-cycle-after-the-first-translation).

המחלץ `gettext_tstrings` מטפל גם בקריאות רגילות ל-`_()`, `gettext()`
ו-`ngettext()`, כך שמיפוי אחד מכסה בסיס קוד מעורב. הוא מזהה את `_()`,
את ארבעת שמות gettext הסטנדרטיים, את הכינויים `tr()` / `ntr()`, ואת
הגרסאות הדחויות `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "הפעילו הערות למתרגמים עם `-c`"

    `pybabel extract` אוסף הערות למתרגמים רק כאשר מעבירים
    `-c "Translators:"`, בדיוק כפי שהוא נוהג בקריאות gettext רגילות. אם
    תשמיטו את הדגל החילוץ עדיין יעבוד — פשוט ההערות לעולם לא יגיעו
    לקטלוג, ושם הן [מנוף האיכות הזול ביותר](workflow.md#working-with-translators-and-platforms)
    בכל צינור העבודה.

## רישום שמות פונקציות משלכם { #registering-your-own-function-names }

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

קובץ ini נותן מחרוזת אחת, מיפוי TOML נותן רשימה, ובתוך מחרוזת מפרידים
בין השמות רווחים או פסיקים. כל ארבע צורות הכתיבה עובדות.

האפשרויות הן `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` ו-`npgettext_functions`.

!!! danger "`-k` אינו מגיע אל מחרוזת-t"

    פונקציית עזר מותאמת אישית כגון `mytr(t"…")` חייבת להיות מוזכרת
    באחת מהאפשרויות שלעיל. מנגנון ה-`--keyword` של Babel אינו מסוגל
    לקרוא ליטרל של מחרוזת-t, ולכן `pybabel extract -k mytr` אינו מוצא
    דבר ואינו אומר דבר — ההודעות פשוט נעדרות מקובץ ה-POT. `-k` ממשיך
    לעבוד עבור קריאות gettext הרגילות שמחולצות לצידן.

    נתמך רק סדר הארגומנטים הסטנדרטי: ההודעה תחילה, הקשר ואז הודעה
    עבור `pgettext`, הקשר ואז יחיד ואז רבים עבור `npgettext`.

## סלחני מקומית, קפדני ב-CI { #lenient-locally-strict-in-ci }

כברירת מחדל, קובץ פגום אחד אינו מסיים את הריצה:

- מחרוזת-t שהמחלץ דוחה — גישה לתכונה, ביטוי, ארגומנט שגוי — מדווחת
  כאזהרה ומדולגת.
- קובץ שאינו ניתן לניתוח מדולג באותו אופן.
- וכך גם קובץ שרק `tokenize` דוחה בעוד `ast` מקבל אותו — קובץ שהמעבר של
  Babel עצמו היה קורס עליו.

זה נוח כל עוד אתם עורכים, ומסוכן כשאינכם: הודעה שדולגה פשוט **נעדרת
מקובץ ה-POT**, ולכן היא לעולם אינה מתורגמת ואיש אינו מודיע על כך.
הגדירו `strict = true` באפשרויות המיפוי בכל מקום שבו החילוץ אינו נצפה
בידי אדם:

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    encoding = utf-8
    strict = true
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    strict = true
    ```

כל אזהרה שלעיל הופכת אז לכשל קשיח. התייחסו לזה כאל ההגדרה של סביבת
הייצור, ולברירת המחדל כאל ההגדרה המקומית.

## שרשרת הכלים הקיימת שלכם מאמתת את הקטלוגים האלה { #your-existing-toolchain-validates-these-catalogs }

Babel מסמן כל הודעה מחולצת בדגל סטנדרטי, והשורה האחת הזאת היא שמפעילה
את בדיקת מצייני המקום בכלים שאתם כבר מריצים:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

תרגמו אותה כ-`こんにちは {nombre}` והטעות נתפסת ללא כל תצורה:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate מתעד את אותה בדיקה בשם [Python brace format][weblate-checks],
ולפלטפורמות המסחריות יש בקרת איכות משלהן למצייני מקום, המבוססת על אותו
דגל. ההתנהגות של כל פלטפורמה היא עניינה שלה; שני הכלים שלהלן הם אלה
שאומתו כאן.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

בנוסף לכך, החבילה רושמת **בודק** (checker) של Babel, כך
ש-`pybabel compile` מחיל את כללי המפרט על כל הודעה הנושאת את הערת
הסימון `gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

עבור הודעת ריבוי, ההצבעה מציינת את שם הצורה, משום שמספר השורה ש-Babel
מדווח הוא של ה-msgid, ומתחתיו בבלוק רוסי יש שלוש שורות `msgstr`:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` עדיין כותב את קובץ ה-`.mo`"

    השגיאה שלעיל מדווחת, קוד היציאה הוא `1` — והקטלוג השבור מקומפל בכל
    זאת. רק קוד היציאה הזה יכול למנוע מצינור עבודה לשלוח אותו;
    [מה ש-CI חוסם](workflow.md#what-ci-gates) מציג את שלב הבנייה
    שמאפשר זאת.

שתי הבדיקות אינן כפל מיותר. הבודק של החבילה קפדני יותר בלפחות שני
מקרים:

- msgid שהסוגריים המסולסלים היחידים בו מוברחים (`Config {{raw}} only`)
  לעולם אינו מקבל את הדגל `python-brace-format`, ולכן שום כלי חיצוני
  אינו מאמת אותו כלל.
- צורות ריבוי נבדקות אחת-אחת. `msgfmt --check-format` קורא את הקובץ
  שלעיל ממש ויוצא עם `0`; צורה שמשמיטה מציין מקום שאחיותיה שומרות
  מתקבלת שם ונדחית כאן.

`msgfmt` בודק רק שמות מצייני מקום שהוא מסוגל לנתח כ-Python brace
format, ולכן שמות ASCII משאירים את כל הכלים בשרשרת מסוגלים לאמת את
ההודעה. הספרייה עצמה מקבלת כל שם העומד ב-`str.isidentifier()`.

## תבניות וכלים אחרים { #templates-and-other-tools }

מחרוזות-t הן תחביר של Python, ולכן ספרייה זו מכסה קוד מקור של Python.
שפות תבניות ממשיכות להשתמש ב-i18n משלהן — `{% trans %}` של Jinja2, תגי
התבנית של Django — ובמחלצים של Babel המיועדים להן. הכול מזין את אותו
קטלוג PO, כך שתהליך תרגום אחד עדיין מכסה בסיס קוד מעורב.

`pygettext` אינו מסוגל כיום לנתח מחרוזות-t, ולכן החילוץ עובר דרך
Babel. המוסכמה כתובה ב[מפרט](spec.md) כדי שמחלץ אחר, או `pygettext`
עתידי, יוכל לכוון אליה.
