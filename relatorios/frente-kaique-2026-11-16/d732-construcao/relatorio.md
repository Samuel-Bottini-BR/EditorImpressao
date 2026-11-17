# Procurar a versão nova ao abrir o programa (construção de 17/11/2026)

**O que é.** A versão nova do Editor de Impressão passa a ser procurada quando o programa abre, e não mais quando o
computador liga. Quem troca os arquivos é um ajudante do Windows. Ele nasce numa pergunta do Windows ("Deseja
permitir...?") na primeira vez que o Kaique abre o programa. Depois disso, nenhuma atualização pede licença.
**Nada foi feito no Windows de verdade:** nos testes, o Windows é de mentira e só anota o que seria feito.

**Situação.** PRONTO PARA CONFERIR. Ramo `desinstalar-tudo-2026-11-16`, commits `73dc4122`, `f3e05a1d`, `d92ba757`,
`87e4b7ff` e `f82a6139`, sem envio ao GitHub. Por ordem da gerente, este agente fez só os itens 1 a 4: D-732, D-733, B1, D-734,
D-735 e D-736. A desinstalação (D-731) e os defeitos B2, B3 e B4 ficaram com outro agente. Nada deles tinha sido
mexido aqui.

## Como fica para quem usa

1. **Primeira abertura.**
   - Aparece a janela da senha, como antes.
   - Com a senha, com "Agora não" ou com a opção desligada, vem depois **uma** pergunta do Windows.
   - Ela prepara o computador: o ajudante, o Visual C++ e a retirada da instalação antiga. Com a senha, liga também
     os testes à distância, na mesma pergunta.
2. **Nas aberturas seguintes,** nada aparece. O ajudante procura e baixa por trás.
3. **Chegou versão nova com o programa aberto.** Aparece o aviso de sempre, com um texto novo no fim: "Se escolher
   "Depois", a versão nova entra sozinha na próxima vez que você abrir o programa."
   - Com **"Reiniciar agora"**, o programa fecha gravando e volta sozinho já na versão nova, sem pergunta do Windows.
   - Com **"Depois"**, nada muda agora. Na próxima vez que ele abrir, há uma espera curta, sem janela, e o programa
     abre já na versão nova. Fechar o programa não troca nada.
4. **No livro e no PDF,** nada muda.

## O que mudou, por decisão

| Decisão | O que mudou | Prova |
|---|---|---|
| D-732: procurar ao abrir | A tarefa do Windows não tem mais hora para rodar (saiu o "ao ligar o computador"). Ao abrir, o programa manda o ajudante rodar. | `test_d732_o_ajudante_nao_roda_mais_ao_ligar_o_computador`, `test_d732_ao_abrir_o_programa_manda_o_ajudante_procurar`, `test_d732_a_janela_aberta_chama_o_ajudante_e_liga_o_aviso` |
| D-733: o ajudante e a pergunta da primeira abertura | A tarefa deixa as contas comuns mandarem rodar, mas não mudá-la. A pergunta da primeira abertura roda o próprio programa no modo `--preparar-o-computador`: o ajudante, o Visual C++ e o Inno, pela regra de sempre. Com a senha, ela vai na mesma pergunta. O "Reiniciar agora" não pede mais licença. Depois de uma troca, o ajudante é refeito como o sistema. | `test_d733_*` (9 provas) |
| B1: os ganchos sem administrador | `ao_instalar` e `ao_atualizar` não criam mais a tarefa. | `test_b1_ao_instalar_e_ao_atualizar_nao_criam_a_tarefa` |
| D-734: o "Depois" | Antes da janela, se há versão baixada esperando, o programa troca e se reabre. A troca e a reabertura do "Depois" e do "Reiniciar agora" passam por uma função só. | `test_d734_*` (3 provas) |
| D-735: a pergunta sempre | "Agora não" e a opção desligada não pulam a pergunta do Windows. | `test_d735_*` (3 provas) |
| D-736: testes à distância | Na conta de testes, o programa não procura, não troca e não faz a primeira abertura. Continua marcando "programa aberto", para nada trocar no meio de um teste. O comando de longe chama o mesmo ajudante. | `test_d736_*` (3 provas) |
| Uma regra num lugar só (§11.12) | O comando que chama o ajudante está escrito uma vez só. | `test_regra_num_lugar_so_todos_os_caminhos_chamam_o_ajudante_pelo_mesmo_comando` |

### O comando de longe (D-736)

O Samuel roda no PC dele, trocando `<notebook>` pelo nome do notebook do Kaique no Tailscale:

```
ssh EditorTestes@<notebook> schtasks /Run /TN "EditorImpressao\Procurar versao nova"
```

Para ler depois o que aconteceu:

```
ssh EditorTestes@<notebook> type "C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log"
```

- Se o programa do Kaique estiver fechado, a versão troca na hora. A assinatura e a volta se falhar são as de sempre.
- Se estiver aberto, a versão fica esperando, e o Kaique vê o aviso de salvar e reiniciar.
- No código, os dois comandos saem de `atualizacao.comando_de_longe_para_atualizar` e
  `comando_de_longe_para_ler_o_registro`.

### A fonte de teste da etapa 5 (pedido da gerente, 17/11)

**O que é.** Um jeito, só para teste, de o programa instalado de verdade buscar a versão de mentira numa pasta, sem
publicar no GitHub. O Kaique nunca vê nada disso: o arquivo não existe no notebook dele.

**Como funciona.** A escolha de onde vêm as versões continua numa função só (`fonte_da_linha`), nesta ordem:
1. `--fonte <pasta>` na linha de comando (o ensaio usa);
2. senão, o arquivo `C:\ProgramData\EditorImpressao\fonte-de-teste.txt`, com uma linha: a pasta das versões de
   mentira. Ele só vale se o **dono** do arquivo for o grupo Administradores ou o sistema. Uma conta comum consegue
   criar o arquivo, mas fica dona dele, e então ele é ignorado, com uma linha no registro;
3. senão, o GitHub, como sempre.

A assinatura é conferida igual nos três casos: só entra versão assinada pela chave do Samuel.

**Como a etapa 5 usa** (PowerShell como administrador, no PC do Samuel):

```
New-Item -ItemType Directory -Force C:\ProgramData\EditorImpressao | Out-Null
Set-Content -Path C:\ProgramData\EditorImpressao\fonte-de-teste.txt -Value 'D:\teste-atualizacao\servidor' -Encoding utf8
icacls C:\ProgramData\EditorImpressao\fonte-de-teste.txt /setowner *S-1-5-32-544
schtasks /Run /TN "EditorImpressao\Procurar versao nova"
```

- A pasta `D:\teste-atualizacao\servidor` é um exemplo. Nela vão o pacote e o arquivo `.assinatura` da versão de
  mentira, como o `publicar_versao_kaique.py --pasta` grava.
- A versão de mentira tem de ter número maior que a instalada e ser assinada pela chave do Samuel. O programa
  instalado só confia nessa chave.
  - **Cuidado:** esse pacote, assinado de verdade, nunca pode ir para o GitHub. Senão ele chegaria ao Kaique. Dê a
    ele um número que nunca será publicado.
- Para conferir, leia `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`. A linha "fonte de teste (etapa 5):
  as versões vêm de ..." mostra que o arquivo valeu.
- **No fim, apague o `fonte-de-teste.txt`.** Ele entra na lista do que foi desfeito (D-722).
- Provas: `test_etapa5_*` (4 provas: sem o arquivo vai ao GitHub; o arquivo do administrador vale; o de conta comum
  é ignorado; a assinatura de outra chave é recusada antes de baixar).

### Caminho → função

| Caminho | Função |
|---|---|
| Abrir o programa (conta do Kaique) | `ui/aviso_de_atualizacao.ligar_na_janela` → `atualizacao.procurar_ao_abrir` → `comando_de_rodar_a_tarefa` |
| O ajudante rodando (como o sistema) | `--procurar-atualizacao` → `rodar_ao_ligar` → `procurar_e_preparar` (sem mudança) |
| Primeira abertura | `ui/testes_a_distancia_ui.primeira_vez_se_preciso` → `atualizacao.preparar_na_primeira_abertura` → a peça de sempre (`core.testes_a_distancia.executor_atual().aplicar`); com senha, `core.testes_a_distancia.ligar` (sem mudança) |
| Dentro da pergunta do Windows | `--preparar-o-computador` → `preparar_como_administrador` → `criar_tarefa` + `preparar_o_computador` (sem mudança) |
| "Reiniciar agora" | `aplicar_agora_e_reabrir` → `trocar_e_reabrir` → `comando_de_rodar_a_tarefa` |
| Abrir depois do "Depois" | `atender_linha_de_comando` → `trocar_antes_de_abrir` → `trocar_e_reabrir` |
| Depois de trocar (como o sistema) | `--conferir-a-versao-nova` → `conferir_e_refazer_o_ajudante` → `conferir_versao_nova` (sem mudança) + `criar_tarefa` |
| Comando de longe do Samuel | `comando_de_longe_para_atualizar` → `comando_de_rodar_a_tarefa` |
| "É a conta de testes?" | `e_a_conta_de_testes` (o nome fixo `core.testes_a_distancia.NOME_DA_CONTA`) |

**Funções dos testes à distância que a primeira abertura chama, sem mudá-las** (pedido da gerente):
`core.testes_a_distancia.ligar`, `executor_atual`, `definir_executor`, `Passo`, `plano_de_ligar` (só nas provas) e
`NOME_DA_CONTA`. Para a senha ir na mesma pergunta, a peça que fala com o Windows recebe, só durante o `ligar`, o
passo de preparar na frente dos passos dela. Depois ela volta a ser a de sempre.

## Prova dos testes de defeito falhando no código de antes

As 23 primeiras provas novas foram rodadas sobre uma cópia do código de antes (commit `997a3085`, extraída em
`D:\agente_temp_testes\d732-codigo-antigo`). **Resultado: 23 falharam.** A do B1 falhou pelo motivo certo:

```
E   AssertionError: os ganchos do instalador não pedem nada que precise de administrador
E   assert ['criar', 'rodar', 'criar'] == []
```

O gancho de instalar criava e rodava a tarefa, e o de atualizar a criava de novo. A D-735 falhou porque o código de
antes não tinha a pergunta do Windows sem a senha. No código novo, as 23 passam.

## Resultado dos testes (um arquivo por vez, offscreen, `--basetemp=D:/agente_temp_testes/d732`)

| Arquivo | Resultado |
|---|---|
| `tests/test_decisoes_ajudante_da_atualizacao.py` (novo) | 27 de 27 passaram (23 das decisões e 4 da fonte de teste da etapa 5) |
| `tests/test_decisoes_testes_a_distancia.py` | 13 de 13 passaram |
| `tests/test_assinatura.py` | 16 de 16 passaram |
| `tests/test_promessas.py -k "215"` | 1 de 1 passou |
| `tests/test_decisoes_atualizacao.py` | 35 passaram e 3 falharam: os três da tabela abaixo, que a decisão nova muda |

**Ensaio da etapa 3** (`ensaio_velopack.py`): rodado, e o resultado foi **"ENSAIO: CERTO"**.
- Ele continua sem tocar o Windows de verdade: usa pacotes portáteis em `build\ensaio-velopack\`, sem Arquivos de
  Programas, sem tarefa e com um ProgramData de mentira.
- Ele empacota só o programinha do ensaio, com a chave de mentira, nunca o programa de verdade.
- Resultados:
  - A, de 1.1.0 para 1.2.0: trocou, e a versão nova passou no teste;
  - B, a 1.3.0 estragada: voltou para a 1.2.0 (falha anotada como "teste-1.3.0");
  - C, a 1.4.0 com a assinatura de outra chave: recusada, e nada foi baixado.
- Ressalva: o pacote 1.1.0 foi montado antes do último commit, o da fonte de teste. O ensaio sempre passa a pasta
  pela linha de comando, então esse commit não muda o caminho dele. Os pacotes 1.2.0 a 1.4.0 já têm o código final.

## Testes antigos afetados (não mudados, §11.8)

| Teste | Por que quebra | Conserto proposto |
|---|---|---|
| `test_d714_a_tarefa_roda_ao_ligar_como_o_sistema_sem_janela` | Cobra `<BootTrigger>`, e a D-732 tirou o "ao ligar o computador". | Trocar só essa cobrança por "sem gatilho" (`<Triggers>` ausente). O resto do teste continua valendo e passa. |
| `test_d720_o_aviso_tem_reiniciar_agora_e_depois_e_depois_nao_troca` | Cobra a frase "próxima vez que o computador ligar", e a D-734 mudou para "próxima vez que você abrir o programa". | Trocar a frase cobrada pela nova. Os botões, o Enter no "Depois" e o "Depois não troca" continuam e passam. |
| `test_d714_a_instalacao_de_verdade_cria_e_roda_a_tarefa` | Cobra que o gancho de instalar cria e roda a tarefa, o que é justamente o defeito B1 que a D-733 manda tirar. | Apagar o teste ou invertê-lo. A prova nova `test_b1_...` já cobra o contrário. |

Também: `test_d720_depois_do_depois_a_tarefa_troca_quando_o_computador_liga` continua passando, mas o nome ficou
velho (fala em "computador liga"). Sugestão: trocar só o nome.

## Perguntas para o Samuel (a gerente leva à Central)

1. **Se o Kaique disser "Não" à pergunta do Windows da primeira abertura.**
   - **Onde fica:** no notebook dele, logo depois da janela da senha, na primeira vez que ele abre o programa.
   - **Como ficou agora:** a pergunta não volta sozinha. Fica anotado no registro. Sem o "Sim", a versão nova
     nunca entra, e não há botão para pedir de novo (o "Pôr a senha" das Configurações só liga os testes).
   - **O que você escolhe:**
     - (a) **Sugestão:** a pergunta volta na próxima abertura, até ele dizer "Sim".
     - (b) Fica como está.
     - (c) Só comentário.
2. **A espera sem janela do "Depois".**
   - **Como ficou agora:** na abertura seguinte ao "Depois", o programa some por alguns segundos enquanto troca. Sem
     internet, ele desiste logo e abre na versão de hoje. No pior caso (a troca travada), espera até 5 minutos. Se o Kaique clicar de novo no atalho nessa espera, abre a versão
     velha no meio da troca. O que acontece então só a etapa 5 mostra.
   - **O que você escolhe:**
     - (a) **Sugestão:** fica assim, e a etapa 5 mede a espera de verdade.
     - (b) Aparece uma janelinha "Atualizando o programa, um momento". O texto você aprova antes.
     - (c) Só comentário.
3. **Na conta de testes, a primeira abertura não faz nada.**
   - **Por quê:** numa sessão de longe ninguém responde à pergunta do Windows nem à janela da senha. Elas travariam o
     teste.
   - **O que pede:** confirme se fica assim (sugestão: sim).

## Bugs para a Lista de bugs (achados em 17/11, não consertados aqui)

- **B5 (importante, impede a pergunta sem senha na etapa 5; arquivo do outro agente).**
  - O script que roda com licença de administrador, `core/_testes_a_distancia_windows._montar_script`, lê sempre o
    arquivo cifrado da senha (`$blob = Get-Content -Raw ...`) logo na segunda linha, com
    `$ErrorActionPreference = 'Stop'`.
  - Esse arquivo só é gravado quando algum passo usa a senha. Sem senha, o script para antes do primeiro passo.
  - Hoje isso quebra, no Windows de verdade, o `desligar` e a pergunta da primeira abertura sem senha (D-735). A
    pergunta apareceria, e nada seria feito.
  - Conserto sugerido: só ler a senha quando o arquivo existe, ou quando algum passo precisa dela. Não mexi, por ordem
    da gerente.
- **B6 (reforço, a decidir).**
  - A pasta `C:\ProgramData\EditorImpressao\atualizacao` (o `estado.json`) segue as licenças de fábrica do Windows.
    Nelas, uma conta comum pode criar um arquivo antes do sistema. Agora a conta comum também pode mandar o ajudante
    rodar.
  - Com isso, um programa na conta do Kaique poderia "pedir" ao ajudante uma volta para uma versão mais velha.
  - Só versão assinada pelo Samuel entra, então o risco é baixo. Conserto possível: a pergunta da primeira abertura
    fecha essa pasta só para o administrador e o sistema.

## O que só a etapa 5 prova (no PC do Samuel)

- Que a tarefa criada pelo XML aceita a licença "contas comuns mandam rodar". E que a conta comum lê o estado dela
  (`Get-ScheduledTask`), que a espera do "Depois" usa.
- Que o Velopack, rodando como o sistema, troca em Arquivos de Programas sem perguntar nada.
- Que o PowerShell escondido continua depois que o programa fecha e reabre a janela na conta do Kaique.
- Que, dentro da pergunta do Windows, o programa roda no modo `--preparar-o-computador` e cria o ajudante. Que o
  programa abre antes do Visual C++ ser instalado (ressalva antiga da D-727). E o B5 acima.
- Quanto dura a espera do "Depois" e do "Reiniciar agora".
- O aviso da versão nova pode levar até 5 minutos para aparecer depois de abrir. O vigia olha 4 segundos depois de
  abrir e, depois, a cada 5 minutos, e o download leva mais que 4 segundos. Isso não foi mudado (§11.7).

## Arquivos fora do projeto (CLAUDE.md §10.9)

- Criei e deixei lá: `D:\agente_temp_testes\d732-codigo-antigo` (a cópia do código de antes, para a prova de
  reversão, uns 800 MB), `D:\agente_temp_testes\d732-ensaio.txt` (a saída do ensaio) e a pasta de testes
  `D:\agente_temp_testes\d732`. A gerente decide se saem.
- Por engano, apaguei `D:\agente_temp_testes\d732-dono.txt`. Era um arquivo de uma linha ("x") que eu mesmo tinha
  criado um minuto antes, para conferir a leitura do dono de um arquivo. A regra manda não apagar nada fora do
  projeto, nem o que é meu. Fica registrado.

## Ideias para a Lista de espera

- O nome `rodar_ao_ligar` ficou da etapa 3; hoje ele roda quando o ajudante é chamado. Trocar o nome muda testes
  antigos, por isso ficou.
