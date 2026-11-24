# Quem tenta quebrar, volta 2: o atualizador novo

24/11/2026. Agente novo que tenta quebrar (D-775, D-815): não escrevi este código e não o conserto. Ramo
`atualizador-novo-2026-11-23`, último commit conferido `069d6dca` (diferença conferida: `7d1f633a..069d6dca`). Nada do
programa nem dos testes do ramo foi mudado. Nenhuma janela na tela, nenhuma pergunta do Windows, nada mudado em
`C:\Program Files` nem em tarefa do Windows. As provas rodaram em pastas minhas no D:; tudo em `provas/` é meu.

## Em uma frase

**NÃO ESTÁ PRONTO para a prova à vista.** Os consertos da volta 1 funcionam no que foi pedido (o do atalho no meio da
troca, rodei com o atualizador do Velopack de verdade), mas achei 1 grave e 9 médios, rodados neste Windows: o pior é
que, se o notebook desliga enquanto o programa volta sozinho de uma versão estragada, o Kaique fica na versão
estragada e a tela diz "O programa voltou para a versão anterior". Pela regra nova (D-842), cada item abaixo precisa
de "consertar" ou "deixo para depois" do Samuel antes da prova.

## Como classifiquei (D-842)

- **grave**: o Kaique fica com o programa errado ou sem ele, e a tela diz outra coisa.
- **médio**: o Kaique veria (frase errada, clique sem resposta, janela parada, atualização que nunca chega).
- **leve-que-só-aparece-no-código**: o Kaique nunca vê.

Em cada achado digo se **EXECUTEI** no Windows ou **só LI**, e se é **defeito provado** ou **risco não provado**.

## O que rodei de verdade neste Windows (resumo)

