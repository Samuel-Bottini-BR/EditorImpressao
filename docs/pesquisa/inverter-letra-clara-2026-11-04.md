# Virar letra clara em fundo escuro para letra preta em papel branco (D-190)

Pesquisa de 04/11/2026, agente pesquisador. Só pesquisa: nenhuma linha do
programa mudou.

**Pergunta do Samuel (04/11/2026), palavras exatas:** "sobre essa questão das
letras brancas em fundo escuro, a gente tem que ter uma maneira de inverter isso
né de forma perfeita, agora veja como o scantailor faz isso, eu acho que faz."

**Decisões tocadas:** D-177 (caixinha "Letra clara em fundo escuro", por página,
à mão, desligada de fábrica; a página sai com as cores do livro, letra clara em
fundo escuro, só limpa) e D-190 (Lista de espera, 21/10, `29-slide`: "o que
gostariamos de fazer é selecionar a cor branca das letras e transformar em preto
e dai então transformar a pagina em branco, porque quando imprimir a impressora
vai imprimir todo esse preto"). Regra D-605: o que vier para a D-190 não pode
mudar o que a caixinha da D-177 faz hoje.

Marcas: **[lido]** = visto no código ou na documentação; **[medido]** = rodei
aqui; **[dedução]** = conclusão minha.

---

## Resposta curta

1. **O ScanTailor não tem.** Nenhum dos três (original, Advanced, Deviant) sabe
   devolver a página como letra preta em papel branco. O Advanced tem a mesma
   coisa que nós já temos (D-177): uma caixinha por página que trata a página
   invertida e no fim **desinverte**, de modo que ela sai como entrou, letra
   clara em fundo escuro, só limpa. O original e o Deviant nem isso têm. Também
   não existe "inverter" como tipo de área no Advanced.
2. **Quem faz de verdade é a Leptonica** (a biblioteca de imagem que vem dentro
   do Tesseract, licença BSD): a função `pixAutoPhotoinvert` acha sozinha as
   áreas de letra clara em fundo escuro e vira **só elas** para letra preta em
   papel branco, deixando o resto da página como está. O Tesseract, o OCRmyPDF
   e o archive-pdf-tools só invertem por dentro, para ler o texto; a imagem que
   sai continua igual.
3. **Recomendação:** uma opção nova, separada da caixinha de hoje, só no Preto e
   branco. O caminho mais seguro é o do próprio ScanTailor **sem a última
   inversão** (página inteira, à mão). O caminho mais completo é a Leptonica
   (acha as áreas sozinha), mas ela também vira foto escura em negativo, então
   precisa proteger as gravuras.

---

## 1. O ScanTailor tem um jeito de inverter? Não.

### 1.1 ScanTailor Advanced (v1.2.1, commit `5eaac18`, 24/05/2026) [lido]

Código: cópia local em `terceiros/scantailor-advanced/` e o repositório
https://github.com/ScanTailor-Advanced/scantailor-advanced (clonado em
04/11/2026, mesmo commit).

- **Na tela:** caixinha **"Black on white mode"** ("modo preto no branco"), na
  etapa de saída (Output), uma por página
  (`src/core/filters/output/OptionsWidget.ui`, linhas 1445-1450). A dica diz
  que ela serve "para corrigir os algoritmos" quando a página tem conteúdo
  claro em fundo escuro. Tem também "Apply To..." para copiar a escolha para
  outras páginas (`OptionsWidget.cpp`, linhas 1036-1043).
- **Automático:** nas Configurações, grupo **"White on black detection"**, com
  "Auto detect light content on dark background" e "Use auto detection at the
  output stage" (`src/app/SettingsDialog.ui`, linhas 296-316). **Os dois vêm
  ligados de fábrica** (`src/core/ApplicationSettings.cpp`, linhas 16-17). Se o
  usuário mexer na caixinha, a escolha dele vale sobre a automática
  (`OptionsWidget.cpp`, linhas 1020-1024; `OutputGenerator.cpp`, linhas
  1229-1239).
- **Como a detecção decide:** `src/core/BlackOnWhiteEstimator.cpp`, linhas
  70-93: preto e branco por Otsu dentro da área de corte; se mais da metade
  sair preto, a página é "claro no escuro". Se der dúvida, refaz a conta a 150
  DPI, limpa pontinhos e olha só a área com conteúdo (linhas 21-68). É sempre a
  **página inteira**, nunca uma área.
