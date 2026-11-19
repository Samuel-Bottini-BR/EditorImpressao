# Passo 0 do plano da parte do Windows: o pacote de regras, o porteiro e o formulário (19/11/2026)

Implementador. Ramo `passo0-porteiro-2026-11-19`, worktree `.claude/worktrees/passo0`, saiu de `obra-2026-10-26`
(`746dbda6`). Nenhuma linha do programa (`core/`, `ui/`, arquivos do programa na raiz) muda. Este ONDE-PAREI é também
o formulário da entrega (D-792), conferido pelo próprio programa:
`python -m regras_dos_agentes entrega relatorios/passo0-2026-11-19/ONDE-PAREI.md --etapa quebrar --pacote
relatorios/passo0-2026-11-19/anexos/pacote-passo0.md`. O pacote do meu pedido foi montado por mim, com o montador, a
partir da lista de arquivos do pedido da gerente (a gerente não tinha mandado um pacote neste passo).

## Pedido

- Papel: implementador
- Commit de partida: 746dbda6
- Ramo: passo0-porteiro-2026-11-19

## Arquivos que vou mexer

- `regras_dos_agentes/` (pasta nova: o pacote, o porteiro, a lista de exceções, o formulário, o montador)
- `tests/test_conferencias_*.py` (novos)
- `tests/conferencias_excecoes.json` (novo: a lista de exceções, proposta, esperando o "sim")
- `ganchos/pre-commit` (novo; não ligado)
- `relatorios/passo0-2026-11-19/` (este relatório)

## Onde parei

- Primeira entrega: 44 lugares. Primeira volta de quem quebrou (19 achados): 125. Segunda volta (N1 a N9): 189.
  Terceira volta (`quem-quebrou/relatorio-3.md`, R1 a R7, furos de estrutura): consertada nesta volta, pela estrutura
  (ver "Como ficou cada achado da terceira volta").
