---
description: "Trent'anni di gettext, due PEP a dieci anni di distanza e la discussione sulla stdlib chiusa come not-planned: perché questa libreria esiste, con i link alle fonti."
---

# Contesto

Questa libreria si trova al punto d'incontro di due lunghe storie — una su
come il software viene tradotto, una su come Python interpola le stringhe —
che si sono finalmente intersecate nel 2025 per poi arenarsi esattamente nel
punto in cui serviva una convenzione piccola e accurata. Questa pagina
racconta entrambe le storie, con i link alle fonti, perché le decisioni di
design di questo sito sono più facili da giudicare quando puoi vedere le
domande a cui rispondono.

## L'ecosistema gettext { #the-gettext-ecosystem }

[GNU gettext] è il modo in cui il software libero viene tradotto dalla metà
degli anni Novanta: marca le stringhe nel codice, estraile in un template,
consegna ai traduttori un file di catalogo per lingua, compila, carica a
runtime. Attorno a quel ciclo è cresciuto un intero ecosistema — editor PO,
flussi di revisione e piattaforme di traduzione che parlano tutti lo stesso
formato di file — e Python distribuisce un [modulo `gettext`][stdlib-gettext]
nella sua libreria standard da più di vent'anni. La metà runtime della
traduzione non è mai stata il problema.

