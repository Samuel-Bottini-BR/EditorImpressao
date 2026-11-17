# Desinstalar tira o que os testes à distância puseram (D-731) e os defeitos B2, B3, B4

**O que é.** Quando o Kaique desinstalar o Editor de Impressão, o notebook volta a ser como era antes: sai o comando
de longe (o Servidor OpenSSH, só se foi o programa que o instalou), a regra do firewall, a conta de testes escondida e
a pasta dela. Os livros e os projetos do Kaique ficam. Ninguém precisa responder pergunta nenhuma a mais.

**Situação.** PRONTO PARA CONFERIR. Construído e provado com o Windows de mentira (17/11/2026). Nada foi feito no Windows
de verdade. Ramo `desinstalar-b-2026-11-17`, commits `47d96ffb` (provas) e `65303058` (código), sobre `997a3085`.

## O que mudou

1. **O caderninho do antes.** O primeiro passo do `ligar`, já com a licença de administrador, anota o que o computador
   já tinha em `C:\ProgramData\EditorImpressao\testes-a-distancia\antes.json`: o OpenSSH, como o serviço ligava, a regra
   larga do firewall, uma conta com o nosso nome, a chave UserList e o que havia na pasta `C:\ProgramData\ssh`. Isso
   acontece só na primeira vez. A pasta fica com dono "administradores" e só de leitura para as contas comuns. Um
   caderninho que não foi gravado pelo sistema nem por um administrador não vale e é gravado de novo.
2. **A tarefa "desfazer"** (alternativa B, D-733). O último passo do `ligar` grava o script do desfazer e cria a tarefa
   `EditorImpressao\Desfazer testes a distancia`. Ela roda como o sistema, escondida e sem gatilho. Pode mandá-la rodar
   quem entrou no Windows, menos a conta de testes, que é negada (D-717). O script é exatamente o `plano_de_desfazer`,
   o mesmo da etapa 5 (D-722): uma regra só.
3. **O gancho de desinstalar** (`atualizacao.ao_desinstalar`) só manda a tarefa rodar (`schtasks /Run`, no máximo 20 s)
   e volta. Depois apaga a tarefa da atualização, como antes. Sem a tarefa, porque os testes nunca foram ligados, ele
   só anota no registro.
4. **O desfazer só tira o que foi nosso:**
   - o OpenSSH, a regra larga e o que nasceu na pasta `ssh` só saem se o caderninho diz que não existiam; sem
     caderninho, o OpenSSH nunca sai;
   - a conta só sai se tem a nossa descrição e o caderninho não anotou uma conta de outro;
   - o perfil é achado pelo número de identidade da conta (SID), não pelo nome da pasta;
   - o `sshd_config` sai pelas linhas-marca; a linha de fábrica `#PasswordAuthentication yes` fica, e o arquivo
     volta igual, letra por letra;
   - antes de apagar, ele para o comando de longe e fecha o que a conta de testes estiver rodando;
   - um passo que falha não para os outros; o caderninho e a tarefa só se apagam se tudo deu certo;
   - cada passo vai para `o-que-foi-desfeito.txt` na mesma pasta (a lista da D-722).
5. **B2.** As linhas do `ligar` vão entre as marcas e antes do primeiro `Match` do `sshd_config`.
6. **B3.** Ligar de novo reativa a conta nossa e troca a senha. Uma conta com o nosso nome que não é nossa faz o
   `ligar` parar sem mexer nela. A regra do firewall e as linhas do `sshd_config` não se repetem.
7. **B4.** Se o OpenSSH já era do dono, desligar devolve o serviço e a regra larga como estavam e tira as nossas
   linhas. Se foi o programa que o pôs, ou não há caderninho, desligar para o serviço como sempre.
8. **Achado e consertado (impedia a tarefa).** O script montado lia sempre o arquivo da senha. Sem ele, parava na
   primeira linha. Por isso o desligar e o desfazer, que não têm senha, nunca rodariam no Windows de verdade. Provado
   no código de antes: o script sem senha saiu com código 1, sem escrever o registro. Agora o arquivo só é lido quando
   um passo precisa da senha. O montador passou a ser um só (`montar_script`, em `core/testes_a_distancia.py`).

## Arquivos

- `core/testes_a_distancia.py`: caderninho, marcas, os três planos, `montar_script`, `Executor.rodar_a_tarefa` e
  `mandar_desfazer`.