- **A lista: 176 lugares em 176 itens** (um item por lugar: arquivo, conferência, função e texto).
- **D-802 (19/11): os 56 lugares de fora do plano passaram para "depois da entrega"** (ver "D-802", logo abaixo). A lista continua "proposta", sem o "sim" escrito: quem liga é a gerente, na versão de teste (D-801).
- Quarta volta (`quem-quebrou/relatorio-4.md`, Q1 a Q7): consertada (ver "Como ficou cada achado da quarta volta").
- Quinta volta (`quem-quebrou/relatorio-5.md`, S1 a S3): consertada nesta volta (ver "Como ficou cada achado da
  quinta volta").
- O juiz já está no workflow (a gerente aplicou no `c41e4309`, no ramo dos testes). **Nada a mudar nele nesta volta:**
  o nome do trabalho ("Porteiro (juiz da versao de teste)") é o que o formulário agora procura.
- **O formulário dos próximos passos fica pendente até a gerente ligar a lista** (Q5): com a lista "proposta", a K21
  dá "não conferido" (código 3) em toda entrega, de propósito.

## D-802

Pedido da gerente (19/11): os 56 lugares "fora do plano, a perguntar" passam a "depois da entrega", como os 5 da
D-800. Palavras do Samuel, à pergunta "esses 56 ficam para depois da entrega ao Kaique? Sugiro que sim.": "ok,
continuamos assim e vamos proceguir". A D-801 ("ok": a lista entra como está e o porteiro passa a barrar) quem liga é
a gerente, direto na versão de teste; aqui a lista continua "proposta" e `sim_do_samuel` continua vazio.

- **A tabela (`regras_dos_agentes/excecoes.py`):** os lugares de "depois da entrega" ficaram em duas listas, uma por
  decisão (`_DEPOIS_D800`, as linhas de antes, e `_DEPOIS_D802`, as 56 novas), que entram no `PASSO_QUE_CONSERTA`
  antes da linha final. Cada linha da D-802 nomeia a função onde o lugar estava (nunca "*" na função; no pacote do
  teste de velocidade, "" = fora de função). **A linha final continua "fora do plano, a perguntar"**: um lugar novo,
  numa função nova do teste de velocidade ou de qualquer arquivo, não entra calado como "depois da entrega".
- **Uma conta só:** `regra_do_lugar` acha a linha que vale; `passo_do_lugar` (a lista) e
  `decisao_que_deixou_para_depois` (o texto para o Samuel) perguntam a ela. O texto não tem lista de funções copiada.
- **A lista, gerada de novo pelo programa** (`python -m regras_dos_agentes excecoes --gerar --de-novo`): 176 lugares
  em 176 itens; 107 no plano (passo 2: 1, 3: 38, 4: 50, 5: 18); 69 "depois da entrega" (13 da D-800, 56 da D-802);
  zero "fora do plano". `situacao` "proposta", `sim_do_samuel` vazio. Conferido contra a lista de antes: as mesmas
  176 chaves, os mesmos "quantas" e linhas; mudaram só o passo e o motivo dos 56, o commit lido e a explicação do
  topo. O porteiro no repositório inteiro, comparado com a lista nova: nenhum lugar novo, nenhum consertado.
- **O texto para o Samuel** (`lista-de-excecoes-para-o-samuel.md`, `.html`, `.pdf`, por `relatorio.gravar`; o `.pdf`
  fica fora do git): a pergunta dos 56 saiu; eles aparecem em "Ficam para depois da entrega ao Kaique, como você
  escolheu em 19/11 (69 lugares)", depois dos pedaços da D-800, com o que cada pedaço faz. Abri o PDF e conferi.
- **As provas (`tests/test_conferencias_excecoes.py`):**
  - Mudou `test_so_os_lugares_que_o_samuel_deixou_para_depois_ficam_depois_da_entrega` (era a prova da D-800), por
    causa da decisão nova, não para passar. Antes: os arquivos "depois da entrega" eram um subconjunto de três
    arquivos, e nos arquivos da D-800 o resto podia estar "fora do plano". Agora: cada lugar "depois da entrega" tem
    de ser uma das funções que o Samuel deixou para depois (D-800 ou D-802, escritas no próprio teste, à parte da
    tabela), todo lugar dessas funções que está na lista tem de ser "depois da entrega", não pode haver nenhum "fora
    do plano" (a prova escrita na D-802), e as contas por decisão só podem cair (13 e 56). A cobrança ficou mais
    estreita (por função, não por arquivo).
  - A constante `ARQUIVOS_DE_FORA_D800` saiu; no lugar, `DEPOIS_D800` e `DEPOIS_D802` (arquivo, conferência, função).
  - Novo `test_d802_a_tabela_do_programa_poe_cada_lugar_dele_depois_da_entrega_com_a_decisao_certa`.
  - Novo `test_d802_lugar_novo_que_ninguem_classificou_continua_fora_do_plano_a_perguntar`: funções novas no teste
    de velocidade, no brasão, na tela de início e no pacote do teste de velocidade, outra conferência numa função da
    lista e o `main.py` continuam "fora do plano"; e pelo caminho inteiro (porteiro + `gerar`). Conferi que ele pega
    o jeito errado: com uma linha `("teste_velocidade.py", "K01", "*", depois da entrega)` na tabela, ele falha.
  - No código anterior (`69b3937c`), os três falham (o primeiro pelos 56 "fora do plano"; os dois novos porque a
    função de decisão não existia).

## Como ficou cada achado da quinta volta

Quinta volta de quem quebrou (`quem-quebrou/relatorio-5.md`): três pequenos, todos do mesmo tipo (código que o Python
carrega e o porteiro não lia). Commit `b5927774`.

- **S1: nenhuma pasta "não é programa" pode ter o nome de um módulo da raiz.** `historico` saiu da lista
  `NAO_E_PROGRAMA`. A pasta `historico/` continua no git como está; o porteiro passa a lê-la, mas ela não tem nenhum
  `.py` nem nome com acento, então não acha nada (a lista de exceções continua com 176 lugares em 176 itens). Um
  `historico/__init__.py` novo agora é lido como programa, e a pasta já é protegida pela conferência das mudanças (o
  handoff só muda com pedido do Samuel). E a colisão não pode voltar: `porteiro.pastas_de_fora_com_nome_de_modulo`
  acusa (K00, que nunca entra na lista) qualquer pasta da lista com o nome de um arquivo de código solto na raiz (ex.:
  alguém criar um `docs.py`). Isso roda no porteiro, então também no juiz, com o código da versão de teste.
  - **Por que não o jeito do `__init__.py`:** a pasta `tests/` tem `__init__.py` de propósito (três scripts da raiz
    importam `tests`), então "acusar `__init__.py` nas pastas de fora" precisaria de exceção já no primeiro dia. E o
    que deixa a pasta tomar o lugar de um arquivo do programa é ter o mesmo nome dele: sem esse nome, um
    `__init__.py` não substitui nada. Com o nome, a pasta sai da lista e é lida inteira. Uma regra, sem exceção.
  - Provas: `tests/test_conferencias_codigo.py::test_s1_nenhuma_pasta_de_fora_tem_o_nome_de_um_modulo_da_raiz` (no
    repositório de verdade) e `::test_s1_a_pasta_com_nome_de_modulo_e_lida_e_a_colisao_e_acusada` (o
    `historico/__init__.py` com `schtasks` de quem quebrou é acusado; um `docs.py` na raiz dá K00).
- **S2: o porteiro lê `.pyw`.** Ficou num lugar só (`porteiro.FONTE_PYTHON` = `.py` e `.pyw`, e `e_fonte_python`).
  Todas as conferências que olhavam `.py` perguntam a ela: o porteiro do código, a K10 e a K12 das mudanças, o teste
  antigo e as funções do Livro no formulário. Hoje não há `.pyw` no git. Prova: `::test_s2_o_pyw_e_lido_como_codigo`.
- **S3: `.pyd` é acusado junto com o código compilado** (`porteiro.COMPILADO_PYTHON` = `.pyc`, `.pyo`, `.pyd`). A
  `.dll` do ScanTailor não entra (o Python não a importa como módulo). Hoje não há `.pyd` no git. Prova:
  `::test_s3_a_extensao_compilada_pyd_e_acusada`.
- As duas listas novas são protegidas ("igual"), como a das pastas.
- **Teste de reversão:** os quatro testes acima falham no código anterior (`65843bb3`) e passam no novo. O primeiro
  falha lá porque a função que conta a colisão não existia; quem prova o comportamento é o segundo (lá, o
  `historico/__init__.py` não era lido).

## Como ficou cada achado da quarta volta

Quarta volta de quem quebrou (`quem-quebrou/relatorio-4.md`), com as escolhas da gerente. Commit `a664329e`.

- **Q1: a marca do juiz só vale lida no trabalho dele.** Antes, o formulário (K21) lia a primeira marca
  "PORTEIRO: ..." de qualquer trabalho da rodada; o código do agente, que roda na suíte, podia escrever
  "PORTEIRO: CONFERIDO" antes do juiz. Agora: `conversa_com_o_github.marca_do_juiz` lê só o trabalho de nome
  "Porteiro (juiz da versao de teste)" (o nome vem do workflow, no ramo dos testes, que o agente não controla; conferi
  que é o mesmo nome no `c41e4309`), pela API de trabalhos da rodada; e a marca só conta quando a linha inteira é a
  marca (depois do nome do trabalho, do passo e da hora que o GitHub põe na frente), valendo a última. Rodada sem esse
  trabalho, ou com ele pulado: sem marca, e a K21 fica pendente (nunca "passou"). Provas:
  `tests/test_conferencias_formulario.py::test_q1_a_marca_so_vale_lida_no_trabalho_do_juiz` (o registro falso de quem
  quebrou: a suíte escreve "CONFERIDO", o juiz "NAO CONFERIDO"; vale o do juiz) e
  `::test_a_marca_do_juiz_e_lida_no_registro_da_rodada` (no formato real do GitHub; `echo 'PORTEIRO: CONFERIDO'` no
  meio da linha não conta). Conferido no registro real da rodada 44479180182 (a primeira com o juiz): devolve
  "NAO CONFERIDO (a versão de teste obra-2026-10-26 ainda não tem o porteiro)". Mudei um teste meu desta tarefa
  (`test_a_marca_do_juiz_e_lida_no_registro_da_rodada`): o exemplo "x PORTEIRO: ..." agora tem a frente que o GitHub
  põe, porque marca no meio da linha deixou de valer de propósito. Não é teste antigo do projeto.
- **Q2: todo `.py` conta como programa, menos uma lista curta de pastas.** A lista, num lugar só
  (`porteiro.NAO_E_PROGRAMA`): `tests`, `relatorios`, `.github`, `.claude`, `docs`, `memoria`, `historico`,
  `gabarito`, `regras_dos_agentes`, `ganchos`, `terceiros`, `velhos`. O porteiro (`e_programa`) e a K08 (nome com
  acento) leem dela; ela é protegida ("igual": pôr uma pasta ali afrouxa o porteiro e o juiz acusa). Pasta nova
  (ex.: `servicos/`) conta como programa. **A lista de exceções não muda com isso:** gerada de novo, continua com 176
  lugares em 176 itens (só o commit lido mudou). Prova:
  `tests/test_conferencias_codigo.py::test_q2_todo_py_fora_das_pastas_de_fora_e_programa` (o `servicos/__init__.py`
  com `schtasks` de quem quebrou é acusado; o mesmo texto em `tests/` não).
- **Q3: o pacote diz as funções de outros passos que não se mexem.** O montador ganhou `--passo`: com ele, o pacote
  escreve, antes da lista dos lugares, "Não renomeie nem mova estas funções neste trabalho", com cada função dos
  arquivos do pedido que guarda lugar de outro passo (o lugar é a função e o texto). É ressalva do pacote, não
  conferência nova. O texto para a gerente pôr no plano dos passos 3 e 4 está em `anexos/funcoes-que-nao-se-mexem.md`,
  tirado pelo mesmo montador:
  - Passo 3 (`atualizacao.py`): não mexer em `ao_desinstalar` e `criar_as_tarefas` (lugares do passo 5).
  - Passo 4 (`core/testes_a_distancia.py`): não mexer em `_comando_apagar_a_pasta_das_tarefas_se_vazia`,
    `_comando_preparar_o_desfazer`, `_passos_das_nossas_tarefas`, `_passos_dos_testes_a_distancia` e
    `xml_da_tarefa_do_desfazer` (lugares do passo 5).
  - O pacote do passo 1 não muda: os arquivos dele não têm lugar nenhum na lista.
  Prova: `tests/test_conferencias_pacote.py::test_q3_o_pacote_do_passo_diz_as_funcoes_de_outros_passos_que_nao_se_mexem`.
- **Q4: código compilado (`.pyc`, `.pyo`) guardado no repositório é acusado** (K00, que nunca entra na lista): o
  Python o importa e o porteiro não consegue lê-lo. Prova:
  `tests/test_conferencias_codigo.py::test_q4_codigo_compilado_sem_fonte_no_repositorio_e_acusado`.
- **Q6: antes do "sim", tirar item da lista sem consertar barra.** Com a lista ainda "proposta", o juiz não julgava o
  código, e o ramo podia encolher a lista que vai ao "sim". Agora o juiz sempre roda o porteiro da versão de teste no
  código do ramo e, com a lista proposta, acusa o item que o ramo tirou (ou diminuiu) enquanto o código ainda tem
  aquele lugar (`juiz.tirados_sem_conserto`); tirar o item de um lugar consertado de verdade continua dando
  "NAO CONFERIDO" (não barra). Prova: `tests/test_conferencias_juiz.py::test_q6_antes_do_sim_tirar_da_lista_sem_consertar_barra`.
- **Q7: a pergunta dos 56 lugares fica sem print**, como a gerente aceitou. O texto para o Samuel diz isso nas
  ressalvas: "esta pergunta não tem print. Esses pedaços são código que não aparece na tela: conversam com o Windows
  por baixo, sem janela nem botão." Regravado nos três formatos (`lista-de-excecoes-para-o-samuel.md`, `.html`,
  `.pdf`; o `.pdf` fica fora do git). No ONDE-PAREI, a pergunta continua mostrando o print do "Reiniciar agora", agora
  com a legenda certa ("o mesmo tipo de erro num pedaço que aparece na tela; os 56 não aparecem"): o formulário (F17)
  cobra um print em toda pergunta, e eu não afrouxei essa regra sozinho. Se a gerente preferir a pergunta sem print
  nenhum, o F17 precisa aceitar "sem print" com o motivo escrito: é uma mudança de regra, e é dela.
- **Q5: é o combinado.** **O formulário dos próximos passos fica pendente até a gerente ligar a lista:** enquanto a
  lista da versão de teste for "proposta", o juiz escreve "PORTEIRO: NAO CONFERIDO (...)", e a K21 do formulário de
  qualquer entrega dá "não conferido" (código 3), nunca "passou". Isso vale para o passo 1 em diante, até a gerente
  ligar a lista na versão de teste (depois do "sim" do Samuel) e trocar `PORTEIRO_LIGADO` para "1".
- **Teste de reversão:** os seis testes acima rodaram no código anterior (`regras_dos_agentes/` do commit `b66e6be9`,
  com os testes novos) e os seis falharam; no código novo, passam.

## Como ficou cada achado da terceira volta

