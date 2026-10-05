# Fase 2, modo Misto: a letra e a tinta que o OCR não enxerga

**Data:** 05/10/2026 · **Quem:** agente pesquisador · **Pedido:** gerente, para o modo Misto da Fase 2 (preto e branco só nas letras; gravuras, fotos e molduras como no original), usando as linhas que o docTR `fast_base` e o Kraken já acham, como o Internet Archive faz.

**A exigência do Samuel, palavra por palavra:** "precisa ter uma solução para isso, para que isso não aconteça, ou algum tipo de opção que eu possa habilitar ou desabilitar, ou que o proprio programa possa perceber, me de opções e por favor faça pesquisas."

**Nada no programa foi mexido.** Li código e documentação de fora (links na seção 11) e fiz uma **prova pequena** numa pasta temporária minha, fora do projeto: usei as imagens e as linhas de OCR que já estavam gravadas da comparação do item 1.3 (`saida_teste/ocr-1.3/`) e, para três páginas, o `core/ocr_doctr.py` só para ler (sem alterar). Nada foi instalado no `.venv`. O método da prova está na seção 4, para refazer.

**Como ler as marcas:**
- **[lido]** = li no código ou no documento de fora (ou no nosso código, quando digo).
- **[medido]** = rodei neste PC (o do Samuel) e olhei as imagens.
- **[dedução]** = conclusão minha, não conferida.

---

## 1. A resposta em cinco frases

1. **Ninguém de fora faz "preto e branco só dentro das linhas e o resto vira branco".** O Internet Archive **soma sempre** o preto e branco da página inteira às linhas do OCR (a chave `MIX_THRESHOLD = True` no `mrc.py`), e o que fica fora não some: vai para a camada de baixo. O DjVu passa tudo para preto e branco e decide **peça por peça** se é tinta. O ScanTailor passa para preto e branco **tudo o que não é gravura**. Um Misto "só nas linhas, o resto branco" seria o único que **apaga** o que não reconheceu [lido].
2. **O risco é real e grande:** medido em 13 páginas, no **Graduale 222 e 223 três quartos da tinta (as pautas e as notas) ficam fora das linhas do OCR**, e no Palatino 9, Siebmacher 9, Opus 256 e Horas 13 ficam fora de 40% a 48% (moldura, capitular, tabela). Só as linhas = **a música inteira do Graduale sumiria** [medido].
3. **Solução que recomendo ("rede de segurança"):** fora das linhas e fora das gravuras, cada pedaço de tinta continua **preto se tiver pelo menos um ponto tão escuro quanto as letras da própria página** (o programa aprende esse escuro dentro das linhas do OCR); o que é só cinza claro (a mancha do verso) vai para o branco. Na prova, isso **guardou notas, pautas, capitular, letrinhas dos diagramas e sinais de métrica**, e **jogou fora a escrita espelhada** do verso no Boécio e no Marial, em **0,02 a 0,17 s por página** [medido].
4. **O programa pode perceber sozinho:** se sobrar muita tinta forte fora das linhas (a música, uma capitular, uma linha que os dois OCRs perderam, como no Graduale 223), a página vai para **"Para revisar"** com o lugar marcado, o mesmo caminho que o 1.3 já usa. E sempre há como corrigir: uma chave de três posições por livro e por página, e o pincel **"isto é letra"** (o tipo LETRA da aba Marcar já existe) [dedução, sobre peças que já temos].
5. **Detectores de região treinados em livro antigo existem** e marcam exatamente os casos de risco (capitular, música, número de página, reclamo, nota de margem, texto dentro de gravura): os modelos D-FINE do próprio autor do Kraken (Apache-2.0, rodam no motor do Kraken que já instalamos) e modelos YOLO de manuscrito medieval (Apache-2.0, viram ONNX como o nosso `doclayout.onnx`). Mas a nota deles é **mediana** e ninguém mediu nos nossos livros: ficam como **segunda etapa, depois de medir**, não como a proteção principal [lido + dedução].

### Tabela no formato do pesquisador

