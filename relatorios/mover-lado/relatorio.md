# D-612: o Mover funciona em "Duas lado a lado" — relatório do implementador (04/11/2026)

Ramo `mover-lado-2026-11-04` (saiu de `obra-2026-10-26` em `dd7a648c`). Teste de **máquina** (testes
automáticos e piloto da janela de verdade). O teste de **olho** é do Samuel.

## O que mudou, em uma frase

Com a ferramenta Mover e a vista em "Duas lado a lado", a página da vez dentro dos pares passa a ser o
próprio Mover: arrastar move, puxar o canto muda o tamanho, o número e a tecla F valem. A vista não muda
sozinha.

## Palavras do Samuel

Pergunta: "Ao escolher Mover, Cortar, Endireitar ou marcar, a tela passa sozinha para Uma página?" →
"1 - ele tem que funcionar com paginas lado a lado também".

## Como ficou

- Nos pares, a página da vez mostra o Mover como na "Uma página": a área branca, a página por cima, os
  quatro cantos azuis, a parte que passa da beirada apagada com listras vermelhas (D-543). A vista se
  ajusta para caber a área branca e a página inteira (D-541), dentro do lugar da página no par.
- A outra página do par continua a prévia de sempre. Clicar nela faz dela a página da vez (como já era);
  o Mover passa para ela.
- A roda do mouse em cima da página do Mover faz o mesmo que no resto dos pares: Ctrl+roda dá zoom no par
  (D-570), sem Ctrl rola.
- "Uma página", outra ferramenta, "antes / depois", Dividir: o Mover volta para o lugar de sempre, com o
  zoom que tinha. Nada muda nesses.
- Cortar, Endireitar, marcar e "antes / depois": **não mexidos** (esperando a resposta do Samuel). Para
  estender, basta pôr a ferramenta na lista `FERRAMENTAS_NO_PAR` (`ui/tela_conferir.py`); a de marcar
  precisa também de um lugar de volta.

## Onde (arquivos)

- `ui/tela_conferir.py`: `FERRAMENTAS_NO_PAR`; `_acertar_a_vista_da_pagina` chama
  `_acertar_a_ferramenta_no_par`; novas `_acertar_a_ferramenta_no_par`, `_devolver_a_peca_do_par`,
  `_roda_na_peca_do_par`; `eventFilter` (a roda da peça vai aos pares); `_limpar_abas` (devolve a peça
  antes de fechar o livro).
- `ui/widgets/paginas_lado_a_lado.py`: `definir_ferramenta`, `tirar_ferramenta`,
  `_por_a_ferramenta_no_lugar`; `_arrumar` e `ir_para` acertam o lugar da peça.
- `ui/widgets/visualizador.py`: `folga_da_moldura` (de fábrica a de sempre, 32; 8 só nos pares).
- `tests/test_decisoes_mover_lado.py` (novo, 7 provas).

## Prints (janela de verdade, Gradus, cópia dos dados de teste)

- `prints/p02-dividir-duas-lado-a-lado-folha-inteira.png`: Dividir em "Duas lado a lado", a folha inteira
  com a linha (D-601); a linha anda com o mouse (D-609).
- `prints/p03-F-mover-nos-pares.png`: tecla F, a vista continua nos pares, a página da vez com os cantos
  azuis; a tira embaixo em pares (D-611).
- `prints/p04-arrastou-nos-pares.png`: arrastada 12% para a esquerda; a parte de fora vermelha com
  listras; o aviso "Parte do que está impresso vai ficar de fora".
- `prints/p05-ctrl-z-ctrl-y.png`: Ctrl+Z desfaz, Ctrl+Y refaz.
- `prints/p06-canto-nos-pares.png`: canto puxado, 85%, o número acompanha.
- `prints/p07-numero-80-nos-pares.png`: 80 digitado no número.
- `prints/p08-ctrl-roda-zoom-nos-pares.png`: Ctrl+roda em cima da página do Mover dá zoom no par.
- `prints/p09-outra-pagina-do-par.png`: clique na outra página do par, ela vira a da vez com o Mover.
- `prints/p10-uma-pagina-mover.png`: "Uma página", o Mover de sempre.
- `prints/p11-cortar-nos-pares.png`: Cortar em "Duas lado a lado", os pares de sempre.
- Piloto: `piloto.py`, **20 de 20** conferências (`conferencias.txt`, `anotacoes-piloto.txt`).

## Testes no PC (um arquivo por vez)

