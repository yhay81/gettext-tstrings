---
description: "Vad som faktiskt går sönder när en liten webbplats översätts till trettiofem språk, vilket av det biblioteket kan fånga åt dig och vilket det inte kan."
---

# Fallgropar

Den här webbplatsen är översatt till trettiofem språk, och varenda en av dem
togs fram genom att köra det kretslopp som dokumentationen lär ut. Det är ett
litet korpus med branschens mått mätt, och ändå räckte det för att träffa de
flesta av de fällor som gör i18n svårare än det ser ut.

Varje avsnitt nedan är något som faktiskt gick fel här, hur det såg ut när det
hände, och var gränsen går mellan vad biblioteket kontrollerar åt dig och vad
som förblir din egen bedömning.

## Att byta namn på en variabel översätter om en mening { #renaming-a-variable-retranslates-a-sentence }

Ett msgid är katalogens nyckel, och ett interpolerat namn ligger *inuti* det.
Att flytta en konstant till modulnivå och versalisera den så som Pythons stil
kräver — `author` till `AUTHOR` — förvandlade
`Copyright © 2026 {author} · MIT License` till ett meddelande som ingen katalog
någonsin hade sett. Varje översättning av den raden skulle ha gått tillbaka
genom fuzzy-cykeln, på varje språk, för ett namnbyte som inte ändrade något en
läsare kunde se.

