# terceiros/scantailor-advanced: o seletor de gravura do ScanTailor Advanced

Trazido em **28/09/2026** para o item 1.2 da Fase 1 ("trazer o seletor de
gravura do ScanTailor Advanced, com o código original"; decisão do Samuel de
24/09). Licença **GPL-3** (arquivo `LICENSE` desta pasta, cópia do original).
Incorporar código GPL foi liberado pelo Samuel em 17/09: se o programa for
distribuído, vai com o código-fonte aberto.

## De onde veio

| | |
|---|---|
| Repositório | https://github.com/ScanTailor-Advanced/scantailor-advanced (o fork vivo; o de 4lex4 parou em 2023) |
| Versão | **v1.2.1** (24/05/2026) |
| Commit | `5eaac1884cdcabb6514bd632114f688631bd8dbc` |
| Autores | Joseph Artsimovich, 4lex4 e colaboradores (ver o cabeçalho de cada arquivo) |
| Licença | GNU GPL versão 3 |

## O que tem aqui

| Pasta | O que é | Mudou? |
|---|---|---|
| `src/` | 150 arquivos do ScanTailor, nos mesmos caminhos do repositório: os 72 do item 1.2 (24 `.cpp`, 48 `.h`: `imageproc/`, `foundation/`, `math/`, `core/EstimateBackground.*`, `core/ImageTransformation.h`, `core/OrthogonalRotation.h`, `core/NullTaskStatus.h`, `core/filters/output/PictureShapeOptions.*`) e, desde 06/10/2026, os 6 do limpar pontinhos (`core/Despeckle.*`, `imageproc/ConnectivityMap.*`, `imageproc/InfluenceMap.*`) os 50 do dividir (item 2.1; lista em "O dividir", abaixo) os 4 do endireitar (item 2.2; ver "O endireitar") e, desde 12/10/2026, os 18 das caixas da página e do conteúdo (itens 2.13 e 2.5; ver "As caixas") | **Não.** Iguais aos da v1.2.1, só com o fim de linha do Windows na pasta do PC (ver "Como conferir que nada mudou") |
| `somas-v1.2.1.txt` | A soma SHA-256 de cada arquivo de `src/` como está no ScanTailor v1.2.1 (tirada do git do ScanTailor, fim de linha LF). O teste `tests/test_st_ferramentas.py` confere todos, a cada rodada | Nosso (a lista) |
| `referencia/ProjectPages.cpp` | O arquivo do ScanTailor de onde veio a única função copiada como "cola" no dividir (`adviseNumberOfLogicalPages`, linhas 205-214). **Não é compilado**: o teste `tests/test_dividir_scantailor.py` confere a soma dele e que o trecho em `ligacao-ferramentas/dividir.cpp` é igual | Não |
| `referencia/deskew/Task.cpp` | O arquivo do ScanTailor de onde veio a limpeza das sombras do endireitar (`cleanup` e `from150dpi`, linhas 222-271). **Não é compilado**: o teste `tests/test_endireitar_scantailor.py` confere a soma dele e que o trecho em `ligacao-ferramentas/endireitar.cpp` é igual | Não |
| `referencia/ImageSettings.cpp` | O arquivo do ScanTailor de onde vieram os dois construtores copiados como "cola" nas caixas (`ImageSettings::PageParams`, linhas 48-51). **Não é compilado**: o teste `tests/test_caixas_scantailor.py` confere a soma dele e que o trecho em `ligacao-ferramentas/caixas.cpp` é igual | Não |
| `referencia/select_content/Task.cpp` | O arquivo do ScanTailor que diz a ordem da etapa "Select Content" (o que `caixas.cpp` repete, passo a passo). **Não é compilado**; o teste confere a soma | Não |
| `referencia/OutputGenerator.cpp` | O arquivo do ScanTailor onde mora o detector. **Não é compilado**: serve para o teste conferir que as funções copiadas não mudaram | Não |
| `ligacao/st_gravura.cpp` | A "cola": copia as funções do detector de `OutputGenerator.cpp` **letra por letra** (entre as marcas `COPIADO SEM MUDANCA (linhas X-Y)`) e troca só o que ligava o detector à janela do ScanTailor | Só a ligação (ver abaixo) |
| `ligacao/st_gravura.h` | As funções em C que o Python chama por `ctypes` | Nosso |
| `ligacao/CMakeLists.txt` | Compila `src/` como biblioteca estática e `st_gravura.cpp` como DLL | Nosso |
| `ligacao-ferramentas/` | A DLL comum `st_ferramentas.dll` (Fase 2, item M9): `st_ferramentas.h` (as funções em C), `comum.h` (conversões e erros, para todas as ferramentas), `st_ferramentas.cpp` (versão e origem), `pontinhos.cpp` (limpar pontinhos, M4), `dividir.cpp` (dividir a folha, item 2.1), `endireitar.cpp` (endireitar a página, item 2.2), `caixas.cpp` (a caixa da página e a do conteúdo, itens 2.13 e 2.5) e `CMakeLists.txt` (compila TODO o `src/`) | Nosso (só a ligação) |

