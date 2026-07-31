---
description: "Deng mlynedd ar hugain o gettext, dau PEP ddeng mlynedd ar wahân, a'r drafodaeth am y llyfrgell safonol a gaeodd fel heb ei chynllunio: pam y mae'r llyfrgell hon yn bodoli, gyda dolenni at y ffynonellau."
---

# Cefndir

Mae'r llyfrgell hon yn eistedd ar gyffordd dwy stori hir — un am sut y caiff
meddalwedd ei chyfieithu, un am sut y mae Python yn rhyngosod llinynnau — a
groesodd o'r diwedd yn 2025 ac wedyn a stopiodd yn union yn y man lle'r oedd
angen confensiwn bach, gofalus. Mae'r dudalen hon yn adrodd y ddwy stori, gyda
dolenni at y ffynonellau, am ei bod hi'n haws barnu penderfyniadau dylunio'r
wefan hon pan allwch weld y cwestiynau y maent yn eu hateb.

## Ecosystem gettext { #the-gettext-ecosystem }

[GNU gettext] fu'r ffordd y mae meddalwedd rydd yn cael ei chyfieithu ers canol
y 1990au: nodwch y llinynnau yn y cod, echdynnwch nhw i dempled, rhowch un ffeil
gatalog fesul iaith i gyfieithwyr, crynhowch, llwythwch wrth redeg. O amgylch y
ddolen honno tyfodd ecosystem gyfan — golygyddion PO, llifau gwaith adolygu, a
llwyfannau cyfieithu sydd oll yn siarad yr un fformat ffeil — ac mae Python wedi
cludo [modiwl `gettext`][stdlib-gettext] yn ei llyfrgell safonol ers mwy na dau
ddegawd. Nid hanner rhedeg cyfieithu fu'r broblem erioed.

