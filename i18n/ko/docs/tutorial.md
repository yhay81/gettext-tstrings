---
description: "빈 디렉터리에서 일본어로 인사하는 프로그램까지 다섯 단계로, 모든 명령을 실제 출력과 함께 보여줍니다."
---

# 튜토리얼

이 페이지는 빈 디렉터리에서 시작해 일본어로 인사하는 프로그램까지
갑니다. 다섯 단계이고, gettext 경험은 가정하지 않으며, 모든 명령을 실제로
만들어 내는 출력과 함께 보여줍니다. 각 단계마다 제대로 가고 있는지 바로
확인할 수 있습니다.

t-string은 3.14의 새 문법이므로 Python 3.14 이상이 필요합니다.
일본어는 이 페이지의 예시 대상일 뿐, 그 선택에 의존하는 것은 아무것도
없습니다. 다른 언어를 쓰려면 4단계의 `ja`를 바꾸세요 — 그 로케일 코드만이
그 언어를 지정하는 유일한 부분입니다.

## 1. 설치 { #1-install }

```console
python -m pip install "gettext-tstrings[babel]"
```

`[babel]` extra는 3단계에서 메시지를 카탈로그 파일로 모으는 도구인
[Babel]을 설치합니다. 개발 시점 도구이며, 프로덕션 코드는 표준
라이브러리만으로 렌더링합니다.

## 2. 코드에 메시지 표시 { #2-mark-a-message-in-your-code }

`app.py`를 만듭니다.

```python
from gettext_tstrings import tr

name = "Ada"
print(tr(t"Hello {name}"))
```

`t"Hello {name}"`은 f-string처럼 보이지만, `t` 접두사는 텍스트와 값을 그
자리에서 합치지 않고 분리해 둡니다. 이 분리 덕분에 `tr()`이 완전한 문장
`Hello {name}`의 번역을 찾은 뒤에 값을 끼워 넣을 수 있습니다.

지금 실행해 보세요.

```console
$ python app.py
Hello Ada
```

아직 설치된 번역이 없으므로 원본 텍스트가 그대로 렌더링됩니다. 이
라이브러리를 쓰는 프로그램은 실행에 카탈로그를 *요구*하지 않습니다.
영어(또는 여러분의 원본 언어)가 내장된 fallback입니다.

## 3. 메시지 추출 { #3-extract-the-messages }

번역자는 보통 소스 코드가 아니라 카탈로그를 보고 작업하므로,
**카탈로그**라는 작은 파일이 여러분과 번역자 사이를 오갑니다. 그 첫걸음은
코드에 표시된 모든 메시지를 모으는 일입니다.

`babel.cfg`를 만들어 Babel에 메시지를 찾는 방법을 알려줍니다.

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

그다음 템플릿 파일(`.pot`)로 추출합니다.

```console
$ mkdir -p locales
$ pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
```

이제 `locales/messages.pot`에는 메시지마다 항목이 하나씩 들어 있습니다.

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

`msgid`는 코드가 조회할 키입니다. 빈 `msgstr`이 번역이 들어갈 자리지만,
이 파일에 쓰지는 않습니다. `.pot`은 *템플릿*이며, 다음 단계에서 언어마다
한 번씩 복사합니다.

## 4. 번역과 컴파일 { #4-translate-and-compile }

템플릿에서 일본어 카탈로그를 만듭니다.

```console
$ pybabel init -i locales/messages.pot -d locales -l ja
creating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

`locales/ja/LC_MESSAGES/messages.po`를 열고 `msgstr`을 채웁니다.

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

`{name}`은 그대로 두세요. 플레이스홀더는 값이 번역된 문장 안에서 자기
자리를 찾는 수단이며, 번역은 대상 언어에 필요한 위치로 플레이스홀더를
자유롭게 옮길 수 있습니다. 실제 프로젝트에서는 이 `.po` 파일을 번역자에게
전달하거나 번역 플랫폼에 업로드합니다. 어느 쪽이든 형식은 같습니다.

카탈로그는 텍스트로 편집하지만 바이너리 형식(`.mo`)으로 로드하므로
컴파일합니다.

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
```

