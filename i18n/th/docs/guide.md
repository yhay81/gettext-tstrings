---
description: "API รันไทม์: ควรใช้จุดเข้าใด การผูกแคตตาล็อก ภาษาแบบต่อคำขอ สตริงแบบเลื่อนเวลา ค่าที่รู้จักโลแคล และวิธีรายงานคำแปลที่เสียหาย"
---

# คู่มือ

หน้านี้คือเอกสารอ้างอิงฝั่งรันไทม์ ครอบคลุมทุกสิ่งที่ *โค้ดแอปพลิเคชัน* ของคุณ
ทำกับไลบรารีนี้เมื่อมีแคตตาล็อกพร้อมแล้ว หากคุณยังไม่เคยเห็นลูปทั้งหมด —
มาร์ก สกัด แปล คอมไพล์ รัน — [บทแนะนำ](tutorial.md) จะพาเดินครบหนึ่งรอบ
ในห้านาที การสร้างและตรวจสอบแคตตาล็อกอธิบายไว้ใน
[การสกัดข้อความ](extraction.md) ส่วนวิธีที่ทีมทำให้ลูปหมุนต่อไป —
รอบการอัปเดต CI แพลตฟอร์มการแปล — อยู่ใน [การใช้งานจริง](workflow.md)

## ควรใช้จุดเข้าไหนดี { #which-entry-point-should-i-use }

แพ็กเกจนี้ส่งออกวิธีแปลข้อความหลายวิธี เพราะแอปพลิเคชันผูกภาษากันคนละแบบ
จงเลือกตามวิธีที่โปรแกรมของคุณตัดสินว่าตอนนี้มันอยู่ในภาษาใด:

| สถานการณ์ของคุณ | ใช้ |
| --- | --- |
| ภาษาเดียวตลอดทั้งโปรเซส — CLI แอปเดสก์ท็อป สคริปต์ | `Translator` เรียกในชื่อ `_` |
| ภาษาเดียวต่อหนึ่งคำขอหรือต่อหนึ่ง async task — เว็บแอปพลิเคชัน | `use_translations()` ครอบงานนั้น แล้วใช้ `tr()` |
| ข้อความที่ถูกนิยามตอน import — ป้ายกำกับฟอร์ม enum ค่าคงที่ | `lazy_gettext()` หรือ `lazy_pgettext()` |
| จำนวนเป็นตัวตัดสินถ้อยคำ | `ngettext()` / `npgettext()` ในรูปแบบใดก็ได้ข้างต้น |
| เรนเดอร์แพตเทิร์นโดยไม่มีแคตตาล็อกเข้ามาเกี่ยวข้อง | `compile_template()` |

ทุกอย่างด้านล่างคือห้าอย่างนั้น เรียงตามลำดับนั้น

## การผูกแคตตาล็อก { #binding-a-catalog }

รูปแบบที่แนะนำสะท้อนการใช้งานแบบคลาสของ gettext: ผูกอ็อบเจกต์การแปลมาตรฐาน
หนึ่งครั้ง แล้วใช้ตัวประมวลผลที่เรียกได้เป็น `_`

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

