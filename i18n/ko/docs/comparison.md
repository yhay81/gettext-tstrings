---
description: "% 포맷, .format(), flufl.i18n $ 문자열, t-string으로 같은 번역 메시지를 작성하고 번역자의 실수, 카탈로그의 권한, 도입 비용이라는 세 축으로 비교합니다."
---

# 왜 t-string인가

번역 메시지에 값을 넣는 네 가지 방식을 같은 메시지로 비교합니다. 네 가지
모두 플레이스홀더에 이름을 붙이고 번역자가 순서를 바꿀 수 있게 해 줍니다.
차이는 번역이 잘못되었을 때 무슨 일이 벌어지는지, 카탈로그가 프로그램의
어디까지 손을 뻗을 수 있는지, 그리고 도입에 얼마가 드는지에 있습니다.

표를 먼저 둡니다. 마음에 걸리는 행을 찾아 그 뒤에 있는 절만 읽어도 됩니다.

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

## 나란히 비교 { #side-by-side }

**번역자가 실수했을 때.** 카탈로그는 여러 사람의 손을 거치고, 그 안에서
잘못되는 일의 대부분은 우연입니다.

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 번역이 플레이스홀더를 *생략*하면 — 무엇이 렌더링되는가? | 값이 조용히 사라짐 | 값이 조용히 사라짐 | 값이 조용히 사라짐 | 경고와 함께 원본 메시지([기본 동작](guide.md#what-happens-when-a-catalog-is-wrong)) |
| 번역이 알 수 없는 플레이스홀더를 *추가*하면 — 무엇이 렌더링되는가? | 예외 | 예외 | 플레이스홀더가 텍스트로 그대로 표시됨 | 경고와 함께 원본 메시지([기본 동작](guide.md#what-happens-when-a-catalog-is-wrong)) |
| 번역이 플레이스홀더의 *포맷을 바꾸면* — 무엇이 렌더링되는가? | 카탈로그가 요구한 대로, 타입 문자가 값에 더는 맞지 않으면 예외 | 카탈로그가 요구한 대로 | `$` 문자열에서는 표현할 수 없음 | 경고와 함께 원본 메시지 |
| 렌더링 시점에 플레이스홀더를 검사하는가? | 아니요 | 아니요 | 아니요 | 예(아래 참고) |

**카탈로그가 가진 권한.** 번역은 여러분의 저장소 바깥에서 오는 데이터이며,
각 방식이 그 데이터에 넘겨주는 힘의 크기는 서로 다릅니다.

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 값은 어디서 오는가? | 명시적 매핑 | 명시적 인수 | 호출자의 지역 변수와 전역 변수, 그리고 선택적인 `extras` | t-string 안에서 캡처된 값 |
| 카탈로그가 값의 포맷 방식을 바꿀 수 있는가? | 예 | 예 | 아니요 | 아니요 |
| 카탈로그가 객체 내부에 접근(속성 접근)할 수 있는가? | 아니요 | 예 | 예, 점 표기 이름 사용 | 아니요 |
| "지금의 언어"는 어디에 있는가? | 애플리케이션이 두는 곳 | 애플리케이션이 두는 곳 | 공유되는 애플리케이션 객체 위의 언어 코드 스택 | 태스크나 요청마다의 `ContextVar` |

**도입에 드는 비용.** 도구가 맞기만 하면 위의 모든 것은 공짜입니다. 맞지
않을 수 있는 지점이 여기입니다.

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 최소 Python 버전 | 무관 | 무관 | 3.10 | **3.14** |
| 성숙도 | 표준 라이브러리 | 표준 라이브러리 | 안정 릴리스 | **알파** |
| 일반 PO/MO 카탈로그를 사용하는가? | 예 | 예 | 예 | 예 |
| 사용자 정의 소스 추출기가 필요한가? | 아니요 | 아니요 | 아니요 | 현재는 예 |
| Babel이 추론하는 PO 플래그, 기존 도구의 검증 근거는? | `python-format` | `python-brace-format` | 없음 | `python-brace-format` |

렌더링 시점 검사에 대해: 단수형 메시지는 플레이스홀더가 정확히
일치하는지 검사합니다. 복수형 메시지도 대상 언어의 복수형이 원본과 다를
수 있도록 허용하는 [합집합/교집합 규칙](spec.md)에 따라 검사하며, 더
엄격한 형태별 검사는 카탈로그를 컴파일할 때 실행됩니다([추출](extraction.md)).

포맷 플래그 행은 카탈로그 호환성이 아니라 플레이스홀더를 인식하는 검증에
관한 것입니다. `없음`은 표준 gettext 도구가 여전히 메시지를 읽고 컴파일하지만
`msgfmt --check-format`이 적용할 `$` 플레이스홀더 문법은 없다는 뜻입니다.

## 호환성과 성숙도 { #compatibility-and-maturity }

마지막 표의 첫 두 행은 도입 여부를 가르는 항목이므로, 칸 안에 밀어 넣기보다
분명하게 적어 둘 만합니다.

`%` 포맷과 `.format()`은 Python에 내장되어 있어 의존성이 전혀 필요 없습니다.
[`flufl.i18n`][flufl-i18n]은 이미 릴리스되어 프로덕션에서 쓰이는 성숙한
패키지이며 Python 3.10 이상에서 동작합니다. `gettext-tstrings`는 **알파**이고
**Python 3.14 이상**이 필요합니다. t-string이 3.14의 새 문법이기 때문이며,
백포트는 없고 있을 수도 없습니다. 자리를 잡은 부분은 [명세](spec.md)이고,
Python API는 1.0 전까지 아직 바뀔 수 있습니다.

넷 중 어느 것도 치르지 않는 비용은 카탈로그 호환성입니다. 네 방식 모두 모든
PO 편집기, 번역 플랫폼, GNU gettext 도구가 이미 읽는 평범한 POT/PO/MO 파일을
만들어 내므로, 아래의 선택은 카탈로그 *형식*을 바꾸는 것과 달리 되돌릴 수
있습니다. 기존 프로젝트를 옮기는 이야기는 [마이그레이션](migration.md)에
있습니다.

아래 절들은 각 절충안을 방식별로 하나씩 자세히 보여줍니다.

## % 포맷 { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

잘못될 수 있는 일: 손상된 플레이스홀더는, 카탈로그 검증이 먼저 잡아내지
않는 한 런타임 예외가 됩니다.

카탈로그 문자열에는 printf 문법이 들어가며, 여기에는 놓치기 쉽고
손상되기 쉬운 끝의 타입 문자 — `%(name)s`의 `s` — 도 포함됩니다.

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

PO 편집기의 한 글자 수정이, 카탈로그 검증이 먼저 잡아내지 않는 한 런타임
예외가 됩니다. GNU `msgfmt --check-format`이 이 경우를 잡아내기는 하지만
`python-format` 표시가 있는 메시지에 한하고, 카탈로그가 애플리케이션으로
가는 길에 실제로 msgfmt를 거칠 때만 가능합니다.

## str.format { #strformat }

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

## `$` 문자열과 flufl.i18n { #-strings-and-flufli18n }

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
이 [문서화된 동작][documented behavior]은 호출을 실패시키지 않고 번역 메시지의 나머지를 보존합니다.
다만 속성을 해결하거나 값을 변환하는 도중 발생한 예외는 여전히 전파될 수 있습니다.

한 가지 관련된 면에서 `flufl.i18n`은 기본 `string.Template`보다 기능이
많습니다. [사용자 정의 Template][custom Template]은 `$settings.api_key` 같은 점 표기
플레이스홀더를 허용하며, [translator]는 호출자의 값에서 그 경로를 해결합니다.
번역된 플레이스홀더는 호출자가 사용할 수 있는 어떤 지역 변수나 전역 변수든
지정할 수 있고, 점 문법으로 속성도 따라갈 수 있습니다. 메시지에 속성이 필요할 때
편리하지만 호출자의 프레임도 카탈로그 치환 네임스페이스의 일부가 됩니다.
여기의 비교는 `flufl.i18n` 6.0.0을 설명하며 `string.Template`의 모든 가능한
사용법을 설명하는 것은 아닙니다.

또한 다른 두 포매팅 방식이 애플리케이션에 통째로 맡겨 두는 질문에도
답합니다. *어떤* 언어가 지금의 언어이며 그것을 어떻게 바꾸는가 하는
질문입니다. [애플리케이션 객체][application object]가 언어 스택을
유지하고, `_.push(code)`와 `_.pop()`이 그 스택을 움직이며,
`with _.using(code):`는 중첩되고, [전략][strategy]이 언어 코드에 해당하는
카탈로그를 찾아 주므로 애플리케이션이 카탈로그 객체를 직접 다룰 일은
없습니다. 하나의 작업 단위 안에서 두 가지 이상의 언어로 텍스트를 만들어야
하는 서버 — 읽는 사람에게 보여 줄 페이지와, 계정 설정이 다른 사람에게
보낼 알림 — 이 바로 이 기능이 존재하는 이유입니다.

그 스택은 프로세스 전체가 공유하는 애플리케이션 객체 위에 있습니다.
따라서 겹쳐서 실행되는 두 요청은 하나의 스택을 함께 쓰게 되고, *시간상*
엄밀하게 중첩되지 않는 블록들은 서로에게 잘못된 언어를 넘겨줍니다.

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

이 라이브러리는 같은 기능 — 바인딩이 같은 방식으로 중첩되고 풀립니다 —
을 공유 스택이 아니라 `ContextVar`에 담으므로, 위와 같이 뒤섞여
실행되어도 태스크마다 따로 해결됩니다. 대응하는 예제는
[여러 언어를 동시에](guide.md#several-languages-at-once)에 있습니다.
제공하지 않는 것은 언어 코드로 카탈로그를 찾아 주는 조회입니다. 번역
객체를 직접 전달하며, 흔한 경우에는 `gettext.translation()` 호출 한 번이면
되고, 파싱된 카탈로그는 표준 라이브러리가 캐시합니다.

## t-string { #t-strings }

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
원본 메시지를 렌더링하므로, 잘못된 카탈로그가 애플리케이션을 중단시키는
일은 없습니다 —
[gettext 자신이 지키는 것과 같은 계약](guide.md#what-happens-when-a-catalog-is-wrong)입니다.

포매팅은 작성된 자리, 즉 코드에 남습니다.

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f`는 카탈로그에 도달하지 않으므로 어떤 번역도 이를 바꿀 수 없고,
어떤 번역자도 이를 볼 필요가 없습니다. 다만 이것은 *고정된* 포맷이지
지역화된 포맷이 아닙니다. 언어마다 자릿수와 구분 기호를 고르는 일은
[호출 전에 Babel이 할 몫](guide.md#locale-aware-values)입니다.

도구 지원도 한 가지 차이입니다. t-string은 새 문법이므로 `.pot`으로
추출하려면 현재는 이 패키지가 [Babel용으로 제공](extraction.md)하는 것과
같은 t-string 인식 추출기가 필요합니다.

## 제약이 치르는 비용 { #the-cost-of-the-restriction }

Python 버전 요구 사항을 빼면, 이 모든 것의 대가는 규칙 하나입니다. 보간은
단순 이름이어야 합니다.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

이는 실제 제약이며, 위의 보장을 만들어 내는 바로 그 제약이기도 합니다.
소스 측 값 연결 및 런타임 플레이스홀더 검사와 결합해 카탈로그 문자열이
표현식을 평가하지 못하게 하고, 플레이스홀더 이름을 번역하는 사람에게
의미 있게 유지합니다.

f-string은 이 방법으로 전혀 사용할 수 없습니다. 어떤 라이브러리가 보기 전에
이미 완성된 문자열이므로 이를 번역하면 조각을 번역하게 됩니다. t-string
([PEP 750])은 f-string과 비슷한 문법과 명시적 값 연결을 유지하면서 정적
텍스트와 값을 분리해 둡니다.

Python이 여기까지 온 경위 — 10년 간격의 두 PEP, 그리고 답 없이
닫힌 표준 라이브러리 논의 — 는 [배경](background.md)에서 출처와 함께
다룹니다.

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
