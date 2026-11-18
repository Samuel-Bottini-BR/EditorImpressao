# Como passar as regras aos agentes: proposta (18/11/2026)

Proposta de um agente, só lendo e escrevendo. **Nenhuma regra mudou de texto, nenhuma linha do programa nem dos testes
mudou.** Os esboços em `esbocos/` mostram como seria; nada está ligado (nem gancho, nem teste, nem conferência antes
do commit). Ramo `regras-agentes-2026-11-18`, a partir do `fase-1` (`0014e618`). O Livro lido é o do obra (o do
`fase-1` ainda não tem as decisões de 17 e 18/11).

## Em poucas frases

1. **155 regras** no CLAUDE.md e nos 4 arquivos de agente (mais 9 trechos que são informação, não regra).
   **80 aparecem em dois lugares ou mais**, e 28 dessas cópias dizem coisas um pouco diferentes.
   **10 contradições** de verdade (duas regras que não dá para cumprir juntas), 6 diferenças pequenas e
   4 regras que parecem vencidas. 23 regras são só da gerente e não precisam ir para agente nenhum.
2. **Hoje o implementador recebe 93 mil caracteres de regras** (CLAUDE.md inteiro, o arquivo dele e o índice da
   memória), e até 167 mil se ler tudo o que o índice manda "antes de qualquer trabalho". **No pacote de exemplo
   (a peça nova do Windows), as regras são 9,2 mil caracteres** (10 "sempre" e 29 do trabalho), e o
   pacote inteiro, com as decisões copiadas do Livro e o formulário, 18,6 mil. Cerca de 9 vezes menos regra.
3. **A máquina pode cobrar 37 regras inteiras e 62 em parte.** 24 conferências dão para
   fazer já; 14 precisam de estudo. Rodando o esboço (só leitura) no código de hoje do obra, as três primeiras
   teriam barrado exatamente os defeitos 1 e 4 da etapa 5 (o `DETACHED_PROCESS` do "Reiniciar agora" e a tranca
   `/inheritance:r` da pasta), e uma quarta acha duas dicas de tela do Automático que mostram número de decisão ao Kaique.
4. **O formulário da entrega** tem 20 campos, em três etapas (antes de quem tenta quebrar, antes da prova à vista,
   antes de "pronto"). O programa vê se cada campo existe e se bate com o código, o Livro e o git; não vê se a resposta
   é boa. Isso é do agente que tenta quebrar, que recebe a lista completa de regras.
5. **5 perguntas para o Samuel** (seção 9).

---

## 1. O catálogo de todas as regras

Etiquetas: **TODO** todo trabalho · **TELA** tela · **WIN** Windows e instalador (e qualquer conversa com programa de
fora) · **IMG** imagem, filtros e processamento · **PERG** perguntas e relatórios ao Samuel · **TESTE** testes ·
**GIT** git e arquivos · **PESQ** pesquisa de peça de fora · **GER** só a gerente.
Papel: todos · código (implementador e layout) · verif · pesq · layout · gerente.
"Máquina": sim = um programa cobra a regra inteira; em parte = cobra um pedaço (ex.: que o campo existe); não = só
gente. "Onde" lista todas as cópias; "Repete/contra" diz se as cópias dizem coisas diferentes e aponta a contradição
(X = contradição, V = parece vencida; a lista está logo depois da tabela). **Nada aqui foi resolvido, só apontado.**
O texto completo de cada regra continua no lugar de onde veio. Os mesmos dados estão em `esbocos/catalogo.py`.

