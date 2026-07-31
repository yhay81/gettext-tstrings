---
description: "Beth y mae cyfieithu un wefan fach i bymtheg ar hugain o ieithoedd yn ei dorri mewn gwirionedd, pa rai o'r rheini y gall y llyfrgell eu dal drosoch, a pha rai na all."
---

# Peryglon

Mae'r wefan hon wedi'i chyfieithu i bymtheg ar hugain o ieithoedd, a
chynhyrchwyd pob un ohonynt drwy redeg y ddolen y mae'r ddogfennaeth hon yn ei
dysgu. Corpws bach yw hwnnw yn ôl safonau'r diwydiant, ac roedd yn dal yn ddigon
i daro'r rhan fwyaf o'r maglau sy'n gwneud i18n yn anos nag y mae'n edrych.

Mae pob adran isod yn rhywbeth a aeth o chwith yma go iawn, sut yr edrychai ar y
pryd, a lle mae'r ffin rhwng yr hyn y mae'r llyfrgell yn ei wirio drosoch a'r
hyn sy'n aros yn fater i'ch crebwyll chi.

## Mae ailenwi newidyn yn ailgyfieithu brawddeg { #renaming-a-variable-retranslates-a-sentence }

Y msgid yw allwedd y catalog, ac mae enw wedi'i ryngosod *y tu mewn* iddi.
Trodd symud un cysonyn i sgôp y modiwl a'i briflythrennu fel y mae arddull
Python yn gofyn — `author` yn `AUTHOR` — `Copyright © 2026 {author} · MIT
License` yn neges nad oedd yr un catalog erioed wedi'i gweld. Byddai pob
cyfieithiad o'r llinell honno wedi mynd yn ôl drwy'r cylch fuzzy, ym mhob iaith,
am ailenwi na newidiodd ddim y gallai darllenydd ei weld.

