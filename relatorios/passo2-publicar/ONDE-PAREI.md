# Passo 2 do plano da parte do Windows: publicar, o motor do Kraken à parte e o servidor das versões de prova (19/11/2026)

Implementador. Ramo `passo2-publicar-2026-11-19`, worktree `.claude/worktrees/passo2`, saiu de `03c91599` (a versão de
teste com o passo 1 e o porteiro ligado). Este ONDE-PAREI é também o formulário da entrega (D-792).

## Pedido

- Papel: implementador
- Commit de partida: 21f1fc50
- Ramo: passo2-publicar-2026-11-19

## Arquivos que vou mexer

- `publicar_versao_kaique.py`
- `empacotar.py`
- `montar_motor_kraken.py`
- `compilar_detector_gravura.py`
- `core/ocr_kraken.py`
- `core/windows.py`
- `atualizacao.py`
- `tests/test_windows_peca.py`
- `tests/test_empacotar.py`
- `tests/test_publicar_*.py`
- `tests/test_motor_kraken*.py`
- `tests/test_ocr_kraken*.py`
- `relatorios/passo2-publicar/`

(Volta 8, 20/11/2026: as duas seções acima são as do pacote da volta 8, `anexos/pacote-volta8.md`, copiadas sem mudar.
As das voltas anteriores (`anexos/pacote-volta7.md`, `anexos/pacote-volta6.md`, `anexos/pacote-volta4.md` e a primeira
entrega, de `03c91599`) estão nos pacotes e no `git log` deste arquivo.)

## Onde parei

- 19/11: leitura feita (pacote, CLAUDE.md, memória e catálogo dos erros F4, F5, F9, plano-v3 passo 2 e peças 8, 9 e
  10b, plano v1 peça 8, estudo do Kraken, estudo de publicar rápido, o código de hoje, o código do vpk 1.2.161, o do
  Velopack do lado do programa, o do `gh`). Seções de antes de escrever preenchidas.
- 19/11: código e testes feitos, em commits pequenos (lista em "Commit"). Prova de reversão: 19 de 19 proteções
  acusadas pelo seu teste (`anexos/reversao-resultado.txt`); os testes novos falham no código antigo
  (`anexos/reversao-codigo-antigo.txt`). Rodada do GitHub 44748591841: success (terceira tentativa; em "Testes").
- `git -C D:\programas\EditorImpressao rev-parse --is-shallow-repository` = false antes e depois. Nenhum atalho de
  pasta (junção) foi criado: nada foi montado de verdade (o vpk e o PyInstaller ficam para a prova à vista).
- 19/11: a rodada 1 do GitHub (44642471223) achou um defeito de verdade: no Windows do GitHub o PowerShell aberto pela
  peça herdava os módulos do PowerShell 7 e não lia a assinatura digital. Consertado na peça (`fa28ab5b`), com teste de
  reversão que refaz o caso no PC (falhou antes do conserto, passa depois). Achado junto, sem consertar (não é deste
  passo): o lançar solto dá "saiu sem começar" para um script rápido (Lista de bugs, em "Ideias e bugs").
- 19/11: pedido da gerente (D-809, D-811, D-812, D-814): consertado o apagar do lançar solto (`64ed0c01`) e o
  apagar do destino com atalho (`0ef0da17`), com testes que falham sem o conserto; as três seções novas do formulário.
- 19/11 (noite): quem tentou quebrar devolveu (volta 1, `quem-quebrou/relatorio-1.md`, commit `a58f181b`): 11
  achados. A gerente pediu o conserto de todos (o 4 por decisão técnica dela, D-014). **Feita a volta 2** (`17cd8635`,
  `85781a08`): os 11 achados com destino em "O que o agente que tentou quebrar achou", cada conserto com o teste que
  falha sem ele (`anexos/reversao-volta2-resultado.txt`). **Próximo:** a gerente manda a quem tenta quebrar de novo.
- **Próximo (antes):** a gerente manda a quem tenta quebrar; depois a prova à vista (o roteiro está em "A prova de verdade").
- 20/11, **volta 3 (agente novo, D-815)**: começo pelo relatório 2 de quem tentou quebrar (`quem-quebrou/relatorio-2.md`,
  10 achados). Pedido da gerente: consertar 1 a 9 pela causa, com teste que falha sem o conserto (D-811), e anotar o 10
  para o passo 3. Leitura feita (implementador, CLAUDE.md, memória, catálogo, pacote, este formulário, os dois
  relatórios, o Livro D-809 a D-815). Andamento em "Volta 3" abaixo de "O que o agente que tentou quebrar achou".
- 20/11, volta 3 feita: os 10 achados do relatório 2 com destino em "O que o agente que tentou quebrar achou"
  (código em `411b46c7`, `d628be0e`, `1b430752`, `4817c2f4`, `05f743ca`, `e4263c0a`, `2e906e94`); cada conserto com o teste que falha sem ele
  (`anexos/reversao-volta3-codigo-antigo.txt`: os testes novos falham no código da volta 2; `anexos/reversao-volta3-resultado.txt`:
  24 de 24 proteções desligadas numa cópia, todas acusadas). `--is-shallow-repository` = false antes e depois; nenhuma
  junção criada. **Próximo:** a gerente manda a um agente novo que tenta quebrar (D-815); depois a prova à vista.

- 20/11, **volta 4 (agente novo, D-815)**: começo pelo relatório 3 de quem tentou quebrar (`quem-quebrou/relatorio-3.md`,
  12 achados). Pedido da gerente: consertar 1 a 4, 6 a 11 (o 1 pela D-816), anotar o 5 como limite da peça e o 12 para a
  Lista de bugs. Leitura feita (implementador, CLAUDE.md, memória, catálogo, pacote da volta 4, este formulário, o
  relatório 3 e os anexos Q1 a Q3 e E2). Andamento em "Volta 4" de cada seção.
- 20/11, volta 4 feita: os 12 achados com destino em "O que o agente que tentou quebrar achou" (código em `783b6814`,
  `dfe5f70d`, `e0921ed8`, `9384f1a3`, `595cc293`); reversão no código de `5f96975b` (26 de 27 casos novos falham) e 24 de 24
  mutações acusadas. Rodada do GitHub 44748591841: success (terceira tentativa; em "Testes"). `--is-shallow-repository` = false antes e depois;
  nenhuma junção criada. **Próximo:** a gerente manda a um agente novo que tenta quebrar (D-815); depois a prova à vista.

- 20/11, **volta 5 (o mesmo escritor da volta 4; a segunda e última volta dele, D-815)**: começo pelo relatório 4 de
  quem tentou quebrar (`quem-quebrou/relatorio-4.md`, 9 achados: 1 médio, 5 baixos, 3 observações) e pelos anexos
  `quem-quebrou/anexos-4/` (Q1 a Q4, E5). Pedido da gerente: consertar 1 a 6 (o 4 e o 5 pelas escolhas técnicas dela),
  e só anotar as observações 7 a 9. Partida do código: `595cc293` (a ponta do ramo é `277fe8fd`; depois de `595cc293`
  só mudaram documentos). Andamento em "Volta 5" de cada seção.

- 20/11, **volta 6 (escritor novo, D-815)**: o defeito achado na prova à vista de 20/11 (14h33 a 14h39 no relógio do
  Samuel): o publicar montado do zero para em "a pasta do programa não serve: ... não tem o Visual C++ em instalar\",
  e os 3 achados baixos do relatório 5 de quem tentou quebrar (o Samuel: "pode concertar"). Partida `b9300da8`. Leitura
  feita (implementador, CLAUDE.md, memória: índice, atualizador, catálogo; o pacote da volta 6; o Livro D-727, D-767,
  D-773, D-776, D-777, D-785, D-788, D-789, D-795, D-815 a D-817; o relatório 5; o registro da prova, só lido). O plano
  (D-709) está em "A causa, a regra e todos os caminhos", "Volta 6", escrito antes de mexer. Andamento em "Volta 6" de
  cada seção.
