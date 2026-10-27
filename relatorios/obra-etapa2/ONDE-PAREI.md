# Obra de 26/10/2026 — etapa 2 (agente de layout): ONDE PAREI

Ramo `obra-etapa2-2026-10-26` (base `obra-2026-10-26` = `ddd4d74`), worktree `.claude/worktrees/obra-etapa2`.
Ordem do Samuel (D-014): fazer até o fim sem pausas; ele confere tudo no fim.

**Situação: PRONTO PARA CONFERIR** (falta só o que é da gerente: suíte no GitHub/PC, verificador separado, teste do
Kaique de novo — CLAUDE.md §11 regra 5).

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| D-001 (25/09) | "Estrutura: Photoshop puro, sem abas. Uma única tela com todas as ferramentas." | Todas as ferramentas (Dividir, Cortar, Endireitar, Retângulo/Oval, Laço/Ponto a ponto, Pincel, Varinha/Pegar tudo desta cor, Mover a área, Zoom, Mão; Filtro no painel) sempre montadas e à vista, com qualquer combinação de caixinhas, inclusive nenhuma. A regra de julho do `carregar` (`d9fae8c`, `f15e469`, `d83bb03`) sai. |
| R7 203 D (05-06/10) | "D — Ícones na borda, tudo fechado" + "Mas eu também quero ter a opção da area de trabalho 1." | Ícones na borda, tudo fechado, continua de fábrica; a "área de trabalho 1" (lado direito em sanfona) vira escolha. |
| R14 902 C (20/10) | "C — Nos dois lugares" (menu Ver e Configurações) | A escolha do lado direito no menu Ver e nas Configurações (Aparência). |
| R9 403 B (09/10) | "B — Filtros numa fila + partes que abrem e fecham" (+ "abrir em tela cheia") | O painel Filtro substitui o botão provisório "Os quatro filtros" da trilha: o botão sai. |
| 07/10 e 09/10 | "Deixar em branco" (tecla Delete; página branca no lugar, encadernação não muda) e "Tirar do livro"; "Essa opção de tirar do livro ou deixar folha em branco eu quero ter em outras paginas" (PLANO-DEFINITIVO l.473 e l.599-600) | Os dois botões em qualquer página; Delete = deixar em branco. |
| Teste do Kaique (26/10) + R8 302 C | "nenhum menu tem Endireitar/Cortar/Dividir"; ferramentas só com ícone + "quando eu passar em cima da agrupada tem que mostrar a letra dela de atalho." | As ferramentas num menu; a dica com nome + letra funcionando. |
| Lista única 1.12 (23/10) | menus Editar/Marcar/Filtro/Página/Painéis cinza | Menus sempre ativos com livro aberto. |
| Lista única 2.2 (23/10) | caixinha marcada aparece só como tique, sem quadrado | Caixinhas com quadrado à vista, marcadas e desmarcadas, no tema (todas). |
| D-009 (26/10), achada no caminho | "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo manualmente." | (A parte de tela.) Sem caixinha nenhuma o "Conferir" fica aceso e o livro abre. O PDF obedecer ao feito à mão é da etapa 1. |

## Como cumpri cada decisão (prova = teste que falha no código antigo e passa no novo; print = janela de verdade)

Provas em `tests/test_decisoes_tela.py` (35 casos). **Rodadas no código antigo (`ddd4d74`, worktree temporária):
32 de 33 falharam lá** (a 33ª, o balão, já funcionava no antigo para as ferramentas que existiam; ficou como guarda).
Os 2 casos que entraram depois (Conferir aceso, Delete da área) também falham no antigo (lá a Delete apagava a página
e o Conferir ficava cinza: print `antes-02-nao-abriu.png`).

