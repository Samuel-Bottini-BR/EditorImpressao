# Causas dos erros do Lusíadas e plano de cada conserto (implementador, 17/11/2026) — onde parei

Tarefa de **investigação**: achar a causa de cada erro e escrever o plano do conserto. **Nenhuma linha do programa
muda.** Quem pediu: a gerente, com as 13 respostas do Samuel de 17/11 na Central (`agente-causas.json`).

- Cópia: `.claude/worktrees/causas-lusiadas`, ramo `causas-lusiadas-2026-11-17`, a partir de `obra-2026-10-26`
  (`a9d81030`). Junção `modelos` (PowerShell `New-Item -ItemType Junction`).
- Base do estudo: ramo `lusiadas-provas-2026-11-14` (`0bd75b41`), relatório e ONDE-PAREI em
  `relatorios/lusiadas-provas-2026-11-14/`. Investigações vizinhas: `quadrados-capa-2026-11-13` (capa do Gradus),
  `quadrados-origem-2026-11-10` / `quadrados-c-2026-11-10` (quadrados do Melhorar e do Mágico pro, D-668).
- Prints do Lusíadas: `prints/` desta pasta, **fora do git** (direito autoral).
- Nada na tela do Samuel: só conta sem janela ou `QT_QPA_PLATFORM=offscreen`. Pasta de dados própria.

## Decisões que esta tarefa precisa cumprir (palavras dele)

- D-691: "eu quero ver esses erros, as provas dele e uma explicação de como acontece, explique de forma simples. quero
  antes de dar inicio."
- D-678 (p. 14, remendos): "tem que verificar o que aconteu". Comentário de 17/11: "Quero entender porque isso
  aconteceu. porque esses pedaços brancos estavam aparecendo também no melhorar e no magico pro e também apareceram em
  outros livros, como no Gradus primus que ele apaga um quadrado da parte superior da capa azul do livro."
- D-679 (números): 17/11: "Mudou sozinho porque ele procurou e achou mais defeitos? numero está errado por causa de
  alguma confusão que o programa está fazendo, provavelmente uma gambiarra o motor de contagem deveria valer para todo o
  programa e não fazer uma conta em cada lugar um motor para paginas e um para folhas( lembrando que eu não lembro a
  diferença entre as duas), Quero entender também o porque desse erro."
- D-680 (miniatura em branco): 17/11: "Quero saber porque isso acontece."
- D-681 (barra cortada): "não é urgente."
- D-682 (página deitada): 17/11: "Quero saber porque saiu deitado? o programa aplicou o girar? é um defeito do
  programa ou do agente que fez esses testes?"
- D-684 (laranja com a Mão): 17/11, opção 2 ("o botão "marcações" manda também no laranja") · "Quero entender porque
  este bug está acontecendo. Segundo, onde aparece essas marcações, vemos claramente alguns defeitos nas gravuras,
  vemos manchas brancas."
- D-685 (aviso de salvar): 17/11: "Quero saber porque esse problema acontece."
- D-686 (frase depois de tirar): 17/11: "Depois que tira uma pagina do livro, ela tem que sumir das miniaturas, ela só
  continuaria existindo se tivessemos deixado ela em branco ou simplismente excluido o conteudo dela."
- D-687 (código na tela): "Não se deve usar código na nomeação de coisas." · 17/11: "além disso tem que rever as regras
  dos agentes para que eles não cometam mais esse erro."
- D-688 (lista volta ao topo): 17/11: "pode consertar, mas quero saber o motivo desse erro, pois isso é um gambiarra né."
- D-528 (marcações ao dividir): 17/11, "Concordo, fica assim" · "Mas tem que ver se não tem gambiarra nessa decisão, e
  nessa função."
- D-689 (p. 22): 17/11, só comentário: "Gostaria de saber como seria esse conserto, por enquanto poderia ter só um
  aviso né? Seria possivel criar uma IA só para parte de avisos do programa?"
