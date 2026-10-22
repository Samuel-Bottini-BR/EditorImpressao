# Horas — página 11 do PDF

- Livro: [horas](../livros/horas.md) · gabarito: sim (`horas_p011`) · imagem: `gabarito/paginas/horas_p011.png` (fora do git).
- Frontispício iluminado: **iluminura** com ouro, anjinho e azuis; no centro claro, "HEURES DE LOUIS LE GRAND…" em vermelho e azul. 72 DPI declarado (o programa usa 138–142 DPI nas ferramentas do ScanTailor), sem camadas. Gira 0,62°.

## O que ela tem de difícil

- R6: letras nas cores originais no meio da iluminura, papel branco, gravura intacta.
- Regra da Fase 1 (28/09): iluminura intacta; só o papel em volta do texto de dentro é branqueado.
- No Preto e branco antigo a iluminura vira preto sólido; no Mágico pro antigo a pintura era apagada como "pedaços do tamanho de letra".
- O nosso endireitar entortava esta página reta; as contas discordam (aviso C1).
- Página pesada: Preto e branco com decoração em cor dá 25,6 MB por página.

## Itens que a usam

- Gabarito dos itens `fase1` e `6.3` ([lista.json](../../gabarito/lista.json)); página obrigatória da Fase 1 (28/09: "iluminura intacta, centro branco").
- [1.2 Detector de gravura](../itens/1.2.md), [1.5](../itens/1.5.md), [1.6 PDF em duas camadas](../itens/1.6.md) (peso), [2.2 Endireitar](../itens/2.2.md), [6.3 Tinta vermelha](../itens/6.3.md).

## O que já se viu nela, rodada a rodada

- 24/09/2026 → ScanTailor: "ruim (áreas da iluminura viraram preto sólido)".
- 28/09/2026 → o Mágico pro apaga quase toda a iluminura (vai para 1.2/1.4/1.5).
- 30/09/2026 → G1 "RUIM" (cor e sujeira); Z8 "RUIM" (esbranquiça, sombras).
- 01/10/2026 → consertos `df9e3be`: ouro, anjinho e azuis como no original. I1 e MP4 "BOM"; A2 miolo creme das letras douradas "RUIM" → consertado.
- 02/10/2026 → A2 e P4 "BOM". Horas 11 mais rápida (17 → 12 s, `7f50e70`). X1 ponto azul encostado na moldura: "entendi" (1.4/1.5).
- 05/10/2026 → D3: o nosso entorta (-0,50°), o ScanTailor deixa reta. Misto: "A". Trava do atalho da Horas 11 consertada.
- 08/10/2026 → endireitar do ScanTailor no programa: aviso C1. 12/10 G6: "Está bom".
- 13/10/2026 → investigação do G6: igual ao olho ("a conta errou": contou a moldura pintada como faixa).

- 20/10/2026 → achado: o mesmo código nem sempre dava a mesma imagem (Mágico pro): com pouca memória o modelo de regiões ficava desligado a sessão inteira e o detector de gravura caía no antigo; repetida 4 vezes no `fase-1` deu sempre a mesma soma. 21/10/2026: consertado em `2ff16e7` (tenta de novo); ramo `consertos-2026-10-21`, não juntado.

## O que o Samuel disse

- 30/09/2026, G1: "RUIM - o centro está branco e pegou a luminaria inteira, mas a cor ainda não está satisfatoria, se você analisar vai ver que perdemos bastante da cor original, e ainda vemos uma sujeiras na parte branca da folha." ([conferência 30/09](../../relatorios/conferencia-samuel-2026-09-30.md))
- 30/09/2026, Z8: "RUIM - Ele está esbranquiçando algumas partes da imagem, quase como se estivesse apagando algumas partes, e objetivo era ele da vida né, e esta criando sombras onde não existe."; N1: "RUIM - o desenho ainda está muito ruim, perde um monte de detalhes, sei que desiners usam tecnicas interessantes dentro do adobe photoshope para fazer esse tipo de coisa sem perder detalhes, não sei como podemos fazer isso, anotar para pesquisar depois" ([conferência 2](../../relatorios/conferencia-samuel-2026-09-30-b.md))
- 01/10/2026, A2: "RUIM - eu não quero esses miolos de letras com a cor da pagina de trás, queremos a pagina inteiramente branca Falando nisso, eu quero ter a opção de tirar a luminura se eu qusier, no caso, apagar todos os desenhos do livro e deixar só escrita." ([conferência 5](../../relatorios/conferencia-samuel-2026-10-01.md))
- 05/10/2026, E1: "CONCORDO" (o nosso entorta uma página reta) ([conferência 9](../../relatorios/conferencia-samuel-2026-10-05-g.md)); H11: "A - Guardar a tinta forte" ([conferência 8](../../relatorios/conferencia-samuel-2026-10-05-f.md)).
- 12/10/2026, G6: "Está bom" ([conferência 12/10/2026](../../relatorios/conferencia-samuel-2026-10-12.md)).

## De onde veio (fontes)

- "Vamos recapitular..." (12/09/2026) e teste do ScanTailor de 24/09/2026 ([gabarito/LEIA-ME.md](../../gabarito/LEIA-ME.md)).
- [plano, Fase 1 (regras de 28/09), Lista de bugs 28/09–01/10, Registro](../../docs/plano/PLANO-DEFINITIVO.md); [relatório D3](../../relatorios/fase2-geometria-d3-2026-10-05/relatorio.md).

- Lista de bugs 20/10/2026 e [PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §4 (ver [para-revisar](../itens/para-revisar.md))
