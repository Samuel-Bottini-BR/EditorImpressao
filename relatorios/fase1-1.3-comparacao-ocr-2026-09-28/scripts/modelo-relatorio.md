# Item 1.3: qual OCR acha melhor onde está o texto

**28/09/2026 · implementador · só medição: o programa não mudou.**

> **Atenção, Samuel:**
> 1. As zonas que dizem "aqui é texto" e "aqui não pode ter linha" foram desenhadas por mim, olhando cada página. **Você ainda precisa conferir essas zonas** (seção 9, 22 imagens). Até lá, todos os números deste relatório são provisórios.
> 2. A escolha dos 2 OCRs que ficam é sua. Abaixo está a minha recomendação, não uma decisão.

## 1. Em poucas palavras

1. **Nenhum OCR sozinho cumpre as duas metas em todas as páginas.** As metas são: achar 98% ou mais da tinta das letras, e cobrir 1% ou menos da tinta de gravura, iluminura, moldura e foto.
2. **O Kraken é o único que não pisa em figura em nenhuma das 7 páginas obrigatórias.** A pior delas ficou em 0,9%. Também é o melhor no manuscrito: no Graduale não pôs nenhuma caixa em cima da música. Tem três defeitos:
   - toma a moldura ornamental do Siebmacher 9 como se fosse texto (83%);
   - perde a tabela do Opus 256 (só 33% achado);
   - é lento: 12 s por página neste PC.
3. **O docTR (modelo `fast_base`, pelo OnnxTR) é o melhor dos rápidos:**
   - acha em média 98,7% da tinta de texto;
   - leva 1 s por página e roda no Python 3.14 do programa;
   - é o único, fora as linhas do Internet Archive, que não toma a moldura do Siebmacher (0,04%);
   - falha em duas obrigatórias: na Horas 13 as caixas encostam na moldura dourada, e no Palatino 5 duas caixinhas caem na borda do retrato (1,7%).
4. **O Tesseract não serve para isto, ao contrário do que a pesquisa apostava:**
   - não acha nenhuma linha no título da Horas 11 e quase nada no Graduale;
   - toma a moldura do Siebmacher inteira como texto (99%);
   - pisa na borda do retrato e nas molduras do Palatino (4% a 6%);
   - o filtro de confiança do Internet Archive quase não muda nada.
5. **Recomendação, para você decidir: Kraken + docTR `fast_base`.** Os dois erram em lugares diferentes. Nas zonas onde os dois concordam, **nenhuma das 22 páginas passou de 1% de figura**. O custo é o Kraken: 1,2 GB a mais no instalador (um Python só dele, sem WSL) e uns 20 a 30 s por página no notebook do Kaique (estimativa). **Alternativa mais leve:** docTR `fast_base` + PP-OCRv6 pequeno (pelo RapidOCR). Os dois são rápidos e rodam no Python do programa, mas erram parecido: os dois pisam no emblema do Opus 3 e na moldura da Horas 13.

## 2. Como foi medido