| # | Regra | Onde | Etiquetas | Papel | Máquina | Repete / contra |
|---|---|---|---|---|---|---|
| R001 | Ordem de leitura e quem manda | C topo; implementador 'Leia antes'; verificador 'Leia antes'; pesquisador 'Leia antes'; layout 'Leia antes' | TODO | todos | nao | 5 lugares; o CLAUDE.md põe o Livro como item 0, os agentes começam pelo ESTADO-ATUAL e só mais abaixo dizem 'Livro antes de tudo' · X10 |
| R002 | PEDIDOS.md e handoff são histórico | C topo; C §7 | TODO | todos | nao | 2 lugares no CLAUDE.md, iguais |
| R003 | Tela em português sem jargão | C §1; layout 'Regras de tela' | TELA PERG | todos | em parte | 2 lugares, iguais |
| R004 | Critério final do livro | C §1 | IMG | todos | nao |  |
| R005 | Não recomeçar do zero | C §2 | TODO | codigo | em parte |  |
| R006 | Uma mudança por vez | C §2; C §8 passo 3; implementador 'O que você faz' | TODO | codigo | nao | 3 lugares; a Obra (D-014) suspende o 'conferir cada item antes do próximo' · X9 |
| R007 | Planejar antes; perguntar antes de mexer em estrutura | C §2 | TODO | codigo | nao |  |
| R008 | Ir até o fim dentro da alçada | C §2 | TODO | todos | nao |  |
| R009 | Primeiro a frase, depois o número | C §2; implementador 'Como entregar'; verificador 'Como entregar'; pesquisador 'Como entregar'; layout 'Como entregar'; C §11.13.7 | PERG | todos | nao | 6 lugares, iguais no sentido |
| R010 | Conciso: essencial no chat, detalhe em arquivo | C §2 | PERG | todos | nao |  |
| R011 | Claro e direto com o Samuel | C §2; C §11.13.7 | PERG | todos | em parte | 2 lugares, parecidos · X11 |
| R012 | Honesto: avisar erro e risco | C §2 | TODO | todos | nao |  |
| R013 | Não inventar detalhe | C §2 | TODO | todos | em parte |  |
| R014 | Relatório em três formatos | C §2; C §8 passo 7; verificador passo 7 | TODO PERG | todos | sim | 3 lugares, iguais |
| R015 | PySide6, nunca tkinter | C §3; layout 'Regras de tela' | TELA | codigo | sim | 2 lugares, iguais |
| R016 | Uma página por vez na memória | C §3 | IMG | codigo | em parte |  |
| R017 | A janela nunca congela | C §3; layout 'Regras de tela' | TELA WIN | codigo | em parte | 2 lugares, iguais |
| R018 | Nenhuma exceção fecha a janela | C §3 | TELA | codigo | em parte |  |
| R019 | Nenhum emoji em rótulo | C §3; layout 'Regras de tela' | TELA | codigo | sim | 2 lugares, iguais |
| R020 | Texto com acento, caminho sem acento | C §3 | TELA GIT WIN | codigo | sim |  |
| R021 | Algoritmo consagrado | C §3 | IMG | codigo | nao |  |
| R022 | Nenhum modelo generativo | C §3; implementador 'nunca'; pesquisador 'nunca' | IMG PESQ | todos | em parte | 3 lugares; o pesquisador acrescenta 'OCR generativo proibido' |
| R023 | Python 3.14, não rebaixar | C §3; implementador 'nunca' | TODO | todos | sim | 2 lugares, iguais |
| R024 | GPU sem float16 rápido | C §3; pesquisador 'roda aqui?' | IMG PESQ | todos | em parte | 2 lugares; o pesquisador acrescenta o notebook do Kaique |
| R025 | Erro nunca como stack trace | C §3 | TELA | codigo | em parte |  |
| R026 | Licença: GPL pode entrar | C §3; pesquisador 'O que você faz' | PESQ | todos | nao | 2 lugares; o pesquisador cobra escrever sempre |
| R027 | Teste de máquina: o agente decide | C §4.1 | TESTE | todos | sim |  |
| R028 | Teste de olho: prepara, abre tudo, para e chama | C §4.2; verificador passos 3 e 4 | TESTE IMG | verif | nao | 2 lugares; dizem coisas diferentes sobre quais páginas · X3 |
| R029 | Número que não pega o pior defeito não dá veredito | C §4.2 | TESTE IMG | todos | nao |  |
| R030 | Ressalva escrita, nunca escondida | C §4.2; implementador 'Como entregar'; verificador 'nunca' | TODO | todos | em parte | 3 lugares, iguais |
| R031 | Nunca 'APROVADO' | C §4.3; C §8; implementador 'nunca'; verificador 'regra de ouro'; verificador 'nunca' | TODO | todos | sim | 5 lugares; dizem coisas diferentes sobre quem pode escrever 'PRONTO PARA CONFERIR' · X4 |
| R032 | Máquina ou olho, item por item | C §4.3; verificador 'regra de ouro'; verificador 'Como entregar' | TESTE | todos | sim | 3 lugares, iguais |
| R033 | Auditoria por amostragem | C §4.4 | GER | gerente | nao |  |
| R034 | Onde roda cada teste | C §4.6; implementador 19/10; verificador 19/10; pesquisador 19/10; layout 19/10 | TESTE | todos | sim | 5 lugares; nos agentes contradiz o texto mais antigo do próprio arquivo · X2 |
| R035 | Só documentos: entra com o GitHub | C §4.6 | GER | gerente | sim |  |
| R036 | Filtro de velocidade no GitHub | C §4.6; implementador 19/10; verificador 19/10; pesquisador 19/10; layout 19/10 | TESTE IMG | codigo | sim | 5 lugares · X1 |
| R037 | Lentidão pequena vai para a Fase 5 | C §4.6 | GER | gerente | nao | X1 |
| R038 | Teste de reversão em todo conserto | C §4.7; implementador 19/10; verificador 19/10; layout 19/10 | TESTE | todos | em parte | 4 lugares, iguais (o pesquisador não tem) |
| R039 | Agente entrega sempre à gerente | C §4.8; implementador 19/10; verificador 19/10; pesquisador 19/10; layout 19/10 | TODO | todos | em parte | 5 lugares, iguais |
| R040 | Recados de outras janelas | C §4.8 | GER | gerente | nao |  |
| R041 | Ler a memória antes | C §4.9; implementador 19/10; verificador 19/10; pesquisador 19/10; layout 19/10 | TODO | todos | nao | 5 lugares; nos agentes ainda diz 'se a pasta já existir (está sendo montada a partir de 19/10)' |
| R042 | Teste de imagem pelo caminho inteiro | C §4.10; implementador 21/10; verificador 21/10; layout 21/10; C §11.13.4 | IMG TESTE | todos | em parte | 5 lugares, iguais |
| R043 | Cada foto diz o caminho e as opções | C §4.10; implementador 21/10; verificador 21/10; layout 21/10; C §11.13.5 | IMG PERG | todos | em parte | 5 lugares, iguais |
| R044 | Só páginas que vão ser impressas | C §4.10; implementador 21/10; verificador 21/10; layout 21/10; C §11.13.4 | IMG TESTE PERG | todos | em parte | 5 lugares, iguais |
| R045 | Protocolo de mudança de imagem | C §5 | IMG | codigo | em parte |  |
| R046 | Tudo o que foi tentado vai para melhorias.md | C §5; pesquisador 'Leia antes' | IMG PESQ | todos | em parte | 2 lugares |
| R047 | O que o agente decide sozinho | C §6 | IMG | codigo | nao |  |
| R048 | O que precisa perguntar antes | C §6; implementador 'nunca' | TODO | todos | em parte | 2 lugares; o implementador só repete 'trocar biblioteca' |
| R049 | core/ não importa ui/ | C §7; implementador 'nunca' | IMG WIN | codigo | sim | 2 lugares, iguais |
| R050 | Modelo de dados em dois níveis | C §7 | IMG TELA | codigo | em parte |  |
| R051 | Onde o programa guarda estado | C §7 | WIN | codigo | em parte |  |
| R052 | Desempenho já resolvido, não refazer | C §7 | IMG | codigo | nao |  |
| R053 | Ordem obrigatória do processamento | C §7 | IMG | codigo | em parte |  |
| R054 | Acervo e originais só para ler | C §7; implementador 'nunca'; verificador 'nunca' | TODO GIT | todos | em parte | 3 lugares; o implementador lista mais pastas |
| R055 | Queixas do Kaique são requisito | C §7 | IMG TELA | todos | nao |  |
| R056 | Handoff só com pedido do Samuel | C §7 | GIT | todos | sim |  |
| R057 | Item da fase atual, na ordem | C §8 passo 1; C §10.2; implementador 'O que você faz' | GER TODO | todos | nao | 3 lugares · X9 |
| R058 | Testes quebrados: conserta antes de seguir | C §8 passo 4; implementador 'O que você faz' | TESTE | codigo | sim | 2 lugares |
| R059 | Régua e velocidade; nada mais lento | C §8 passo 5; implementador 'O que você faz'; verificador passo 2 | TESTE IMG | codigo | em parte | 3 lugares · X1 |
| R060 | Antes/depois só nas páginas-gabarito do item | C §8 passo 6; verificador passo 3 | TESTE IMG | verif | em parte | 2 lugares · X3 |
| R061 | Item de tela: janela real com mouse nativo | C §8 passo 6; verificador passo 5; layout 'Como provar' | TELA TESTE | verif | em parte | 3 lugares |
| R062 | Commit na hora com o defeito por extenso; nunca segredo | C §8 passo 10 | GIT | todos | em parte | X12 |
| R063 | Mancha do verso: o defeito mais grave | C §9 | IMG | todos | nao |  |
| R064 | A régua precisa de critérios novos | C §9 | IMG | todos | nao |  |
| R065 | Amarelado está na tinta | C §9 | IMG | todos | nao |  |
| R066 | Não há binarizador vencedor | C §9 | IMG | todos | nao |  |
| R067 | Não desfazer a correção do 'magic color' | C §9 | IMG | codigo | em parte |  |
| R068 | Scan de baixa resolução não se recupera | C §9 | IMG | todos | nao |  |
| R069 | Barra de rolagem cinza, de propósito | C §9 | TELA | codigo | sim |  |
| R070 | Gerente não escreve código | C §10.1 | GER | gerente | nao |  |
| R071 | Cada papel no seu lugar | C §10.1; implementador 'O que você faz'; verificador 'nunca'; pesquisador 'nunca'; layout 'Onde você trabalha' | TODO GIT | todos | sim | 5 lugares · X7 |
| R072 | Layout só começa com o plano de layout | C §10.1; layout 'Antes de tudo' | TELA | layout | nao | 2 lugares · V1 |
| R073 | Ideia nova vai para a Lista de espera; bug que não impede, para a Lista de bugs | C §10.2; implementador 'Ideias e bugs'; layout 'Como entregar' | TODO | todos | em parte | 3 lugares · X9 |
| R074 | Uma cópia e um ramo por frente | C §10.3; layout 'Onde você trabalha' | GIT | todos | sim | 2 lugares · X5 |
| R075 | Plano em duas cópias | C §10.4 | GER | gerente | sim |  |
| R076 | Docstring em tudo o que tocar | C §10.5; implementador 'O que você faz'; layout 'Regras de tela' | TODO | codigo | sim | 3 lugares, iguais |
| R077 | Plano novo não apaga pendência | C §10.6 | TODO | todos | nao |  |
| R078 | Item resolvido guarda o pedido original | C §10.7 | GER | gerente | em parte |  |
| R079 | Prosa de checkpoint não é prova | C §10.8; C §9 (menu Abrir) | TODO | todos | nao | 2 lugares |
| R080 | Apagar: fora do projeto nada; dentro só o seu; junções | C §10.9; implementador 'Apagar'; verificador 'Apagar'; pesquisador 'Apagar'; layout 'Apagar' | GIT | todos | sim | 5 lugares; os agentes acrescentam 'conferir o que há dentro' e as junções |
| R081 | Conferências em página do claude.ai com banco | C §10.10 | GER | gerente | nao |  |
| R082 | Aba Respostas: gerente responde no documento | C §10.10 | GER | gerente | sim |  |
| R083 | Responder de novo guardando a antiga | C §10.10 | GER | gerente | sim |  |
| R084 | Modelo de print (o do girar) | C §10.10; C §11.13.3 | PERG | todos | em parte | 2 lugares; o §11.13.3 resume com azul e verde só |
| R085 | Central: um jeito de ver e celular | C §10.10 | GER | gerente | sim |  |
| R086 | Central: atualizar sempre | C §10.10 | GER | gerente | em parte |  |
| R087 | Central: ler as ordens dele primeiro | C §10.10 | GER | gerente | em parte |  |
| R088 | Aviso no celular ao pôr cartão | C §10.10 | GER | gerente | nao |  |
| R089 | Pergunta de agente vai à Central na hora | C §10.10; implementador 26/10; verificador 26/10; pesquisador 26/10; layout 26/10 | PERG | todos | em parte | 5 lugares; os agentes dizem 'na dúvida, pare e pergunte' · X13 |
| R090 | Agente não grava na Central | C §10.10 | PERG | todos | sim |  |
| R091 | Aba Conferência | C §10.10 | GER | gerente | em parte |  |
| R092 | Abrir a conferência sozinha no navegador | C §10.10 | GER | gerente | nao | X13 |
| R093 | Comentário dele se responde na página | C §10.10 | GER | gerente | nao |  |
| R094 | Livro de decisões único | C §11.1 | GER | gerente | em parte |  |
| R095 | Nenhuma decisão sem dono | C §11.2 | GER | gerente | sim |  |
| R096 | Pedido leva as decisões; ONDE-PAREI diz como cumpriu | C §11.3; implementador 26/10; verificador 26/10; pesquisador 26/10; layout 26/10 | TODO | todos | sim | 5 lugares, iguais |
| R097 | Cada decisão tem prova de comportamento; aparência não é prova | C §11.4; C §11.8; implementador 26/10; verificador 26/10; pesquisador 26/10; layout 26/10 | TESTE | todos | em parte | 6 lugares; o §11.4 e os agentes dizem test_decisoes.py, o §11.8 diz test_decisoes*.py |
| R098 | Quem confere não construiu, e confere do zero | C §11.5; verificador 26/10 | TESTE | verif | em parte | 2 lugares |
| R099 | Na dúvida, parar e perguntar | C §11.6; implementador 26/10; verificador 26/10; pesquisador 26/10; layout 26/10 | TODO | todos | nao | 5 lugares, iguais |
| R100 | Gerente procura no Livro antes de perguntar | C §11.6; C §11.13.10 | GER | gerente | em parte | 2 lugares |
| R101 | Só o que ele mandou | C §11.7 | TODO | todos | em parte |  |
| R102 | O novo não estraga o escolhido e testado (D-605) | C §11.8; implementador 03/11; verificador 03/11; pesquisador 03/11; layout 03/11 | TODO TESTE | todos | sim | 5 lugares, iguais · X14 |
| R103 | Verificador confere o que funcionava ao redor | C §11.8; implementador 03/11; verificador 03/11; pesquisador 03/11; layout 03/11 | TESTE | verif | nao | 5 lugares, iguais |
| R104 | Como fica para quem usa e no livro (D-637) | C §11.9; implementador D-637; verificador D-637; pesquisador D-637; layout D-637 | TODO | todos | sim | 5 lugares, iguais |
| R105 | Mudou a ferramenta, muda em todos os lugares (D-667) | C §11.10 | TODO TELA | todos | em parte |  |
| R106 | Agente não abre agente | C §11.11 | TODO | todos | sim | X6 |
| R107 | Sem gambiarra: a causa, a regra, todos os caminhos | C §11.12; implementador 13/11; verificador 13/11; pesquisador 13/11; layout 13/11 | TODO | todos | em parte | 5 lugares; cada agente tem um resumo diferente para o seu papel |
| R108 | Como conserta: um lugar só | C §11.12 | TODO | codigo | em parte | X7 |
| R109 | Prova: caminho → função e o mesmo resultado em todos | C §11.12; implementador 13/11; verificador 13/11 | TESTE | todos | em parte | 3 lugares |
| R110 | Quando só der remendo: parar | C §11.12 | TODO | todos | nao |  |
| R111 | Gerente pede sobre a ferramenta inteira | C §11.12; C §11.10 | GER | gerente | nao | 2 lugares |
| R112 | Sem gambiarra vale para tudo | C §11.12 (18/11); implementador 18/11; verificador 18/11; pesquisador 18/11; layout 18/11 | TODO | todos | nao | 5 lugares; os agentes dizem 'os cinco pontos' e listam seis |
| R113 | Uma peça só para conversar com o que está fora | C §11.12.1; implementador 18/11; verificador 18/11; pesquisador 18/11; layout 18/11 | WIN | todos | sim | 5 lugares, iguais |
| R114 | Nada dá como feito o que não conferiu | C §11.12.2; implementador 18/11; verificador 18/11; pesquisador 18/11; layout 18/11 | WIN TODO | todos | em parte | 5 lugares, iguais |
| R115 | Antes de escrever, a lista das falhas | C §11.12.3; implementador 18/11; verificador 18/11; pesquisador 18/11; layout 18/11 | WIN | codigo | em parte | 5 lugares, iguais |
| R116 | Peça de mentira não prova (D-767) | C §11.12.4; implementador 18/11; verificador 18/11; pesquisador 18/11; layout 18/11 | WIN TESTE | todos | em parte | 5 lugares, iguais · X8 |
| R117 | Gerente não aceita 'pronto' sem prova | C §11.12.5; implementador 18/11; verificador 18/11; pesquisador 18/11; layout 18/11 | GER TESTE | verif | em parte | 5 lugares, iguais |
| R118 | Ler a peça de fora antes de usar | C §11.12.6; implementador 18/11; verificador 18/11; pesquisador 18/11; layout 18/11 | WIN PESQ TODO | todos | em parte | 5 lugares, iguais |
| R119 | Perguntar: comece pelo que é e onde fica | C §11.13.1; implementador 13/11; verificador 13/11; pesquisador 13/11; layout 13/11 | PERG | todos | em parte | 5 lugares, iguais |
| R120 | Perguntar: nenhuma palavra de dentro | C §11.13.2; implementador 13/11; verificador 13/11; pesquisador 13/11; layout 13/11 | PERG | todos | sim | 5 lugares, iguais |
| R121 | Perguntar: print que prova | C §11.13.3; implementador 13/11; verificador 13/11; pesquisador 13/11; layout 13/11 | PERG | todos | em parte | 5 lugares, iguais |
| R122 | Perguntar: o caso que o Kaique encontra, print conferido | C §11.13.4; implementador 13/11; verificador 13/11; pesquisador 13/11; layout 13/11 | PERG | todos | nao | 5 lugares, iguais |
| R123 | Perguntar: o caminho, e se é defeito ou escolha | C §11.13.5; implementador 13/11; verificador 13/11; pesquisador 13/11; layout 13/11 | PERG | todos | em parte | 5 lugares, iguais |
| R124 | Perguntar: o que você escolhe e o que muda | C §11.13.6; implementador 13/11; verificador 13/11; pesquisador 13/11; layout 13/11 | PERG | todos | em parte | 5 lugares, iguais |
| R125 | Perguntar: curto, sem ficha | C §11.13.7; implementador 13/11; verificador 13/11; pesquisador 13/11; layout 13/11 | PERG | todos | em parte | 5 lugares, iguais |
| R126 | Perguntar: ele continua no controle? | C §11.13.8; implementador 13/11; verificador 13/11; pesquisador 13/11; layout 13/11 | PERG | todos | nao | 5 lugares, iguais |
| R127 | Perguntar: de onde veio | C §11.13.9; implementador 13/11; verificador 13/11; pesquisador 13/11; layout 13/11 | PERG | todos | em parte | 5 lugares, iguais |
| R128 | Perguntar: a situação de agora, sem repetir | C §11.13.10; implementador 13/11; verificador 13/11; pesquisador 13/11; layout 13/11 | PERG | todos | em parte | 5 lugares, iguais |
| R129 | Depois de 'Ainda não entendi': mudar o jeito | C §11.13 | GER | gerente | nao |  |
| R130 | A lista de conferência antes de mandar | C §11.13; C §10.10 | GER PERG | gerente | em parte | 2 lugares |
| R131 | Obra D-014: o que não vale durante a obra | C fim | GER TODO | todos | nao | X9 |
| R132 | Teste escrito antes do código, quando der | implementador 'O que você faz' | TESTE | codigo | nao |  |
| R133 | Nunca commit no master | implementador 'nunca'; layout 'Onde você trabalha' | GIT | codigo | sim | 2 lugares · X5 |
| R134 | Nunca fechar à força janela que o Samuel usa | implementador 'nunca'; verificador 'Como pilotar'; layout 'Como provar' | TODO TELA | todos | em parte | 3 lugares |
| R135 | Como entregar (lista do papel) | implementador 'Como entregar'; verificador 'Como entregar'; pesquisador 'Como entregar'; layout 'Como entregar' | TODO | todos | sim | 4 lugares, cada um com itens diferentes (vira o formulário único) |
| R136 | Commit e push a cada passo; ONDE-PAREI | implementador 19/10; verificador 19/10; pesquisador 19/10; layout 19/10 | GIT | todos | sim | 4 lugares, iguais · X12 |
| R137 | Verificador: não conserta código | verificador passo 1; verificador 'nunca' | TESTE | verif | sim | 2 lugares no verificador |
| R138 | Verificador: skill conferir-testes-visuais | verificador passo 4 | TESTE IMG | verif | nao |  |
| R139 | Defeitos conhecidos da Fase 1 em destaque | verificador passo 6 | IMG PERG | verif | nao | V2 |
| R140 | Pilotar: instância nova, nunca a dele | verificador 'Como pilotar' | TELA TESTE | verif | nao |  |
| R141 | Pilotar: mouse por mensagem nativa ao hwnd | verificador 'Como pilotar' | TELA TESTE | verif | nao |  |
| R142 | Pilotar: nunca pywinauto click_input/send_keys | verificador 'Como pilotar' | TELA TESTE | verif | sim |  |
| R143 | Pilotar: roda do mouse não funciona sem foco | verificador 'Como pilotar' | TELA TESTE | verif | nao |  |
| R144 | Pilotar: print fora da tela | verificador 'Como pilotar' | TELA TESTE | verif | nao | X8 |
| R145 | offscreen não tem fonte | verificador 'Como pilotar' | TELA TESTE | verif | nao |  |
| R146 | Verificador: prova de reversão numa cópia à parte | verificador 19/10 | TESTE | verif | em parte |  |
| R147 | Pesquisador: não repetir caminho fechado | pesquisador 'Leia antes' | PESQ | pesq | nao |  |
| R148 | Pesquisador: resumir com as próprias palavras | pesquisador 'O que você faz' | PESQ | pesq | nao |  |
| R149 | Pesquisador: roda aqui e no notebook do Kaique? | pesquisador 'O que você faz' | PESQ WIN | pesq | nao |  |
| R150 | Lido na fonte separado de dedução | pesquisador 'O que você faz'; pesquisador 'nunca' | PESQ TODO | todos | em parte | 2 lugares no pesquisador |
| R151 | Pesquisa gravada em docs/pesquisa/ com data e links | pesquisador 'O que você faz' | PESQ | pesq | sim |  |
| R152 | Não instalar no .venv sem pedido | pesquisador 'nunca' | PESQ TODO | todos | em parte |  |
| R153 | Layout: pista visual em toda área de clicar | layout 'Regras de tela' | TELA | codigo | nao |  |
| R154 | Toda função automática tem ligar e desligar | layout 'Regras de tela'; implementador 'O que você faz' (exceção da tela) | TELA IMG | todos | em parte | 2 lugares |
| R155 | Layout: ler a Lista de espera e as referências | layout 'Leia antes' | TELA | layout | nao |  |