| O que é | Licença | Roda aqui (Windows, Python 3.14)? | Roda no notebook do Kaique? |
|---|---|---|---|
| **Rede de segurança** (peças de tinta + "escuro como a letra", OpenCV e DoxaPy que já temos) | Apache-2.0 (OpenCV), CC0 (DoxaPy) — já no programa | **Sim** [medido: 0,02–0,17 s por página] | Sim (processador; uns 2× mais lento, [dedução]) |
| `archive-pdf-tools` (`mrc.py`), só para entender | AGPL-3.0 | Não precisa rodar | Não precisa |
| ScanTailor Advanced (Misto) | GPL-3.0 | Sim (já é o caminho da Fase 2) | Sim |
| DjVu (artigo de 1999; DjVuLibre) | artigo; DjVuLibre GPL-2.0 | Só a ideia serve | — |
| `didjvu` (Gamera) | GPL-2.0 | **Não** (Python 2.7) [lido] | Não |
| `unpaper` (filtro de cinza) | GPL-2.0-only [lido no código] | Programa à parte em C; só a ideia serve | — |
| Comparar com o verso espelhado | ideia da literatura; OpenCV | Sim [dedução] | Sim |
| DocLayout-YOLO (`modelos/doclayout.onnx`, já no programa) | AGPL-3.0 (código); pesos do mesmo repositório | Sim (já roda) | Sim |
| D-FINE treinado no LADaS (`dfine_kraken`, Kiessling) | Apache-2.0 (código e pesos) [lido] | **Só no motor do Kraken** (Python 3.12; o pacote pede Python < 3.14 e Kraken ≥ 7.1) [lido] | Sim, pelo mesmo motor; tempo desconhecido |
| YOLO11 de manuscrito medieval (`biglam/medieval-manuscript-yolov11`) | Apache-2.0 nos pesos [lido]; Ultralytics (para converter) AGPL-3.0 | Sim, depois de convertido para ONNX (`onnxruntime` já está no programa) [dedução] | Sim [dedução] |
| PP-DocLayout (Baidu) | Apache-2.0 | Por ONNX (RapidLayout, Apache-2.0), não testado [dedução] | Sim [dedução] |
| eynollah (Biblioteca de Berlim) | Apache-2.0 | **Não**: Linux, Python 3.8–3.11 [lido] | Não |
| Pauta de música por morfologia (receita do próprio OpenCV) | Apache-2.0 | Sim [medido: 0,16 s, mas achou só metade das linhas da pauta] | Sim |
| OMMR4all (notação quadrada medieval) | GPL-3.0 | Não na prática: servidor web com redes próprias [lido + dedução] | Não |
| oemer (partitura moderna) | MIT | Talvez (pede `onnxruntime-gpu`); feito para pauta de 5 linhas moderna [lido] | Talvez |
| Audiveris (partitura moderna) | AGPL-3.0 | Programa Java à parte; não lê neuma [dedução] | — |

---

## 2. Os casos de risco, um por um (o que cobre cada um)

"Fica fora das linhas" foi visto na prova (seção 4) ou na comparação do 1.3 (`relatorios/fase1-1.3-comparacao-ocr-2026-09-28/`).

| Caso | O OCR acha? | O que salva |
|---|---|---|
| **Pauta e notas do Graduale** | **Não**: o Kraken não põe nenhuma caixa na música; o docTR põe 5 caixinhas em 3 páginas [lido no 1.3] | Rede de segurança (guardou as notas e as pautas, [medido]); detector de música (MusicZone) ou de pauta como reforço |
| **Capitular xilográfica** (Q do Palatino 9) | Não (às vezes uma caixinha na borda) | Se o detector de gravura do ScanTailor a pega, fica original. Se não pega (foi o caso no teste de 24/09), a rede guarda o traço escuro e **perde as hachuras claras** [medido]; DropCapitalZone mandaria para gravura |
| **Capitular a pena colorida** (Graduale, Horas) | Às vezes | A cor forte já vira gravura no nosso detector (`SATURACAO_DE_COR`); a rede guarda a parte escura |
| **Letrinhas dentro do diagrama** (Opus 165) | Algumas | A rede guardou "a", "b", "c", "d" e as linhas do diagrama; perdeu **dois pedacinhos de traço fino** claro [medido] |
| **Número de página, reclamo, assinatura de caderno** ("A iii" no Palatino 9) | Quase sempre, na prova | Se escapar, a rede guarda (é tinta escura). Atenção: o **número de fólio clarinho** do Graduale 222 ("Cvij") nem o preto e branco pega: some em qualquer Misto e também no Preto e branco de hoje [medido] |
| **Rubrica / nota na margem** ("Docens, loqua-" no Marial) | Na prova, sim | Rede de segurança; cor vermelha vira gravura pelo detector de cor |
| **Texto em ângulo, texto dentro de moldura** | docTR e Kraken são feitos para linha deitada | Rede de segurança (não depende de ângulo) |
| **Linha que os dois OCRs perdem juntos** (Graduale 223) | Não, e a comparação não vê [lido no relatório de 29/09] | A rede guarda; o **aviso** "tinta forte fora das linhas" pega esse caso, que a comparação entre OCRs não pega |

---

## 3. Como os outros tratam a tinta fora das linhas

### 3.1 Internet Archive (`archive-pdf-tools`, `mrc.py`) [lido no código, 05/10]

- `create_hocr_mask`: dentro de cada linha do OCR (pulando linha vazia ou com confiança média < 20), Sauvola com k = 0,1, testando a linha normal e invertida.
- `create_mrc_hocr_components`: logo depois, `MIX_THRESHOLD = True` chama `create_threshold_mask`, que faz **Sauvola da página inteira** (k = 0,34, janela = DPI/4; antes, um borrão leve se a imagem for ruidosa) e **soma** à máscara (`mask_arr |= thres_arr`). Há uma linha comentada "isto apaga a máscara do hOCR, só para teste": eles experimentaram e ficaram com a soma.
- O que fica fora da máscara **não é apagado**: vai para a camada de baixo (reduzida, 1/3 da resolução nos nossos livros), que continua aparecendo no PDF.
- **Consequência para nós** [dedução]: o Archive nunca precisou resolver o nosso problema, porque para ele "não entrou na máscara" quer dizer "ficou menos nítido", não "sumiu". O nosso Misto, que pinta o papel de branco, é mais perigoso que o modelo que estamos copiando. O que vale copiar dele é a **ordem** (linhas primeiro, página inteira como reforço), não o "só linhas".
- Isso confirma o que o `fase1-1.1-camadas-internet-archive.md` (seção 7) já tinha corrigido no `TESTE-SCANTAILOR-MISTO.md`.

### 3.2 DjVu (AT&T, Haffner, Bottou, Howard e LeCun, 1999) [lido no artigo]

