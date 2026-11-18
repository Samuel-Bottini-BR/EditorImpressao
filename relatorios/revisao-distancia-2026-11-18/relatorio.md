# Revisão dos testes à distância e do pedido de licença (18/11/2026)

**Do que se trata.** É a parte do programa que, no notebook do Kaique, pede a licença do Windows ("Deseja permitir...?"),
instala o servidor de entrar de longe, cria a conta escondida dos testes, abre a porta só para a rede do Tailscale, liga e
desliga isso pela caixinha das Configurações, e desfaz tudo quando o programa é desinstalado.

**A conclusão em uma frase.** Os defeitos da etapa 5 não são sete acidentes: vêm de quatro escolhas da estrutura, e
consertar um por um deixaria as quatro de pé. (1) A tela mostra o que o programa *anotou*, não o que o Windows *tem*.
(2) Ligar para no meio e deixa o computador pela metade, sem desfazer. (3) O programa não consegue ler a resposta de
quem fez o trabalho com licença (o pedido lê o erro errado; o relatório nasce numa pasta que ele não lê). (4) As
licenças de pasta foram feitas à mão com um comando que estraga os arquivos que já estão dentro. Por cima disso, nenhuma
peça que fala com o Windows tinha sido rodada de verdade antes da etapa 5: os testes automáticos trocam essa peça por uma
de mentira (está escrito no topo do próprio arquivo: "nao foi rodada").

Feito só lendo o código (ramo `obra-2026-10-26`, `b74a94e2`), os registros da etapa 5 e três provas pequenas na pasta de
rascunho desta conversa, **sem administrador, sem janela na tela do Samuel e sem tocar no que a etapa 5 ligou**.
Nenhuma linha do programa mudou.

As três provas que este trabalho rodou (máquina, no PC do Samuel, 18/11/2026 11:55 a 12:05):

- **A tranca da pasta estraga os arquivos de dentro (causa provada).** O mesmo comando do programa, numa pasta de
  rascunho: o arquivo que já estava lá ficou com a lista de licenças **vazia** (ninguém lê nem grava) e o comando disse
  "deu certo" (código 0). O mesmo comando só na pasta, sem passar nos arquivos, deixou o arquivo certo (Sistema e
  Administradores tudo, Usuários só lê). Script: `provas/prova_tranca_da_pasta.sh`.
- **Senha com acento vira outra senha (defeito novo, provado).** O jeito que o programa manda a senha ao Windows trocou
  "maçã-Ação" por "maþÒ-AþÒo" (o "ç" chegou como "þ", o "ã" como "Ò"). Com um texto de exemplo, não uma senha.
  Script: `provas/prova_acento.py`.
- **O estado de verdade dá para ler sem pedir licença.** Uma conta comum, sem administrador, lê se um serviço está
  rodando e liga com o Windows, se uma conta está ativa, se uma regra do firewall está ligada e para quais endereços, quais
  portas estão abertas e quais tarefas existem. Só "o recurso do Windows está instalado?" pede administrador (dá para
  saber pelo serviço). Lido em coisas do Windows que não são nossas (o serviço de impressão, a conta "Administrador"
  desligada, uma regra de fábrica do firewall).

---

## 1. Cada coisa que esta parte pede ao Windows