### As contradições (não resolvidas, só apontadas)

- **X1.** Velocidade. §8 passo 5, o implementador e o verificador (passo 2) mandam rodar o teste_velocidade antes e depois e dizem 'nenhum item pode deixar o programa mais lento'. §4.6 e as regras de 19/10 dos quatro agentes dizem: não rode o completo no PC, use o filtro do GitHub, e lentidão pequena achada no meio da fase vai para a Fase 5. (regras R036, R037, R059)
- **X2.** Testes no PC. O implementador ('rode pytest tests -q antes de entregar'), o layout ('pytest tests -q passando') e o verificador (passo 1) mandam rodar a suíte inteira; o §4.6 e o bloco de 19/10 do mesmo arquivo dizem 'só um arquivo por vez no PC'. O bloco de 19/10 diz que vale sobre o de cima, mas o de cima continua escrito. (regras R034)
- **X3.** Páginas do antes/depois. §4.2 passo 1: 'roda a mudança em TODOS os PDFs do conjunto de teste'. §8 passo 6 e o verificador (passo 3): 'só com as páginas-gabarito daquele item'. (regras R028, R060)
- **X4.** Quem escreve 'PRONTO PARA CONFERIR'. §4.3: 'o Claude Code pode escrever'. O implementador: 'quem escreve isso é o verificador'. (regras R031)
- **X5.** Ramo principal. §10.3 ('só a gerente junta no master', 'conferir git log do master'), o implementador e o layout falam do master; o resto do CLAUDE.md (§4.6, §11.4) fala do fase-1, e a obra (D-014) junta no obra-2026-10-26. (regras R074, R133)
- **X6.** Quantos agentes. §11.11: 'no máximo dois; em 10/11 deixou três'. A memória (geral/pc-e-github.md §2 e geral/regras-de-trabalho.md §5): 'no máximo 3 a 4 agentes ao mesmo tempo'. A Central tem config agentes.max. (regras R106)
- **X7.** Layout e core/. O layout 'só mexe em ui/' e 'não escreve em core/' (§10.1 e layout.md); o §11.12 manda mudar a regra 'num lugar só, de preferência em core/ (a tela só chama)', e o próprio resumo do layout diz 'de preferência em core/'. (regras R071, R108)
- **X8.** Janela escondida. O verificador manda tirar print com a janela fora da tela (-32000) e os testes rodam offscreen (memória da gerente: 'testes offscreen, nunca abrir na tela'); o §11.12.4 (D-767) diz 'só conta rodando de verdade, à vista; nada em área escondida', e o plano da parte do Windows: 'nenhuma janela empurrada para fora da tela'. O texto não diz que uma vale para tela e a outra para Windows. (regras R116, R144)
- **X9.** Ritmo do trabalho. §2, §8 e §10.2 (uma fase por vez, conferir cada item antes do próximo, bug que impede se conserta na hora); a Obra (D-014, fim do CLAUDE.md) suspende 'conferir cada item' e 'uma fase por vez', e a D-765 suspende todo conserto até a entrega ao Kaique. Os arquivos dos agentes não citam nem a obra nem a D-765. (regras R006, R057, R073, R131)
- **X10.** Ordem de leitura. O CLAUDE.md põe o Livro de decisões como item 0; os quatro agentes começam por ESTADO-ATUAL → PLANO → CLAUDE.md e só no bloco de 26/10 dizem 'leia o Livro antes de tudo'; o INDICE da memória põe o Livro no item 5. (regras R001)

### Diferenças pequenas

- **X11.** Tabela: o §2 diz 'nada de tabela' (para o Samuel); o pesquisador entrega 'Tabela: o que é · licença...' (para a gerente). (regras R011)
- **X12.** Commit: o §8 passo 10 diz 'se aprovado, commit na hora'; os agentes dizem 'commit e push a cada passo no seu ramo'. (regras R062, R136)
- **X13.** Abrir a página: pergunta de agente abre no navegador dele na hora; conferência só abre se ele já fez a anterior (§10.10). (regras R089, R092)
- **X14.** Teste antigo: o §11.8 diz 'nunca mude um teste antigo para ele passar'; o plano da parte do Windows e a D-774 dizem 'só com o sim dele'; a D-644 e a D-663 abriram exceções. Não é contradição, mas o texto da regra não diz como se pede a exceção. (regras R102)
- **X15.** test_decisoes.py (§11.4 e agentes) e test_decisoes*.py (§11.8).
- **X16.** Os resumos de 18/11 nos agentes dizem 'os cinco pontos' e listam seis.

### Regras que parecem vencidas

- **V1.** Layout: 'só começa quando o Samuel entregar o plano de layout' e worktree .claude/worktrees/layout no ramo layout. Hoje há a obra do layout (memoria/itens/layout.md) e as frentes usam outras cópias e ramos. (regras R072)
- **V2.** Verificador: 'até a Fase 1 ficar pronta, avisar que moldura dourada e iluminura são defeito conhecido' (28/09). Não diz se ainda vale. (regras R139)
- **V3.** Agentes: 'memória: leia o INDICE se a pasta já existir no fase-1 (está sendo montada a partir de 19/10)'. Ela existe.
- **V4.** CLAUDE.md §7 'os testes (666 casos em 26/09/2026)' e §4.5 '241 funções'.

### O que está no meio das regras mas é informação

- §4.5: Quantos testes existem (241 funções, 279 casos em 07/09) (desatualizado: §7 diz 666 casos (26/09), §4.6 diz ~2.050, a memória ~2.100)
- §4.5: teste_botoes.py clica de verdade; teste_interface.py dirige a lógica (útil para trabalho de tela)
- §4.6: Comandos do GitHub e do filtro de velocidade (útil para testes)
- §7: Mapa de onde ficam as coisas e comandos (útil para todos)
- §7: Acervo e queixas do Kaique: onde ficam (útil para imagem)
- §9: O bug do menu Abrir já foi corrigido (história)
- §10.10: Endereços das páginas do claude.ai (só a gerente)
- §11: Por que o Livro existe (sessão 1 dos testes guiados) (história)
- §11.12: O que aconteceu em 10/11 e na etapa 5 (o porquê da regra; vai resumido no pacote)

---

## 2. As regras "sempre" (vão em todo pacote)

Escolhidas pelo que já deu errado mais vezes e pelo que o Samuel mandou que **todo** agente leia. Cada uma junta
várias regras do catálogo (entre parênteses), para o pacote não repetir.

1. **Só o que foi pedido e decidido.** Faça só o que o pedido e as decisões do Samuel mandam. Nada de botão, aviso, texto ou comportamento a mais. Se a decisão parecer impossível, contraditória ou pouco clara, ou se a única saída for um remendo: pare e escreva a pergunta (não faça diferente em silêncio, nem 'por enquanto').
   *Por que está aqui:* É a falha que mais se repetiu: decisões de 25/09 nunca construídas, e agentes mudando o que ele tinha definido (§11.7). (cobre R101, R099, R048, R006, R007, R110)
2. **O novo não estraga o que já funciona.** Antes de mexer, anote o que já está escolhido e testado ali. Teste antigo que quebra faz a entrega voltar; nunca mude um teste antigo para ele passar.
   *Por que está aqui:* Ele disse: 'essa é uma nova regra que todos os agentes precisam ler' (D-605). (cobre R102, R058)
3. **Sem gambiarra, em tudo.** Ache a causa, a função que decide, e todos os caminhos que chegam nela (grep). Mude num lugar só e faça todos os caminhos usarem esse lugar. Nada de desvio para um caso, nem conta ou lista copiada.
   *Por que está aqui:* 17 remendos achados em 10/11 e os 33 defeitos do atualizador em 18/11 têm a mesma causa (§11.12). (cobre R107, R108, R112, R105)
4. **Nada é feito sem conferir de verdade.** Só diga 'feito' do que você conferiu de verdade (abrindo o arquivo, olhando a imagem, perguntando ao Windows). Escreva toda ressalva. Nunca escreva 'APROVADO': só o Samuel aprova.
   *Por que está aqui:* 57 commits 'feito' e zero aprovados; '10 de 10 corretas' com seis erradas; 'Desligado' gravado sem desligar. (cobre R114, R030, R031, R029)
5. **Leia a peça de fora antes de usar.** Antes de usar uma peça que não é nossa (biblioteca, função do Windows, PowerShell, Velopack, Qt), leia a documentação e, se não bastar, o código. Anote o que ela faz em cada caso que usamos, com a fonte. Separe o lido do deduzido.
   *Por que está aqui:* Na etapa 5 o atualizador foi escrito sem ler o Velopack nem o Windows (§11.12.6). (cobre R118, R150)
