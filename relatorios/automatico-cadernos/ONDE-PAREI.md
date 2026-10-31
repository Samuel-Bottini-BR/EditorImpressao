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
- [x] Rodada do GitHub 41131159641: passou inteira (suíte em 5 partes + botões).

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

## 30/10, segunda parte — P1 respondida: também Margens iguais e Gravuras e fotos

- Samuel, respondendo a "conserto essas duas também ['Margens iguais' e 'Gravuras e fotos'], do mesmo
  jeito que os cadernos?": **"Sim, se algo não está marcado, não é para fazer , certo?"**. Dividir fica
  como está (a gerente ainda vai perguntar).
- Reproduzido antes do conserto (livro sintético com texto e uma "foto"): Limpar + Gravuras + Margens
  ligadas → desmarcar as duas e rodar só o Limpar → continuavam "ligada no livro todo", voltavam
  marcadas, e o PDF saía com margens (345 x 432 pt em vez de 288 x 403) e a foto em cinzas.
- Conserto: `core/automatico.py`, `_desligar_as_desmarcadas` (lista `DESLIGAM_DESMARCADAS` = Gravuras,
  Margens, Cadernos), chamada no "Rodar" DEPOIS das etapas marcadas (Gravuras só conta como ligada com o
  Limpar ligado, e o Limpar pode ter ligado na mesma rodada). Desliga do mesmo jeito do "Desligar as
  marcadas": Margens → `margens_iguais=False`; Gravuras → `gravura_forma="desligada"`. Mesma ação do
  Desfazer. "Desligar as marcadas" igual a antes.
- Provas novas (falharam no código de `3b70bb3`, passam agora):
  `test_d589_desmarcar_margens_iguais_e_rodar_sai_sem_margens_e_nao_volta_marcada`,
  `test_d589_desmarcar_gravuras_e_rodar_a_foto_sai_em_preto_e_branco_e_nao_volta_marcada`, e
  `test_d589_desligar_as_marcadas_nao_mexe_nas_desmarcadas`.
- P2 (do verificador, aberta): **sim, com este conserto acontece o mesmo com Margens iguais e Gravuras
  e fotos** — rodar "só nesta página" ou "nas escolhidas" com uma delas desmarcada desliga no livro
  todo (são do livro todo, D-484). Não mudei.
- Atenção (mudança que o Samuel precisa saber): antes, rodar só "Limpar a folha" já fazia o livro
  achar gravuras sozinho (a etapa aparecia ligada e marcada depois). Agora, com "Gravuras e fotos"
  desmarcada, o livro não procura gravuras. A receita de sempre (D-018) marca as gravuras, então o
  caminho do aviso do livro novo não muda.
- Rodada do GitHub 41147611641 (commit 484cb1c): passou inteira (suíte em 5 partes + botões).

## 30/10, terceira parte — 2ª rodada do verificador: Gravuras não religavam

- Parecer (`verif-cadernos/.../parecer-d589-rodada2.md`): NÃO CUMPRE nas Gravuras. Depois de desmarcar e
  rodar, marcar "Gravuras e fotos" de novo e rodar não religava (a frase prometia "achar gravuras e fotos";
  a caixinha voltava desmarcada).
- Causa conferida: `_desligar_as_desmarcadas` gravava `gravura_forma="desligada"`, que é também a caixinha
  de dentro "Achar gravuras e fotos" (D-212). A janela começa do livro (`opcoes_do_livro`), então o Rodar
  seguinte, com a etapa marcada, aplicava a forma "desligada" de novo (`aplicar`, ramo GRAVURAS:
  `opcoes.get(campo, ...)`) e `ligada_no_livro` continuava falso. Reproduzido pela prova nova
  `test_d589_desmarcar_rodar_marcar_rodar_religa[gravuras]` (falhou: "desligada" ≠ "ligada no livro todo";
  `[margens]` e `[cadernos]` já religavam).
- Conserto (como o verificador sugeriu): desmarcada, a etapa Gravuras desliga pelo "Procurar" do livro
  (`detectar_regioes=False`), o mesmo campo que o Rodar liga quando ela vem marcada. A forma de dentro não
  muda. Sem `detectar_regioes`, o PDF não usa as áreas achadas pela máquina; a marcação feita à mão fica
  (`garantir_selecao`/`etapas.marcacao_a_mao`). Mesma ação do Desfazer.
- "Desligar as marcadas" NÃO mudou (D-068): continua gravando a forma "desligada" (`_desligar`). Por isso
  o mesmo defeito continua por esse caminho: depois de "Desligar as marcadas" com Gravuras, marcar e rodar
  não religa (só pela caixinha de dentro). **Pergunta P3 para o Samuel/gerente:** o "Desligar as marcadas"
  das Gravuras passa a desligar do mesmo jeito (pelo "Procurar", para religar ao marcar)? Não mexi.
- Provas: `test_d589_desmarcar_rodar_marcar_rodar_religa` para Gravuras, Margens e Cadernos (desmarcar,
  rodar, marcar, rodar → "ligada no livro todo", caixinha marcada e o PDF igual ao da primeira vez:
  cinzas da foto, largura da folha, cadernos). A prova das Gravuras agora confere também que a forma de
  dentro não fica "desligada". Arquivo: 8 de 8.
- Testes um por vez (todos passaram): decisoes_automatico 24, decisoes_impressao 22, dialogo_impressao 5, impressao 17, cadernos 28, ver_como_fica 19, filtro_automatico 4, nucleo2 21, cancelar 1, recomeco 13, para_revisar_na_tela 26, respeitar_gravuras 19, marcacoes 19, trabalho_nao_se_perde 82.
- Rodada do GitHub 41151868748 (commit bc1b590): passou inteira.
