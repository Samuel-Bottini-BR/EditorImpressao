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
