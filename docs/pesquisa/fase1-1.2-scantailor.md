# Fase 1.2: como trazer o seletor de gravura do ScanTailor Advanced com o código original

**Data:** 28/09/2026 · **Quem:** agente pesquisador · **Pedido:** gerente, item 1.2 do Plano Definitivo. **Decisão que vale (Samuel, 24/09):** o código original, compilado e ligado ao programa, não traduzido para Python.

Nada foi compilado nem instalado; nenhum código do programa foi mexido. O código-fonte do ScanTailor foi baixado para a pasta temporária da sessão e lido lá.

---

## 1. A resposta em cinco frases

1. O fork vivo é o **`ScanTailor-Advanced/scantailor-advanced`** (última versão v1.2.1 em 24/05/2026, GPL-3.0); o do `4lex4` parou em 2023. O detector de gravura é o **mesmo** nos dois e na versão de 16/08/2019 que o Samuel testou em 24/09 (conferi o texto da função; só mudou o estilo dos nomes).
2. O detector fica em `src/core/filters/output/OutputGenerator.cpp` (funções `detectPictures` e `estimateBinarizationMask`). Ele usa só a biblioteca de imagem do próprio ScanTailor (`imageproc`, com `foundation` e `math`), que depende de **Qt Core/Gui** e de partes do **Boost que são só cabeçalho**. Não precisa de libtiff, libpng nem libjpeg: esses são do programa completo.
3. **O ScanTailor Advanced não tem linha de comando** (nenhum dos três forks): o caminho (a) só existe com **outro fork**, o ScanTailor Universal, cujo `scantailor-universal-cli` roda o modo Misto e grava a máscara de gravura. Serve como plano B e como régua, mas processa a página inteira, mexe na geometria e não é o Advanced.
4. **Recomendação: caminho (b).** Compilar só o detector como uma **DLL pequena com função em C, chamada por `ctypes`** (sem pybind11, para não ficar preso ao Python 3.14), com as bibliotecas do ScanTailor sem mudança e as funções do detector copiadas como estão, usando o Qt que o PySide6 já traz no programa.
5. A conferência é objetiva: o ScanTailor de 24/09 deixou **7 máscaras de gravura prontas** em `gabarito/scantailor-24-09/out/cache/automask/`; a DLL tem de dar a mesma máscara nessas páginas antes de entrar no programa.

## 2. Tabela

| O que é | Licença | Roda aqui? | Roda no notebook do Kaique? |
|---|---|---|---|
| ScanTailor Advanced (fork `ScanTailor-Advanced`, v1.2.1) | GPL-3.0 | Sim; o PC do Samuel já tem a versão 2019.8.16 (Qt 5, MinGW, 29 MB, só a janela) | Sim (só processador), mas **sem linha de comando** não serve para ligar ao programa |
| (a) ScanTailor Universal 0.2.14 com `scantailor-universal-cli` | GPL-3.0 | Sim, há instalador de 64 bits pronto (não testado) | Sim (só processador); mais uns ~30 MB no instalador (dedução) |
| (b) DLL só com o detector (código do Advanced) | GPL-3.0 (o programa passa a ser GPL ao distribuir, aceito em 17/09); Qt LGPL-3; Boost BSL-1.0 | Compila aqui depois de instalar as ferramentas (seção 5); roda dentro do programa | Sim: é código C++ no processador. O notebook só recebe a DLL pronta, não compila |
| (c) programa auxiliar `.exe` com o mesmo código de (b) | igual a (b) | Sim | Sim |

---

## 3. O que foi lido na fonte

### 3.1 Qual repositório

| Repositório | Situação (API do GitHub, 28/09/2026) |
|---|---|
| `4lex4/scantailor-advanced` | GPL-3.0, último envio 13/09/2023. Foi daqui que saiu a versão **2019.8.16_EA** (16/08/2019), a mesma instalada no PC do Samuel (os DLLs em `C:\Program Files\ScanTailor Advanced` têm essa data). |
| **`ScanTailor-Advanced/scantailor-advanced`** | GPL-3.0, último envio **24/05/2026**, versões v1.2.1 e v1.2.0 (24/05/2026, só Linux), v1.1.1 (03/04/2026, zip para Windows de 14 MB). O README diz que é a continuação, porque o do 4lex4 não está mais ativo. **É o fork mais vivo.** |
| `vigri/scantailor-advanced` | GPL-3.0, envio 18/04/2026; ramo do porte para Qt 6. |
| `trufanov-nok/scantailor-universal` | GPL-3.0, envio 07/04/2026; última versão 0.2.14 (19/08/2023) com instaladores de Windows 32 e 64 bits. **Tem linha de comando.** |
| `scantailor/scantailor` (o original) | Arquivado desde 2020; também tinha `scantailor-cli`. |