- Sem OCR. Primeiro separa cada bloco da página em "cor clara" (fundo) e "cor escura" (primeiro plano), passando a página inteira.
- Depois um **filtro decide, para cada mancha escura, se vale mais como letra ou como fundo**: compara o custo de guardar a mancha como "peça de cor uniforme destacada do papel" contra "parte do fundo que muda devagar". Mancha que **se destaca com borda nítida e cor uniforme** fica como letra; mancha que **se mistura com o fundo** vai para o fundo. Outro filtro conserta letra que saiu "em negativo".
- Os autores admitem erros do tipo "olhos e sobrancelhas de uma foto viram letra".
- **O que serve para nós:** a decisão é **peça por peça**, e o critério é "destaca-se do papel ou não". É a mesma família da rede de segurança da seção 4. E, de novo, o rejeitado vai para o fundo, não some.

### 3.3 ScanTailor Advanced (modo Misto) [lido em `fase2-mapa-scantailor.md`, seção 5]

- Passa **a página inteira** para preto e branco e só deixa original o que a máscara de gravura (o detector do item 1.2) e as zonas à mão mandam. Não usa OCR.
- Logo: **nunca perde letra fora de linha** (tudo que não é gravura vira preto e branco), mas **a mancha do verso escura vira preta**, que é o defeito mais grave aberto (`CLAUDE.md`, seção 9).

### 3.4 didjvu, minidjvu, csepdjvu [lido]

- `didjvu` (GPL-2.0, Python 2.7, Gamera): binariza **a página inteira** com um dos métodos do Gamera; tudo o que é preto vai para a camada de cima. Não usa OCR. Não roda no 3.14.
- `minidjvu`: só páginas já em preto e branco. `csepdjvu` (DjVuLibre): só recebe a separação pronta, não decide nada.

### 3.5 unpaper, o "filtro de cinza" [lido no manual]

- `--grayfilter`: anda pela página com uma janela (de fábrica 50×50 pontos, passo 20) e **apaga a janela inteira se nela não houver nenhum ponto preto, só cinza** (limiar de "cinza aceitável" 0,5). Pode ser desligado por folha (`--no-grayfilter`).
- É a mesma ideia da rede de segurança, só que em janelas quadradas: **"sem nenhum ponto realmente escuro, é sujeira"**.

### 3.6 Kraken, eScriptorium, OCR-D, eynollah [lido]

- **Kraken / eScriptorium:** só acham linhas e regiões para transcrever; não montam imagem, então "o que sobra" simplesmente não é transcrito. O Kraken 7 ganhou detecção de **regiões** com o D-FINE (seção 6.3).
- **OCR-D:** a binarização é da página inteira, antes de achar o leiaute; o formato PAGE-XML tem tipos de região próprios para **música, fórmula, gravura, separador e "ruído"**. Ou seja: lá também a tinta fora do texto não é apagada, é **classificada**.
- **eynollah** (Biblioteca Estadual de Berlim, Apache-2.0): acha texto, título, imagem, separador, **nota de margem, capitular ("initial")** e tabela. Só Linux, Python 3.8–3.11, e os autores avisam que "pode ser lento". Não serve aqui, mas mostra que capitular e margem são tratadas como **regiões à parte** nos projetos de livro antigo.

### 3.7 ABBYY FineReader (programa comercial) [lido na ajuda]

Tipos de área: **Texto**, **Imagem** (recriada como está), **Imagem de fundo** (imagem com texto por cima), Tabela, Código de barras. O programa propõe as áreas sozinho e a pessoa corrige desenhando e trocando o tipo, com a cor da borda dizendo o tipo. É o mesmo padrão da nossa aba Marcar.

---

## 4. A prova: quanto fica fora das linhas, e quanto a rede de segurança salva

### 4.1 Método (para refazer)

Numa pasta temporária, com o `.venv` do projeto só para ler:
1. Página: as imagens de `saida_teste/ocr-1.3/imagens/` (as mesmas do 1.3; Horas e Graduale com ~1000 px de largura, as outras até 300 DPI). Para Marial 7, Boécio 22 e Palatino 10 também desenhei o PDF de `gabarito/paginas/` e rodei o docTR pelo `core/ocr_doctr.py`.
2. **Tinta** = Sauvola do DoxaPy na página inteira, k = 0,34, janela = DPI/4 (o mesmo do Archive). Para simular um preto e branco mais forte, que pega a mancha, repeti com k = 0,1.
3. **Linhas** = união das linhas do docTR (`D2`, `fast_base`) e do Kraken (`K1`), alargadas 15% da altura da linha (como no 1.3). **Não usei o detector de gravura** (seção 4.4).
4. **Rede de segurança:** separa a tinta fora das linhas em pedaços ligados (componentes conexos do OpenCV). O "escuro da letra" desta página = a **mediana do cinza da tinta dentro das linhas**. Um pedaço fica (preto) se tem **pelo menos um ponto tão escuro quanto isso** e área de pelo menos (altura da linha ÷ 6)²; senão vai para branco. É uma "histerese": semente escura, crescimento pelo resto do pedaço.
5. Desenhei por cima da página: verde = linhas do OCR; **azul = fora das linhas, guardado pela rede**; **vermelho = fora das linhas, iria para branco**. Abri todas as imagens.

### 4.2 Números [medido]

"Fora" e "descarta" em % de toda a tinta da página.

