# Passo 2 do plano da parte do Windows: primeira conferência de quem tentou quebrar (19/11/2026)

Sou o verificador que tenta quebrar o passo 2 (D-775): publicar, o motor do Kraken à parte e o servidor das versões
de prova. Não escrevi este código e não mexi nele. Não rodei o vpk, o PyInstaller nem o GitHub de verdade, não publiquei
nada, não pedi licença de administrador e não abri janela na tela do Samuel.

## Pedido

- Papel: verificador
- Commit de partida: e5f4eabe
- Ramo: passo2-publicar-2026-11-19

## Arquivos que vou mexer

- `relatorios/passo2-publicar/quem-quebrou/`

## Veredito

**NÃO ESTÁ PRONTO para a prova à vista no GitHub.** Quando o publicar apaga um rascunho no GitHub, ele vai dizer
"o GitHub não deixou apagar", mesmo tendo apagado (achado 1). Isso aparece exatamente nos dois momentos da prova
em que o Samuel olha o GitHub: o erro de propósito e a limpeza do fim. Os testes não pegam, porque o GitHub de
mentira deles sempre consegue apagar.

A parte da pasta e do servidor das versões está bem feita. Tentei quebrar o servidor pelos três pontos do foco (a porta
só dele, o rascunho que não aparece, fechar no meio de um download) e ele aguentou todos. A D-809 aguentou cinco casos
com junções de verdade.

Há mais três achados médios:

- a vigia do espaço fecha o vpk, mas não o programa que ele abre para fazer o .msi (achado 2);
- nove proteções não têm teste que falhe sem elas, entre elas a conferência da assinatura lida de volta, que é do foco
  (achado 3);
- a resposta à pergunta do outro: não é certo apagar uma versão já liberada e conferida só porque a leitura de
  confirmação falhou (achado 4).

Não escrevo "PRONTO PARA CONFERIR" (D-798): falta o conserto do achado 1 e a prova à vista.

## O que li

- `.claude/agents/verificador.md`, o `CLAUDE.md` inteiro, `memoria/INDICE.md` e `memoria/catalogo-de-erros.md`
  (famílias F1 a F5 e F9).
- O meu pacote (`anexos/pacote-quem-quebra.md`), o formulário do outro (`ONDE-PAREI.md`) e os três anexos de reversão.
- O plano v3 (worktree `plano-windows`): "Regras de todos os passos", passo 2 e as peças 8, 9 e 10.
- O modelo do relatório do passo 1 (`relatorio-1.md` de quem quebrou, worktree `passo1`).
- O código: `publicar_versao_kaique.py` inteiro, `servidor_das_versoes.py` inteiro, a parte nova de `empacotar.py`
  (linhas 1090 a 1650 e `construir_pasta`), e as mudanças de `core/windows.py`, `core/ocr_kraken.py`,
  `montar_motor_kraken.py` e `versao.py` (o diff de 03c91599 a 0ef0da17). Mais `atualizacao.Fonte` e os testes novos.
- **O código do vpk 1.2.161** (a cópia do outro, `saida_teste\publicar-rapido\fonte-velopack\repo`), lido por mim:
  `PackageBuilder.cs` 60-190 (a pergunta e a versão anterior), `DeltaMode.cs`, `DefaultName.cs` (os nomes),
  `MsiBuilder.cs` 186-221 e `Exe.cs` 41-66 (como o .msi é feito).
- **O código do Velopack do lado do programa:** `lib-rust/src/sources/github.rs` 77-137 e `mod.rs` 112-144 (como o
  programa acha as versões no GitHub), `manager.rs` 412-459 e 537-557 (como ele baixa e confere).
- **O código do `gh`** (cli/cli, ramo trunk, lido em 19/11): `release/delete/delete.go` (`deleteRun`, `deleteTag`),
  `release/shared/fetch.go` (como acha um rascunho, os campos de `--json`) e `release/download/download.go`.

## O que conferi nos campos de falhas, de peça de fora e de caminhos, e como

**Rodei no PC (só leitura do Windows, sem licença, tudo em pasta temporária minha):**

