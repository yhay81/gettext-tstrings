---
description: "Traduza mensagens t-string completas com gettext e Babel, mantendo os valores e a formatação fora do catálogo."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Traduza mensagens completas<br>com t-strings do Python

O `gettext-tstrings` liga as t-strings do Python 3.14+ a catálogos gettext
padrão e ao ferramental do Babel. Os valores e a formatação ficam no código da
aplicação; quem traduz trabalha com mensagens completas e marcadores `{name}`
simples:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

O catálogo contém `Hello {name}`. Uma tradução pode mover ou repetir `{name}`.
Se ela remover, renomear ou reformatar o marcador, a validação do catálogo
relata o erro. Se uma entrada inválida ainda assim chegar à produção, a
biblioteca registra um aviso e renderiza a mensagem de origem, em vez de
derrubar a aplicação.

[Comece o tutorial de cinco minutos :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Compare as alternativas](comparison.md){ .md-button }

Alfa · Python 3.14+ · catálogos PO/MO padrão · sem dependências de execução de terceiros
{ .home-facts }

Este site pratica o que documenta: cada edição de idioma —
navegação, rótulos e o relatório de build com plurais — é renderizada de
catálogos PO pelo
[próprio `gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Isto serve para você? { #is-this-for-you }

**Serve hoje quando** sua aplicação roda em Python 3.14 ou mais recente; você
já usa gettext e Babel, ou quer adotar o fluxo PO/MO dessas ferramentas; e você
quer a sintaxe de t-strings com marcadores nomeados que são verificados antes
de serem renderizados.

**Ainda não serve quando** você precisa do Python 3.13 ou anterior; você exige
uma API Python estável — isto é um alfa, e a [especificação](spec.md) é a parte
que já se acomodou; ou quase todo o seu texto traduzível vive em uma linguagem
de template, e não no código Python.

Já tem catálogos? Eles continuam funcionando. `_("Hello {name}").format(name=name)`
e `tr(t"Hello {name}")` produzem o mesmo msgid, então as traduções existentes
sobrevivem à troca — a [Migração](migration.md) percorre a mudança inteira.

## O que o catálogo pode dizer { #what-the-catalog-may-say }

**Uma tradução não pode mudar a estrutura da mensagem que traduz.** Essa é toda
a promessa, e o resto deste site decorre dela. Uma tradução pode reordenar ou
repetir `{name}`, e pode reescrever todas as outras palavras ao redor. Ela não
pode remover o marcador, inventar um novo, atravessá-lo para alcançar seus
objetos nem acrescentar formatação própria.

A biblioteca verifica isso na entrada — quando os catálogos são compilados — e
de novo na renderização, que é a diferença entre um erro encontrado na revisão
e um erro encontrado por quem usa a aplicação.

!!! note "Nunca usou gettext? O fluxo inteiro em quatro frases"

    **gettext** é a forma padrão de traduzir software, em Python e muito além
    dele. Seu código marca as mensagens traduzíveis; um *extrator* as coleta em
    um arquivo de template (`.pot`); quem traduz — em geral, não é quem
    programa — preenche um arquivo de catálogo (`.po`) por idioma, que é
    compilado em um `.mo` binário carregado pela aplicação em tempo de
    execução. O nome convencional da função de tradução é `_`, então
    `_(t"Hello {name}")` se lê como "traduza esta mensagem". O
    **[tutorial](tutorial.md)** percorre o caminho inteiro — marcar, extrair,
    traduzir, compilar, executar — em cerca de cinco minutos.

## O problema que resolve { #the-problem-it-solves }

Uma f-string já foi interpolada quando chega a uma biblioteca —
`f"Hello {name}"` virou `"Hello Ada"`, e traduzir os fragmentos ao redor de um
valor quebra a gramática da maioria dos idiomas. Uma t-string ([PEP 750])
mantém separados o texto estático, os valores avaliados, as expressões de
origem, as conversões e as especificações de formato — exatamente a separação
que um catálogo de mensagens precisa.
[O que isso muda](comparison.md), em relação a `%(name)s`, `.format()` e
strings `$`.

Nada em gettext ou no Babel diz como uma t-string vira uma mensagem, no
entanto. Esta biblioteca faz essa escolha, registra-a como
[especificação versionada](spec.md) e inclui a
[suíte de conformidade](spec.md#conformance) que a verifica.

## As regras de projeto { #the-design-rules }

- Traduzir mensagens completas, nunca fragmentos de frase.
- Aceitar somente nomes de variável simples, como `{name}`.
- Manter `!r` e `:.2f` sob controle da aplicação e fora do catálogo.
- Permitir que traduções reordenem e repitam marcadores conhecidos, sem
  deixá-las alcançar atributos ou acrescentar formatação.
- Reutilizar arquivos POT, PO e MO comuns, e as ferramentas que já os leem.

E a lista correspondente do que ela deliberadamente não faz: não localiza
números, moedas ou datas — [formate esses valores antes](guide.md#locale-aware-values),
com o Babel; não escapa a saída renderizada para HTML, para um shell ou para um
terminal; e não consegue julgar se uma tradução está *correta*, apenas se os
marcadores dela estão intactos.

## Instalação { #install }

```console
python -m pip install gettext-tstrings
```

Requer Python 3.14 ou mais recente. **A renderização não tem dependências**:
usa o `gettext` da biblioteca padrão e nada mais.

A extração e a validação de catálogos passam pelo [Babel], então instale esse
extra onde o `pybabel` for executado, que costuma ser um ambiente de
desenvolvimento ou de CI, e não uma imagem de produção:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Próximos passos { #where-to-go-next }

**Comece aqui** — sem pressupor experiência com gettext:

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — de um diretório vazio a uma tradução japonesa
  funcionando em cinco passos, cada comando mostrado com sua saída.
- **[Por que t-strings](comparison.md)** — a mesma mensagem escrita de quatro
  formas, e o que `%(name)s`, `.format()` e strings `$` entregam ao catálogo.

</div>

**Use na prática** — as referências de trabalho:

<div class="grid cards" markdown>

- **[Guia](guide.md)** — a API de execução: qual ponto de entrada usar,
  plurais, idioma por requisição, strings adiadas e o que acontece quando um
  catálogo está errado.
- **[Extração](extraction.md)** — a referência do `pybabel`: configuração,
  nomes de função personalizados e como as ferramentas existentes validam
  esses catálogos de graça.
- **[Em produção](workflow.md)** — o ciclo como uma equipe o executa: o ciclo
  de atualização, entradas fuzzy, portões de CI, plataformas de tradução e o
  envio para produção.
- **[Migração](migration.md)** — adotar isto em um projeto que já tem
  catálogos, um ponto de chamada por vez.
- **[Para quem traduz](translators.md)** — uma única página para entregar a
  quem edita os arquivos `.po`.

</div>

**Entenda a fundo** — da história à implementação:

<div class="grid cards" markdown>

- **[Contexto](background.md)** — por que esta biblioteca existe: trinta anos
  de gettext, duas PEPs e a discussão na biblioteca padrão que se encerrou sem
  resposta.
- **[Armadilhas](pitfalls.md)** — o que traduzir este site para trinta e cinco
  idiomas realmente quebrou, e que metade disso uma ferramenta consegue pegar.
- **[Como funciona](internals.md)** — do objeto template da PEP 750 à string
  renderizada, e os caches que tornam a verificação barata.

</div>

**Referência** — os contratos:

<div class="grid cards" markdown>

- **[API](api.md)** — tudo que o pacote exporta, em uma página.
- **[Especificação](spec.md)** — a convenção t-string ↔ msgid como contrato
  estável e versionado, com uma suíte de conformidade legível por máquinas.

</div>

## Estado { #status }

| | |
| --- | --- |
| Versão do pacote | 0.1.0a8 |
| Estabilidade da API | alfa — a API Python ainda pode mudar |
| [Especificação](spec.md) | v1, com uma [suíte de conformidade](spec.md#conformance) |
| Python | 3.14 e mais recentes; testado em 3.14, 3.14t (free-threaded) e 3.15 |
| Babel | 2.18 ou mais recente, e apenas onde o `pybabel` roda |
| Dependências de execução | nenhuma — o `gettext` da biblioteca padrão |
| Formato de catálogo | POT, PO e MO comuns |
| Mudanças | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Um alfa. O contrato é pequeno de propósito e a [especificação](spec.md) é a
parte estável dele; a API Python ainda pode mudar. Antes de uma versão estável,
isto precisa de casos de idioma mais amplos, acompanhamento contínuo de
desempenho, revisão de API por quem usa gettext e Babel a sério e testes de
compatibilidade em todas as versões suportadas de Python e do Babel.

[Issues e pull requests](https://github.com/yhay81/gettext-tstrings/issues) são
bem-vindos — um alfa é exatamente o momento em que ainda vale a pena discutir a
interface.

## Participe { #join-the-community }

- Escolha uma
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  para uma contribuição bem delimitada.
- Faça perguntas de uso nas
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Leve fluxos gettext de produção e ideias de API para as
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Leia o
  [guia de contribuição](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  antes de abrir um pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
