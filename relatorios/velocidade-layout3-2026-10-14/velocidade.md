# Velocidade do layout juntado no PC do Samuel, 14/10/2026

Gerente. Conferido por **máquina** (teste de velocidade). Só medi. O layout já foi aprovado pelo Samuel em 13/10; esta medição é a regra 6 do plano (nenhum item pode deixar o programa mais lento) antes de juntar ao `fase-1`.

## A resposta em uma frase

**Ficou igual: o layout novo não deixou o programa mais lento.** Abrir o livro, trocar de página e processar em Preto e branco ficaram dentro do vai-e-vem normal entre rodadas iguais. Processar em Mágico pro saiu um pouco **mais rápido** com o layout (os três pares para o mesmo lado).

- **Abrir o livro de 300 folhas:** 55,2 s antes, 55,6 s depois (+0,4 s no livro inteiro). Rodadas iguais do antes variaram 7,1 s entre si. Os pares apontam para lados diferentes (+4,7; -1,6; -1,9 s): igual.
- **Trocar de página:** 2,36 s antes, 2,31 s depois (-0,05 s). Igual.
- **Processar em Mágico pro, 10 páginas:** 57,0 s antes, 55,2 s depois (-1,7 s, -3,0%). Os três pares foram para o mesmo lado (-1,7; -1,8; -1,6 s), mas a diferença é do tamanho do vai-e-vem (2,1 s e 1,9 s). Leitura: no mínimo, não piorou.
- **Processar em Preto e branco, 10 páginas:** 26,0 s antes, 26,4 s depois (+0,4 s). Pares para lados diferentes (+1,3; -1,3; +1,2 s): igual.
- **Memória máxima:** 1.375 a 1.406 MB antes, 1.261 a 1.379 MB depois. Igual.
- **O PDF de saída** em Mágico pro saiu com 70,7 MB nas seis rodadas: o processamento da imagem é o mesmo (o layout só mexe nas telas).

## O que foi comparado

| | Antes | Depois |
|---|---|---|
| Programa | o de hoje, `fase-1` (código igual ao `1d37f8f`) | o layout juntado, `juntar-layout3-2026-10-13` (`f35bcaf`) |
| Pasta | `.claude\worktrees\velocidade-antes` | `.claude\worktrees\juntar-layout3` |

- O código do `fase-1` de 14/10 é o mesmo do `1d37f8f`: de lá para cá só mudaram documentos.
- O `teste_velocidade.py` é idêntico nos dois ramos.
- Mesmo livro (`gabarito\velocidade\marial_300.pdf` da pasta principal, só lido), mesmo Python (`.venv` da pasta principal), detector carregado e notebook na tomada em todas.
- Cada rodada repete tudo 3 vezes: abrir o livro, 20 trocas de página, processar as páginas 146 a 155 em Mágico pro e em Preto e branco.
- Ordem alternada, uma de cada vez, depois de um aquecimento curto em cada cópia: antes, depois, antes, depois, antes, depois. Cada uma levou de 11 a 12,5 minutos.
- Scripts: `rodar_uma.ps1`, `rodar_todas.ps1` e `juntar.py` nesta pasta (adaptados dos da medição do G6, de 12/10).

## Ressalvas

- **A exigência de memória livre baixou de 3 GB para 2,5 GB** antes de começar: o PC tinha 2,6 GB livres mesmo depois de fechar o CapCut e desligar o Ubuntu do WSL. O teste usa no máximo 1,4 GB. Na prática, todas as rodadas começaram com 3,8 a 4,4 GB livres.
- Na rodada `depois-1` o processador estava em 20% antes de começar (nas outras, de 5 a 10%). Os números dela não destoam das outras rodadas do depois.
- Enquanto as rodadas corriam, a gerente fez trabalho leve (escrever no plano e nas páginas do claude.ai). Nenhum outro agente nem teste rodou.
- O Mágico pro mais rápido não tem causa conhecida (o layout não mexe no filtro). Não vale como ganho; vale como "não piorou".

## Todas as rodadas e cada repetição

As tabelas completas estão em `juntar-saida.md`, nesta mesma pasta.


## Todas as rodadas (mediana das 3 repeticoes de cada execucao)