이 명령은 안전망이기도 합니다. 번역이 플레이스홀더를 손상시켰다면 —
예를 들어 `{name}` 대신 `{nome}` — 통과를 거부합니다.

```console
$ pybabel compile -d locales
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nome} is not in the source message
1 errors encountered.
```

지금 알아 둘 만한 단서가 하나 있습니다. 오류를 보고하고 0이 아닌 상태로
종료하지만, `.mo`는 어쨌든 기록합니다. 실제 프로젝트에서는 그 종료 상태를
보고 멈춰야 하는 쪽이 CI이며, [프로덕션에서](workflow.md#what-ci-gates)가
그것을 설정합니다.

## 5. 실행 { #5-run-it }

2–4단계에서는 `tr()`을 썼는데, 이 함수는 카탈로그를 찾아보고 아무것도
찾지 못했습니다. 이제 하나가 존재하니 로드해서 한 번 바인딩합니다.
`Translator`가 카탈로그를 들고 있으므로 호출 지점이 카탈로그를 지목할
필요가 없고, `_`는 그 결과에 붙이는 gettext의 관례적인 이름입니다.

`app.py`가 컴파일된 카탈로그를 가리키게 합니다. 각 줄이 무엇을 하는지
마커를 클릭해 확인하세요.

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales", languages=["ja"]))  # (1)!

name = "Ada"
print(_(t"Hello {name}"))  # (2)!
```

1. 표준 라이브러리가 컴파일된 `.mo`를 로드하고, `Translator`가 이를
   호출 가능한 객체로 바인딩합니다. `_`는 "이것을 번역하라"를 뜻하는
   gettext의 관례적인 이름입니다. 사용자에게 보이는 모든 문자열에
   등장하므로 짧습니다. 하나의 카탈로그에 바인딩된 채로 `tr`과 같은
   번역을 수행합니다.
2. 호출 시점에는 이렇게 됩니다. t-string의 텍스트가 조회 키
   `Hello {name}`이 되고, 카탈로그가 `こんにちは {name}`으로 답하며, 그
   답을 원본 플레이스홀더와 대조해 검사한 뒤에야 값이 들어갑니다.

```console
$ python app.py
こんにちは Ada
```

이것이 전체 루프이며, 한 장의 그림으로 볼 가치가 있습니다.

```mermaid
flowchart LR
  mark["1–2 표시<br>코드의 t-string"] --> extract["3 추출<br>messages.pot"]
  extract --> translate["4 번역<br>ja/…/messages.po"]
  translate --> compile["4 컴파일<br>ja/…/messages.mo"]
  compile --> run["5 실행<br>こんにちは Ada"]
```

**표시 → 추출 → 번역 → 컴파일 → 실행.** 이 사이트의 나머지 내용은 모두
이 다섯 단계 중 하나를 다듬은 것입니다.

## 다음 단계 { #where-next }

- [왜 t-string인가](comparison.md) — `%(name)s`, `.format()`, `$` 문자열과
  비교해 이 설계가 무엇으로부터 보호해 주는지.
- [가이드](guide.md) — 복수형, 요청별 언어, 지연 문자열, 그리고 그럼에도
  카탈로그가 잘못되었을 때 런타임에 일어나는 일.
- [프로덕션에서](workflow.md) — 팀이 매주 굴리는 바로 이 루프: 카탈로그
  업데이트, CI 게이트, 번역 플랫폼.
- [추출](extraction.md) — 전체 `pybabel` 레퍼런스: 사용자 정의 함수 이름,
  strict CI 모드, 카탈로그를 지키는 검사.
- [마이그레이션](migration.md) — 실제로 이 일을 적용하려는 프로젝트에
  이미 gettext 카탈로그가 있다면.
- [번역자를 위한 안내](translators.md) — 그 `msgstr` 줄을 채우는 사람에게
  건넬 단 한 페이지.

  [Babel]: https://babel.pocoo.org/
