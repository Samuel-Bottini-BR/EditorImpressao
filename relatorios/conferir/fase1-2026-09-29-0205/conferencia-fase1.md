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

<div class="faixa falta"><p><strong>NÃO ESTÁ PRONTO (falta uma coisa).</strong> O verificador olhou as imagens e escreveu a opinião dele logo abaixo, com as ressalvas: ainda há uma página que perde escrita sem aviso (Siebmacher 106). O resto do que foi pedido está consertado ou marcado. Quem marca o item no plano é o Samuel.</p></div>

Gerada em 29/09/2026 às 02:05, com 16 páginas-gabarito do item fase1. O **depois** são imagens já prontas, da pasta `relatorios\conferir\fase1-2026-09-29-0108`. São as imagens da rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf, reaproveitadas sem processar de novo. A coluna **Rodada anterior** mostra as imagens de `relatorios\conferir\fase1-2026-09-28-2014` (rodada de 28/09/2026 às 20:14, do programa no filtro Mágico pro), para ver o que a mudança de código mudou.

Teste **de olho**: quem decide é o Samuel, olhando.

Em cada página: **a página inteira** e, embaixo, **o detalhe ampliado** do ponto que importa (o retângulo rosa). **Clique** numa imagem para abrir em tamanho cheio. A explicação completa está no fim, em "Como ler esta página".

## Opinião do verificador

**Em uma frase:** NÃO ESTÁ PRONTO, por um motivo só: ainda achei uma página que perde escrita sem aviso (Siebmacher 106, figuras 9 e 10). Todo o resto que o implementador disse ter consertado eu conferi, e bate. As molduras do Palatino 9, 10 e 57 ficam cheias. O remendo amarelo acabou. A Rhetorica 38 sai inteira. O Siebmacher 104 e 105 ficam intactos. O verso, o carimbo e a mancha d'água continuam sumidos. Contra o Mágico pro de hoje, o placar das 14 páginas antigas foi de **4 melhores, 4 piores e 6 empates** para **5 melhores, 2 piores e 7 empates**.

<div class="faixa falta"><p><strong>Defeito conhecido (decisão do Samuel, 28/09): a moldura dourada e a iluminura ainda não estão resolvidas.</strong> Elas ficam para os itens 1.2, 1.4 e 1.5. Nesta conferência não aparece nenhuma das duas. Os livros que as têm (Horas, Graduale) não vêm em camadas, então o "tirar o fundo" nem mexe neles, e eles continuam no Mágico pro.</p></div>

### Como ler as colunas desta página

- **1. Original:** a página do gabarito, como foi escaneada.
- **2. "Rodada anterior":** é o **Mágico pro de hoje** (rodada `fase1-2026-09-28-2014`). O script chama essa coluna de "Rodada anterior" porque não tem outro nome para ela.
- **3. Resultado:** é o **"tirar o fundo" novo** (`core/camadas.py`, commit `e588374`), a mesma imagem da rodada `fase1-2026-09-29-0108`. Nada foi processado de novo para esta página.
- O Mágico pro também corta a borda e endireita. O "tirar o fundo" só troca o fundo, então no Siebmacher a borda preta do scanner continua ali.
- O "tirar o fundo" **ainda não está ligado ao programa**. Página que ele deixa "intacta" aparece aqui igual ao PDF. No programa, pelo que o código diz, ela seguiria para o filtro de hoje.

### Página por página, pelas regras do resultado (papel todo branco, inclusive dentro da gravura; letra e gravura intactas)

