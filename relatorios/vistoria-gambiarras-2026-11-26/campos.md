# Campos de ConfigPagina / ConfigFolha: todo lugar de `core/` e `ui/` que grava neles

Gerado em 26/11/2026 por `relatorios/vistoria-gambiarras-2026-11-26/campos_que_gravam.py`, lendo o codigo com `ast` (sem importar nem rodar o programa). Insumo da vistoria de gambiarras (CLAUDE.md §11.12: o mesmo campo gravado em lugares diferentes e suspeita obrigatoria).

## Leia antes (ressalvas)

- **A tabela nao sabe o tipo do objeto.** Toda gravacao de atributo com o nome de um campo entra, de qualquer objeto. Quando o nome tambem e atributo de outra classe do nosso codigo (coluna "nome exclusivo?", ex.: `recorte`, `alertas`, `indice`), a linha PODE NAO SER de ConfigPagina/ConfigFolha: confira no codigo. Objetos de biblioteca (Qt, numpy, PyMuPDF) nao entram nessa conferencia.
- **"(self de Classe)"** marca a linha cujo receptor e `self` dentro de uma classe que nao e ConfigPagina/ConfigFolha: e fato lido na AST, e quase certamente NAO e o campo. A coluna "sem self de outra" do resumo conta sem essas linhas.
- **Nao pega:** apelido de lista (`l = pagina.alertas; l.append(...)`); troca da pagina inteira por outra (`deepcopy`, `projeto.paginas[i] = nova`); dicionario do projeto.json (`d["filtro"] = ...`); `exec`/`eval`/`getattr(x, n).append(...)`; e as gravacoes de dentro de `modelos.py` (migracao em `Projeto.de_dicionario`, `guardar_selecao`), dos scripts da raiz e de `tests/`.
- **Pega:** `x.campo =`, `+=` e demais compostos, atribuicao multipla e desempacotada, `for`/`with` com o campo como alvo, `del`, `setattr(x, "campo")` (e com o nome numa constante de texto do modulo), `object.__setattr__`, `dataclasses.replace(x, campo=)`, `ConfigPagina(...)`/`ConfigFolha(...)` por nome e por posicao, e mutacao no lugar (`.append/.extend/.insert/.pop/.remove/.clear/.update/...`, `x.campo[i] =`, `del x.campo[i]`, tambem por dentro de indices).
- **Boa parte da tela e do Automatico grava por dados**: monta `{"filtro": v}` e um aplicador generico faz `setattr(pagina, campo, v)` (`core/automatico._Gravador`, `historico_acoes.py`). Essa gravacao nao aparece ligada ao campo. Por isso cada campo traz tambem "nome como texto": os lugares onde o nome esta escrito como texto (chave de dicionario, `dict(campo=)`, `d["campo"] =`, argumento de funcao fora `getattr`/`hasattr`, item de lista/tupla). Isso NAO e contado como gravacao: muitas sao leituras ou listas de nomes. Campo com zero gravacoes e varias mencoes por texto quase certamente e gravado por esse caminho indireto.
- O que nao da para saber o campo (nome variavel, `**algo`, `__dict__`, `vars`) esta numa lista a parte, no fim do resumo. Ali podem estar gravacoes em QUALQUER campo, inclusive nos que aparecem com zero.
- "Funcoes diferentes" conta pares (arquivo, funcao); funcoes internas e `<lambda>` contam a parte (`Classe.metodo.interna`).

**Numeros:** 63 campos (18 de ConfigFolha, 51 de ConfigPagina, 6 nas duas); 166 gravacoes achadas em 23 arquivos; 42 campos com alguma gravacao; 486 mencoes do nome como texto; 12 gravados ao mesmo tempo em `ui/` e em `core/`; 22 gravacoes sem campo sabido (contando `historico_acoes.py`); 114 arquivos lidos.

## Resumo (os campos com mais lugares primeiro)

Ordem: funcoes diferentes, depois gravacoes, depois arquivos. "UI+CORE" = gravado em `ui/` e em `core/`.

| campo | classe | funcoes | gravacoes | arquivos | sem self de outra (func./grav.) | ui e core | nome como texto (lugares/arquivos) | nome exclusivo? |
|---|---|---:|---:|---:|---:|---|---:|---|
| `alertas` | ConfigFolha e ConfigPagina (campo nas DUAS) | 22 | 35 | 4 | 22/35 | **UI+CORE** | 8/5 | NAO: tambem e atributo de MedidaDaFolha (core/automatico.py), Pagina (teste_bateria.py), ResultadoLivro (avaliar.py) |
| `indice` | ConfigFolha e ConfigPagina (campo nas DUAS) | 15 | 17 | 9 | 10/12 | **UI+CORE** | 1/1 | NAO: tambem e atributo de Aviso (core/avisos.py), InfoPagina (core/pdf_io.py), ItemDaGrade (ui/widgets/todas_as_paginas.py), MedidaDaFolha (core/automatico.py), TarefaPreviaDoAutomatico (ui/tarefas.py), TelaCheiaDoPDF (ui/widgets/folhear_pdf.py), _FolhaDaVez (core/pipeline.py), _FolhaParaMedir (core/automatico.py), _Tarefa (ui/widgets/paginas_rolando.py) |
| `filtro` | ConfigPagina | 15 | 15 | 9 | 10/10 | **UI+CORE** | 18/11 | NAO: tambem e atributo de CartaoFiltro (ui/widgets/cartao_filtro.py), Entrada (historico.py), FonteDoPrograma (conferencia.py), PainelFiltroDaPagina (ui/widgets/paineis.py), Regiao (core/selecao.py), _TarefaDasOpcoes (ui/widgets/filtros_tela_cheia.py), _TarefaPrevia (ui/tarefas.py) |
| `metade` | ConfigPagina | 8 | 8 | 4 | 6/6 | **UI+CORE** | 2/1 | NAO: tambem e atributo de TodasAsPaginas (ui/widgets/todas_as_paginas.py) |
| `revisada` | ConfigFolha e ConfigPagina (campo nas DUAS) | 8 | 8 | 2 | 8/8 | so core | 23/4 | sim, so destas classes |
| `folha` | ConfigPagina | 5 | 5 | 4 | 4/4 | **UI+CORE** | 25/7 | NAO: tambem e atributo de ItemDaGrade (ui/widgets/todas_as_paginas.py), TarefaFolhaDoCaderno (ui/widgets/folhas_do_caderno.py) |
| `posicao_corte` | ConfigFolha | 5 | 5 | 3 | 3/3 | **UI+CORE** | 10/3 | NAO: tambem e atributo de MedidaDaFolha (core/automatico.py), Visualizador (ui/widgets/visualizador.py), _FolhaParaMedir (core/automatico.py) |
| `apagada` | ConfigFolha e ConfigPagina (campo nas DUAS) | 4 | 5 | 2 | 3/4 | **UI+CORE** | 7/4 | NAO: tambem e atributo de ItemDaGrade (ui/widgets/todas_as_paginas.py), Miniatura (ui/widgets/tira_miniaturas.py) |
| `selecao` | ConfigPagina | 4 | 4 | 3 | 2/2 | **UI+CORE** | 12/5 | NAO: tambem e atributo de EditorSelecao (ui/widgets/editor_selecao.py) |
| `gravura_feita_com` | ConfigPagina | 4 | 4 | 2 | 4/4 | **UI+CORE** | 2/2 | sim, so destas classes |
| `geometria_das_zonas` | ConfigPagina | 3 | 4 | 2 | 3/4 | so core | 7/5 | sim, so destas classes |
| `dividir` | ConfigFolha | 3 | 3 | 2 | 3/3 | so core | 11/4 | NAO: tambem e atributo de MedidaDaFolha (core/automatico.py), _FolhaParaMedir (core/automatico.py) |
| `e_paisagem` | ConfigFolha | 3 | 3 | 2 | 3/3 | so core | 2/2 | NAO: tambem e atributo de Lombada (core/dividir.py), MedidaDaFolha (core/automatico.py) |
| `em_branco` | ConfigPagina | 3 | 3 | 2 | 3/3 | so core | 8/4 | NAO: tambem e atributo de Medidas (teste_livros.py) |
| `forca_preto` | ConfigPagina | 3 | 3 | 2 | 2/2 | **UI+CORE** | 6/3 | NAO: tambem e atributo de _TarefaCartoes (ui/tarefas.py) |
| `mexida_a_mao` | ConfigFolha e ConfigPagina (campo nas DUAS) | 3 | 3 | 2 | 3/3 | so core | 10/5 | sim, so destas classes |
| `forca_antes_do_reforco` | ConfigPagina | 3 | 3 | 1 | 3/3 | so core | 2/2 | sim, so destas classes |
| `gravura_forma` | ConfigPagina | 2 | 5 | 2 | 2/5 | so ui | 11/5 | NAO: tambem e atributo de Projeto (modelos.py) |
| `dividir_como` | ConfigFolha | 2 | 2 | 2 | 2/2 | **UI+CORE** | 13/5 | NAO: tambem e atributo de Fotografia (core/automatico.py), Projeto (modelos.py) |
| `endireitar_como` | ConfigPagina | 2 | 2 | 2 | 2/2 | **UI+CORE** | 7/4 | NAO: tambem e atributo de Projeto (modelos.py), _FolhaParaMedir (core/automatico.py) |
| `fundo_tirado` | ConfigPagina | 2 | 2 | 2 | 2/2 | so core | 1/1 | sim, so destas classes |
| `tem_cor` | ConfigPagina | 2 | 2 | 2 | 2/2 | so core | 2/2 | NAO: tambem e atributo de Medidas (teste_livros.py), Pagina (teste_bateria.py) |
| `confianca_corte` | ConfigFolha | 2 | 2 | 1 | 2/2 | so core | 4/3 | NAO: tambem e atributo de MedidaDaFolha (core/automatico.py), Medidas (teste_livros.py), Pagina (teste_bateria.py) |
| `faixa_na_beirada` | ConfigPagina | 2 | 2 | 1 | 2/2 | so core | 1/1 | sim, so destas classes |
| `recorte` | ConfigPagina | 2 | 2 | 1 | 0/0 | so ui | 21/6 | NAO: tambem e atributo de Visualizador (ui/widgets/visualizador.py) |
| `reforco_desfeito` | ConfigPagina | 2 | 2 | 1 | 2/2 | so core | 2/2 | sim, so destas classes |
| `sobra` | ConfigFolha | 2 | 2 | 1 | 2/2 | so core | 7/2 | NAO: tambem e atributo de MedidaDaFolha (core/automatico.py) |
| `alertas_aceitos` | ConfigFolha e ConfigPagina (campo nas DUAS) | 1 | 1 | 1 | 1/1 | so core | 7/5 | sim, so destas classes |
| `angulo_detectado` | ConfigFolha | 1 | 1 | 1 | 1/1 | so core | 1/1 | NAO: tambem e atributo de MedidaDaFolha (core/automatico.py) |
| `angulo_manual` | ConfigPagina | 1 | 1 | 1 | 1/1 | so ui | 9/4 | sim, so destas classes |
| `automatico` | ConfigPagina | 1 | 1 | 1 | 0/0 | so ui | 15/7 | NAO: tambem e atributo de ColunaDePaineis (ui/widgets/paineis.py) |
| `confianca_angulo` | ConfigFolha | 1 | 1 | 1 | 1/1 | so core | 1/1 | NAO: tambem e atributo de MedidaDaFolha (core/automatico.py), Medidas (teste_livros.py), Pagina (teste_bateria.py) |
| `gravura_achada_a_mao` | ConfigPagina | 1 | 1 | 1 | 1/1 | so core | 3/3 | sim, so destas classes |
| `inserida` | ConfigPagina | 1 | 1 | 1 | 1/1 | so core | 2/1 | sim, so destas classes |
| `limpar_pontinhos` | ConfigPagina | 1 | 1 | 1 | 1/1 | so ui | 10/5 | NAO: tambem e atributo de Projeto (modelos.py) |
| `marcacao_provisoria` | ConfigPagina | 1 | 1 | 1 | 1/1 | so core | 4/4 | sim, so destas classes |
| `metades_guardadas` | ConfigFolha | 1 | 1 | 1 | 1/1 | so core | 4/1 | sim, so destas classes |
| `misto_fora_do_texto` | ConfigPagina | 1 | 1 | 1 | 1/1 | so ui | 11/6 | NAO: tambem e atributo de Projeto (modelos.py) |
| `misto_letras_na_moldura` | ConfigPagina | 1 | 1 | 1 | 1/1 | so ui | 11/6 | NAO: tambem e atributo de Projeto (modelos.py) |
| `misto_papel_da_gravura` | ConfigPagina | 1 | 1 | 1 | 1/1 | so ui | 11/6 | NAO: tambem e atributo de Projeto (modelos.py) |
| `misto_so_as_letras` | ConfigPagina | 1 | 1 | 1 | 1/1 | so ui | 15/6 | NAO: tambem e atributo de Projeto (modelos.py) |
| `rotacao` | ConfigFolha | 1 | 1 | 1 | 0/0 | so ui | 9/3 | NAO: tambem e atributo de CamadasDaPagina (core/camadas.py), _FolhaParaMedir (core/automatico.py), _TarefaPrevia (ui/tarefas.py) |
| `algoritmo_preto_branco` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 11/5 | sim, so destas classes |
| `alinhar_com_as_outras` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 2/2 | sim, so destas classes |
| `clareza_melhorar` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 4/3 | sim, so destas classes |
| `claro_no_escuro` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 10/5 | sim, so destas classes |
| `conteudo_deslocamento` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 6/4 | sim, so destas classes |
| `conteudo_escala` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 5/3 | sim, so destas classes |
| `desentortar` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 1/1 | sim, so destas classes |
| `desentortar_aumentar` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 2/1 | sim, so destas classes |
| `giro_da_pagina` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 6/3 | sim, so destas classes |
| `gravuras_em_tons_de_cinza` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 11/5 | sim, so destas classes |
| `intensidade_magico` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 4/3 | sim, so destas classes |
| `letras_com_a_cor` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 13/5 | sim, so destas classes |
| `linha_a_mao` | ConfigFolha | 0 | 0 | 0 | 0/0 | - | 2/1 | sim, so destas classes |
| `luz_chuvisco` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 11/5 | sim, so destas classes |
| `luz_igualar` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 11/5 | sim, so destas classes |
| `luz_suavizar` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 10/5 | sim, so destas classes |
| `reduzir_cores` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 13/5 | sim, so destas classes |
| `respeitar_gravuras_achadas` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 11/5 | sim, so destas classes |
| `retangulo_do_corte` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 9/5 | NAO: tambem e atributo de Projeto (modelos.py) |
| `tamanho_folha_cm` | ConfigPagina | 0 | 0 | 0 | 0/0 | - | 5/3 | sim, so destas classes |
| `tampa_do_scanner` | ConfigFolha | 0 | 0 | 0 | 0/0 | - | 3/3 | sim, so destas classes |

