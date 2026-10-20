# Onde parei: Fase 2, itens que faltam, igual ao ScanTailor (implementador)

Pedido da gerente em 20/10/2026. Ramo `fase2-scantailor-itens-2026-10-19` (do `origin/fase-1` em `b8e9af7`),
worktree `D:\programas\EditorImpressao\.claude\worktrees\fase2-itens` (junções: `modelos`, `gabarito\paginas`,
`gabarito\scantailor-24-09` — nunca `Remove-Item -Recurse` nelas).

Regra (Samuel, 13/10): igual ao ScanTailor, ajustes de fábrica dele, desligado de fábrica quando muda a imagem.
Decisões já tomadas que valem aqui (conferência 10, 05/10, `relatorios/conferencia-samuel-2026-10-05-b.md`):
P8 (b) "Trazer os dez do ScanTailor como opções a mais"; P9 (a) caixinha por página "Letra clara em fundo escuro",
à mão; P10 (a) "letras com a cor delas" como opção desligada de fábrica.

Ordem (D1 de 02/10, depois a lista da gerente): 2.8 → 2.9 → 2.11 → 2.15 → 2.12 → 2.16 → 2.19 → 2.17.

## Estado por item

| Item | Estado | Commits | Rodada do GitHub |
|---|---|---|---|
| 2.8 preto e branco (os dez do ScanTailor) | **entregue à gerente** (falta verificador e Samuel) | `77e9446` (core), `34b3d0e` (tela), `b36b540` (script) | 39395632426: 2084 passaram, 0 falharam; botões 221 ações, 0 falhas |
| 2.9 claro no escuro | rascunho pronto, não ligado (`rascunho-2.9/`) | | |
| 2.11 cores | não começado | | |
| 2.15 páginas diferentes | não começado | | |
| 2.12 desentortar | não começado | | |
| 2.16 todos os núcleos | não começado | | |
| 2.19 unidades e perfis | não começado | | |
| 2.17 iluminação e suavizar | não começado | | |

## Anotações

- `memoria/` ainda não existe no `fase-1` (20/10): nada a ler.
- Filtro de velocidade do GitHub (antes x depois) ainda **não existe**: outro agente está montando
  (`ONDE-PAREI-filtro-velocidade.md` no ramo `claude/list-server-files-gkos8v`, passo 1 de 9).
- A DLL `st_ferramentas` também muda no ramo `fase2-caixa-conteudo` (versão 4, não juntado). Aqui a versão
  pula para 5, para não brigar; quem juntar os dois recompila a DLL (`compilar_st_ferramentas.py`).

## 2.8 — o que foi feito e onde olhar

- Os dez jeitos do ScanTailor (Otsu, Sauvola, Wolf, Fox, Window, Bradley, Grad, EdgePlus, BlurDiv, EdgeDiv), com o
  código dele (`ligacao-ferramentas/saida.cpp`, `core/preto_e_branco_scantailor.py`), como opções a mais na lista
  "Algoritmo" da aba Filtro. De fábrica continua "Automático".
- Prova de "desligado de fábrica": `2.8/somas-antigo.json` (código `b8e9af7`) = `2.8/somas-novo.json` nas 32 páginas
  do gabarito × Original, Preto e branco, Melhorar (96 de 96 iguais, ponto a ponto).
- Antes/depois (Original · Hoje · Otsu ST · Sauvola ST · Wolf ST), 32 páginas + recorte ampliado de cada:
  `relatorios/conferir/fase2-itens/2.8/` (fora do git, só neste PC). Números por página: `2.8/numeros/`.
  Script: `scripts/rodada_gabarito.py` (uma página por processo; `scripts/rodar_todas.sh` roda as 32).
- Horas 13 falhou uma vez por falta de memória do PC (outros agentes); rodada de novo sozinha, deu certo.

## 2.9 — onde parei (próximo item)

Rascunho em `relatorios/fase2-itens/rascunho-2.9/` (fora de `core/` e `tests/` para não quebrar a suíte):
`claro_no_escuro.py` (vai para `core/`), `test_claro_no_escuro.py` (vai para `tests/`) e `patch_2_9.py` (rodar da
worktree: acrescenta `ConfigPagina.claro_no_escuro`, inverte na entrada e na saída em `pipeline._filtrar`, como o
ScanTailor em `initFilterData` e no fim da saída, e põe o sufixo na assinatura da gravura só com a caixinha ligada).
Falta: aplicar, rodar os testes, a caixinha na aba Filtro (P9 (a)), o "comparar" da tela ampliada
(`ui/tela_ampliada._imagem_do_outro_filtro` chama `aplicar_filtro` direto), somas de fábrica e antes/depois
(o gabarito não tem página de letra clara em fundo escuro: procurar uma no acervo ou usar a Horas 11 invertida).
