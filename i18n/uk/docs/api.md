---
description: "Кожне ім'я, яке експортує gettext_tstrings: функції, Translator, прив'язування контексту, ліниві рядки та помилки."
---

# API

Усе нижче експортується з `gettext_tstrings`. Ніщо інше не є публічним. Ця
сторінка — довідник сигнатур; готові приклади кожної функції — у
[посібнику](guide.md).

## Переклад { #translating }

Кожна функція приймає свій t-рядок позиційно і два ключові аргументи:
`translations` (з відкатом до контекстної прив'язки, а потім до глобальних
функцій стандартної бібліотеки) та `strict` (див.
[Посібник](guide.md#what-happens-when-a-catalog-is-wrong)).

| Функція | Сигнатура |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | псевдонім `gettext` |
| `ntr` | псевдонім `ngettext` |

### `Translator`

Заморожений датаклас, що прив'язує один об'єкт перекладів, щоб місця виклику
його не повторювали.

```python
Translator(translations, strict=False)
```

Він викликаний (`_(t"…")`) і несе `gettext`, `ngettext`, `pgettext`,
`npgettext` та псевдоніми `tr` / `ntr`.

## Прив'язування контексту { #context-binding }

| Ім'я | Призначення |
| --- | --- |
| `use_translations(translations)` | Прив'язати на час блока `with`, потім відновити. |
| `set_translations(translations)` | Прив'язати без блока, для життєвих циклів під керуванням фреймворку. |
| `get_translations()` | Прочитати поточну прив'язку або `None`. |

Прив'язка — це `ContextVar`, тож вона поконтекстна і безпечна за
конкурентності.

## Відкладені рядки { #deferred-strings }

| Ім'я | Призначення |
| --- | --- |
| `lazy_gettext(template, /)` | Відкласти переклад до першого використання. |
| `lazy_pgettext(context, template, /)` | Контекстна форма. |
| `LazyString` | Те, що повертають обидві. Рендериться через `str()` і `format()`, дорівнює своєму тексту при порівнянні й навмисно негешований. |

## Нижчий рівень { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Скомпілювати t-рядок, перевикористовуючи його кешований статичний план.

### `CompiledTemplate`

| Член | Значення |
| --- | --- |
| `.msgid` | Стабільний ідентифікатор повідомлення gettext. |
| `.placeholders` | Імена заповнювачів у порядку першої появи. |
| `.render(pattern)` | Перевірити один шаблон і відрендерити його. При розбіжності **завжди кидає виняток**. |

## Типи та помилки { #types-and-errors }

### `Translations`

`runtime_checkable` `Protocol` для чотирьох стандартних методів, усі лише
позиційні:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` і `Translations` з
Babel — усі його задовольняють.

### Винятки

| Клас | Коли підіймається |
| --- | --- |
| `TStringError` | Базовий клас обох нижче. |
| `InvalidTemplateError` | Угоду порушує **вихідний** t-рядок — складна інтерполяція або повторене ім'я з різним форматуванням. |
| `InvalidTranslationError` | Її порушує **переклад**. У типовому поблажливому режимі це записується в журнал, а натомість рендериться початковий текст. |

## Точки входу видобування { #extraction-entry-points }

Реєструються автоматично при встановленні; ви звертаєтеся до них за іменем, а
не через import.

| Група | Ім'я | Використовується |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` у `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, автоматично. |

## Продуктивність { #performance }

Повний виклад — що кешується, на чому кеші ключуються і виміряні числа — це
[Гарячий шлях](internals.md#the-hot-path). Коротка версія: перевірка
кешується й ніколи не пропускається, а весь рендеринг коштує частку
мікросекунди. Запустіть бенчмарк на власній цілі:

```console
uv run python benchmarks/runtime.py
```
