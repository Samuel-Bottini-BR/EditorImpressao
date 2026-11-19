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
  `empacotar.py` nem no nome do arquivo.
- 19/11: código, testes e janela de prova feitos e no GitHub (commits abaixo). Rodada do GitHub disparada; resultado
  em "Testes". **Próximo:** a gerente manda a quem tenta quebrar; depois a sessão A à vista.

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

- **`core/windows.py` (novo): a peça única do Windows e a pasta segura.** Pedir a licença abre o próprio programa
  com o aviso de trabalho numa pasta de troca (`pedir_licenca()`), e o lado com licença faz só os passos do aviso
  (`atender_trabalho_de_administrador()`), de uma lista fechada: criar, conferir e apagar a pasta segura, gravar nela,
  criar e apagar tarefa, rodar um script. Mais: rodar e esperar com as letras certas, lançar solto com sinal de vida,
  ler tarefas, licenças e marcas sem licença, o segredo cifrado pelo Windows, a janela dona trazida para a frente.
  Toda resposta é "deu certo", "disse Não" ou "falhou" com o motivo em português; "deu certo" só depois de conferir
  (lendo de volta), e o desfecho do trabalho com licença vem do relatório, nunca só do código de saída.
- **`main.py`: a entrada do trabalho de administrador**, antes de tudo (antes do brasão e dos outros modos). O texto do
  argumento fica escrito no `main.py`, como os outros modos, porque importar a peça em toda abertura atrasava o brasão
  em ~100 ms (medido); um teste cobra que é o mesmo texto da peça.
- **`janela_de_prova.py` (novo): a janela de prova da sessão A** (as seis provas do plano), que só usa a peça.
- **Testes:** `tests/test_windows_peca.py` (31) e `tests/test_windows_janela_de_prova.py` (3).
- Nenhum chamador do programa mudou; nenhum item saiu da lista de exceções do porteiro; nenhum teste antigo mudou.
- **Não mexi** em `empacotar.py` nem no nome do arquivo do programa (vira pergunta, abaixo).

## Arquivos criados ou alterados

- `core/windows.py` (novo)
- `main.py`
- `janela_de_prova.py` (novo)
- `tests/test_windows_peca.py` (novo)
- `tests/test_windows_janela_de_prova.py` (novo)
- `relatorios/passo1-peca-unica-windows/` (este formulário, o print e os anexos)

## Como cumpri cada uma

- D-782: quem pede é o próprio programa (`pedir_licenca()` abre `programa_deste_processo()` com o aviso); o
  `main.py` atende sem janela nem brasão (`tests/test_windows_peca.py::test_o_trabalho_de_administrador_nao_abre_janela_nem_brasao`,
  `tests/test_windows_peca.py::test_o_main_atende_o_argumento_da_peca_antes_de_tudo`). **O nome "Editor de
  Impressão" na pergunta, pela leitura, não sai com o arquivo de hoje:** pergunta abaixo. A janelinha de antes da
  pergunta é do passo 3.
- D-767 e D-785: nenhum teste pede licença, cria tarefa ou mexe em Arquivos de Programas; isso fica na janela de prova,
  à vista (`tests/test_windows_peca.py::test_pedir_licenca_errado_para_antes_da_pergunta` garante que o pedido errado
  nem chega à pergunta). Ensaio da janela sem nenhuma pergunta: `prints/janela-de-prova-ensaio-sem-pergunta.png`.
- D-775 e D-798: entregue à gerente sem rótulo; a prova à vista vem depois de quem tenta quebrar.
- D-733: a tarefa que roda como o sistema e que a conta comum manda rodar (`xml_da_tarefa_do_sistema()`, com o
  descritor do ajudante lido de `atualizacao.QUEM_PODE_MANDAR_RODAR`); a prova é a pergunta 1 da sessão A.
- D-724: a leitura do nome na pergunta depende disto (sem certificado pago): ver "O que li".
- D-780: as leituras básicas sem licença (`ler_tarefa()`, `ler_licencas()`, `marca_existe()`); as duas trancas são do
  passo 4 (ressalva).
- D-722: a pergunta 3 da janela apaga a tarefa e a pasta de prova e a janela lê de novo que não existem.
- D-786: não mexe no processamento das páginas; mediu-se só o atraso do brasão (evitado).
- D-787: no PC, um arquivo de teste por vez; o conjunto inteiro no GitHub (rodada em "Testes").
- D-791, D-801 e D-802: porteiro passando (`tests/test_conferencias_codigo.py` e os outros, aqui e no GitHub); a lista
  de exceções não mudou.
- D-796: nada em `ui/`; só os arquivos do pedido.
- D-797: tudo no meu ramo; quem junta é a gerente.
- D-799: só o passo 1.
- D-605: nenhum teste antigo mudou; os que leem o `main.py` passam (`tests/test_decisoes_brasao.py`,
  `tests/test_decisoes_atualizacao.py`, `tests/test_botoes_em_portugues.py`).
- D-637: "Como fica para quem usa e no livro" acima: nada muda para o Kaique nem no PDF neste passo.