ฟังก์ชันระดับโมดูลใช้ชื่อเดียวกับไลบรารีมาตรฐาน รวมถึงข้อตกลงการเรียกแบบ
positional-only เช่นเดียวกัน

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` และ `ntr` เป็น alias ที่ตรงกันทุกประการของ `gettext` และ `ngettext`

## ภาษาแบบต่อคำขอ { #per-request-language }

เว็บเฟรมเวิร์กเลือกภาษาเป็นรายคำขอ เมื่อผูกการแปลของคำขอนั้นเข้ากับคอนเท็กซ์
ปัจจุบัน การเรียกระดับโมดูลทุกครั้งจะถูกแปลงเป็นภาษานั้น
อย่างปลอดภัยแม้มีหลายคำขอทำงานพร้อมกัน

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` ผูกโดยไม่ต้องใช้บล็อก `with` สำหรับเฟรมเวิร์ก
ที่จัดการวงจรชีวิตของคำขอเอง ส่วน `get_translations()` อ่านการผูกปัจจุบัน
อาร์กิวเมนต์ `translations=` ที่ระบุอย่างชัดเจนจะชนะคอนเท็กซ์เสมอ
และคอนเท็กซ์ที่ยังไม่ถูกผูกจะถอยกลับไปใช้ฟังก์ชัน gettext ที่ติดตั้งแบบ global
ของไลบรารีมาตรฐาน ตัวอย่างการใช้งานจริงสำหรับ Flask และมิดเดิลแวร์ ASGI
อยู่ที่หน้า [การใช้งานจริง](workflow.md#binding-a-language-at-runtime)

## การแปลแบบเลื่อนเวลา { #deferred-translation }

t-string จับค่าทันทีที่สร้าง ซึ่งไม่ถูกต้องสำหรับสตริงที่นิยามตอน import —
ป้ายกำกับฟอร์ม ค่า enum ค่าคงที่ของโมดูล — ที่ต้องเรนเดอร์ในภาษาที่ใช้งานอยู่
ณ ตอนที่มัน*ถูกใช้*

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` เรนเดอร์ผ่าน `str()`, `format()` และ f-string
และเปรียบเทียบเท่ากับข้อความที่เรนเดอร์แล้ว

!!! note "แฮชไม่ได้โดยตั้งใจ"

    ข้อความของ `LazyString` ขึ้นกับภาษาที่ใช้งานอยู่ ค่าแฮชจึงจะเปลี่ยนไป
    เมื่อสลับภาษา และทำให้ set หรือ dict ใดก็ตามที่เก็บมันไว้เสียหาย
    อย่างเงียบ ๆ หากต้องใช้เป็นคีย์ ให้เรียก `str()` ก่อน

`strict` ถูกตัดสิน ณ จุดที่ *เขียน* ข้อความ ไม่ใช่จุดที่ข้อความถูกเรนเดอร์:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

สตริงแบบเลื่อนเวลาจะเรนเดอร์ ณ ที่ใดก็ตามที่มันถูกใช้จริงในท้ายที่สุด —
ในเทมเพลต ในฟอร์ม ในบรรทัดล็อก — และที่แห่งนั้นแทบไม่เคยรู้เลยว่านี่คือ
การรันเทสต์หรือโปรดักชัน การส่ง `strict=True` ตั้งแต่ตอนนิยามคือสิ่งที่ทำให้
ตัวเลือก[ดังใน CI ผ่อนปรนในโปรดักชัน](#what-happens-when-a-catalog-is-wrong)
อันเดียวกันนี้มีผลกับสตริงที่ไม่ได้ถูกเรนเดอร์ ณ จุดที่เรียกมัน

รูปพหูพจน์ขึ้นกับจำนวนที่รู้ตอนรันไทม์ จึงควรเรนเดอร์ทันทีด้วย `ngettext`
ณ จุดที่รู้จำนวนแล้ว

## หลายภาษาพร้อมกัน { #several-languages-at-once }

คำขอเดียวมักต้องใช้มากกว่าหนึ่งภาษา: หน้าที่เรนเดอร์ให้ผู้อ่าน
แล้วยังจ่อคิวการแจ้งเตือนไปยังบัญชีที่ตั้งค่าไว้เป็นอีกภาษาหนึ่ง
หรือสรุปรวมที่ยกคำพูดของผู้ร่วมสนทนาแต่ละคนในภาษาของเขาเอง การผูกซ้อนกันได้
และเมื่อออกจากบล็อกด้านใน การผูกของบล็อกด้านนอกจะกลับคืนมา

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

เมื่อวนไปตามรายชื่อผู้รับ สตริงแบบเลื่อนเวลาคือสิ่งที่ทำงานให้:
ข้อความถูกเขียนไว้ครั้งเดียวตอน import แล้วเรนเดอร์หนึ่งครั้งต่อหนึ่งภาษา

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

การผูกอยู่ใน `ContextVar` ไม่ใช่สแตกที่แขวนไว้บนอ็อบเจกต์ที่ใช้ร่วมกัน
คำขอที่ทับซ้อนกันจึงหยิบภาษาของกันและกันไปไม่ได้ — รวมถึงกรณีที่มัน*ออก*จากบล็อก
ตามลำดับเดียวกับที่เข้าไป ซึ่งเป็นการสลับกันแบบที่สแตกทำผิดพลาด
การโหลดแคตตาล็อกทีละภาษามีต้นทุนต่ำ: `gettext.translation()` แจงไฟล์ `.mo`
แต่ละไฟล์เพียงครั้งเดียว แล้วแจกสำเนาที่ใช้แคตตาล็อกที่แจงแล้วร่วมกัน

!!! warning "เธรดทำงานจะสืบทอดการผูกหรือไม่ ขึ้นอยู่กับบิลด์"

    `threading.Thread` เปล่า ๆ หรือ `ThreadPoolExecutor.submit`
    เริ่มต้นจากสำเนาของคอนเท็กซ์ของผู้เรียก หรือไม่ก็จากคอนเท็กซ์ว่าง ๆ
    และตัวที่ตัดสินว่าจะเป็นแบบใดคือ `sys.flags.thread_inherit_context` —
    ซึ่งเป็นจริงโดยปริยายบนบิลด์แบบ free-threaded และเป็นเท็จในที่อื่นทั้งหมด
    โค้ดเดียวกันจึงเรนเดอร์ภาษาที่ผูกไว้บน 3.14t แต่เรนเดอร์แคตตาล็อก
    gettext ที่เป็น global ของโปรเซสบน 3.14
    ให้พาคอนเท็กซ์ติดไปด้วยแทนที่จะพึ่งค่าปริยาย:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    ส่วน `asyncio.to_thread` ทำสิ่งนี้ให้คุณอยู่แล้ว

## ค่าที่รู้จักโลแคล { #locale-aware-values }

ไลบรารีนี้ตัดสินว่าค่าจะไปปรากฏ *ตรงไหน* ในข้อความที่แปลแล้ว
มันไม่ได้แปลงค่าตัวนั้นให้เข้ากับท้องถิ่น `{amount:,.2f}` คือ format spec
ของ Python ที่มีพฤติกรรมตายตัว — จุลภาคทุกสามหลักและจุดก่อนทศนิยม —
และมันผลิตอักขระชุดเดิมไม่ว่าข้อความจะอยู่ในภาษาใด:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

ภาษาเยอรมันเขียนตัวเลขนั้นว่า `1.234,50` ภาษาฝรั่งเศสเขียน `1 234,50`
และภาษาฮินดีจัดกลุ่ม `1234567` เป็น `12,34,567` ไม่ใช่ `1,234,567`
ตัวเลข สกุลเงิน วันที่ เวลา และหน่วยวัดเป็นงานของ [Babel][babel-numbers]
จงจัดรูปแบบค่าก่อน แล้วค่อยวางสตริงที่เสร็จแล้วลงไป:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

สำหรับข้อความที่มีการนับ ตัวเลขทำงานสองอย่าง — มันเลือกรูปพหูพจน์
และมันปรากฏอยู่ในตัวข้อความ — และมีเพียงอย่างที่สองเท่านั้นที่ถูกแปลงตามท้องถิ่น
จงเก็บจำนวนดิบไว้สำหรับการเลือก และส่งสตริงที่จัดรูปแบบแล้วไปแสดงผล:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

การจัดรูปแบบก่อนถึงจุดเรียกใช้ยังเป็นสิ่งที่กัน format spec ไม่ให้เข้าไปในแคตตาล็อกด้วย
สิ่งที่นักแปลเห็นคือข้อความชิ้นที่เสร็จแล้ว ไม่ใช่ตัวเลขบวกกับคำสั่งวิธีเรนเดอร์มัน

## เมื่อแคตตาล็อกผิดพลาดจะเกิดอะไรขึ้น { #what-happens-when-a-catalog-is-wrong }

หากตัวยึดตำแหน่งของคำแปลไม่ตรงกับข้อความต้นทาง — ฟิลด์ที่หายไป ไม่รู้จัก
หรือถูกเปลี่ยนรูปแบบ ซึ่งหลุดรอดการตรวจสอบมาจาก MO ที่แก้ด้วยมือ
แคตตาล็อกจากผู้ขาย หรือไปป์ไลน์ที่ข้ามตัวตรวจ — พฤติกรรมเริ่มต้นคือ
การเรนเดอร์ข้อความต้นทางแทนที่จะโยนข้อยกเว้น ซึ่งสอดคล้องกับสัญญาของ gettext
เองที่ว่าแคตตาล็อกที่เสียต้องไม่ทำให้แอปพลิเคชันพัง

เมื่อ `Hello {name}` ถูกแปลเป็น `こんにちは {nombre}` การเรนเดอร์จะสำเร็จ
และมีคำเตือนหนึ่งรายการส่งไปยัง logger `gettext_tstrings`

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

คำเตือนเกิดขึ้นครั้งเดียวต่อคู่ของข้อความและแพตเทิร์น ไม่ใช่ทุกครั้งที่เรนเดอร์
รายการแคตตาล็อกที่เสียจึงไม่ท่วมล็อก

สำหรับการทดสอบและ CI คุณเลือกให้ล้มเหลวแบบชัดเจนได้

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

การค้นหาเดียวกันจะโยนข้อยกเว้นแทน โดยพาประโยคเดียวกันไปด้วย
แต่ไม่มีส่วน "using source text"

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

ข้อความเหล่านี้เขียนขึ้นสำหรับคนที่ลงมือแก้ปัญหาได้ ซึ่งสำหรับปัญหาในแคตตาล็อก
มักเป็นนักแปลมากกว่าโปรแกรมเมอร์ — ดังนั้นเมื่อตัวยึดตำแหน่งดูเหมือนมีอยู่แต่จริง ๆ
แล้วไม่มี ข้อความจะอธิบายเหตุผลแทนที่จะย้ำว่ามันหายไป วงเล็บปีกกาแบบเต็มความกว้าง
การซ้อนเป็น `{{name}}` no-break space ที่มองไม่เห็น อักษรซีริลลิกที่ปนอยู่ในอักษรละติน:
แต่ละกรณีมีถ้อยคำของตัวเอง มีรายการพร้อมตัวอย่างอยู่ใน
[สำหรับนักแปล](translators.md#reading-a-failure-message)
หน้านั้นเขียนขึ้นเพื่อส่งมอบให้คนที่เป็นผู้แก้ไข `.po`

## การเรนเดอร์แพตเทิร์นโดยไม่ใช้แคตตาล็อก { #rendering-a-pattern-without-a-catalog }

`compile_template` เปิดเผยกลไกเดียวกันในระดับที่ต่ำลงหนึ่งขั้น: มันแปลง
t-string เป็น msgid พร้อมชุดค่าที่ผูกไว้ และเรนเดอร์แพตเทิร์นใดก็ตาม
ที่คุณส่งให้

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` ตรวจสอบด้วยกฎเดียวกันและ**โยนข้อยกเว้นเสมอ**เมื่อไม่ตรงกัน
ที่นี่ไม่มีโหมดผ่อนปรน: ความผ่อนปรนมีไว้เพื่อให้การค้นหาใน*แคตตาล็อก*
ถอยกลับไปใช้ข้อความต้นทางได้ แต่แพตเทิร์นที่คุณส่งเข้ามาเอง
ไม่มีอะไรให้ถอยกลับ

## ความปลอดภัยและขอบเขต { #safety-and-scope }

แบบนี้ใช้ได้

```python
tr(t"Hello {name}")
```

แบบเหล่านี้ถูกปฏิเสธโดยตั้งใจ

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

ให้คำนวณค่าที่มีความหมายก่อน

```python
name = user.display_name()
tr(t"Hello {name}")
```

ข้อจำกัดนี้ทำให้ได้คีย์แคตตาล็อกที่เสถียร ให้ชื่อที่มีประโยชน์แก่นักแปล
และป้องกันไม่ให้สตริงที่แปลแล้วกลายเป็นภาษาสำหรับเขียนนิพจน์

การรับประกันจำกัดขอบเขตอยู่ที่*โครงสร้างและการจัดรูปแบบ*: คำแปลไม่มีวัน
ถูกประเมินผล และไม่มีทางเพิ่มการเข้าถึงแอตทริบิวต์ การเรียกฟังก์ชัน
การแปลงค่า หรือ format spec ได้ สองสิ่งยังคงเป็นความรับผิดชอบของผู้เรียก
เช่นเดียวกับ gettext ของไลบรารีมาตรฐานทุกประการ — การ **escape**
ผลลัพธ์ที่เรนเดอร์แล้วให้เหมาะกับปลายทาง (HTML เชลล์ เทอร์มินัล)
และ**ความสมบูรณ์ของแคตตาล็อก** เนื่องจากแคตตาล็อกที่ประสงค์ร้ายสามารถ
ทำซ้ำตัวยึดตำแหน่งเพื่อขยายขนาดผลลัพธ์ได้ ซึ่งเป็นธรรมชาติของ i18n
แบบใช้ตัวยึดตำแหน่งทุกระบบ

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
