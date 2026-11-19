# Passo 0 do plano da parte do Windows: o pacote de regras, o porteiro e o formulário (19/11/2026)

Implementador. Ramo `passo0-porteiro-2026-11-19`, worktree `.claude/worktrees/passo0`, saiu de `obra-2026-10-26`
(`746dbda6`). Nenhuma linha do programa (`core/`, `ui/`, arquivos do programa na raiz) muda.

## Pedido

- Papel: implementador
- Commit de partida: 746dbda6
- Ramo: passo0-porteiro-2026-11-19

## Onde parei

- (19/11, começo) Li o implementador.md, o CLAUDE.md inteiro, a memória (índice e regras de trabalho), as decisões
  pedidas (D-767, D-775, D-784 a D-787, D-791 a D-800), o plano-v3 (seção 3 inteira e 6.3), a proposta das regras e
  os seis esboços. Li a documentação do git (ver "O que li da peça de fora e onde"). Começando o pacote.

## Arquivos que vou mexer

- `regras_dos_agentes/` (pasta nova: o pacote, o porteiro, a lista de exceções, o formulário, o montador)
- `tests/test_conferencias_*.py` (novos)
- `tests/conferencias_excecoes.json` (novo: a lista de exceções, proposta, esperando o "sim")
- `ganchos/pre-commit` (novo; não ligado)
- `relatorios/passo0-2026-11-19/` (este relatório)

## Decisões que esta tarefa precisa cumprir

(Palavras copiadas do Livro, `docs/plano/DECISOES.md` desta cópia.)

- **D-767**: "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione". Aqui: a
  conferência antes do commit é provada com o git de verdade num repositório de verdade (pasta temporária), não com
  peça de mentira; nada mexe no Windows.
- **D-775**: "o agente vai tentar quebrar antes de fazer o teste real na tela né?". Aqui: o formulário confere as três
  etapas e os seis campos do relatório de quem quebra.
- **D-784**: "ok, mas como vai saber que regras enviar para o agente?" · "ok". Aqui: o pacote sai de um programa
  (catálogo + tabela arquivo → etiquetas + montador); um teste cobra que todo arquivo do git tem linha.
- **D-785**: "ok, mais ainda existem mais casos na opção A". Aqui: nada deste passo mexe no Windows; não há prova à
  vista; nenhuma janela abre.
- **D-786**: "a". Aqui: nenhum processamento muda; não há filtro de velocidade a rodar.
- **D-787**: "A". Aqui: no PC, um arquivo de teste por vez; o conjunto inteiro no GitHub.
- **D-791**: "não sei do que você está falando" · "b". Aqui: as 24 conferências viram testes em `tests/` e a mesma
  busca roda antes do commit; cada uma acusa um exemplo errado feito de propósito e não acusa o certo; a lista de
  exceções é por lugar, gerada pelo programa, e só diminui.
- **D-792**: "mas e o que vai determinar o que vai nesse formulario? vai ser feito um toda vez que for enviado um
  trabalho para um agente?". Aqui: um programa confere o formulário (F1 a F20 e as perguntas das etiquetas) nas três
  etapas.
- **D-793**: "ok". Aqui: a conferência K23 lê a lista de ferramentas de cada agente.
- **D-796**: "1, mas tem que ser explissito o pedido né". Aqui: K13 lê a lista de arquivos do pedido no formulário e
  barra agente de tela que mexe em `core/` fora dela.
- **D-797**: "Só precisa de dois lugares né?". Aqui: nada deste passo junta nem fala do `master`.
- **D-798**: "fechou". Aqui: K10 barra o rótulo "PRONTO PARA CONFERIR" no ramo de quem construiu e "APROVADO" escrito
  por agente. Esta entrega não traz esse rótulo.
- **D-799**: "Aprova o plano?" → "ok". Aqui: o passo 0 do plano-v3, como escrito.
- **D-800**: "esses consertos deixa para depois". Aqui: os 5 lugares de fora ficam na lista marcados "depois da
  entrega".
- **D-605**: "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está
  escolhido e testado". Aqui: nenhum teste antigo muda; o porteiro não é ligado no repositório (a gerente liga).
- **D-637**: "você tem que pensar na experiencia do usario e no resultado final do livro dentro do programa". Aqui:
  ver "Como fica para quem usa e no livro".

