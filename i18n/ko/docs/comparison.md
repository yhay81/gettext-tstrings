---
description: "% 포맷, .format(), flufl.i18n $ 문자열, t-string으로 같은 번역 메시지를 작성하고 각 방식이 값을 연결하고 손상된 카탈로그를 처리하는 방법을 비교합니다."
---

# 왜 t-string인가

번역 메시지에 값을 넣는 네 가지 방식을 같은 문장으로 비교합니다.
요약하면 다음과 같습니다.

- **% 포맷**에서는 번역자가 글자 하나를 지운 것이 프로덕션 충돌이
  됩니다.
- **str.format**에서는 번역이 코드가 전달한 객체의 속성을 — 비밀 값까지
  포함해 — 읽을 수 있습니다.
- **$ 문자열**(flufl.i18n)에서는 값이 호출한 함수의 변수에서 암묵적으로
  당겨지고, 점 표기 플레이스홀더는 속성에도 접근합니다.
- **t-string**에서는 포매팅이 코드에 남고, 번역은 런타임에 검사되며,
  손상된 카탈로그는 충돌 대신 원본 텍스트로 fallback합니다.

이 페이지의 나머지는 그 근거를 방식별로 하나씩 보여줍니다.

!!! note "모든 번역 메시지에는 세 당사자가 관여합니다"

    **카탈로그**는 번역이 담긴 파일입니다. 사람이 편집하는 동안은
    `.po`이고, 애플리케이션이 로드하도록 `.mo`로 컴파일됩니다(둘 다
    [튜토리얼](tutorial.md)에서 다룹니다). 모든 메시지에는 세 당사자가
    관여합니다. **개발자**가 원본 문자열을 작성하고, **번역자**가 —
    대개 코드 리뷰에서 멀리 떨어진 외부 플랫폼에서 — 카탈로그를
    편집하며, **애플리케이션**이 런타임에 둘을 함께 렌더링합니다. 아래의
    각 포매팅 방식은 같은 질문에 서로 다르게 답합니다. *카탈로그가 포맷
    언어를 어디까지 제어해야 하는가?* 예제에서 `_`는 번역 함수의
    관례적인 이름이고 `tr`은 이 라이브러리의 이름입니다.

## % 포맷

```python
_("Hello %(name)s") % {"name": name}
```

잘못될 수 있는 일: 번역에서 글자 하나가 지워지면 렌더링이 충돌합니다.

카탈로그 문자열에는 printf 문법이 들어가며, 여기에는 놓치기 쉽고
손상되기 쉬운 끝의 타입 문자 — `%(name)s`의 `s` — 도 포함됩니다.

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

PO 편집기의 한 글자 수정이 프로덕션의 traceback이 됩니다. GNU
`msgfmt --check-format`이 잡을 수 있지만 `python-format` 표시가 있는
메시지에 한하고, 카탈로그가 애플리케이션으로 가는 길에 실제로 msgfmt를
거칠 때만 가능합니다.

## str.format

```python
_("Hello {name}").format(name=name)
```

끝의 타입 문자를 없애면서 이름이 있고 자유롭게 순서를 바꿀 수 있는
플레이스홀더는 유지합니다. 잘못될 수 있는 일은 교환의 반대편으로
옮겨갑니다. 번역이 여러분의 객체에 대한 권한을 얻습니다.

`str.format`은 작은 표현식 언어이며, 문자열에 이를 호출하면 그 문자열에
이 언어를 사용할 권한을 주게 됩니다.

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

이제 위의 리터럴 문자열을 `_()`가 반환하는 값으로 바꿔 보세요.
`Hello {name}`의 번역이 `{conf.api_key}`로 돌아온다면, 렌더링은 여러분의
API 키를 출력합니다. 무엇을 읽을지 결정한 것은 코드가 아니라
카탈로그입니다. 카탈로그는 코드가 아니지만 데이터처럼 이동합니다. 번역
플랫폼으로 나가고, 여러 사람의 손을 거쳐, `.po`로 돌아와, `.mo`로
컴파일되고, 때로는 프로젝트 바깥에서 통째로 vendoring됩니다.
`.format()`은 그 여정의 모든 단계에 전달한 객체의 속성 접근 권한을
줍니다.

