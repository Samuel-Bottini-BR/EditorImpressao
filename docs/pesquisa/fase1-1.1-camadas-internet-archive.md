# Fase 1.1: como os PDFs com camadas estão montados

**Data:** 28/09/2026 · **Quem:** agente pesquisador · **Pedido:** gerente, item 1.1 do Plano Definitivo ("tirar o fundo de PDF que já vem com camadas").

Nada de código do programa foi mexido. Os PDFs do gabarito e os livros originais foram só **lidos** com PyMuPDF 1.28 (lista de imagens, máscaras, ordem de desenho, texto invisível e, em 14 páginas, a própria máscara e o fundo decodificados para medir). Os scripts de medição ficaram na pasta temporária da sessão, fora do projeto; o método está descrito na seção 8.

---

## 1. A resposta em cinco frases

1. Os quatro livros com camadas (Palatino, Opus Majus, Rhetorica e Siebmacher) têm **o mesmo desenho em todas as páginas**: primeiro uma imagem de fundo sem máscara, depois, por cima, uma imagem colorida da página inteira recortada por uma **máscara de 1 bit (JBIG2)**; o programa reconhece isso só olhando a lista de imagens, sem decodificar nada.
2. Nas 14 páginas medidas, **nenhuma tem "tudo na camada de baixo"**: todas têm tinta na camada de cima (de 2% a 16% da página). O fundo em resolução cheia do Palatino 5, 7, 9 e 10 vem da opção `--hq-pages` do Internet Archive (as **10 primeiras e as 4 últimas páginas** de cada livro saem com fundo inteiro), e não de uma decisão sobre gravura.
3. A camada de cima **não é só texto**: o código atual do Internet Archive soma à máscara das linhas de texto uma binarização da página inteira. Por isso moldura, capitular xilográfica, retrato, diagramas, fios de tabela e os pontinhos da foto também sobem. Isso **corrige** duas frases do `TESTE-SCANTAILOR-MISTO.md` (seção 7).
4. "Tirar o fundo" = pintar a página de branco e pôr por cima a cor da camada de cima **só onde a máscara manda**. Isso já dá papel branco, texto com a cor original (o vermelho do Opus 3 continua vermelho) e some com a mancha do verso (Palatino 10), o carimbo (Opus 3) e a mancha d'água (Rhetorica 73).
5. O caso perigoso é o de **figura cujos tons só existem embaixo** (a foto do Opus 20; os meios-tons do retrato do Palatino 5). Nenhuma medida simples do fundo separa foto de mancha (testei duas e as duas erraram), então a decisão de "aqui é figura, manter o que o PDF mostra" tem de vir do **seletor de gravura (1.2)**, e não de uma regra nova só para o 1.1.

## 2. Tabela

| O que é | Licença | Roda aqui? | Roda no notebook do Kaique? |
|---|---|---|---|
| Ler as camadas com PyMuPDF (lista de imagens e máscara JBIG2) | AGPL-3.0 (PyMuPDF, já no programa) | Sim, medido: as 14 páginas em ~4 s no total, com fundo e máscara decodificados | Sim (só processador; é a mesma biblioteca que o programa já usa) |
| `archive-pdf-tools` (`internetarchivepdf/mrc.py`), só para **entender** como o PDF foi feito | AGPL-3.0 (o `pdfrenderer.py` é Apache-2.0) | Não precisa rodar: o programa só reconhece o resultado | Não precisa |

---

## 3. O que tem em cada página (lido nos PDFs)

"Tinta em cima" = parte da página onde a máscara deixa aparecer a camada de cima. "Dentro das linhas" = quanto dessa tinta cai dentro das caixas de linha do **texto invisível** que já vem no PDF (o OCR do Internet Archive).