- **Páginas:** as 19 da pesquisa, que são as 16 do item `fase1` da `gabarito/lista.json` mais Rhetorica 18, Siebmacher 9 e Palatino 57. Para ver o manuscrito, entraram mais **Graduale 221, 222 e 223**. As Horas 11, 13, 26, 27 e 47 já estavam entre as 19.
- **Imagem:** o PDF de uma página de `gabarito/paginas/`, desenhado na resolução do scan, com teto de 300 DPI. As Horas e o Graduale têm scan pequeno (1024 e 961 px de largura) e ficaram assim. **Não passei pelo corte nem pelo endireitamento do programa** (ver Ressalvas). Todos os OCRs receberam a mesma imagem.
- **Gabarito:** para cada página, retângulos "tem de ser texto" e "não pode ter linha" (gravura, iluminura, moldura, foto, carimbo). Há também zonas "neutras", que não contam para nada: filete colado no texto, capitular grande do Graduale, letrinhas dentro dos diagramas do Opus 165. O arquivo é `gabarito/ocr-zonas.json`, marcado "a conferir pelo Samuel".
- **Tinta:** separei a tinta do papel como o Internet Archive faz (método Sauvola, janela de 1/4 do DPI, k 0,34). Na tabela do Opus 256, as linhas retas da grade não contam como texto: só os números e as letras.
- **Caixas:** cada caixa de linha foi alargada em 15% da altura da linha, para pegar as hastes das letras, como manda a pesquisa.
- **As duas medidas pedidas:**
  - **texto achado:** quanto da tinta das zonas de texto cai dentro de alguma caixa (meta: 98% ou mais);
  - **figura tomada por texto:** quanto da tinta das zonas "não pode ter linha" cai dentro de alguma caixa (meta: 1% ou menos; numa página obrigatória, passar disso reprova).
- **Três medidas a mais, para não julgar só por um número:**
  - **área da figura coberta:** a faixa dourada e a pintura lisa quase não viram "tinta", mas uma caixa em cima delas estraga do mesmo jeito;
  - **figura tomada sem o alargamento de 15%:** separa "a caixa encosta na moldura" de "a caixa cobre a figura";
  - **linhas falsas:** caixas que quase não tocam texto nenhum.
- **Tempo:** mediana de 3 rodadas por página, neste PC (Ryzen 7 5800H, 8 núcleos e 16 linhas de execução). Cada OCR rodou sozinho, com o número de linhas de execução que ele usa por padrão. O tempo não inclui carregar o modelo, com uma exceção: o Tesseract abre um programa novo a cada página, então o tempo dele já inclui a carga.
- **Olhei as 22 folhas de contato**, com as caixas de todos os OCRs lado a lado (seção 8).

### Os OCRs e configurações medidos

| Código | O que é | Onde rodou |
|---|---|---|
| R0 | Linhas do texto invisível que o Internet Archive já pôs no PDF (só Palatino, Opus Majus, Rhetorica e Siebmacher) | leitura do PDF |
| T1 | Tesseract 5.4.0 (o que o `winget` instalou), `--psm 3`, modelo `tessdata_best` do idioma do livro: `ita`, `por`, `fra`, `eng` (o Opus Majus é tradução inglesa), `lat` e `script/Fraktur` | Windows |
| T2 | T1 com o filtro do Internet Archive: jogar fora a linha com confiança média abaixo de 20 | Windows |
| T3a | Tesseract com o modelo `frak2021` da UB Mannheim (CC0), mais o filtro | Windows |
| T3b | Tesseract com o modelo `GT4HistOCR` da UB Mannheim, mais o filtro | Windows |
| D1 | docTR pelo OnnxTR 0.9.0, só detecção, `db_resnet50`; palavras juntadas em linhas pelo próprio docTR | Windows, Python 3.14 |
| D2 | docTR pelo OnnxTR, só detecção, `fast_base` | Windows, Python 3.14 |
| P1 | PP-OCRv5 servidor pelo RapidOCR 3.9.2, só detecção; página inteira até 3000 px | Windows, Python 3.14 |
| P2 | PP-OCRv5 móvel pelo RapidOCR, idem | Windows, Python 3.14 |
| P3 | PP-OCRv6 pequeno pelo RapidOCR (extra: é o padrão do RapidOCR 3.9.2, não estava na pesquisa) | Windows, Python 3.14 |
| K1 | Kraken 7.1.1, segmentador de linhas de base `blla` (o modelo que vem no pacote), no processador | WSL (Ubuntu), Python 3.13; e **também no Windows**, em 6 páginas (ver seção 6) |

## 3. Resultado resumido (19 páginas)

As colunas "figura" olham só as 7 páginas obrigatórias: Palatino 5, Escola 35, Horas 11, 13, 26 e 27, e Opus 20.