Foram trazidos só os arquivos que o detector usa: o fecho dos `#include` a
partir das funções copiadas (os `.cpp` de `ImageTransformation`,
`OrthogonalRotation` do `core/` e `AutoRemovingFile` ficaram de fora porque só
o cabeçalho é usado). Nada de libtiff, libpng, libjpeg nem da janela.

### As funções copiadas sem mudança (de `src/core/filters/output/OutputGenerator.cpp`)

| Linhas | O que é |
|---|---|
| 366-386 | `RaiseAboveBackground`, `CombineInverted` (contas de ponto a ponto) |
| 782-985 | `findRectAreas` e ajudantes (forma "retangular") |
| 1206-1212 | `to300dpi` |
| 1893-1926 | `normalizeIlluminationGray` (normaliza a iluminação) |
| 1928-1973 | `estimateBinarizationMask` (reduz a 300 DPI, detecta, volta ao tamanho, corta em 48) |
| 2108-2184 | `detectPictures` (o coração do detector) |
| 2583-2606 | `transformToWorkingCs` (leva a página para o sistema de trabalho) |

O teste `tests/test_gravura_scantailor.py::test_funcoes_copiadas_sem_mudanca`
confere, a cada rodada, que esses 7 blocos continuam idênticos ao original.

### O que a ligação troca (e só isso)

1. A classe `OutputGenerator::Processor` do ScanTailor depende do projeto, das
   configurações, das zonas desenhadas à mão e das imagens de depuração. Em
   `st_gravura.cpp` ela é trocada por uma classe **com o mesmo nome** que tem só
   os membros que as funções copiadas usam, para elas compilarem sem mudar uma
   letra. O aviso de cancelamento vira `NullTaskStatus` (do próprio ScanTailor)
   e as imagens de depuração ficam desligadas.
2. `process()`: as etapas de `processImpl()` + `processWithoutDewarping()` (modo
   Misto, sem desentortar) até a máscara, na mesma ordem. O filtro de Wiener
   fica de fora porque no padrão do ScanTailor o coeficiente é 0 (não faz nada).
   Um atalho pula a "cor dominante do fundo" quando nenhum ponto cai fora da
   página (não muda o resultado: conferido igual, ponto a ponto, nas 9 páginas
   do teste de 24/09).
3. `processPictureZones()`: sem as zonas da janela. Na forma retangular, os
   retângulos de `findRectAreas` são pintados direto na máscara (no ScanTailor
   eles viram zonas "pintar" e são pintados depois, com o mesmo
   `PolygonRasterizer`).
4. A página sempre é tratada como "preto no branco" (o ScanTailor tem uma
   detecção automática que às vezes decide o contrário; ver "Ressalvas").
5. A função em C `st_gravura_detectar()`, que recebe os pontos da página do
   Python e devolve a máscara (255 = gravura).

## Duas DLLs (desde 06/10/2026)

