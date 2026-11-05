# Painel do livro e qualidade na barra de baixo (D-619, D-620): onde parei

Cópia `.claude/worktrees/painel-livro`, ramo `painel-livro-2026-11-04`, saiu de `obra-2026-10-26` (`2329129f`).
Agente de tela. Entrega à gerente.

## Decisões que esta tarefa precisa cumprir

- **D-619** (04/11/2026). Print a-69: "para o livro todo, não entendi essa mensagem, elas não deveriam ser opções para
  se escolher, essa opção de qualidade não deveria ser para todas as ferramentas?". Opções A e B; ele: "1- B".
  O quadro "Para o livro todo" continua só mostrando o que o Automático já fez no livro (D-051). O título passa a ser
  "Já feito no livro todo". O "mudar no Automático..." e a caixinha "Margens iguais" (D-554) ficam.
  Vale no Cortar, no Dividir e no Endireitar (as três chamam `_parte_do_livro`).
- **D-620** (04/11/2026). Mesmo print; ele: "2- Pode". A "Qualidade da prévia" (Rápida / Média / Alta) sai do painel
  do Cortar e vai para a barra de baixo, ao lado do zoom. Aparece em todas as ferramentas. Continua uma escolha só
  para o programa inteiro (`configuracoes` "qualidade_previa"), com o mesmo efeito.

## O que já está escolhido e testado aqui (regra D-605, CLAUDE.md §11.8)

Decisões do Livro que tocam o Propriedades e a barra de baixo:
- D-051: o Propriedades tem duas partes, "Só nesta página" e "Para o livro todo"; a do livro só mostra e leva ao
  Automático. Prova: `tests/test_paineis_na_tela.py` (linhas 255, 378 e 425 procuram "PARA O LIVRO TODO").
- D-002: o "mudar no Automático..." abre o Automático na etapa.
- D-554 / D-494 / D-075: a caixinha "Margens iguais" na parte do livro do Cortar (`tests/test_decisoes_9b2.py::test_d554_*`).
- D-373 e D-602: "Motor de corte: o do Editor / o do ScanTailor" na parte do livro do Dividir
  (`tests/test_decisoes_dividir_linha.py`).
- D-015 / D-006 / D-007: "Uma página / Duas lado a lado" na barra de baixo (`tests/test_decisoes_ver.py`).
- D-577: "antes / depois" na barra de baixo. D-580: "marcações" ao lado dele (`tests/test_decisoes_marcacoes.py`).
- Zoom "– N% +" e "ajustar à tela" na barra de baixo (rodada 13; `tests/test_zoom_no_ponteiro.py`).
- D-045: desfazer, refazer e Histórico na barra de baixo. D-064: as duas bolinhas de carregamento (`test_decisoes_9b2.py`).
- D-050: "Confirmar e processar" desce para a barra de baixo, à direita (`tests/test_miniaturas_novas.py`).
- Etapa 7 e 9b-1: o contador da barra de baixo não pode sumir; o nome do livro encolhe primeiro e a conta vai em
  duas linhas se precisar (`tests/test_decisoes_9b1.py::test_contador_*`, `::test_barra_de_baixo_nada_saiu`).
- P6 (23/10): o sinal "Desentortando..." depende da qualidade da prévia (`tests/test_desentortar_medida_por_tras.py`).

Arquivos que vou tocar: `ui/tela_conferir.py` (só `_parte_do_livro`, `_montar_aba_bordas` e
`_montar_o_ver_da_barra_de_baixo`), `ui/estilo.py` (uma regra de estilo nova para a lista da barra).

## Andamento

- [x] Lidos CLAUDE.md §11, regras de 03/11 dos agentes, D-619, D-620 e as da barra de baixo; print a-69.
- [x] Pergunta à gerente sobre os 3 testes antigos com "PARA O LIVRO TODO": resposta "Opção A autorizada" (trocar só
  a palavra nas linhas 255, 378 e 425, commit separado, comentário citando a D-619).
- [x] D-620: teste novo (`tests/test_decisoes_painel_livro.py`, 4 testes; os 4 falham no código antigo), código
  (commit `fd274726`).
- [x] D-619: teste novo (mesmo arquivo, 4 casos; falham no antigo), código (`a9a0892b`), troca autorizada nos
  3 testes antigos (`84995d4e`).
