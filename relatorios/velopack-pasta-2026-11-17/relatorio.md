# Prova: onde a peça de atualização (Velopack) grava no notebook do Kaique

17/11/2026, verificador. Investigação: nenhuma linha do programa mudou, nada foi consertado.
Cópia `.claude\worktrees\velopack-pasta`, ramo `velopack-pasta-2026-11-17`.

## A resposta em uma frase

**Sim: no notebook do Kaique, toda vez que ele abrir o programa, a peça de atualização vai gravar dentro da pasta dos
projetos dele** (uma pasta `packages` e uma cópia do `Update.exe`, uns 4 MB). E achei um risco maior, que ninguém
tinha visto: **o desinstalador apaga a pasta `%LOCALAPPDATA%\<nome do pacote>` inteira**. No teste, ele apagou o
projeto de mentira que estava lá dentro. O nome do nosso pacote é `EditorImpressao`, que é o mesmo nome da pasta dos
projetos.

- **É defeito do programa**, não escolha do Samuel. Vem de o nome do pacote ser igual ao nome da pasta dos projetos.
- **Situação:** só achado. O programa ainda não foi instalado em lugar nenhum: nem no notebook do Kaique, nem no PC do
  Samuel. Por isso ainda dá para consertar sem mexer em nada instalado.
- **Até o conserto, a etapa 5 não pode instalar e desinstalar o programa de verdade no PC do Samuel.** A pasta de
  projetos dele estaria em risco (ver "Desinstalar").

## Como a prova foi feita

- Montei um programa de mentira, `ProvaPasta.exe`. Ele não abre janela nem console. O nome do pacote é
  `EditorImpressaoProvaPasta` (nunca `EditorImpressao`). Ele leva o `atualizacao.py` de verdade e chama as mesmas
  funções que o programa chama ao abrir e que o ajudante chama ao atualizar.
- Por segurança, só isto foi trocado dentro dele:
  - as pastas que o nosso código lê pela variável foram para pastas de mentira no D:;
  - as tarefas do Windows ganharam nome de mentira;
  - a peça que fala com o Windows nos testes à distância foi trocada por uma que só anota;
  - não mexe no Visual C++ nem no Inno;
  - a assinatura usa uma chave de mentira (a do Samuel não foi usada);
  - nunca pede ao Velopack para trocar a pasta.
- Empacotei com o `vpk` 1.2.161, o mesmo do projeto: versões 1.0.0 e 1.0.1, um `.msi` "por usuário", sem atalhos.
  Esse `.msi` instala sem administrador. A instalação foi calada (`msiexec /qn`), numa pasta do D:.
- **Caso A, pasta trancada:** tirei da minha conta o direito de criar arquivos na raiz da instalação
  (`icacls /deny`, sem administrador). É o que acontece com o Kaique em Arquivos de Programas.
- **Caso B, pasta aberta:** a mesma pasta, com a permissão devolvida.
- Depois de cada chamada, uma "foto" (`provas\foto.py`, só lê) da pasta de reserva esperada e da pasta instalada.
  A foto também mostra os nomes do primeiro nível de `%LOCALAPPDATA%\EditorImpressao`, só para conferir que nada mudou
  ali.
- Nenhuma pergunta do Windows apareceu. Nenhuma janela foi aberta.

## O que vi rodando (máquina)

### Caso A: pasta da instalação trancada (como Arquivos de Programas para o Kaique)