### 3.2 Onde fica o detector de gravura (fork `ScanTailor-Advanced`, ramo `master`)

Arquivo `src/core/filters/output/OutputGenerator.cpp`:

- **`Processor::processWithoutDewarping`**, bloco "Mixed begin" (~linha 1386): no modo Misto chama `processPictureZones(bwMask, pictureZones, GrayImage(maybeNormalized))`. A imagem que entra é a página já girada e recortada pelo ScanTailor, passada para cinza, e **com a iluminação normalizada** (`transformToWorkingCs` → `normalizeIlluminationGray`, ~linhas 2583 e 1893).
- **`Processor::processPictureZones`** (~2540): se a forma não é "desligada", chama `estimateBinarizationMask`; na forma "Retangular" transforma a máscara em retângulos com `findRectAreas` (~813), usando a "sensibilidade" em %.
- **`Processor::estimateBinarizationMask`** (~1928): reduz a página para **300 DPI**, chama `detectPictures`, volta ao tamanho original e corta no nível **48** → máscara de 1 bit (branco = figura).
- **`Processor::detectPictures`** (~2108), o coração. Em palavras minhas:
  1. estica os níveis de cinza (corta 1% no preto e 1% no branco), para texto grande não parecer figura;
  2. calcula o **gradiente morfológico** 3×3 (dilatação menos erosão): alto em borda de letra, baixo em papel liso e em área de tom contínuo;
  3. faz uma erosão **35×35** desse gradiente como semente e **reconstrói** a partir dela (preenchimento por semente, conectividade 8): sobra o que é "grande e com tom";
  4. inverte e **preenche os buracos** a partir de uma moldura;
  5. com a opção "maior sensibilidade de busca" ligada, estica de novo os níveis (5% no preto).
- **Valores padrão** (`PictureShapeOptions.cpp`, linha 10): forma **livre**, sensibilidade **100**, maior sensibilidade **desligada**. No modo Misto a normalização de iluminação vem das opções de preto e branco, que começam **ligadas** (`BlackWhiteOptions.cpp`, linha 18); o filtro de Wiener começa com coeficiente **0** (desligado, `ColorCommonOptions.cpp`).
- `estimateBackground` (a estimativa do fundo usada na normalização) está em `src/core/EstimateBackground.cpp` (289 linhas; usa `imageproc` e Boost.Lambda).

**Mesmo código em 2019, 2023 e 2026 (conferido):** `detectPictures`, `estimateBinarizationMask` e `findRectAreas` são idênticas, caractere por caractere, entre o `4lex4` (master) e o fork atual. Entre a versão 2019.8.16_EA (a do teste de 24/09) e a atual, `detectPictures` só mudou o estilo dos nomes (`input_300dpi` → `input300dpi`); tirando comentários, espaços e o estilo dos nomes, o texto é o mesmo. O `detectPictures` do ScanTailor Universal tem os mesmos passos, sem a opção "maior sensibilidade".

### 3.3 De que ele depende

- `src/imageproc/CMakeLists.txt`: biblioteca **estática** `imageproc` (~50 arquivos, 1 MB de fonte) que liga só em `foundation` e `math`.
- `src/foundation/CMakeLists.txt`: liga em **Qt Core, Qt Xml e Qt Gui**. `math` liga em `foundation`.
- A imagem cinza do ScanTailor (`GrayImage`) é uma casca em volta de `QImage` de 8 bits: por isso o **Qt Gui** é obrigatório.
- Boost em `imageproc`/`foundation`: só cabeçalhos (`foreach`, `scoped_array`, `lambda`, `function`, `intrusive/list`, `cstdint`). A biblioteca compilada do Boost (`unit_test_framework`) só é pedida para os testes.
- O programa completo (`CMakeLists.txt` raiz) pede também Qt Widgets, Network, OpenGL, Svg, LinguistTools, **libjpeg, libpng, zlib, libtiff** e Boost ≥ 1.60, C++17, CMake ≥ 3.9. Nada disso é preciso para o detector sozinho.

