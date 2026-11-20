# Passo 2 do plano da parte do Windows: segunda conferência de quem tentou quebrar (19/11/2026)

Sou um agente novo nesta volta (D-815): não escrevi este código, não fiz a volta 1 e não mexi no código. Não rodei o
vpk, o PyInstaller nem o `gh release`, não publiquei nada, não pedi licença de administrador e não abri janela na tela
do Samuel. Tudo o que rodei foi numa cópia do código (`git archive`) na pasta de rascunho desta conversa.

## Pedido

- Papel: quebrador
- Commit de partida: 403afc07
- Ramo: passo2-publicar-2026-11-19

## Arquivos que vou mexer

- `publicar_versao_kaique.py`
- `empacotar.py`
- `montar_motor_kraken.py`
- `core/ocr_kraken.py`
- `versao.py`
- `core/windows.py`
- `tests/test_windows_peca.py`
- `servidor_das_versoes.py`
- `tests/test_empacotar.py`
- `tests/test_publicar_*.py`
- `relatorios/passo2-publicar/`

(A lista é a do pacote, copiada sem mudar. Na prática só escrevi em `relatorios/passo2-publicar/quem-quebrou/`.)

## Veredito

**NÃO ESTÁ PRONTO para a prova à vista.** Os 11 achados da volta 1 foram consertados pela causa, e conferi isso eu
mesmo: desliguei cada conserto numa cópia e o teste dele falhou. Mas achei **três problemas médios novos**:

1. depois de pedir para liberar, uma leitura atrasada do destino faz o publicar **apagar uma versão que já estava
   liberada**: a regra "só o rascunho é apagado" é decidida numa leitura, e o apagar lê de novo por conta própria;
2. se a cópia do .msi para a pasta de saída falha no meio (disco cheio), **um .msi pela metade fica lá com o nome
   certo**, e a frase diz "o que esta vez fez pela metade foi apagado";
3. a peça fechada do Windows **deixa rodar o cmd.exe por um arquivo .bat ou .cmd**, e a peça nova `abrir_em_grupo`
   herda essa porta (os próprios testes usam um `vpk.cmd`).

Nenhum é grave e nenhum aparece no roteiro da prova à vista como ele está. Pela D-775, achado volta para quem
escreveu; a gerente decide se manda consertar antes ou se leva à prova com eles escritos. Não escrevo "PRONTO PARA
CONFERIR" (D-798): ainda falta a prova à vista. Nunca "aprovado": só o Samuel aprova.

## Decisões que esta tarefa precisa cumprir

- D-775 "o agente vai tentar quebrar antes de fazer o teste real na tela né?" · "ok". Aqui: tentei quebrar sem
  pergunta do Windows; o resultado vai à gerente.
- D-815 "esses agentes que você criou, sempre que vai fazer uma tarefa nova, chama outro com a mesmas instruções ou
  ifac rodando sempre o mesmo com memorias compactadas?" · "ok". Aqui: agente novo nesta volta.
- D-798 "fechou". Aqui: sem o rótulo de pronto.
- D-776 "Sim, no C só tem que cuidar para não encher o disco C inteiro". Aqui: conferi a conta (4 e 7 vezes) no código
  do vpk.
- D-767 "não faça mais nada escodindo ou de mentira". Aqui: o grupo do Windows rodou de verdade; o vpk e o GitHub, não
  (proibidos neste pedido).
- D-809, D-811, D-812, D-813 (as regras da peça fechada e das proteções). Aqui: achados 3, 4 e 5.

## O que li

- `.claude/agents/verificador.md`, o `CLAUDE.md` inteiro, `memoria/INDICE.md` e `memoria/catalogo-de-erros.md`
  (famílias F1 a F10).
- O meu pacote (`anexos/pacote-quem-quebra-volta2.md`), o relatório da volta 1 (`quem-quebrou/relatorio-1.md`), o
  formulário do outro (`ONDE-PAREI.md`) e os anexos `reversao-volta2-resultado.txt` e `d809-jeito-antigo.txt`.
