# Revisão da estrutura do atualizador (18/11/2026)

Revisão feita por um implementador, só lendo. Nenhuma linha do programa nem dos testes mudou. Nenhuma janela abriu na
tela do Samuel, nenhuma pergunta do Windows, nada instalado, nada apagado. Ramo `revisao-atualizador-2026-11-18`.

## A resposta, em poucas frases

1. O atualizador foi montado como se o Windows sempre respondesse "deu certo". Os testes trocam o Windows por peças
   de mentira que sempre respondem assim. Por isso os defeitos só apareceram na etapa 5.
2. Além dos 5 defeitos já conhecidos, a leitura achou **13 defeitos novos**. Três deles provados hoje no Windows de
   verdade, só lendo: depois de desinstalar, **as duas tarefas do Windows continuam lá**; a pasta interna do programa
   em `C:\ProgramData` (789 MB) fica; e essa pasta **aceita arquivos de qualquer conta**, embora quem a usa seja o
   ajudante, que manda em tudo no Windows.
3. Os mais graves para o Kaique, lidos no código:
   - se a internet piscar no segundo em que o programa lê a assinatura, **aquela versão fica recusada para sempre** e o
     Kaique vê "a atualização não deu certo";
   - publicar no GitHub **libera a versão antes de pôr a assinatura**: quem abrir o programa nesse meio-tempo recusa a
     versão para sempre;
   - **abrir o programa durante a troca** (que dura de 7 a 23 minutos) faz o Velopack fechá-lo à força e o programa
     acusar uma falha que não houve;
   - mesmo sem o defeito do PowerShell, **o "Reiniciar agora" espera só 5 minutos** e reabre o programa no meio de uma
     troca que dura 7 ou mais;
   - se a versão nova estiver estragada a ponto de nem abrir, **ninguém volta para a anterior**: quem faz a volta é a
     própria versão nova;
   - **reinstalar depois de desinstalar** deixa o programa sem atualização para sempre, sem aviso.
4. Consertar cada um onde apareceu seria remendo. A seção 3 traz o desenho com **10 regras**, cada uma num lugar só.
   A seção 3b junta a pasta do ajudante e a dos testes à distância num "lugar seguro de fábrica" só, como propôs o
   revisor dos testes à distância.
   A ideia central: **o que o programa lembra não é prova; prova é o que o Windows responde**.
5. A seção 4 é o plano de provar cada peça **de verdade e à vista** no PC do Samuel, uma por uma, antes de montar a
   versão: 14 provas pequenas, umas 11 perguntas do Windows, perto de 2 horas, quase tudo em janelas que ele vê.
6. São 8 perguntas para o Samuel (seção 5).

**Sobre o "provado hoje":** as leituras do Windows foram feitas por volta das 12:00, só lendo e sem administrador,
depois do desinstalar da etapa 5 (11:53) e **antes** da limpeza à mão da fase 12 dela. Às 12:11 as tarefas, a pasta do
ProgramData e a pasta de reserva do Velopack já não existiam: a fase 12 as tirou, e o programa não as tirou sozinho.

Fontes: código do programa (ramo `obra-2026-10-26`, `b74a94e2`); registros e ONDE-PAREI da etapa 5; relatório do
estudo de publicar mais rápido; código do Velopack 1.2.161 (cópia do estudo, só lida); documentação da Microsoft e do
Python citada em cada item; leituras feitas hoje no Windows, só lendo (`icacls`, Agendador de Tarefas, registro).

---

## 1. Cada coisa que o atualizador pede ao Windows

Para cada uma: **onde** no código; **como falha** no Windows de verdade, com a fonte; **hoje**, o que o programa faz
quando falha; **devia**, o que fazer. "Provado" quer dizer visto no Windows de verdade. "Lido" quer dizer lido no
código ou na documentação, ainda sem prova.

### 1.1 Abrir um PowerShell escondido e solto (o "trocar e reabrir")

- **Onde:** `atualizacao._lancar_escondido` (linhas 956-968), usado pelo "Reiniciar agora" e pela abertura depois do
  "Depois" (`trocar_e_reabrir`, 971-989).
- **Como falha:**
  - Com `DETACHED_PROCESS`, o PowerShell 5.1 sai sem rodar nada (**provado** na etapa 5:
    `registros/variantes-lancar-escondido.txt`). A Microsoft (página "Process Creation Flags") diz que
    `CREATE_NO_WINDOW` é ignorado quando vem junto com `DETACHED_PROCESS`. Então o processo nasce sem console nenhum,
    e o PowerShell não roda assim.
  - Antivírus e regras do Windows (proteção "ASR" do Defender) podem bloquear PowerShell com `-EncodedCommand`
    escondido, que é o jeito típico de programa malicioso (lido: documentação do Microsoft Defender sobre as regras de
    redução de superfície de ataque). No PC do Samuel não bloqueou; no notebook do Kaique não se sabe.
  - Um `Popen` que dá certo só quer dizer que o processo nasceu, não que o script rodou.
- **Hoje:** anota "o ajudante foi chamado; o programa volta sozinho" e sai. O programa não volta (**provado**, fase 4).
- **Devia:** um jeito só de lançar processo solto, sem `DETACHED_PROCESS`, e com um sinal de vida: o processo lançado
  escreve "comecei" num arquivo e quem lançou espera esse sinal por alguns segundos. Sem o sinal, avisa e abre o
  programa na versão de hoje.

### 1.2 Abrir o Update.exe solto (a volta para a versão anterior)

- **Onde:** `_aplicar_pacote_quando_sair` (669-674).
- **Como falha:** o mesmo par de opções do 1.1. Funcionou na etapa 5 (a volta da 1.1.3, **provado**) porque o
  Update.exe não é um PowerShell. É uma segunda regra para a mesma coisa (§11.12).
- **Hoje:** não confere se a volta aconteceu.
- **Devia:** usar a mesma peça do 1.1, e quem faz a volta confere depois que a versão anterior está no lugar.

### 1.3 Rodar um comando do Windows e esperar (schtasks, vc_redist, desinstalador antigo, teste rápido)

- **Onde:** `_rodar` (786-793), `rodar_teste_rapido` (629-637).
- **Como falha:**
  - As ferramentas de linha de comando do Windows em português respondem na página de código OEM (850). O `_rodar`
    lê com a do Windows (1252). Resultado: "ÒXITO" no lugar de "ÊXITO" (**provado**: `atualizacao.log`, linhas de
    09:34:32, 09:59:30 e 11:39:09; página OEM 850 lida no registro deste PC). Fonte: documentação do Python,
    `subprocess` (o texto é lido com a codificação do local) e o codec "oem" do Python no Windows.
  - Tempo esgotado: vira código -1 e a mensagem do Python.