| Página | "Tirar o fundo" novo (coluna 3) | O que mudou desde 28/09 | Mágico pro de hoje (coluna 2) | Quem cumpre melhor |
|---|---|---|---|---|
| **Palatino 5** (retrato) | Igual ao original: papel amarelo e a mancha marrom. | Nada. | Papel branco, inclusive no oval. | **Mágico pro** |
| **Palatino 7** (texto) | Papel branco. A escrita da página vizinha some, sobram uns pontinhos. | Nada. | Tem uma caixa cinza atrás do título. | **Tirar o fundo**, por pouco |
| **Palatino 9** (moldura e "Q") | A moldura fica **cheia**, sem furos (figura 3). A tira entre os dois fios fica branca. No "Q", o papel fica quase branco e a hachura fica inteira (figura 2). | Muito melhor. | Moldura cheia. O "Q" fica mais lavado e sobra a tira creme entre os fios (bug já na lista). | **Tirar o fundo**, por pouco (antes era o Mágico pro) |
| **Palatino 10** (verso) | **A mancha do verso continua sumida** no texto. As barras da moldura ficam cheias. Mas entre os fios da direita sobra a sombra do verso: uma faixa cinza-clara em pedaços, com buracos brancos (figura 4). | Melhor. O remendo trocou o amarelo pelo cinza, mas continua lá. | Moldura limpa, sem faixa. | **Mágico pro**, por pouco |
| **Palatino 57** (moldura) | A moldura dupla fica cheia, sem a faixa amarela (figura 5). | Muito melhor. | Moldura cheia. | **Empate** (antes era o Mágico pro) |
| **Palatino 66** (título gótico) | O título **não fica mais oco**. Mas o recheio das letras volta mais claro e manchado, com partes brancas no meio (figura 1). | Melhor que o oco de 28/09. | Letras cheias. | **Mágico pro** |
| **Palatino 67** (capitular "M") | No "M", o papel fica branco e a hachura fica com tom (figura 19). Não tem a caixa cinza em volta de "5 ꝛ ꝑ ꝝ t9". As manchas "8" e "28" continuam: isso é do item 6.2. | Não entrou na rodada de 28/09. | Caixa cinza e "M" mais ralo. | **Tirar o fundo**, por pouco |
| **Opus Majus 3** | O vermelho fica igual ao original e **o carimbo continua sumido** (figura 8). | Nada. | Vermelho vira vinho, e sobram arcos do carimbo. | **Tirar o fundo** |
| **Opus Majus 11** | Papel branco, texto bom. | Nada. | Igual. | Empate |
| **Opus Majus 20** (foto) | **A auréola bege sumiu.** O papel fica branco até a borda da foto (figura 6). Mas a foto toda fica mais clara, e não só sem o creme: a estátua passa do cinza 184 para 228 (0 = preto, 255 = branco). Ela não fica lavada como no Mágico pro (figura 7). | 35% da página clareou. | Foto lavada, com a faixa quebrada no alto. | **Tirar o fundo**, com folga |
| **Opus Majus 165** | Papel branco e figuras nítidas. | Nada. | Caixa cinza atrás das figuras. | **Tirar o fundo** |
| **Opus Majus 256** | Tabela inteira. | Nada. | Tabela inteira, tinta mais preta. | Empate |
| **Rhetorica 18** | Papel branco, texto como o original. | Nada. | Igual, texto mais escuro. | Empate |
| **Rhetorica 73** | **A mancha d'água continua sumida.** Esquema e ornamentos, inteiros. | Quase nada (0,03% da página). | Igual. | Empate |
| **Siebmacher 7** | Papel branco, moldura inteira, a anotação "ach" fica. | Quase nada. | Divide a folha em duas. | Empate no filtro |
| **Siebmacher 9** | Papel branco, moldura e assinatura inteiras. | Quase nada. | Divide a folha em duas. | Empate no filtro |

**Placar nas 14 páginas da conferência anterior:** 5 melhores (Palatino 7 e 9; Opus 3, 20 e 165), 2 piores (Palatino 5 e 10) e 7 empates. **Antes eram 4, 4 e 6.** Entraram agora nas melhores o Palatino 9 e nos empates o Palatino 57. Com a Palatino 66 (pior) e a 67 (melhor), as 16 páginas dão 6 melhores, 3 piores e 7 empates.

### O que o implementador afirmou, e o que eu vi

- **A tinta que só existe no fundo volta: confere.** As molduras do Palatino 9, 10 e 57 ficam cheias. O título da Palatino 66 recupera parte do recheio, mas não todo.
- **O verso, o carimbo e a mancha d'água não voltam: confere** nas três páginas (Palatino 10 no texto, Opus 3 e Rhetorica 73). Tem duas exceções. Dentro da faixa mantida da moldura do Palatino 10, a sombra do verso fica. E, quando o verso é forte e está colado na linha de texto, ele volta em pontinhos cinza: não só no Palatino 48, como o implementador disse, mas também no Palatino 12 (figura 16).
- **A escrita clara só no fundo deixa a página intacta (Siebmacher 104 e 105): confere.** As duas saem iguais ao PDF. **Mas a regra não pega o Siebmacher 106** (ver "Bugs novos").
- **A máscara invertida (Siebmacher 13, 15 e 25): confere em parte.** O bordado não fica mais bege-pálido em faixas inteiras. No 13, o papel fica em parte branco e em parte bege-claro, com manchas (figura 12). No 15, a grade fina some em manchas brancas (figura 11). No 25, o bordado fica inteiro. As três saem marcadas "conferir".
- **O papel dentro das zonas mantidas vira branco: confere.** O remendo amarelo e a auréola do Opus 20 acabaram. A Rhetorica 38 não sai mais metade amarela, metade branca: a gravura sai inteira, com o papel branco (figura 15). A exceção é o Palatino 10, em que o remendo virou cinza.
- **O aviso "conferir" conta também o traço trazido do fundo: confere.** São 26 páginas do Palatino, 3 da Rhetorica (125, 206 e 259) e 3 do Siebmacher (13, 15 e 25).
- **As sobras que ele declarou: todas conferem.** A grade do Siebmacher 15 vira manchas brancas. O verso do Palatino 48 volta cinzento (figura 13). O pontilhado do Palatino 94 fica ralo (figura 14). No Palatino 68, as letras continuam perdendo o recheio cinza e ficam pontilhadas, quase como em 28/09. No Opus 20, como já disse, a foto fica mais clara no todo, e não só sem o creme.