## Testes

- **No PC, um arquivo por vez** (19/11): `tests/test_windows_peca.py` 31 passaram;
  `tests/test_windows_janela_de_prova.py` 3; `tests/test_conferencias_codigo.py` 77; `tests/test_conferencias_pacote.py`
  20; `tests/test_conferencias_excecoes.py` 14; `tests/test_conferencias_protecao.py` 11;
  `tests/test_conferencias_mudancas.py` 21; `tests/test_conferencias_formulario.py` 34;
  `tests/test_conferencias_antes_do_commit.py` 12; `tests/test_conferencias_juiz.py` 9;
  `tests/test_conferencias_copia_inteira.py` 2; `tests/test_decisoes_brasao.py` 22; `tests/test_decisoes_atualizacao.py`
  38; `tests/test_botoes_em_portugues.py` 5. O repositório do PC continuou inteiro (`--is-shallow-repository` = false
  antes e depois).
- **No GitHub:** RODADA_AQUI
- **Achado de verdade nos testes:** a pasta de dados dos testes fica no D:, onde "Todos" têm controle total; a peça
  recusou a pasta de troca ali (certo). Os testes da peça usam uma pasta própria na pasta temporária da conta (no C:,
  como o programa de verdade), criada e apagada pelo próprio teste.

## Caminho e função

- O começo do programa com o argumento → `atender_trabalho_de_administrador()`.
- A janela de prova, cada prova → `pedir_licenca()`, `lancar_powershell_solto()`, `rodar_e_esperar()`,
  `rodar_tarefa()`, `ler_tarefa()`, `conferir_pasta_segura()`.
- Rodar um script (no trabalho com licença, ao ler uma tarefa, solto, na tarefa de prova) → `comando_do_powershell()`
  (o mesmo comando) e `_gravar_script()` (a mesma marca de UTF-8).
- A regra "a pasta de troca é só desta conta": o lado que pede e o lado com licença → `_problemas_da_pasta_de_troca()`.
- A regra "o passo é aceito": o lado que pede e o lado com licença → `_problemas_do_passo()`.
- O desfecho de todo pedido → `_desfecho_do_trabalho()` (pelo relatório).
- O XML da tarefa, o que a peça escreve e o que o Windows devolve → `ler_xml_da_tarefa()`.
- Provas de que os caminhos dão o mesmo resultado: `tests/test_windows_peca.py::test_o_xml_da_tarefa_ida_e_volta`,
  `tests/test_windows_peca.py::test_o_leitor_de_tarefa_le_o_que_o_windows_devolve`,
  `tests/test_windows_peca.py::test_a_regra_da_pasta_de_troca_recusa_outra_conta`,
  `tests/test_windows_peca.py::test_o_aviso_so_aceita_a_lista_fechada`,
  `tests/test_windows_peca.py::test_o_trabalho_com_licenca_faz_so_o_aviso`.
- **Ainda com conta própria (passos 3 a 5, como o plano manda; estão na lista de exceções):** `atualizacao.py`
  (inclusive `xml_da_tarefa()`, com o mesmo desenho de `xml_da_tarefa_do_sistema()` até o passo 3),
  `core/_testes_a_distancia_windows.py`, `core/testes_a_distancia.py`.

## Máquina ou olho

- Máquina: tudo o que está em "Testes" (leituras de verdade do Windows, sem mudar nada, e a lógica em volta).
- À vista (não feito; é da sessão A com o Samuel): a pergunta do Windows ("Sim", "Não", com o navegador na frente),
  criar e apagar a pasta segura e a tarefa de prova, a tarefa rodando como o sistema, a conta comum sem gravar.
- Olho: o nome que a pergunta mostra (foto do celular, se ele quiser).

## Ressalvas

- **Nada do que pede licença rodou.** Pedir a licença, a pasta segura em Arquivos de Programas, criar e apagar tarefa
  e o lado com licença fazendo os passos só foram testados até a porta: aqui (sem licença) ele recusa; no GitHub (o
  Windows da nuvem roda como administrador, sem pergunta) ele roda um script. Só a sessão A prova o resto.
- **O nome na pergunta:** pela leitura, aparece "EditorImpressao.exe", não "Editor de Impressão". Pergunta abaixo.
- **Pergunta 3 (navegador na frente), pela documentação:** a pergunta deve vir piscando na barra de tarefas, não no
  meio da tela. A peça tenta trazer a janela para a frente e diz se conseguiu (`janela_na_frente`), sem truque. Se a
  sessão A confirmar, o plano para (risco 1); a pergunta pronta está abaixo.
- **O programa montado para a sessão A** tem de sair deste commit (a entrada nova no `main.py`). O empacotador leva a
  peça (o `main.py` a importa) e não leva a janela de prova; não montei o pacote.
- **Dono da pasta segura:** se o Windows estiver configurado para dar o dono ao administrador (e não ao grupo
  Administradores), a pasta segura não confere e é apagada de novo (falha dita, nada pela metade). Na configuração de
  fábrica o dono é o grupo. Não testado.