{{RESUMO}}

## 4. Tabela OCR × página

### 4.1 Texto achado (%; em negrito, abaixo de 98%)

{{TEXTO_A}}

{{TEXTO_B}}

### 4.2 Figura tomada por texto (% da tinta da figura; em negrito, acima de 1%)

Só as páginas que têm figura. "Pal 57" conta a moldura e os laços em volta do título; "Opus 3" conta o emblema da editora e o carimbo; "Opus 165" conta os dois diagramas de traço fino.

{{FIG_A}}

{{FIG_B}}

### 4.3 A mesma coisa pela área da figura coberta (%)

{{AREA_A}}

{{AREA_B}}

### 4.4 Obrigatórias sem o alargamento de 15% (%)

Na Horas 13 o texto está colado na moldura dourada. Com o alargamento de 15%, qualquer caixa de linha inteira encosta na moldura. Sem o alargamento, o docTR `fast_base` e o Kraken ficam em 0% ali, e o PP-OCRv6 pequeno em 0,2%. Mas o 1.4 vai precisar de algum alargamento para não comer a ponta das letras. Então a Horas 13 é um problema real para quem desenha a caixa rente à moldura, e o 1.5 terá de resolver isso (ver Ideias).

{{OBRIG_CRU}}

### 4.5 Linhas falsas (todas as 22 páginas)

Uma linha é "falsa" quando menos de 30% dela cai em texto. As que ficam fora de figura importam para o 1.4, porque a tinta dentro de uma caixa fica com a cor. Uma caixa em cima da mancha do verso ou da pauta de música guardaria a mancha ou a pauta.

{{FALSAS}}

## 5. O que se vê nas folhas de contato

- **R0, as linhas que já vêm no PDF:**
  - são de graça e acham bem o texto corrido;
  - no Palatino 9, 10 e 57, as "linhas" invadem a moldura e os laços do título (6% a 18%);
  - na tabela do Opus 256, as caixas são pedacinhos que cobrem só 30% dos números;
  - servem de referência, não de detector.
- **Tesseract (T1 a T3b):**
  - acha muito bem o texto corrido impresso;
  - no Siebmacher 9 desenha "linhas" em cima de toda a moldura ornamental;
  - na Horas 11 não acha nenhuma das 10 linhas do título dentro da iluminura;
  - no Graduale acha 0 a 4 linhas;
  - no Palatino 5 põe duas linhas no alto da oval do retrato, com confiança 36 e 40, acima do limiar 20 do filtro;
  - no Palatino 9 e 10, as linhas da direita entram na moldura preta;
  - o filtro do IA só mexe no Palatino 57 (tira as "linhas" dos laços, mas também 4 linhas de texto: cai para 69% achado) e no Siebmacher (tira metade da moldura);
  - trocar o modelo (T3a, T3b) **não muda as linhas**, só a confiança, como a pesquisa tinha deduzido (seção 10.2). Com o filtro, o `GT4HistOCR` joga fora muito texto de verdade (82% achado, em média).
- **docTR `db_resnet50` (D1):** acha bem o texto, mas põe caixinhas na moldura do Siebmacher (16%), nos laços do Palatino 57 (14%) e no emblema do Opus 3 (17%).
- **docTR `fast_base` (D2):**
  - caixas justas, uma por trecho de linha;
  - não pega a moldura do Siebmacher nem os laços do Palatino 57;
  - erros: o emblema do Opus 3 (7,6%, e o emblema tem letras dentro), caixinhas na borda do retrato do Palatino 5 e na capitular Q do Palatino 9 (1,7% e 2,1%), e 4 caixas em "fantasmas" de letras da mancha do verso no Palatino 9;
  - na tabela do Opus 256 perde parte dos números (87%), porque o docTR reduz a página a 1024 px por dentro;
  - no Palatino 57 perde o "A" grande de "Anno Domini" (69% dessa linha).
