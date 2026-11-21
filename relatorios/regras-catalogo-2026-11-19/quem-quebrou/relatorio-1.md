# Regras novas do catálogo dos erros: primeira conferência de quem tentou quebrar (20/11/2026)

Feita por um verificador que não escreveu este código. Conferi o código de `ce3fa9c4` (o último de código) e o
formulário de `03446920`. Não mexi no código, não pedi licença ao Windows e não abri janela na tela do Samuel. O
repositório do PC continuou inteiro: `--is-shallow-repository` deu false antes e depois.

## Pedido

- Papel: verificador
- Commit de partida: 047fd330
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

(Copiado do pacote, sem mudar nada. Só escrevi em `relatorios/regras-catalogo-2026-11-19/quem-quebrou/`.)

## Veredito

**Ainda não pode juntar.**

- **Grave (achado 1):** a conferência nova do porteiro vai barrar todas as rodadas do GitHub, mesmo depois do
  passo 2.
  - A rodada 44650587272 não falhou só por causa do `core/windows.py:1211`. Ela acusou mais quatro lugares nos
    scripts da própria rodada (`.github/scripts/trocar_codigo.sh` e `preparar_versao.sh`).
  - No PC esses scripts não existem no ramo. Por isso a falha só aparece no GitHub. É a família "o teste supõe o
    computador" do próprio catálogo.
  - Um desses quatro é falso alarme (`git rm -r --cached` mexe só no índice do git, não apaga pasta).
  - Quando a conferência estiver na versão de teste, o juiz também vai acusar esses quatro lugares e escrever
    BARROU em toda rodada.
- **Médio:** os comandos do PowerShell escritos dentro de um texto maior não são acusados (achado 2), e há o
  mesmo erro hoje em `core/testes_a_distancia.py:601` e `:605`. A proteção contra afrouxar não vê três jeitos de
  afrouxar a conferência (achado 4). As funções de escrever da peça do git aceitam o repositório de verdade
  (achado 5).
- O resto é pequeno, ou vem de uma escolha já anotada pela gerente.
- O formulário do próprio trabalho é devolvido pelo programa (achado 13).
- Não escrevo o rótulo de pronto, pela D-798. Este trabalho não tem prova à vista, porque não mexe no Windows, e ainda
  há achado grave.

## O que li

- `.claude/agents/verificador.md`, o `CLAUDE.md` inteiro, `memoria/INDICE.md` e `memoria/catalogo-de-erros.md`
  (família F9, linhas 277 a 410).
- O meu pacote (`anexos/pacote-quem-quebra.md`), o ONDE-PAREI do trabalho, `anexos/mutacoes.py` e
  `anexos/mutacoes-resultado.txt`.
- No Livro, as linhas D-808 a D-814 inteiras, com as colunas "onde" e "prova".
- O código mudado: `git diff 0fe54cb3..ce3fa9c4` de `porteiro.py`, `leitura_do_codigo.py`, `formulario.py`,
  `montar_pacote.py`, `catalogo.py` e `protecao.py`, e as provas novas em `tests/`. Li também, sem mudança no
  trabalho:
  - `juiz.py`;
  - `porteiro_mudancas.py`, nos trechos de `PROTEGIDOS` e da K10;
  - `conversa_com_o_git.py`, nas funções de escrever.
- O registro da rodada 44650587272 do GitHub (só as partes que falharam) e o resumo dela. Foram duas consultas ao
  GitHub.
- Os scripts da rodada no ramo `claude/list-server-files-gkos8v` (commit `781d64e6`): `porteiro_juiz.sh`,
  `trocar_codigo.sh`, `preparar_versao.sh` e o `testes-windows.yml`.
- A peça de fora, lida de verdade:
  - `shutil.py` do Python 3.14, linhas 659 a 690, e `os.py`, linhas 378 a 383. As linhas que o ONDE-PAREI cita
    batem;
  - o `rm` do Git Bash 5.2.37 e o `Remove-Item` do PowerShell 5.1.26100, testados num atalho de pasta de verdade,
    na minha pasta de rascunho (ver Q2).

## O que conferi nas falhas, nas peças de fora e nos caminhos

Tudo por máquina, no PC.