| DLL | O que tem | Compila com | Python |
|---|---|---|---|
| `core/nativo/st_gravura.dll` | O detector de gravura (item 1.2, aprovado) | `compilar_detector_gravura.py` (pasta `ligacao/`) | `core/gravura_scantailor.py` |
| `core/nativo/st_ferramentas.dll` | A DLL **comum** das outras ferramentas. Hoje: limpar pontinhos (`Despeckle`), dividir a folha (`PageLayoutEstimator`), endireitar (`SkewFinder`) e as caixas da página e do conteúdo (`PageFinder`, `ContentBoxFinder`) | `compilar_st_ferramentas.py` (pasta `ligacao-ferramentas/`) | `core/st_ferramentas.py` (abre a DLL) + um módulo por ferramenta (`core/pontinhos_scantailor.py`, `core/dividir_scantailor.py`, `core/endireitar_scantailor.py`, `core/caixas_scantailor.py`) |

**Por que a comum fica AO LADO da do 1.2, e não no lugar dela:** a do 1.2 foi
aprovada pelo Samuel, está ligada ao programa e foi conferida contra as
máscaras do próprio ScanTailor. Trocar de DLL é mexer no que funciona sem
ganho para ele. As duas usam o mesmo `src/` e o mesmo Qt do PySide6, e não
brigam (cada DLL tem a sua cópia do código; nada é compartilhado entre elas).
Conferido em 06/10/2026: com os 6 arquivos novos em `src/`, a `st_gravura`
recompilada numa pasta de rascunho dá as **mesmas 64 máscaras** (32 páginas do
gabarito, forma livre e retangular) que a DLL guardada no projeto; a DLL
guardada não foi tocada (o teste `test_a_dll_do_1_2_nao_mudou` confere a soma).

**Quando juntar:** quando alguém quiser uma DLL só, a cola do detector
(`ligacao/st_gravura.cpp`) vira mais um `.cpp` de `ligacao-ferramentas/`, e o
`core/gravura_scantailor.py` passa a abrir a comum - **só depois** de a comum
dar as mesmas 64 máscaras (o roteiro está em
`tests/test_gravura_scantailor.py` e na conferência do 1.2).

**Como acrescentar uma ferramenta à comum** (dividir `estimatePageLayout`,
endireitar `SkewFinder`, `PageFinder`, `ContentBoxFinder`, os binarizadores de
`Binarize.cpp`, a segmentação de cor `ColorSegmenter`): ver o topo de
`ligacao-ferramentas/st_ferramentas.h`. Em resumo: os arquivos do ScanTailor
entram em `src/` sem mudança, com a soma em `somas-v1.2.1.txt`; a cola vira um
`.cpp` novo em `ligacao-ferramentas/`; a função em C entra no `.h` e em
`ASSINATURAS` do `core/st_ferramentas.py` (o teste confere que batem), e a
versão sobe. Cuidado ao trazer os filtros de geometria: cada um tem
`Settings.h`, `Task.h` etc. com o mesmo nome (ver o `CMakeLists.txt`).

**O `ligacao/CMakeLists.txt` do 1.2 compila `src/core/*.cpp` e
`src/imageproc/*.cpp` inteiros.** Arquivo novo nessas pastas entra na
biblioteca do 1.2 também (não muda a DLL: o vinculador só puxa o que o
detector usa), mas, se um dia o arquivo novo precisar de uma pasta de
cabeçalhos que o 1.2 não tem, a recompilação da `st_gravura` quebra. Aí, ou
se lista os arquivos do 1.2 um a um, ou se faz a junção acima.

## O dividir (item 2.1, desde 06/10/2026)

Decisões do Samuel G2 (a) e G3 (b), 05/10/2026: dividir só quando o Kaique
pedir, livro a livro, "o do programa" ou "o do ScanTailor", trocando numa
folha; o "corte da sobra" do ScanTailor como opção desligada.

**Função em C:** `st_ferramentas_dividir` (`ligacao-ferramentas/dividir.cpp`),
a mesma chamada do `page_split::Task` do ScanTailor:
`PageLayoutEstimator::estimatePageLayout(modo, cinza, geometria, limiar)`.
A cola monta o que o Task recebe com as linhas do construtor de `FilterData`
(`toGrayscale`, `ImageTransformation(image.rect(), Dpm(image))`) e o limiar
Otsu do `fix_orientation::Task` (linha 87); `FilterData.cpp` e
`ImageSettings.cpp` **não** vieram (puxariam o projeto e as miniaturas do
ScanTailor). Uma função de `ProjectPages.cpp` (`adviseNumberOfLogicalPages`,
10 linhas) está copiada sem mudança na cola, entre marcas; o original está em
`referencia/ProjectPages.cpp`.

