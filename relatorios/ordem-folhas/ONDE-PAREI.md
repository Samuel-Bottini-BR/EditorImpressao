# ONDE-PAREI — ordem das folhas (D-615 e D-616)

Ramo `ordem-folhas-2026-11-04` (saiu de `obra-2026-10-26`, `d66a588b`). Cópia:
`D:\programas\EditorImpressao\.claude\worktrees\ordem-folhas`.

## Decisões que esta tarefa precisa cumprir

- **D-615** (04/11): "eu quero poder mover folhas para onde eu quiser dentro do app, quero poder arrastar e
  mover folhas, caso eu precise resolver esse problema na mão" → proposta (arrastar a miniatura) → "ok".
  Arrastar uma miniatura da tira e soltar onde quiser; a folha (ou a página, se dividida) muda de lugar; vale
  na tela, no PDF e nos cadernos; Ctrl+Z desfaz.
- **D-616** (04/11): caixinha "A 1ª folha é a capa aberta" na etapa Dividir do Automático, desmarcada de
  fábrica, por livro; marcada, ao dividir, a metade da direita da 1ª folha vira a página 1 e a da esquerda vai
  para a última.
- **D-004** (pular as mexidas à mão), **D-527** (aviso de número fora de ordem: Lista de espera, não muda aqui),
  **D-589** (o que está desmarcado não é feito), **D-590** (Dividir desmarcado não junta), **D-601** (Dividir em
  "Uma página"; tira do Dividir por página), **D-603** (caderno da etapa 7 segue as etapas marcadas antes do
  Rodar), **D-611** (tira em pares com "Duas lado a lado"), **D-613** (aviso do "dividir todas"), **D-614**
  (prévia do Dividir uma página por vez), **D-605** (o novo não estraga o testado).

## O que já está escolhido e testado aqui

Tira de miniaturas (`ui/widgets/tira_miniaturas.py`):
- clique simples vai para a página/folha (`tests/test_decisoes_9b1.py::test_page_down_chega_a_pagina_depois_de_clicar_numa_miniatura`);
- duplo clique amplia; a tira não fica com o teclado (D-021, etapa 9b-1);
- pares "Ver em pares" (D-032) e pares da vista "Duas lado a lado" (D-611): `test_decisoes_tira_em_pares.py`,
  `test_decisoes_tira_pares_juntas.py`;
- giro sem reler o PDF, miniatura "como sai" (D-547), tique e "!" (`test_miniaturas_novas.py`,
  `test_girar_cartoes_e_previas.py`, `test_decisoes_avisos.py`).

Dividir (`core/dividir_a_mao.py`, ferramenta Dividir): `test_decisoes_dividir.py`, `test_decisoes_dividir_metade.py`
(D-601), `test_decisoes_dividir_arrastar.py`, `test_decisoes_dividir_linha.py`, `test_decisoes_dividir_aviso.py`
(D-613), `test_dividir_na_tela.py`, `test_dividir_no_programa.py`, `test_dividir_ajustes_03_11.py`,
`test_dividir_desmarcada_caixinha.py` (D-590), `test_automatico_pular_depois_de_dividir.py` (D-004).

Cadernos: `test_caderno_segue_as_etapas.py` (D-603), `test_decisoes_montar_cadernos.py`, `test_cadernos.py`,
`test_decisoes_caderno_tela_grande.py`.

Automático: `test_decisoes_automatico.py`, `test_decisoes_automatico_ver_como_fica.py` (D-577/D-614),
`test_decisoes_automatico_margens_no_depois.py`, `test_decisoes_automatico_opcoes_do_filtro.py`.

Desfazer e projeto salvo: `test_historico_depois_de_reabrir.py`, `test_recomeco_limpa_o_historico.py`,
`test_projetos.py`, `test_salva_sozinho.py`, `test_trabalho_nao_se_perde.py`; provas gerais `test_decisoes*.py`.

## Como vou fazer (técnico)

- A ordem do livro É a ordem da lista `projeto.paginas` (já gravada no `projeto.json`; o PDF, a tela e os
  cadernos já seguem essa lista). Projeto antigo: a lista em ordem de folha, abre igual.
- Ação nova do desfazer com o campo `livro.ordem_das_paginas` (a lista [folha, metade] de cada página, na
  ordem). Módulo novo `core/ordem_das_paginas.py`.
- Tira: arrastar com o mouse (sem o arrastar do Windows), linha azul onde vai cair, a miniatura arrastada fica
  apagadinha; remontar a tira depois de mudar a ordem só reordena os quadros (não lê o PDF de novo).

## Andamento

- [x] Entrega 1 (D-615): commits 7150504a..c34699d3 (+ relatório `entrega-1.*`); testes no PC ok; janela de
  verdade ok (prints e1-*); GitHub 41885681255 passou; velocidade 41885686939. Mandada à gerente.
- [x] Entrega 2 (D-616): b701df31..bd406a79; `tests/test_decisoes_capa_aberta.py` (6 passam; 5 falham na
  ponta da entrega 1); janela de verdade ok (prints e2-*); GitHub 41888422108 e velocidade 41888426950.

## Perguntas para o Samuel

1. (opcional; tem jeito padrão) Juntar ("não dividir esta") uma folha cujas páginas foram separadas: a folha
   inteira fica no lugar da primeira das duas. Pode ser assim? Sugestão: sim. (ver `entrega-1.md`)

## GitHub

- Entrega 1: testes 41885681255 passaram inteiros; velocidade 41885686939 (obra-2026-10-26 -> ordem-folhas) "igual".
- Entrega 2: testes 41888422108 passaram inteiros (com botões e prints da janela real); velocidade 41888426950
  (755bfae3 -> ordem-folhas) "igual".
