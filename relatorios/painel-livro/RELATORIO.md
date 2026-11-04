# D-619 e D-620: relatório curto (04/11/2026)

Ramo `painel-livro-2026-11-04` (saiu de `obra-2026-10-26`, `2329129f`). Ainda sem push e sem a rodada do GitHub:
falta a resposta da pergunta da D-620 abaixo.

## Como cumpri cada decisão

- **D-619**: o quadro do livro do Propriedades se chama "Já feito no livro todo" no Dividir, no Cortar e no
  Endireitar (`_parte_do_livro`). Ele continua só mostrando. O "mudar no Automático..." e a caixinha "Margens
  iguais" (D-554) ficaram. Print: `prints/quadros-ja-feito-no-livro-todo-1920.png`.
- **D-620**: a "Qualidade da prévia" saiu do painel do Cortar e foi para a barra de baixo, logo depois de
  "ajustar à tela" (`_montar_a_qualidade_da_barra_de_baixo`). Continua uma escolha só, gravada em
  `qualidade_previa`, com o mesmo efeito. Na janela de verdade, escolher "Alta" no Cortar vale no Endireitar, no
  Mover e no Dividir (300 DPI, gravado). Prints: `prints/1920-07..10`, `prints/1366-07..10`.

## Testes

- Teste novo: `tests/test_decisoes_painel_livro.py`, com 8 casos. Todos falham no código antigo e passam no novo.
- Testes antigos: 3 linhas de `tests/test_paineis_na_tela.py` (255, 378, 425). Só a palavra
  "PARA O LIVRO TODO" virou "JÁ FEITO NO LIVRO TODO", com autorização da gerente (opção A), em commit separado.
- No PC, um arquivo por vez, tudo passou:
  - `test_paineis_na_tela` 22
  - `test_decisoes_9b2` 30
  - `test_zoom_no_ponteiro` 5
  - `test_decisoes_ver` 11
  - `test_decisoes_9b1` 25
  - `test_decisoes_marcacoes` 19
  - `test_miniaturas_novas` 5
  - `test_decisoes_dividir_linha` 13
  - `test_desentortar_medida_por_tras` 6
  - `test_visualizador` 70
  - `test_trilha_agrupada` 19
  - `test_decisoes_mover_lado` 7
  - `test_paineis` 34
  - as outras 28 provas `test_decisoes*.py`
- Ressalva: numa rodada, 1 teste do 9b2 e 1 do ver falharam enquanto eu rodava outro teste ao mesmo tempo
  (disputa de máquina). Os dois passaram sozinhos e na rodada inteira sem nada em paralelo.

## Pergunta aberta (print `prints/pergunta-qualidade-na-barra.png`)

Com o nome inteiro "Qualidade da prévia", a barra não cabe:
- Na tela do Samuel (janela de 1536), a conta fica cortada em "0 de 140 co...".
- Em 1366 com o Propriedades aberto, botões ficam cortados.

Opções:
- A) Só a lista "Rápida ▾", com o nome no balão. Em 1536 tudo cabe. Em 1366 nenhum botão é cortado, mas a conta
  vira "0...". Ela já saía cortada antes da D-620.
- B) "prévia" + lista. Corta "Duas lado a lado" em 1366.
- C) Nome inteiro, como está agora no ramo.

Recomendação: A.
