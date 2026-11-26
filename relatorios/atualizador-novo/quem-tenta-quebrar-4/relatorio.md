# Quem tenta quebrar, volta 4: o atualizador novo

24/11/2026. Quarto agente que tenta quebrar (D-775, D-862): não escrevi este código e não o conserto. Ramo
`atualizador-novo-2026-11-23`, commit `5dfcdc9d` (o GitHub estava verde exatamente nesse commit, rodada 45520421089:
conferido no registro da rodada, "TESTADO_SHA: 5dfcdc9d..."). Nada do programa nem dos testes do ramo foi mudado.
Nenhuma janela na tela do Samuel, nenhuma pergunta do Windows, nada instalado, nada escrito em `C:\ProgramData\EditorImpressao`,
em `%LOCALAPPDATA%\EditorImpressao` nem na instalação dele: em toda prova o PROGRAMDATA e o LOCALAPPDATA foram trocados
DENTRO do Python e conferidos com `assert` antes de rodar. Tudo o que rodei está em `provas/` (o script e a saída de cada
um).

## Em uma frase

**NÃO ESTÁ PRONTO para a prova à vista.** As três regras do Samuel funcionam no caminho para que foram feitas: a volta
recusada pelo Windows não vira mais laço, a versão aprovada não é testada de novo, a primeira versão do instalador não
baixa nada, sem internet o pacote que já chegou é oferecido (rodei com a biblioteca do Velopack de verdade), e todas as
frases batem com o Livro, palavra por palavra. Mas achei **1 grave e 6 médios**. O grave: quando a versão nova está
tão estragada que a janela dela não abre (é justamente o que o teste rápido reprova), a frase (3) "não desinstale nada,
avise o Samuel" nunca aparece; o Kaique só vê "Aconteceu um problema inesperado, mas o programa continua funcionando." e
o programa some; e, pela marca de "sem volta", nenhuma abertura seguinte tenta voltar. Pela D-862 ("Se achar médio,
para e avisa"), **tudo para aqui** e o Samuel é avisado.

## Como classifiquei (D-842)

- **grave**: o Kaique fica sem o programa, ou com o programa errado, e a tela não diz o que aconteceu.
- **médio**: o Kaique veria (frase errada ou que falta, frase que promete o que não acontece, clique sem resposta,
  segundos sem nada na tela, versão estragada sem volta), uma decisão do Livro que o código não cumpre, ou uma proteção
  sem teste (D-827).
- **leve**: só aparece lendo o código ou o registro; o Kaique nunca veria.

Cada achado diz **EXECUTADO** (rodei neste Windows) ou **LIDO** (só li o código), e o que é de mentira em cada prova.

## O que rodei de verdade neste Windows

| Prova (`provas/`) | De verdade | De mentira |
|---|---|---|
| `prova_janela_que_nao_abre.py` | o `main.py` de verdade (o `main()` inteiro, com o Qt fora da tela), o executor, a regra, o disco (marcas, bilhete, "vistos"), a caixa "Aconteceu um problema inesperado" do próprio main.py | a janela principal quebrada (o import dela falha, como numa versão que perdeu uma peça); as peças do Windows e do Velopack (só anotam); o teste rápido (falha) |
| `prova_frase_velha.py` | a regra, o executor, o disco, as assinaturas (chave de prova) e a **lista de processos do Windows**, com a "outra janela" sendo um processo de verdade aberto de dentro de `current\` (uma cópia do ping.exe, sem janela) | o pedido ao Velopack (só anotado), o teste rápido |
| `prova_update_exe_some.py` | a **biblioteca do Velopack 1.2.161 de verdade** (o `UpdateManager` numa instalação de prova minha), a peça `conversa_com_o_velopack` (procurar, pendente, baixar, trocar), a lista de processos do Windows | o reabrir do programa (só anotado: abriria o nosso .exe, que aqui não existe), o teste rápido |
| `prova_pacote_esperando.py` | a biblioteca do Velopack de verdade (`get_update_pending_restart`, `check_for_updates`, `download_updates` com o arquivo já no lugar), a falta de internet (a fonte que some; para o GitHub, um proxy que não existe, só neste processo) | a lista de processos, o teste rápido |
| `prova_volta_sem_janela.py` | o **`vpk` 1.2.161 e o `Update.exe` de verdade** (um programa de prova sem janela feito com o PyInstaller, a instalação portátil numa pasta minha, `--silent`), com o `--norestart` que a biblioteca põe quando não é para reabrir, e um arquivo de `current\` preso por outro processo | o programa (é o de prova, não o nosso de 460 MB); depois, o executor com as peças de mentira |
| `prova_casinhas.py` | a regra, o executor, o disco, as assinaturas | as peças do Windows e do Velopack, o teste rápido, o número de bytes livres (a conta é a de verdade) |
| `prova_guarda_morta.py` | a guarda de verdade copiando 300 MB, o processo **morto à força** (TerminateProcess) no meio da cópia, as aberturas seguintes | as peças, o teste rápido |
| o GitHub de verdade | `Fonte.padrao().ler(...)` de uma versão que não existe no GitHub do projeto: a resposta 404 de verdade | — |
| `mutacoes_qtq4.py` | 30 proteções desligadas uma a uma numa CÓPIA do ramo (`git archive`), com os 10 arquivos de teste do atualizador, um por vez | — |
| os testes do ramo | 83 arquivos, um por vez (os do atualizador, da peça do Windows, do porteiro, do publicar e das conferências, e os 64 `tests/test_decisoes*.py`) | — |

Não rodei: o disco cheio de verdade (sem licença de administrador não dá para criar um disco pequeno; simulei o número
de bytes livres), dois processos guardando ou anotando o bilhete ao mesmo tempo (são a D-850 e a (a) da D-866, que o
Samuel deixou para depois; o terceiro "quem tenta quebrar" já rodou), e a troca com a janelinha do Velopack (só a prova
à vista).

---

## Achado grave

### G1. Se a janela da versão estragada não abre, a frase (3) nunca aparece, e o programa nunca mais tenta voltar

- **O que o Kaique veria.** A versão nova entrou e não passou no teste rápido. Ou o Windows não deixou voltar (um
  arquivo preso, D-855), ou ainda não havia última boa (a primeira atualização depois do instalador, D-857). A regra
  manda mostrar "A atualização não deu certo e o programa não conseguiu voltar sozinho. Não desinstale nada. Avise o
  Samuel." e abrir a janela. Mas o teste rápido reprova exatamente a versão que não abre (ele importa a janela; um erro
  nessa importação é "não passou"). Nesse caso a janela não abre, e a frase, que espera a janela numa fila, nunca é
  mostrada. O Kaique vê só a caixa "Um momento — Aconteceu um problema inesperado, mas o programa continua funcionando."
  (que não é verdade: o programa fecha em seguida). E toda abertura seguinte é igual: nada de frase, nada de volta.
- **EXECUTADO (`prova_janela_que_nao_abre.py`)**, nos dois caminhos, cada abertura num processo à parte:
  - A (a volta recusada; o Velopack reabriu a 1.2.0 com `--voltando 1.2.0 1.1.0`): a frase (3) ficou **na fila da tela**;
    o `main.main()` parou na importação da janela; na tela, só "Aconteceu um problema inesperado, mas o programa continua
    funcionando."; a marca de "sem volta" ficou no disco; nenhuma frase marcada como vista. A abertura seguinte, pelo
    atalho: 0 testes, nenhum pedido de volta, a mesma caixa genérica. A última boa 1.1.0 continua guardada e nunca é usada.
  - B (sem última boa, o pacote da 1.2.0 em `packages\`): o teste rodou e falhou, a frase (3) ficou na fila, a mesma
    caixa genérica, a marca de "sem volta"; a abertura seguinte, a mesma coisa.
- **A causa.** Duas coisas juntas: (1) toda frase da atualização só chega à tela por `ligar_na_janela`, chamada no fim do
  `main()`, depois de a janela principal abrir; nenhuma frase tem caminho que não dependa dela; (2) a marca de "sem
  volta" (D-863) é gravada no disco ANTES de a frase ser vista (`_ao_abrir` e `_volta_que_nao_deu`), e é ela que impede
  as aberturas seguintes de tentar de novo. A tabela da volta 4 não tem a casinha "a versão que falhou não consegue abrir
  a janela": diz, em "Voltar × Windows nega", "a frase (3), uma vez, e a janela (na versão que falhou)".
- **Por que grave.** O Kaique fica sem o programa, a tela diz uma coisa falsa ("continua funcionando"), a frase que pede
  "não desinstale nada" não aparece, e nada mais tenta resolver. Antes da volta 4, a volta recusada ao menos era tentada
  de novo (em laço, o G1 do terceiro); agora a marca a desliga mesmo sem a frase ter sido vista. Quando acontece: uma
  versão publicada com uma peça faltando que impede a janela de abrir (uma DLL ou um módulo que não foi para o pacote: o teste rápido acusa justamente isso, ao importar a janela) E (o
  arquivo preso na volta OU a primeira atualização depois do instalador). A primeira atualização do Kaique é exatamente
  o segundo caso.
- **Fere:** D-855 ("mostra a frase (3) e abre"), D-857 ("aparece a frase (3) da D-778 e para"), D-778, D-842, CLAUDE.md
  §11.12 pontos 2 e 3 (a marca dá como feito o que não aconteceu: "a frase foi mostrada").

---

## Achados médios

### M1. A frase do "Sim" ao fechar aparece depois de a atualização ter dado certo

- **O que o Kaique veria.** É o caso da própria D-858: ele tem duas janelas do programa abertas, as duas com o aviso da
  versão nova. Fecha a primeira e responde "Sim": não troca (há outra janela) e a frase fica guardada. Fecha a segunda e
  responde "Sim": agora troca, e dá certo. Na abertura seguinte, **já na versão nova**, aparece "Não deu para atualizar
  agora: havia outra janela do programa aberta. Tente ao fechar o programa." Ele vai tentar atualizar o que já está
  atualizado.
- **EXECUTADO (`prova_frase_velha.py`)**: a peça do Windows de verdade viu a "outra janela" (um processo de verdade em
  `current\`); o "Sim" da primeira guardou a frase; o "Sim" da segunda pediu a troca; a reabertura sem janela da 1.2.0
  passou no teste, marcou aprovada e guardou a última boa; a abertura seguinte, na 1.2.0, mostrou a frase acima.
- **A causa.** A frase guardada no bilhete é mostrada na abertura seguinte sem olhar se ela ainda é verdade: o nome dela
  traz a versão ("nao_deu_agora-1.2.0-..."), e a versão que roda já é a 1.2.0. É o contrário da emenda do Fable ("a
  verdade vem do disco, não do bilhete"): aqui o bilhete diz e ninguém confere. A tabela ("Sim ao fechar × clique
  repetido") só pensa no caso em que nada troca depois.
- **Fere:** D-858/D-864 (a frase é para "o 'Sim' que não troca"), D-842 (frase errada), §11.12 ponto 2.

### M2. O atualizador do Velopack que some: a frase manda "Tente ao fechar o programa" e fechar não pergunta nada; a atualização para de vez, calada

- **O que o Kaique veria.** Com a versão nova baixada e o aviso na tela, um antivírus põe de lado o `Update.exe` (o caso
  que o terceiro achou). Ele clica "Reiniciar agora": a janela fecha (o trabalho é gravado) e abre de novo, com "Não deu
  para atualizar agora: o atualizador do programa não começou. Tente ao fechar o programa." Ao fechar, **nenhuma
  pergunta**. Nas aberturas seguintes, nada: nem aviso, nem frase. A atualização nunca mais chega, e nada diz isso.
- **EXECUTADO (`prova_update_exe_some.py`, a biblioteca do Velopack de verdade):** com o `Update.exe` no lugar, achou,
  conferiu, baixou e mostrou o aviso; apagado o `Update.exe`, o clique fechou a janela e pediu a reabertura; a biblioteca
  recusou a troca ("This application is not properly installed: Update.exe does not exist"); a abertura reaberta mostrou
  a frase acima, e o fechar não perguntou nada (fase "parado"); daí em diante `pendente` e `procurar` falham com o mesmo
  erro, e a regra trata isso como "sem internet" (só o registro). **LIDO:** baixar de novo não traz o `Update.exe` de
  volta: com o pacote já em `packages\`, o Velopack nem baixa nem tira o `Update.exe` de dentro dele (`manager.rs`
  413-416, antes da linha 463 que o tira); e o `UpdateManager` nem chega a ser criado.
- **A causa.** A conferência única da troca (`conferencia_da_troca`) confere o pacote, o motor e a outra janela, mas não o
  `Update.exe`, que é a única coisa que a biblioteca exige para trocar: a janela fecha por nada. Depois, a frase promete
  uma pergunta ao fechar que só existe com a versão pronta nesta abertura, e sem o `Update.exe` nenhuma abertura chega a
  "pronta". Raro (precisa de o `Update.exe` sumir), mas o caso foi pedido por nome.
- **Fere:** D-845 ("Tente ao fechar o programa" tem de levar a algum lugar), D-842 (frase que promete o que não
  acontece), §11.12 ponto 3 (a falha "o Update.exe sumiu" pensada só até a primeira frase).

### M3. A volta que não pôde ser pedida por um motivo de um instante vira "sem volta" para sempre

- **O que o Kaique veria.** A versão nova falhou no teste e há última boa guardada. Na hora de voltar, o Windows não deu
  a lista de processos (um instante), ou o Kaique clicou duas vezes no atalho nos segundos sem nada na tela (o M1 que o
  Samuel deixou para depois). A volta não é pedida, aparece a frase (3), e **nenhuma abertura seguinte tenta voltar**,
  embora a última boa esteja lá e a volta fosse dar certo um segundo depois. Ele fica na versão estragada até a próxima
  atualização.
- **EXECUTADO (`prova_casinhas.py`, C1 e C2):** nos dois casos, a primeira abertura: 1 teste, nenhum pedido de volta, a
  frase (3), a marca de "sem volta"; a segunda e a terceira aberturas, com um clique só e nada mais aberto: 0 testes,
  nenhum pedido de volta, nada na tela; a última boa 0.1.0 continua no disco.
- **A causa.** `_volta_que_nao_deu` põe a marca de "sem volta" para todo motivo, inclusive os que passam num instante. A
  D-863 foi perguntada sobre o arquivo preso ("o arquivo preso pode já ter sido solto"); a extensão para "a volta que nem
  pôde ser pedida" foi do implementador (está escrita no ONDE-PAREI, não escondida). Para os dois cliques, o efeito do
  M1 deixado para depois mudou: o terceiro relatou "na próxima abertura (um clique só), a volta acontece e aparece a
  frase (1)"; agora ela nunca acontece. O Samuel decidiu a D-861 com o efeito antigo.
- **O que precisa:** a palavra do Samuel (a D-863 vale também para "a volta nem pôde ser pedida por um instante"?) e a
  reconfirmação da D-861 com o efeito novo. Não é defeito de frase: a frase (3) é verdade.

### M4. A volta pedida depois do "Sim" ao fechar tenta duas vezes, a primeira calada, e a tabela diz uma

- **O que o Kaique veria.** Fecha com "Sim", a versão nova entra e falha no teste (por trás, sem janela). A volta é pedida
  sem reabrir (nada abre na tela, D-769). Se o Windows não deixa (um arquivo preso), o Velopack desiste e não reabre nada:
  nada é marcado. Na próxima abertura pelo atalho, o teste roda de novo (segundos sem nada na tela) e a volta é pedida de
  novo, agora reabrindo. Só então vem a frase (3), ou a (1). Não é laço, mas são duas tentativas e duas janelinhas do
  atualizador, e a tabela ("Voltar × Windows nega") diz que "o Velopack reabre a que falhou com a marca".
- **EXECUTADO (`prova_volta_sem_janela.py`, o `Update.exe` de verdade):** com `--norestart` e um arquivo de `current\`
  preso, o Update.exe saiu com código 1, `current` ficou na 1.2.0, e **nenhuma reabertura** (só o gancho
  `--veloapp-obsolete`). O executor: na reabertura sem janela, 1 teste e o pedido de volta com `reabrir=False`; na abertura
  seguinte pelo atalho, mais 1 teste e outro pedido de volta, com `reabrir=True`. **LIDO:** `apply.rs` 57-60 (`if restart`).
- **A causa.** A marca `--voltando` só serve se o Velopack reabrir o programa; no caminho sem janela ele não reabre.
- **Por que médio e não leve:** o Kaique vê os segundos sem nada e a janelinha uma segunda vez, e a D-855 diz "tenta uma
  vez". É o mais fraco dos médios: nenhuma frase errada, e a segunda tentativa pode até dar certo.

### M5. Duas proteções sem teste (D-827)

Desligadas numa cópia, nenhum dos 10 arquivos de teste do atualizador reclamou (`mutacoes_qtq4-resultado.txt`):
- **X11 — o 404 do GitHub como "não existe".** É o caminho de verdade da frase (2) no GitHub: uma versão publicada sem a
  assinatura dá 404 e tem de mostrar "Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do
  Samuel...". Trocado o 404 por "sem rede", a frase some e a versão é procurada calada a cada abertura. EXECUTADO: o
  GitHub de verdade responde 404 e o código de hoje dá `FileNotFoundError` (a frase 2), certo; mas o teste novo da
  volta 4 (`test_a_rede_que_nao_responde_na_assinatura_nao_e_recusada`) só usa a fonte de pasta.
- **X18 — a assinatura guardada do pacote esperando (D-859) não ser conferida.** Sem internet, o pacote esperando é
  oferecido pela assinatura guardada em `ultima-boa\`, uma pasta que Usuários podem modificar (D-837). Sem a conferência
  da chave do Samuel, um arquivo de assinatura posto por outra conta, com a soma de um pacote trocado, faria o programa
  trocar para ele. É a D-724 ("só pacote assinado") no caminho novo, sem teste.

As outras 27 foram acusadas (item 5); a X25 é equivalente (ver o item 2).

### M6. A marca de "sem volta" que não consegue ser gravada: a cada abertura o teste e a janelinha do atualizador, sem frase

- **O que o Kaique veria.** A volta recusada pelo Windows (o caso da D-855), com a pasta da última boa não aceitando mais
  arquivo nenhum. A primeira vez: a frase (3). Daí em diante, a cada abertura pelo atalho: segundos sem nada (o teste), a
  janelinha do atualizador (a volta pedida de novo), o Velopack recusa e reabre, e **nenhuma frase** (a (3) já foi
  "vista"). É o laço do G1 do terceiro, uma volta por abertura, enquanto a marca não grava.
- **EXECUTADO (`prova_casinhas.py`, C3):** com o nome da marca ocupado (a gravação dela falha), três aberturas seguidas:
  cada uma, 1 teste e 1 pedido de volta; a reabertura com `--voltando` mostrou a frase (3) só na primeira; marca nenhuma.
- **A causa.** O "não tenta de novo" da D-863 depende de uma gravação que pode falhar, e a falha só vai para o registro
  (`marcar`). A tabela ("Voltar × disco cheio") diz "a marca de sem volta, a frase (3), e abre; não tenta de novo".
- **Raro:** no uso normal a pasta aceita gravação (licença de Usuários) e um arquivo pequeno costuma caber mesmo com o
  disco cheio. Pus como médio porque o Kaique veria (D-842), não porque seja provável.

---

## Achados leves (só aparecem no código ou no registro)

1. **O registro diz uma coisa que deixou de ser verdade.** Quando a guarda não cabe, a linha é "...o teste roda de novo
   na próxima abertura" (`fases_da_atualizacao.py`, `UltimaBoaGuardada`), mas desde a D-856 a versão aprovada não é
   testada de novo (EXECUTADO, C4: a abertura seguinte não testou). Só a gerente lê.
2. **Sem internet, o registro diz "versão 1.2.0 publicada e assinada pelo Samuel: baixando"** para o pacote esperando
   (EXECUTADO, `prova_pacote_esperando.py`); nada é baixado e nada foi lido da publicação.
3. **A tabela ("Guardar × o nome final preso") descreve um passo que saiu** no próprio commit `5dfcdc9d` ("o nome final é
   tirado do caminho antes de copiar"). O comportamento continua certo (a assinatura por último; os testes `test_l1_*`
   passam e a mutação P17/N4 do implementador foi acusada); só o texto ficou velho.
4. **Depois de a guarda morrer no meio, sobra a cópia pela metade** (`<pacote>.chegando`, até 460 MB) em `ultima-boa\` até
   a guarda da versão seguinte (EXECUTADO, `prova_guarda_morta.py`: morto aos 64 MB, a última boa continuou a 1.1.0, a
   marca de aprovada ficou, as duas aberturas seguintes não testaram nem copiaram, e os 68 MB ficaram). A pasta não fica
   pela metade (a última boa de antes vale), por isso pus leve; é parecido com a (b) da D-866.
5. **Outra conta de espaço no programa:** `configuracoes.espaco_livre_mb` (de julho, a pasta de saída do PDF) também usa
   `shutil.disk_usage`. Não é do atualizador nem desta volta; "só `espaco_livre_basta` mede o disco" vale para o
   atualizador.
6. **O título e as duas primeiras frases do aviso da versão nova** ("Versão nova do programa", "Chegou uma versão nova do
   Editor de Impressão.", "Salve o seu trabalho e reinicie o programa para usar a versão nova.") vêm de 16/11 e não estão
   escritos no Livro (o terceiro já disse; continua para a gerente confirmar se o Samuel as viu).

---

## Item 1: a tabela contra o código (D-862)

**74 casinhas** (9 passos; 7 a 9 linhas cada). **Rodei 13 delas, mais 1 que falta na tabela** (marcadas abaixo), e
**li as outras 61** no código e, onde a tabela cita, no código do Velopack.

| Casinha | Executado? | Bate com a tabela? |
|---|---|---|
| Procurar × sem internet (o pacote esperando, D-859) | EXECUTADO, Velopack de verdade | sim: o aviso e a pergunta ao fechar vieram, e o "Sim" pediu a troca |
| Conferir × sem internet (a fonte que some; o GitHub sem rede) | EXECUTADO (C5; `URLError` de verdade) | sim: nada na tela, só o registro |
| Conferir × a assinatura que não existe (pasta; o GitHub 404 de verdade) | EXECUTADO | sim: a frase (2), uma vez |
| "Reiniciar agora" × o atualizador não abre (o `Update.exe` sumiu) | EXECUTADO, Velopack de verdade | a parte escrita sim (a janela reabre com a frase); a frase promete o que não acontece: **M2** |
| "Sim" ao fechar × outra janela aberta | EXECUTADO, lista de processos de verdade | a frase guardada sim; **depois** dela a troca pode acontecer: **M1** |
| Testar × passou (a marca de aprovada) | EXECUTADO (C4, guarda morta) | sim |
| Testar × clique repetido | EXECUTADO (C1) | o efeito mudou com a D-863: **M3** |
| Guardar × desliga no meio da cópia | EXECUTADO (morto à força) | sim (sobra o `.chegando`, como a tabela diz: leve 4) |
| Guardar × disco cheio | EXECUTADO (C4, bytes livres de prova) | sim: não copia, a anterior vale, nada se repete |
| Guardar × primeira versão instalada | EXECUTADO (G1-B) | sim: não testa, nada é baixado (0 pedidos ao Velopack) |
| Voltar × Windows nega, com janela | lido (a prova de verdade é a do implementador, que reli) | sim, se a janela da versão abrir: **G1** |
| Voltar × Windows nega, depois do "Sim" ao fechar | EXECUTADO, `Update.exe` de verdade | **não**: o Velopack não reabre: **M4** |
| Voltar × sem última boa | EXECUTADO (G1-B) | sim, se a janela abrir: **G1** |
| Voltar × disco cheio (a marca que não grava) | EXECUTADO (C3) | **não**: tenta de novo a cada abertura: **M6** |
| Voltar × a lista do Windows que não veio | EXECUTADO (C2) | casinha que falta; vira "sem volta" para sempre: **M3** |

**As frases, palavra por palavra (EXECUTADO: o texto que a tela recebe comparado com o Livro):** as três da D-778, a da
D-839, a da D-840, a da D-843, a da D-864, o molde da D-845 com os nove motivos da D-847, o título "Atualização" da D-846
e os textos da D-835: **todos iguais**.

**O que fica no disco (lido e, nos casos acima, olhado):** o que a tabela diz, menos o G1 (a marca de "sem volta" sem a
frase vista), o M1 (a frase guardada que fica velha) e o M6 (a marca que não fica).

**As casinhas que faltam na tabela:** a versão que falhou não consegue abrir a janela (G1); a frase guardada que deixa
de ser verdade antes de ser vista (M1); a volta do caminho sem janela (M4); a volta que não pôde ser pedida por um
motivo de um instante (M3); a marca que não grava (M6); e, no "Reiniciar agora", o `Update.exe` que some (M2: está na
tabela só até a primeira frase).

## Item 2: as perguntas do Fable

- **O `estado.json` decide alguma coisa além de "reprovadas" e "frase"? Não** (LIDO, o arquivo inteiro): é lido num
  lugar só (`abrir` → `reprovadas_do_bilhete`, `frase_do_bilhete`) e escrito num lugar só (`mudar_o_bilhete`), que joga
  fora qualquer outra chave. As reprovadas decidem "não baixar/oferecer de novo" (também o pacote esperando) e a frase (1)
  derivada. Mas a frase guardada é mostrada sem ser conferida contra o disco (M1): o bilhete não decide nada novo, porém
  o que ele diz passa para a tela sem a conferência que a emenda pede.
- **As marcas novas viraram um juiz novo? Sim, as duas decidem** (se a versão é testada, e por isso se volta). A de
  aprovada é a que o Samuel e o Fable pediram por nome (D-856: "marca no disco (`aprovada-<versao>`, ao lado da última
  boa)"): é o juiz combinado, num lugar só (`_precisa_do_teste`), e funciona (C4). A de "sem volta" é escolha do
  implementador para cumprir a D-863 (o Samuel decidiu o comportamento, não o arquivo); é arquivo novo que decide, o
  sinal que o Fable pediu para olhar. Ela é lida num lugar só e escrita num lugar só (`marcar`), não é gambiarra de
  desvio; mas é ela que causa o G1 (gravada antes de a frase ser vista), o M3 (gravada para todo motivo) e o M6 (quando
  não grava, nada a substitui). **Opinião:** precisa de uma memória para a D-863, e o lugar é razoável; o problema é
  quando ela é escrita e o que ela supõe que já aconteceu.
- **Sobrou caminho morto? Não.** Procurei todo nome de função dos três arquivos que o programa não chama: nenhum. O
  download da última boa (`_baixar_a_que_roda`, o índice publicado) e o teste por trás (`antes_da_janela`,
  `_depois_da_licenca`, `_com_antes`) saíram; o nome `antes_da_janela` só aparece num nome de teste antigo. A mutação X25
  (tirar o "sem o pacote em packages, não guarda") é equivalente: sem o pacote, a guarda dá erro na mesma linha seguinte
  e devolve o motivo; não há caminho de download para onde ela pudesse ir.
- **O que cresceu (+5,6%) é necessário? Sim**, tudo vem de uma decisão: as duas marcas (D-856, D-863), a conta única do
  espaço (D-856), a assinatura que chega com outro nome (o leve 1 do terceiro), o pacote esperando (D-859), a frase do
  "Sim" ao fechar (D-858/D-864), a separação "não existe / sem rede" (achado do implementador, que tira uma frase (2)
  falsa sem internet). Não achei nada a mais. Falta, isso sim, o que não cresceu: a conferência da frase guardada (M1) e
  do `Update.exe` (M2).

## Item 3: o ReabrirOPrograma e o `Update.exe` que some

- **Um lugar só na regra** (LIDO): a troca do "Reiniciar agora" que não pôde ser pedida depois de a janela fechar, sem
  outra janela aberta (não mudou desde o terceiro). A peça que reabre (`lancar_solto`, com o sinal de vida) eu só li.
- **O `Update.exe` que some entre o download e o clique: EXECUTADO** (`prova_update_exe_some.py`, M2). A reabertura
  acontece e a frase aparece; o problema é o que vem depois (a pergunta ao fechar não vem, e a atualização para de vez).

## Item 4: uma peça só (§11.12)

- **Só `core/conversa_com_o_velopack.py` importa `velopack`** no programa (EXECUTADO: busca no código; fora dele só
  testes e as minhas provas). `test_trava_windows.py` passa (42 + 3 pulados).
- **Só `espaco_livre_basta` mede o disco no atualizador** (o motor e a guarda a chamam; só ela chama `disk_usage`). A
  outra conta do programa é de julho e não é do atualizador (leve 5).
- **A soma de um arquivo é uma conta só** (`assinatura.soma_sha256`, também para copiar): o leve 5 do terceiro está
  consertado.
- **A K03 continua a aprovada da D-837:** `core/windows.py` e `regras_dos_agentes/` não mudaram desde o terceiro (que a
  conferiu); `test_porteiro_licenca_que_acrescenta.py` passa (14).

## Item 5: proteções desligadas (D-811, D-827)

EXECUTADO (`provas/mutacoes_qtq4.py`, saída em `mutacoes_qtq4-resultado.txt`): numa cópia do commit feita com
`git archive` (o ramo nunca foi mexido), 30 proteções que eu escolhi, uma de cada vez, com os 10 arquivos de teste do
atualizador, um por vez. Sem mutação, os 10 passam na cópia (no arquivo de resultado, a linha "SEM MUTACAO" diz
"SOBREVIVEU": nenhum teste falhou).
- **Acusadas (27):** as duas marcas (não olhadas, não postas, não gravadas pelo executor, a de aprovada depois da guarda),
  a reabertura com `--voltando` (não lida; sem a marca; a que deu certo virando "não conseguiu voltar"; testando de novo),
  a volta sem `--voltando`, a primeira versão do .msi testada, a frase (3) sem última boa, a separação "sem rede" (na
  regra, no executor, na fonte de pasta), o "Sim" ao fechar (sem frase, com a frase da D-840, com o texto da D-864
  trocado, com o pacote trocado), o pacote esperando (não oferecido; oferecido reprovado), o espaço da guarda, e as
  quatro do M7 do terceiro (Q1, Q2, Q9, Q13: as quatro agora acusadas; a D-860 está cumprida).
- **Sobreviveram (2, M5):** X11 (o 404 do GitHub) e X18 (a assinatura guardada do pacote esperando).
- **Equivalente (1):** X25 (explicada no item 2).

## Item 6: o que já funcionava ao redor (§11.8)

EXECUTADO, um arquivo por vez, no ramo, com a pasta temporária no D: (`provas/testes-um-por-vez-resultado.txt`): **83
arquivos** (os do atualizador, da peça do Windows, do porteiro, do publicar e das conferências, e os **64
`tests/test_decisoes*.py`**): **3921 casos passaram, 13 pulados, nenhum falhou**; só os 64 das decisões, 929 passaram e
5 pulados. Do atualizador:
`test_atualizador_volta4` 20, `test_fases_da_atualizacao` 2387, `test_atualizador_d851` 3, `test_atualizador_novo` 34,
`test_atualizador_volta2` 32, `test_atualizador_volta3` 36, `test_atualizador_volta3_de_verdade` 4 (+1 pulado),
`test_decisoes_atualizacao` 42, `test_decisoes_ajudante_da_atualizacao` 22, `test_velopack_de_verdade` 3: todos passam.
Os testes que saíram ou mudaram nesta volta estão na lista da D-836 ("Volta 4"); conferi que cada um que saiu tem o seu
substituto citado (os três do `test_atualizador_d851` pelos `test_d857_*`; o do índice publicado, porque o programa não o
lê mais). O conjunto inteiro fica com a rodada do GitHub (verde em `5dfcdc9d`).


## Os achados do terceiro "quem tenta quebrar", conferidos na causa

| Achado | A causa de antes | Hoje |
|---|---|---|
| G1 a volta recusada em laço | o pedido da volta ia sem marca | **resolvido na causa** no caminho com janela: `--voltando` (X20, X21 acusadas; a prova de verdade do implementador). No caminho sem janela não há laço, mas há duas tentativas (M4). Se a marca não grava, volta uma volta por abertura (M6) |
| M1 dois cliques | duas aberturas testando juntas | deixado para depois (D-861); o efeito mudou: agora fica na versão estragada para sempre (M3) |
| M2 sem última boa, falha calada | "sem última boa" tratado como "nada a fazer" | **resolvido na causa** (D-857: a frase (3), a reprovação, X24 acusada), **se a janela abrir** (G1) |
| M3 "Sim" ao fechar calado | a D-845 só no "Reiniciar agora" | **resolvido na causa** (D-858/D-864, X13-X15 acusadas); a frase pode ficar velha (M1) |
| M4 teste e cópia a cada abertura | nenhuma memória de "passou" | **resolvido na causa** (D-856, X1, X6, X8, X19 acusadas; C4 e a guarda morta executados) |
| M5 a premissa da D-851 | o download da guarda | **resolvido na causa** (D-857: o download saiu inteiro; nenhum caminho morto; X25 equivalente) |
| M6 o pacote esperando | a regra recebia e não usava | **resolvido na causa** (D-859, executado com o Velopack de verdade; X16, X17 acusadas), menos uma proteção sem teste (X18, M5) |
| M7 quatro proteções sem teste | — | **resolvido** (D-860: Q1, Q2, Q9, Q13 acusadas) |
| leve 1 a assinatura antes do pacote | a assinatura gravada no nome final antes da hora | consertado (a assinatura por último; o texto da tabela ficou velho: leve 3) |
| leve 4 sobras | o `pendente` sem uso; o motivo da outra janela sem uso | consertado (os dois passaram a ser usados) |
| leve 5 a soma em dois lugares | duas contas | consertado (uma conta só) |
| leves 2, 3, 6 | — | deixados para depois (D-866) |
| leve 7 testes de tempo | — | não é do atualizador; nesta rodada não falhou |

## O que precisa da palavra do Samuel (para a gerente levar à Central, no jeito do §11.13)

1. **G1** e **M1, M2, M4, M5, M6**: consertar antes da prova, ou "deixo para depois", um por um (D-842).
2. **M3**: a regra "depois da frase (3), não tentar voltar de novo" vale também quando a volta nem pôde ser pedida por
   um motivo de um instante (a lista do Windows, dois cliques)? E a D-861 (dois cliques, para depois) continua para
   depois sabendo que agora ele fica na versão estragada até a próxima atualização?

## O que eu fiz fora das minhas pastas (para a gerente saber)

- **Nada escrito em `C:\ProgramData\EditorImpressao`, em `%LOCALAPPDATA%\EditorImpressao` nem na instalação do Samuel.**
  Toda prova trocou as variáveis dentro do Python e conferiu o caminho com `assert` antes de rodar.
- **Sobrou fora do projeto (não apaguei):** `%LOCALAPPDATA%\velopack\velopack_ProvaQ4.log` (7 KB, o registro do
  `Update.exe` do meu programa de prova `ProvaQ4`). O `vpk` mexeu na pasta `%LOCALAPPDATA%\velopack\velopack` às 21:25
  (a dele; não olhei dentro). O PyInstaller e o `vpk` podem ter deixado arquivos na pasta temporária da conta (`%TEMP%`;
  procurei pelos nomes de costume e não achei nada das últimas duas horas).
- **Conferido só lendo:** o `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log` foi gravado pela última vez às
  16:38:49 (as 7 linhas do erro do terceiro), antes do começo do meu trabalho (20:44).
- **Uma pergunta de verdade ao GitHub do projeto** (`releases/download/v0.0.1/...assinatura`, um arquivo que não existe),
  para ver a resposta 404 de verdade. Nenhum dado pessoal; o projeto é público e o programa faz essa mesma pergunta.
- O clone do Velopack que li é o que já estava na pasta de rascunho desta sessão (`vp\src`, etiqueta `1.2.161`, commit
  `92d6a1c`), só lido.
- Dentro do projeto, só criei `saida_teste\qtq4\` e esta pasta do relatório. A `saida_teste\qtq4\` foi apagada no fim,
  depois de tirar antes as 5 junções que um teste do ramo cria na pasta temporária (todas apontavam para dentro dela).

## O que só a prova à vista pode mostrar

- Quantos segundos ficam sem nada na tela na abertura que testa e volta, no notebook (copiar 460 MB para `packages\`, a
  soma duas vezes, o teste): é nesse tempo que o segundo clique do M3 acontece.
- A janelinha do Velopack nas duas tentativas do M4.

## A minha opinião, com as ressalvas

Este relatório está **PRONTO PARA CONFERIR**. Não é aprovação: só o Samuel marca.

A minha opinião: **o atualizador NÃO ESTÁ PRONTO para a prova à vista.** As três regras do Samuel encolheram a volta
como o Fable queria: nenhum laço no caminho com janela, nenhum teste repetido, nenhum download de 460 MB, nenhum caminho
morto, e as frases batem todas com o Livro. O que achei não são remendos nem peças duplicadas; são casos que a tabela não
pensou, quase todos em volta de **quando** uma frase ou uma marca vale:

- o G1: a frase (3) depende de a janela abrir, e a marca de "sem volta" é gravada antes de a frase ser vista;
- o M1: a frase guardada é mostrada sem conferir se ainda é verdade;
- o M2: a frase "Tente ao fechar" é mostrada quando fechar não vai perguntar nada;
- o M3 e o M6: a marca de "sem volta" para todo motivo, e nada no lugar dela quando ela não grava;
- o M4: a marca `--voltando` no caminho em que o Velopack não reabre;
- o M5: duas proteções sem teste, uma delas a que guarda a assinatura do Samuel no caminho novo.

O Fable previu "coisa pequena (frases, tempos)". Achei frases, sim, mas uma delas é a que falta justamente no pior
momento (G1).

**Ressalvas minhas:**

1. O G1 rodou com o `main.py` de verdade e a janela quebrada de propósito (o import dela falha); não com uma versão de
   verdade publicada estragada. Que o teste rápido reprova exatamente o que impede a janela de abrir é leitura do
   `teste_rapido` (ele importa a janela).
2. O M1 e o M3 rodaram com o pedido ao Velopack de mentira (só anotado); a troca de verdade está nas provas da volta 4.
3. O "disco cheio" foi simulado (o número de bytes livres; e, no M6, o nome da marca ocupado).
4. As provas com o `Update.exe` usaram `--silent` (sem a janelinha) e um programa de prova, não o nosso de 460 MB.
5. Rodei as mutações e a rodada dos testes ao mesmo tempo no mesmo PC; nenhuma falha apareceu, mas os testes de tempo
   (leve 7 do terceiro) poderiam ter falhado por isso.
6. A cópia das mutações não tem o git do ramo; por isso o `test_trava_windows.py` ficou fora delas (nenhuma mutação minha
   é da trava; ele passa no ramo).
