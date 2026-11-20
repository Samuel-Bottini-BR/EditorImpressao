# Regras novas do catálogo dos erros (D-809 a D-814) — ONDE-PAREI

Implementador. Ramo `regras-catalogo-2026-11-19`, worktree `.claude/worktrees/regras-catalogo`. Pacote:
`relatorios/regras-catalogo-2026-11-19/anexos/pacote.md`.

## Pedido

- Papel: implementador
- Commit de partida: 0fe54cb3
- Ramo: regras-catalogo-2026-11-19

## Arquivos que vou mexer

- `regras_dos_agentes/catalogo.py`
- `regras_dos_agentes/porteiro.py`
- `regras_dos_agentes/formulario.py`
- `regras_dos_agentes/montar_pacote.py`
- `regras_dos_agentes/leitura_do_codigo.py`
- `regras_dos_agentes/protecao.py`
- `relatorios/passo0-2026-11-19/anexos/juiz-no-workflow/porteiro_juiz.sh`
- `tests/test_conferencias_codigo.py`
- `tests/test_conferencias_formulario.py`
- `tests/test_conferencias_pacote.py`
- `tests/test_conferencias_protecao.py`
- `relatorios/regras-catalogo-2026-11-19/`

## Onde parei

- 19/11: li o pedido, o CLAUDE.md, a memória, o catálogo dos erros, o Livro (D-791 a D-814) e o código do pacote.
- 19/11 (noite): as seis decisões feitas, com teste; os testes do porteiro rodados no PC, um arquivo por vez; duas
  rodadas do GitHub disparadas. A K25 achou dois lugares no código de hoje; não entraram na lista de exceções.
- 20/11 (gerente): os dois vão ser consertados. O do juiz, consertado aqui; o do `core/windows.py`, pelo passo 2. As
  listas da K25 protegidas; os dois jeitos de tirar atalho aceitos; pacote novo copiado (commit `e075c467`).
- 20/11 (madrugada): quem quebrou devolveu (`quem-quebrou/relatorio-1.md`). Feitos os achados 1, 4, 6, 7, 10, 11 e
  13, pela decisão da gerente; os outros na Lista de espera. Rodada nova do GitHub disparada.

## Decisões que esta tarefa precisa cumprir

- **D-791** (18/11/2026): "não sei do que você está falando" · "b". Aqui: a K25 barra desde o primeiro dia; a prova é
  "acusa o exemplo errado e não acusa o certo"; o que ela achar no código de hoje NÃO entra na lista de exceções.
- **D-792** (18/11/2026): "mas e o que vai determinar o que vai nesse formulario? vai ser feito um toda vez que for enviado um trabalho para um agente?" · "ok". Aqui: as perguntas novas entram no formulário único, pela etiqueta do trabalho, e o programa confere.
- **D-798** (19/11/2026): "fechou". Aqui: não escrevo o rótulo de pronto para conferir.
- **D-803** (19/11/2026): "pera ai, quando acontece esses erros, eles são catalogados para virarem regras depois?" · "ok". Aqui: as regras saem do catálogo, só com o "sim" dele (D-809 a D-814).
- **D-804** (19/11/2026): "como vai ser organizado esse catologo de erros?" · "ok". Aqui: as famílias F9, F4, F3+F5, F1, F2 e F6 do catálogo.
- **D-808** (19/11/2026): "1- pode". Aqui: o que ele aprovou nas seis perguntas é feito junto, por um agente (este).
- **D-809** (19/11/2026): "ok, mas essas coisas foram recuperadas? e porque ele fez essa confusão se era regra ele não mexer? e tinha o porteiro para ele não fazer isso" · "ok". Aqui: regra nova no catálogo (git e arquivos) e a conferência K25 do porteiro.
- **D-810** (19/11/2026): a gerente: "Proposta: os agentes que escrevem testes recebem uma lista curta dessas diferenças entre o seu PC, o GitHub e o PC do Kaique, para já escrever o teste certo de primeira. Fica assim?" Ele: "ok". Aqui: regra nova (Windows e testes), só regra.
- **D-811** (19/11/2026): a gerente: "Proposta: na ficha de entrega, quem escreve passa a mostrar, para cada proteção, o teste que falha quando ela é desligada." Ele: "ok". Aqui: pergunta nova no formulário (Windows e instalador); o programa confere que a lista existe e que cada teste citado existe.
- **D-812** (19/11/2026): a gerente: "É como deixar o aluno corrigir a própria prova. Proposta: toda conferência diz de onde vem cada informação que usa. Informação que o conferido pode trocar não vale como prova." Ele: "ok". Aqui: regra nova e pergunta nova no formulário.
- **D-813** (19/11/2026): a gerente: "Proposta: acrescentar à sua regra de 'ler antes de usar peça de fora' que, quando o programa recusa ou procura alguma coisa, o agente lista antes todos os jeitos que o Windows ou o Python aceitam para ela." Ele: "ok". Aqui: o acréscimo vai no catálogo, na regra 6 (e no "sempre" que a cobre); o CLAUDE.md fica com a gerente.
- **D-814** (19/11/2026): a gerente: "Proposta: antes de mandar qualquer pergunta para você, o agente anota em quais decisões suas procurou e por que essa ainda não está respondida." Ele: "ok". Aqui: pergunta nova no formulário, para entrega com perguntas ao Samuel.

