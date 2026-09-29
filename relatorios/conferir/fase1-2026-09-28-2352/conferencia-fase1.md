# Conferência do item fase1: Fase 1 inteira (1.1 a 1.6): separar o escrito do fundo

<style>
body { max-width: 120rem; }
body > p, body > ul, body > ol, body > blockquote, body > pre, body > h1,
body > h2, body > h3, body > .faixa { max-width: 58rem; }
table.paineis { display: table; width: 100%; table-layout: fixed; border-collapse: separate;
  border-spacing: 10px 0; margin: .3em 0 1.3em; font-size: .92rem; }
table.paineis td { border: none; padding: 0 0 .9em; vertical-align: top; }
table.paineis td b { display: block; font-weight: 620; padding: .2em 0 .3em; }
table.paineis img { display: block; width: auto; height: auto; max-width: 100%;
  max-height: 82vh; margin: 0; }
table.paineis .falta { display: block; padding: 2.5em 1em; background: #f1efec; color: #55524d;
  border-radius: 6px; }
.faixa { padding: .8em 1.1em; border-radius: 8px; margin: 1em 0 1.4em; }
.faixa p { margin: 0; }
.faixa.falta { background: #fff1c2; border: 1px solid #e0b400; color: #3d3000; }
.faixa.pronta { background: #dff3e2; border: 1px solid #5aa469; color: #123d1c; }
@media (prefers-color-scheme: dark) {
  table.paineis .falta { background: #262421; color: #b0aca6; }
  .faixa.falta { background: #3d3200; border-color: #8a6d00; color: #fff1c2; }
  .faixa.pronta { background: #173d20; border-color: #3f7a4c; color: #dff3e2; }
}
</style>

<div class="faixa pronta"><p><strong>PRONTO PARA CONFERIR.</strong> O verificador olhou as imagens e escreveu a opinião dele logo abaixo, com as ressalvas. Quem marca o item no plano é o Samuel.</p></div>

Gerada em 28/09/2026 às 23:52, com 14 páginas-gabarito do item fase1. O **depois** são imagens já prontas, da pasta `relatorios\conferir\fase1-2026-09-28-1915`. São as imagens da rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf, reaproveitadas sem processar de novo. A coluna **Rodada anterior** mostra as imagens de `relatorios\conferir\fase1-2026-09-28-2014` (rodada de 28/09/2026 às 20:14, do programa no filtro Mágico pro), para ver o que a mudança de código mudou.

Teste **de olho**: quem decide é o Samuel, olhando.

Em cada página: **a página inteira** e, embaixo, **o detalhe ampliado** do ponto que importa (o retângulo rosa). **Clique** numa imagem para abrir em tamanho cheio. A explicação completa está no fim, em "Como ler esta página".

## Opinião do verificador

**Em uma frase:** PRONTO PARA CONFERIR, mas o resultado se divide. Nas 14 páginas, "tirar o fundo" é **melhor** que o Mágico pro de hoje em 4, **pior** em 4 e **empata** em 6. Ele ganha no livro impresso moderno (Opus Majus) e na foto. Perde no Palatino, porque ali parte do traço da moldura e da xilogravura só existe na camada que ele joga fora. Tudo o que o implementador afirmou eu conferi, e bate. Mas achei problemas que ele não contou. O mais grave: no Siebmacher, o manuscrito de tinta clara some sem aviso. Além disso, o título da Palatino 66, página do gabarito, fica oco (ver "Bugs novos").

<div class="faixa falta"><p><strong>Defeito conhecido (decisão do Samuel, 28/09): a moldura dourada e a iluminura ainda não estão resolvidas.</strong> Isso fica para os itens 1.2, 1.4 e 1.5. Nesta conferência não aparece nenhuma das duas. Os livros que as têm (Horas, Graduale) não vêm em camadas, então o "tirar o fundo" nem mexe neles, e eles continuam no Mágico pro. O mesmo vale para o papel amarelado que sobra dentro das gravuras mantidas (ver abaixo): pelas regras da Fase 1 é defeito, e o conserto é do item 1.5.</p></div>

### Como ler as colunas desta página

- **1. Original:** a página do gabarito, como foi escaneada.
- **2. "Rodada anterior":** é o **Mágico pro de hoje**, na rodada `fase1-2026-09-28-2014`, que já tem os consertos do corte e dos quadradinhos. O script chama essa coluna de "Rodada anterior" porque não tem outro nome para ela.
- **3. Resultado:** é o **"tirar o fundo"** (`core/camadas.py`), a mesma imagem da rodada `fase1-2026-09-28-1915`. Rodei de novo nas 14 páginas e deu igual, ponto por ponto.
- O Mágico pro também **corta a borda e endireita** a página. O "tirar o fundo" só troca o fundo: não corta nada. Por isso, no Siebmacher, a borda preta do scanner continua ali. Quem tira essa borda é o corte, que não faz parte deste item.
- O "tirar o fundo" **ainda não está ligado ao programa** (nem ao processamento, nem à tela). Por enquanto só dá para vê-lo por esta conferência.

### Página por página, pelas regras do resultado (papel todo branco, inclusive dentro da gravura; letra e gravura intactas; só pintura de verdade mantém a cor)

| Página | "Tirar o fundo" (coluna 3) | Mágico pro de hoje (coluna 2) | Quem cumpre melhor as regras |
|---|---|---|---|
| **Palatino 5** (retrato) | Sai **igual ao original**: papel amarelo, com a mancha marrom à esquerda do retrato. **Não cumpre** "papel branco". | Papel branco, inclusive dentro do oval. A hachura do retrato fica inteira, mas o rosto fica mais branco e duro. | **Mágico pro** |
| **Palatino 7** (texto) | Papel branco. A escrita da página vizinha some, sobram só uns pontinhos. O título "PAVLVS PAPA III" fica limpo. | Papel branco e o verso some, mas tem uma caixa cinza atrás do título. | **Tirar o fundo**, por pouco |
| **Palatino 9** (moldura e capitular "Q") | O fio grosso de cima da moldura fica **furado** (buracos brancos) e a moldura toda mais fina. Nas laterais sobra papel amarelo entre os dois fios. O "Q" fica igual ao original, **com o papel amarelo** e uma manchinha laranja dentro. | Moldura cheia e preta. O "Q" com papel branco e a hachura um pouco lavada. Sobra a tira creme entre os fios (bug já na lista). | **Mágico pro** |
| **Palatino 10** (mancha do verso) | **A mancha do verso some.** Mas a moldura fica mais fina e furada. A barra da esquerda fica oca, só com o contorno. A da direita fica com uma faixa amarelada, interrompida por buracos brancos (figura 4 abaixo). | A mancha do verso some, e a moldura fica cheia e limpa. | **Mágico pro**, por causa da moldura. No verso, empate. |
| **Palatino 57** (moldura) | A moldura dupla vira um fio fino e pontilhado em toda a volta, bem mais fraco que no original. Na metade de baixo do fio direito sobra uma faixa amarelada. Letras e floreios, bons. | Moldura cheia. Letras e floreios, bons. | **Mágico pro** |
| **Opus Majus 3** (título vermelho, carimbo) | O vermelho fica **igual ao original**. **O carimbo some inteiro.** O emblema sai mais claro, mas por igual. | O vermelho escurece para vinho, com orla escura. Do carimbo sobram os arcos cinza. O emblema fica com manchas escuras na hachura. | **Tirar o fundo** |
| **Opus Majus 11** (texto) | Papel branco, texto bom. | Papel branco, texto bom (mais escuro). | Empate |
| **Opus Majus 20** (foto da estátua) | **A foto fica intacta**, com os tons do original, e o papel em volta fica branco. Em volta da foto sobra uma **auréola bege esfumada de 2 a 3 mm** (figura 5). As partes claras da estátua ficam creme, como no original. | A foto fica lavada: estátua branca, auréola clara em volta da cabeça, contornos ondulados na parede e a faixa quebrada no alto da foto (bugs já na lista). | **Tirar o fundo**, com folga |
| **Opus Majus 165** (dois diagramas) | Papel branco e figuras nítidas, sem caixa nenhuma. | Tem uma caixa cinza atrás de cada figura (bug já na lista). | **Tirar o fundo** |
| **Opus Majus 256** (tabela) | Tabela inteira e a dobra some. A tinta fica castanha e leve, como no original. | Tabela inteira e a dobra some. A tinta fica mais preta. | Empate |
| **Rhetorica 18** (texto e notas) | Papel branco, texto como no original. | Papel branco, texto mais escuro. | Empate |
| **Rhetorica 73** (mancha d'água) | **A mancha d'água some.** Esquema e ornamentos, inteiros. | A mancha d'água some. Letra mais grossa. | Empate |
| **Siebmacher 7** (moldura ornamental) | Papel branco, moldura inteira e a anotação a mão "ach" fica. A borda preta do scanner continua (é do corte). | Papel branco e moldura inteira. Mas o programa **dividiu a folha em duas** (faixa cinza no meio) e deixou um fio castanho na borda. | Empate no filtro |
| **Siebmacher 9** (moldura e assinatura) | Igual ao 7: papel branco, moldura e "J. Sibmacher" inteiros, e a borda preta do scanner continua. | Igual ao 7: também **dividiu a folha em duas**, com a faixa cinza atravessando a assinatura. | Empate no filtro |

**Resumo:** melhor em 4 (Palatino 7, Opus 3, 20 e 165), pior em 4 (Palatino 5, 9, 10 e 57), empate em 6.

**Duas páginas do gabarito ficaram de fora desta rodada, e as duas vêm em camadas:** Palatino 66 e 67 (R4). Rodei as duas à parte (figuras 1 e 2 abaixo):

- **Palatino 66:** o título gótico "Domine dominus" fica **oco**, só o contorno das letras. O Mágico pro de hoje as deixa cheias. **Pior.**
- **Palatino 67:** sem a caixa cinza do Mágico pro em volta de "5 ꝛ ꝑ ꝝ t9", o que é melhor. Em compensação, a capitular "M" fica com o papel amarelo e a borda esfumada, e a moldura fica mais fina. **As manchas "8" e "28" continuam nos dois** (R4 não se resolve aqui; é o item 6.2). Resultado misto.

### O que o implementador afirmou, e o que eu vi

- **Papel branco e letra com a cor, nas páginas com camadas: confere.** Em 9 das 14 páginas, todo o papel fora da letra sai branco puro (medido). Nas outras 5, o que não sai branco é justamente a zona mantida (visto no mapa). O título vermelho do Opus 3 continua vermelho.
- **Somem a mancha do verso (Palatino 10), o carimbo (Opus 3) e a mancha d'água (Rhetorica 73): confere.** O carimbo some melhor que no Mágico pro.
- **A foto do Opus 20 fica intacta: confere**, com a ressalva da auréola bege em volta.
- **O Palatino 5 fica intacto e não cumpre "papel branco": confere** (a imagem é igual ao original, ponto por ponto).
- **O papel dentro das zonas mantidas fica amarelado: confere.** Isso acontece na capitular do Palatino 9, nas faixas das molduras do Palatino 9, 10 e 57 e na faixa em volta da foto do Opus 20. Na moldura, a zona mantida aparece como um remendo amarelado com buracos brancos, o que chama mais atenção do que "papel amarelado" sugere.
- **1.256 páginas reconhecidas e nenhuma por engano: confere** (medido nos 10 PDFs).
- **Gravuras que o detector não marca perdem a hachura e vêm marcadas "conferir": confere**, mas a lista do implementador é curta. No Palatino, 26 páginas saem marcadas "conferir", não 7. E existe perda **sem** o aviso (ver "Bugs novos").

### Amostra dos livros inteiros

Rodei o "tirar o fundo" em **todas as 1.256 páginas** dos 5 livros com camadas, em miniatura, e olhei as folhas de contato. Também rodei em resolução cheia 38 páginas espalhadas e olhei cada uma. Entre elas estão 9 páginas marcadas "conferir": Palatino 48, 66, 68, 73 e 94; Rhetorica 125 e 206; Siebmacher 13 e 15.

- **Os 4 livros sem camadas dizem "não":** Graduale, Horas, Marial e Escola, e também o Boécio. Nenhuma página de nenhum deles é reconhecida.
- **Palatino (134 páginas):** 100 com o fundo tirado; 26 marcadas "conferir"; 8 intactas (as duas capas e 6 pranchas de figura em página inteira, entre elas a 5, a 71 e a 116). Nas páginas "conferir" que olhei de perto, a perda é real. Na 68, as letras góticas perdem o recheio cinza e ficam pontilhadas. Na 94, o fundo pontilhado da gravura fica ralo. Na 66, o título fica oco. Na 48, a faixa pontilhada do título fica clara.
- **Siebmacher (134 páginas):** 75 com o fundo tirado, 3 "conferir" e 56 intactas (44 pranchas de bordado que o detector marca inteiras, 10 em que a camada de cima cobre a página e 2 capas). Nas "conferir" 13, 15 e 25, o quadriculado do bordado **fica bege-pálido** em faixas inteiras (figuras 8 e 14): a perda é grave. As páginas com o verso transparecendo ficam brancas, o que está certo. **Nas páginas manuscritas do fim (101 a 106), a tinta clara some:** na 104 e na 105, palavras e linhas inteiras desaparecem, e nenhuma das duas sai marcada "conferir" (figuras 7 e 11). O manuscrito da 10 e o da 103 ficam quase inteiros.
- **Pesel (92 páginas):** 17 com o fundo tirado (o texto e as folhas em branco) e 75 intactas (capa, cartão pardo e todas as pranchas de bordado). Nada de foto se apagou. O ornamento vermelho do rosto continua vermelho.
- **Rhetorica (446 páginas):** 428 com o fundo tirado, 3 "conferir" (125, 206, 259) e 15 intactas (as gravuras de página inteira). O texto corrido sai branco e bom. Nos versos em que a gravura de trás transparece (126, 128, 205), o fantasma some, o que está certo. Em 11 páginas a gravura fica mantida como o PDF, num retângulo amarelado sobre a página branca (266, por exemplo). A Rhetorica 38 sai pior: a zona do detector cobre só parte da gravura, que fica **metade amarela, metade branca**, sem aviso (figura 12).
- **Opus Majus (450 páginas):** 448 com o fundo tirado, nenhuma "conferir" e 2 intactas (as capas). É o livro em que o "tirar o fundo" acerta mais: o texto e os diagramas saem brancos e limpos, e as duas fotos (20 e 109, o retrato de Clemente IV) ficam intactas, com o papel branco em volta (figura 13).
- **Nas 38 páginas em resolução cheia, o saldo foi este:** no Opus Majus e na Rhetorica, texto e figuras de traço saem certos. No Palatino e no Siebmacher, mais da metade das páginas "conferir" perde traço de verdade. Na Rhetorica 125 e 206 e no Palatino 73, a perda é pequena e o aviso sobra.

### Ressalvas

1. **Velocidade não foi medida pelo teste oficial** (pediram para não rodar). Os tempos que existem não se comparam direto. A função levou de 1,5 a 5,2 s por página, na resolução cheia do PDF (400 a 600 DPI), e cerca de 1,5 s por página no livro inteiro em miniatura, porque o exame da página roda sempre a 150 DPI. Quando isto for ligado ao programa, falta medir se a prévia ficou mais lenta (regra 6).
2. **A decisão "é figura, manter" depende do detector de hoje** (`core/detectar_regioes.py`), o mesmo que já erra em outras páginas (Palatino 67, Rhetorica 18). O item 1.2 troca esse detector, e o resultado pode mudar.
3. **Quando o tom ou a hachura da gravura só existe na camada de baixo, não há meio-termo.** Ou a gravura sai inteira, com o papel amarelo (Palatino 5 e 9, Opus 20, Rhetorica 266), ou sai com o papel branco e o traço mais fraco (Palatino 48, 66, 68 e 94; Siebmacher 13 e 15). Juntar as duas coisas é trabalho do 1.5. Quando o traço está todo na camada de cima (Opus 165, Rhetorica 125, as molduras do Siebmacher), a gravura sai certa: papel branco e traço inteiro.
4. **Duas páginas do gabarito com camadas (Palatino 66 e 67) não estavam na rodada do implementador.** Mostro as duas abaixo, fora das colunas.
5. **A tela não foi testada**, porque a função ainda não está ligada a ela.

### Máquina ou olho

- **Máquina:** os testes passam (790 no total, 60 deles do `test_camadas`). O "tirar o fundo" rodado de novo nas 14 páginas dá o mesmo resultado, ponto por ponto. O reconhecimento dos 10 PDFs deu 1.256 páginas nos 5 livros com camadas e 0 nos outros 5. O Palatino 5 sai idêntico ao original. O papel fora das zonas é 100% branco em 9 das 14 páginas. A auréola do Opus 20 mede de 2 a 3 mm.
- **Olho:** todo o resto. As 14 páginas, cada uma com as três colunas lado a lado e ampliadas nos pontos pedidos; as páginas 66 e 67; as 38 páginas da amostra em resolução cheia; e as folhas de contato das 1.256 páginas dos 5 livros inteiros, em miniatura. Na miniatura só aparece a perda grande; a perda fina, só nas páginas vistas em tamanho cheio.

### Para o Samuel conferir em 10 minutos

1. **Opus Majus 20:** a foto intacta (coluna 3) contra a foto lavada (coluna 2), e a auréola bege em volta (figura 5). Vale a troca?
2. **Opus Majus 3:** o vermelho e o carimbo, na coluna 3 contra a 2.
3. **Palatino 5:** fica igual ao original. Aceita assim até o 1.5, ou prefere o Mágico pro, que já deixa o papel branco?
4. **Palatino 9, 10 e 57:** a moldura furada e mais fina, e o remendo amarelado (figuras 3 e 4). É o pior do "tirar o fundo".
5. **Palatino 66 (figura 1):** o título oco. É página de R4.
6. **Siebmacher 104, 105 e 13 (figuras 11, 7 e 8):** o manuscrito que some sem aviso, e o bordado que fica pálido.
7. **A decisão:** usar o "tirar o fundo" sempre que o PDF tem camadas, ou só como opção, ou esperar o 1.2 e o 1.5 antes de ligar? Pelo que vi, **ligar para todas as páginas com camadas pioraria o Palatino** em relação ao Mágico pro de hoje.

### Figuras extras (fora das colunas)

**Figura 1: Palatino 66, o título.** Original · Mágico pro de hoje · tirar o fundo. As letras ficam ocas.

<img src="verificador/v01-palatino66-titulo.jpg" alt="Palatino 66: original, Mágico pro de hoje, tirar o fundo">

**Figura 2: Palatino 67 inteira.** Original · Mágico pro de hoje · tirar o fundo.

<img src="verificador/v02-palatino67-inteira.jpg" alt="Palatino 67 inteira">

**Figura 3: Palatino 9, o canto da moldura.** No "tirar o fundo", o fio grosso de cima fica furado.

<img src="verificador/v03-palatino09-moldura.jpg" alt="Palatino 9, canto da moldura">

**Figura 4: Palatino 10, a moldura da direita.** O remendo amarelado com buracos brancos (coluna da direita).

<img src="verificador/v04-palatino10-moldura-direita.jpg" alt="Palatino 10, moldura direita">

**Figura 5: Opus Majus 20, o canto da foto.** No "tirar o fundo", a auréola bege em volta da foto. No Mágico pro, a faixa quebrada no alto.

<img src="verificador/v05-opus20-aureola.jpg" alt="Opus 20, canto da foto">

**Figura 6: Palatino 68 ("conferir").** À esquerda o PDF como está, à direita o "tirar o fundo". As letras perdem o recheio.

<img src="verificador/v06-palatino68.jpg" alt="Palatino 68">

**Figura 7: Siebmacher 105 (sem aviso).** À esquerda o PDF, à direita o "tirar o fundo". O manuscrito claro some quase todo e a página **não** sai marcada "conferir".

<img src="verificador/v07-siebmacher105.jpg" alt="Siebmacher 105">

**Figura 8: Siebmacher 13 ("conferir").** À esquerda o PDF, à direita o "tirar o fundo". O quadriculado do bordado fica bege-pálido.

<img src="verificador/v08-siebmacher13.jpg" alt="Siebmacher 13">

**Figura 9: Rhetorica 125 ("conferir"), exemplo em que o aviso sobra.** À esquerda o PDF, à direita o "tirar o fundo". A gravura fica boa, com o papel branco.

<img src="verificador/v09-rhetorica125.jpg" alt="Rhetorica 125">

**Figura 10: Palatino 94 ("conferir").** À esquerda o PDF, à direita o "tirar o fundo". O fundo pontilhado da gravura fica ralo.

<img src="verificador/v10-palatino94.jpg" alt="Palatino 94">

**Figura 11: Siebmacher 104 (sem aviso).** À esquerda o PDF, à direita o "tirar o fundo". Somem palavras inteiras do manuscrito.

<img src="verificador/v11-siebmacher104.jpg" alt="Siebmacher 104">

**Figura 12: Rhetorica 38 (sem aviso).** À esquerda o PDF, à direita o "tirar o fundo". A mesma gravura sai metade amarela, metade branca.

<img src="verificador/v12-rhetorica38.jpg" alt="Rhetorica 38">

**Figura 13: Opus Majus 109, exemplo bom.** À esquerda o PDF, à direita o "tirar o fundo". O retrato fica intacto e o papel em volta, branco.

<img src="verificador/v13-opus109.jpg" alt="Opus Majus 109">

**Figura 14: Siebmacher 15 ("conferir").** À esquerda o PDF, à direita o "tirar o fundo". A faixa do meio do bordado fica pálida.

<img src="verificador/v14-siebmacher15.jpg" alt="Siebmacher 15">

### Bugs novos (para a Lista de bugs, 28/09)

1. **Siebmacher 104 e 105: o manuscrito de tinta clara some em boa parte, sem o aviso "conferir"** (figuras 7 e 11). A tinta desses manuscritos está quase toda na camada de baixo, e o aviso só conta o traço bem mais escuro que o papel. É perda de conteúdo em silêncio. Onde: `core/camadas.py` (o aviso `CONFERIR_TINTA_PERDIDA` e o `TOM_DE_FIGURA`).
2. **Palatino 66, página do gabarito (R4): o título gótico fica oco** (figura 1). A página sai marcada "conferir", mas fica pior que o Mágico pro de hoje. Onde: `core/camadas.py`. É da mesma família das gravuras "conferir".
3. **O Palatino 10 perde parte da moldura sem o aviso "conferir"** (a medida dá 1,17%, e o aviso só dispara a partir de 1,5%). Onde: `core/camadas.py`.
4. **Onde a zona mantida acaba, fica um remendo:** faixa amarelada com borda esfumada e buracos brancos (Palatino 10, moldura direita; Palatino 9, laterais; Opus 20, auréola de 2 a 3 mm). Na Rhetorica 38, a zona pega só parte da gravura, que sai metade amarela, metade branca, sem aviso (figura 12). Onde: `core/camadas.py` (a borda suave da zona do detector em `compor`) e o detector de hoje.
5. **A rodada do implementador deixou de fora Palatino 66 e 67**, que são do gabarito e vêm em camadas. Não é defeito do programa; é da conferência.

## 1. Giovambattista Palatino cittadino romano, página 5 do PDF

**O que olhar:** R1: papel branco, letras e gravura (retrato) intactas

`palatino_p005`. Processada em 5,2 segundos, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-3-resultado.jpg" width="115" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p005.jpg" target="_blank"><img src="paineis/01-palatino_p005-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-1-original-detalhe.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-2-anterior-detalhe.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p005.png" target="_blank"><img src="paineis/01-palatino_p005-3-resultado-detalhe.jpg" width="115" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p005.jpg" target="_blank"><img src="paineis/01-palatino_p005-4-scantailor-detalhe.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 2. Giovambattista Palatino cittadino romano, página 7 do PDF

**O que olhar:** R1: papel branco, letras intactas; tem mancha de outra página (marcada de azul no documento)

`palatino_p007`. Processada em 2,1 segundos, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-1-original-detalhe.jpg" width="239" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-2-anterior-detalhe.jpg" width="239" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p007.png" target="_blank"><img src="paineis/02-palatino_p007-3-resultado-detalhe.jpg" width="239" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td><td></td></tr>
</table>

## 3. Giovambattista Palatino cittadino romano, página 9 do PDF

**O que olhar:** R1: papel branco, letras e gravura intactas; borda preta em volta do texto

`palatino_p009`. Processada em 2,1 segundos, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-3-resultado.jpg" width="115" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-1-original-detalhe.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-2-anterior-detalhe.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-3-resultado-detalhe.jpg" width="115" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/palatino_p009.png" target="_blank"><img src="paineis/03-palatino_p009-4-scantailor-detalhe.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 4. Giovambattista Palatino cittadino romano, página 10 do PDF

**O que olhar:** R2: sumir com a sombra do verso (folha só de letras)

`palatino_p010`. Processada em 2,0 segundos, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p010.png" target="_blank"><img src="paineis/04-palatino_p010-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 5. Giovambattista Palatino cittadino romano, página 57 do PDF

**O que olhar:** R3: margens iguais / centralizar (texto mais à esquerda, moldura em volta)

`palatino_p057`. Processada em 1,5 segundo, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 6. opusmajustransla01baco, página 3 do PDF

**O que olhar:** Fase 1.1: folha de rosto com título em vermelho. As letras (vermelhas e pretas) e o emblema estão na camada de cima, com a cor original. O fundo vem em resolução cheia e tem o carimbo da biblioteca, um tique de lápis e 'fantasmas' claros das letras: ao tirar o fundo, o carimbo some e as letras têm de continuar vermelhas.

`opusmajus_p003`. Processada em 1,8 segundo, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p003.png" target="_blank"><img src="paineis/06-opusmajus_p003-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p003.png" target="_blank"><img src="paineis/06-opusmajus_p003-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p003.png" target="_blank"><img src="paineis/06-opusmajus_p003-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p003.png" target="_blank"><img src="paineis/06-opusmajus_p003-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p003.png" target="_blank"><img src="paineis/06-opusmajus_p003-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p003.png" target="_blank"><img src="paineis/06-opusmajus_p003-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 7. opusmajustransla01baco, página 11 do PDF

**O que olhar:** Fase 1.1 (tirar o fundo de PDF com camadas): texto corrido, abertura da Introdução. O fundo é só papel, em baixa resolução; todo o texto está na camada de cima. Caso normal.

`opusmajus_p011`. Processada em 2,3 segundos, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p011.png" target="_blank"><img src="paineis/07-opusmajus_p011-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p011.png" target="_blank"><img src="paineis/07-opusmajus_p011-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p011.png" target="_blank"><img src="paineis/07-opusmajus_p011-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p011.png" target="_blank"><img src="paineis/07-opusmajus_p011-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p011.png" target="_blank"><img src="paineis/07-opusmajus_p011-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p011.png" target="_blank"><img src="paineis/07-opusmajus_p011-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 8. opusmajustransla01baco, página 20 do PDF

**O que olhar:** Fase 1.1: foto (estátua de Roger Bacon). Os tons da foto estão só no fundo, em baixa resolução; a camada de cima tem os pontinhos pretos da foto e a legenda. Jogando o fundo fora, a foto vira um pontilhado duro: caso que o programa precisa perceber para não estragar a foto.

`opusmajus_p020`. Processada em 3,1 segundos, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p020.png" target="_blank"><img src="paineis/08-opusmajus_p020-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p020.png" target="_blank"><img src="paineis/08-opusmajus_p020-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p020.png" target="_blank"><img src="paineis/08-opusmajus_p020-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p020.png" target="_blank"><img src="paineis/08-opusmajus_p020-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p020.png" target="_blank"><img src="paineis/08-opusmajus_p020-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p020.png" target="_blank"><img src="paineis/08-opusmajus_p020-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 9. opusmajustransla01baco, página 165 do PDF

**O que olhar:** Fase 1.1: texto com dois diagramas geométricos de traço fino (Fig. 7 e 8). O fundo é só papel; texto e diagramas estão na camada de cima. Caso fácil com figura: os traços finos não podem sumir.

`opusmajus_p165`. Processada em 1,9 segundo, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p165.png" target="_blank"><img src="paineis/09-opusmajus_p165-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p165.png" target="_blank"><img src="paineis/09-opusmajus_p165-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p165.png" target="_blank"><img src="paineis/09-opusmajus_p165-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p165.png" target="_blank"><img src="paineis/09-opusmajus_p165-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p165.png" target="_blank"><img src="paineis/09-opusmajus_p165-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p165.png" target="_blank"><img src="paineis/09-opusmajus_p165-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 10. opusmajustransla01baco, página 256 do PDF

**O que olhar:** Fase 1.1: tabela grande numa folha dobrável deitada (tamanho de página diferente das outras), com linhas finas e números pequenos. A tabela está na camada de cima; o fundo tem o papel, a marca da dobra e 'fantasmas' claros das linhas.

`opusmajus_p256`. Processada em 2,4 segundos, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p256.png" target="_blank"><img src="paineis/10-opusmajus_p256-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p256.png" target="_blank"><img src="paineis/10-opusmajus_p256-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p256.png" target="_blank"><img src="paineis/10-opusmajus_p256-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p256.png" target="_blank"><img src="paineis/10-opusmajus_p256-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p256.png" target="_blank"><img src="paineis/10-opusmajus_p256-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p256.png" target="_blank"><img src="paineis/10-opusmajus_p256-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 11. Rhetorica Christiana -  Fray Diego Valadés, página 18 do PDF

**O que olhar:** Teste do ScanTailor de 24/09: página de texto ('Præfatio') com notas na margem; papel branco com o texto 'o mais vivo possível'

`rhetorica_p018`. Processada em 1,9 segundo, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p018.png" target="_blank"><img src="paineis/11-rhetorica_p018-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/rhetorica_p018.png" target="_blank"><img src="paineis/11-rhetorica_p018-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/rhetorica_p018.png" target="_blank"><img src="paineis/11-rhetorica_p018-3-resultado.jpg" width="115" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/rhetorica_p018.png" target="_blank"><img src="paineis/11-rhetorica_p018-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p018.png" target="_blank"><img src="paineis/11-rhetorica_p018-1-original-detalhe.jpg" width="239" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/rhetorica_p018.png" target="_blank"><img src="paineis/11-rhetorica_p018-2-anterior-detalhe.jpg" width="239" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/rhetorica_p018.png" target="_blank"><img src="paineis/11-rhetorica_p018-3-resultado-detalhe.jpg" width="239" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/rhetorica_p018.png" target="_blank"><img src="paineis/11-rhetorica_p018-4-scantailor-detalhe.jpg" width="239" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 12. Rhetorica Christiana -  Fray Diego Valadés, página 73 do PDF

**O que olhar:** Teste do ScanTailor de 24/09: esquema com chaves e dois ornamentos ('Pars secunda', número impresso 49); na lista de 18/07, 'gravura de traço fino'

`rhetorica_p073`. Processada em 1,9 segundo, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p073.png" target="_blank"><img src="paineis/12-rhetorica_p073-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/rhetorica_p073.png" target="_blank"><img src="paineis/12-rhetorica_p073-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/rhetorica_p073.png" target="_blank"><img src="paineis/12-rhetorica_p073-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p073.png" target="_blank"><img src="paineis/12-rhetorica_p073-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/rhetorica_p073.png" target="_blank"><img src="paineis/12-rhetorica_p073-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/rhetorica_p073.png" target="_blank"><img src="paineis/12-rhetorica_p073-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 13. Schön Neues Modell Buch - Johann Siebmacher, página 7 do PDF

**O que olhar:** R7: tamanho final A4 com margem certa para encadernar (página do teste do ScanTailor)

`siebmacher_p007`. Processada em 1,7 segundo, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p007.png" target="_blank"><img src="paineis/13-siebmacher_p007-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/siebmacher_p007.png" target="_blank"><img src="paineis/13-siebmacher_p007-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/siebmacher_p007.png" target="_blank"><img src="paineis/13-siebmacher_p007-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p007.png" target="_blank"><img src="paineis/13-siebmacher_p007-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/siebmacher_p007.png" target="_blank"><img src="paineis/13-siebmacher_p007-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/siebmacher_p007.png" target="_blank"><img src="paineis/13-siebmacher_p007-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 14. Schön Neues Modell Buch - Johann Siebmacher, página 9 do PDF

**O que olhar:** R7: tamanho final A4 com margem certa para encadernar (página do print do Vamos recapitular, assinada 'J. Sibmacher')

`siebmacher_p009`. Processada em 2,0 segundos, na rodada de 28/09/2026 às 19:15, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p009.png" target="_blank"><img src="paineis/14-siebmacher_p009-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/siebmacher_p009.png" target="_blank"><img src="paineis/14-siebmacher_p009-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/siebmacher_p009.png" target="_blank"><img src="paineis/14-siebmacher_p009-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p009.png" target="_blank"><img src="paineis/14-siebmacher_p009-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/siebmacher_p009.png" target="_blank"><img src="paineis/14-siebmacher_p009-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/siebmacher_p009.png" target="_blank"><img src="paineis/14-siebmacher_p009-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## Como ler esta página

- Cada página tem duas faixas: **a página inteira** e, logo abaixo, **o detalhe ampliado** do ponto que o gabarito manda olhar. O retângulo rosa na página inteira mostra de onde o detalhe saiu, em cada coluna.
- As colunas vêm sempre nesta ordem: **Original** (a página do gabarito, como foi escaneada), **Rodada anterior** (quando houver), **Resultado**, e as referências que existem para aquela página: **CamScanner Mágico Pro** e **ScanTailor 24/09**.
- **Clique** em qualquer imagem para abrir em tamanho cheio.
- Quadriculado cinza no detalhe é pedaço que não existe naquela imagem (por exemplo, a margem que o programa cortou).

## Como esta página foi feita

- **Comando:** `.venv\Scripts\python.exe conferencia.py fase1 --paginas palatino_p005,palatino_p007,palatino_p009,palatino_p010,palatino_p057,opusmajus_p003,opusmajus_p011,opusmajus_p020,opusmajus_p165,opusmajus_p256,rhetorica_p018,rhetorica_p073,siebmacher_p007,siebmacher_p009 --pasta-depois relatorios/conferir/fase1-2026-09-28-1915 --comparar-com relatorios/conferir/fase1-2026-09-28-2014 --opiniao C:/Users/fotog/AppData/Local/Temp/claude/d--programas/e4642c9c-e61b-4a83-8212-99957ed37365/scratchpad/verif11/opiniao.md`
- **Pasta:** `D:\programas\EditorImpressao\relatorios\conferir\fase1-2026-09-28-2352`. Nela, `resultado\` tem o resultado de cada página em tamanho cheio (é o que o `--comparar-com` lê numa conferência futura), `paineis\` tem as imagens reduzidas desta página e `dados.json` tem os números crus. O original fica no gabarito (`gabarito\paginas\`); as referências recortadas, em `relatorios\conferir\_referencias\`.
- **Como o detalhe é achado em cada coluna:** o programa corta as bordas e endireita a página, e as referências têm outro enquadramento; por isso o detalhe não sai da mesma fração de cada imagem, e sim do mesmo ponto do livro, achado alinhando cada imagem com o original pelos pontos em comum (SIFT e RANSAC, do OpenCV). Quando o alinhamento não dá certeza, o bloco da página avisa.
- **Levou** 20,9 segundos no total.
- **Versões:** Python 3.14.3 · PyMuPDF 1.28.0 · OpenCV 5.0.0 · numpy 2.5.1
