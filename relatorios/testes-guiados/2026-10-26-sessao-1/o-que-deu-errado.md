# O que foi feito errado, e por que os testes não perceberam (26/10/2026)

Pedido do Samuel na sessão 1, palavras dele: "Eu quero saber o que foi feito errado, para poder arrumar, quero saber
como foram feitos esses testes e porque eles não perceberam. Isso tinha sido uma coisa falada expliccitamente e já
aviamos tradados dessa opção A e de como seria o modo automatico, isso foi uma grande alucinação". E sobre a
gerente: "Eu já tinha decidido isso antes, você não lembra porque?"

## 1. O que estava decidido (com data e onde está escrito)

| Quando | O que | Onde está |
|---|---|---|
| 22/09/2026 | Pedido do Kaique: "Essa pagina não era mais para aparecer – nós tínhamos que abrir direto na área de trabalho" e ter "um botão" para escolher o automático | `observações 2\observação 2.1.docx`; rascunho do layout, linha 266 |
| 25/09/2026 | **Decisão 1:** "Estrutura: Photoshop puro, sem abas. Uma única tela com todas as ferramentas." | `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\Plano de layout (rascunho).md`, "Decisões tomadas" |
| 25/09/2026 | **Decisão 2:** "Trabalho automático = painel 'Automático' que abre e fecha (substitui a tela 7). Marcar só as etapas que se quer; escolher a ordem; salvar como receita [...]. Funciona antes/ao abrir o livro e depois, na área de trabalho (ex.: abrir o PDF sem mexer e rodar as etapas depois)." | mesmo arquivo; `memoria/itens/layout.md` ("A tela decidida") |
| 28/09/2026 | 2a: ordem das etapas livre, arrastando. 2b: automático em livro mexido à mão pergunta se pula as páginas mexidas | mesmo arquivo |
| 12/10/2026 | Rodada 12, 708: "'O que fazer': o painel Automático a substitui (decisão 2, 25/09; pedido do Kaique de 22/09)" | rascunho, rodada 12 |

## 2. O que foi construído no lugar

- **A tela "Marque o que você quer fazer" continua sendo a porta de entrada** do livro, e o painel "Automático" só
  mostra a lista das etapas (não roda nada).
- **As ferramentas dependem das caixinhas.** A regra está em `ui/tela_conferir.py` (função `carregar`, linhas
  ~2519-2537): só monta a ferramenta Dividir se "Dividir" estiver marcada, Bordas se "Cortar as bordas", Endireitar se
  "Endireitar", e as ferramentas de marcar e o Filtro só com "Limpar a folha". **Essa regra é de julho de 2026**
  (commits `d9fae8c` de 18/07, `f15e469` de 01/08, `d83bb03` de 08/08), do tempo das "abas por etapa" — o desenho que a
  decisão 1 recusou em 25/09.
- **O layout trocou a aparência, não a regra.** A etapa 2 do layout (09/10) tirou as abas da tela, mas por baixo
  cada ferramenta continua sendo uma "aba" que só existe se a caixinha foi marcada. "Sem abas" foi feito como
  desenho; "todas as ferramentas numa tela só" não foi feito.
- **Mudar as caixinhas depois não vale** (defeito de 29/09/2026, aberto há quase um mês). Hoje (26/10) o
  `projeto.json` do "La vida eterna" continuou com `limpar: false` depois de o Samuel marcar "Limpar a folha".

## 3. Como a decisão se perdeu

- A obra do layout foi dividida em etapas (1 temas, 2 tela sem abas, 3 painéis, 4 Propriedades e Filtro,
  5 miniaturas, 6 tela cheia dos filtros, 7 tela inicial). **Nenhuma etapa recebeu "trocar a tela 'O que fazer' pelo
  painel Automático e abrir o livro direto na área de trabalho".**
- Na lista "O que falta" do layout (`memoria/itens/layout.md`), isso aparece só como "Pendências sem dono achadas na
  conferência de 12/10/2026: receitas, ordem arrastando e 'pular as páginas mexidas' do Automático" e "aviso de livro
  novo (804 B: só faz sentido quando o livro abrir direto na tela de trabalho, etapa 7)". Ficou anotado como
  pendência **sem dono** e ninguém pôs numa etapa. A gerente não cobrou.
