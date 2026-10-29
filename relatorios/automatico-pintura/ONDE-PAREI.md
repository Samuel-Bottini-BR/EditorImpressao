# "Só as letras" no Automático e a pintura da capa (D-585) — onde parei

Ramo `automatico-pintura-2026-10-29` (saiu de `obra-2026-10-26`, commit `226536c`), worktree
`.claude/worktrees/auto-pintura`. Agente de consertos, 29/10/2026. Sem push, sem juntar.

## Decisões que esta tarefa precisa cumprir (escrito antes de mexer)

Conferidas no `docs/plano/DECISOES.md` desta worktree:

- **D-144** (30/09/2026): "Mantém a cor original (como o ANTES); traço preto só se eu escolher" · 01/10, P1: "Sim,
  mantém a cor - [...] o resultado do preto e branco da iluminura não está bom." → no Preto e branco, moldura e
  iluminura ficam com a cor de fábrica.
- **D-147** (30/09/2026): P1a "Cinza (tons de cinza): BOM" → no Preto e branco, foto e pintura saem em tons de cinza,
  nunca pontilhadas.
- **D-148** (30/09 e 05/10/2026): "(a) Uma caixinha 'Só as letras' dentro do Preto e branco, para o livro (tela 'O que
  fazer') e para a página (aba Filtro) (recomendado)" → marcada, só as letras viram preto e branco; gravura, foto,
  moldura e iluminura ficam como no original. (A do livro mora hoje na janela do Automático.)
- **D-168** (05/10/2026): "(a) Fica apagada (cinza) enquanto 'Só as letras' estiver marcada, e volta como estava ao
  desligar (recomendado)" → a caixinha das molduras fica cinza com "Só as letras" ligada.
- **D-126** (28/09/2026): "Gravura e letras intactas, e todo o papel totalmente branco, inclusive o papel dentro da
  gravura [...]. Só pintura de verdade, como a roupa do anjo e o céu colorido, mantém a cor."
- **D-127** (28/09/2026): "Iluminura sai intacta: cores, figuras, fundos e dourados como no original. [...]"
- **D-128** (28/09 e 30/09/2026): moldura dourada mantida sem mudar a cor · "a borda dourada deveria sair sem alteração".
- **D-585** (29/10/2026): "enfeite colorido guarda a cor em todos os filtros. só se eu escolher né? se eu colocar filtro
  preto e branco só nas letras." Registro: defeito contra a D-147 na capa do *Na escola de Jesus* (a pintura, 82% da
  página, foi tratada como enfeite e guardou a cor no Preto e branco sem "Só as letras").
- **Pedido de 29/10** (palavras dele): "eu usei no painel automatico, mas não foi agora na ultima sessão e não lembro
  que ssessão foi, mas cofira se isso está funcionando" (o "Só as letras" do Automático).
- **D-583** (29/10, "c"): a escolha "o filtro respeita ou não as gravuras achadas" no painel do Filtro — decidida, não
  construída; **não é desta tarefa** (não mexer).
- **CLAUDE.md §3** (algoritmo consagrado, nada de fórmula inventada), **§4.7** (teste de reversão), **§4.10** (caminho
  inteiro; cada foto diz por onde passou), **§5** (medir antes, uma mudança, medir depois; tudo em
  `relatorios/melhorias.md`), **§11 regras 1 a 7** (só o que ele mandou; na dúvida, perguntar).

(As seções seguintes são escritas ao longo do trabalho.)
