# Quem tenta quebrar, volta 5: o atualizador novo

25/11/2026. Quinto agente que tenta quebrar (D-775): não escrevi este código e não o conserto. Ramo
`atualizador-novo-2026-11-23`, commit conferido `0d9cac4e` (o GitHub verde nele: rodada 45645041894, na repetição,
segundo a gerente). Nada do programa nem dos testes do ramo foi mudado. Tudo o que rodei está em `provas/`.

## Em uma frase

**A volta 5 cumpre o que o Samuel decidiu em 25/11, mas eu causei dois incidentes no PC dele enquanto testava.**
A volta automática saiu inteira. A versão reprovada mostra a caixa do Windows com "A versão nova não funcionou. Não
desinstale nada. Avise o Samuel." e depois o programa abre. As frases de antes da janela vão pela caixa. A frase
"outra janela" não aparece depois da troca certa. O atualizador que some tem a frase própria (rodei com a biblioteca do
Velopack de verdade, inclusive quando ele some no meio do pedido). Achei **0 graves, 2 médios e 1 leve**. O primeiro médio já
existia antes da volta 5: na segunda vez que o Windows não deixa trocar para a mesma versão, o Kaique não vê frase
nenhuma. O segundo: duas proteções que funcionam, mas sem teste que reclame se forem desligadas. Pela D-842, os três
vão ao Samuel decidir antes da prova à vista.

**Em destaque, os dois incidentes** (seção própria abaixo): às 14:17 uma caixa de prova minha apareceu na tela do
Samuel; às 14:27 a guarda que eu escrevi para evitar isso fechou à força o Explorador, o app do Claude e mais dois
programas dele.

## Os dois incidentes no PC do Samuel (culpa minha; lição para os próximos agentes)

### Primeiro: às 14:17, uma caixa de prova apareceu na tela dele

- **O que apareceu (às 14:17:37):** a caixa do próprio Windows, título "Atualização", com "Chegou uma versão nova, mas
  ela não foi instalada porque não tem a assinatura do Samuel. O programa continua funcionando. Avise o Samuel." e o
  botão OK. Alguém clicou OK às 14:17:41 (a minha prova não a via, então foi na tela dele). Era uma caixa de teste: o
  programa dele não teve nada com isso.
- **A causa:** a prova da caixa de verdade (`provas/prova_caixa.py`, o caso em que a frase chega por trás) rodava numa
  área de trabalho separada, mas a área separada vale **para cada linha de execução** do programa, uma por uma
  (`SetThreadDesktop`). O processo da prova entrou nela só pela linha principal. Nesse caso a caixa sai da linha de
  trás do atualizador, que é uma linha nova: ela nasceu na área de trabalho normal, a tela dele.
- **O conserto da prova:** o processo da prova passou a **nascer** dentro da área separada (`CreateProcessW` com
  `lpDesktop`), o que vale para todas as linhas dele; e, antes de tudo, ele confere que a linha principal e uma linha
  nova estão lá, e sai sem fazer nada se não estiverem. Com isso a rodada de 14:25 (os sete casos) ficou toda na área
  separada.

### Segundo: às 14:27, a guarda da prova fechou à força programas dele

- **O que foi fechado (às 14:27:05):** o Explorador do Windows (o Windows o reabriu sozinho às 14:27:18; a janela do
  Explorador aberta na pasta "para-o-fable-2026-11-23" fechou), **o app do Claude** (o Samuel confirmou que ele fechou
  às 14:27), a "Experiência de Entrada do Windows" (o Windows a reabriu às 14:27:30) e o ajudante do Narrador. Não sei a lista
  completa: a guarda só anotou as janelas visíveis, e todos os processos que ela juntou receberam a ordem de fechar.
- **De onde veio a guarda:** depois do primeiro incidente, a gerente pediu que, durante cada prova, um vigia na tela
  normal procurasse janelas dos processos da prova e, se aparecesse alguma, **parasse e fechasse tudo na hora**. A
  ordem de fechar veio desse pedido; o jeito de achar "os processos da prova" foi meu, e foi ele que errou.
