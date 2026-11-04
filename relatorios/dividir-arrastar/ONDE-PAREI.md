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

## O que já está escolhido e testado aqui (antes de mexer)

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

## Perguntas para o Samuel

(nenhuma por enquanto)
