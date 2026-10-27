# Obra de 26/10/2026 — etapa 6 (ver o livro na área de trabalho): ONDE PAREI

Ramo `obra-etapa6-2026-10-26` (base `obra-2026-10-26` = `3e112f9`, com as etapas 1-5, 9a, 9c, 10a, 10b), worktree
`.claude/worktrees/obra-etapa6`. Agente: layout. Ordem do Samuel (D-014): fazer até o fim sem pausas; ele confere tudo
no fim. Regra nova da gerente (27/10, palavras do Samuel: "é só para fazer o que eu já tinha mandado, fazer as
ferramentas que colocamos no programa funcionem como deveriam e como eu tinha escolhido"): só o que está no Livro e no
pedido; onde o Livro não responde, deixar como está e perguntar.

**Situação: em andamento** (começada em 27/10/2026).

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| D-015 (22/10, mais recente que 06/10) | Livro aberto como no UPDF aprovado: "Uma página / Duas lado a lado" na barra de baixo · 20/10, 904 A: "A — Sim, no menu Ver" | Na área de trabalho, a barra de baixo tem "Uma página / Duas lado a lado" e o menu Ver também. |
| D-006 (06/10) | "eu não quero padrão eu quero como opção um botão que eu clique e veja pagina lado a lado" · 201 B / 202 A · 26/10: "eu tinha escolhido para poder trocar de duas paginas para duas" | Opção (não padrão); pares rolando (202 A), também na área de trabalho. O lugar (201 B) foi trocado pela D-015. |
| D-058 (20/10) | `r14-menus-novas`: "A — Sim, no menu Ver" · `ly-ver`: "Está bom" | O menu Ver ganha "Ver lado a lado" (o 5º item que faltava). |
| D-007 (26/10) | "quando eu escolher para começar no automatico e dividir as folhas o livro tem que aparecer em uma pagina por vez para mim." | Dividido, o livro aparece uma página por vez (de fábrica "Uma página"); a folha inteira só no Dividir. |
| D-501 (etapa 4) | (escolha da gerente) como a D-007 fica na tela | Continua valendo. |
| D-343 (05/10) | "Na opção 2 (pares), clicar abre as duas páginas lado a lado, como vai ser impresso." | Na grade "Todas as páginas" em pares, clicar num par abre as duas lado a lado. |
| D-347 (22/10, `lyupdf`, `lu-par`) | "da uma na internet como o updf faz. Tem uma pagina maior que outra ali" | No par as duas ficam da mesma altura; a 1 (capa) sozinha à direita (o mesmo `paginas_rolando.py`). |
| D-021 (29/07, paráfrase) | navegação: roda do mouse, Page Up/Down, Home/End | Na área de trabalho: roda troca de página (sem zoom); Page Up/Down pulam 10 (PEDIDOS.md l.290: "Pula 10 páginas de cada vez"); Home/End vão ao começo e ao fim. |
| D-026 (24/09 e 28/09, paráfrase) | 3.8: consertar o zoom que às vezes não funciona | Não piorar o zoom; a roda no zoom é da etapa 6 (ver "Contradições"). |
| Desenho decidido (rodada 13, `21-rodada13-base.html`) | barra de baixo à direita: "antes / depois", "– 78% +", "ajustar à tela" | Os três na barra de baixo. "antes / depois" = o Original × como vai sair (o "Comparar com o Original" da tela cheia, R11 601 A). |
| Troca da etapa 4 | "a página da vez agora fica na mesma folha quando a lista muda (`lista_de_paginas_mudou`); quem fizer o 'Ver lado a lado' deve usar o mesmo cuidado." | O lado a lado acompanha a lista nova e fica na mesma folha. |
| D-010 | "o botão tem que ser provado que ele faz o que se diz que se faz" | Promessas dos botões novos, com prova; P-136 sem "aguarda". |
| Regra fixa da gerente | não trocar o que vem do ScanTailor nem módulos inteiros que funcionam (reaproveitar `ui/widgets/paginas_rolando.py`) | O lado a lado é o mesmo `PaginasRolando`, com a página que vem das prévias. |

## Contradições achadas (vale a mais recente, D-014)

- **D-015 (22/10) × D-006/201 B (06/10):** lugar do botão. Vale a D-015: barra de baixo e menu Ver (nada "em cima das
  páginas, canto direito").
- **Roda do mouse: D-026 (prova escrita pela gerente "a roda do mouse sempre dá zoom") × D-021 e o pedido desta etapa
  (27/10: "roda do mouse troca de página (quando não está com zoom)").** As palavras do Samuel na D-026 são só
  "consertar o zoom que às vezes não funciona"; a frase da roda é a prova anotada. Vale o pedido mais recente (27/10):
  sem zoom a roda troca de página; com zoom ela continua dando zoom como antes; e Ctrl+roda dá zoom sempre, para o
  zoom pela roda não sumir (ver Perguntas).

## Andamento

- [ ] ONDE-PAREI com as decisões
- [ ] lado a lado na área de trabalho (barra de baixo + menu Ver), pares das prévias divididas
- [ ] antes / depois, zoom, ajustar à tela
- [ ] roda, Page Up/Down, Home/End
- [ ] lista de páginas muda → mesma folha também no lado a lado
- [ ] provas (`tests/test_decisoes_ver.py`), promessas, reversão
- [ ] GitHub, prints, ONDE-PAREI final
