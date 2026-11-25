# Conferência curta do conserto da segunda recusa do Windows (25/11/2026)

**Do que se trata.** Quando a versão nova chega, o Kaique clica "Reiniciar agora". Se o Windows não deixa trocar (um
arquivo preso), o programa reabre na versão de antes e mostra a caixa "A atualização não deu certo. O programa continua
na versão de antes e funcionando. Avise o Samuel." Até agora, na segunda vez que isso acontecia para a mesma versão, a
caixa não aparecia. O conserto põe a hora no nome do aviso, para cada recusa ser um aviso novo.

Conferência do tamanho da mudança (D-879): só a linha que mudou, o que ela toca e as mutações dela. Código de
`0d9cac4e` (antes) a `11bd0575` (depois), ramo `atualizador-novo-2026-11-23`. Não fui eu que escrevi o conserto.
Só usei a caixa de mentira. Nenhuma caixa nem janela de verdade apareceu, e não fechei nenhum processo.

## A resposta em uma frase

**PRONTO PARA CONFERIR, com uma volta pequena antes:** o conserto funciona (a segunda e a terceira recusa mostram a
caixa, e a abertura pelo atalho não mostra nada), mas o teste novo só põe as duas recusas em dias diferentes. Se
alguém reduzir a hora do nome para "só o dia", a segunda recusa no mesmo dia volta a ficar sem aviso e nenhum teste
acusa. Achados: **0 graves, 1 médio, 0 leves, 3 pequenos.**

## Os cinco itens

### 1. O conserto faz o que a D-877 diz: EXECUTADO

Caso L1, só com a caixa de mentira: na versão 7.0.0, o Windows recusa duas vezes a troca para a 7.0.1, na mesma conta.
Rodei o `prova_casos.py` do quinto "quem tenta quebrar" e o meu `provas/l1_curto.py`. O meu faz seis aberturas:
recusa, recusa, atalho, atalho, recusa e atalho.

| Abertura | Depois do conserto (pausa de 1,2 s entre elas) | Antes do conserto (`0d9cac4e`) |
|---|---|---|
| 1, primeira recusa | a caixa aparece | a caixa aparece |
| 2, segunda recusa | **a caixa aparece** | nada |
| 3, pelo atalho | nada | nada |
| 4, pelo atalho | nada | nada |
| 5, terceira recusa | **a caixa aparece** | nada |
| 6, pelo atalho | nada | nada |

- **Não fica em laço.** A caixa só aparece na abertura que o Velopack reabriu depois de uma recusa. O programa só manda
  esse pedido quando o Kaique clica para trocar (`atualizacao.py:1337`). O "abrir de novo" do próprio programa não
  manda o pedido (`_reabrir`, linha 1357). As aberturas pelo atalho não mostram nada.
- **Ressalva.** O `prova_casos.py` do quinto, rodado como está, ainda mostra "nada" na segunda recusa, mesmo no código
  novo. Ele faz as duas aberturas no mesmo segundo, e a hora do nome vai só até o segundo. O meu `l1_curto.py` com
  pausa 0 dá o mesmo resultado, e com pausa de 1,2 s mostra a caixa nas três recusas. Isso não aparece para o Kaique
  (ver o pequeno 1), mas aquele script não serve como prova deste conserto.

### 2. O que o conserto toca: EXECUTADO, e LIDO onde está escrito

- **As frases guardadas para a próxima abertura (`guardar_frase`): EXECUTADO, comportamento igual ao de antes.** O
  `provas/bilhete_curto.py` rodou nos dois códigos. Caso testado: a frase "Não deu para atualizar agora: havia outra
  janela do programa aberta. Tente ao fechar o programa." Ela aparece uma vez, não aparece na abertura seguinte, e
  aparece de novo quando é guardada noutro dia. O mesmo vale para a recusa depois do "Sim" ao fechar: a caixa aparece
  uma vez na abertura seguinte. O nome continua no formato `<tipo>-<versão>-<hora>`. Entre o código antigo e o novo, a
  saída só muda nas horas.