- **Testes no PC, um arquivo por vez, no commit `ce3fa9c4`:** `test_conferencias_codigo` 102 passaram;
  `test_conferencias_pacote` 25; `test_conferencias_protecao` 15; `test_conferencias_formulario` 39.
- **A prova de reversão (as provas novas no código de antes, `0fe54cb3`, numa cópia à parte feita com `git archive`):**
  - as provas da conferência nova (K25): 14 falham no código de antes; as 12 que passam lá são as de "não acusa o
    que está certo" e a das 24 conferências (que é o esperado);
  - as provas do formulário (D-811, D-812, D-814): 4 falham no código de antes; passa a de "não vale para o
    trabalho só de testes", que é de não-regressão (esperado);
  - as provas do pacote (D-809, D-813, campos em branco, perguntas novas): as 4 falham no código de antes.
- **As mutações dele (12 de 12 acusadas):** conferi que cada uma desliga a coisa certa. Elas provam só que os testes
  do próprio ramo reclamam; o que um ramo consegue afrouxar sem a proteção do GitHub ver está no achado 4.
- **A conferência nova contra 108 variações de comando** (script e resultado: `anexos/sondar_k25.py.txt` e
  `anexos/sondar_k25-resultado.txt`). Acusa certo: aspas, comando em lista, `subprocess` com lista, apelido do
  módulo, `from subprocess import run`, `os.system`, `os.popen`, `shell=True`, `git -C`, `git --git-dir`,
  `git config --global`, `rm -fr`, `rm -r -f`, `rm -f -r`, `rm --recursive`, `rm -Rf`, `/usr/bin/rm`, `bash -c "rm
  -rf"`, `find -exec rm -rf`, `Remove-Item -Recurse:$true`, `-Rec`, `ri -r`, `rd`, `del`, `rmdir -r`, o
  `Get-ChildItem | Remove-Item -Recurse` dentro de uma chamada, `.cmd` com `powershell -c "Remove-Item ..."`, e
  `.psm1`. Não acusa o que está certo: `git config` que só lê, `git stash list`, `git fetch` normal, `git clone
  --depth`, `git -c chave=valor`, `cmd /c rmdir`, `(Get-Item x).Delete()`, comentário. O que passa e o que é falso
  alarme está nos achados 1, 2, 3 e 9.
- **O atalho de pasta de verdade (D-813: o que a peça de fora faz de verdade)**, na minha pasta de rascunho, com
  uma junção feita com `mklink /J` (`anexos/atalho-de-pasta-de-verdade.txt`):
  - o trecho consertado do juiz, com a pasta do juiz sendo a junção, para e diz "é um atalho de pasta". A pasta de
    verdade continua inteira. **O conserto funciona**;
  - `rm -rf junção` sem barra no fim tira só o atalho. **`rm -rf junção/` com barra no fim apaga o conteúdo da pasta
    de verdade.** `[ -L junção/ ]` com barra responde "não é atalho";
  - `Remove-Item -Recurse` na junção, e na pasta que tem a junção dentro, tirou só o atalho neste PowerShell 5.1.
  - Todas as junções que sobraram foram tiradas com `cmd /c rmdir`.
- **O script do juiz:** o texto do anexo deste ramo e o `.github/scripts/porteiro_juiz.sh` do commit `781d64e6` são
  iguais letra por letra (a cópia de trabalho deste PC só troca o fim de linha). Na rodada 44650587272, o porteiro
  não acusou o `rm -rf "$JUIZ"` desse script, e o job do juiz passou.
- **O "um lugar só":** `formulario.vale_para` é a única conta que escolhe os campos. A busca no código não acha
  outra cópia de `quem != "*"`. O formulário e o pacote chamam a mesma função (mutação M11).
- **O teste antigo mudado (o das 24 conferências):** continua cobrando K01 a K24 iguais e na mesma ordem, e as
  novas na sequência, cada uma citando a decisão. Ficou do mesmo tamanho de antes: o original também só olhava os
  números. A gerente aceitou a mudança.
