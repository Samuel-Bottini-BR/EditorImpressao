# Item 1.3: qual OCR acha melhor onde está o texto

**28/09/2026 · implementador · só medição: o programa não mudou.**

> **Atenção, Samuel:**
> 1. As zonas que dizem "aqui é texto" e "aqui não pode ter linha" foram desenhadas por mim, olhando cada página. **Você ainda precisa conferir essas zonas** (seção 9, 22 imagens). Até lá, todos os números deste relatório são provisórios.
> 2. A escolha dos 2 OCRs que ficam é sua. Abaixo está a minha recomendação, não uma decisão.

## 1. Em poucas palavras

1. **Nenhum OCR sozinho cumpre as duas metas em todas as páginas.** As metas são: achar 98% ou mais da tinta das letras, e cobrir 1% ou menos da tinta de gravura, iluminura, moldura e foto.
2. **O Kraken é o único que não pisa em figura em nenhuma das 7 páginas obrigatórias.** A pior delas ficou em 0,9%. Também é o melhor no manuscrito: no Graduale não pôs nenhuma caixa em cima da música. Tem três defeitos:
   - toma a moldura ornamental do Siebmacher 9 como se fosse texto (83%);
   - perde a tabela do Opus 256 (só 33% achado);
   - é lento: 12 s por página neste PC.
3. **O docTR (modelo `fast_base`, pelo OnnxTR) é o melhor dos rápidos:**
   - acha em média 98,7% da tinta de texto;
   - leva 1 s por página e roda no Python 3.14 do programa;
   - é o único, fora as linhas do Internet Archive, que não toma a moldura do Siebmacher (0,04%);
   - falha em duas obrigatórias: na Horas 13 as caixas encostam na moldura dourada, e no Palatino 5 duas caixinhas caem na borda do retrato (1,7%).
4. **O Tesseract não serve para isto, ao contrário do que a pesquisa apostava:**
   - não acha nenhuma linha no título da Horas 11 e quase nada no Graduale;
   - toma a moldura do Siebmacher inteira como texto (99%);
   - pisa na borda do retrato e nas molduras do Palatino (4% a 6%);
   - o filtro de confiança do Internet Archive quase não muda nada.
5. **Recomendação, para você decidir: Kraken + docTR `fast_base`.** Os dois erram em lugares diferentes. Nas zonas onde os dois concordam, **nenhuma das 22 páginas passou de 1% de figura**. O custo é o Kraken: 1,2 GB a mais no instalador (um Python só dele, sem WSL) e uns 20 a 30 s por página no notebook do Kaique (estimativa). **Alternativa mais leve:** docTR `fast_base` + PP-OCRv6 pequeno (pelo RapidOCR). Os dois são rápidos e rodam no Python do programa, mas erram parecido: os dois pisam no emblema do Opus 3 e na moldura da Horas 13.

## 2. Como foi medido

- **Páginas:** as 19 da pesquisa, que são as 16 do item `fase1` da `gabarito/lista.json` mais Rhetorica 18, Siebmacher 9 e Palatino 57. Para ver o manuscrito, entraram mais **Graduale 221, 222 e 223**. As Horas 11, 13, 26, 27 e 47 já estavam entre as 19.
- **Imagem:** o PDF de uma página de `gabarito/paginas/`, desenhado na resolução do scan, com teto de 300 DPI. As Horas e o Graduale têm scan pequeno (1024 e 961 px de largura) e ficaram assim. **Não passei pelo corte nem pelo endireitamento do programa** (ver Ressalvas). Todos os OCRs receberam a mesma imagem.
- **Gabarito:** para cada página, retângulos "tem de ser texto" e "não pode ter linha" (gravura, iluminura, moldura, foto, carimbo). Há também zonas "neutras", que não contam para nada: filete colado no texto, capitular grande do Graduale, letrinhas dentro dos diagramas do Opus 165. O arquivo é `gabarito/ocr-zonas.json`, marcado "a conferir pelo Samuel".
- **Tinta:** separei a tinta do papel como o Internet Archive faz (método Sauvola, janela de 1/4 do DPI, k 0,34). Na tabela do Opus 256, as linhas retas da grade não contam como texto: só os números e as letras.
- **Caixas:** cada caixa de linha foi alargada em 15% da altura da linha, para pegar as hastes das letras, como manda a pesquisa.
- **As duas medidas pedidas:**
  - **texto achado:** quanto da tinta das zonas de texto cai dentro de alguma caixa (meta: 98% ou mais);
  - **figura tomada por texto:** quanto da tinta das zonas "não pode ter linha" cai dentro de alguma caixa (meta: 1% ou menos; numa página obrigatória, passar disso reprova).
- **Três medidas a mais, para não julgar só por um número:**
  - **área da figura coberta:** a faixa dourada e a pintura lisa quase não viram "tinta", mas uma caixa em cima delas estraga do mesmo jeito;
  - **figura tomada sem o alargamento de 15%:** separa "a caixa encosta na moldura" de "a caixa cobre a figura";
  - **linhas falsas:** caixas que quase não tocam texto nenhum.
- **Tempo:** mediana de 3 rodadas por página, neste PC (Ryzen 7 5800H, 8 núcleos e 16 linhas de execução). Cada OCR rodou sozinho, com o número de linhas de execução que ele usa por padrão. O tempo não inclui carregar o modelo, com uma exceção: o Tesseract abre um programa novo a cada página, então o tempo dele já inclui a carga.
- **Olhei as 22 folhas de contato**, com as caixas de todos os OCRs lado a lado (seção 8).

### Os OCRs e configurações medidos

| Código | O que é | Onde rodou |
|---|---|---|
| R0 | Linhas do texto invisível que o Internet Archive já pôs no PDF (só Palatino, Opus Majus, Rhetorica e Siebmacher) | leitura do PDF |
| T1 | Tesseract 5.4.0 (o que o `winget` instalou), `--psm 3`, modelo `tessdata_best` do idioma do livro: `ita`, `por`, `fra`, `eng` (o Opus Majus é tradução inglesa), `lat` e `script/Fraktur` | Windows |
| T2 | T1 com o filtro do Internet Archive: jogar fora a linha com confiança média abaixo de 20 | Windows |
| T3a | Tesseract com o modelo `frak2021` da UB Mannheim (CC0), mais o filtro | Windows |
| T3b | Tesseract com o modelo `GT4HistOCR` da UB Mannheim, mais o filtro | Windows |
| D1 | docTR pelo OnnxTR 0.9.0, só detecção, `db_resnet50`; palavras juntadas em linhas pelo próprio docTR | Windows, Python 3.14 |
| D2 | docTR pelo OnnxTR, só detecção, `fast_base` | Windows, Python 3.14 |
| P1 | PP-OCRv5 servidor pelo RapidOCR 3.9.2, só detecção; página inteira até 3000 px | Windows, Python 3.14 |
| P2 | PP-OCRv5 móvel pelo RapidOCR, idem | Windows, Python 3.14 |
| P3 | PP-OCRv6 pequeno pelo RapidOCR (extra: é o padrão do RapidOCR 3.9.2, não estava na pesquisa) | Windows, Python 3.14 |
| K1 | Kraken 7.1.1, segmentador de linhas de base `blla` (o modelo que vem no pacote), no processador | WSL (Ubuntu), Python 3.13; e **também no Windows**, em 6 páginas (ver seção 6) |

