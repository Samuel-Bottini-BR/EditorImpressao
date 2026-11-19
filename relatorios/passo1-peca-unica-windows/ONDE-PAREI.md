# Passo 1 do plano da parte do Windows: a peça única do Windows e a pasta segura (19/11/2026)

Implementador. Ramo `passo1-peca-unica-windows`, worktree `.claude/worktrees/passo1`, saiu de `b9f07e43` (a versão de
teste com o porteiro ligado). Este ONDE-PAREI é também o formulário da entrega (D-792).

## Pedido

- Papel: implementador
- Commit de partida: b9f07e43
- Ramo: passo1-peca-unica-windows

## Arquivos que vou mexer

- `core/windows.py` (novo)
- `main.py`
- `tests/test_windows_*.py` (novo)
- `janela_de_prova.py` (novo)
- `relatorios/passo1-peca-unica-windows/`

## Onde parei

- 19/11: leitura feita (pacote, plano v3, plano v1 §1.2 e §2, Livro, código de hoje, peças de fora). Seções de antes
  de escrever preenchidas abaixo. **Achado que vira pergunta:** pela leitura, a pergunta do Windows mostra o nome do
  arquivo (`EditorImpressao.exe`), não "Editor de Impressão" (ver "O que li" e "Perguntas para o Samuel"). Não mexi em
  `empacotar.py` nem no nome do arquivo. Começando o código.

## Decisões que esta tarefa precisa cumprir

- D-782 "como assim assusta?" · "ele não vai pensar isso" · "sim" (à pergunta "Prefere a B?"). Aqui: quem pede a
  licença é o próprio programa do Editor (não o PowerShell), com um aviso de trabalho na pasta de troca; na pergunta
  deveria aparecer "Editor de Impressão" (ver a pergunta para o Samuel: pela leitura, aparece o nome do arquivo).
- D-767 "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione". Aqui: o que
  mexe no Windows (licença, tarefa, pasta segura) só roda de verdade na janela de prova, à vista; os testes
  automáticos só leem o Windows ou provam a lógica em volta.
- D-775 "o agente vai tentar quebrar antes de fazer o teste real na tela né?" · "ok". Aqui: entrego à gerente sem
  rótulo; a prova à vista vem depois de quem tenta quebrar.
- D-785 "ok, mais ainda existem mais casos na opção A". Aqui: a pergunta "Deseja permitir...?", as tarefas e a pasta
  em Arquivos de Programas são da lista "sempre à vista": não rodei nada disso; a janela de prova faz na tela.
- D-733 "1- sim / VAI CONSEGUIR FAZER OS TESTS A DISTANCIA NÉ?". Aqui: a peça pede a licença uma vez por trabalho e
  cria tarefas que rodam como o sistema e que a conta comum pode mandar rodar (a base do ajudante; o ajudante mesmo
  muda no passo 3).
- D-724 "gratis, mas o que é essa assinatura e é segura?". Aqui: o programa não tem certificado pago; isso decide o
  que a pergunta do Windows mostra (faixa amarela, "Editor: Desconhecido").
- D-780 "não quero fazer essa prova com o celular, eu quero que tu programa o negocio e ele funcione". Aqui: a peça
  dá as leituras básicas sem licença (tarefa, licenças de pasta, marca); a leitura das duas trancas é do passo 4.
- D-722 "Sim". Aqui: a prova à vista no PC do Samuel termina com a pergunta 3 apagando a tarefa e a pasta de prova, e
  a janela lê que não existem mais (a lista do que foi desfeito).
- D-786 "a". Aqui: este passo não mexe no processamento das páginas; a velocidade fica com a gerente.
- D-787 "A". Aqui: no PC rodei um arquivo de teste por vez; o conjunto inteiro roda no GitHub.
- D-791 "não sei do que você está falando" · "b". Aqui: o porteiro roda; `core/windows.py` é o único lugar onde a
  conversa com o Windows é permitida; nenhum item sai da lista de exceções neste passo.
