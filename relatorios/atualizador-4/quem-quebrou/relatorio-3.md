# Quem tentou quebrar: a volta 4 dos consertos do atualizador (relatório 3)

Verificador, 23/11/2026. É a conferência do atualizador, a peça que troca o programa pela versão nova no notebook do
Kaique. Conferi só a volta 4: os 3 defeitos que a prova à vista de 22/11 achou (o "Reiniciar agora" não trocava, a
pergunta do Windows piscava na barra, a segunda preparação dava "acesso negado").

Trabalho conferido: ramo `atualizador-4-consertos-2026-11-21`, ponta de código `aa1963b7`, mais o plano `00506da4` e os
commits `b756ddc2`, `3adea01f`, `586b483f`, `1e5ea67d`, `929195b4`, `5a1aa6b2`, `7ca2c55f`, `b3f6d99f`, `528afac0` e
`aa1963b7`. Eu não escrevi este código. Não abri janela na tela do Samuel, não pedi licença ao Windows e não mudei o
código do ramo. As provas foram feitas numa cópia minha (`.claude/worktrees/quebra-volta4`), tirada no fim.

## Veredito

**NÃO ESTÁ PRONTO.** A causa principal saiu: o script da troca não segura mais a pasta do programa, e isso está bem feito.
Mas achei **5 médios**, e pela regra "só grave e médio voltam" eles voltam ao escritor:

- dois buracos em que a troca ainda pode ser estragada por um clique no atalho, ou pela abertura do próprio programa no
  meio dela;
- duas proteções novas sem teste nenhum (desligadas, todos os testes continuam passando);
- a pasta segura feita por fora da peça única e conferida só depois de já ter gravado nela.

Nenhum é grave. Os consertos são pequenos e ficam nos mesmos lugares únicos que o escritor criou: nenhum pede para
refazer a volta.

Máquina ou olho: tudo aqui é **máquina** (leitura do código, testes no PC um arquivo por vez, 26 proteções desligadas uma
por vez na minha cópia, 3 demonstrações rodando de verdade no Windows, sem licença e sem janela). O que só o Windows de
verdade prova está na lista do fim.

## Os achados

### Médio 1. A troca sem o script confere "o programa está aberto?" antes de a marca existir (nasceu na volta 4)

- **Onde:** `atualizacao.py`, `procurar_e_preparar`. A pergunta "está aberto?" (linha 676) vem primeiro. Depois o estado
  vira "aplicando" (linha 681) e só então o pedido da troca (linha 684) chama `segurar_a_marca_da_troca` (linha 1307),
  que lança o vigia e espera a marca aparecer por até 10 s. Depois que a marca aparece, ninguém pergunta de novo.
- **O caso:** o Kaique fecha o programa durante o download e logo o abre de novo. Nesse meio tempo (o PowerShell do vigia
  nascendo como o sistema, de 1 a 10 s), a marca ainda não existe. O clique abre o programa normalmente, e o pedido de
  troca sai mesmo assim. O Velopack espera o ajudante sair, monta a versão nova e **fecha à força tudo o que roda da pasta
  do programa**: o programa do Kaique some no meio do uso. Nesse caminho ninguém o reabre, porque o vigia não reabre.
- **Prova (minha cópia):** `test_demo_a_troca_sem_o_script_confere_o_programa_antes_de_ter_a_marca`. O clique "no meio"
  não é segurado (`troca_em_andamento` = False), e mesmo com o programa já aberto o pedido de troca sai ("aplicando", 1
  troca pedida). O teste passa: o defeito existe.
- **Por que é médio:** o pedido da gerente (resposta 4) era a mesma proteção na troca sem o script. No caminho do script
  a ordem está certa (primeiro a marca, depois a pergunta). No caminho do vigia está ao contrário. O conserto natural
  fica no lugar único: perguntar "está aberto?" de novo **depois** de a marca estar segura, dentro do
  `GerenteComAMarcaDaTroca`. Antes da volta 4 a janela era maior: sem marca nenhuma, já existia.

### Médio 2. O script da troca para de esperar quando uma leitura do estado falha (já existia; a volta 4 deixou duas regras para a mesma leitura)