## 3. Resultado resumido (19 páginas)

As colunas "figura" olham só as 7 páginas obrigatórias: Palatino 5, Escola 35, Horas 11, 13, 26 e 27, e Opus 20.

| OCR | Texto achado (média) | Páginas com 98% ou mais | Pior página | Figura tomada, pior obrigatória | Obrigatórias acima de 1% | Área de figura coberta, pior obrigatória | Itens pequenos perdidos | Tempo por página |
|---|---|---|---|---|---|---|---|---|
| R0 | 93,0% | 9 de 12 | Opus 256 (30,4%) | 1,06% | Pal 5 | 1,4% | 4 de 20 | 0 |
| T1 | 93,8% | 15 de 19 | Hor 11 (0,0%) | 5,03% | Pal 5, Hor 13 | 4,7% | 6 de 27 | 2,4 s |
| T2 | 92,2% | 14 de 19 | Hor 11 (0,0%) | 5,03% | Pal 5, Hor 13 | 4,7% | 6 de 27 | 2,4 s |
| T3a | 90,1% | 12 de 19 | Hor 11 (0,0%) | 3,89% | Pal 5, Hor 13 | 4,1% | 6 de 27 | 2,1 s |
| T3b | 82,1% | 6 de 19 | Hor 11 (0,0%) | 4,65% | Pal 5, Hor 13 | 4,0% | 13 de 27 | 1,9 s |
| D1 | 97,4% | 15 de 19 | Opus 256 (62,7%) | 12,51% | Pal 5, Hor 13, Hor 27 | 10,4% | 0 de 27 | 1,1 s |
| D2 | 98,7% | 16 de 19 | Opus 256 (86,9%) | 8,24% | Pal 5, Hor 13 | 5,2% | 1 de 27 | 1,0 s |
| P1 | 99,2% | 16 de 19 | Pal 57 (94,7%) | 48,12% | Pal 5, Hor 13, Esc 35 | 52,8% | 2 de 27 | 6,7 s |
| P2 | 99,1% | 15 de 19 | Opus 256 (96,0%) | 12,50% | Pal 5, Hor 13 | 10,1% | 1 de 27 | 1,2 s |
| P3 | 98,7% | 16 de 19 | Pal 57 (88,1%) | 9,26% | Hor 13 | 7,2% | 3 de 27 | 1,0 s |
| K1 | 95,5% | 14 de 19 | Opus 256 (33,2%) | 0,90% | nenhuma | 2,5% | 1 de 27 | 12,3 s |

## 4. Tabela OCR × página

### 4.1 Texto achado (%; em negrito, abaixo de 98%)

| OCR | Pal 5 | Pal 7 | Pal 9 | Pal 10 | Pal 57 | Esc 7 | Esc 35 | Hor 11 | Hor 13 | Hor 26 |
|---|---|---|---|---|---|---|---|---|---|---|
| R0 | 99,8 | 99,2 | 99,4 | 99,9 | **93,4** |  |  |  |  |  |
| T1 | 100,0 | 98,1 | 100,0 | 100,0 | **92,6** | 100,0 | 100,0 | **0,0** | 100,0 | 100,0 |
| T2 | 100,0 | 98,1 | 100,0 | 100,0 | **69,2** | 100,0 | 100,0 | **0,0** | 100,0 | 100,0 |
| T3a | 100,0 | 98,1 | 100,0 | 100,0 | **58,4** | 100,0 | 100,0 | **0,0** | **95,7** | **93,7** |
| T3b | **75,4** | 98,0 | **96,7** | **95,5** | **46,7** | **89,0** | 100,0 | **0,0** | **85,3** | **77,9** |
| D1 | 100,0 | 99,9 | 100,0 | 100,0 | **97,2** | 99,8 | 99,8 | 100,0 | 100,0 | **97,0** |
| D2 | 100,0 | 99,9 | 100,0 | 100,0 | **96,7** | 99,8 | 99,8 | 100,0 | 99,5 | 98,5 |
| P1 | 100,0 | 99,6 | 100,0 | 100,0 | **94,7** | 99,7 | 100,0 | 100,0 | 100,0 | 100,0 |
| P2 | 100,0 | 99,9 | 100,0 | 100,0 | **96,9** | 99,8 | 100,0 | 99,6 | 99,8 | **97,6** |
| P3 | 100,0 | 99,9 | 100,0 | 100,0 | **88,1** | 99,7 | 99,9 | 100,0 | 100,0 | 100,0 |
| K1 | 100,0 | 99,8 | 100,0 | 100,0 | **96,1** | 99,7 | 100,0 | **96,9** | **96,3** | 98,5 |

| OCR | Hor 27 | Hor 47 | Opus 3 | Opus 11 | Opus 20 | Opus 165 | Opus 256 | Rhet 18 | Sieb 9 |
|---|---|---|---|---|---|---|---|---|---|
| R0 |  |  | 100,0 | 98,9 | 100,0 | 99,8 | **30,4** | 99,7 | **95,3** |
| T1 | **96,4** | 99,3 | 99,0 | 100,0 | 100,0 | 100,0 | **97,4** | 99,7 | 100,0 |
| T2 | **93,2** | 99,3 | 99,0 | 100,0 | 100,0 | 100,0 | **96,3** | **97,1** | 100,0 |
| T3a | **93,2** | 99,3 | **97,4** | 100,0 | 100,0 | 100,0 | **76,5** | 99,0 | 100,0 |
| T3b | **74,3** | 98,9 | **53,8** | **98,0** | 100,0 | 98,7 | **75,3** | **97,1** | 99,5 |
| D1 | 99,4 | 100,0 | 100,0 | 98,7 | 100,0 | 100,0 | **62,7** | 100,0 | **96,1** |
| D2 | 99,6 | 100,0 | 100,0 | 98,5 | 100,0 | 100,0 | **86,9** | 99,9 | **95,7** |
| P1 | 99,9 | 100,0 | 100,0 | 98,8 | 100,0 | 100,0 | **96,6** | 100,0 | **95,7** |
| P2 | 98,7 | 100,0 | 100,0 | 98,7 | 100,0 | 100,0 | **96,0** | 100,0 | **96,7** |
| P3 | 98,2 | 100,0 | 100,0 | 98,7 | 100,0 | 100,0 | **95,6** | 99,9 | **95,5** |
| K1 | 98,7 | 100,0 | **98,0** | 99,3 | 100,0 | 100,0 | **33,2** | 100,0 | 98,1 |

### 4.2 Figura tomada por texto (% da tinta da figura; em negrito, acima de 1%)

Só as páginas que têm figura. "Pal 57" conta a moldura e os laços em volta do título; "Opus 3" conta o emblema da editora e o carimbo; "Opus 165" conta os dois diagramas de traço fino.

