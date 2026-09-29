# Opinião do verificador: item 1.1, rodadas 08:51 e 09:56 de 29/09/2026

> **Aviso (decisão do Samuel, 28/09): moldura dourada e iluminura são defeito conhecido** até a Fase 1 ficar pronta (itens 1.2, 1.4 e 1.5). Nenhuma página desta conferência tem moldura dourada nem iluminura; o aviso vale para o item inteiro.

## Veredito

**PRONTO PARA CONFERIR.** Os dois consertos fazem o que prometem. O Siebmacher 106, o 118 e o 124 agora saem marcados "conferir" (antes perdiam escrita sem aviso). A foto do Opus Majus 20 sai com o mesmo tom e o mesmo creme do original, com o papel em volta branco e sem auréola. Continuam três defeitos já conhecidos: a faixa cinza do Palatino 10, o véu na gravura da Rhetorica 38 e a ferrugem rosada da Pesel 2. O Palatino 5 continua saindo amarelo, porque a página inteira fica intacta. Detalhes e ressalvas abaixo.

Quem decide é o Samuel. Isto não é aprovação.

## O que foi feito (máquina ou olho)

| O quê | Tipo | Resultado |
|---|---|---|
| Testes automáticos (`pytest tests -q`) | máquina | **844 passaram**, nenhum falhou (o teste instável `test_marcacao_em_todas` passou desta vez) |
| As 16 imagens da rodada 09:56 saem mesmo do código atual (commit `06f747e`)? | máquina | Rodei a função de novo nas 16 páginas: **as 16 saem idênticas ponto a ponto** às imagens da rodada |
| "As outras 15 páginas são idênticas à rodada 08:51" | máquina | **Confirmado**: os 15 arquivos são iguais byte a byte; só o Opus Majus 20 mudou |
| Todas as imagens das duas rodadas: 16 páginas × original, anterior, resultado e referências, página inteira e detalhe; os 3 lado a lado do acervo em 09:56 e os 10 do acervo em 08:51 | olho | Abertas todas, página a página (as colunas de cada página juntas numa folha só, e os detalhes difíceis um por um) |
| Rhetorica 38 (não estava em nenhuma das duas rodadas) | olho | Gerei a página inteira e dois recortes ampliados |
| Opus Majus 20, beiradas da foto | olho + máquina | Mapa das diferenças contra o PDF e quatro recortes ampliados |
| Afirmação do Palatino 12 ("não é perda") | olho + máquina | Separei a camada de cima do Internet Archive e comparei |
| Velocidade | máquina | Só a medida isolada. O teste de velocidade oficial **não** foi rodado, por ordem da gerente |

## O que vi em cada página

### As 16 páginas do gabarito (iguais nas duas rodadas, menos o Opus Majus 20)

