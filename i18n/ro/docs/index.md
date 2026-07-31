---
description: "Tradu mesaje t-string complete prin gettext și Babel, cu valorile și formatarea ținute în afara catalogului."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Tradu mesaje întregi,<br>nu fragmente de șir.

`gettext-tstrings` leagă t-stringurile din Python 3.14+ de cataloagele gettext
standard și de uneltele Babel. Valorile și formatarea rămân în codul aplicației;
catalogul ține un mesaj complet, cu substituenți simpli `{name}`:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Începe tutorialul :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Compară alternativele](comparison.md){ .md-button }

Alpha · Python 3.14+ · cataloage PO/MO obișnuite · fără dependențe la rulare
{ .home-facts }

Acest sit practică ceea ce documentează: fiecare ediție lingvistică —
navigarea, etichetele și raportul de build conștient de plural — este randată
din cataloage PO de
[`gettext-tstrings` însuși](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Este pentru tine? { #is-this-for-you }

**Se potrivește astăzi dacă** aplicația ta rulează pe Python 3.14 sau mai nou;
folosești deja gettext și Babel, sau vrei să le adopți fluxul PO/MO; și vrei
sintaxă de t-string cu substituenți denumiți, verificați înainte de a fi
randați.

**Nu se potrivește încă dacă** ai nevoie de Python 3.13 sau mai vechi; îți
trebuie un API Python stabil — acesta este un alpha, iar
[specificația](spec.md) este partea lui care s-a așezat; sau dacă aproape tot
textul tău traductibil trăiește într-un limbaj de șabloane, nu în sursă Python.

Ai deja cataloage? Ele continuă să funcționeze.
`_("Hello {name}").format(name=name)` și `tr(t"Hello {name}")` produc același
msgid, așa că traducerile existente supraviețuiesc trecerii —
[Migrare](migration.md) parcurge toată mutarea.

## Ce poate spune catalogul { #what-the-catalog-may-say }

Catalogul primește mesajul complet `Hello {name}`. O traducere poate reordona
sau repeta `{name}` și poate rescrie fiecare alt cuvânt din jurul lui. Ea nu
poate elimina substituentul, nu poate inventa unul nou, nu poate ajunge prin el
la obiectele tale și nu îi poate atașa formatare proprie.

Aceasta este toată promisiunea: **o traducere nu poate schimba structura
mesajului pe care îl traduce.** Biblioteca o verifică la intrare — când sunt
compilate cataloagele — și încă o dată la randare; o intrare stricată care
ajunge totuși în producție jurnalizează un avertisment și randează mesajul
sursă, în loc să cadă.

!!! note "Nou la gettext? Întregul flux în patru propoziții"

    **gettext** este modul standard în care software-ul ajunge să fie tradus,
    în Python și cu mult dincolo de el. Codul tău marchează mesajele
    traductibile; un *extractor* le adună într-un fișier șablon (`.pot`); un
    traducător — de obicei nu un programator — completează câte un fișier
    catalog (`.po`) pe limbă, care este compilat într-un `.mo` binar pe care
    aplicația ta îl încarcă la rulare. Numele convențional al funcției de
    traducere este `_`, așa că `_(t"Hello {name}")` se citește ca „tradu
    mesajul acesta”. **[Tutorialul](tutorial.md)** parcurge întregul drum —
    marchează, extrage, tradu, compilează, rulează — în vreo cinci minute.

## Problema pe care o rezolvă { #the-problem-it-solves }

Un f-string este deja interpolat până când vreo bibliotecă apucă să îl vadă —
`f"Hello {name}"` a devenit `"Hello Ada"`, iar traducerea fragmentelor din
jurul unei valori strică gramatica majorității limbilor. Un t-string
([PEP 750]) ține separate textul static, valorile evaluate, expresiile sursă,
conversiile și specificațiile de format — exact împărțirea de care are nevoie
un catalog de mesaje.
[Ce schimbă asta](comparison.md), în comparație cu `%(name)s`, `.format()` și
`$`-stringurile.

Nimic din gettext sau Babel nu spune însă cum devine un t-string un mesaj.
Biblioteca de față face acea alegere, o consemnează ca
[specificație versionată](spec.md) și livrează
[suita de conformitate](spec.md#conformance) care o verifică.

## Regulile de proiectare { #the-design-rules }

- Traduce mesaje complete, niciodată fragmente de propoziție.
- Acceptă doar nume simple de variabile, precum `{name}`.
- Ține `!r` și `:.2f` sub controlul aplicației, în afara catalogului.
- Permite traducerilor să reordoneze și să repete substituenții cunoscuți,
  împiedicându-le totodată să ajungă la atribute sau să adauge formatare.
- Reutilizează fișiere POT, PO și MO obișnuite, și uneltele care le citesc deja.

Și lista pe potrivă a ceea ce lasă în mod deliberat în pace: nu localizează
numere, monede sau date — [formatează-le întâi](guide.md#locale-aware-values),
cu Babel; nu escapează ieșirea randată pentru HTML, un shell sau un terminal; și
nu poate judeca dacă o traducere este *corectă*, ci doar dacă substituenții ei
sunt intacți.

## Instalare { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 sau mai nou. **Randarea nu are dependențe** — folosește `gettext`
din biblioteca standard și nimic altceva.

Extragerea și validarea cataloagelor trec prin [Babel], așa că instalează acel
extra oriunde rulează `pybabel`, ceea ce înseamnă de obicei un mediu de
dezvoltare sau de CI, mai degrabă decât o imagine de producție:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Încotro mai departe { #where-to-go-next }

**Începe aici** — fără a presupune experiență cu gettext:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — de la un director gol la o traducere japoneză
  care rulează, în cinci pași, fiecare comandă arătată cu ieșirea ei.
- **[De ce t-stringuri](comparison.md)** — același mesaj scris în patru feluri,
  și ce anume dau catalogului `%(name)s`, `.format()` și `$`-stringurile.

</div>

**Folosește-l** — referințele de lucru:

<div class="grid cards" markdown>

- **[Ghid](guide.md)** — API-ul de rulare: ce punct de intrare să folosești,
  plural, limbi per cerere, șiruri amânate și ce se întâmplă când un catalog
  este greșit.
- **[Extragere](extraction.md)** — referința `pybabel`: configurare, nume
  proprii de funcții și felul în care uneltele existente validează gratuit
  aceste cataloage.
- **[În producție](workflow.md)** — bucla așa cum o rulează o echipă: ciclul de
  actualizare, intrările fuzzy, porțile de CI, platformele de traducere și
  livrarea.
- **[Migrare](migration.md)** — adoptarea acestei biblioteci într-un proiect
  care are deja cataloage, un loc de apel pe rând.
- **[Pentru traducători](translators.md)** — o singură pagină de dat celui care
  editează fișierele `.po`.

</div>

**Înțelege-l** — de la istorie la implementare:

<div class="grid cards" markdown>

- **[Context](background.md)** — de ce există această bibliotecă: treizeci de
  ani de gettext, două PEP-uri și discuția din biblioteca standard care s-a
  închis fără un răspuns.
- **[Capcane](pitfalls.md)** — ce a stricat cu adevărat traducerea acestui sit
  în treizeci și cinci de limbi, și ce jumătate din asta poate prinde o unealtă.
- **[Cum funcționează](internals.md)** — de la obiectul șablon al PEP 750 până
  la șirul randat, și cache-urile care fac verificarea ieftină.

</div>

**Referință** — contractele:

<div class="grid cards" markdown>

- **[API](api.md)** — tot ce exportă pachetul, pe o singură pagină.
- **[Specificație](spec.md)** — convenția t-string ↔ msgid ca un contract
  stabil și versionat, cu o suită de conformitate lizibilă de mașină.

</div>

## Stadiu { #status }

Un alpha. Contractul este mic în mod intenționat, iar
[specificația](spec.md) este partea lui stabilă; API-ul Python încă se poate
mișca. Înainte de o lansare stabilă, aici este nevoie de fixture-uri
lingvistice mai largi, de urmărire susținută a performanței, de o recenzie de
API din partea celor care folosesc gettext și Babel în serios, și de testare a
compatibilității pe fiecare versiune suportată de Python și de Babel.

[Tichetele și pull requesturile](https://github.com/yhay81/gettext-tstrings/issues)
sunt binevenite — un alpha este exact momentul în care încă merită să te cerți
despre interfață.

## Alătură-te comunității { #join-the-community }

- Alege un
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  pentru o contribuție bine delimitată.
- Pune întrebări de utilizare în
  [Discuțiile Q&A](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Adu fluxuri gettext din producție și idei de API în
  [Discuțiile Ideas](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Citește
  [ghidul de contribuție](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  înainte de a deschide un pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