### Amostra do acervo (páginas que ninguém tinha olhado)

Rodei o "tirar o fundo" em **todas as 1.256 páginas** dos 5 livros com camadas, em miniatura. A decisão de cada página sai igual em qualquer resolução, porque a análise é sempre a 150 DPI. Depois abri **33 páginas novas, espalhadas pelos 5 livros**: 12 em resolução cheia e 21 em miniatura, lado a lado com o PDF. Também medi, página por página, onde a tinta do PDF vira branco, para achar perda fora da amostra. Só apareceram a borda da folha vizinha e o papel escuro da Pesel, que não são conteúdo.

- **Como o livro inteiro ficou** (entre parênteses, a conta de 28/09):
  - **Opus Majus:** 448 com o fundo tirado e 2 intactas (as capas) (igual a 28/09).
  - **Palatino:** 100 com o fundo tirado, 26 "conferir" e 8 intactas (igual).
  - **Rhetorica:** 428 com o fundo tirado, 3 "conferir" e 15 intactas (igual).
  - **Siebmacher:** 55 com o fundo tirado, 3 "conferir" e 76 intactas (antes 75, 3 e 56). As 20 intactas a mais são as de escrita clara: os manuscritos e as folhas em que o bordado de trás transparece. Elas não perdem nada, mas também não saem limpas.
  - **Pesel:** 15 com o fundo tirado e 77 intactas (antes 17 e 75). A 8 e a 9 agora ficam intactas.
- **Palatino** 12, 21, 45, 74, 87, 100, 112 e 126: texto, caligrafia, capitulares e a prancha de letras sobre xilogravura (74) saem certos, com o papel branco. Na 12, sobram pontinhos cinza do verso ao lado das linhas (figura 16).
- **Siebmacher:**
  - 4, 25, 88, 97, 99, 100, 101, 102, 112 e 126: certas. O manuscrito escuro (99 a 102) fica inteiro. O verso transparente some. As manchas de tinta ficam.
  - **106: perda sem aviso** (figuras 9 e 10).
  - 118 e 124: duvidosas. Traços muito fracos somem, sem aviso (figura 18). Não consegui dizer se é desenho ou o bordado de trás: não batem com as páginas vizinhas espelhadas.
- **Pesel:**
  - 2: o ex-libris fica mantido, mas as manchas de ferrugem dentro dele ficam rosadas sobre o papel branco (figura 17).
  - 8: o manuscrito "Printed in Switzerland" deixa a página intacta, o que está certo.
  - 12 e 13: o texto sobre papel escuro sai inteiro, com o papel branco.
  - 30: cartão pardo, intacta (sei pela conta; a imagem eu não abri).
