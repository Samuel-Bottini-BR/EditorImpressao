# Plano D-731: desinstalar tira junto o comando de longe e a conta de testes

**O que é.** Quando alguém desinstala o Editor de Impressão do notebook do Kaique, o programa sai. Hoje ficam no
notebook o comando de longe (Servidor OpenSSH), a regra do firewall e a conta de testes escondida. Este plano faz essas
coisas saírem junto. Os projetos do Kaique (`%LOCALAPPDATA%\EditorImpressao`) nunca são tocados.

**Situação.** Este é só o plano (regra D-709). Nenhum arquivo do programa nem dos testes foi mudado. Nada foi feito no
Windows. Ramo `desinstalar-tudo-2026-11-16`, criado do `obra-2026-10-26` (`b624007f`). Espera o "sim" da gerente e as
respostas da seção 10.

## Decisões que esta tarefa precisa cumprir

- **D-731** (Samuel, 16/11): "ok" à pergunta "se um dia o programa for desinstalado do notebook do Kaique, o comando de
  longe e a conta de testes saem junto? Assim o notebook fica como era antes de instalar." Saem: o OpenSSH (só se foi o
  programa que instalou), a regra do firewall, a conta de testes e o perfil dela.
- **D-705, D-711, D-717**: o que o `ligar` monta (OpenSSH só pelo Tailscale, liga com o Windows, senha, conta sem
  administrador e escondida). O desfazer tira exatamente isso, e nada além.
- **D-722**: a etapa 5 desfaz tudo no PC do Samuel e mostra a lista do que foi desfeito. Ela usa o mesmo desfazer.
- **D-714, D-723**: a tarefa do Windows da atualização sai ao desinstalar (já é assim no código; ver o achado 2).
- **D-712, D-721, D-728**: não mudam. O instalador continua sem perguntar nada, e pelo atalho "(desenvolvimento)"
  nada liga.
- **CLAUDE.md §7 e §10.9**: os projetos do Kaique e nada que não seja nosso é apagado.
- **§11.7 só o que foi mandado; §11.8 o novo não estraga o testado; §11.12 uma regra num lugar só.**

## O que já está escolhido e testado aqui (não pode mudar)

- `tests/test_decisoes_testes_a_distancia.py` (11 provas da etapa 4). Elas procuram pedaços de texto nos comandos.
  O plano mantém todos esses pedaços. Atenção: `ligar` não pode passar a conter a palavra "Administ" nem
  "PubkeyAuthentication".
- `tests/test_decisoes_atualizacao.py`: `test_d714_criar_e_apagar_a_tarefa_pelo_schtasks` (o `apagar_tarefa` continua
  existindo, com o mesmo comando) e `test_d723_o_portatil_nunca_cria_nem_apaga_a_tarefa` (o pacote portátil continua
  sem mexer no Windows).
- Nenhum teste antigo será mudado. O Samuel ainda não testou nada desta frente no PC dele (a etapa 5 não rodou).

---

## 1. O que o `ligar` põe no computador, e como saber se foi nosso

Hoje o programa **não anota** o que já existia antes. Por isso o desfazer de hoje tira tudo às cegas, inclusive um
OpenSSH que já estivesse lá. A saída é um **caderninho do "antes"**: o primeiro passo do `ligar` (já com a licença de
administrador) olha o computador e grava o que encontrou. Fica em
`C:\ProgramData\EditorImpressao\testes-a-distancia\antes.json`. Ele só é gravado **se ainda não existir**: assim, um
desligar e ligar de novo não faz o programa achar que o OpenSSH "já estava lá" quando foi ele mesmo que o pôs. A pasta
recebe permissão só de leitura para os usuários comuns, para ninguém sem administrador mudar o caderninho.

