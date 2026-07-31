---
description: "Kile ambacho kutafsiri tovuti moja ndogo katika lugha thelathini na tano huvunja kwa hakika, ni yapi kati ya hayo maktaba inaweza kuyanasa kwa ajili yako, na yapi haiwezi."
---

# Mitego

Tovuti hii imetafsiriwa katika lugha thelathini na tano, na kila toleo
lilizalishwa kwa kuendesha mzunguko ambao nyaraka hizi hufundisha. Kwa vipimo
vya sekta hii ni mkusanyiko mdogo wa maandishi, na hata hivyo ulitosha kuingia
katika mingi kati ya mitego inayoifanya i18n kuwa ngumu kuliko inavyoonekana.

Kila sehemu iliyo hapa chini ni jambo lililokwenda kombo hapa kwa kweli, jinsi
lilivyoonekana wakati huo, na mahali mstari unapopita kati ya kile maktaba
inachokukagulia na kile kinachobaki kuwa hukumu yako.

## Kubadili jina la kigezo hutafsiri sentensi upya { #renaming-a-variable-retranslates-a-sentence }

msgid ndio ufunguo wa katalogi, nalo jina lililoingizwa liko *ndani* yake.
Kuhamisha kigezo kimoja kisichobadilika hadi ngazi ya moduli na kukiandika kwa
herufi kubwa jinsi mtindo wa Python unavyotaka — `author` kuwa `AUTHOR` —
kuligeuza `Copyright © 2026 {author} · MIT License` kuwa ujumbe ambao hakuna
katalogi iliyowahi kuuona. Kila tafsiri ya mstari huo ingelazimika kupitia
mzunguko wa fuzzy tena, katika kila lugha, kwa ajili ya kubadili jina ambako
hakukubadilisha chochote ambacho msomaji angeweza kukiona.

