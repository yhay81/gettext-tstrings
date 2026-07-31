---
description: "Trīsdesmit gadi gettext, divi PEP ar desmit gadu starpību un standarta bibliotēkas diskusija, kas noslēdzās kā not-planned: kāpēc šī bibliotēka pastāv, ar saitēm uz avotiem."
---

# Priekšvēsture

Šī bibliotēka atrodas divu garu stāstu satikšanās vietā — viens ir par to, kā
programmatūra tiek tulkota, otrs par to, kā Python interpolē virknes —, kuri
beidzot krustojās 2025. gadā un tad apstājās tieši tajā punktā, kur bija
vajadzīga maza, rūpīga konvencija. Šī lapa izstāsta abus stāstus ar saitēm uz
avotiem, jo šīs vietnes dizaina lēmumus ir vieglāk novērtēt, kad redzami
jautājumi, uz kuriem tie atbild.

## gettext ekosistēma { #the-gettext-ecosystem }

Kopš 1990. gadu vidus [GNU gettext] ir tas, kā tiek tulkota brīvā
programmatūra: atzīmē virknes kodā, ekstrahē tās veidnē, iedod tulkotājiem
vienu kataloga failu katrai valodai, kompilē, ielādē izpildlaikā. Ap šo ciklu
izauga vesela ekosistēma — PO redaktori, pārskatīšanas darbplūsmas un
tulkošanas platformas, kas visas runā vienā un tajā pašā faila formātā —, un
Python savā standarta bibliotēkā vairāk nekā divas desmitgades piegādā
[`gettext` moduli][stdlib-gettext]. Tulkošanas izpildlaika puse nekad nebija
problēma.