- **A causa:** para achar os processos da prova, a guarda lia na lista do Windows quem abriu cada processo e juntava os
  "filhos". O Windows **reaproveita os números** de processos que já morreram. O número do processo da prova era o de um
  programa antigo, já morto, que tinha aberto o Explorador; então o Explorador e tudo o que ele abriu (o app do Claude
  entre eles) foram contados como da prova e fechados. Faltaram duas conferências: a hora em que cada processo nasceu e
  o caminho de cada programa. E fechar processo pelo número lido de uma lista nunca é seguro.
- **O que fiz depois (ordens da gerente):** apaguei a guarda e todo código meu que fecha processo
  (`rodar_escondido.py` apagado; a guarda e o "fechar o processo" tirados do `prova_caixa.py`, que agora se recusa a
  rodar). Nenhuma prova com caixa ou janela de verdade rodou depois disso: as mutações e os testes rodaram só com a
  caixa de mentira.

### O que não mudou nos dois

- O registro de verdade (`C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`) não mudou: 16110 bytes,
  gravado em 24/11 16:38, a mesma soma antes e depois.
- Nada escrito em `C:\ProgramData\EditorImpressao`, em `%LOCALAPPDATA%\EditorImpressao` nem na instalação dele.
- O ramo do atualizador não foi mexido.

### A regra para os próximos

- **Quem testa não fecha processo que não criou.** Se precisar terminar um, só pelo identificador que o próprio
  `subprocess.Popen` devolveu, ou por um grupo do Windows (Job Object) criado na mesma hora; nunca pelo número lido de
  uma lista do Windows.
- **Área de trabalho separada não basta entrar nela depois:** o processo tem de nascer nela, porque ela vale para cada
  linha de execução, e uma linha nova nasce na área de trabalho normal.
- **Na tela do Samuel não aparece nada de prova**, nem caixa nem janela, nem por um instante.


## Como classifiquei (D-842)

- **Grave:** o Kaique perde trabalho, o programa fica sem abrir, ou some uma frase que devia aparecer.
- **Médio:** o Kaique vê algo errado (frase errada ou que falta, clique sem resposta), ou o programa faz diferente do
  que foi decidido, ou uma proteção sem teste (D-827).
- **Leve:** só aparece no código ou no registro, ou num caso que o Kaique nunca encontra (a abertura sem tela à vista,
  que só acontece quando o programa é aberto de longe).

Cada achado diz **EXECUTADO** (rodei neste Windows) ou **LIDO** (só li o código).

## O que rodei de verdade neste Windows

| Prova (`provas/`) | De verdade | De mentira |
|---|---|---|
| `prova_caixa.py` (rodada uma vez às 14:25, já consertada; não roda mais) | a caixa do Windows (`MessageBoxW` pela peça), a regra, o executor, o disco, o fio por trás; tudo numa área de trabalho separada, com o processo nascendo nela | a borda que não é a caixa (Velopack, lista de processos), o teste rápido, a janela do programa (uma lista) |
| `prova_update_exe.py` (14:24) | a biblioteca do Velopack 1.2.161 (procurar, pendente, baixar e o pedido da troca, sempre sem o `Update.exe`, então ela recusa antes de abrir qualquer programa), a regra, o executor, o disco, a lista de processos | a caixa (anota o texto), o reabrir, o teste rápido |
| `prova_casos.py` (L1 a L6), no código de agora e numa cópia de `aba7b844` | a regra, o executor, o disco (bilhete, vistos, marcas, `ultima-boa`), as assinaturas | a borda (Windows e Velopack anotam; a caixa "clica OK") |
| `testes_mudados.py` | o `git` e o `ast`: cada teste antigo que saiu ou mudou de `aba7b844` para `0d9cac4e` | — |
| `mutacoes_qtq5.py` | as 22 mutações do escritor e 14 minhas, numa cópia `git archive`, os testes um arquivo por vez | — |
| os testes do ramo | 79 arquivos, um por vez, no ramo: 3504 passaram, 13 pulados, nenhum falhou (`testes-um-por-vez-resultado.txt`; de fora só o `test_windows_janela_de_prova.py`, ordem da gerente) | — |