- **O que ele faz com a página marcada:** `OutputGenerator.cpp`
  (`terceiros/scantailor-advanced/referencia/OutputGenerator.cpp`):
  - inverte a página na entrada (linhas 1242-1250, `initFilterData`);
  - processa como página comum (preto e branco, pontinhos, cores);
  - **inverte de novo no fim**: linhas 1344-1345 (preto e branco), 1370-1371
    (letras com cor), 1497-1498 (cor e Misto), e as mesmas três no caminho com
    desentortar (linhas 1722-1723, 1738-1739, 1858-1859).
  - a margem de fora também é trocada para ficar da cor certa depois da
    segunda inversão (linhas 1485-1488: "branco" vira preto antes de inverter).
  - Resultado: **a página sai como entrou, letra clara em fundo escuro**, só que
    limpa. É exatamente o que o nosso `core/claro_no_escuro.py` copiou (D-177).
  - O README do Advanced descreve assim: "permite processar imagens com conteúdo
    claro em fundo escuro corretamente, corrigindo os algoritmos automáticos"
    (README.md, linhas 415-421). Não fala em virar a página.
- **Áreas (zonas):** as zonas de figura têm só "Subtract from all layers",
  "Add to auto layer", "Subtract from auto layer", "Add to foreground", "Add to
  background" (`PictureZonePropDialog.ui`, linhas 20-48;
  `PictureLayerProperty.h`, linha 19). As zonas de preenchimento só pintam a
  área de uma cor escolhida ("Pick color", `FillZoneEditor.cpp`, linha 162),
  o que cobriria as letras também. **Não existe zona "inverter".**

**Detalhe que interessa:** no preto e branco, a imagem `dst` logo antes da linha
1344 (`if (!m_blackOnWhite) dst.invert();`) **já é letra preta em papel branco**.
O ScanTailor calcula o que o Samuel quer e depois desfaz. Não há opção na tela
para pular essa última inversão [lido; a conclusão de que `dst` é preto no
branco ali é dedução direta do código: a página entrou invertida e foi
binarizada como página comum].

### 1.2 ScanTailor original (scantailor/scantailor, último commit `e881b30`, 28/11/2020) [lido]

Não tem nada para letra clara em fundo escuro: nenhuma ocorrência de
"BlackOnWhite"/"white on black" no código nem na tela; os únicos "invert" são
internos (`imageproc/BinaryImage.cpp`, `PolygonRasterizer.cpp`). Página assim é
tratada como página comum (o Otsu decide e o fundo escuro sai preto).

### 1.3 ScanTailor Deviant (ImageProcessing-ElectronicPublications/scantailor-deviant, commit `031878a`, 15/10/2025) [lido]

Também não tem. A tela de saída (`src/core/filters/output/ui/OutputOptionsWidget.ui`)
só tem Preto e branco / Cor / Misto, limiares e pontinhos. O único "inverted"
na tela é na exportação de camadas: "Binarized and inverted background"
(`src/app/ui/ExportDialog.ui`, linha 97), que é uma máscara para DjVu, não a
página. Licença GPL-3 (arquivo `COPYING`).

---

## 2. Como outros programas fazem

