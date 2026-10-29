# D-583/D-586: caixinha "Respeitar as gravuras achadas" no painel do Filtro — onde parei

Ramo `automatico-respeitar-gravuras-2026-10-29` (saiu de `obra-2026-10-26`, commit `2db002e`), worktree
`.claude/worktrees/auto-respeitar`. Agente construtor, 29/10/2026. Sem push, sem juntar.

## Decisões que esta tarefa precisa cumprir (escrito antes de mexer)

Conferidas no `docs/plano/DECISOES.md` desta worktree.

**A que se constrói:**

- **D-583** (29/10/2026): "Precisamos da opção de jogar o filtro em cima de outro filtro ou só substituir o filtro que
  está colocado em cima." · depois da investigação (o que fica "por cima" é a marcação do Automático): "c" — "C — As
  duas, com uma escolha no painel do Filtro. Por exemplo, uma caixinha que diz se o filtro respeita ou não as gravuras
  achadas."
- **D-586** (29/10/2026, "A"): "A — Uma caixinha no painel "Filtro da página", logo abaixo das figurinhas dos filtros:
  "Respeitar as gravuras achadas". De início vem ligada, que é como funciona hoje. Desligada, o filtro vale na página
  inteira: no Preto e branco, a capa sairia toda em preto e branco, como na fileira de baixo da primeira imagem que te
  mostrei. Vale com o "Aplicar em: só nesta / todas / daqui em diante" que já existe no painel."

**As que não podem quebrar:**

- **D-148** (30/09 e 05/10): "(a) Uma caixinha 'Só as letras' dentro do Preto e branco, para o livro [...] e para a
  página (aba Filtro) (recomendado)" — marcada, só as letras viram preto e branco; gravura, foto, moldura e iluminura
  ficam como no original.
- **D-168** (05/10): "(a) Fica apagada (cinza) enquanto 'Só as letras' estiver marcada, e volta como estava ao desligar
  (recomendado)".
- **D-144** (30/09): "Mantém a cor original (como o ANTES); traço preto só se eu escolher" · 01/10: "Sim, mantém a cor"
  — com a caixinha nova LIGADA, moldura e iluminura continuam com a cor no Preto e branco.
- **D-127** (28/09): "Iluminura sai intacta: cores, figuras, fundos e dourados como no original." · **D-128**: "a borda
  dourada deveria sair sem alteração" — idem, com a caixinha ligada.
- **D-126** (28/09): "Gravura e letras intactas, e todo o papel totalmente branco, inclusive o papel dentro da gravura"
  — idem, com a caixinha ligada.
- **D-199** (06/08 e 01/10): "quero ter opção de colocar o filtro só em um lugar, por exemplo colocar só na iluminura ou
  só no texto" e **D-224** (01/10): "espero ter a escolha de conseguir deixar a foto em original, caso precise." — os
  pedaços feitos À MÃO ("Só neste pedaço") continuam valendo com a caixinha desligada.
- **D-020** (18/07): "Ctrl+Z desfaz qualquer alteração, sem limite de quantidade, e Ctrl+Shift+Z refaz".
- **D-066** (23/10): "precisamos que o pdf saia que nem está na tela" e **D-473** (26/10): "Tela e PDF saem da mesma
  conta."
- **D-010** (26/10): "eu acho que o botão tem que ser provado que ele faz o que se diz que se faz, e não só se ele muda
  algo na tela." — promessa em `tests/promessas/promessas.md`, prova em `tests/test_promessas.py`.
- **D-090** (08/10) e **D-545** (27/10): "usar em todas" nunca apaga exceção.
- **D-585** (29/10): "deixar como está e deixar anotado" — a classificação pintura × enfeite NÃO se mexe aqui.
- **CLAUDE.md §6**: mudar o formato do projeto precisa de autorização → dada por esta decisão (D-586: "campo por
  página"); documentado abaixo. **§4.7** (reversão), **§4.10** (caminho inteiro; cada foto diz por onde passou), **§11
  regra 7** (só o que ele mandou: nenhum atalho, menu, aviso ou texto além do nome e do balão).
- **Fora do escopo (não consertar):** as figurinhas do painel não usam a marcação (Lista de bugs, 29/10).

## Andamento

- [ ] campo novo na página + conta no `core/pipeline.py`
- [ ] caixinha no painel + "Aplicar em" + desfazer
- [ ] provas, reversão, velocidade, prints