Não rodei (e não rodo mais, ordem da gerente depois dos incidentes): nenhuma caixa nem janela de verdade além da
rodada de 14:25. A caixa na tela de verdade do Kaique (o tamanho, se vem para a frente) só a prova à vista mostra.

---

## Achados médios

### M1. Na segunda vez que o Windows não deixa trocar para a MESMA versão, nenhuma frase aparece

- **O que o Kaique veria.** A versão nova chegou e ele clica "Reiniciar agora". Um arquivo do programa está preso (um
  antivírus, um programa que segura o arquivo), e o atualizador do Velopack não consegue trocar: ele reabre a versão de
  antes. Na primeira vez aparece "A atualização não deu certo. O programa continua na versão de antes e funcionando.
  Avise o Samuel." e o aviso da versão nova volta. Ele clica "Reiniciar agora" de novo (outro dia, ou na hora), a
  janela fecha, a janelinha do Velopack aparece, o programa reabre e **nada diz que não deu**: só o aviso de novo. É um
  clique sem resposta.
- **EXECUTADO** (`provas/prova_casos.py`, caso L1; resultado em `prova_casos-resultado-0d9cac4e.txt`): duas aberturas
  reabertas pelo Velopack com `--conferir-a-versao-nova 7.0.0 7.0.1` na versão 7.0.0; a primeira mostrou a caixa com a
  frase; a segunda, nada.
- **Já existia antes da volta 5.** O mesmo caso na cópia de `aba7b844` (`prova_casos-resultado-aba7b844.txt`): a
  primeira mostra a frase (na janela, como era), a segunda, nada.
- **Como repetir:** `python -I provas/prova_casos.py <raiz do código> <pasta de trabalho>`; o L1. À mão: abrir duas
  vezes o executor com `atualizacao.ARG_CONFERIR_NOVA, "7.0.0", "7.0.1"` e `versao.VERSAO = "7.0.0"`, na mesma conta.
- **A causa (LIDO).** A frase da D-839 tem o nome `troca-<versão>` sem a hora (`fases._frase` → `id_da_falha`), e a
  tela mostra cada nome uma vez só por conta (`ler_vistos`). As frases guardadas no bilhete levam a hora no nome
  justamente para "a mesma frase de novo, noutro dia, aparece de novo" (`guardar_frase`); esta não. A tabela das
  falhas da volta 5 ("Trocar × Windows nega") diz que a frase aparece, sem "só na primeira vez".