### 3.4 Linha de comando

- **ScanTailor Advanced:** a árvore dos três forks não tem `main-cli.cpp` nem `ConsoleBatch.cpp`. O executável é só a janela. O PC do Samuel tem só `scantailor.exe`.
- **ScanTailor Universal** (`src/app_cli/`, alvo `scantailor-universal-cli`): opções `--color-mode=mixed`, `--picture-shape=free|rectangular`, `--dpi`, `--output-dpi`, `--layout=1`, `--rotate`, `--deskew`, `--content-box`, `--disable-content-detection`, `--margins`, `--alignment`, `--normalize-illumination`, `--start-filter`/`--end-filter`, `--tiff-compression`. O script do instalador de Windows apaga `scantailor-universal-cli.exe` ao desinstalar (sinal de que o instalador o põe lá; não baixei para conferir).
- **A máscara de gravura sai em arquivo** mesmo em lote: `filters/output/Task.cpp` do Universal diz, num comentário, que o modo lote grava a "automask" porque a janela vai precisar dela depois; o arquivo vai para `<saída>/cache/automask/<página>.tif`. O teste de 24/09 com o Advanced deixou exatamente isso: 7 arquivos de 1 bit (escola 7, horas 11, 13 e 47, palatino 5 e 9, rhetorica 18), do tamanho da saída (7925×11933 px, saída a 600 DPI). Medido: a máscara do Palatino 5 é o oval do retrato (5,1% da folha); a do Palatino 9 está **vazia** (a capitular não foi achada, como o teste relatou); a da Horas 11 cobre 39,6%.

### 3.5 Compilar no Windows (README do `ScanTailor-Advanced/scantailor-libs-build`, seção Qt 6)

- Qt 6 **já compilado** (instalador oficial), com MSVC ou MinGW; no MSVC, abrir o prompt com `vcvars64.bat` do Visual Studio 2022; Ninja (vem com o Qt).
- Boost compilado com `b2 toolset=msvc`; zlib, libpng, libtiff e libjpeg-turbo compilados com CMake + Ninja.
- As versões oficiais recentes de Windows usam MSVC (o README pede o Visual C++ Redistributable).
- Para Qt 5 o caminho do README é compilar o próprio Qt a partir do fonte (horas de compilação).

---

## 4. Os caminhos

### (a) O ScanTailor inteiro pela linha de comando, chamado pelo programa

Só é possível com o **ScanTailor Universal** (o Advanced não tem linha de comando). O programa gravaria a página num PNG, chamaria `scantailor-universal-cli --color-mode=mixed ...` e leria `cache/automask/<página>.tif`.

- **Prós:** nada a compilar (instalador de 64 bits pronto); roda o caminho inteiro do ScanTailor, com a normalização e tudo; programa separado, então a licença é trivial.
- **Contras:**
  - não é o Advanced (o detector tem os mesmos passos, mas o preparo da imagem pode ser diferente: no Universal a normalização de iluminação começa **desligada** na linha de comando, no Advanced começa ligada no Misto);
  - o ScanTailor gira, recorta, põe margem e muda o DPI da página. Para a máscara cair no lugar certo seria preciso travar tudo (`--layout=1 --rotate=0 --content-box=<página toda> --margins=0 --dpi=X --output-dpi=X`) ou fazer a conta de volta (dedução: dá, mas é onde mora o erro);
  - gera a saída inteira (TIFF grande) só para aproveitar a máscara, e abre um processo por página. Dedução: vários segundos por página, contra a regra 6 (nenhum item pode deixar o programa mais lento);
  - última versão de 2023.
- **Instalar:** só o instalador do Universal (~30 MB instalado, dedução pelo tamanho do Advanced do Samuel). **Notebook:** roda. **Risco:** médio (geometria e tempo).

### (b) Só o detector como biblioteca, ligada ao Python — **recomendado**

