# ONDE PAREI — D-589 ("Montar cadernos" volta sozinho)

Ramo `automatico-cadernos-2026-10-30` (saiu de `obra-2026-10-26` em `d93c506`), cópia
`.claude/worktrees/auto-cadernos`. Construtor: implementador (pedido da gerente, 30/10/2026).

## Decisões que esta tarefa precisa cumprir

- **D-589 (30/10/2026).** Kaique: "ela não tá selecionada, nem ela e nem a opção de dividir [...] aí
  aplicou o filtro branco, letra preta. Aí só que ele forma os cadernos do mesmo jeito." · "depois de
  rodar a etapa, aí ele volta a marcar." · "tiro, é, a opção de montar os cadernos, aí depois ele
  coloca de novo sozinho." Livro: **"Desmarcar 'Montar cadernos' no Automático tem que valer: o livro
  sai sem cadernos, e a etapa não volta marcada sozinha."** Prova do Livro: "livro com 'Montar
  cadernos' ligada → desmarcar e rodar → o PDF sai sem cadernos, e o painel não mostra a etapa ligada".
- **D-068 (24/09).** "Toda função automática tem botão de ligar e desligar." (a caixinha de cada etapa
  e "Desligar as marcadas" continuam como estão).
- **D-484 (27/10, escolha da gerente).** "Gravuras e fotos, Margens iguais e Montar cadernos valem
  sempre para o livro todo (são do livro, não de uma página)".
- **D-002 (25/09)** e o desenho: "Marcar só as etapas que se quer; escolher a ordem" · nada muda no
  livro até "Rodar".
- **Regra 7 (27/10): só o que ele mandou.** Nenhum botão, aviso ou texto novo.

## Andamento

- [x] Li implementador.md, CLAUDE.md §3/§10/§11, D-589, relato e prints k-01/k-02.
- [x] Causa achada (abaixo).
- [x] Prova `tests/test_decisoes_montar_cadernos.py` escrita ANTES do conserto: falhou no código
      antigo (`assert not janela.projeto.montar_cadernos` → era True; e `Pedido` sem `desmarcadas`).
- [x] Conserto (commit `4ad3dbf`).
- [x] Prova passa (2 de 2). Testes do Automático e do "Montar para imprimir", um arquivo por vez: todos
      passaram (lista na entrega).
- [x] Prints num livro de verdade copiado (12 primeiras páginas do "Sobre a Consolação da Filosofia"),
      antes e depois do conserto: `antes-*.png` e `depois-*.png` nesta pasta; script `prints_d589.py`.
- [x] Commit e push.
- [ ] Rodada do GitHub (número na entrega).

## Causa

1. `core/automatico.py`, `aplicar` (no código antigo, linhas 684-705): o "Rodar" só LIGA as etapas
   marcadas (`g.no_livro(CAMPO_DO_LIVRO[etapa], True)` para Margens e Cadernos). Etapa desmarcada fica
   de fora da rodada, mas o que estava ligado no livro continua ligado. "Montar cadernos" tinha sido
   ligada numa rodada anterior → `Projeto.montar_cadernos` continuava `True` → `core/pipeline.py:4440`
   (`if projeto.montar_cadernos:`) monta os cadernos no PDF.
2. `ui/janela_principal.py:1358` (`_aplicar_o_automatico`): depois do "Rodar", o painel relê o livro
   (`EstadoDoAutomatico.do_projeto`), e `ui/automatico.py:198` faz
   `self.marcadas = set(A.etapas_ligadas(projeto))` → a etapa ainda ligada volta MARCADA. É o "ele
   coloca de novo sozinho".

Reproduzido no livro de verdade (código antigo): desmarcada e rodada, o livro continuou com
`montar_cadernos=True`, a caixinha voltou marcada, "ligada no livro todo", e o PDF saiu com 6 folhas
deitadas (cadernos) em vez de 12 páginas em pé.

## O conserto (só "Montar cadernos", como a D-589 manda)

- `core/automatico.py`: `Pedido.desmarcadas` (as etapas com a caixinha desmarcada na janela). No
  "Rodar" (não no "Desligar as marcadas"), "Montar cadernos" desmarcada e ligada no livro DESLIGA,
  na mesma ação do Automático (o Ctrl+Z traz de volta). Vale em qualquer "Rodar em", porque a etapa
  é do livro todo (D-484), como o ligar já era.
- `ui/automatico.py` (só `EstadoDoAutomatico.pedido`, uma linha + docstring): manda as desmarcadas.
- Como a etapa fica desligada no livro, o painel a relê como desligada: não volta marcada.
- Pedido montado por outro caminho (testes, linha de comando) sem `desmarcadas` não muda nada.

## Perguntas para o Samuel

**P1 — As outras etapas desmarcadas também devem desligar no "Rodar"?** O mesmo jeito de funcionar vale
para todas as etapas, mas a D-589 fala só de "Montar cadernos", e o conserto ficou só nela. Exemplo
real: no livro do Kaique, "Margens iguais" ligada numa rodada anterior → ele desmarca "Margens iguais"
e roda → o livro continua com as margens iguais e a caixinha volta marcada (igual aos cadernos). O
mesmo com "Dividir folhas ao meio", que ele também tinha desmarcado ("nem ela e nem a opção de
dividir"): hoje o livro continua dividido.
- **A** — Só "Montar cadernos" (como ficou). As outras desmarcadas ficam como estão no livro e voltam
  marcadas depois do "Rodar"; para tirar, "Desligar as marcadas".
- **B** — Também as outras etapas "do livro todo" (Margens iguais, Gravuras e fotos): desmarcada e
  "Rodar" desliga, como os cadernos. Nenhuma página perde trabalho.
- **C** — Todas: desmarcada e "Rodar" desliga no livro todo. Cuidado: "Dividir" desmarcado juntaria as
  folhas de novo (as páginas divididas voltam a ser a folha inteira), e Endireitar/Cortar/Limpar
  desmarcados fariam as páginas voltarem como vieram (o feito à mão fica).
- Recomendação do construtor: **B** (é o mesmo tipo de etapa dos cadernos e não desfaz trabalho de
  página); C muda muito o livro com um clique só.