- D-690 (p. 8): 17/11, só comentário: "explique melhor como vai funcionar a opção 3."
- Regras: CLAUDE.md §11.12 (sem gambiarra: causa, regra da ferramenta, todos os caminhos), §11.13 (como escrever para
  ele), §10 (modelo de print do girar), §4.10 (caminho inteiro), §3 (rede neural só aponta, nunca desenha), §11.7 (só o
  que ele mandou), D-605 (o novo não estraga o testado).

## O que já está escolhido e testado aqui

Nada é mexido (só leitura). Ao propor cada conserto, cito as decisões e provas que ele não pode mudar (na seção de cada
item, "não pode mudar").

## Como fica para quem usa e no livro

Nada muda nesta tarefa: não há código. Em cada plano de conserto digo o que muda para o Kaique e no PDF.

## Plano da investigação

1. [ ] Ler regras, Central, estudo de 14/11, Livro (feito ao começar).
2. [ ] Remendos e pedaços brancos (lu-1, lu-7 parte 2): decompor a marcação da p. 14 e da p. 8 (de onde vem cada
   pedaço: leitor de texto, ScanTailor, sobra de tinta, papel); rodar Melhorar e Mágico pro na p. 14 pelo caminho
   inteiro; ligar com o Gradus (estudo de 13/11) e com a D-668.
3. [ ] Números (lu-2): todas as contas de "páginas" e "folhas" do programa; o sino.
4. [ ] Miniatura em branco (lu-3), frase (lu-9), barra (lu-4), aviso de salvar (lu-8), lista (lu-11), códigos (lu-10).
5. [ ] Página deitada (lu-5): de onde vem o giro na montagem.
6. [ ] D-528: ler a função de dividir com as marcações.
7. [ ] lu-12 e lu-13: explicar o conserto e a opção 3 com o caso real.
8. [ ] Prints novos no modelo do girar onde a resposta pede imagem.
9. [ ] "Respostas para a Central", uma por item.

## Andamento

(abaixo, a cada passo)

### Passo 2 (lu-1, lu-7): feito — o que achei
- `scripts/decompor_marcacao.py` (procura a marcação de novo, espiando por dentro) → `decompor_marcacao.json`; imagens
  em `prints/decompor/` (fora do git).
- P. 14: o leitor de texto NÃO viu texto na página (só uma caixa "figure"). Os dois pedaços azuis ("letra") são
  buracos da pintura do ScanTailor (ele deixou de fora as partes escuras e lisas: a nuca do homem da frente e o casaco
  do da direita). A regra `letra = (letra_layout | blocos_de_tinta(sobrou)) & ~gravura` (core/detectar_regioes.detectar)
  chama de "letra" toda tinta que sobrou fora da gravura, sem conferir se parece escrita. O mesmo pedaço sai remendo
  nos três filtros: Preto e branco (1 bit), Melhorar e Mágico pro (cinza chapado, com pontinhos brancos na beirada).
- P. 8: igual, mais os pedaços do céu e do mar que sobraram viram "papel" (branco).
- `scripts/pedacos_de_letra.py` → `pedacos_de_letra.json`: os pedaços remendo (p. 14 e o mar da p. 8) dão
  "não parece escrita" na régua que o detector já tem (`_parece_escrita`) e encostam na gravura; os blocos de texto da
  p. 2 dão "parece escrita" e não encostam. Medida em poucas páginas: o conserto precisa medir no gabarito.
- Ligação com o Gradus (estudo de 13/11, ramo quadrados-capa): lá o pedaço "ÓNAI" veio de outra porta (caixa de texto do
  leitor, regra "a escrita ganha", `ESCRITA_GANHA_DO_SCANTAILOR`) e o branco do passo da sombra em quadros do Preto e
  branco (D-700, suspensa). Os quadrados do Melhorar e do Mágico pro na Escola eram a limpeza do papel (D-668, consertado
  13/11, testado por ele: "funcionando").
