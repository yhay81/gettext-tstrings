---
description: "이미 gettext 카탈로그가 있는 프로젝트에 t-string 도입하기: 그대로 남는 것, fuzzy가 되는 것, 그리고 호출 지점을 하나씩 옮기는 방법."
---

# 마이그레이션

프로젝트가 이미 gettext를 쓰고 있다면, 이 라이브러리를 도입할 수 있는지를
가르는 질문은 몇 가지로 좁혀집니다. 지금 가진 카탈로그를 무효로 만드는가,
아직 손댈 준비가 되지 않은 코드와 공존할 수 있는가, 그리고 이전 작업 중
얼마나가 한꺼번에 일어나야 하는가. 짧은 답부터 보면 이렇습니다.

| 질문 | 답 |
| --- | --- |
| 기존 `.po`와 `.mo` 파일이 계속 동작하나요? | 예. 같은 파일, 같은 도구입니다. |
| 예전 호출과 새 호출이 한 파일에 있어도 되나요? | 예. 추출기 매핑 하나로 둘 다 처리됩니다. |
| msgid가 바뀌나요? | `.format()`에서는 아니요. `%` 포맷에서는 예. |
| 프로젝트 전체를 한 번에 옮겨야 하나요? | 아니요. 호출 지점 하나짜리 변경도 유효합니다. |
| Jinja, Django 템플릿, JavaScript는요? | 그대로입니다. 같은 카탈로그를 씁니다. |

이 페이지의 나머지는 그 각각의 자세한 내용입니다.

## `.format()`에서: msgid가 바뀌지 않습니다 { #from-format-the-msgid-does-not-change }

이전 비용이 거의 들지 않는 경우입니다. `str.format` 메시지와 t-string
메시지는 *같은* 카탈로그 키를 만들어 냅니다. 어느 쪽이든 키는 `{name}`이
그대로 남아 있는 텍스트이기 때문입니다.

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

그래서 기존 번역이 계속 붙어 있습니다. 다음을 담고 있는 카탈로그에서
출발한다고 해 봅시다.

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

호출을 바꾸고, 다시 추출하고, 업데이트합니다.

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

돌아온 항목은 메타데이터 두 줄만 다르고 나머지는 같습니다. t-string
메시지임을 알리는 표시 주석과 소스 줄 번호입니다.

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

`fuzzy` 플래그도, 재번역도 없습니다. 어떤 언어에서도 그렇습니다. 메시지는
곧바로 렌더링됩니다.

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check`는 카탈로그가 최신이 아니라고 보고합니다"

    그 표시 주석과 옮겨진 줄 번호만으로도 `pybabel update --check`는
    카탈로그를 다시 만들어야 한다고 말합니다. 번역만이 아니라 항목 전체를
    비교하기 때문입니다. 코드 변경과 같은 커밋에서 진짜 `pybabel update`를
    실행하고 카탈로그도 함께 커밋하세요.
    [CI 게이트](workflow.md#what-ci-gates)가 이미 요구하는 것과 같은
    습관입니다.

## `%` 포맷에서: msgid가 바뀌므로 번역이 fuzzy가 됩니다 { #from--format-the-msgid-changes-so-translations-go-fuzzy }

printf 문법은 메시지 *안에* 들어 있으므로, 이를 교체하면 카탈로그 키가 다시
쓰입니다. 피할 방법은 없으며, `%(name)s`를 떠나는 데 드는 정직한 비용입니다.

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update`는 새 메시지가 제거된 메시지와 가깝다는 것을 알아보고 예전
번역을 fuzzy 표시와 함께 넘겨줍니다.

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

그 상태에 대해 알아야 할 것이 세 가지 있습니다.