- O plano v3 (worktree `plano-windows`): o passo 2 e as peças 8, 9 e 10.
- O Livro de decisões no ramo `obra-2026-10-26` (D-809 a D-815; no ramo deste passo elas ainda não estão).
- O código da volta 2 inteiro (`git diff a58f181b 0d51ad5e`): `core/windows.py` (`ProgramaEmGrupo`, `abrir_em_grupo`,
  `lancar_powershell_solto`), `empacotar.py` (`rodar_vpk`, `espaco_que_vai_usar`, `proibidos_no_pacote_do_velopack`,
  `nome_do_msi_publicado`), `publicar_versao_kaique.py` inteiro, `servidor_das_versoes.py` e os testes novos.
- **O código do vpk 1.2.161** (a cópia em `saida_teste\publicar-rapido\fonte-velopack\repo`, etiqueta 1.2.161,
  commit 92d6a1c9), para a conta do espaço: `PackageBuilder.cs` 55-192 e 286-305, `WindowsPackCommandRunner.cs` 35-60
  e 200-252, `MsiBuilder.cs` 180-225, `BuildAssets.cs` 37-42.
- **O código do gh** (`cli/cli`, `pkg/cmd/release/delete/delete.go`, ramo trunk, lido de novo em 19/11): com
  `--cleanup-tag`, o `deleteRun` apaga a etiqueta depois da publicação, sem olhar se é rascunho; o `IsDraft` só aparece
  no aviso de "a etiqueta ficou". Bate com o conserto do achado 1.

## O que conferi nas falhas, nas peças de fora e nos caminhos

**Os 11 achados da volta 1, refeitos por mim numa cópia** (o resultado está em `anexos-2/mutacoes-resultado.txt`; as
primeiras linhas com "0 vezes" são da minha primeira tentativa, antes de eu ajustar o script às quebras de linha do
Windows, e foram refeitas logo abaixo):

| Achado | O que eu desliguei | O teste falhou? |
|---|---|---|
| 1 | o apagar do rascunho no GitHub volta a pedir a etiqueta | sim |
| 1 | o aviso do gh volta a virar "não apagou" sem ler | sim |
| 2 | fechar só o vpk e dizer "fechados (conferido)" | **não** (achado 4 abaixo) |
| 3 | N5, N14, N13, e os do formulário | sim; **N4: não** na comparação (achado 6) |
| 4 | apagar a versão depois de pedir para liberar | sim |
| 4 | nunca apagar o rascunho depois de pedir para liberar | **não** (achado 5) |
| 5 | o erro do disco volta a sair cru | sim |
| 6 | o sinal de vida volta para a pasta que o script apaga | sim |
| 7 | o servidor volta a entregar nome repetido | sim |
| 7 | o .msi volta ao nome sem o número | sim |
| 8 | a atualização volta a aceitar o motor em instalar\ | sim |
| 9 | a conta volta a 3 e 5 vezes | sim |
| 11 | a etiqueta volta ao `match` | sim |

E rodei os testes novos **no código da volta 1** (os três arquivos novos copiados sobre `a58f181b`): 11 falharam em
`test_publicar_versao.py`, 2 em `test_publicar_servidor.py` e 2 em `test_windows_peca.py`. Os de N1, N3, N4, N5, N6,
N8 e N14 passam lá, e está certo: essas proteções já existiam, só não tinham teste.

Dois testes falham no código antigo pela frase ou por falta da função, não pelo comportamento: o do achado 2 (falha
em "fechados (conferido)") e o do achado 11 (falta `e_etiqueta`). O comportamento dos dois está provado pelas
mutações acima (o do 2, só em parte: achado 4).

**A peça nova `abrir_em_grupo`, rodada de verdade** (`anexos-2/grupo_casos.py.txt`, resultado em
`anexos-2/experiencias-resultado.txt`):