| O que o `ligar` põe | Como saber se foi nosso | O que o desfazer faz |
|---|---|---|
| Servidor OpenSSH (recurso do Windows) | caderninho: `openssh_ja_existia` | só tira se o caderninho diz "não existia" |
| Serviço `sshd` automático e ligado | caderninho: como estava o início e o estado do serviço | se o OpenSSH já existia, devolve como estava; se era nosso, sai com ele |
| Regra larga `OpenSSH-Server-In-TCP` desligada | caderninho: se ela existia e estava ligada | se já existia ligada, liga de novo; se era nossa, apaga junto com o OpenSSH |
| Regra `EditorImpressao-Testes` (só o Tailscale) | o nome é só nosso | apaga sempre |
| Conta `EditorTestes` | caderninho: `conta_ja_existia`; e a descrição da conta é a nossa ("Conta so para os testes a distancia") | só apaga se as duas coisas dizem "nossa" |
| Perfil da conta (`C:\Users\EditorTestes`) | o perfil é da conta nossa (pelo número de identidade dela, o SID) | apaga, achando pelo SID e não pelo nome da pasta |
| Valor `EditorTestes` em `...\Winlogon\SpecialAccounts\UserList` | vai junto com a conta; caderninho: se a chave `UserList` já existia | apaga o valor; a chave só sai se não existia e ficou vazia |
| Linhas no `C:\ProgramData\ssh\sshd_config` | passam a ir entre duas linhas-marca (`# --- Editor de Impressao: inicio ---` e `fim`) | tira só o que está entre as marcas |
| Pasta `C:\ProgramData\ssh` e o que nasce nela (chaves do servidor, registro) | caderninho: se a pasta existia e a lista do que havia dentro | se o OpenSSH era nosso: apaga só o que não estava na lista; a pasta só sai se não existia |
| Tarefa da atualização (etapa 3, não dos testes) | o nome é só nosso | apaga (`schtasks /Delete`) |

Exemplo real, conferido agora no PC do Samuel (só leitura): não há serviço `sshd` nem `sshd.exe`, mas a pasta
`C:\ProgramData\ssh` **já existe** (vazia ou sem licença de ler). Sem o caderninho, um desfazer que apagasse essa pasta
apagaria algo que não é nosso.

## 2. Onde a remoção roda, e a licença de administrador

**Achado: o gancho de desinstalar do Velopack roda SEM licença de administrador.**
- No `vpk` 1.2.161 instalado (`~/.dotnet/tools/.store/vpk/1.2.161`), o modelo do instalador `.msi`, dentro do
  `Velopack.Packaging.Windows.dll`, diz:
  `<CustomAction Id="UninstallHookDeferred" ... Execute="deferred" Impersonate="yes" Return="ignore"/>`
  (o de instalar, `InstallHookDeferred`, é igual).
- A documentação da Microsoft ("Custom Action Security") diz: "If the msidbCustomActionTypeNoImpersonate bit is not
  set for a custom action, the installer runs the custom action with user-level privileges." `Impersonate="yes"` é
  justamente sem esse bit. Ou seja: o gancho roda com a licença de usuário comum, mesmo que a desinstalação tenha
  pedido administrador.
- A documentação do Velopack (docs.velopack.io, "hooks"): o gancho de desinstalar tem **30 segundos**; depois disso o
  processo é morto. `Return="ignore"`: se o gancho falhar, o programa sai mesmo assim.
- O `vpk pack` 1.2.161 não tem opção para trocar o modelo do `.msi` (conferido em `vpk pack -h`).

Consequência: tirar o OpenSSH, apagar a conta, mexer no firewall e até o `apagar_tarefa` de hoje precisam de
administrador e **não funcionam dentro do gancho**. Tirar o OpenSSH também demora minutos, mais que os 30 segundos.

**A tarefa do Windows não serve para isso.** Ela roda como o sistema, mas só quando o computador liga. O usuário comum
não pode mandá-la rodar, e o `.exe` que ela chama some junto com o programa.

