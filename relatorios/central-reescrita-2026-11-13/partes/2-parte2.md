## Parte 2: a aba "Revisão dos nomes" (20 perguntas mudaram)

Arquivo: `novas/nomes-28-10.json` (as 20; o resumo da aba também, que tinha "D-374", "D-365"
e caminhos de arquivo).

**Em todas:**
- A primeira frase diz onde o botão fica e o que ele faz ("Do que se trata").
- Depois, por que o nome confunde, com o caso real e as palavras do Kaique.
- Depois, de onde veio, com data e palavras dele. Saíram os números de decisão, os códigos de rodada (`pr-esta-bom`,
  `b-11-nome`, `fr-26`...), "etapa 9a/9b-1" e "escolha da gerente" (agora: "escolhido pela gerente, sem perguntar a
  você", regra 9).
- No fim, a mesma frase de situação: nada mudou; o que o botão faz não muda; o nome escolhido entra junto com a
  arrumação nova do layout, como ele pediu em 04/11 ("Isso deveria ser feito junto com a repaginação do layout [...]
  o agente não vai escolher os nomes ele pode sugerir opções"). Isso não estava dito e é regra 10.
- Cada pergunta tem duas sugestões de nome, "Deixar como está" e "Ainda não entendi" (ids mantidos). A sugestão
  passou para o campo "sugestão", com o porquê em uma frase.
- **Conferido no programa de hoje** (busca dos textos de tela em `ui/` e `core/`): todos os nomes citados continuam
  lá. Únicas diferenças: o subtítulo da etapa agora é "tira o amarelado" (minúsculo); o "Show Details..." da Lista de
  atalhos é o botão que o próprio Qt põe (vem do `setDetailedText`), não um texto escrito no código.

### As três que voltaram com "não entendi"

**nm-desligar-marcadas** — ele: "Eu não entendi o que você quis dizer." (13/11)
- O texto antigo dizia o que o botão faz só em palavras ("o programa deixa de fazer sozinho..."). Agora diz que ele
  **desfaz** o que o Automático fez nas etapas marcadas, e mostra.
- **Print novo** `nm-desligar-marcadas-resumo.png` (Gradus, cópia, hoje): azul, depois do Automático só com
  "Dividir folhas ao meio" (140 páginas); verde, depois de "desligar as marcadas" (as folhas voltam inteiras; a
  caixinha da etapa fica desmarcada; na tira, a metade que sobrou aparece como "apagada"). Conferido pelo Histórico:
  "Automático desligado: dividir folhas ao meio".
- As opções viraram "desfazer estas etapas" e "tirar o automático das etapas marcadas" (ids `estas-etapas` e
  `nao-fazer` mantidos; ele não tinha escolhido nenhuma).
- **Achado no print (não é desta pergunta):** depois de desligar o Dividir, a barra de baixo continua "página 11 de
  140" e a tira mostra "apagada" no lugar das metades. Pode confundir o Kaique; não investiguei.

**nm-jeito-pb** — ele: "Ainda não entendi" (13/11), sem comentário.
- Agora explica primeiro o que é a lista (maneiras de decidir o que vira preto e o que vira branco) e por que
  "Sauvola", "Otsu" e "Wolf" não dizem nada (são sobrenomes dos inventores).
- **Print novo** `nm-jeito-pb-resumo.png`: a lista (print de 28/10) e a mesma página do Palatino (cópia, página 9),
  desenhada pela conta do PDF com cada jeito, o mesmo pedaço aumentado. Aviso honesto na imagem: nesta página a
  diferença é pequena (a moldura da direita e a grossura das letras). O "Automático" escolheu o Sauvola nela.
- Segunda opção (`so-padrao`) ganhou o texto que faltava.

**nm-tela-livros** — ele: "Suas respostas ainda não são claras, tem que rever isso, não consegui entender, tem que
ser de fácil entendimento." (13/11)
- O texto antigo juntava três assuntos num parágrafo só. Agora são três itens numerados (1. tirar da lista;
  2. achar o PDF que mudou de pasta; 3. "projeto" no lugar de "livro"), e a imagem tem uma faixa para cada um.
- **Imagem nova** `nm-tela-livros-resumo.png`, montada com os quatro prints de 28/10 (os textos continuam iguais no
  programa de hoje).
- A opção `so-botoes` ganhou o texto que faltava.

### As outras 17 (reescritas no mesmo formato, sem print novo; os prints de 28/10 continuam)
- **nm-codigos:** ele já decidiu em 09/11 ("Não se deve usar código na nomeação de coisas"; mandou consertar). A
  pergunta agora diz isso, diz que está na fila, e pergunta só o que falta (tirar só o código ou a frase da regra). A
  opção "Deixar como está" ficou (o id não sai), mas avisa que é contra o que ele decidiu. Conferi hoje: os três
  códigos ainda estão na tela.
- **nm-montar-nomes:** tirei das opções o "Folhas de (0 = todas)" e o "Páginas do livro de (0 = todas)", porque ele
  já decidiu em 08/11 a caixinha "Imprimir só algumas folhas" (regra 10: não perguntar de novo).
- **nm-montar-frases:** diz com todas as letras que as frases foram escolha de agente, sem pedido dele.
- **nm-dois-mover, nm-desligar-marcadas:** dizem que o nome foi escolhido pela gerente, sem perguntar.
- Opções que estavam sem texto ganharam texto: `aumentar` (nm-dois-mover), `nao-fazer`, `so-padrao`, `so-botoes`.
- **nm-esta-bom, nm-antes-de-processar, nm-folha-pagina, nm-nao-esta, nm-limpar-a-folha, nm-scantailor, nm-tirada,
  nm-frase-salvar, nm-historico, nm-menu-marcar, nm-manter-cor-tinta, nm-montar-dois, nm-atalhos:** mesmo conteúdo,
  no formato novo; nomes de decisão e de rodada tirados do meio do texto.

### Fatos que não consegui confirmar (Parte 2)
1. Os números dos exemplos (54 avisos, 8 páginas, "6 páginas", "12 das 50") são dos prints e testes de 26-28/10;
   não refiz as contas hoje.
2. Se o Kaique ainda vê "Show Details..." em inglês: depende do Qt instalado no notebook dele; no PC, conferi só no
   código que a lista vem pelo "detalhe" da caixa de mensagem.