- Fecha os filhos: sim. O teste da peça abre um processo que abre outro, e os dois param. Os netos (o wix.exe dentro do
  cmd.exe) entram no mesmo grupo, pela documentação da Microsoft ("Job Objects").
- Programa que sai na hora (o `true.exe` do Git, 40 vezes): nenhuma vez deu "não deixou pôr no grupo".
- **O instante entre abrir e pôr no grupo:** existe (o `Popen` abre e só depois o programa entra no grupo). Com o vpk
  o risco é pequeno, porque ele só abre o cmd.exe minutos depois. Mas a conferência "nada ficou vivo" **não vê** quem
  escapou: provei com um processo fora do grupo, e `fechar_tudo` disse "fechados (conferido)" com ele vivo (achado 4).
- **Se o grupo não puder ser criado:** `abrir_em_grupo` devolve "falhou" e fecha o que abriu; o `rodar_vpk` devolve
  "não consegui abrir o vpk (...)", o publicar para e o rascunho é apagado. Não há desvio para rodar sem o grupo. Lido,
  não provocado (não dá para fazer o Windows recusar sem mexer nele).
- **As regras da peça fechada:** `abrir_em_grupo` usa a mesma recusa do rodar genérico (`_programa_com_funcao_propria`),
  sem conta própria. Mas a recusa deixa passar o .bat e o .cmd, que o Windows roda pelo cmd.exe (achado 3).

**A decisão da gerente (depois de pedir para liberar, não apagar):**

- Se a leitura falha: não apaga, diz "NÃO apaguei" e para. Conferido no teste e na mutação.
- Se a leitura diz "rascunho": apaga. Funciona (meu caso 2 em `anexos-2/liberada_apagada.py.txt`), mas nenhum teste
  cobra isso (achado 5).
- **Só o rascunho é apagado? Não garantido** (achado 1).

**O .msi com o número da versão:** o publicar dá o nome num lugar só (`empacotar.nome_do_msi_publicado`). O servidor
não tem regra de nome: ele recusa qualquer nome que esteja em duas publicações. Não há duas regras, e os dois batem.
O índice (`releases.win.json`), que se repete em toda publicação, é tratado à parte, como antes.

**A conta do espaço refeita (4 e 7 vezes), conferida linha por linha no vpk 1.2.161:**

- `PackageBuilder.cs:76`: a pasta temporária vive até o fim do pack. Confere.
- `WindowsPackCommandRunner.cs:55-56`: a cópia do pré-processo. É uma cópia inteira da pasta. Confere.
- `PackageBuilder.cs:288-294`: a cópia para o pacote. Outra cópia inteira. Confere.
- `PackageBuilder.cs:303` e `WindowsPackCommandRunner.cs:211-226`: o pacote, e o Setup.exe com o pacote dentro. Os
  dois ficam na temporária, porque `BuildAssets(pkgTempDir)` grava lá até o `MoveBagTo` do fim. Confere: 2 cópias e
  2 comprimidos.
- `WindowsPackCommandRunner.cs:231-235`: o .msi copia a pasta mais uma vez. Confere.
- `MsiBuilder.cs:186-221`: o WiX usa uma temporária que sai do mesmo `TempUtil`, dentro do rascunho. Confere. Que os
  pedaços do WiX somam mais um comprimido não está no código do vpk (é do WiX): o outro escreveu "deduzido, não lido",
  e está certo.
- Contando o comprimido igual à pasta: 4 vezes sem o .msi e 7 com ele. A conta está certa.
- Medi a pasta montada de hoje no D: (`dist\EditorImpressao`): 1,84 GB, dos quais 1,06 GB são o motor. Sem o motor,
  uns 0,78 GB. A conta com o .msi dá uns 12,8 GB. O C: tem hoje 48,9 GB livres: a prova com o .msi passa da reserva.
- Fica de fora da conta o arquivo do motor baixado para o rascunho, uns 0,8 GB (achado 7). A margem de 1 GB cobre.

**O que os consertos podem ter quebrado.** Rodei na cópia, um arquivo por vez:

