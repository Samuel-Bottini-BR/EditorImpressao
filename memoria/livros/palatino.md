# Palatino — "Giovambattista Palatino cittadino romano"

- Arquivo: `D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE\Giovambattista Palatino cittadino romano.pdf` (somente leitura; cópia idêntica em `...\LIVROS PARA FAZER TESTE (duplicata)\`).
- Tamanho: 9.736.688 bytes (9,3 MB). Folhas: 134 (ficha de 18/07/2026 e relatório por livro de 08/08).
- Um dos nove livros do acervo original (2903 folhas ao todo).

## Como ele é

| Pergunta | Resposta |
|---|---|
| Tem camadas (Internet Archive)? | **Sim**: fundo + camada de cima com máscara JBIG2 de 1 bit, 400 DPI. Nas páginas HQ (primeiras e últimas) o fundo vem em resolução cheia; nas outras, a 133 DPI. |
| Borda preta de scanner? | Não. |
| Folha grande? | Não. |
| Moldura? | Sim: molduras de fios, floreios e laços (p. 9, 10, 57, 67, 113). |
| Iluminura / cor? | Pouca cor: 7 de 134 páginas com tinta colorida (ficha de 18/07); manchas cor de ferrugem (R4). O relatório por livro de 08/08 diz "o livro inteiro é colorido" (observação automática do programa de então). |
| Manuscrito? | É um manual de caligrafia com xilogravuras (capitulares, retrato). O plano trata como manuscrito no item 7.3 ("Decidir se os manuscritos (Graduale, Palatino) entram"). |
| Música? | Não. |
| DPI declarado errado? | Não (400 DPI de verdade). |
| Baixa resolução? | Não (qualidade boa). |
| Livro aberto? | Não ("este livro tem uma página por folha, não duas"). |

## Páginas de teste

- Gabarito: [5](../paginas-de-teste/palatino-005.md) (R1, retrato), [7](../paginas-de-teste/palatino-007.md) (R1), [9](../paginas-de-teste/palatino-009.md) (R1, capitular Q), [10](../paginas-de-teste/palatino-010.md) (R2, sombra do verso), [57](../paginas-de-teste/palatino-057.md) (R3, margens), [66](../paginas-de-teste/palatino-066.md) e [67](../paginas-de-teste/palatino-067.md) (R4, manchas; a 67 é o print marcado "76").
- Estudo do "Para revisar": [76](../paginas-de-teste/palatino-076.md) (a p. 76 do PDF, "DELLE CIFRE" — não é o print "76"), [104](../paginas-de-teste/palatino-104.md), [113](../paginas-de-teste/palatino-113.md).
- Citada de passagem: [12](../paginas-de-teste/palatino-012.md) (pontinhos do verso já na camada de cima).

## O que o programa faz bem ou mal nele

- **Bem:** "Tirar o fundo" (1.1, aprovado em 02/10/2026) mantém letras e molduras depois dos consertos de 29/09; retrato do p. 5 com fundo branco (B2 "BOM"); caixa cinza do 67 e tira creme do 9 resolvidas com o detector do ScanTailor (1.2).
- **Mal / aberto:** manchas vermelhas e marrons (R4, item 6.2, não começado); no "Só as letras" de fábrica, capitulares xilográficas de traço claro somem (67, 76, rodapé do 66); faixa cinza ao lado da moldura no "tirar o fundo" (p. 10, vai para o 1.5); "Palatino 5 fica intacto e amarelo" no 1.1 (regra da Fase 1 pede papel branco: 1.5).
- Achado de 08/09/2026: o travamento do MuPDF (duas threads lendo o mesmo PDF) foi visto ao vivo com o Palatino e a Rhetorica ([histórico, PARTE -2](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)).
- No binarizador, "No Palatino o Otsu sai sólido e o Sauvola quebra o traço" (`CLAUDE.md` §9).

## O que o Samuel e o Kaique disseram

- Samuel: ver as fichas das páginas (conferências de 30/09 a 12/10/2026). Ex.: 30/09/2026, G3 Palatino 67: "quero pode melhorar o contorno das letras, mas isso seria uma nova funcionalidade" ([conferência 30/09](../../relatorios/conferencia-samuel-2026-09-30.md)).
- Kaique: nada específico deste livro nas fontes lidas (as queixas em `BIBLIOTECA DO FIM DOS TEMPOS\Teste de livros` não citam livro).

## Projetos salvos do Samuel

- Há projeto real do Palatino na pasta de dados dele (dois, segundo o conserto `144d29f`: "os projetos reais do Samuel, inclusive os dois do Palatino, casam dos dois jeitos"); estava gravado com `\` no caminho ([plano, Lista de bugs 29/09/2026](../../docs/plano/PLANO-DEFINITIVO.md)).
- Projeto-sombra "Palatino" (marca do bug do mesmo nome de arquivo; sem trabalho real perdido, pelo que se viu).
- Verificador de 29/09: os projetos do Palatino, da Rhetorica e do Siebmacher (em Preto e branco) mudariam quase todas as páginas ao reabrir com o 1.1 automático (por isso o 1.1 virou filtro) ([plano, Registro 29/09/2026](../../docs/plano/PLANO-DEFINITIVO.md)).

## De onde veio

- Acervo de teste desde 18/07/2026 (prompt de testes, [histórico, APÊNDICE B](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)); movido da área de trabalho para `EditorImpressao-arquivos` em 07/09/2026 (`CLAUDE.md` §7).
- Ficha de 18/07/2026: `LIVROS PARA FAZER TESTE (duplicata)\Giovambattista Palatino cittadino romano.txt` (134 páginas, ~400 DPI, bem amarelado, verso 8,8%); [relatório por livro](../../relatorios/por-livro/Giovambattista%20Palatino%20cittadino%20romano.md).
