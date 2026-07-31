---
description: "Platshållarkontraktet för den som redigerar .po-filerna: vad du får ändra, vad du måste lämna i fred, och hur du läser felmeddelandena."
---

# För översättare

Den här sidan är till för den som redigerar katalogen, inte för den som skriver
koden. Den är kort med avsikt, och den är tänkt att länkas eller kopieras in i
ett projekts egna översättarinstruktioner.

Ingenting här kräver att du kan läsa Python. Allt här handlar om en enda sak:
de delar av ett meddelande som står inom klammerparenteser.

## Vad en platshållare är { #what-a-placeholder-is }

Ett meddelande i en katalog kan innehålla namn inom klammerparenteser:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` är en **platshållare**. När programmet visar det här meddelandet
ersätter det `{name}` med ett värde som det själv levererar — ett personnamn,
ett filnamn, ett tal. Platshållaren är inte ett ord att översätta; den är en
lucka.

Din översättning hamnar i `msgstr`, och den måste behålla den luckan:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Vad du får ändra, och vad du inte får { #what-you-may-change-and-what-you-may-not }

Du **får**:

- **Flytta en platshållare** dit målspråkets grammatik vill ha den, även längst
  fram i meddelandet.
- **Upprepa en platshållare** om språket behöver värdet två gånger.
- **Skriva om varenda annat ord**, inklusive skiljetecken, mellanrum och
  meningsbyggnad.

Du får **inte**:

- **Översätta namnet inuti klamrarna.** `{name}` förblir `{name}`, även i ett
  språk som inte skriver något annat med latinska bokstäver.
- **Ta bort klamrarna**, eller skriva namnet utan dem.
- **Byta ut de latinska klamrarna `{` `}` mot klamrar i helbredd `｛` `｝`.**
  Många inmatningsmetoder producerar formerna i helbredd; de ser nästan
  likadana ut och fungerar inte.
- **Lägga till formatering**, som `{name!r}` eller `{amount:.2f}`. Hur ett värde
  visas bestäms i programmet, inte i katalogen.
- **Hitta på en platshållare** som inte finns i `msgid`.

Om ett meddelande behöver ett värde som originalet inte erbjuder är det ett
meddelande som utvecklaren måste ändra. Säg till i stället för att gå runt det.

## Pluralformer { #plural-forms }

Ett räknat meddelande kommer med en `msgstr`-lucka per pluralform i ditt språk,
och ditt språk avgör hur många det är — en för japanska, två för tyska, tre för
ryska, sex för arabiska. Fyll i varje lucka katalogen ger dig.

Två regler som brukar överraska:

- **Luckorna är inte "singular, plural, ännu mer plural".** Varje index betyder
  det som ditt språks pluralregel säger att det betyder. Lettiskans tredje form
  gäller bara noll; slovenskans andra gäller exakt två; walesiskan lägger det
  allmänna fallet på index 0 och singularen på index 1.
- **Två luckor får med rätta innehålla samma text.** I turkiska, ungerska,
  persiska och bengali står ett substantiv kvar i singular efter ett räkneord,
  så båda formerna av ett räknat meddelande är samma sträng. Det är korrekt,
  inte ett klipp-och-klistra-misstag.

Platshållarreglerna ovan gäller för varje form för sig.

## Fuzzy-poster { #fuzzy-entries }

En post märkt `fuzzy` är en maskins gissning: utvecklaren ändrade
originalmeddelandet, och verktygen parade ihop den nya texten med din gamla
översättning så att du har någonstans att börja.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

En fuzzy-post **används inte av programmet** — det visar det oöversatta
originalet i stället — förrän någon bearbetar texten och tar bort
`fuzzy`-märkningen. De flesta PO-redigerare har en knapp för precis det.

## Läsa ett felmeddelande { #reading-a-failure-message }

Verktygen kontrollerar platshållare när katalogen kompileras, och meddelandet
är skrivet för dig snarare än för en programmerare. Att bara rapportera att
`{name}` saknas är en återvändsgränd när du kan se de tecknen framför dig, så
där en platshållare ser ut att finnas men inte gör det säger meddelandet
varför. Mot originalet `Hello {name}` rapporteras vart och ett av dessa under
`translation does not match the source placeholders:`

| Din översättning säger | Skälet den anger |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Tecken som inte kan ses får sin egen behandling. Ett hårt mellanslag inne i
klamrarna är något en inmatningsmetod producerar och ingen redigerare visar,
så meddelandet skriver ut det med kodpunkt i stället för att namnge ett
tecken du aldrig skulle kunna hitta:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Ett namn vars bokstäver blandar skriftsystem — homoglyffallet, där ett
kyrilliskt `а` inte går att skilja från ett latinskt — visas två gånger, en
gång läsbart och en gång med escape-sekvens, vilket är den enda form som
skiljer de två åt:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Samma särskiljning gäller när ett grekiskt eller kyrilliskt namn skrivet helt
i ett skriftsystem kolliderar med ett ASCII-källnamn, inklusive fallet med
enbokstaviga latinska `a` / kyrilliska `а`.

Om du stöter på ett av dessa och rättningen inte är uppenbar är det säkraste
draget att radera platshållaren du skrev och kopiera in den från `msgid`.

## Vad kontrollerna inte kan göra { #what-the-checks-cannot-do }

Verktygen verifierar att dina platshållare är intakta. De kan inte avgöra om
översättningen är korrekt, naturlig eller rätt för sammanhanget — det förblir
helt och hållet ditt.

Två saker hjälper mer än någon kontroll:

- **Läs översättarkommentaren.** En rad som börjar med `#.` ovanför meddelandet
  är utvecklaren som berättar var det dyker upp och vad det betyder.
- **Fråga om `msgctxt`.** När samma ord förekommer två gånger med olika
  kontexter är det för att de två behöver översättas olika — "Open" knappen och
  "Open" tillståndet, till exempel.