**A saída: a mesma pergunta do Windows que o `ligar` usa.**
1. O gancho (`ao_desinstalar`) monta a lista do que sai: a tarefa da atualização e o `plano_de_desfazer`.
2. Ele grava um script com essa lista fora da pasta do programa, numa pasta temporária, porque a pasta do programa é
   apagada logo depois.
3. Ele abre um PowerShell escondido e solto. Esse PowerShell faz a pergunta "Deseja permitir...?" (o mesmo `runas` do
   `ligar`) e o gancho volta na hora. Assim a espera pela resposta do Kaique não conta nos 30 segundos.
4. Com o "Sim", o script roda como administrador, por trás. Ele faz cada passo mesmo se um anterior falhar, anota
   cada um em `C:\ProgramData\EditorImpressao\testes-a-distancia\o-que-foi-desfeito.txt` e, se tudo der certo, apaga o
   caderninho do "antes".

**Se o Kaique disser "Não":** o programa sai mesmo assim, porque o Windows continua a desinstalação. O OpenSSH, a
conta, as regras e a tarefa ficam. O registro anota "disse Não". O comando de longe continua aberto só para o
Tailscale e só com a senha. Para tirar o que ficou, basta instalar e desinstalar de novo, dizendo "Sim". O que fazer
nesse caso é pergunta ao Samuel (seção 10).

## 3. Reaproveitar o `plano_de_desfazer` (uma regra num lugar só) e a etapa 5

Sim, o mesmo `plano_de_desfazer` serve aos dois caminhos. "Desfazer o que o `ligar` pôs" é uma regra só:

- **Desinstalar** → `atualizacao.ao_desinstalar` → `atualizacao.plano_ao_desinstalar()` =
  [apagar a tarefa] + `testes_a_distancia.plano_de_desfazer()`.
- **Etapa 5** (D-722, no PC do Samuel) → o mesmo `plano_de_desfazer()`. A lista do que foi desfeito sai do mesmo
  registro.
- O comando de apagar a tarefa fica escrito num lugar só (`atualizacao`), usado pelo `apagar_tarefa` de hoje e pelo
  passo novo.

O que muda dentro do `plano_de_desfazer`:
- Cada passo que pode atingir algo que não é nosso só roda se o caderninho disser "foi nosso". Essa conferência roda
  dentro do script, já como administrador, e cada passo usa um ajudante só (`_so_se_foi_nosso`).
- O `sshd_config` sai pelas marcas. O jeito de hoje apaga também a linha de fábrica `#PasswordAuthentication yes` e
  qualquer linha igual do dono.
- O perfil é achado pelo número de identidade (SID) da conta, e não pelo nome da pasta.
- Volta a ligar a regra larga do OpenSSH e devolve o início do serviço, quando o OpenSSH já existia.
- Antes de apagar o perfil, o script fecha o que a conta de testes estiver rodando (um teste de longe no meio).
- Os textos que as provas antigas procuram continuam lá (`Remove-LocalUser -Name EditorTestes`, `Win32_UserProfile`,
  `Remove-ItemProperty ... UserList`, `Remove-WindowsCapability ... OpenSSH.Server`).
- A frase do comentário "O que fazer ao DESINSTALAR ainda nao esta decidido" sai, porque agora está decidido (D-731).

No `plano_de_ligar` entra **um passo no começo**: "anotar o que já existia". As linhas do `sshd_config` passam a ir entre
as marcas, no mesmo lugar de hoje (no fim do arquivo; ver o bug B2).

**Onde isso deixa a etapa 5.** Ela fica mais simples e prova a D-731 de verdade:
1. instalar o `.msi`;
2. ligar os testes;
3. desinstalar pelo Windows, dizendo "Sim";
4. conferir a lista.

Se o gancho não funcionar no Windows de verdade, roda-se o mesmo `plano_de_desfazer` à mão. A etapa 5 precisa usar o
`ligar` com este código, para o caderninho existir.

