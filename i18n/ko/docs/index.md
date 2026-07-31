---
description: "포매팅을 카탈로그 밖에 둔 채 gettext와 Babel로 완전한 t-string 메시지를 안전하게 번역합니다."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# 문장은 한 번만 쓰고,<br>통째로 번역하세요.

Python 3.14+ t-string을 위한 안전한 gettext·Babel 통합 — 값은 제자리에
있고, 카탈로그는 완전한 메시지를 봅니다:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[튜토리얼 시작하기 :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[왜 t-string인가](comparison.md){ .md-button }

이 사이트는 문서화한 내용을 스스로 실천합니다. 내비게이션, 레이블,
복수형을 반영한 빌드 보고서까지 모든 언어판을
[`gettext-tstrings` 자신](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)이
PO 카탈로그에서 렌더링합니다.
{ .home-hero-note }

</div>

카탈로그에는 완전한 문장 `Hello {name}`이 들어갑니다. 번역은 `{name}`의
위치를 바꾸거나 반복할 수 있지만, 생략하거나 새로운 플레이스홀더를
만들거나 자체 포매팅을 붙일 수는 없습니다. 이 라이브러리가 이를 검사하며,
잘못된 카탈로그는 충돌 대신 원본 텍스트로 fallback합니다.

!!! note "gettext가 처음이라면? 네 문장으로 보는 전체 작업 흐름"

    **gettext**는 Python을 비롯해 훨씬 넓은 범위에서 소프트웨어를
    번역하는 표준 방식입니다. 코드가 번역 가능한 문자열을 표시하면,
    *추출기*가 이를 템플릿 파일(`.pot`)로 모으고, 대개 프로그래머가 아닌
    번역자가 언어마다 하나씩 카탈로그 파일(`.po`)을 채우며, 이는
    애플리케이션이 런타임에 로드하는 바이너리 `.mo`로 컴파일됩니다.
    번역 함수의 관례적인 이름은 `_`이므로 `_(t"Hello {name}")`은
    "이 문장을 번역하라"로 읽힙니다. **[튜토리얼](tutorial.md)**은
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

## 설계 선택 { #the-choice-it-makes }

- 문장 조각이 아닌 완전한 메시지를 번역합니다.
- `{name}` 같은 단순 변수 이름만 허용합니다.
- `!r`, `:.2f`는 애플리케이션이 관리하고 카탈로그에는 넣지 않습니다.
- 알려진 플레이스홀더의 순서 변경과 반복은 허용하지만 속성 접근이나
  포매팅 추가는 허용하지 않습니다.
- 기존 POT, PO, MO 파일과 도구를 그대로 사용합니다.

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

이곳에 도착하는 독자는 세 부류입니다. 첫 프로그램을 번역하는 사람, 실제
프로젝트에 번역을 연결하는 사람, 그리고 이 장치가 왜 이런 모양인지
정확히 알고 싶은 사람. 각자에게 경로가 있습니다.

**배우기** — gettext 경험을 가정하지 않습니다:

<div class="grid cards" markdown>

- **[튜토리얼](tutorial.md)** — 여기서 시작하세요. 빈 디렉터리에서
  동작하는 일본어 번역까지 다섯 단계, 모든 명령을 출력과 함께 보여줍니다.
- **[왜 t-string인가](comparison.md)** — 같은 메시지를 네 가지 방식으로
  작성하고, `%(name)s`, `.format()`, `$` 문자열이 각각 카탈로그에 무엇을
  넘기는지 비교합니다.
- **[배경](background.md)** — 이 라이브러리가 존재하는 이유: 30년의
  gettext, 두 개의 PEP, 그리고 답 없이 닫힌 표준 라이브러리 논의.

</div>

**본격적으로 사용하기** — 실무 레퍼런스:

<div class="grid cards" markdown>

- **[가이드](guide.md)** — 런타임 API: 복수형, 요청별 언어, 지연 문자열,
  잘못된 카탈로그 처리.
- **[추출](extraction.md)** — `pybabel` 레퍼런스: 설정, 사용자 정의 함수
  이름, 기존 도구가 이 카탈로그를 공짜로 검증하는 방법.
- **[프로덕션에서](workflow.md)** — 팀이 굴리는 루프: 업데이트 주기,
  fuzzy 항목, CI 게이트, 번역 플랫폼, 웹 애플리케이션의 요청별 언어.
- **[API](api.md)** — 패키지의 모든 공개 API를 한 페이지에 담았습니다.

</div>

**이해하기** — 원리에서 구현까지:

<div class="grid cards" markdown>

- **[동작 원리](internals.md)** — PEP 750의 템플릿 객체에서 렌더링된
  문자열까지, 그리고 검사를 값싸게 만드는 캐시.
- **[명세](spec.md)** — t-string ↔ msgid 규약을 안정된 버전 계약으로
  정의하고 기계 판독 가능한 적합성 테스트 모음을 제공합니다.

</div>

## 상태 { #status }

현재 알파 단계입니다. 작은 규약과 명세가 안정성의 중심이며 Python API는
안정 버전 전까지 변경될 수 있습니다. 더 다양한 언어 사례, 지속적인 성능
측정, 실제 gettext/Babel 프로젝트의 피드백이 필요합니다.

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
