---
description: "La convenzione da t-string a msgid come un piccolo contratto versionato, con una suite di conformità leggibile dalle macchine."
---

# Specifica

Puoi usare questa libreria senza leggere questa pagina — il
[tutorial](tutorial.md) e la [guida](guide.md) coprono l'uso quotidiano.
Questa pagina è per gli autori di strumenti: la convenzione che la libreria
implementa è messa per iscritto come un contratto piccolo e stabile, così che
un'altra implementazione — un estrattore, un IDE, un type checker o un futuro
`pygettext` — possa prenderla di mira e interoperare. Per le stesse regole
spiegate con le loro ragioni, e per come l'implementazione di riferimento le
mette in pratica, leggi prima [Come funziona](internals.md).

[Leggi la spec v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Le regole in una schermata { #the-rules-in-one-screen }

**Un msgid** è la concatenazione, in ordine di sorgente, dei segmenti
letterali e di un token `{name}` per interpolazione. Le graffe letterali sono
escapate (`{` diventa `{{`). Un nome deve essere un semplice nome di
segnaposto — `str.isidentifier()` è vero e non è una parola chiave Python. Le
conversioni e le specifiche di formato **non** fanno parte del msgid; restano
sotto il controllo dell'applicazione.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *rifiutata — non è un nome semplice* |

**Una traduzione** è valida quando contiene soltanto segnaposto `{name}`
semplici, ogni nome richiesto compare almeno una volta e nessun nome fuori
dall'insieme consentito compare. Riordino e ripetizione sono deliberatamente
senza vincoli: entrambi possono essere grammaticalmente necessari in una
lingua di destinazione.

Per i plurali, *consentito* è l'unione dei nomi dei rami e *richiesto* la
loro intersezione — così `t"One file"` contro `t"{n} files"` lascia `n`
disponibile a chi traduce l'una o l'altra forma ma richiesto in nessuna, e le
regole di plurale di una lingua di destinazione possono differire da quelle
della sorgente.

**Un msgid vuoto** non viene mai cercato, perché gettext lo riserva
all'intestazione di metadati di un catalogo.

## Conformità { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
è lo stesso documento in forma leggibile dalle macchine: casi che mappano la
struttura statica di una t-string in un msgid, e un msgid più un pattern di
catalogo in una stringa resa o in un rifiuto.

Un'implementazione **è conforme alla spec v1** quando riproduce ogni caso. I
casi nominano solo ciò che la specifica definisce — msgid derivati, pattern
accettati e rifiutati, output reso — e mai un messaggio di errore o un tipo
di eccezione, così che un'implementazione in un altro linguaggio possa
eseguirli immutati.

Le interpolazioni sono descritte strutturalmente, mai come sorgente Python:

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

L'implementazione di riferimento esegue la suite come parte della propria
suite di test, così la prosa e il codice non possono allontanarsi in
silenzio.

## Versionamento { #versioning }

Questa è la spec v1. Una modifica incompatibile all'indietro alla derivazione
dei msgid o alla validazione delle traduzioni incrementa la versione e
distribuisce un nuovo `conformance/vN.json` accanto a quello esistente. I
chiarimenti additivi che non cambiano né i msgid derivati né i pattern
accettati non lo fanno.