| Decisão | Como ficou | Prova | Print (`relatorios/obra-etapa2/prints/`) |
|---|---|---|---|
| D-001 | `carregar` monta as cinco ferramentas de dentro em todo livro (`ORDEM_DAS_FERRAMENTAS`); a trilha mostra todos os botões (`definir_disponiveis(None)`); `editor_selecao` existe sempre com livro aberto. Abre na 1ª etapa marcada (Dividir, Cortar, Endireitar) ou, sem elas, na página com a Mão. | `test_d001_sem_nenhuma_caixinha_…`, `test_d001_qualquer_combinacao_…` (as 16 combinações das 4 caixinhas), `test_d001_sem_caixinhas_marcar_zoom_mao_e_filtro_funcionam` (o Retângulo marca, o Zoom aproxima, a Mão, o painel Filtro troca o filtro) | `depois-02-area-de-trabalho-sem-caixinhas.png` (10 botões na trilha, sem caixinha nenhuma); antes: `antes-02-nao-abriu.png` |
| D-001 "todos os menus" + 1.12 | Com livro aberto todos os menus acesos, também na tela das caixinhas (menos "Confirmar e processar" e "Voltar para as opções" ali). O que mexe no trabalho passa por `_no_trabalho`: só age no trabalho DESTE livro; na tela das caixinhas de um livro ainda não conferido, avisa "Clique em Conferir" (antes as teclas, que já valiam ali, mexiam no livro anterior). | `test_d001_sem_caixinhas_todos_os_menus_acesos`, `test_na_tela_das_caixinhas_de_livro_novo_o_menu_nao_mexe_no_livro_de_antes` | `depois-01-o-que-fazer-sem-caixinhas.png` (menus acesos); antes: `antes-00-…` (cinza) |
| D-009 (tela) | "Conferir" aceso sem caixinha; o resumo diz "Nada marcado: o livro abre como veio, na área de trabalho, com todas as ferramentas para você fazer à mão." | `test_d001_sem_caixinhas_o_conferir_fica_aceso` | `depois-01-…` × `antes-01-…` ("Marque pelo menos uma coisa", Conferir cinza) |
| R7 203 D + R14 902 C | Ver > "Lado direito": "Ícones na borda (de fábrica)" / "Sanfona (a área de trabalho 1)"; o mesmo em Configurações > Aparência > "Lado direito". Sanfona = coluna de 300 px com os cinco painéis empilhados: o aberto com o cabeçalho e o corpo, os outros só com a linha (setinha, ícone, nome, contagem/subtítulo); clicar na linha abre ali; "»" no alto esconde. Fica guardada (`configuracoes.json`, `lado_direito`). | `test_de_fabrica_icones_na_borda_tudo_fechado`, `test_area_de_trabalho_1_pelo_menu_ver`, `test_area_de_trabalho_1_nas_configuracoes`, `test_a_area_de_trabalho_1_volta_no_proximo_programa` | `depois-07-area-de-trabalho-1-sanfona.png`, `depois-08-sanfona-para-revisar-aberto.png` |
| R9 403 B | "Os quatro filtros" saiu da trilha e não está no menu Ferramentas; o painel "Filtro da página" (fila + tela cheia) faz o mesmo. A "aba" de dentro continua (é dela que o painel tira as amostras). | `test_os_quatro_filtros_sairam_da_trilha_e_o_painel_filtro_faz_o_mesmo`; `tests/test_trilha_agrupada.py` | `depois-02-…` (trilha sem a meia-lua) |
| 07 e 09/10 | Delete = "Deixar em branco" (de novo: volta). Menu Página: "Deixar esta página em branco" (Del), "Tirar esta página do livro" (Shift+Del), "Trazer de volta a página tirada". Bloco "Esta página" no alto do Propriedades, em TODA ferramenta e página: "deixar em branco" / "tirar do livro" (viram "voltar a página" / "trazer de volta"). No painel Filtro, o "apagar página" virou os mesmos dois. Com a ferramenta "Mover e mudar o tamanho da área" e uma área escolhida, a Delete continua apagando só a área. | `test_delete_deixa_em_branco_e_nao_tira_do_livro`, `test_os_dois_botoes_em_qualquer_pagina` (4 ferramentas × 3 páginas, sem aviso nenhum), `test_com_uma_area_escolhida_a_delete_apaga_a_area_e_nao_a_pagina` | `depois-06-delete-deixou-em-branco.png`, `depois-04-*-com-propriedades.png` |
| Teste do Kaique + R8 302 C | Menu novo "Ferramentas" (entre Editar e Marcar): Dividir a folha, Cortar as bordas, Endireitar, as de marcar e Zoom/Mão, com a letra na coluna da direita; marca a da vez e acompanha a trilha. O balão da trilha: nome, letra e as outras do mesmo botão. | `test_o_menu_ferramentas_tem_dividir_cortar_endireitar_e_troca_a_ferramenta`, `test_o_balao_da_trilha_aparece_com_o_nome_e_a_letra` | `depois-05-menu-ferramentas.png`, `depois-03-balao-retangulo.png`, `depois-03-balao-endireitar.png` |
| 2.2 | Todas as caixinhas do programa com quadrado (folha do tema, `_regras_da_caixinha`): desmarcada = quadrado com borda; marcada = quadrado azul com tique branco. | `test_caixinha_marcada_tem_quadrado_azul_e_desmarcada_tem_quadrado` (conta os pixels do quadrado) | `depois-00-o-que-fazer-de-fabrica.png` × `antes-00-…` (só o tique) |

