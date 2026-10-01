# Quarta conferência do Samuel (01/10/2026)

Formulário: `relatorios/conferir-aqui-4.html` (as marcações ficam no navegador com a chave
`conferir-2026-10-01-d`). Feito pelo implementador; o programa **não mudou** e **nenhuma página
foi processada**: as imagens saem só de imagens prontas da rodada
`relatorios/conferir/pb-mp-decoracao-2026-10-01/` (antes-pb, depois-pb, antes-mp, depois-mp),
das páginas originais do gabarito (`gabarito/paginas/*.png`) e da medida do corte
`relatorios/corte-crista-2026-10-01/medida-corte-2026-10-01.json`.

## Cartões

| Código | O quê | Imagem |
|---|---|---|
| F1, F2 | Preto e branco, foto em tons de cinza: Opus Majus 20 (estátua), Escola 35 (anjo) | `cartoes/pb1`, `pb2` |
| V1, V2, V3 | Preto e branco, vermelho sai preto: Horas 13 (títulos), Horas 27 (letras "A" douradas), Graduale 223 (palavras vermelhas) | `cartoes/pb3`, `pb4`, `pb5` |
| M1, M2, M3 | Preto e branco, moldura com a cor original: Horas 13, 26, 27 | `cartoes/pb6`, `pb7`, `pb8` |
| I1, I2 | Preto e branco, iluminura com a cor original: Horas 11, 47 | `cartoes/pb9`, `pb10` |
| G1 | Graduale 222: pauta e notas iguais (ANTES e AGORA idênticos ponto por ponto) | `cartoes/pb11` |
| MP1, MP2 | Mágico pro, moldura dourada sem escurecer: Horas 13, 26 | `cartoes/mp1`, `mp2` |
| MP3 | Mágico pro, Horas 47: a faixa cinza embaixo de "pitié de nous" (com uma linha de contraste aumentado, só para enxergar) | `cartoes/mp3` |
| MP4 | Mágico pro, Horas 11: a cena azul de baixo e a margem | `cartoes/mp4` |
| T1 | A tela "O que fazer" com a caixinha nova (print sem janela, Qt offscreen) | `tela/tela-caixinha.jpg` |
| P1 | Pergunta: a iluminura também mantém a cor no Preto e branco? | — |
| P2 | Pergunta: corte com 0,6 mm ou 1 mm depois da última letra (Escola 7, "CRISTÃ") | `corte/corte-crista.jpg` |
| X1, X2 | O que não deu (botão "Entendi"): Opus 256, Graduale 221 (dependem do 6.1) | — |

## Como as imagens são desenhadas

- ORIGINAL, ANTES e AGORA no mesmo recorte: ANTES e AGORA saem do mesmo programa com o mesmo
  corte (mesmo tamanho nas quatro pastas); o ORIGINAL é redesenhado no enquadramento do resultado
  pelos pontos em comum (ORB + ECC, `scripts/alinhar.py`).
- **O retângulo de destaque fica com folga, por fora do lugar ampliado** (a página inteira ganha
  uma margem branca para ele caber), e **os detalhes ampliados não têm nada desenhado por cima**;
  nenhum texto é escrito em cima das imagens (rótulos em faixas acima de cada parte). No corte da
  Escola 7, nem o retângulo: um triângulo na faixa branca de cima aponta o canto, e a régua fica
  numa faixa branca embaixo. Motivo: na conferência 2 o retângulo desenhado por cima escondeu a
  perna do "A" de "CRISTÃ".
- Corte da Escola 7: a página original ampliada para 300 DPI (o tamanho que o programa usa no
  corte) e a borda direita da medida de 01/10 (x = 2012). Última tinta do título medida aqui:
  x = 2004, folga 7 pontos = 0,59 mm. Com 1 mm a borda iria para x = 2017.

## Achados ao montar (para a gerente)

- **Horas 11 no Preto e branco:** as letras do título no oval ("HEURES DE LOUIS LE GRAND...")
  ficam vermelhas e azuis, porque estão dentro da zona da iluminura; pela regra do vermelho
  sairiam pretas. Avisado no cartão I1.
- **Horas 47 no Preto e branco:** o "JESUS" dourado sai com o "E" partido, ANTES e AGORA (ouro
  claro demais). Avisado no cartão I2.
- **Opus Majus 20 no Preto e branco (forma "livre", de fábrica):** só a parte de baixo da estátua
  sai em tons de cinza; cabeça, ombro e a faixa à direita continuam brancos chapados, ANTES e
  AGORA (o "degrau no alto da foto"). Avisado no cartão F1.
- **Horas 13 no Preto e branco:** o quadradinho preto na faixa de baixo da moldura, perto de
  "pag. 54", continua (já na Lista de bugs). Avisado no cartão M1.
- **Horas 11 no Mágico pro:** tracinhos escuros na margem branca da esquerda (resto da beirada da
  folha), ANTES e AGORA. Avisado no cartão MP4.
- **Escola 7, corte com 1 mm:** entraria também um pontinho de sujeira ao lado do "Ã". Avisado no
  cartão P2.

## Arquivos

- `scripts/alinhar.py`: o original no enquadramento do resultado.
- `scripts/montar_imagens.py`: todas as imagens dos cartões, a da tela e a do corte.
- `scripts/print_tela.py`: o print da tela "O que fazer" sem janela visível (rodar antes do
  `montar_imagens.py`).
- `cartoes/`, `tela/`, `corte/`: imagens (fora do git; refazer com os scripts).