| Página | Tinta fora das linhas | A rede guarda | A rede descarta | O que é a tinta de fora |
|---|---|---|---|---|
| **Graduale 222** | **75,6%** | 74,6% | 1,0% | pautas e notas; o descartado são pedaços da pauta vermelha clara |
| **Graduale 223** | **74,0%** | 72,3% | 1,8% | idem |
| Palatino 9 | 47,7% | 46,2% | 1,5% | moldura, **capitular Q** (descarta hachuras claras dela) |
| Siebmacher 9 | 44,9% | 42,0% | 2,9% | moldura ornamental |
| Opus Majus 256 | 42,1% | 41,1% | 1,0% | fios e números da tabela |
| Horas 13 | 41,6% | 37,2% | 4,4% | **moldura dourada** (o dourado claro vai para "descartar"; ela é gravura, ver 4.4) |
| Palatino 10 | 31,5% | 31,3% | 0,2% | moldura |
| Marial 7 (k 0,34) | 14,7% | 14,4% | 0,4% | beirada do livro, letras do verso na margem |
| Rhetorica 18 | 11,7% | 10,8% | 0,8% | notas de margem, fios |
| Opus Majus 165 | 5,5% | 5,4% | 0,0% | os dois diagramas e as letrinhas |
| Boécio 22 (k 0,34) | 4,5% | 3,3% | 1,2% | capitulares azuis, sinais de métrica, verso |
| Palatino 7 | 0,2% | 0,1% | 0,1% | quase nada |
| **Boécio 22 (k 0,1, preto e branco forte)** | 17,7% | 3,9% | **13,8%** | **a escrita espelhada do verso** na coluna da direita |
| **Marial 7 (k 0,1)** | 15,5% | 12,2% | 3,3% | **letras do verso** na margem direita |

**Tempo da rede**, depois do preto e branco: 0,02 a 0,08 s nas páginas acima; **0,12 s no Palatino 10 em resolução cheia** (1929 × 2943), mais 0,05 s do Sauvola. O docTR levou 1,1 a 1,7 s por página (já se sabia).

### 4.3 O que se vê nas imagens [medido]

- **Graduale 222:** todas as notas quadradas e as quatro linhas de cada pauta ficaram azuis (guardadas). A escrita do verso, que aparece por trás, **nem entrou** no Sauvola k = 0,34. Vermelho só em pedacinhos da pauta vermelha e numa rubrica.
- **Boécio 22 com k = 0,1:** a escrita espelhada do verso, à direita das linhas de verso, ficou **vermelha** (descartada); as duas capitulares "Q" azuis e os sinais "– v v" da métrica ficaram azuis (guardados). Falha: algumas letras do verso mais escuras, encostadas no texto, ficaram azuis.
- **Marial 7 com k = 0,1:** as letras espelhadas da margem direita ficaram vermelhas; a nota de margem e o "52" estavam dentro das linhas do OCR.
- **Opus 165:** diagramas e letras "a, b, c, d" azuis; **dois pedacinhos de traço fino** (perto do "e f") vermelhos.
- **Palatino 9:** a capitular Q azul no traço escuro, com **as hachuras claras em vermelho**. A mancha do verso no alto à esquerda **está dentro de caixas falsas do docTR** (verde), ou seja: ali o perigo é o contrário, a mancha entrar como linha.
- **Horas 13:** a moldura dourada sai metade azul, metade vermelha: confirma que moldura tem de vir do detector de gravura, nunca desta rede.

### 4.4 Ressalvas da prova

- **Sem o detector de gravura.** No programa, moldura, iluminura, retrato e (às vezes) a capitular saem antes, como gravura; a rede só olharia o que sobra. Por isso os números de "fora das linhas" acima são **maiores** do que seriam no Misto de verdade, mas os casos de risco (música, letrinhas, números) continuam lá.
- **Treze páginas, um limiar só** (a mediana). Traço fino claro (Opus 165) e hachura de capitular pedem um limiar mais tolerante (por exemplo o percentil 75 da tinta das letras) ou um segundo critério (seção 5); isso é para o implementador medir.
- **A mancha do verso que fica fora das linhas, nestas páginas, é fraca** e quase não entra no Sauvola k = 0,34. Ela vira problema quando o preto e branco é forte (k baixo) ou quando a tinta atravessou muito o papel (manuscrito com tinta ferrogálica). Nesse último caso o verso pode ser tão escuro quanto a letra, e a rede **não** separa: precisa da comparação com o verso (5.5).
- **A mancha que fica dentro das linhas** (Palatino 10, Boécio, Palatino 9) é outro problema, do preto e branco **dentro** da linha, e não é resolvido por nenhuma das opções deste documento.
- Página **sem nenhuma linha** (página só de gravura, ou OCR que falhou, como o Tesseract na Horas 11): não há como aprender o "escuro da letra". Ali o programa tem de cair no Misto do ScanTailor (tudo fora da gravura em preto e branco) e avisar [dedução].
- Graduale e Horas em ~1000 px de largura; não testei em resolução maior.

---

## 5. Sinais para separar tinta de verdade da mancha, sem OCR

Do mais barato ao mais caro. Todos rodam com o que já está no `.venv` (OpenCV, numpy, scikit-image, DoxaPy).