## O que já está escolhido e testado aqui

- O porteiro tem 24 conferências com a numeração da tabela da proposta:
  `tests/test_conferencias_codigo.py::test_as_24_conferencias_tem_a_numeracao_da_tabela_da_proposta`.
- Cada conferência acusa o errado e não acusa o certo (D-791): os testes de `tests/test_conferencias_codigo.py`.
- A lista de exceções só diminui e nada entra por ramo de agente:
  `tests/test_conferencias_excecoes.py::test_o_repositorio_so_tem_os_erros_que_a_lista_deixa` (a lista está "valendo").
- O formulário certo de um trabalho só de testes passa:
  `tests/test_conferencias_formulario.py::test_o_formulario_certo_passa_e_o_github_nao_consultado_fica_pendente`.
- O trabalho do Windows cobra as falhas e as perguntas do Windows:
  `tests/test_conferencias_formulario.py::test_trabalho_do_windows_cobra_as_falhas_e_as_perguntas_do_windows`.
- O catálogo é coerente e o "sempre" tem no máximo 10: `tests/test_conferencias_pacote.py::test_o_catalogo_e_coerente`.
- O pacote do passo 1 traz as regras e o formulário do Windows:
  `tests/test_conferencias_pacote.py::test_o_pacote_do_passo_1_traz_as_regras_do_windows_e_o_formulario_do_windows`.

## Como fica para quem usa e no livro

Nada muda para o Kaique nem no PDF: este trabalho só mexe nas regras dos agentes, no porteiro e no formulário da
entrega. Antes e depois, o programa abre, trata as páginas e monta o mesmo PDF; nenhuma tela muda.

O que muda é para os agentes e para a gerente:
- antes: um script de agente podia rodar `git fetch --depth=1` ou `rm -rf` numa pasta com atalho, e nada acusava;
  depois: o porteiro acusa (a K25), no GitHub e antes do commit;
- antes: o pacote não trazia a regra do .git dividido, a lista dos três computadores nem "de onde vem cada dado";
  depois: traz, e o "sempre" n.º 5 traz o acréscimo da D-813;
- antes: o formulário não perguntava pelas proteções e seus testes, pela fonte dos dados nem pelas decisões procuradas
  antes de cada pergunta ao Samuel; depois: pergunta, conforme o tipo de trabalho.

## A causa, a regra e todos os caminhos

- **Por que os erros aconteceram (o catálogo):** F9, nenhuma regra dizia que a cópia do agente divide o `.git` com o PC
  e nenhuma conferência olhava esses comandos; F4, nenhuma regra dizia como os computadores dos testes são
  diferentes; F3+F5, nada pedia, para código novo, o teste que acusa cada proteção; F1, nada pedia de onde vem o dado
  da conferência; F2, a regra 6 não pedia "tudo o que a peça aceita"; F6, nada pedia as decisões procuradas.
- **As regras, cada uma num lugar só:**
  - o que é comando perigoso: `PALAVRAS_DO_GIT`, `PALAVRAS_DE_APAGAR` e `CONFERE_SE_E_ATALHO`, decididos por
    `_o_que_o_comando_muda()` (`regras_dos_agentes/porteiro.py`);
  - o que é um comando no Python: `comandos()` (`regras_dos_agentes/leitura_do_codigo.py`);
  - que campos do formulário valem para um trabalho: `vale_para()` (`regras_dos_agentes/formulario.py`);
  - o texto das regras: `catalogo.REGRAS` e `catalogo.SEMPRE` (o acréscimo da D-813 escrito uma vez, `ACRESCIMO_D813`).
- **Todos os caminhos (achados com grep por `conferir_codigo`, `_DO_CODIGO_PYTHON`, `CAMPOS`, `formulario_em_branco`):**
  - a rodada do GitHub, o repositório inteiro: `achados_do_repositorio` → `conferir_codigo()` → `k25()` ou
    `k25_terminal()` → `_o_que_o_comando_muda()`;
  - antes do commit (`ganchos/pre-commit`): `achados_do_proximo_commit` → `conferir_codigo()` → o mesmo;
  - o juiz da versão de teste: `conferir_codigo()` da versão de teste (só depois de a gerente juntar);
  - o formulário: `_conferir_campos()` → `vale_para()`; o pacote em branco: `formulario_em_branco()` → `vale_para()`
    (antes, cada um tinha a sua conta `quem != "*" and quem not in tags`: era a mesma conta copiada em dois lugares);
  - as regras do pacote: `escolher_regras()` (não mudou).

## O que pode falhar e o que o programa faz

