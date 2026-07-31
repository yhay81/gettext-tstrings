---
description: "30년의 gettext, 10년 간격의 두 PEP, 그리고 not-planned로 닫힌 표준 라이브러리 논의: 이 라이브러리가 존재하는 이유를 출처 링크와 함께 설명합니다."
---

# 배경

이 라이브러리는 두 개의 긴 이야기 — 소프트웨어가 번역되는 방식에 관한
이야기와 Python이 문자열을 보간하는 방식에 관한 이야기 — 가 만나는
지점에 있습니다. 두 이야기는 2025년에 마침내 교차했지만, 작고 신중한
규약이 필요한 바로 그 지점에서 멈춰 섰습니다. 이 페이지는 출처 링크와
함께 두 이야기를 들려줍니다. 이 사이트의 설계 결정은 그것이 답하는
질문을 볼 수 있을 때 판단하기가 훨씬 쉽기 때문입니다.

## gettext 생태계 { #the-gettext-ecosystem }

[GNU gettext]는 1990년대 중반부터 자유 소프트웨어가 번역되는 방식이었습니다.
코드의 문자열을 표시하고, 템플릿으로 추출하고, 번역자에게 언어당 하나의
카탈로그 파일을 건네고, 컴파일하고, 런타임에 로드합니다. 이 루프를 중심으로
PO 편집기, 리뷰 워크플로, 그리고 같은 파일 형식을 공유하는 번역 플랫폼까지
하나의 생태계 전체가 자라났고, Python도 20년 넘게 표준 라이브러리에
[`gettext` 모듈][stdlib-gettext]을 포함해 왔습니다. 번역의 런타임 절반은
한 번도 문제였던 적이 없습니다.

