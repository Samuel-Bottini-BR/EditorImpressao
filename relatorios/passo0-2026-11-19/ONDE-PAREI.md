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

- Primeira entrega: o pacote, o porteiro (24 conferências), a lista (44 lugares), o formulário, o gancho (não ligado),
  o pacote do passo 1 e o texto para o Samuel.
- Quem tentou quebrar devolveu com 19 achados (`quem-quebrou/relatorio.md`, NÃO ESTÁ PRONTO). Esta é a volta: todos
  os achados que a gerente mandou consertar estão consertados, cada um com prova em `tests/` (ver "Como ficou cada
  achado"). A lista foi refeita com a busca ampliada: 125 lugares em 118 itens (eram 44 em 42).
- Rodada de prova com a lista "valendo" (ramo `passo0-prova-valendo`, que eu criei): passou, e o ramo foi apagado.
  Rodada final do ramo de trabalho: passou. O formulário, conferido com o pacote e com o GitHub, passa na etapa "antes de
  ir ao agente que tenta quebrar". Entregue à gerente.

## Como ficou cada achado de quem tentou quebrar

1. **Ligar a lista deixava um teste vermelho.** O teste monta a lista com dados próprios e vale nos dois estados
   (`tests/test_conferencias_excecoes.py::test_a_lista_valendo_sem_o_sim_do_samuel_conferido_no_livro_nao_vale`). E uma
   rodada inteira do GitHub num ramo de prova, com a lista "valendo" e um "sim" de mentira, roda o teste que barra o
   repositório (ver "Testes").
2. **A busca do Windows conhecia poucas palavras.** Ampliada (`PALAVRAS_DO_WINDOWS`, 23 linhas: o PowerShell com
   qualquer nome, as tarefas por qualquer meio, o ShellExecute por qualquer nome, o cmd, o registro, a licença e o
   dono de arquivo, os instaladores, o firewall, os serviços, as contas, os recursos do Windows, o WMI e o COM, o
   pywin32, o ctypes, o número do DETACHED_PROCESS). Provas: os 18 jeitos de
   `tests/test_conferencias_codigo.py::test_k01_acusa_os_outros_nomes_da_mesma_conversa_com_o_windows` e o que não
   deve ser acusado. **Eram 44 lugares; ficaram 125.** Dos 81 novos: 75 estão nos arquivos que o plano conserta e
   ganharam o passo certo (o desfazer e a tarefa dele no passo 5, o resto pelo arquivo); 1 é a régua dos filtros (a
   linha que prepara a mesma pergunta, no mesmo pedaço que o Samuel deixou para depois); 22 ficam "fora do plano, a
   perguntar ao Samuel" (o teste de velocidade 16, a tela de início 2, a memória livre 1, o motor de achar texto 1, o
   brasão 1, o pacote do teste de velocidade 1). Escolha técnica: no ctypes, conta só a linha onde a biblioteca do
   Windows é pega, não cada chamada feita depois pela mesma variável (senão o mesmo pedaço viraria dezenas de linhas).
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
12. **Arquivo novo sem as regras do Windows.** Para arquivo que ainda não existe, o texto do pedido (o título do pacote)
    que fala do Windows dá a etiqueta
    (`tests/test_conferencias_pacote.py::test_arquivo_novo_ganha_as_regras_do_windows_pelo_texto_do_pedido`).
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

- `regras_dos_agentes/` (novo: 17 arquivos, contados pelo git)
- `tests/test_conferencias_codigo.py` (novo)
- `tests/test_conferencias_excecoes.py` (novo)
- `tests/test_conferencias_mudancas.py` (novo)
- `tests/test_conferencias_formulario.py` (novo)
- `tests/test_conferencias_pacote.py` (novo)
- `tests/test_conferencias_protecao.py` (novo)
- `tests/test_conferencias_antes_do_commit.py` (novo)
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
- **D-605:** nenhum teste antigo mudou (o próprio porteiro, K11, confere isso nesta entrega).
- **D-637:** ver "Como fica para quem usa e no livro": nada muda para o Kaique nem no PDF.

## Testes

- No PC, um arquivo por vez (`QT_QPA_PLATFORM=offscreen`, pasta temporária fora do projeto):
  `tests/test_conferencias_codigo.py` 43 passaram; `tests/test_conferencias_excecoes.py` 11 passaram e 1 parado de
  propósito (o que barra o repositório espera o "sim"); `tests/test_conferencias_mudancas.py` 20;
  `tests/test_conferencias_formulario.py` 28; `tests/test_conferencias_pacote.py` 13;
  `tests/test_conferencias_protecao.py` 7 passaram e 1 parado (a versão de teste ainda não tem o porteiro);
  `tests/test_conferencias_antes_do_commit.py` 9.
- Mutação da primeira volta (desfazer cada correção do esboço numa cópia e ver o teste dela falhar): correção 1, 2
  testes falham; correção 2, 1 falha; correção 3, 1 falha.