- **R1 (grave): nenhum item entra na lista por ramo de agente.** Saiu do código o caminho de abrir a lista ou pôr item
  com um "sim" (`problema_do_sim`, `acrescentados_sem_sim` e as leituras do Livro que só serviam a isso). A conta
  única (`porteiro_mudancas.mudancas_na_lista`) acusa sempre, com ou sem "sim": item novo, "quantas" maior, passo,
  situação e "sim" mudados. Ela é usada pela proteção, pelo juiz da rodada, pela K17 do formulário e pelo gancho. O
  gancho só deixa mudar a lista no ramo da versão de teste (é ali que a gerente liga, depois do "sim" do Samuel
  registrado no Livro). O `sim_do_samuel` continua no arquivo como registro do que ela fez, não como chave. Provas:
  `tests/test_conferencias_excecoes.py::test_r1_qualquer_item_novo_ou_ligar_e_mudanca_que_so_a_gerente_faz` (até com o
  "sim" de 12 letras da D-791 que o quebrador forjou),
  `tests/test_conferencias_antes_do_commit.py::test_o_gancho_barra_mexer_na_situacao_ou_no_sim_num_ramo_de_agente`,
  `tests/test_conferencias_antes_do_commit.py::test_na_versao_de_teste_a_gerente_liga_a_lista`,
  `tests/test_conferencias_protecao.py::test_item_novo_com_qualquer_sim_e_acusado_e_tirar_item_e_livre`.
- **R2 e R3 (o juiz vem de fora do ramo).** Novo `regras_dos_agentes/juiz.py`: o porteiro e a lista **da versão de
  teste** julgando a cópia do ramo. A rodada do GitHub o roda assim: o workflow (no ramo dos testes) troca o código pelo
  do ramo pedido, como hoje; busca a versão de teste (o nome `obra-2026-10-26` escrito no workflow, não no ramo); tira
  dela, numa pasta à parte, o pacote `regras_dos_agentes/` e a lista; e roda `python -m regras_dos_agentes juiz
  --conferido <cópia do ramo>` de dentro dessa pasta. O juiz confere a lista do ramo contra a da versão de teste (R1)
  e, quando a lista da versão de teste já vale, roda o porteiro da versão de teste no código do ramo: afrouxar o
  porteiro do ramo (tirar o `re.I`, deixar uma pasta de fora, trocar o pacote inteiro) não tira lugar nenhum da lista.
  Provas: `tests/test_conferencias_juiz.py` (8 testes, entre eles
  `tests/test_conferencias_juiz.py::test_r3_afrouxar_o_porteiro_do_ramo_nao_tira_lugar_da_lista` e duas rodadas do
  próprio script do workflow com um "GitHub" de prova). Prova de verdade no repositório real, em 19/11 (o script do
  anexo, rodado na minha cópia): contra `obra-2026-10-26` de hoje, "PORTEIRO: NAO CONFERIDO (a versão de teste
  obra-2026-10-26 ainda não tem o porteiro)", código 0; com este ramo no lugar da versão de teste (como ficará depois
  de juntar), "PORTEIRO: NAO CONFERIDO (a lista de exceções da versão de teste ainda espera o "sim" do Samuel)"; com
  as duas listas em "valendo", "PORTEIRO: CONFERIDO"; com a versão de teste "valendo" e o ramo ainda "proposta",
  "PORTEIRO: BARROU" (a situação mudou).
  **"Parado" nunca vira "passou":** o juiz sempre escreve uma linha com a marca (CONFERIDO, BARROU ou NAO CONFERIDO e o
  motivo), que vira aviso no topo da rodada e no resumo; a K21 do formulário lê a marca no registro da rodada e trata
  "sem juiz" e "NAO CONFERIDO" como pendente (código 3) e "BARROU" como problema
  (`tests/test_conferencias_formulario.py::test_k21_o_juiz_do_porteiro_tem_de_ter_conferido`).
  **A primeira vez (a junção deste passo, pela gerente):** antes de juntar, a versão de teste não tem o porteiro: o juiz
  diz "NAO CONFERIDO (a versão de teste ainda não tem o porteiro)" e a rodada não falha por isso. No commit em que
  juntar o passo 0, a gerente troca `PORTEIRO_LIGADO` para "1" no workflow: daí em diante, a versão de teste sem o
  porteiro faz a rodada falhar. Depois de juntar e até o "sim", o juiz já barra item novo e mudança da lista, e diz
  "NAO CONFERIDO" para o código. Depois do "sim" (a gerente liga a lista direto na versão de teste), ele julga tudo.
- **R4 (pergunta ao Samuel, não decidido).** Do teste de velocidade, só a leitura da placa de vídeo e do tipo de disco
  pelo PowerShell (as funções `_placas_de_video`, `tipo_do_disco`, `_powershell`, `_caminho_do_powershell`: 9 lugares)
  fica "depois da entrega (D-800)". Os outros 43 (a memória do computador e do próprio teste, a janela preta, impedir
  o computador de dormir, a classe da janela, o registro do Windows) entram na pergunta dos "fora do plano",
  explicados em palavras simples. O texto não diz "como você escolheu" sobre eles.
- **R5 (falsos alarmes do apelido).** Uma função só "devolve a biblioteca" quando devolve a biblioteca em si (ou um
  `lambda` que a usa), não o resultado de uma chamada feita por ela; quem recebe o que ela devolve vira apelido só na
  posição certa da tupla; `self.metodo()` só segue o método da mesma classe; e o resultado de uma chamada
  (`_MARCA = ctypes.windll.kernel32.CreateMutexW(...)`) não vira apelido. Saíram `atualizacao.py:748` e
  `teste_velocidade.py:2317`. Um teste para cada caso (`tests/test_conferencias_codigo.py::test_r5_...`, 4 testes),
  que falham no código anterior (`8a1f56d8`).
- **R6 (`creationflags` só para esconder a janela).** A busca por texto do `creationflags` saiu; no lugar, a leitura
  da estrutura do código (`porteiro._bandeiras_do_windows`) segue o valor (o número, `subprocess.NOME`,
  `getattr(subprocess, "NOME", ...)`, `a | b`, `x if c else y`, a variável do mesmo arquivo). Esconder a janela preta
  (`CREATE_NO_WINDOW`) e baixar a prioridade (`BELOW_NORMAL_PRIORITY_CLASS`, `IDLE_PRIORITY_CLASS`) não contam; o
  `DETACHED_PROCESS`, as outras bandeiras e o valor que não dá para ler continuam. Saíram os 5 lugares (o Tesseract 2,
  o Kraken 1, as páginas em outro processo 1, a tela de carregamento 1). **Escolha minha, para a gerente conferir:**
  dois dos 5 (o Tesseract ao rodar e o Kraken) somam a prioridade baixa à janela escondida; contei a prioridade baixa
  junto, porque ela também não muda o Windows e a gerente disse que os 5 saem. Provas:
  `tests/test_conferencias_codigo.py::test_r6_abrir_sem_janela_preta_nao_e_conversa_com_o_windows` e
  `tests/test_conferencias_codigo.py::test_r6_outra_bandeira_continua_sendo_conversa_com_o_windows`.
- **R7.** Os itens 2 e 12 da primeira volta foram reescritos com o que o código faz hoje.
- **O lugar passa a ser arquivo, conferência, função e texto.** O mesmo texto (`import winreg`) aparece em duas funções
  do teste de velocidade com destinos diferentes (uma é a decisão de 19/11, a outra vai para a pergunta). Com a
  função na chave, cada um tem o seu item, e a mesma linha levada para outra função passa a contar como lugar novo (o
  caso antigo do achado 11 da primeira volta).
- **N1 da segunda volta:** a conferência do "sim" no Livro foi substituída pela R1 (o "sim" não abre mais nada num ramo
  de agente).

## A mudança do workflow (para a gerente aplicar no ramo dos testes; eu não mexi)

Aplicada pela gerente no `c41e4309`. Na quarta volta não precisa mudar nada; só o passo 4 abaixo continua por fazer,
na junção. Se um dia o nome do trabalho do juiz mudar no workflow, o `TRABALHO_DO_JUIZ` de
`regras_dos_agentes/conversa_com_o_github.py` tem que mudar junto (senão a K21 fica pendente em toda entrega; nunca
passa).

No ramo `claude/list-server-files-gkos8v`:
1. **Arquivo novo `.github/scripts/porteiro_juiz.sh`:** o conteúdo inteiro de
   `relatorios/passo0-2026-11-19/anexos/juiz-no-workflow/porteiro_juiz.sh` (testado com o git e o bash de verdade:
   `tests/test_conferencias_juiz.py`, as duas últimas provas, e no repositório real, acima).
2. **`.github/workflows/testes-windows.yml`:** acrescentar o job `porteiro` de
   `relatorios/passo0-2026-11-19/anexos/juiz-no-workflow/job-porteiro.yml` dentro de `jobs:`, logo depois do job
   `suite`, e mudar o `needs:` do job `resumo` para `[suite, janela, porteiro]`.
3. **`trocar_codigo.sh` não muda.**
4. **No commit em que juntar o passo 0 na versão de teste:** trocar `PORTEIRO_LIGADO: "0"` para `"1"` no job.

## Como ficou cada achado da segunda volta