**Sobre "dicas que não apareceram" (teste do Kaique):** o Qt só mostra balão em janela ATIVA; a janela de teste, fora da
tela, abre sem ativar e o Windows manda "o mouse saiu" logo depois de cada movimento postado (depurado: a trilha só recebe
"Enter"). Por isso o agente não viu as dicas. No roteiro (`roteiro/print_sem_caixinhas.py`) o balão foi pedido com o
mesmo evento que o Qt manda depois de 0,7 s parado, e apareceu (prints `depois-03-*`). Com o mouse de verdade, na
janela ativa, falta conferir com os olhos (não mexi no cursor do Samuel).

## O que mudou (arquivos)

- `ui/tela_conferir.py`: `carregar` sem a regra de julho; `_aba_de_partida`/`_ferramenta_de_partida`; `_ligar_ferramentas`
  uma vez só no `_montar`, falando com o editor da vez por `_ao_editor`/`_mudar_no_editor` (antes: uma ligação a mais
  por livro, as antigas apontando para o editor destruído); `editor_selecao` sai em `_limpar_abas`; `_acertar_a_trilha`
  mostra tudo; bloco "Esta página" (`_montar_os_botoes_da_pagina`, `deixar_em_branco_ou_voltar`,
  `_atualizar_os_botoes_da_pagina`); Delete = deixar em branco; `apagar_pagina` = "tirar do livro".
- `ui/widgets/trilha_agrupada.py`: "Os quatro filtros" fora dos grupos; sinal `ferramenta_mudou`.
- `ui/barra_de_menu.py`: menu Ferramentas; Página com os dois itens; Ver > Lado direito; `mostrar_tela_das_opcoes`;
  a lista de atalhos mostra a letra das ferramentas.
- `ui/janela_principal.py`: `_no_trabalho`, `_trocar_lado_direito`, menus acesos na tela das caixinhas.
- `ui/widgets/paineis.py`: `LinhaDaSanfona`, `ColunaDePaineis.definir_jeito` (ícones / sanfona), `jeito_guardado`,
  `guardar_jeito`; cabeçalho avisa quando a contagem/subtítulo muda; painel Filtro com "Esta página".
- `ui/tela_configuracoes.py`: Aparência > "Lado direito".
- `ui/tela_opcoes.py`: Conferir aceso sem caixinha, frase de nada marcado.
- `ui/estilo.py`: caixinha com quadrado para todas; o tique desenhado com o Pillow (a folha nasce antes da QApplication).
- `ui/widgets/editor_selecao.py`: a Delete com área escolhida é do editor (ShortcutOverride).
- `configuracoes.py` (fora de `ui/`, só uma chave nova em `PADROES`: `"lado_direito": "icones"` — sem ela o
  `configuracoes.carregar` joga a chave fora).
