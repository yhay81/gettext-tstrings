---
description: "Trettio år av gettext, två PEP:ar med tio års mellanrum, och stdlib-diskussionen som stängdes som not-planned: varför det här biblioteket finns, med länkar till källorna."
---

# Bakgrund

Det här biblioteket sitter vid mötespunkten mellan två långa berättelser — en
om hur programvara översätts, en om hur Python interpolerar strängar — som
till slut korsades 2025 och sedan stannade av exakt vid den punkt där en
liten, omsorgsfull konvention behövdes. Den här sidan berättar båda
berättelserna, med länkar till källorna, eftersom designbesluten på den här
webbplatsen är lättare att bedöma när du kan se frågorna de besvarar.

## gettext-ekosystemet { #the-gettext-ecosystem }

[GNU gettext] har varit sättet fri programvara översätts på sedan mitten av
1990-talet: markera strängarna i koden, extrahera dem till en mall, ge
översättarna en katalogfil per språk, kompilera, läs in vid körning. Runt det
kretsloppet växte ett helt ekosystem — PO-redigerare, granskningsflöden och
översättningsplattformar som alla talar samma filformat — och Python har
levererat en [`gettext`-modul][stdlib-gettext] i sitt standardbibliotek i mer
än två decennier. Körningshalvan av översättning var aldrig problemet.

