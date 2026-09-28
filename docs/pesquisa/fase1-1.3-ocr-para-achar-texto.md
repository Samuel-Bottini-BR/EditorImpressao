# Fase 1.3: OCRs já treinados, só para ACHAR onde está o texto

**Data:** 28/09/2026 · **Quem:** agente pesquisador · **Pedido:** gerente, item 1.3 do Plano Definitivo (comparar Tesseract, com os modelos normais e os históricos da UB Mannheim, docTR, PaddleOCR e Kraken; ficam os 2 melhores). O uso é o do item 1.4: **caixas de linha** para fazer a máscara de tinta como o Internet Archive. Transcrever fica para a Fase 7.

Nada foi instalado nem rodado; o `.venv` do projeto não foi tocado. As versões e a compatibilidade com Python 3.14 vêm da página de cada pacote no PyPI e dos repositórios, lidas em 28/09/2026.

---

## 1. A resposta em cinco frases

1. Os quatro têm um **detector de texto que só aponta** (devolve caixas ou contornos de linha ou palavra, nunca pixel nem texto inventado). Os quatro programas são **Apache-2.0**; dos modelos, `tessdata` e o `blla` do Kraken são Apache-2.0, o `frak2021` da UB Mannheim é CC0, e o `GT4HistOCR` da UB Mannheim e os pesos do docTR e do PP-OCR não têm licença própria escrita que eu tenha achado.
2. **No Windows com Python 3.14** entram direto: Tesseract (programa à parte da UB Mannheim, 5.5.3 de 24/07/2026, chamado pelo `pytesseract`) e o docTR (pacote com `torch`, ou a versão leve **OnnxTR** sobre o `onnxruntime` que o programa já usa). **PaddleOCR não instala no 3.14** (o `paddlepaddle` só tem Windows até o 3.13); os mesmos modelos PP-OCR rodam no 3.14 pelo **RapidOCR** (também sobre `onnxruntime`). **Kraken não roda no Windows nem no 3.14**: só no WSL2 (Linux), com Python até 3.13.
3. Todos rodam só no processador. Pelas fontes, em processadores mais fortes que o do notebook do Kaique, a detecção custa de décimos de segundo (PP-OCRv5 móvel) a ~1 s por página (docTR, Tesseract completo); o Kraken não tem número em processador publicado, e o único achado (43 s por página, com GPU de Mac) indica que é o mais lento.
4. A comparação do 1.3 deve medir **duas coisas nas páginas do gabarito**: quanto da tinta de texto fica dentro das caixas (tem de ser quase tudo) e quanto da tinta de gravura, iluminura, moldura e foto cai dentro de caixas (tem de ser quase nada, por causa das regras do Samuel de 28/09), além do tempo por página.
5. **Recomendação:** testar Tesseract (com e sem o filtro de confiança do Internet Archive, e com os modelos da UB Mannheim), docTR pelo OnnxTR, PP-OCRv5 pelo RapidOCR e Kraken pelo WSL, mais as linhas que já vêm no PDF do Internet Archive como referência de graça; a minha aposta (dedução) é que ficam o Tesseract e um dos dois detectores neurais que rodam no 3.14, porque o Kraken exigiria WSL no notebook.

## 2. Tabela