- **PP-OCRv5 servidor (P1):** fora de questão. Põe caixas enormes em cima do retrato do Palatino 5 (48%), da gravura da Escola 7 (67%) e do anjo da Escola 35 (25%).
- **PP-OCRv5 móvel (P2):** texto bom; pega pedaços da moldura do Siebmacher (15%) e da moldura do Palatino 10 (4%); no Graduale põe 26 caixas em cima das notas de música.
- **PP-OCRv6 pequeno (P3):** parecido com o docTR `fast_base`:
  - não pisa no retrato do Palatino 5;
  - pega um pouco da moldura do Siebmacher (4%) e o emblema do Opus 3 (7%);
  - no Palatino 57 perde a maior parte de "Palatinus Ciuis Romanus" (só 42% dessa linha) e parte da assinatura "D iii" (88% achado na página);
  - no Graduale põe 13 caixinhas nas notas.
- **Kraken (K1):**
  - contorno ondulado, colado nas letras;
  - não pisa no retrato, no anjo nem na foto, e quase não pisa nas iluminuras das Horas 11 e 47 (menos de 1%);
  - no Siebmacher desenha "linhas" em toda a moldura ornamental (83%);
  - no Opus 165 põe uma linha num traço do diagrama (6,6%);
  - na tabela do Opus 256 falha: 33%, e o próprio Kraken avisou que não conseguiu fechar o contorno de algumas linhas ali;
  - na Horas 13 perde o "DE" grande de "DE CE QUI EST", e no Opus 3 perde o "OF" pequeno.
- **Todos os detectores** perdem parte da letra grande de floreio da assinatura "J. Sibmacher" (o docTR `fast_base` acha 48% dela, o Kraken 74%).

## 6. Manuscritos: Graduale 221 a 223 e Horas

Texto achado (%):

{{MANUSCRITO}}

- **Graduale (gótico do séc. XIV, com pauta vermelha e notas):**
  - **o Tesseract não serve** (0% a 26%);
  - o **Kraken é o melhor:** acha 95% a 99% das palavras e **não põe nenhuma caixa na música**;
  - o docTR `fast_base` acha 97% a 99%, com 5 caixinhas em notas nas três páginas;
  - o PP-OCRv6 pequeno acha 98% a 99,5%, com 13 caixinhas em notas;
  - o PP-OCRv5 móvel põe 26 caixas na música e perde parte das palavras da 222 (87%).
- **Horas (caligrafia francesa em iluminura, scan de 1024 px):**
  - todos os detectores neurais acham 96% a 100%;
  - o Tesseract não acha nada na Horas 11;
  - com o alargamento de 15%, só o Kraken fica abaixo de 1% de figura nas cinco páginas das Horas;
  - nas Horas 13 e 47 os outros encostam na moldura (ver 4.4).

## 7. Tempo

Segundos por página neste PC (mediana de 3 rodadas). T2 tem o mesmo tempo do T1: o filtro é só uma conta depois.

{{TEMPO_A}}

{{TEMPO_B}}

- **Os rápidos:** docTR `fast_base`, PP-OCRv6 pequeno e PP-OCRv5 móvel fazem cerca de 1 s por página. O Tesseract faz de 0,5 s a 9 s, conforme a quantidade de texto. O PP-OCRv5 servidor faz de 3 s a 13 s.
- **O Kraken:** 6 s a 25 s por página, mediana de 12 s. Uma página da tabela leva 25 s.
- **Kraken no Windows**, com o Python 3.12 separado que o pesquisador montou, sem WSL, em 6 páginas:
  - **deu exatamente as mesmas linhas** do WSL;
  - foi de 3% a 33% mais lento (Graduale 222: 9,6 s contra 9,0 s; Opus 11: 17,7 s contra 13,3 s).
