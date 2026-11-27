# Triagem das regras e dos erros: resumo (27/11/2026)

**Em uma frase:** a maior parte das regras de hoje é jeito de fazer ou coisa que o computador já confere; a maior parte
dos erros veio de pedido claro feito diferente, e três conferências do computador (uma porta só para cada dado, a prova
de cada decisão e o arquivo fora da lista que barra) teriam pegado a maioria deles.

Só leitura (D-887): nenhuma regra nova, nenhum arquivo do projeto mudou, nenhuma skill ou gancho criado. O detalhe está
nos três arquivos ao lado: `tabela-regras`, `tabela-erros` e `ordem-de-servico` (cada um em .md e .html).

## Contagens por destino

| destino | regras de hoje (Parte A, 158) | tipos de erro (Parte B, 31) |
|---|---|---|
| FISCAL RÁPIDO | 40 (34 já cobradas pelo porteiro) | 13 |
| FISCAL GITHUB | 13 | 9 |
| SKILL | 46 | 3 |
| PERMISSÃO | 10 | 3 |
| REGRA POR PASTA | 16 | 1 |
| FICA NO CLAUDE.md | 24 | 0 |
| GANCHO | 2 | 0 (2 como segundo jeito) |
| APAGAR | 2 | 0 |
| DÚVIDA | 5 | 2 |

- **Causa dos erros:** 29 tipos são erro de programação (o pedido estava claro); 2 não dá para saber sem o Samuel. As
  38 vezes em que ele mudou de ideia depois de ver ficam só como registro.
- **O que achei e não estava na ordem:** o porteiro tem 25 conferências (não 9) e a lista de exceções tem 135 itens
  hoje (não 164); o gancho antes do commit não está ligado; não existe configuração de permissões nem de ganchos do
  Claude Code no projeto; 20 decisões dele sobre o jeito de trabalhar (16 a 25/11) não estão no CLAUDE.md nem nos agentes (algumas só no catálogo do porteiro); o pacote do
  pedido e o formulário da entrega deixaram de ser usados depois de 21/11.

## Os 10 fiscais que mais erros teriam evitado, em ordem

A conta é a soma das vezes dos tipos de erro que cada um pegaria (Parte B). Nenhum é plano: é só a ordem.

| | o fiscal | rápido ou GitHub | pegaria | vezes (aprox.) |
|---|---|---|---|---|
| 1 | Cada dado da página é gravado por uma porta só, e as listas ("o que vai junto") saem do modelo de dados; a segunda cópia é acusada | rápido (lendo o código) | conserto só num caminho; conta repetida; conta feita na tela | ~140 |
| 2 | Toda decisão "construída" tem a sua prova de comportamento rodando; a que não tem é acusada | GitHub (e rápido para achar a sem prova) | decisão não construída ou só na aparência; caixinha que não vale; o novo que estraga o que funcionava | ~95 |
| 3 | Arquivo mudado fora do "Dentro" da ordem barra a entrega (hoje só avisa) | rápido | agente que acrescentou o que não foi pedido | ~45 |
| 4 | Mutação automática: cada proteção e cada conferência desligada numa cópia faz um teste falhar | GitHub | dá como feito sem conferir; proteção sem teste; teste que só confere texto | ~40 |
| 5 | O texto para o Samuel é lido antes de ir: sem código nem número, com imagem, e conferido no Livro se já foi respondido | rápido | pergunta sem prova; palavra de dentro; pergunta repetida | ~40 |
| 6 | O mesmo resultado por todos os caminhos de uma ferramenta, e a mesma imagem na tela, na miniatura e no PDF | GitHub | desvio por caso; tela diferente do PDF | ~25 |
| 7 | A conversa com o Windows conferida pelo que o código importa, não por lista de palavras | rápido | a recusa que deixa passar o vizinho (e acaba com a maior parte das 135 exceções) | ~20 |
| 8 | Caça de função que ninguém chama | rápido | código morto | ~20 |
| 9 | "De onde vem cada dado" da conferência, cobrado no formulário e conferido por quem tenta quebrar | rápido | conferência que acredita no que o conferido escreve | ~15 |
| 10 | Comando que mexe no `.git` inteiro ou apaga pasta com tudo, acusado em script e teste (já existe) | rápido | comando que estraga o que é do Samuel | ~8 |

## Dúvidas para o Samuel

Cada uma diz o que é, o que você escolhe e a sugestão do agente da triagem. O número da decisão vai no fim, só para
consulta.

1. **O ritmo do trabalho depois da entrega.** As regras dizem "uma mudança por vez, uma fase por vez, conferir cada item
   antes do próximo". A obra de 26/10 e a parada de consertos até a entrega suspenderam isso. **O que você escolhe:**
   volta a valer agora, ou continua suspenso enquanto durar a vistoria? Sugestão: dizer qual vale, para tirar a outra do
   texto. (X9; R006, R057, R131)