| Arquivo de teste | Resultado |
|---|---|
| `test_publicar_versao.py` | 36 passaram |
| `test_publicar_servidor.py` | 13 passaram |
| `test_publicar_motor.py` | 12 passaram |
| `test_windows_peca.py` | 57 passaram, 2 pulados |
| `test_empacotar.py` | 41 passaram |
| `test_decisoes_atualizacao.py` | 38 passaram |
| `test_windows_janela_de_prova.py` | 10 passaram |

- A rodada do GitHub 44663876080 testou o commit 0d51ad5e (está no registro da rodada: "codigo trocado pelo de
  passo2-publicar-2026-11-19 (0d51ad5e...)"). Deu success, com o porteiro em success.
- Na peça do passo 1, o lançar solto ganhou uma segunda pasta de troca. Ela é apagada no fim e, se sobrar, pela limpeza
  das trocas velhas. A janela de prova (`prova_lancar_solto`) continua passando.

## Caminhos que o outro não listou

1. **Liberar que deu certo no destino, com a resposta perdida ou a leitura atrasada.** O pedido falha, mas a versão
   já está liberada lá (achado 1).
2. **A cópia do .msi para a pasta de saída depois de a versão estar liberada.** Pode falhar no meio, por disco cheio ou
   Ctrl+C (achado 2).
3. **Um programa que é um arquivo .bat ou .cmd**, pelo rodar genérico e pelo grupo. Quem roda é o cmd.exe (achado 3).
4. **Um processo que escapou do grupo** no instante antes de o programa entrar nele (achado 4).
5. **O arquivo do motor baixado para o rascunho** antes da segunda passada do vpk (achado 7).
6. **A peça chamada por um programa sem console** (pythonw, ou o próprio programa no passo 3). `abrir_em_grupo` abre o
   programa "com a janela de console de quem chama": sem console, o Windows cria uma janela de console nova na tela
   (achado 10, observação para o passo 3).

## Falhas não pensadas e resultado não conferido

- **Resultado não conferido (F5):**
  - o apagar decide de novo, numa leitura própria, o que apagar (achado 1);
  - "o que esta vez fez pela metade foi apagado" é dito sem conferir (achado 2);
  - `fechar_tudo` diz "conferido" contando só quem está no grupo (achado 4);
  - `vivos()` sem leitura vira "algum continua rodando" (achado 9).
- **O vizinho passa (F2):** o .bat e o .cmd passam pela recusa da peça (achado 3).
- **Proteção sem teste que a acuse (F3):**
  - o apagar do rascunho depois de pedir para liberar (achado 5);
  - a comparação "o motor mudou durante a publicação" (achado 6);
  - a frase "conferido" da vigia (achado 4).
- **O escrito não bate com o código (F7):** achado 8 (o cabeçalho da peça, a nota do rascunho na pasta, a frase do
  servidor, as contas da seção "Ressalvas").
- **Regra copiada (§11.12):** o nome "motor-kraken-" está escrito à mão em mais um lugar novo (achado 7).
- **F1 (dado que o conferido pode trocar), F9 (mexer no que é do Samuel), F4 (o teste supõe o computador):** não achei
  caso novo. O conserto do teste do achado 5 (o vpk de mentira na linha de comando) resolve a F4 que o GitHub pegou.

## As regras que conferi

- **§11.12.1 (uma peça por conversa):** o grupo do Windows está na peça, com a mesma recusa do rodar genérico.
  Cumprida. As constantes do grupo foram escritas de novo como números soltos em `_situacao_do_grupo`
  (`core/windows.py:1281-1291`). É pouco, mas é a mesma conta em dois jeitos.
- **§11.12.2 (nada dado como feito sem conferir):** falha nos achados 2 e 4.
- **§11.12.3 (a lista das falhas):** faltam os caminhos 1 a 5 acima.
- **§11.12.6 e D-813 (ler a peça de fora e tudo o que ela aceita):** o vpk e o gh foram bem lidos. O Windows aceita
  rodar .bat e .cmd pelo CreateProcess, que abre o cmd.exe, e isso não foi listado (achado 3).
- **D-811 (cada proteção com o teste que falha sem ela):** três lacunas (achados 4, 5 e 6).
- **D-776:** a conta está certa. A vigia roda durante o vpk e durante a compressão do motor, mas não durante o
  download do motor (achado 7).
- **D-795:** o Setup.exe é apagado logo depois de cada vpk e nunca está na lista do destino. Conferido no código e no
  teste N6.
- **Decisão da gerente do achado 4 (D-014):** cumprida pela metade (achados 1 e 5).
- **D-798:** o ramo não tem rótulo de pronto.
- **D-809:** não criei junção nesta volta. O repositório continua com `--is-shallow-repository` = false, antes e
  depois.

## Achados

1. **MÉDIO: uma leitura atrasada depois de liberar faz o publicar apagar uma versão que já estava liberada.**
   - Onde: `publicar_versao_kaique.py:533` (`publicar_arquivos`, o `if agora != "rascunho"`),
     `publicar_versao_kaique.py:468` (`apagar_publicacao`) e `publicar_versao_kaique.py:451-456`
     (`DestinoGitHub.apagar`).
   - O que acontece: a decisão "ainda é rascunho, pode apagar" é tomada numa leitura. Depois, `apagar_publicacao` lê de
     novo, e `DestinoGitHub.apagar` lê uma terceira vez. Se essa leitura disser "liberada", ele apaga a versão
     liberada, e com a etiqueta.
   - Quando acontece: o liberar chega ao GitHub, mas a resposta se perde (a internet cai na volta). Ou o liberar dá
     certo e a leitura logo depois ainda mostra o estado antigo. É o mesmo caso que a decisão da gerente quer evitar:
     o número da versão fica livre para outro conteúdo.
   - Provado com uma pasta de verdade: o liberar troca o nome da pasta e depois dá erro, e a primeira leitura ainda
     diz "rascunho". Resultado: "a publicação v9.9.9 foi apagada (conferido)", e a versão liberada sumiu
     (`anexos-2/liberada_apagada.py.txt`, caso 1).
   - Não sei se o GitHub responde mesmo com atraso depois de liberar: não achei isso na documentação. A falha de
     desenho existe nos dois destinos.
   - O que pedir: o apagar do caminho de erro recebe "só se for rascunho" e confere isso na hora de apagar. Se ler
     "liberada", não apaga e diz "liberada; não apaguei". Com um teste.

2. **MÉDIO: um .msi pela metade fica na pasta de saída com o nome certo, e a frase diz que o que ficou pela metade foi
   apagado.**
   - Onde: `publicar_versao_kaique.py:756` (`shutil.copyfile(msi, ...)`, depois de a versão estar liberada) e
     `publicar_versao_kaique.py:864` e `:868` (as frases do `main`).
   - O que acontece: o `copyfile` do Python não apaga o arquivo de destino quando falha no meio (disco D: cheio, ou
     Ctrl+C). O publicar para. A conferência do fim lista o .msi como se fosse normal. A linha de comando diz "O que
     esta vez fez pela metade foi apagado". A versão foi publicada, e a frase não diz isso.
   - Provado: com a cópia falhando depois de 10 bytes, ficou `v9.9.9/EditorImpressaoPrograma-9.9.9-win.msi` (10 bytes)
     na pasta de saída, e o destino continuou com a versão liberada (`anexos-2/test_quebra_msi.py.txt` e
     `experiencias-resultado.txt`).
   - Risco: o Samuel entregar ao Kaique um instalador estragado.
   - O que pedir: copiar num nome provisório e trocar de uma vez, como o `DestinoPasta.enviar` já faz. Na falha, apagar
     o provisório. A frase do `OSError` e do Ctrl+C dizer o que de fato ficou: a versão publicada, o .msi que não
     saiu. Com um teste.

3. **MÉDIO: a peça fechada do Windows deixa rodar o cmd.exe por um arquivo .bat ou .cmd, e a peça nova herda isso.**
   - Onde: `core/windows.py:1050` (`_programa_com_funcao_propria`), usada por `rodar_e_esperar`, `lancar_solto` e
     `abrir_em_grupo` (`core/windows.py:1204`).
   - O que acontece: a recusa olha onde está o arquivo pedido. Um `x.bat` fora da pasta do Windows passa, e o Windows
     o roda pelo `C:\WINDOWS\system32\cmd.exe`, que é programa da pasta do Windows, com função própria na peça.
   - Provado: `abrir_em_grupo(["x.bat"])` e `rodar_e_esperar(["x.bat"])` deram certo, e o .bat escreveu
     `C:\WINDOWS\system32\cmd.exe` (`anexos-2/experiencias-resultado.txt`, E3).
   - Os testes do passo dependem dessa porta: o vpk de mentira é um `vpk.cmd`
     (`tests/test_publicar_versao.py:103-104`).
   - É a família F2 de novo (o vizinho passa), na peça do passo 1. Por um .bat, um chamador dos passos 3 a 5 pode
     rodar ferramentas de tarefa e de licença sem o porteiro ver.
   - O que pedir: a recusa olha também o tipo do arquivo. Extensão de lote (.bat, .cmd), e o que mais o Windows abre
     por outro programa, é recusada. A lista vem da documentação do CreateProcess, como a D-813 manda. O vpk de
     mentira dos testes passa a ser um programa de verdade. Com um teste.

4. **BAIXO-MÉDIO: `fechar_tudo` diz "fechados (conferido)" contando só quem está no grupo, e o teste do achado 2 não
   prova a frase.**
   - Onde: `core/windows.py:1170-1187` (`fechar_tudo`) e o texto do cabeçalho em `core/windows.py:1141` ("o
     `fechar_tudo` confere o que ficou").
   - O que acontece: um processo que escapou do grupo no instante antes de o vpk entrar nele não é visto. Provado com
     um processo fora do grupo: "deu certo, fechados (conferido)", e ele continuou vivo (E2).
   - E mais: desliguei o fechamento do grupo e pus a frase "conferido" direto. Os testes do achado 2 e do N10
     passaram. O que fecha o filho nos testes é o fechar-ao-fechar do grupo, no fim do `with`, que vem depois da
     frase. A frase "conferido" não tem teste que a acuse.
   - O que pedir: abrir o programa já parado, pô-lo no grupo e só então soltá-lo. O Windows documenta isso:
     `CREATE_SUSPENDED`, `AssignProcessToJobObject` e `ResumeThread`, ou a lista de grupos do `CreateProcess`. Assim o
     instante some, e o texto do cabeçalho passa a ser verdade. Com um teste que acuse a frase sem a conferência.

5. **BAIXO-MÉDIO: nenhum teste cobra que o rascunho é apagado quando o liberar falha e ele continua rascunho.**
   - Onde: `publicar_versao_kaique.py:533-543`.
   - Desliguei esse apagar (`if True:`) e os 36 testes de `test_publicar_versao.py` passaram. É a outra metade da
     decisão da gerente: sem ela, o rascunho fica no destino.
   - Rodando, o caminho funciona (`liberada_apagada.py.txt`, caso 2), mas falta o teste (D-811).

6. **BAIXO: a comparação "o motor publicado mudou durante a publicação" não tem teste.**
   - Onde: `publicar_versao_kaique.py:622`.
   - O teste do N4 apaga o motor, e a leitura para antes, com "não está publicado". Desligando só a comparação
     (`if False:`), os quatro testes passam. O caso que fica sem prova: o motor trocado por outro com a mesma etiqueta.

7. **BAIXO: o arquivo do motor baixado para o rascunho fica fora da conta e da vigia; e o nome "motor-kraken-" está
   escrito à mão em mais um lugar.**
   - Onde: `publicar_versao_kaique.py:731` (o download, uns 0,8 GB no C:) e `empacotar.py:1288`
     (`espaco_que_vai_usar`, que não o conta). A margem de 1 GB cobre hoje.
   - A vigia do espaço só roda durante o vpk e a compressão do motor; durante esse download, não (D-776: "ele vigia o
     espaço durante o trabalho").
   - O nome: `empacotar.py:1435` (novo, achado 8), mais `empacotar.py:1210` e `publicar_versao_kaique.py:86`, escrevem
     "motor-kraken-" à mão. O lugar único é `versao.arquivo_do_motor` e `versao.etiqueta_do_motor` (§11.12: "uma lista
     é escrita uma vez").

8. **BAIXO: textos que não batem com o código (F7).**
   - `core/windows.py:9-11`: "Nenhum chamador do programa usa esta peça ainda". Agora o `empacotar` a usa, para o
     grupo e para a assinatura.
   - `publicar_versao_kaique.py:276`: "Cria o rascunho vazio (com as notas num arquivo de texto ...)". Nenhuma nota é
     gravada.
   - `servidor_das_versoes.py:195`: um nome que está em duas publicações aparece na janela como "não existe aqui
     (404)". Ele existe, duas vezes.
   - Na seção "Ressalvas" do ONDE-PAREI, as contas do espaço com o .msi se contradizem: "26 GB livres ... recusa (pede
     uns 10 GB)" e, na mesma linha, "com 26 GB livres e o .msi pedido, a conta dá uns 8 GB e passa". Pela pasta de
     hoje, a conta com o .msi dá uns 12,8 GB.

9. **BAIXO: sem leitura do grupo, a frase diz "algum continua rodando".**
   - Onde: `core/windows.py:1186-1187`.
   - Quando `vivos()` não consegue ler o grupo (devolve None), a frase é "algum continua rodando". O certo é "não deu
     para conferir".
   - Na mesma linha de cuidado: em `core/windows.py:1381-1382`, se a segunda pasta de troca não puder ser criada, a
     primeira fica para a limpeza do dia seguinte.

10. **OBSERVAÇÃO para o passo 3 (não é defeito hoje): `abrir_em_grupo` abre o programa com o console de quem chama.**
    - Onde: `core/windows.py:1206`.
    - Do publicar, isso está certo. Do programa do Kaique, que não tem console, abriria uma janela preta na tela dele.
    - Se o passo 3 usar o grupo, isso precisa de uma escolha.

## O que falta para a prova à vista

1. Quem escreveu consertar os achados 1, 2 e 3, cada um com o teste que falha sem o conserto. De preferência também
   os testes dos achados 4, 5 e 6.
2. Ou a gerente decidir levar à prova com eles escritos. Nenhum deles aparece no roteiro como ele está.
3. Uma rodada do GitHub sobre o conserto, e outro agente novo para conferir (D-815).
4. Na prova à vista, item 5 do roteiro: além do Gerenciador de Tarefas, olhar que o .msi da pasta de saída tem o
   tamanho do .msi do rascunho.

## Para a gerente: o que ficou fora do projeto

- Na pasta de rascunho desta conversa
  (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\q3\`)
  deixei:
  - as cópias do código: `0d51ad5e\` (com um arquivo de teste meu, `tests\test_quebra_msi.py`), `a58f181b\` e
    `velho\`;
  - as pastas das experiências: `casos\`, `casos2\`, `casos-lib\` e `casos-lib2\`;
  - os scripts.
  - Não apaguei nada.
- Nenhuma junção foi criada. Nada mudou no Windows: nenhuma tarefa, licença, pergunta de administrador ou janela. Os
  grupos do Windows que abri foram fechados no fim de cada caso.
- Consultei o GitHub duas vezes (a rodada 44663876080 e o registro dela). O repositório não ficou raso.
- No projeto, só escrevi este relatório (três formatos) e a pasta `quem-quebrou/anexos-2/`.
