# Graduale — "Graduale - Saeculum XIV"

- Arquivo: `D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE\Graduale - Saeculum XIV.pdf` (somente leitura).
- Tamanho: 283.790.785 bytes (~271 MB; o maior do acervo). Folhas: 750 (ficha de 18/07/2026 e relatório por livro). O exemplo do prompt de 18/07 dizia "320 páginas · 277 MB · ~400 DPI" — era só um modelo de ficha.

## Como ele é

| Pergunta | Resposta |
|---|---|
| Tem camadas? | Não. A imagem é **maior que a página** (1499 × 1800 pontos). |
| Borda preta de scanner? | Não. |
| Folha grande? | Não. |
| Moldura? | Borda de ramos em algumas páginas (p. 269). |
| Iluminura / cor? | Sim: capitulares em ouro, azul e vermelho, rubricação, **pautas vermelhas** (210 de 750 páginas com cor). |
| Manuscrito? | **Sim** (século XIV). Item 7.3 do plano: decidir se os manuscritos (Graduale, Palatino) entram no treino dos OCRs. |
| Música? | **Sim**: neumas e pautas; o Samuel: "não costumamos imprimir livros de musica". |
| DPI declarado errado? | **Sim.** O gabarito registra 72 DPI; a ficha de 18/07 diz "~112 DPI"; o histórico explica: "diz 112 na largura e 93 na altura, imagem esticada" ([PARTE -12 §5](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)). O programa usa 129–131 DPI nas ferramentas do ScanTailor. |
| Baixa resolução? | Sim ("qualidade BAIXA"). |
| Livro aberto? | Não. |
| Outro | Partituras tortas; letras raspadas; mancha do verso (16,2%). |

## Páginas de teste

- Gabarito: [221](../paginas-de-teste/graduale-221.md) (R5/R6, partitura torta), [222](../paginas-de-teste/graduale-222.md) e [223](../paginas-de-teste/graduale-223.md) (R3, margem da costura).
- Estudo do "Para revisar": [269](../paginas-de-teste/graduale-269.md), [588](../paginas-de-teste/graduale-588.md) (capitular azul).
- Citadas sem ficha: p. 224 do "Vamos recapitular" ("L com um desenho grande, queremos manter o desenho", não extraída, [lista.json](../../gabarito/lista.json)); p. 126 (régua de 08/08: "partitura manuscrita marcada 100% gravura", [histórico, PARTE 5](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)); p. 1, 8, 13 nas imagens da ficha de 18/07.

## O que o programa faz bem ou mal nele

- **Bem:** endireitar (nosso e ScanTailor acertam a 221); o G6 deixa o número da folha ("Cvij", "Cviij") inteiro; a pauta deixou de ser gravura (`47cabac`); vermelho sai preto no Preto e branco (V1, V3 "BOM").
- **Mal / aberto:** no "Guardar só o texto" **a música some** (botão "Trazer de volta" no ramo `fase2-para-revisar`); notas perdem traços no Preto e branco (N5); letras raspadas tratadas como mancha (depende do 6.1); "corte da sobra" do ScanTailor leva o número da folha; cunhas brancas no G6 (221).
- Velocidade: projeção de 58 min para o livro inteiro em 18/07 (4,66 s por página, a mais lenta depois do Horas).

## O que o Samuel e o Kaique disseram

- Samuel, 06/10/2026 (rodada 1, Graduale 222): "não precisa, mas esse é um caso isolado? porque esse é um livro atipico , não costumamos imprimir livros de musica, se isso não ir para revisar pode afetar outros livros?" ([rodada 1](../../relatorios/revisar-decisoes/rodada-1/respostas-samuel.md))
- Samuel, 30/09/2026, N5: "queremos conseguir as notas integralmente, diferenciado o que é mancha das notas da folha de trás e o que é nota realmente da pauta." ([conferência 2](../../relatorios/conferencia-samuel-2026-09-30-b.md))
- Prompt de 18/07 (Samuel): "`Graduale - Saeculum XIV` e `Livro de Horas - Luís XIV` têm iluminuras [...] O filtro **Preto e branco destruiria** essas páginas" ([histórico, APÊNDICE B, Parte 4](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)).
- Kaique: nada específico nas fontes lidas.

## Projetos salvos do Samuel

- Não achado nas fontes lidas.

## De onde veio

- Acervo desde 18/07/2026 (um dos "arquivos grandes", teste da regra de memória); ficha `LIVROS PARA FAZER TESTE (duplicata)\Graduale - Saeculum XIV.txt`; [relatório por livro](../../relatorios/por-livro/Graduale%20-%20Saeculum%20XIV.md).
