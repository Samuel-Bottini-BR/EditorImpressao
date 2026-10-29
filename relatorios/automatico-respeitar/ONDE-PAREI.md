# D-583/D-586: caixinha "Respeitar as gravuras achadas" no painel do Filtro — onde parei

Ramo `automatico-respeitar-gravuras-2026-10-29` (saiu de `obra-2026-10-26`, commit `2db002e`), worktree
`.claude/worktrees/auto-respeitar`. Agente construtor, 29/10/2026. Sem push, sem juntar.

## Decisões que esta tarefa precisa cumprir (escrito antes de mexer)

Conferidas no `docs/plano/DECISOES.md` desta worktree.

**A que se constrói:**

- **D-583** (29/10/2026): "Precisamos da opção de jogar o filtro em cima de outro filtro ou só substituir o filtro que
  está colocado em cima." · depois da investigação (o que fica "por cima" é a marcação do Automático): "c" — "C — As
  duas, com uma escolha no painel do Filtro. Por exemplo, uma caixinha que diz se o filtro respeita ou não as gravuras
  achadas."
- **D-586** (29/10/2026, "A"): "A — Uma caixinha no painel "Filtro da página", logo abaixo das figurinhas dos filtros:
  "Respeitar as gravuras achadas". De início vem ligada, que é como funciona hoje. Desligada, o filtro vale na página
  inteira: no Preto e branco, a capa sairia toda em preto e branco, como na fileira de baixo da primeira imagem que te
  mostrei. Vale com o "Aplicar em: só nesta / todas / daqui em diante" que já existe no painel."

