# Página em branco pelo botão direito (D-623): entrega

**Em uma frase:** o botão direito numa miniatura da tira de baixo mostra, embaixo do "Desfazer
nesta página", "adicionar página em branco antes" e "adicionar página em branco depois"; a página
em branco tem o tamanho da clicada, entra no livro, no PDF e nos cadernos, "tirar do livro" a
tira, e o Ctrl+Z desfaz.

Teste de **máquina** (provas em `tests/test_decisoes_pagina_em_branco.py`) e janela de verdade
pilotada por mensagens do Windows no Gradus Primus (cópia), com prints. Nada aqui está aprovado.

## O pedido (palavras do Samuel)

Print a-80: "as paginas ainda estão em lugar errado né? eu queria conseguir com botão direito
apertando no meio das paginas aperece opção de adicionar folha em branco."

## Como ficou

- Botão direito numa miniatura da tira: o menu tem "Desfazer nesta página >" (D-621), uma linha, e
  os dois itens novos (print `prints-d623/03-menu-com-o-item-em-destaque.png`). Na página da área
  de trabalho o menu continua só com o "Desfazer nesta página" (a D-623 fala da tira).
- "depois" põe a página em branco logo depois da clicada; "antes", logo antes. Na ferramenta
  Dividir, a miniatura de uma folha inteira vale pela folha: antes da folha ou depois dela.
- A página em branco copia o tamanho da clicada (a folha, a metade, o corte, o ângulo, o tamanho
  de folha e o mover) e sai toda branca. Na tira ela aparece branca. A tela fica na página em que
  estava.
- Uma ação só no Histórico ("Página em branco depois da página 2"). Ctrl+Z tira, Ctrl+Y põe de
  novo. "tirar do livro" a tira do PDF, como qualquer página.
- Pode ser mudada de lugar arrastando (D-615), como as outras.

## O modelo de dados (a mudança que a D-623 autorizou)

Cada página ganhou o campo `inserida`: 0 = veio do PDF (o de sempre); um número = página em branco
posta à mão. O projeto antigo não tem o campo e abre com 0: igual ponto por ponto (prova
`test_d623_projeto_antigo_abre_igual`). A página posta não é "da folha": dividir ou juntar a folha
à mão, o Dividir do Automático e mudar a folha de lugar não a levam junto (prova com a folha
dividida e o "não dividir esta").

Arquivos: `core/paginas_em_branco.py` (novo), `modelos.py`, `historico_acoes.py`,
`core/ordem_das_paginas.py`, `core/dividir_a_mao.py`, `core/automatico.py`, `core/pipeline.py`
(a página posta sai sempre branca), `ui/tela_conferir.py`, `ui/desfazer_nesta_pagina.py`.

## Testes

- Novos, `tests/test_decisoes_pagina_em_branco.py`: 9 casos, todos passam. O menu da miniatura;
  "depois" na 2 vira a 3 do tamanho da 2 (o exemplo do Livro); "antes" na 1; Ctrl+Z (o PDF volta
  igual ponto por ponto) e Ctrl+Y; "tirar do livro"; os cadernos (PDF com a página em branco no
  lugar dela e a lista da etapa 7); a folha dividida e o "não dividir esta"; arrastar a página em
  branco; fechar e abrir o projeto; projeto antigo.
- Reversão: os 9 falham no código de antes (`reversao-d623.txt`).
- Antigos no PC, um arquivo por vez: `testes-no-pc-d623.txt`. Nenhum teste antigo foi mudado.

## Janela de verdade (Gradus Primus, cópia)

Anotações em `anotacoes-d623.txt`, prints em `prints-d623/`. A cópia de teste do Gradus mudou desde
a D-621 (alguém a deixou com as folhas juntas e o "dividir" para refazer): o livro abriu com 70
páginas, e o Ctrl+Y da primeira vez refez esse "dividir" (140 páginas). Não mexe no que se testa.

- `02`, `03`: botão direito na miniatura 2 e o menu.
- `04`: a tira com a página em branco na 3 (71 páginas, 71 no PDF, 141 no caderno da etapa 7).
- `05`: a página 3: "Esta página vai sair em branco"; do tamanho da folha 2 (inteira, deitada).
- `06`, `07`: Ctrl+Z (some) e Ctrl+Y (volta).
- `09`: "antes" na miniatura 1: a página em branco vira a 1.
- `10`: "tirar do livro" na página em branco: sai do PDF.

## Ressalvas

- No piloto, o clique esquerdo por mensagem do Windows num item comum do menu (com a janelinha do
  menu posta fora da tela) fechava o menu sem escolher; o item foi escolhido pelo teclado do
  mesmo menu (setas e Enter, também por mensagens). As caixinhas da D-621 foram clicadas
  normalmente. Na mão do Samuel o clique comum deve valer: é um menu do Qt como os outros.
- A página em branco copia o tamanho da vizinha na hora em que é posta. Se depois a folha da
  vizinha for dividida, a página em branco continua do tamanho de antes (a folha inteira).
- O botão "voltar a página" aparece na página em branco (é o do "deixar em branco"); apertar não a
  faz mostrar a folha da vizinha: ela continua saindo branca.

## Perguntas abertas

Nenhuma bloqueou. Escolhas de detalhe, pelo que o programa já faz: os dois itens vêm embaixo do
"Desfazer nesta página", com uma linha entre eles; a tela não muda de página.
