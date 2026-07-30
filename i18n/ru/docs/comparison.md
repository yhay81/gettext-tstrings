---
description: "Одно переводимое сообщение через %-формат, .format() и t-строку — и границы контроля каталога."
---

# Зачем нужны t-строки

Любой способ подстановки значения в переводимое сообщение отвечает на вопрос:
*какую часть языка форматирования должен контролировать каталог?*

## %-форматирование

```python
_("Hello %(name)s") % {"name": name}
```

В каталоге находится синтаксис printf. Потеря одного символа может вызвать
ошибку в production:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

`msgfmt --check-format` это обнаружит, но лишь для сообщений с флагом
`python-format` и только если каталог действительно проходит через msgfmt.

## str.format

```python
_("Hello {name}").format(name=name)
```

Заполнитель именован и легко переставляется. Но `str.format` — небольшой язык
выражений:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Каталог проходит через платформы и людей как данные, однако `.format()` даёт
ему доступ к атрибутам переданных объектов.

## t-строки

```python
tr(t"Hello {name}")
```

msgid остаётся `Hello {name}`, но перевод не исполняется как строка формата. Он
сверяется с заполнителями источника, и допустимы только простые имена:

| Перевод содержит | Причина отклонения |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Форматирование остаётся в приложении:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` никогда не попадает в каталог.

## Сравнение

| | `%(name)s` | `.format()` | `t"…"` |
| --- | --- | --- | --- |
| Именованный заполнитель | да | да | да |
| Можно менять порядок | да | да | да |
| Потеря символа ломает сообщение | **да** | нет | нет |
| Каталог управляет форматом | да | да | **нет** |
| Каталог читает атрибуты | нет | **да** | **нет** |
| Неверный каталог вызывает ошибку при рендеринге | **да** | **да** | по умолчанию [нет](guide.md#what-happens-when-a-catalog-is-wrong) |
| Работает с PO/MO и `msgfmt` | да | да | да |

## Цена

f-строка уже готова к моменту вызова. t-строки ([PEP 750]) требуют Python 3.14
или новее, а каждая интерполяция должна быть простым именем:

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Это ограничение обеспечивает безопасность и даёт переводчикам понятные имена.

  [PEP 750]: https://peps.python.org/pep-0750/