Biblioteket hindrar dig inte: båda stavningarna är giltiga platshållarnamn.
Vad det däremot gör är att göra namnet *värt* att skydda — en interpolation
måste vara ett [enkelt namn](internals.md#from-template-to-msgid), så det som
står i katalognyckeln är ett ord som en översättare kan läsa, inte ett uttryck.

Spegelfallet är säkert av konstruktion. Konverteringar och formatspecifikationer
ingår inte i msgid:t, så att strama åt `{amount:,.2f}` till `{amount:,.0f}`
ändrar ingen nyckel och ogiltigförklarar ingen översättning någonstans.

## `nplurals=2` betyder inte två olika strängar { #nplurals-2-does-not-mean-two-different-strings }

Turkiska, ungerska, persiska och bengaliska deklarerar alla två pluralformer,
och i alla fyra är de två formerna av ett räknat meddelande med rätta *samma
sträng* — substantivet står kvar i singular efter ett räkneord, så `{n} sayfa`
är rätt både för en sida och för tio. En granskare som "rättar" dubbleringen
förstör översättningen.

Det motsatta misstaget är precis lika lätt. Lettiskans tredje form finns för
**noll ensamt**; slovenskans andra är ett **dualis**, för exakt två;
rumänskans sista form kräver ordet `de` som dess två första inte får ha. Att
fylla de platserna med en singular och en plural ger en katalog som bara är fel
för antal som ingen testar.

Värre är att *ordningen* mellan platserna inte är semantisk. Kymriskan
indexerar sina fem former så att `msgstr[0]` är det allmänna fallet och
`msgstr[1]` är singularen. Att fylla i dem i den självklara följden placerar
singularen där varje oräknat meddelande kommer att hitta den.

Biblioteket tar inget av detta på sig, och det är just poängen: målspråkets
pluralregel bor i dess egen kataloghuvud, och
[unions-/snittregeln](spec.md) låter en översättning ha fler former, eller
färre, än källan. Vad det kontrollerar är det enda det kan kontrollera utan att
kunna språket — att varje form behåller de platshållare den behöver.

## Två former kan vara identiska av en anledning { #two-forms-can-be-identical-for-a-reason }

Iriskan har fem pluralformer, och i den här webbplatsens byggrapport stavas
flera av dem likadant. Det är inte ett klipp-och-klistra-slarv: *leathanach*
börjar på `l`, och ingen av de två initiala mutationer som iriska räkneord
utlöser skrivs ut på `l`. Formerna gör fortfarande verkligt arbete — stammen
växlar mellan *leathanach* och *leathanaigh*, och antal över tio återgår till
singularen — men inget substantiv med betydelsen "sida" skulle visa
kontrasten.

Varje kontroll som flaggar dubblerade former som misstänkta kommer att flagga
korrekt iriska. En människa som kan språket är den enda granskaren för detta.

## Ett meddelande kan bara kongruera med ett enda antal { #a-message-can-only-agree-with-one-count }

Den här webbplatsens byggrapport berättar hur många sidor som renderades och
hur lång tid det tog. Att skriva det som "Rendered {n} pages in {seconds}
seconds" ser harmlöst ut och går inte att översätta: gettext väljer en form
utifrån ett antal, och det antalet är `n`. Ordet *seconds* skulle behöva
kongruera med ett tal som pluralmaskineriet aldrig får se.

Lösningen är att göra den andra storheten till en enhetssymbol i stället för
ett ord, och enhetssymboler är i sin tur lokaliserade: den här webbplatsens
kataloger bär `s`, `с`, `ث`, `שנ׳` och `mp`, och fransk, spansk och svensk
typografi vill ha ett mellanslag före symbolen där engelskan inte vill det.
Inget av det är bibliotekets sak — men att lägga märke till att ett meddelande
behöver *två* kongruenser är det, och det enda verktyget för den saken är att
skriva meddelandet annorlunda.

## Att redigera en engelsk mening redigerar främmande grammatik { #editing-an-english-sentence-edits-foreign-grammar }

Startsidan sa förut "all ten language editions". Att ta bort talet — en
engelsk ändring på ett ord, gjord för att talet ständigt blev inaktuellt —
gjorde ett plural-subjekt singulart. Spanska, italienska, portugisiska, ryska,
ukrainska, grekiska, nederländska och hebreiska behövde alla kongruera om
verbet; flera behövde ändra participet också.

En källändring som läses som trivial på engelska är inte trivial längre ned i
kedjan. Att markera den som fuzzy, vilket är vad `pybabel update` gör, är den
mekanism som ger varje översättare chansen att upptäcka den.

## Osynliga skillnader överlever varje kopiering { #invisible-differences-survive-every-copy-paste }

Guiden citerar ett diagnostikmeddelande som innehåller `(nаme)` — en avsiktlig
escape-sekvens, eftersom tecknet den namnger är ett kyrilliskt `а` som ingen
läsare kan skilja från det latinska. Översättare av den här webbplatsen
förvandlade den escape-sekvensen till det faktiska tecknet **fem separata
gånger**, på fem olika språk, och producerade varje gång en sida som såg
korrekt ut och var fel.

Just den här fångar biblioteket, och det är skälet till att diagnostiken är
formad som den är: en platshållare vars bokstäver blandar skriftsystem
[rapporteras två gånger](internals.md#diagnostics-are-part-of-the-design), en
gång läsbart och en gång escapat, eftersom den escapade formen är den enda
stavning som skiljer dem åt. Ett hårt mellanslag inuti klamrar skrivs ut med
kodpunkt av samma skäl. Katalogkontrollen avvisar meddelandet innan det hinner
gå ut.

## Icke-tom är inte översatt { #non-empty-is-not-translated }

En katalog som ställts i ordning med sina msgid:n kopierade in i msgstr:erna
klarar varje naiv kontroll: inget är tomt, inget är fuzzy, meddelandemängden
stämmer exakt. En utgåva av den här webbplatsen låg ute så i flera timmar. Det
gjorde också åtta sidor i en annan utgåva som var byte-identiska kopior av den
engelska källan — vilket klarar en kontroll som jämför kodblock mellan dem,
eftersom de är samma fil.

Inget av det är något ett översättningsbibliotek kan se. Båda är billiga att
testa för när man väl vet att man ska: jämför mot källan och kräv en skillnad.

## Katalogen är inte det enda som översätts { #the-catalog-is-not-the-only-translated-thing }

Två fel här hade ingenting med gettext att göra.

Att översätta en rubrik ändrar ankaret som genereras ur den, så varje
korssidelänk in i det avsnittet går sönder — tyst, och bara på det språket.
Den här webbplatsen spikar det engelska ankaret på varje rubrik, och ett test
härleder den förväntade listan från den engelska sidan.

Och webbplatsgeneratorn levererar gränssnittsöversättningar för sextioåtta
språk, vilket inte omfattar swahili eller iriska. Utan en sådan faller bygget
inte tillbaka till engelska; mall-inkluderingen misslyckas och utgåvan går
över huvud taget inte att bygga. Två av det här förrådets egna filer finns för
att fylla den luckan.

## Dina verktyg har också buggar { #your-tools-have-bugs-too }

CI-steget som den här dokumentationen rekommenderar för att fånga inaktuella
kataloger, `pybabel update --check`, klarar inte det jobbet för något projekt
som använder `pgettext` eller `npgettext` — det rapporterar varje katalog med
ett `msgctxt` som inaktuell, vid varje körning, på grund av en bugg i hur
jämförelsen slår upp meddelanden. Den hittades här genom att någon försökte
använda verktyget, rapporterades uppströms och är
[beskriven i sin helhet med lösningen](workflow.md#what-ci-gates).

Den allmänna lärdomen är den obekväma: en grind som alltid lyser rött är sämre
än ingen grind alls, eftersom ett team stänger av den. Kontrollera att din
CI-kontroll faktiskt kan gå igenom innan du litar på att den kan fälla något.

## Vad biblioteket är till för, på en rad { #what-the-library-is-for-in-one-line }

Det mesta på den här sidan är omdöme som inget verktyg kan ta över. Vad ett
verktyg *kan* göra är att garantera att en översättning inte kan ändra
strukturen i den mening den översätter — inte kan tappa ett värde, hitta på
ett, formatera om ett eller sträcka sig in i dina objekt — och att säga det i
en mening som den som ska rätta felet kan agera på. Det är hela vad det här
biblioteket lovar, och resten av den här webbplatsen är hur det håller löftet.
