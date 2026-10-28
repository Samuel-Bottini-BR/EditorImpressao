# Obra de 26/10/2026 — etapa 9b-1 (menus, impressão, janelas e lado direito): ONDE PAREI

Ramo `obra-etapa9b1-2026-10-26` (base `obra-2026-10-26` = `27b4c52`), worktree `.claude/worktrees/obra-etapa9b1`.
Agente: layout + implementador. Regra 7 (Samuel, 27/10/2026): "é só para fazer o que eu já tinha mandado, fazer as
ferramentas que colocamos no programa funcionem como deveriam e como eu tinha escolhido."

**Situação: PRONTO PARA CONFERIR** (começada e terminada em 27/10/2026). Ramo enviado ao GitHub. (Rodada do GitHub:
ver "GitHub", no fim.)

## Em uma frase

A janela "Montar para imprimir" voltou a ter os nomes de antes (do `fase-1`, os do UPDF) com a disposição nova em duas
colunas; o lado direito tem os quatro jeitos (ícones na borda, sanfona, **abas no alto** e **painel solto**), no menu
Ver e nas Configurações; o tique do menu Filtro acompanha a página; o menu Arquivo > "Confirmar e processar" (e
Ctrl+Return) passa pela "Antes de processar"; o nome sugerido do PDF voltou a ter acento; a "Antes de processar" é a
aprovada no `lm22` e o "Mostrar" não corta mais o motivo; o "Pintar por cima" sobre letras pergunta antes ("Pintar assim
mesmo" / "Voltar"); as teclas chegam à página depois de clicar na lista do Automático; o Desfazer do menu fica apagado
sem nada para desfazer; o cartão deixa de dizer "PDF gerado" quando o trabalho muda depois do PDF; o contador da barra de
baixo aparece inteiro a 1280 com um painel aberto; e os três testes instáveis ficaram estáveis (sem mudar o programa).

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Item | Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|---|
| 1 | Auditoria C3 · `fr-26` (22/10) / D-333 | "Está bom" + "Só tem que melhorar esse layout, cheio de letras uma em cima da outra, tudo bagunçado e dificil de saber o que é o que." | Disposição nova (duas colunas) fica; os NOMES voltam aos de antes. |
| 1 | D-315 (14/10) | "todas as outras opções que aparecem nos prints do PDF que mandei. Quero TODAS essas opções dentro do programa" · `fr22`: APROVADO | Os nomes das opções do UPDF, como estavam no `fase-1`. |
| 1 | D-374 (22/10) | "Anote a ideia de depois revisarmos todos os nomes de botão com um novo agente que vai ser criado." | Nome novo só pela revisão de nomes (etapa 11), decidido por ele. |
| 2 | D-033 (05/10) · R14 902 (20/10) | "Quer os quatro jeitos no app, escolhendo dentro dele: sanfona (o primeiro), abas no alto, ícones na borda, painel flutuante" · `r14-lado-direito-onde`: "C — Nos dois lugares" | Os 4 jeitos no menu Ver > "Lado direito" e em Configurações > Aparência. |
| 2 | R7 203 D (rodada 7) | "Ícones na borda, tudo fechado" + "Mas eu também quero ter a opção da area de trabalho 1." | Ícones na borda continua o de fábrica. |
| 3 | D-492 (27/10, escolha da gerente) · P-085 | "o botão tem que ser provado que ele faz o que se diz" | O tique do menu Filtro acompanha o filtro da página aberta. |
| 4 | D-274 (08/10) · P-127 | "quando alguém tentar imprimir sem ver os alertas o programa para e mostra os alertas e a pessoa diz se quer ver ou continuar" | Menu Arquivo > "Confirmar e processar" (Ctrl+Return) passa pela "Antes de processar", igual ao botão. |
| 5 | D-555 (27/10) | Central `ac-nome-sem-acento`: "Voltar com acento (recomendo)" | Nome sugerido do PDF com acento ("Ofício da Imaculada Conceição - mágico pro.pdf"). |
| 5 | D-365 (18/07) | "Corrija TODOS os textos da interface para português correto" | — |
| 6 | D-283 (21-22/10) · `lm22` | `pr-antes-de-processar`: "Melhorar" + "ficou meio embolado, deve ficar mais claro e não tão grande." · `lm-antes-de-processar`: "Está bom" / `lm22` "Aprovado" (com o "Mostrar" cortado a consertar) | "Antes de processar" do commit `138e425`, e o motivo inteiro no "Mostrar". |
| 6 | D-061 (21-23/10) | `lm22`: "Aprovado" | Trabalho aprovado vai para o programa como estava. |
| 6 | D-285 (21/10) · etapa 7 | `pr-contagens`: "A janela de salvar passa a contar as páginas com aviso pendente" | A contagem da etapa 7 continua (um número só). |
| 7 | D-250 (22/10) | `fr-218-aviso`: "A — Avisar (recomendo)" · no chat: "1- sim" | "Pintar por cima" sobre letras → aviso com "Pintar assim mesmo" e "Voltar"; nada pintado sem confirmar. |
| 8 | D-561 (27/10) | Central `ac-letras`: "Manter (recomendo)" — D, X, I, F, Shift+Del | As teclas não mudam; só passam a chegar à página com o foco na lista do Automático. |
| 8 | D-021 | "Page Up/Down, Home/End" | Page Down anda as páginas também depois de clicar no painel. |
| 9 | D-057 (20-21/10) | `r14-menu-paineis`: "B — Um menu novo, “Painéis”" · `ly-paineis`: "Está bom" | Os "Painel: …" saíram do Ver para o menu Painéis; cada item abre o painel. |
| 9 | D-020 (18/07) · P-125 | "13. Ctrl+Z desfaz qualquer alteração, sem limite de quantidade, e Ctrl+Shift+Z refaz" | Desfazer apagado sem nada para desfazer (barra de baixo e menu). |
| 9 | D-309 (05/10) | "pode mandar concertar, mas continue com a fase 2 em paralelo" | O cartão só diz "PDF gerado" quando o PDF é o do trabalho de agora (Lista de bugs 332). |
| 9 | D-342 (05/10) | "o programa quando estiver pronto, ele vai ter que ser capaz de abrir arquivos de versões anteriores." | `projeto.json` ilegível: cópia guardada e aviso na tela. |
| 10 | D-045 (06/10) · D-015 (22/10) · etapa 7 ressalva 1 | R9 405: "C — Os dois" · "Uma página / Duas lado a lado" na barra de baixo | Barra de baixo com tudo o que tem; o contador inteiro a 1280 com painel aberto, sem tirar nada. |
| 11 | D-272 · D-280 · P-092 · P-094 | "com todas as paginas ou com todos os motivos" | Testes estáveis sem mudar o programa só para o teste passar. |

## Como cumpri cada uma

Prova: `tests/test_decisoes_9b1.py` (25 testes; os 20 marcados REVERSÃO falham no código antigo `27b4c52`, cada um pelo
defeito que conserta: `relatorios/obra-etapa9b1/reversao-no-codigo-antigo.txt`). Prints da janela de verdade em
`relatorios/obra-etapa9b1/prints/` (ver "Prints").

| Item | O que ficou no programa | Prova | Print (depois × antes) |
|---|---|---|---|
| 1 nomes (C3, D-315, D-333, D-374) | `ui/dialogo_impressao.py`: voltaram os nomes do `fase-1` — "Ordem de páginas", "Páginas por caderno" (com os números sozinhos na lista, como era), "Rotação automática", "Centralizar automático", "Reverter páginas", "Agrupar", "Esquerda"/"Direita", "cancelar" (os oito da auditoria) e também os outros que a 9a tinha trocado: "Escala personalizada", "em pé (retrato)"/"deitada (paisagem)", "Frente e verso"/"Só a frente"/"Só o verso", "Horizontal"/"Vertical", "Escala de cada lado", "Só uma página", "Imprimir em escala de cinza", "Folhas de (0 = todas)", "Páginas do livro de (0 = todas)", "(a de sempre do Windows)", "Impressora (para mandar direto)". **Ficou da 9a** só a disposição: as duas colunas com o cartão "O que vai sair", o texto que era parêntese virou a frase de baixo da caixinha (a de "Rotação automática" é a do `fase-1`, "Página deitada gira de pé."), o nome curto do formato com a explicação embaixo e o "todas" escrito no campo. Promessa P-162 acompanha ("cancelar"). | `test_c3_nomes_da_montar_para_imprimir_sao_os_do_fase_1` (os do `fase-1` voltaram, os da 9a saíram, o cartão continua) | `depois-17` e `-17b` × `antes-17` |
| 2 quatro jeitos (D-033, R14 902 C) | `ui/widgets/paineis.py`: `JEITOS_DO_LADO_DIREITO` com os quatro, nomes da pergunta 902 ("Ícones na borda (de fábrica)", "Sanfona (a área de trabalho 1)", "Abas no alto", "Painel solto"); o menu Ver e as Configurações leem a mesma lista (aparecem nos dois, o mesmo caminho, guardado para a próxima vez). **Abas no alto** (desenho `7-paineis-da-direita-opcao-1` / `13-rodada7-padrao-c-abas`, "aberto em Revisar"): coluna de 300 px com as cinco abas no alto (ícone e nome curto: "Revisar", "Automático", "Propriedades", "Filtro", "Histórico"; o nome inteiro no balão; a bolinha laranja no "Revisar"), o painel embaixo; abre no "Para revisar"; clicar na aba aberta não fecha; a seta ">>" na ponta esconde a coluna. **Painel solto** (desenho `7-paineis-da-direita-opcao-3` / `13-rodada7-padrao-e-flutuante`): os botões dos cinco painéis vão para a linha de cima, à direita (só o ícone; nome no balão); o painel abre POR CIMA da página, no canto de cima à direita (12 da direita, 10 do alto, borda arredondada), a página não encolhe; clicar de novo no botão fecha; fora da tela de trabalho os botões somem. Ícones na borda continua o de fábrica. | `test_d033_os_quatro_jeitos_no_menu_ver_e_nas_configuracoes`, `test_d033_abas_no_alto` (clique do mouse nas abas), `test_d033_painel_solto` (a página não encolhe; o painel por cima, no canto); P-043 com os quatro; `teste_botoes.py` (os quatro, ida e volta) | `depois-04` (menu), `-05` ícones, `-06`/`-07` abas, `-08` solto, `-09` sanfona, `-10` Configurações × `antes-04` (dois jeitos), `antes-10` |
| 3 tique do Filtro (D-492, P-085) | `ui/janela_principal._marcar_o_filtro_no_menu`: marca só o filtro da página da tela, a cada mudança da tela (folhear, trocar filtro por qualquer lugar, desfazer) e ao abrir o menu; o clique no item já marcado não tira mais a marca. Página em "Tirar o fundo" (que o menu não tem): nenhum marcado. P-085 sem "defeito". | `test_d492_tique_do_menu_filtro_acompanha_a_pagina`, `test_d492_clicar_no_filtro_que_ja_esta_nao_tira_a_marca`; P-085 | `depois-02` (página 2 em Preto e branco) e `-03` (página 1, Original) × `antes-02`/`-03` (a marca ficou em "Preto e branco" na página 1, que está em Original) |
| 4 menu processar (D-274, P-127) | O menu Arquivo > "Confirmar e processar" (e Ctrl+Return) chama o mesmo caminho do botão (`TelaConferir._pedir_processamento`): com aviso pendente, a "Antes de processar"; sem aviso, direto à janela de salvar. P-127 sem "defeito". | `test_d274_menu_e_ctrl_return_mostram_antes_de_processar[menu/tecla]`, `test_d274_sem_aviso_o_menu_vai_direto_para_salvar`; P-127 | `depois-13` (pelo menu) × `antes-13-menu-processar-foi-direto-para-salvar` |
| 5 acento (D-555) | `modelos.nome_de_saida_sugerido` e `ui/dialogo_impressao.destino_sugerido` sem o `sem_acento` (as duas funções `sem_acento` das etapas 9a/9c saíram; ninguém mais as usava). As três provas que exigiam o sem acento (`test_core`, `test_decisoes_nucleo`, `test_decisoes_impressao`) agora exigem o acento e conferem que o sem acento saiu. | `test_d555_nome_do_pdf_pronto_e_do_para_imprimir_com_acento`; `test_d555_*` dos outros dois arquivos | `depois-16` ("Sobre a Consolação da Filosofia - Severino Boécio - arrumado.pdf") × `antes-16` ("Consolacao", "Boecio") |
| 6 "Antes de processar" (D-283, `lm22`, D-061) | `138e425` trazido por cherry-pick (sem conflito: a frase de cima já usa a contagem da etapa 7, `frase_de_quantos(avisos, projeto)`); o "Mostrar" tem a largura do motivo mais comprido da lista (antes 20 letras, cortava o "(12)"); a janela só passa dos 500 pontos quando um motivo comprido precisa (558 × 400 no print). | `test_d283_antes_de_processar_aprovada_e_o_mostrar_nao_corta` (mede o campo de texto do "Mostrar" contra o motivo); `test_antes_de_processar_menor_e_em_duas_filas` (do `138e425`) | `depois-13`, `-14` ("Endireitar: as contas discordam (11)" inteiro), `-15` × `antes-14` (a janela velha, 560 × 520) |
| 7 "Pintar por cima" (D-250) | `core/editar_zonas.letras_na_area` / `cobre_letras` (conta os borrões de tinta do tamanho de letra dentro do retângulo, pelo Preto e branco da página, só lendo; 3 ou mais = cobre letras) e, na ferramenta de marcar, o retângulo de "Pintar por cima" sobre letras pergunta antes, com o texto e os botões aprovados no `fr-218-aviso` ("Este retângulo cobre letras; elas vão ser pintadas também." · "Pintar assim mesmo" / "Voltar"). "Voltar" (ou fechar) não pinta nada. Sem letras (margem, sombra da lombada) pinta direto. Promessa nova P-079; P-070/P-071 respondem ao aviso. | `test_d250_pintar_por_cima_das_letras_pergunta_antes[Pintar assim mesmo/Voltar]` (o Marial 7 do gabarito, o caso do teste dele), `test_d250_sem_letras_pinta_sem_perguntar`; P-079 | `depois-18` (o aviso) e `-19` (depois do "Voltar": nada pintado) × `antes-19` (pintou as letras sem perguntar) |
| 8 foco preso (D-561, D-021) | A lista de etapas do painel Automático, a rolagem dos painéis e a rolagem da tira de miniaturas não pegam mais o teclado (o mesmo jeito dos botões do painel e da lista do "Para revisar", que já eram assim). O mouse continua igual (clicar escolhe a etapa, a caixinha liga, arrastar muda a ordem, a roda rola). As teclas não mudaram. Achado ao provar: o Page Down ficava preso também na rolagem da tira (ao abrir o livro e depois de clicar numa miniatura) e na rolagem do painel; consertado junto. | `test_teclas_chegam_a_pagina_depois_de_clicar_na_lista_do_automatico[D/PageDown/2]`, `test_page_down_chega_a_pagina_depois_de_clicar_numa_miniatura` | `depois-12` (página 1 → 11 com Page Down depois do clique na lista) × `antes-12` (ficou na página 1) |
| 9 Desfazer (P-125, D-020) | Menu Editar > Desfazer/Refazer acesos só quando há o que desfazer/refazer, como os da barra de baixo (`_acertar_o_desfazer_do_menu`). P-125 sem "aguarda". | `test_p125_desfazer_do_menu_acompanha_o_que_ha_para_desfazer`; P-125 | `depois-01` (cinza) × `antes-01` (aceso) |
| 9 cartão "PDF gerado" (D-309, bug 332) | Mudou o trabalho depois do PDF (uma ação a mais, a menos ou outra na pilha do desfazer, ou a marcação mexida à mão) → o cartão volta a "N de M conferidas" com "continuar" (os dois jeitos que ele já tinha); folhear não conta; gerar de novo → pronto outra vez. | `test_d309_cartao_deixa_de_dizer_pronto_quando_o_trabalho_muda`, `test_d309_marcacao_mexida_tambem_tira_o_pronto`; `tests/test_cartao_pdf_gerado.py` (4) | — |
| 9 `projeto.json` ilegível (D-342) | **A etapa 3 já cobria:** abrir com o arquivo estragado mostra "Comecei a conferência deste livro de novo: o trabalho salvo não pôde ser lido…" com a cópia, e a 9c guarda o estragado ao lado. Nada mudou. | `test_d342_projeto_ilegivel_mostra_o_aviso` (passa no antigo e no novo) | — |
| 9 "Painel: …" (D-057) | **Já resolvido:** os "Painel: …" saíram do menu Ver para o menu Painéis (rodada 14); cada item abre o painel. Nada mudou. | `test_d057_menu_paineis_abre_cada_painel_e_o_ver_nao_tem_painel` (passa no antigo e no novo) | — |
| 10 contador (etapa 7, ressalva 1) | Nada saiu da barra. Quando a conta não cabe numa linha, ela vai em duas ("1 de 50 conferidas" / "2 com dúvida"), em letra 11 (cabe nos 30 pontos da barra); o nome do livro fica no balão; os vãos da barra ficaram menores (6 → 4 e 8 → 4; a folga dos botões pequenos, 7 → 5). Com o painel fechado continua numa linha só, com o nome. | `test_contador_da_barra_de_baixo_em_duas_linhas_quando_nao_cabe_em_uma`, `test_barra_de_baixo_nada_saiu` | `depois-11` × `antes-11` ("1 de 50 c…") |
| 11 testes instáveis | **P-092/P-094:** a medida do livro novo por trás (D-284) termina depois de abrir e PÕE OS AVISOS do livro por cima dos que a prova tinha posto à mão; quando ela terminava no meio da prova, os avisos sumiam ("0 == 3"). O ajudante que abre o livro agora espera a medida terminar. **Página torta:** a análise mede as folhas em vários trabalhadores ao mesmo tempo (item 2.16) e a medida falsa do teste dava os ângulos na ordem das chamadas, não das páginas; o teste agora usa um trabalhador só. **Também:** a ferramenta de marcar recebe a imagem da página por trás; as provas de marcar esperam a imagem (o aviso do D-250 mede nela). O programa não mudou em nada disso. | Antes × depois, só o teste: página torta 12 de 15 falharam × 0 de 15; P-092/P-094 5 de 25 × 0 de 25 | — |

## Arquivos mudados

- Tela: `ui/dialogo_impressao.py`, `ui/janela_principal.py`, `ui/janela_dos_avisos.py` (cherry-pick + "Mostrar"),
  `ui/widgets/paineis.py` (os quatro jeitos; a rolagem dos painéis), `ui/barra_de_menu.py` e `ui/tela_configuracoes.py`
  (só comentários), `ui/automatico.py` (a lista do painel), `ui/widgets/tira_miniaturas.py` (a rolagem), `ui/estilo.py`
  (a folga dos botões pequenos da barra de baixo).
- **Na área do outro agente (9b-2), o mínimo:** `ui/tela_conferir.py` — só a classe `_RotuloDoLivro` (as duas linhas)
  e os números dos vãos em `_montar_barra_de_baixo`/`_montar_o_ver_da_barra_de_baixo` (constantes
  `ESPACO_DA_BARRA_DE_BAIXO`, `RESPIRO_DA_BARRA_DE_BAIXO`); `ui/widgets/editor_selecao.py` — duas linhas em
  `_acrescentar` e o método `_pintar_mesmo_sobre_letras` (o aviso do D-250). Na junção, conferir esses dois arquivos.
- Núcleo: `modelos.py` (o nome com acento), `core/editar_zonas.py` (só acrescentei `letras_na_area`/`cobre_letras`, que
  só leem; o processamento e o PDF não mudam — não precisa do filtro de velocidade).
- Testes: `tests/test_decisoes_9b1.py` (novo), `tests/test_promessas.py` + `tests/promessas/promessas.md` (P-043 com os
  quatro, P-079 nova, P-085/P-127 sem "defeito", P-125 sem "aguarda", P-162 "cancelar", P-070/P-071 respondem ao aviso,
  a varredura acha o aviso do "Pintar por cima"), `tests/promessas/ajudantes.py` (espera a medida ao abrir),
  `tests/test_paginas_diferentes.py` (um trabalhador), `tests/test_core.py`, `tests/test_decisoes_nucleo.py`,
  `tests/test_decisoes_impressao.py` (o acento), `tests/test_decisoes_tela.py` (os quatro nas Configurações),
  `teste_botoes.py` (os quatro jeitos).
- Livro de decisões: só a coluna "situação" de D-020, D-033, D-250, D-283, D-309, D-333, D-492, D-555.
- `relatorios/layout-antes-de-processar/` (veio com o cherry-pick de `138e425`: os prints antes/depois aprovados).

## Testes

(números finais na seção "GitHub")

- No PC, um arquivo por vez: `test_decisoes_9b1.py` 25 passaram; `test_promessas.py` inteiro (ver GitHub);
  `test_decisoes_tela.py` 35, `test_decisoes_ver.py` 11, `test_decisoes_avisos.py` 13, `test_decisoes_automatico.py`
  24, `test_decisoes_impressao.py` 22, `test_dialogo_impressao.py` 5, `test_impressao.py` 17, `test_paineis.py` 34,
  `test_menu_paineis.py` 3, `test_cartao_pdf_gerado.py` 4, `test_para_revisar_na_tela.py` 26, `test_editor_selecao.py`
  17, `test_editar_zonas.py` 10, `test_miniaturas_novas.py` 5, `test_paginas_diferentes.py` (as duas da análise, 15
  vezes seguidas sem falhar).
- Reversão: `relatorios/obra-etapa9b1/reversao-no-codigo-antigo.txt` — os 20 REVERSÃO falham no `27b4c52`, cada um pelo
  defeito (ex.: "Oficio" sem acento; "livro aberto sem a marca"; "a janela 'Antes de processar' não apareceu"; "o
  cartão continua 'PDF gerado'"; "nomes do fase-1 que não voltaram"; "o teclado ficou no painel (ListaDeEtapas)";
  "'0 de 360 conferid…'"; `KeyError: 'lado_abas'`).

## Prints da janela de verdade (1280×657 lógicos, a 125% deste PC = 1600×821; fora da tela)

Roteiro `relatorios/obra-etapa9b1/roteiro/prints.py` (base da etapa 3: cliques e teclas por mensagens do Windows,
PrintWindow; a troca do jeito do lado direito pelo item do menu, `trigger`). Cópias do Boécio ("Sobre a Consolação da
Filosofia - Severino Boécio.pdf", o nome com acento) e do Marial (página 7). Nunca processa (janela de salvar em
"voltar"). Os números de cada passo: `depois-numeros.txt` / `antes-numeros.txt`; os textos das janelas:
`depois-textos.txt`. Abri e olhei todos.

- `depois-01` menu Editar sem nada feito: Desfazer e Refazer cinza (`antes-01`: acesos).
- `depois-02`/`-03` menu Filtro: Preto e branco marcado na página 2 (posto pela tecla 2), Original na página 1
  (`antes-03`: continuava "Preto e branco" na página 1).
- `depois-04` Ver > Lado direito com os quatro (`antes-04`: dois); `-05` ícones na borda; `-06` abas no alto (aberto em
  "Revisar"); `-07` clique (mensagem do Windows) na aba "Filtro"; `-08` painel solto: os botões na linha de cima e o
  "Para revisar" por cima da página, a página do mesmo tamanho; `-09` sanfona; `-10` Configurações > Aparência com os
  quatro.
- `depois-11` barra de baixo a 1280 com o "Para revisar" aberto: "1 de 50 conferidas / 2 com dúvida" em duas linhas
  (`antes-11`: "1 de 50 c…").
- `depois-12` clique na página, clique na lista do Automático, Page Down: página 1 → 11 (`antes-12`: ficou na 1).
- `depois-13` menu Arquivo > "Confirmar e processar" com 13 páginas com aviso: a "Antes de processar" (`antes-13-menu-
  processar-foi-direto-para-salvar`: foi direto à janela de salvar); `-14` "Mostrar" em "Endireitar: as contas
  discordam (11)", inteiro; `-15` a mesma pelo botão. **Os avisos dessas 12 páginas foram postos pelo roteiro para a
  foto** (o Boécio novo só tem 2). No "antes", `antes-13/14/15` são a janela velha aberta pelo botão.
- `depois-16` janela de salvar: "Sobre a Consolação da Filosofia - Severino Boécio - arrumado.pdf" (`antes-16`:
  "Consolacao", "Boecio").
- `depois-17`/`-17b` "Montar para imprimir" (em cima e rolada para baixo) com os nomes do `fase-1` (`antes-17`: "Cada
  caderno", "costura à esquerda", "Imprimir", "Folhas de papel", "parar").
- `depois-18` o aviso do "Pintar por cima" no Marial 7 (retângulo sobre o começo das linhas, arrastado por mensagens do
  Windows); `-19` depois do "Voltar": nenhuma área (`antes-19`: a área roxa pintada sobre as letras, sem perguntar).

## Ressalvas

1. **Mexi em dois arquivos da área da 9b-2** (`ui/tela_conferir.py`, `ui/widgets/editor_selecao.py`), o mínimo
   (listado acima). Conferir na junção.
2. **Painel solto:** os botões de cima são só o ícone (o nome fica no balão): com o nome escrito ao lado, como no
   desenho, eles não cabem na linha dos menus a 1280 junto com os ajustes da ferramenta. O painel fica dentro da altura
   da página (para não cobrir a faixa do aviso e o "está certo"); num livro novo, com a faixa "Livro novo: ainda não
   passou pelo automático", a página é mais baixa e o "Para revisar" fica com pouca lista à vista (rola). Pergunta 1.
3. **Abas no alto:** o cabeçalho do painel (nome, subtítulo, "x", o botão de tela cheia do Filtro) continua embaixo das
   abas, como na sanfona — no desenho das abas não havia cabeçalho; tirar levaria o "x" e o botão de tela cheia. Os
   nomes curtos das abas são os do desenho, com "Propriedades" no lugar de "Ajustes". Pergunta 2.
4. **"Montar para imprimir":** voltaram todos os nomes que a 9a tinha trocado, não só os oito da auditoria (a lista
   completa está na tabela). Ficou redundante "Folhas de (0 = todas): todas até todas" (o rótulo do `fase-1` e o "todas"
   escrito no campo, da 9a). Pergunta 3.
5. **D-250 vale só para o retângulo** (a decisão fala do retângulo); oval, laço e pincel de "Pintar por cima" pintam
   sem perguntar, como antes. A conta mede a imagem que a ferramenta de marcar mostra; se a pessoa desenhar antes de a
   página chegar (fração de segundo ao trocar de página), pinta sem perguntar. Pergunta 4.
6. **Cartão "PDF gerado":** mudar o trabalho depois do PDF tira o "pronto" (volta "N de M conferidas" e "continuar"; o
   "abrir a pasta" sai até gerar de novo). Não criei texto novo ("PDF desatualizado") porque não está no Livro.
   Pergunta 5. Mudança que não passa pela pilha do desfazer nem pela marcação (ex.: "procurar de novo") não tira o
   "pronto".
7. **Foco:** além da lista do Automático, a rolagem dos painéis e a da tira não pegam mais o teclado (o Page Down ficava
   preso nelas). Com isso as setas do teclado não rolam a tira nem o painel (a roda do mouse, a barra e as setinhas da
   tira continuam).
8. **Contador:** com um painel aberto a 1280, o nome do livro sai da barra (fica no balão) e a conta vai em duas linhas,
   em letra 11; a segunda linha encosta na beirada de baixo da barra (inteira no print). Vãos da barra um pouco
   menores.
9. **"Antes de processar"** fica mais larga que os 500 pontos do `138e425` quando há motivo comprido (558 no print),
   para o "Mostrar" caber.
10. **O "Mostrar" do `138e425`** tinha 20 letras de largura fixa; agora acompanha o motivo mais comprido da lista
    (a lista "todos os motivos (N)" fica com a mesma largura).
11. Os testes P-092/P-094 e os de marcar demoram um pouco mais (esperam a medida e a imagem, como o Kaique).
12. A D-554 ("Margens iguais" também no Cortar), a D-558 ("Dividir" na grade) e a D-559 (a tampa no Automático) estão
    no Livro com dono "Etapa 9b", mas não estavam no meu pedido (são da tela de corte e da grade, da 9b-2?). Não fiz.

## Perguntas para o Samuel (com recomendação; nenhuma trava a etapa)

1. **Painel solto: os botões de cima só com o ícone** (o nome no balão), porque com o nome não cabem a 1280; e o painel
   na altura da página (não cobre o aviso nem o "está certo"). *Recomendo deixar assim.*
2. **Abas no alto: o cabeçalho do painel fica embaixo das abas** (repete o nome da aba, mas guarda o "x", o subtítulo e
   o botão de tela cheia do Filtro), e os nomes curtos das abas ("Revisar", "Automático", "Propriedades", "Filtro",
   "Histórico"). *Recomendo deixar assim.*
3. **"Montar para imprimir": voltaram TODOS os nomes do `fase-1`** (não só os oito da auditoria); quer que a revisão de
   nomes (D-374, etapa 11) olhe "Folhas de (0 = todas): todas até todas" e as frases embaixo das caixinhas que a 9a
   escreveu ("Ligada de fábrica: sem ela pode sair algo errado.", "Sai o livro inteiro, depois o livro inteiro de
   novo.")? *Recomendo levar à etapa 11, sem mexer agora.*
4. **O aviso do "Pintar por cima" também para oval, laço e pincel?** Hoje só o retângulo pergunta (a decisão fala do
   retângulo). *Recomendo os quatro (o risco de apagar letras é o mesmo), mas só com o seu "sim".*
5. **Cartão depois de mudar o trabalho:** volta a "N de M conferidas" com "continuar" (some o "abrir a pasta" até gerar
   de novo). Quer um texto próprio, como "PDF desatualizado" com "abrir a pasta"? *Recomendo deixar como está (não
   inventa texto; gerar de novo devolve o "pronto").*

## GitHub

(preenchido no fim)

## Commits (ramo `obra-etapa9b1-2026-10-26`)

(preenchido no fim)
