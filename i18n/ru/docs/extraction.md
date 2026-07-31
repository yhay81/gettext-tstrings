---
description: "Извлечение t-string-сообщений через pybabel и проверка каталогов с msgfmt и встроенным checker Babel."
---

# Извлечение

Извлечение — это шаг, который собирает все помеченные сообщения из исходного
кода в шаблон `.pot` для переводчиков — шаг 3 цикла из
[учебника](tutorial.md). Эта страница — справочник по этому шагу: настройка,
собственные имена функций, строгий режим для CI и проверки, которые затем
охраняют ваши каталоги.

Для извлечения нужен extra `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Процесс { #the-workflow }

Создайте `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Затем используйте обычные команды Babel:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` выполняется один раз на язык; дальше `pybabel update` вливает каждый
свежий шаблон в существующие каталоги. Этот регулярный цикл — и что его
записи `fuzzy` значат для релиза — разобран в разделе
[В продакшене](workflow.md#the-cycle-after-the-first-translation).

Экстрактор обрабатывает также `_()`, `gettext()` и `ngettext()`. Одно
сопоставление покрывает смешанный код с `tr()`, `ntr()`, `lazy_gettext()` и
`lazy_pgettext()`.

!!! warning "Включите комментарии для переводчиков через `-c`"

    Передайте `-c "Translators:"`, чтобы собрать комментарии для переводчиков,
    как в обычном gettext. Без этого флага извлечение всё равно работает —
    просто комментарии никогда не доходят до каталога, где они
    [самый дешёвый рычаг качества](workflow.md#working-with-translators-and-platforms)
    во всём процессе.

## Собственные имена функций { #registering-your-own-function-names }

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

В INI значение — строка с разделителями-пробелами или запятыми; TOML принимает
список. Опции охватывают все шесть семейств функций gettext.

!!! danger "`-k` не видит t-string"

    Helper вроде `mytr(t"…")` нужно объявить в этих опциях. Механизм Babel
    `--keyword` не читает литералы t-string:
    `pybabel extract -k mytr` пропустит их без предупреждения.

    Поддерживается только стандартный порядок аргументов.

## Снисходительно локально, строго в CI { #lenient-locally-strict-in-ci }

По умолчанию один плохой файл не срывает весь запуск:

- Отклонённая t-строка отмечается предупреждением и пропускается.
- Неразбираемый файл изолируется тем же способом.
- Файл, отклонённый только `tokenize`, также изолируется.

Это удобно, пока вы правите код, и опасно, когда уже не правите: пропущенное
сообщение просто **отсутствует в POT**, поэтому оно никогда не будет переведено
и никто об этом не скажет. Ставьте `strict = true` в опциях сопоставления
везде, где за извлечением не следит человек:

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

Каждое предупреждение выше тогда становится жёсткой ошибкой. Считайте такую
настройку продакшен-настройкой, а поведение по умолчанию — локальной.

## Проверка существующими инструментами { #your-existing-toolchain-validates-these-catalogs }

Babel добавляет стандартный флаг:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Перевод `こんにちは {nombre}` обнаруживается без настройки:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate документирует эту проверку как
[Python brace format][weblate-checks], а у коммерческих платформ есть
собственный QA заполнителей, привязанный к тому же флагу. Поведение каждой
платформы — её собственное дело; здесь проверены два инструмента ниже: msgfmt
и поставляемый checker Babel.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

`pybabel compile` применяет checker к каждому отмеченному сообщению:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Для множественного числа ошибка называет форму:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` всё равно записывает `.mo`"

    Ошибка выше сообщается, статус выхода равен `1` — и неверный каталог
    всё равно компилируется. Остановить pipeline от его выпуска может только
    этот статус выхода; [Что проверяет CI](workflow.md#what-ci-gates)
    показывает шаг сборки, который это делает.

Проверки не дублируют друг друга: checker из этого пакета строже как минимум в
двух случаях — он отдельно проверяет
экранированные скобки и каждую множественную форму там, где msgfmt может принять
файл. ASCII-имена позволяют участвовать всем инструментам; сама библиотека
принимает любое `str.isidentifier()`.

## Шаблоны и другие инструменты { #templates-and-other-tools }

t-строки — синтаксис Python. Jinja2 (`{% trans %}`), Django и другие шаблоны
сохраняют свои экстракторы, записывая в тот же PO-каталог.

`pygettext` пока не разбирает t-строки. Другие экстракторы могут реализовать
правила [спецификации](spec.md).