- `core/_testes_a_distancia_windows.py`: usa o montador único; `rodar_a_tarefa_no_windows`.
- `atualizacao.py`: **só a função `ao_desinstalar`** (linhas 897 a 913). Mudaram a docstring (898 a 906) e as linhas
  novas 908 a 912 (`from core import testes_a_distancia`, `mandar_desfazer()` e o `registrar`). A linha 913,
  `apagar_tarefa()`, ficou igual.
- `tests/test_decisoes_desinstalar.py` (novo, 35 provas).
- A assinatura `ligar(senha)` e o `Executor.aplicar` (a pergunta de administrador) não mudaram.

## Caminho → função (uma regra num lugar só, §11.12)

| Caminho | Função |
|---|---|
| Desinstalar pelo Windows | `atualizacao.ao_desinstalar` → `testes_a_distancia.mandar_desfazer` → `Executor.rodar_a_tarefa` → a tarefa roda `montar_script(plano_de_desfazer())` |
| Etapa 5 no PC do Samuel | a mesma tarefa (`mandar_desfazer`), ou `plano_de_desfazer` → `Executor.aplicar` |
| Ligar (janela da senha, caixinha, botão "Pôr a senha") | `testes_a_distancia.ligar` → `plano_de_ligar` |
| Tirar as nossas linhas do `sshd_config` (ligar de novo, desligar do dono, desfazer) | `_comando_tirar_o_bloco` |
| "O OpenSSH foi nosso?" / "A conta é nossa?" | `_so_se_o_openssh_foi_nosso` / `_so_se_a_conta_foi_nossa` |
| Montar qualquer script (ligar, desligar, desfazer) | `montar_script` |

Prova de que a etapa 5 e a desinstalação usam o mesmo desfazer: `test_d731_ligar_cria_a_tarefa_desfazer_com_o_mesmo_plano`.
Ela abre o script gravado pelo `ligar` e cobra que ele seja igual a `montar_script(plano_de_desfazer())`.

## Como se provou sem tocar o Windows

- **O executor de mentira**, como na etapa 4, só anota.
- **O Windows de mentira do PowerShell.** O comando de cada passo roda num `powershell.exe` em que cada comando que
  muda o Windows (Stop-Service, Remove-LocalUser, icacls...) é trocado por uma função que só anota. No PowerShell, uma
  função com o mesmo nome ganha do comando de verdade. Os caminhos apontam para a pasta temporária do teste. Antes de
  rodar, o teste confere o texto e se recusa a rodar se houver um comando sem troca, o disco C:, o registro do Windows
  ou um serviço COM.
- **O leitor do PowerShell** confere que os três scripts montados não têm erro de escrita. Ele só lê, não executa.

## Cada prova de defeito falhando no código de antes

Rodei o arquivo novo com os três arquivos do código de antes (`997a3085`): 28 falham e 7 passam. As 7 que passam só
guardam o que já era certo (portátil, conta nova sem administrador, desligar do OpenSSH nosso). Saída inteira em
`prova-no-codigo-de-antes.txt`.

| Prova | Por que falhou no código de antes |
|---|---|
| `test_d731_desinstalar_manda_rodar_a_tarefa_desfazer` (a principal) | "o gancho de desinstalar não mandou rodar a tarefa desfazer": `ao_desinstalar` só apagava a tarefa da atualização |
| `test_d731_ligar_cria_a_tarefa_desfazer_com_o_mesmo_plano`, `..._a_conta_comum_manda_rodar...` | o `ligar` não criava tarefa |
| `test_d731_ligar_anota_o_antes_primeiro...` | não havia caderninho |
| `test_b2_as_linhas_do_ligar_vao_antes_do_match` | "B2: as linhas caíram dentro do bloco Match Group administrators" |
| `test_b3_ligar_de_novo_nao_repete_as_linhas` | 2 linhas `AllowUsers` em vez de 1 |
| `test_b3_ligar_depois_de_desligar_reativa_a_conta` | "ligar de novo parou no erro: A conta EditorTestes ja existe." |
| `test_b3_ligar_de_novo_refaz_a_regra_do_firewall` | só `New-NetFirewallRule`, sem apagar a de antes |
| `test_b4_desligar_devolve_o_openssh_que_ja_era_do_dono` | "B4: desligou o OpenSSH que era do dono" |
| `test_d731_sshd_config_sai_pelas_marcas...` | o desfazer procurava a linha solta `PasswordAuthentication yes` (apagava a de fábrica) |
| `test_d731_openssh_so_sai_se_foi_o_programa_que_pos` (2 casos) | tirava o OpenSSH do dono e sem caderninho |
| `test_d731_a_conta_so_sai_se_for_a_nossa` (2 casos), `..._de_outro_que_existia_antes_fica` | apagava qualquer conta EditorTestes |
| `test_d731_o_perfil_e_achado_pelo_sid` | apagou o perfil de outra conta com pasta `...\EditorTestes` |
| `test_d731_a_regra_larga_so_sai...`, `test_d731_da_pasta_ssh_so_sai...` (2+2) | não havia esses passos |
| `test_script_sem_senha_nao_procura_o_arquivo_da_senha`, `test_d731_o_desfazer_continua_depois_de_um_erro` | o montador não era único e parava sem o arquivo da senha |

