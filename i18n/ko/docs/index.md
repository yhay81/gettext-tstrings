---
description: "값과 포매팅을 카탈로그 밖에 둔 채 gettext와 Babel로 완전한 t-string 메시지를 번역합니다."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Python t-string으로<br>완전한 메시지를 번역합니다

`gettext-tstrings`는 Python 3.14+ t-string을 표준 gettext 카탈로그와 Babel
도구에 연결합니다. 값과 포매팅은 애플리케이션 코드에 남고, 번역자는 완전한
메시지와 단순한 `{name}` 플레이스홀더를 다룹니다.

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

카탈로그에는 `Hello {name}`이 들어갑니다. 번역은 `{name}`의 위치를 바꾸거나
반복할 수 있습니다. 플레이스홀더를 없애거나, 이름을 바꾸거나, 포매팅을
덧붙이면 카탈로그 검증이 오류를 보고합니다. 잘못된 항목이 그럼에도
프로덕션까지 도달하면 라이브러리는 충돌하는 대신 경고를 남기고 원본 메시지를
렌더링합니다.

[5분 튜토리얼 시작하기 :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[대안과 비교하기](comparison.md){ .md-button }

알파 · Python 3.14+ · 표준 PO/MO 카탈로그 · 서드파티 런타임 의존성 없음
{ .home-facts }

이 사이트는 문서화한 내용을 스스로 실천합니다. 내비게이션, 레이블,
복수형을 반영한 빌드 보고서까지 모든 언어판을
[`gettext-tstrings` 자신](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)이
PO 카탈로그에서 렌더링합니다.
{ .home-hero-note }

</div>

## 당신에게 맞을까요? { #is-this-for-you }

**지금 잘 맞는 경우**는 애플리케이션이 Python 3.14 이상에서 동작하고, 이미
gettext와 Babel을 쓰고 있거나 그 PO/MO 작업 흐름을 도입하고 싶으며, 렌더링
전에 검사되는 이름 있는 플레이스홀더를 t-string 문법으로 쓰고 싶을 때입니다.

**아직 맞지 않는 경우**는 Python 3.13 이하가 필요할 때, 안정된 Python API가
필요할 때(이 패키지는 알파이며 자리를 잡은 부분은 [명세](spec.md)입니다),
또는 번역 대상 텍스트가 Python 소스가 아니라 거의 전부 템플릿 언어 안에
있을 때입니다.

이미 카탈로그가 있나요? 그대로 동작합니다.
`_("Hello {name}").format(name=name)`과 `tr(t"Hello {name}")`은 같은 msgid를
만들어 내므로 기존 번역이 전환에서 살아남습니다. 전체 이전 과정은
[마이그레이션](migration.md)이 안내합니다.

## 카탈로그가 말할 수 있는 것 { #what-the-catalog-may-say }

**번역은 자신이 번역하는 메시지의 구조를 바꿀 수 없습니다.** 이것이 약속의
전부이며, 이 사이트의 나머지는 모두 여기서 따라 나옵니다. 번역은 `{name}`의
위치를 바꾸거나 반복할 수 있고, 그 주변의 다른 모든 낱말을 새로 쓸 수
있습니다. 하지만 플레이스홀더를 생략하거나, 새로 만들어 내거나, 그것을 통해
객체 속으로 손을 뻗거나, 자체 포매팅을 붙일 수는 없습니다.

라이브러리는 들어오는 길목에서, 즉 카탈로그를 컴파일할 때 한 번, 그리고
렌더링할 때 다시 한 번 이를 검사합니다. 이것이 리뷰에서 발견되는 실수와
사용자가 발견하는 실수의 차이입니다.

!!! note "gettext가 처음이라면? 네 문장으로 보는 전체 작업 흐름"

    **gettext**는 Python을 비롯해 훨씬 넓은 범위에서 소프트웨어를
    번역하는 표준 방식입니다. 코드가 번역 가능한 메시지를 표시하면,
    *추출기*가 이를 템플릿 파일(`.pot`)로 모으고, 대개 프로그래머가 아닌
    번역자가 언어마다 하나씩 카탈로그 파일(`.po`)을 채우며, 이는
    애플리케이션이 런타임에 로드하는 바이너리 `.mo`로 컴파일됩니다.
    번역 함수의 관례적인 이름은 `_`이므로 `_(t"Hello {name}")`은
    "이 메시지를 번역하라"로 읽힙니다. **[튜토리얼](tutorial.md)**은
    표시, 추출, 번역, 컴파일, 실행이라는 전체 경로를 약 5분 만에
    안내합니다.

## 해결하는 문제 { #the-problem-it-solves }

f-string은 라이브러리가 받기 전에 이미 보간되어 있습니다.
`f"Hello {name}"`은 이미 `"Hello Ada"`가 되었고, 값 주변의 조각을
번역하면 대부분 언어의 문법이 깨집니다. t-string([PEP 750])은 정적
텍스트, 평가된 값, 원본 식, 변환, 포맷 명세를 분리해 보존합니다. 메시지
카탈로그에 정확히 필요한 구조입니다. `%(name)s`, `.format()`,
`$` 문자열과의 차이는 [비교 페이지](comparison.md)에서 확인할 수
있습니다.

gettext와 Babel은 t-string을 메시지로 바꾸는 규칙까지 정하지 않습니다.
이 라이브러리는 그 규칙을 [버전이 있는 명세](spec.md)로 정의하고
[적합성 테스트 모음](spec.md#conformance)을 제공합니다.

## 설계 규칙 { #the-design-rules }

- 문장 조각이 아닌 완전한 메시지를 번역합니다.
- `{name}` 같은 단순 변수 이름만 허용합니다.
- `!r`, `:.2f`는 애플리케이션이 관리하고 카탈로그에는 넣지 않습니다.
- 번역이 알려진 플레이스홀더의 순서를 바꾸고 반복하는 것은 허용하되,
  속성에 접근하거나 포매팅을 추가하는 것은 막습니다.
- 기존 POT, PO, MO 파일과 그것을 이미 읽는 도구를 그대로 사용합니다.

그리고 의도적으로 손대지 않는 것의 목록도 있습니다. 숫자, 통화, 날짜는
지역화하지 않으므로 [먼저 포매팅하세요](guide.md#locale-aware-values).
Babel의 몫입니다. 렌더링된 출력을 HTML, 셸, 터미널에 맞게 이스케이프하지
않습니다. 그리고 번역이 *올바른지*는 판단할 수 없고, 플레이스홀더가
온전한지만 판단합니다.

## 설치 { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 이상이 필요합니다. 렌더링에는 **외부 의존성이 없으며** 표준
라이브러리의 `gettext`만 사용합니다.

추출과 카탈로그 검증에는 [Babel]을 사용합니다. `pybabel`이 실행되는 곳,
즉 보통 프로덕션 이미지가 아니라 개발 또는 CI 환경에 다음 extra를
설치하세요.

```console
python -m pip install "gettext-tstrings[babel]"
```

## 다음 단계 { #where-to-go-next }

**여기서 시작** — gettext 경험을 가정하지 않습니다:

<div class="grid cards" markdown>

- **[튜토리얼](tutorial.md)** — 빈 디렉터리에서 동작하는 일본어 번역까지
  다섯 단계, 모든 명령을 출력과 함께 보여줍니다.
- **[왜 t-string인가](comparison.md)** — 같은 메시지를 네 가지 방식으로
  작성하고, `%(name)s`, `.format()`, `$` 문자열이 각각 카탈로그에 무엇을
  넘기는지 비교합니다.

</div>

**사용하기** — 실무 레퍼런스:

<div class="grid cards" markdown>

- **[가이드](guide.md)** — 런타임 API: 어떤 진입점을 쓸지, 복수형, 요청별
  언어, 지연 문자열, 그리고 잘못된 카탈로그를 만났을 때의 동작.
- **[추출](extraction.md)** — `pybabel` 레퍼런스: 설정, 사용자 정의 함수
  이름, 기존 도구가 이 카탈로그를 공짜로 검증하는 방법.
- **[프로덕션에서](workflow.md)** — 팀이 굴리는 루프: 업데이트 주기,
  fuzzy 항목, CI 게이트, 번역 플랫폼, 그리고 배포.
- **[마이그레이션](migration.md)** — 이미 카탈로그가 있는 프로젝트에
  호출 지점 하나씩 도입하기.
- **[번역자를 위한 안내](translators.md)** — `.po` 파일을 편집하는 사람에게
  그대로 건넬 수 있는 한 페이지.

</div>

**이해하기** — 역사에서 구현까지:

<div class="grid cards" markdown>

- **[배경](background.md)** — 이 라이브러리가 존재하는 이유: 30년의
  gettext, 두 개의 PEP, 그리고 답 없이 닫힌 표준 라이브러리 논의.
- **[함정](pitfalls.md)** — 이 사이트를 서른다섯 개 언어로 번역하면서
  실제로 무엇이 깨졌고, 그중 도구가 잡아낼 수 있는 절반은 무엇인지.
- **[동작 원리](internals.md)** — PEP 750의 템플릿 객체에서 렌더링된
  문자열까지, 그리고 검사를 값싸게 만드는 캐시.

</div>

**레퍼런스** — 계약:

<div class="grid cards" markdown>

- **[API](api.md)** — 패키지의 모든 공개 API를 한 페이지에 담았습니다.
- **[명세](spec.md)** — t-string ↔ msgid 규약을 안정된 버전 계약으로
  정의하고 기계 판독 가능한 적합성 테스트 모음을 제공합니다.

</div>

## 상태 { #status }

| | |
| --- | --- |
| 패키지 버전 | 0.1.0a7 |
| API 안정성 | 알파 — Python API는 아직 바뀔 수 있습니다 |
| [명세](spec.md) | v1, [적합성 테스트 모음](spec.md#conformance) 포함 |
| Python | 3.14 이상. 3.14, 3.14t(자유 스레드), 3.15에서 테스트 |
| Babel | 2.18 이상. `pybabel`을 실행하는 곳에서만 필요 |
| 런타임 의존성 | 없음 — 표준 라이브러리의 `gettext` |
| 카탈로그 형식 | 일반적인 POT, PO, MO |
| 변경 이력 | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

현재 알파 단계입니다. 규약은 의도적으로 작고 그중 안정된 부분은
[명세](spec.md)이며, Python API는 아직 바뀔 수 있습니다. 안정 릴리스
전에는 더 폭넓은 언어 사례, 지속적인 성능 추적, gettext와 Babel을 실제로
쓰는 사람들의 API 검토, 그리고 지원 대상 Python·Babel 릴리스 전반에 걸친
호환성 테스트가 필요합니다.

[이슈와 풀 리퀘스트](https://github.com/yhay81/gettext-tstrings/issues)를
환영합니다. 알파는 인터페이스에 대해 논쟁할 가치가 있는 바로 그
시기입니다.

## 커뮤니티 참여 { #join-the-community }

- 범위가 분명한
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)를 선택하세요.
- 사용법은
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a)에서 질문하세요.
- 실제 gettext 작업 흐름과 API 아이디어는
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas)에서 논의하세요.
- 풀 리퀘스트 전에
  [기여 가이드](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)를 읽어 주세요.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
