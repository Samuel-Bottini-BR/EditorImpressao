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
  rodadas do GitHub disparadas. **A K25 achou dois lugares no código de hoje (seção "Para a gerente"): não entraram
  na lista de exceções; a gerente leva ao Samuel.** Por causa deles, o teste do repositório inteiro
  (`tests/test_conferencias_excecoes.py::test_o_repositorio_so_tem_os_erros_que_a_lista_deixa`) falha, no PC e no
  GitHub, até o Samuel decidir.

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
  **Achou 2 lugares no código de hoje (seção "Para a gerente"); não entraram na lista.**
- **D-810:** regra nova R157 (os três computadores), etiqueta testes.
- **D-811:** pergunta nova F21 no formulário (trabalho do Windows): a lista das proteções, cada uma com o teste
  (`arquivo::função`) que existe.
- **D-812:** regra nova R158 e pergunta nova F22 (trabalho do Windows e do porteiro).
- **D-813:** o acréscimo à regra 6 na R118 e no "sempre" n.º 5, letra por letra do Livro.
- **D-814:** pergunta nova F23, só quando há pergunta para o Samuel: um "###" por pergunta, com as decisões procuradas
  (que existem no Livro da versão de teste) e "Por que ainda não está respondida".
- Uma função só (`vale_para()`) escolhe os campos para o formulário e para o pacote.
- Contradição nova anotada no catálogo (X17): o CLAUDE.md manda tirar a junção com `(Get-Item).Delete()`; a D-809 diz
  "só com `cmd /c rmdir`".
- Um teste antigo mudado, com a D-809 citada no commit: o que cobrava exatamente 24 conferências (ressalva 1).

## Arquivos criados ou alterados

- `regras_dos_agentes/catalogo.py`
- `regras_dos_agentes/porteiro.py`
- `regras_dos_agentes/formulario.py`
- `regras_dos_agentes/montar_pacote.py`
- `regras_dos_agentes/leitura_do_codigo.py`
- `tests/test_conferencias_codigo.py`
- `tests/test_conferencias_formulario.py`
- `tests/test_conferencias_pacote.py`
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
  originou) e `tests/test_conferencias_codigo.py::test_k25_acusa_apagar_com_tudo_dentro_sem_conferir_o_atalho`; a regra
  no pacote: `tests/test_conferencias_pacote.py::test_d809_d810_d812_as_regras_novas_vao_aos_trabalhos_certos`.
- D-810: `tests/test_conferencias_pacote.py::test_d809_d810_d812_as_regras_novas_vao_aos_trabalhos_certos` (a lista com
  "Everyone" vai no pacote do Windows e no de testes; não no de pesquisa). Sem conferência do porteiro, como a decisão.
- D-811: `tests/test_conferencias_formulario.py::test_d811_trabalho_do_windows_sem_as_protecoes_e_os_testes_volta`.
- D-812: `tests/test_conferencias_formulario.py::test_d812_trabalho_que_confere_tem_de_dizer_de_onde_vem_cada_dado`.
- D-813: `tests/test_conferencias_pacote.py::test_d813_o_acrescimo_a_regra_6_e_o_texto_do_livro_e_vai_em_todo_pacote`
  (o texto é o do Livro letra por letra e vai nos pacotes dos cinco papéis). O CLAUDE.md ficou com a gerente.
- D-814: `tests/test_conferencias_formulario.py::test_d814_pergunta_ao_samuel_sem_as_decisoes_procuradas_volta`.

## Testes

- No PC, um arquivo por vez (`.venv` do repositório, `QT_QPA_PLATFORM=offscreen`):
  `tests/test_conferencias_codigo.py` 101 passaram; `tests/test_conferencias_formulario.py` 39; `tests/test_conferencias_pacote.py`
  25; `tests/test_conferencias_mudancas.py` 21; `tests/test_conferencias_antes_do_commit.py` 12;
  `tests/test_conferencias_juiz.py` 9; `tests/test_conferencias_copia_inteira.py` 2; `tests/test_conferencias_protecao.py` 11;
  `tests/test_conferencias_excecoes.py` 13 passaram e **1 falhou, de propósito da decisão**:
  `tests/test_conferencias_excecoes.py::test_o_repositorio_so_tem_os_erros_que_a_lista_deixa` acusa os 2 lugares da
  K25 (seção "Para a gerente").
- As provas das decisões (`tests/test_decisoes*.py`) e o resto: só no GitHub (não mexi em nada que elas usam).
- GitHub: rodada 44645835672 (último commit do código, `88d834c7`): RESULTADO A PREENCHER. Antes, a rodada
  44644866610 (commit `f4a9ee9c`) e a 44645456574 (cancelada, ficou velha).
- PORTEIRO: A PREENCHER.

## Caminho e função

- O GitHub e o antes do commit → `conferir_codigo()` → `k25()` (Python) e `k25_terminal()` (terminal) →
  `_o_que_o_comando_muda()`: o mesmo resultado nos dois, provado pelos testes da K25 em
  `tests/test_conferencias_codigo.py`, que chamam o `conferir_codigo()` (o que os dois caminhos usam).
- O formulário e o pacote → `vale_para()`: o mesmo resultado nos dois, provado por
  `tests/test_conferencias_pacote.py::test_os_campos_em_branco_do_pacote_sao_os_que_o_formulario_cobra`.

## Máquina ou olho

Máquina: tudo (testes em `tests/` e o exercício de desligar cada proteção). Nada aqui é de olho (não há imagem nem tela).

## Ressalvas