| arquivo | resultado |
|---|---|
| test_decisoes_mover | 13 passaram |
| test_decisoes_mover_lado (novo) | 7 passaram |
| test_decisoes_ver | 11 passaram |
| test_decisoes_dividir_metade | 6 passaram |
| test_decisoes_dividir_arrastar | 16 passaram |
| test_decisoes_tira_em_pares | 4 passaram |
| test_previa_composta | 10 passaram |
| test_paineis_na_tela | 22 passaram |
| test_visualizador | 70 passaram |
| test_zoom_no_ponteiro | 5 passaram |
| test_decisoes_9b2 | 30 passaram |
| test_livro_aberto | 14 passaram |
| test_decisoes_dividir_linha | 13 passaram |
| test_decisoes_dividir | 21 passaram |
| test_dividir_na_tela | 9 passaram |
| test_decisoes_marcacoes | 19 passaram |
| test_guias | 14 passaram |
| test_decisoes_shift_todas_as_telas | 10 passaram |
| test_decisoes | 26 passaram |

Depois do segundo conserto (a roda), rodados de novo: test_decisoes_mover_lado 7, test_zoom_no_ponteiro 5,
test_decisoes_9b2 30, test_decisoes_ver 11 — todos passaram. **Nenhum teste antigo foi mudado.**

**Teste de reversão:** `tests/test_decisoes_mover_lado.py` no código antigo (`dd7a648c`, os três arquivos de
`ui/` voltados): **5 falharam** (arrastar nos pares, vindo do Dividir, canto, número/peça nos pares, outra
página do par) e 2 passaram (são guardas do que já funcionava: "Uma página"/outra ferramenta/Dividir, e o
Ctrl+roda nos pares).

## Rodada do GitHub

Rodada **41856247413** (ramo `mover-lado-2026-11-04` em `bb11ff93`): **passou inteira** — as 5 partes da
suíte, os botões e prints da janela real, e o resumo.

## Ressalvas

- **Achado do piloto, já consertado:** na janela de verdade, Ctrl+roda em cima da página do Mover dava zoom
  mas pulava para a última página (a conta do ponto passava pela tela inteira). Consertado (commit
  `1aa98650`); a prova automática confere que a página da vez não muda, mas na janela de teste do PC (sem
  tela) a conta errada não aparecia: quem pegou foi o piloto (`piloto_roda.py`: Cortar e Mover agora iguais).
- Nos pares, a página do Mover fica com 8 pontos de folga em volta (para os cantos azuis aparecerem
  inteiros): ela sai um pouco menor que a outra página do par. Com o conteúdo passando da beirada, a área
  branca fica ainda menor, porque a vista mostra a página inteira (D-541), como na "Uma página".
- Página da vez tirada do livro (não aparece nos pares): o Mover fica fora dos pares, como antes.
- Com o foco do teclado no número "Tamanho do conteúdo" (depois de digitar nele), as letras X e F viram
  texto do número e não trocam de ferramenta. Já era assim; não mexi.

## Bugs para a Lista de bugs (não consertados, já eram assim)

- **Área branca muda de 29,7 × 21,0 para 31,7 × 22,0 cm** no Gradus (página 39, "margens iguais" ligado pelo
  Automático) depois de Ctrl+Z e Ctrl+Y de um arrasto, com o mesmo estado da página. Acontece também na "Uma
  página" (`piloto_area.py`, `anotacoes-piloto-area.txt`, print `p201`), caminho que este conserto não mexe.
  Parece a conta das margens iguais chegando depois; não investigado a fundo.

## Perguntas para o Samuel (escolhas que mantive como já eram)

1. Clicar na outra página do par: hoje (como já era nos pares) o clique só a escolhe; o arrasto vale a
   partir do próximo aperto. Quer que já arraste no mesmo aperto? (print `p09`)
2. Os cantos azuis aparecem só na página da vez, não nas duas (como na "Uma página", que mostra uma).
   Está bom? (print `p03`)
3. "usar em todas..." nos pares: igual à "Uma página" (leva o tamanho e o lugar da página da vez). Não muda.

## Decisões: como cumpri cada uma

- D-612: provas `test_reversao_d612_*` e `test_d612_*`; piloto 20/20; prints p03 a p09.
- D-008/D-541 (arrastar, canto, número, a vista se ajusta): `test_reversao_d612_arrastar...` (tela = PDF até
  1%), `..._puxar_o_canto...`, `test_d612_numero_do_tamanho...`; p04, p06, p07.
- D-540 (F): `test_reversao_d612_vindo_do_dividir...`, `test_d612_numero_do_tamanho_e_tecla_f...`; p03.
- D-543/D-017: a parte de fora vermelha com listras e o aviso nos pares (p04).
- D-006/D-015/D-570 (pares, zoom do par): `test_d612_os_pares_continuam_pares`,
  `test_d612_ctrl_roda...`; p08, p09, p11.
- D-601/D-609/D-610/D-611: provas antigas passando; piloto (linha arrastada no Dividir em "Duas lado a
  lado", p02; tira em pares, p03).
- D-605: nenhum teste antigo mudado; 19 arquivos de teste passando; "Uma página" igual (p10).