- Testes adaptados (pulavam quando faltava ferramenta → agora FALHAM): `tests/test_trilha_agrupada.py`
  (`test_so_aparecem_as_ferramentas_do_livro` virou `test_de_fabrica_a_trilha_mostra_todos_os_botoes` + o de esconder de
  propósito), `tests/test_paineis_na_tela.py` (335, 435 e o do bloco do alto), `tests/test_barra_de_menu.py` (o menu
  novo). `teste_botoes.py`: os dois botões de "Esta página" conferidos uma vez com a promessa, o Lado direito ida e
  volta, o "trazer de volta" no lugar do "restaurar página". `teste_interface.py`: Delete deixa em branco.
- Novo: `tests/test_decisoes_tela.py`; roteiros em `relatorios/obra-etapa2/roteiro/` (`medir_abrir.py`,
  `print_sem_caixinhas.py`, `rodar_por_arquivo.py`, `base.py` copiado do ramo `testes-livros-2026-10-23`).

## Escolhas feitas por mim (D-014: decidir e anotar)

1. **Onde o livro abre:** na 1ª etapa marcada (Dividir → Cortar → Endireitar), como antes; sem nenhuma delas, na página
   com a **Mão** (com "Limpar" + "procurar gravuras", o Retângulo de sempre). A tela provisória dos quatro filtros não é
   mais lugar de abrir: sem o botão na trilha, quem abrisse nela não teria como voltar.
2. **Ferramentas no menu:** um menu novo "Ferramentas" (não o menu Página): o teste do Kaique procurou em todos e não
   achou; um menu com esse nome é o lugar mais fácil de achar. A letra fica só escrita (quem atende a tecla continua a
   tela: um atalho de uma letra no menu roubaria a letra de quem digita num campo).
3. **"Tirar do livro" com tecla:** Shift+Del (a Delete é do "Deixar em branco", decidido em 07/10). Remapeável nas
   Configurações.
4. **Os dois botões em qualquer página:** no alto do painel Propriedades (embaixo do "Girar a folha"), que vale em toda
   ferramenta, e no painel Filtro (no lugar do "apagar página"). No Dividir (que mostra a folha inteira) ficam apagados
   com a explicação no balão.
5. **Sanfona:** só os dois jeitos que o Samuel pediu (ícones e área de trabalho 1); "abas no alto" e "painel solto", que
   a pergunta 902 listava, não foram pedidos e não entraram. Ao entrar na sanfona sem painel aberto, abre o Automático
   (o desenho da área de trabalho 1). O painel aberto mostra o cabeçalho dele (com o "x"), e não a linha com a setinha.
6. **Menus na tela das caixinhas:** acesos; o que mexe no trabalho só age no trabalho deste livro já conferido (o
   Desfazer ali já valia: verificador 30/09, r15); num livro ainda não conferido, aviso "Clique em Conferir".
   "Confirmar e processar" e "Voltar para as opções" ficam apagados ali.
7. **Caixinhas:** todas com quadrado de 18 px (antes 22 px só com tique na tela das caixinhas); borda azul ao passar o
   mouse.

## Velocidade (abrir o Marial, 214 MB, só a montagem da tela; `roteiro/medir_abrir.py`, mediana de 5)

Em palavras: **abrir um livro não ficou mais lento que se veja.** Montar todas as ferramentas sempre custa pouco perto
do resto (a tira de miniaturas e o primeiro desenho); a diferença ficou dentro do vai-e-vem do PC, que estava com
outros agentes rodando.

