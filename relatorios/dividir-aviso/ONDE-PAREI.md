# ONDE-PAREI — D-613: o "dividir todas" pergunta sobre as folhas juntadas à mão

Ramo `dividir-aviso-2026-11-04` (saiu de `obra-2026-10-26` em `dd7a648c`), cópia
`D:\programas\EditorImpressao\.claude\worktrees\dividir-aviso`. Agente implementador, 04/11/2026.

## Decisões que esta tarefa precisa cumprir

- **D-613** (04/11/2026). Pergunta: "O "dividir todas" pula as folhas que você juntou à mão? Sugiro que sim."
  → "2- ele dá um aviso perguntando ." Na prática: quando há folhas juntadas à mão, o "dividir todas" dá
  um aviso perguntando se divide também essas ou se pula. As outras folhas são divididas como hoje.
- **D-004** (28/09/2026): "Automático em livro já mexido à mão: o programa pergunta se quer pular as
  páginas mexidas." O aviso que o Samuel já conhece: "Pular as N" / "Rodar nelas também" / "cancelar".
  O aviso novo segue o mesmo jeito.
- **D-605 / CLAUDE.md §11.8** (03/11/2026): "A partir de agora, nenhuma função nova, ou nova escolha dentro
  do programa pode alterar o que já está escolhido e testado, coisas novas não podem criar novos
  problemas, essa é uma nova regra que todos os agentes precisam ler".
- **§11.7 "Só o que ele mandou"**: nada além do aviso; o que o Livro não responde vira pergunta.

## O que já está escolhido e testado aqui (não pode mudar)

Decisões do Dividir e do "dividir todas":
- **D-590** "juntar todas" (uma ação do desfazer; não marca conferida; desmarcar o Dividir no
  Automático não junta). Provas: `tests/test_decisoes_juntar_todas.py`, `test_dividir_desmarcada_caixinha.py`.
- **D-498** "não dividir esta" guarda as duas páginas; "dividir esta" de novo devolve como estavam, na
  linha de antes. O "dividir todas" também devolve a juntada assim (se o motor a acha dupla).
- **D-601** "Uma página" mostra só a metade; tira com duas miniaturas por folha dividida.
  Prova: `tests/test_decisoes_dividir_metade.py`.
- **D-602** linha azul antes de cortar; "dividir todas" lê cada folha pelo motor (por trás, com
  andamento e "parar") e corta cada dupla na sua linha, numa ação só; a de uma página fica inteira;
  a já dividida fica; nada vira "conferida"; "motor de corte". Prova: `tests/test_decisoes_dividir_linha.py`.
- **D-606** trocar o motor na folha juntada refaz a conta. **D-607** texto do aviso do Automático para
  as juntadas. **D-608** a seta depois de clicar num botão do painel passa de folha.
  Prova: `tests/test_dividir_ajustes_03_11.py`.
- **D-609** arrastar a linha na folha inteira; o "dividir todas" corta a arrastada onde ficou.
  **D-610** dividir (esta / todas) em "Duas lado a lado" passa para "Uma página".
  Prova: `tests/test_decisoes_dividir_arrastar.py`.
- **D-611** tira em pares em "Duas lado a lado". Prova: `tests/test_decisoes_tira_em_pares.py`.
- **D-004** e o conserto de 03/11 (pular pelas páginas depois de dividir):
  `tests/test_automatico_pular_depois_de_dividir.py`.
- **D-090** "usar em todas" copia a linha desta folha (testado em `test_decisoes_dividir_linha.py` e
  `test_decisoes_dividir_arrastar.py`).

Testes que existem e precisam continuar passando sem mudança (contagem de `def test`):
- `tests/test_decisoes_dividir.py` (21), `test_decisoes_dividir_arrastar.py` (15),
  `test_decisoes_dividir_linha.py` (13), `test_decisoes_dividir_metade.py` (6),
  `test_decisoes_juntar_todas.py` (4), `test_decisoes_tira_em_pares.py` (4)
- `tests/test_dividir_na_tela.py` (9), `test_dividir_ajustes_03_11.py` (8),
  `test_dividir_no_programa.py` (19), `test_dividir_desmarcada_caixinha.py` (3),
  `test_dividir_scantailor.py`
- `tests/test_caderno_segue_as_etapas.py` (4), `test_automatico_pular_depois_de_dividir.py` (4)
- Desfazer: `tests/test_historico_depois_de_reabrir.py` (11), `test_recomeco_limpa_o_historico.py` (13)
- `tests/test_promessas.py` (P-212 "dividir todas", P-059, juntar todas)

Conferido: nenhum teste antigo clica no "dividir todas" com folha juntada à mão presente (todos
partem de livro sem nada juntado, ou de folhas só divididas). Então sem folha juntada à mão o
caminho fica igual, e nenhum teste antigo contradiz a D-613.

## Plano

1. Função em `core/dividir_a_mao.py` que acha as folhas juntadas à mão (inteiras, com as duas páginas
   guardadas) e separa as juntadas uma por uma ("não dividir esta") das juntadas pelo "juntar todas",
   olhando no histórico do desfazer qual foi a última ação que juntou cada folha. Sem mudar o formato
   dos arquivos. Uma chave única (`JUNTAR_TODAS_CONTA`) liga/desliga as do "juntar todas".
2. `ui/tela_conferir.py`, `_dividir_todas`: antes de ler as folhas, se há juntadas à mão, o aviso
   (método separado, para os testes trocarem). Pular → divide só as outras; Dividir também → como hoje;
   cancelar → nada.
3. Teste novo `tests/test_decisoes_dividir_aviso.py` (falha no código de antes).

## Perguntas para o Samuel

- (da gerente, aberta) As folhas juntadas pelo "juntar todas" contam como "juntadas à mão" para esse
  aviso? Enquanto não houver resposta: **não contam** (só as juntadas uma por uma). Ligar = trocar
  `JUNTAR_TODAS_CONTA` para `True` em `core/dividir_a_mao.py`.

## Andamento

- [x] Li CLAUDE.md, implementador.md, verificador.md, DECISOES (D-004, D-590, D-601, D-602, D-606 a D-610, D-613)
- [ ] teste novo
- [ ] código
- [ ] testes do Dividir e do desfazer no PC
- [ ] janela de verdade (prints)
- [ ] GitHub
- [ ] relatório