## Resultado de cada arquivo (um por vez, offscreen, `--basetemp=D:/agente_temp_testes/d731`)

- `tests/test_decisoes_testes_a_distancia.py`: 13 passaram (as provas da etapa 4, sem mudança).
- `tests/test_decisoes_atualizacao.py`: 38 passaram.
- `tests/test_decisoes_desinstalar.py` (novo): 35 passaram.
- `tests/test_promessas.py -k "215"`: 1 passou.
- Rodada do GitHub: **não disparada** (o pedido disse "sem push"). A gerente dispara depois do push.

**Testes antigos afetados: nenhum.** Nenhum teste antigo foi mudado.

## Como fica para quem usa e no livro

- **Kaique, usando o programa:** nada muda. A janela da senha, as Configurações, os filtros e o PDF ficam iguais.
- **Kaique, ao pôr a senha:** a mesma pergunta do Windows de hoje. Por trás, o programa anota o que já havia e deixa a
  tarefa pronta.
- **Kaique, ao desinstalar:** nenhuma pergunta a mais. Em poucos minutos, por trás, o notebook fica como era.
- **No PDF:** nada muda.
- **Problema novo:** nenhum achado. Ressalva: um ligar demora alguns segundos a mais (anotar o antes, criar a tarefa).

## Perguntas abertas (para a gerente; cada uma com a sugestão)

1. **A tarefa da atualização não sai ao desinstalar.** O gancho roda sem administrador, e o `apagar_tarefa` falha
   (achado B1). A tarefa "desfazer" só existe se os testes foram ligados. Sugestão: o agente da atualização faz a
   tarefa dele sair pelo mesmo caminho. Por exemplo, a pergunta do Windows da primeira abertura (D-735) cria sempre a
   tarefa "desfazer", e ela apaga também a da atualização. Isso é da frente do outro agente: eu não mexi.
2. **Quem pode mandar rodar o desfazer.** Hoje é qualquer conta que entrou no Windows, menos a de testes. Sugestão:
   fica assim. A tarefa só desfaz o que é nosso, e prender só à conta do Kaique pediria saber qual é a conta dele na
   hora de ligar.
3. **Se o notebook do Kaique já tiver um OpenSSH dele**, enquanto os testes estão ligados só a conta de testes entra
   por ele (é a D-711). Desligar e desinstalar devolvem tudo como era. Sugestão: só perguntar ao Samuel se a etapa 6
   mostrar que o notebook já tem um OpenSSH.
4. **Defeito provável, não consertado (B5).** O passo que esconde a conta usa `New-Item ... UserList -Force`. Se a
   chave já existir, isso pode apagar as outras contas escondidas do dono. Sugestão: consertar já, com "só cria se não
   existe" (uma linha) e teste de reversão. Fica fora deste pedido, por isso não mexi.
5. **O registro do desfazer** (`o-que-foi-desfeito.txt`) e a pasta dele ficam no ProgramData depois de desinstalar,
   para a gerente ler o que foi feito. Sugestão: fica, como a pasta do registro da atualização.
6. **Depois de uma atualização**, a tarefa roda o desfazer da versão que ligou por último. Sugestão: fica assim, ou o
   ajudante da atualização grava o script de novo (frente do outro agente).

## O que só a etapa 5 prova (no PC do Samuel)

- Que a conta comum consegue mandar a tarefa rodar com essa licença, de dentro do gancho do `.msi`, e em menos de 30 s.
- Que a tarefa continua rodando depois que o desinstalador termina e apaga a pasta do programa.
- Que `Register-ScheduledTask -Xml` aceita o XML com `S-1-5-18`, e o `SetSecurityDescriptor`, a licença.
- Que o `icacls` com os números dos grupos protege a pasta e que um arquivo gravado como administrador tem dono
  "administradores".
