# Treinar os OCRs e o detector de gravura para um livro: quantas páginas e quanto tempo

**Data:** 29/09/2026 · **Quem:** agente pesquisador · **Pedido:** gerente, a partir das duas linhas de 29/09 na Lista de espera do plano (seção 6): "Anote quantas páginas cada OCR precisa e quanto tempo o treino levaria no notebook do Kaique." Vale para o item 7.2 (treinar os OCRs para transcrever) e para a ideia nova de **ajustar os modelos para um livro só, dentro do programa, em segundo plano**.

**Como ler as marcas:**
- **[medido]** = rodei um treino curto de verdade neste PC (o PC do Samuel: Ryzen 7 5800H, 8 núcleos/16 linhas, GTX 1650 4 GB).
- **[estimativa]** = conta minha a partir do que medi (multiplicar pelo número de páginas, de passadas e pela diferença de processador).
- **[lido]** = está escrito na fonte (links na seção 10).
- **[dedução]** = conclusão minha, não conferida.

**Atenção às medidas:** o verificador rodou testes na mesma máquina durante quase todo o tempo. Os tempos valem como **ordem de grandeza**, não como número final. Os dados de treino foram **falsos de propósito** (a "correção" era a própria leitura do modelo): serviam só para cronometrar, **não medem se o treino melhora a leitura**.