| Sinal | O que faz | Onde já é usado | Custo | Risco |
|---|---|---|---|---|
| **5.1 Escuro como a letra** (histerese, a rede da seção 4) | Pedaço com pelo menos um ponto tão escuro quanto as letras da página fica; pedaço só cinza vai para branco | unpaper (`grayfilter`, em janelas) [lido]; o `apply_hysteresis_threshold` do scikit-image faz o mesmo em uma chamada [lido: existe no `.venv`] | 0,02–0,17 s por página [medido] | Perde traço fino claro e hachura (4.3); guarda verso muito escuro |
| **5.2 Borda nítida** | A mancha do verso atravessou o papel e chega **borrada**: a borda dela muda devagar; a letra da frente tem borda brusca | É o critério do DjVu ("destaca-se do fundo") [lido]; o método **Su** (2010), que já está no DoxaPy (`SU`), acha os pontos de **contraste alto perto do traço** e só aceita tinta perto deles [lido no resumo do artigo] | Sobel ou contraste local: décimos de segundo [dedução] | Scan borrado ou de baixa resolução (Horas, Graduale a 72 DPI) deixa a letra também borrada |
| **5.3 Tamanho e forma** | Poeira muito pequena sai; pedaço com tamanho de letra ou de nota fica | DjVu, Archive (limpeza de pontinhos), ScanTailor (`Despeckle`) [lido] | Desprezível | Pingo de i, ponto final e neuma pequena: usar a distância até a letra vizinha, como o `Despeckle` do ScanTailor faz |
| **5.4 Cor** | Vermelho, azul, dourado forte = tinta pintada | Já temos (`SATURACAO_DE_COR = 130` em `core/detectar_regioes.py`) [lido no nosso código] | Desprezível | Rubrica desbotada é marrom, igual ao papel velho (`CLAUDE.md`, seção 9) |
| **5.5 Espelho do verso** | Espelhar a página de trás, encaixar sobre a frente e ver se o pedaço "fora das linhas" coincide com tinta do verso: se coincide e é mais claro, é mancha | É a solução já recomendada no `CLAUDE.md` (seção 9) para a mancha do verso. Na literatura: Rowley-Brooke, Pitié e Kokaram (CVPR 2013) espelham e alinham o verso e classificam pelo histograma conjunto frente/verso; há trabalho só para **livros de música antiga** com o mesmo método [lido nos resumos] | Encaixe (por exemplo `findTransformECC` do OpenCV): perto de 1 s por página [dedução]; precisa saber qual página é o verso | Página com verso faltando, folha montada fora de ordem, papel que encolheu (encaixe local) |
| **5.6 Largura do traço** | Letra e nota têm traço de largura parecida com a do texto; mancha tem largura irregular | "Stroke width transform" (Epshtein, Ofek e Wexler, 2010) — conheço da literatura, **não li hoje** | Transformada de distância: décimos de segundo [dedução] | Capitular xilográfica e hachura têm larguras muito diferentes do texto: guardaria pouco |

**Recomendação para a rede de segurança** [dedução]: 5.1 + 5.3 + 5.4 de fábrica (baratos e já medidos), 5.2 como segundo voto se a prova no gabarito mostrar mancha guardada, e 5.5 entra junto com o item "tirar a mancha do verso", porque serve aos dois.

---

## 6. Detectores de leiaute e de música

### 6.1 DocLayout-YOLO (já no programa) [lido no nosso código e no artigo]

- `core/detectar_regioes.py` usa 10 classes. Uma delas, **`abandon`**, é, pela definição do DocStructBench, "**cabeçalho, rodapé, número de página, nota de rodapé e nota de margem**". **O nosso código não põe `abandon` em `CLASSES_DE_LETRA`** (só `title`, `plain text` e as legendas). No Misto isso importa: é justamente a classe dos itens pequenos que o OCR pode perder. Barato de aproveitar como reforço [dedução].
- Foi treinado em documento moderno; não tem capitular nem música.

### 6.2 PP-DocLayout (Baidu, Apache-2.0) [lido]

- 23 classes, entre elas **número de página**, **texto lateral** (margem), **carimbo**, cabeçalho e rodapé. Versão L: 124 MB, 0,5 s no processador da Baidu; versão S: 5 MB, 0,02 s.
- PaddlePaddle não instala no 3.14 (`fase1-1.3-ocr-para-achar-texto.md`), mas há conversão para ONNX (RapidLayout, Apache-2.0). Também é treinado em documento moderno. Não vale a troca sobre o DocLayout que já temos [dedução].

### 6.3 D-FINE treinado no LADaS (Kiessling, autor do Kraken; 2026) [lido]

- **37 tipos de região** do vocabulário SegmOnto, entre eles: `DropCapitalZone` (capitular), **`MusicZone`**, `NumberingZone` (número), **`QuireMarksZone`** (assinatura e reclamo), `MarginTextZone-Notes` (nota de margem), `RunningTitleZone` (título corrente), **`GraphicZone-TextualContent`** (texto dentro de gravura), `MainZone-Maths`, `StampZone`, `DigitizationArtefactZone`.
- Treinado em livros do **século XVII até hoje**, quase todos franceses. Tamanhos: 15 MB (nano) a 252 MB; o melhor é o "large" (126 MB), entrada de 1280 px.
- **Notas (versão large, mAP 50:95):** capitular 0,58 (acerta 84% do que marca, acha 71%); música 0,55 (82% / 69%); número 0,37 (78% / 52%); reclamo 0,29 (54% / 61%); nota de margem 0,42. Ou seja: **acha de metade a dois terços** do que deveria. Serve de reforço, **não** de rede de segurança.
- Roda pelo `kraken segment` com o pacote `dfine_kraken` 0.4.4 (Apache-2.0), que pede **Kraken ≥ 7.1 e Python < 3.14**: cabe no **motor do Kraken que já instalamos** (Python 3.12, Kraken 7.1.1). Precisa de mais pacotes no motor (`timm`, `albumentations`, `torchmetrics`). Tempo no processador: **não publicado**; o motor já leva ~10 s por página só nas linhas.
- **Risco:** as páginas do século XVI e os manuscritos (Palatino, Graduale, Horas) ficam fora do período de treino.

