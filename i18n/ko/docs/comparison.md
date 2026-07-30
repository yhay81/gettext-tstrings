---
description: "% 포맷, .format(), flufl.i18n $ 문자열, t-string으로 같은 번역 메시지를 작성하고 각 방식이 값을 연결하고 손상된 카탈로그를 처리하는 방법을 비교합니다."
---

# 왜 t-string인가

번역 메시지에 값을 넣는 모든 방식은 같은 질문에 답해야 합니다.
*카탈로그가 포맷 언어를 어디까지 제어해야 하는가?* 아래 네 가지 답은
값을 어디서 가져오는지와 카탈로그가 플레이스홀더를 바꿀 때 어떤 일이
일어나는지도 서로 다릅니다.

## % 포맷

```python
_("Hello %(name)s") % {"name": name}
```

카탈로그 문자열에는 printf 문법이 들어가며, 여기에는 놓치기 쉽고 문자
하나만 바뀌어도 손상될 수 있는 끝의 타입 문자도 포함됩니다.

```pycon
>>> "Hello %(name)" % {"name": "Ada"}
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

`msgfmt --check-format`이 잡을 수 있지만 `python-format` 표시가 있고 실제
빌드가 msgfmt를 통과할 때만 가능합니다.

## str.format

```python
_("Hello {name}").format(name=name)
```

끝의 타입 문자를 없애면서 이름이 있고 자유롭게 순서를 바꿀 수 있는
플레이스홀더는 유지합니다.

문제는 다른 쪽에 있습니다. `str.format`은 작은 표현식 언어이며, 문자열에
이를 호출하면 그 문자열에 이 언어를 사용할 권한을 주게 됩니다.

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

카탈로그는 여러 플랫폼과 사람을 거치는 데이터지만 `.format()`은 전달한
객체의 속성 접근 권한을 카탈로그에 줍니다.

## `$` 문자열과 flufl.i18n

```python
name = "Ada"
_("Hello $name")
```

표준 라이브러리의 [`string.Template`][stdlib-template]은 `$name` 보간 언어를 제공하지만,
그 자체가 번역 API는 아닙니다. [`flufl.i18n`][flufl-i18n]은 이 형식에 gettext 카탈로그
조회를 결합합니다. 호출자의 전역 변수와 지역 변수로 치환 네임스페이스를
만들며, 선택적인 `extras` 매핑은 둘보다 우선합니다. 번역자가 다루는 문법에는
끝의 타입 문자나 포맷 지정자가 없고 플레이스홀더 순서도 자유롭게 바꿀 수 있습니다.

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
사용합니다. 소스 추출은 다릅니다. 현재 도구에는 이 패키지가 제공하는 것과 같은
t-string 인식 추출기가 필요합니다. 번역은 원본 메시지의 플레이스홀더와 대조해
검사하고 이 라이브러리가 렌더링하며, 단순 이름만 허용합니다.

| 번역에 포함된 내용 | 거부 이유 |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

포매팅은 애플리케이션에 남습니다.

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f`는 카탈로그에 도달하지 않습니다.

## 나란히 비교

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 이름 있는 플레이스홀더 | 예 | 예 | 예 | 예 |
| 번역자가 순서 변경 가능 | 예 | 예 | 예 | 예 |
| 값을 가져오는 곳 | 명시적 매핑 | 명시적 인수 | 호출자의 전역 변수와 지역 변수, 선택적인 `extras`가 우선함 | t-string이 캡처한 보간 |
| 카탈로그가 값 변환이나 포맷 지정자 제어 | 예 | 예 | 아니요 | 아니요 |
| 카탈로그가 속성 접근 요청 가능 | 아니요 | 예 | 예, 점 표기 이름 사용 | 아니요 |
| 렌더링할 때 원본 플레이스홀더가 삭제됨 | 조용히 생략 | 조용히 생략 | 조용히 생략 | [기본적으로](guide.md#what-happens-when-a-catalog-is-wrong) 원본 패턴을 완전히 렌더링 |
| 렌더링할 때 추가된 플레이스홀더 값을 찾을 수 없음 | 예외 발생 | 예외 발생 | 그대로 표시 | [기본적으로](guide.md#what-happens-when-a-catalog-is-wrong) 원본 패턴을 완전히 렌더링 |
| 런타임에 원본 플레이스홀더 집합 검사(단수형) | 아니요 | 아니요 | 아니요 | 예 |
| Babel이 예제에서 추론하는 PO 포맷 플래그 | `python-format` | `python-brace-format` | 없음 | `python-brace-format` |
| 일반 PO/MO 카탈로그 사용 | 예 | 예 | 예 | 예 |
| 사용자 정의 소스 추출기 필요 | 아니요 | 아니요 | 아니요 | 현재는 예 |

포맷 플래그 행은 카탈로그 호환성이 아니라 플레이스홀더를 인식하는 검증에
관한 것입니다. `없음`은 표준 gettext 도구가 여전히 메시지를 읽고 컴파일하지만
`msgfmt --check-format`이 적용할 `$` 플레이스홀더 문법은 없다는 뜻입니다.

## 비용

f-string은 이 방법으로 전혀 사용할 수 없습니다. 어떤 라이브러리가 보기 전에
이미 완성된 문자열이므로 이를 번역하면 조각을 번역하게 됩니다. t-string
([PEP 750])은 f-string과 비슷한 문법을 유지하고 값을 명시적으로 연결하면서
이 분리를 제공합니다. `$` 문자열은 이미 연결 방식과 실패 모델이 다른 간결한
대안을 제공합니다. `flufl.i18n`은 현재 릴리스가 Python 3.10을 지원하는 성숙한
패키지입니다. `gettext-tstrings`는 현재 알파 단계이며 네이티브 t-string 때문에
최소 버전은 Python 3.14입니다.

또 다른 비용은 제약 자체입니다. 보간은 단순 이름이어야 합니다.

```python
tr(t"Hello {user.name}")  # rejected
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
