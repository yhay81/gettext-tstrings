---
description: "API รันไทม์: การผูกแคตตาล็อก ภาษาแบบต่อคำขอ สตริงแบบเลื่อนเวลา และวิธีรายงานคำแปลที่เสียหาย"
---

# คู่มือ

หน้านี้คือเอกสารอ้างอิงฝั่งรันไทม์ ครอบคลุมทุกสิ่งที่ *โค้ดแอปพลิเคชัน* ของคุณ
ทำกับไลบรารีนี้เมื่อมีแคตตาล็อกพร้อมแล้ว หากคุณยังไม่เคยเห็นลูปทั้งหมด —
มาร์ก สกัด แปล คอมไพล์ รัน — [บทแนะนำ](tutorial.md) จะพาเดินครบหนึ่งรอบ
ในห้านาที การสร้างและตรวจสอบแคตตาล็อกอธิบายไว้ใน
[การสกัดข้อความ](extraction.md) ส่วนวิธีที่ทีมทำให้ลูปหมุนต่อไป —
รอบการอัปเดต CI แพลตฟอร์มการแปล — อยู่ใน [การใช้งานจริง](workflow.md)

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

## เมื่อแคตตาล็อกผิดพลาดจะเกิดอะไรขึ้น { #what-happens-when-a-catalog-is-wrong }

หากตัวยึดตำแหน่งของคำแปลไม่ตรงกับข้อความต้นทาง — ฟิลด์ที่หายไป ไม่รู้จัก
หรือถูกเปลี่ยนรูปแบบ ซึ่งหลุดรอดการตรวจสอบมาจาก MO ที่แก้ด้วยมือ
แคตตาล็อกจากผู้ขาย หรือไปป์ไลน์ที่ข้ามตัวตรวจ — พฤติกรรมเริ่มต้นคือ
การคืนข้อความต้นทางแทนที่จะโยนข้อยกเว้น ซึ่งสอดคล้องกับสัญญาของ gettext
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

## การอ่านข้อความแจ้งข้อผิดพลาด { #reading-a-failure-message }

ข้อความเหล่านี้เขียนขึ้นสำหรับคนที่ลงมือแก้ปัญหาได้ ซึ่งสำหรับปัญหาในแคตตาล็อก
มักเป็นนักแปลมากกว่าโปรแกรมเมอร์ การรายงานเพียงว่า `{name}` หายไปเป็นทางตัน
ในเมื่อผู้อ่านมองเห็นอักขระเหล่านั้นอยู่ตรงหน้า ดังนั้นเมื่อตัวยึดตำแหน่งดูเหมือน
มีอยู่แต่จริง ๆ แล้วไม่มี ข้อความจะบอกเหตุผลด้วย เทียบกับข้อความต้นทาง
`Hello {name}` แต่ละกรณีต่อไปนี้จะถูกรายงานภายใต้
`translation does not match the source placeholders:`

| คำแปลที่เขียน | เหตุผลที่รายงาน |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

อักขระที่มองไม่เห็นได้รับการปฏิบัติแยกต่างหาก no-break space ภายใน
วงเล็บปีกกาเป็นสิ่งที่ input method สร้างขึ้นได้และไม่มีอีดิเตอร์ใดแสดงให้เห็น
ข้อความจึงพิมพ์มันเป็น code point แทนที่จะเรียกชื่ออักขระที่ผู้อ่านหาไม่พบ

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

ชื่อที่ตัวอักษรผสมกันหลายระบบการเขียน — กรณี homoglyph ที่อักษรซีริลลิก `а`
แยกไม่ออกจากอักษรละติน — จะถูกแสดงสองครั้ง ครั้งหนึ่งแบบอ่านได้และอีกครั้ง
แบบ escape ซึ่งเป็นรูปเดียวที่บอกความแตกต่างของทั้งสองได้

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

การแยกแยะแบบเดียวกันนี้ใช้กับกรณีที่ชื่อซึ่งเขียนด้วยอักษรกรีกหรือซีริลลิกล้วน
ชนกับชื่อต้นทางแบบ ASCII รวมถึงกรณีอักษรตัวเดียวอย่างละติน `a` กับซีริลลิก `а`

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