| O que é | Licença | Instala aqui (Windows, Python 3.14)? | Roda no notebook do Kaique? | Devolve caixas de linha? | Só aponta? |
|---|---|---|---|---|---|
| **Tesseract 5.5.3** (programa) + `pytesseract` 0.3.13 | Apache-2.0 (Leptonica: BSD-2); `pytesseract` Apache-2.0 | Sim: instalador de 64 bits da UB Mannheim (5.5.3.20260724); `pytesseract` é Python puro (a página lista até 3.12, dedução: funciona no 3.14). `tesserocr` **não** tem pacote pronto para Windows | Sim (processador) | Sim: hOCR, ALTO, PAGE e TSV com linha e palavra | Sim para a divisão em linhas; o reconhecedor produz texto, mas no 1.3 só usamos caixas e confiança |
| Modelos `tessdata_best` / `tessdata_fast` (`lat`, `ita`, `fra`, `por`, `deu`) | Apache-2.0 | Sim (arquivos) | Sim | (os mesmos do Tesseract) | idem |
| Modelos UB Mannheim: `frak2021` | CC0 (registro Zenodo 10125246, Stefan Weil) | Sim (arquivo) | Sim | idem | idem |
| Modelos UB Mannheim: `GT4HistOCR`, `german_print` | **licença não escrita na página de download** (os dados GT4HistOCR são CC-BY 4.0) | Sim (arquivo) | Sim | idem | idem |
| **docTR** 1.1.0 (`python-doctr`) | Apache-2.0 | Sim: Python puro, lista o 3.14; precisa de `torch` (2.14.0 tem pacote Windows para 3.14) e `torchvision`, que são grandes | Sim (processador) | Palavras (a detecção acha "sequências de caracteres sem interrupção"); linhas saem juntando palavras, e há exportação hOCR | Sim (modelos DB, LinkNet, FAST: mapa de "aqui tem texto" → caixas) |
| **OnnxTR** 0.9.0 (docTR sobre `onnxruntime`) | Apache-2.0 | Provável: pede Python ≥ 3.11 (a página lista até 3.13); o `onnxruntime` já está no `.venv` (1.28) e tem pacote para 3.14. Conferir | Sim, e é o mais leve do docTR | idem docTR (`detection_predictor` existe) | Sim |
| **PaddleOCR** 3.7.0 (`paddlepaddle` 3.3.1) | Apache-2.0 | **Não**: o `paddlepaddle` para Windows só tem 3.9 a 3.13. Caminho: um Python 3.13 à parte só para o teste | Só com o Python à parte | Polígono de 4 pontos por região de texto (`dt_polys`) com nota (`dt_scores`); sem hOCR | Sim (DB) |
| **RapidOCR** 3.9.2 (modelos PP-OCR sobre `onnxruntime`) | Apache-2.0 (o README diz que os modelos são da Baidu) | Provável: Python puro, pede ≥ 3.8 (a página lista até 3.13); dependências com pacote 3.14. Conferir | Sim | Polígonos por região; dá para ligar só a detecção (`use_det` sem `use_cls`/`use_rec`) | Sim |
| **Kraken** 7.1.1 + modelo `blla` padrão | Apache-2.0 (programa e modelo, Zenodo 14602569) | **Não**: "roda em Linux ou macOS", Python 3.10 a 3.13 (o pacote recusa o 3.14). Caminho: WSL2 + Ubuntu + Python 3.13. O PC do Samuel tem o WSL, mas **nenhuma distribuição instalada** | Só com WSL2 instalado lá (pesado para o Kaique) | Sim: linha de base + contorno de cada linha; ALTO, PageXML, abbyyXML, hOCR | Sim (segmentação treinada em manuscrito e impresso) |

---

## 3. O que foi lido na fonte

### Tesseract
- README do `tesseract-ocr/tesseract`: o motor LSTM do Tesseract 4 "é focado em reconhecer **linhas**"; saídas: texto, **hOCR, PDF, PDF só de texto invisível, TSV, ALTO e PAGE**; Apache-2.0. Última versão: **5.5.3 (24/07/2026)**.
- Wiki da UB Mannheim: instalador `tesseract-ocr-w64-setup-5.5.3.20260724.exe` (64 bits).
- Documentação da UB Mannheim para Windows: para Fraktur, os modelos **`frak2021`** e **`GT4HistOCR`**; baixar de `ub-backup.bib.uni-mannheim.de/~stweil/tesstrain/` e preferir `tessdata_fast`, porque "os resultados são equivalentes e o reconhecimento é bem mais rápido". Na pasta há `Fraktur_5000000`, `GT4HistOCR`, `frak2021`, `german_print`, `German-Konzilsprotokolle` e também pastas `kraken` e `calamari`.
- Zenodo 10125246 (o link do `OCR-PESQUISA.md`): é o `frak2021` (versões "best" e "fast"), **CC0**; "treinado principalmente com alemão e latim, serve também para inglês, francês e outras línguas da Europa Ocidental".
- `archive-pdf-tools` (ver `fase1-1.1-camadas-internet-archive.md`): o Internet Archive usa as linhas do hOCR e **descarta linha com confiança média das palavras menor que 20**. É o filtro que tira "linha" achada dentro de gravura.
- PyPI: `pytesseract` 0.3.13 (Python puro, ≥ 3.8); `tesserocr` 2.11.0 só com pacotes para macOS e Linux.