| OCR | Pal 5 | Pal 9 | Pal 10 | Pal 57 | Esc 7 | Esc 35 | Hor 11 | Hor 13 |
|---|---|---|---|---|---|---|---|---|
| R0 | **1,06** | **6,79** | **5,87** | **17,85** |  |  |  |  |
| T1 | **5,03** | **4,76** | **6,10** | **22,64** | 0,24 | 0,00 | 0,00 | **1,53** |
| T2 | **5,03** | **4,76** | **6,10** | 0,69 | 0,24 | 0,00 | 0,00 | **1,53** |
| T3a | **3,89** | **4,76** | **6,09** | **21,95** | 0,24 | 0,00 | 0,00 | **1,38** |
| T3b | **4,65** | **4,76** | **6,03** | **22,64** | 0,24 | 0,39 | 0,00 | **1,46** |
| D1 | **1,58** | **2,94** | **1,06** | **13,85** | 0,00 | 0,00 | 0,26 | **12,51** |
| D2 | **1,73** | **2,12** | 0,00 | 0,40 | 0,00 | 0,00 | 0,01 | **8,24** |
| P1 | **48,12** | **15,97** | 0,12 | 0,21 | **67,19** | **25,33** | 0,05 | **11,63** |
| P2 | **1,26** | **1,56** | **4,11** | 0,78 | 0,00 | 0,00 | 0,40 | **12,50** |
| P3 | 0,00 | **1,24** | 0,00 | 0,16 | 0,00 | 0,00 | 0,09 | **9,26** |
| K1 | 0,35 | 0,58 | 0,00 | 0,55 | 0,00 | 0,00 | 0,75 | 0,90 |

| OCR | Hor 26 | Hor 27 | Hor 47 | Opus 3 | Opus 20 | Opus 165 | Sieb 9 |
|---|---|---|---|---|---|---|---|
| R0 |  |  |  | 0,03 | 0,00 | 0,36 | **1,32** |
| T1 | 0,00 | 0,00 | **4,86** | 0,11 | 0,00 | **8,97** | **99,36** |
| T2 | 0,00 | 0,00 | **4,86** | 0,11 | 0,00 | **8,97** | **50,18** |
| T3a | 0,00 | 0,00 | **4,20** | 0,11 | 0,00 | **8,97** | **73,80** |
| T3b | 0,00 | 0,00 | **3,58** | 0,00 | 0,00 | **8,97** | **54,10** |
| D1 | 0,00 | **3,23** | **5,02** | **17,44** | 0,00 | 0,00 | **16,29** |
| D2 | 0,00 | 0,13 | 0,99 | **7,60** | 0,00 | 0,00 | 0,04 |
| P1 | 0,00 | 0,67 | **3,17** | **23,44** | 0,02 | **23,66** | **4,76** |
| P2 | 0,00 | 0,13 | **3,45** | **8,23** | 0,00 | 0,56 | **15,22** |
| P3 | 0,00 | 0,00 | **1,67** | **7,45** | 0,00 | 0,00 | **4,22** |
| K1 | 0,00 | 0,00 | 0,21 | 0,00 | 0,00 | **6,55** | **83,00** |

### 4.3 A mesma coisa pela área da figura coberta (%)

| OCR | Pal 5 | Pal 9 | Pal 10 | Pal 57 | Esc 7 | Esc 35 | Hor 11 | Hor 13 |
|---|---|---|---|---|---|---|---|---|
| R0 | **1,4** | **6,9** | **5,8** | **38,8** |  |  |  |  |
| T1 | **3,8** | **5,3** | **5,9** | **57,7** | **2,7** | 0,0 | 0,0 | **4,7** |
| T2 | **3,8** | **5,3** | **5,9** | 0,3 | **2,7** | 0,0 | 0,0 | **4,7** |
| T3a | **2,9** | **5,3** | **5,9** | **57,3** | **2,7** | 0,0 | 0,0 | **4,1** |
| T3b | **3,5** | **5,3** | **5,9** | **57,6** | 0,8 | 0,1 | 0,0 | **4,0** |
| D1 | **1,1** | **2,4** | **1,8** | **24,9** | 0,0 | 0,0 | 0,1 | **10,4** |
| D2 | 1,0 | **1,7** | 0,1 | 0,4 | 0,0 | 0,0 | 0,0 | **5,2** |
| P1 | **52,8** | **12,3** | **4,3** | **1,7** | **77,1** | **25,8** | 0,1 | **8,4** |
| P2 | 0,8 | **1,6** | **5,9** | **2,0** | 0,1 | 0,0 | 0,5 | **10,1** |
| P3 | 0,0 | **1,0** | 0,6 | **1,1** | 0,0 | 0,0 | 0,1 | **7,2** |
| K1 | 0,6 | 0,7 | 0,7 | **2,1** | 0,0 | 0,0 | 0,6 | **2,5** |

| OCR | Hor 26 | Hor 27 | Hor 47 | Opus 3 | Opus 20 | Opus 165 | Sieb 9 |
|---|---|---|---|---|---|---|---|
| R0 |  |  |  | **4,3** | 0,0 | 0,4 | **1,4** |
| T1 | 0,0 | **1,4** | **2,7** | **6,2** | 0,0 | **14,6** | **97,1** |
| T2 | 0,0 | 0,0 | **2,7** | **6,2** | 0,0 | **14,6** | **49,5** |
| T3a | 0,0 | 0,0 | **2,2** | **6,2** | 0,0 | **14,6** | **69,1** |
| T3b | 0,0 | 0,0 | **1,8** | 0,0 | 0,0 | **14,5** | **49,4** |
| D1 | **1,1** | **1,4** | **2,2** | **5,0** | 0,0 | 0,3 | **16,4** |
| D2 | 0,0 | 0,2 | 0,4 | **2,2** | 0,0 | 0,4 | 0,0 |
| P1 | 0,4 | **2,9** | **1,2** | **32,2** | 0,1 | **17,3** | **5,9** |
| P2 | 0,4 | **2,0** | **1,5** | **2,8** | 0,0 | **1,2** | **16,8** |
| P3 | 0,3 | 0,1 | 0,7 | **3,2** | 0,0 | 0,1 | **5,3** |
| K1 | 0,8 | **1,1** | 0,5 | 0,3 | 0,0 | **3,1** | **79,5** |

### 4.4 Obrigatórias sem o alargamento de 15% (%)

Na Horas 13 o texto está colado na moldura dourada. Com o alargamento de 15%, qualquer caixa de linha inteira encosta na moldura. Sem o alargamento, o docTR `fast_base` e o Kraken ficam em 0% ali, e o PP-OCRv6 pequeno em 0,2%. Mas o 1.4 vai precisar de algum alargamento para não comer a ponta das letras. Então a Horas 13 é um problema real para quem desenha a caixa rente à moldura, e o 1.5 terá de resolver isso (ver Ideias).

