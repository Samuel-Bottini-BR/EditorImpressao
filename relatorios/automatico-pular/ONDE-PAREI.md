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
- [ ] 6. GitHub: conjunto inteiro rodada 41688177103; velocidade rodada 41688199193 (8846017 → ae88f15).
- [ ] 7. Relatório.

## Perguntas para o Samuel

(nenhuma até agora)