| Rodada | Hora | Mem. livre antes | Processador antes | Abrir o livro | Troca (media) | Troca (pior) | Magico pro, 10 pag. | Preto e branco, 10 pag. | Memoria maxima | Durou |
|---|---|---|---|---|---|---|---|---|---|---|
| antes-1 | 13:25 | 3,82 GB | 6% | 51,2 s | 2,21 s | 3,39 s | 57,5 s | 25,5 s | 1375 MB | 11,3 min |
| depois-1 | 13:37 | 4,19 GB | 20% | 55,9 s | 2,30 s | 3,53 s | 55,8 s | 26,8 s | 1261 MB | 12,4 min |
| antes-2 | 13:49 | 4,18 GB | 7% | 56,1 s | 2,44 s | 3,71 s | 57,7 s | 27,0 s | 1374 MB | 12,3 min |
| depois-2 | 14:02 | 4,09 GB | 5% | 54,5 s | 2,33 s | 3,39 s | 55,9 s | 25,7 s | 1379 MB | 11,8 min |
| antes-3 | 14:14 | 4,35 GB | 10% | 58,3 s | 2,41 s | 3,55 s | 55,7 s | 25,6 s | 1406 MB | 12,1 min |
| depois-3 | 14:26 | 3,91 GB | 10% | 56,4 s | 2,29 s | 3,63 s | 54,0 s | 26,8 s | 1376 MB | 12,0 min |

## Cada repeticao (3 por execucao)

| Rodada | Medida | 1a | 2a | 3a |
|---|---|---|---|---|
| antes-1 | Abrir o livro (300 folhas) | 49,7 s | 51,2 s | 53,9 s |
| antes-1 | Trocar de pagina (media de 20) | 2,61 s | 2,19 s | 2,21 s |
| antes-1 | Trocar de pagina (a pior das 20) | 3,39 s | 2,90 s | 4,37 s |
| antes-1 | Processar 10 paginas em Magico pro | 57,5 s | 48,1 s | 59,2 s |
| antes-1 | Processar 10 paginas em Preto e branco | 25,6 s | 22,1 s | 25,5 s |
| depois-1 | Abrir o livro (300 folhas) | 55,1 s | 56,5 s | 55,9 s |
| depois-1 | Trocar de pagina (media de 20) | 2,97 s | 2,30 s | 2,29 s |
| depois-1 | Trocar de pagina (a pior das 20) | 3,88 s | 3,42 s | 3,53 s |
| depois-1 | Processar 10 paginas em Magico pro | 70,9 s | 55,1 s | 55,8 s |
| depois-1 | Processar 10 paginas em Preto e branco | 27,4 s | 26,8 s | 26,4 s |
| antes-2 | Abrir o livro (300 folhas) | 53,7 s | 56,1 s | 58,7 s |
| antes-2 | Trocar de pagina (media de 20) | 2,79 s | 2,38 s | 2,44 s |
| antes-2 | Trocar de pagina (a pior das 20) | 3,71 s | 3,31 s | 3,80 s |
| antes-2 | Processar 10 paginas em Magico pro | 60,2 s | 57,7 s | 54,4 s |
| antes-2 | Processar 10 paginas em Preto e branco | 26,7 s | 27,0 s | 29,0 s |
| depois-2 | Abrir o livro (300 folhas) | 53,8 s | 55,3 s | 54,5 s |
| depois-2 | Trocar de pagina (media de 20) | 2,82 s | 2,33 s | 2,28 s |
| depois-2 | Trocar de pagina (a pior das 20) | 3,51 s | 3,39 s | 3,38 s |
| depois-2 | Processar 10 paginas em Magico pro | 56,1 s | 54,9 s | 55,9 s |
| depois-2 | Processar 10 paginas em Preto e branco | 25,7 s | 25,5 s | 26,7 s |
| antes-3 | Abrir o livro (300 folhas) | 58,2 s | 58,9 s | 58,3 s |
| antes-3 | Trocar de pagina (media de 20) | 2,79 s | 2,34 s | 2,41 s |
| antes-3 | Trocar de pagina (a pior das 20) | 3,90 s | 3,29 s | 3,55 s |
| antes-3 | Processar 10 paginas em Magico pro | 59,3 s | 55,7 s | 53,9 s |
| antes-3 | Processar 10 paginas em Preto e branco | 26,2 s | 25,6 s | 25,0 s |
| depois-3 | Abrir o livro (300 folhas) | 56,4 s | 56,6 s | 51,7 s |
| depois-3 | Trocar de pagina (media de 20) | 2,88 s | 2,17 s | 2,29 s |
| depois-3 | Trocar de pagina (a pior das 20) | 3,63 s | 3,18 s | 3,73 s |
| depois-3 | Processar 10 paginas em Magico pro | 66,5 s | 50,7 s | 54,0 s |
| depois-3 | Processar 10 paginas em Preto e branco | 27,3 s | 24,4 s | 26,8 s |

