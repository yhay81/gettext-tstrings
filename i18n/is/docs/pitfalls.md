---
description: "Hvað brotnar í raun þegar einn lítill vefur er þýddur á þrjátíu og fimm tungumál, hvað af því safnið getur gripið fyrir þig og hvað ekki."
---

# Fallgryfjur

Þessi vefur er þýddur á þrjátíu og fimm tungumál og hver einasta útgáfa varð
til með því að keyra þá hringrás sem þessi skjölun kennir. Það er lítill texti
á mælikvarða iðnaðarins og dugði samt til að lenda í flestum þeim gildrum sem
gera i18n erfiðara en það sýnist.

Hver kafli hér að neðan er eitthvað sem fór raunverulega úrskeiðis hér,
hvernig það leit út þegar það gerðist, og hvar mörkin liggja milli þess sem
safnið athugar fyrir þig og þess sem er áfram þitt eigið mat.

## Að endurnefna breytu þýðir setningu upp á nýtt { #renaming-a-variable-retranslates-a-sentence }

Msgid-ið er lykill þýðingaskrárinnar og innskeytt nafn er *inni í* því. Að
færa einn fasta upp á einingarsvið og hástafa hann eins og stíll Pythons biður
um — `author` í `AUTHOR` — breytti `Copyright © 2026 {author} · MIT License` í
skilaboð sem engin þýðingaskrá hafði nokkurn tíma séð. Sérhver þýðing þeirrar
línu hefði farið aftur í gegnum fuzzy-hringinn, á öllum tungumálum, fyrir
endurnefningu sem breytti engu sem lesandi gat séð.

