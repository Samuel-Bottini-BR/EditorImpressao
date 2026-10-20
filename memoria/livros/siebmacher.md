# Siebmacher — "Schön Neues Modell Buch - Johann Siebmacher"

- Arquivo: `D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE\Schön Neues Modell Buch - Johann Siebmacher.pdf` (somente leitura).
- Tamanho: 11.849.866 bytes (~11 MB). Folhas: 134, todas deitadas (paisagem).

## Como ele é

| Pergunta | Resposta |
|---|---|
| Tem camadas? | **Sim** (Internet Archive): fundo a ~200 DPI + camada de cima com máscara a ~600 DPI. |
| Borda preta de scanner? | **Não exatamente**: fundo escuro **estreito de estúdio** (cinza-azulado, ~3–5%), mais visível à direita, à esquerda e em cima ("caso de borda escura estreita, mas não é borda preta larga", `LEIA-ME borda preta (05-10-2026).txt`). |
| Folha grande? | Não. |
| Moldura? | **Sim**: moldura de ornamentos em volta do texto (p. 7 e 9). |
| Iluminura / cor? | Pouca: 23 de 134 páginas com cor. |
| Manuscrito? | Tem páginas com **manuscrito de tinta clara** (p. 104, 105, 106). |
| Música? | Não. É um livro de modelos de bordado (gravuras de traço fino). |
| DPI declarado errado? | Não. |
| Baixa resolução? | Não (~601 DPI). |
| Livro aberto? | **Discordância entre fontes:** a ficha de 18/07 diz "folhas duplas: SIM (134 de 134 em paisagem)" e o programa de então dividia (268 páginas de saída, lombada incerta em 133). **Vale hoje:** é **uma página só, deitada**, com a beirada do livro; o certo é não dividir (relatório D3 de 05/10; conferência 9, F1; Lista de bugs 08/10/2026: "o Siebmacher 7 e 9 não são mais divididos"). |
| Outro | 39 folhas em branco (bordado transparecendo do verso), que saem "conferir" no "tirar o fundo". |

## Páginas de teste

- Gabarito: [7](../paginas-de-teste/siebmacher-007.md) (teste do ScanTailor de 24/09), [9](../paginas-de-teste/siebmacher-009.md) (R7, o print marcado "7"; item 2.6).
- Citadas de passagem: [104](../paginas-de-teste/siebmacher-104.md), [105](../paginas-de-teste/siebmacher-105.md), [106](../paginas-de-teste/siebmacher-106.md), [118](../paginas-de-teste/siebmacher-118.md), [124](../paginas-de-teste/siebmacher-124.md) (1.1, escrita clara que sumia). Sem ficha: p. 45 (régua de 08/08: "as legendas impressas da prancha não viram letra"), p. 1, 37, 111, 134 nas imagens de 18/07.

## O que o programa faz bem ou mal nele

- **Bem:** "tirar o fundo" sem perda depois dos consertos de 29/09 (página duvidosa sai "conferir"); dividir de fábrica desligado (livro novo não divide).
- **Mal / aberto:** a borda escura só sai com a busca da página / caixa do conteúdo do ScanTailor (2.13/2.5, na DLL no ramo `fase2-caixa-conteudo`, não ligadas); nosso corte via o preto e a beirada como tinta (fica quase na folha inteira); moldura de cima colada na borda com o G6 (p. 9); borda de folha volta no "Só as letras" (p. 9 direita).
- Velocidade: a tela "O que fazer" parava a janela 1,35 s ao clicar "continuar" no Siebmacher (Lista de bugs 05/10).

## O que o Samuel e o Kaique disseram

- Samuel, 05/10/2026, F1 (Siebmacher 7): "o scantailor respeitou o desenho, a moldura, ele só teria que cortar em cima e embaixo e do lado esquerdo par atirar a lombada, o nosso não respeitou a moldura e deixou a lombada." ([conferência 9](../../relatorios/conferencia-samuel-2026-10-05-g.md))
- Samuel, 05/10/2026, G7: "(a) Sim, desligada de fábrica; testar com o Siebmacher e os livros que eu indicar" ([conferência 9](../../relatorios/conferencia-samuel-2026-10-05-g.md)).
- Prompt de 18/07: "`Rhetorica Christiana` e `Schön Neues Modell Buch` têm gravuras em preto e branco com traço muito fino." ([histórico, APÊNDICE B](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md))
- Kaique: nada específico nas fontes lidas.

## Projetos salvos do Samuel

- Projeto "Schön Neues Modell Buch - Johann Siebmacher" (com `projeto.json`, `acoes.jsonl`, `posicao.json`, sem `resumo.json`): ficava invisível na tela inicial; em 29/09/2026, com autorização do Samuel, a gerente gravou só o `resumo.json` apontando para o PDF do acervo (134 folhas); cópia em `EditorImpressao-arquivos\backups\projetos-antigos-antes-de-reconhecer-2026-09-29\` ([plano, Lista de bugs 29/09/2026](../../docs/plano/PLANO-DEFINITIVO.md)).
- O projeto dele do Siebmacher está **em Preto e branco** e mudaria quase todas as páginas com o 1.1 automático (verificador, [plano, Registro 29/09/2026](../../docs/plano/PLANO-DEFINITIVO.md)).

## De onde veio

- Acervo desde 18/07/2026; ficha `LIVROS PARA FAZER TESTE (duplicata)\Schön Neues Modell Buch - Johann Siebmacher.txt`; [relatório por livro](../../relatorios/por-livro/Schon%20Neues%20Modell%20Buch%20-%20Johann%20Siebmacher.md); [relatório D3](../../relatorios/fase2-geometria-d3-2026-10-05/relatorio.md).
