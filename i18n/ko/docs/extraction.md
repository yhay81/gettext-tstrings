---
description: "pybabel로 t-string 메시지를 추출하고 msgfmt와 내장 Babel checker로 카탈로그를 검증합니다."
---

# 추출

추출은 소스 코드에 표시된 모든 메시지를 번역자를 위한 `.pot` 템플릿으로
모으는 단계로, [튜토리얼](tutorial.md) 루프의 3단계입니다. 이 페이지는 그
단계의 레퍼런스입니다. 설정, 사용자 정의 함수 이름, strict CI 모드,
그리고 그 후 카탈로그를 지키는 검사를 다룹니다.

추출에는 `babel` extra가 필요합니다.

```console
python -m pip install "gettext-tstrings[babel]"
```

## 작업 흐름 { #the-workflow }

`babel.cfg`를 만듭니다.

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

일반 Babel 명령을 그대로 사용합니다.

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init`은 언어마다 한 번만 실행합니다. 그 뒤로는 `pybabel update`가 새
템플릿을 기존 카탈로그에 접어 넣습니다. 그 반복되는 주기 — 그리고 그
`fuzzy` 항목이 릴리스에 무엇을 뜻하는지 — 는
[프로덕션에서](workflow.md#the-cycle-after-the-first-translation)가
차례로 살펴봅니다.

추출기는 `_()`, `gettext()`, `ngettext()`도 처리합니다. 따라서 한 매핑으로
`tr()`, `ntr()`, `lazy_gettext()`, `lazy_pgettext()`가 섞인 코드를 모두
다룹니다.

!!! warning "`-c`는 선택 사항이 아님"

    일반 gettext처럼 번역자 주석을 모으려면 `-c "Translators:"`를
    전달해야 합니다.

## 사용자 정의 함수 이름 { #registering-your-own-function-names }

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

INI 값은 공백이나 쉼표로 나눈 문자열이고 TOML은 목록을 받습니다. 옵션은
여섯 gettext 함수 계열을 모두 지원합니다.

!!! danger "`-k`는 t-string에 도달하지 않음"

    `mytr(t"…")` 같은 helper는 위 옵션에 선언해야 합니다. Babel의
    `--keyword`는 t-string 리터럴을 읽지 않으므로
    `pybabel extract -k mytr`은 경고 없이 누락합니다.

    표준 인수 순서만 지원합니다.

## 기본적으로 견고함 { #robust-by-default }

- 거부된 t-string은 경고 후 건너뜁니다.
- 파싱할 수 없는 파일도 같은 방식으로 격리합니다.
- `tokenize`만 거부하는 파일도 격리합니다.

CI에서 경고를 오류로 바꾸려면 `strict = true`를 사용하세요.

## 기존 도구 체인으로 검증 { #your-existing-toolchain-validates-these-catalogs }

Babel은 표준 플래그를 추가합니다.

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

`こんにちは {nombre}` 같은 번역은 추가 설정 없이 감지됩니다.

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate는 이 검사를 [Python brace format][weblate-checks]으로 설명합니다.
여기서 검증한 도구는 msgfmt와 패키지가 제공하는 Babel checker입니다.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

`pybabel compile`은 표시된 메시지마다 checker를 실행합니다.

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

복수형 오류에는 해당 형태가 표시됩니다.

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile`은 `.mo`를 계속 기록함"

    위 오류가 보고되고 종료 상태는 `1`이지만, 잘못된 카탈로그도 어쨌든
    컴파일됩니다. 그 종료 상태만이 파이프라인이 이를 배포하는 것을 막을
    수 있으며, 이를 가능하게 하는 빌드 단계는
    [CI가 막는 것](workflow.md#what-ci-gates)에서 보여줍니다.

검사는 중복이 아닙니다. 제공된 checker는 msgfmt가 통과시킬 수 있는
이스케이프된 중괄호와 각 복수형을 따로 검증합니다. ASCII 이름은 모든
도구가 검사하게 하며 라이브러리 자체는 모든 `str.isidentifier()` 이름을
허용합니다.

## 템플릿과 다른 도구 { #templates-and-other-tools }

t-string은 Python 문법입니다. Jinja2(`{% trans %}`), Django와 다른
템플릿은 자체 추출기를 유지하면서 같은 PO 카탈로그를 사용할 수 있습니다.

`pygettext`는 아직 t-string을 파싱하지 못합니다. 다른 추출기는
[명세](spec.md)의 규약을 구현할 수 있습니다.