- Os três arquivos de teste novos, um por vez: `test_publicar_versao.py` 20 passaram; `test_publicar_motor.py` 12;
  `test_publicar_servidor.py` 11.
- **O servidor, sem janela, numa pasta minha:**
  - Uma conexão aberta que não manda nada (como faz um navegador): fechar levou 0,11 s.
  - Quem baixa para de ler no meio de um arquivo de 30 MB: fechar levou 0,03 s.
  - Fechar no meio de um download com o limite de velocidade: quem baixava recebeu o erro "download incompleto"
    (4 de 31 MB), e a janela escreveu "CORTADO no meio".
  - A porta: um segundo servidor nosso na mesma porta é recusado. Outro programa já em 127.0.0.1 na mesma porta:
    recusado. Outro programa em "todos os endereços" (0.0.0.0): o nosso abre e quem atende o 127.0.0.1 é o nosso. Não
    é defeito.
  - Eu esperava que a conexão parada travasse o fechar. Não travou: o Python 3.14 não espera os fios de atendimento.
- **A D-809, com junções de verdade** (criadas com `mklink /J` na minha pasta; as que sobraram tirei com
  `cmd /c rmdir`, e o outro lado continuou inteiro):
  - (a) a publicação da pasta de destino é uma junção: o apagar para, diz que é atalho, e o outro lado fica inteiro.
    Pela linha de comando (`--apagar`), devolve 1 com "PAREI".
  - (b) uma publicação de verdade com uma junção dentro: a publicação some, e o outro lado fica inteiro.
  - (c) o rascunho do C: com uma junção dentro: some, e o outro lado fica inteiro.
  - (d) um rascunho velho que é junção: não é apagado.
  - (e) o script lançado solto cria duas junções na própria pasta de troca (uma dentro de subpasta) e apaga a pasta no
    fim: a pasta some, e o outro lado fica inteiro.
- **A lista de módulos do PowerShell 7 (o conserto na peça do passo 1).** Testei os 20 comandos que os scripts da
  peça usam, entre eles o Agendador, as licenças de pasta e a assinatura. Todos carregam com o ambiente da peça,
  inclusive com quatro módulos estragados do PowerShell 7 na frente da lista.
  - O caminho com licença abre o próprio programa (`pedir_licenca` → `_abrir_com_licenca`), e ele roda os scripts
    pela mesma `rodar_powershell`. Então o conserto vale lá também.
  - **Não rodei com licença.**
- **A corrida do lançar solto** (o defeito que o outro anotou): um script vazio, 15 vezes. Deu "o processo lançado
  saiu sem começar" 4 vezes, mesmo tendo rodado.
- **Mutações minhas** numa cópia (`git archive` de 0ef0da17, na minha pasta temporária): 16 proteções que o outro não
  desligou. A cópia limpa passa nos cinco arquivos (122 testes). O resultado está no achado 3 e no fim deste relatório.
  - Aviso, por honestidade: cada mutação rodou cinco arquivos de teste juntos no PC, contra a regra de um arquivo por
    vez (D-807). Foram uns 17 segundos por mutação.
