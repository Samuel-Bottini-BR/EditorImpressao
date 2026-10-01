# Fase 2: mapa das ferramentas do ScanTailor Advanced (o que trazer, de onde, em que ordem)

**Data:** 01/10/2026 · **Quem:** agente pesquisador · **Pedido:** gerente, Fase 2 adiantada pelo Samuel em 01/10 ("eu quero ter a opção de colocar [o filtro] onde eu escolher, se quero só nos textos ou nas gravuras, como tem no ScanTailor Advanced"; escolha "c", adiantar a Fase 2 inteira).

**Nada no programa foi mexido.** Li o código-fonte completo do ScanTailor Advanced **v1.2.1** (commit `5eaac18`, a mesma versão do item 1.2), que já estava em `D:\programas\EditorImpressao-arquivos\ferramentas\scantailor-advanced-v1.2.1\`. Para não responder só de leitura, compilei um teste pequeno numa pasta minha (`D:\programas\EditorImpressao-arquivos\ferramentas\pesquisa-fase2-2026-10-01\`, fora do projeto, 34 MB) e rodei as funções automáticas do ScanTailor nas 32 páginas do gabarito. Essa pasta fica lá até o Samuel dizer se pode apagar (regra do `CLAUDE.md`, seção 10, item 9).

Legenda: **[lido]** = está no código do ScanTailor; **[medido]** = rodei e vi; **[dedução]** = conclusão minha, não confirmada.

---

## 1. A resposta em cinco frases

1. **Quase tudo dá para trazer do jeito do 1.2** (função em C numa DLL, chamada pelo Python com a página na memória): no teste, as bibliotecas de imagem do ScanTailor, o desentortar e as funções automáticas de dividir, endireitar, caixa da página, caixa do conteúdo, claro-no-escuro, pontinhos, preto e branco e segmentação de cor **compilaram e rodaram sem a janela**, com só três arquivos pequenos a mais e uma função copiada como "cola" [medido].
2. O que **não** dá para trazer é a **tela** do ScanTailor (editor de zonas, guias, unidades, perfis, tema): é Qt Widgets, e a nossa é PySide6. Ali se traz a **regra** (o que cada tipo de zona faz) e se refaz a tela do nosso jeito; a aba Marcar já tem quase todas as formas de desenhar.
3. **O modo Misto é pequeno por dentro e é exatamente o pedido do Samuel:** a página inteira é passada para preto e branco, a máscara de gravura (a que o 1.2 já dá) diz onde fica a imagem original, e cinco tipos de zona feitas à mão corrigem a máscara; no fim, "zonas de preenchimento" pintam por cima. Isso dá para trazer como uma função só na DLL, usando o detector que já temos.
4. **Atenção a duas expectativas do plano que o código não confirma:** o "dividir" automático do ScanTailor decide pela proporção da folha, igual ao nosso (no teste ele cortou as claves do Graduale 222 e partiu a moldura do Siebmacher 9) [medido]; e o "endireitar" usa o mesmo método do nosso, com o mesmo ângulo em 28 das 32 páginas [medido]. Trazer esses dois ajuda, mas não resolve sozinho o "funciona mal": o ganho está na escolha por livro e por página e na correção à mão.
5. **Ordem sugerida:** primeiro a DLL comum e o **modo Misto com as zonas** (2.18, mais 2.7, 2.8, 2.11, 2.17 e 2.9, que são opções da mesma saída); depois a **geometria** na ordem do próprio ScanTailor (girar, dividir, endireitar, caixa da página, caixa do conteúdo, preencher fora, margens, tamanho); por último duas camadas (2.10, junto do 1.6), páginas diferentes (2.15), desentortar (2.12, o maior e mais arriscado), todos os núcleos (2.16, depende de decisão) e unidades/perfis/tema (2.19, tela).

### Tabela no formato do pesquisador

| O que é | Licença | Roda aqui? | Roda no notebook do Kaique? |
|---|---|---|---|
| ScanTailor Advanced v1.2.1, partes de processamento (imageproc, foundation, math, dewarping, filtros) | GPL-3.0 (os 801 arquivos de código `.cpp`/`.h` têm o cabeçalho GPLv3) | Sim: compilado com o Visual Studio 2022 e o Qt 6.11.1 que já estão neste PC para o 1.2 [medido] | Sim (é processador, sem placa de vídeo) [dedução, mesma base da `st_gravura.dll`] |
| Qt 6.11 (Core, Gui, Xml) | LGPL-3 | Sim (o PySide6 já traz) | Sim |
| Boost 1.78 (só cabeçalhos) | BSL-1.0 | Sim | Não precisa (entra na compilação) |

---

## 2. Tabela-resumo (ferramenta × onde no ScanTailor × o que temos × como trazer × esforço × risco)

Linhas de código contadas no v1.2.1 (`.cpp` + `.h`). "DLL" = o caminho do 1.2: função em C, `ctypes`, página na memória.

| # | Ferramenta | Onde no ScanTailor | O que temos hoje | Como trazer | Esforço | Risco |
|---|---|---|---|---|---|---|
| 2.1 | Dividir a folha | `src/core/filters/page_split/` (pasta: 5.030 l.; o cálculo: `PageLayoutEstimator.cpp` 760, `VertLineFinder.cpp` 310, `PageLayout.cpp` 373) | `core/dividir.py` (185 l.): folha com largura > 1,2 × altura é dividida na lombada | DLL com `estimatePageLayout` (rodou) + escolha "uma página / página com sobra / duas páginas" por livro e por página, e a linha arrastável (tela nossa) | médio | médio: o automático do ScanTailor também erra (seção 6.1) |
| 2.2 | Endireitar | `src/core/filters/deskew/` (2.463 l.; o cálculo: `imageproc/SkewFinder.cpp` 278 + limpeza de sombras ~40 em `Task.cpp` + `ObliqueFinder.cpp` 67) | `core/endireitar.py` (154 l.), mesmo método (perfil de projeção) | DLL: `SkewFinder` + limpeza; correção "oblíqua" opcional; ângulo à mão na tela | pequeno | baixo; ganho pequeno nas páginas do gabarito |
| 2.3 | Orientação / girar | `src/core/filters/fix_orientation/` (1.378 l.): **só à mão** (90° e aparar) | `girar_90` e botão girar | nada a trazer em C; copiar o jeito de aplicar (esta página, todas, pares/ímpares) na nossa tela | pequeno (núcleo), médio (tela) | baixo |
| 2.4 | Margens iguais + alinhamento | `src/core/filters/page_layout/` (5.032 l.; as contas: `Utils.cpp` 251, "tamanho agregado" em `Settings.cpp` 734, `Alignment.cpp` 97) | não existe (há folha A4/A5/Carta por página, `core/folha.py`) | contas na DLL (ou copiadas) + uma passada no livro inteiro para achar o maior conteúdo | médio | médio: muda o enquadramento de páginas já conferidas |
| 2.5 | Caixa da página e guias | caixa do conteúdo: `select_content/ContentBoxFinder.cpp` (1.331 l.); guias: só tela (`page_layout/ImageView.cpp`, 1.081 l.) | `core/recortar.py` (910 l., corte pela tinta com 1 mm de folga); guias e ímã em `ui/widgets/visualizador.py` | DLL: `findContentBox` (rodou) como **opção**; guias na nossa tela | médio | alto: no Horas 13 deixou a moldura dourada de fora (seção 6.5) |
| 2.6 | Tamanho final em cm/mm | o ScanTailor **não tem papel-alvo**; tem unidades (`Units*`, 326 l.) e DPI de saída | tem: A4/A5/Carta e cm (`core/folha.py`, diálogo "tamanho...") | manter o nosso; usar a conta do 2.4 para chegar no tamanho | pequeno | baixo |
| 2.7 | Limpar pontinhos | `src/core/Despeckle.cpp` (948 l.), força de 0,5 a 3,5 (padrão 1,0) | `_despeckle` em `core/filtros.py` (só pelo tamanho da mancha) | DLL (rodou) | pequeno | baixo |
| 2.8 | Preto e branco Sauvola e Wolf | `src/imageproc/Binarize.cpp` (763 l., **10 métodos**) + suavização Savitzky-Golay (`SavGolFilter.cpp` 279) e morfológica (~80 l. no `OutputGenerator.cpp`) | Sauvola, Otsu e Wolf pelo DoxaPy, com escolha automática e k pela letra | DLL: métodos do ScanTailor como **opções a mais**, sem trocar o padrão aprovado | pequeno | médio |
| 2.9 | Texto claro em fundo escuro | `src/core/BlackOnWhiteEstimator.cpp` (106 l.); a saída inverte a página na entrada e de novo no fim | não tem | DLL + caixinha por página; detecção automática desligada de fábrica | pequeno | baixo (à mão), médio (automático) |
| 2.10 | Saída em duas camadas | `output/SplittingOptions`, `OutputImageWithForegroundMask.cpp` (67 l.); `output/Task.cpp` grava "foreground" e "background" | não tem (é o item 1.6) | as máscaras saem de graça do Misto; montar o PDF em duas camadas é nosso (PyMuPDF) | médio | médio |
| 2.11 | Segmentação de cor / reduzir cores | `imageproc/ColorSegmenter.cpp` (408 l.), `imageproc/Posterizer.cpp` (399 l.) | não tem | DLL (rodou: Horas 13 com títulos em vermelho e azul, seção 6.11) | pequeno | baixo |
| 2.12 | Desentortar página curva | `src/dewarping/` (5.846 l.) + `math/spfit` e `math/adiff` (math: 4.841 l.) + ~700 l. no `OutputGenerator.cpp` | não tem | DLL grande (a biblioteca compilou; a ligação não foi feita) | grande | alto |
| 2.13 | Página dentro da borda preta do scanner | `select_content/PageFinder.cpp` (223 l.), **desligado de fábrica** | `recortar.py` para no escuro do scanner (`_parar_no_escuro`) | DLL (rodou; o gabarito quase não tem borda preta, não deu para julgar) | pequeno | médio |
| 2.14 | Preencher com branco o que sobra fora da página | `OutputGenerator.cpp` (`fillMarginsInPlace`, `fillExcept`, ~150 l.); opções em `ColorCommonOptions` | em parte (`compor_na_folha` põe branco em volta do recorte) | DLL, junto do Misto | pequeno | baixo |
| 2.15 | Destacar páginas diferentes das outras | `src/core/DeviationProvider.h` (163 l.), usado em deskew, select_content e page_layout | não tem | conta simples (média e desvio-padrão); pode ser copiada para Python | pequeno | baixo |
| 2.16 | Usar todos os núcleos | `src/core/WorkerThreadPool.cpp` (90 l.): uma página por linha de execução | não (só o desenho do PDF vai para outro processo) | várias linhas no Python chamando as DLLs (o `ctypes` solta o GIL) | médio | médio: choca com "uma página por vez na memória" |
| 2.17 | Normalizar iluminação e suavizar | `EstimateBackground.cpp` (289) e `normalizeIlluminationGray` (**já estão na `st_gravura.dll`**), `SavGolFilter.cpp` (279), `WienerFilter.cpp` (160) | o Melhorar (divisão pelo fundo, nosso) | DLL (metade já compilada) | pequeno | baixo a médio |
| 2.18 | Edição manual das zonas de gravura | regra: `modifyBinarizationMask` (~60 l.) e preenchimento (~120 l.) no `OutputGenerator.cpp`; dados: `core/zones` (`Zone`, `ZoneSet`, ~150 l.); tela: `interaction/`, `zones/`, editores (~3.200 l., Qt Widgets) | aba Marcar: retângulo, oval, laço, polígono, pincel, varinha, desfazer, "só neste pedaço" | regra na DLL; tela nossa (PySide6), com copiar, colar e mover zona | grande (tela), médio (regra) | médio |
| 2.19 | Unidades cm/mm, perfis, tema claro/escuro | `Units*` (326 l.), `DefaultParams*` (947 l.), `*ColorScheme*` (524 l.): tudo janela e configuração | tela de Configurações com atalhos; sem tema | nada a trazer em C; fazer na nossa tela | pequeno a médio | baixo (o tema é do agente de layout) |
| — | Modo Misto (base de 2.10, 2.11, 2.18) | bloco "Mixed" de `processWithoutDewarping` (~100 l.) + `imageproc/ImageCombination.cpp` (408 l.) | máscara do 1.2 ligada; filtro por pedaço na aba Marcar | DLL: montar a página como o ScanTailor (seção 5) | médio | médio |
| — | Aba Bordas e margens (a aperfeiçoar) | `page_layout` + `select_content` | aba Bordas (espelhado, proporção travada, cm, A4/A5, moldura, mover conteúdo) | junto de 2.4 a 2.6 | médio | médio |
| — | Aba Filtro (a aperfeiçoar) | `Binarize.cpp`, `Despeckle.cpp` | aba Filtro (Sauvola, Otsu, Wolf, pontinhos, aviso escuro/apagado) | junto de 2.7 e 2.8 | pequeno a médio | médio |

---

## 3. Licença

- **Todo o código do ScanTailor Advanced v1.2.1 é GPL-3** [lido]: os arquivos têm o cabeçalho "Use of this source code is governed by the GNU GPLv3 license"; um único arquivo novo (`fix_orientation/DeskewExternalToolSpike.h`, só comentário, não compila nada) diz "GPL-3.0-or-later". Procurei MIT, BSD, Apache, LGPL e "public domain" no código: nada além do texto da GPL.
- Um trecho de `OutputGenerator.cpp` (contar bits, linhas ~780-810) vem do "Bit Twiddling Hacks" de Sean Anderson, que é **domínio público** [lido no comentário]: não muda nada.
- Por fora: **Qt** LGPL-3 (já no programa pelo PySide6), **Boost** BSL-1.0 (só cabeçalhos). Os ícones e temas do ScanTailor (`src/resources/`) não seriam usados.
- O que obriga: como no 1.2, se o programa for distribuído, vai com o código-fonte (o Samuel liberou em 17/09). Nenhuma parte pede outra coisa.

---

## 4. Como o ScanTailor é montado (o que importa para trazer)

### 4.1 Seis etapas, um caminho de geometria [lido]

O ScanTailor processa cada página em seis etapas, nesta ordem: **girar** (`fix_orientation`) → **dividir** (`page_split`) → **endireitar** (`deskew`) → **caixa da página e do conteúdo** (`select_content`) → **margens** (`page_layout`) → **saída** (`output`: desentortar, preto e branco, Misto, pontinhos, preenchimentos).

As cinco primeiras **não mexem nos pontos da imagem**: cada uma só acrescenta uma conta de geometria (`ImageTransformation`: giro, polígono de corte, ângulo). A imagem só é redesenhada uma vez, na saída. As zonas feitas à mão são guardadas nas **coordenadas da folha original** e levadas para a saída pela mesma conta.

O nosso programa faz parecido mas redesenha a cada etapa (gira, corta, endireita), e a ordem é outra: **cortar antes de endireitar** (`core/pipeline.py`, ordem do `CLAUDE.md`). Trazer as ferramentas uma a uma **não obriga** a mudar isso: cada função recebe uma imagem. Mas há uma consequência séria, na seção 4.3.

### 4.2 O que é núcleo e o que é tela [lido + medido]

Em cada etapa o ScanTailor separa:
- **o cálculo**, em funções "estáticas" que recebem a imagem e devolvem um resultado (por exemplo `PageLayoutEstimator::estimatePageLayout(tipo, imagem, geometria, limiar)`, `SkewFinder::findSkew(imagem)`, `ContentBoxFinder::findContentBox(...)`, `PageFinder::findPageBox(...)`, `Despeckle::despeckleInPlace(...)`);
- **o "Task"**, que lê e grava as escolhas do projeto (modo automático ou à mão, "aplicar a todas") e chama o cálculo;
- **a tela** (`OptionsWidget`, `ImageView`, diálogos), em Qt Widgets.

**Teste feito (01/10):** compilei numa biblioteca só `imageproc` (44 arquivos), `foundation`, `math` (com `spfit` e `adiff`), `dewarping` e os arquivos de cálculo de `page_split`, `deskew`, `select_content`, mais `Despeckle`, `BlackOnWhiteEstimator`, `EstimateBackground`, `FilterData`, `ImageTransformation`. **Compilou de primeira** com o mesmo kit do 1.2 (MSVC 2022, Qt 6.11.1, Boost 1.78). Para o programa de teste ligar, faltaram só `PageId.cpp`, `ImageId.cpp`, `RelinkablePath.cpp` (pequenos, do projeto) e **uma** função de `ProjectPages` (`adviseNumberOfLogicalPages`, 10 linhas), copiada sem mudança como "cola", igual ao que o 1.2 fez. O executável de teste ficou com 290 KB.

Conclusão: o caminho do 1.2 serve para todas as ferramentas de cálculo. A sugestão é **uma DLL nova** (por exemplo `st_ferramentas.dll`) com as mesmas pastas de `terceiros/scantailor-advanced/src/` aumentadas, várias funções em C (uma por ferramenta) e o mesmo teste que confere, a cada rodada, que os trechos copiados não mudaram. A `st_gravura.dll` fica como está até a nova dar a mesma máscara nas páginas do gabarito; depois as duas podem virar uma [dedução].

### 4.3 Cuidado: as zonas guardadas em fração da página preparada [lido no nosso código]

A nossa seleção (aba Marcar) guarda as zonas em **fração da página já dividida, cortada e endireitada** (`core/selecao.py`, `core/pipeline.garantir_selecao`: "a seleção guarda frações daquele recorte"). Se o 2.1, 2.2, 2.5 ou 2.12 mudarem o corte ou o ângulo de uma página, **as zonas feitas à mão nos projetos que já existem ficam deslocadas**. O ScanTailor evita isso guardando as zonas na folha original. Recomendação [dedução]: antes de mexer na geometria, guardar as zonas novas na folha original (ou converter as antigas na hora de abrir), e o verificador conferir projeto antigo aberto depois da mudança.

---

## 5. O modo Misto por dentro (itens 2.10, 2.11, 2.18)

### 5.1 Em uma frase

O Misto **passa a página inteira para preto e branco**, decide **ponto por ponto** onde mostrar esse preto e branco e onde mostrar a **imagem original**, e essa decisão vem de uma **máscara** (o detector automático, que o 1.2 já trouxe) corrigida por **zonas desenhadas à mão**; no fim, **zonas de preenchimento** pintam por cima com uma cor.

### 5.2 Passo a passo (`OutputGenerator.cpp`, `processWithoutDewarping`, linhas 1275-1530) [lido]

1. **Prepara a página:** gira e recorta pela geometria das etapas anteriores e **iguala a luz** (estima o fundo e divide por ele; `normalizeIlluminationGray`). Na página colorida, a correção de luz feita no cinza é aplicada às cores (`adjustBrightnessGrayscale`).
2. **Faz o preto e branco da página inteira** (`binarize`): de fábrica **Otsu** (um limiar só), com suavização Savitzky-Golay antes e morfológica depois; Sauvola, Wolf e outros 7 métodos são opções.
3. **Máscara de gravura:** branco = imagem, preto = texto. Vem do detector automático (`processPictureZones` → `estimateBinarizationMask`, o mesmo do 1.2). Na forma "retangular", os retângulos achados viram **zonas automáticas editáveis**.
4. **Aplica as zonas feitas à mão** (`modifyBinarizationMask`, linhas 1975-2033), em cinco passadas, nesta ordem (a de baixo vence a de cima):

   | Nome na tela do ScanTailor | Nome interno | O que faz dentro da zona |
   |---|---|---|
   | "Subtrair da camada automática" | `ZONEERASER1` | apaga o que o detector achou: ali vira texto (preto e branco); zonas dos tipos de baixo ainda valem por cima |
   | "Somar ao primeiro plano" | `ZONEFG` | **a tinta fica com a cor original e o papel vai a branco** (o preto e branco decide o que é tinta) |
   | "Somar ao fundo" | `ZONEBG` | a tinta vira **preto puro** e o fundo fica **como no original** |
   | "Somar à camada automática" | `ZONEPAINTER2` | tudo fica como no original (é "isto é gravura") |
   | "Subtrair de todas as camadas" | `ZONEERASER3` | tudo vira preto e branco, vence todas as outras |

   (O efeito exato de "primeiro plano" e "fundo" é conta minha a partir das operações de bits do código: a máscara é trocada por "o contrário do preto e branco" dentro da zona no primeiro caso, e "igual ao preto e branco" no segundo. Vale conferir numa página antes de pôr nomes na tela [dedução].)
5. **Tira os pontinhos** do preto e branco (`maybeDespeckleInPlace`), sempre por último na parte preto e branco.
6. **Volta a cor sem igualar a luz** onde é imagem (a opção "Igualar a luz (cor)" vem **desligada**): as imagens saem "como estão".
7. **Junta** (`combineImages`): onde a máscara diz texto, o ponto preto ou branco; onde diz imagem, o ponto original. Opcional: em vez de preto, **pintar cada letra com a cor dela** (segmentação de cor, 2.11).
8. Reserva o preto e o branco puros para o texto (as imagens perdem o 0 e o 255, viram 1 e 254), para depois dar para separar as camadas.
9. **Preenche** margens e o que está fora da página (branco, preto ou a cor do fundo, 2.14) e põe na folha do tamanho final (margens do 2.4).
10. **Zonas de preenchimento** (aba própria, "Fill zones"): cada polígono é pintado com uma cor escolhida com conta-gotas na página; no Misto, a cor vale tanto na parte preto e branco quanto na imagem. É o "apagar" do ScanTailor (carimbo, mancha, número de biblioteca).
11. **Duas camadas** (2.10), se pedido: grava a página em dois arquivos, "primeiro plano" (as letras, em 1 bit ou com cor) e "fundo" (as imagens), e, com "fundo original", um terceiro com o papel de verdade.

**Editor de zonas** [lido no README e no código]: polígono (Z), laço livre (X), retângulo (C); arrastar zona com Shift; **copiar zona** arrastando com Ctrl+Shift; **colar a última zona** onde está o mouse com Ctrl+Alt+clique; apagar zona (Del) ou um vértice (D); Ctrl deixa o ângulo reto. Cada zona tem um diálogo com os cinco tipos acima.

### 5.3 Comparação com a nossa aba Marcar ("só neste pedaço")

| | ScanTailor (Misto) | Nosso programa hoje |
|---|---|---|
| Quantos tratamentos | **dois**: preto e branco (texto) ou original (imagem), mais as variações "primeiro plano" e "fundo" | **quatro filtros** (Original, Preto e branco, Melhorar, Mágico pro), e cada tipo de área (gravura, letra, papel, fora) muda **como** o filtro trata aquela área |
| Quem acha a gravura | o detector (já trazido no 1.2) | o mesmo detector (1.2), mais letra e papel pelo detector antigo |
| Corrigir à mão | 5 tipos de zona + zonas de preenchimento com cor | tipos gravura/letra/papel/fora, somar ou tirar, e **filtro só neste pedaço** (`Regiao.filtro`) |
| Formas | polígono, laço, retângulo; mover, copiar, colar | retângulo, oval, laço, polígono, pincel, varinha mágica, desfazer; **sem** copiar, colar e mover |
| Papel dentro da zona | segue a zona (a imagem sai com o papel amarelado dela) | segue a **página** (`_filtro_so_no_pedaco`: o papel da zona vai a branco, só o conteúdo segue o filtro da zona) |
| Onde guarda | na folha original (sobrevive a mudar corte e ângulo) | em fração da página preparada (ver 4.3) |

O que o Samuel pediu ("só nos textos ou nas gravuras") **já existe em parte** no nosso: uma zona com "só neste pedaço = Original" numa página em Preto e branco dá quase o "Somar ao primeiro plano" do ScanTailor (conteúdo original, papel branco). O que falta é: (1) **o automático fazer isso em toda a página**, sem desenhar zona, com a máscara do 1.2 (é o Misto); (2) poder escolher **o filtro do texto e o filtro da imagem** separadamente; (3) os tipos "primeiro plano", "fundo" e "preenchimento com cor"; (4) copiar, colar e mover zona.

**Sugestão** [dedução]: trazer o Misto do ScanTailor como **montagem na DLL** (passos 1 a 9, copiados sem mudança, como o 1.2 copiou o detector), com as zonas mandadas do Python como polígonos; e, na tela, mostrar como "Texto em: [filtro]" e "Gravuras em: [filtro]", com o ScanTailor dando o caso de fábrica (texto em Preto e branco, gravura em Original). Isso cobre a caixinha "Só as letras" do 1.5 pelo lado do ScanTailor; o 1.5 continua para depois, para melhorar a máscara com o OCR.

**O que o Misto do ScanTailor não resolve** [lido + 1.2]: o papel **dentro** da gravura fica amarelado (a imagem sai como está), contra a regra R1 do Samuel; isso continua sendo trabalho do 1.4/1.5 ou de um filtro nosso na parte "imagem".

---

## 6. Uma seção por ferramenta

Tempos medidos no teste (um núcleo, PC dividido com outro agente, páginas do gabarito de 150 a 400 DPI): servem só de ordem de grandeza.

### 6.1 Dividir a folha (2.1)

- **Onde:** `src/core/filters/page_split/`. O cálculo é `PageLayoutEstimator::estimatePageLayout` (760 l.), que tenta primeiro achar a **linha da dobra** (`VertLineFinder`, linhas verticais pela transformada de Hough, 310 l.) e, se não achar, corta no **maior espaço em branco** (`cutAtWhitespace`). Três tipos: "uma página sem corte", "uma página com sobra" (corta a beirada da folha vizinha) e "duas páginas". Depende de `imageproc` e de uma função de `ProjectPages`.
- **Como o automático decide quantas páginas** [lido, `ProjectPages.cpp` linhas 205-214]: **folha mais larga que alta = duas páginas**. É a mesma regra do nosso (`dividir.py`: largura > 1,2 × altura). O ScanTailor **não sabe pelo conteúdo** que a folha é uma só; ele resolve pela escolha da pessoa ("aplicar a todas") e pela linha arrastável.
- **Medido nas 32 páginas:**
  - Siebmacher 7 e 9 (paisagem, uma página só): o automático do ScanTailor dividiu em **duas páginas a 80-82% da largura, passando pela moldura da direita**; o nosso divide a 57-58%, no meio do poema (confiança 0,22-0,24). Os dois erram. No modo "uma página com sobra", o ScanTailor manteve a página inteira (cortes a 4% e 96%), mas **não** tirou a beirada escura do livro.
  - Opus Majus 256 (tabela em paisagem): o ScanTailor dividiu no meio (50%); o nosso não divide (proporção 1,19, abaixo de 1,2).
  - Páginas em retrato: o ScanTailor escolhe "uma página com sobra" e corta linhas verticais. No **Graduale 222 o corte da esquerda (23% da largura) passa em cima das claves e das primeiras letras de todas as linhas**; no Opus 20 os cortes caem na beirada da foto. Imagens: `...\pesquisa-fase2-2026-10-01\saida\corte_*.jpg` (linhas vermelhas = cortes; azul = divisão em duas páginas).
  - Tempo: 10 a 150 ms por folha.
- **O nosso:** funciona para folha dupla de verdade; erra a folha paisagem de uma página (é o que o plano diz).
- **Como trazer:** DLL com `estimatePageLayout` (já rodou). O ganho real está na **tela**: escolher "uma página / uma página com sobra / duas páginas" por livro e por página, com o automático só como sugestão, e arrastar a linha. Sugiro, de fábrica, "uma página" quando o livro não for marcado como de folha dupla [dedução].
- **Esforço:** médio (núcleo pequeno, tela média). **Risco:** médio.
- **Bugs da Lista que entram aqui:** nenhum direto; o "Dividir folhas ao meio" que voltava marcado já foi consertado.

### 6.2 Endireitar (2.2)

- **Onde:** `src/core/filters/deskew/Task.cpp` (332 l.) chama `imageproc/SkewFinder` (278 l.): preto e branco por Otsu, **apaga as sombras horizontais compridas** (`cleanup`, abertura 200×14 a 150 DPI), e procura o ângulo pelo perfil de projeção com cisalhamento, até 7°, precisão 0,1°, só aceita com confiança ≥ 2,0. Opções novas na v1.2.1: usar a **beirada de cima da página** (para scans de livro com fundo escuro) e correção **oblíqua** (cisalhamento, `ObliqueFinder.cpp`, desligada de fábrica).
- **O nosso:** `core/endireitar.py`, **o mesmo método** (perfil de projeção), até 5°, a 700 px de altura.
- **Medido nas 32 páginas** (só o `SkewFinder`, sem a limpeza das sombras): **em 28 páginas os dois dão o mesmo ângulo, com diferença de até 0,2°**. Diferem: **Horas 11** (sentidos opostos: o ScanTailor gira 0,5° para um lado, o nosso 0,8° para o outro; não conferi qual está certo), **Horas 47** (0,5° contra 0,1°, o nosso com confiança baixa), Siebmacher 7 e 9 (0,25° contra 0°). O ScanTailor levou 0 a 10 ms; o nosso, 22 a 44 ms.
- **Conclusão:** nas páginas do gabarito o nosso não "funciona mal" no ângulo. O defeito que o Samuel vê deve estar em outro lugar (página sem texto, página de ilustração, a folga do giro de menos de 1 mm que está na Lista de bugs, ou a tela). **A gerente precisa perguntar quais páginas** [dedução].
- **Como trazer:** DLL com `SkewFinder` + a limpeza copiada do `Task.cpp`; ângulo à mão na tela; a correção oblíqua como opção.
- **Esforço:** pequeno. **Risco:** baixo (mas o ganho pode ser pequeno).
- **Bug que entra aqui:** "páginas endireitadas ficam com menos de 1 mm nos cantos" (01/10, `recortar.alargar_para_o_giro`).

### 6.3 Orientação / girar (2.3)

- **Onde:** `src/core/filters/fix_orientation/` (1.378 l.). **Não há nada automático** [lido]: são botões de girar 90° (esquerda, direita, 180°), "reiniciar", "aplicar a" (esta página, todas, daqui em diante, alternadas, selecionadas) e um "aparar" à mão (v1.2.1). O giro entra na conta de geometria antes de tudo, e as etapas seguintes recalculam sozinhas.
- **O nosso:** `endireitar.girar_90` e o botão girar. Não achei registrado o que "funciona mal" no girar; a gerente precisa perguntar ao Samuel.
- **Como trazer:** nada em C. Copiar o **jeito**: girar por página com "aplicar a todas / pares / ímpares", e que girar refaça dividir, corte e endireitar da página.
- **Esforço:** pequeno no núcleo, médio na tela. **Risco:** baixo.

### 6.4 Margens iguais em todas as páginas + alinhamento (2.4)

- **Onde:** `src/core/filters/page_layout/`. Como funciona [lido, `Utils.cpp` e `Settings.cpp`]: cada página tem a **caixa do conteúdo** (2.5) e **margens fixas** em mm (de fábrica 10 mm dos lados e 5 mm em cima e embaixo). O programa guarda o **maior tamanho** (conteúdo + margens) entre todas as páginas do livro e aumenta cada página até esse tamanho, distribuindo a sobra conforme o **alinhamento** (em cima / meio / embaixo × esquerda / meio / direita, "automático" ou "como no original"). "Margens automáticas" mede as margens que a página já tinha. Dá para aplicar margens "a páginas alternadas", o que permite esquerda e direita diferentes para a costura (R3).
- **Depende de:** a caixa do conteúdo de **todas** as páginas antes de montar qualquer uma.
- **O nosso:** não há igualar entre páginas. Há o tamanho da folha por página e o conteúdo centralizado (`core/folha.compor_na_folha`), com o mover conteúdo preparado mas ainda não ligado.
- **Como trazer:** as contas são pequenas (`calcSoftMarginsMM`, `calcPageRectPhys`, ~250 l.); podem ir na DLL ou ser copiadas. O trabalho de verdade é uma **passada no livro inteiro** (a análise já passa por todas as folhas) e a tela.
- **Esforço:** médio. **Risco:** médio: muda o enquadramento das páginas já conferidas e o corte com 1 mm aprovado em 01/10 precisa conviver com as margens em mm.

### 6.5 Caixa da página e guias (2.5)

- **Onde:** `select_content/ContentBoxFinder.cpp` (1.331 l.) acha a **caixa do conteúdo**: preto e branco, separa "sujeira" (sombras compridas, coisas encostadas na borda), estima onde há texto e apara. Modos: automático, à mão, desligado; duplo clique ajusta a caixa ao conteúdo [lido no README]. As **guias** são só da tela de margens (`page_layout/ImageView.cpp`: "adicionar guia horizontal/vertical", arrastar).
- **O nosso:** `core/recortar.py` corta **pela tinta**, com folga de 1 mm e sem partir peça de tinta (aprovado 01/10). Guias e ímã: `ui/widgets/visualizador.py` (`guias_ativas`, `encaixar_no_ima`).
- **Medido:** em várias páginas a caixa do ScanTailor é mais justa e segue a moldura (Horas 26: abraça a moldura e deixa a margem de papel de fora; Siebmacher 9: deixa de fora a beirada escura do livro, o nosso não). Mas no **Horas 13 a caixa do ScanTailor ficou por dentro da moldura dourada** (a moldura ficou de fora e "pag. 54" encostado na borda) [medido]: o ScanTailor trata linha comprida e reta como sombra de scanner [dedução pelo nome das funções `filterShadows`/`segmentGarbage`]. Imagens: `saida\caixa_*.jpg` na pasta do teste (vermelho = ScanTailor, azul = nosso corte). Tempo: 90 a 850 ms por página (o Horas 13 foi o mais lento).
- **Como trazer:** DLL com `findContentBox` (já rodou), **como opção** ("seguir a beirada da moldura/do papel", que o Samuel pediu em 28/09 para o Livro de Horas), não como troca do corte aprovado.
- **Esforço:** médio. **Risco:** alto se trocar o corte de fábrica; médio como opção.
- **Bugs que entram aqui:** "Cvii" do Graduale 221 cortado (o ScanTailor também corta perto: caixa começa na mesma altura); aba Bordas mostrando a folha inteira; aviso "encostou no conteúdo" calculado a 150 DPI.

### 6.6 Tamanho final da página em cm/mm (2.6)

- **Onde:** o ScanTailor **não tem tamanho de papel-alvo** (A4) [lido]: o tamanho da saída é conteúdo + margens, no DPI de saída escolhido (padrão 600). Tem um sistema de unidades (pixels, mm, cm, polegadas) que vale para margens e medidas.
- **O nosso:** já tem A4/A5/Carta e medidas em cm (`core/folha.py`, `ui/dialogo_tamanho_da_folha.py`).
- **Como trazer:** manter o nosso; o 2.4 dá o tamanho do conteúdo + margens, e o nosso põe na folha A4 sem cortar nada. Atenção: se o maior conteúdo + margens passar do A4, o `compor_na_folha` hoje devolve sem mudar (não reduz) [lido no nosso].
- **Esforço:** pequeno. **Risco:** baixo.

### 6.7 Limpar pontinhos, com controle de força (2.7)

- **Onde:** `src/core/Despeckle.cpp` (948 l.). Olha o **tamanho** da mancha **e a distância** dela até as outras peças (uma mancha pequena perto de letra é poupada, por exemplo pingo de i e pontuação). Três níveis (cuidadoso, normal, agressivo), e a v1.2.1 interpola entre eles com um controle de 0,5 a 3,5 (padrão 1,0) [lido].
- **O nosso:** `_despeckle` em `core/filtros.py`: só o tamanho da mancha, proporcional à resolução.
- **Medido:** rodou em todas as páginas (13 a 400 ms); na força 1,0 tirou de 1 a 675 pontos pretos por página, sobre o Otsu.
- **Como trazer:** DLL; controle de força na aba Filtro.
- **Esforço:** pequeno. **Risco:** baixo.

### 6.8 Preto e branco Sauvola e Wolf (2.8)

- **Onde:** `src/imageproc/Binarize.cpp` (763 l.): Otsu, Sauvola, Wolf, Fox, Window, Bradley, Grad, EdgePlus, BlurDiv, EdgeDiv. **De fábrica o ScanTailor usa Otsu**, com igualar a luz, suavização Savitzky-Golay antes e morfológica depois, e um ajuste de limiar; Sauvola com janela 200 e k 0,34 [lido, `BlackWhiteOptions.cpp`].
- **O nosso:** Sauvola (padrão), Otsu e Wolf, pelo DoxaPy (CC0), escolha automática pela espessura do traço, k pela letra, e as regras do Samuel (vermelho sai preto, foto em cinza, decoração em cor). É o filtro mais trabalhado e com decisões aprovadas.
- **Medido:** o Sauvola do ScanTailor, na Horas 13, **manteve as letras coloridas** (TABLE e CONTENU em vermelho, DE CE QUI EST em azul) em preto, sem apagar (seção 6.11). Isso interessa ao defeito I2/A1 da conferência 5 ("o Preto e branco apaga letras coloridas"), mas foi uma página só.
- **Como trazer:** DLL com os métodos do ScanTailor como **opções a mais** na aba Filtro (e a suavização). Trocar o padrão mudaria páginas já conferidas: só com rodada de antes/depois e decisão do Samuel.
- **Esforço:** pequeno. **Risco:** médio.

### 6.9 Texto claro em fundo escuro (2.9)

- **Onde:** `src/core/BlackOnWhiteEstimator.cpp` (106 l.): Otsu, limpa, e conta se há mais preto que branco dentro da área de conteúdo. A saída, quando a página é "claro no escuro", **inverte a página na entrada, processa normalmente e inverte de novo no fim** (`initFilterData`, linhas 1242-1251). Tem caixinha por página; a detecção automática pode ser desligada [lido].
- **Medido:** as 32 páginas deram "preto no branco", **inclusive a Horas 11**. No teste de 24/09, o ScanTailor de verdade tinha decidido que a Horas 11 era "claro no escuro"; não reproduzi (talvez porque lá ele mede depois do corte, ou pela versão 2019) [dedução].
- **O nosso:** não tem.
- **Como trazer:** DLL + caixinha por página. A Lista de espera (28/09) já recomenda **não** trazer a detecção automática; sugiro trazê-la desligada de fábrica.
- **Esforço:** pequeno. **Risco:** baixo à mão, médio no automático.

### 6.10 Separar a saída em duas camadas (2.10)

- **Onde:** `output/SplittingOptions`, `OutputImageWithForegroundMask.cpp` (67 l.); `output/Task.cpp` grava as pastas "foreground", "background" e "original_background". Primeiro plano em 1 bit ou com cor; o fundo leva as imagens [lido].
- **O nosso:** não tem; é o item **1.6** (que o Samuel deixou para depois na Fase 1). A decisão P3 da conferência 5 diz "quero ter a opção 1.6, mas quero poder deixar como está".
- **Como trazer:** as máscaras saem do Misto sem custo; o que falta é **montar o PDF** em duas camadas (letra em 1 bit em cima, fundo comprimido embaixo), que é nosso (PyMuPDF), não do ScanTailor (ele só grava TIFFs).
- **Esforço:** médio. **Risco:** médio. Resolveria o PDF pesado da Lista de bugs (01/10: 25,6 MB por página na Horas 11).

### 6.11 Segmentação de cor / reduzir cores (2.11)

- **Onde:** `imageproc/ColorSegmenter.cpp` (408 l.): pega o preto e branco e a página colorida, separa as peças de tinta por cor (limiar de Otsu em cada canal: preto, vermelho, verde, azul, ciano, magenta, amarelo), tira o ruído e **pinta cada peça com a cor média dela**. `imageproc/Posterizer.cpp` (399 l.): reduz o número de cores (nível 4 de fábrica) [lido].
- **Medido (Horas 13, 26 e Graduale 223):** a página saiu com papel branco, texto preto, **títulos em vermelho e azul e a moldura em dourado chapado** (Horas 13). 120 ms a segmentação, 20-30 ms a redução de cores. Imagens em `...\pesquisa-fase2-2026-10-01\saida\` (painel `painel_horas13.jpg`).
- **O nosso:** não tem.
- **Como trazer:** DLL. Serve como opção "letras com a cor delas" e para o PDF leve (cores indexadas). Atenção: a regra aprovada do Preto e branco diz que **vermelho sai preto**; a segmentação seria opção, não o padrão. Ela só colore o que o preto e branco achou: se o preto e branco perder a letra colorida, ela continua perdida.
- **Esforço:** pequeno. **Risco:** baixo.

### 6.12 Desentortar página curva perto da lombada (2.12)

- **Onde:** `src/dewarping/` (5.846 l.: segue as linhas de texto, as beiradas de cima e de baixo, monta uma superfície cilíndrica e redesenha) + `math/spfit`, `math/adiff` (ajuste de curvas) + ~700 l. em `OutputGenerator.cpp` (`processWithDewarping`, `buildAutoDistortionModel`, `buildMarginalDistortionModel`, `dewarp`). Modos: desligado, automático, "marginal" (pela beirada curva sobre fundo preto) e à mão (malha azul com pontos vermelhos) [lido].
- **Medido:** a biblioteca `dewarping` **compilou** junto com o resto; a ligação (copiar `processWithDewarping`) não foi feita.
- **O nosso:** não tem.
- **Como trazer:** DLL, copiando as funções do `OutputGenerator` como no 1.2. O desentortar **muda a geometria**: a máscara de gravura, as zonas e o corte têm de ser feitos depois dele (ver 4.3). É redesenho de pontos (reamostragem), não inventa detalhe.
- **Esforço:** grande. **Risco:** alto. Páginas para conferir: Graduale 221 e Escola 7 (R5).

### 6.13 Detectar a página dentro da borda preta do scanner (2.13)

- **Onde:** `select_content/PageFinder.cpp` (223 l.): reduz a 150 DPI, faz cinco tipos de preto e branco e anda da borda para dentro enquanto for preto; opção de ajustar os cantos e de dar o tamanho esperado da página em mm (escolhe o preto e branco que mais se aproxima). **Desligado de fábrica** [lido, `DefaultParams.cpp`: `m_pageDetectMode(MODE_DISABLED)`].
- **Medido:** rodou (25 a 155 ms), mas as páginas do gabarito quase não têm borda preta: devolveu a folha inteira ou quase (Siebmacher e Marial um pouco menores). **Não deu para julgar.**
- **O nosso:** o corte para no escuro do scanner (`recortar._parar_no_escuro`) e tira borda sólida.
- **Como trazer:** DLL, como opção por livro.
- **Esforço:** pequeno. **Risco:** médio. Precisa de páginas com borda preta no gabarito.

### 6.14 Preencher com branco o que sobra fora da página (2.14)

- **Onde:** `OutputGenerator.cpp`: `fillMarginsInPlace`, `fillExcept` (~150 l.). Opções: preencher a sobra da divisão (ligado), preencher fora da caixa da página (desligado), preencher as margens (ligado); cor: a do fundo estimado, branco ou preto [lido, `ColorCommonOptions.cpp`].
- **O nosso:** em parte: `compor_na_folha` põe branco em volta do recorte; o "fora da página" depende do corte.
- **Como trazer:** na DLL, junto do Misto (é o passo 9 da seção 5.2).
- **Esforço:** pequeno. **Risco:** baixo.

### 6.15 Destacar páginas diferentes das outras (2.15)

- **Onde:** `src/core/DeviationProvider.h` (163 l.): média e desvio-padrão de um número por página; a página é "diferente" se se afasta mais que coeficiente × desvio (e mais que 1% da média). Números: ângulo de endireitar (coeficiente 1,5), diagonal da caixa do conteúdo (0,35), soma das margens (0,35). A tela marca a miniatura com asterisco vermelho e permite ordenar por diferença [lido].
- **O nosso:** não tem.
- **Como trazer:** é uma conta curta; pode ser copiada para Python (ou ir na DLL). Depende dos números do 2.2, 2.5 e 2.4.
- **Esforço:** pequeno. **Risco:** baixo.

### 6.16 Usar todos os núcleos do processador (2.16)

- **Onde:** `src/core/WorkerThreadPool.cpp` (90 l.): um "pool" do Qt, uma página por linha de execução, número de linhas ajustável; o README avisa que mais linhas gastam mais memória [lido].
- **O nosso:** cada página por vez; só o desenho do PDF vai para processos à parte (`core/paginas_em_outro_processo.py`), porque o PyMuPDF segura o GIL.
- **Como trazer:** depois que o trabalho pesado estiver nas DLLs, várias linhas no Python podem processar páginas ao mesmo tempo (o `ctypes` solta o GIL durante a chamada) [lido na documentação do ctypes + dedução]. O código do ScanTailor foi feito para rodar em várias linhas, mas convém conferir que nenhuma função usada guarda estado global [dedução].
- **Esforço:** médio. **Risco:** médio: **choca com a regra técnica "uma página por vez na memória"** (`CLAUDE.md`, seção 3). Precisa de decisão do Samuel (por exemplo, 2 a 4 páginas por vez, com teto de memória; o notebook do Kaique tem 32 GB).

### 6.17 Normalizar iluminação e suavizar (2.17)

- **Onde:** `EstimateBackground.cpp` (289 l.) e `normalizeIlluminationGray` (já copiados e compilados na `st_gravura.dll`); `imageproc/SavGolFilter.cpp` (279 l.); filtro de Wiener (`WienerFilter.cpp`, 160 l., coeficiente 0 de fábrica = desligado); suavização morfológica (~80 l. no `OutputGenerator.cpp`) [lido].
- **O nosso:** o Melhorar (divisão pelo fundo estimado, receita nossa) e o Mágico pro.
- **Como trazer:** DLL; a metade já existe. Pode virar opção "igualar a luz como o ScanTailor" e as suavizações no Preto e branco.
- **Esforço:** pequeno. **Risco:** baixo a médio (mexe na aparência).

### 6.18 Edição manual das zonas de gravura (2.18)

- **Onde:** a **regra** está em `OutputGenerator.cpp` (`modifyBinarizationMask`, ~60 l.; `applyFillZones*`, ~120 l.); os **dados** em `core/zones` (`Zone`, `ZoneSet`, `SerializableSpline`, ~150 l.) e `foundation/PropertySet`; a **tela** em `core/interaction/`, `core/zones/*Interaction*`, `ZoneEditorBase`, `PictureZoneEditor`, `FillZoneEditor` (~3.200 l., Qt Widgets) [lido].
- **O nosso:** a aba Marcar já tem retângulo, oval, laço, polígono, pincel, varinha, desfazer e "só neste pedaço". Faltam: copiar, colar e mover zona; apagar vértice; ângulo reto; os tipos "primeiro plano", "fundo" e "preencher com cor".
- **Como trazer:** a regra vai na DLL (a montagem do Misto recebe a lista de polígonos com o tipo de cada um); a tela é nossa, em PySide6, aproveitando o `editor_selecao.py`. Os detalhes da seleção "nível Photoshop" (varinha com tolerância, refinar borda, somar e cruzar seleções) são da **Fase 3**; aqui entra só o que o ScanTailor tem.
- **Esforço:** grande na tela, médio na regra. **Risco:** médio (ver 4.3: onde guardar as zonas).

### 6.19 Unidades cm/mm, perfis de configuração, tema claro/escuro (2.19)

- **Onde:** `Units*` (326 l.), `DefaultParams*` e `DefaultParamsProfileManager` (947 l., perfis "Default", "Source" e os da pessoa, gravados em XML), `*ColorScheme*` (524 l., tema claro, escuro e do sistema). Tudo configuração de janela [lido].
- **O nosso:** tela de Configurações com atalhos editáveis; medidas em cm na aba Bordas; sem perfis e sem tema.
- **Como trazer:** nada em C. Os perfis seriam "receitas" de opções do livro guardadas com nome; o tema é trabalho do agente de layout (Fase 4, que anda em paralelo).
- **Esforço:** pequeno a médio. **Risco:** baixo.

### 6.20 Já no programa, a aperfeiçoar

- **Aba Bordas e margens:** recorte espelhado, proporção travada, cm ao arrastar, A4/A5/Carta, moldura e margem branca, mover conteúdo, qualidade da prévia. Entra junto de 2.4, 2.5 e 2.6: a caixa do conteúdo do ScanTailor (opção), as margens iguais e o alinhamento viram controles desta aba. Bugs da Lista que entram aqui: a aba mostra a folha inteira no corte automático; o "tamanho..." não faz nada antes da imagem chegar; o aviso "encostou no conteúdo".
- **Aba Filtro:** três tipos de preto e branco, limpar pontinhos e o aviso de escuro/apagado. Entra junto de 2.7 e 2.8: os métodos do ScanTailor como opções, a força dos pontinhos de 0,5 a 3,5 e a suavização. O aviso de "escuro/apagado demais" é nosso (o ScanTailor não tem); o bug "aviso aparece em página de outro filtro" entra aqui.

---

## 7. Ordem sugerida, e por quê

1. **DLL comum** (`st_ferramentas`): mesmas pastas de `terceiros/scantailor-advanced/src/` aumentadas, script de compilação, teste "copiado sem mudança". Tudo depende disso. *(pequeno a médio)*
2. **Modo Misto com as zonas (2.18 + base de 2.10/2.11)**, com as opções que a mesma saída usa: **2.7** pontinhos, **2.8** métodos de preto e branco, **2.17** igualar a luz e suavizar, **2.14** preencher, **2.11** segmentação de cor e **2.9** claro no escuro (à mão). Por quê: é o pedido literal do Samuel; depende só do detector que já temos (1.2); não mexe em geometria, então não estraga corte nem zonas aprovadas. Junto, a aba Filtro.
3. **Geometria, na ordem do próprio ScanTailor**, porque cada etapa usa a anterior: **2.3** girar → **2.1** dividir → **2.2** endireitar → **2.13** caixa da página → **2.5** caixa do conteúdo (opção) → **2.4** margens iguais (precisa da caixa de todas as páginas) → **2.6** tamanho final, com a aba Bordas. Antes de começar: decidir onde guardar as zonas (4.3), porque mudar o corte desloca as zonas dos projetos existentes.
4. **2.15** páginas diferentes (precisa dos números do 2.2, 2.5 e 2.4).
5. **2.10** duas camadas, junto do 1.6 (as máscaras já saem do passo 2; falta o PDF).
6. **2.12** desentortar: o maior e mais arriscado; depois da geometria estável, porque muda a página antes da máscara.
7. **2.16** todos os núcleos: depois que o pesado estiver em C, e depois da decisão sobre a regra da memória.
8. **2.19** unidades, perfis e tema: tela; o tema vai para o agente de layout.

---

## 8. Decisões que o Samuel precisa tomar (a gerente leva)

1. **Dividir (2.1):** como o automático do ScanTailor também decide pela proporção, aceitar que a solução é "escolher por livro e por página" (e qual o padrão: "uma página" ou "automático")?
2. **Endireitar e girar (2.2, 2.3):** em que páginas ele viu "funciona mal"? Nas 32 do gabarito o ângulo do nosso bate com o do ScanTailor em 28.
3. **Caixa do conteúdo (2.5):** trazer como opção ("seguir a moldura/o papel") e manter o corte aprovado de fábrica?
4. **Misto:** nome e forma na tela ("Texto em: [filtro]" / "Gravuras em: [filtro]"?), e se os tipos "primeiro plano" e "fundo" do ScanTailor entram com nomes em português comum.
5. **Todos os núcleos (2.16):** abrir exceção à regra "uma página por vez na memória"? Quantas páginas por vez?
6. **Zonas na folha original (4.3):** autorizar mudar o formato do projeto (campos novos) para as zonas sobreviverem a mudanças de corte e ângulo.
7. **Pasta do teste** `D:\programas\EditorImpressao-arquivos\ferramentas\pesquisa-fase2-2026-10-01\` (34 MB: `CMakeLists.txt`, `prova.cpp`, `prova2.cpp`, pasta `build\` e `saida\` com 12 PNG, 11 JPG de comparação e o texto da rodada `prova-saida.txt`): manter (serve de ponto de partida para o implementador) ou apagar?

---

## 9. O que ficou em aberto ou não deu para confirmar

- **DPI das páginas do Graduale, Horas e Marial:** os PDFs dizem 72 DPI (a página tem o tamanho da imagem em pontos). No teste usei **150 DPI** para elas; as funções do ScanTailor reduzem para 150 ou 300 DPI por dentro, então o DPI errado muda o resultado. No programa, o DPI certo é o da prévia/qualidade do projeto.
- **Endireitar:** testei só o `SkewFinder`, sem a limpeza das sombras horizontais do `Task.cpp`; não conferi a olho qual ângulo está certo na Horas 11.
- **Efeito exato de "primeiro plano" e "fundo"** (seção 5.2): conta minha sobre as operações de bits; conferir numa página antes de nomear.
- **Claro no escuro na Horas 11:** não reproduzi a decisão do teste de 24/09.
- **Página dentro da borda preta (2.13):** o gabarito quase não tem borda preta; faltam páginas assim.
- **Montagem completa do Misto e desentortar:** li e vi compilar a biblioteca, mas não montei a página nem desentortei nada.
- **Tempos:** um núcleo, PC dividido com o implementador; servem só como ordem de grandeza. Não rodei o `teste_velocidade.py` (pedido da gerente).
- **"Funciona mal" do girar e do endireitar:** não achei a queixa registrada com páginas; só a frase do plano.

---

## 10. Arquivos e links consultados (01/10/2026)

**Código do ScanTailor Advanced v1.2.1** (cópia local, commit `5eaac1884cdcabb6514bd632114f688631bd8dbc`, de https://github.com/ScanTailor-Advanced/scantailor-advanced), em `D:\programas\EditorImpressao-arquivos\ferramentas\scantailor-advanced-v1.2.1\`:
- `README.md` (funções do Advanced: zonas, Misto, camadas, segmentação, desvio, unidades, perfis, núcleos)
- `src/core/filters/output/`: `OutputGenerator.cpp` (inteiro), `RenderParams.cpp`, `BlackWhiteOptions.cpp`, `ColorCommonOptions.cpp`, `SplittingOptions.h`, `PictureLayerProperty.*`, `PictureZonePropDialog.*`, `OutputImageWithForegroundMask.cpp`, `Task.cpp`, `OptionsWidget.cpp/.ui`
- `src/core/filters/page_split/`: `Task.cpp`, `PageLayoutEstimator.*`, `VertLineFinder.cpp`, `PageLayout.*`, `LayoutType.h`, `OptionsWidget.ui`
- `src/core/filters/deskew/`: `Task.cpp`, `ObliqueFinder.cpp`, `Settings.cpp`, `OptionsWidget.ui`; `src/imageproc/SkewFinder.*`
- `src/core/filters/fix_orientation/`: `Task.cpp`, `ImageTrim.cpp`, `DeskewExternalToolSpike.h`, `OptionsWidget.ui`
- `src/core/filters/select_content/`: `Task.cpp`, `ContentBoxFinder.h`, `PageFinder.cpp`, `Settings.cpp`, `OptionsWidget.ui`
- `src/core/filters/page_layout/`: `Utils.*`, `Task.cpp`, `Settings.*`, `Alignment.*`, `ImageView.cpp`, `ApplyMarginsDialog.ui`, `OptionsWidget.ui`
- `src/core/`: `ProjectPages.cpp`, `BlackOnWhiteEstimator.cpp`, `Despeckle.h`, `DeviationProvider.h`, `WorkerThreadPool.cpp`, `DefaultParams.cpp`, `ApplicationSettings.cpp`, `FilterData.*`, `ImageSettings.*`, `zones/`
- `src/imageproc/`: `Binarize.cpp`, `ImageCombination.cpp`, `ColorSegmenter.*`, `Posterizer.h`, `BWColor.h`, `GrayImage.h`, `BinaryImage.h`
- `src/dewarping/CMakeLists.txt`, `src/math/` (lista)

**Nosso projeto:** `docs/plano/ESTADO-ATUAL.md`, `docs/plano/PLANO-DEFINITIVO.md` (Fase 1, Fase 2, Lista de bugs, Lista de espera, Registro de 01/10), `CLAUDE.md` (seções 3 e 10), `docs/pesquisa/fase1-1.2-scantailor.md`, `docs/plano/TESTE-SCANTAILOR-MISTO.md`, `terceiros/scantailor-advanced/LEIA-ME.md` e `ligacao/`, `compilar_detector_gravura.py`, `core/dividir.py`, `core/endireitar.py`, `core/recortar.py`, `core/folha.py`, `core/selecao.py`, `core/filtros.py`, `core/pipeline.py`, `core/gravura_scantailor.py`, `core/paginas_em_outro_processo.py`, `ui/widgets/editor_selecao.py`, `ui/tela_conferir.py` (só nomes de botões), `gabarito/LEIA-ME.md` e `gabarito/paginas/` (32 páginas).

**Teste feito:** `D:\programas\EditorImpressao-arquivos\ferramentas\pesquisa-fase2-2026-10-01\` (`CMakeLists.txt`, `prova.cpp`: dividir, endireitar, claro no escuro, caixa da página, caixa do conteúdo e pontinhos nas 32 páginas; `prova2.cpp`: preto e branco Otsu/Sauvola, segmentação de cor e redução de cores em 3 páginas; saídas em `saida\`). Compilado com `C:\Program Files\CMake\bin\cmake.exe`, Visual Studio 2022 Build Tools e o Qt 6.11.1 de `ferramentas\qt\`. Nada instalado; nada no `.venv`.

Não consultei a internet nesta pesquisa: tudo veio da cópia local da v1.2.1, a mesma versão do item 1.2.
