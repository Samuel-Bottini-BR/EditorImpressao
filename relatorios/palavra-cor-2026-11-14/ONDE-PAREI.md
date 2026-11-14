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

## A regra da ferramenta e os caminhos (§11.12, item 3; achados com grep por `cores_scantailor`, `letras_com_a_cor`, `reduzir_cores`, `filtro_com_as_caixinhas`, `renderizar_pagina`, `_filtrar`)
**A função que decide a cor de cada letra:** `core/cores_scantailor.aplicar(preparada, saida, filtro, letras, reduzir, dpi)`
→ `cores()` → DLL `st_ferramentas_cores` (segmentação + posterização do ScanTailor). Ela é chamada em **dois** lugares
do `core/pipeline.py`, os dois com a mesma função (nenhuma conta copiada):
- `_filtrar` (linha ~3514): o corpo da página com a marcação, o "Só as letras", o "só neste pedaço";
- `filtro_com_as_caixinhas` (linha ~3564): o filtro numa imagem solta (sem a marcação), para cartões e "comparar".

| Caminho | Por onde passa | Usa a função? | Resolução |
|---|---|---|---|
| PDF ("Confirmar e processar") | `processar` → `_pagina_pronta` → `_filtrar` | sim | 300 |
| Prévia da página e miniaturas da tira | `GerenciadorPrevias` → `renderizar_pagina` → `_filtrar` | sim | 110 |
| Grade "Todas as páginas", folhear, folhas do caderno | as prévias (`renderizar_pagina`) | sim | até 160 / 90 / 180 |
| Tela cheia dos filtros (D-192) | `renderizar_com_filtro` → `renderizar_pagina` → `_filtrar` | sim | 150 |
| Figurinhas (cartões) do painel Filtro | `_TarefaCartoes` → `filtro_com_as_caixinhas` | sim, **sem a marcação** | 70 (amostra) |
| "Comparar" da tela ampliada | `tela_ampliada` → `filtro_com_as_caixinhas` | sim, **sem a marcação** | 220 |
| Automático / "Limpar a folha" (D-594) | grava os dois campos nas páginas; prévia por `renderizar_pagina` + `compor_como_no_pdf` | sim | 180 (prévia) e 300 (PDF) |
| Painel Filtro (caixinhas), tela cheia (caixinhas), "Aplicar em" (só nesta / todas / daqui em diante), desfazer e refazer | só gravam `letras_com_a_cor` / `reduzir_cores` na página (`_mudar_cores`, `_gravar_opcao_da_tela_cheia`, `MARCAS_DA_PAGINA`); a imagem vem dos caminhos acima | — | — |
| "Só neste pedaço" | o pedaço é composto dentro de `_filtrar_preto_no_branco`; as cores valem depois, na página composta | sim | a do caminho |
| "Tirar o fundo" (e Original com o fundo tirado) | `aplicar` devolve None (nada muda) | sim (sai sem cor) | — |

**Conclusão:** a regra já está num lugar só (bom). O defeito está **dentro** dela, e ela dá resultado diferente em cada
resolução porque as duas contas do ScanTailor olham a página inteira (o limiar de cada canal na segmentação; o
"mais escuro da página" e "a cor mais frequente de cada caixa" na redução). Por isso a prévia (110), a tela cheia
(150), o Automático (180), o "comparar" (220) e o PDF (300) pintam palavras diferentes de azul. Cartões e "comparar"
ainda recebem uma página sem a marcação (outra entrada, mesma regra) — já era assim, fora do escopo.