Uma DLL (`st_gravura.dll`, por exemplo) com:
- as bibliotecas `imageproc`, `foundation` e `math` do ScanTailor **sem nenhuma mudança** (compiladas como estão no repositório);
- um arquivo C++ curto com `detectPictures`, `estimateBinarizationMask`, `findRectAreas`, `normalizeIlluminationGray` e `estimateBackground` **copiadas como estão**. Elas são métodos de uma classe interna (`OutputGenerator::Processor`) e usam dois ajudantes da janela (o aviso de cancelamento `m_status` e as imagens de depuração `m_dbg`): só essa "cola" muda, para nada;
- uma função em C, por exemplo `st_detectar_gravuras(pixels, largura, altura, passo, dpi, normalizar, forma, sensibilidade, mais_sensivel, máscara_saída)`, chamada do Python com **`ctypes`** sobre o array do NumPy (sem cópia para disco).

Por que `ctypes` e não pybind11: um módulo pybind11 é compilado para uma versão exata do Python (cp314) e tem de ser refeito a cada troca; a DLL com função em C não depende da versão do Python.

- **O Qt:** o PySide6 6.11.1 do `.venv` já traz `Qt6Core.dll` (10 MB), `Qt6Gui.dll` (9,6 MB) e `Qt6Xml.dll`, carregadas no processo quando o programa abre. Compilando a DLL contra **o mesmo Qt 6.11** (MSVC 2022, como o PySide6), o Windows reaproveita as que já estão carregadas e a DLL nova fica com poucos MB (**dedução, a validar primeiro**). O PySide6 não traz os arquivos `.lib` nem os cabeçalhos do Qt, então para compilar é preciso o Qt de desenvolvimento.
- **Instalar, uma vez, só no PC do Samuel:** Visual Studio 2022 Build Tools com "Desenvolvimento para desktop com C++" (alguns GB; pede administrador), CMake e Ninja, Qt 6.11 para `msvc2022_64` **só a base** (instalador oficial com conta Qt gratuita, ou `aqtinstall` num ambiente Python separado, sem conta), e os **cabeçalhos** do Boost (basta descompactar). Nada vai para o `.venv`. O vcpkg também daria Qt e Boost, mas compila o Qt a partir do fonte (horas; dedução), então o Qt já compilado é o caminho curto; o README do ScanTailor não usa vcpkg.
- **Prós:** é o código original; roda dentro do programa, sem disco e sem processo novo (o mais rápido); usa a página já cortada e endireitada pelo nosso programa, então não há geometria para desfazer; as opções do Advanced (forma, sensibilidade, maior sensibilidade) ficam disponíveis; botão de ligar e desligar simples (regra 8).
- **Contras:** exige a caixa de ferramentas de compilação no PC do Samuel; a "cola" precisa de cuidado; se o reaproveitamento do Qt do PySide6 der problema, cai no plano (c).
- **Notebook:** roda (processador; nenhuma placa de vídeo). **Tamanho:** DLL de 1 a 3 MB (dedução), mais nada se o Qt do PySide6 servir. **Risco:** médio-baixo, porque a conferência é objetiva (seção 5).

### (c) Outros

- **(c1) Programa auxiliar `st_gravura.exe`** com o mesmo código de (b), num processo separado, com as próprias DLLs do Qt na pasta dele: elimina qualquer choque com o Qt do PySide6. Custo: abrir um processo por página (dedução: fração de segundo), ou deixá-lo aberto recebendo pedidos. **É o plano B de (b).**
- **(c2) Pôr linha de comando no Advanced** trazendo o `ConsoleBatch` do Universal: trabalho grande, sem ganho sobre (b).
- **(c3) Traduzir para Python:** fora, pela decisão de 24/09. As duas recriações falharam, e o cabeçalho de `core/detectar_regioes.py` registra que "o detector morfológico do ScanTailor portado para Python" falhou no acervo. Por isso a conferência contra as máscaras do ScanTailor de verdade (seção 5) é o que separa "original" de "recriação".

---

## 5. Recomendação e como conferir

**Caminho (b)**, a partir do fork `ScanTailor-Advanced/scantailor-advanced`, **fixado na versão v1.2.1** (anotar o commit no programa), com (c1) como plano B e (a) só se a compilação se mostrar impossível.