- Os valores reais do caderninho (o estado do OpenSSH, o tipo de início do serviço, a regra larga).
- O `sshd_config` de fábrica de verdade, e se o `sshd` aceita as linhas antes do `Match`.
- Que o `Remove-CimInstance` apaga o perfil e que o `Remove-WindowsCapability` termina dentro de 1 hora.
- Que a tarefa consegue se apagar no último passo.
- O antivírus (D-725).


---

## Continuação de 17/11/2026: a junção, a D-740, o desfazer sempre, a D-741 e a D-742

**O que é.** Quatro coisas na cópia que junta os dois trabalhos (ramo `kaique-juntar-2026-11-17`). Nada foi feito no
Windows de verdade: nada instalado, nenhuma conta, nenhuma tarefa; nenhuma janela abriu na tela.

**Situação.** PRONTO PARA CONFERIR. Commits sobre `cf49ff7f`, sem envio ao GitHub:
`4eac1959` (D-740), `77be80ff` (desfazer sempre), `866186b3` (D-741) e `1a42dfb0` (D-742).

### 1. D-740: os 3 testes antigos cobram o jeito novo

O Samuel autorizou a mudança (D-740, "Sim"). Só estes três mudaram, em `tests/test_decisoes_atualizacao.py`:

- `test_d714_a_tarefa_roda_ao_ligar_como_o_sistema_sem_janela`: cobra que a tarefa **não** tem gatilho de ligar o
  computador e continua rodando como o sistema, em prioridade baixa (D-732). O nome ficou o de antes, porque a D-740
  cita o teste por ele.
- `test_d720_o_aviso_tem_reiniciar_agora_e_depois_e_depois_nao_troca`: cobra a frase nova, "próxima vez que você
  abrir o programa" (D-734). O resto ficou igual.
- `test_d714_a_instalacao_de_verdade_cria_e_roda_a_tarefa` virou `test_d714_a_instalacao_de_verdade_nao_cria_a_tarefa`:
  cobra que a instalação **não** cria a tarefa (B1, D-733). O nome antigo mentia.

**Prova.** No código de antes (`997a3085`), os três falham; no novo, passam. Saída em
`prova-d740-no-codigo-de-antes.txt`.

### 2. A tarefa "desfazer" existe sempre e apaga também a tarefa da atualização (pergunta (a) acima)

**O defeito.** A tarefa "desfazer" só nascia quando os testes à distância eram ligados. E o gancho de desinstalar roda
sem administrador, então a tarefa da atualização ("Procurar versao nova") ficava no Windows depois de desinstalar.
O computador não voltava a ser como era antes (D-731).

**O conserto, numa regra só.**
- A pergunta do Windows da primeira abertura (o modo `--preparar-o-computador`) cria agora as duas tarefas
  (`atualizacao.criar_as_tarefas`): o ajudante da atualização, como antes, e a tarefa "desfazer".
- A tarefa "desfazer" nasce pelo mesmo caminho do `ligar` (`_comando_preparar_o_desfazer`), com o plano curto:
  `plano_de_desfazer(testes_ligados=False)`, que só mexe nas nossas tarefas.
- Todo desfazer, curto ou inteiro, termina igual (`_passos_das_nossas_tarefas`):
  - apaga a tarefa da atualização, sempre;
  - apaga a si mesmo, só se tudo deu certo.
- Os testes à distância ligados continuam sendo desfeitos como antes. O `ligar` grava o plano inteiro, com o mesmo
  fim.
- Se os testes já foram ligados (o caderninho do antes existe), a primeira abertura não troca o desfazer inteiro pelo
  curto. Isso importa por causa da D-741: a pergunta pode voltar depois de os testes serem ligados nas Configurações.
- A licença da tarefa nega a conta de testes só quando ela existe. Na primeira abertura ela ainda não existe, e o
  `ligar` refaz a tarefa já com a negação (D-717).
- A pasta do desfazer fica protegida pelo mesmo `icacls` do `ligar`, agora escrito num lugar só
  (`_comando_proteger_a_pasta`).
- Os projetos do Kaique nunca são citados.

**Caminho → função.**

