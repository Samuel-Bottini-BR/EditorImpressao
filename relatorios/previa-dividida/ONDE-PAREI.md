# ONDE-PAREI — a prévia do Dividir no Automático (D-614, 04/11/2026)

Cópia: `.claude/worktrees/previa-dividida`, ramo `previa-dividida-2026-11-04` (saiu de `obra-2026-10-26`, `ad563c35`).

## Decisões que esta tarefa precisa cumprir

- **D-614 (04/11/2026)** — print a-60: "o dividir folha está escolhido era para aparecer uma folha divida ali né, e
  não duas folhas coladas, está errado" · "era para eu ter um preview de como vai ficar a folha separada" · "não
  gostei de nenhuma alternativa é para aparecer como se já tivesse sido feita a separação." · "você já sabe como é,
  porque eu preciso mandar um print". No Livro: na janela grande do Automático, com "Dividir" marcado, o "depois"
  mostra a folha como se a divisão já tivesse sido feita, igual à área de trabalho depois de dividir (D-601, "Uma
  página"): uma página por vez, a metade cortada na linha, e as setas andam pelas páginas. Muda só a parte da D-577
  sobre o Dividir; o resto da D-577 fica.
- **D-577 (29-31/10)** — o antes e depois da janela grande; o antes sempre cru; a linha que se arrasta (o lado para
  onde vai); a bolinha; a tela cheia com zoom e folhear; o "comparar" com as opções nos dois lados e o "usar este";
  a roda dá zoom. A frase que a D-614 troca: "com 'Dividir' marcado, o depois mostra as duas metades lado a lado
  ('pode', 30/10)".
- **D-601 (02/11)** — no Dividir da área de trabalho, "Uma página": a folha dividida mostra só uma metade, as setas
  andam pelas páginas (esquerda, direita, próxima folha; folha não dividida é um passo só); o rótulo continua
  "folha N de M".
- **D-603 (03-04/11)** — o caderno da etapa 7 segue as etapas marcadas (usa `core/automatico.paginas_do_pdf_depois`).
- **D-589 / D-590** — etapa desmarcada não é feita; Dividir desmarcado não junta nada (folhas já divididas continuam).
- **D-004** — a pergunta das páginas mexidas à mão é do "Rodar"; a prévia nunca pula (D-577, 30/10).
- **D-605 (CLAUDE.md §11.8)** — o novo não estraga o que já está escolhido e testado.

## O que já está escolhido e testado aqui

A janela grande do Automático, o lado direito (`ui/automatico.py`: `PaginaAntesEDepois`, `TelaCheiaDoAntesEDepois`,
`LadoDoComparar`, `VistaAntesDepoisComZoom`) e a conta da tarefa (`ui/tarefas.TarefaPreviaDoAutomatico`).

| Decisão | O que já está escolhido | Testado pelo Samuel | Provas que já existem |
|---|---|---|---|
| D-577 | antes cru, depois com as etapas marcadas, linha, bolinha, tela cheia, comparar, roda dá zoom | sim, 01/11 ("está funcionando") | `tests/test_decisoes_automatico_ver_como_fica.py` (19) |
| D-577 / D-594 | o "comparar" com "opções" nos dois lados e "usar este"; opções do painel Filtro | sim, 01/11 | `tests/test_decisoes_automatico_opcoes_do_filtro.py` (10) |
| margens no depois (02/11) | a prévia mede o livro para as margens; balão da bolinha | — | `tests/test_decisoes_automatico_margens_no_depois.py` (5) |
| D-574 / D-603 | etapa 7 mostra as folhas do caderno, que seguem as etapas marcadas ("Folha 1 de 35" no Gradus) | a testar | `tests/test_decisoes_caderno_tela_grande.py` (15), `tests/test_caderno_segue_as_etapas.py` (4) |
| D-600 | Shift + roda anda para os lados no antes e depois e na tela cheia | — | `tests/test_decisoes_shift_todas_as_telas.py` (5) |
| D-599 | zoom para o mouse | sim | `tests/test_zoom_no_ponteiro.py` (4) |
| D-589 / D-590 | desmarcada não volta marcada; Dividir desmarcado não junta | a testar | `tests/test_dividir_desmarcada_caixinha.py` (3), `tests/test_decisoes_montar_cadernos.py` |
| D-004 / Automático | o Rodar, as etapas, pular mexidas | sim | `tests/test_decisoes_automatico.py` (29), `tests/test_automatico_pular_depois_de_dividir.py` |
| D-601 / D-610 | o Dividir da área de trabalho ("Uma página") | sim (D-610 "3- ok") | `tests/test_decisoes_dividir_metade.py`, `tests/test_decisoes_dividir_arrastar.py` |

**Provas antigas que pedem "as duas metades lado a lado" (a parte da D-577 que a D-614 troca)**, em
`tests/test_decisoes_automatico_ver_como_fica.py`:

1. `test_d577_cortar_e_dividir_mudam_o_tamanho_do_depois` — com Dividir, o depois tem a largura da folha + o vão
   (`VAO_ENTRE_AS_METADES`) e o vão branco no meio.
2. `test_d577_o_depois_bate_com_o_rodar_de_verdade` — na folha dupla, compara a prévia com as duas metades do Rodar
   postas lado a lado (`_lado_a_lado`).
3. `test_d577_folha_inteira_com_dividir_marcado_antes_inteiro_depois_duas_metades` — o depois são as duas metades
   lado a lado.
4. `test_d577_marcar_e_desmarcar_dividir_muda_so_o_depois` — marcar Dividir: o depois são as duas metades lado a
   lado (o resto da prova, antes cru e desmarcar volta, continua valendo).

Pela regra da gerente: **não toco nesses testes**; paro e explico antes. **Resposta da gerente (04/11):** a D-614
substitui exatamente essa frase da D-577; trocar só a conferência "lado a lado" por "uma metade, como o Rodar
desenha", manter o resto e citar a D-614 em comentário. Feito em `ba2c67dd`; nenhum outro teste antigo mudou.

## Escolhas que segui do que já existe (sem pergunta)

- **Contador e setas = os da área de trabalho no Dividir com "Uma página" (D-601):** as setas andam pelas páginas
  (metade esquerda, metade direita, próxima folha; folha que não vai ser dividida é um passo só); o contador não
  muda de forma ("página 68 de 70" nas duas metades da folha 68), como o rodapé da área de trabalho continua
  "folha 68 de 70" nas duas metades.
- Quais folhas o Dividir parte: a mesma conta das folhas do caderno (D-603, `paginas_do_pdf_depois`), sem desenhar.

## Perguntas para o Samuel

(nenhuma até agora)

## Andamento

- [x] ler CLAUDE.md §11, agentes, Livro (D-614, D-577, D-601, D-603, D-589, D-590, D-004); prints a-59 e a-60
- [x] teste novo `tests/test_decisoes_previa_dividida.py` (4): no código de antes 3 falham (a da folha já
      dividida passa, de propósito: não deve mudar); no código novo, 4 passam
- [x] código (`ee5b1049`): `ui/automatico.py` (PaginaAntesEDepois: `_passos`, `_passo_mais_perto`,
      `_escolher_o_depois`, `ir_para(indice, metade)`, `virar`, `_acertar_botoes`, `_acertar_o_passo`, `_na_lista`,
      `_chegou`; LadoDoComparar.ir_para com a metade; TelaCheia._acertar_lados), `ui/tarefas.py` (a tarefa manda
      a metade de cada imagem)
- [x] testes no PC, um arquivo por vez (ver abaixo)
- [x] velocidade (`medir_velocidade.py`, `velocidade.txt`)
- [x] parado nas 4 provas antigas; a gerente autorizou; trocadas (`ba2c67dd`); o arquivo passa (22)
- [x] janela de verdade (Gradus, página 68), prints (`piloto.py`, `anotacoes*.txt`, `prints/`)
- [x] todas as `tests/test_decisoes*.py` no PC, um arquivo por vez: 31 arquivos, todos passam (2 pulados por falta
      de livro no PC)
- [x] GitHub (ver o relatório)
- [x] relatório `relatorio.md/.html/.pdf`

## Testes no PC (04/11, código novo `ee5b1049`)

| arquivo | resultado |
|---|---|
| test_decisoes_previa_dividida (novo) | 4 passaram (antes: 3 falharam, 1 passou) |
| test_decisoes_automatico_ver_como_fica | 18 passaram, **4 falharam** (as 4 da lista, cada uma na conta da largura "folha + vão" ou na comparação com as duas metades lado a lado); antes da mudança: 22 passaram |
| test_decisoes_automatico_opcoes_do_filtro | 21 passaram |
| test_decisoes_automatico_margens_no_depois | 5 passaram |
| test_decisoes_caderno_tela_grande | 15 passaram (o do Gradus rodou com a cópia do PDF em `_tmp/livros`) |
| test_caderno_segue_as_etapas | 11 passaram |
| test_decisoes_shift_todas_as_telas | 10 passaram |
| test_zoom_no_ponteiro | 5 passaram |
| test_dividir_desmarcada_caixinha | 3 passaram |
| test_decisoes_automatico | 29 passaram |
| test_automatico_pular_depois_de_dividir | 4 passaram |
| test_decisoes_montar_cadernos | 13 passaram |
| test_decisoes_juntar_todas | 4 passaram |
| test_decisoes_dividir_aviso | 11 passaram |

## Velocidade (Gradus, página 68, 9 rodadas de cada, alternadas, mesma máquina)

- ir à página (sem etapa): antes 0,21 a 0,32 s; agora 0,22 a 0,31 s (igual).
- marcar o Dividir até o depois chegar: antes 0,70 a 0,99 s; agora 0,75 a 0,95 s (igual, dentro do vaivém).
- ">" para a outra metade: 0,05 a 0,07 s (a conta já tinha desenhado as duas). Antes o ">" ia para a folha
  seguinte (0,65 a 0,93 s, com conta nova).
- a lista dos passos (`paginas_do_pdf_depois`): 2 a 3 milésimos de segundo.