- **Onde:** `atualizacao.py`, `script_de_trocar_e_reabrir`, linha 1189. A linha `$fase = ''; $tipo = ''` zera a fase
  antes de cada leitura. Se a leitura falha, a fase fica vazia, e o teste `$fase -ne 'pendente' -and $fase -ne
  'aplicando'` sai do laço.
- **O caso:** a leitura falha no instante em que o ajudante troca o arquivo do estado pelo nome. O próprio escritor achou
  isso e consertou só no vigia (o teste dele diz: "o arquivo trocado no instante da leitura"). Quando o script da troca
  sai do laço: reabre o programa com o argumento "depois da troca", que a marca nunca segura; e solta a marca. O programa
  nasce de dentro da pasta no meio da troca, e o Velopack o fecha à força ou a troca falha ("A atualização não deu
  certo"). É exatamente o defeito 1 da prova.
- **Prova (de verdade, no Windows):** o laço tirado do script de verdade, com o estado "aplicando" e o arquivo sem
  deixar ler por 6 s, saiu em 1 s com a fase vazia (`SAIU fase=[] depois de 1 s`). Controle: o mesmo laço, sem travar o
  arquivo, esperou o estado mudar (`SAIU fase=[ok] depois de 6 s`).
- **Por que é médio:** é raro (a leitura precisa coincidir com uma das 2 ou 3 gravações da troca). Mas fica no caminho
  principal do "Reiniciar agora", e a regra "só muda a fase se leu" já está escrita em `_linha_de_ler_a_fase`. O script
  da troca só não a segue, porque zera antes. É a mesma leitura com dois comportamentos (§11.12).

### Médio 3. "Sem licença para abrir a marca" quer dizer "existe": proteção sem teste (nasceu na volta 4; D-827)

- **Onde:** `atualizacao.py`, `_linhas_da_marca_existe`, linha 1086: `catch { return $true }`.
- **Para que serve:** na troca sem o script, a marca é do sistema. O script "só de reabrir" roda na conta do Kaique e não
  tem licença para abri-la. Confirmei no Windows deste PC que o Windows avisa isso com um erro, e não com "não existe":
  uma marca sem licença para a conta faz a pergunta do PowerShell dar `UnauthorizedAccessException`. Sem esse `catch`,
  o script entenderia "a troca acabou" e reabriria o programa no meio dela.
- **Prova:** desliguei a proteção (`return $false` no `catch`) e os 55 testes do arquivo continuaram passando (M02).
- **Como testar sem licença:** uma marca criada pelo próprio teste com a lista de licenças vazia dá o mesmo erro. Testei
  isso no PC.

### Médio 4. A pergunta vai com a janela da frente como dona: proteção sem teste (nasceu na volta 4; D-827)

- **Onde:** `atualizacao.py`, `preparar_na_primeira_abertura`, linha 2111: `janela = dona`.
- **Para que serve:** quando um aviso do programa está na frente, a pergunta do Windows tem de ir com o aviso como dona.
  Com a janela principal como dona (ela fica atrás do aviso), a pergunta pode voltar a piscar na barra.
- **Prova:** troquei a linha por `pass` e os 55 testes continuaram passando (M08). Os testes da tela de mentira sempre
  devolvem a própria janela principal, então não veem a diferença.

### Médio 5. A pasta segura do desfazer é criada e gravada por fora da peça única, e conferida só depois (nasceu na volta 4)

- **Onde:** `core/testes_a_distancia.py`. `_comando_criar_a_pasta` (linhas 370 a 379) cria a pasta com `New-Item`. O
  mesmo texto está repetido em `_comando_anotar_o_antes` (linha 290). Depois o passo 2 grava o `desfazer.ps1` e cria a
  tarefa que o roda como o sistema. Só então `preparar_o_desfazer` (linhas 869 e 872) confere a pasta.
- **A peça única já tem isso:** `core.windows.criar_pasta_segura` cria, confere e, se não conferir, apaga.
  `gravar_na_pasta_segura` confere antes de gravar e lê de volta. A volta 4 usou a conferência da peça, mas não a criação
  nem a gravação (§11.12, ponto 1: uma peça só para cada conversa com o Windows ou com o disco).
- **O caso:** a pasta `C:\Program Files\EditorImpressaoAjudante` já existe com outras licenças, ou é um atalho para outro
  lugar (só um administrador consegue fazer isso, então é raro). O script que roda como o sistema é gravado nela, a
  tarefa passa a apontar para ele e fica. A preparação diz "falhou", e a pergunta do Windows volta em toda abertura, sem
  nunca dar certo.
- **O que o formulário afirma e o código não faz:** "A pasta segura existe mas não confere: [...] não grava nada nela".
  Grava. Isso é o ponto 2 da §11.12: o formulário dá como feito o que não foi conferido.

### Baixos (para a lista do depois)

1. **A volta para a versão anterior não passa pelo pedido único de troca** (já existia). `_aplicar_pacote_quando_sair`
   (linha 779) chama o `Update.exe` direto. A marca só a cobre por 60 s fixos (`ESPERA_DA_VOLTA_S`), e a volta primeiro
   baixa a versão anterior inteira (~460 MB). Com internet lenta, a marca acaba antes de a volta começar. O comentário
   "É o único jeito de o programa pedir uma troca ao Velopack" (linhas 558 e 559) e a lista "caminho → função" estão
   errados e precisam ser corrigidos. O caminho só acontece se a versão nova falhar no teste rápido.
2. **A leitura do PowerShell cita o documento ao contrário.** O documento do `Start-Process` 5.1 diz: "The default is
   the location of the executable file or document being started". O formulário cita esse documento para "abre na
   localização atual do PowerShell", que é o que o experimento 3 mediu. O código funciona dos dois jeitos (o
   `Set-Location` vai para a pasta do próprio programa). Só a citação precisa dizer que o documento e o Windows
   divergem.
