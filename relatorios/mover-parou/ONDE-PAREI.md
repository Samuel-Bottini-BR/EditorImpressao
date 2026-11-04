# ONDE-PAREI — "mover e dimensionar para de funcionar" (04/11/2026)

Ramo `mover-parou-2026-11-04` (saiu de `obra-2026-10-26`, ponta `249922d2`). Cópia:
`D:\programas\EditorImpressao\.claude\worktrees\mover-parou`.

**Situação: reproduzido; parado numa pergunta para o Samuel. Nenhuma linha do programa foi mudada.**

## Decisões que esta tarefa precisa cumprir

- **D-605** (03/11): "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que
  já está escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os
  agentes precisam ler".
- **D-008** (22/09 e 26/10): "quero conseguir redimensionar o conteudo tambem" · "a ferramenta de mover não deveria
  estar vinculada ao corte de bordas, deveriam ser duas coisas independentes" · "como é no photoshope, que você
  arrasta a hora que quiser e aumenta a hora que quiser". Na prática: "ferramenta própria, sempre ativa".
- **D-541** (27/10, apoiada na D-008): arrastar em qualquer lugar da área branca ou da página move (ao vivo); o meio
  do conteúdo fica dentro da área branca; puxar um canto aumenta/diminui na mesma proporção, de 5% até 4 vezes; o
  número "Tamanho do conteúdo (%)" faz o mesmo.
- **D-540** (tecla F), **D-542** (Centralizar e ímã olham o impresso), **D-543**/**D-017** (aviso da parte de fora,
  "Avisar e não reduzir"), **D-544** (Mover separado do Cortar), **D-545** ("usar em todas..."), **D-546**/**D-547**
  (o que cada tela mostra), **D-056** (linhas de apoio).
