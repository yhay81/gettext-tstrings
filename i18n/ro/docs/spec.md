---
description: "Convenția de la t-string la msgid ca un mic contract versionat, cu o suită de conformitate lizibilă de mașină."
---

# Specificație

Poți folosi această bibliotecă fără să citești pagina de față —
[tutorialul](tutorial.md) și [ghidul](guide.md) acoperă utilizarea de zi cu zi.
Această pagină este pentru autorii de unelte: convenția pe care biblioteca o
implementează este consemnată ca un contract mic și stabil, astfel încât o altă
implementare — un extractor, un IDE, un verificator de tipuri sau un viitor
`pygettext` — să o poată ținti și să interopereze cu ea. Pentru aceleași reguli
explicate împreună cu motivele lor, și pentru felul în care implementarea de
referință le duce la îndeplinire, citește mai întâi
[Cum funcționează](internals.md).

[Citește specificația v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Regulile pe un singur ecran { #the-rules-in-one-screen }

**Un msgid** este concatenarea, în ordinea din sursă, a segmentelor literale și
a câte unui token `{name}` per interpolare. Acoladele literale sunt escapate
(`{` devine `{{`). Un nume trebuie să fie un nume simplu de substituent —
`str.isidentifier()` este adevărat și nu este un cuvânt-cheie Python.
Conversiile și specificațiile de format **nu** fac parte din msgid; ele rămân
sub controlul aplicației.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *respins — nu este un nume simplu* |

**O traducere** este validă când conține numai substituenți `{name}` goi, când
fiecare nume cerut apare cel puțin o dată și când nu apare niciun nume din
afara mulțimii permise. Reordonarea și repetarea sunt lăsate intenționat
neconstrânse: amândouă pot fi necesare gramatical într-o limbă țintă.

Pentru plural, mulțimea *permisă* este reuniunea numelor din ramuri, iar cea
*cerută* este intersecția lor — așa că `t"One file"` față de `t"{n} files"`
lasă `n` disponibil traducătorului oricăreia dintre forme, dar nu îl cere
niciuneia, iar regulile de plural ale unei limbi țintă pot diferi de ale
sursei.

**Un msgid gol** nu este căutat niciodată, pentru că gettext îl rezervă
antetului cu metadatele catalogului.

## Conformitate { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
este același document în formă lizibilă de mașină: cazuri care leagă structura
statică a unui t-string de un msgid, și un msgid plus un tipar de catalog de un
șir randat sau de o respingere.

O implementare **se conformează specificației v1** atunci când reproduce fiecare
caz. Cazurile numesc doar ceea ce definește specificația — msgid-uri derivate,
tipare acceptate și respinse, ieșirea randată — și niciodată un mesaj de eroare
sau un tip de excepție, așa că o implementare în alt limbaj le poate rula
nemodificate.

Interpolările sunt descrise structural, niciodată ca sursă Python:

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

Câmpul `"spec"` **nu** este o versiune a specificației — fiecare caz din
`v1.json` aparține specificației v1. El numește secțiunea din `SPEC.md` pe care
o exersează cazul, așa că `"2.2"` se citește ca §2.2, regula de derivare a unui
token de substituent.

Implementarea de referință rulează suita ca parte a propriei suite de teste,
astfel încât proza și codul nu pot să se depărteze una de alta în tăcere.

## Versionare { #versioning }

Aceasta este specificația v1. O schimbare incompatibilă retroactiv în derivarea
msgid-ului sau în validarea traducerilor incrementează versiunea și livrează un
nou `conformance/vN.json` alături de cel existent. Clarificările aditive care nu
schimbă nici msgid-urile derivate, nici tiparele acceptate, nu o fac.