### 6.4 YOLO11 de manuscrito medieval (`biglam/medieval-manuscript-yolov11`) [lido]

- Treinado no CATMuS Medieval Segmentation (manuscritos, SegmOnto), pesos **Apache-2.0**, cinco tamanhos.
- Notas (mAP 50:95): texto principal 0,89; capitular 0,35; gravura 0,37; número 0,16; reclamo 0,22. **A linha da música tem números idênticos aos de outras quatro classes** (0,298 / 0,352 / 0,368 / 0,389 / 0,370), o que parece erro de cópia no cartão do modelo: **a nota da música não é confiável**.
- Convertido para ONNX roda como o nosso `doclayout.onnx` (no 3.14, com `onnxruntime`) [dedução]; o Ultralytics, que converte, é AGPL-3.0 (cabe na decisão de 17/09).
- Interessa para Graduale e Horas; a nota baixa de capitular e número diz o mesmo: reforço, não proteção.

### 6.5 Música: achar a pauta

- **Morfologia do OpenCV** (o próprio tutorial "extrair linhas horizontais e verticais" usa uma **partitura** de exemplo) [lido]: abrir a imagem com um traço horizontal comprido separa as linhas da pauta das notas. **Prova no Graduale 222** [medido]: achou **16 linhas compridas, cerca de metade** das ~28 da página, em 0,16 s; a pauta vermelha, fina e levemente torta escapa. Funcionaria como "esta página tem música" (aviso), não como máscara exata.
- **OMMR4all** (Wick, Hartelt e Puppe, 2019, GPL-3.0): feito exatamente para **notação quadrada medieval**; acha linhas de pauta com mais de 99% de acerto e símbolos com 96% [lido no resumo]. Mas é um servidor web com redes próprias: não cabe no programa sem muito trabalho [dedução].
- **oemer** (MIT) e **Audiveris** (AGPL-3.0, Java) são para partitura moderna de 5 linhas; não leem neuma [lido + dedução].
- **Conclusão:** para o Misto não é preciso **entender** a música, só **não apagá-la**, e a rede de segurança já guardou as notas e as pautas do Graduale. Detectar pauta só serve para o aviso e para mandar a área inteira para "letra" [dedução].

---

## 7. Padrões de interface usados por outros

| Padrão | Onde | Serve para nós? |
|---|---|---|
| **Tipos de área desenhados à mão** (texto, imagem, imagem de fundo) com cor da borda por tipo | ABBYY FineReader [lido]; ScanTailor (cinco tipos de zona) [lido] | Já temos: aba Marcar, tipos GRAVURA / LETRA / PAPEL [lido no nosso código]. O "pincel isto é letra" é o tipo LETRA |
| **Ligar/desligar o filtro por folha** | unpaper: `--no-grayfilter` por intervalo de folhas [lido] | Sim: a chave do Misto por livro e por página |
| **Ser conservador por padrão** (na dúvida, guardar) | Archive: soma a página inteira; DjVu: rejeitado vai para o fundo [lido] | Sim: a rede de segurança é isto |
| **Marcar para conferir** onde há dúvida | Nosso 1.3 já manda para "Para revisar" onde os OCRs discordam [lido no nosso código] | Sim: o mesmo caminho para "tinta forte fora das linhas" |
| **Tipos de região à parte para capitular, música, margem** | eynollah, OCR-D (PAGE-XML), SegmOnto [lido] | Como segunda etapa (seção 6) |

---

## 8. O aviso automático ("o programa perceber")

Proposta [dedução, com números da prova]:

- Depois da rede de segurança, somar **a tinta forte guardada fora das linhas e fora das gravuras**. Se passar de um limite (a calibrar no gabarito; na prova, página de texto puro deu 0,1% a 3% e página de música 72% a 75%), ou se houver **um pedaço maior que uma letra grande** ali, a página vai para **"Para revisar"** com o motivo em português comum, por exemplo: *"Há tinta fora do texto que o programa reconheceu (música, capitular ou anotação). Confira se ficou como você quer."* e o lugar marcado em contorno.
- Isso pega o caso que a comparação entre OCRs **não** pega (Graduale 223: os dois perdem o mesmo pedaço).
- Página sem nenhuma linha de OCR: aviso próprio, *"Não achei texto nesta página; usei o preto e branco em tudo o que não é gravura."*

---

## 9. Opções para o Samuel escolher

Todas valem **só dentro do Misto** e **só fora das gravuras** (gravura, foto, moldura e iluminura continuam como no original, pelo detector do 1.2 e pelas zonas à mão).