6. **Decisões do Livro: cumprir e provar cada uma.** As decisões que o pedido traz (número e palavras dele) vão no começo do ONDE-PAREI; na entrega, como cumpriu cada uma, com teste ou print. Aparência não é prova. Palavras dele sempre copiadas do Livro, nunca de memória.
   *Por que está aqui:* As decisões se perdiam entre o pedido e o código (§11.3 e §11.4). (cobre R096, R097, R013)
7. **Pense em quem usa e no livro que sai.** Antes de mexer, escreva o que o Kaique vê e faz, passo a passo, antes e depois, e o que muda no PDF. Na entrega, confira.
   *Por que está aqui:* Regra do Samuel para todo agente (D-637). (cobre R104, R003)
8. **Pergunta ao Samuel: no ONDE-PAREI, na hora, no jeito dele.** Pergunta vai na seção 'Perguntas para o Samuel' do ONDE-PAREI assim que surge. Começa pelo que é e onde fica, sem palavra de dentro (número, arquivo, etapa), com print do caso real e 'O que você escolhe', com a sua sugestão. Você nunca grava na Central.
   *Por que está aqui:* 106 perguntas voltaram com 'Ainda não entendi' (§11.13); 8 perguntas ficaram escondidas num ONDE-PAREI (22/10). (cobre R089, R090, R119, R120, R124)
9. **Seu ramo, commit a cada passo, nada se apaga fora.** Trabalhe só na sua cópia e no seu ramo; commit e push a cada passo, com o ONDE-PAREI em dia. Fora de D:\programas\EditorImpressao nada se apaga; dentro, só o que você criou. Junção nunca com rm -rf. Acervo só para ler.
   *Por que está aqui:* O limite da conta já derrubou agentes; em 29/09 um agente apagou D:\d inteira. (cobre R136, R074, R080, R054, R133)
10. **Não abra agente, não use a tela dele, entregue à gerente.** Não abra outros agentes. Não abra janela nem pergunta do Windows na tela do Samuel, e não feche processo que não é seu, a não ser numa prova que a gerente combinou com ele. Entregue sempre à gerente.
   *Por que está aqui:* Cinco agentes rodando sem ele saber (10/11); caixas abertas na tela dele (30/09, 23/10). (cobre R106, R039, R134)

**Por que não mais de 10:** o problema de hoje é a regra que importa se perder no meio de 70 mil caracteres. Dez
regras curtas cabem numa tela. Tudo o que é de um tipo de trabalho vai pela etiqueta; o que é do jeito de entregar vai
pelo formulário (que o programa confere), e não precisa estar no "sempre".

---

## 3. A tabela "arquivos que o trabalho mexe → etiquetas"

Cobre **todos** os 4.665 arquivos do ramo obra e os 4.144 do `fase-1` (conferido com o esboço: 0 sem linha). Três
regras:

1. **Um arquivo recebe as etiquetas de todas as linhas que casam com ele.** Ex.: `ui/aviso_de_atualizacao.py` casa com
   a sua linha (tela + Windows) e com `ui/*` (tela).
2. **Linha de reserva** (`core/*`, `teste_*.py`, `relatorios/*`, `docs/plano/*`, `*.md`) só vale quando nenhuma linha
   mais própria casou. Assim `core/windows.py` é só Windows, e `core/filtros.py` é imagem.
3. **O conteúdo também conta:** se o arquivo (ou o pedido, quando o arquivo é novo) tem `subprocess`, `ctypes`,
   `powershell`, `schtasks`, `icacls`, `Update.exe`, `urllib`... ganha a etiqueta Windows, mesmo que a tabela não diga.
   Isso pega o script novo que conversa com o Windows sem ninguém lembrar de pôr na tabela.

**Arquivo que não está na tabela:** recebe **todas** as etiquetas (o pacote fica grande, nunca pequeno demais) e a
gerente é avisada no próprio pacote ("X não está na tabela"), para acrescentar a linha. Com um arquivo fora da tabela,
o pacote de exemplo passa de 29 para 73 regras.

**A pasta do relatório do próprio trabalho não conta** (todo trabalho escreve ONDE-PAREI e relatório). **Git e
arquivos vai sempre** (todo trabalho faz commit).

| Arquivo ou pasta | Etiquetas | Por quê |
|---|---|---|
| `core/windows.py` | WIN | o porteiro do Windows (arquivo novo do plano da parte do Windows) |
| `core/_testes_a_distancia_windows.py` | WIN | pede licença ao Windows |
| `core/testes_a_distancia.py` | WIN | planos de comandos do ligar, desligar e desfazer |
| `atualizacao.py` | WIN | atualizador, ajudante, tarefas do Windows, desinstalar |
| `publicar_versao_kaique.py` | WIN | publicar no GitHub com o Velopack |
| `empacotar.py` | WIN | monta o pacote do Velopack e o instalador |
| `empacotar_teste_velocidade.py` | WIN TESTE | empacota a medida de velocidade |
| `instalador.iss` | WIN | instalador antigo (Inno Setup) |
| `assinatura.py` | WIN | assinatura da versão para o Kaique |
| `versao.py` | WIN | número da versão e nome do pacote (lugar único) |
| `montar_motor_kraken.py` | WIN IMG | monta o Python à parte do Kraken |
| `motor_kraken/*` | WIN IMG | o motor do Kraken |
| `main.py` | TELA WIN | o começo do programa: primeira abertura, troca antes de abrir |
| `ui/aviso_de_atualizacao.py` | TELA WIN | aviso de versão nova |
| `ui/testes_a_distancia_ui.py` | TELA WIN | janela da senha dos testes à distância |
| `ui/tela_configuracoes.py` | TELA WIN | Configurações, inclusive os testes à distância |
| `ui/tela_de_carregamento.py` | TELA WIN | abre processo à parte (o brasão) |
| `compilar_*.py` | IMG WIN | compila DLL do ScanTailor (chama o compilador) |
| `core/nativo/*` | IMG WIN | DLLs compiladas: peça de fora |
| `core/paginas_em_outro_processo.py` | IMG WIN | lança processo à parte |
| `core/ocr_*.py` | IMG WIN | chama programas de fora (Tesseract, Kraken) |
| `ui/*` | TELA | telas |
| `ui/widgets/*` | TELA | peças de tela |
| `atalhos.py` | TELA | registro único dos atalhos de teclado |
| `brasao.py` | TELA | medidas do brasão |
| `gerar_brasao.py` | TELA | desenha o ícone e o giro |
| `recursos/*` | TELA | imagens do programa |
| `arte/*` | TELA | arte do brasão |
| `core/*` (reserva) | IMG | processamento do livro (o que não estiver acima) |
| `modelos.py` | IMG TELA | modelo de dados: ConfigFolha e ConfigPagina (mexer pede pergunta, §6) |
| `projetos.py` | IMG WIN | projetos salvos em %LOCALAPPDATA% |
| `historico.py` | IMG TELA | lista de projetos da tela de início |
| `historico_acoes.py` | IMG TELA | desfazer e refazer (mexer pede pergunta, §6) |
| `configuracoes.py` | TELA WIN | preferências; hoje também marcas do atualizador |
| `registro.py` | TODO | arquivo de log |
| `avaliar.py` | IMG TESTE | a régua dos filtros |
| `avaliar_selecao.py` | IMG TESTE | a régua da seleção |
| `montar_misto.py` | IMG | monta o Misto |
| `rodada_*.py` | IMG TESTE PERG | rodadas de comparação para o Samuel |
| `conferir_gravura_scantailor.py` | IMG TESTE | confere a gravura contra o ScanTailor |
| `gabarito/*` | IMG TESTE | páginas fixas de conferência (fora do git; junções!) |
| `terceiros/*` | IMG PESQ | código de fora (ScanTailor): ler a licença |
| `conferencia.py` | IMG PERG | página de antes/depois |
| `conferir.py` | IMG PERG | conferir amostras falando |
| `montar_para_conferir.py` | IMG PERG | relatorios/para-conferir.html |
| `gerar_prints.py` | IMG PERG | prints para o Samuel |
| `relatorio.py` | PERG | grava os três formatos |
| `docs/plano/central/*` | PERG GER | fonte da Central (só a gerente grava) |
| `docs/plano/para_a_*.py` | PERG GER | scripts que alimentam as páginas |
| `tests/*` | TESTE | testes de máquina |
| `tests/conftest.py` | TESTE TODO | vale para todos os testes: avisar a gerente |
| `tests/test_decisoes*.py` | TESTE | provas das decisões (D-605: teste antigo não muda) |
| `tests/*atualizacao*` | TESTE WIN |  |
| `tests/*ajudante*` | TESTE WIN |  |
| `tests/*desinstalar*` | TESTE WIN |  |
| `tests/*testes_a_distancia*` | TESTE WIN |  |
| `tests/*empacotar*` | TESTE WIN |  |
| `tests/*assinatura*` | TESTE WIN |  |
| `tests/*nome_do_pacote*` | TESTE WIN |  |
| `tests/*windows*` | TESTE WIN |  |
| `tests/*na_tela*` | TESTE TELA |  |
| `tests/*tela*` | TESTE TELA |  |
| `tests/*botoes*` | TESTE TELA |  |
| `tests/*menu*` | TESTE TELA |  |
| `tests/*paineis*` | TESTE TELA |  |
| `tests/*janela*` | TESTE TELA |  |
| `tests/promessas/*` | TESTE TELA | promessas dos botões (D-010) |
| `teste_botoes.py` | TESTE TELA | clica em botões de verdade |
| `teste_interface.py` | TESTE TELA | dirige a lógica da tela |
| `teste_velocidade.py` | TESTE IMG | medida de velocidade |
| `teste_*.py` (reserva) | TESTE IMG | testes soltos da raiz (geram relatório e imagem) |
| `rodar_suite_por_arquivo.py` | TESTE | roda a suíte um arquivo por vez |
| `pasta_de_dados_dos_scripts.py` | TESTE | pasta de dados dos scripts de teste |
| `requirements.txt` | TODO PESQ | trocar ou acrescentar biblioteca pede pergunta (§6) |
| `.claude/agents/*` | GER | regras dos agentes: só com o 'sim' do Samuel |
| `.claude/skills/*` | GER | skills do projeto |
| `.claude/*` | GER | outros arquivos do Claude Code (ex.: m.txt, settings) |
| `CLAUDE.md` | GER | regras: só com o 'sim' do Samuel |
| `docs/plano/DECISOES.md` | GER | o Livro: só a gerente escreve |
| `docs/plano/PLANO-DEFINITIVO.md` | GER | o plano: só o Samuel muda |
| `docs/plano/*` (reserva) | GER PERG | plano e estado |
| `docs/pesquisa/*` | PESQ | pesquisas |
| `memoria/*` | GIT | memória do projeto (conferir_memoria.py depois) |
| `historico/*` | GIT GER | handoff: só com pedido do Samuel |
| `velhos/*` | GIT | histórico |
| `relatorios/*` (reserva) | PERG | relatórios (três formatos) |
| `ONDE-PAREI.md` | GIT |  |
| `PEDIDOS.md` | GER | histórico desde 24/09 |
| `PLANO-RETOMADA.md` | GER | histórico |
| `LEIAME.md` | GIT |  |
| `.gitignore` | GIT GER | nunca desfazer sem avisar |
| `*.md` (reserva) | PERG | documento solto |

---

## 4. O pacote de exemplo: a peça nova do Windows

O próximo trabalho real é o **passo 1 do plano da parte do Windows**: escrever o "porteiro do Windows" e a pasta segura
(peças 1 e 2) em `core/windows.py`, com os testes da lógica em volta, sem mudar nenhum chamador. Abaixo está o texto
exato que o implementador receberia: o pedido curto da gerente (modelo da seção 7) e o pacote que o programa monta
(`esbocos/montar_pacote.py`) a partir de "implementador", dos dois arquivos novos e das decisões que o pedido toca.

**Tamanho, comparado ao de hoje:**

