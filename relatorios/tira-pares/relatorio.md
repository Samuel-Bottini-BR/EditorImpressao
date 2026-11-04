# Tira em pares (D-611 refeita) — 04/11/2026

Ramo `tira-pares-2026-11-04` (saiu de `obra-2026-10-26`, `5cf4aaed`). Nada foi juntado.

## A causa, em uma frase

A tira já estava em pares por dentro, mas as duas miniaturas do par ficavam tão longe uma da outra quanto em
"Uma página" (22 pontos), então a olho parecia uma a uma.

## Como achei

- Abri o projeto do Gradus dele (cópia de `dados-teste-rodada-de-consertos`) na janela de verdade, com as
  configurações dele, e segui o caminho do a-57: Dividir, "dividir todas", "Duas lado a lado" (`piloto.py`).
- Medi onde os desenhos ficam na tira. Com as folhas divididas, cada miniatura é uma página em pé, estreita, no meio
  de um quadro de largura fixa. Vão dentro do par: **22 pontos** (igual a "Uma página"); entre pares: 32.
  Com as folhas inteiras: 14 e 24. Prints `prints/antes-abrir-*`, números em `anotacoes-abrir-antes.txt`.
- Suspeitas descartadas: a vista não vem gravada ao abrir (abriu em "Uma página", como a configuração dele); o
  Automático e o tamanho da janela não mudam nada; a tira "FOLHAS" do Dividir usa o mesmo arranjo.

## Por que os 4 testes de antes não pegaram

Eles conferiam só a coluna de cada quadro na grade (1 | 2-3 | 4-5), que estava certa. Nenhum olhava onde os
desenhos aparecem na tela. E os prints do agente anterior foram num livro aberto do zero, com folhas inteiras e
largas, onde o par aparece um pouco melhor; o Samuel testou com as folhas divididas.

## O conserto

`ui/widgets/tira_miniaturas.py`, só quando a tira está em pares por causa do "Duas lado a lado":
os dois quadros do par ficam sem vão e os desenhos se encostam (a página da esquerda encosta à direita, a da direita
à esquerda; `Miniatura.encostar`); entre um par e outro, 22 pontos. O número fica embaixo do desenho.
Depois: vão dentro do par 4 pontos (as duas molduras), entre pares 50 (páginas) ou 34 (folhas inteiras).

O que não mudou: "Uma página" (22 pontos, uma a uma) e o "Ver em pares" do menu dos três pontinhos (jeito aprovado
em 21/10, "Está bom"). O tamanho do desenho não muda.

## Provas

- Nova: `tests/test_decisoes_tira_pares_juntas.py` (3), mede os desenhos na imagem da tira.
  `test_reversao_d611_par_junto_no_dividir_em_duas_lado_a_lado` **falha no código de antes** (vãos 31/21) e passa
  agora. As outras duas (Uma página igual; "Ver em pares" do menu igual) passam nos dois.
- Nenhum teste antigo mudou.

## Na janela de verdade (Gradus dele), depois

`prints/depois-caminho-*` e `anotacoes-caminho-depois.txt`: Dividir com folhas inteiras e divididas em "Duas lado a
lado" (pares juntos); "Uma página" igual a antes; setas (folha 2 → 3 → 4); clique na miniatura 10 vai à página 10 da
folha 5; Ctrl+Z (volta o "dividir todas") e Ctrl+Y; Cortar em "Duas lado a lado" (pares juntos, iguais à vista
grande 8-9) e em "Uma página" (igual). O arrastar da linha (D-609) e o D-610 seguem pelas provas deles (passaram).

## Testes no PC, um arquivo por vez

test_decisoes_tira_pares_juntas 3, test_decisoes_tira_em_pares 4, test_miniaturas_novas 5, test_decisoes_dividir 21,
test_decisoes_dividir_metade 6, test_decisoes_dividir_arrastar 16, test_decisoes_dividir_linha 13,
test_dividir_na_tela 9, test_dividir_ajustes_03_11 9, test_decisoes_ver 11, test_decisoes_9b1 25,
test_decisoes_9b2 30, test_decisoes_avisos 22, test_menu_paineis 3, test_girar_cartoes_e_previas 23,
test_decisoes 26, test_decisoes_juntar_todas 4, test_dividir_no_programa 19, test_visualizador 70 — todos passaram.

## GitHub

Rodada `41856231452` (commit `987f964a`): as 5 partes do conjunto e "Botões e prints da janela real" passaram, de primeira.

## Pergunta para o Samuel (aberta)

No Dividir, com "Duas lado a lado", a vista grande mostra a folha (as duas metades: folha 2 = páginas 3 e 4). A tira
junta como o livro aberto: 1 sozinha, 2-3, 4-5. Então a página 3 aparece junto da capa (2), e não da 4 que está ao
lado dela na vista grande.

- Como está (livro aberto): `prints/pergunta-opcao_a-01-opcao-a-par-do-livro-aberto.png`
- Pela folha, como a vista grande do Dividir (feito só no piloto, não está no programa):
  `prints/pergunta-opcao_b-01-opcao-b-par-pela-folha.png`

Sugestão: no Dividir, juntar pela folha (1-2, 3-4), igual à vista grande; nas outras ferramentas, como o livro
aberto. Não fiz: espera o "sim" dele.

## Ressalvas

- Escolha técnica minha: 22 pontos entre pares (o mesmo total de antes) e 4 pontos dentro do par (as molduras).
- Com a tira de lado (à esquerda/direita) e "Duas lado a lado", o par também encosta (mesma regra); não tirei print.
