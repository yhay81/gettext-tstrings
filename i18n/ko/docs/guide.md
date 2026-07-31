---
description: "런타임 API: 카탈로그 바인딩, 요청별 언어, 지연 문자열, 잘못된 번역 처리."
---

# 가이드

이 페이지는 런타임 레퍼런스입니다. 카탈로그가 준비된 뒤 *애플리케이션
코드*가 이 라이브러리로 하는 모든 일을 다룹니다. 표시, 추출, 번역,
컴파일, 실행이라는 전체 루프를 아직 본 적이 없다면
[튜토리얼](tutorial.md)이 5분 만에 한 바퀴 안내합니다. 카탈로그 생성과
검증은 [추출](extraction.md)에서 다루며, 팀이 루프를 계속 돌리는 방법 —
업데이트 주기, CI, 번역 플랫폼 — 은 [프로덕션에서](workflow.md)가
다룹니다.

## 카탈로그 바인딩 { #binding-a-catalog }

권장 방식은 gettext의 객체 사용법과 같습니다. 표준 번역 객체를 한 번
바인딩하고 호출 가능한 프로세서를 `_`로 사용합니다.

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

모듈 함수는 표준 라이브러리의 이름과 위치 인수를 따릅니다.

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr`, `ntr`은 각각 `gettext`, `ngettext`의 정확한 별칭입니다.

## 요청별 언어 { #per-request-language }

웹 프레임워크는 요청마다 언어를 고릅니다. 번역을 현재 컨텍스트에
바인딩하면 동시 요청에서도 모든 모듈 호출이 각 요청의 언어를 사용합니다.

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

프레임워크가 생명주기를 관리한다면 `set_translations()`로 블록 없이
바인딩하고 `get_translations()`로 읽습니다. 명시한 `translations=`가 항상
우선합니다. 바인딩이 없으면 표준 라이브러리의 전역 gettext 함수가
fallback입니다. Flask와 ASGI 미들웨어의 실전 예제는
[프로덕션에서](workflow.md#binding-a-language-at-runtime) 페이지에
있습니다.

## 지연 번역 { #deferred-translation }

t-string은 값을 즉시 캡처합니다. import 때 정의한 레이블, enum, 상수를
실제 *사용 시점*의 활성 언어로 렌더링하려면 지연 문자열을 사용하세요.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString`은 `str()`, `format()`, f-string으로 렌더링되고 텍스트와
비교됩니다.

!!! note "의도적으로 해시할 수 없음"

    텍스트가 언어에 따라 바뀝니다. 변하는 해시는 set이나 dict를 조용히
    손상시킵니다. 키가 필요하면 먼저 `str()`을 호출하세요.

`strict`는 렌더링되는 곳이 아니라 메시지를 작성하는 곳에서 결정합니다.

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

