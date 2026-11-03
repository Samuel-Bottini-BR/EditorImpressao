# D-602 — Dividir: a linha aparece antes de cortar, "dividir todas" e "motor de corte"

Ramo `dividir-linha-2026-11-03` (saiu do `obra-2026-10-26`, `8846017`). Implementador, 03/11/2026.
**PRONTO PARA CONFERIR** é com o verificador; aqui vai o que foi feito e as ressalvas.

## O que foi feito

Ao entrar no Dividir, a folha dupla ainda inteira já mostra a linha azul onde o motor de corte escolhido cortaria
— em "Uma página" e em "Duas lado a lado" —, sem cortar nada. A folha que o motor acha de uma página só fica sem
linha. "dividir esta" corta nessa linha. O botão novo "dividir todas" lê cada folha pelo motor (por trás, com
andamento e "parar") e corta cada dupla na sua linha; as de uma página ficam inteiras. "jeito" virou "motor de
corte" no Dividir e no Automático. A lista travada era a lista apagada em toda folha não dividida; agora fica acesa.

## Como cumpri cada uma

| Decisão | Como | Prova |
|---|---|---|
| D-602, linha na folha dupla inteira (também em "Uma página"), nada cortado | a folha inteira é lida pelo motor por trás (`core/dividir_a_mao.ler_a_linha`, a mesma conta do "dividir esta", sem forçar; `ui/tarefas.TarefaLerLinhas`); enquanto lê, o selo "atualizando..." | `test_reversao_d602_linha_azul_na_folha_dupla_inteira_em_uma_pagina` (falhou no `8846017`), `test_d602_linha_tambem_em_duas_lado_a_lado`; print `depois-1` (Gradus, folha 5, linha a 51%) |
| D-602, folha de uma página sem linha | o motor diz "uma página" (folha em pé) → sem linha | `test_d602_folha_de_uma_pagina_nao_mostra_linha`; print `depois-6` (Boécio, folha 3). O Gradus não tem folha de uma página: as 70 são deitadas e o motor acha todas duplas (até a capa, print `depois-2`) |
| D-602, "dividir esta" corta nessa linha | usa a leitura guardada da folha | `test_d602_dividir_esta_corta_na_linha_mostrada` |
| D-602, "dividir todas" | por trás, com andamento e "parar"; uma ação só do desfazer; já dividida não é dividida de novo | `test_d602_dividir_todas_corta_as_duplas_cada_uma_na_sua_linha`, `..._usa_a_linha_ja_mostrada`, `..._parar_nao_muda_nada`; promessa P-212 com prova; prints `depois-4` e `depois-5` (Gradus: 70 de 70 divididas) |
| D-602, "jeito" → "motor de corte" | rótulo da lista e "Para o livro todo" do Dividir; lista e segunda linha da etapa 1 do Automático; dica e Histórico | `test_d602_jeito_vira_motor_de_corte_no_dividir` / `..._no_automatico`; prints `depois-1` e `depois-7` |
| D-602, lista travada | causa e conserto abaixo | `test_reversao_d602_lista_do_motor_nao_trava_na_folha_inteira` (falhou no `8846017`), `test_d602_lista_do_motor_acesa_depois_de_dividir_e_juntar` |
| D-090, "usar em todas" | não mexido | `test_d602_usar_em_todas_continua_copiando_a_linha_desta_folha`; `test_decisoes_9b2.py` (30 passaram) |
| D-373, nomes das opções | não mexidos | os dois testes de "motor de corte" conferem "o do Editor" e "o do ScanTailor" |
| D-528, marcações para a metade certa | o "dividir todas" usa `campos_para_dividir` (a mesma do "dividir esta") | `test_decisoes_nucleo2.py` (21 passaram) |
| D-601, D-590, D-498 | mantidas; os testes da D-601 que diziam "folha inteira sem linha" agora apontam para a D-602 (mais nova) | `test_decisoes_dividir_metade.py` (6), `test_decisoes_juntar_todas.py` (3), `test_d602_folha_juntada_mostra_a_linha_de_antes` |