- D-796 "1, mas tem que ser explissito o pedido né". Aqui: não mexo em `ui/`; só nos arquivos do pedido.
- D-797 "ok". Aqui: trabalho no meu ramo; quem junta na versão de teste é a gerente.
- D-798 "fechou". Aqui: não escrevo o rótulo de pronto para conferir nem "aprovado".
- D-799 "Aprova o plano?" → "ok". Aqui: sigo o passo 1 do plano v3, só ele.
- D-801 "ok". Aqui: a lista de exceções entrou valendo; este passo não acrescenta nem tira item.
- D-802 "ok, continuamos assim e vamos proceguir". Aqui: os lugares antigos fora do plano ficam como estão.
- D-605 "A partir de agora, nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está
  escolhido e testado, coisas novas não podem criar novos problemas, essa é uma nova regra que todos os agentes
  precisam ler". Aqui: nenhum chamador muda; o programa do Kaique continua igual.
- D-637 "você tem que pensar na experiencia do usario e no resultado final do livro dentro do programa, quando vai
  mudar algo, deixe isso anotado." Aqui: seção "Como fica para quem usa e no livro".

## O que já está escolhido e testado aqui

- **`main.py`:** a ordem dos modos sem janela (o servidor de páginas, o brasão girando, a conferência dos OCRs e a
  atualização, antes da janela); provas em `tests/test_decisoes_brasao.py` (o brasão antes dos imports pesados, o
  ícone) e `tests/test_decisoes_atualizacao.py` (`test_o_main_chama_a_atualizacao_por_um_ponto_so`, os modos antigos
  antes da atualização; `test_d719_nenhum_token_dentro_do_programa`). A entrada nova vem **antes** de todos e não
  muda nenhum deles.
- **A conversa com o Windows de hoje** (`atualizacao.py`, `core/_testes_a_distancia_windows.py`,
  `core/testes_a_distancia.py`): fica como está neste passo (os chamadores mudam nos passos 3 a 5). Testes que a
  cobrem e que não podem quebrar: `tests/test_decisoes_ajudante_da_atualizacao.py` (37),
  `tests/test_decisoes_atualizacao.py` (38), `tests/test_decisoes_testes_a_distancia.py` (13),
  `tests/test_decisoes_desinstalar.py` (37), `tests/test_decisoes_preparo_d749.py` (5).
- **O porteiro** (`tests/test_conferencias_codigo.py` e os outros `tests/test_conferencias_*.py`): `core/windows.py`
  é o lugar permitido para a conversa com o Windows (K01), mas a K02 (`DETACHED_PROCESS`) e a K03 (licença de pasta à
  mão) valem também nele; a K04 (número de decisão em texto) vale em `core/` e no `main.py`.
- **Decisões tocadas:** D-782 (quem pede a licença), D-733 (uma pergunta, a tarefa que roda como o sistema), D-767 e
  D-785 (à vista), D-724 (sem certificado pago).
- Nenhum teste antigo muda neste passo (plano v3, passo 1: "Testes antigos que mudam: nenhum").

## Como fica para quem usa e no livro

- **O Kaique, antes e depois deste passo: nada muda.** A peça nova ainda não é chamada por nenhuma tela; a primeira
  abertura, a atualização e os testes à distância continuam pelo caminho de hoje até os passos 3 e 4.
- **A entrada nova no começo do programa** só age quando o programa é aberto com o aviso de trabalho de
  administrador; aberto pelo atalho, como o Kaique abre, ela não faz nada (e não atrasa: só olha o primeiro
  argumento).
- **No PDF e nos livros: nada muda.** Nenhuma linha de processamento das páginas é tocada.
- **Depois dos passos 3 e 4 (não neste):** o que o Kaique verá é a pergunta do Windows com o nome do programa (ver a
  pergunta sobre o nome), uma vez na primeira abertura, e a janela do programa continua respondendo enquanto o
  Windows trabalha (o trabalho roda fora do fio da tela).
- **A janela de prova** é ferramenta da prova à vista, não vai no pacote do Kaique (fica na raiz do projeto, fora do
  que o empacotador leva; conferido em "Ressalvas").

## A causa, a regra e todos os caminhos

**A causa (etapa 5):** cada função falava com o Windows do seu jeito e só pelo caminho em que tudo dá certo: o "Não"
lido como "deu certo" (o erro lido sem guardar o último erro do Windows), o PowerShell lançado solto que saía sem
rodar (`DETACHED_PROCESS`), a pasta temporária do Python 3.14 que só o dono lê (o relatório do script com licença
ficava ilegível), a resposta das ferramentas lida na tabela de letras errada, o script sem a marca de UTF-8.