| Página | Feito por | Fundo (desenhado 1º) | Camada de cima (desenhada 2º) | Máscara | Tinta em cima | Dentro das linhas | Em cima | Embaixo | Tudo embaixo? |
|---|---|---|---|---|---|---|---|---|---|
| Palatino 5 | Internet Archive PDF 1.4.22 | 1929×2943, ~400 DPI (**inteiro**) | 1929×2943, ~400 DPI, JPEG 2000 | SMask JBIG2 1 bit, 1929×2943 | 10,7% | 22% | título, retrato em traço (binarizado), "CON GRATIE" | a página inteira: retrato com meios-tons, mancha marrom, letras "fantasma" | **Não.** O retrato está nas duas camadas |
| Palatino 7 | idem | 1929×2943 (**inteiro**) | 1929×2943 | idem | 8,5% | 99% | texto e alguns pontinhos da mancha da página vizinha | papel, fantasma das letras, a escrita espelhada da página vizinha | Não |
| Palatino 9 | idem | 1929×2943 (**inteiro**) | 1929×2943 | idem | 12,2% | 57% | texto, moldura, capitular "Q" (binarizada) | página inteira, capitular com tons | Não |
| Palatino 10 | idem | 1929×2943 (**inteiro**) | 1929×2943 | idem | 11,0% | 73% | texto e moldura | papel e **a mancha do verso** | Não |
| Palatino 57 | idem | 643×981, ~133 DPI (1/3) | 1929×2943, ~400 DPI | idem | 8,2% | 52% | texto, moldura, floreios | papel em baixa resolução | Não |
| Opus Majus 3 | Internet Archive PDF 1.4.24 (Scribe 6.7) | 2874×4623, ~500 DPI (**inteiro**) | 2874×4623 | SMask JBIG2 | 2,1% | 80% | letras **vermelhas e pretas, com a cor**, e o emblema | papel, **carimbo**, tique de lápis, fantasmas | Não |
| Opus Majus 11 | idem | 958×1541, ~167 DPI (1/3) | 2874×4623, ~500 DPI | idem | 6,9% | 94% | texto | papel | Não |
| Opus Majus 20 | idem | 921×1507, ~167 DPI (1/3) | 2765×4525, ~500 DPI | idem | 6,9% | **2%** | legenda e **os pontinhos escuros da foto** | **a foto com todos os tons**, em baixa resolução | Não, mas é o caso perigoso: sem o fundo a foto vira pontilhado |
| Opus Majus 165 | idem | 899×1489 (1/3) | 2699×4470 | idem | 6,5% | 88% | texto e os dois diagramas | papel | Não |
| Opus Majus 256 | idem | 1367×1152 (1/3) | 4103×3458 | idem | 5,6% | 21% | a tabela inteira (fios e números) | papel, marca da dobra, fantasmas | Não |
| Rhetorica 18 | "Recoded by LuraDocument PDF v2.28", criador "Digitized by the Internet Archive" | 784×1176, ~133 DPI (1/3) | 2352×3528, ~400 DPI | SMask JBIG2 | 10,1% | 84% | texto, notas de margem, fios | papel, verso, fantasmas | Não |
| Rhetorica 73 | idem | 784×1176 (1/3) | 2352×3528 | idem | 8,7% | 66% | esquema com chaves e os dois ornamentos | papel com **grande mancha d'água** | Não |
| Siebmacher 7 | produtor "Samsung Electronics" | 1109×856, ~200 DPI (1/3) | 3325×2568, ~600 DPI | **/Mask de estêncil** (ImageMask) JBIG2, não SMask | 14,3% | 40% | texto, **moldura ornamental**, borda escura da folha | papel | Não |
| Siebmacher 9 | idem | 1108×856 (1/3) | 3324×2567 | idem | 15,9% | 24% | idem | papel | Não |

Em todas: o texto invisível usa modo de desenho 3 ("não pintar"), com a fonte `GlyphLessFont` nos PDFs do archive-pdf-tools e `Courier` nos LuraDocument. No Siebmacher esse texto é ilegível (OCR ruim de Fraktur), mas as caixas de linha estão no lugar.

### O livro inteiro (só a lista de imagens, sem decodificar)

| Livro | Páginas | Montagem |
|---|---|---|
| Opus Majus | 450 | todas com fundo + cima com máscara; **fundo inteiro nas p. 1–10 e 447–450**, 1/3 da resolução nas outras 436 |
| Palatino | 134 | igual; **fundo inteiro nas p. 1–10 e 131–134**, 1/3 nas outras 120 |
| Rhetorica | 446 | todas com fundo em 1/3 + cima com máscara |
| Siebmacher | 134 | todas com fundo em 1/3 + cima com máscara de estêncil |
| Graduale, Marial, Escola, Boécio | 750, 907, 199, 50 | uma imagem por página, sem camadas |
| Livro de Horas | 191 | 189 com uma imagem; as p. 1 e 2 têm 4 imagens, 2 com máscara (não olhei o que é) |