3. **"Alguém já vai reabrir?" em Python não tem teste** (M25 sobreviveu). Não faz mal: o script "só de reabrir" confere
   de novo e não reabre. A conferência usa `_marca_existe`, a cópia antiga que o escritor já anotou como bug.
4. **Duas leituras de marca no mesmo arquivo** (`_marca_existe` antiga e `core.windows.marca_existe`). Já existia e já
   está anotada pelo escritor.
5. **No meio da troca, o clique no atalho fica sem resposta.** No caso normal, de 1 a 3 minutos. No pior caso, até ~16
   min: o estado preso em "aplicando" e o vigia esperando o limite. É escolha (nenhuma frase nova sem o "sim" do
   Samuel; a janelinha fica para depois), e o escritor já pôs como ressalva. Entra na prova à vista.
6. **O "ligar" das Configurações cria a pasta segura sem conferi-la** (fora desta entrega, ressalva do escritor). A
   conferência antiga, o mesmo `icacls` no ligar e na preparação, saiu do ligar sem nada no lugar. Foi listado, como a
   D-827 pede, mas o ligar ficou sem nenhuma conferência.

## O que está certo (conferido)

- **A causa do defeito 1** (o PowerShell da troca nascendo com a pasta do programa como pasta de trabalho) saiu na peça
  única (`core/windows._lancar_solto`, `cwd=` a pasta do sistema). Vale para todo processo lançado solto, não só para
  este. Confere com o Velopack 1.2.161 que eu li: `force_stop_package` fecha só o que roda de dentro da pasta do
  programa, e o PowerShell mora no System32. A pasta é renomeada com 10 tentativas, uma por segundo, com a frase "one or
  more running processes prevented it".
- **"O programa terminou de fechar?"** passou a ser lido no Windows (`programas_rodando_de`), num lugar só, usado só pelo
  ajudante. Os servidores de páginas e o brasão saem junto com o programa, então a espera de 30 s basta. O programa
  empacotado é "em pasta", um processo por programa, então o próprio ajudante não se conta.
- **A pergunta do Windows** espera num fio solto (daemon), que não segura o programa ao fechar. A janela minimizada não é
  desminimizada. A janela fechada não recebe pergunta.
- **A pasta segura:** as licenças de Arquivos de Programas deste PC (lidas só para ver, com `icacls`) são as que o
  formulário diz. Refazer a preparação regrava o `desfazer.ps1` (o teste do escritor faz isso de verdade).