- **N1 (grave), o "sim" forjável.** O "sim" é conferido no Livro da versão de teste no GitHub
  (`origin/obra-2026-10-26`, `Livro.da_versao_de_teste`), nunca no da pasta nem no do ramo do agente. Ele tem de citar
  uma decisão que exista lá e trate da lista de exceções, e trazer um trecho literal, de ao menos 12 letras, da coluna
  das palavras do Samuel daquela decisão (`excecoes.problema_do_sim`). O gancho também lê o Livro da versão de teste;
  sem internet, barra (código 3). Provas do ataque do quebrador (`"palavras": "sim"`):
  `tests/test_conferencias_excecoes.py::test_o_sim_forjado_nao_passa` (5 jeitos de forjar),
  `tests/test_conferencias_antes_do_commit.py::test_o_gancho_barra_o_sim_forjado_num_item_novo`,
  `tests/test_conferencias_antes_do_commit.py::test_o_gancho_barra_a_lista_valendo_com_o_sim_forjado`,
  `tests/test_conferencias_antes_do_commit.py::test_sem_internet_o_gancho_barra_em_vez_de_passar`,
  `tests/test_conferencias_protecao.py::test_item_novo_com_o_sim_forjado_e_acusado` e
  `tests/test_conferencias_protecao.py::test_o_livro_do_ramo_nao_vale_so_o_da_versao_de_teste` (o agente que escreve a
  decisão no Livro do próprio ramo não passa). Consequência para ligar a lista: a gerente registra o "sim" do Samuel
  como uma decisão no Livro da versão de teste (com as palavras dele e dizendo que é sobre a lista de exceções) e a
  cita em `sim_do_samuel`. A D-791 de hoje não serve sozinha: as palavras dele ali ("não sei do que você está
  falando" · "b") não são o "sim" à lista.
- **N2, o apelido do ctypes.** O porteiro segue o apelido dentro do arquivo (`porteiro._apelidos_do_windows`): o nome
  que recebe a biblioteca, a função que a devolve (inclusive num `lambda`), quem recebe o que ela devolve, e toda
  linha que usa esses nomes. O resultado de uma chamada feita pela biblioteca não vira apelido. `CDLL`/`cdll` com uma
  biblioteca do Windows conta; `creationflags` com qualquer valor que não seja o 0 escrito conta (inclusive guardado
  numa variável). O caso do `teste_velocidade.py:1746` (`return kernel32, ...`) é seguido: a função
  `_entrada_da_janela_preta` devolve a biblioteca, e as linhas de quem a recebe (1758, 1760, 1771, 1772, 2252 a
  2255) entram na lista. Prova: `tests/test_conferencias_codigo.py::test_k01_segue_o_apelido_da_biblioteca_do_windows`.
  O que não é seguido está nas ressalvas.
- **N3, afrouxar a busca pelo uso.** Cada palavra da busca agora tem um exemplo (uma palavra por linha, 48 linhas). A
  proteção do GitHub pega o exemplo de cada palavra da lista da versão de teste (gerado dos dados de lá, não escrito à
  mão) e cobra que o porteiro do ramo ainda o acha (`protecao.exemplos_que_o_porteiro_nao_acha`). Prova:
  `tests/test_conferencias_protecao.py::test_afrouxar_a_busca_pelo_uso_e_acusado` (o caso do `msiexec`). Nomes
  acrescentados: `sc create` em lista, `net stop`/`net start`, `taskkill`, `Stop-Process`, `-ComObject`,
  `Get-PhysicalDisk` (e `Get-Disk`, `Get-Volume`, `-Partition`), `CDLL`/`cdll` do Windows, `shutdown`,
  `Restart-Computer`, o registro de eventos (`Write-EventLog`, `wevtutil`). Prova:
  `tests/test_conferencias_codigo.py::test_k01_acusa_os_nomes_que_ainda_escapavam`.
- **N4.** O rótulo só vale na `quem-quebrou/` do próprio trabalho
  (`tests/test_conferencias_mudancas.py::test_k10_o_rotulo_so_vale_na_quem_quebrou_do_proprio_trabalho`).
- **N5.** `creationflags=0`, "self-service" e "hku:" não são mais alarme
  (`tests/test_conferencias_codigo.py::test_k01_falsos_alarmes_que_quem_quebrou_apontou_nao_sao_acusados`).
- **N6, o texto para o Samuel.** O print é de verdade: uma cópia (marcada em vermelho) do print da janela de versão
  nova com o "Reiniciar agora", tirado na instalação de 18/11 (`saida_teste/etapa5/prints/fase4/1-aviso.png`; não
  abri o programa). O teste de velocidade inteiro foi para "depois da entrega (D-800)", como a régua dos filtros; o
  texto não fala mais em "5" e "6": diz os três pedaços que ele deixou para depois e quantas linhas a busca maior achou
  neles. **Na pergunta nova sobraram 18 lugares** (a tela de início 2, a memória livre 1, o motor de achar texto 4, o
  brasão 5, o pacote do teste de velocidade 1, e, achados pela regra nova do `creationflags`, os motores Tesseract 2 e
  Kraken 1, as páginas em outro processo 1 e a tela de carregamento 1).
- **N7.** A folha de estilo só conta com um seletor do Qt seguido de "{" e de uma propriedade
  (`tests/test_conferencias_codigo.py::test_k04_correcao_3_um_f_string_comum_com_chaves_nao_e_folha_de_estilo`).
- **N8.** As regras do Windows vêm do arquivo, pela tabela: o arquivo novo que só cai na linha de reserva (`core/*`)
  recebe todas as regras e a gerente é avisada (o título do pedido não conta mais)
  (`tests/test_conferencias_pacote.py::test_arquivo_novo_so_da_linha_de_reserva_recebe_todas_as_regras`,
  `tests/test_conferencias_pacote.py::test_os_arquivos_do_windows_ganham_as_regras_do_windows_pela_tabela`).
- **N9.** O pacote do meu pedido (`anexos/pacote-passo0.md`) foi montado com exatamente esta lista de arquivos:
  `regras_dos_agentes/`, `tests/test_conferencias_*.py`, `tests/conferencias_excecoes.json`, `ganchos/pre-commit`,
  `relatorios/passo0-2026-11-19/`; papel implementador; partida `746dbda6`; ramo `passo0-porteiro-2026-11-19`.
- **6, 7 e 8 pela metade:** fechados pelos itens N1, N3 e N6 acima.

## Como ficou cada achado de quem tentou quebrar (primeira volta)

1. **Ligar a lista deixava um teste vermelho.** O teste monta a lista com dados próprios e vale nos dois estados
   (`tests/test_conferencias_excecoes.py::test_a_lista_valendo_sem_o_sim_do_samuel_conferido_no_livro_nao_vale`). E uma
   rodada inteira do GitHub num ramo de prova, com a lista "valendo" e um "sim" de mentira, roda o teste que barra o
   repositório (ver "Testes").
2. **A busca do Windows conhecia poucas palavras.** Ampliada (`PALAVRAS_DO_WINDOWS`, uma palavra por linha, cada uma com
   um exemplo; na primeira volta eram 23 linhas: o PowerShell com
   qualquer nome, as tarefas por qualquer meio, o ShellExecute por qualquer nome, o cmd, o registro, a licença e o
   dono de arquivo, os instaladores, o firewall, os serviços, as contas, os recursos do Windows, o WMI e o COM, o
   pywin32, o ctypes, o número do DETACHED_PROCESS). Provas: os 18 jeitos de
   `tests/test_conferencias_codigo.py::test_k01_acusa_os_outros_nomes_da_mesma_conversa_com_o_windows` e o que não
   deve ser acusado. **Eram 44 lugares; ficaram 125.** Dos 81 novos: 75 estão nos arquivos que o plano conserta e
   ganharam o passo certo (o desfazer e a tarefa dele no passo 5, o resto pelo arquivo); 1 é a régua dos filtros (a
   linha que prepara a mesma pergunta, no mesmo pedaço que o Samuel deixou para depois); 22 ficam "fora do plano, a
   perguntar ao Samuel" (o teste de velocidade 16, a tela de início 2, a memória livre 1, o motor de achar texto 1, o
   brasão 1, o pacote do teste de velocidade 1). **Como está hoje (terceira volta):** além da linha onde a
   biblioteca do Windows é pega, o porteiro segue o apelido dela dentro do arquivo (sem os falsos alarmes da R5), e o
   `creationflags` é lido pela estrutura (R6). A conta de hoje é 176 lugares (ver "Onde parei").
3. **O papel era o que o agente escrevia.** Sem `--pacote`, o formulário volta (código 1); o papel e a lista que valem
   são os do pacote (`tests/test_conferencias_formulario.py::test_sem_o_pacote_da_gerente_o_formulario_volta`,
   `tests/test_conferencias_formulario.py::test_o_papel_que_vale_e_o_do_pacote`).
4. **A barreira do agente de tela só olhava `core/`.** Agora tudo fora de `ui/` que o pedido não nomeou, menos a pasta
   do relatório dele
   (`tests/test_conferencias_mudancas.py::test_k13_o_agente_de_tela_e_barrado_em_tudo_fora_de_ui_que_o_pedido_nao_nomeou`).