- **Notebook do Kaique (i5-1235U), não medido.** O item 0.6 ainda não tem a régua. Estimo, por dedução, 1,5 a 2 vezes mais lento que este PC, então:
  - docTR `fast_base`: uns 2 s por página, ou 10 minutos num livro de 300 páginas;
  - Kraken: 20 a 30 s por página, ou 2 horas a 2 horas e meia num livro de 300 páginas.
- **Regra 6 (nada mais lento):** a detecção de linhas não pode entrar na prévia. Tem de rodar na hora de processar, em segundo plano.

## 8. Folhas de contato (caixas de cada OCR por cima de cada página)

Como ler:

- **azul:** caixa de linha (desenhada sem o alargamento);
- **contorno vermelho:** zona "não pode ter linha";
- **laranja** (só no T1 e no T3): linha que o filtro do Internet Archive jogaria fora;
- **R0 em cinza:** o PDF não tem texto do Internet Archive.

No alto de cada quadro: texto achado, figura tomada (tinta e área) e tempo.

{{FOLHAS}}

## 9. As zonas do gabarito (a conferir pelo Samuel)

Em cada imagem:

- **à esquerda:** verde = tem de ser texto, vermelho = não pode ter linha, cinza = neutro (não conta);
- **à direita:** a tinta que entra na conta. Verde = tinta de texto, vermelho = tinta de figura, cinza = tinta fora de zona, que não conta.

O que eu decidi ao desenhar e **você precisa confirmar**:

- os floreios do Palatino 57 ficaram dentro do texto, e os laços em volta do título ficaram como figura;
- as capitulares xilogravadas (a Q do Palatino 9) são figura, mas as capitulares desenhadas a pena do Graduale ficaram neutras;
- o endereço do site no pé da Escola é texto, mesmo que o R8 vá apagá-lo;
- o emblema do Opus 3 é figura, embora tenha letras dentro;
- as letrinhas dentro dos diagramas do Opus 165 ficaram neutras;
- os filetes da Rhetorica ficaram neutros;
- no Graduale, a pauta e as notas ficaram fora de toda zona. Elas não contam na figura, só aparecem nas "linhas falsas".

{{ZONAS}}

## 10. Detalhes

### 10.1 Pares (só para indicar se os erros se completam; juntar de verdade é o item 1.5)

"Os dois concordam" = só é texto onde os dois põem caixa. "Qualquer um" = é texto onde pelo menos um põe caixa.

{{PARES}}

- **Kraken + docTR `fast_base`, onde os dois concordam:**
  - nenhuma página passa de 1% de figura, inclusive o Siebmacher;
  - o texto cai para 95% em média, porque se perde onde qualquer um dos dois perde. A pior é a tabela do Opus 256 (32%); as outras ficam entre 94% e 100%.
- **Juntar por "qualquer um"** acha quase todo o texto, mas soma as figuras dos dois.
- O 1.5 vai precisar de algo melhor que essas duas contas simples. Por exemplo, usar o detector de gravura do ScanTailor (1.2) para vetar caixa dentro de figura. Isso é trabalho do 1.5, não deste item.

### 10.2 O modelo do Tesseract muda as linhas? (a dedução da pesquisa)

Quase nunca. Sem o filtro, T1, T3a e T3b acham o mesmo número de linhas em 19 das 22 páginas, e diferem em 1 ou 2 linhas nas outras três. O que muda é a confiança, e portanto o que o filtro joga fora.

{{LINHAS_TESS}}

## 11. Quais 2 ficam (recomendação; quem decide é o Samuel)

Pelo critério da pesquisa (seção 5.6):

1. **Cai fora quem passar de 1% de figura numa página obrigatória, a não ser que a própria confiança resolva.**
   - Com a medida pedida, só o Kraken passa nas 7.
   - Sem o alargamento, passam o Kraken e o PP-OCRv6 pequeno. O docTR `fast_base` fica a um passo: 1,2% no Palatino 5.
   - O filtro de confiança do Tesseract não resolve o caso dele.