## `$` 문자열과 flufl.i18n

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

표준 라이브러리의 [`string.Template`][stdlib-template]은 `$name` 보간 언어를 제공하지만,
그 자체가 번역 API는 아닙니다. [`flufl.i18n`][flufl-i18n]은 이 형식에 gettext 카탈로그
조회를 결합합니다. 값을 전혀 전달하지 않는다는 점에 주목하세요.
flufl.i18n은 호출자의 전역 변수와 지역 변수로 치환 네임스페이스를
만들므로, 호출 지점에 존재하는 변수라면 무엇이든 메시지에서 사용할 수
있습니다. 선택적인 `extras` 매핑은 둘보다 우선합니다. 번역자가 다루는
문법에는 끝의 타입 문자나 포맷 지정자가 없고 플레이스홀더 순서도
자유롭게 바꿀 수 있습니다.

치환 값을 찾지 못해도 예외가 발생하지 않습니다. `name = "Ada"`이고 호출자의
네임스페이스에 `nombre`가 없다면 카탈로그 번역 `Hello $nombre`는
`Hello $nombre`로 렌더링되어, 해결되지 않은 플레이스홀더가 그대로 보입니다.
이 [문서화된 동작]은 호출을 실패시키지 않고 번역 메시지의 나머지를 보존합니다.
다만 속성을 해결하거나 값을 변환하는 도중 발생한 예외는 여전히 전파될 수 있습니다.

한 가지 관련된 면에서 `flufl.i18n`은 기본 `string.Template`보다 기능이
많습니다. [사용자 정의 Template]은 `$settings.api_key` 같은 점 표기
플레이스홀더를 허용하며, [translator]는 호출자의 값에서 그 경로를 해결합니다.
번역된 플레이스홀더는 호출자가 사용할 수 있는 어떤 지역 변수나 전역 변수든
지정할 수 있고, 점 문법으로 속성도 따라갈 수 있습니다. 메시지에 속성이 필요할 때
편리하지만 호출자의 프레임도 카탈로그 치환 네임스페이스의 일부가 됩니다.
아래 비교는 `flufl.i18n` 6.0.0을 설명하며 `string.Template`의 모든 가능한
사용법을 설명하는 것은 아닙니다.

## t-string

```python
tr(t"Hello {name}")
```

카탈로그에는 계속 `Hello {name}`이 보이며 일반 PO/MO 카탈로그를 그대로
사용합니다. 차이는 번역이 *무엇을 말할 수 있는지*, 그리고 누가 그것을
검사하는지에 있습니다.

이 라이브러리는 렌더링 전에 모든 번역을 원본 메시지의 플레이스홀더와
대조해 검증하며, 단순 이름만 허용하고 그 외에는 아무것도 허용하지
않습니다. `t"Hello {name}"`에 대해서는 다음과 같습니다.

| 번역에 포함된 내용 | 거부 이유 |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