- **Os 3 testes autorizados pelo Samuel em 23/11** ("ok"): mudou só uma linha, mais duas de comentário, no Windows de
  mentira de `tests/test_atualizador_4.py`. Nenhuma conferência mudou, nenhum código do programa mudou. Depois do
  `528afac0`, só esse arquivo e o formulário mudaram. No PC: 57 de 57. No GitHub: rodada 45238891880, que testou
  `aa1963b7`, success na 2ª tentativa (a 1ª caiu no teste instável já conhecido da gravura). A rodada 45065432536, que
  testou `b3f6d99f`, só falhou nesses 3.
- **Os testes que a regra de 18/11 nomeou** (`tests/test_decisoes_desinstalar.py`): mudaram só os 3 nomeados. A lista
  de exceções do porteiro só perdeu os 4 itens do `icacls`, e nenhum entrou.
- **Nenhuma frase nova na tela:** os textos novos vão só ao registro.

## As decisões, uma por uma

| Decisão (palavras do Samuel) | Situação |
|---|---|
| D-828 (1) "foi eu, pode consertar essas coisas": o "Reiniciar agora" troca, também com o atalho clicado no meio | **Pela metade.** A causa saiu. Ficam os médios 1, 2 e 3. |
| D-828 (2) a pergunta no meio da tela | **Feita no código, pela metade nas provas** (médio 4). Só a prova à vista confirma. |
| D-828 (3) refazer a preparação dá certo | **Feita** (sem tranca, provado numa pasta do teste), mas fora da peça única (médio 5). |
| D-828: nenhuma frase nova sem o "sim" dele | **Cumprida.** |
| D-806 "no mesmo instante do clique [...] enquanto a janela do programa ainda está na frente" | Leitura da gerente: ver abaixo. |
| D-824 "uma coisa de cade vez" | **Cumprida** (um conserto por commit). |
| D-827 proteção sem teste volta na hora | **Não cumprida** em 2 proteções (médios 3 e 4). |
| D-811 cada proteção com o teste que a acusa | 23 de 26 acusadas; das 3 que sobreviveram, 2 são proteções (médios 3 e 4) e 1 é uma conferência repetida (baixo 3). |
| D-812 dado do próprio conferido não vale | Os testes principais cobram o comportamento (código de saída, script lançado, marca de verdade). O registro entra só como prova extra. |
| D-813 todos os jeitos que a peça de fora aceita | Velopack, CreateProcess, mutex e janela da frente batem com a documentação. A citação do `Start-Process` está trocada (baixo 2). |
| D-767 só conta rodando de verdade | O que eu não pude provar está na lista do fim. |
| D-829 os 3 testes só no Windows de mentira | **Cumprida**: nada mais mudou. |
| §11.8 o novo não estraga o que já funcionava | Os arquivos dos testes de antes passam (no GitHub, todos; no PC, `test_atualizador_4.py` 57). |
| §11.12 sem gambiarra, uma peça só | **Pela metade:** a pasta segura por fora da peça (médio 5); a mesma leitura do estado com duas regras (médio 2). |

**A espera sem limite pela janela na frente (leitura da gerente da D-806, não palavra do Samuel).** O risco de **nunca
perguntar** é pequeno. Ele só acontece se o Kaique não voltar à janela do programa durante aquela abertura, e a próxima
abertura pergunta de novo. Procurei no código algo que recriasse a janela principal (o que faria o programa achar que
ela fechou) e não achei. Os riscos de verdade são três:

- a pergunta pode aparecer **minutos depois**, num momento que o Kaique não espera (quando ele volta ao programa). Isso
  já não é "no mesmo instante do clique";
- a tentativa de trazer a janela para a frente, quando o Windows recusa, faz o **botão do programa piscar uma vez** na
  barra. O Samuel reclamou justamente de piscar;
- uma janela do programa aberta sem dona (por exemplo, o aviso de erro inesperado) segura a pergunta até ser fechada.

Quem decide se isso é o que ele quis é o Samuel, na prova à vista.

## As mutações (proteção desligada → teste que acusou)

