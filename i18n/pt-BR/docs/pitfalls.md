---
description: "O que traduzir um site pequeno para trinta e cinco idiomas realmente quebra, o que disso a biblioteca consegue detectar para você e o que não consegue."
---

# Armadilhas

Este site é traduzido para trinta e cinco idiomas, e cada uma dessas edições
foi produzida rodando o ciclo que esta documentação ensina. Para os padrões da
indústria é um corpus pequeno, e ainda assim foi suficiente para cair na
maioria das armadilhas que tornam a i18n mais difícil do que parece.

Cada seção abaixo é algo que de fato deu errado aqui, como aquilo se apresentou
na hora e onde fica a linha entre o que a biblioteca verifica por você e o que
continua sendo julgamento seu.

## Renomear uma variável retraduz uma frase { #renaming-a-variable-retranslates-a-sentence }

O msgid é a chave do catálogo, e um nome interpolado está *dentro* dela. Mover
uma constante para o escopo do módulo e escrevê-la em maiúsculas, como o estilo
do Python pede — `author` virando `AUTHOR` —, transformou
`Copyright © 2026 {author} · MIT License` em uma mensagem que nenhum catálogo
jamais tinha visto. Toda tradução dessa linha teria voltado ao ciclo de fuzzy,
em todos os idiomas, por uma renomeação que não mudou nada que um leitor
pudesse ver.