| Página | O que vi |
|---|---|
| Palatino 5 | **Página deixada intacta**: papel amarelo e fundo do retrato amarelo, como no original. É o comportamento combinado do 1.1 ("tudo na camada de baixo fica intacto"), mas **não cumpre a regra da Fase 1** (papel todo branco, inclusive no retrato). Não sai marcada "conferir". |
| Palatino 7 | Papel branco, letras intactas. A mancha de outra página sumiu quase toda; sobram pontinhos cinza dos dois lados de "gusti, M. D. XXXX." (vêm na camada de cima). |
| Palatino 9 | Molduras cheias, capitular Q inteira. Dentro da caixa do Q o papel fica **levemente azulado** (branco 248, 252, 255), com um véu cinza-claro em parte do miolo. Sai "conferir". |
| Palatino 10 | Sombra do verso sumida no texto, papel branco. **A moldura da direita está cheia, mas ao lado dela continua a faixa cinza-azulada com buracos brancos** (bug "em parte", sem mudança). Não sai "conferir". |
| Palatino 57 | Moldura dupla cheia; título e ornamentos intactos. Sobra um fantasma cinza do verso acima de "Palatinus". Sai "conferir". |
| Palatino 66 | Título "Domine dominus noster" **cheio** (não mais oco), mas mais claro que o original e com riscas claras dentro de algumas hastes. Restos marrons da mancha no "P" de "Palatinus" (a mancha em si é da Fase 6). Sai "conferir". |
| Palatino 67 | Papel branco, texto intacto. As manchas laranja "8", "28" e a da capitular continuam coloridas (Fase 6). Dentro da capitular M, o miolo fica acinzentado e mais macio que o original. |
| Opus Majus 3 | Muito bom: papel branco, título vermelho, carimbo da biblioteca sumido. **Novo desde a rodada 08:51: sai marcada "conferir"** (a regra da escrita fraca vê o carimbo). É o preço combinado de "página duvidosa sai marcada". |
| Opus Majus 11 | Papel branco, texto intacto. Caso normal, sem defeito. |
| Opus Majus 20 | Ver a seção própria abaixo. **Consertado.** |
| Opus Majus 165 | Papel branco; as figuras 7 e 8 com os traços finos inteiros. |
| Opus Majus 256 | Tabela inteira, linhas e números intactos, papel branco. (O detalhe da coluna "Resultado" sai deslocado em relação ao original: é o alinhamento da página de conferência, não defeito da imagem.) |
| Rhetorica 18 | Papel branco, texto e notas da margem intactos, igual ou melhor que o ScanTailor. |
| Rhetorica 73 | Esquema com chaves e os dois ornamentos intactos; sobram alguns pontinhos cinza no meio, à esquerda. |
| Siebmacher 7 | Papel branco, moldura de ornatos intacta, a nota manuscrita "ach" mantida. O fundo preto do scanner sai em retalhos pretos na borda direita. Conferi: **o retalho já vem na camada de cima do Internet Archive** (fica para o corte, item 2.13). |
| Siebmacher 9 | Igual ao 7: papel branco, ornatos e assinatura intactos, retalhos pretos do scanner na borda. |

### Opus Majus 20 (o conserto de 09:56)

- **A estátua e o creme estão iguais ao original.** A olho, lado a lado, não há diferença de tom. Na máquina, 98,8% dos pontos dentro da foto são idênticos ao PDF, e o rosto mede o mesmo valor antes e depois.
- **Papel entre a foto e a legenda: branco** (média 254, mínimo 233; só 2% abaixo de 250: uma linhazinha cinza bem fraca logo abaixo da foto, que é a marca da chapa).
- **Sem auréola e sem remendo** em volta da foto (a auréola da rodada 08:51 sumiu).
- **Beirada clara da foto:** procurei de propósito. Nas beiradas de cima, da direita e da esquerda, perde-se só a linha de 1 a 3 pontos da borda. **Na beirada de baixo, num trecho de uns 3 cm, a foto perde até uns 6 pontos (cerca de 0,35 mm), e aparece um degrauzinho** onde o corte sobe (imagem v01). O implementador escreveu "fora a linha de 1 ponto da beirada"; na beirada de baixo é um pouco mais. **Não se vê no tamanho normal**, só ampliando.

![](v01-opus20-beirada-de-baixo.jpg)

![](v02-opus20-beirada-esquerda.jpg)

![](v03-opus20-beirada-de-cima.jpg)

![](v04-opus20-lado-direito.jpg)

### Páginas do acervo