Yr hanner ansefydlog fu bob amser *sut olwg sydd ar linyn y catalog*. Mae neges
`%(name)s` yn rhoi i gyfieithwyr gystrawen printf y mae un llythyren wedi'i
dileu yn ei throi'n chwalfa mewn cynhyrchu; mae neges `.format()` yn rhoi i'r
catalog fynediad priodoledd ar wrthrychau byw. (Mae
[Pam llinynnau-t](comparison.md) yn cerdded drwy'r ddau, gyda'r methiannau i'w
gweld.) Ac ni all llinynnau-f gymryd rhan o gwbl — y gystrawen y mae'r rhan
fwyaf o god Python bellach yn ei ffafrio: erbyn i unrhyw lyfrgell weld un, mae
eisoes yn llinyn gorffenedig. Mae pobl yn ceisio serch hynny, yn ddigon aml i
draciwr materion Babel gasglu'r ymdrechion ([#594][babel-594],
[#715][babel-715]); mae'r methiant yn strwythurol, nid yn nodwedd goll.

## Dau PEP, ddeng mlynedd ar wahân { #two-peps-ten-years-apart }

Yn 2015, ysgrifennodd Alyssa Coghlan a Nick Humrich [PEP 501], gan gynnig
templedi rhyngosod y datganwyd mai i18n oedd eu cymhelliant cyntaf — "providing
a cleaner syntax for i18n translation", yng ngeiriau'r PEP ei hun. Gohiriwyd y
cynnig, yn rhannol am fod y drafodaeth wedi dangos bod yr achos i18n yn cario
ystyriaethau ychwanegol sylweddol nad oedd achosion defnydd symlach yn eu cario.

Ddegawd yn ddiweddarach, adfywiodd [PEP 750] — gan Jim Baker, Guido van Rossum,
Paul Everitt, Koudai Aono, Lysandros Nikolaou, a Dave Peck — y syniad fel
llinynnau-t, cafodd ei [dderbyn ym mis Ebrill 2025][sc-resolution], a chludwyd
ef yn [Python 3.14] ym mis Hydref 2025. Tynnwyd PEP 501 yn ôl wedyn o'i blaid.
Mae un manylyn o bwys i'r dudalen hon: *nid* yw i18n ymhlith cymhellion
datganedig PEP 750. Cyffredinolodd y PEP y mecanwaith — math templed y gall
unrhyw lyfrgell ei fwyta — a gadawodd y cwestiwn cyfieithu yn union lle'r oedd
PEP 501 wedi ei barcio ddeng mlynedd ynghynt: ar agor.

Felly o Python 3.14 ymlaen, roedd gan yr iaith yn union y strwythur data y mae
catalog negeseuon ei angen, a dim confensiwn ar gyfer ei ddefnyddio fel un.

## Y drafodaeth am y llyfrgell safonol { #the-stdlib-discussion }

Ddeufis cyn i 3.14 gael ei chludo, cynigiodd Adrian Mönnich (ThiefMaster,
cynhaliwr ar brosiect Indico) gau'r bwlch hwnnw yn y llyfrgell safonol ei hun:
daeth yr edefyn [Support t-strings in gettext][discuss-thread] ar
discuss.python.org, a agorwyd ym mis Awst 2025, gyda [chynnig tynnu][cpython-pr]
gweithredol yn ychwanegu cefnogaeth i linynnau-t at `gettext` a `pygettext` fel
ei gilydd.

Mae'r edefyn yn werth ei ddarllen yn llawn, am ei fod yn codi pob cwestiwn anodd
y bu'n rhaid i'r llyfrgell hon eu hateb wedyn:

- **Beth gaiff rhyngosodiad fod?** Enw syml yn unig, ynteu priodoleddau a
  galwadau ag enw daliwr lle deilliedig? Mae pob ateb yn cyfnewid cyfleustra am
  sefydlogrwydd msgid a diogelwch catalogau.
- **Beth mae ffurfiau lluosog yn ei fynnu,** pan fo system luosog yr iaith
  darged yn wahanol i un y ffynhonnell?
- **A yw gettext hyd yn oed y targed cywir?** Cyfeiriodd Barry Warsaw — a oedd
  wedi dadlau yn ystod datblygiad PEP 750 nad oedd llinynnau-t yn ffit dda i
  i18n — at ei [`flufl.i18n`][flufl-i18n] a'i harddull llinynnau-`$` fel yr
  offeryn cyfeillgarach; dadleuodd eraill dros adael gettext ar ôl yn gyfan gwbl
  o blaid systemau mwy newydd megis [Fluent].
- **A'r meta-gwestiwn:** beth bynnag y mae'r llyfrgell safonol yn ei gludo, ni
  all bron byth ei newid. Mae confensiwn â chymaint o ddewisiadau agored yn beth
  peryglus i'w rewi ar y cynnig cyntaf.

Ni ffurfiodd unrhyw gonsensws. Cafodd mater CPython ei
[gau fel "heb ei gynllunio"][cpython-issue] a chaewyd y cynnig tynnu heb ei
uno ym mis Hydref 2025, ddyddiau ar ôl rhyddhad 3.14. Roedd y gallu'n bodoli yn
yr iaith; nid oedd gan y confensiwn gartref.

## Pam pecyn, yn gyntaf { #why-a-package-first }

Dyna'r bwlch y dewisodd y prosiect hwn ei lenwi o'r tu allan i'r llyfrgell
safonol, ar fentr fwriadol: mae confensiwn yn aeddfedu'n gyflymach lle y gall
fersiynu'n rhydd ac ennill mabwysiad achos wrth achos, a'r llyfrgell safonol —
sy'n gorfod bod yn iawn y tro cyntaf — yw lle *dylai* confensiwn ddod i ben, nid
lle y dylid ei weithio allan.

Yn benodol, mae gan bob cwestiwn dadleuol yn yr edefyn ateb wedi'i ysgrifennu i
lawr yma, pob un ar ei dudalen ei hun:

- **Enwau syml yn unig** yw rhyngosodiadau, fel bod msgidiau'n aros yn sefydlog
  ac yn ystyrlon — mae [y canllaw](guide.md#safety-and-scope) yn dangos y rheol,
  a [Sut mae'n gweithio](internals.md#from-template-to-msgid) y rhesymau.
- Mae **fformatio'n aros allan o'r catalog** yn gyfan gwbl
  ([Pam llinynnau-t](comparison.md)).
- Mae **lluosogion** yn dilyn rheol uniad/croestoriad sy'n gadael i system
  luosog iaith darged fod yn wahanol i un y ffynhonnell ([manyleb §4](spec.md)).
- Mae catalog toredig yn **cwympo'n ôl yn lle chwalu**, gan gadw contract
  gettext ei hun ([y canllaw](guide.md#what-happens-when-a-catalog-is-wrong)).
- Ac mae'r confensiwn cyfan yn [fanyleb â fersiwn](spec.md) gyda chyfres
  gydymffurfio y gall peiriant ei darllen — wedi'i hysgrifennu fel y gallai
  gweithrediad arall, gan gynnwys un yn y llyfrgell safonol yn y dyfodol, ei
  mabwysiadu heb ei newid a rhyngweithredu.

Nid yw'r drafodaeth wedi dod i ben, a chyfrannwr ynddi yw'r prosiect hwn, nid
dyfarniad arni. Os oes gennych brofiad gettext cynhyrchu sy'n berthnasol i'r
dewisiadau hyn, yr [un edefyn][discuss-thread] a [Thrafodaethau][gh-discussions]
y storfa hon yw lle y mae'r drafodaeth yn parhau.

## Llinell amser { #timeline }

| Pryd | Beth ddigwyddodd |
| --- | --- |
| canol y 1990au | Mae GNU gettext yn sefydlu'r llif gwaith PO/POT/MO y mae cyfieithwyr a llwyfannau'n dal i'w siarad. |
| 2015 | Mae [PEP 501] yn cynnig templedi rhyngosod, gydag i18n fel ei gymhelliant cyntaf; gohiriwyd. |
| 2016 | Mae llinynnau-f yn cyrraedd yn Python 3.6 — mae rhyngosod yn cael ei gystrawen, ac ni all cyfieithu ei defnyddio. |
| Gorff 2024 | Mae [PEP 750] yn cynnig llinynnau-t. |
| Ebr 2025 | [Derbynnir][sc-resolution] PEP 750; tynnir PEP 501 yn ôl o'i blaid. |
| Awst 2025 | Mae'r edefyn [Support t-strings in gettext][discuss-thread] yn agor, gyda [chynnig tynnu][cpython-pr] i'r llyfrgell safonol. |
| Hyd 2025 | Mae [Python 3.14] yn cludo llinynnau-t; mae mater y llyfrgell safonol yn cau fel [heb ei gynllunio][cpython-issue]. |
| 2026 | Mae `gettext-tstrings` yn cyrraedd fel alffa, gyda [manyleb v1](spec.md) a'i chyfres gydymffurfio. |

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