**Os 50 arquivos trazidos** (todos sem mudança, com a soma em
`somas-v1.2.1.txt`, conferida três vezes: a soma do `git show v1.2.1`, a do
arquivo aqui e o `git hash-object --path` contra o `rev-parse` do ScanTailor):
`core/filters/page_split/` (`PageLayoutEstimator.*`, `VertLineFinder.*`,
`PageLayout.*`, `LayoutType.h`); `core/` (`ContentSpanFinder.*`,
`ImageMetadata.*`, `ImageTransformation.cpp`, `OrthogonalRotation.cpp`,
`ProjectPages.h`, `PageId.h`, `PageInfo.h`, `PageView.h`, `ImageId.h`,
`BeforeOrAfter.h`); `imageproc/` (`ConnComp.h`, `ConnCompEraser.*`,
`ConnCompEraserExt.*`, `HoughLineDetector.*`, `MorphGradientDetect.*`,
`OrthogonalRotation.*`, `ReduceThreshold.*`, `Shear.*`, `SkewFinder.*`,
`SlicedHistogram.*`); `foundation/` (`XmlMarshaller.*`, `XmlUnmarshaller.*`,
`Utils.*`, `Hashes.h`, `NumericTraits.h`, `Span.h`, `VirtualFunction.h`);
`math/ToLineProjector.*`. É o fecho dos `#include` a partir dos três `.cpp`
do `page_split`, mais os `.cpp` que o vinculador pediu.

**Conferido em 06/10/2026, com os 50 arquivos novos em `src/`:**
- a `st_gravura` (item 1.2), recompilada numa pasta de rascunho (fora do
  projeto; a DLL guardada não foi tocada), dá as **mesmas 64 máscaras** (32
  páginas do gabarito, forma livre e retangular) que a DLL do projeto;
- o limpar pontinhos da DLL comum nova dá **o mesmo, ponto a ponto**, que a
  DLL comum anterior (versão 1) nas 32 páginas do gabarito, nas forças
  pouco, normal e muito (96 de 96 iguais);
- o dividir dá, no Siebmacher 9 e no Opus Majus 256, a mesma divisão do
  programa de teste do D3 (82% e 50%).

A versão da interface subiu para 2 (`ST_FERRAMENTAS_VERSAO_API`); a função
dos pontinhos não mudou.

## O endireitar (item 2.2, desde 06/10/2026)

Decisões do Samuel G4 (b) e G6 (a), 05/10/2026: o endireitar do ScanTailor de
fábrica, a conta do programa continua como escolha (por livro e por página), a
página vai para "Para revisar" quando as duas discordam mais de 0,3°, e o
endireitar passa a vir ANTES do corte (como no ScanTailor).

**Função em C:** `st_ferramentas_endireitar` (`ligacao-ferramentas/endireitar.cpp`),
o que o `deskew::Task` do ScanTailor faz numa página nova: o cinza e a
geometria do `FilterData`, o limiar Otsu e a detecção "claro no escuro"
(`BlackOnWhiteEstimator`, ligada de fábrica no ScanTailor) do
`Task::updateFilterData`, a **limpeza das sombras horizontais compridas**
(`Task::cleanup`, copiada sem mudança entre marcas, com uma classe `deskew::Task`
de mesmo nome só com as três funções `static`) e o `SkewFinder::findSkew`, que
só vale com confiança 2,0 ou mais. A correção "oblíqua" vem desligada de
fábrica no ScanTailor e não foi trazida. O original do `Task.cpp` está em
`referencia/deskew/Task.cpp` (não compilado).

**Os 4 arquivos trazidos** (sem mudança, soma em `somas-v1.2.1.txt`, tirada do
`git show v1.2.1:` do ScanTailor): `imageproc/UpscaleIntegerTimes.*` (a
limpeza usa) e `core/BlackOnWhiteEstimator.*` (a detecção "claro no escuro").
O `SkewFinder` já tinha vindo com o dividir.