Este trabalho não pede nada ao Windows; as falhas são as do porteiro e do formulário:
- sem internet: o formulário busca o Livro da versão de teste no GitHub (`Livro.da_versao_de_teste`); sem internet, a
  peça do git levanta `GitFalhou` e a conferência diz que não conferiu (nunca "passou"). A K25 não usa a internet.
- sem licença para ler um arquivo, ou disco cheio: arquivo do projeto que não dá para ler vira K00 ("não deu para ler"),
  nunca "passou"; o arquivo sem extensão que não dá para ler é pulado (só o "#!" diria que é script).
- a pessoa diz "Não": não se aplica, nada aqui pergunta à pessoa.
- arquivo preso por outro programa: a leitura falha e vira K00, como acima.
- desligar no meio: a K25 e o formulário só leem; nada fica pela metade (não gravam nada).

## Cada proteção e o teste que falha sem ela

Cada uma foi desligada na memória e o arquivo de teste rodou de novo (script e resultado:
`relatorios/regras-catalogo-2026-11-19/anexos/mutacoes.py` e `anexos/mutacoes-resultado.txt`, 12 de 12 acusadas):
- M1, a lista do git que muda o `.git` → `tests/test_conferencias_codigo.py::test_k25_acusa_o_git_que_muda_a_pasta_git_inteira_num_script`.
- M2, conferir o atalho antes de apagar → `tests/test_conferencias_codigo.py::test_k25_nao_acusa_quem_confere_o_atalho_antes_nem_o_que_nao_entra_nele`.
- M3, a exceção só para as duas peças do git → `tests/test_conferencias_codigo.py::test_k25_vale_nos_testes_e_nao_vale_nas_duas_pecas_do_git` (na primeira volta NÃO falhava: o teste lia a lista do próprio porteiro; consertado).
- M4, ler o comando pela estrutura e não o texto solto → `tests/test_conferencias_codigo.py::test_k25_nao_acusa_o_git_que_so_le_nem_o_texto_solto`.
- M5, tirar o comentário do terminal → `tests/test_conferencias_codigo.py::test_k25_le_o_gancho_sem_extensao_e_pula_o_comentario`.
- M6, o teste de cada proteção (F21) → `tests/test_conferencias_formulario.py::test_d811_trabalho_do_windows_sem_as_protecoes_e_os_testes_volta`.
- M7, a pergunta de onde vem cada dado (F22) → `tests/test_conferencias_formulario.py::test_d812_trabalho_que_confere_tem_de_dizer_de_onde_vem_cada_dado`.
- M8, as decisões procuradas (F23) → `tests/test_conferencias_formulario.py::test_d814_pergunta_ao_samuel_sem_as_decisoes_procuradas_volta`.
- M9, as perguntas novas só nos trabalhos certos → `tests/test_conferencias_formulario.py::test_as_perguntas_novas_nao_valem_para_o_trabalho_so_de_testes`.
- M10, a decisão citada no F23 tem de existir no Livro → `tests/test_conferencias_formulario.py::test_d814_pergunta_ao_samuel_sem_as_decisoes_procuradas_volta`.
- M11, o pacote e o formulário escolhem os campos pela mesma função → `tests/test_conferencias_pacote.py::test_os_campos_em_branco_do_pacote_sao_os_que_o_formulario_cobra`.
- M12, o acréscimo da D-813 no "sempre" → `tests/test_conferencias_pacote.py::test_d813_o_acrescimo_a_regra_6_e_o_texto_do_livro_e_vai_em_todo_pacote`.
- O `git config` que só lê não é acusado (feito depois das mutações) → `tests/test_conferencias_codigo.py::test_k25_git_config_so_acusa_o_que_grava`.
- As listas da K25 na proteção do GitHub (20/11): tirar linha → `tests/test_conferencias_protecao.py::test_k25_tirar_linha_das_listas_e_acusado`; crescer a exceção ou o "conferiu o atalho" → `tests/test_conferencias_protecao.py::test_k25_crescer_a_excecao_ou_o_que_conta_como_conferir_e_acusado`; afrouxar pelo uso → `tests/test_conferencias_protecao.py::test_k25_afrouxar_pelo_uso_e_acusado`.
- Os dois jeitos certos de tirar atalho não são acusados → `tests/test_conferencias_codigo.py::test_k25_os_dois_jeitos_certos_de_tirar_o_atalho_nao_sao_acusados`.
- O `git rm` não lido como o `rm` do terminal, o `git clean` e o "só no GitHub" na mesma linha → `tests/test_conferencias_codigo.py::test_k25_o_rm_do_git_nao_e_o_rm_do_terminal`, `tests/test_conferencias_codigo.py::test_k25_acusa_o_git_clean_e_nao_o_que_so_lista` e `tests/test_conferencias_codigo.py::test_k25_o_comando_do_git_so_no_github_na_mesma_linha_passa`.
- Os scripts da rodada consertados → `tests/test_conferencias_codigo.py::test_k25_os_scripts_do_workflow_consertados_passam_e_os_de_antes_nao`.
- Cada jeito de ler o comando na proteção → `tests/test_conferencias_protecao.py::test_k25_desligar_um_jeito_de_ler_o_comando_e_acusado` e `tests/test_conferencias_protecao.py::test_k25_tirar_exemplo_de_um_jeito_e_acusado`.
- Só conta como teste um `def test_...` do código → `tests/test_conferencias_formulario.py::test_achado_6_so_conta_como_teste_um_def_test_do_codigo`.
- "Nenhuma" com pergunta embaixo → `tests/test_conferencias_formulario.py::test_achado_7_nenhuma_com_pergunta_embaixo_nao_desliga_a_conferencia`.
- A R157 no trabalho do Windows sem teste → `tests/test_conferencias_pacote.py::test_d810_a_regra_dos_tres_computadores_vai_tambem_ao_trabalho_do_windows_sem_teste`.

