### Erro 1 — Remendos pretos e brancos nos rostos (página 14)

**Do que se trata.** É a página 14 do Lusíadas, a pintura dos homens de chapéu com os barcos ao fundo. No PDF, o peito
do homem da direita e a cabeça do homem da frente saem com retângulos pretos e brancos duros, como remendos.

**O que acontece hoje.** Ainda acontece, igual ao teste do Kaique.

![Erro 1](prints/erro1-remendos-p14.jpg)

**Como acontece.** Quando a página está em Preto e branco, o programa primeiro procura o que é pintura e o que é letra.
A pintura ele deixa em cinza; a letra ele passa para preto e branco puro. Nesta página ele achou a pintura quase
inteira (verde na imagem do meio), mas tomou dois pedaços dela por letra (azul). Nesses dois pedaços a pintura vira
preto e branco de texto: são os remendos.

**Defeito ou escolha.** Defeito do programa: quem marcou "letra" no meio da pintura foi a procura automática. A
caixinha "Gravuras em tons de cinza" não resolve (faixa laranja).

**De onde veio.** Da procura de letra e pintura que o programa faz sozinho, ligada desde o começo de outubro.

**Situação.** Você escolheu "Consertar" em 09/11. Ainda não começou: espera o seu sim, um erro por vez.

### Erro 5 — Página que sai deitada no arquivo para imprimir

**Do que se trata.** É o arquivo que sai de "montar para imprimir em A4" (na tela de "Ficou pronto!"), com o Livreto
de fábrica: duas páginas de cada lado de uma folha A4 deitada.

**O que acontece hoje.** Ainda acontece. Nesta rodada foi a página 3 (a folha de rosto), que saiu deitada na face 3.
Na folha 7, a do Kaique, o corte caiu de novo no meio do título "PERIGOS E TRAIÇÕES".

![Erro 5](prints/erro5-pagina-deitada.jpg)

**Como acontece.** São duas coisas em fila.
1. Na folha que tem só uma página impressa (a outra metade em branco), o Dividir não acha a dobra e corta fora do
   meio. Ele mesmo avisa "Não tenho certeza de onde cortar" (folhas 2 e 7). Uma das páginas fica mais larga que alta.
2. Na montagem, toda página mais larga que alta é girada de lado para caber na metade da folha A4. O programa escreve
   um aviso ("Página 3: era deitada e foi girada de pé e diminuída"), mas só depois de gravar, lá embaixo, fora da
   vista. Antes de gravar não aparece nada.

**Defeito ou escolha.** As duas coisas. O corte errado é defeito do Dividir, mas ele avisou, e o Kaique (como no
teste) disse "continuar assim mesmo". O giro escondido é defeito: o aviso existe e ninguém vê.

**De onde veio.** O girar sozinho e o aviso são do "montar para imprimir" (22/10); o aviso nasceu do seu pedido de
20/10 ("Quero que o programa avise quando isso estiver acontecendo"), mas ficou só depois de gravar. A sua pergunta de 09/11 já foi respondida na
Central: dá para arrastar a linha só naquela folha, e o resto fica como o Automático fez.

**Situação.** "Consertar" (09/11). Ainda não começou.

### Erro 7 — Marcações laranja à vista com a Mão

**Do que se trata.** A Mão é a última ferramenta da coluna da esquerda (o desenho de uma mãozinha, logo abaixo da
lupa). Ela serve só para olhar a página e arrastá-la quando está ampliada; não muda nada. Os contornos laranja são
o programa mostrando onde ele achou letra e pintura.

**O que acontece hoje.** Ainda acontece: com a Mão escolhida e o botão "marcações" desligado, os contornos laranja
continuam em volta do texto e da pintura.

![Erro 7](prints/erro7-laranja-com-a-mao.jpg)

**Como acontece.** Existem duas coisas diferentes na tela, e elas seguem regras diferentes:
- as cores das marcações (o rosa, o azul...): seguem o botão "marcações", e esse obedece o que você decidiu em 29/10
  (some com a Zoom e com a Mão);
- os contornos laranja ("Mostrar as áreas achadas"): você pediu em 08/10 que "no para revisar, elas já vão aparecer
  laranjas". O programa liga esse laranja sozinho em toda página que tem aviso, com qualquer ferramenta. Logo depois
  do Automático quase todas as páginas têm aviso, então quase todas ficam com laranja.

**Defeito ou escolha.** As duas regras foram pedidas por você, e elas se cruzam. Não é um defeito de conta: falta
dizer qual vale quando as duas batem.

**O que você escolhe.**
- **Opção 1 — a Mão e a Zoom escondem também o laranja** (a página limpa, como vai sair). O laranja aparece com as
  ferramentas de marcar, e com a caixinha "Mostrar as áreas achadas". Muda o que você pediu em 08/10 só para a Mão e a
  Zoom.
- **Opção 2 — o botão "marcações" passa a mostrar e esconder o laranja também.** Um botão só para tudo o que é
  marcação; desligado, nenhuma cor e nenhum contorno.
- **Opção 3 — fica como está** (laranja sempre nas páginas com aviso).
- Sugestão da verificação: opção 2 (um botão só, que você já conhece). Nada mais do que já funciona muda.

**Situação.** "Consertar" (09/11), mas precisa desta escolha antes.