- A gerente desta sessão também não lembrou: ao abrir, leu só a parte mais nova do resumo (PARTE -20), que não fala
  da decisão 2, e ofereceu ao Samuel como "opção A" uma coisa que ele já tinha decidido em 25/09.

## 4. Como foram feitos os testes, e por que não pegaram

| Teste | O que ele confere | Por que não pegou |
|---|---|---|
| **Suíte automática** (2744 testes, PC e GitHub) | Que cada pedaço faz **o que o código manda**: o filtro dá a imagem certa, o Dividir corta na linha, o painel abre etc. | Testa o código contra ele mesmo, não contra as decisões. Os testes de tela **pulam** quando a ferramenta não está montada (ex.: `tests/test_paineis_na_tela.py:435`, `if "marcar" not in tela._abas_ativas`) — ou seja, aceitam o esconder como normal. Nenhum teste abre um livro com tudo desmarcado. |
| **`teste_botoes.py`** (233 cliques) | Que cada botão que existe, clicado, não dá erro | Só clica no que existe. Não confere se o clique dá resposta na tela (o "está certo" mudo passa) nem se falta botão. |
| **Conferências do Samuel** (prints das etapas do layout) | Se a tela parece com o desenho aprovado | Os prints eram tirados com as caixinhas certas marcadas, então todas as ferramentas apareciam. A conferência mostrava a aparência, não o caminho de usar. |
| **Mapa do programa e 14 livros** (verificadores, 23/10) | Usar o programa de verdade, livro por livro | Os agentes já sabiam usar o programa e marcaram as caixinhas certas desde o começo (lição registrada em 23/10: "Agente que já sabe usar o programa não acha o que confunde o Kaique"). O mapa até anotou "Desmarcada, todas somem", mas como descrição, não como erro contra a decisão 1. |

**O que faltou em todos:** ninguém conferiu o programa **contra a lista de decisões** (decisão 1 e decisão 2). Cada
teste verificava se o que foi feito funcionava, nunca se o que foi feito era o que tinha sido decidido.

## 4b. Mover e redimensionar presos ao corte de bordas (achado 1-9)

Pedidos dele de 22/09/2026 ("quero conseguir redimensionar o conteudo tambem") e 22/10 (`fr-24`: "Mas se eu quiser
redimensionar isso dentro do programa eu vou conseguir né?" → "sim"). Os dois existem
(`ui/widgets/visualizador.py`, modo `MODO_CONTEUDO`: arrastar move, arrastar um canto redimensiona), mas só dentro da
ferramenta de bordas, que só aparece com "Cortar as bordas" marcada, e ficam cinza até escolher um tamanho de folha
(`ui/tela_conferir.py:1365-1374`). O mesmo erro da seção 2: a ferramenta depende de uma caixinha. Ele quer o Mover
como ferramenta própria, a qualquer hora, como no Photoshop.

A gerente errou na sessão (achado 1-7) ao dizer que redimensionar não existia: procurou um botão, não o canto que se
arrasta. Mais um caso de não conferir com as decisões antes de responder.

## 4c. "Ver lado a lado" só no livro aberto (achado 1-10)

Decidido em 06/10/2026, rodada 7 do layout (201 B: botão "Ver lado a lado" em cima das páginas, canto direito; 202 A:
pares rolando). Construído só no livro aberto da tela inicial (`ui/widgets/paginas_rolando.py`, usado só por
`ui/tela_inicio.py`). Na área de trabalho, onde se edita, não existe: o Dividir mostra a folha do scan inteira e o
Endireitar uma página só, sem botão para trocar. Mais uma decisão feita pela metade e que ninguém conferiu.

## 5. Para arrumar (a planejar com o Samuel, uma decisão por vez)

- Fazer o que as decisões 1 e 2 mandam: o livro abre direto na área de trabalho com todas as ferramentas; o
  automático vira o painel/botão opcional, com receitas, ordem arrastando e a pergunta de pular páginas mexidas.
- Um teste novo que confira as decisões: abrir um livro sem nada marcado e exigir todas as ferramentas à vista.
- Uma conferência "decidido × construído": ler todas as decisões do rascunho do layout e do plano e marcar, uma a
  uma, se estão no programa — para achar outras que se perderam do mesmo jeito.
