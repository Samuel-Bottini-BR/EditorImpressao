# Ramos e cópias de trabalho (worktrees)

Conferido em 20/10/2026, de manhã (ramos remotos lidos com `git branch -r` depois da atualização do dia). Os ramos
"em andamento hoje" andam enquanto você lê: confira de novo com `git -C D:\programas\EditorImpressao fetch` e
`git -C D:\programas\EditorImpressao log -1 origin/<ramo>` antes de agir.

**O plano manda.** O que entra ou não no programa está no
[PLANO-DEFINITIVO](../docs/plano/PLANO-DEFINITIVO.md) (Registro de mudanças). Esta ficha só diz onde está cada coisa.

## Em uma frase

O programa de verdade é o ramo `fase-1` (pasta principal). O `master` está parado desde 28/09/2026 e só recebe o que o
Samuel aprovar. Hoje (20/10) há agentes em oito ramos próprios: os seis que o Samuel liberou em 19/10 (Pesel 21 no
corte, conferência do "Para revisar", itens da Fase 2 iguais ao ScanTailor, layout etapas 4 a 7, caixa do conteúdo e
pesquisa da impressão), mais o filtro de velocidade no GitHub e esta memória.

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