## De onde vem cada dado que a conferência usa

- K25: o código dos arquivos do ramo (é o que se confere, não uma prova); as listas de comandos e o que conta como
  "conferir o atalho" vêm do `porteiro.py`. No GitHub, quem julga é o porteiro da versão de teste (o juiz), não o do
  ramo; mas as listas novas da K25 ainda não estão na proteção (`protecao.PROTEGIDOS`, arquivo da gerente): até lá, um
  ramo poderia afrouxá-las sem o teste de proteção acusar (ressalva 3).
- F21: os testes citados são procurados no git do ramo (existem?); se eles falham mesmo sem a proteção, só quem tenta
  quebrar confere (o agente escreve a lista).
- F22: texto do agente; só se confere que existe.
- F23: as decisões citadas são procuradas no Livro da versão de teste (`Livro.da_versao_de_teste`, que só a gerente
  escreve), nunca no do ramo.
- Quais campos valem: as etiquetas saem da lista de arquivos do pacote da gerente (o formulário compara o pedido do
  ONDE-PAREI com o do pacote), pela tabela; nunca do que o agente escreve no ONDE-PAREI.

## O que li da peça de fora e onde

- O `shutil.rmtree` do Python 3.14 (instalado): recusa atalho de pasta e não entra nele —
  `C:/Users/fotog/AppData/Local/Python/pythoncore-3.14-64/Lib/shutil.py:660` (`_rmtree_islink`, junção = link),
  `shutil.py:680` ("Cannot call rmtree on a symbolic link"), e dentro da pasta o atalho conta como arquivo,
  `Lib/os.py:381` (`not entry.is_junction()`). Lido. Por isso a K25 não acusa `shutil.rmtree`.
- O `Remove-Item` do PowerShell 5.1: os apelidos `del`, `erase`, `rd`, `ri`, `rm`, `rmdir` e o `-Recurse` —
  https://learn.microsoft.com/powershell/module/microsoft.powershell.management/remove-item?view=powershell-5.1 (lido).
  A página não fala de atalho de pasta. Que o PowerShell aceita `-Rec` e `-r` no lugar de `-Recurse`: a página
  https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_parameters não diz; provado aqui
  com `Remove-Item -LiteralPath <pasta de rascunho> -Rec -WhatIf` e `-r -WhatIf` (PowerShell 5.1.26100; nada apagado).
- O `git config`: o que grava e o que só lê, e que sem `--worktree` grava no `.git/config` que todas as cópias dividem —
  https://git-scm.com/docs/git-config (lido).
- O `git fetch` (`--depth`, `--deepen`, `--shallow-since`, `--shallow-exclude`, `--prune`), `git gc`, `git prune`,
  `git worktree prune`, `git remote prune`, `git stash` (list e show só leem), e as opções gerais do git antes do
  subcomando (`-C`, `-c`, `--git-dir`...) — https://git-scm.com/docs/git-fetch, https://git-scm.com/docs/git
  (conhecimento meu, não relido nesta tarefa: deduzido, ressalva 6).
- O `rm` do Git Bash (`-r`, `-R`, `--recursive`, letras juntas) —
  https://www.gnu.org/software/coreutils/manual/html_node/rm-invocation.html (conhecimento meu, não relido: deduzido).

## O que foi feito

- **D-809:** regra nova R156 no catálogo (etiqueta git, vai a todo trabalho) e a conferência K25 do porteiro: comando que
  muda a pasta `.git` inteira (fetch/pull com `--depth` e parentes, `--prune`, gc, prune, stash, config que grava) ou
  `rm -r`/`Remove-Item -Recurse` sem conferir antes se é atalho, nos arquivos Python e nos de terminal (`.sh`, `.ps1`,
  `.bat`, o gancho com "#!"), fora das duas peças do git. Lê o comando pela estrutura do código, nunca o texto solto.
  Os dois jeitos certos de tirar atalho, `cmd /c rmdir <atalho>` e `(Get-Item <atalho>).Delete()`, não são acusados
  (a R156 diz os dois). As listas da K25 estão em `protecao.PROTEGIDOS`.
  A K25 achou 2 lugares no código de hoje. Pela decisão da gerente (20/11), os dois vão ser consertados, nenhum vai
  para a lista: o do juiz, consertado aqui (seção "O script do juiz consertado"); o do `core/windows.py`, pelo agente
  do passo 2.
