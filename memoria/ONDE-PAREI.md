# Montagem da memória — onde parei

Ramo `memoria-2026-10-19`, worktree `.claude/worktrees/memoria`, a partir de `origin/fase-1` (`b8e9af7`).
Pedido: gerente, 19-20/10/2026 (CLAUDE.md §4.9; conjunto aprovado pelo Samuel: "Está certo").

> **Atualização de 26/10/2026 (etapa 0 da obra):** a memória **já foi juntada** ao `fase-1` (merge `ccc3d6d`, "Junta a
> memoria por assunto (ramo memoria-2026-10-19) ao fase-1"). O texto abaixo é de 20/10 e fica como registro. As
> decisões do Samuel agora moram no Livro de decisões, `docs/plano/DECISOES.md`.

## Situação em 20/10/2026: montagem terminada, NÃO juntada ao `fase-1`

Todas as partes feitas, com commit e push no ramo. `conferir_memoria.py`: "Tudo certo." (0 links quebrados; 152 de
152 entradas do Registro com ficha; nenhuma pergunta aberta já respondida). `tests/test_conferir_memoria.py`: 11
passaram.

| Parte | Arquivos | Situação |
|---|---|---|
| 0 | ONDE-PAREI, recados/LEIAME | feito |
| 1 | INDICE, geral/glossario | feito |
| 2 | itens/ da Fase 2 + para-revisar (20 fichas) | feito |
| 3 | itens/ das Fases 0, 1, 3 a 7 + layout (37 fichas) | feito |
| 4 | LINHA-DO-TEMPO, licoes, geral/jeito-do-samuel, geral/kaique | feito |
| 5 | mapa-do-codigo, geral/ambiente, geral/pc-e-github | feito |
| 6 | pedidos, resultados-R1-a-R9 | feito |
| 7 | conferencias, geral/paginas-claude-ai | feito |
| 8 | paginas-de-teste/ (102), livros/ (23) | feito |
| 9 | ramos, bugs, referencias/ (4) | feito |
| 10 | geral/regras-de-trabalho, geral/perguntas-abertas | feito |
| 11 | conferir_memoria.py + tests/test_conferir_memoria.py | feito |
| 12 | pagina/index.html (+ pagina/montar_pagina.py, que a gera) | feito; publicar é com a gerente |

## Falta (gerente)

1. Revisar e juntar o ramo ao `fase-1` (só acrescenta a pasta `memoria/` e `tests/test_conferir_memoria.py`).
2. Publicar `memoria/pagina/index.html` no claude.ai. Antes, gerar de novo:
   `.venv\Scripts\python.exe memoria\pagina\montar_pagina.py` (os links para fora da memória apontam para o GitHub no
   ramo `fase-1`; enquanto não juntar, use `--ramo memoria-2026-10-19`).
3. Levar ao Samuel as perguntas de `geral/perguntas-abertas.md` quando for a hora.
