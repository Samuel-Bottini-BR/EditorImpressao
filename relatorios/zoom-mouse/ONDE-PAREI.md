# ONDE-PAREI — zoom para o mouse e nomes do "Mais ajustes" (01/11/2026)

Cópia: `.claude/worktrees/zoom-mouse`, ramo `zoom-mouse-2026-11-01` (parte de `obra-2026-10-26`, `6b4e4f9`).

## Pedido

1. Samuel, 31/10/2026: "mesmo assim, na area de trabalho o zoom se comporta sozinho, porque ele se direciona
   somente para o centro da pagina e não onde o mouse está, que é como o zoom se comporta em outros lugares no
   programa."
2. Print do Samuel (janela 1280 x 657 a 125%): no painel Filtro, "Mais ajustes", nomes cortados: "Igual"
   ("Igualar a luz da página"), "Suavi" ("Suavizar as letras"), "Tirar o chu" ("Tirar o chuvisco").

## Causa achada

1. **Zoom.** Na área de trabalho, Ctrl + roda passava por `TelaConferir._roda_na_pagina`, que chamava
   `vista.definir_zoom(vista.zoom * fator)` sem dizer onde estava o mouse: a página crescia a partir do meio.
   No "Duas lado a lado", `PaginasLadoALado.wheelEvent` chamava `definir_zoom`, que põe o par no meio da largura
   e o alto da página da vez no alto da tela. Além disso, nos dois lugares a página ficava presa no meio de lado
   enquanto era mais estreita que a tela (o limite do deslocamento da "Uma página" e a largura do que rola no lado
   a lado), então mesmo com a conta certa o zoom não iria para o mouse para os lados.
2. **Nomes cortados.** Em `_montar_aba_filtro`, as caixinhas "Igualar a luz da página", "Suavizar as letras" e o
   "Tirar o chuvisco:" com o número ficavam numa MESMA linha. O painel tem largura fixa (300 pontos); a linha
   precisava de uns 480 no Windows, e o Qt espremeu cada peça (a "Igualar..." ficou com 58 dos 180 pontos).

## O que mudou

- `ui/tela_conferir.py`
  - `_roda_na_pagina`: o Ctrl + roda chama `_zoom_no_ponteiro(vista, fator, ponto do mouse)`.
  - `_zoom_no_ponteiro` (novo): guarda em que ponto da página o mouse está, dá o zoom e põe o deslocamento que
    deixa esse ponto debaixo do mouse. Conta pelo zoom e deslocamento de agora (não pelo último desenho): várias
    voltas seguidas dão certo (D-026). Volta a 100%: no meio, como sempre.
  - `_andar_pela_pagina` passou a usar `_tamanho_da_pagina_na_tela` e `_por_o_deslocamento` (as mesmas contas de
    antes, separadas para o zoom usar também).
  - `_por_o_deslocamento`: o limite de quanto a página anda é o de antes OU o da área de rolar da janela do
    Automático (a tela vezes o zoom), o que for maior, sem o meio da página sair da tela. **Ressalva:** isso vale
    também para a roda com zoom (D-568): com Shift, a página mais estreita que a tela pode andar para os lados até
    essa conta (antes ficava presa no meio). Sem isso, rolar depois de um zoom faria a página pular de lado.
  - `_montar_aba_filtro`: "Igualar a luz da página" e "Suavizar as letras" uma por linha (como as caixinhas de
    cima); "Tirar o chuvisco:" com o número na linha dele. Nomes, controles e ações iguais.
- `ui/widgets/paginas_lado_a_lado.py`: `zoom_no_ponteiro` e `_pagina_mais_perto` (novos); o Ctrl + roda usa o
  `zoom_no_ponteiro`. `_largura_do_conteudo`: com zoom, o que rola fica pelo menos a tela vezes o zoom (até o
  dobro), com o par no meio, como a área de rolar do Automático.
- `ui/widgets/paginas_rolando.py`: `_largura_do_conteudo` (gancho; no livro aberto continua a largura da tela).
- Não mudou: os botões "–", "+", "ajustar à tela" (continuam pelo centro); a roda sem Ctrl (D-568); a roda dos
  outros lugares (D-577); o Automático (`PainelDeOpcoes` tem o "Mais ajustes" dele, montado à parte em
  `ui/automatico.py`, já uma caixinha por linha: o conserto 2 não o toca).

## Testes

- Novo: `tests/test_zoom_no_ponteiro.py` (4 casos): Ctrl + roda na Mão e no Endireitar, no lado a lado, e os nomes
  inteiros no "Mais ajustes" (com a letra Segoe UI carregada no teste: no "offscreen" o Qt mede cada letra como
  um quadrado).
- Reversão (§4.7): os 4 falham no código de `6b4e4f9` (arquivos de `ui/` trocados pelos antigos, teste novo
  mantido) — saída em `reversao-no-codigo-antigo.txt`; passam no novo.
- Arquivos que tocam zoom, roda, painel Filtro e tela cheia, um por vez, offscreen: 22 arquivos, todos passaram
  (936 casos, 1 xfail já existente), entre eles `test_decisoes_9b2` 30, `test_livro_aberto` 14, `test_luz_scantailor`
  14, `test_filtros_tela_cheia` 11, `test_paineis_na_tela` 22, `test_promessas` 262. Lista em `testes-locais.txt`.

## Prints (janela de verdade, plataforma do Windows, 1280 x 657)

- `mais-ajustes-antes.png` / `mais-ajustes-depois.png` (e `janela-mais-ajustes-*`).
- `uma-pagina-1-sem-zoom-*.png` e `uma-pagina-2-ctrl-roda-3-vezes-*.png`: a cruz vermelha é onde está o mouse.
- `lado-a-lado-1-sem-zoom-*.png` e `lado-a-lado-2-ctrl-roda-3-vezes-*.png`.

## GitHub

(preencher)

## Perguntas para o Samuel

Nenhuma.