- **D-810:** regra nova R157 (os três computadores), etiqueta testes.
- **D-811:** pergunta nova F21 no formulário (trabalho do Windows): a lista das proteções, cada uma com o teste
  (`arquivo::função`) que existe.
- **D-812:** regra nova R158 e pergunta nova F22 (trabalho do Windows e do porteiro).
- **D-813:** o acréscimo à regra 6 na R118 e no "sempre" n.º 5, letra por letra do Livro.
- **D-814:** pergunta nova F23, só quando há pergunta para o Samuel: um "###" por pergunta, com as decisões procuradas
  (que existem no Livro da versão de teste) e "Por que ainda não está respondida".
- Uma função só (`vale_para()`) escolhe os campos para o formulário e para o pacote.
- Um teste antigo mudado, com a D-809 citada no commit: o que cobrava exatamente 24 conferências (aceito pela gerente
  em 20/11: continua cobrando as 24 iguais; as novas seguem a numeração).
- Tirar atalho de pasta: `(Get-Item x).Delete()` (do CLAUDE.md §10.9) e `cmd /c rmdir x` (da D-809) não se
  contradizem: os dois tiram só o atalho (a gerente, 20/11). A contradição X17 que eu tinha anotado saiu do catálogo.

- Depois de quem quebrou (20/11, decisões da gerente):
  - a `.github/` conta para a K25; os dois scripts da rodada consertados como anexos (`anexos/workflow/`): busca rasa só
    numa cópia já rasa, e o `git clean` só no GitHub;
  - a K25 acusa o `git clean` (menos `-n` e `--dry-run`), aceita o comando do git que só roda no GitHub na mesma
    linha, e não lê o `git rm` como o `rm` do terminal;
  - a proteção tem um exemplo de cada jeito de ler o comando (`EXEMPLOS_DA_K25`);
  - no formulário, só conta como teste um `def test_...` do código, e "Nenhuma" só vale sem pergunta embaixo;
  - a R157 vai também ao trabalho do Windows sem teste;
  - o comentário do juiz diz o que foi provado sobre a barra no fim.

## Arquivos criados ou alterados

- `regras_dos_agentes/catalogo.py`
- `regras_dos_agentes/porteiro.py`
- `regras_dos_agentes/formulario.py`
- `regras_dos_agentes/montar_pacote.py`
- `regras_dos_agentes/leitura_do_codigo.py`
- `regras_dos_agentes/protecao.py`
- `relatorios/passo0-2026-11-19/anexos/juiz-no-workflow/porteiro_juiz.sh`
- `tests/test_conferencias_codigo.py`
- `tests/test_conferencias_formulario.py`
- `tests/test_conferencias_pacote.py`
- `tests/test_conferencias_protecao.py`
- `relatorios/regras-catalogo-2026-11-19/` (este ONDE-PAREI e os anexos)

## Como cumpri cada uma

- D-791: a K25 barra desde já (está em `_DO_CODIGO_PYTHON` e no `conferir_codigo`), acusa o errado e não acusa o certo:
  `tests/test_conferencias_codigo.py::test_k25_acusa_o_git_que_muda_a_pasta_git_inteira_num_script` e
  `tests/test_conferencias_codigo.py::test_k25_nao_acusa_o_git_que_so_le_nem_o_texto_solto`. Os 2 lugares de hoje não
  foram para a lista de exceções.
- D-792: as perguntas novas estão em `formulario.CAMPOS`, escolhidas pela etiqueta (`vale_para()`), e o pacote as mostra:
  `tests/test_conferencias_pacote.py::test_os_campos_em_branco_do_pacote_sao_os_que_o_formulario_cobra`.
- D-798: não escrevi o rótulo de pronto (a K10 confere).
- D-803 e D-804: as seis propostas do catálogo, cada uma com o "ok" no Livro, viraram regra, conferência ou pergunta.
- D-808: feitas juntas, por este agente, depois das seis perguntas.
- D-809: `tests/test_conferencias_codigo.py::test_k25_acusa_o_script_do_juiz_de_19_11_e_nao_o_consertado` (o caso que
  originou), `tests/test_conferencias_codigo.py::test_k25_acusa_apagar_com_tudo_dentro_sem_conferir_o_atalho` e
  `tests/test_conferencias_codigo.py::test_k25_os_dois_jeitos_certos_de_tirar_o_atalho_nao_sao_acusados`; a regra no
  pacote: `tests/test_conferencias_pacote.py::test_d809_d810_d812_as_regras_novas_vao_aos_trabalhos_certos`; as listas
  protegidas: `tests/test_conferencias_protecao.py::test_k25_tirar_linha_das_listas_e_acusado`,
  `tests/test_conferencias_protecao.py::test_k25_crescer_a_excecao_ou_o_que_conta_como_conferir_e_acusado` e
  `tests/test_conferencias_protecao.py::test_k25_afrouxar_pelo_uso_e_acusado`. O script do juiz consertado: a K25 não o
  acusa mais, e `tests/test_conferencias_copia_inteira.py` (que roda o script de verdade) passa.
