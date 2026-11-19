# Passo 0 do plano da parte do Windows: relatório de quem tentou quebrar (19/11/2026)

Feito por um agente verificador que não escreveu nada do passo 0. Eu não mexi no código entregue: os testes que mudam
coisas foram feitos numa cópia temporária e num repositório de prova, os dois fora do projeto.

## Pedido

- Papel: quebrador
- Commit de partida: 39aafbee
- Ramo: passo0-porteiro-2026-11-19

## Arquivos que vou mexer

- `relatorios/passo0-2026-11-19/quem-quebrou/`

## Veredito

**NÃO ESTÁ PRONTO.** A base está boa: as conferências acham os dois defeitos da etapa 5, a recontagem bate (44
lugares em 42 itens), o gancho barra de verdade num git de verdade, e nada do programa mudou. Mas encontrei 19
problemas. Os quatro primeiros pedem conserto antes de a lista ir ao Samuel:

- **Ligar a lista deixa um teste vermelho.** Quando a gerente trocar a lista para "valendo", com o "sim" dele escrito, um
  dos testes novos falha (achado 1).
- **A busca só conhece 13 palavras.** O mesmo pedido ao Windows escrito com outra palavra passa: tarefa criada pelo
  PowerShell em vez do `schtasks`, registro do Windows, `pwsh`, `os.startfile`. Só no programa de hoje, são 73 linhas a
  mais que ficam de fora da lista. Se a busca for ampliada, a lista muda, e essa decisão tem de vir antes do "sim" do
  Samuel (achado 2).
- **A barreira do agente de tela e do rótulo de pronto se apoia no papel que o próprio agente escreve.** Basta o agente
  escrever outro papel no ONDE-PAREI para passar (achado 3).
- **Os papéis se atrapalham.** O rótulo de pronto que quem quebra escreve no ramo de quem construiu faz o formulário de
  quem construiu voltar (achado 5).

Cada achado tem um destino proposto. Muitos deles são "consertar", e conserto ainda não feito não conta como destino
resolvido (D-798; plano, "Regras de todos os passos"). Por isso o veredito é este, e não o rótulo de pronto.

## O que li

- Regras: `.claude/agents/verificador.md`, `CLAUDE.md` inteiro (§11.12 e §11.13 com cuidado), `memoria/INDICE.md`, o
  Livro (`docs/plano/DECISOES.md` desta cópia), com as decisões D-767, D-775, D-784 a D-787, D-791 a D-800 inteiras e
  ainda D-722, D-724, D-771, D-774, D-778, D-781 e D-783 para conferir o pacote do passo 1.
- O plano aprovado: `relatorios/plano-windows-2026-11-18/plano-v3.md` (worktree `plano-windows`), §2 (peça 1), §3
  ("Regras de todos os passos", "Passo 0", "Passo 1") e §6.3.
- A proposta das regras: `git show origin/regras-agentes-2026-11-18:relatorios/regras-agentes-2026-11-18/proposta.md`
  (§5.1, as 24 conferências; §6, os seis campos) e o esboço `esbocos/conferir_codigo.py` do mesmo ramo.
- A entrega, ramo `passo0-porteiro-2026-11-19`, ponta `39aafbee`, saída de `746dbda6` (16 commits): o
  `relatorios/passo0-2026-11-19/ONDE-PAREI.md`, todo o `regras_dos_agentes/` (16 arquivos), os seis
  `tests/test_conferencias_*.py`, `tests/conferencias_excecoes.json`, `ganchos/pre-commit`,
  `relatorios/passo0-2026-11-19/anexos/pacote-passo1.md` e o texto para o Samuel (`.md`, `.html` e a imagem `.png`).
- O script do GitHub que troca o código (`origin/claude/list-server-files-gkos8v:.github/scripts/trocar_codigo.sh`) e a
  rodada 44453253677 (`gh run view`: terminada, "success").