- **D-587** (29/10/2026, resposta à pergunta 1 desta tarefa; "sim" a: "enquanto a "Só as letras" estiver marcada, a
  caixinha nova fica cinza e não dá para clicar. É assim que já funciona com a caixinha das molduras. Está bom
  assim?") — a opção C, do jeito da D-168.

**As que não podem quebrar:**

- **D-148** (30/09 e 05/10): "(a) Uma caixinha 'Só as letras' dentro do Preto e branco, para o livro [...] e para a
  página (aba Filtro) (recomendado)" — marcada, só as letras viram preto e branco; gravura, foto, moldura e iluminura
  ficam como no original.
- **D-168** (05/10): "(a) Fica apagada (cinza) enquanto 'Só as letras' estiver marcada, e volta como estava ao desligar
  (recomendado)".
- **D-144** (30/09): "Mantém a cor original (como o ANTES); traço preto só se eu escolher" · 01/10: "Sim, mantém a cor"
  — com a caixinha nova LIGADA, moldura e iluminura continuam com a cor no Preto e branco.
- **D-127** (28/09): "Iluminura sai intacta: cores, figuras, fundos e dourados como no original." · **D-128**: "a borda
  dourada deveria sair sem alteração" — idem, com a caixinha ligada.
- **D-126** (28/09): "Gravura e letras intactas, e todo o papel totalmente branco, inclusive o papel dentro da gravura"
  — idem, com a caixinha ligada.
- **D-199** (06/08 e 01/10): "quero ter opção de colocar o filtro só em um lugar, por exemplo colocar só na iluminura ou
  só no texto" e **D-224** (01/10): "espero ter a escolha de conseguir deixar a foto em original, caso precise." — os
  pedaços feitos À MÃO ("Só neste pedaço") continuam valendo com a caixinha desligada.
- **D-020** (18/07): "Ctrl+Z desfaz qualquer alteração, sem limite de quantidade, e Ctrl+Shift+Z refaz".
- **D-066** (23/10): "precisamos que o pdf saia que nem está na tela" e **D-473** (26/10): "Tela e PDF saem da mesma
  conta."
- **D-010** (26/10): "eu acho que o botão tem que ser provado que ele faz o que se diz que se faz, e não só se ele muda
  algo na tela." — promessa em `tests/promessas/promessas.md`, prova em `tests/test_promessas.py`.
- **D-090** (08/10) e **D-545** (27/10): "usar em todas" nunca apaga exceção.
- **D-585** (29/10): "deixar como está e deixar anotado" — a classificação pintura × enfeite NÃO se mexe aqui.
- **CLAUDE.md §6**: mudar o formato do projeto precisa de autorização → dada por esta decisão (D-586: "campo por
  página"); documentado abaixo. **§4.7** (reversão), **§4.10** (caminho inteiro; cada foto diz por onde passou), **§11
  regra 7** (só o que ele mandou: nenhum atalho, menu, aviso ou texto além do nome e do balão).
- **Fora do escopo (não consertar):** as figurinhas do painel não usam a marcação (Lista de bugs, 29/10).

## O que mudou

Em português simples: no painel "Filtro da página", logo abaixo das figurinhas dos filtros, apareceu a caixinha
**"Respeitar as gravuras achadas"**, ligada em toda página. Ligada, nada muda. Desligada, o filtro da página (Preto e
branco, Melhorar, Mágico pro) trata a página como se a máquina não tivesse achado gravura, letra, papel nem enfeite:
na capa do *Na escola de Jesus*, em Preto e branco, a pintura sai toda em preto e branco (prints 2 e 4). O que foi
marcado à mão (inclusive o "Só neste pedaço") continua valendo.

Arquivos:
- `modelos.py` — campo novo da página `respeitar_gravuras_achadas` (padrão ligado). **Mudança de formato do
  `projeto.json`** (autorizada pela D-586, "campo por página"): cada página ganha a chave
  `"respeitar_gravuras_achadas": true`. Projeto gravado antes não tem a chave e abre com ela ligada (campo que falta
  ganha o padrão); o programa de antes, se abrir um projeto novo, descarta a chave e respeita as gravuras.
- `core/pipeline.py` — `marcacao_que_o_filtro_usa` (e `respeita_as_gravuras_achadas`), chamada em
  `_filtrar_com_a_marcacao`, logo depois de achar a marcação. É o único lugar da conta: a prévia da tela, o "antes /
  depois", a tela cheia e o PDF passam todos por ali (D-066/D-473). Ligada, devolve o mesmo objeto (nenhuma conta a
  mais). Desligada, só as áreas de origem "mão". A marcação guardada na página não muda (religar devolve a mesma
  imagem, byte a byte).
- `ui/tela_conferir.py` — a caixinha (estilo das outras caixinhas do painel, balão de uma frase), a ação do
  desfazer (`_mudar_respeitar_gravuras`), mostrar o valor da página ao trocar de página (`_mostrar_respeitar_gravuras`,
  em todo filtro), o campo no "Aplicar em" (`_filtro_em_todas`, `_filtro_nas_proximas`) e na marca "mexida à mão"
  (`MARCAS_DA_PAGINA`, como as outras caixinhas do Filtro).
- `ui/widgets/paineis.py` — o painel põe a caixinha logo abaixo da fila das figurinhas.
- `ui/tarefas.py` — a chave da prévia ganha `:sem_as_achadas` só com a caixinha desligada (ligada, a chave é a de
  sempre).
- `tests/test_decisoes_respeitar_gravuras.py` (16 provas), `tests/promessas/promessas.md` (P-086) e
  `tests/test_promessas.py` (`test_p086_respeitar_as_gravuras_achadas`).
- Nada mais: nenhum atalho, menu, aviso ou texto além do nome, do balão e da frase do Histórico ("Respeitar as
  gravuras achadas na página N: ligada/desligada", como as outras caixinhas fazem).

## Como cumpri cada uma

| Decisão | Como (prova) |
|---|---|
| D-583 / D-586 — caixinha logo abaixo das figurinhas, ligada de fábrica | `test_d586_ligada_guarda_a_cor_desligada_toda_em_preto_e_branco_religada_igual` (a caixinha é o item seguinte à fila no painel, ligada); prints 1 a 4 |
| D-586 — ligada = como hoje | mesma prova (iluminura colorida, >50% de pontos com cor); `test_d586_ligada_e_a_conta_de_antes_byte_a_byte` (4 filtros); entre commits: `identica-ao-2db002e.txt` (capa e páginas 9, 19, 45 do *Na escola de Jesus*, 4 filtros: os 16 desenhos iguais, md5) |
| D-586 — desligada, Preto e branco: página toda em preto e branco | prova 1 (0 pontos com cor, na tela e no desenho); `test_d586_o_pdf_sai_como_a_tela`; print 2 e 4 |
| D-586 — desligada, Melhorar/Mágico pro | `test_d586_melhorar_e_magico_pro_desligada_e_a_pagina_sem_a_marcacao` (igual, byte a byte, à página sem marcação) |
| "No Original não muda nada" | `test_d586_no_original_nada_muda` (byte a byte) |
| D-586 — "Vale com o Aplicar em" + D-090/D-545 | `test_d586_aplicar_em_leva_a_caixinha_sem_apagar_excecao` ("todas" e "daqui em diante"; o pedaço à mão da página 3 fica e continua valendo) |
| D-020 — Ctrl+Z / Ctrl+Shift+Z | `test_d586_ctrl_z_desfaz_e_ctrl_shift_z_refaz` (teclas de verdade; a caixinha acompanha) e o desfazer na P-086 |
| D-066 / D-473 — tela = PDF | prova 1 (tela = desenho), `test_d586_antes_depois_e_tela_cheia_seguem_a_caixinha`, `test_d586_o_pdf_sai_como_a_tela` (PDF gerado = desenho do tamanho do PDF) |
| D-199 / D-224 — pedaço à mão continua | `test_d586_o_pedaco_a_mao_continua_valendo_com_a_caixinha_desligada` |
| D-148 / D-168 — "Só as letras" | com "Só as letras" ligado a caixinha não muda nada (`test_d586_com_so_as_letras_a_caixinha_nao_muda_a_pagina`); `tests/test_decisoes_so_as_letras.py` verde |
| D-587 — caixinha cinza com "Só as letras" | `test_d587_com_so_as_letras_na_pagina_a_caixinha_fica_cinza_e_volta` (ligada e desligada antes; clique não muda nada; volta com o valor) e `test_d587_so_as_letras_herdado_do_livro_tambem_deixa_cinza`; falham no `ae0dc8c` (`reversao-no-2db002e.txt`); print 5 |
| D-144 / D-127 / D-128 / D-126 | intocadas com a caixinha ligada (provas byte a byte acima; `test_decoracao_no_preto_e_branco.py`, `test_filtro_com_selecao.py` verdes) |
| D-585 | não mexi na classificação pintura × enfeite |
| D-010 | promessa P-086 (fora da varredura: a varredura ainda não olha caixinhas) + prova `test_p086_*` (clica, confere projeto, PDF e desfazer) |
| §4.7 reversão | as 16 provas falham no `2db002e` (`reversao-no-2db002e.txt`) e passam aqui |
| §4.10 | provas com o Automático de fábrica (Endireitar, Cortar, Limpar a folha); prints da capa do livro dele pelo caminho inteiro (endireitada, cortada, "Limpar a folha", "Gravuras e fotos", Preto e branco, "Só as letras" desligado) |
| §11 regra 7 | nada além do nome e do balão |
| Fora do escopo | figurinhas do painel × marcação: não mexi |

## Prints (offscreen, 1280 × 657, ~140 KB cada)

Capa do *Na escola de Jesus* (cópia do projeto de teste em `_tmp`), depois do Automático do livro dele (endireitada,
cortada, "Limpar a folha", "Gravuras e fotos"), Preto e branco, "Só as letras" desligado, ferramenta Zoom:
- `1-uma-pagina-ligada.jpg` — caixinha ligada: a pintura com a cor (como hoje);
- `2-uma-pagina-desligada.jpg` — desligada: a capa toda em preto e branco;
- `3-antes-depois-ligada.jpg` — "antes / depois", ligada;
- `4-antes-depois-desligada.jpg` — "antes / depois", desligada.
- `5-so-as-letras-caixinha-cinza.jpg` — D-587: "Só as letras" ligado na página; a caixinha fica cinza (marcada, como
  estava) e a pintura com a cor.
Refazer: `fazer_prints.py` (instruções no topo).

## Velocidade (mexi em `core/`)

`velocidade.txt`: `teste_velocidade.py --rapido` alternado 3 vezes (antes = `2db002e`, depois = este ramo) e o
desenho da prévia de 4 páginas do livro dele alternado 2 vezes. **Não ficou mais lento**: as diferenças entre antes
e depois ficam dentro do vai-e-vem entre rodadas do mesmo código. Ressalva: o `--rapido` não vale como medição
oficial e o PC estava em uso; a conta nova é uma leitura de campo por página.

## Testes (um arquivo por vez, offscreen, `--basetemp` e TEMP em `_tmp`)

- `tests/test_decisoes_respeitar_gravuras.py`: **16 passed** (no `2db002e`: **16 failed**)
- `tests/test_promessas.py -k "p086 or todo_botao or toda_promessa or p081 or p080"`: **19 passed**
- `test_decisoes_filtro_automatico` 4 passed · `test_decisoes_so_as_letras` 5 passed · `test_decisoes_nucleo` 38
  passed · `test_decisoes_tela` 35 passed · `test_decisoes_9b2` 30 passed
- painel e cartões: `test_paineis` 34 · `test_paineis_na_tela` 22 · `test_cartoes_e_previas` 2 ·
  `test_cartoes_seguem_as_caixinhas` 5 · `test_filtros_tela_cheia` 11 · `test_misto_na_tela` 14 (todos passed)
- formato do projeto: `test_modelos` 4 · `test_projetos` 24 · `test_misto_no_projeto` 12 · `test_claro_no_escuro` 8 ·
  `test_historico_depois_de_reabrir` 11 (todos passed)
- caminho do filtro com a marcação: `test_filtro_com_selecao` 22 · `test_so_neste_pedaco_no_preto_e_branco` 8 ·
  `test_so_neste_pedaco_no_original` 22 · `test_decoracao_no_preto_e_branco` 12 · `test_garantir_selecao_corrida` 2
  (todos passed)
- **D-587 (rodada de novo depois):** `test_decisoes_respeitar_gravuras` 19 passed · `test_decisoes_so_as_letras` 5 ·
  `test_misto_na_tela` 14 · `test_paineis_na_tela` 22 · `test_promessas -k "p086 or todo_botao"` 2 passed
- Não rodei a suíte inteira nem o `teste_botoes.py` (regra do PC); falta a rodada do GitHub (não fiz push, como
  pedido).

## Ressalvas

- **Com "Só as letras" valendo (Preto e branco, na página ou herdado do livro), a caixinha fica cinza e não dá para
  clicar (D-587)**, como a das molduras (D-168); o valor guardado não muda e volta ao desligar "Só as letras". A conta
  também ignora a caixinha nesse caso (o "Só as letras" manda). Em Melhorar e Mágico pro o "Só as letras" não vale,
  então ela fica clicável.
- **No Original a caixinha também não muda nada** (pedido da gerente: "No Original não muda nada"); ela continua à
  vista, como a D-586 descreve (não a escondi: seria comportamento novo).
- **Desligada e sem pedaço à mão, a página passa pelo filtro "sem marcação"**, e nesse caminho o programa de hoje
  não usa o "jeito do preto e branco" de "Mais ajustes" (já anotado no código, `core/filtros.aplicar_filtro_com_
  selecao`: "O algoritmo continua de fora, como estava (ver o relatorio da ligacao do limpar pontinhos, Lista de
  bugs)"). É o mesmo que acontece hoje em qualquer página sem marcação; não mexi.
- **A deteccão continua rodando** com a caixinha desligada (a marcação fica guardada para religar dar a mesma
  imagem). Não fica mais rápido desligando.
- **Achado à parte, não consertado (existe igual no `2db002e`):** o primeiro desenho de uma página no Original logo
  depois do Automático sai um pouco diferente dos seguintes (no livro de teste, 38% dos pontos, até 19 tons em 255;
  no *Na escola de Jesus*, páginas 1, 9, 19 e 45 no Original: md5 da primeira vez ≠ da segunda, nos dois commits —
  `identica-ao-2db002e.txt`). Nos outros filtros não acontece. Parece a medida da página (geometria) guardada no
  primeiro desenho. Nas provas, desenho cada página uma vez antes de comparar. Para a Lista de bugs, se a gerente
  achar que vale (29/10/2026).
- As provas usam um livro sintético com a marcação posta direto (sem o detector, lento e sem o modelo nas worktrees);
  o caso real foi conferido nos prints e no `identica-ao-2db002e.txt`.
- Velocidade só com `--rapido` e o desenho da prévia, no PC em uso: não é a medida oficial (GitHub/fim de fase).
- Nos prints, a figurinha "Preto e branco" acompanha a página (colorida com a caixinha ligada, em preto e branco
  desligada) porque é a página da vez nesse filtro; as outras figurinhas continuam sem a marcação (o achado
  conhecido de 29/10, fora do escopo).

## Perguntas para o Samuel

1. ~~"Só as letras" + caixinha desligada~~ — **respondida: D-587 (opção C), construída** (ver abaixo).
2. **(Ainda não feita a ele.) No Original a caixinha também não faz nada.** Quer que ela fique apagada (cinza) no Original, ou à vista como
   está? (Hoje: à vista, como a D-586 descreve.)
