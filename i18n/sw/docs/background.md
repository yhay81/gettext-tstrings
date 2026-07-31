---
description: "Miaka thelathini ya gettext, PEP mbili zenye tofauti ya miaka kumi, na mjadala wa stdlib uliofungwa kama not-planned: kwa nini maktaba hii ipo, pamoja na viungo vya vyanzo."
---

# Usuli

Maktaba hii inakaa mahali ambapo hadithi mbili ndefu hukutana — moja kuhusu
jinsi programu zinavyotafsiriwa, nyingine kuhusu jinsi Python inavyoingiza
thamani ndani ya mifuatano — ambazo hatimaye zilikutana mwaka 2025 kisha
zikakwama hasa mahali ambapo makubaliano madogo na ya makini yalihitajika.
Ukurasa huu husimulia hadithi zote mbili, pamoja na viungo vya vyanzo, kwa
sababu maamuzi ya muundo yaliyo kwenye tovuti hii ni rahisi kuyapima
unapoweza kuona maswali wanayoyajibu.

## Mfumo ikolojia wa gettext { #the-gettext-ecosystem }

[GNU gettext] imekuwa ndiyo njia ambayo programu huria hutafsiriwa tangu katikati
ya miaka ya 1990: weka alama kwenye mifuatano ndani ya msimbo, itoe ndani ya
kiolezo, wape wafasiri faili moja la katalogi kwa kila lugha, kusanya, pakia
wakati wa utekelezaji. Kuzunguka mzunguko huo ulikua mfumo ikolojia mzima —
vihariri vya PO, mitiririko ya mapitio, na majukwaa ya tafsiri ambayo yote
huzungumza umbizo lilelile la faili — na Python imesambaza
[moduli ya `gettext`][stdlib-gettext] katika maktaba yake sanifu kwa zaidi ya
miongo miwili. Nusu ya wakati wa utekelezaji ya tafsiri haikuwa tatizo kamwe.