2. **Entre os que sobram, ganha quem achar mais texto e depois quem for mais rápido.**
3. **Preferir erros diferentes.**
4. **Fica fora quem exigir WSL ou um segundo Python no notebook, a menos que ganhe com folga.**
   - O Kraken não precisa mais de WSL: roda no Windows com um Python 3.12 só dele. Ainda é um "segundo Python".
   - Ele ganha com folga em duas coisas que o Samuel pediu: não pisar em figura e servir para manuscrito.

**Recomendo Kraken + docTR `fast_base`:**

- **Kraken:**
  - é o único que respeita as páginas obrigatórias sozinho;
  - é o melhor no manuscrito;
  - é o mesmo programa que a Fase 7 usaria para ler o manuscrito;
  - o Samuel pediu OCR de manuscrito desde o começo.
- **docTR `fast_base`:**
  - é rápido, está no Python do programa e acha mais texto;
  - erra onde o Kraken acerta, e vice-versa: moldura do Siebmacher, tabela do Opus 256;
  - juntos, onde concordam, nenhuma página passou de 1% de figura.

**Alternativa, se o peso do Kraken não compensar agora:** docTR `fast_base` + PP-OCRv6 pequeno.

- Os dois são rápidos (1 s cada), leves e no Python 3.14 do programa. Onde concordam, só a Horas 13 passa de 1%, e é a moldura encostada no texto.
- Mas erram parecido: os dois pisam no emblema do Opus 3 e deixam caixinhas nas notas do Graduale.
- E o PP-OCRv6 não estava na lista da pesquisa. Entrou porque é o detector padrão do RapidOCR hoje, e mediu melhor que o PP-OCRv5 pedido.

**Ficam fora, pelo que foi medido:**

- **Tesseract:** falha no título da Horas 11, no Graduale e na moldura do Siebmacher, e o filtro não resolve. Continua sendo candidato para **transcrever** impresso na Fase 7, que é outra pergunta.
- **PP-OCRv5 servidor:** cobre retrato e gravuras.
- **docTR `db_resnet50`:** pior que o `fast_base` em tudo.
- **As linhas do Internet Archive:** são de graça, mas invadem moldura e perdem a tabela. Podem entrar no 1.4 como terceira opinião nos PDFs do IA.

## 12. O que precisa para rodar no notebook do Kaique

| OCR | O que instalar | Tamanho | Pede administrador? | Observação |
|---|---|---|---|---|
| docTR `fast_base` | pacote `onnxtr` (Python puro, Apache-2.0) e as dependências `pyclipper`, `shapely`, `rapidfuzz`, `langdetect`, `huggingface-hub`, `pypdfium2`, `defusedxml`, `anyascii`. O `onnxruntime`, o `scipy` e o `opencv` o programa já tem | pacotes: poucos MB; modelo `rep_fast_base`: **42 MB** | não | Instalou e rodou no **Python 3.14** (ambiente de teste `.venv-ocr`). Na primeira vez, o modelo baixa sozinho do GitHub: o instalador tem de levar o arquivo junto (o Kaique pode estar sem internet). A licença dos pesos não está escrita à parte (ver a pesquisa) |
| PP-OCRv6 pequeno (alternativa) | pacote `rapidocr` (Apache-2.0) e `omegaconf`, `shapely`, `pyclipper`, `colorlog` | modelo de detecção: **9,9 MB** | não | Rodou no **3.14**. Na primeira vez, baixa os modelos de um site chinês (modelscope.cn): o instalador tem de levá-los. Os modelos são da Baidu, sem licença própria escrita |
| Kraken `blla` | um **Python 3.12 só dele**, com `kraken` 7.1.1, `torch` para processador e o resto, com as versões travadas; `PYTHONUTF8=1` | **~1,2 GB** (medido pelo pesquisador); o modelo `blla` vem dentro do pacote | não | **Sem WSL** (conferido: as mesmas linhas no Windows e no WSL). O autor do Kraken não dá suporte a Windows, então cada versão nova tem de ser testada antes de ir para o instalador. Estimativa de 20 a 30 s por página no notebook. Memória: pico de 1,4 GB (pesquisador) |
| Tesseract (fora) | programa da UB Mannheim + modelos | 239 MB + 4 a 18 MB por idioma | o instalador sim; uma cópia da pasta, provavelmente não | não recomendado |

