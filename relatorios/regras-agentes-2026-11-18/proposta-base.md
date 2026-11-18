# Como passar as regras aos agentes: proposta (18/11/2026)

Proposta de um agente, só lendo e escrevendo. **Nenhuma regra mudou de texto, nenhuma linha do programa nem dos testes
mudou.** Os esboços em `esbocos/` mostram como seria; nada está ligado (nem gancho, nem teste, nem conferência antes
do commit). Ramo `regras-agentes-2026-11-18`, a partir do `fase-1` (`0014e618`). O Livro lido é o do obra (o do
`fase-1` ainda não tem as decisões de 17 e 18/11).

## Em poucas frases

1. **{{N_TOTAL}} regras** no CLAUDE.md e nos 4 arquivos de agente (mais {{N_INFO}} trechos que são informação, não regra).
   **{{N_REP}} aparecem em dois lugares ou mais**, e {{N_DIF}} dessas cópias dizem coisas um pouco diferentes.
   **{{N_CONTRA}} contradições** de verdade (duas regras que não dá para cumprir juntas), {{N_PEQ}} diferenças pequenas e
   {{N_VENC}} regras que parecem vencidas. {{N_GER}} regras são só da gerente e não precisam ir para agente nenhum.
2. **Hoje o implementador recebe {{HOJE_MIN}} mil caracteres de regras** (CLAUDE.md inteiro, o arquivo dele e o índice da
   memória), e até {{HOJE_MAX}} mil se ler tudo o que o índice manda "antes de qualquer trabalho". **No pacote de exemplo
   (a peça nova do Windows), as regras são {{PAC_REGRAS}} mil caracteres** (10 "sempre" e {{PAC_N}} do trabalho), e o
   pacote inteiro, com as decisões copiadas do Livro e o formulário, {{PAC_TOTAL}} mil. Cerca de {{RAZAO}} vezes menos regra.
3. **A máquina pode cobrar {{N_MAQ_SIM}} regras inteiras e {{N_MAQ_PARTE}} em parte.** {{N_JA}} conferências dão para
   fazer já; {{N_ESTUDO}} precisam de estudo. Rodando o esboço (só leitura) no código de hoje do obra, as três primeiras
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

{{CATALOGO}}

### As contradições (não resolvidas, só apontadas)

{{CONTRADICOES}}

### Diferenças pequenas

{{DIFERENCAS}}

### Regras que parecem vencidas

{{VENCIDAS}}

### O que está no meio das regras mas é informação

{{INFORMACAO}}

---

## 2. As regras "sempre" (vão em todo pacote)

Escolhidas pelo que já deu errado mais vezes e pelo que o Samuel mandou que **todo** agente leia. Cada uma junta
várias regras do catálogo (entre parênteses), para o pacote não repetir.

{{SEMPRE}}

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

{{TABELA}}

---

## 4. O pacote de exemplo: a peça nova do Windows

O próximo trabalho real é o **passo 1 do plano da parte do Windows**: escrever o "porteiro do Windows" e a pasta segura
(peças 1 e 2) em `core/windows.py`, com os testes da lógica em volta, sem mudar nenhum chamador. Abaixo está o texto
exato que o implementador receberia: o pedido curto da gerente (modelo da seção 7) e o pacote que o programa monta
(`esbocos/montar_pacote.py`) a partir de "implementador", dos dois arquivos novos e das decisões que o pedido toca.

**Tamanho, comparado ao de hoje:**

| | hoje | com o pacote |
|---|---|---|
| Regras que o agente tem de ler | CLAUDE.md {{C_CLAUDE}} + implementador.md {{C_IMPL}} + índice da memória {{C_INDICE}} = **{{HOJE_MIN_N}}** caracteres (até {{HOJE_MAX_N}} com as fichas que o índice manda ler antes de tudo) | "sempre" {{C_SEMPRE}} + regras do trabalho {{C_TRAB}} = **{{C_REGRAS_N}}** |
| Regras de tela, imagem e Central que não servem para este trabalho | vão junto | não vão (dizem no fim que não vieram) |
| Decisões do Livro | a gerente copia à mão | o programa copia da linha do Livro ({{C_DEC}}) |
| O que entregar | listas diferentes em cada arquivo de agente | um formulário só, conferido ({{C_FORM}}) |
| **Total** | **{{HOJE_MIN_N}}** + o pedido | **{{PAC_TOTAL_N}}** com o pedido |

Para comparar: o mesmo programa monta {{OUTROS}}.

O pedido de exemplo inteiro está no arquivo `pedido-exemplo` (nos três formatos), e é este:

{{PEDIDO}}

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

### 5.1 As que dão para fazer já ({{N_JA}})

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

### 5.2 As que precisam de estudo ({{N_ESTUDO}})

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
  (o que o montador devolve), `ONDE-PAREI.md`, e `esbocos/`: `catalogo.py` (as {{N_TOTAL}} regras em dados),
  `tabela_arquivos.py`, `montar_pacote.py`, `conferir_codigo.py`, `conferir_entrega.py`, `montar_proposta.py` (gera
  este documento a partir dos dados). Nada está ligado; nada foi rodado contra o PC fora de leitura do git e do código.
- Contas: `python esbocos/catalogo.py` dá os números do catálogo; `python esbocos/tabela_arquivos.py obra-2026-10-26`
  confere a cobertura da tabela.
- Achado no caminho, para a Lista de bugs (não impede; D-765 segura o conserto): as dicas de tela do Automático
  "desligar as marcadas" e a do retângulo do corte mostram "D-068" e "D-094" ao Kaique (`ui/automatico.py` 765 e
  2304, no obra). Mesmo tipo do bug de 17/11 dos passos dos testes à distância.
- O `CLAUDE.md` da cópia `obra-juncao` (66.755 caracteres) é mais velho que o do `fase-1` (71.186): o catálogo usa o do
  `fase-1`.