### Gravacoes em que nao da para saber o campo

| onde | funcao | forma |
|---|---|---|
| `core/automatico.py:472` | `livro_leve` | `setattr(projeto, campo, False) (nome do atributo variavel)` |
| `core/automatico.py:560` | `fotografar` | `setattr(livro, campo, copy.deepcopy(valor)) (nome do atributo variavel)` |
| `core/automatico.py:702` | `_Gravador.no_livro` | `setattr(self.projeto, campo, valor) (nome do atributo variavel)` |
| `core/automatico.py:708` | `_Gravador.na_folha` | `setattr(folha, campo, valor) (nome do atributo variavel)` |
| `core/automatico.py:723` | `_Gravador.na_pagina` | `setattr(pagina, campo, valor) (nome do atributo variavel)` |
| `core/automatico.py:884` | `aplicar` | `setattr(novas, campo, opcoes.get(campo, getattr(projeto, campo))) (nome do atributo variavel)` |
| `core/dividir_a_mao.py:136` | `metades_da_pagina` | `replace(..., **copy.deepcopy(limpos))` |
| `core/dividir_a_mao.py:163` | `pagina_inteira_das` | `replace(..., **_limpos(base))` |
| `core/impressao.py:214` | `OpcoesDeImpressao.de_dicionario` | `setattr(opcoes, campo.name, valor) (nome do atributo variavel)` |
| `core/paginas_em_branco.py:85` | `pagina_em_branco_como` | `setattr(nova, campo, copy.deepcopy(getattr(padrao, campo))) (nome do atributo variavel)` |
| `core/perfis.py:159` | `aplicar` | `setattr(projeto, campo, copy.deepcopy(valor)) (nome do atributo variavel)` |
| `core/pipeline.py:2394` | `trocar_opcoes_da_gravura` | `setattr(projeto, campo, getattr(novas, campo)) (nome do atributo variavel)` |
| `historico_acoes.py:446` | `aplicar` | `setattr(projeto, nome, _restaurar_tipo(nome, valor)) (nome do atributo variavel)` |
| `historico_acoes.py:465` | `aplicar` | `setattr(item, campo, _restaurar_tipo(campo, valor[str(indice)])) (nome do atributo variavel)` |
| `historico_acoes.py:467` | `aplicar` | `setattr(item, campo, _restaurar_tipo(campo, valor)) (nome do atributo variavel)` |
| `historico_acoes.py:498` | `_aplicar_numa_pagina` | `setattr(projeto.paginas[indice], nome, _restaurar_tipo(nome, valor)) (nome do atributo variavel)` |
| `historico_acoes.py:515` | `_aplicar_numa_folha` | `setattr(projeto.folhas[indice], nome, _restaurar_tipo(nome, valor)) (nome do atributo variavel)` |
| `ui/automatico.py:463` | `EstadoDoAutomatico.frase` | `setattr(livro, campo, valor) (nome do atributo variavel)` |
| `ui/tela_conferir.py:1585` | `TelaConferir._mudar_no_editor` | `setattr(editor, campo, valor) (nome do atributo variavel)` |
| `ui/tela_conferir.py:8188` | `TelaConferir._medidor_arrastando` | `setattr(self.projeto.paginas[self.indice_pagina], campo, int(valor)) (nome do atributo variavel)` |
| `ui/tela_conferir.py:8222` | `TelaConferir._medidor_soltou` | `setattr(pagina, campo, antigo) (nome do atributo variavel)` |
| `ui/widgets/filtros_tela_cheia.py:131` | `pagina_com_as_opcoes` | `replace(..., **campos)` |

## Por campo

### `alertas`

ConfigFolha e ConfigPagina (campo nas DUAS) · nome exclusivo? NAO: tambem e atributo de MedidaDaFolha (core/automatico.py), Pagina (teste_bateria.py), ResultadoLivro (avaliar.py) · **35 gravacoes, 22 funcoes diferentes, 4 arquivos**

- `core/automatico.py:1219` · `_avisos_medidos` · x.alertas = ... · em `pagina`
- `core/automatico.py:1865` · `avisos_do_livro` · x.alertas = ... · em `folha`
- `core/automatico.py:1875` · `avisos_do_livro` · x.alertas = ... · em `pagina`
- `core/automatico.py:1884` · `avisos_do_livro` · x.alertas = ... · em `item`
- `core/pipeline.py:189` · `analisar_projeto` · x.alertas = ... · em `item`
- `core/pipeline.py:250` · `_analisar_a_folha` · x.alertas = ... · em `folha`
- `core/pipeline.py:270` · `_analisar_a_folha` · x.alertas = ... · em `pagina`
- `core/pipeline.py:1092` · `_anotar_aviso_da_pagina` · mutacao no lugar: x.alertas.insert(...) · em `pagina`
- `core/pipeline.py:1095` · `_anotar_aviso_da_pagina` · x.alertas = ... · em `pagina`
- `core/pipeline.py:1571` · `_anotar_corte_encostou` · x.alertas = ... · em `folha`
- `core/pipeline.py:1656` · `marcar_paginas_diferentes` · mutacao no lugar: x.alertas.append(...) · em `pagina`
- `core/pipeline.py:1666` · `_anotar_contas_discordam` · mutacao no lugar: x.alertas.insert(...) · em `pagina`
- `core/pipeline.py:1669` · `_anotar_contas_discordam` · x.alertas = ... · em `pagina`
- `core/pipeline.py:2014` · `_anotar` · mutacao no lugar: x.alertas.insert(...) · em `pagina`
- `core/pipeline.py:2017` · `_anotar` · x.alertas = ... · em `pagina`
- `core/pipeline.py:2561` · `garantir_selecao` · mutacao no lugar: x.alertas.append(...) · em `pagina`
- `core/pipeline.py:2729` · `_anotar_conferir` · mutacao no lugar: x.alertas.insert(...) · em `pagina`
- `core/pipeline.py:2732` · `_anotar_conferir` · x.alertas = ... · em `pagina`
- `core/pipeline.py:3054` · `_acertar_o_em_branco` · x.alertas = ... · em `pagina`
- `core/pipeline.py:3057` · `_acertar_o_em_branco` · x.alertas = ... · em `pagina`
- `core/pipeline.py:4052` · `acertar_aviso_do_reforco` · x.alertas = ... · em `pagina`
- `core/pipeline.py:4055` · `acertar_aviso_do_reforco` · x.alertas = ... · em `pagina`
- `core/pipeline.py:4137` · `_por_avisos_do_so_as_letras` · x.alertas = ... · em `pagina`
- `core/pipeline.py:4166` · `_acertar_alerta_do_misto` · x.alertas = ... · em `pagina`
- `core/pipeline.py:4212` · `acertar_faixa_do_livro` · x.alertas = ... · em `pagina`
- `core/pipeline.py:4215` · `acertar_faixa_do_livro` · x.alertas = ... · em `pagina`
- `core/pipeline.py:4311` · `acertar_alertas_de_cor` · x.alertas = ... · em `pagina`
- `core/pipeline.py:4313` · `acertar_alertas_de_cor` · mutacao no lugar: x.alertas.append(...) · em `pagina`
- `core/pipeline.py:4478` · `renderizar_com_filtro` · replace(x, alertas=...) · em `pagina`
- `core/pipeline.py:5199` · `_anotar_folha_maior` · x.alertas = ... · em `pagina`
- `ui/tela_conferir.py:2177` · `TelaConferir._conferir_tamanho_da_folha` · x.alertas = ... · em `pagina`
- `ui/tela_conferir.py:2188` · `TelaConferir._conferir_tamanho_da_folha` · mutacao no lugar: x.alertas.append(...) · em `pagina`
- `ui/tela_conferir.py:5115` · `TelaConferir._conferir_qualidade_do_preto_e_branco` · x.alertas = ... · em `pagina`
- `ui/tela_conferir.py:5117` · `TelaConferir._conferir_qualidade_do_preto_e_branco` · mutacao no lugar: x.alertas.append(...) · em `pagina`
- `ui/widgets/filtros_tela_cheia.py:131` · `pagina_com_as_opcoes` · replace(x, alertas=...) · em `pagina`