**Conferido em 06/10/2026, com a DLL nova (versão 3 da interface):**
- o limpar pontinhos dá o mesmo, ponto a ponto, que a DLL anterior (versão 2)
  nas 32 páginas do gabarito, nas forças pouco, normal e muito (96 de 96);
- o dividir dá o mesmo que a versão 2 nas 32 páginas, nos modos automático,
  "uma página + sobra" e "duas páginas" (96 de 96);
- o endireitar dá, nas páginas do D3 em que o ScanTailor não cortou sobra
  (Palatino 5, Boécio 3, 7, 8, Opus Majus 3, 11, 165), o mesmo ângulo e a
  mesma confiança do programa de teste do D3;
- a `st_gravura` (item 1.2), recompilada numa pasta de rascunho com os 4
  arquivos novos em `src/`, ver a seção "Duas DLLs".

## O preto e branco da saída (item 2.8, desde 20/10/2026)

Decisão do Samuel P8 (b), 05/10/2026: "Trazer os dez do ScanTailor como opções
a mais"; regra de 13/10: igual ao ScanTailor, com os ajustes de fábrica dele,
desligado de fábrica.

| | |
|---|---|
| Cola | `ligacao-ferramentas/saida.cpp` (função em C `st_ferramentas_preto_e_branco`) |
| Python | `core/preto_e_branco_scantailor.py`; chamado por `core.filtros.filtro_preto_e_branco` quando a página escolhe um dos dez (`ConfigPagina.algoritmo_preto_branco` = `st_otsu` ... `st_edgediv`) |
| Arquivos novos em `src/` (sem mudança, somas em `somas-v1.2.1.txt`) | `imageproc/SavGolFilter.*`, `imageproc/SavGolKernel.*`, `core/filters/output/BlackWhiteOptions.*` (o `Binarize.cpp` com os dez jeitos já estava, desde o 1.2) |
| Funções copiadas de `referencia/OutputGenerator.cpp` (marcas `COPIADO SEM MUDANCA`, conferidas por `tests/test_preto_e_branco_scantailor.py`) | 366-386 (`RaiseAboveBackground`), 1004-1050 (`hitMissReplaceAllDirections`), 1178-1196 (`smoothToGrayscale`), 1893-1926 (`normalizeIlluminationGray`), 2186-2192 (`adjustThreshold`), 2220-2302 (`morphologicalSmoothInPlace`), 2304-2403 (`binarize`, os dez jeitos), 2583-2606 (`transformToWorkingCs`) |
| Ordem (a de `processWithoutDewarping`, modo preto e branco) | igualar a luz → [Wiener: coeficiente 0 de fábrica, fica de fora] → Savitzky-Golay → binarizar → suavização morfológica |
| Ajustes de fábrica (os de `BlackWhiteOptions.cpp`) | método Otsu, ajuste do limiar 0, janela 200, k Sauvola 0,34, k Wolf 0,3, limites do Wolf 1 e 254, as três etapas ligadas |

O que a ligação troca: a classe `OutputGenerator::Processor` vira uma classe
com o mesmo nome e só os membros usados (como no 1.2); `m_colorParams` vira
uma estrutura com só `blackWhiteOptions()`. A página chega já girada e cortada
pelo programa, então o sistema de trabalho é a própria imagem e a área de
conteúdo é a imagem inteira: `binarize(imagem, área)` do original vira
`binarize(imagem)`, que é exatamente o caminho do original quando a área cobre
a imagem toda (linhas 2412-2420). Os pontinhos (Despeckle) não entram aqui: no
programa eles são a escolha "Limpar a sujeira", que já existe.

## As cores da saída (item 2.11, desde 20/10/2026)

"Letras com a cor delas" (Color segmentation) e "Reduzir cores" (Posterize), decisão P10 (a) do Samuel
(05/10): opção desligada de fábrica. Função em C `st_ferramentas_cores` em `ligacao-ferramentas/saida.cpp`;
Python em `core/cores_scantailor.py`, chamado no fim de `core.pipeline._filtrar`. Arquivos novos em `src/`
(sem mudança, com soma): `imageproc/ColorSegmenter.*`, `imageproc/Posterizer.*`,
`imageproc/ImageCombination.*`, `core/filters/output/ColorCommonOptions.*`, `core/AutoManualMode.*`. Funções
copiadas a mais de `OutputGenerator.cpp`: 2502-2538 (`segmentImage`, `posterizeImage`). Ajustes de fábrica:
"Reduce noise" 7, ajustes de vermelho/verde/azul 0, nível 4, sem normalizar, "forçar preto e branco" ligado.
## As caixas da página e do conteúdo (itens 2.13 e 2.5, desde 12/10/2026)