- **As frases que continuam sem a hora: EXECUTADO, nada mudou.** A da versão sem a assinatura, a do motor e a da
  versão reprovada aparecem uma vez por versão, com os nomes `recusada-9.9.0` e `motor-9.9.0`, iguais aos de antes. O
  `prova_casos.py` inteiro (L1 a L6) dá a mesma saída do resultado guardado de `0d9cac4e`, fora as horas.
- **De onde vem a hora (`Abriu.momento`): LIDO.**
  - Ela vem de um lugar só, `atualizacao.py:1410` (`_agora()`, hora local até o segundo).
  - Quando falta (valor vazio, como nos testes da regra), o nome fica como antes, `troca-<versão>`: o aviso aparece
    uma vez por versão, sem laço.
  - Duas aberturas só têm a mesma hora se acontecerem no mesmo segundo (pequeno 1).
- **Alguém ainda monta o nome à mão (§11.12)? EXECUTADO com `git grep`.**
  - No programa, não: `id_do_acontecimento` é o único lugar.
  - Num teste, sim (pequeno 2).

### 3. O teste de reversão (§4.7): EXECUTADO

`test_d877_cada_recusa_do_windows_avisa_uma_vez_e_nao_se_repete`:

- **na minha cópia de `0d9cac4e`** (feita com `git archive`): **falha** porque a segunda recusa não mostra nada
  (`[[frase], [], []]`);
- **em `11bd0575`:** **passa**.

As saídas estão em `provas/reversao-0d9cac4e.txt` e `provas/reversao-11bd0575.txt`.

### 4. As mutações (D-827): EXECUTADO

Rodei numa cópia de `11bd0575` com git próprio, nunca no ramo. Os 12 arquivos de teste do atualizador rodaram um por
vez. Sem mutação, nenhum teste falhou. No fim, os arquivos mexidos voltaram ao original.

| Mutação | Resultado |
|---|---|
| V23 do escritor: o nome sem a hora | acusada (teste da D-877) |
| V24 do escritor: a abertura não manda a hora | acusada (teste da D-877) |
| C1 minha: a hora só com o dia | **SOBREVIVEU**: é o médio 1 |
| C2 minha: a hora fixa | acusada (teste da D-877) |
| C3 minha: a frase guardada sem a hora | acusada (`test_m7_q9_a_mesma_frase_noutro_dia_aparece_de_novo`) |
| C4 minha: a frase guardada volta a montar o nome à mão | sobreviveu, e é o esperado: o nome sai igual, então nenhum teste de comportamento pode acusar (ver o item 2) |
| C5 minha: o tracinho no nome mesmo sem hora | acusada (`test_a_frase_que_a_caixa_nao_mostrou_fica_para_a_proxima_abertura`) |

### 5. Os testes dos arquivos tocados: EXECUTADO

- **Um arquivo por vez, no ramo:**
  - `test_decisoes_atualizacao_volta5.py`: 23 passaram;
  - `test_fases_da_atualizacao.py`: 2255 passaram;
  - `test_atualizador_volta5.py`: 21 passaram;
  - `test_atualizador_volta4.py`: 18 passaram.
- **Os 12 arquivos do atualizador**, na cópia, como base das mutações: nenhum falhou.
- **No GitHub, a rodada 45695180689** testou `11bd0575` (conferi no registro da rodada) e passou inteira.

## Os achados (D-842)

### Médio 1: nenhum teste acusa se a hora do nome ficar só com o dia (proteção sem teste, D-827)

- **O que o Kaique veria se isso voltasse.** Ele clica "Reiniciar agora", o Windows recusa e a caixa aparece. Ele
  clica de novo na hora, o Windows recusa de novo, e nada aparece. É o mesmo clique sem resposta do defeito consertado.
- **Hoje o programa está certo.** O médio é a falta da prova: o teste da D-877 põe a primeira recusa em 25/11 e a
  segunda em 26/11, e o caso "de novo na hora", que o próprio conserto cita, fica sem teste.