2. **As páginas do antes e depois.** Um trecho manda mostrar a mudança em todos os livros do conjunto de teste; outro, só
   nas páginas-gabarito daquele item. **O que você escolhe:** todas, ou só as do gabarito? Sugestão: só as do gabarito,
   que é o que se faz hoje. (X3; R060)
3. **Quantos agentes ao mesmo tempo.** O CLAUDE.md diz no máximo dois (três em 10/11); a memória diz 3 a 4; a Central
   tem um número próprio. **O que você escolhe:** qual vale? (X6)
4. **O que o agente lê primeiro.** O CLAUDE.md põe o Livro de decisões primeiro; os arquivos dos agentes começam pelo
   estado atual e pelo plano. **O que você escolhe:** o Livro primeiro em todos? Sugestão: sim. (X10)
5. **O aviso da moldura dourada.** O verificador tem de avisar, em toda conferência, que moldura e iluminura são defeito
   conhecido "até a Fase 1 ficar pronta". **O que você escolhe:** ainda vale, ou sai? (V2; R139)
6. **O atualizador antigo, complicado demais.** Ele foi refeito porque tinha peças que só protegiam outras peças, e a
   volta automática saiu depois de três rodadas. Foi feito o que você pediu ("volta sozinho"), mas o jeito custou mais
   do que valia. **O que você escolhe:** conta como erro de programação (o jeito estava errado) ou como pedido que você
   trocou depois de ver? Só muda a conta da triagem. (E08; D-718, D-830, D-868)
7. **As contradições que você já resolveu.** Em 18 e 19/11 você resolveu seis (velocidade, testes no PC, quem escreve
   "pronto", os dois ramos, o agente de tela no núcleo, janela escondida ou à vista), mas o CLAUDE.md e os arquivos dos
   agentes ainda dizem o antigo. **O que você escolhe:** a gerente acerta o texto agora, ou isso espera a construção das
   skills e fiscais? (D-785 a D-798)
8. **O plano antes de mexer.** Você mandou que todo agente apresente um plano antes de consertar. Falta dizer se ele
   espera o seu "sim" depois do plano. **O que você escolhe:** espera sempre, só nos consertos e ferramentas novas, ou
   nunca? Sugestão (já da gerente em 16/11): espera nos consertos e ferramentas novas; não nas investigações. (D-709)
9. **Um modelo de agente por tipo de tarefa.** A gerente propôs três opções em 16/11 e ficou sem resposta. **O que você
   escolhe:** uma das três, ou deixar para depois? (D-710)
10. **O pacote do pedido e o formulário da entrega.** Eles foram construídos em 18-19/11 e usados até 21/11; do
    atualizador novo em diante deixaram de ser usados, sem decisão sua. **O que você escolhe:** voltam a valer em todo
    trabalho, ou ficam esperando o modelo novo da ordem de serviço? (D-784, D-792)
11. **Onde mora a trava da ordem de serviço.** Opção 1: no programa das regras dos agentes, rodado pela gerente. Opção 2:
    num gancho do Claude Code, que roda sozinho antes de abrir o agente. **O que você escolhe:** 1, 2, ou as duas com
    uma peça só? Sugestão do agente: as duas com uma peça só (a conferência mora na opção 1 e o gancho só a chama).
12. **O gancho antes do commit.** Ele existe desde 19/11, mas nunca foi ligado; quem confere hoje é o GitHub. **O que
    você escolhe:** ligar, ou deixar só o GitHub? Sugestão: ligar, porque avisa mais cedo e não muda o programa.

## O tempo de cada parte (relógio da máquina)

| parte | começo | fim |
|---|---|---|
| leitura das fontes | 14:56 | 15:05 |
| A, as regras | 15:05 | 15:10 |
| B, os erros | 15:10 | 15:13 |
| C, a ordem de serviço | 15:13 | 15:15 |
| resumo | 15:15 | 15:18 |

## Ressalvas

- **Destino e causa são julgamento meu**, com o motivo em cada linha. O Samuel e o Fable podem trocar qualquer um.
- **A vistoria ainda corre**: os números dos erros de código (Parte B, E05 a E09) são os da lista em 27/11 às 15h.
- **Não rodei nada**: nem testes, nem o porteiro, nem o programa. "Já cobre" e "não achei uso" são por leitura.
- **Não li uma por uma** as 19 conferências antigas nem os relatórios de quem tenta quebrar dos passos 0 a 2: entraram
  pelo Livro e pelo catálogo dos erros, que já as tinham juntado.