- **As regras novas nos pacotes** (montei pacotes de prova para nove tipos de trabalho):
  - a regra do `.git` dividido (R156) vai a todos;
  - o acréscimo da D-813 vai a todos, letra por letra igual ao Livro;
  - a dos três computadores (R157) e a de "de onde vem cada dado" (R158) vão a todo trabalho com teste, e não vão a
    trabalho do Windows sem teste (achado 10).
- **O formulário do próprio trabalho**, conferido pelo programa (`--etapa quebrar`, sem o GitHub): é **devolvido**
  (achado 13).

## Caminhos que o outro não listou

- **A rodada do GitHub tem arquivos que o PC não tem.** O workflow troca o código pelo do ramo e mantém a `.github/`
  do ramo dos testes. O `achados_do_repositorio` (no teste e no juiz) lê o que o git conhece, e no GitHub isso inclui
  a `.github/scripts/`. O ONDE-PAREI lista os caminhos "GitHub" e "antes do commit" como se lessem os mesmos
  arquivos, e não leem (achado 1).
- **As funções de escrever da peça do git chamadas de fora** (`configurar`, `criar_e_ir_para_o_ramo`, `enviar` com
  `push -f`). A K25 não olha a peça do git, de propósito, mas nada na peça confere que o repositório é de prova
  (achado 5).
- **O comando do PowerShell montado num texto que não começa com `Remove-Item`**, que é o jeito comum no projeto:
  o comando vai inteiro para a peça do Windows (achado 2).
- **O comando dividido com `.split()` ou `shlex.split()`** (achado 3).
- **Os comandos dentro do `testes-windows.yml`**: `git fetch --depth=1`, `git worktree prune`, `rm -rf`,
  `Remove-Item -Recurse`. A K25 não lê `.yml`. É razoável, porque só roda no GitHub, mas falta decidir junto com
  o achado 1.

## Falhas não pensadas e resultado não conferido

- **"Falha só pelo `core/windows.py:1211`, o esperado"** foi escrito sem ler a rodada. O próprio ONDE-PAREI diz "RODADA
  A PREENCHER". O registro mostra cinco lugares (achado 1).
- **O comentário do juiz consertado** diz que, sem a conferência, "o `rm -rf` apagaria o conteúdo da pasta de verdade".
  No Git Bash deste PC, `rm -rf "$JUIZ"` sem barra no fim não entra na junção. O perigo é com barra no fim. A
  conferência continua útil, mas a frase afirma o que não foi conferido (achado 11).
- **A conferência de atalho aceita qualquer caminho e qualquer menção** (achado 9): um `[ -L "$OUTRA" ]` no começo do
  script libera todo `rm -rf` depois dele; no Python, a palavra `islink` dentro de um texto qualquer antes da linha
  também libera.

## As regras que conferi

Para cada decisão tocada: cumprida, pela metade ou não cumprida. Não há tela nem print: as provas são de máquina.