| OCR | Pal 5 | Esc 35 | Hor 11 | Hor 13 | Hor 26 | Hor 27 | Opus 20 |
|---|---|---|---|---|---|---|---|
| R0 | 0,66 |  |  |  |  |  | 0,00 |
| T1 | 4,28 | 0,00 | 0,00 | 0,50 | 0,00 | 0,00 | 0,00 |
| T2 | 4,28 | 0,00 | 0,00 | 0,50 | 0,00 | 0,00 | 0,00 |
| T3a | 3,03 | 0,00 | 0,00 | 0,36 | 0,00 | 0,00 | 0,00 |
| T3b | 4,04 | 0,00 | 0,00 | 0,49 | 0,00 | 0,00 | 0,00 |
| D1 | 1,07 | 0,00 | 0,13 | 2,21 | 0,00 | 2,55 | 0,00 |
| D2 | 1,18 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| P1 | 30,87 | 17,05 | 0,00 | 1,50 | 0,00 | 0,00 | 0,02 |
| P2 | 0,96 | 0,00 | 0,16 | 2,16 | 0,00 | 0,00 | 0,00 |
| P3 | 0,00 | 0,00 | 0,00 | 0,20 | 0,00 | 0,00 | 0,00 |
| K1 | 0,19 | 0,00 | 0,54 | 0,00 | 0,00 | 0,00 | 0,00 |

### 4.5 Linhas falsas (todas as 22 páginas)

Uma linha é "falsa" quando menos de 30% dela cai em texto. As que ficam fora de figura importam para o 1.4, porque a tinta dentro de uma caixa fica com a cor. Uma caixa em cima da mancha do verso ou da pauta de música guardaria a mancha ou a pauta.

| OCR | Linhas falsas fora de texto (papel, mancha do verso, pauta) | Linhas falsas dentro de figura | Só no Graduale (pauta de música) |
|---|---|---|---|
| R0 | 10 | 30 | 0 |
| T1 | 6 | 10 | 1 |
| T2 | 6 | 4 | 1 |
| T3a | 2 | 4 | 0 |
| T3b | 5 | 5 | 1 |
| D1 | 17 | 45 | 10 |
| D2 | 14 | 8 | 5 |
| P1 | 29 | 24 | 28 |
| P2 | 30 | 16 | 26 |
| P3 | 15 | 3 | 13 |
| K1 | 5 | 57 | 0 |

## 5. O que se vê nas folhas de contato

- **R0, as linhas que já vêm no PDF:**
  - são de graça e acham bem o texto corrido;
  - no Palatino 9, 10 e 57, as "linhas" invadem a moldura e os laços do título (6% a 18%);
  - na tabela do Opus 256, as caixas são pedacinhos que cobrem só 30% dos números;
  - servem de referência, não de detector.
- **Tesseract (T1 a T3b):**
  - acha muito bem o texto corrido impresso;
  - no Siebmacher 9 desenha "linhas" em cima de toda a moldura ornamental;
  - na Horas 11 não acha nenhuma das 10 linhas do título dentro da iluminura;
  - no Graduale acha 0 a 4 linhas;
  - no Palatino 5 põe duas linhas no alto da oval do retrato, com confiança 36 e 40, acima do limiar 20 do filtro;
  - no Palatino 9 e 10, as linhas da direita entram na moldura preta;
  - o filtro do IA só mexe no Palatino 57 (tira as "linhas" dos laços, mas também 4 linhas de texto: cai para 69% achado) e no Siebmacher (tira metade da moldura);
  - trocar o modelo (T3a, T3b) **não muda as linhas**, só a confiança, como a pesquisa tinha deduzido (seção 10.2). Com o filtro, o `GT4HistOCR` joga fora muito texto de verdade (82% achado, em média).
- **docTR `db_resnet50` (D1):** acha bem o texto, mas põe caixinhas na moldura do Siebmacher (16%), nos laços do Palatino 57 (14%) e no emblema do Opus 3 (17%).
- **docTR `fast_base` (D2):**
  - caixas justas, uma por trecho de linha;
  - não pega a moldura do Siebmacher nem os laços do Palatino 57;
  - erros: o emblema do Opus 3 (7,6%, e o emblema tem letras dentro), caixinhas na borda do retrato do Palatino 5 e na capitular Q do Palatino 9 (1,7% e 2,1%), e 4 caixas em "fantasmas" de letras da mancha do verso no Palatino 9;
  - na tabela do Opus 256 perde parte dos números (87%), porque o docTR reduz a página a 1024 px por dentro;
  - no Palatino 57 perde o "A" grande de "Anno Domini" (69% dessa linha).
- **PP-OCRv5 servidor (P1):** fora de questão. Põe caixas enormes em cima do retrato do Palatino 5 (48%), da gravura da Escola 7 (67%) e do anjo da Escola 35 (25%).
- **PP-OCRv5 móvel (P2):** texto bom; pega pedaços da moldura do Siebmacher (15%) e da moldura do Palatino 10 (4%); no Graduale põe 26 caixas em cima das notas de música.
- **PP-OCRv6 pequeno (P3):** parecido com o docTR `fast_base`:
  - não pisa no retrato do Palatino 5;
  - pega um pouco da moldura do Siebmacher (4%) e o emblema do Opus 3 (7%);
  - no Palatino 57 perde a maior parte de "Palatinus Ciuis Romanus" (só 42% dessa linha) e parte da assinatura "D iii" (88% achado na página);
  - no Graduale põe 13 caixinhas nas notas.
- **Kraken (K1):**
  - contorno ondulado, colado nas letras;
  - não pisa no retrato, no anjo nem na foto, e quase não pisa nas iluminuras das Horas 11 e 47 (menos de 1%);
  - no Siebmacher desenha "linhas" em toda a moldura ornamental (83%);
  - no Opus 165 põe uma linha num traço do diagrama (6,6%);
  - na tabela do Opus 256 falha: 33%, e o próprio Kraken avisou que não conseguiu fechar o contorno de algumas linhas ali;
  - na Horas 13 perde o "DE" grande de "DE CE QUI EST", e no Opus 3 perde o "OF" pequeno.
- **Todos os detectores** perdem parte da letra grande de floreio da assinatura "J. Sibmacher" (o docTR `fast_base` acha 48% dela, o Kraken 74%).

## 6. Manuscritos: Graduale 221 a 223 e Horas

Texto achado (%):

| OCR | Hor 11 | Hor 13 | Hor 47 | Hor 26 | Hor 27 | Grad 221 | Grad 222 | Grad 223 |
|---|---|---|---|---|---|---|---|---|
| R0 |  |  |  |  |  |  |  |  |
| T1 | **0,0** | 100,0 | 99,3 | 100,0 | **96,4** | **25,7** | **0,0** | **15,8** |
| T2 | **0,0** | 100,0 | 99,3 | 100,0 | **93,2** | **25,7** | **0,0** | **15,8** |
| T3a | **0,0** | **95,7** | 99,3 | **93,7** | **93,2** | **25,5** | **0,0** | **15,8** |
| T3b | **0,0** | **85,3** | 98,9 | **77,9** | **74,3** | **25,7** | **0,0** | **15,8** |
| D1 | 100,0 | 100,0 | 100,0 | **97,0** | 99,4 | 98,8 | 98,2 | 98,1 |
| D2 | 100,0 | 99,5 | 100,0 | 98,5 | 99,6 | 98,1 | 99,0 | **97,2** |
| P1 | 100,0 | 100,0 | 100,0 | 100,0 | 99,9 | **95,7** | **96,8** | 99,7 |
| P2 | 99,6 | 99,8 | 100,0 | **97,6** | 98,7 | 100,0 | **87,2** | 98,1 |
| P3 | 100,0 | 100,0 | 100,0 | 100,0 | 98,2 | **97,9** | 98,2 | 99,5 |
| K1 | **96,9** | **96,3** | 100,0 | 98,5 | 98,7 | 98,7 | 98,6 | **94,8** |