- **Hoje:** só o código decide; a mensagem vai torta para o registro que a gerente lê de longe (D-719).
- **Devia:** ler a saída na página OEM, em um lugar só.

### 1.4 Pedir licença de administrador ("Deseja permitir...?") na primeira abertura

- **Onde:** `preparar_na_primeira_abertura` (1460-1514) e `passo_de_preparar_o_computador` (1410-1438), que usam a
  peça do outro agente, `core/_testes_a_distancia_windows._rodar_elevado` (80-100).
- **Como falha:**
  - "Não" do Kaique: o Windows devolve o erro 1223. O programa lê 0 ("deu certo"), porque usa `ctypes.get_last_error()`
    sem ter aberto a biblioteca com `use_last_error=True` (**provado**: `registros/prova-get-last-error.txt`). Fonte:
    documentação do Python, `ctypes.get_last_error`.
  - Programa que não está na frente: o Windows não mostra a pergunta no meio da tela, só um botão piscando na barra de
    tarefas; ninguém clica e ela se cancela (documentado pela Microsoft em "How User Account Control works";
    **visto** na etapa 5, 08:26 a 08:28: "não apareceu nada"). O pedido vai sem a janela do programa como dona
    (`hwnd` vazio).
  - Área de trabalho que não é a de verdade: "Não há suporte para o pedido" (**provado**, fase 3.1). Falta
    `SEE_MASK_FLAG_NO_UI`, que impede a caixa crua de erro (documentação da Microsoft, `SHELLEXECUTEINFOW`).
  - Conta do Kaique sem administrador: a pergunta pede a senha de um administrador, não "Sim/Não". Não se sabe como é a
    conta dele.
  - **A janela congela** enquanto espera (lido): a pergunta e a preparação rodam no fio principal, antes do laço da
    janela (`main.py` 96 → `testes_a_distancia_ui.py` 166/170 → `WaitForSingleObject` sem limite, linha 96). A
    preparação pode levar até 10 min (Visual C++) mais 15 min (desinstalador antigo). Contra o CLAUDE.md §3
    ("Interface nunca congela"). Na etapa 5 ficou 91 s parada.
- **Hoje:** depois de um "Não" ou de uma falha, grava "computador preparado" e nunca mais pergunta (**provado**, 08:19,
  contra a D-741).
- **Devia:** a peça única de "pedir licença" devolve três respostas certas (deu certo, a pessoa disse "Não", falhou com
  o código); leva a janela do programa como dona; não mostra caixa crua; roda por trás com a janela respondendo e uma
  frase "Preparando o computador..."; e a resposta final é conferida no Windows (regra 2 da seção 3).

### 1.5 Criar, refazer e apagar tarefas do Agendador (o ajudante e o "desfazer")

- **Onde:** `criar_tarefa` (1155-1167), `criar_as_tarefas` (1384-1402), `apagar_tarefa` (1177-1181),
  `core/testes_a_distancia._comando_preparar_o_desfazer` e `_passos_das_nossas_tarefas`.
- **Como falha:**
  - Sem administrador, criar e apagar dão "Acesso negado". O gancho de desinstalar roda sem administrador (achado B1)
    e dá esse erro (**provado**: `atualizacao.log` 11:53:41, "apagar a tarefa do Windows: NÃO deu certo (ERRO: Acesso
    negado.)").
  - **A tarefa "desfazer" rodou e falhou**: última execução 11:53:41, resultado 1. Por isso **as duas tarefas continuam
    no Agendador depois do desinstalar** (**provado hoje**, só lendo, com `Get-ScheduledTaskInfo`). O ajudante aponta
    para `C:\Program Files\EditorImpressaoPrograma\current\EditorImpressao.exe`, que não existe mais.
  - O desfazer depende de um arquivo (`desfazer.ps1`) numa pasta cuja licença o outro agente achou estragada (acesso
    negado até para o administrador, fase 7). Por isso o desinstalar do atualizador depende de uma peça de outra parte
    do programa.
- **Hoje:** o registro diz "mandado" e o programa segue; ninguém confere.
- **Devia:** a limpeza do desinstalar não depender do gancho de 30 s nem da pasta dos testes (regra 9 da seção 3), e
  terminar com a conferência: as tarefas não existem mais.

### 1.6 Mandar o ajudante rodar e olhar se ele está rodando

- **Onde:** `comando_de_rodar_a_tarefa` (1041-1047), `procurar_ao_abrir` (1062-1080), o script de trocar (921-935).
- **Como falha:**
  - Tarefa que não existe: "O sistema não pode encontrar o arquivo especificado" (**provado**, 08:19:31).
  - `MultipleInstancesPolicy IgnoreNew`: pedido feito com o ajudante rodando é ignorado sem erro.
  - O ajudante sai logo depois de pedir a troca; a troca segue no Update.exe. Quem olha "a tarefa está rodando?" acha
    que acabou, e não acabou (lido, linha 588).
- **Hoje:** só anota. A conta de testes e a do Kaique podem mandar rodar (**provado**, fases 3 e 9).
- **Devia:** "terminou" vem de um sinal escrito pelo ajudante no fim de cada fase, não do estado da tarefa.

### 1.7 A marca "programa aberto" (mutex do Windows)

- **Onde:** `marcar_programa_aberto` e `ha_programa_aberto` (745-783).
- **Como falha:** só é olhada uma vez, depois de baixar (581). Depois disso, abrir o programa não impede a troca.
- **Hoje:** funciona para "baixar com o programa aberto → pendente" (**provado**, fase 4).
- **Devia:** uma segunda marca, "trocando", que o ajudante segura do começo ao fim da troca; o programa, ao abrir, olha
  essa marca primeiro (regra 6 da seção 3).

### 1.8 Gravar e ler em `C:\ProgramData\EditorImpressao`

- **Onde:** `pasta_do_estado`, `registrar`, `gravar_estado`, `registrar_falha` (207-273), `voltar_para_a_anterior`
  (652-655), `arquivo_do_preparo` (1405).