## Antes contra depois

| Medida | Antes (media das medianas) | Depois (media das medianas) | Diferenca | Em % | Por unidade | Vai-e-vem do antes | Vai-e-vem do depois | Pares (depois - antes) | Todas as 9: antes | Todas as 9: depois |
|---|---|---|---|---|---|---|---|---|---|---|
| Abrir o livro (300 folhas) | 55,2 s | 55,6 s | +0,4 s | +0,7% | +1 ms por folha | 51,2 a 58,3 s (abre 7,1 s) | 54,5 a 56,4 s (abre 1,9 s) | +4,7; -1,6; -1,9 s | mediana 56,1 s, de 49,7 a 58,9 s | mediana 55,3 s, de 51,7 a 56,6 s |
| Trocar de pagina (media de 20) | 2,36 s | 2,31 s | -0,05 s | -2,2% | - | 2,21 a 2,44 s (abre 0,23 s) | 2,29 a 2,33 s (abre 0,04 s) | +0,08; -0,11; -0,13 s | mediana 2,41 s, de 2,19 a 2,79 s | mediana 2,30 s, de 2,17 a 2,97 s |
| Trocar de pagina (a pior das 20) | 3,55 s | 3,52 s | -0,03 s | -0,9% | - | 3,39 a 3,71 s (abre 0,31 s) | 3,39 a 3,63 s (abre 0,24 s) | +0,13; -0,32; +0,09 s | mediana 3,55 s, de 2,90 a 4,37 s | mediana 3,51 s, de 3,18 a 3,88 s |
| Processar 10 paginas em Magico pro | 57,0 s | 55,2 s | -1,7 s | -3,0% | -173 ms por pagina | 55,7 a 57,7 s (abre 2,1 s) | 54,0 a 55,9 s (abre 1,9 s) | -1,7; -1,8; -1,6 s | mediana 57,5 s, de 48,1 a 60,2 s | mediana 55,8 s, de 50,7 a 70,9 s |
| Processar 10 paginas em Preto e branco | 26,0 s | 26,4 s | +0,4 s | +1,5% | +39 ms por pagina | 25,5 a 27,0 s (abre 1,5 s) | 25,7 a 26,8 s (abre 1,1 s) | +1,3; -1,3; +1,2 s | mediana 25,6 s, de 22,1 a 29,0 s | mediana 26,7 s, de 24,4 a 27,4 s |

## Conferencias

- antes-1: commit 1d37f8f, saida 0, livro marial_300.pdf (300 folhas, 300 paginas), detector carregado, energia: na tomada (bateria em 100%), mem. livre depois 4,20 GB, trocas 20, processadas 146 a 155, PDF Magico pro 70,7 MB
- depois-1: commit f35bcaf, saida 0, livro marial_300.pdf (300 folhas, 300 paginas), detector carregado, energia: na tomada (bateria em 100%), mem. livre depois 4,20 GB, trocas 20, processadas 146 a 155, PDF Magico pro 70,7 MB
- antes-2: commit 1d37f8f, saida 0, livro marial_300.pdf (300 folhas, 300 paginas), detector carregado, energia: na tomada (bateria em 100%), mem. livre depois 4,09 GB, trocas 20, processadas 146 a 155, PDF Magico pro 70,7 MB
- depois-2: commit f35bcaf, saida 0, livro marial_300.pdf (300 folhas, 300 paginas), detector carregado, energia: na tomada (bateria em 100%), mem. livre depois 4,35 GB, trocas 20, processadas 146 a 155, PDF Magico pro 70,7 MB
- antes-3: commit 1d37f8f, saida 0, livro marial_300.pdf (300 folhas, 300 paginas), detector carregado, energia: na tomada (bateria em 100%), mem. livre depois 3,91 GB, trocas 20, processadas 146 a 155, PDF Magico pro 70,7 MB
- depois-3: commit f35bcaf, saida 0, livro marial_300.pdf (300 folhas, 300 paginas), detector carregado, energia: na tomada (bateria em 100%), mem. livre depois 5,34 GB, trocas 20, processadas 146 a 155, PDF Magico pro 70,7 MB
