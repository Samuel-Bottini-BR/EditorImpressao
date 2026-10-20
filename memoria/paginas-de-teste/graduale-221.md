# Graduale — página 221 do PDF

- Livro: [graduale](../livros/graduale.md) · gabarito: sim (`graduale_p221`) · imagem: `gabarito/paginas/graduale_p221.png` (fora do git).
- Manuscrito do século XIV: **partitura torta** (neumas e pautas vermelhas), rubricação, letras raspadas; número da folha "Cvij" no alto à direita. Scan de 72 DPI declarado (o programa usa 129–131 DPI para as ferramentas do ScanTailor), imagem maior que a página, sem camadas. Gira 0,75°.

## O que ela tem de difícil

- R5 e R6 do "Vamos recapitular": endireitar a partitura, manter as linhas vermelhas e os neumas, papel branco, tirar manchas.
- Letras raspadas com o tom da mancha do verso: o programa trata como mancha.
- O número da folha "Cvij" e as guias do fim das pautas ficam perto da beirada: o corte (o nosso antigo, e o "corte da sobra" do ScanTailor) já os levou.

## Itens que a usam

- Gabarito dos itens `2.2` e `6.3` ([lista.json](../../gabarito/lista.json)): [2.2 Endireitar](../itens/2.2.md) (R5), [6.3 Tinta vermelha](../itens/6.3.md) (R6).
- [1.3 OCR](../itens/1.3.md): zonas do gabarito (Z20); a comparação dos OCRs não pega o erro dela.
- [2.1 Dividir](../itens/2.1.md): o corte da sobra do ScanTailor leva o "Cvij".
- [6.1 Mancha do verso](../itens/6.1.md): as letras raspadas dependem do 6.1.

## O que já se viu nela, rodada a rodada

- 28/09/2026 → corte novo: o fim do número da folha sai cortado (já vem cortado no escaneamento; vai para 2.5/2.13). [plano, Lista de bugs 28/09](../../docs/plano/PLANO-DEFINITIVO.md)
- 30/09/2026 → zonas do OCR: "NÃO SEI - precisa melhorar"; depois "RUIM - ele apagou um detalhe que já estava meio apagado na folha original" (Mágico pro).
- 01/10/2026 → medida do corte nas 32 páginas: "Cvii" sai "Cv" e meio "i". Tentado e revertido um segundo binarizador para as letras raspadas (depende do 6.1). Conferência 5: X2 "letras raspadas" → ideia de alerta (Lista de espera).
- 05/10/2026 → geometria D3: os dois endireitam bem (nosso +0,70°, ScanTailor +0,75°); o corte da sobra do ScanTailor leva o "Cvij" e as guias. [relatório D3](../../relatorios/fase2-geometria-d3-2026-10-05/relatorio.md)
- 06/10/2026 → estudo: "Guardar a tinta forte" certa; "Só o texto achado" errada (a música some). [estudo](../../relatorios/revisar-criterios-2026-10-06/revisar-criterios.md)
- 12/10/2026 → conferência do G6: "Está bom"; ficam as cunhas brancas quando o corte vai até a beirada.
- 13/10/2026 → investigação do G6: **melhorou** (o "Cvij" sai inteiro; somem as cunhas brancas; tinta de fora 0,20% → 0,03%). Conserto do corte: "Está bom". Caixa do conteúdo com o DPI do programa: pega o número da folha. "Para revisar": a medida não depende mais da prévia ("Graduale 221 sem aviso"); a aba Marcar se acerta sozinha (9 áreas viram 18 em 10,7 s).
- 20/10/2026 → hoje: endireitar (G6) aprovado e no `fase-1`; cunhas brancas e letras raspadas continuam como pendências.

## O que o Samuel disse

- 12/09/2026, "Vamos recapitular": origem do R5/R6 (texto literal no documento `explicacoes-do-samuel\Vamos recapitular...docx`, não transcrito aqui).
- 30/09/2026, Z20 (2ª conferência): "RUIM - ele apagou um detalhe que já estava meio apagado na folha original." ([conferência 2](../../relatorios/conferencia-samuel-2026-09-30-b.md))
- 01/10/2026, X2: "eu acho que ela pode ser tratada como mancha, mas sabemos que é uma linha apaga da folha, pode ser criado um alerta dentro do programa, para que se olhe o original e se reescreva manualmente, anote como ideia." ([conferência 5](../../relatorios/conferencia-samuel-2026-10-01.md))
- 05/10/2026, S2 (geometria): "CONCORDO - mas está cortando no lugar errado, mas isso é opnião minha, eu tenho como configurar esse corte para todas as paginas e o programa me avisar onde o corte pode ter ficado ruim" ([conferência 9](../../relatorios/conferencia-samuel-2026-10-05-g.md))
- 12/10/2026, G6: "Está bom" ([conferência 12/10/2026](../../relatorios/conferencia-samuel-2026-10-12.md)); 13/10/2026, `cg6-graduale-221`: "Está bom" ([conferência 13/10/2026](../../relatorios/conferencia-samuel-2026-10-13.md)).

## De onde veio (fontes)

- "Vamos recapitular..." (12/09/2026); gabarito montado em 25/09/2026 ([gabarito/LEIA-ME.md](../../gabarito/LEIA-ME.md), [lista.json](../../gabarito/lista.json)).
- [plano, Lista de bugs 28/09–01/10 e Registro](../../docs/plano/PLANO-DEFINITIVO.md); `ramo verif-corte-g6-2026-10-13: relatorios/conferir/corte-g6-2026-10-13/corte-g6.md`; `ramo fase2-geometria-perguntas: relatorios/conferir/geometria-g7-g10-2026-10-12/pesquisa.md`.