Decisões do Samuel G7 (a) e G8 (a), 05/10/2026: "achar a página dentro da
borda preta" e "seguir a moldura / o papel" entram como opção **desligada de
fábrica**. Em 12/10/2026 só a base foi trazida: a função existe e é testada,
mas **nada no programa a chama** (como liga depende das seis perguntas de
12/10, ainda sem resposta; o teste `test_ninguem_no_programa_chama_as_caixas_ainda`
segura isso).

**Função em C:** `st_ferramentas_caixas` (`ligacao-ferramentas/caixas.cpp`), o
que o `select_content::Task` do ScanTailor faz numa página sem caixa nenhuma
(o original está em `referencia/select_content/Task.cpp`, não compilado):
o `FilterData` da página, o "claro no escuro" e o limiar do
`deskew::Task::updateFilterData`, `PageFinder::findPageBox` (a caixa da
página), `ContentBoxFinder::findContentBox` dentro dela (a caixa do conteúdo),
o corte `contentRect &= pageRect` e o tamanho em mm do `PhysSizeCalc`. Dois
construtores de `ImageSettings::PageParams` (4 linhas) estão copiados sem
mudança na cola, entre marcas; `ImageSettings.cpp` inteiro puxaria o projeto e
as miniaturas do ScanTailor. Python: `core/caixas_scantailor.py`.

**Os 18 arquivos trazidos** (sem mudança, soma em `somas-v1.2.1.txt` tirada do
`git show v1.2.1:` do ScanTailor, e conferidos também pelo `git hash-object
--path` contra o `rev-parse` do ScanTailor): `core/filters/select_content/`
(`PageFinder.*`, `ContentBoxFinder.*`, `PhysSizeCalc.*`); `core/`
(`FilterData.*`, `ImageSettings.h`, `Margins.h`, `Units.h`,
`UnitsConverter.*`); `imageproc/` (`MaxWhitespaceFinder.*`, `SEDM.*`);
`foundation/FlagOps.h`. É o fecho dos `#include` a partir dos três `.cpp` do
`select_content` e do `FilterData.cpp`. **Da pasta `select_content` só vieram
esses três pares** (os filtros têm `Settings.h`, `Task.h`, `Utils.h` de mesmo
nome; o teste confere que não há outros). O `CMakeLists.txt` não mudou: a
cola inclui `filters/select_content/...` a partir de `core/`.

**O que não é óbvio no código original** (nada foi consertado; está escrito no
topo de `caixas.cpp`): o `ContentBoxFinder` monta o retângulo da página com
(esquerda, cima, direita, baixo) onde o Qt espera largura e altura, e a
procura do conteúdo pode passar da página à direita e embaixo (no ljs47 o
conteúdo sai 16 a 108 pontos dentro do preto de baixo; o corte pela página
devolve); o `PageFinder` calcula cinco preto e branco e usa um.

**Conferido em 12/10/2026, com a DLL nova (versão 4 da interface):**
- nas 37 páginas que o pesquisador mediu com o programa de teste dele (o mesmo
  código, ligado na `st_tudo.lib` de 01/10; 26 do gabarito, 6 folhas com borda
  preta da rodada 4 e 5 do acervo), mais a Horas 13 e o Graduale 222 a 150 DPI,
  a DLL dá **as mesmas caixas** (página, conteúdo dentro dela, conteúdo na
  folha inteira e as duas com "ajustar os cantos"): a maior diferença é 0,04
  ponto, o arredondamento da casa decimal que ele imprimiu;
- o limpar pontinhos, o dividir e o endireitar dão **o mesmo que a DLL
  anterior** (versão 3, a do `fase-1` em `4b19a9b`) nas 32 páginas do
  gabarito: pontinhos nas três forças, ponto a ponto (96 de 96), dividir nos
  três modos (96 de 96) e endireitar (32 de 32). Script:
  `relatorios/caixa-conteudo-impl/scripts/comparar_dll_anterior.py`;
