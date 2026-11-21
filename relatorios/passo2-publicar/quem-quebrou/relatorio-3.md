# Passo 2 do plano da parte do Windows: terceira conferência de quem tentou quebrar (20/11/2026)

Sou um agente novo nesta volta (D-815): não escrevi este código e não fiz as voltas 1 e 2. Não mexi no código do
outro. Não rodei o vpk, o PyInstaller nem o `gh release`, não publiquei nada, não pedi licença de administrador e não
abri janela na tela do Samuel. Tudo o que rodei foi numa cópia do código (`git archive` de `e4263c0a` e de `9cd555a5`)
na pasta de rascunho desta conversa, um arquivo de teste por vez.

## Pedido

- Papel: quebrador
- Commit de partida: c8897f3a
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

(A lista é a do pacote, copiada sem mudar. Na prática só escrevi em `relatorios/passo2-publicar/quem-quebrou/`:
este relatório e a pasta `anexos-3/`.)

## Veredito

**NÃO ESTÁ PRONTO para a prova à vista.** Os 10 achados da volta 2 foram consertados e, na pasta das provas, pela
causa: desliguei cada conserto numa cópia, 18 desligamentos meus, e 15 foram acusados pelo teste. Dos 3 que não
foram, dois são proteções em dobro e um é uma olhada que não achei como alcançar (achado 10). Mas achei **dois
problemas médios**:

1. **No GitHub, a versão já liberada ainda pode ser apagada.** O conserto lê a situação mais uma vez antes de
   apagar. Se a leitura do GitHub vier atrasada duas vezes seguidas, em vez de uma, o publicar apaga a versão
   liberada e diz "foi apagada (conferido)". O teste do conserto imita só uma leitura atrasada, exatamente o número
   de leituras que o código faz. A etiqueta fica no GitHub, e o mesmo número de versão pode voltar com outro conteúdo.
   É o que a decisão da gerente queria evitar.
2. **A recusa da peça do Windows ainda deixa passar o PowerShell 7 e o atualizador do Velopack com um ponto no fim do
   nome** (`pwsh.exe.`). O Windows tira o ponto e roda o programa. A mesma função tira o ponto para conferir o .bat e
   o .cmd, mas não para conferir a lista de nomes. É a regra única com dois jeitos de ler o nome.

Os outros são baixos (frases que dizem mais do que se sabe, uma regressão sem uso hoje, um teste com o caminho
escrito errado). Pela D-775, volta para quem escreveu; a gerente decide se manda consertar antes ou se leva à prova
com eles escritos. Não escrevo "PRONTO PARA CONFERIR" (D-798): ainda falta a prova à vista. Nunca "aprovado": só o
Samuel aprova.

## Decisões que esta tarefa precisa cumprir

- D-775 "o agente vai tentar quebrar antes de fazer o teste real na tela né?" · "ok". Aqui: tentei quebrar sem
  pergunta do Windows; o resultado vai à gerente.
- D-815 (no Livro do ramo `obra-2026-10-26`; o pacote diz "NÃO ACHADA" porque o Livro deste ramo ainda não a tem).
  Aqui: sou um agente novo nesta volta.
- D-798 "fechou". Aqui: sem o rótulo de pronto.
- D-767 "não faça mais nada escodindo ou de mentira". Aqui: a peça do Windows (o lote, os nomes, o grupo) rodou de
  verdade no Windows; o vpk e o GitHub, não (proibidos neste pedido): no GitHub usei o gh de mentira dos próprios
  testes.
- D-773 "A" (o rascunho de prova no GitHub, liberado só na prova e apagado no fim). Aqui: achados 1, 3 e 4.
- D-776 "Sim, no C só tem que cuidar para não encher o disco C inteiro". Aqui: achado 7.

## O que li

- `.claude/agents/verificador.md`, o `CLAUDE.md` inteiro, `memoria/INDICE.md` e `memoria/catalogo-de-erros.md`
  (famílias F1 a F10).
