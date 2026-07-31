---
description: "API времени выполнения: привязка каталога, язык запроса, отложенные строки и обработка неверных переводов."
---

# Руководство

Эта страница — справочник по времени выполнения: всё, что делает с этой
библиотекой *код приложения*, когда каталоги уже существуют. Если вы ещё не
видели весь цикл — пометить, извлечь, перевести, скомпилировать, запустить, —
[учебник](tutorial.md) проходит его за пять минут; создание и проверка
каталогов описаны в разделе [Извлечение](extraction.md), а то, как команда
поддерживает вращение цикла — циклы обновления, CI, платформы перевода, —
в разделе [В продакшене](workflow.md).

## Привязка каталога { #binding-a-catalog }

Рекомендуемая форма повторяет объектный API gettext: один раз привяжите
стандартный объект переводов и используйте вызываемый обработчик как `_`.

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

Функции модуля повторяют имена и позиционные аргументы стандартной библиотеки:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` и `ntr` — точные псевдонимы `gettext` и `ngettext`.

## Язык для каждого запроса { #per-request-language }

Веб-фреймворк выбирает язык для каждого запроса. Привяжите перевод к текущему
контексту, и все вызовы модуля будут использовать этот язык даже при
параллельных запросах.

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations()` привязывает без блока, если жизненным циклом управляет
фреймворк; `get_translations()` читает привязку. Явный `translations=` имеет
приоритет. Без привязки fallback — глобальные функции gettext стандартной
библиотеки. Разобранные примеры для Flask и middleware ASGI — на странице
[В продакшене](workflow.md#binding-a-language-at-runtime).

## Отложенный перевод { #deferred-translation }

t-строка захватывает значения немедленно. Для метки, enum или константы,
созданной при импорте, но выводимой на активном языке в момент *использования*,
применяйте отложенную строку.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` рендерится через `str()`, `format()` и f-строки и сравнивается с
текстом.

!!! note "Намеренно не хешируется"

    Текст зависит от языка. Изменение хеша незаметно повредило бы set или dict.
    Для ключа сначала вызовите `str()`.

`strict` задаётся там, где сообщение написано, а не там, где оно рендерится:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Отложенная строка рендерится там, где её в итоге используют, — внутри шаблона,
формы, строки лога, — и это место редко знает, тестовый ли это прогон или
продакшен. Именно передача `strict=True` при определении позволяет применить к
строке, которая рендерится не в месте вызова, тот же выбор
[«громко в CI, снисходительно в продакшене»](#what-happens-when-a-catalog-is-wrong).

Множественные формы зависят от числа во время выполнения; выводите их сразу
через `ngettext`.

## Несколько языков сразу { #several-languages-at-once }

Одному запросу часто нужен не один язык: страница, отрисованная для читателя,
рядом с уведомлением в очередь для аккаунта, у которого выбран другой, или
дайджест, цитирующий каждого участника на его собственном. Привязки
вкладываются, и выход из внутреннего блока восстанавливает внешний.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Для списка получателей работу делают отложенные строки: сообщение написано
один раз, при импорте, и рендерится по разу на каждый язык.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Привязка — это `ContextVar`, а не стек, лежащий в общем объекте, поэтому
перекрывающиеся запросы не могут подхватить язык друг друга — в том числе
когда они *выходят* из своих блоков в том же порядке, в каком вошли; именно на
таком чередовании стек с проталкиванием ошибается. Загружать каталог на каждый
язык дёшево: `gettext.translation()` разбирает каждый `.mo` один раз и раздаёт
копии, которые пользуются общим разобранным каталогом.

!!! warning "Рабочий поток стартует без привязки"

    Обычный `threading.Thread` или `ThreadPoolExecutor.submit` начинает работу
    со свежим контекстом и не наследует привязку — вызов откатывается к
    глобальному для процесса каталогу gettext. Переносите контекст явно:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` уже делает это за вас.

## Если каталог неверен { #what-happens-when-a-catalog-is-wrong }

Если заполнители перевода не соответствуют источнику, режим по умолчанию
выводит исходный текст вместо исключения. Это контракт gettext: неверный
каталог не должен останавливать приложение.

Если `Hello {name}` переведено как `こんにちは {nombre}`, рендеринг завершается,
а logger `gettext_tstrings` получает предупреждение:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Предупреждение появляется один раз для каждой пары сообщения и шаблона, а не
при каждом рендеринге, поэтому неверная запись каталога не заливает журнал.

В тестах и CI включайте строгий режим:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Тогда тот же поиск вызывает исключение:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Чтение сообщений об ошибках { #reading-a-failure-message }

Сообщения объясняют и то, почему видимый заполнитель неверен:

| Перевод содержит | Причина |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Невидимый неразрывный пробел показывается как кодовая точка:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Омоглиф из другого алфавита показан читаемо и в экранированном виде:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Это также обнаруживает конфликты полностью греческих или кириллических имён с
их ASCII-аналогами.

## Рендеринг шаблона без каталога { #rendering-a-pattern-without-a-catalog }

`compile_template` создаёт msgid, связывает значения и рендерит шаблон:

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` проверяет по тем же правилам и при несоответствии **всегда вызывает
исключение**. Без поиска в каталоге нет fallback.

## Безопасность и границы { #safety-and-scope }

Допустимо:

```python
tr(t"Hello {name}")
```

Намеренно отклоняется:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Сначала явно вычислите значение:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Перевод никогда не вычисляется и не может добавить доступ к атрибутам, вызов,
преобразование или формат. Как и с обычным gettext, приложение отвечает за
**экранирование для места вывода** и **целостность каталога**.