Para cada uma: onde está, como ela falha no Windows de verdade (com a fonte), o que o programa faz hoje e o que devia
fazer. "Etapa 5" = prova no PC do Samuel em 18/11 (`saida_teste\etapa5\registros\` e o ONDE-PAREI da etapa 5).

### 1.1 O pedido de licença ("Deseja permitir...?")
**Onde:** `core/_testes_a_distancia_windows.py`, `_rodar_elevado` (linhas 81 a 100). Usado pela primeira abertura, pelo
ligar e pelo desligar (todos passam por `aplicar_no_windows`).

**Como falha:**
- A pessoa clica "Não" ou fecha: o Windows responde "cancelado" (erro 1223). Fonte: documentação do `ShellExecuteEx` (Microsoft).
- O Windows não consegue mostrar a pergunta (programa numa área de trabalho que não é a de verdade): caixa crua "Não há
  suporte para o pedido". Etapa 5, fase 3.1.
- O programa não está na frente: a pergunta não aparece no meio da tela (fica para trás, no mais provável piscando na
  barra de baixo), ninguém clica, e depois de ~1 min 30 s volta como falha. Etapa 5, fase 3 pela opção (a): "não apareceu
  nada". A prova de fora do programa (sem janela) mostrou a pergunta na hora. **A provar** onde exatamente ela foi.
- A pergunta pede senha de outro administrador (conta do Kaique sem poder de administrador). O trabalho roda **em outra
  conta**: a senha cifrada pela conta do Kaique não abre nela (ver 1.2) e o ligar falha sempre. Lido no código; a provar.
  Pela D-716 a conta dele é de administrador, então é caso raro.
- O PowerShell é chamado só pelo nome, sem o caminho inteiro (`powershell.exe`, linha 90): o Windows procura o arquivo;
  e a pergunta mostra "Windows PowerShell" e não "Editor de Impressão".
- Uma política do computador (Group Policy) que proíbe scripts vence a opção `-ExecutionPolicy Bypass`. Fonte:
  `about_Execution_Policies` (Microsoft). Num notebook de casa é raro.
- O antivírus pode barrar um PowerShell escondido, com "Bypass" e texto em base64 (é o desenho que eles vigiam).
  Na etapa 5 o Defender não reclamou (`antivirus-fase7.txt` vazio); o do Kaique é outro (D-725).

**Hoje:** o erro é lido com `ctypes.get_last_error()` sobre `ctypes.windll`, que não guarda o erro (falta
`use_last_error=True`; fonte: documentação do `ctypes`, Python). Resultado: **toda falha vira 0 = "deu certo"**
(etapa 5: o Windows disse erro 2, o programa leu 0). Falta `SEE_MASK_FLAG_NO_UI` (fonte: `SHELLEXECUTEINFO`, Microsoft),
por isso a caixa crua. Sem janela dona (`hwnd` vazio). Espera **sem limite** (`WaitForSingleObject` com `INFINITE`)
**no fio da tela** (ver defeito novo N2). Se o Windows não devolver o processo, o código fica 0 = "deu certo".

**Devia:** ler o erro certo; esconder a caixa crua e dizer em português ("Você clicou Não; nada mudou." · "O Windows não
mostrou a pergunta; tente de novo com o programa na frente."); dar a janela do programa como dona e trazê-la para a frente
antes de pedir; chamar o PowerShell pelo caminho inteiro do Windows; esperar com limite, fora do fio da tela, com uma
janela "Esperando o Windows..." que diz o que está acontecendo; e só contar como feito o que o relatório do script diz
que foi feito (1.3), nunca o código de saída sozinho.

### 1.2 A senha entregue ao Windows
**Onde:** `_senha_cifrada_pelo_windows` (linhas 45 a 58) e o começo do script (`montar_script`, linhas 626 a 632).

**Como falha:**
- **Senha com acento ou cedilha vira outra senha** (provado agora; defeito novo N3). O Python manda o texto numa
  codificação e o PowerShell lê em outra.
- A senha é cifrada pela conta de quem abriu o programa; se o trabalho com licença rodar em outra conta (1.1), ela não
  abre ("Chave inválida"). O script morre na primeira linha, antes de anotar qualquer passo.
- A senha não passa pelas regras de senha do Windows daquele computador (tamanho, complexidade): a conta não é criada.
  No Windows Home de fábrica não há regra; num computador de empresa, há.
- A pessoa erra uma letra ao digitar: a conta nasce com a senha errada, o Samuel não entra e ninguém sabe por quê
  (a janela tem um campo só). Ver pergunta 1.

**Hoje:** a senha não vai para a linha de comando nem fica em disco em claro (isso está certo e foi conferido na etapa 5).
Erros viram o aviso genérico.

**Devia:** mandar o texto numa codificação só dos dois lados (UTF-8 declarado nos dois); conferir antes, sem licença,
se a senha passa nas regras do Windows e dizer em português se não passa; e (se o Samuel quiser) pedir a senha duas vezes.

### 1.3 A pasta temporária e o relatório do script
**Onde:** `aplicar_no_windows` (linhas 105 a 125).

**Como falha:** no Python 3.14 a pasta de `tempfile.mkdtemp` nasce só para Sistema, Administradores e "o dono"
(fonte: documentação do Python, `os.mkdir`, "Changed in version 3.13: Windows now handles a mode of 0o700", correção de
segurança CVE-2024-4030). O relatório é criado pelo PowerShell com licença, cujo dono é "Administradores"; o programa,
sem licença, não lê. Etapa 5, fases 7 e 10: `PermissionError`.

**Hoje:** a leitura falha dentro da própria mensagem de erro, o programa cai no aviso genérico, perde o que o script disse,
e a tela mostra "Ligado, mas falta a senha" com 8 de 9 passos feitos. A pasta (com o relatório que o Kaique nem consegue
apagar) fica para trás a cada pedido (defeito novo N9).

**Devia:** o relatório nasce numa pasta que o programa cria do jeito comum (herda as licenças da pasta da conta, que
incluem a própria conta), e o script ainda dá leitura ao arquivo para a conta que pediu. O programa lê o relatório
**sempre** (deu certo ou não), mostra na tela, passo a passo, em português, e apaga a pasta no fim.

### 1.4 O caderninho do antes e a tranca da pasta
**Onde:** `core/testes_a_distancia.py`, `_comando_anotar_o_antes` (250 a 286), `_comando_criar_e_proteger_a_pasta`
(353 a 361), `_comando_proteger_a_pasta` (364 a 371).

**Como falha:** **provado agora**: o comando passa nos arquivos de dentro (`/T`) com licenças que só valem para pasta;
nos arquivos ele tira as licenças herdadas e não põe nenhuma: a lista fica **vazia** e ninguém lê nem grava, nem o
administrador, nem o Sistema. O comando devolve 0, então a conferência do código de saída (linha 371) não pega.
Segundo jeito de falhar: a pasta-mãe `C:\ProgramData\EditorImpressao` nasce na instalação, pelo gancho que roda **sem
licença** (achado B1), então o dono dela é a conta de quem instalou; e qualquer conta pode criar pastas e arquivos
dentro de pastas do ProgramData (lido agora: "Usuários: criar arquivos e pastas" na raiz do ProgramData). Ver N11.

**Hoje:** na primeira abertura o `desfazer.ps1` nasce certo (pasta vazia na hora da tranca). No primeiro ligar, a tranca
roda depois de gravar o `antes.json` e estraga **os dois**. Daí em diante, para sempre: o último passo do ligar falha
(etapa 5, fase 7), o primeiro do desligar falha (fase 10), e a tarefa do desfazer, que roda como o Sistema, **não
consegue nem ler o próprio script** (ver N1).

**Devia:** o que roda como o Sistema e o caderninho ficam num lugar que só administrador consegue criar e mudar, com as
licenças de fábrica do Windows, **sem nenhum comando de licença à mão nos arquivos** (por exemplo, uma chave do registro
do Windows em "HKLM\SOFTWARE", ou uma pasta própria em Arquivos de Programas fora da pasta do programa; os dois só deixam
o administrador gravar e as contas comuns não conseguem criar nada ali). Se ficar no ProgramData, a tranca é só na
pasta (os arquivos herdam), a pasta-mãe também é trancada, e o script confere que a pasta não é um atalho para outro
lugar antes de gravar.

### 1.5 Instalar o servidor de entrar de longe (OpenSSH)
**Onde:** `plano_de_ligar`, passo 2 (linha 411): `Add-WindowsCapability`.

**Como falha (fonte: Microsoft, "Get started with OpenSSH Server for Windows" e as falhas conhecidas dos "recursos sob
demanda"):** precisa da internet e do Windows Update (o arquivo vem de lá); sem internet, falha; com o Windows Update
desligado ou num computador preso a um servidor de atualização de empresa, falha (erro 0x800f0954); com outra
instalação do Windows pendente, falha ou pede reiniciar; e demora: na etapa 5 levou cerca de 13 min (10:40 a 10:53).

**Hoje:** os 13 minutos passam com a janela do programa parada (N2). Uma falha aqui é o aviso genérico.

**Devia:** dizer antes "isto baixa uma peça do Windows pela internet e pode levar até 15 minutos"; mostrar que está
trabalhando; dizer a causa quando falha ("sem internet", "o Windows Update está desligado"); e não deixar nada pela
metade (1.13). Pergunta 4: isso fere a D-727 ("nada baixado da internet na hora de instalar")?

### 1.6 Ligar o servidor com o Windows
**Onde:** passo 3 (linha 413).

**Como falha:** a porta 22 já está em uso por outro programa (outro servidor SSH): o serviço não sobe (erro 1067);
o serviço sobe mas cai depois por um `sshd_config` com erro (1.9).

**Hoje:** o erro sai do script; aviso genérico. **Devia:** conferir a porta antes e dizer qual programa a usa.

### 1.7 O firewall: fechar a porta larga e abrir só para o Tailscale
**Onde:** passos 4 e 5 (linhas 418 a 427).

**Como falha:**
- **Nunca foi provado que a regra funciona.** Na etapa 5 a entrada foi feita do próprio PC; o Windows não costuma
  filtrar a conversa do computador com ele mesmo, então a prova mostrou que a conta entra, não que **só** o Tailscale
  entra. A D-739 já deixava essa prova para depois. A provar com um segundo aparelho (pergunta 2).
- A regra é presa à placa de rede chamada "Tailscale". Se o Tailscale não estiver instalado na hora de ligar, ou se a
  placa trocar de nome ou for refeita numa reinstalação, a regra pode falhar ou deixar de valer. A provar.
- Se o firewall do Windows estiver desligado, ou trocado pelo de um antivírus (Norton, Kaspersky, Avast e outros
  desligam o do Windows), as nossas regras não valem: o servidor ouve em todas as redes (etapa 5: porta 22 em
  0.0.0.0) e a porta fica aberta para o Wi-Fi da casa, com senha.
- A regra larga do OpenSSH com outro nome, ou já apagada pelo dono: o passo 4 para tudo.

**Hoje:** nada disso é conferido. **Devia:** pôr uma segunda tranca no próprio servidor, que não depende do firewall:
"só a conta de testes, e só vinda de endereço do Tailscale" (`AllowUsers EditorTestes@100.64.0.0/10,...`; fonte: manual
do `sshd_config`, "USER@HOST ... CIDR address/masklen"). E provar as duas portas, a que entra e a que não entra.

### 1.8 A conta de testes e esconder a conta
**Onde:** passos 6 e 7 (linhas 434 a 455).

**Como falha:** regras de senha (1.2); já existe uma conta ou um grupo com esse nome (o programa para sem mexer, está
certo); o antivírus estranha conta escondida (D-725); o PowerShell de 32 bits não tem os comandos de conta (o programa é
de 64 bits, então não acontece hoje).

**Hoje:** funcionou na etapa 5 (conta só no grupo Usuários, escondida, entra pelo SSH). **Devia:** o mesmo, com a falha
dita em português e o desfazer da vez (1.13).

**O que a conta enxerga (D-717, D-743):** na etapa 5 ela leu e gravou no disco D: (dá "controle total a Todos"). Isso é
do disco, não do programa; a D-743 já manda conferir os discos do Kaique antes do primeiro teste. Um ponto a mais:
qualquer conta, inclusive a de testes, pode criar arquivos dentro das pastas do programa no ProgramData (1.4, N11);
a de testes também pode mandar o ajudante da atualização rodar (é de propósito, D-736).

### 1.9 O arquivo de configuração do servidor (`sshd_config`)
**Onde:** passo 8 e `_comando_por_o_bloco` (231 a 247).

**Como falha:** se o dono já tinha o OpenSSH e escreveu `PasswordAuthentication no` antes do nosso bloco, vale a linha
dele (no `sshd_config` vale **o primeiro** valor; fonte: manual do `sshd_config`) e a senha não entra; o arquivo pode ter
`Include` e outros `AllowUsers`. Só importa no computador que já tinha OpenSSH (B4).

**Hoje:** o bloco entra antes do primeiro "Match" (certo; conferido na etapa 5). **Devia:** pôr o bloco no começo do
arquivo e, depois de reiniciar o serviço, conferir com o próprio servidor (`sshd -T`) que a regra valeu.

### 1.10 A tarefa "desfazer" e a licença dela
**Onde:** `_comando_preparar_o_desfazer` (321 a 350), `xml_da_tarefa_do_desfazer` (289 a 306).

**Como falha:** o script que ela roda está na pasta estragada pela tranca (1.4): ela começa e não lê o script; o Agendador
desligado; a tarefa criada mas a licença não aplicada (o passo para no meio e a tarefa fica sem a negação da conta de
testes). Na etapa 5 a tarefa nasceu na primeira abertura; o "rodar" dela pela conta comum ainda não foi provado (fase 11,
com outro agente agora).

**Devia:** ver 1.4 (lugar seguro, sem licença à mão) e conferir, depois de criar, que a tarefa existe, aponta para o
script certo e tem a licença certa.

### 1.11 Desligar
**Onde:** `plano_de_desligar` (468 a 491), `desligar` (800 a 807), a caixinha (`ui/tela_configuracoes.py`, 383 a 393).

**Como falha:** o primeiro passo lê o caderninho estragado e para (etapa 5, fase 10); "Não" na pergunta; qualquer erro.

**Hoje:** grava "desligado" **sempre**, dê certo, dê errado ou a pessoa diga "Não" (N4); não avisa nada (N5); para no
primeiro erro, então um erro no começo deixa tudo ligado. Na etapa 5: a tela disse "Desligado." e o servidor continuou
rodando e ligando com o Windows, a porta aberta para o Tailscale e a conta ativa.

**Devia:** tentar os três passos mesmo se um falhar; depois, **ler o Windows** e mostrar o que está de verdade
("Desligado" só se o servidor está parado e não liga com o Windows, a regra não existe e a conta está desativada); se não
desligou, dizer em português o que ficou ligado e oferecer "Tentar de novo".

### 1.12 Desfazer ao desinstalar
**Onde:** `atualizacao.ao_desinstalar` (atualizacao.py 1560 a 1580), `mandar_desfazer` (810 a 823), `plano_de_desfazer`.

**Como falha:** o gancho de desinstalar roda sem licença e é cortado em 30 s (por isso ele só manda a tarefa rodar; o
desenho está certo); a tarefa não lê o script (1.4); o perfil da conta não sai se ainda estiver carregado; tirar o OpenSSH
pode pedir reiniciar. Ninguém vê o resultado: ele fica num registro na pasta trancada.

**Hoje:** com os testes ligados alguma vez, **nada é desfeito**: nem o OpenSSH, nem a conta, nem a regra, nem as duas
tarefas (a do ajudante, que roda como o Sistema, fica apontando para um programa que já não existe). Ver N1.

**Devia:** o script num lugar que o Sistema lê (1.4); a lista do que foi desfeito num lugar que a conta do Kaique lê; e,
na próxima vez que alguém olhar (o Samuel de longe não dá mais, porque o servidor saiu), a prova é a foto do Windows
depois de desinstalar, item por item (D-722).

### 1.13 A primeira abertura
**Onde:** `ui/testes_a_distancia_ui.primeira_vez_se_preciso` (124 a 176), `atualizacao.preparar_na_primeira_abertura`
(1460 a 1514), chamada pelo `main.py` antes de o programa começar a atender a tela (`app.exec()`).

**Como falha:** tudo de 1.1 a 1.10 junto, porque com a senha o preparo da atualização e os passos dos testes vão num
script só; o programa ainda não está atendendo a tela (a janela não se redesenha nem fecha: etapa 5, o "fechar" perdido
das 08:14).

**Hoje:** um "Não" ou uma falha viram "preparado" (o erro lido como 0, e a regra da D-749 cai no "vale o resultado da
pergunta inteira" quando o script nem rodou). A pergunta não volta (contra a D-741).

**Devia:** o mesmo porteiro de 1.1, com a janela do programa já na frente e atendendo; a resposta lida certa; e o preparo
da atualização separado do ligar dos testes dentro do script, de modo que uma falha num não apague o resultado do outro.

### 1.14 O estado que a tela mostra
**Onde:** `configuracoes.json` da conta (`%LOCALAPPDATA%`), chaves `testes_a_distancia_ligado` e `_pronto`;
`ui/tela_configuracoes._mostrar_estado_dos_testes` (368 a 381).

**Como falha:** o que fica ligado é do computador inteiro, mas a anotação é por conta do Windows (N7); "pronto" nunca
volta a "não" ao desligar (N8); "Ligado, mas falta a senha" aparece para qualquer falha, mesmo com o Windows todo ligado.

**Devia:** a tela pergunta ao Windows (sem licença, provado agora) e mostra isso. A anotação guarda só o que é da pessoa:
"o Kaique quer ligado?" e "a janela da senha já apareceu?".

---

## 2. Defeitos novos (achados nesta leitura)

Os já conhecidos (da etapa 5) ficam no fim, com o que esta leitura acrescentou a eles.

- **N1. Com os testes ligados uma vez, desinstalar não desfaz nada, e ligar e desligar falham para sempre.**
  `core/testes_a_distancia.py` 368 a 370. É o efeito da tranca provada agora (1.4) sobre a tarefa do desfazer: o Sistema
  também não lê o `desfazer.ps1` de lista vazia, então nenhum passo roda, nem o de apagar a tarefa da atualização.
  Prova da causa: `provas/prova_tranca_da_pasta.sh` (máquina, sem licença). O efeito na tarefa: lido no código, a
  confirmar quando o outro agente rodar a desinstalação (fase 11).
- **N2. A janela inteira fica parada enquanto o Windows trabalha.** `ui/tela_configuracoes.py` 389 e 391 e
  `ui/testes_a_distancia_ui.py` 117 e 170 chamam o ligar e o desligar no fio da tela; `_rodar_elevado` espera sem limite
  (linha 96). Na etapa 5 o ligar levou 14 min (10:39:56 a 10:53:33) com a janela sem responder; o Windows mostra "Não
  está respondendo" e o Kaique pode fechar à força no meio. Fere a regra "a interface nunca congela" (CLAUDE.md §3).
  Lido no código e pelos horários; ninguém fotografou a janela parada.
- **N3. Senha com acento ou cedilha vira outra senha.** `core/_testes_a_distancia_windows.py` 54 a 57 (o texto vai sem
  dizer a codificação). Provado agora: "ç" chega "þ", "ã" chega "Ò". O Samuel digitaria a senha certa e não entraria.
- **N4. Desligar com "Não" grava "desligado".** `core/testes_a_distancia.py` 805 e 806: a anotação vem antes de olhar o
  resultado, para qualquer resultado. Lido no código.
- **N5. O desligar nunca avisa nada.** `ui/tela_configuracoes.py` 391 joga fora o resultado. Etapa 5, fase 10.
- **N6. Ligar que falha no meio não desfaz o que fez.** `montar_script` (645: `throw` no primeiro erro) e não há passo de
  volta. Etapa 5, fase 7: servidor, porta e conta ligados, e a tela dizendo "falta a senha". (O sintoma era conhecido; o
  novo é que o desenho não tem o desfazer da vez.)
- **N7. O estado fica por conta do Windows, mas o que liga é do computador.** `configuracoes.py` linha 3 e 77 a 79. Em
  outra conta do mesmo computador: a tela diz "Ligado, mas falta a senha" com tudo ligado, a janela da senha aparece de
  novo e uma senha digitada ali troca a senha da conta de testes. Lido no código.
- **N8. "Pronto" nunca volta a "não".** `desligar` (800 a 807) não mexe nele; um ligar que falha também não. Lido no código.
- **N9. Cada pedido deixa uma pasta no TEMP que o Kaique não consegue apagar.** `aplicar_no_windows` (105 e 130 a 137): o
  `finally` apaga o script e a senha cifrada, mas não o relatório (dono: Administradores) nem a pasta. Os restos da etapa 5
  estão em `saida_teste\etapa5\temp\editor-testes-*`.
- **N10. Nada prova que só o Tailscale entra, e sem o firewall do Windows a porta fica aberta para o Wi-Fi.** Ver 1.7.
  O servidor ouve em todas as redes (etapa 5, porta 22 em 0.0.0.0 e ::) e a única tranca é o firewall.
- **N11. O Sistema roda um script numa pasta cuja pasta-mãe pode ser da conta comum.** A pasta
  `C:\ProgramData\EditorImpressao` nasce na instalação pelo gancho sem licença (B1); quem é dono da pasta-mãe pode trocar
  a pasta trancada de lugar e pôr outro `desfazer.ps1`, que a tarefa roda como o Sistema, e qualquer conta pode mandar
  essa tarefa rodar (licença "AU" na linha 317). E qualquer conta, inclusive a de testes, pode criar arquivos nas pastas
  do programa no ProgramData (lido agora na raiz do ProgramData). **A provar:** quem é o dono da pasta-mãe no PC do
  Samuel (só lendo, depois da limpeza da etapa 5). Toca também a pasta da atualização (`...\atualizacao`, que o ajudante
  lê como o Sistema): para o agente do atualizador conferir.
- **N12. A pergunta do Windows aparece como "Windows PowerShell".** `_rodar_elevado` linha 90. O Kaique vê um programa da
  Microsoft pedindo licença, e não o Editor de Impressão. Pergunta 5.
- **N13. Uma letra errada na senha não tem como ser vista.** A janela tem um campo só (`ui/testes_a_distancia_ui.py` 78).
  Pergunta 1.

**Os conhecidos, com o que esta leitura acrescentou:**
- Erro do pedido lido como 0, e a caixa crua: confirmados no código (1.1). Acrescento: o programa também conta "deu
  certo" quando o Windows não devolve o processo, e espera sem limite.
- Pedido sem janela dona que some da frente: confirmado (1.1); falta provar onde a pergunta foi.
- "Acesso negado" no `desfazer.ps1` e no `antes.json`: **causa provada** (1.4) e consequência maior (N1).
- Relatório que o programa não lê: causa confirmada na documentação do Python (1.3).
- Desligar que grava "desligado" sempre: confirmado, e também com "Não" (N4).
- Desinstalar deixa tudo para trás: confirmado pela causa (N1), e deixa também as duas tarefas.
- A conta de testes grava no D: com "Todos: controle total": é do disco (D-743).

---

## 3. Como a estrutura fica certa

**O que fica (está certo e foi provado na etapa 5):** o caminho (servidor do próprio Windows, só a conta de testes, com
senha, sem porta no programa, D-705/D-711); os planos de comandos num lugar só (`core/testes_a_distancia.py`); a senha
fora da linha de comando; a conta só no grupo Usuários e escondida; o bloco do `sshd_config` antes do "Match"; o gancho
de desinstalar que só manda a tarefa rodar; a negação da conta de testes na tarefa do desfazer.

**O que muda: uma peça só que fala com o Windows, com cinco obrigações.** Hoje são três funções soltas, cada uma com o
seu jeito de pedir, esperar e ler. Passa a ser uma peça, que a primeira abertura, o ligar, o desligar e o desfazer usam:

1. **Pedir licença de um jeito só e ler a resposta certa.** Erro lido como o Windows dá; sem caixa crua; a janela do
   programa como dona, trazida para a frente antes; PowerShell pelo caminho inteiro; espera com limite; fora do fio da
   tela, com uma janela que diz "Esperando o Windows. Isto pode levar até 15 minutos." e não deixa clicar no resto.
2. **O relatório volta sempre.** O script escreve, passo a passo, num lugar que o programa lê; o programa mostra o que
   foi feito e o que falhou, em português, deu certo ou não. Código de saída sozinho não decide nada.
3. **Tudo ou nada.** O ligar anota o que cada passo fez **nesta vez**; se um passo falha, o próprio script desfaz, de
   trás para frente, só o que fez nesta vez (o que já existia antes fica, pelo caderninho). O desligar tenta todos os
   passos e diz o que ficou. O computador nunca fica pela metade sem a tela dizer.
4. **A tela mostra o Windows, não a anotação.** Uma função "como está agora" lê, sem pedir licença, o serviço, a conta,
   a regra e a porta (provado que dá) e devolve uma de quatro situações: **Desligado** · **Ligado** · **Ligado pela
   metade** (com o que falta, e "Tentar de novo" e "Desligar tudo") · **Não deu para saber**. Ela roda ao abrir as
   Configurações e depois de cada ligar e desligar. A anotação guarda só o que é da pessoa: "o Kaique quer ligado?" e "a
   janela da senha já apareceu?" (esta, por computador, para não pedir a senha de novo noutra conta).
5. **O que roda como o Sistema mora num lugar seguro de fábrica.** O script do desfazer e o caderninho saem da pasta do
   ProgramData e vão para um lugar que só administrador cria e muda, com as licenças de fábrica do Windows (chave do
   registro em "HKLM\SOFTWARE" ou pasta própria em Arquivos de Programas). Nenhum comando de licença à mão em arquivo.

**Mais quatro acertos que entram junto:** a senha em UTF-8 dos dois lados e conferida nas regras do Windows antes;
a segunda tranca no servidor ("só a conta de testes, só vinda do Tailscale"), que vale mesmo sem o firewall; a conferência
do servidor depois de configurar (`sshd -T`); e a pasta temporária apagada no fim.

**O que é remendo e o que é solução limpa.** Remendo seria: pôr `use_last_error`, trocar `mkdtemp` por `mkdir`, tirar o
`/T` e mudar a ordem da anotação do desligar. Cada um é uma linha e cada um passa no teste do seu caso; mas a tela
continuaria mostrando a anotação, o computador continuaria podendo ficar pela metade, a janela continuaria parada 14
minutos e o Sistema continuaria rodando script de uma pasta que a conta comum alcança. A solução limpa é a peça única
acima, porque as cinco obrigações moram num lugar só e todos os caminhos passam por ela (CLAUDE.md §11.12).

**O que muda para o Kaique:** na primeira abertura e ao ligar, uma janelinha diz que está esperando o Windows e quanto
pode demorar; se ele clicar "Não", aparece "Nada mudou" e a pergunta volta na próxima abertura (D-741); nas
Configurações, a frase diz o que o computador tem de verdade. Nada muda nos livros nem no PDF. Nada do que já foi
escolhido e testado muda, a não ser o que as perguntas abaixo pedem.

**Testes automáticos:** os de hoje (planos de comandos com peça de mentira) continuam valendo para o texto dos planos, mas
pela D-767 **não provam** que funciona. A peça única ganha as provas de verdade da seção 4, rodadas à vista.

---

## 4. Como provar cada peça de verdade e à vista no PC do Samuel (D-767)

Tudo **depois** de o outro agente terminar a limpeza da etapa 5, com o programa na tela de verdade, na frente, e o
Samuel olhando. Nenhuma área escondida, nenhuma janela empurrada para fora da tela. Cada prova é pequena, roda o código de
verdade da peça nova (não uma cópia) e termina desfazendo o que pôs. Em cada uma, antes de rodar, a gerente diz a ele o
que vai aparecer.

| # | O que prova | Perguntas do Windows | O que ele vê | Tempo |
|---|---|---|---|---|
| P1 | O pedido de licença: "Sim", "Não", fechar a pergunta e o programa atrás de outra janela. Cada caso, a frase certa na tela. O trabalho com licença só escreve um arquivo de prova. | 4 | a janelinha "Esperando o Windows", a pergunta no meio da tela, a frase do resultado | 5 min |
| P2 | O relatório volta e o programa lê (no mesmo P1) | 0 | a lista dos passos na tela | — |
| P3 | A tranca do lugar seguro: o administrador grava; a conta comum lê e não grava; o Sistema lê | 2 | uma janela com "leu / não gravou / o Sistema leu" | 3 min |
| P4 | A senha com acento entra igual (com uma senha de prova, que não é a dos testes, digitada por ele; apagada no fim) | 2 | "a senha entrou igual" | 3 min |
| P5 | "Como está agora" diz "Desligado" no computador limpo | 0 | a frase nas Configurações | 1 min |
| P6 | Ligar sem internet (cabo e Wi-Fi tirados): o programa diz "sem internet" e não deixa nada ligado | 1 | a frase da falha; P5 de novo diz "Desligado" | 5 min |
| P7 | Ligar de verdade, com a senha dele, pelas Configurações; a janela não para; a conta entra pelo comando de longe | 1 | a janelinha de espera com o tempo, e depois "Ligado" | 15 a 20 min |
| P8 | Só o Tailscale entra: do celular com o Tailscale, entra; do celular só no Wi-Fi, não entra (pergunta 2) | 0 | o celular dele | 10 min |
| P9 | Desligar com "Não" (a tela continua "Ligado") e com "Sim" (a tela diz "Desligado" e o Windows confirma) | 2 | a frase muda só quando desligou | 3 min |
| P10 | Ligar de novo e trocar a senha | 1 | "Ligado"; a senha nova entra, a velha não | 3 min |
| P11 | Desinstalar à vista (barra de progresso do Windows); depois a foto do Windows: sem servidor, sem conta, sem regra, sem tarefas, projetos intactos | 1 | a barra do desinstalar e a lista do que saiu | 15 min |

Total: cerca de 14 perguntas do Windows e 1h20 a 1h30, em duas ou três sentadas (P1 a P6 numa; P7 a P10 noutra; P11 no
fim). O teste grande da versão (a etapa 5 de novo) vem só depois, para confirmar.

---

## 5. Perguntas para o Samuel

(No formato do CLAUDE.md §11.13. Faltam os prints no modelo do girar: estas perguntas são de janelas que ainda não
existem; a gerente pede o print de prévia ao agente que construir, ou leva com a foto da janela de hoje.)

**Pergunta 1. A senha dos testes digitada duas vezes.**
- Do que se trata: na primeira vez que o programa abre no notebook do Kaique, uma janela pequena, "Testes à distância",
  pede a senha que você passou a ele (a mesma janela abre em Configurações > Testes à distância > "Pôr a senha dos testes").
- O que acontece hoje: há um campo só, com pontinhos. Se o Kaique errar uma letra, a conta de testes nasce com a senha
  errada, você não consegue entrar e nenhum dos dois sabe por quê. É um risco do jeito de hoje, não um defeito achado.
- O que você escolhe: **(a) dois campos, "Senha" e "Repita a senha"; se forem diferentes, a janela avisa e não segue
  (sugestão).** O Kaique digita duas vezes, uma vez só na vida. · (b) um campo só, como hoje. · Só comentário.
- De onde veio: escolha de agente, sem pedido seu; o Windows e a maioria dos programas pedem a senha nova duas vezes.
- Situação: só ideia. Nada do que já funciona muda.

**Pergunta 2. Como provar que só a rede do Tailscale entra.**
- Do que se trata: o programa abre a porta de entrar de longe só para a rede do Tailscale. Na prova de hoje no seu PC, a
  entrada foi feita do próprio PC, e isso não prova que a porta está fechada para o Wi-Fi da casa.
- O que você escolhe: **(a) provar no seu PC com o seu celular: com o Tailscale ligado no celular, entra; com o celular
  só no Wi-Fi, não entra (sugestão).** Precisa do Tailscale e de um aplicativo de entrar de longe no celular (por
  exemplo o Termius, grátis); uns 10 minutos. · (b) deixar para o primeiro teste no notebook do Kaique, como estava
  combinado em 17/11. · Só comentário.
- Situação: a prova da porta ainda não foi feita em lugar nenhum.

**Pergunta 3. Se ligar os testes der erro no meio.**
- Do que se trata: ligar os testes à distância (na primeira abertura ou em Configurações) faz nove coisas no Windows.
  Hoje, se a nona falha, as oito primeiras ficam ligadas e a tela diz "falta a senha". Foi o que aconteceu no seu PC hoje
  de manhã.
- O que você escolhe: **(a) se uma falhar, o programa desfaz sozinho o que fez naquela vez, deixa o computador como
  estava e diz o que falhou (sugestão).** · (b) deixa o que deu certo ligado, diz na tela "Ligado pela metade" e o que
  falta, com o botão "Tentar de novo". · Só comentário.
- Nas duas, a tela passa a mostrar o que o computador tem de verdade. Situação: é defeito do programa e vai ser
  consertado de qualquer jeito; a escolha é só o que fazer com o que já foi feito.

**Pergunta 4. A peça de entrar de longe vem da internet na hora de ligar.**
- Do que se trata: a peça do Windows que deixa você entrar de longe (o servidor de entrar de longe da Microsoft) não vem no
  nosso instalador: o programa pede ao Windows Update na hora de ligar os testes. No seu PC levou 13 minutos. Sem
  internet, não liga. Em 16/11 você decidiu "se tiver qualquer coisa que o kaique precise, ele tem que estar no
  instalador".
- O que você escolhe: **(a) continua vindo do Windows Update, e o programa avisa antes que precisa de internet e pode
  levar até 15 minutos (sugestão: é o jeito que a Microsoft manda fazer e é ela quem mantém a peça em dia).** · (b) pôr a
  peça dentro do nosso instalador (a Microsoft publica uma versão para isso); o instalador fica maior e as correções de
  segurança dela passam a vir das nossas versões. · Só comentário.
- Situação: funciona assim hoje; a pergunta é se vale a sua regra de 16/11 também para ela.

**Pergunta 5. O nome que aparece na pergunta do Windows.**
- Do que se trata: quando o programa pede licença, o Windows mostra "Deseja permitir que este aplicativo faça alterações
  no seu dispositivo?" com o nome **"Windows PowerShell", Editor verificado: Microsoft Windows**, e não "Editor de
  Impressão". O Kaique pode estranhar.
- O que você escolhe: **(a) deixar assim, e a janelinha de espera do programa diz antes "O Windows vai perguntar se pode
  deixar o Windows PowerShell fazer alterações. Clique em Sim." (sugestão).** · (b) o próprio Editor de Impressão pedir: o
  Windows mostra "Editor de Impressão" com a faixa amarela "Editor desconhecido" (o programa não tem o certificado pago do
  Windows, D-724). · Só comentário.
- Situação: é assim hoje; não é defeito, é como o Windows mostra.

---

## Ressalvas

- O efeito do N1 na tarefa do desfazer é lido no código; a causa está provada. Confirma quando o outro agente rodar a
  desinstalação.
- N11 depende de quem é o dono da pasta `C:\ProgramData\EditorImpressao` no PC do Samuel; não li para não tocar no que a
  etapa 5 está limpando.
- Onde a pergunta do Windows foi quando o programa estava atrás (barra de baixo ou outro lugar) ainda não está provado.
- A regra do firewall presa à placa do Tailscale (o que acontece se a placa mudar) não foi provada.
- Fontes citadas de memória da documentação (Microsoft, Python, OpenSSH), não baixadas nesta tarefa; as três provas
  desta tarefa foram rodadas de verdade.
