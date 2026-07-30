---
description: "포매팅을 카탈로그 밖에 둔 채 gettext와 Babel로 완전한 t-string 메시지를 안전하게 번역합니다."
---

# gettext-tstrings

Python 3.14+ t-string을 gettext 및 Babel과 안전하게 통합합니다.

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))
```

카탈로그에는 완전한 문장 `Hello {name}`이 들어갑니다. 번역은 `{name}`의
위치를 바꾸거나 반복할 수 있지만, 생략하거나 새로운 플레이스홀더를
만들거나 자체 포매팅을 붙일 수는 없습니다.

## 해결하는 문제

f-string은 라이브러리가 받기 전에 이미 보간되어 있으므로 번역하면 문장
조각만 남습니다. t-string([PEP 750])은 정적 텍스트, 평가된 값, 원본 식,
변환, 포맷 명세를 분리해 보존합니다. 메시지 카탈로그에 정확히 필요한
구조입니다. `%(name)s`, `.format()`과의 차이는
[비교 페이지](comparison.md)에서 확인할 수 있습니다.

gettext와 Babel은 t-string을 메시지로 바꾸는 규칙까지 정하지 않습니다.
이 라이브러리는 그 규칙을 [버전이 있는 명세](spec.md)로 정의하고
[적합성 테스트 모음](spec.md#conformance)을 제공합니다.

## 설계 선택

- 문장 조각이 아닌 완전한 메시지를 번역합니다.
- `{name}` 같은 단순 변수 이름만 허용합니다.
- `!r`, `:.2f`는 애플리케이션이 관리하고 카탈로그에는 넣지 않습니다.
- 알려진 플레이스홀더의 순서 변경과 반복은 허용하지만 속성 접근이나
  포매팅 추가는 허용하지 않습니다.
- 기존 POT, PO, MO 파일과 도구를 그대로 사용합니다.

## 이 사이트가 직접 사용합니다

이 문서는 번역된 데모에 그치지 않습니다. 내비게이션, 테마 레이블,
저작권 문구, 복수형을 반영한 빌드 결과를 `gettext-tstrings`가 PO
카탈로그에서 직접 렌더링합니다.
[다국어 빌더](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)는
매 strict 빌드에서 컨텍스트 메시지, 이름 있는 플레이스홀더, 열 개 언어의
복수형 규칙을 모두 실행합니다.

## 설치

```console
python -m pip install gettext-tstrings
```

Python 3.14 이상이 필요합니다. 렌더링에는 **외부 의존성이 없으며** 표준
라이브러리의 `gettext`만 사용합니다.

추출과 카탈로그 검증에는 [Babel]을 사용합니다. 개발 또는 CI 환경에
다음 extra를 설치하세요.

```console
python -m pip install "gettext-tstrings[babel]"
```

## 다음 단계

<div class="grid cards" markdown>

- **[왜 t-string인가](comparison.md)** — 같은 메시지를 세 가지 방식으로 비교합니다.
- **[가이드](guide.md)** — 런타임 API, 요청별 언어, 지연 번역, 잘못된 카탈로그.
- **[추출](extraction.md)** — `pybabel` 작업 흐름과 검증.
- **[명세](spec.md)** — 안정된 규약과 적합성 테스트 모음.
- **[API](api.md)** — 패키지의 모든 공개 API.

</div>

## 상태

현재 알파 단계입니다. 작은 규약과 명세가 안정성의 중심이며 Python API는
안정 버전 전까지 변경될 수 있습니다. 더 다양한 언어 사례, 지속적인 성능
측정, 실제 gettext/Babel 프로젝트의 피드백이 필요합니다.

[이슈와 풀 리퀘스트](https://github.com/yhay81/gettext-tstrings/issues)를
환영합니다.

## 커뮤니티 참여

- 범위가 분명한
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)를 선택하세요.
- 사용법은
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a)에서 질문하세요.
- API 아이디어는
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas)에서 논의하세요.
- 풀 리퀘스트 전에
  [기여 가이드](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)를 읽어 주세요.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