## O que já está escolhido e testado aqui

- Testes que já existem e fazem parte do mesmo cuidado, e continuam como estão (plano-v3 §8 item 11):
  `tests/test_botoes_em_portugues.py`, `tests/test_sem_janela_na_tela.py`,
  `tests/test_memoria_nao_cresce_com_o_livro.py`, `tests/test_decisoes*.py`, `tests/test_promessas.py`.
- Nenhum deles é tocado. As conferências novas vivem em arquivos novos.
- A barra de rolagem cinza (CLAUDE.md §9): a conferência K22 é escrita contra os valores de hoje de `ui/estilo.py`.

## Como fica para quem usa e no livro

- **O Kaique:** nada muda. Nenhuma tela, nenhum botão, nenhum texto do programa, nenhum arquivo do programa. O PDF que
  sai é o mesmo, página por página: nada do processamento é tocado.
- **O Samuel:** recebe um texto curto com a lista de exceções para dizer "sim" (ver "Perguntas para o Samuel").
- **Os agentes e a gerente:** passam a ter o pacote de regras montado por programa, o porteiro (testes no GitHub e,
  quando a gerente ligar, a conferência antes do commit) e o programa que confere o formulário.

## A causa, a regra e todos os caminhos

(a preencher ao construir)

## O que pode falhar e o que o programa faz

(a preencher ao construir)

## O que li da peça de fora e onde

- **git, a pasta dos ganchos (`core.hooksPath`).** Documentação local do git 2.53 (`C:\Program Files\Git\mingw64\share\doc\git-doc\git-config.html`, entrada `core.hooksPath`): "By default Git will look for your hooks in the $GIT_DIR/hooks directory. Set this to different path [...] A relative path is taken as relative to the directory where the hooks are run (see the "DESCRIPTION" section of githooks(5))." E: "You can also disable all hooks entirely by setting core.hooksPath to /dev/null."
- **Onde o gancho roda.** https://git-scm.com/docs/githooks, DESCRIPTION: "Before Git invokes a hook, it changes its working directory to either $GIT_DIR in a bare repository or the root of the working tree in a non-bare repository." Portanto `core.hooksPath=ganchos` (relativo) faz cada cópia (worktree) usar a pasta `ganchos/` da própria cópia.
- **A configuração é uma só para todas as cópias.** https://git-scm.com/docs/git-worktree, CONFIGURATION FILE: "By default, the repository config file is shared across all worktrees." Ligar uma vez no `.git/config` do repositório principal vale para todas as cópias (a gerente liga).
- **Gancho que não existe numa cópia: o git não avisa.** Código do git v2.53.0, `hook.c`, `find_hook` (linhas 13-48, lido com `gh api repos/git/git/contents/hook.c?ref=v2.53.0`): se o arquivo não existe, devolve `NULL` sem mensagem (só avisa quando existe mas não é executável, `ADVICE_IGNORED_HOOK`). Uma cópia de um ramo sem `ganchos/` faz commit sem conferência e sem aviso. Por isso o teste no GitHub é quem garante.
- **Executável no Windows.** Código do git v2.53.0, `run-command.c`, `is_executable` (linhas 132-170): no Windows não há bit de executável; o git trata como executável o `.exe` ou o arquivo que começa com `#!`. A documentação (githooks) diz: "Hooks that don't have the executable bit set are ignored." O `ganchos/pre-commit` começa com `#!/bin/sh` e vai ao git com o bit de executável (vale também fora do Windows).
- **O gancho antes do commit.** https://git-scm.com/docs/githooks, pre-commit: "It takes no parameters [...] Exiting with a non-zero status from this script causes the git commit command to abort before creating a commit." E: "can be bypassed with the --no-verify option." Por isso a conferência antes do commit só avisa cedo; quem garante é o teste no GitHub.
- **Variáveis do git no gancho.** https://git-scm.com/docs/githooks, DESCRIPTION: "Environment variables, such as GIT_DIR, GIT_WORK_TREE, etc., are exported so that Git commands run by the hook can correctly locate the repository." O gancho lê o que vai no commit pelo índice (`git diff --cached`, `git show :caminho`), não pela pasta.

## Perguntas para o Samuel

(a preencher)