**Onde mexi:** nada em `core/`, `ui/`, `gabarito/`, `.venv` do programa nem no acervo (só li as 22 páginas de `saida_teste/ocr-1.3/imagens/`). Tudo foi instalado em `D:\programas\EditorImpressao-arquivos\ferramentas\treino-ocr-2026-09-29\` (ambientes Python separados, modelos, dados e resultados). O Kraken usou o ambiente `kraken312` da pesquisa de 28/09 (pasta temporária). Nada pediu reinício. Ver a ressalva da seção 8 sobre uma pasta `D:\d` que apaguei.

---

## 1. A resposta em cinco frases

1. **Para transcrever um livro, poucas páginas corrigidas já ajudam:** de **2 a 3 páginas** para começar e **cerca de 10** para um bom resultado (Kraken e reconhecedores do mesmo tipo). Num estudo com manuscritos alemães, 2 páginas baixaram o erro de 6,2% para 3,3% e 32 páginas para 1,7% **[lido]**. Para achar as linhas, o guia da UB Mannheim pede **5 a 10 páginas** corrigidas **[lido]**. O PaddleOCR pede muito mais: **500 imagens** para achar texto e **5.000** para transcrever **[lido]**.
2. **No notebook do Kaique, os ajustes baratos cabem numa tarde, só no processador:** Kraken transcrevendo (10 páginas) leva **uns 45 min a 1¼ h**; Tesseract, **uns 20 a 30 min**; Kraken achando linhas (10 páginas), **1 a 3 horas**; docTR, **35 min a 1¼ h** cada parte; o detector de gravura (DocLayout-YOLO, 20 páginas), **2½ a 4 horas** **[estimativa a partir do medido]**.
3. **Os modelos PP-OCRv6 (no Kraken ou no PaddleOCR) não dão para treinar sem placa de vídeo:** medi **mais de 1 minuto por linha** no Kraken e **1,4 s por palavra** no PaddleOCR, o que daria **dias** no notebook. Na GTX 1650 do Samuel o mesmo treino do Kraken foi **~300 vezes mais rápido** **[medido]**.
4. **A Iris Xe do notebook não ajuda:** nenhum desses programas treina nela no Windows (o PyTorch para placas Intel não inclui a Iris Xe; o DirectML parou em 2024 e não serve para o PyTorch que o Kraken pede; o OpenVINO só roda modelo pronto; o Tesseract não usa placa nenhuma) **[lido + dedução]**. É só o processador.
5. **O modelo treinado volta para a versão leve do programa sem perda**, nos cinco casos que testei: Kraken e docTR para ONNX (diferença de arredondamento), PP-OCR para ONNX (só com o PaddlePaddle 3.1.1: as versões novas quebram o conversor), DocLayout-YOLO para ONNX no **mesmo formato** do `modelos/doclayout.onnx` (caixas idênticas em 6 páginas), e o Tesseract nem precisa converter **[medido]**.

---

## 2. Tabela principal (modelo × uso)

"Páginas" = páginas corrigidas **do próprio livro**, partindo do modelo pronto (ajuste fino). "Tempo" = o treino inteiro no cenário da coluna "cenário", **[estimativa]** feita a partir do tempo **[medido]** por página ou linha (seção 4). Notebook do Kaique = tempo do PC do Samuel (processador) × 1,5 a 2,5 (seção 3). 1 página ≈ 30 linhas ≈ 240 palavras (média das nossas páginas de teste, [dedução]).

| Modelo · uso | Páginas: mínimo que já melhora | Páginas: recomendado | Cenário da conta | PC do Samuel, só processador | PC do Samuel, GTX 1650 | Notebook do Kaique | Base do tempo |
|---|---|---|---|---|---|---|---|
| **Kraken · transcrever** (CATMuS / McCATMuS, rede pequena) | 2 a 3 [lido: UB Mannheim; Reul 2022] | ~10 (TRIDIS); até 32 melhora mais [lido] | 300 linhas × 30 passadas | **~30 min** | **~6 min** | **45 min a 1¼ h** | medido: 0,17–0,23 s por linha por passada (CPU); 0,04 s (GPU) |
| Kraken · transcrever (PP-OCRv6 pequeno do Kraken 7.1) | idem | idem | idem | **~170 horas** (inviável) | **~35 min** | **inviável** (semanas) | medido: 60–70 s por linha (CPU); 0,23 s (GPU) |
| **Kraken · achar linhas** (`blla`) | 5 a 10 [lido: UB Mannheim] | não achei número oficial para ajuste; "menos de umas centenas" para um modelo próprio [lido: Kraken] | 10 páginas × 50 passadas | **45 min a 1 h 10** | **~8 min** | **1 a 3 horas** | medido: 5,3–8 s por página por passada (CPU); ~1 s (GPU) |
| **Tesseract · transcrever** (`lat` do `tessdata_best`) | não achei número oficial; reconhecedor do mesmo tipo melhorou com 60 linhas (2 páginas) [lido: Reul 2017/2018, OCRopus] | ~150 a 1.000 linhas (5 a 30 páginas) [idem] | 9.000 passos (≈ 300 linhas × 30) | **~20 min** | não usa placa (= processador) | **20 a 30 min** | medido: 0,13 s por passo, **um núcleo só** |
| Tesseract · achar linhas | — | — | — | **não treina**: a divisão em linhas é por regras [dedução] | — | — | — |
| **docTR · achar texto** (`fast_base`) | não encontrado | não encontrado | 20 páginas × 10 passadas | **22 a 28 min** | **~8 min** (+4 min na 1ª passada) | **35 min a 1¼ h** | medido: 6,5–8,5 s por página (CPU); 2,2 s (GPU) |
| **docTR · transcrever** (`crnn_vgg16_bn`) | não encontrado | não encontrado | 2.400 palavras (10 páginas) × 10 passadas | **~23 min** | **~2 min** | **35 min a 1 h** | medido: 0,058 s por palavra (CPU); 0,005 s (GPU) |
| **PP-OCR · achar texto** (PP-OCRv6 pequeno, PaddleOCR) | não encontrado | **500 imagens** [lido: PaddleOCR] | 20 páginas × 50 passadas / 500 × 50 | **~2 h** / **~49 h** | não medido | **3 a 5 h** / **3 a 5 dias** | medido: ~7 s por recorte de 640×640 (CPU) |
| **PP-OCR · transcrever** (PP-OCRv6 pequeno, PaddleOCR) | não encontrado | **5.000 imagens** [lido: PaddleOCR] | 5.000 × 20 passadas | **~37 h** | não medido (~6 h, [estimativa] pelo Kraken PP-OCRv6 na GPU) | **2 a 4 dias** (inviável) | medido: 1,3–1,4 s por palavra (CPU) |
| **DocLayout-YOLO · achar gravura** (`modelos/doclayout.onnx`) | não encontrado | não encontrado para ajuste; ≥ 1.500 imagens por classe para treino geral [lido: Ultralytics] | 20 páginas × 50 passadas | **1½ a 1¾ h** | **~50 min** (1 página por vez; 2 não cabem nos 4 GB) | **2½ a 4 h** | medido: 5,5–6 s por página (CPU); 3 s (GPU) |
| MobileSAM · seleção por clique | 5 a 20 imagens em estudos médicos [lido] | — | — | não medi | — | — | **não faz sentido ajustar** (seção 6.6) |

**As passadas (épocas) do cenário são suposição minha**, tirada do padrão de cada programa: Kraken para de treinar sozinho quando não melhora (usei 30); a documentação do Kraken recomenda 50 passadas para o ajuste de linhas **[lido]**; o `tesstrain` para em 10.000 passos por padrão **[lido]**; o script do docTR usa 10 passadas por padrão **[lido no código]**. O tempo real depende de quando o treino para de melhorar, o que só se sabe com correções de verdade.

---

## 3. A máquina: notebook do Kaique × PC do Samuel

- **Processador.** Pela comparação da Notebookcheck, o i5-1235U faz **55%** do Ryzen 7 5800H em trabalho com vários núcleos (Cinebench R23) e **111%** num núcleo só **[lido]**. Por isso usei **× 1,5 a × 2,5** para o PyTorch e o PaddlePaddle (a ponta alta cobre o notebook fino esquentar e baixar a velocidade num treino de horas **[dedução]**) e **× 0,9 a × 1,5** para o Tesseract, que treina num núcleo só.
- **Os treinos quase não ganharam com mais núcleos neste PC:** docTR, YOLO e Kraken deram praticamente o mesmo tempo com 4 e com 12 linhas de execução (ex.: Kraken lendo, 21 s × 17 s por passada; docTR achando texto, 13 s × 13,5 s por lote). Isso sugere que a diferença para o notebook fique mais perto de × 1,5 do que de × 2,5, mas a máquina estava dividida com o verificador **[medido + dedução]**.
- **Simular o notebook limitando núcleos não é exato:** o i5-1235U tem 2 núcleos rápidos e 8 econômicos; o limite de núcleos neste PC não reproduz isso **[dedução]**. **Nada foi medido no notebook.**
- **Iris Xe (vídeo integrado do notebook): nenhum dos cinco programas treina nela no Windows.**
  - PyTorch com placa Intel ("XPU"): a lista oficial tem as Arc A e B, e os Core Ultra com Arc; **a Iris Xe da 12ª geração não está** **[lido]**.
  - `torch-directml` (Microsoft, qualquer placa com DirectX 12): última versão é de **15/09/2024**, ainda "pré-lançamento", até o Python 3.12 **[lido, PyPI]**. O Kraken 7.1.1 exige PyTorch **2.9 a 2.14** **[lido, metadados do pacote]**, bem mais novo que o do DirectML **[dedução]**. Não testei.
  - OpenVINO (Intel): a documentação é toda sobre rodar e otimizar modelo pronto; o "treino" que aparece é só a quantização **[lido]**.
  - PaddlePaddle: os pacotes para Windows são só de processador ou de placa NVIDIA **[dedução, pela página de instalação e pelos pacotes do PyPI]**.
  - Tesseract: "No GPU is needed. (No support.)" **[lido]**.
- **GTX 1650 do Samuel (4 GB, sem float16 rápido):** funcionou com PyTorch para CUDA 12.6 (instalado só na pasta de ferramentas), tudo em float32 **[medido]**. O DocLayout-YOLO com 2 páginas por lote pediu **8,3 GB** e o Windows jogou o excesso na memória comum, ficando **tão lento quanto o processador**; com 1 página por lote (4,5 GB) ficou 2 vezes mais rápido que o processador **[medido]**. O docTR levou **4 minutos só na primeira passada** na placa (preparação da placa), e depois 2,2 s por página **[medido]**.

---

## 4. Cada modelo em detalhe

### 4.1 Kraken (motor à parte: Python 3.12 + PyTorch para processador)

**Transcrever (ketos train).**
- **Páginas [lido]:**
  - Guia da UB Mannheim para o eScriptorium (que usa o Kraken): "mesmo **pouco** material basta para começar"; corrigir **2 a 3 páginas**, ajustar, conferir, depois mais **4 páginas**, e assim por diante.
  - Reul e outros, 2022 (DAS 2022), manuscritos góticos alemães, reconhecedor Calamari (mesmo tipo de rede do Kraken): erro de 6,22% com o modelo pronto; **2 páginas → 3,27%**, **4 → 2,58%**, **32 → 1,65%**. E: "a maioria dos treinos termina em **poucas horas** num computador comum **sem placa de vídeo**".
  - Modelo TRIDIS (Kraken, manuscritos medievais, licença MIT): "ajustar com **10 páginas** corrigidas" leva o erro para 6% a 10%.
  - Documentação do Kraken: um modelo **novo** para impresso com poucos sinais pede **~800 linhas**; manuscrito pede mais. "30 páginas" de 25 a 40 linhas para começar do zero. "Raramente melhora depois de **50 passadas**, que levam **8 a 24 horas** num PC comum" (treino do zero, não ajuste).
- **Tempo [medido]**, CATMuS Medieval (rede de 4,1 milhões de números), 90 linhas de 4 páginas nossas:
  - 12 linhas de execução: 17 s por passada = **0,19 s por linha**; 8 linhas: 17 s; 4 linhas: 21 s (0,23 s por linha); lotes de 16 linhas: 0,17 s por linha.
  - GTX 1650, lotes de 16: **0,04 s por linha** (≈ 4 a 5 vezes mais rápido); com lote de 1, quase igual ao processador.
  - Mais ~20 s para abrir o Kraken e carregar o modelo, e ~10% de validação por passada.
- **PP-OCRv6 pequeno do Kraken 7.1 (14 milhões de números) [medido]:** no processador, **9 linhas levaram 10 minutos por passada** (60 a 70 s por linha), com ou sem o compilador do PyTorch (`torch.compile`, que no Windows ainda exige o compilador C++ da Microsoft; sem ele o treino quebra, e é preciso desligá-lo com `TORCHDYNAMO_DISABLE=1`). Na GTX 1650: **0,23 s por linha**. Por que o processador vai tão mal eu não investiguei; a rede tem uma parte extra só de treino (um decodificador "NRTR" de 9,5 milhões de números) **[lido no resumo do modelo]** e convoluções de núcleo grande, que costumam ser lentas no processador **[dedução]**.
- **Instalar a mais:** nada além do motor à parte já escolhido no item 1.3 (1,2 GB instalado, ~205 MB no instalador; ver `fase1-1.3-kraken-windows.md`). O `ketos` vem junto do Kraken.
- **Licença:** Kraken Apache-2.0; CATMuS e McCATMuS CC-BY 4.0 (citar a autoria); PP-OCRv6 do Kraken Apache-2.0; TRIDIS MIT. O modelo ajustado continua obra derivada do modelo de partida: vale a licença dele **[dedução]**.
- **Volta para ONNX:** a pesquisa de 28/09 exportou o CATMuS e o PP-OCRv6 para ONNX e deu **o mesmo texto** **[medido em 28/09]**; o ajustado tem a mesma forma, então o caminho é o mesmo **[dedução, não refeito hoje]**.

**Achar linhas (ketos segtrain, modelo `blla`).**
- **Páginas [lido]:** UB Mannheim: "corrigir **5 a 10 páginas** da segmentação automática" antes de ajustar. Documentação do Kraken: "um modelo pequeno para um tipo de material pode precisar de **menos de algumas centenas** de exemplos"; começar ajustando o `blla` "por **50 passadas**". Número mínimo para ajustar a um livro só: **não encontrado** na documentação oficial.
- **Tempo [medido]**, 3 páginas de treino + 1 de validação: 12 linhas de execução: **5,3 s por página por passada** (0,19 páginas/s); 4 linhas: **8 s**; GTX 1650: **~1 s**. Mais ~30 s para abrir.
- **Volta para ONNX [medido]:** exportei o `blla` **ajustado** para ONNX e comparei o mapa com o do PyTorch na Horas 47: maior diferença 0,019 e **0,0014% dos pontos mudam de lado** no limiar, o mesmo que o `blla` original deu em 29/09. O porte ONNX do 1.3 (`blla_onnx.py`) lê o arquivo novo sem mudança **[dedução]**.

### 4.2 Tesseract 5 (lstmtraining)

- **O que treina:** só o **reconhecedor de linha** (a rede LSTM). A divisão da página em blocos e linhas é por regras e **não treina** **[dedução, pelo que o `tesstrain` faz: só recebe linha recortada + texto]**.
- **Páginas:** a documentação oficial diz só que o ajuste "pode funcionar com **pouco** material" e dá dois exemplos: **400 passos** para uma fonte nova (erro de letra 0,5%) e **3.600 passos** para acrescentar um sinal (±) **[lido]**. Número de linhas: **não encontrado** na documentação do Tesseract. O `tesstrain` para em **10.000 passos** por padrão **[lido]**. Para reconhecedores do mesmo tipo em impressos antigos: **60 linhas** já reduzem bastante o erro (43% menos erros que treinar do zero); com pré-treino e votação, 2,5% de erro com 60 linhas e menos de 1% com **1.000 linhas** **[lido: Reul 2017 e 2018, OCRopus/Calamari]**. **Cuidado:** um estudo de 2025 com jornais espanhóis ajustou o Tesseract com 500 páginas e **não teve melhora consistente** **[lido]**.
- **Tempo [medido]:** 200 passos em **26 s** = **0,13 s por passo** (1 passo = 1 linha), com 1, 4 ou todas as linhas de execução: **usa um núcleo só**. Por isso o notebook deve ficar parecido com este PC (o núcleo rápido do i5 é até um pouco mais rápido) **[dedução]**. 10.000 passos ≈ 22 min.
- **Achado:** 37% das nossas linhas foram puladas porque tinham letras que o modelo `lat` não conhece (ſ, ꝑ, abreviações medievais). Para livro com esses sinais, o ajuste tem de **aumentar o alfabeto** (o caminho "`--old_traineddata`" do `tesstrain`), que é mais lento **[medido o pulo + lido]**.
- **Achado 2:** a lista de arquivos de treino tem de ter fim de linha do Linux (LF). Com o do Windows (CRLF) o `lstmtraining` falha com "Deserialize header failed" **[medido]**.
- **Instalar a mais:** **nada**. O instalador da UB Mannheim (5.4, já nesta máquina) traz `lstmtraining.exe`, `combine_tessdata.exe` e `text2image.exe` **[medido]**. O `tesstrain` (Makefile) exige `make`, `bash` etc.; **não é preciso**: fiz os passos direto com Python (`tess_preparar.py`).
- **Licença:** Tesseract, `tesstrain` e `tessdata_best` Apache-2.0 **[lido]**.
- **Volta para a versão do programa [medido]:** não precisa converter. `lstmtraining --stop_training` gera o `.traineddata` (9,7 MB) e, com `--convert_to_int`, a versão rápida (3,2 MB); o `tesseract.exe` leu uma linha com ele na hora. **Atenção:** só dá para ajustar a partir do modelo "best" (números com vírgula); o `lat` que está em `modelos/tessdata` é desse tipo (9,7 MB) **[medido]**.

### 4.3 docTR (original, com PyTorch) → OnnxTR

- **Páginas:** a documentação do docTR explica o formato dos dados e os scripts, mas **não diz quantas páginas** **[lido]**. **Não encontrado.**
- **O que se corrige:** o detector do docTR acha **palavras**, não linhas **[lido, documento do 1.3]**. Corrigir é mexer em caixas de palavra, mais trabalhoso que linhas **[dedução]**.
- **Tempo, achar texto (`fast_base`, entrada 1024×1024) [medido]:** processador: **6,5 a 8,5 s por página por passada** (12 ou 4 linhas de execução, quase igual); GTX 1650: **2,2 s**, depois de **4 minutos** de preparação na primeira passada.
- **Tempo, transcrever (`crnn_vgg16_bn`) [medido]:** processador: **0,058 s por palavra por passada** (1.067 palavras em 59 s); GTX 1650: **0,005 s** (12 vezes mais rápido). O `crnn` só aceita palavra de até ~30 letras e o alfabeto "french" (tirei as palavras fora disso antes de treinar).
- **Achado:** o script de treino do repositório (ramo principal) **não funciona** com o docTR 1.1.0 do PyPI; é preciso usar o do marco `v1.1.0` **[medido]**.
- **Instalar a mais:** PyTorch para processador + `python-doctr` + scripts do repositório: o ambiente de teste ficou com **1,2 GB** (inclui OnnxTR e matplotlib) **[medido]**. Dá para caber no motor à parte do Kraken, que já tem o PyTorch **[dedução]**.
- **Licença:** docTR e OnnxTR Apache-2.0 **[lido]**; os pesos prontos não têm licença própria escrita (documento do 1.3).
- **Volta para ONNX [medido]:** exportei os dois modelos ajustados (`export_model_to_onnx`, com o `fast_base` "reparametrizado") e comparei a saída bruta com a do PyTorch: diferença máxima 0,0001 na detecção (**nenhum ponto muda de lado**) e 0,00007 na leitura (**mesma letra em todas as posições**). O OnnxTR carrega modelo próprio passando o caminho do `.onnx` **[lido]**. **Ressalva:** rodando a página inteira pelos dois "preditores" (docTR e OnnxTR) com as opções padrão, saíram 217 × 223 palavras e só 84 iguais na mesma posição; a rede é a mesma, então a diferença vem das **opções padrão diferentes** dos dois preditores (tamanho, preenchimento, ordem) **[dedução, não investigado]**. Ao ligar, fixar as mesmas opções.

### 4.4 PaddleOCR (original, com PaddlePaddle) → RapidOCR

- **Páginas [lido, documentação de ajuste fino do PaddleOCR]:** "pelo menos **500** imagens" para ajustar a detecção e "pelo menos **5.000**" para a leitura (sem mudar o alfabeto); misturar meio a meio com dados gerais. São os únicos números oficiais que achei entre os cinco, e são para "cenas" em geral, não um livro só.
- **Tempo, achar texto (PP-OCRv6 pequeno) [medido]:** ~**13,5 s por lote de 2** = ~**7 s por imagem**. Cada imagem de treino é um **recorte de 640×640** da página, não a página inteira **[lido na configuração]**.
- **Tempo, transcrever (PP-OCRv6 pequeno) [medido]:** **0,72 a 0,76 imagens por segundo** = ~**1,35 s por palavra**; a primeira passada de 1.067 palavras ia levar ~25 min, e parei. Como no Kraken, a rede traz um decodificador extra só para o treino (perda "NRTR" no registro) **[medido]**.
- **Placa de vídeo:** não medi (seria o `paddlepaddle-gpu`, outro pacote grande).
- **Instalar a mais [medido]:** `paddlepaddle` 3.3.1 + dependências do PaddleOCR: **~960 MB**, mais o repositório do PaddleOCR (para `tools/train.py`) e os pesos de partida (11 MB detecção, 125 MB leitura). O PaddlePaddle para Windows vai só até o Python 3.13 (documento do 1.3): no programa (3.14) não entra, tem de ser à parte.
- **Licença:** PaddleOCR e PaddlePaddle Apache-2.0 **[lido]**; `paddle2onnx` Apache-2.0 **[dedução, não conferido]**.
- **Volta para ONNX [medido], com um tropeço:**
  1. `tools/export_model.py` gera o modelo de uso.
  2. `paddle2onnx` 2.1.0 converte para ONNX. **Com o PaddlePaddle 3.3.1 ou 3.2.2 ele nem abre** ("DLL load failed"). Com o 3.1.1 abre, mas **recusa o modelo exportado pelo 3.3.1**. Funcionou exportando **e** convertendo com o **3.1.1** num ambiente separado.
  3. Comparação ONNX × PaddlePaddle na mesma página: diferença máxima **0,00018**, e **0,0002% dos pontos** mudam de lado no limiar.
  4. O RapidOCR aceita modelo próprio (caminho do `.onnx` de detecção, de leitura e o arquivo do alfabeto) **[lido]**. Só converti a detecção.

### 4.5 DocLayout-YOLO (`modelos/doclayout.onnx`, detector de gravura e letra)

- **Qual é o modelo [medido]:** os metadados do `modelos/doclayout.onnx` dizem "YOLOv10m-doclayout", classes `title, plain text, abandon, figure, figure_caption, table...`, entrada de 1024, licença **AGPL-3.0**. É o **DocLayout-YOLO treinado no DocStructBench** (o `doclayout_inference_referencia.py` baixa `wybxc/DocLayout-YOLO-DocStructBench-onnx`). O `core/detectar_regioes.py` usa `figure`, `table` e `isolate_formula` como gravura.
- **Páginas:** o repositório do DocLayout-YOLO não diz **[lido]**. A Ultralytics (de onde ele vem) recomenda, para treino em geral, **≥ 1.500 imagens e ≥ 10.000 caixas por classe**, e "partir de pesos prontos em conjuntos pequenos" **[lido]**. Número para ajustar a um livro: **não encontrado**. Minha aposta: de 10 a 20 páginas marcadas, com várias gravuras cada **[dedução]**.
- **Tempo [medido]**, 5 páginas de treino, entrada 1024: processador **5,5 s por página por passada** (12 linhas) ou 6 s (4 linhas); GTX 1650 com 1 página por lote: **3 s**; com 2 por lote, 8,3 GB e **mesma velocidade do processador** (a placa transborda para a memória comum).
- **Achados de instalação [medido]:**
  - O pacote `doclayout-yolo` 0.0.4 é anterior ao PyTorch 2.6 e **não abre os próprios arquivos** no PyTorch 2.14 sem a variável `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`.
  - A exportação para ONNX com o exportador novo do PyTorch 2.14 (padrão) gera um arquivo que o `onnxruntime` **recusa**. Com o exportador antigo (`dynamo=False`) funciona.
- **Instalar a mais:** PyTorch + `doclayout-yolo` (que traz uma cópia antiga da Ultralytics); tamanho do ambiente: ver a seção 7.
- **Licença:** **AGPL-3.0** (código e modelo) **[lido nos metadados]**. O modelo ajustado é obra derivada; como o programa já aceita GPL/AGPL (decisão de 17/09, PyMuPDF), não muda nada, mas se distribuir o modelo ajustado vai junto o código **[dedução]**.
- **Volta para ONNX [medido]:** exportado com entrada de tamanho livre, o arquivo tem **a mesma entrada e a mesma saída** do `modelos/doclayout.onnx` (`images` → `output0`, 300 × 6). Em 6 páginas (Palatino 5, Horas 26 e 11, Opus 20, Escola 7, Rhetorica 18), preparadas do jeito do `core/detectar_regioes.py`, **as caixas com nota ≥ 0,2 saíram idênticas** (mesma classe, diferença de posição 0,0 pixel) entre o PyTorch e o `onnxruntime`. Arquivo de 74 MB, do tamanho do atual. Ou seja: o programa usaria o modelo ajustado **sem mudar uma linha** **[dedução a partir do medido]**.

### 4.6 MobileSAM (`modelos/mobile_sam`, seleção por clique)

- Ele não "acha" nada sozinho: recorta **o objeto em que se clicou** **[lido, documento do projeto]**. Quando erra, o conserto é outro clique (somar ou tirar), que a Fase 3 já prevê.
- Existem ferramentas para ajustar o MobileSAM (ex.: `MobileSAM_Finetune`) e estudos médicos que ajustam só a parte final com **5 a 20 imagens** **[lido]**.
- **Não faz sentido ajustar por livro [dedução]:** o que o Samuel marca num livro que não funciona é "isto é gravura, isto é letra", e isso é o que o detector (DocLayout-YOLO) aprende. O MobileSAM só ajudaria se o **contorno** saísse sempre errado num tipo de gravura, e aí o melhor é a Fase 3 (refinar a borda). Não medi. Licença Apache-2.0.

---

## 5. A ideia nova: treinar dentro do programa, em segundo plano

**Resumo:** dá, para os modelos baratos, e sem instalar quase nada a mais, **se** o motor à parte do Kraken (Python 3.12 + PyTorch, escolhido para o item 1.3) já estiver no instalador **[dedução]**.

| O que ajustar | Custo no notebook (cenário da tabela) | Precisa instalar a mais | Minha avaliação |
|---|---|---|---|
| Kraken transcrever (CATMuS/McCATMuS) | 45 min a 1¼ h | nada (o `ketos` vem no motor) | **bom candidato** |
| Tesseract transcrever | 20 a 30 min, um núcleo | nada (vem no Tesseract da UB Mannheim) | **bom candidato**, mas cuidado com letras que o modelo não conhece e com o resultado de 2025 que não melhorou |
| Kraken achar linhas | 1 a 3 h | nada | possível, deixar rodando |
| docTR (achar e transcrever) | 35 min a 1¼ h cada | `python-doctr` no motor (o PyTorch já está lá) [dedução] | possível; corrigir palavra por palavra é mais trabalhoso |
| DocLayout-YOLO (gravura) | 2½ a 4 h | `doclayout-yolo` + as manhas do PyTorch 2.14 | possível à noite; é o único que resolve "a gravura deste livro não é achada" |
| PP-OCRv6 (Kraken ou PaddleOCR) | dias | Paddle: + ~1 GB e outro Python | **não**, sem placa de vídeo |
| MobileSAM | — | — | **não** |

Pontos a pensar antes (todos **[dedução]**):
- **O treino deixa o notebook lento** enquanto roda (usa vários núcleos por horas). Melhor: botão "ajustar este livro" que roda à noite ou com o programa parado, com cancelar; ou limitar a 2–4 núcleos (medi quase o mesmo tempo com 4 e 12).
- **Memória:** não medi o pico do treino. O PyTorch no motor à parte usou 1,3 GB só para achar linhas; treino deve pedir mais.
- **Conferir o ganho:** separar sempre 1 ou 2 páginas corrigidas que o treino não vê e mostrar o erro antes/depois; se não melhorou, ficar com o modelo de fábrica (o próprio Kraken e o Tesseract já calculam isso).
- **Regra do projeto:** treinar não muda a natureza do modelo. Kraken, Tesseract, docTR (CRNN) e o detector só reconhecem ou apontam. O PP-OCRv6 treina com um decodificador que gera texto (NRTR), mas o modelo que o programa usa lê pelo CTC **[lido nos registros + dedução]**; como não é viável no processador, a questão não se põe.

---

## 6. Tabela "o que é · licença · roda aqui · roda no notebook"

| O que é | Licença | Treina aqui (PC do Samuel)? | Treina no notebook do Kaique? |
|---|---|---|---|
| Kraken 7.1.1 `ketos` (CATMuS, `blla`) | Apache-2.0; CATMuS CC-BY 4.0 | sim, processador e GTX 1650 [medido] | sim, só processador [estimativa] |
| Kraken 7.1.1 PP-OCRv6 | Apache-2.0 | só na GTX 1650 na prática [medido] | não (dias) |
| Tesseract 5.4 `lstmtraining` | Apache-2.0 | sim, um núcleo [medido] | sim [estimativa] |
| docTR 1.1.0 (scripts `references/`, marco v1.1.0) | Apache-2.0 | sim, processador e GTX 1650 [medido] | sim [estimativa] |
| PaddleOCR 3.x + PaddlePaddle 3.3.1 | Apache-2.0 | sim, processador (lento) [medido]; placa não testada | detecção sim (horas); leitura não (dias) |
| `paddle2onnx` 2.1.0 | Apache-2.0 [dedução] | só com PaddlePaddle 3.1.1 [medido] | idem |
| DocLayout-YOLO 0.0.4 | **AGPL-3.0** | sim, processador e GTX 1650 (lote 1) [medido] | sim (horas) [estimativa] |
| MobileSAM | Apache-2.0 | não testado | não recomendado |

---

## 7. O que ficou em aberto

- **Nada foi medido no notebook do Kaique.** Os tempos dele são o tempo daqui × 1,5 a 2,5 (× 0,9 a 1,5 no Tesseract).
- **Máquina dividida:** o verificador rodou `pytest` durante as medidas. Tempos são ordem de grandeza.
- **Dados falsos:** medi o tempo, **não** o ganho. Quantas páginas *o nosso acervo* precisa só se sabe corrigindo páginas de verdade (sugestão: Rhetorica 18 para impresso antigo, Horas 47 para caligrafia).
- **Páginas por modelo:** para docTR, PP-OCR (por livro) e DocLayout-YOLO **não achei** número oficial de ajuste fino. Os números de "2 páginas" e "10 páginas" são de estudos com Kraken e Calamari, em manuscritos e impressos antigos; valem para o Tesseract por semelhança de rede, não por teste **[dedução]**.
- **Passadas:** o número de passadas de cada cenário é suposição.
- **PP-OCR na placa de vídeo:** não medido.
- **PP-OCRv6 lento no processador:** não investiguei a causa.
- **docTR × OnnxTR na página inteira:** a rede dá o mesmo resultado, mas os dois preditores com as opções padrão não; falta alinhar as opções.
- **Leitura do PP-OCR para ONNX:** só converti a detecção.
- **Leitura do Kraken ajustada para ONNX:** não refeita hoje (foi medida em 28/09 com o modelo de fábrica).
- **Tamanhos:** medi o ambiente do docTR (1.185 MB) e do Paddle (960 MB); os do YOLO e do PyTorch com CUDA ficaram por medir (o `du` ficou lento demais com a máquina dividida).
- **Iris Xe:** conclusão pela documentação; não testei o `torch-directml`.

---

## 8. Ressalva sobre uma pasta apagada

Ao baixar o modelo do DocLayout-YOLO, passei um caminho no formato do Git Bash (`/d/programas/...`) para uma função do Python do Windows, que o entendeu como `D:\d\programas\...` e criou a pasta `D:\d`. Movi o arquivo baixado para o lugar certo e **apaguei a pasta `D:\d` inteira**. Eu **não conferi antes** se `D:\d` já existia com outra coisa dentro. Pela forma como foi criada, acredito que só tinha o download, mas **não tenho como provar**. Se o Samuel usava uma pasta `D:\d`, ela precisa ser conferida.

---

## 9. Método para refazer

Tudo em `D:\programas\EditorImpressao-arquivos\ferramentas\treino-ocr-2026-09-29\`:

| Arquivo | O que faz |
|---|---|
| `kraken_gerar_dados.py` | acha linhas e lê 4 páginas com o Kraken; grava `dados-kraken/linhas` (png + `.gt.txt`) e `dados-kraken/paginas` (PageXML) |
| `doctr_gerar_dados.py` | roda o docTR pronto em 6 páginas; grava `dados-doctr/det` e `dados-doctr/rec` no formato dos scripts do docTR |
| `tess_preparar.py` | transforma as linhas do Kraken em `.box` + `.lstmf` do Tesseract (`dados-tess/lista.txt`, **com LF**) |
| `paddle_preparar.py` | listas no formato do PaddleOCR (`dados-paddle/`) |
| `yolo_preparar_e_treinar.py` | rótulos YOLO pelo modelo pronto + treino + exportação |
| `yolo_exportar.py` | exporta o YOLO ajustado para ONNX (exportador antigo, entrada livre) e compara com o do programa |
| `doctr_exportar_onnx.py` | exporta o docTR ajustado e compara com o OnnxTR |
| `kraken_exportar_ajustado.py` | exporta o `blla` ajustado para ONNX e compara o mapa |
| `rodar_ppocr_compilado.bat` | PP-OCRv6 do Kraken com o compilador da Microsoft ligado |
| `log-*.txt` | a saída de cada treino medido |
| `venv-doctr`, `venv-paddle`, `venv-p2o` (Paddle 3.1.1 só para converter), `venv-yolo`, `venv-cuda` (PyTorch CUDA 12.6 + Kraken + docTR + YOLO) | ambientes Python 3.12; podem ser apagados |

Comandos principais (Git Bash; `K` = `ketos.exe` do ambiente com Kraken; `PYTHONUTF8=1` sempre):

```
# Kraken, transcrever (troque --threads, ou -d cuda:0 no ambiente CUDA)
$K --threads 12 train -f path -i catmus-medieval-1.6.0.mlmodel --resize union -q fixed -N 2 -B 1 dados-kraken/linhas/*.png
# Kraken, achar linhas
$K --threads 12 segtrain -f page -i blla.mlmodel --resize union -q fixed -N 2 -p 0.75 dados-kraken/paginas/*.xml
# Tesseract
combine_tessdata -e lat.traineddata lat.lstm
lstmtraining --model_output saida/lat_ft --continue_from lat.lstm --traineddata lat.traineddata --train_listfile dados-tess/lista.txt --max_iterations 200
lstmtraining --stop_training --continue_from saida/lat_ft_checkpoint --traineddata lat.traineddata --model_output lat_ft.traineddata
# docTR (scripts do marco v1.1.0; sem --device = processador)
python doctr-repo/references/detection/train.py fast_base --train_path dados-doctr/det/train --val_path dados-doctr/det/val --epochs 2 -b 2 --pretrained -j 0
python doctr-repo/references/recognition/train.py crnn_vgg16_bn --train_path dados-doctr/rec/train --val_path dados-doctr/rec/val --epochs 1 -b 64 --pretrained -j 0
# PaddleOCR (dentro de paddleocr-repo; caminhos no formato D:/...)
python tools/train.py -c configs/det/PP-OCRv6/PP-OCRv6_small_det.yml -o Global.use_gpu=False Global.epoch_num=2 Global.pretrained_model=.../PP-OCRv6_small_det_pretrained Train.dataset.label_file_list=[.../det_train.txt] Train.loader.batch_size_per_card=2 Train.loader.num_workers=0 ...
# conversão: no venv-p2o (PaddlePaddle 3.1.1): tools/export_model.py e depois paddle2onnx.export(...)
# DocLayout-YOLO
TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 python yolo_preparar_e_treinar.py 12 2 horas_p047 palatino_p005 escola_p035 opusmajus_p020 horas_p026 palatino_p057
```

Para limitar núcleos: `--threads N` no Kraken; `OMP_NUM_THREADS`/`MKL_NUM_THREADS` no docTR e no PaddlePaddle; `torch.set_num_threads` no YOLO (o script recebe o número); o Tesseract usa um só de qualquer jeito.

---

## 10. Links consultados (29/09/2026)

- Kraken, tutorial de treino (6.0): https://kraken.re/6.0.0/tutorials/training.html ("~800 linhas", "30 páginas", "50 passadas, 8 a 24 horas", "menos de algumas centenas" para segmentação)
- Kraken, documentação 5.2 (`ketos`): https://kraken.re/5.2/ketos.html ("ajustar o modelo padrão por 50 passadas")
- UB Mannheim, "Training with eScriptorium": https://ub-mannheim.github.io/eScriptorium_Dokumentation/Training-with-eScriptorium-EN.html (2 a 3 páginas; 5 a 10 páginas de segmentação)
- eScriptorium tutorial, treino: https://escriptorium-tutorial.readthedocs.io/en/latest/train/
- Reul, Tomasek, Langhanki, Springmann, 2022, "Open Source Handwritten Text Recognition on Medieval Manuscripts using Mixed Models and Document-Specific Finetuning": https://arxiv.org/abs/2201.07661 (2/4/32 páginas; Calamari; "poucas horas sem placa de vídeo")
- Reul, Wick, Springmann, Puppe, 2017, "Transfer Learning for OCRopus Model Training on Early Printed Books": https://arxiv.org/abs/1712.05586 (60 e 150 linhas)
- Reul e outros, 2018, "Improving OCR Accuracy on Early Printed Books by combining Pretraining, Voting and Active Learning": https://arxiv.org/abs/1802.10038 (60 linhas → 2,5%; 1.000 linhas → < 1%)
- TRIDIS (Zenodo): https://zenodo.org/records/10788591 (10 páginas; MIT)
- Tesseract, "How to train LSTM/neural net Tesseract" (4.00): https://tesseract-ocr.github.io/tessdoc/tess4/TrainingTesseract-4.00.html (400 e 3.600 passos)
- Tesseract 5, treino: https://tesseract-ocr.github.io/tessdoc/tess5/TrainingTesseract-5.html ("No GPU is needed. (No support.)")
- tesstrain: https://github.com/tesseract-ocr/tesstrain (MAX_ITERATIONS 10000; Apache-2.0)
- Macicior-Mitxelena, 2025, "Transcribing History with Tesseract" (PastReader): https://ceur-ws.org/Vol-4098/PastReader2025_paper2.pdf (ajuste sem melhora consistente)
- docTR, treinar modelo próprio: https://mindee.github.io/doctr/latest/using_doctr/custom_models_training.html e os `README.md` de `references/detection` e `references/recognition` (marco v1.1.0)
- OnnxTR: https://github.com/felixdittrich92/OnnxTR (carregar modelo próprio exportado do docTR)
- PaddleOCR, ajuste fino: https://www.paddleocr.ai/v2.9/en/ppocr/model_train/finetune.html (500 e 5.000 imagens)
- Paddle2ONNX (PaddleOCR): https://www.paddleocr.ai/v2.9.1/en/ppocr/infer_deploy/paddle2onnx.html
- RapidOCR: https://github.com/rapidai/rapidocr (modelo próprio por caminho)
- DocLayout-YOLO: https://github.com/opendatalab/DocLayout-YOLO (AGPL-3.0)
- Ultralytics, dicas de treino: https://docs.ultralytics.com/yolov5/tutorials/tips_for_best_training_results/ (1.500 imagens / 10.000 caixas por classe)
- PyTorch, placas Intel: https://docs.pytorch.org/docs/2.14/notes/get_start_xpu.html (lista sem Iris Xe)
- torch-directml (PyPI): https://pypi.org/project/torch-directml/ (0.2.5.dev240914, 15/09/2024)
- OpenVINO: https://docs.openvino.ai/2025/index.html
- Notebookcheck, i5-1235U × Ryzen 7 5800H: https://www.notebookcheck.net/i5-1235U-vs-R7-5800H_14078_13005.247596.0.html (55% em vários núcleos, 111% num núcleo)
- MobileSAM_Finetune: https://github.com/thedannyliu/MobileSAM_Finetune ; SAM few-shot (WACV 2024): https://openaccess.thecvf.com/content/WACV2024/papers/Xie_SAM_Fewshot_Finetuning_for_Anatomical_Segmentation_in_Medical_Images_WACV_2024_paper.pdf
- Locais: `docs/pesquisa/fase1-1.3-kraken-windows.md`, `docs/pesquisa/fase1-ocr-manuscrito-no-windows.md`, `docs/pesquisa/fase1-1.3-ocr-para-achar-texto.md`, `docs/plano/OCR-PESQUISA.md`, `core/detectar_regioes.py`, `modelos/doclayout_inference_referencia.py`, metadados de `modelos/doclayout.onnx`