## A lista travada (causa)

`ui/tela_conferir.py`, `_atualizar_botoes`: `combo_jeito_da_folha.setEnabled(bool(folha.dividir))`. A lista só
ficava acesa em folha dividida; livro aberto sem Dividir = todas as folhas inteiras = lista apagada em todas (no
tema escuro quase não se vê que está apagada), e trocar também não fazia nada (`_trocar_jeito_da_folha` voltava).
Depois de "não dividir esta" ou "juntar todas" apagava de novo. Conserto: acesa em toda folha; na folha inteira,
trocar grava o motor desta folha (uma ação do desfazer) e a linha é lida de novo, sem cortar.

## Arquivos

`core/dividir_a_mao.py` (função nova `ler_a_linha`; `medir_para_dividir` passa a usá-la, mesma conta),
`ui/tarefas.py` (`TarefaLerLinhas`), `ui/tela_conferir.py`, `ui/widgets/visualizador.py` (linha só para ver, sem a
pega "arraste"; selo enquanto lê), `ui/automatico.py` (dois textos), testes e `tests/promessas/promessas.md`.

## Testes

- **PC, um arquivo por vez (todos passaram):** test_decisoes_dividir_linha (13), test_decisoes_dividir_metade (6),
  test_dividir_na_tela (9), test_decisoes_dividir (19), test_decisoes_juntar_todas (3), test_decisoes_9b2 (30),
  test_paineis_na_tela (22), test_dividir_no_programa (19), test_visualizador (70), test_decisoes_nucleo2 (21),
  test_decisoes_automatico (24), test_dividir_scantailor (13), test_decisoes_tela (35); test_promessas só as do
  Dividir, P-083 e as de inventário (12).
- **Reversão:** os dois testes `test_reversao_d602_*` falharam no `8846017` ("a lista não trava"; "a folha dupla
  inteira mostra a linha azul") e passam no novo.
- **GitHub:** rodada 41706257524 (commit d2c6ffa1): falhou 1 — faltava a promessa do botão novo (P-212), escrita
  depois. Rodada 41711039690 (cd735793): na 1ª tentativa, a parte 1 acusou um erro no fim do
  `test_p083_jeitos_no_automatico[Guardar tudo]` (uma prévia do Automático tentou abrir o PDF de um teste que já
  tinha sido apagado; nada do Dividir; o teste passa no PC); na 2ª tentativa, **tudo verde**, conjunto inteiro e
  `teste_botoes.py` (370 ações, 0 falhas).
- **Filtro de velocidade** (rodada 41706298782, `8846017` → `d2c6ffa1`, mexe em `core/dividir_a_mao.py`):
  **igual (dentro do vai-e-vem)** — abrir o livro -0,6%, trocar de página +0,3%, Mágico pro -0,1%, Preto e branco
  -0,3%.

## Linhas de `ui/automatico.py` (para a gerente juntar)

No `8846017`: linha 148 (`return "jeito: " + ...` em `texto_das_opcoes`) e linha 1900 (`"Jeito de dividir:",` em
`PainelDeOpcoes._opcoes_dividir`). No ramo: linha 148 é um comentário novo, 149 o `return "motor de corte: " + ...`
e 1901 o `"Motor de corte:",`. Nada mais nesse arquivo.

## Ressalvas

- A linha da folha inteira não arrasta (pergunta 1 do ONDE-PAREI).
- O "Ampliar" (janela grande) do Dividir continua mostrando a linha só na folha dividida (não pedido).
- A frase "Você trocou o jeito de dividir do livro..." da janela de recomeço (`projetos.py`) e a tela antiga "O que
  fazer" (`ui/tela_opcoes.py`, fora do caminho) ainda dizem "jeito": não são o Dividir nem o Automático.
- "Jeito de limpar" e "Jeito do preto e branco" do Automático são outra coisa (filtro): não mudaram.
- A leitura de cada folha leva uns décimos de segundo; no "dividir todas" do Gradus (70 folhas) a caixa do andamento
  fica alguns segundos na tela.