- D-810: `tests/test_conferencias_pacote.py::test_d809_d810_d812_as_regras_novas_vao_aos_trabalhos_certos` (a lista com
  "Everyone" vai no pacote do Windows e no de testes; não no de pesquisa). Sem conferência do porteiro, como a decisão.
- D-811: `tests/test_conferencias_formulario.py::test_d811_trabalho_do_windows_sem_as_protecoes_e_os_testes_volta`.
- D-812: `tests/test_conferencias_formulario.py::test_d812_trabalho_que_confere_tem_de_dizer_de_onde_vem_cada_dado`.
- D-813: `tests/test_conferencias_pacote.py::test_d813_o_acrescimo_a_regra_6_e_o_texto_do_livro_e_vai_em_todo_pacote`
  (o texto é o do Livro letra por letra e vai nos pacotes dos cinco papéis). O CLAUDE.md ficou com a gerente.
- D-814: `tests/test_conferencias_formulario.py::test_d814_pergunta_ao_samuel_sem_as_decisoes_procuradas_volta`.

## Testes

- No PC, um arquivo por vez (`.venv` do repositório, `QT_QPA_PLATFORM=offscreen`), no commit `32ff536a`:
  `tests/test_conferencias_codigo.py` 107 passaram; `tests/test_conferencias_formulario.py` 41;
  `tests/test_conferencias_pacote.py` 26; `tests/test_conferencias_protecao.py` 19; `tests/test_conferencias_juiz.py` 9;
  `tests/test_conferencias_copia_inteira.py` 2. `tests/test_conferencias_excecoes.py` (no commit `ce3fa9c4`): 13
  passaram e 1 falhou, o esperado (abaixo). No PC, o porteiro do repositório inteiro acha só o `core/windows.py:1211`.
- As provas das decisões (`tests/test_decisoes*.py`) e o resto: só no GitHub (não mexi em nada que elas usam).
- GitHub: rodada RODADA_FINAL (commit `32ff536a`): VEREDITO_FINAL.
  **O esperado:** falha só em `tests/test_conferencias_excecoes.py::test_o_repositorio_so_tem_os_erros_que_a_lista_deixa`,
  com estes lugares, até eles saírem do código:
  - `core/windows.py:1211`, até o passo 2 entrar;
  - `.github/scripts/preparar_versao.sh:24` e `:29` e `.github/scripts/trocar_codigo.sh:30` (o `--depth=1` fixo) e
    `.github/scripts/trocar_codigo.sh:34` (o `git clean`), até a gerente copiar os consertos de
    `anexos/workflow/` para o ramo dos testes. O `git rm` da linha 32 não é mais acusado.
  Rodadas antigas: 44650587272 (commit `ce3fa9c4`, a que quem quebrou leu), 44645835672, 44644866610 e 44645456574
  (cancelada).
- PORTEIRO: LINHA_PORTEIRO.

## Caminho e função

- O GitHub e o antes do commit → `conferir_codigo()` → `k25()` (Python) e `k25_terminal()` (terminal) →
  `_o_que_o_comando_muda()`: o mesmo resultado nos dois, provado pelos testes da K25 em
  `tests/test_conferencias_codigo.py`, que chamam o `conferir_codigo()` (o que os dois caminhos usam). No GitHub, o
  repositório tem também a `.github/` do ramo dos testes, e ela conta (decisão da gerente, 20/11).
- O formulário e o pacote → `vale_para()`: o mesmo resultado nos dois, provado por
  `tests/test_conferencias_pacote.py::test_os_campos_em_branco_do_pacote_sao_os_que_o_formulario_cobra`.
- A proteção do GitHub → `protecao.comparar()` → `o_que_afrouxou()` e `exemplos_que_o_porteiro_nao_acha()`, com as
  listas da K25 e um exemplo de cada jeito de ler o comando:
  `tests/test_conferencias_protecao.py::test_k25_desligar_um_jeito_de_ler_o_comando_e_acusado`.

## Máquina ou olho

Máquina: tudo (testes em `tests/` e o exercício de desligar cada proteção). Nada aqui é de olho (não há imagem nem tela).

## Ressalvas

1. **O GitHub vai acusar** o teste do repositório inteiro até o passo 2 entrar e até a gerente copiar os consertos dos
   scripts da rodada (decisão da gerente, 20/11). Ver "Testes".
