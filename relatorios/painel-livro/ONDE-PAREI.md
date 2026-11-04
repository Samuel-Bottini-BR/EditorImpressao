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
- [ ] D-620: teste novo, código, testes por arquivo.
- [ ] D-619: teste novo, código, troca autorizada nos 3 testes antigos.
- [ ] Janela de verdade: prints.
- [ ] GitHub.

## Perguntas para o Samuel

(nenhuma ainda)
