---
description: "gettext_tstrings의 모든 공개 이름: 함수, Translator, 컨텍스트 바인딩, 지연 문자열, 오류."
---

# API

아래 이름은 모두 `gettext_tstrings`에서 내보냅니다. 그 밖의 이름은
공개 API가 아닙니다. 이 페이지는 시그니처 레퍼런스입니다. 각 함수의
실제 사용 예는 [가이드](guide.md)를 참고하세요.

## 번역 { #translating }

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

## 컨텍스트 바인딩 { #context-binding }

| 이름 | 역할 |
| --- | --- |
| `use_translations(translations)` | `with` 블록 동안 바인딩하고 종료 후 복원합니다. |
| `set_translations(translations)` | 프레임워크가 관리하는 생명주기에 블록 없이 바인딩합니다. |
| `get_translations()` | 현재 바인딩 또는 `None`을 반환합니다. |

바인딩은 `ContextVar`를 사용해 동시 실행에 안전합니다.

## 지연 문자열 { #deferred-strings }

| 이름 | 역할 |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | 렌더링할 때마다 번역을 미룹니다. |
| `lazy_pgettext(context, template, /, *, strict=False)` | 컨텍스트가 있는 변형입니다. |
| `LazyString` | 둘이 반환하는 것. 그 순간 바인딩된 언어로 `str()`과 `format()`을 통해 렌더링하고, 렌더링된 텍스트와 비교하며, 의도적으로 해시할 수 없습니다. |

`strict`를 정의 시점에 두는 이유를 포함한 실제 예시는
[지연 번역](guide.md#deferred-translation)에 있습니다.

## 저수준 API { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

캐시된 정적 계획을 재사용해 t-string을 컴파일합니다.

### `CompiledTemplate`

| 멤버 | 의미 |
| --- | --- |
| `.msgid` | 안정된 gettext 식별자. |
| `.placeholders` | 처음 등장한 순서의 이름. |
| `.render(pattern)` | 검증 후 렌더링하며, 불일치하면 **항상 예외를 냅니다**. |

## 타입과 오류 { #types-and-errors }

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

## 추출 Entry Point { #extraction-entry-points }

| 그룹 | 이름 | 사용처 |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `babel.cfg`의 `method` |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`이 자동 사용 |

## 성능 { #performance }

무엇이 캐시되는지, 캐시 키가 무엇인지, 측정된 수치가 얼마인지에 대한
전체 설명은 [핫 패스](internals.md#the-hot-path)에 있습니다. 요약하면
검증은 캐시될 뿐 생략되지 않으며, 전체 렌더링 비용은 1마이크로초에
훨씬 못 미칩니다. 자신의 환경에서 직접 벤치마크를 실행해 보세요.

```console
uv run python benchmarks/runtime.py
```