2. **O conserto do script do juiz não tem teste em `tests/` com um atalho de verdade** (`tests/test_conferencias_juiz.py`
   não está na minha lista). A prova é a do PC (20/11): no Git Bash 5.2.37, `[ -L ]` e `[ -h ]` deram sim para uma
   junção feita com `mklink /J` na minha pasta de rascunho; quem quebrou rodou o trecho consertado com a pasta do juiz
   sendo uma junção, e ele parou sem apagar (`quem-quebrou/relatorio-1.md`, Q2).
3. **Os dois scripts consertados da rodada não foram rodados** (só `bash -n` e a K25): o `preparar_versao.sh` e o
   `trocar_codigo.sh` rodam só na rodada do GitHub, e o conserto é o mesmo do juiz, já rodado. A condição do
   `git clean` foi provada com `set -euo pipefail`: fora do GitHub não roda e o script continua; com
   `GITHUB_ACTIONS=true`, roda.
4. **O resto do `trocar_codigo.sh` continua mexendo na cópia de quem roda:** o `git rm --cached` e o `git checkout
   FETCH_HEAD -- .` trocam o índice e os arquivos da cópia; o `preparar_versao.sh` faz um `git worktree add` (que fica
   anotado na pasta `.git` que as cópias dividem). Rodados à mão no PC, ainda bagunçariam a cópia. Não mexi (o pedido
   foi o `--depth` e o `git clean`); a gerente decide se o script inteiro deve recusar rodar fora do GitHub.
5. **A D-812 não vale para o trabalho só de testes** (achado 12 de quem quebrou): a pergunta "De onde vem cada dado"
   vale para o trabalho do Windows e o do porteiro (`TRABALHO_QUE_CONFERE`); o Livro fala em "toda conferência (do
   porteiro, de um teste ou do programa)". Isso estreita a decisão do Samuel; a gerente leva a ele se for preciso.
6. **Falso alarme possível nos testes:** um texto de exemplo que começa com o comando (`"git gc"`) conta como comando;
   aconteceu com o meu próprio teste duas vezes e foi consertado. A docstring de `comandos()` avisa.
7. **`shutil.rmtree` não é acusado** (aceito pela gerente, 20/11); as linhas lidas do Python 3.14 estão no comentário da
   K25 (`regras_dos_agentes/porteiro.py`, acima de `PALAVRAS_DE_APAGAR`).
8. **O ONDE-PAREI do passo 2** (`relatorios/passo2-publicar/ONDE-PAREI.md`) é de trabalho do Windows: passa a ser
   devolvido por faltar "Cada proteção e o teste que falha sem ela" e "De onde vem cada dado que a conferência usa";
   e, se ele tiver pergunta para o Samuel, as decisões procuradas.

## Ideias e bugs

Para a Lista de espera (decisão da gerente, 20/11: sem mexer agora):
- Achado 2: o comando do PowerShell no meio de um texto que não começa com ele não é acusado (os dois lugares de
  `core/testes_a_distancia.py`, `:601` e `:605`, vão para o passo 4, que reescreve o arquivo).
- Achado 3: o comando dividido com `.split()` ou `shlex.split()`, o programa numa variável, o `"git"` entre aspas no
  `.sh` e o `& "git.exe"` no `.ps1` passam.
- Achado 5: as funções de escrever da peça do git (`configurar`, `criar_e_ir_para_o_ramo`, `enviar`) aceitam o
  repositório de verdade.
- Achado 8: falsos alarmes raros (`-Recurse:$false`, o comentário de bloco `<# #>`, o aviso que começa com o comando).
- Achado 9: "conferiu o atalho" vale para qualquer caminho e qualquer menção antes; `[ -L "$X/" ]` com barra responde
  "não é atalho".
- Achado 15 (menos o `git clean`, que entrou): `git maintenance`, `git repack`, `git reflog expire`, `git remote
  set-url`, `git branch -D`, `rd /s`, `(Get-Item x).Delete($true)`, `find -delete` e o `.yml` não são olhados.
- Uma etiqueta "conferência" na tabela, para a D-812 valer também para o teste comum (ressalva 5).
- A R158 (de onde vem cada dado) tem só a etiqueta de testes.
- As opções do `git fetch` e do `rm` que a K25 procura são do meu conhecimento, não relidas na documentação.
- Bug que não impede (19/11): a conferência do F6 diz "ou escreva não se aplica: motivo", mas não aceita "não se aplica"
  (`regras_dos_agentes/formulario.py`, `_conferir_conteudo`, o laço de `CASOS_DE_FALHA`).
- Bug que não impede (20/11): o destino de cada achado no F19 aceita só "consertado no commit", "não é defeito" ou
  "vira pergunta"; não há "vai para a Lista de espera" (`regras_dos_agentes/formulario.py`, `_conferir_f19`).
- Incidente meu (20/11, 00:33 UTC): a cota da conta no GitHub acabou; parte foi dos meus vigias da rodada. Daqui em
  diante, no máximo uma consulta a cada 5 minutos.

## Perguntas para o Samuel

Nenhuma minha.

## O script do juiz consertado (para a gerente copiar para `.github/scripts/porteiro_juiz.sh`)

