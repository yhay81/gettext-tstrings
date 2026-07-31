---
description: "Trinta anos de gettext, duas PEPs com dez anos de intervalo e a discussão na biblioteca padrão encerrada como not-planned: por que esta biblioteca existe, com links para as fontes."
---

# Contexto

Esta biblioteca está no ponto de encontro de duas longas histórias — uma sobre
como o software é traduzido, outra sobre como o Python interpola strings — que
finalmente se cruzaram em 2025 e então pararam exatamente no ponto em que uma
convenção pequena e cuidadosa era necessária. Esta página conta as duas
histórias, com links para as fontes, porque as decisões de design deste site
ficam mais fáceis de julgar quando se podem ver as perguntas que elas
respondem.

## O ecossistema gettext { #the-gettext-ecosystem }

O [GNU gettext] é a forma como o software livre é traduzido desde meados dos
anos 1990: marcar as strings no código, extraí-las para um template, entregar
a quem traduz um arquivo de catálogo por idioma, compilar, carregar em tempo
de execução. Em torno desse ciclo cresceu um ecossistema inteiro — editores de
PO, fluxos de revisão e plataformas de tradução que falam o mesmo formato de
arquivo — e o Python inclui um [módulo `gettext`][stdlib-gettext] em sua
biblioteca padrão há mais de duas décadas. A metade da tradução relativa ao
tempo de execução nunca foi o problema.