Na minha cópia, uma por vez, rodando `tests/test_atualizador_volta4.py` inteiro (55 testes). Na primeira rodada, as
mutações M02 a M10 deram erro de preparação dos testes (a pasta temporária ficou presa por um processo da M01). Refiz
essas com uma pasta temporária nova para cada uma, e os resultados abaixo são os da segunda rodada. A M16 também foi
refeita: a primeira versão dela não mudava nada.

| # | Proteção desligada | Resultado |
|---|---|---|
| M01 | o lançado solto nasce na pasta do sistema | acusada (`..._nao_prende_a_pasta_de_trabalho_de_quem_lancou`) |
| M02 | "sem licença para abrir a marca" = existe (script só de reabrir) | **sobreviveu** (médio 3) |
| M03 | o "só de reabrir" só reabre se criou a marca de reabrir | acusada (`test_d827_dois_cliques_no_meio_da_troca_so_um_reabre`) |
| M04 | o próprio ajudante não conta | acusada (`test_conserto1_o_proprio_ajudante_nao_conta`) |
| M05 | o processo sem caminho conta pelo nome | acusada (`test_d827_o_processo_que_nao_deixa_ler_o_caminho_...`) |
| M06 | a lista cortada é "não sei" | acusada (`test_d827_a_lista_que_o_windows_nao_deu_inteira_e_nao_sei[cortada]`) |
| M07 | o executor confere que a pasta conferida é a do desfazer | acusada (`test_conserto3_o_executor_de_verdade_le_a_pasta_segura[...Outra\Pasta...]`) |
| M08 | a dona da pergunta é a janela da frente (o aviso) | **sobreviveu** (médio 4) |
| M09 | o aviso do programa na frente conta | acusada (`test_d827_a_leitura_da_frente_reconhece_o_aviso_...`) |
| M10 | a janela minimizada não conta como na frente | acusada (o mesmo teste) |
| M11 | não traz a janela minimizada | acusada (`test_conserto2_a_janela_minimizada_...`) |
| M12 | sem a marca, a versão volta a "pendente" | acusada (`test_conserto1_sem_a_marca_segura_o_velopack_nem_e_chamado_...`) |
| M13 | o pedido de troca só com a marca | acusada (o mesmo teste) |
| M14 | `criar_gerente` devolve o gerente com a proteção | acusada (`test_conserto1_o_gerente_do_programa_e_sempre_...`) |
| M15 | o vigia só conta como seguro depois de ler a marca | acusada (`test_conserto1_segurar_a_marca_usa_a_do_script_...`) |
| M16 | a marca que não deu para ler não segura a abertura | acusada (`..._nao_deu_para_ler_nao_segura_a_abertura[None]`) |
| M17 | o vigia espera a volta para a anterior | acusada (`test_d827_o_vigia_segura_a_marca_durante_a_volta_...`) |
| M18 | o programa reaberto nasce na pasta dele | acusada (`test_conserto1_o_programa_reaberto_pela_troca_nasce_...`) |
| M19 | a lista que não deu para ler conta como aberto | acusada (`..._lista_que_nao_deu_para_ler_...[None]`) |
| M21 | a preparação confere a pasta | acusada (`test_conserto3_a_preparacao_so_da_certo_com_a_pasta_conferida[False]`) |
| M22 | a gravação do estado tenta de novo | acusada (`test_d827_a_gravacao_do_estado_espera_...`) |
| M23 | a leitura do estado com o `-ErrorAction Stop` | acusada (`test_d827_o_vigia_nao_solta_a_marca_por_um_estado_...`) |
| M24 | o reaberto pela troca não sai pela marca | acusada (`..._os_ganchos_e_os_modos_escondidos_nao_saem[--depois-da-troca]`) |
| M25 | "alguém já vai reabrir?" em Python | **sobreviveu** (baixo 3: o script confere de novo) |
| M27 | a pasta do desfazer é a pasta segura | acusada (`test_conserto3_nenhum_comando_de_licenca_a_mao_...`) |
| M28 | o script da troca segura a marca da troca | acusada (`test_conserto1_o_script_da_troca_segura_as_duas_marcas_...`) |

