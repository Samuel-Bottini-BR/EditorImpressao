### Erro 2 — Números que não batem

**Do que se trata.** São dois números: o "página 132 de 134" e o "(134 páginas)" na janela do Automático, e o sino
(o triângulo de aviso no alto da coluna da direita, com o número de páginas que pedem um olhar).

**O que acontece hoje.**
- **"de 134" e saem 133: ainda acontece.** Com uma página tirada do livro, o Automático continua dizendo 134. A
  janela de salvar, logo depois, diz certo: "133 páginas vão para o PDF, e 1 foi apagada". A barra de baixo da área de
  trabalho também diz "página 133 de 134".
- **O sino que muda sozinho: ainda acontece.** Com o livro aberto do zero, logo depois do Automático, fiz como o
  Kaique ("Qualidade baixa" + "Selecionar todas" + "está bom nas marcadas"): o sino ficou em 25, parado, por dois
  minutos. Depois só andei com a seta para a direita da página 1 até a 41, sem mexer em nada: o sino passou para 26.

![Erro 2](prints/erro2-numeros.jpg)

**Como acontece (o "de 134").** A página tirada do livro continua na lista do programa, só marcada como "não vai para
o PDF" (para dar para trazer de volta). O Automático e a barra de baixo contam a lista inteira; a janela de salvar
conta só as que vão para o PDF. Quem escreveu a conta do Automático deixou de propósito ("para a numeração não mudar
quando uma página é tirada"), mas não escreveu em lugar nenhum que o número inclui a página tirada.

**Como o sino muda sem ninguém mexer.** Um dos avisos, "Endireitar: as contas discordam" (o programa tem duas contas
para saber quanto a página está torta, e avisa quando elas não concordam), é medido de novo quando a página é
desenhada no tamanho do PDF. Esse desenho acontece por trás, sozinho, quando a pessoa passa pela página (ou perto
dela). Se a medida nova discorda, o aviso aparece numa página que não o tinha, e o sino sobe; se passa a concordar, o
aviso some e o sino desce. Na minha rodada, a página nova com aviso foi a 19 (entre as que eu passei). É o que o
Kaique viu (24 → 25 → 28). SINO_RESULTADO

**Defeito ou escolha.** Defeito: o mesmo livro tem dois números diferentes, conforme a tela.

**Situação.** "Consertar" (09/11). Ainda não começou.

### Erro 3 — A miniatura não fica branca depois de "deixar em branco"

**Do que se trata.** É a tira de miniaturas embaixo da área de trabalho, e o botão "deixar em branco" (no painel
Propriedades, em "Esta página"), que põe uma folha branca no lugar da página.

**O que acontece hoje.** Ainda acontece: a página grande fica branca, a miniatura continua mostrando o título.

![Erro 3](prints/erro3-miniatura-branco.jpg)

**Como acontece.** A miniatura mostra a folha como veio do scanner, cortada no lugar da página. Ela só é redesenhada
"como sai no PDF" em dois casos: quando a página foi mudada de lugar ou de tamanho, e quando é uma página em branco
acrescentada à mão (essa sai branca). A página "deixada em branco" não entrou nessa regra. Na grade "Todas as
páginas" acontece o mesmo.

**Defeito ou escolha.** Defeito. Vai contra o que você pediu em 07/11: "O preview as miniaturas tem que estar
sincronizada e o resultado final tem que sair como a edição foi mostrada no preview."

**Situação.** "Consertar" (09/11). Ainda não começou.

### Erro 4 — Textos cortados na barra de baixo (não é urgente)

**Do que se trata.** É a barra do pé da área de trabalho: "página N de M", desfazer, refazer, "Uma página", "Duas
lado a lado", "antes / depois", "marcações", zoom.

**O que acontece hoje.** Ainda acontece na janela do tamanho do notebook do Kaique (1280 x 657) com o painel
Propriedades aberto: "uas lado a lad" e "página 133 de 13". Na janela grande, com o mesmo painel aberto, coube
inteira nesta rodada.

![Erro 4](prints/erro4-barra-cortada.jpg)

**Como acontece.** O painel aberto ocupa a direita, e a barra de baixo fica mais estreita. Os botões não sabem
encolher nem ir para outra linha: quando falta lugar, o Windows corta o texto do botão.

**Defeito ou escolha.** Defeito de tela (o que se aperta continua funcionando; o PDF não muda).

**Situação.** "Consertar" (09/11), no fim da fila, como você disse: "não é urgente".

### Erro 6 — Com a Mão e "Uma página", a folha aparece espremida

**Do que se trata.** Logo depois de dividir o livro no Automático, com a ferramenta Mão escolhida e a vista "Uma
página", a página aparecia com a folha inteira (as duas páginas) apertada na largura de uma.

**O que acontece hoje.** Já não acontece. Na versão de teste de hoje, pelo mesmo caminho, as páginas 1, 2, 5, 8 e 14
aparecem certas com a Mão e "Uma página".

![Erro 6](prints/erro6-folha-espremida.jpg)

**Como acontecia.** Era um desenho errado que a tela mostrava enquanto o desenho certo não chegava: o programa
entregava, por um caminho, a folha inteira como veio do scanner no lugar da página já dividida, e a tela a esticava
para a forma de uma página. Isso foi consertado em 09/11, no conserto do Preto e branco escolhido à mão (a mesma
causa fazia o PDF sair sem o título na página 5, que você testou em 13/11: "funcionando"). Há duas provas automáticas
que guardam isso e as duas passam hoje.

**Ressalva.** Rodei o mesmo caminho também na versão do teste do Kaique (06/11) e lá também não apareceu: o defeito
dependia de quanto o desenho demorava. Por isso a prova do "antes" é o print do próprio Kaique. Ainda há um ponto
fraco: a tela continua esticando, sem avisar, qualquer imagem que chegue com outra forma; se outro caminho entregar a
imagem errada, o espremido volta. Fica anotado na parte da gerente.

**Defeito ou escolha.** Defeito de tela (o PDF saía certo).

**Situação.** Consertado na versão de teste em 09/11. Falta você conferir pelo caminho do Kaique (dividir no
Automático, Mão, "Uma página").

### Erro 8 — Na janela de salvar, o aviso "será substituído" não some

**Do que se trata.** É a janela "Onde salvar o livro pronto", que abre ao clicar em "Confirmar e processar". Quando já
existe um PDF com o mesmo nome na pasta, aparece a faixa "Já existe um arquivo chamado ... Se continuar, ele será
substituído."

**O que acontece hoje.** Ainda acontece: troquei o nome para "rodada-2.pdf" (que não existe) e a faixa continuou
dizendo que o outro arquivo seria substituído. Nada é apagado: o programa só substitui o arquivo que tem o nome
escrito, e pergunta antes.

![Erro 8](prints/erro8-aviso-velho-salvar.jpg)

**Como acontece.** A janela confere o nome em dois lugares. Um aviso pequeno, embaixo do nome, é refeito a cada letra
digitada. A faixa grande só é refeita quando se troca a pasta, nunca quando se troca o nome. Por isso ela fica
falando do nome velho.

**Sua pergunta: "porque aconteceu esse bugue, que regra o agente errou".**
- **Quem fez e quando.** A faixa grande entrou em 08/08/2026, quando o "Salvar em" e o "Nome do arquivo" saíram da
  tela de trabalho e foram para esta janela (um trabalho do Claude daquela época, antes das regras dos agentes). O
  pedido era o seu de 18/07: "avisar se já existir arquivo com o mesmo nome, oferecendo substituir ou renomear". O
  agente ligou a faixa só ao "escolher pasta" e esqueceu o campo do nome.
- **Por que ninguém viu.** O teste que confere a faixa não digita um nome: ele manda a janela se conferir direto, por
  dentro. Por isso passa, e o defeito ficou. Em 25/09, outro trabalho escreveu no código o comentário "a faixa é
  refeita toda vez que o destino muda", o que não era verdade, e ninguém conferiu.
- **Que regra faltou.** Na época, nenhuma. Hoje três regras pegariam: o teste tem que fazer o caminho de quem usa (o
  clique simulado por dentro não vale como prova, 22/09); o conserto tem que passar por todos os caminhos da mesma
  coisa (aqui, mudar a pasta e mudar o nome; regra de 13/11); e todo comentário que diz "isto acontece sempre que..."
  é conferido na hora (regra de 13/11).
- O modelo de pedido aos agentes que você também pediu para ver é da gerente: ela mostra junto com este erro.

**Situação.** "Consertar" (09/11). Ainda não começou.

### Erro 9 — Depois de "tirar do livro", a faixa ainda diz "vai sair em Preto e branco"

**Do que se trata.** A faixa é a tarja logo acima da tira de miniaturas, com uma frase e os botões "está certo" e
"próxima dúvida".

**Sua pergunta: "para que serve, e em que situação é disparado?"** A faixa sempre diz uma frase sobre a página da
vez:
- se a página tem um aviso, mostra o aviso (com os botões para resolver);
- se não tem aviso e você ainda não deu "está certo", mostra uma frase da ferramenta escolhida. Com a Mão, a Zoom, as
  de marcar, o Mover e o Filtro, a frase é "Esta página vai sair em [filtro]": serve para dizer com que filtro a
  página vai para o PDF. Com o Endireitar, diz "Vou endireitar sozinho..."; com o Cortar, "Vou cortar a borda
  sozinho...";
- se a página foi deixada em branco, diz "Esta página vai sair em branco";
- se você já deu "está certo", diz "Página N conferida".
Ela não é disparada por nenhum clique: muda sozinha a cada página e a cada ferramenta.

**O que acontece hoje.** Ainda acontece: a miniatura diz "apagada", e a faixa diz "Esta página vai sair em Preto e
branco." Com o Endireitar escolhido, ela diz "Vou endireitar sozinho...", também errado.

![Erro 9](prints/erro9-frase-depois-de-tirar.jpg)

**Como acontece.** A frase da faixa tem um caso para a página "deixada em branco", mas não tem para a página "tirada do
livro". Quando os dois botões foram postos em toda página (26/10), só um ganhou frase.

**Defeito ou escolha.** Defeito.

**Situação.** "Consertar" (09/11). Ainda não começou.

### Erro 11 — A lista de etapas do Automático volta para o topo

**Do que se trata.** É a lista "Etapas, na ordem" da janela grande do Automático (1 Dividir ... 7 Montar cadernos),
com uma caixinha em cada etapa.

**O que acontece hoje.** Ainda acontece quando a lista não cabe na janela (no tamanho do notebook do Kaique): rolei
até o fim, marquei "6 Margens iguais", e a lista pulou para o topo. O mesmo com "7 Montar cadernos".

![Erro 11](prints/erro11-lista-volta-ao-topo.jpg)

**Como acontece.** Cada vez que qualquer coisa muda no Automático (uma caixinha, uma opção), a lista é apagada e
montada de novo, do começo. Montada de novo, ela volta para o alto. O clique seguinte cai na etapa que estiver
naquele lugar (no teste do Kaique, "Cortar as bordas").

**Defeito ou escolha.** Defeito. Acontece também no painel Automático da direita, que usa a mesma lista.

**Situação.** "Consertar" (09/11). Ainda não começou. A sua ideia da ferramenta que descreve tudo sem precisar de
foto foi para a Lista de espera.
