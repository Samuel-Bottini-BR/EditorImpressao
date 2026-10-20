# O jeito do Samuel: como ele entende, como ele decide, o que ele pediu como regra

O Samuel coordena a parte digital do projeto e toma as decisões. Ele **não é programador**, não fala
inglês e não lê relatório longo. Ele decide **vendo** (imagem, lado a lado, ampliado), não lendo
número. Ele quer **opções** dentro do programa, e só ele aprova.

As frases dele estão **entre aspas, literais**, com data e fonte. O que não está entre aspas é resumo.
O plano manda: se algo aqui discordar do [plano](../../docs/plano/PLANO-DEFINITIVO.md), vale o plano.

Abreviações: **H** = [histórico](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)
(PARTE -N §k); **R** = [plano, Registro de mudanças](../../docs/plano/PLANO-DEFINITIVO.md).
Montado em 20/10/2026 pelo ajudante A.

---

## 1. Como ele entende melhor uma pergunta

**A receita que funciona** (H, PARTE -15 §6, "Como o Samuel entende uma pergunta", escrita depois das
rodadas de layout de 12/10/2026):

1. Começar por **"O que você está escolhendo: …"**.
2. No máximo **3 parágrafos curtos**.
3. A **primeira imagem é só a parte que muda, ampliada**; depois a tela inteira.
4. **Uma imagem por opção** e sempre a opção **"Ainda não entendi"** (H, PARTE -13 §0, depois que ele
   não entendeu três perguntas da rodada 4 que falavam em "o jeito rápido e o manual" sem mostrar).
5. Em conferência de imagens, **cada quadro tem a sua pergunta e o seu comentário** (H, PARTE -14 §6).
6. **Nunca retângulo por cima do conteúdo.** Para mostrar o que foi tirado: uma linha de quadros lado a
   lado, preto = fica no papel, vermelho = o programa tirou, a folha inteira em cima e a parte ampliada
   pintada de amarelo transparente, legenda fixa embaixo; a grade 3×3 confundiu (H, PARTE -12 §0;
   PARTE -9 §1, o retângulo que escondeu o "A" de "CRISTÃ").
7. Toda pergunta com foto, **dizendo exatamente onde olhar**, com o resultado ao lado do original, e as
   opções escritas por extenso (H, PARTE -9 §1).

**Os pedidos de 12/10/2026 nas rodadas de layout** (R, 12/10/2026): "Explique de maneira mais fácil e
concisa.", "explique melhor e de maneira mais facil o que estou escolhendo", "explique melhor, por favor
e de forma mais simples.". Antes: "eu não entendi, me de mais exemplos e explique melhor." (09/10,
`g6-retangulo`); "não entendi, explique melhor e com exemplos." e "Isso ficou horrivel para conferir,
[...] traga exemplos melhores e que eu consiga destinguir o que é para ver" (07/10). Quando a pergunta
volta explicada de novo, ele costuma decidir na segunda leitura.

**Sem jargão.** "não entendi do que você está falando, seja mais simples" (06/08/2026, H, PARTE 2, pedido
60). Primeiro a frase que se entende, depois o número: "O programa estava estragando a capa dos livros",
não "o balanço de branco eleva o ruído de 5,5 para 17,5" ([CLAUDE.md](../../CLAUDE.md) §2). Termos de
git e de programação: dizer o que significam e o que muda para ele, com a recomendação (memória do
Claude Code no PC do Samuel, "Explicar termos em português simples"). Sempre em português: "você está
falando em inglês e eu não falo em inglês" (05/10/2026; memória da gerente no PC do Samuel, "Responder
sempre em português").

**Curto no chat, detalhe em arquivo.** "não entendi, o jeito que você escreve fica dificil para eu
entender as informações, seja mais direto por favor" (01/08/2026, pedido 23); "muita coisa para eu ler,
seja mais consigo por favor, fale em quatro linhas o que eu preciso escolher" (05/08/2026, pedido 51).

**Ele não abre `.md`.** O Acrobat recusa o arquivo. Todo relatório de teste ou conferência sai em três
formatos (`.md`, `.html`, `.pdf`) por `relatorio.gravar` ([CLAUDE.md](../../CLAUDE.md) §2).

**Ele quer ver, não ler.** Na Rodada 6 de 05/10/2026: "eu quero ver a coisa quando eu for escolher algo,
preciso que seja mais intuitivo [...] esse arquivo html está cheio de coisa, não está organizado está
acumulando respostas, isso precisa ser salvo em outro lugar [...] que eu possa entrar e clicar" (memória
da gerente no PC do Samuel, "escolhas visuais"). Daí as **páginas do claude.ai** com banco de dados
(ver [paginas-claude-ai.md](paginas-claude-ai.md)).