| Caminho | Função |
|---|---|
| Primeira abertura (dentro da pergunta do Windows) | `preparar_como_administrador` → `criar_as_tarefas` → `criar_tarefa` + `testes_a_distancia.preparar_o_desfazer` → `plano_de_preparar_o_desfazer` → `_comando_preparar_o_desfazer(testes_ligados=False)` |
| Ligar os testes (janela, caixinha, botão) | `ligar` → `plano_de_ligar` → `_comando_preparar_o_desfazer()` (plano inteiro) |
| Desinstalar | `ao_desinstalar` → `mandar_desfazer` → a tarefa roda `montar_script(plano_de_desfazer(...))` |
| O fim de todo desfazer | `_passos_das_nossas_tarefas` |
| Proteger a pasta | `_comando_proteger_a_pasta` (o `ligar` e a primeira abertura) |

**Prova.** 9 provas novas `test_d731a_*` em `tests/test_decisoes_desinstalar.py`. A principal: sem os testes ligados,
a primeira abertura cria o desfazer; desinstalar manda rodá-lo; ele apaga a tarefa da atualização e a si mesmo, e
nada dos testes. Ela roda o script gravado no "Windows de mentira" do PowerShell. No código de antes (`4eac1959`), as
9 falham. A principal falha pelo motivo certo: "a primeira abertura não criou a tarefa desfazer". Saída em
`prova-d731a-no-codigo-de-antes.txt`.

### 3. D-741: depois de um "Não", a pergunta do Windows volta até o "Sim"

**O defeito.** Era a pergunta aberta 1 do relatório da D-732. Se o Kaique dissesse "Não" à pergunta do Windows da
primeira abertura, ela nunca mais voltava. O ajudante da atualização nunca nascia.

**O conserto, numa regra só.**
- `atualizacao.falta_a_pergunta_do_windows` decide se a pergunta aparece de novo.
- `preparar_na_primeira_abertura` grava a marca nas Configurações (`atualizacao_computador_preparado`), só quando a
  resposta não foi "Não".
- A tela (`primeira_vez_se_preciso`) pergunta de novo só a pergunta do Windows. A janela da senha não volta, porque a
  senha vai nas Configurações (D-721), e não aparece aviso.
- Na conta de testes e pelo código, nada pergunta (D-736, D-728).

**Prova.** 4 provas `test_d741_*`. A principal faz "Não", abre de novo e vê a pergunta voltar; faz "Não" de novo e ela
volta; faz "Sim" e ela nunca mais aparece. No código de antes (`77be80ff`), a principal falha pelo comportamento:
"depois do Não, a pergunta do Windows volta ao abrir de novo", com 1 pergunta em vez de 2. As outras três falham só
porque a função nova não existia; o comportamento delas já era certo. Saída em `prova-d741-no-codigo-de-antes.txt`.

### 4. D-742: a janelinha "Atualizando o programa, espere um pouco..."

**Como fica para o Kaique.** Ele clicou "Depois" e, mais tarde, abre o programa. A janela do programa não abre logo.
Aparece no meio da tela uma janelinha pequena, sem título e sem botão, só com o texto "Atualizando o programa, espere
um pouco...". Quando o programa abre, já na versão nova, ela some. Se a versão nova falhar, a volta para a anterior
acontece igual (D-718), e a janelinha some quando o programa abrir na versão anterior. O "Reiniciar agora" ficou como
era. Nenhuma outra tela muda. No PDF, nada muda.

**Onde a janelinha vive.** A troca acontece fora do programa: o programa tem de sair para os arquivos dele serem
trocados. Quem espera e reabre é um PowerShell escondido, na conta do Kaique (`script_de_trocar_e_reabrir`).
- A janelinha é uma janela do Windows aberta por esse mesmo PowerShell, numa linha de execução separada
  (`script_da_janelinha`, `_linhas_da_janelinha`).
- A troca não espera por ela, e ela não espera pela troca. Um erro nela não impede a troca nem a volta.
- Ela some quando o programa marca que abriu, pela mesma marca de "programa aberto" que o ajudante usa. No pior
  caso, some sozinha depois do tempo inteiro da troca.
- Se o programa já abriu enquanto ela se montava, ela nem aparece, para nada piscar na tela.
- O resto do PowerShell da troca ficou igual, letra por letra (há uma prova disso).

**Prova, sem abrir nada na tela.** A janela do Windows foi trocada por uma de mentira que só anota. A prova abre a
"janelinha", confere que ela continua enquanto a troca não terminou, cria a marca de "programa aberto" e confere que
ela fechou. Também confere o texto exato, que não há botão, que ela fica por cima e sem título. Uma segunda prova
confere que ela nem aparece se o programa já abriu. Ao todo, 6 provas `test_d742_*`. No código de antes
(`866186b3`), as 5 primeiras falham (a janelinha não existia). Saída em `prova-d742-no-codigo-de-antes.txt`.

