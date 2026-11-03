# ONDE-PAREI — Automático pulando as folhas erradas depois de dividir (03/11/2026)

Ramo `automatico-pular-2026-11-03` (saiu de `obra-2026-10-26`, ponta `8846017`). Implementador.

## Decisões que esta tarefa precisa cumprir

- **D-004** (28/09/2026): "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas
  mexidas." — com "pular", a página mexida fica igual; as outras são feitas.
- **D-528** (27/10/2026): ao dividir uma folha pela primeira vez, as marcações feitas na folha inteira vão para a
  metade em que estão (não quebrar).
- **D-589** (30/10/2026): "Sim, se algo não está marcado, não é para fazer , certo?" — etapa desmarcada não é feita
  (não quebrar).
- **D-590** (30/10/2026): "Dividir" desmarcada no Automático não junta nada (não quebrar; a caixinha do Dividir é
  outro trabalho, não mexer).
- CLAUDE.md §11 item 7, "Só o que ele mandou": nenhuma tela, texto, pergunta ou comportamento novo.

## O defeito

Samuel (03/11, Gradus Primus): "fui testar o margens iguais e o dividir e acho que deu algum erro. envestiga isso
para mim" · "teve até uma folha que ficou colocada uma na outra." Folhas 1, 2 e 9 divididas à mão; Automático só com
"Dividir" no livro todo → 138 páginas; as folhas 6 e 7 do scan ficaram inteiras.

Causa: `core/automatico.aplicar` guarda as páginas a pular (D-004) pelo **número** da página, antes de dividir. Cada
folha dividida no laço renumera as seguintes, e o número guardado passa a apontar para outra página.

## Passos

- [x] 1. Teste de reversão `tests/test_automatico_pular_depois_de_dividir.py` (4 testes, sem DLL, sem PDF): no
      código de `8846017` 3 falham (18 páginas em vez de 20; a folha 10 com ângulo à mão era dividida).
- [x] 2. Conserto (`b772402`): `core/automatico._Puladas` guarda as páginas a pular pelo objeto da página;
      `_dividir` e `_ligar_na_pagina` perguntam "esta página está entre as puladas?". O `fotografar` não muda
      (roda antes de qualquer renumeração; ali o número ainda vale).
- [x] 3. Prova D-004 pela janela: `tests/test_decisoes_automatico.py::test_d004_pular_as_folhas_divididas_a_mao_divide_todas_as_outras`
      (7 folhas, 1, 2 e 6 divididas à mão → 14 páginas; no código antigo 13).
- [x] 4. PC, um arquivo por vez: test_decisoes_automatico 25, juntar_todas 3, montar_cadernos 13, nucleo2 21,
      dividir_metade 6 passaram (mais uma leva rodando: ver relatório).
- [x] 5. Replay do Gradus (`replay_gradus.py`, saída em `replay_gradus_saida.txt`): código novo 140 páginas,
      nenhuma folha inteira; código antigo 138, folhas de índice 5 e 6 inteiras.
- [x] 6. GitHub: conjunto inteiro rodada **41688177103 — passou** (5 partes + botões e prints); filtro de
      velocidade rodada **41688199193 — "igual (dentro do vai-e-vem)"** (8846017 → ae88f15; abrir 35,9 → 36,6 s,
      trocar de página 4,59 → 4,60 s, Mágico pro 47,6 → 47,5 s, Preto e branco 30,5 → 30,5 s, medianas das 3).
- [x] 7. Relatório (abaixo). **PRONTO PARA A GERENTE** (nada juntado em `obra-2026-10-26` nem `fase-1`).

## Relatório

O Automático agora pula exatamente as folhas e páginas mexidas à mão e divide todas as outras, mesmo quando as
páginas mudam de número no caminho. No Gradus, o "Dividir" dá 140 páginas (antes 138, com as folhas 6 e 7 inteiras).

Arquivos: `core/automatico.py` (classe `_Puladas`; `aplicar`, `_dividir`, `_ligar_na_pagina`),
`tests/test_automatico_pular_depois_de_dividir.py` (novo), `tests/test_decisoes_automatico.py` (1 prova nova),
`relatorios/automatico-pular/` (este arquivo, `replay_gradus.py`, `replay_gradus_saida.txt`).

Testes no PC (um arquivo por vez, código novo): pular_depois_de_dividir 4, decisoes_automatico 25, juntar_todas 3,
montar_cadernos 13, nucleo2 21, dividir_metade 6, decisoes_dividir 19, dividir_no_programa 19, dividir_na_tela 9,
automatico_ver_como_fica 22, margens_no_depois 5, opcoes_do_filtro 21, filtro_automatico 4 — todos passaram.
No código de `8846017`: 3 dos 4 testes de reversão e a prova nova da janela **falham** (18 em vez de 20; 13 em vez
de 14; folha com ângulo à mão dividida).

### Como cumpri cada uma
- **D-004:** com "pular", a folha/página mexida fica igual e as outras são feitas, qualquer que seja a ordem —
  `test_dividir_pula_so_as_folhas_divididas_a_mao_mesmo_com_as_paginas_renumeradas`,
  `test_dividir_em_qualquer_ordem_de_folhas_mexidas`, `test_endireitar_na_mesma_rodada_pula_a_pagina_certa_depois_de_dividir`,
  e pela janela `test_d004_pular_as_folhas_divididas_a_mao_divide_todas_as_outras` (pergunta "6", 14 páginas, PDF
  com 14). "Rodar nelas também" continua igual (`test_rodar_nelas_tambem_divide_todas_as_folhas`, e as 3 provas
  D-004 antigas passam).
- **D-528:** a partição continua pela mesma `metades_da_pagina` com a linha achada; `test_decisoes_nucleo2.py` (21) passa.
- **D-589:** `_desligar_as_desmarcadas` não foi tocado; `test_decisoes_montar_cadernos.py` (13) passa.
- **D-590:** não mexi na caixinha do Dividir nem no `_desligar`; `test_decisoes_juntar_todas.py` (3) passa.
- **§11 item 7:** nenhuma tela, texto ou pergunta mudou (só `core/automatico.py`).

### Ressalvas
- A folha que tem uma página mexida à mão em OUTRA etapa (ex.: ângulo à mão) e é pulada também não é dividida.
  Isso já era assim antes (o pular sempre pulou a folha inteira dessa página); não mudei.
- `fotografar` continua usando os números das páginas: ali ainda não houve renumeração, então estão certos.

## Perguntas para o Samuel

(nenhuma até agora)