Ordem sugerida para o implementador:
1. Compilar primeiro **o ScanTailor Advanced inteiro** com o mesmo kit (MSVC + Qt 6.11). Se ele compila e abre, o kit está certo. Os testes do próprio projeto (`imageproc_tests`) servem de prova extra.
2. Montar a DLL de (b) e um teste que passe as páginas do gabarito.
3. **Régua:** comparar com as 7 máscaras de `gabarito/scantailor-24-09/out/cache/automask/`. Elas estão na geometria de saída do ScanTailor (girada, recortada, com margem, a 600 DPI); o `conferencia.py` já sabe alinhar imagens de outro enquadramento. Critério sugerido: sobreposição (interseção sobre união) de pelo menos 0,95 em cada página e nenhuma zona de figura a mais ou a menos vista a olho. Se precisar de mais referências, o Samuel gera no próprio Advanced 2019 do PC dele (modo Misto, padrão), como fez em 24/09.
4. Medir o tempo por página (dedução: menos de 1 s a 300 DPI; tem de ser medido pela régua de velocidade da Fase 0).
5. Ligar ao programa com o botão de ligar e desligar e com as opções do Advanced (forma livre/retangular, sensibilidade), começando pelos padrões do teste de 24/09.

**O que o 1.2 sozinho não resolve** (o teste de 24/09 já mostrou, e as máscaras confirmam): a capitular do Palatino 9 não é achada (máscara vazia); a iluminação inteira da Horas 11 e a moldura dourada da Horas 13 saem mal; o papel dentro do oval do Palatino 5 fica dentro da zona de figura (amarelado). Isso é trabalho do 1.4 e do 1.5, e a conferência do 1.2 deve avisar.

---

## 6. O que ficou em aberto

- **Reaproveitar o Qt do PySide6** é dedução (o Qt promete compatibilidade dentro do Qt 6, e o Windows reaproveita DLL já carregada com o mesmo nome). Tem de ser o primeiro teste; se falhar, (c1).
- **Tempo por página** do detector não foi medido (nada foi compilado).
- **Se o instalador do Universal traz mesmo o `scantailor-universal-cli.exe`**: deduzido pelo script do desinstalador, não baixado.
- **Tamanho das ferramentas de compilação** (Build Tools, Qt base) é estimativa; o Visual Studio pede administrador.
- A versão v1.1.1 (zip de Windows, 03/04/2026) poderia servir de segunda referência de comparação no PC do Samuel; não baixei.
- O detector do ScanTailor trabalha em cinza. A página colorida entra convertida para cinza (a mesma conversão do ScanTailor, `GrayImage`), e isso pode explicar parte da falha na iluminura colorida; não investiguei.

## 7. Links consultados (28/09/2026)

- https://github.com/ScanTailor-Advanced/scantailor-advanced (README, releases, `CMakeLists.txt`, `src/imageproc/CMakeLists.txt`, `src/foundation/CMakeLists.txt`, `src/core/filters/output/OutputGenerator.cpp`, `PictureShapeOptions.cpp`, `BlackWhiteOptions.cpp`, `ColorCommonOptions.cpp`, `RenderParams.cpp`, `src/core/EstimateBackground.cpp`, `.github/workflows/`)
- https://github.com/ScanTailor-Advanced/scantailor-libs-build (instruções de compilação para Windows)
- https://github.com/4lex4/scantailor-advanced (master e a tag `2019.8.16_EA`, releases)
- https://github.com/vigri/scantailor-advanced
- https://github.com/trufanov-nok/scantailor-universal (`src/core/CommandLine.cpp`, `src/app_cli/`, `src/core/filters/output/Task.cpp`, `src/core/filters/output/OutputGenerator.cpp`, `src/packaging/windows/scantailor.nsi.in`, releases)
- https://github.com/scantailor/scantailor (original, arquivado; `main-cli.cpp`, `ConsoleBatch.cpp`)
- https://github.com/scantailor/scantailor/wiki/A.-Output-Tabs:-Picture-Zones
- Locais: `C:\Program Files\ScanTailor Advanced\` (lista de arquivos), `gabarito/scantailor-24-09/out/cache/automask/` (as 7 máscaras), `.venv\Lib\site-packages\PySide6\` (DLLs do Qt), `docs/plano/TESTE-SCANTAILOR-MISTO.md`, `core/detectar_regioes.py` (só o cabeçalho).
