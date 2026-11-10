# Testes guiados — sessão 5 (10/11/2026)

## Cantinho do giro (D-639), Destino do socialismo

Palavras dele (prints 01 e 02, 08h31): "1- apareceu um aviso 2- cliquei nele, era para fazer isso?"

- Print 01: página 18 de 193 (texto da página 10 do livro), ferramenta Endireitar, "Desentortar perto da lombada" =
  "Pelas margens de cima e de baixo"; aviso "O desentortar empurrava o texto para fora da página [...] Por isso a página
  saiu sem desentortar" com "Desentortar aumentando a página" / "está bom assim" / "está certo". É o aviso esperado
  (a página segurada, como no teste de 06/11).
- Print 02: depois do clique, a página aparece maior, o aviso sumiu ("0 com dúvida") e ele circulou a beirada esquerda.

Destino: a gerente pergunta qual botão foi clicado e o que ele viu na beirada circulada.

Respostas dele sobre o que circulou: "um pedaçõ da pagina de fora" · "e a parte que o programa pintou".

Destino:
- A gerente ampliou a beirada (prints 01b e 02b). Antes do clique (01b) a beirada está limpa, da cor do papel. Depois de
  "Desentortar aumentando a página" (02b) aparecem uma faixa clara pintada pelo programa, de outra cor que o papel, e um
  pedaço da beirada da página de fora; o aviso "A página ainda saiu deformada" não apareceu.
- Defeito novo na **Lista de bugs** do PLANO-DEFINITIVO (10/11), nas duas cópias. Não é o conserto do cantinho (D-639),
  que vale para a página sem desentortar (print 01).

## Manchas pretas nas laterais no Preto e branco (prints 03 e 04, 08h33 e 08h35)

Palavras dele: "deixe anotado, hoje não temos como reconhecer essa partes que são marcas da folha ou folha meio dobrada ou manchas na folha que quando vão para o preto e branco fica essa mancha, o ocr está funcionando? porque era para ele preservar as letras e passar e deixar a folha branca, acho que ainda não chegamos no padrão do wikipedia."

Destino: **Lista de bugs** (10/11), ligada aos itens 1.4 e 1.5 da Fase 1 (não feitos). O OCR (docTR) hoje só acha as
linhas do texto para endireitar; o Preto e branco não usa o OCR.

## Endireitar, canto de cima (print 05, 08h38)

Palavras dele: "eu vim no endireitar" (círculo no canto de cima à esquerda, zoom 244%).

Destino: a gerente ampliou (05b). O canto de cima está fora da tela por causa do zoom, e a página está com inclinação
0,00 graus: sem giro não há cantinho. Explicado no chat: girar à mão (ex.: 1,5 grau com os botões de 0,1°) e olhar os
quatro cantos com "ajustar à tela".

## Pesquisa do Internet Archive (ordem dele, 10/11)

Palavras dele: "eu errei é internet arquive, sim é isso que temos que fazer, coloque um agente para fazer pesquisas de como eles fazem por favor." · sobre o cantinho: "usei ele, mas continua sem ver esse tal cantinho que você"

Destino:
- Agente pesquisador chamado (10/11): como o Internet Archive deixa a letra preservada e o papel branco, o que serve para
  nós no Windows, licenças. Entrega em `docs/pesquisa/fase1-1.4-como-o-internet-archive-faz.md` e
  `relatorios/pesquisa-internet-archive-2026-11-10/`.
- Cantinho: explicado no chat que, com o conserto, ele fica da cor do papel e não aparece; a página 18 está a 0,00 grau
  (sem giro, sem cantinho). Oferecida uma prova antes/depois no modelo do girar (esperando o "sim").

## Girar à mão: cor do cantinho e lentidão (print 06, 08h41)

Palavras dele: "acho que pode ser branca mesmo, só achei muito lento para fazer o carregamento quando eu giro, tinha que ser tão rápido quanto o photoshop, será que isso tem haver com a gente usar phyton e não outra engine para nosso programa? mudar a linguagem pode aumentar a velocidade do programa?"

Destino:
- Cor do cantinho: "acho que pode ser branca" muda a D-639 (hoje: cor do papel). A gerente pergunta antes de mudar.
- Lentidão do giro: **Lista de bugs** (10/11), para a Fase 5. Resposta sobre a linguagem no chat.

## O giro leva o branco junto (print 07, 08h44)

Palavras dele: "o jeito também como ele gira, olha só, não é que nem o photoshop que vira só a imagem dele, ele gira até a parte branca da area de trablho junto."

Destino: acrescentado ao item da lentidão do giro na **Lista de bugs** (10/11).

## Cantinho: a prova de 06/11 aberta na tela dele (09h)

Palavras dele: "Não estou achando esse cantinho, por favor abre a tela do meu pc e faz o teste para eu ver" · "eu quero que seja rapido" · "você não viu minha resposta na central, pois eu respondi essa foto ai." · "a cor é diferente da cor do papel."

Destino:
- A gerente abriu `relatorios/cunha-desentortar/destino18-direita-antes-depois.png` (ramo obra) na tela dele. Não há
  ferramenta de controlar o mouse nesta conversa.