- **Rhetorica** 60, 212, 259, 330 e 344, e **Opus Majus** 130, 250 e 350: todas certas.
- **As 9 páginas do implementador** (pasta `acervo\`): Siebmacher 104 e 105, intactas. Siebmacher 13 e 15, Palatino 48, 66, 68 e 94: "conferir", com a perda descrita acima. Rhetorica 38: certa.

### Ressalvas

1. **Velocidade: o teste oficial não foi rodado** (pediram para não rodar). Medi só a função, a antiga contra a nova, nas mesmas 6 páginas, em duas rodadas alternadas: a nova é **cerca de 25% mais lenta** (8,6 s para 10,8 s, uns 0,35 s a mais por página). A função ainda não está ligada ao programa. Quando for ligada, isto entra na regra 6.
2. **Os números da conferência `0108` (a coluna de tempo)** foram medidos com outro agente trabalhando no PC. Não servem para comparar.
3. **A decisão do que é figura ainda depende do detector de hoje.** O item 1.2 troca esse detector, e o resultado pode mudar.
4. **O que separa a escrita clara do verso é a quantidade**, medida só nestes cinco livros (o próprio código diz isso). Uma nota clara pequena numa página quase vazia passa sem aviso, e foi o que aconteceu no Siebmacher 106.
5. **Os testes:** passam 811. Os 3 que falham são de `tests/test_melhorar_em_volta_da_gravura.py`, o trabalho em andamento de outro agente em `core/filtros.py`, e não do "tirar o fundo". O `test_camadas` passa inteiro (69).
6. **A tela não foi testada:** a função não está ligada a ela.

### Máquina ou olho

- **Máquina:**
  - Os testes (811 passam; os 3 que falham são do outro agente).
  - A conta das 1.256 páginas.
  - O que mudou, ponto por ponto, entre a rodada de 28/09 e a nova: nada no Opus 3, 11, 165 e 256, na Rhetorica 18 e no Palatino 5; menos de 0,1% no Palatino 7, na Rhetorica 73 e no Siebmacher 7 e 9; 6,6% no Palatino 9, 2,4% no 10 e no 57, e 36% no Opus 20.
  - O tom da estátua (184 para 228).
  - O tempo, antiga contra nova.
- **Olho:**
  - As 16 páginas do gabarito, inteiras e ampliadas nos pontos pedidos, com o original, o "tirar o fundo" de 28/09, o novo e o Mágico pro lado a lado.
  - As 9 páginas do implementador.
  - As 33 páginas novas da amostra.

### Recomendação sobre as três opções do Samuel

**Usar "tirar o fundo" só como opção (um botão, rodando livro por livro), e não sempre. E não esperar o 1.2 e o 1.5 para oferecer o botão.**

- **Não "sempre":**
  - ainda existe uma perda sem aviso (Siebmacher 106);
  - o Palatino continua misto: título da 66 mais claro, sombra do verso na moldura da 10, pontinhos de verso na 12 e na 48, 26 páginas "conferir";
  - a função ficou uns 25% mais lenta.
- **Não esperar:**
  - no Opus Majus ele já é melhor que o Mágico pro, em 448 páginas, sem nenhum "conferir": foto intacta, sem auréola, carimbo e mancha fora, vermelho certo;
  - na Rhetorica, empata ou ganha;
  - como botão, o Kaique usa onde ganha e deixa desligado no Palatino.
- **Antes de "sempre":** consertar a escrita clara do tipo Siebmacher 106 e rever depois do 1.2 e do 1.5, que mudam as zonas de figura.

### Para o Samuel conferir em 10 minutos

1. **Opus Majus 20 (figuras 6 e 7):** a foto sem a auréola, contra a foto lavada do Mágico pro. A estátua ficou mais clara que o original. Aceita assim?
2. **Palatino 9, 10 e 57 (figuras 2 a 5):** as molduras agora cheias. No Palatino 10, a faixa cinza com buracos entre os fios da direita.
3. **Palatino 66 (figura 1):** o título não está mais oco, mas fica mais claro que no Mágico pro.
4. **Siebmacher 106 (figuras 9 e 10):** a escrita clara que some sem aviso.
5. **Siebmacher 15 e 13 (figuras 11 e 12):** a grade do bordado.
6. **A decisão:** sempre, só como opção, ou esperar o 1.2 e o 1.5.

### Figuras extras (fora das colunas)

Nas figuras de quatro colunas: original · "tirar o fundo" de 28/09 · "tirar o fundo" novo · Mágico pro. Nas de duas: o PDF como está · "tirar o fundo" novo.

**Figura 1: Palatino 66, o título.** Original · novo · Mágico pro. As letras voltam a ter recheio, mas mais claro e manchado.

<img src="verificador/v01-palatino66-titulo.jpg" alt="Palatino 66, título">

**Figura 2: Palatino 9, a capitular "Q".** Papel quase branco, hachura inteira.

<img src="verificador/v02-palatino09-capitular.jpg" alt="Palatino 9, capitular">

**Figura 3: Palatino 9, o canto da moldura.** Sem os furos de 28/09.

<img src="verificador/v03-palatino09-canto.jpg" alt="Palatino 9, canto">

**Figura 4: Palatino 10, a moldura da direita.** As barras ficam cheias, mas sobra a faixa cinza-clara com buracos (a sombra do verso).

<img src="verificador/v04-palatino10-moldura-direita.jpg" alt="Palatino 10, moldura direita">

**Figura 5: Palatino 57, a moldura da direita.** Cheia, sem a faixa amarela.

<img src="verificador/v05-palatino57-moldura.jpg" alt="Palatino 57, moldura">

**Figura 6: Opus Majus 20, o canto da foto.** Sem a auréola bege de 28/09.

<img src="verificador/v06-opus20-canto.jpg" alt="Opus 20, canto da foto">

**Figura 7: Opus Majus 20, a estátua.** No novo, ela fica mais clara que o original, mas não lavada como no Mágico pro.

<img src="verificador/v07-opus20-estatua.jpg" alt="Opus 20, estátua">

**Figura 8: Opus Majus 3, o carimbo.** Continua sumido.

<img src="verificador/v08-opus03-carimbo.jpg" alt="Opus 3, carimbo">

**Figura 9: Siebmacher 106 (sem aviso).** À esquerda o PDF, à direita o "tirar o fundo". Somem as sete linhas de escrita clara no alto, à esquerda. Fica só o "1672".

<img src="verificador/v09-siebmacher106.jpg" alt="Siebmacher 106">

**Figura 10: Siebmacher 106 com o contraste aumentado,** ao lado da 107 e da 104 espelhadas. A escrita da 106 não bate com o verso: é da própria página.

<img src="verificador/v10-siebmacher106-realce.jpg" alt="Siebmacher 106, contraste">

**Figura 11: Siebmacher 15 ("conferir").** A grade fina some em manchas brancas.

<img src="verificador/v11-siebmacher15.jpg" alt="Siebmacher 15">

**Figura 12: Siebmacher 13 ("conferir").** A grade fica, mas o papel fica manchado, em parte branco e em parte bege-claro.

<img src="verificador/v12-siebmacher13.jpg" alt="Siebmacher 13">

**Figura 13: Palatino 48 ("conferir").** Os floreios do verso voltam cinzentos, e a faixa pontilhada do título fica mais rala.

<img src="verificador/v13-palatino48.jpg" alt="Palatino 48">

**Figura 14: Palatino 94 ("conferir").** O fundo pontilhado da gravura fica ralo.

<img src="verificador/v14-palatino94.jpg" alt="Palatino 94">

**Figura 15: Rhetorica 38.** A gravura sai inteira, com o papel branco. Não sai mais metade amarela, metade branca.

<img src="verificador/v15-rhetorica38.jpg" alt="Rhetorica 38">

**Figura 16: Palatino 12 (sem aviso).** O verso forte volta em pontinhos cinza ao lado das linhas. Não é perda: é sujeira que fica.

<img src="verificador/v16-palatino12-verso.jpg" alt="Palatino 12">

**Figura 17: Pesel 2.** O ex-libris fica inteiro, mas as manchas de ferrugem dentro dele ficam rosadas.

<img src="verificador/v17-pesel02-exlibris.jpg" alt="Pesel 2">

**Figura 18: Siebmacher 118 (duvidosa).** Traços muito fracos somem, sem aviso. Não sei dizer se é desenho.

<img src="verificador/v18-siebmacher118.jpg" alt="Siebmacher 118">

**Figura 19: Palatino 67, a capitular "M".** Original · novo · Mágico pro.

<img src="verificador/v19-palatino67-capitular.jpg" alt="Palatino 67, capitular">

### Bugs novos (para a Lista de bugs, 29/09)

1. **Siebmacher 106: escrita clara some sem aviso** (figuras 9 e 10). São umas sete linhas de manuscrito claro no alto, à esquerda. A página não fica intacta nem sai marcada "conferir". A medida dá 0,2% de escrita clara perdida, e ela é 0,067 da tinta de cima: abaixo dos dois limites (1% e 0,15). Onde: `core/camadas.py` (`TINTA_CLARA_DOMINA`, `CONFERIR_TINTA_CLARA`).
2. **Palatino 10: a sombra do verso fica dentro da zona mantida da moldura**, como uma faixa cinza-clara com buracos brancos (figura 4). O remendo trocou o amarelo pelo cinza, mas continua. Onde: `core/camadas.py` (a zona mantida branqueia só o papel, e o verso fica).
3. **O verso forte colado na linha de texto volta em pontinhos cinza**: não só no Palatino 48, mas também no 12 (figura 16), e provavelmente em outras páginas do Palatino com verso forte. Onde: `core/camadas.py` (`TINTA_DO_FUNDO_COMECA` junto com `PERTO_DA_TINTA_DE_CIMA_MM`).
4. **Opus Majus 20: a foto inteira fica mais clara que o original** (estátua de 184 para 228), e não só sem o creme. Pelas regras da Fase 1 (papel branco) pode estar certo. Fica para o Samuel decidir.
5. **A função ficou cerca de 25% mais lenta** (medida antiga contra nova, nas mesmas 6 páginas). Entra na regra 6 quando for ligada.
6. Pequeno: **Pesel 2**, a ferrugem dentro do ex-libris mantido fica rosada (figura 17).

## 1. Giovambattista Palatino cittadino romano, página 5 do PDF

**O que olhar:** R1: papel branco, letras e gravura (retrato) intactas

`palatino_p005`. Processada em 4,6 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

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

`palatino_p007`. Processada em 2,5 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

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

`palatino_p009`. Processada em 2,5 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

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

`palatino_p010`. Processada em 2,5 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

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

`palatino_p057`. Processada em 2,0 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p057.png" target="_blank"><img src="paineis/05-palatino_p057-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 6. Giovambattista Palatino cittadino romano, página 66 do PDF

**O que olhar:** R4: tirar as manchas vermelhas sem mexer no título

`palatino_p066`. Processada em 2,2 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p066.png" target="_blank"><img src="paineis/06-palatino_p066-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 7. Giovambattista Palatino cittadino romano, página 67 do PDF

**O que olhar:** R4: manchas no papel amarelado (circuladas de laranja no documento), 'mesmo problema da anterior' (p. 66)

`palatino_p067`. Processada em 2,3 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-1-original-detalhe.jpg" width="239" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-2-anterior-detalhe.jpg" width="239" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/palatino_p067.png" target="_blank"><img src="paineis/07-palatino_p067-3-resultado-detalhe.jpg" width="239" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td><td></td></tr>
</table>

## 8. opusmajustransla01baco, página 3 do PDF

**O que olhar:** Fase 1.1: folha de rosto com título em vermelho. As letras (vermelhas e pretas) e o emblema estão na camada de cima, com a cor original. O fundo vem em resolução cheia e tem o carimbo da biblioteca, um tique de lápis e 'fantasmas' claros das letras: ao tirar o fundo, o carimbo some e as letras têm de continuar vermelhas.

`opusmajus_p003`. Processada em 3,0 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p003.png" target="_blank"><img src="paineis/08-opusmajus_p003-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p003.png" target="_blank"><img src="paineis/08-opusmajus_p003-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p003.png" target="_blank"><img src="paineis/08-opusmajus_p003-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p003.png" target="_blank"><img src="paineis/08-opusmajus_p003-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p003.png" target="_blank"><img src="paineis/08-opusmajus_p003-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p003.png" target="_blank"><img src="paineis/08-opusmajus_p003-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 9. opusmajustransla01baco, página 11 do PDF

**O que olhar:** Fase 1.1 (tirar o fundo de PDF com camadas): texto corrido, abertura da Introdução. O fundo é só papel, em baixa resolução; todo o texto está na camada de cima. Caso normal.

`opusmajus_p011`. Processada em 3,3 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p011.png" target="_blank"><img src="paineis/09-opusmajus_p011-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p011.png" target="_blank"><img src="paineis/09-opusmajus_p011-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p011.png" target="_blank"><img src="paineis/09-opusmajus_p011-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p011.png" target="_blank"><img src="paineis/09-opusmajus_p011-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p011.png" target="_blank"><img src="paineis/09-opusmajus_p011-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p011.png" target="_blank"><img src="paineis/09-opusmajus_p011-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 10. opusmajustransla01baco, página 20 do PDF

**O que olhar:** Fase 1.1: foto (estátua de Roger Bacon). Os tons da foto estão só no fundo, em baixa resolução; a camada de cima tem os pontinhos pretos da foto e a legenda. Jogando o fundo fora, a foto vira um pontilhado duro: caso que o programa precisa perceber para não estragar a foto.

`opusmajus_p020`. Processada em 4,2 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p020.png" target="_blank"><img src="paineis/10-opusmajus_p020-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p020.png" target="_blank"><img src="paineis/10-opusmajus_p020-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p020.png" target="_blank"><img src="paineis/10-opusmajus_p020-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p020.png" target="_blank"><img src="paineis/10-opusmajus_p020-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p020.png" target="_blank"><img src="paineis/10-opusmajus_p020-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p020.png" target="_blank"><img src="paineis/10-opusmajus_p020-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 11. opusmajustransla01baco, página 165 do PDF

**O que olhar:** Fase 1.1: texto com dois diagramas geométricos de traço fino (Fig. 7 e 8). O fundo é só papel; texto e diagramas estão na camada de cima. Caso fácil com figura: os traços finos não podem sumir.

`opusmajus_p165`. Processada em 3,1 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p165.png" target="_blank"><img src="paineis/11-opusmajus_p165-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p165.png" target="_blank"><img src="paineis/11-opusmajus_p165-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p165.png" target="_blank"><img src="paineis/11-opusmajus_p165-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p165.png" target="_blank"><img src="paineis/11-opusmajus_p165-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p165.png" target="_blank"><img src="paineis/11-opusmajus_p165-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p165.png" target="_blank"><img src="paineis/11-opusmajus_p165-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 12. opusmajustransla01baco, página 256 do PDF

**O que olhar:** Fase 1.1: tabela grande numa folha dobrável deitada (tamanho de página diferente das outras), com linhas finas e números pequenos. A tabela está na camada de cima; o fundo tem o papel, a marca da dobra e 'fantasmas' claros das linhas.

`opusmajus_p256`. Processada em 4,2 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p256.png" target="_blank"><img src="paineis/12-opusmajus_p256-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p256.png" target="_blank"><img src="paineis/12-opusmajus_p256-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p256.png" target="_blank"><img src="paineis/12-opusmajus_p256-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/opusmajus_p256.png" target="_blank"><img src="paineis/12-opusmajus_p256-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/opusmajus_p256.png" target="_blank"><img src="paineis/12-opusmajus_p256-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/opusmajus_p256.png" target="_blank"><img src="paineis/12-opusmajus_p256-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 13. Rhetorica Christiana -  Fray Diego Valadés, página 18 do PDF

**O que olhar:** Teste do ScanTailor de 24/09: página de texto ('Præfatio') com notas na margem; papel branco com o texto 'o mais vivo possível'

`rhetorica_p018`. Processada em 2,7 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p018.png" target="_blank"><img src="paineis/13-rhetorica_p018-1-original.jpg" width="115" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/rhetorica_p018.png" target="_blank"><img src="paineis/13-rhetorica_p018-2-anterior.jpg" width="115" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/rhetorica_p018.png" target="_blank"><img src="paineis/13-rhetorica_p018-3-resultado.jpg" width="115" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/rhetorica_p018.png" target="_blank"><img src="paineis/13-rhetorica_p018-4-scantailor.jpg" width="115" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p018.png" target="_blank"><img src="paineis/13-rhetorica_p018-1-original-detalhe.jpg" width="239" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/rhetorica_p018.png" target="_blank"><img src="paineis/13-rhetorica_p018-2-anterior-detalhe.jpg" width="239" alt="2. Rodada anterior"></a></td></tr>
<tr><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/rhetorica_p018.png" target="_blank"><img src="paineis/13-rhetorica_p018-3-resultado-detalhe.jpg" width="239" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td><td><b>4. ScanTailor 24/09</b><a href="../_referencias/scantailor-24-09/rhetorica_p018.png" target="_blank"><img src="paineis/13-rhetorica_p018-4-scantailor-detalhe.jpg" width="239" alt="4. ScanTailor 24/09"></a></td></tr>
</table>

## 14. Rhetorica Christiana -  Fray Diego Valadés, página 73 do PDF

**O que olhar:** Teste do ScanTailor de 24/09: esquema com chaves e dois ornamentos ('Pars secunda', número impresso 49); na lista de 18/07, 'gravura de traço fino'

`rhetorica_p073`. Processada em 2,7 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p073.png" target="_blank"><img src="paineis/14-rhetorica_p073-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/rhetorica_p073.png" target="_blank"><img src="paineis/14-rhetorica_p073-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/rhetorica_p073.png" target="_blank"><img src="paineis/14-rhetorica_p073-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/rhetorica_p073.png" target="_blank"><img src="paineis/14-rhetorica_p073-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/rhetorica_p073.png" target="_blank"><img src="paineis/14-rhetorica_p073-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/rhetorica_p073.png" target="_blank"><img src="paineis/14-rhetorica_p073-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 15. Schön Neues Modell Buch - Johann Siebmacher, página 7 do PDF

**O que olhar:** R7: tamanho final A4 com margem certa para encadernar (página do teste do ScanTailor)

`siebmacher_p007`. Processada em 2,7 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p007.png" target="_blank"><img src="paineis/15-siebmacher_p007-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/siebmacher_p007.png" target="_blank"><img src="paineis/15-siebmacher_p007-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/siebmacher_p007.png" target="_blank"><img src="paineis/15-siebmacher_p007-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p007.png" target="_blank"><img src="paineis/15-siebmacher_p007-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/siebmacher_p007.png" target="_blank"><img src="paineis/15-siebmacher_p007-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/siebmacher_p007.png" target="_blank"><img src="paineis/15-siebmacher_p007-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## 16. Schön Neues Modell Buch - Johann Siebmacher, página 9 do PDF

**O que olhar:** R7: tamanho final A4 com margem certa para encadernar (página do print do Vamos recapitular, assinada 'J. Sibmacher')

`siebmacher_p009`. Processada em 2,5 segundos, na rodada de 29/09/2026 às 01:08, da função core.camadas:tirar_fundo_do_pdf.

**A página inteira** (o retângulo rosa é de onde vem o detalhe):

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p009.png" target="_blank"><img src="paineis/16-siebmacher_p009-1-original.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/siebmacher_p009.png" target="_blank"><img src="paineis/16-siebmacher_p009-2-anterior.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/siebmacher_p009.png" target="_blank"><img src="paineis/16-siebmacher_p009-3-resultado.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

**O detalhe ampliado**, o mesmo ponto do livro em cada coluna:

<table class="paineis">
<tr><td><b>1. Original</b><a href="../../../gabarito/paginas/siebmacher_p009.png" target="_blank"><img src="paineis/16-siebmacher_p009-1-original-detalhe.jpg" width="157" alt="1. Original"></a></td><td><b>2. Rodada anterior</b><a href="../fase1-2026-09-28-2014/resultado/siebmacher_p009.png" target="_blank"><img src="paineis/16-siebmacher_p009-2-anterior-detalhe.jpg" width="157" alt="2. Rodada anterior"></a></td><td><b>3. Resultado: core.camadas:tirar_fundo_do_pdf</b><a href="resultado/siebmacher_p009.png" target="_blank"><img src="paineis/16-siebmacher_p009-3-resultado-detalhe.jpg" width="157" alt="3. Resultado: core.camadas:tirar_fundo_do_pdf"></a></td></tr>
</table>

## Como ler esta página

- Cada página tem duas faixas: **a página inteira** e, logo abaixo, **o detalhe ampliado** do ponto que o gabarito manda olhar. O retângulo rosa na página inteira mostra de onde o detalhe saiu, em cada coluna.
- As colunas vêm sempre nesta ordem: **Original** (a página do gabarito, como foi escaneada), **Rodada anterior** (quando houver), **Resultado**, e as referências que existem para aquela página: **CamScanner Mágico Pro** e **ScanTailor 24/09**.
- **Clique** em qualquer imagem para abrir em tamanho cheio.
- Quadriculado cinza no detalhe é pedaço que não existe naquela imagem (por exemplo, a margem que o programa cortou).

## Como esta página foi feita

- **Comando:** `.venv\Scripts\python.exe conferencia.py fase1 --paginas palatino_p005,palatino_p007,palatino_p009,palatino_p010,palatino_p057,palatino_p066,palatino_p067,opusmajus_p003,opusmajus_p011,opusmajus_p020,opusmajus_p165,opusmajus_p256,rhetorica_p018,rhetorica_p073,siebmacher_p007,siebmacher_p009 --pasta-depois relatorios/conferir/fase1-2026-09-29-0108 --comparar-com relatorios/conferir/fase1-2026-09-28-2014 --opiniao C:/Users/fotog/AppData/Local/Temp/claude/d--programas/e4642c9c-e61b-4a83-8212-99957ed37365/scratchpad/v12/opiniao.md`
- **Pasta:** `D:\programas\EditorImpressao\relatorios\conferir\fase1-2026-09-29-0205`. Nela, `resultado\` tem o resultado de cada página em tamanho cheio (é o que o `--comparar-com` lê numa conferência futura), `paineis\` tem as imagens reduzidas desta página e `dados.json` tem os números crus. O original fica no gabarito (`gabarito\paginas\`); as referências recortadas, em `relatorios\conferir\_referencias\`.
- **Como o detalhe é achado em cada coluna:** o programa corta as bordas e endireita a página, e as referências têm outro enquadramento; por isso o detalhe não sai da mesma fração de cada imagem, e sim do mesmo ponto do livro, achado alinhando cada imagem com o original pelos pontos em comum (SIFT e RANSAC, do OpenCV). Quando o alinhamento não dá certeza, o bloco da página avisa.
- **Levou** 28,3 segundos no total.
- **Versões:** Python 3.14.3 · PyMuPDF 1.28.0 · OpenCV 5.0.0 · numpy 2.5.1
