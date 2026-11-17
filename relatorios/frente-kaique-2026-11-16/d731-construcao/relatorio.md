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
