# Referência: Internet Archive (PDFs em camadas e a máscara de tinta)

Conferido em 20/10/2026. **O plano manda**: itens [1.1](../itens/1.1.md) (aprovado), [1.4](../itens/1.4.md) e
[1.6](../itens/1.6.md) do [PLANO-DEFINITIVO](../../docs/plano/PLANO-DEFINITIVO.md), e duas linhas da Lista de espera
de 28/09/2026.

## Em uma frase

Alguns livros do acervo vêm do Internet Archive já separados em duas camadas (o papel embaixo, a tinta em cima): o
programa usa isso para "tirar o fundo" (1.1, no programa). E o jeito como o Internet Archive monta a camada de cima, a
**máscara de tinta** feita dentro das linhas de texto, é o modelo do item 1.4, ainda não feito.

## 1. Os PDFs com camadas (item 1.1)

Pesquisa: [`docs/pesquisa/fase1-1.1-camadas-internet-archive.md`](../../docs/pesquisa/fase1-1.1-camadas-internet-archive.md)
(28/09/2026). Código: `core/camadas.py`.

- **Quais livros:** Palatino ([ficha](../livros/palatino.md)), Opus Majus ([ficha](../livros/opusmajus.md)), Rhetorica
  ([ficha](../livros/rhetorica.md)) e Siebmacher ([ficha](../livros/siebmacher.md)). Graduale, Marial, Escola e Boécio
  têm uma imagem por página, sem camadas. O plano cita só os dois primeiros ("o Opus Majus e o Palatino são assim");
  a pesquisa achou os quatro.
- **Como são montados (todas as páginas):** primeiro o **fundo**, a página inteira sem máscara, quase sempre em 1/3
  da resolução; depois a **camada de cima**, a página inteira colorida (JPEG 2000 nos do archive-pdf-tools), recortada
  por uma **máscara de 1 bit (JBIG2)**. Fora da máscara a cor de cima é lixo. Exceções: as 10 primeiras e as 4 últimas
  páginas do Palatino e do Opus Majus têm o fundo inteiro (opção `--hq-pages`); o Siebmacher usa máscara de estêncil
  (`/Mask`), não `SMask`. Rhetorica ("LuraDocument") e Siebmacher ("Samsung Electronics") vêm do programa comercial que
  o Internet Archive usava antes, com o mesmo desenho.
- **Tirar o fundo** = página branca + a cor de cima só onde a máscara deixa. Dá papel branco, letra com a cor original
  (o título vermelho do Opus Majus 3 continua vermelho), e some a mancha do verso (Palatino 10), o carimbo (Opus 3) e a
  mancha d'água (Rhetorica 73).
- **O perigo:** figura cujos tons só existem embaixo (a foto da estátua do Opus Majus 20,
  [página](../paginas-de-teste/opusmajus-020.md); os meios-tons do retrato do Palatino 5,
  [página](../paginas-de-teste/palatino-005.md)). Duas medidas simples do fundo erraram; a zona de figura vem do
  detector de gravura (1.2). Bug de 29/09/2026, decisão do Samuel: "A foto do Opus Majus 20 não pode sair mais clara:
  tem que ficar igual ao original." (consertado em `06f747e`; ver [bugs](../bugs.md)).

### Decisões do Samuel sobre o 1.1 (plano, item 1.1)

- 29/09/2026, a que vale (substituiu o "automático" do mesmo dia): "Página sempre abre em 'Original', sem mexer. Em PDF
  com camadas, 'Tirar o fundo' vira mais uma opção na lista de filtros (ao lado de Original, Preto e branco, Melhorar e
  Mágico pro), com botão para aplicar no livro inteiro. Assim eu decido se tiro ou não, e o Kaique escolhe um filtro
  só, sem mudança escondida. Ao abrir um livro com camadas, o programa pode avisar: 'Este livro tem fundo separado.
  Quer tirar o fundo?'. A caixinha 'Tirar o fundo sozinho' não é mais necessária." E: "eu quero poder escolher tirar o
  fundo sem colocar nenhum filtro." Sobre projetos: "nenhum livro vem marcado, nem novo, nem velho."