Olhando as camadas lado a lado (fundo, máscara, só a camada de cima): Palatino 5, 7, 9, 10 e 57, Opus 3, 20 e 256, Rhetorica 18 e 73 e Siebmacher 9. As imagens ficaram na pasta temporária; qualquer uma se refaz pelo método da seção 8.

---

## 4. Como o Internet Archive monta as camadas (lido no código)

Repositório `internetarchive/archive-pdf-tools`, ramo `master`, lido em 28/09/2026. Licença **AGPL-3.0** para todo o código, menos `internetarchivepdf/pdfrenderer.py` (Apache-2.0).

**O que o README diz:**
- A camada de cima deve ter "todos os glifos/texto da página, **e também as linhas e bordas de desenhos e imagens**"; o fundo fica com "o que não interessa" e pode ser reduzido.
- No PDF: "a imagem de fundo é inserida na página, **seguida** da imagem de cima, que usa a máscara como canal alfa".
- Sem arquivo hOCR (o resultado do OCR) não há recompressão.

**O que o código faz** (`internetarchivepdf/mrc.py`, função `create_mrc_hocr_components`, e `recode.py`, função `insert_images_mrc`):
1. **Máscara das linhas** (`create_hocr_mask`): para cada linha do hOCR, pula a linha se ela estiver vazia ou se a confiança média das palavras for menor que 20. Dentro da caixa da linha, binariza com Sauvola (janela = DPI/4, k = 0,1), testa a linha normal e invertida e fica com a mais limpa.
2. **Máscara da página inteira** (`create_threshold_mask`): com `MIX_THRESHOLD = True`, soma à máscara uma binarização Sauvola **da página toda** (k = 0,34, janela = DPI/4), depois de um borrão leve se a imagem for ruidosa. **É aqui que moldura, gravura e pontinhos de foto entram na camada de cima.**
3. Limpeza de pontinhos da máscara (padrão `fast`).
4. **Camada de cima** (`optimise_rgb2`): a imagem original em que os pixels **fora** da máscara são preenchidos com a cor dos vizinhos de tinta (para comprimir melhor). Por isso a cor da camada de cima fora da máscara é lixo (no Siebmacher aparecem listras). Ela só vale onde a máscara é 1.
5. **Fundo** (`optimise_rgb2` com a máscara invertida): os pixels de tinta são preenchidos com a cor do papel em volta, e depois o fundo é reduzido pelo fator `--bg-downsample` (nos nossos livros, 3). Esse preenchimento não é perfeito: sobram letras "fantasma" claras (medido: no Palatino 5, o fundo sob a tinta tem cinza 147 contra 199 do papel em volta).
6. **Páginas HQ** (`--hq-pages`, na linha de comando `bin/recode_pdf`): as páginas listadas **não têm o fundo reduzido** e usam compressão mais fina. É só uma lista de números de página. Nos nossos dois livros ela foi "10 primeiras e 4 últimas" (deduzido pela contagem acima).
7. A página recebe o fundo (`overlay=False`) e depois a camada de cima com a máscara (`mask=...`, JBIG2 feito pelo `jbig2enc`).

Os PDFs "LuraDocument" (Rhetorica) e o "Samsung Electronics" (Siebmacher) vêm do programa comercial de compressão que o Internet Archive usava antes. O código não é aberto, mas o **resultado tem o mesmo desenho**: fundo em 1/3 embaixo, página inteira colorida por cima com máscara JBIG2. A única diferença que importa para o programa: o Siebmacher usa **máscara de estêncil** (`/Mask` apontando para uma `ImageMask`), e não `SMask`.

---

## 5. Como o programa reconhece sozinho

### 5.1 "Este PDF tem camadas" (sem decodificar nada, milissegundos por página)

Para cada página, com PyMuPDF (`page.get_images(full=True)` e `page.get_image_info(xrefs=True)`):

