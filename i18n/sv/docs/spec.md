---
description: "Konventionen t-string till msgid som ett litet versionerat kontrakt, med en maskinläsbar konformitetssvit."
---

# Specifikation

Du kan använda det här biblioteket utan att läsa den här sidan —
[handledningen](tutorial.md) och [guiden](guide.md) täcker vardagsbruket. Den
här sidan är för verktygsförfattare: konventionen biblioteket implementerar
är nedskriven som ett litet, stabilt kontrakt så att en annan implementation
— en extraktor, en IDE, en typkontroll eller en framtida `pygettext` — kan
rikta in sig på det och interoperera. För samma regler förklarade med sina
skäl, och hur referensimplementationen genomför dem, läs
[Så fungerar det](internals.md) först.

[Läs spec v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Reglerna på en skärm { #the-rules-in-one-screen }

**En msgid** är sammanfogningen, i källordning, av de bokstavliga segmenten
och ett `{name}`-token per interpolation. Bokstavliga klamrar escapas (`{`
blir `{{`). Ett namn måste vara ett enkelt platshållarnamn —
`str.isidentifier()` är sant och det är inte ett Python-nyckelord.
Konverteringar och formatspecifikationer är **inte** en del av msgid:n; de
stannar under applikationens kontroll.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *avvisas — inte ett enkelt namn* |

**En översättning** är giltig när den bara innehåller rena
`{name}`-platshållare, varje obligatoriskt namn förekommer minst en gång,
och inget namn utanför den tillåtna mängden förekommer. Omflyttning och
upprepning är avsiktligt obegränsade: båda kan vara grammatiskt nödvändiga i
ett målspråk.

För pluralformer är *tillåtet* unionen av grenarnas namn och *obligatoriskt*
deras snitt — så `t"One file"` mot `t"{n} files"` lämnar `n` tillgängligt
för en översättare av endera formen men obligatoriskt för ingen, och ett
målspråks pluralregler kan skilja sig från källans.

**En tom msgid** slås aldrig upp, eftersom gettext reserverar den för
katalogens metadatahuvud.

## Konformitet { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
är samma dokument i maskinläsbar form: fall som mappar en t-strängs statiska
struktur till en msgid, och en msgid plus ett katalogmönster till en
renderad sträng eller en avvisning.

En implementation **uppfyller spec v1** när den reproducerar varje fall.
Fallen namnger bara vad specifikationen definierar — härledda msgid:n,
accepterade och avvisade mönster, renderad utdata — och aldrig ett
felmeddelande eller en undantagstyp, så en implementation i ett annat språk
kan köra dem oförändrade.

Interpolationer beskrivs strukturellt, aldrig som Python-källkod:

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

Fältet `"spec"` är **inte** en specifikationsversion — varje fall i `v1.json`
hör till spec v1. Det namnger det avsnitt i `SPEC.md` som fallet prövar, så
`"2.2"` läses som §2.2, regeln för att härleda ett platshållartoken.

Referensimplementationen kör sviten som en del av sin egen testsvit, så att
prosan och koden inte kan glida isär i tysthet.

## Versionering { #versioning }

Detta är spec v1. En bakåtinkompatibel ändring av msgid-härledningen eller
av översättningsvalideringen ökar versionen och levererar en ny
`conformance/vN.json` bredvid den befintliga. Additiva förtydliganden som
varken ändrar härledda msgid:n eller accepterade mönster gör det inte.