La metà irrisolta è sempre stata *che aspetto ha la stringa nel catalogo*. Un
messaggio `%(name)s` consegna ai traduttori sintassi printf che una lettera
cancellata trasforma in un crash in produzione; un messaggio `.format()`
consegna al catalogo l'accesso agli attributi di oggetti vivi.
([Perché le t-string](comparison.md) li percorre entrambi, con i fallimenti
in bella vista.) E le f-string — la sintassi che la maggior parte del codice
Python ormai preferisce — non possono partecipare affatto: quando una
libreria ne vede una, è già una stringa finita. La gente ci prova comunque,
abbastanza spesso che il tracker di Babel colleziona i tentativi
([#594][babel-594], [#715][babel-715]); il fallimento è strutturale, non una
funzionalità mancante.

## Due PEP, a dieci anni di distanza { #two-peps-ten-years-apart }

Nel 2015 Alyssa Coghlan e Nick Humrich scrissero la [PEP 501], proponendo
template di interpolazione la cui prima motivazione dichiarata era l'i18n —
"providing a cleaner syntax for i18n translation", nelle parole della PEP
stessa. La proposta fu rinviata, in parte perché la discussione mostrò che il
caso i18n portava con sé considerazioni aggiuntive significative che i casi
d'uso più semplici non avevano.

Un decennio dopo, la [PEP 750] — di Jim Baker, Guido van Rossum, Paul
Everitt, Koudai Aono, Lysandros Nikolaou e Dave Peck — riprese l'idea come
t-string, fu [accettata nell'aprile 2025][sc-resolution] e arrivò con
[Python 3.14] nell'ottobre 2025. La PEP 501 fu allora ritirata in suo favore.
Un dettaglio conta per questa pagina: l'i18n *non* è tra le motivazioni
dichiarate della PEP 750. La PEP ha generalizzato il meccanismo — un tipo
template che qualunque libreria può consumare — e ha lasciato la questione
della traduzione esattamente dove la PEP 501 l'aveva parcheggiata dieci anni
prima: aperta.

Così, a partire da Python 3.14, il linguaggio aveva precisamente la struttura
dati di cui un catalogo di messaggi ha bisogno, e nessuna convenzione per
usarla come tale.

## La discussione sulla stdlib { #the-stdlib-discussion }

Due mesi prima dell'uscita della 3.14, Adrian Mönnich (ThiefMaster, un
manutentore del progetto Indico) propose di colmare quel divario nella
libreria standard stessa: il thread
[Support t-strings in gettext][discuss-thread] su discuss.python.org, aperto
nell'agosto 2025, arrivò con una [pull request][cpython-pr] funzionante che
aggiungeva il supporto alle t-string sia in `gettext` sia in `pygettext`.

Il thread merita di essere letto per intero, perché fa emergere ogni domanda
difficile a cui questa libreria ha poi dovuto rispondere:

- **Che cosa può essere un'interpolazione?** Solo un nome semplice, o anche
  attributi e chiamate con un nome di segnaposto derivato? Ogni risposta
  scambia comodità contro stabilità dei msgid e sicurezza del catalogo.
- **Che cosa richiedono le forme plurali,** quando il sistema di plurali
  della lingua di destinazione differisce da quello della sorgente?
- **gettext è davvero il bersaglio giusto?** Barry Warsaw — che durante lo
  sviluppo della PEP 750 aveva sostenuto che le t-string non fossero adatte
  all'i18n — indicò la sua [`flufl.i18n`][flufl-i18n] e il suo stile a
  `$`-string come lo strumento più amichevole; altri sostennero di lasciarsi
  gettext alle spalle del tutto in favore di sistemi più nuovi come
  [Fluent].
- **E la meta-domanda:** qualunque cosa la libreria standard distribuisca,
  essenzialmente non può più cambiare. Una convenzione con così tante scelte
  aperte è una cosa rischiosa da congelare al primo tentativo.

Non si formò alcun consenso. La issue di CPython fu
[chiusa come "not planned"][cpython-issue] e la pull request fu chiusa senza
merge nell'ottobre 2025, pochi giorni dopo l'uscita della 3.14. La capacità
esisteva nel linguaggio; la convenzione non aveva una casa.

## Perché un pacchetto, prima { #why-a-package-first }

Questo è il divario che questo progetto ha scelto di colmare da fuori della
libreria standard, su una scommessa deliberata: una convenzione matura più in
fretta dove può versionarsi liberamente e guadagnarsi l'adozione caso per
caso, e la libreria standard — che deve essere giusta al primo colpo — è dove
una convenzione dovrebbe *finire*, non dove dovrebbe essere elaborata.

Concretamente, ogni domanda contesa nel thread ha qui una risposta scritta,
ciascuna nella sua pagina:

- Le interpolazioni sono **solo nomi semplici**, così i msgid restano stabili
  e significativi — [la guida](guide.md#safety-and-scope) mostra la regola,
  [Come funziona](internals.md#from-template-to-msgid) le ragioni.
- **La formattazione resta interamente fuori dal catalogo**
  ([Perché le t-string](comparison.md)).
- **I plurali** seguono una regola di unione/intersezione che permette al
  sistema di plurali della lingua di destinazione di differire da quello
  della sorgente ([spec §4](spec.md)).
- Un catalogo danneggiato **ripiega invece di andare in crash**, mantenendo
  il contratto di gettext stesso
  ([la guida](guide.md#what-happens-when-a-catalog-is-wrong)).
- E l'intera convenzione è una [specifica versionata](spec.md) con una suite
  di conformità leggibile dalle macchine — scritta perché un'altra
  implementazione, inclusa una futura nella libreria standard, possa
  adottarla immutata e interoperare.

La discussione non è finita, e questo progetto ne è un partecipante, non un
verdetto. Se hai esperienza di gettext in produzione che riguarda queste
scelte, lo [stesso thread][discuss-thread] e le
[Discussions][gh-discussions] di questo repository sono i luoghi dove se ne
discute.

## Cronologia { #timeline }

| Quando | Che cosa è successo |
| --- | --- |
| metà anni '90 | GNU gettext stabilisce il flusso PO/POT/MO che traduttori e piattaforme parlano ancora. |
| 2015 | La [PEP 501] propone i template di interpolazione, con l'i18n come prima motivazione; rinviata. |
| 2016 | Le f-string arrivano con Python 3.6 — l'interpolazione ottiene la sua sintassi, e la traduzione non può usarla. |
| lug 2024 | La [PEP 750] propone le t-string. |
| apr 2025 | La PEP 750 è [accettata][sc-resolution]; la PEP 501 è ritirata in suo favore. |
| ago 2025 | Si apre il thread [Support t-strings in gettext][discuss-thread], con una [pull request][cpython-pr] per la stdlib. |
| ott 2025 | [Python 3.14] distribuisce le t-string; la issue sulla stdlib si chiude come [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` esce come alpha, con la [spec v1](spec.md) e la sua suite di conformità. |

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