**Ressalva medida.** Neste PC, a primeira letra de uma janela do Windows num processo novo leva uns 5,5 s. Por isso a
janelinha aparece uns 6 s depois de o programa sair. Isso foi medido com a janela de mentira e com relógio, sem
mostrar nada. A troca de verdade leva mais que isso, então ela aparece durante a troca. No notebook do Kaique, só a
etapa 5 mostra o tempo.

### Resultado de cada arquivo (um por vez, offscreen, `--basetemp=D:/agente_temp_testes/juntar2`)

- `tests/test_decisoes_atualizacao.py`: 38 passaram (os 3 da D-740 incluídos).
- `tests/test_decisoes_ajudante_da_atualizacao.py`: 37 passaram (27 de antes, 4 da D-741 e 6 da D-742).
- `tests/test_decisoes_desinstalar.py`: 46 passaram (37 de antes e 9 novas `test_d731a_*`).
- `tests/test_decisoes_testes_a_distancia.py`: 13 passaram.
- `tests/test_assinatura.py`: 16 passaram.
- `tests/test_promessas.py -k "215"`: 1 passou.
- **Ensaio da etapa 3** (`ensaio_velopack.py`): **"ENSAIO: CERTO"**. Ele continua sem tocar o Windows de verdade:
  pacotes portáteis em `build\ensaio-velopack\`, sem tarefa, sem Arquivos de Programas, com um ProgramData de
  mentira, e só o programinha do ensaio, com a chave de mentira.
  - A, de 1.1.0 para 1.2.0: trocou, e a versão nova passou no teste.
  - B, a 1.3.0 estragada: voltou para a 1.2.0.
  - C, a 1.4.0 com a assinatura de outra chave: recusada, nada baixado.
  - Ressalva: as duas primeiras tentativas pararam no meio (a primeira pelo meu limite de 50 minutos, com o PC lento;
    a segunda quando a internet caiu). A terceira foi até o fim. Nenhum processo delas ficou rodando.
- Rodada do GitHub: não disparada (sem push). Fica com a gerente.

### Testes antigos

Só os três da D-740 mudaram, com a autorização dele. Nenhum outro teste antigo mudou. As provas novas foram
acrescentadas no fim dos arquivos.

### Perguntas abertas (para a gerente; cada uma com a sugestão)

1. **A pasta das tarefas no Agendador do Windows.** O desfazer apaga as duas tarefas, mas a pasta vazia
   "EditorImpressao" fica no Agendador. Ela não faz nada, mas é um rastro. Sugestão: o desfazer apaga a pasta se ela
   estiver vazia (uma linha). Fica para outro pedido, porque o "Windows de mentira" dos testes não roda esse tipo de
   comando e a prova seria só no PC (etapa 5).
2. **"Sim" à pergunta do Windows, mas o preparo deu erro.** Hoje vale a regra dele ao pé da letra: depois do "Sim",
   nunca mais pergunta, mesmo se o preparo falhou. O erro fica no registro da atualização. Sugestão: fica assim; a
   etapa 5 mostra se isso acontece de verdade.
3. **Com a senha e "Não".** Na abertura seguinte volta só a pergunta do Windows, sem a janela da senha; os testes à
   distância ficam desligados até ele pôr a senha nas Configurações. Sugestão: fica assim (D-721).
4. **A espera da janelinha.** Ela aparece uns 6 s depois de o programa sumir, neste PC. Sugestão: a etapa 5 mede no
   notebook antes de mudar qualquer coisa.

### O que só a etapa 5 prova (no PC do Samuel)

- Que o `--preparar-o-computador` roda o PowerShell do desfazer sem pergunta, e que a tarefa nasce sem a conta de
  testes.
- Que, depois de desinstalar, as duas tarefas somem do Agendador.
- Que a janelinha aparece de verdade na conta do Kaique, a partir do PowerShell escondido, e some quando o programa
  abre.
- Quanto tempo ela leva para aparecer no notebook.

### Arquivos fora do projeto (CLAUDE.md §10.9)

Criei e deixei lá (a gerente decide se saem):
- as cópias do código de antes, para as provas: `D:\agente_temp_testes\juntar2-antigo-997a3085`,
  `...-4eac1959`, `...-77be80ff` e `...-866186b3` (uns 11 MB cada);
- as pastas de teste `D:\agente_temp_testes\juntar2` e `D:\agente_temp_testes\juntar2-antigo-tmp`.
Não apaguei nada.
