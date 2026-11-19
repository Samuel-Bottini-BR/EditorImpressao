# Catálogo dos erros achados (desde 19/11/2026)

Decisões do Samuel: D-803 e D-804 (19/11/2026). À pergunta "quando acontece esses erros, eles são catalogados para
virarem regras depois?", ele aceitou a proposta ("ok"). Ao jeito de organizar, explicado no chat (um caderno só,
quatro coisas de cada erro, os erros da mesma causa juntos num tipo, o que se repete vira pergunta), ele disse "ok".
A proposta inteira, com os porquês: `relatorios/catalogo-erros-2026-11-19/proposta.md`.

## Como funciona

- **Só a gerente escreve aqui,** no fim de cada passo, antes de juntar. Os agentes deixam os erros nos relatórios
  deles (ONDE-PAREI, relatório de quem tenta quebrar); a gerente passa para cá.
- **O catálogo não copia, aponta.** Uma entrada por erro, de poucas linhas, com o caminho do relatório que tem a
  prova. O que só ele guarda: a família (a causa), quem achou e o que devia ter pegado antes.
- **Famílias pela causa, nunca pelo lugar.** Cada erro numa família só.
- **"Se repete"** = a mesma família em dois passos, ou três vezes no mesmo passo em voltas diferentes de quem quebra.
- **O que vira** depende do "o que devia ter pegado": não havia regra → regra nova dos agentes; havia regra e não
  bastou → conferência do porteiro (se a máquina vê no código) ou pergunta nova do formulário (se só o agente sabe);
  havia conferência com furo → conserto dela; defeito do programa → Lista de bugs.
- **Chega ao Samuel** pela Central, uma pergunta por vez, no formato do CLAUDE.md §11.13. Nada entra sem o "sim" dele.
- **Uso imediato:** as famílias em observação vão como foco no pacote de quem tenta quebrar o próximo passo. A mesma
  família em duas voltas seguidas do mesmo passo faz a gerente pedir o conserto pela causa (§11.12) antes da volta
  seguinte.

## Os campos de cada erro

Cada erro é um título `###` com um código e o nome do erro em palavras simples, e estes campos, sempre nesta ordem:

| Campo | O que vai | Valores |
|---|---|---|
| **Código** | passo, de onde veio e o número que a fonte já usa | `P1-v1-05` (passo 1, volta 1 de quem quebrou, achado 5); `P1-v2-N1`; `P1-gh-1` (GitHub); `P0-ger-1` (achado pela gerente); `P1-port-1` (porteiro); `P1-form-1` (formulário); `P2-sam-1` (achado pelo Samuel) |
| **O que foi** | uma ou duas frases simples: o que dava errado e para quem | — |
| **Causa** | por que aconteceu, numa frase, sem o nome do arquivo | — |
| **Família** | o código da família (seção 3), ou "sem família" | `F1` a `F10`, ou "sem família" |
| **Quem achou** | quem viu primeiro | teste no PC · GitHub · porteiro · formulário · quem tenta quebrar (volta N) · prova à vista · a gerente · o Samuel · o próprio agente |
| **Quando** | data e passo; para quem quebra, a volta | — |
| **Gravidade** | a que a fonte deu | grave · médio · baixo |
| **Onde** | arquivo e função (nunca só a linha: muda) | — |
| **O que devia ter pegado antes** | a regra ou a conferência que já existia e devia ter pegado, e por que não pegou; ou "nenhuma" | "nenhuma" · "regra X existia e não foi seguida" · "conferência KNN existia e tinha furo" |
| **Destino** | o que aconteceu com ele | consertado no commit X, com o teste Y · não é defeito (porquê) · Lista de bugs · Lista de espera · pergunta ao Samuel · combinado do plano |
| **Fonte** | o relatório e o número do achado, com o ramo | — |

E cada família é um título `##` com:

| Campo | O que vai |
|---|---|
| **A causa, numa frase** | o que todos os erros dela têm em comum |
| **Erros** | os códigos, quantos, em que passos e voltas |
| **Já visto antes do catálogo** | casos parecidos nas revisões de 10/11 e 18/11 ou no `licoes.md`, só como apontador |
| **Regra ou conferência que já existia** | qual, ou "nenhuma" |
| **Situação** | em observação · se repete, proposta preparada · levada à Central em DATA · o Samuel disse sim (D-NNN) · o Samuel disse não em DATA · não vira nada (porquê) |
| **Virou** | a regra (R-NNN) ou a conferência (K-NN) ou a pergunta do formulário, quando existir |

**O que não entra no catálogo:** o que a própria fonte diz que não é defeito (observação) e o que é o combinado do
plano sem furo; o que já está na Lista de bugs ou no plano e só foi visto de novo (fica uma linha na seção "não
entram", com o motivo). Tentativa de imagem continua só no `melhorias.md`.

**Um exemplo de entrada:**

```
### P1-v1-05 · A tarefa que não confere fica no Windows
- O que foi: quando a tarefa lida de volta não batia com a pedida, a peça dizia "não ficou criada como pedido" e a
  tarefa ficava lá, com outro conteúdo.
- Causa: só o caminho em que a leitura confere foi pensado; o "não confere" não desfazia nada.
- Família: F5
- Quem achou: quem tenta quebrar (volta 1)
- Quando: 19/11/2026, passo 1
- Gravidade: médio
- Onde: core/windows.py, criar_tarefa
- O que devia ter pegado antes: CLAUDE.md §11.12, pontos 2 e 3 (existia desde 18/11; não foi seguida)
- Destino: consertado em dcc4981c e 7e726221 (test_a_tarefa_criada_que_nao_confere_e_apagada)
- Fonte: relatorios/passo1-peca-unica-windows/quem-quebrou/relatorio-1.md, achado 5 (ramo passo1-peca-unica-windows)
```

---


## Os erros: os passos 0 e 1, já agrupados

Fontes lidas: passo 0 (o porteiro), as seis voltas de quem quebrou (`relatorio.md`, `relatorio-2.md` a
`relatorio-6.md`) e o ONDE-PAREI, ramo `passo0-porteiro-2026-11-19`; passo 1 (a peça única do Windows), as duas voltas
(`relatorio-1.md` e `relatorio-2.md`), o ONDE-PAREI e o `git log`, ramo `passo1-peca-unica-windows`. As revisões de
10/11 e 18/11 e o `licoes.md` aparecem só como "já visto antes".

**Passo 1 ainda não acabou:** falta a prova à vista. O que o Samuel achar nela entra depois.

### Quantos e quem achou

- **Passo 0: 47 erros.** Quem tenta quebrar achou 45 (seis voltas: 19, 9, 7, 6, 3 e 1); a gerente, 1 (o repositório
  raso); o porteiro, 1 (os arquivos com marca de UTF-8).
- **Passo 1: 29 erros.** Quem tenta quebrar achou 22 (duas voltas: 16 e 6); o GitHub, 4; o porteiro, 1; o formulário,
  1; o próprio agente, lendo a documentação, 1.
- **O Samuel: 0** (a prova à vista do passo 1 ainda não aconteceu; o passo 0 não tem prova à vista).
- **Leitura:** quem tenta quebrar acha quase tudo. O GitHub pegou quatro que o PC não pegava. O porteiro e o
  formulário já estão pegando coisa no passo seguinte ao que os construiu.

Na lista abaixo, "v1" é a primeira volta de quem quebrou, "N", "R", "Q", "S" e "T" são os nomes das voltas 2 a 6 do
passo 0, e "v2-N" a segunda volta do passo 1.

### As famílias

#### F1 · A conferência acredita num dado que não prova nada

**A causa:** o dado que decide vem do próprio conferido (o ramo do agente, o que ele escreve no ONDE-PAREI, um texto
que ele pode copiar) ou já estava lá antes (o arquivo da vez anterior, a pasta criada por outra conta).

| Código | O que foi | Quem achou | Destino |
|---|---|---|---|
| P0-v1-03 | o papel do agente era o que ele mesmo escrevia no ONDE-PAREI | quebra v1 | consertado: vale o papel do pacote |
| P0-v1-06 | o porteiro e a lista não tinham proteção contra o próprio agente | quebra v1 | consertado (reaberto em N1 e R2) |
| P0-v1-07 | "a lista só diminui" não era conferido no GitHub nem antes do commit | quebra v1 | consertado |
| P0-v1-19 | a K18 conferia o GitHub pela cópia local | quebra v1 | consertado: pergunta ao GitHub |
| P0-N1 (grave) | o "sim" do Samuel era forjável com um texto curto | quebra v2 | consertado (reaberto em R1) |
| P0-N3 | o ramo podia afrouxar a busca do porteiro; 8 grupos de palavras sem exemplo nos testes (vizinha: F3) | quebra v2 | consertado |
| P0-N9 | o pacote que confere o formulário do passo foi feito por quem construiu | quebra v2 | consertado |
| P0-R1 (grave) | o "sim" continuava forjável: bastava copiar 12 letras de uma decisão que existe | quebra v3 | consertado pela estrutura: nada entra na lista por ramo de agente |
| P0-R2 (grave) | a versão com que se compara era escolhida pelo código do próprio ramo; "não achei" virava "passou" | quebra v3 | consertado pela estrutura: o juiz vem da versão de teste |
| P0-R3 | o porteiro podia ser afrouxado pelo uso sem nenhum teste acusar | quebra v3 | consertado (o juiz) |
| P0-Q1 | a K21 aceitava a marca "PORTEIRO" de qualquer trabalho da rodada, inclusive um que roda o código do agente | quebra v4 | consertado: só o trabalho do juiz |
| P0-Q6 | com a lista "proposta", o ramo podia encolhê-la sem consertar nada | quebra v4 | consertado |
| P1-v1-02 | um arquivo da vez anterior fazia a janela de prova dizer "a tarefa rodou" | quebra v1 | consertado em duas camadas |
| P1-v1-14 | um relatório com menos passos que o pedido virava "deu certo" | quebra v1 | consertado |
| P1-v2-N3 | qualquer conta do computador pode criar antes a pasta do programa no Agendador | quebra v2 | consertado: a peça confere dono e licença da pasta |

- **15 erros, passos 0 e 1.** Se repete.
- **Já visto antes:** revisões de 18/11 ("o programa mostra o que ele mesmo anotou": desligar grava "Desligado",
  "preparado" sem nada preparado).
- **Regra que já existia:** CLAUDE.md §11.12, ponto 2, fala do programa ("o que a tela mostra vem dessa conferência,
  nunca só da anotação"), não de conferência, de juiz nem de teste. Nenhuma conferência do porteiro. → **não havia
  regra para este caso.**

#### F2 · A conferência olha o jeito mais comum, e o vizinho passa

**A causa:** a conferência compara o texto (uma palavra, uma pasta, uma extensão, um jeito de escrever o caminho, o
título do pedido) em vez da coisa de verdade, e não lista antes todos os jeitos que o Python ou o Windows aceitam.

| Código | O que foi | Quem achou | Destino |
|---|---|---|---|
| P0-v1-02 (grave) | a busca do Windows conhecia 13 palavras; o mesmo pedido com outra palavra passava (73 linhas) | quebra v1 | consertado: 48 linhas, cada uma com exemplo |
| P0-v1-04 | a K13 só barrava o agente de tela em `core/` | quebra v1 | consertado |
| P0-v1-09 | a K04 e a K05 não olhavam `core/`, onde moram avisos que o Kaique lê | quebra v1 | consertado |
| P0-v1-10 | a correção da folha de estilo cegava a busca em qualquer texto com `/* */` | quebra v1 | consertado |
| P0-v1-14 | a K11 não olhava os testes soltos da raiz | quebra v1 | consertado |
| P0-v1-15 | o rótulo de pronto numa linha numerada passava | quebra v1 | consertado |
| P0-v1-17 | o instalador antigo (Inno) conversa com o Windows fora do Python; o porteiro só lê `.py` | quebra v1 | pergunta à gerente |
| P0-N2 | chamada por apelido da biblioteca do Windows passava | quebra v2 | consertado: segue o apelido no arquivo |
| P0-N4 | o rótulo de pronto valia numa pasta de quem quebrou de outro trabalho | quebra v2 | consertado |
| P0-N7 | a mesma cegueira da folha de estilo num f-string com `{}` | quebra v2 | consertado |
| P0-N8 | arquivo novo só ganhava as regras do Windows se o título do pedido dissesse "Windows" | quebra v2 | consertado: vale a tabela |
| P0-Q2 | o porteiro não via programa fora de `core/`, `ui/` e da raiz | quebra v4 | consertado: lista curta do que não é programa |
| P0-Q4 | um `.pyc` sem fonte, que o Python importa, passava | quebra v4 | consertado |
| P0-S1 | uma pasta `historico/` com `__init__.py` tomava o lugar do `historico.py` e não era lida | quebra v5 | consertado |
| P0-S2 | `.pyw` não era lido | quebra v5 | consertado |
| P0-S3 | `.pyd` passava | quebra v5 | consertado |
| P0-T1 | `import docs.segredo` ou um `.zip` no caminho de busca passam | quebra v6 | Lista de espera (não é grave hoje) |
| P1-v1-12 | a peça entregava a biblioteca crua do Windows e o "rodar qualquer ferramenta" a qualquer arquivo; o porteiro não via | quebra v1 | consertado: a peça é fechada |
| P1-v2-N2 | a peça fechada tinha três portas: o caminho escrito de outro jeito (`\\?\`, `\\localhost\C$`), o nome com "_" usado por apelido, programas de fora do Windows | quebra v2 | consertado (o apelido fica com a gerente, no porteiro) |

- **19 erros, passos 0 e 1.** Se repete. No passo 0, a mesma família voltou nas seis voltas: o agente acrescentava a
  palavra ou a extensão que faltou, e o vizinho seguinte passava (o próprio quebrador, na volta 5: "Os três são o mesmo
  tipo de furo do Q2").
- **Regra que já existia:** CLAUDE.md §11.12, ponto 6 ("ler antes de usar peça de fora"): pede o que a peça faz em
  cada caso (deu certo, falhou, "Não"), não **tudo o que ela aceita como entrada**. → **a regra existia e não cobria
  este caso.**

#### F3 · Proteção ou caminho que nenhum teste percorre

**A causa:** a proteção foi escrita e o teste não a cobra (desligada numa cópia, todos os testes passam), ou o ensaio
só percorreu os caminhos fáceis.

| Código | O que foi | Quem achou | Destino |
|---|---|---|---|
| P1-v1-01 (grave) | a janela de prova não fazia as perguntas 2 e 3: o nome da tarefa tinha parênteses e a própria peça recusava; o ensaio só rodou as provas 1, 5 e 6 | quebra v1 | consertado: um teste passa todo pedido de toda prova pelas regras da peça |
| P1-v1-03 | nenhum teste provava que o "Não" vira "você disse Não" e que uma falha não vira "Não" (mutações M8 e M9 passavam) | quebra v1 | consertado |
| P1-v1-04 | nenhum teste provava a recusa da pasta de troca onde outra conta grava (M7) | quebra v1 | consertado |
| P1-v1-13 | três proteções sem teste (M10, M11, M12) | quebra v1 | consertado |
| P1-v2-N1 | o conserto do achado 12 apagou a prova do "Não" lido do jeito certo (o defeito 2 da etapa 5) | quebra v2 | consertado: a peça diz quais bibliotecas guardam o erro |
| P1-v2-mut | cinco proteções da volta 1 sem teste (A1c, A2, A6, A6b, A9) | quebra v2 | consertado |

- **6 erros, passo 1, duas voltas.** Se repete (três ou mais no mesmo passo, em voltas diferentes).
- **Já visto antes:** revisão de 18/11 ("os testes trocavam as peças do Windows por peças de mentira e passavam").
- **Regra que já existia:** CLAUDE.md §4.7 (teste de reversão, só para bug consertado) e §11.12, ponto 4 (peça de
  mentira não prova). Nenhuma pede, para código novo, a prova de que cada proteção tem um teste que a acusa. No passo
  1, o agente fez essa prova (o anexo "reversão", 26 de 27 acusadas) **depois** de quem quebrou pedir. → **não havia
  regra.**

#### F4 · O teste supõe o computador, a língua ou o estado de hoje

**A causa:** o teste foi escrito olhando o PC do Samuel (Windows em português, sem a licença ligada, pasta temporária
no C:) ou o estado do dia (a lista ainda "proposta"), e quebra noutro lugar.

| Código | O que foi | Quem achou | Destino |
|---|---|---|---|
| P0-v1-01 (grave) | ligar a lista deixava um teste vermelho: ele só valia com a lista "proposta" | quebra v1 | consertado: o teste usa dados próprios |
| P1-gh-1 | no GitHub a pasta temporária fica no D:, sem as licenças da conta; a peça (com razão) recusava, e dois testes falharam | GitHub (rodada 44549715965) | consertado no teste (`20054121`) |
| P1-gh-2 | o teste exigia a conta como dona da pasta nova; o Windows do GitHub roda com a licença ligada e dá o dono aos Administradores | GitHub (44553075293) | consertado no teste (`b271cefc`, `1b1b0fa6`) |
| P1-gh-3 | o Windows do GitHub em inglês escreveu "Everyone"; o teste procurava "Todos"; e a frase da peça mostrava o número da conta | GitHub (44582797901) | consertado: a peça diz as contas em português pelo número delas (`bd46892a`, `6bf3459a`) |
| P1-gh-4 | o teste do "Só as letras" que desfaz o Automático falhou por tempo em duas rodadas e passou na repetição (não é deste passo) | GitHub (44558364601, 44571676129) | Lista de bugs (instabilidade) |

- **5 erros, passos 0 e 1.** Se repete. Cada falha do GitHub custou uma rodada.
- **Já visto antes:** `licoes.md`, 24/10 ("suíte que passa no GitHub pode falhar no PC pela ordem dos testes"); C3
  ("teste simulado passa e o uso real falha").
- **Regra que já existia:** nenhuma diz como o Windows do GitHub é diferente do PC. → **não havia regra.**

#### F5 · Dá como feito o que não conferiu, ou deixa pela metade

**A causa:** depois de pedir algo ao Windows, a peça não lê de volta o que aconteceu, ou para no meio sem desfazer, ou
a frase diz mais do que se sabe.

| Código | O que foi | Quem achou | Destino |
|---|---|---|---|
| P1-v1-05 | a tarefa que não conferia ficava no Windows; a licença era comparada pelo texto | quebra v1 | consertado |
| P1-v1-06 | a pergunta 3 deixava a pasta do programa no Agendador, e "o que foi desfeito" não dizia | quebra v1 | consertado |
| P1-v1-07 | "a pasta foi apagada de novo" sem conferir que sumiu | quebra v1 | consertado |
| P1-v1-08 | ninguém conferia quem pode ler a pasta de troca (o segredo cifrado abre em qualquer conta do computador) | quebra v1 | consertado |
| P1-v1-09 | depois do "não terminou no tempo", o trabalho com licença continua e a frase dá a entender que nada aconteceu | quebra v1 | consertado |
| P1-v1-10 | o script dava "deu certo" com um comando de dentro falhando | quebra v1 | consertado |
| P1-v1-11 | a resposta juntava o que o programa escreve como saída e como erro | quebra v1 | consertado |
| P1-v1-17 | fechar a janela de prova no meio de uma pergunta derrubava o processo | quebra v1 | consertado |
| P1-v2-frase | a janela dizia "foi apagada" de uma pasta que nunca foi criada | quebra v2 | consertado |

- **9 erros, passo 1, duas voltas.** Se repete.
- **Já visto antes:** as revisões de 18/11 inteiras (desligar com "Não" grava "desligado"; ligar que falha no meio não
  desfaz; a volta que diz "voltou" antes de saber). Foi por elas que a regra nasceu.
- **Regra que já existia:** CLAUDE.md §11.12, pontos 2 e 3, escritos em 18/11 **por causa deste tipo de erro**, e lidos
  pelo agente do passo 1. → **a regra existia e não bastou.**

#### F6 · O que se diz ao Samuel foge do combinado

**A causa:** o texto para ele não segue a lista do CLAUDE.md §11.13, ou diz que ele decidiu o que não decidiu, ou
pergunta de novo o que ele já respondeu.

| Código | O que foi | Quem achou | Destino |
|---|---|---|---|
| P0-v1-08 | o texto da lista de exceções não seguia o §11.13 | quebra v1 | consertado |
| P0-N6 | o texto ainda sem print que prova, e perguntando de novo parte do que ele decidiu em 19/11 | quebra v2 | consertado |
| P0-R4 | o texto dizia "como você escolheu" sobre os 54 lugares do teste de velocidade, e a escolha dele tratava de uma parte deles (uns 10) | quebra v3 | consertado: os outros viraram pergunta |
| P0-Q7 | a pergunta dos 56 lugares não tinha print | quebra v4 | aceito pela gerente (código sem tela) |

- **4 erros, passo 0, quatro voltas.** Se repete.
- **Já visto antes:** `licoes.md` B1 e B2 (perguntas que voltaram com "Ainda não entendi"; perguntas dadas como "nunca
  feitas" e já respondidas).
- **Regra que já existia:** CLAUDE.md §11.13 inteiro; o formulário (F17) confere parte dele. → **a regra existia e não
  bastou.**

#### F7 · O escrito não bate com o código

**A causa:** o docstring, o ONDE-PAREI ou o formulário dizem uma coisa que o código não faz (ou citam um arquivo que
ainda não existe).

| Código | O que foi | Quem achou | Destino |
|---|---|---|---|
| P0-v1-12 | o docstring da tabela prometia ler o pedido para arquivo novo, e não lia | quebra v1 | consertado |
| P0-v1-16 | o docstring do porteiro, o texto do gancho e a contagem de arquivos não batiam com o código | quebra v1 | consertado |
| P0-R7 | dois itens do ONDE-PAREI não batiam com o código | quebra v3 | consertado |
| P1-form-1 | o formulário citava como prova um arquivo que só nasce na sessão à vista; faltavam o pacote e a fonte nos anexos | formulário e a gerente | consertado (`a8921a49`, `d1f6be95`) |

- **4 erros, passos 0 e 1.** Se repete.
- **Regra que já existia:** CLAUDE.md §10.8 e §11.12 ("comentário que diz ... é conferido na hora"); o formulário já
  confere que a função e o teste citados existem, e pegou o do passo 1. → **a conferência que existe já pega a maior
  parte.**

#### F8 · Falso alarme da conferência

**A causa:** a conferência acusa o que está certo (e, se ninguém vê, isso faz a lista de exceções crescer à toa).

| Código | O que foi | Quem achou | Destino |
|---|---|---|---|
| P0-N5 | `creationflags=0`, "self-service" e "hku:" contavam como conversa com o Windows | quebra v2 | consertado, com o exemplo certo como teste |
| P0-R5 | o seguir do apelido acusava linhas que não conversam com o Windows | quebra v3 | consertado, com teste |
| P0-R6 | abrir sem a janela preta contava como conversa com o Windows | quebra v3 | consertado, com teste |
| P1-port-1 | o porteiro barrou o nome de uma ferramenta de licença escrito numa lista que servia para recusá-la; o agente trocou a lista pela regra "tudo da pasta do Windows" | porteiro | resolvido por um desenho melhor (`a21b311a`) |

- **4 erros, passos 0 e 1.** Se repete.
- **Regra que já existia:** a prova da D-791 ("cada conferência ... não acusa o código certo"); cada falso alarme já
  virou teste com o exemplo certo. → **o jeito que existe já resolve cada caso.**

#### F9 · Comando que muda o que é do Samuel sem ele ver

**A causa:** um comando rodado como se fosse numa cópia isolada mexe no repositório ou no Windows do PC dele, por
baixo.

| Código | O que foi | Quem achou | Destino |
|---|---|---|---|
| P0-ger-1 (grave) | o repositório do PC ficou raso: o script do juiz, com `git fetch --depth=1`, rodou na cópia do agente, que divide a pasta `.git` com o repositório dele; o `git merge` recusou | a gerente (no merge) | consertado: `--depth=1` só se a cópia já é rasa, com teste de reversão; restaurado com `git fetch --unshallow` |
| P1-v2-N4 | um teste novo cria uma tarefa de verdade no Windows do PC se o terminal tiver a licença ligada | quebra v2 | consertado: esse teste só roda no GitHub |

- **2 erros, passos 0 e 1.** Se repete.
- **Já visto antes:** `licoes.md` D1 (agente apagou `D:\d`), D2 (`robocopy` esvaziou pastas por uma junção), D4
  (`git stash` levou arquivos de outro agente), C4 (testes gravando no `erros.log` real), C9 (teste quase apagou um
  projeto).
- **Regra que já existia:** CLAUDE.md §10.9 (apagar) e D-785 (nada escondido no Windows). Nenhuma diz que a cópia do
  agente divide o `.git` com o PC. → **não havia regra para o git.**

#### F10 · Duas regras que se atrapalham

| Código | O que foi | Quem achou | Destino |
|---|---|---|---|
| P0-v1-05 | o rótulo que quem quebra escreve no ramo de quem construiu fazia o formulário de quem construiu voltar | quebra v1 | consertado |
| P0-v1-18 | a regra da barra de rolagem no CLAUDE.md §9 (`#a8a49e`) contradiz os valores que a K22 cobra | quebra v1 | pergunta à gerente |

- **2 erros, passo 0, uma volta.** Em observação. As contradições já têm a lista própria na proposta das regras (X1 a
  X11); a gerente as leva lá.

#### Sem família

| Código | O que foi | Quem achou | Destino |
|---|---|---|---|
| P0-v1-11 | o lugar da lista de exceções é o texto da linha: mexer na linha sem consertar vira erro novo | quebra v1 | combinado do plano; o pacote mostra os lugares |
| P0-v1-13 | listas escritas à mão em mais de um lugar | quebra v1 | consertado (mesma causa dos remendos de 10/11: se voltar, vira família) |
| P0-Q3 | a função na chave trava os passos 3 e 4 se renomearem funções que guardam lugares do passo 5 | quebra v4 | aviso no pacote dos passos 3 e 4 |
| P0-port-1 | três arquivos começam com a marca de UTF-8 (BOM) | porteiro | Lista de bugs |
| P1-v1-15 | a mesma conta, sem licença, pode trocar o script antes de o programa com licença usar | quebra v1 | não é defeito deste passo; cuidado no pacote do passo 3 |
| P1-leit-1 | pela leitura da documentação, a pergunta do Windows vai mostrar "EditorImpressao.exe", não "Editor de Impressão" | o próprio agente | pergunta ao Samuel, pronta |

#### Não entram

- P0-Q5 (o formulário fica pendente até a lista ser ligada): é o combinado.
- P1-v1-16 (o texto do argumento escrito à mão no `main.py`): a fonte diz "observação, não é defeito".
- O disco D: dá controle total a "Todos" (achado de novo no passo 1): já está na lista do plano (item 59).

### As famílias que se repetem e as propostas (esperam o "sim" do Samuel, uma por vez)

Seis perguntas, uma por vez. A ordem é sugestão minha: primeiro o que o próximo passo (publicar e o servidor das versões
de prova) mais vai encontrar.

**1. F9, comando que muda o que é do Samuel sem ele ver** → **regra nova** (etiqueta git) e **conferência nova do
porteiro**.
- Regra: "A sua cópia divide a pasta `.git` com o repositório do Samuel. Comando que muda o `.git` inteiro (`fetch` com
  `--depth`, `gc`, `prune`, `stash`, `config`, mexer em ramo que não é o seu) não roda na sua cópia, nem em script ou
  teste, a não ser num repositório de prova que o próprio teste cria em pasta temporária. Caso que originou: o
  repositório do PC raso em 19/11."
- Conferência: o porteiro acusa esses comandos em scripts e testes fora das duas peças de git que já existem
  (`conversa_com_o_git.py`, `repositorio_de_prova.py`). É busca de texto, como a K01; pouco falso alarme.
- Por que primeiro: é o único tipo que já estragou uma coisa do Samuel nestes dois passos, e o passo 2 mexe com o
  GitHub.

**2. F4, o teste supõe o computador** → **regra nova** (etiquetas Windows e testes).
- Regra: "O teste do Windows roda em três computadores diferentes. GitHub: Windows em inglês ('Everyone',
  'Administrators'), a licença de administrador já ligada (o dono do que se cria é o grupo Administradores), pasta
  temporária no D:. PC do Samuel: português, sem a licença, o D: dá controle total a 'Todos'. Notebook do Kaique: a
  conferir. O teste compara a conta pelo número dela, nunca pelo nome escrito, e não supõe o estado de hoje da lista ou
  da versão de teste. Casos que originaram: três rodadas perdidas no passo 1."
- Uma conferência do porteiro aqui daria falso alarme (os testes de frase em português precisam escrever "Todos"); fica
  só a regra.

**3. F3 e F5 juntas, proteção sem teste e resultado não conferido** → **pergunta nova no formulário** (com a regra que
a cria).
- Pergunta do formulário, para trabalho de Windows e de instalador: "Cada proteção e cada conferência do resultado
  (recusa, leitura de volta, desfazer) → o teste que falha quando ela é desligada, provado numa cópia." É o anexo de
  reversão que o passo 1 fez depois do pedido de quem quebrou, passado para antes. O programa do formulário confere que
  a lista existe e que cada teste citado existe; quem tenta quebrar confere se a lista está completa.
- Por que juntas: desligar a conferência do resultado e ver um teste falhar pega a F5 também (os achados 5, 7 e 14 do
  passo 1 seriam vistos assim). A regra da F5 já existe e não bastou; escrever mais texto não resolve.

**4. F1, a conferência acredita num dado que não prova nada** → **regra nova** e **pergunta nova no formulário**.
- Regra: "Toda conferência (do porteiro, de um teste ou do programa) diz de onde vem cada dado que ela usa. Dado que o
  próprio conferido escreve ou pode trocar (o ramo do agente, o ONDE-PAREI, a anotação do programa, a pasta de troca,
  o arquivo da vez anterior) não serve de prova. Casos que originaram: o 'sim' forjável e o juiz escolhido pelo ramo, no
  passo 0; o arquivo da vez anterior, no passo 1."
- Pergunta do formulário, para trabalho que confere algo: "De onde vem cada dado que a sua conferência usa?"
- Vale muito para o passo 3: o atualizador confere a assinatura e a marca "preparado".

**5. F2, o vizinho passa** → **ampliar a regra 6 do CLAUDE.md §11.12** (texto de regra: precisa do "sim") e **foco de
quem tenta quebrar**.
- Texto a acrescentar: "Quando o nosso código recusa, filtra ou procura algo, a leitura da peça de fora lista também
  tudo o que ela aceita como entrada, com a fonte (ex.: o Python importa `.py`, `.pyw`, `.pyd`, `.pyc`, pasta com e sem
  `__init__`, `.zip` no caminho; o Windows aceita `\\?\`, `\\localhost\C$`, nome curto), e a recusa compara a coisa de
  verdade, não o texto."
- A conferência que acusaria import de pasta de fora já está na Lista de espera (ideia do passo 0); o catálogo só
  aponta para ela.

**6. F6, o texto ao Samuel foge do combinado** → **pergunta nova no formulário**.
- Pergunta: "Para cada pergunta ao Samuel: as decisões do Livro que você procurou antes, e por que esta ainda não está
  respondida." Pega o "perguntar de novo o que ele já respondeu" e o "como você escolheu" sobre o que ele não escolheu
  (§11.13, ponto 10).

**Não viram pergunta (uma linha na pergunta seguinte, para ele saber):**
- **F7, o escrito não bate com o código:** se repete, mas o formulário já confere o que dá e pegou o do passo 1; o resto
  fica com quem tenta quebrar.
- **F8, falso alarme:** cada caso já vira teste com o exemplo certo; o jeito funciona.
- **F10, duas regras que se atrapalham:** em observação; as contradições têm a lista própria.

---

