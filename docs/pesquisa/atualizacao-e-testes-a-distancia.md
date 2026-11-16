# Atualização pela internet e testes à distância no notebook do Kaique

Estudo do agente pesquisador, **16/11/2026**, etapa 1 da frente do notebook do Kaique
(`relatorios/frente-kaique-2026-11-16/plano.md`). **Só estudo: nenhuma linha do programa mudou, nada foi instalado no
Windows nem no `.venv` do projeto.** O único teste prático foi instalar pacotes num ambiente virtual novo, feito do
Python 3.14.3 da máquina, numa pasta da cópia (`relatorios/frente-kaique-2026-11-16/estudo/venv-teste/`, fora do git).

Marcas usadas: **[fonte]** = lido na documentação ou no código-fonte (link no fim); **[teste]** = rodado aqui;
**[dedução]** = conclusão minha, ainda não provada; **[a conferir]** = precisa da etapa 5 (PC do Samuel).

Decisões do Samuel que este estudo respeita: D-705, D-706, D-711 a D-722 (16/11/2026) e a regra do CLAUDE.md §3
"Algoritmo consagrado em vez de fórmula própria". As palavras dele estão no ONDE-PAREI desta tarefa.

---

## 0. A conclusão em cinco frases

1. Para a atualização, a ferramenta recomendada é o **Velopack** (licença MIT, viva, última versão estável 1.2.161 de
   29/09/2026): instala no Python 3.14 sem compilar nada **[teste]**, foi feita para o PyInstaller em pasta **[fonte]**,
   baixa só os arquivos que mudaram **[fonte]**, troca a pasta do programa de uma vez e devolve a anterior se a troca
   falhar **[fonte, código]**, e lê as versões direto do GitHub Releases de um projeto público, sem senha **[fonte]**.
2. O **tufup** (MIT) é o outro candidato sério: tem assinatura de verdade conferida pelo programa (TUF, grátis), mas
   no Python 3.14 só instala compilando uma peça em C **[teste]**, não volta para a versão anterior quando falha
   **[fonte, código]**, e o "baixar só o que mudou" dele não aguenta um programa de 1,9 GB **[fonte]**.
3. **Nenhuma** das ferramentas atualiza sozinha quando o computador liga: isso é sempre uma tarefa agendada do
   Windows, rodando como o próprio sistema (SYSTEM), que é como o Chrome e o Edge fazem **[fonte]**; ela é criada uma
   vez, na instalação, que já tem a licença de administrador.
4. Os testes à distância dá para fazer só com o que o Windows 11 traz, **igual no Home e no Pro**: o Servidor OpenSSH
   (recurso opcional), uma regra do firewall só para a rede do Tailscale, uma conta local sem administrador escondida
   da tela de entrada, e a prioridade baixa herdada pelos processos filhos **[fonte]**; tudo pedido com **uma** pergunta
   do Windows ("Deseja permitir...?").
5. O maior risco não é técnico: **conta escondida + porta de comando aberta é exatamente o desenho de um vírus de
   acesso remoto**, e antivírus podem acusar o programa **[fonte + dedução]**; e a assinatura do Velopack, sozinha, só
   confere se o arquivo chegou inteiro (a "prova de que é nosso" pede um passo a mais, ver §1.6).

---

## 1. Atualização pela internet

### 1.1 Como o programa é empacotado e instalado hoje (lido em `empacotar.py`, `instalador.iss`, `main.py`)

- **PyInstaller 6.21 em modo pasta** (`--onedir --windowed --contents-directory _internal`), saída
  `dist\EditorImpressao\`. Ao lado do `.exe` vão `motor-kraken\` (~1,2 GB) e `tesseract\`. Instalado: ~1,9 GB.
- **Inno Setup 6**, `PrivilegesRequired=admin`, instala em `C:\Program Files\Editor de Impressao\` (`{autopf}`),
  `AppId={{7C4E1B92-...}` fixo ("NAO troque este AppId"), atalho no Menu Iniciar, roda o `vc_redist.x64.exe` oficial
  só se faltar, `[UninstallDelete]` não apaga `%LOCALAPPDATA%\EditorImpressao`.
- **Versão:** só `#define MinhaVersao "1.0.0"` no `.iss`; o programa em si **não sabe a própria versão** (nenhuma
  constante de versão no código, conferido com `grep`).
- `main.py` atende, antes de qualquer janela, `--servidor-de-paginas` e `--conferir-ocr`. Não há modo de atualizar.
- Os dados do Kaique ficam em `%LOCALAPPDATA%\EditorImpressao` (fora da pasta do programa): **trocar a pasta do
  programa não toca nos projetos** — bom para qualquer ferramenta de atualização.