5. **O relatório de quem quebra batia com a barreira do rótulo.** Como ficou: o rótulo de pronto vale na pasta do
   próprio trabalho de quem confere (papel verificador ou quebrador, do pacote) e, no ramo de quem construiu, só dentro
   de `relatorios/<trabalho>/quem-quebrou/`, quando todo commit que mexeu nessa pasta mexeu só nela e o relatório diz,
   no pedido dele, que o papel é de quem confere. Fora disso, barra
   (`tests/test_conferencias_mudancas.py::test_k10_o_rotulo_de_quem_quebrou_vale_so_no_relatorio_dele_num_commit_so_dele`
   e os dois testes seguintes).
6. **O porteiro e a lista sem proteção contra o próprio agente.** No GitHub, `tests/test_conferencias_protecao.py`
   compara o ramo com a versão de teste (`obra-2026-10-26`, buscada no GitHub): a lista só diminui (item novo só com o
   "sim" próprio, conferido no Livro), a situação, o "sim" e o passo de cada item não mudam, e nenhum dado das buscas
   some (`regras_dos_agentes/protecao.py`). O "sim" do Samuel passa a ser conferido no Livro (decisão e palavras): um
   "sim" inventado não abre a lista. O porteiro, o gancho e as provas entram entre os arquivos que só a gerente muda
   (K17). **Continua sem proteção no GitHub:** o código das funções do porteiro (o que conta como programa, como se
   compara), os próprios testes e o `protecao.py`; para esses vale a K17 do formulário e quem tenta quebrar. E, antes
   de juntar este passo, a versão de teste ainda não tem o porteiro: até lá, o teste de proteção fica parado, com o
   motivo escrito.
7. **"Só diminui" não era conferido no GitHub nem antes do commit.** O GitHub, pelo item 6; antes do commit, o gancho
   compara a lista do commit com a do último commit e barra item novo sem o "sim"
   (`tests/test_conferencias_antes_do_commit.py::test_o_gancho_barra_o_agente_que_poe_o_proprio_erro_na_lista_no_mesmo_commit`).
8. **O texto para o Samuel.** Refeito pelo CLAUDE.md §11.13: primeira linha diz o que é e onde fica; dois casos reais
   (o "Reiniciar agora" que abre o PowerShell e fecha sem rodar; as dicas do Automático com número); diz o que ela faz
   ("barra o trabalho que acrescentar mais um lugar com um desses erros, escrito com as palavras que ela conhece") e o
   que não faz; o que acontece se ele disser não; de onde veio; e os 22 de fora do plano como pergunta, com as duas
   opções.
9. **K04 e K05 não olhavam `core/`.** Agora olham (hoje dá zero a mais)
   (`tests/test_conferencias_codigo.py::test_k04_e_k05_olham_tambem_os_avisos_que_moram_em_core`).
10. **A busca cega entre `/*` e `*/`.** Agora o comentário só sai de dentro do mesmo texto com cara de folha de estilo
    (`tests/test_conferencias_codigo.py::test_k04_correcao_3_so_dentro_do_mesmo_texto_da_folha_de_estilo`).
11. **O lugar é o texto da linha.** Não consertado: é o combinado no plano (arquivo, conferência, texto, quantas). Vai
    nas ressalvas, e o pacote de quem mexe num arquivo com lugares na lista passa a mostrá-los, com o aviso de que
    mexer numa dessas linhas sem consertar vira erro novo
    (`tests/test_conferencias_pacote.py::test_o_pacote_mostra_os_lugares_da_lista_nos_arquivos_do_pedido`).
12. **Arquivo novo sem as regras do Windows.** Como está hoje (desde a segunda volta, N8): vale a tabela, não o título
    do pedido. O arquivo novo que só cai numa linha de reserva (`core/*`) recebe todas as regras e a gerente é avisada
    (`tests/test_conferencias_pacote.py::test_arquivo_novo_so_da_linha_de_reserva_recebe_todas_as_regras`).
13. **Listas escritas em mais de um lugar.** A lista do Windows é uma só (a do porteiro; a tabela usa a mesma); as
    pastas de fora (`FORA_DO_PROJETO`) e quem pode escrever o rótulo (`QUEM_CONFERE`) também
    (`tests/test_conferencias_pacote.py::test_a_lista_do_windows_da_tabela_e_a_do_porteiro`).
14. **K11 não olhava os testes soltos da raiz.** Agora olha toda função dos `teste_*.py` da raiz
    (`tests/test_conferencias_mudancas.py::test_k11_olha_tambem_os_testes_soltos_da_raiz`).
15. **O rótulo numa linha numerada passava.** Agora `3. **Pronto para conferir**` conta. Entre aspas ou crases
    continua não contando, de propósito (é como se cita a regra): vai nas ressalvas.
16. **Textos que não batiam.** O docstring do porteiro cita o comando de verdade; o gancho não diz mais que pular com
    `--no-verify` é proibido por escrito (diz o que a documentação do git diz); a contagem de arquivos foi refeita
    pelo git (17 arquivos em `regras_dos_agentes/`, agora com o `protecao.py`).
17. **O instalador antigo (Inno, `instalador.iss`) conversa com o Windows fora do Python.** Não consertado: o porteiro
    só lê `.py`, e se o Inno ainda vale é da gerente (pergunta abaixo, para a gerente).
18. **O pacote do passo 1.** Remontado com a D-722 e a D-724. A regra da barra de rolagem com `#a8a49e` vem do
    CLAUDE.md §9 e contradiz os valores que a K22 cobra: não mudo o CLAUDE.md (pergunta abaixo, para a gerente).
19. **A K18 olhava a cópia local.** Agora pergunta ao GitHub de verdade (`git ls-remote`); sem internet, "não deu para
    conferir" (`tests/test_conferencias_mudancas.py::test_k18_barra_mudanca_fora_de_commit_e_sem_push`).

## Perguntas para a gerente

- O instalador antigo (Inno Setup, `instalador.iss`) ainda é usado? Se for, o `Exec` do `vc_redist` (linha 272) é
  conversa com o Windows fora da peça única que o porteiro não lê (ele só lê `.py`).
- O CLAUDE.md §9 diz que a barra de rolagem é `#a8a49e`; desde os temas, ela tem uma cor por tema (os valores que a K22
  cobra). O texto do CLAUDE.md é seu, com o "sim" do Samuel.
- Escrever nas regras dos agentes que pular a conferência antes do commit (`--no-verify`) é proibido? Hoje não está
  escrito em lugar nenhum das regras do projeto.

## Decisões que esta tarefa precisa cumprir

(Palavras copiadas do Livro, `docs/plano/DECISOES.md` desta cópia.)

- **D-767** (18/11/2026): "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione".
  Aqui: a conferência antes do commit é provada com o git de verdade, num repositório de verdade numa pasta temporária,
  com um Python de verdade; nada mexe no Windows.
- **D-775** (18/11/2026): "o agente vai tentar quebrar antes de fazer o teste real na tela né?". Aqui: o formulário
  confere as três etapas e os seis campos do relatório de quem quebra.
- **D-784** (18/11/2026): "ok, mas como vai saber que regras enviar para o agente?". Aqui: o pacote sai de um programa
  (catálogo + tabela arquivo → etiquetas + montador); um teste cobra que todo arquivo do git tem linha.
- **D-785** (18/11/2026): "ok, mais ainda existem mais casos na opção A". Aqui: nada deste passo mexe no Windows; não
  há prova à vista; nenhuma janela abre.
- **D-786** (18/11/2026): "a". Aqui: nenhum processamento muda; não há filtro de velocidade a rodar.
- **D-787** (18/11/2026): "A". Aqui: no PC, um arquivo de teste por vez; o conjunto inteiro no GitHub.
- **D-791** (18/11/2026): "não sei do que você está falando" · "b". Aqui: as 24 conferências viram testes em
  `tests/` e a mesma busca roda antes do commit; cada uma acusa um exemplo errado feito de propósito e não acusa o certo;
  a lista de exceções é por lugar, gerada pelo programa, e só diminui.
- **D-792** (18/11/2026): "mas e o que vai determinar o que vai nesse formulario? vai ser feito um toda vez que for
  enviado um trabalho para um agente?". Aqui: um programa confere o formulário (F1 a F20 e as perguntas das etiquetas)
  nas três etapas.
- **D-793** (18/11/2026): "ok". Aqui: a conferência K23 lê a lista de ferramentas de cada agente.
- **D-796** (19/11/2026): "1, mas tem que ser explissito o pedido né". Aqui: a K13 lê a lista de arquivos do pedido
  no formulário e barra o agente de tela que mexe em `core/` fora dela.
- **D-797** (19/11/2026): "Só precisa de dois lugares né?". Aqui: nada deste passo junta nem fala do `master`.
- **D-798** (19/11/2026): "fechou". Aqui: a K10 barra o rótulo de pronto no ramo de quem construiu e "APROVADO"
  escrito por agente. Esta entrega não traz esse rótulo.
- **D-799** (19/11/2026): "Aprova o plano?". Aqui: o passo 0 do plano-v3, como escrito.
- **D-800** (19/11/2026): "esses consertos deixa para depois". Aqui: os 5 lugares de fora ficam na lista marcados
  "depois da entrega".