Maktaba haitakuzuia: tahajia zote mbili ni majina halali ya vishika nafasi.
Kinachofanya ni kulifanya jina *listahili* kulindwa — uingizaji lazima uwe
[jina rahisi](internals.md#from-template-to-msgid), hivyo kilicho ndani ya
ufunguo wa katalogi ni neno ambalo mfasiri anaweza kulisoma, si usemi.

Kesi ya kinyume ni salama kwa muundo wenyewe. Ubadilishaji na maainisho ya
umbizo si sehemu ya msgid, hivyo kukaza `{amount:,.2f}` kuwa `{amount:,.0f}`
hakubadilishi ufunguo wowote wala hakubatilishi tafsiri yoyote popote.

## `nplurals=2` haimaanishi mifuatano miwili tofauti { #nplurals-2-does-not-mean-two-different-strings }

Kituruki, Kihungari, Kiajemi na Kibengali vyote hutangaza maumbo mawili ya
wingi, na katika lugha zote nne maumbo mawili ya ujumbe unaohesabu kihalali ni
*mfuatano uleule* — nomino hubaki katika umoja baada ya nambari, hivyo
`{n} sayfa` ni sahihi kwa ukurasa mmoja na kwa kurasa kumi. Mkaguzi
"anayerekebisha" urudufu huo huivunja tafsiri.

Kosa la kinyume ni rahisi vivyo hivyo. Umbo la tatu la Kilatvia lipo kwa ajili
ya **sifuri pekee**; la pili la Kislovenia ni **uwili**, kwa mbili hasa; umbo
la mwisho la Kiromania linahitaji neno `de` ambalo mawili yake ya kwanza
hayapaswi kuwa nalo. Kujaza nafasi hizo kwa umbo la umoja na la wingi
huzalisha katalogi ambayo ni batili kwa idadi zile tu ambazo hakuna mtu
huzijaribu.

Vibaya zaidi, *mpangilio* wa nafasi hizo si wa kimaana. Kiwelisi huyapanga
maumbo yake matano hivi kwamba `msgstr[0]` ndilo umbo la jumla nalo
`msgstr[1]` ndilo la umoja. Kuyajaza kwa mfuatano ulio dhahiri huweka umbo la
umoja pale ambapo kila ujumbe usiohesabu utalipata.

Maktaba haichukui lolote kati ya haya juu yake, na hilo ndilo lengo: kanuni ya
wingi ya lugha lengwa hukaa katika kichwa cha katalogi yake yenyewe, nayo
[kanuni ya muungano/mwingiliano](spec.md) huruhusu tafsiri kuwa na maumbo mengi
zaidi, au machache zaidi, kuliko chanzo. Kinachokaguliwa ni kitu pekee
kinachoweza kukaguliwa bila kuijua lugha — kwamba kila umbo huhifadhi vishika
nafasi linavyohitaji.

## Maumbo mawili yanaweza kufanana kwa sababu { #two-forms-can-be-identical-for-a-reason }

Kiayalandi kina maumbo matano ya wingi, na katika ripoti ya ujenzi ya tovuti
hii kadhaa kati yake huandikwa vilevile. Hilo si kosa la kunakili na kubandika:
*leathanach* huanza na `l`, nayo mabadiliko mawili ya mwanzo ambayo nambari za
Kiayalandi huyachochea hayaandikwi kamwe juu ya `l`. Maumbo hayo bado hufanya
kazi halisi — shina hupishana kati ya *leathanach* na *leathanaigh*, nazo idadi
zilizo zaidi ya kumi hurejea kwenye umoja — lakini hakuna nomino yenye maana ya
"ukurasa" ambayo ingeonyesha tofauti hiyo.

Ukaguzi wowote unaotia alama maumbo yanayojirudia kuwa ya kutiliwa shaka
utakitia alama Kiayalandi kilicho sahihi. Mtu anayeijua lugha ndiye mkaguzi
pekee kwa jambo hili.

## Ujumbe unaweza kukubaliana na idadi moja tu { #a-message-can-only-agree-with-one-count }

Ripoti ya ujenzi ya tovuti hii husema kurasa ngapi zilionyeshwa na ilichukua
muda gani. Kuiandika kama "Rendered {n} pages in {seconds} seconds" huonekana
kuwa jambo lisilo na madhara, kumbe hakutafsiriki: gettext huchagua umbo moja
kutokana na idadi moja, nayo idadi hiyo ni `n`. Neno *seconds* lingelazimika
kukubaliana na nambari ambayo mfumo wa wingi hauioni kamwe.

Suluhisho ni kukifanya kiasi cha pili kuwa alama ya kipimo badala ya neno, nazo
alama za vipimo zenyewe hutafsiriwa: katalogi za tovuti hii hubeba `s`, `с`,
`ث`, `שנ׳` na `mp`, nayo taipografia ya Kifaransa, Kihispania na Kiswidi hutaka
nafasi kabla ya alama pale ambapo Kiingereza hakitaki. Hakuna hata mojawapo ya
hayo iliyo shughuli ya maktaba — lakini kutambua kwamba ujumbe unahitaji
makubaliano *mawili* ni shughuli yake, nacho kifaa pekee cha kufanya hivyo ni
kuuandika ujumbe kwa namna tofauti.

## Kuhariri sentensi ya Kiingereza huhariri sarufi ya kigeni { #editing-an-english-sentence-edits-foreign-grammar }

Ukurasa wa mwanzo hapo awali ulisema "all ten language editions". Kuondoa
nambari — uhariri wa neno moja katika Kiingereza, uliofanywa kwa sababu nambari
hiyo iliendelea kupitwa na wakati — kuligeuza kiima cha wingi kuwa cha umoja.
Kihispania, Kiitaliano, Kireno, Kirusi, Kiukreni, Kigiriki, Kiholanzi na
Kiebrania vyote vililazimika kukikubalisha kitenzi upya; kadhaa vilihitaji
shirikishi kibadilishwe pia.

Uhariri wa chanzo unaosomeka kama wa kawaida katika Kiingereza si wa kawaida
kwa walio chini ya mkondo. Kuutia alama ya fuzzy, jambo ambalo `pybabel update`
hulifanya, ndiyo mbinu inayompa kila mfasiri nafasi ya kulitambua.

## Tofauti zisizoonekana hunusurika kila kunakili na kubandika { #invisible-differences-survive-every-copy-paste }

Mwongozo hunukuu uchunguzi wa hitilafu wenye `(nаme)` — ukwepaji wa makusudi,
kwa sababu herufi ambayo ukwepaji huo huitaja ni `а` ya Kisirili ambayo hakuna
msomaji anayeweza kuitofautisha na ile ya Kilatini. Wafasiri wa tovuti hii
waligeuza ukwepaji huo kuwa herufi halisi **mara tano tofauti**, katika lugha
tano tofauti, kila mara wakizalisha ukurasa ulioonekana sahihi kumbe ulikuwa na
kasoro.

Huu ndio maktaba huunasa, nayo ndiyo sababu uchunguzi wa hitilafu umeundwa
jinsi ulivyo: kishika nafasi ambacho herufi zake huchanganya mifumo ya uandishi
[huripotiwa mara mbili](internals.md#diagnostics-are-part-of-the-design), mara
moja kwa namna inayosomeka na mara moja kwa namna iliyokwepwa, kwa sababu namna
iliyokwepwa ndiyo tahajia pekee inayozitofautisha. Nafasi isiyokatika iliyo
ndani ya mabano huchapishwa kwa nukta ya msimbo kwa sababu ileile. Kikaguzi cha
katalogi huukataa ujumbe huo kabla haujaweza kusafirishwa.

## Kutokuwa tupu si kutafsiriwa { #non-empty-is-not-translated }

Katalogi iliyojengwa kiunzi kwa kunakili msgid zake ndani ya msgstr hupita kila
ukaguzi wa kijuujuu: hakuna kilicho tupu, hakuna kilicho fuzzy, seti ya jumbe
hulingana kabisa. Toleo moja la tovuti hii lilisafirishwa hivyo kwa saa kadhaa.
Vivyo hivyo kurasa nane za toleo jingine ambazo zilikuwa nakala zenye baiti
zilezile za chanzo cha Kiingereza — jambo linalopita ukaguzi unaolinganisha
vizuizi vya msimbo kati ya hivyo viwili, kwa sababu ni faili lilelile.

Wala hakuna kati ya haya mawili ambalo maktaba ya tafsiri inaweza kuliona. Yote
mawili ni rahisi kuyajaribu mara tu unapojua kufanya hivyo: linganisha dhidi ya
chanzo na udai tofauti.

## Katalogi si kitu pekee kinachotafsiriwa { #the-catalog-is-not-the-only-translated-thing }

Matukio mawili ya kushindwa hapa hayakuhusiana kabisa na gettext.

Kutafsiri kichwa cha habari hubadilisha nanga inayotokana nacho, hivyo kila
kiungo cha kuvuka kurasa kinachoingia katika sehemu hiyo huvunjika —
kimyakimya, katika lugha hiyo pekee. Tovuti hii hubandika nanga ya Kiingereza
kwenye kila kichwa, nalo jaribio hutokeza orodha inayotarajiwa kutoka ukurasa
wa Kiingereza.

Nacho kizalishaji cha tovuti husambaza tafsiri za kiolesura kwa lugha sitini na
nane, ambazo hazijumuishi Kiswahili wala Kiayalandi. Bila hizo ujenzi haurudi
nyuma hadi Kiingereza; ujumuishaji wa kiolezo hushindwa nalo toleo haliwezi
kujengwa kabisa. Faili mbili za hazina hii yenyewe zipo ili kuziba pengo hilo.

## Zana zako nazo zina hitilafu { #your-tools-have-bugs-too }

Hatua ya CI ambayo nyaraka hizi hupendekeza kwa kunasa katalogi zilizopitwa na
wakati, `pybabel update --check`, haiwezi kufanya kazi hiyo kwa mradi wowote
unaotumia `pgettext` au `npgettext` — huripoti kila katalogi yenye `msgctxt`
kuwa imepitwa na wakati, kila inapoendeshwa, kwa sababu ya hitilafu katika
jinsi ulinganisho unavyotafuta jumbe. Ilipatikana hapa kwa kujaribu kuitumia,
ikaripotiwa kwa watengenezaji walio juu ya mkondo, nayo [imeelezwa kwa ukamilifu
pamoja na njia ya kuizunguka](workflow.md#what-ci-gates).

Funzo la jumla ndilo lisilopendeza: kizuizi kilicho chekundu daima ni kibaya
kuliko kutokuwa na kizuizi kabisa, kwa sababu timu hukizima. Hakikisha kwamba
ukaguzi wako wa CI unaweza kweli kupita kabla ya kuuamini kwamba utashindwa.

## Maktaba ni ya nini, kwa mstari mmoja { #what-the-library-is-for-in-one-line }

Sehemu kubwa ya ukurasa huu ni hukumu ambayo hakuna zana inayoweza kuichukua.
Kile ambacho zana *inaweza* kufanya ni kuhakikisha kwamba tafsiri haiwezi
kubadilisha muundo wa sentensi inayoitafsiri — haiwezi kudondosha thamani,
kubuni mpya, kuumbiza upya, wala kuingia ndani ya vitu vyako — na kwamba
inaweza kusema hivyo kwa sentensi ambayo mtu anayepaswa kurekebisha anaweza
kuitendea kazi. Hiyo ndiyo ahadi yote ya maktaba hii, nayo sehemu iliyobaki ya
tovuti hii ni jinsi inavyoitunza.