- Conferências de um trecho só:
  - a conferência do pacote da atualização com o arquivo do motor em `instalar\`: aceita (achado 8);
  - o servidor com o .msi em duas versões: entrega o da primeira pasta (achado 7);
  - o publicar com o lugar do rascunho ocupado por um arquivo: o erro sai cru (achado 5).

**Lido nas peças de fora:**

- **"O vpk roda mesmo sem a diferença":** confere. A versão anterior só é procurada na pasta de saída
  (`PackageBuilder.cs:66` e `:119`). A diferença só é feita com `prev != null && DeltaMode != None` (`:165`). Com a
  pasta de saída sempre nova, ele não pergunta nada (`:67-73`).
- **Os nomes que o publicar supõe** (`<id>-win-Setup.exe`, `<id>-win.msi`, `-full.nupkg`): batem com `DefaultName.cs`.
  O .msi não leva a versão no nome (isso pesa no achado 7).
- **O .msi é feito por outro programa:** `MsiBuilder.CompileWixMsi` chama `Exe.RunHostedCommand`, que abre
  `cmd.exe /S /C "wix.exe build ..."` (achado 2). O formulário dizia "deduzido, não lido": agora está lido.
- **O programa do Kaique e o GitHub:**
  - O programa pede ao GitHub as 10 publicações mais recentes, sem conta (`github.rs:80`). Rascunho não aparece para
    quem não entra com conta, conforme a documentação do GitHub.
  - Ele junta o índice de cada publicação e pula as que não têm índice (`mod.rs:119-141`). A publicação do motor não
    atrapalha.
  - Ele baixa num arquivo ".partial", confere a soma SHA-256 e só depois troca o nome (`manager.rs:412-459`). Um
    download cortado nunca parece inteiro.
- **O gh:**
  - `release view` acha o rascunho pela etiqueta (GraphQL, `fetch.go`), e `digest` é campo dos arquivos. Confere com
    o formulário.
  - `release delete --cleanup-tag` apaga a publicação e **depois** apaga a etiqueta, sem olhar se é rascunho, e
    devolve o erro dessa segunda parte (`delete.go`, `deleteRun` e `deleteTag`). Achado 1.

**Os campos do formulário:**

- "O que pode falhar": faltam três casos:
  - o apagar do rascunho no GitHub;
  - o vpk fechado à força com o WiX rodando;
  - erro do disco que não é `Parou`.
- "De onde vem cada dado": confere. Os dois dados que o próprio conferido escreve (a ficha da pasta e a do motor)
  estão marcados como não-prova.
- "Caminho e função": confere. O vpk roda num lugar só (`rodar_vpk`), o GitHub num lugar só (`DestinoGitHub._gh`) e a
  assinatura do Windows pela peça.

## Caminhos que o outro não listou

1. Apagar uma publicação que ainda é rascunho no GitHub (`--cleanup-tag` sem etiqueta). É o caminho de todo erro antes
   de liberar, e do `--apagar` de um rascunho.
2. Os programas que o vpk abre (o `cmd.exe` e o `wix.exe` do .msi), quando a vigia fecha o vpk.
3. O mesmo nome de arquivo em duas publicações da pasta (o .msi), quando o servidor junta tudo numa lista só.
4. Uma publicação da pasta que é junção: o servidor a serve, e o apagar a recusa. A regra do que é publicação está em
   dois lugares.
5. Os erros do disco que não viram `Parou` (o rascunho que não cria, o arquivo preso ao somar, a cópia do .msi depois
   de publicar).

## Falhas não pensadas e resultado não conferido

- **Resultado não conferido (F5):**
  - `apagar_publicacao` trata o erro do gh como "não apagou" sem ler de volta (achado 1).
  - `rodar_vpk` diz "parei" e não confere se sobrou programa escrevendo no C: (achado 2).
- **Peça de mentira que esconde (F4):** o gh de mentira apaga sempre (`tests/test_publicar_versao.py`,
  `_GitHubDeMentira`, `sub == "delete"`), por isso o achado 1 passou.
- **Proteção sem teste (F3):** nove (achado 3).
- **F1 (dado que o conferido pode trocar):** não achei. O motor e a assinatura vêm do destino, e a soma do GitHub é a
  que o GitHub calcula.
- **F9 (mexer no que é do Samuel):** o formulário já avisa do `--so-ficha` na pasta de ferramentas dele. O rascunho
  fica em `%LOCALAPPDATA%\EditorImpressao-publicar` e só apaga pastas com o nome do publicar, nunca junção. Conferido
  no caso (d).

## As regras que conferi

- **§11.12.1 (uma peça por conversa):** cumprida para o vpk, o gh e a assinatura. Fechar o vpk junto com os filhos é
  conversa com o Windows: o conserto do achado 2 deve ir para a peça.
- **§11.12.2 (nada dado como feito sem conferir):** falha no sentido contrário no achado 1 ("não apagou" sem ler).
- **§11.12.3 (a lista das falhas):** faltam os três casos acima. O achado 5 contraria "sempre um aviso em português".
- **§11.12.4 e D-767 (peça de mentira não prova):** o gh de mentira escondeu o achado 1.
- **§11.12.6 (ler a peça de fora):** o vpk foi bem lido. O apagar do gh não foi.
- **D-811 (cada proteção com o teste que falha sem ela):** nove sem teste (achado 3).
- **D-776:** a conta para antes do vpk e a vigia para durante. Mas no .msi a vigia não para quem escreve (achado 2).
- **D-795:** o Setup.exe nunca está na lista do destino. A lista do destino é conferida exata, e o Setup.exe é apagado
  logo depois do vpk. A conferência do fim, porém, nunca foi testada acusando (achado 3, N6).
- **D-790:** a conferência do motor no começo tem teste. A de antes de liberar não tem (achado 3, N4).
- **D-789 e D-777:** conferidas pela leitura do vpk e pela mutação M13 do outro.
- **D-773:** o servidor aguentou, e o rascunho não aparece (servidor e GitHub).
- **D-809:** cumprida nos cinco casos.
- **D-798:** o ramo do outro não tem rótulo de pronto.

## Achados

1. **MÉDIO, impede a parte do GitHub da prova à vista: apagar um rascunho no GitHub sempre acaba em "o GitHub não
   deixou apagar", mesmo apagado** (`publicar_versao_kaique.py`, `DestinoGitHub.apagar`, que roda
   `release delete <etiqueta> --yes --cleanup-tag`; `apagar_publicacao`).
   - O que li no gh:
     - o `deleteRun` apaga a publicação e, com `--cleanup-tag`, apaga em seguida a etiqueta `refs/tags/<etiqueta>`,
       sem olhar se é rascunho;
     - o `deleteTag` devolve o erro do GitHub, e o gh sai com erro;
     - num rascunho a etiqueta ainda não existe: o GitHub só a cria ao liberar, e o próprio `fetch.go` chama isso de
       "pending tag".
   - Não rodei contra o GitHub: o pedido proíbe. É leitura do código, não medida.
   - O que acontece:
     - Todo erro antes de liberar (internet caindo no envio, soma que não bate) apaga o rascunho e escreve "ATENÇÃO:
       o GitHub não deixou apagar ...; apague com --apagar".
     - Rodar o `--apagar` de um rascunho dá "PAREI" e sai com 1, embora tenha apagado.
     - O `apagar_publicacao` levanta o erro antes de ler de volta.
   - Na prova (itens 5 e 8 do roteiro), o Samuel veria a tela dizer o contrário do que aconteceu.
   - O que pedir:
     - ler de volta sempre (se a publicação não existe mais, está apagada, venha o gh com erro ou não);
     - num rascunho, não pedir a etiqueta (ler a situação antes);
     - o gh de mentira imitar esse erro, com um teste que falhe no código de hoje.

2. **MÉDIO: a vigia do espaço fecha o vpk, mas o programa que faz o .msi continua escrevendo no C:**
   (`empacotar.py`, `rodar_vpk`: `processo.kill()`).
   - O que li no vpk: o .msi sai de `cmd.exe /S /C "wix.exe build ..."` (`MsiBuilder.cs:216-221`, `Exe.cs:46-65`). O
     `kill` do Python fecha só o vpk.
   - No passo do instalador (o que mais escreve), se o disco cair abaixo de 20 GB, o WiX continua gravando o .msi em
     `rascunho\temp`. O C: desce abaixo da reserva, pelo tamanho do .msi (hoje uns 0,8 GB, pelo estudo citado no
     formulário).
   - O rascunho não sai enquanto o WiX segura os arquivos. A frase "não saiu inteiro" aparece, e isso está certo, mas
     a reserva da D-776 foi furada.
   - O que pedir: fechar o vpk junto com os programas que ele abriu (um grupo de processos do Windows que fecha tudo
     junto). É conversa com o Windows, então vai na peça (§11.12.1).
   - Não dá para provar sem o vpk de verdade. Na prova, vale conferir no Gerenciador de Tarefas que nada sobrou depois
     do erro de propósito.

3. **MÉDIO: nove proteções do publicar não têm teste que falhe sem elas** (D-811). Desliguei cada uma numa cópia, e
   os 122 testes dos cinco arquivos do passo continuaram passando:
   - **N14:** a assinatura da versão lida de volta do destino não é conferida (`_conferir_versao_lida`,
     `if motivo is not None`). É o foco do plano ("nada liberado antes da assinatura lida de volta"). O teste
     `test_d53` cobra só a ordem. Hoje a soma de cada arquivo (testada) e a assinatura conferida em casa cobrem por
     tabela.
   - **N4:** o motor não é lido de novo antes de liberar (D-790, `de_novo != motor`). O formulário diz que `test_d53`
     prova isso: não prova.
   - **N3:** o índice lido de volta (`releases.win.json` apontando para o pacote publicado).
   - **N6:** a conferência do fim nunca acusa o Setup.exe. Só o caminho "não está" é testado, e é a tela que a D-795
     manda mostrar.
   - **N5:** o `--apagar` não confere que sumiu (`apagar_publicacao`).
   - **N1:** a lista lida do destino ("nada a mais").
   - **N8:** o .msi vai para a pasta de saída antes de a versão sair.
   - **N10:** o Ctrl+C não fecha o vpk.
   - **N13:** o servidor serve através de junção (ver o achado 7).
   - Acusadas, para comparar: N2 (soma), N7 (motor-exigido.json com a soma errada), N9 (o arquivo do motor que sobra
     em `instalar\`), N11 (o .msi contado 3 vezes), N12 (apagar o rascunho recente de outro), N15 (a vigia).

4. **MÉDIO, é a pergunta do outro ("isso é certo?"): se a leitura logo depois de liberar falhar, o publicar apaga uma
   versão já liberada e já conferida** (`publicar_arquivos`, o `except BaseException` envolve também o `liberar` e a
   leitura de depois).
   - Minha opinião: não é certo. Quando o `liberar` foi pedido, tudo já tinha sido lido de volta e conferido. A
     versão está inteira, não "pela metade".
   - Apagá-la é que cria risco: o número da versão fica livre para ser publicado de novo com outro conteúdo. Um
     programa que tenha pegado a primeira naqueles segundos nunca pega a segunda, porque tem o mesmo número (contra o
     "um número de versão só" da peça 8).
   - O que pedir:
     - só apagar se a leitura disser que ainda é rascunho;
     - se não der para ler, dizer "liberada; não deu para reconferir" e parar, sem apagar.
   - Fica para a gerente decidir, porque mexe no "nunca pela metade" do plano.

5. **BAIXO-MÉDIO: erro do disco sai como tela de erro do Python, não como frase** (`publicar_versao_kaique.main`, que
   só pega `Parou` e `KeyboardInterrupt`).
   - Demonstrei com o lugar do rascunho ocupado por um arquivo: `FileExistsError` cru, fora do `Parou`.
   - O mesmo vale para:
     - o arquivo preso pelo antivírus ao somar no destino pasta (`DestinoPasta.soma`);
     - a cópia do .msi para a pasta de saída depois de publicar;
     - as cópias de `preparar_saida`.
   - O `finally` ainda apaga o rascunho: nada fica pela metade, só a frase falta (§11.12.3).

6. **BAIXO-MÉDIO, pesa no passo 3: o lançar solto diz "saiu sem começar" para um script curto que rodou**
   (`core/windows.py`, `_lancar_solto` e o fim do script de `lancar_powershell_solto`).
   - O outro já anotou o defeito. A minha medida: 4 de 15 com um script vazio.
   - É uma falha dita para uma coisa que aconteceu. Quem chamar no passo 3 e tentar de novo faz a coisa duas vezes.
   - Sugiro consertar antes do passo 3: o sinal de vida fora da pasta que o script apaga, ou a peça olhar o código de
     saída junto.

7. **BAIXO: o servidor entrega o .msi de outra versão** (`servidor_das_versoes.py`, `Versoes.achar`).
   - O .msi tem o mesmo nome em todas as versões (`EditorImpressaoPrograma-win.msi`). O servidor junta tudo numa lista
     só e entrega o da primeira pasta em ordem de nome. Demonstrado: com `v1.2.0` e `v1.10.0`, entregou o da `v1.10.0`.
   - O cabeçalho diz "os nomes já trazem a versão, então não se repetem": para o .msi, não é verdade.
   - E `publicacoes` pula atalho de arquivo, mas não junção, enquanto `DestinoPasta.apagar` recusa os dois.
   - Hoje o programa não baixa o .msi; por isso é baixo.

8. **BAIXO: a conferência do pacote da atualização aceita o arquivo do motor em `instalar\`**
   (`empacotar.proibidos_no_pacote_do_velopack`, que só proíbe `motor-kraken/`).
   - `SAIDAS` diz que a atualização não leva o motor em `instalar\`, mas a regra do proibido não lê esse campo.
     Demonstrado: o pacote com `instalar/motor-kraken-1.zip` passa.
   - Hoje quem tira o arquivo é `preparar_saida`, e isso tem teste (N9 acusada). Fica uma camada só.

9. **BAIXO: a conta do espaço com o .msi pode ficar curta em 1 a 2 GB.** O arquivo do motor já é comprimido e não
   encolhe nas cópias do vpk, e o WiX monta os pedaços do .msi antes de juntar.
   - Pela minha leitura, com a pasta de 1,3 GB e o motor de 0,8 GB, o pico é de uns 13,7 GB. A conta dá 12,8 GB.
   - A vigia cobre, a não ser pelo achado 2. Medir na prova (item 6 do roteiro).

10. **BAIXO, transparência: a reversão do D-809 no lançar solto é só pelo texto do script.**
    - O próprio teste diz que o apagar antigo não entrava na junção neste Windows. O "M18 acusada" do formulário vem
      da conferência do texto (`-Recurse`, `ReparsePoint`), não do comportamento. A seção "Cada proteção" não diz isso.
    - O comportamento novo está certo: provei com duas junções.

11. **BAIXO: `ETIQUETA_ACEITA` aceita uma etiqueta com quebra de linha no fim.** O `$` do Python casa antes do último
    `\n`: `"v1.2.0\n"` passa. Usar `fullmatch`. Não achei caminho de hoje que leve a isso.

## O que falta para a prova à vista

1. O outro consertar o achado 1, com o gh de mentira imitando o erro e um teste que falhe no código de hoje. De
   preferência também o 2 (pela peça) e os testes do 3 (N14, N4 e N6 primeiro, que são do foco).
2. A gerente decidir o achado 4.
3. Nova rodada do GitHub sobre o commit do conserto, e eu (ou outro verificador) conferir o conserto.
4. A prova à vista pelo roteiro do formulário. No erro de propósito, olhar também o Gerenciador de Tarefas (achado 2) e
   a frase do apagar no GitHub (achado 1).

A parte da pasta e do servidor (itens 1 a 4 do roteiro) não depende dos achados 1 e 4. Pode ir à prova antes, se a
gerente quiser dividir.

Só depois disso, e com cada achado com destino, cabe "PRONTO PARA CONFERIR" (D-798). Nunca "aprovado": só o Samuel
aprova.

## Para a gerente: o que ficou fora do projeto

- Na pasta de rascunho desta conversa
  (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\q2\`)
  deixei:
  - a cópia do código (`limpa\`, `mut2\`, `mut3\`);
  - as pastas das experiências (`qq-*`);
  - os scripts `servidor_casos.py`, `juncoes.py`, `juncao_e.py`, `modulos.py`, `minhas_mutacoes.py`,
    `pacote_com_motor.py` e `erro_cru.py`.
  - Não apaguei nada disso.
- Todas as junções foram criadas dentro dessa pasta. As que o próprio código não tirou, eu tirei com
  `cmd /c rmdir`, e o outro lado continuou inteiro (conferido; `dir /AL /S` não acha mais nenhuma).
- O repositório não ficou raso (`--is-shallow-repository` = false antes e depois). O ramo não mudou além deste
  relatório.
- Nada mudou no Windows: nenhuma tarefa, nenhuma licença, nenhuma pergunta de administrador, nenhuma janela na tela.
  O servidor só abriu portas em 127.0.0.1, dentro dos meus scripts, e fechou.
- Consultei a rodada 44650408369 uma vez: success na segunda tentativa, com o "Porteiro (juiz da versao de teste)" em
  success.