### 1.2 As candidatas

| Ferramenta | Licença | Python 3.14 + nosso PyInstaller | Baixa só o que mudou | Volta se falhar | Assinatura | GitHub público | Program Files | Ao ligar o PC |
|---|---|---|---|---|---|---|---|---|
| **Velopack** 1.2.161 | MIT | **Sim**: roda inteira (`abi3`, vale para 3.8+), instalada e importada aqui **[teste]**; feita para `pyinstaller --onedir` **[fonte]** | Sim, por arquivo (Zstandard) **[fonte]** | **Sim** na troca de arquivos **[fonte, código]**; não se a versão nova abrir quebrada | Confere SHA-256 do pacote **[fonte, código]**; assinatura Authenticode do `.exe` na hora de empacotar (certificado pago) **[fonte]** | Sim, `GithubSource`, sem senha (60 consultas/hora por endereço) **[fonte]** | Sim, com instalador MSI "por máquina"; ao atualizar pede administrador, ou atualiza direto se já rodar como administrador/SYSTEM **[fonte, código]** | Não tem; tarefa agendada nossa **[dedução]** |
| **tufup** 0.10.0 (04/10/2025) | MIT | Só **compilando** o `bsdiff4` 1.2 (não há pacote pronto para 3.14); compilado com o Visual Studio daqui, funcionou **[teste]**; prende o `tuf` na 4.0 (a atual é 7.0) **[fonte]** | Sim, mas um remendo binário do arquivo **inteiro** do programa; relato de 8+ horas para 450 MB **[fonte]**; com 1,9 GB teria de desligar e baixar tudo | **Não**: copia por cima com `robocopy`, sem cópia de segurança **[fonte, código]** | **Sim, de verdade**: metadados TUF assinados com chave nossa (grátis), conferidos pelo programa antes de instalar **[fonte]** | Não vem pronto; "deixado para quem implementa" **[fonte]** (dá com GitHub Pages ou endereços fixos **[dedução]**) | Copia com `as_admin` (pergunta do Windows a cada vez) **[fonte, código]** | Não tem **[fonte]** |
| **PyUpdater** | BSD (arquivado) | **Não**: projeto arquivado em 2022, última versão 4.0 de 2021 **[fonte]** | — | — | — | — | — | — |
| **WinSparkle** 0.9.4 (21/07/2026) | MIT | Biblioteca em C; o Python chamaria por fora **[dedução]** | **Não**: baixa o instalador inteiro (~600 MB) e roda **[fonte]** | Não (é o instalador) | **Sim**, Ed25519 conferida pelo programa **[fonte]** | Sim (arquivo de lista no GitHub) **[dedução]** | O instalador Inno pede administrador **[dedução]** | **Não**: é feita para mostrar uma janela "há versão nova" com o programa aberto **[fonte]** |
| **Inno Setup + verificador nosso** | (Inno: licença própria, grátis) | Sim | Não (instalador inteiro) | Não | Teria de ser nossa | Sim | Sim | Tarefa nossa |
| **MSIX + App Installer** (do próprio Windows; como o Slack desde 2025) | — | Empacotar o PyInstaller em MSIX **[dedução]** | Sim, por bloco (do Windows) **[dedução]** | Sim (do Windows) **[dedução]** | Certificado obrigatório; pode ser nosso, instalado uma vez **[dedução]** | Sim | Instala **por usuário**; a conta de testes precisaria de outra cópia **[dedução]** | Tarefa do próprio Windows a cada 8 h, não "ao ligar" **[fonte]** |

"Inno + verificador nosso" fica fora por regra (seria ferramenta inventada por nós). MSIX fica fora por risco: o
Windows "redireciona" o que o programa grava em `%LOCALAPPDATA%` para uma pasta do pacote **[dedução, a conferir]**, o
que poderia esconder os projetos que o Kaique já tem; e o motor do Kraken e o Tesseract são programas soltos que
rodam por baixo, o que o MSIX restringe **[dedução]**. WinSparkle e PyUpdater ficam fora pelo que está na tabela.

### 1.3 Velopack em detalhe

**O que é.** Sucessor do Squirrel.Windows (a documentação tem guia de migração dele **[fonte]**; o Squirrel foi o
atualizador do Slack, do Discord e do GitHub Desktop **[conhecimento geral, não conferido nesta tarefa]**), em Rust,
com biblioteca para Python. Repositório `velopack/velopack`, MIT **[fonte]**. Ativo: issues fechadas em outubro e
novembro de 2026, versão de desenvolvimento 1.3 em 17/10/2026 **[fonte]**.

