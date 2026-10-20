# Explicação da impressão, do Samuel (14/10/2026, no chat do Claude Code, literal)

Enviada como resposta às quatro perguntas abertas da página de escolhas (`g10-papel-ou-pagina`,
`g10-ajustar-todas`, `g9-folha-maior-impressao`, `g7-borda-ate-onde`). Junto, cinco fotos da janela
de imprimir do leitor de PDF dele (impressora EPSON WF-C5890), em `prints/`.
Mensagem seguinte dele: "This is to respond uh, to those questions that you had there. É, se não
responder, pode abrir o relatório de novo para mim."

---

Esta é a explicação da impressão, para refazer as 4 perguntas abertas no "Escolhas do Editor de Impressão" (as duas de Tamanho final, a da folha dobrável e a da borda preta).

A ideia central: o programa tem duas fases separadas.

1. Na edição
Cada página ocupa a folha inteira. Aqui eu só me preocupo em deixar legível, a folha branca, os desenhos certos, endireitar. Não penso em tamanho final, formato nem margem.
(Mexer na escala do conteúdo — aumentar/diminuir — também existe aqui dentro, mas na prática só vou me preocupar com isso na hora de imprimir.)

2. Na hora de gerar o arquivo para impressão
É só nesta fase que se decide o formato de saída. Eu quero poder escolher:
- Livreto na horizontal (A4 deitada com duas páginas A5 lado a lado, embaralhadas na ordem de caderno — imposição), ou
- Página inteira A4 na vertical, ou
- todas as outras opções que aparecem nos prints do PDF que mandei. Quero TODAS essas opções dentro do programa, para ter bastante escolha.

O livreto o programa monta automático, como o embaralhador antigo (o primeiro que fizemos) já fazia: pegava tudo, punha no tamanho livreto e embaralhava sozinho. Quero isso dentro do programa.

Controles de escala na impressão:
- aumentar ou diminuir a escala das páginas no formato livreto (igual à escala personalizada que aparece nos prints);
- poder diminuir só o lado esquerdo, só o lado direito, ou as duas páginas juntas.

Margens (só nesta fase, por causa da encadernação clássica):
- Contadas na página A5, não na folha A4 inteira.
- Mínimo de 1 cm em cada um dos quatro lados (cima, baixo e os dois lados).
- O lado de dentro (costura) também é 1 cm: página par → direita, página ímpar → esquerda.
- A impressora ainda come mais uns 3 mm na borda.

Aviso: o programa precisa avisar quando o corte deixar qualquer margem abaixo de 1 cm, porque o livro vai ser encadernado (encadernação clássica) e tem que sobrar espaço nos quatro lados.

(Anexei os prints do PDF com as opções de impressão e as 5 fotos da janela de impressão de 13/10.)

---

## O que aparece nas cinco fotos (leitura da gerente)

- **Tamanho do papel:** A4 (210 x 297 mm), Carta 216 x 279 mm, Ofício 9 (215 x 315 mm), 8,5 x 13 pol. (216 x 330 mm), México-Ofício (216 x 341 mm), Ofício 216 x 356 mm, Executivo 184 x 267 mm, Envelope #10 (105 x 241 mm), 8 x 10 pol. (203 x 254 mm), 5 x 7 pol. (127 x 178 mm), e a lista continua.
- **Orientação:** Retrato / Paisagem. Caixas "Rotação Automática" e "Centralizar Automático".
- **Cópias** e "Agrupar"; "Imprimir em escala de cinza (preto e branco)"; "Imprimir como imagem"; "Reverter páginas".
- **Intervalo de páginas** (de / até) e "Todas as páginas".
- **Quatro abas:** Tamanho · Pôster · Múltiplo · Livreto.
  - **Tamanho:** Ajustar · Tamanho real · Escala personalizada (%) · Reduzir páginas muito grandes. Nas fotos: 75% e 83% num livreto de 250 páginas em A4 paisagem; 70% de valor guardado; "Ajustar" dá 69% em paisagem e 97% em retrato para a capa do Balzac.
  - **Livreto:** Ordem de páginas "Frente e verso"; "Folhas de" 1 – 244; Encadernação "Esquerda".
- Prévia com "Redimensionar: N%" e navegação de página.
