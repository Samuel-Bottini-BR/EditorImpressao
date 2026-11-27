# Ordem de serviço da triagem das regras e dos erros (27/11/2026)

Colada pelo Samuel no chat da gerente em 27/11/2026, sem mudar nada. O que a gerente preparou está no fim.

---

Triagem das regras e dos erros (frente 1b — decisão do Samuel, 27/11). SÓ LEITURA: nenhuma regra nova, nenhum arquivo do projeto muda, nenhuma skill ou gancho é criado ainda. Agente NOVO, separado do da vistoria (os dois só leem; podem rodar ao mesmo tempo).

OBJETIVO. Uma tabela que diga, para cada regra que existe hoje e para cada tipo de erro que já aconteceu, qual é o destino dele — para depois a gente construir de uma vez: skills, ganchos, porteiro, fiscais e o modelo de ordem de serviço.

OS DESTINOS POSSÍVEIS (um por linha, com o motivo em uma frase):
- FISCAL RÁPIDO: o computador confere lendo o código, sem abrir o programa (< 10 s). Roda num gancho depois de cada mexida em arquivo e no porteiro. Ex.: a trava dos donos.
- FISCAL GITHUB: o computador confere, mas é lento (abre o programa, processa página).
- GANCHO: ação que deve acontecer sozinha num momento fixo (antes/depois de mexer em arquivo, ao gravar, ao terminar).
- PERMISSÃO: coisa que o agente simplesmente não deve poder fazer (pasta, comando).
- SKILL: procedimento, jeito de fazer (ex.: relatório nos três formatos; conferência curta; como perguntar ao Samuel). Lido só quando o serviço pede.
- FICA NO CLAUDE.md: contexto que vale sempre e não se descobre lendo o código (quem é o Kaique, o que é o programa, onde ficam as coisas).
- REGRA POR PASTA: vale só para certos arquivos (.claude/rules com paths).
- APAGAR: repete outra, ou protege peça que não existe mais, ou é registro de história.
- DÚVIDA: o agente não decide; vai para o Samuel.

PARTE A — AS REGRAS DE HOJE. Fontes: CLAUDE.md (819 linhas), .claude/agents/{implementador,verificador,pesquisador,layout}.md, regras_dos_agentes/porteiro.py (as conferências K01–K09 e as 164 exceções), ganchos/pre-commit, .claude/skills/. Uma linha por regra: texto resumido · onde está (arquivo e seção) · desde quando e por que entrou (a data e o erro que a motivou, quando o texto diz) · destino · motivo · se já existe teste que cobre essa regra (nome do arquivo em tests/) ou se a regra está em mais de um arquivo (quais).

PARTE B — OS ERROS QUE JÁ ACONTECERAM. Fontes: docs/plano/DECISOES.md (ramo obra-2026-10-26; as decisões que nasceram de erro), a Central LIDA DA PÁGINA (respostas com "não gostei", "ainda não entendi", "isso é gambiarra", "o agente fez sem eu pedir", e as abas de auditoria), relatorios/atualizador-novo/quem-tenta-quebrar-*/relatorio.md, relatorios/para-o-fable-2026-11-23/resposta-do-fable.md, memoria/bugs.md, relatorios/testes-guiados/ (a lista única de 23/10), relatorios/conferencia-samuel-*.md, relatorios/obra-auditoria-escolhas/.
Não é uma linha por erro: é uma linha por TIPO de erro (ex.: "conta repetida em outro lugar", "agente acrescentou o que não foi pedido", "conserto só no botão", "relatório que o Samuel não entendeu", "teste que confere texto e não comportamento", "janela aberta na tela do Samuel"). Para cada tipo: 3 exemplos com referência (D-xxx, id da Central ou arquivo) · quantas vezes aconteceu (contagem aproximada) · a CAUSA, separando: (1) erro de programação — o pedido do Samuel estava claro e foi feito diferente; (2) mudança de ideia — foi feito como pedido e o Samuel quis outra coisa depois de ver; (3) dúvida — não dá para saber (vai para o Samuel). Para decidir entre 1 e 2, comparar a frase original do Samuel (o Livro e a Central guardam) com o que foi entregue. Os de tipo (2) ficam só como registro. · destino · qual fiscal/skill/gancho cobriria esse tipo daqui em diante.

PARTE C — A ORDEM DE SERVIÇO. Levantar como os pedidos aos agentes são escritos hoje (o modelo fixo de 10/11 e exemplos reais: os ONDE-PAREI e relatórios que citam o pedido recebido). Propor, sem implementar: (1) o modelo com os campos obrigatórios — pelo menos: a regra do programa que o serviço toca; onde ela deve morar no core; todas as cópias conhecidas (da vistoria); "Dentro" (arquivos que podem mudar) e "Fora" (o que não pode); a prova que falha antes e passa depois; o que o Kaique vê; (2) como travar: um programinha que recusa a ordem sem esses campos antes de abrir o agente, e o verificador marcar qualquer arquivo mudado fora do "Dentro". Dar 2 opções de onde essa trava mora e uma recomendação.

ENTREGA: relatorios/triagem-das-regras-2026-11-27/ com tabela-regras.md, tabela-erros.md, ordem-de-servico.md e resumo.md (contagens por destino; os 10 fiscais que mais erros teriam evitado, em ordem; a lista de DÚVIDAS para o Samuel). Também em .html. Linhas curtas; sem plano de construção; sem regra nova. Commit pode (não há segredo). O Fable e o Samuel leem juntos.

Antes de começar: estimativa de tempo e confirmação de que nada muda fora dessa pasta.

---

## O que a gerente preparou (27/11/2026)

- **Cópia de trabalho própria:** `D:\programas\EditorImpressao\.claude\worktrees\triagem-regras`, ramo
  `triagem-regras-2026-11-27`, tirado do `obra-2026-10-26` em `336d2a37` (a vistoria continua na cópia `obra-juncao`,
  sem cruzar commits com esta).
- **A Central lida da página em 27/11/2026** (o agente não tem acesso a ela): as 353 respostas e as 28 abas da coleção
  `conferencias` (inclusive as seis de auditoria), um arquivo JSON por documento, em
  `C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\50e82f38-e05a-42cd-b347-2b8b579ff516\scratchpad\central-27-11\`
  (pastas `respostas\` e `conferencias\`). Ficam fora do git.
- **Dois CLAUDE.md:** o desta cópia (ramo `obra-2026-10-26`) tem 819 linhas, o número da ordem; o da pasta principal
  (`D:\programas\EditorImpressao\CLAUDE.md`, ramo `fase-1`, o que o Claude Code carrega) tem 859. A tabela parte do de
  819 e diz, em cada regra, se ela está só num dos dois.