- **Política de scripts** (empresa) ou antivírus que barre o PowerShell: o script falha e a resposta diz "falhou".
- **Lançar solto num grupo de processos que fecha os filhos:** a peça lê o grupo e recusa. No PC (dentro da conversa
  do Claude) o grupo solta sozinho; aberto pelo atalho não há grupo. Os outros casos não foram vistos.
- **Os testes da peça** criam e apagam uma pasta própria na pasta temporária da conta (fora do projeto), como o pytest
  faz; só a que o próprio teste criou.
- **Lido × deduzido:** o que tem endereço em "O que li" foi lido; o nome na pergunta e a pergunta 3 são dedução, a
  provar.
- **Para o passo 4:** as leituras do serviço de entrar de longe, da conta e das duas trancas (a peça já dá o rodar e
  esperar e o ler; a leitura específica é da peça 3).

## Ideias e bugs

- **Bug para a Lista de bugs (19/11):** o disco D: do PC do Samuel dá controle total a "Todos" (visto em
  `saida_teste` deste ramo). Já era conhecido (plano v1, item 59); fica anotado que é por isso que a pasta de troca
  não pode ficar no D:. Não impede o passo.
- **Ideia para a Lista de espera:** a janelinha de antes da pergunta (passo 3) ter um botão "Continuar", para o
  programa ganhar a frente com o clique dele (resolveria o caso do navegador na frente). Está como pergunta abaixo.

## Perguntas para o Samuel

**Pergunta 1. O nome que aparece na pergunta do Windows.** É a pergunta "Deseja permitir que este aplicativo faça
alterações?", que vai aparecer uma vez, na primeira vez que o Kaique abre o programa. Você escolheu, em 18/11, que nela
apareça "Editor de Impressão" em vez de "Windows PowerShell". A troca de quem pede já está feita: agora é o próprio
programa. Mas a Microsoft escreve que, num programa sem o certificado pago, a pergunta mostra o **nome do arquivo** do
programa, e o arquivo hoje se chama "EditorImpressao.exe" (tudo junto, sem acento).
- Foto da Microsoft de um programa sem certificado (faixa amarela; o nome fica logo abaixo da faixa, borrado por
  eles): `anexos/pergunta-do-windows-sem-certificado-foto-da-microsoft.png`. Com certificado (faixa cinza, nome
  bonito): `anexos/pergunta-do-windows-com-certificado-foto-da-microsoft.png`.
- Situação: é escolha, não defeito. O Kaique ainda não vê esta pergunta; a prova na sua tela mostra como fica.
- **O que você escolhe:**
  - A (sugestão): fica "EditorImpressao.exe". Nada mais muda.
  - B: o arquivo passa a se chamar "Editor de Impressão.exe", e a pergunta mostra esse nome. Muda o nome do programa
    instalado (o atalho continua igual); nome com acento e espaço pede testar de novo a instalação e a atualização.
  - C: comprar o certificado: aparece "Editor de Impressão" e a faixa fica cinza. Custa todo ano.
  - Só comentário.
- Sugestão à gerente: levar depois da sessão A, com a foto de verdade (decisão de 18/11, D-782).

**Pergunta 2 (preparada; levar só se a sessão A confirmar). Quando o Kaique está em outra janela.** Na primeira vez
que ele abre o programa, se clicar no navegador enquanto o programa carrega, o Windows não põe a pergunta no meio da
tela: o escudo fica piscando na barra de tarefas (regra do Windows, para não roubar a tela de quem faz outra coisa).
Situação: a confirmar na sua tela.
- **O que você escolhe:**
  - A (sugestão): a janelinha que avisa antes da pergunta ganha um botão "Continuar"; quando ele clica, o programa
    fica na frente e a pergunta vem no meio da tela.
  - B: a janelinha diz também "Se a pergunta não aparecer, clique no escudo que pisca na barra de tarefas".
  - C: fica como está.
  - Só comentário.

## Commit

COMMIT_AQUI

## O que o agente que tentou quebrar achou

(a preencher depois da volta de quem tenta quebrar)

## A prova de verdade

(a preencher na sessão A, à vista)

## Perguntas do Windows que o Samuel vê

- Nesta entrega: 0 (nada pediu licença).
- Na sessão A: 3 (pergunta 1 "Sim", pergunta 2 "Não", pergunta 3 "Sim" com o navegador na frente), como o plano
  diz. Antes, a gerente monta o programa deste commit no C: (0 perguntas).

## O print que prova

- `prints/janela-de-prova-ensaio-sem-pergunta.png`: a janela de prova desenhada fora da tela, depois das provas sem
  pergunta (1: o script solto rodou depois de quem o lançou fechar; 5: "não achei o programa", sem caixa do Windows;
  6: a resposta do Windows com acento certo, aqui "não pode encontrar", porque a tarefa de prova ainda não existe).
  Nenhuma tela do programa do Kaique mudou. O print das perguntas 1 a 3 é da sessão A.
