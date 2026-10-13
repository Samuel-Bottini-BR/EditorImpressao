# Segunda conferência do "Para revisar": onde parei

Verificador, 13/10/2026 (tarde). Ramo conferido: `origin/fase2-para-revisar` em `ce2b835`, trazido para esta
worktree (`verif-para-revisar`, ramo `verif-para-revisar-2026-10-13`). A primeira conferência (commit `2d820d6`)
foi feita em `36b9e32`.

## Já conferido na janela de verdade (pasta de dados nova: `trabalho/dados_teste2`)

| Ponto | Resultado | Print bruto (`trabalho/prints`) |
|---|---|---|
| 1. Graduale 221 | Sem aviso depois de medir (antes dava "Desenho apagado") | `r2-graduale-221.png` |
| 2. Dois cliques no cartão | Abre o "Ver de perto", não grava ação, o aviso continua | `r2-duplo-clique-*.png` |
| 3. "está bom assim" (3º botão) | Egenloff 12, Gladstone 18, Rariora 8: aparece e aceita só aquele motivo; Ctrl+Z desfaz | `r2-egenloff-12-tres-botoes.png`, `r2-gladstone-18.png`, `r2-rariora-8.png` |
| 4. Teclado | Os botões do aviso não ficam com o foco; a barra de espaço faz "está certo e avança"; Tab não chega neles. A seta não troca de página na minha janela de teste, mas é igual no programa de hoje (`q2_setas.py`): não dá para confirmar a seta | `r2-teclado-depois-do-clique.png` |
| 5. Frase da lista | "Ainda tem 75 páginas que eu não tive certeza (104 avisos na lista)" (Camões) | `r2-contagens-2-lista.png` |
| 6. "usar mais escuro" | No Egenloff 3 com a força em 85 o botão não aparece mais | `r2-egenloff-3-forca-85.png` |
| 7. Força sozinha | Camões 27 e 104: age (85, "Desfazer"). Palatino 66, Egenloff 3, Camões 11: só o aviso "Texto falhado", força 50 | `r2-camoes-27.png`, `r2-palatino-66.png`, `r2-egenloff-3.png` |
| 8. Aba Marcar se acerta sozinha | Graduale 221: 9 áreas, e 18 áreas 10,7 s depois de chegar. Área marcada à mão no intervalo (página 5) continuou lá | `r2-marcar-1-antes.png` … `r2-marcar-4-a-mao-depois.png` |

As três contagens no Camões (para a `pergunta_contagens`): painel "Para revisar 39"; contador de cima "100 páginas
para você olhar"; lista "75 páginas (104 avisos na lista)"; janela de salvar "106 página(s) que você não conferiu".
Prints `r2-contagens-1-painel.png`, `-2-lista.png`, `-3-salvar.png`.

## Falta (nesta ordem)

1. As 89 páginas na ordem da janela, de novo (`scripts/conferir_89_como_a_janela.py`; apagar antes o
   `conferir-89-como-a-janela.json` antigo, guardado como `...-1a-conferencia.json`).
2. Folhear com "Só as letras" na janela, programa de hoje contra o ramo (`scripts/q4_folhear.py`, 2 rodadas de cada).
3. `teste_velocidade.py`, 2 rodadas de cada, alternando (`velocidade/rodar_uma.ps1`, saída em `velocidade/rodadas-2`).
   O "antes" é a minha worktree `.claude/worktrees/velocidade-antes-pr` (origin/fase-1, 94f71bd; junção `modelos`).
4. Refazer as imagens de `img/`, os quadros do `conferencia.json`, as três perguntas e o relatório nos três formatos.

## Cuidados

- Outro verificador (`verif-corte-g6`) rodou teste de velocidade das 13:58 às 14:49: esperei ele acabar antes de usar o PC.
- `v.fechar()` fecha primeiro o "Ver de perto" que ficar aberto (sem isso a janela de teste não fechava).
- Para desfazer a worktree `velocidade-antes-pr`: primeiro `(Get-Item …\velocidade-antes-pr\modelos).Delete()`.