- **D-801** (19/11/2026): à pergunta "a lista entra assim, e o porteiro passa a barrar erro novo? Sugiro que sim.":
  "ok". Aqui: quem liga a lista ("valendo" e o "sim") é a gerente, direto na versão de teste; no ramo ela continua
  "proposta".
- **D-802** (19/11/2026): à pergunta "esses 56 ficam para depois da entrega ao Kaique? Sugiro que sim.": "ok,
  continuamos assim e vamos proceguir". Aqui: os 56 lugares ficam na lista marcados "depois da entrega"; nenhum
  "fora do plano".
- **D-605** (03/11/2026): "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o
  que já está escolhido e testado". Aqui: nenhum teste antigo muda; o porteiro não é ligado no repositório.
- **D-637** (05/11/2026): "você tem que pensar na experiencia do usario e no resultado final do livro dentro do
  programa". Aqui: ver "Como fica para quem usa e no livro".

## O que já está escolhido e testado aqui

- Os testes que já existem e fazem parte do mesmo cuidado continuam como estão (plano-v3 §8, item 11):
  `tests/test_botoes_em_portugues.py`, `tests/test_sem_janela_na_tela.py`,
  `tests/test_memoria_nao_cresce_com_o_livro.py`, `tests/test_promessas.py` e as provas das decisões
  (`tests/test_decisoes.py` e os outros `test_decisoes_*`). Nenhum deles foi tocado; as conferências novas vivem em
  arquivos novos.
- A barra de rolagem cinza (CLAUDE.md §9): a K22 é escrita contra os valores de hoje de `ui/estilo.py`.

## Como fica para quem usa e no livro

- **O Kaique:** antes e depois, nada muda. Nenhuma tela, nenhum botão, nenhum texto do programa, nenhum arquivo do
  programa. O PDF que sai é o mesmo, página por página: nada do processamento foi tocado.
- **O Samuel:** recebe um texto curto com a lista de exceções para dizer "sim" (ver "Perguntas para o Samuel").
- **Os agentes e a gerente:** antes, as regras iam inteiras e o formulário não existia; depois, o pacote sai de um
  programa, o porteiro roda nos testes do GitHub (quando o Samuel disser "sim") e o formulário é conferido por programa.

## A causa, a regra e todos os caminhos

- **Por que existe:** na etapa 5, cada função conversava com o Windows do seu jeito e nada conferia o código antes de
  juntar (CLAUDE.md §11.12, caso da etapa 5). O porteiro barra esses erros já conhecidos; o pacote e o formulário fazem
  as regras chegarem ao agente e voltarem conferidas.
- **A regra, num lugar só:** cada conferência do código parado é uma função em `regras_dos_agentes/porteiro.py`
  (`k01()` a `k24()`, rodadas por `conferir_codigo()`); a comparação com a lista é `comparar()` em `excecoes.py`; as
  conferências das mudanças, `conferir_mudancas()` em `porteiro_mudancas.py`; o formulário, `conferir()` em
  `formulario.py`; as etiquetas de um trabalho, `etiquetas_do_trabalho()` em `tabela_arquivos.py`; se um arquivo está
  no pedido, `coberto()` em `pedido.py`; o Livro, a classe `Livro` em `livro.py`.
- **Os caminhos que chegam nelas (procurados com busca no código):**
  - teste do GitHub → `achados_do_repositorio()` → `conferir_codigo()` → `comparar()`;
  - conferência antes do commit (`ganchos/pre-commit` → `python -m regras_dos_agentes antes-do-commit`) →
    `achados_do_proximo_commit()` → `conferir_codigo()` → `comparar()`;
  - linha de comando `porteiro` → as mesmas duas de cima;
  - `excecoes --gerar` e `--diminuir` → `achados_do_repositorio()` → `gerar()` / `diminuir()` (que usa `comparar()`);
  - formulário (`entrega`) → `conferir_mudancas()` e as conferências de cada campo;
  - o que só a gerente pode mudar na lista → `mudancas_na_lista()`, chamada pela K17 do formulário, pelo teste de
    proteção do GitHub (`comparar()` em `protecao.py`) e pela conferência antes do commit;
  - o que é "conversa com o Windows" → a lista `PALAVRAS_DO_WINDOWS` do porteiro, usada pela K01 e pela tabela de
    etiquetas (`fala_com_o_windows()`);
  - montador do pacote e formulário → `etiquetas_do_trabalho()` (as mesmas etiquetas nos dois) e `formulario.CAMPOS`
    (os mesmos títulos nos dois).
  Nenhum caminho tem conta própria.

## O que pode falhar e o que o programa faz

- **O git não responde** (não instalado, repositório estragado, commit de partida que não existe): `GitFalhou` com o
  motivo; a linha de comando sai com código 3 ("não deu para conferir"), nunca 0.
- **Sem licença:** não se aplica a licença do Windows (nada aqui pede); arquivo sem licença de leitura vira K00 ("não
  deu para ler"), nunca "passou".
- **Sem internet:** o GitHub não responde na K21: fica "não conferido" (código 3), nunca "passou".
- **Disco cheio:** a gravação da lista ou do pacote falha com `OSError`; a linha de comando sai com código 3 e diz o
  arquivo. Nada é gravado pela metade no repositório do projeto (a lista é escrita de uma vez).
- **A pessoa diz "Não":** não se aplica: nenhuma pergunta do Windows neste passo.
- **Arquivo preso** (outro programa segurando a lista ou o pacote): `OSError`, código 3, com o motivo.
- **Desligar no meio:** a conferência só lê; o commit barrado não acontece (o git só faz o commit se o gancho sair
  com 0). A lista e o pacote são gravados de uma vez; se o computador desligar no meio da gravação, o git mostra o
  arquivo mudado e a gerente vê antes do commit.
- **Sem o Python do projeto no gancho:** o commit é barrado com a mensagem de onde o Python foi procurado.
- **O gancho não existe numa cópia de ramo antigo:** o git não avisa (documentação lida); quem garante é o teste do
  GitHub.
- **Arquivo do programa que não é Python válido** (ou com a marca de UTF-8 no começo): o primeiro vira K00; o segundo
  é lido normalmente (três arquivos de hoje têm a marca).
- **O GitHub não responde ao buscar a versão de teste** (o teste de proteção) ou ao perguntar o último commit (K18):
  `GitFalhou`; o teste falha com o motivo e a linha de comando sai com 3. Nunca "passou".
- **A versão de teste ainda não tem o porteiro** (antes de juntar este passo): o teste de proteção fica parado, com o
  motivo escrito; nada é dado como conferido.
- **Buscar a versão de teste na cópia do PC:** busca normal (sem `--depth`), para não deixar a cópia rasa e cortar a
  história do repositório; no GitHub (cópia rasa), só o último commit.

## O que li da peça de fora e onde

- **git, a pasta dos ganchos (`core.hooksPath`):** https://git-scm.com/docs/git-config (entrada `core.hooksPath`; lida
  na cópia local do git 2.53, `git-config.html`): "A relative path is taken as relative to the directory where the hooks
  are run". E: "You can also disable all hooks entirely by setting core.hooksPath to /dev/null."
- **Onde o gancho roda:** https://git-scm.com/docs/githooks, DESCRIPTION: "Before Git invokes a hook, it changes its
  working directory to either $GIT_DIR in a bare repository or the root of the working tree in a non-bare repository."
  Então `core.hooksPath=ganchos` faz cada cópia usar a pasta `ganchos/` do próprio ramo.
- **A configuração é uma só para todas as cópias:** https://git-scm.com/docs/git-worktree, CONFIGURATION FILE: "By
  default, the repository config file is shared across all worktrees." Ligar uma vez no repositório principal vale
  para todas as cópias (a gerente liga).
- **Gancho que não existe: o git não avisa:** código do git v2.53.0, `hook.c:13` (`find_hook`, linhas 13 a 48, lido
  com `gh api repos/git/git/contents/hook.c?ref=v2.53.0`): sem o arquivo, devolve `NULL` sem mensagem; só avisa quando
  o arquivo existe e não é executável. Provado em `tests/test_conferencias_antes_do_commit.py`.