Nusu isiyotatuliwa daima ilikuwa *mfuatano wa katalogi unaonekanaje*. Ujumbe wa
`%(name)s` huwakabidhi wafasiri sintaksia ya printf ambayo herufi moja
iliyofutwa huigeuza kuwa kuanguka kwa programu katika uzalishaji; ujumbe wa
`.format()` huikabidhi katalogi ufikiaji wa sifa za vitu hai.
([Kwa nini t-strings](comparison.md) hupitia zote mbili, na hitilafu
zikionyeshwa waziwazi.) Na f-strings — sintaksia ambayo msimbo mwingi wa Python
sasa huipendelea — haziwezi kushiriki hata kidogo: kufikia wakati maktaba
yoyote inaiona, tayari ni mfuatano uliokamilika. Watu hujaribu hata hivyo, mara
nyingi vya kutosha kiasi kwamba kifuatiliaji masuala cha Babel hukusanya
majaribio hayo ([#594][babel-594], [#715][babel-715]); kushindwa ni kwa
kimuundo, si kipengele kilichokosekana.

## PEP mbili, zenye tofauti ya miaka kumi { #two-peps-ten-years-apart }

Mwaka 2015, Alyssa Coghlan na Nick Humrich waliandika [PEP 501], wakipendekeza
violezo vya uingizaji ambavyo kichocheo chake cha kwanza kilichotajwa kilikuwa
i18n — "kutoa sintaksia safi zaidi kwa tafsiri ya i18n", kwa maneno ya PEP
yenyewe. Pendekezo hilo liliahirishwa, kwa sehemu kwa sababu mjadala ulionyesha
kuwa kesi ya i18n ilibeba mazingatio ya ziada makubwa ambayo matumizi rahisi
zaidi hayakuwa nayo.

Muongo mmoja baadaye, [PEP 750] — ya Jim Baker, Guido van Rossum, Paul Everitt,
Koudai Aono, Lysandros Nikolaou, na Dave Peck — ilifufua wazo hilo kama
t-strings, [ilikubaliwa Aprili 2025][sc-resolution], na ikatolewa katika
[Python 3.14] Oktoba 2025. Kisha PEP 501 ikaondolewa kwa manufaa yake. Kuna
kipengele kimoja muhimu kwa ukurasa huu: i18n *haipo* miongoni mwa vichocheo
vilivyotajwa vya PEP 750. PEP hiyo iliufanya mfumo kuwa wa jumla — aina ya
kiolezo ambayo maktaba yoyote inaweza kuitumia — na ikaliacha swali la tafsiri
hasa pale ambapo PEP 501 ilikuwa imeliegesha miaka kumi mapema: wazi.

Kwa hiyo, kufikia Python 3.14, lugha ilikuwa na muundo wa data ambao katalogi
ya jumbe inauhitaji, bila makubaliano yoyote ya kuutumia hivyo.

## Mjadala wa stdlib { #the-stdlib-discussion }

Miezi miwili kabla 3.14 haijatolewa, Adrian Mönnich (ThiefMaster, mtunzaji wa
mradi wa Indico) alipendekeza kuziba pengo hilo ndani ya maktaba sanifu
yenyewe: uzi [Support t-strings in gettext][discuss-thread] kwenye
discuss.python.org, uliofunguliwa Agosti 2025, ulikuja na
[ombi la kuunganisha][cpython-pr] linalofanya kazi lililoongeza uungwaji mkono
wa t-string kwa `gettext` na `pygettext` vyote viwili.

Uzi huo unastahili kusomwa mzima, kwa sababu huibua kila swali gumu ambalo
maktaba hii ilibidi ilijibu baadaye:

- **Uingizaji unaweza kuwa nini?** Jina rahisi tu, au sifa na miito yenye jina
  la kishika nafasi linalotokana nayo? Kila jibu hubadilishana urahisi na
  uthabiti wa msgid pamoja na usalama wa katalogi.
- **Maumbo ya wingi yanahitaji nini,** wakati mfumo wa wingi wa lugha lengwa
  unatofautiana na ule wa chanzo?
- **Je, gettext ndilo lengo sahihi hata kidogo?** Barry Warsaw — ambaye
  alikuwa amehoji wakati wa uandaaji wa PEP 750 kwamba t-strings hazioani vyema
  na i18n — alielekeza kwenye [`flufl.i18n`][flufl-i18n] yake na mtindo wake wa
  `$`-string kama zana rafiki zaidi; wengine walihoji kuiacha gettext kabisa
  kwa manufaa ya mifumo mipya kama [Fluent].
- **Na swali kuu:** chochote maktaba sanifu inachotoa, kimsingi hakiwezi
  kubadilika kamwe. Makubaliano yenye machaguo mengi wazi kiasi hiki ni kitu
  hatari kukigandisha katika jaribio la kwanza.

Hakuna maafikiano yaliyoundwa. Suala la CPython
[lilifungwa kama "not planned"][cpython-issue] na ombi la kuunganisha
likafungwa bila kuunganishwa Oktoba 2025, siku chache baada ya kutolewa kwa
3.14. Uwezo ulikuwepo ndani ya lugha; makubaliano hayakuwa na makazi.

## Kwa nini kifurushi, kwanza { #why-a-package-first }

Hilo ndilo pengo ambalo mradi huu ulichagua kuliziba kutoka nje ya maktaba
sanifu, kwa dau la makusudi: makubaliano hukomaa haraka zaidi mahali ambapo
yanaweza kubadilisha matoleo kwa uhuru na kupata wafuasi kesi baada ya kesi, na
maktaba sanifu — ambayo lazima iwe sahihi mara ya kwanza — ndipo makubaliano
yanapopaswa *kuishia*, si mahali yanapopaswa kuundwa.

Kwa uhalisia, kila swali lililobishaniwa katika uzi lina jibu lililoandikwa
hapa, kila moja kwenye ukurasa wake:

- Uingizaji ni **majina rahisi tu**, ili msgid zibaki thabiti na zenye maana —
  [mwongozo](guide.md#safety-and-scope) huonyesha kanuni,
  [Jinsi inavyofanya kazi](internals.md#from-template-to-msgid) huonyesha
  sababu.
- **Uumbizaji hubaki nje ya katalogi** kabisa
  ([Kwa nini t-strings](comparison.md)).
- **Wingi** hufuata kanuni ya muungano/mwingiliano inayoruhusu mfumo wa wingi
  wa lugha lengwa kutofautiana na ule wa chanzo ([ainisho §4](spec.md)).
- Katalogi mbovu **hurejea badala ya kuanguka**, ikitunza mkataba wa gettext
  wenyewe ([mwongozo](guide.md#what-happens-when-a-catalog-is-wrong)).
- Na makubaliano yote ni [ainisho lenye matoleo](spec.md) pamoja na seti ya
  utiifu inayosomeka na mashine — yaliyoandikwa ili utekelezaji mwingine,
  ikiwemo ule wa maktaba sanifu wa siku zijazo, uweze kuyachukua bila
  kuyabadilisha na kushirikiana.

Mjadala haujaisha, na mradi huu ni mshiriki ndani yake, si hukumu juu yake.
Ikiwa una uzoefu wa gettext wa uzalishaji unaohusu machaguo haya,
[uzi uleule][discuss-thread] na [Discussions][gh-discussions] za hazina hii
ndipo hoja hizo zinapojadiliwa.

## Ratiba ya matukio { #timeline }

| Lini | Kilichotokea |
| --- | --- |
| katikati ya miaka ya 1990 | GNU gettext huanzisha mtiririko wa kazi wa PO/POT/MO ambao wafasiri na majukwaa bado huuzungumza. |
| 2015 | [PEP 501] hupendekeza violezo vya uingizaji, ikiwa na i18n kama kichocheo chake cha kwanza; huahirishwa. |
| 2016 | f-strings hutolewa katika Python 3.6 — uingizaji hupata sintaksia yake, na tafsiri haiwezi kuitumia. |
| Julai 2024 | [PEP 750] hupendekeza t-strings. |
| Aprili 2025 | PEP 750 [yakubaliwa][sc-resolution]; PEP 501 yaondolewa kwa manufaa yake. |
| Agosti 2025 | Uzi wa [Support t-strings in gettext][discuss-thread] hufunguliwa, ukiwa na [ombi la kuunganisha][cpython-pr] la stdlib. |
| Oktoba 2025 | [Python 3.14] hutoa t-strings; suala la stdlib hufungwa kama [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` hutolewa kama alpha, ikiwa na [ainisho v1](spec.md) na seti yake ya utiifu. |

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