- **런타임에는 아무것도 깨지지 않습니다.** fuzzy 항목은 컴파일된 `.mo`에서
  빠지므로, 사람이 그 짝을 확인할 때까지 애플리케이션은 원본 메시지를
  렌더링합니다. 표현을 바꾼 메시지가 겪는
  [같은 성능 저하](workflow.md#the-cycle-after-the-first-translation)입니다.
- **`pybabel compile`이 하나하나 보고합니다.** 넘어온 `%(name)s`가 유효한
  중괄호 플레이스홀더가 아니기 때문이며, 종료 코드도 0이 아닙니다. 그 목록은
  거짓 경보가 아니라 여러분의 작업 대기열입니다. 목록에 있는 항목은 정말로
  편집이 필요합니다.
- **예전 `python-format` 플래그가 함께 따라옵니다.** `fuzzy` 플래그와 함께
  지워야 합니다. 그러지 않으면 `msgfmt --check-format`이 중괄호 포맷 메시지에
  계속 printf 규칙을 적용합니다.

이름이 있는 printf 플레이스홀더라면 편집은 기계적입니다. `%(name)s`가
`{name}`이 되고 그 밖에는 아무것도 움직이지 않으므로, 큰 카탈로그도 재번역이
아니라 스크립트 한 번에 번역자 검토를 붙이는 일이 됩니다. 위치 기반 `%s`는
기계적이지 않습니다. 넘겨받을 이름이 없고, 이름을 고르는 일이 바로 이 변경의
핵심입니다.

그래서 실무에서의 순서는 `%` 포맷 메시지를 의도적으로 — 모듈 단위, 릴리스
단위, 언어 단위로 — 옮기는 것이지, 모든 카탈로그를 한꺼번에 빨갛게 만드는
일괄 작업이 아닙니다.

## 예전 호출과 새 호출의 공존 { #old-and-new-calls-coexist }

t-string을 읽는 추출기는 평범한 gettext 호출도 읽으므로, 이전 작업 중인
파일도 매핑 하나로 처리됩니다.

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

두 메시지 모두 같은 템플릿에 들어가며, 이 라이브러리의 추가 검사를 켜는 표시
주석은 t-string 쪽에만 붙습니다.

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

추출기는 `_()`, 표준 gettext 이름 네 가지, `tr()` / `ntr()` 별칭, 그리고
지연 호출인 `lazy_gettext()` / `lazy_pgettext()`를 인식합니다. 직접 만든
헬퍼는 [매핑에 이름을 적어](extraction.md#registering-your-own-function-names)
주어야 합니다.

런타임에서도 두 방식은 똑같이 독립적입니다. `gettext.translation()`이 번역
객체 하나를 반환하고, `_`와 이 라이브러리의 진입점 모두가 그 객체에서
읽습니다.

## 옮기지 않아도 되는 것 { #what-does-not-move }

- **템플릿 언어.** Jinja2의 `{% trans %}`, Django의 템플릿 태그, 그리고 그
  Babel 추출기들은 그대로 동작하며 계속 같은 PO 카탈로그에 메시지를
  공급합니다. t-string은 Python 문법이므로 Python 소스에만 적용됩니다.
- **카탈로그 파일.** 형식 변경도, 새 파일도, 변환 단계도 없습니다.
- **번역 플랫폼.** `.po` 교환 방식은 동일하고, t-string 메시지가 달고 있는
  `python-brace-format` 플래그는 `.format()` 메시지가 달고 있는 플래그와 같은
  것이므로 플레이스홀더 QA도 계속 동작합니다.
- **Python이 아닌 코드.** 같은 프로젝트 안의 JavaScript나 C 카탈로그는 영향을
  받지 않습니다.

## 마이그레이션 체크리스트 { #a-migration-checklist }

1. `pybabel`이 실행되는 곳에 `babel` extra를 추가하고, `babel.cfg`의 `python`
   매핑을 `gettext_tstrings` 메서드로 바꾸세요. 그러면 매핑 하나가 두 방식을
   모두 처리하고, 평범한 호출에 대해서는 `-k`도 계속 동작합니다.
2. `.format()` 호출 지점을 먼저 옮기세요. 다시 추출하고 `pybabel update`를
   실행한 뒤 카탈로그를 코드와 함께 커밋합니다. fuzzy 항목은 나오지 않아야
   합니다.
3. `%` 포맷 호출 지점을 검토받을 수 있는 크기로 나누어 옮기면서, 넘어온
   플레이스홀더를 고쳐 쓰고 `fuzzy`와 `python-format` 플래그를 지우세요.
4. 제약에 걸리는 부분을 고치세요. 보간은 단순 이름이어야 하므로
   `t"Hello {user.name}"`은 지역 변수를 먼저 두는 형태가 됩니다. 카탈로그가
   아니라 호출 지점을 고치는 일입니다.
5. 작업이 끝나면 추출기 매핑에서 `strict = true`를 켜세요. 추출할 수 없는
   메시지가 템플릿에서 조용히 사라지는 대신
   [빌드를 실패시키도록](extraction.md#lenient-locally-strict-in-ci) 말입니다.
6. [프로덕션에서](workflow.md#what-ci-gates)의 런타임 검사를 추가하세요.
   출시하는 언어마다 메시지 하나씩을 strict `Translator`로 렌더링하는
   것입니다.

2번과 3번은 평범한 커밋입니다. 이 목록에 하루를 통째로 비워야 하는 항목은
없습니다.