- **Executável no Windows:** código do git v2.53.0, `run-command.c:132` (`is_executable`): no Windows não há bit de
  executável; vale o `.exe` ou o arquivo que começa com `#!`. A documentação (https://git-scm.com/docs/githooks):
  "Hooks that don't have the executable bit set are ignored." O gancho começa com `#!/bin/sh` e vai ao git com o bit.
- **O gancho antes do commit:** https://git-scm.com/docs/githooks, pre-commit: "It takes no parameters [...] Exiting
  with a non-zero status from this script causes the git commit command to abort before creating a commit." E: "can be
  bypassed with the --no-verify option".
- **Quebra de linha do Windows no gancho:** com `core.autocrlf=true` (a configuração do Git deste PC, lida com
  `git config --show-origin`), o git troca a quebra de linha ao tirar o arquivo para a cópia
  (https://git-scm.com/docs/git-config, entrada `core.autocrlf`), e o gancho sai com as quebras do Windows. Testado de
  verdade em 19/11: o `sh` do Git para Windows 2.53 roda um script assim sem erro; no GitHub, os testes do gancho rodam
  com a cópia que o git tirou (com as quebras do Windows) e passaram.
- **A rodada do GitHub (K21):** lida em 19/11 na rodada 44202459161 (https://github.com/Samuel-Bottini-BR/EditorImpressao/actions/runs/44202459161):
  o commit testado só aparece no registro do passo "Trocar o codigo" (`.github/scripts/trocar_codigo.sh:31`, a linha
  "codigo trocado pelo de <ramo> (<commit>)"); `gh api .../jobs/<id>/logs` recusa ("the response contains terminal
  escape sequences") e `gh run view <id> --log --job <id>` dá o registro.
- **As palavras novas da busca do Windows:** os módulos do PowerShell, lidos na documentação da Microsoft, por exemplo
  https://learn.microsoft.com/powershell/module/scheduledtasks/ (os 19 comandos das tarefas, todos com o nome
  `...-ScheduledTask...`, como `Register-ScheduledTask`, `Unregister-ScheduledTask`, `Get-ScheduledTask`); o `winreg`
  (https://docs.python.org/3/library/winreg.html, o registro do Windows); o `os.startfile`
  (https://docs.python.org/3/library/os.html#os.startfile, que abre pelo ShellExecute); o `ctypes`
  (https://docs.python.org/3/library/ctypes.html, `windll`, `WinDLL`, `oledll`: as bibliotecas do Windows).
- **Ler o código Python:** https://docs.python.org/3/library/tokenize.html (os comentários vêm como `COMMENT`; um `#`
  dentro de texto não é comentário) e https://docs.python.org/3/library/ast.html (a coluna `col_offset` é contada em
  bytes UTF-8: "the UTF-8 byte offset of the first token that generated the node"; por isso a conversão para letras em
  `leitura_do_codigo.py`).

## O que foi feito

O pacote de regras por trabalho, o porteiro (as 24 conferências) com a lista de exceções gerada pelo programa (44
lugares, proposta, esperando o "sim" do Samuel), o programa que confere o formulário da entrega nas três etapas, a
conferência antes do commit (não ligada) e o pacote do passo 1, montado pelo programa.

## Arquivos criados ou alterados

- `regras_dos_agentes/` (novo: 18 arquivos, contados pelo git)
- `tests/test_conferencias_codigo.py` (novo)
- `tests/test_conferencias_excecoes.py` (novo)
- `tests/test_conferencias_mudancas.py` (novo)
- `tests/test_conferencias_formulario.py` (novo)
- `tests/test_conferencias_pacote.py` (novo)
- `tests/test_conferencias_protecao.py` (novo)
- `tests/test_conferencias_antes_do_commit.py` (novo)
- `tests/test_conferencias_juiz.py` (novo)
- `tests/conferencias_excecoes.json` (novo)
- `ganchos/pre-commit` (novo)

## Como cumpri cada uma

- **D-767:** o gancho e as conferências das mudanças são provados com o git de verdade e um Python de verdade, numa
  pasta temporária (`tests/test_conferencias_antes_do_commit.py`, `tests/test_conferencias_mudancas.py`).
- **D-775:** o formulário confere as três etapas e os seis campos de quem quebra
  (`tests/test_conferencias_formulario.py::test_antes_da_prova_a_vista_exige_o_relatorio_de_quem_quebrou`,
  `tests/test_conferencias_formulario.py::test_relatorio_de_quem_quebra_tem_os_seis_campos_e_o_lugar_de_cada_achado`).
- **D-784:** `tests/test_conferencias_pacote.py::test_todo_arquivo_do_git_tem_linha_na_tabela` e o pacote do passo 1
  em `anexos/pacote-passo1.md`, montado pelo programa.
- **D-785:** nada abre janela; os testes novos não usam tela.
- **D-786:** nenhum processamento muda (nenhum arquivo do programa no git diff).
- **D-787:** no PC, um arquivo de teste por vez (ver "Testes"); o conjunto inteiro no GitHub.
- **D-791:** cada conferência acusa o errado e não acusa o certo (`tests/test_conferencias_codigo.py`,
  `tests/test_conferencias_mudancas.py`); a exceção por lugar
  (`tests/test_conferencias_excecoes.py::test_correcao_2_erro_novo_no_mesmo_arquivo_e_barrado`); a lista só diminui
  (`tests/test_conferencias_excecoes.py::test_lugar_consertado_tem_de_sair_da_lista`); a proteção contra o próprio
  agente (`tests/test_conferencias_protecao.py::test_a_lista_so_diminui_e_a_situacao_o_sim_e_o_passo_nao_mudam`).
- **D-792:** `tests/test_conferencias_formulario.py` (cada campo que falta volta; enchimento não vale).
- **D-793:** `tests/test_conferencias_codigo.py::test_k23_acusa_agente_com_ferramenta_de_abrir_agente_ou_da_central`.
- **D-796:** `tests/test_conferencias_mudancas.py::test_k13_barra_o_agente_de_tela_em_core_fora_da_lista_do_pedido` e
  `tests/test_conferencias_formulario.py::test_o_pedido_tem_de_ser_o_do_pacote_da_gerente`.
- **D-797:** nada junta; nenhuma regra nova fala do `master`.
- **D-798:** `tests/test_conferencias_mudancas.py::test_k10_barra_o_rotulo_de_pronto_no_ramo_de_quem_construiu`.
- **D-799:** o passo 0 do plano-v3: as três correções, a lista por lugar, o formulário, o K13 e o K10.
- **D-800:** `tests/test_conferencias_excecoes.py::test_so_os_lugares_que_o_samuel_deixou_para_depois_ficam_depois_da_entrega`.
- **D-801:** a lista gerada continua `"situacao": "proposta"` e `"sim_do_samuel": null` (a gerente liga).
- **D-802:** `tests/test_conferencias_excecoes.py::test_so_os_lugares_que_o_samuel_deixou_para_depois_ficam_depois_da_entrega`
  (nenhum "fora do plano"; os 56 "depois da entrega"),
  `::test_d802_a_tabela_do_programa_poe_cada_lugar_dele_depois_da_entrega_com_a_decisao_certa` e
  `::test_d802_lugar_novo_que_ninguem_classificou_continua_fora_do_plano_a_perguntar`.
- **D-605:** nenhum teste antigo mudou (o próprio porteiro, K11, confere isso nesta entrega).
- **D-637:** ver "Como fica para quem usa e no livro": nada muda para o Kaique nem no PDF.

## Testes

- No PC, um arquivo por vez (`QT_QPA_PLATFORM=offscreen`, pasta temporária fora do projeto):
  `tests/test_conferencias_codigo.py` 77 passaram; `tests/test_conferencias_excecoes.py` 11 passaram e 1 parado de
  propósito (o que barra o repositório espera o "sim"); `tests/test_conferencias_mudancas.py` 21;
  `tests/test_conferencias_formulario.py` 34; `tests/test_conferencias_pacote.py` 20;
  `tests/test_conferencias_protecao.py` 10 passaram e 1 parado (a versão de teste ainda não tem o porteiro);
  `tests/test_conferencias_antes_do_commit.py` 12; `tests/test_conferencias_juiz.py` 9.
- Teste de reversão da quinta volta: os quatro testes novos (S1 duas vezes, S2, S3) falham com o código anterior e
  passam com o de hoje.
- Teste de reversão da quarta volta: os seis testes novos (Q1, Q1 no formato do GitHub, Q2, Q3, Q4, Q6) falham com o
  código anterior e passam com o de hoje.
- Teste de reversão da terceira volta: os 4 testes do R5 e o do `CREATE_NO_WINDOW` guardado numa variável (R6) falham
  com o código anterior (`8a1f56d8`) e passam com o de hoje.
- Prova de verdade do juiz no repositório real: ver "Como ficou cada achado da terceira volta", R2 e R3.
- GitHub, rodada 44487102520 (https://github.com/Samuel-Bottini-BR/EditorImpressao/actions/runs/44487102520; o último
  commit de código, b5927774): passou inteira. 251 arquivos de teste, 4198 passaram, 0 falharam, 148 pulados; os
  botões e os prints da janela real passaram; o juiz escreveu "PORTEIRO: NAO CONFERIDO (a versão de teste
  obra-2026-10-26 ainda não tem o porteiro)", de propósito (Q5).
- Rodada anterior, 44481987404 (commit a664329e, quarta volta): 251 arquivos de teste, 4194 passaram, 0 falharam, 148 pulados (entre
  eles o teste do porteiro que espera o "sim" e o de proteção, que espera a versão de teste ter o porteiro, os dois
  com o motivo escrito); os botões e os prints da janela real também passaram. É a primeira rodada deste ramo com o
  juiz: o trabalho "Porteiro (juiz da versao de teste)" escreveu "PORTEIRO: NAO CONFERIDO (a versão de teste
  obra-2026-10-26 ainda não tem o porteiro)", lido pelo próprio formulário (`ler_rodada`, só no trabalho do juiz). A
  K21 dá "não conferido" por isso, de propósito (Q5).

## Caminho e função

- A lista caminho → função está em "A causa, a regra e todos os caminhos".
- Prova de que o gancho e o GitHub acham o mesmo, pela mesma função:
  `tests/test_conferencias_antes_do_commit.py::test_o_gancho_e_o_github_acham_o_mesmo_no_mesmo_arquivo`.
- Prova de que o montador e o formulário usam o mesmo pedido: `tests/test_conferencias_pacote.py::test_o_pedido_do_pacote_e_lido_de_volta_igual`.

## Máquina ou olho

- Máquina: todas as conferências, a lista, o formulário, o gancho (testes novos).
- Olho: o texto para o Samuel (aberto em PDF e conferido: os números batem com a lista; a lista com marcadores aparece
  certa) e o pacote do passo 1 (lido).

## Ressalvas

- **A lista não vale ainda:** até a gerente ligar a lista direto na versão de teste (depois do "sim" do Samuel
  registrado no Livro), o juiz da rodada diz "NAO CONFERIDO" para o código, e o teste do próprio ramo que barra o
  repositório fica parado com o motivo. O juiz já barra item novo e mudança da lista desde a junção deste passo.
- **O juiz está na rodada desde o `c41e4309`** (aplicado pela gerente), mas diz "NAO CONFERIDO" até a lista ser
  ligada na versão de teste; a K21 de toda entrega dá "não conferido" (código 3) até lá, de propósito. A marca só é
  lida no trabalho de nome "Porteiro (juiz da versao de teste)": se esse nome mudar no workflow sem mudar o
  `TRABALHO_DO_JUIZ`, a K21 fica pendente (nunca passa). Os testes do próprio ramo (`tests/test_conferencias_protecao.py` e o
  teste que barra o repositório) continuam como aviso cedo, mas rodam o código do ramo: quem garante é o juiz.
- **A conta deu 176** (primeira entrega 44, primeira volta 125, segunda 189; o plano tinha contado 43): 107 no plano
  (passo 2: 1, 3: 38, 4: 50, 5: 18) e 69 depois da entrega: 13 da D-800 (a régua dos filtros 2, a leitura da placa de
  vídeo e do disco 9, as dicas do Automático 2) e 56 da D-802 (o resto do teste de velocidade 43, o brasão 5, o motor
  de achar texto 4, a tela de início 2, a memória livre 1, o pacote do teste de velocidade 1). Nenhum fora do plano.
- **A página para o Samuel ainda traz a pergunta da lista ("sim, a lista entra assim...")**, que ele já respondeu
  (D-801, "ok"). Não mexi: o pedido foi tirar só a pergunta dos 56. Se a página for mostrada de novo, a gerente decide
  se essa pergunta vira frase do que ele decidiu (o teste do texto cobra hoje "O que você escolhe" e "Sugestão").
- **O Livro deste ramo não tem a D-801 nem a D-802** (estão na versão de teste, `obra-2026-10-26`, commits
  `c5838a1f` e `8a34960c`); eu não juntei a versão de teste neste ramo. O código e os testes citam as duas.
- **O juiz confia no código da versão de teste.** Se a própria versão de teste tiver um porteiro afrouxado, o juiz
  também estará; isso só a gerente evita, juntando com a conferência das mudanças (K17) e com quem tenta quebrar.
- **O apelido do ctypes não é seguido** quando vai para outro arquivo (importado), nem quando passa por um dicionário
  ou um atributo (`self.k = ...`). Quem recebe o que uma função devolve recebe todos os nomes como apelido, por cautela
  (ex.: `kernel32, entrada = ...`: as linhas que usam `entrada` também entram).
- **O "sim" agora precisa de internet** onde é conferido (o gancho, o teste do GitHub, o formulário): sem o GitHub,
  "não deu para conferir". E a gerente precisa registrar o "sim" como decisão no Livro da versão de teste antes de
  ligar a lista.
- **O rótulo de pronto continua sendo o que está escrito:** a K10 aceita o rótulo no relatório de quem quebrou quando
  os commits daquela pasta são só dela e o relatório diz o papel; um agente que imite isso de propósito passaria. A
  gerente confere com o pacote que deu a quem quebrou. Entre aspas ou crases o rótulo não conta (é como se cita a
  regra).
- **O teste de proteção busca a versão de teste no GitHub:** precisa de internet (no PC e no GitHub); e um ramo feito
  de uma versão de teste antiga, depois que a lista diminuiu lá, vê os itens que já saíram como "item novo": precisa
  juntar a versão de teste antes da entrega.
- **As pastas que não são programa (Q2)** ficam numa lista só, protegida. Se alguém criar código do programa dentro
  de uma delas (ex.: um `.py` em `docs/` importado pelo `main.py`), o porteiro não lê; a lista é curta de propósito.
- **Importar direto uma pasta de fora (S1, o vizinho que fica):** o programa que escrever `import docs.segredo` carrega
  `docs/segredo.py`, mesmo sem `__init__.py`, e o porteiro não lê `docs/`. Hoje nenhum arquivo do programa importa
  uma dessas pastas, a não ser `tests` (por três scripts da raiz que não vão para o Kaique). Acusar esse import seria
  uma conferência nova; está em "Ideias".
- **As funções que não se mexem (Q3)** são só aviso no pacote: se o agente renomear uma delas mesmo assim, o ramo barra
  (o lugar vira erro novo), e é aí que ele descobre; o pacote só evita a surpresa.
- **O que o porteiro não pega:** texto montado em pedaços (ex.: `"power" + "shell"`), uma segunda peça com outro nome,
  importação por texto (`importlib`). A K10 só lê documentos (não `.py`) e conta o rótulo em maiúsculas ou como linha
  de situação; o rótulo escrito de outro jeito no meio da frase passa.
- **K21 lê o registro da rodada:** depende da frase do `trocar_codigo.sh`; se a frase mudar, a K21 dá "não conferido"
  (nunca "passou").
- **K09 olha a pasta da cópia**, porque o `.pdf` fica fora do git; no GitHub ela não roda.
- **O gancho só foi provado no Windows** (com o `sh` do Git para Windows); fora do Windows, a quebra de linha do
  Windows quebraria o script.
- **As linhas das janelas de prova na tabela** pegam qualquer nome com "janela_de_prova" ou "servidor_das_versoes": se
  o agente do passo 1 escolher outro nome, o pacote avisa "fora da tabela" e manda todas as regras (o lado seguro).
- **O pacote do passo 1 foi montado com o commit de partida `746dbda6`:** a gerente remonta com o commit da versão de
  teste depois de juntar este passo (o comando está no anexo).
- Nenhum teste antigo foi rodado no PC (só os novos): o conjunto inteiro roda no GitHub.

## Ideias e bugs

- **Ideia (Lista de espera):** a K06 poderia pegar também a importação por texto (`importlib.import_module("ui...")`),
  que hoje fica de fora.
- **Ideia (Lista de espera):** o porteiro acusar o arquivo do programa que importa uma pasta de fora do programa
  (`import docs.x`, `from memoria import y`), o vizinho do S1 que ainda passa.
- **Ideia (Lista de espera):** o montador sugerir as decisões do pedido pelos arquivos (o Livro diz "onde toca"), como
  a proposta das regras já previa.
- **Bug para a Lista de bugs (19/11/2026):** três arquivos do repositório começam com a marca de UTF-8 (BOM):
  `relatorios/mover-lado/piloto_roda.py`, `tests/test_decisoes_ferramentas_antes_depois.py`,
  `tests/test_decisoes_tira_marca_a_tela.py`. Não quebra nada (o Python aceita), mas é diferente do resto; achado pelo
  porteiro.

## Perguntas para o Samuel

- Nenhuma em aberto. As duas deste passo foram respondidas em 19/11: a da lista ("ok": ela entra como está e a
  conferência passa a barrar; a gerente liga na versão de teste) e a dos 56 pedaços que conversam com o Windows por
  conta própria ("ok, continuamos assim e vamos proceguir": ficam para depois da entrega ao Kaique, como os outros que
  ele já tinha deixado para depois). Os textos das duas perguntas, como foram, estão no histórico do git deste arquivo
  (commit `69b3937c`).

## Commit

Último commit de código do trabalho: 7858d11f (D-802; depois dele, só este ONDE-PAREI mudou). A rodada do GitHub para ele fica com a gerente (pedido de 19/11: "Não rode a suíte inteira: a gerente roda").

## Perguntas do Windows que o Samuel vê

0 (nada deste passo mexe no Windows).

## A prova de verdade

Não se aplica: nada deste passo mexe no Windows (o plano diz "Prova à vista: não há"); a prova de verdade do gancho é
o git de verdade nos testes, numa pasta temporária.