- 20/11, volta 6 feita: plano `3abc3953`; testes antes do código `a07f22b8`; código `3abf9acf`. Reversão no código de
  `b9300da8`: 7 de 8 casos novos falham (o do achado 1 cobra uma proteção que já existia; provado pela mutação Y7);
  mutações: 10 de 10 acusadas. `--is-shallow-repository` = false antes e depois; nenhuma junção criada; a junção
  `modelos` da gerente e a pasta `dist\` não foram tocadas (só lidas). **Próximo:** a rodada do GitHub (em "Testes") e
  a entrega à gerente; depois um agente novo tenta quebrar (D-815) e a prova à vista (itens 13 a 15).

- 20/11, **volta 7 (o mesmo escritor da volta 6; a segunda e última volta dele, D-815)**: o relatório 6 de quem tentou
  quebrar (`quem-quebrou/relatorio-6.md`, "NÃO ESTÁ PRONTO": 1 médio, 4 baixos, 5 observações) e a D-818 do Samuel
  ("vai ter que reprogramar?" · "A"). Partida `db4b377a` (`git pull` feito). Lido: o relatório 6 inteiro e os anexos
  `quem-quebrou/anexos-6/` (sondas S1 a S5, mutações Z1 a Z11), o pacote da volta 7 e a linha da D-818 no Livro. O
  plano (D-709) está em "A causa, a regra e todos os caminhos", "Volta 7", escrito antes de mexer. Pasta de rascunho
  nova: `v7\` (a `v6\` e a `quebra6\` não são tocadas).
- 20/11, volta 7 feita: plano `0867fe57`; testes antes do código `8a02ecca`; código `4e8fdd98`; mais dois casos de prova
  `25c514ad`. Reversão no código de `db4b377a`: 9 de 12 casos novos falham, e os 88 antigos (com a pasta de mentira
  nova) passam lá; mutações: 11 de 12 acusadas (a R12 é dupla proteção). `--is-shallow-repository` = false antes e
  depois; nenhuma junção criada. **Próximo:** a rodada do GitHub (em "Testes") e a entrega à gerente.

- 20/11, **volta 8 (escritor novo, D-815)**: os 2 defeitos da prova à vista de 20/11 (18h a 19h30 no relógio do
  Samuel: as peças procuradas no lugar errado quando o publicar roda de uma cópia de trabalho; a frase depois de
  apagar), os 6 baixos do relatório 7 (o Samuel: "pode") e o texto do formulário que o conferidor ainda devolvia.
  Partida `21f1fc50`. Lido: as regras do implementador, o CLAUDE.md inteiro, a memória (índice, atualizador, catálogo
  dos erros F3, F4, F5, F7), o pacote da volta 8, no Livro da `obra-juncao` as linhas inteiras de D-605, D-727, D-767,
  D-773, D-776, D-777, D-785, D-788, D-789, D-795, D-815, D-816, D-817 e D-818, este formulário (Onde parei, Volta 6,
  Volta 7), o relatório 7 inteiro e os registros da prova (`C:\EditorImpressaoProva\prova1.log` a `prova7c.log`, só
  lidos, em UTF-16). Pasta de rascunho nova: `v8\` (as outras não são tocadas). O plano (D-709) está em "A causa, a
  regra e todos os caminhos", "Volta 8", escrito antes de mexer.

- 20/11, volta 8 feita **em parte**: plano `df40b18e`; testes antes do código `44029d6a`; código `b2863630` (a frase do
  `--apagar` saída do lugar único do apagar; a versão do Visual C++ do pacote lida por uma função só, a do publicar,
  usada pelo programa instalado; os testes dos baixos 1 a 3; o roteiro e o texto do formulário). Reversão no código de
  `21f1fc50`: 10 dos 23 casos novos falham lá, e os 98 antigos passam; mutações U1 a U12: 12 de 12 acusadas.
  **O defeito 1 (as peças procuradas no lugar errado numa cópia) parou antes de mexer:** o conserto pela causa pede
  arquivos fora da lista do pacote (a peça do git, um lugar novo em `core/`, o `compilar_st_ferramentas.py`); o pedido
  à gerente está em "Perguntas para o Samuel", Volta 8, e o plano em "A causa, a regra e todos os caminhos", Volta 8.
  `--is-shallow-repository` = false antes e depois; nenhuma junção criada; a pasta errada de 19/11 e a junção `modelos`
  não foram tocadas (só listadas). **Próximo:** a gerente decide a lista do defeito 1 (uma volta 9, minha segunda).

## Decisões que esta tarefa precisa cumprir

- D-767 "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione". Aqui: o publicar
  de verdade (montar no C:, o vpk, o rascunho no GitHub) só conta na prova à vista; os testes automáticos provam a
  lógica com uma pasta de verdade como destino e com um vpk e um `gh` de mentira só para a lógica em volta (escrito
  assim nos testes).
- D-768 "mas dai vai ter que baixar o motor do kraken toda vez e reinstalar ele de novo?" · "vou escolher a 16, vamos
  para a proxima". Aqui: a atualização sai sem o motor; o motor tem publicação própria.
- D-773 "A". Aqui: o servidor das versões de prova (janela pequena e visível; fechar é a internet caindo) e o rascunho
  no GitHub, liberado só na prova e apagado no fim.
- D-775 "o agente vai tentar quebrar antes de fazer o teste real na tela né?" · "ok". Aqui: entrego à gerente sem
  rótulo; a prova à vista vem depois de quem tenta quebrar.
- D-776 "Sim, no C só tem que cuidar para não encher o disco C inteiro". Aqui: o rascunho no C:, a conta do espaço
  antes (reserva de 20 GB), a vigia durante e o rascunho apagado no fim, também com erro.
- D-777 "mas dai vai fazer quais versões?" · "ok, fica assim". Aqui: a atualização sem .msi e sem zip portátil; o .msi
  só quando pedido.
- D-785 "ok, mais ainda existem mais casos na opção A". Aqui: publicar é da lista "sempre à vista" (item 8): não montei
  nada pesado nem publiquei nada; o servidor é janela à vista.
- D-786 "a". Aqui: o passo mexe em `core/ocr_kraken.py`, que o caminho do livro não usa; a gerente decide o filtro de
  velocidade.
- D-788 "1" (a primeira opção). Aqui: o motor numa pasta por versão; o instalador leva o motor como um arquivo só em
  instalar\.
- D-789 "mas iria demorar mais toda vez que eu fosse fazer a compilação né?" · "A". Aqui: sem o pacote de diferença,
  sem baixar a versão anterior.
- D-790 "A". Aqui: antes de liberar uma versão, o publicar confere que o motor que ela pede está publicado e o lê de
  volta (a parte do Kaique é do passo 3).
- D-791 "não sei do que você está falando" · "b". Aqui: o porteiro barra desde o primeiro dia; este passo tira o item
  de `empacotar.assinatura_do_arquivo` da lista no mesmo commit do conserto.
- D-795 "porque fazer isso?" · "porque ter um instalador pequeno então?" · "não tem nenhuma documentação dizendo para o
  que isso serve?" · "ok". Aqui: o Setup.exe é apagado no fim, também com erro; nunca vai ao rascunho do GitHub nem à
  pasta do servidor; a conferência do fim lê a pasta de saída e o destino.
- D-796 "não entendi" · "1, mas tem que ser explissito o pedido né". Aqui: sou implementador; não mexi em `ui/`.
- D-797 "Só precisa de dois lugares né?" · "ok". Aqui: trabalhei no meu ramo; quem junta é a gerente.
- D-798 "fechou". Aqui: não escrevo o rótulo de pronto.
- D-724 "gratis, mas o que é essa assinatura e é segura?". Aqui: o motor é assinado com a mesma chave e conferido pela
  mesma peça (`assinatura.py` não muda), com outro nome de pacote.
- D-727 "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né". Aqui: o motor vai
  dentro do instalador, como um arquivo só.
- D-809 "ok". Aqui: o script lançado solto da peça apaga a pasta de troca sem seguir atalho, e o destino do
  publicar não apaga uma publicação que é atalho (pedido da gerente de 19/11, depois das regras novas).
- D-811 "ok". Aqui: a seção "Cada proteção e o teste que falha sem ela", provada numa cópia.
- D-812 "ok". Aqui: a seção "De onde vem cada dado da conferência".
- D-814 "ok". Aqui: não há pergunta ao Samuel nesta entrega (ver "Perguntas para o Samuel").
- D-807 "ok". Aqui: no PC, só os arquivos de teste que mexi, um por vez; o conjunto inteiro no GitHub.
- D-714 "1 - vamos seguir sua sugestão" · "2- ok". Aqui: publicar continua só quando alguém roda o comando.
- D-763 "ok, pode fazer". Aqui: o nome do pacote do motor é outro (EditorImpressaoMotorKraken) e não é o nome da pasta
  dos projetos.
- D-813 "ok". Aqui (volta 3): a recusa da peça lista o que o Windows aceita como programa (a documentação do
  CreateProcess e do subprocess, e o que foi rodado no PC) e compara a coisa de verdade (o arquivo completado pelo
  Windows e o começo dele), não o texto.
- D-815 "ok". Aqui: a volta 3 é de um agente novo, que começou por este formulário.

**Volta 4 (20/11/2026), as decisões do pedido da gerente:**
- D-816 "A , mas onde estamos antes de você fazer qualquer processo". Aqui: depois do pedido de liberar, o publicar
  nunca apaga nada, em nenhum destino (o GitHub e a pasta das provas), sem depender de leitura; a frase diz o que pode
  ter ficado (liberada ou rascunho), como conferir e o comando de apagar. Antes do pedido de liberar, o erro continua
  apagando o rascunho na hora, como hoje.
- D-815 "ok". Aqui: sou o escritor novo da volta 4 (pode ser também o da volta 5).
- D-767 "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione". Aqui: a peça
  do Windows (o nome com ponto no fim, o grupo com o gh, a gravação no disco) roda de verdade nos testes; o GitHub
  continua de mentira (só a lógica), e o de verdade fica para a prova à vista.
- D-773 "A". Aqui: o rascunho de prova no GitHub, liberado só na prova; a frase nova da D-816 diz como conferir e
  apagar.
- D-775 "ok". Aqui: entrego à gerente; depois um agente novo tenta quebrar, e só então a prova à vista.
- D-776 "Sim, no C só tem que cuidar para não encher o disco C inteiro". Aqui: o download para somar (quando o GitHub
  não dá a soma pronta) vai para o rascunho do C:, pela vigia e na conta do espaço.
- D-795 "ok". Aqui: nada muda no Setup.exe (continua fora do que vai ao destino e apagado no fim).
- D-811 "ok". Aqui: cada proteção nova ou consertada tem o teste que falha quando ela é desligada, provado numa cópia
  (seção "Cada proteção", "Volta 4").
- D-812 "ok". Aqui: a seção "De onde vem cada dado", "Volta 4" (a frase da D-816 não usa leitura nenhuma).
- D-813 "ok". Aqui: o nome do programa como o Windows o completa (lido na Microsoft e rodado no PC: o nome sozinho com
  ponto no fim também roda pelo PATH), uma vez só, e todas as conferências usam esse nome.
- D-798 "fechou". Aqui: nenhum rótulo de pronto.

**Volta 5 (20/11/2026), as mesmas decisões da volta 4, com o que cada conserto toca:**
- D-816 "A , mas onde estamos antes de você fazer qualquer processo". Aqui: o gh que nem abriu no pedido de liberar
  não é pedido (achado 4); então, pela D-816 ("Antes do pedido de liberar, erro no meio continua apagando o rascunho na
  hora"), o rascunho é apagado. Qualquer erro depois de o gh abrir continua sem apagar nada.
- D-773 "A". Aqui: as frases de "já existe" e "sobrou um rascunho" dão o comando de apagar do destino certo (achado 1).
- D-767 "não faça mais nada escodindo ou de mentira". Aqui: o fluxo escondido e o gh fechado por tempo rodam de verdade
  nos testes (um programa de prova); o GitHub continua de mentira só para a lógica.
- D-775 "ok". Aqui: os achados do relatório 4 voltaram a quem escreveu; depois, um agente novo tenta quebrar.
- D-815 "ok". Aqui: é a minha segunda volta, a última permitida.
- D-811 "ok". Aqui: as 10 proteções desta volta desligadas numa cópia, todas acusadas.
- D-812 "ok". Aqui: "pedi" ou "não pedi" vem de qual pedido saiu (o de apagar em si, ou o gh que nem abriu).
- D-813 "ok". Aqui: o que o Windows faz com o ":" de um fluxo, lido na Microsoft e rodado de verdade.
- D-798 "fechou". Aqui: sem rótulo de pronto.

**Volta 6 (20/11/2026), as decisões do pacote da volta 6 (palavras copiadas do Livro, `obra-juncao`):**
- D-727 "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né". Aqui: o Visual C++
  continua dentro (em instalar\ da pasta, na atualização e no instalador); a conferência da pasta pronta continua
  cobrando o Visual C++ de uma pasta que vem de fora. O conserto só faz a pasta montada do zero chegar a essa
  conferência com o Visual C++ já posto.
- D-767 "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione" · "quero que faça
  as coisas certas e sem bugs ou erros, deveria ter pensado nesses erros na hora de montar a estrutura do atualizador e
  testes a distancias". Aqui: o teste de reversão passa a pasta pelo `construir_pasta` de verdade (só o PyInstaller é
  trocado por quem escreve o que ele escreve, lido do próprio comando), e não por uma pasta de mentira já pronta. O
  PyInstaller e o vpk de verdade só na prova à vista da gerente.
- D-773 "A". Aqui: na pasta das provas, a frase do motor que falta dá o comando com o `--pasta` (achado 2).
- D-776 "Sim, no C só tem que cuidar para não encher o disco C inteiro". Aqui: nada muda na conta do espaço; o Visual C++
  (uns 25 MB) entra na pasta antes da conta, como já entrava na pasta pronta.
- D-777 "mas dai vai fazer quais versões?" · "ok, fica assim". Aqui: nada muda (a atualização sem .msi; o .msi só com
  `--com-instalador`).
- D-785 "ok, mais ainda existem mais casos na opção A" · "ok". Aqui: publicar é "sempre à vista" (item 8): não rodei o
  publicar de verdade, nem o PyInstaller, nem o vpk; só li a pasta que a gerente montou na prova.
- D-788 "1" (a primeira opção). Aqui: nada muda no motor (o arquivo do motor em instalar\ só no instalador).
- D-789 "mas iria demorar mais toda vez que eu fosse fazer a compilação né?" · "A". Aqui: nada muda (sem diferença).
- D-795 "porque fazer isso?" · "porque ter um instalador pequeno então?" · "não tem nenhuma documentação dizendo para o
  que isso serve?" · "ok". Aqui: nada muda no Setup.exe.
- D-815 "ok". Aqui: sou um escritor novo; comecei por este formulário.
- D-816 "A , mas onde estamos antes de você fazer qualquer processo". Aqui: o achado 1 (o apagar em que o gh nem abre)
  só ganha teste; nada muda no que é apagado.
- D-817 "pode". Aqui: nenhum teste antigo muda nesta volta.

**Volta 7 (20/11/2026), as decisões do pedido (palavras copiadas do Livro, `obra-juncao`, linha 1108 para a D-818):**
- D-818 "vai ter que reprogramar?" · "A" (a resposta à pergunta da gerente sobre consertar a conferência da pasta já
  montada, que está inteira na linha 1108 do Livro). Aqui: a
  pasta já montada (`--pasta-pronta`) e a montada do zero passam pela mesma conferência, num lugar só
  (`conferir_pasta_pronta`), que agora cobra o Visual C++ pela assinatura da Microsoft (a mesma checagem da montagem),
  o arquivo da versão dele e o Tesseract. A pasta de mentira dos testes antigos ganha as peças que faltam, e os testes
  continuam cobrando o mesmo (a lista de cada teste antigo mudado vai em "O que já está escolhido e testado aqui",
  Volta 7).
- D-727 "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né". Aqui: o Visual C++
  oficial, a versão dele e o Tesseract são cobrados de toda pasta antes do vpk e de todo pacote depois do vpk.
- D-767 "não faça mais nada escodindo ou de mentira". Aqui: a leitura da assinatura é a peça de verdade do Windows; nos
  testes do publicar, só o Visual C++ de prova (um arquivo de poucos bytes) é dado como da Microsoft, e o "Visual C++
  falso" do teste novo é lido pela peça de verdade. O vpk e o publicar de verdade, só na prova à vista.
- D-773 "A". Aqui: o comando da frase com uma pasta com espaço no nome (achado 5).
- D-776, D-777, D-788, D-789, D-795: nada muda (a conta, o .msi, o motor, sem diferença, o Setup.exe).
- D-785 (item 8): não rodei o publicar de verdade.
- D-815 "ok". Aqui: é a minha segunda e última volta.
- D-816 e D-817: nada muda no liberar nem no apagar.

**Volta 8 (20/11/2026), as decisões do pedido (palavras copiadas do Livro, `obra-juncao`, linhas inteiras):**
- D-605 "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está
  escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os agentes precisam
  ler". Aqui: nenhum teste antigo muda; o programa instalado continua achando o motor e lendo a versão do Visual C++
  como hoje (com prova); o que muda está listado em "O que já está escolhido e testado aqui", Volta 8.
- D-727 "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né". Aqui: o Visual C++ e a
  versão dele continuam dentro; a leitura dessa versão passa a ser uma só, a do publicar (o que a prova conferiu), e o
  programa instalado a usa.
- D-767 "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione". Aqui: os testes
  novos do Visual C++ usam a leitura de verdade do Windows (uma cópia do PowerShell do próprio Windows fazendo papel de
  Visual C++, com assinatura de verdade); o defeito 1 é provado com um git de verdade numa cópia de trabalho de verdade.
- D-773 "A". Aqui: o apagar nas provas (pasta e GitHub) diz o que aconteceu de verdade.
- D-776 "Sim, no C só tem que cuidar para não encher o disco C inteiro". Aqui: nada muda na conta do espaço.
- D-777 "mas dai vai fazer quais versões?" · "ok, fica assim". Aqui: nada muda nas saídas.
- D-785 "ok, mais ainda existem mais casos na opção A". Aqui: publicar é "sempre à vista" (item 8): não rodei o
  publicar de verdade; a gerente o repete com o Samuel ("A prova de verdade", Volta 8).
- D-788 "1". Aqui: o programa instalado continua procurando o motor ao lado do programa, como hoje (o defeito 1 mexe
  só onde o código, rodando pelas fontes, acha a pasta das ferramentas do Samuel).
- D-789 "mas iria demorar mais toda vez que eu fosse fazer a compilação né?" · "A". Aqui: nada muda.
- D-795 "porque fazer isso?" · "porque ter um instalador pequeno então?" · "não tem nenhuma documentação dizendo para o
  que isso serve?" · "ok". Aqui: nada muda no Setup.exe.
- D-815 "ok". Aqui: sou um escritor novo nesta volta; comecei por este formulário e pelo relatório 7.
- D-816 "A , mas onde estamos antes de você fazer qualquer processo". Aqui: a frase nova do apagar não muda o que é
  apagado: depois do pedido de liberar, nada se apaga (o caminho da D-816 não passa pelo apagar).
- D-817 "pode". Aqui: nenhum teste antigo muda nem sai nesta volta.
- D-818 "vai ter que reprogramar?" · "A". Aqui: as duas proteções do Visual C++ da pasta já montada (a leitura que falha
  e a mesma régua) e a versão dele ganham os testes que faltavam; a régua não muda.

## O que já está escolhido e testado aqui

- `tests/test_empacotar.py`: o motor do jeito novo passa e o velho, com atalhos ou de outro protocolo, é recusado
  (`empacotar.conferir_motor_kraken`, com um motor de mentira SEM a ficha: por isso essa função não passou a exigir a
  ficha); `empacotar.achar_motor_kraken` pula o velho (troca `empacotar.LUGARES_DO_MOTOR`: o nome não pode mudar);
  faltando peça, para antes do PyInstaller; o Visual C++ oficial confere; `empacotar.assinatura_do_arquivo` roda de
  verdade num arquivo sem assinatura e o resultado não confere. Os testes do Inno continuam.
- `tests/test_decisoes_atualizacao.py`: D-714 (a versão de um lugar só; `empacotar.comando_do_vpk` com quatro
  argumentos tem `--packVersion`); D-724 (publicar sem a chave para antes de tudo, pelo `publicar(versao,
  destino_pasta=..., arquivo_da_chave=...)` e pelo `main(["--pasta", ..., "--chave", ...]) == 1`; a chave nunca dentro
  do repositório; o que o publicar assina o programa aceita); D-727 (`empacotar.comando_do_vpk` de fábrica tem `--msi`,
  `--instLocation PerMachine`, `--runtime win-x64` e nada de `--framework`; `empacotar.preparar_pasta_para_o_velopack`
  põe o Visual C++ em instalar\; `empacotar.esperados_no_pacote_do_velopack` e `empacotar.conferir_pacote_do_velopack`
  com peças cujo motor nem existe).
- `tests/test_decisoes_brasao.py` (o ícone no `vpk --icon`), `tests/test_nome_do_pacote.py` (o `--packId`, o
  `--packTitle`, o vpk preso na 1.2.161, `empacotar.nupkg_inteiro`).
- `tests/test_ocr_kraken.py`: `ocr_kraken.lugares_do_motor` tem pelo menos 2 lugares e `ocr_kraken.achar_pasta_do_motor`
  não quebra (o nome não pode mudar; e o defeito antigo nº 330, dos testes do motor que pulam calados numa cópia,
  continua, como o plano manda).
- `tests/test_windows_peca.py` e as conferências do porteiro (`tests/test_conferencias_codigo.py`,
  `tests/test_conferencias_excecoes.py`): a peça é fechada, o rodar genérico recusa o PowerShell, a lista de exceções
  só diminui.
- Livro: D-714, D-723, D-724, D-727, D-746, D-763, D-768, D-773, D-776, D-777, D-788 a D-790, D-795.
- **Nenhum desses testes mudou.** Todos passam (ver "Testes").

- **Volta 3:** nenhum teste antigo mudou no que ele cobra. A única mudança num teste antigo é a pedida pela gerente: o
  vpk de mentira deixou de ser um `vpk.cmd` (a peça passou a recusar o .bat e o .cmd) e virou um programa de prova de
  verdade (`tests/test_publicar_versao.py::_programa_de_prova`, o lançador do pip com o mesmo script). O teste antigo
  da janela do servidor (`test_o_que_nao_esta_numa_versao_liberada_e_recusado`, que cobra "não existe aqui (404)") foi
  respeitado: a frase nova só vale para o nome repetido.

**Volta 4 (antes de mexer).** O que esta volta toca e já está escolhido e testado:
- O caminho de erro do publicar (`publicar_versao_kaique.publicar_arquivos` e `apagar_publicacao`): D-776 e D-795 (o
  rascunho do C: e o Setup.exe somem também com erro), a escolha técnica da gerente de 19/11 (D-014: nada liberado é
  apagado) e os testes `test_achado4_depois_de_liberar_a_leitura_que_falha_nao_apaga_a_versao` ("não deu para reconferir
  agora", "NÃO apaguei"), `test_volta3_achado1_uma_leitura_atrasada_depois_de_liberar_nunca_apaga_a_versao_liberada`
  ("NÃO apaguei", "ficou liberada em", nunca "foi apagada"), `test_volta3_achado1_no_github_a_leitura_atrasada_tambem_nunca_apaga_a_liberada`,
  `test_achado1_erro_antes_de_liberar_no_github_apaga_e_diz_que_apagou` ("foi apagada", sem "ATENÇÃO"),
  `test_a_leitura_de_volta_que_nao_bate_nao_libera_e_apaga_o_rascunho_do_destino` ("chegou diferente ... apagada"),
  `test_n1_n3_n4_n14_cada_leitura_de_volta_errada_impede_liberar`, `test_n5_o_apagar_que_nao_apaga_e_acusado`
  ("continua lá"), `test_achado1_apagar_um_rascunho_no_github_le_de_volta_e_nao_acusa_erro_falso` e
  `test_achado1_quem_decide_se_apagou_e_a_leitura_de_volta` (o `--apagar`), todos em `tests/test_publicar_versao.py`.
- **Um teste antigo cobra o que a D-816 tirou:** `test_volta3_achado5_o_liberar_que_falha_e_continua_rascunho_apaga_o_rascunho` (saiu na volta 4: a D-816 tirou o que ele cobrava)
  cobra que, quando o PEDIDO de liberar falha e a publicação continua rascunho (na pasta), o rascunho é apagado. A D-816
  diz o contrário ("depois de pedir ao GitHub para liberar a versão, o programa nunca apaga nada"; "Na pasta das provas
  (não no GitHub) vale a mesma regra"), e o pedido da gerente repete ("em nenhum destino"). Pela regra das decisões
  (CLAUDE.md §11, ponto 4: quando a decisão substitui um comportamento antigo, a prova confere que o antigo saiu), este
  teste passa a cobrar o jeito novo nesse mesmo caso. É a única mudança num teste antigo nesta volta, e está nas
  Ressalvas para a gerente conferir.
- A peça do Windows (`core/windows.py`, a recusa `_programa_com_funcao_propria`, o grupo `abrir_em_grupo`,
  `_gravar_por_inteiro`): os testes de `tests/test_windows_peca.py` (o lote recusado pelos três caminhos, com a frase
  "função própria"; o programa de verdade passando; "não achei" para o que não existe; o grupo que nasce parado e fecha
  tudo; as pastas de troca; a pasta segura e as tarefas) e `tests/test_windows_janela_de_prova.py`.
- O vpk pela função única (`empacotar.rodar_vpk`): os testes da vigia (D-776, "19.0 GB", "reserva"), do grupo
  ("fechados (conferido)"), do Ctrl+C e do soltar segurado, em `tests/test_publicar_versao.py`.
- O gh (`DestinoGitHub._gh`): `test_volta3_achado7_o_gh_que_baixa_e_fechado_pela_vigia` (um gh de prova de verdade,
  fechado pela vigia em menos de 20 s, "abaixo da reserva").
- A cópia conferida e o motor comprimido (`empacotar.copiar_inteiro`, `empacotar.zipar_motor`):
  `test_volta3_a_copia_conferida_le_de_volta_e_obedece_a_vigia`, `test_volta3_a_copia_cortada_no_meio_nunca_deixa_o_nome_certo`,
  os do .msi, e os de `tests/test_publicar_motor.py` (o zip conferido pela ficha, a vigia na compressão).
- Livro: D-767, D-773, D-775, D-776, D-795, D-811 a D-813, D-815, D-816.

**Volta 5 (antes de mexer):** as escolhas e os testes que esta volta toca são os mesmos da volta 4 (acima), mais os da
volta 4 em si: `test_d816_*` (nada é apagado depois do pedido de liberar), `test_volta4_achado3_*` (a frase diz se
pediu), `test_volta4_achado4_*`, `test_volta4_o_nome_com_ponto_no_fim_e_lido_como_o_windows_completa` e os do lote
(`test_bat_e_cmd_sao_recusados_pelo_rodar_pelo_lancar_e_pelo_grupo`, que cobra a frase "função própria" para o
`x.bat::$DATA`). Nenhum teste antigo mudou nesta volta: o fluxo escondido é conferido depois do lote, para o
`x.bat::$DATA` continuar com a frase do lote; e o "não abriu" do achado 4 só vale para o gh que nem começou, para os
testes da D-816 (o liberar que responde erro, o Ctrl+C) continuarem como estão.

**Volta 6 (antes de mexer).** O que esta volta toca e já está escolhido e testado:
- O Visual C++ em instalar\ (D-727): `tests/test_decisoes_atualizacao.py` (perto da linha 540) chama
  `empacotar.preparar_pasta_para_o_velopack(pasta, pecas)` e cobra o arquivo e a versão em instalar\;
  `empacotar.esperados_no_pacote_do_velopack(pecas)` tem o Visual C++; `empacotar.conferir_pacote_do_velopack` acusa
  `instalar/vc_redist.x64.exe` quando falta. O nome `preparar_pasta_para_o_velopack` não pode mudar (o teste o chama).
- A conferência da pasta pronta (`empacotar.conferir_pasta_pronta`): `tests/test_publicar_versao.py::test_a_pasta_pronta_de_outra_versao_e_recusada`
  ("é da versão 1.0.0", antes do vpk). Continua cobrando o .exe, a ficha da mesma versão e não portátil, o Visual C++
  em instalar\ e nada de motor solto.
- `empacotar.preparar_saida`: `tests/test_publicar_motor.py` (linhas 142 e 147) a chama com quatro argumentos
  posicionais (`pasta, ATUALIZACAO, None, motor`): a ordem e o terceiro argumento (`pecas`) não podem mudar.
- A pasta portátil e o Inno (`empacotar.construir_pasta()` de fábrica, `construir_instalador`): o Visual C++ vai para
  `build\` e o Inno o pega de lá (`tests/test_empacotar.py::test_registro_do_inno_tem_de_listar_cada_peca`,
  `test_o_script_do_inno_recusa_pasta_sem_as_pecas`); `construir_pasta()` para antes do PyInstaller sem modelo, DLL
  ou peça (`test_modelo_faltando_para_antes_do_pyinstaller`, `test_pecas_faltando_param_antes_do_pyinstaller`,
  `test_dll_da_gravura_faltando_para_antes_do_pyinstaller`). Nada disso muda: a pasta portátil continua sem instalar\.
- As três saídas (`empacotar.SAIDAS`, "o lugar único do que muda entre o que este script monta"): os testes da D-768 e
  da D-777 em `tests/test_publicar_versao.py` (a atualização sem o motor; o instalador com o arquivo do motor em
  instalar\ e o .msi; a pasta volta sem o arquivo do motor).
- A frase do motor que falta: `tests/test_publicar_versao.py::test_d790_sem_o_motor_publicado_nada_e_montado` cobra
  "publique o motor antes" (o começo da frase continua).
- A recusa do caminho de rede e do que não vira letra de disco: `tests/test_windows_peca.py::test_a_recusa_vale_para_o_caminho_escrito_de_outro_jeito`
  (N2) e o teste do "raiz global" (perto da linha 930) cobram que a recusa tem as palavras "função própria". A frase
  nova do achado 3 diz o motivo de verdade, que inclui essas palavras (ver "Ressalvas", Volta 6): nenhum desses testes
  muda.
- O apagar de antes do pedido de liberar (`apagar_publicacao`, `_pedir_para_apagar`, `NadaSaiu`, `ApagarSemResposta`):
  os testes `test_volta5_achado2_*`, `test_volta5_achado3a_*` e `test_volta5_achado4_*`. Nada muda no código; só um teste
  novo.
- Livro: D-727, D-767, D-773, D-776, D-777, D-785, D-788, D-789, D-795, D-816, D-817.

**Volta 7 (antes de mexer).** O que esta volta toca e já está escolhido e testado: tudo o da volta 6 (acima) e os testes
da volta 6 (`test_volta6_*`). Mais:
- `empacotar.preparar_vc_redist` e `empacotar.vc_redist_confere` (a régua do Visual C++ oficial):
  `tests/test_empacotar.py::test_vc_redist_oficial_confere`, `test_vc_redist_que_nao_confere` (5 casos) e
  `test_assinatura_de_um_arquivo_sem_assinatura` (a leitura de verdade pelo Windows). Os nomes e o que devolvem não
  mudam.
- `empacotar.esperados_no_pacote_do_velopack` e `conferir_pacote_do_velopack`: `tests/test_decisoes_atualizacao.py::test_d727_o_visual_c_vai_dentro_e_e_conferido_no_pacote`
  (monta o pacote com os esperados e cobra que, sem o Visual C++, a única falta é `instalar/vc_redist.x64.exe`),
  `tests/test_publicar_versao.py::test_d768_o_pacote_da_atualizacao_com_o_motor_solto_e_recusado` e
  `test_achado8_o_arquivo_do_motor_em_instalar_e_recusado_na_atualizacao` (os dois montam o pacote com os esperados).
  Cobrar mais peças nos esperados não os quebra (o pacote deles é feito da própria lista).
- `empacotar._destinos_das_pecas` (a lista do Tesseract): `tests/test_empacotar.py::test_registro_do_inno_tem_de_listar_cada_peca`
  (os caminhos do Tesseract no Inno). A lista não muda; passa a ser escrita uma vez só.

**Os testes antigos que mudam, pela D-818 (só a pasta de mentira e o que ela precisa para "ser" a de verdade; nenhum
muda o que cobra):**
1. `tests/test_publicar_versao.py::_pasta_pronta` (a pasta de mentira de todos os testes do publicar, 29 chamadas de
   `_publicar(a` mais as diretas): passa a trazer o arquivo da versão do Visual C++ (o vc_redist.versao.txt de instalar\,
   "14.44.35211.0") e o Tesseract (os mesmos arquivos que a montagem copia, pela lista única). O "Visual C++" continua o
   mesmo arquivo de poucos bytes.
2. `tests/test_publicar_versao.py::ambiente` (a preparação de todos os testes do publicar): a leitura da assinatura
   (`empacotar.assinatura_do_arquivo`) passa a responder "assinado pela Microsoft, Visual C++ 2015-2022 x64, 14.44" para
   os Visual C++ de prova (o da pasta de mentira e o do teste da montagem, reconhecidos pelo conteúdo); qualquer outro
   arquivo vai à leitura de verdade do Windows. Sem isso, um arquivo de poucos bytes nunca é da Microsoft, e todos os
   testes antigos parariam na conferência nova (não pelo que eles cobram). É o que os testes já fazem com o vpk e o gh
   (peças de mentira só para a lógica em volta, D-767), escrito no texto da preparação.
3. O `VPK_FALSO` de `tests/test_publicar_versao.py` (o vpk de mentira): ganha uma opção, `VPK_FALSO_SEM` (deixa de fora do
   pacote os caminhos que começam com o que ela diz), desligada de fábrica: com ela vazia, ele faz exatamente o que fazia.
Se algum teste antigo precisar mudar o que cobra, paro e escrevo em "Perguntas para o Samuel".

**Volta 8 (antes de mexer).** O que esta volta toca e já está escolhido e testado:
- O apagar (`publicar_versao_kaique.apagar_publicacao`, o lugar único de apagar e conferir; o `--apagar` do `main`):
  devolve o aviso do destino ou nada, e levanta com a frase pronta nos outros casos. Testes antigos que dependem disso
  (o que ela devolve e o que levanta, não mudam): `tests/test_publicar_versao.py::test_d809_apagar_uma_publicacao_que_e_atalho_nao_apaga_o_outro_lado`,
  `test_achado1_apagar_um_rascunho_no_github_le_de_volta_e_nao_acusa_erro_falso` (cobra que devolve nada),
  `test_achado1_erro_antes_de_liberar_no_github_apaga_e_diz_que_apagou` (cobra "foi apagada" no caminho de erro),
  `test_n5_o_apagar_que_nao_apaga_e_acusado`, `test_achado1_quem_decide_se_apagou_e_a_leitura_de_volta` (cobra o aviso
  devolvido) e os `test_volta4_*`, `test_volta5_*` do apagar. O `--apagar` do `main` não tinha teste.
- A versão do Visual C++ lida do pacote: no programa instalado, `atualizacao.instalar_visual_c_se_faltar`
  (`tests/test_decisoes_atualizacao.py::test_d727_o_visual_c_so_roda_se_faltar`, `tests/test_decisoes_preparo_d749.py`);
  no publicar, `empacotar.conferir_pasta_pronta` (`tests/test_publicar_versao.py::test_d818_a_pasta_ja_montada_e_conferida_igual_a_montada_do_zero`).
  A frase do publicar ("a pasta ... diz que o Visual C++ é o ...") não muda.
- A régua do Visual C++ (`empacotar.conferir_o_visual_c`, `vc_redist_confere`, `assinatura_do_arquivo`) e a lista do
  Tesseract (`empacotar.relativos_do_tesseract`): não mudam; só ganham testes.
- O defeito 1 (só o plano, ver "A causa", Volta 8): `tests/test_ocr_kraken.py` (um teste cobra que há pelo menos dois
  lugares para procurar o motor), `tests/test_empacotar.py` (trocam `empacotar.LUGARES_DO_MOTOR` e `empacotar.DOWNLOADS`
  pelo nome: os nomes têm de continuar existindo) e o programa instalado (o motor ao lado do programa, D-788).
- Livro: D-605, D-727, D-767, D-773, D-788, D-816, D-817, D-818.

## Como fica para quem usa e no livro

- **O Kaique: nada muda** na tela nem no livro (nenhum arquivo de `ui/` nem do processamento das páginas). O PDF que
  sai não muda, antes e depois. O que muda é o que ele vai baixar a partir do passo 3: a atualização sem o motor do
  Kraken (uns 460 MB em vez de 826 MB, conta do estudo) e, na primeira instalação, o .msi com o motor dentro como um
  arquivo só.
- **O Samuel, ao publicar (na prova à vista).** Antes: um comando que montava no D:, baixava a versão anterior, fazia
  a diferença, o .msi e o zip portátil, e liberava no GitHub antes de a assinatura subir. Depois: o mesmo comando; (1)
  primeiro diz quanto espaço vai usar no C: e para, com aviso, se o C: ficaria com menos de 20 GB livres; (2) monta no
  C:; (3) não baixa a versão anterior nem faz a diferença; (4) sobe como rascunho, lê de volta e só então libera; (5)
  no fim apaga o rascunho do C: e o Setup.exe, também quando dá erro, e lista o que ficou na pasta de saída e no
  destino. Para o motor, um comando próprio (`--motor`), raro. O .msi só com `--com-instalador`. Para apagar a versão
  de prova no fim: `--apagar v<versão>`.
- **O servidor das versões de prova:** uma janela pequena, com o endereço, as versões que ela serve e uma linha por
  pedido. Fechar a janela corta o que estiver sendo baixado (a internet caindo).
- **Problema novo criado:** a pasta que o publicar enche com `--pasta` agora tem uma subpasta por versão (como o
  GitHub). O jeito da etapa 5 de servir as versões direto de uma pasta (a fonte de teste do programa de hoje, que lê a
  pasta plana) não lê esse desenho: nas provas, as versões vêm pelo servidor (D-773), e o programa passa a falar com
  ele no passo 3. Escrito também em "Ressalvas".

- **Volta 3, para quem publica (o Samuel na prova):** nada muda no caminho que dá certo, fora duas linhas a mais na
  conferência do fim (o instalador "igual ao feito agora (tamanho e soma conferidos)", e no `--motor` a linha do
  rascunho). Muda o que se lê quando dá errado: (1) se a resposta do liberar se perder, a versão liberada fica e a
  frase diz "ficou liberada ... NÃO apaguei"; (2) se o .msi não couber na pasta de saída, nenhum .msi pela metade fica
  lá e a frase diz que a versão FOI publicada e que o instalador está inteiro na publicação; (3) o "PAREI" do fim
  aponta para a conferência do fim, em vez de dizer "foi apagado" sem conferir. Nenhum problema novo para o Kaique
  (nenhum arquivo do programa dele mudou de comportamento: a peça ainda não é usada por ele).

**Volta 4 (antes de mexer):**
- **O Kaique: nada muda** (nenhum arquivo de `ui/` nem do processamento das páginas; o PDF que sai é o mesmo; a peça do
  Windows ainda não é usada pelo programa dele).
- **O Samuel, publicando (na prova à vista).** No caminho que dá certo, nada muda na tela. Muda quando dá errado
  depois do pedido de liberar (a resposta do GitHub se perde, a internet cai, Ctrl+C): antes, o publicar lia o GitHub e
  podia apagar o que achasse que era rascunho; agora não apaga nada e diz, numa frase só, que a versão pode ter ficado
  liberada (inteira) ou como rascunho, como conferir e o comando para apagar o rascunho depois. Antes do pedido de
  liberar, continua como hoje: o rascunho do destino é apagado na hora e a frase diz "foi apagada (conferido)" só quando
  pediu e conferiu; quando não deu para conferir, a frase diz se chegou a pedir.
- **Com o GitHub sem a soma pronta** (o "digest"), o arquivo baixado para somar fica no rascunho do C: (apagado no fim)
  em vez de na pasta temporária da conta, e a vigia do espaço olha o download. A conta do espaço soma esse arquivo: em
  teoria o publicar pode recusar um pouco mais cedo (uns 0,8 GB a mais na conta), de propósito.
- **O gh passa a rodar pelo grupo do Windows**, como o vpk: nada aparece de diferente (a saída dele já era guardada,
  não mostrada); fechar por tempo, pela vigia ou pelo Ctrl+C fecha o gh e o que ele abrir.
- **As cópias e o motor comprimido** pedem ao Windows para gravar no disco antes de conferir: alguns segundos a mais
  num arquivo grande no HD externo (o dado tinha de ser gravado de qualquer jeito).
- **Problema novo criado:** nenhum que eu saiba. O que fica para conferir está em "Ressalvas" (o teste antigo da D-816,
  a gravação no disco na peça do passo 1).

**Volta 5:** o Kaique: nada muda (nem a tela, nem o PDF). O Samuel, publicando: nada muda no caminho que dá certo. Muda
quando dá errado: (1) na pasta das provas, a frase de "já existe" ou "sobrou um rascunho" dá o comando com o `--pasta`
(antes, seguir a frase apagava no GitHub); (2) se o gh nem abrir no pedido de liberar, o rascunho do GitHub é apagado
na hora, e a frase diz que foi apagado (antes ficava, com a frase "pedi para liberar"); (3) a frase do apagar não diz
"pedi" quando só uma leitura ficou sem resposta. A peça do Windows recusa o programa escrito como fluxo escondido
(ninguém usa isso). Problema novo: nenhum que eu saiba.

**Volta 6:** o Kaique: nada muda (nem a tela, nem o PDF, nem o que ele baixa: a atualização e o instalador continuam
levando o Visual C++ em instalar\, D-727). O Samuel, publicando:
- **Antes:** `publicar_versao_kaique.py --pasta <pasta>` (sem `--pasta-pronta`) montava a pasta (uns 4 minutos de
  PyInstaller) e parava sempre em "a pasta do programa não serve: ... não tem o Visual C++ em instalar\". Nenhuma
  versão montada do zero saía.
- **Depois:** a mesma linha monta a pasta, põe o Visual C++ conferido em instalar\ na própria montagem, passa pela mesma
  conferência e segue para o vpk. Com `--pasta-pronta`, nada muda: a pasta que vem de fora sem o Visual C++ continua
  recusada (a pasta que a prova montou hoje, com o código antigo, é recusada assim; é preciso montar de novo).
- Na pasta das provas, se o motor não estiver publicado, a frase manda rodar o `--motor` com o `--pasta` (antes, sem o
  `--pasta`: seguida ao pé da letra, publicava o motor no GitHub).
- O caminho de rede pedido à peça do Windows tem frase própria (só o texto muda; ninguém usa caminho de rede).
- A pasta portátil (`empacotar.py --modo pasta`) e o instalador do Inno: nada muda (continuam sem instalar\).
Problema novo: nenhum que eu saiba. O que só a prova à vista mostra: o PyInstaller e o vpk de verdade depois deste
ponto (nunca rodaram por este caminho; ver "Ressalvas").

**Volta 7:** o Kaique: nada muda no caminho certo (a mesma atualização, com o Visual C++ oficial, a versão dele e o
Tesseract). O que muda é que uma pasta errada não chega mais até ele. O Samuel, publicando:
- com a pasta montada do zero: nada muda no que ele vê, fora uma leitura a mais da assinatura do Visual C++ (cerca de
  um segundo, pelo Windows) em cada conferência da pasta;
- com `--pasta-pronta`: a pasta sem o Tesseract, com um Visual C++ que não é o oficial ou sem o arquivo da versão dele
  é recusada antes da conta do espaço, com a mesma frase que a montada do zero daria (antes passava e era publicada);
- o empacotar chamado sozinho recusa a pasta antes de mexer nela;
- o pacote depois do vpk é conferido também na versão do Visual C++ e no Tesseract, com ou sem `--pasta-pronta`.
Problema novo possível: uma pasta pronta que só não tem o arquivo da versão (como a da prova de 20/11 arrumada à mão)
passa a ser recusada; é o pedido. A pasta portátil e o Inno não mudam.

**Volta 8:** o Kaique: nada muda (nem a tela, nem o PDF, nem o que ele recebe). No programa instalado dele, a versão do
Visual C++ que vem no pacote passa a ser lida pela mesma função que o publicar usa para conferir o pacote; para todo
pacote que o publicar aceita (o único que chega a ele), o resultado é o mesmo de hoje (provado num teste com os cinco
jeitos de arquivo que o relatório 7 testou). O Samuel, publicando:
- `--apagar` passa a dizer o que aconteceu: "a publicação v1.1.0 foi apagada de a pasta ... (conferido)" quando havia o
  que apagar, e "v1.1.0: não existia em ..., e nada foi apagado (conferido)" quando não havia (antes, as duas viravam
  "não existe em ... (conferido)", e na prova pareceu que nada tinha sido apagado). O que é apagado não muda.
- O caminho de erro do publicar (antes do pedido de liberar) continua dizendo "foi apagada (conferido)", pela mesma
  frase.
- (Defeito 1, quando for feito: rodando o publicar de uma cópia de trabalho, o motor e o Visual C++ passam a ser
  procurados em `D:\programas\EditorImpressao-arquivos\ferramentas`, como da pasta principal; nenhuma pasta nova aparece
  dentro de `.claude\worktrees`.)
- O PDF: nada muda antes e depois (esta volta não toca o caminho do livro).
Problema novo possível: nenhum que eu saiba; o que só a prova à vista mostra está em "A prova de verdade", Volta 8.

## A causa, a regra e todos os caminhos

**Por que os defeitos aconteciam (lista do plano, itens 53 a 57, e os do estudo):**
1. O vpk era rodado por dois caminhos, cada um do seu jeito (o `_rodar` do publicar com a pasta pronta e
   `empacotar.construir_pacote_do_velopack` com `subprocess.run`), e a pasta temporária vinha de quem chamava (a etapa 5
   a desviou à mão). Causa: não havia uma função que roda o vpk.
2. O PowerShell de `empacotar.assinatura_do_arquivo` falava com o Windows fora da peça única (item da lista de
   exceções).
3. O motor do Kraken ia dentro de toda versão (98% dos arquivos), porque a pasta portátil, a atualização e o instalador
   eram a mesma coisa.
4. No GitHub, o upload do vpk com publish liberava a versão antes de a assinatura subir (item 53): se a assinatura
   falhasse, a versão ficava liberada sem assinatura e o programa do Kaique a recusaria para sempre.
5. O Setup.exe e o rascunho ficavam (nada apagava) e a pasta pronta podia ser de outra versão (item 54).

**As regras, cada uma num lugar só:**
- Rodar o vpk: `empacotar.rodar_vpk` (a pasta temporária e a vigia do espaço).
- O comando do vpk: `empacotar.comando_do_vpk` (como hoje), com `--delta None` e `--noPortable` sempre, e o `--msi`
  só quando a saída pede.
- As três saídas (pasta portátil, atualização, instalador): `empacotar.SAIDAS`; tudo o que muda entre elas (motor
  solto, o motor-exigido.json, o arquivo do motor em instalar\, o .msi, o que o pacote tem de ter e não pode ter, a
  conta do espaço) lê dali.
- A conta do espaço e a reserva: `empacotar.espaco_que_vai_usar` e `empacotar.conferir_espaco`.
- O motor "inteiro e da versão certa": `ocr_kraken.conferir_motor` e a regra da ficha `ocr_kraken.conferir_ficha`
  (usada pela pasta e pelo arquivo do motor); a versão do motor: `ocr_kraken.VERSAO_DO_MOTOR`; a ficha é escrita só por
  `montar_motor_kraken.gravar_ficha_do_motor`; a forma do motor: `ocr_kraken.problemas_da_forma` (o empacotador a usa).
- Os nomes do motor publicado (pacote, etiqueta, arquivo) e a etiqueta da versão: `versao.py`.
- Ler a assinatura digital de um arquivo pelo Windows: `windows.ler_assinatura_digital` (função própria na peça).
- Publicar num destino (rascunho, enviar, ler de volta, liberar, apagar): `publicar_versao_kaique.publicar_arquivos`,
  sobre os dois destinos (`publicar_versao_kaique.DestinoPasta`, que o servidor serve, e
  `publicar_versao_kaique.DestinoGitHub`, pelo gh); a conversa com o GitHub, só em `DestinoGitHub._gh`.
- O que vai a um destino: `publicar_versao_kaique.arquivos_da_versao` (nunca o Setup.exe).
- O motor que a versão pede, lido de volta: `publicar_versao_kaique.obter_motor_publicado` (no começo, antes de liberar,
  e na leitura de volta da própria publicação do motor).

**Todos os caminhos (achados com busca no código: `vpk`, `comando_do_vpk`, `construir_pacote_do_velopack`,
`assinatura_do_arquivo`, `motor-kraken`, `LUGARES_DO_MOTOR`, `lugares_do_motor`, `conferir_motor_kraken`, `upload`):**
- `publicar_versao_kaique.publicar` (com e sem `--pasta-pronta`, com e sem `--com-instalador`) → `empacotar.rodar_vpk`
  pelo `empacotar.construir_pacote_do_velopack`.
- O download e o upload do vpk no publicar → saíram (sem diferença não há o que baixar; o envio é `publicar_arquivos`).
- `empacotar.preparar_vc_redist` → `empacotar.assinatura_do_arquivo` → `windows.ler_assinatura_digital`.
- `empacotar.construir_pasta` (a pasta portátil, o `--modo pasta`, o `--modo instalador` e o `--modo entrega` do Inno,
  e a atualização) → o motor solto só quando a saída diz.
- `montar_motor_kraken.main` (montar, `--so-servidor`, `--so-ficha`) → grava a ficha depois do teste e confere por
  `ocr_kraken.conferir_motor`.
- `publicar_versao_kaique.publicar_motor` → `ocr_kraken.conferir_motor` (a pasta) e `empacotar.problemas_do_zip_do_motor`
  (o arquivo), as duas pela mesma `ocr_kraken.conferir_ficha`.
- O programa (`ocr_kraken.achar_pasta_do_motor`, o teste rápido, o `--conferir-ocr`, o ajudante): **não mudam neste
  passo** (passo 3 do plano). `ocr_kraken.lugares_do_motor` continua igual.
- O servidor das versões lê a mesma pasta que `DestinoPasta` grava, pelas mesmas regras (`ETIQUETA_ACEITA` do publicar,
  `NOME_DO_INDICE` do empacotar), sem copiar.

**Volta 3 (relatório 2 de quem tentou quebrar). As causas e as regras, cada uma num lugar só:**
- *Versão liberada apagada (achado 1).* Causa: "só o rascunho é apagado" era decidido por uma leitura no
  `publicar_arquivos`, e o apagar lia de novo por conta própria e apagava o que achasse. Regra:
  `publicar_versao_kaique.apagar_publicacao(destino, etiqueta, so_rascunho=True)` lê ali dentro antes e depois, e
  chama `destino.apagar_rascunho`, que na pasta só toca na subpasta do rascunho (pela construção) e no GitHub lê de
  novo logo antes de pedir. Caminhos: o erro antes de liberar e o erro depois de pedir para liberar, na versão e no
  motor (os dois passam por `publicar_arquivos`) → `apagar_publicacao(so_rascunho=True)`; o `--apagar` →
  `apagar_publicacao` (apaga liberada, de propósito: o fim da prova).
- *O .msi pela metade (achado 2).* Causa: cópia direta no nome certo (`shutil.copyfile`, que não apaga o destino quando
  falha). Regra: a cópia conferida `empacotar.copiar_inteiro` (nome provisório, lida de volta: tamanho e soma, só então
  o nome certo; na falha apaga o pedaço e confere). Caminhos: o .msi para a pasta de saída
  (`publicar_versao_kaique.guardar_o_instalador`), o envio à pasta de destino (`DestinoPasta.enviar`) e a leitura de
  volta da pasta de destino (`DestinoPasta.baixar` → `baixar_vigiado`). (A cópia do motor para instalar\ do
  `empacotar.preparar_saida` não mudou: ela já confere a soma assinada e apaga o que não bate, e o `finally` do
  publicar tira o arquivo do motor de instalar\.)
- *O .bat e o .cmd pela peça (achado 3).* Causa: a recusa olhava onde o arquivo pedido mora, e não o que o Windows roda
  de verdade (um lote vai ao cmd.exe). Regra: `windows._programa_com_funcao_propria` → `windows._nao_e_programa_do_windows`
  (a extensão depois de o Windows completar o caminho, e o começo do arquivo, "MZ"). Caminhos: `windows.rodar_e_esperar`,
  `windows.lancar_solto`, `windows.abrir_em_grupo` (todos chamam a mesma regra).
- *O instante do grupo e a frase "conferido" (achados 4 e 9).* Causa: o programa nascia rodando e era posto no grupo
  depois; e a frase do fechar dependia de uma leitura que, sem resposta, virava "continua rodando". Regra:
  `windows.abrir_em_grupo` abre parado, põe no grupo, confere (IsProcessInJob) e só então solta
  (`windows._soltar_o_programa_parado`); `windows.ProgramaEmGrupo.fechar_tudo` só diz "conferido" com 0 vivos lidos.
  Caminho: `empacotar.rodar_vpk` (a vigia, o fim normal e o Ctrl+C) → `fechar_tudo`.
- *O motor baixado fora da conta e da vigia (achado 7).* Causa: a conta e a vigia só olhavam o vpk e a compressão; a
  vigia estava escrita duas vezes (no `rodar_vpk` e no `zipar_motor`). Regra: a vigia única `empacotar.vigia_do_espaco`
  (usada pelo `rodar_vpk`, pelo `zipar_motor`, pelo `copiar_inteiro` e pelo `DestinoGitHub._gh`); a conta
  `empacotar.espaco_que_vai_usar(..., baixado_para_o_rascunho=...)`. O nome "motor-kraken-": `versao.PREFIXO_DO_MOTOR`
  (a etiqueta aceita do publicar, o molde dos arquivos de motor em instalar\ e a lista do que não pode ir na
  atualização leem dali).
- *Textos (achado 8):* o cabeçalho da peça (quem a usa), o docstring do rascunho da pasta (as notas não são gravadas),
  a janela do servidor (`Versoes.procurar` diz por que não entrega) e a conta das "Ressalvas".

**Volta 4 (relatório 3 de quem tentou quebrar). Cada conserto: a causa, a regra num lugar só e os caminhos (achados
com `grep` por `apagar_publicacao`, `pediu_para_liberar`, `_programa_com_funcao_propria`, `.soma(`, `baixar_vigiado`,
`_gh(`, `abrir_em_grupo`, `copiar_inteiro`, `zipar_motor`, `os.replace`, `_gravar_por_inteiro`):**
- *Achado 1 (D-816).* Causa: depois do pedido de liberar, a decisão "só o rascunho é apagado" ainda dependia de
  leituras do GitHub, e duas leituras atrasadas bastavam para apagar a versão liberada. Regra: em
  `publicar_versao_kaique.publicar_arquivos`, o caminho de erro olha UMA coisa, que o próprio publicar sabe sem ler:
  se já pediu para liberar. Pediu: não chama apagar nenhum, em nenhum destino, e a frase (uma função só,
  `_frase_depois_do_pedido_de_liberar`) diz o que pode ter ficado e os comandos (`como_conferir` e `comando_de_apagar`,
  um por destino). Não pediu: `apagar_publicacao(so_rascunho=True)`, como hoje. Caminhos: a versão do programa
  (`publicar`) e o motor (`publicar_motor`), os dois por `publicar_arquivos`; os dois destinos. O `--apagar` não muda
  (é o fim da prova, de propósito).
- *Achados 3 e 4.* Causa: a frase do apagar era escrita por quem chamava, sem saber se o pedido de apagar tinha saído;
  e "não achei" logo depois de criar o rascunho virava "já sumiu". Regra: `apagar_publicacao` é o único que escreve a
  frase de cada desfecho, porque é ele que sabe se pediu (antes de pedir, ao pedir, depois de pedir); com
  `acabou_de_criar=True`, "não achei" é "não achei o rascunho para apagar; confira com --apagar", nunca "apagada". O
  `criar_rascunho` entra no `try` (se ele cria e a resposta se perde, o caminho de erro procura e apaga, ou diz que não
  achou). O pedido de apagar ao gh que sai e fica sem resposta (por tempo) é `SemResposta`: "pedi e não deu para
  conferir". Caminhos: o caminho de erro de `publicar_arquivos` (versão e motor) e o `--apagar`.
- *Achado 2 (D-813).* Causa: a regra única lia o nome do programa de dois jeitos (o lote pelo nome completado pelo
  Windows; a lista de nomes e o nome sozinho pelo texto cru). Regra: `windows._caminho_do_programa` devolve o nome
  como o Windows o completa (GetFullPathNameW para caminho com pasta; para o nome sozinho, o mesmo corte de pontos e
  espaços do fim), uma vez só, e `_programa_com_funcao_propria` usa só esse nome na lista, na pasta do Windows e no
  lote. Caminhos: `rodar_e_esperar`, `lancar_solto`, `abrir_em_grupo` (e por ele o vpk e o gh).
  **Achado junto, rodando:** o nome sozinho com ponto no fim também passava para programa DA PASTA DO WINDOWS:
  `rodar_e_esperar(["whoami.exe."])` rodou o whoami (o Windows corta o ponto e acha pelo PATH; `shutil.which` não
  acha). A mesma causa e o mesmo conserto.
- *Achado 6.* Causa: `_nao_e_programa_do_windows` respondia só sim ou não, e o "não consegui ler" virava a frase do
  "tem função própria". Regra: a recusa devolve o motivo (`_por_que_recusa`, um lugar só), com uma frase para cada um:
  tem função própria; não consegui ler o programa para saber se é um programa do Windows. Recusar na dúvida continua.
  Caminhos: os mesmos três.
- *Achado 10.* A segunda olhada depois do PATH: o `shutil.which` acha o nome sozinho com as extensões do PATHEXT (um
  `.BAT`), e só ela recusa. Teste com um lote achado pelo PATH.
- *Achado 7 (D-776).* Causa: `DestinoGitHub.soma` baixava para `%TEMP%` com a pasta e o jeito dele, fora da vigia e da
  conta. Regra: o download para somar usa a peça que já baixa vigiada (`baixar_vigiado`), dentro do rascunho do C:
  (`usar_rascunho`, dado pelo publicar logo que o rascunho nasce, com a vigia única), e a conta do espaço soma o maior
  arquivo que a leitura de volta pode baixar (`soma_pode_baixar`, de cada destino). Caminhos que chegam na soma:
  `publicar_arquivos` (cada arquivo), `obter_motor_publicado` (no começo e na conferência) e `_conferir_versao_lida`.
- *Achado 8 (§11.12, ponto 1).* Causa: o laço "rodar, olhar a vigia e fechar" estava escrito duas vezes (o vpk pela
  peça, num grupo; o gh com `subprocess` direto, sem grupo). Regra: `windows.rodar_em_grupo` (novo, na peça) é o único
  laço: abre pelo `abrir_em_grupo`, espera, olha a vigia e o tempo, fecha o grupo inteiro (conferido) e trata o
  Ctrl+C; com `capturar=True` guarda a saída. Caminhos: `empacotar.rodar_vpk` e `DestinoGitHub._gh` (todos os pedidos
  ao gh: view, create, upload, download, edit, delete).
- *Achado 11.* Causa: "lida de volta do disco" sem pedir ao Windows para gravar no disco. Regra: `windows.gravar_no_disco`
  (novo: o `flush` do Python e o `os.fsync`, que no Windows é o `_commit`), usada antes de conferir e de trocar o nome
  em todos os lugares dos meus arquivos que gravam num nome provisório e trocam: `empacotar.copiar_inteiro` (o envio e
  a leitura de volta da pasta, o motor baixado, o .msi), `empacotar.zipar_motor` e `windows._gravar_por_inteiro` (o
  aviso, os scripts, a tarefa, a pasta segura, o relatório). Fora da lista do pacote, não mexi: `montar_motor_kraken.py`
  também grava e troca (Ideias).
- *Achado 9:* o caminho do teste em texto cru. *Achado 5:* limite da peça (Ressalvas e "Cada proteção"). *Achado 12:*
  Lista de bugs ("Ideias e bugs").

**Volta 5 (relatório 4 de quem tentou quebrar). Antes de mexer: a causa, a regra num lugar só e os caminhos (grep por
`--apagar`, `comando_de_apagar`, `SemResposta`, `PublicacaoLiberada`, `pediu_para_liberar`, `abriu`, `_por_que_recusa`,
`gravar_no_disco`):**
- *Achado 1.* Causa: a volta 4 criou o lugar único do comando de apagar (`_Destino.comando_de_apagar`, com o `--pasta`
  da pasta das provas) e deixou três frases antigas escrevendo `--apagar <etiqueta>` à mão, sem o destino; na pasta das
  provas, quem segue a frase apaga no GitHub. Os caminhos (grep `--apagar` em `publicar_versao_kaique.py`): o "sobrou um
  rascunho" de `publicar_arquivos`, o "já existe" de `publicar` e o de `publicar_motor`; o resto já usa
  `comando_de_apagar` (a frase da D-816, as do `apagar_publicacao`, a da liberada no meio). Regra: toda frase que manda
  apagar chama `destino.comando_de_apagar(etiqueta)`.
- *Achado 2.* Causa: `apagar_publicacao` tratava qualquer `SemResposta` que saísse do apagar do destino como "o pedido
  de apagar saiu", e o `DestinoGitHub.apagar_rascunho` lê a situação ANTES de pedir: uma leitura sem resposta virava
  "pedi para apagar". Regra: só o pedido de apagar em si (`DestinoGitHub._pedir_para_apagar`) pode dizer "saiu e ficou
  sem resposta" (`ApagarSemResposta`, um caso de `SemResposta`); a leitura sem resposta é "não pedi".
- *Achado 3.* Duas proteções sem teste: (a) o `_gh` de verdade que fecha o gh por tempo levanta `SemResposta`; (b) o
  `except PublicacaoLiberada: raise` de `apagar_publicacao` (sem ele, a liberada no meio vira "não apaguei" comum e a
  frase "outra pessoa ... a liberou no meio" some). Um teste para cada, provado desligando numa cópia.
- *Achado 4 (escolha da gerente).* Causa: `pediu_para_liberar` era marcado antes de saber se o gh chegou a abrir; se o
  gh nem começa (o `rodar_em_grupo` devolve `abriu: False`: recusado pela peça, não achado, ou fechado ainda parado,
  antes de rodar), nada saiu do PC. Regra: o `_gh` diz isso com `NadaSaiu` (um caso de `Parou`), e o caminho de erro
  conta como "não pedi para liberar" só nesse caso, comprovado; e então, pela D-816, apaga o rascunho como antes do
  pedido. Qualquer outro erro depois de o gh abrir continua sendo pedido. A pasta das provas não muda (o liberar dela
  é a troca do nome da subpasta; não tem "não abriu").
- *Achado 5 (escolha da gerente, D-813).* Causa: a regra única olhava o nome do arquivo e o começo dele, mas não o
  jeito de escrever um FLUXO escondido de outro arquivo (`nada.txt:pwsh.exe`), que o Windows roda. Lido: Microsoft
  Learn, "File Streams" (o nome completo de um fluxo é "filename:stream name:stream type"; "filename::$DATA" é o
  próprio arquivo) e "Naming Files, Paths, and Namespaces" (o ":" é reservado no nome; depois da letra do disco, só
  aparece para fluxo). Regra: em `windows._por_que_recusa`, qualquer ":" depois da letra do disco (no caminho já
  completado) é recusado, com frase própria. Caminhos: `rodar_e_esperar`, `lancar_solto`, `abrir_em_grupo` (e por ele o
  vpk e o gh).
- *Achado 6.* Causa: o texto de `windows.gravar_no_disco` dizia "todo código que grava num nome provisório"; só três
  passam. Regra: o texto nomeia quem passa (`_gravar_por_inteiro`, `empacotar.copiar_inteiro`,
  `empacotar.zipar_motor`) e diz quem não passa (a ficha do motor, o PDF de saída, os projetos), sem mexer neles.

**Volta 6 (o defeito da prova à vista e os 3 baixos do relatório 5). O plano, escrito antes de mexer (D-709):**

*O defeito da prova.* Conferido no código de `b9300da8` e no registro da prova (`C:\EditorImpressaoProva\publicar-versao.log`,
só lido) e na pasta que a prova deixou (`dist\EditorImpressao`, só lida: tem o .exe, `_internal`, `tesseract`, a ficha
"versao 1.1.0, saida atualização", e **não tem** `instalar\`; `empacotar.conferir_pasta_pronta` sobre ela devolve só
"não tem o Visual C++ em instalar\"; `anexos/volta6-a-pasta-da-prova.txt`). A leitura da gerente está certa:
- **Onde aparece:** `publicar_versao_kaique.publicar` chama `empacotar.conferir_pasta_pronta(pasta, versao)` logo
  depois de `empacotar.construir_pasta(ATUALIZACAO)`, e a conferência cobra `instalar\vc_redist.x64.exe`.
- **A causa (não só onde aparece):** a regra "a pasta pronta para o vpk tem o Visual C++ em instalar\" (D-727) era
  cumprida em dois momentos diferentes conforme o caminho. A pasta que vem de fora (`--pasta-pronta`) tinha de chegar
  com ele; a pasta montada do zero só o recebia depois, em `empacotar.preparar_saida` (quando há `pecas`), dentro de
  `construir_pacote_do_velopack`, que roda DEPOIS da conferência. Ou seja: a montagem (`construir_pasta`) não deixava a
  pasta no estado que a própria conferência do empacotar cobra, e o "pôr o Visual C++" morava na preparação de cada
  saída, embora seja igual nas duas saídas do Velopack. Os testes não pegaram porque todos passam pela pasta de mentira
  `_pasta_pronta` (já com o Visual C++); nenhum teste do publicar passava pelo `construir_pasta` (família F3 e F1 do
  catálogo: a conferência acreditou num estado que o teste preparou).
- **A regra, num lugar só:** (1) o QUE cada saída leva continua em `empacotar.SAIDAS`; ganha o campo `vc_em_instalar`
  (a atualização e o instalador: sim; a pasta portátil: não, porque o Inno pega o Visual C++ de `build\`), como manda o
  comentário de `SAIDAS` ("Não escreva 'se for o instalador...' em outro lugar: acrescente um campo aqui"); (2) QUEM
  põe o Visual C++ é a montagem, `construir_pasta(saida)`, pela função de sempre (`preparar_pasta_para_o_velopack`),
  antes de gravar a ficha da versão (a ficha é o sinal de "montada inteira": se a cópia falhar, a pasta fica sem ficha
  e o `--pasta-pronta` a recusa); `preparar_saida` deixa de pô-lo (só faz o que muda entre as saídas: o
  motor-exigido.json e o arquivo do motor em instalar\); (3) QUEM DECIDE "a pasta está pronta para o vpk" é uma função
  só, `conferir_pasta_pronta`, sem mudar o que ela cobra; ela passa a ler o campo `vc_em_instalar` (para as duas saídas
  do Velopack, o mesmo de hoje) e é chamada também por `construir_pacote_do_velopack` logo antes de rodar o vpk, para
  todo caminho que chega ao vpk passar pela mesma conferência (hoje só o publicar a chamava; quem chamasse o empacotar
  direto chegava ao vpk sem ela). O publicar continua chamando-a cedo (antes da conta do espaço), com a frase de hoje.
  `esperados_no_pacote_do_velopack` também lê o campo (para as duas saídas, o mesmo de hoje).
- **Todos os caminhos que chegam na decisão** (grep `conferir_pasta_pronta`, `preparar_saida`,
  `preparar_pasta_para_o_velopack`, `construir_pasta`, `construir_pacote_do_velopack`, `VC_REDIST_NOME`,
  `PASTA_DO_QUE_SE_INSTALA`, `_PECAS`, em todo o projeto fora de `.venv`, `build` e `dist`):
  | Caminho | Hoje (`b9300da8`) | Depois |
  |---|---|---|
  | `publicar` montado do zero (sem `--pasta-pronta`) | `construir_pasta(ATUALIZACAO)` sem o Visual C++ → `conferir_pasta_pronta` recusa sempre | `construir_pasta(ATUALIZACAO)` põe o Visual C++ → a mesma `conferir_pasta_pronta` → `construir_pacote_do_velopack` (a mesma conferência de novo, antes do vpk) |
  | `publicar --pasta-pronta` | `conferir_pasta_pronta` (a pasta tem de trazer) | igual |
  | `publicar --com-instalador`, a segunda passada (o motor em instalar\) | `construir_pacote_do_velopack(INSTALADOR)` → `preparar_saida` (com `pecas` montado do zero: copia o Visual C++ de novo) → vpk, sem conferência | `preparar_saida` (só o motor) → `conferir_pasta_pronta(INSTALADOR)` → vpk |
  | a volta da pasta para a atualização depois do instalador (o `finally`) | `preparar_saida(pasta, ATUALIZACAO, None, motor)` (tira o arquivo do motor; não mexe no Visual C++) | igual |
  | `construir_pacote_do_velopack` chamado sozinho, sem pasta | `construir_pasta(ATUALIZACAO)` → `preparar_saida` com `_PECAS` põe o Visual C++ → vpk, sem conferência | `construir_pasta(ATUALIZACAO)` já põe → `conferir_pasta_pronta` → vpk (nenhum código chama assim hoje; grep) |
  | `construir_pacote_do_velopack` sozinho, com uma pasta de fora | `preparar_saida` sem `pecas` → vpk, sem conferência (o pacote sem o Visual C++ só era recusado DEPOIS do vpk) | `conferir_pasta_pronta` antes do vpk (nenhum código chama assim hoje) |
  | a pasta portátil (`empacotar.py --modo pasta`, `tudo`) e o Inno (`--modo instalador`, `entrega`) | `construir_pasta()` (PORTATIL), sem instalar\; o Inno pega o Visual C++ de `build\` | igual (`vc_em_instalar=False`) |
  | `empacotar.main` | só os modos do Inno e da pasta portátil; não chega ao vpk | igual |
  | a conferência do pacote depois do vpk (`conferir_pacote_do_velopack` → `esperados_no_pacote_do_velopack`) | cobra o Visual C++ sempre | cobra pelo campo (o mesmo para as duas saídas do Velopack) |
  | o programa instalado (`atualizacao.py`, que lê `instalar\`) | lê `<programa>\instalar\vc_redist.x64.exe` | não muda (o nome e o lugar são os mesmos) |
  Conta própria achada: só uma, a do `preparar_saida` (pôr o Visual C++ quando há `pecas`); ela sai. Nenhum outro lugar
  põe ou confere o Visual C++ do Velopack.
- **O que não muda (D-605):** o que `conferir_pasta_pronta` cobra de uma pasta que vem de fora; o nome e o lugar do
  arquivo (`atualizacao.PASTA_DO_QUE_SE_INSTALA`, `atualizacao.VC_REDIST_NOME`); a assinatura de `preparar_saida` e de
  `preparar_pasta_para_o_velopack` (testes antigos as chamam); a pasta portátil e o Inno.
- **A prova:** um teste em `tests/test_publicar_versao.py` que passa a pasta pelo `construir_pasta` de verdade (com
  `empacotar.RAIZ` numa pasta do teste; só o PyInstaller é trocado por quem escreve o que ele escreveria, lido do
  próprio `comando_do_pyinstaller`: o .exe e cada `--add-data` em `_internal\`; e as peças apontando para arquivos do
  teste, porque no Windows do GitHub não há Tesseract nem o Visual C++ baixado) e publica de verdade na pasta das
  provas, com e sem o instalador; e um teste que cobra o mesmo resultado da conferência em todos os caminhos da tabela.
  Rodado no código de `b9300da8`, o primeiro tem de falhar com "não tem o Visual C++ em instalar\".

*Os 3 baixos do relatório 5 (o Samuel: "pode concertar"):*
- **Achado 1 (o apagar em que o gh nem abre, sem teste).** Causa: a proteção (`NadaSaiu` não é um caso de
  `SemResposta`, então `_pedir_para_apagar` não o troca por "pedi") nunca foi percorrida por teste. Regra: não muda.
  Prova: um teste em que o pedido de apagar passa pelo `_gh` de verdade com um gh que não existe (o programa nem
  começa) e a frase diz "não apaguei", nunca "pedi para apagar"; desligada a proteção numa cópia (a mutação X3 de quem
  quebrou), o teste tem de falhar.
- **Achado 2 (na pasta das provas, a frase do motor que falta manda `--motor` sem o `--pasta`).** Causa: a frase de
  `obter_motor_publicado` escreve o comando à mão, fora do lugar único dos comandos do destino (o vizinho do achado 1 do
  relatório 4, família F2). Regra: o destino escreve também este comando (`_Destino.comando_de_publicar_o_motor`, ao
  lado de `comando_de_apagar`, pelos mesmos `_argumentos_do_destino`). Caminhos (grep `--motor` em
  `publicar_versao_kaique.py`, `empacotar.py`, `servidor_das_versoes.py`): só esta frase manda rodar o `--motor`; o
  resto é o cabeçalho e o `main`. Prova: a frase na pasta tem `--motor --pasta "<pasta>"`; no GitHub, `--motor` sem
  `--pasta`; e seguir a frase da pasta publica o motor na pasta.
- **Achado 3 (o caminho de rede recusado com a frase "tem função própria ... use a função dela").** Causa: quando
  `_caminho_do_programa` devolve "nada" (caminho de rede, ou caminho que o Windows não completa com uma letra de disco),
  `_por_que_recusa` usava a frase de outro motivo (o mesmo tipo do achado 6 do relatório 3, F7). Regra: uma frase
  própria, ao lado das outras frases da recusa (`FRASE_CAMINHO_DE_REDE`), dizendo o motivo de verdade: por esse
  caminho a peça não consegue saber se é um programa do Windows (que tem função própria na peça), e só roda programa
  deste computador pelo caminho com a letra do disco. Os testes antigos N2 e o do "raiz global" procuram "função
  própria" na recusa: a frase nova tem essas palavras porque é o motivo de verdade (Ressalvas). Caminhos: o rodar
  genérico, o lançar solto e o grupo, todos pela regra única `_por_que_recusa`. Prova: um teste pelos três caminhos com
  `\\localhost\C$\...` e `\\?\UNC\...`, que cobra a frase nova e que ela não manda "use a função dela".

**Volta 7 (o relatório 6 e a D-818). O plano, escrito antes de mexer (D-709):**

*Achado 1 (médio), pela D-818.*
- **Onde aparece:** `conferir_pasta_pronta` cobra do Visual C++ só que exista um arquivo com o nome certo; não cobra o
  arquivo da versão dele nem o Tesseract. A pasta de mentira dos testes (`_pasta_pronta`, 11 bytes, sem a versão, sem o
  Tesseract) passava e era publicada (sondas S1 e S1b do relatório 6).
- **A causa:** a mesma regra ("a pasta leva o Visual C++ oficial com a versão dele, e o Tesseract") tinha duas réguas.
  A montagem confere de verdade na hora de copiar (a assinatura da Microsoft em `preparar_vc_redist`, o tamanho em
  `preparar_pasta_para_o_velopack`, o Tesseract em `conferir_pecas_no_pacote`, contra o original); a conferência da
  pasta (a única que vê a pasta pronta) só olhava o nome. E a conferência do pacote depois do vpk só procurava o
  Tesseract quando havia peças (montado do zero), e nunca a versão do Visual C++. Família F1 e F5 do catálogo (acreditar
  num dado fraco; dar como pronto o que não conferiu).
- **A regra, num lugar só:**
  - "este arquivo é o Visual C++ oficial, e de que versão" → uma função, `empacotar.conferir_o_visual_c(arquivo)`
    (lê a assinatura pela peça do Windows, `assinatura_do_arquivo`, e a confere por `vc_redist_confere`; devolve a
    versão e os problemas). `preparar_vc_redist` passa a usá-la (hoje faz a mesma conta em dois lugares dentro dela) e
    a conferência da pasta também. A régua não muda.
  - "o que é o Tesseract dentro da pasta" → uma lista, `empacotar.relativos_do_tesseract()` (os 27 arquivos, as duas
    licenças e os seis idiomas). `_destinos_das_pecas` (o que a montagem copia, o que o Inno confere) e a conferência da
    pasta e do pacote usam a mesma lista. A lista não muda.
  - "a pasta está pronta para o vpk" → continua uma função, `conferir_pasta_pronta`, que passa a cobrar, nas saídas
    com `vc_em_instalar`: o Visual C++ pela `conferir_o_visual_c`; o arquivo da versão dele, igual à versão lida da
    assinatura (é o que o programa instalado lê para decidir se instala; `atualizacao.py:1230`); e, em toda saída, cada
    arquivo do Tesseract da lista, não vazio. A frase de cada falta é a mesma para a pasta montada e a pronta (é a
    mesma função).
  - "o pacote saiu certo" → `esperados_no_pacote_do_velopack` passa a cobrar sempre o Tesseract (pela lista, com ou sem
    peças) e, nas saídas com `vc_em_instalar`, o arquivo da versão do Visual C++.
- **Todos os caminhos** (grep `conferir_pasta_pronta`, `vc_redist_confere`, `assinatura_do_arquivo`,
  `preparar_vc_redist`, `_destinos_das_pecas`, `ARQUIVOS_DO_TESSERACT`, `LICENCAS_DO_TESSERACT`,
  `IDIOMAS_DO_INSTALADOR`, `esperados_no_pacote_do_velopack`, `VC_REDIST_VERSAO`, fora de `.venv`, `build`, `dist`):
  | Caminho | Hoje (`db4b377a`) | Depois |
  |---|---|---|
  | montagem: o Visual C++ baixado ou achado | `preparar_vc_redist`: `vc_redist_confere(assinatura_do_arquivo(...))`, escrito duas vezes | a mesma, pela `conferir_o_visual_c` |
  | publicar montado do zero, a conferência cedo | `conferir_pasta_pronta`: só o nome do Visual C++ | `conferir_pasta_pronta`: assinatura, versão, Tesseract |
  | publicar `--pasta-pronta` | o mesmo (só o nome) | o mesmo (a régua da montagem) |
  | `construir_pacote_do_velopack` (as duas passadas e o chamado sozinho) | `preparar_saida` e depois `conferir_pasta_pronta` | `conferir_pasta_pronta` ANTES de `preparar_saida` (achado 4), depois o vpk |
  | o pacote depois do vpk | `conferir_pacote_do_velopack`: o nome do Visual C++; o Tesseract só com peças | o Tesseract sempre e a versão do Visual C++ |
  | a montagem copia o Tesseract / o Inno confere | `_destinos_das_pecas` (a lista escrita ali) | a mesma lista, de `relativos_do_tesseract` |
  | o programa instalado (`atualizacao.instalar_visual_c_se_faltar`) | lê o vc_redist.versao.txt de instalar\ | não muda |
- **Os testes antigos:** a pasta de mentira ganha as peças (lista em "O que já está escolhido e testado aqui", Volta 7).
- **A prova:** um teste da D-818 em `tests/test_publicar_versao.py` (o arquivo das decisões não está na lista do
  pacote): a pasta pronta sem o Tesseract, com um Visual C++ falso (lido pela peça de verdade do Windows) e sem o
  arquivo da versão → o publicar para antes do vpk, com a mesma frase que a montada do zero dá no mesmo caso; e a
  montada do zero continua passando. Falha em `db4b377a`.

*Os 4 baixos do relatório 6:*
- **Achado 2 (o item 14 do roteiro depois do 13):** só o roteiro: o 14 passa para antes do 13, e entra o que o
  relatório 6 pede para a prova ("O que falta para a prova à vista", item 2).
- **Achado 3 (duas conferências do pacote sem teste):** o vpk de mentira ganha a opção de deixar caminhos de fora; um
  teste para cada falta (o Visual C++, a versão dele, o Tesseract), pelo publicar, que cobra "o pacote do Velopack saiu
  errado" e nada publicado.
- **Achado 4 (o empacotar chamado sozinho mexe na pasta antes de recusá-la):** a conferência vem antes de
  `preparar_saida` (ela não depende de nada que `preparar_saida` faz). Teste: a pasta recusada continua como estava
  (o zip do motor em instalar\ fica, o motor-exigido.json não aparece).
- **Achado 5 (as aspas do `--pasta "<pasta>"` sem teste):** um teste com uma pasta das provas com espaço no nome, que
  segue a frase do motor e a do apagar ao pé da letra e confere que chegam à pasta certa.

**Volta 8 (os 2 defeitos da prova à vista de 20/11 e os 6 baixos do relatório 7). O plano, escrito antes de mexer
(D-709):**

*Defeito 1: as peças procuradas no lugar errado numa cópia de trabalho (só o plano; PARADO, ver "Perguntas para o
Samuel").*
- **Onde aparece:** prova 6b (`C:\EditorImpressaoProva\prova6b.log`): seguida ao pé da letra a frase do próprio
  publicar (`--motor --pasta "C:\EditorImpressaoProva\versoes 2"`), rodada da cópia `.claude\worktrees\passo2`, parou em
  "não achei um motor pronto do jeito novo: ... não existe D:\programas\EditorImpressao\.claude\worktrees\EditorImpressao-arquivos\ferramentas\motor-kraken".
  O Visual C++ só foi achado porque havia uma cópia idêntica no lugar errado:
  `D:\programas\EditorImpressao\.claude\worktrees\EditorImpressao-arquivos\ferramentas\downloads\vc_redist.x64.exe`
  (19/11, 15h44, 25.635.768 bytes; só listado, não mexi).
- **A causa:** cinco lugares calculam, cada um por conta própria, "a pasta das ferramentas do Samuel" como "a pasta de
  cima de onde está este arquivo de código" + `EditorImpressao-arquivos\ferramentas`: `empacotar.DOWNLOADS`,
  `empacotar.LUGARES_DO_MOTOR`, `core/ocr_kraken.lugares_do_motor` (o defeito antigo nº 330), `montar_motor_kraken.PASTA_FERRAMENTAS`
  e `compilar_detector_gravura.PASTA_FERRAMENTAS_PADRAO`. Isso só está certo quando o código roda da pasta principal
  (`D:\programas\EditorImpressao`); numa cópia de trabalho (`D:\programas\EditorImpressao\.claude\worktrees\<nome>`) a
  pasta de cima é `.claude\worktrees`. Um sexto lugar, `compilar_st_ferramentas.pasta_de_ferramentas_padrao` (fora da
  lista do pacote), tem uma terceira conta: sobe as pastas e fica com a primeira `EditorImpressao-arquivos\ferramentas`
  que existir; hoje, numa cópia em `.claude\worktrees`, ela acharia justamente a pasta errada de 19/11. E o
  `empacotar.preparar_vc_redist` cria a pasta das ferramentas onde a conta mandar (`DOWNLOADS.mkdir(parents=True)`): foi
  assim que a pasta errada nasceu (um empacotar rodado de uma cópia, que baixou o Visual C++ para lá). Família F4 do
  catálogo (o código supõe o computador de hoje: "roda da pasta principal") e conta copiada (§11.12).
- **A regra, num lugar só:** "a pasta das ferramentas do Samuel" = a pasta ao lado da **pasta principal do
  repositório**, `<principal>\..\EditorImpressao-arquivos\ferramentas`. Quem sabe a pasta principal é o git: numa cópia
  de trabalho, o `.git` dela aponta para a pasta de git da principal (documentação do git-worktree, "DETAILS", e do
  git-rev-parse, `--git-common-dir`; fontes em "O que li", Volta 8). Uma função só (proposta: `pasta_das_ferramentas`,
  num módulo de `core/` que o programa e os scripts importam), e os seis lugares passam a usá-la; os nomes antigos
  (`empacotar.DOWNLOADS`, `empacotar.LUGARES_DO_MOTOR`, `montar_motor_kraken.PASTA_FERRAMENTAS`,
  `compilar_detector_gravura.PASTA_FERRAMENTAS_PADRAO`) continuam existindo, calculados por ela (os testes antigos os
  trocam pelo nome).
- **Por que parei:** a peça única do git (`regras_dos_agentes/conversa_com_o_git.py`, já usada pelo empacotar e pelo
  publicar para ler o commit) não tem a pergunta "qual é a pasta principal desta cópia", e esse arquivo não está na lista
  do pacote. Junto: a função nova precisa morar num módulo novo de `core/` (ou em `core/ocr_kraken.py`, que está na
  lista, mas não é o lugar natural para "onde ficam o Qt e o Boost do ScanTailor"), e o `compilar_st_ferramentas.py`
  (fora da lista) tem a terceira conta. E há dois cuidados que mudam o desenho (detalhe em "Perguntas para o Samuel"):
  (1) o `core/ocr_kraken` roda também dentro da janela do programa pelas fontes; perguntar ao git de lá abre o git como
  programa de console e, sem cuidado, pisca uma janela preta na tela do Samuel; (2) o programa do Kaique (empacotado)
  nunca pode perguntar ao git, e a peça do git não pode ir dentro do pacote dele.
- **Todos os caminhos que chegam na conta** (grep `RAIZ.parent`, `EditorImpressao-arquivos`, `PASTA_FERRAMENTAS`,
  `LUGARES_DO_MOTOR`, `DOWNLOADS`, `lugares_do_motor`, `pasta_de_ferramentas_padrao`, fora de `.venv`, `build`, `dist`):
  | Caminho | Conta que usa hoje | Depois (o plano) |
  |---|---|---|
  | `publicar --motor` (achar o motor a publicar) | `empacotar.achar_motor_kraken` → `LUGARES_DO_MOTOR` (a conta 1) | a função única |
  | `publicar` e `empacotar` (o Visual C++ baixado) | `empacotar.preparar_vc_redist` → `DOWNLOADS` (a conta 1), e cria a pasta | a função única; só cria `downloads\` dentro de uma pasta de ferramentas que já existe |
  | `empacotar --modo pasta/tudo` (o motor solto) | `achar_motor_kraken` → `LUGARES_DO_MOTOR` | a função única |
  | `montar_motor_kraken.py` (onde montar e baixar) | `PASTA_FERRAMENTAS` (a conta 1) | a função única |
  | `compilar_detector_gravura.py` (Qt, Boost, rascunho) | `PASTA_FERRAMENTAS_PADRAO` (a conta 1) | a função única |
  | `compilar_st_ferramentas.py` | `pasta_de_ferramentas_padrao` (sobe as pastas; a conta 3) | a função única (fora da lista) |
  | o programa pelas fontes e os testes (`core/ocr_kraken.lugares_do_motor`) | a conta 2 (a mesma ideia, escrita de novo) | a função única, sem janela |
  | o programa do Kaique (empacotado) | o motor ao lado do programa (primeiro lugar da lista) | igual; nunca pergunta ao git |
- **O que pode falhar** e **a prova**: em "O que pode falhar", Volta 8, e em "Perguntas para o Samuel".

*Defeito 2: a frase depois de apagar.*
- **Onde aparece:** provas 3a, 5 e 7c: o `--apagar` apagou de verdade (a gerente conferiu na pasta e no GitHub), e a
  única frase foi "v1.1.0: não existe em ... (conferido)", a mesma de quando não havia nada.
- **A causa:** quem sabe se havia o que apagar é o lugar único do apagar (`apagar_publicacao`: ele lê a situação antes);
  mas ele devolve só o aviso do destino (ou nada), nos dois casos. O `main` do `--apagar` escrevia a sua própria frase,
  fora do lugar único, sem saber qual dos dois casos foi. O caminho de erro do publicar escreve uma terceira frase
  ("foi apagada (conferido)"), também fora. Três lugares, duas frases, e a do `--apagar` errada (F5 e F7).
- **A regra, num lugar só:** o apagar conferido devolve o que fez (havia ou não havia o que apagar, e o aviso), e a frase
  de cada desfecho sai dele: "a publicação X foi apagada de Y (conferido)" e "X: não existia em Y, e nada foi apagado
  (conferido)". O `--apagar` e o caminho de erro passam a imprimir essa frase. `apagar_publicacao` continua devolvendo o
  aviso (os testes antigos cobram isso), pela mesma conta.
- **Caminhos** (grep `apagar_publicacao`, `não existe em`, `foi apagada`): o `--apagar` do `main` (pasta e GitHub,
  versão e motor), o caminho de erro de `publicar_arquivos` (só rascunho, logo depois de criar: "não existia" não
  acontece ali, vira a frase "não achei o rascunho"). Não há outro lugar que apague publicação.

*Os 6 baixos do relatório 7:*
- **(1) As duas proteções do Visual C++ sem teste** (mutações W1 e W5 do relatório 7). Causa: os testes novos só usavam
  um arquivo sem assinatura (qualquer régua recusa) e nenhum fazia a leitura falhar. Regra: não muda. Prova: (a) a
  peça do PowerShell responde "não terminou" → a pasta é recusada com "não é o oficial da Microsoft" (não pela versão
  diferente) e a montagem também; (b) uma cópia do `powershell.exe` do Windows (assinatura válida, de "CN=Microsoft
  Windows") como Visual C++ na pasta e na pasta de downloads → recusada pelos dois, lida pela peça de verdade.
- **(2) A versão do Visual C++ comparada inteira:** casos novos "arquivo da versão vazio" e "só um pedaço" ("14.44").
- **(3) As licenças do Tesseract:** caso novo "sem a licença" na pasta (`tesseract/LICENSE` e `tesseract/AUTHORS`) e o
  pacote do vpk sem a licença.
- **(4) A família repetida:** é da gerente (catálogo dos erros, F3); só cito. Para esta volta: cada mutação minha tira
  uma condição de dentro da proteção, não só a desliga inteira.
- **(5) O item 14 do roteiro:** a linha "Visual C++: ..." só aparece quando a montagem começa (item 15); o item passa a
  dizer isso.
- **(6) O arquivo da versão do Visual C++ lido de dois jeitos.** Causa: quem escreve é a montagem
  (`empacotar.preparar_pasta_para_o_velopack`, UTF-8); quem lê são dois: a conferência do publicar
  (`empacotar.conferir_pasta_pronta`: UTF-8 trocando os caracteres ruins, tira os espaços; o que a prova conferiu) e o
  programa instalado (`atualizacao.instalar_visual_c_se_faltar`: UTF-8 estrito, tira os espaços; "0.0.0" se o arquivo
  não existe). Regra: uma leitura só, a do publicar, numa função de `atualizacao.py` (o programa instalado não pode
  importar o empacotar; o empacotar já importa o `atualizacao` para o nome e o lugar do arquivo). As duas passam a
  chamá-la; o que cada uma faz com "não existe" continua o de hoje (o publicar recusa; o programa instalado usa "0.0.0").
  A frase do publicar não muda.

*O texto do formulário (o conferidor devolvia):* a linha da D-818 da Volta 7 (o contexto entre aspas lido como fala do
Samuel) passa a descrever a pergunta sem aspas; as citações do vpk de mentira e do arquivo da versão do Visual C++ saem
do jeito que o conferidor lê como "arquivo ou teste citado"; "Arquivos criados ou alterados" passa a listar só o que
mudou desde a partida desta volta (as listas das voltas anteriores ficam no `git log` e nos pacotes).

## O que pode falhar e o que o programa faz

| O que pode dar errado | O que o publicar faz |
|---|---|
| Sem licença de administrador | não precisa: nada do publicar pede licença (0 perguntas do Windows) |
| A pessoa diz "Não" | não há pergunta do Windows neste passo; não se aplica |
| Sem a chave, ou chave que não é a do programa | para antes de tudo (como hoje); nada é criado |
| A versão já foi publicada (ou sobrou um rascunho dela no destino) | para antes de montar, dizendo qual e como apagar o rascunho |
| O motor que a versão pede não está publicado, ou a assinatura dele não confere | para antes de montar: "publique o motor antes (--motor)" |
| Disco cheio antes (sobraria menos de 20 GB no C:) | para antes do vpk, dizendo quanto precisa e quanto há; o rascunho vazio é apagado |
| Disco cheio durante (outra coisa usando o C:) | a vigia vê o espaço cair abaixo da reserva, fecha o vpk que este comando abriu (só ele), o rascunho é apagado e a frase diz quanto ficou livre |
| O vpk falha ou não está instalado | para com o aviso; o rascunho é apagado |
| O pacote sai sem uma peça, ou com o motor dentro na atualização | para; o rascunho é apagado; nada vai ao destino |
| A pasta pronta é de outra versão, não tem a ficha, ou não tem o Visual C++ | para antes do vpk |
| Sem internet, ou o gh sem conta | para; se o rascunho do destino já tinha sido criado, é apagado e conferido; se não der para apagar, a frase diz o que ficou e o comando de apagar |
| O GitHub não responde ao perguntar se a versão existe | para (nunca vira "não existe") |
| A leitura de volta não bate (o arquivo no destino tem outra soma, ou a assinatura não confere) | não libera; apaga o rascunho do destino e confere |
| O Setup.exe | é apagado logo depois de cada vpk e o rascunho inteiro some no fim (também com erro); a conferência do fim lê a pasta de saída e o destino e diz se ele está lá |
| Arquivo preso (o antivírus lendo) ao apagar o rascunho | tenta de novo por alguns segundos; se ficar, diz o caminho e o tamanho do que ficou (nunca "apagado" sem conferir) |
| Arquivo preso por outro programa ao enviar | o envio falha → mesmo caminho da falha de internet |
| Desligar no meio (o PC ou a energia) | o rascunho fica no C: e o rascunho do destino fica sem liberar (nunca liberado pela metade); na próxima vez o comando acha o rascunho velho do destino e para dizendo como apagar; o rascunho velho do C: é apagado no começo da próxima vez (só as pastas com o nome do publicar) |
| O publicar roda dentro de um PowerShell 7 (terminal pwsh) | a peça abre o PowerShell do Windows sem a lista de módulos herdada: a assinatura do Visual C++ é lida igual (antes falhava com CouldNotAutoloadMatchingModule) |
| Um atalho (junção) dentro da pasta de troca do lançar solto, ou uma publicação do destino que é atalho | o lançar solto tira só o atalho e apaga o resto; o destino para sem apagar nada e diz que é atalho |
| O apagar de um rascunho no GitHub (o gh sai com erro mesmo tendo apagado, delete.go) | o rascunho é apagado sem pedir a etiqueta, e quem decide se apagou é a leitura de volta; o aviso do gh vai na frase |
| A vigia fecha o vpk com o WiX rodando (o .msi) | o vpk roda num grupo do Windows: fechar fecha ele, o cmd.exe e o wix.exe, e confere no Windows que nenhum ficou vivo; se ficou, a frase diz e manda olhar o Gerenciador de Tarefas |
| Erro do disco que não é dos previstos (pasta que não cria, arquivo preso ao somar, cópia do .msi) | a linha de comando diz "PAREI: o disco não deixou terminar (o arquivo): o motivo"; o rascunho já foi apagado pelo fim de cada caminho |
| A leitura depois de liberar falha | não apaga a versão liberada (achado 4); diz "liberada; não deu para reconferir agora" |
| Ctrl+C no meio | o mesmo caminho do erro: o vpk é fechado, o rascunho é apagado e o do destino também; a frase diz "interrompido" (sem a tela de erro do Python) |
| Dois publicar ao mesmo tempo | cada um tem o seu rascunho; o rascunho de outra vez só é apagado se tiver mais de 12 horas (antes, pode ser do outro rodando); a mesma versão no mesmo destino é recusada pelo segundo (já existe um rascunho) |
| O instalador pedido e a publicação falha depois | o .msi só vai para a pasta de saída depois de a versão estar publicada: um .msi de versão que não saiu nunca fica lá |
| O servidor: porta ocupada | a janela diz "NÃO ESTÁ SERVINDO" e o motivo, e não serve nada (a porta é exclusiva: outro servidor não abre a mesma) |
| O servidor: fechar no meio de um envio | corta a conexão de quem está baixando; quem baixa recebe menos do que o tamanho anunciado (o Velopack confere a soma e recusa) |
| O servidor: pedido de arquivo fora da pasta ("..", caminho com barra, o rascunho) | recusado (404), com a linha na janela |

| (volta 3) A resposta do liberar se perde e a leitura logo depois vem atrasada | a versão liberada nunca é apagada: o apagar só toca no rascunho, lido de novo na hora (na pasta, pela construção); a frase diz "ficou liberada ... NÃO apaguei" |
| (volta 3) O GitHub libera entre a leitura e o pedido de apagar (um instante) | fica o risco: o GitHub não tem "apague só se for rascunho" (Ressalvas) |
| (volta 3) A cópia do .msi para a pasta de saída falha (D: cheio, Ctrl+C) ou o publicar é fechado no meio | nenhum .msi com o nome certo fica pela metade (nome provisório); na falha o pedaço é apagado e conferido; a frase diz que a versão foi publicada e o instalador está na publicação; a conferência do fim compara o .msi da saída com o do rascunho |
| (volta 3) Um .bat ou .cmd (ou um lote com outro nome) pedido à peça | recusado antes de rodar ("este programa do Windows tem função própria na peça") |
| (volta 3) Um filho aberto no primeiro instante do vpk | não escapa: o vpk nasce parado e só é solto dentro do grupo |
| (volta 3) O Windows não responde à leitura do grupo depois de fechar | "não deu para conferir (o Windows não respondeu à leitura do grupo)", nunca "conferido" nem "continua rodando" |
| (volta 3) O C: cai abaixo da reserva enquanto o motor é baixado para o instalador | a vigia para o download (a cópia da pasta ou o gh), o segundo vpk não roda, o rascunho é apagado |
| (volta 3) A segunda pasta de troca do lançar solto não nasce | a primeira é apagada na hora |

| (volta 4) O pedido de liberar sai e a resposta se perde, a leitura vem atrasada (1, 2 ou mais vezes), a internet cai ou Ctrl+C depois do pedido | nada é apagado em nenhum destino, sem ler; a frase diz que pode ter ficado liberada (inteira) ou rascunho, como conferir e o comando de apagar o rascunho |
| (volta 4) O pedido de liberar falha com resposta (o destino diz que não liberou) | o mesmo: depois do pedido, nunca apaga (D-816); a frase diz que pode ter ficado rascunho e o comando de apagar |
| (volta 4) Antes do pedido de liberar: o erro, e a leitura de antes de apagar falha | não pede para apagar; a frase diz "não pedi para apagar" e o comando para conferir e apagar |
| (volta 4) Antes do pedido de liberar: pede para apagar e a leitura de depois falha | a frase diz "pedi para apagar e não deu para conferir se sumiu" (nunca "NÃO apaguei") |
| (volta 4) O rascunho acabou de ser criado e a leitura ainda não o acha | não pede nada; a frase diz "não achei o rascunho para apagar; confira com --apagar" (nunca "foi apagada") |
| (volta 4) A criação do rascunho chega ao destino e a resposta se perde | o caminho de erro procura o rascunho: achou, apaga e confere; não achou, diz que não achou e o comando |
| (volta 4) O gh do apagar sai sem resposta (fechado por tempo) | "pedi para apagar e não deu para conferir" |
| (volta 4) O programa pedido à peça com ponto ou espaço no fim (`pwsh.exe.`, `Update.exe.`, `whoami.exe.`) | recusado como o nome sem o ponto (o nome é lido como o Windows o completa) |
| (volta 4) O programa não deixa ler o começo (os atalhos da Loja, WindowsApps) | recusado, com a frase "não consegui ler o programa para saber se é um programa do Windows" |
| (volta 4) O GitHub não dá a soma pronta de um arquivo | baixa para o rascunho do C: pela vigia, soma e apaga; na conta do espaço entra o maior arquivo que pode ser baixado; abaixo da reserva, para e o rascunho é apagado |
| (volta 4) A leitura de volta precisa baixar para somar e não há rascunho (quem chama não deu) | para com a frase (nunca baixa para outro lugar) |
| (volta 4) O gh não abre (não instalado) | "não consegui falar com o GitHub pelo gh" (como hoje); nada foi pedido |
| (volta 4) O gh passa do tempo ou a vigia manda parar | o grupo inteiro é fechado e conferido; a frase diz o motivo; o pedido conta como "sem resposta" |
| (volta 4) Ctrl+C com o gh rodando | o grupo é fechado e a interrupção segue (o mesmo jeito do vpk) |
| (volta 4) O Windows não grava no disco (o pedido de gravar falha) | a cópia falha como erro do disco: o pedaço é apagado e conferido; o nome certo nunca aparece |

| (volta 5) Na pasta das provas sobrou um rascunho, ou a versão ou o motor já existem | a frase dá o comando de apagar COM o `--pasta` (o lugar único `comando_de_apagar`); seguir a frase nunca toca o GitHub |
| (volta 5) Antes do pedido de liberar, a leitura de dentro do apagar do rascunho fica sem resposta | a frase diz "não apaguei" e não "pedi para apagar"; só o pedido de apagar que saiu e ficou sem resposta diz "pedi" |
| (volta 5) O gh nem abre no pedido de liberar (não achado, recusado, fechado antes de rodar) | conta como "não pedi para liberar": o rascunho é apagado e conferido, como antes do pedido (D-816) |
| (volta 5) O gh abre no pedido de liberar e qualquer coisa dá errado depois (erro, tempo, vigia, Ctrl+C) | continua contando como pedido: nada é apagado (D-816) |
| (volta 5) O programa pedido à peça é um fluxo escondido de outro arquivo (`arquivo:nome.exe`) | recusado pelo rodar, pelo lançar solto e pelo grupo, com a frase própria do fluxo |

| (volta 6) Falta o Visual C++ no PC e não há internet para baixá-lo | como hoje: a montagem para antes do PyInstaller ("Visual C++: não consegui baixar..."); nada é apagado nem montado |
| (volta 6) A cópia do Visual C++ para instalar\ falha no meio (o D: cheio, o antivírus segurando) | o erro do disco sobe como hoje ("PAREI: o disco não deixou terminar"); se a cópia termina menor, a montagem para com "chegou pela metade" e devolve "nada". Nos dois casos a ficha da versão NÃO é gravada (ela vem depois): a pasta pela metade fica em `dist\` (como qualquer montagem que para) e um `--pasta-pronta` nela é recusado ("não tem a ficha da versão: monte de novo"); a próxima montagem apaga a pasta e começa do zero |
| (volta 6) Uma pasta de fora sem o Visual C++ (`--pasta-pronta`), como a que a prova de 20/11 montou com o código antigo | recusada antes da conta do espaço, com a frase de hoje ("não tem o Visual C++ em instalar\") |
| (volta 6) Quem chamar o empacotar direto com uma pasta sem o Visual C++, sem a ficha ou de outra versão | recusado antes de rodar o vpk (antes, o vpk rodava e só a conferência do pacote pegava) |
| (volta 6) Na pasta das provas, o motor que a versão pede não está publicado | a frase dá o comando com o `--pasta` (`publicar_versao_kaique.py --motor --pasta "<pasta>"`); seguida, publica o motor na pasta, nunca no GitHub |
| (volta 6) O gh nem abre no pedido de apagar (não achado, recusado pela peça) | "não apaguei" e o comando para conferir e apagar; nunca "pedi para apagar" (como hoje; agora com teste) |
| (volta 6) Um caminho de rede (`\\computador\...`, `\\?\UNC\...`) ou um caminho que o Windows não completa com letra de disco pedido à peça | recusado como hoje, pelos três caminhos, com a frase própria (o motivo e o que fazer), sem mandar usar uma função que não existe |

| (volta 7) A pasta já montada (ou a montada do zero) com um Visual C++ que não é o oficial | recusada antes da conta do espaço: "o Visual C++ da pasta ... não é o oficial da Microsoft: <o que a assinatura diz>"; nada é mudado nela |
| (volta 7) Sem o arquivo da versão do Visual C++, ou com uma versão que não é a do arquivo | recusada: "não tem a versão do Visual C++ (...)" ou "diz que o Visual C++ é o X ..., e o arquivo dele é o Y (pela assinatura)" |
| (volta 7) Sem o Tesseract, sem um idioma, ou com um arquivo dele vazio | recusada: "não tem o Tesseract inteiro: falta <os primeiros cinco> e mais N" |
| (volta 7) O Windows não responde à leitura da assinatura (a peça falha) | a leitura vira "erro: <motivo>", que nunca confere: a pasta é recusada com esse motivo (nunca passa por "não deu para ler") |
| (volta 7) O vpk deixa de fora do pacote o Visual C++, a versão dele ou um arquivo do Tesseract | "o pacote do Velopack saiu errado", com a peça; nada é publicado; o rascunho é apagado |
| (volta 7) O empacotar chamado sozinho com uma pasta que não serve | recusada antes de qualquer mudança na pasta (antes, o motor-exigido.json era gravado e o zip do motor apagado) |
| (volta 7) A pasta das provas com espaço no nome | os comandos das frases saem com o caminho entre aspas; seguidos, chegam a essa pasta |

**Volta 8.**
- *Defeito 1, sem git* (o notebook do Kaique; uma cópia feita com `git archive`, sem `.git`): pelo plano, a pergunta ao
  git falha ("o git não está instalado" ou "não é um repositório") e a função única cai na conta de hoje (a pasta de
  cima do código), que é a certa quando o código roda da pasta principal; o programa empacotado nunca pergunta (o motor
  fica ao lado dele). Nunca "achei" sem a pasta existir.
- *Defeito 1, cópia sem a pasta de ferramentas* (a pasta principal não tem `EditorImpressao-arquivos` ao lado; o
  Windows do GitHub): a frase de hoje ("não existe ...", com cada lugar procurado), com o lugar certo; e a montagem não
  cria a pasta das ferramentas (só `downloads\` dentro de uma que já existe), para nunca mais nascer uma pasta no lugar
  errado.
- *Defeito 1, pasta com espaço no nome* (a cópia ou a principal): o git devolve o caminho como está; a frase do motor já
  põe o `--pasta "<pasta>"` entre aspas (teste da volta 7). A prova roda numa pasta com espaço.
- *Defeito 1, janela na tela:* perguntar ao git de dentro da janela do programa (pelas fontes) não pode abrir janela de
  console; e o programa do Kaique não leva a peça do git (ver "Perguntas para o Samuel").
- *Defeito 2:* a leitura de antes falha, o pedido não sai, fica sem resposta, a leitura de depois falha, continua lá:
  cada um continua com a frase de hoje (só "apagada" e "não existia" mudam, e só saem com a leitura de volta conferida).
  Sem internet no `--apagar` do GitHub: a leitura de antes falha, "NÃO pedi para apagar nada" (como hoje).
- *Baixo 6:* o arquivo da versão não existe (o publicar recusa; o programa instalado usa "0.0.0", como hoje); sem
  licença de leitura ou arquivo preso pelo antivírus (o erro do disco sobe, como hoje nos dois); em UTF-16 ou com a marca
  de UTF-8 (o publicar recusa, e o programa instalado lê o mesmo texto que o publicar leu: hoje o UTF-16 levantava erro no
  programa instalado); disco cheio e desligar no meio: não se aplica a ler um arquivo de poucos bytes (nada é gravado).
- *Baixos 1 a 3 e 5:* só testes e o roteiro; o programa não muda.
- Esta volta não pede licença ao Windows, não pede "Sim" ou "Não" a ninguém e não fala com a internet.

## O que li da peça de fora e onde

Código do Velopack na etiqueta 1.2.161 (commit `92d6a1c9`, MIT), cópia só para ler em
`D:\programas\EditorImpressao\saida_teste\publicar-rapido\fonte-velopack\repo`:
- `src/vpk/Velopack.Packaging/PackageBuilder.cs:60` a 190: o vpk pack lê a versão anterior da pasta de saída só para a
  diferença (com `--delta None` não a faz); se a pasta de saída já tem versão igual ou maior, **pergunta** ("Do you want
  to continue...?"): por isso a pasta de saída é sempre nova; o portátil só sai sem `--noPortable`; o Setup.exe sai
  sempre que não houver `--noInst`; no fim move tudo para a pasta de saída e grava a lista dos arquivos
  dele, o índice das versões e o RELEASES antigo.
- `src/vpk/Velopack.Packaging/PackOptionsValidator.cs:19`: "Cannot use 'noPortable' and 'noInst' options together"
  (por isso o Setup.exe sempre sai, D-795).
- `src/vpk/Velopack.Vpk/Commands/Packaging/PackCommand.cs:89` a 117: `--delta` (de fábrica `BestSpeed`),
  `--noPortable` e `--noInst` (escondidos); `src/vpk/Velopack.Vpk/Commands/Packaging/WindowsPackCommand.cs:101`:
  `--msi`.
- `src/vpk/Velopack.Packaging.Windows/Commands/WindowsPackCommandRunner.cs:200` a 252: o Setup.exe leva o pacote
  inteiro dentro; o .msi copia a pasta do programa outra vez e a comprime (não leva o pacote).
- `src/vpk/Velopack.Core/DefaultName.cs:5` a 63: os nomes `<id>-<versao>-full.nupkg`, `<id>-win-Setup.exe`,
  `<id>-win.msi`, `<id>-win-Portable.zip` (o sufixo é "-" mais o canal, "win"). Conferido na pasta da etapa 5
  (`D:\programas\EditorImpressao\saida_teste\etapa5\servidor`): os mesmos nomes.
- `src/lib-csharp/Util/TempUtil.cs:20` a 45: a pasta temporária do vpk é a da variável VELOPACK_TEMP, senão
  TMPDIR, TEMP ou TMP mais "velopack". Por isso `empacotar.rodar_vpk` dá ao vpk as três dentro do rascunho.
- `src/vpk/Velopack.Core/BuildAssets.cs:72` e `src/vpk/Velopack.Deployment/_GitRelease.cs:213` a 262: o upload do vpk
  para o GitHub envia **todos** os arquivos da lista (inclusive o Setup.exe) e falha se faltar um; com publish, libera
  logo depois de enviar. `src/vpk/Velopack.Deployment/Local.cs:115` e `_ObjectStore.cs:215`: o upload para uma pasta
  também envia todos. Por isso o publicar não usa mais o upload do vpk (o Setup.exe chegaria ao rascunho do GitHub,
  contra a D-795, e a liberação viria antes da assinatura).
- `src/vpk/Velopack.Packaging/ReleaseEntryHelper.cs:100` a 134: o índice da pasta de saída lista os pacotes da pasta
  (com a pasta nova, só esta versão) com a soma SHA-256 e o tamanho; é o mesmo formato que o upload envia.
- Do lado do programa, `src/lib-rust/src/sources/http.rs:42` a 70 e `src/lib-rust/src/sources/mod.rs:64`: um endereço
  http:// vira a fonte HTTP, que pede o índice com "?localVersion=...&id=...&stagingId=..." e baixa
  "<endereço>/<FileName>". É o que o servidor das versões responde.

**Lido na volta 2:** https://github.com/cli/cli/blob/trunk/pkg/cmd/release/delete/delete.go (deleteRun e deleteTag):
o gh apaga a publicação e, com `--cleanup-tag`, apaga depois a etiqueta sem olhar se é rascunho, e devolve o erro dessa
segunda parte; num rascunho a etiqueta não existe. Microsoft Learn, https://learn.microsoft.com/windows/win32/procthread/job-objects
e AssignProcessToJobObject: o que um processo do grupo cria entra no grupo; TerminateJobObject fecha todos; com
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, fechar a última alça fecha todos; grupos dentro de grupos desde o Windows 8. O vpk:
`src/vpk/Velopack.Packaging.Windows/Msi/MsiBuilder.cs:221` (o .msi sai de `Exe.RunHostedCommand`, que abre
cmd.exe e wix.exe), `src/vpk/Velopack.Packaging/PackageBuilder.cs:76` (a pasta temporária vive até o fim do pack) e
`src/vpk/Velopack.Packaging.Windows/Commands/WindowsPackCommandRunner.cs:231` (a cópia a mais do .msi).

O gh 2.99.0 (instalado no PC), código `cli/cli`, https://github.com/cli/cli/blob/trunk/pkg/cmd/release/shared/fetch.go
(lido em 19/11): `FetchRelease` acha uma publicação liberada pela etiqueta ou um rascunho pela etiqueta pendente; sem
nenhuma, o erro "release not found". Os campos de `--json` incluem `isDraft` e `assets` (cada um com `name`, `size` e
`digest`). `gh release download <etiqueta> --pattern <nome> --dir <pasta>` baixa (vale para rascunho).

Microsoft Learn, https://learn.microsoft.com/dotnet/api/system.management.automation.signaturestatus: os estados de
`Get-AuthenticodeSignature` são Valid, UnknownError, NotSigned, HashMismatch, NotTrusted, NotSupportedFileFormat e
Incompatible; "Valid" diz só que a assinatura é válida (quem assinou, o nosso `empacotar.vc_redist_confere` confere).
Conferido rodando: o PowerShell do Windows dá "Valid" com a Microsoft; um script sem assinatura dá "NotSigned"; um
arquivo que começa com "MZ" e não é programa dá "UnknownError".

Python 3.14, https://docs.python.org/3/library/: `shutil.disk_usage` (o espaço livre do disco de uma pasta);
`subprocess.Popen.kill` (fecha só o processo que abrimos); `zipfile` (confere a soma de cada arquivo ao abrir,
`Lib/zipfile/__init__.py:1115`, estudo do Kraken §3); `http.server.ThreadingHTTPServer` (a documentação avisa que não
é para servidor de produção: aqui só escuta em 127.0.0.1, na prova). **Achado rodando:** o http.server liga de fábrica
o "reusar o endereço" (`Lib/http/server.py:135`, `allow_reuse_address = True`), e no Windows isso deixou um segundo
servidor abrir a mesma porta sem erro; o servidor das versões desliga isso e pede a porta exclusiva (SO_EXCLUSIVEADDRUSE,
https://learn.microsoft.com/windows/win32/winsock/using-so-reuseaddr-and-so-exclusiveaddruse).

Microsoft Learn, https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_psmodulepath?view=powershell-5.1
(lido em 19/11, depois da rodada 1 do GitHub): o PowerShell do Windows monta a lista de módulos ao abrir; sem a
variável PSModulePath, usa a de fábrica; e a nota "Inherited PowerShell 7 module paths precede the Windows PowerShell
system module path [...] This breaks module autoloading". Refeito no PC com um módulo que não carrega na frente da
lista: o mesmo CouldNotAutoloadMatchingModule do GitHub.

**Deduzido, não lido:** que o vpk não deixa programa rodando depois de ser fechado à força pela vigia (o .msi roda o
WiX por dentro; se sobrar um, o rascunho não apaga e a frase diz o que ficou).

**Lido e rodado na volta 3 (20/11/2026):**
- Microsoft Learn, CreateProcessW (https://learn.microsoft.com/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw):
  o módulo é "a Windows-based application" ou "some other type of module (for example, MS-DOS or OS/2) if the
  appropriate subsystem is available"; "To run a batch file, you must start the command interpreter"; sem extensão,
  ".exe is appended"; a busca do nome sozinho: a pasta do programa que chama, a pasta atual, System32, System, Windows,
  o PATH. Python 3.14, subprocess, "Security Considerations": "On Windows, batch files (*.bat or *.cmd) may be launched
  by the operating system in a system shell regardless of the arguments passed to this library"; e "when resolving or
  searching for the executable path with shell=False, cwd does not override the current working directory".
- **Rodado no PC** (`relatorios/passo2-publicar/anexos/variantes-do-lote-resultado.txt:1`; subprocess sem shell, um lote que escreve a COMSPEC): "x.bat", "X.BAT" e "x.bat " rodaram pelo
  cmd.exe; "x.bat." e o prefixo de caminho longo abriram algo que saiu com código 1; "x.bat::$DATA" deu o erro 193; um
  lote com nome de .exe e um .bat que começa com "MZ" deram o erro 216 (não rodaram). Conclusão: o Windows só entrega
  ao cmd.exe o que não começa com "MZ" e tem extensão de lote. **Deduzido, não lido:** que o mesmo vale para o
  `CreateProcess` chamado de outro jeito (só o do subprocess foi rodado).
- Microsoft Learn, Process Creation Flags (https://learn.microsoft.com/windows/win32/procthread/process-creation-flags): CREATE_SUSPENDED: "The primary thread of the new process is created in a
  suspended state, and does not run until the ResumeThread function is called". CREATE_NO_WINDOW: "The process is a
  console application that is being run without a console window" (achado 10).
- Microsoft Learn, AssignProcessToJobObject (https://learn.microsoft.com/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject): "By default, all child processes are associated with the immediate job
  and every job in the parent job chain"; "The child process breaks away from every job in the job chain unless a job
  in the chain does not allow breakaway". "Job Objects" (https://learn.microsoft.com/windows/win32/procthread/job-objects): "Child processes created using Win32_Process.Create are not
  associated with the job" (o vpk não usa o WMI); "closing the last job object handle terminates all associated
  processes" (com KILL_ON_JOB_CLOSE).
- O `IsProcessInJob` (https://learn.microsoft.com/windows/win32/api/jobapi/nf-jobapi-isprocessinjob) pede uma alça com licença de leitura do processo: sem ela, o Windows respondeu "acesso negado"
  (erro 5), achado rodando; a alça passou a pedir PROCESS_QUERY_LIMITED_INFORMATION.
- Python 3.14, `Lib/subprocess.py:1575` (`_execute_child`, na cópia do PC): o subprocess fecha a alça da linha
  principal (`_winapi.CloseHandle(ht)`) e não guarda o número dela; por isso a peça a acha pela foto das linhas do
  Windows (CreateToolhelp32Snapshot, TH32CS_SNAPTHREAD, Thread32First/Next) e a solta com ResumeThread.
  `Popen.communicate` com tempo: "Catching this exception and retrying communication will not lose any output" (a vigia
  do gh).
- O lançador do pip (`.venv/Lib/site-packages/pip/_vendor/distlib/scripts.py:259`, `_write_script`, até a linha 278): o .exe é
  "launcher + shebang + zip_data", com o `__main__.py` no zip. É o vpk de mentira dos testes.
- GitHub, a API de apagar uma publicação (https://docs.github.com/rest/releases/releases#delete-a-release): recebe só o número da publicação, sem condição (lembrado; não relido nesta
  volta): por isso fica o instante da Ressalva.

**Lido e rodado na volta 4 (20/11/2026; separado o lido do deduzido):**
- **O nome que o Windows completa (achado 2).** Microsoft Learn, "File path formats on Windows systems"
  (https://learn.microsoft.com/dotnet/standard/io/file-path-formats), "Path normalization": "Almost all paths passed to
  Windows APIs are normalized"; "you can do it explicitly by calling [...] the GetFullPathName() function"; "Trim
  characters": "If the path doesn't end in a separator, all trailing periods and spaces (U+0020) are removed"; "Skip
  normalization": só o que começa exatamente com `\\?\` não é normalizado ("A file or directory called `hidden.`, for
  example, is impossible to access in any other way"). O Python: `os.path.abspath` no Windows chama o
  `_getfullpathname` (o GetFullPathNameW). **Rodado no PC** (cópias do `hostname.exe` numa pasta do rascunho desta
  conversa): com caminho, `provaeco.exe.` e `provaeco.exe .` rodaram; pelo PATH do próprio processo, o nome sozinho
  `provaeco.exe.`, `provaeco.exe..` e `provaeco.exe. ` rodaram, `provaeco.` não (erro 2), e o `shutil.which` não acha
  nenhum com ponto no fim. E na peça de hoje: `rodar_e_esperar(["whoami.exe."])` rodou o whoami da pasta do Windows.
  **Rodado também:** o CreateProcess procura o nome sozinho no PATH de QUEM CHAMA, não no `env` passado ao subprocess
  (com o PATH só no `env`, o nome sozinho deu erro 2). Por isso o teste muda o PATH do próprio processo.
- **Os atalhos da Loja (achado 6).** Rodado no PC (`relatorios/passo2-publicar/anexos/volta4-nome-e-loja.py.txt:1`, resultado em `relatorios/passo2-publicar/anexos/volta4-nome-e-loja-resultado.txt:1`): os `.exe` de `%LOCALAPPDATA%\Microsoft\WindowsApps` (ex.:
  `bash.exe`, `claude-desktop.exe`) existem para o `os.path.isfile`, mas abrir para ler dá `OSError` 22 ("Invalid
  argument"). **Deduzido, não lido:** que é assim em todo Windows (são "atalhos de execução de aplicativo"; não li a
  documentação deles).
- **Gravar no disco (achado 11).** Python 3.14, `os.fsync`: força a gravação no disco do arquivo; no Windows chama o
  `_commit` da biblioteca C; com um arquivo do Python, primeiro `f.flush()`, depois `os.fsync(f.fileno())` (lembrado
  da documentação do `os`, não relido). Microsoft Learn, `_commit`
  (https://learn.microsoft.com/cpp/c-runtime-library/reference/commit): "Flushes a file directly to disk"; "forces the
  operating system to write the file associated with fd to disk"; devolve -1 se deu erro. FlushFileBuffers
  (https://learn.microsoft.com/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers): "Flushes the buffers of a
  specified file and causes all buffered data to be written to a file"; "The file handle must have the GENERIC_WRITE
  access right" (por isso a gravação é pedida no arquivo aberto para escrever). **Deduzido, não lido:** que o `_commit`
  chama o FlushFileBuffers (a página do `_commit` não diz). **O que a gravação NÃO faz:** a leitura de volta continua
  vindo do que o Windows guarda na memória; o que muda é que, quando o nome certo aparece, o conteúdo já foi mandado ao
  disco (a falta de luz logo depois não deixa um arquivo pela metade com o nome certo). A pasta (o nome trocado) não é
  gravada à parte: o Windows não abre pasta para isso pelo Python (Ressalvas).
- **O laço com a saída guardada (achado 8).** Python 3.14, `subprocess.Popen.communicate` (https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate): "If the process does not
  terminate after timeout seconds, a TimeoutExpired exception will be raised. Catching this exception and retrying
  communication will not lose any output" (já citado na volta 3; é o jeito do laço com `capturar=True`). O gh: a saída
  em UTF-8, como hoje.
- **Conferir uma publicação no GitHub sem mudar nada (achado 1, a frase):** `gh release view <etiqueta> --json isDraft`,
  o mesmo pedido que o publicar já faz para ler a situação (cli/cli,
  https://github.com/cli/cli/blob/trunk/pkg/cmd/release/shared/fetch.go, lido na volta 1): `"isDraft": true` é rascunho; "release not found", não existe.

**Lido na volta 5 (20/11/2026):**
- **Os fluxos no nome do programa (achado 5, D-813).** Microsoft Learn, "File Streams (Local File Systems)"
  (https://learn.microsoft.com/windows/win32/fileio/file-streams): "the full name of a stream is "filename:stream
  name:stream type", as in the following example: "myfile.dat:stream1:$DATA""; "To fully specify the default data
  stream, use "filename::$DATA" [...] This is the equivalent of "filename""; "When a drive letter is specified with a
  relative path, a colon separates the drive letter from the path". "Naming Files, Paths, and Namespaces"
  (https://learn.microsoft.com/windows/win32/fileio/naming-a-file): o ":" está entre os "reserved characters" de um
  nome; "C:tmp.txt" é relativo à pasta atual do disco C. Então, num caminho, o ":" só aparece depois da letra do disco
  (o "C:") ou para dizer um fluxo. **Rodado por quem tentou quebrar** (`relatorios/passo2-publicar/quem-quebrou/anexos-4/e5-nomes-resultado.txt:16`):
  o Windows roda `nada.txt:pwsh.exe` (uma cópia do hostname.exe gravada como fluxo); o `::$DATA` ele não roda. E rodado
  de novo por mim no teste novo (os três caminhos), sem a peça e pela peça.
- **O gh que não abre (achado 4).** `core/windows.py`, `rodar_em_grupo` (o `abriu: False`) e `abrir_em_grupo`: só sai
  sem programa quando a peça recusa, o Windows não deixa criar o grupo, o `subprocess.Popen` falha (programa não
  achado), ou o programa, aberto PARADO, é fechado antes de ser solto (Microsoft Learn, Process Creation Flags,
  CREATE_SUSPENDED: "does not run until the ResumeThread function is called",
  https://learn.microsoft.com/windows/win32/procthread/process-creation-flags). Em todos, o gh não executou nada: o
  pedido não saiu do PC.

**Lido na volta 6 (20/11/2026):** nenhuma peça de fora nova. O que o conserto usa e de onde vem:
- **O que o PyInstaller deixa na pasta** (o teste de reversão escreve o mesmo): o .exe em `--distpath\--name\`, e cada
  `--add-data origem;destino` em `<pasta>\_internal\<destino>\` (o `--contents-directory _internal`). **Rodado, não
  deduzido:** a pasta que o PyInstaller 6 de verdade montou na prova de 20/11 (`dist\EditorImpressao`, só lida) tem
  exatamente isso (`_internal\modelos\doclayout.onnx`, `_internal\modelos\doctr`, `_internal\modelos\mobile_sam`,
  `_internal\core\nativo\st_gravura.dll` e o `.txt`, `st_ferramentas.dll` e o `.txt`), mais o que o `construir_pasta`
  põe depois (`tesseract\`, a ficha, o "COMO USAR.txt"), e **nenhum** `instalar\`
  (`anexos/volta6-a-pasta-da-prova.txt`). A documentação do PyInstaller (https://pyinstaller.org/en/stable/usage.html,
  "--add-data SOURCE:DEST", "--contents-directory CONTENTS_DIRECTORY": "the directory name where all files are placed
  besides the executable") diz o mesmo; não a reli nesta volta além disso.
- **O vpk e o instalar\:** nada muda no que o vpk recebe (a pasta com `instalar\vc_redist.x64.exe` e a versão no .txt,
  como na pasta pronta de hoje); o que o vpk faz com ela foi lido na volta 1 (acima:
  `src/vpk/Velopack.Packaging/PackageBuilder.cs:60`, no código do Velopack 1.2.161). O programa instalado lê
  `<programa>\instalar\` por `atualizacao.PASTA_DO_QUE_SE_INSTALA` (`atualizacao.py:196`; código nosso, não muda).
- **O caminho de rede (achado 3):** o que o Windows faz com ele foi rodado por quem quebrou (relatório 5, E7: "caminho de
  rede (`\\localhost\C$\...` e `\\?\UNC\...`) | sim [o Windows roda] | recusa | recusa (frase errada)";
  `relatorios/passo2-publicar/quem-quebrou/relatorio-5.md:171`); a regra não muda, só a frase.

**Lido na volta 7 (20/11/2026):** nenhuma peça de fora nova. A leitura da assinatura continua a da peça do Windows
(`core/windows.py`, `ler_assinatura_digital`; lida na volta 1, `windows.ler_assinatura_digital`), com o que o Windows
responde pelo `vc_redist.x64.exe` oficial já conferido de verdade no PC (status "Valid", assinante "CN=Microsoft
Corporation, ...", produto "Microsoft Visual C++ 2015-2022 Redistributable (x64) - 14.44.35211", versão
"14.44.35211.0": `tests/test_empacotar.py:370`, o `_assinatura` dos testes, e o registro da prova de 20/11, "versão
14.44.35211.0, assinatura da Microsoft conferida"). Para um arquivo sem assinatura, o Windows responde status
"NotSigned" e assinante vazio (rodado de novo pelo teste novo da régua única, `tests/test_empacotar.py`, no PC). O que o
programa instalado faz com a versão: `atualizacao.py:1230` (lê o vc_redist.versao.txt; sem ele, "0.0.0").

**Volta 8.**
- O git: `git rev-parse --git-common-dir` mostra a pasta de git comum (com `--path-format=absolute`, o caminho inteiro e
  canônico): https://git-scm.com/docs/git-rev-parse (opções "--git-common-dir" e "--path-format"). Rodado no PC:
  da cópia `passo2` e da principal, `D:/programas/EditorImpressao/.git`; fora de um repositório, código 128 e "not a git
  repository". (Lido e rodado.)
- O git, cópias de trabalho: "Within a linked worktree, $GIT_DIR is set to point to this private directory [...] and
  $GIT_COMMON_DIR is set to point back to the main worktree's $GIT_DIR (e.g. /path/main/.git). These settings are made
  in a .git file located at the top directory of the linked worktree": https://git-scm.com/docs/git-worktree ("DETAILS");
  e "The main worktree is listed first", no `git worktree list` (mesma página, "COMMANDS", list). O `.git` da cópia
  `passo2` diz "gitdir: D:/programas/EditorImpressao/.git/worktrees/passo2" (lido no disco). (Lido.)
- O Python, ler texto: `read_text(encoding="utf-8", errors="replace")` troca o que não é UTF-8 pela marca U+FFFD e nunca
  levanta erro de leitura de texto; sem `errors`, levanta `UnicodeDecodeError`; a marca de UTF-8 no começo não é tirada
  pelo "utf-8" (só pelo "utf-8-sig"): https://docs.python.org/3/library/functions.html#open ("errors") e
  https://docs.python.org/3/library/codecs.html#standard-encodings ("utf_8_sig"). (Lido.)
- O Windows, a assinatura de um arquivo copiado: o `Get-AuthenticodeSignature` lê a assinatura de dentro do arquivo ou,
  se ele é assinado por catálogo, a do catálogo do Windows achado pela soma do arquivo; por isso a cópia do
  `powershell.exe` continua "Valid", de "CN=Microsoft Windows": https://learn.microsoft.com/powershell/module/microsoft.powershell.security/get-authenticodesignature
  e o relatório 7 (`relatorios/passo2-publicar/quem-quebrou/relatorio-7.md:178`, rodado no PC). (Lido; o "por catálogo"
  é dedução minha, a conferir rodando.)

## O que foi feito

1. **A assinatura digital pela peça única** (`windows.ler_assinatura_digital`, nova): o empacotar deixou de abrir o
   PowerShell por conta própria para ler a assinatura do Visual C++. O item saiu da lista de exceções (176 → 175), no
   mesmo commit.
2. **As três saídas num lugar só** (`empacotar.SAIDAS`): a pasta portátil (com o motor solto, como sempre), a
   atualização (sem o motor, com o motor-exigido.json) e o instalador (com o arquivo do motor publicado em instalar\ e
   o .msi). O pacote da atualização com o motor solto é recusado.
3. **Uma função roda o vpk** (`empacotar.rodar_vpk`): a pasta temporária no rascunho e a vigia do espaço; o comando sem
   a diferença e sem o zip portátil; o .msi só no instalador; o Setup.exe apagado na hora.
4. **A conta do espaço e a reserva de 20 GB** (`empacotar.espaco_que_vai_usar`, `empacotar.conferir_espaco`): antes do
   vpk e durante.
5. **O motor à parte, na parte que o publicar usa:** a versão do motor (`ocr_kraken.VERSAO_DO_MOTOR` = 1), a ficha
   motor.json gravada pelo montar depois do teste (`--so-ficha` para o motor que já existe), a conferência única
   (`ocr_kraken.conferir_motor` e `ocr_kraken.conferir_ficha`), o arquivo do motor comprimido e conferido
   (`empacotar.zipar_motor`), os nomes em `versao.py`.
6. **O publicar refeito:** o rascunho no C:; dois destinos (uma pasta com uma subpasta por versão, e o GitHub pelo gh)
   com o mesmo caminho (rascunho, enviar só o pacote, o índice e a assinatura, ler de volta, só então liberar; falha
   apaga o rascunho do destino); antes, o motor que a versão pede tem de estar publicado e conferir; `--motor` publica
   o motor; `--com-instalador` faz o .msi numa segunda passada do vpk (o publicado é sempre o pacote da atualização) e
   o .msi vai à publicação e à pasta de saída; `--apagar` apaga uma publicação e confere; no fim, sempre, a conferência
   do rascunho, da pasta de saída, do destino e do Setup.exe. A ficha da versão na pasta montada recusa a pasta pronta
   de outra versão.
7. **Conserto na peça do Windows (bug que impedia a tarefa):** o PowerShell aberto pela peça herdava a lista de
   módulos do PowerShell 7 (no Windows do GitHub, ou num terminal pwsh) e não carregava os dele; a assinatura digital
   nunca era lida lá. Agora a peça o abre sem essa lista (`_ambiente_do_powershell`, lugar único, ao lado do comando
   do PowerShell), no rodar e esperar e no lançar solto.
8. **Volta 2 (os achados de quem tentou quebrar):** o apagar no GitHub certo para rascunho e para liberada, decidido
   pela leitura de volta; o vpk num grupo do Windows (`windows.abrir_em_grupo`), que a vigia e o Ctrl+C fecham inteiro;
   nada apagado depois de pedir para liberar; o erro do disco em frase; o lançar solto sem "saiu sem começar"; o .msi
   com o número da versão e o servidor sem nome repetido nem junção (a regra das publicações num lugar só); o motor em
   instalar\ recusado na atualização; a conta do espaço refeita; a etiqueta conferida inteira.
9. **O servidor das versões de prova** (`servidor_das_versoes.py`, novo): a janela, o índice de todas as versões
   liberadas, os arquivos pelo nome, o rascunho escondido, fechar corta o envio, `--limite` deixa lento, a porta
   exclusiva.

10. **Volta 3 (os achados do relatório 2):** só o rascunho apagado no caminho de erro; a cópia conferida para o .msi e
   para a pasta de destino; a conferência do fim compara o .msi; a peça recusa o lote; o programa do grupo nasce parado;
   a frase do fechar só com o grupo lido; o motor baixado na conta e na vigia; a vigia num lugar só; o nome do motor
   num lugar só; os textos que não batiam; o vpk de mentira como programa de verdade.

11. **Volta 4 (os achados do relatório 3):** depois do pedido de liberar, nada é apagado em nenhum destino, e a frase
   diz o que pode ter ficado e os comandos (D-816); o apagar escreve a frase de cada desfecho e sabe se pediu; "não
   achei" logo depois de criar não vira "sumiu"; o criar do rascunho entrou no caminho de erro; a peça lê o nome do
   programa uma vez, como o Windows o completa (`pwsh.exe.`, `Update.exe.` e `whoami.exe.` passavam); o programa que
   não deixa ler tem a frase própria; sem a soma pronta do GitHub, o download vai para o rascunho, pela vigia, e entra
   na conta; o gh e o vpk passam pelo mesmo laço da peça (`windows.rodar_em_grupo`); a cópia, o motor comprimido e a
   gravação da peça pedem ao Windows para gravar no disco antes de conferir e trocar o nome (`windows.gravar_no_disco`);
   o caminho do teste do lote em texto cru; o teste da segunda olhada depois do PATH.

12. **Volta 5 (os achados do relatório 4):** as três frases de "já existe" e "sobrou um rascunho" pelo lugar único
   do comando de apagar; só o pedido de apagar que saiu diz "pedi" (`ApagarSemResposta`); o gh que nem abriu não é
   pedido de liberar (`NadaSaiu`), e então o rascunho é apagado (D-816); a peça recusa o fluxo escondido de outro
   arquivo, com frase própria; o texto de `windows.gravar_no_disco` diz quem passa por ela; os testes das duas
   proteções que não tinham teste; o tempo do pedido ao gh num lugar só (`DestinoGitHub.LIMITE_DO_PEDIDO_S`).

13. **Volta 6 (o defeito da prova à vista de 20/11 e os 3 baixos do relatório 5):** a pasta montada do zero sai com o
   Visual C++ em instalar\ (quem o põe é a montagem, `construir_pasta`, pelo campo novo `Saida.vc_em_instalar`, antes da
   ficha da versão; `preparar_saida` deixou de pô-lo); a mesma conferência (`conferir_pasta_pronta`) vale para a pasta
   montada e para a pasta pronta, e roda também logo antes do vpk em `construir_pacote_do_velopack` (todo caminho até o
   vpk passa por ela); a frase do motor que falta dá o comando do destino (`_Destino.comando_de_publicar_o_motor`, com o
   `--pasta` na pasta das provas); a peça recusa o caminho de rede com frase própria (`windows.FRASE_CAMINHO_DE_REDE`);
   o apagar em que o gh nem abre ganhou o teste que faltava. Nada mudou no que a pasta pronta precisa trazer, nem na
   pasta portátil e no Inno.

14. **Volta 7 (D-818 e os 4 baixos do relatório 6):** a pasta já montada é conferida igual à montada do zero, pela
   mesma `conferir_pasta_pronta`, que agora cobra o Visual C++ pela assinatura da Microsoft (a régua única nova,
   `conferir_o_visual_c`, que a montagem também passou a usar), o arquivo da versão dele igual à versão da assinatura e
   o Tesseract inteiro (a lista única nova, `relativos_do_tesseract`, que a montagem e o Inno também usam); o pacote
   depois do vpk cobra sempre o Tesseract e a versão do Visual C++; o empacotar chamado sozinho confere antes de mexer
   na pasta; a pasta de mentira dos testes antigos ganhou as peças (D-818); testes novos para o pacote sem uma peça e
   para a pasta das provas com espaço no nome; o roteiro da prova na ordem certa.

15. **Volta 8 (os 2 defeitos da prova à vista de 20/11 e os 6 baixos do relatório 7):**
    - *Defeito 2, a frase depois de apagar:* o lugar único do apagar (`apagar_e_conferir`, o antigo corpo de
      `apagar_publicacao`) passa a devolver o que fez (`Apagado`: havia ou não o que apagar, e o aviso do destino) e a
      frase de cada desfecho sai dele (`Apagado.frase`): "a publicação X foi apagada de Y (conferido)" e "X: não existia
      em Y, e nada foi apagado (conferido)". O `--apagar` (pasta e GitHub, versão e motor) e o caminho de erro do
      publicar (antes do pedido de liberar) imprimem essa frase; `apagar_publicacao` continua devolvendo o aviso, pela
      mesma conta (os testes antigos cobram isso).
    - *Baixo 6, a versão do Visual C++ lida de dois jeitos:* uma leitura só, `atualizacao.versao_do_visual_c_do_pacote`
      (o jeito do publicar: UTF-8 trocando o que não é UTF-8, sem os espaços das pontas; nada se o arquivo não existe),
      usada pela conferência da pasta (`empacotar.conferir_pasta_pronta`) e pelo programa instalado
      (`atualizacao.instalar_visual_c_se_faltar`, que continua usando "0.0.0" sem o arquivo).
    - *Baixos 1 a 3, só testes:* a leitura da assinatura que falha (a peça do PowerShell respondendo "não terminou");
      uma cópia do powershell.exe do Windows como Visual C++, lida de verdade (assinatura válida, de outro assinante); o
      arquivo da versão vazio ou pela metade; as licenças do Tesseract na pasta e no pacote. A régua e a lista não mudam.
    - *Baixo 5, o roteiro:* o item 14 diz onde a linha "Visual C++: ..." aparece ("A prova de verdade", Volta 8).
    - *O formulário:* a linha da D-818 da Volta 7, as citações do vpk de mentira e do arquivo da versão do Visual C++, e
      esta lista de arquivos (só o que mudou desde a partida da volta).
    - *Defeito 1, as peças procuradas no lugar errado numa cópia:* **não feito**. Parei: o conserto pela causa pede
      arquivos fora da lista do pacote (o plano e o porquê em "A causa, a regra e todos os caminhos", Volta 8, e em
      "Perguntas para o Samuel", Volta 8).

## Arquivos criados ou alterados

Desde a partida desta volta (`21f1fc50`, o pacote da volta 8); o que as voltas 1 a 7 mexeram está nos itens abaixo
desta lista, no `git log` deste arquivo e nas seções "O que foi feito" e "Caminho e função".

- `publicar_versao_kaique.py` (o `Apagado` e o `apagar_e_conferir`, o lugar único do apagar e das frases dele; o
  `--apagar` e o caminho de erro passam a usar a frase dele; `apagar_publicacao` só repassa)
- `atualizacao.py` (a leitura única da versão do Visual C++ do pacote, `versao_do_visual_c_do_pacote`, usada pelo
  programa instalado)
- `empacotar.py` (a conferência da pasta lê a versão do Visual C++ pela leitura única; o texto)
- `tests/test_publicar_versao.py` (9 testes novos, 23 casos, acrescentados no fim; nenhum antigo mudou)
- `relatorios/passo2-publicar/` (este formulário, o pacote da volta 8 e os anexos `reversao-volta8-*`)

Nesta volta não mudaram: `core/windows.py`, `core/ocr_kraken.py`, `montar_motor_kraken.py`,
`compilar_detector_gravura.py`, `tests/test_empacotar.py`, `tests/test_windows_peca.py` (o defeito 1 parou antes de
mexer).

- **Volta 4** (desde `5f96975b`, o pacote da volta 4): `core/windows.py`, `empacotar.py`, `publicar_versao_kaique.py`,
  `tests/test_windows_peca.py` (5 testes novos e o caminho do achado 9 em texto cru; nenhum antigo mudou no que cobra),
  `tests/test_publicar_versao.py` (13 testes novos, 22 casos; o teste antigo do achado 5 da volta 3 saiu, com a nota no
  lugar dele: ver "O que já está escolhido e testado aqui" e "Ressalvas") e, em `relatorios/passo2-publicar/`, este
  formulário, o pacote da volta 4 e os anexos `reversao-volta4-*` e `volta4-*`. `tests/test_empacotar.py` não mudou.

- **Volta 5** (desde `595cc293`, dentro da lista acima): `core/windows.py`, `publicar_versao_kaique.py`,
  `tests/test_windows_peca.py` (1 teste novo), `tests/test_publicar_versao.py` (7 testes novos, 9 casos; nenhum antigo
  mudou) e, em `relatorios/passo2-publicar/`, este formulário, o pacote de quem tentou quebrar da volta 4 e os anexos
  `reversao-volta5-*`. `empacotar.py` não mudou nesta volta.

- **Volta 6** (desde `b9300da8`, dentro da lista do pacote): `empacotar.py` (o campo `vc_em_instalar`, a montagem, a
  conferência antes do vpk, os textos), `publicar_versao_kaique.py` (o comando do motor, os textos), `core/windows.py`
  (a frase do caminho de rede), `tests/test_publicar_versao.py` (6 testes novos, 8 casos; nenhum antigo mudou),
  `tests/test_windows_peca.py` (1 teste novo; nenhum antigo mudou) e, em `relatorios/passo2-publicar/`, este formulário,
  o pacote da volta 6 e os anexos `relatorios/passo2-publicar/anexos/volta6-a-pasta-da-prova.txt` e `reversao-volta6-*`. `tests/test_empacotar.py` não
  mudou.

- **Volta 7** (desde `db4b377a`): `empacotar.py` (`conferir_o_visual_c`, `relativos_do_tesseract`, a conferência da
  pasta, os esperados do pacote, a ordem em `construir_pacote_do_velopack`, os textos), `publicar_versao_kaique.py` (só
  o texto do cabeçalho), `tests/test_publicar_versao.py` (3 ajudantes antigos mudados pela D-818, listados em "O que já
  está escolhido e testado aqui", Volta 7; 5 testes novos, 13 casos), `tests/test_empacotar.py` (1 teste novo; nenhum
  antigo mudou) e, em `relatorios/passo2-publicar/`, este formulário, o pacote da volta 7 e os anexos `reversao-volta7-*`.
  `core/windows.py` e `tests/test_windows_peca.py` não mudaram.

## Como cumpri cada uma

- D-767: o defeito da lista de módulos só apareceu rodando de verdade (no GitHub) e foi refeito de verdade no PC antes
  de consertar (`tests/test_windows_peca.py::test_o_powershell_nao_herda_os_modulos_do_powershell_7`).
  Nada rodou de verdade no Windows além de ler (a assinatura digital, o espaço do disco); o vpk e o GitHub dos
  testes são de mentira e os testes dizem isso no cabeçalho; o de verdade fica para a prova à vista ("A prova de
  verdade").
- D-768: o pacote da atualização sai sem o motor e é conferido sem ele
  (`tests/test_publicar_versao.py::test_d768_o_motor_e_a_versao_publicados_numa_pasta_sem_o_motor_no_pacote`,
  `tests/test_publicar_versao.py::test_d768_o_pacote_da_atualizacao_com_o_motor_solto_e_recusado`).
- D-773: o servidor das versões (`tests/test_publicar_servidor.py::test_d773_o_indice_junta_as_versoes_liberadas_e_nao_mostra_o_rascunho`,
  `tests/test_publicar_servidor.py::test_d773_fechar_e_a_internet_caindo_no_meio_do_download`); o rascunho no GitHub
  (`tests/test_publicar_versao.py::test_o_github_sobe_como_rascunho_le_de_volta_e_so_entao_libera`, com o gh de
  mentira) e o `--apagar`.
- D-775: entrego à gerente sem rótulo, para quem tenta quebrar.
- D-776: `tests/test_publicar_versao.py::test_d776_sem_espaco_para_antes_do_vpk_e_nada_fica`,
  `tests/test_publicar_versao.py::test_d776_a_vigia_fecha_o_vpk_quando_o_disco_cai_abaixo_da_reserva`,
  `tests/test_publicar_versao.py::test_d776_a_conta_do_espaco_e_a_reserva_de_20_gb`,
  `tests/test_publicar_motor.py::test_d776_comprimir_o_motor_para_quando_o_disco_cai_abaixo_da_reserva`.
- D-777: `tests/test_publicar_versao.py::test_d789_d777_o_comando_do_vpk_sem_diferenca_sem_portatil_e_o_msi_so_quando_pedido`,
  `tests/test_publicar_versao.py::test_d777_o_instalador_so_quando_pedido_e_o_publicado_e_o_da_atualizacao`.
- D-785: nada pesado montado, nada publicado; a janela do servidor só foi aberta fora da tela, nos testes.
- D-786: o caminho do livro não usa nada do que mudou (ver "Velocidade").
- D-788: o arquivo do motor em instalar\ só no instalador (`tests/test_publicar_motor.py::test_o_motor_exigido_diz_o_motor_publicado`).
- D-789: `--delta None` e nenhum download da versão anterior (o mesmo teste da D-777 confere o comando de cada vez
  que o vpk rodou).
- D-790: `tests/test_publicar_versao.py::test_d790_sem_o_motor_publicado_nada_e_montado` e, antes de liberar, o motor
  lido de novo (`tests/test_publicar_versao.py::test_n1_n3_n4_n14_cada_leitura_de_volta_errada_impede_liberar`, o caso
  "motor sumiu"). **Correção da volta 2:** a primeira entrega dizia que o `test_d53` provava isso; não provava (ele só
  cobra a ordem; quem tentou quebrar desligou a leitura de novo do motor e ele passou).
- D-791: o item saiu da lista no commit do conserto (`0d844b4f`); o porteiro passou no GitHub ("Testes").
- D-795: `tests/test_publicar_versao.py::test_d795_o_setup_exe_e_o_rascunho_somem_tambem_quando_da_erro` (com erro) e
  o teste da D-768 (sem erro): o Setup.exe nunca está no destino nem na pasta de saída, e a conferência do fim diz isso.
- D-796: nenhum arquivo de `ui/` mudou.
- D-797: tudo no ramo `passo2-publicar-2026-11-19`.
- D-798: nenhum rótulo de pronto neste ramo.
- D-724: `tests/test_publicar_versao.py::test_d724_o_motor_com_a_assinatura_de_outra_chave_e_recusado`; `assinatura.py`
  não mudou.
- D-727: o motor dentro do instalador (o teste da D-777 confere a segunda passada com o arquivo do motor).
- D-809: `tests/test_windows_peca.py::test_o_lancado_solto_apaga_a_pasta_de_troca_sem_seguir_atalho` e
  `tests/test_publicar_versao.py::test_d809_apagar_uma_publicacao_que_e_atalho_nao_apaga_o_outro_lado`; as junções
  dos testes nascem e saem em pastas temporárias do próprio teste, com o outro lado conferido inteiro depois.
- D-811: a seção "Cada proteção e o teste que falha sem ela" (19 de 19 na primeira entrega; na volta 2, mais 21, das
  quais 20 acusadas sozinhas e uma dupla proteção escrita).
- D-812: a seção "De onde vem cada dado da conferência" (os dois dados que o conferido escreve estão marcados como
  não-prova).
- D-814: nenhuma pergunta ao Samuel; procurei antes no Livro (ver "Perguntas para o Samuel").
- D-807: no PC, um arquivo de teste por vez (lista em "Testes"); o conjunto inteiro no GitHub.
- D-714: o publicar só roda pelo comando; nada liga sozinho.
- D-763: `tests/test_publicar_motor.py::test_d763_o_nome_do_pacote_do_motor_e_outro_e_nao_e_pasta_de_dados`.

- **Volta 3:** D-776 (a conta soma o motor baixado e a vigia vigia o download:
  `tests/test_publicar_versao.py::test_volta3_achado7_o_motor_baixado_entra_na_conta_e_na_vigia`,
  `tests/test_publicar_versao.py::test_volta3_achado7_o_gh_que_baixa_e_fechado_pela_vigia`); D-795 (a conferência do fim
  continua dizendo do Setup.exe; o .msi ganha a sua linha:
  `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_da_pasta_de_saida_e_comparado_com_o_do_rascunho`); D-767 (o
  grupo, o lote e a cópia cortada rodam de verdade:
  `tests/test_windows_peca.py::test_o_programa_nasce_parado_e_so_roda_dentro_do_grupo`,
  `tests/test_windows_peca.py::test_bat_e_cmd_sao_recusados_pelo_rodar_pelo_lancar_e_pelo_grupo`,
  `tests/test_publicar_versao.py::test_volta3_a_copia_cortada_no_meio_nunca_deixa_o_nome_certo`); D-811 (24 de 24
  proteções acusadas, `anexos/reversao-volta3-resultado.txt`); D-812 (a seção "De onde vem cada dado", acrescentada);
  D-813 (o que o Windows aceita como programa, em "O que li", e a recusa pelo arquivo de verdade); D-815 (agente novo,
  começou por este formulário); D-798 (nenhum rótulo de pronto); D-809 (nenhuma junção nesta volta).

- **Volta 4:**
  - D-816 "A , mas onde estamos antes de você fazer qualquer processo": depois do pedido de liberar, nenhum apagar é
    chamado, em nenhum destino, e a frase não lê nada. Provas: `tests/test_publicar_versao.py::test_d816_depois_do_pedido_de_liberar_nada_e_apagado_com_qualquer_atraso`
    (1, 2, 3 e 10 leituras atrasadas, pasta e GitHub), `tests/test_publicar_versao.py::test_d816_o_motor_tambem_nunca_e_apagado_depois_do_pedido_de_liberar`,
    `tests/test_publicar_versao.py::test_d816_o_liberar_que_falha_e_fica_rascunho_nao_apaga_e_diz_o_comando` (o
    comportamento antigo saiu: o rascunho continua) e `tests/test_publicar_versao.py::test_d816_ctrl_c_depois_do_pedido_de_liberar_nao_apaga`.
    "Antes do pedido de liberar, erro no meio continua apagando o rascunho na hora": os testes antigos
    `test_achado1_erro_antes_de_liberar_no_github_apaga_e_diz_que_apagou`, `test_a_leitura_de_volta_que_nao_bate_nao_libera_e_apaga_o_rascunho_do_destino`
    e `test_n1_n3_n4_n14_cada_leitura_de_volta_errada_impede_liberar` continuam passando, sem mudar.
  - D-815 "ok": escritor novo nesta volta; comecei pelo formulário e pelo relatório 3.
  - D-767 "não faça mais nada escodindo ou de mentira": o nome com ponto no fim, o programa trancado, o lote pelo PATH, o
    laço com o grupo e a gravação no disco rodam de verdade no Windows nos testes; o GitHub é de mentira (só a lógica),
    e o gh dos testes do laço é um programa de verdade de prova. O de verdade fica para a prova à vista.
  - D-773 "A": a frase da D-816 diz como conferir e o comando de apagar o rascunho de prova
    (`tests/test_publicar_versao.py::test_d816_o_liberar_que_falha_e_fica_rascunho_nao_apaga_e_diz_o_comando` roda o
    comando da frase e confere que apagou).
  - D-775 "ok": entrego à gerente, sem rótulo; o próximo é um agente novo que tenta quebrar.
  - D-776 "Sim, no C só tem que cuidar para não encher o disco C inteiro": o download para somar no rascunho, na vigia e
    na conta (`tests/test_publicar_versao.py::test_volta4_achado7_sem_a_soma_pronta_o_download_vai_ao_rascunho_pela_vigia`,
    `tests/test_publicar_versao.py::test_volta4_achado7_a_conta_do_espaco_soma_o_que_a_soma_pode_baixar`,
    `tests/test_publicar_versao.py::test_volta4_achado7_no_publicar_sem_a_soma_pronta_tudo_e_baixado_no_rascunho`).
  - D-795 "ok": nada mudou no Setup.exe; os testes dele (`test_d795_o_setup_exe_e_o_rascunho_somem_tambem_quando_da_erro`,
    `test_n6_a_conferencia_do_fim_acusa_o_setup_exe`) passam sem mudar.
  - D-811 "ok": a seção "Cada proteção", "Volta 4": cada proteção desligada numa cópia, com o resultado em
    `anexos/reversao-volta4-resultado.txt`.
  - D-812 "ok": a seção "De onde vem cada dado", "Volta 4".
  - D-813 "ok": o que o Windows faz com o nome (lido na Microsoft e rodado no PC, em "O que li") e a recusa pelo nome
    completado, não pelo texto.
  - D-798 "fechou": nenhum rótulo de pronto neste ramo.

- **Volta 5:**
  - D-816: o gh que nem abriu não é pedido, e o rascunho é apagado:
    `tests/test_publicar_versao.py::test_volta5_achado4_o_gh_que_nem_abre_no_liberar_nao_conta_como_pedido` e
    `tests/test_publicar_versao.py::test_volta5_achado4_so_o_gh_que_nao_abriu_de_verdade_e_nada_saiu`; os testes
    `test_d816_*` da volta 4 (o resto continua sem apagar nada) passam sem mudar.
  - D-773: `tests/test_publicar_versao.py::test_volta5_achado1_as_frases_de_ja_existe_dao_o_comando_do_destino` (as
    três frases; seguir a frase apaga na pasta e não toca o GitHub).
  - D-767 e D-813: `tests/test_windows_peca.py::test_volta5_o_programa_num_fluxo_escondido_de_outro_arquivo_e_recusado`
    (o Windows roda o fluxo sem a peça; a peça o recusa nos três caminhos) e
    `tests/test_publicar_versao.py::test_volta5_achado3a_o_gh_de_verdade_fechado_por_tempo_no_apagar_diz_que_pediu`.
  - D-811: `anexos/reversao-volta5-resultado.txt` (10 de 10 acusadas).
  - D-812: "De onde vem cada dado", "Volta 5".
  - D-775, D-815, D-798: entrego à gerente, sem rótulo; é a minha última volta.

- **Volta 6:**
  - D-727 "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né": o Visual C++ vai
    dentro do pacote da atualização e do instalador também quando a pasta é montada do zero:
    `tests/test_publicar_versao.py::test_volta6_a_versao_montada_do_zero_leva_o_visual_c_e_e_publicada` (com e sem o
    instalador: o arquivo e a versão em instalar\ dentro do pacote publicado). A pasta pronta continua cobrada igual:
    `tests/test_publicar_versao.py::test_volta6_a_mesma_conferencia_da_pasta_em_todos_os_caminhos` (a pasta de fora
    sem o Visual C++, a frase de sempre) e o teste antigo `test_a_pasta_pronta_de_outra_versao_e_recusada`, sem mudar.
  - D-767 "não faça mais nada escodindo ou de mentira": o teste de reversão passa pelo `construir_pasta` de verdade
    (trocados só o PyInstaller, que escreve o que o de verdade escreve, lido do próprio comando, e as peças de entrada);
    a pasta que a prova montou de verdade foi lida (`anexos/volta6-a-pasta-da-prova.txt`). O PyInstaller e o vpk de
    verdade ficam para a prova à vista ("A prova de verdade", Volta 6).
  - D-773 "A": `tests/test_publicar_versao.py::test_volta6_achado2_a_frase_do_motor_que_falta_da_o_comando_do_destino`
    (na pasta, a frase tem o `--pasta` e segui-la publica o motor na pasta, sem tocar o GitHub).
  - D-776, D-777, D-788, D-789, D-795: nada muda; os testes deles passam sem mudar (lista em "Testes").
  - D-785 (item 8, publicar à vista): não rodei o publicar, o PyInstaller nem o vpk de verdade.
  - D-815 "ok": escritor novo; comecei por este formulário.
  - D-816 "A , mas onde estamos antes de você fazer qualquer processo": nada muda no que é apagado; o achado 1 ganhou o
    teste (`tests/test_publicar_versao.py::test_volta6_achado1_o_apagar_em_que_o_gh_nem_abre_diz_nao_apaguei`).
  - D-817 "pode": nenhum teste antigo mudou nesta volta.
  - D-811 (cada proteção com o teste que falha sem ela): 10 de 10 acusadas (`anexos/reversao-volta6-resultado.txt`).

- **Volta 7:**
  - D-818 "vai ter que reprogramar?" · "A": a pasta já montada sem o Tesseract, sem um idioma, com um arquivo dele vazio,
    com um Visual C++ falso (lido pela peça de verdade do Windows), sem a versão do Visual C++ ou com a versão errada →
    o publicar recusa antes do vpk, nada é publicado, e a frase é a mesma que a pasta montada do zero recebe com o mesmo
    defeito; a montada do zero inteira continua passando:
    `tests/test_publicar_versao.py::test_d818_a_pasta_ja_montada_e_conferida_igual_a_montada_do_zero` (6 casos). A
    mesma régua do Visual C++ na montagem e na pasta: `tests/test_empacotar.py::test_d818_a_montagem_e_a_pasta_usam_a_mesma_regua_do_visual_c`.
    Os testes antigos mudados (só a pasta de mentira e o que ela precisa) estão listados em "O que já está escolhido e
    testado aqui", Volta 7; todos continuam passando, no código novo e no de `db4b377a` (88 de 88 antigos, em
    `anexos/reversao-volta7-codigo-antigo.txt`).
  - D-727: o pacote cobra o Visual C++, a versão dele e o Tesseract
    (`tests/test_publicar_versao.py::test_volta7_achado3_o_pacote_sem_uma_peca_e_recusado_depois_do_vpk`, 4 casos, e
    `tests/test_publicar_versao.py::test_volta7_achado3_o_pacote_montado_do_zero_sem_o_tesseract_e_recusado`).
  - D-767: a leitura da assinatura nos testes novos do Visual C++ falso é a de verdade; a de mentira só responde pelos
    Visual C++ de prova (escrito na preparação `ambiente`).
  - D-773: `tests/test_publicar_versao.py::test_volta7_achado5_a_pasta_das_provas_com_espaco_no_nome`.
  - D-776, D-777, D-788, D-789, D-795, D-816, D-817: nada mudou neles; os testes deles passam sem mudar.
  - D-785 (item 8): nada de verdade rodou; o roteiro da prova está em "A prova de verdade", Volta 7.
  - D-815: segunda e última volta deste escritor.

- **Volta 8:**
  - D-605: nenhum teste antigo mudou (`git diff 21f1fc50 -- tests/` só acrescenta no fim de `tests/test_publicar_versao.py`);
    os 98 antigos do publicar passam no código novo e, com o arquivo novo, no código de `21f1fc50` (111 de 121 lá: os 98
    antigos e 13 novos que cobram proteções que já existiam). O programa instalado: `tests/test_decisoes_atualizacao.py`
    38 de 38 e o caso do Visual C++ de `tests/test_decisoes_preparo_d749.py` passam; o teste novo do baixo 6 prova que,
    para todo arquivo que o publicar aceita, o programa instalado lê a mesma versão de hoje.
  - D-727: o Visual C++ e a versão dele continuam cobrados de toda pasta e todo pacote; a leitura da versão é uma só
    (`tests/test_publicar_versao.py::test_volta8_baixo6_o_publicar_e_o_programa_instalado_usam_a_mesma_leitura`).
  - D-767: o Visual C++ de outro assinante é uma cópia do powershell.exe do Windows, lida pela peça de verdade
    (`tests/test_publicar_versao.py::test_volta8_baixo1b_um_programa_da_microsoft_que_nao_e_o_visual_c_e_recusado_pela_mesma_regua`).
    O defeito 1 não foi feito (parado).
  - D-773: o `--apagar` na pasta das provas e no GitHub (`tests/test_publicar_versao.py::test_volta8_defeito2_o_apagar_diz_que_apagou_quando_apagou`).
  - D-776, D-777, D-789, D-795: nada desta volta toca a conta do espaço, as saídas, a diferença nem o Setup.exe
    (conferido no `git diff 21f1fc50`).
  - D-785 (item 8): não rodei o publicar de verdade; o roteiro para a gerente está em "A prova de verdade", Volta 8.
  - D-788: nada mudou em `core/ocr_kraken.py` (o defeito 1 parou antes de mexer); o programa instalado acha o motor
    como hoje.
  - D-815: sou o escritor novo desta volta (a primeira das minhas duas).
  - D-816: o caminho depois do pedido de liberar não passa pelo apagar; os `test_d816_*` passam.
  - D-817: nenhum teste antigo saiu nem mudou.
  - D-818: as proteções da pasta já montada ganharam os testes que faltavam (baixos 1 a 3), provados pelas mutações
    U8 a U12 ("Cada proteção", Volta 8).

## Testes

- **No PC, um arquivo por vez** (19/11, com `QT_QPA_PLATFORM=offscreen`):
  `tests/test_publicar_versao.py` 20 passaram; `tests/test_publicar_motor.py` 12; `tests/test_publicar_servidor.py` 11
  (três vezes seguidas, para ver se o corte no meio é estável); `tests/test_windows_peca.py` 55 passaram e 2 pulados (os
  que só rodam no GitHub); `tests/test_empacotar.py` 41; `tests/test_decisoes_atualizacao.py` 38;
  `tests/test_decisoes_brasao.py` 22; `tests/test_nome_do_pacote.py` 5; `tests/test_ocr_kraken.py` 27 e 6 pulados (o
  motor não está nesta cópia, o defeito antigo nº 330); `tests/test_ocr_diagnostico.py` 6;
  `tests/test_windows_janela_de_prova.py` 10; `tests/test_conferencias_codigo.py` 77; `tests/test_conferencias_pacote.py`
  20; `tests/test_conferencias_excecoes.py` 14. Porteiro no PC: "nada novo" (175 lugares).
- **Prova de reversão** numa cópia à parte (git archive no rascunho da sessão, fora do projeto): 19 de 19 proteções
  acusadas pelo seu teste (`anexos/reversao-resultado.txt`, script em `anexos/reversao-mutacoes.py.txt`); os testes
  novos rodados no código antigo falham (`anexos/reversao-codigo-antigo.txt`).
- **No GitHub, rodada 1:** 44642471223, sobre o commit 2e88d125: **failure**. O porteiro passou (PORTEIRO: success,
  o trabalho "Porteiro (juiz da versao de teste)"); as partes 1 a 4 e os botões passaram; na parte 5 falhou
  `tests/test_windows_peca.py::test_a_assinatura_digital_e_lida_pela_peca_de_verdade` (CouldNotAutoloadMatchingModule:
  o defeito da lista de módulos herdada do PowerShell 7, consertado em `fa28ab5b`). As rodadas 44644159110 e
  44644488805 foram canceladas por mim (testavam commits já passados).
- **No PC, depois do conserto:** `tests/test_windows_peca.py` 54 passaram e 2 pulados; o teste novo da lista de
  módulos falhou antes do conserto (CouldNotAutoloadMatchingModule) e passa depois.
- **No GitHub, rodada 4:** 44645740920, sobre o commit fa28ab5b (o conserto da lista de módulos): **success**, todas
  as partes e os botões. PORTEIRO: success (o trabalho "Porteiro (juiz da versao de teste)").
- **Volta 2, no PC, um arquivo por vez** (19-20/11): `tests/test_publicar_versao.py` 36 passaram;
  `tests/test_publicar_servidor.py` 13; `tests/test_publicar_motor.py` 12; `tests/test_windows_peca.py` 57 e 2 pulados;
  `tests/test_empacotar.py` 41; `tests/test_decisoes_atualizacao.py` 38; `tests/test_windows_janela_de_prova.py` 10;
  `tests/test_conferencias_codigo.py` 77; `tests/test_nome_do_pacote.py` 5. Porteiro no PC: "nada novo" (175).
  Reversão: `anexos/reversao-volta2-resultado.txt`.
- **No GitHub, volta 2, rodada final:** 44663876080, sobre o ramo em 0d51ad5e: **success** na primeira tentativa, todas
  as partes e os botões. PORTEIRO: success (o trabalho "Porteiro (juiz da versao de teste)").
- **No GitHub, volta 2, rodada anterior:** 44661337397, sobre 0f7639eb: **failure**. PORTEIRO: success. Falharam
  `tests/test_publicar_versao.py::test_achado5_erro_do_disco_vira_frase` (o teste supunha o vpk instalado, como no PC;
  no Windows do GitHub não há vpk e a linha de comando parava antes; consertado no teste em `0d51ad5e`, família F4) e
  `tests/test_decisoes_so_as_letras.py::test_d148_desfazer_o_automatico_devolve_o_so_as_letras_do_livro` (o instável
  conhecido, por tempo; não é deste passo).
- **No GitHub, rodada final da volta 1:** 44650408369, sobre o ramo em a14b7d55 (o código de 0ef0da17; depois só o formulário):
  **success** na segunda tentativa (só a parte 3 rodou de novo). PORTEIRO: success (o trabalho "Porteiro (juiz da
  versao de teste)"). Na primeira tentativa falhou só
  `tests/test_decisoes_gravura_a_mao.py::test_d659_g_outros_filtros_a_mao_nada_e_procurado_e_sai_igual_ao_de_antes`
  ("procurou: [0]"), o teste instável já conhecido (catálogo P1-gh-5), que não usa nada deste passo.

- **Volta 3, no PC, um arquivo por vez** (20/11, `QT_QPA_PLATFORM=offscreen`): `tests/test_publicar_versao.py` 49
  passaram; `tests/test_windows_peca.py` 62 passaram e 2 pulados; `tests/test_publicar_servidor.py` 14;
  `tests/test_publicar_motor.py` 12; `tests/test_empacotar.py` 41; `tests/test_decisoes_atualizacao.py` 38;
  `tests/test_nome_do_pacote.py` 5; `tests/test_decisoes_brasao.py` 22; `tests/test_windows_janela_de_prova.py` 10;
  `tests/test_ocr_kraken.py` 27 e 6 pulados; `tests/test_conferencias_codigo.py` 77; `tests/test_conferencias_excecoes.py`
  14; `tests/test_conferencias_pacote.py` 20. Porteiro no PC: "nada novo" (175 lugares). (Uma vez rodei dois arquivos
  juntos, por engano: `test_publicar_versao.py` e `test_publicar_motor.py`; depois, só um por vez.)
- **Volta 3, reversão:** os testes novos no código da volta 2 (9cd555a5): falham os 15 do defeito consertado
  (`anexos/reversao-volta3-codigo-antigo.txt`); passam lá os dos achados 5 e 6 e o do soltar do grupo, que cobram
  proteções que já existiam e são provados pela mutação (B5, B6, B4b).
- **No GitHub, volta 3:** rodada 44675872042, sobre o ramo em 2e906e94 (o código de e4263c0a e três docstrings de um
  teste). Resultado: **success** na segunda tentativa. PORTEIRO: success (o trabalho "Porteiro (juiz da versao de teste)", nas duas tentativas). Na primeira tentativa falhou só a parte 2: `tests/test_caixinha_do_dividir_nao_volta.py` saiu com o código 0xC0000409 e "sem saída", um travamento do Qt que não usa nada deste passo (instável novo, em "Ideias e bugs"); a parte 2 rodou de novo e passou. A rodada 44675045916, sobre 05f743ca, foi cancelada por mim aos 7 minutos (o porteiro já tinha dado success), porque depois dela mudaram um comentário da peça e as docstrings.

- **Volta 4, no PC, um arquivo por vez** (20/11, `QT_QPA_PLATFORM=offscreen`): `tests/test_publicar_versao.py` 70
  passaram; `tests/test_windows_peca.py` 67 passaram e 2 pulados (os que só rodam no GitHub); `tests/test_publicar_motor.py`
  12; `tests/test_publicar_servidor.py` 14; `tests/test_empacotar.py` 41; `tests/test_decisoes_atualizacao.py` 38;
  `tests/test_windows_janela_de_prova.py` 10; `tests/test_nome_do_pacote.py` 5; `tests/test_decisoes_brasao.py` 22;
  `tests/test_decisoes_ajudante_da_atualizacao.py` 37; `tests/test_decisoes_testes_a_distancia.py` 13;
  `tests/test_ocr_kraken.py` 27 e 6 pulados; `tests/test_conferencias_codigo.py` 77; `tests/test_conferencias_excecoes.py`
  14; `tests/test_conferencias_pacote.py` 20. Porteiro no PC: "nada novo" (175 lugares). Os testes do desinstalar não
  rodei (falham no PC por causa da pasta temporária no C:, achado 12; o GitHub os roda).
- **Volta 4, reversão:** os testes novos no código de `5f96975b`: 26 de 27 casos falham
  (`anexos/reversao-volta4-codigo-antigo.txt`, com a leitura de cada falha no fim); o do achado 10 passa lá (a proteção
  já existia) e é provado pela mutação V10. Mutações: 24 de 24 acusadas (`anexos/reversao-volta4-resultado.txt`).
- **No GitHub, volta 4:** a rodada 44748279819 (sobre `2d866750`) foi cancelada por mim aos 6 minutos: depois dela
  corrigi dois textos (docstrings) da peça e da vigia. Rodada que vale: 44748591841, sobre o ramo depois de `595cc293`
  (depois dele, só este formulário). Resultado: **success** na terceira tentativa. PORTEIRO: success (o trabalho
  "Porteiro (juiz da versao de teste)"). As partes 1, 3, 4 e 5 e os botões passaram na primeira tentativa. A parte 2
  falhou duas vezes num teste que não usa nada deste passo, `tests/test_decisoes_so_as_letras.py`: na primeira, o
  arquivo inteiro caiu com o código 0xC0000005 (um travamento do Qt, "cannot get C stack"); na segunda, o
  `test_d148_desfazer_o_automatico_devolve_o_so_as_letras_do_livro` falhou por tempo ("não aconteceu a tempo: o
  projeto.json com o 'Só as letras' desfeito"), o instável já conhecido (catálogo P1-gh-4). Na terceira, passou.

- **Volta 5, no PC, um arquivo por vez** (20/11, `QT_QPA_PLATFORM=offscreen`): `tests/test_publicar_versao.py` 78
  passaram; `tests/test_windows_peca.py` 68 passaram e 2 pulados; `tests/test_publicar_motor.py` 12;
  `tests/test_publicar_servidor.py` 14; `tests/test_empacotar.py` 41; `tests/test_decisoes_atualizacao.py` 38;
  `tests/test_windows_janela_de_prova.py` 10; `tests/test_nome_do_pacote.py` 5;
  `tests/test_decisoes_ajudante_da_atualizacao.py` 37; `tests/test_decisoes_testes_a_distancia.py` 13;
  `tests/test_conferencias_codigo.py` 77; `tests/test_conferencias_excecoes.py` 14; `tests/test_conferencias_pacote.py`
  20. Porteiro no PC: "nada novo" (175 lugares).
- **Volta 5, reversão:** os testes novos no código de `595cc293`: 8 de 9 casos falham
  (`anexos/reversao-volta5-codigo-antigo.txt`, com a leitura no fim); o do achado 3 (b) passa lá (a proteção existia
  sem teste) e é provado pela mutação W3b. Mutações: 10 de 10 acusadas (`anexos/reversao-volta5-resultado.txt`).
- **No GitHub, volta 5:** rodada 44766224353, sobre o ramo depois de `35ec0c27` (depois, só a pasta deste relatório).
  Resultado: **success** na segunda tentativa. PORTEIRO: success (o trabalho "Porteiro (juiz da versao de teste)"). Na
  primeira, falhou só a parte 3, em `tests/test_decisoes_gravura_a_mao.py::test_d659_g_outros_filtros_a_mao_nada_e_procurado_e_sai_igual_ao_de_antes`
  ("procurou: [0]"), o instável já conhecido (catálogo P1-gh-5), que não usa nada deste passo; a parte 3 rodou de novo e passou.

- **Volta 6, no PC, um arquivo por vez** (20/11, `QT_QPA_PLATFORM=offscreen`): `tests/test_publicar_versao.py` 85
  passaram; `tests/test_windows_peca.py` 69 passaram e 2 pulados; `tests/test_empacotar.py` 41;
  `tests/test_publicar_motor.py` 12; `tests/test_publicar_servidor.py` 14; `tests/test_decisoes_atualizacao.py` 38;
  `tests/test_windows_janela_de_prova.py` 10; `tests/test_nome_do_pacote.py` 5; `tests/test_decisoes_brasao.py` 22;
  `tests/test_decisoes_ajudante_da_atualizacao.py` 37; `tests/test_decisoes_testes_a_distancia.py` 13;
  `tests/test_conferencias_codigo.py` 77; `tests/test_conferencias_excecoes.py` 14; `tests/test_conferencias_pacote.py`
  20. Porteiro no PC: "nada novo" (175 lugares). Os do desinstalar não rodei (falham no PC, Lista de bugs de 20/11).
  Na primeira passada de `tests/test_windows_peca.py` o meu teste novo usava `windows._por_que_recusa` (com "_", de
  dentro da peça) e o teste antigo `test_a_peca_e_fechada_ninguem_usa_o_que_tem_sublinhado_fora_dela` acusou; o teste
  novo passou a perguntar pelo `rodar_e_esperar` (sem mudar o antigo).
- **Volta 6, reversão** (`anexos/reversao-volta6-codigo-antigo.txt`; o código de `b9300da8` numa cópia à parte, com os
  dois arquivos de teste novos por cima): 7 de 8 casos falham. Os dois do defeito da prova falham com a mesma frase da
  prova ("a pasta do programa não serve: ... não tem o Visual C++ em instalar\"); o de "todos os caminhos" falha na
  montagem sem o Visual C++; o da cópia pela metade, na montagem que não parava; o do achado 2 na pasta, na frase sem o
  `--pasta` (e o do GitHub pela função que não existia); o do achado 3, na frase "use a função dela". O do achado 1
  passa lá (a proteção existia, sem teste) e é provado pela mutação Y7 (a X3 de quem quebrou).
- **Volta 6, mutações** (`anexos/reversao-volta6-resultado.txt`, script em `anexos/reversao-volta6-mutacoes.py.txt`):
  10 de 10 acusadas, numa cópia de `3abf9acf`.
- **No GitHub, volta 6:** rodada 44800950547, sobre o ramo em `d73e7fc8` (o código de `3abf9acf`; depois dele só a pasta
  deste relatório): **success** na primeira tentativa, todas as partes (1 a 5), os botões e o resumo. PORTEIRO: success
  (o trabalho "Porteiro (juiz da versao de teste)"). O registro diz "TESTADO_SHA: d73e7fc8..." nas 52 linhas. A rodada
  44799633578 (sobre `3abf9acf`) foi cancelada por mim antes do fim: depois dela entraram os anexos `.txt` da reversão,
  e a rodada que vale tem de ser a do último commit que não é só `.md`.

- **Volta 7, no PC, um arquivo por vez** (20/11, `QT_QPA_PLATFORM=offscreen`): `tests/test_publicar_versao.py` 98
  passaram; `tests/test_empacotar.py` 42; `tests/test_publicar_motor.py` 12; `tests/test_publicar_servidor.py` 14;
  `tests/test_decisoes_atualizacao.py` 38; `tests/test_windows_peca.py` 69 e 2 pulados; `tests/test_windows_janela_de_prova.py`
  10; `tests/test_nome_do_pacote.py` 5; `tests/test_decisoes_brasao.py` 22; `tests/test_decisoes_ajudante_da_atualizacao.py`
  37; `tests/test_decisoes_testes_a_distancia.py` 13; `tests/test_conferencias_codigo.py` 77;
  `tests/test_conferencias_excecoes.py` 14; `tests/test_conferencias_pacote.py` 20. Porteiro no PC: "nada novo" (175
  lugares). `tests/test_decisoes_preparo_d749.py`: 3 falham no PC ("tudo na pasta de mentira": o comando tem "C:\"),
  igual no código de `db4b377a` (rodado numa cópia): o mesmo caso dos testes do desinstalar (a pasta temporária do PC no
  C:), em "Ideias e bugs"; não é deste trabalho.
- **Volta 7, reversão** (`anexos/reversao-volta7-codigo-antigo.txt`; o código de `db4b377a` numa cópia à parte, com o
  arquivo de teste de `4e8fdd98` por cima): 9 de 12 casos novos falham (os 5 da D-818 de então, "DID NOT RAISE Parou":
  a pasta estragada era publicada; 3 do pacote sem uma peça: a versão do Visual C++ e o Tesseract da pasta já montada;
  o do empacotar sozinho: "a pasta recusada foi mudada antes da recusa"). Passam lá: o pacote sem o Visual C++ (a
  conferência do pacote já o pegava), o montado do zero sem o Tesseract (já pegava com as peças) e o da pasta com espaço
  (as aspas já estavam lá); os três cobram proteções que existiam sem teste e são provados pelas mutações. Os 88 testes
  antigos, com a pasta de mentira nova, passam no código antigo (a pasta nova não muda o que eles cobram). O caso do
  arquivo do Tesseract vazio e o teste da régua única entraram depois (`25c514ad`) e são provados pelas mutações R5,
  R9 e R10.
- **Volta 7, mutações** (`anexos/reversao-volta7-resultado.txt`; script `anexos/reversao-volta7-mutacoes.py.txt`), numa
  cópia de `25c514ad`: ver "Cada proteção", Volta 7.
- **No GitHub, volta 7:** rodada 44816609032, sobre o ramo em `eda1dc6b` (o código de `25c514ad`; depois dele só a pasta
  deste relatório): **success** na primeira tentativa, todas as partes (1 a 5), os botões e o resumo. PORTEIRO: success
  (o trabalho "Porteiro (juiz da versao de teste)"). O registro diz "TESTADO_SHA: eda1dc6b..." nas 52 linhas.

- **Volta 8, no PC, um arquivo por vez** (20/11, `QT_QPA_PLATFORM=offscreen`): `tests/test_publicar_versao.py` 121
  passaram (98 antigos e 23 casos novos); `tests/test_empacotar.py` 42; `tests/test_decisoes_atualizacao.py` 38;
  `tests/test_publicar_motor.py` 12; `tests/test_publicar_servidor.py` 14; `tests/test_decisoes_ajudante_da_atualizacao.py`
  37; `tests/test_decisoes_preparo_d749.py` 5 passam e os mesmos 3 da volta 7 falham no PC (o comando com "C:\", a pasta
  temporária do PC; não é deste trabalho, em "Ideias e bugs", Volta 7). Porteiro no PC: "nada novo" (175 lugares).
- **Volta 8, reversão** (`anexos/reversao-volta8-codigo-antigo.txt`; o código de `21f1fc50` numa cópia à parte, com o
  arquivo de testes novo por cima): **10 dos 23 casos novos falham** lá (os 6 do defeito 2: a frase depois de apagar é
  "não existe em", e `Apagado` não existia; 4 do baixo 6: a leitura única não existia). Passam lá os 13 que cobram
  proteções que já existiam (os baixos 1 a 3 e os casos do baixo 6 que a conferência já recusava); servem para a
  proteção não sumir calada e são provados pelas mutações. Os 98 antigos passam lá.
- **Volta 8, mutações** (`anexos/reversao-volta8-resultado.txt`; script `anexos/reversao-volta8-mutacoes.py.txt`), numa
  cópia de `b2863630`: ver "Cada proteção", Volta 8.

## Caminho e função

- O publicar da versão, com ou sem pasta pronta, com ou sem instalador → `empacotar.construir_pacote_do_velopack` →
  `empacotar.rodar_vpk` (prova: `tests/test_publicar_versao.py::test_d777_o_instalador_so_quando_pedido_e_o_publicado_e_o_da_atualizacao`,
  as duas passadas pelo mesmo caminho).
- Os dois destinos → `publicar_versao_kaique.publicar_arquivos` (prova: o mesmo fluxo na pasta,
  `tests/test_publicar_versao.py::test_d53_nada_e_liberado_antes_da_assinatura_lida_de_volta`, e no GitHub,
  `tests/test_publicar_versao.py::test_o_github_sobe_como_rascunho_le_de_volta_e_so_entao_libera`).
- A versão do programa e o motor → `publicar_versao_kaique.publicar_arquivos` e `publicar_versao_kaique.obter_motor_publicado`
  (os dois testes acima publicam os dois).
- A pasta do motor e o arquivo do motor → `ocr_kraken.conferir_ficha` (prova:
  `tests/test_publicar_motor.py::test_o_arquivo_do_motor_leva_tudo_da_ficha_e_e_conferido` e
  `tests/test_publicar_motor.py::test_o_motor_estragado_ou_de_outra_versao_nao_confere`).
- A forma do motor no empacotador e no programa → `ocr_kraken.problemas_da_forma` (prova:
  `tests/test_publicar_motor.py::test_o_empacotador_usa_a_forma_do_motor_do_lugar_unico`).
- O que o vpk escreve e o que vai ao destino → `publicar_versao_kaique.arquivos_da_versao` (prova: o teste da D-768).
- Todo PowerShell que a peça abre (o rodar e esperar, o lançar solto, os scripts do trabalho com licença) → o mesmo
  comando e o mesmo ambiente (`_comando_do_powershell`, `_ambiente_do_powershell`; prova:
  `tests/test_windows_peca.py::test_o_powershell_nao_herda_os_modulos_do_powershell_7`, pelo rodar e pelo lançar solto).
- A assinatura digital do Visual C++ → `windows.ler_assinatura_digital` (prova:
  `tests/test_windows_peca.py::test_o_empacotar_le_a_assinatura_pela_peca_e_nao_abre_o_powershell`).
- O servidor e o publicar na pasta → o mesmo desenho (`DestinoPasta` grava; o servidor lê pelas mesmas regras; prova:
  `tests/test_publicar_servidor.py::test_d773_o_indice_junta_as_versoes_liberadas_e_nao_mostra_o_rascunho`, que monta a
  pasta pelo próprio `DestinoPasta`).

- **Volta 3:** só o rascunho apagado → `apagar_publicacao(so_rascunho=True)` (prova, os dois destinos pelo mesmo caminho:
  `tests/test_publicar_versao.py::test_volta3_achado1_uma_leitura_atrasada_depois_de_liberar_nunca_apaga_a_versao_liberada`
  e `tests/test_publicar_versao.py::test_volta3_achado1_no_github_a_leitura_atrasada_tambem_nunca_apaga_a_liberada`); as
  três cópias do publicar → `empacotar.copiar_inteiro` (prova:
  `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_que_nao_termina_de_copiar_nao_fica_com_o_nome_certo` e os
  testes antigos do envio à pasta); o rodar, o lançar e o grupo → `windows._programa_com_funcao_propria` (prova: o mesmo
  lote recusado pelos três, `tests/test_windows_peca.py::test_bat_e_cmd_sao_recusados_pelo_rodar_pelo_lancar_e_pelo_grupo`);
  a vigia do vpk, da compressão, da cópia e do gh → `empacotar.vigia_do_espaco` (prova: os testes antigos da vigia do vpk
  e da compressão continuam, e
  `tests/test_publicar_versao.py::test_volta3_achado7_o_motor_baixado_entra_na_conta_e_na_vigia` e
  `tests/test_publicar_versao.py::test_volta3_achado7_o_gh_que_baixa_e_fechado_pela_vigia`); o nome do motor →
  `versao.PREFIXO_DO_MOTOR` (prova: `tests/test_publicar_versao.py::test_volta3_achado7_o_nome_do_motor_so_em_versao_py`).

- **Volta 4:**
  - o caminho de erro depois do pedido de liberar, na versão e no motor, nos dois destinos →
    `publicar_versao_kaique.publicar_arquivos` → `_frase_depois_do_pedido_de_liberar` (nenhum apagar). Prova, o mesmo
    resultado em todos os caminhos (pasta e GitHub; versão e motor; 1, 2, 3 e 10 leituras atrasadas; o liberar que
    falha; o Ctrl+C): `tests/test_publicar_versao.py::test_d816_depois_do_pedido_de_liberar_nada_e_apagado_com_qualquer_atraso`,
    `tests/test_publicar_versao.py::test_d816_o_motor_tambem_nunca_e_apagado_depois_do_pedido_de_liberar`,
    `tests/test_publicar_versao.py::test_d816_o_liberar_que_falha_e_fica_rascunho_nao_apaga_e_diz_o_comando` e
    `tests/test_publicar_versao.py::test_d816_ctrl_c_depois_do_pedido_de_liberar_nao_apaga`;
  - o caminho de erro de antes do pedido de liberar e o `--apagar` → `publicar_versao_kaique.apagar_publicacao` (a frase
    de cada desfecho; prova: `tests/test_publicar_versao.py::test_volta4_achado3_a_frase_diz_se_pediu_para_apagar`,
    `tests/test_publicar_versao.py::test_volta4_achado3_o_pedido_de_apagar_sem_resposta_diz_que_pediu`,
    `tests/test_publicar_versao.py::test_volta4_achado3_liberada_no_meio_do_apagar_nunca_vira_apagada`,
    `tests/test_publicar_versao.py::test_volta4_achado4_nao_achei_logo_depois_de_criar_nao_e_apagado`, e os testes antigos
    do `--apagar`, que continuam);
  - o rodar genérico, o lançar solto, o grupo (e por ele o vpk e o gh) → `windows._por_que_recusa`, com o nome de
    `windows._caminho_do_programa` (prova, o mesmo nome recusado pelos três:
    `tests/test_windows_peca.py::test_volta4_o_nome_com_ponto_no_fim_e_lido_como_o_windows_completa`,
    `tests/test_windows_peca.py::test_volta4_o_programa_que_nao_deixa_ler_e_recusado_com_frase_propria`,
    `tests/test_windows_peca.py::test_volta4_a_segunda_olhada_depois_do_path_recusa_o_lote_achado_pelo_pathext`);
  - o vpk e todos os pedidos ao gh → `windows.rodar_em_grupo` (prova: os dois chamam o laço,
    `tests/test_publicar_versao.py::test_volta4_achado8_o_gh_roda_pelo_laco_unico_da_peca_e_fecha_o_que_abriu`; o laço,
    `tests/test_windows_peca.py::test_volta4_rodar_em_grupo_e_o_laco_unico_com_a_saida_a_vigia_e_o_tempo`; os testes
    antigos do vpk, que continuam);
  - a soma do GitHub sem a soma pronta (na leitura de volta da versão, do motor e do motor que a versão pede) →
    `DestinoGitHub.soma` → `baixar_vigiado` no rascunho dado por `usar_rascunho` (prova:
    `tests/test_publicar_versao.py::test_volta4_achado7_sem_a_soma_pronta_o_download_vai_ao_rascunho_pela_vigia` e
    `tests/test_publicar_versao.py::test_volta4_achado7_no_publicar_sem_a_soma_pronta_tudo_e_baixado_no_rascunho`, este
    pela versão e pelo motor); a conta → `publicar` e `publicar_motor`, com `soma_pode_baixar` de cada destino (prova:
    `tests/test_publicar_versao.py::test_volta4_achado7_a_conta_do_espaco_soma_o_que_a_soma_pode_baixar` e o mesmo do
    publicar sem a soma pronta);
  - toda gravação num nome provisório com troca de nome (a cópia conferida, o motor comprimido, a gravação da peça) →
    `windows.gravar_no_disco` (prova:
    `tests/test_publicar_versao.py::test_volta4_achado11_a_copia_e_o_motor_gravam_no_disco_antes_de_conferir_e_trocar` e
    `tests/test_windows_peca.py::test_volta4_a_peca_manda_gravar_no_disco_antes_de_trocar_o_nome`).

- **Volta 5:**
  - toda frase que manda apagar (a D-816, as do apagar, a da liberada no meio, o "sobrou um rascunho", os dois "já
    existe") → `_Destino.comando_de_apagar` (prova, as três que eram à mão:
    `tests/test_publicar_versao.py::test_volta5_achado1_as_frases_de_ja_existe_dao_o_comando_do_destino`);
  - "pedi para apagar" → só o `DestinoGitHub._pedir_para_apagar` (`ApagarSemResposta`; prova:
    `tests/test_publicar_versao.py::test_volta5_achado2_a_leitura_sem_resposta_antes_do_pedido_nao_vira_pedi_para_apagar`
    e `tests/test_publicar_versao.py::test_volta5_achado3a_o_gh_de_verdade_fechado_por_tempo_no_apagar_diz_que_pediu`);
  - "não saiu nada" → `DestinoGitHub._gh` (`NadaSaiu`, do `abriu: False` do laço único), usado pelo caminho de erro
    de `publicar_arquivos` (a versão e o motor; prova:
    `tests/test_publicar_versao.py::test_volta5_achado4_o_gh_que_nem_abre_no_liberar_nao_conta_como_pedido`);
  - o fluxo escondido, nos três caminhos da peça → `windows._por_que_recusa` → `windows._e_fluxo_escondido` (prova:
    `tests/test_windows_peca.py::test_volta5_o_programa_num_fluxo_escondido_de_outro_arquivo_e_recusado`).

- **Volta 6** ("a pasta está pronta para o vpk" → `empacotar.conferir_pasta_pronta`; "pôr o Visual C++ na pasta" →
  `empacotar.construir_pasta` → `empacotar.preparar_pasta_para_o_velopack`; "a saída leva o Visual C++?" →
  `empacotar.Saida.vc_em_instalar`):
  - o publicar montado do zero → `construir_pasta(ATUALIZACAO)` (põe) → `conferir_pasta_pronta` →
    `construir_pacote_do_velopack` → `conferir_pasta_pronta` de novo → `rodar_vpk`;
  - o publicar com `--pasta-pronta` → `conferir_pasta_pronta` → o mesmo `construir_pacote_do_velopack`;
  - a segunda passada do instalador → `preparar_saida(INSTALADOR)` (só o motor) → `conferir_pasta_pronta(INSTALADOR)`;
  - a volta da pasta depois do instalador → `preparar_saida(ATUALIZACAO, None, motor)` (não mexe no Visual C++);
  - o empacotar chamado direto, sem pasta → `construir_pasta(ATUALIZACAO)` → `conferir_pasta_pronta`; com uma pasta de
    fora → `conferir_pasta_pronta` antes do vpk;
  - a pasta portátil e o Inno → `construir_pasta(PORTATIL)` (`vc_em_instalar=False`: sem instalar\; o Inno pega de
    `build\`);
  - a conferência do pacote depois do vpk → `esperados_no_pacote_do_velopack` (pelo mesmo campo).
  Prova, o mesmo resultado em todos: `tests/test_publicar_versao.py::test_volta6_a_mesma_conferencia_da_pasta_em_todos_os_caminhos`
  (a montada passa; a montada sem o Visual C++ e a de fora sem o Visual C++ recebem a mesma frase; o empacotar direto
  com a de fora para antes do vpk; o empacotar direto sem pasta empacota com o Visual C++; a portátil sem instalar\) e
  `tests/test_publicar_versao.py::test_volta6_a_versao_montada_do_zero_leva_o_visual_c_e_e_publicada` (o publicar
  montado do zero, com e sem o instalador, até a publicação na pasta das provas).
  - toda frase que manda rodar um comando do publicar (o `--apagar` e agora o `--motor`) → `_Destino.comando_de_apagar`
    e `_Destino.comando_de_publicar_o_motor`, pelos mesmos `_argumentos_do_destino` (prova:
    `tests/test_publicar_versao.py::test_volta6_achado2_a_frase_do_motor_que_falta_da_o_comando_do_destino`, pasta e
    GitHub);
  - o caminho de rede pelo rodar, pelo lançar solto e pelo grupo → `windows._por_que_recusa` → `FRASE_CAMINHO_DE_REDE`
    (prova: `tests/test_windows_peca.py::test_volta6_achado3_o_caminho_de_rede_e_recusado_com_a_frase_propria`, os
    três caminhos).

- **Volta 7** ("este arquivo é o Visual C++ oficial?" → `empacotar.conferir_o_visual_c`; "o que é o Tesseract na
  pasta" → `empacotar.relativos_do_tesseract`; "a pasta está pronta para o vpk" → `empacotar.conferir_pasta_pronta`; "o
  pacote saiu certo" → `empacotar.conferir_pacote_do_velopack` → `esperados_no_pacote_do_velopack`):
  - a montagem, o Visual C++ baixado e o achado → `preparar_vc_redist` → `conferir_o_visual_c`;
  - a montagem copia o Tesseract e confere a cópia; o Inno confere o registro → `_destinos_das_pecas` →
    `relativos_do_tesseract`;
  - o publicar montado do zero e o `--pasta-pronta` (cedo) → `conferir_pasta_pronta` → `conferir_o_visual_c` e
    `relativos_do_tesseract`;
  - `construir_pacote_do_velopack` (as duas passadas e o chamado sozinho) → `conferir_pasta_pronta` antes de
    `preparar_saida`;
  - o pacote depois do vpk, com ou sem as peças → `esperados_no_pacote_do_velopack` → `relativos_do_tesseract` e a
    versão do Visual C++.
  Prova, o mesmo resultado nos dois caminhos: `tests/test_publicar_versao.py::test_d818_a_pasta_ja_montada_e_conferida_igual_a_montada_do_zero`
  (a mesma frase para a pasta já montada e a montada do zero, em cada um dos 6 defeitos) e
  `tests/test_empacotar.py::test_d818_a_montagem_e_a_pasta_usam_a_mesma_regua_do_visual_c` (o mesmo motivo na montagem
  e na régua).

- **Volta 8** ("a frase depois de apagar" → `publicar_versao_kaique.Apagado.frase`, devolvida pelo lugar único do apagar,
  `publicar_versao_kaique.apagar_e_conferir`; "a versão do Visual C++ do pacote" → `atualizacao.versao_do_visual_c_do_pacote`):
  | Caminho | Função que usa |
  |---|---|
  | `--apagar <etiqueta> --pasta <pasta>` (a versão e o motor) | `apagar_e_conferir` → `Apagado.frase` |
  | `--apagar <etiqueta>` no GitHub (a versão e o motor) | `apagar_e_conferir` → `Apagado.frase` |
  | o caminho de erro do publicar, antes do pedido de liberar (`publicar_arquivos`) | `apagar_e_conferir` (só o rascunho, logo depois de criar) → `Apagado.frase` |
  | `apagar_publicacao` (quem chama pelo contrato antigo: os testes antigos) | `apagar_e_conferir(...).aviso` |
  | depois do pedido de liberar (D-816) | não apaga: a frase da D-816 (`_frase_depois_do_pedido_de_liberar`), sem mudança |
  | a conferência da pasta (publicar montado do zero, `--pasta-pronta`, a segunda passada, o empacotar sozinho) | `empacotar.conferir_pasta_pronta` → `atualizacao.versao_do_visual_c_do_pacote` |
  | o programa instalado do Kaique (o preparo do computador) | `atualizacao.instalar_visual_c_se_faltar` → `atualizacao.versao_do_visual_c_do_pacote` |
  | quem escreve o arquivo da versão | só a montagem, `empacotar.preparar_pasta_para_o_velopack` (grep do nome do arquivo: nenhum outro) |
  | o pacote depois do vpk | `empacotar.esperados_no_pacote_do_velopack`: cobra que o arquivo está lá (não o lê) |
  Prova do mesmo resultado em todos: `tests/test_publicar_versao.py::test_volta8_defeito2_o_apagar_diz_que_apagou_quando_apagou`
  (quatro caminhos: pasta e GitHub, versão e motor), `tests/test_publicar_versao.py::test_volta8_defeito2_o_caminho_de_erro_usa_a_mesma_frase_do_apagar`
  e `tests/test_publicar_versao.py::test_volta8_baixo6_o_publicar_e_o_programa_instalado_usam_a_mesma_leitura`.
- **Volta 8, o defeito 1 (só o plano):** os seis caminhos da tabela de "A causa", Volta 8, passariam todos pela função
  única da pasta das ferramentas; não feito (parado).

## Cada proteção e o teste que falha sem ela

Cada uma foi desligada numa cópia à parte (git archive no rascunho da sessão, fora do projeto) e o teste dela falhou
(`anexos/reversao-resultado.txt`; o script em `anexos/reversao-mutacoes.py.txt`):
- Nada liberado antes da leitura de volta (recusa da ordem errada) →
  `tests/test_publicar_versao.py::test_d53_nada_e_liberado_antes_da_assinatura_lida_de_volta` (M1).
- Só os arquivos da versão vão ao destino, nunca o Setup.exe →
  `tests/test_publicar_versao.py::test_d768_o_motor_e_a_versao_publicados_numa_pasta_sem_o_motor_no_pacote` (M2).
- O rascunho do C: apagado e conferido também com erro (desfazer) →
  `tests/test_publicar_versao.py::test_d795_o_setup_exe_e_o_rascunho_somem_tambem_quando_da_erro` (M3).
- A conta do espaço recusa antes do vpk →
  `tests/test_publicar_versao.py::test_d776_sem_espaco_para_antes_do_vpk_e_nada_fica` (M4).
- A vigia fecha o vpk abaixo da reserva →
  `tests/test_publicar_versao.py::test_d776_a_vigia_fecha_o_vpk_quando_o_disco_cai_abaixo_da_reserva` (M5).
- A assinatura do motor publicado é conferida (leitura de volta) →
  `tests/test_publicar_versao.py::test_d724_o_motor_com_a_assinatura_de_outra_chave_e_recusado` (M6).
- O motor solto recusado no pacote da atualização →
  `tests/test_publicar_versao.py::test_d768_o_pacote_da_atualizacao_com_o_motor_solto_e_recusado` (M7).
- A falha antes de liberar apaga o rascunho do destino (desfazer) →
  `tests/test_publicar_versao.py::test_a_leitura_de_volta_que_nao_bate_nao_libera_e_apaga_o_rascunho_do_destino` (M8).
- Erro do GitHub nunca vira "não existe" →
  `tests/test_publicar_versao.py::test_o_github_sem_resposta_nunca_vira_nao_publicada` (M9).
- O servidor não serve o rascunho →
  `tests/test_publicar_servidor.py::test_d773_o_indice_junta_as_versoes_liberadas_e_nao_mostra_o_rascunho` (M10).
- A porta do servidor é exclusiva →
  `tests/test_publicar_servidor.py::test_a_porta_ocupada_vira_frase_e_a_janela_diz_que_nao_serve` (M11).
- A ficha confere o tamanho de cada arquivo →
  `tests/test_publicar_motor.py::test_o_motor_estragado_ou_de_outra_versao_nao_confere` (M12).
- O vpk sem a diferença →
  `tests/test_publicar_versao.py::test_d789_d777_o_comando_do_vpk_sem_diferenca_sem_portatil_e_o_msi_so_quando_pedido` (M13).
- O empacotar não abre o PowerShell por conta própria →
  `tests/test_windows_peca.py::test_o_empacotar_le_a_assinatura_pela_peca_e_nao_abre_o_powershell` (M14).
- A versão sem o motor publicado não é montada →
  `tests/test_publicar_versao.py::test_d790_sem_o_motor_publicado_nada_e_montado` (M15).
- A pasta pronta de outra versão é recusada →
  `tests/test_publicar_versao.py::test_a_pasta_pronta_de_outra_versao_e_recusada` (M16).
- O PowerShell sem a lista de módulos herdada →
  `tests/test_windows_peca.py::test_o_powershell_nao_herda_os_modulos_do_powershell_7` (M17).
- O script lançado solto apaga sem seguir atalho (D-809) →
  `tests/test_windows_peca.py::test_o_lancado_solto_apaga_a_pasta_de_troca_sem_seguir_atalho` (M18, no código anterior;
  acusa pelo JEITO de apagar: neste Windows o apagar antigo não entrou na junção, `anexos/d809-jeito-antigo.txt`).
- O destino não apaga uma publicação que é atalho (D-809) →
  `tests/test_publicar_versao.py::test_d809_apagar_uma_publicacao_que_e_atalho_nao_apaga_o_outro_lado` (M19).
- **Volta 2** (`anexos/reversao-volta2-resultado.txt`): o apagar do rascunho no GitHub sem a etiqueta (A1), a
  leitura de volta decide se apagou (A1b), o grupo fecha o que o vpk abriu (A2), nada apagado depois de liberar (A4), o
  erro do disco em frase (A5), o sinal de vida fora da pasta (A6), nome repetido não entregue (A7), o motor em
  instalar\ recusado na atualização (A8), a conta de 7 vezes (A9), a etiqueta inteira (A11), e N1, N3, N4, N5, N6,
  N8, N10, N13, N14: todas acusadas pelos testes citados no achado 3 e nos achados acima.
- Sem teste que acuse sozinho (dupla proteção; escrito para quem tenta quebrar): a conferência de que nada ficou vivo
  depois de fechar o grupo (A2b: o fechamento do Windows já fecha tudo; com ele desligado, o A2 acusa); o Ctrl+C que
  fecha o grupo (N10: o fechar-ao-fechar do grupo também cobre; com os dois desligados, acusa); o Setup.exe apagado logo depois do vpk
  (o rascunho inteiro some no fim de qualquer jeito); o corte das conexões no fechar do servidor (o envio também para
  pela marca de fechado).

- **Volta 3** (`anexos/reversao-volta3-resultado.txt`; script em `anexos/reversao-volta3-mutacoes.py.txt`), cada uma
  desligada numa cópia e acusada:
  - só o rascunho apagado (B1, B1b, B1c, B1d) →
    `tests/test_publicar_versao.py::test_volta3_achado1_uma_leitura_atrasada_depois_de_liberar_nunca_apaga_a_versao_liberada`
    e `tests/test_publicar_versao.py::test_volta3_achado1_no_github_a_leitura_atrasada_tambem_nunca_apaga_a_liberada`;
  - a cópia pelo nome provisório (B2) → `tests/test_publicar_versao.py::test_volta3_a_copia_cortada_no_meio_nunca_deixa_o_nome_certo`;
  - a cópia lida de volta (B2b) e a vigia no meio da cópia (B2e) →
    `tests/test_publicar_versao.py::test_volta3_a_copia_conferida_le_de_volta_e_obedece_a_vigia`;
  - a conferência do fim compara o .msi (B2c) →
    `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_da_pasta_de_saida_e_comparado_com_o_do_rascunho`;
  - o .msi pela cópia conferida (B2d) →
    `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_que_nao_termina_de_copiar_nao_fica_com_o_nome_certo`;
  - a peça recusa o que não é programa (B3), pelo começo do arquivo (B3b) →
    `tests/test_windows_peca.py::test_bat_e_cmd_sao_recusados_pelo_rodar_pelo_lancar_e_pelo_grupo`; pela extensão (B3c) →
    `tests/test_windows_peca.py::test_um_lote_que_a_peca_nao_acha_tambem_e_recusado_pela_extensao`;
  - o programa nasce parado (B4) → `tests/test_windows_peca.py::test_o_programa_nasce_parado_e_so_roda_dentro_do_grupo`;
  - "conferido" só fechando o grupo (B4b) e só com 0 vivos lidos (B4c), "não deu para conferir" sem leitura (B9) →
    `tests/test_windows_peca.py::test_fechar_tudo_so_diz_conferido_quando_o_windows_diz_que_nenhum_ficou` (B4b também por
    `tests/test_publicar_versao.py::test_volta3_achado4_a_vigia_fecha_o_filho_do_vpk_antes_de_soltar_o_grupo`);
  - a primeira pasta de troca apagada (B9b) →
    `tests/test_windows_peca.py::test_o_lancado_solto_apaga_a_primeira_pasta_se_a_segunda_nao_nasce`;
  - o rascunho apagado quando o liberar falha (B5) →
    `test_volta3_achado5_o_liberar_que_falha_e_continua_rascunho_apaga_o_rascunho` (saiu na volta 4: a D-816 tirou o que ele cobrava);
  - o motor que mudou (B6) → `tests/test_publicar_versao.py::test_volta3_achado6_o_motor_trocado_durante_a_publicacao_impede_liberar`;
  - o motor baixado na conta (B7) e na vigia (B7b) →
    `tests/test_publicar_versao.py::test_volta3_achado7_o_motor_baixado_entra_na_conta_e_na_vigia`; o gh na vigia (B7c) →
    `tests/test_publicar_versao.py::test_volta3_achado7_o_gh_que_baixa_e_fechado_pela_vigia`; o nome do motor num lugar
    só (B7d) → `tests/test_publicar_versao.py::test_volta3_achado7_o_nome_do_motor_so_em_versao_py`;
  - a janela diz do nome repetido (B8) →
    `tests/test_publicar_servidor.py::test_achado8_o_nome_repetido_aparece_na_janela_como_repetido_e_nao_como_inexistente`.
  - Sem teste que acuse sozinho (dupla proteção): a conferência IsProcessInJob depois de pôr no grupo (o
    AssignProcessToJobObject que deu certo já põe; sem ele, o B4 acusa). Na primeira passada, a B1d e a B2 não foram
    acusadas: a B1d porque o teste só cobrava "NÃO apaguei" (passou a cobrar "ficou liberada em"); a B2 porque o apagar
    do pedaço também a cobre na falha comum (ganhou o teste da cópia cortada no meio, sem nada rodando depois).

- **Volta 4** (`anexos/reversao-volta4-resultado.txt`; script em `anexos/reversao-volta4-mutacoes.py.txt`): cada uma
  desligada numa cópia (git archive, fora do projeto) e acusada pelo teste dela, 24 de 24:
  - depois do pedido de liberar, nada é apagado (V1) →
    `tests/test_publicar_versao.py::test_d816_depois_do_pedido_de_liberar_nada_e_apagado_com_qualquer_atraso` e
    `tests/test_publicar_versao.py::test_d816_o_liberar_que_falha_e_fica_rascunho_nao_apaga_e_diz_o_comando`;
  - "não achei" logo depois de criar não é "sumiu" (V2) e o criar no caminho de erro (V3) →
    `tests/test_publicar_versao.py::test_volta4_achado4_nao_achei_logo_depois_de_criar_nao_e_apagado`;
  - a frase diz se pediu: a leitura de depois falha (V4), a de antes falha (V5) →
    `tests/test_publicar_versao.py::test_volta4_achado3_a_frase_diz_se_pediu_para_apagar`; o pedido sem resposta (V6) →
    `tests/test_publicar_versao.py::test_volta4_achado3_o_pedido_de_apagar_sem_resposta_diz_que_pediu`; liberada no
    meio do apagar (V7) → `tests/test_publicar_versao.py::test_volta4_achado3_liberada_no_meio_do_apagar_nunca_vira_apagada`;
  - o nome como o Windows o completa (V8) →
    `tests/test_windows_peca.py::test_volta4_o_nome_com_ponto_no_fim_e_lido_como_o_windows_completa`;
  - a frase do programa que não deixa ler (V9) →
    `tests/test_windows_peca.py::test_volta4_o_programa_que_nao_deixa_ler_e_recusado_com_frase_propria`;
  - a segunda olhada depois do PATH (V10, achado 10) →
    `tests/test_windows_peca.py::test_volta4_a_segunda_olhada_depois_do_path_recusa_o_lote_achado_pelo_pathext`;
  - a soma no rascunho (V11), pela vigia (V12), na conta da versão (V13) e do motor (V14), com o rascunho dado pelo
    publicar (V15) → `tests/test_publicar_versao.py::test_volta4_achado7_sem_a_soma_pronta_o_download_vai_ao_rascunho_pela_vigia`,
    `tests/test_publicar_versao.py::test_volta4_achado7_a_conta_do_espaco_soma_o_que_a_soma_pode_baixar` e
    `tests/test_publicar_versao.py::test_volta4_achado7_no_publicar_sem_a_soma_pronta_tudo_e_baixado_no_rascunho`;
  - o gh pelo laço único (V16), o laço fecha o grupo inteiro (V17), o limite de tempo (V18), o Ctrl+C fecha o grupo
    (V19; V19b com o fechar-ao-fechar do grupo também desligado) →
    `tests/test_publicar_versao.py::test_volta4_achado8_o_gh_roda_pelo_laco_unico_da_peca_e_fecha_o_que_abriu` e
    `tests/test_windows_peca.py::test_volta4_rodar_em_grupo_e_o_laco_unico_com_a_saida_a_vigia_e_o_tempo`;
  - gravar no disco na cópia (V20), no motor comprimido (V21), na gravação da peça (V22), e com o os.fsync de verdade
    (V23) → `tests/test_publicar_versao.py::test_volta4_achado11_a_copia_e_o_motor_gravam_no_disco_antes_de_conferir_e_trocar`
    e `tests/test_windows_peca.py::test_volta4_a_peca_manda_gravar_no_disco_antes_de_trocar_o_nome`.
  - **Na primeira passada, duas não foram acusadas** (V17 e V19): quem fechava o filho era o fechar-ao-fechar do fim do
    `with` (o grupo é solto e o Windows fecha o que ficou). Os dois testes passaram a segurar o soltar do grupo (como o
    da volta 3, achado 4), e as duas foram acusadas na segunda passada. O `test_n10_ctrl_c_fecha_o_vpk_e_o_que_ele_abriu`
    sozinho continua não acusando a V19 (dupla proteção, já escrito na volta 2). Na primeira passada também apareceu
    um defeito do teste: o filho do gh de prova rodava para sempre quando escapava (a V16 levou 10 minutos, presa no
    cano da saída); passou a sair sozinho em 30 s.
- **Volta 4, limite conhecido (achado 5, não é proteção):** a recusa da peça é pela pasta do Windows e pela lista de
  nomes; uma cópia de um programa do Windows fora da pasta, com outro nome, passa (Ressalvas).

- **Volta 5** (`anexos/reversao-volta5-resultado.txt`; script em `anexos/reversao-volta5-mutacoes.py.txt`), 10 de
  10 acusadas:
  - cada uma das três frases com o comando à mão (W1a, W1b, W1c) →
    `tests/test_publicar_versao.py::test_volta5_achado1_as_frases_de_ja_existe_dao_o_comando_do_destino`;
  - qualquer "sem resposta" do apagar vira "pedi" (W2) →
    `tests/test_publicar_versao.py::test_volta5_achado2_a_leitura_sem_resposta_antes_do_pedido_nao_vira_pedi_para_apagar`;
  - o pedido de apagar sem resposta não marcado (W2b) e o gh fechado por tempo virando Parou comum (W3a, achado 3 a) →
    `tests/test_publicar_versao.py::test_volta5_achado3a_o_gh_de_verdade_fechado_por_tempo_no_apagar_diz_que_pediu`;
  - sem o `except PublicacaoLiberada: raise` (W3b, achado 3 b) →
    `tests/test_publicar_versao.py::test_volta5_achado3b_liberada_antes_do_pedido_no_github_continua_publicacao_liberada`;
  - o gh que nem abriu contando como pedido (W4) →
    `tests/test_publicar_versao.py::test_volta5_achado4_o_gh_que_nem_abre_no_liberar_nao_conta_como_pedido`; o _gh
    que não abriu levantando Parou comum (W4b) →
    `tests/test_publicar_versao.py::test_volta5_achado4_so_o_gh_que_nao_abriu_de_verdade_e_nada_saiu`;
  - sem a recusa do fluxo escondido (W5) →
    `tests/test_windows_peca.py::test_volta5_o_programa_num_fluxo_escondido_de_outro_arquivo_e_recusado`.
  - As duas mutações do relatório 4 que não pedem conserto (A6: o laço não junta a saída depois de fechar; A10: o
    destino não volta ao estado de antes no fim do publicar) são arrumação: hoje ninguém usa essa saída nem reaproveita
    o destino (observação 8).

- **Volta 6** (`anexos/reversao-volta6-resultado.txt`; script em `anexos/reversao-volta6-mutacoes.py.txt`), 10 de 10
  acusadas:
  - a montagem não põe o Visual C++ (Y1, o defeito da prova) →
    `tests/test_publicar_versao.py::test_volta6_a_versao_montada_do_zero_leva_o_visual_c_e_e_publicada`;
  - sem a conferência antes do vpk em `construir_pacote_do_velopack` (Y2), a pasta portátil com o Visual C++ (Y5), a
    conferência sem cobrar o Visual C++ (Y6) → `tests/test_publicar_versao.py::test_volta6_a_mesma_conferencia_da_pasta_em_todos_os_caminhos`;
  - a ficha gravada antes do Visual C++ (Y3) e a cópia pela metade ignorada (Y4) →
    `tests/test_publicar_versao.py::test_volta6_a_copia_do_visual_c_pela_metade_nao_deixa_a_ficha`;
  - `NadaSaiu` como caso de `SemResposta` (Y7, a X3 de quem quebrou) →
    `tests/test_publicar_versao.py::test_volta6_achado1_o_apagar_em_que_o_gh_nem_abre_diz_nao_apaguei`;
  - o comando do motor sem o destino (Y8) e a frase escrita à mão de novo (Y9) →
    `tests/test_publicar_versao.py::test_volta6_achado2_a_frase_do_motor_que_falta_da_o_comando_do_destino`;
  - o caminho de rede com a frase antiga (Y10) →
    `tests/test_windows_peca.py::test_volta6_achado3_o_caminho_de_rede_e_recusado_com_a_frase_propria`.

- **Volta 7** (`anexos/reversao-volta7-resultado.txt`; script em `anexos/reversao-volta7-mutacoes.py.txt`; mutações
  próprias, R1 a R12, diferentes das Y da volta 6 e das Z de quem quebrou), numa cópia de `25c514ad`, rodando o arquivo
  de teste inteiro: **11 de 12 acusadas**.
  - a conferência da pasta sem ler a assinatura (R1), sem cobrar o arquivo da versão (R2), sem comparar a versão (R3),
    o Tesseract só pela pasta existir (R4), aceitando arquivo vazio (R5) →
    `tests/test_publicar_versao.py::test_d818_a_pasta_ja_montada_e_conferida_igual_a_montada_do_zero`;
  - o pacote sem cobrar o Tesseract (R6) ou a versão do Visual C++ (R7) →
    `tests/test_publicar_versao.py::test_volta7_achado3_o_pacote_sem_uma_peca_e_recusado_depois_do_vpk` (e o montado do
    zero, R6);
  - a ordem antiga no empacotar chamado sozinho (R8) →
    `tests/test_publicar_versao.py::test_volta7_achado4_o_empacotar_chamado_sozinho_recusa_antes_de_mexer_na_pasta`;
  - a régua única ignorando `vc_redist_confere` (R9) e a montagem com outra régua (R10) →
    `tests/test_empacotar.py::test_d818_a_montagem_e_a_pasta_usam_a_mesma_regua_do_visual_c`;
  - o `--pasta` sem aspas (R11) → `tests/test_publicar_versao.py::test_volta7_achado5_a_pasta_das_provas_com_espaco_no_nome`.
  - **Não acusada: R12** (a conferência deixa de cobrar o Visual C++ só na saída do instalador, a segunda passada).
    É dupla proteção: a mesma pasta já passou pela conferência como atualização (cedo, no publicar, e antes do primeiro
    vpk), e entre as duas passadas só o arquivo do motor muda. Nenhum teste a acusa sozinha; fica escrito aqui.

- **Volta 8** (`anexos/reversao-volta8-resultado.txt`; script em `anexos/reversao-volta8-mutacoes.py.txt`), numa cópia de
  `b2863630` (git archive no rascunho da sessão, `v8\novo`), uma por vez, o arquivo devolvido ao original depois de cada
  uma (conferido byte a byte), o arquivo de testes do publicar inteiro. Diferentes das R, Y, Z e W das voltas
  anteriores; cada uma tira uma condição de dentro da proteção, não só a desliga inteira (achado 4 do relatório 7):
  - "foi apagada" só quando havia e sumiu: U1 (o `--apagar` volta à frase própria), U2 (a frase ignora se havia), U3
    (a leitura de antes que não acha nada vira "havia") →
    `tests/test_publicar_versao.py::test_volta8_defeito2_o_apagar_diz_que_apagou_quando_apagou`.
  - O caminho de erro usa a mesma frase: U4 (frase própria no caminho de erro) →
    `tests/test_publicar_versao.py::test_volta8_defeito2_o_caminho_de_erro_usa_a_mesma_frase_do_apagar`.
  - A leitura única nos dois lados: U5 (o programa instalado lê por conta própria) e U6 (a conferência do publicar lê
    por conta própria) → `tests/test_publicar_versao.py::test_volta8_baixo6_o_publicar_e_o_programa_instalado_usam_a_mesma_leitura`.
  - A leitura tira as pontas: U7 → `tests/test_publicar_versao.py::test_volta8_baixo6_a_versao_do_visual_c_e_lida_por_uma_funcao_so`.
  - A régua olha quem assinou: U8 (só a condição do assinante) →
    `tests/test_publicar_versao.py::test_volta8_baixo1b_um_programa_da_microsoft_que_nao_e_o_visual_c_e_recusado_pela_mesma_regua`.
  - A régua não aceita a leitura que falhou: U9 (só a condição do estado) →
    `tests/test_publicar_versao.py::test_volta8_baixo1a_a_leitura_da_assinatura_que_falha_nunca_vira_passou`.
  - A versão comparada inteira: U10 (só os dois primeiros pedaços) →
    `tests/test_publicar_versao.py::test_volta8_baixo2_o_arquivo_da_versao_vazio_ou_pela_metade_e_recusado`.
  - As licenças do Tesseract: U11 (a conferência da pasta deixa de cobrar só a AUTHORS) e U12 (o pacote deixa de cobrar as licenças) →
    `tests/test_publicar_versao.py::test_volta8_baixo3_sem_a_licenca_do_tesseract_a_pasta_e_o_pacote_sao_recusados`.
  **12 de 12 acusadas** (a U11 na segunda forma: a primeira, tirar a AUTHORS da própria lista única, quebrava o preparo de todos os testes, porque a montagem casa a lista com as origens pelo zip estrito, e não provava o teste da licença). A cópia sem mutação: 121 de 121 passam.

## De onde vem cada dado da conferência

- **Se a versão ou o motor já existem no destino:** lido do destino (a pasta; ou o GitHub pelo gh), nunca de uma
  anotação do publicar.
- **A soma de cada arquivo publicado:** lida do destino (a pasta: somada do arquivo lá; o GitHub: a soma que o próprio
  GitHub calcula, ou o arquivo baixado e somado), comparada com a soma do arquivo do rascunho.
- **A assinatura:** o texto baixado do destino, conferido com a chave pública que vai dentro do programa (nos testes, a
  chave de teste) e com a soma lida do destino. A chave privada não confere nada (ela assina).
- **O motor que a versão pede:** a assinatura do motor baixada do destino e a soma do arquivo do motor lida do destino;
  o motor-exigido.json é escrito a partir disso, nunca de um arquivo local.
- **O índice das versões:** baixado do destino, conferido contra a soma do pacote lida do destino.
- **O espaço livre:** lido do Windows na hora (`shutil.disk_usage`), a cada 2 s durante o vpk.
- **A versão da pasta pronta:** a ficha da versão dentro da pasta. **Este dado o conferido pode trocar** (quem monta a
  pasta escreve a ficha): ela pega o engano (a pasta de outra versão), não serve de prova; a prova é a leitura de volta
  do que foi publicado e a prova à vista.
- **O motor inteiro:** a ficha motor.json dentro do motor. **Também escrita por quem monta**: a conferência forte é a
  soma assinada do arquivo do motor, lida do destino.
- **O resultado do vpk:** os arquivos que ele deixa na pasta de saída, abertos e conferidos (o pacote aberto como zip),
  não só o código de saída dele.
- **O servidor:** as subpastas liberadas da pasta, lidas a cada pedido.

- **Volta 3:** o .msi feito agora: o nome, o tamanho e a soma lidos do arquivo no rascunho, logo depois de o vpk
  gravá-lo e antes de o rascunho ser apagado; o .msi da pasta de saída: lido do arquivo de lá (tamanho e soma). Quem
  escreve os dois é o próprio publicar; a prova de que o instalador está certo continua sendo a leitura de volta da
  publicação (a soma lida do destino) e a prova à vista.
- **Volta 3:** se o programa entrou no grupo: perguntado ao Windows (IsProcessInJob); quantos estão vivos no grupo:
  perguntado ao Windows (QueryInformationJobObject); se o arquivo é programa: o começo do arquivo lido do disco e o
  caminho completado pelo Windows (GetFullPathNameW, pelo os.path.abspath).
- **Volta 3:** só o rascunho apagado: a situação lida do destino dentro do apagar, antes e depois de pedir (na pasta,
  a subpasta do rascunho é a única tocada).

- **Volta 4, a frase da D-816:** não usa dado nenhum do destino (de propósito: uma leitura atrasada não entra nela).
  O único dado que decide é se o próprio publicar já pediu para liberar (uma variável dele, `pediu_para_liberar`, que
  ninguém de fora troca). Os comandos da frase vêm do destino (`como_conferir`, `comando_de_apagar`), que é o lugar
  que o publicar recebeu na linha de comando.
- **Volta 4, a frase do apagar:** "pedi" ou "não pedi" vem de por onde o apagar passou (antes do pedido, no pedido,
  depois), nunca de uma anotação; "sumiu" vem da leitura do destino depois do pedido; "não achei logo depois de criar"
  vem do próprio caminho de erro (`acabou_de_criar`).
- **Volta 4, a recusa da peça:** o nome vem do Windows (o GetFullPathNameW, pelo `os.path.abspath`); o começo do arquivo,
  lido do disco; "não deu para ler", o erro do Windows ao abrir.
- **Volta 4, a soma sem a soma pronta:** o arquivo baixado do destino para o rascunho e somado ali; o lugar do download
  vem do publicar (`usar_rascunho`), não do destino; a vigia lê o espaço do Windows na hora.
- **Volta 4, o laço único:** se o programa terminou e com que código, do Windows (o processo); se algo ficou vivo, do
  Windows (a leitura do grupo).
- **Volta 4, gravar no disco:** o que o Windows responde ao pedido de gravar (erro vira erro do disco). Não há leitura que
  prove que chegou ao disco (a leitura de volta vem da memória do Windows): isso está escrito em "Ressalvas".

- **Volta 5:** "pedi para apagar" vem de qual pedido saiu e ficou sem resposta: só o pedido de apagar em si
  (`ApagarSemResposta`, levantado pelo destino no pedido); "nada saiu" vem do laço único da peça (`abriu: False`: o
  programa nem começou, lido do que a peça fez); "fluxo escondido" vem do caminho completado pelo Windows (o
  GetFullPathNameW). Os comandos das frases vêm do destino que o publicar recebeu.

- **Volta 6:** "a pasta tem o Visual C++" vem do disco (o arquivo em instalar\ existe); "chegou inteiro" vem do tamanho
  lido do disco, comparado com o do original conferido pela assinatura da Microsoft (`preparar_vc_redist`, que não
  mudou). "Montada inteira" é a ficha da versão, que o próprio empacotar escreve por último: ela pega a pasta que parou
  no meio, mas é um dado que quem monta escreve (não serve de prova; a prova é a conferência do pacote depois do vpk,
  que abre o pacote e procura o Visual C++, e a prova à vista). O comando da frase do motor vem do destino que o
  publicar recebeu.

- **Volta 7:** "é o Visual C++ oficial" vem da assinatura lida pelo Windows no arquivo que está na pasta (não do nome,
  não de uma anotação); a versão vem da mesma leitura e é comparada com o arquivo da versão da pasta (que quem monta
  escreve: por isso a comparação); "tem o Tesseract" vem do disco (cada arquivo da lista existe e não está vazio). O
  conteúdo do Tesseract não é comparado com o original na pasta já montada (não há original; a montagem compara na
  hora de copiar): escrito nas Ressalvas.

- **Volta 8:** "foi apagada" vem de duas leituras do destino feitas pelo próprio apagar (havia antes do pedido; não há
  depois), nunca do código de saída do gh nem de uma anotação; "não existia" vem da leitura de antes (nada foi pedido).
  A versão do Visual C++ do pacote vem do arquivo que está na pasta (disco), lido pela função única, e é comparada com a
  versão que o Windows lê na assinatura do arquivo do Visual C++ (o que o conferido não escreve). O "assinado por outra
  pessoa" dos testes novos vem do Windows de verdade (a cópia do powershell.exe); o "não terminou" vem da peça do
  PowerShell trocada no teste (só a lógica em volta: o que a régua faz com uma leitura que falhou).

## Máquina ou olho

- Máquina: tudo o que está em "Testes" (a lógica, a pasta de verdade como destino, o servidor de verdade, a vigia com
  um processo de verdade, a assinatura digital lida pelo Windows de verdade).
- Olho: nada nesta entrega. A prova à vista (o vpk de verdade no C:, o rascunho no GitHub de verdade, a janela do
  servidor na tela) é da gerente com o Samuel, depois de quem tenta quebrar.

- **Volta 4:** máquina, tudo (os testes; a peça do Windows de verdade: o nome com ponto no fim, o programa trancado, o
  lote pelo PATH, o grupo com o gh de prova, a gravação no disco). Olho: nada. A prova à vista continua com a gerente e o
  Samuel (itens 10 a 12 acrescentados em "A prova de verdade").

- **Volta 6:** máquina, tudo (os testes, a reversão no código antigo, as mutações; a pasta que a prova montou de verdade,
  só lida). Olho: nada. O PyInstaller e o vpk de verdade por este caminho são da prova à vista (itens 13 a 15).

- **Volta 7:** máquina, tudo (os testes; a leitura de verdade da assinatura de um arquivo sem assinatura). Olho: nada.
  A prova à vista: itens 13 a 17 da Volta 7.

- **Volta 8:** máquina, tudo (os testes, a reversão no código antigo, as mutações; a leitura de verdade da assinatura
  da cópia do powershell.exe). Olho: nada. A prova à vista: itens 18 e 19 de "A prova de verdade", Volta 8.

## Ressalvas

- **O vpk de verdade e o GitHub de verdade não rodaram.** Os testes usam um vpk de mentira (escreve os nomes que li no
  código do vpk) e um gh de mentira (responde no formato que li no código do gh). Pode dar diferente na prova: os nomes
  dos arquivos que o vpk 1.2.161 grava (conferidos só na pasta da etapa 5), o "digest" das publicações de rascunho do
  GitHub (se faltar, o publicar baixa o arquivo para somar: mais lento, ainda certo), e o gh achar o rascunho pela
  etiqueta.
- **A conta do espaço é conta, não medida** (volta 2, achado 9, refeita pela leitura do vpk: 4 vezes a pasta na
  atualização, 7 com o .msi, mais 1 GB; na volta 3, mais o motor baixado para o rascunho; fontes no docstring de
  `empacotar.espaco_que_vai_usar`). Corrigido na volta 3 (achado 8: as duas contas daqui se contradiziam). Pela pasta
  de hoje sem o motor (0,78 GB, medida por quem tentou quebrar) e o motor comprimido (uns 0,8 GB, conta, não medido):
  sem o .msi a conta dá uns 4,1 GB (o C: precisa de uns 24 GB livres); com o .msi, uns 13,7 GB (precisa de uns 34 GB
  livres). Hoje o C: tem 48,9 GB livres (medido por quem tentou quebrar). O .msi com o motor nunca foi medido; se a
  conta for alta demais, o publicar recusa com espaço que bastaria (é de propósito, pelo pior caso).
- **A pasta do programa ainda é montada no D:** (o PyInstaller, em dist\EditorImpressao\); no C: ficam o trabalho do
  vpk e o rascunho. Sem o motor, a pasta tem uns 582 arquivos e o vpk lê rápido do D: (estudo). Mudar também a pasta
  para o C: mexeria no Inno; não fiz.
- **O motor que existe hoje não tem a ficha.** Para publicar o motor 1, alguém roda uma vez
  `montar_motor_kraken.py --so-ficha --destino D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken`: abre o
  motor (1 minuto) e grava o motor.json **dentro da pasta de ferramentas do Samuel** (fora do projeto; não apaga nada).
  Não rodei: é coisa da gerente com o "sim" dele.
- **A pasta do publicar com `--pasta` mudou de desenho** (uma subpasta por versão, como o GitHub). O programa de hoje,
  pela fonte de teste da etapa 5, lê uma pasta plana: ele não acha as versões nesse desenho. Nas provas as versões vêm
  pelo servidor (D-773); o programa fala com o servidor no passo 3 (a fonte de teste aponta para o endereço). Até lá, o
  servidor só pode ser provado com um cliente comum (o teste faz isso).
- **A ficha da versão** (versao-do-pacote.json, a versão e o commit) passou a ir também na pasta portátil e no
  instalador do Inno: um arquivo pequeno a mais, sem efeito no programa.
- **Duas peças de conversa com o GitHub:** a do publicar (`DestinoGitHub._gh`) e a do porteiro
  (`regras_dos_agentes/conversa_com_o_github.py`, fora da lista dos meus arquivos). Fazem coisas diferentes (publicar e
  ler rodadas), mas o §11.12, ponto 1, pede uma peça só por conversa: fica para a gerente decidir se junta.
- **Os dois nomes para "onde achar o motor"** (para montar: `empacotar.LUGARES_DO_MOTOR`; onde o programa procura:
  `ocr_kraken.lugares_do_motor`) não foram trocados, porque testes antigos usam os nomes de hoje; ficaram escritos nos
  comentários das duas. O plano pedia nomes diferentes.
- **A versão do protocolo está escrita em dois lugares** (`core/ocr_kraken.py` e `montar_motor_kraken.py`), como antes;
  a ficha usa a do `core/ocr_kraken.py`. Não mexi na do montar (o teste do fim do montar confere as duas).
- **Achado do servidor (consertado):** o http.server deixava dois servidores na mesma porta no Windows (o segundo
  "servia" sem erro). Consertado com a porta exclusiva; o teste falha no jeito de fábrica (mutação M11).
- **A conversa com o GitHub não foi rodada contra o GitHub de verdade, nem como rascunho** (o pedido proíbe sem a
  gerente).
- **Depois de pedir para liberar, nada é apagado** (volta 2, achado 4, decisão técnica da gerente, D-014): se a
  leitura que vem depois falhar, o publicar lê a situação; só se ainda for rascunho, apaga. Se ficou liberada (ou não dá
  para ler), para com "liberada; não deu para reconferir agora" e "NÃO apaguei". **Por quê:** quando o liberar é pedido,
  tudo já foi lido de volta e conferido (a versão está inteira); apagá-la deixaria o número dela livre para outro
  conteúdo, e um programa que a pegou naqueles segundos nunca pegaria a outra, que teria o mesmo número ("um número de
  versão só", peça 8). Isso muda o "nunca pela metade" do plano só neste ponto: a versão inteira fica.
- **O conserto da lista de módulos mexe na peça do passo 1** (todo PowerShell que ela abre passa a nascer sem a lista
  herdada). Os testes do passo 1 continuam passando (`tests/test_windows_peca.py`, `tests/test_windows_janela_de_prova.py`).
  O que a peça faz com licença de administrador (a pergunta do Windows, as tarefas) não foi rodado de novo: a próxima
  prova à vista que usar a peça confere.
- O aviso K14 do formulário ("mexeu em arquivo fora da lista": a lista de exceções) é o item tirado da lista, que o
  pedido mandou.

- **Volta 3, o instante do GitHub:** no GitHub, o apagar do caminho de erro lê a situação logo antes de pedir; se o
  GitHub liberar entre essa leitura e o pedido (o liberar que se perdeu e chega atrasado), a versão liberada seria
  apagada, sem a etiqueta (o pedido de rascunho não leva `--cleanup-tag`). A API do GitHub não tem "apague só se for
  rascunho" (lembrado, não relido nesta volta). Na pasta das provas isso não acontece (só a subpasta do rascunho é
  tocada). O teste cobra a leitura atrasada, não esse instante.
- **Volta 3, a vigia no download do GitHub** olha a cada 2 s e fecha o gh; não foi rodada contra o gh de verdade (o
  teste usa um programa de prova que demoraria 60 s). Na pasta das provas, a vigia olha no começo e a cada 64 MB.
- **Volta 3, a peça abre o programa do grupo parado**, e quem o solta é a foto das linhas do Windows. Rodado no PC
  com o Python; o vpk de verdade não foi aberto assim (é da prova à vista). Se o Windows não deixar soltar, o programa
  é fechado e o publicar para com "não consegui soltar o programa depois de pô-lo no grupo".
- **Volta 3, a cópia conferida lê o arquivo duas vezes** (copia e lê de volta). No envio à pasta das provas (D:) e no
  .msi para a pasta de saída, isso soma alguns segundos por arquivo grande; não medi.
- **Volta 3, o achado 10 (para o passo 3; não é defeito hoje):** `windows.abrir_em_grupo` abre o programa com o console
  de quem chama. Do publicar (um terminal), está certo: a saída do vpk aparece ali. Se o programa do Kaique (que não
  tem console) chamasse o grupo para um programa de console, o Windows abriria uma janela preta nova na tela dele.
  Como evitar sem mexer em mais nada: quando quem chama não tem console, abrir com a bandeira CREATE_NO_WINDOW
  (Microsoft Learn: "The process is a console application that is being run without a console window"; o porteiro só
  barra a bandeira de processo sem console, DETACHED_PROCESS, não esta) e mandar a saída para um arquivo; a decisão de
  quando (um parâmetro de quem chama, ou perguntar ao Windows se há console) fica para o pedido do passo 3. Não mudei.
- **Volta 3, o comentário da peça:** a primeira versão do comentário da recusa do lote citava de memória a correção do
  Rust (BatBadBut); relida a página do Rust, ela não diz isso, e o comentário passou a dizer o que foi rodado no PC
  (`e4263c0a`).
- **Volta 3, uma pasta fora do projeto:** num ensaio rápido criei `C:\Users\fotog\AppData\Local\Temp\tmpqhb16hsh`
  (três .bat e um .exe de lote, de poucos bytes) fora da pasta de rascunho desta conversa. Não apaguei (regra de
  29/09): a gerente decide.

- **Volta 4, um teste antigo saiu (para a gerente conferir):** `test_volta3_achado5_o_liberar_que_falha_e_continua_rascunho_apaga_o_rascunho`
  cobrava que o rascunho é apagado quando o pedido de liberar falha. A D-816 tirou isso ("depois de pedir ao GitHub
  para liberar a versão, o programa nunca apaga nada"; "Na pasta das provas (não no GitHub) vale a mesma regra"). No
  lugar dele ficou uma nota, e o mesmo caso (o mesmo destino de prova, `_DestinoQueNaoLibera`) é cobrado do jeito
  novo, com a prova de que o antigo saiu, em `test_d816_o_liberar_que_falha_e_fica_rascunho_nao_apaga_e_diz_o_comando`.
  Nenhum outro teste antigo mudou no que cobra (o do achado 9 só passou a testar o caminho que está escrito nele).
- **Volta 4, D-816 na prática:** se o pedido de liberar falhar com resposta clara (o GitHub diz "não liberei"), o
  rascunho fica no GitHub até alguém rodar o comando da frase. Ele não aparece para o programa do Kaique (rascunho), mas
  o próximo publicar da mesma versão para dizendo que sobrou um rascunho, como já fazia. É o que a D-816 escolheu.
- **Volta 4, o `--apagar` apaga também uma versão liberada** (é o fim da prova, de propósito). A frase da D-816 diz
  para conferir primeiro e só apagar se for rascunho; se a pessoa rodar o `--apagar` numa versão que ficou liberada, ela
  é apagada. Não mudei (não foi pedido); fica escrito.
- **Volta 4, o instante do GitHub continua, mas só antes do pedido de liberar:** no caminho de erro de antes de
  liberar, se outra pessoa ou outro publicar liberar a mesma versão entre a leitura e o pedido de apagar, o gh apaga a
  publicação que acha pela etiqueta (o gh não confere se é rascunho). Depois do pedido de liberar deste publicar, isso
  não acontece mais (nada é pedido).
- **Volta 4, achado 5, limite conhecido da peça (não consertado, pedido da gerente):** a recusa é pela pasta do
  Windows e pela lista de nomes; uma CÓPIA de um programa do Windows fora da pasta do Windows, com outro nome (quem
  tentou quebrar rodou um `meu-cmd.exe`, cópia do cmd.exe, pelo rodar genérico), passa. Só um código que copia um
  programa do Windows de propósito faz isso. O jeito de pegar (o nome original gravado dentro do programa, ou quem o
  assinou) fica para a gerente decidir.
- **Volta 4, gravar no disco:** o pedido de gravar (o `os.fsync`) não prova que o arquivo chegou ao disco (a leitura de
  volta vem da memória do Windows), e o nome trocado (a pasta) não é gravado à parte. O que muda: quando o nome certo
  aparece, o conteúdo já foi mandado ao disco. Um disco com memória própria que mente para o Windows continua podendo
  perder o fim de uma cópia numa queda de luz. A gravação da peça do passo 1 (o aviso, os scripts, a tarefa, a pasta
  segura) também passou a pedir isso: ela roda também no lado com licença de administrador, que não rodei (a próxima
  prova à vista que usar a peça confere). Alguns segundos a mais por arquivo grande no HD externo, não medidos.
- **Volta 4, o gh no grupo do Windows:** rodado com um gh de prova (um programa de verdade, pelo lançador do pip), não
  com o gh de verdade (o pedido proíbe). O gh de verdade nasce parado e é solto dentro do grupo, como o vpk; se o
  Windows não deixar, o pedido ao GitHub para com a frase da peça ("não consegui falar com o GitHub pelo gh").
- **Volta 4, a conta do espaço com o GitHub** soma o maior arquivo que a soma pode baixar, mesmo que o GitHub dê a soma
  pronta (o publicar só sabe disso depois). É a conta pelo pior caso: pode recusar com espaço que bastaria (uns 0,8 GB
  a mais na conta da versão; o tamanho da pasta do motor a mais no `--motor`).
- **Volta 4, o nome sozinho com ponto no fim, pelo PATH:** rodado no PC com uma cópia do hostname.exe; o nome sozinho
  que o Windows procura na pasta do programa que chama (a do Python) não foi rodado (o `which` não olha lá, como antes).

- **Volta 5, o achado 4 muda um pouco o que a D-816 faz na prática:** se o gh nem abrir no pedido de liberar, o
  rascunho é apagado na hora (antes ficava). É a escolha técnica da gerente, pela própria D-816 ("Antes do pedido de
  liberar, erro no meio continua apagando o rascunho"): nada saiu do PC, então não houve pedido. Só vale para o gh
  que nem começou (não achado, recusado pela peça, fechado ainda parado); qualquer erro depois de o gh abrir continua
  sem apagar nada.
- **Volta 5, o fluxo escondido:** a peça recusa qualquer ":" depois da letra do disco, também o "::$DATA" do próprio
  arquivo (o Windows nem roda esse; recusar na dúvida). O "x.bat::$DATA" continua com a frase do lote (conferido
  antes). Rodado de verdade só no NTFS do PC; outro sistema de arquivos sem fluxos daria "não achei o programa", o que
  também não roda.
- **Volta 5, as observações do relatório 4 (só anotadas, como pedido):** (7) o `--apagar` apaga também uma versão
  liberada (já nas Ressalvas e na Lista de espera; com o achado 1 consertado, o comando da frase vai sempre ao destino
  certo); (8) as mutações A6 e A10 são arrumação, sem efeito hoje ("Cada proteção"); (9) os testes do desinstalar que
  falham no PC (já em "Ideias e bugs").

- **Volta 6, o PyInstaller e o vpk de verdade nunca rodaram por este caminho.** O teste de reversão troca só o
  PyInstaller (escreve o que o de verdade escreve, lido do próprio comando e conferido contra a pasta que a prova montou)
  e as peças de entrada (o Tesseract e o Visual C++ de prova; o de verdade é conferido pela assinatura da Microsoft em
  outros testes). Depois deste conserto, a primeira vez que o vpk de verdade recebe uma pasta montada do zero é na prova
  à vista: pode aparecer o próximo defeito dali para a frente (o vpk de verdade nunca rodou pelo publicar; ver as
  Ressalvas da volta 1). **A única prova honesta do caminho inteiro é a publicação de verdade, na tela do Samuel.**
- **Volta 6, a pasta que a prova de 20/11 montou (797 MB, `dist\EditorImpressao`) não serve com `--pasta-pronta`:** foi
  montada pelo código antigo, sem o Visual C++, e a conferência da pasta de fora continua cobrando (D-727). A próxima
  prova precisa montar de novo (sem `--pasta-pronta`; uns 4 minutos de PyInstaller). Não mexi nela.
- **Volta 6, `preparar_saida` ficou com um argumento que não usa (`pecas`):** o Visual C++ saiu de lá, e o argumento
  ficou porque quem chama o passa pela posição (o publicar, e `tests/test_publicar_motor.py` nas linhas 142 e 147, que
  não posso mudar). Está escrito no texto da função. Tirá-lo pede mudar esse teste antigo.
- **Volta 6, a frase nova do caminho de rede tem as palavras "função própria"** porque é o motivo de verdade (por esse
  caminho, a peça não sabe se é um programa do Windows, e esses têm função própria), e os testes antigos N2 e o do "raiz
  global" (`tests/test_windows_peca.py`, perto das linhas 814 e 930) procuram essas palavras na recusa. Ela não manda
  mais "use a função dela". Nenhum teste antigo mudou; se a gerente achar que a frase devia ser outra, os dois testes
  antigos teriam de mudar junto (pede o "pode" do Samuel, como na D-817).
- **Volta 6, no teste, o Tesseract de prova é "rodado" uma vez** (a montagem pergunta a versão dele): o arquivo não é
  programa, e o Windows recusa na hora (erro 216, sem janela); a montagem segue com a versão "?", como já fazia.
- **Volta 6, a ficha da versão é o sinal de "montada inteira"**, mas é escrita pelo próprio empacotar (não prova nada
  sozinha; "De onde vem cada dado", Volta 6). A prova forte continua sendo a conferência do pacote depois do vpk.
- **Volta 6, as observações 4 a 6 do relatório 5 (não pedidas; não mexi):** (4) o "nada saiu" supõe que o programa
  aberto parado tem uma linha só; medido por quem quebrou (gh e Python, 30 vezes cada, sempre uma linha); só um outro
  programa que ponha uma linha dentro do gh parado criaria o caso; fica escrito aqui. (5) e (6) vão para "Ideias e bugs".

- **Volta 7, os testes do publicar dão o Visual C++ de prova como assinado pela Microsoft** (a preparação `ambiente`,
  pela D-818: sem isso, nenhum arquivo de poucos bytes é da Microsoft, e todos os testes antigos parariam na conferência
  nova). Só os dois conteúdos de prova são reconhecidos; qualquer outro arquivo vai à leitura de verdade do Windows (o
  "Visual C++ falso" do teste novo passa por ela). A leitura de verdade do Visual C++ oficial só roda na prova à vista
  (e no PC, que tem o arquivo; no GitHub ele não existe).
- **Volta 7, a leitura da assinatura agora roda em cada conferência da pasta** (o publicar a faz cedo e de novo antes de
  cada vpk: 2 vezes sem o instalador, 3 com ele). Cada uma abre o PowerShell do Windows pela peça (uns segundos, não
  medido). Escrito também em "Velocidade".
- **Volta 7, o Tesseract da pasta já montada é conferido arquivo por arquivo (existe e não está vazio), não comparado
  com o original** (a pasta já montada não tem de onde comparar; a montagem compara o tamanho na hora de copiar). Uma
  pasta arrumada à mão com um arquivo do Tesseract trocado por outro do mesmo nome passaria. A pasta montada do zero
  passa pelas duas conferências.
- **Volta 7, `pecas` deixou de mudar a conferência do pacote** (`esperados_no_pacote_do_velopack` cobra o Tesseract
  pela lista única, com ou sem peças). O argumento fica (quem chama o passa pela posição; um teste antigo o usa), como o
  de `preparar_saida` na volta 6; e o publicar continua passando `pecas` (sem efeito). Escrito no texto das funções.
- **Volta 7, os testes antigos mudados** (a lista está em "O que já está escolhido e testado aqui", Volta 7): a pasta de
  mentira (`_pasta_pronta`), a preparação (`ambiente`) e o vpk de mentira (uma opção nova, desligada de fábrica).
  Nenhum mudou o que cobra; os 88 antigos passam também no código de `db4b377a` com a pasta nova (anexo da reversão).
- **Volta 7, a prova da D-818 está em `tests/test_publicar_versao.py`**, não em `tests/test_decisoes*.py`: o arquivo das
  decisões não está na lista do pacote. A gerente decide se a copia para lá.
- **Volta 7, as observações do relatório 6 (não pedidas; não mexi):** (6) o "lugar único" de pôr o Visual C++ não é
  cobrado por teste (se `preparar_saida` voltasse a pô-lo, nada acusa; hoje não faz mal, e o texto dela diz que é
  arriscado); (7) a frase do caminho de rede tem "(que tem função própria na peça)" para os testes antigos (já nas
  Ressalvas da volta 6); (8) a saída do teste da montagem mostra "assinatura da Microsoft conferida" para um arquivo de
  prova (só a saída do teste; no uso de verdade, `juntar_pecas` confere antes); (10) a cópia do Visual C++ para a pasta
  só confere o tamanho (agora a conferência da pasta lê a assinatura da cópia, o que também pega uma cópia corrompida do
  mesmo tamanho). A (9) vai para "Ideias e bugs".

- **Volta 8, o defeito 1 não foi feito.** O conserto pela causa pede arquivos fora da lista do pacote (o plano está em
  "A causa, a regra e todos os caminhos", Volta 8, e o pedido à gerente em "Perguntas para o Samuel", Volta 8). Até
  lá, publicar de uma cópia de trabalho continua procurando o motor e o Visual C++ no lugar errado (a prova 6b); da
  pasta principal funciona.
- **Volta 8, o programa instalado lê a versão do Visual C++ pelo jeito do publicar.** Para todo arquivo que o publicar
  aceita, o resultado é o mesmo de hoje (teste do baixo 6). Num arquivo que o publicar recusa, muda um caso: em UTF-16,
  o programa instalado levantava erro ao ler; agora lê um texto trocado, que não é uma versão, e não instala o Visual
  C++ (como já fazia com qualquer texto que não é versão). Esse arquivo nunca chega ao Kaique (o publicar o recusa antes
  do vpk).
- **Volta 8, a cópia do powershell.exe nos testes:** no PC, o Windows diz que a assinatura dela é válida e de
  "CN=Microsoft Windows" (rodado). No Windows do GitHub, o mesmo é dedução (o arquivo existe em todo Windows; a rodada
  do GitHub confere). O teste confere isso antes e para com a leitura na frase se não for assim.
- **Volta 8, o `apagar_publicacao` ficou como um nome a mais** para o contrato antigo (devolve só o aviso), porque os
  testes antigos o chamam (D-605). A regra e as frases moram num lugar só (`apagar_e_conferir`); o nome antigo só
  repassa.
- **Volta 8, as observações do relatório 7 (não pedidas; não mexi):** (7) a régua do Visual C++ recusa o Visual C++ novo
  da Microsoft (14.50, "v14 Redistributable") e aceitaria um oficial mais velho (2015-2019), em "Ideias e bugs"; (8) o
  caminho certo com o Visual C++ oficial lido de verdade não roda em nenhum teste automático, em "Ideias e bugs"; (9) a
  troca da leitura da assinatura na preparação dos testes do publicar vai um pouco além da letra da D-818: a gerente
  decide; (10) a prova da D-818 está em `tests/test_publicar_versao.py`, não em `tests/test_decisoes*.py` (o pacote não
  traz esse arquivo): da gerente; (11) o Tesseract da pasta já montada é conferido pela existência e pelo tamanho, não
  pelo conteúdo (um arquivo de 1 byte passa), como já estava nas ressalvas da volta 7.
- **Volta 8, o achado 4 do relatório 7 (a mesma família de erro em duas voltas seguidas):** é da gerente (o catálogo
  dos erros, F3). Nesta volta, cada mutação minha tira uma condição de dentro de uma proteção (o assinante, o estado
  "erro", um item da lista, um pedaço da versão), não só a desliga inteira ("Cada proteção", Volta 8).

## Velocidade

Não se aplica: nenhum arquivo do processamento das páginas do livro mudou; em `core/ocr_kraken.py` só
entraram a versão do motor, a ficha e a conferência, que o caminho do livro não chama (a segunda opinião do Kraken está
desligada, D-164). A gerente decide se roda o filtro de velocidade do GitHub (D-786; plano-v3, "Regras de todos os
passos"). O tempo de publicar é medido na prova à vista.

- Volta 4: não se aplica, pelo mesmo motivo: nenhum arquivo do processamento das páginas mudou (só o publicar, o
  empacotar e a peça do Windows, que o caminho do livro não usa). A gravação no disco pede alguns segundos a mais por
  arquivo grande ao publicar; o tempo de publicar é medido na prova à vista.

- Volta 6: não se aplica, pelo mesmo motivo (só o empacotar, o publicar e uma frase da peça do Windows; o caminho do
  livro não usa nenhum deles). O publicar montado do zero copia o Visual C++ (uns 25 MB) uma vez, onde antes copiava
  dentro do `preparar_saida`.

- Volta 7: não se aplica ao caminho do livro (só o empacotar e o publicar). O publicar ganha 2 ou 3 leituras da
  assinatura do Visual C++ pelo PowerShell (uns segundos cada, não medido; medido na prova à vista).

- Volta 8: não se aplica ao caminho do livro (só o publicar, o empacotar e a leitura de um arquivo de poucos bytes no
  preparo do programa instalado; nenhuma página passa por aqui). Rodada do filtro de velocidade: nenhuma pedida nesta
  volta (a gerente decide; a última do passo, se houver, fica com ela).

## Ideias e bugs

- Ideia (Lista de espera): juntar as duas peças de conversa com o GitHub (a do publicar e a do porteiro) numa só.
- Ideia (Lista de espera): um comando `--so-o-instalador` que faça o .msi da versão já publicada, sem publicar de novo
  (hoje o .msi sai junto com uma versão nova).
- Ideia (Lista de espera): a versão do protocolo do motor num lugar só (hoje está em `core/ocr_kraken.py`, em
  `montar_motor_kraken.py` e no servidor do motor).
- (Consertado na volta 2, pedido da gerente, achado 6): o lançar solto que dava "saiu sem começar" para um script
  curto. Já não vai para a Lista de bugs.
- Bug (Lista de bugs, 19/11/2026, não impede): o http.server do Python, de fábrica, deixa dois servidores abrirem a mesma
  porta no Windows; outros lugares do projeto que usem o http.server podem ter o mesmo defeito (não procurei fora deste
  passo).

- Bug (Lista de bugs, 20/11/2026, não impede): `DestinoGitHub.soma`, quando o GitHub não dá a soma de um arquivo,
  baixa o arquivo inteiro para a pasta temporária da conta (`%TEMP%`, no C:), fora do rascunho: fora da conta do espaço
  e da vigia (o pacote tem uns 460 MB). Achado lendo o código na volta 3; não é dos achados do relatório 2.
- Ideia (Lista de espera): a cópia do motor para instalar\ (`empacotar.preparar_saida`) pela cópia conferida também.
- Bug (Lista de bugs, 20/11/2026, não impede; instável novo): na rodada 44675872042 do GitHub, primeira tentativa, `tests/test_caixinha_do_dividir_nao_volta.py` saiu com o código 0xC0000409 e "sem saída" (um travamento do Qt); na repetição passou. Não usa nada deste passo.

- **Volta 4.** Bug (Lista de bugs, 20/11/2026, não impede; achado 12 do relatório 3 de quem tentou quebrar, família
  F4): `tests/test_decisoes_desinstalar.py` (25 falham) e `tests/test_decisoes_desinstalar_pasta.py` (5 falham) falham
  no PC do Samuel e passam no GitHub: a proteção do próprio teste (`tests/test_decisoes_desinstalar_pasta.py`, perto da
  linha 96) recusa qualquer "C:\" no comando, e no PC a pasta temporária fica no C: (no GitHub, no D:). Falham igual no
  código da volta 2 e no desta volta; não é deste passo. (Visto por quem tentou quebrar; não rodei de novo.)
- Ideia (Lista de espera, volta 4): `montar_motor_kraken.py` também grava num nome provisório e troca
  (`gravar_ficha_do_motor` e a montagem); passar a usar `windows.gravar_no_disco` (fora da lista de arquivos desta volta).
- Ideia (Lista de espera, volta 4): o `--apagar` perguntar antes de apagar uma versão LIBERADA (hoje apaga qualquer uma,
  de propósito, para o fim da prova).
- Ideia (Lista de espera, volta 4): pegar a cópia de um programa do Windows fora da pasta do Windows (achado 5) pelo nome
  original gravado dentro do programa ou por quem o assinou.

- Ideia (Lista de espera, volta 5, achado 6 do relatório 4): a ficha do motor (`montar_motor_kraken.py`), o PDF de
  saída (`core/pipeline.py`) e os projetos (`projetos.py`) também gravam num nome provisório e trocam, sem pedir ao
  Windows para gravar no disco; passarem a usar `windows.gravar_no_disco` (não mexi: fora deste passo e do pedido).

- **Volta 6, o mesmo cuidado em volta (item 3 do pedido): onde a conferência só passava porque o teste usa algo mais
  pronto que o de verdade.**
  - *O Visual C++ em instalar\* (o defeito da prova): consertado.
  - *O Tesseract dentro do pacote:* todos os testes do publicar usavam a pasta pronta, sem as peças (`pecas=None`), e a
    conferência do pacote então nem procurava o Tesseract. O caminho com as peças (o de verdade, montado do zero) nunca
    tinha sido percorrido. Não era defeito (passa); agora o teste novo o percorre.
  - *O vpk de mentira aceita qualquer argumento* e nunca recusa o que o de verdade pode recusar (o `--icon`, o
    `--mainExe`, a pasta). Só a prova à vista mostra. Não é o mesmo defeito; fica como está.
  - *O motor de mentira já vem com a ficha;* o de verdade precisa do `montar_motor_kraken.py --so-ficha` (a gerente já
    rodou antes da prova: o motor 1 foi publicado e conferido no registro de 20/11). Não é o mesmo defeito.
  - *O espaço livre é trocado por 500 GB nos testes;* a conta de verdade só na prova (já nas Ressalvas da volta 1).
- **Bug (Lista de bugs, 20/11/2026, não impede; achado lateral da prova à vista):** a procura das peças, rodando numa
  cópia (`.claude\worktrees\<cópia>`), olha um lugar errado. `empacotar.DOWNLOADS` é
  `RAIZ.parent / "EditorImpressao-arquivos" / "ferramentas" / "downloads"`: no projeto, `RAIZ.parent` é `D:\programas`
  (o lugar certo, `D:\programas\EditorImpressao-arquivos\ferramentas\downloads`); numa cópia, é
  `D:\programas\EditorImpressao\.claude\worktrees`, e o programa procura em
  `D:\programas\EditorImpressao\.claude\worktrees\EditorImpressao-arquivos\ferramentas\downloads`. Na prova, achou lá um
  `vc_redist.x64.exe` (pasta com data de 19/11, 15:44; o arquivo é igual byte a byte ao do lugar certo: a mesma soma
  SHA-256 `cc0ff0eb...b713b`, conferida só lendo). **Se essa pasta não existisse:** `preparar_vc_redist` (com
  `baixar=True`, o de fábrica) criaria a pasta e baixaria o Visual C++ da internet (aka.ms) para ela, conferindo a
  assinatura; sem internet, a montagem pararia antes do PyInstaller ("não consegui baixar o Visual C++"). Ou seja: numa
  cópia, cada montagem pode baixar de novo e deixar pastas soltas dentro de `.claude\worktrees` (provável origem desta,
  deduzido, não conferido), e o Visual C++ baixado pode ser de outra versão que o do lugar certo (o link da Microsoft
  aponta sempre para o mais novo). O mesmo jeito (`RAIZ.parent`) está em `empacotar.LUGARES_DO_MOTOR`,
  `core/ocr_kraken.lugares_do_motor` (o defeito antigo nº 330), `montar_motor_kraken.PASTA_FERRAMENTAS` e
  `compilar_detector_gravura.PASTA_FERRAMENTAS_PADRAO`. Pede um lugar só para "onde fica a pasta de ferramentas", que
  saiba subir de uma cópia até o projeto. Não consertei nem apaguei nada (o pedido).
- **Bug (Lista de bugs, 20/11/2026, não impede):** o `construir_pasta` escreve na pasta o "COMO USAR.txt" da versão
  portátil ("Não precisa instalar nada. De dois cliques em EditorImpressao.exe...") também na atualização e no
  instalador do Velopack; o arquivo vai para dentro do programa instalado do Kaique, com um texto que não vale para ele.
  Visto na pasta que a prova montou. Não mexi.
- Ideia (Lista de espera, observação 5 do relatório 5): uma linha no texto de `DestinoGitHub.liberar` dizendo que ele
  faz um pedido só ao gh (a regra do "o gh nem abriu não é pedido" depende disso), e, se a gerente quiser, um teste que
  confira isso.
- Ideia (Lista de espera, observação 6 do relatório 5): o teste do fluxo escondido ganhar também o fluxo de uma pasta
  (`pastinha:programa.exe`, que o Windows roda e a regra já recusa).

- **Volta 7.** Ideia (Lista de espera, observação 9 do relatório 6): a ficha da versão guarda o commit de que a pasta
  saiu, e ninguém o lê; uma pasta feita com código antigo passa como desta versão. Comparar o commit com o atual
  mudaria o uso normal (montar e depois fazer um commit só de documento); fica como ideia.
- Ideia (Lista de espera, volta 7): tirar o `pecas` que não muda mais nada no caminho do Velopack (`preparar_saida`,
  `esperados_no_pacote_do_velopack`, `conferir_pacote_do_velopack`, o publicar), mudando junto os dois testes antigos
  que o passam pela posição (pede o "pode" do Samuel).
- Ideia (Lista de espera, observação 6 do relatório 6): um teste que acuse se `preparar_saida` voltar a pôr o Visual
  C++ (o lugar único de pô-lo é a montagem).
- Bug (Lista de bugs, 20/11/2026, não impede; visto nesta volta): `tests/test_decisoes_preparo_d749.py`, 3 casos de
  `test_d749_o_passo_anota_como_o_preparo_terminou`, falham no PC ("tudo na pasta de mentira": o comando tem "C:\"),
  igual no código de `db4b377a`. Parece o mesmo caso dos testes do desinstalar (a pasta temporária do PC fica no C:; no
  GitHub, no D:), não conferido a fundo. Não é deste trabalho.

- **Volta 8, bug (20/11/2026, não impede esta volta; é parte do defeito 1):** a pasta errada de 19/11
  (`D:\programas\EditorImpressao\.claude\worktrees\EditorImpressao-arquivos\ferramentas\downloads\vc_redist.x64.exe`,
  25.635.768 bytes, 15h44) faz hoje o `compilar_st_ferramentas.py`, rodado de uma cópia em `.claude\worktrees`, achar
  essa pasta (ele sobe as pastas e fica com a primeira `EditorImpressao-arquivos\ferramentas` que existe): sem o Qt e o
  Boost lá, a compilação pararia ou baixaria tudo para o lugar errado. Lido no código
  (`compilar_st_ferramentas.py`, função `pasta_de_ferramentas_padrao`), não rodado. A pasta não é minha: só a gerente
  decide sobre ela, com o Samuel.
- **Volta 8, bug do mesmo tipo, fora deste passo (não impede):** `rodada_gravura_1_2.py` acha o acervo pela pasta de
  cima do código (`RAIZ.parent`), e numa cópia de trabalho não o acha. Lido, não rodado. Para a Lista de bugs.
- **Volta 8, ideia (Lista de espera, observação 7 do relatório 7):** decidir qual Visual C++ o publicar aceita: hoje a
  régua pede o nome "2015-20xx" (recusa o 14.50 novo, "v14 Redistributable") e qualquer versão que começa com "14."
  (aceitaria um 14.2x mais velho que o do notebook). O endereço permanente que o programa usa ainda leva ao 14.44.
- **Volta 8, ideia (Lista de espera, observação 8 do relatório 7):** um teste que lê de verdade o Visual C++ oficial da
  pasta de downloads do Samuel quando ele existe (o PC) e diz que pulou quando não existe (o GitHub).

## Perguntas para o Samuel

Nenhuma nesta entrega. Procurei no Livro antes: a D-773, a D-776, a D-777, a D-788, a D-789, a D-790 e a D-795 respondem
tudo o que este passo precisou. O que depende de um "sim" dele é uma licença, não uma escolha (gravar a ficha na pasta
de ferramentas dele, em "Ressalvas"): a gerente pergunta, se achar preciso.

**Volta 4:** nenhuma pergunta nova. Procurei no pedido e no Livro antes: a D-816 responde o achado 1 (inclusive o caso
do liberar que falha e fica rascunho, que a volta 3 apagava: "Na pasta das provas (não no GitHub) vale a mesma regra"),
e a gerente decidiu os outros (os achados 5 e 12 ficam escritos). O que fica para a gerente olhar está em "Ressalvas":
o teste antigo do achado 5 da volta 3, que saiu porque cobrava o que a D-816 tirou.

**Volta 6:** nenhuma pergunta. O Samuel autorizou o conserto do defeito da prova e dos três baixos ("pode concertar");
a D-727 diz onde o Visual C++ fica. O que fica para a gerente olhar está em "Ressalvas", Volta 6 (a frase do caminho de
rede com as palavras que os testes antigos procuram; o argumento que `preparar_saida` não usa mais).

**Volta 7:** nenhuma pergunta. A D-818 respondeu o achado 1 e autorizou mudar a pasta de mentira dos testes antigos.
Nenhum teste antigo precisou mudar o que cobra (só a pasta de mentira, a preparação que a faz "assinada" e uma opção
desligada do vpk de mentira; lista em "O que já está escolhido e testado aqui", Volta 7).

**Volta 8: nenhuma pergunta para o Samuel.** Para a **gerente** (não é pergunta para ele; é o pacote):

*O defeito 1 parou antes de mexer: o conserto pela causa pede arquivos fora da lista.* O que eu peço para a lista:
1. `regras_dos_agentes/conversa_com_o_git.py`: uma função nova, "a pasta principal desta cópia" (pergunta ao git
   `rev-parse --path-format=absolute --git-common-dir` e devolve a pasta de cima, quando ela se chama `.git`; nada se o
   repositório não tem pasta principal). E o git aberto sem janela de console (hoje a peça abre o git sem esse cuidado;
   rodando dentro da janela do programa pelas fontes, piscaria uma janela preta na tela do Samuel).
2. Um lugar novo para a regra "onde fica a pasta das ferramentas do Samuel", importável pelo programa e pelos scripts:
   sugiro um módulo novo em `core/` (ex.: `core/pasta_das_ferramentas.py`); a outra saída é pôr em `core/ocr_kraken.py`
   (está na lista), mas lá ficaria a regra do Qt e do Boost do ScanTailor, que não é do Kraken.
3. `compilar_st_ferramentas.py`: a terceira conta (sobe as pastas; hoje acha a pasta errada) passa a usar a regra única.
4. Um teste novo (sugiro um arquivo novo test_pasta_das_ferramentas.py em tests, ou um nome que caiba no padrão test_publicar_ da lista) e,
   para montar a cópia de trabalho de prova com o git de verdade, uma ajuda nova em `regras_dos_agentes/repositorio_de_prova.py`
   (criar uma cópia de trabalho, `git worktree add`).
O que acontece em cada caso, pelo plano: o programa do Kaique (empacotado) nunca pergunta ao git (acha o motor ao lado
dele, como hoje; e a peça do git fica fora do pacote dele, com o `--exclude-module` do empacotar); um computador sem git,
ou uma cópia sem repositório (feita com `git archive`), cai na conta de hoje (a pasta de cima do código), que é a certa
na pasta principal; a pasta das ferramentas que não existe não é criada (só a `downloads\` dentro de uma que existe).
Se a gerente preferir só o que está na lista, a saída seria ler o `.git` da cópia à mão (o formato está na
documentação do git), fora da peça do git: seria uma segunda conversa com o git, e o `compilar_st_ferramentas.py`
ficaria com a conta dele; não recomendo.

## Commit

2e906e94 (o último commit de código e testes da volta 3, com três docstrings de um teste; depois dele só este formulário muda).

Volta 4: 595cc293 (o último commit de código e testes da volta 4: os textos da peça e da vigia; depois dele só este formulário muda).

Volta 5: 35ec0c27 (o último commit de código e testes da volta 5; depois dele só a pasta deste relatório muda).

Volta 6: 3abf9acf (o último commit de código e testes da volta 6; depois dele só a pasta deste relatório muda).

Volta 7: 25c514ad (o último commit de código e testes da volta 7; depois dele só a pasta deste relatório muda).

Volta 8: b2863630 (o último commit de código e testes da volta 8; depois dele só a pasta deste relatório muda).

## O que o agente que tentou quebrar achou

**Volta 1** (`quem-quebrou/relatorio-1.md`, commit `a58f181b`). Destino de cada achado (volta 2 deste agente; código em
`17cd8635` e `85781a08`; reversão em `anexos/reversao-volta2-resultado.txt`):
1. **O apagar de um rascunho no GitHub dizia "não deixou apagar" tendo apagado:** consertado. Lido o `delete.go` do gh
   (apaga a publicação e depois a etiqueta, que num rascunho não existe, e sai com esse erro): rascunho sem
   `--cleanup-tag`, liberada com; quem decide é a leitura de volta. O gh de mentira imita o de verdade, com a fonte.
   Testes: `tests/test_publicar_versao.py::test_achado1_apagar_um_rascunho_no_github_le_de_volta_e_nao_acusa_erro_falso`,
   `tests/test_publicar_versao.py::test_achado1_erro_antes_de_liberar_no_github_apaga_e_diz_que_apagou` e
   `tests/test_publicar_versao.py::test_achado1_quem_decide_se_apagou_e_a_leitura_de_volta`.
2. **A vigia fechava só o vpk:** consertado na peça do Windows, num lugar só (`windows.abrir_em_grupo`, um grupo do
   Windows que fecha tudo junto e confere que nada ficou vivo); `empacotar.rodar_vpk` o usa. Testes de verdade, num
   processo que abre outro: `tests/test_windows_peca.py::test_fechar_o_programa_em_grupo_fecha_tambem_o_que_ele_abriu` e
   `tests/test_publicar_versao.py::test_achado2_a_vigia_fecha_o_vpk_e_o_que_ele_abriu`.
3. **Nove proteções sem teste:** cada uma ganhou o seu (N1, N3, N4, N14:
   `tests/test_publicar_versao.py::test_n1_n3_n4_n14_cada_leitura_de_volta_errada_impede_liberar`; N5:
   `tests/test_publicar_versao.py::test_n5_o_apagar_que_nao_apaga_e_acusado`; N6:
   `tests/test_publicar_versao.py::test_n6_a_conferencia_do_fim_acusa_o_setup_exe`; N8:
   `tests/test_publicar_versao.py::test_n8_o_msi_nao_fica_na_pasta_de_saida_se_a_versao_nao_saiu`; N10:
   `tests/test_publicar_versao.py::test_n10_ctrl_c_fecha_o_vpk_e_o_que_ele_abriu`; N13:
   `tests/test_publicar_servidor.py::test_n13_o_servidor_nao_serve_por_uma_juncao`). Todos acusam com a proteção
   desligada; o N10 só com o fechar-ao-fechar do grupo desligado junto (é dupla proteção agora). Corrigida a afirmação de
   que o `test_d53` provava o N4.
4. **Apagar uma versão já liberada quando a leitura depois falha:** decisão técnica da gerente (D-014): não apaga; diz
   "liberada; não deu para reconferir agora". Porquê em "Ressalvas". Teste:
   `tests/test_publicar_versao.py::test_achado4_depois_de_liberar_a_leitura_que_falha_nao_apaga_a_versao`.
5. **Erro do disco cru:** consertado (frase em português). Teste: `tests/test_publicar_versao.py::test_achado5_erro_do_disco_vira_frase`.
6. **O lançar solto "saiu sem começar":** consertado (o sinal de vida numa pasta à parte). Teste repetido 20 vezes:
   `tests/test_windows_peca.py::test_o_lancado_solto_curto_nunca_vira_saiu_sem_comecar` (no código anterior: 12 de 20).
7. **O .msi de outra versão:** consertado (o .msi publicado com o número da versão; o servidor usa a regra única das
   publicações, `DestinoPasta.liberadas`, sem junção, e não entrega nome repetido). Teste:
   `tests/test_publicar_servidor.py::test_achado7_nome_repetido_em_duas_versoes_nao_e_entregue`.
8. **O motor em `instalar\` aceito na atualização:** consertado (lido de `SAIDAS`). Teste:
   `tests/test_publicar_versao.py::test_achado8_o_arquivo_do_motor_em_instalar_e_recusado_na_atualizacao`.
9. **A conta com o .msi curta:** refeita pela leitura do vpk (fontes no docstring de `empacotar.espaco_que_vai_usar`):
   4 vezes a pasta, 7 com o .msi. Teste: `tests/test_publicar_versao.py::test_d776_a_conta_do_espaco_e_a_reserva_de_20_gb`.
10. **A reversão da D-809 só pelo texto:** rodado de verdade o jeito antigo numa junção temporária
    (`anexos/d809-jeito-antigo.txt`): neste Windows ele não entrou na junção. A seção "Cada proteção" passa a dizer que
    o M18 acusa pelo jeito de apagar, não por arquivo perdido.
11. **A etiqueta com quebra de linha:** consertado (conferida inteira). Teste:
    `tests/test_publicar_versao.py::test_achado11_etiqueta_com_quebra_de_linha_e_recusada`.

**Volta 3** (`quem-quebrou/relatorio-2.md`, commit `9cd555a5`; agente novo, D-815). Destino de cada achado:
1. **Versão liberada apagada por uma leitura atrasada:** consertado pela causa (só o rascunho é apagado, lido de novo
   dentro do apagar). Testes: `tests/test_publicar_versao.py::test_volta3_achado1_uma_leitura_atrasada_depois_de_liberar_nunca_apaga_a_versao_liberada`
   (o caso do relatório: o liberar muda a pasta e devolve erro) e
   `tests/test_publicar_versao.py::test_volta3_achado1_no_github_a_leitura_atrasada_tambem_nunca_apaga_a_liberada`.
   Fica o instante do GitHub (Ressalvas).
2. **O .msi pela metade com o nome certo:** consertado (a cópia conferida; a frase diz que a versão foi publicada; a
   conferência do fim compara o .msi). Testes: `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_que_nao_termina_de_copiar_nao_fica_com_o_nome_certo`,
   `tests/test_publicar_versao.py::test_volta3_achado2_o_msi_da_pasta_de_saida_e_comparado_com_o_do_rascunho`,
   `tests/test_publicar_versao.py::test_volta3_achado2_a_frase_do_fim_nao_diz_apagado_sem_conferir`,
   `tests/test_publicar_versao.py::test_volta3_a_copia_conferida_le_de_volta_e_obedece_a_vigia` e
   `tests/test_publicar_versao.py::test_volta3_a_copia_cortada_no_meio_nunca_deixa_o_nome_certo`.
3. **O .bat e o .cmd pela peça:** consertado na peça do passo 1 (regra única do rodar, do lançar e do grupo). Testes:
   `tests/test_windows_peca.py::test_bat_e_cmd_sao_recusados_pelo_rodar_pelo_lancar_e_pelo_grupo` e
   `tests/test_windows_peca.py::test_um_lote_que_a_peca_nao_acha_tambem_e_recusado_pela_extensao`. O vpk de mentira
   virou um programa de prova de verdade.
4. **O "conferido" do `fechar_tudo` e o instante do grupo:** consertado (nasce parado, entra no grupo, conferido, solto).
   Testes: `tests/test_windows_peca.py::test_o_programa_nasce_parado_e_so_roda_dentro_do_grupo`,
   `tests/test_windows_peca.py::test_fechar_tudo_so_diz_conferido_quando_o_windows_diz_que_nenhum_ficou` e
   `tests/test_publicar_versao.py::test_volta3_achado4_a_vigia_fecha_o_filho_do_vpk_antes_de_soltar_o_grupo` (fechar só
   o vpk não passa).
5. **O rascunho apagado quando o liberar falha:** teste novo,
   `test_volta3_achado5_o_liberar_que_falha_e_continua_rascunho_apaga_o_rascunho` (saiu na volta 4: a D-816 tirou o que ele cobrava).
6. **O motor que muda durante a publicação:** teste novo,
   `tests/test_publicar_versao.py::test_volta3_achado6_o_motor_trocado_durante_a_publicacao_impede_liberar`.
7. **O motor baixado fora da conta e da vigia; o nome escrito à mão:** consertado (a conta, a vigia única, o nome em
   `versao.py`). Testes: `tests/test_publicar_versao.py::test_volta3_achado7_o_motor_baixado_entra_na_conta_e_na_vigia`,
   `tests/test_publicar_versao.py::test_volta3_achado7_o_gh_que_baixa_e_fechado_pela_vigia` e
   `tests/test_publicar_versao.py::test_volta3_achado7_o_nome_do_motor_so_em_versao_py`.
8. **Textos que não batiam:** consertados (o cabeçalho da peça, o rascunho da pasta, a janela do servidor, a conta das
   Ressalvas). Teste da janela:
   `tests/test_publicar_servidor.py::test_achado8_o_nome_repetido_aparece_na_janela_como_repetido_e_nao_como_inexistente`.
9. **Sem a leitura do grupo, "continua rodando":** consertado ("não deu para conferir"); e a primeira pasta de troca
   apagada quando a segunda não nasce. Testes: `tests/test_windows_peca.py::test_fechar_tudo_so_diz_conferido_quando_o_windows_diz_que_nenhum_ficou`
   e `tests/test_windows_peca.py::test_o_lancado_solto_apaga_a_primeira_pasta_se_a_segunda_nao_nasce`.
10. **O console do grupo chamado pelo programa do Kaique:** anotado para o passo 3 (Ressalvas), com o jeito de evitar
    (CREATE_NO_WINDOW quando quem chama não tem console). Não mudei.

**Volta 4** (`quem-quebrou/relatorio-3.md`, commit `5f96975b`; escritor novo, D-815). Destino de cada achado (código em
`783b6814`, `dfe5f70d` e seguintes; reversão em `anexos/reversao-volta4-codigo-antigo.txt` e
`anexos/reversao-volta4-resultado.txt`):
1. **No GitHub, duas leituras atrasadas depois de liberar apagavam a versão liberada:** consertado pela D-816 (Samuel,
   20/11: "A , mas onde estamos antes de você fazer qualquer processo"): depois do pedido de liberar, nada é apagado,
   em nenhum destino, sem ler. Testes com 1, 2, 3 e 10 atrasos, na pasta e no GitHub, na versão e no motor, o liberar
   que falha e o Ctrl+C (`test_d816_*`, em `tests/test_publicar_versao.py`). O teste antigo de 1 atraso continua passando.
2. **`pwsh.exe.`, `pwsh.exe..` e `Update.exe.` passavam pela peça:** consertado (o nome lido uma vez, como o Windows o
   completa, e usado em todas as conferências). Achado junto: `whoami.exe.` (o nome sozinho) rodava o whoami da pasta
   do Windows; o mesmo conserto. Teste:
   `tests/test_windows_peca.py::test_volta4_o_nome_com_ponto_no_fim_e_lido_como_o_windows_completa` (os três caminhos,
   pelo caminho e pelo PATH).
3. **"NÃO apaguei" tendo pedido para apagar:** consertado (o apagar escreve a frase e sabe se pediu). No caso do
   relatório (o liberar falha), a D-816 já não pede nada. Testes:
   `tests/test_publicar_versao.py::test_volta4_achado3_a_frase_diz_se_pediu_para_apagar`,
   `tests/test_publicar_versao.py::test_volta4_achado3_o_pedido_de_apagar_sem_resposta_diz_que_pediu` e
   `tests/test_publicar_versao.py::test_volta4_achado3_liberada_no_meio_do_apagar_nunca_vira_apagada`.
4. **"foi apagada (conferido)" sem ter pedido nada; o criar fora do try:** consertado. Teste:
   `tests/test_publicar_versao.py::test_volta4_achado4_nao_achei_logo_depois_de_criar_nao_e_apagado` (os dois casos).
5. **A cópia de um programa do Windows fora da pasta do Windows passa:** não consertado (pedido da gerente); limite
   escrito em "Ressalvas" e em "Cada proteção", e no docstring da regra (`windows._por_que_recusa`).
6. **Os atalhos da Loja recusados com frase falsa:** consertado (frase própria). Teste:
   `tests/test_windows_peca.py::test_volta4_o_programa_que_nao_deixa_ler_e_recusado_com_frase_propria` (um programa
   trancado de verdade pelo Windows, e os atalhos da Loja deste computador).
7. **A soma do GitHub baixava para o C: fora da conta e da vigia:** consertado (o rascunho, `baixar_vigiado`, a conta).
   Testes: `tests/test_publicar_versao.py::test_volta4_achado7_sem_a_soma_pronta_o_download_vai_ao_rascunho_pela_vigia`,
   `tests/test_publicar_versao.py::test_volta4_achado7_a_conta_do_espaco_soma_o_que_a_soma_pode_baixar` e
   `tests/test_publicar_versao.py::test_volta4_achado7_no_publicar_sem_a_soma_pronta_tudo_e_baixado_no_rascunho`.
8. **O laço "rodar, olhar a vigia e fechar" em dois lugares:** consertado (`windows.rodar_em_grupo`, usado pelo vpk e
   pelo gh; o gh passou para a peça e o grupo). Testes:
   `tests/test_windows_peca.py::test_volta4_rodar_em_grupo_e_o_laco_unico_com_a_saida_a_vigia_e_o_tempo` e
   `tests/test_publicar_versao.py::test_volta4_achado8_o_gh_roda_pelo_laco_unico_da_peca_e_fecha_o_que_abriu`.
   Nada do que já estava escolhido mudou (a frase do vpk e a do gh na vigia são as mesmas; os testes antigos passam).
9. **O caminho do teste do lote escrito errado:** consertado (texto cru).
10. **A segunda olhada depois do PATH sem teste:** teste novo,
    `tests/test_windows_peca.py::test_volta4_a_segunda_olhada_depois_do_path_recusa_o_lote_achado_pelo_pathext` (um lote
    achado pelo PATHEXT). Passa também no código antigo (a proteção já existia); a mutação prova que ele a cobra.
11. **"lida de volta do disco" sem gravar no disco:** consertado (`windows.gravar_no_disco`, na cópia, no motor
    comprimido e na gravação da peça). Testes:
    `tests/test_publicar_versao.py::test_volta4_achado11_a_copia_e_o_motor_gravam_no_disco_antes_de_conferir_e_trocar` e
    `tests/test_windows_peca.py::test_volta4_a_peca_manda_gravar_no_disco_antes_de_trocar_o_nome`.
12. **Os testes do desinstalar falham no PC:** não é deste passo; em "Ideias e bugs" para a Lista de bugs.

**Volta 5** (`quem-quebrou/relatorio-4.md`, commit `277fe8fd`; o mesmo escritor da volta 4, segunda e última volta,
D-815). Destino de cada achado (código em `35ec0c27`; reversão em `anexos/reversao-volta5-codigo-antigo.txt` e
`anexos/reversao-volta5-resultado.txt`):
1. **Três frases mandavam apagar no GitHub estando na pasta:** consertado (o lugar único `comando_de_apagar`). Teste:
   `tests/test_publicar_versao.py::test_volta5_achado1_as_frases_de_ja_existe_dao_o_comando_do_destino` (as três).
2. **"Pedi para apagar" sem ter pedido:** consertado (`ApagarSemResposta`). Teste:
   `tests/test_publicar_versao.py::test_volta5_achado2_a_leitura_sem_resposta_antes_do_pedido_nao_vira_pedi_para_apagar`.
3. **Duas proteções sem teste:** testes novos,
   `tests/test_publicar_versao.py::test_volta5_achado3a_o_gh_de_verdade_fechado_por_tempo_no_apagar_diz_que_pediu` e
   `tests/test_publicar_versao.py::test_volta5_achado3b_liberada_antes_do_pedido_no_github_continua_publicacao_liberada`.
4. **"Pedi para liberar" com o gh sem abrir:** consertado pela escolha da gerente (`NadaSaiu`; o rascunho é apagado,
   D-816). Testes: `tests/test_publicar_versao.py::test_volta5_achado4_o_gh_que_nem_abre_no_liberar_nao_conta_como_pedido`
   e `tests/test_publicar_versao.py::test_volta5_achado4_so_o_gh_que_nao_abriu_de_verdade_e_nada_saiu`.
5. **O fluxo escondido passava:** consertado (recusa com frase própria). Teste:
   `tests/test_windows_peca.py::test_volta5_o_programa_num_fluxo_escondido_de_outro_arquivo_e_recusado`.
6. **O texto de `gravar_no_disco` prometia demais:** consertado (nomeia quem passa e quem não passa).
7. a 9. **Observações:** anotadas em "Ressalvas".

**Volta 6** (`quem-quebrou/relatorio-5.md`, commit `b9300da8`; escritor novo, D-815; e o defeito da prova à vista de
20/11). Destino de cada achado (código em `3abf9acf`; reversão em `anexos/reversao-volta6-codigo-antigo.txt` e
`anexos/reversao-volta6-resultado.txt`):
- **O defeito da prova à vista (o publicar montado do zero parava em "não tem o Visual C++ em instalar\"):** consertado
  pela causa (a montagem põe o Visual C++, a mesma conferência para todos os caminhos, também antes do vpk). Testes:
  `tests/test_publicar_versao.py::test_volta6_a_versao_montada_do_zero_leva_o_visual_c_e_e_publicada`,
  `tests/test_publicar_versao.py::test_volta6_a_mesma_conferencia_da_pasta_em_todos_os_caminhos` e
  `tests/test_publicar_versao.py::test_volta6_a_copia_do_visual_c_pela_metade_nao_deixa_a_ficha`.
1. **O apagar em que o gh nem abre, sem teste:** teste novo,
   `tests/test_publicar_versao.py::test_volta6_achado1_o_apagar_em_que_o_gh_nem_abre_diz_nao_apaguei` (o pedido de
   apagar passa pelo `_gh` de verdade; a X3 de quem quebrou é acusada, mutação Y7).
2. **A frase do motor que falta sem o `--pasta`:** consertado (`_Destino.comando_de_publicar_o_motor`). Teste:
   `tests/test_publicar_versao.py::test_volta6_achado2_a_frase_do_motor_que_falta_da_o_comando_do_destino`.
3. **O caminho de rede com a frase errada:** consertado (`windows.FRASE_CAMINHO_DE_REDE`). Teste:
   `tests/test_windows_peca.py::test_volta6_achado3_o_caminho_de_rede_e_recusado_com_a_frase_propria`.
4. **Observação 4:** em "Ressalvas", Volta 6. **Observações 5 e 6:** em "Ideias e bugs", Volta 6.

**Volta 7** (`quem-quebrou/relatorio-6.md`, commit `db4b377a`; o mesmo escritor da volta 6, segunda e última volta,
D-815). Destino de cada achado:
1. **A pasta já montada conferida bem menos que a montada do zero (médio):** consertado pela D-818 (a mesma
   conferência, a régua única do Visual C++, a versão dele e o Tesseract pela lista única). Teste:
   `tests/test_publicar_versao.py::test_d818_a_pasta_ja_montada_e_conferida_igual_a_montada_do_zero` e
   `tests/test_empacotar.py::test_d818_a_montagem_e_a_pasta_usam_a_mesma_regua_do_visual_c`. A pasta de mentira dos
   testes antigos ganhou as peças (lista em "O que já está escolhido e testado aqui", Volta 7).
2. **O item 14 do roteiro depois do 13:** o roteiro mudou ("A prova de verdade", Volta 7: o da pasta antiga primeiro).
3. **Duas conferências do pacote sem teste:** testes novos com o vpk de mentira deixando uma peça de fora:
   `tests/test_publicar_versao.py::test_volta7_achado3_o_pacote_sem_uma_peca_e_recusado_depois_do_vpk` (4 casos) e
   `tests/test_publicar_versao.py::test_volta7_achado3_o_pacote_montado_do_zero_sem_o_tesseract_e_recusado`; e o
   pacote passou a cobrar a versão do Visual C++ e, sempre, o Tesseract.
4. **O empacotar sozinho mexia na pasta antes de recusá-la:** consertado (a conferência antes de `preparar_saida`).
   Teste: `tests/test_publicar_versao.py::test_volta7_achado4_o_empacotar_chamado_sozinho_recusa_antes_de_mexer_na_pasta`.
5. **As aspas sem teste:** teste novo, `tests/test_publicar_versao.py::test_volta7_achado5_a_pasta_das_provas_com_espaco_no_nome`
   (a frase do motor e a do apagar, seguidas, numa pasta com espaço).
6. a 10. **Observações:** em "Ressalvas", Volta 7 (6, 7, 8 e 10) e em "Ideias e bugs", Volta 7 (6 e 9).

**Volta 8** (`quem-quebrou/relatorio-7.md`, commit `21f1fc50`; escritor novo, D-815; e os 2 defeitos da prova à vista de
20/11, 18h a 19h30). Destino de cada achado:
1. **Duas proteções do Visual C++ sem teste (W1, W5):** testes novos, a leitura que falha (a peça do PowerShell
   responde "não terminou") e uma cópia do powershell.exe do Windows como Visual C++, lida de verdade, na pasta e na
   montagem: `tests/test_publicar_versao.py::test_volta8_baixo1a_a_leitura_da_assinatura_que_falha_nunca_vira_passou` e
   `tests/test_publicar_versao.py::test_volta8_baixo1b_um_programa_da_microsoft_que_nao_e_o_visual_c_e_recusado_pela_mesma_regua`
   (mutações U8 e U9).
2. **A versão comparada inteira sem teste (W4):** `tests/test_publicar_versao.py::test_volta8_baixo2_o_arquivo_da_versao_vazio_ou_pela_metade_e_recusado`
   (5 casos; mutação U10).
3. **As licenças do Tesseract sem teste (W2, W3):** `tests/test_publicar_versao.py::test_volta8_baixo3_sem_a_licenca_do_tesseract_a_pasta_e_o_pacote_sao_recusados`
   (as duas licenças, na pasta e no pacote; mutações U11 e U12).
4. **A família repetida:** da gerente (catálogo); em "Ressalvas", Volta 8.
5. **O item 14 do roteiro:** corrigido ("A prova de verdade", Volta 8, item 14).
6. **O arquivo da versão do Visual C++ lido de dois jeitos:** consertado em `b2863630`, uma leitura só, a do publicar,
   usada pelo programa instalado: `tests/test_publicar_versao.py::test_volta8_baixo6_a_versao_do_visual_c_e_lida_por_uma_funcao_so`
   e `tests/test_publicar_versao.py::test_volta8_baixo6_o_publicar_e_o_programa_instalado_usam_a_mesma_leitura`
   (mutações U5, U6 e U7).
7. a 11. **Observações:** em "Ressalvas", Volta 8 (9, 10 e 11) e em "Ideias e bugs", Volta 8 (7 e 8).
- **O defeito 2 da prova à vista (a frase depois de apagar):** consertado em `b2863630`:
  `tests/test_publicar_versao.py::test_volta8_defeito2_o_apagar_diz_que_apagou_quando_apagou`,
  `tests/test_publicar_versao.py::test_volta8_defeito2_o_caminho_de_erro_usa_a_mesma_frase_do_apagar` e
  `tests/test_publicar_versao.py::test_volta8_defeito2_o_que_o_apagar_devolve_nao_mudou` (mutações U1 a U4).
- **O defeito 1 da prova à vista (as peças no lugar errado numa cópia):** não consertado; parado (em "Perguntas para o
  Samuel", Volta 8, o pedido à gerente).

## A prova de verdade

Roteiro para a gerente (não rodado; D-785, item 8; o plano: "0 perguntas do Windows"; o Samuel olha a janela, não
clica nada):
1. Gravar a ficha do motor de hoje (com o "sim" dele, ver "Ressalvas"):
   `.venv\Scripts\python.exe montar_motor_kraken.py --so-ficha --destino D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken`.
2. Abrir o servidor das versões à vista: `.venv\Scripts\python.exe servidor_das_versoes.py --pasta <pasta de prova>`.
3. Publicar o motor 1 na pasta: `publicar_versao_kaique.py --motor --pasta <pasta de prova>`.
4. Publicar uma versão de prova no C: sem o .msi, com a janela do servidor mostrando a versão chegar: o espaço do C:
   antes e depois (volta ao que era), o tempo, e no fim a conferência mostra que o Setup.exe não está em lugar nenhum.
5. Um erro de propósito no meio (fechar o vpk pelo Gerenciador de Tarefas, ou desligar a internet antes do envio ao
   GitHub; olhar no Gerenciador de Tarefas que não sobrou cmd.exe nem wix.exe depois, achado 2; e que a frase do
   apagar no GitHub diz "foi apagada (conferido)", achado 1): o rascunho e o Setup.exe também somem. Na passada com o
   .msi, olhar também que o .msi da pasta de saída tem o tamanho do feito no rascunho (a linha "igual ao feito agora"
   da conferência do fim; relatório 2, "O que falta", item 4).
6. Outra versão com `--com-instalador`: medir o .msi com o motor num arquivo só.
7. O aviso de pouco espaço: com a reserva aumentada só nesta prova (`--reserva-gb` com um número maior que o espaço
   livre do C:; a opção só aumenta, nunca abaixo de 20 GB), o publicar recusa antes do vpk; o C: nunca é enchido.
8. No GitHub, como rascunho: `publicar_versao_kaique.py --motor` e a versão de teste sem `--pasta`; ler de volta,
   liberar, e no fim `--apagar v<versão>` e `--apagar motor-kraken-1` (conferido: "não existe").
9. Depois, as versões de prova do passo 3 (lista do plano): a primeira com o .msi (motor 1); uma boa; uma que nem abre;
   uma com a assinatura de uma chave falsa; uma que pede o motor 2, com o motor 2 verdadeiro e o motor 2 com assinatura
   falsa (o motor 2 pede aumentar `core/ocr_kraken.VERSAO_DO_MOTOR` numa cópia); e uma boa para o atualizar de longe.

**Volta 4, o que a prova à vista acrescenta (relatório 3, "O que falta", item 4, e a D-816):**
10. No item 8, depois do `--apagar`, conferir também que a etiqueta sumiu do GitHub (a lista de etiquetas do
    repositório), não só a publicação.
11. Se der para provocar sem risco (desligar a internet logo depois de o publicar dizer "lido de volta ... somas e
    assinatura conferidas", antes de liberar), conferir que nada é apagado e que a frase diz o que pode ter ficado, como
    conferir e o comando de apagar; e rodar o comando de conferir da frase.
12. O gh roda agora num grupo do Windows, como o vpk: olhar, no Gerenciador de Tarefas, que não sobra gh.exe depois de
    publicar.

**Volta 6, o que a prova à vista acrescenta (o defeito de 20/11):**
13. Repetir o publicar da prova SEM `--pasta-pronta` (`publicar_versao_kaique.py --pasta C:\EditorImpressaoProva\versoes`):
    a montagem tem de dizer "Visual C++ em instalar\, conferido" antes de "pronto: ...\dist\EditorImpressao", passar da
    conferência da pasta e chegar ao vpk de verdade. Depois, abrir o pacote publicado (é um zip) e ver
    `lib/app/instalar/vc_redist.x64.exe` lá dentro.
14. A pasta que a prova de 20/11 montou (código antigo) com `--pasta-pronta`: tem de ser recusada com "não tem o Visual
    C++ em instalar\" (a pasta de fora continua cobrada).
15. Na pasta das provas, sem o motor publicado: a frase tem de dizer `publicar_versao_kaique.py --motor --pasta "..."`.
(A ordem dos itens 13 a 15 acima não dá para seguir: o 14 tem de vir antes do 13. Vale a lista da Volta 7, abaixo.)

**Volta 7, os itens 13 a 15 na ordem certa e o que o relatório 6 pede para a prova (achado 2 e "O que falta para a
prova à vista", item 2). Substituem os itens 13 a 15 da Volta 6:**
13. **Antes de montar qualquer coisa** (a pasta da prova de 20/11 ainda existe; o item 14 a apaga e monta de novo):
    `publicar_versao_kaique.py --pasta C:\EditorImpressaoProva\versoes --pasta-pronta <a pasta dist\EditorImpressao da
    cópia passo2>`. Tem de parar ANTES da conta do espaço com "não tem o Visual C++ em instalar\" (a pasta de fora
    continua cobrada). E não usar `--pasta-pronta` numa pasta arrumada à mão: agora ela é recusada pela assinatura, pela
    versão e pelo Tesseract, mas a prova não precisa disso.
14. Ainda antes de montar, ler na linha "Visual C++: ..." de onde ele vem. Rodando da cópia `passo2`, vem de
    `D:\programas\EditorImpressao\.claude\worktrees\EditorImpressao-arquivos\ferramentas\downloads\` (o bug de 20/11 em
    "Ideias e bugs"); se o arquivo sumir de lá, a montagem baixa da internet.
15. O publicar SEM `--pasta-pronta` (`publicar_versao_kaique.py --pasta C:\EditorImpressaoProva\versoes`): a montagem tem
    de dizer "Visual C++ em instalar\, conferido" antes de "pronto: ...\dist\EditorImpressao", passar da conferência da
    pasta (agora com a leitura da assinatura) e chegar ao vpk de verdade. Depois, abrir o pacote publicado (um zip) e
    ver dentro: `lib/app/instalar/vc_redist.x64.exe` com o mesmo tamanho do baixado (uns 25 MB, 25.635.768 bytes),
    o lib/app/instalar/vc_redist.versao.txt com "14.44.35211.0" e a pasta `lib/app/tesseract/` com os idiomas.
16. O item 6 (`--com-instalador`) **montado do zero**; depois dele, ver que `dist\EditorImpressao\instalar\` ficou só com
    o Visual C++ e a versão dele (o zip do motor tem de sair).
17. Na pasta das provas, sem o motor publicado (numa pasta de provas nova, vazia): a frase tem de dizer
    `publicar_versao_kaique.py --motor --pasta "..."`; seguir a frase ao pé da letra e ver o motor chegar na janela do
    servidor, e nada no GitHub.

**Volta 8, o que a prova à vista acrescenta (os 2 defeitos de 20/11 e o achado 5 do relatório 7):**
14. (substitui o item 14 da Volta 7, que não dava para fazer onde estava) No item 15, logo no começo, antes de o
    PyInstaller começar, ler a linha "Visual C++: ..." que a montagem imprime (vem junto com "motor do Kraken: ..." e
    "Tesseract: ..."): ela diz de onde o arquivo vem. Rodando da pasta principal, tem de ser
    `D:\programas\EditorImpressao-arquivos\ferramentas\downloads\vc_redist.x64.exe`. Rodando de uma cópia, enquanto o
    defeito 1 não for consertado, vem da pasta errada de 19/11 (ou é baixado para lá, se ela sumir). Antes do item 15,
    só dá para olhar se o arquivo está na pasta de downloads (está: 25.635.768 bytes, conferido pelo relatório 7).
18. **O `--apagar` (o defeito 2):** depois de uma publicação de prova na pasta das provas,
    `publicar_versao_kaique.py --apagar v<versão> --pasta <pasta de prova>` tem de dizer "a publicação v<versão> foi
    apagada de a pasta ... (conferido)", e a janela do servidor não mostra mais a versão. Rodado de novo, o mesmo comando
    tem de dizer "v<versão>: não existia em a pasta ..., e nada foi apagado (conferido)". No item 8 (o GitHub), o mesmo:
    "foi apagada de o GitHub (...) (conferido)" para a versão e para o `motor-kraken-1` (antes o roteiro esperava "não
    existe"; agora essa frase só aparece se não havia nada).
19. **O motor achado no lugar certo, da cópia (o defeito 1; só depois do conserto dele):** da cópia de trabalho (a
    `passo2` ou a da versão de teste), numa pasta de provas nova e vazia com espaço no nome:
    `publicar_versao_kaique.py --pasta "C:\EditorImpressaoProva\versoes 3"` tem de parar com "publique o motor antes,
    com: publicar_versao_kaique.py --motor --pasta "C:\EditorImpressaoProva\versoes 3"". Seguir essa frase ao pé da letra,
    da mesma cópia: a linha "motor do Kraken 1: ..." tem de dizer
    `D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken (conferido pela ficha)` (na prova 6b dizia "não
    achei", procurando em `.claude\worktrees\EditorImpressao-arquivos`), e o motor chega na janela do servidor. Depois, um
    publicar montado do zero da cópia: a linha "Visual C++: ..." tem de dizer a pasta de downloads de
    `D:\programas\EditorImpressao-arquivos\ferramentas`. E nenhuma pasta nova aparece em `D:\programas\EditorImpressao\.claude\worktrees`
    (olhar a lista dela antes e depois).

## Perguntas do Windows que o Samuel vê

- Nesta entrega: 0 (nada pede licença; o publicar não pede).
- Na prova à vista: 0 (o plano: "0 perguntas do Windows"). O servidor escuta só em 127.0.0.1: o firewall não pergunta.

- Volta 4: 0 (nada desta volta pede licença; o gh e o vpk no grupo não pedem).

- Volta 6: 0 (nada desta volta pede licença; pôr o Visual C++ na pasta é uma cópia de arquivo no D:, sem instalar nada).

- Volta 7: 0 (ler a assinatura de um arquivo não pede licença nem abre janela; a peça abre o PowerShell sem janela).

- Volta 8: 0 (a frase do apagar e a leitura de um arquivo de poucos bytes não pedem licença nem abrem janela; a leitura
  da assinatura da cópia do powershell.exe pela peça abre o PowerShell sem janela).

## Páginas em que foi conferido

Não se aplica: nenhuma página de livro passa por este passo (0 páginas). Os arquivos com a etiqueta de imagem
(`montar_motor_kraken.py`, `core/ocr_kraken.py`) mudaram só na ficha e na conferência do motor, que não tocam a imagem
de nenhuma página.