**A regra (um lugar só):** `core/windows.py`. Toda conversa com o Windows passa por ele, com uma de três respostas
(deu certo, a pessoa disse "Não", falhou com o motivo em português):
- pedir licença: `pedir_licenca()` (abre o próprio programa com licença e um aviso de trabalho na pasta de troca);
- o lado com licença: `atender_trabalho_de_administrador()` (o `main.py` chama, antes de tudo);
- lançar solto: `lancar_solto()` e `lancar_powershell_solto()`;
- rodar e esperar: `rodar_e_esperar()` e `rodar_powershell()`;
- tarefas: `criar_tarefa()`, `apagar_tarefa()`, `rodar_tarefa()`, `ler_tarefa()`, `xml_da_tarefa_do_sistema()`;
- a pasta de troca: `criar_pasta_de_troca()`, `apagar_pasta_de_troca()`;
- a pasta segura: `pasta_segura()`, `criar_pasta_segura()`, `conferir_pasta_segura()`, `apagar_pasta_segura()`;
- ler sem licença: `ler_licencas()`, `marca_existe()`, `ler_tarefa()`;
- o segredo numa codificação só: `cifrar_segredo()` e `decifrar_segredo()`.

**Todos os caminhos que chegam nela, neste passo** (achados com busca no código por `core.windows`, `windows.`,
`--trabalho-de-administrador`):
- o começo do programa (`main.py`) → `atender_trabalho_de_administrador()`;
- a janela de prova (`janela_de_prova.py`) → todas as funções acima, importadas do programa (nunca copiadas);
- os testes (`tests/test_windows_*.py`) → as leituras e a lógica.
- **Ainda não chegam** (mudam nos passos 3 a 5, como o plano diz; hoje têm conta própria e estão na lista de
  exceções do porteiro): `atualizacao.py` (`_rodar`, `_lancar_escondido`, `criar_tarefa`, `apagar_tarefa`,
  `rodar_tarefa_agora`, `_marca_existe`, `xml_da_tarefa`), `core/_testes_a_distancia_windows.py` (`_rodar_elevado`,
  `aplicar_no_windows`, `rodar_a_tarefa_no_windows`), `core/testes_a_distancia.py`.

## O que pode falhar e o que o programa faz

Cada caso devolve uma das três respostas, com uma frase em português; o técnico vai para o registro. Nada fica pela
metade sem dizer: o relatório do trabalho diz, passo a passo, o que foi feito, o que falhou e o que não foi tentado.

- **Sem licença** (a conta não é administradora e ninguém digita a senha de um administrador): o Windows não abre o
  programa; a resposta é "a pessoa disse Não" (o Windows devolve o mesmo código de cancelado) e nada muda.
- **A pessoa diz "Não"** (ou fecha a pergunta pelo X): o Windows devolve "cancelado" (1223); a resposta é "você
  disse Não; nada mudou". O código é lido do jeito certo (guardando o último erro do Windows logo depois da chamada).
- **A pergunta não vem para a frente** (o Kaique está em outra janela): a peça tenta trazer a janela do programa para
  a frente antes e diz se conseguiu; se não conseguiu, o Windows põe a pergunta piscando na barra de tarefas. A
  espera continua; a resposta diz "a janela não estava na frente".
- **Ninguém responde a pergunta:** a chamada fica esperando no fio de trabalho (nunca no da tela); a tela continua
  respondendo.
- **O programa a abrir não existe** (pasta apagada, caminho errado): a peça confere antes de pedir; resposta "falhou:
  não achei o programa", sem a caixa crua do Windows (e a caixa crua fica desligada também para os outros erros).
- **Sem internet:** não se aplica a este passo (nada aqui usa a rede).
- **Disco cheio:** a pasta de troca ou o aviso não conseguem ser gravados → "falhou: não consegui gravar o pedido",
  sem perguntar nada ao Windows. Se o disco enche durante o trabalho com licença, o passo daquele momento falha, o
  relatório diz qual, e os seguintes não são tentados.
- **Arquivo preso** (outro programa segura a pasta de troca ou a pasta segura): apagar falha → a resposta diz o que
  ficou; a pasta de troca velha é tentada de novo na próxima vez (as com mais de um dia são limpas).
- **Desligar no meio** (o computador desliga durante o trabalho com licença): o relatório fica pela metade ou nem
  existe → na próxima leitura, a resposta é "falhou: o trabalho não terminou"; o que já tinha sido feito se confere
  pelas leituras (tarefa existe? pasta segura confere?), nunca pela anotação.
