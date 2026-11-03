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

- [ ] 1. Teste de reversão (sem DLL, sem PDF) — rodar no código de `8846017` e ver falhar.
- [ ] 2. Conserto: pular pela página (o objeto), não pelo número.
- [ ] 3. Prova de comportamento D-004 com renumeração (janela, `tests/test_decisoes_automatico.py`).
- [ ] 4. Testes do Automático e do dividir no PC, um arquivo por vez.
- [ ] 5. `replay.py` do Gradus no código novo (140 páginas).
- [ ] 6. GitHub: conjunto inteiro e filtro de velocidade.
- [ ] 7. Relatório.

## Perguntas para o Samuel

(nenhuma até agora)
