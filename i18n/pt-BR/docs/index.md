---
description: "Traduza mensagens t-string completas com gettext e Babel com segurança, mantendo a formatação fora do catálogo."
---

# gettext-tstrings

Integração segura de t-strings do Python 3.14+ com gettext e Babel.

Escreva a frase uma única vez, no idioma de origem, com o valor no lugar:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

O catálogo recebe a frase completa `Hello {name}`. Uma tradução pode reordenar
ou repetir `{name}`, mas não pode removê-lo, inventar outro marcador nem impor
sua própria formatação — esta biblioteca verifica isso, e um catálogo danificado
recai no texto de origem em vez de derrubar a aplicação.

!!! note "Nunca usou gettext? O fluxo inteiro em quatro frases"

    **gettext** é a forma padrão de traduzir software, em Python e muito além
    dele. Seu código marca as strings traduzíveis; um *extrator* as coleta em
    um arquivo de template (`.pot`); quem traduz — em geral, não é quem
    programa — preenche um arquivo de catálogo (`.po`) por idioma, que é
    compilado em um `.mo` binário carregado pela aplicação em tempo de
    execução. O nome convencional da função de tradução é `_`, então
    `_(t"Hello {name}")` se lê como "traduza esta frase". O
    **[tutorial](tutorial.md)** percorre o caminho inteiro — marcar, extrair,
    traduzir, compilar, executar — em cerca de cinco minutos.

## O problema que resolve

Uma f-string já foi interpolada quando chega a uma biblioteca —
`f"Hello {name}"` virou `"Hello Ada"`, e traduzir os fragmentos ao redor de um
valor quebra a gramática da maioria dos idiomas. Uma t-string ([PEP 750])
mantém separados texto estático, valores avaliados, expressões de origem,
conversões e especificações de formato — exatamente a separação necessária a
um catálogo de mensagens. Veja [o que isso muda](comparison.md) em relação a
`%(name)s`, `.format()` e strings `$`.

gettext e Babel não definem como uma t-string vira uma mensagem. Esta biblioteca
escolhe uma convenção, registra-a numa
[especificação versionada](spec.md) e inclui uma
[suíte de conformidade](spec.md#conformance).

## As escolhas

- Traduzir mensagens completas, nunca fragmentos de frase.
- Aceitar somente nomes simples, como `{name}`.
- Manter `!r` e `:.2f` sob controle da aplicação e fora do catálogo.
- Permitir reordenar e repetir marcadores conhecidos, sem acesso a atributos ou
  formatação adicional.
- Reutilizar arquivos POT, PO e MO e as ferramentas existentes.

## Instalação

```console
python -m pip install gettext-tstrings
```

Requer Python 3.14 ou mais recente. A renderização **não possui dependências**:
usa apenas o `gettext` da biblioteca padrão.

Extração e validação de catálogos usam [Babel]. Instale o extra no ambiente de
desenvolvimento ou CI em que `pybabel` será executado:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Próximos passos

<div class="grid cards" markdown>

- **[Tutorial](tutorial.md)** — comece aqui: de um diretório vazio a uma
  tradução japonesa funcionando em cinco passos, cada comando mostrado com sua
  saída.
- **[Por que t-strings](comparison.md)** — a mesma mensagem escrita de quatro
  formas, e o que `%(name)s`, `.format()` e strings `$` entregam ao catálogo.
- **[Guia](guide.md)** — a API de execução: plurais, idioma por requisição,
  strings preguiçosas e o que acontece quando um catálogo está errado.
- **[Extração](extraction.md)** — a referência do `pybabel`: configuração,
  nomes de função personalizados e como as ferramentas existentes validam
  esses catálogos de graça.
- **[Especificação](spec.md)** — a convenção t-string ↔ msgid como contrato
  estável e versionado, com uma suíte de conformidade legível por máquinas.
- **[API](api.md)** — tudo que o pacote exporta, em uma página.

</div>

## Este site usa a própria biblioteca

Esta documentação não é apenas uma demonstração traduzida. A navegação, os
rótulos do tema, a linha de copyright e o relatório de build com plurais são
renderizados de catálogos PO pelo próprio `gettext-tstrings`. O
[builder multilíngue](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
exercita mensagens com contexto, marcadores nomeados e as regras de plural dos
dez idiomas em todo build estrito.

## Estado

Este é um projeto alfa. O contrato pequeno e a especificação são a parte
estável; a API Python ainda pode mudar antes da primeira versão estável. São
bem-vindos casos de idiomas adicionais, acompanhamento contínuo de desempenho
e experiência de projetos que usam gettext e Babel em produção.

[Issues e pull requests](https://github.com/yhay81/gettext-tstrings/issues) são
bem-vindos.

## Participe

- Escolha uma
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22).
- Faça perguntas nas
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Discuta ideias de API nas
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Leia o
  [guia de contribuição](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  antes de abrir um pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
