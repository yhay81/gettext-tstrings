---
description: "API часу виконання: яку точку входу обрати, прив'язування каталогу, мова на запит, відкладені рядки, значення з урахуванням локалі і як повідомляється про зіпсований переклад."
---

# Посібник

Ця сторінка — довідник часу виконання: усе, що робить із цією бібліотекою
ваш *код застосунку*, коли каталоги вже існують. Якщо ви ще не бачили повного
циклу — позначити, видобути, перекласти, скомпілювати, запустити —
[підручник](tutorial.md) проходить його раз за п'ять хвилин; створення й
перевірку каталогів описує [Видобування](extraction.md), а те, як команда
підтримує обертання циклу — оновлення, CI, платформи перекладу, — сторінка
[У продакшені](workflow.md).

## Яку точку входу обрати? { #which-entry-point-should-i-use }

Пакет експортує кілька способів перекласти повідомлення, бо застосунки
прив'язують мову кількома різними шляхами. Обирайте за тим, як ваша програма
вирішує, якою мовою вона зараз говорить:

| Ваша ситуація | Використовуйте |
| --- | --- |
| Одна мова на весь процес — CLI, настільний застосунок, скрипт | `Translator`, викликаний як `_` |
| Одна мова на запит чи на асинхронне завдання — вебзастосунок | `use_translations()` навколо роботи, далі `tr()` |
| Повідомлення, означене під час імпорту, — підпис поля, enum, стала | `lazy_gettext()` або `lazy_pgettext()` |
| Формулювання обирає кількість | `ngettext()` / `npgettext()`, у будь-якій із форм вище |
| Рендеринг шаблона без жодного каталогу | `compile_template()` |

Усе нижче — це ті самі п'ять пунктів, у тому самому порядку.

## Прив'язування каталогу { #binding-a-catalog }

Рекомендована форма віддзеркалює класове використання gettext: прив'яжіть
стандартний об'єкт перекладів один раз і використовуйте викликаний процесор
як `_`.

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