### docTR e OnnxTR
- Documentação do docTR ("Choosing the right model"): `detection_predictor` para "só as caixas das palavras, sem reconhecer"; modelos `db_resnet50`, `db_mobilenet_v3_large`, `linknet_resnet18/34/50`, `fast_tiny/small/base`; exportação `export_as_xml` em formato hOCR (`ocr_line`, `ocrx_word`). Entrada dos modelos de detecção: **1024×1024**.
- Tempo na detecção (Intel i7-11800H, lote de 1, 1024×1024): `db_resnet50` 1,1 s; `db_mobilenet_v3_large` 0,5 s; `linknet_resnet18` 0,6 s; `fast_base` 0,8 s (0,5 s reparametrizado).
- PyPI: `python-doctr` 1.1.0 (21/08/2026) pede `torch` ≥ 2.0 e lista Python 3.11 a 3.14; `onnxtr` 0.9.0 (24/08/2026) pede ≥ 3.11, instala com `pip install "onnxtr[cpu]"`, tem modelos de 8 bits para processador e um `detection_predictor`.
- README do OnnxTR, OCR completo em processador (i7-14700K): docTR ~1,29 s/página (FUNSD) e ~0,60 (CORD); OnnxTR ~0,57 e ~0,25; OnnxTR 8 bits ~0,38 e ~0,14; **PyTesseract ~0,50 e ~0,52**; PaddleOCR 2.7.3 sem classificador ~1,27 e ~0,38.

### PaddleOCR e RapidOCR
- Documentação do PaddleOCR 3.x (módulo de detecção de texto, classe `TextDetection`; saída `dt_polys` e `dt_scores`). Tabela (Xeon Gold 6271C, 8 linhas de execução, FP32): **PP-OCRv5_server_det** 383 ms no processador, Hmean 83,8%; **PP-OCRv5_mobile_det** 57,8 / 28,2 ms (normal / alto desempenho), 79,0%, 4,7 MB; PP-OCRv4_server_det 586 / 490 ms.
- PyPI: `paddleocr` 3.7.0 depende do `paddlex`; `paddlepaddle` 3.3.1 tem pacote para Windows só de cp39 a cp313.
- RapidOCR: Apache-2.0; "os direitos dos modelos de OCR são da Baidu"; tem página "Usar os modelos PP-OCRv5". No código atual (`python/rapidocr/main.py` e `config.yaml`): `use_det`, `use_cls`, `use_rec` ligam e desligam cada etapa; o motor padrão é `onnxruntime`; a página é limitada por `max_side_len: 2000` e `limit_side_len: 736` (tem de ser ajustado para página de livro, senão letra pequena some; dedução). A configuração do ramo principal já cita PP-OCRv6 como detector padrão (não conferi se a versão 3.9.2 do PyPI é igual).