- GitHub, rodada de prova 44461329846 (ramo `passo0-prova-valendo`, a lista em "valendo" com um "sim" de mentira):
  passou inteira (4136 passaram, 0 falharam). O teste que barra o repositório
  rodou de verdade (não aparece entre os parados) e passou: com a lista valendo, o código de hoje só tem o que a lista
  deixa. O ramo de prova foi apagado depois (no GitHub e na cópia; só tinha o commit da prova).
- GitHub, rodada 44461501923 (o último commit de código, 76fed2ee): passou inteira. 250 arquivos de teste, 4135 passaram, 0 falharam,
  148 pulados (entre eles o teste do porteiro que espera o "sim" do Samuel e o de proteção, que espera a versão de
  teste ter o porteiro, os dois com o motivo escrito); os botões e os prints da janela real também passaram.

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

- **A lista não vale ainda:** o teste que barra o repositório fica parado até a gerente trocar a situação para
  "valendo" com o "sim" do Samuel, que agora tem de estar no Livro (`sim_do_samuel`: a decisão, a data e as palavras,
  conferidas na linha da decisão). A gerente registra o "sim" no Livro primeiro. Até lá, nenhuma conferência do código parado barra no GitHub (nem as que hoje dão
  zero, como a do emoji): escolhi deixar o porteiro inteiro desligado, como o plano diz ("depende dele antes de ligar o
  porteiro").
- **A conta deu 125** (na primeira volta, 44; o plano tinha contado 43): a busca ampliada pegou 81 lugares a mais (ver o
  achado 2 acima). A régua dos filtros, que o Samuel deixou para depois, passa a contar 2 linhas no mesmo pedaço (o
  texto para ele explica).
- **O rótulo de pronto continua sendo o que está escrito:** a K10 aceita o rótulo no relatório de quem quebrou quando
  os commits daquela pasta são só dela e o relatório diz o papel; um agente que imite isso de propósito passaria. A
  gerente confere com o pacote que deu a quem quebrou. Entre aspas ou crases o rótulo não conta (é como se cita a
  regra).
- **O teste de proteção busca a versão de teste no GitHub:** precisa de internet (no PC e no GitHub); e um ramo feito
  de uma versão de teste antiga, depois que a lista diminuiu lá, vê os itens que já saíram como "item novo": precisa
  juntar a versão de teste antes da entrega.
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
- **Ideia (Lista de espera):** o montador sugerir as decisões do pedido pelos arquivos (o Livro diz "onde toca"), como
  a proposta das regras já previa.
- **Bug para a Lista de bugs (19/11/2026):** três arquivos do repositório começam com a marca de UTF-8 (BOM):
  `relatorios/mover-lado/piloto_roda.py`, `tests/test_decisoes_ferramentas_antes_depois.py`,
  `tests/test_decisoes_tira_marca_a_tela.py`. Não quebra nada (o Python aceita), mas é diferente do resto; achado pelo
  porteiro.

## Perguntas para o Samuel

### A lista do que já está errado no código (para dizer sim)

**O que é e onde fica:** é a conferência automática que barra o trabalho de um agente quando o código tem um erro que
já conhecemos. Ela roda nos testes do GitHub, em toda entrega; você não vê nada dela no programa.

**O que acontece hoje:** ela leu o programa e achou 125 lugares com esses erros, que ficam numa lista; ela barra o
trabalho que acrescentar mais um lugar com um desses erros, escrito com as palavras que ela conhece. A lista só diminui:
o plano da parte do Windows tira 97 deles. Os 5 que você deixou para depois da entrega ficam na lista até lá.

![A lista, como vai para você](lista-de-excecoes-para-o-samuel.png)

**O que você escolhe:** sim, a lista entra assim e a conferência passa a barrar; ou não, e diga o que mudar. Sugestão:
sim. Nada do programa muda com isso, e nada do que já funciona muda.

**De onde veio:** do seu "sim" de 19/11 à lista que só diminui; a conta saiu do próprio programa que confere.

### Os pedaços novos que conversam com o Windows por conta própria

**O que é e onde fica:** procurando com mais palavras, a mesma conferência achou outros pedaços do programa que falam
com o Windows por conta própria e que o plano da parte do Windows não conserta. Por exemplo: a tela de início abre a
pasta do projeto e manda imprimir pelo Windows; o teste de velocidade lê a memória e a placa de vídeo direto no Windows.
São 22 lugares.

![O texto, como vai para você](lista-de-excecoes-para-o-samuel.png)

**O que você escolhe:** ficam para depois da entrega ao Kaique, como os outros 5 (ficam na lista até lá); ou entram no
plano (cada um vira conserto antes da entrega). Sugestão: depois da entrega, como você decidiu para os outros 5. Nada do
programa muda com nenhuma das duas escolhas agora.

**De onde veio:** da busca maior pedida depois da conferência de quem tentou quebrar a conferência automática.

## Commit

Último commit de código do trabalho: 76fed2ee (depois dele, só este ONDE-PAREI mudou).

## Perguntas do Windows que o Samuel vê

0 (nada deste passo mexe no Windows).

## A prova de verdade

Não se aplica: nada deste passo mexe no Windows (o plano diz "Prova à vista: não há"); a prova de verdade do gancho é
o git de verdade nos testes, numa pasta temporária.
