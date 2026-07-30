---
description: "t-string에서 msgid로 변환하는 규약을 버전이 있는 계약과 기계 판독 가능한 적합성 테스트로 정의합니다."
---

# 명세

이 페이지를 읽지 않아도 라이브러리를 사용할 수 있습니다. 일상적인
사용법은 [튜토리얼](tutorial.md)과 [가이드](guide.md)에서 다룹니다. 이
페이지는 도구 작성자를 위한 것입니다. 추출기, IDE, 타입 검사기, 미래의
`pygettext` 같은 다른 구현이 겨냥하고 상호 운용할 수 있도록, 라이브러리가
구현하는 규약을 작고 안정된 계약으로 적어 둡니다.

[명세 v1 읽기 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## 한 화면으로 보는 규칙

**msgid**는 원본 순서의 리터럴 조각과 각 보간의 `{name}` 토큰을
이어 붙입니다. 리터럴 중괄호는 이스케이프합니다(`{` → `{{`). 이름은
`str.isidentifier()`를 만족하고 Python 키워드가 아니어야 합니다. 변환과
포맷 명세는 애플리케이션에 남습니다.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *거부 — 단순 이름이 아님* |

**번역**은 단순한 `{name}` 플레이스홀더만 포함하고 모든 필수 이름이
있으며 알 수 없는 이름을 추가하지 않을 때 유효합니다. 순서 변경과 반복은
허용합니다.

복수형에서 허용되는 이름은 두 가지 원문의 합집합이고 필수 이름은
교집합입니다. 따라서 `t"One file"`과 `t"{n} files"`은 모든 형태에서
`n`을 허용하지만 강제하지는 않습니다.

**빈 msgid**는 gettext가 메타데이터로 예약하므로 조회하지 않습니다.

## 적합성 { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)은
같은 규칙을 기계 판독 가능한 사례로 설명합니다. 구현이 모든 사례를
재현하면 spec v1에 적합합니다. 오류 문구와 예외 타입은 판정 대상이
아닙니다.

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

참조 구현은 자체 테스트에서 이 모음을 실행합니다.

## 버전 관리

msgid 생성이나 검증의 호환되지 않는 변경은 새 버전과
`conformance/vN.json`을 만듭니다. 결과를 바꾸지 않는 보충 설명은 버전을
바꾸지 않습니다.