Os médios 1, 2 e 5 não são proteção desligada, e sim proteção que falta. Nenhuma mutação os pega. Eles foram mostrados
pelas demonstrações descritas acima.

## O que a prova à vista nº 2 precisa conferir

Só o Windows de verdade prova isto (D-767). Tudo na conta comum do Kaique (ou numa conta comum), com o .msi aberto com
dois cliques, sem licença.

1. **"Reiniciar agora"**: a versão nova abre sozinha. No registro do Velopack como o sistema, nenhum "erro 32" e nenhum
   "running processes prevented it".
2. **Clique no atalho no meio dessa troca** (uma, duas, três vezes): nada abre na hora, a troca termina e o programa abre
   **uma vez só** no fim.
3. **"Depois" e abrir de novo**: a janelinha aparece, a troca acontece e o programa abre na versão nova.
4. **A troca sem o script** (fechar o programa enquanto a versão nova baixa):
   - o vigia nasce como o sistema e a troca acontece;
   - um clique no atalho no meio não abre nada e o programa abre no fim (o "só de reabrir" lendo uma marca do sistema
     que ele não tem licença para abrir; médio 3);
   - abrir de novo **logo depois de fechar** (médio 1): se ainda não estiver consertado, espera-se o programa fechar
     sozinho no meio do uso.
5. **A marca criada pela conta comum** (o script da troca) com a conta do Kaique, não com a do Samuel.
6. **A pergunta do Windows:**
   - (a) abrir e ficar na janela: a pergunta vem no meio da tela, na hora;
   - (b) clicar noutra janela durante o carregamento: a pergunta não pisca. Anotar se o botão do programa pisca uma vez.
     Ao voltar ao programa, a pergunta aparece no meio;
   - (c) minimizar durante o carregamento: nada até restaurar, e a janela não se desminimiza sozinha;
   - (d) com um aviso do programa na frente: a pergunta no meio (médio 4);
   - (e) fechar sem voltar: nada é perguntado, e a próxima abertura pergunta.
7. **Refazer a preparação.** No PC do Samuel as duas tarefas já existem (da prova nº 1) e a tarefa "desfazer" aponta
   para a pasta antiga do ProgramData, possivelmente trancada outra vez. Do jeito que está, a pergunta não volta, e o
   conserto 3 não aparece. Para provar:
   - começar sem as tarefas;
   - preparar com "Sim";
   - tirar uma tarefa e preparar de novo com "Sim";
   - as duas vezes têm de dar certo, sem "acesso negado";
   - `C:\Program Files\EditorImpressaoAjudante` nasce com as licenças de fábrica (ler com `icacls`, só leitura);
   - a pasta antiga não atrapalha.
8. **A pasta segura criada como administrador** pelo `New-Item` (não pela peça): o dono são os Administradores e as
   contas comuns só leem.
9. O motor do Kraken depois da troca (`EditorImpressao.exe --conferir-ocr`).
10. Desinstalar: a tarefa "desfazer" roda o script da pasta nova.

## Ressalvas

- Não rodei o programa instalado, não pedi licença e não abri janela (pedido da gerente). A troca inteira, a pergunta no
  meio da tela e a pasta criada como administrador só se provam à vista.
- No PC rodei, um arquivo por vez: `tests/test_atualizador_volta4.py` (55, sem mudança; e 26 vezes com uma proteção
  desligada) e `tests/test_atualizador_4.py` (57). O conjunto inteiro é a rodada 45238891880 do GitHub.
- Não rodei `tests/test_decisoes_desinstalar.py` no PC. As três mutações que deviam rodá-lo (M07, M21, M27) já foram
  acusadas no primeiro arquivo, e ele passa no GitHub.
- O médio 2 depende de um instante raro. A minha demonstração trava o arquivo por 6 s, o que é muito mais do que o
  instante real. Ela prova o que o script faz quando a leitura falha, não quantas vezes isso acontece.
- As demonstrações e as mutações ficaram na minha cópia, que foi removida no fim. O código delas está descrito acima.
  Para refazer: uma cópia nova de `aa1963b7` e o mesmo arquivo de testes.