**Opção A — Rede de segurança (minha recomendação para o padrão de fábrica).**
*Em uma frase:* o texto achado pelo OCR recebe o preto e branco normal; fora dele, o que é tinta forte (nota de música, capitular, número, letrinha de diagrama) também vira preto e branco, e só a mancha clara vai para o branco.
- Prós: não perdeu nada importante nas 13 páginas; tira a escrita espelhada do verso na margem; rápida (décimo de segundo); automática; usa só o que já temos.
- Contras: perde hachura clara de capitular e traço muito fino (dá para afrouxar o limiar); não separa verso **tão escuro** quanto a letra; não resolve a mancha **dentro** das linhas.
- Automática, com o aviso da seção 8 ligado.

**Opção B — Tratar tudo como letra (o Misto do ScanTailor puro).**
*Em uma frase:* tudo o que não é gravura vira preto e branco, como no ScanTailor, sem olhar o OCR.
- Prós: nunca perde letra, nota ou número; não depende do OCR (mais rápido: sem os ~11 s por página do docTR + Kraken).
- Contras: a mancha do verso volta a escurecer, exatamente o defeito que o Samuel mais quer tirar.
- **Liga/desliga por livro e por página**; também é o que o programa usa sozinho quando a página não tem nenhuma linha de OCR.

**Opção C — Só o texto achado (o "só linhas" estrito).**
*Em uma frase:* só o que está nas linhas do OCR vira preto e branco; todo o resto fora das gravuras vira papel branco.
- Prós: a página mais limpa possível em livro só de texto com muita mancha nas margens.
- Contras: **apaga a música do Graduale, capitular não detectada e qualquer linha que o OCR perca.** Nunca de fábrica.
- **Liga/desliga por página**, com o aviso da seção 8 sempre ativo (se houver tinta forte fora das linhas, o programa avisa antes de apagar).

**Opção D — O que sobra fica como no original, só com o papel clareado.**
*Em uma frase:* fora do texto e das gravuras, nada vira preto nem branco puro: a tinta fica como estava e só o papel em volta clareia (como a camada de baixo do Archive e do DjVu).
- Prós: não perde nada e **não escurece** a mancha (ela fica fraca como no original); capitular e hachura saem intactas.
- Contras: a página não sai "papel branco de verdade" fora do texto; a mancha continua visível, só clara; mistura dois aspectos na mesma página.
- Liga/desliga por livro e por página. Útil para manuscrito com música e capitular a pena [dedução].

**Opção E — Detector de regiões de livro antigo (segunda etapa, depois de medir).**
*Em uma frase:* um modelo treinado em livros antigos aponta capitular, música, número de página, reclamo e nota de margem, e essas áreas vão sozinhas para "letra" (ou "gravura", no caso da capitular).
- Prós: dá nome às coisas (o aviso pode dizer "música" ou "capitular"); pode mandar a capitular xilográfica para gravura, guardando as hachuras.
- Contras: acha só metade a dois terços do que deveria nos testes publicados; não foi medido nos nossos livros; o D-FINE roda no motor do Kraken (mais lento e mais pacotes); o YOLO medieval precisa ser convertido. Tem de ser medido no gabarito antes, como foi feito no 1.3.
- Automático, desligado de fábrica até ser medido; entra como **reforço** da opção A, nunca no lugar dela.

**Sempre presente, em qualquer opção:** o pincel/zona **"isto é letra"** (o tipo LETRA que a aba Marcar já tem) e o **"isto é papel"** para corrigir à mão.

### Minha recomendação

- **Padrão de fábrica: A (rede de segurança) com o aviso automático ligado.** É o único caminho que atende às duas regras do Samuel ao mesmo tempo ("o papel saia branco" e "o desenho também saia perfeito") sem apostar que o OCR acerta tudo, e foi o que se comportou bem na prova.
- **Na tela, uma escolha só, de três posições, por livro e por página** (nome sugerido, a decidir): *"O que está fora do texto: Guardar a tinta forte (recomendado) · Guardar tudo · Apagar"*, que são A, B e C. A opção D pode entrar como quarta posição ("Deixar como no original") se o Samuel quiser ver antes.
- **E entra depois**, como reforço medido, junto com o item da mancha do verso para o espelho do verso (5.5).
- Antes de ligar, o implementador deve **medir A nas 32 páginas do gabarito com o detector de gravura ligado**, e o verificador mostrar ao Samuel, lado a lado, A, B e C no Graduale 222, Palatino 9, Opus 165, Boécio 22 e Marial 7.

---

## 10. O que ficou em aberto

- **A prova foi sem o detector de gravura** e com um limiar só; os números do Misto de verdade serão menores e precisam ser refeitos no gabarito inteiro.
- **Verso escuro como a letra** (manuscrito com tinta que atravessou): a rede A não separa; só o espelho do verso (5.5), que não testei.
- **Número de fólio muito claro** (Graduale 222, "Cvij"): nem o preto e branco o pega; some em qualquer opção que use preto e branco. Só D ou uma zona à mão o salvam.
- **Mancha dentro das linhas** (caixas falsas do docTR sobre o verso no Palatino 9; verso entre as linhas no Palatino 10): problema do preto e branco **dentro** da linha, fora do escopo deste documento.
- **Tempo do D-FINE no processador** e nota dele nos nossos livros: não publicados, não medidos. Não instalei nada no motor do Kraken.
- **Nota da música no YOLO medieval**: o cartão do modelo parece ter números copiados de outras classes.
- **Licença dos pesos** do DocLayout-YOLO e do CATMuS: os repositórios dizem AGPL-3.0 / Apache-2.0, mas não achei licença escrita só para o conjunto de dados CATMuS.
- **Pauta por morfologia** achou só metade das linhas no Graduale 222; não tentei melhorar (por faixas, por cor vermelha).
- As imagens da prova ficaram na pasta temporária da sessão, fora do projeto; refazem-se pelo método da seção 4.1.

