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

## 30/10, terceira parte — 2ª rodada do verificador: Gravuras não religavam (PARADO, pergunta P3)

- Parecer (`verif-cadernos/.../parecer-d589-rodada2.md`): NÃO CUMPRE nas Gravuras. Depois de desmarcar e
  rodar, marcar "Gravuras e fotos" de novo e rodar não religa (a frase promete "achar gravuras e fotos";
  a caixinha volta desmarcada).
- Causa conferida: o desligar grava `gravura_forma="desligada"`, que é também a caixinha de dentro
  "Achar gravuras e fotos" (D-212). A janela começa do livro (`opcoes_do_livro`), então o Rodar seguinte,
  com a etapa marcada, aplica de novo a forma "desligada" (`aplicar`, ramo GRAVURAS) e `ligada_no_livro`
  continua falso. Reproduzido pela prova nova `test_d589_desmarcar_rodar_marcar_rodar_religa[gravuras]`
  ("desligada" ≠ "ligada no livro todo"); `[margens]` e `[cadernos]` religam.
- Tentei a ideia do verificador (commit `bc1b590`): desligar pelo "Procurar" do livro
  (`detectar_regioes=False`). Religava, e a prova passou, mas a rodada do GitHub 41151868748 FALHOU:
  - `tests/test_decisoes_so_as_letras.py::test_d148_...` (prova da D-148): com "Limpar" + "Só as letras"
    e "Gravuras e fotos" desmarcada, a gravura saiu em preto e branco ("a gravura perdeu a cor"). O
    `detectar_regioes` é o "Procurar gravura e letra": desliga também a marcação das letras e do papel,
    da qual o "Só as letras" depende. (Eu não tinha rodado esse arquivo; falha também no PC.)
  - `teste_botoes.py`: 4 falhas ("o ícone 'automatico'/'props'/'filtro'/'historico' não abriu o painel
    dele"). Com as gravuras desligadas, o livro de teste ganhou "1 página para você olhar", o roteiro
    clicou em "ver a lista…" do "Para revisar", e os ícones seguintes não abriram. Efeito da mesma troca.
- Voltei o código ao jeito da forma "desligada" (igual ao `484cb1c`, que passou no GitHub e na
  1ª conferência), com o defeito escrito no código. A prova de religar das Gravuras ficou marcada como
  "falha conhecida" (`xfail` estrito, com o motivo); Margens e Cadernos passam.
- "Desligar as marcadas" NÃO mudou (D-068). Ele já tinha o mesmo defeito antes desta tarefa: depois de
  "Desligar as marcadas" com Gravuras, marcar e rodar também não religa.

**P3 — Como desligar "Gravuras e fotos" desmarcada sem quebrar o religar nem o "Só as letras"?**
Exemplo real: Kaique liga Limpar (Preto e branco) + Gravuras e roda; depois desmarca Gravuras e roda; depois
marca Gravuras de novo e roda. Hoje a gravura não volta (a etapa fica "desligada").
- **A** — Desligar pelo "Procurar gravura e letra" (o que tentei): religa, mas com Gravuras desmarcada o
  programa também para de achar as letras, e o "Só as letras" deixa a gravura em preto e branco (fere a
  prova da D-148, que roda com Gravuras desmarcada).
- **B** — Continuar com a forma "desligada" e, quando a pessoa marca a etapa Gravuras com "Achar gravuras e
  fotos" desligada, a janela marca "Achar gravuras e fotos" junto (volta ao contorno "livre", D-213; a
  escolha "Este livro tem fotos" de antes se perde). Mexe na tela (`ui/automatico.py`) e vale também
  depois do "Desligar as marcadas".
- **C** — Guardar a forma de antes ao desligar e devolvê-la ao marcar (precisa de um campo novo no
  projeto.json — mudança de formato de dados, CLAUDE.md §6).
- Também precisa da resposta: com "Gravuras e fotos" desmarcada e "Só as letras" ligado, a gravura deve
  sair com a cor (como a D-148 diz) ou em preto e branco ("se algo não está marcado, não é para fazer")?
  Não conferi o que acontece hoje num livro de verdade com a forma "desligada" (a prova da D-148 usa uma
  marcação antiga, sem assinatura, que não é refeita).
- Recomendação do construtor: decidir primeiro a pergunta do "Só as letras"; se a gravura deve ficar com
  cor, B; se deve sair em preto e branco, A.
- Rodada do GitHub 41154048024 (commit c854ade, forma "desligada" de volta + xfail): passou inteira.

## 31/10 — resposta da pergunta de base da P3 e conferência da B

- Samuel: "Sim" para "vale o 'Só as letras', e a figura sai colorida" (com "Gravuras e fotos" desmarcada).
- Conferido (teste temporário, apagado): o "Só as letras" só guarda a figura colorida quando ela está
  marcada como gravura pela máquina. Sem a área da gravura (só a das letras), a pintura sumiu (cor 0,0 em
  vez de > 0,8). Ou seja: para a figura sair colorida, o programa precisa PROCURAR as gravuras. Com o
  "Só as letras" ligado e "Gravuras e fotos" desmarcada, as duas frases dele se chocam, em qualquer jeito
  de desligar (A, B ou C).
- Jeito que não perde nada e não mexe na tela: desligar pelo "Procurar" do livro (religa ao marcar, guarda
  o "Este livro tem fotos"), MAS não desligar quando o "Só as letras" estiver ligado. Custo: nesse caso a
  etapa "Gravuras e fotos" continua ligada e volta marcada depois do "Rodar". Parado esperando a resposta.