**Responder na página, não no chat.** Quando ele comenta numa página de conferência, a resposta vai
**na própria página** (explicação refeita, desenho, pergunta nova); no chat só um aviso curto
([CLAUDE.md](../../CLAUDE.md) §10.10, regra de 07/10/2026). O comentário anterior **sobe e fica fixado**
quando a pergunta volta.

**Mas, quando a pergunta é feita no chat** (como as cinco decisões de 19/10/2026), a explicação de cada
opção vai **por extenso no chat**, com um caso real, e ele responde digitando ("1", "2"); a caixinha de
pergunta cobria o texto e ele respondeu várias vezes "não entendi", "onde está a ilustração?",
"explica no chat" (memória do Claude Code no PC do Samuel, "explicar no chat sem caixinha", 19/10/2026).
As duas regras convivem: **conferência → página; decisão perguntada no chat → explicação no chat.**

**Uma decisão por vez.** Em sessão de planejamento, explicar cada item e confirmar antes de passar ao
próximo; ele disse em 17/09/2026 que estava "muito confuso" quando as perguntas vieram juntas (memória
do Claude Code no PC do Samuel, "Planejar devagar, um por um"; H, PARTE -5: "várias rodadas de 'me
explique melhor'").

**Pergunta dele é pergunta de fato.** "Não era X, né?" pede conferência no registro e a resposta
"está escrito em …", não mudança de arquivo (memória do Claude Code no PC do Samuel, "Não mudar o
combinado por pergunta", caso de outro projeto em 19/09/2026). E não perguntar de novo o que ele já
respondeu: "Porque essa opção voltou ? eu já não tinha respondido?" (14/10/2026, R).

---

## 2. Como ele decide

- **Só ele aprova.** Só o Samuel marca `[x]` aprovado, `[~]` melhorar, `[-]` descartado no plano; o
  Claude Code escreve no máximo "PRONTO PARA CONFERIR" ([CLAUDE.md](../../CLAUDE.md) §4.3; plano, regra 4).
- **Confere em fotos.** Nas páginas de conferência, cada quadro tem "Está bom / Melhorar / Está pior" e
  um comentário, e o trabalho inteiro tem uma decisão final ("Aprovado"); nos formulários de setembro e
  outubro era "Bom / Ruim / Não sei" (H, PARTE -9 §1 e PARTE -14 §3). Desde 13/10/2026, nos itens da
  Fase 2 ele só confere no fim, em fotos (plano, abertura da Fase 2).
- **Escolha dele = padrão de fábrica; as outras ficam como opção.** "esse programa deve presar por dar
  opções, pois nunca teremos sempre os mesmos casos, então temos que ter opções de contornar novos
  problemas." (05/10/2026, R, conferência 12). Ele pergunta muito "ainda posso ter as duas opções?"
  (ex.: `g6-retangulo`, 09/10: "Posso ter as duas opções mas a opção do scantailor ficar como padrão?").
- **Quer ver lado a lado antes de decidir.** "Quero ver o lado a lado antes de decidir: A, B e C [...]"
  (05/10/2026, R); limpar pontinhos "gostaria de ver lado a lado" (05/10, conferência 10).
- **Avisa quando respondeu.** Ele responde nas páginas e avisa no chat ("respondi"); a gerente lê o banco
  e copia palavra por palavra para `relatorios/` e para o Registro ([CLAUDE.md](../../CLAUDE.md) §10.10).
  Ele pediu: "quando tiver mais perguntas me chama aqui" (09-12/10, H, PARTE -14 §6).
- **Aprova o plano inteiro antes de codar** e confere cada item pelo atalho "(desenvolvimento)" em até
  10 minutos ([CLAUDE.md](../../CLAUDE.md) §2 e §8; plano, regra 4).
- **Às vezes adianta ou muda a ordem**, sempre registrado: adiantou a Fase 2 em 01/10/2026 ("c");
  mandou seguir sem esperar a aprovação item a item em 28/09/2026 (R).
- **Decisão da gerente fica "a rever pelo Samuel"** no Registro, quando ele ainda não decidiu (R, 28/09/2026).

---

## 3. Frases dele que viraram regra

| Frase literal | Data | Fonte | Virou |
|---|---|---|---|
| "eu quero que o papel saia branco, e o desenho também saia perfeito." | 01/08/2026 | H, PARTE 2, pedido 22 | o critério final ([CLAUDE.md](../../CLAUDE.md) §1; plano §2) |
| "esse programa deve presar por dar opções, pois nunca teremos sempre os mesmos casos, então temos que ter opções de contornar novos problemas." | 05/10/2026 | R, conferência 12 | escolha dele = padrão de fábrica, alternativas ficam |
| "não me responda no chat quando tiver questionamentos nas conferencias, responda nas conferencias." | 07/10/2026 | R, 07/10; [CLAUDE.md](../../CLAUDE.md) §10.10 | resposta na página |
| "o meu comentario serve como resposta, porque você não responde ele e me mostra a questão de novo?" | 07/10/2026 | [CLAUDE.md](../../CLAUDE.md) §10.10 | o comentário vale como resposta; a pergunta volta refeita |
| "eu acho que ele devia subir e virar um comentario fixado junto quando voltasse, para que dai eu colocasse outro e tivesse referencia do que foi colocado antes" | 07/10/2026 | [CLAUDE.md](../../CLAUDE.md) §10.10 | comentário fixado (campo `historico`) |
| "sempre que tiver paginas de conferencia prontas, pode abrir automaticamente no meu pc, caso eu já tenha feito a ultima pagina de conferencia e te dado ok." | 06/10/2026 | R, 06/10; [CLAUDE.md](../../CLAUDE.md) §10.10 | a gerente abre com `start` sem perguntar |
| "mas eu preciso responder o que? não dá para simplismente implementar no programa?" (e "ok" à regra proposta) | 13/10/2026 | R, 13/10; plano, abertura da Fase 2 | Fase 2 igual ao ScanTailor, sem perguntar antes |
| "o programa quando estiver pronto, ele vai ter que ser capaz de abrir arquivos de versões anteriores." | 05/10/2026 | R, conferência 14 | compatibilidade com projetos antigos |
| "ok, por favor tome muito cuidado, porque não quero apagar as varias rodadas que eu fiquei respondendo relatorios, quero que isso continue salvo e que o plano não mude, só seja acrescentado coisas." | 09/10/2026 | R, 09/10 | o plano só recebe acréscimos; cópia anterior guardada |
| "Se eu quiser preto eu escolho o preto e branco, simples." | 05/10/2026 | R, conferência 10 (EX2) | nada vira preto escondido fora do Preto e branco |
| "Anote, por favor, que depois precisamos rever essas coisas que deixam mais lentas [...] mas o principal agora e ter um bom resultado nos pdf's." | 05/10/2026 | R, Lista de espera (conferência 9, V) | lentidão pequena aceita e anotada para a Fase 5 |
| "Quero todos os agentes trabalhando em alguma coisa" e "estamos atrasados no planejamento" | 12/10/2026 | R, 12/10 | agentes em paralelo (dentro do limite de memória) |
| "vamos deixar esse concerto de lentidão para o final, para a fase de desempenho." | 19/10/2026 | R, 19/10; [CLAUDE.md](../../CLAUDE.md) §4.6 | lentidão do meio da fase vai para a Fase 5 |
| "acho que você pode ir colocando os botões e as funcionalidades e depois eu resolvo com o agente de layout, mas é bom que seja listado tudo para o agente de layout para ele ter ideia desses botões e funcionalidades." | 06/10/2026 | R, conferência 15 | botões já, com aparência provisória; lista para o layout |
| "a questão das funcionalidades eu acho que é contigo, mas a questão visual é com o agente de layout, deve ser feito as funcionalidades e depois passado relatorio para ele né" | 08/10/2026 | plano, Fase 2 ("Para revisar", rodada 4) | função pela gerente/implementador, aparência pelo layout |
| "Página sempre abre em 'Original', sem mexer. [...] Assim eu decido se tiro ou não, e o Kaique escolhe um filtro só, sem mudança escondida." | 29/09/2026 | plano, item 1.1 | nada automático escondido; página nova em Original |
| "A opção D fica de fora, porque o papel tem que sair branco." | 05/10/2026 | R, 05/10 | papel sempre branco |
| "Devemos sempre buscar que o programa use todo o potencial do computador para que o programa funcione de maneira rapida." | 05/10/2026 | R, Lista de espera (conferência 7, V1) | item 2.16 / Fase 5 |
| "quero começar a trabalhar com subagentes agora, para que aqui fique uma conversa livre, enquanto subagentes implementam coisas no código e outros verificam, e eu fico só vendo coisas novas a serem mudadas ou testadas aqui nesse chat — ele vira nosso chat de gerenciamento e não de codar." | 22/09/2026 | H, PARTE -6 §2 | conversa gerente + agentes ([CLAUDE.md](../../CLAUDE.md) §10.1) |
| "crie essa regra no projeto" | 06/10/2026 | R, 06/10 | regra das páginas que abrem sozinhas |
| "não vou comitar, quero voltar a versão que estava antes." | 16/09/2026 | H, PARTE -4 §2 | frente do ScanTailor revertida; plano antes de codar |
| "não quero problemas nela, hoje o aplicativo é travado demais" | 12-13/09/2026 | H, PARTE -3 | testar função e interface juntas |

Pergunta dele ainda útil como critério (19/10/2026, R): "mas nós precisamos medir a velocidade no meu pc
sempre? porque o programa deveria conseguir se desenvolver bem em qualquer computador né?" (resposta
dada: o notebook do Kaique é a régua final; o PC é a régua por ser sempre a mesma máquina).

---

## 4. As regras permanentes da PARTE 2 do histórico

O histórico lista seis pedidos que "não são tarefa: são o modo de trabalhar" (H, PARTE 2, "Os pedidos que
valem como regra permanente"). As palavras **literais** dos pedidos são estas (a PARTE 2 as resume um
pouco diferente; vale a literal):

| Regra | Palavras literais | Data, pedido |
|---|---|---|
| Ser direto | "não entendi, o jeito que você escreve fica dificil para eu entender as informações, seja mais direto por favor" | 01/08/2026, pedido 23 |
| Ser conciso, em quatro linhas | "muita coisa para eu ler, seja mais consigo por favor, fale em quatro linhas o que eu preciso escolher" | 05/08/2026, pedido 51 |
| Ser simples (não é o mesmo que ser curto) | "não entendi do que você está falando, seja mais simples" | 06/08/2026, pedido 60 |
| Conferir sozinho, abrindo todas as imagens | "por favor, confira os teste que você fez sozinho, não vou ter como fazer isso." | 03/08/2026, pedido 36 |
| Ir até o fim dentro da alçada | "porque você continua travando , porque não vai até o final?" | 04/08/2026, pedido 46 |
| A ordem de trabalho daquela época | "vai concertar os filtros e depois a gente volta para parte de seleção." | 02/08/2026, pedido 35 |
| O critério final | "eu quero que o papel saia branco, e o desenho também saia perfeito." | 01/08/2026, pedido 22 |

(São sete linhas porque "direto" e "conciso" aparecem juntas no histórico. A ordem "filtros antes da
seleção" é de agosto e foi substituída pelas fases do plano de 24/09/2026.)

---

## 5. O que está na memória do Claude Code no PC do Samuel

Notas que o Claude Code guarda para todos os projetos do Samuel (memória do Claude Code no PC do
Samuel). Valem aqui também:

- **Seja breve.** Resposta curta; tabela longa no chat não é lida; o detalhe vai para arquivo; numa
  escolha, só as opções e a recomendação (de 01/08 e 05/08/2026, neste projeto).
- **Ir até o fim.** Escolher sozinho o que está dentro da alçada e executar o protocolo inteiro; parar a
  cada passo "é lido como travar". Perguntar só o que o projeto exige: criar ou remover filtro, mudar
  tela ou controle, formato de dados, desfazer/refazer, trocar biblioteca (de 04/08/2026, neste projeto).
- **Planejar devagar, um por um.** Em sessão de planejamento, uma decisão explicada e confirmada por
  vez; só codar depois de aprovado o plano inteiro (de 17/09/2026, neste projeto).
- **Não mudar o combinado por pergunta.** "Não era X, né?" é pergunta de fato: conferir o registro e
  citar onde está escrito antes de concordar ou mexer em arquivo (de 19/09/2026, outro projeto).
- **Explicar termos em português simples.** Decisão com jargão de git ou programação: dizer o que
  significa e o que muda, com recomendação (de 20-21/09/2026, outros projetos).
- **Explicar no chat, sem caixinha.** Ao pedir decisão no chat, explicar cada opção por extenso, com caso
  real, e deixar ele responder digitando; não abrir a caixinha de pergunta logo depois (de 19/10/2026,
  neste projeto).

A gerente tem também notas próprias (memória da gerente no PC do Samuel, projeto `d--programas`):
responder sempre em português; sempre dar opções; escolhas visuais nas páginas; botões já, layout
depois; página de andamento; abrir conferências sem perguntar; limite de agentes; tudo no GitHub;
nunca mover pastas com junção; responder nas conferências.

---

## 6. O CLAUDE.md §2, "Como trabalhar comigo"

Resumo do [CLAUDE.md](../../CLAUDE.md) §2 (o texto lá é o que vale):

- Não recomeçar do zero; não reescrever módulos inteiros; testar não é permissão para reconstruir.
- Uma mudança por vez, um item do plano por vez, na fase atual; ele aprova pela página de antes/depois,
  não pelo diff.
- Planejar antes de codar; perguntar antes de mexer em estrutura.
- Ir até o fim dentro da alçada; se o contexto acabar, parar num commit com o programa rodando.
- Português comum, sem jargão; a frase antes do número.
- Conciso: o essencial no chat, o detalhe em arquivo.
- Honesto: avisar quando ele estiver enganado ou correndo risco; não concordar só para agradar.
- Não inventar detalhe que ele não forneceu.
- Todo relatório em três formatos (`.md`, `.html`, `.pdf`), porque ele não abre `.md`.