Safnið stöðvar þig ekki: báðar ritmyndirnar eru gild nöfn staðgengla. Það sem
það gerir er að gera nafnið *þess virði* að vernda — innskeyting verður að
vera [einfalt nafn](internals.md#from-template-to-msgid), svo að það sem
stendur í lykli þýðingaskrárinnar er orð sem þýðandi getur lesið, ekki segð.

Spegilmyndin af þessu er örugg í eðli sínu. Umbreytingar og sniðlýsingar eru
ekki hluti af msgid-inu, svo að herða `{amount:,.2f}` í `{amount:,.0f}` breytir
engum lykli og ógildir enga þýðingu, hvergi.

## `nplurals=2` þýðir ekki tvo ólíka strengi { #nplurals-2-does-not-mean-two-different-strings }

Tyrkneska, ungverska, persneska og bengalska lýsa allar yfir tveimur
fleirtölumyndum, og í öllum fjórum eru myndirnar tvær í töldum skilaboðum með
fullum rétti *sami strengurinn* — nafnorðið stendur í eintölu á eftir
töluorði, svo `{n} sayfa` á jafnt við um eina síðu og tíu. Yfirlesari sem
„lagfærir“ tvítekninguna eyðileggur þýðinguna.

Öfug mistök eru alveg jafn auðveld. Þriðja mynd lettneskunnar er til **fyrir
núllið eitt**; önnur mynd slóvenskunnar er **tvítala**, fyrir nákvæmlega tvö;
síðasta mynd rúmenskunnar krefst orðsins `de` sem fyrstu tvær mega ekki hafa.
Að fylla þau hólf með eintölu og fleirtölu skilar þýðingaskrá sem er aðeins
röng fyrir fjölda sem enginn prófar.

Verra er að *röð* hólfanna er ekki merkingarleg. Velskan raðar sínum fimm
myndum þannig að `msgstr[0]` er almenna tilvikið og `msgstr[1]` er eintalan.
Að fylla þau í augljósri röð setur eintöluna þangað sem öll ótalin skilaboð
finna hana.

Safnið tekur ekkert af þessu að sér, og það er einmitt kjarninn: fleirtöluregla
markmálsins býr í haus þess eigin þýðingaskrár, og
[sammengis-/sniðmengisreglan](spec.md) leyfir þýðingu að hafa fleiri myndir en
frumtextinn, eða færri. Það sem safnið athugar er það eina sem hægt er að
athuga án þess að kunna málið — að hver mynd haldi þeim staðgenglum sem hún
þarf.

## Tvær myndir geta verið eins af gildri ástæðu { #two-forms-can-be-identical-for-a-reason }

Írskan hefur fimm fleirtölumyndir og í byggingarskýrslu þessa vefs eru nokkrar
þeirra ritaðar eins. Það er ekki afritunarslys: *leathanach* byrjar á `l`, og
hvorug þeirra framstöðubreytinga sem írsk töluorð kalla fram er rituð á `l`.
Myndirnar vinna samt raunverulegt verk — stofninn víxlast milli *leathanach*
og *leathanaigh*, og fjöldi yfir tíu fer aftur í eintöluna — en ekkert
nafnorð í merkingunni „síða“ myndi sýna andstæðuna.

Sérhver athugun sem flaggar endurteknum myndum sem grunsamlegum mun flagga
réttri írsku. Manneskja sem kann málið er eini yfirlesarinn fyrir þetta.

## Skilaboð geta aðeins samræmst einum fjölda { #a-message-can-only-agree-with-one-count }

Byggingarskýrsla þessa vefs segir hversu margar síður voru birtar og hversu
langan tíma það tók. Að skrifa það sem „Rendered {n} pages in {seconds}
seconds“ virðist meinlaust og er óþýðanlegt: gettext velur eina mynd út frá
einum fjölda, og sá fjöldi er `n`. Orðið *seconds* þyrfti að samræmast tölu
sem fleirtöluvélin sér aldrei.

Lausnin er að gera seinni stærðina að einingartákni fremur en orði, og
einingartákn eru sjálf staðfærð: þýðingaskrár þessa vefs bera `s`, `с`, `ث`,
`שנ׳` og `mp`, og frönsk, spænsk og sænsk prentvenja vill bil á undan
tákninu þar sem enskan vill það ekki. Ekkert af því er á ábyrgð
safnsins — en að taka eftir því að skilaboð þurfi *tvenns konar* samræmi er
það, og eina tólið til þess er að skrifa skilaboðin öðruvísi.

## Að breyta enskri setningu breytir erlendri málfræði { #editing-an-english-sentence-edits-foreign-grammar }

Forsíðan sagði áður „all ten language editions“. Að fjarlægja töluna — eins
orðs breyting á ensku, gerð af því að talan úreltist í sífellu — gerði
fleirtölufrumlag að eintölu. Spænska, ítalska, portúgalska, rússneska,
úkraínska, gríska, hollenska og hebreska þurftu allar að samræma sögnina upp á
nýtt; nokkrar þurftu líka að breyta lýsingarhættinum.

Breyting á frumtexta sem virðist léttvæg á ensku er ekki léttvæg lengra niðri
í keðjunni. Að merkja hana fuzzy, sem er einmitt það sem `pybabel update`
gerir, er kerfið sem gefur hverjum þýðanda tækifæri til að taka eftir henni.

## Ósýnilegur munur lifir af hverja afritun { #invisible-differences-survive-every-copy-paste }

Handbókin vitnar í greiningarskilaboð sem innihalda `(nаme)` — vísvitandi
escape-ritun, því stafurinn sem hún nefnir er kýrillískt `а` sem enginn
lesandi greinir frá því latneska. Þýðendur þessa vefs breyttu þeirri
escape-ritun í raunverulega stafinn **fimm aðskilin skipti**, á
fimm ólíkum tungumálum, og bjuggu í hvert sinn til síðu sem leit rétt út og
var röng.

Þetta grípur safnið hins vegar, og það er ástæðan fyrir því að
greiningarskilaboðin eru mótuð eins og þau eru: staðgengill sem blandar
ritkerfum í stöfum sínum er
[tilkynntur tvisvar](internals.md#diagnostics-are-part-of-the-design), einu
sinni læsilega og einu sinni með escape-ritun, því escape-myndin er eina
ritmyndin sem greinir þá að. Fast bil inni í slaufusvigum er prentað með
kóðapunkti af sömu ástæðu. Þýðingaskrárathugunin hafnar skilaboðunum áður en
þau komast í dreifingu.

## Ekki tómt er ekki þýtt { #non-empty-is-not-translated }

Þýðingaskrá sem er stofnuð með msgid-in afrituð yfir í msgstr-in stenst hverja
einfalda athugun: ekkert er tómt, ekkert er fuzzy, skilaboðamengið stemmir
nákvæmlega. Ein útgáfa þessa vefs fór þannig í dreifingu í nokkrar
klukkustundir. Sömuleiðis átta síður í annarri útgáfu sem voru bætaeins afrit
af enska frumtextanum — sem stenst athugun sem ber saman kóðablokkir milli
þeirra, því þær eru sama skráin.

Hvorugt er eitthvað sem þýðingasafn getur séð. Hvort tveggja er ódýrt að prófa
þegar maður veit að þess þarf: berðu saman við frumtextann og krefstu munar.

## Þýðingaskráin er ekki það eina sem er þýtt { #the-catalog-is-not-the-only-translated-thing }

Tvær bilanir hér áttu ekkert skylt við gettext.

Að þýða fyrirsögn breytir akkerinu sem búið er til út frá henni, svo hver
tengill milli síðna inn í þann kafla brotnar — hljóðlaust, og aðeins á því
tungumáli. Þessi vefur festir enska akkerið á hverja fyrirsögn, og próf leiðir
væntanlega listann af ensku síðunni.

Og vefsmiðurinn fylgir með viðmótsþýðingar fyrir sextíu og átta tungumál, sem
ná hvorki yfir svahílí né írsku. Án þeirra hrörnar byggingin ekki yfir í ensku;
innlestur sniðmátsins mistekst og útgáfuna er alls ekki hægt að byggja. Tvær
skrár í þessari geymslu eru til þess eins að fylla það gat.

## Tólin þín eru líka gölluð { #your-tools-have-bugs-too }

CI-skrefið sem þessi skjölun mælir með til að grípa úreltar þýðingaskrár,
`pybabel update --check`, ræður ekki við það verk í neinu verkefni sem notar
`pgettext` eða `npgettext` — það tilkynnir hverja þýðingaskrá sem inniheldur
`msgctxt` sem úrelta, í hverri einustu keyrslu, vegna galla í því hvernig
samanburðurinn flettir skilaboðum upp. Þetta fannst hér við tilraun til að
nota það, var tilkynnt til upprunaverkefnisins og er
[lýst til fulls ásamt lausninni](workflow.md#what-ci-gates).

Almenna lærdóminn er óþægilegt að draga: hlið sem er alltaf rautt er verra en
ekkert hlið, því teymi slekkur á því. Gakktu úr skugga um að CI-athugunin þín
geti raunverulega staðist áður en þú treystir henni til að falla.

## Til hvers safnið er, í einni línu { #what-the-library-is-for-in-one-line }

Mestur hluti þessarar síðu er mat sem ekkert tól getur tekið að sér. Það sem
tól *getur* gert er að ábyrgjast að þýðing geti ekki breytt byggingu
setningarinnar sem hún þýðir — geti ekki sleppt gildi, búið eitt til,
endursniðið eitt eða teygt sig inn í hlutina þína — og að það geti sagt frá
því í setningu sem sá sem þarf að laga hana getur unnið eftir. Það er allt og
sumt sem þetta safn lofar, og afgangur þessa vefs er hvernig það stendur við
það.