거부가 충돌을 뜻하지는 않습니다. 기본적으로 라이브러리는 경고를 기록하고
원본 텍스트를 렌더링하므로, 잘못된 카탈로그가 애플리케이션을 중단시키는
일은 없습니다 —
[gettext 자신이 지키는 것과 같은 계약](guide.md#what-happens-when-a-catalog-is-wrong)입니다.

포매팅은 작성된 자리, 즉 코드에 남습니다.

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f`는 카탈로그에 도달하지 않으므로 어떤 번역도 이를 바꿀 수 없고,
어떤 번역자도 이를 볼 필요가 없습니다.

도구 지원도 한 가지 차이입니다. t-string은 새 문법이므로 `.pot`으로
추출하려면 현재는 이 패키지가 [Babel용으로 제공](extraction.md)하는 것과
같은 t-string 인식 추출기가 필요합니다.

## 나란히 비교

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 플레이스홀더에 이름이 있는가? | 예 | 예 | 예 | 예 |
| 번역자가 플레이스홀더 순서를 바꿀 수 있는가? | 예 | 예 | 예 | 예 |
| 값은 어디서 오는가? | 명시적 매핑 | 명시적 인수 | 호출자의 지역 변수와 전역 변수, 그리고 선택적인 `extras` | t-string 안에서 캡처된 값 |
| 카탈로그가 값의 포맷 방식을 바꿀 수 있는가? | 예 | 예 | 아니요 | 아니요 |
| 카탈로그가 객체 내부에 접근(속성 접근)할 수 있는가? | 아니요 | 예 | 예, 점 표기 이름 사용 | 아니요 |
| 번역이 플레이스홀더를 *생략*하면 — 무엇이 렌더링되는가? | 값이 조용히 사라짐 | 값이 조용히 사라짐 | 값이 조용히 사라짐 | 경고와 함께 원본 텍스트([기본 동작](guide.md#what-happens-when-a-catalog-is-wrong)) |
| 번역이 알 수 없는 플레이스홀더를 *추가*하면 — 무엇이 렌더링되는가? | 예외 | 예외 | 플레이스홀더가 텍스트로 그대로 표시됨 | 경고와 함께 원본 텍스트([기본 동작](guide.md#what-happens-when-a-catalog-is-wrong)) |
| 렌더링 시점에 플레이스홀더를 검사하는가? | 아니요 | 아니요 | 아니요 | 예(아래 참고) |
| Babel이 추론하는 PO 플래그, 기존 도구의 검증 근거는? | `python-format` | `python-brace-format` | 없음 | `python-brace-format` |
| 일반 PO/MO 카탈로그를 사용하는가? | 예 | 예 | 예 | 예 |
| 사용자 정의 소스 추출기가 필요한가? | 아니요 | 아니요 | 아니요 | 현재는 예 |

렌더링 시점 검사에 대해: 단수형 메시지는 플레이스홀더가 정확히
일치하는지 검사합니다. 복수형 메시지도 대상 언어의 복수형이 원본과 다를
수 있도록 허용하는 [합집합/교집합 규칙](spec.md)에 따라 검사하며, 더
엄격한 형태별 검사는 카탈로그를 컴파일할 때 실행됩니다([추출](extraction.md)).

포맷 플래그 행은 카탈로그 호환성이 아니라 플레이스홀더를 인식하는 검증에
관한 것입니다. `없음`은 표준 gettext 도구가 여전히 메시지를 읽고 컴파일하지만
`msgfmt --check-format`이 적용할 `$` 플레이스홀더 문법은 없다는 뜻입니다.

## 비용

f-string은 이 방법으로 전혀 사용할 수 없습니다. 어떤 라이브러리가 보기 전에
이미 완성된 문자열이므로 이를 번역하면 조각을 번역하게 됩니다. t-string
([PEP 750])은 f-string과 비슷한 문법과 명시적 값 연결을 유지하면서 정적
텍스트와 값을 분리해 둡니다. `$` 문자열은 이미 연결 방식과 실패 모델이 다른
간결한 대안을 제공합니다. `flufl.i18n`은 Python 3.10 이상에서 동작하는
성숙한 패키지입니다. `gettext-tstrings`는 현재 알파 단계이며, t-string이
새 문법이므로 Python 3.14 이상이 필요합니다.

또 다른 비용은 제약 자체입니다. 보간은 단순 이름이어야 합니다.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

이는 실제 제약입니다. 소스 측 값 연결 및 런타임 플레이스홀더 검사와 결합해
카탈로그 문자열이 표현식을 평가하지 못하게 하고 플레이스홀더 이름을 의미 있게
유지합니다.

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [문서화된 동작]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [사용자 정의 Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
