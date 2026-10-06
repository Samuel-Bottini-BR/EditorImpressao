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
| `src/` | 78 arquivos do ScanTailor, nos mesmos caminhos do repositório: os 72 do item 1.2 (24 `.cpp`, 48 `.h`: `imageproc/`, `foundation/`, `math/`, `core/EstimateBackground.*`, `core/ImageTransformation.h`, `core/OrthogonalRotation.h`, `core/NullTaskStatus.h`, `core/filters/output/PictureShapeOptions.*`) e, desde 06/10/2026, os 6 do limpar pontinhos (`core/Despeckle.*`, `imageproc/ConnectivityMap.*`, `imageproc/InfluenceMap.*`) | **Não.** Iguais aos da v1.2.1, só com o fim de linha do Windows na pasta do PC (ver "Como conferir que nada mudou") |
| `somas-v1.2.1.txt` | A soma SHA-256 de cada arquivo de `src/` como está no ScanTailor v1.2.1 (tirada do git do ScanTailor, fim de linha LF). O teste `tests/test_st_ferramentas.py` confere todos, a cada rodada | Nosso (a lista) |
| `referencia/OutputGenerator.cpp` | O arquivo do ScanTailor onde mora o detector. **Não é compilado**: serve para o teste conferir que as funções copiadas não mudaram | Não |
| `ligacao/st_gravura.cpp` | A "cola": copia as funções do detector de `OutputGenerator.cpp` **letra por letra** (entre as marcas `COPIADO SEM MUDANCA (linhas X-Y)`) e troca só o que ligava o detector à janela do ScanTailor | Só a ligação (ver abaixo) |
| `ligacao/st_gravura.h` | As funções em C que o Python chama por `ctypes` | Nosso |
| `ligacao/CMakeLists.txt` | Compila `src/` como biblioteca estática e `st_gravura.cpp` como DLL | Nosso |
| `ligacao-ferramentas/` | A DLL comum `st_ferramentas.dll` (Fase 2, item M9): `st_ferramentas.h` (as funções em C), `comum.h` (conversões e erros, para todas as ferramentas), `st_ferramentas.cpp` (versão e origem), `pontinhos.cpp` (limpar pontinhos, M4) e `CMakeLists.txt` (compila TODO o `src/`) | Nosso (só a ligação) |

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
| `core/nativo/st_ferramentas.dll` | A DLL **comum** das outras ferramentas. Hoje: limpar pontinhos (`Despeckle`) | `compilar_st_ferramentas.py` (pasta `ligacao-ferramentas/`) | `core/st_ferramentas.py` (abre a DLL) + um módulo por ferramenta (`core/pontinhos_scantailor.py`) |

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
ferramentas; sai em `core/nativo/st_ferramentas.dll`, ~43 KB). A do 1.2:


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
