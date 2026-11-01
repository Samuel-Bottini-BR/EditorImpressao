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

Rodada 41324371101 ("Testes no Windows", ramo `zoom-mouse-2026-11-01`, commit `c269e33`):
- 1ª tentativa: partes 2 a 5 e "Botões e prints da janela real" passaram; parte 1 falhou só em
  `test_promessas.py::test_p090_por_pagina_e_por_motivo` (ERROR na desmontagem: uma prévia em segundo plano
  (`ui/tarefas.py::_folha_crua`) tentou abrir o PDF do teste que já tinha sido apagado; "um botão falhou por
  baixo (erros.log)"). Não passa pelo código mexido aqui; no PC, `test_promessas` passou inteiro (262).
- 2ª tentativa (só a parte que falhou, rodada de novo uma vez): **passou**. Rodada inteira: sucesso.

## Perguntas para o Samuel

Nenhuma.

---

## Defeito de 01/11/2026: Shift + roda no "Duas lado a lado" com zoom trocava de página

Samuel, testando a junção `d6d6e6f`: "1- funcionando" · "2- funciona o zoom mas com shift para os lados não
funciona ele rola as paginas para pagina, no caso troca de pagina." · "3- ok". A escolha de a página sair um pouco
do meio (e o Shift mover página estreita) foi aprovada: "sim" (D-599).

- **Causa:** no lado a lado, a roda sem Ctrl ia para o rolar padrão do Qt (`PaginasRolando.wheelEvent` ->
  `QScrollArea`), que usa o Shift para rolar de página em página na barra de pé. Então Shift + roda descia
  páginas (no print de antes, da página 3 para a 6) em vez de andar para os lados.
- **Conserto:** `ui/widgets/paginas_lado_a_lado.py`, `PaginasLadoALado.wheelEvent`: com zoom e Shift, a roda anda
  na barra de baixo, o mesmo tanto que a roda anda para cima e para baixo (3 linhas por dente); a roda de lado
  (tilt) também. Sem zoom, e a roda sem Shift, como antes. Nada mais mudou.
- **Teste:** `tests/test_zoom_no_ponteiro.py::test_bug_01_11_shift_roda_no_lado_a_lado_com_zoom_anda_para_os_lados`.
  Falha em `a6b9e02` (arquivo antigo trocado, teste novo mantido; saída em
  `reversao-shift-no-codigo-antigo.txt`) e passa no novo.
- **Testes no PC** (offscreen, um por vez; `testes-locais-shift.txt`): 10 arquivos, todos passaram (418 casos, 1 xfail
  que já existia): test_zoom_no_ponteiro 5, test_decisoes_9b2 30, test_livro_aberto 14, test_decisoes_9b1 25,
  test_decisoes_ver 11, test_decisoes_automatico_ver_como_fica 22, test_ajustar_pedaco 13, test_dividir_scantailor 13,
  test_girar_cartoes_e_previas 23, test_promessas 262.
- **Prints:** `shift-lado-a-lado-1-com-zoom-*.png` e `shift-lado-a-lado-2-shift-roda-3-vezes-*.png` (cruz = mouse).
  Antes: as páginas descem (página 3 -> 6). Depois: o par anda para os lados, mesma altura, página 3.
- **GitHub:** (preencher)