**Licença e obrigações.** MIT: pode usar, mudar e distribuir; obriga só a manter o aviso de copyright e a licença
junto **[fonte]**. Compatível com o programa virar GPL.

**Python 3.14.** O pacote `velopack-1.2.161-cp38-abi3-win_amd64.whl` é de "ABI estável" (serve do 3.8 em diante sem
recompilar). Instalado no ambiente novo e importado: `UpdateManager`, `GithubSource`, `UpdateOptions`, `App`
**[teste]**. É um `.pyd` (código nativo); o PyInstaller deve levá-lo sozinho por ser importado **[dedução, a conferir
na etapa 2/3]**.

**PyInstaller.** A documentação manda usar `pyinstaller --onedir` (o nosso) e diz que o `--onefile` **não** serve
**[fonte]**. O arquivo único do pendrive continua existindo, mas não se atualiza.

**Como se liga no programa** **[fonte]**:
- `velopack.App().run()` tem de ser **a primeira coisa** do `main.py` (pode encerrar ou reiniciar o processo para
  cumprir tarefas de instalação). Tem ganchos: primeira vez, depois de atualizar, antes de desinstalar.
  `set_auto_apply_on_startup(False)` evita que aplique sozinho ao abrir **[fonte]**.
- `UpdateManager(GithubSource("https://github.com/Samuel-Bottini-BR/EditorImpressao"))` →
  `check_for_updates()` → `download_updates(info)` → `apply_updates_and_restart(info)` ou
  `wait_exit_then_apply_updates(info, silent=True, restart=False)` (espera o programa fechar e aplica) **[fonte, stub
  do pacote]**. `get_update_pending_restart()` diz se há versão baixada esperando **[fonte]**.
- `UpdateOptions(AllowVersionDowngrade=True, ...)` permite **voltar** para uma versão mais velha que esteja no feed
  **[fonte]**.

**Empacotar e publicar** **[fonte]**:
- `vpk pack --packId <id> --packVersion 1.2.3 --packDir dist\EditorImpressao --mainExe EditorImpressao.exe` gera o
  pacote completo, os pacotes de diferença, o `Setup.exe`, e com `--msi --instLocation PerMachine` um MSI que instala
  em `Program Files\{publisher}\{packTitle}` (pede administrador). `VELOPACK_INSTALLDIR` muda a pasta.
- `vpk upload github` sobe para o GitHub Releases (o token fica só no PC do Samuel, nunca no programa).
- O `vpk` é uma ferramenta .NET: o PC que empacota precisa do **.NET SDK** (o do Kaique não).
- `--framework vcredist143-x64` instala o Visual C++ antes do programa, **baixando da internet** (hoje o nosso vai
  dentro do instalador) **[fonte]**.

**Baixar só o que mudou.** Remendo por **arquivo**, com Zstandard; quem está várias versões atrás baixa uma diferença
por versão, ou o pacote inteiro se compensar; limite de 2 GB **por arquivo** (o nosso maior é bem menor) **[fonte]**.
Na prática: se só o código mudou, o motor do Kraken (1,2 GB) não é baixado de novo **[dedução]**. Achado: a issue
#1118 (fechada em 19/10/2026, depois da 1.2.161) diz que o MSI não guardava o pacote inicial, e a **primeira**
atualização vinha inteira **[fonte]**; o conserto deve estar só na 1.3 **[dedução, a conferir]**.

**Como troca os arquivos e volta se falhar** (lido em `src/bins/src/commands/apply_windows_impl.rs`) **[fonte, código]**:
1. monta a versão nova numa pasta temporária;
2. renomeia a pasta `current` (a versão de agora) para uma pasta de reserva;
3. renomeia a nova para `current`;
4. **se o passo 3 falhar, renomeia a reserva de volta** e mostra "Unable to complete the update, the previous version
   was restored"; se nem isso der, guarda a reserva e registra onde ela está;
5. se algum arquivo estiver preso (programa aberto), tenta **encerrar** os processos que rodam de dentro de `current`
   **[fonte]** — por isso a tarefa só pode aplicar com o programa fechado (ver §1.5).

O que o Velopack **não** faz: se a versão nova trocar certinho mas **não abrir** (defeito nosso), ele não volta
sozinho **[fonte: não há nada disso no código lido]**. Para cumprir a decisão "se falhar, volta" também nesse caso, o
caminho com função da própria ferramenta é: depois de aplicar, rodar a versão nova num teste rápido sem janela (como o
`--conferir-ocr` de hoje); se falhar, pedir ao `UpdateManager` com `AllowVersionDowngrade=True` a versão anterior,
que continua publicada no GitHub **[dedução, a provar na etapa 3]**.