- O meu pacote (`anexos/pacote-quem-quebra-volta3.md`), os relatórios 1 e 2 de quem tentou quebrar, o formulário do
  outro (`ONDE-PAREI.md`: "O que o agente que tentou quebrar achou", "Caminho e função", "Cada proteção e o teste que
  falha sem ela", "De onde vem cada dado", "Ressalvas") e os anexos `reversao-volta3-codigo-antigo.txt`,
  `reversao-volta3-resultado.txt` e `reversao-volta3-mutacoes.py.txt`.
- O plano v3, passo 2 (worktree `plano-windows`).
- O código da volta 3 inteiro (`git diff 9cd555a5 e4263c0a`): `core/windows.py` (`_nao_e_programa_do_windows`,
  `_programa_com_funcao_propria`, `abrir_em_grupo`, `_soltar_o_programa_parado`, `ProgramaEmGrupo.fechar_tudo`,
  `lancar_powershell_solto`), `empacotar.py` (`vigia_do_espaco`, `copiar_inteiro`, `espaco_que_vai_usar`,
  `rodar_vpk`, `zipar_motor`), `publicar_versao_kaique.py` (`apagar_publicacao`, `DestinoPasta.apagar_rascunho`,
  `DestinoGitHub.apagar_rascunho`, `DestinoGitHub._gh`, `publicar_arquivos`, `guardar_o_instalador`,
  `conferencia_do_fim`), `servidor_das_versoes.py`, `versao.py` e os testes novos.
- Peça de fora, o que ela aceita (D-813): o que o Windows faz com cada nome eu não li de novo, **rodei**: o mesmo
  arquivo de lote com 28 nomes e jeitos de chamar, e o que o Windows rodou de verdade (anexo
  `anexos-3/e1-lote-resultado.txt`). Lido de novo: Microsoft Learn, CreateProcessW (o Windows tira o ponto e o espaço
  do fim do nome, pelo GetFullPathNameW) e as citações do Python que o outro pôs no comentário da peça.

## O que conferi nas falhas, nas peças de fora e nos caminhos

**Os 10 achados da volta 2, refeitos por mim numa cópia.**

Rodei os testes novos da volta 3 no código da volta 2 (`anexos-3/reversao-no-codigo-da-volta2.txt`): 5 falham em
`test_windows_peca.py`, 10 em `test_publicar_versao.py` e 1 em `test_publicar_servidor.py`. Bate com o anexo do outro
(mais o teste da cópia cortada no meio, que ele fez depois).

Depois desliguei cada conserto no código novo, um por vez, com um script meu (`anexos-3/mutar.py.txt`,
`anexos-3/mutar2.py.txt`; resultado em `anexos-3/mutacoes-resultado.txt`):

| Achado da volta 2 | O que eu desliguei | O teste falhou? |
|---|---|---|
| 1 | o apagar do GitHub não olha se ficou liberada logo antes de pedir | sim |
| 1 | o apagar não olha a primeira leitura (só a do destino) | **não**: proteção em dobro (a do destino cobre) |
| 2 | a cópia grava direto no nome certo | sim |
| 2 | a conferência do fim não acusa o pedaço `.copiando` | sim |
| 2 | o .msi comparado só pelo tamanho, sem a soma | sim |
| 3 | a peça não lê o começo do arquivo (só a extensão) | sim |
| 3 | a peça não olha a extensão (só o começo) | sim |
| 3 | a segunda olhada, depois de achar o nome no PATH | **não** (achado 10) |
| 4 | o grupo abre o programa rodando, sem parar | sim |
| 4 | a conferência "ele está no grupo" desligada | **não**: o outro já escreveu que é em dobro |
| 5 | o caminho de erro nunca apaga o rascunho | sim |
| 6 | sem a comparação "o motor mudou" | sim |
| 7 | o motor baixado fora da conta | sim |
| 7 | o download do motor sem a vigia | sim |
| 7 | a vigia única nunca manda parar | sim |
| 8 | o servidor trata o nome repetido como inexistente | sim |
| 9 | a primeira pasta de troca fica | sim |
| 9 | sem leitura do grupo, "continua rodando" | sim |

**O apagar que só apaga rascunho.**

- Na pasta das provas está certo pela construção. O apagar do caminho de erro só toca a subpasta do rascunho; a
  liberada é outra pasta, que ele nem olha.
- No GitHub, não. A regra "só o rascunho" depende de a leitura estar em dia. O código lê duas vezes antes de apagar
  (uma em `apagar_publicacao`, outra em `DestinoGitHub.apagar_rascunho`). Com uma leitura atrasada, a segunda vê
  "liberada" e não apaga. Com duas, apaga (achado 1).
- O outro escreveu nas Ressalvas que sobra "um instante" no GitHub, entre a leitura e o pedido de apagar. Não é só
  um instante. É qualquer atraso que dure duas leituras.

**A cópia conferida com nome provisório.**

- Funciona. A cópia cortada no meio nunca deixa o nome certo, e o pedaço é apagado e conferido.
- A cópia é lida de volta e a soma comparada. O .msi da pasta de saída é comparado com o feito no rascunho.
- Desliguei cada uma dessas partes e o teste dela falhou.
- Ressalva: "lida de volta do disco" é lida do que o Windows ainda guarda na memória. O código não força a gravação
  no disco antes de trocar o nome (achado 11).

**A recusa do .bat e do .cmd, tentando passar por ela.** Rodei de verdade (`anexos-3/e1-lote-resultado.txt`):

| Jeito de chamar | O Windows roda pelo cmd.exe? | A peça recusa? |
|---|---|---|
| `a.bat`, `b.CMD`, `a.bat ` (espaço no fim) | sim | sim |
| `a.bat.`, `a.BaT. .` (ponto no fim) | não (sai com código 1) | sim |
| nome curto `NOME-B~1.BAT` (de `nome-bem-comprido.batch`), `OUTRO-~1.CMD` | sai com código 0, sem o lote escrever a marca | sim |
| `c.batx`, `d.cmdfoo`, `e.bat1`, `f.btm`, `.batch`, `.cmdx` | não (erro 193) | sim |
| arquivo sem extensão que começa com texto | não (193) | sim |
| `g.com` que não é programa | não (216) | sim |
| `.ps1`, `.vbs`, `.js`, `.txt` | não (193) | sim |
| atalho `.lnk` para o cmd.exe | não (193) | sim (rodar e grupo) |
| lote que começa com "MZ", com `.bat`, `.batx` ou `.cmdx` | não (216) | `.bat`: sim; os outros: não, e o Windows também não roda |
| só o nome `a` (`PATHEXT`), `a.bat` | não acha (erro 2) | `a`: não; `a.bat`: sim |
| `a.bat::$DATA` | não (193) | sim |

- O `wscript` está na pasta do Windows: recusado pela pasta.
- Nada do que tentei roda pelo cmd.exe passando pela peça. A regra de olhar a coisa de verdade (a extensão do nome já
  completado pelo Windows, mais o começo do arquivo) segura o lote.
- O que passa é outra coisa: a **lista de nomes** da mesma função (achado 2). Também passa uma **cópia** do cmd.exe
  fora da pasta do Windows (achado 5).

**O programa que nasce parado e entra no grupo antes de ser solto.** Rodei de verdade (`anexos-3/e3-e4-resultado.txt`):

- Desliguei o "nascer parado" e o teste dele falhou.
- Um filho aberto com a bandeira de sair do grupo (`CREATE_BREAKAWAY_FROM_JOB`) **não saiu**. Ele estava entre os vivos
  do grupo e morreu no `fechar_tudo`.
- Um atalho `.lnk` é recusado também pelo grupo.
- O que não provoquei: um antivírus que injeta uma linha no programa parado. Pela leitura do código, isso faz o
  soltar devolver 0, e o programa é fechado com "não consegui soltar": falha segura, nunca solto fora do grupo.
- O que fica de fora do grupo, pela documentação: o que nasce pelo WMI. O outro escreveu isso. O vpk de verdade não
  foi aberto assim (é da prova à vista).

**A vigia única e o "motor-kraken-" num lugar só.**

- A regra da vigia mora num lugar só (`empacotar.vigia_do_espaco`), e os quatro usos a chamam: o vpk, a compressão do
  motor, a cópia e o download pelo gh.
- O que ficou em dois lugares é o laço "rodar um programa, olhar a vigia e fechar" (achado 8).
- Ficou de fora da vigia o download que o GitHub faz para somar um arquivo grande (achado 7).
- "motor-kraken-" só aparece escrito em `versao.py`. Procurei no código inteiro, fora os comentários. O que sobra é
  outra coisa: a pasta `motor-kraken\`, que é `core/ocr_kraken.NOME_DA_PASTA`.

**O que os consertos podem ter quebrado.** Rodei na cópia, um arquivo por vez (`anexos-3/arredor-um-arquivo-por-vez.txt`):

| Arquivo de teste | Resultado |
|---|---|
| `test_windows_peca.py` | 62 passaram, 2 pulados |
| `test_publicar_versao.py` | 49 passaram |
| `test_publicar_servidor.py` | 14 passaram |
| `test_publicar_motor.py` | 12 passaram |
| `test_empacotar.py` | 41 passaram |
| `test_windows_janela_de_prova.py` | 10 passaram |
| `test_decisoes_atualizacao.py` | 38 passaram |
| `test_decisoes_ajudante_da_atualizacao.py` | 37 passaram |
| `test_decisoes_testes_a_distancia.py` | 13 passaram |
| `test_decisoes_desinstalar.py` e `_pasta.py` | 25 e 5 falham, **também no código da volta 2 e no worktree**: não é deste passo (achado 12) |

- A rodada do GitHub 44675872042 deu success. Pelo registro dela, rodou o código de `2e906e94` (e `668192b4` na parte
  2, na segunda tentativa). Entre `e4263c0a` e esses dois só mudaram documentos e três explicações de função num
  teste: o código testado é o desta volta.
- Na peça do passo 1, há uma **regressão sem uso hoje**: os atalhos de aplicativo da Loja da Microsoft passaram a ser
  recusados com uma frase falsa (achado 6).
- O vpk de verdade do PC (`C:\Users\fotog\.dotnet\tools\vpk.exe`) começa com "MZ" e passa pela peça.
- O repositório não ficou raso: `--is-shallow-repository` = false antes e depois.

## Caminhos que o outro não listou

1. **O GitHub com a leitura atrasada por mais de uma vez** depois do liberar (achado 1).
2. **O nome do programa com ponto no fim**, na lista de nomes com função própria (achado 2).
3. **A leitura que falha depois de pedir para apagar** (achado 3).
4. **O rascunho recém-criado que a leitura ainda não acha** (achado 4).
5. **Uma cópia de um programa do Windows fora da pasta do Windows** (achado 5).
6. **Um atalho de aplicativo da Loja (WindowsApps)** passado ao rodar, ao lançar ou ao grupo (achado 6).
7. **A soma lida do GitHub quando ele não dá a soma pronta**: baixa o arquivo inteiro para o C: (achado 7).

## Falhas não pensadas e resultado não conferido

- **Resultado não conferido (F5):**
  - a decisão de apagar depende de quantas leituras estão atrasadas (achado 1);
  - "NÃO apaguei" depois de pedir para apagar (achado 3);
  - "foi apagada (conferido)" sem pedir nada (achado 4);
  - "lida de volta do disco" sem forçar a gravação (achado 11).
- **O vizinho passa (F2):** `pwsh.exe.` e `Update.exe.` (achado 2); a cópia do cmd.exe (achado 5).
- **Proteção sem teste, ou teste afinado ao código (F3):**
  - o teste do achado 1 imita exatamente uma leitura atrasada (achado 1);
  - a segunda olhada depois do PATH (achado 10).
- **O escrito não bate com o código (F7):** o caminho do teste do lote (achado 9) e "lida de volta do disco"
  (achado 11).
- **O teste supõe o computador (F4):** os testes do desinstalar no PC (achado 12, não é deste passo).
- **Peça duplicada (§11.12.1):** o laço de rodar com a vigia, em dois lugares (achado 8).
- **F1 (dado que o conferido troca) e F9 (mexer no que é do Samuel):** não achei caso novo. Nenhuma junção, nada
  mudou no Windows, o repositório não ficou raso.

## As regras que conferi

- **§11.12 (uma regra, um lugar):**
  - a recusa é uma função só para o rodar, o lançar e o grupo, e isso está cumprido;
  - dentro dela, o nome é lido de dois jeitos (achado 2);
  - a vigia é uma só; o laço que a aplica, não (achado 8).
- **§11.12.2 (nada dado como feito sem conferir):** falha nos achados 1, 3 e 4.
- **§11.12.3 (a lista das falhas):** faltam os caminhos 1 a 7 acima.
- **§11.12.6 e D-813 (tudo o que a peça de fora aceita):**
  - para o lote, cumprida, e rodada de verdade (pelo outro e por mim);
  - para a lista de nomes, não: o ponto no fim, que o próprio comentário da peça cita, não vale ali.
- **D-811 (cada proteção com o teste que falha sem ela):** cumprida nos 10 achados. Fica o teste afinado do achado 1
  e uma olhada sem teste (achado 10).
- **D-776:** a conta e a vigia pegam o motor baixado. Fica de fora o download para somar (achado 7).
- **D-795:** sem mudança nesta volta. O Setup.exe continua fora da lista do destino (conferido no código).
- **Decisão da gerente (depois de pedir para liberar, uma versão liberada nunca é apagada, D-014):**
  - cumprida na pasta das provas;
  - no GitHub, pela metade (achado 1).
- **D-798:** o ramo não tem rótulo de pronto.
- **D-809:** não criei junção.
- **CLAUDE.md §10.9 (apagar):** só apaguei o que eu criei, dentro da minha pasta de rascunho.

## Achados

1. **MÉDIO: no GitHub, duas leituras atrasadas depois de liberar fazem o publicar apagar a versão liberada.**
   - Onde (código `e4263c0a`): `publicar_versao_kaique.py:539`, `:509`, `:520` e `:617`; `tests/test_publicar_versao.py:955`.
     Nas funções `apagar_publicacao` (o caminho `so_rascunho`),
     `DestinoGitHub.apagar_rascunho`, `DestinoGitHub._pedir_para_apagar` e `publicar_arquivos` (o `except
     BaseException`). O teste é `tests/test_publicar_versao.py`, classe `_GitHubQueLiberaEPerdeAResposta`
     (`self.atrasadas = 1`).
   - O que acontece:
     - o liberar chega ao GitHub e a resposta se perde;
     - a leitura de `apagar_publicacao` e a de `apagar_rascunho` ainda dizem "rascunho";
     - o publicar pede para apagar, e sem `--cleanup-tag`, porque acha que é rascunho;
     - a versão liberada some e a frase diz "a publicação v9.9.9 foi apagada de o GitHub (dono/projeto) (conferido)".
   - O pior: a etiqueta `v9.9.9` fica no GitHub. O próximo publicar com o mesmo número não acha publicação nenhuma,
     cria outra e a libera nessa etiqueta. É exatamente o "número livre para outro conteúdo" que a decisão da gerente
     queria evitar.
   - Provado com o gh de mentira dos próprios testes, mudando só o atraso de 1 para 2 leituras
     (`anexos-3/testes_q.py.txt`, Q1; resultado em `anexos-3/testes_q-resultado.txt`).
   - Não sei se o GitHub de verdade atrasa duas leituras. O ponto é outro: o conserto funciona para o número de
     leituras que o código faz, e o teste imita esse número.
   - O que pedir (a gerente decide, porque mexe na decisão dela):
     - **(a) Sugestão:** depois de pedir para liberar, não apagar nada, em nenhum destino. Um rascunho no GitHub não
       aparece para o programa do Kaique. A frase diz exatamente o que ficou ("pode ter ficado liberada ou como
       rascunho; confira e, se for rascunho, apague com `--apagar`"). É uma regra só, sem depender de leitura.
     - **(b)** Manter como está, e escrever no plano que, no GitHub, a regra depende de a leitura estar em dia.
   - Com um teste que use dois ou mais atrasos.

2. **MÉDIO: a peça do Windows deixa rodar o PowerShell 7 e o atualizador do Velopack com um ponto no fim do nome.**
   - Onde: `core/windows.py:1118` e `core/windows.py:1040`. Em `_programa_com_funcao_propria` (a linha
     `if nome.removesuffix(".exe") in PROGRAMAS_COM_FUNCAO_PROPRIA`) e `_caminho_do_programa` (o `strip()` não tira o
     ponto do fim). Usada pelo `rodar_e_esperar`, pelo `lancar_solto` e pelo `abrir_em_grupo`.
   - O que acontece:
     - `pwsh.exe` é recusado, mas `pwsh.exe.`, `pwsh.exe..` e `Update.exe.` passam;
     - o Windows tira o ponto do fim e roda o `pwsh.exe` (CreateProcessW, pelo GetFullPathNameW);
     - a mesma função já tira o ponto para conferir o .bat e o .cmd (`os.path.abspath`), mas compara a lista de nomes
       pelo nome cru.
   - Provado de verdade, com um `pwsh.exe` de prova (uma cópia do `hostname.exe`) numa pasta minha: o rodar e o
     grupo rodaram `pwsh.exe.` e devolveram o nome do computador (`anexos-3/e2_nomes.py.txt`,
     `anexos-3/e2-nomes-resultado.txt`). O `pwsh.exe::$DATA` passa pela peça, mas o Windows não o roda.
   - Já existia no código da volta 2 (conferi: `pwsh.exe.` passava lá). Mas está na função que esta volta mexeu, e
     ela é "a regra única".
   - Família F2, de novo na peça do passo 1.
   - O que pedir: ler o nome **uma vez só**, já completado pelo Windows (o mesmo `abspath`, ou o `resolve`), e usar
     esse nome em todas as conferências da função: a lista, a pasta do Windows e o lote. Com um teste para
     `pwsh.exe.`, `pwsh.exe..` e `Update.exe.` no rodar, no lançar e no grupo.

3. **BAIXO-MÉDIO: a frase diz "NÃO apaguei" depois de ter pedido para apagar o rascunho.**
   - Onde: `publicar_versao_kaique.py:630` (`publicar_arquivos`, o ramo `except Parou as outro` com `pediu_para_liberar`).
   - O que acontece:
     - o liberar falha e o GitHub continua com o rascunho;
     - o apagar do rascunho dá certo;
     - a leitura de depois não responde (a rede caiu);
     - a frase diz "não deu para ler a situação agora ... NÃO apaguei", e o rascunho foi apagado.
   - Provado com o gh de mentira (Q2).
   - O que pedir: o apagar diz à frase se chegou a pedir. Se pediu: "pedi para apagar o rascunho e não deu para
     conferir se sumiu".

4. **BAIXO-MÉDIO: "foi apagada (conferido)" sem ter pedido nada, com o rascunho ainda no GitHub.**
   - Onde: `publicar_versao_kaique.py:550` (`apagar_publicacao`, o `if antes is None: return None`), `:620` (a frase
     de `publicar_arquivos`) e `:600` (o `criar_rascunho` fora do `try`).
   - O que acontece:
     - o rascunho acabou de ser criado;
     - o envio falha;
     - a leitura ainda não acha o rascunho (o mesmo atraso do achado 1);
     - o apagar entende "já sumiu", não pede nada, e a frase diz "foi apagada ... (conferido)";
     - o rascunho fica.
   - Provado com o gh de mentira (Q3).
   - Já era assim antes desta volta.
   - Também: o `criar_rascunho` fica fora do `try`. Se ele cria e a resposta se perde, nada é desfeito e a frase não
     diz que pode ter ficado um rascunho. O próximo publicar avisa ("sobrou um rascunho").
   - O que pedir: no caminho de erro, "não achei" logo depois de criar não é "sumiu". A frase diz "não achei o
     rascunho para apagar; confira com `--apagar`".

5. **BAIXO: uma cópia do cmd.exe (ou de qualquer programa do Windows) fora da pasta do Windows passa pela peça.**
   - Onde: `core/windows.py:1108` (`_programa_com_funcao_propria`): a regra é pela pasta.
   - Provado: `meu-cmd.exe` (cópia do `cmd.exe`) numa pasta minha rodou `/c echo` pelo rodar genérico
     (`anexos-3/e2-nomes-resultado.txt`).
   - É escolha da gerente no passo 1 ("a regra é pela pasta"). Só um código que copia um programa do Windows de
     propósito faz isso.
   - O que pedir (a gerente decide):
     - escrever como limite da peça;
     - ou comparar a coisa de verdade: o nome original gravado dentro do programa, ou quem assinou.

6. **BAIXO: regressão sem uso hoje: os atalhos de aplicativo da Loja são recusados com uma frase falsa.**
   - Onde: `core/windows.py:1104` (`_nao_e_programa_do_windows`, o `except OSError: return True`).
   - O que acontece:
     - o `winget.exe` e o atalho `python.exe` de `%LOCALAPPDATA%\Microsoft\WindowsApps` não deixam ler o começo do
       arquivo (erro 22);
     - a peça recusa com "este programa do Windows tem função própria na peça: use a função dela";
     - não existe essa função;
     - no código da volta 2, o `winget --version` rodava.
   - Nenhum chamador usa isso hoje. Pode aparecer nos passos 3 a 5.
   - O que pedir: uma frase própria ("não consegui ler o programa para saber se é um programa do Windows"), e a
     escolha escrita (recusar na dúvida está certo; a frase é que não).

7. **BAIXO: a soma lida do GitHub baixa arquivos grandes para o C: fora da conta e da vigia.**
   - Onde: `publicar_versao_kaique.py:462` e `:470`, `DestinoGitHub.soma` (baixa para
     `%TEMP%\publicar-soma-...` quando o GitHub não dá o "digest").
   - O que acontece: é o vizinho do achado 7 da volta 2. Sem o "digest", a leitura de volta baixa o pacote (uns
     460 MB), o .msi (uns 826 MB) e o motor, duas vezes (o motor é lido no começo e na conferência). Isso vai para o C:,
     sem a vigia e fora da conta.
   - As Ressalvas dizem "mais lento, ainda certo", e não falam do disco.
   - O que pedir: baixar para o rascunho com `baixar_vigiado` e a vigia, e contar. Ou escrever que, sem o "digest",
     o C: pode encher (D-776).

8. **BAIXO: o laço "rodar um programa, olhar a vigia e fechar" está em dois lugares.**
   - Onde: `empacotar.py:1424` (`rodar_vpk`, pela peça, num grupo) e `publicar_versao_kaique.py:391` (`DestinoGitHub._gh`, o
     `subprocess.Popen` direto, sem a peça nem o grupo).
   - O que acontece:
     - a regra da vigia é uma só;
     - o jeito de esperar, de fechar e de tratar o Ctrl+C foi escrito duas vezes, e cada um fecha de um jeito;
     - o gh continua rodando fora da peça, como as Ressalvas já dizem ("duas peças de conversa com o GitHub").
   - O que pedir: a gerente decide se o gh passa pela peça (o `abrir_em_grupo` já faz o laço), ou se fica escrito
     como está.

9. **BAIXO: o teste do lote que não se acha usa um caminho escrito errado.**
   - Onde: `tests/test_windows_peca.py:1354`, `test_um_lote_que_a_peca_nao_acha_tambem_e_recusado_pela_extensao`
     (`"C:\nao\existe.bat"` num texto comum).
   - O que acontece:
     - o `\n` vira uma quebra de linha, e o caminho testado não é o escrito;
     - o `\e` dá o aviso "invalid escape sequence" (são os 3 avisos da rodada do arquivo);
     - o Python diz que isso vai virar erro no futuro, e aí o arquivo inteiro deixa de rodar.
   - Hoje o teste ainda cobra a extensão: a mutação que tira a extensão faz ele falhar.
   - O que pedir: texto cru (`r"C:\nao\existe.bat"`).

10. **BAIXO: uma olhada da peça sem teste, que não achei como alcançar.**
    - Onde: `core/windows.py:1141` (`_programa_com_funcao_propria`), o `or _nao_e_programa_do_windows(caminho)` do fim
      (depois de achar o nome pelo PATH).
    - Desliguei: os 62 testes da peça passam.
    - Não achei um caso em que ela importe. O nome sozinho que vira `.BAT` pelo `PATHEXT` o Windows não roda (ele
      procura `.exe`), e o atalho para um lote a primeira olhada já pega.
    - O que pedir: um teste, ou a explicação de que é em dobro na seção "Cada proteção".

11. **BAIXO: "lida de volta do disco" não força a gravação no disco.**
    - Onde: `empacotar.py:1363` e `empacotar.py:1416` (`copiar_inteiro`: lê de volta e troca o nome com `os.replace`, sem `os.fsync`).
    - O que acontece:
      - a leitura vem do que o Windows ainda guarda na memória;
      - se o HD externo sair ou a luz cair logo depois, o arquivo pode ficar com o nome certo e o conteúdo pela
        metade.
    - O programa do Kaique confere a soma assinada e recusaria esse pacote. O .msi da pasta de saída, não.
    - O que pedir: `os.fsync` da cópia antes de ler de volta e de trocar o nome, ou corrigir o texto.

12. **OBSERVAÇÃO (não é deste passo): dois arquivos de teste do desinstalar falham no PC.**
    - Onde: `tests/test_decisoes_desinstalar_pasta.py:96` (a proteção do teste); `tests/test_decisoes_desinstalar.py`
      (25 falham) e `tests/test_decisoes_desinstalar_pasta.py` (5 falham).
    - Falham igual no worktree do passo 2 e no código da volta 2.
    - A proteção do próprio teste recusa qualquer "C:\" no comando, e no PC a pasta temporária fica no C:. No GitHub
      ela fica no D:, e eles passam.
    - É a família F4. Para a Lista de bugs.

## O que falta para a prova à vista

1. Quem escreveu consertar os achados 1 e 2, cada um com o teste que falha sem o conserto. O 1 precisa antes da
   escolha da gerente, (a) ou (b). De preferência também os achados 3, 4, 6 e 9.
2. Ou a gerente decidir levar à prova com eles escritos. O roteiro da prova não passa pelos achados 2 a 12. O
   achado 1 só aparece se a leitura do GitHub atrasar, o que a prova não provoca.
3. Uma rodada do GitHub sobre o conserto, e outro agente novo para conferir (D-815).
4. Na prova à vista, item 8 do roteiro: depois do `--apagar`, conferir também que a etiqueta sumiu do GitHub (as
   etiquetas do repositório), não só a publicação.

## Para a gerente: o que ficou fora do projeto

- Na pasta de rascunho desta conversa
  (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\v3\`)
  deixei:
  - as cópias do código: `novo\` (`e4263c0a`) e `velho\` (`9cd555a5`, com os três arquivos de teste novos copiados
    por cima);
  - as pastas das experiências `casos1\` a `casos4\`, com os lotes, o atalho `.lnk`, o `pwsh.exe` e o `Update.exe`
    de prova (cópias do `hostname.exe`) e a cópia do `cmd.exe`;
  - os scripts.
  - Não apaguei nada.
- Os processos de prova que abri foram fechados.
- Nenhuma junção foi criada. Nada mudou no Windows: nenhuma tarefa, licença, pergunta de administrador ou janela. O
  atalho `.lnk` foi escrito como arquivo, pelo próprio Windows, dentro de `casos3\`.
- Consultei o GitHub duas vezes, para a situação da rodada 44675872042 e o registro dela. O repositório não ficou
  raso.
- No projeto, só escrevi este relatório (três formatos) e a pasta `quem-quebrou/anexos-3/`.