## 13. Ressalvas

- **As zonas são minhas e ainda não foram conferidas.** Mudar uma zona muda os números da página, principalmente na Horas 13, onde a moldura e o texto se encostam.
- **Sem o corte e o endireitamento do programa.** A pesquisa pedia as páginas depois dessas etapas. Usei a página como vem no PDF, porque as zonas foram desenhadas nela e as páginas do gabarito já estão quase retas. No Siebmacher, cortar a borda do scan não tira a moldura, que é do livro.
- **Scan pequeno das Horas e do Graduale** (72 DPI no arquivo, ~1000 px de largura): não aumentei a imagem. O Tesseract talvez melhore com a imagem ampliada; não testei.
- **O alargamento de 15% pesa contra quem desenha a caixa rente à moldura.** Por isso a tabela 4.4 também mostra a medida sem o alargamento.
- **O tempo no notebook do Kaique não foi medido.** Os números da seção 7 são deste PC; a conta para o notebook é dedução.
- **O Kraken no Windows** foi medido no ambiente que o pesquisador montou, em 6 páginas. As outras 16 são do WSL. O Kraken avisou "não consegui fechar o contorno" em várias linhas da tabela do Opus 256; essas linhas sumiram da saída dele.
- **O docTR reduz a página inteira a 1024 px por dentro.** Na tabela do Opus 256 isso custa números. Não testei cortar a página em pedaços.
- **O RapidOCR** rodou com o limite de lado aumentado de 2000 para 3000 px, para a página entrar inteira (a pesquisa pedia esse ajuste).
- **Tesseract 5.4.0**, o que o `winget` instalou, não o 5.5.3 citado na pesquisa. Os modelos foram baixados para `modelos\tessdata\` (fora do git): `por`, `lat`, `fra`, `ita`, `deu`, `eng`, `osd`, `script/Fraktur`, `frak2021` e `GT4HistOCR`.
- **O ambiente de teste tem o `onnxruntime` 1.30**; o programa tem o 1.28. Não testei o OnnxTR e o RapidOCR com o 1.28.
- **As linhas do Internet Archive (R0)** saem da medida das letras invisíveis, não da tinta. Uma caixa pode sair um pouco maior ou menor que a linha de verdade.
- **Três medidas são minhas, não da pesquisa:** área coberta, figura sem alargamento e linhas falsas. Estão marcadas como extra.

## 14. Arquivos

- `relatorios\fase1-1.3-comparacao-ocr-2026-09-28\` — este relatório (`.md`, `.html`, `.pdf`), as folhas de contato (`folhas\`), as zonas (`zonas\`), os números (`resultados.json`, `pares.json`) e os scripts que refazem tudo (`scripts\`, ver a docstring de cada um; ordem: `preparar.py`, `rodar_todos.sh`, `medir.py`, `pares.py`, `tabelas.py`).
- `gabarito\ocr-zonas.json` — as zonas (fora do git, como todo o `gabarito\`; há uma cópia em `zonas\ocr-zonas.json` desta pasta).
- `saida_teste\ocr-1.3\` — imagens de trabalho e as linhas de cada OCR (fora do git).
- `modelos\tessdata\` — modelos do Tesseract (fora do git).
- `.venv-ocr\` — ambiente de teste com OnnxTR, RapidOCR e `pytesseract` (fora do git; linha nova no `.gitignore`). No WSL: `/root/ocr-kraken/.venv` (Python 3.13, Kraken 7.1.1).