Neatrisinātā puse vienmēr bija *tas, kā izskatās kataloga virkne*. Ziņojums ar
`%(name)s` iedod tulkotājiem printf sintaksi, ko viens nodzēsts burts pārvērš
par avāriju produkcijā; ziņojums ar `.format()` iedod katalogam piekļuvi dzīvu
objektu atribūtiem. ([Kāpēc t-virknes](comparison.md) izstaigā abus, ar
kļūmēm redzamā vietā.) Bet f-virknes — sintakse, ko lielākā daļa Python koda
tagad izvēlas — nevar piedalīties nemaz: brīdī, kad kāda bibliotēka to
ierauga, tā jau ir pabeigta virkne. Cilvēki tomēr mēģina, un tik bieži, ka
Babel problēmu izsekotājs šos mēģinājumus savāc kopā
([#594][babel-594], [#715][babel-715]); kļūme ir strukturāla, nevis trūkstoša
iespēja.

## Divi PEP ar desmit gadu starpību { #two-peps-ten-years-apart }

2015. gadā Alyssa Coghlan un Nick Humrich uzrakstīja [PEP 501], piedāvājot
interpolācijas veidnes, kuru pirmā deklarētā motivācija bija i18n — “providing
a cleaner syntax for i18n translation”, kā teikts pašā PEP. Priekšlikums tika
atlikts, daļēji tāpēc, ka diskusija parādīja: i18n gadījums nes līdzi
ievērojamus papildu apsvērumus, kādu vienkāršākiem lietojumiem nav.

Desmit gadus vēlāk [PEP 750] — no Jim Baker, Guido van Rossum, Paul Everitt,
Koudai Aono, Lysandros Nikolaou un Dave Peck — atdzīvināja ideju kā t-virknes,
tika [pieņemts 2025. gada aprīlī][sc-resolution] un nonāca
[Python 3.14] versijā 2025. gada oktobrī. PEP 501 tad tika atsaukts par labu
tam. Šai lapai svarīga ir viena detaļa: i18n *nav* starp PEP 750 deklarētajām
motivācijām. PEP vispārināja mehānismu — veidnes tipu, ko var patērēt jebkura
bibliotēka — un atstāja tulkošanas jautājumu tieši tur, kur PEP 501 to bija
nolicis desmit gadus agrāk: atvērtu.

Tātad no Python 3.14 valodā bija tieši tā datu struktūra, kāda ziņojumu
katalogam vajadzīga, un nekādas konvencijas, kā to par tādu izmantot.

## Standarta bibliotēkas diskusija { #the-stdlib-discussion }

Divus mēnešus pirms 3.14 iznākšanas Adrian Mönnich (ThiefMaster, viens no
Indico projekta uzturētājiem) piedāvāja aizvērt šo plaisu pašā standarta
bibliotēkā: pavediens [Support t-strings in gettext][discuss-thread] vietnē
discuss.python.org, atvērts 2025. gada augustā, nāca kopā ar strādājošu
[pull request][cpython-pr], kas pievieno t-virkņu atbalstu gan `gettext`, gan
`pygettext`.

Pavedienu ir vērts izlasīt pilnībā, jo tas izceļ katru grūto jautājumu, uz ko
šai bibliotēkai vēlāk nācās atbildēt:

- **Kas drīkst būt interpolācija?** Tikai vienkāršs nosaukums vai arī atribūti
  un izsaukumi ar atvasinātu viettura nosaukumu? Katra atbilde maina ērtumu
  pret msgid stabilitāti un kataloga drošību.
- **Ko prasa daudzskaitļa formas,** kad mērķa valodas daudzskaitļa sistēma
  atšķiras no avota valodas sistēmas?
- **Vai gettext vispār ir pareizais mērķis?** Barry Warsaw — kurš PEP 750
  izstrādes laikā bija apgalvojis, ka t-virknes i18n nav labi piemērotas —
  norādīja uz savu [`flufl.i18n`][flufl-i18n] un tā `$`-virkņu stilu kā
  draudzīgāku rīku; citi iestājās par gettext pilnīgu pamešanu par labu
  jaunākām sistēmām, tādām kā [Fluent].
- **Un meta-jautājums:** lai ko standarta bibliotēka piegādātu, to pēc tam
  praktiski nekad nevar mainīt. Konvenciju ar tik daudz atvērtām izvēlēm ir
  riskanti iesaldēt jau pirmajā mēģinājumā.

Vienprātība neizveidojās. CPython problēmziņojums tika
[aizvērts kā “not planned”][cpython-issue], un pull request 2025. gada
oktobrī, dažas dienas pēc 3.14 laidiena, tika aizvērts nesapludināts. Iespēja
valodā bija; konvencijai nebija mājvietas.

## Kāpēc vispirms pakotne { #why-a-package-first }

Šī ir tā plaisa, ko šis projekts izvēlējās aizpildīt no ārpuses standarta
bibliotēkai, ar apzinātu likmi: konvencija nobriest ātrāk tur, kur tā var
brīvi versionēties un iekarot lietotājus gadījumu pēc gadījuma, bet standarta
bibliotēka — kurai jābūt pareizai jau pirmajā reizē — ir vieta, kur konvencijai
*būtu jānonāk*, nevis kur tā būtu jāizstrādā.

Konkrēti: katram pavedienā apstrīdētajam jautājumam šeit ir pierakstīta
atbilde, katra savā lapā:

- Interpolācijas ir **tikai vienkārši nosaukumi**, lai msgid paliktu stabili un
  jēgpilni — [ceļvedis](guide.md#safety-and-scope) parāda likumu,
  [Kā tas darbojas](internals.md#from-template-to-msgid) — iemeslus.
- **Formatējums paliek pilnībā ārpus kataloga**
  ([Kāpēc t-virknes](comparison.md)).
- **Daudzskaitļi** seko apvienojuma/šķēluma likumam, kas ļauj mērķa valodas
  daudzskaitļa sistēmai atšķirties no avota valodas sistēmas
  ([spec. §4](spec.md)).
- Sabojāts katalogs **atkāpjas, nevis avarē**, ievērojot paša gettext kontraktu
  ([ceļvedis](guide.md#what-happens-when-a-catalog-is-wrong)).
- Un visa konvencija ir [versionēta specifikācija](spec.md) ar mašīnlasāmu
  atbilstības komplektu — uzrakstīta tā, lai cita implementācija, arī nākotnes
  standarta bibliotēkas implementācija, varētu to pārņemt nemainītu un
  savietoties.

Diskusija nav beigusies, un šis projekts tajā ir dalībnieks, nevis spriedums
par to. Ja jums ir produkcijas gettext pieredze, kas skar šīs izvēles, tas
pats [pavediens][discuss-thread] un šī repozitorija
[Diskusijas][gh-discussions] ir vieta, kur diskusija turpinās.

## Laika līnija { #timeline }

| Kad | Kas notika |
| --- | --- |
| 1990. gadu vidus | GNU gettext nostiprina PO/POT/MO darbplūsmu, ko tulkotāji un platformas runā vēl šodien. |
| 2015 | [PEP 501] piedāvā interpolācijas veidnes ar i18n kā pirmo motivāciju; atlikts. |
| 2016 | F-virknes nonāk Python 3.6 — interpolācija iegūst savu sintaksi, un tulkošana to nevar izmantot. |
| 2024. g. jūl. | [PEP 750] piedāvā t-virknes. |
| 2025. g. apr. | PEP 750 [pieņemts][sc-resolution]; PEP 501 atsaukts par labu tam. |
| 2025. g. aug. | Atveras pavediens [Support t-strings in gettext][discuss-thread] ar standarta bibliotēkas [pull request][cpython-pr]. |
| 2025. g. okt. | [Python 3.14] piegādā t-virknes; standarta bibliotēkas problēmziņojums aizveras kā [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` iznāk kā alfa, ar [spec. v1](spec.md) un tā atbilstības komplektu. |

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
