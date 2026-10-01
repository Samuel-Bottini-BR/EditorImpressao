# Quinta conferência do Samuel (01/10/2026)

Pedido: "faz um novo relatório com mais fotos por favor, tem uns que estão faltando foto, para
que eu possa responder, deixe todas as questões bem explicadas e com fotos para eu responder".

Formulário: `relatorios/conferir-aqui-5.html` (marcações no navegador com a chave
`conferir-2026-10-01-e`, separadas da conferência 4). Feito pelo implementador; o programa
**não mudou** e **nenhuma página foi processada**. As imagens saem só de imagens prontas:

- a rodada `relatorios/conferir/pb-mp-decoracao-2026-10-01/` (antes-pb, depois-pb, antes-mp,
  depois-mp) e as páginas originais do gabarito;
- o verificador dessa rodada (`verificador/imagens/ampliados/a5` e `a6`, rodadas dele pelo
  caminho do programa; `verificador/reproducoes/prints/p05`, print da janela) e as medidas do
  parecer dele (peso do PDF e tempos);
- o print da tela "O que fazer" da conferência 4 (Qt offscreen), copiado para `tela/`.

## Cartões

Todos os 17 da conferência 4 (F1, F2, V1–V3, M1–M3, I1, I2, G1, MP1–MP4, T1, P2), com as mesmas
imagens (refeitas pelo mesmo código; iguais às da 4), mais:

| Código | O quê | Imagem | De onde vem |
|---|---|---|---|
| P1 | A iluminura mantém a cor no Preto e branco? Horas 11 e 47: ORIGINAL · MANTÉM A COR · EM PRETO E BRANCO | `cartoes/q1-horas011-…`, `q1-horas047-…` | MANTÉM A COR = depois-pb; EM PRETO E BRANCO = antes-pb (o traço de antes; conferido contra a imagem do verificador com a caixinha marcada, a6: diferença média 21 de 255, contra 65 da versão em cor) |
| P3 | PDF pesado: Horas 11 e 13, cor × traço, com o tamanho em cima | `cartoes/q2-pdf-pesado.jpg` | Horas 11 cor e traço: a6 do verificador; Horas 13 cor: depois-pb; Horas 13 traço: a6. Tamanhos e tempos: parecer do verificador |
| P4 | Títulos dentro da decoração: pretos ou na cor? Horas 11 (oval) e Horas 26 ("NOVEMBRE.") | `cartoes/q3-…` | FICAM NA COR = depois-pb; SAEM PRETOS = antes-pb |
| A1 | Horas 47, "JESUS" e "C" dourados quase somem (PB) | `cartoes/a1-…` | rodada (o mesmo achado do a8 do verificador) |
| A2 | Horas 11, miolo das letras douradas creme | `cartoes/a2-…` | rodada (a2 do verificador) |
| A3 | Opus 20 no PB: "livre" × "Este livro tem fotos" | `cartoes/a3-…` | livre = depois-pb; tem fotos = a5 do verificador (terceira parte), ampliada ao tamanho do resultado |
| A4 | Horas 13, retângulo na barra de baixo da moldura | `cartoes/a4-…` | rodada (a1 do verificador) |
| A5 | Horas 27, buraco na barra de cima da moldura | `cartoes/a5-…` | rodada (a3 do verificador) |
| X1 | Opus 256, números fracos da última coluna (com setas numa faixa ao lado) | `cartoes/x1-…` | rodada (depois-pb, depois-mp) |
| X2 | Graduale 221, letras raspadas entre "ſu" e "mus" | `cartoes/x2-…` | rodada (depois-pb, depois-mp) |
| X3 | Aviso falso "o preto e branco vai perder a ilustração" | `cartoes/x3-aviso-falso.jpg` | p05 do verificador |

## Imagens que não existiam prontas

- **Horas 11 e 47 no Preto e branco com a caixinha marcada**, no tamanho da rodada: não há.
  Para a P1 usei o ANTES do Preto e branco (o traço de antes de 01/10). O verificador tem a
  Horas 11 com a caixinha marcada (a6), mas pequena, sem a Horas 47; ela entrou na P3.
- **Opus 20 no Preto e branco com "Este livro tem fotos"** em resolução cheia: só a imagem a5 do
  verificador (1000 pontos de altura); por isso o detalhe fica um pouco menos nítido. Avisado no
  cartão A3.
- **Horas 13 com a caixinha marcada** em resolução cheia: só a a6 do verificador (usada na P3).

## Como as imagens são desenhadas

Igual à conferência 4: ORIGINAL redesenhado no enquadramento do resultado (ORB + ECC);
retângulos com folga, por fora do lugar ampliado; detalhes sem nada por cima; rótulos em faixas
acima de cada parte. No X1 as setas ficam numa faixa branca ao lado de cada detalhe; no X3 os
retângulos ficam com folga em volta do aviso e do cartão (no print da tela).

## Arquivos

- `scripts/montar_imagens.py`: todas as imagens (usa o script da conferência 4 para os cartões
  repetidos e as peças de desenho, com a saída trocada para esta pasta).
- `cartoes/`, `tela/`, `corte/`: imagens (fora do git; refazer com o script).