O arquivo inteiro está em `relatorios/passo0-2026-11-19/anexos/juiz-no-workflow/porteiro_juiz.sh` (commit `32ff536a`;
a conferência é a mesma do commit `ce3fa9c4`, só o comentário mudou). No lugar da linha
`rm -rf "$JUIZ" && mkdir -p "$JUIZ"`:

```bash
# A pasta do juiz é apagada com tudo dentro: antes, confere que ela não é atalho de pasta (junção ou link) (D-809; a
# pasta modelos/ esvaziada em 18/11). O que foi provado no Git Bash 5.2.37 (msys), em 20/11, numa junção de prova:
# `rm -rf "$JUIZ"` SEM barra no fim tira só o atalho; `rm -rf "$JUIZ/"` COM barra no fim apaga o conteúdo da pasta de
# verdade; `[ -L ]` e `[ -h ]` dão sim para a junção (sem barra no fim). A conferência fica porque nada garante que
# ninguém vai acrescentar a barra. Arriscado: tirar esta conferência, ou escrever `$JUIZ/` nela ou no `rm`.
if [ -L "$JUIZ" ] || [ -h "$JUIZ" ]; then
  avisar error "PORTEIRO: NAO CONFERIDO (a pasta do juiz $JUIZ é um atalho de pasta: não apago o que está nela)"
  exit 1
fi
rm -rf "$JUIZ" && mkdir -p "$JUIZ"
```

## Os dois scripts da rodada consertados (para a gerente copiar para `.github/scripts/`)

Os arquivos inteiros: `relatorios/regras-catalogo-2026-11-19/anexos/workflow/preparar_versao.sh` e
`relatorios/regras-catalogo-2026-11-19/anexos/workflow/trocar_codigo.sh` (commit `c51285c4`). O que muda:
- nos dois, a busca: `PROFUNDIDADE=""`, `[ "$(git rev-parse --is-shallow-repository)" = "true" ] &&
  PROFUNDIDADE="--depth=1"`, e `git fetch $PROFUNDIDADE origin ...` no lugar de `git fetch --depth=1 origin ...` (as
  duas buscas do `preparar_versao.sh` e a do `trocar_codigo.sh`);
- no `trocar_codigo.sh`, o `git clean -fdq -- . ':(exclude).github'` passa a ter na frente, na mesma linha,
  `[ "${GITHUB_ACTIONS:-}" = "true" ] &&`;
- os comentários do começo dizem por quê.

## Commit

Último commit do trabalho: 32ff536a.

## O que o agente que tentou quebrar achou

Relatório: `quem-quebrou/relatorio-1.md` (commit `6ac413d8`). Cada achado e o destino:

1. A `.github/` conta para a K25: consertado no commit c51285c4 (os dois scripts da rodada em `anexos/workflow/`, o
   `git clean` na K25, o `git rm` não lido como `rm`); a gerente copia para o ramo dos testes.
2. O comando no meio de um texto: não é defeito que impeça este trabalho; vai para a Lista de espera (gerente, 20/11),
   e os dois lugares de `core/testes_a_distancia.py` para o passo 4.
3. O comando com `.split()`: não é defeito que impeça este trabalho; Lista de espera (gerente, 20/11).
4. Os três jeitos de afrouxar a K25 na proteção: consertado no commit c51285c4 (`EXEMPLOS_DA_K25`).
5. As funções de escrever da peça do git: não é defeito que impeça este trabalho; Lista de espera (gerente, 20/11).
6. "O teste existe" aceitava o que não é teste: consertado no commit 32ff536a.
7. "Nenhuma" desligava a conferência das perguntas: consertado no commit 32ff536a.
8. Falsos alarmes raros: não é defeito que impeça este trabalho; Lista de espera (gerente, 20/11).
9. "Conferiu o atalho" vale para qualquer menção: não é defeito que impeça este trabalho; Lista de espera (gerente,
   20/11).
10. A R157 não ia ao trabalho do Windows sem teste: consertado no commit 32ff536a.
11. O comentário do juiz: consertado no commit 32ff536a.
12. A D-812 não vale para o trabalho só de testes: vira pergunta ao Samuel se a gerente achar preciso (ressalva 5).
13. O formulário deste trabalho era devolvido: não é defeito do código; completado neste ONDE-PAREI (o item sem teste
    saiu da lista das proteções e foi para as ressalvas; a rodada e a linha do porteiro em "Testes").
14. O pacote de quem quebrou com o papel errado: não é defeito deste trabalho (o pacote é da gerente; sem ação).
15. Comandos que a K25 não olha: o `git clean` consertado no commit c51285c4; o resto não é defeito que impeça este
    trabalho, Lista de espera (gerente, 20/11).

## A prova de verdade

Não se aplica: este trabalho não pede nada ao Windows; a K25 e o formulário só leem texto e o git, e rodam nos testes.

## Perguntas do Windows que o Samuel vê

0: nada aqui pede licença ao Windows nem abre janela.
