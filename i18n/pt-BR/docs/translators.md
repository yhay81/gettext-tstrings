---
description: "O contrato dos marcadores para quem edita os arquivos .po: o que você pode mudar, o que precisa deixar em paz e como ler os erros."
---

# Para quem traduz

Esta página é para quem edita o catálogo, não para quem escreve o código. Ela é
curta de propósito, e foi feita para ser referenciada ou copiada nas instruções
de tradução do seu próprio projeto.

Nada aqui exige que você leia Python. Tudo aqui trata de uma coisa só: os
pedaços de uma mensagem que ficam entre chaves.

## O que é um marcador { #what-a-placeholder-is }

Uma mensagem em um catálogo pode conter nomes entre chaves:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` é um **marcador**. Quando o programa exibe esta mensagem, ele
substitui `{name}` por um valor que ele mesmo fornece — o nome de uma pessoa, o
nome de um arquivo, um número. O marcador não é uma palavra a traduzir; é um
espaço reservado.

Sua tradução vai no `msgstr`, e precisa preservar esse espaço:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## O que você pode mudar, e o que não pode { #what-you-may-change-and-what-you-may-not }

Você **pode**:

- **Mover um marcador** para onde a gramática do idioma de destino quiser,
  inclusive para o começo da mensagem.
- **Repetir um marcador**, se o idioma precisar do valor duas vezes.
- **Reescrever todas as outras palavras**, incluindo pontuação, espaçamento e
  ordem da frase.

Você **não pode**:

- **Traduzir o nome que está dentro das chaves.** `{name}` continua `{name}`,
  mesmo em um idioma que não escreve mais nada em letras latinas.
- **Remover as chaves**, nem escrever o nome sem elas.
- **Trocar as chaves ASCII `{` `}` pelas de largura total `｛` `｝`.** Muitos
  métodos de entrada produzem as formas de largura total; elas parecem quase
  idênticas e não funcionam.
- **Acrescentar formatação**, como `{name!r}` ou `{amount:.2f}`. Como um valor
  é exibido se decide no programa, não no catálogo.
- **Inventar um marcador** que não esteja no `msgid`.

Se uma mensagem precisa de um valor que o original não oferece, essa é uma
mensagem que quem desenvolve precisa mudar. Diga isso em vez de improvisar uma
saída.

## Formas de plural { #plural-forms }

Uma mensagem com contagem chega com um espaço de `msgstr` por forma de plural
do seu idioma, e é o seu idioma que decide quantas são — uma para o japonês,
duas para o alemão, três para o russo, seis para o árabe. Preencha todos os
espaços que o catálogo lhe der.

Duas regras que costumam pegar as pessoas de surpresa:

- **Os espaços não são "singular, plural, mais plural".** Cada índice
  significa o que a regra de plural do seu idioma disser que ele significa. A
  terceira forma do letão é só para o zero; a segunda do esloveno é para
  exatamente dois; o galês coloca o caso geral no índice 0 e o singular no
  índice 1.
- **Dois espaços podem legitimamente ter o mesmo texto.** Em turco, húngaro,
  persa e bengali um substantivo permanece no singular depois de um numeral,
  então as duas formas de uma mensagem com contagem são a mesma string. Isso
  está correto; não é um deslize de copiar e colar.

As regras de marcadores acima valem para cada forma independentemente.

## Entradas fuzzy { #fuzzy-entries }

Uma entrada marcada como `fuzzy` é um palpite da máquina: quem desenvolve mudou
a mensagem original, e o ferramental emparelhou o texto novo com sua tradução
antiga para você ter de onde partir.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Uma entrada fuzzy **não é usada pelo programa** — ele mostra o original não
traduzido no lugar — até que alguém revise o texto e remova a marca `fuzzy`. A
maioria dos editores de PO tem um botão exatamente para isso.

## Como ler as mensagens de erro { #reading-a-failure-message }

O ferramental verifica os marcadores quando o catálogo é compilado, e a
mensagem é escrita para você, não para quem programa. Relatar apenas que
`{name}` está faltando não leva a lugar nenhum quando você está vendo esses
caracteres à sua frente, então, onde um marcador parece presente mas não está,
a mensagem diz por quê. Contra o original `Hello {name}`, cada um destes casos
é relatado sob `translation does not match the source placeholders:`

| A sua tradução contém | Motivo apresentado |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Caracteres que não podem ser vistos recebem um tratamento próprio. Um espaço
inseparável dentro das chaves é algo que um método de entrada produz e que
nenhum editor mostra, então a mensagem o imprime por code point, em vez de
nomear um caractere que você jamais encontraria:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Um nome cujas letras misturam sistemas de escrita — o caso do homoglyph, em que
um `а` cirílico é indistinguível de um latino — é mostrado duas vezes, uma
legível e outra escapada, que é a única forma capaz de diferenciar os dois:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

A mesma desambiguação vale quando um nome grego ou cirílico escrito inteiramente
em um só sistema entra em conflito com um nome ASCII de origem, inclusive no
caso do `a` latino contra o `а` cirílico de uma única letra.

Se você encontrar um destes casos e a correção não for óbvia, o movimento
seguro é apagar o marcador que você digitou e copiar o que está no `msgid`.

## O que as verificações não conseguem fazer { #what-the-checks-cannot-do }

O ferramental confirma que os seus marcadores estão intactos. Ele não consegue
dizer se a tradução está exata, natural ou adequada ao contexto — isso continua
inteiramente com você.

Duas coisas ajudam mais do que qualquer verificação:

- **Leia o comentário para quem traduz.** Uma linha começando com `#.` acima da
  mensagem é quem desenvolve contando a você onde ela aparece e o que ela
  significa.
- **Pergunte sobre o `msgctxt`.** Quando a mesma palavra aparece duas vezes com
  contextos diferentes, é porque as duas precisam ser traduzidas de formas
  diferentes — "Open" o botão e "Open" o estado, por exemplo.