| Rodada (segundos, mediana) | nenhuma caixinha | só Limpar | tudo | Dividir+Endireitar |
|---|---|---|---|---|
| antes (`ddd4d74`), sozinho, PC calmo (`velocidade-antes.txt`) | 1,33 | 1,35 | 1,44 | 1,37 |
| depois, sozinho, PC já carregado (`velocidade-depois.txt`) | 2,30 | 2,41 | 2,64 | 2,28 |
| A/B alternado, rodada 1: antes / depois | 2,58 / 2,38 | 2,61 / 2,43 | 2,69 / 2,97 | 2,42 / 3,16 |
| A/B alternado, rodada 2: antes / depois | 2,26 / 2,33 | 2,31 / 2,20 | 3,35 / 2,61 | 2,93 / 2,30 |

A primeira comparação (1,3 → 2,3 s) assustou, mas foi o PC: rodando antes e depois alternados, no mesmo momento, os
dois códigos dão o mesmo (ora um ganha, ora o outro). **Ressalva:** a medida que vale (§4.6) é a da gerente, no PC sem
agentes, ou o filtro do GitHub.

## Testes rodados (um arquivo por vez, TEMP e --basetemp na worktree)

- **Todos os arquivos de teste que usam a tela: 70 arquivos, 1060 casos, 0 falhas** (rodada final, depois da última
  mudança; lista arquivo por arquivo em `testes-de-tela-por-arquivo.txt`). Inclui `tests/test_decisoes_tela.py` (35).
- Arquivos sem tela que tocam o `configuracoes.py`: `test_core` 62, `test_impressao` 17, `test_nucleos` 8,
  `test_pasta_de_dados_dos_scripts` 14, `test_pasta_de_dados_dos_testes` 3 — todos passaram.
- `tests/test_decisoes_tela.py` no código antigo (`ddd4d74`): 32 de 33 falharam (teste de reversão, §4.7).
- Janela de verdade fora da tela (`roteiro/print_sem_caixinhas.py`): depois 14 de 14; antes 3 de 5 (não abre sem
  caixinha).
- `teste_botoes.py` (no PC, sem tela): **293 ações, 0 falhas**; inclui os dois botões de "Esta página" com a promessa conferida (em branco / volta / tira / traz de volta) e o Lado direito ida e volta.
- Não rodei a suíte inteira no PC (regra: um arquivo por vez; a inteira é no GitHub, pela gerente).

## Commits (ramo `obra-etapa2-2026-10-26`, com push)

- `ce88dd1` ONDE-PAREI com as decisões e a velocidade antes
- `3be204a` D-001: todas as ferramentas sempre montadas; "Os quatro filtros" fora da trilha
- `82cdada` menu Ferramentas, menus acesos, Delete = em branco, os dois botões, área de trabalho 1, caixinhas com quadrado
- `02ca71e` Conferir aceso sem caixinhas, menus da tela das caixinhas, Delete da área, provas, prints
- `f4a1f38` velocidade, testes por arquivo, teste_botoes, ONDE-PAREI
- (este ONDE-PAREI final)

## Ressalvas

- **Com "Limpar" desligado, o filtro escolhido à mão (e a marcação) ainda não vai ao PDF**: o processamento ignora o
  feito à mão com a etapa desligada. É a etapa 1 (D-009, outro agente); não mexi em `core/`. Até a etapa 1 juntar, a tela
  deixa escolher o que o PDF ainda não obedece.
- O balão com o mouse de verdade (janela ativa) não foi visto por mim (ver acima); falta o olho do Samuel ou o piloto.
- Uma primeira rodada do `teste_botoes.py` ficou parada na tela das caixinhas (o "Confirmar e processar" ainda aceso ali, numa versão intermediária desta entrega); consertado (`mostrar_tela_das_opcoes`), o processo terminou pelo próprio `timeout` e a rodada nova passou inteira.

## Perguntas para o Samuel

1. **Letras para Dividir, Cortar e Endireitar?** Hoje elas não têm atalho de letra (as de marcar têm: R, O, L, P, B, V,
   C, A, Z, E). O balão e o menu Ferramentas mostram só o nome delas. Quer uma letra para cada (ex.: D, X, I), como no
   Photoshop? Não inventei: fica como está até ele dizer.