**Program Files.** O instalador comum do Velopack é por usuário (`%LocalAppData%`); para `Program Files` é o MSI
"PerMachine" **[fonte]**. Ao aplicar, o `Update.exe` testa se consegue gravar na pasta; **se não consegue e não é
administrador, se reabre pedindo administrador** (a pergunta do Windows); se já é administrador, aplica direto **[fonte,
código, linhas 73-118]**. Logo: rodando pela tarefa do Windows como SYSTEM, ao ligar o PC, **não aparece pergunta**
**[dedução a partir do código, a conferir]**. Issue aberta #1040: com `--instLocation Either`, os ganchos do MSI rodam
sem administrador **[fonte]**; com `PerMachine` não achei relato **[a conferir]**.

**Assinatura** **[fonte]**:
- O programa, ao baixar, **confere o SHA-256** que está na lista de versões (`verify_package_checksum` em
  `src/lib-rust/src/manager.rs`). Isso prova que o arquivo chegou inteiro; **não** prova que é nosso, porque a lista
  vem do mesmo lugar que o arquivo (se alguém entrasse na conta do GitHub, publicaria os dois).
- A assinatura do Velopack é a **Authenticode** (a do Windows), aplicada na hora de empacotar com `signtool` ou o Azure
  Artifact Signing. Ela tira o aviso "editor desconhecido" do Windows e diminui alarme de antivírus. O programa **não**
  a confere ao atualizar (não há verificação dela no cliente; só no empacotador) **[fonte, busca no código]**.
- Custo: o Azure Artifact Signing (US$ 10/mês) só aceita pessoa física nos EUA e no Canadá **[fonte: Microsoft Learn,
  Q&A]** — **não serve no Brasil**. Certificado comercial (Certum, Sectigo...) tem custo anual e exige chave num
  dispositivo de segurança (USB ou nuvem) desde 2023 **[fonte]**. A SignPath Foundation assina de graça projetos de
  código aberto, mas confere que o binário foi construído a partir do repositório **[fonte]** — o nosso pacote leva
  peças que não estão no git (motor do Kraken, modelos), então exigiria empacotar no GitHub **[dedução]**.

### 1.4 tufup em detalhe

- MIT; criado para substituir o PyUpdater; usa o python-tuf (implementação de referência do The Update Framework, o
  desenho de segurança de atualização usado por grandes projetos) **[fonte]**. 149 estrelas, um mantenedor principal,
  último lançamento 04/10/2025 **[fonte]**.
- **Assinatura de verdade e grátis:** o PC do Samuel guarda as chaves privadas; o programa leva só o `root.json`
  (público) e confere a assinatura dos metadados e o resumo de cada arquivo **antes** de instalar **[fonte]**. Nenhuma
  senha dentro do programa.
- **Python 3.14:** `pip install tufup` falhou ("Unable to find a compatible Visual Studio installation") porque prende o
  `bsdiff4==1.2.*`, que não tem pacote pronto para o 3.14 (o `bsdiff4` 1.4.3 tem, mas o tufup não aceita). Com o
  `vcvars64.bat` do Visual Studio Build Tools daqui, compilou e funcionou: `tufup 0.10.0, tuf 4.0.0, bsdiff4 1.2.6`,
  `from tufup.client import Client` sem erro **[teste]**. O Windows do GitHub também tem compilador **[dedução]**.
- **Instalar:** extrai para uma pasta temporária e roda um `.bat` com `robocopy` **por cima** da pasta do programa,
  num processo novo, e o programa fecha; com `as_admin=True` pede administrador ao Windows (`ShellExecuteW` com
  `runas`) **[fonte, código `utils/platform_specific.py`]**. **Não há cópia de segurança nem volta**: se a cópia parar
  no meio, o programa fica metade novo, metade velho **[dedução a partir do código]**. Aceita uma função de instalação
  nossa — mas aí a volta seria código nosso.
- **Remendos:** um `bsdiff` do arquivo `.tar.gz` inteiro **[fonte]**; issue #154 (aberta): 8+ horas para 450 MB.
  Com 1,9 GB, na prática teria de desligar os remendos e baixar ~600 MB a cada versão **[dedução]**.