- A resposta dele na Central (`cantinho-outros-casos`, 09/11 19h18, "Ainda não entendi": "esse teste é totalmente
  inconslusivo para mim, não consigo ter visão clara do que o programa tentou fazer, ou de qual problema ele tentou
  reslver.") não tinha sido lida. A pergunta vai ser refeita no modelo do girar (D-639 e os casos que ficaram brancos).
- "a cor é diferente da cor do papel": no "depois", o creme pintado é mais claro que o papel ao lado. Vai na pergunta
  refeita, como defeito da D-639.
- "eu quero que seja rapido": sem saber se é o giro na tela ou o teste; perguntado no chat.

## O giro aparece cortado (print 08, 08h47)

Palavras dele: "olha como fica ruim esse girar, não consigo ver direito o que está girando porque fica cortado então não consigo voltar direito para como estava."

Destino: acrescentado ao item do giro na **Lista de bugs** (10/11).

## Cantinho: não é urgente (10/11)

Palavras dele: "olha essa questão do canto não é urgente, pode deixar como branco por enquanto."

Destino: **D-664** (fica como está, nada muda no programa) e **Lista de espera** (refazer a pergunta no modelo do girar).
Central `cantinho-outros-casos` respondida.

Correção dele sobre o print 08: "esse print você leu errado, o que eu quis mostrar é que quando eu estou com a pagina fora da area de trabalho e vou girar ela novamente para dentro, enquanto eu estou girando ela continua com aquela parte que estava para fora cortada, e fica dificil de visualizar o que realmente vai ficar dentro da area de trabalho."

Destino: texto do item corrigido na **Lista de bugs** (as duas cópias).

## Quadrados brancos no Melhorar e no Mágico pro (prints 09 e 10, 08h53 e 08h55)

Palavras dele: "anotar erro do filtro melhorar, ele deixa a imagem pixelada, olha esses quadrados brancos. também acontece no automatico e no magico pro, pode colocar um agente para investigar isso."

- Print 09: *Na escola de Jesus*, página 13 (Jonas e a baleia), Melhorar, "Clareza do fundo: bem forte", "Respeitar as
  gravuras achadas" marcada: quadrados brancos nas partes claras da gravura.
- Print 10: janela do Automático, Mágico pro "bem fraco", mesma página: os mesmos quadrados no "depois".

Destino: **Lista de bugs** (10/11). Agente investigador: pedido; entra quando um dos 2 agentes de agora terminar (limite de 2).

Mais uma frase dele: "o erro não aparece só na pagina 13, aparece em varias." Destino: repassada ao agente investigador
(medir o livro inteiro).

## Gravura à mão e "Pular" (D-659, D-661)

Palavras dele: "fiz os dois testes que você pediu e estão funcionando."

Destino: Livro de decisões, D-659 e D-661 "testadas pelo Samuel em 10/11, funciona".

## Testes do Dividir e do Automático (prints 11, 12 e 13, 09h02 a 09h08)

Palavras dele (os números são os da lista de testes da gerente):
"10- print 1 - quanto eu mudo uma folha de lugar ela começa a recarregar novamente
3- em páginas que já vieram separadas no pdf não acontece nada
4- ok
5- print 2 - não existe um botão para juntar só duas paginas que acabaram de ser juntas, só dá para juntar todas
6- eu não consegui testar por causa da 5
7- sim
print 3 - clicar nas caixinha de selecionar é dificil as vezes preciso de 5 cliques para conseguir.
8- não passou, mas não é um erro grave, pode ficar para depois
9- funciona"

Destino (Livro de decisões, coluna de situação, e Lista de bugs):
- 3 (D-590/D-607): no livro com páginas já separadas no PDF, "juntar todas" não faz nada.
- 4 (D-602/D-609): ok. 7 (D-608): funciona. 9 (D-611/D-612): funciona.
- 5 (D-606): ele não achou o botão de juntar uma folha só; esse botão é o "não dividir esta" (print 12). 6 (D-613): não testado.
- 8 (D-610): não passou, para depois (**Lista de bugs**).
- 10 (D-615): a página recarrega ao mudar a folha de lugar (print 11, **Lista de bugs**).
- Caixinhas do Automático difíceis de marcar (print 13, **Lista de bugs**).

## Central: o Quadro dos trabalhos rolava de lado (print 14, 09h12)

Palavras dele: "arrumar, para passar para o lado eu tenho que ir lá embaixo na barra, e dai eu não consigo ler enquanto passo a barra, bota um agente para resolver isso."

Destino: feito pela gerente (os dois agentes estavam ocupados), Central **versão 41**: no PC as colunas do Quadro descem
para a linha de baixo quando não cabem; as abas também quebram em duas linhas em vez de rolar; as Etapas cabem sem
rolar. Testado em 1366, 1000, 800, 700, 360 e 300 px, todas as 9 abas: nada passa da borda.

## Quadrados brancos: investigação pronta (agente, 10/11)

Causa: o último passo do Melhorar e do Mágico pro (`core/filtros.py`, `_limpar_o_papel_de_verdade`) pinta de branco o que
parece papel; a água, o céu e roupas claras passam, e os blocos vêm dos quadradinhos do JPEG do livro. Sai igual no PDF.
110 páginas (Melhorar) e 112 (Mágico pro) no *Na escola de Jesus*; também Livro de Horas 47. Relatório:
`relatorios/quadrados-brancos-2026-11-10/relatorio.html` no ramo `obra-2026-10-26` (commit `36e0b3b2`).

Destino: 2 perguntas na Central, Conferência → "Quadrados brancos no Melhorar e no Mágico pro: 2 perguntas (10/11)".

Palavras dele: "mas como assim , o que parece papel para ele, não estamos usando o scantailor?" · "faça um teste com os dois para ver qual se sai melhor."

Destino: explicado no chat (o ScanTailor divide, endireita, desentorta e acha as gravuras; o Melhorar e o Mágico pro são
nossos e, à mão, não rodam o detector). O agente compara A (regra "em volta é papel"), B (detector do ScanTailor no
Melhorar e no Mágico pro) e C (os dois), no livro inteiro, Livro de Horas 47, gabarito, Boécio e velocidade.