Den olösta halvan var alltid *hur katalogsträngen ser ut*. Ett
`%(name)s`-meddelande räcker översättarna printf-syntax som en raderad
bokstav förvandlar till en produktionskrasch; ett `.format()`-meddelande ger
katalogen attributåtkomst till levande objekt. ([Varför
t-strings](comparison.md) går igenom båda, med felen till beskådan.) Och
f-strings — syntaxen mest Python-kod numera föredrar — kan inte delta alls:
när något bibliotek ser en är den redan en färdig sträng. Folk försöker ändå,
ofta nog att Babels ärendehanterare samlar försöken
([#594][babel-594], [#715][babel-715]); felet är strukturellt, inte en
saknad funktion.

## Två PEP:ar, tio år isär { #two-peps-ten-years-apart }

2015 skrev Alyssa Coghlan och Nick Humrich [PEP 501], som föreslog
interpolationsmallar vars uttalade första motivering var i18n — "providing a
cleaner syntax for i18n translation", med PEP:ens egna ord. Förslaget
sköts upp, delvis för att diskussionen visade att i18n-fallet bar på
betydande extra överväganden som enklare användningsfall inte gjorde.

Ett decennium senare återupplivade [PEP 750] — av Jim Baker, Guido van
Rossum, Paul Everitt, Koudai Aono, Lysandros Nikolaou och Dave Peck — idén
som t-strings, blev [accepterad i april 2025][sc-resolution] och levererades
i [Python 3.14] i oktober 2025. PEP 501 drogs sedan tillbaka till dess
förmån. En detalj spelar roll för den här sidan: i18n finns *inte* bland
PEP 750:s uttalade motiveringar. PEP:en generaliserade mekanismen — en
malltyp vilket bibliotek som helst kan konsumera — och lämnade
översättningsfrågan exakt där PEP 501 hade parkerat den tio år tidigare:
öppen.

Så från och med Python 3.14 hade språket precis den datastruktur en
meddelandekatalog behöver, och ingen konvention för att använda den som en.

## Stdlib-diskussionen { #the-stdlib-discussion }

Två månader innan 3.14 levererades föreslog Adrian Mönnich (ThiefMaster, en
underhållare av Indico-projektet) att gapet skulle slutas i själva
standardbiblioteket: tråden [Support t-strings in gettext][discuss-thread] på
discuss.python.org, öppnad i augusti 2025, kom med en fungerande
[pull request][cpython-pr] som lade till t-string-stöd i både `gettext` och
`pygettext`.

Tråden är värd att läsa i sin helhet, eftersom den lyfter fram varje svår
fråga det här biblioteket senare fick besvara:

- **Vad får en interpolation vara?** Enbart ett enkelt namn, eller attribut
  och anrop med ett härlett platshållarnamn? Varje svar byter bekvämlighet
  mot msgid-stabilitet och katalogsäkerhet.
- **Vad kräver pluralformer,** när målspråkets pluralsystem skiljer sig från
  källans?
- **Är gettext ens rätt mål?** Barry Warsaw — som under PEP 750:s utveckling
  hade hävdat att t-strings inte passade bra för i18n — pekade på sitt
  [`flufl.i18n`][flufl-i18n] och dess `$`-strängstil som det vänligare
  verktyget; andra argumenterade för att lämna gettext helt till förmån för
  nyare system som [Fluent].
- **Och metafrågan:** vad standardbiblioteket än levererar kan det i
  praktiken aldrig ändras. En konvention med så här många öppna val är en
  riskabel sak att frysa på första försöket.

Ingen konsensus uppstod. CPython-ärendet
[stängdes som "not planned"][cpython-issue] och pull requesten stängdes
osammanfogad i oktober 2025, dagar efter 3.14:s utgivning. Förmågan fanns i
språket; konventionen hade inget hem.

## Varför ett paket, först { #why-a-package-first }

Det är gapet det här projektet valde att fylla utanför standardbiblioteket,
på ett medvetet vad: en konvention mognar snabbare där den kan versioneras
fritt och förtjäna adoption fall för fall, och standardbiblioteket — som
måste ha rätt första gången — är där en konvention bör *hamna*, inte där den
bör arbetas fram.

Konkret har varje omtvistad fråga i tråden ett nedskrivet svar här, var och
en på sin egen sida:

- Interpolationer är **enbart enkla namn**, så att msgid:n förblir stabila
  och meningsfulla — [guiden](guide.md#safety-and-scope) visar regeln,
  [Så fungerar det](internals.md#from-template-to-msgid) skälen.
- **Formatering hålls helt utanför katalogen**
  ([Varför t-strings](comparison.md)).
- **Pluralformer** följer en unions-/snittregel som låter ett målspråks
  pluralsystem skilja sig från källans ([spec §4](spec.md)).
- En trasig katalog **faller tillbaka i stället för att krascha**, i enlighet
  med gettexts eget kontrakt
  ([guiden](guide.md#what-happens-when-a-catalog-is-wrong)).
- Och hela konventionen är en [versionerad specifikation](spec.md) med en
  maskinläsbar konformitetssvit — skriven så att en annan implementation,
  inklusive en framtida i standardbiblioteket, skulle kunna anta den
  oförändrad och interoperera.

Diskussionen har inte tagit slut, och det här projektet är en deltagare i
den, inte en dom över den. Om du har produktionserfarenhet av gettext som
berör de här valen är [samma tråd][discuss-thread] och det här förrådets
[Discussions][gh-discussions] där diskussionen fortsätter.

## Tidslinje { #timeline }

| När | Vad hände |
| --- | --- |
| mitten av 1990-talet | GNU gettext etablerar PO/POT/MO-arbetsflödet som översättare och plattformar fortfarande talar. |
| 2015 | [PEP 501] föreslår interpolationsmallar, med i18n som sin första motivering; uppskjuten. |
| 2016 | f-strings levereras i Python 3.6 — interpolation får sin syntax, och översättning kan inte använda den. |
| jul 2024 | [PEP 750] föreslår t-strings. |
| apr 2025 | PEP 750 [accepteras][sc-resolution]; PEP 501 dras tillbaka till dess förmån. |
| aug 2025 | Tråden [Support t-strings in gettext][discuss-thread] öppnas, med en stdlib-[pull request][cpython-pr]. |
| okt 2025 | [Python 3.14] levererar t-strings; stdlib-ärendet stängs som [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` levereras som en alfa, med [spec v1](spec.md) och dess konformitetssvit. |

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