### Kraken
- README (`mittagessen/kraken`, Apache-2.0): "roda em Linux ou Mac OS X"; Python 3.10 a 3.13; `kraken -i imagem.tif linhas.json segment -bl` para só segmentar; saídas ALTO, PageXML, abbyyXML e hOCR.
- PyPI: `kraken` 7.1.1 (04/09/2026) pede Python **< 3.14** e fixa versões antigas de `scipy` (~1.15.3) e `scikit-image` (~0.25.2), além de `torch`, `lightning`, `coremltools`.
- Documentação da API (5.2): a segmentação roda no processador por padrão; "como a maior parte do trabalho é pós-processamento, o ganho com placa de vídeo deve ser modesto".
- Modelo `blla` padrão (Zenodo 14602569, Apache-2.0): treinado no conjunto cBAD 2019; limitações escritas: escrita inclinada ou vertical, **"escrita embutida em decoração"** (a iluminura da Horas 11 é exatamente isso) e linhas muito juntas, que se fundem.
- Tempo: não achei número em processador. Uma medição de terceiros (issue 142 do `kkkamur07/greekOCR`) dá 43 s por página com o `blla` num Apple M4 usando a GPU.

---

## 4. Tempo no notebook do Kaique (dedução, a medir)

As fontes mediram em máquinas mais fortes (i7-14700K, i7-11800H, Xeon de 8 linhas) e, no caso do OnnxTR, em páginas pequenas (formulários do FUNSD). O i5-1235U tem 2 núcleos rápidos e 8 econômicos, a 15 W. Estimativa grosseira, **só para planejar**:

| Detector | Por página no notebook (dedução) |
|---|---|
| PP-OCRv5 móvel (RapidOCR) | ~0,2 a 0,5 s |
| docTR / OnnxTR (`db_resnet50`, `fast_base`) | ~1 a 3 s |
| PP-OCRv5 servidor (RapidOCR) | ~1 a 2 s |
| Tesseract completo (hOCR), página de 300 DPI | ~2 a 6 s (cresce com o número de pixels e de linhas) |
| Kraken `blla` (WSL) | dezenas de segundos (sem fonte em processador) |

Isso roda **na hora de processar**, não na prévia. A regra 6 (nada pode ficar mais lento) pede que a detecção de linhas não entre no caminho da prévia, ou entre em baixa resolução e em segundo plano.

---

## 5. Como montar a comparação medida do 1.3

### 5.1 Páginas

- As 16 da lista `fase1` do `gabarito/lista.json` (inclui as obrigatórias de 28/09: Palatino 5, Escola 35, Horas 11, 13, 26 e 27, Opus Majus 20).
- Mais três que testam o tipo de letra: **Rhetorica 18** (latim impresso com notas de margem), **Siebmacher 9** (Fraktur com moldura ornamental) e **Palatino 57** (cursiva xilográfica com floreios).
- Sempre **depois do corte e do endireitamento do programa**, a 300 DPI: o `OCR-PESQUISA.md` mediu que a moldura estraga o OCR da página inteira.

### 5.2 Gabarito (o que é texto e o que não pode ser)

Seguindo o jeito do `avaliar_selecao.py` (frases que uma pessoa assinaria, sem desenhar pixel a pixel), para cada página, retângulos em fração da página, como o campo `detalhe` da `lista.json`:
- **"tem de ser texto"**: blocos de texto corrido, títulos coloridos, legendas, número de página, reclamo, notas de margem (cada item pequeno com o seu retângulo, para contar o que se perde);
- **"não pode ter linha"**: retrato, capitular, foto, iluminura, moldura dourada, anjo, carimbo, mancha d'água, mancha do verso.

Quem desenha: o agente propõe olhando a página e o Samuel confere na página de conferência (uns 10 minutos). Nunca a partir do que um OCR devolveu (é o erro de 30/07 contado no `avaliar_selecao.py`). As linhas do texto invisível dos PDFs do Internet Archive servem só de terceira opinião, porque também saíram de um OCR.

### 5.3 Medidas (pixel de tinta, que é o que o 1.4 usa)

Tinta = binarização Sauvola da página (a mesma do Internet Archive: janela DPI/4, k 0,34). As caixas de cada detector são alargadas em ~15% da altura da linha, para pegar hastes e pernas das letras.

