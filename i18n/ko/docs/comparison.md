---
description: "% 포맷, .format(), t-string으로 같은 번역 메시지를 작성하고 카탈로그가 제어하는 범위를 비교합니다."
---

# 왜 t-string인가

번역 메시지에 값을 넣는 모든 방식은 같은 질문에 답해야 합니다.
*카탈로그가 포맷 언어를 어디까지 제어해야 하는가?*

## % 포맷

```python
_("Hello %(name)s") % {"name": name}
```

카탈로그에 printf 문법이 들어갑니다. 문자 하나만 빠져도 운영 환경에서
오류가 발생합니다.

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

이름 있는 플레이스홀더라 순서 변경은 쉽습니다. 그러나 `str.format`은
작은 표현식 언어입니다.

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

카탈로그는 여러 플랫폼과 사람을 거치는 데이터지만 `.format()`은 전달한
객체의 속성 접근 권한을 카탈로그에 줍니다.

## t-string

```python
tr(t"Hello {name}")
```

msgid는 계속 `Hello {name}`입니다. 하지만 번역을 포맷 문자열로 실행하지
않고 원본 플레이스홀더와 대조하며 단순 이름만 허용합니다.

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

| | `%(name)s` | `.format()` | `t"…"` |
| --- | --- | --- | --- |
| 이름 있는 플레이스홀더 | 예 | 예 | 예 |
| 번역에서 순서 변경 | 예 | 예 | 예 |
| 문자 하나가 빠지면 실패 | **예** | 아니요 | 아니요 |
| 카탈로그가 포매팅 제어 | 예 | 예 | **아니요** |
| 카탈로그가 속성 접근 | 아니요 | **예** | **아니요** |
| 잘못된 카탈로그가 렌더 중 예외 | **예** | **예** | 기본값은 [아니요](guide.md#what-happens-when-a-catalog-is-wrong) |
| PO/MO와 `msgfmt` 사용 | 예 | 예 | 예 |

## 비용

f-string은 함수가 받기 전에 완성됩니다. t-string([PEP 750]) 때문에
Python 3.14 이상이 필요하며, 각 보간은 단순 이름이어야 합니다.

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

이 제약이 안전성을 만들고 번역자에게 이해하기 쉬운 이름을 제공합니다.

  [PEP 750]: https://peps.python.org/pep-0750/