- 29/09/2026 (Registro): a pergunta do fundo aparece "uma vez por livro, inclusive nos que ele já tem"; o "Sim" num
  livro antigo "troca só as páginas que estão em 'Original'".
- **Aprovado pelo Samuel em 02/10/2026** (M1: "[x] Aprovado"). Defeitos pequenos que continuam (faixa cinza no Palatino
  10, véu na Rhetorica 38, ferrugem rosada na Pesel 2) foram para o 1.5.

### Ideias da Lista de espera (28/09/2026, literal)

- "Item 1.1: branquear o papel dentro das zonas mantidas usando a cor do papel que o `core/camadas.py` já mede; fundo em
  resolução cheia a partir dos scans **JPEG 2000 originais** do Internet Archive." Quem: agente (item 1.1). Fase
  sugerida: "1.5 / a definir". A pesquisa (seção 9) avisa que isso "não foi conferido e ficaria fora do programa".
- 30/09/2026: "ligar o ScanTailor também no item 1.1" (junto de outras ideias do detector). Fase: "1.5 / a definir".
- 29/09/2026: primeira prévia mais rápida em livro com camadas (o "tirar o fundo" devolver também a folha "como veio").

## 2. A máscara de tinta "como o Internet Archive" (item 1.4)

Item 1.4 do plano: "**Máscara de tinta como o Internet Archive:** achar a tinta só dentro das linhas de texto,
guardando a **cor original** (resolve o texto colorido que o ScanTailor transforma em preto)." **Não começado.**

**Como o Internet Archive faz** (programa aberto `internetarchive/archive-pdf-tools`, **AGPL-3.0**, menos o
`pdfrenderer.py`, Apache-2.0; arquivo `internetarchivepdf/mrc.py`), lido em 28/09 e de novo em 05/10/2026:

1. OCR (Tesseract) marca cada linha de texto (hOCR); pula linha vazia ou com confiança média menor que 20.
2. Dentro de cada linha: Sauvola (janela = DPI/4, k = 0,1), linha normal e invertida, fica a mais limpa.
3. **Soma** um Sauvola da página inteira (k = 0,34; `MIX_THRESHOLD = True`). É por aqui que moldura, gravura e
   pontinhos de foto também sobem.
4. Limpa pontinhos; a camada de cima guarda a cor original onde a máscara diz "tinta"; o fundo fica com as letras
   apagadas, reduzido.

**Duas fontes discordam, e vale a mais nova:**

| [TESTE-SCANTAILOR-MISTO.md](../../docs/plano/TESTE-SCANTAILOR-MISTO.md) (24/09/2026) | Pesquisa de 28/09/2026 (seção 7) e de 05/10/2026 |
|---|---|
| "O segredo é o passo 1: mancha fora das linhas de texto nunca entra na máscara." | No código atual entra, sim, tudo o que o Sauvola da página inteira pega; só a mancha lisa fica embaixo. "Quem quiser 'só texto' na máscara (o item 1.4) tem de usar **só o passo 1**" |
| "nas páginas de gravura (5, 7, 9, 10), o Archive deixou a página inteira na camada de baixo" | O fundo inteiro vem da lista de páginas HQ (as 10 primeiras e as 4 últimas); a 7 e a 10 são só texto |

O documento de 24/09 não foi corrigido: o Registro 29/09/2026 diz "As duas frases para o `TESTE-SCANTAILOR-MISTO.md`
são mostradas a ele antes de mudar"; não achei a resposta do Samuel nas fontes lidas. A pesquisa de 05/10
([`docs/pesquisa/fase2-misto-letras-fora-do-ocr.md`](../../docs/pesquisa/fase2-misto-letras-fora-do-ocr.md), 3.1)
tira a lição: para o Internet Archive, "não entrou na máscara" quer dizer "ficou menos nítido", e não "sumiu"; o nosso
Misto, que pinta o papel de branco, é mais perigoso. "O que vale copiar dele é a **ordem** (linhas primeiro, página
inteira como reforço), não o 'só linhas'."

