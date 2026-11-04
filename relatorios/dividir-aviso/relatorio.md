# D-613: o "dividir todas" pergunta sobre as folhas juntadas à mão

Ramo `dividir-aviso-2026-11-04` (saiu de `obra-2026-10-26` em `dd7a648c`). Agente implementador, 04/11/2026.
Situação: **feito, a testar pelo Samuel.** Nada foi juntado em outro ramo.

## O pedido

Pergunta: "O "dividir todas" pula as folhas que você juntou à mão? Sugiro que sim." → Samuel: "2- ele dá um aviso perguntando ."

## O que mudou

Quando há folha juntada à mão ("dividir esta" e depois "não dividir esta"), o "dividir todas" mostra um aviso antes de começar:

- **Pular**: essas folhas ficam inteiras; as outras são divididas como sempre.
- **Dividir também**: todas são divididas, como era antes.
- **cancelar**: nada muda (nem começa a ler as folhas).

Cada escolha é uma ação só no desfazer (Ctrl+Z e Ctrl+Y). Sem folha juntada à mão, não aparece aviso nenhum: tudo como antes.

Onde: `ui/tela_conferir.py` (`_dividir_todas` e o aviso novo `_perguntar_as_juntadas`) e `core/dividir_a_mao.py` (`folhas_juntadas_a_mao` e a chave `JUNTAR_TODAS_CONTA`). Para saber quem juntou cada folha, o programa olha o histórico do desfazer (a última ação que juntou a folha foi um "não dividir esta" ou o "juntar todas"). Nada novo é gravado no projeto: o formato dos arquivos não muda.

## O texto do aviso (para mostrar ao Samuel)

Título: **Folhas juntadas à mão**

Com uma folha:

> 1 folha foi juntada à mão no Dividir. Pular essa folha?
>
> Pular: ela fica inteira, como você deixou. Dividir também: ela é dividida junto com as outras (o Desfazer traz de volta). As outras folhas são divididas nos dois casos.
>
> Botões: **Pular esta** (o de fábrica) · **Dividir também** · **cancelar**

Com mais de uma (exemplo, 3):

> 3 folhas foram juntadas à mão no Dividir. Pular essas folhas?
>
> Pular: elas ficam inteiras, como você deixou. Dividir também: elas são divididas junto com as outras (o Desfazer traz de volta). As outras folhas são divididas nos dois casos.
>
> Botões: **Pular as 3** (o de fábrica) · **Dividir também** · **cancelar**

Mesmo jeito do aviso do Automático (D-004): a pergunta, a explicação embaixo, "Pular as N"/"Pular esta", o outro caminho e "cancelar" (minúsculo, como lá).

## Pergunta aberta (não é minha de decidir)

**As folhas juntadas pelo "juntar todas" contam como "juntadas à mão" para esse aviso?** Enquanto o Samuel não responder: **não contam** (só as juntadas uma por uma). Para ligar: trocar `JUNTAR_TODAS_CONTA = False` para `True` em `core/dividir_a_mao.py`; o teste `test_d613_juntar_todas_conta_com_a_chave_ligada` já prova esse jeito. Hoje, no Gradus copiado (as 70 folhas juntadas pelo "juntar todas"), o "dividir todas" divide as 70 sem aviso, como antes.

## Na janela de verdade (Gradus copiado, mensagens do Windows)

Piloto: `relatorios/dividir-aviso/piloto.py`; anotações: `anotacoes.txt`; prints em `prints/`.

| print | o que mostra |
|---|---|
| 01 | Dividir aberto: 70 folhas juntadas pelo "juntar todas", linha azul à vista |
| 02 | sem juntada à mão: "dividir todas" sem aviso, 70 divididas (depois, Ctrl+Z) |
| 03, 04 | folha 5: linha azul; "dividir esta" (a seta → depois foi para a página 6, D-608) |
| 05 | folha 5 juntada à mão ("não dividir esta") |
| 06, 07 | aviso → "cancelar": nada mudou, nenhuma ação nova |
| 08, 09, 10 | em "Duas lado a lado", aviso → "Pular esta": 69 divididas, a folha 5 inteira com a linha azul, a vista passou para "Uma página" (D-610) |
| 11, 12 | Ctrl+Z: tudo volta (a 5 continua juntada); Ctrl+Y: de novo 69 divididas |
| 13, 14, 15 | aviso → "Dividir também": as 70 divididas; Ctrl+Z volta |
| 16 | "dividir esta" na 5 e "juntar todas": continua juntando (D-590) |

## Testes (PC, um arquivo por vez)

Novo: `tests/test_decisoes_dividir_aviso.py`, **11 passaram**. No código de antes (`dd7a648c`) **10 falham** (os de pular, dividir também, cancelar, mistura, o aviso de verdade; o de reversão acusa "o aviso não aparece": `[] == [1]`); só o "sem juntada não pergunta" passa lá, como deve.

Antigos, sem nenhuma mudança: `test_decisoes_dividir` 21 · `test_decisoes_dividir_linha` 13 · `test_decisoes_dividir_arrastar` 16 · `test_decisoes_dividir_metade` 6 · `test_decisoes_juntar_todas` 4 · `test_decisoes_tira_em_pares` 4 · `test_dividir_ajustes_03_11` 9 · `test_dividir_na_tela` 9 · `test_dividir_no_programa` 19 · `test_dividir_desmarcada_caixinha` 3 · `test_dividir_scantailor` 13 · `test_caderno_segue_as_etapas` 11 · `test_automatico_pular_depois_de_dividir` 4 · `test_historico_depois_de_reabrir` 11 · `test_recomeco_limpa_o_historico` 13 · `test_promessas` (Dividir: P-212, P-059, juntar) 10. Todos passaram. **Nenhum teste antigo foi mudado.**

GitHub: rodada **41851955352** (resultado no fim deste relatório, quando chegar).

## Ressalvas

- Se o histórico do desfazer foi recomeçado, uma folha juntada sem ação no histórico conta como juntada à mão (o aviso pergunta: é o lado seguro).
- Se a pessoa escolhe "Pular" e todas as folhas que faltam são as juntadas, nada acontece e nenhuma frase aparece (não havia o que dividir).
- O aviso aparece antes de ler as folhas; uma folha juntada que o motor ache de uma página só entra na conta do aviso, mas mesmo com "Dividir também" ela fica inteira (como já era).
- A ordem dos botões na tela é a do Windows/Qt, igual à do aviso da D-004 ("Pular", "Dividir também", "cancelar").
