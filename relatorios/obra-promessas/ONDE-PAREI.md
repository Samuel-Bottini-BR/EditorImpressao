# Bateria nova, parte 4: "Cada botão prova que faz o que promete" — ONDE PAREI

Verificador (`.claude/agents/verificador.md`), ramo `obra-promessas-2026-10-26` (base `obra-2026-10-26` `fdabf0d`,
com as etapas 1, 2 e 9a), worktree `.claude/worktrees/obra-promessas`. Não mexo em `ui/` nem `core/`: só testes, a
lista de promessas e este relatório.

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que esta tarefa faz |
|---|---|---|
| D-010 (26/10) | "eu acho que o botão tem que ser provado que ele faz o que se diz que se faz, e não só se ele muda algo na tela." | Uma promessa escrita por botão (`tests/promessas/promessas.md`), tirada do nome, da dica e do Livro; o teste (`tests/test_promessas.py`) clica e confere a promessa inteira: tela, projeto gravado e PDF gerado de verdade. Botão sem promessa reprova. |
| D-011 (26/10) | "Sim" (nova bateria de testes: teste do Kaique, tarefas, decisões, promessas, conferência em caminho) | Esta é a parte "promessas" (item 4 da bateria, plano de 26/10). |
| D-014 (26/10) | "Faça até o final sem pausas [...] pode escolher sem minha conferência" | Detalhes decididos por mim e anotados aqui. |
| Regra 4 do §11 | "Aparência não conta como prova." | A prova mede o projeto gravado (`projeto.json`, `acoes.jsonl`) e o PDF que sai, não só a tela. |

Promessas de decisões ainda não construídas (dono: etapas 3 a 11) ficam `xfail(strict=True)`: quando a etapa fizer, o
teste passa a exigir.

## Andamento

- [ ] inventário dos botões de cada tela (varredura automática)
- [ ] lista de promessas
- [ ] provas
- [ ] rodada e tabela cumpre / quebra / aguarda etapa