- **Graduale (gótico do séc. XIV, com pauta vermelha e notas):**
  - **o Tesseract não serve** (0% a 26%);
  - o **Kraken é o melhor:** acha 95% a 99% das palavras e **não põe nenhuma caixa na música**;
  - o docTR `fast_base` acha 97% a 99%, com 5 caixinhas em notas nas três páginas;
  - o PP-OCRv6 pequeno acha 98% a 99,5%, com 13 caixinhas em notas;
  - o PP-OCRv5 móvel põe 26 caixas na música e perde parte das palavras da 222 (87%).
- **Horas (caligrafia francesa em iluminura, scan de 1024 px):**
  - todos os detectores neurais acham 96% a 100%;
  - o Tesseract não acha nada na Horas 11;
  - com o alargamento de 15%, só o Kraken fica abaixo de 1% de figura nas cinco páginas das Horas;
  - nas Horas 13 e 47 os outros encostam na moldura (ver 4.4).

## 7. Tempo

Segundos por página neste PC (mediana de 3 rodadas). T2 tem o mesmo tempo do T1: o filtro é só uma conta depois.

| OCR | Pal 5 | Pal 7 | Pal 9 | Pal 10 | Esc 7 | Hor 11 | Hor 13 | Hor 47 | Opus 11 | Opus 3 | Opus 20 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | 2,2 | 4,6 | 3,1 | 3,9 | 3,5 | 0,5 | 0,9 | 1,1 | 4,6 | 1,7 | 1,2 | 27 s |
| T3a | 2,4 | 3,0 | 2,2 | 2,9 | 2,5 | 0,6 | 1,6 | 1,2 | 2,8 | 1,6 | 0,8 | 22 s |
| T3b | 1,9 | 3,8 | 2,8 | 3,3 | 2,4 | 0,6 | 1,2 | 1,3 | 3,2 | 1,7 | 0,9 | 23 s |
| D1 | 1,1 | 1,2 | 1,1 | 1,1 | 1,2 | 1,1 | 1,0 | 1,1 | 1,3 | 1,0 | 1,1 | 12 s |
| D2 | 1,0 | 1,1 | 1,0 | 1,1 | 1,1 | 1,0 | 0,9 | 1,0 | 1,2 | 1,0 | 0,9 | 11 s |
| P1 | 5,8 | 5,8 | 6,1 | 7,0 | 7,2 | 3,5 | 3,0 | 4,0 | 12,0 | 9,7 | 9,9 | 74 s |
| P2 | 1,0 | 1,2 | 1,2 | 1,1 | 1,2 | 0,5 | 0,8 | 0,5 | 2,1 | 1,6 | 2,1 | 13 s |
| P3 | 1,0 | 0,9 | 1,0 | 0,9 | 0,9 | 0,4 | 0,7 | 0,6 | 1,6 | 1,4 | 1,8 | 11 s |
| K1 | 10,3 | 17,2 | 12,4 | 14,3 | 14,1 | 9,0 | 9,9 | 10,2 | 13,3 | 7,4 | 6,1 | 124 s |

| OCR | Opus 165 | Opus 256 | Hor 26 | Hor 27 | Esc 35 | Rhet 18 | Sieb 9 | Pal 57 | Grad 221 | Grad 222 | Grad 223 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | 3,5 | 9,0 | 1,4 | 1,3 | 2,8 | 3,5 | 2,4 | 1,7 | 0,5 | 0,5 | 0,5 | 27 s |
| T3a | 2,9 | 6,3 | 1,6 | 1,4 | 2,1 | 3,4 | 1,7 | 1,4 | 0,6 | 0,6 | 0,5 | 22 s |
| T3b | 2,6 | 7,9 | 1,6 | 1,6 | 1,9 | 3,2 | 1,8 | 1,4 | 0,5 | 0,5 | 0,5 | 24 s |
| D1 | 1,2 | 1,3 | 1,0 | 1,1 | 1,2 | 1,2 | 1,0 | 1,2 | 1,2 | 1,0 | 1,2 | 13 s |
| D2 | 1,0 | 1,2 | 1,0 | 1,0 | 1,0 | 1,0 | 1,0 | 1,0 | 1,1 | 1,1 | 1,0 | 12 s |
| P1 | 10,7 | 12,7 | 3,5 | 3,6 | 8,6 | 11,4 | 4,7 | 6,7 | 2,6 | 3,0 | 2,7 | 70 s |
| P2 | 1,7 | 2,5 | 0,6 | 0,5 | 1,2 | 1,8 | 0,8 | 1,1 | 0,5 | 0,4 | 0,4 | 11 s |
| P3 | 1,7 | 2,2 | 0,5 | 0,6 | 1,7 | 1,6 | 0,7 | 1,1 | 0,5 | 0,4 | 0,4 | 11 s |
| K1 | 12,3 | 25,1 | 11,5 | 13,3 | 11,9 | 17,7 | 17,6 | 9,8 | 9,5 | 9,0 | 12,1 | 150 s |

- **Os rápidos:** docTR `fast_base`, PP-OCRv6 pequeno e PP-OCRv5 móvel fazem cerca de 1 s por página. O Tesseract faz de 0,5 s a 9 s, conforme a quantidade de texto. O PP-OCRv5 servidor faz de 3 s a 13 s.
- **O Kraken:** 6 s a 25 s por página, mediana de 12 s. Uma página da tabela leva 25 s.
- **Kraken no Windows**, com o Python 3.12 separado que o pesquisador montou, sem WSL, em 6 páginas:
  - **deu exatamente as mesmas linhas** do WSL;
  - foi de 3% a 33% mais lento (Graduale 222: 9,6 s contra 9,0 s; Opus 11: 17,7 s contra 13,3 s).
- **Notebook do Kaique (i5-1235U), não medido.** O item 0.6 ainda não tem a régua. Estimo, por dedução, 1,5 a 2 vezes mais lento que este PC, então:
  - docTR `fast_base`: uns 2 s por página, ou 10 minutos num livro de 300 páginas;
  - Kraken: 20 a 30 s por página, ou 2 horas a 2 horas e meia num livro de 300 páginas.
- **Regra 6 (nada mais lento):** a detecção de linhas não pode entrar na prévia. Tem de rodar na hora de processar, em segundo plano.

## 8. Folhas de contato (caixas de cada OCR por cima de cada página)

Como ler:

- **azul:** caixa de linha (desenhada sem o alargamento);
- **contorno vermelho:** zona "não pode ter linha";
- **laranja** (só no T1 e no T3): linha que o filtro do Internet Archive jogaria fora;
- **R0 em cinza:** o PDF não tem texto do Internet Archive.

