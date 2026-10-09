# Respostas do Samuel, 09/10/2026 (literais)

O Samuel avisou no chat: "respondi tudo".

## Página de escolhas (https://claude.ai/artifact/EJoJq5mocxi3vbNxU8ZecV)

Lida da coleção `respostas` em 09/10/2026 (respondidas às 15:47 e 15:49, horário de Brasília):

- **"Endireitar antes de cortar (como o ScanTailor): pode começar?"** (`g6-endireitar-antes`): **Pode começar**, sem comentário (respondido em 09/10/2026, 15:47).
- **"Num livro novo, se você mudar o ângulo depois de ajustar o corte à mão, o retângulo do corte fica no mesmo lugar da página reta (como no ScanTailor) ou acompanha o texto?"** (`g6-retangulo`): **Ainda não entendi**, com o comentário (respondido em 09/10/2026, 15:49):

  > eu não entendi, me de mais exemplos e explique melhor.

### O que a gerente fez (09/10)

- `g6-endireitar-antes`: o implementador do endireitar recomeçou o G6 em 09/10 (ramo `fase2-endireitar-2`), com o plano da PARTE -13 §2 do resumo.
- `g6-retangulo`: a pergunta foi refeita na própria página (regra 10 do `CLAUDE.md`). O comentário dele subiu para o campo `historico` (fixado no alto da pergunta) e a resposta foi esvaziada, para a pergunta voltar a ficar aberta. A pergunta nova traz:
  - uma frase simples do que está sendo perguntado e o passo a passo de quando acontece (o programa endireita; o Kaique ajusta o corte; depois muda o ângulo; e o retângulo?);
  - um aviso de que, se o ângulo for mudado antes do corte, a pergunta nem aparece;
  - três exemplos desenhados, cada um com "o corte que você fez", "Fica no mesmo lugar" e "Acompanha o texto" lado a lado, com uma lupa no canto que importa e uma frase do que o Kaique veria e faria:
    1. o ângulo muda pouco (0,3°), o caso mais comum: o canto anda meio milímetro; tanto faz;
    2. o ângulo muda muito (2°) com o corte justo: "Fica no mesmo lugar" corta o fim de uma linha e o começo de outra (os cantos andam 3,5 mm), e é preciso ajustar de novo; "Acompanha o texto" cresce uns 3 mm e não corta nada;
    3. texto encostado na faixa escura da lombada (2°): "Fica no mesmo lugar" corta um canto e deixa entrar 1 mm da faixa; "Acompanha o texto" guarda o texto, mas deixa entrar uns 4 mm da faixa; nos dois é preciso ajustar.
  - as mesmas três opções ("Fica no mesmo lugar da página (como no ScanTailor)", "Acompanha o texto", "Ainda não entendi"), com o bom e o ruim de cada uma.
  - Desenhos: `img/g6/retangulo-passo-a-passo.svg`, `retangulo-ex1-pouco.svg`, `retangulo-ex2-muito.svg` e `retangulo-ex3-beirada.svg`, feitos por `docs/plano/paginas-claude-ai/escolhas/desenhos_g6_retangulo.py` (as contas de quanto o canto anda são feitas no script). A página ganhou um jeito de mostrar um desenho largo na linha inteira, sem cortar (campo `largo` do exemplo); as outras perguntas não mudam.

### Segunda leitura (09/10/2026, respondida às 16:09, horário de Brasília)

- **"Se o Kaique mudar o ângulo depois de ajustar o corte à mão, o retângulo verde do corte fica parado ou se mexe junto com o texto?"** (`g6-retangulo`, pergunta refeita): **Fica no mesmo lugar da página (como no ScanTailor)**, com o comentário:

  > Posso ter as duas opções mas a opção do scantailor ficar como padrão?

### O que a gerente fez (09/10, segunda leitura)

- `g6-retangulo`: marcada `decidida`, com a decisão "Fica no mesmo lugar (como no ScanTailor) é o padrão". O comentário subiu para o `historico` (fixado) e saiu da caixa de comentário; a escolha dele continua gravada na resposta.
- Pergunta nova, respondendo ao comentário (`g6-retangulo-onde`, parte "Endireitar", ordem 118): "Sim, dá para ter as duas, com a do ScanTailor de fábrica. Onde você quer trocar?" Opções, cada uma com um esquema da tela (`img/g6/retangulo-onde-livro.svg`, `retangulo-onde-configuracoes.svg`, `retangulo-onde-pagina.svg`, feitos por `docs/plano/paginas-claude-ai/escolhas/desenhos_g6_retangulo_onde.py`): (a) na tela "O que fazer", por livro, abaixo da "Conta do endireitar:"; (b) nas Configurações, para todos os livros; (c) na ferramenta Endireitar, por página, junto do "aplicar em"; (d) "Ainda não entendi". Aberta.