**A peça que fala com o Windows** ganha um jeito "sem esperar": `Executor.deixar_rodando(passos)`, ao lado do
`aplicar` de hoje (que espera). No `ExecutorWindows`, ele chama `deixar_rodando_no_windows` em
`core/_testes_a_distancia_windows.py`. O montador do script ganha a opção "continuar depois de um erro", que só o
desfazer usa. O `ligar` continua parando no primeiro erro, como hoje.

## 4. Testes novos (offscreen, com o executor de mentira, sem tocar o Windows)

Num arquivo novo, `tests/test_decisoes_desinstalar.py`, mais um nome novo de teste em cada arquivo antigo, se precisar.
Nenhum teste antigo muda.

| Prova | O que cobra | Por que falha no código de hoje |
|---|---|---|
| `test_d731_desinstalar_tira_o_que_os_testes_puseram` | `ao_desinstalar(portatil=False)` entrega ao executor de mentira, numa pergunta só e sem esperar, o apagar da tarefa, o apagar da regra `EditorImpressao-Testes`, da conta, do perfil, do UserList, o tirar das marcas do `sshd_config` e o tirar do OpenSSH | hoje `ao_desinstalar` só chama `apagar_tarefa`; o executor nunca é chamado |
| `test_d731_desinstalar_nao_espera` | o gancho usa `deixar_rodando` e não `aplicar`, e volta logo | hoje não há `deixar_rodando` |
| `test_d731_ligar_anota_o_antes_primeiro` | o 1º passo do `ligar` grava o caderninho, só se não existe, e vem antes do `Add-WindowsCapability` | hoje não há esse passo |
| `test_d731_openssh_que_ja_existia_fica` | no desfazer, o `Remove-WindowsCapability`, o apagar da pasta `ssh` e o apagar da regra larga estão dentro da conferência "foi nosso" do OpenSSH; a conta, dentro da conferência da conta | hoje o `Remove-WindowsCapability` é incondicional |
| `test_d731_sshd_config_sai_pelas_marcas` | o `ligar` escreve as marcas; o desfazer tira só o que está entre elas e não procura `PasswordAuthentication yes` solto | hoje o desfazer apaga por esse texto solto |
| `test_d731_nunca_toca_os_projetos` | nenhum comando do desfazer e do desinstalar cita `LOCALAPPDATA`, `AppData` ou `C:\Users\` (fora o perfil achado pelo SID) | cobra a regra; passa hoje e continua passando |
| `test_d731_disse_nao_fica_anotado` | executor de mentira devolve "cancelado" → o registro da atualização ganha a linha "disse Não", e nada quebra | hoje não há registro disso |
| `test_d731_etapa5_e_desinstalar_usam_o_mesmo_desfazer` | os passos dos testes à distância dentro do `plano_ao_desinstalar` são exatamente os do `plano_de_desfazer` (prova do §11.12) | hoje o `plano_ao_desinstalar` não existe |
| `test_d731_portatil_e_pelo_codigo_nao_desfazem_nada` | portátil, ou rodando pelo código → o executor nunca é chamado | passa hoje; garante que continua (D-728, D-723) |

Rodar no PC um arquivo por vez: o novo, `test_decisoes_testes_a_distancia.py`, `test_decisoes_atualizacao.py` e os
`test_decisoes*.py`. Depois a rodada do GitHub, e o teste de reversão rodado no código antigo, mostrando que falha.

## 5. Riscos no notebook do Kaique, e como o plano evita

- **Apagar um OpenSSH que não é nosso** (o Kaique ou outro programa pode ter um). Evita: o caderninho do antes; sem
  caderninho, o OpenSSH nunca é tirado.
- **Apagar uma conta `EditorTestes` que não é nossa** (quase impossível). Evita: o caderninho e a descrição da conta,
  os dois.
- **Apagar a pasta `C:\ProgramData\ssh` que já existia** (é o caso do PC do Samuel). Evita: só sai o que não estava na
  lista; a pasta só sai se não existia.
- **Estragar o `sshd_config` do dono.** Evita: as marcas.
- **Um teste de longe rodando na hora.** Evita: o desfazer para o `sshd` primeiro e fecha os processos da conta antes
  de apagar o perfil.
- **Os 30 segundos do gancho.** Evita: o gancho não espera. Só a etapa 5 prova que o PowerShell solto sobrevive ao fim
  do gancho e ao fim do instalador.
- **O "Não" do Kaique.** Fica o que estava, anotado; ver a pergunta.
- **Desinstalar dentro de uma troca de instalador** (um `.msi` novo por cima do velho). O modelo do Velopack 1.2.161 não
  tem "troca de versão por cima" (procurei `MajorUpgrade` e não há). Se um dia tiver, o gancho dispararia numa
  reinstalação e tiraria a conta. A etapa 5 confere isso, e a etapa 6 não manda um `.msi` por cima de outro.
- **Os projetos do Kaique.** Nenhum comando cita a pasta dele; uma prova cobra isso.
- **Alguém mudar o caderninho sem administrador.** Evita: a pasta é só de leitura para os usuários comuns.
- **Sem caderninho** (um `ligar` feito pelo código antigo da etapa 4, que nunca foi ao Kaique). Fica do lado seguro:
  sai só o que tem nome nosso (regra, conta com a nossa descrição, tarefa) e o OpenSSH fica.

## 6. Caminho → função

| Caminho | Função |
|---|---|
| Desinstalar pelo Windows (gancho do Velopack) | `atualizacao.ao_desinstalar` → `atualizacao.plano_ao_desinstalar` → `testes_a_distancia.plano_de_desfazer` → `Executor.deixar_rodando` |
| Etapa 5, desfazer à mão no PC do Samuel | `testes_a_distancia.plano_de_desfazer` → `Executor.aplicar` |
| Apagar a tarefa (o `apagar_tarefa` de hoje e o passo novo) | o mesmo comando, escrito uma vez em `atualizacao` |
| Ligar (janela da senha, caixinha, botão) | `testes_a_distancia.ligar` → `plano_de_ligar` (com o passo novo do antes) |

## 7. Como fica para quem usa e no livro

- **Kaique, ao desinstalar** (Configurações do Windows > Aplicativos > Editor de Impressão > Desinstalar): o Windows
  pergunta "Deseja permitir...?" para tirar o programa. Logo depois, pergunta de novo, para tirar o comando de longe e
  a conta de testes. A segunda é a mesma pergunta que apareceu quando ele pôs a senha dos testes. Com "Sim" nas duas,
  em poucos minutos, por trás, o notebook fica como antes. Os livros e os projetos dele ficam onde estão.
- **Usando o programa:** nada muda. A janela da senha, as Configurações, os filtros e o PDF ficam iguais.
- **Pelo atalho "(desenvolvimento)" do Samuel:** nada muda e nada liga.

## 8. Arquivos que vão mudar (depois do "sim")

- `core/testes_a_distancia.py`: o passo do antes no `plano_de_ligar`, as marcas no `sshd_config`, o
  `plano_de_desfazer` com as conferências e o `Executor.deixar_rodando`.
- `core/_testes_a_distancia_windows.py`: `deixar_rodando_no_windows` e a opção "continuar depois de um erro".
- `atualizacao.py`: `ao_desinstalar`, `plano_ao_desinstalar` e o comando de apagar a tarefa num lugar só.
- `tests/test_decisoes_desinstalar.py` (novo).
- O `ONDE-PAREI.md` e o relatório desta pasta. O Livro (D-731) e a ficha são da gerente.

## 9. Bugs para a Lista de bugs (achados lendo o código, 16/11; não consertados)

- **B1 (importante, etapas 3 e 5): o gancho de instalar também roda sem administrador.** É o mesmo achado da seção 2.
  O `ao_instalar` cria a tarefa como o sistema (`schtasks /Create`, que pede administrador). Pelo `.msi`, isso deve
  falhar: o registro mostraria "criar a tarefa: NÃO deu certo", e **a atualização sozinha (D-714) nunca rodaria** no
  notebook do Kaique. É a ressalva 1 do relatório da etapa 3, agora com a causa provável. O `apagar_tarefa` de hoje,
  ao desinstalar, falha pelo mesmo motivo.
  - Saídas possíveis, para a gerente decidir: a mesma pergunta do Windows no gancho de instalar; ou criar a tarefa na
    pergunta de administrador que já aparece na primeira abertura (D-721).
- **B2 (provável, a conferir na etapa 5): as linhas do `ligar` caem dentro do bloco "Match Group administrators".**
  O `sshd_config` de fábrica do Windows termina com esse bloco, e o `ligar` acrescenta as linhas no fim. Assim
  `AllowUsers`, `PasswordAuthentication` e `MaxAuthTries` valeriam só para contas de administrador. Contas comuns do
  notebook não ficariam barradas, e a conta do Kaique, se for administradora, ficaria. O conserto é pôr o bloco antes
  do primeiro `Match`. É mudança no `ligar`, com teste de reversão: separada desta, salvo ordem da gerente.
- **B3: ligar de novo depois de desligar falha.** O `desligar` só desativa a conta. O `ligar` seguinte tenta criá-la de
  novo (`New-LocalUser`), dá erro e para. Também não reativa a conta e repete as linhas do `sshd_config`.
- **B4: o `desligar` desativa o `sshd` mesmo quando o OpenSSH já era do dono.** É fora da D-731; fica registrado.

## 10. Perguntas para o Samuel

**Do que se trata.** É a desinstalação do Editor de Impressão no notebook do Kaique, em Configurações do Windows >
Aplicativos > Editor de Impressão > Desinstalar. Você decidiu que o comando de longe e a conta de testes saem junto.
Para isso, o Windows vai perguntar duas vezes "Deseja permitir...?": uma para tirar o programa, outra para tirar o
comando de longe e a conta. A segunda é a mesma pergunta que aparece quando o Kaique põe a senha dos testes.

**O que acontece hoje.** Isso ainda não existe. Hoje, desinstalar deixa os dois no notebook.

**A dúvida.** Se o Kaique disser "Não" na segunda pergunta, o programa sai mesmo assim (o Windows não deixa parar), e o
comando de longe e a conta de testes ficam. Eles continuam fechados para todo mundo, menos para a rede do Tailscale com
a sua senha.

**O que você escolhe:**
- **(a) Sugestão:** fica assim, e isso fica anotado num registro do notebook. Para tirar o que ficou, o Kaique instala
  e desinstala de novo, dizendo "Sim". Nada novo aparece na tela dele.
- **(b)** Aparece uma janelinha para ele, dizendo que o comando de longe ficou e como tirar. O texto você aprova antes.
- **Só comentário.**

Nada do que já funciona muda nas duas opções. Print: não há tela nova. A pergunta do Windows é a mesma do `ligar`, e
o print dela sai na etapa 5.

## 11. Ressalvas (o que só a etapa 5 prova, no PC do Samuel)

- Que o gancho de desinstalar roda mesmo sem administrador, como dizem o modelo do Velopack e a documentação da
  Microsoft.
- Que a pergunta do Windows aparece na frente da janela de desinstalar.
- Que o PowerShell solto continua depois do fim do gancho (os 30 segundos) e do fim do instalador.
- O texto de fábrica do `sshd_config` (B2) e o que o tirar do OpenSSH deixa para trás (a regra larga, a pasta `ssh`).
- A pasta `C:\ProgramData\EditorImpressao` (o registro da atualização, da etapa 3) continua depois de desinstalar.
  Ela não é dos testes à distância, por isso fica fora da D-731. Se for para sair também, é pergunta nova.
- Este plano ficou só em `.md`, como a gerente pediu. Os três formatos e a aba na Central (D-709) ficam com a gerente.