Ni fydd y llyfrgell yn eich rhwystro: mae'r ddau sillafiad yn enwau dalwyr lle
dilys. Yr hyn y mae'n ei wneud yw gwneud yr enw'n *werth* ei ddiogelu — rhaid i
ryngosodiad fod yn [enw plaen](internals.md#from-template-to-msgid), felly gair y
gall cyfieithydd ei ddarllen yw'r peth sydd yn allwedd y catalog, nid mynegiant.

Mae'r achos drych yn ddiogel wrth ei natur. Nid yw trawsnewidiadau a manylebau
fformat yn rhan o'r msgid, felly nid yw tynhau `{amount:,.2f}` yn `{amount:,.0f}`
yn newid yr un allwedd nac yn dirymu'r un cyfieithiad yn unman.

## Nid yw `nplurals=2` yn golygu dau linyn gwahanol { #nplurals-2-does-not-mean-two-different-strings }

Mae Twrceg, Hwngareg, Perseg a Bengaleg oll yn datgan dwy ffurf luosog, ac ym
mhob un o'r pedair mae dwy ffurf neges gyfrifedig yn gyfreithlon yr *un llinyn*
— mae'r enw'n aros yn unigol ar ôl rhifolyn, felly mae `{n} sayfa` yn iawn ar
gyfer un dudalen ac ar gyfer deg. Mae adolygydd sy'n "trwsio" y dyblygu yn torri'r
cyfieithiad.

Mae'r camgymeriad i'r cyfeiriad arall yr un mor hawdd. Ar gyfer **sero'n unig**
y mae trydedd ffurf Latfieg yn bodoli; **deuol** yw ail ffurf Slofeneg, ar gyfer
union ddau; mae ffurf olaf Rwmaneg yn mynnu'r gair `de` na chaiff ei dwy ffurf
gyntaf mo'i gynnwys. Mae llenwi'r slotiau hynny ag unigol a lluosog yn cynhyrchu
catalog sy'n anghywir dim ond ar gyfer cyfrifon nad oes neb yn eu profi.

Yn waeth, nid yw *trefn* y slotiau'n semantig. Mae'r Gymraeg yn mynegeio ei phum
ffurf fel mai `msgstr[0]` yw'r achos cyffredinol ac `msgstr[1]` yw'r unigol. Mae
eu llenwi yn y drefn amlwg yn rhoi'r unigol lle bydd pob neges anghyfrifedig yn
dod o hyd iddo.

Nid yw'r llyfrgell yn cymryd dim o hyn arni ei hun, a dyna'r pwynt: mae rheol
luosog yr iaith darged yn byw ym mhennyn ei chatalog ei hun, ac mae'r
[rheol undeb/croestoriad](spec.md) yn gadael i gyfieithiad gael mwy o ffurfiau,
neu lai, na'r ffynhonnell. Yr hyn y mae'n ei wirio yw'r unig beth y gall ei
wirio heb wybod yr iaith — bod pob ffurf yn cadw'r dalwyr lle sydd eu hangen
arni.

## Gall dwy ffurf fod yn union yr un fath am reswm { #two-forms-can-be-identical-for-a-reason }

Mae gan y Wyddeleg bum ffurf luosog, ac yn adroddiad adeiladu'r wefan hon mae
sawl un ohonynt wedi'u sillafu'r un fath. Nid llithriad copïo-a-gludo mo hynny:
mae *leathanach* yn dechrau ag `l`, ac nid yw'r naill na'r llall o'r treigladau
blaen y mae rhifolion Gwyddeleg yn eu sbarduno yn cael ei ysgrifennu ar `l`. Mae'r
ffurfiau'n gwneud gwaith go iawn o hyd — mae'r bôn yn amrywio rhwng *leathanach*
a *leathanaigh*, ac mae cyfrifon uwchlaw deg yn dychwelyd at yr unigol — ond ni
fyddai'r un enw sy'n golygu "tudalen" yn dangos y gwrthgyferbyniad.

Bydd unrhyw wiriad sy'n baneru ffurfiau dyblyg fel rhai amheus yn baneru
Gwyddeleg gywir. Bod dynol sy'n gwybod yr iaith yw'r unig adolygydd ar gyfer hyn.

## Ni all neges gytuno ond ag un cyfrif { #a-message-can-only-agree-with-one-count }

Mae adroddiad adeiladu'r wefan hon yn dweud sawl tudalen a rendrwyd a pha mor
hir y cymerodd. Mae ei ysgrifennu fel "Rendered {n} pages in {seconds} seconds"
yn edrych yn ddiniwed ac nid yw'n gyfieithadwy: mae gettext yn dewis un ffurf o
un cyfrif, ac `n` yw'r cyfrif hwnnw. Byddai'n rhaid i'r gair *seconds* gytuno â
rhif nad yw'r peirianwaith lluosog byth yn ei weld.

Y ffordd i'w drwsio yw gwneud yr ail faint yn symbol uned yn hytrach nag yn air,
ac mae symbolau unedau eu hunain wedi'u lleoleiddio: mae catalogau'r wefan hon
yn cario `s`, `с`, `ث`, `שנ׳` a `mp`, ac mae teipograffeg Ffrangeg, Sbaeneg a
Swedeg am gael bwlch cyn y symbol lle nad yw'r Saesneg. Nid busnes y llyfrgell
mo dim o hynny — ond mae sylwi bod angen *dau* gytundeb ar neges yn fusnes iddi,
a'r unig offeryn ar ei gyfer yw ysgrifennu'r neges yn wahanol.

## Mae golygu brawddeg Saesneg yn golygu gramadeg tramor { #editing-an-english-sentence-edits-foreign-grammar }

Arferai'r dudalen gartref ddweud "all ten language editions". Trodd tynnu'r rhif
— golygiad Saesneg un gair, a wnaed am fod y rhif yn dal i heneiddio — oddrych
lluosog yn unigol. Bu'n rhaid i Sbaeneg, Eidaleg, Portiwgaleg, Rwseg, Wcreineg,
Groeg, Iseldireg a Hebraeg oll ail-gytuno'r ferf; roedd angen newid y
rhangymeriad hefyd ar sawl un.

Nid yw golygiad ffynhonnell sy'n darllen fel un dibwys yn Saesneg yn ddibwys i
lawr yr afon. Ei farcio'n fuzzy, sef yr hyn y mae `pybabel update` yn ei wneud,
yw'r mecanwaith sy'n rhoi'r cyfle i bob cyfieithydd sylwi.

## Mae gwahaniaethau anweledig yn goroesi pob copïo-a-gludo { #invisible-differences-survive-every-copy-paste }

Mae'r canllaw'n dyfynnu diagnostig sy'n cynnwys `(nаme)` — dihangfa fwriadol,
oherwydd `а` Cyrilig yw'r nod y mae'n ei enwi, un na all yr un darllenydd ei
wahaniaethu oddi wrth yr un Lladin. Trodd cyfieithwyr y wefan hon y ddihangfa
honno'n nod go iawn **bum gwaith ar wahân**, mewn pum iaith wahanol, gan
gynhyrchu bob tro dudalen a edrychai'n gywir ac a oedd yn anghywir.

Mae'r llyfrgell yn dal hon, a dyma'r rheswm y mae'r diagnosteg wedi'i siapio fel
y mae: caiff daliwr lle y mae ei lythrennau'n cymysgu systemau ysgrifennu ei
[adrodd ddwywaith](internals.md#diagnostics-are-part-of-the-design), unwaith yn
ddarllenadwy ac unwaith wedi'i ddianc, oherwydd mai'r ffurf wedi'i dianc yw'r
unig sillafiad sy'n eu gwahaniaethu. Caiff bwlch di-dor y tu mewn i fachau
cyrliog ei argraffu fesul pwynt cod am yr un rheswm. Mae gwiriwr y catalog yn
gwrthod y neges cyn iddi allu cludo.

## Nid cyfieithiad yw peidio â bod yn wag { #non-empty-is-not-translated }

Mae catalog a sgaffaldwyd â'i msgids wedi'u copïo i'w msgstrs yn pasio pob
gwiriad naïf: nid oes dim yn wag, nid oes dim yn fuzzy, mae'r set negeseuon yn
cyfateb yn union. Cludodd un argraffiad o'r wefan hon felly am sawl awr. Felly
hefyd wyth tudalen o argraffiad arall a oedd yn gopïau beit-union o'r ffynhonnell
Saesneg — sy'n pasio gwiriad sy'n cymharu blociau cod rhyngddynt, oherwydd mai'r
un ffeil ydynt.

Nid yw'r naill na'r llall yn rhywbeth y gall llyfrgell gyfieithu ei weld. Mae'r
ddau'n rhad i'w profi unwaith y gwyddoch am wneud hynny: cymharwch â'r
ffynhonnell a mynnwch wahaniaeth.

## Nid y catalog yw'r unig beth sydd wedi'i gyfieithu { #the-catalog-is-not-the-only-translated-thing }

Nid oedd a wnelo dau fethiant yma ddim â gettext.

Mae cyfieithu pennawd yn newid yr angor a gynhyrchir ohono, felly mae pob dolen
groes-dudalen i mewn i'r adran honno'n torri — yn dawel, yn yr iaith honno'n
unig. Mae'r wefan hon yn pinio'r angor Saesneg ar bob pennawd, ac mae prawf yn
deillio'r rhestr ddisgwyliedig o'r dudalen Saesneg.

Ac mae cynhyrchydd y wefan yn cludo cyfieithiadau rhyngwyneb ar gyfer chwe deg
wyth o ieithoedd, nad yw'n cynnwys Swahili na Gwyddeleg. Heb un nid yw'r
adeiladu'n diraddio i'r Saesneg; mae cynnwys y templed yn methu ac ni ellir
adeiladu'r argraffiad o gwbl. Mae dwy o ffeiliau'r storfa hon ei hun yn bodoli i
lenwi'r bwlch hwnnw.

## Mae gan eich offer chithau fygiau { #your-tools-have-bugs-too }

Ni all y cam CI y mae'r ddogfennaeth hon yn ei argymell ar gyfer dal catalogau
hen, `pybabel update --check`, wneud y gwaith hwnnw i'r un prosiect sy'n
defnyddio `pgettext` neu `npgettext`. Ar Babel 2.18.0 mae'n adrodd bod pob
catalog sydd â `msgctxt` yn hen, ar bob rhediad. Mae'r gymhariaeth yn rhedeg
drwy `Catalog.is_identical`, sy'n chwilio am bob neges yn ôl yr allwedd y
cedwir hi oddi tani — ac ar gyfer neges gyd-destunol y pâr `(id, context)` yw'r
allwedd honno, nad yw `Catalog.get` yn ei derbyn. Nid yw'r chwiliad yn
dychwelyd dim, ac nid yw'r catalogau byth yn cymharu'n gyfartal:

```pycon
>>> from babel.messages.catalog import Catalog
>>> c = Catalog(locale="ja")
>>> c.add("Guide", "ガイド", context="navigation")
<Message 'Guide' (flags: [])>
>>> c.is_identical(c)
False
```

Cafodd ei ganfod yma drwy geisio ei ddefnyddio, ei adrodd i fyny'r afon, ac mae'r
gwiriad amgen [ar y dudalen gynhyrchu](workflow.md#what-ci-gates).

Y wers gyffredinol yw'r un anghyfforddus: mae gât sydd bob amser yn goch yn
waeth na dim gât o gwbl, oherwydd bod tîm yn ei diffodd. Gwiriwch y gall eich
gwiriad CI basio go iawn cyn i chi ymddiried ynddo i fethu.

## At beth y mae'r llyfrgell, mewn un llinell { #what-the-library-is-for-in-one-line }

Crebwyll na all yr un offeryn ei gymryd drosodd yw'r rhan fwyaf o'r dudalen hon.
Yr hyn y *gall* offeryn ei wneud yw gwarantu na all cyfieithiad newid strwythur y
frawddeg y mae'n ei chyfieithu — na all ollwng gwerth, dyfeisio un, ailfformatio
un, na chyrraedd i mewn i'ch gwrthrychau — a gall ddweud hynny mewn brawddeg y
gall y sawl sy'n gorfod ei drwsio weithredu arni. Dyna gyfanrwydd yr hyn y mae'r
llyfrgell hon yn ei addo, a gweddill y wefan hon yw sut y mae'n ei gadw.