## O que conferi nas falhas, nas peças de fora e nos caminhos

**Como conferi.** Rodei os comandos do pacote na cópia da entrega e fiz uma recontagem minha, com um script
independente que não usa o código do porteiro. As provas que mudam coisas rodaram numa cópia temporária, um clone
local do ramo, e num repositório de git de prova com um `.venv` próprio. Os dois ficam na pasta temporária da sessão,
fora do projeto. Em nenhum deles liguei o gancho no repositório principal.

- **As conferências no código de hoje** (`python -m regras_dos_agentes porteiro`, 11 s): 44 achados.
  - **O defeito 1 da etapa 5 é achado.** O "Reiniciar agora" lança o PowerShell com `DETACHED_PROCESS`. Saem a K02 em
    `atualizacao.py:968` (`_lancar_escondido`) e em `atualizacao.py:674`, e a K01 em `atualizacao.py:965`, por causa
    do `powershell.exe`.
  - **O defeito 4 é achado.** A tranca da pasta feita à mão (`icacls ... /inheritance:r`, `/setowner`) sai como K03
    em `core/testes_a_distancia.py:368` e `:369`.
  - **Os 13 lugares que o esboço perdia também saem.** Rodei o esboço da proposta (sem as exceções dele) no mesmo
    código: ele acha 12 lugares da K01. O porteiro novo acha 26. A diferença são 14 linhas: as 13 que o plano previa
    (`atualizacao.py` 883 e 965; `core/_testes_a_distancia_windows.py` 55, 86, 89, 90, 94 e 153;
    `core/testes_a_distancia.py` 304; `empacotar.py` 527; `teste_velocidade.py` 391 e 392; `avaliar.py` 1659), mais a
    linha `class _SHELLEXECUTEINFO` (`core/_testes_a_distancia_windows.py:61`).
- **A recontagem da lista. Bate: 44 lugares em 42 itens.**
  - Por conferência: K01 26, K02 2, K03 2, K04 14.
  - Por passo: 2 → 1; 3 → 14; 4 → 21; 5 → 3; depois da entrega → 5.
  - São 42 itens porque a linha `| getattr(subprocess, "DETACHED_PROCESS", 0))` aparece duas vezes em
    `atualizacao.py`, e cada uma das duas conferências que a acham (K01 e K02) a guarda como um item só, com "quantas: 2".
  - Os 43 do plano mais a linha da `class _SHELLEXECUTEINFO` dão os 44. O resto bate com a tabela do plano, passo a
    passo.
  - A K04 recontada por mim dá os mesmos 14. O comentário da folha de estilo (`ui/estilo.py:449`) fica de fora, como
    manda a correção 3. Os números de decisão do `teste_botoes.py` também ficam de fora, e é certo: aquilo não é tela do
    Kaique.
  - Texto montado em pedaços: nenhum no programa de hoje.
  - **O que fica de fora da lista, e não é pedaço:** as outras palavras para a mesma coisa (achado 2). São 73 linhas a
    mais no programa.
- **Erro novo num arquivo que já tem exceção: barra.** Na cópia, com a lista trocada para "valendo", acrescentei ao
  `atualizacao.py` a mesma linha do `DETACHED_PROCESS` pela terceira vez: barrou (K01 e K02), código 1. Com outro texto
  (`["schtasks", "/Run", "/TN", "outra"]`) também barrou. Mas a mesma linha **mudada de função**, com a mesma contagem,
  passa (achado 11).