| Página | O que vi |
|---|---|
| Siebmacher 104 e 105 | Deixadas intactas: todo o manuscrito claro fica. Nada some. |
| Siebmacher 106 | As sete linhas de manuscrito claro **continuam sumindo** (só fica o "1672"), mas agora **a página sai marcada "conferir"**. É o que foi decidido. |
| Siebmacher 118 | O desenho fraco (triângulos, linhas) some quase todo; **sai "conferir"**. |
| Siebmacher 124 | Os furinhos do molde ficam em boa parte, os traços mais fracos somem; **sai "conferir"**. |
| Siebmacher 13 e 15 | Os bordados ficam mais claros e partes da grade de baixo clareiam; as duas **saem "conferir"** (traço trazido do fundo). |
| Siebmacher 25 | Sem diferença a olho entre antes e depois (a zona "de tom" é o preto do scanner embaixo da folha). |
| Palatino 12 | Ver abaixo. A moldura está cheia (a camada de cima a traz oca), com uma tira levemente azulada entre os dois fios. |
| Palatino 48 | Faixa escura do alto mais clara e granulada; fantasmas do verso visíveis no pé. Sai "conferir". |
| Palatino 94 | O fundo escuro rendado da gravura fica **bem mais claro e ralo** que o original. Sai "conferir". |
| Pesel 2 | **A ferrugem do ex-libris continua rosada**, igual antes e depois (bug separado, sem conserto, como o implementador avisou). |
| Rhetorica 38 | Não há mais metade amarela. Mas a gravura fica **desigual**: à esquerda e no alto, só o traço da camada de cima em papel branco; à direita e embaixo (zona mantida), um véu cinza-bege e o traço mais denso (imagens v08 e v09). |

**Palatino 12, a afirmação "não é perda": confirmada.** Separei a camada de cima do Internet Archive: os pontinhos cinza do verso ao lado de "hora" já estão lá, e o resultado é igual a ela nesse trecho (imagem v06). Não é escrita que sumiu: é sujeira do verso que o Internet Archive já tinha posto na camada de cima (defeito de limpeza, da família da mancha do verso, R2 e Fase 6).

![](v06-palatino12-verso.jpg)

![](v05-palatino10-faixa-cinza.jpg)

![](v09-rhetorica38-meio.jpg)

## Estado de cada bug do 1.1 na Lista de bugs

| Data | Bug | Estado que eu vi |
|---|---|---|
| 28/09 | Siebmacher 104 e 105: manuscrito some sem aviso | **Consertado**: as duas ficam intactas. |
| 29/09 | Siebmacher 106 (e 118, 124) perde escrita sem aviso; pontinhos do Palatino 12 | **Consertado como decidido**: a escrita ainda some, mas as três saem "conferir". Palatino 12: não é perda (confirmado). |
| 29/09 | "Tirar o fundo" 25% mais lento (8,6 para 10,8 s) | **Parece devolvido**, pelas medidas do implementador (8,6 s). Ver "Velocidade". |
| 28/09 | Palatino 66 título oco; molduras do 9, 10 e 57 furadas | **Consertado**: título e molduras cheios. O título fica mais claro que o original, com riscas claras. |
| 28/09 | Remendo amarelado, auréola, Rhetorica 38 metade amarela | **Em parte.** O amarelo e a auréola sumiram (inclusive no Opus 20). Continuam: a faixa cinza com buracos do Palatino 10; o véu cinza-bege da zona mantida na Rhetorica 38; papel levemente azulado dentro das zonas mantidas (Palatino 9, 12, 67). |
| 29/09 | Opus Majus 20 mais claro que o original | **Consertado.** Ressalva pequena: até 0,35 mm da beirada de baixo da foto vira branco, com um degrauzinho (só ampliando). |
| 29/09 | Pesel 2: ferrugem rosada no ex-libris | **Continua** (não fazia parte do conserto). Falta a decisão do Samuel: a mancha deve sumir ou manter a cor? |

## As regras do resultado da Fase 1

- **Papel todo branco:** cumprida em 15 das 16 páginas do gabarito. **Não cumprida no Palatino 5** (página intacta, amarela). Dentro das zonas mantidas, o papel sai só quase branco (levemente azulado, ou com véu cinza): Palatino 9, 10 e 67, e Rhetorica 38.
- **Gravura e letras intactas:** cumprida nas 16 páginas do gabarito. No acervo, o traço trazido do fundo sai mais claro (Palatino 94 e 48; Siebmacher 13 e 15), mas essas páginas saem "conferir".
- **Pintura de verdade mantém a cor:** a foto do Opus 20 mantém. Não há pintura colorida nas páginas do 1.1.
- **Moldura dourada e iluminura:** nenhuma nestas páginas; continuam defeito conhecido (1.2, 1.4, 1.5).