- **D-809** ("ok, mas essas coisas foram recuperadas? e porque ele fez essa confusão se era regra ele não mexer? e tinha
  o porteiro para ele não fazer isso" · "ok"): **pela metade.**
  - A regra chega a todo pacote. O porteiro acusa os exemplos da prova do Livro ("barra um script com `git fetch
    --depth` ou `rm -rf` num atalho").
  - Mas falta resolver o falso alarme e os lugares da `.github/`, que barram toda rodada (achado 1).
  - E o mesmo `Remove-Item -Recurse` é acusado num arquivo e passa no vizinho (achado 2).
- **D-810** ("ok"): **pela metade.** A prova do Livro diz "O pacote dos agentes de Windows e de testes traz a lista".
  O pacote de um trabalho do Windows sem arquivo de teste não traz (achado 10). O ONDE-PAREI anota isso em "Ideias".
- **D-811** ("ok"): **cumprida, com um furo pequeno.** O formulário devolve a entrega do Windows sem a lista. Mas
  aceita citar uma função de ajuda ou um `def` escrito dentro de um texto de exemplo como se fosse o teste (achado 6).
- **D-812** ("ok"): **pela metade.**
  - A regra (R158) e a pergunta (F22) existem.
  - Mas a pergunta só vale para o trabalho do Windows e o do porteiro. O trabalho que escreve um teste também confere
    algo, e a decisão fala em "de um teste" (achado 12).
  - A gerente deixou isso para depois em 20/11. Fica anotado, porque estreita a decisão do Samuel.
- **D-813** ("ok"): **cumprida no texto, pela metade no próprio trabalho.**
  - O acréscimo está no "sempre" n.º 5 e na regra 6, letra por letra.
  - Mas a K25 é uma busca, e o ONDE-PAREI diz que as opções do `git` e do `rm` são "conhecimento meu, não relido:
    deduzido".
  - Ninguém testou o que o `rm` e o `Remove-Item` fazem num atalho de verdade. Eu testei: o perigo é o `rm -rf x/`,
    com barra no fim (Q2).
- **D-814** ("ok"): **cumprida, com um furo pequeno.** Sem as decisões procuradas, a pergunta volta. Mas basta começar
  "Perguntas para o Samuel" com "Nenhuma" para o programa não conferir nenhuma pergunta escrita embaixo (achado 7).
- **D-791** ("b"): **cumprida.** A K25 barra desde já. Os lugares de hoje não foram para a lista de exceções.
- **D-792** ("ok"): **cumprida.** Os campos novos vêm da mesma tabela (`vale_para`).
- **D-798** ("fechou"): **cumprida.** Nem quem construiu nem eu escrevemos o rótulo de pronto.
- **D-803, D-804, D-808** ("ok", "ok", "1- pode"): **cumpridas.** As seis propostas viraram regra, conferência ou
  pergunta, feitas juntas.
- **Regra 8 do §11 (o novo não estraga o que já funciona):** as provas antigas dos arquivos tocados passam no PC. O
  achado 1 quebra uma prova antiga no GitHub, além do lugar esperado do passo 2.
- **Regra 12 do §11 (sem gambiarra):**
  - não achei desvio para um caso nem conta copiada;
  - mas há duas maneiras de ler o mesmo comando, e elas dão resultados diferentes: o `Remove-Item` acusado num
    arquivo e não no vizinho (achado 2);
  - e há o mesmo comando aceito no `.yml` e acusado no `.sh` (ver Q3).

## Achados

1. **(grave) A K25 barra toda rodada do GitHub, mesmo depois do passo 2.** `regras_dos_agentes/porteiro.py:396`
   (`PALAVRAS_DE_APAGAR`) e `regras_dos_agentes/porteiro.py:364` (`PALAVRAS_DO_GIT`), lidas por
   `achados_do_repositorio`. Na rodada 44650587272, `tests/test_conferencias_excecoes.py:146` acusou cinco lugares, não
   um:
   - `.github/scripts/preparar_versao.sh:24` e `:29`, e `.github/scripts/trocar_codigo.sh:30`: o `git fetch
     --depth=1`. É o mesmo comando que deixou o PC raso em 19/11. Esses scripts, rodados à mão numa cópia, fariam o
     mesmo (o `trocar_codigo.sh` ainda roda `git clean -fdq`). O porteiro acerta em acusar, e eles precisam do mesmo
     conserto do juiz: buscar raso só se a cópia já é rasa;
   - `.github/scripts/trocar_codigo.sh:32`: `git rm -rq --cached`. **Falso alarme:** é o `rm` do git, que tira só do
     índice. Ele é lido como o `rm` do terminal porque a expressão aceita espaço antes de `rm`;
   - `core/windows.py:1211`: o lugar esperado, consertado no passo 2. Conferi no ramo `passo2-publicar-2026-11-19`
     que lá ele não é mais acusado.

   No PC aparece só o último, porque o ramo não tem a `.github/`. Quando a K25 estiver na versão de teste, o juiz
   (`regras_dos_agentes/juiz.py:65`, a mesma leitura) também acusa os quatro. Com a lista valendo, a rodada sai
   BARROU.

   O que precisa vir antes de juntar, para a gerente decidir:
   - consertar os dois scripts no ramo dos testes;
   - fazer a K25 não ler `git rm` como `rm`;
   - e decidir se a `.github/` conta para a K25.
2. **(médio) O comando do PowerShell guardado num texto só é acusado se o texto começar com `Remove-Item`.**
   `regras_dos_agentes/leitura_do_codigo.py:305` (`comeca_com_comando`).
   - Hoje no código: `core/testes_a_distancia.py:601` (`if (...) { Remove-Item -LiteralPath $p -Recurse -Force }`) e
     `core/testes_a_distancia.py:605` (`| ForEach-Object { Remove-Item ... -Recurse -Force`). São o mesmo tipo de erro
     do `core/windows.py:1211`, que só é acusado porque o texto dele começa com `Remove-Item`.
   - Também passam, guardados num texto: `rd x -Recurse`, `ri x -r` e `del x -Recurse`.
   - No projeto, o PowerShell vai quase sempre assim, como texto para a peça do Windows. O ONDE-PAREI anota isso em
     "Ideias".
   - Pela regra sem gambiarra, a mesma regra está dando resultados diferentes em dois arquivos vizinhos.
3. **(médio) O comando dividido com `.split()` ou `shlex.split()` passa.** `regras_dos_agentes/leitura_do_codigo.py:287`:
   o texto dentro da chamada é marcado como já lido, e a chamada vira `<?>`. `subprocess.run("git fetch --depth=1 origin
   x".split())` não é acusado. Também passam o programa numa variável (`GIT = "git"; subprocess.run([GIT, "gc"])`), o
   `"git" fetch` entre aspas no `.sh`, e o `& "git.exe" gc` no `.ps1`. Razoável deixar o da variável; o do `.split()` é
   comum e devia ser pego.
4. **(médio) A proteção do GitHub não vê três jeitos de afrouxar a K25.** `regras_dos_agentes/protecao.py:99`
   (`EXEMPLOS`) e `regras_dos_agentes/protecao.py:119`: todo exemplo da K25 vira uma linha de Python com
   `subprocess.run(...)` ou `os.system(...)`, que é o jeito 1 da leitura. Desliguei na memória cada jeito e a proteção
   não acusou nenhum (`anexos/afrouxar_k25.py.txt` e o resultado):
   - a K25 nos arquivos do terminal (`k25_terminal` sem achado);
   - a lista guardada (`PROGRAMAS_DA_LISTA` vazio);
   - o texto guardado (o jeito 3).

   Tirar a K25 da lista de conferências é acusado. A defesa que sobra é a K17 (só a gerente muda o porteiro). Conserto
   simples: um exemplo de cada jeito e um exemplo de terminal.
5. **(médio) As funções de escrever da peça do git aceitam o repositório de verdade.** As funções são
   `regras_dos_agentes/conversa_com_o_git.py:253` (`configurar`, que grava no `.git/config`), `:274`
   (`criar_e_ir_para_o_ramo`, um `git switch -C` com qualquer nome de ramo) e `:279` (`enviar`, com `push -f`).
   - O comentário diz "só para os repositórios de prova", mas nada confere isso.
   - A K25 não olha a peça, então `git.configurar(RAIZ, "core.hooksPath", "x")` num teste passaria calado. Isso é
     exatamente o que a D-809 proíbe.
   - Hoje as 8 chamadas de fora usam repositório de prova.
6. **(pequeno) No formulário, "o teste existe" aceita o que não é teste.** `regras_dos_agentes/formulario.py:231`
   (`teste_existe`) procura `def <nome>` em qualquer lugar do arquivo. Por isso
   `tests/test_conferencias_codigo.py::conferir` (uma função de ajuda) e `::lancar` (um `def` escrito dentro de um texto
   de exemplo) contam como testes. Também passa: a mesma prova citada para cinco proteções, e as proteções escritas em
   linhas sem "-" embaixo do primeiro item (viram continuação dele, `regras_dos_agentes/formulario.py:188`).
7. **(pequeno) Começar com "Nenhuma" desliga a conferência das perguntas.** `regras_dos_agentes/formulario.py:572`:
   "Nenhuma por enquanto, mas:" seguido de um `### pergunta` sem print, sem "O que você escolhe" e sem as decisões
   procuradas passa. A conta já existia para a seção das perguntas. Agora ela desliga também a das decisões procuradas
   (D-814).
8. **(pequeno) Falsos alarmes raros da K25.** `regras_dos_agentes/porteiro.py:397`: `Remove-Item x -Recurse:$false` é
   acusado, e o comentário de bloco `<# ... #>` do PowerShell também. O texto de aviso que começa com o comando
   (`print("git gc é proibido")`) é acusado, e o ONDE-PAREI já avisa disso na ressalva 3.
9. **(pequeno) "Conferiu o atalho" vale para qualquer caminho e qualquer menção.** No terminal,
   `regras_dos_agentes/porteiro.py:834` olha o arquivo inteiro até a linha. No Python, `regras_dos_agentes/porteiro.py:802`
   olha a função inteira, com os textos.
   - `[ -L "$OUTRA" ]` no começo libera todo `rm -rf` depois.
   - `print("não confiro islink")` libera também.
   - `[ -L "$X/" ]`, com barra no fim, responde "não é atalho" justamente no caso perigoso (Q2).
10. **(pequeno) A regra dos três computadores não vai ao trabalho do Windows sem teste.**
    `regras_dos_agentes/catalogo.py:429` (R157 e, na linha 431, R158, só com a etiqueta de testes). A prova da D-810 no
    Livro diz "O pacote dos agentes de Windows e de testes traz a lista". Está anotado em "Ideias", mas é diferente do
    Livro.
11. **(pequeno) O comentário do juiz consertado afirma o que não foi conferido.**
    `relatorios/passo0-2026-11-19/anexos/juiz-no-workflow/porteiro_juiz.sh:52`. No Git Bash, `rm -rf "$JUIZ"` sem barra
    não entra na junção (Q2). A conferência das linhas 55 a 58 continua certa e útil; só a frase precisa dizer o perigo
    de verdade (a barra no fim).
12. **(pequeno; escolha da gerente) A pergunta "de onde vem cada dado" não vale para o trabalho que escreve teste.**
    `regras_dos_agentes/formulario.py:64` (`TRABALHO_QUE_CONFERE = ("WIN", "GER")`). A D-812 fala em "toda conferência
    (do porteiro, de um teste ou do programa)". A gerente deixou para depois em 20/11. Como isso estreita a decisão do
    Samuel, devia ir à Central em vez de ficar só em "Ideias".
13. **(pequeno) O formulário do próprio trabalho é devolvido pelo programa.**
    `relatorios/regras-catalogo-2026-11-19/ONDE-PAREI.md:130`: "A conferência do atalho no script do juiz: sem teste com
    atalho de verdade" não cita um teste (F21). Ainda faltam a rodada do GitHub em "Testes" (linha 243, "RODADA A
    PREENCHER") e a linha do porteiro (linha 247).
14. **(pequeno; do pacote, não do código) O meu pacote foi montado com o papel "verificador", não "quebrador".**
    `relatorios/regras-catalogo-2026-11-19/anexos/pacote-quem-quebra.md:3`.
    - Por isso ele trouxe 43 regras em vez de todas (D-775).
    - Trouxe também o formulário de quem constrói em vez dos seis campos de quem quebra, e a lista de arquivos de quem
      construiu.
    - Usei os seis campos que o programa confere (`CAMPOS_DE_QUEM_QUEBRA`).
15. **(pequeno; não pega, razoável deixar) Comandos que a K25 não olha.** `regras_dos_agentes/porteiro.py:364`.
    - Não são acusados: `git clean -fdx`, `git maintenance`, `git repack`, `git reflog expire`, `git remote set-url` e
      `git branch -D` de outro ramo.
    - Também não: o `rd /s` e o `rmdir /s` do cmd, `(Get-Item x).Delete($true)`, `find -delete` e o `.yml`.
    - O `git clean` é o único que me preocupa: está no `trocar_codigo.sh` (achado 1).
    - Os outros são raros, e alguns estão na lista de "não pega" da própria K25.

## Para a gerente

- Grave: achado 1. A conferência nova vai barrar toda rodada do GitHub, mesmo depois do passo 2. Ela acusa quatro
  lugares nos scripts da rodada, e um deles é falso alarme. Precisa de decisão e conserto antes de juntar.
- Médios: achados 2, 3, 4 e 5. O mais importante é o 2: há o mesmo erro hoje em `core/testes_a_distancia.py`, e ele
  passa calado.
- Pequenos: achados 6 a 15.
- Pode juntar? Ainda não, por causa do achado 1. O resto pode vir junto ou ir para depois, como a gerente escolher.