- **GitHub:** o autor diz que não vai pôr suporte a GitHub Releases ("keep tufup lean"), mas que dá para usar
  **[fonte, issue #63]**. Os metadados TUF precisam de endereços fixos; o GitHub Pages do projeto serviria **[dedução]**.

### 1.5 Atualizar ao ligar o computador, sem ninguém clicar (vale para qualquer ferramenta)

- **Como os grandes fazem** **[fonte: artigo codenote, documentação do VS Code]**: o Chrome e o Edge têm um
  atualizador que roda como **SYSTEM** (serviço + tarefas agendadas), e por isso grava em `Program Files` sem
  perguntar; o VS Code "para o sistema" (em Program Files) **pede administrador a cada atualização** e recomenda o
  instalador "por usuário"; o Slack, o Discord e o VS Code "por usuário" instalam em `%LocalAppData%`, onde o usuário
  grava sem pedir.
- **Para nós** **[dedução]**: uma **tarefa agendada do Windows**, criada uma vez na instalação (que já tem a licença
  de administrador), com gatilho "ao iniciar o computador", atraso de uns 2 minutos, "só com rede", rodando como
  SYSTEM: `EditorImpressao.exe --procurar-atualizacao` (modo sem janela, atendido no `main.py` antes de qualquer janela,
  como o `--servidor-de-paginas`). Ela procura, baixa e, **se o programa não estiver aberto**, aplica.
- **Por que não "por usuário" (sem administrador, como o Slack)?** Porque a conta de testes (D-717) precisa rodar o
  **mesmo** programa e **não pode** enxergar a pasta do Kaique; instalado em `%LocalAppData%` do Kaique, a conta de
  testes não alcançaria **[dedução]**. Por isso Program Files continua certo.
- **Programa aberto quando a versão chega (D-715, D-720):** a tarefa só baixa; o programa aberto percebe
  (`get_update_pending_restart`) e mostra "Reiniciar agora" / "Depois". Com "Depois", a tarefa aplica na próxima vez que
  o PC ligar. Com "Reiniciar agora": o programa do Kaique **não** é administrador, então o Velopack pede a licença ao
  Windows (uma pergunta "Deseja permitir...?") **[fonte, código]**; para evitar essa pergunta, o programa pode pedir
  ao Windows para rodar a tarefa agendada na hora (exige dar à conta do Kaique permissão de disparar aquela tarefa)
  **[dedução, a provar na etapa 3]**.
- **Falhou (D-718, D-719):** a mensagem combinada aparece na próxima abertura; o erro vai para um registro em
  `C:\ProgramData\EditorImpressao\atualizacao.log` — **não** no `%LOCALAPPDATA%` do Kaique, porque a conta de testes
  (por onde a gerente lê, D-719) não enxerga a pasta dele **[dedução]**.

### 1.6 A "assinatura que prova que o arquivo é nosso" com o Velopack

Duas saídas, as duas com algoritmo consagrado:
- **(a) Grátis, conferida pelo programa:** o PC do Samuel assina a lista de versões com uma chave **Ed25519** (o mesmo
  método do TUF, do Sparkle do Mac e do WinSparkle), no formato da ferramenta `minisign`; o programa leva só a chave
  pública e, antes de aplicar, confere que o SHA-256 do pacote que o Velopack baixou é o mesmo da lista assinada
  **[dedução; Ed25519 já vem no `cryptography`, que o tufup também usa]**. É um passo pequeno nosso em cima da
  ferramenta, **sem** inventar algoritmo.
- **(b) Certificado de assinatura do Windows (Authenticode):** tira o aviso "editor desconhecido" e diminui alarme de
  antivírus; tem custo anual e exige identidade; o programa não a confere ao atualizar **[fonte]**.
- As duas juntas são o mais forte **[dedução]**.

---

## 2. Testes à distância (Servidor OpenSSH do Windows, só pelo Tailscale)

Tudo abaixo **é do próprio Windows**; nada é instalado de fora. Nada foi feito nesta máquina: só leitura (aqui há o
cliente OpenSSH em `C:\Windows\System32\OpenSSH`, sem o servidor; listar os recursos opcionais já pede administrador
— "A operação solicitada requer elevação" **[teste]**).

### 2.1 Home ou Pro?

- O Servidor OpenSSH é um "recurso sob demanda" do Windows 10 1809+ e do Windows 11; os pré-requisitos da Microsoft
  não citam edição **[fonte]** — **funciona no Home** (este PC é Home 26200 e tem o cliente) **[dedução forte]**.
- Contas locais (`New-LocalUser`), firewall com filtro de endereço (`New-NetFirewallRule`), tarefas agendadas e a
  chave do registro que esconde a conta funcionam no Home **[dedução]**. O que o Home **não** tem são o "Editor de
  Política de Grupo" e o "Usuários e Grupos Locais" com janela — não precisamos deles.
- Conclusão: **nada muda entre Home e Pro** para este plano **[dedução]**. Se for Pro, nada a mais é preciso.

### 2.2 Os passos ao ligar a opção (todos pedem administrador; feitos num passo só)

1. **Instalar o servidor:** `Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0` (baixa do Windows Update,
   leva alguns minutos; precisa de internet) **[fonte]**.
2. **Ligar com o Windows:** `Set-Service sshd -StartupType Automatic` e `Start-Service sshd` **[fonte]**.
3. **Firewall só para o Tailscale:** a instalação cria a regra `OpenSSH-Server-In-TCP`, que libera a porta 22
   **[fonte]**; ela precisa ser **desligada** e trocada por uma nossa:
   `New-NetFirewallRule -Name EditorImpressao-Testes -Direction Inbound -Protocol TCP -LocalPort 22 -RemoteAddress 100.64.0.0/10 -InterfaceAlias Tailscale -Action Allow`.
   100.64.0.0/10 é a faixa do Tailscale **[fonte]**; prender também à placa de rede "Tailscale" impede que alguém do
   Wi-Fi da casa use essa faixa **[dedução; nome da placa a conferir]**. O Tailscale também tem endereços IPv6
   (`fd7a:115c:a1e0::/48`) **[dedução]**: ou entram na regra, ou ficam de fora de propósito.
4. **Só a conta de testes entra:** no `C:\ProgramData\ssh\sshd_config`, `AllowUsers <conta-de-testes>` e
   `PasswordAuthentication yes` (senha, D-711), `MaxAuthTries 3` **[dedução; opções padrão do OpenSSH]**. Assim nem a
   conta do Kaique entra por ali.
5. **Criar a conta:** `New-LocalUser` com a senha digitada na janela da primeira abertura (D-721), **sem** pôr no grupo
   Administradores, só em "Usuários". A senha passa do programa para o passo de administrador **por dentro** (nunca na
   linha de comando, que outros programas enxergam) e não é guardada **[dedução]**.
6. **Esconder da tela de entrada:** valor `<conta> = 0` (DWORD) em
   `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList`. Não achei página oficial da
   Microsoft; é o método usado amplamente e citado num Q&A da Microsoft **[fonte, terceiros]**. **Ferramentas de
   segurança marcam essa chave como suspeita** (Splunk, regras Sigma) **[fonte]**.
7. **Projetos separados:** cada conta tem o seu `%LOCALAPPDATA%`; o programa já grava lá (`historico.pasta_de_dados`),
   então os projetos de teste ficam na conta de testes sozinhos **[dedução a partir do código]**. A pasta
   `C:\Users\<Kaique>` não é legível por outra conta comum **[dedução, regra padrão do Windows; é a prova da etapa 4]**.
   **Cuidado:** pastas fora de `C:\Users` (por exemplo um `D:\Livros`) costumam ser legíveis e graváveis por qualquer
   conta **[dedução]** — a prova tem de olhar onde o Kaique guarda os livros.

**Prioridade baixa ou normal (D-716).** Pela Microsoft: um processo criado sem prioridade explícita **herda** a
prioridade do pai quando o pai está em "abaixo do normal" ou "ociosa" **[fonte: CreateProcessW]**. Então basta o
comando de longe começar em baixa (`start "" /belownormal /wait ...` ou o próprio programa aceitar `--prioridade
baixa`) e os processos filhos do programa (servidores de páginas, Kraken, Tesseract) seguem em baixa; o código de hoje
cria esses filhos sem prioridade explícita, só com "sem janela" **[fonte, código: `core/paginas_em_outro_processo.py`,
`core/ocr_kraken.py`]**. O `rodar_suite_por_arquivo.py` já usa `BELOW_NORMAL_PRIORITY_CLASS`. Sem dizer nada → baixa.

**Sem janela na tela do Kaique.** O `sshd` roda como serviço; o que se roda por ele não tem área de trabalho, e o
programa precisa de `QT_QPA_PLATFORM=offscreen` — o que combina com a regra "nunca abrir janela na tela" **[dedução]**.

### 2.3 Como o programa pede a licença (uma pergunta do Windows só)

- O programa (que roda sem administrador) abre **um** ajudante com o verbo `runas` do Windows (o mesmo que o tufup
  usa no `run_bat_as_admin`) **[fonte]**: aparece **uma** pergunta "Deseja permitir que este aplicativo faça alterações
  no seu dispositivo?", e o ajudante faz os 7 passos de uma vez.
- **Se o Kaique disser "Não":** o Windows devolve "cancelado" (erro 1223) **[dedução: comportamento conhecido do
  `ShellExecuteEx`]**; nada é instalado, a opção volta para desligada e aparece um aviso curto; dá para ligar depois
  nas Configurações (como a D-721 já prevê para a senha).
- **Não** usar a tarefa de SYSTEM da atualização para fazer isso sem perguntar: seria um "atalho" para qualquer
  programa da conta do Kaique virar administrador **[dedução]**.

### 2.4 Desligar e desfazer

- **Desligar** (na opção): `Stop-Service sshd`, `Set-Service sshd -StartupType Disabled`, apagar a regra
  `EditorImpressao-Testes`, deixar a `OpenSSH-Server-In-TCP` desligada, e desativar a conta (`Disable-LocalUser`) —
  os projetos de teste ficam guardados **[fonte + dedução]**.
- **Desfazer tudo** (etapa 5, D-722, e talvez ao desinstalar): os passos acima e mais `Remove-LocalUser`, apagar o
  perfil da conta (`Win32_UserProfile`), apagar o valor do `UserList`, devolver o `sshd_config` e
  `Remove-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0` (a Microsoft pede reiniciar se o serviço estava em
  uso) **[fonte]**.

### 2.5 Riscos de segurança

- **Parece vírus:** conta escondida + serviço de comando + regra de firewall é o desenho de um "acesso remoto"
  malicioso; o Defender ou outro antivírus pode bloquear o ajudante ou apagar o programa **[dedução; a chave da conta
  escondida está em regras de detecção, fonte]**. Ajuda: assinar o programa (Authenticode), a opção à vista nas
  Configurações, e um registro do que foi feito.
- **Adivinhar a senha:** só quem está na rede do Tailscale do Samuel chega à porta; senha forte; `MaxAuthTries`; o
  Windows 11 tem bloqueio de conta depois de tentativas erradas **[dedução, a conferir com `net accounts`]**. Lembrete
  da D-705: o Tailscale do PC do Samuel está entrando na conta do servidor de livros; quem mais estiver nessa rede chega
  à porta.
- **Falha no próprio OpenSSH:** é mantido pela Microsoft e atualizado pelo Windows Update **[fonte]**.
- **Escrever fora da conta:** a conta de testes não é administradora, mas pastas fora de `C:\Users` podem estar
  abertas (§2.2, item 7).

### 2.6 Como fazem as ferramentas de suporte remoto (TeamViewer, AnyDesk, RustDesk, Área de Trabalho Remota do Chrome)

**[dedução, conhecimento geral; não li a documentação de cada uma nesta tarefa]**: rodam como serviço do sistema,
mas **não abrem porta**: o computador liga **para fora**, num servidor deles, e a conexão passa por lá; o acesso sem
ninguém na frente usa uma senha definida pelo dono; mostram **um aviso na tela** enquanto alguém está conectado e
guardam um histórico. O nosso jeito (OpenSSH pelo Tailscale) também não expõe porta à internet — o Tailscale faz o
papel do "servidor do meio" — e não mostra a tela do Kaique (só comando, sem imagem). O que eles têm e o nosso não tem:
o aviso visível de "alguém está conectado"; o Windows guarda o histórico de entradas do OpenSSH no Visualizador de
Eventos (`OpenSSH/Operational`) **[dedução]**.

---

## 3. O que está pronto e o que falta no empacotamento de hoje

**Pronto:**
- PyInstaller em pasta, que é o que o Velopack pede; a pasta `_internal` e as peças ao lado do `.exe` continuam iguais.
- Instalação em Program Files (certo para a conta de testes enxergar o mesmo programa).
- Dados do Kaique fora da pasta do programa (`%LOCALAPPDATA%`), e o desinstalar não apaga: atualizar não toca nos
  projetos.
- `main.py` já atende modos sem janela antes de abrir qualquer janela (`--servidor-de-paginas`, `--conferir-ocr`): o
  `--procurar-atualizacao` e o "teste rápido da versão nova" entram do mesmo jeito.
- `--conferir-ocr` já é uma prova de que o empacotado está inteiro.
- O registro de erros (`registro.py`) e a regra "nenhuma exceção fecha a janela".
- Prioridade baixa já usada em `rodar_suite_por_arquivo.py`, `ocr_kraken.py` e `ocr_tesseract.py`.

**Falta (atualização):**
- O programa saber **a própria versão** (hoje só "1.0.0" no `.iss`, nunca mudado).
- `velopack.App().run()` no começo do `main.py` (cuidado: os servidores de páginas usam o mesmo `.exe`; `run()` com
  argumentos comuns volta logo **[dedução, a conferir]**).
- O modo `--procurar-atualizacao` e a tarefa agendada que o chama ao ligar o PC.
- O aviso "Reiniciar agora / Depois" e a mensagem de falha (D-719), e o registro em `C:\ProgramData`.
- Um comando nosso de publicar a "versão para o Kaique": `empacotar.py` → `vpk pack` → assinar → `vpk upload github`.
- O .NET SDK e o `vpk` no PC que empacota.
- A assinatura (§1.6).
- **Trocar o instalador:** o Velopack tem o próprio instalador (MSI "por máquina"); o Inno Setup sai, e com ele o
  `vc_redist` de dentro (o Velopack baixa) e as travas do `.iss` (que precisam ir para o `empacotar.py`). O Kaique já
  tem uma instalação do Inno de 28/10: a primeira instalação nova precisa tirar a velha, senão ficam duas cópias
  **[dedução]**.
- Os testes de `tests/test_empacotar.py` que conferem o `.iss` passam a conferir o pacote do Velopack (teste antigo não
  se muda para passar: o plano da etapa 3 tem de dizer quais saem e por quê, com o "sim" do Samuel).

**Falta (testes à distância):**
- A opção nas Configurações, ligada de fábrica, e a janela da senha na primeira abertura.
- O ajudante de administrador (ligar, desligar, desfazer), com registro do que fez.
- Nada no instalador (D-712).

---

## 4. O que ficou em aberto

- Velopack com MSI "por máquina" + tarefa SYSTEM ao ligar: aplica sem pergunta? (código diz que sim) — **etapa 5**.
- Se os ganchos do MSI "PerMachine" rodam como administrador (para criar a tarefa na instalação) — se não, a tarefa
  é criada na primeira abertura, junto com a pergunta única do Windows.
- O `.pyd` do Velopack no PyInstaller 6.21 e o `App().run()` com os servidores de páginas.
- O tamanho do pacote inteiro (~600 MB comprimido?) e o espaço no disco do Kaique durante a troca (~2 × 1,9 GB).
- O nome da placa "Tailscale" no Windows e se o IPv6 do Tailscale entra.
- Se o antivírus do notebook do Kaique reclama do ajudante.
- O que fazer com a conta de testes e o OpenSSH quando o programa for **desinstalado** (não está decidido).

## 5. Links consultados (16/11/2026)

- Velopack: https://github.com/velopack/velopack · https://docs.velopack.io/getting-started/python ·
  https://docs.velopack.io/packaging/installer · https://docs.velopack.io/packaging/operating-systems/windows ·
  https://docs.velopack.io/packaging/deltas · https://docs.velopack.io/packaging/signing ·
  https://docs.velopack.io/packaging/bootstrapping · https://docs.velopack.io/reference/cli/content/update-windows ·
  https://docs.velopack.io/troubleshooting/faq · issues #32, #1040, #1118 · código
  `src/bins/src/commands/apply_windows_impl.rs`, `src/lib-rust/src/manager.rs` · https://pypi.org/project/velopack/
- tufup: https://github.com/dennisvang/tufup (README, `pyproject.toml`, `src/tufup/utils/platform_specific.py`) ·
  issues #63, #154 · https://pypi.org/project/tufup/ · https://pypi.org/project/bsdiff4/ · https://pypi.org/project/tuf/
- PyUpdater: https://github.com/Digital-Sapphire/PyUpdater (arquivado) · https://pypi.org/project/pyupdater/
- WinSparkle: https://github.com/vslavik/winsparkle (README, assinatura EdDSA)
- Padrões de atualização por máquina: https://codenote.net/en/posts/windows-desktop-app-per-machine-silent-auto-update-patterns/
- Assinatura: https://learn.microsoft.com/azure/artifact-signing/quickstart ·
  https://learn.microsoft.com/en-us/answers/questions/2243504/trusted-signing-for-other-countries · https://signpath.org/
- OpenSSH: https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse
- Prioridade herdada: https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw
- Tailscale: https://tailscale.com/kb/1015/100.x-addresses · https://tailscale.com/kb/1193/tailscale-ssh (o servidor
  SSH do próprio Tailscale **não** roda no Windows — por isso o OpenSSH do Windows)
- Conta escondida: https://www.thewindowsclub.com/hide-specific-user-accounts-from-the-sign-in-screen-on-windows-10 ·
  https://research.splunk.com/endpoint/834ba832-ad89-11eb-937d-acde48001122/ ·
  https://detection.fyi/sigmahq/sigma/windows/registry/registry_set/registry_set_special_accounts
