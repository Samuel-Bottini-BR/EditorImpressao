# ONDE-PAREI — de onde vieram os quadrados brancos (investigador, 10/11/2026)

Ramo `quadrados-origem-2026-11-10` (a partir de `obra-2026-10-26`, ponta `d9f80eb4`), worktree
`.claude/worktrees/quadrados-origem`. Só investigação: nenhuma linha do programa muda. Acervo só lido;
tudo em cópias, sem janela (`QT_QPA_PLATFORM=offscreen`), `LOCALAPPDATA` à parte, prioridade baixa.

## O que o Samuel perguntou

Central, 10/11, resposta "Ainda não entendi" ao relatório `relatorios/quadrados-brancos-2026-11-10/`:

> "Mas antes ele não fazia isso né, você tentou usar o motor do scantailor para achar gravura e onde achar
> gravura ele não deixar esses pontos brancos assim, pois eu nunca tinha visto o programa fazer isso, descubra
> que agente fez o programa começar a fazer isso, é só você ver os testes que fizemos antes com o melhorar e
> magico pro."

## Decisões que esta tarefa precisa cumprir

- Regra da Fase 1 (28/09): "todo o papel totalmente branco, inclusive o papel dentro da gravura"; "sem
  quadradinhos" (bug 202, roupa do anjo da Escola 35, `tests/test_papel_dentro_da_gravura.py`).
- D-009 (26/10): "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo manualmente."
- D-002 (25/09 e 26/10): o livro abre direto na área de trabalho; o Automático é um painel.
- D-586 / D-583 (29/10): "Respeitar as gravuras achadas" ligada = o filtro respeita a marcação.
- D-659 (09/11): no Preto e branco à mão, "Respeitar" marcada faz o programa procurar a gravura.
- D-605 (03/11): o novo não estraga o já escolhido e testado.
- CLAUDE.md §9: a correção do "magic color" não se desfaz. Não abrir janela na tela do Samuel (09/11).
- CLAUDE.md §10: modelo de print do girar. §2: relatório em três formatos. §11.7: só o que ele mandou.

## Andamento

- [x] ramo e worktree; versões antigas em cópias (`git worktree` e `git archive`)
- [x] página 13 em dez versões (bisseção)
- [ ] oito páginas, Livro de Horas 47 e Boécio em cinco situações
- [ ] livro inteiro: antes, hoje e só a mudança desfeita
- [ ] imagens no modelo de print
- [ ] relatório nos três formatos, commit e push

## O que achei

(em andamento)

## Perguntas para o Samuel

(em andamento)