- Vista da área de trabalho: **D-006**/**D-015** ("Duas lado a lado" = pares rolando, na barra de baixo e no menu
  Ver), **D-601**/**D-609**/**D-610** (no Dividir o "Duas lado a lado" é a folha inteira com a linha; D-610: dividir em
  "Duas lado a lado" passa para "Uma página" — ainda não construída em `249922d2`).

## O que já está escolhido e testado aqui

- `tests/test_decisoes_mover.py` (13 provas da etapa 5: tecla F, área branca, arrastar → PDF, canto, Centralizar,
  %, voltar como veio, D-017, linhas de apoio, "usar em todas...", letra F com foco na página de marcar). No PC em
  04/11: **13 passaram** (sem mudança de código).
- `tests/test_previa_composta.py`, `tests/test_paineis_na_tela.py`, `tests/test_visualizador.py` (modo do conteúdo).
- Vista: `tests/test_decisoes_ver.py` (fora do Dividir, "Duas lado a lado" = os pares;
  `test_no_dividir_a_folha_inteira_continua`: com a ferramenta "mao", os pares voltam),
  `tests/test_decisoes_dividir_metade.py` (`escolher_ferramenta("mao")` em "Duas lado a lado" → os pares).

## O que foi feito

1. Cópia do projeto do Gradus (pasta `dados-teste-rodada-de-consertos`, só lida) e do PDF para
   `scratchpad\mover-parou-dados`; programa aberto ali, janela de verdade fora da tela, cliques/arrastos/teclas/roda
   por mensagens do Windows (`relatorios/mover-parou/piloto.py`, fases t1 a t4; anotações `anotacoes-t*.txt`).
2. Registro de ações lido: só tem 17 linhas, de 02:27:01 a 02:29:32 (o arquivo é regravado quando se faz uma ação
   nova depois de Ctrl+Z, `historico_acoes.registrar`; o que veio antes de 02:27 foi desfeito antes). O print a-56 do
   Samuel é das 02:27, no Dividir, **em "Duas lado a lado"**; às 02:27:06 "dividir todas".
3. Situações tentadas (cada uma seguida de um arrasto na página):

| Situação | Arrasto move? |
|---|---|
| Caminho do registro em "Uma página": arrastar a página 2, diminuir pela roda no número até 88%, digitar 100 | sim (t1, t3) |
| Ctrl+Z, Ctrl+Z+Ctrl+Y | sim |
| Trocar de página (setas) e voltar | sim |
| Trocar de ferramenta (Cortar, Dividir) e voltar com F | sim |
| Zoom pelo "+", Ctrl+roda, Shift+roda, "ajustar à tela" | sim (t4) |
| Diminuir a 5%, Centralizar, puxar o canto, levar o meio até a beirada | sim (ver ressalvas) |
| Soltar o mouse em cima do painel; "ver no Mover"; "está bom assim" | sim |
| **Dividir em "Duas lado a lado" → "dividir todas" → tecla F** | **NÃO** (t3, p2) |
| **Na ferramenta Mover, clicar "Duas lado a lado"** | **NÃO** (t2, t4) |
| **Na ferramenta Mover, ligar "antes / depois"** | **NÃO** (t3, t4, p3) |
| Voltar a "Uma página" | volta a mover |

## O passo a passo que faz o Mover "parar"

1. Ferramenta Dividir, barra de baixo em **"Duas lado a lado"** (é o que a própria frase do Dividir manda fazer para
   arrastar a linha, D-601). Print `p1-dividir-duas-lado-a-lado-depois-de-dividir-todas.png`.
2. "dividir todas" (ou não; basta estar em "Duas lado a lado").
3. Tecla **F** (ou a trilha/menu): o título diz "Mover e redimensionar", o painel diz "Arraste a página para mover.
   Puxe um canto para aumentar ou diminuir.", mas no meio da tela estão **os pares** (a página 1 sozinha à direita
   parece uma página só, sem os quadradinhos azuis). Arrastar não faz nada. O número "Tamanho do conteúdo",
   "Centralizar" e "voltar como veio" continuam mudando a página. Print `p2-tecla-F-mover-nos-pares-arrastar-nao-
   move.png` (e `p5-...`: a página diminuída nos pares).
4. O mesmo com o **"antes / depois"** ligado: print `p3-mover-com-antes-depois-arrastar-nao-move.png`.
5. Clicando "Uma página", volta a funcionar (`p4-mover-em-uma-pagina-arrasta.png`).

## A causa

`ui/tela_conferir.py`, `_acertar_a_vista_da_pagina` (linhas 7559-7579): fora do Dividir, quando a barra de baixo
está em "Duas lado a lado" ela põe **os pares** (`PaginasLadoALado`) no lugar da ferramenta, e com "antes / depois"
põe a comparação. O mouse vai para esses quadros, que não sabem mover (o clique nos pares só escolhe a página da
vez). A escolha "Duas lado a lado" fica guardada ao trocar de ferramenta (`self.mostrar`), então quem veio do
Dividir em "Duas lado a lado" chega ao Mover nos pares sem ter clicado em nada. Não é erro gravado (nada no
`erros.log`): o programa faz o que está escrito, só que o painel do Mover continua à vista dizendo "Arraste".
O mesmo acontece com Cortar, Endireitar e as ferramentas de marcar (mesma linha de código); só o Dividir foi
tratado (D-601).

A D-610 (a fazer, agente do Dividir) muda só o caso "dividir esta/todas em Duas lado a lado"; não cobre: ir ao
Mover estando em "Duas lado a lado" sem dividir, clicar "Duas lado a lado" no Mover, nem o "antes / depois".

## Por que não consertei

Não há decisão no Livro sobre o que uma ferramenta de mexer na página faz quando a tela está em "Duas lado a lado"
ou "antes / depois" (procurado em DECISOES.md, PLANO-DEFINITIVO.md e Central). Qualquer conserto muda o que a tela
mostra (D-605, §11.7): é escolha dele.

## Perguntas para o Samuel

**P1 (com print p2):** "Quando você está em 'Duas lado a lado' (por exemplo, vindo do Dividir) e aperta F, a tela
continua mostrando as páginas em pares, e nos pares não dá para arrastar: por isso o Mover 'parou'. Sugestão: ao
escolher o Mover, a tela passa sozinha para 'Uma página' (e o 'antes / depois' desliga), como você pediu no Dividir
(D-610). Pode ser assim?"

Opções por extenso (caso real: Gradus, Dividir em "Duas lado a lado", tecla F, página 2):
- **A (recomendo):** ao escolher o Mover, a tela vai sozinha para "Uma página" (e o "antes / depois" desliga). Se
  depois ele clicar "Duas lado a lado" ou "antes / depois" com o Mover na mão, vê os pares/a comparação só para
  olhar; para mexer, "Uma página" (ou F de novo).
- **B:** com o Mover na mão, "Duas lado a lado" e "antes / depois" ficam apagados (cinza) com o balão "No Mover a
  tela mostra uma página por vez". (Foi o que o Dividir tinha antes da D-601, e ele mudou.)
- **C:** o Mover passa a funcionar dentro dos pares (arrastar a página da vez no par). Mais trabalho.

**P2:** vale o mesmo para Cortar, Endireitar e as ferramentas de marcar, que param do mesmo jeito?

## Provas

- `relatorios/mover-parou/teste_que_pegaria.py` (fora de `tests/` até a resposta): arrasta no que está NA TELA no
  lugar da página. Rodado no PC em `249922d2` (copiado para `tests/` e apagado depois): **2 falharam** (Dividir em
  "Duas lado a lado" → F: "a tela está em PaginasLadoALado"; "antes / depois" ligado) e **1 passou** (guarda: em
  "Uma página" move).
- `tests/test_decisoes_mover.py` no PC: 13 passaram.
- GitHub: não rodado (nenhum arquivo do programa nem de `tests/` mudou; a rodada testaria o mesmo `249922d2`).

## Por que os testes que já existiam não pegaram

Os 13 testes do Mover (`tests/test_decisoes_mover.py`, `_arrastar`) mandam o arrasto **direto** ao visualizador do
Mover (`vis.mousePressEvent(...)`), que recebe o evento mesmo escondido atrás dos pares. Conferem a conta (tela =
PDF, canto, %, Centralizar, aviso), mas nunca o que está À VISTA no lugar da página. E sempre começam em "Uma
página" (`_no_mover` abre o livro e aperta F). Os testes da vista (`test_decisoes_ver.py`) conferem que os pares
aparecem fora do Dividir, mas nunca com uma ferramenta de mexer na página. O teste que pegaria é o
`teste_que_pegaria.py`: entra no Mover vindo do Dividir em "Duas lado a lado" (e com "antes / depois") e arrasta no
widget que está embaixo do ponto.

## Ressalvas e bugs para a Lista de bugs (não consertados)

- Conteúdo muito pequeno (5%, uns 25 pontos na tela): apertar bem no meio dele pega um canto (os quatro cantos se
  sobrepõem, `DISTANCIA_PEGA` = 14) e o arrasto diminui em vez de mover (já está no mínimo: nada muda). Apertar em
  outro lugar da área branca move. Visto no piloto t2 (`tamanho-5`, `centralizar`).
- O meio do conteúdo não passa da beirada da área branca (D-541): arrastar mais para aquele lado não faz nada. É a
  decisão, mas pode parecer "parou" (piloto t2, `antes-depois-e-volta`).
- Não deu para reproduzir com a janela ATIVA (o foco do teclado no número "Tamanho do conteúdo" depois de digitar
  100): pilotar com a janela ativa tomaria o teclado do Samuel. Com a janela inativa, arrastar depois de digitar 100
  funcionou.
