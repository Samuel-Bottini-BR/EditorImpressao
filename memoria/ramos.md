# Ramos e cópias de trabalho (worktrees)

Conferido em 20/10/2026, de manhã (ramos remotos lidos com `git branch -r` depois da atualização do dia). Os ramos
"em andamento hoje" andam enquanto você lê: confira de novo com `git -C D:\programas\EditorImpressao fetch` e
`git -C D:\programas\EditorImpressao log -1 origin/<ramo>` antes de agir.

**O plano manda.** O que entra ou não no programa está no
[PLANO-DEFINITIVO](../docs/plano/PLANO-DEFINITIVO.md) (Registro de mudanças). Esta ficha só diz onde está cada coisa.

## Em uma frase

> **Atualização de 24/10/2026 ([PARTE -20](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §1 e §3; vale sobre as atualizações abaixo):** todos os aprovados foram juntados no `fase-1` em `718454b` (ramo `juncao-fase2-2026-10-23`, worktree `juncao-23`, ponta `ff1f6cd`): `consertos-2026-10-21`, `fase2-para-revisar`, `layout-etapas4a7-2026-10-19`, `fase2-caixa-conteudo`, `fase2-scantailor-itens-2026-10-19` (`c3b66fb`), `fase2-ferramentas-2026-10-22` (`d4c820b`). **Ficou fora:** `layout-antes-de-processar-2026-10-22` (`138e425`). Ramos novos, só documentos/roteiros, **ainda fora do `fase-1`:** `mapa-do-programa-2026-10-23` (`df322a7`, worktree `mapa`) e `testes-livros-2026-10-23` (`2f5dc46`, worktree `livros`). Verificações novas: `verif-tinta-papel-2026-10-23` (`vtp23`, `vtp23-antes`), `verif-2.12-2026-10-23` (`v212`, `v212-antes`, `v212-p5`). Todas com junções: `(Get-Item <junção>).Delete()` antes de remover.

O programa de verdade é o ramo `fase-1` (pasta principal). O `master` está parado desde 28/09/2026 e só recebe o que o
Samuel aprovar. Hoje (20/10) há agentes em oito ramos próprios: os seis que o Samuel liberou em 19/10 (Pesel 21 no
corte, conferência do "Para revisar", itens da Fase 2 iguais ao ScanTailor, layout etapas 4 a 7, caixa do conteúdo e
pesquisa da impressão), mais o filtro de velocidade no GitHub e esta memória.

## Atualização de 23/10/2026 ([PARTE -19](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §2): vale mais que as tabelas abaixo

- `fase2-scantailor-itens-2026-10-19` (worktree `fase2-itens`): ponta `f60067a` (2.12 com proteção, botão e P5; parado na P6).
- `fase2-ferramentas-2026-10-22` (worktree `fase2-novas`): ponta `d4c820b` (7 ferramentas + tinta A/B + papel da área + 10/11).
- Verificações novas: `verif-caixa-2026-10-22` `65857a4`; `verif-ferramentas-2026-10-22` `eda69bb` (`vfr22-novo`, `vfr22-antes`); `verif-layout-melhorias-2026-10-22` `2f2d791` (`vlm22`, `vlm22-antes`, `vlm22-av`, `vlm22-av-antes`); `verif-tinta-2026-10-23` `a92e6ca` (`vtc23`, `vtc23-antes`); `verif-tinta-papel-2026-10-23` `097f887` (`vtp23`, pausada).
- Novo: `layout-antes-de-processar-2026-10-22` `138e425` (worktree `layout-avisos`, sai de `f54428e`).
- Todas as worktrees de verificação têm junções `modelos` e `gabarito\paginas`: tirar a junção com `(Get-Item <junção>).Delete()` antes de `git worktree remove --force`.

## Atualização de 22/10/2026 ([PARTE -18](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)): vale mais que as tabelas abaixo

| Ramo (último commit) | Situação em 22/10/2026 |
|---|---|
| `fase-1` | só documentos novos (Central, regras §4.10, Registro) |
| `fase2-para-revisar` (`f54428e`) | APROVADO; espera a junção final |
| `fase2-scantailor-itens-2026-10-19` (`8cb90a1`) | 2.8/2.9/2.11/2.15 APROVADOS (até `25504fb`); 2.12 parado na pergunta `a-212-desentortar` |
| `layout-etapas4a7-2026-10-19` (`7843503`) | layout 4 a 7 APROVADO; livro aberto UPDF + tela cheia verificados (`verif-layout-updf-2026-10-22` `40bc3ed`); conferência `lyupdf` na Central; contém o merge de `25504fb` |
| `fase2-caixa-conteudo` (`49d1ed3`) | PRONTO; verificador **pausado** em `verif-caixa-2026-10-22` (`c03f24b`, worktree `vcx22-novo`, ONDE-PAREI em `relatorios/conferir/caixa-2026-10-22/`); worktrees dele com junções: `vcx22-novo`, `vcx22-antes`, `vcx22-04b` |
| `fase2-ferramentas-2026-10-22` (`f26407c`, worktree `fase2-novas`) | 2.4, 2.6, 2.16, 2.17, 2.18, 2.19, 2.10+1.6 PRONTOS; falta o verificador e a pergunta 8 |
| `consertos-2026-10-21` (`2ff16e7`) | pronto; entra na junção final |

Worktrees de apoio a limpar (com junções): `fase2-novas-antes` (`9804b98`), `fase2-novas-prova` (`c9f3335`).

## Atualização de 21/10/2026 ([PARTE -17](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)): vale mais que a tabela de 20/10 abaixo

Tudo parou em 21/10/2026 (pausa pedida pelo Samuel), com commit, push e `ONDE-PAREI.md` em dia. O `fase-1` está em
`e1f4c7d` (registro da pausa). **Nada foi juntado depois do conserto do corte** (`f418cc3`, 20/10/2026). Os arquivos soltos
antigos em `relatorios/` continuam sem commit; não mexer.

| Ramo (último commit) | O que é | Situação em 21/10/2026 |
|---|---|---|
| `fase-1` (`e1f4c7d`) | o programa | conserto do corte juntado (`f418cc3`); memória `memoria/` (`ccc3d6d`); regras novas; registros `31a9253`, `e1f4c7d` |
| `conserto-corte-g6-2026-10-13` (`5a84f7c`) / `juntar-corte-2026-10-20` | conserto do corte com borda preta + Pesel 21 | **juntado** (`f418cc3`) |
| `memoria-2026-10-19` (`ccc3d6d`) | a memória por assunto | **juntada** ao `fase-1` e publicada (20/10/2026) |
| `fase2-para-revisar` (`8cb84b8`) | "Para revisar" sobre o layout aprovado + frases da r14 + 2 consertos | PRONTO; aba 4 publicada, sem resposta |
| `fase2-scantailor-itens-2026-10-19` (`ffa2463`) | 2.8, 2.9 (+ cartões `e49463c`, `e3c4d49`), 2.11, 2.15, erros.log do ScanTailor, 2.12 pela metade | 2.8/2.9/2.11/2.15 PRONTOS (abas 6-8 publicadas, sem resposta); 2.12: falta antes/depois em páginas reais e ler as rodadas 39623234116 e 39623242157 |
| `layout-etapas4a7-2026-10-19` (`2eeec20`) | etapas 4 a 7 do layout + rodadas 14 e 14b + acertos de nitidez | 4-5 PRONTAS (aba 5 publicada); 6-7 PRONTAS, conferência `verif-layout-4a5-2026-10-21` (`5650a1c`) não publicada; suíte 39629275637 não lida |
| `fase2-caixa-conteudo` (`ed68928`) | 2.5 caixa do conteúdo + guias, 2.13 borda preta, 2.14 pintar de branco, tamanho do livro (`57de8af`) | conferência `verif-caixa-2026-10-21` (`f10b2df`) não publicada; aberto: etiqueta do Egenloff 3, passada 2-3× mais lenta, velocidade 39623840809 não lida |
| `consertos-2026-10-21` (`2ff16e7`) | instalador com as duas DLLs; teste dos atalhos; Gladstone 18 "Parece em branco"; Horas 11 com pouca memória | verificado até `4c53152`; falta GitHub do `2ff16e7` e a parada no PC para juntar |
| `pesquisa-impressao-2026-10-19` (`479706f`) | pesquisa da fase de impressão + relatório das 6 perguntas | entregue; perguntas publicadas (só documentos) |
| `claude/list-server-files-gkos8v` (`6f6fe76`) | workflow com o filtro de velocidade `velocidade_ab` | **adotado**; provado com versão lenta de propósito |
| `teste-filtro-lento-2026-10-20` | a versão lenta de propósito que provou o filtro | **NUNCA JUNTAR** |

**Ramos de verificação** (todos só relatórios): `verif-para-revisar-2026-10-13`, `verif-pesel21-2026-10-20`,
`verif-2.8-2026-10-20`, `verif-2.9-2026-10-21`, `verif-2.11-2.15-2026-10-21`, `verif-caixa-2026-10-21`,
`verif-layout-4a5-2026-10-21`, `verif-consertos-2026-10-21`.

**Worktrees novas** em `.claude\worktrees\` (v28-*, v29-*, v211, vcx-*, vcs-*, vly-*, pr-*, fase1-*, juntar-corte,
fase2-itens, layout-4a7, consertos-2026-10-21, filtro-velocidade, memoria, pesquisa-impressao, teste-filtro-lento):
**as junções `modelos` e `gabarito` se removem com `(Get-Item …).Delete()` antes de apagar qualquer worktree** (lição D2).
Para continuar uma frente numa conversa nova, chame um agente novo apontando o ramo, a worktree e o `ONDE-PAREI.md` dela.
## Tabela-resumo

"No fase-1?" = `git merge-base --is-ancestor origin/<ramo> origin/fase-1` (SIM = tudo o que o ramo tem já está no
programa). "+A/−B" = commits que o ramo tem e o `fase-1` não / que o `fase-1` tem e o ramo não.

| Ramo | Último commit | No fase-1? | +A/−B | Situação | Itens |
|---|---|---|---|---|---|
| `fase-1` | `b8e9af7` 20/10 Regras de 19/10 | é ele | 0/0 | **o programa** (pasta principal) | todos |
| `master` | `44c86a4` 28/09 Plano: seguir para a Fase 1 sem esperar aprovação | SIM | 0/−454 | parado; só recebe o aprovado | — |
| `conserto-corte-g6-2026-10-13` | `3e1cc3a` 20/10 Junta o fase-1 ao conserto do corte | não | +5/0 | **em andamento hoje** (Pesel 21) | [2.2](itens/2.2.md), [2.13](itens/2.13.md) |
| `fase2-caixa-conteudo` | `a67e1f0` 20/10 Merge origin/fase-1 | não | +5/0 | **em andamento hoje** (caixa do conteúdo e borda preta) | [2.13](itens/2.13.md), [2.5](itens/2.5.md), [2.4](itens/2.4.md) |
| `fase2-scantailor-itens-2026-10-19` | `c02d9b9` 20/10 ONDE-PAREI do trabalho | não | +1/0 | **em andamento hoje** (novo) | [2.8](itens/2.8.md), [2.9](itens/2.9.md), [2.11](itens/2.11.md), [2.15](itens/2.15.md), [2.12](itens/2.12.md), [2.16](itens/2.16.md), [2.19](itens/2.19.md), [2.17](itens/2.17.md) |
| `layout-etapas4a7-2026-10-19` | `a1d796c` 20/10 começo do ONDE-PAREI | não | +1/0 | **em andamento hoje** (novo) | [layout](itens/layout.md) |
| `pesquisa-impressao-2026-10-19` | `c522919` 20/10 começo e ONDE-PAREI | não | +1/0 | **em andamento hoje** (novo) | [2.6](itens/2.6.md), [2.4](itens/2.4.md), [6.5](itens/6.5.md), [6.6](itens/6.6.md) |
| `claude/list-server-files-gkos8v` | `0e614f5` 20/10 Filtro de velocidade: ONDE-PAREI | não | +14/−64 | **infraestrutura**; em andamento hoje (filtro de velocidade) | testes e velocidade ([0.5](itens/0.5.md)) |
| `verif-para-revisar-2026-10-13` | `119b648` 20/10 retomada da segunda conferência | não | +25/−39 | **em andamento hoje** (verificador) | [para-revisar](itens/para-revisar.md) |
| `memoria-2026-10-19` | `9e8c5d5` 20/10 Memória, parte 0 | não | +1/0 | **em andamento hoje** (este trabalho) | [INDICE](INDICE.md) |
| `fase2-para-revisar` | `ce2b835` 13/10 marcação procurada por trás | não | +19/−39 | pronto, não juntado | [para-revisar](itens/para-revisar.md) |
| `fase2-geometria-perguntas` | `0701e8b` 13/10 caixas refeitas com o DPI do programa | não | +7/−38 | parado (perguntas publicadas) | [2.13](itens/2.13.md), [2.5](itens/2.5.md), [2.4](itens/2.4.md), [2.6](itens/2.6.md) |
| `verif-corte-g6-2026-10-13` | `d9bc9c6` 13/10 tira o `__pycache__` | não | +12/−34 | parado (relatórios prontos) | [2.2](itens/2.2.md) |
| `dados-de-teste` | `a627665` 09/10 marial_300.pdf | não (ramo à parte) | +2/−564 | **infraestrutura** (gaveta do GitHub) | testes |
| `prints-testes` | `2256b13` 15/10 prints do fase-1 | não (ramo à parte) | +26/−564 | **infraestrutura** (prints da janela) | testes |
| `conferir-09-10` | `878654b` 09/10 pergunta em cada quadro | não | +2/−59 | parado (superado em 12/10) | [2.2](itens/2.2.md), [layout](itens/layout.md) |
| `fase2-endireitar` | `9a9b2d0` 06/10 EM ANDAMENTO (interrompido) | não | +1/−122 | parado (substituído pelo `fase2-endireitar-2`) | [2.2](itens/2.2.md) |
| `verif-recomeco-2026-10-07` | `605e94b` 07/10 Merge recomeco-historico | não | +1/−78 | parado (só a junção; nada a juntar) | [bugs](bugs.md) |
| `layout-impl-2026-10-08` | `e94fe8c` 13/10 "a do Editor" | SIM | 0/−20 | juntado (14/10, `ccc84aa`) | [layout](itens/layout.md) |
| `juntar-layout3-2026-10-13` | `3bdbab3` 14/10 velocidade do layout juntado | SIM | 0/−10 | juntado | [layout](itens/layout.md) |
| `juntar-g6-2026-10-12` | `4a7f288` 12/10 Junta o G6 | SIM | 0/−40 | juntado | [2.2](itens/2.2.md) |
| `fase2-endireitar-2` | `98c9b5e` 12/10 velocidade do G6 | SIM | 0/−57 | juntado | [2.2](itens/2.2.md) |
| `plano-09-10` | `c618c3b` 12/10 Checkpoint 09-12/10 | SIM | 0/−55 | juntado | plano |
| `conserto-conftest-2026-10-08` | `9ec0494` 08/10 relatório do conftest | SIM | 0/−63 | juntado (09/10, `a358d4e`) | [bugs](bugs.md) |
| `juntar-recomeco-2026-10-07` | `5ecc4dc` 08/10 layout etapa 1 | SIM | 0/−65 | juntado | [2.2](itens/2.2.md), [layout](itens/layout.md) |
| `nomes-rodada10-2026-10-07` | `62d01e8` 07/10 nomes da rodada 10 | SIM | 0/−78 | juntado | [2.7](itens/2.7.md), [1.5](itens/1.5.md), [layout](itens/layout.md) |
| `juntar-dividir-2026-10-07` | `8ca1e4b` 07/10 relatório da junção | SIM | 0/−88 | juntado | [2.1](itens/2.1.md), [2.7](itens/2.7.md) |
| `recomeco-historico` | `52ef2b0` 06/10 Ctrl+Z recomeça vazio | SIM | 0/−119 | juntado (08/10) | [bugs](bugs.md) |
| `fase2-dividir` | `eebe358` 06/10 parecer 2ª rodada | SIM | 0/−122 | juntado (07/10) | [2.1](itens/2.1.md) |
| `consertos-06-10` | `6e8bf27` 06/10 parecer | SIM | 0/−128 | juntado | [bugs](bugs.md), [2.3](itens/2.3.md) |
| `fase2-misto-opcoes` | `a755087` 06/10 limpar pontinhos ligado | SIM | 0/−136 | juntado (07/10) | [2.7](itens/2.7.md) |
| `girar-aplicar-copia` | `7c8c032` 06/10 parecer do "aplicar em" | SIM | 0/−142 | juntado | [2.3](itens/2.3.md) |
| `misto-desenho-apagado` | `03b73eb` 06/10 parecer | SIM | 0/−158 | juntado | [1.5](itens/1.5.md) |
| `fase2-geometria` | `5b58e07` 06/10 parecer verificador-3 do girar | SIM | 0/−169 | juntado | [2.3](itens/2.3.md) |
| `fase2-misto` | `c9eb3ad` 06/10 parecer (2) | SIM | 0/−206 | juntado | [1.5](itens/1.5.md) |
| `pedaco-e-salvo-2-2026-10-05` | `3cf1500` 05/10 relatório (3) | SIM | 0/−218 | juntado (06/10) | [bugs](bugs.md) |
| `consertos-cancelar-pedaco-2026-10-05` | `0b4f9e7` 05/10 parecer | SIM | 0/−235 | juntado | [bugs](bugs.md) |
| `consertos-janela-2026-10-05` | `e10c4c8` 05/10 parecer | SIM | 0/−249 | juntado | [bugs](bugs.md) |
| `fase-0` | `d621484` 26/09 CLAUDE.md: 666 testes | SIM | 0/−461 | juntado (só história) | Fase 0 ([0.4](itens/0.4.md), [0.5](itens/0.5.md)) |
| `trabalho-17-a-23-09` | `b15ac31` 25/09 Cópia de segurança | SIM | 0/−467 | **só cópia de segurança** | [0.1](itens/0.1.md) |

Total: 40 ramos remotos (fora `origin/HEAD`). 24 dão "SIM" (contando o próprio `fase-1`); 16 não.

## Como criar uma worktree nova

Juntado das regras de 06 a 08/10/2026 ([histórico, PARTE -13 §0 e PARTE -12 §0](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md);
[plano, Registro 07/10/2026 e 08/10/2026](../docs/plano/PLANO-DEFINITIVO.md); `.claude/agents/*.md`, "Apagar arquivo ou pasta").

1. **Ramo novo a partir do `origin/fase-1`**, na pasta `.claude\worktrees\<nome>`. Todos os ramos de 19-20/10 nasceram
   assim (`b8e9af7`). Exemplo das fontes: `git worktree add .claude/worktrees/layout -b layout` (`.claude/agents/layout.md`).
   Para só rodar uma versão (sem ramo), o verificador usa HEAD solta:
   `git worktree add --detach .claude/worktrees/verificador HEAD` (histórico, PARTE -9).
2. **Junções para o que fica fora do git**: `modelos`, `gabarito\paginas` e `gabarito\scantailor-24-09`, cada uma
   apontando para a mesma pasta em `D:\programas\EditorImpressao`. Sem elas os testes de OCR, de gravura e de gabarito
   pulam sem avisar (Lista de bugs, 05/10/2026: "~87" testes pulam numa cópia). O comando exato usado pelos agentes
   não está escrito nas fontes lidas; o comum no Windows é
   `New-Item -ItemType Junction -Path <worktree>\modelos -Target D:\programas\EditorImpressao\modelos`.
3. **TEMP, TMP e `--basetemp` dentro da worktree** (ex.: `$env:TEMP="$PWD\_tmp"`). No máximo 3 a 4 agentes ao
   mesmo tempo; **um arquivo de pytest por vez**; esperar enquanto houver menos de 3 GB de memória livre
   (PARTE -13 §0: em 07/10/2026 quatro agentes esgotaram os 15 GB e o Claude Code caiu).
4. **Push só no próprio ramo**, depois de cada commit. O push do `fase-1` é só da gerente (Registro 08/10/2026).
   A pasta principal só avança com o ok do Samuel ("pode atualizar o programa", PARTE -13 §0).
5. **Testes inteiros no GitHub**, não no PC:
   `gh workflow run "Testes no Windows" -R Samuel-Bottini-BR/EditorImpressao --ref claude/list-server-files-gkos8v -f ramo=<ramo>`
   ([CLAUDE.md §4.6](../CLAUDE.md)).
6. Escrever um `ONDE-PAREI.md` no ramo logo no começo (todos os agentes de 20/10 fizeram) e mantê-lo em dia.

## Cuidados com as junções (leia antes de apagar ou mover qualquer coisa)

- **Nunca `Remove-Item -Recurse` (nem `rm -rf`) numa worktree.** No PowerShell 5.1 ele atravessa a junção e apaga
  a pasta de verdade (`modelos\`, `gabarito\`), que não está no git.
- **Para desfazer uma junção:** `(Get-Item <junção>).Delete()`, conferir que a pasta original continua inteira, e só
  então `git worktree remove --force` (PARTE -9; `.claude/agents/implementador.md`).
- **Nunca mover árvore de pastas sem listar as junções antes.** Em 07/10/2026 um `robocopy /MOVE` **sem `/XJ`**
  seguiu as junções de um scratchpad e esvaziou `modelos\` (18 arquivos) e `gabarito\paginas\` +
  `scantailor-24-09\` (117 arquivos) das 19h20 às 22h; foi restaurado da cópia no D: (Registro 07/10/2026;
  PARTE -13 §0).
- **Regra de apagar (Samuel, 29/09/2026):** dentro do projeto, só o que o próprio agente criou na tarefa; fora do
  projeto, nada sem perguntar ([CLAUDE.md §10 item 9](../CLAUDE.md)). Nenhuma worktree antiga foi liberada para
  apagar: a Lista de espera de 05/10/2026 diz, sobre a do verificador, "Vamos apagar mais para frente".

## As worktrees (29, contando a pasta principal)

Lista de `git worktree list` em 20/10/2026. Junções listadas com
`Get-ChildItem <pasta> -Attributes ReparsePoint -Recurse -Depth 2` (só até 2 níveis; pode haver mais fundo).
"3 junções" = `modelos`, `gabarito\paginas`, `gabarito\scantailor-24-09`, todas apontando para a pasta principal.

| Pasta (`D:\programas\EditorImpressao\...`) | Ramo ou HEAD solta | Para que serve | Junções |
|---|---|---|---|
| *(pasta principal)* | `fase-1` `b8e9af7` | o programa; o atalho "(desenvolvimento)" abre daqui | nenhuma |
| `.claude\worktrees\conserto-corte-g6` | `conserto-corte-g6-2026-10-13` | conserto do corte com borda preta; hoje, o Pesel 21 | 3 |
| `.claude\worktrees\caixa-conteudo` | `fase2-caixa-conteudo` | caixa da página e do conteúdo do ScanTailor (2.13, 2.5) | 3 |
| `.claude\worktrees\fase2-itens` | `fase2-scantailor-itens-2026-10-19` | Fase 2 a partir do 2.8, igual ao ScanTailor | 3 |
| `.claude\worktrees\layout-4a7` | `layout-etapas4a7-2026-10-19` | rodada 14 e etapas 4 a 7 do layout | 3 |
| `.claude\worktrees\pesquisa-impressao` | `pesquisa-impressao-2026-10-19` | pesquisa da fase de impressão | nenhuma |
| `.claude\worktrees\filtro-velocidade` | `claude/list-server-files-gkos8v` | workflow do GitHub e filtro de velocidade | nenhuma |
| `.claude\worktrees\verif-para-revisar` | `verif-para-revisar-2026-10-13` | 2ª conferência do "Para revisar" (retomada 20/10) | 3 |
| `.claude\worktrees\memoria` | `memoria-2026-10-19` | esta memória | nenhuma |
| `.claude\worktrees\para-revisar` | `fase2-para-revisar` | o "Para revisar" (pronto, não juntado) | 3 |
| `.claude\worktrees\verif-corte-g6` | `verif-corte-g6-2026-10-13` | investigação do corte do G6 e conferência do conserto | 3 |
| `.claude\worktrees\verif-conserto-corte-g6` | HEAD solta `d97b937` | cópia do conserto do corte, só para rodar (criada pelo verificador em 13/10) | `modelos` |
| `.claude\worktrees\velocidade-antes` | HEAD solta `1d37f8f` (fase-1 de 13/10) | o "antes" das medidas de velocidade alternadas (12 e 14/10) | `modelos` |
| `.claude\worktrees\velocidade-antes-pr` | HEAD solta `94f71bd` (fase-1 de 13/10) | o "antes" da velocidade do "Para revisar" (verificador, 13/10) | `modelos` |
| `.claude\worktrees\geometria-perguntas` | `fase2-geometria-perguntas` | perguntas G7 a G10 (publicadas) | 3 |
| `.claude\worktrees\juntar-layout3` | `juntar-layout3-2026-10-13` | junção do layout; o "depois" da velocidade de 14/10 | `modelos` |
| `.claude\worktrees\layout-impl` | `layout-impl-2026-10-08` | layout etapas 2 e 3 (juntado) | nenhuma |
| `.claude\worktrees\juntar-g6` | `juntar-g6-2026-10-12` | junção do G6 (feita) | nenhuma |
| `.claude\worktrees\endireitar` | `fase2-endireitar-2` | endireitar do ScanTailor e G6 (juntado) | 3 |
| `.claude\worktrees\juntar-recomeco` | `juntar-recomeco-2026-10-07` | junções de 07-08/10 (feitas) | 3 |
| `.claude\worktrees\juntar-dividir` | `juntar-dividir-2026-10-07` | junção do dividir e do limpar pontinhos (feita) | 3, mais `saida_teste\copia-botoes\modelos` |
| `.claude\worktrees\nomes` | `nomes-rodada10-2026-10-07` | nomes da rodada 10 (juntado) | 3 |
| `.claude\worktrees\verif-recomeco` | `verif-recomeco-2026-10-07` | verificação do recomeço (feita) | 3 |
| `.claude\worktrees\conserto-conftest` | `conserto-conftest-2026-10-08` | conserto do `erros.log` dos testes (juntado) | 3 |
| `.claude\worktrees\consertos` | `recomeco-historico` | Ctrl+Z no recomeço (juntado) | 3 |
| `.claude\worktrees\misto` | `fase2-misto-opcoes` | DLL comum + limpar pontinhos (juntado) | 3 |
| `.claude\worktrees\geometria` | `fase2-endireitar` (atenção: não é o `fase2-geometria`) | começo do endireitar, interrompido em 06/10 | 3 |
| `.claude\worktrees\consertos2` | `consertos-cancelar-pedaco-2026-10-05` | consertos de 05/10 (juntado) | `modelos`, `saida_teste`, `gabarito\paginas` |
| `.claude\worktrees\consertos3` | `pedaco-e-salvo-2-2026-10-05` | consertos do pedaço (juntado) | `modelos`, `saida_teste`, `gabarito\paginas`, `gabarito\scantailor-24-09` |

Sem junção (até 2 níveis): pasta principal, `pesquisa-impressao`, `filtro-velocidade`, `memoria`, `layout-impl`,
`juntar-g6`. Nas `consertos2` e `consertos3`, **`saida_teste` também é junção** para a pasta principal: cuidado em
dobro ao limpar saídas de teste ali.

## Os ramos, um por um

### Ramos especiais

**`master`** — `44c86a4` (28/09/2026, "Plano: seguir para a Fase 1 sem esperar aprovação item a item (ramo
fase-1)"). Está inteiro dentro do `fase-1` e **454 commits atrás** dele. Nada foi levado ao `master` desde então.
Regra: Registro 28/09/2026, "Seguir sem esperar a aprovação item a item": "cada item vira um commit separado no ramo
`fase-1`, que vai ao GitHub; o ramo principal (`master`) só recebe o que o Samuel aprovar, e o que ele recusar é
desfeito no ramo antes de juntar". Registro 01/10/2026 repete: "o `master` só recebe o que o Samuel aprovar".
Decisão O4 do Samuel (Registro 02/10/2026): "**O4:** limpar os 48 MB juntando o trabalho aprovado num commit só ao
levar ao master." Ainda não feito. Itens já aprovados `[x]` que esperam ir ao `master`: 0.1, 0.3, 0.4, 0.5, 0.7,
1.1, 1.2, 1.3 (seção 4 do plano).

**`fase-1`** — `b8e9af7` (20/10/2026, regras de 19/10). É o programa da pasta principal, que o Samuel abre pelo
atalho "(desenvolvimento)". Push só da gerente. Últimas entradas: layout etapas 2 e 3 (`ccc84aa`, 14/10) e as regras
de 19/10. Continua no programa o defeito do corte do G6 (faixa preta em página torta com borda preta), com conserto
em ramo. Tem um `relatorios/layout-impl/ONDE-PAREI.md` herdado do ramo do layout (13/10), que fala do trabalho já
juntado.

**`claude/list-server-files-gkos8v`** — `0e614f5` (20/10). **Infraestrutura.** Guarda o workflow "Testes no
Windows" (`.github/workflows/testes-windows.yml` e `.github/scripts/`), que só existe neste ramo (o `fase-1` não tem
`.github/`). Saiu do `fase-1` em `4bf3888` (08/10). Desde 20/10 tem o **filtro de velocidade** (modo
`velocidade_ab`, `.github/scripts/velocidade_ab.py`). Não é para juntar ao `fase-1`: dispara-se com
`--ref claude/list-server-files-gkos8v -f ramo=<ramo>`. Commits do filtro levam `[skip ci]`.
`ONDE-PAREI-filtro-velocidade.md` (20/10): feitos os passos 1 a 4 (script, conferência com os números do PC de 14/10
dando "igual", modo novo no workflow); faltam 5 (rodada curta 39394176019, disparada 20/10 08:32 UTC), 6 e 7
(validação: antes `1d37f8f`, depois `3bdbab3`), 8 (controle com o mesmo commit dos dois lados) e 9 (entrega à
gerente). Ressalva anotada: a regra do veredito dá uns 3% de "falso lento" por medida; se acusar lentidão, repetir.

**`dados-de-teste`** — `a627665` (09/10). **Infraestrutura**, ramo à parte (sem história em comum com o
`fase-1`): cópia somente leitura de `gabarito/` e `modelos/` para o Windows do GitHub (`12bbb01`) e o livro do teste
de velocidade `marial_300.pdf` (71 MB). Fica de fora `gabarito/scantailor-24-09/out/horas_p047.tif` (154 MB).
Nunca juntar (Registro 09/10/2026).

**`prints-testes`** — `2256b13` (15/10). **Infraestrutura**, ramo à parte: o workflow grava aqui os prints da
janela real de cada rodada, numa pasta `<data>_<hora>_<commit>_<ramo>`. O último é do `fase-1` (rodada
38662254297). Os prints citados na [Lista de bugs](bugs.md) de 09 e 12/10 estão aqui. Nunca juntar.

**`memoria-2026-10-19`** — `9e8c5d5` (20/10). Este trabalho: a pasta `memoria/` (CLAUDE.md §4.9). Saiu do `fase-1`
em `b8e9af7`. `memoria/ONDE-PAREI.md`: parte 0 feita, partes 1 a 12 a fazer (no começo do dia).

### Em andamento hoje (agentes liberados pelo Samuel em 19/10/2026)

Liberação, palavras dele (Registro 19/10/2026): "Implementador 1 - ok / Verificador - ok / Implementador 3 - ok /
Agente de layout - ok / Implementador 4 - ok / Pesquisador - ok".

**`conserto-corte-g6-2026-10-13`** — `3e1cc3a` (20/10, "Junta o fase-1 (b8e9af7...) ao conserto do corte, sem
conflito"). Não está no `fase-1`. Conserto da faixa preta que o G6 trouxe em página torta com borda preta
(`d97b937`, 13/10). O Samuel marcou **"Melhorar"** (Registro 13/10/2026) e a decisão `cg6` foi reaberta até acertar
o **Pesel 21** (Registro 14/10/2026). `relatorios/conserto-corte-g6/ONDE-PAREI.md` (13/10, ainda não atualizado
hoje): PRONTO PARA CONFERIR; mudou `core/recortar.py` (bloco "A cunha do giro") e uma chamada em `core/pipeline.py`;
falta o verificador olhar as imagens e o teste de velocidade; Escola 197 e `_apagar_riscas_de_dobra` ficaram fora.
Hoje: implementador 1 acerta o Pesel 21. Itens: [2.2](itens/2.2.md), [2.13](itens/2.13.md).

**`fase2-caixa-conteudo`** — `a67e1f0` (20/10, merge do `fase-1`). Busca de página e caixa do conteúdo do
ScanTailor na `st_ferramentas.dll` (interface versão 4) e `core/caixas_scantailor.py`, **não ligadas a nada**.
`relatorios/caixa-conteudo-impl/ONDE-PAREI.md` (12-13/10): PRONTO PARA CONFERIR por máquina (76 testes); o que
falta para ligar depende da resposta `g7-borda-ate-onde` (aberta). Hoje: implementador 4 ("caixa do conteúdo e
borda preta, ligando o corte só depois da `g7`", Registro 19/10/2026). Detalhe em
[referencias/scantailor.md](referencias/scantailor.md). Itens: [2.13](itens/2.13.md), [2.5](itens/2.5.md), [2.4](itens/2.4.md).

**`fase2-scantailor-itens-2026-10-19`** — `c02d9b9` (20/10). Novo. Fase 2 a partir do 2.8, igual ao ScanTailor
(regra de 13/10/2026). `relatorios/fase2-itens/ONDE-PAREI.md` (20/10): ordem 2.8 → 2.9 → 2.11 → 2.15 → 2.12 → 2.16 →
2.19 → 2.17; **2.8 em andamento**, os outros não começados. Atenção anotada lá: aqui a DLL `st_ferramentas` sobe
para a **versão 5**, para não brigar com a versão 4 do `fase2-caixa-conteudo`; quem juntar os dois tem de recompilar
(`compilar_st_ferramentas.py`).

**`layout-etapas4a7-2026-10-19`** — `a1d796c` (20/10). Novo. `relatorios/layout-4a7/ONDE-PAREI.md` (20/10):
tarefa 1, rodada 14 de perguntas, "começando"; tarefa 2, etapas 4 a 7, "não começada". Só mexe em `ui/`; não desfaz
os controles mínimos que o agente da Fase 2 puser nos painéis. Item: [layout](itens/layout.md).

**`pesquisa-impressao-2026-10-19`** — `c522919` (20/10). Novo. Só documentos em `docs/pesquisa/`.
`docs/pesquisa/ONDE-PAREI-impressao.md` (19-20/10): já leu a explicação de 14/10 e as 5 fotos; achou o embaralhador
antigo (ver [referencias/embaralhador.md](referencias/embaralhador.md)). Falta: pesquisar cada opção do UPDF e como
fazer com PyMuPDF; escrever `docs/pesquisa/fase-impressao.md` nos três formatos; entregar à gerente.

**`verif-para-revisar-2026-10-13`** — `119b648` (20/10, "retomada da segunda conferência"). O ONDE-PAREI
(`relatorios/conferir/para-revisar-2026-10-13/ONDE-PAREI.md`, retomada de 20/10): 1. as 19 imagens abertas (feito);
faltam 2. reabrir Opus Majus 20, Antiphon 260, Cursus 3 e Camões 66 na janela; 3. escrever o teclado; 4. aba 4 da
conferência; 5. parecer. **Achado grave anotado lá hoje:** as fotos são da tela de antes do layout aprovado (no
`fase-1` desde 14/10), e juntar o `fase-1` ao `fase2-para-revisar` dá conflito em `ui/tela_conferir.py` e
`ui/widgets/paineis.py`. Velocidade: não medir (Mágico pro +1,1% foi para a Fase 5).

### Prontos, não juntados

**`fase2-para-revisar`** — `ce2b835` (13/10). O bloco "Decidido pelo Samuel, a fazer: o 'Para revisar'" (seis
pedaços). `relatorios/para-revisar-impl/ONDE-PAREI.md`: PRONTO PARA CONFERIR; regra com limites reacertados
(1,5 → 1,2 e 0,20 → 0,13): 21 vão / 78 certas no preparo antigo, 22 / 75 no novo. Esperando a 2ª conferência do
verificador (acima) e três perguntas ao Samuel (medir o livro inteiro; contagens; tela igual ao PDF). Conserta também
o `_escolher_forca` da [Lista de bugs](bugs.md). Item: [para-revisar](itens/para-revisar.md).

### Parados

**`fase2-geometria-perguntas`** — `0701e8b` (13/10). As seis perguntas de geometria (G7 a G10) e a pesquisa do
ScanTailor; imagens refeitas com o DPI do programa. Leva dentro o `fase2-caixa-conteudo` de 13/10. Tem uma cópia do
`relatorios/caixa-conteudo-impl/ONDE-PAREI.md`. Perguntas publicadas; nada a juntar além de relatórios.

**`verif-corte-g6-2026-10-13`** — `d9bc9c6` (13/10). Investigação das 89 páginas (`relatorios/conferir/corte-g6-2026-10-13/`)
e conferência do conserto (`.../conserto-corte-g6-verificado-2026-10-13/ONDE-PAREI.md`: "Terminado"). Só relatórios.

**`conferir-09-10`** — `878654b` (09/10). Página de conferência de 09/10 (G6 e layout etapa 2). Superada: a do G6
foi respondida em 12/10 e a da etapa 2 foi "dada por desatualizada" (Registro 12/10/2026).

**`fase2-endireitar`** — `9a9b2d0` (06/10, "EM ANDAMENTO (interrompido pelo Samuel em 06/10)"). Começo do
endireitar do ScanTailor; nada conferido. O trabalho recomeçou e entrou pelo `fase2-endireitar-2`. A worktree
`geometria` está neste ramo.

**`verif-recomeco-2026-10-07`** — `605e94b` (07/10). Só a junção do `recomeco-historico` para verificar; o
`recomeco-historico` entrou no `fase-1` em 08/10 (merge `d198081`). Nada a juntar.

### Já juntados (história)

Todos com "No fase-1? SIM" na tabela. Destaques:

- **`conserto-conftest-2026-10-08`** (`9ec0494`): juntado em 09/10 pelo merge `a358d4e` ("Samuel, 09/10: autorizou
  juntar ao programa", mensagem do commit). **A Lista de bugs ainda diz "não juntado"** (linha de 08/10): está
  desatualizada; ver [bugs.md](bugs.md).
- **`trabalho-17-a-23-09`** (`b15ac31`, 25/09): **só cópia de segurança** do trabalho sem commit de 17 a 23/09
  (item 0.1; Registro 25/09/2026: "O ramo `trabalho-17-a-23-09` fica só como cópia de segurança").
- **`fase-0`** (`d621484`, 26/09): o ramo da Fase 0, inteiro no `fase-1`.
- `layout-impl-2026-10-08`, `juntar-layout3-2026-10-13` (layout, 14/10); `fase2-endireitar-2`, `juntar-g6-2026-10-12`
  (G6, 12/10); `juntar-recomeco-2026-10-07`, `recomeco-historico`, `nomes-rodada10-2026-10-07` (08/10);
  `fase2-dividir`, `fase2-misto-opcoes`, `juntar-dividir-2026-10-07` (07/10); `fase2-misto`, `fase2-geometria`,
  `girar-aplicar-copia`, `misto-desenho-apagado`, `consertos-06-10`, `pedaco-e-salvo-2-2026-10-05` (06/10);
  `consertos-janela-2026-10-05`, `consertos-cancelar-pedaco-2026-10-05` (05/10); `plano-09-10` (sessão na nuvem).
  O que cada um trouxe está no Registro de mudanças, na data da junção.

## Ramos do Automático, 29-30/10/2026 (todos saíram do `obra-2026-10-26` e foram juntados nele)

| Cópia | Ramo | O que é | Junção |
|---|---|---|---|
| `.claude\worktrees\auto-marcacoes` | `automatico-marcacoes-2026-10-29` | botão "marcações" (D-578, D-580, D-584) | `5338cdc` |
| `.claude\worktrees\auto-filtro` | `automatico-filtro-2026-10-29` | investigação da D-582 (só provas e relatório) | `acd44d4` |
| `.claude\worktrees\auto-pintura` | `automatico-pintura-2026-10-29` | D-585 e "Só as letras" do Automático (só provas e relatório) | `18fe50b` |
| `.claude\worktrees\auto-respeitar` | `automatico-respeitar-gravuras-2026-10-29` | caixinha "Respeitar as gravuras achadas" (D-583, D-586, D-587) | `99a3cdc` |
| `.claude\worktrees\auto-ver` | `automatico-ver-como-fica-2026-10-29` | antes e depois na janela do Automático (D-577); `_vtmp\` (~1,1 GB, do verificador, fora do git) | `d00dcec` |

## Ramos de 30-31/10/2026 (saíram do `obra-2026-10-26`)

| Cópia | Ramo | O que é | Situação |
|---|---|---|---|
| `.claude\worktrees\auto-ver` | `automatico-ver-como-fica-2026-10-29` | D-577, 2ª a 4ª rodada (prévia nas páginas mexidas, antes cru, comparar, roda do mouse, lado da linha) | juntado: `21f7e0a`, `f39a37d`, `53a301b` |
| `.claude\worktrees\auto-cadernos` | `automatico-cadernos-2026-10-30` | D-589 (desmarcado não é feito) + D-590 ("juntar todas") | parado em `d67933f`, não juntado; falta o verificador das Gravuras e do "juntar todas" |
| `.claude\worktrees\livreto-ver` | `livreto-ver-2026-10-31` | D-574, opção 1 (ver as folhas no "Montar para imprimir") | parado em `ff0260f`, não juntado; o verificador parou no meio |

Cópias de verificador (destacadas, sem ramo, sem commit; podem ser apagadas depois de copiar os pareceres):
`verif-ver`, `verif-ver-antes`, `verif-cadernos`, `verif-cadernos-antes`, `verif-cadernos-merge`, `verif-livreto`,
`verif-livreto-antes`. Os pareceres ficam em `relatorios/.../verificador/` dentro de cada uma.

## Ramos e cópias de 31/10/2026 (noite)

| Cópia | Ramo | O que é | Situação |
|---|---|---|---|
| `.claude\worktrees\auto-ver` | `automatico-ver-como-fica-2026-10-29` | tarefa 1: D-577 comparar com opções + "usar este", D-594 todas as opções do Filtro, começa pela receita, conserto do lado esquerdo | `d0f0d72`, verificado (CUMPRE COM RESSALVAS), **não juntado** (esperando o "sim" dele) |
| `.claude\worktrees\verif-t1` / `verif-t1-antes` | (destacadas) | pareceres e scripts dos dois verificadores da tarefa 1 | sem commit; podem ser apagadas depois de copiar os pareceres |
| `.claude\worktrees\verif-gravuras` | (destacada) | criada pelo verificador da D-589 que foi parado | sem trabalho |

## Ramos e cópias de 01/11/2026

| Cópia | Ramo | O que é | Situação |
|---|---|---|---|
| `.claude\worktrees\auto-ver` | `automatico-ver-como-fica-2026-10-29` | tarefa 1 (D-577 comparar + D-594) | **juntado** no `obra-2026-10-26` (`01a1d68`); testado: "está funcionando" |
| `.claude\worktrees\zoom-mouse` | `zoom-mouse-2026-11-01` | D-599 zoom da área de trabalho para o mouse + nomes inteiros do "Mais ajustes" + Shift + roda no lado a lado | `e9f01ac`, **juntado** (`d6d6e6f`, `b43dc40`); sem verificador (a pedido dele); falta ele testar o Shift + roda |
| `.claude\worktrees\gravuras-cinza` | `gravuras-cinza-2026-11-01` | D-588 caixinha "Gravuras em tons de cinza" | `09e47d2`, **juntado** (`63fbbff`); sem verificador (a pedido dele); falta ele testar; 4 perguntas do construtor |

As três cópias têm junções `modelos` e `gabarito\paginas`: apagar com `git worktree remove`, nunca `Remove-Item -Recurse`.

## Ramos, cópias e agentes de 02/11/2026 (PAUSA a pedido do Samuel)

Para continuar **com os mesmos agentes** (sem gastar contexto de novo): retomar **esta mesma conversa** do Claude Code
(histórico do VS Code / `claude --resume`, sessão de 02/11 que começou com `/projeto`) e mandar mensagem (SendMessage) ao
id do agente. Numa conversa nova os agentes não existem mais: aí o agente novo lê o ONDE-PAREI da cópia.

| Agente (id) | Cópia | Ramo | O que é | Onde parou |
|---|---|---|---|---|
| `a49db993e3f745aea` (construtor do cinza) | `.claude\worktrees\gravuras-cinza` | `gravuras-cinza-2026-11-01` | aviso (balão) do "Gravuras em tons de cinza", texto aprovado | `relatorios/gravuras-cinza/ONDE-PAREI.md`, seção PAUSA |
| `ad9b53152639a3338` (construtor da D-574) | `.claude\worktrees\livreto-ver` | `livreto-ver-2026-10-31` | tirar o travamento da prévia do livreto (outro processo) | `relatorios/livreto-ver/ONDE-PAREI.md`, seção PAUSA |
| `a362a5e1bc6daa615` (prints da Central, Sonnet) | `.claude\worktrees\prints-central` (destacada, `6a98173`) | — | prints das 54 perguntas sem print + nomes | `relatorios/prints-central/ONDE-PAREI.md` e `mapa.json` |
| `abe0a2d12c9917ab0` (testador clicando) | `.claude\worktrees\teste-cadernos` (destacada, `6a98173`) | — | testar D-589/D-590/P4 clicando | `relatorios/teste-cadernos/LEIA-ME.md` |
| `ab2a8133fd0002828` (construtor da D-589) | `.claude\worktrees\auto-cadernos` | `automatico-cadernos-2026-10-30` | terminado e juntado (`6a98173`) | — |
| `a65f9586a0808351d` (construtor do Shift) | `.claude\worktrees\zoom-mouse` | `zoom-mouse-2026-11-01` | terminado, juntado e testado | — |
| `a4d4ad985632432b3` (verificador da D-574) | `.claude\worktrees\verif-livreto` | — | parecer entregue (`parecer.html`) | — |
| `a6b8cb7bad729666a` (investigador do endireitar) | `.claude\worktrees\investiga-inclinado` (+ `-fase1`, pode apagar) | — | entregue; ele: "parece estar tudo certo" | `relatorios/investiga-inclinado/LEIA-ME.md` |

Versão de teste (`obra-2026-10-26`) em `6a98173`+ (Livro em `640170d`). As cópias novas têm junção `modelos`: apagar só com
`git worktree remove`, nunca `Remove-Item -Recurse`.

## Agentes e cópias de 02/11/2026 (noite)

| Agente (id) | Cópia | Ramo | O que é |
|---|---|---|---|
| `a8326b31cd59aeb9c` | `.claude\worktrees\esta-certo` | `esta-certo-2026-11-02` | D-572: faixa "Página N conferida." depois do "está certo" |
| `a8778a545254480c4` | `.claude\worktrees\dividir-metade` | `dividir-metade-2026-11-02` | D-601: Dividir mostra a metade em "Uma página" |
| `a54d1b8de5ca73d1b` | `.claude\worktrees\margens-depois` | `margens-depois-2026-11-02` | Margens iguais no "depois" do Automático (D-577, D-329) |

Juntados no `obra-2026-10-26` nesta noite: balão do cinza (`99e7c6b`), D-574 sem travamento (`45b8704`). Cópias `prints-central`,
`teste-cadernos`, `investiga-inclinado`, `investiga-inclinado-fase1` terminadas (podem ser apagadas com `git worktree remove`).
| (agente da tela grande de caderno) | `.claude\worktrees\caderno-tela-grande` | `caderno-tela-grande-2026-11-02` | D-574: folhas do caderno na etapa 7 do Automático, painel "Montar cadernos" e tela grande |

## Agentes e cópias de 03/11/2026

| Agente (id) | Cópia | Ramo | O que é |
|---|---|---|---|
| `a0be25a78346e4ef1` | `.claude\worktrees\automatico-pular` | `automatico-pular-2026-11-03` (de `8846017`) | Automático pula as folhas erradas depois de folha dividida à mão (`pular` com índices antigos em `core/automatico._dividir`); Samuel: "pode chamar um agente para concertar isso" · **entregue e juntado** em `obra-2026-10-26` (`046ade5e`, 03/11) |
| `a51997f8d559dfd78` | `.claude\worktrees\dividir-caixinha` | `dividir-caixinha-2026-11-03` (de `8846017`) | D-590: caixinha do Dividir fica desmarcada depois do Rodar; só olhar (sem consertar) Endireitar, Cortar e Limpar; Samuel: "o problema 2" · **entregue e juntado** (`f5149f16`, 03/11); achados P1/P2 na Central (`conferencias/dividir-03-11`) |
| `ae2e90af4058a940e` | `.claude\worktrees\dividir-linha` | `dividir-linha-2026-11-03` (de `8846017`) | D-602: linha azul antes de cortar, "dividir todas", "jeito" vira "motor de corte", lista travada; Samuel: "nós vamos terminar esses primeiro" (D-602, D-603, D-604, um por vez) · **entregue e juntado** (`eb0df1c4`, 03/11); 6 perguntas na Central (`conferencias/dividir-03-11`) |
| `a91c58db9777e3d5b` | `.claude\worktrees\verif-03-11` | destacado em `613d6833` (obra-2026-10-26) | Verificador clicando de verdade nos 3 consertos de 03/11 (linha azul D-602, Automático depois de dividir à mão, caixinha D-590); Samuel: "você testou essas coisas clicando dentro do aplicativo?" → "Sim" |
| `aaf49ca19ba7ca34f` | `.claude\worktrees\dividir-ajustes` | `dividir-ajustes-2026-11-03` (de `75ed04af`) | D-606 (motor refaz a conta na folha juntada), D-607 (aviso do "juntar todas"), seta → depois da lista, tira depois do Ctrl+Z, "7 com dúvida", coluna cortada no Margens iguais; regra D-605; Samuel: "Sim" · **entregue** (`41359dc9`, código `abd8cd0a`, 03/11; GitHub 41759151010 passou; velocidade 41759125497 passou); 2ª parte (Ctrl+Y, D-608) `909c6055`, testes no PC; **juntado** (`1229a281`, 04/11) |
| `a1bfe001aa3299d74` | `.claude\worktrees\caderno-etapas` | `caderno-etapas-2026-11-04` (de `016ec37a`) | D-603: folhas do caderno (etapa 7) seguem as etapas marcadas antes do Rodar, montando só a folha à vista; regra D-605; Samuel: "pode começar a fazer mais esse concerto" · **entregue e juntado** (`8c40dad8`, 04/11; GitHub 41780218098; velocidade igual) |
| `ab51c85b21054d53a` | `.claude\worktrees\dividir-arrastar` | `dividir-arrastar-2026-11-04` (de `e17410fe`) | D-609: arrastar a linha azul na folha inteira, "dividir esta" corta onde ficou; regra D-605; Samuel: "sim"; + D-610 e D-611 · **entregue e juntado** (`2af68a60`, 04/11; GitHub 41788480788) |
| `ac80c97236ffce747` | `.claude\worktrees\mover-parou` | `mover-parou-2026-11-04` (de `249922d2`) | "Mover e redimensionar" para de funcionar (reproduzir pelo `acoes.jsonl` do Gradus de 04/11, achar a causa, consertar); regra D-605; Samuel: "pode colocar um agente para concertar isso" · **causa achada, sem mudar código** (vista Duas lado a lado / antes-depois cobre a ferramenta); esperando o Samuel (04/11) |
- `mover-lado-2026-11-04` (04/11): D-612, Mover funciona em “Duas lado a lado”. Completo e juntado (`152a750b`).
- `dividir-aviso-2026-11-04` (04/11): D-613, “dividir todas” pergunta sobre as folhas juntadas à mão. Entregue e juntado (`77cccc09`).
- `tira-pares-2026-11-04` (04/11): D-611 não funcionou para o Samuel no Dividir (print a-57). Entregue e juntado (`d216819d`).
- `previa-dividida-2026-11-04` (04/11): D-614, prévia do Dividir no Automático como se já tivesse dividido. Entregue e juntado (`856cc235`).
- `ordem-folhas-2026-11-04` (04/11): D-615 (arrastar a miniatura muda a folha de lugar) e D-616 (caixinha da capa aberta). Agente trabalhando.
- `previa-numero-2026-11-04` (04/11): D-617, escrever o número da folha na prévia do Automático. Entregue e juntado (`fa430a85`).
- `caixinha-volta-2026-11-04` (04/11): D-590, a caixinha do Dividir volta marcada depois de usar o Dividir (print a-67). Entregue e juntado (`9ac7d433`).
- `girar-pagina-2026-11-04` (04/11): D-618, girar só a página numa folha dividida. Agente trabalhando.
- `painel-livro-2026-11-04` (04/11): D-619 e D-620. Agente trabalhando.
- `desfazer-pagina-2026-11-04` (04/11): D-621, desfazer nesta página pelo botão direito. Agente trabalhando.
- `memoria-pdf-2026-11-04` (04/11): falta de memória ao processar (causa) + D-591. Agente trabalhando.
- `caderno-numeros-2026-11-04` (04/11): D-604, números das páginas nas folhas do caderno. Agente trabalhando.
- `ordem-folhas-2026-11-04`: entregas 1 e 2 juntadas (`7af096ab`, `9d72dfb8`).
- 04/11 fim da sessão: previa-numero parte 2 juntada (`50b69a74`). Ainda trabalhando: mover-lado (clique no par, antes/depois do Mover, clicar fora, pares pela folha no Dividir), painel-livro (setinha da qualidade), girar-pagina (falta GitHub e a pergunta do "aplicar em"), memoria-pdf, desfazer-pagina (+ página em branco), caderno-numeros.
- 04/11 ~fim: os 6 agentes pausados a pedido do Samuel ("pode pausar eles, pois a sessão vai acabar"). Pontas: mover-lado `af4005d2` (0 não salvos) · painel-livro `dc998272` (2 não salvos) · girar-pagina `064b2e4e` (0) · memoria-pdf `8c952cad` (5) · desfazer-pagina `dd1fb46b` (1) · caderno-numeros `cd5dc539` (1). Ao retomar: ler o ONDE-PAREI de cada um, conferir `git status`, rodar os testes e o GitHub antes de juntar.
- 04/11 noite (sessão nova): os 6 agentes retomados (Samuel: "pode colocar os agentes para começar"). girar-pagina **entregue**: ponta `d7bea265` (junção do obra em `b23ad645`, sem conflito); GitHub 41948211799 passou inteiro; PC: test_decisoes*.py + 15 arquivos ok (test_d148 instável, passou ao repetir). Falta a resposta do Samuel à pergunta do "aplicar em" (na Central, aba "Pergunta: girar numa folha dividida"); depois, juntar.
- 04/11 noite: mover-lado **entregue**: ponta `fd2eee9e` (junção do obra `37926156`, sem conflito); só a parte do Dividir de test_decisoes_tira_em_pares/tira_pares_juntas mudou (commit `d7d08837`, autorizado, D-611); PC: 44 test_decisoes*.py + 18 arquivos ok; GitHub 41948184684: 1ª tentativa caiu por travamento do Python (access violation) em test_dividir_ajustes_03_11.py sem nenhum teste falhar, a repetição passou inteira (ressalva). Pergunta 4 (rótulo "antes: Original") na Central; código sem pendência. Falta: Samuel testar, gerente juntar.
- 04/11 noite: painel-livro **entregue** (D-619, D-620): ponta `41120c0b` (junção do obra `04b0ff8c`, sem conflito); os 2 arquivos sem commit eram a promessa P-213 da setinha e o teste dela, só acréscimo (commit `0accc9bb`); PC: 40 test_decisoes*.py + 5 arquivos ok (respeitar_gravuras falhou 1 vez por falta de memória com outros agentes rodando, passou ao repetir); GitHub 41949243543: 3331 passaram, só test_d148 (instável conhecido) falhou. Sem pergunta nova. Ressalva: em 1366 px a conta da barra de baixo sai cortada. Falta: verificador na janela real e a parada no PC.
- 04/11 noite: memoria-pdf **entregue**: causa = o livro novo inteiro ficava na memória até gravar o PDF; conserto: páginas vão a um arquivo de trabalho no disco de 64 em 64 MB (`d693a0c7`) + acréscimo só do novo (`df514cb4`, sem lentidão); Rhetorica 270 folhas: antes caía, agora pico 1674 MB; D-591 conferida; ponta `45005116` (junção do obra sem conflito); PC ok (2 falhas soltas com o PC carregado, passaram sozinhos); reversão falha no antigo; GitHub 41951184818 passou; velocidade 41951188321 igual. Sem pergunta. 2 bugs novos na Lista de bugs (imprimir agora e extrair páginas põem o PDF inteiro na memória). Falta: parada no PC e juntar.
- 04/11 noite: desfazer-pagina **entregue** (D-621, D-623): ponta `e9f19653` (junção do obra sem conflito); reversão: 9 testes da D-623 falham no antigo `ed758424`; projeto antigo do Gradus abre igual (prova em relatorios/desfazer-pagina/prova-projeto-antigo.txt); PC ok; GitHub 41949496078 falhou só um teste novo por tempo (consertado só no teste, `2222f348`), 41955321135 passou inteiro; velocidade 41949515821 igual. Sem pergunta. Ressalvas: página em branco guarda o tamanho da vizinha da hora; "voltar a página" aparece na página em branco; menu escolhido pelo teclado no piloto. Sobra fora do projeto (não apagada): scratchpad antigo base-d623 de outra sessão.
- 04/11 noite: caderno-numeros **entregue** (D-604): ponta `23d2b157` (junção do obra `9e21350b` sem conflito); conserto achado hoje: em livro de 300 páginas o texto cortava, agora desce para a linha de baixo (`12407cd7`); 7 provas, reversão falha no antigo; PC ok (2 falhas soltas com o PC carregado, passaram sozinhas); GitHub 41948429688 e 41958485208 passaram. Pergunta 1 ("páginas em branco e 61") na Central, pergunta 6 de "Perguntas novas (04/11)". "Folha 2 de 32" respondido ao Samuel na aba Respostas. Falta: verificador e juntar.
- 05/11: **verificador separado** das 6 entregas (relatorios/verificacao-04-11, commit 4c42b4bb): girar cumpre; mover-lado cumpre em parte (o "defeito A" dos rótulos do antes/depois é o comportamento da D-577 de 30/10: rótulos parados, a linha mostra o depois à esquerda; vira explicação ao Samuel no teste, não conserto); painel-livro cumpre (3 linhas de test_paineis_na_tela autorizadas na sessão de 04/11); memoria-pdf cumpre (D-591); desfazer-pagina cumpre com defeito B (página posta em branco mostra a imagem da vizinha na tela; mandado consertar); caderno-numeros cumpre com defeito C (quebra de linha começa com ':'; mandado consertar). Junção: girar-pagina e mover-lado dão conflito na mesma linha da tira em ui/tela_conferir.py (as duas linhas ficam; testar a tira de novo).
- 05/11: caderno-numeros, defeito C consertado (`b0e2edb1`): quando não cabe, a linha de baixo diz "páginas 20 e 1" sem os dois pontos; ponta `5f29d87d` (obra `d3b613b6` juntado); 9 provas, reversão falha em `23d2b157`; PC 21 arquivos ok; GitHub 41974099823 passou; seção D-637 no ONDE-PAREI.
- 05/11: girar-pagina, D-636 feita: ponta `ac36f58f` (obra `d3b613b6` juntado); 10 provas em tests/test_decisoes_girar_paginas_aplicar_em.py (8 falham no antigo `10f74f65`, as 2 da folha inteira passam nos dois, como deve); trocou só uma prova provisória dele mesmo (`18b24395`, não existe no obra); PC 41 decisoes + 16 ok; GitHub 41970202273 passou; seção D-637 no ONDE-PAREI. 2 perguntas novas: (2) "todas as páginas" não gira a folha inteira (capa aberta); (3) na folha inteira, "todas as folhas" ainda gira as divididas como folha (volta o a-70) — sugestão: página por página.
- 05/11: desfazer-pagina, defeito B consertado (`1fa0c850`): a página posta à mão aparece branca no Cortar e nos cartões, e a faixa diz "Esta página vai sair em branco...", também depois do "voltar a página"; ponta `e1b6d8eb`; 2 provas, reversão falha em `f83e5fb8`; PC ok; GitHub 41973822273 passou. Pergunta: esconder o "voltar a página" na página posta à mão? **Achado:** test_desentortar_conferir_de_novo.py::test_destino_do_socialismo_18_o_botao_traz_a_deformacao_e_aparece_a_pergunta falha (assert 2292 == 0) no próprio obra-2026-10-26 `d3b613b6`: investigar antes da junção.
- 05/11: medida de memória nos 9 livros **feita**: pico parado em todos (sobe 24 a 69 MB do começo ao fim, sem acompanhar o tamanho; no código antigo, Na escola de Jesus subiu 888 MB); nenhum caiu; 5 livros iguais byte a byte ao código antigo; Marial e Graduale em pedaço. Relatório relatorios/memoria-pdf/nove-livros (ramo memoria-pdf, `bfe98c3e`). Sobra: worktree memoria-pdf-antes (com junção modelos). Achado: Siebmacher saía com 268 páginas em agosto, hoje 134 (investigar).
- 06/11: as 6 entregas juntadas no obra pelo ramo `juntar-6-2026-11-06` (avanço direto até `51bdcb0b`; conflito da tira em `ui/tela_conferir.py` resolvido mantendo D-618 e D-611). `cunha-desentortar-2026-11-06` (D-095, D-639) juntado em `6205a813`; obra em `6904a634` no fechamento. Cópia `.claude\worktrees\teste-kaique-lusiadas` (de `51bdcb0b`) só com o resultado do teste como o Kaique, fora do git (livro com direito autoral). Nenhum ramo da fila nova criado.
