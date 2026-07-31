---
description: "Mkataba wa vishika nafasi kwa yeyote anayehariri faili za .po: kipi unaweza kukibadilisha, kipi lazima ukiache, na jinsi ya kusoma hitilafu."
---

# Kwa watafsiri

Ukurasa huu ni kwa mtu anayehariri katalogi, si kwa mtu anayeandika msimbo. Ni
mfupi kwa makusudi, nao umekusudiwa kuunganishwa au kunakiliwa ndani ya maagizo
ya wafasiri ya mradi wako mwenyewe.

Hakuna kilicho hapa kinachokutaka usome Python. Kila kilicho hapa kinahusu jambo
moja: vipande vya ujumbe vilivyo ndani ya mabano ya mviringo.

## Kishika nafasi ni nini { #what-a-placeholder-is }

Ujumbe ulio katika katalogi waweza kuwa na majina ndani ya mabano ya mviringo:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` ni **kishika nafasi**. Programu inapouonyesha ujumbe huu hukibadilisha
`{name}` kwa thamani inayoitoa yenyewe — jina la mtu, jina la faili, nambari.
Kishika nafasi si neno la kutafsiriwa; ni nafasi iliyoachwa wazi.

Tafsiri yako huingia katika `msgstr`, nayo lazima iihifadhi nafasi hiyo:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Kipi waweza kukibadilisha, na kipi huwezi { #what-you-may-change-and-what-you-may-not }

**Waweza**:

- **Kuhamisha kishika nafasi** mahali popote sarufi ya lugha lengwa
  inapokitaka, hata mwanzoni kabisa mwa ujumbe.
- **Kurudia kishika nafasi** iwapo lugha inahitaji thamani hiyo mara mbili.
- **Kuandika upya kila neno jingine**, pamoja na alama za uakifishaji, nafasi,
  na mpangilio wa sentensi.

**Hupaswi**:

- **Kutafsiri jina lililo ndani ya mabano.** `{name}` hubaki `{name}`, hata
  katika lugha isiyoandika kingine chochote kwa herufi za Kilatini.
- **Kuondoa mabano**, wala kuandika jina bila hayo.
- **Kubadilisha mabano ya ASCII `{` `}` kwa yale ya upana kamili `｛` `｝`.**
  Mbinu nyingi za uingizaji huzalisha maumbo ya upana kamili; hufanana karibu
  kabisa nayo hayafanyi kazi.
- **Kuongeza uumbizaji**, kama vile `{name!r}` au `{amount:.2f}`. Jinsi thamani
  inavyoonyeshwa huamuliwa ndani ya programu, si ndani ya katalogi.
- **Kubuni kishika nafasi** ambacho hakiko ndani ya `msgid`.

Iwapo ujumbe unahitaji thamani ambayo asili haiitoi, huo ni ujumbe ambao
mtengenezaji ndiye anayepaswa kuubadilisha. Sema hivyo badala ya kutafuta njia
ya kuuzunguka.

## Maumbo ya wingi { #plural-forms }

Ujumbe unaohesabu hufika ukiwa na nafasi moja ya `msgstr` kwa kila umbo la
wingi la lugha yako, nayo lugha yako ndiyo huamua ni ngapi — moja kwa Kijapani,
mawili kwa Kijerumani, matatu kwa Kirusi, sita kwa Kiarabu. Jaza kila nafasi
ambayo katalogi hukupa.

Kanuni mbili zinazowatega watu:

- **Nafasi hizo si "umoja, wingi, wingi zaidi".** Kila kielezo humaanisha
  chochote ambacho kanuni ya wingi ya lugha yako husema kinamaanisha. Umbo la
  tatu la Kilatvia ni kwa ajili ya sifuri pekee; la pili la Kislovenia ni kwa
  mbili hasa; Kiwelisi huweka hali ya jumla katika kielezo 0 nao umoja katika
  kielezo 1.
- **Nafasi mbili zaweza kihalali kubeba maandishi yaleyale.** Katika Kituruki,
  Kihungari, Kiajemi na Kibengali nomino hubaki katika umoja baada ya nambari,
  hivyo maumbo yote mawili ya ujumbe unaohesabu ni mfuatano uleule. Hilo ni
  sahihi, si kuteleza kwa kunakili na kubandika.

Kanuni za vishika nafasi zilizo hapo juu hutumika kwa kila umbo peke yake.

## Maingizo ya fuzzy { #fuzzy-entries }

Ingizo lililotiwa alama ya `fuzzy` ni kisio la mashine: mtengenezaji aliubadilisha
ujumbe wa asili, nazo zana zikaoanisha maandishi mapya na tafsiri yako ya zamani
ili uwe na mahali pa kuanzia.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Ingizo la fuzzy **halitumiwi na programu** — huonyesha asili isiyotafsiriwa
badala yake — hadi mtu ayarekebishe maandishi na aiondoe alama ya `fuzzy`.
Vihariri vingi vya PO vina kitufe cha kufanya hivyo hasa.

## Kusoma ujumbe wa kushindwa { #reading-a-failure-message }

Zana hukagua vishika nafasi wakati katalogi inapokusanywa, nao ujumbe
umeandikwa kwa ajili yako badala ya kwa ajili ya mwandishi wa programu.
Kuripoti tu kwamba `{name}` haipo ni njia isiyo na mwisho ilhali unaziona herufi
hizo mbele yako, hivyo pale kishika nafasi kinapoonekana kuwepo kumbe hakipo,
ujumbe husema kwa nini. Dhidi ya asili `Hello {name}`, kila kimoja kati ya hivi
huripotiwa chini ya `translation does not match the source placeholders:`

| Tafsiri yako husema | Sababu inayotolewa |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` haipo (mabano yanayoizunguka si `{` na `}` za ASCII) |
| `こんにちは {{name}}` | `{name}` haipo (imeandikwa `{{name}}`, ambayo ndiyo namna bano halisi hukwepwa) |
| `こんにちは name` | `{name}` haipo (jina huonekana, lakini si ndani ya mabano) |
| `こんにちは {名前}` | `{name}` haipo; `{名前}` haiko ndani ya ujumbe wa chanzo |

