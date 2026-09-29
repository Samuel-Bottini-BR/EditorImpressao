# OCR de manuscrito direto no Windows, sem WSL

**Data:** 28/09/2026 · **Quem:** agente pesquisador · **Pedido:** gerente, a partir da pergunta do Samuel (28/09): ele quer OCR de manuscrito desde o começo, e o Kraken, o candidato natural, "só roda em Linux". O Kaique (Windows, i5-1235U, 32 GB, sem placa de vídeo dedicada, não é técnico) **não pode ter de instalar WSL à mão**.

**Como ler as marcas:** **[lido]** = está escrito na fonte (link na seção 9). **[medido aqui]** = rodei no PC do Samuel (Ryzen 7 5800H, Windows 11 Home) numa pasta temporária. **[dedução]** = conclusão minha, não conferida.

**O que foi instalado e onde:** nada no `.venv` do programa. Criei dois ambientes de teste **na pasta temporária da sessão** (`C:\Users\fotog\AppData\Local\Temp\claude\d--programas\e4642c9c-...\scratchpad\`): `kraken312` (Python 3.12 que já existia na máquina) e `kraken314` (Python 3.14), mais os modelos baixados do Zenodo e cópias de 3 páginas do gabarito (Graduale 222, Horas 47, Palatino 57; o `gabarito/` só foi lido). A pasta ocupa uns 2,5 GB e pode ser apagada. Nada em `core/`, `ui/`, `docs/plano/` nem `gabarito/` foi mexido.

---

## 1. A resposta em cinco frases

1. **Dá, e sem WSL:** o Kraken 7.1.1 instalou com um `pip` comum e rodou no Windows deste PC, num Python 3.12 separado. Leu bem as nossas páginas: a Horas 47 saiu praticamente sem erro, e o Graduale 222 e o texto corrido do Palatino 57 saíram com poucos erros. As pautas de música não foram tomadas por linha de texto **[medido aqui]**.
2. **Recomendação:** o instalador leva um **"motor de manuscrito" pronto**, com um Python 3.12 só dele, o Kraken e os modelos. O programa (que continua no 3.14) chama esse motor por baixo. O Kaique não faz nada: não precisa de administrador nem de reiniciar. O custo é **~1,2 GB instalado** e **~12 a 25 s por página**.
3. **Os modelos a levar só reconhecem**, sem gerar texto livre: CTC, em que cada letra sai de um pedaço da imagem. São o **CATMuS Medieval** (CC-BY 4.0) para o gótico e o latim medieval, o **PP-OCRv6 do Kraken 7.1** (Apache-2.0), que foi o melhor na Horas, e o **McCATMuS** (CC-BY 4.0) para a escrita dos séculos XVI a XVIII. **TrOCR, PARSeq e a Party são geradores** (um decodificador escreve o texto palavra por palavra e pode inventar). Ficam fora enquanto o Samuel não decidir (item 7.1).
4. **O risco principal:** o autor do Kraken escreveu em 18/06/2026 que não tem Windows e não dá suporte ao sistema **[lido]**. Então cada versão nova do Kraken tem de ser testada por nós antes de ir para o instalador, com as versões das bibliotecas travadas. No Python 3.14, com bibliotecas mais novas, 2 de 13 linhas saíram **vazias, sem aviso** **[medido aqui]**.
5. **As outras saídas são piores.** Instalar o WSL pelo nosso instalador **pede administrador e reinício** **[lido, Microsoft]**, e um Linux embutido esbarra na mesma exigência ou fica lento demais. Para depois fica um caminho mais leve: os modelos do Kraken **exportaram para ONNX** e deram o mesmo texto **[medido aqui]**, o que pode tirar o PyTorch e o segundo Python. Mas exige trazer para o programa o código do Kraken que transforma o mapa em linhas.

---

## 2. Tabela das opções

| Opção | O que é | Licença | Só reconhece ou gera texto? | Roda aqui (Windows)? | Roda no notebook do Kaique? | O que o Kaique faz |
|---|---|---|---|---|---|---|
| **a1. Kraken nativo, Python privado 3.12/3.13** | pip no Windows, empacotado junto do programa | Apache-2.0 (Kraken); modelos CC-BY 4.0 / Apache-2.0 / CC0 / MIT | **Só reconhece** (CTC) | **Sim** [medido aqui] | Sim [dedução: mesmo Windows 11 64 bits, sem placa de vídeo] | **Nada** |
| a2. Kraken no Python 3.14 do programa | pip forçado, bibliotecas sem as versões fixadas | idem | Só reconhece | Roda, mas **perdeu 2 de 13 linhas sem avisar** [medido aqui] | não recomendado | nada |
| a3. Kraken por conda | — | — | — | **Não existe mais** (retirado no Kraken 6.0) [lido] | — | — |
| **a4. Modelos do Kraken em ONNX, dentro do programa** | a rede roda no `onnxruntime` que o programa já tem | idem | Só reconhece | Rede: **sim, mesmo texto** [medido aqui]; o resto (achar linhas) falta portar | Sim [dedução] | Nada |
| b1. PyLaia (Teklia) | reconhecedor CTC, modelos medievais | MIT (programa e modelos) | Só reconhece (com opção de "modelo de língua" de letras) | **Não na prática**: Python 3.9–3.10, torch 1.13 e uma extensão C++ só com pacote Linux [lido + dedução] | não | — |
| b2. Calamari | reconhecedor CTC em TensorFlow | GPL-3.0 (programa); modelos MIT | Só reconhece | Provável com Python ≤3.11 [dedução], mas **não tem modelo de manuscrito** [lido] | — | — |
| b3. docTR / OnnxTR | detector + reconhecedor | Apache-2.0 | CRNN só reconhece; PARSeq/MASTER/SAR geram | Sim (ver documento do 1.3) | Sim | — mas **não tem modelo de manuscrito** [lido via busca] |
| b4. PARSeq | reconhecedor de texto de cena | Apache-2.0 | **Gera** (autorregressivo, com modelo de língua interno) [lido] | Sim [dedução] | Sim | — treinado em placa de rua, não em livro |
| b5. TrOCR (e ajustes medievais) | codificador de imagem + **decodificador que gera palavras** | MIT (os ajustes medievais que conferi) | **Gera: pode inventar** [lido] | Sim [dedução] | Sim | **proibido sem decisão do Samuel** |
| b6. Party (do autor do Kraken) | página inteira, Swin + **Llama** | Apache-2.0 | **Gera** (decodificador autorregressivo) [lido] | não conferi (instala pelo código-fonte; o README não diz o sistema) | — | **proibido sem decisão do Samuel** |
| c. WSL instalado pelo nosso instalador | `wsl --install` + Linux nosso importado | — | depende do motor (Kraken: só reconhece) | Sim (este PC já tem Ubuntu no WSL, ver 7) | Só se a virtualização estiver ligada na BIOS [dedução] | **Aceitar o pedido de administrador e reiniciar** [lido] |
| d. Linux mínimo junto do programa | WSL importado (= c) ou máquina virtual QEMU | — | idem | QEMU rápido também pede um recurso do Windows ligado (admin) [lido]; sem ele, emulação lenta [dedução] | idem c | idem c |
| e. Outras ideias | rodar no PC do Samuel; serviço na internet; detector de linhas YOLO | ver seção 4.5 | — | — | — | — |

---

## 3. O teste (medido aqui)

### 3.1 Instalação no Windows, sem WSL

- `python -m venv` com o **Python 3.12** da máquina, depois `pip install kraken`: **instalou o Kraken 7.1.1** com o torch 2.14.0 (só processador), scipy 1.15.3, scikit-image 0.25.2 e shapely 2.1.2. O `coremltools` 9.0 **não tem pacote pronto para Windows** [lido no PyPI], mas o pip o montou sozinho como Python puro, e ele funcionou para ler os modelos `.mlmodel` **[medido aqui]**.
- O comando `kraken` **quebra no Windows sem `PYTHONUTF8=1`**, porque não consegue escrever o sinal "✓" na janela preta **[medido aqui]**. Com a variável ligada, tudo rodou. O mesmo ajuste aparece nos pedidos de mudança para Windows mandados ao Kraken em junho/2026 **[lido]**.
- Rodar a mesma página duas vezes deu **o mesmo texto** **[medido aqui]**.
- Tamanho do ambiente: **1,2 GB**. Os maiores são torch (539 MB), scipy (125), pyarrow (88), sympy (74), scikit-learn (45), numpy (33), scikit-image (30) e coremltools (24) **[medido aqui]**.
- Memória: pico de **1,4 GB** numa página do Palatino de 1929×2943 com dois modelos carregados **[medido aqui]**.

### 3.2 Qualidade nas nossas páginas

A segmentação usou o modelo `blla` que vem dentro do Kraken 7.1.1.

**Graduale 222** (gótico do séc. XIV, com pautas vermelhas e neumas): o `blla` achou **13 pedaços de linha, todos no texto embaixo das pautas, nenhum na música**. Texto:

| Modelo | Saída (trecho) |
|---|---|
| CATMuS Medieval 1.6.0 | "hi mole sci essent / bam me cilicio / moue / et humilia / bam in ieuini / O animam meam / et oratio mea / i suui meo conuer / tetur. ꝟsus. Iudica do mine nocentes me / expug / na impugnantes me / appreheude ar ma et scu / tum" |
| PP-OCRv6 medium (Kraken 7.1) | "chi mole᷑ sti essent / bam me cilicio / idlie / … / i sinu meo conuer / tetur. uesus. Iudica do mine nocentes me / … / appreheude ar ma et scu / tum" |
| Manicule 2026 Latin Medieval | "chi mole sti essent / bammecilicio / … / tetur uersus judica domine nocentes me / … / apprehende arma et scu / tum" |

- O texto é o Salmo 34 ("…induebam me cilicio et humiliabam in ieiunio animam meam et oratio mea in sinu meo convertetur. Versus. Iudica Domine nocentes me, expugna impugnantes me. Apprehende arma et scutum").
- Os três acertam a maior parte das palavras. Os erros ficam na palavra abreviada "induē" ("moue", "idlie", "moie") e em letras sozinhas.
- As palavras saem partidas onde o copista espaçou as sílabas para a música ("do mine", "ar ma"). A página está em baixa resolução (961×1396).
- Não calculei a taxa de erro: a transcrição de referência teria de ser feita por quem lê a abreviação com segurança.

**Horas 47** (Livro de Horas de Luís XIV, caligrafia francesa com s longo, texto dentro de iluminura): taxa de erro de caractere contra uma transcrição que eu fiz olhando a imagem. Na conta, o s longo virou "s" e os hifens de fim de linha foram tirados.

| Modelo | Erro de caractere |
|---|---|
| PP-OCRv6 medium | **0,0%** (mistura "s" e "ſ" de linha para linha, o que o cartão do modelo avisa) |
| PP-OCRv6 small | **0,0%** |
| McCATMuS (séc. XVI–XXI) | 1,5% ("saire", "vmne", "recevou" e uma "linha" falsa "2" na iluminura) |
| CATMuS Medieval | 7,6% (modelo de outro período: "E.SUS", "Peau", "uin") |

Só **uma "linha" falsa** apareceu dentro da iluminura, e só com um modelo.

**Palatino 57** ("Lettera Notaresca", xilogravura de escrita notarial, 1545):

- O **texto corrido saiu bom** nos três modelos. Com o CATMuS Medieval: "N nomine domini Amen. In mei Notarii publici / testiumq infrascriptorum ad hoc specialiter uocato. / … / tutus uenerabilis et circunispectus uir dominub."
- A capitular "I" ornamentada ficou de fora da primeira palavra ("N nomine").
- As **linhas de alfabeto de amostra** saíram lixo, como era de esperar.
- O PP-OCRv6 medium **pôs letras cirílicas e gregas** nelas ("AвСеFдjkмnоp", "τοκу3"). É o risco de um modelo multilíngue.
- Uma "linha" falsa, só um número ("6" ou "14", conforme o modelo), foi achada no ornamento.

**Atenção aos modelos que "expandem" as abreviações.** O Manicule escreveu "testiumque" e "etc." onde a página tem "testiumq3" e "⁊c". Esses modelos são CTC e não geram texto livre, mas foram **treinados para escrever letras que não estão desenhadas** (abreviação resolvida, u/v e maiúsculas modernizados), como está escrito nos cartões do Manicule e do TRIDIS **[lido]**. Para um projeto que não quer nada inventado, a escolha coerente é o modelo **grafemático**: o CATMuS "não resolve abreviação nenhuma" **[lido]** [dedução para a escolha].

### 3.3 Tempo neste PC (Ryzen 7 5800H)

| Etapa | Tempo |
|---|---|
| Abrir o Kraken (importar) | 5 a 6 s, uma vez por sessão |
| Carregar os modelos | 1 a 2,5 s cada, uma vez |
| **Achar as linhas** (`blla`), por página | **11 a 14 s** (Graduale 11,2; Horas 12,8 a 18,7; Palatino 13,6). Pôr 4 linhas de execução não ajudou |
| Reconhecer, CATMuS (rede pequena, com LSTM) | 1,0 a 3,1 s por página (0,08 a 0,15 s por linha) |
| Reconhecer, PP-OCRv6 small | 1,8 a 5,4 s por página |
| Reconhecer, PP-OCRv6 medium | 5,3 a 15,7 s por página (0,4 a 0,75 s por linha) |
| Comando `kraken` completo, da abertura ao texto, uma página | 39 a 72 s. A diferença para a soma acima deve ser abrir o programa e criar os processos auxiliares, que no Windows nascem do zero [dedução] |

**Onde vai o tempo de achar as linhas** (perfil de uma página da Horas, 15,6 s):

- a rede neural gasta só **~2 s**;
- o resto é pós-processamento em Python (transformar o mapa em linhas): um filtro de sulcos do scikit-image (`sato`) leva **~7 s**, e o contorno de cada linha leva **~4 s**.

Por isso trocar a rede por ONNX quase não acelera a segmentação (3.4).

### 3.4 Exportar para ONNX (a pergunta da letra a)

O autor do Kraken escreveu em 2024 que o ONNX "não se dá bem com os tamanhos variáveis" dos modelos de reconhecimento **[lido, issue 614]**. No teste de hoje, com o exportador comum do PyTorch (`torch.onnx.export`, largura da linha variável), deu certo:

| Rede | Exportou? | Mesmo texto que o Kraken? | Tempo só da rede, PyTorch → onnxruntime |
|---|---|---|---|
| CATMuS Medieval (convolução + LSTM) | sim, direto | **21/21** linhas (Horas) e **13/13** (Graduale); maior diferença 1e-4 | 2,5 → 0,7 s e 1,5 → 0,25 s |
| PP-OCRv6 medium | sim, com **uma linha trocada** (uma média no fim da rede usa a altura da linha como tamanho, e a altura é fixa) | **21/21** e **13/13** | 12,2 → 7,5 s e 3,5 → 2,2 s |
| PP-OCRv6 small | idem | **21/21** | 4,0 → 1,7 s |
| `blla` (segmentação) | sim, direto | mapa praticamente igual: menos de 0,25% dos pontos diferem mais de 0,01, e ~0% muda de lado no limiar | ~2,5 s nos dois (não acelera) |

- A exportação foi feita numa linha só (a menor, 60 px de largura) e valeu para linhas de até 1500 px.
- Tamanho dos arquivos `.onnx`: 16 MB (CATMuS), 13 MB (small) e 64 MB (medium).

**O que falta para o caminho ONNX [dedução]:**

- trazer para o programa, do código do Kraken (Apache-2.0), o pós-processamento da segmentação (`kraken/lib/segmentation.py`, `vgsl/spred.py`), o recorte e o desentortar de cada linha, e a decodificação CTC com o alfabeto do modelo;
- conferir que o resultado é igual ao do Kraken.

Esse código usa scipy, scikit-image e shapely, que existem para o 3.14. Mas foi justamente no 3.14, com scikit-image 0.26 e scipy 1.18, que o recorte de linha perdeu 2 linhas (3.5). A causa ainda não foi achada.

### 3.5 Kraken dentro do Python 3.14 (o do programa)

- O pip **recusa** (o Kraken pede Python < 3.14). Forcei com `--ignore-requires-python` e instalei as bibliotecas sem as versões que o Kraken fixa.
- Resultado: **roda**, e a segmentação do Graduale saiu **idêntica** à do 3.12.
- Mas **2 das 13 linhas saíram vazias, sem erro nem aviso**. Repeti e deu igual, inclusive sem processos paralelos **[medido aqui]**.
- Conclusão **[dedução]**: as versões fixadas no Kraken existem por um motivo, e usar o 3.14 com bibliotecas novas é arriscar texto sumido em silêncio.

---

## 4. Cada opção em detalhe

### 4.1 (a) O Kraken no Windows nativo

**Lido na fonte:**

- README: "roda em Linux ou Mac OS X", Python 3.10 a 3.13, Apache-2.0.
- PyPI (7.1.1, 04/09/2026): pacote Python puro (serve em qualquer sistema) e marca "Operating System :: POSIX". Depende de `coremltools~=9.0`, `torch<=2.14,>=2.9`, `scipy~=1.15.3`, `scikit-image~=0.25.2`, `lightning==2.6.1` e outras.
- 6.0.0 (09/2025): "a instalação pelo anaconda acabou" (o coremltools não é mantido no conda-forge). **Conda está fora.**
- 7.0 (04/2026): o formato padrão dos modelos passou a ser **safetensors**. Os modelos antigos são **CoreML** (`.mlmodel`), que o Kraken usa só como "caixa" dos pesos; ele nunca roda o CoreML da Apple. Há rotina para **converter** `.mlmodel` em `.safetensors` (`kraken/models/convert.py`). Não existe exportação para ONNX pronta.
- 7.0.3 (07/2026): corrigido um erro que derrubava o programa "em sistemas que usam `spawn` para os processos" (é o caso do Windows).
- 7.1 (05/08/2026): arquitetura nova de reconhecimento baseada no **PP-OCRv6**, com modelos-base multilíngues tiny, small e medium treinados em "manuscritos e impressos históricos". O código (`kraken/lib/ppocr/heads.py`) e o cartão do modelo dizem: "reconhecedor convencional baseado em **CTC**", "sem alucinações". A cabeça auxiliar NRTR (que é autorregressiva) só existe no treino e "é descartada na inferência".
- Pedidos de mudança #783 a #787 (junho/2026, de um terceiro e gerados por IA): trocar `fork` por `spawn`, importar o coremltools só quando precisar, abrir arquivos em UTF-8, `PYTHONUTF8=1`, PDF pelo `pypdfium2`. Eles dizem ter testado "no Windows 11 com Python 3.13.13". **O autor fechou todos sem aceitar** (18/06/2026): "Não tenho acesso a máquinas Windows e não posso dar suporte à plataforma de nenhum jeito significativo."
- Issue 411 (2023, do autor): "não é suportado oficialmente… alguém rodou tudo no Ubuntu/WSL".

**Medido aqui:** ver a seção 3 (instala e roda no Python 3.12; precisa de `PYTHONUTF8=1`).

**Prós:**
- é o motor mais forte em manuscrito histórico, com o maior acervo de modelos prontos (4.4);
- faz também a segmentação em linhas, que é o que o item 1.3 precisa;
- saída em ALTO, PageXML e hOCR [lido].

**Contras:**
- sem suporte oficial no Windows;
- grande (1,2 GB) e lento para achar linhas (11 a 14 s por página aqui);
- exige um **segundo Python** (3.12 ou 3.13) ao lado do 3.14 do programa. Não é rebaixar o Python do programa, mas é um segundo ambiente para manter.

**Como empacotar, sem o Kaique fazer nada [dedução]:**
- o "pacote incorporável" do Python oficial é um zip que "não precisa de instalação nem de administrador" e é feito "para ir dentro do instalador de outro programa" [lido, docs.python.org]; outra saída é congelar o motor com o PyInstaller, que o `empacotar.py` já usa;
- o programa chama o motor como um processo à parte (`motor.exe pagina.png → linhas.json`), com `PYTHONUTF8=1`, uma página por vez, em segundo plano;
- as bibliotecas vão **travadas nas versões testadas**.

### 4.2 (b) Outros motores

- **PyLaia** (Teklia, MIT):
  - Modelos prontos **MIT** no Hugging Face. **HOME-Alcar** é latim medieval de cartulários, com erro de caractere de 8,35% sem modelo de língua e 7,85% com ele. **Himanis** é francês medieval de registros, com 9,87% e 8,87% [lido].
  - Reconhecedor CTC (só reconhece). O "modelo de língua de 6 letras" opcional pesa as leituras pelo que é comum no texto de treino. É da família da opção c do item 7.1 [dedução].
  - **Não roda no Windows na prática.** A versão 1.1.2 pede Python 3.9 ou 3.10, torch 1.13 e `nnutils-pytorch`, que só tem pacote para Linux [lido no PyPI]. No Windows seria preciso compilar C++ [dedução].
  - Também não acha linhas: precisa de outro detector [dedução].
- **Calamari** (GPL-3.0; modelos MIT):
  - O `tfaip` exige `tensorflow<2.16` e `tensorflow-addons` [lido]. Isso prende a Python antigo; acho que no máximo o 3.11 [dedução].
  - **Todos os modelos prontos são de impresso** (GT4HistOCR, Fraktur, antiqua, francês dos séc. XVII a XIX). **Nenhum é de manuscrito** [lido]. Não resolve a pergunta.
- **docTR / OnnxTR** (Apache-2.0):
  - Rodam no 3.14 (documento do 1.3). Segundo a discussão do docTR, "não vem com modelo de escrita à mão" [lido via busca].
  - O reconhecedor CRNN é CTC. PARSeq, MASTER e SAR são decodificadores que geram.
- **PARSeq** (Apache-2.0): decodificação "autorregressiva", com "modelo de língua interno" e refinamento [lido]. Foi treinado em texto de cena (placas, fotos) [lido]. **Gerador** e fora do domínio.
- **TrOCR** (Microsoft):
  - A própria descrição diz que usa o transformador "para **gerar** texto em pedaços de palavra" [lido]. Um cartão de modelo derivado registra "alucinações graves" fora da língua de treino [lido].
  - Existem ajustes medievais: `medieval-data/trocr-medieval-textualis` (MIT; erro de 3,55% na validação, "não foi testado formalmente") e `LaMOP/TrOCR_Manicule_2026_Latin_Medieval` [lido].
  - **É gerador: pode escrever palavra latina plausível que não está na página.** Pela regra do projeto, fica fora sem decisão do Samuel.
- **Party** (Benjamin Kiessling, o autor do Kraken; Apache-2.0):
  - Lê a página inteira com um codificador Swin e um **decodificador Llama autorregressivo** [lido]. Modelos de 518 MB (base) e 858 MB (línguas europeias) [lido].
  - **Gerador.** Mesma restrição do TrOCR.
- **Orli** (do mesmo autor; Apache-2.0): acha as linhas e a ordem de leitura com um decodificador autorregressivo [lido]. Não escreve texto, só gera **posições de linha**, então "aponta". Ainda assim pode "inventar" uma linha onde não há [dedução]. O pacote marca só POSIX e pede kraken ~7.0.2; o modelo tem 594 MB [lido]. Não testei.

### 4.3 (c) Instalar o WSL pelo nosso instalador

**Lido (Microsoft Learn):**
- `wsl --install`: "Abra o PowerShell em modo **administrador** … e depois **reinicie** a máquina".
- A instalação manual liga a "Plataforma de Máquina Virtual" (`VirtualMachinePlatform`) como administrador, e a máquina "vai precisar de capacidades de virtualização" e de **reinício**.
- Existe `--no-distribution` (instala o WSL sem Linux), e `wsl --import <nome> <pasta> <arquivo.tar>` importa um Linux nosso a partir de um `.tar`.

**Então [dedução]:**
- dá para o instalador fazer quase tudo sozinho: ligar o WSL (pedindo administrador), pedir o reinício e, na primeira abertura, importar um Linux nosso já com o Kraken;
- mas o Kaique teria de **aceitar o aviso de administrador** (ou digitar a senha, se a conta dele não for de administrador) e **reiniciar o computador**;
- se a virtualização estiver desligada na BIOS do Galaxy Book2, ele não resolve sozinho.

Riscos [dedução]:
- uma máquina virtual escondida ocupando memória enquanto roda;
- a primeira chamada leva alguns segundos para ligar o Linux;
- atualizações do Windows e do WSL fora do nosso controle;
- arquivos de dois "mundos" (`C:\` visto como `/mnt/c`);
- tamanho maior que o da opção a1 (Linux + Python + torch).

O próprio documento do 1.3 já decidiu: "fica fora do programa quem exigir WSL… no notebook do Kaique, a menos que ganhe com folga". **O teste da seção 3 mostra que o Kraken não precisa do WSL**, então o WSL deixou de ser necessário.

### 4.4 (d) Empacotar um Linux mínimo

- **Pelo WSL** (um `.tar` nosso importado): é a opção c e tem a mesma exigência de administrador e reinício [lido].
- **Por máquina virtual (QEMU):** a aceleração no Windows (WHPX) "exige o recurso Plataforma do Hipervisor do Windows instalado", ligado pelo `DISM` [lido]. Isso também pede administrador e reinício [dedução]. Sem ela, o QEMU emula o processador em software, muitas vezes mais devagar [dedução]. **Não compensa.**
- Docker Desktop também depende do WSL 2 ou do Hyper-V [dedução, não conferi hoje].

### 4.5 (e) Outras ideias

1. **O motor privado da opção a1** é a "outra ideia" que resolve: nenhum Linux, nenhum administrador.
2. **ONNX dentro do programa** (a4): tira o PyTorch (539 MB) e o segundo Python; o `onnxruntime` já está no programa. Falta portar e conferir o pós-processamento (3.4). É bom como segundo passo, depois que o a1 provar o valor com o Samuel [dedução].
3. **Transcrever no PC do Samuel**, pelo WSL que agora já tem Ubuntu (seção 7), e entregar o PDF pronto ao Kaique. Serve para a Fase 7, não para o uso diário do Kaique.
4. **Serviço pela internet** (Transkribus, eScriptorium hospedado): não é offline, manda página de livro raro para fora e depende de conta e créditos. Não pesquisei a fundo. Não recomendo para o programa.
5. **Detector de linhas YOLO feito para manuscrito medieval** (Manicule 2026 Yolo-Seg TextRegion/TextLine; pesos **CC0**, 6,6 MB e 141,7 MB; biblioteca `ultralytics` **AGPL-3.0**) [lido]. O YOLO exporta para ONNX [dedução], o que poderia trocar o pós-processamento lento do `blla` (7 a 11 s por página) na hora de só achar linhas (item 1.3). Não testei.

---

## 5. Modelos prontos que servem aos nossos livros

Todos estão no repositório de modelos do Kraken no Zenodo (comunidade `ocr_models`, 81 registros em 28/09/2026) **[lido]**. Nenhum deles gera texto livre (são CTC), com a ressalva dos que "expandem" abreviação.

| Modelo | Material | Transcrição | Licença | Tamanho | Nossa página |
|---|---|---|---|---|---|
| **CATMuS Medieval** 1.6.x (22/07/2026) | séc. VIII a XVI; francês antigo e médio, latim, espanhol, italiano; textualis, cursiva, híbrida; litúrgico, literário, documental (dados: 160 mil linhas, 200+ manuscritos) | **grafemática, sem resolver abreviação** | CC-BY 4.0 (citar autores) | 16,4 MB `.mlmodel` | **Graduale**, Palatino (notaresca) |
| **PP-OCRv6** tiny / small / medium (Kraken 7.1, 04/08/2026) | 44 línguas; manuscrito e impresso; latim medium 6,45% e small 9,12% de erro; francês médio 3,41%; italiano 2,89% | mistura convenções; "pode resolver abreviação de modo imprevisível" | Apache-2.0 | 2,8 / 13,1 / 63,8 MB `.safetensors` | **Horas** (0% no teste), Graduale |
| **McCATMuS** (09/2024) | séc. XVI a XXI; manuscrito, impresso e datilografado; 7 línguas | diretrizes CATMuS | CC-BY 4.0 | 16,2 MB | Horas (1,5%) |
| Generic CREMMA (2023) | latim e francês antigo, séc. VIII a XV | grafemática | CC-BY 4.0 | 22,8 MB | Graduale (não testei) |
| Manicule 2026 Latin Medieval | cartas, séc. X a XIV | **expande abreviação**, normaliza | CC0 | 16,2 MB | testei no Graduale e no Palatino |
| TRIDIS v2 | documentos medievais e modernos, séc. XI a XVI | **expande**, maiúsculas e pontuação modernas | MIT | 25,1 MB | não testei |
| CATMuS Gothic Print; Latin Incunabula | impressos góticos (não manuscritos) | grafemática | CC-BY 4.0; CC-BY-SA 4.0 | ~23 MB | Siebmacher, Rhetorica (para a Fase 7) |
| `blla` (segmentação) | linhas em manuscrito e impresso; há um novo, de 21/09/2026, treinado em 11 mil páginas | — | Apache-2.0 | 5 MB | usei o que vem no Kraken 7.1.1 |

- **HTR-United** é um **catálogo de conjuntos de treino** (imagem + transcrição em ALTO/PAGE), cada um com a sua licença, e não de modelos prontos [lido]. Serve para a Fase 7 (treinar).
- CC-BY obriga a **dar o crédito** (autores e projeto) em algum lugar do programa ou da documentação.
- CC-BY-SA obriga, além disso, a distribuir derivados na mesma licença. Só vale se treinarmos em cima do modelo.

---

## 6. Tempo no notebook do Kaique (dedução, a medir)

- O i5-1235U tem 2 núcleos rápidos e 8 econômicos, a 15 W.
- A parte lenta (achar linhas) é Python com scipy num núcleo só. Num núcleo, o i5 é parecido com o Ryzen 7 5800H daqui, mas esquenta e baixa a velocidade em trabalho longo.
- Estimativa grosseira, **só para planejar**:

| Com o modelo… | Por página no notebook |
|---|---|
| CATMuS Medieval (achar linhas + ler) | ~15 a 30 s |
| PP-OCRv6 medium | ~20 a 45 s |
| Livro de 300 páginas, CATMuS | ~1,5 a 2,5 horas |

Isso só cabe **em segundo plano, com barra de progresso**, nunca na prévia (regra 6 do plano). Tem de ser medido no notebook, junto com a rodada da 0.6.

---

## 7. Recomendação

1. **Não instalar WSL no notebook do Kaique.** Montar um **motor de manuscrito**: Python 3.12 (ou 3.13) próprio, com Kraken 7.1.1 e as bibliotecas **travadas nas versões testadas**, chamado pelo programa como processo à parte, com `PYTHONUTF8=1`. Levar os modelos **CATMuS Medieval** (gótico/latim) e **PP-OCRv6 small ou medium** (Horas, caligrafia moderna). **Não** levar os que expandem abreviação. **Não** levar TrOCR, PARSeq nem Party.
2. **Separar em dois pacotes** [dedução]: o instalador normal (hoje com 120 MB) e um "pacote de manuscrito" opcional (~1,2 GB instalado). Assim quem não usa manuscrito não carrega o peso.
3. **Para o item 1.3 (achar texto):** o Kraken pode entrar na comparação **sem WSL** (o K1 do documento do 1.3), rodando assim. Mas custa ~12 s por página só para achar linhas neste PC, contra décimos de segundo a ~1 s dos outros detectores (pelas fontes daquele documento).
4. **Depois**, se o Samuel aprovar o motor: estudar o caminho ONNX (a4) para tirar o PyTorch e o segundo Python, e o detector YOLO de linhas para acelerar.
5. **Antes de ir ao Kaique:** rodar o motor no notebook dele (tempo e memória) e conferir, no PC do Samuel com o WSL/Ubuntu, que o texto do Windows é igual ao do Linux nas páginas do gabarito.

**Observação para a gerente.** Transcrever (OCR que produz texto) está na **Fase 7** do plano; a Fase 1 só acha onde está o texto. "OCR de manuscrito desde o começo" muda a ordem do plano, e só o Samuel muda o plano. Esta pesquisa responde se **dá**, não **quando**.

**Achado de passagem:** o `wsl -l -v` deste PC mostra hoje uma distribuição **Ubuntu (WSL 2, parada)**. O documento do 1.3 e o plano de execução da Fase 1 diziam que não havia Linux no WSL. Alguém instalou depois.

---

## 8. O que ficou em aberto

- **Nada foi testado no notebook do Kaique.** Tempo, memória e virtualização são dedução.
- **Não conferi** se o texto no Windows é igual ao do Kraken no Linux. Só conferi que se repete no Windows e que a segmentação do 3.14 é igual à do 3.12.
- **Por que 2 linhas somem no Python 3.14** com as bibliotecas novas: não investiguei a causa (desconfio do recorte da linha com o scikit-image 0.26). Isso importa se um dia o caminho ONNX usar o código do Kraken no 3.14.
- **Taxa de erro no Graduale e no Palatino:** só avaliei a olho. Falta uma transcrição de referência feita por quem lê abreviação medieval. O Palatino tem vários tipos de letra, e testei **uma** página (a notaresca).
- **Tamanho comprimido do motor no instalador:** não medi. Chuto 300 a 500 MB [dedução].
- **Sem `PYTHONUTF8=1` o comando quebra.** Pelo jeito de chamada que proponho (processo nosso) basta ligar a variável, mas isso tem de ser testado no pacote final.
- **Suporte:** o autor não aceita correções para Windows. Se uma versão futura quebrar no Windows, ficamos presos à última que funcionou, ou mantemos um remendo.
- **Licença do Windows/WSL e da Party para distribuição:** não li as condições do WSL; a Party está fora de qualquer jeito por ser geradora.
- Não li o artigo do OMMR4all (texto embaixo de neuma; a página devolveu 403). Não achei fonte específica sobre Kraken em graduais. O resultado no Graduale 222 é o do teste.

---

## 9. Links consultados (28/09/2026)

**Kraken**
- https://github.com/mittagessen/kraken (README, licença)
- https://pypi.org/pypi/kraken/json (7.1.1, dependências, "POSIX", Python < 3.14)
- https://pypi.org/pypi/coremltools/json (9.0 sem pacote Windows)
- https://github.com/mittagessen/kraken/releases (6.0.0: fim do conda; 7.0: safetensors e plugins; 7.0.3: correção do `spawn`; 7.1: PP-OCRv6)
- https://github.com/mittagessen/kraken/pull/783 · /784 · /785 · /786 · /787 (Windows, fechados pelo autor em 18/06/2026)
- https://github.com/mittagessen/kraken/issues/614 (ONNX, 2024) · https://github.com/mittagessen/kraken/issues/411 (Windows, 2023)
- Código: `kraken/lib/ppocr/model.py`, `heads.py`, `network.py`, `backbone.py`; `kraken/models/loaders.py`, `convert.py`, `ctc.py`; `kraken/configs/base.py`
- https://kraken.re/main/getting_started.html
- https://arxiv.org/abs/2606.13108 (PP-OCRv6)

**Modelos no Zenodo** (https://zenodo.org/communities/ocr_models)
- https://zenodo.org/records/21488839 (CATMuS Medieval)
- https://zenodo.org/records/21788403 · /21788405 · /21788410 (PP-OCRv6 tiny, small, medium)
- https://zenodo.org/records/13788177 (McCATMuS)
- https://zenodo.org/records/7631619 (Generic CREMMA)
- https://zenodo.org/records/20676471 (Manicule Latin Medieval)
- https://zenodo.org/records/21195087 (Manicule Français Moderne)
- https://zenodo.org/records/21243273 (Manicule YOLO-Seg)
- https://zenodo.org/records/13862096 (TRIDIS v2)
- https://zenodo.org/records/10599911 (CATMuS Gothic Print)
- https://zenodo.org/records/11113737 (Latin Incunabula)
- https://zenodo.org/records/22879549 (`blla` novo)
- https://zenodo.org/records/20642057 · /15764161 (Party)
- https://zenodo.org/records/20558179 (Orli)

**Dados**
- https://huggingface.co/datasets/CATMuS/medieval
- https://github.com/HTR-United/htr-united

**Outros motores**
- https://github.com/mittagessen/party · https://pypi.org/project/orli/
- https://pypi.org/project/pylaia/ · https://pypi.org/project/nnutils-pytorch/ · https://huggingface.co/Teklia/pylaia-home-alcar · https://huggingface.co/Teklia/pylaia-himanis
- https://pypi.org/project/calamari-ocr/ · https://pypi.org/project/ocrd-fork-tfaip/ · https://github.com/Calamari-OCR/calamari_models
- https://pypi.org/project/python-doctr/ · https://pypi.org/project/onnxtr/ · https://github.com/mindee/doctr/discussions/2034 (via busca)
- https://github.com/baudm/parseq
- https://arxiv.org/abs/2109.10282 (TrOCR)
- https://huggingface.co/medieval-data/trocr-medieval-textualis · https://huggingface.co/LaMOP/TrOCR_Manicule_2026_Latin_Medieval (via busca) · https://huggingface.co/ifesther/trocr-spanish-handwritten · https://arxiv.org/abs/2606.24302
- https://pypi.org/project/ultralytics/ (AGPL-3.0)

**Windows, WSL e máquina virtual**
- https://learn.microsoft.com/en-us/windows/wsl/install · https://learn.microsoft.com/en-us/windows/wsl/install-manual · https://learn.microsoft.com/en-us/windows/wsl/basic-commands · https://learn.microsoft.com/en-us/windows/wsl/use-custom-distro
- https://www.qemu.org/docs/master/system/whpx.html
- https://docs.python.org/3.13/using/windows.html (pacote incorporável)

**Locais**
- `docs/plano/OCR-PESQUISA.md`, `docs/plano/PLANO-DEFINITIVO.md`, `docs/plano/ESTADO-ATUAL.md`, `docs/pesquisa/fase1-1.3-ocr-para-achar-texto.md`, `relatorios/fase1-plano-de-execucao-2026-09-28/`, `CLAUDE.md`
- Páginas do gabarito copiadas (só leitura): `graduale_p222.png`, `horas_p047.png`, `palatino_p057.png`