1. **Mudei um teste antigo**, com a D-809 citada no commit `282c4684`:
   `tests/test_conferencias_codigo.py::test_as_24_conferencias_tem_a_numeracao_da_tabela_da_proposta` cobrava exatamente
   24 conferências, e a D-809 manda uma a mais. Continua cobrando as 24, iguais e na mesma ordem; passou a cobrar que
   as novas continuam a numeração e citam a decisão. A gerente confirma se aceita.
2. **O GitHub vai acusar** o teste do repositório inteiro por causa dos 2 lugares da K25, até o Samuel decidir.
3. **As listas novas da K25 ainda não estão protegidas** contra um ramo que as afrouxe: falta pôr `PECAS_DO_GIT`,
   `COMANDOS_DE_TERMINAL`, `PALAVRAS_DO_GIT`, `PALAVRAS_DE_APAGAR` e `CONFERE_SE_E_ATALHO` em `protecao.PROTEGIDOS`
   (`regras_dos_agentes/protecao.py`, fora da minha lista; a gerente).
4. **"Trabalho que confere algo" (D-812) não tem etiqueta própria.** Usei Windows ou da gerente (o porteiro e as provas
   dele), `TRABALHO_QUE_CONFERE`. Um trabalho só de testes não recebe a pergunta: se recebesse, o teste antigo do
   formulário certo de um trabalho só de testes quebraria. Mais justo seria uma etiqueta "conferência" na tabela
   (`tabela_arquivos.py`, fora da minha lista).
5. **As regras R157 e R158 têm só a etiqueta de testes** (a D-810 diz "Windows e testes"): o montador só manda uma regra
   com WIN junto a trabalho do Windows; só com TESTE, ela vai a todo trabalho com teste, inclusive os do Windows. Um
   trabalho do Windows sem nenhum arquivo de teste não a recebe.
6. **O que a K25 não pega** (está no "não pega" dela): comando montado em outra função ou guardado num texto que não
   começa com ele (ex.: `core/testes_a_distancia.py:601`, um `Remove-Item -Recurse` dentro de um `if` do PowerShell,
   não é acusado, e o vizinho dele em `core/windows.py:1211` é); `os.exec`/`os.spawn`; `rd /s` e `robocopy`; apagar
   DENTRO de um atalho; mexer em ramo que não é o seu (fica só na regra). As opções do `git fetch` e do `rm` são do
   meu conhecimento, não relidas.
7. **Falso alarme possível nos testes:** um texto de exemplo que começa com o comando (`"git gc"`) conta como comando;
   aconteceu com o meu próprio teste e foi consertado (commit `f4a9ee9c`). A docstring de `comandos()` avisa.
8. **`shutil.rmtree` não é acusado**, de propósito (o do Python 3.14 já confere o atalho, ver "O que li"). O pedido
   listava ele; se a gerente quiser que acuse mesmo assim, são cerca de 80 lugares no código de hoje.
9. **O ONDE-PAREI do passo 2** (`relatorios/passo2-publicar/ONDE-PAREI.md`, ramo `passo2-publicar-2026-11-19`) é de
   trabalho do Windows: passa a ser devolvido por faltar as duas seções novas "Cada proteção e o teste que falha sem
   ela" e "De onde vem cada dado que a conferência usa"; e, se ele tiver pergunta para o Samuel, a terceira. O código
   dele tem o mesmo lugar do `core/windows.py` (linha 1212 lá).

## Ideias e bugs

- Ideia: uma etiqueta "conferência" na tabela (para a D-812 valer também para o teste comum que confere algo).
- Ideia: a K25 seguir o comando guardado num texto que não começa com ele (o caso do `core/testes_a_distancia.py:601`).
- Incidente meu (20/11, 00:33 UTC): a cota da conta no GitHub (5000 pedidos por hora) acabou; parte foi dos meus
  vigias da rodada (consultavam a cada 30 a 60 segundos). A cota é a mesma do agente do passo 2. Parei os vigias e
  esperei a cota voltar (01:00 UTC) sem consultar. Ideia: a regra dos testes no GitHub dizer "uma consulta à rodada a
  cada 5 minutos, no máximo".
- Bug que não impede (19/11): a conferência do F6 diz "ou escreva não se aplica: motivo", mas não aceita "não se aplica"
  (`regras_dos_agentes/formulario.py`, `_conferir_conteudo`, o laço de `CASOS_DE_FALHA`).

## Perguntas para o Samuel

Nenhuma minha. Os 2 lugares que a K25 achou vão à gerente (seção abaixo), que decide como levar ao Samuel.

## Para a gerente: os lugares que a K25 achou no código de hoje

Não entraram na lista de exceções (o ramo de agente nunca acrescenta item). Os dois apagam uma pasta com tudo dentro
sem conferir antes se ela é atalho:
1. `core/windows.py:1211`, função `lancar_powershell_solto` (a peça única do Windows, programa, não script): o script do
   PowerShell que o programa lança apaga a própria pasta de troca no fim com
   `Remove-Item -LiteralPath <pasta> -Recurse -Force -ErrorAction SilentlyContinue`. A pasta é criada pela peça
   (`criar_pasta_de_troca`), então hoje ela não é atalho; mas nada confere.
2. `relatorios/passo0-2026-11-19/anexos/juiz-no-workflow/porteiro_juiz.sh:52` (o script do juiz, que roda no GitHub):
   `rm -rf "$JUIZ" && mkdir -p "$JUIZ"`, a pasta de trabalho do juiz.

## Commit

Último commit do trabalho: 88d834c7.

## O que o agente que tentou quebrar achou

(a preencher depois de quem tenta quebrar)

## A prova de verdade

Não se aplica: este trabalho não pede nada ao Windows; a K25 e o formulário só leem texto e o git, e rodam nos testes.

## Perguntas do Windows que o Samuel vê

0: nada aqui pede licença ao Windows nem abre janela.