### Erro 10 — O código "(G2)" na tela

**Do que se trata.** Na janela do Automático, na etapa "1 Dividir folhas ao meio", embaixo de "Motor de corte", está
escrito "Livro novo não divide sozinho: só quando esta etapa roda (G2)".

**O que acontece hoje.** Ainda acontece.

![Erro 10](prints/erro10-codigo-g2.jpg)

**Como acontece.** "G2" é o nome que a sua pergunta tinha numa conferência antiga (05/10). Quem escreveu o texto da
tela copiou o código junto.

**Onde mais tem código na tela.** Procurei em todos os textos do programa. Além do "(G2)", há dois em balões (o
texto que aparece quando o mouse para em cima):
- no botão "desligar as marcadas" do Automático: "(D-068: toda função automática liga e desliga)";
- na lista "Quando o ângulo muda depois do corte à mão, o corte:" (etapa Endireitar do Automático): "D-094: a mesma
  escolha existe nas Configurações...".

**Defeito ou escolha.** Defeito: contra a sua regra "Não se deve usar código na nomeação de coisas". Os três entraram
juntos em 26/10, na obra.

**Situação.** "Consertar" (09/11). Ainda não começou.

### Erro 12 — Página 22 quase em branco sai suja (investigar)

**Do que se trata.** É a página 22, o verso de uma folha que não tem nada impresso; só se vê, bem fraquinho, o texto
da outra face por transparência. No PDF ela sai com tracinhos pretos pela página toda e um bloco preto embaixo.

**O que acontece hoje.** Ainda acontece.

![Erro 12](prints/erro12-pagina-suja-p22.jpg)

**Sua pergunta: defeito ou escolha das ferramentas?** As duas coisas, mas o principal é defeito.
- **O defeito:** o Preto e branco tem jeitos diferentes de decidir o que é tinta. De fábrica, o programa escolhe
  sozinho o jeito de cada página. Numa página sem tinta, ele mede as manchinhas do papel como se fossem letra grossa e
  escolhe o jeito de letra grossa. Esse jeito sempre acha "tinta" em algum lugar: separa o papel em dois tons e pinta
  o mais escuro de preto. Com o jeito de sempre (o de letra fina), a mesma página sai toda branca (faixa laranja).
  Medido: 10,7% da página em preto no jeito que o programa escolheu; 0% no outro.
- **A escolha:** o programa avisou "Parece em branco" nessa página, e o aviso estava certo. Se o Kaique apertasse
  "deixar em branco", a página sairia branca. Mas ninguém deveria precisar disso para não sair sujeira.

**De onde veio.** A escolha sozinha do jeito de preto é antiga (setembro, antes do plano de 24/09); o jeito de
letra grossa existe por causa das letras góticas pesadas (Graduale, Palatino).

**Situação.** Você pediu "investigar antes" (09/11). Investigado: é defeito. O conserto espera o seu sim.

### Erro 13 — A pintura das bandeiras quase some (página 8) (investigar)

**Do que se trata.** É a página 8, a pintura das bandeiras e dos navios. No PDF quase tudo vira branco, com riscos
soltos.

**O que acontece hoje.** Ainda acontece.

![Erro 13](prints/erro13-pintura-p8.jpg)

**Suas perguntas.**
- **"a gravura foi achada?"** Sim. O programa achou a pintura (verde na imagem do meio), mais da metade da página.
- **"mau uso ou bugue?"** Defeito do programa. Depois de achar, ele decide se é pintura (sai em cinza) ou desenho de
  traço (sai em preto e branco, só as linhas). Aqui ele errou: tomou a pintura de pincel, clarinha, por desenho de
  traço, e o cinza claro foi para branco. Também marcou pedaços do céu e do mar como papel, que vão a branco.
- **Tem jeito hoje?** Tem: a caixinha "Gravuras em tons de cinza" (no Preto e branco, painel "Filtro da página" e
  Automático), que você aprovou em 01/11. Com ela, a página sai inteira em cinza (faixa laranja). Ela vem desmarcada, e
  o Kaique não tinha como saber que precisava dela nessa página.

**De onde veio.** É da mesma família do defeito que você aceitou deixar para depois em 29/10 (pintura confundida com
enfeite no *Na escola de Jesus*). A sua ideia de 09/11 (o aviso com as marcações para aumentar, diminuir ou trocar o
filtro só naquele pedaço) foi para a Lista de espera, na Fase 3.

**O que você escolhe (para quando o conserto começar).**
- **Opção 1 — consertar a conta** que separa pintura de desenho de traço, para a pintura clara de pincel sair em cinza
  sozinha. É conserto de imagem: precisa ser medido em outros livros antes, porque a mesma conta decide as gravuras de
  traço (que devem continuar em preto e branco).
- **Opção 2 — o programa avisar** nas páginas onde ele achou a pintura e a transformou em traço, com o botão
  "Gravuras em tons de cinza" no próprio aviso (a caixinha já existe; só passa a ser oferecida na hora certa).
- **Opção 3 — as duas.**
- Sugestão da verificação: opção 3, começando pela 2 (mais rápida e não muda nenhuma outra página).
- Nada do que já funciona muda na opção 2; na 1, as gravuras de traço precisam ser conferidas de novo.

**Situação.** Investigado: defeito. O conserto espera o seu sim.