지연 문자열은 최종적으로 쓰이는 곳 — 템플릿 안, 폼, 로그 한 줄 — 에서
렌더링되는데, 그곳은 지금이 테스트 실행인지 프로덕션인지 알지 못하는
경우가 대부분입니다. 정의 시점에 `strict=True`를 넘기는 것이,
호출 지점에서 렌더링되지 않는 문자열에도
[CI에서는 시끄럽게, 프로덕션에서는 관대하게](#what-happens-when-a-catalog-is-wrong)라는
같은 선택을 적용할 수 있게 해 줍니다.

복수형은 런타임의 수에 의존하므로 `ngettext`로 즉시 렌더링합니다.

## 여러 언어를 동시에 { #several-languages-at-once }

한 요청에 두 가지 이상의 언어가 필요한 경우는 흔합니다. 읽는 사람에게
보여 줄 페이지를 렌더링하면서 다른 언어로 설정된 계정에 보낼 알림을 큐에
넣거나, 참가자마다 각자의 언어로 인용하는 요약을 만드는 경우입니다.
바인딩은 중첩되며, 안쪽 블록을 빠져나오면 바깥쪽 바인딩이 복원됩니다.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

수신자 목록을 도는 자리에서는 지연 문자열이 그 일을 대신합니다. 메시지는
import 시점에 한 번만 작성되고, 언어마다 한 번씩 렌더링됩니다.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

바인딩은 공유 객체에 매달린 스택이 아니라 `ContextVar`이므로, 겹쳐서
실행되는 요청이 서로의 언어를 집어 올 수 없습니다. 들어간 순서 그대로
블록을 *빠져나오는* 경우 — 푸시다운 스택이 틀리게 처리하는 바로 그
뒤섞임 — 까지 포함해서 그렇습니다. 언어마다 카탈로그를 로드하는 비용은
저렴합니다. `gettext.translation()`은 각 `.mo`를 한 번만 파싱하고, 파싱된
카탈로그를 공유하는 복사본을 건네줍니다.

!!! warning "워커 스레드가 바인딩을 물려받는지는 빌드에 달려 있습니다"

    맨 `threading.Thread`나 `ThreadPoolExecutor.submit`은 호출자 컨텍스트의
    복사본에서 시작하거나 빈 컨텍스트에서 시작하며, 둘 중 어느 쪽인지는
    `sys.flags.thread_inherit_context`가 정합니다 — 프리스레드 빌드에서는
    기본값이 참이고, 그 밖의 모든 빌드에서는 거짓입니다. 그래서 같은
    코드가 3.14t에서는 바인딩된 언어를, 3.14에서는 프로세스 전역
    카탈로그를 렌더링합니다. 기본값에 기대지 말고 컨텍스트를 넘기세요.

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread`는 이미 이 일을 대신해 줍니다.

## 카탈로그가 잘못되었을 때 { #what-happens-when-a-catalog-is-wrong }

번역의 플레이스홀더가 원본과 맞지 않으면 기본 모드는 예외 대신 원본
텍스트를 렌더링합니다. 잘못된 카탈로그가 애플리케이션을 중단하지 않아야
한다는 gettext의 계약을 따릅니다.

`Hello {name}`의 번역이 `こんにちは {nombre}`라면 렌더링은 성공하고
`gettext_tstrings` 로거에 다음 경고가 기록됩니다.

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

경고는 렌더링마다가 아니라 메시지와 패턴마다 한 번만 기록되므로,
손상된 카탈로그 항목이 로그를 넘치게 하지 않습니다. 테스트와 CI에서는 strict
모드를 켜세요.

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

그러면 같은 조회가 예외를 냅니다.

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## 오류 메시지 읽기 { #reading-a-failure-message }

메시지는 눈에 보이는 플레이스홀더가 왜 유효하지 않은지도 설명합니다.

| 번역에 포함된 내용 | 이유 |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

보이지 않는 줄 바꿈 없는 공백은 코드 포인트로 표시됩니다.

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

다른 문자 체계의 동형 문자는 읽을 수 있는 형태와 이스케이프를 함께
표시합니다.

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

그리스어 또는 키릴 문자로만 된 이름과 ASCII 이름의 충돌도 같은 방식으로
처리합니다.

## 카탈로그 없이 패턴 렌더링 { #rendering-a-pattern-without-a-catalog }

`compile_template`은 msgid와 바인딩된 값을 만들고 패턴을 렌더링합니다.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render`는 같은 규칙으로 검증하며 불일치하면 **항상 예외를 냅니다**.
카탈로그 조회가 없으므로 fallback도 없습니다.

## 보안과 범위 { #safety-and-scope }

유효:

```python
tr(t"Hello {name}")
```

의도적으로 거부:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

값을 먼저 명시적으로 계산하세요.

```python
name = user.display_name()
tr(t"Hello {name}")
```

번역은 평가되지 않으며 속성 접근, 호출, 변환, 포맷을 추가할 수 없습니다.
일반 gettext와 마찬가지로 애플리케이션이 출력 대상의 **이스케이프**와
**카탈로그 무결성**을 책임집니다.
