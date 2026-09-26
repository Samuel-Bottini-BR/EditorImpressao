# Pasta `gabarito/`: as páginas fixas do antes/depois

Montada em **25/09/2026** (item 0.3 do Plano Definitivo).

## O que é

São as páginas de teste que todo item do plano usa na página de antes/depois
(item 0.4). São sempre as mesmas, para que um resultado possa ser comparado com
o outro, de um dia para o outro.

## Fora do git

A pasta tem cerca de 450 MB (só a cópia do teste do ScanTailor tem 329 MB).
Por isso ela fica fora do git: só entram no repositório este `LEIA-ME.md` e a
`lista.json`. O resto existe só neste PC. Se a pasta se perder, dá para montar
de novo a partir dos originais (ver "Como foi montada").

## Os originais são somente leitura

Aqui só tem **cópia**. Os PDFs do acervo, a pasta `D:\programas\Scan Tailor\`,
a pasta `plano-24-09-2026\` e a Área de Trabalho do Samuel nunca são
alterados, movidos ou apagados.

## Numeração

**Número da página no PDF, começando em 1.** Não é o número impresso na folha.
Exemplo: em "Na escola de Jesus", a folha com "37" impresso no pé é a página 35
do PDF.

Nome dos arquivos: `<livro>_p<NNN>`. Exemplo: `palatino_p005` é a página 5 do
PDF do Palatino.

## O que tem em cada lugar

| Onde | O que é |
|---|---|
| `paginas/` | Para cada página, um `.pdf` e um `.png`. O `.pdf` é a página copiada do PDF original **sem redesenhar**: as camadas e as imagens são as originais, byte a byte (a Fase 1.1 precisa das camadas). O `.png` é para olhar, na resolução do scan (no máximo 400 DPI). |
| `camscanner/` | As 6 fotos do CamScanner feitas pelo Kaique (3 pares original / Mágico Pro): Horas p. 26 (NOVEMBRE), Horas p. 27 (DECEMBRE) e Escola impressa "37" = p. 35 do PDF (ver Pendências). |
| `scantailor-24-09/` | Cópia intacta do teste do ScanTailor de 24/09: páginas de entrada, `out/` (saída no modo Misto) e `comparacoes/`. |
| `opusmajus-candidatas.png` | A p. 11 do Opus Majus e as 4 candidatas, lado a lado, para o Samuel aprovar. |
| `velocidade/` | É do teste de velocidade (item 0.5), feita por outro agente. **Não mexer.** |
| `lista.json` | A lista que os scripts leem (ver abaixo). |

## Como a `lista.json` funciona

- **`paginas`**: uma entrada por página, pelo nome (`palatino_p005`). Diz de
  que livro ela veio (`livro`, caminho completo do original), o número no PDF
  (`pagina`), onde estão o `pdf` e o `png` (caminhos relativos a esta pasta),
  o DPI do PNG, para que a página serve (`para_que`), de onde ela veio
  (`origem`) e como foi conferida.
- **`itens`**: quais páginas cada item do plano usa (`fase1`, `2.2`, `2.4`,
  `2.6`, `fase3`, `6.1` a `6.7`). O script de antes/depois pega a lista do
  item e abre essas páginas. `nomes_dos_itens` diz o nome de cada item.
- **`camscanner`**: cada par de fotos e a página do gabarito que corresponde a
  ele (`pagina_gabarito`).
- **`scantailor_24_09`**: para cada página do teste do ScanTailor, a entrada, a
  saída e a comparação, quando existem.
- **`pendencias`**: dúvidas que o Samuel precisa resolver.

O que foi acrescentado à estrutura combinada, e por quê:

- `a_confirmar`: `true` quando o Samuel ainda precisa confirmar a página antes
  de ela virar gabarito fixo.
- `bate_com_a_origem`: `false` quando a página pedida não é a do print ou da
  foto de onde ela veio. Nesse caso, `observacao` diz qual página parece certa.
- `dpi_scan`, `png_px`, `camadas` e `imagens`: o que o PDF tem dentro (uma
  imagem só, ou fundo + camada de cima com máscara, e em que resolução). Isso
  serve para a Fase 1.1.

Acrescentado em 25/09/2026 pelo item 0.4 (a página de antes/depois):

- `detalhe` (em cada página, logo depois do `para_que`): o ponto que o
  `para_que` manda olhar, que a página de conferência mostra já ampliado. São
  quatro números de 0 a 1, `[x0, y0, x1, y1]`: a fração da largura e da altura
  da página, a partir do canto de cima à esquerda (`[0.5, 0, 1, 0.2]` = a
  metade direita da faixa de cima). Foi escolhido **olhando cada página**: a
  mancha, a letra colorida, a gravura, a borda, a margem. Para mudar, basta
  trocar os números; o `conferencia.py` recusa valor fora de 0 a 1.
- `recorte_da_pagina` (em cada entrada de `camscanner`): onde está a página
  dentro de cada captura de tela do celular, em pixels da captura,
  `[x0, y0, x1, y1]` (x1 e y1 são o primeiro pixel já fora da página), uma
  para a foto `original` e outra para a `magico_pro`. As fotos são capturas
  da tela (576 x 1280), com o aplicativo em volta; a página ocupa uns 520
  pixels no meio. Achado pela diferença para o fundo escuro do aplicativo e
  conferido olhando os quatro cantos ampliados. Serve para comparar a cor e o
  branco do papel, não o detalhe.

## Como usar o `conferencia.py` (item 0.4)

É o script que gera a página de antes/depois de qualquer item (regra 4 do
plano). Da pasta do projeto:

```
.venv\Scripts\python.exe conferencia.py 6.7
.venv\Scripts\python.exe conferencia.py 6.7 --filtro "Preto e branco"
.venv\Scripts\python.exe conferencia.py fase1 --funcao core.modulo:funcao
.venv\Scripts\python.exe conferencia.py 6.2 --pasta-depois PASTA
.venv\Scripts\python.exe conferencia.py 6.7 --comparar-com relatorios\conferir\6.7-AAAA-MM-DD-HHMM
.venv\Scripts\python.exe conferencia.py 6.7 --pasta-depois relatorios\conferir\6.7-AAAA-MM-DD-HHMM --opiniao opiniao.txt
.venv\Scripts\python.exe conferencia.py 6.7 --paginas horas_p026,escola_p035
```

- O item é uma chave de `itens` (`fase1`, `2.2`, `6.7`...). Item que não
  existe: o script diz quais existem.
- **De onde vem o "depois"**: sem opção, é o programa de hoje (o mesmo caminho
  do botão "Confirmar e processar", a partir do PDF de uma página, com o que a
  análise automática decidir), no filtro Mágico pro, o mais parecido com o
  CamScanner. `--funcao` roda uma função sozinha: ela recebe o caminho do PDF
  da página e a imagem original (BGR, do OpenCV) e devolve a imagem pronta.
  `--pasta-depois` usa imagens prontas, `<id da página>.png` (ou .jpg/.tif), ou
  a pasta de uma conferência já feita.
- `--comparar-com` acrescenta a coluna "Rodada anterior" (as imagens de outra
  conferência): serve para ver o que uma mudança de código mudou.
- `--opiniao` põe o texto do verificador; só com ele a página diz PRONTO PARA
  CONFERIR. Para não processar tudo de novo, use junto `--pasta-depois` com a
  pasta da própria conferência.

A página sai em `relatorios\conferir\<item>-<AAAA-MM-DD-HHMM>\` (.html, .pdf e
.md), com `resultado\` (o "depois" de cada página em tamanho cheio), `paineis\`
e `dados.json`. As colunas: Original (o PNG daqui), Rodada anterior, Resultado,
e as referências quando existem para a página: CamScanner Mágico Pro (a foto
recortada por `recorte_da_pagina`) e ScanTailor 24/09 (a saída de
`scantailor-24-09/out/`). O detalhe de cada coluna é achado alinhando a imagem
com o original (o programa corta e endireita a página, e as referências têm
outro enquadramento); quando o alinhamento não dá certeza, a página avisa.
Nada nesta pasta é gravado pelo script: ele só lê.

## De onde veio cada página

- **"Vamos recapitular..." (12/09/2026)**, documento do Samuel em
  `explicacoes-do-samuel\`: Palatino 5, 7, 9, 10, 57 e 66; Graduale 221, 222 e
  223; Horas 11, 13, 14 e 47; Escola 7. Casos que estavam em dúvida e foram
  decididos pelo Samuel em 25/09: Palatino "76" = p. 67, Siebmacher "7" = p. 9,
  Marial = p. 7 (ver Pendências).
- **Teste do ScanTailor de 24/09**: Palatino 5 e 9, Escola 7, Horas 11, 13 e
  47, Siebmacher 7, Rhetorica 18 e 73.
- **Fotos do CamScanner (24/09)**: Horas 26 e 27, Escola 35 (impressa "37").
- **TESTE 1 do Boécio (16/09)**: Boécio 3, 7, 8 e 22. O documento só tem
  prints, sem o número da página: as páginas foram achadas comparando os
  prints com o PDF.
- **Opus Majus** (`opusmajustransla01baco.pdf`, Área de Trabalho): a p. 11,
  pedida pelo Samuel, e 4 escolhidas olhando o livro inteiro (3, 20, 165 e
  256), aprovadas pelo Samuel em 25/09.

## Como foi conferida

- **Numeração:** cada print do "Vamos recapitular" e do TESTE 1, e cada foto
  do CamScanner, foi comparado com as páginas do PDF e depois olhado. Os PNGs
  do Palatino 5 e 9, da Rhetorica 18 e 73 e do Siebmacher 7 são idênticos,
  byte a byte, aos de entrada do teste do ScanTailor.
- **PDFs:** cada página extraída tem o mesmo número de imagens da original, os
  mesmos bytes de cada imagem e máscara, o mesmo tamanho e o mesmo desenho.
- **PNGs:** todos foram abertos e olhados: página certa, sem estar em branco,
  cortada ou girada.

## Pendências — todas resolvidas em 25/09 (detalhes em `lista.json`, seção `pendencias`)

1. **Palatino "76" — resolvida:** o print do "Vamos recapitular" é a p. 67 do
   PDF. O Samuel confirmou: o item 6.2 usa 66 e 67, e a p. 76 saiu do
   gabarito.
2. **Escola "37" — resolvida em 25/09:** as fotos do CamScanner são a p. 35
   do PDF (37 é o número impresso). Os itens usam a `escola_p035`; a extração
   da p. 37 do PDF (impresso 39) foi apagada, porque nada a pedia e o nome
   confundia com as fotos.
3. **Siebmacher "7" — resolvida:** o print do "Vamos recapitular" é a p. 9.
   O Samuel escolheu só a 9 para o item 2.6. A p. 7 continua no gabarito como
   página do teste do ScanTailor de 24/09.
4. **Marial — resolvida:** o Samuel escolheu só a p. 7 (a do "Vamos
   recapitular") para o item 6.1. A 862, que vinha da lista `para_comparar` de
   18/07, saiu do gabarito. O `detalhe` da p. 7 aponta para a faixa em volta da
   assinatura "O Pref. Fr. Francisco de Gouuea", onde o texto do verso aparece
   invertido.
5. **Opus Majus — resolvida:** o Samuel aprovou as 4 (3, 20, 165 e 256).

## Como foi montada

- **PDF de uma página:** `novo.insert_pdf(original, from_page=i, to_page=i)`
  (PyMuPDF), sem redesenhar.
- **PNG:** a página desenhada com o DPI da maior imagem dela: pixels divididos
  pelas polegadas do lugar onde a imagem é desenhada, com teto de 400. No
  Graduale e no Boécio a imagem é maior que a página; dividir pela página daria
  mais DPI do que o scan tem. Horas, Graduale e Marial foram escaneados a
  72 DPI, então os PNGs deles são pequenos de propósito: essa é a resolução
  real.
- **Cópias** (`camscanner/` e `scantailor-24-09/`): conferidas arquivo por
  arquivo (mesmo número de arquivos, mesmos bytes, mesmo conteúdo).