A metade nunca resolvida sempre foi *qual é a aparência da string no
catálogo*. Uma mensagem `%(name)s` entrega a quem traduz sintaxe printf que
uma única letra apagada transforma em um travamento em produção; uma mensagem
`.format()` entrega ao catálogo acesso a atributos de objetos vivos.
([Por que t-strings](comparison.md) percorre as duas, com as falhas à mostra.)
E as f-strings — a sintaxe que a maior parte do código Python hoje prefere —
não podem participar de forma alguma: quando qualquer biblioteca vê uma, ela
já é uma string pronta. Mesmo assim as pessoas tentam, com frequência
suficiente para que o rastreador de issues do Babel colecione as tentativas
([#594][babel-594], [#715][babel-715]); a falha é estrutural, não um recurso
ausente.

## Duas PEPs, dez anos de intervalo { #two-peps-ten-years-apart }

Em 2015, Alyssa Coghlan e Nick Humrich escreveram a [PEP 501], propondo
templates de interpolação cuja primeira motivação declarada era i18n —
"providing a cleaner syntax for i18n translation", nas palavras da própria
PEP. A proposta foi adiada, em parte porque a discussão mostrou que o caso de
i18n trazia considerações extras significativas que casos de uso mais simples
não tinham.

Uma década depois, a [PEP 750] — de Jim Baker, Guido van Rossum, Paul
Everitt, Koudai Aono, Lysandros Nikolaou e Dave Peck — reviveu a ideia como
t-strings, foi [aceita em abril de 2025][sc-resolution] e chegou ao
[Python 3.14] em outubro de 2025. A PEP 501 foi então retirada em seu favor.
Um detalhe importa para esta página: i18n *não* está entre as motivações
declaradas da PEP 750. A PEP generalizou o mecanismo — um tipo de template
que qualquer biblioteca pode consumir — e deixou a questão da tradução
exatamente onde a PEP 501 a havia estacionado dez anos antes: em aberto.

Assim, a partir do Python 3.14, a linguagem tinha precisamente a estrutura de
dados de que um catálogo de mensagens precisa, e nenhuma convenção para
usá-la como tal.

## A discussão na biblioteca padrão { #the-stdlib-discussion }

Dois meses antes do lançamento do 3.14, Adrian Mönnich (ThiefMaster,
mantenedor do projeto Indico) propôs fechar essa lacuna na própria biblioteca
padrão: a thread [Support t-strings in gettext][discuss-thread] no
discuss.python.org, aberta em agosto de 2025, veio acompanhada de um
[pull request][cpython-pr] funcional que adicionava suporte a t-strings tanto
ao `gettext` quanto ao `pygettext`.

A thread merece ser lida por inteiro, porque levanta todas as perguntas
difíceis que esta biblioteca depois teve de responder:

- **O que uma interpolação pode ser?** Apenas um nome simples, ou atributos e
  chamadas com um nome de marcador derivado? Cada resposta troca conveniência
  por estabilidade de msgid e segurança do catálogo.
- **O que as formas de plural exigem,** quando o sistema de plural do idioma
  de destino difere do da origem?
- **O gettext é sequer o alvo certo?** Barry Warsaw — que havia argumentado,
  durante o desenvolvimento da PEP 750, que t-strings não eram uma boa opção
  para i18n — apontou seu [`flufl.i18n`][flufl-i18n] e o estilo de strings
  `$` como a ferramenta mais amigável; outros defenderam deixar o gettext
  para trás de vez, em favor de sistemas mais novos como o [Fluent].
- **E a metaquestão:** o que quer que a biblioteca padrão inclua,
  essencialmente nunca poderá mudar. Uma convenção com tantas escolhas em
  aberto é algo arriscado de congelar na primeira tentativa.

Nenhum consenso se formou. A issue do CPython foi
[encerrada como "not planned"][cpython-issue] e o pull request foi fechado
sem merge em outubro de 2025, dias depois do lançamento do 3.14. A capacidade
existia na linguagem; a convenção não tinha lar.

## Por que um pacote, primeiro { #why-a-package-first }

É essa a lacuna que este projeto escolheu preencher de fora da biblioteca
padrão, numa aposta deliberada: uma convenção amadurece mais rápido onde pode
versionar livremente e conquistar adoção caso a caso, e a biblioteca padrão —
que precisa acertar de primeira — é onde uma convenção deve *terminar*, não
onde deve ser elaborada.

Concretamente, cada questão contestada na thread tem aqui uma resposta
escrita, cada uma em sua própria página:

- Interpolações são **apenas nomes simples**, para que os msgids permaneçam
  estáveis e significativos — [o guia](guide.md#safety-and-scope) mostra a
  regra, [Como funciona](internals.md#from-template-to-msgid), as razões.
- **A formatação fica inteiramente fora do catálogo**
  ([Por que t-strings](comparison.md)).
- **Plurais** seguem uma regra de união/interseção que permite que o sistema
  de plural do idioma de destino difira do da origem ([spec §4](spec.md)).
- Um catálogo danificado **recai no texto de origem em vez de travar**,
  mantendo o próprio contrato do gettext
  ([o guia](guide.md#what-happens-when-a-catalog-is-wrong)).
- E toda a convenção é uma [especificação versionada](spec.md) com uma suíte
  de conformidade legível por máquinas — escrita para que outra
  implementação, inclusive uma futura na biblioteca padrão, possa adotá-la
  sem mudanças e interoperar.

A discussão não terminou, e este projeto é um participante dela, não um
veredicto sobre ela. Se você tem experiência de produção com gettext que diga
respeito a essas escolhas, a [mesma thread][discuss-thread] e as
[Discussions][gh-discussions] deste repositório são onde a discussão continua.

## Linha do tempo { #timeline }

| Quando | O que aconteceu |
| --- | --- |
| meados dos anos 1990 | O GNU gettext estabelece o fluxo PO/POT/MO que quem traduz e as plataformas usam até hoje. |
| 2015 | A [PEP 501] propõe templates de interpolação, com i18n como primeira motivação; adiada. |
| 2016 | As f-strings chegam ao Python 3.6 — a interpolação ganha sua sintaxe, e a tradução não pode usá-la. |
| jul 2024 | A [PEP 750] propõe as t-strings. |
| abr 2025 | A PEP 750 é [aceita][sc-resolution]; a PEP 501 é retirada em seu favor. |
| ago 2025 | A thread [Support t-strings in gettext][discuss-thread] é aberta, com um [pull request][cpython-pr] para a biblioteca padrão. |
| out 2025 | O [Python 3.14] é lançado com t-strings; a issue da biblioteca padrão é encerrada como [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` é lançado como alfa, com a [spec v1](spec.md) e sua suíte de conformidade. |

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
