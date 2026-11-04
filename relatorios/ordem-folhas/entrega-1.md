# Entrega 1 — D-615: mudar folhas de lugar arrastando a miniatura

Ramo `ordem-folhas-2026-11-04` (saiu de `obra-2026-10-26`, `d66a588b`). PRONTO PARA CONFERIR (teste de
máquina e janela de verdade; o "está bom" é do Samuel).

## O que o Samuel pediu

"eu quero poder mover folhas para onde eu quiser dentro do app, quero poder arrastar e mover folhas, caso eu
precise resolver esse problema na mão" → proposta (arrastar uma miniatura da tira e soltar onde quiser) → "ok".

## O que mudou, em português simples

- Na tira de baixo, aperte uma miniatura e arraste. Ela fica apagadinha e uma **linha azul** aparece no vão
  onde ela vai cair. Soltou, a página muda de lugar no livro.
- Folha **não dividida** anda inteira. Folha **dividida**: anda só a página arrastada.
- Perto da beirada da tira, ela **rola sozinha** (mais depressa quanto mais tempo parado ali), para levar a
  página longe. Soltar bem acima ou abaixo da tira não muda nada.
- O **clique** continua igual (vai para a página na hora). Soltar no mesmo lugar não muda nada.
- **Ctrl+Z** desfaz, **Ctrl+Y** refaz; o Histórico mostra "Mudar de lugar a página N".
- A nova ordem vale na tela (tira, setas, "página N de M"), no **PDF de saída** e nos **cadernos** (etapa 7 e
  "Montar para imprimir", que monta a partir do PDF de saída).
- **Fechar e abrir** mantém a ordem (e o Ctrl+Z dela).
- Funciona também na ferramenta Dividir e com "Duas lado a lado" (tira em pares, D-611).

## Como cumpri cada decisão

| Decisão | Como | Prova |
|---|---|---|
| D-615 arrastar e soltar | tira: apertar, andar, soltar (sem o arrastar do Windows) | `test_d615_arrastar_a_miniatura...`, prints e1-03 a e1-06 |
| D-615 folha ou página | `core/ordem_das_paginas.bloco` | `test_d615_pagina_de_folha_dividida...`, `test_d615_folha_nao_dividida...` |
| D-615 tela, PDF, cadernos | a ordem é a da lista de páginas | `test_d615_a_nova_ordem_vale_no_pdf`, `..._nos_cadernos`, print e1-pdf-e1-pagina-1 |
| D-615 Ctrl+Z / Ctrl+Y | ação `livro.ordem_das_paginas` | testes + prints e1-07, e1-08 |
| D-615 reabrir | lista gravada no projeto.json | `test_d615_fechar_e_abrir_mantem_a_ordem`, print e1-14 |
| Projeto antigo igual | nada novo é gravado; sem ordem mudada nada muda | `test_d615_projeto_antigo_abre_como_hoje` |
| D-611 pares | arrastar com "Duas lado a lado" | prints e1-10 a e1-12 |
| D-601 Dividir | tira do Dividir também arrasta; setas em "Duas lado a lado" seguem a ordem | `test_d615_no_dividir...`, print e1-13 |
| Livro grande | conta, ação e desfazer em 1010 páginas < 0,5 s; a tira só troca os quadros de lugar | `test_d615_livro_de_1010_paginas...` |
| D-605 | testes antigos dos arquivos tocados passaram sem mudança | lista abaixo |

## Decisões técnicas (minhas)

- A ordem do livro é a ordem da lista de páginas, que já ia para o `projeto.json`. Nenhum campo novo no projeto.
  O desfazer ganhou o campo `livro.ordem_das_paginas` (a lista folha/metade de cada página, ~20 KB numa ação
  de um livro de 1010 páginas).
- Arrastar à mão (não o arrastar do Windows): funciona igual com o mouse e com o piloto da janela.
- "não dividir esta" numa folha com as páginas separadas: a folha inteira fica no lugar da **primeira** página
  dela no livro; o Ctrl+Z devolve cada página ao lugar em que estava. As duas metades guardadas ficam sempre
  na ordem esquerda, direita (antes era a ordem do livro, que era sempre essa).
- Depois de mudar de lugar, as prévias são refeitas (como depois de dividir uma folha).
- Achado na janela de verdade e consertado: passar um pouco da beirada esquerda cancelava; agora vale como a
  beirada (`test_d615_passar_da_beirada...`).

## Testes no PC (um arquivo por vez)

Novo: `tests/test_decisoes_ordem_folhas.py` — 12 passaram; no código de antes (`d66a588b`) os 11 primeiros
falharam (o 12º foi escrito depois do achado).

Antigos, sem mudança: test_decisoes_tira_em_pares 4, test_decisoes_tira_pares_juntas 3, test_miniaturas_novas 5,
test_decisoes_dividir 21, test_decisoes_dividir_metade 6, test_decisoes_dividir_arrastar 16,
test_decisoes_dividir_linha 13, test_decisoes_dividir_aviso 11, test_dividir_na_tela 9, test_dividir_no_programa 19,
test_dividir_ajustes_03_11 9, test_dividir_desmarcada_caixinha 3, test_automatico_pular_depois_de_dividir 4,
test_caderno_segue_as_etapas 11, test_decisoes_montar_cadernos 13, test_cadernos 28,
test_historico_depois_de_reabrir 11, test_recomeco_limpa_o_historico 13, test_projetos 24, test_decisoes_9b1 25,
test_decisoes_avisos 22, test_girar_cartoes_e_previas 23, test_decisoes 26, test_salva_sozinho 11,
test_trabalho_nao_se_perde 82. Todos passaram. Nenhum teste antigo foi mudado.

## Janela de verdade (Gradus Primus, cópia no scratchpad)

`relatorios/ordem-folhas/piloto.py e1`, anotações em `anotacoes-e1.txt`, prints em `prints/`:
e1-02 clique na miniatura 3 (vai à página 3, nada muda) · e1-03 arrastando a capa (linha azul antes da 1) ·
e1-04 capa na frente · e1-05 arrastando a contracapa até o fim (a tira rolou sozinha) · e1-06 contracapa na
página 140 · e1-07 Ctrl+Z · e1-08 Ctrl+Y · e1-09 seta depois da capa (página 2 = folha 2) · e1-10/11/12 pares ·
e1-13 Dividir (a tira do Dividir já com a capa na frente) · e1-14 reaberto (a ordem ficou) ·
e1-pdf-e1-pagina-1 (o PDF de saída começa pela capa) e -pagina-140 (a contracapa).

## Ressalvas

- Home/End no Dividir em "Duas lado a lado" continuam indo à folha 1 e à última pelo número (não mexi).
- Uma página por vez: arrastar várias de uma vez não existe (não foi pedido).

## Perguntas para o Samuel

1. (opcional, já tem jeito padrão) Se uma página de uma folha dividida foi levada para longe da irmã e depois a
   folha é juntada ("não dividir esta"), a folha inteira fica no lugar da primeira das duas. Ex.: com a capa
   na página 1 e a contracapa na 140 (print e1-06), juntar a folha 1 põe a folha inteira na página 1. Pode ser
   assim? Sugestão: sim.
