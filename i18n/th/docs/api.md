---
description: "ทุกชื่อที่ gettext_tstrings ส่งออก: ฟังก์ชัน Translator การผูกกับคอนเท็กซ์ สตริงแบบเลื่อนเวลา และข้อผิดพลาด"
---

# API

ทุกอย่างด้านล่างนี้ถูกส่งออกจาก `gettext_tstrings` นอกเหนือจากนี้ไม่มีสิ่งใด
เป็นสาธารณะ หน้านี้คือเอกสารอ้างอิงลายเซ็นฟังก์ชัน สำหรับตัวอย่างการใช้งาน
ของแต่ละฟังก์ชัน ดูที่[คู่มือ](guide.md)

## การแปล { #translating }

แต่ละฟังก์ชันรับ t-string เป็นอาร์กิวเมนต์ตามตำแหน่ง และรับคีย์เวิร์ด
อาร์กิวเมนต์สองตัว: `translations` (ถอยกลับไปใช้การผูกในคอนเท็กซ์
แล้วจึงไปที่ฟังก์ชัน global ของไลบรารีมาตรฐาน) และ `strict`
(ดู[คู่มือ](guide.md#what-happens-when-a-catalog-is-wrong))

| ฟังก์ชัน | ลายเซ็น |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | alias ของ `gettext` |
| `ntr` | alias ของ `ngettext` |

### `Translator`

dataclass แบบ frozen ที่ผูกอ็อบเจกต์การแปลไว้หนึ่งตัว
จุดที่เรียกใช้จึงไม่ต้องส่งมันซ้ำ

```python
Translator(translations, strict=False)
```

มันเรียกได้ (`_(t"…")`) และมี `gettext`, `ngettext`, `pgettext`,
`npgettext` พร้อมด้วย alias `tr` / `ntr`

## การผูกกับคอนเท็กซ์ { #context-binding }

| ชื่อ | จุดประสงค์ |
| --- | --- |
| `use_translations(translations)` | ผูกไว้ตลอดช่วงของบล็อก `with` แล้วคืนค่าเดิม |
| `set_translations(translations)` | ผูกโดยไม่ใช้บล็อก สำหรับวงจรชีวิตที่เฟรมเวิร์กจัดการเอง |
| `get_translations()` | อ่านการผูกปัจจุบัน หรือ `None` |

การผูกใช้ `ContextVar` จึงแยกตามคอนเท็กซ์และปลอดภัยภายใต้การทำงานพร้อมกัน

## สตริงแบบเลื่อนเวลา { #deferred-strings }

| ชื่อ | จุดประสงค์ |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | เลื่อนการแปลออกไปจนถึงการใช้ครั้งแรก |
| `lazy_pgettext(context, template, /, *, strict=False)` | รูปแบบที่มีคอนเท็กซ์ |
| `LazyString` | สิ่งที่ทั้งสองฟังก์ชันคืนค่า เรนเดอร์ผ่าน `str()` และ `format()` เปรียบเทียบเท่ากับข้อความของมัน และแฮชไม่ได้โดยตั้งใจ |

## ระดับล่าง { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

คอมไพล์ t-string โดยนำแผนสถิตที่แคชไว้กลับมาใช้ซ้ำ

### `CompiledTemplate`

| สมาชิก | ความหมาย |
| --- | --- |
| `.msgid` | ตัวระบุข้อความ gettext ที่เสถียร |
| `.placeholders` | ชื่อตัวยึดตำแหน่งเรียงตามลำดับการปรากฏครั้งแรก |
| `.render(pattern)` | ตรวจสอบแพตเทิร์นหนึ่งชุดแล้วเรนเดอร์ **โยนข้อยกเว้นเสมอ**เมื่อไม่ตรงกัน |

## ชนิดข้อมูลและข้อผิดพลาด { #types-and-errors }

### `Translations`

`Protocol` แบบ `runtime_checkable` สำหรับสี่เมธอดมาตรฐาน
ทั้งหมดเป็น positional-only

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` และ `Translations`
ของ Babel ล้วนผ่านเงื่อนไขนี้ทั้งหมด

### ข้อยกเว้น

| คลาส | ถูกโยนเมื่อ |
| --- | --- |
| `TStringError` | คลาสฐานของทั้งสองคลาสด้านล่าง |
| `InvalidTemplateError` | t-string **ต้นทาง**ละเมิดข้อตกลง — การแทรกค่าที่ซับซ้อน หรือชื่อซ้ำที่จัดรูปแบบต่างกัน |
| `InvalidTranslationError` | **คำแปล**ละเมิดข้อตกลง ภายใต้โหมดผ่อนปรนซึ่งเป็นค่าเริ่มต้น กรณีนี้จะถูกบันทึกลงล็อกและเรนเดอร์ข้อความต้นทางแทน |

## จุดเชื่อมต่อการสกัดข้อความ { #extraction-entry-points }

ถูกลงทะเบียนโดยอัตโนมัติเมื่อติดตั้ง คุณอ้างถึงมันด้วยชื่อ ไม่ใช่ด้วยการ import

| กลุ่ม | ชื่อ | ใช้โดย |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | ค่า `method` ใน `babel.cfg` |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile` โดยอัตโนมัติ |

## ประสิทธิภาพ { #performance }

รายละเอียดฉบับเต็ม — อะไรถูกแคช แคชใช้อะไรเป็นคีย์ และตัวเลขที่วัดได้ —
อยู่ที่[เส้นทางร้อน](internals.md#the-hot-path) ฉบับย่อคือ: การตรวจสอบ
ถูกแคชไว้ ไม่มีการข้าม และการเรนเดอร์ทั้งหมดมีต้นทุนเพียงเสี้ยวหนึ่งของ
ไมโครวินาที รันเบนช์มาร์กบนเครื่องเป้าหมายของคุณเองได้

```console
uv run python benchmarks/runtime.py
```
