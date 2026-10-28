# Testes guiados — sessão 2 (ele testando sozinho pelo atalho, 28/10/2026)

Programa: atalho "Editor de Impressao (rodada de consertos)" → worktree `.claude\worktrees\obra-juncao`, ramo
`obra-2026-10-26` (`fc38afd`), dados de teste em `D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos`.

Tipos: **erro** (faz errado ou não faz nada) · **confuso** (faz, mas não dá para entender) · **falta** ·
**a conferir**.

## Achados

| # | O que ele escreveu | Print | Tipo | O que a gerente achou (só leitura, nada mudado) |
|---|---|---|---|---|
| 2-1 | "eu cheguei a abrir o aplicativo, mas ele está bem travado" | — | erro (a conferir) | Livro aberto de manhã: *Cursus philosophicus. Tomo 2* (402 páginas). Pelo `acoes.jsonl`: aberto ~10:32, primeira ação 10:36, Mover na página 1 (10:36), **Marcação na página 1** (10:37–10:38), fechado 10:44. A página 1 tem **302 marcações de letra** feitas pelo programa; cada mexida na Marcação grava as 302 de novo (antes + depois, 140 a 565 mil caracteres por ação; ação comum ~500). Suspeita, não provada: a Marcação pesa a cada clique. Também no PC: League of Legends aberto desde 27/10 22:16 (1,6 GB de memória), só 2 GB livres de 16. Perguntado a ele onde travou mais (abrir / passar páginas / Marcação ou Mover / travou tudo); sem resposta ainda. |
| 2-2 | "quando eu clico em tirar do livro a pagina fica como apagada, mas não é tirada do pc" | ![](s2-01-tirar-do-livro-fica-apagada.png) | a conferir | Print: Palatino, página 6 de 134; as 4 primeiras miniaturas com "apagada". **O que o programa faz hoje:** "Tirar do livro" marca a página como tirada; ela **continua na tira de miniaturas com a palavra "apagada"** (para poder "trazer de volta") e **não vai para o PDF final** (`ui/tela_conferir.py` `apagar_pagina`; `core/avisos.py`). O arquivo do PDF de entrada no computador nunca é mexido. **Decidido (D-046, 07/10):** "Tirar do livro" = "o que não é página do livro sai de vez". Nada decidido sobre a página sumir da tira na tela. Perguntado a ele o que esperava (sumir da tira? sair do PDF? apagar do PDF de entrada?). |
