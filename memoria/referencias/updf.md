# Referência: UPDF (o leitor de PDF do Samuel)

Conferido em 20/10/2026. **O plano manda**: o que vai para o programa está no
[PLANO-DEFINITIVO](../../docs/plano/PLANO-DEFINITIVO.md) (item 2.6 e Lista de espera de 24/09/2026).

## Em uma frase

O UPDF é o leitor de PDF que o Samuel usa. Ele serve de modelo em duas coisas: **a janela de imprimir** (o Samuel quer
"TODAS essas opções dentro do programa", 14/10/2026) e **o layout limpo e a grade de páginas** (Lista de espera,
24/09/2026).

## 1. A janela de imprimir (14/10/2026)

### As cinco fotos

Estão no git: [`relatorios/conferencia-samuel-2026-10-14/prints/`](../../relatorios/conferencia-samuel-2026-10-14/explicacao-da-impressao.md)
(`janela-imprimir-1.png` a `-5.png`), junto com a explicação. A impressora é a EPSON WF-C5890. O Registro 19/10/2026
diz que são "cinco fotos da janela de imprimir do **UPDF**"; o arquivo da explicação diz só "leitor de PDF dele".

| Foto | O que mostra |
|---|---|
| [1](../../relatorios/conferencia-samuel-2026-10-14/prints/janela-imprimir-1.png) | Livro de 250 páginas, A4 paisagem, aba **Tamanho**, "Escala personalizada (%)" em **75**; prévia com duas páginas lado a lado ("Redimensionar: 75%") |
| [2](../../relatorios/conferencia-samuel-2026-10-14/prints/janela-imprimir-2.png) | O mesmo, com a escala em **83** |
| [3](../../relatorios/conferencia-samuel-2026-10-14/prints/janela-imprimir-3.png) | Lista **Tamanho do papel** aberta (A4, Carta, Ofício 9, 8,5 × 13 pol., México-Ofício, Ofício, Executivo, Envelope #10, 8 × 10 pol., 5 × 7 pol. ...) e a aba **Livreto**: "Ordem de páginas: Frente e verso", "Folhas de 1 – 244", "Encadernação: Esquerda" |
| [4](../../relatorios/conferencia-samuel-2026-10-14/prints/janela-imprimir-4.png) | Capa do Balzac (486 páginas), A4 paisagem, **Ajustar** → 69% |
| [5](../../relatorios/conferencia-samuel-2026-10-14/prints/janela-imprimir-5.png) | A mesma capa em A4 retrato, **Ajustar** → 97% (a escala personalizada guarda 70) |

Em todas: orientação Retrato/Paisagem, "Rotação Automática", "Centralizar Automático", cópias e "Agrupar", "Imprimir em
escala de cinza (preto e branco)", "Imprimir como imagem", "Reverter páginas", intervalo de páginas, e quatro abas:
**Tamanho · Pôster · Múltiplo · Livreto**. Na aba Tamanho: Ajustar · Tamanho real · Escala personalizada (%) ·
Reduzir páginas muito grandes.

### O que o Samuel quer dele (literal, chat de 14/10/2026)

Fonte: [`relatorios/conferencia-samuel-2026-10-14/explicacao-da-impressao.md`](../../relatorios/conferencia-samuel-2026-10-14/explicacao-da-impressao.md).
Trecho que fala das opções da janela de imprimir:

> "2. Na hora de gerar o arquivo para impressão
> É só nesta fase que se decide o formato de saída. Eu quero poder escolher:
> - Livreto na horizontal (A4 deitada com duas páginas A5 lado a lado, embaralhadas na ordem de caderno — imposição), ou
> - Página inteira A4 na vertical, ou
> - todas as outras opções que aparecem nos prints do PDF que mandei. Quero TODAS essas opções dentro do programa, para ter bastante escolha."

> "Controles de escala na impressão:
> - aumentar ou diminuir a escala das páginas no formato livreto (igual à escala personalizada que aparece nos prints);
> - poder diminuir só o lado esquerdo, só o lado direito, ou as duas páginas juntas."

O resto da explicação (as duas fases, as margens de 1 cm, o aviso de margem e o livreto "como o embaralhador antigo")
está no mesmo arquivo; o livreto está em [embaralhador.md](embaralhador.md). Anotado no item [2.6](../itens/2.6.md).

### O que já foi decidido sobre a impressão (Registro 14/10/2026)

- `g10-papel-ou-pagina`: decidida pela explicação: "é o papel da impressora; formato só na impressão".
- `g10-ajustar-todas`: "Cada página até encher a folha" = **"Ajustar" de fábrica** (o nome vem da aba Tamanho do
  UPDF). Comentário dele: "Porque essa opção voltou ? eu já não tinha respondido?"
- `g11-margem-impressora`: "1 cm a partir de onde a impressora imprime (1,3 cm do papel)".
- `g12-diminuir-um-lado`: "Em todas, e dá para mudar uma folha só".
- **Aberta:** `g9-folha-maior-impressao`, "A folha muito maior (tabela dobrável): como ela sai impressa?", com opções
  tiradas do UPDF: "Ajustar: gira de pé e reduz até caber na página A5" · "Tamanho real, numa folha A4 à parte" ·
  "Pôster" · "Divide em duas páginas" · "Ainda não entendi" ([histórico, PARTE -16 §4](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)).
  Sem resposta na leitura de 19/10/2026.

### Quem está estudando hoje

O pesquisador, no ramo `pesquisa-impressao-2026-10-19` (ver [ramos](../ramos.md)). O ONDE-PAREI dele (19-20/10)
diz que falta "Pesquisar cada opção do UPDF (o que faz) e como fazer com PyMuPDF" e escrever
`docs/pesquisa/fase-impressao.md`.

## 2. Layout: a grade de páginas e a tela limpa (24/09/2026)

As duas fotos estão no git, em `docs/plano/referencias-layout/` (o caminho da Lista de espera,
`referencias-layout/updf-*.jpg`, é relativo a `docs/plano/`).

| Data | Ideia (Lista de espera, literal) | Foto |
|---|---|---|
| 24/09/2026 | "Ver todas as páginas do livro em grade, como o "Organizar páginas" do UPDF: seleção múltipla, girar, apagar, extrair, inserir, dividir." Quem pediu: Samuel. Fase sugerida: "Fase 4 (layout), a confirmar" | [updf-todas-as-paginas.jpg](../../docs/plano/referencias-layout/updf-todas-as-paginas.jpg) (o livro "Vidas dos Santos" em grade de 6 colunas; barra com Seleção múltipla, Selecionar páginas, Inserir, Extrair, Substituir, Dividir, girar, apagar) |
| 24/09/2026 | "Layout limpo como o do UPDF: página no centro, poucas ferramentas em ícones numa barra fina no topo, miniaturas numa coluna à esquerda que dá para esconder, navegação e zoom num canto de baixo." Quem pediu: Samuel. Fase sugerida: "Fase 4 (layout), a confirmar" | [updf-tela-de-leitura.jpg](../../docs/plano/referencias-layout/updf-tela-de-leitura.jpg) |

O que aconteceu com elas no layout (fontes: o inventário de telas de 02/10,
[`relatorios/layout-inventario-2026-10-02/inventario-telas-e-funcoes.md`](../../relatorios/layout-inventario-2026-10-02/inventario-telas-e-funcoes.md),
e o `Plano de layout (rascunho).md`, fora do git em `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\`):

- O agente de layout leu "as duas fotos do UPDF (tela de leitura e grade de páginas)" em 25/09 (rascunho, linha 12).
- No inventário, a grade "todas as páginas" do UPDF com seleção múltipla ficou entre as peças **caras**; "uma versão só
  para **navegar** (sem selecionar várias) seria bem mais barata" (rascunho).
- A tela "Todas as páginas" foi aprovada como parte do protótipo, com "uma a uma / em pares" (no par, o clique mostra
  as duas como vão ser impressas); a vista que vem de fábrica ainda está "A decidir" (rascunho, tabela de decisões;
  Registro 12/10/2026: "qual vista de 'Todas as páginas' vem de fábrica" ficou para a rodada 14).
- Rodada 13, 808 (Registro 12/10/2026): o botão de "Todas as páginas" fica **no cabeçalho das miniaturas**.
- As miniaturas do nosso programa: a posição de fábrica é **embaixo** (rascunho: "Embaixo (opção 2, decidido)";
  esquerda, direita e em pares como opções). Ou seja, a "coluna à esquerda" do UPDF virou opção, não padrão.
- A grade e a "área de trabalho" entram nas etapas 4 a 7 do layout, em andamento hoje no ramo
  `layout-etapas4a7-2026-10-19` (ver [layout](../itens/layout.md)).
