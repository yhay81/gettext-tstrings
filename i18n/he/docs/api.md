---
description: "כל שם ש-gettext_tstrings מייצאת: הפונקציות, ה-Translator, קשירת ההקשר, המחרוזות הדחויות והשגיאות."
---

# API

כל מה שמופיע להלן מיוצא מ-`gettext_tstrings`. שום דבר אחר אינו ציבורי.
עמוד זה הוא מסמך העיון של החתימות; לדוגמאות מלאות לכל פונקציה, ראו את
ה[מדריך](guide.md).

## תרגום { #translating }

כל פונקציה מקבלת את מחרוזת-t שלה כארגומנט פוזיציונלי, ומקבלת שני
ארגומנטים בעלי שם: `translations` (המבצע נסיגה לקשירת ההקשר, ואחריה
לפונקציות הגלובליות של הספרייה הסטנדרטית) ו-`strict` (ראו
[מדריך](guide.md#what-happens-when-a-catalog-is-wrong)).

| פונקציה | חתימה |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | כינוי של `gettext` |
| `ntr` | כינוי של `ngettext` |

### `Translator`

dataclass קפואה הקושרת אובייקט תרגום אחד, כך שאתרי הקריאה אינם צריכים
לחזור עליו.

```python
Translator(translations, strict=False)
```

היא ניתנת לקריאה (`_(t"…")`) ונושאת את `gettext`, את `ngettext`, את
`pgettext`, את `npgettext` ואת הכינויים `tr` / `ntr`.

## קשירת הקשר { #context-binding }

| שם | תפקיד |
| --- | --- |
| `use_translations(translations)` | קושרת למשך בלוק `with`, ואז משחזרת את המצב הקודם. |
| `set_translations(translations)` | קושרת ללא בלוק, עבור מחזורי חיים המנוהלים בידי המסגרת. |
| `get_translations()` | קוראת את הקשירה הנוכחית, או `None`. |

הקשירה היא `ContextVar`, ולכן היא נפרדת לכל הקשר ובטוחה תחת מקביליות.

## מחרוזות דחויות { #deferred-strings }

| שם | תפקיד |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | דוחה את התרגום עד לכל רינדור. |
| `lazy_pgettext(context, template, /, *, strict=False)` | הצורה ההקשרית. |
| `LazyString` | מה ששתיהן מחזירות. עוברת רינדור דרך `str()` ו-`format()` בשפה הקשורה באותו רגע, נחשבת שווה לטקסט המרונדר שלה, ובלתי ניתנת לגיבוב בכוונה. |

דוגמאות מלאות, ובכללן ההסבר למה `strict` שייך למקום ההגדרה, נמצאות תחת
[תרגום דחוי](guide.md#deferred-translation).

## רמה נמוכה יותר { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

מקמפלת מחרוזת-t, תוך שימוש חוזר בתוכנית הסטטית שלה השמורה במטמון.

### `CompiledTemplate`

| חבר | משמעות |
| --- | --- |
| `.msgid` | מזהה ההודעה היציב של gettext. |
| `.placeholders` | שמות מצייני המקום לפי סדר ההופעה הראשונה. |
| `.render(pattern)` | מאמתת דפוס אחד ומרנדרת אותו. **תמיד מעלה חריגה** על אי-התאמה. |

## טיפוסים ושגיאות { #types-and-errors }

### `Translations`

`Protocol` מסומן `runtime_checkable` עבור ארבע המתודות הסטנדרטיות,
כולן פוזיציונליות-בלבד:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, וכן `gettext.GNUTranslations` ו-`Translations`
של Babel — כולם מקיימים אותו.

### חריגות

| מחלקה | מועלית כאשר |
| --- | --- |
| `TStringError` | מחלקת הבסיס לשתי המחלקות שלהלן. |
| `InvalidTemplateError` | מחרוזת-t של ה**מקור** מפרה את המוסכמה — אינטרפולציה מורכבת, או שם החוזר עם עיצוב שונה. |
| `InvalidTranslationError` | ה**תרגום** הוא שמפר אותה. במצב הסלחני, שהוא ברירת המחדל, הדבר נרשם ביומן וטקסט המקור מרונדר במקומו. |

## נקודות כניסה לחילוץ { #extraction-entry-points }

נרשמות אוטומטית בעת ההתקנה; מפנים אליהן לפי שם, לא באמצעות ייבוא.

| קבוצה | שם | בשימוש של |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | ה-`method` שבקובץ `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, אוטומטית. |

## ביצועים { #performance }

התיאור המלא — מה נשמר במטמון, על מה מבוססים מפתחות המטמונים, והמספרים
שנמדדו — נמצא בעמוד [הנתיב החם](internals.md#the-hot-path). הגרסה
הקצרה: האימות נשמר במטמון ולעולם אינו מדולג, והרינדור כולו עולה שבריר
של מיקרו-שנייה. הריצו את מדד הביצועים על היעד שלכם:

```console
uv run python benchmarks/runtime.py
```