Nome como texto (8; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:1194` · `_avisos_medidos` · texto passado a g.na_folha(...)
  - `core/automatico.py:1209` · `_avisos_medidos` · texto passado a g.na_pagina(...)
  - `core/automatico.py:1220` · `_avisos_medidos` · texto passado a g.na_pagina(...)
  - `core/dividir_a_mao.py:88` · `(nivel do modulo)` · dict(alertas=...)
  - `core/paginas_em_branco.py:71` · `(nivel do modulo)` · item de tuple literal
  - `ui/desfazer_nesta_pagina.py:222` · `desfazer` · item de tuple literal
  - `ui/tela_conferir.py:6035` · `TelaConferir._com_os_avisos_de_agora` · item de tuple literal
  - `ui/tela_conferir.py:10058` · `(nivel do modulo)` · item de set literal

### `indice`

ConfigFolha e ConfigPagina (campo nas DUAS) · nome exclusivo? NAO: tambem e atributo de Aviso (core/avisos.py), InfoPagina (core/pdf_io.py), ItemDaGrade (ui/widgets/todas_as_paginas.py), MedidaDaFolha (core/automatico.py), TarefaPreviaDoAutomatico (ui/tarefas.py), TelaCheiaDoPDF (ui/widgets/folhear_pdf.py), _FolhaDaVez (core/pipeline.py), _FolhaParaMedir (core/automatico.py), _Tarefa (ui/widgets/paginas_rolando.py) · **17 gravacoes, 15 funcoes diferentes, 9 arquivos**

- `core/automatico.py:476` · `livro_leve` · ConfigFolha(indice=...) [classe certa: ConfigFolha]
- `core/automatico.py:478` · `livro_leve` · ConfigPagina(indice=...) [classe certa: ConfigPagina]
- `core/automatico.py:655` · `medir` · ConfigPagina(indice=...) [classe certa: ConfigPagina]
- `core/automatico.py:985` · `_dividir` · x.indice = ... · em `pagina`
- `core/dividir_a_mao.py:212` · `trocar_as_paginas_da_folha` · x.indice = ... · em `pagina`
- `core/ordem_das_paginas.py:75` · `renumerar` · x.indice = ... · em `pagina`
- `core/paginas_em_branco.py:124` · `por_as_inseridas` · x.indice = ... · em `pagina`
- `core/pipeline.py:166` · `analisar_projeto` · x.indice = ... · em `pagina`
- `core/pipeline.py:241` · `_analisar_a_folha` · ConfigFolha(indice=...) [classe certa: ConfigFolha]
- `core/pipeline.py:264` · `_analisar_a_folha` · ConfigPagina(indice=...) [classe certa: ConfigPagina]
- `core/pipeline.py:4776` · `_FolhaDaVez.__init__` · x.indice: T = ... · em `self` (self de _FolhaDaVez)
- `core/pipeline.py:4792` · `_pagina_pronta` · x.indice = ... · em `da_vez`
- `ui/desfazer_nesta_pagina.py:314` · `acrescentar_ao_menu` · x.indice = ... · em `submenu`
- `ui/tarefas.py:714` · `TarefaPreviaDoAutomatico.__init__` · x.indice = ... · em `self` (self de TarefaPreviaDoAutomatico)
- `ui/widgets/folhear_pdf.py:181` · `TelaCheiaDoPDF.__init__` · x.indice = ... · em `self` (self de TelaCheiaDoPDF)
- `ui/widgets/folhear_pdf.py:225` · `TelaCheiaDoPDF.ir_para` · x.indice = ... · em `self` (self de TelaCheiaDoPDF)
- `ui/widgets/paginas_rolando.py:109` · `_Tarefa.__init__` · desempacotada: x.indice = ... · em `self` (self de _Tarefa)

Nome como texto (1; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/pipeline.py:4773` · `_FolhaDaVez` · item de tuple literal

### `filtro`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de CartaoFiltro (ui/widgets/cartao_filtro.py), Entrada (historico.py), FonteDoPrograma (conferencia.py), PainelFiltroDaPagina (ui/widgets/paineis.py), Regiao (core/selecao.py), _TarefaDasOpcoes (ui/widgets/filtros_tela_cheia.py), _TarefaPrevia (ui/tarefas.py) · **15 gravacoes, 15 funcoes diferentes, 9 arquivos**

- `core/automatico.py:479` · `livro_leve` · ConfigPagina(filtro=...) [classe certa: ConfigPagina]
- `core/editar_zonas.py:158` · `pintada_de_branco` · x.filtro = ... · em `nova`
- `core/fundo_tirado.py:198` · `migrar_projeto_antigo` · x.filtro = ... · em `pagina`
- `core/pipeline.py:267` · `_analisar_a_folha` · ConfigPagina(filtro=...) [classe certa: ConfigPagina]
- `core/pipeline.py:4478` · `renderizar_com_filtro` · replace(x, filtro=...) · em `pagina`
- `ui/tarefas.py:920` · `_TarefaPrevia.__init__` · x.filtro = ... · em `self` (self de _TarefaPrevia)
- `ui/widgets/cartao_filtro.py:31` · `CartaoFiltro.__init__` · x.filtro = ... · em `self` (self de CartaoFiltro)
- `ui/widgets/editor_selecao.py:479` · `EditorSelecao._acrescentar` · x.filtro = ... · em `regiao`
- `ui/widgets/editor_selecao.py:1095` · `EditorSelecao._varinha` · x.filtro = ... · em `regiao`
- `ui/widgets/editor_selecao.py:1160` · `EditorSelecao._tudo_desta_cor` · x.filtro = ... · em `regiao`
- `ui/widgets/editor_selecao.py:1194` · `EditorSelecao.selecionar_com_a_rede` · x.filtro = ... · em `regiao`
- `ui/widgets/filtros_tela_cheia.py:94` · `_TarefaDasOpcoes.__init__` · desempacotada: x.filtro = ... · em `self` (self de _TarefaDasOpcoes)
- `ui/widgets/filtros_tela_cheia.py:131` · `pagina_com_as_opcoes` · replace(x, filtro=...) · em `pagina`
- `ui/widgets/paineis.py:1708` · `PainelFiltroDaPagina.__init__` · x.filtro = ... · em `self` (self de PainelFiltroDaPagina)
- `ui/widgets/paineis.py:1839` · `PainelFiltroDaPagina.atualizar` · x.filtro = ... · em `self` (self de PainelFiltroDaPagina)

Nome como texto (18; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:1062` · `_ligar_na_pagina` · texto passado a g.na_pagina(...)
  - `core/etapas.py:547` · `tem_pedaco_a_mao` · texto passado a r.get(...)
  - `core/fundo_tirado.py:157` · `campos_para_desfazer` · campos["campo"] = ...
  - `core/zonas_na_folha.py:697` · `_iguais` · texto passado a a.get(...)
  - `core/zonas_na_folha.py:697` · `_iguais` · texto passado a b.get(...)
  - `ui/automatico.py:2339` · `PainelDeOpcoes._opcoes_limpar` · texto passado a radio.setProperty(...)
  - `ui/barra_de_menu.py:318` · `BarraDeMenu` · item de tuple literal
  - `ui/desfazer_nesta_pagina.py:157` · `campos_para_desfazer` · campos["campo"] = ...
  - `ui/janela_principal.py:969` · `JanelaPrincipal._tirar_o_fundo_do_livro_inteiro` · chave de dicionario {"campo": ...}
  - `ui/tela_ampliada.py:59` · `(nivel do modulo)` · item de tuple literal
  - `ui/tela_conferir.py:284` · `(nivel do modulo)` · item de tuple literal
  - `ui/tela_conferir.py:292` · `(nivel do modulo)` · item de tuple literal
  - `ui/tela_conferir.py:7778` · `TelaConferir._escolher_filtro` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9142` · `TelaConferir._campos_do_aplicar_em` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10155` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/tela_opcoes.py:461` · `TelaOpcoes._montar_filtros` · texto passado a radio.setProperty(...)
  - `ui/tela_opcoes.py:896` · `TelaOpcoes.mostrar_opcoes` · texto passado a botao.property(...)
  - `ui/tela_opcoes.py:970` · `TelaOpcoes._filtro_escolhido` · texto passado a botao.property(...)

### `metade`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de TodasAsPaginas (ui/widgets/todas_as_paginas.py) · **8 gravacoes, 8 funcoes diferentes, 4 arquivos**

- `core/automatico.py:478` · `livro_leve` · ConfigPagina(metade=...) [classe certa: ConfigPagina]
- `core/automatico.py:655` · `medir` · ConfigPagina(metade=...) [classe certa: ConfigPagina]
- `core/dividir_a_mao.py:136` · `metades_da_pagina` · replace(x, metade=...) · em `copy.deepcopy(inteira)`
- `core/dividir_a_mao.py:163` · `pagina_inteira_das` · replace(x, metade=...) · em `copy.deepcopy(base)`
- `core/dividir_a_mao.py:247` · `campos_para_dividir` · x.metade = ... · em `pagina`
- `core/pipeline.py:266` · `_analisar_a_folha` · ConfigPagina(metade=...) [classe certa: ConfigPagina]
- `ui/widgets/todas_as_paginas.py:337` · `TodasAsPaginas.__init__` · x.metade = ... · em `self` (self de TodasAsPaginas)
- `ui/widgets/todas_as_paginas.py:590` · `TodasAsPaginas.mostrar` · x.metade = ... · em `self` (self de TodasAsPaginas)

Nome como texto (2; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/zonas_na_folha.py:167` · `geometria_do_desenho` · chave de dicionario {"campo": ...}
  - `core/zonas_na_folha.py:521` · `repartir_nas_metades` · texto passado a geometria.get(...)

### `revisada`

ConfigFolha e ConfigPagina (campo nas DUAS) · nome exclusivo? sim, so destas classes · **8 gravacoes, 8 funcoes diferentes, 2 arquivos**

- `core/dividir_a_mao.py:166` · `pagina_inteira_das` · x.revisada = ... · em `inteira`
- `core/pipeline.py:1093` · `_anotar_aviso_da_pagina` · x.revisada = ... · em `pagina`
- `core/pipeline.py:1569` · `_anotar_corte_encostou` · x.revisada = ... · em `folha`
- `core/pipeline.py:1667` · `_anotar_contas_discordam` · x.revisada = ... · em `pagina`
- `core/pipeline.py:2015` · `_anotar` · x.revisada = ... · em `pagina`
- `core/pipeline.py:2730` · `_anotar_conferir` · x.revisada = ... · em `pagina`
- `core/pipeline.py:4053` · `acertar_aviso_do_reforco` · x.revisada = ... · em `pagina`
- `core/pipeline.py:4141` · `_por_avisos_do_so_as_letras` · x.revisada = ... · em `pagina`

Nome como texto (23; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/dividir_a_mao.py:88` · `(nivel do modulo)` · dict(revisada=...)
  - `core/dividir_a_mao.py:235` · `campos_para_dividir` · chave de dicionario {"campo": ...}
  - `core/dividir_a_mao.py:285` · `campos_para_juntar` · chave de dicionario {"campo": ...}
  - `core/paginas_em_branco.py:71` · `(nivel do modulo)` · item de tuple literal
  - `ui/desfazer_nesta_pagina.py:170` · `campos_para_desfazer` · campos["campo"] = ...
  - `ui/desfazer_nesta_pagina.py:222` · `desfazer` · item de tuple literal
  - `ui/tela_conferir.py:6108` · `TelaConferir._mover_corte` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6549` · `TelaConferir._trocar_jeito_da_folha` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7013` · `TelaConferir._mover_recorte` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7021` · `TelaConferir._sem_recorte` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7041` · `TelaConferir._usar_corte_alargado` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7052` · `TelaConferir._alinhar_com_as_outras` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7143` · `TelaConferir._mudar_o_angulo` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7329` · `TelaConferir._acao_nas_escolhidas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7332` · `TelaConferir._acao_nas_escolhidas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7525` · `TelaConferir._dividir_as_medidas` · texto passado a campos.pop(...)
  - `ui/tela_conferir.py:7721` · `TelaConferir._trocar_conta_do_endireitar` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7778` · `TelaConferir._escolher_filtro` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:8226` · `TelaConferir._medidor_soltou` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:8380` · `TelaConferir.usar_da_tela_cheia` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9235` · `TelaConferir.apagar_pagina` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9318` · `TelaConferir._marcar_revisada` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9431` · `TelaConferir._deixar_em_branco` · campos["campo"] = ...

### `folha`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de ItemDaGrade (ui/widgets/todas_as_paginas.py), TarefaFolhaDoCaderno (ui/widgets/folhas_do_caderno.py) · **5 gravacoes, 5 funcoes diferentes, 4 arquivos**

- `core/automatico.py:478` · `livro_leve` · ConfigPagina(folha=...) [classe certa: ConfigPagina]
- `core/automatico.py:655` · `medir` · ConfigPagina(folha=...) [classe certa: ConfigPagina]
- `core/dividir_a_mao.py:201` · `trocar_as_paginas_da_folha` · x.folha = ... · em `pagina`
- `core/pipeline.py:265` · `_analisar_a_folha` · ConfigPagina(folha=...) [classe certa: ConfigPagina]
- `ui/widgets/folhas_do_caderno.py:302` · `TarefaFolhaDoCaderno.__init__` · desempacotada: x.folha = ... · em `self` (self de TarefaFolhaDoCaderno)

Nome como texto (25; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/paginas_em_outro_processo.py:601` · `_servir_folha_do_livreto` · item de tuple literal
  - `ui/barra_de_menu.py:240` · `BarraDeMenu._montar_pagina` · texto passado a nomes_dos_alcances(...)
  - `ui/dialogo_impressao.py:869` · `DialogoImpressao.resumo_antes` · texto passado a contar(...)
  - `ui/dialogo_impressao.py:875` · `DialogoImpressao.resumo_antes` · texto passado a contar(...)
  - `ui/dialogo_impressao.py:995` · `DialogoImpressao._mostrar_carregando` · texto passado a contar(...)
  - `ui/dialogo_impressao.py:1238` · `DialogoImpressao._pronto` · texto passado a contar(...)
  - `ui/dialogo_impressao.py:1412` · `ConfirmarImpressao.frase_do_que_sai` · texto passado a contar(...)
  - `ui/tela_ampliada.py:286` · `TelaAmpliada._atualizar_imagens` · item de tuple literal
  - `ui/tela_conferir.py:4554` · `TelaConferir._atualizar_previa` · item de tuple literal
  - `ui/tela_conferir.py:5292` · `TelaConferir._conferida_na_faixa` · texto passado a self._ok_dado(...)
  - `ui/tela_conferir.py:6119` · `TelaConferir._mover_corte` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:6151` · `TelaConferir._mover_a_linha_da_folha_inteira` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:6173` · `TelaConferir._corte_em_todas` · texto passado a self._espera_pelas_marcacoes(...)
  - `ui/tela_conferir.py:6181` · `TelaConferir._corte_em_todas` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:6240` · `TelaConferir._nao_dividir` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:6257` · `TelaConferir._juntar_todas` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:6479` · `TelaConferir._dividir_esta` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:6533` · `TelaConferir._trocar_jeito_da_folha` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:6546` · `TelaConferir._trocar_jeito_da_folha` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:6641` · `TelaConferir._girar_folhas` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:6684` · `TelaConferir._girar_as_divididas_pagina_por_pagina` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:7324` · `TelaConferir._acao_nas_escolhidas` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:7535` · `TelaConferir._dividir_as_medidas` · texto passado a self._registrar(...)
  - `ui/tela_final.py:254` · `TelaFinal.mostrar` · texto passado a _contar(...)
  - `ui/widgets/barra_girar.py:244` · `BarraGirar.__init__` · texto passado a nomes_dos_alcances(...)

### `posicao_corte`

ConfigFolha · nome exclusivo? NAO: tambem e atributo de MedidaDaFolha (core/automatico.py), Visualizador (ui/widgets/visualizador.py), _FolhaParaMedir (core/automatico.py) · **5 gravacoes, 5 funcoes diferentes, 3 arquivos**

- `core/automatico.py:476` · `livro_leve` · ConfigFolha(posicao_corte=...) [classe certa: ConfigFolha]
- `core/pipeline.py:243` · `_analisar_a_folha` · ConfigFolha(posicao_corte=...) [classe certa: ConfigFolha]
- `core/pipeline.py:507` · `trazer_divisao_da_analise` · x.posicao_corte = ... · em `f_salva`
- `ui/widgets/visualizador.py:273` · `Visualizador.__init__` · x.posicao_corte = ... · em `self` (self de Visualizador)
- `ui/widgets/visualizador.py:596` · `Visualizador.definir_corte` · x.posicao_corte = ... · em `self` (self de Visualizador)

Nome como texto (10; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:959` · `_dividir` · texto passado a g.na_folha(...)
  - `core/dividir_a_mao.py:257` · `campos_para_dividir` · campos["campo"] = ...
  - `ui/tela_conferir.py:6108` · `TelaConferir._mover_corte` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6152` · `TelaConferir._mover_a_linha_da_folha_inteira` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6174` · `TelaConferir._corte_em_todas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6182` · `TelaConferir._corte_em_todas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6530` · `TelaConferir._trocar_jeito_da_folha` · campos["campo"] = ...
  - `ui/tela_conferir.py:6548` · `TelaConferir._trocar_jeito_da_folha` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6923` · `TelaConferir` · item de set literal
  - `ui/tela_conferir.py:10170` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `apagada`

ConfigFolha e ConfigPagina (campo nas DUAS) · nome exclusivo? NAO: tambem e atributo de ItemDaGrade (ui/widgets/todas_as_paginas.py), Miniatura (ui/widgets/tira_miniaturas.py) · **5 gravacoes, 4 funcoes diferentes, 2 arquivos**

- `core/dividir_a_mao.py:164` · `pagina_inteira_das` · x.apagada = ... · em `inteira`
- `core/dividir_a_mao.py:240` · `campos_para_dividir` · x.apagada = ... · em `direita`
- `core/dividir_a_mao.py:249` · `campos_para_dividir` · x.apagada = ... · em `pagina`
- `ui/widgets/tira_miniaturas.py:149` · `Miniatura.__init__` · x.apagada = ... · em `self` (self de Miniatura)
- `ui/widgets/tira_miniaturas.py:970` · `TiraMiniaturas.marcar` · desempacotada: x.apagada = ... · em `mini`

Nome como texto (7; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:968` · `_dividir` · texto passado a g.na_pagina(...)
  - `core/automatico.py:1158` · `_desligar` · texto passado a g.na_pagina(...)
  - `core/paginas_em_branco.py:71` · `(nivel do modulo)` · item de tuple literal
  - `ui/tela_conferir.py:7332` · `TelaConferir._acao_nas_escolhidas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7335` · `TelaConferir._acao_nas_escolhidas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9235` · `TelaConferir.apagar_pagina` · chave de dicionario {"campo": ...}
  - `ui/widgets/todas_as_paginas.py:258` · `_Quadro._pintar` · texto passado a pintor.drawText(...)

### `selecao`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de EditorSelecao (ui/widgets/editor_selecao.py) · **4 gravacoes, 4 funcoes diferentes, 3 arquivos**

- `core/dividir_a_mao.py:147` · `metades_da_pagina` · x.selecao = ... · em `metade`
- `core/zonas_na_folha.py:581` · `acompanhar` · x.selecao = ... · em `pagina`
- `ui/widgets/editor_selecao.py:260` · `EditorSelecao.__init__` · x.selecao = ... · em `self` (self de EditorSelecao)
- `ui/widgets/editor_selecao.py:348` · `EditorSelecao.definir_selecao` · x.selecao = ... · em `self` (self de EditorSelecao)

Nome como texto (12; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/dividir_a_mao.py:87` · `(nivel do modulo)` · dict(selecao=...)
  - `core/paginas_em_branco.py:71` · `(nivel do modulo)` · item de tuple literal
  - `core/zonas_na_folha.py:662` · `para_o_disco` · texto passado a dados_da_pagina.get(...)
  - `core/zonas_na_folha.py:684` · `do_disco` · texto passado a dados_da_pagina.get(...)
  - `core/zonas_na_folha.py:685` · `do_disco` · dados_da_pagina["campo"] = ...
  - `core/zonas_na_folha.py:724` · `tem_zonas_no_formato_antigo` · texto passado a p.get(...)
  - `ui/desfazer_nesta_pagina.py:159` · `campos_para_desfazer` · campos["campo"] = ...
  - `ui/tela_conferir.py:3052` · `TelaConferir` · item de tuple literal
  - `ui/tela_conferir.py:3326` · `TelaConferir._marcacao_em_todas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:3343` · `TelaConferir._marcacao_nas_proximas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:4791` · `TelaConferir._ajustar_pedaco_a_figura` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10165` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `gravura_feita_com`

ConfigPagina · nome exclusivo? sim, so destas classes · **4 gravacoes, 4 funcoes diferentes, 2 arquivos**

- `core/pipeline.py:2404` · `trocar_opcoes_da_gravura` · x.gravura_feita_com = ... · em `pagina`
- `core/pipeline.py:2542` · `garantir_selecao` · x.gravura_feita_com = ... · em `pagina`
- `ui/tela_conferir.py:3190` · `TelaConferir._detectar_de_novo` · x.gravura_feita_com = ... · em `pagina`
- `ui/tela_conferir.py:3226` · `TelaConferir._preparar_para_trocar_forma` · x.gravura_feita_com = ... · em `pagina`

Nome como texto (2; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/dividir_a_mao.py:89` · `(nivel do modulo)` · dict(gravura_feita_com=...)
  - `core/paginas_em_branco.py:73` · `(nivel do modulo)` · item de tuple literal

### `geometria_das_zonas`

ConfigPagina · nome exclusivo? sim, so destas classes · **4 gravacoes, 3 funcoes diferentes, 2 arquivos**

- `core/dividir_a_mao.py:148` · `metades_da_pagina` · x.geometria_das_zonas = ... · em `metade`
- `core/zonas_na_folha.py:576` · `acompanhar` · x.geometria_das_zonas = ... · em `pagina`
- `core/zonas_na_folha.py:582` · `acompanhar` · x.geometria_das_zonas = ... · em `pagina`
- `core/zonas_na_folha.py:646` · `anotar_se_ainda_antiga` · x.geometria_das_zonas = ... · em `pagina`

Nome como texto (7; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/dividir_a_mao.py:87` · `(nivel do modulo)` · dict(geometria_das_zonas=...)
  - `core/paginas_em_branco.py:72` · `(nivel do modulo)` · item de tuple literal
  - `core/zonas_na_folha.py:661` · `para_o_disco` · texto passado a dados_da_pagina.get(...)
  - `core/zonas_na_folha.py:674` · `do_disco` · texto passado a dados_da_pagina.get(...)
  - `core/zonas_na_folha.py:676` · `do_disco` · dados_da_pagina["campo"] = ...
  - `ui/desfazer_nesta_pagina.py:161` · `campos_para_desfazer` · campos["campo"] = ...
  - `ui/tela_conferir.py:3052` · `TelaConferir` · item de tuple literal

### `dividir`

ConfigFolha · nome exclusivo? NAO: tambem e atributo de MedidaDaFolha (core/automatico.py), _FolhaParaMedir (core/automatico.py) · **3 gravacoes, 3 funcoes diferentes, 2 arquivos**

- `core/automatico.py:476` · `livro_leve` · ConfigFolha(dividir=...) [classe certa: ConfigFolha]
- `core/automatico.py:971` · `_dividir` · x.dividir = ... · em `folha`
- `core/pipeline.py:242` · `_analisar_a_folha` · ConfigFolha(dividir=...) [classe certa: ConfigFolha]

Nome como texto (11; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:965` · `_dividir` · texto passado a g.na_folha(...)
  - `core/automatico.py:988` · `_dividir` · texto passado a g.na_folha(...)
  - `core/automatico.py:1153` · `_desligar` · texto passado a g.na_folha(...)
  - `core/dividir_a_mao.py:235` · `campos_para_dividir` · chave de dicionario {"campo": ...}
  - `core/dividir_a_mao.py:285` · `campos_para_juntar` · chave de dicionario {"campo": ...}
  - `core/dividir_a_mao.py:325` · `campos_para_juntar_todas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:1985` · `TelaConferir._montar_aba_corte` · texto passado a self._parte_do_livro(...)
  - `ui/tela_conferir.py:6923` · `TelaConferir` · item de set literal
  - `ui/tela_conferir.py:10170` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/todas_as_paginas.py:442` · `TodasAsPaginas._montar_faixa_da_escolha` · item de tuple literal
  - `ui/widgets/todas_as_paginas.py:442` · `TodasAsPaginas._montar_faixa_da_escolha` · item de tuple literal

### `e_paisagem`

ConfigFolha · nome exclusivo? NAO: tambem e atributo de Lombada (core/dividir.py), MedidaDaFolha (core/automatico.py) · **3 gravacoes, 3 funcoes diferentes, 2 arquivos**

- `core/automatico.py:477` · `livro_leve` · ConfigFolha(e_paisagem=...) [classe certa: ConfigFolha]
- `core/pipeline.py:247` · `_analisar_a_folha` · ConfigFolha(e_paisagem=...) [classe certa: ConfigFolha]
- `core/pipeline.py:509` · `trazer_divisao_da_analise` · x.e_paisagem = ... · em `f_salva`

Nome como texto (2; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:961` · `_dividir` · texto passado a g.na_folha(...)
  - `core/dividir_a_mao.py:259` · `campos_para_dividir` · campos["campo"] = ...

### `em_branco`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de Medidas (teste_livros.py) · **3 gravacoes, 3 funcoes diferentes, 2 arquivos**

- `core/dividir_a_mao.py:165` · `pagina_inteira_das` · x.em_branco = ... · em `inteira`
- `core/dividir_a_mao.py:250` · `campos_para_dividir` · x.em_branco = ... · em `pagina`
- `core/paginas_em_branco.py:86` · `pagina_em_branco_como` · x.em_branco = ... · em `nova`

Nome como texto (8; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/analise.py:272` · `(nivel do modulo)` · texto passado a Alerta(...)
  - `core/analise.py:365` · `(nivel do modulo)` · texto passado a Alerta(...)
  - `core/automatico.py:682` · `(nivel do modulo)` · item de tuple literal
  - `ui/tela_conferir.py:7329` · `TelaConferir._acao_nas_escolhidas` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:7329` · `TelaConferir._acao_nas_escolhidas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7335` · `TelaConferir._acao_nas_escolhidas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9429` · `TelaConferir._deixar_em_branco` · chave de dicionario {"campo": ...}
  - `ui/widgets/todas_as_paginas.py:444` · `TodasAsPaginas._montar_faixa_da_escolha` · item de tuple literal

### `forca_preto`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de _TarefaCartoes (ui/tarefas.py) · **3 gravacoes, 3 funcoes diferentes, 2 arquivos**

- `core/pipeline.py:3945` · `_filtrar_no_misto` · x.forca_preto = ... · em `pagina`
- `core/pipeline.py:4026` · `_reforcar_se_o_texto_falhou` · x.forca_preto = ... · em `pagina`
- `ui/tarefas.py:820` · `_TarefaCartoes.__init__` · x.forca_preto = ... · em `self` (self de _TarefaCartoes)

Nome como texto (6; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:150` · `(nivel do modulo)` · item de tuple literal
  - `core/perfis.py:61` · `(nivel do modulo)` · item de tuple literal
  - `ui/tela_conferir.py:9142` · `TelaConferir._campos_do_aplicar_em` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9417` · `TelaConferir._escolher_forca` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9449` · `TelaConferir._desfazer_o_reforco` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10155` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `mexida_a_mao`

ConfigFolha e ConfigPagina (campo nas DUAS) · nome exclusivo? sim, so destas classes · **3 gravacoes, 3 funcoes diferentes, 2 arquivos**

- `core/dividir_a_mao.py:151` · `metades_da_pagina` · x.mexida_a_mao = ... · em `metade`
- `core/etapas.py:125` · `marcar_mexida_a_mao` · x.mexida_a_mao = ... · em `item`
- `core/etapas.py:136` · `desmarcar_mexida_a_mao` · x.mexida_a_mao = ... · em `item`

Nome como texto (10; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:963` · `_dividir` · texto passado a g.na_folha(...)
  - `core/automatico.py:1049` · `_ligar_na_pagina` · texto passado a g.na_pagina(...)
  - `core/dividir_a_mao.py:107` · `_limpos` · limpos["campo"] = ...
  - `core/paginas_em_branco.py:71` · `(nivel do modulo)` · item de tuple literal
  - `ui/desfazer_nesta_pagina.py:169` · `campos_para_desfazer` · campos["campo"] = ...
  - `ui/desfazer_nesta_pagina.py:206` · `desfazer` · campos["campo"] = ...
  - `ui/desfazer_nesta_pagina.py:222` · `desfazer` · item de tuple literal
  - `ui/tela_conferir.py:3052` · `TelaConferir` · item de tuple literal
  - `ui/tela_conferir.py:6081` · `TelaConferir._com_a_marca_mexida_a_mao` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10055` · `(nivel do modulo)` · item de set literal

### `forca_antes_do_reforco`

ConfigPagina · nome exclusivo? sim, so destas classes · **3 gravacoes, 3 funcoes diferentes, 1 arquivos**

- `core/pipeline.py:3946` · `_filtrar_no_misto` · x.forca_antes_do_reforco = ... · em `pagina`
- `core/pipeline.py:4025` · `_reforcar_se_o_texto_falhou` · x.forca_antes_do_reforco = ... · em `pagina`
- `core/pipeline.py:4045` · `acertar_aviso_do_reforco` · x.forca_antes_do_reforco = ... · em `pagina`

Nome como texto (2; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/paginas_em_branco.py:73` · `(nivel do modulo)` · item de tuple literal
  - `ui/tela_conferir.py:9450` · `TelaConferir._desfazer_o_reforco` · chave de dicionario {"campo": ...}

### `gravura_forma`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de Projeto (modelos.py) · **5 gravacoes, 2 funcoes diferentes, 2 arquivos**

- `ui/tela_conferir.py:3222` · `TelaConferir._preparar_para_trocar_forma` · x.gravura_forma = ... · em `pagina`
- `ui/tela_conferir.py:3224` · `TelaConferir._preparar_para_trocar_forma` · x.gravura_forma = ... · em `pagina`
- `ui/tela_opcoes.py:1016` · `TelaOpcoes._mudou` · x.gravura_forma = ... · em `self.projeto`
- `ui/tela_opcoes.py:1018` · `TelaOpcoes._mudou` · x.gravura_forma = ... · em `self.projeto`
- `ui/tela_opcoes.py:1020` · `TelaOpcoes._mudou` · x.gravura_forma = ... · em `self.projeto`

Nome como texto (11; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:238` · `(nivel do modulo)` · item de tuple literal
  - `core/automatico.py:1139` · `_desligar` · texto passado a g.no_livro(...)
  - `core/perfis.py:47` · `(nivel do modulo)` · item de tuple literal
  - `core/perfis.py:198` · `etapas_da_receita` · texto passado a dados.get(...)
  - `core/pipeline.py:2364` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:183` · `texto_das_opcoes` · texto passado a o.get(...)
  - `ui/automatico.py:2497` · `PainelDeOpcoes._opcoes_gravuras` · self.controles["campo"] = ...
  - `ui/automatico.py:2617` · `PainelDeOpcoes._forma_mudou` · texto passado a self._mudou(...)
  - `ui/automatico.py:2681` · `PainelDeOpcoes._mostrar_opcoes` · texto passado a o.get(...)
  - `ui/tela_conferir.py:3246` · `TelaConferir._mudar_forma_da_pagina` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:3273` · `TelaConferir._forma_nas` · chave de dicionario {"campo": ...}

### `dividir_como`

ConfigFolha · nome exclusivo? NAO: tambem e atributo de Fotografia (core/automatico.py), Projeto (modelos.py) · **2 gravacoes, 2 funcoes diferentes, 2 arquivos**

- `core/pipeline.py:500` · `trazer_divisao_da_analise` · x.dividir_como = ... · em `salvo`
- `ui/tela_opcoes.py:981` · `TelaOpcoes._mudou` · x.dividir_como = ... · em `self.projeto`

Nome como texto (13; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:231` · `(nivel do modulo)` · item de tuple literal
  - `core/automatico.py:565` · `fotografar` · texto passado a opcoes.get(...)
  - `core/automatico.py:962` · `_dividir` · texto passado a g.na_folha(...)
  - `core/automatico.py:1699` · `paginas_do_pdf_depois` · texto passado a (pedido.opcoes or {}).get(...)
  - `core/perfis.py:44` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:155` · `texto_das_opcoes` · texto passado a o.get(...)
  - `ui/automatico.py:1744` · `PaginaAntesEDepois._passos` · texto passado a (pedido.opcoes or {}).get(...)
  - `ui/automatico.py:2281` · `PainelDeOpcoes._opcoes_dividir` · texto passado a self._combo(...)
  - `ui/automatico.py:2643` · `PainelDeOpcoes._mostrar_opcoes` · item de tuple literal
  - `ui/tela_conferir.py:6524` · `TelaConferir._trocar_jeito_da_folha` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6547` · `TelaConferir._trocar_jeito_da_folha` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10171` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/folhas_do_caderno.py:463` · `FolhasDoCaderno._depois` · texto passado a (pedido.opcoes or {}).get(...)

### `endireitar_como`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de Projeto (modelos.py), _FolhaParaMedir (core/automatico.py) · **2 gravacoes, 2 funcoes diferentes, 2 arquivos**

- `core/automatico.py:656` · `medir` · ConfigPagina(endireitar_como=...) [classe certa: ConfigPagina]
- `ui/tela_opcoes.py:989` · `TelaOpcoes._mudou` · x.endireitar_como = ... · em `self.projeto`

Nome como texto (7; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:232` · `(nivel do modulo)` · item de tuple literal
  - `core/perfis.py:45` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:157` · `texto_das_opcoes` · texto passado a o.get(...)
  - `ui/automatico.py:2297` · `PainelDeOpcoes._opcoes_endireitar` · texto passado a self._combo(...)
  - `ui/automatico.py:2643` · `PainelDeOpcoes._mostrar_opcoes` · item de tuple literal
  - `ui/tela_conferir.py:6925` · `TelaConferir` · item de set literal
  - `ui/tela_conferir.py:7720` · `TelaConferir._trocar_conta_do_endireitar` · chave de dicionario {"campo": ...}

### `fundo_tirado`

ConfigPagina · nome exclusivo? sim, so destas classes · **2 gravacoes, 2 funcoes diferentes, 2 arquivos**

- `core/fundo_tirado.py:197` · `migrar_projeto_antigo` · x.fundo_tirado = ... · em `pagina`
- `core/pipeline.py:4479` · `renderizar_com_filtro` · replace(x, fundo_tirado=...) · em `pagina`

Nome como texto (1; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `ui/widgets/filtros_tela_cheia.py:130` · `pagina_com_as_opcoes` · campos["campo"] = ...

### `tem_cor`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de Medidas (teste_livros.py), Pagina (teste_bateria.py) · **2 gravacoes, 2 funcoes diferentes, 2 arquivos**

- `core/automatico.py:1876` · `avisos_do_livro` · x.tem_cor = ... · em `pagina`
- `core/pipeline.py:271` · `_analisar_a_folha` · x.tem_cor = ... · em `pagina`

Nome como texto (2; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:1210` · `_avisos_medidos` · texto passado a g.na_pagina(...)
  - `core/paginas_em_branco.py:73` · `(nivel do modulo)` · item de tuple literal

### `confianca_corte`

ConfigFolha · nome exclusivo? NAO: tambem e atributo de MedidaDaFolha (core/automatico.py), Medidas (teste_livros.py), Pagina (teste_bateria.py) · **2 gravacoes, 2 funcoes diferentes, 1 arquivos**

- `core/pipeline.py:244` · `_analisar_a_folha` · ConfigFolha(confianca_corte=...) [classe certa: ConfigFolha]
- `core/pipeline.py:508` · `trazer_divisao_da_analise` · x.confianca_corte = ... · em `f_salva`

Nome como texto (4; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:960` · `_dividir` · texto passado a g.na_folha(...)
  - `core/dividir_a_mao.py:258` · `campos_para_dividir` · campos["campo"] = ...
  - `ui/tela_conferir.py:6531` · `TelaConferir._trocar_jeito_da_folha` · campos["campo"] = ...
  - `ui/tela_conferir.py:6549` · `TelaConferir._trocar_jeito_da_folha` · chave de dicionario {"campo": ...}

### `faixa_na_beirada`

ConfigPagina · nome exclusivo? sim, so destas classes · **2 gravacoes, 2 funcoes diferentes, 1 arquivos**

- `core/pipeline.py:4109` · `_acertar_avisos_do_misto` · x.faixa_na_beirada = ... · em `pagina`
- `core/pipeline.py:4149` · `_tirar_avisos_do_so_as_letras` · x.faixa_na_beirada = ... · em `pagina`

Nome como texto (1; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/paginas_em_branco.py:72` · `(nivel do modulo)` · item de tuple literal

### `recorte`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de Visualizador (ui/widgets/visualizador.py) · **2 gravacoes, 2 funcoes diferentes, 1 arquivos**

- `ui/widgets/visualizador.py:284` · `Visualizador.__init__` · x.recorte = ... · em `self` (self de Visualizador)
- `ui/widgets/visualizador.py:609` · `Visualizador.definir_recorte` · x.recorte = ... · em `self` (self de Visualizador)

Nome como texto (21; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:1053` · `_ligar_na_pagina` · texto passado a g.na_pagina(...)
  - `core/dividir_a_mao.py:87` · `(nivel do modulo)` · dict(recorte=...)
  - `core/girar.py:295` · `campos_da_pagina_que_giram_junto` · campos["campo"] = ...
  - `core/zonas_na_folha.py:168` · `geometria_do_desenho` · chave de dicionario {"campo": ...}
  - `core/zonas_na_folha.py:201` · `geometria_valida` · texto passado a g.get(...)
  - `core/zonas_na_folha.py:239` · `mesma_geometria` · texto passado a a.get(...)
  - `core/zonas_na_folha.py:239` · `mesma_geometria` · texto passado a b.get(...)
  - `core/zonas_na_folha.py:278` · `_tamanhos` · texto passado a g.get(...)
  - `core/zonas_na_folha.py:289` · `_antes_do_corte` · texto passado a g.get(...)
  - `core/zonas_na_folha.py:369` · `_matriz_folha_para_pagina` · texto passado a g.get(...)
  - `ui/desfazer_nesta_pagina.py:152` · `campos_para_desfazer` · campos["campo"] = ...
  - `ui/tela_conferir.py:6924` · `TelaConferir` · item de set literal
  - `ui/tela_conferir.py:7013` · `TelaConferir._mover_recorte` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7021` · `TelaConferir._sem_recorte` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7041` · `TelaConferir._usar_corte_alargado` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7059` · `TelaConferir._recorte_automatico` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7073` · `TelaConferir._recorte_em_todas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7083` · `TelaConferir._recorte_em_todas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7220` · `TelaConferir._com_o_retangulo_do_corte` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10153` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10176` · `(nivel do modulo)` · item de tuple literal

### `reforco_desfeito`

ConfigPagina · nome exclusivo? sim, so destas classes · **2 gravacoes, 2 funcoes diferentes, 1 arquivos**

- `core/pipeline.py:3947` · `_filtrar_no_misto` · x.reforco_desfeito = ... · em `pagina`
- `core/pipeline.py:4046` · `acertar_aviso_do_reforco` · x.reforco_desfeito = ... · em `pagina`

Nome como texto (2; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/paginas_em_branco.py:73` · `(nivel do modulo)` · item de tuple literal
  - `ui/tela_conferir.py:9450` · `TelaConferir._desfazer_o_reforco` · chave de dicionario {"campo": ...}

### `sobra`

ConfigFolha · nome exclusivo? NAO: tambem e atributo de MedidaDaFolha (core/automatico.py) · **2 gravacoes, 2 funcoes diferentes, 1 arquivos**

- `core/pipeline.py:248` · `_analisar_a_folha` · ConfigFolha(sobra=...) [classe certa: ConfigFolha]
- `core/pipeline.py:497` · `trazer_divisao_da_analise` · x.sobra = ... · em `f_salva`

Nome como texto (7; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:990` · `_dividir` · texto passado a g.na_folha(...)
  - `core/zonas_na_folha.py:172` · `geometria_do_desenho` · desenho["campo"] = ...
  - `core/zonas_na_folha.py:205` · `geometria_valida` · texto passado a g.get(...)
  - `core/zonas_na_folha.py:244` · `mesma_geometria` · texto passado a a.get(...)
  - `core/zonas_na_folha.py:244` · `mesma_geometria` · texto passado a b.get(...)
  - `core/zonas_na_folha.py:273` · `_tamanhos` · texto passado a g.get(...)
  - `core/zonas_na_folha.py:355` · `_matriz_folha_para_pagina` · texto passado a g.get(...)

### `alertas_aceitos`

ConfigFolha e ConfigPagina (campo nas DUAS) · nome exclusivo? sim, so destas classes · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `core/pipeline.py:4065` · `_esquecer_aceitos` · x.alertas_aceitos = ... · em `pagina`

Nome como texto (7; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/avisos.py:248` · `campos_para_aceitar` · chave de dicionario {"campo": ...}
  - `core/dividir_a_mao.py:88` · `(nivel do modulo)` · dict(alertas_aceitos=...)
  - `core/paginas_em_branco.py:71` · `(nivel do modulo)` · item de tuple literal
  - `ui/desfazer_nesta_pagina.py:222` · `desfazer` · item de tuple literal
  - `ui/tela_conferir.py:6035` · `TelaConferir._com_os_avisos_de_agora` · item de tuple literal
  - `ui/tela_conferir.py:9497` · `TelaConferir._aceitar_avisos` · texto passado a campo_de_pagina(...)
  - `ui/tela_conferir.py:10058` · `(nivel do modulo)` · item de set literal

### `angulo_detectado`

ConfigFolha · nome exclusivo? NAO: tambem e atributo de MedidaDaFolha (core/automatico.py) · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `core/pipeline.py:245` · `_analisar_a_folha` · ConfigFolha(angulo_detectado=...) [classe certa: ConfigFolha]

Nome como texto (1; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:1196` · `_avisos_medidos` · texto passado a g.na_folha(...)

### `angulo_manual`

ConfigPagina · nome exclusivo? sim, so destas classes · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `ui/tela_conferir.py:7683` · `TelaConferir._atualizar_conta_do_endireitar` · replace(x, angulo_manual=...) · em `pagina`

Nome como texto (9; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:1051` · `_ligar_na_pagina` · texto passado a g.na_pagina(...)
  - `core/dividir_a_mao.py:87` · `(nivel do modulo)` · dict(angulo_manual=...)
  - `ui/desfazer_nesta_pagina.py:150` · `campos_para_desfazer` · campos["campo"] = ...
  - `ui/tela_conferir.py:6924` · `TelaConferir` · item de set literal
  - `ui/tela_conferir.py:7586` · `TelaConferir._gravar_angulo` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7649` · `TelaConferir._angulo_zero` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7752` · `TelaConferir._angulo_automatico` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10154` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10176` · `(nivel do modulo)` · item de tuple literal

### `automatico`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de ColunaDePaineis (ui/widgets/paineis.py) · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `ui/widgets/paineis.py:2654` · `ColunaDePaineis.__init__` · x.automatico = ... · em `self` (self de ColunaDePaineis)

Nome como texto (15; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:755` · `_Gravador.acao` · texto passado a Acao.nova(...)
  - `core/automatico.py:770` · `_Gravador.acao` · texto passado a Acao.nova(...)
  - `core/automatico.py:1047` · `_ligar_na_pagina` · texto passado a g.na_pagina(...)
  - `core/automatico.py:1168` · `_desligar` · texto passado a g.na_pagina(...)
  - `core/automatico.py:1170` · `_desligar` · texto passado a g.na_pagina(...)
  - `core/margens_scantailor.py:93` · `(nivel do modulo)` · item de tuple literal
  - `core/paginas_em_branco.py:72` · `(nivel do modulo)` · item de tuple literal
  - `ui/barra_de_menu.py:138` · `BarraDeMenu._montar_arquivo` · texto passado a self._acao(...)
  - `ui/barra_de_menu.py:320` · `BarraDeMenu` · item de tuple literal
  - `ui/barra_de_menu.py:371` · `BarraDeMenu.mostrar_tela_inicial` · item de tuple literal
  - `ui/barra_de_menu.py:378` · `BarraDeMenu.mostrar_tela_de_trabalho` · item de tuple literal
  - `ui/janela_principal.py:265` · `JanelaPrincipal._montar_menu` · texto passado a self.menu.ligar(...)
  - `ui/janela_principal.py:1258` · `JanelaPrincipal._escolhidas_chegaram` · texto passado a self.tela_conferir.paineis.mostrar_pa...(...)
  - `ui/tarefas.py:216` · `TarefaAutomatico.run` · texto passado a registrar_erro(...)
  - `ui/widgets/todas_as_paginas.py:450` · `TodasAsPaginas._montar_faixa_da_escolha` · item de tuple literal

### `confianca_angulo`

ConfigFolha · nome exclusivo? NAO: tambem e atributo de MedidaDaFolha (core/automatico.py), Medidas (teste_livros.py), Pagina (teste_bateria.py) · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `core/pipeline.py:246` · `_analisar_a_folha` · ConfigFolha(confianca_angulo=...) [classe certa: ConfigFolha]

Nome como texto (1; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:1197` · `_avisos_medidos` · texto passado a g.na_folha(...)

### `gravura_achada_a_mao`

ConfigPagina · nome exclusivo? sim, so destas classes · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `core/pipeline.py:2552` · `garantir_selecao` · x.gravura_achada_a_mao = ... · em `pagina`

Nome como texto (3; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:1060` · `_ligar_na_pagina` · texto passado a g.na_pagina(...)
  - `core/dividir_a_mao.py:93` · `(nivel do modulo)` · dict(gravura_achada_a_mao=...)
  - `core/paginas_em_branco.py:75` · `(nivel do modulo)` · item de tuple literal

### `inserida`

ConfigPagina · nome exclusivo? sim, so destas classes · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `core/paginas_em_branco.py:87` · `pagina_em_branco_como` · x.inserida = ... · em `nova`

Nome como texto (2; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/paginas_em_branco.py:117` · `por_as_inseridas` · texto passado a dados.get(...)
  - `core/paginas_em_branco.py:157` · `onde_entrou.<lambda>` · texto passado a item['pagina'].get(...)

### `limpar_pontinhos`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de Projeto (modelos.py) · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `ui/tela_opcoes.py:1050` · `TelaOpcoes._mudou` · x.limpar_pontinhos = ... · em `self.projeto`

Nome como texto (10; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:237` · `(nivel do modulo)` · item de tuple literal
  - `core/perfis.py:50` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:175` · `texto_das_opcoes` · texto passado a o.get(...)
  - `ui/automatico.py:2365` · `PainelDeOpcoes._opcoes_limpar` · texto passado a self._combo(...)
  - `ui/automatico.py:2644` · `PainelDeOpcoes._mostrar_opcoes` · item de tuple literal
  - `ui/tela_conferir.py:7951` · `TelaConferir._mudar_pontinhos` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9147` · `TelaConferir._campos_do_aplicar_em` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10157` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/filtros_tela_cheia.py:595` · `FiltrosEmTelaCheia._montar_as_opcoes.<lambda>` · texto passado a self._guardar_opcao(...)
  - `ui/widgets/filtros_tela_cheia.py:636` · `FiltrosEmTelaCheia._valores_da_pagina` · chave de dicionario {"campo": ...}

### `marcacao_provisoria`

ConfigPagina · nome exclusivo? sim, so destas classes · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `core/dividir_a_mao.py:149` · `metades_da_pagina` · x.marcacao_provisoria = ... · em `metade`

Nome como texto (4; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/dividir_a_mao.py:90` · `(nivel do modulo)` · dict(marcacao_provisoria=...)
  - `core/paginas_em_branco.py:72` · `(nivel do modulo)` · item de tuple literal
  - `ui/desfazer_nesta_pagina.py:160` · `campos_para_desfazer` · campos["campo"] = ...
  - `ui/tela_conferir.py:3052` · `TelaConferir` · item de tuple literal

### `metades_guardadas`

ConfigFolha · nome exclusivo? sim, so destas classes · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `core/automatico.py:975` · `_dividir` · x.metades_guardadas = ... · em `folha`

Nome como texto (4; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/dividir_a_mao.py:260` · `campos_para_dividir` · campos["campo"] = ...
  - `core/dividir_a_mao.py:288` · `campos_para_juntar` · campos["campo"] = ...
  - `core/dividir_a_mao.py:325` · `campos_para_juntar_todas` · chave de dicionario {"campo": ...}
  - `core/dividir_a_mao.py:370` · `_e_do_juntar_todas` · texto passado a (getattr(acao, 'depois', None) or {})...(...)

### `misto_fora_do_texto`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de Projeto (modelos.py) · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `ui/tela_opcoes.py:1031` · `TelaOpcoes._mudou` · x.misto_fora_do_texto = ... · em `self.projeto`

Nome como texto (11; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:236` · `(nivel do modulo)` · item de tuple literal
  - `core/misto.py:218` · `(nivel do modulo)` · item de tuple literal
  - `core/misto.py:252` · `escolhas_da_pagina` · texto passado a _da_pagina_ou_do_livro(...)
  - `core/perfis.py:49` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:2351` · `PainelDeOpcoes._opcoes_limpar.<lambda>` · texto passado a self._mudou(...)
  - `ui/automatico.py:2663` · `PainelDeOpcoes._mostrar_opcoes` · texto passado a o.get(...)
  - `ui/tela_conferir.py:7987` · `TelaConferir._mudar_misto` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:8014` · `TelaConferir._mudar_fora_do_texto` · texto passado a self._mudar_misto(...)
  - `ui/tela_conferir.py:10158` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/filtros_tela_cheia.py:580` · `FiltrosEmTelaCheia._montar_as_opcoes.<lambda>` · texto passado a self._guardar_opcao(...)
  - `ui/widgets/filtros_tela_cheia.py:633` · `FiltrosEmTelaCheia._valores_da_pagina` · chave de dicionario {"campo": ...}

### `misto_letras_na_moldura`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de Projeto (modelos.py) · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `ui/tela_opcoes.py:1034` · `TelaOpcoes._mudou` · x.misto_letras_na_moldura = ... · em `self.projeto`

Nome como texto (11; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:236` · `(nivel do modulo)` · item de tuple literal
  - `core/misto.py:219` · `(nivel do modulo)` · item de tuple literal
  - `core/misto.py:254` · `escolhas_da_pagina` · texto passado a _da_pagina_ou_do_livro(...)
  - `core/perfis.py:50` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:2353` · `PainelDeOpcoes._opcoes_limpar.<lambda>` · texto passado a self._mudou(...)
  - `ui/automatico.py:2665` · `PainelDeOpcoes._mostrar_opcoes` · texto passado a o.get(...)
  - `ui/tela_conferir.py:7989` · `TelaConferir._mudar_misto` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:8026` · `TelaConferir._mudar_letras_na_moldura` · texto passado a self._mudar_misto(...)
  - `ui/tela_conferir.py:10159` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/filtros_tela_cheia.py:583` · `FiltrosEmTelaCheia._montar_as_opcoes.<lambda>` · texto passado a self._guardar_opcao(...)
  - `ui/widgets/filtros_tela_cheia.py:635` · `FiltrosEmTelaCheia._valores_da_pagina` · chave de dicionario {"campo": ...}

### `misto_papel_da_gravura`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de Projeto (modelos.py) · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `ui/tela_opcoes.py:1032` · `TelaOpcoes._mudou` · x.misto_papel_da_gravura = ... · em `self.projeto`

Nome como texto (11; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:236` · `(nivel do modulo)` · item de tuple literal
  - `core/misto.py:219` · `(nivel do modulo)` · item de tuple literal
  - `core/misto.py:253` · `escolhas_da_pagina` · texto passado a _da_pagina_ou_do_livro(...)
  - `core/perfis.py:49` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:2352` · `PainelDeOpcoes._opcoes_limpar.<lambda>` · texto passado a self._mudou(...)
  - `ui/automatico.py:2664` · `PainelDeOpcoes._mostrar_opcoes` · texto passado a o.get(...)
  - `ui/tela_conferir.py:7988` · `TelaConferir._mudar_misto` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:8019` · `TelaConferir._mudar_papel_da_gravura` · texto passado a self._mudar_misto(...)
  - `ui/tela_conferir.py:10159` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/filtros_tela_cheia.py:581` · `FiltrosEmTelaCheia._montar_as_opcoes.<lambda>` · texto passado a self._guardar_opcao(...)
  - `ui/widgets/filtros_tela_cheia.py:634` · `FiltrosEmTelaCheia._valores_da_pagina` · chave de dicionario {"campo": ...}

### `misto_so_as_letras`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de Projeto (modelos.py) · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `ui/tela_opcoes.py:1030` · `TelaOpcoes._mudou` · x.misto_so_as_letras = ... · em `self.projeto`

Nome como texto (15; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:235` · `(nivel do modulo)` · item de tuple literal
  - `core/misto.py:218` · `(nivel do modulo)` · item de tuple literal
  - `core/misto.py:251` · `escolhas_da_pagina` · texto passado a _da_pagina_ou_do_livro(...)
  - `core/perfis.py:49` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:173` · `texto_das_opcoes` · texto passado a o.get(...)
  - `ui/automatico.py:178` · `texto_das_opcoes` · texto passado a o.get(...)
  - `ui/automatico.py:459` · `EstadoDoAutomatico.frase` · texto passado a self.opcoes.get(...)
  - `ui/automatico.py:2350` · `PainelDeOpcoes._opcoes_limpar.<lambda>` · texto passado a self._mudou(...)
  - `ui/automatico.py:2662` · `PainelDeOpcoes._mostrar_opcoes` · texto passado a o.get(...)
  - `ui/automatico.py:2667` · `PainelDeOpcoes._mostrar_opcoes` · texto passado a o.get(...)
  - `ui/tela_conferir.py:7986` · `TelaConferir._mudar_misto` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:8008` · `TelaConferir._mudar_so_as_letras` · texto passado a self._mudar_misto(...)
  - `ui/tela_conferir.py:10158` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/filtros_tela_cheia.py:578` · `FiltrosEmTelaCheia._montar_as_opcoes.<lambda>` · texto passado a self._guardar_opcao(...)
  - `ui/widgets/filtros_tela_cheia.py:633` · `FiltrosEmTelaCheia._valores_da_pagina` · chave de dicionario {"campo": ...}

### `rotacao`

ConfigFolha · nome exclusivo? NAO: tambem e atributo de CamadasDaPagina (core/camadas.py), _FolhaParaMedir (core/automatico.py), _TarefaPrevia (ui/tarefas.py) · **1 gravacoes, 1 funcoes diferentes, 1 arquivos**

- `ui/tarefas.py:929` · `_TarefaPrevia.__init__` · x.rotacao = ... · em `self` (self de _TarefaPrevia)

Nome como texto (9; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/girar.py:207` · `campos_do_giro` · chave de dicionario {"campo": ...}
  - `core/zonas_na_folha.py:165` · `geometria_do_desenho` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6679` · `TelaConferir._girar_as_divididas_pagina_por_pagina` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6706` · `TelaConferir._com_as_paginas_que_giram_junto` · texto passado a campos.get(...)
  - `ui/tela_conferir.py:6876` · `TelaConferir._com_as_folhas_inteiras_tambem` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6923` · `TelaConferir` · item de set literal
  - `ui/tela_conferir.py:7325` · `TelaConferir._acao_nas_escolhidas` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:7383` · `TelaConferir._girar_as_escolhidas_que_sao_metade` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10172` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `algoritmo_preto_branco`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (11; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:150` · `(nivel do modulo)` · item de tuple literal
  - `core/automatico.py:176` · `campos_da_pagina_no_filtro` · item de list literal
  - `core/perfis.py:61` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:2440` · `PainelDeOpcoes._opcoes_do_painel_filtro.<lambda>` · texto passado a self._mudou(...)
  - `ui/automatico.py:2442` · `PainelDeOpcoes._opcoes_do_painel_filtro` · self.controles["campo"] = ...
  - `ui/automatico.py:2585` · `PainelDeOpcoes._mostrar_opcoes_do_painel_filtro` · texto passado a o.get(...)
  - `ui/tela_conferir.py:7800` · `TelaConferir._mudar_algoritmo_pb` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9145` · `TelaConferir._campos_do_aplicar_em` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10157` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/filtros_tela_cheia.py:610` · `FiltrosEmTelaCheia._montar_as_opcoes.<lambda>` · texto passado a self._guardar_opcao(...)
  - `ui/widgets/filtros_tela_cheia.py:637` · `FiltrosEmTelaCheia._valores_da_pagina` · chave de dicionario {"campo": ...}

### `alinhar_com_as_outras`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (2; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/analise.py:318` · `(nivel do modulo)` · texto passado a Alerta(...)
  - `ui/tela_conferir.py:7052` · `TelaConferir._alinhar_com_as_outras` · chave de dicionario {"campo": ...}

### `clareza_melhorar`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (4; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:150` · `(nivel do modulo)` · item de tuple literal
  - `core/perfis.py:61` · `(nivel do modulo)` · item de tuple literal
  - `ui/tela_conferir.py:9143` · `TelaConferir._campos_do_aplicar_em` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10156` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `claro_no_escuro`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (10; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:151` · `(nivel do modulo)` · item de tuple literal
  - `core/automatico.py:174` · `campos_da_pagina_no_filtro` · item de list literal
  - `core/perfis.py:62` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:223` · `_texto_das_opcoes_da_pagina` · chave de dicionario {"campo": ...}
  - `ui/automatico.py:2444` · `PainelDeOpcoes._opcoes_do_painel_filtro` · item de tuple literal
  - `ui/automatico.py:2587` · `PainelDeOpcoes._mostrar_opcoes_do_painel_filtro` · item de tuple literal
  - `ui/tela_conferir.py:7834` · `TelaConferir._mudar_claro_no_escuro` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10161` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/filtros_tela_cheia.py:615` · `FiltrosEmTelaCheia._montar_as_opcoes` · item de tuple literal
  - `ui/widgets/filtros_tela_cheia.py:638` · `FiltrosEmTelaCheia._valores_da_pagina` · chave de dicionario {"campo": ...}

### `conteudo_deslocamento`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (6; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/dividir_a_mao.py:89` · `(nivel do modulo)` · dict(conteudo_deslocamento=...)
  - `core/girar.py:303` · `campos_da_pagina_que_giram_junto` · campos["campo"] = ...
  - `ui/desfazer_nesta_pagina.py:155` · `campos_para_desfazer` · campos["campo"] = ...
  - `ui/tela_conferir.py:2513` · `TelaConferir._gravar_o_conteudo` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10054` · `(nivel do modulo)` · item de set literal
  - `ui/tela_conferir.py:10166` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `conteudo_escala`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (5; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/dividir_a_mao.py:88` · `(nivel do modulo)` · dict(conteudo_escala=...)
  - `ui/desfazer_nesta_pagina.py:154` · `campos_para_desfazer` · campos["campo"] = ...
  - `ui/tela_conferir.py:2513` · `TelaConferir._gravar_o_conteudo` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10054` · `(nivel do modulo)` · item de set literal
  - `ui/tela_conferir.py:10166` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `desentortar`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (1; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `ui/tela_conferir.py:7741` · `TelaConferir._mudar_desentortar` · chave de dicionario {"campo": ...}

### `desentortar_aumentar`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (2; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `ui/tela_conferir.py:9605` · `TelaConferir._desentortar_aumentando` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9628` · `TelaConferir._desfazer_aumento_do_desentortar` · chave de dicionario {"campo": ...}

### `giro_da_pagina`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (6; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/dividir_a_mao.py:100` · `(nivel do modulo)` · dict(giro_da_pagina=...)
  - `core/girar.py:315` · `campos_do_giro_da_pagina` · chave de dicionario {"campo": ...}
  - `core/girar.py:397` · `campos_do_giro_das_paginas` · chave de dicionario {"campo": ...}
  - `core/girar.py:412` · `campos_do_giro_relativo_das_paginas` · chave de dicionario {"campo": ...}
  - `core/girar.py:487` · `campos_do_giro_numa_folha_inteira` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6926` · `TelaConferir` · item de set literal

### `gravuras_em_tons_de_cinza`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (11; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:153` · `(nivel do modulo)` · item de tuple literal
  - `core/automatico.py:177` · `campos_da_pagina_no_filtro` · item de list literal
  - `core/perfis.py:65` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:229` · `_texto_das_opcoes_da_pagina` · chave de dicionario {"campo": ...}
  - `ui/automatico.py:2408` · `PainelDeOpcoes._opcoes_do_painel_filtro` · texto passado a self._caixa(...)
  - `ui/automatico.py:2587` · `PainelDeOpcoes._mostrar_opcoes_do_painel_filtro` · item de tuple literal
  - `ui/tela_conferir.py:7901` · `TelaConferir._mudar_gravuras_em_cinza` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9156` · `TelaConferir._campos_do_aplicar_em` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10164` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/filtros_tela_cheia.py:572` · `FiltrosEmTelaCheia._montar_as_opcoes.<lambda>` · texto passado a self._guardar_opcao(...)
  - `ui/widgets/filtros_tela_cheia.py:641` · `FiltrosEmTelaCheia._valores_da_pagina` · chave de dicionario {"campo": ...}

### `intensidade_magico`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (4; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:150` · `(nivel do modulo)` · item de tuple literal
  - `core/perfis.py:61` · `(nivel do modulo)` · item de tuple literal
  - `ui/tela_conferir.py:9144` · `TelaConferir._campos_do_aplicar_em` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10156` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `letras_com_a_cor`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (13; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:151` · `(nivel do modulo)` · item de tuple literal
  - `core/automatico.py:176` · `campos_da_pagina_no_filtro` · item de list literal
  - `core/perfis.py:62` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:224` · `_texto_das_opcoes_da_pagina` · chave de dicionario {"campo": ...}
  - `ui/automatico.py:2445` · `PainelDeOpcoes._opcoes_do_painel_filtro` · item de tuple literal
  - `ui/automatico.py:2588` · `PainelDeOpcoes._mostrar_opcoes_do_painel_filtro` · item de tuple literal
  - `ui/tela_conferir.py:3489` · `TelaConferir._montar_aba_filtro` · item de tuple literal
  - `ui/tela_conferir.py:8064` · `TelaConferir._configurar_medidor` · item de tuple literal
  - `ui/tela_conferir.py:8399` · `TelaConferir._gravar_opcao_da_tela_cheia` · item de tuple literal
  - `ui/tela_conferir.py:9149` · `TelaConferir._campos_do_aplicar_em` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10162` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/filtros_tela_cheia.py:616` · `FiltrosEmTelaCheia._montar_as_opcoes` · item de tuple literal
  - `ui/widgets/filtros_tela_cheia.py:639` · `FiltrosEmTelaCheia._valores_da_pagina` · chave de dicionario {"campo": ...}

### `linha_a_mao`

ConfigFolha · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (2; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `ui/tela_conferir.py:6152` · `TelaConferir._mover_a_linha_da_folha_inteira` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:6527` · `TelaConferir._trocar_jeito_da_folha` · campos["campo"] = ...

### `luz_chuvisco`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (11; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:152` · `(nivel do modulo)` · item de tuple literal
  - `core/automatico.py:174` · `campos_da_pagina_no_filtro` · item de list literal
  - `core/luz_scantailor.py:89` · `(nivel do modulo)` · item de tuple literal
  - `core/perfis.py:63` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:2460` · `PainelDeOpcoes._opcoes_do_painel_filtro.<lambda>` · texto passado a self._mudou(...)
  - `ui/automatico.py:2464` · `PainelDeOpcoes._opcoes_do_painel_filtro` · self.controles["campo"] = ...
  - `ui/automatico.py:2594` · `PainelDeOpcoes._mostrar_opcoes_do_painel_filtro` · texto passado a o.get(...)
  - `ui/automatico.py:2606` · `PainelDeOpcoes._mostrar_opcoes_do_painel_filtro` · texto passado a o.get(...)
  - `ui/tela_conferir.py:3531` · `TelaConferir._montar_aba_filtro.<lambda>` · texto passado a self._mudar_luz(...)
  - `ui/tela_conferir.py:7968` · `TelaConferir._mudar_luz` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10161` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `luz_igualar`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (11; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:152` · `(nivel do modulo)` · item de tuple literal
  - `core/automatico.py:174` · `campos_da_pagina_no_filtro` · item de list literal
  - `core/luz_scantailor.py:89` · `(nivel do modulo)` · item de tuple literal
  - `core/perfis.py:63` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:226` · `_texto_das_opcoes_da_pagina` · chave de dicionario {"campo": ...}
  - `ui/automatico.py:2447` · `PainelDeOpcoes._opcoes_do_painel_filtro` · item de tuple literal
  - `ui/automatico.py:2588` · `PainelDeOpcoes._mostrar_opcoes_do_painel_filtro` · item de tuple literal
  - `ui/automatico.py:2605` · `PainelDeOpcoes._mostrar_opcoes_do_painel_filtro` · texto passado a o.get(...)
  - `ui/tela_conferir.py:3516` · `TelaConferir._montar_aba_filtro` · item de tuple literal
  - `ui/tela_conferir.py:7966` · `TelaConferir._mudar_luz` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10160` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `luz_suavizar`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (10; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:152` · `(nivel do modulo)` · item de tuple literal
  - `core/automatico.py:176` · `campos_da_pagina_no_filtro` · item de list literal
  - `core/luz_scantailor.py:89` · `(nivel do modulo)` · item de tuple literal
  - `core/perfis.py:63` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:227` · `_texto_das_opcoes_da_pagina` · chave de dicionario {"campo": ...}
  - `ui/automatico.py:2448` · `PainelDeOpcoes._opcoes_do_painel_filtro` · item de tuple literal
  - `ui/automatico.py:2588` · `PainelDeOpcoes._mostrar_opcoes_do_painel_filtro` · item de tuple literal
  - `ui/tela_conferir.py:3517` · `TelaConferir._montar_aba_filtro` · item de tuple literal
  - `ui/tela_conferir.py:7967` · `TelaConferir._mudar_luz` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10160` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `reduzir_cores`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (13; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:151` · `(nivel do modulo)` · item de tuple literal
  - `core/automatico.py:174` · `campos_da_pagina_no_filtro` · item de list literal
  - `core/perfis.py:62` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:225` · `_texto_das_opcoes_da_pagina` · chave de dicionario {"campo": ...}
  - `ui/automatico.py:2446` · `PainelDeOpcoes._opcoes_do_painel_filtro` · item de tuple literal
  - `ui/automatico.py:2588` · `PainelDeOpcoes._mostrar_opcoes_do_painel_filtro` · item de tuple literal
  - `ui/tela_conferir.py:3491` · `TelaConferir._montar_aba_filtro` · item de tuple literal
  - `ui/tela_conferir.py:8065` · `TelaConferir._configurar_medidor` · item de tuple literal
  - `ui/tela_conferir.py:8399` · `TelaConferir._gravar_opcao_da_tela_cheia` · item de tuple literal
  - `ui/tela_conferir.py:9150` · `TelaConferir._campos_do_aplicar_em` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10162` · `(nivel do modulo)` · chave de dicionario {"campo": ...}
  - `ui/widgets/filtros_tela_cheia.py:617` · `FiltrosEmTelaCheia._montar_as_opcoes` · item de tuple literal
  - `ui/widgets/filtros_tela_cheia.py:640` · `FiltrosEmTelaCheia._valores_da_pagina` · chave de dicionario {"campo": ...}

### `respeitar_gravuras_achadas`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (11; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:152` · `(nivel do modulo)` · item de tuple literal
  - `core/automatico.py:173` · `campos_da_pagina_no_filtro` · item de tuple literal
  - `core/automatico.py:178` · `campos_da_pagina_no_filtro` · item de tuple literal
  - `core/perfis.py:63` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:228` · `_texto_das_opcoes_da_pagina` · chave de dicionario {"campo": ...}
  - `ui/automatico.py:2401` · `PainelDeOpcoes._opcoes_do_painel_filtro` · texto passado a self._caixa(...)
  - `ui/automatico.py:2587` · `PainelDeOpcoes._mostrar_opcoes_do_painel_filtro` · item de tuple literal
  - `ui/desfazer_nesta_pagina.py:162` · `campos_para_desfazer` · campos["campo"] = ...
  - `ui/tela_conferir.py:7855` · `TelaConferir._mudar_respeitar_gravuras` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:9153` · `TelaConferir._campos_do_aplicar_em` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10163` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `retangulo_do_corte`

ConfigPagina · nome exclusivo? NAO: tambem e atributo de Projeto (modelos.py) · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (9; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:232` · `(nivel do modulo)` · item de tuple literal
  - `core/perfis.py:55` · `(nivel do modulo)` · item de tuple literal
  - `ui/automatico.py:2302` · `PainelDeOpcoes._opcoes_endireitar` · texto passado a self._combo(...)
  - `ui/automatico.py:2643` · `PainelDeOpcoes._mostrar_opcoes` · item de tuple literal
  - `ui/tela_conferir.py:7158` · `TelaConferir._jeito_do_retangulo` · texto passado a configuracoes.ler(...)
  - `ui/tela_conferir.py:7233` · `TelaConferir._mudar_retangulo_da_pagina` · texto passado a self._registrar(...)
  - `ui/tela_conferir.py:7234` · `TelaConferir._mudar_retangulo_da_pagina` · chave de dicionario {"campo": ...}
  - `ui/tela_configuracoes.py:276` · `TelaConfiguracoes._parte_medidas` · texto passado a configuracoes.ler(...)
  - `ui/tela_configuracoes.py:281` · `TelaConfiguracoes._parte_medidas.<lambda>` · texto passado a configuracoes.escrever(...)

### `tamanho_folha_cm`

ConfigPagina · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (5; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/dividir_a_mao.py:89` · `(nivel do modulo)` · dict(tamanho_folha_cm=...)
  - `core/girar.py:298` · `campos_da_pagina_que_giram_junto` · campos["campo"] = ...
  - `ui/tela_conferir.py:2141` · `TelaConferir._mudar_tamanho_da_folha` · chave de dicionario {"campo": ...}
  - `ui/tela_conferir.py:10055` · `(nivel do modulo)` · item de set literal
  - `ui/tela_conferir.py:10167` · `(nivel do modulo)` · chave de dicionario {"campo": ...}

### `tampa_do_scanner`

ConfigFolha · nome exclusivo? sim, so destas classes · **0 gravacoes, 0 funcoes diferentes, 0 arquivos**

Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista "nao da para saber o campo" e o nome como texto, abaixo).

Nome como texto (3; nao e gravacao, pode ser gravacao indireta ou leitura):

  - `core/automatico.py:920` · `_a_tampa` · texto passado a g.na_folha(...)
  - `core/dividir_a_mao.py:262` · `campos_para_dividir` · campos["campo"] = ...
  - `ui/tela_conferir.py:6114` · `TelaConferir._mover_corte` · campos["campo"] = ...