- **O agente de tela mexendo em `core/` fora do pedido (K13): barra**, como diz a D-796 (`core/filtros.py`, "o agente
  de tela mexeu em core/ sem o pedido nomear o arquivo"). Mas o mesmo trabalho, com o agente escrevendo "implementador"
  no lugar de "layout", passa: só um aviso (achado 3). E o agente de tela mexendo no `atualizacao.py` e no `modelos.py`
  também passa (achado 4).
- **"PRONTO PARA CONFERIR" no ramo de quem construiu (K10): barra quando está em maiúsculas.** Passa entre aspas, entre
  crases, e numa linha numerada como `3. **Pronto para conferir**` (achado 15). E barra também o relatório legítimo de
  quem quebra, quando ele fica no mesmo ramo (achado 5).
- **A lista como "valendo" sem o "sim".** A linha de comando diz "não deu para conferir" e sai com o código 3; os
  testes de `tests/test_conferencias_excecoes.py` falham (4 de 11). Está certo. Com o "sim" escrito, o porteiro passa,
  mas um teste falha (achado 1). E um "sim" inventado ("x", "x") também é aceito (achado 6).
- **O gancho num repositório de prova, com o git de verdade e a mesma configuração de quebra de linha deste PC.**
  - Barra o arquivo novo com `DETACHED_PROCESS`, o `git commit -a` e o `git commit -- caminho`, mesmo com outro arquivo
    já no índice: código 1, com a linha e o motivo.
  - Deixa passar o commit que só muda um `.md`.
  - Sem o Python do projeto, barra e diz onde procurou.
  - Sem a lista no índice, barra com o código 3.
  - **Quando a pasta `ganchos/` falta no ramo, o commit com `DETACHED_PROCESS` passa calado.** Isso está escrito no
    ONDE-PAREI.
  - **O agente que põe o próprio erro na lista, no mesmo commit, passa no gancho e no teste do repositório** (achado 7).
- **O pacote do passo 1** traz as regras de Windows: a peça única, a lista das falhas, peça de mentira não prova, a
  D-785, a leitura da peça de fora. As decisões estão certas no essencial (D-767, D-775, D-782, D-780, D-733, D-785,
  D-791, D-796, D-798, D-605, D-637). Faltam duas que o passo 1 toca (achado 18).
- **As peças de fora (F7 do formulário).**
  - Conferi a leitura do git na prática. O gancho rodou no Windows a partir do arquivo tirado pelo git com as quebras
    de linha do Windows, e o `git commit -a` e o `git commit -- caminho` usam o índice certo (o gancho herda o
    `GIT_INDEX_FILE`), como a documentação do githooks diz.
  - A frase "pular com --no-verify é proibido aos agentes (CLAUDE.md, git)" não está no CLAUDE.md nem nos arquivos dos
    agentes (achado 16).
  - A leitura do registro do GitHub (a K21) bate com o script `trocar_codigo.sh` lido por mim.
- **O teste de reversão do conserto da K21.** Com o `formulario.py` de `e2fad264~1`, o teste
  `test_k21_vale_a_rodada_do_ultimo_commit_mesmo_citada_antes_de_uma_antiga` falha. Com o de hoje, passa. Está provado.
- **O formulário da própria entrega**, conferido com o GitHub: passa na etapa "antes de quem quebra", código 0, mas só
  com o aviso "o pedido não foi comparado com o pacote da gerente" (achado 3).
- **Nada mudou fora do combinado.** `git diff --name-status 746dbda6 HEAD` mostra só os 29 arquivos novos (A), todos em
  `regras_dos_agentes/`, `ganchos/`, `relatorios/passo0-2026-11-19/`, `tests/test_conferencias_*` e
  `tests/conferencias_excecoes.json`. Nada em `core/`, `ui/`, na raiz do programa, em `.claude/`, no `CLAUDE.md`, em
  `docs/plano/`, nem em teste antigo. Não há `core.hooksPath` ligado no repositório principal nem nesta cópia.
- **Arquivos sem linha na tabela:** nenhum (`python -m regras_dos_agentes tabela`, 0). Dos arquivos que o plano cita,
  só ficam de fora `motor.json`, `motor-exigido.json` e `preparo.txt`, que são dados gerados, não arquivos do git.
- **Peça duplicada de git e GitHub:** não achei. Só `conversa_com_o_git.py` e `conversa_com_o_github.py` chamam o `git`
  e o `gh`. Mas há listas duplicadas (achado 13).

## Caminhos que o outro não listou

Procurei no código, não no formulário.

- **Outros nomes para a mesma conversa com o Windows, em linhas do programa que a K01 não vê** (achado 2):
  - `atualizacao.py:435`, a função `_dono_do_arquivo`, que lê o dono do arquivo pelo `advapi32`. É "ler como o Windows
    está", coisa da peça 1.
  - `atualizacao.py:1194` a `:1263`, leituras do registro do Windows com `winreg`.
  - `atualizacao.py:931` (`Get-ScheduledTask`), `:942` e `:1435` (`Start-Process`).
  - `core/testes_a_distancia.py:343` (`Register-ScheduledTask`), `:414` (`Set-Service`), `:434` a `:445`
    (`New-LocalUser`, `Add-LocalGroupMember`), `:451` (registro), `:419` e `:422` (`Disable-` e `Remove-NetFirewallRule`).
  - `historico.py:199` e `:212` (`os.startfile`, inclusive o "imprimir").
  - `core/nucleos.py:78`, `core/ocr_comum.py:211` e `ui/brasao_girando.py:225` (o `kernel32`).
  - `teste_velocidade.py`: 16 linhas com `winreg`, `WinDLL` e `Get-CimInstance`.
- **O instalador antigo** (`instalador.iss:272`) roda o `vc_redist` com `Exec`. O porteiro só lê `.py` (achado 17).
- **Textos que o Kaique vê dentro de `core/`.** Os avisos do "Para revisar" moram em `core/analise.py:187`, e a K04
  (número de decisão) e a K05 (emoji) não olham ali (achado 9).
- **Agente de tela fora de `ui/` nos arquivos do programa da raiz** (`atualizacao.py`, `modelos.py`,
  `historico_acoes.py`): a K13 não olha (achado 4).
- **Testes antigos da raiz** (`teste_botoes.py`): a K11 não olha (achado 14).
- **Arquivo novo de `core/` no pedido.** O texto do pedido não é lido, e o arquivo novo não ganha as regras de Windows
  (achado 12).
- **Quem tenta quebrar, conferido pelo comando `entrega`.** Só passa se a partida dele for a ponta do ramo de quem
  construiu; senão a K13 acusa os arquivos do construtor como se fossem dele. Isso não está escrito em lugar nenhum
  (achado 5).

## Falhas não pensadas e resultado não conferido

**Falhas não pensadas** (fora do "O que pode falhar" da entrega):

- **Ligar a lista legitimamente quebra um teste** (achado 1).
- **O teste que barra o repositório nunca rodou no GitHub.** Ele fica pulado enquanto a lista é "proposta". A leitura
  do repositório inteiro na cópia que o GitHub monta (o `trocar_codigo.sh` deixa a pasta `.github/` do ramo dos testes
  no índice) só vai ser provada na primeira rodada depois do "sim". Sugestão: antes de levar a lista ao Samuel, uma
  rodada do GitHub num ramo de prova com a lista "valendo". Ela teria mostrado o achado 1.
- **Mexer numa linha da lista sem consertá-la vira erro novo.** Isso inclui mudar a linha de arquivo, renomear uma
  variável nela ou reformatá-la. E esse erro novo só sai com o "sim" do Samuel (achado 11).
- **Um `"pasta/*"` seguido de um `"*/"` mais adiante cega a K04 no trecho entre os dois** (achado 10).
- **O commit de junção (merge) não passa pelo gancho do git** (o `pre-commit` não roda nele). A gerente junta ramos sem
  essa conferência; o GitHub cobre depois. Fica como ressalva.
- **O agente pode afrouxar o próprio porteiro.** Pode tirar uma palavra da busca, mudar o passo de um item, ou trocar
  "proposta" por "valendo" com um "sim" inventado (achado 6).

**Resultado não conferido** (§11.12, ponto 2):

- **O comando `entrega` sem `--pacote` sai com 0** e aceita o papel que o próprio agente escreveu (achado 3).
- **O `sim_do_samuel` aceita qualquer texto.** Ninguém confere que as palavras estão no Livro (achado 6).
- **A K18 diz "o último commit já está no GitHub" olhando a cópia local** (`@{upstream}`, "o último buscado"), sem
  perguntar ao GitHub (achado 19).
- **"Só diminui" só é conferido pela K17 do formulário**, rodada à mão pela gerente. O GitHub e o gancho não conferem
  (achado 7).

## As regras que conferi

- **CLAUDE.md §11.12, os seis pontos.**
  - (1) Peça única de git e GitHub: cumprida. Mas há listas escritas à mão em mais de um lugar (achado 13).
  - (2) Nada dado como feito sem conferir: pela metade (achados 3, 6, 7 e 19).
  - (3) Lista das falhas: existe, mas faltaram casos (achados 1, 10 e 11).
  - (4) Peça de mentira: cumprida. O git é de verdade e nada mexe no Windows.
  - (5) Não se aplica a mim.
  - (6) Leitura da peça de fora: conferida (achado 16, sobre a citação errada).
- **CLAUDE.md §11.13** (o texto para o Samuel): regra 1 cumprida. Regra 2 quase: "peça única" é palavra de dentro, mas
  ele já a ouviu. Regras 3 e 4 não cumpridas: a imagem é o próprio texto, não prova nada, e não há caso real. Regra 6
  cumprida, mas sem dizer o que acontece se ele disser "não". Regra 9 falta no `.md`, embora exista no ONDE-PAREI.
  Regra 7: o texto é curto. Ainda: "barra qualquer erro novo" promete mais do que o porteiro faz (achado 8).
- **Cada decisão tocada:**
  - D-767: cumprida.
  - D-775: pela metade (achado 5).
  - D-784: cumprida, com o achado 12.
  - D-785, D-786 e D-787: cumpridas.
  - D-791: pela metade (achados 1, 2, 6 e 7).
  - D-792: cumprida, com o achado 3.
  - D-793: cumprida (a K23 passa nos quatro agentes).
  - D-796: pela metade (achados 3 e 4).
  - D-797: cumprida.
  - D-798: pela metade (achados 5 e 15).
  - D-799: pela metade (o passo 0 está feito, com os achados acima).
  - D-800: cumprida (o teste cobra que só os 5 ficam para depois).
  - D-605: cumprida (nenhum teste antigo mudou).
  - D-637: cumprida (nada muda para o Kaique nem no PDF).
- **Regras do catálogo:** a R113 (K01 a K03), a R120 (K04), a R031 (K10), a R071 (K13), a R102 (K11), a R056 e a R094
  (K17) e a R136 (K18). Não se aplicam a este passo: as de imagem, de filtro e de tela (nenhum arquivo do programa mudou).

## Achados

1. **Grave: ligar a lista deixa um teste vermelho.** O teste `test_a_lista_valendo_sem_o_sim_do_samuel_nao_vale`
   (`tests/test_conferencias_excecoes.py:82`) monta o caso trocando `"situacao": "proposta"` no texto do arquivo real
   da lista. Com a lista já "valendo" e o "sim" escrito, a troca não acontece, e o teste falha. Provado na cópia: 1
   falha, 10 passam. Consequência: no dia do "sim", o GitHub fica vermelho. E consertar nesse momento seria mudar um
   teste antigo (K11, D-605). Destino: consertar antes de juntar (o teste monta a lista dele com dados próprios). Junto,
   uma rodada do GitHub com a lista "valendo" num ramo de prova.
2. **Grave: a busca da conversa com o Windows conhece poucas palavras, e a lista que vai ao "sim" depende disso.**
   (`regras_dos_agentes/porteiro.py:153`).
   - Na cópia, de 14 jeitos de pedir a mesma coisa com outro nome, só 1 foi barrado. Passaram: `pwsh`;
     `Register-ScheduledTask`, que é o mesmo que o `schtasks`; `takeown`, o mesmo que o `/setowner`; `msiexec`;
     `reg add` e `winreg`; `os.startfile`, o mesmo que o `ShellExecute`; `windll.advapi32`; `creationflags=0x8`, o
     mesmo número do `DETACHED_PROCESS`; `New-LocalUser`; `Set-Service`; `cmd /c start`; e os textos em pedaços.
   - No programa de hoje, são 73 linhas a mais. Algumas são do próprio plano: tarefas, registro, o dono do arquivo em
     `atualizacao.py:435` e as contas e serviços em `core/testes_a_distancia.py:343` a `:451`. Outras estão fora do
     plano: `historico.py:199` e `core/nucleos.py:78`.
   - Destino: pergunta. A gerente decide o alcance técnico, mas a lista que vai ao Samuel muda. Sugestão: ampliar com
     o que o plano já chama de peça 1 (tarefas por qualquer meio, registro, PowerShell com qualquer nome, `ShellExecute`
     com qualquer nome, licença e dono de arquivo, o número do `DETACHED_PROCESS`), recontar, e só então levar a lista.
     O que fica de fora (memória, prioridade do processo) vai escrito, com o motivo.
3. **Médio: o papel do agente é o que ele mesmo escreve.**
   - Sem `--pacote`, a comparação com o pedido da gerente vira só aviso, e a saída é 0
     (`regras_dos_agentes/formulario.py:512`).
   - Provado na cópia: um agente de tela que se declara "implementador" mexe no `core/filtros.py` sem ser barrado.
   - Quem se declara "quebrador" pula o formulário inteiro (`regras_dos_agentes/formulario.py:528`) e fica livre para
     escrever o rótulo de pronto.
   - Destino: consertar (sem `--pacote`, "não conferido", código 3).
4. **Médio: a K13 só barra o agente de tela em `core/`** (`regras_dos_agentes/porteiro_mudancas.py:177`). A D-796 diz
   "sem isso escrito no pedido, continua só em `ui/`". Provado na cópia: o agente de tela mexendo no `atualizacao.py` e
   no `modelos.py` recebe só o aviso K14. Destino: consertar (barrar o agente de tela em qualquer arquivo do programa
   fora de `ui/` que o pedido não nomeou). Se a gerente preferir outro limite, vira pergunta.
5. **Médio: a convenção "o relatório de quem quebra vai para o ramo de quem construiu" bate com a K10.**
   - A K10 lê todas as linhas novas do ramo com o papel de quem construiu (`regras_dos_agentes/porteiro_mudancas.py:88`).
     Então o rótulo de pronto que quem quebra escreve no próprio relatório (D-798; plano: "Ele só escreve com o próprio
     relatório") faz o formulário de quem construiu voltar. Provado na cópia.
   - Também não está escrito que a partida do relatório de quem quebra tem de ser a ponta do ramo. Sem isso, a K13
     acusa os arquivos do construtor.
   - Por causa disso, este relatório só escreve o rótulo entre aspas.
   - Destino: consertar. A K10 deixa de fora a pasta `quem-quebrou/` quando o relatório ali é de quem quebra ou do
     verificador, e as duas regras ficam escritas no `regras_dos_agentes/formulario.py:19`.
6. **Médio: o porteiro e a lista não estão protegidos contra o próprio agente.**
   - Os arquivos que só a gerente muda não incluem `regras_dos_agentes/` nem `ganchos/`
     (`regras_dos_agentes/porteiro_mudancas.py:40`). Da lista, só se acusa item novo e a volta de "valendo" para
     "proposta" (`regras_dos_agentes/porteiro_mudancas.py:220`).
   - Provado na cópia: tirei o `schtasks` da busca, escrevi um `schtasks` novo, rodei `--diminuir` (a lista caiu de 44
     para 39), troquei para "valendo" com um "sim" inventado e mudei o passo de um item. O porteiro passou, e o
     formulário só deu avisos K14.
   - O GitHub pegaria esse caso só porque há exemplo de `schtasks` nos testes e porque um teste confere quais itens
     ficam para depois da entrega. Uma palavra sem exemplo ficaria desprotegida.
   - O "sim" aceita qualquer texto (`regras_dos_agentes/excecoes.py:99`).
   - Destino: consertar (pôr o porteiro, o gancho e a situação, o "sim" e o passo da lista entre os arquivos
     protegidos, e conferir o "sim" no Livro).
7. **Médio: "só diminui" não é conferido no GitHub nem antes do commit.** O gancho lê a lista do próprio commit
   (`regras_dos_agentes/__main__.py:43`). O agente que põe o erro novo dele na lista, no mesmo commit, passa no gancho e
   no teste do repositório. Provado no repositório de prova. Só a K17, rodada à mão pela gerente, acusa. Destino:
   pergunta à gerente. Ou um teste do GitHub compara a lista com a da versão de teste, ou fica escrito que o comando
   `entrega` com `--pacote` é obrigatório antes de juntar.
8. **Médio: o texto para o Samuel não segue o §11.13.**
   - A imagem é o próprio texto: não prova nada e não mostra caso real (`relatorios/passo0-2026-11-19/lista-de-excecoes-para-o-samuel.md:5`).
   - A frase "barra qualquer erro novo" promete mais do que o porteiro faz (achados 2 e 11).
   - Falta "de onde veio" no `.md`, e não diz o que acontece se ele disser "não".
   - Destino: consertar. Usar um caso real (por exemplo, a dica do Automático com o número, circulada em vermelho),
     dizer em uma frase o que ele não pega, e recontar depois do achado 2.
9. **Baixo: a K04 e a K05 não olham `core/`**, mas os avisos do "Para revisar" que o Kaique lê moram em
   `core/analise.py:187` (`regras_dos_agentes/porteiro.py:133`). Hoje há zero achados ali, então ampliar não muda a
   lista. Destino: consertar.
10. **Baixo: a correção 3 vale para qualquer texto, não só para a folha de estilo.** Um `"imagens/*"` seguido de um
    `"*/fim"` apaga da busca o que está entre os dois (`regras_dos_agentes/leitura_do_codigo.py:114`). Provado: o
    "D-731" de uma tela de exemplo deixou de ser achado. Destino: consertar (tirar o comentário só dentro do mesmo texto
    da folha de estilo).
11. **Baixo: o lugar é identificado pelo texto da linha** (`regras_dos_agentes/excecoes.py:60`).
    - A mesma linha mudada de função passa. Provado na cópia: o `DETACHED_PROCESS` tirado de `_lancar_escondido` e
      posto numa função nova.
    - Mexer numa linha da lista sem consertá-la vira erro novo, que só sai com o "sim" do Samuel. Isso vale para mudar
      a linha de arquivo, renomear uma variável nela ou reformatá-la.
    - Destino: não é defeito, é o combinado no plano (arquivo, conferência, texto e quantas). Mas tem de ir nas
      ressalvas e no pacote dos passos 2 a 5.
12. **Baixo: o pedido não é lido para arquivo novo.** O docstring promete (`regras_dos_agentes/tabela_arquivos.py:10`),
    mas o código lê só o conteúdo, que não existe para arquivo novo (`regras_dos_agentes/tabela_arquivos.py:199`).
    Provado: `novo:core/registro_do_windows.py` sai só com as etiquetas de imagem e de git, sem as regras de Windows e
    sem a pergunta "O que pode falhar". Destino: consertar (ou o código lê o pedido, ou o docstring diz que a gerente
    acrescenta a linha na tabela antes).
13. **Baixo: listas escritas à mão em mais de um lugar** (§11.12: "uma lista é escrita uma vez e importada").
    - O que é "conversa com o Windows" está em dois lugares, e as duas listas diferem
      (`regras_dos_agentes/porteiro.py:153` e `regras_dos_agentes/tabela_arquivos.py:142`).
    - Os nomes `terceiros` e `velhos` estão em três (`regras_dos_agentes/porteiro.py:144`,
      `regras_dos_agentes/porteiro_mudancas.py:147` e `regras_dos_agentes/formulario.py:180`).
    - Quem pode escrever o rótulo de pronto está em dois (`regras_dos_agentes/porteiro_mudancas.py:37` e
      `regras_dos_agentes/formulario.py:436`).
    - Destino: consertar.
14. **Baixo: a K11 não olha os testes da raiz**, como o `teste_botoes.py`, que é teste antigo pelo CLAUDE.md §4.5
    (`regras_dos_agentes/porteiro_mudancas.py:120`). Destino: consertar, ou escrever na ressalva.
15. **Baixo: o rótulo de pronto passa entre aspas, entre crases ou numa linha numerada** (`3. **Pronto para conferir**`)
    (`regras_dos_agentes/porteiro_mudancas.py:45` e `:66`). A ressalva da entrega só fala do "meio da frase". Destino:
    não é defeito, porque as aspas existem para citar a regra. Mas a ressalva tem de dizer isso.
16. **Baixo: textos que não batem com a verdade.**
    - `regras_dos_agentes/porteiro.py:9` cita `antes_do_commit.py`, que não existe.
    - `ganchos/pre-commit:11` diz que "--no-verify é proibido aos agentes (CLAUDE.md, git)", e nem o CLAUDE.md nem os
      arquivos dos agentes dizem isso.
    - O ONDE-PAREI diz "17 arquivos" em `regras_dos_agentes/`, e o git tem 16.
    - Destino: consertar (a regra do `--no-verify`, se for para valer, é da gerente com o "sim" do Samuel).
17. **Baixo: o instalador antigo conversa com o Windows fora do Python** (`instalador.iss:272`, `Exec` do
    `vc_redist`), e o porteiro só lê `.py`. Destino: pergunta à gerente. Se o Inno não é mais usado, não é defeito.
18. **Baixo: o pacote do passo 1** (`relatorios/passo0-2026-11-19/anexos/pacote-passo1.md:1`).
    - Faltam a D-722 (a lista do que foi desfeito no fim da sessão de prova, que cria uma tarefa e uma pasta) e a D-724
      (a assinatura grátis, de onde vem a faixa "Editor desconhecido" que o passo 1 prova).
    - A regra da barra de rolagem ("#a8a49e") contradiz os valores que a K22 cobra.
    - Destino: a gerente decide ao remontar o pacote (as duas decisões). O texto da barra é do CLAUDE.md §9: vira
      pergunta.
19. **Baixo: a K18 confere o GitHub pela cópia local** (`regras_dos_agentes/conversa_com_o_git.py:168`, "o último
    buscado"). Destino: não é defeito grave. Escrever na ressalva, ou perguntar ao GitHub de verdade (`git ls-remote`).

## Para a gerente: o que ficou fora do projeto

Criei, na pasta temporária da sessão (fora do projeto; não apaguei, pela regra de 29/09):

- `C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\quebrar\copia`:
  um clone local do ramo, com uns 3,3 GB. Tem os ramos de prova `prova-k13`, `prova-k10`, `prova-k17` e
  `prova-ligar`, só nele.
- `...\quebrar\gancho`: o repositório de prova do gancho, com o `core.hooksPath` ligado só nele.
- `...\quebrar\esboco`, `recontar.py` e `largo.py`: o esboço da proposta e os meus scripts de recontagem.

A gerente pergunta ao Samuel se pode apagar.