No alto de cada quadro: texto achado, figura tomada (tinta e área) e tempo.

<h4 style="page-break-before: always">Palatino 5</h4>
<p><img src="folhas/palatino_p005.jpg" alt="Palatino 5: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Palatino 7</h4>
<p><img src="folhas/palatino_p007.jpg" alt="Palatino 7: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Palatino 9</h4>
<p><img src="folhas/palatino_p009.jpg" alt="Palatino 9: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Palatino 10</h4>
<p><img src="folhas/palatino_p010.jpg" alt="Palatino 10: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Palatino 57</h4>
<p><img src="folhas/palatino_p057.jpg" alt="Palatino 57: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Escola 7</h4>
<p><img src="folhas/escola_p007.jpg" alt="Escola 7: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Escola 35</h4>
<p><img src="folhas/escola_p035.jpg" alt="Escola 35: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Horas 11</h4>
<p><img src="folhas/horas_p011.jpg" alt="Horas 11: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Horas 13</h4>
<p><img src="folhas/horas_p013.jpg" alt="Horas 13: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Horas 26</h4>
<p><img src="folhas/horas_p026.jpg" alt="Horas 26: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Horas 27</h4>
<p><img src="folhas/horas_p027.jpg" alt="Horas 27: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Horas 47</h4>
<p><img src="folhas/horas_p047.jpg" alt="Horas 47: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Opus Majus 3</h4>
<p><img src="folhas/opusmajus_p003.jpg" alt="Opus Majus 3: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Opus Majus 11</h4>
<p><img src="folhas/opusmajus_p011.jpg" alt="Opus Majus 11: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Opus Majus 20</h4>
<p><img src="folhas/opusmajus_p020.jpg" alt="Opus Majus 20: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Opus Majus 165</h4>
<p><img src="folhas/opusmajus_p165.jpg" alt="Opus Majus 165: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Opus Majus 256</h4>
<p><img src="folhas/opusmajus_p256.jpg" alt="Opus Majus 256: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Rhetorica 18</h4>
<p><img src="folhas/rhetorica_p018.jpg" alt="Rhetorica 18: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Siebmacher 9</h4>
<p><img src="folhas/siebmacher_p009.jpg" alt="Siebmacher 9: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Graduale 221</h4>
<p><img src="folhas/graduale_p221.jpg" alt="Graduale 221: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Graduale 222</h4>
<p><img src="folhas/graduale_p222.jpg" alt="Graduale 222: caixas de cada OCR"></p>

<h4 style="page-break-before: always">Graduale 223</h4>
<p><img src="folhas/graduale_p223.jpg" alt="Graduale 223: caixas de cada OCR"></p>

## 9. As zonas do gabarito (a conferir pelo Samuel)

Em cada imagem:

- **à esquerda:** verde = tem de ser texto, vermelho = não pode ter linha, cinza = neutro (não conta);
- **à direita:** a tinta que entra na conta. Verde = tinta de texto, vermelho = tinta de figura, cinza = tinta fora de zona, que não conta.

O que eu decidi ao desenhar e **você precisa confirmar**:

- os floreios do Palatino 57 ficaram dentro do texto, e os laços em volta do título ficaram como figura;
- as capitulares xilogravadas (a Q do Palatino 9) são figura, mas as capitulares desenhadas a pena do Graduale ficaram neutras;
- o endereço do site no pé da Escola é texto, mesmo que o R8 vá apagá-lo;
- o emblema do Opus 3 é figura, embora tenha letras dentro;
- as letrinhas dentro dos diagramas do Opus 165 ficaram neutras;
- os filetes da Rhetorica ficaram neutros;
- no Graduale, a pauta e as notas ficaram fora de toda zona. Elas não contam na figura, só aparecem nas "linhas falsas".

<h4 style="page-break-before: always">Palatino 5</h4>
<p><img src="zonas/palatino_p005.jpg" width="400" alt="Palatino 5: zonas do gabarito"></p>

<h4>Palatino 7</h4>
<p><img src="zonas/palatino_p007.jpg" width="400" alt="Palatino 7: zonas do gabarito"></p>

<h4 style="page-break-before: always">Palatino 9</h4>
<p><img src="zonas/palatino_p009.jpg" width="400" alt="Palatino 9: zonas do gabarito"></p>

<h4>Palatino 10</h4>
<p><img src="zonas/palatino_p010.jpg" width="400" alt="Palatino 10: zonas do gabarito"></p>

<h4 style="page-break-before: always">Palatino 57</h4>
<p><img src="zonas/palatino_p057.jpg" width="400" alt="Palatino 57: zonas do gabarito"></p>

<h4>Escola 7</h4>
<p><img src="zonas/escola_p007.jpg" width="400" alt="Escola 7: zonas do gabarito"></p>

<h4 style="page-break-before: always">Escola 35</h4>
<p><img src="zonas/escola_p035.jpg" width="400" alt="Escola 35: zonas do gabarito"></p>

<h4>Horas 11</h4>
<p><img src="zonas/horas_p011.jpg" width="400" alt="Horas 11: zonas do gabarito"></p>

<h4 style="page-break-before: always">Horas 13</h4>
<p><img src="zonas/horas_p013.jpg" width="400" alt="Horas 13: zonas do gabarito"></p>

<h4>Horas 26</h4>
<p><img src="zonas/horas_p026.jpg" width="400" alt="Horas 26: zonas do gabarito"></p>

<h4 style="page-break-before: always">Horas 27</h4>
<p><img src="zonas/horas_p027.jpg" width="400" alt="Horas 27: zonas do gabarito"></p>

<h4>Horas 47</h4>
<p><img src="zonas/horas_p047.jpg" width="400" alt="Horas 47: zonas do gabarito"></p>

<h4 style="page-break-before: always">Opus Majus 3</h4>
<p><img src="zonas/opusmajus_p003.jpg" width="400" alt="Opus Majus 3: zonas do gabarito"></p>

<h4>Opus Majus 11</h4>
<p><img src="zonas/opusmajus_p011.jpg" width="400" alt="Opus Majus 11: zonas do gabarito"></p>

<h4 style="page-break-before: always">Opus Majus 20</h4>
<p><img src="zonas/opusmajus_p020.jpg" width="400" alt="Opus Majus 20: zonas do gabarito"></p>

<h4>Opus Majus 165</h4>
<p><img src="zonas/opusmajus_p165.jpg" width="400" alt="Opus Majus 165: zonas do gabarito"></p>

<h4 style="page-break-before: always">Opus Majus 256</h4>
<p><img src="zonas/opusmajus_p256.jpg" width="400" alt="Opus Majus 256: zonas do gabarito"></p>

<h4>Rhetorica 18</h4>
<p><img src="zonas/rhetorica_p018.jpg" width="400" alt="Rhetorica 18: zonas do gabarito"></p>

<h4 style="page-break-before: always">Siebmacher 9</h4>
<p><img src="zonas/siebmacher_p009.jpg" width="400" alt="Siebmacher 9: zonas do gabarito"></p>

<h4>Graduale 221</h4>
<p><img src="zonas/graduale_p221.jpg" width="400" alt="Graduale 221: zonas do gabarito"></p>

