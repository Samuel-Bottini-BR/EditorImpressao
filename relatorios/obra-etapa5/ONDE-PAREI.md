# Obra de 26/10/2026 — etapa 5 (Mover e redimensionar como ferramenta própria): ONDE PAREI

Ramo `obra-etapa5-2026-10-26` (base `obra-2026-10-26` = `7fb3e4a`), worktree `.claude/worktrees/obra-etapa5`. Agente:
layout + implementador. Ordem do Samuel (D-014): fazer até o fim sem pausas; ele confere tudo no fim.

**Situação: PRONTO PARA CONFERIR** (começada em 27/10/2026; uma pausa pedida pela gerente no meio; terminada no mesmo
dia). Ramo enviado ao GitHub.

## Em uma frase

Agora o Kaique pega a página e a arrasta ou aumenta "como no Photoshop", numa ferramenta própria (botão da trilha, menu
Ferramentas, tecla F), sem escolher tamanho de folha e sem passar pelo Cortar; o que a tela mostra é o que sai no PDF; o
botão "Centralizar" põe o texto no meio; e quando parte do que está impresso passa da beirada, ela aparece em vermelho e
a página ganha aviso, sem o programa diminuir nada sozinho.

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| Pedido da etapa 5 (sessão 1, 26/10, 1-7 e 1-9) | "essa folha eu não precisava endireitar ela, eu precisava conseguir mover ela dentro da area branca e redimensionar." · "mover deveria se poder fazer sem ter que ir em cortar bordas e poder ser feito como é no photoshope, que você arrasta a hora que quiser e aumenta a hora que quiser. a ferramenta de mover não deveria estar vinculada ao corte de bordas, deveriam ser duas coisas independentes" | Ferramenta própria na trilha, sempre ativa; sem folha, a área branca é a própria página; arrastar move, canto aumenta/diminui na proporção; letra e menu Ferramentas; marca "mexida à mão". |
| D-008 (22/09 e 26/10) | "quero conseguir redimensionar o conteudo tambem" · `fr-24`: "Mas se eu quiser redimensionar isso dentro do programa eu vou conseguir né?" | Mover e aumentar sem tamanho de folha → PDF com o conteúdo no lugar e no tamanho novos. |
| Teste do Kaique (26/10, tarefa 5) | "O texto dessa página está deslocado; quero mover ele para o meio da folha e aumentar um pouco." → o mover não chegou ao PDF (15 × 53), "o retângulo não passa da borda da folha e o texto não aumenta", sem "centralizar". | Tela = PDF; aumentar aumenta; botão Centralizar; teste de reversão. |
| D-473 (escolha da gerente sobre D-066: "precisamos que o pdf saia que nem está na tela") | "Tela e PDF saem da mesma conta [...] Tela e PDF diferentes é defeito" | A ferramenta Mover mostra a página pela mesma conta do PDF. |
| D-017 (G10, 05/10: "(b) Avisar e não reduzir - avisar para eu reduzir manualmente, e ter uma opção para passar isso para todas as folhas [...]") | — | Além da beirada: nada cortado escondido, a parte de fora marcada, aviso no "Para revisar"; nada diminuído sozinho. |
| D-303 (12/09) | "precisamos centralizar" | Botão "Centralizar". |
| D-056 `g8-guias` (13/10) + D-025 | "As duas" + "Mas ele vai poder tirar a automatica a hora que ele quiser." · "a Etapa 5 leva as guias à ferramenta Mover" | Linhas de apoio à mão e automáticas, com caixinha, na ferramenta Mover. |
| D-314 (14/10) | "1. Na edição — Cada página ocupa a folha inteira. [...] (Mexer na escala do conteúdo — aumentar/diminuir — também existe aqui dentro, mas na prática só vou me preocupar com isso na hora de imprimir.)" | Sem folha, a página não muda de tamanho; formato e margens de encadernação continuam no "Montar para imprimir". |
| G10 + D-090/D-091 | "ter uma opção para passar isso para todas as folhas" · "usar em todas" com exceções desmarcadas · "'Selecionar todas' e 'Nenhuma'" | "usar em todas..." no Mover. |
| D-016, D-001, D-041/42/48, D-044/51/52, D-481, D-004/D-485/D-009, D-019/D-043, D-068, D-329, D-010, D-020 | (ver o Livro) | Montagem na ordem obrigatória; ferramenta sempre à vista; balão com letra; Propriedades abre sozinho; letra remapeável; marca mexida e vale no PDF; nada por cima da página; ímã desligável; margens iguais na tela; promessas; desfazer. |

