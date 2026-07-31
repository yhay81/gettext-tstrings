---
description: "Видобування t-рядкових повідомлень через pybabel і як msgfmt та вбудований чекер Babel перевіряють каталоги."
---

# Видобування

Видобування — це крок, що збирає кожне позначене повідомлення з вашого
вихідного коду в шаблон `.pot` для перекладачів — крок 3 циклу
[підручника](tutorial.md). Ця сторінка — довідник цього кроку: налаштування,
власні імена функцій, строгий режим для CI та перевірки, що охороняють ваші
каталоги опісля.

Видобуванню потрібен extra `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Процес { #the-workflow }

Створіть `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Потім використовуйте звичайні команди Babel:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` запускається один раз на мову; далі `pybabel update` вливає кожен
свіжий шаблон у наявні каталоги. Цей повторюваний цикл — і що його записи
`fuzzy` означають для релізу — розібрано в
[У продакшені](workflow.md#the-cycle-after-the-first-translation).

Видобувач `gettext_tstrings` обробляє і звичайні виклики `_()`, `gettext()`
та `ngettext()`, тож одне зіставлення покриває мішану кодову базу. Він
розпізнає `_()`, чотири стандартні імена gettext, псевдоніми `tr()` / `ntr()`
і відкладені `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "`-c` не є необов'язковим"

    `pybabel extract` збирає коментарі для перекладачів лише тоді, коли ви
    передаєте `-c "Translators:"`, — точно як для звичайних викликів gettext.

## Реєстрація власних імен функцій { #registering-your-own-function-names }

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

Файл ini дає один рядок, TOML-зіставлення дає список, а всередині рядка імена
розділяються пробілами або комами. Працюють усі чотири написання.

Доступні опції: `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` і `npgettext_functions`.

!!! danger "`-k` не дістає до t-рядка"

    Власний помічник на кшталт `mytr(t"…")` мусить бути названий в одній з
    опцій вище. Механізм `--keyword` у Babel не вміє читати літерал t-рядка,
    тож `pybabel extract -k mytr` нічого не знаходить і нічого не каже —
    повідомлення просто відсутні в POT. `-k` і далі працює для звичайних
    викликів gettext, що видобуваються поруч.

    Підтримується лише стандартний порядок аргументів: спершу повідомлення;
    контекст, потім повідомлення для `pgettext`; контекст, однина, множина
    для `npgettext`.

## Стійкість за замовчуванням { #robust-by-default }

Один поганий файл не завершує прогін:

- t-рядок, який видобувач відхиляє, — доступ до атрибута, вираз, хибний
  аргумент — повідомляється попередженням і пропускається.
- Файл, що не парситься, пропускається так само.
- Так само й файл, який відкидає лише `tokenize`, тоді як `ast` його приймає,
  — на такому власний прохід Babel інакше б аварійно зупинився.

Установіть `strict = true` в опціях зіставлення, щоб перетворити кожен із цих
випадків на жорстку відмову, — саме це вам потрібно в CI.

## Ваш наявний інструментарій перевіряє ці каталоги { #your-existing-toolchain-validates-these-catalogs }

Babel позначає кожне видобуте повідомлення стандартним прапорцем, і саме цей
один рядок вмикає перевірку заповнювачів в інструментах, які ви вже
запускаєте:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Перекладіть його як `こんにちは {nombre}` — і помилку буде впіймано без
жодного налаштування:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate документує ту саму перевірку як [Python brace format][weblate-checks],
а комерційні платформи мають власний контроль заповнювачів, зав'язаний на той
самий прапорець. Їхня поведінка — їхня; два інструменти нижче — ті, що
перевірені тут.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Понад те, пакет реєструє **чекер** Babel, тож `pybabel compile` застосовує
правила специфікації до кожного повідомлення з маркерним коментарем
`gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Для повідомлення з множиною вказівник називає форму, бо номер рядка, який
повідомляє Babel, належить msgid, а російський блок має під ним три `msgstr`:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` все одно записує `.mo`"

    Помилку вище повідомлено, статус виходу — `1`, і зламаний каталог усе
    одно скомпільовано. Лише цей статус виходу може зупинити конвеєр від його
    доставки; [Що вартує CI](workflow.md#what-ci-gates) показує крок збірки,
    який це робить.

Дві перевірки не дублюють одна одну. Постачений чекер — суворіша сторона
щонайменше у двох місцях:

- msgid, чиї єдині дужки екрановані (`Config {{raw}} only`), ніколи не
  отримує прапорця `python-brace-format`, тож жоден зовнішній інструмент його
  взагалі не перевіряє.
- Форми множини перевіряються поодинці. `msgfmt --check-format` читає той
  самий файл вище і виходить із `0`; форма, що викидає заповнювач, який
  тримають її сусідки, там приймається, а тут відхиляється.

`msgfmt` перевіряє лише імена заповнювачів, які може розпарсити як Python
brace format, тож ASCII-імена зберігають здатність кожного інструмента в
ланцюжку перевіряти повідомлення. Сама бібліотека приймає будь-яке ім'я, для
якого `str.isidentifier()` істинне.

## Шаблонізатори та інші інструменти { #templates-and-other-tools }

t-рядки — синтаксис Python, тож ця бібліотека покриває вихідний код Python.
Мови шаблонів і далі користуються власною i18n — `{% trans %}` у Jinja2,
шаблонні теги Django — та видобувачами Babel для них. Усе живить той самий
PO-каталог, тож один процес перекладу так само покриває мішану кодову базу.

`pygettext` сьогодні не вміє парсити t-рядки — тому видобування йде через
Babel. Угода записана у [специфікації](spec.md), щоб інший видобувач або
майбутній `pygettext` міг на неї орієнтуватися.