| Prova (pasta `provas/`) | O que é de verdade | O que é de mentira |
|---|---|---|
| `prova_velopack_start_e_espera.py` | o `Update.exe` do Velopack 1.2.161 (tirado, só lendo, do pacote 1.1.0 do Samuel), `start` e `apply --waitPid`, numa instalação minha portátil; a lista de processos | nada (o "programa" é um pythonw sem janela que pergunta) |
| `prova_g1_e_troca_interrompida.py` | o executor, a regra, o `estado.json`, a lista de processos, o `Update.exe` esperando | o Velopack da biblioteca (procurar) |
| `prova_volta_interrompida.py` | dois processos de verdade, o primeiro morto no meio da volta (`os._exit`, como desligar) | o teste rápido (falha de propósito), a fonte |
| `prova_reabrir_o_programa.py` | o executor, a regra, o `estado.json` preso por outro processo de verdade, outro "programa" de verdade aberto de dentro de `current\`, um pacote de verdade | o Velopack (trocar), o motor, o lançar de novo (anotado) |
| `prova_reiniciar_agora_na_tela.py` | a ponte da tela de verdade com uma janela Qt de verdade (fora da tela), um pacote de 460 MB, a lista de processos | as caixas (respondem sozinhas), o Velopack |
| `prova_estado_de_outra_conta.py` | o `icacls` de verdade numa pasta minha, imitando a licença do `C:\ProgramData` (lida com o `icacls`, só lendo) | o Velopack (procurar) |
| `prova_licenca_de_verdade.py` | a função única da licença (`icacls /grant ... /T`) numa pasta minha, com um arquivo preso e um atalho de pasta dentro | nada |
| `prova_laco_d841.py` | a ponte da tela e a regra | as caixas |
| `mutacoes_qtq2.py` + as duas listas de antes | 26 proteções minhas desligadas numa cópia do ramo, com todos os arquivos de teste do atualizador | — |
| os 18 arquivos de teste do atualizador, um por vez | — | — |

O tempo de conferir o pacote foi medido no pacote de verdade de 460 MB (`EditorImpressaoPrograma-1.1.0-full.nupkg`,
só lendo).

---

## Achado grave

### G1. A volta para a versão anterior, interrompida no meio, deixa o Kaique na versão estragada com a frase "voltou para a versão anterior"

- **O que o Kaique veria.** Ele fecha o programa, responde "Sim" ao "Atualizar agora?" e desliga o notebook (o mais
  comum no fim do dia). A versão nova entra, não passa no teste rápido e o programa começa a voltar sozinho para a de
  antes, sem nada na tela. Se o notebook desliga nesses minutos, no dia seguinte o programa abre **na versão que
  falhou**, e a caixa diz: "A atualização não deu certo. O programa voltou para a versão anterior e continua
  funcionando. Avise o Samuel." Não voltou, e nada tenta voltar de novo.
- **O que acontece, com arquivo:linha.** No teste rápido que falha, a regra manda, na mesma hora, anotar a falha e
  pedir a volta (`core/fases_da_atualizacao.py:645-648`). A anotação (`atualizacao.py:202-214`, `anotar_falha`, a única)
  grava "o programa fica na anterior" e **apaga a troca em andamento** (`estado.pop("tentando")`, linha 210) **antes**
  de a volta acontecer. A volta (`atualizacao.py:952-980`) busca a assinatura e o índice na internet e baixa o pacote
  da anterior inteiro: o Velopack já tinha apagado esse pacote quando baixou a versão nova (`manager.rs` 419-438 e
  478-481: todo `*.nupkg` velho de `packages\` sai), então são uns 460 MB, minutos. Só depois `trocar_para` anota a
  troca de volta. Se o processo morre nesse meio, o disco diz "falhou o teste, fica na anterior, nenhuma troca em
  andamento"; a abertura seguinte (`_ao_abrir`, linha 506) mostra a falha (1) e abre a janela normal, sem rodar o
  teste rápido de novo.
- **A causa.** A anotação da falha registra o desfecho ("fica na anterior") antes de ele acontecer, e apaga a única
  marca que faria a abertura seguinte conferir. É o "dar como feito o que não conferiu" (§11.12, ponto 2).
- **Prova: EXECUTADA.** `provas/prova_volta_interrompida.py` (saída em `-resultado.txt`): processo 1 (a reabertura
  sem janela da 1.2.0, teste rápido falhando) morre com código 9 no primeiro passo da volta; o `estado.json` fica com
  `falha: teste, fica 1.1.0` e sem `tentando`; o processo 2 (o atalho, a 1.2.0 abrindo) vai para a abertura normal
  (`fase motor`, teste rápido não roda) com a frase (1) para a tela. O registro diz "o programa fica na 1.1.0".
- **Fere:** D-718 ("volta sozinho para a versão anterior"); D-778 e D-839 (a frase (1) "fica só para quando a versão
  nova entrou, falhou e o programa voltou"); D-769 ("Se o notebook desligar no meio, nada se perde"); §11.12 ponto 2.
- **Defeito provado.** Raro: precisa de uma versão que falhe no teste rápido e de uma interrupção nos minutos da volta.

---

## Achados médios

### M1. A troca interrompida (o notebook desliga no meio) vira "a atualização não deu certo" e a versão nunca mais é tentada

- **O que o Kaique veria.** "Sim" ao fechar, desliga o notebook enquanto a janelinha do Velopack ainda abre o pacote.
  Na abertura seguinte: "A atualização não deu certo. O programa continua na versão de antes e funcionando. Avise o
  Samuel." E a versão nova nunca mais chega: só a próxima que o Samuel publicar.
- **O que acontece.** A anotação "tentando 1.1.0 para 1.2.0" fica no disco; o atualizador do Velopack já não roda; a
  regra conclui "a troca não aconteceu" e trata como uma versão estragada: falha "troca" e a 1.2.0 em "não tentar"
  (`core/fases_da_atualizacao.py:489-496`). O mesmo vale quando o Windows não deixou o Velopack trocar uma vez (um
  arquivo preso por segundos): a versão, que não tem nada de errado, fica proibida.
- **A causa.** A regra não separa "a versão nova é ruim" (não passou no teste) de "a troca não chegou a acontecer"
  (interrompida, ou recusada pelo Windows): as duas põem a versão em "não tentar".
- **Prova: EXECUTADA.** `provas/prova_g1_e_troca_interrompida.py`, parte 2: o `estado.json` passa a `nao_tentar:
  [1.2.0]` e `falha: troca`; a tela recebe a frase da D-839; na abertura seguinte, com a 1.2.0 publicada, o registro
  diz "a versão 1.2.0 já falhou antes; espero uma mais nova".
- **Fere:** D-769: "Se o notebook desligar no meio, nada se perde e a troca tenta de novo depois." A frase da D-839
  está certa para o arquivo preso; o "nunca tentar de novo" não foi decidido por ele.
- **Defeito provado** (a lógica). Quanto tempo dura a janela em que desligar estraga, no notebook: só a prova à vista.

### M2. "Reiniciar agora" deixa a janela parada enquanto confere o pacote (até uns 8 segundos)

- **O que o Kaique veria.** Clica "Reiniciar agora", o aviso some e a janela do programa fica parada, sem responder,
  antes de fechar. Passados 5 segundos sem responder, o Windows costuma escrever "Não está respondendo" no título.
- **O que acontece.** O conserto do M1 da volta 1 pôs a conferência da troca ANTES de fechar, e ela roda no fio da
  tela: o clique (`ui/aviso_de_atualizacao.py:70`) manda o evento, e o efeito `ConferirTroca` roda na hora
  (`atualizacao.py:770-771`), com a soma SHA256 do pacote inteiro (`atualizacao.py:893`, ~460 MB). Depois de fechar, a
  soma é feita de novo (`trocar_para`, linha 921).
- **Prova: EXECUTADA.** `provas/prova_reiniciar_agora_na_tela.py`, parte A: com a ponte da tela de verdade e um pacote
  de 460 MB já na memória, o relógio do Qt não bateu nenhuma vez entre o clique e o fechar (0,54 s parada). A mesma
  soma no pacote de verdade de 460 MB, com o disco frio: **8,06 s** (com o disco quente, 0,35 s).
- **Fere:** CLAUDE.md §3: "Interface nunca congela." Defeito novo, nascido do conserto (o medo do Samuel: um conserto
  cria um defeito ao lado).
- **Defeito provado** (a janela parada); o tempo no notebook do Kaique só a prova à vista mede.

### M3. "Reiniciar agora" que não pode trocar por outro motivo não responde nada

- **O que o Kaique veria.** Clica "Reiniciar agora" e nada acontece: o aviso some, o programa continua aberto, nenhuma
  frase. Só ao fechar vem "Atualizar agora?".
- **O que acontece.** Fora "outra janela aberta" (que ganhou a frase da D-840), todo outro "não pode agora" vai para a
  fase "Depois" sem nada na tela (`core/fases_da_atualizacao.py:604-607`): o pacote que sumiu (um antivírus que o põe
  de lado), o motor fora do lugar, o Windows que não deu a lista de processos. O implementador escolheu o silêncio
  (ONDE-PAREI, volta 2b: "nada aparece, como antes (§11.7)").
- **Prova: EXECUTADA.** `provas/prova_reiniciar_agora_na_tela.py`, parte B: o pacote posto de lado logo depois do
  clique; resultado: nenhuma caixa depois do aviso, a janela não fechou, fase "depois".
- **Fere:** D-842 ("um clique sem resposta" nunca é pequeno). Não é defeito do código contra uma decisão: é um clique
  sem resposta que o Samuel não decidiu. **Pergunta de desenho.**

### M4. Se o `estado.json` nasce de uma abertura com licença de administrador, a atualização para para sempre, calada, e o registro da gerente fica vazio

- **O que o Kaique veria.** Nada, nunca: a versão nova nunca chega e nenhuma frase diz por quê. E a gerente, lendo o
  registro de longe (D-719), também não vê nada: as linhas vão para o `erros.log` da conta do Kaique.
- **Como acontece de verdade.** Toda abertura grava o `estado.json` logo no começo (`estado_aceita_gravacao`,
  `atualizacao.py:239-242`, chamada em `abrir`, linha 1014) e escreve no registro. Se a abertura é feita com a licença
  de administrador (o "Iniciar" do fim do `.msi` aberto por janela com licença, prova nº 1 de 22/11; ou "Executar como
  administrador"), os dois arquivos nascem do grupo Administradores. A licença do `C:\ProgramData` (lida aqui com o
  `icacls`, só lendo) dá a Usuários só "ler" nos arquivos e "criar arquivo novo" na pasta: a conta comum não consegue
  substituir nem apagar o `estado.json` nem escrever no `atualizacao.log`. Daí em diante, toda abertura dá "o estado da
  atualização não aceita gravação: nenhuma versão é procurada" (`core/fases_da_atualizacao.py:544-548`). Prova de que
  esse arquivo existe de verdade: no PC do Samuel, o `estado.json.antes-do-experimento` (o `estado.json` do desenho
  antigo, renomeado) tem exatamente essa licença: Sistema e Administradores com controle total, Usuários só ler.
- **Por que a prova à vista no PC do Samuel não mostraria.** A conta dele tem controle total herdado em
  `C:\ProgramData\EditorImpressao` (lido com o `icacls`): para ele, gravar sempre dá certo.
- **Prova: EXECUTADA** (a licença imitada; a criação com licença de administrador eu não posso rodar):
  `provas/prova_estado_de_outra_conta.py`: 3 aberturas, 0 procuras, nada para a tela, o `atualizacao.log` sem nenhuma
  linha nova, o `erros.log` da conta com "Acesso negado" e "nenhuma versão é procurada" três vezes.
- **Fere:** D-732 ("faz quando o programa é aberto"), D-719 (o registro que a gerente lê), §11.12 ponto 3 (a lista das
  falhas: "sem licença" do lado do estado não foi pensada; a abertura com licença é o leve 11 da volta 1, deixado sem
  mexer).
- **Defeito provado** no que o programa faz com o arquivo assim; **risco** no "quanto acontece" (depende de alguém
  abrir o programa com licença de administrador uma vez).

### M5. O fechar-e-reabrir sem trocar tem um caminho que dava para conferir antes de fechar (e outro que deixa duas janelas)

Detalhe na seção "ReabrirOPrograma: os caminhos", abaixo. Em resumo, executado: com o `estado.json` preso por outro
processo (um antivírus lendo, outra conta lendo), o "Reiniciar agora" passa na conferência, a janela fecha, a anotação
da troca não grava e o programa é aberto de novo, sem trocar e sem frase. A conferência antes de fechar não pergunta se
o estado aceita a anotação, e a anotação só é feita depois de fechar. E se outra janela do programa abre nos segundos
do fechar, o programa reabre e o Kaique fica com **duas** janelas, sem a frase da D-840.

- **Fere:** volta 1, M1 (o conserto existia para isso não acontecer); §11.12 ponto 2. **Defeito provado** (o caminho
  do estado); o das duas janelas é corrida de segundos (provado, raro).

### M6. Uma versão que pede motor do Kraken novo nunca é anunciada, e nada diz por quê

- **O que o Kaique veria.** Nenhuma atualização chega, para sempre, a partir da primeira versão que o Samuel publicar
  com um motor novo.
- **O que acontece.** O anúncio pergunta se o motor que a versão nova pede está no lugar (`atualizacao.py:856-857`,
  conserto do M2 da volta 1), e ninguém põe um motor de versão diferente no lugar: `garantir_o_motor` só põe o motor
  do programa que roda (`atualizacao.py:576`), e baixar o motor pela internet "fica de fora" (plano, linha 53). O
  pacote já baixado fica em `packages\`, e a cada abertura tudo se repete, calado.
- **Prova:** só LIDA, mais o teste do ramo `test_m2_a_versao_nova_sem_o_motor_dela_nao_e_anunciada` (que passa:
  mostra que nada é anunciado; não mostra que é para sempre).
- **Fere:** D-790 pela metade ("ela só entra depois que o motor chegou inteiro": nada faz o motor chegar). Está no
  plano aprovado; o "para sempre, calado" eu não achei explicado a ele. **Risco**, só quando o motor mudar. Precisa de
  "deixo para depois" dele.

### M7. Contar "pelo nome" quando o caminho de um processo não dá para ler pode prender o programa ou mostrar a frase errada

- **O que o Kaique veria, se acontecer.** (a) Depois de uma troca interrompida, o programa não abre (sai calado) a cada
  clique no atalho, enquanto rodar no computador qualquer processo de nome `Update.exe` cujo caminho a conta dele não
  consegue ler. (b) "Feche a outra janela do programa e clique de novo." sem outra janela nenhuma, enquanto rodar um
  `tesseract.exe` ou um `vc_redist.x64.exe` de outro programa, de outra conta ou com licença.
- **O que acontece.** `atualizador_do_velopack_rodando` conta como "rodando" qualquer `Update.exe` sem caminho
  legível (`core/windows.py:1983`), em qualquer pasta; e `programas_rodando_de` conta como "de dentro" qualquer
  processo sem caminho legível cujo nome é o de um `.exe` da pasta (`core/windows.py:1959-1960`). É o lado seguro da
  conta ("nunca se dá como parado o que não deu para conferir"), mas o efeito na tela não foi pensado.
- **Prova: EXECUTADA em parte.** Neste PC, a conta do Samuel não consegue ler o caminho de 96 processos (serviços do
  Windows, antivírus, placa de vídeo); nenhum se chama `Update.exe`, `tesseract.exe` ou `vc_redist.x64.exe`. O
  efeito em si **não provado** (não criei processo assim).
- **Risco não provado**, improvável; fica para ele decidir.

### M8. O título da caixa da D-840 não foi decidido por ele

A caixa "Feche a outra janela do programa e clique de novo." sai com o título "Versão nova do programa"
(`ui/aviso_de_atualizacao.py:88`) e o botão "entendi". A frase é a dele (D-840); o título e o botão, não (ressalva 2 do
próprio implementador). Não é defeito: é texto na tela sem decisão (§11.7, D-842). **Só lido.**

### M9. Cinco proteções novas da volta 2 que nenhum teste acusa quando desligadas (D-827)

Desliguei cada uma numa cópia do ramo, rodando os 11 arquivos de teste do atualizador (1263 casos), não só o teste
escolhido (`provas/mutacoes_qtq2.py`, saída em `mutacoes_qtq2-resultado.txt`). **EXECUTADO.** Sobreviveram:

| Proteção desligada | Onde | O que ela protege |
|---|---|---|
| V3 o `Update.exe` cujo caminho não dá para ler conta como "rodando" | `core/windows.py:1983` | G1: nunca dar a troca como parada sem conferir |
| V9 "o programa foi aberto de novo" só quando o sinal de vida veio | `atualizacao.py:947` | §11.12 ponto 2: o registro que a gerente lê diz o que aconteceu |
| V10 o pacote sem o `motor-exigido.json` não é anunciado | `atualizacao.py:857` | D-833: sem saber o motor da versão nova, nada é anunciado |
| V11 o pacote sem o `motor-exigido.json` não é trocado | `atualizacao.py:900-901` | D-833: nada é trocado sem o motor dela |
| V13 o número do motor tem de ser número de verdade (nem texto, nem "verdadeiro") | `atualizacao.py:517` | a leitura única do `motor-exigido.json` |

- **O que o Kaique veria:** nada hoje; a proteção pode sumir numa mudança futura sem ninguém ver (foi o que a D-827
  nasceu para impedir).
- **Fere:** D-827 ("proteção sem teste nunca é 'baixo': volta para conserto na hora"), D-811 a D-813. As 32 do
  implementador e as 17 da volta 1 são todas acusadas; estas cinco são novas da volta 2 e ficaram de fora da lista
  dele.
- **Defeito** (falta de prova; as proteções existem no código).

---

## Achados leves (só aparecem no código)

1. **Os testes escrevem no registro de verdade do PC.** `tests/test_decisoes_testes_a_distancia.py`
   (`test_d721_primeira_vez_pede_a_senha_e_liga` e `test_d728_instalado_primeira_vez_pede_a_senha`) chamam a
   primeira abertura como "instalado" sem desviar o `PROGRAMDATA`, e a linha nova de `ui/testes_a_distancia_ui.py:163`
   escreve em `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`. **EXECUTADO:** esse registro, no PC do
   Samuel, já tem 16 linhas "primeira abertura: a senha dos testes à distância foi digitada..." (2 por rodada; duas
   delas da minha rodada das 10:32). O Kaique nunca vê; a gerente lê esse registro na prova à vista e pode se enganar.
2. **O laço da D-841 empilha chamadas.** Cada "Reiniciar agora" com a outra janela aberta abre a caixa seguinte por
   dentro da anterior (`_mostrar` → `evento` → `_fazer` → `_para_a_tela` → `_mostrar`). **EXECUTADO**
   (`provas/prova_laco_d841.py`): no clique 142 o Python para por profundidade, o erro é engolido e o aviso deixa de
   voltar. Ninguém clica 142 vezes; fica anotado.
3. **Uma exceção dentro da troca não reabre o programa.** Se `trocar_para` levantar algo fora do previsto (só o
   `OSError` da soma e o erro do Velopack são pegos), o `evento` engole (`atualizacao.py:737-741`), não há
   `TrocaPedida` e o "Reiniciar agora" fecha sem reabrir. Só lido; não achei como provocar.
4. **O `estado.json` é lido e regravado inteiro em toda abertura, sem tranca entre processos**
   (`estado_aceita_gravacao`). Dois processos ao mesmo tempo (o atalho e a reabertura sem janela do "Sim" ao fechar)
   podem desfazer a anotação um do outro. Só lido; risco não provado.

---

## ReabrirOPrograma: os caminhos

O efeito `ReabrirOPrograma` nasce num lugar só da regra: `TrocaPedida(certa=False)` na fase TROCANDO, quando a troca
é a do "Reiniciar agora" (`core/fases_da_atualizacao.py:632`; `trocando_com_janela` só fica verdade em
`JanelaFechou(True)`, linha 611). Isto é: a conferência antes de fechar disse "pode", a janela fechou, e
`trocar_para` (`atualizacao.py:914-933`) devolveu "não pedida". `trocar_para` devolve "não pedida" em três pontos:

| Caminho | Dava para conferir antes de fechar? | Rodei? O que vi |
|---|---|---|
| a segunda conferência acha o pacote sumido (antivírus, outra conta) | não: é corrida de segundos (o fechar grava o trabalho) | lido |
| a segunda conferência acha o pacote trocado (soma diferente) | não: corrida | **EXECUTADO (R4)**: reabre; a reabertura mostra a frase (2) "não tem a assinatura do Samuel" (certo pelo desenho) |
| a segunda conferência acha o motor fora do lugar | não: corrida | lido |
| a segunda conferência não consegue a lista de processos | não: falha passageira do Windows | lido |
| a segunda conferência acha outra janela do programa aberta | não: corrida (o Kaique abre o atalho enquanto fecha) | **EXECUTADO (R3)**: reabre com a outra janela ainda aberta: **duas janelas**, sem a frase da D-840 |
| a anotação da troca não grava (`anotar_tentativa`, linha 926) | **sim**: a conferência não pergunta se o estado aceita a anotação, e a anotação podia ser feita antes de fechar | **EXECUTADO (R2)**: o `estado.json` aberto por outro processo dá "Acesso negado" (WinError 5) na troca do arquivo; a janela fecha e o programa reabre sem trocar e sem frase |
| o Velopack não aceita o pedido (`velopack.trocar` levanta) | em parte: o Velopack só confere que o pacote está em `packages\` (o mesmo que a nossa conferência) e abre o `Update.exe`; "o `Update.exe` está lá" dava para conferir; o abrir, não | **EXECUTADO com o Velopack de mentira (R6)**: reabre |
| uma exceção fora do previsto dentro de `trocar_para` | — | lido: **não reabre** (leve 3) |

O que isso diz sobre "a conferência antes de fechar pega tudo?": pega tudo o que é do pacote, do motor e das janelas
no instante do clique. **Não pega o estado** (o único caminho que dava para conferir antes e não confere). Os outros
são corridas dos segundos do fechar, e cada um, quando acontece, é visível para o Kaique como "o programa fechou e
abriu de novo, na mesma versão". Quantas vezes isso acontece no notebook, só a prova à vista e o registro dirão (cada
vez fica a linha "a troca para a X não foi pedida (...)" seguida de "o programa foi aberto de novo"). Saída das quatro
rodadas: `provas/prova_reabrir_o_programa-resultado.txt`.

---

## A volta 1, achado por achado

| Achado da volta 1 | Situação | A prova |
|---|---|---|
| G1 abrir pelo atalho no meio da troca anota falha falsa | **consertado na causa** | EXECUTADO com o `Update.exe` de verdade esperando (`apply --waitPid`): a função nova viu "rodando" do começo ao fim da espera (13 amostras, 12 s) e "parado" depois; a abertura saiu sem janela e não anotou nada. O `Update.exe start` do atalho já tinha saído em menos de 60 ms nas 8 vezes, então ele não confunde a conta. **Ao lado:** a troca que parou de verdade continua virando falha que nunca é tentada de novo (M1 deste relatório). |
| M1 "Reiniciar agora" fecha antes de conferir e some | **consertado, com dois defeitos novos ao lado** | EXECUTADO: com outra janela aberta, a frase e o aviso de novo (D-840/D-841). Ao lado: a janela parada na conferência (M2), o clique sem resposta nos outros casos (M3), e o caminho do estado que fecha e reabre (M5). |
| M2 a volta confere o motor da versão que falhou | **consertado na causa; três proteções novas sem teste** | EXECUTADO (mutações): V12 acusada (o motor é o que o pacote da versão que entra pede); V10, V11 e V13 sobrevivem (M9). Ao lado: a versão com motor novo nunca é anunciada (M6), que já era do plano. |
| M3 nove proteções sem teste | **consertado** | EXECUTADO: as 17 mutações da volta 1, de novo, numa cópia do ramo: 0 de 17 sobreviveram (todas acusadas). |
| M4 o estado que não grava | **consertado no "não conferir"; a causa de o estado não gravar ficou** | EXECUTADO: sem gravar, nada é procurado (certo). Mas a origem real (a abertura com licença de administrador) deixa a atualização parada para sempre, calada (M4 deste relatório). |
| M5 a licença vale para todas as contas | **nada mudou** (continua `*S-1-5-32-545:(OI)(CI)M /T`) | lido; é pergunta de desenho guardada para o Samuel. Executei a licença de verdade numa pasta minha: o `/T` **não** passa por atalho de pasta (junção) de dentro para fora; o arquivo preso também recebe a licença. |
| leve 1 a frase da falha "troca" | **consertado** (D-839, palavra por palavra) | EXECUTADO: a frase que vai para a tela é a da D-839. |
| leve 2 a exceção da K03 mais larga | **consertado na causa** | EXECUTADO: a prova da volta 1 (`prova_porteiro_k03.py`) agora acusa os 5 casos. |
| leve 3 a família pelo número, sem a hora | **consertado** | mutação V17 acusada. |
| leve 4 "nenhum PowerShell" | **o texto foi corrigido; o PowerShell continua** | lido; a pergunta C do implementador (fica ou troca) espera a gerente e o Samuel. |
| leve 5 (= M3, Q5) | **consertado** | mutação Q5 da volta 1 acusada. |
| leve 6 afirmação sobre o registro velho | **corrigido no ONDE-PAREI** | lido. |
| leve 7 comentários que citavam o que saiu | **consertado** | lido: nenhum resto (`preparar_como_administrador`, marcas, janelinha, `atualizacao_computador_preparado`) no programa. |
| leve 8 corrida entre o aviso e o fechar | **não consertado** (risco) | lido. |
| leve 9 sem o "Sim", sem o motor | **não consertado** (é a D-749) | lido. |
| leve 10 falha que nunca passa, pergunta a cada abertura sem aviso | **não consertado** | lido. |
| leve 11 aberto como administrador conta como preparado | **não consertado**, e a consequência é maior do que parecia | EXECUTADO em parte: ver M4 deste relatório. |
| leve 12 segundos sem nada na tela depois da troca | **não consertado**, e na volta são minutos | lido: na volta, o pacote da anterior é baixado inteiro antes de qualquer janela (G1 deste relatório). |

Pela D-842, os leves 8 a 12 da volta 1 são todos visíveis para o Kaique; continuam sem a decisão dele.

---

## Conferido e certo (curto)

- **EXECUTADO:** os 18 arquivos de teste do atualizador, um por vez, todos passam (`test_fases_da_atualizacao` 1012,
  `test_atualizador_novo` 35, `test_atualizador_volta2` 32, `test_decisoes_atualizacao` 42,
  `test_decisoes_ajudante_da_atualizacao` 22, `test_decisoes_preparo_d749` 3, `test_decisoes_brasao` 20,
  `test_decisoes_desinstalar` 45, `test_decisoes_desinstalar_pasta` 6, `test_decisoes_testes_a_distancia` 13,
  `test_trava_windows` 42 + 3 pulados, `test_porteiro_licenca_que_acrescenta` 14, `test_windows_peca` 68 + 3 pulados,
  `test_windows_preparo_do_computador` 19 + 1 pulado (e 20 com a licença de verdade numa pasta de prova),
  `test_velopack_de_verdade` 3, `test_conferencias_pacote` 26, `test_conferencias_codigo` 122,
  `test_conferencias_excecoes` 14).
- **EXECUTADO:** as mutações. As 32 do implementador: 32 de 32 acusadas. As 17 da volta 1: 0 de 17 sobreviveram (todas acusadas). As minhas 26
  (as proteções novas da volta 2 e 2b: G1, M1, M2, M4, leve 2, leve 3, D-839, D-840, D-841, a ponte da tela):
  **5 de 26 sobreviveram** (M9).
- **EXECUTADO:** o conserto do G1 com o Velopack de verdade (acima); a licença de verdade (arquivo preso recebe; junção
  não é seguida; as licenças das minhas pastas voltaram ao normal); a K03 do porteiro (5 de 5); a D-841 volta à fase
  "pronta" com o aviso de novo, sem espera.
- **LIDO:** os textos palavra por palavra: D-715/D-835 (o aviso), D-835 (a pergunta ao fechar, "Sim"/"Não"), as três
  da D-778, a da D-839 e a da D-840. A ordem da primeira abertura (D-834) e o resto do que a volta 1 deu como certo
  continuam iguais. A leitura do Velopack do implementador confere com o clone da etiqueta `1.2.161` (commit
  `92d6a1c`): `start` sai logo depois de abrir o programa (`start_windows_impl.rs` 111-133), o `apply` espera até 60 s
  (`util_common.rs` 14-26) e reabre com os mesmos argumentos na falha (`apply.rs` 57-61); a raiz que grava faz o
  `Update.exe` da troca ser o da raiz (`locator.rs` 152-158), o que a função do G1 procura.
- **LIDO:** nenhuma sobra do desenho antigo viva (marcas, ajudante, janelinha nossa, espera de 30 s); o
  `estado.json.antes-do-experimento` não é lido por nada; o `ARG_PROCURAR` da tarefa velha só anota e sai.

## O que só a prova à vista pode mostrar

- A pergunta do Windows no meio da tela na primeira abertura (D-806, D-834).
- A janelinha do Velopack de verdade com `wait_exit_then_apply_updates`, e quanto tempo ela fica.
- Quanto tempo a janela fica parada no "Reiniciar agora" no disco do notebook (M2).
- A janela reaberta (ReabrirOPrograma) vindo para a frente ou ficando atrás das outras.
- Desligar no meio da troca e no meio da volta, no notebook (M1, G1): eu provei a lógica, não o desligar.
- O `.msi` aberto com e sem licença no notebook, e de quem ficam o `estado.json` e o `atualizacao.log` (M4).
- O atalho clicado durante a troca do "Sim" ao fechar: pela D-828 e a D-770 adiada, nada abre; o clique se perde.

## O que eu mudei fora das minhas pastas (para a gerente saber)

- Uma linha "teste" no registro de verdade `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`, às
  10:35:49, por engano meu (uma prova rodou antes de eu desviar o `PROGRAMDATA`). Não apaguei (fora do projeto).
- Duas linhas "primeira abertura: a senha..." no mesmo registro às 10:32:53, escritas pelo teste do ramo (leve 1)
  quando rodei os testes. Nas mutações, desviei o `PROGRAMDATA` para não escrever mais.
- O clone do Velopack (só lido) ficou na pasta de rascunho desta sessão, no `%TEMP%` da conta (`...\scratchpad/velopack-fonte`; o caminho inteiro vai na mensagem à gerente). Fora do projeto: não apaguei.

Não proponho conserto: a causa de cada achado está escrita acima.