- **Fere:** D-839 ("Troca recusada pelo Windows (arquivo preso): aparece esta frase"), D-845 ("nenhum clique fica sem
  resposta"), D-842.

### M2. Duas proteções sem teste (D-827)

Desligadas numa cópia (`mutacoes_qtq5.py`), nenhum dos 12 arquivos de teste do atualizador reclamou
(`mutacoes_qtq5-resultado.txt`). As duas funcionam hoje (conferido); falta o teste que acusa se alguém as desligar.
- **Q3: a peça que lê se há tela à vista** (`core/windows.py`, `area_de_trabalho_a_vista`, a bandeira `WSF_VISIBLE`).
  Trocada por "sempre há tela", nenhum teste reclama: o único teste dela lê o Windows deste PC, que tem tela, e por isso
  dá o mesmo resultado com e sem a proteção. Sem ela, o programa aberto de longe (sem tela) chamaria a caixa onde
  ninguém vê e ficaria parado para sempre esperando o OK. O escritor rodou esse caso de verdade uma vez (o caso C da
  prova dele), mas nada o repete. EXECUTADO (a mutação); LIDO (o efeito).
- **Q7: nenhuma frase guardada aparece na reabertura sem janela do "Sim" ao fechar** (`fases._frases_ao_abrir`, o
  `and not novo.sem_janela`). Tirada, nenhum teste reclama. Sem ela, uma frase guardada e ainda não vista apareceria
  numa caixa do Windows logo depois de o Kaique fechar o programa com "Sim" (o caso: duas janelas, a primeira com "Sim"
  guarda a frase da outra janela, a segunda com "Sim" e o Windows não deixa trocar). Fere a D-769 ("nada abre na tela"
  depois do "Sim"). A proteção irmã (a reprovada sem janela guarda em vez de mostrar, Q8) foi acusada. EXECUTADO (a
  mutação); LIDO (o efeito).
- **Como repetir:** `python -I provas/mutacoes_qtq5.py <cópia git archive de 0d9cac4e>`; as linhas Q3 e Q7.

## Achado leve

1. **Sem área de trabalho à vista, de duas frases na mesma abertura a primeira se perde** (EXECUTADO, L5). O programa
   aberto de longe (sem tela) e reaberto pelo Velopack com a troca recusada, e com uma frase guardada no bilhete: as duas
   não puderam aparecer; cada uma é guardada no bilhete antes da caixa, e a segunda apaga a primeira. A abertura
   seguinte com tela mostra só a segunda. O Kaique abre sempre com tela, por isso é leve; é parente da ressalva 6 do
   escritor (o notebook que desliga entre as duas caixas) e da D-850 (duas frases no bilhete), que o Samuel deixou para
   depois.

---

## Item 1: a tabela das falhas contra o código (D-862)

Li a tabela da volta 5 casinha por casinha contra `core/fases_da_atualizacao.py` e `atualizacao.py`. Rodei estas:

| Casinha | Executado? | Bate? |
|---|---|---|
| Procurar × `Update.exe` some; quando volta, o aviso | EXECUTADO (Velopack de verdade) | sim: sem ele, nada (a biblioteca recusa); de volta, o aviso, com internet e sem internet (o pacote esperando) |
| Conferir × assinatura recusada, antes da janela | EXECUTADO (caixa de verdade, FUNDO) | sim: a frase (2) na caixa do Windows, uma vez, e a janela não a recebe de novo |
| "Reiniciar agora" × `Update.exe` some antes do clique | EXECUTADO (Velopack de verdade) | sim: a frase da D-873, palavra por palavra; a janela não fecha; fechar não pergunta |
| "Reiniciar agora" × `Update.exe` some nos segundos do pedido | EXECUTADO (a biblioteca de verdade recusou o pedido) | sim: o motivo vem do disco; o programa reabre e mostra a frase da D-873 antes da janela; fechar não pergunta |
| "Sim" ao fechar × outra janela, e a troca certa depois | EXECUTADO (L6, pelo "Reiniciar agora" da abertura seguinte) | sim: na versão nova, nenhuma frase (o M1 do quarto consertado também por este caminho) |
| Trocar × Windows nega (arquivo preso) | EXECUTADO (L1) | **só na primeira vez**: o médio M1 |
| Testar × não passou; a abertura seguinte; a correção | EXECUTADO (L3; caixa de verdade, MATAR e ESPERA) | sim: a caixa, a reprovação antes dela, nada pedido ao Velopack, o programa abre depois do OK; a seguinte não testa nem mostra; a procura volta; a correção 9.9.1 é oferecida; na 9.9.1 a frase da 9.9.0 não aparece |
| Testar × não passou depois do "Sim" ao fechar | EXECUTADO (L4) | sim: nada na hora; na abertura seguinte a caixa uma vez; na outra, nada |
| Testar × desliga com a caixa na tela | EXECUTADO (caixa de verdade, MATAR) | sim: a abertura seguinte mostra a caixa de novo; depois do OK, nunca mais |
| Testar × a caixa não pode aparecer (sem tela) | EXECUTADO (L5, caixa de mentira que falha) | sim para uma frase; com duas, o leve 1 |
| Guardar × a marca `.sem-volta` velha de uma versão de prova | EXECUTADO (L2) | sim: ignorada; a última boa é lida certo; a abertura segue até o aviso |

As outras casinhas eu li e batem com o código. As frases, palavra por palavra, batem com o Livro (D-778 (2), D-839,
D-840, D-843, D-845 com os nove motivos e o da D-864, D-846, D-868, D-873).

## Item 2: a caixa do Windows

- **A documentação da Microsoft, lida por mim** (§11.12 item 6): `MessageBoxW` ("Return value": com só o OK, o ESC e o X
  devolvem `IDOK`; zero é falha, com `GetLastError`); "About Dialog Boxes" (a caixa é modal e trava só a linha que a
  chama, até ser fechada; sem dona, nenhuma outra janela é desativada); `MB_TOPMOST`, `MB_SETFOREGROUND`;
  "Interactive Services" e `USEROBJECTFLAGS` (`WSF_VISIBLE`). A leitura do escritor bate com a documentação, e o código
  segue a leitura.
- **EXECUTADO:** o X (WM_CLOSE) voltou como OK e a frase contou como vista; o OK que demora 6 s deixa a abertura
  parada esses 6 s (o programa só tenta abrir depois); morto com a caixa na tela, a frase volta na abertura seguinte;
  a frase que chega por trás (a assinatura recusada) aparece na caixa enquanto a janela abre, e a janela abre sem
  esperar o OK; ela não aparece duas vezes.
- **Uma só chamada (EXECUTADO, busca):** `MessageBoxW` só em `core/windows.py` no programa (fora dele, só testes e
  provas).
- **Toda frase de antes da janela passa por ela (LIDO):** `Atualizacao._para_a_tela` é o único lugar que escolhe; o
  `main.py` não mostra frase da atualização; `ui/aviso_de_atualizacao.py` só recebe depois de `ligar_na_janela`.
- **A frase guardada antes, vista só depois do OK (LIDO e EXECUTADO):** sim. Laço: não há (cada abertura mostra no
  máximo uma vez cada frase; a reprovada não é testada de novo). "Nunca": só quando a caixa não pode aparecer E outra
  frase chega na mesma abertura (leve 1), ou quando o bilhete não grava e não há tela.
- **Tela bloqueada e de longe (LIDO):** bloqueada, a caixa espera na área de trabalho dele; de longe (sem
  `WSF_VISIBLE`), a peça não chama a caixa e a frase fica guardada (o escritor rodou o caso C).

## Item 3: nada sobrou da volta

- **Busca (EXECUTADO):** nenhum `--voltando`, `sem-volta`, `MarcarSemVolta`, `VoltaPedida`, `Fase.VOLTANDO`,
  `_voltar` da atualização, `FRASE_DA_FALHA`/`_SEM_VOLTA`, `permitir_voltar` no programa.
- **A marca `.sem-volta` velha no disco (EXECUTADO, L2):** ignorada sem quebrar.
- **Os testes antigos (EXECUTADO, `testes_mudados-resultado.txt`):** todo teste que saiu ou mudou de `aba7b844` para
  `0d9cac4e` está na lista da D-836 da volta 5, com o porquê. Só o ajudante `morre` do `test_atualizador_volta3.py`
  saiu sem estar na lista (é função de apoio da volta, não teste).

## Item 4: a versão reprovada

- Não é testada de novo e não fica em laço (EXECUTADO, L3, MATAR).
- O "e para" da D-857: nesta abertura nada é pedido ao Velopack (EXECUTADO, L3: zero pedidos); nas seguintes a procura
  volta (EXECUTADO).
- **A reprovação depois do "Sim" ao fechar** (EXECUTADO, L4): na hora, nada (o programa já fechou, D-769: nada abre na
  tela depois do "Sim"); na próxima vez que o Kaique abrir o programa, a caixa do Windows antes de tudo, uma vez. Isso
  bate com a D-769 e com a D-868 (a frase vai pela caixa do Windows; a D-868 não diz "na hora"). O que o Kaique vê: ele
  fecha, responde "Sim", nada aparece; no dia seguinte, ao abrir, a caixa "A versão nova não funcionou. Não desinstale
  nada. Avise o Samuel.", OK, e o programa tenta abrir.
- Uma coisa que só li: na abertura da reprovação o motor do Kraken não é conferido (`GarantirMotor` não roda nela). Na
  abertura seguinte é. Não achei efeito para o Kaique.

## Item 5: o M1 e o M2 do quarto "quem tenta quebrar"

- **M1 (EXECUTADO):** troca certa depois do "Sim" com outra janela, pelo "Reiniciar agora" da abertura seguinte (L6):
  nenhuma frase; a errada (a troca não aconteceu): a frase aparece (L5, a abertura com tela).
- **M2 (EXECUTADO, a biblioteca de verdade):** a frase, palavra por palavra igual à D-873; a janela não fecha; fechar
  não pergunta nada; um segundo clique não faz nada (o aviso já fechou); quando o `Update.exe` volta, o aviso volta,
  com internet e sem internet. **Se ele some no meio do pedido:** a biblioteca recusa ("Update.exe does not exist in
  the expected path"), o motivo vem do disco (não do texto do erro), o programa reabre e mostra a frase própria antes
  da janela; fechar não pergunta.

## Item 6: proteções desligadas (D-811, D-827)

EXECUTADO (`provas/mutacoes_qtq5.py`, saída em `mutacoes_qtq5-resultado.txt`): numa cópia do commit feita com
`git archive` (o ramo nunca foi mexido), cada proteção desligada uma de cada vez, com os 12 arquivos de teste do
atualizador, um por vez, parando no primeiro que acusa. Só com a caixa de mentira (os testes trocam o Windows por um
de mentira). Sem mutação: nenhum teste falhou.
- **As 22 do escritor (V1 a V22): todas acusadas**, de novo, no código final.
- **As 14 minhas (Q1 a Q14): 12 acusadas** (a caixa que não olha os vistos; o OK que não grava o visto; a caixa chamada
  quando não deu para ler a estação; sem `MB_TOPMOST`; sem `MB_SETFOREGROUND`; a reprovada sem janela que mostraria a
  caixa; a frase guardada com outro nome; o motivo do pedido sempre "o atualizador sumiu"; a frase sem versão no nome
  escondida; a frase da troca valendo com a versão igual; a volta zero contada como vista; a frase da D-845 no lugar da
  própria no "Sim" ao fechar).
- **Sobreviveram 2: Q3 e Q7** (o médio M2).

## Item 7: o que já funcionava ao redor (§11.8)

EXECUTADO, um arquivo por vez, no ramo, com a pasta temporária no D: (`provas/testes-um-por-vez-resultado.txt`):
**79 arquivos** (os do atualizador, da peça do Windows, do porteiro, da trava, da assinatura e os **64
`tests/test_decisoes*.py`**): **3504 passaram, 13 pulados, nenhum falhou**. Do atualizador: `test_fases_da_atualizacao`
2255, `test_atualizador_novo` 31, `test_atualizador_volta2` 31, `test_atualizador_volta3` 32, `test_atualizador_volta4`
18, `test_atualizador_volta5` 21, `test_decisoes_atualizacao_volta5` 22, `test_decisoes_atualizacao` 38, `test_windows_peca`
68 (+3 pulados). Ficou de fora o `test_windows_janela_de_prova.py` (ordem da gerente: nada de janela; não é do
atualizador).

O que já estava escolhido e continua igual (LIDO no diff, e coberto pelos testes acima e pelas provas): a troca normal
(a conferência única, agora com o `Update.exe` primeiro); a assinatura (D-778 (2), a soma do pacote, D-848); a D-839
(a palavra igual; o médio M1 é de quando ela aparece, não do texto); os nove motivos e o da D-864; a pergunta ao fechar
(D-831, D-835); a guarda da última boa e a marca de aprovada (D-854, D-856; a marca `.sem-volta` velha ignorada, L2); o
pacote esperando (D-859, EXECUTADO com a biblioteca de verdade); o motor (D-833, D-843). A peça do Velopack perdeu só o
"aceitar versão mais velha", que só a procura lia (o escritor cita `manager.rs` 294; conferi que procurar, baixar e
trocar continuam iguais nas provas de verdade).

## Item 8: uma peça só (§11.12)

- **A caixa:** só `core.windows.mostrar_caixa_do_windows` chama `MessageBoxW`; só `Atualizacao._para_a_tela` escolhe
  onde a frase aparece; só `frase_da_falha` escolhe o texto (EXECUTADO, busca; LIDO).
- **O `Update.exe`:** só `tem_o_atualizador` olha; a conferência da troca e o pedido a chamam (LIDO).
- **O Velopack:** só `core/conversa_com_o_velopack.py` importa `velopack` (EXECUTADO, busca).
- **O espaço:** só `espaco_livre_basta` no atualizador (a `configuracoes.espaco_livre_mb` é a D-876, para depois).
- **Resultado dado como certo sem conferir:** não achei. A frase só conta como vista com o OK de verdade (`IDOK`); o
  motivo do pedido que falha vem do disco.
- **Uma observação, não remendo:** a mesma frase (2) ou a do motor aparece na caixa do Windows ou na caixa da janela,
  conforme a procura termine antes ou depois de a janela abrir. A escolha está num lugar só e o texto é o mesmo; muda
  só o desenho da caixa. Vai como pergunta (abaixo).

## Item 9: a pergunta do Fable

**Os defeitos estão de novo todos na mesma funcionalidade? Não.** O único que o Kaique veria (o médio M1) é da frase
da D-839, que existe desde a volta 4; os dois testes que faltam (o médio M2) são da parte nova, a caixa do Windows, mas
as duas proteções funcionam; o leve é um caso sem tela. A volta automática, onde estavam os defeitos das três rodadas
anteriores, saiu inteira, e não sobrou nada dela.
**O que o Kaique perde se ficar para depois:** pelo M1, num caso raro (um arquivo preso duas vezes na troca para a
mesma versão), o segundo "Reiniciar agora" não diz nada; o programa continua funcionando na versão de antes, e o aviso
volta. Pelo M2, nada hoje; o risco é uma mudança futura desligar a proteção sem que nenhum teste avise.

## O que precisa da palavra do Samuel (no jeito do §11.13)

Antes da prova à vista, cada achado precisa de "conserta agora" ou "deixo para depois" dele (D-842). São três
perguntas.

**1. A frase de quando o Windows não deixa trocar a versão, na segunda vez.**
- Do que se trata: é a caixa "Atualização" que aparece quando o Kaique clica "Reiniciar agora" no aviso da versão nova
  e o Windows não deixa trocar (um arquivo do programa preso). A frase é "A atualização não deu certo. O programa
  continua na versão de antes e funcionando. Avise o Samuel.", e o aviso da versão nova volta.
- O que acontece hoje: na primeira vez a frase aparece. Se ele clicar "Reiniciar agora" de novo e o Windows não deixar
  de novo, para a mesma versão, a janela fecha, o programa reabre e **nada diz que não deu**: só o aviso de novo. É
  **defeito do programa**, e já existia antes desta volta.
- O que você escolhe:
  - **A (sugestão): consertar agora.** A frase aparece toda vez que a troca não acontece, como já acontece com as frases
    guardadas para a abertura seguinte. É uma mudança pequena, num lugar só; nada do que já funciona muda.
  - **B: deixar para depois.** O caso é raro (o arquivo preso duas vezes na troca para a mesma versão), e o programa
    continua funcionando na versão de antes.
  - Só comentário também vale.

**2. Duas proteções sem teste automático.**
- Do que se trata: duas proteções do programa funcionam (conferido), mas, se alguém as desligar sem querer, nenhum
  teste reclama. Pela sua regra (cada proteção tem um teste que falha quando ela é desligada), isso é defeito.
  - a que **não mostra a caixa quando o programa é aberto sem tela à vista** (aberto de longe): sem ela, o programa
    ficaria parado para sempre esperando um OK que ninguém pode dar;
  - a que **não mostra caixa nenhuma depois do "Sim" ao fechar** (você decidiu que nada abre na tela depois do "Sim"):
    sem ela, uma frase guardada de antes apareceria numa caixa logo depois de o Kaique fechar o programa.
- O que você escolhe:
  - **A (sugestão): pôr os dois testes agora.** Só testes; o programa não muda.
  - **B: deixar para depois.**
  - Só comentário também vale.

**3. Duas frases na mesma abertura sem tela à vista: a primeira se perde.**
- Do que se trata: só quando o programa é aberto de longe (sem tela) e chegam duas frases ao mesmo tempo; a abertura
  seguinte, com tela, mostra só a segunda. O Kaique abre sempre com tela.
- O que você escolhe: **A (sugestão): deixar para depois**, junto com "duas janelas anotando o bilhete ao mesmo tempo",
  que você já deixou para depois. **B: consertar agora.** Só comentário também vale.

**Um ponto que não é defeito, para você saber (sem pergunta):** a frase "Chegou uma versão nova, mas ela não foi
instalada porque não tem a assinatura do Samuel..." e a do motor novo podem aparecer na caixa do Windows (quando a
procura termina antes de a janela abrir) ou na caixa da janela do programa (quando termina depois). As palavras e o
título são os mesmos; muda só o desenho da caixa. A sua decisão de 25/11 ("toda frase que pode aparecer antes da janela
existir usa esse caminho") foi lida pelo escritor como "a frase que aparece antes da janela vai pela caixa do Windows".
Se quiser que essas duas vão sempre pela caixa do Windows, é uma pergunta à parte.


## O que fiz fora das minhas pastas

- **Os dois incidentes** (seção própria acima): a caixa na tela dele às 14:17 e os programas dele fechados às 14:27.
- **Nada escrito** em `C:\ProgramData\EditorImpressao`, em `%LOCALAPPDATA%\EditorImpressao` nem na instalação dele:
  toda prova trocou o PROGRAMDATA e o LOCALAPPDATA dentro do Python e conferiu com `assert`. O
  `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log` não mudou: 16110 bytes, gravado em 24/11 16:38, a mesma
  soma (MD5 `37312391…`) antes e depois.
- **Objetos do Windows:** a área de trabalho de prova "EditorProvaQtq5", criada e fechada pelas provas (some sozinha).
- **Arquivos fora do projeto:** só a minha pasta de rascunho da sessão (scripts de edição, este rascunho). Nada
  instalado, nada no registro do Windows. Não apaguei nada fora do projeto.
- **Dentro do projeto:** `saida_teste\qtq5\` (cópias `git archive`, as pastas das provas; o git ignora) e esta pasta.

## A minha opinião, com as ressalvas

Este relatório está **PRONTO PARA CONFERIR**. Não é aprovação: só o Samuel marca.

A minha opinião: **a volta 5 está quase pronta para a prova à vista; faltam as três respostas do Samuel.** O que o
Samuel decidiu em 25/11 está construído e rodou de verdade: a volta automática saiu sem deixar resto; a caixa do
Windows aparece com as palavras dele, antes da janela, e só conta como vista com o OK; a versão reprovada não é testada
de novo e não fica em laço; o M1 e o M2 do quarto estão consertados na causa (rodei o `Update.exe` que some no meio do
pedido, com a biblioteca de verdade). Não achei remendo nem conta em dois lugares: a caixa, o lugar da frase, o texto
e o `Update.exe` têm cada um uma função só. Pela primeira vez em três rodadas os achados não estão na parte nova.

**Ressalvas minhas:**

1. **Os dois incidentes** (seção própria): causei uma caixa na tela do Samuel e fechei programas dele. Depois disso não
   rodei mais nada com caixa ou janela de verdade: as mutações e os testes foram só com a caixa de mentira.
2. A caixa de verdade rodou uma vez com o processo nascido na área separada (14:25), com o `python.exe` da `.venv`, não
   com o programa empacotado; o tamanho, a posição e se ela vem para a frente na tela do Kaique só a prova à vista mostra.
3. No caso MATAR (o programa morto com a caixa na tela), quem fechou foi a vigia da prova, pelo número do processo lido
   da janela da caixa; ela acertou o processo da prova, mas esse jeito é o que a regra nova proíbe, e o código foi tirado.
4. O `Update.exe` das provas é um arquivo de dois bytes; a troca de verdade nunca foi pedida com ele no lugar (a
   biblioteca só recusou o pedido sem ele). A troca com a janelinha do Velopack só a prova à vista mostra.
5. A minha primeira rodada da prova do `Update.exe` usou um pacote sem o manifesto que o Velopack exige, e o "pacote
   esperando" não apareceu; era defeito da prova. Refiz com o pacote certo e o aviso voltou.
6. O conjunto inteiro dos testes e o `teste_botoes.py` ficam com a rodada do GitHub (verde em `0d9cac4e`, segundo a
   gerente).