**Pedido do Samuel ligado ao 1.4** (plano, item 1.4; "Para revisar", rodada 4, 08/10/2026): "mas temos que melhorar o
reconhecimento de tintas, para não sair falhado assim, não precisar usar sempre o reforço." Rodada 5 (09/10/2026,
`rv5-erro-4-tintas`): "Fica no plano; até lá, a força sozinha" (o 1.4 não é adiantado).

## 3. As linhas de texto invisível: a "terceira opinião" do OCR

Os PDFs do Internet Archive trazem o **texto invisível** do OCR deles (modo 3, "não pintar"; fonte `GlyphLessFont`
nos do archive-pdf-tools, `Courier` nos LuraDocument). As **caixas de linha** estão no lugar mesmo onde o texto é
ilegível (Siebmacher, Fraktur). Nas páginas de texto corrido, 84% a 99% da tinta de cima cai dentro delas (pesquisa
de 28/09, seção 6: "o 1.4 tem caixas de linha sem rodar OCR nenhum").

- **Lista de espera, 28/09/2026 (literal):** "Itens 1.3 e 1.4: vetar caixa de linha do OCR dentro da gravura detectada
  pelo 1.2 (resolve Horas 13 e 47); rodar o docTR em pedaços da página, para tabela grande (Opus Majus 256); **usar as
  linhas de texto invisível dos PDFs do Internet Archive como terceira opinião**." Quem: agente (item 1.3). Fase
  sugerida: "1.4 / 1.5".
- Por que importa: a comparação automática docTR + Kraken (item [1.3](../itens/1.3.md)) não pega 4 erros em que os dois
  erram quase igual (Horas 27, Graduale 221 a 223); "Pegar esses erros pede informação de fora (tinta da página ou
  terceira opinião, já na Lista de espera)" (Registro 01/10/2026).
- Cuidado: só existe nos livros do Internet Archive, e "foi feito por um OCR, não é gabarito humano" (pesquisa, 6).
  Na pesquisa do 1.3 ([`docs/pesquisa/fase1-1.3-ocr-para-achar-texto.md`](../../docs/pesquisa/fase1-1.3-ocr-para-achar-texto.md))
  ela aparece como "R0", referência de graça (só Palatino e Opus Majus).

## 4. O OCR no plano (para situar)

- **Mudou em 24/09/2026** ([ESTADO-ATUAL §2](../../docs/plano/ESTADO-ATUAL.md)): o OCR "volta ao plano na **Fase 1**,
  só para *achar onde está o texto* (fazer a máscara de tinta como o Internet Archive), não para transcrever. A
  transcrição fica na Fase 7."
- [`docs/plano/OCR-PESQUISA.md`](../../docs/plano/OCR-PESQUISA.md) (24/09/2026): benchmark do Tesseract em 8 páginas
  (Escola 99,4%, Pesel 99,6%, Rhetorica 88,0%, Siebmacher 76,0%, Horas 81,8%, Boécio 56,1%, Palatino e Graduale
  "inutilizável"); "O OCR deve entrar **depois** do corte de bordas"; e a decisão pendente da Fase 7 (opções a, b, c
  sobre IA corrigindo texto; item [7.1](../itens/7.1.md)).
- O que existe hoje: item 1.3 aprovado em 02/10/2026 (docTR `fast_base` + Kraken de fábrica, Tesseract instalado e
  desligado). Pesquisas em `docs/pesquisa/`: `fase1-1.3-ocr-para-achar-texto.md`, `fase1-1.3-kraken-windows.md`,
  `fase1-ocr-manuscrito-no-windows.md`, `treinar-ocr-e-detector.md`, `fase2-misto-letras-fora-do-ocr.md`.

## 5. Licenças

- `archive-pdf-tools`: AGPL-3.0 (cabe na decisão de 17/09/2026, [CLAUDE.md §3](../../CLAUDE.md)). O programa **não usa**
  o código dele: só reconhece o resultado nos PDFs; o 1.4 copiaria a ideia.
- PyMuPDF (que lê as camadas): AGPL; a ressalva antiga "deixa de existir" com a decisão de 17/09 (CLAUDE.md §3).