- **Por que é médio.** Pela D-827, uma proteção sem teste nunca é "baixo".
- **Como repetir:**
  1. Faça uma cópia de `11bd0575` com git próprio.
  2. Rode `python -I relatorios/atualizador-novo/conferencia-curta-d877/provas/mutacoes_curtas.py <cópia> C1`.
  3. A resposta é "SOBREVIVEU".
- **Conserto sugerido (não mexi):** no teste da D-877, pôr as duas recusas no mesmo dia, com alguns segundos de
  diferença (por exemplo 10:00:00 e 10:00:05).

### Pequeno 1: duas recusas no mesmo segundo viram um aviso só

- A hora do nome vai até o segundo.
- O Kaique nunca chega nisso. Entre duas recusas ele clica OK na caixa, a janela abre, ele clica "Reiniciar agora" e
  o Velopack ainda tenta a troca. Tudo isso leva vários segundos.
- Só aparece na prova automática que abre duas vezes seguidas sem pausa (o `prova_casos.py`, item 1).
- **Como repetir:** `python -I provas/l1_curto.py <código> <pasta> 0`.

### Pequeno 2: um teste ainda monta o nome à mão

- Em `tests/test_atualizador_volta5.py:214`, o teste monta o nome com hora assim:
  `f"{fases.id_da_falha('nao_deu_agora', '1.2.0')}-2026-11-25T10:00:00"`.
- Pela §11.12 ampliada (vale também para testes), ele deveria usar `fases.id_do_acontecimento`.
- O Kaique nunca vê.

### Pequeno 3: a lista dos avisos já vistos ganha um nome por recusa

- Antes era um nome por versão. Agora cada recusa acrescenta uns 30 bytes ao arquivo da conta, e a lista nunca é
  limpa.
- O Kaique nunca vê.
- Sugestão: deixar como está.

## Fora do escopo (só anotado, não conferido)

- Os dois testes das proteções e o achado pequeno da D-878 continuam para depois, como o Samuel decidiu. Não mexi
  neles.
- A versão no nome é lida cortando no primeiro tracinho (`versao_da_falha`). Uma versão com tracinho (ex.:
  "1.2.0-beta") não seria lida. Isso é anterior a este conserto, e hoje as versões não usam tracinho.

## Decisões tocadas

- **D-839, cumprida.** A frase sai palavra por palavra, na caixa do Windows, a cada recusa.
- **D-845, cumprida neste caso.** "Nenhum clique fica sem resposta": a segunda recusa agora responde.
- **D-877, cumprida no programa e pela metade na prova.** Falta o caso "duas recusas no mesmo dia" (médio 1).
- **D-879, seguida.** Esta conferência ficou no tamanho da mudança.

## Minha opinião, com as ressalvas

- O conserto está no lugar certo e num lugar só. A regra do nome mora em `core/fases_da_atualizacao.py`, a frase
  guardada usa a mesma função, e os avisos que devem aparecer uma vez por versão continuam como eram. Não achei desvio
  para um caso só.
- Ele resolve o defeito e não cria laço.
- Antes de ir para a prova à vista, sugiro consertar o médio 1: é uma linha no teste.
- Os três pequenos vão ao Samuel para "deixo para depois" (D-842).

**Ressalvas:**

1. Nada disto rodou com a caixa de verdade nem com o Velopack de verdade. Só a prova à vista mostra a caixa na tela do
   Kaique.
2. O teste da D-877 troca o relógio por uma lista de três horas. Se o programa passar a ler a hora mais vezes numa
   abertura, o teste quebra por falta de hora, e não por defeito.
3. O que o Velopack faz depois de uma recusa (reabrir a versão de antes uma vez, com o pedido) eu só LI, no
   ONDE-PAREI e no relatório do quinto. Não rodei.
4. Não escrevi em `C:\ProgramData\EditorImpressao` nem em `%LOCALAPPDATA%\EditorImpressao`. As datas dos arquivos de
   lá não mudaram (24/11 e 22/11).

Provas e scripts: `relatorios/atualizador-novo/conferencia-curta-d877/provas/`.