<h4 style="page-break-before: always">Graduale 222</h4>
<p><img src="zonas/graduale_p222.jpg" width="400" alt="Graduale 222: zonas do gabarito"></p>

<h4>Graduale 223</h4>
<p><img src="zonas/graduale_p223.jpg" width="400" alt="Graduale 223: zonas do gabarito"></p>

## 10. Detalhes

### 10.1 Pares (só para indicar se os erros se completam; juntar de verdade é o item 1.5)

"Os dois concordam" = só é texto onde os dois põem caixa. "Qualquer um" = é texto onde pelo menos um põe caixa.

| Par | Como junta | Texto achado (média, 19 páginas) | Páginas com 98% ou mais | Pior obrigatória (figura) | Páginas com figura acima de 1% (de 22) | Graduale 221 / 222 / 223 |
|---|---|---|---|---|---|---|
| K1+D2 | os dois concordam | 95,0% | 12 de 19 | 0,68% | 0 | 96,9 / 98,1 / 94,3 |
| K1+D2 | qualquer um | 99,1% | 18 de 19 | 8,46% | 7 (Pal 5, Pal 9, Hor 13, Hor 47, Opus 3, Opus 165, Sieb 9) | 99,9 / 99,5 / 97,7 |
| K1+P3 | os dois concordam | 94,6% | 12 de 19 | 0,90% | 1 (Sieb 9) | 96,7 / 97,2 / 94,8 |
| K1+P3 | qualquer um | 99,6% | 18 de 19 | 9,27% | 6 (Pal 9, Hor 13, Hor 47, Opus 3, Opus 165, Sieb 9) | 99,9 / 99,5 / 99,5 |
| D2+P3 | os dois concordam | 97,9% | 15 de 19 | 7,19% | 1 (Hor 13) | 97,8 / 98,2 / 97,2 |
| D2+P3 | qualquer um | 99,5% | 17 de 19 | 10,31% | 6 (Pal 5, Pal 9, Hor 13, Hor 47, Opus 3, Sieb 9) | 98,2 / 99,0 / 99,6 |
| T1+D2 | os dois concordam | 92,7% | 14 de 19 | 1,10% | 1 (Hor 13) | 25,5 / 0,0 / 15,8 |
| T1+D2 | qualquer um | 99,8% | 18 de 19 | 8,66% | 9 (Pal 5, Pal 9, Pal 10, Hor 13, Hor 47, Opus 3, Opus 165, Sieb 9, Pal 57) | 98,3 / 99,0 / 97,2 |
| K1+T1 | os dois concordam | 89,8% | 13 de 19 | 0,56% | 2 (Opus 165, Sieb 9) | 25,6 / 0,0 / 15,8 |
| K1+T1 | qualquer um | 99,6% | 18 de 19 | 5,38% | 8 (Pal 5, Pal 9, Pal 10, Hor 13, Hor 47, Opus 165, Sieb 9, Pal 57) | 98,8 / 98,6 / 94,8 |

- **Kraken + docTR `fast_base`, onde os dois concordam:**
  - nenhuma página passa de 1% de figura, inclusive o Siebmacher;
  - o texto cai para 95% em média, porque se perde onde qualquer um dos dois perde. A pior é a tabela do Opus 256 (32%); as outras ficam entre 94% e 100%.
- **Juntar por "qualquer um"** acha quase todo o texto, mas soma as figuras dos dois.
- O 1.5 vai precisar de algo melhor que essas duas contas simples. Por exemplo, usar o detector de gravura do ScanTailor (1.2) para vetar caixa dentro de figura. Isso é trabalho do 1.5, não deste item.

### 10.2 O modelo do Tesseract muda as linhas? (a dedução da pesquisa)

Quase nunca. Sem o filtro, T1, T3a e T3b acham o mesmo número de linhas em 19 das 22 páginas, e diferem em 1 ou 2 linhas nas outras três. O que muda é a confiança, e portanto o que o filtro joga fora.

| Página | T1 (linhas) | T3a sem filtro | T3b sem filtro | T2 (depois do filtro) | T3a (depois do filtro) | T3b (depois do filtro) |
|---|---|---|---|---|---|---|
| Pal 5 | 13 | 13 | 13 | 13 | 12 | 9 |
| Pal 7 | 38 | 38 | 38 | 38 | 37 | 37 |
| Pal 9 | 27 | 27 | 27 | 27 | 27 | 25 |
| Pal 10 | 28 | 28 | 28 | 28 | 28 | 26 |
| Esc 7 | 43 | 43 | 43 | 43 | 43 | 41 |
| Hor 11 | 0 | 0 | 0 | 0 | 0 | 0 |
| Hor 13 | 17 | 17 | 17 | 17 | 15 | 15 |
| Hor 47 | 19 | 19 | 19 | 19 | 19 | 19 |
| Opus 11 | 39 | 39 | 39 | 39 | 39 | 37 |
| Opus 3 | 13 | 13 | 13 | 13 | 12 | 8 |
| Opus 20 | 2 | 2 | 2 | 2 | 2 | 2 |
| Opus 165 | 40 | 40 | 40 | 40 | 40 | 38 |
| Opus 256 | 54 | 54 | 54 | 53 | 47 | 45 |
| Hor 26 | 33 | 32 | 33 | 33 | 31 | 27 |
| Hor 27 | 38 | 38 | 38 | 36 | 36 | 25 |
| Esc 35 | 24 | 24 | 24 | 24 | 24 | 24 |
| Rhet 18 | 38 | 38 | 38 | 37 | 37 | 37 |
| Sieb 9 | 26 | 26 | 25 | 21 | 21 | 19 |
| Pal 57 | 16 | 14 | 16 | 10 | 7 | 8 |
| Grad 221 | 4 | 4 | 4 | 4 | 2 | 4 |
| Grad 222 | 0 | 0 | 0 | 0 | 0 | 0 |
| Grad 223 | 1 | 1 | 1 | 1 | 1 | 1 |

## 11. Quais 2 ficam (recomendação; quem decide é o Samuel)

Pelo critério da pesquisa (seção 5.6):

1. **Cai fora quem passar de 1% de figura numa página obrigatória, a não ser que a própria confiança resolva.**
   - Com a medida pedida, só o Kraken passa nas 7.
   - Sem o alargamento, passam o Kraken e o PP-OCRv6 pequeno. O docTR `fast_base` fica a um passo: 1,2% no Palatino 5.
   - O filtro de confiança do Tesseract não resolve o caso dele.
2. **Entre os que sobram, ganha quem achar mais texto e depois quem for mais rápido.**
3. **Preferir erros diferentes.**
4. **Fica fora quem exigir WSL ou um segundo Python no notebook, a menos que ganhe com folga.**
   - O Kraken não precisa mais de WSL: roda no Windows com um Python 3.12 só dele. Ainda é um "segundo Python".
   - Ele ganha com folga em duas coisas que o Samuel pediu: não pisar em figura e servir para manuscrito.

**Recomendo Kraken + docTR `fast_base`:**

