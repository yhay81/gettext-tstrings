---
description: "gettext_tstrings의 모든 공개 이름: 함수, Translator, 컨텍스트 바인딩, 지연 문자열, 오류."
---

# API

아래 이름은 모두 `gettext_tstrings`에서 내보냅니다. 그 밖의 이름은
공개 API가 아닙니다.

## 번역

각 함수는 t-string을 위치 인수로 받고 `translations`와 `strict`를
키워드 인수로 받습니다
([가이드](guide.md#what-happens-when-a-catalog-is-wrong)).

| 함수 | 시그니처 |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | `gettext`의 별칭 |
| `ntr` | `ngettext`의 별칭 |

### `Translator`

번역 객체를 바인딩하는 frozen dataclass입니다.

```python
Translator(translations, strict=False)
```

호출 가능하며(`_(t"…")`) `gettext`, `ngettext`, `pgettext`, `npgettext`,
`tr`, `ntr`을 제공합니다.

## 컨텍스트 바인딩

| 이름 | 역할 |
| --- | --- |
| `use_translations(translations)` | `with` 블록 동안 바인딩하고 종료 후 복원합니다. |
| `set_translations(translations)` | 프레임워크가 관리하는 생명주기에 블록 없이 바인딩합니다. |
| `get_translations()` | 현재 바인딩 또는 `None`을 반환합니다. |

바인딩은 `ContextVar`를 사용해 동시 실행에 안전합니다.

## 지연 문자열

| 이름 | 역할 |
| --- | --- |
| `lazy_gettext(template, /)` | 사용할 때까지 번역을 미룹니다. |
| `lazy_pgettext(context, template, /)` | 컨텍스트가 있는 변형입니다. |
| `LazyString` | `str()`, `format()`, f-string으로 렌더링하고 텍스트와 비교하며 의도적으로 해시할 수 없습니다. |

## 저수준 API

### `compile_template(template, /) -> CompiledTemplate`

캐시된 정적 계획을 재사용해 t-string을 컴파일합니다.

### `CompiledTemplate`

| 멤버 | 의미 |
| --- | --- |
| `.msgid` | 안정된 gettext 식별자. |
| `.placeholders` | 처음 등장한 순서의 이름. |
| `.render(pattern)` | 검증 후 렌더링하며, 불일치하면 **항상 예외를 냅니다**. |

## 타입과 오류

### `Translations`

표준 네 메서드를 나타내는 `runtime_checkable` `Protocol`입니다.

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations`, Babel의 `Translations`가
이 프로토콜을 만족합니다.

### 예외

| 클래스 | 발생 조건 |
| --- | --- |
| `TStringError` | 기본 클래스. |
| `InvalidTemplateError` | 원본 t-string이 규약을 위반합니다. |
| `InvalidTranslationError` | 번역이 규약을 위반합니다. 완화 모드는 기록 후 원본을 렌더링합니다. |

## 추출 Entry Point

| 그룹 | 이름 | 사용처 |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `babel.cfg`의 `method` |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`이 자동 사용 |

## 성능

Apple Silicon에서 필드 하나인 메시지는 t-string 생성까지 약 0.4 µs로,
`gettext(...).format(...)`의 약 2.5배입니다. 캐시는 크기가 제한되고 보간
값을 보관하지 않습니다.

```console
uv run python benchmarks/runtime.py
```