- **O programa com licença trava ou demora:** a espera tem limite; passou dele, "falhou: o Windows não terminou no
  tempo" (o processo com licença não pode ser fechado pela conta comum; fica anotado).
- **O programa com licença começa e cai sem relatório:** "falhou: o trabalho com licença não deixou relatório"
  (código de saída anotado). Código de saída sozinho nunca decide "deu certo".
- **Alguém troca o aviso de trabalho por outro:** a pasta de troca nasce na pasta da conta, que outra conta comum não
  consegue gravar; o lado com licença confere isso antes de ler (dono, quem pode gravar, não é atalho para outro
  lugar) e recusa se não for assim. O aviso só aceita uma lista fechada de tipos de passo; nomes de pasta segura e de
  tarefa só de uma lista fechada e da pasta de tarefas do programa.
- **Aberto com o aviso sem ter licença** (alguém roda à mão): o lado do trabalho recusa ("este trabalho precisa da
  licença de administrador") e não faz nada.
- **Lançar solto quando quem lança está preso a um grupo que mata os filhos ao fechar** (job do Windows): a peça
  confere antes; se não der para soltar, "falhou", em vez de lançar algo que morreria junto. O lançado tem de dar
  sinal de vida em poucos segundos; sem sinal, a peça fecha o lançado e diz "falhou".
- **A pasta segura já existe com licenças diferentes** (alguém mexeu, ou é um atalho para outro lugar): não se
  conserta à mão; a resposta diz "a pasta segura não confere" e quais licenças estão lá.
- **O Windows desligado de política** (scripts proibidos por política da empresa, o antivírus segurando o
  PowerShell): o script falha → "falhou", com o que o PowerShell disse no registro.

## O que li da peça de fora e onde

Lido (documentação ou código), separado do deduzido:

- **O nome que a pergunta do Windows mostra (risco 2):** para programa sem assinatura, "only a generic icon, the
  file name, and "Unidentified Publisher"" (Mark Russinovich, "Inside Windows Vista User Account Control",
  https://learn.microsoft.com/en-us/previous-versions/technet-magazine/cc138019(v=msdn.10)); e o guia de compatibilidade
  da Microsoft manda dar "a short, meaningful name for the executable. This name will be shown in the User Account
  Control dialog box" (https://learn.microsoft.com/en-us/previous-versions/bb756922(v=msdn.10)). A página atual da
  Microsoft só diz que o programa sem assinatura tem faixa amarela, e a foto dela esconde o nome
  (https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/how-it-works).
  **Deduzido:** com o arquivo `EditorImpressao.exe`, a pergunta mostra "EditorImpressao.exe". Só a sessão A prova.
- **O atalho de partida do Velopack** (se pedir pela entrada da raiz mudaria o nome): ela é nomeada pelo nome do
  programa, `<programa>_ExecutionStub.exe` → `<programa>.exe` (Velopack 1.2.161,
  https://github.com/velopack/velopack/blob/1.2.161/src/lib-rust/src/bundle.rs linhas 275-299), e repassa os
  argumentos para `Update.exe start --` (https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/stub.rs). Então
  ela também se chama `EditorImpressao.exe`: não resolve o nome. A peça abre o programa direto.
- **Pedir licença:** `ShellExecuteExW` devolve FALSE e o erro vem de `GetLastError`; "ERROR_CANCELLED: The function
  prompted the user for additional information, but the user canceled the request"; COM deve ser iniciado no fio que
  chama (https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecuteexw). `SEE_MASK_FLAG_NO_UI`:
  "Do not display user interface (UI) error dialogs [...] Security prompts are exempted"; `SEE_MASK_NOCLOSEPROCESS`
  dá o processo para esperar; `hwnd` é a janela dona; `SEE_MASK_NOASYNC` quando o fio não tem laço de mensagens
  (https://learn.microsoft.com/en-us/windows/win32/api/shellapi/ns-shellapi-shellexecuteinfow).
- **Ler o erro do Windows no Python:** só com `use_last_error=True` o `ctypes.get_last_error()` traz o erro daquela
  chamada (https://docs.python.org/3/library/ctypes.html, a classe `CDLL`, parâmetro *use_last_error*). O código de
  hoje usa `ctypes.windll.shell32`, sem isso (`core/_testes_a_distancia_windows.py:91`).
- **A pergunta com o programa atrás de outra janela (risco 1):** "Background applications will automatically prompt
  the user for elevation on the taskbar [...] will appear minimized on the taskbar and will blink"; "The UAC elevation
  mechanism uses the HWND as part of determining whether the elevation is a background or foreground elevation"
  (https://learn.microsoft.com/en-us/previous-versions/bb756922(v=msdn.10)). E "An application cannot force a window to
  the foreground while the user is working with another window. Instead, Windows flashes the taskbar button"
  (https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow). **Deduzido:** com o
  navegador na frente (pergunta 3 da sessão A), a pergunta deve vir piscando na barra de tarefas, não no meio da tela.
- **A pasta temporária do Python 3.14:** `os.mkdir(mode=0o700)` (o que o `mkdtemp` usa) põe licença "only the current
  user and administrators" (https://github.com/python/cpython/blob/3.14/Doc/library/os.rst, linhas 2535-2537), feita
  com o dono da pasta ("OW") (https://github.com/python/cpython/blob/3.14/Modules/posixmodule.c, linhas 5760-5768). O
  arquivo que o programa com licença cria tem outro dono (os Administradores), e a conta comum não lê. **Por isso a
  pasta de troca nasce com `os.mkdir` comum, herdando as licenças da pasta da conta** (conferido só lendo:
  `%LOCALAPPDATA%` dá controle total à conta pelo nome dela, herdado).
- **O script do PowerShell 5.1:** "Without the BOM, Windows PowerShell misinterprets your script as being encoded in the
  legacy "ANSI" codepage" (https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1).
  Conferido no PC, só lendo: com a marca, texto e segredo com acento chegam iguais; sem a marca, o script nem roda.
- **A resposta das ferramentas do Windows:** o `schtasks` escreve na tabela de letras do console (OEM, 850 no PC do
  Samuel); conferido só lendo uma tarefa do Windows: lido como OEM sai "Hora da próxima execução"; lido como ANSI sai
  trocado (é o "ÒXITO" da etapa 5). O Python lê essa tabela com o codec `oem`.
- **Lançar solto:** `DETACHED_PROCESS` deixa o processo de console sem console; `CREATE_NO_WINDOW` roda o programa de
  console sem janela; `CREATE_BREAKAWAY_FROM_JOB` só funciona se o grupo deixar
  (https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags). Um grupo (job) com
  `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` fecha todos os processos dele quando fecha; os filhos ficam no grupo, a não ser
  com `BREAKAWAY_OK`/`SILENT_BREAKAWAY_OK` (https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).
- **Tarefas do Windows:** pelo COM do Agendador, "não existe" é o código 0x80070002 e "acesso negado" é 0x80070005
  (conferido no PC, só lendo: uma tarefa que não existe e uma do Windows que a conta comum não lê). O
  `schtasks /Create /XML` é o que já criou o ajudante na etapa 5 (`atualizacao.py:1155`).
- **A pasta segura:** as licenças de fábrica de Arquivos de Programas (lidas no PC): o Instalador Confiável, o
  sistema e os Administradores mudam; os Usuários leem e executam; o "Proprietário Criador" vira o dono da pasta
  nova. Lidas pelo `GetNamedSecurityInfoW` (https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getnamedsecurityinfow).
- **O segredo:** cifrado pelo próprio Windows para o computador (`CryptProtectData` com `CRYPTPROTECT_LOCAL_MACHINE`,
  https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata), num arquivo da pasta de troca
  (só a conta e os administradores leem), apagado no fim; assim abre também quando quem diz "Sim" é outro
  administrador (defeito 7 do plano v1).
- **Onde fica Arquivos de Programas e a pasta do sistema:** `SHGetKnownFolderPath(FOLDERID_ProgramFiles)`
  (https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath) e
  `GetSystemDirectoryW` (https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getsystemdirectoryw),
  em vez das variáveis de ambiente (que a conta pode mudar).

## O que foi feito

(a preencher)

## Arquivos criados ou alterados

(a preencher)

## Como cumpri cada uma

(a preencher)

## Testes

(a preencher)

## Caminho e função

(a preencher)

## Máquina ou olho

(a preencher)

## Ressalvas

(a preencher)

## Ideias e bugs

(a preencher)

## Perguntas para o Samuel

(a preencher)

## Commit

(a preencher)

## O que o agente que tentou quebrar achou

(a preencher depois da volta de quem tenta quebrar)

## A prova de verdade

(a preencher na prova à vista)

## Perguntas do Windows que o Samuel vê

(a preencher)

## O print que prova

(a preencher)