| O que é | Faz o quê com letra clara em fundo escuro | Muda a imagem que sai? | Licença | Roda aqui? | Notebook do Kaique? |
|---|---|---|---|---|---|
| **Leptonica `pixAutoPhotoinvert`** | Acha as áreas claro-no-escuro e vira **só elas** para preto no branco | **Sim** (devolve a página em preto e branco 1 bit) | BSD 2 cláusulas (pode usar, só manter o aviso de copyright) | Sim: `C:\Program Files\Tesseract-OCR\libleptonica-6.dll` (Leptonica 1.84.1) já tem a função; chamei por `ctypes` [medido] | Sim [dedução]: o instalador já leva a pasta `tesseract\`, que traz essa DLL |
| ScanTailor Advanced | Inverte, limpa e desinverte (página inteira) | Não vira: sai claro no escuro | GPL-3 | Já está no programa (D-177) | Sim |
| Tesseract 5 (`invert_threshold`) | Lê de novo a **linha** invertida se a confiança for baixa | Não: só o texto lido | Apache-2.0 | Sim (v5.4.0 instalado) | Sim |
| archive-pdf-tools (`create_hocr_mask`) | Em cada **linha** do OCR, testa normal e invertida e fica com a mais limpa | Só a máscara de letra; a letra guarda a cor dela (continua branca) | AGPL-3.0 | Sim | Sim |
| OCRmyPDF | Não tem opção própria; depende do Tesseract | Não | MPL-2.0 | Sim | Sim |
| unpaper | Não tem nada (nenhum "invert"/"negate" no código nem no manual) | Não | GPL-2.0 | Precisa compilar | — |

Detalhes, com fonte:

- **Leptonica** (https://github.com/DanBloomberg/leptonica, commit `5914a43`,
  04/11/2026), `src/pageseg.c`, linhas 2905-3000 [lido]:
  1. passa a página para preto e branco com limiar fixo (128 se não disser
     outro, linha 2943);
  2. usa a máscara de "meio-tom" (`pixGenerateHalftoneMask`, a mesma que acha
     foto na página) para achar blocos grandes e escuros, tira ruído
     (`o15.15 + c25.25`) e fecha buracos (linhas 2953-2955);
  3. só aceita o bloco se **pelo menos 60% dele for preto** (linhas 2974-2988);
  4. inverte a página e copia o invertido **só dentro desses blocos** (linhas
     2995-2997).
  Entrou na versão 1.79 "para o tesseract, para inverter sozinho áreas de texto
  onde o fundo é preto e o texto é branco" (`version-notes.html`, linhas
  351-352). Tem teste de regressão próprio (`prog/pageseg_reg.c`, linhas
  205-230). Hoje o Tesseract **não** chama essa função (procurei no `src/`): ela
  ficou na Leptonica para quem quiser usar.
- **Tesseract** (https://github.com/tesseract-ocr/tesseract, commit `c21194d`):
  parâmetro `invert_threshold` = 0,7 (`src/ccmain/tesseractclass.cpp`, linhas
  71-73); em `src/lstm/lstmrecognizer.cpp`, linhas 379-405, se a confiança média
  da linha ficar abaixo disso, lê a linha invertida e fica com a melhor. Só
  muda o texto lido.
- **archive-pdf-tools** (https://github.com/internetarchive/archive-pdf-tools,
  commit `68c7a21`): `internetarchivepdf/mrc.py`, linhas 223-264 (já estava
  resumido em `fase1-1.1-camadas-internet-archive.md`, linha 74). A máscara diz
  onde está a letra; a cor da letra vem da imagem original, então letra branca
  continua branca.
- **OCRmyPDF** (https://github.com/ocrmypdf/OCRmyPDF, commit `b457e9e`): nenhuma
  opção de inverter no código nem na documentação (procurei "invert" e
  "negat" em `src/` e `docs/`).
- **unpaper** (https://github.com/unpaper/unpaper, commit `5bcef8a`): nenhuma
  opção de inverter (procurei no código e em `doc/`).

### 2.1 Teste rápido da Leptonica, nesta máquina [medido]

Script de pesquisa (fora do projeto):
`C:\Users\fotog\AppData\Local\Temp\claude\195a7ef9582f81cd\e4fd3df2-ffc2-4ff8-9d6b-c5c2f4b2d0ca\scratchpad\scripts\teste_inverter.py`
e `teste_foto_escura.py`; imagens em
`C:\Users\fotog\AppData\Local\Temp\claude\195a7ef9582f81cd\e4fd3df2-ffc2-4ff8-9d6b-c5c2f4b2d0ca\scratchpad\teste-inverter-saida\`
(painel em `painel.png` e `foto_painel.png`). **Páginas sintéticas**, feitas
por mim: não é página de livro.

| Página de teste | Tinta preta antes | Leptonica | Inverter a página inteira |
|---|---|---|---|
| Slide inteiro: fundo escuro, 25 linhas de letra clara | 94% | **6%**, letra preta inteira em papel branco | 6% (igual) |
| Página branca com texto preto em cima e uma **faixa** escura com letra clara embaixo | 32% | **4%**: a faixa virou preto no branco e o texto de cima ficou igual | **68%**: o papel branco virou preto |
| Página branca com uma **foto escura** (sem letra dentro) | 92% dentro da foto | **8%: a foto virou negativo** | — |

O que isso mostra:

- Para slide inteiro, os dois caminhos dão o mesmo resultado.
- Para página com só uma parte escura, inverter tudo estraga; a Leptonica
  acerta.
- **A Leptonica não sabe o que é foto**: foto escura também é invertida. No
  nosso programa isso se resolve com a marcação de gravura que já existe
  (a área marcada como gravura não seria invertida) [dedução, não testado].

---

## 3. Recomendação

**Em uma frase:** uma opção nova por página, "Letra preta em papel branco",
**só no Preto e branco**, ao lado da caixinha de hoje e sem mudar o que ela faz.

Os três caminhos, do mais simples ao mais completo:

**A. O caminho do ScanTailor sem a última inversão (página inteira, à mão).**
O programa já inverte a página na entrada e processa (D-177); para a opção
nova, basta não inverter de novo no fim. É o mesmo cálculo do ScanTailor
(`OutputGenerator.cpp`, antes da linha 1344).
- Bom para: slide inteiro, capa toda escura.
- Risco: página com papel branco em volta do slide ou só uma faixa escura sai
  com o papel branco virado preto (teste: 68% de preto). Foto no slide vira
  negativo, a não ser que a gravura marcada fique de fora. O próprio
  `core/claro_no_escuro.py` (linhas 37-40) já avisa que "inverter só na entrada"
  é arriscado **para a caixinha de hoje**; por isso tem que ser opção nova,
  separada (D-605).
- Esforço: pequeno. Licença: a do ScanTailor (GPL-3), que já está no programa.

**B. Leptonica `pixAutoPhotoinvert` (acha as áreas sozinha).**
- Bom para: slide inteiro e página com faixa ou quadro escuro; não precisa
  marcar área.
- Risco: foto escura vira negativo (medido); precisa tirar da conta a gravura
  marcada. O limiar dela é fixo (128): num slide de fundo cinza-médio pode não
  achar a área [dedução]. Sai só preto e branco (1 bit), não serve para
  Melhorar nem Mágico pro. A detecção automática foi recusada para a caixinha
  da D-177 (P9: "que o Kaique marca à mão"); aqui a opção continuaria marcada à
  mão, e a Leptonica só diria **onde** inverter dentro da página. Isso é escolha
  do Samuel.
- Esforço: pequeno a médio (a DLL já vem com o Tesseract do instalador).
  Licença BSD-2: só manter o aviso de copyright.

**C. Área marcada à mão ("Só neste pedaço") com o caminho A dentro dela.**
- Bom para: página com faixa escura, sem nada automático.
- Risco: dá trabalho ao Kaique em livro com muitas páginas assim.

**Minha sugestão:** começar pelo **A**, porque é o próprio ScanTailor, resolve o
caso do slide (`29-slide`) e não toca no que já foi aprovado; deixar **B** como
passo seguinte para páginas com só uma parte escura, sempre com a gravura
protegida.

**Em cor (Melhorar, Mágico pro):** nenhum programa consagrado que achei vira
letra clara em escura nas cores. Inverter a cor dá as cores trocadas (azul vira
amarelo). Por isso a sugestão é só no Preto e branco [dedução].

---

## 4. O que ficou em aberto

- Não testei em página de livro de verdade: não achei no projeto a página
  "O meio ambiente hoje" do `29-slide` (só as respostas da Central). O teste
  foi com páginas sintéticas.
- Não confirmei que a pasta `tesseract\` do instalador leva a
  `libleptonica-6.dll` com essa função no notebook do Kaique; nesta máquina
  leva (Leptonica 1.84.1).
- O limiar fixo da Leptonica (128) em slide de fundo cinza ou colorido não foi
  medido.
- O "71% da folha em preto" citado pela gerente não foi medido por mim.

## 5. Links e códigos consultados (04/11/2026)

- ScanTailor Advanced v1.2.1: https://github.com/ScanTailor-Advanced/scantailor-advanced
  (commit `5eaac1884cdcabb6514bd632114f688631bd8dbc`) e cópia local
  `terceiros/scantailor-advanced/`.
- ScanTailor original: https://github.com/scantailor/scantailor (commit `e881b30`).
- ScanTailor Deviant: https://github.com/ImageProcessing-ElectronicPublications/scantailor-deviant
  (commit `031878a`); espelho https://gitea.com/ImageProcessing-ElectronicPublications/scantailor-deviant
- Leptonica: https://github.com/DanBloomberg/leptonica (commit `5914a43`),
  `src/pageseg.c`, `leptonica-license.txt`, `version-notes.html`.
- Tesseract: https://github.com/tesseract-ocr/tesseract (commit `c21194d`).
- archive-pdf-tools: https://github.com/internetarchive/archive-pdf-tools (commit `68c7a21`).
- OCRmyPDF: https://github.com/ocrmypdf/OCRmyPDF (commit `b457e9e`).
- unpaper: https://github.com/unpaper/unpaper (commit `5bcef8a`).
- No projeto: `docs/pesquisa/fase2-mapa-scantailor.md` §6.9,
  `memoria/itens/2.9.md`, `core/claro_no_escuro.py`, `core/pipeline.py`
  (linhas 2919-2934), `docs/plano/DECISOES.md` (D-177, D-190).