1. **Texto achado:** dentro de "tem de ser texto", quanto da tinta cai em alguma caixa. Meta: **≥ 98%**.
2. **Figura tomada por texto:** dentro de "não pode ter linha", quanto da tinta cai em alguma caixa. Meta: **≤ 1%**. Nas páginas obrigatórias (retrato, foto, iluminura, moldura, anjo) isto **reprova sozinho**, porque viola as regras de 28/09 (gravura, iluminura e moldura intactas).
3. **Itens pequenos perdidos:** quantos números de página, reclamos e notas ficaram sem caixa.
4. **Tempo:** mediana de 3 rodadas por página no PC do Samuel (Ryzen 7 5800H), anotando quantas linhas de execução; e uma rodada no notebook do Kaique quando ele estiver disponível (0.6).
5. Opcional, para comparar com a literatura: acerto por linha com interseção sobre união ≥ 0,5 (precisão, revocação, F1) nas páginas de texto corrido.

### 5.4 O que rodar

| Código | Configuração |
|---|---|
| T1 | Tesseract 5.5.3, `--psm 3`, hOCR, modelo `tessdata_best` do idioma do livro (`lat`, `ita`, `fra`, `por`, `deu`) |
| T2 | T1 + o filtro do Internet Archive (descarta linha com confiança média < 20) |
| T3 | T2 com os modelos da UB Mannheim (`frak2021`; `GT4HistOCR`) em vez do modelo do idioma |
| D1, D2 | OnnxTR, só detecção: `db_resnet50` e `fast_base` (palavras juntadas em linhas) |
| P1, P2 | RapidOCR, só detecção: PP-OCRv5 servidor e móvel, com o limite de lado ajustado para a página inteira |
| K1 | Kraken 7.1.1 `segment -bl` com o `blla` padrão, no WSL2 |
| R0 | Referência de graça: as linhas do texto invisível que já vêm no PDF (só Palatino e Opus Majus) |

Opcional, para tirar dúvida: o docTR original (com `torch`) contra o OnnxTR, e o PaddleOCR nativo num Python 3.13 à parte contra o RapidOCR, numa página só, para confirmar que dão o mesmo.

Dedução importante para ler o resultado: no Tesseract, a divisão da página em linhas é a análise de página clássica, e o modelo LSTM só reconhece o que está dentro de cada linha. Então T1 e T3 devem achar **as mesmas linhas**; o modelo muda a **confiança**, e é ela que o filtro T2/T3 usa para jogar fora "linha" dentro de gravura.

### 5.5 Onde e como, sem mexer no programa