- [x] Janela de verdade (`piloto.py`): prints em `prints/`. Quadro novo nos três; a troca para "Alta" no Cortar vale
  no Endireitar, no Mover e no Dividir (300 DPI, gravada).
- [x] A barra não cabe com o nome inteiro: pergunta abaixo. Resposta do Samuel (pela gerente, 04/11): "é porque o
  aplicativo está mal diagramado, não tem como colocar só uma setinha e quando aperta nela aparece as opções de
  qualidade?" -> feito (`c6e73beb`): botão só com a setinha, menu com a escolhida marcada, balão
  "Qualidade da prévia: X". Medidas e ressalva da barra em 1366 no `RELATORIO.md`.
- [x] 05/11 (retomada): os 2 arquivos sem commit (`tests/promessas/promessas.md` e `tests/test_promessas.py`) eram
  desta tarefa: a promessa P-213 da setinha nova e a prova dela. Só acrescentam (botão novo precisa de promessa,
  D-010); nenhuma conferência antiga mudou. Troquei só o jeito de ler o projeto na prova nova para o ajudante de
  sempre (`aj.projeto_gravado`). Commit `0accc9bb`.
- [x] Juntei `obra-2026-10-26` (`f06e0c15`) sem conflito (`04b0ff8c`).
- [x] PC, um arquivo por vez: os 40 `tests/test_decisoes*.py`, `test_paineis_na_tela.py`, `test_promessas.py`
  (268 passaram, 1 xfail), `test_zoom_no_ponteiro.py`, `test_miniaturas_novas.py`,
  `test_desentortar_medida_por_tras.py`: todos passaram. `test_decisoes_respeitar_gravuras.py` falhou uma vez por
  falta de memória do PC (outros agentes rodando); de novo, 19 passaram.
- [x] GitHub, rodada 41949243543: 3.331 passaram, 1 falhou: `test_decisoes_so_as_letras::test_d148` (instável
  conhecido; no PC passou, 5 de 5). Botões e prints da janela real: passou.

## Como cumpri cada decisão

- **D-619**: o quadro do livro do Propriedades se chama "Já feito no livro todo" no Dividir, no Cortar e no
  Endireitar; continua só mostrando (D-051); o "mudar no Automático..." e a caixinha "Margens iguais" (D-554)
  ficaram. Prova: `tests/test_decisoes_painel_livro.py::test_d619_*` (falham no código antigo). Prints:
  `prints/1536-01..03`, `prints/1366-01..03`, `prints/quadros-ja-feito-no-livro-todo-1920.png`.
- **D-620**: a "Qualidade da prévia" saiu do painel do Cortar e está na barra de baixo, logo depois de "ajustar à
  tela", em todas as ferramentas: só uma setinha que abre Rápida / Média / Alta, com a escolhida marcada e o balão
  "Qualidade da prévia: X". Continua uma escolha só (`qualidade_previa`). Provas:
  `tests/test_decisoes_painel_livro.py::test_d620_*` e `tests/test_promessas.py::test_p213_*`. Prints:
  `prints/barra-com-a-setinha-1536-e-1366.png`, `prints/15xx-06..10`.
- **Ressalva**: em 1366 com o Propriedades aberto, a conta da barra vira "0 de 140 co..." (inteira no balão); com
  as miniaturas fechadas a barra já não cabia antes. Detalhe no `RELATORIO.md`.

## Perguntas para o Samuel

1. **D-620: como a qualidade aparece na barra de baixo** (print `prints/pergunta-qualidade-na-barra.png`).
   Com o nome inteiro "Qualidade da prévia" + a lista, a barra não cabe: na tela dele (1920 a 125% = janela de
   1536) a conta vira "0 de 140 co..."; em 1366 com o Propriedades aberto, botões ficam cortados. Antes da D-620,
   em 1366 com o painel aberto, a conta já saía cortada ("0 de 140 confe..."). Opções: A) só a lista "Rápida", o
   nome no balão (1536: tudo cabe, conta inteira; 1366: nenhum botão cortado, a conta vira "0...", inteira no
   balão); B) "prévia" + lista (1366 corta "Duas lado a lado"); C) nome inteiro (corta). Recomendação: A.
   Ordem: logo depois de "ajustar à tela" (antes do "Confirmar e processar" quando ele desce para a barra).