| | hoje | com o pacote |
|---|---|---|
| Regras que o agente tem de ler | CLAUDE.md 69.519 + implementador.md 12.115 + índice da memória 11.501 = **93.135** caracteres (até 167.069 com as fichas que o índice manda ler antes de tudo) | "sempre" 3.565 + regras do trabalho 5.624 = **9.189** |
| Regras de tela, imagem e Central que não servem para este trabalho | vão junto | não vão (dizem no fim que não vieram) |
| Decisões do Livro | a gerente copia à mão | o programa copia da linha do Livro (5.538 caracteres) |
| O que entregar | listas diferentes em cada arquivo de agente | um formulário só, conferido (1.521 caracteres) |
| **Total** | **93.135** + o pedido | **18.582** com o pedido |

Para comparar: o mesmo programa monta um trabalho de tela do girar: 35 regras do trabalho e 11.982 caracteres sem as decisões; um trabalho no filtro: 48 regras do trabalho e 14.203 caracteres sem as decisões; uma pesquisa: 23 regras do trabalho e 9.986 caracteres sem as decisões; o agente que tenta quebrar a peça do Windows: 94 regras do trabalho e 22.214 caracteres sem as decisões.

O pedido de exemplo inteiro está no arquivo `pedido-exemplo` (nos três formatos), e é este:

    > Você é o **implementador** do Editor de Impressão. Não abra outros agentes.
    >
    > **Trabalho:** escrever o porteiro do Windows e a pasta segura (peças 1 e 2), a peça única que todo o programa vai
    > usar para pedir licença, lançar processo, rodar comando, mexer em tarefa e ler como o Windows está. Vem do plano da
    > parte do Windows (`relatorios/plano-windows-2026-11-18/plano.md`, ramo `plano-windows-2026-11-18`): seção 1.2, peças
    > 1 e 2; seção 2, defeitos 1 a 16; seção 3, passos 1 e 2.
    > **Cópia e ramo:** `.claude/worktrees/porteiro-windows`, ramo `porteiro-windows-<data>`, a partir de `<commit do obra>`.
    > Relatório em `relatorios/porteiro-windows-<data>/`.
    > **Arquivos:** `core/windows.py` (novo) e `tests/test_windows.py` (novo). Mexer fora deles: pare e me avise (o pacote muda).
    > **Fica de fora:** nenhum chamador muda ainda (o atualizador e os testes à distância passam a usar o porteiro nos
    > passos 3 e 4). Nada roda no Windows de verdade neste trabalho: a prova à vista é a sessão A, que a gerente marca
    > com o Samuel depois do agente que tenta quebrar.
    > **Pronto quer dizer:** o formulário passa na etapa "antes de quem tenta quebrar"; o script da sessão A fica descrito
    > no ONDE-PAREI (o que cada linha da janela de prova vai mostrar).
    > **Leia:** este pacote inteiro; as seções do plano acima; as fichas `memoria/geral/ambiente.md` e
    > `memoria/licoes.md` (parte D). O CLAUDE.md só nas seções que o pacote cita, quando tiver dúvida.
    
    # Pacote de regras: o porteiro do Windows e a pasta segura (passo 1 do plano da parte do Windows)
    
    Papel: **implementador**. Arquivos: `core/windows.py` (novo), `tests/test_windows.py` (novo).
    Tipo de trabalho (sai dos arquivos): git e arquivos, testes, Windows e instalador (e qualquer conversa com programa de fora).
    
    ## 1. Sempre (todo trabalho)
    
    1. **Só o que foi pedido e decidido.** Faça só o que o pedido e as decisões do Samuel mandam. Nada de botão, aviso, texto ou comportamento a mais. Se a decisão parecer impossível, contraditória ou pouco clara, ou se a única saída for um remendo: pare e escreva a pergunta (não faça diferente em silêncio, nem 'por enquanto'). *Por quê:* É a falha que mais se repetiu: decisões de 25/09 nunca construídas, e agentes mudando o que ele tinha definido (§11.7).
    2. **O novo não estraga o que já funciona.** Antes de mexer, anote o que já está escolhido e testado ali. Teste antigo que quebra faz a entrega voltar; nunca mude um teste antigo para ele passar. *Por quê:* Ele disse: 'essa é uma nova regra que todos os agentes precisam ler' (D-605).
    3. **Sem gambiarra, em tudo.** Ache a causa, a função que decide, e todos os caminhos que chegam nela (grep). Mude num lugar só e faça todos os caminhos usarem esse lugar. Nada de desvio para um caso, nem conta ou lista copiada. *Por quê:* 17 remendos achados em 10/11 e os 33 defeitos do atualizador em 18/11 têm a mesma causa (§11.12).
    4. **Nada é feito sem conferir de verdade.** Só diga 'feito' do que você conferiu de verdade (abrindo o arquivo, olhando a imagem, perguntando ao Windows). Escreva toda ressalva. Nunca escreva 'APROVADO': só o Samuel aprova. *Por quê:* 57 commits 'feito' e zero aprovados; '10 de 10 corretas' com seis erradas; 'Desligado' gravado sem desligar.
    5. **Leia a peça de fora antes de usar.** Antes de usar uma peça que não é nossa (biblioteca, função do Windows, PowerShell, Velopack, Qt), leia a documentação e, se não bastar, o código. Anote o que ela faz em cada caso que usamos, com a fonte. Separe o lido do deduzido. *Por quê:* Na etapa 5 o atualizador foi escrito sem ler o Velopack nem o Windows (§11.12.6).
    6. **Decisões do Livro: cumprir e provar cada uma.** As decisões que o pedido traz (número e palavras dele) vão no começo do ONDE-PAREI; na entrega, como cumpriu cada uma, com teste ou print. Aparência não é prova. Palavras dele sempre copiadas do Livro, nunca de memória. *Por quê:* As decisões se perdiam entre o pedido e o código (§11.3 e §11.4).
    7. **Pense em quem usa e no livro que sai.** Antes de mexer, escreva o que o Kaique vê e faz, passo a passo, antes e depois, e o que muda no PDF. Na entrega, confira. *Por quê:* Regra do Samuel para todo agente (D-637).
    8. **Pergunta ao Samuel: no ONDE-PAREI, na hora, no jeito dele.** Pergunta vai na seção 'Perguntas para o Samuel' do ONDE-PAREI assim que surge. Começa pelo que é e onde fica, sem palavra de dentro (número, arquivo, etapa), com print do caso real e 'O que você escolhe', com a sua sugestão. Você nunca grava na Central. *Por quê:* 106 perguntas voltaram com 'Ainda não entendi' (§11.13); 8 perguntas ficaram escondidas num ONDE-PAREI (22/10).
    9. **Seu ramo, commit a cada passo, nada se apaga fora.** Trabalhe só na sua cópia e no seu ramo; commit e push a cada passo, com o ONDE-PAREI em dia. Fora de D:\programas\EditorImpressao nada se apaga; dentro, só o que você criou. Junção nunca com rm -rf. Acervo só para ler. *Por quê:* O limite da conta já derrubou agentes; em 29/09 um agente apagou D:\d inteira.
    10. **Não abra agente, não use a tela dele, entregue à gerente.** Não abra outros agentes. Não abra janela nem pergunta do Windows na tela do Samuel, e não feche processo que não é seu, a não ser numa prova que a gerente combinou com ele. Entregue sempre à gerente. *Por quê:* Cinco agentes rodando sem ele saber (10/11); caixas abertas na tela dele (30/09, 23/10).
    
    ## 2. As regras do seu trabalho (29)
    
    **Windows e instalador (e qualquer conversa com programa de fora)**
    - A janela nunca congela: Todo trabalho demorado em QThread, com barra e cancelar que funciona; esperar o Windows também (na etapa 5 a janela ficou parada 14 min). (CLAUDE.md §3)
    - Texto com acento, caminho sem acento: Texto de tela com acento (UTF-8); caminho de disco sem acento. (CLAUDE.md §3)
    - core/ não importa ui/: core/ nunca importa ui/: o processamento roda por linha de comando, sem janela. (CLAUDE.md §7)
    - Onde o programa guarda estado: %LOCALAPPDATA%\EditorImpressao guarda projetos e histórico; fechar e reabrir preserva tudo; desinstalar NÃO apaga essa pasta. (CLAUDE.md §7)
    - Uma peça só para conversar com o que está fora: Windows, disco, rede, GitHub, Velopack, outro programa: uma peça só para cada conversa; ninguém escreve a sua versão (na etapa 5, cada função pedia licença do seu jeito). (CLAUDE.md §11.12.1)
    - Antes de escrever, a lista das falhas: No ONDE-PAREI, para cada coisa que pode dar errado (sem licença, sem internet, disco cheio, 'Não', arquivo preso, desligar no meio), o que o programa faz; nunca pela metade. (CLAUDE.md §11.12.3)
    - Peça de mentira não prova (D-767): Teste com peça de mentira só prova a lógica em volta. O que mexe no Windows só conta rodando de verdade, à vista, e funcionando. Nada em área escondida. (CLAUDE.md §11.12.4) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
    
    **Testes**
    - Teste de máquina: o agente decide: O que tem resposta objetiva (fecha? páginas certas? memória? PDF estragado? cadernos? acento?) roda a cada mudança, sozinho. (CLAUDE.md §4.1)
    - Máquina ou olho, item por item: Todo item diz se foi conferido por máquina ou por olho. (CLAUDE.md §4.3)
    - Onde roda cada teste: No PC, um arquivo de teste por vez; a suíte inteira e o teste_botoes no GitHub (push antes); a entrega traz o número da rodada. (CLAUDE.md §4.6) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
    - Teste de reversão em todo conserto: Todo bug consertado ganha teste que FALHA no código antigo e passa no novo, com o bug na docstring; o verificador prova no antigo. Bug de imagem: uma medida, ou ressalva escrita. (CLAUDE.md §4.7)
    - Prova: caminho → função e o mesmo resultado em todos: Na entrega, a lista 'caminho → função' e uma prova em tests/ que cobra o mesmo resultado por todos os caminhos. (CLAUDE.md §11.12)
    - Teste escrito antes do código, quando der: Teste automático do que é objetivo, escrito antes do código quando der. (implementador.md 'O que você faz')
    
    **Git e arquivos**
    - Handoff só com pedido do Samuel: Só atualizar o handoff de historico/ quando o Samuel pedir. (CLAUDE.md §7)
    - Commit na hora com o defeito por extenso; nunca segredo: Commit com o defeito resolvido escrito por extenso e push; revisar o que vai no commit; nunca segredo; nunca desfazer o .gitignore sem avisar. (CLAUDE.md §8 passo 10)
    - Cada papel no seu lugar: Implementador: core/ e scripts, não ui/ (salvo pedido). Layout: só ui/. Verificador e pesquisador: não mexem no código do programa. (CLAUDE.md §10.1) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
    
    **Todo trabalho**
    - Ordem de leitura e quem manda: Quem manda: o Livro de decisões e o plano; o CLAUDE.md vem depois. O que ele disser contra o plano, vale o plano. (CLAUDE.md topo) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
    - PEDIDOS.md e handoff são histórico: PEDIDOS.md e o handoff em historico/ só servem de consulta; não dizem o que fazer. (CLAUDE.md topo)
    - Não recomeçar do zero: Não reescrever módulo inteiro nem reorganizar o que funciona. Testar não é licença para reconstruir. (Duas versões já fracassaram.) (CLAUDE.md §2)
    - Ir até o fim dentro da alçada: Decidir o que é da alçada e executar tudo, sem parar a cada passo. Se o contexto acabar, parar num commit com o programa rodando. (CLAUDE.md §2)
    - Honesto: avisar erro e risco: Se o Samuel ou a gerente estiver enganado ou correndo risco, avisar. Não concordar para agradar. (CLAUDE.md §2)
    - Python 3.14, não rebaixar: A máquina só tem Python 3.14. Nunca sugerir rebaixar. (CLAUDE.md §3)
    - Ler a memória antes: Antes de começar, ler memoria/INDICE.md e as fichas do assunto. A memória nunca contradiz o plano. (CLAUDE.md §4.9)
    - Item da fase atual, na ordem: O item vem da fase atual do plano; Lista de bugs no começo da fase. (CLAUDE.md §8 passo 1) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
    - Ideia nova vai para a Lista de espera; bug que não impede, para a Lista de bugs: Ideia nova: não fazer, anotar para a Lista de espera. Bug que impede a tarefa: consertar e dizer. Bug que não impede: anotar com data e print. (CLAUDE.md §10.2) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
    - Docstring em tudo o que tocar: Todo arquivo e função tocados ganham docstring: o que faz e o que é seguro ou arriscado mudar. (CLAUDE.md §10.5)
    - Plano novo não apaga pendência: Plano novo diz o que resolve e o que deixa de fora; nunca apaga pendência por omissão. (CLAUDE.md §10.6)
    - Prosa de checkpoint não é prova: Quando o estado importa, conferir o código e o git log, não o texto de checkpoint. (CLAUDE.md §10.8)
    - Obra D-014: o que não vale durante a obra: Durante a obra não valem 'conferir cada item antes do próximo' nem 'uma fase por vez'; nada entra no fase-1 antes da conferência final; duas decisões que se contradizem: vale a mais recente. (CLAUDE.md fim) **Atenção: outro texto das regras diz diferente; na dúvida, pergunte à gerente.**
    
    ## 3. As decisões que este trabalho precisa cumprir (copiadas do Livro)
    
    - **D-767** (18/11/2026): Chat, na etapa 5, depois dos 7 defeitos achados no Windows de verdade (a gerente explicou que os testes automáticos trocam as peças do Windows por peças de mentira): "não faça mais nada escodindo ou de mentira" · logo depois: "não quero fazer consertos quero que funcione" · e: "quero que faça as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros na hora de montar a estrutura do atualizador e testes a distancias"
      Na prática: O que mexe no Windows (pergunta de administrador, PowerShell, tarefas, licenças de pasta, instalar e desinstalar, testes à distância) só conta como pronto quando roda de verdade no Windows, à vista, e funciona. Teste automático com peça de mentira não prova que funciona. Nada de área de trabalho escondida nos testes. O objetivo não é remendar cada defeito, é a parte do Windows funcionar inteira (CLAUDE.md §11.12). O alcance exato (por exemplo, as versões de teste servidas de uma pasta do D: em vez do GitHub) está sendo confirmado com o Samuel.
    - **D-775** (18/11/2026): Chat: "o agente vai tentar quebrar antes de fazer o teste real na tela né?" (a gerente descreveu a ordem abaixo) · "ok"
      Na prática: A ordem de cada passo do plano da parte do Windows: (1) um agente escreve a peça; (2) os testes automáticos rodam, cobrando o jeito certo; (3) outro agente, que não escreveu, tenta quebrar (lê procurando falha não pensada, resultado não conferido e peça duplicada; roda o que dá sem pergunta do Windows); (4) só então a prova de verdade e à vista na tela do Samuel. Se o passo 3 achar problema, volta ao 1; o Samuel só é chamado quando a peça passou pelos três primeiros. Completa a D-767.
    - **D-605** (03/11/2026): "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os agentes precisam ler"
      Na prática: Nenhuma coisa nova (função ou escolha nova) muda o que já está escolhido e testado, nem cria problema novo. Antes de mexer, o agente lista o que já está escolhido e testado ali; se a coisa nova mudaria isso, para e pergunta; teste antigo que quebra faz a entrega voltar (nunca se muda o teste antigo para passar); o verificador confere também o que já funcionava ao redor.
    - **D-637** (05/11/2026): No chat, ao aprovar a D-636: "1- pode ser, só garanta que não crie mais problemas fazendo isso, você tem que pensar na experiencia do usario e no resultado final do livro dentro do programa, quando vai mudar algo, deixe isso anotado."
      Na prática: Regra: antes de mudar qualquer coisa, pensar na experiência de quem usa (o Kaique) e no resultado final do livro dentro do programa, e garantir que a mudança não cria problema novo. Isso fica escrito: no ONDE-PAREI de cada tarefa, uma seção "Como fica para quem usa e no livro" (o que a pessoa vê e faz, passo a passo, e o que muda no PDF), antes de começar e conferida na entrega. Junta-se à D-605.
    - **D-741** (17/11/2026): Chat, à pergunta "Se o Kaique clicar "Não" [no "Deseja permitir...?" da primeira abertura], do jeito que está, a pergunta não volta, e ele fica sem a atualização sozinha. Faço a pergunta voltar toda vez que ele abrir o programa, até ele clicar "Sim"? Sugiro que sim.": "Sim"
      Na prática: Se o Kaique disser "Não" à pergunta do Windows da primeira abertura (D-733, D-735), ela volta a cada vez que ele abrir o programa, até ele dizer "Sim". Depois do "Sim", nunca mais aparece (as atualizações seguem sem perguntar). Na conta de testes, nada pergunta (D-736).
    - **D-763** (17/11/2026): Chat, à pergunta "Posso mandar um agente fazer esse conserto? Sugiro que sim." (prova de 17/11, ramo `velopack-pasta-2026-11-17`: o nome interno do pacote, "EditorImpressao", é igual ao da pasta dos projetos; a cada abertura o Velopack grava ali uma cópia do Update.exe, e o desinstalador do .msi apagou a pasta `%LOCALAPPDATA%\<nome do pacote>` inteira, com o projeto de mentira dentro): "ok, pode fazer"
      Na prática: O nome interno do pacote do Velopack deixa de ser igual ao nome da pasta dos projetos (`%LOCALAPPDATA%\EditorImpressao`), antes da primeira instalação de verdade. A troca é num lugar só (`versao.ID_DO_PACOTE`), que todo o resto lê; o Kaique continua vendo "Editor de Impressão". Uma prova cobra que o nome do pacote nunca é o da pasta dos projetos, e a prova da pasta de reserva e do desinstalar é repetida com o nome novo. O nome novo exato é detalhe técnico (escolha da gerente, D-014). A instalação no PC do Samuel (etapa 5) espera esse conserto.
    - **D-717** (16/11/2026): Chat: "Fica a conta separada, escondida, só para os testes?" → "sim"
      Na prática: No notebook do Kaique, os testes à distância entram numa conta do Windows só para eles, sem poder de administrador, escondida da tela de entrada, com a senha que o Samuel criar (D-711). Os projetos de teste ficam na pasta dessa conta e nunca se misturam com os do Kaique.
    - **D-771** (18/11/2026): Chat, decisão 4 do plano da parte do Windows ("se ligar os testes à distância der erro no meio"; A = desfazer tudo, sugestão; B = deixar o que deu certo, com "Ligado pela metade"): "A"
      Na prática: Ligar os testes à distância é tudo ou nada: se um dos passos falhar, o programa desfaz sozinho o que fez naquela vez, deixa o computador como estava e diz na tela "Desligado" e o motivo. A tela sempre mostra o que o Windows tem de verdade (D-767). Nenhum botão novo. Completa a D-712/D-721.
    
    ## 4. O formulário da entrega (no seu ONDE-PAREI; um programa confere, campo vazio volta)
    
    - [ ] **Arquivos que vou mexer** (antes de ir ao agente que tenta quebrar)
    - [ ] **Decisões que esta tarefa precisa cumprir** (antes de ir ao agente que tenta quebrar)
    - [ ] **O que já está escolhido e testado aqui** (antes de ir ao agente que tenta quebrar)
    - [ ] **Como fica para quem usa e no livro** (antes de ir ao agente que tenta quebrar)
    - [ ] **A causa, a regra e todos os caminhos** (antes de ir ao agente que tenta quebrar)
    - [ ] **O que pode falhar e o que o programa faz** (antes de ir ao agente que tenta quebrar)
    - [ ] **O que li da peça de fora e onde** (antes de ir ao agente que tenta quebrar)
    - [ ] **O que foi feito** (antes de ir ao agente que tenta quebrar)
    - [ ] **Arquivos criados ou alterados** (antes de ir ao agente que tenta quebrar)
    - [ ] **Como cumpri cada uma** (antes de ir ao agente que tenta quebrar)
    - [ ] **Testes** (antes de ir ao agente que tenta quebrar)
    - [ ] **Caminho e função** (antes de ir ao agente que tenta quebrar)
    - [ ] **Máquina ou olho** (antes de ir ao agente que tenta quebrar)
    - [ ] **Ressalvas** (antes de ir ao agente que tenta quebrar)
    - [ ] **Ideias e bugs** (antes de ir ao agente que tenta quebrar)
    - [ ] **Perguntas para o Samuel** (antes de ir ao agente que tenta quebrar)
    - [ ] **Commit** (antes de ir ao agente que tenta quebrar)
    - [ ] **O que o agente que tentou quebrar achou** (antes da prova à vista)
    - [ ] **A prova de verdade** (antes de 'pronto para conferir')
    
    ## 5. O que você não recebeu, e quando parar
    
    Este pacote não traz as regras de: imagem, filtros e processamento do livro, perguntas e relatórios ao Samuel, pesquisa de peça de fora, tela (ui/). Se precisar mexer num arquivo fora da lista acima, pare e avise a gerente: o pacote muda. Se tiver pergunta para o Samuel, a regra 8 acima é o mínimo; a lista inteira está no CLAUDE.md §11.13, e a gerente devolve a pergunta que não passar. O texto que vale é o do CLAUDE.md: a fonte de cada regra está entre parênteses; leia lá quando tiver dúvida.