Функції рівня модуля наслідують імена стандартної бібліотеки та її угоду про
лише позиційні аргументи:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` і `ntr` — точні псевдоніми `gettext` і `ngettext`.

## Мова на запит { #per-request-language }

Вебфреймворк обирає мову для кожного запиту. Прив'яжіть переклади запиту до
поточного контексту — і кожен виклик рівня модуля розв'яжеться в цю мову,
безпечно між конкурентними запитами:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` прив'язує без блока `with` — для
фреймворків, які самі керують життєвим циклом запиту; `get_translations()`
читає поточну прив'язку. Явний аргумент `translations=` завжди перемагає
контекст, а неприв'язаний контекст відкочується до глобально встановлених
функцій gettext стандартної бібліотеки. Готові приклади для Flask і
ASGI-проміжного шару — на сторінці
[У продакшені](workflow.md#binding-a-language-at-runtime).

## Відкладений переклад { #deferred-translation }

t-рядок захоплює свої значення одразу, що неправильно для рядка, визначеного
під час імпорту, — підпису форми, значення enum, модульної константи, — який
має відрендеритися тією мовою, що активна в момент його *використання*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` рендериться через `str()`, `format()` та f-рядки і дорівнює при
порівнянні своєму відрендереному тексту.

!!! note "Навмисно негешований"

    Текст `LazyString` залежить від активної мови, тож геш змінювався б при
    перемиканні мови й тихо псував би будь-яку множину чи словник, що його
    тримає. Якщо потрібен ключ, спершу викличте `str()`.

`strict` вирішується там, де повідомлення *написане*, а не там, де воно
рендериться:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Відкладений рядок рендериться там, де його врешті використано — у шаблоні, у
формі, у рядку журналу, — і це місце рідко знає, тестовий це прогін чи
продакшен. Передавання `strict=True` при визначенні — це те, що дозволяє
застосувати той самий вибір
[гучно в CI, поблажливо у продакшені](#what-happens-when-a-catalog-is-wrong)
й до рядка, який рендериться не в місці свого виклику.

Форми множини залежать від лічильника часу виконання, тож рендерте їх одразу
через `ngettext` там, де лічильник відомий.

## Кілька мов одночасно { #several-languages-at-once }

Один запит нерідко потребує більш ніж однієї мови: сторінка, відрендерена для
читача, ще й ставить у чергу сповіщення до облікового запису з іншою мовою; або
дайджест цитує кожного учасника його власною. Прив'язки вкладаються, а вихід із
внутрішнього блока відновлює зовнішній.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

На списку одержувачів роботу роблять відкладені рядки: повідомлення написане
один раз, під час імпорту, а рендериться по разу на кожну мову.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Прив'язка — це `ContextVar`, а не стек на спільному об'єкті, тож запити, що
перекриваються, не можуть підхопити мову одне одного — зокрема й у випадку,
коли вони *виходять* зі своїх блоків у тому самому порядку, в якому входили;
саме на цьому чергуванні магазинний стек помиляється. Завантажувати каталог на
кожну мову дешево: `gettext.translation()` розбирає кожен `.mo` один раз і
роздає копії, які спільно користуються розібраним каталогом.

!!! warning "Чи успадкує робочий потік прив'язку, залежить від збірки"

    Голий `threading.Thread` чи `ThreadPoolExecutor.submit` стартує або з копії
    контексту того, хто його викликав, або з порожнього, а котре саме —
    визначає `sys.flags.thread_inherit_context`: типово істинний на
    free-threaded збірках і хибний усюди інде. Тому той самий код рендерить
    прив'язану мову на 3.14t і глобальний для процесу каталог на 3.14.
    Передавайте контекст, а не покладайтеся на типове значення:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` уже робить це за вас.

## Значення з урахуванням локалі { #locale-aware-values }

Ця бібліотека вирішує, *де* значення з'явиться в перекладеному повідомленні.
Саме значення вона не локалізує. `{amount:,.2f}` — це специфікація формату
Python із фіксованою поведінкою: кома через кожні три цифри й крапка перед
десятковими, — і вона дає ті самі символи, хоч би якою мовою було
повідомлення:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Німецька пише це число як `1.234,50`, французька — `1 234,50`, а гінді
групує `1234567` як `12,34,567`, а не `1,234,567`. Числа, валюти, дати, час і
одиниці — це справа [Babel][babel-numbers]. Спершу відформатуйте значення,
потім розмістіть готовий рядок:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

У повідомленні з лічильником число виконує дві роботи — воно обирає форму
множини і воно з'являється в тексті, — і локалізується лише друга. Лишіть
сиру кількість для вибору форми, а для показу передайте відформатований рядок:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Форматування перед викликом — це також те, що тримає специфікацію формату
поза каталогом: перекладач бачить готовий шматок тексту, а не число разом з
інструкціями, як його рендерити.

## Що відбувається, коли каталог хибний { #what-happens-when-a-catalog-is-wrong }

Якщо заповнювачі перекладу не збігаються з джерелом — відсутнє, невідоме чи
переформатоване поле, що прослизнуло повз перевірку, з відредагованого вручну
MO, вендорного каталогу чи конвеєра, який пропускає чекер, — типова поведінка
полягає в тому, щоб відрендерити початкове повідомлення, а не кинути виняток. Це
віддзеркалює власний контракт gettext: поганий каталог ніколи не ламає
застосунок.

З `Hello {name}`, перекладеним як `こんにちは {nombre}`, рендеринг вдається, а
в логер `gettext_tstrings` іде одне попередження:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Попередження спрацьовує один раз на повідомлення і шаблон, а не на кожен
рендеринг, тож зламаний запис каталогу не затоплює журнал.

Увімкніть гучну відмову для тестів і CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Той самий пошук тоді кидає виняток із тим самим реченням, але без половини
про «using source text»:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

Ці повідомлення написані для того, хто може на них подіяти, а для проблеми з
каталогом це частіше перекладач, ніж програміст, — тож там, де заповнювач
виглядає наявним, але таким не є, повідомлення пояснює чому, замість повторити,
що його бракує. Повноширинні дужки, подвоєне `{{name}}`, невидимий нерозривний
пробіл, кирилична літера серед латинських: кожен випадок має власне
формулювання, перелічене з прикладами на сторінці
[Для перекладачів](translators.md#reading-a-failure-message). Ту сторінку
написано так, щоб її можна було дати людині, яка редагує `.po`.

## Рендеринг шаблона без каталогу { #rendering-a-pattern-without-a-catalog }

`compile_template` відкриває ту саму машинерію на рівень нижче: він
перетворює t-рядок на msgid плюс зв'язаний набір значень і рендерить
будь-який шаблон, який ви йому передасте.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` перевіряє за тими самими правилами і при розбіжності **завжди кидає
виняток**. Поблажливого режиму тут немає: поблажливість існує, щоб пошук у
*каталозі* міг деградувати до початкового тексту, а шаблону, який ви передали
самі, нема від чого деградувати.

## Безпека та межі { #safety-and-scope }

Це припустимо:

```python
tr(t"Hello {name}")
```

Це відхиляється навмисно:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Спершу обчисліть осмислене значення:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Обмеження дає стабільні ключі каталогу, дає перекладачам корисні імена й не
дозволяє перекладеному рядку стати мовою виразів.

Гарантія обмежена *структурою та форматуванням*: переклад ніколи не
обчислюється й ніколи не може додати доступ до атрибутів, виклики,
перетворення чи специфікації формату. Дві речі лишаються відповідальністю
того, хто викликає, — точно як зі stdlib gettext: **екранування**
відрендереного виводу під його призначення (HTML, оболонка, термінал) і
**цілісність каталогу**, адже ворожий каталог може повторити заповнювач, щоб
роздути розмір виводу, — це властиво будь-якій i18n на заповнювачах.

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