- **Kraken:**
  - é o único que respeita as páginas obrigatórias sozinho;
  - é o melhor no manuscrito;
  - é o mesmo programa que a Fase 7 usaria para ler o manuscrito;
  - o Samuel pediu OCR de manuscrito desde o começo.
- **docTR `fast_base`:**
  - é rápido, está no Python do programa e acha mais texto;
  - erra onde o Kraken acerta, e vice-versa: moldura do Siebmacher, tabela do Opus 256;
  - juntos, onde concordam, nenhuma página passou de 1% de figura.

**Alternativa, se o peso do Kraken não compensar agora:** docTR `fast_base` + PP-OCRv6 pequeno.

- Os dois são rápidos (1 s cada), leves e no Python 3.14 do programa. Onde concordam, só a Horas 13 passa de 1%, e é a moldura encostada no texto.
- Mas erram parecido: os dois pisam no emblema do Opus 3 e deixam caixinhas nas notas do Graduale.
- E o PP-OCRv6 não estava na lista da pesquisa. Entrou porque é o detector padrão do RapidOCR hoje, e mediu melhor que o PP-OCRv5 pedido.

**Ficam fora, pelo que foi medido:**

- **Tesseract:** falha no título da Horas 11, no Graduale e na moldura do Siebmacher, e o filtro não resolve. Continua sendo candidato para **transcrever** impresso na Fase 7, que é outra pergunta.
- **PP-OCRv5 servidor:** cobre retrato e gravuras.
- **docTR `db_resnet50`:** pior que o `fast_base` em tudo.
- **As linhas do Internet Archive:** são de graça, mas invadem moldura e perdem a tabela. Podem entrar no 1.4 como terceira opinião nos PDFs do IA.

## 12. O que precisa para rodar no notebook do Kaique

| OCR | O que instalar | Tamanho | Pede administrador? | Observação |
|---|---|---|---|---|
| docTR `fast_base` | pacote `onnxtr` (Python puro, Apache-2.0) e as dependências `pyclipper`, `shapely`, `rapidfuzz`, `langdetect`, `huggingface-hub`, `pypdfium2`, `defusedxml`, `anyascii`. O `onnxruntime`, o `scipy` e o `opencv` o programa já tem | pacotes: poucos MB; modelo `rep_fast_base`: **42 MB** | não | Instalou e rodou no **Python 3.14** (ambiente de teste `.venv-ocr`). Na primeira vez, o modelo baixa sozinho do GitHub: o instalador tem de levar o arquivo junto (o Kaique pode estar sem internet). A licença dos pesos não está escrita à parte (ver a pesquisa) |
| PP-OCRv6 pequeno (alternativa) | pacote `rapidocr` (Apache-2.0) e `omegaconf`, `shapely`, `pyclipper`, `colorlog` | modelo de detecção: **9,9 MB** | não | Rodou no **3.14**. Na primeira vez, baixa os modelos de um site chinês (modelscope.cn): o instalador tem de levá-los. Os modelos são da Baidu, sem licença própria escrita |
| Kraken `blla` | um **Python 3.12 só dele**, com `kraken` 7.1.1, `torch` para processador e o resto, com as versões travadas; `PYTHONUTF8=1` | **~1,2 GB** (medido pelo pesquisador); o modelo `blla` vem dentro do pacote | não | **Sem WSL** (conferido: as mesmas linhas no Windows e no WSL). O autor do Kraken não dá suporte a Windows, então cada versão nova tem de ser testada antes de ir para o instalador. Estimativa de 20 a 30 s por página no notebook. Memória: pico de 1,4 GB (pesquisador) |
| Tesseract (fora) | programa da UB Mannheim + modelos | 239 MB + 4 a 18 MB por idioma | o instalador sim; uma cópia da pasta, provavelmente não | não recomendado |

## 13. Ressalvas

- **As zonas são minhas e ainda não foram conferidas.** Mudar uma zona muda os números da página, principalmente na Horas 13, onde a moldura e o texto se encostam.
- **Sem o corte e o endireitamento do programa.** A pesquisa pedia as páginas depois dessas etapas. Usei a página como vem no PDF, porque as zonas foram desenhadas nela e as páginas do gabarito já estão quase retas. No Siebmacher, cortar a borda do scan não tira a moldura, que é do livro.
- **Scan pequeno das Horas e do Graduale** (72 DPI no arquivo, ~1000 px de largura): não aumentei a imagem. O Tesseract talvez melhore com a imagem ampliada; não testei.
- **O alargamento de 15% pesa contra quem desenha a caixa rente à moldura.** Por isso a tabela 4.4 também mostra a medida sem o alargamento.
- **O tempo no notebook do Kaique não foi medido.** Os números da seção 7 são deste PC; a conta para o notebook é dedução.
- **O Kraken no Windows** foi medido no ambiente que o pesquisador montou, em 6 páginas. As outras 16 são do WSL. O Kraken avisou "não consegui fechar o contorno" em várias linhas da tabela do Opus 256; essas linhas sumiram da saída dele.
- **O docTR reduz a página inteira a 1024 px por dentro.** Na tabela do Opus 256 isso custa números. Não testei cortar a página em pedaços.
- **O RapidOCR** rodou com o limite de lado aumentado de 2000 para 3000 px, para a página entrar inteira (a pesquisa pedia esse ajuste).
- **Tesseract 5.4.0**, o que o `winget` instalou, não o 5.5.3 citado na pesquisa. Os modelos foram baixados para `modelos\tessdata\` (fora do git): `por`, `lat`, `fra`, `ita`, `deu`, `eng`, `osd`, `script/Fraktur`, `frak2021` e `GT4HistOCR`.
- **O ambiente de teste tem o `onnxruntime` 1.30**; o programa tem o 1.28. Não testei o OnnxTR e o RapidOCR com o 1.28.
- **As linhas do Internet Archive (R0)** saem da medida das letras invisíveis, não da tinta. Uma caixa pode sair um pouco maior ou menor que a linha de verdade.
- **Três medidas são minhas, não da pesquisa:** área coberta, figura sem alargamento e linhas falsas. Estão marcadas como extra.

## 14. Arquivos

- `relatorios\fase1-1.3-comparacao-ocr-2026-09-28\` — este relatório (`.md`, `.html`, `.pdf`), as folhas de contato (`folhas\`), as zonas (`zonas\`), os números (`resultados.json`, `pares.json`) e os scripts que refazem tudo (`scripts\`, ver a docstring de cada um; ordem: `preparar.py`, `rodar_todos.sh`, `medir.py`, `pares.py`, `tabelas.py`).
- `gabarito\ocr-zonas.json` — as zonas (fora do git, como todo o `gabarito\`; há uma cópia em `zonas\ocr-zonas.json` desta pasta).
- `saida_teste\ocr-1.3\` — imagens de trabalho e as linhas de cada OCR (fora do git).
- `modelos\tessdata\` — modelos do Tesseract (fora do git).
- `.venv-ocr\` — ambiente de teste com OnnxTR, RapidOCR e `pytesseract` (fora do git; linha nova no `.gitignore`). No WSL: `/root/ocr-kraken/.venv` (Python 3.13, Kraken 7.1.1).