- Tudo num ambiente separado (por exemplo `D:\programas\ocr-teste\`), **nunca no `.venv` do projeto** sem a gerente pedir; o Kraken no WSL2 (pede instalar o Ubuntu no PC do Samuel). O Python 3.13 à parte só para o teste opcional do PaddleOCR nativo; o programa continua no 3.14.
- Cada detector escreve o mesmo formato (página, lista de contornos, nota, tempo); um script só calcula as medidas e desenha as caixas por cima da página, e o `conferencia.py --pasta-depois` mostra as sobreposições lado a lado para o Samuel.

### 5.6 Critério para escolher os 2

1. **Cai fora** quem passar de 1% de "figura tomada por texto" em qualquer página obrigatória, a menos que a sua própria nota ou confiança resolva (como o filtro T2).
2. Entre os que sobram, ganha quem tiver **mais texto achado** na média, e depois quem for **mais rápido** no notebook.
3. Dos dois escolhidos, preferir **erros diferentes** (por exemplo um clássico e um neural), porque o 1.5 vai juntar os detectores.
4. Fica fora do programa quem exigir WSL ou um segundo Python no notebook do Kaique, a menos que ganhe com folga.

## 6. Recomendação

Montar a comparação da seção 5 com Tesseract (T1 a T3), OnnxTR (D1, D2), RapidOCR com PP-OCRv5 (P1, P2) e Kraken (K1), com R0 como referência. **Aposta (dedução, não medida):** o Tesseract com o filtro de confiança (é o que o Internet Archive usa em milhões de livros e lida bem com página de livro grande) e um detector neural que roda no 3.14 sem programa extra (PP-OCRv5 pelo RapidOCR ou docTR pelo OnnxTR). O Kraken é o único treinado de fábrica em manuscrito e documento histórico e merece estar na comparação, mas só entraria no programa se ganhasse com folga, porque exige WSL e é o mais lento.

Nos PDFs do Internet Archive (Palatino, Opus Majus, Rhetorica, Siebmacher) o 1.4 pode usar as linhas que já vêm no PDF, sem rodar OCR (ver o documento do 1.1).

## 7. O que ficou em aberto

- **Nada foi instalado nem medido:** a compatibilidade com o 3.14 do OnnxTR, do RapidOCR e do `pytesseract` está deduzida das páginas do PyPI (pedem Python ≥ 3.8 ou ≥ 3.11, as dependências têm pacote para 3.14), e o tempo por página no notebook é estimativa.
- **Licença dos modelos `GT4HistOCR` e `german_print` da UB Mannheim** não está escrita na página de download (o `frak2021` é CC0).
- **Licença dos pesos pré-treinados** do docTR/OnnxTR e dos modelos PP-OCR: os repositórios são Apache-2.0 e o RapidOCR diz que os modelos são da Baidu; não achei licença separada para os pesos.
- **Tempo do Kraken em processador**: nenhuma fonte achada.
- **Detectores neurais reduzem a página** (docTR a 1024 px; RapidOCR a 2000 px por padrão): número pequeno de tabela (Opus 256) pode sumir. A comparação tem de anotar a resolução usada e testar em pedaços se preciso.
- O gabarito de retângulos (5.2) precisa do olho do Samuel antes de valer.

## 8. Links consultados (28/09/2026)

- https://github.com/tesseract-ocr/tesseract (README, licença, versões)
- https://github.com/UB-Mannheim/tesseract/wiki (instalador 5.5.3.20260724)
- https://ub-mannheim.github.io/Tesseract_Dokumentation/Tesseract_Doku_Windows.html
- https://ub-backup.bib.uni-mannheim.de/~stweil/tesstrain/ (pastas `frak2021`, `GT4HistOCR`, `german_print`)
- https://zenodo.org/records/10125246 (frak2021, CC0)
- https://github.com/tesseract-ocr/tessdata_best e https://github.com/tesseract-ocr/tessdata_fast (Apache-2.0)
- https://pypi.org/project/pytesseract/ · https://pypi.org/project/tesserocr/
- https://mindee.github.io/doctr/latest/using_doctr/using_models.html e https://github.com/mindee/doctr (`docs/source/using_doctr/using_models.rst`)
- https://pypi.org/project/python-doctr/ · https://pypi.org/project/onnxtr/ · https://github.com/felixdittrich92/OnnxTR (README, `onnxtr/models/detection/zoo.py`)
- http://www.paddleocr.ai/latest/en/version3.x/module_usage/text_detection.html
- https://pypi.org/project/paddleocr/ · https://pypi.org/project/paddlepaddle/
- https://rapidai.github.io/RapidOCRDocs/main/ · https://github.com/RapidAI/RapidOCR (`python/rapidocr/main.py`, `config.yaml`) · https://pypi.org/project/rapidocr/
- https://github.com/mittagessen/kraken (README) · https://kraken.re/main/getting_started.html · https://kraken.re/5.2/api.html · https://pypi.org/project/kraken/
- https://zenodo.org/records/14602569 (modelo `blla`, Apache-2.0)
- https://github.com/kkkamur07/greekOCR/issues/142 (tempo do `blla` num Apple M4)
- https://pypi.org/project/torch/ · https://pypi.org/project/onnxruntime/ (pacotes para Python 3.14 no Windows)
- Locais: `docs/plano/OCR-PESQUISA.md`, `avaliar_selecao.py` (só o cabeçalho), `gabarito/lista.json`, `requirements.txt`, lista de pacotes do `.venv` (só leitura).
