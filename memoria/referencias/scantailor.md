# Referência: ScanTailor Advanced (o código original dentro do programa)

Conferido em 20/10/2026. **O plano manda**: a regra da Fase 2 e o que já foi decidido estão no
[PLANO-DEFINITIVO](../../docs/plano/PLANO-DEFINITIVO.md). Esta ficha junta o que já se sabe para ninguém refazer.

## Em uma frase

O programa usa o **código original** do ScanTailor Advanced **v1.2.1**, compilado em duas DLLs (`st_gravura.dll`, o
detector de gravura do 1.2; `st_ferramentas.dll`, as outras ferramentas), chamadas pelo Python por `ctypes`. Não é
tradução para Python: as duas tentativas de recriar o detector em Python falharam.

## O que é e de onde veio

| | |
|---|---|
| Programa | ScanTailor Advanced, fork vivo `ScanTailor-Advanced/scantailor-advanced` (o do 4lex4 parou em 2023) |
| Versão | **v1.2.1** (24/05/2026), commit `5eaac1884cdcabb6514bd632114f688631bd8dbc` |
| Licença | **GPL-3** (cópia em `terceiros/scantailor-advanced/LICENSE`) |
| Onde está no projeto | [`terceiros/scantailor-advanced/`](../../terceiros/scantailor-advanced/LEIA-ME.md): `src/` (arquivos sem mudança), `ligacao/` (cola do 1.2), `ligacao-ferramentas/` (cola da DLL comum), `referencia/` (originais só para conferir) |
| Código-fonte inteiro baixado | `D:\programas\EditorImpressao-arquivos\ferramentas\scantailor-advanced-v1.2.1\` (fora do git; também há `scantailor-advanced-2019.8.16`, a versão do teste de 24/09) |

**Licença.** Decisão do Samuel de 17/09/2026 ([CLAUDE.md §3](../../CLAUDE.md)): "Código GPL pode ser incorporado
direto agora (não só estudado de longe)", porque "se um dia o programa for liberado, é de graça com doação voluntária".
Se o programa for distribuído, vai com o código-fonte. O pesquisador conferiu em 01/10/2026 que todo o código da v1.2.1
é GPL-3 (Qt LGPL-3, Boost BSL-1.0, um trecho de domínio público) ([mapa, seção 3](../../docs/pesquisa/fase2-mapa-scantailor.md)).

## A história, em ordem

1. **31/07/2026 e 16/09/2026: o seletor de gravura foi recriado em Python duas vezes, e falhou.**
   ([ESTADO-ATUAL §3](../../docs/plano/ESTADO-ATUAL.md): "O seletor de gravura foi **recriado** duas vezes a partir da
   descrição do ScanTailor (31/07 e 16/09) e falhou.") A de 31/07 é o "detector morfológico do ScanTailor portado para
   Python" (`core/detectar_regioes.py`, commit `e8aeec9`).
2. **15-16/09/2026: "trazer técnicas do ScanTailor" foi implementado inteiro e REVERTIDO**
   ([histórico, PARTE -4 §2](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)). Nove frentes
   (pontinhos por proximidade, Wolf, polaridade invertida, gravura por reconstrução morfológica, tamanho de página e
   margem), 312 testes, nada commitado. Palavras do Samuel: "não vou comitar, quero voltar a versão que estava antes."
   Guardado num `git stash` ("Fase 3 ScanTailor - revertido a pedido do Samuel, 16/09/2026"). Achados que valem até
   hoje: a reconstrução morfológica **já falhou duas vezes** neste acervo (o vão entre linhas de um livro é menor que
   o vão entre traços de gravura de outro; `avaliar_selecao.py` caiu de 24/26 para 20/26) e "Não vale tentar de novo
   sem uma ideia genuinamente diferente"; o ScanTailor não acha a lombada sozinho nem força tamanho A4 real.
3. **24/09/2026: teste com o ScanTailor de verdade, modo Misto.**
   [TESTE-SCANTAILOR-MISTO.md](../../docs/plano/TESTE-SCANTAILOR-MISTO.md). Arquivos em
   `D:\programas\Scan Tailor\Testes de ajuste\` (`teste-gravuras-varios\` e `teste-gravuras-palatino\`). Resultado:
   Escola 7 e Palatino 5 "Ótimo"; Palatino 9 "Bom"; Horas 47 "Muito bom"; Horas 13 "Ruim na cor"; Horas 11 "Ruim".
   Conclusão do documento: "O detector **verdadeiro** do ScanTailor funciona muito melhor que as duas recriações
   anteriores"; falha em página inteira iluminada e em texto colorido. **Decisão do Samuel (24/09): caminho (a)**,
   usar o código original compilado, "e não uma tradução para Python". As máscaras desse teste ficaram em
   `gabarito/scantailor-24-09/` (fora do git) e são a régua da DLL.
   - **Não confundir:** a pasta `D:\programas\Scan Tailor` tem também o **ExtratorPDF**, que é **outro programa**
     ([ESTADO-ATUAL §5](../../docs/plano/ESTADO-ATUAL.md): "Não misturar pastas nem pedidos").
4. **28/09/2026: a `st_gravura.dll`** (item [1.2](../itens/1.2.md)). Pesquisa:
   [`docs/pesquisa/fase1-1.2-scantailor.md`](../../docs/pesquisa/fase1-1.2-scantailor.md) (caminho "(b)": só o detector
   como DLL com função em C, sem pybind11, para não depender do Python 3.14). Sete blocos de `OutputGenerator.cpp`
   copiados **letra por letra** (`detectPictures`, `estimateBinarizationMask`, `findRectAreas`...), conferidos a cada
   rodada por `tests/test_gravura_scantailor.py::test_funcoes_copiadas_sem_mudanca`. Ligada ao programa em 30/09;
   **1.2 aprovado pelo Samuel em 02/10/2026** (M2). Ressalva guardada: a DLL sempre trata a página como "preto no
   branco" (no teste de 24/09 o ScanTailor inverteu a Horas 11 sozinho).
5. **01/10/2026: Fase 2 adiantada e o mapa das 19 ferramentas.** Samuel (conferência 5, X3): "eu quero ter a opção de
   colocar [o filtro] onde eu escolher, se quero só nos textos ou nas gravuras, como tem no ScanTailor Advanced; acho
   que o melhor é pularmos algumas coisas e já instalarmos ele junto do programa", e escolheu "c" (adiantar a Fase 2
   inteira). O pesquisador mapeou as 19 ferramentas: [`docs/pesquisa/fase2-mapa-scantailor.md`](../../docs/pesquisa/fase2-mapa-scantailor.md)
   (onde cada uma mora no código, o que já temos, esforço e risco; o modo Misto por dentro, seção 5).
6. **06/10/2026: a DLL comum `st_ferramentas.dll`** (M9), ao lado da do 1.2, com o limpar pontinhos (`Despeckle`,
   6 arquivos); no mesmo dia o dividir (`estimatePageLayout`, 50 arquivos, item 2.1) e o endireitar (`SkewFinder` +
   limpeza de sombras do `deskew::Task`, 4 arquivos, item 2.2). Juntados ao `fase-1` em 07 e 08/10.
7. **12-13/10/2026: busca de página e caixa do conteúdo** (`PageFinder` + `ContentBoxFinder`, 18 arquivos) no ramo
   `fase2-caixa-conteudo` (`19e8e56`), **não ligados a nada** (itens [2.13](../itens/2.13.md) e [2.5](../itens/2.5.md)).
8. **13/10/2026: regra da Fase 2, "igual ao ScanTailor sem perguntar"** (abaixo).
9. **20/10/2026 (hoje):** o ramo `fase2-scantailor-itens-2026-10-19` começou o 2.8 (os dez preto e branco do
   `Binarize.cpp`); tem um `ligacao-ferramentas/saida.cpp` novo e uma pasta de rascunho de compilação criada hoje,
   `D:\programas\EditorImpressao-arquivos\ferramentas\build-st-ferramentas-fase2-itens`. O `fase2-caixa-conteudo`
   também voltou a andar (ligar o corte só depois da resposta `g7-borda-ate-onde`). Ver [ramos](../ramos.md).

## A regra de 13/10/2026: igual ao ScanTailor, sem perguntar antes

Palavras do Samuel (Registro 13/10/2026): "mas eu preciso responder o que? não dá para simplismente implementar no
programa?"; à proposta da regra, "ok". Como ficou na seção da Fase 2 do plano: "(1) cada ferramenta vem igual à do
ScanTailor, com os ajustes de fábrica dele; (2) quando ela muda a imagem, vem desligada de fábrica, para livro já
começado sair igual ao de hoje; (3) o botão vai para o lugar que o layout já decidido manda (painel Propriedades ou
painel Filtro), sem rodada nova de perguntas; (4) o Samuel só confere no fim, em fotos ("Está bom / Melhorar / Está
pior"), porque só ele aprova. Pergunta antes de construir só quando houver uma escolha de verdade que o ScanTailor não
resolve." Vale para os nove itens sem perguntas: 2.8 a 2.12, 2.15 a 2.17 e 2.19.

Decisões anteriores que continuam valendo nesses itens (conferência 10, 05/10/2026): P8 (b) "trazer os dez jeitos de
preto e branco do ScanTailor como opções a mais"; P9 (a) caixinha por página "Letra clara em fundo escuro", à mão;
P10 (a) "letras com a cor delas" como opção, desligada de fábrica (Registro 05/10/2026).

## Como foi compilado

Os dois scripts estão na raiz (leia o topo de cada um):
[`compilar_detector_gravura.py`](../../compilar_detector_gravura.py) (a `st_gravura.dll`) e
[`compilar_st_ferramentas.py`](../../compilar_st_ferramentas.py) (a `st_ferramentas.dll`, que reaproveita as peças do
primeiro).

- **Ferramentas, só no PC de quem compila:** Visual Studio 2022 Build Tools (C++; `vcvars64.bat`) e CMake, instalados
  em 28/09/2026 (Registro 28/09/2026: "Instalados neste PC (sem reinício): Tesseract ..., CMake, Visual Studio 2022
  Build Tools (C++)"). Compilador anotado nas DLLs: MSVC 19.44.35229.0.
- **Qt 6.11.1 de desenvolvimento** (só `qtbase`, MSVC 2022 64 bits), baixado de download.qt.io e conferido pela soma
  SHA-1 do servidor; **tem de ser a mesma versão do Qt do PySide6** (o script recusa se não for), porque a DLL usa o
  `Qt6Core.dll` e o `Qt6Gui.dll` que o PySide6 já traz.
- **Boost 1.78.0**, só cabeçalhos, conferido pela soma SHA-256 de archives.boost.io.
- Tudo isso fora do git, em `D:\programas\EditorImpressao-arquivos\ferramentas\` (pastas `qt`, `boost`, `downloads`),
  com as pastas de rascunho `build-st-gravura`, `build-st-ferramentas`, `build-st-ferramentas-dividir`,
  `build-st-ferramentas-endireitar`, `build-st-ferramentas-endireitar-2`, `build-st-gravura-endireitar` e, de hoje,
  `build-st-ferramentas-fase2-itens`. Nada pede administrador; nada é instalado no Windows nem no `.venv`.
- **Soma SHA-256 conferida contra o git do ScanTailor:** cada arquivo de `src/` tem a soma em
  `terceiros/scantailor-advanced/somas-v1.2.1.txt`, tirada do `git show v1.2.1:` (fim de linha LF); o teste
  `tests/test_st_ferramentas.py` confere todos a cada rodada. Cuidado: o git deste PC troca o fim de linha (CR+LF), então
  `cmp` direto contra o GitHub dá "diferente" sem nada ter mudado; o LEIA-ME de `terceiros/` ensina os dois jeitos
  certos.
- **Versão da interface da DLL comum** (`ST_FERRAMENTAS_VERSAO_API`): 1 (pontinhos), 2 (dividir), **3 no `fase-1`**
  (endireitar), **4 no ramo `fase2-caixa-conteudo`** (caixas), e **5 no ramo `fase2-scantailor-itens-2026-10-19`**
  (o ONDE-PAREI dele: "Aqui a versão pula para 5, para não brigar; quem juntar os dois recompila a DLL").
- As DLLs guardadas: `core/nativo/st_gravura.dll` (compilada 28/09/2026 23:08; 166.912 bytes; SHA-256
  `833d03db...4193f`) e `core/nativo/st_ferramentas.dll` (06/10/2026 23:35; 215.040 bytes; SHA-256 `9c5a4920...74477`),
  cada uma com um `.txt` ao lado ([st_gravura.txt](../../core/nativo/st_gravura.txt),
  [st_ferramentas.txt](../../core/nativo/st_ferramentas.txt)). No ramo das caixas a comum foi a 298 KB.
- **A `st_gravura.dll` aprovada não é tocada** pelas recompilações da comum; cada vez que `src/` cresceu, ela foi
  recompilada num rascunho e deu as mesmas 64 máscaras (32 páginas × livre e retangular). Risco anotado no ONDE-PAREI
  das caixas: com os 18 arquivos novos, a próxima recompilação dela pode precisar de ajuste.
- Bug aberto: o `compilar_detector_gravura.py` não acha a pasta de ferramentas numa worktree (Lista de bugs 06/10/2026;
  o `compilar_st_ferramentas.py` contorna subindo as pastas). Ver [bugs](../bugs.md).
- Em 06/10/2026 o implementador do dividir perguntou se pode apagar uma pasta de rascunho criada fora do projeto
  (Registro 06/10/2026, nome escrito lá sem as barras: `EditorImpressao-arquivoserramentasuild-st-ferramentas-dividir`).
  Não achei resposta nas fontes lidas.

## O DPI muda o resultado (cuidado de sempre)

- As contas do ScanTailor dependem do DPI que o PDF **diz**. Vários PDFs do acervo dizem **72 DPI**, que não é a
  resolução de verdade (Horas, Graduale, Marial).
- Limpar pontinhos (06/10/2026): "Antes de ligar: acertar o DPI dos PDFs que dizem 72 DPI (o ScanTailor limpa menos
  neles)"; acertado "pela mesma conta do detector de gravura, com trava abaixo de 140 DPI" (Registro 06/10/2026).
- Caixa do conteúdo (Registro 13/10/2026): "o resultado muda com o DPI, e **as imagens das perguntas de 12/10 foram
  feitas a 72 DPI no Horas, Graduale e Marial**". Refeitas com o DPI do programa (Registro 13/10/2026): na Horas 14,
  com 141 em vez de 72, "o corte do ScanTailor deixa de fora **a moldura dourada inteira e o título "TABLE"**". Horas 13
  a 72 DPI dá quase a folha inteira; a 150 fica por dentro da moldura (ONDE-PAREI das caixas).
- Lista de bugs, 28/09/2026: "DPI absurdo faz a DLL do ScanTailor corromper a memória, e o programa fecha sem aviso";
  há trava em `core/gravura_scantailor.py` (teste `tests/test_gravura_no_processamento.py::test_dpi_absurdo_nao_chega_a_dll`).

## O que já veio, e o que falta trazer, por item

Fonte: o mapa de 01/10 (tabela da seção 2) e o estado dos ramos em 20/10/2026.

| Item | Peça do ScanTailor | Situação hoje |
|---|---|---|
| [1.2](../itens/1.2.md) | `detectPictures`, `estimateBinarizationMask`, `findRectAreas`, `normalizeIlluminationGray` (`st_gravura.dll`) | **no programa, aprovado** (02/10) |
| [2.1](../itens/2.1.md) | `PageLayoutEstimator::estimatePageLayout` | no programa; de fábrica "o do ScanTailor" ao marcar Dividir (07/10) |
| [2.2](../itens/2.2.md) | `SkewFinder::findSkew` + limpeza do `deskew::Task`; G6 (endireitar antes de cortar) | no programa (08/10 e 12/10). A correção "oblíqua" não foi trazida (desligada de fábrica no ScanTailor) |
| [2.3](../itens/2.3.md) | nada em C (o girar dele é só à mão) | feito com o jeito de aplicar dele |
| [2.4](../itens/2.4.md) | contas de margens `page_layout/Utils.cpp`, `Settings.cpp`, `Alignment.cpp` | **não trazidas** |
| [2.5](../itens/2.5.md) | `ContentBoxFinder` | no ramo `fase2-caixa-conteudo`, não ligado |
| [2.6](../itens/2.6.md) | o ScanTailor não tem papel-alvo | é nosso (fase de impressão; ver [updf](updf.md) e [embaralhador](embaralhador.md)) |
| [2.7](../itens/2.7.md) | `Despeckle` | no programa, **desligado de fábrica** (Samuel, 07/10/2026: "só deve ser usado se for selecionado junto") |
| [2.8](../itens/2.8.md) | `Binarize.cpp` (10 métodos), `SavGolFilter.cpp` | **em andamento hoje** (`fase2-scantailor-itens-2026-10-19`); os arquivos `Binarize.*` já estão em `src/` |
| [2.9](../itens/2.9.md) | `BlackOnWhiteEstimator` | o arquivo já veio com o endireitar; a caixinha por página falta |
| [2.10](../itens/2.10.md) | `SplittingOptions`, `OutputImageWithForegroundMask` | não trazido; junto do 1.6 |
| [2.11](../itens/2.11.md) | `ColorSegmenter`, `Posterizer` | não trazido |
| [2.12](../itens/2.12.md) | `dewarping/` (5.846 linhas) | não trazido; o maior e mais arriscado |
| [2.13](../itens/2.13.md) | `PageFinder` | no ramo `fase2-caixa-conteudo`, não ligado; sozinho não tira a borda do Siebmacher (só faixa que cobre 95% do lado) |
| [2.14](../itens/2.14.md) | `fillMarginsInPlace`, `fillExcept` | não trazido |
| [2.15](../itens/2.15.md) | `DeviationProvider` | não trazido (conta simples) |
| [2.16](../itens/2.16.md) | `WorkerThreadPool` | não trazido; as DLLs soltam o Python, mas duas chamadas ao mesmo tempo não foram testadas |
| [2.17](../itens/2.17.md) | `EstimateBackground`, `normalizeIlluminationGray` (já na `st_gravura`), `SavGolFilter`, `WienerFilter` | metade já compilada |
| [2.18](../itens/2.18.md) | regra das zonas `modifyBinarizationMask` e preenchimento | não trazida; a tela é nossa |
| [2.19](../itens/2.19.md) | só tela | nada a trazer em C |
| Misto ([1.5](../itens/1.5.md)) | bloco "Mixed" de `processWithoutDewarping` | o "Só as letras" (`core/misto.py`) faz "como o Misto do ScanTailor" em Python, com a máscara do 1.2 |

## Perguntas em aberto ligadas ao ScanTailor (exatas, da página de escolhas)

- `g7-borda-ate-onde`: "Página com borda preta: até onde vai o corte que o programa sugere?" (aberta em 19/10/2026;
  [histórico, PARTE -16 §4](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)). Comentário
  do Samuel em 13/10: "hoje no programa temos o motor de busca só do scantailor?"
- A pasta de rascunho fora do projeto (Registro 06/10/2026): "pode ser apagada?" (sem resposta achada).
