---
description: "การสกัดข้อความ t-string ด้วย pybabel และวิธีที่ msgfmt กับตัวตรวจ Babel ที่มาพร้อมแพ็กเกจตรวจสอบแคตตาล็อก"
---

# การสกัดข้อความ

การสกัดข้อความคือขั้นตอนที่รวบรวมข้อความที่ถูกมาร์กไว้ทุกรายการออกจาก
ซอร์สโค้ดของคุณลงในเทมเพลต `.pot` สำหรับนักแปล — ขั้นตอนที่ 3 ของลูปใน
[บทแนะนำ](tutorial.md) หน้านี้คือเอกสารอ้างอิงของขั้นตอนนั้น: การตั้งค่า
ชื่อฟังก์ชันแบบกำหนดเอง โหมด strict สำหรับ CI และการตรวจสอบที่คอย
คุ้มครองแคตตาล็อกของคุณหลังจากนั้น

การสกัดข้อความต้องการ extra `babel`

```console
python -m pip install "gettext-tstrings[babel]"
```

## ขั้นตอนการทำงาน { #the-workflow }

สร้าง `babel.cfg`

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

จากนั้นใช้คำสั่ง Babel ตามปกติ

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` รันเพียงครั้งเดียวต่อภาษา หลังจากนั้น `pybabel update` จะพับเทมเพลตใหม่
แต่ละชุดเข้ากับแคตตาล็อกที่มีอยู่ วงรอบที่เกิดซ้ำนี้ — และความหมายของรายการ
`fuzzy` ต่อการออกรุ่น — เดินให้ดูทีละขั้นใน
[การใช้งานจริง](workflow.md#the-cycle-after-the-first-translation)

ตัวสกัด `gettext_tstrings` ยังจัดการการเรียก `_()`, `gettext()` และ
`ngettext()` แบบธรรมดาด้วย mapping เดียวจึงครอบคลุมโค้ดเบสแบบผสมได้
มันรู้จัก `_()` ชื่อ gettext มาตรฐานทั้งสี่ alias `tr()` / `ntr()`
และ `lazy_gettext()` / `lazy_pgettext()` แบบเลื่อนเวลา

!!! warning "เปิดใช้คอมเมนต์สำหรับนักแปลด้วย `-c`"

    `pybabel extract` จะรวบรวมคอมเมนต์สำหรับนักแปลก็ต่อเมื่อคุณส่ง
    `-c "Translators:"` เท่านั้น เช่นเดียวกับที่ทำกับการเรียก gettext
    แบบธรรมดา ถ้าละไว้ การสกัดก็ยังทำงานได้ เพียงแต่คอมเมนต์เหล่านั้น
    จะไม่มีวันไปถึงแคตตาล็อก ซึ่งเป็นที่ที่มันคือ[คันโยกด้านคุณภาพที่ราคาถูกที่สุด](workflow.md#working-with-translators-and-platforms)
    ในเวิร์กโฟลว์ทั้งหมด

## การลงทะเบียนชื่อฟังก์ชันของคุณเอง { #registering-your-own-function-names }

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

ไฟล์ ini ให้ค่าเป็นสตริงเดียว mapping แบบ TOML ให้เป็นลิสต์
และภายในสตริงจะคั่นชื่อด้วยช่องว่างหรือจุลภาคก็ได้
การเขียนทั้งสี่แบบใช้ได้ทั้งหมด

ตัวเลือกที่มีคือ `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` และ `npgettext_functions`

!!! danger "`-k` ไปไม่ถึง t-string"

    ตัวช่วยแบบกำหนดเองอย่าง `mytr(t"…")` ต้องถูกระบุชื่อไว้ในตัวเลือกข้างต้น
    ตัวใดตัวหนึ่ง กลไก `--keyword` ของ Babel อ่าน t-string literal ไม่ได้
    ดังนั้น `pybabel extract -k mytr` จึงไม่พบสิ่งใดและไม่แจ้งสิ่งใด —
    ข้อความก็แค่หายไปจาก POT เฉย ๆ ส่วน `-k` ยังใช้ได้ตามปกติกับการเรียก
    gettext ธรรมดาที่ถูกสกัดควบคู่กัน

    รองรับเฉพาะลำดับอาร์กิวเมนต์มาตรฐานเท่านั้น: ข้อความมาก่อน
    คอนเท็กซ์แล้วตามด้วยข้อความสำหรับ `pgettext` และคอนเท็กซ์ เอกพจน์
    แล้วพหูพจน์สำหรับ `npgettext`

## ผ่อนปรนบนเครื่อง เข้มงวดใน CI { #lenient-locally-strict-in-ci }

โดยค่าเริ่มต้น ไฟล์เสียหนึ่งไฟล์ไม่ทำให้การรันทั้งหมดจบลง

- t-string ที่ตัวสกัดปฏิเสธ — การเข้าถึงแอตทริบิวต์ นิพจน์
  อาร์กิวเมนต์ที่ผิด — จะถูกรายงานเป็นคำเตือนแล้วข้ามไป
- ไฟล์ที่ parse ไม่ได้จะถูกข้ามด้วยวิธีเดียวกัน
- เช่นเดียวกับไฟล์ที่มีเพียง `tokenize` ปฏิเสธในขณะที่ `ast` ยอมรับ
  ซึ่งรอบการทำงานของ Babel เองจะยกเลิกกลางคันหากเจอ

นั่นสะดวกในระหว่างที่คุณกำลังแก้ไขอยู่ และอันตรายเมื่อคุณไม่ได้อยู่:
ข้อความที่ถูกข้ามไปจะ **ไม่ปรากฏใน POT** เลย มันจึงไม่มีวันถูกแปล
และไม่มีอะไรบอกคุณเรื่องนั้น จงตั้ง `strict = true` ในตัวเลือกของ mapping
ทุกที่ที่การสกัดไม่มีมนุษย์คอยเฝ้าดู:

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

จากนั้นคำเตือนทุกข้อข้างต้นจะกลายเป็นความล้มเหลวแบบเด็ดขาด
จงถือว่านี่คือค่าตั้งสำหรับการใช้งานจริง และค่าเริ่มต้นคือค่าตั้งสำหรับบนเครื่องของคุณ

## Toolchain ที่คุณใช้อยู่ตรวจสอบแคตตาล็อกเหล่านี้ได้ { #your-existing-toolchain-validates-these-catalogs }

Babel ติดแฟล็กมาตรฐานให้ทุกข้อความที่สกัดออกมา และบรรทัดเดียวนั้นคือสิ่งที่
เปิดใช้การตรวจตัวยึดตำแหน่งในเครื่องมือที่คุณรันอยู่แล้ว

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

แปลข้อความนี้เป็น `こんにちは {nombre}` แล้วความผิดพลาดจะถูกจับได้
โดยไม่ต้องตั้งค่าใด ๆ เพิ่ม

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate จัดทำเอกสารการตรวจแบบเดียวกันในชื่อ
[Python brace format][weblate-checks] และแพลตฟอร์มเชิงพาณิชย์ต่างก็มี QA
ตัวยึดตำแหน่งของตนเองที่อิงแฟล็กเดียวกัน พฤติกรรมเหล่านั้นเป็นของแต่ละเจ้า
เครื่องมือสองตัวด้านล่างคือสิ่งที่ตรวจสอบยืนยันไว้ที่นี่

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

นอกเหนือจากนั้น แพ็กเกจนี้ลงทะเบียน **checker** ของ Babel ไว้ด้วย
`pybabel compile` จึงใช้กฎของข้อกำหนดกับทุกข้อความที่มีคอมเมนต์เครื่องหมาย
`gettext-tstrings`

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

สำหรับข้อความพหูพจน์ ตัวชี้จะระบุชื่อรูปด้วย เพราะหมายเลขบรรทัดที่ Babel
รายงานคือบรรทัดของ msgid และบล็อกภาษารัสเซียมี `msgstr` สามรายการอยู่ใต้มัน

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` ยังคงเขียนไฟล์ `.mo` อยู่ดี"

    ข้อผิดพลาดข้างต้นถูกรายงาน สถานะทางออกคือ `1` — แต่แคตตาล็อกที่เสีย
    ก็ยังถูกคอมไพล์อยู่ดี มีเพียงสถานะทางออกนั้นเท่านั้นที่หยุดไปป์ไลน์
    ไม่ให้ส่งมันออกไปได้ [สิ่งที่ CI ป้องกัน](workflow.md#what-ci-gates)
    แสดงขั้นตอนบิลด์ที่ทำให้มันทำงาน

การตรวจทั้งสองไม่ซ้ำซ้อนกัน ตัวตรวจของแพ็กเกจนี้เข้มงวดกว่าอย่างน้อยสองกรณี

- msgid ที่วงเล็บปีกกาทั้งหมดถูก escape (`Config {{raw}} only`)
  จะไม่ได้รับแฟล็ก `python-brace-format` เลย เครื่องมือภายนอกจึงไม่ตรวจสอบ
  มันเลยแม้แต่น้อย
- รูปพหูพจน์ถูกตรวจทีละรูป `msgfmt --check-format` อ่านไฟล์ข้างต้น
  แล้วออกด้วยสถานะ `0` รูปที่ทิ้งตัวยึดตำแหน่งซึ่งรูปพี่น้องยังเก็บไว้
  จะผ่านที่นั่นแต่ถูกปฏิเสธที่นี่

`msgfmt` ตรวจเฉพาะชื่อตัวยึดตำแหน่งที่มัน parse เป็น Python brace format
ได้เท่านั้น การใช้ชื่อ ASCII จึงทำให้ทุกเครื่องมือในสายโซ่ยังตรวจสอบข้อความได้
ตัวไลบรารีเองยอมรับชื่อใดก็ได้ที่ผ่าน `str.isidentifier()`

## เทมเพลตและเครื่องมืออื่น ๆ { #templates-and-other-tools }

t-string เป็นไวยากรณ์ของ Python ไลบรารีนี้จึงครอบคลุมซอร์ส Python
ภาษาเทมเพลตยังคงใช้ i18n ของตนเอง — `{% trans %}` ของ Jinja2,
template tag ของ Django — และตัวสกัดของ Babel สำหรับภาษาเหล่านั้น
ทุกอย่างป้อนเข้าสู่แคตตาล็อก PO เดียวกัน เวิร์กโฟลว์การแปลเดียวจึงยัง
ครอบคลุมโค้ดเบสแบบผสมได้

`pygettext` ในปัจจุบัน parse t-string ไม่ได้ นี่คือเหตุผลที่การสกัดข้อความ
ทำผ่าน Babel ข้อตกลงนี้ถูกบันทึกไว้เป็นลายลักษณ์อักษรใน[ข้อกำหนด](spec.md)
เพื่อให้ตัวสกัดอื่น หรือ `pygettext` ในอนาคต นำไปรองรับได้