O Velopack avisa "Failed to open directory for writing `...\instalado-trancado\.velopack_dir_test`: Acesso negado"
(`provas\A4-avisos-do-velopack.txt`). Depois disso, grava em **`C:\Users\fotog\AppData\Local\EditorImpressaoProvaPasta\`**.
Esse é o LocalAppData do Windows, e não a variável `LOCALAPPDATA`: o programa de mentira recebeu a variável trocada
para o D:, e nada foi parar lá (foto, item 5). Apaguei a pasta de reserva antes de cada chamada, para saber qual
chamada a cria:

| Chamada (a mesma do programa) | Quando o programa faz | O que apareceu em `...\Local\EditorImpressaoProvaPasta` |
|---|---|---|
| `velopack.App().run()` (`_rodar_o_velopack`) | **toda abertura**, antes da janela (`atender_linha_de_comando`) | `Update.exe` (3.979.264 bytes) e `packages\` vazia |
| `versao_que_roda()` | toda abertura (`trocar_antes_de_abrir`) e o aviso de versão nova | o mesmo |
| `e_portatil()` | toda abertura (`trocar_antes_de_abrir`, `procurar_ao_abrir`) | o mesmo |
| `procurar_ao_abrir()` | toda abertura (o aviso liga o ajudante) | o mesmo |
| `--procurar-atualizacao` (o que o ajudante faz: procurar, conferir a assinatura, baixar) | se rodasse na conta do Kaique | `Update.exe`, `packages\.betaId`, `packages\.velopack_lock` e **`packages\EditorImpressaoProvaPasta-1.0.1-full.nupkg` (19,8 MB)** |

Fotos: `provas\A1-...txt` a `provas\A4-...txt`. Na pasta instalada não foi gravado nada.

### Caso B: pasta da instalação aberta (como o ajudante, que roda como o sistema)

As mesmas chamadas **não** criaram a pasta de reserva. A versão baixada foi para
`...\instalado-trancado\packages\EditorImpressaoProvaPasta-1.0.1-full.nupkg`, dentro da pasta do programa
(`provas\B-aberta-tudo.txt`). É o mesmo que o ensaio de 16/11 mostrou ("writable: true").

### Desinstalar (o `.msi` por usuário, sem administrador)

- **C1 (pasta trancada):** antes de desinstalar, a pasta de reserva tinha a versão baixada. Pus ao lado um
  "projeto de mentira" (`projetos\livro-de-mentira\projeto.json`) e um `configuracoes.json`. Desinstalei com
  `msiexec /x /qn`. Depois, **`C:\Users\fotog\AppData\Local\EditorImpressaoProvaPasta` não existia mais: foi apagada
  inteira, com o projeto de mentira dentro** (`provas\C-depois-de-desinstalar.txt`).
- **C2 (pasta aberta, sem pasta de reserva):** instalei de novo e pus **só** o projeto de mentira em
  `...\Local\EditorImpressaoProvaPasta\projetos\`. Desinstalei. **Ele foi apagado de novo**
  (`provas\C2-desinstalar-so-com-projeto-de-mentira.txt`). Então quem apaga não depende da pasta de reserva: é o
  desinstalador que apaga `LocalAppData\<nome do pacote>`.
- **Quem apaga:**
  - o nosso gancho `ao_desinstalar` (D-731) só anotou e mandou a tarefa de mentira rodar (`provas\registro-do-app.txt`);
  - o registro do `.msi` mostra, depois do nosso gancho, a ação do Velopack `RustCleanup` → `CleanupDeferred`, que
    recebe `<pasta instalada>"EditorImpressaoProvaPasta"<Temp>`;
  - dentro do arquivo dessa ação no `vpk` 1.2.161 (`vendor\velopack_wix_x64.dll`) estão as frases `LOCALAPPDATA` e
    "Failed to remove local app data directory".

## O que é dedução (não vi rodando)

1. **A janela do Kaique grava em `%LOCALAPPDATA%\EditorImpressao\packages` e `%LOCALAPPDATA%\EditorImpressao\Update.exe`.**
   - Por que acredito: é a mesma regra do caso A, com o nome do nosso pacote (`EditorImpressao`) no lugar do de mentira.
     O código do Velopack monta o caminho como LocalAppData + id do pacote + `packages` (`locator.rs`).
   - Não testei com o nome de verdade, de propósito.
2. **Na conta do Kaique nada baixa para lá.** Quem baixa é o ajudante, que roda como o sistema e consegue gravar em
   Arquivos de Programas (caso B). Só baixaria na conta dele se o código mudasse.
3. **No desinstalar de verdade (o `.msi` para todo o computador, aberto com administrador), não se sabe de quem é a
   pasta apagada.** A ação `CleanupDeferred` roda como o sistema.
   - Se ela pega o LocalAppData do sistema, apaga `C:\Windows\System32\config\systemprofile\AppData\Local\EditorImpressao`
     e os projetos do Kaique ficam.
   - Se ela pega o LocalAppData de quem desinstalou, **apaga `%LOCALAPPDATA%\EditorImpressao` inteira: todos os projetos
     do Kaique** (ou os do Samuel, na etapa 5).
   - Não deu para provar sem administrador.
4. **Numa versão mais nova do Velopack, o risco fica certo.** No código atual do Velopack (ramo develop), o
   desinstalador `.msi` ganhou outra ação, `UserCleanupDeferred`. Ela roda **como o usuário que desinstala** e apaga
   `%LocalAppData%\{AppId}` de propósito (o comentário do código diz "the fallback dir"). A 1.2.161 ainda não tem essa
   ação (procurei o nome no arquivo dela e não achei). Atualizar o `vpk` sem consertar antes faria a desinstalação
   apagar os projetos.
5. **O `App().run()` apaga pacotes velhos só dentro de `packages\`** (`cleanup_old_packages_from_list`, só arquivos
   `.nupkg`). Ele não toca em `projetos\`.

## Risco para os projetos, em português simples

- **Ao abrir o programa:** o Kaique não perde nada. Mas aparece uma pasta `packages` e um `Update.exe` dentro da pasta
  dos projetos dele, sem ninguém pedir. Isso contraria o que o próprio programa promete no `atualizacao.py`
  ("Os projetos do Kaique nunca são tocados: o Velopack troca só a pasta do programa").
- **Ao desinstalar:** pode apagar todos os projetos. No teste, apagou. Falta saber se, na instalação de verdade, ele
  apaga a pasta do Kaique ou só a do sistema.
- **Na etapa 5, no PC do Samuel:** a lista manda instalar o programa de verdade e desinstalar no fim. Com o nome
  `EditorImpressao`, a desinstalação pode apagar a pasta de projetos **do Samuel**. A cópia de reserva da D-738 é
  obrigatória, mas não basta. Não rodar a etapa 5 antes do conserto.

## Desinstalar: provado ou não, e como provar na etapa 5

- **Provado, rodando:**
  - o desinstalador `.msi` por usuário, do `vpk` 1.2.161, apaga `LocalAppData\<id>` inteira, com o que estiver dentro;
  - o nosso `ao_desinstalar` não apaga nada.
- **Não provado:** de quem é a pasta apagada no `.msi` para todo o computador. Isso precisa de administrador.
- **Como provar na etapa 5:** duas perguntas do Windows, sempre com o pacote de mentira e nunca com o id
  `EditorImpressao`. O que é preciso já está em `D:\agente_temp_testes\velopack-pasta\app\`.
  1. Empacotar o `ProvaPasta` com `--msi --instLocation PerMachine`.
  2. Instalar com administrador (1ª pergunta) em Arquivos de Programas.
  3. Abrir na conta comum (`ProvaPasta.exe prova-app-run`). Ver a pasta de reserva aparecer em
     `%LOCALAPPDATA%\EditorImpressaoProvaPasta`.
  4. Pôr um projeto de mentira em `%LOCALAPPDATA%\EditorImpressaoProvaPasta\projetos\`.
  5. Desinstalar com `msiexec /x` (2ª pergunta).
  6. Ver se sobrou `%LOCALAPPDATA%\EditorImpressaoProvaPasta` (o do Samuel). Ver também
     `C:\Windows\System32\config\systemprofile\AppData\Local\EditorImpressaoProvaPasta`. Guardar o registro do `.msi`
     (`/l*v`).

## Plano do conserto (só o plano; nada foi codado)

**Por que acontece.** O Velopack usa a pasta `LocalAppData\<id do pacote>` para duas coisas:
- a pasta de reserva, quando a pasta do programa não aceita gravação (toda abertura na conta do Kaique);
- a limpeza do desinstalador.

O nosso id é `EditorImpressao`, e esse é também o nome da pasta onde os projetos moram (`historico.pasta_de_dados`).
Os dois nomes caíram iguais por acaso. Não foi decisão de ninguém.

**O que mudar, numa regra só (CLAUDE.md §11.12):**
1. **O id do pacote nunca é o nome da pasta dos dados.** Mudar só `versao.ID_DO_PACOTE`, para um nome que não seja
   `EditorImpressao`.
   - Sugestões: `EditorImpressaoPrograma` ou `EditorImpressao.Programa`.
   - O Kaique não vê esse nome em tela nenhuma: o nome em Arquivos de Programas e na lista de programas vem do título
     do pacote, que não muda.
   - Todos os outros lugares já leem esse valor dali: `empacotar.py`, `publicar_versao_kaique.py`,
     `atualizacao.voltar_para_a_anterior`, os testes e o ensaio.
   - **Tem de ser antes de qualquer instalação de verdade:** o próprio `versao.py` avisa que trocar depois de instalado
     faz o Velopack achar que é outro programa. Hoje não está instalado em lugar nenhum.
2. **Uma prova em `tests/`**, que cobra:
   - `versao.ID_DO_PACOTE` diferente do nome da pasta de `historico.pasta_de_dados()`;
   - o `--packId` do `empacotar.comando_do_vpk` igual a `versao.ID_DO_PACOTE`.
   - Rodada no código de hoje, ela falha (o teste de reversão da §4.7).
3. **Corrigir a frase falsa** no topo do `atualizacao.py` ("Os projetos do Kaique nunca sao tocados"). Ela tem de
   dizer onde o Velopack grava e por que o id é diferente.
4. **Prender o `velopack` e o `vpk` na 1.2.161** (já é a versão em uso). Antes de subir de versão, repetir esta prova:
   a versão nova muda o desinstalar (`UserCleanupDeferred`).

**O que fica igual:**
- os projetos continuam em `%LOCALAPPDATA%\EditorImpressao` (CLAUDE.md §7, D-731);
- nada muda para o Kaique, nem no PDF.
- Com o id novo, a pasta de reserva vai para `%LOCALAPPDATA%\<id novo>`, uma pasta só do Velopack. O desinstalador
  pode apagá-la sem perder nada.

**O que não resolve (descartado):**
- **Passar ao Velopack outra pasta de pacotes (o `VelopackLocatorConfig`):** só vale para o gerente de atualização. O
  `App().run()` do Python não aceita essa troca, e a limpeza do desinstalador continua apagando `LocalAppData\<id>`.
- **Trocar a variável `LOCALAPPDATA`:** o Velopack pergunta a pasta ao Windows (`SHGetKnownFolderPath`), e isso foi
  visto rodando.

**Como provar o conserto:**
1. A prova nova em `tests/`, que falha hoje e passa depois.
2. Repetir esta prova (casos A, B e C), com o id do pacote de mentira tirado da mesma regra.
3. Na etapa 5, com administrador e a cópia de reserva da D-738:
   - instalar o programa de verdade;
   - abrir sem administrador e ver que nada novo aparece em `%LOCALAPPDATA%\EditorImpressao`;
   - desinstalar e ver que `projetos\`, `configuracoes.json` e `historico.json` continuam lá.

## Como cumpri cada decisão

- **D-723** (Velopack, Arquivos de Programas): a prova usou o mesmo `vpk` 1.2.161. Arquivos de Programas foi imitado
  com uma pasta em que a minha conta não pode criar arquivos.
- **D-724** (só a assinatura do Samuel): a chave dele não foi usada. A conferência da assinatura rodou com uma chave
  de mentira e aceitou a versão de mentira ("publicada e assinada": `provas\atualizacao-de-mentira.log`).
- **D-731** (desinstalar tira o que os testes puseram, os projetos ficam): o nosso gancho não apaga nada. **Mas o
  desinstalador do Velopack apagou a pasta `LocalAppData\<id>`** (caso C). Com o id de hoje, a promessa "os projetos
  do Kaique continuam lá" não está garantida.
- **D-733** (janela sem administrador, ajudante como o sistema): o caso A é a janela, o caso B é o ajudante.
- **D-741 e D-749:** não foram tocadas.
- **Pasta de verdade dos projetos:** nunca foi aberta para mudar. A foto só leu os nomes do primeiro nível, iguais do
  começo ao fim (`configuracoes.json, erros.log, historico.json, projetos`).
- **Nenhuma pergunta do Windows, nenhuma janela, nenhum agente aberto.**

## O que criei fora do projeto (nada apagado sem ser meu)

- `D:\agente_temp_testes\velopack-pasta\`: o programa de mentira, os pacotes, a chave de mentira, o código do Velopack
  baixado para ler, as fotos e os registros. Cerca de 180 MB.
- `C:\Users\fotog\AppData\Local\EditorImpressaoProvaPasta\`: criado pelas provas. Apaguei entre as chamadas e o
  desinstalador apagou no fim. **Hoje não existe.**
- **`D:\Config.Msi`** (escondida, do sistema): **criada pelo Windows Installer** às 18:08:45, na primeira
  desinstalação. Ele não conseguiu limpá-la (erro 1926: "Could not set file security"). Não dá para apagar sem
  administrador, e não tentei. Fica para a gerente perguntar ao Samuel.
- As duas instalações de teste (`instalado-trancado`, `instalado-aberto`) foram tiradas pelo próprio desinstalador.
  A entrada do Windows também saiu. A permissão negada foi devolvida (`icacls /remove:d`), e a pasta trancada não
  existe mais.

## Ressalvas

- O `.msi` da prova é "por usuário", e o do Kaique é "para todo o computador". O que muda entre os dois está em
  "O que é dedução", item 3.
- A pasta trancada só negava criar arquivos na raiz. Em Arquivos de Programas, o Kaique também não grava em
  `current\`. Para a regra do Velopack isso não muda nada, porque ele só testa a raiz.
- A chamada `falta_a_pergunta_do_windows()` não rodou no programa de mentira: ela precisa de partes pesadas do
  programa, que deixei de fora. Ela não usa o Velopack.
- O Velopack não gravou arquivo de registro próprio para o pacote de mentira. Os avisos saíram na saída de erro e
  foram guardados em `provas\`.