Herufi zisizoweza kuonekana hushughulikiwa kwa namna yake. Nafasi isiyokatika
iliyo ndani ya mabano ni kitu ambacho mbinu ya uingizaji huizalisha nacho hakuna
kihariri kinachoionyesha, hivyo ujumbe huichapisha kwa nukta ya msimbo badala ya
kutaja herufi ambayo usingeweza kuipata kamwe:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Jina ambalo herufi zake huchanganya mifumo ya uandishi — hali ya homoglifu,
ambapo `а` ya Kisirili haitofautishiki na ile ya Kilatini — huonyeshwa mara
mbili, mara moja kwa namna inayosomeka na mara moja kwa namna iliyokwepwa,
ambayo ndiyo namna pekee inayozitofautisha hizo mbili:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Utofautishaji uleule hutumika pale jina la Kigiriki au la Kisirili lililoandikwa
kwa mfumo mmoja kabisa linapogongana na jina la chanzo lililo la ASCII, pamoja
na hali ya herufi moja ya `a` ya Kilatini / `а` ya Kisirili.

Ukikutana na mojawapo ya hizi nako kurekebisha hakuko wazi, hatua salama ni
kukifuta kishika nafasi ulichokiandika na kunakili kile kilicho ndani ya
`msgid`.

## Kile ambacho ukaguzi hauwezi kukifanya { #what-the-checks-cannot-do }

Zana huhakiki kwamba vishika nafasi vyako viko sawa. Haiwezi kutambua iwapo
tafsiri ni sahihi, ya asili, au inayofaa kwa muktadha — hilo hubaki kwako wewe
peke yako.

Mambo mawili husaidia kuliko ukaguzi wowote:

- **Soma maoni ya mfasiri.** Mstari unaoanza kwa `#.` juu ya ujumbe ni
  mtengenezaji akikuambia mahali ujumbe unapotokea na maana yake.
- **Uliza kuhusu `msgctxt`.** Neno lilelile linapotokea mara mbili likiwa na
  miktadha tofauti, ni kwa sababu hayo mawili yanahitaji kutafsiriwa kwa namna
  tofauti — "Open" kitufe na "Open" hali, kwa mfano.