- **Como falha:**
  - **Contas comuns podem criar arquivos e pastas ali** (**provado hoje** com `icacls`): `BUILTIN\Usuários:(CI)(WD,AD)`
    em `atualizacao` e em `volta`. E a conta `fotog` tem controle total da pasta de cima, porque foi o gancho de
    instalar (que roda na conta de quem instala, sem administrador) que a criou ao escrever a primeira linha do
    registro. O ajudante, que roda como o sistema, grava ali o estado, o registro e o pacote da volta. Quem consegue
    criar o arquivo ou a pasta antes dele pode desviar essa gravação (tipo de falha conhecido do Windows, "seguir um
    atalho de pasta em área gravável"; ver as notas da Microsoft sobre licenças padrão do ProgramData). Contra a D-717
    ("um teste não consegue mudar o Windows"). **Lido, não provado.**
  - Disco cheio: `gravar_estado` levanta erro; o ajudante registra e sai (ver 1.14).
  - A pasta `volta` (789 MB) nunca é limpa (**provado hoje**: continua lá depois do desinstalar).
- **Hoje:** nada confere a licença da pasta.
- **Devia:** sair do ProgramData para o "lugar seguro de fábrica" do outro revisor (seção 3b): uma pasta própria em
  Arquivos de Programas, ao lado da pasta do programa, criada na pergunta de administrador, só com as licenças que o
  Windows dá ali (nenhum comando de licença à mão). A janela do Kaique nunca grava nela; o registro da janela vai para a
  pasta da conta dele.

### 1.9 Ler o dono de um arquivo e o registro do Windows

- **Onde:** `_dono_do_arquivo` (428-449, a fonte de teste); `_ler_versao_do_visual_c` (1188-1205); `_ler_chave_do_inno`
  (1257-1266).
- **Como falha:** chave ausente ou sem licença: devolve "não há". Funcionou na etapa 5 (**provado**).
- **Hoje:** certo. Ressalva: a "fonte de teste" (um arquivo que troca o GitHub por uma pasta) vai dentro do programa
  do Kaique. Só o administrador cria esse arquivo e a assinatura continua valendo, mas é uma peça de teste no
  programa de verdade.
- **Devia:** ficar como está, documentado; ou sair do programa depois da entrega (é escolha técnica, não do Kaique).

### 1.10 Instalar o Visual C++ e tirar a instalação antiga

- **Onde:** `instalar_visual_c_se_faltar` (1219-1239), `tirar_instalacao_antiga` (1292-1310).
- **Como falha:** 1618 (outra instalação do Windows em andamento, por exemplo uma atualização do Windows) e 1603
  (erro geral), códigos documentados do Windows Installer; desinstalador antigo que pede reiniciar. A instalação
  antiga saiu certa na etapa 5 (**provado**, 09:02:07).
- **Hoje:** devolve "não feito" (D-749: a pergunta volta). Certo.
- **Devia:** igual, com a mensagem do código em português no registro.

### 1.11 O Velopack na conta do Kaique

- **Onde:** `versao_que_roda` (507-514), `e_portatil` (1313-1325), `_rodar_o_velopack` em toda abertura (1600-1614,
  chamado por 1638).
- **Como falha:**
  - Sem licença para gravar em Arquivos de Programas, o Velopack usa a pasta de reserva
    `%LOCALAPPDATA%\EditorImpressaoPrograma` e copia o Update.exe para ela (**provado**: 5,2 MB, nasceu às 07:58 e
    continua depois do desinstalar). O desinstalador do Velopack 1.2.161 não a apaga (problemas #989 e #1004 do
    Velopack, consertados no commit `b40a2781`, que só está na prévia 1.3.39; conferido hoje no código).
  - Qualquer erro do Velopack na conta do Kaique faz `e_portatil` responder "é portátil" (1324-1325), e aí
    `procurar_ao_abrir` desiste sem anotar nada (1075-1076). A atualização desliga em silêncio.
- **Hoje:** a pasta sobra e o erro some.
- **Devia:** a janela do Kaique não cria o Velopack nunca. A versão vem de um arquivo que o ajudante escreve; "é
  portátil" é a regra do próprio Velopack, o arquivo `.portable` ao lado do Update.exe (`locator.rs`, linha 376); o
  `_rodar_o_velopack` só roda quando a linha de comando traz um gancho do Velopack. Sem o Velopack na conta, a pasta de
  reserva não nasce (é a causa, não o sintoma).

### 1.12 O Velopack como o sistema: procurar, baixar, trocar

- **Onde:** `procurar_e_preparar` (536-590), via `wait_exit_then_apply_updates`.
- **Como falha** (lido no código do Velopack 1.2.161, `apply_windows_impl.rs` e `util_windows.rs`):
  - **A troca mata todo processo que estiver rodando da pasta do programa** (`force_stop_package`, linha 159), sem
    aviso. Se o Kaique abrir o programa durante os 7 a 23 minutos da troca, ele é fechado à força.
  - Primeira troca de pastas falha (arquivo preso por antivírus, 10 tentativas de 1 s): "Unable to start the update";
    a versão de hoje fica.
  - **Segunda troca falha: o programa fica sem a pasta `current`** ("the app was left in a broken state"). Não abre,
    não atualiza, não desinstala. O Velopack só passou a voltar a pasta velha no commit `afa30e56` (10/10/2026), que
    não está na 1.2.161 (conferido).
  - Desligar o notebook no meio: na extração, nada se perde; entre as duas trocas de pasta, o mesmo estrago de cima.
  - Diferença ("só o que mudou"): conferida contra uma soma que não é assinada (achado do estudo; contra a D-724).
- **Hoje:** com a troca em andamento, o estado fica "aplicando"; qualquer leitura nessa hora conta como **falha**
  (`situacao`, 309-310). A próxima chamada do ajudante grava a falha e põe a versão na lista de nunca mais tentar
  (722-724).
- **Devia:** ver regras 3, 4, 5 e 6 da seção 3.

### 1.13 O instalador (.msi) e os ganchos

- **Onde:** `empacotar.comando_do_vpk` (1055-1079); `ao_instalar`, `ao_desinstalar` (1541-1580).
- **Como falha:** os ganchos rodam na conta de quem instala, **sem administrador** (achado B1, provado em 16/11); o de
  desinstalar tem tempo curto. 1618, 1603 e 1638 são os códigos de erro do Windows Installer. O gancho de instalar cria
  `C:\ProgramData\EditorImpressao` com a conta comum como dona (**provado hoje**, ver 1.8).
- **Hoje:** o de desinstalar não confere nada.
- **Devia:** o gancho de instalar não grava nada fora da pasta da conta; a limpeza de desinstalar roda como o
  sistema, depois que o Windows avisa que o programa saiu (regra 9 da seção 3).

### 1.14 A rede e o GitHub

- **Onde:** `Fonte` (335-394), `conferir_assinatura_do` (522-529).
- **Como falha:** sem internet; tempo esgotado (60 s); GitHub fora do ar; limite de 60 consultas por hora sem senha
  (documentação do GitHub); internet do celular, que cobra por megabyte (826 MB por versão sem a diferença).
- **Hoje:** **qualquer erro ao ler a assinatura vira "assinatura recusada"** (528 → 573-576): a versão entra na lista
  de nunca mais tentar e o Kaique vê "A atualização não deu certo. O programa voltou para a versão anterior", sem nada
  ter sido instalado.
- **Devia:** falha passageira (rede, tempo, disco) não é recusa: tenta de novo na próxima abertura, sem aviso.

### 1.15 Pastas temporárias

- **Onde:** `criar_tarefa` (1159-1164), `aplicar_no_windows` (outro agente, 105).
- **Como falha:** no Python 3.13 e 3.14, `tempfile.mkdtemp` cria a pasta só para quem a criou (conserto de
  segurança CVE-2024-4030; notas do Python sobre `os.mkdir` com modo 0o700). O que um administrador escreve nela a
  conta comum não lê (**provado**, fase 7: PermissionError).
- **Hoje:** no atualizador só é usada dentro do administrador (certo). No outro agente, quebrou.
- **Devia:** quando dois níveis de licença trocam arquivos, usar uma pasta com licença dada de propósito.

### 1.16 Publicar (PC do Samuel)

- **Onde:** `publicar_versao_kaique.publicar` (153-189).
- **Como falha:**
  - **No GitHub, a versão é liberada antes de a assinatura subir** (`--publish` na 181, assinatura na 186). Quem abrir
    o programa nesse meio-tempo cai no 1.14 e recusa a versão para sempre. Se o envio da assinatura falhar, a versão
    fica publicada sem assinatura para todos.
  - `--pasta-pronta` publica uma pasta cuja versão de dentro pode ser outra (na etapa 5, todo registro diz "versão
    1.1.0" numa 1.1.5). Nada confere.
  - Lentidão de 59 a 82 min: ver o estudo.
- **Devia:** sobe como rascunho, sobe a assinatura, confere, e só então libera; recusa pasta pronta com outra versão;
  anota de que commit saiu a versão.

### 1.17 Proteções do Windows contra programa sem certificado

- **Como falha:** o "Controle Inteligente de Aplicativos" do Windows 11 bloqueia programa sem certificado pago, e não
  dá para liberar um programa só (página de suporte da Microsoft "Smart App Control"). Neste PC está desligado (lido
  hoje no registro: 0). No notebook do Kaique não se sabe; num Windows novo ele começa "em avaliação" e pode ligar
  sozinho. O SmartScreen avisa ao abrir o .msi baixado.
- **Devia:** conferir no notebook antes de instalar (pergunta 8).

---

## 2. Defeitos novos (achados nesta leitura)

Separados dos já conhecidos. "Provado" = visto no Windows de verdade; "lido" = falta provar.

1. **Rede piscando vira recusa para sempre** (lido). `atualizacao.py` 522-529 transforma qualquer erro de leitura em
   motivo de recusa; 573-576 grava "recusada"; 269 põe a versão em "nunca mais tentar". O aviso diz "voltou para a
   versão anterior" sem nada ter sido instalado.
2. **Publicar no GitHub fica pela metade** (lido). `publicar_versao_kaique.py` 181-186: libera a versão e só depois
   envia a assinatura. Junto com o 1, a versão fica recusada para quem abriu nesse meio-tempo.
3. **O "Reiniciar agora" espera 5 minutos; a troca leva 7 a 23** (lido; tempos medidos na etapa 5). `LIMITE_DA_TROCA_S
   = 300` (160), usado em 923-944. Mesmo sem o `DETACHED_PROCESS`, o programa seria reaberto no meio da troca. A D-742
   foi decidida com "alguns segundos, até 5 minutos".
4. **Abrir o programa durante a troca** (lido no nosso código e no do Velopack). O ajudante sai logo depois de pedir a
   troca (588). Durante a troca, `situacao` lê "aplicando" como falha (309-310), a janela mostra o aviso de falha, a
   próxima chamada do ajudante grava a falha e risca a versão (722-724), e o Velopack mata o programa aberto
   (`apply_windows_impl.rs` 159).
5. **Quem socorre é a própria versão nova** (lido). A conferência e a volta rodam no `.exe` novo
   (`--conferir-a-versao-nova`), e o ajudante aponta para esse mesmo `.exe` (1147). Uma versão que nem abre deixa o
   programa morto, sem volta e sem aviso. A versão estragada da etapa 5 (sem o Tesseract) abria; esse caso nunca foi
   testado.
6. **A volta depende da internet e o aviso diz que voltou antes de saber** (lido). `voltar_para_a_anterior` baixa a
   anterior (653-658); se falhar, só anota. A falha já foi gravada com a frase "voltou" (693-696).
7. **Reinstalar deixa o programa sem atualização para sempre** (lido). A marca "computador preparado" (1513, 1519)
   mora nas Configurações do Kaique, que de propósito ficam depois do desinstalar (CLAUDE.md §7). Reinstalado, ele não
   pergunta de novo, o ajudante não existe, e só o registro diz "não consegui chamar o ajudante".
8. **Desinstalar deixa as duas tarefas do Windows** (**provado hoje**, só lendo). "Desfazer testes a distancia": última
   execução 18/11 11:53:41, resultado 1. "Procurar versao nova" continua, apontando para um `.exe` que não existe.
9. **Desinstalar deixa `C:\ProgramData\EditorImpressao`** (**provado hoje**): o estado, o registro, o `preparo.txt` e a
   cópia da volta de 789 MB. Nenhum plano de desfazer cita essa pasta.
10. **A pasta do ajudante aceita arquivos de contas comuns** (licença **provada hoje** com `icacls`; o desvio é lido,
    não provado). Ver 1.8. Contra a D-717.
11. **A janela congela na primeira abertura** (lido; a etapa 5 viu 91 s parada). Ver 1.4. Contra o CLAUDE.md §3.
12. **Erro do Velopack na conta do Kaique desliga a atualização em silêncio** (lido). `e_portatil` 1324-1325 e
    `procurar_ao_abrir` 1075-1076.
13. **Falha passageira na troca vira falha para sempre** (lido). Arquivo preso, notebook desligado no meio ou disco
    cheio deixam "aplicando"; a próxima chamada grava "troca" e risca a versão (722-724, 269).

Menores:

- O teste automático do lançamento **cobra o defeito**: `tests/test_decisoes_ajudante_da_atualizacao.py` 281-290 exige
  `DETACHED_PROCESS`. Os testes que rodam um PowerShell de verdade usam outro jeito de lançar (`-File`, sem as duas
  opções, por volta da linha 616). O caminho de verdade nunca rodou num teste. Mudar esse teste precisa do ok
  (pergunta 7).
- Duas regras para "lançar solto" (1.1 e 1.2).
- Letras trocadas no registro (1.3) e "versão 1.1.0" em todas as linhas (1.16).
- O aviso de falha é marcado como visto **antes** de aparecer (`ui/aviso_de_atualizacao.py` 125-126): se o programa
  fechar nessa hora, ele não volta.

### Os defeitos já conhecidos, com a causa de cada um

- **"Reiniciar agora" não volta, e com versão esperando o programa não abre:** `DETACHED_PROCESS` (1.1). Para
  funcionar mesmo, é preciso resolver também os novos 3 e 4.
- **A diferença não passa pela assinatura:** o arquivo de versões do servidor não é assinado (estudo, 1.12).
- **Publicar leva ~1 h e a troca leva 7 a 23 min:** os 35 mil arquivos do motor do Kraken, que nunca muda, entram em
  toda versão; publicar no HD externo; remontar a diferença no notebook (estudo). A troca de 7,5 min é quase toda
  abrir esses 35 mil arquivos.
- **O aviso de falha aparece só uma vez:** é uma marca por conta, gravada antes de mostrar; a frase é a mesma para
  todos os casos, e em dois deles não é verdade (recusada: nada foi instalado; volta que não deu certo). A gerente só
  sabe se ler o registro de longe.
- **Desinstalar deixa `%LOCALAPPDATA%\EditorImpressaoPrograma`:** a causa é o Velopack ser criado na conta do Kaique
  (1.11), mais o desinstalador da 1.2.161 que não limpa essa pasta (#989 e #1004 do Velopack).

---

## 3. Como a estrutura fica certa

O que **fica**: o Velopack; o ajudante como o sistema, chamado sem pergunta; uma pergunta do Windows na primeira
abertura; a assinatura do Samuel; o aviso com "Reiniciar agora" e "Depois"; a janelinha; o registro lido de longe;
`registrar_falha` e `situacao` como lugar único de cada decisão.

O que **muda**, em 10 regras. Cada uma mora num lugar só.

1. **Uma peça só para cada pedido ao Windows.** "Lançar solto", "rodar e esperar", "pedir licença" e "mandar a tarefa
   rodar" ficam numa função cada, que devolve sempre uma de três respostas: deu certo, a pessoa disse "Não", falhou
   (com o código e a frase em português). Nenhuma devolve "deu certo" sem prova. *Limpo.* Trocar só a opção do
   PowerShell e o `get_last_error` onde estão seria remendo: a próxima peça repetiria o erro.
2. **Conferir em vez de lembrar.** "O computador está preparado" é a resposta do Windows, e não uma marca nas
   Configurações: a tarefa existe, aponta para este programa e tem a licença certa. Conferir não pede pergunta e leva
   menos de 1 s. Resolve o "Não" que vira "Sim", o reinstalar sem ajudante e a conta que muda. *Limpo.*
3. **Falha passageira não é falha.** Sem internet, tempo esgotado, disco cheio, arquivo preso, notebook desligado no
   meio: tenta de novo na próxima abertura, sem aviso. Só três coisas riscam a versão e avisam: assinatura que não
   confere, pacote estragado e teste rápido que falha. *Limpo.* Aumentar o tempo de espera da rede seria remendo.
4. **O aviso diz o que aconteceu.** Uma frase para cada caso (recusada; instalada e voltou; não conseguiu voltar),
   escolhida pelo mesmo `registrar_falha`. É marcada como vista só depois de aparecer, e o registro anota que o Kaique
   viu. As frases são do Samuel (pergunta 4).
5. **O socorro mora fora do que é trocado.** Antes de trocar, o ajudante guarda a versão de hoje no disco (o pacote
   que o Velopack já tem; a pasta `volta` deixa de baixar da internet). Quem confere a versão nova e volta, se preciso,
   é uma peça que não está dentro de `current`: um script do ajudante numa pasta protegida, que roda o teste rápido no
   `.exe` novo e, se ele nem abrir, aplica a versão guardada. Resolve os novos 5 e 6 e cobre a falha do Velopack 1.2.161
   (programa sem `current`). *Limpo*; trocar o Velopack pela prévia é outra saída (pergunta 6).
6. **Sinal de fim em vez de relógio, e trava durante a troca.** O ajudante escreve "troca começou / terminou bem /
   voltou / falhou" e segura a marca "trocando" do começo ao fim. A janelinha e a reabertura esperam o sinal (com um
   limite de segurança medido, não de 5 min). Se o Kaique clicar no atalho com a marca "trocando", aparece a janelinha
   e o programa abre quando a troca acaba, em vez de ser fechado à força (pergunta 3). Resolve os novos 3 e 4.
   *Limpo.* Trocar 300 s por 1800 s seria remendo.
7. **A assinatura cobre tudo o que se instala, e publicar nunca fica pela metade.** Ou sem diferença, ou com a
   diferença assinada (pergunta 3 do estudo). No GitHub: sobe como rascunho, sobe a assinatura, confere lendo de volta
   do GitHub, e só então libera. Um número de versão só: o publicar recusa pasta pronta de outra versão e anota o
   commit. *Limpo.*
8. **A janela do Kaique não mexe no Velopack nem na pasta do ajudante.** Ela só pede ao ajudante e lê o que ele
   escreveu. A pasta do ajudante é a "pasta segura do programa", a mesma dos testes à distância (seção 3b). O registro
   da janela vai para a pasta da conta. Resolve a pasta de reserva que sobra e a pasta gravável por todos. *Limpo.*
   Apagar a pasta de reserva no desinstalar, sem deixar de criá-la, seria remendo; trancar o ProgramData com comandos
   de licença à mão também (foi o que estragou a pasta dos testes à distância).
9. **Desinstalar limpa como o sistema, depois que o Windows avisa que o programa saiu.** Uma tarefa criada na primeira
   abertura, disparada pelo próprio aviso do Windows Installer ("o produto foi removido", evento 1034 do registro de
   aplicativos), roda como o sistema, sem os 30 s do gancho e sem depender da pasta dos testes. Tira as tarefas, a
   pasta do ajudante e as sobras do Velopack em cada conta. Nunca toca os projetos. Termina conferindo e deixa a lista
   do que tirou. **Falta provar** que esse aviso não aparece também numa atualização por .msi novo. *Limpo*, se a prova
   passar; se não passar, a outra saída é a mesma tarefa conferir, ao ligar o computador, se o programa ainda existe
   (pergunta 5).
10. **A janela nunca congela.** A pergunta e a preparação da primeira abertura rodam por trás, com a janela respondendo
    e a frase "Preparando o computador...". *Limpo.*

## 3b. A pasta do ajudante e a dos testes à distância: dono, licença e uma peça só

Pedido da gerente (recado do revisor dos testes à distância, achado N11 dele, ramo `revisao-distancia-2026-11-18`).

**Dono e licença de cada pasta, segundo o código** (o Windows não foi lido como administrador):

- **`C:\ProgramData\EditorImpressao`** e **`...\atualizacao`** nascem juntas na **instalação**: o gancho de instalar
  (`atualizacao.ao_instalar`, 1549) chama `registrar`, que cria as duas pastas (`caminho.parent.mkdir(parents=True)`,
  228). Esse gancho roda **na conta de quem instala, sem administrador** (achado B1). Então:
  - o **dono** das duas é a conta de quem instalou (no notebook, a do Kaique);
  - a **licença** é a herdada do ProgramData, e nenhum código a muda: o sistema e os administradores, tudo; quem
    criou ("proprietário criador"), tudo; os Usuários, ler, e também **criar arquivos e pastas** dentro.
  - Lido hoje **sem administrador**, por volta das 12:00, antes de a fase 12 da etapa 5 limpar o PC (`icacls`): bate
    com o código. `SAMUEL-PC\fotog` com controle total nas duas, e `Usuários:(CI)(WD,AD,WEA,WA)` em `atualizacao` e em
    `volta`. Às 12:11 as pastas já não existiam (fase 12), e o dono não chegou a ser lido.
- **`atualizacao\atualizacao.log`:** a primeira linha é escrita pelo mesmo gancho; dono a conta de quem instalou, com
  controle total. Lido hoje: `fotog:(I)(F)`.
- **`atualizacao\estado.json`, `atualizacao\volta\`:** criados pelo ajudante (o sistema). A licença é herdada; dentro de
  `volta` os Usuários também podem criar.
- **`atualizacao\preparo.txt`:** criado pelo PowerShell da pergunta de administrador; licença herdada.
- **`fonte-de-teste.txt`:** só na etapa 5; o programa aceita só se o dono for administrador ou o sistema.
- **`testes-a-distancia\`:** criada pelo PowerShell de administrador, que depois põe a licença à mão (dono
  administradores, sem herança, `/T` nos arquivos). O outro revisor provou que isso deixa os arquivos sem licença
  nenhuma.

**O risco, nas duas partes:**

- Quem é dono da pasta de cima pode trocar de lugar qualquer pasta de dentro, inclusive a trancada.
- Qualquer conta, inclusive a de testes, pode criar arquivos e pastas onde o sistema vai gravar depois.
- O sistema roda o script dos testes à distância e grava o estado e a cópia da volta do atualizador ali.

**O desenho do outro revisor serve para o atualizador: sim, e deve ser uma peça só.** "O que roda como o sistema mora
num lugar seguro de fábrica, sem licença à mão" resolve os dois casos.

- **O lugar:** uma pasta própria em Arquivos de Programas, **ao lado** da pasta do programa (nunca dentro dela: o
  Velopack troca e apaga a pasta dele ao atualizar e ao desinstalar). Ali o Windows já deixa só o administrador e o
  sistema criarem e mudarem; os Usuários leem. Nenhuma conta comum cria nada, e nenhum comando de licença é preciso.
  O nome exato é detalhe técnico, mas não pode lembrar a pasta dos projetos (a regra da D-763).
- **Quem cria:** a pergunta de administrador da primeira abertura, sempre (nunca o gancho de instalar).
- **O que vai para lá:**
  - do atualizador: o estado, o registro, a cópia para voltar, o sinal "trocando", o socorro (regra 5) e a marca do
    preparo;
  - dos testes à distância: o script do desfazer e o caderninho do antes.
- **Uma função só** diz onde é a pasta e **uma função só** a cria e confere (é pasta de verdade, não um atalho para
  outro lugar, e com a licença do Windows). Os dois lados usam as duas.
- **O que continua igual:** a gerente lê o registro de longe pela conta de testes, porque os Usuários leem (D-719). A
  janela do Kaique lê o estado para mostrar o aviso, mas não grava; o que ela anota vai para a pasta da conta dela.
- **Uma chave do registro do Windows em HKLM\SOFTWARE** serve só para dados pequenos (o estado, a marca do preparo).
  Para o registro que cresce, para a cópia de 788 MB e para os scripts, é preciso pasta. Por isso a sugestão é a pasta
  em Arquivos de Programas, um lugar só para tudo.
- **O desinstalar** (regra 9) apaga essa pasta inteira no fim, como o sistema, depois de conferir; os projetos nunca
  estão nela.

O que muda para quem usa: nada visível. O ProgramData deixa de ter pastas do programa.

**Fica para depois, só se ainda ficar lento:** tirar o motor do Kraken do pacote que se troca (estudo, pergunta 4). É
o único jeito de a troca cair de minutos para segundos. É mudança grande; plano antes.

**O que isso muda para quem usa:**

- O Kaique deixa de ver aviso de falha falso.
- Clicar no atalho durante a troca mostra a janelinha, em vez de o programa sumir.
- "Reiniciar agora" mostra a janelinha e volta (pergunta 1).
- A primeira abertura não congela.
- Reinstalar volta a perguntar.
- Desinstalar deixa o notebook limpo. Os projetos ficam, como sempre.
- Nada muda nos livros nem no PDF.

---

## 4. Como provar cada peça de verdade e à vista (D-767)

**Regras de todas as provas:**

- No PC do Samuel, na área de trabalho de verdade, nunca escondida.
- Cada prova abre uma janela pequena de PowerShell visível que diz o que está fazendo e mostra o resultado.
- O Samuel clica "Sim" quando a pergunta do Windows aparecer.
- Nada de peça de mentira no lugar do Windows.
- Os testes automáticos continuam para o resto, mas não contam como prova destas peças.
- As provas 1 a 4, 13 e 14 rodam com o código novo antes de montar a versão. As outras pedem o programa instalado.
- Depende do alcance da D-767 que a gerente está confirmando (versões de teste numa pasta do D: ou no GitHub).

1. **Lançar solto** (regra 1). O programa lança um script que escreve "rodei às HH:MM:SS" e mostra uma janela; depois,
   o mesmo com o programa já fechado. Ele vê a janela aparecer. 0 perguntas, 2 min.
2. **Pedir licença, as três respostas** (regras 1 e 2). (a) "Sim" → a janela de prova diz "rodou como
   administrador"; (b) "Não" → diz "você disse Não" (código 1223 lido certo); (c) com outra janela na frente → a
   pergunta aparece no meio da tela, não na barra; (d) um arquivo que não existe → frase em português, sem a caixa
   crua do Windows. 3 perguntas, 5 min.
3. **A pasta segura do programa** (regra 8, seção 3b; é a mesma prova P3 do revisor dos testes à distância: fazer uma
   vez só). Cria com administrador em Arquivos de Programas e mostra na janela a licença que o Windows deu, sem comando
   de licença; a conta comum lê e tenta criar um arquivo ("recusado"); o sistema lê e grava. 1 a 2 perguntas, 3 min.
4. **O ajudante criado, chamado e conferido** (regra 2). Cria, a conta comum manda rodar, a janela mostra o fim do
   registro e a resposta "preparado: sim" lida do Windows; apaga a tarefa e mostra "preparado: não". 2 perguntas, 3
   min.
5. **A troca com sinal e janelinha** (regra 6). Programa instalado; uma versão nova; "Reiniciar agora": a janelinha
   fica visível o tempo todo e o programa volta na versão nova. Medir quanto levou. 0 perguntas, ~10 a 25 min.
6. **Abrir durante a troca** (regra 6). No meio da troca, ele clica no atalho: aparece a janelinha, nada é fechado à
   força, o programa abre no fim. 0 perguntas, ~10 min.
7. **Falha passageira** (regra 3). Com a versão nova publicada, desligar o cabo/Wi-Fi na hora de ler a assinatura (o
   teste avisa a hora certa): nenhum aviso; religar e abrir de novo: a versão entra. 0 perguntas, 5 min.
8. **Versão que nem abre** (regra 5). Uma versão com o `.exe` quebrado de propósito: o socorro volta para a anterior
   sem internet, e o aviso certo aparece. 0 perguntas, ~15 min.
9. **Assinatura em tudo o que se instala** (regra 7). Conforme a pergunta 3 do estudo: sem diferença, mostrar no
   registro que só o pacote inteiro, conferido, foi usado; com diferença assinada, uma diferença trocada é recusada
   antes de instalar. 0 perguntas, 5 a 15 min.
10. **Publicar sem ficar pela metade** (regra 7). Publicar no GitHub como rascunho, a janela mostra a assinatura lida
    de volta, libera, e o programa instalado acha a versão; apagar a versão de teste no fim (pergunta 7). 0 perguntas,
    o tempo de publicar.
11. **Desinstalar limpo** (regra 9). Pelas Configurações do Windows, como o Kaique faria: a barra de progresso do
    Windows aparece; depois, a janela de prova lista que as tarefas, a pasta do ajudante e as sobras do Velopack
    saíram e que os projetos são os mesmos 44 arquivos. 1 pergunta, 5 min.
12. **Reinstalar** (regra 2). Instalar de novo e abrir: a pergunta do Windows volta e o ajudante nasce. 2 perguntas,
    10 min.
13. **A primeira abertura não congela** (regra 10). Durante a pergunta e a preparação, ele arrasta a janela e ela
    responde, com "Preparando o computador...". 1 pergunta, 3 min.
14. **O registro legível** (1.3). Uma linha com resposta do Windows aparece com "ÊXITO" certo na janela. 0 perguntas,
    1 min.

**Total:** umas 11 perguntas do Windows e perto de 2 horas, contando duas trocas reais. O teste grande depois só
confirma.

---

## 5. Perguntas para o Samuel

### Pergunta 1. A janelinha também no "Reiniciar agora"

**Do que se trata.** É o aviso "Chegou uma versão nova do Editor de Impressão", que aparece com o programa aberto
quando chega uma versão nova. Ele tem os botões "Reiniciar agora" e "Depois". Print do aviso, da etapa 5:
`saida_teste\etapa5\prints\fase4\1-aviso.png`.

**O que acontece hoje.** Com "Depois", na próxima abertura aparece a janelinha "Atualizando o programa, espere um
pouco..." até o programa abrir (você escolheu em 17/11). Com "Reiniciar agora", o programa fecha e **não aparece nada**
durante a troca. Medido na etapa 5, a troca leva de 7 a 23 minutos. O Kaique vai achar que o programa quebrou. É uma
falta no que foi pedido, não um defeito do Windows.

**O que você escolhe:**
- **Sim (sugestão):** a mesma janelinha aparece também depois do "Reiniciar agora", até o programa voltar. Nada mais
  muda.
- **Não:** fica como está, sem nada na tela durante a troca.
- **Só comentário.**

### Pergunta 2. Com "Depois", quando a versão nova entra

**Do que se trata.** É o botão "Depois" do mesmo aviso. Em 17/11 você escolheu "quando ele abrir o programa de novo",
com uma espera curta. A explicação de então falava em "alguns segundos, até 5 minutos".

**O que acontece hoje.** A espera medida na etapa 5 foi de **7 a 23 minutos**, e não alguns segundos. O Kaique clica no
atalho para trabalhar e fica esse tempo olhando a janelinha.

**O que você escolhe:**
- **Continua na próxima abertura:** como você decidiu, com a janelinha de 7 a 23 minutos (ou uns 7,5 se a versão vier
  inteira, pergunta 3 do estudo de publicar).
- **Na hora de fechar (sugestão):** quando o Kaique fecha o programa, a troca acontece sozinha, por trás. Na próxima
  vez ele já abre na versão nova, sem esperar. Se ele abrir no meio da troca, aparece a janelinha até acabar
  (pergunta 3). Se ele desligar o notebook no meio, nada se perde: a troca tenta de novo depois.
- **Só comentário.**

Você continua no controle: o "Reiniciar agora" continua trocando na hora.

### Pergunta 3. O Kaique abre o programa no meio da troca

**Do que se trata.** É o momento em que a versão nova está sendo trocada, com o programa fechado (7 a 23 minutos).

**O que acontece hoje.** Se o Kaique clicar no atalho nessa hora, o programa abre. Aí a ferramenta de atualização
fecha o programa à força para trocar os arquivos, e o programa ainda mostra "A atualização não deu certo", sem ter
dado errado. É um defeito, achado lendo o código (ainda não provado).

**O que você escolhe:**
- **Sim (sugestão):** nessa hora, em vez do programa, aparece a janelinha "Atualizando o programa, espere um pouco...",
  e o programa abre sozinho quando a troca acaba. É a mesma janelinha que você já escolheu.
- **Não:** fica como está.
- **Só comentário.**

### Pergunta 4. A frase do aviso de falha, para cada caso

**Do que se trata.** É o aviso que aparece na tela do Kaique quando a atualização não dá certo. Hoje é sempre a frase
que você escolheu em 16/11: "A atualização não deu certo. O programa voltou para a versão anterior e continua
funcionando. Avise o Samuel."

**O que acontece hoje.** Ela aparece em três casos diferentes, e em dois ela não é verdade:
- a versão chegou sem a sua assinatura e **nem foi instalada** (não "voltou", nunca saiu);
- a versão foi instalada, falhou, e **a volta não deu certo** (o programa não voltou).

**O que você escolhe:**
- **Três frases (sugestão):**
  - recusada: "Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do Samuel. O programa
    continua funcionando. Avise o Samuel.";
  - voltou: a frase de hoje;
  - não voltou: "A atualização não deu certo e o programa não conseguiu voltar sozinho. Não desinstale nada. Avise o
    Samuel."
- **Uma frase só:** a de hoje em todos os casos.
- **Quero outras palavras:** diga quais.
- **Só comentário.**

### Pergunta 5. O que o desinstalar tira

**Do que se trata.** É o desinstalar do programa (Configurações do Windows > Aplicativos). Em 16/11 você decidiu que o
computador fica como era antes de instalar e que os projetos ficam.

**O que acontece hoje.** Medido hoje no seu PC, depois do desinstalar da etapa 5, ficaram: as duas tarefas do
Windows que o programa criou; uma pasta interna do programa com 789 MB (a cópia para voltar de versão); e uma pastinha
de 5 MB da ferramenta de atualização na sua conta. É um defeito.

**O que você escolhe:**
- **Sim (sugestão):** o desinstalar tira tudo isso, e no fim deixa a lista do que tirou. Os projetos e as
  configurações do Kaique ficam, como sempre.
- **Só as tarefas:** as pastas internas ficam.
- **Só comentário.**

### Pergunta 6. A ferramenta de atualização tem dois defeitos já consertados numa versão mais nova

**Do que se trata.** É a ferramenta pronta que faz a atualização (a Velopack, que você escolheu em 16/11). Usamos a
versão 1.2.161, a última que já saiu como final.

**O que acontece hoje.** Os autores dela consertaram dois defeitos que nos atingem, mas o conserto só está numa versão
de teste (1.3.39):
- se a troca falhar num momento ruim, o programa pode ficar sem abrir, sem atualizar e sem desinstalar;
- o desinstalar deixa uma pasta para trás.

**O que você escolhe:**
- **Ficar na 1.2.161 e nos protegermos (sugestão):** o programa guarda a versão de hoje antes de trocar e volta sozinho
  se a troca estragar (regra 5 da seção 3). Nada muda para o Kaique.
- **Trocar pela versão de teste:** os consertos vêm prontos, mas é uma versão ainda em teste, e todas as provas de
  instalar e desinstalar têm de ser refeitas.
- **Esperar a versão final** e trocar quando ela sair.
- **Só comentário.**

### Pergunta 7. Duas licenças para as provas

**Do que se trata.** São as provas à vista que vêm antes de montar a versão (seção 4).

**O que acontece hoje.**
- Um teste antigo cobra justamente o jeito errado que fez o "Reiniciar agora" não voltar. Mudar teste antigo precisa
  do seu ok.
- Para provar o publicar no GitHub de verdade, é preciso pôr lá uma versão de teste. Como rascunho, ninguém vê e o
  programa do Kaique não enxerga.

**O que você escolhe:**
- **Sim para as duas (sugestão):** o teste antigo passa a cobrar o jeito certo, e a versão de teste vai ao GitHub como
  rascunho, sendo apagada no fim.
- **Só o teste.**
- **Nenhuma.**
- **Só comentário.**

### Pergunta 8. Uma opção do Windows no notebook do Kaique

**Do que se trata.** É uma proteção do Windows 11, o "Controle Inteligente de Aplicativos" (em Segurança do Windows >
Controle de aplicativos e navegador). Quando está ligada, ela bloqueia programas que não têm um certificado pago, e não
dá para liberar um programa só. O nosso não tem (você escolheu a assinatura grátis em 16/11).

**O que acontece hoje.** No seu PC ela está desligada (lido hoje). No notebook do Kaique não se sabe. Num Windows novo
ela começa "em avaliação" e pode ligar sozinha. Se estiver ligada, o programa não abre lá.

**O que você escolhe:**
- **Sim (sugestão):** antes de mandar o programa, o Kaique olha essa tela e diz o que aparece (pode ser por telefone).
  Se estiver ligada, você decide o que fazer antes de instalar.
- **Não:** instalar e ver.
- **Só comentário.**

---

## 6. Ressalvas

- Os defeitos marcados "lido" não foram provados. A seção 4 diz como provar cada um.
- O desvio de gravação na pasta do ajudante (novo 10) é um tipo de falha conhecido do Windows; não tentei fazê-lo.
- A prova de que o aviso "o produto foi removido" (regra 9) não aparece numa atualização por .msi novo ainda falta.
- A regra 5 (o socorro fora de `current`) precisa de um plano à parte antes de construir, porque muda o que o ajudante
  roda.
- Não li o código inteiro da parte dos testes à distância (é de outro agente), só o que o desinstalar e a pergunta do
  Windows usam.
- Os prints das perguntas são os da etapa 5. Os prints novos saem nas provas à vista da seção 4.