## Velocidade

- **Medida do implementador** (isolada, sem outro agente rodando, 6 páginas a 300 DPI): 8,58 s antes e 8,64 s depois do conserto do Opus 20 (dentro do ruído).
- **A minha repetição, com a máquina dividida com outro agente** (não vale como medida, só como comparação na mesma condição): commit `3779ec5` 11,9 s em média, commit `06f747e` 11,4 s. O conserto não deixou a função mais lenta.
- **O teste de velocidade oficial não foi rodado** (ordem da gerente: há outro agente na máquina). "Tirar o fundo" ainda não está ligado ao programa; a regra 6 só vai ser medida de verdade quando ele for ligado.
- Dúvida para a gerente: o commit `3779ec5` diz "8,7 s nas 6 páginas; 7,25 s em 28/09". Se a referência for 7,25 s, a função ainda está uns 20% mais lenta que em 28/09; se for os 8,6 s da Lista de bugs, voltou ao que era.

## Ressalvas

1. **A regra da escrita fraca só vale em página com pouca impressão** (menos de 5% de tinta na camada de cima). O próprio código avisa: nota clara pequena numa página cheia de texto ainda some sem aviso. Não achei caso assim no gabarito, mas não procurei no acervo inteiro.
2. **Não conferi a afirmação "nas 1256 páginas nenhuma decisão mudou"** (levaria muito tempo com a máquina dividida). Conferi as 16 do gabarito e as páginas do acervo que abri.
3. A regra da escrita fraca marca como "conferir" também páginas sem nada a perder: as 39 folhas em branco do Siebmacher (decidido) e agora o **Opus Majus 3** (o carimbo da biblioteca).
4. **Palatino 5 intacta e sem aviso:** sai amarela e não é marcada "conferir". Pela regra do 1.1 está certo; pela regra da Fase 1, não. Fica para o 1.5.
5. O retalho preto do scanner na borda do Siebmacher 7, 9, 106, 118 e 124 vem da camada de cima do Internet Archive. Não é o 1.1 que o cria, mas ele aparece no resultado (corte, item 2.13).
6. Não pilotei a janela: o 1.1 ainda não tem botão no programa (a decisão de 29/09 pede o botão de desligar por livro, que ainda não foi feito).

## Bugs para a Lista de bugs

- **29/09, pequeno:** no Opus Majus 20, a beirada de baixo da foto perde até uns 6 pontos (0,35 mm) num trecho de uns 3 cm, com um degrauzinho; nas outras beiradas, 1 a 3 pontos. Só se vê ampliando. `core/camadas.py` (`_onde_branquear`). Print: `v01-opus20-beirada-de-baixo.jpg`.
- **29/09, pequeno:** o papel das zonas mantidas de traço sai branco **levemente azulado** (Palatino 9, dentro do Q: 248, 252, 255; tira entre os fios da moldura do Palatino 12) e com véu cinza (Palatino 67, Rhetorica 38). Mesma família do "em parte" do remendo. Prints: `v07-palatino12-moldura.jpg`, `v11-palatino67-capitular.jpg`, `v09-rhetorica38-meio.jpg`.

## Arquivos

- Esta opinião: `relatorios\conferir\fase1-2026-09-29-0956\verificador\opiniao-do-verificador.html`
- A página de antes/depois: `relatorios\conferir\fase1-2026-09-29-0956\conferencia-fase1.html` (e a da rodada anterior, `fase1-2026-09-29-0851`)
- Os recortes ampliados (v01 a v13) estão nesta mesma pasta.

![](v07-palatino12-moldura.jpg)

![](v08-rhetorica38-alto.jpg)

![](v10-palatino66-titulo.jpg)

![](v11-palatino67-capitular.jpg)

![](v12-siebmacher7-borda.jpg)

![](v13-siebmacher106.jpg)