- há **exatamente duas imagens** e as duas cobrem a página inteira (a caixa de cada uma é a página, com folga de ~1%);
- a **primeira desenhada não tem máscara** (fundo); a **segunda tem** (camada de cima). A ordem se lê no conteúdo da página (os operadores `Do`) ou na ordem de `get_image_info`;
- a máscara tem **1 bit**: `SMask` com `BitsPerComponent 1` ou `/Mask` para uma `ImageMask true`; nos 4 livros ela é sempre `JBIG2Decode`. O PyMuPDF devolve o número da máscara no segundo campo de `get_images` nos dois casos (conferido nas 14 páginas);
- a camada de cima tem **a mesma largura ou mais** que o fundo (medido: igual nas páginas HQ, 3× nas outras).

Pistas que ajudam mas não podem ser obrigatórias: produtor/criador com "Internet Archive" ou "LuraDocument" (o Siebmacher diz "Samsung Electronics" e tem o mesmo desenho) e texto invisível (modo 3).

Casos que o programa deve tratar como "sem camadas" e seguir pelo caminho normal: uma imagem só; uma imagem só de 1 bit (página já em preto e branco); qualquer outra combinação.

### 5.2 "Esta página tem texto na camada de cima"

Decodificar **só a máscara** (JBIG2 de 1 bit, rápido) e contar a tinta: nas 14 páginas ela vai de 2,1% a 15,9% da página. Um limite prático é "tinta em cima acima de ~0,2% da página" (dedução: página sem nada teria perto de 0%). Como segundo sinal, o texto invisível: tem pelo menos uma linha. As 14 páginas passam nos dois.

Atenção ao valor dos pixels: nas duas formas de máscara o PyMuPDF devolve **255 onde a camada de cima aparece** (conferido olhando as imagens; no estêncil do Siebmacher a leitura "0 pinta" da especificação deu o contrário do que se vê).

### 5.3 Tirar o fundo

Na resolução da camada de cima (400 a 600 DPI): começar de uma página branca e copiar a cor da camada de cima **só onde a máscara é 255**. Nunca usar a cor da camada de cima fora da máscara (item 4 da seção 4).

Resultado esperado, visto nas imagens: papel branco; letras com a cor que tinham (Opus 3 vermelho); somem a mancha do verso (Palatino 10), a escrita da página vizinha (Palatino 7, sobram pontinhos), o carimbo e o tique de lápis (Opus 3), a dobra (Opus 256) e a mancha d'água (Rhetorica 73). A moldura e a borda escura da folha continuam, porque estão em cima (Siebmacher: a borda escura tem de sair pelo corte).

---

## 6. As páginas "com tudo embaixo" e o que fazer

**O que foi medido:** nenhuma das 14 páginas tem a camada de cima vazia. O caso real é outro: **figura cujos tons só existem no fundo**. Na foto do Opus 20 a camada de cima tem só os pontinhos escuros (2% da tinta cai dentro das linhas do OCR); os meios-tons estão no fundo, em ~167 DPI. No retrato do Palatino 5 os traços sobem binarizados e os tons ficam no fundo.

**Duas tentativas de achar isso só pelo fundo, e as duas erraram** (medido nas 14 páginas):
- "fundo escuro fora da tinta": a mancha d'água da Rhetorica 73 dá 32% da página, mais que a foto do Opus 20 (9,5%);
- "fundo com textura fora da tinta": o Palatino 9 (fantasmas e verso num fundo inteiro) dá 11%, a foto do Opus 20 dá 0,3%.

É a mesma conclusão do `relatorios/melhorias.md` (tentativa 9): medidas de pixel se cruzam entre foto e não-foto.

**Recomendação (dedução):**
1. A decisão "aqui é figura" vem do **seletor de gravura** (item 1.2, o do ScanTailor). Dentro da zona de figura, manter a página **como o PDF desenha** (fundo + cima, o que dá a foto com tons). Fora dela, só a camada de cima no branco. É exatamente a junção do item 1.5; o 1.1 não deve inventar um terceiro detector.
2. Enquanto o 1.2 não existe, o 1.1 pode usar o detector que o programa já tem (`core/detectar_regioes.py`) para as zonas de figura, e **avisar na conferência** que as figuras dependem dele.
3. Mostrar ao Samuel as duas versões do retrato do Palatino 5: "só a camada de cima" (papel dentro do oval fica branco, como pede a regra de 28/09, mas os traços saem binarizados) e "fundo + cima na zona da gravura" (tons intactos, papel do oval amarelado, a branquear no 1.5). A regra "o desenho também saia perfeito" pede a segunda; a regra "papel dentro da gravura branco" pede um passo a mais no 1.5.
4. **Botão de ligar e desligar** (regra 8): "Usar as camadas do PDF" ligado sozinho quando a seção 5.1 reconhece o PDF.