## Como cumpri cada uma

| Decisão | O que ficou no programa | Prova (teste) | Print |
|---|---|---|---|
| Pedido da etapa 5 / D-008 / D-001 | Ferramenta "Mover e redimensionar" (cruz de setas), logo depois do Endireitar na trilha e no menu Ferramentas, tecla **F** (D-540). Propriedades: área branca ("A própria página (15,7 × 21,0 cm)" ou a folha escolhida), "tamanho da folha...", "Tamanho do conteúdo" em %, "Centralizar", "voltar como veio", "usar em todas...", aviso vermelho, linhas de apoio. O "Mover conteúdo" saiu do Cortar (D-544). | `test_d008_ferramenta_mover_propria_na_trilha_no_menu_e_na_letra` (prova também que o antigo saiu), `test_d008_sem_tamanho_de_folha_a_area_branca_e_a_propria_pagina`; P-035 | `depois-03-ferramenta-mover.png` × `antes-03-mover-conteudo-cinza-no-cortar.png` |
| D-008 arrastar e aumentar, no PDF | Arrastar em qualquer lugar da página anda ao vivo; passa da beirada (o meio fica dentro); o canto aumenta na proporção, em volta do meio, até 4×. Cada arrasto = uma ação do desfazer, com a marca MOVER. | `test_d008_arrastar_com_o_mouse_sai_no_pdf_no_mesmo_lugar_da_tela` (impresso no PDF = o da tela até 1%), `test_d008_puxar_o_canto_aumenta_o_texto_no_pdf` (largura do texto no PDF × escala, até 2%) | `depois-04-arrastada.png`, `depois-05-aumentada-pelo-canto.png` |
| Teste do Kaique (reversão) | Folha do tamanho do corte + arrastar → chega ao PDF. | `test_kaique_folha_do_tamanho_do_corte_arrastar_chega_ao_pdf`; no código antigo, pelo caminho antigo (Cortar > "Mover conteúdo"), o PDF não muda e o deslocamento fica (0, 0) — `reversao-no-codigo-antigo.txt` | `depois-02` (a página 7 de verdade) |
| D-303 / D-542 Centralizar | Põe o **impresso** (não a moldura da página) no meio, nas duas direções. O impresso: tinta, sem poeira, sem peças coladas na beirada; só blocos com ≥2% do impresso (sai a marca-d'água do site). | `test_d303_centralizar_poe_o_impresso_no_meio_no_pdf` (margens iguais até 1%); P-191. Janela de verdade, "La vida eterna" p. 7 a 104%: no PDF o bloco do texto fica 0,181 × 0,184 (esq. × dir.) e 0,129 × 0,127 (cima × baixo) | `depois-07-centralizada.png`, `depois-08-tela-e-pagina-do-pdf.png`, `depois-09-pagina-7-do-pdf.png` |
| D-473 | A ferramenta Mover desenha a área branca e a página no retângulo de `core.folha.retangulo_na_folha`, com a área de `core.folha.area_branca_que_vale` (a mesma regra de `compor_na_folha`) e as margens iguais quando ligadas. O resto das telas é da etapa 10 (D-546). | os testes acima medem o PDF contra o retângulo da tela; `tests/test_previa_composta.py::test_retangulo_do_conteudo_bate_com_conteudo_como_retangulo` | `depois-08` (tela e PDF lado a lado) |
| D-017 / D-543 | Aviso "Parte do impresso fica de fora" (botões "ver no Mover" e "está bom assim") quando ≥0,05% do impresso sai; a parte de fora apagada, puxada para o vermelho e listrada; frase vermelha no painel. A mesma conta na tela, na conferência por trás e no PDF. Nada diminuído. | `test_d017_aumentar_alem_da_beirada_avisa_e_marca_a_parte_de_fora` (mede os pontos vermelhos pintados fora da área branca), `test_d017_so_o_papel_da_margem_saindo_nao_avisa`, `test_d017_o_pdf_tambem_poe_o_aviso`; P-194 | `depois-06-alem-da-beirada-aviso.png` |
| D-056 / D-025 | Linhas de apoio no Mover, também sem folha (antes, sem folha, nada acontecia); o ímã gruda pelo impresso; caixinha das automáticas. | `test_d056_linhas_de_apoio_na_ferramenta_mover_sem_tamanho_de_folha`; `tests/test_corte_pelo_conteudo_na_tela.py` (as do livro) | `depois-03` (caixinha no painel) |
| G10 + D-090/D-091 / D-545 | "usar em todas..." → janela "Em quais páginas?" com as já mexidas desmarcadas; uma ação; conferência por trás (QThread) põe o aviso nas que passaram da beirada. | `test_g10_usar_em_todas_nas_escolhidas_e_avisa_por_tras`; P-193 | — |
| D-314 | Sem folha a página do PDF fica do mesmo tamanho (o conteúdo anda dentro dela). | `test_d008_arrastar_...` (mesma forma da página no PDF), `test_d017_aumentar_...` | — |
| D-004/D-009/D-485 | Toda mudança passa pelo `_registrar` (marca MOVER) e vale com tudo desligado. | `test_d008_arrastar_...`, `test_d303_...` | — |
| D-020 | Arrastar, %, Centralizar, voltar, usar em todas: cada um uma ação; Ctrl+Z volta. | `test_d008_arrastar_...` (desfazer), `tests/test_previa_composta.py::test_mover_conteudo_e_uma_acao_do_historico_desfazivel` | — |
| D-481 / D-540 | F, remapeável (`ferramenta_mover`). Achado e consertado: com o foco na página de marcar, **qualquer letra** dava "Aconteceu um problema inesperado" (`editor_selecao` chamava `evento.matches(Qt.Key_Z)`, que o PySide6 6.11 recusa). | `test_letra_f_com_o_foco_na_pagina_de_marcar_chega_a_ferramenta` (reversão: no código antigo dá o TypeError) | conferência "tecla F (com o foco na página)" do roteiro |
| D-010 | Promessas P-035 e P-190 a P-194 com prova. | `tests/test_promessas.py` | — |

## Causas (por que não funcionava)

1. **O mover não chegava ao PDF no teste do Kaique:** o retângulo do conteúdo ficava preso inteiro dentro da folha
   (`Visualizador._mover_conteudo`: `x = min(max(0, x0+dx), 1-w)`); com a folha do tamanho do corte, `1-w ≈ 0`, o
   conteúdo não andava e o deslocamento gravado ficava (0, 0). A prévia composta das Bordas também chamava
   `compor_na_folha` sem a marca de mexido: com a folha 1 ponto menor que o conteúdo, desistia e mostrava a página sem
   folha nenhuma.
2. **"O texto não aumenta":** o canto parava quando o conteúdo encostava na folha (`fator_max_x/y`).
3. **Preso às Bordas:** a caixinha morava no Cortar e ficava cinza sem tamanho de folha (`_mover_conteudo` da tela
   saía se `tamanho_folha_cm is None`).
4. **Sem "centralizar":** não havia botão, e centralizar o retângulo da página não centraliza o texto (as margens da
   página são diferentes dos dois lados).
5. **Letra com o foco na página** (achado nos prints): `evento.matches(Qt.Key_Z)` no `editor_selecao.keyPressEvent`.

## O que mudou (por arquivo)

- `core/folha.py`: área branca em pontos (`tamanho_da_folha_px`, `area_branca_que_vale`), retângulo ⇄ escala e
  deslocamento em pontos, a máscara e a caixa do impresso, `deslocamento_para_centralizar`, `parte_impressa_de_fora`.
- `core/analise.py`: aviso `IMPRESSO_DE_FORA`. `core/pipeline.py`: `anotar_o_impresso_de_fora` no PDF (só mede quando o
  conteúdo passa da área branca). `core/guias.py`: o ímã deixa o conteúdo maior que a folha grudar no meio.
  `core/etapas.py`: `conteudo_fora_do_padrao`.
- `ui/widgets/visualizador.py`: o modo Mover (mundo, área branca, página ao vivo, parte de fora marcada), arrastar e
  canto sem prender na folha, ímã pelo impresso.
- `ui/widgets/trilha_agrupada.py`: a ferramenta, o ícone, a letra F. `ui/tela_conferir.py`: `_montar_aba_mover` e as
  ações; as Bordas sem o "Mover conteúdo"; mover não manda desenhar a página de novo (`CAMPOS_SO_DO_MOVER`); "ver no
  Mover". `ui/tarefas.py`: `TarefaConferirOImpressoDeFora`. `ui/dialogo_escolher_paginas.py`: a regra da exceção vem
  de quem chama. `ui/widgets/editor_selecao.py`: o conserto da letra.
- Testes: `tests/test_decisoes_mover.py` (novo, 13); reescritos para provar que o antigo saiu:
  `tests/test_visualizador.py` (3), `tests/test_previa_composta.py` (7, agora na ferramenta Mover),
  `tests/test_paineis_na_tela.py` (1), `tests/test_decisoes_tela.py` (a lista das ferramentas); promessas.
- `docs/plano/DECISOES.md`: D-540 a D-546; situação de D-008, D-017, D-303.

## Testes

- **No PC, um arquivo por vez (TEMP e `--basetemp` em `_tmp/`), todos passam:** test_decisoes_mover 13 ·
  test_decisoes 23 · _automatico 24 · _dividir 19 · _impressao 22 · _nucleo 36 · _tela 35 · test_trabalho_nao_se_perde
  82 · test_visualizador 70 · test_previa_composta 10 · test_paineis_na_tela 22 · test_corte_pelo_conteudo_na_tela 13 ·
  test_guias 14 · test_folha 20 · test_trilha_agrupada 19 · test_trilha_e_opcoes 29 · test_pipeline_folha 7 ·
  test_core 62 · test_substituir_e_cancelar 21 · test_dialogo_tamanho_da_folha 5 · test_menu_paineis 3 · test_paineis 34 ·
  test_editor_selecao 17.
- **Promessas** (`-k "mover or conteudo or centralizar or p035 or p19 or p065 or p066 or promessa"`): 245 passaram,
  7 xfail; falharam só P-085 e P-127 (defeitos já conhecidos da base, D-492 e defeito C) e P-094 (passa sozinha; também
  falhava na rodada da base 40537146001). Depois: P-035, P-190 a P-194 e as três de inventário passam (10).
- **teste_botoes.py:** 331 ações, 0 falhas (passa pelo Mover: "tamanho da folha...", "Centralizar", "voltar como
  veio", "usar em todas...", menu "usar_mover").
- **Reversão** no código antigo (`7fb3e4a`, cópia em `_tmp/antigo`): os 13 de `test_decisoes_mover.py` e os 3
  reescritos do visualizador falham; o caso do Kaique pelo caminho antigo "NAO ANDOU"; o da letra dá o TypeError
  (`relatorios/obra-etapa5/reversao-no-codigo-antigo.txt`). Ressalva honesta: parte dos 13 falha porque a ferramenta
  não existe no antigo; as medidas que pegam o defeito de verdade são o roteiro `scripts/kaique_antigo.py`, os 3 do
  visualizador e o da letra.

## Somas "Desligado de fábrica"

**96 de 96 iguais** (32 páginas do gabarito × Original, Preto e branco, Melhorar; livro novo; `processar`):
`somas-antes-7fb3e4a.json` × `somas-depois.json` (`scripts/somas.sh`, `scripts/rodada_processar.py`). Nenhuma muda: sem
página mexida, `parte_impressa_de_fora` sai sem medir e `compor_na_folha` não muda.

## GitHub

- **40559025254** (commit `709abac`): partes 2 a 5 e "Botões e prints da janela real" passam; parte 1 com 2 falhas, as
  mesmas da base: P-085 e P-127.
- **40583163203** (commit `88e04f8`, a final, com a caixa do impresso por blocos): partes 2, 3 e 5 e "Botões e prints
  da janela real" passam; parte 1 com as mesmas 2 da base (P-085, P-127); parte 4 com
  `tests/test_paginas_diferentes.py::test_na_analise_a_pagina_torta_ganha_o_aviso`, que **falha às vezes também no
  código antigo**: no PC, 1 de 3 vezes no novo e 3 de 6 vezes no antigo (`7fb3e4a`), sem nada desta etapa no caminho
  dela (é a análise do livro). Troca para a gerente (teste instável, Lista de bugs).

## Prints da janela de verdade (1600×821, fora da tela; `relatorios/obra-etapa5/prints/`)

Roteiro `relatorios/obra-etapa5/roteiro/prints.py`, caminho do Kaique do zero, nada pré-marcado: "La vida eterna"
(cópia) → Automático só "Dividir" (clique) → página 7 (a do teste do Kaique) → botão da trilha → tecla F com o foco na
página → arrastar → puxar o canto → 125% → 104% e "Centralizar" → PDF.
- **Depois (10 de 10):** `depois-00` livros · `-01` aberto · `-02` página 7 com o texto deslocado · `-03` a ferramenta
  · `-04` arrastada · `-05` aumentada pelo canto · `-06` 125%, aviso e a parte de fora em vermelho · `-07` centralizada
  · `-08` a tela e a página do PDF lado a lado · `-09` a página 7 do PDF.
- **Antes (código `7fb3e4a`, 5 de 5):** `antes-00` a `-02`, e `antes-03-mover-conteudo-cinza-no-cortar.png` (a tecla F
  não faz nada; "Mover conteúdo" cinza, "(só depois de escolher um tamanho de folha)").
- Abri e olhei todos. Visto nos prints e consertado: a frase do aviso não cabia na faixa (encurtada); "Centralizar"
  puxado pela marca-d'água do site e pelos restos escuros da beirada (caixa do impresso por blocos, sem peças coladas
  na beirada).

## Escolhas da gerente (D-014) feitas aqui — no Livro como D-540 a D-546

| Nº | Escolha |
|---|---|
| D-540 | Letra F. |
| D-541 | Como mexe: passa da beirada (meio dentro), canto proporcional em volta do meio, 5% a 4×, %, vista que mostra tudo e fica parada no arrasto. |
| D-542 | "Centralizar" e ímã pelo impresso (blocos ≥2%, sem peças coladas na beirada). |
| D-543 | O aviso do D-017: limiar 0,05%, três lugares, vermelho, "ver no Mover"/"está bom assim". |
| D-544 | "Mover conteúdo" sai do Cortar; "tamanho..." fica no Cortar e também no Mover. |
| D-545 | "usar em todas..." no Mover. |
| D-546 | Só o Mover mostra a página na área branca (o resto da D-473 é da etapa 10); folha menor ainda não mexida aparece como sai. |

## Ressalvas

1. **As outras ferramentas mostram a página sem o mover** (D-546): na Marcar, Endireitar, Cortar e Filtro a página
   aparece como antes de mover (lá se marca e se corta sobre a página). Pode confundir ("mexi e voltou?"). É da etapa
   10 (D-473).
2. **Com o foco na lista do Automático, as letras vão para a lista** (D, X, I, F — de todas as ferramentas, não só da
   nova). Um clique na página devolve as letras.
3. **A letra que já vinha cortada na beirada da página não conta** para o aviso nem para o "Centralizar" (as peças
   coladas na beirada saem da conta, para o fundo do scanner e a marca-d'água não enganarem).
4. **Página real com cabeçalho na beirada** ("La vida eterna" p. 7): qualquer mover para cima tira um pedaço do
   cabeçalho e dá o aviso (é o que a D-017 pede, mas vai aparecer bastante em livro escaneado com o corte justo).
5. **O "Centralizar" junta letras próximas em blocos e deixa de fora bloco com menos de 2% do impresso**: um número de
   página sozinho longe do texto também fica de fora da conta (a página fica centrada pelo texto).
6. **"tamanho..." em dois lugares** (Cortar e Mover), a mesma janela.
7. **Velocidade:** não medi (a medida é a do filtro do GitHub, pela gerente). O caminho de sempre não ganha conta: sem
   mover, `parte_impressa_de_fora` volta sem medir; com mover, uns 45 ms por página a 300 DPI.
8. **Conferência por trás do "usar em todas"** usa a página sem filtro, a 75 DPI: o aviso dela pode diferir do PDF num
   caso de borda (o PDF refaz a conta e acerta).

## Perguntas para o Samuel (com recomendação; nenhuma trava a etapa)

1. **As outras telas devem mostrar a página já movida?** Hoje só a ferramenta Mover mostra (D-546). *Recomendo levar à
   etapa 10, junto da D-473 (tela = PDF), porque na Marcar a marcação é feita sobre a página e mudar isso mexe no
   editor de marcar.*
2. **Página com cabeçalho colado na beirada:** quer que o aviso do D-017 ignore o que já estava a menos de ~2 mm da
   beirada? *Recomendo não: a D-017 diz "nada é cortado sem a pessoa ver", e o "está bom assim" resolve em um clique.*

## Trocas que outra área precisa

- **Etapa 10 (D-473):** mostrar a página movida também nas outras ferramentas e nas miniaturas.
- **Etapa 7 (avisos):** novo aviso `impresso_de_fora` (pode entrar na lista de avisos do livro, D-521, se muitas
  páginas o tiverem depois de "usar em todas").
- **Etapa 9b (promessas):** P-094 depende da ordem dos testes (passa sozinha).
- **Gerente:** o atalho F e o conserto da letra no `editor_selecao` mexem em `ui/widgets/editor_selecao.py` (uma linha).

## Commits (ramo `obra-etapa5-2026-10-26`)

- `9e5a83d` ONDE-PAREI com as decisões
- `de69f29` ferramenta Mover e redimensionar própria (núcleo e tela)
- `1fc55f6` provas, testes antigos reescritos, promessas, Livro D-540 a D-546
- `709abac` P-191 começa com o conteúdo fora do meio
- (letra com o foco na página; reversão; somas; roteiro) · `efa2b99` pausa · `88e04f8` prints e o PDF medido pelo
  bloco do texto · (este ONDE-PAREI final)