- a `st_gravura.dll` (item 1.2) **não foi tocada** nem recompilada (o teste
  `test_a_dll_do_1_2_nao_mudou` confere a soma). Ressalva: a recompilação dela
  com os 18 arquivos novos em `src/` (ver "Duas DLLs") **não foi refeita** em
  12/10; os novos de `core/` e `imageproc/` entram na biblioteca do 1.2.

## Como conferir que nada mudou

**Não use `cmp` direto na pasta do PC.** O git deste PC está com
`core.autocrlf=true` (na configuração do próprio Git for Windows): ao tirar os
arquivos do git, ele troca o fim de linha para o do Windows (CR+LF). O arquivo
no GitHub tem só LF. Então um `cmp` contra o arquivo baixado do GitHub dá
"diferente" nos 74 arquivos, mesmo sem nenhuma mudança. (Em 28/09 o `cmp` deu
"igual" só porque a cópia de comparação também tinha sido tirada do git neste
PC, com o mesmo CR+LF - não provava nada contra o original.)

Dois jeitos certos (os dois feitos em 28/09/2026: **74 de 74 iguais**, os 72
de `src/`, o `LICENSE` e a `referencia/OutputGenerator.cpp`):

1. **Pela soma do git** (o que vai para o repositório já sem o CR). Com uma
   cópia do repositório do ScanTailor na tag v1.2.1 em `<clone>`, no Git Bash,
   dentro desta pasta:

       for f in $(find src -type f); do
         [ "$(git hash-object --path="$f" "$f")" = "$(git -C <clone> rev-parse "v1.2.1:$f")" ] || echo "MUDOU $f"
       done

   (`--path` faz o git aplicar a mesma troca de fim de linha que aplica ao
   guardar; o `LICENSE` compara com `v1.2.1:LICENSE` e a
   `referencia/OutputGenerator.cpp` com `v1.2.1:src/core/filters/output/OutputGenerator.cpp`.)
2. **Tirando o CR** e comparando com o arquivo cru do GitHub:

       curl -sL https://raw.githubusercontent.com/ScanTailor-Advanced/scantailor-advanced/5eaac1884cdcabb6514bd632114f688631bd8dbc/src/imageproc/Scale.cpp \
         | cmp - <(tr -d '\r' < src/imageproc/Scale.cpp) && echo igual

O teste `tests/test_gravura_scantailor.py` guarda a soma SHA-256 da
`referencia/OutputGenerator.cpp` do GitHub (sem o CR) e confere a cada rodada.

## Como recompilar

A DLL comum: `.venv\Scripts\python.exe compilar_st_ferramentas.py` (mesmas
ferramentas; sai em `core/nativo/st_ferramentas.dll`, ~290 KB; leva uns 3 minutos). A do 1.2:


    .venv\Scripts\python.exe compilar_detector_gravura.py            # compila
    .venv\Scripts\python.exe compilar_detector_gravura.py --baixar   # baixa Qt/Boost que faltarem e compila

Precisa, só no PC de quem compila: Visual Studio 2022 Build Tools com C++,
CMake, o Qt 6.11.1 de desenvolvimento (só a parte `qtbase`) e os cabeçalhos
do Boost 1.78.0. O script baixa os dois últimos do servidor oficial, confere
as somas, e guarda tudo em `D:\programas\EditorImpressao-arquivos\ferramentas\`
(fora do git). A DLL sai em `core/nativo/st_gravura.dll`, com
`core/nativo/st_gravura.txt` ao lado (origem e soma SHA-256).

A DLL **não leva o Qt dentro**: usa o `Qt6Core.dll` e o `Qt6Gui.dll` que o
PySide6 já traz. Por isso o Qt de compilação tem de ser da mesma versão do
PySide6 (o script recusa se não for).

## Ressalvas

- Na Horas 11 do teste de 24/09, o ScanTailor decidiu sozinho que a página era
  "claro no escuro" e analisou a página **invertida** (é o que deixou grandes
  áreas da iluminura pretas naquele teste). A DLL sempre trata a página como
  preto no branco. Ver o relatório do item 1.2.
