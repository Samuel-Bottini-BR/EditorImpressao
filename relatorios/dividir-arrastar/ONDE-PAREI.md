# ONDE-PAREI — dividir-arrastar (D-609), ramo `dividir-arrastar-2026-11-04`

Saiu de `obra-2026-10-26` em `e17410fe`.

## Decisões que esta tarefa precisa cumprir

- **D-609 (04/11):** print a-54 (Gradus folha 2 inteira): "não consigo mover a linha azul manualmente." · pergunta:
  "Quer poder arrastar a linha já na folha inteira, antes de dividir, e o "dividir esta" cortar onde você deixou?" → "Sim".
- **D-605 (03/11):** "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já
  está escolhido e testado, coisas novas não podem criar novos problemas".
- **D-602 (03/11):** a folha dupla ainda inteira já mostra a linha do motor (também em "Uma página"); a de uma página só
  não mostra linha; "dividir esta" corta nessa linha; "dividir todas" corta cada dupla na sua linha; "usar em todas"
  (D-090) fica como está; "motor de corte".
- **D-601 (02/11):** "Uma página" mostra só a metade da folha dividida; "Duas lado a lado", a folha inteira com a linha
  azul para arrastar.
- **D-498 (27/10):** "não dividir esta" junta e guarda; "dividir esta" devolve as duas como estavam, na linha de antes.
- **D-090 (08/10):** "usar em todas" abre a lista com as exceções (linha própria) desmarcadas; nunca apaga exceção.
- **D-606 (03/11):** "Ele deve fazer a conta novamente com o novo motor" (trocar o motor refaz a conta, a linha vai para
  onde o motor acha).
- **D-608 (03/11):** depois de clicar num botão do painel, as setas continuam passando de folha.

- **D-610 (04/11, pedido da gerente no meio da tarefa):** print a-56: "quando eu dividir uma folha que estiver em duas
  lado a lado ela tem que ir para opção uma pagina, se não quando eu usar seta ela vai pular uma folha." → no Dividir,
  "dividir esta" e "dividir todas" em "Duas lado a lado" passam a vista para "Uma página". Mais nova que a D-601.
- **D-611 (04/11, idem):** "quando estiver duas lado a lado escolhido os icones embaixo tem que estar em duas folhas" ·
  "Quer dizer que, com 'Duas lado a lado' escolhido, as miniaturas embaixo também aparecem de duas em duas, juntas como
  no livro aberto?" → "Sim". Em "Uma página", a tira fica como está.

## O que já está escolhido e testado aqui (antes de mexer)

- (D-610) D-601: em "Duas lado a lado" a vista ficava depois de dividir → `tests/test_dividir_na_tela.py::
  test_linha_azul_some_quando_a_folha_nao_e_dividida` (o fim dele contava com isso: ver Situação), D-608 (setas).
- (D-611) A tira: "Ver em pares" do menu dos três pontinhos (etapa 5 do layout, guardado para o próximo livro) →
  `tests/test_miniaturas_novas.py`; a tira do Dividir (D-601: dividida = duas miniaturas, inteira = uma dupla) →
  `tests/test_decisoes_dividir_metade.py`; rolar até a escolhida depois do Ctrl+Z (03/11) →
  `tests/test_dividir_ajustes_03_11.py`. A tira da tela inicial (de lado) não muda.

- D-602: linha do motor na folha inteira, "Uma página" e "Duas lado a lado"; sem linha na de uma página só; "dividir
  esta" corta na linha mostrada; "dividir todas"; lista do motor acesa → `tests/test_decisoes_dividir_linha.py`.
- D-601: metade em "Uma página", linha para arrastar em "Duas lado a lado" na folha dividida →
  `tests/test_decisoes_dividir_metade.py`.
- D-498 / etapa 4: juntar e dividir de novo devolve as páginas → `tests/test_decisoes_dividir.py`, `tests/test_dividir_na_tela.py`.
- D-090: "usar em todas" com exceções desmarcadas → `tests/test_decisoes_9b2.py::test_d090_*`.
- D-606, D-607, D-608, Ctrl+Y do "Parece em branco" → `tests/test_dividir_ajustes_03_11.py`.
- D-590 "juntar todas" → `tests/test_decisoes_juntar_todas.py`.
- Outros do Dividir: `test_dividir_no_programa.py`, `test_dividir_scantailor.py`, `test_dividir_desmarcada_caixinha.py`,
  `test_automatico_pular_depois_de_dividir.py`, `test_visualizador.py`.
- **Conflito achado:** `test_decisoes_dividir_linha.py::test_reversao_d602_linha_azul_na_folha_dupla_inteira_em_uma_pagina`
  tem a linha `assert not vista.corte_arrastavel` ("a linha da folha inteira é só para ver: arrastar não muda nada
  (pergunta ao Samuel)"). É exatamente o que a D-609 manda mudar (resposta "Sim" à pergunta `d602-arrastar`). Ver
  "Situação".

## Plano

1. `modelos.ConfigFolha.linha_a_mao` = [rotação, motor] em que a linha da folha inteira foi arrastada (None = não).
2. `ui/tela_conferir.py`: folha inteira dupla → linha arrastável; arrastar grava posicao_corte + linha_a_mao numa ação;
   "dividir esta" / "dividir todas" cortam nela; trocar o motor apaga a marca (D-606).
3. Testes novos em `tests/test_decisoes_dividir_arrastar.py`.

## Situação

(atualizada a cada passo)

- 04/11: feito e commitado (`ecf5e3a1` o código e as provas; `6e5b4cdd` a linha 127 do teste da D-602, em
  commit separado — ver o relatório). 13 provas novas; 11 falham em `e17410fe` (as 2 que passam lá são das escolhas
  que continuam: folha de uma página sem linha, seta depois de arrastar).
- Prints na janela de verdade (Gradus): p01 a p06 nesta pasta, anotações em `anotacoes.txt`.
- GitHub: rodada 41785344022 (em andamento ao escrever). Testes do Dividir no PC, um por vez: `_tmp/um_por_vez.txt`.

- 04/11, depois: D-610 (`bbecf4f7`; fim de um teste antigo em `784a5bf6`) e D-611 (`2fccd164`) feitas; prints p07 a
  p12; reversão das três decisões conferida em `e17410fe`. Testes do Dividir e da tira no PC, um por vez: todos
  passaram. GitHub rodada 2: `41788480788` verde (parte 1 repetida por um erro intermitente do p083 do Automático, ver o relatório). Relatório: `relatorio.md` (.html, .pdf). Entregue à gerente.

## Perguntas para o Samuel

1. D-611 no Dividir, com folhas ainda inteiras: a tira junta de dois em dois pela ordem (1 sozinha; 2-3; 4-5); no
   Dividir a miniatura de folha inteira já é a folha dupla, então junta, p. ex., a capa (metade da folha 1) com a folha
   2 inteira (print p10b). Quer assim, ou no Dividir cada folha junta (as duas metades da dividida lado a lado, como a
   vista grande mostra)?
2. D-611, aparência: os pares têm um vão pequeno dentro do par e um maior entre pares (o mesmo "Ver em pares" que já
   existia, p10b). Quer as duas miniaturas do par encostadas?