**Bônus para o 1.3 e o 1.4 (medido):** o texto invisível desses PDFs já traz as **caixas de linha** do OCR do Internet Archive. Nas páginas de texto corrido, 84% a 99% da tinta de cima cai dentro delas. Para esses livros, o 1.4 tem caixas de linha sem rodar OCR nenhum. Serve também de referência gratuita na comparação do 1.3 (com cuidado: foi feito por um OCR, não é gabarito humano).

---

## 7. Correções ao `TESTE-SCANTAILOR-MISTO.md` (para a gerente decidir se atualiza)

1. **"nas páginas de gravura (5, 7, 9, 10), o Archive deixou a página inteira na camada de baixo".** O fundo inteiro nessas páginas vem da lista de páginas HQ (as 10 primeiras e as 4 últimas do livro), não da gravura: a 7 e a 10 são só texto. E a camada de cima dessas páginas também tem o texto (e, na 5 e na 9, a gravura binarizada).
2. **"O segredo é o passo 1: mancha fora das linhas de texto nunca entra na máscara".** No código atual (`MIX_THRESHOLD = True`) entra, sim, tudo o que a binarização da página inteira pega: moldura, gravura, pontinhos de foto, fios de tabela, borda da folha. Mancha lisa (d'água, amarelado) de fato fica embaixo, porque o Sauvola não a pega. Quem quiser "só texto" na máscara (o item 1.4) tem de usar **só o passo 1** (linhas do OCR), e não copiar a máscara do Archive inteira.

## 8. Método (para refazer)

Tudo com o `.venv` do projeto, só leitura: `fitz.open(pdf)`; `page.get_images(full=True)` (número da imagem, número da máscara, tamanho, filtro); `doc.xref_get_key(xref, "ImageMask"/"Mask"/"Filter")`; `page.read_contents()` para a ordem dos `Do`; `page.get_image_info(xrefs=True)` para a caixa de cada imagem; `fitz.Pixmap(doc, xref)` para decodificar máscara e fundo; `page.get_text("dict")` para as linhas do texto invisível. Tempo total das medições: poucos segundos no PC do Samuel.

## 9. O que ficou em aberto

- **Por que "10 primeiras e 4 últimas"** está deduzido pela contagem nos dois livros, não lido numa configuração do Internet Archive (o `--hq-pages` não tem valor padrão no código; quem chama escolhe).
- Não olhei as p. 1 e 2 do Livro de Horas (4 imagens, 2 com máscara).
- O limite "tinta em cima > 0,2%" é sugestão, não medida em página vazia de verdade.
- Outros livros do Internet Archive podem ter camada de cima em cinza (DeviceGray) ou página só de 1 bit; a regra da seção 5.1 cobre, mas só foi vista em cor.
- Os tons de figura no fundo das páginas comuns estão em ~133 a 200 DPI. O Internet Archive costuma publicar também os scans originais em resolução cheia (os arquivos JPEG 2000 de cada livro); isso não foi conferido e ficaria fora do programa (sugestão para a Lista de espera, se o Samuel quiser).

## 10. Links consultados (28/09/2026)

- https://github.com/internetarchive/archive-pdf-tools (README, licença)
- https://raw.githubusercontent.com/internetarchive/archive-pdf-tools/master/internetarchivepdf/mrc.py
- https://raw.githubusercontent.com/internetarchive/archive-pdf-tools/master/internetarchivepdf/recode.py
- https://raw.githubusercontent.com/internetarchive/archive-pdf-tools/master/bin/recode_pdf (opção `--hq-pages`)
- https://raw.githubusercontent.com/internetarchive/archive-pdf-tools/master/internetarchivepdf/pdfhacks.py (`fast_insert_image`)
- https://raw.githubusercontent.com/internetarchive/archive-pdf-tools/master/tools/mrcview
- https://archive-pdf-tools.readthedocs.io/
- https://en.wikipedia.org/wiki/LuraTech (LuraDocument, compressão MRC comercial)
- Arquivos locais: `gabarito/paginas/*.pdf`, `gabarito/lista.json` e os livros originais listados nela (só leitura).