---

## 5. As conferências automáticas

Onde cada uma roda:

- **Teste em `tests/`**: roda no GitHub em toda entrega, ninguém consegue pular. É o lugar das buscas no código.
- **Antes do commit** (uma conferência que o git roda sozinho, guardada no repositório e ligada com uma configuração
  em cada cópia): a mesma busca, só nos arquivos mudados, em segundos. Avisa cedo; o GitHub garante.
- **Gancho do Claude Code** (um programa que o Claude Code roda sozinho em certos momentos; lido na documentação
  dele em 18/11, `code.claude.com/docs/en/hooks`): "antes de uma ferramenta" (`PreToolUse`: "Exit with code 2 to block
  the action"), e "quando o agente termina" (`SubagentStop`: código 2 "Prevents the subagent from stopping"). O gancho
  recebe o `agent_id` e o `agent_type` quando quem chama é um agente ("the input carries the agent_id and agent_type
  common input fields that identify the subagent"), e pode ficar no próprio arquivo do agente ("hooks can be defined
  directly in skills and subagents using frontmatter"). Ressalva lida lá: se o agente responder com `continue: false`,
  isso vence o código 2 e ele termina mesmo assim.
- **Lista de ferramentas do agente**: o arquivo de cada agente pode dizer quais ferramentas ele tem. Sem a ferramenta
  de abrir agente e a de gravar na Central, ele não consegue, nem por engano.

### 5.1 As que dão para fazer já (24)

| # | O que confere | Regra | Como | O que não pega | Falso alarme? |
|---|---|---|---|---|---|
| K01 | Conversa com o Windows fora da peça única (`ShellExecute`, `runas`, `schtasks`, `icacls`, `powershell`, `Update.exe`, `netsh`...) em texto do código | R113 | busca nas strings do código (sem docstring), teste em `tests/` + antes do commit | chamada disfarçada (texto montado em pedaços), uma segunda "peça" com outro nome | hoje acha 12 lugares, todos nos 3 arquivos que o plano muda: entram numa lista de exceções com data, que só diminui |
| K02 | `DETACHED_PROCESS` em qualquer lugar | R113, D-774 | busca | outro jeito de lançar que também falha | não: acha hoje `atualizacao.py` linhas 674 e 968 (o defeito 1 da etapa 5) |
| K03 | `icacls`, `/inheritance:r`, `/setowner`, `Set-Acl` | R113, plano peça 2 | busca | licença mudada por outra função do Windows | não: acha hoje `core/testes_a_distancia.py` 367-368 (o defeito 4) |
| K04 | Número de decisão (`D-123`) em texto que a pessoa vê (tela, avisos, passos e registro dos testes à distância) | R120, Lista de bugs 17/11 | busca nas strings, sem docstring nem comentário | número escrito de outro jeito ("decisão 731") | 1 em 15 hoje: um comentário dentro do texto da folha de estilo (`ui/estilo.py` 447). Acha também 2 dicas de tela reais em `ui/automatico.py` (765 e 2304) |
| K05 | Emoji em texto de tela | R019 | busca nas strings de `ui/` e `main.py` | emoji que chega por arquivo de dados | baixo (símbolos como "→" ficam de fora da faixa) |
| K06 | `core/` importa `ui/` | R049 | leitura da estrutura do código | importação feita por texto (`importlib`) | não |
| K07 | `tkinter` ou `customtkinter` | R015 | leitura da estrutura | — | não |
| K08 | Nome de arquivo com acento no programa | R020 | lista de arquivos do git | caminho com acento que o programa monta ao rodar | não (o esboço olha só `core/`, `ui/` e a raiz) |
| K09 | Relatório só em `.md` | R014 | na pasta do relatório do trabalho, o relatório principal tem `.html` e `.pdf` | relatório gravado fora da pasta | sim, para anexos em `.md`: só o principal é cobrado |
| K10 | "APROVADO" escrito por agente; `[x]` posto no plano ou no Livro num ramo de agente | R031 | linhas novas do ramo | aprovação dita com outras palavras | citação da regra ("nunca APROVADO"): fica de fora quando está entre aspas |
| K11 | Teste antigo mudado ou apagado | R102, D-605 | linhas tiradas ou trocadas dentro de funções `test_` que já existiam no commit de partida | teste antigo enfraquecido por fora (uma ajuda que ele usa mudou) | mudança autorizada (como a D-774): passa só se o commit citar a decisão que autoriza e ela existir no Livro |
| K12 | Função ou arquivo tocado sem docstring | R076 | leitura da estrutura, só nas funções mudadas | docstring vazia de sentido | funções de 1 a 2 linhas dentro de outra: ficam de fora |
| K13 | Mexeu fora do papel (implementador em `ui/` sem pedido, layout em `core/`, verificador ou pesquisador no programa) | R071 | arquivos mudados no ramo × papel do pedido | — | quando o pedido autoriza: o pedido lista os arquivos permitidos |
| K14 | Mexeu em arquivo fora da lista do pedido | camada 2 | arquivos mudados × "Arquivos que vou mexer" | — | não barra: avisa e o pacote é refeito |
| K15 | `requirements.txt` mudou | R048 | arquivos mudados | biblioteca instalada à mão no `.venv` | só passa com o "sim" citado no commit |
| K16 | Biblioteca que desenha ou inventa (`diffusers`, `realesrgan`, `gfpgan`...) | R022 | `requirements.txt` e importações | biblioteca nova que não está na lista | uma biblioteca grande usada só para apontar: a gerente põe na lista de permitidas |
| K17 | Agente mexeu no CLAUDE.md, nos agentes, no Livro, no plano ou no handoff | R056, R094 | arquivos mudados num ramo de agente | — | quando o pedido é esse (como hoje): o pedido diz |
| K18 | Terminar com mudança sem commit ou sem push | R136 | gancho "quando o agente termina" + `git status` | — | não |
| K19 | O formulário da entrega (seção 6) | R096, R104, R115, R118 e outras | gancho "quando o agente termina" + `esbocos/conferir_entrega.py` | se a resposta é verdadeira | o commit de partida tem de vir no pedido: comparando com o ramo errado, o esboço deu 30 alarmes falsos no ONDE-PAREI do plano de hoje |
| K20 | As palavras do Samuel citadas batem com o Livro, letra por letra | R013, R096 | parte do K19 | palavras certas na decisão errada | aspas tiradas de outra fonte (Central) que o Livro resume: aceitar também a fonte citada |
| K21 | A rodada do GitHub existe, é do último commit do ramo e passou | R034 | `gh run view` | — | commit só de documento depois da rodada: aceitar se o que mudou depois é só `.md` |
| K22 | A barra de rolagem continua cinza | R069 | busca em `ui/estilo.py` | — | não |
| K23 | Agente não abre agente; agente não grava na Central | R106, R090 | lista de ferramentas no arquivo de cada agente (muda o texto do agente: precisa do "sim") | — | não |
| K24 | `pywinauto` com `click_input` ou `send_keys` | R142 | busca nos scripts de teste | — | não |

Já existem hoje, e continuam: botões em inglês (`tests/test_botoes_em_portugues.py`), nenhuma janela na tela nos
testes (`tests/test_sem_janela_na_tela.py`), memória que não cresce com o livro
(`tests/test_memoria_nao_cresce_com_o_livro.py`), as provas das decisões (`tests/test_decisoes*.py`) e as promessas
dos botões (`tests/test_promessas.py`).

O esboço `esbocos/conferir_codigo.py` faz K01 a K08 (só lê). Rodado no obra de hoje: **15 achados com as exceções**
(todos do K04), e **31 sem as exceções** (12 do K01, 2 do K02, 2 do K03, 15 do K04).

### 5.2 As que precisam de estudo (14)

| # | O que conferiria | Regra | Por que precisa de estudo |
|---|---|---|---|
| E1 | Apagar fora do projeto, ou `rm -rf` numa junção | R080 | gancho "antes do comando": ler o comando com segurança (variável, script que apaga por dentro do Python); decidir o que fazer com a pasta temporária do próprio agente, que também fica fora do projeto |
| E2 | Fechar processo que não é seu | R134 | o gancho precisa saber quais processos o agente abriu (lista de números de processo) |
| E3 | Escrever no acervo ou nos originais | R054 | a permissão do Claude Code pode negar editar e gravar ali; um comando que grava por dentro escapa |
| E4 | O teste de reversão falha mesmo no código antigo | R038 | rodar os testes novos no commit de partida (no GitHub, como o filtro de velocidade); pesado |
| E5 | Conta ou lista copiada em dois arquivos | R108 | comparar trechos parecidos dá muito alarme falso; serviria como lista para quem tenta quebrar, não para barrar |
| E6 | Desvio para um caso (`if` com o nome de uma opção) | R105, R108 | idem |
| E7 | A janela congela (esperar o Windows, a rede ou outro programa fora do trabalho por trás) | R017 | o defeito 4 da etapa 5 era exatamente isso, mas separar o que roda por trás exige ler o código com cuidado |
| E8 | "Gravou que deu certo sem conferir" | R114 | difícil por busca; o melhor é a peça única só devolver as três respostas (deu certo, "Não", falhou) e o resto do código não ter outro jeito de saber |
| E9 | A prova foi de verdade e à vista | R116 | a máquina vê a hora e o print; não vê se foi à vista. Fica com quem tenta quebrar e com o Samuel |
| E10 | Página de lombada ou capa em teste | R044 | precisa marcar na lista do gabarito quais páginas não vão ser impressas |
| E11 | Texto de tela sem acento ("nao", "voce") | R020 | lista de palavras; muito alarme falso em nome de variável |
| E12 | O verificador abriu todas as imagens | R028 | contar no registro da conversa do agente as imagens abertas contra as geradas |
| E13 | Erro engolido (`except: pass`) | proposta do revisor de 10/11 | **ainda não é regra** (espera o Samuel); não se cobra o que ele não aprovou |
| E14 | O resto da lista de perguntas ao Samuel (o caso real, o controle, de onde veio) | R122, R126, R127 | só gente; a máquina já cobra o que dá no K19 |

---

## 6. O formulário da entrega

O agente preenche no próprio ONDE-PAREI, com estes títulos de seção. O programa (`esbocos/conferir_entrega.py`)
confere **em três etapas**: antes de ir ao agente que tenta quebrar; antes da prova à vista na tela do Samuel; antes de
"pronto para conferir". Campo que falta ou está vazio: o programa devolve, e o gancho não deixa o agente terminar.

**Texto de enchimento não vale:** "—", "...", "ver acima", "idem", "n/a", "TODO", "a fazer". "Não se aplica" só vale com
o motivo ("não se aplica: este passo não pede licença ao Windows").

| # | Campo (título da seção) | Quando é obrigatório | O que é preenchimento válido | O que o programa confere | O que ele não confere |
|---|---|---|---|---|---|
| F1 | Arquivos que vou mexer | sempre, antes de escrever | lista de caminhos | que bate com os arquivos mudados no fim (K14) e monta o pacote | se a lista era a certa |
| F2 | Decisões que esta tarefa precisa cumprir | sempre | cada linha: número e as palavras dele entre aspas | que a decisão existe e as palavras estão no Livro assim | se faltou alguma decisão (isso é da gerente, que manda no pedido) |
| F3 | O que já está escolhido e testado aqui | sempre | decisões e nomes de testes que existem | que os testes citados existem | se é a lista completa |
| F4 | Como fica para quem usa e no livro | sempre | antes e depois, passo a passo; o PDF (ou "nada muda no PDF") | que existe e fala de antes, depois e PDF | se é verdade |
| F5 | A causa, a regra e todos os caminhos | sempre que muda comportamento | causa; a função que decide; cada caminho → a função que ele usa | que cada função citada existe no código | se achou todos os caminhos (quem tenta quebrar procura de novo) |
| F6 | O que pode falhar e o que o programa faz | Windows e instalador | uma linha por caso, com o que o programa faz; os seis de sempre (sem licença, sem internet, disco cheio, "Não", arquivo preso, desligar no meio) aparecem ou dizem "não se aplica: motivo" | os seis casos | se pensou em todos os outros |
| F7 | O que li da peça de fora e onde | sempre que usa peça de fora | para cada peça e cada caso que usamos (deu certo, falhou, "Não", interrompida): o que ela faz, com endereço da documentação ou arquivo:linha do código dela | que cada item tem fonte; (a fazer) que cada importação ou programa de fora novo do código aparece aqui | se leu mesmo e entendeu certo |
| F8 | O que foi feito | sempre | uma ou duas frases | que existe | — |
| F9 | Arquivos criados ou alterados | sempre | lista | que bate com o git (sem contar a pasta do relatório) | — |
| F10 | Como cumpri cada uma | sempre | cada decisão do F2, com o teste ou o print | que nenhuma decisão do F2 ficou sem linha; que o teste e o print existem | se o teste prova a decisão |
| F11 | Testes | sempre | arquivos rodados no PC; número da rodada do GitHub | (K21) que a rodada é do último commit e passou | se os testes cobram o que importa |
| F12 | Caminho e função | sempre que F5 | a lista caminho → função e a prova em `tests/` que cobra o mesmo resultado em todos | que o teste existe | se cobre todos |
| F13 | Máquina ou olho | sempre | item por item | que existe | — |
| F14 | Ressalvas | sempre | o que não foi testado, o que pode dar errado | que existe e não é enchimento ("nenhuma" é aceito, mas vai marcado para quem tenta quebrar) | se escondeu alguma |
| F15 | Velocidade | imagem e processamento | número da rodada do filtro de velocidade | que a rodada existe | — |
| F16 | Ideias e bugs | sempre | "nenhum" vale | que existe | — |
| F17 | Perguntas para o Samuel | sempre | "nenhuma" vale; cada pergunta num `###` | sem palavra de dentro, com "O que você escolhe", print que existe, sugestão | se ele vai entender |
| F18 | Commit | sempre | o código do último commit, já enviado | que está no GitHub | — |
| F19 | O que o agente que tentou quebrar achou | antes da prova à vista (Windows e instalador; nos outros, quando a gerente pedir) | o relatório dele (outro agente), a lista de achados e, para cada um: consertado no commit X / não é defeito, porquê / vira pergunta | que o relatório existe, é de outro agente e cada achado tem destino | se ele procurou direito |
| F20 | A prova de verdade | antes de "pronto" (Windows e instalador) | o que rodou de verdade, onde, data e hora, à vista, e o print ou o registro da janela de prova; ou "falta a sessão X" (então não é "pronto") | data, hora e o arquivo de print ou registro | se foi à vista e se mostra o que diz |

**O agente que tenta quebrar (D-775)** recebe o pacote com **todas** as etiquetas (94 regras, uns 22 mil caracteres no
esboço), o formulário preenchido do outro e o código. Ele preenche o seu próprio relatório, com:

1. o que leu (arquivos e commits);
2. para F5, F6 e F7 do outro: o que conferiu, como (a busca que rodou, o documento que abriu), e o que achou;
3. caminhos que o outro não listou (procurados com busca no código, não lidos do formulário);
4. falhas não pensadas (casos fora do F6) e resultado não conferido (lugar que grava sem perguntar ao Windows);
5. as regras do catálogo que conferiu, por número, e as que não se aplicam;
6. os achados numerados, cada um com o lugar no código.

O mesmo programa confere que esses seis campos existem. A qualidade de quem quebra a gerente vê pela taxa: o que ele
achou e o que o Samuel achou depois na prova à vista.

---

## 7. Como a gerente passa a montar o pedido

1. Escreve o pedido curto (modelo abaixo), com a lista de arquivos e as decisões.
2. Roda o montador: `python montar_pacote.py <papel> docs/plano/DECISOES.md "<título>" <D-...> <arquivos>`.
3. Lê o aviso de arquivo fora da tabela, se houver, e acrescenta a linha na tabela.
4. Junta: pedido + pacote. Manda.

**Modelo do pedido:**

> Você é o **<papel>** do Editor de Impressão. Não abra outros agentes.
>
> **Trabalho:** <uma frase do que fazer, sobre a coisa inteira>. Vem de <documento, seção>.
> **Cópia e ramo:** `<pasta>`, ramo `<ramo>`, a partir de `<commit>`. Relatório em `relatorios/<nome>/`.
> **Arquivos:** <lista>. Mexer fora dela: pare e me avise (o pacote muda).
> **Fica de fora:** <o que não faz neste trabalho>.
> **Pronto quer dizer:** <ex.: o formulário passa na etapa "antes de quem tenta quebrar">.
> **Leia:** este pacote inteiro; <seções do plano>; as fichas <...> da memória. O CLAUDE.md só nas seções que o pacote
> cita, quando tiver dúvida.
>
> <o pacote, montado pelo programa>

Seis linhas da gerente; o resto sai do programa. O que antes ela copiava à mão (as regras de cada assunto, as palavras
do Livro) não depende mais da memória dela.

---

## 8. O que pode dar errado, e como cada risco é coberto

| Risco | O que acontece | Como fica coberto |
|---|---|---|
| Regra nova sem etiqueta | o agente não recebe | o catálogo é a lista que o montador lê: regra fora dele não existe para o pacote. Uma conferência (teste) cobra que cada número de regra do CLAUDE.md esteja no catálogo, e que toda regra do catálogo tenha etiqueta |
| Etiqueta errada (ex.: regra de Windows marcada só como tela) | o agente de Windows não recebe | quem tenta quebrar recebe tudo; achado dele que cair numa regra que o pacote não trouxe vira correção da etiqueta |
| Tabela de arquivos atrasada | arquivo novo sem linha | arquivo fora da tabela recebe **todas** as regras (o pacote cresce, nunca encolhe) e a gerente é avisada; o conteúdo também dá etiqueta (subprocess → Windows); um teste cobra que todo arquivo do git tem linha |
| O trabalho se espalha para arquivos que não estavam no pedido | o agente seguiu com o pacote errado | K14 avisa no commit e no fim; o pacote é refeito com os arquivos de verdade |
| A máquina dá falso alarme | o agente perde tempo ou contorna | exceções com data e motivo, numa lista que só diminui; alarme de conferência nova começa como aviso, e só passa a barrar depois de uma semana sem falso alarme; toda exceção nova é da gerente |
| O agente contorna a conferência (`--no-verify`, `continue: false`, texto montado em pedaços) | passa sem cobrar | o teste em `tests/` roda no GitHub e ninguém pula; quem tenta quebrar procura contorno de propósito |
| O agente preenche o formulário de qualquer jeito | campo existe, resposta vazia de sentido | o programa cobra o que dá (a decisão existe, o teste existe, a fonte tem endereço); o resto é de quem tenta quebrar, que confere F5, F6 e F7 contra o código; "nenhuma ressalva" vai marcado para ele |
| O texto curto do pacote fica diferente do texto que vale | o agente cumpre a versão curta errada | cada regra do pacote diz de onde veio; quando a regra muda, o catálogo muda no mesmo commit (um teste pode cobrar que a seção citada ainda existe) |
| As contradições continuam | o agente recebe as duas | o pacote marca cada regra com contradição ("outro texto das regras diz diferente; na dúvida, pergunte à gerente") até o Samuel resolver |
| Gerente esquece de mandar a decisão certa | F2 incompleto | o programa não pega. A Central já liga decisão a etapa e dono; o Livro diz em "onde toca" quais arquivos cada decisão toca: dá para o montador sugerir as decisões dos arquivos (a fazer) |
| O pacote fica grande de novo com o tempo | volta o problema de hoje | o montador mostra o tamanho; o "sempre" tem limite de 10 |
| O agente não lê o CLAUDE.md e perde uma regra que não estava no pacote | falha que a regra pegaria | o pacote diz o que não trouxe e quando parar; quem tenta quebrar lê tudo |

---

## 9. Perguntas para o Samuel

Ressalva sobre as imagens (regra 3 do jeito de perguntar): nenhuma destas perguntas é sobre uma tela do programa.
A prova de cada uma é o exemplo de verdade que está nesta proposta (o pacote da peça nova do Windows e o que a
conferência achou no código de hoje). A gerente põe esses exemplos ao lado na Central.

### 1. O agente passa a receber só as regras do trabalho dele, em vez do livro de regras inteiro?

**Do que se trata.** Quando a gerente chama um agente, ele lê hoje o livro de regras inteiro (umas 40 regras, 70 mil
letras) e o arquivo do papel dele. Na etapa 5, os agentes do atualizador leram as regras e mesmo assim fizeram a
gambiarra que a regra proíbe.
**Como seria.** Um programa olha quais arquivos o trabalho vai mexer e monta um pacote: 10 regras que valem sempre, as
regras daquele tipo de trabalho (Windows, tela, imagem...) e as suas palavras copiadas do Livro de decisões. Na peça
nova do Windows, são 39 regras curtas em vez do livro inteiro, umas 9 vezes menos texto. O livro de regras continua
inteiro, do mesmo jeito: é dele que o pacote sai. O agente que tenta quebrar recebe tudo.
**O que você escolhe:**
- **Opção 1 (sugestão):** o agente recebe o pacote; o livro inteiro fica para consulta e para quem tenta quebrar. Muda
  só o jeito de passar as regras; nenhuma regra muda.
- **Opção 2:** o agente recebe o pacote **e** continua lendo o livro inteiro. Mais seguro de não faltar nada, mas
  continua o problema de hoje: a regra que importa se perde no meio.
- **Só comentário.**
**Situação:** só proposta; nada foi ligado.

### 2. As conferências que barram o trabalho podem entrar já?

**Do que se trata.** São programas pequenos que leem o código e não deixam o trabalho entrar se acharem uma coisa
proibida. Exemplo de verdade: rodando no código de hoje, eles acham o jeito de abrir o PowerShell que fazia o
"Reiniciar agora" fechar e não voltar, e o comando que trancou a pasta dos testes à distância. Os dois defeitos que
você viu na instalação de verdade teriam sido barrados antes.
**Como seria.** 24 conferências que dão para fazer já. Rodam no GitHub em toda entrega (ninguém consegue pular) e
antes de cada gravação no git. Os lugares de hoje que o plano da parte do Windows ainda vai mudar ficam numa lista de
exceções com data, que só diminui. Nada muda para o Kaique.
**O que você escolhe:**
- **Opção 1 (sugestão):** entram já, com a lista de exceções; uma conferência nova só avisa na primeira semana e depois
  passa a barrar.
- **Opção 2:** entram só depois da entrega ao Kaique (você pediu que nenhum conserto comece antes disso; isto não muda
  o programa, mas é trabalho novo).
- **Só comentário.**
**Situação:** só proposta, com dois esboços que só leem.

### 3. Posso tirar dos agentes a ferramenta de abrir outro agente e a de gravar na Central?

**Do que se trata.** Cada agente tem uma lista de ferramentas. Hoje a regra diz "não abra outro agente" e "agente não
grava na Central", mas eles têm as duas ferramentas na mão. Em 10/11 um agente abriu três ajudantes e você viu cinco
rodando.
**Como seria.** As duas ferramentas saem da lista de cada agente. Ele não consegue mais, nem por engano. A gerente
continua com as duas. Isso muda o arquivo de regras de cada agente (só a lista de ferramentas).
**O que você escolhe:**
- **Opção 1 (sugestão):** sim, tirar as duas.
- **Opção 2:** deixar como está e confiar na regra escrita.
- **Só comentário.**
**Situação:** só proposta.

### 4. A entrega do agente passa a ter um formulário que um programa confere?

**Do que se trata.** Hoje cada arquivo de agente tem a sua lista do que entregar, e a gerente confere a olho. Na etapa
5, o "pronto" chegou sem a lista do que pode falhar e sem a leitura do Velopack.
**Como seria.** Um formulário só, de 20 campos (o que pode falhar e o que o programa faz; o que leu da peça de fora e
onde; a prova de verdade; o que achou o agente que tentou quebrar...). Um programa não deixa o agente terminar com
campo vazio, e confere o que dá: que a sua frase está no Livro do jeito que você disse, que o teste citado existe, que
a rodada do GitHub passou. Se a resposta é boa, quem vê é o agente que tenta quebrar, antes de chamar você.
**O que você escolhe:**
- **Opção 1 (sugestão):** sim, o formulário e o programa que confere, começando pela parte do Windows.
- **Opção 2:** o formulário, mas conferido só pela gerente, sem o programa.
- **Só comentário.**
**Situação:** só proposta, com um esboço que só lê.

### 5. Posso trazer, uma por vez, as regras que dizem o contrário uma da outra?

**Do que se trata.** Lendo tudo, achei 10 lugares em que duas regras não dá para cumprir juntas. Exemplo: uma regra
manda tirar o print da janela escondida, fora da tela; a regra nova da parte do Windows diz que nada conta se não for à
vista. Outra: uma manda medir a velocidade no seu PC a cada item; outra diz para não medir no PC no meio da fase.
**Como seria.** Uma pergunta por contradição, com o texto das duas regras e a sugestão. Até você responder, o pacote
avisa o agente: "outro texto das regras diz diferente; na dúvida, pergunte à gerente".
**O que você escolhe:**
- **Opção 1 (sugestão):** sim, uma por vez, primeiro as duas que tocam o próximo trabalho do Windows (a janela escondida
  e a velocidade).
- **Opção 2:** a gerente propõe as 10 de uma vez, numa lista.
- **Só comentário.**
**Situação:** só apontadas; nenhuma resolvida.

---

## Detalhe técnico (para a gerente)

- Arquivos desta proposta: `proposta` (este, nos três formatos), `pedido-exemplo` (três formatos), `pacote-exemplo.md`
  (o que o montador devolve), `ONDE-PAREI.md`, e `esbocos/`: `catalogo.py` (as 155 regras em dados),
  `tabela_arquivos.py`, `montar_pacote.py`, `conferir_codigo.py`, `conferir_entrega.py`, `montar_proposta.py` (gera
  este documento a partir dos dados). Nada está ligado; nada foi rodado contra o PC fora de leitura do git e do código.
- Contas: `python esbocos/catalogo.py` dá os números do catálogo; `python esbocos/tabela_arquivos.py obra-2026-10-26`
  confere a cobertura da tabela.
- Achado no caminho, para a Lista de bugs (não impede; D-765 segura o conserto): as dicas de tela do Automático
  "desligar as marcadas" e a do retângulo do corte mostram "D-068" e "D-094" ao Kaique (`ui/automatico.py` 765 e
  2304, no obra). Mesmo tipo do bug de 17/11 dos passos dos testes à distância.
- O `CLAUDE.md` da cópia `obra-juncao` (66.755 caracteres) é mais velho que o do `fase-1` (71.186): o catálogo usa o do
  `fase-1`.
