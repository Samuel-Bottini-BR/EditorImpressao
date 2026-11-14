# Onde parei: estudo "cada palavra numa cor só" (implementador, 14/11/2026)

**Tarefa só de estudo** (Samuel: "bota o 13 para ser estudado"). Nenhuma linha do programa muda (`core/`, `ui/`, raiz).
Ramo `palavra-cor-2026-11-14` (sai do `obra-2026-10-26`, `c7e34fd8`).

## Situação
- [x] Lidas as regras (implementador.md, CLAUDE.md inteiro, INDICE, fichas 2.11 e 1.5, decisões do Livro).
- [x] Abertos os dois prints da prova (ramo `fase-1`, `relatorios/provas-central-2026-11-13/2-cores-*`).
- [ ] Causa medida no Livro de Horas 26 (caminho inteiro).
- [ ] Caminhos que chegam na função.
- [ ] Plano do conserto.
- [ ] Relatório em três formatos.

## Decisões que esta tarefa precisa cumprir
- **D-701** (13/11/2026), Central `dv-211-215`: "Consertar: cada palavra sai numa cor só, como no scan (recomendo)".
- **D-178**: "(a) Trazer como opção, desligada de fábrica (recomendado)" · "Aprovado" · "Está bom".
- **D-189** (21/10): "Ele está apagando as letras, isso sim, e quando foi que eu pedi para fazer isso? isso é do scantailor?" · "aprovado, mas ainda tem que melhorar, em alguns casos, ele acaba apagando a letra."
- **D-191**: "entra no programa e a caixinha não fica escondida."
- **D-192**: tela cheia com as mesmas opções do painel e a página do meio igual ao que sai ("faça o recomendado." · "Está bom").
- **D-594**: "Limpar a folha" do Automático com todas as opções do painel ("mas isso era uma coisa obvia que deveria ter").
- **D-649**: "o resultado final tem que sair como a edição foi mostrada no preview".
- **D-605 / §11.8**: "nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e testado".
- **D-147** (achada na busca): no Preto e branco, foto e pintura em tons de cinza, nunca pontilhadas (toca `core/cores_scantailor.py:25`).

## O que já está escolhido e testado aqui
- "Letras com a cor delas" desligada de fábrica, só no Preto e branco (D-178; `tests/test_cores_scantailor.py`,
  `tests/test_cores_scantailor_na_tela.py`): letra vermelha sai vermelha, letra preta sai escura, papel branco.
- "Reduzir cores" à vista no painel Filtro, desligada de fábrica (D-191); nos outros filtros posteriza a página
  inteira, uma cor por grupo (`test_reduzir_cores_na_pagina_de_cor`).
- "Reduzir cores" não apaga letra (D-189, etapa 10b): no Preto e branco a posterização vai SEM o "forçar preto e
  branco" (`tests/test_decisoes.py::test_d189_reduzir_cores_no_preto_e_branco_nao_forca_preto`) e menos de 2% das
  letras viram preto na Horas 26 (`tests/test_etapa10b_imagem.py::test_reversao_d189_reduzir_cores_nao_apaga_meia_palavra`).
- Cartões (figurinhas) seguem as caixinhas da página (`tests/test_cartoes_seguem_as_caixinhas.py`); tela cheia com as
  mesmas opções (D-192, `tests/test_filtros_tela_cheia.py`); Automático com as duas opções (D-594,
  `tests/test_decisoes_automatico_opcoes_do_filtro.py`); sem a DLL a página sai como sem as caixinhas
  (`test_sem_a_dll_sai_como_sem_as_caixinhas`, `tests/test_falha_do_scantailor_vai_ao_erros_log.py`).
- "No Preto e branco o vermelho sai preto" de fábrica (V1, 30/09) e foto em cinza (D-147): não são tocados.

## Causa (medida; scripts em `scripts/m1` a `m3`)
Livro de Horas 26, livro novo de fábrica, caminho inteiro (endireitada, cortada, Preto e branco + "Letras com a cor
delas" + "Reduzir cores"), a página como sai no PDF (300 pontos por polegada).
1. "Letras com a cor delas" (a segmentação do ScanTailor, `ColorSegmenter.cpp`, código copiado sem mudança na DLL)
   pinta **cada peça** de tinta com a cor **média dela**. Letra de traço grosso dá média mais escura (R 131-150);
   letra fina, mais clara (R 155-182), porque tem mais beirada clara. A mesma tinta vira dezenas de cores próximas.
2. "Reduzir cores" (o `Posterizer.cpp` do ScanTailor, sem mudança) estica as cores da página entre a mais escura
   (122) e o branco, e corta cada canal em 4 faixas fixas. A primeira divisa cai em R = 155: **bem no meio** da faixa
   das letras. Letra com média até 155 vai para uma caixa; acima, para outra.
3. Cada caixa sai com **a cor mais frequente dentro dela**, venha de onde vier: a caixa das letras escuras pega o
   azul-acinzentado (115,127,146) do "N" do título azul "NOVEMBRE."; a caixa das letras claras pega o bege
   (179,171,140) da faixa da beirada direita da folha. Por isso a diferença pequena vira azul x bege.
- Prova: a conta refeita em numpy dá o mesmo que a DLL em 100% dos pontos de letra (`m2_causa.py`). Em "S. Leonard":
  "S", "L", "o", "n", "a", "r" com média ≤ 155 → azul; "e" (158), "d" (parte) e o "r" final (164-168) → bege.
- Medida "palavra em duas cores" (`m3_palavras.py`): no PDF, **48%** das palavras do calendário saem em duas cores
  com "Reduzir cores"; 32% já variam com só "Letras com a cor delas" (variação suave, de claridade).
- **A prévia não mostra as mesmas cores do PDF** (achado novo, D-649): a parte azul da tinta do calendário é 69% na
  prévia (110), 59% na tela cheia (150), 63% no Automático (180), 43% a 220 (a resolução do "comparar", medida pelo corpo da prévia) e 50% no PDF (300). As
  duas contas do ScanTailor dependem da página inteira na resolução em que rodam.
- De onde veio: a conta é do ScanTailor (código original, na DLL). No ScanTailor, com o "forçar preto e branco" de
  fábrica, a caixa escura vira PRETO: era o "ANTES" (metade preta, metade clara). A etapa 10b (27/10, D-189,
  `c8844671`) tirou o "forçar" para não apagar letra: a caixa escura passou a sair azul. Tratou o sintoma (o preto e a
  letra apagada), não a causa (a divisa no meio da tinta). Defeito do programa, não efeito de escolha do Kaique.