풀리지 않은 절반은 언제나 *카탈로그 문자열이 어떤 모습인가*였습니다.
`%(name)s` 메시지는 글자 하나만 지워도 프로덕션 충돌이 되는 printf 문법을
번역자에게 넘기고, `.format()` 메시지는 살아 있는 객체에 대한 속성 접근을
카탈로그에 넘깁니다. ([왜 t-string인가](comparison.md)에서 두 실패를 직접
보여주며 다룹니다.) 그리고 지금 대부분의 Python 코드가 선호하는 문법인
f-string은 아예 참여할 수 없습니다. 어떤 라이브러리가 보기 전에 이미
완성된 문자열이기 때문입니다. 그래도 사람들은 시도하고, Babel의 이슈
트래커에는 그 시도가 쌓일 만큼 쌓였습니다([#594][babel-594],
[#715][babel-715]). 이 실패는 기능이 빠진 것이 아니라 구조적인 것입니다.

## 10년 간격의 두 PEP { #two-peps-ten-years-apart }

2015년, Alyssa Coghlan과 Nick Humrich는 보간 템플릿을 제안하는
[PEP 501]을 작성했습니다. PEP 자체의 표현을 빌리면 "i18n 번역을 위한
더 깔끔한 문법 제공"이 첫 번째 동기였습니다. 이 제안은 유보되었는데,
i18n 사례가 더 단순한 사용 사례에는 없는 상당한 추가 고려 사항을
동반한다는 점이 논의에서 드러난 것도 한 이유였습니다.

10년 뒤, Jim Baker, Guido van Rossum, Paul Everitt, Koudai Aono,
Lysandros Nikolaou, Dave Peck의 [PEP 750]이 이 아이디어를 t-string으로
되살렸고, [2025년 4월에 수락되어][sc-resolution] 2025년 10월
[Python 3.14]에 실렸습니다. PEP 501은 그에 밀려 철회되었습니다. 이
페이지에 중요한 세부 사항이 하나 있습니다. i18n은 PEP 750의 명시된 동기에
*포함되지 않습니다*. PEP 750은 어떤 라이브러리든 소비할 수 있는 템플릿
타입으로 메커니즘을 일반화했고, 번역이라는 질문은 PEP 501이 10년 전에
세워 둔 바로 그 자리 — 미해결 상태 — 에 그대로 남겨 두었습니다.

그래서 Python 3.14 시점의 언어에는 메시지 카탈로그에 필요한 데이터 구조가
정확히 갖춰져 있었지만, 그것을 카탈로그로 사용하는 규약은 없었습니다.

## 표준 라이브러리 논의 { #the-stdlib-discussion }

3.14 출시 두 달 전, Adrian Mönnich(ThiefMaster, Indico 프로젝트의
메인테이너)는 그 공백을 표준 라이브러리 안에서 메우자고 제안했습니다.
2025년 8월 discuss.python.org에 열린
[Support t-strings in gettext][discuss-thread] 스레드는 `gettext`와
`pygettext` 양쪽에 t-string 지원을 추가하는 동작하는
[풀 리퀘스트][cpython-pr]와 함께 시작되었습니다.

이 스레드는 전체를 읽어 볼 가치가 있습니다. 이 라이브러리가 나중에 답해야
했던 어려운 질문이 모두 여기서 드러나기 때문입니다.

- **보간에는 무엇이 허용되는가?** 단순 이름만인가, 아니면 파생된
  플레이스홀더 이름을 붙인 속성 접근과 호출까지인가? 어떤 답을 택하든
  편의성과 msgid 안정성·카탈로그 안전성을 맞바꾸게 됩니다.
- **복수형은 무엇을 요구하는가,** 대상 언어의 복수형 체계가 원문 언어와
  다를 때는?
- **애초에 gettext가 올바른 대상인가?** PEP 750 개발 과정에서 t-string이
  i18n에 잘 맞지 않는다고 주장했던 Barry Warsaw는 자신의
  [`flufl.i18n`][flufl-i18n]과 그 `$` 문자열 스타일을 더 친절한 도구로
  제시했고, 다른 이들은 gettext를 아예 떠나 [Fluent] 같은 더 새로운
  시스템으로 가자고 주장했습니다.
- **그리고 메타 질문:** 표준 라이브러리에 무엇을 싣든, 그것은 사실상 다시
  바꿀 수 없습니다. 이렇게 열린 선택지가 많은 규약을 첫 시도에 동결하는
  것은 위험한 일입니다.

합의는 이루어지지 않았습니다. CPython 이슈는
["not planned"로 닫혔고][cpython-issue] 풀 리퀘스트는 3.14 출시 며칠 뒤인
2025년 10월에 병합되지 않은 채 닫혔습니다. 능력은 언어에 존재했지만,
규약은 머물 곳이 없었습니다.

## 왜 먼저 패키지인가 { #why-a-package-first }

바로 그 공백을 이 프로젝트는 표준 라이브러리 바깥에서 메우기로 했습니다.
의도된 내기입니다. 규약은 자유롭게 버전을 올리고 사례 하나하나로 채택을
얻어낼 수 있는 곳에서 더 빨리 성숙하며, 처음부터 옳아야만 하는 표준
라이브러리는 규약이 *도달해야 할* 곳이지 규약을 다듬어야 할 곳이 아닙니다.

구체적으로, 스레드에서 다투어진 모든 질문에 대해 여기에는 각각의 페이지에
글로 적힌 답이 있습니다.

- 보간은 **단순 이름만** 허용하므로 msgid가 안정적이고 의미 있게
  유지됩니다 — [가이드](guide.md#safety-and-scope)가 규칙을,
  [동작 원리](internals.md#from-template-to-msgid)가 이유를 보여줍니다.
- **포매팅은 카탈로그 밖에** 완전히 머뭅니다
  ([왜 t-string인가](comparison.md)).
- **복수형**은 대상 언어의 복수형 체계가 원문과 달라도 되는
  합집합/교집합 규칙을 따릅니다([명세 §4](spec.md)).
- 잘못된 카탈로그는 **충돌하는 대신 fallback**하여 gettext 자체의 계약을
  지킵니다([가이드](guide.md#what-happens-when-a-catalog-is-wrong)).
- 그리고 규약 전체가 기계 판독 가능한 적합성 테스트 모음을 갖춘
  [버전이 있는 명세](spec.md)입니다. 미래의 표준 라이브러리 구현을 포함해
  다른 구현이 그대로 채택하고 상호 운용할 수 있도록 작성되었습니다.

논의는 끝나지 않았고, 이 프로젝트는 그 논의에 대한 판결이 아니라
참여자입니다. 이 선택들과 관련된 프로덕션 gettext 경험이 있다면,
[같은 스레드][discuss-thread]와 이 저장소의
[Discussions][gh-discussions]에서 그 논의가 이어지고 있습니다.

## 타임라인 { #timeline }

| 시기 | 무슨 일이 있었나 |
| --- | --- |
| 1990년대 중반 | GNU gettext가 번역자와 플랫폼이 지금도 공유하는 PO/POT/MO 워크플로를 확립합니다. |
| 2015 | [PEP 501]이 i18n을 첫 번째 동기로 내세워 보간 템플릿을 제안하지만 유보됩니다. |
| 2016 | Python 3.6에 f-string이 실립니다 — 보간은 문법을 얻었지만 번역은 그것을 쓸 수 없습니다. |
| 2024년 7월 | [PEP 750]이 t-string을 제안합니다. |
| 2025년 4월 | PEP 750이 [수락되고][sc-resolution] PEP 501은 그에 밀려 철회됩니다. |
| 2025년 8월 | [Support t-strings in gettext][discuss-thread] 스레드가 표준 라이브러리 [풀 리퀘스트][cpython-pr]와 함께 열립니다. |
| 2025년 10월 | [Python 3.14]가 t-string을 싣고 출시되며, 표준 라이브러리 이슈는 [not planned][cpython-issue]로 닫힙니다. |
| 2026 | `gettext-tstrings`가 [spec v1](spec.md)과 그 적합성 테스트 모음을 갖춘 알파로 출시됩니다. |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
