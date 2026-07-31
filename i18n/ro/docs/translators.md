---
description: "Contractul substituenților pentru cine editează fișierele .po: ce ai voie să schimbi, ce trebuie să lași în pace și cum se citesc erorile."
---

# Pentru traducători

Pagina de față este pentru persoana care editează catalogul, nu pentru cea care
scrie codul. Este scurtă intenționat și este menită să fie legată sau copiată în
instrucțiunile proprii pentru traducători ale unui proiect.

Nimic de aici nu îți cere să citești Python. Totul de aici este despre un singur
lucru: bucățile dintre acolade ale unui mesaj.

## Ce este un substituent { #what-a-placeholder-is }

Un mesaj dintr-un catalog poate conține nume între acolade:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` este un **substituent**. Când programul arată acest mesaj, el
înlocuiește `{name}` cu o valoare pe care o furnizează el însuși — numele unei
persoane, numele unui fișier, un număr. Substituentul nu este un cuvânt de
tradus; este o casetă goală.

Traducerea ta merge în `msgstr` și trebuie să păstreze acea casetă:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Ce ai voie să schimbi și ce nu { #what-you-may-change-and-what-you-may-not }

**Ai voie**:

- **Să muți un substituent** oriunde îl vrea gramatica limbii țintă, inclusiv la
  începutul mesajului.
- **Să repeți un substituent**, dacă limba are nevoie de valoare de două ori.
- **Să rescrii fiecare alt cuvânt**, inclusiv punctuația, spațierea și ordinea
  propoziției.

**Nu ai voie**:

- **Să traduci numele dintre acolade.** `{name}` rămâne `{name}`, chiar și
  într-o limbă care nu scrie nimic altceva cu litere latine.
- **Să elimini acoladele** sau să scrii numele fără ele.
- **Să înlocuiești acoladele ASCII `{` `}` cu cele de lățime întreagă `｛` `｝`.**
  Multe metode de introducere produc formele de lățime întreagă; ele arată
  aproape identic și nu funcționează.
- **Să adaugi formatare**, precum `{name!r}` sau `{amount:.2f}`. Felul în care
  este afișată o valoare se decide în program, nu în catalog.
- **Să inventezi un substituent** care nu se află în `msgid`.

Dacă un mesaj are nevoie de o valoare pe care originalul nu o oferă, acela este
un mesaj pe care trebuie să îl schimbe dezvoltatorul. Spune asta, în loc să
ocolești problema.

## Formele de plural { #plural-forms }

Un mesaj cu numărare sosește cu câte o casetă `msgstr` pentru fiecare formă de
plural din limba ta, iar limba ta decide câte sunt acelea — una pentru japoneză,
două pentru germană, trei pentru rusă, șase pentru arabă. Completează fiecare
casetă pe care ți-o dă catalogul.

Două reguli care îi prind pe oameni pe picior greșit:

- **Casetele nu sunt „singular, plural, și mai plural”.** Fiecare index
  înseamnă exact ce spune regula de plural a limbii tale. A treia formă din
  letonă este numai pentru zero; a doua din slovenă este pentru exact doi; galeza
  pune cazul general la indexul 0 și singularul la indexul 1.
- **Două casete pot conține pe bună dreptate același text.** În turcă, maghiară,
  persană și bengaleză un substantiv rămâne la singular după un numeral, așa că
  ambele forme ale unui mesaj cu numărare sunt același șir. Este corect, nu o
  scăpare de copiere-lipire.

Regulile de mai sus despre substituenți se aplică independent fiecărei forme.

## Intrările fuzzy { #fuzzy-entries }

O intrare marcată `fuzzy` este ghiceala unei mașini: dezvoltatorul a schimbat
mesajul original, iar uneltele au împerecheat noul text cu vechea ta traducere,
ca să ai de unde porni.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

O intrare fuzzy **nu este folosită de program** — el arată în locul ei
originalul netradus — până când cineva revizuiește textul și scoate marcajul
`fuzzy`. Majoritatea editoarelor de PO au un buton exact pentru asta.

## Citirea unui mesaj de eșec { #reading-a-failure-message }

Uneltele verifică substituenții atunci când catalogul este compilat, iar mesajul
este scris pentru tine, nu pentru un programator. A raporta doar că `{name}`
lipsește este o fundătură atunci când vezi acele caractere chiar în fața ta, așa
că acolo unde un substituent pare prezent, dar nu este, mesajul spune de ce.
Față de originalul `Hello {name}`, fiecare dintre acestea este raportat sub
`translation does not match the source placeholders:`

| Ce spune traducerea ta | Motivul pe care îl dă |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` lipsește (acoladele din jurul lui nu sunt `{` și `}` din ASCII) |
| `こんにちは {{name}}` | `{name}` lipsește (este scris `{{name}}`, ceea ce este modul de a escapa o acoladă literală) |
| `こんにちは name` | `{name}` lipsește (numele apare, dar nu între acolade) |
| `こんにちは {名前}` | `{name}` lipsește; `{名前}` nu se află în mesajul sursă |

Caracterele care nu se pot vedea au parte de un tratament propriu. Un spațiu
neîntreruptor între acolade este ceva ce produce o metodă de introducere și nu
arată niciun editor, așa că mesajul îl tipărește după punctul de cod, în loc să
numească un caracter pe care nu l-ai putea găsi niciodată:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Un nume ale cărui litere amestecă sisteme de scriere — cazul homoglifelor, în
care un `а` chirilic nu se deosebește de unul latin — este arătat de două ori, o
dată lizibil și o dată escapat, ceea ce este singura formă care le distinge una
de alta:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Aceeași dezambiguizare se aplică atunci când un nume grecesc sau chirilic scris
în întregime într-un singur alfabet intră în conflict cu un nume sursă ASCII,
inclusiv cazul cu o singură literă `a` latin / `а` chirilic.

Dacă dai peste unul dintre acestea și reparația nu este evidentă, mișcarea
sigură este să ștergi substituentul pe care l-ai tastat și să îl copiezi pe cel
din `msgid`.

## Ce nu pot face verificările { #what-the-checks-cannot-do }

Uneltele verifică dacă substituenții tăi sunt intacți. Ele nu pot spune dacă
traducerea este exactă, naturală sau potrivită pentru context — asta rămâne în
întregime la tine.

Două lucruri ajută mai mult decât orice verificare:

- **Citește comentariul pentru traducător.** O linie care începe cu `#.`
  deasupra mesajului este dezvoltatorul care îți spune unde apare mesajul și ce
  înseamnă.
- **Întreabă despre `msgctxt`.** Când același cuvânt apare de două ori cu
  contexte diferite, este pentru că cele două trebuie traduse diferit — „Open”
  butonul și „Open” starea, de pildă.
