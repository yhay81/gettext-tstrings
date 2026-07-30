---
description: "Все публичные имена gettext_tstrings: функции, Translator, привязка контекста, отложенные строки и ошибки."
---

# API

Все перечисленные имена экспортируются из `gettext_tstrings`. Остальные имена
не являются публичными.

## Перевод

Каждая функция принимает t-строку позиционно, а `translations` и `strict` —
именованными аргументами
([руководство](guide.md#what-happens-when-a-catalog-is-wrong)).

| Функция | Сигнатура |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | псевдоним `gettext` |
| `ntr` | псевдоним `ngettext` |

### `Translator`

Frozen dataclass, привязывающий объект переводов:

```python
Translator(translations, strict=False)
```

Он вызываемый (`_(t"…")`) и предоставляет `gettext`, `ngettext`, `pgettext`,
`npgettext`, `tr` и `ntr`.

## Привязка контекста

| Имя | Назначение |
| --- | --- |
| `use_translations(translations)` | Привязывает на время блока `with`, затем восстанавливает. |
| `set_translations(translations)` | Привязывает без блока для управляемого фреймворком цикла. |
| `get_translations()` | Возвращает текущую привязку или `None`. |

Используется `ContextVar`, поэтому привязка безопасна при конкурентном
выполнении.

## Отложенные строки

| Имя | Назначение |
| --- | --- |
| `lazy_gettext(template, /)` | Откладывает перевод до использования. |
| `lazy_pgettext(context, template, /)` | Вариант с контекстом. |
| `LazyString` | Рендерится через `str()`, `format()` и f-строки, сравнивается с текстом и намеренно не хешируется. |

## Низкий уровень

### `compile_template(template, /) -> CompiledTemplate`

Компилирует t-строку, переиспользуя кэшированный статический план.

### `CompiledTemplate`

| Член | Значение |
| --- | --- |
| `.msgid` | Стабильный идентификатор gettext. |
| `.placeholders` | Имена в порядке первого появления. |
| `.render(pattern)` | Проверяет и рендерит; при несоответствии **всегда вызывает исключение**. |

## Типы и ошибки

### `Translations`

`runtime_checkable`-`Protocol` для четырёх стандартных методов:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

Ему соответствуют `gettext.NullTranslations`, `gettext.GNUTranslations` и
`Translations` из Babel.

### Исключения

| Класс | Когда |
| --- | --- |
| `TStringError` | Базовый класс. |
| `InvalidTemplateError` | Исходная t-строка нарушает соглашение. |
| `InvalidTranslationError` | Перевод нарушает соглашение; мягкий режим журналирует и выводит источник. |

## Entry points извлечения

| Группа | Имя | Использование |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` в `babel.cfg` |
| `babel.checkers` | `gettext_tstrings` | автоматически в `pybabel compile` |

## Производительность

Сообщение с одним полем занимает около 0,4 мкс на Apple Silicon вместе с
созданием t-строки — примерно в 2,5 раза больше
`gettext(...).format(...)`. Кэши ограничены и не сохраняют подставленные
значения.

```console
uv run python benchmarks/runtime.py
```
