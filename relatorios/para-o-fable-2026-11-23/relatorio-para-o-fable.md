# Relatório para o Fable: o Editor de Impressão, o atualizador, os testes à distância e o jeito de trabalhar

23/11/2026. Montado pela conversa gerente do projeto.
- As Partes 1, 2 e 3 foram escritas por dois agentes que só leram o código.
- A Parte 4 foi escrita pela gerente.
- Ninguém mudou código para fazer este relatório.

**Para que serve.** O dono do projeto, o Samuel, quer uma opinião de fora. A conclusão dele: faz um mês que cada
volta de conserto cria erros novos e obriga a refazer o caminho, e cada vez que isso acontece se escreve uma regra
nova. As perguntas estão na Parte 5.

**Como ler.** Fato e opinião estão separados: a opinião fica no fim de cada parte, marcada. Cada fato aponta o
arquivo e a linha num link fixo do GitHub, num commit que não muda. O que o autor não conferiu está escrito "não
conferi".

---

# Parte 0. Onde está cada coisa

## O repositório

- GitHub, público: https://github.com/Samuel-Bottini-BR/EditorImpressao
- No PC do Samuel: `D:\programas\EditorImpressao`, com um worktree por trabalho em `.claude\worktrees\`.

| Ramo | Commit lido | O que é |
|---|---|---|
| `obra-2026-10-26` | `0f58346a` | **a versão de teste**, o programa de hoje (Parte 1); é onde está o Livro de decisões que vale |
| `atualizador-4-consertos-2026-11-21` | `aa1963b7` (código), `046c0271` (relatório 3) | o atualizador e os testes à distância (Partes 2 e 3); ainda não juntado |
| `fase-1` | `47394b4a` | a versão oficial: tem o plano e o histórico; o código dela parou em 23/10 |

## A árvore das pastas e as dependências

Estão no anexo "Árvore, dependências e montagem do .exe", no fim deste relatório.

## Os documentos

| O quê | Caminho | Observação |
|---|---|---|
| Regras do projeto | `CLAUDE.md` | 71 KB |
| Regras de cada agente | `.claude/agents/*.md` | 4 arquivos |
| Livro de decisões | `docs/plano/DECISOES.md` no ramo `obra-2026-10-26` | 618 KB; D-001 a D-829 |
| Plano (fases, Lista de bugs, Registro) | `docs/plano/PLANO-DEFINITIVO.md` no `fase-1` | 395 KB |
| Estado atual | `docs/plano/ESTADO-ATUAL.md` no `fase-1` | |
| Memória por assunto | `memoria/INDICE.md`; o catálogo de erros em `memoria/catalogo-de-erros.md` | o catálogo só no `obra-2026-10-26` |
| Histórico das sessões | `historico/Editor de Impressao - resumo para o Claude.md` | 784 KB, a PARTE mais nova no topo |
| O porteiro (barreira automática) | `regras_dos_agentes/` e `tests/conferencias_excecoes.json` | ver Parte 4 |
| Relatórios do atualizador | `relatorios/atualizador-4/` (ONDE-PAREI e `quem-quebrou/relatorio-1..3`), no ramo do atualizador | |
| Revisão de código de 10/11 | ramo `revisao-codigo-2026-11-10`, `relatorios/revisao-codigo-2026-11-10/relatorio.md` | os 17 remendos |
| Revisões de 18/11 | ramos `revisao-atualizador-2026-11-18` e `revisao-distancia-2026-11-18` | |

## O que não está no GitHub

- **A Central de decisões e as outras páginas de conferência.** São páginas do claude.ai e só abrem na conta do
  Samuel. O código delas não está no git.
- **A cópia do plano que o Samuel edita**, em `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\`.
- **Os livros de teste**: nove livros e 2.903 folhas, que ficam fora do git.
- **As redes neurais** (`modelos/`).
- **Os comandos `/projeto` e `/checkpoint`**, que ficam na pasta do Claude Code do Samuel.

---


# Parte 1. O Editor de Impressão hoje

Escrito em 23/11/2026 pelo agente pesquisador, só lendo código e documentos (nenhuma linha mudou, nada foi rodado além
de `pytest --collect-only`). **Fato** = o que o código ou o documento diz, com apontamento. **Opinião** fica só na
última seção. O que não conferi está dito.

**Qual código.** O programa de hoje é a "versão de teste", ramo `obra-2026-10-26`, commit `0f58346a` (está no GitHub,
`origin/obra-2026-10-26`). A "versão oficial" é o ramo `fase-1` (`47394b4a`): o código dele (`core/`, `ui/`) parou em
23/10/2026; os 342 commits dele depois da separação (26/10) são só documentos, e a versão de teste tem 1206 commits a
mais, com 75 arquivos de `core/`+`ui/` diferentes (+29.584 / -1.950 linhas; 77 contando `modelos.py` e `projetos.py`). Nada da versão de teste entra na oficial
antes da conferência final do Samuel (regra D-014).

**Links.** Os links apontam para o commit `0f58346a` (o código de hoje); os marcados `bc766007:` apontam para
`bc76600779eaa753d9f3a8d3ea9fb30d412e1ae7`, o código que a revisão de 10/11 leu ("de antes"). Um "L<n>" solto depois de
um link é outra linha do mesmo arquivo. Todos os commits citados foram conferidos com `git branch -r --contains`.

## 1. Para que serve, quem usa, o fluxo

- Aplicativo de Windows (Python 3.14 + PySide6) que recupera PDFs de livros antigos escaneados e os prepara para
  reimpressão em cadernos. Projeto de preservação de livros esgotados (CLAUDE.md §1).
- Quem usa: o Kaique, impressor, sem formação técnica. Toda a tela em português, sem termo técnico.
- Critério do dono, Samuel: "Eu quero que o papel saia branco, e o desenho também saia perfeito."
- Fluxo de hoje ([main.py](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/main.py), [ui/janela_principal.py#L1-L21](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/janela_principal.py#L1-L21)): arrasta o PDF na tela inicial → o livro abre **direto
  na área de trabalho** (a tela antiga "O que fazer", `ui/tela_opcoes.py`, saiu do caminho na etapa 3, decisão D-002) com
  as páginas como vieram, em Original → o Kaique roda o **Automático** (painel ou janela grande) ou usa as ferramentas
  página a página → confere com o "Para revisar" → "Confirmar e processar" (pasta e nome) → o programa gera o PDF,
  uma página por vez → opcional: cadernos no próprio processar (`core/cadernos.impor_pdf`, [core/pipeline.py#L4695](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/pipeline.py#L4695))
  ou "Montar para imprimir" (`core/impressao.py`), que monta outro PDF com as folhas como vão para a impressora.

## 2. Telas e ferramentas

| Nome na tela | O que faz | Onde no código |
|---|---|---|
| Tela inicial (livros) | arrastar o PDF, cartões dos livros (continuar, recomeçar, renomear, tirar da lista) | [ui/tela_inicio.py#L126](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_inicio.py#L126), `ui/widgets/area_arrastar.py` |
| Área de trabalho | uma tela só, sem abas, com todas as ferramentas à vista (D-001) | `TelaConferir`, [ui/tela_conferir.py#L650](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_conferir.py#L650) (10.187 linhas); troca de ferramenta em `escolher_ferramenta` L1630 |
| Trilha de ferramentas | Dividir a folha (D), Cortar as bordas (X), Endireitar (I), Mover e redimensionar (F); marcar: Retângulo/Oval, Laço/Ponto a ponto, Pincel, Varinha mágica/Pegar tudo desta cor, Mover a área; Zoom, Mão | `GRUPOS`, [ui/widgets/trilha_agrupada.py#L122](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/widgets/trilha_agrupada.py#L122); o desenho à mão em `ui/widgets/editor_selecao.py` |
| Girar (de 90 em 90, com "aplicar em") | só esta / todas / daqui em diante / pares / ímpares | contas em [core/girar.py](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/girar.py); tela em `_girar_folhas`, [ui/tela_conferir.py#L6570](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_conferir.py#L6570); barra em `ui/widgets/barra_girar.py` |
| Painéis da direita | Para revisar, Automático, Propriedades, Filtro da página, Histórico | `NOMES_DOS_PAINEIS`, [ui/widgets/paineis.py#L88](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/widgets/paineis.py#L88); Automático em [ui/automatico.py#L689](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/automatico.py#L689) e `core/automatico.py` |
| Filtros | Original, Preto e branco, Melhorar, Mágico pro, e "Tirar o fundo" (PDF com camadas) | [core/filtros.py#L71](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/filtros.py#L71); "Só as letras" em `core/misto.py`; fundo em `core/camadas.py` e `core/fundo_tirado.py` |
| Grade "Todas as páginas" | escolher várias páginas: girar, tirar, dividir | [ui/widgets/todas_as_paginas.py#L313](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/widgets/todas_as_paginas.py#L313) |
| Tela grande e "comparar" | a página ampliada, comparando dois filtros | [ui/tela_ampliada.py#L66](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_ampliada.py#L66) |
| Filtros em tela cheia | antes/depois de cada filtro e das opções | [ui/widgets/filtros_tela_cheia.py#L369](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/widgets/filtros_tela_cheia.py#L369) |
| Desfazer nesta página | lista do desfazer só de uma página | `ui/desfazer_nesta_pagina.py` |
| Antes de processar / Confirmar | os avisos, depois pasta e nome | [ui/janela_dos_avisos.py#L87](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/janela_dos_avisos.py#L87), [ui/janela_confirmar.py#L80](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/janela_confirmar.py#L80) |
| Progresso e "Ficou pronto!" | barra, cancelar, conferência dos cadernos | [ui/tela_final.py#L48](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_final.py#L48), L122 |
| Montar para imprimir | livreto, página inteira, margens da impressora | [ui/dialogo_impressao.py#L471](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/dialogo_impressao.py#L471), `core/impressao.py`, `core/cadernos.py` |
| Configurações, menus | atalhos, temas; menus Arquivo, Editar, Ferramentas, Marcar, Filtro, Página, Ver, Painéis, Ajuda | `ui/tela_configuracoes.py`, `ui/barra_de_menu.py` |
| Atualização e testes à distância | existem (`atualizacao.py`, `ui/aviso_de_atualizacao.py`, `core/testes_a_distancia.py`, `core/windows.py`, `ui/testes_a_distancia_ui.py`); ficam com outro agente | — |

Por trás: `ui/tarefas.py` (QThread/QRunnable para análise, prévias, processar), `core/paginas_em_outro_processo.py` (dois
processos desenham as páginas do PDF, porque o PyMuPDF segura o GIL), DLLs do ScanTailor em `core/nativo/` por `ctypes`.

## 3. O caminho da página

- **Livro novo** (desde 09/10/2026): girar de 90 em 90 → dividir a folha → **endireitar a página inteira** → achar o corte
  na página reta e cortar → filtro → cadernos (a ordem do ScanTailor).
- **Projeto gravado antes de 09/10** (sem o campo): girar → dividir → **cortar** → endireitar → filtro → cadernos, igual
  ponto por ponto ao de antes.
- Quem decide: `Projeto.ordem_do_preparo`, lido só por `core/ordem_do_preparo.py` (`ORDEM_DO_LIVRO_NOVO` e
  `ORDEM_DO_PROJETO_ANTIGO`, [core/ordem_do_preparo.py#L51-L53](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/ordem_do_preparo.py#L51-L53); `endireita_antes`, L68; valor estranho cai na ordem
  antiga, L56). Quem executa: `_preparar_metade_e_geometria`, [core/pipeline.py#L627](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/pipeline.py#L627) (o desvio em L695), chamada por
  `preparar_metade` (L567). A mesma ordem tem de valer em `_matriz_folha_para_pagina`, [core/zonas_na_folha.py#L332](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/zonas_na_folha.py#L332)
  (as marcações à mão são guardadas em relação à folha original).
- Páginas tiradas do livro saem logo depois de dividir. O "Tirar o fundo" roda antes de tudo, na folha inteira do PDF.
- Prévia e PDF: `renderizar_pagina` ([core/pipeline.py#L2805](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/pipeline.py#L2805)) e `_pagina_pronta` (L4781) dentro de `processar`
  (L4641); o filtro com as opções da página em `_filtrar_a_pagina` (L3437).

## 4. Modelo de dados, gravação, desfazer

- `ConfigFolha` ([modelos.py#L42](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/modelos.py#L42), 18 campos): o que veio no PDF (dividir, posição do corte, giro, ângulo achado,
  apagada, avisos...). `ConfigPagina` ([modelos.py#L138](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/modelos.py#L138), 51 campos): o que vai sair (metade inteira/esquerda/direita,
  filtro, recorte, ângulo, os três ajustes separados `forca_preto`/`clareza_melhorar`/`intensidade_magico`, marcação,
  opções do "Só as letras", fundo tirado, giro da página...). `Projeto` (L537, 49 campos): o livro e as opções do livro.
  `Acao` (L1175): uma mudança, para o desfazer. Recorte e ângulo moram na página porque vêm depois de dividir.
- Campo novo sempre com valor que reproduz o comportamento antigo quando falta (projeto antigo abre igual).
- Gravação em `%LOCALAPPDATA%\EditorImpressao\<projeto>\`: `projeto.json` (`ARQUIVO_ESTADO`, [projetos.py#L451](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/projetos.py#L451)), gravado
  por trás num fio só (`salvar_estado_por_tras`, L475), em arquivo ao lado e trocado no fim; cópias `projeto.antigo-*`.
  O PDF do livro nunca é copiado.
- Desfazer/refazer ilimitado: `HistoricoAcoes`, [historico_acoes.py#L25](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/historico_acoes.py#L25), uma ação por linha em `acoes.jsonl`
  (sobrevive a fechar e abrir); `montar_acao` (L612) e `aplicar` (L398). Na tela, a porta oficial é
  `TelaConferir._registrar` ([ui/tela_conferir.py#L5942](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_conferir.py#L5942)); há outras (ver §8, M1).

## 5. Regras técnicas fixas (CLAUDE.md §3)

| Regra | Por quê |
|---|---|
| PySide6, nunca tkinter/customtkinter | a versão com customtkinter travava |
| Uma página por vez na memória | livro de 300 MB no acervo; provado em `tests/test_memoria_nao_cresce_com_o_livro.py` (L131, L169); com vários núcleos, uma por trabalhador ([core/pipeline.py#L4970-L4979](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/pipeline.py#L4970-L4979)) |
| Interface nunca congela | tudo que demora em QThread com cancelar (`ui/tarefas.py`) |
| Nenhuma exceção fecha a janela | `sys.excepthook` grava em `erros.log` e mostra aviso em português ([main.py#L64-L76](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/main.py#L64-L76)) |
| Nenhum emoji em rótulo | quebrou no Windows na versão anterior (`ui/estilo.py`, L3) |
| Texto de tela com acento; caminho de disco sem acento | Windows e o Kaique |
| Algoritmo consagrado, não fórmula própria | a versão com fórmula caseira dava qualidade ruim |
| Nenhum modelo generativo | não pode inventar detalhe numa gravura de 1579; rede só aponta |
| Só Python 3.14, sem rebaixar | a máquina só tem ele; o Kraken roda num Python 3.12 à parte |
| GPU GTX 1650 sem tensor cores | nada que dependa de float16 rápido |
| Erro nunca como stack trace | o Kaique não é técnico |
| GPL pode ser incorporado (17/09) | se distribuir, será grátis com código aberto; por isso o código do ScanTailor (GPL-3) está dentro |

## 6. Testes

- `pytest tests --collect-only -q` no commit `0f58346a`: **4.668 casos coletados**, de 258 arquivos `tests/test_*.py`
  (3.641 funções `def test_`; o resto vem de `parametrize`). 64 arquivos são `test_decisoes*.py`, as provas de
  comportamento das decisões do Samuel. Rodado da raiz, o pytest também entra em `relatorios/` e para em 2 erros de
  leitura (arquivos `.txt` em outra codificação); por isso contei só `tests/`.
- Mais 19 scripts `teste_*.py` soltos na raiz, fora do pytest; o principal é `teste_botoes.py` (clica em todos os botões).
- Onde rodam (CLAUDE.md §4.6): no PC, um arquivo por vez enquanto o agente trabalha; a suíte inteira e o
  `teste_botoes.py` no Windows do GitHub (`windows-latest`, Python 3.14.3, em 5 partes; `.github/workflows/testes-windows.yml`
  no ramo `claude/list-server-files-gkos8v`, commit `4008bd31`); filtro de velocidade antes/depois no GitHub; a suíte
  inteira no PC só antes de juntar na versão oficial.
- Não rodei a suíte. Não conferi quantos passam hoje.

## 7. A situação

Fontes: o Livro `docs/plano/DECISOES.md` (commit `0f58346a`) e a Lista de bugs do `PLANO-DEFINITIVO.md` (ramo `fase-1`).

- **Livro de decisões: 804 decisões** (D-001 a D-829, contadas por número único). Pela coluna "Situação": 345
  construídas, 175 não construídas, 45 pela metade, 54 "pronta para conferir", 23 "a conferir", 28 "testada pelo
  Samuel", 38 substituídas por uma mais nova, 7 descartadas; o resto são regras de trabalho e "a fazer". 8 dizem
  "falta o teste" do Samuel (ex.: D-638, D-640, D-645 do Girar; D-699 do fundo tirado; D-758). "Construída" quer dizer
  achada no código, não aprovada (aviso do próprio Livro, L17-L20).
- **Aprovado pelo Samuel no plano** (`[x]`): 8 itens, todos das fases 0 e 1 (0.1, 0.3, 0.4, 0.5, 0.7; 1.1 tirar o
  fundo, 1.2 seletor de gravura do ScanTailor, 1.3 OCRs para achar o texto, aprovados em 02/10/2026); 2 com `[~]`
  (melhorar); 29 abertos.
- **Esperando o olho dele:** a seção "Consertos esperando o olho do Samuel" do Livro (L651) lista **40 consertos** já no
  programa, com teste, que mudam o que ele vê (ex.: o corte que partia o número da página; o mesmo PDF aberto por outro
  caminho apagava o trabalho; o Ctrl+Z desfazia a ação errada depois de reabrir). Vão numa conferência só, no fim da obra.
- **Lista de bugs** (plano `fase-1`, seção 5): 273 linhas na tabela e 22 caixinhas (21 abertas). A última contagem por
  situação é de 20/10/2026 (`memoria/bugs.md`): 107 abertos, 58 consertados a conferir, 43 fechados. Não refiz essa
  contagem linha por linha.
- **Agora:** a decisão D-765 (17/11) suspendeu todo conserto do programa até o `.exe` ser entregue ao Kaique e os testes
  à distância funcionarem. O trabalho de hoje é o atualizador (ramo `atualizador-4-consertos-2026-11-21`, de outro agente).

## 8. Os ciclos de várias voltas

Fontes: a revisão de código de 10/11/2026 (ramo `revisao-codigo-2026-11-10`, commit `ab9ba273`,
`relatorios/revisao-codigo-2026-11-10/relatorio.md`, 348 linhas; leu o commit `bc766007`), o CLAUDE.md §11.10 e §11.12,
o `memoria/catalogo-de-erros.md` (só no `obra-2026-10-26`) e o `git log`. "Hoje" = conferido no `0f58346a`.

**Caso 1 — Girar.** Decisões: D-035, D-036 (06/10), D-618 (04/11), D-636 (05/11), D-638, D-640, D-645 (06-07/11), D-662
(10/11), D-666 (10/11, não construída). Commits: `1a5745dd`, `3046cc43`, `27a0498d` (06/10), `93a390ed`, `06b80752`
(04/11), `78f2e025` (05/11), `99d7d782`, `df8db4ec` (07/11), `c76d4b97` (10/11): **9 voltas**. Causa (revisão, A1): cada
decisão ganhou um caminho novo em `_girar_folhas`, escolhido pelo jeito de ver a tela, e não pelo que a folha é; a
D-662 entrou só no item "todas as folhas". Trecho ([bc766007:ui/tela_conferir.py#L6494-L6500](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/bc76600779eaa753d9f3a8d3ea9fb30d412e1ae7/ui/tela_conferir.py#L6494-L6500)):
```python
if alcance == girar.ALCANCE_TODAS:
    # D-662: no Dividir com "Duas lado a lado", numa folha dividida,
    # "todas as folhas" gira pagina por pagina, como fora do Dividir
    referencia = self._pagina_da_folha_dividida_no_dividir_em_duas()
```
**Hoje: não resolvido.** O mesmo desvio está em [ui/tela_conferir.py#L6613-L6640](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_conferir.py#L6613-L6640); a grade ainda soma o giro com
`(rotacao + giro) % 360` (L7322, L7382) em vez de `girar.nova_rotacao` ([core/girar.py#L170](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/girar.py#L170)); D-666 não construída.

**Caso 2 — "Como fica com este filtro" em três contas.** A página e o PDF passam por `_filtrar_a_pagina`; as
figurinhas do painel e o "comparar" da tela grande, por `filtro_com_as_caixinhas` ([core/pipeline.py#L3546](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/pipeline.py#L3546)), que
não vê a marcação. Voltas no mesmo ponto: `dfe3b890` (29/09, desvio para "Tirar o fundo"), `14d721ad` (05/10, desvio
para "Só as letras" **só nas figurinhas**), `e49463c0` e `e3c4d491` (21/10, as figurinhas seguem as caixinhas),
`f86b68a1` (13/11, figurinhas, comparar e chave das prévias seguem o fundo tirado, em 3 arquivos de `ui/`): **5 voltas**.
Causa (A2): a conta da tela foi copiada em versão simples, e cada defeito ganhou um desvio por caso.
**Hoje: não resolvido.** `_imagem_do_outro_filtro` ([ui/tela_ampliada.py#L304-L351](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_ampliada.py#L304-L351)) continua sem nenhuma linha do
"Só as letras"; os desvios das figurinhas seguem em [ui/tela_conferir.py#L5001](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_conferir.py#L5001), L5019, L5038.

**Caso 3 — "Usar em todas" quer dizer uma coisa em cada ferramenta.** Cortar, Dividir e Mover deixam de fora o que foi
mexido à mão (D-090); o Marcar copia a marcação desta página por cima de todas, enquanto o "todas" do Filtro (`_filtro_em_todas`, hoje
L9188) diz no comentário "nunca apaga exceção". Trecho ([bc766007:ui/tela_conferir.py#L3325](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/bc76600779eaa753d9f3a8d3ea9fb30d412e1ae7/ui/tela_conferir.py#L3325), igual desde `b15ac310`, 25/09):
```python
{"selecao": copy.deepcopy(pagina.selecao)},
```
Causa (A3): cada ferramenta escreveu o seu "aplicar em". **Hoje: não resolvido** ([ui/tela_conferir.py#L3311-L3328](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_conferir.py#L3311-L3328));
a pergunta 1 da revisão ao Samuel (devem as quatro proteger o que foi feito à mão?) não achei respondida no Livro.

**Caso 4 — Automático e "não dividir esta" juntam a folha de dois jeitos.** O botão foi refeito na etapa 4 (`4d521de0`,
27/10: uma página inteira); o Automático, escrito na etapa 3 (`4d535ab6`, 26/10), ficou com o jeito antigo (a da direita
"tirada do livro"), e o comentário dele ainda diz "como o 'não dividir esta'". A revisão provou com script: 1 página
pelo botão, 2 (uma escondida) pelo Automático, e o contador mostra "1 apagadas". Causa (A4): duas funções para o mesmo
dado. **Hoje: não resolvido** ([core/automatico.py#L932-L968](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/automatico.py#L932-L968), a linha `g.na_pagina(direita, "apagada", not
medida.dividir)` em L968; a função do botão é `campos_para_juntar`, [core/dividir_a_mao.py#L267](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/dividir_a_mao.py#L267)).

**Caso 5 — A lista "o que é do filtro" em seis lugares.** O mesmo dicionário estava copiado em `_filtro_em_todas` e
`_filtro_nas_proximas` ([bc766007:ui/tela_conferir.py#L9001](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/bc76600779eaa753d9f3a8d3ea9fb30d412e1ae7/ui/tela_conferir.py#L9001) e L9038) e, de outro jeito, em `core/automatico.py`,
`core/perfis.py`, na tela cheia, em `MARCAS_DA_PAGINA` e na chave das prévias. Já divergia: "Letra clara em fundo escuro"
(`claro_no_escuro`) vai pelo Automático e não pelo "todas" do painel. **Hoje: em parte.** Em 13/11 (`1268ae56`) as duas
cópias da tela viraram uma função, `_campos_do_aplicar_em` ([ui/tela_conferir.py#L9133-L9163](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_conferir.py#L9133-L9163)); mas `claro_no_escuro`
continua fora do `_campos_do_aplicar_em`: está em `CAMPOS_DA_PAGINA` ([core/automatico.py#L149-L154](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/automatico.py#L149-L154)) e em `MARCAS_DA_PAGINA` (L10161), e as outras listas continuam separadas.

**Caso 6 — Contraexemplo: "Tirar o fundo" que qualquer filtro desfazia.** O fundo tirado era guardado só como um valor do
filtro (`dfe3b890`, 29/09); trocar de filtro, por qualquer caminho, o perdia (D-646, 07/11). Em 13/11 virou um dado
próprio com regra única em `core/fundo_tirado.py` ([core/fundo_tirado.py#L1-L40](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/fundo_tirado.py#L1-L40), que lista os caminhos que a usam).
**Hoje: resolvido no código** (falta o teste do Samuel, D-699). Mas precisou de mais dois commits no mesmo dia
(`f86b68a1`, `4747a6a0`) para chegar às figurinhas, ao comparar, à chave das prévias, ao "Desfazer nesta página" e à
tela cheia, justamente os caminhos duplicados dos casos 2 e M1.

**Os 17 remendos da revisão de 10/11** (4 altos, 9 médios, 4 baixos), conferidos um a um no `0f58346a`:
**0 consertados por inteiro, 1 em parte (M9, caso 5), 16 continuam.** Continuam, com o lugar de hoje: A1 a A4 (casos 1 a
4); M1, o "Desfazer nesta página" ainda copia o `_registrar` ([ui/desfazer_nesta_pagina.py#L187](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/desfazer_nesta_pagina.py#L187)); M2, "como sai no
PDF" ainda em [ui/tela_conferir.py#L4910](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_conferir.py#L4910) e [core/automatico.py#L1292](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/automatico.py#L1292); M3, a prévia ainda lê o livro ao vivo
([ui/tarefas.py#L978](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tarefas.py#L978)) e o conserto de 09/11 continua como conta por fio (`_resolucao_que_faltava`,
[core/pipeline.py#L2928](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/pipeline.py#L2928)); M4, `recalcular_divisao` ainda sem a tampa do scanner ([core/pipeline.py#L463](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/pipeline.py#L463), usada em
[ui/tela_conferir.py#L6542](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_conferir.py#L6542)); M5, o "dividir" da grade não chama `_linha_arrastada` (`_dividir_escolhidas`,
[ui/tela_conferir.py#L7410](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tela_conferir.py#L7410)), e o comentário "pela MESMA conta do 'dividir esta'" segue em L7402; M6,
`MARCAS_DA_PAGINA` sem o giro da página (L10152) e a capa do cartão só com `folhas[0].rotacao`
([ui/janela_principal.py#L1662](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/janela_principal.py#L1662)); M7, 26 testes `getattr(..., "inserida", ...)` espalhados em `core/`, `ui/` e
`modelos.py`; M8, o "Tirar o fundo" que falha ainda só vai ao registro ([core/pipeline.py#L2653-L2658](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/pipeline.py#L2653-L2658)); B1
([ui/tarefas.py#L944](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/tarefas.py#L944)), B2 (a tela tem 10.187 linhas, eram 10.041), B3 ([core/automatico.py#L419](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/core/automatico.py#L419)), B4
([ui/janela_principal.py#L1916-L1917](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/ui/janela_principal.py#L1916-L1917)). Motivo escrito: D-765 (17/11) congelou os consertos do programa.

**Fora do programa, o mesmo desenho** (só cito; é do outro agente): o catálogo de erros conta a família F2 ("a
conferência olha o jeito mais comum, e o vizinho passa") voltando nas **seis** voltas de quem tentou quebrar o passo 0, o porteiro
(as seis voltas acharam 19, 9, 7, 6, 3 e 1 erros, de todas as famílias), e a F5 ("dá como feito o que não conferiu") com 9 erros no passo 1, mesmo com a regra
§11.12 escrita por causa dela (`memoria/catalogo-de-erros.md`, L131-L163 e L204-L225, no `obra-2026-10-26`).

## 9. Opinião do agente

- O que se repete não é falta de cuidado num ponto: é que a **regra de cada ferramenta não mora num lugar**. Ela mora
  em `ui/tela_conferir.py` (10 mil linhas), em vários métodos parecidos, e cada decisão nova do Samuel chega como um
  `if` a mais no método onde o defeito apareceu. O próximo caminho continua com o jeito antigo, e o Samuel o encontra.
- O trabalho é guiado por decisão (D-xxx) e por print, e o teste prova o caso pedido. Ninguém é cobrado por "todos os
  caminhos dão o mesmo resultado", então os caminhos divergem sem nenhum teste ficar vermelho. A regra §11.12 pede
  exatamente essa prova, mas os 16 remendos de 10/11 continuam no código, então ela ainda não foi aplicada ao passado.
- O caso 6 mostra o remédio funcionando (um dado, uma função em `core/`) e também o custo de não ter feito o resto:
  mesmo com a regra certa, foi preciso costurá-la à mão em cinco caminhos duplicados.
- Os comentários do tipo "é a mesma conta de..." ficam falsos e enganam o agente seguinte (casos 4 e M5).


---

# Partes 2 e 3: o atualizador e os testes à distância

Pesquisador, 23/11/2026. Só leitura: nenhum código, teste ou documento existente mudou, nada rodou no Windows.
Código lido: ramo `atualizador-4-consertos-2026-11-21`, ponta de código `aa1963b7` (relatórios em `046c0271`; os dois
estão no GitHub, conferido com `git branch -r --contains`). Livro de decisões: ramo `obra-2026-10-26`, `0f58346a`.
Histórico e CLAUDE.md: `fase-1`, `47394b4a`. Todos os links abaixo são fixos nesses commits.

Abreviações dos links: **A** = `atualizacao.py`, **W** = `core/windows.py`, **T** = `core/testes_a_distancia.py`,
**TW** = `core/_testes_a_distancia_windows.py`. "Fato" = lido no código, no documento ou na fonte de fora citada.
"Dedução" = minha leitura, marcada. A opinião fica só na última seção.

**Tamanho, para dar a escala (fato, `git show <commit>:<arquivo> | wc -l`):** `atualizacao.py` tinha 935 linhas na
etapa 3 (`16c838a7`, 16/11), 1.681 no começo deste ramo (`4a775ba8`, 21/11), 1.892 depois da volta 2, 1.942 depois da
volta 3 e **2.314** na volta 4 (`aa1963b7`). `core/windows.py` (a "peça única", nascida em 19/11) tem 2.813.
`core/testes_a_distancia.py` tem 877. Os dois arquivos de teste deste ramo somam 1.855 linhas.

---

# Parte 2. O atualizador

## 2.1 O que o Samuel pediu

- **D-706** (16/11): "vamos adicionar uma forma de atualizar o aplicativo via internet quando ele achar algum problema e
  precisarmos arrumar, as atualizaçõpes não podem estar ligadas via api". [Livro L996](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L996)
- **D-723**: "velopack" (contra o tufup). [L1013](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1013)
- **D-718/D-719**: se falhar, volta para a anterior e avisa: "Sim, e tem que avisar a gente de alguma maneira" · "1".
  [L1008](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1008)
- **D-715/D-720**: com o programa aberto, aviso "Reiniciar agora" / "Depois". **D-734**: com "Depois", "quando ele abrir
  o programa de novo". D-715 em L1005, D-720 em L1010, D-734 em [L1024](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1024)
- **D-732**: procurar "quando ele abre o programa né? assim como todo aplicativo faz". [L1022](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1022)
- **D-733** (a escolha que gera o ajudante): entre (1) uma pergunta do Windows só na primeira abertura, (2) uma pergunta
  a cada versão, (3) instalar só na conta do Kaique, "os testes de longe deixam de funcionar": **"1- sim / VAI CONSEGUIR
  FAZER OS TESTS A DISTANCIA NÉ?"**. [L1023](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1023)
- **D-735/D-741/D-749**: a pergunta aparece sempre; depois do "Não" volta a cada abertura; preparação pela metade conta
  como não feita. D-735 em L1025, D-749 em L1039, D-741 em [L1031](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1031)
- **D-736**: "Se tiver nova versão eu quero poder mandar atualizar aqui pelo meu pc". [L1026](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1026)
- **D-742/D-748**: a janelinha "Atualizando o programa, espere um pouco..." no "Depois", que some quando o brasão aparece.
- **D-767** (18/11): "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione".
  [L1057](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1057)
- **D-779**: "ta vamos continuar com ele, mas o que fazemos para ele não dar defeito e porque nossa peças em voltadele
  deram defeito?" (Velopack 1.2.161 com "a nossa proteção"; situação no Livro: "decidida, não construída").
  [L1069](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1069)
- **D-806**: a licença pedida "no mesmo instante do clique do Kaique [...] enquanto a janela do programa ainda está na
  frente" ("então pode ser opção A"). [L1096](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1096)
- **D-824** (21/11): entrega em duas vezes, primeiro só "os 4 consertos"; "vamos fazer com um só, uma coisa de cade vez.".
  Ficam para depois: "Atualizar agora?" ao fechar (D-769/D-794), a janelinha em toda troca (D-770), os testes à distância.
  [L1114](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1114)
- **D-828** (22/11): "foi eu, pode consertar essas coisas": o "Reiniciar agora" troca de verdade, "o nosso programa
  garante que o programa terminou de fechar", abrir pelo atalho no meio não estraga; a pergunta no meio da tela; refazer a
  preparação dá certo. [L1118](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1118)

## 2.2 Como funciona hoje, passo a passo (fato, do código e do cabeçalho de `atualizacao.py`)

Instalação: `.msi` do Velopack, por máquina, em `C:\Program Files\EditorImpressaoPrograma\current`. O gancho de instalar
só anota, porque o `.msi` roda os ganchos **sem** licença de administrador (achado B1, [A:20-23](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L20)).

1. **Primeira abertura (conta do Kaique).** A janela da senha → "Agora não" → um fio solto (daemon) chama
   `preparar_ao_abrir` → `preparar_na_primeira_abertura` ([A:2088](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2088)).
   Espera a janela estar na frente (`esperar_a_janela_na_frente`, [A:2042](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2042)),
   depois `core.windows.pedir_licenca` ([W:2760](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2760)):
   grava `trabalho.json` numa pasta de troca e abre **o próprio `EditorImpressao.exe`** com `ShellExecuteExW` "runas"
   (o UAC; `hwnd` = a janela dona, [W:2724](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2724)).
   Esse processo elevado (administrador, sessão do Kaique) roda um passo de PowerShell que abre **de novo** o `.exe` com
   `--preparar-o-computador` e espera ([A:1906](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1906)).
   Esse terceiro processo cria o **ajudante** (`schtasks /Create` com XML: roda como SYSTEM, `--procurar-atualizacao`,
   contas autenticadas podem mandar rodar, [A:1457](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1457), `QUEM_PODE_MANDAR_RODAR` [A:164](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L164)),
   a tarefa "desfazer" (pelo caminho dos testes à distância, Parte 3), o Visual C++ e tira o Inno antigo. Depois, na conta
   do Kaique, `ler_o_computador` lê as duas tarefas no Agendador e decide se a pergunta volta ([A:1953](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1953)).
2. **Toda abertura comum (conta do Kaique).** `main.py` → `atender_linha_de_comando` ([A:2260](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2260)):
   se há troca acontecendo (`troca_em_andamento`, [A:2286](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2286)), sai em silêncio;
   se há versão esperando do "Depois", troca antes da janela (`trocar_antes_de_abrir`, [A:1267](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1267)).
   Senão a janela abre, segura o mutex `Global\EditorImpressao-programa-aberto` e manda o ajudante rodar com
   `schtasks /Run` (`procurar_ao_abrir`, [A:1409](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1409)).
3. **O ajudante (SYSTEM, sessão 0, é o próprio `EditorImpressao.exe` de `current`).** `rodar_ao_ligar` ([A:813](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L813)):
   Visual C++/Inno, motor do Kraken, resultado da última troca, e `procurar_e_preparar` ([A:617](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L617)):
   `check_for_updates` → assinatura Ed25519 antes de baixar → motor no lugar → `download_updates` → "programa aberto?"
   (mutex **e** lista de processos de `current`, até 30 s, [A:907](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L907)).
   Aberto: grava `"pendente"` em `C:\ProgramData\EditorImpressao\atualizacao\estado.json`; a tela, que lê esse arquivo
   4 s depois de abrir e de 5 em 5 min, mostra o aviso. Fechado: grava `"aplicando"` e pede a troca.
4. **O pedido de troca** passa sempre por `GerenteComAMarcaDaTroca.wait_exit_then_apply_updates` ([A:552](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L552)):
   só chama o Velopack se o mutex `Global\EditorImpressao-trocando` estiver seguro (`segurar_a_marca_da_troca`,
   [A:1307](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1307)).
   O Velopack lança o `Update.exe` (SYSTEM), que espera o ajudante sair, extrai, fecha à força o que roda da pasta,
   renomeia `current` e reabre `EditorImpressao.exe --conferir-a-versao-nova` (SYSTEM, escondido): teste rápido num
   subprocesso; passou → `"ok"` e refaz o ajudante ([A:2226](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2226)); falhou → baixa o pacote inteiro da anterior, confere a assinatura e chama `Update.exe apply --package` direto ([A:750](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L750), [A:779](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L779)).
5. **Caminho COM o script** ("Reiniciar agora", ou "Depois" + nova abertura). A janela fecha gravando; `trocar_e_reabrir`
   ([A:1232](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1232))
   lança pela peça um PowerShell solto **na conta do Kaique** ([A:1120](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1120)),
   com pasta de trabalho System32 e sinal de vida. Linha 1: pega as marcas da troca e de reabrir. Depois: `Wait-Process`
   do programa (120 s), `schtasks /Run` do ajudante (passo 3, agora com o programa fechado), laço lendo `estado.json` e o
   estado da tarefa a cada 2 s até 900 s, mais 60 s se a nova falhou no teste, e `Start-Process` do programa com
   `--depois-da-troca`. No "Depois", o mesmo script abre ainda a janelinha (Windows Forms num runspace STA, [A:968](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L968)).
6. **Caminho SEM o script** (o Kaique fechou o programa durante o download; ou o Samuel mandou de longe pela conta de
   testes, `ssh ... schtasks /Run`, [A:1430](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1430)).
   O ajudante vê "fechado" e, antes de pedir a troca, lança o **vigia** (PowerShell, SYSTEM, [A:1091](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1091)),
   que segura a marca da troca enquanto a fase for "aplicando". Ninguém reabre o programa (SYSTEM não abre janela na tela
   do Kaique), salvo se ele clicar no atalho no meio: aí `abrir_quando_a_troca_acabar` ([A:1362](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1362))
   lança o script "só de reabrir" (conta do Kaique), que espera a marca sumir e abre.

Num "Reiniciar agora" que dá certo, contei (dedução, seguindo o código) **sete processos em duas contas**: o PowerShell
do script (Kaique), `schtasks`, o ajudante (SYSTEM), o `Update.exe` (SYSTEM), o `--conferir-a-versao-nova` (SYSTEM), o
teste rápido (SYSTEM) e o programa reaberto (Kaique). O único canal entre as duas contas é `estado.json` e três mutexes.

## 2.3 As peças, uma ficha cada

"Por causa de outra peça nossa?": **fato** quando o próprio comentário do código diz; **dedução** quando é minha.

| Peça | Onde | O que faz | Problema que tentou resolver | Origem | Se sair | Por causa de outra peça nossa? |
|---|---|---|---|---|---|---|
| Ajudante (tarefa SYSTEM) | [A:1457](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1457) | troca em Arquivos de Programas sem UAC | trocar sem pergunta a cada versão; trocar de longe | **D-733** (Samuel, 17/11), commit `73dc4122` | um UAC por versão (o jeito 2 que ele recusou) e sem "mandar atualizar de longe" (D-736) | não: vem de o programa morar em Arquivos de Programas |
| Pergunta da primeira abertura (exe elevado → PowerShell → exe de novo) | [A:1906](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1906), [W:2760](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2760) | um UAC cria as tarefas, VC++, tira Inno | o "Não" lido como "Sim" (defeito 2 da etapa 5) | D-733/D-735/D-805; peça de `9e2268cc` (19/11), usada desde o conserto 1 `85590fe4` | sem ajudante não há o que criar | **sim (fato)**: só existe para criar o ajudante; o salto duplo vem de a peça só aceitar passos de uma lista fechada ([W:54-70](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L54)) |
| "Preparado?" lido no Windows | [A:1953](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1953) | lê as 2 tarefas; vazio = não pergunta | a marca nas Configurações dizia "preparado" sem estar | conserto 1 `85590fe4`; ajustes `9979419d` (volta 2), `ce728693`/`ebd4197e`/`f15863b8` (volta 3, D-826) | volta a anotação que mente (§11.12 ponto 2) | **sim (dedução)**: só existe porque o ajudante existe |
| Esperar a janela na frente | [A:2042](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2042), [W:1942](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L1942) | sem limite, lê a cada 0,3 s quem está na frente | a pergunta piscando na barra (prova nº 1) | volta 4 `1e5ea67d`; **leitura da gerente** da D-806 (o relatório 3 e a PARTE -44 dizem isso) | volta a piscar | **sim (fato, [A:2052-2054](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2052))**: o pedido sai 17-20 s depois do clique porque o programa primeiro carrega e monta a janela |
| Script da troca (PowerShell, conta do Kaique) | [A:1120](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1120) | espera fechar, chama o ajudante, espera, reabre | o .exe tem de sair; SYSTEM não abre janela | D-720/D-734, `73dc4122` (17/11) | "Reiniciar agora" não reabre | **sim (fato, docstring [A:1123-1127](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1123))**: "Por que nao o ajudante: ele roda como SYSTEM" |
| Lançar solto com sinal de vida e pasta System32 | [W:1662](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L1662), `cwd` [W:1689](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L1689) | lança o script e confere que começou | `DETACHED_PROCESS` (o PowerShell saía sem rodar); a pasta de trabalho prendia `current` | peça `9e2268cc`; usada no conserto 3 `77a05d2e`; `cwd` na volta 4 `b756ddc2` | o script não roda ou prende a pasta | **sim (dedução)**: existe para o script da troca |
| Mutex "programa aberto" | [A:864](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L864) | a janela segura; o ajudante lê | o ajudante (outra sessão) saber se o programa está aberto | etapa 3 `16c838a7` | o ajudante trocaria com o programa aberto | **sim (dedução)**: só porque quem troca é outro processo |
| Lista de processos de `current`, até 30 s | [A:907](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L907), [W:1855](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L1855) | confere que nada roda de `current` | o mutex some antes de o processo terminar de gravar | volta 4 `3adea01f`; D-828 "garante que o programa terminou de fechar" | o Velopack fecha à força o que ainda grava | **sim (dedução)**: o `--waitPid` do Velopack espera o **ajudante**, não a janela |
| Marca da troca + `troca_em_andamento` | [A:196](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L196), [A:1344](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1344) | clique no atalho durante a troca sai em silêncio | o clique às 14h34min58 da prova nº 1 | volta 4 `586b483f`; D-828 | o clique estraga a troca | não conferi se o atalho do Velopack (`stub.rs`) já faz algo parecido |
| `FASES_EM_QUE_HA_TROCA` | [A:206](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L206) | só lê o mutex nessas fases | não carregar a peça (~30 ms) em toda abertura | volta 4 `586b483f`, escolha do escritor | 30 ms por abertura | **sim (fato, comentário)**: atalho de velocidade da marca da troca |
| Vigia da troca (PowerShell, SYSTEM) | [A:1091](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1091) | segura a marca na troca sem script | o clique no meio da troca sem script | volta 4 `586b483f`; **resposta 4 da gerente**, não do Samuel ([ONDE-PAREI L1428](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/ONDE-PAREI.md#L1428)) | volta a ressalva que o escritor propunha deixar | **sim (fato)**: existe só para a marca da troca no caminho sem script; e porque o ajudante (que é o `.exe` de `current`) tem de sair antes da troca |
| `GerenteComAMarcaDaTroca` + `segurar_a_marca` + `TrocaSemAMarca` | [A:552](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L552), [A:1307](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1307) | embrulha o `UpdateManager`; sem marca, não troca; lança o vigia e espera 10 s o mutex | "toda troca com a marca" | volta 4 `586b483f` | uma troca sem marca | **sim (fato)**: força a marca da troca e lança o vigia |
| Marca de reabrir + script "só de reabrir" | [A:200](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L200), [A:1167](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1167) | depois do clique engolido, alguém reabre, uma vez só | o clique engolido não abria nada | volta 4 `586b483f` | o Kaique clica e nada abre | **sim (fato)**: existe porque a marca da troca engole o clique e o vigia não reabre |
| Janelinha + mutex da janelinha | [A:968](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L968), [A:187](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L187) | avisa durante a espera do "Depois" | o Kaique achar que não abriu | **D-742, D-748** (Samuel, 17/11), `1a42dfb0`, `5a407a6f` | contra a decisão dele | sim (dedução): existe porque a troca do "Depois" é fora do programa |
| Voltar para a anterior | [A:750](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L750), [A:779](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L779) | teste rápido; falhou → baixa a anterior e `Update.exe apply --package` | versão nova estragada | **D-718** (Samuel), etapa 3 `16c838a7` | contra a decisão dele | não; mas fica **fora** da peça e do pedido único de troca (baixo 1 do relatório 3) |
| Refazer o ajudante depois da troca | [A:2226](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2226) | recria a tarefa como SYSTEM | o gancho de atualizar não tem licença (B1) | `73dc4122` | XML de versão velha | sim (dedução): por causa do ajudante |
| Motor do Kraken à parte | [A:1766](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1766) | põe o motor em `<raiz>\motor-kraken\1`; sem ele, não anuncia versão | não baixar 370 MB a cada versão | **D-768/D-788/D-790** (Samuel), conserto 4 `75cfa928`, volta 2 | o motor some na troca | não |
| `estado.json` + gravar com 30 tentativas | [A:285](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L285), leitura [A:1059](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1059) | o canal entre SYSTEM e Kaique | duas contas precisam combinar a fase | etapa 3; o "tenta de novo" e o `-ErrorAction Stop` na volta 4 (`5a1aa6b2`) | sem canal | **sim (dedução)**: por causa do ajudante e dos scripts |
| Pasta segura | [W:2287-2385](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2287) | pasta em Arquivos de Programas com as licenças de fábrica | a tranca à mão (`icacls /T`) deixava arquivos sem licença | peça `9e2268cc` (plano-v3); usada nos testes à distância na volta 4 `929195b4` | volta a tranca à mão | sim (fato): substitui a nossa tranca de 18/11 |

## 2.4 O que o Windows e o Velopack fazem de difícil

| Comportamento | Fonte | Lido por mim? |
|---|---|---|
| O `Update.exe` fecha à força todo processo cujo `.exe` está dentro da raiz (`PROCESS_TERMINATE`), menos ele mesmo | Velopack 1.2.161, [`util_windows.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/shared/util_windows.rs) (`get_processes_running_in_directory`, `_force_stop_package`) | sim, hoje |
| Renomeia `current` com 10 tentativas, 1 s cada; se não der: "Unable to start the update, because one or more running processes prevented it"; se falhar a **segunda** troca de nome, "the app was left in a broken state" (a volta está comentada no código) | [`apply_windows_impl.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/commands/apply_windows_impl.rs) | sim, hoje |
| `WaitExitThenApplyUpdates` "wait for 60 seconds before proceeding. If your app has not exited within 60 seconds it will be killed" | [docs.velopack.io/integrating/overview](https://docs.velopack.io/integrating/overview) | sim, hoje |
| A tranca do Velopack (`packages\.velopack_lock`) é segurada também durante o download; o atalho passa `AllowSetForegroundWindow` e abre com `current` como pasta de trabalho | `manager.rs:406`, `stub.rs:39-41`, segundo o escritor ([ONDE-PAREI L1376](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/ONDE-PAREI.md#L1376)) | **não conferi** |
| O processo filho herda a pasta de trabalho do pai, e uma pasta que é pasta de trabalho não se renomeia (erro 32) | `CreateProcessW`, `lpCurrentDirectory` (citado pelo escritor) e experimento no PC (`anexos/volta4-experimentos.txt`) | a documentação não reabri; o experimento não refiz |
| O Windows tira de um programa o direito de vir para a frente "the next time the user generates input"; o UAC usa a janela dona | `AllowSetForegroundWindow`, `SetForegroundWindow` (citados pelo escritor) | não reabri |
| O `.msi` "PerMachine" roda os ganchos sem administrador (`Impersonate="yes"`) | achado B1, [A:20-23](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L20) | não reabri o WiX |
| PowerShell 5.1 lê `.ps1` sem BOM como ANSI: "Without the BOM, Windows PowerShell misinterprets your script as being encoded in the legacy "ANSI" codepage" | [about_Character_Encoding (5.1)](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1) | sim, hoje |
| PowerShell 5.1 com `DETACHED_PROCESS` sai sem rodar | provado na etapa 5 ([revisão 18/11 §1.1](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/8cf8358aaf310a726c4833cbd951f1c133e8f086/relatorios/revisao-atualizador-2026-11-18/relatorio.md#L50)) | não refiz |
| `ctypes.get_last_error()` sem `use_last_error=True` devolve sempre 0: o "Não" do UAC (1223) virava sucesso | [W:45](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L45) e o conserto 1 | doc do Python não reabri |
| `icacls /inheritance:r /grant:r ... /T` deixa os arquivos já existentes com a lista de licenças vazia, e devolve 0 | provado em 18/11 ([revisão distância](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/77848768818c294f9b0e95029b2827dd78ac4600/relatorios/revisao-distancia-2026-11-18/relatorio.md#L21)) | não refiz |
| `Start-Process` 5.1: o documento diz que a pasta padrão é a do executável; o experimento mediu a do PowerShell | baixo 2 do [relatório 3](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L106) | não |

## 2.5 A história das voltas

- **16 a 18/11.** Etapa 3 escrita com o Velopack. Na etapa 5 (18/11, PC do Samuel), 7 defeitos no Windows de verdade; as
  revisões só lendo acharam mais 13 no atualizador e 4 causas de estrutura nos testes à distância. Frase central da
  revisão: "o que o programa lembra não é prova; prova é o que o Windows responde" ([revisão atualizador](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/8cf8358aaf310a726c4833cbd951f1c133e8f086/relatorios/revisao-atualizador-2026-11-18/relatorio.md#L29)).
  Nasce a regra §11.12 ampliada ([CLAUDE.md L712](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/47394b4a5d7d4f9d461d6987676d235254910d9f/CLAUDE.md#L712)) e a peça única (19/11).
- **Volta 1 (21/11, escritor A).** Os 4 consertos: o "Não" pela peça; a janela como dona; "Reiniciar agora" sem
  `DETACHED_PROCESS`; o motor à parte. **Relatório 1:** NÃO ESTÁ PRONTO, 3 médios (motor estragado engolido, "versão
  nova" sem fim sem o motor, a pergunta voltando depois do "Sim") e 10 baixos ([R1 L8](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-1.md#L8)).
- **Volta 2 (escritor A).** Os 3 médios consertados. **Relatório 2:** PRONTO PARA CONFERIR, 6 baixos e uma pergunta
  ([R2 L8](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-2.md#L8)).
  Samuel: "então o agente fez um codigo novo para arrumar outro e criou 6 problemas novos?" → D-826, D-827.
- **Volta 3 (escritor B).** Os 2 baixos de código e os testes das proteções. Não achei relatório de "quem quebrou" desta
  volta na pasta.
- **Prova à vista nº 1 (22/11, 13h52-14h39).** Funcionou: o "Não", o "Sim" lido do Windows, a conta comum lê as tarefas,
  o motor, o aviso, a volta com a frase da falha. Falhou: o "Reiniciar agora" não troca (erro 32 em 10 tentativas), a
  pergunta pisca na barra, a segunda preparação dá "acesso negado" ([PARTE -44 §3](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/47394b4a5d7d4f9d461d6987676d235254910d9f/historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md#L70)).
- **Volta 4 (escritor C).** A causa do erro 32 (a pasta de trabalho), a lista de processos, a marca da troca, o vigia,
  o só de reabrir, a espera pela janela na frente, a pasta segura. D-829 autoriza 3 testes. **Relatório 3:** NÃO ESTÁ
  PRONTO, 5 médios ([R3 L12](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L12)).
  Ele diz que "a causa principal saiu" e que "nenhum pede para refazer a volta".

## 2.6 Os 5 médios do relatório 3, com o código

**Médio 1. Sem o script, "está aberto?" vem antes da marca** ([R3 L31](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L31)).
[A:676-685](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L676):
```python
    if programa_aberto():                      # 676: pergunta primeiro
        ...
    gravar_estado({"fase": "aplicando", **base})
    try:
        gerente.wait_exit_then_apply_updates(...)   # 684: só aqui o vigia nasce e a marca aparece (até 10 s)
```
Um clique no atalho entre a pergunta e a marca abre o programa; o Velopack o fecha à força e ninguém reabre.

**Médio 2. O script da troca zera a fase antes de ler** ([R3 L48](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L48)).
[A:1189-1196](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1189):
```python
        "    $fase = ''; $tipo = ''",
        "    " + _linha_de_ler_a_fase(estado),       # uma leitura que falha deixa $fase vazia
        ...
        "    if ($fase -ne 'pendente' -and $fase -ne 'aplicando') { break }",
```
O vigia não zera (a regra "só muda a fase se leu", [A:1059](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1059)). O verificador provou no Windows: com o arquivo
travado, o laço saiu em 1 s. O script então reabre o programa no meio da troca.

**Médio 3. "Sem licença para abrir a marca" = "existe", sem teste** ([R3 L65](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L65)).
[A:1085-1086](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1085):
```python
        "  try { if ([System.Threading.Mutex]::TryOpenExisting($nome, [ref]$m)) { $m.Dispose(); return $true }"
        " ; return $false } catch { return $true }",
```
Trocando o `catch` por `return $false`, os 55 testes passam.

**Médio 4. A janela da frente vira a dona, sem teste** ([R3 L76](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L76)).
[A:2106-2111](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2106):
```python
        dona = esperar_a_janela_na_frente(janela)
        if dona is None:
            ...
        janela = dona                                # trocar por `pass`: os 55 testes passam
```

**Médio 5. A pasta segura criada e gravada por fora da peça, e conferida depois** ([R3 L84](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L84)).
[T:378-379](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L378) (repetido em [T:290](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L290)) e [T:869-872](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L869):
```python
    return (f"$pasta = '{pasta_dos_testes()}';"
            f" if (-not (Test-Path -LiteralPath $pasta)) {{ New-Item -ItemType Directory -Path $pasta -Force | Out-Null }}")
    ...
        resultado = executor.aplicar_ja_como_administrador(plano_de_preparar_o_desfazer())  # já gravou desfazer.ps1 e a tarefa
        ...
        conferida = executor.conferir_a_pasta_dos_testes()                                  # só agora confere
```
A peça já tem `criar_pasta_segura` (cria, confere, apaga se não confere) e `gravar_na_pasta_segura` (confere antes,
lê de volta), [W:2320](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2320) e [W:2361](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2361), e os passos `passo_criar_pasta_segura`, `passo_gravar_na_pasta_segura`, `passo_criar_tarefa` ([W:2394-2414](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2394)).

---

# Parte 3. Os testes à distância

## 3.1 O que é e o que ele pediu

O Samuel entra de longe no notebook do Kaique para rodar testes (velocidade e outros) e mandar atualizar.
- **D-705**: "vamos colocar uma api no programa para que eu possa fazer chamadas dentro do proprio pc do kaique para
  fazer testes de velocidade e outras coisas" → escolhido o Servidor OpenSSH do Windows, só pela rede do Tailscale, sem
  porta dentro do programa. [L995](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L995)
- **D-711** "liga sozinho com o windows, eu vou fazer uma senha, e não vai sr chave"; **D-712** ligado de fábrica, botão
  nas Configurações; **D-717** conta separada, sem administrador, escondida ("sim"); **D-721** janela da senha na primeira
  abertura; **D-731** desinstalar desfaz tudo ("ok"); **D-736** mandar atualizar de longe.
- Decididas e **não construídas**: **D-771** ligar é "tudo ou nada" ("A"); **D-780** duas trancas, firewall e dentro do
  próprio OpenSSH; **D-781** dois campos de senha. [L1061](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1061), [L1070](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1070)
- **D-824/D-825**: ficam para uma entrega depois; nesta, a senha digitada não liga nada ("opção B").
  [L1115](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1115)

## 3.2 Como funciona hoje, e as peças

- **Ligar** (botão das Configurações, [ui/tela_configuracoes.py:389](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/ui/tela_configuracoes.py#L389)) → `ligar(senha)` ([T:802](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L802)) →
  `plano_de_ligar` (9 passos, [T:408](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L408)) →
  `ExecutorWindows.aplicar` → `TW.aplicar_no_windows` ([TW:103](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/_testes_a_distancia_windows.py#L103)):
  script em `tempfile.mkdtemp`, senha cifrada por DPAPI, e `_rodar_elevado`, um `runas` **próprio**, fora da peça única.
- **Desligar**: o mesmo caminho, com outro UAC. **Desfazer**: a tarefa SYSTEM "Desfazer testes a distancia" roda
  `desfazer.ps1` da pasta segura; o gancho de desinstalar só manda rodar (`schtasks /Run`, [T:840](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L840)).
  A primeira abertura cria essa tarefa pelo `aplicar_ja_como_administrador_no_windows`, que abre o `powershell.exe` direto
  e grava o script em UTF-8 **sem BOM** ([TW:148-152](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/_testes_a_distancia_windows.py#L148)).
- **`core/_testes_a_distancia_windows.py` não mudou desde `b74a94e2`** (a base das revisões de 18/11): `git diff
  b74a94e2 aa1963b7` vazio. A linha que lia o "Não" como "Sim" continua no caminho do ligar:
  `return ctypes.get_last_error()` com `ctypes.windll` ([TW:94-95](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/_testes_a_distancia_windows.py#L94)). Isso já está anotado como lembrete no relatório 1 (L119-L121).

| Peça | Onde | O que faz | Origem | Se sair | Por causa de outra peça nossa? |
|---|---|---|---|---|---|
| Conta `EditorTestes` (Usuários, escondida) | [T:408](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L408) | quem entra de longe | D-717 (Samuel) | entra com a conta do Kaique | não |
| OpenSSH + bloco no `sshd_config` (`AllowUsers`, `PasswordAuthentication yes`, `MaxAuthTries 3`) | [T:120](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L120) | a porta de entrar | D-705, D-711 | não há teste à distância | não |
| Regra do firewall só para 100.64.0.0/10 e a placa Tailscale | [T:88](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L88) | tranca de rede | D-705 | porta aberta à rede da casa | não |
| Caderninho `antes.json` | [T:268](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L268) | o que o PC já tinha, para desfazer só o nosso | D-731, `65303058` | o desfazer tiraria o OpenSSH do dono | não |
| Tarefa "desfazer" (SYSTEM; nega a conta de testes; AU pode mandar rodar) | [T:306](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L306), [T:334](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L334) | desfaz ao desinstalar, apaga também o ajudante | D-731/D-733, `77be80ff` | desinstalar deixa tudo (o gancho não tem licença) | **sim (fato)**: o gancho do `.msi` roda sem administrador (B1) |
| `Executor` / `ExecutorWindows` | [T:669-760](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L669) | os testes trocam por um de mentira | etapa 4 `59aa8049` | nada | não; mas é a segunda "peça do Windows" do programa (dedução) |
| `CHAVE_PRONTO` nas Configurações | [T:158](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L158) | anota "ligado" | etapa 4 | — | é a anotação que a §11.12 (ponto 2) proíbe como prova (dedução) |

## 3.3 O que dá para fazer no PC do Kaique, e os riscos

Fato do código: pelo `ssh EditorTestes@<endereço>` o Samuel roda comandos como uma conta comum; pode mandar o ajudante
rodar (`comando_de_longe_para_atualizar`, [A:1430](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1430)) e ler `atualizacao.log` no ProgramData ([A:1445](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1445)).
O ajudante só roda o `.exe` fixo com o argumento fixo; mudar a tarefa pede administrador (`GRGX` só lê e executa).

Riscos (fato, salvo onde marcado):
- **Senha por senha**, com 3 tentativas por conexão; a única tranca de rede é o firewall (a segunda, D-780, não existe):
  o bloco do `sshd_config` não tem `Match Address`. Desligado o firewall, a porta 22 aceita qualquer rede (dedução).
- **Ligar pela metade:** o script do ligar para no primeiro erro e não desfaz ([T:619-660](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L619)):
  pode ficar o OpenSSH, a regra, a conta. D-771 ("tudo ou nada") não está construída.
- **O "Não" do UAC pode virar "ligado"** no caminho das Configurações (TW:95, acima): `CHAVE_PRONTO = True` sem nada feito.
- **Senha com acento** trocada no caminho (provado na [revisão de 18/11](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/77848768818c294f9b0e95029b2827dd78ac4600/relatorios/revisao-distancia-2026-11-18/relatorio.md#L25)); o arquivo não mudou depois, então continua (dedução).
- **Desfazer:** roda como SYSTEM o `desfazer.ps1` da pasta segura (contas comuns só leem). Com o médio 5, numa pasta que
  já existia com outras licenças, o script é gravado e a tarefa aponta para ele mesmo assim.
- O que fica se falhar no meio do desfazer: os passos seguem depois de erro e a tarefa só se apaga se tudo deu certo
  ([T:524](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L524)): dá para rodar de novo.

## 3.4 A situação de agora

Não entra na primeira entrega ao Kaique (D-824, D-825). O que existe no código é o de 16 a 17/11, mais a pasta segura
da volta 4. O ligar e o desligar nunca passaram pela peça única. As decisões de 18/11 (D-771, D-780, D-781) estão só no
Livro. Na prova de 18/11 (etapa 5), os testes à distância deram os defeitos que a revisão daquele dia descreve.

---

# Opinião do agente

Tudo aqui é opinião. Marco **certeza** quando decorre direto do código lido, e **palpite** quando não.

**1. As peças que parecem existir só para proteger outra.** Certeza, pelo próprio comentário do código: o vigia existe
para a marca da troca no caminho sem script; a marca de reabrir e o script "só de reabrir" existem porque a marca da
troca engole o clique e o vigia não reabre; o `GerenteComAMarcaDaTroca` existe para obrigar a marca; `FASES_EM_QUE_HA_TROCA`
existe para a marca não custar 30 ms. As quatro nasceram juntas na volta 4 (`586b483f`), e três dos cinco médios moram
nelas (1, 3 e, em parte, 2). Num nível abaixo, quase todo o resto é consequência de uma escolha só: **quem troca é um
processo SYSTEM que é o próprio `.exe` de `current`**. Por isso ele tem de sair antes da troca; por isso alguém de fora
precisa segurar o estado (script, vigia, `estado.json`, mutexes); por isso o `--waitPid` do Velopack espera o processo
errado e foi preciso a lista de processos.

**2. O desenho mais simples do atualizador (palpite).**
- *Só o Velopack:* instalar por usuário (`%LOCALAPPDATA%`), procurar e baixar no próprio programa, `apply_updates_and_restart`
  no "Reiniciar agora" e `wait_exit_then_apply_updates` (ou a troca do próprio Velopack ao abrir) no "Depois". O Velopack
  espera o programa sair, fecha o que sobrou, troca e reabre na conta certa. Somem o ajudante, a pergunta da primeira
  abertura, os dois scripts, o vigia, as três marcas, a lista de processos e o `estado.json`. **Perde-se:** o jeito 1 da
  D-733 (era o jeito 3 que ele não quis, "os testes de longe deixam de funcionar") e o "mandar atualizar de longe" da
  D-736; o Visual C++ e tirar o Inno ainda pediriam uma licença. Em Arquivos de Programas sem ajudante, seria um UAC por
  versão (o jeito 2, também recusado).
- *Mantendo a D-733:* um ajudante que **não mora em `current`** (um `.exe` pequeno na pasta segura, ou a tarefa chamando o
  `Update.exe` direto), que segura ele mesmo a marca do começo ao fim, espera o programa do Kaique pelo número do
  processo e faz o teste rápido e a volta. Sumiriam o vigia, o `GerenteComAMarcaDaTroca`, a espera de 10 s pela marca e a
  duplicação "script lê o estado / vigia lê o estado". Ficaria um script do lado do Kaique só para reabrir (SYSTEM não
  abre janela na sessão dele sem um caminho mais complicado). Não conferi no Velopack 1.2.161 se a tarefa pode chamar o
  `Update.exe` assim.

**3. O desenho mais simples dos testes à distância (palpite).** Ligar e desligar pela peça única, com os passos que ela
já tem (`passo_criar_pasta_segura`, `passo_gravar_na_pasta_segura`, `passo_criar_tarefa`, `passo_script`), e apagar o
`runas` próprio de `_testes_a_distancia_windows.py`. Isso cumpre o ponto 1 da §11.12 e leva junto o "Não" lido como "Sim"
e o médio 5. A tela mostraria o que o Windows tem (o serviço, a conta, a regra), não `CHAVE_PRONTO`.

**4. Quais dos 5 médios somem se a peça sair.**
- Médio 1: some se o ajudante nunca trocar sem o script (certeza: o defeito só existe nesse caminho). O preço: a troca
  de longe e a do "fechou durante o download" esperariam a próxima abertura (mexe na D-736).
- Médio 2: não depende de peça a mais. É a mesma leitura escrita duas vezes, uma certa e uma errada (certeza). Some
  apagando a linha `$fase = ''`, ou se o script esperasse a marca em vez de ler o JSON (palpite).
- Médio 3: some se o vigia e o "só de reabrir" saírem (certeza), porque a marca SYSTEM lida da conta comum só acontece
  entre os dois.
- Médio 4: some se a espera pela janela sair (certeza). A pergunta volta a piscar, a não ser que ela seja feita antes de
  o programa carregar, o jeito que a D-806 descreve ("no mesmo instante do clique") e que o escritor recusou (palpite meu
  de que é o mais simples; ele argumentou que o brasão não toma a frente).
- Médio 5: some se o desfazer for preparado pela peça (certeza: a peça já cria, confere e grava).

**5. Resposta curta à pergunta do Samuel (palpite com base nos fatos acima).** Sim, em parte. As voltas 1 a 3 consertaram
causas de verdade e não empilharam proteção. A volta 4 consertou a causa principal com um conserto pequeno (`b756ddc2`: 19 linhas de código, o `cwd` do lançado solto) e depois
acrescentou de uma vez quatro peças que só protegem outra, e foi ali que o relatório 3 achou três dos cinco médios. O que
não é "proteção da proteção" é o custo da escolha do ajudante SYSTEM (D-733), que foi do Samuel e tem motivo.

---

## Fontes consultadas (23/11/2026)

- Código e relatórios do repositório, nos commits dos links.
- Velopack 1.2.161: [apply_windows_impl.rs](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/commands/apply_windows_impl.rs),
  [util_windows.rs](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/shared/util_windows.rs) (licença MIT,
  D-723); [docs.velopack.io/integrating/overview](https://docs.velopack.io/integrating/overview).
- Microsoft: [about_Character_Encoding, PowerShell 5.1](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1).
- O resto das fontes de fora (CreateProcessW, AllowSetForegroundWindow, CreateMutexW, `manager.rs`, `stub.rs`) é citado
  pelo escritor da volta 4 e **não foi reaberto por mim**.


---

# Parte 4. A Central e o jeito de trabalhar

Escrita pela conversa gerente em 23/11/2026. Fato e opinião separados: a opinião está no fim, marcada.

## 4.1 Quem faz o quê

- **O dono (Samuel)** decide o que o programa faz e confere o resultado. Não é programador. Lê em português simples.
- **O usuário (Kaique)** é impressor e não tem formação técnica. Recebe o programa instalado no notebook dele.
- **A conversa gerente** é uma sessão do Claude Code aberta com o Samuel. Ela conversa com ele, divide o trabalho,
  manda os subagentes, junta os ramos e mantém os documentos. Pela regra, não escreve código do programa
  (`CLAUDE.md` §10.1).
- **Os subagentes** têm as regras em `.claude/agents/`. Cada arquivo tem de 10 a 14 KB.
  - `implementador.md`: código de `core/` e scripts.
  - `verificador.md`: testes, antes/depois, pilotar a janela; nunca aprova.
  - `pesquisador.md`: lê código e documentação de fora.
  - `layout.md`: só `ui/`.
  - Desde 20/11 (D-815), quem confere é um **agente novo a cada volta** ("quem tenta quebrar"). Ele lê o código,
    desliga as proteções uma a uma (mutação manual) e roda demonstrações no Windows de verdade. Um mesmo escritor
    fica no máximo 2 voltas.
- **Limite:** no máximo 2 agentes ao mesmo tempo, ou 3 quando o terceiro só lê (§11.11). Agente não abre agente.

## 4.2 Os documentos que mandam

Ordem de leitura obrigatória, no topo do `CLAUDE.md`:

| Documento | Onde | Tamanho em 23/11 | O que é |
|---|---|---|---|
| Livro de decisões | `docs/plano/DECISOES.md`; a cópia que vale está no ramo da versão de teste `obra-2026-10-26` | 618 KB, 841 linhas de decisão (D-001 a D-829) | Cada decisão do Samuel: palavras exatas, o que quer dizer, onde toca, prova de comportamento, situação, dono |
| Estado atual | `docs/plano/ESTADO-ATUAL.md` (`fase-1`) | pequeno | Onde o projeto está |
| Plano | `docs/plano/PLANO-DEFINITIVO.md` (`fase-1`) | 395 KB | Fases, Lista de bugs, Lista de espera, Registro de mudanças |
| Regras técnicas | `CLAUDE.md` (raiz) | 71 KB | Regras do projeto; a seção 11 tem 13 regras, de 26/10 a 18/11 |
| Memória | `memoria/` (índice em `memoria/INDICE.md`) | vários arquivos | Fichas por assunto, `bugs.md`, `catalogo-de-erros.md` (só nos ramos `obra-2026-10-26` e seguintes) |
| Histórico | `historico/Editor de Impressao - resumo para o Claude.md` | 784 KB | Um "PARTE -N" por checkpoint, o mais novo no topo |

- O plano e o Livro têm uma segunda cópia em `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\`, fora do
  git, onde o Samuel edita. A gerente mantém as duas iguais (§10.4).
- Todo relatório para o Samuel sai em `.md`, `.html` e `.pdf` por `relatorio.gravar` (`relatorio.py`, linha 346),
  porque ele não abre `.md`.
- Os comandos `/projeto` e `/checkpoint` ficam fora do repositório (`C:\Users\fotog\.claude\commands\`).
  - `/projeto` obriga a conversa nova a ler as regras inteiras.
  - `/checkpoint` grava o estado no histórico e faz commit.

## 4.3 Ramos

- **`fase-1`**: a versão oficial. Tem o plano e o histórico.
- **`obra-2026-10-26`**: a versão de teste, que o Samuel instala e testa. É o ramo onde o Livro vale. Worktree em
  `.claude/worktrees/obra-juncao`.
- **Um ramo por trabalho**, cada um no seu worktree em `.claude/worktrees/`. Em 23/11 havia 200 worktrees (194 em `.claude/worktrees/`)
  (`git worktree list`). Só a gerente junta os ramos.
- O atualizador está em `atualizador-4-consertos-2026-11-21`, que ainda não foi juntado.

## 4.4 Testes

- O `pytest` inteiro roda no GitHub num Windows da nuvem, pela ação "Testes no Windows":
  `.github/workflows/testes-windows.yml` no ramo `claude/list-server-files-gkos8v`.
  - Comando: `gh workflow run "Testes no Windows" -R Samuel-Bottini-BR/EditorImpressao --ref claude/list-server-files-gkos8v -f ramo=<ramo>`.
  - Leva cerca de 2 h.
- No PC do Samuel, um arquivo de teste por vez enquanto o agente trabalha. A suíte inteira roda só antes de juntar no
  `fase-1`.
- Há um filtro de velocidade no GitHub: antes e depois alternados (§4.6).
- Todo conserto de bug ganha um teste que falha no código antigo (§4.7).
- Cada decisão tem uma prova de comportamento em `tests/test_decisoes*.py` (§11.4).

### O porteiro: a barreira automática que já existe

Este fato a gerente tinha esquecido e só achou ao escrever esta parte.

- **O que é.** Existe uma barreira automática desde 18/11 (D-791; ligada no GitHub em 19/11, D-801): o "porteiro", em `regras_dos_agentes/porteiro.py`
  (1.048 linhas) e `porteiro_mudancas.py`. Ele tem 25 conferências, K01 a K25.
- **O que confere.** Algumas leem o código parado. Exemplos:
  - K01: conversa com o Windows fora de `core/windows.py`;
  - K02: `DETACHED_PROCESS`;
  - K03: licença de pasta à mão.

  Outras olham o que a entrega mudou.
- **Onde roda.** No GitHub, em toda entrega (`tests/test_conferencias_codigo.py`), e por
  `python -m regras_dos_agentes porteiro`.
- **O gancho que não roda.** Existe um gancho antes do commit (`ganchos/pre-commit`), mas ele **não está instalado** no
  clone do PC: `.git/hooks/pre-commit` não existe e `core.hooksPath` não está definido.
- **A lista de exceções.** O que já estava errado em 19/11 fica em `tests/conferencias_excecoes.json`, um item por
  lugar, ligada com o "sim" dele (D-801/D-802). No ramo do atualizador (`aa1963b7`) ela tem **164 lugares** (175 na versão de teste, `0f58346a`). Os que mais pesam:
  - 52 em `teste_velocidade.py`;
  - 50 em `core/testes_a_distancia.py`;
  - 33 em `atualizacao.py`;
  - 12 em `core/_testes_a_distancia_windows.py`.
- **Rodado no código da volta 4** (`aa1963b7`, 23/11): "Porteiro: nada novo (5000 arquivos lidos; a lista deixa 164
  lugares)". Ele não pegou o médio 5 por dois motivos:
  - `New-Item -ItemType Directory` não está na lista de palavras da K01;
  - o arquivo já tem 50 lugares de conversa com o Windows aceitos como exceção.
- **O que ele não pode pegar.** Uma mesma lógica escrita de dois jeitos, como o médio 2: é texto diferente fazendo a
  mesma coisa.

## 4.5 A Central de decisões

- **O que é.** Uma página do claude.ai, um "artifact" com banco de dados:
  https://claude.ai/artifact/XNFrsdVR7q4K8cBcxNftZy. Só abre logado na conta do Samuel. **O código da página não
  está no git**: ele só é lido e publicado pela ferramenta de artifacts da conversa gerente.
- **Para que serve.** É onde o Samuel responde perguntas com imagens grandes, escolhe uma opção, comenta, dá
  ordens e registra testes. As respostas ficam gravadas na hora.
- **As abas:** Decidir agora · Conferência · Respostas · Quadro dos trabalhos · Etapas · Agentes · Defeitos ·
  Velocidade · Ordens e ideias.
- **As coleções do banco:**
  - `respostas`: o que ele escolheu e comentou. A gerente responde no próprio documento, com os campos
    `gerente`, `gerenteEm` e `lida`, e com `reabrir`/`anteriores` para pedir uma resposta de novo sem perder a
    antiga.
  - `conferencias`: um relatório por aba.
  - `ordens`, `testes`, `ideias` e `config`: escritas pela página. A gerente marca `estado`.
  - O resto, gerado pela gerente.
- **Como é alimentada:**
  1. A gerente mantém `docs/plano/central/fonte.json`, com as chaves `geral`, `trabalhos`, `agentes` e
     `velocidade`.
  2. `docs/plano/para_a_central.py` junta esse arquivo com o plano, o `memoria/bugs.md` e o git, e grava lotes
     JSON em `D:\programas\EditorImpressao-arquivos\central-banco\`.
  3. A gerente grava esses lotes no banco, de 50 em 50, com a ferramenta de dados de artifacts (ação `batch`).
  4. As abas da Conferência saem de `docs/plano/central/extrair_conferencia.py`, e há 18 arquivos em
     `docs/plano/central/conferencias/`.
- **As regras de escrita** estão no `CLAUDE.md` §10.10 e §11.13. São dez pontos sobre como perguntar ao Samuel,
  tirados de 106 casos de "Ainda não entendi" e 176 comentários dele. Há também um modelo de print com faixas
  coloridas de antes e depois, em `docs/plano/central/modelo-de-print/`.
- **Outras páginas** do mesmo tipo: "Escolhas do Editor de Impressão", "Layout do Editor de Impressão" e "Quando
  revisar uma página". Os endereços estão no `CLAUDE.md` §10.10.
- **Situação:** o quadro dos trabalhos não é atualizado desde 18/11.

## 4.6 Como um trabalho anda, do pedido ao programa

1. O Samuel pede, no chat ou na Central. A gerente grava a decisão no Livro, com as palavras dele, e no Registro
   do plano.
2. A gerente escreve o pedido ao agente. Ele leva as decisões que tocam aquilo e as regras de que o agente lê o
   arquivo dele, o `CLAUDE.md` inteiro e o índice da memória.
3. O agente escreve no seu `ONDE-PAREI.md`, antes de mexer:
   - as decisões que precisa cumprir;
   - o que já está escolhido e testado;
   - como fica para quem usa;
   - a causa;
   - os caminhos que chegam na função;
   - a lista das falhas.

   Depois faz o código e os testes, e entrega à gerente.
4. A gerente manda a rodada inteira no GitHub. Depois vem um agente novo que tenta quebrar.
5. Se ele acha problema, volta para o escritor, numa nova "volta".
6. Quando não acha mais nada, o trabalho entra na versão de teste e o Samuel testa no PC dele. Só ele marca
   aprovado.

## 4.7 O que não está funcionando

Fatos:

- **As regras crescem e os erros continuam.**
  - A seção 11 do `CLAUDE.md` nasceu em 26/10/2026 e tem hoje 13 regras.
  - A regra 12 ("sem gambiarra") ocupa mais de uma página. Foi escrita em 13/11 e estendida a todo o código em
    18/11.
  - De 18 a 22/11 entraram mais decisões de processo: D-796 a D-798, D-807, D-811 a D-813, D-815, D-819 e
    D-827. Várias ainda não viraram texto nas regras.
- **Antes de trabalhar, cada agente lê cerca de 95 KB de regras:** o `CLAUDE.md` (71 KB), o arquivo dele (10 a 14 KB) e o índice (12 KB). Mais
  as decisões copiadas no pedido.
- **O caso do atualizador:** 4 consertos pedidos em 21/11 já levaram 4 voltas, mais uma prova à vista no PC do
  Samuel, e a quinta volta está pendente. A volta 4 foi escrita por um agente que leu a regra 12. Mesmo assim, o
  agente seguinte achou 5 problemas médios, dois deles do tipo que a regra proíbe:
  - a mesma leitura do arquivo de estado com duas regras, uma no vigia e outra no script da troca;
  - a pasta segura criada por `New-Item` próprio em vez de `core.windows.criar_pasta_segura`.

  Detalhe na Parte 2.
- **O mesmo padrão antes do atualizador:** o Girar, o "Só as letras", o "usar em todas" e o Automático. A revisão de
  código de 10/11 achou 17 remendos desse tipo. Detalhe na Parte 1, seção "Os outros ciclos".
- **A gerente também falhou.**
  - Passou a volta 4 para a conferência sem procurar duplicação antes.
  - Em 23/11 disse ao Samuel que não havia barreira automática. O porteiro (acima) existe desde 19/11. As regras e
    os documentos já são tantos que a própria gerente perde o que está construído.

## 4.8 Anatomia dos ciclos

Fatos tirados das Partes 1 e 2. Os casos são o Girar, as três contas do "como fica com este filtro", o "usar em
todas", o Automático contra o "não dividir esta", a lista "o que é do filtro" e a volta 4 do atualizador. O ciclo
tem sempre os mesmos passos:

1. **O pedido chega como um caso.** O Samuel vê um defeito ou decide algo olhando uma página, um botão, um item do
   "aplicar em". A decisão é gravada com as palavras dele sobre aquele caso.
2. **O conserto vai para o lugar onde o caso apareceu.** O agente muda o método que o print mostra. A regra não mora
   num lugar só: fica espalhada em métodos parecidos de `ui/tela_conferir.py` (10.187 linhas) ou em textos de
   PowerShell montados dentro de `atualizacao.py` (2.314 linhas).
   - Exemplo do programa: a D-662 entrou só no "todas as folhas" do Girar.
   - Exemplo do atualizador: a leitura que tenta de novo entrou só no vigia.
3. **O teste prova o caso pedido.** Ninguém cobra que todos os caminhos deem o mesmo resultado. Então a divergência não
   deixa nenhum teste vermelho.
4. **O Samuel ou o agente que tenta quebrar acha o mesmo defeito no caminho vizinho.** Abre-se uma volta nova.
   - O Girar levou 9 voltas.
   - As figurinhas e o "comparar" levaram 5.
   - O porteiro (o passo 0 da parte do Windows) teve 6 rodadas de conferência, com 19, 9, 7, 6, 3 e 1 achados.
5. **Quando o defeito é de efeito colateral, entra uma proteção nova em vez de sair a causa.** Na volta 4 do
   atualizador, quatro peças que só protegem outra nasceram num commit só (`586b483f`). Três dos cinco problemas novos
   moram nelas.

Dois fatos agravam o ciclo:

- **O que se sabe errado não é desfeito.** Dos 17 remendos que a revisão de 10/11 listou, 16 continuam no código. A
  decisão D-765, de 17/11, congelou os consertos do programa até a entrega ao Kaique, e o código novo continua sendo
  escrito em cima deles.
- **A resposta a cada ciclo foi escrever uma regra nova.** A regra 12 ("sem gambiarra") nasceu do Girar em 13/11. A
  ampliação de 18/11 nasceu do atualizador. A volta 4 foi escrita depois das duas e repetiu o padrão.

O único caso em que o ciclo fechou foi o "Tirar o fundo" (caso 6 da Parte 1). Ali o dado passou a ter uma função só
em `core/`, e os caminhos foram levados até ela.

## 4.9 Opinião da gerente (separada)

- Escrever mais regra não segurou o erro. O que segurou foi o agente que tenta quebrar, e ele só entra no fim da
  volta, quando o código já está escrito.
- Parte das voltas do atualizador vem do desenho dele: peças que existem para proteger outras peças nossas. Cada
  conserto acrescentou uma peça em vez de tirar uma causa. A Parte 2 diz quais peças parecem ser assim.
- O peso de leitura antes de cada tarefa (regras longas, documentos de centenas de KB) provavelmente atrapalha mais
  do que ajuda. Isso é palpite, não medição.


---

# Parte 5. O que queremos que você responda

1. **O atualizador e os testes à distância estão complicados demais?** A Parte 2 mostra que quase tudo vem de uma
   escolha: quem troca a versão é uma tarefa SYSTEM que roda o próprio `.exe` instalado. Dado o que o Samuel pediu
   (Parte 2.1, principalmente D-733 e D-736), qual seria o desenho mais simples? Vale a pena refazer, ou consertar os 5
   problemas e seguir?
2. **Por que o ciclo se repete?** A seção 4.8 descreve o mesmo padrão em seis casos. Qual é a causa de verdade: o
   código (regras espalhadas numa tela de 10 mil linhas, PowerShell montado como texto), o jeito de trabalhar (pedido
   por caso, conserto por volta, regra nova a cada falha) ou os dois?
3. **O jeito de trabalhar está pesado demais?** Cada agente lê cerca de 95 KB de regras antes de começar, e o Livro tem
   mais de 800 decisões. O que você cortaria, e o que manteria? O agente novo que tenta quebrar é o que mais acha
   defeito.
4. **O porteiro existe e não pegou o problema.** Como deixar essa barreira útil de verdade? Ampliar as palavras, diminuir
   as 164 exceções, ou outro tipo de conferência?
5. **Os 16 remendos conhecidos do programa** continuam no código, congelados até a entrega ao Kaique. Isso deve mudar de
   ordem?
6. **Algo que não perguntamos** e que você faria diferente.

**Como responder.** Sua resposta vai para a gerente, que vai explicar ao Samuel em português simples e levar as
escolhas a ele. Separe o que é certeza do que é palpite. Diga também o que você precisaria ler a mais para ter
certeza.


---

# Anexo. Editor de Impressão — árvore, dependências e montagem do .exe

Escrito em 23/11/2026 pelo agente pesquisador, só lendo o código (nenhuma linha mudou).
Código lido: ramo `obra-2026-10-26` (a "versão de teste", o programa de hoje), commit
`0f58346ae3c49f10a07ec5abc8411d9f441da946` (conferido: está em `origin/obra-2026-10-26`).
Links abaixo: `O/<caminho>#L<n>` = `https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/<caminho>#L<n>`.

## 1. Árvore (só o que importa)

Contado com `git ls-files` no commit acima (arquivos no git por pasta, entre parênteses).

```
EditorImpressao/
├─ main.py                ponto de entrada; excepthook; atende --servidor-de-paginas e --conferir-ocr antes de abrir janela
├─ modelos.py             ConfigFolha, ConfigPagina, Projeto, Acao (o modelo de dados)
├─ projetos.py            gravar/abrir projetos em %LOCALAPPDATA%\EditorImpressao (gravação por trás, cópias de segurança)
├─ historico_acoes.py     desfazer/refazer ilimitado (acoes.jsonl)
├─ historico.py, configuracoes.py, atalhos.py, registro.py   livros recentes, preferências, atalhos, erros.log
├─ versao.py              o número da versão (único lugar; hoje "1.1.0")
├─ atualizacao.py, assinatura.py, servidor_das_versoes.py, publicar_versao_kaique.py
│                         atualizador (Velopack) e publicação; ficam com outro agente, só cito que existem
├─ empacotar.py, instalador.iss, montar_motor_kraken.py, compilar_*.py   montar o .exe, o instalador, o motor do Kraken e as DLLs
├─ avaliar.py, avaliar_selecao.py, conferencia.py, conferir.py           réguas e páginas de conferência
├─ teste_*.py (19)      scripts de teste soltos na raiz, fora do pytest; o principal é teste_botoes.py (clica em todos os botões)
├─ core/ (67)             todo o processamento; não importa nada de ui/ (O/core/__init__.py#L3)
│  └─ nativo/             st_gravura.dll e st_ferramentas.dll: código original do ScanTailor Advanced compilado (GPL-3)
├─ ui/ (49)               as telas em PySide6; ui/widgets/ = peças (painéis, prévia, tira, grade, trilha de ferramentas)
├─ tests/ (269)           o pytest: 258 arquivos test_*.py, 64 deles test_decisoes*.py (provas das decisões do Samuel)
├─ terceiros/scantailor-advanced/ (268)   fonte original do ScanTailor Advanced v1.2.1 + a "cola" em C nossa (ligacao*/)
├─ motor_kraken/ (2)      servidor_kraken.py + requisitos-travados.txt do motor à parte (Python 3.12)
├─ docs/plano/ (69)       DECISOES.md (Livro de decisões), PLANO-DEFINITIVO.md, ESTADO-ATUAL.md, prints de bugs
├─ docs/pesquisa/ (8)     pesquisas de código de fora
├─ memoria/ (209)         memória por assunto (fichas de itens, livros, páginas de teste, catálogo de erros)
├─ relatorios/ (3912)     relatórios de cada trabalho e conferência (.md/.html/.pdf + prints)
├─ regras_dos_agentes/ (18), .claude/agents/   regras dos agentes de IA que trabalham no projeto
├─ gabarito/ (5)          lista das páginas-gabarito (as imagens ficam fora do git)
├─ modelos/               redes neurais, FORA do git: doclayout.onnx, mobile_sam/, doctr/, tessdata/
├─ recursos/, arte/       brasão e ícones
└─ velhos/                o EditorImpressao.spec antigo, guardado por decisão
```

## 2. Dependências externas

Fonte: [`requirements.txt`](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/requirements.txt)
(não há `pyproject.toml` nem `setup.py`). "No .venv" = versão instalada hoje em `D:\programas\EditorImpressao\.venv`
(lida nos `*.dist-info`). Python do programa: 3.14 (o GitHub usa 3.14.3, `.github/workflows/testes-windows.yml` L98, ramo
`claude/list-server-files-gkos8v`). Licenças: as marcadas (CLAUDE) vêm do CLAUDE.md §3; (req) do comentário do
requirements; (LICENSE) do arquivo no repositório; as outras são **de memória, não conferi** no arquivo da licença.

| Pacote | Pedido | No .venv | Para que o programa usa | Licença |
|---|---|---|---|---|
| PySide6 | >=6.9 | 6.11.1 | toda a interface (Qt); as DLLs do ScanTailor usam o mesmo Qt 6.11.1 | LGPL-3 (CLAUDE) |
| PyMuPDF | >=1.24 | 1.28.0 | única porta de PDF: ler páginas, escrever o PDF final, cadernos (`core/pdf_io.py`, `core/cadernos.py`) | AGPL-3 (CLAUDE) |
| opencv-python | >=4.10 | 5.0.0.93 | operações de imagem em todo `core/` | Apache-2.0 (CLAUDE) |
| numpy | >=2.0 | 2.5.1 | imagens como matrizes | BSD (CLAUDE) |
| Pillow | >=10.0 | 12.3.0 | ler/gravar imagens, prints | HPND (CLAUDE) |
| doxapy | >=0.9.9 | 0.9.9 | binarização (Sauvola e outros) do Preto e branco | CC0 (CLAUDE) |
| scikit-image | >=0.24 | 0.26.0 | operações morfológicas e de medida (traz o scipy) | BSD (CLAUDE) |
| onnxruntime | >=1.28.0 | 1.28.0 | roda as redes que só apontam: doclayout (gravura/letra) e MobileSAM (seleção por clique) | MIT (de memória) |
| onnxtr | ==0.9.0 (travado) | 0.9.0 | detector de texto docTR `fast_base` (`core/ocr_doctr.py`; usa método interno, por isso travado) | Apache-2.0 (de memória) |
| pyclipper | ==1.4.0 (travado) | 1.4.0 | alarga as caixas do docTR, por dentro do OnnxTR | MIT (de memória) |
| velopack | ==1.2.161 (travado) | 1.2.161 | atualização pela internet (`atualizacao.py`); travado na mesma versão do `vpk` | MIT (req) |
| markdown | >=3.10.3 | 3.10.3 | relatórios `.md` → `.html`/`.pdf` (`relatorio.py`) | BSD (de memória) |
| pytest | >=8.0 | 9.1.1 | testes | MIT (de memória) |
| pyinstaller | >=6.0 | 6.21.0 | monta o `.exe` | GPL-2 com exceção do bootloader (de memória) |

Fora do `requirements.txt`:

| Peça | Versão | Para que | Onde | Licença |
|---|---|---|---|---|
| ScanTailor Advanced (código-fonte) | v1.2.1 | detector de gravura, limpar pontinhos, dividir, endireitar, caixas, compilados em `core/nativo/*.dll` e chamados por `ctypes` | `terceiros/scantailor-advanced/` | GPL-3 (LICENSE) |
| Motor do Kraken | kraken 7.1.1, torch 2.14.0 (CPU), Python 3.12 embutível | segunda opinião das linhas de texto do "Só as letras"; processo à parte | `motor_kraken/requisitos-travados.txt`, `montar_motor_kraken.py` | Kraken Apache-2.0, PyTorch BSD (de memória) |
| Tesseract (UB Mannheim) | 5.4.0 | OCR instalado, desligado de fábrica | levado por `empacotar.py` (L64) | Apache-2.0 (de memória) |
| Visual C++ Redistributable | oficial Microsoft | DLLs que o programa precisa; conferido pela assinatura digital | `empacotar.py` (L68-80) | licença da Microsoft |
| Redes neurais | doclayout.onnx, MobileSAM, docTR rep_fast_base | só apontam onde está gravura, letra, texto (nunca desenham) | `modelos/`, fora do git; caminhos em `core/detectar_regioes.py` L158, `core/rede_selecao.py` L29-31, `core/ocr_doctr.py` L100 | não conferi |
| Inno Setup 6 | — | instalador antigo da "pasta portátil" (`ISCC.exe`) | `instalador.iss` | licença própria do Inno (de memória) |
| vpk (Velopack) + WiX | vpk 1.2.161 | pacote de atualização e o `.msi` | `empacotar.py` L1192 (`VERSAO_DO_VPK`) | MIT / MS-RL (de memória) |

Roda no PC do Samuel (Windows 11, Python 3.14, GTX 1650; o pacote é o `onnxruntime` comum, não o `-gpu`, então as redes rodam no processador: dedução pelo nome do pacote) e no notebook do
Kaique (i5-1235U, sem placa de vídeo) **pelo que o código diz**; o notebook só recebeu o teste de velocidade da Fase 0
(não conferi o resultado).

## 3. Como o `.exe` e o instalador são montados

- **Script único:** [`empacotar.py`](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/empacotar.py)
  (2036 linhas). Modos `tudo | pasta | arquivo | instalador | entrega` (`main`, L1971).
- **PyInstaller** monta a versão em pasta (`onedir`, `--contents-directory _internal`) e o arquivo único do pendrive
  (`comando_do_pyinstaller`, L859; `_pyinstaller`, L907). O script põe junto os modelos, as DLLs do ScanTailor, o
  docTR, o motor do Kraken, o Tesseract e o Visual C++, e **para antes de gerar** se faltar alguma peça; depois confere
  que cada peça chegou (cabeçalho, L29-106).
- **Três saídas, descritas num lugar só** (`Saida`, `PORTATIL`, `ATUALIZACAO`, `INSTALADOR`, L228-268): a pasta
  portátil (o Inno Setup a empacota em `dist\EditorImpressao-Setup.exe`, `instalador.iss`); a atualização do Velopack
  (sem o motor do Kraken, que é publicado à parte); e o instalador `.msi` feito pelo `vpk` (que chama o WiX). O `vpk`
  roda só por `rodar_vpk` (L1530).
- **Publicar** uma versão para o Kaique é outro script, `publicar_versao_kaique.py` (assina, sobe ao GitHub); é do
  agente do atualizador.
- **DLLs do ScanTailor:** `compilar_detector_gravura.py` e `compilar_st_ferramentas.py` (CMake + Visual Studio 2022
  Build Tools, Qt 6.11.1 qtbase e Boost 1.78 baixados e conferidos pela soma).