A biblioteca não vai impedir você: as duas grafias são nomes de marcador
válidos. O que ela faz é tornar o nome *digno* de proteção — uma interpolação
precisa ser um [nome simples](internals.md#from-template-to-msgid), de modo que
o que está na chave do catálogo é uma palavra que quem traduz consegue ler, não
uma expressão.

O caso espelhado é seguro por construção. Conversões e especificações de
formato não fazem parte do msgid, então apertar `{amount:,.2f}` para
`{amount:,.0f}` não altera chave nenhuma e não invalida tradução alguma em
lugar algum.

## `nplurals=2` não significa duas strings diferentes { #nplurals-2-does-not-mean-two-different-strings }

Turco, húngaro, persa e bengali declaram todos duas formas plurais, e nos
quatro as duas formas de uma mensagem contada são legitimamente a *mesma
string* — o substantivo permanece no singular depois de um numeral, então
`{n} sayfa` está certo para uma página e para dez. Quem revisa e "corrige" a
duplicação quebra a tradução.

O erro oposto é igualmente fácil. A terceira forma do letão existe para **zero
apenas**; a segunda do esloveno é um **dual**, para exatamente dois; a última
forma do romeno exige a palavra `de`, que as duas primeiras não podem ter.
Preencher esses espaços com um singular e um plural produz um catálogo que está
errado apenas nas contagens que ninguém testa.

Pior: a *ordem* dos espaços não é semântica. O galês indexa suas cinco formas
de modo que `msgstr[0]` é o caso geral e `msgstr[1]` é o singular. Preenchê-los
na sequência óbvia coloca o singular exatamente onde toda mensagem sem contagem
vai encontrá-lo.

A biblioteca não assume nada disso, e é esse justamente o ponto: a regra de
plural do idioma de destino vive no cabeçalho do próprio catálogo, e a [regra
de união/interseção](spec.md) permite que uma tradução tenha mais formas, ou
menos, que a origem. O que ela verifica é a única coisa verificável sem
conhecer o idioma — que cada forma mantenha os marcadores de que precisa.

## Duas formas podem ser idênticas por um motivo { #two-forms-can-be-identical-for-a-reason }

O irlandês tem cinco formas plurais, e no relatório de build deste site várias
delas se escrevem igual. Não é um deslize de copiar e colar: *leathanach*
começa com `l`, e nenhuma das mutações iniciais que os numerais irlandeses
provocam se escreve em `l`. As formas continuam fazendo trabalho de verdade —
o radical alterna entre *leathanach* e *leathanaigh*, e contagens acima de dez
voltam ao singular —, mas nenhum substantivo com o sentido de "página"
mostraria o contraste.

Qualquer verificação que marque formas duplicadas como suspeitas vai marcar
irlandês correto. Um humano que conheça o idioma é o único revisor possível
aqui.

## Uma mensagem só concorda com uma contagem { #a-message-can-only-agree-with-one-count }

O relatório de build deste site informa quantas páginas foram renderizadas e
quanto tempo levou. Escrevê-lo como "Rendered {n} pages in {seconds} seconds"
parece inofensivo e não é traduzível: o gettext seleciona uma forma a partir de
uma contagem, e essa contagem é `n`. A palavra *seconds* teria de concordar com
um número que o maquinário de plural nunca vê.

A correção é fazer da segunda grandeza um símbolo de unidade em vez de uma
palavra, e símbolos de unidade também são localizados: os catálogos deste site
trazem `s`, `с`, `ث`, `שנ׳` e `mp`, e a tipografia do francês, do espanhol e do
sueco quer um espaço antes do símbolo onde a do inglês não quer. Nada disso é
assunto da biblioteca — mas perceber que uma mensagem precisa de *duas*
concordâncias é, e a única ferramenta para isso é escrever a mensagem de outro
jeito.

## Editar uma frase em inglês edita gramática estrangeira { #editing-an-english-sentence-edits-foreign-grammar }

A página inicial dizia "all ten language editions". Remover o número — uma
edição de uma palavra em inglês, feita porque o número vivia ficando
desatualizado — tornou singular um sujeito plural. Espanhol, italiano,
português, russo, ucraniano, grego, neerlandês e hebraico tiveram todos de
reconcordar o verbo; vários precisaram mudar também o particípio.

Uma edição na origem que soa trivial em inglês não é trivial rio abaixo.
Marcá-la como fuzzy, que é o que o `pybabel update` faz, é o mecanismo que dá a
cada tradutor a chance de perceber.

## Diferenças invisíveis sobrevivem a todo copiar e colar { #invisible-differences-survive-every-copy-paste }

O guia cita um diagnóstico que contém `(nаme)` — um escape deliberado,
porque o caractere que ele nomeia é um `а` cirílico que nenhum leitor
distingue do latino. Tradutores deste site converteram esse escape no caractere
real **cinco vezes distintas**, em cinco idiomas diferentes, produzindo a cada
vez uma página que parecia correta e estava errada.

Esta a biblioteca de fato pega, e é a razão de os diagnósticos terem a forma
que têm: um marcador cujas letras misturam sistemas de escrita é
[relatado duas vezes](internals.md#diagnostics-are-part-of-the-design), uma de
forma legível e outra escapada, porque a forma escapada é a única grafia que as
distingue. Um espaço inquebrável dentro das chaves é impresso por ponto de
código pela mesma razão. O verificador de catálogos recusa a mensagem antes que
ela possa ir ao ar.

## Não vazio não é traduzido { #non-empty-is-not-translated }

Um catálogo esqueletado com seus msgids copiados para os msgstrs passa por toda
verificação ingênua: nada está vazio, nada está fuzzy, o conjunto de mensagens
bate exatamente. Uma edição deste site foi ao ar assim por várias horas. O
mesmo aconteceu com oito páginas de outra edição que eram cópias byte a byte da
origem em inglês — o que passa por uma verificação que compara os blocos de
código entre elas, porque são o mesmo arquivo.

Nenhum dos dois é algo que uma biblioteca de tradução consiga enxergar. Ambos
são baratos de testar assim que você sabe que deve: compare com a origem e
exija uma diferença.

## O catálogo não é a única coisa traduzida { #the-catalog-is-not-the-only-translated-thing }

Duas falhas aqui não tiveram nada a ver com o gettext.

Traduzir um título muda a âncora gerada a partir dele, de modo que todo link
entre páginas que aponte para aquela seção quebra — silenciosamente, e só
naquele idioma. Este site fixa a âncora em inglês em todos os títulos, e um
teste deriva a lista esperada da página em inglês.

E o gerador do site vem com traduções de interface para sessenta e oito
idiomas, o que não inclui suaíli nem irlandês. Sem uma delas o build não
degrada para o inglês: o include do template falha e a edição simplesmente não
pode ser gerada. Dois arquivos deste próprio repositório existem para preencher
essa lacuna.

## Suas ferramentas também têm bugs { #your-tools-have-bugs-too }

O passo de CI que esta documentação recomenda para pegar catálogos
desatualizados, `pybabel update --check`, não consegue fazer esse trabalho em
nenhum projeto que use `pgettext` ou `npgettext` — ele relata como desatualizado
todo catálogo que tenha um `msgctxt`, em toda execução, por causa de um bug na
forma como a comparação busca as mensagens. Ele foi descoberto aqui ao tentar
usá-lo, foi reportado upstream e está [descrito por inteiro, com a solução de
contorno](workflow.md#what-ci-gates).

A lição geral é a desconfortável: um portão sempre vermelho é pior que portão
nenhum, porque a equipe o desliga. Verifique que a sua checagem de CI é capaz
de passar antes de confiar nela para falhar.

## Para que serve a biblioteca, em uma linha { #what-the-library-is-for-in-one-line }

A maior parte desta página é julgamento que ferramenta nenhuma assume por você.
O que uma ferramenta *pode* fazer é garantir que uma tradução não consiga mudar
a estrutura da frase que traduz — não consiga descartar um valor, inventar um,
reformatar um nem alcançar seus objetos — e dizer isso em uma frase sobre a
qual quem tem de consertar consiga agir. É tudo o que esta biblioteca promete,
e o resto deste site é como ela cumpre essa promessa.