---

## 11. Links e arquivos consultados (05/10/2026)

**De fora:**
- https://raw.githubusercontent.com/internetarchive/archive-pdf-tools/master/internetarchivepdf/mrc.py (`create_hocr_mask`, `create_threshold_mask`, `create_mrc_hocr_components`, `MIX_THRESHOLD`)
- Haffner, Bottou, Howard, LeCun, "DjVu: Analyzing and Compressing Scanned Documents for Internet Distribution" (ICDAR 1999): https://www.hlevkin.com/hlevkin/04imageprocDoc/DJVU-haffner-99.pdf ; https://leon.bottou.org/research/djvu
- https://github.com/jwilk/didjvu (GPL-2.0, Python 2.7)
- https://raw.githubusercontent.com/unpaper/unpaper/main/doc/unpaper.1.rst (`--grayfilter-*`, `--no-grayfilter`); `unpaper.c` (GPL-2.0-only)
- https://github.com/mittagessen/dfine_kraken ; https://pypi.org/project/dfine_kraken/ (0.4.4, Python ≥ 3.10 e < 3.14, Kraken ≥ 7.1)
- https://zenodo.org/records/18715364 (D-FINE large, notas por classe) ; https://zenodo.org/records/18715373 (medium, lista das 37 classes) ; https://zenodo.org/records/18715381 (small)
- https://github.com/DEFI-COLaF/LADaS (CC-BY-4.0; período e classes) ; https://huggingface.co/datasets/almanach/LADaS
- https://github.com/ponteineptique/YALTAi (GPL-3.0, arquivado em 15/04/2026)
- https://huggingface.co/biglam/medieval-manuscript-yolov11 (Apache-2.0; tabela por classe) ; https://huggingface.co/johnlockejrr/medieval-manuscript-yolov11-seg
- DocLayout-YOLO: https://arxiv.org/abs/2410.12628 (definição de "abandon") ; https://github.com/opendatalab/DocLayout-YOLO (AGPL-3.0)
- PP-DocLayout: https://paddlepaddle.github.io/PaddleX/latest/en/module_usage/tutorials/ocr_modules/layout_detection.html ; https://github.com/RapidAI/RapidLayout (Apache-2.0)
- https://github.com/qurator-spk/eynollah (Apache-2.0; classes, Linux, Python 3.8–3.11)
- OCR-D / PAGE-XML: tipos de região (conhecimento do formato; não reli a especificação hoje)
- OpenCV, "Extract horizontal and vertical lines by using morphological operations": `doc/tutorials/imgproc/morph_lines_detection/morph_lines_detection.md` e `samples/python/tutorial_code/imgProc/morph_lines_detection/morph_lines_detection.py`
- Wick, Hartelt, Puppe, "Staff, Symbol and Melody Detection of Medieval Manuscripts Written in Square Notation Using Deep FCN" (Applied Sciences 2019): https://www.mdpi.com/2076-3417/9/13/2646 ; https://github.com/OMMR4all/ommr4all-server (GPL-3.0)
- https://pypi.org/project/oemer/ (MIT) ; https://github.com/Audiveris/audiveris (AGPL-3.0)
- Rowley-Brooke, Pitié, Kokaram, "A Non-Parametric Framework for Document Bleed-Through Removal" (CVPR 2013): https://openaccess.thecvf.com/content_cvpr_2013/papers/Rowley-Brooke_A_Non-parametric_Framework_2013_CVPR_paper.pdf ; "Enhanced Bleedthrough Correction for Early Music Documents with Recto-Verso Registration" (resumo): https://www.researchgate.net/publication/220722861
- Su, Lu, Tan, "Binarization of historical document images using the local maximum and minimum" (DAS 2010), pelo resumo em https://link.springer.com/article/10.1007/s10032-010-0130-8
- ABBYY FineReader, tipos de área: https://help.abbyy.com/en-us/finereader/15mac/user_guide/areatypes/
- Licenças conferidas pela API do GitHub e pelo PyPI (05/10).

**Do projeto (só leitura):** `CLAUDE.md` (seções 3 e 9), `.claude/agents/pesquisador.md`, `docs/plano/ESTADO-ATUAL.md`, `docs/plano/PLANO-DEFINITIVO.md` (1.2 a 1.6 e Fase 2), `docs/plano/TESTE-SCANTAILOR-MISTO.md`, `docs/pesquisa/fase2-mapa-scantailor.md`, `fase1-1.3-ocr-para-achar-texto.md`, `fase1-1.1-camadas-internet-archive.md`, `treinar-ocr-e-detector.md`, `relatorios/fase1-1.3-comparacao-ocr-2026-09-28/` e `fase1-1.3-comparar-ocr-2026-09-29/` (relatórios), `core/detectar_regioes.py` (classes do DocLayout e cor), `core/ocr_comparar.py`, `core/ocr_kraken.py`, `core/ocr_doctr.py`, `core/ocr_comum.py` (cabeçalhos), `saida_teste/ocr-1.3/` (imagens e linhas), `gabarito/paginas/` (Marial 7, Boécio 22, Palatino 10).
