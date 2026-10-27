# Obra de 26/10/2026 — etapa 7 ("está certo" com resposta e os avisos): ONDE PAREI

Ramo `obra-etapa7-2026-10-26` (base `obra-2026-10-26` = `7859b97`, com as etapas 1-6, 9a, 9c, 10a, 10b), worktree
`.claude/worktrees/obra-etapa7`. Agente: layout. Regra 7 (Samuel, 27/10/2026): "é só para fazer o que eu já tinha
mandado, fazer as ferramentas que colocamos no programa funcionem como deveriam e como eu tinha escolhido."

**Situação: PRONTO PARA CONFERIR** (começada e terminada em 27/10/2026). Ramo enviado ao GitHub.

## Em uma frase

Agora o "está certo" responde: a página (ou, no Dividir, a folha) fica conferida, a miniatura ganha um tique verde, o
contador de conferidas sobe e a tela vai para a próxima dúvida; o cartão da página no "Para revisar" tem os mesmos
botões do aviso; os avisos de folha ("Lombada incerta", "Qualidade baixa") deixaram de ficar escondidos e o número de
dúvidas é um só em todo lugar (no "La vida eterna", 15 no rodapé, no painel, na "Antes de processar", na janela de
salvar, na grade e no livro aberto — antes 9, 17, 359 e 0); "ver as N em tela cheia" abre só as páginas com dúvida;
os avisos do livro inteiro aparecem numa linha no alto do "Para revisar" e no livro aberto.

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| Plano de 26/10, etapa 7 (aprovado: "então vamos, fazer um plano para ajeitar isso.") | "'está certo' com resposta + avisos baratos: tique, contador certo, próxima dúvida (1.1); botões no cartão do aviso (1.8); um número só de dúvidas (5.5)" | O "está certo" responde; o cartão tem botões; um número só. |
| D-010 / P-101 (26/10) | "eu acho que o botão tem que ser provado que ele faz o que se diz que se faz" — o exemplo: "a folha fica conferida, tique na miniatura, contador sobe, vai para a próxima dúvida" | "está certo": conferida, tique, contador sobe, próxima dúvida. |
| Sessão 1, 1-5 (26/10) | "eu clico no esta certo e não acontece nada." | (o mesmo) |
| Sessão 0, 0-7 e 0-8 (23/10) | "tem os avisos mas não tem como apertar para fazer ele sumir ou alguma sugestão de como se livrar dele." | Botões no cartão; no Dividir, o aviso da página tem como ser resolvido. |
| D-268 (07-08/10) | `rv4-conserto-desenho`: "(a) Botão no aviso" | O conserto rápido é botão no próprio aviso. |
| D-255 (27/07) | Kaique: "Colocar botão clicavel nas paginas que o programa não tem certeza" | Página com dúvida clicável no "Para revisar", com botão de conserto. |
| D-282 (21/10) | `pr`: "Aprovado" | Página com aviso → cartão com o motivo e os botões. |
| D-259 (05/10) / P-095 | "Opção 1 (faixa fina). Mais: abrir todas as páginas em tela cheia (como no UPDF) mostrando as que precisam de atenção." · Rodada 2: "Aprovado" | Faixa com aviso, "está certo", "próxima dúvida"; "ver as N em tela cheia" (no desenho decidido, rodada 13, botão largo no pé do "Para revisar"). |
| D-343 (05/10) | "todas / só as que precisam de atenção" | O "ver as N" abre a grade nesse filtro. |
| D-285 (21/10) | `pr-contagens`: "A janela de salvar passa a contar as páginas com aviso pendente" | Painel, "Antes de processar" e janela de salvar com o mesmo número. |
| Lista única 5.5 e 5.4; teste do Kaique | os três números; "356 páginas que você não conferiu" depois de "nada pendente" | Um número só; avisos de folha à vista. |
| D-284 / D-483 (etapa 3) | `pr-medir-o-livro`: "Medir o livro inteiro por trás, depois de abrir" | Feita na etapa 3; continua. |
| D-500 / D-501 (etapa 4) | (escolhas da gerente) | "Lombada incerta" no "Para revisar"; "ver" em aviso da divisão leva ao Dividir, os outros à página. |
| D-521 (27/10) | Central `pd-avisos-do-livro`: "No alto do painel \"Para revisar\" e no livro aberto da tela inicial (recomendo)" | Avisos do livro inteiro numa linha nos dois lugares. |
| D-543 / D-548 (etapa 5) | apoiada em D-017: "Avisar e não reduzir - avisar para eu reduzir manualmente" | "Parte do impresso fica de fora" no "Para revisar" com "ver no Mover" e "está bom assim". |
| D-522 (27/10) | Central `pd-versos-em-branco`: "Juntar num aviso só do livro quando forem muitas" | Conta da 9d; a tela fica pronta (linha da D-521). |
| D-497 (27/10) | (escolha da gerente) | Conta da 9d; a tela fica pronta para ligar. |
| D-265 / D-266 / D-272 | abas "Por página / Por motivo"; "Sempre 'Por página'"; "está bom" em quatro níveis | Continuam. |
| D-271, D-273, D-288, D-289, D-290 | avisos separados com os dois botões; o aviso some sozinho; título não é "em branco"; dois cliques no cartão do filtro; teclado depois do botão | Continuam. |
| D-254 | "menos de 10% das páginas são marcadas para revisão" | É da etapa 9 (não desta). |
| D-014 | "Use as respostas mais recentes" | Quando duas se contradizem, vale a mais recente. |

## Contradições achadas (vale a mais recente, D-014) — qual venceu

- **D-285 (21/10) × plano de 26/10 / lista única 5.5 ("um número só")**: em 21/10 ele escolheu "A janela de salvar
  passa a contar as páginas com aviso pendente" e não escolheu a opção "O painel passa a listar também os motivos de
  folha". Em 26/10 aprovou o plano com "um número só de dúvidas (5.5)", e o 5.5 diz que "os avisos de folha ficam
  escondidos". **Venceu a mais recente (26/10):** a janela de salvar conta as páginas com aviso pendente (D-285
  cumprida) e o painel mostra também os avisos de folha, nas páginas da folha (uma linha por página, não por folha:
  o painel não fica mais comprido que o número). A D-500 (27/10, "a folha vai para o 'Para revisar' como 'Lombada
  incerta'") aponta para o mesmo lado.
- **Desenho da rodada 2 ("ver as 3 em tela cheia" dentro da faixa) × desenho decidido da rodada 13 (botão largo no pé
  do "Para revisar")**: venceu a rodada 13 (a mais recente), que também é a chave da promessa P-095.

## Como cumpri cada uma

| Decisão | O que ficou no programa | Prova (`tests/test_decisoes_avisos.py`, salvo dito) | Print |
|---|---|---|---|
| 1.1 / D-010 / P-101 / 1-5 | "está certo" (`TelaConferir.esta_certo`): grava a página como conferida (uma ação do desfazer, como antes), a miniatura ganha um tique verde (desenhado em traços, sem símbolo), o rodapé "N de M conferidas" sobe, e a tela vai para a próxima página com dúvida. No Dividir: a folha, o tique na miniatura da folha, o contador em folhas ("1 de 180 conferidas", como o "folha 1 de 180" ao lado) e a próxima folha com dúvida. Sem outra dúvida, fica onde está. A barra de espaço não mudou ("marca e vai para a próxima"). | `test_p101_esta_certo_na_pagina_*`, `test_esta_certo_no_dividir_*`, `test_esta_certo_sem_outra_duvida_*`; P-101 sem "aguarda" (`tests/test_promessas.py`) | `depois-04-esta-certo-1/2/3` × `antes-04-esta-certo-1/2/3` (antes: a mesma página, sem tique, o contador parado) |
| 5.5 / D-285 / Kaique "356" | Uma conta só, `core/avisos.quantas_com_duvida`: as páginas que vão para o PDF com algum aviso pendente, o dela ou o da folha dela. Usada no rodapé, no "Para revisar" (e no ícone), na "Antes de processar", na janela de salvar (D-285: antes contava toda página sem "está certo"), na grade "só as que precisam de atenção" e no livro aberto ("Para revisar: N" e o "Ver todas as páginas"). O aviso de folha aparece na faixa das páginas dela, com o botão; o "está certo" de cada página responde por ele ali; quando as páginas da folha estão todas conferidas, o aviso sai também da "Antes de processar". | `test_5_5_um_numero_so_*` (os sete lugares dão 3), `test_kaique_356_*` ("está bom em tudo" → 0 em todo lugar, a janela de salvar sem aviso), `test_aviso_da_folha_aparece_na_pagina_*`; `tests/test_barra_de_menu.py` (a prova antiga da janela de salvar, reescrita para a D-285) | `depois-05`, `-06`, `-07`, `-08`, `-09`: 15 em todos × `antes-06` (17 páginas), `antes-07` (359 páginas), `antes-04` (9 no painel), `antes-09` ((0)) |
| 1.8 / D-268 / D-255 / D-282 / 0-7 | O cartão da página da vez no "Para revisar" ganha os mesmos botões da faixa (laranja), em filas com o nome inteiro; o clique faz o mesmo que o da faixa. | `test_1_8_cartao_do_aviso_*` ("ver no Mover" leva ao Mover; "está bom assim" tira o aviso) | `depois-03` (página 2: "Deixar em branco", "Tirar do livro", "está bom assim"), `depois-04-esta-certo-1` (página 7: "aceitar o corte") × `antes-03` (cartão sem botões) |
| 0-8 / D-501 | O clique num cartão estando no Dividir sai do Dividir para a página (a ferramenta de marcar, como o Automático faz, D-007) e o aviso aparece com os botões; se o primeiro aviso da página é da divisão ("Lombada incerta"), vai ao Dividir na folha. | `test_0_8_clicar_no_cartao_*`, `test_d501_cartao_com_aviso_da_divisao_vai_ao_dividir` | `depois-03` (o clique no cartão: página 2, fora do Dividir) |
| D-259 / D-343 / P-095 | "ver as N em tela cheia" no pé do "Para revisar" (o desenho da rodada 13); abre a grade "Todas as páginas" já em "só as que precisam de atenção"; o N é o número de todo lugar. | `test_d259_*`; P-095 sem "aguarda", com prova de verdade (clica e confere quais páginas) | `depois-02` (o botão), `depois-05` (a grade com as 15) |
| D-521 | A linha "No livro inteiro: …" no alto do "Para revisar" mostra todos os avisos do livro (antes só a faixa escura; os outros moravam num rótulo escondido); a mesma linha no livro aberto da tela inicial (via `projetos.Resumo.avisos_do_livro`). | `test_d521_*` | — (o "La vida eterna" não tem aviso de livro inteiro; a prova usa dois) |
| D-543 / D-548 | O aviso "Parte do impresso fica de fora" aparece no "Para revisar" e o cartão traz "ver no Mover" e "está bom assim". | `test_1_8_cartao_do_aviso_*` | — |
| D-522 | A linha da D-521 mostra qualquer aviso do livro: quando a conta da 9d (40%, desligada) for ligada, a frase entra ali sem mexer na tela. | (a da D-521) | — |
| D-497 | Depois de dividir, juntar ou mover a linha de uma folha, a tela chama por trás (QThread, `ui/tarefas.TarefaMedirOEmBranco`) a conta da 9d, `core.pipeline.medir_o_em_branco(doc, projeto, pagina)`, nas páginas da folha, e redesenha a faixa, a tira, o contador e o painel. **Enquanto a 9d não estiver na obra, a função não existe e nada acontece.** | `test_d497_*` (com uma conta de mentira no lugar da da 9d) | — |
| D-265, D-266, D-272, D-271, D-273, D-288, D-289, D-290 | Sem mudança. | `test_paineis.py` 34, `test_para_revisar_na_tela.py` 25, `test_avisos.py` 34, `test_revisar.py` 28, `test_reversao_para_revisar.py` 6, `test_em_branco.py` 6 | — |
| D-284 | Sem mudança (etapa 3); os avisos de folha que ela põe agora contam e aparecem. | `test_decisoes_automatico.py` 24 | — |

## Causa (por que não funcionava)

- **"está certo" mudo:** o botão só gravava `revisada` (`_marcar_revisada`); não andava, a miniatura não tinha marca
  de conferida, e no Dividir o rodapé contava páginas enquanto o botão conferia a folha.
- **Três números:** o rodapé e o painel contavam só os avisos de página; a "Antes de processar" juntava os de folha
  (`core/avisos.paginas_com_aviso`); o botão escondido contava folhas e páginas separadas; a janela de salvar contava
  toda página sem "está certo"; a grade só olhava `alertas` sem os aceitos; o livro aberto passava a grade sem motivos.
  Os avisos de folha só apareciam na faixa do Dividir.

## O que mudou (por arquivo)

- `core/avisos.py` (núcleo, o mínimo, avisado): `avisos_da_pagina`, `avisos_da_folha`, `linhas_do_para_revisar`,
  `quantas_com_duvida`, `DA_DIVISAO`; `pendentes_do_livro` deixa de fora o aviso da folha cujas páginas já foram todas
  conferidas; `paginas_com_aviso` conta o aviso da folha só nas páginas dela ainda não conferidas.
- `ui/tela_conferir.py`: `esta_certo`, `_avisos_da_vez`/`_avisos_do_item`/`_itens_com_duvida`, `_ir_do_para_revisar`,
  `abrir_so_as_que_precisam`, `_medir_o_em_branco_por_tras`; a faixa, os botões do aviso, a tira, o rodapé (o nome do
  livro encolhe antes da conta, `_RotuloDoLivro`), o contador e a grade usam a mesma dúvida.
- `ui/widgets/paineis.py`: o "Para revisar" com as linhas de `linhas_do_para_revisar`, os botões no cartão da vez
  (`definir_botoes_da_vez`, sinal `botao_do_aviso`), "ver as N em tela cheia" (sinal `ver_em_tela_cheia`), a linha dos
  avisos do livro (`frase_dos_avisos_do_livro`).
- `ui/widgets/tira_miniaturas.py`: o tique de conferida. `ui/widgets/todas_as_paginas.py`: `ItemDaGrade.duvidas`.
- `ui/janela_confirmar.py`: D-285. `ui/tela_inicio.py`: a linha da D-521 e a grade com as dúvidas.
  `projetos.py`: `Resumo.avisos_do_livro`, `Resumo.duvidas_por_folha`, `para_revisar` = o número de todo lugar.
  `ui/tarefas.py`: `TarefaMedirOEmBranco`.
- Testes: `tests/test_decisoes_avisos.py` (novo, 13), `tests/test_promessas.py` (P-095, P-101),
  `tests/promessas/promessas.md` (P-095 e P-101 sem "aguarda"; as chaves dos botões no cartão em P-103, P-104, P-105),
  `tests/test_paineis_na_tela.py`, `tests/test_tirar_fundo_no_programa.py`, `tests/test_barra_de_menu.py` (o aviso de
  folha agora aparece na página; a janela de salvar segue a D-285).
- `docs/plano/DECISOES.md`: só a coluna de situação de D-255, D-259, D-268, D-284, D-285, D-497, D-521, D-522, D-543.

## Testes (no PC, um arquivo por vez, TEMP e --basetemp em `_tmp/`)

- `tests/test_decisoes_avisos.py`: **13 passaram**. **Reversão** no código antigo (`7859b97`, worktree `_tmp/antigo`):
  **os 13 falham** (`relatorios/obra-etapa7/reversao-no-codigo-antigo.txt`). Ressalva honesta: 5 falham porque a peça
  não existe lá (o tique, os botões do cartão, o "ver as N"); os outros 8 por asserção (os números diferentes, ficou no
  Dividir, o aviso da folha fora da faixa, a "Lombada incerta" fora do painel, a linha do livro, o livro aberto, a D-497).
- `test_decisoes.py` 28 · `test_decisoes_automatico.py` 24 · `test_decisoes_dividir.py` 19 · `test_decisoes_impressao.py`
  22 · `test_decisoes_mover.py` 13 · `test_decisoes_nucleo.py` 36 · `test_decisoes_tela.py` 35 · `test_decisoes_ver.py` 11
  · `test_trabalho_nao_se_perde.py` 82 · `test_para_revisar_na_tela.py` 25 · `test_paineis_na_tela.py` 22 ·
  `test_paineis.py` 34 · `test_avisos.py` 34 · `test_revisar.py` 28 · `test_reversao_para_revisar.py` 6 ·
  `test_em_branco.py` 6 · `test_dividir_no_programa.py` 19 · `test_livro_aberto.py` 14 · `test_tela_inicio.py` 15 ·
  `test_miniaturas_novas.py` 5 · `test_misto_na_tela.py` 14 · `test_misto_consertos.py` 25 · `test_projetos.py` 24 ·
  `test_resumo_seguro.py` 7 · `test_tirar_fundo_no_programa.py` 54 · `test_barra_de_menu.py` 20 ·
  `test_janela_cabe_na_tela.py` 2 · `test_menu_paineis.py` 3 · `test_marcacao_em_todas.py` 4 ·
  `test_tirar_da_lista_nao_volta.py` 10 · `test_so_neste_pedaco_no_tirar_o_fundo.py` 8: **todos passam**.
- `test_promessas.py -k "revisar or certo or aviso"`: 16 passaram, **1 falha que já falha no código antigo** (P-094,
  conferido no `7859b97` com o mesmo `-k`: depende da ordem dos testes, já anotada na etapa 5). `-k "todo_botao or
  toda_promessa or p095 or p10 or p194"`: 17 passaram (a varredura acha os botões novos e cada um tem promessa).
- `teste_botoes.py`: na rodada do GitHub (abaixo); não rodei no PC (ele abre janelas).

## GitHub

GITHUB_AQUI

## Prints da janela de verdade (1280×657 lógicos, a 125% deste PC = 1600×821; fora da tela; `relatorios/obra-etapa7/prints/`)

Roteiro `relatorios/obra-etapa7/roteiro/prints.py` (cliques por mensagens do Windows; a base é a da etapa 3), do zero e
sem nada marcado: "La vida eterna" (cópia) → Automático só "Dividir" (clique na caixinha, "Rodar") → clique no ícone
"Para revisar" → clique no primeiro cartão → "está certo" três vezes → "ver as N em tela cheia" → "Confirmar e
processar": a "Antes de processar" ("continuar assim mesmo") e a janela de salvar (fechada em "voltar", **sem
processar**) → voltar aos livros → livro aberto → "Ver todas as páginas" → "só as que precisam de atenção". O livro
aberto foi aberto pela função da tela inicial (`abrir_o_livro`), não pelo clique no cartão; o resto por clique.

- **Depois (21 de 21 conferências):** `depois-01` dividido ("0 de 360 conferidas · 18 com dúvida", ícone 18) · `-02`
  "Para revisar" (18, com "Lombada incerta" das páginas 7 e 8, que antes não apareciam; "ver as 18 em tela cheia") ·
  `-03` cartão da página 2 com "Deixar em branco", "Tirar do livro", "está bom assim" · `-04-esta-certo-1/2/3`: página
  2 → 7 → 8 → 9, tique em 2, 7 e 8, contador 1, 2, 3, painel 17, 16, 15 · `-05` a grade com as 15 · `-06` "Antes de
  processar": "Ainda tem 15 páginas [...] (14 avisos na lista)" · `-07` janela de salvar: "Ainda há 15 páginas" · `-08`
  livro aberto "Para revisar: 15" · `-09` "só as que precisam de atenção (15)". Os números: `depois-numeros.txt`.
- **Antes (código `7859b97`):** `antes-01` a `antes-09`: o "está certo" três vezes na página 2 sem nada mudar (sem
  tique, ficou na página 2, contador parado em 1); painel 9; "Antes de processar" 17; janela de salvar **359**; livro
  aberto 9 e a grade **(0)**. Os números: `antes-numeros.txt`.
- Abri e olhei todos. Visto nos prints e consertado: os três botões do cartão saíam cortados ("xar em bra") — agora em
  filas com o nome inteiro; o contador do rodapé não se via (só "La vida ete") — agora o nome encolhe primeiro (ver
  ressalva 1).

## Ressalvas

1. **O contador do rodapé ainda sai cortado com um painel aberto a 1280** ("3 de 36…"): a barra de baixo ficou cheia
   com os botões da etapa 6 ("Uma página", "Duas lado a lado", "antes / depois", zoom). Antes sobrava só o começo do
   nome do livro ("La vida ete"); agora o nome encolhe primeiro e a conta aparece até onde cabe; com o painel fechado
   cabe inteira (`depois-01`); o texto inteiro fica no balão. O rascunho do layout (rodada 12b) já tinha anotado que,
   com um painel aberto, "o nome do livro e a contagem [...] somem". Pergunta 4.
2. **Mexi no núcleo, o mínimo** (`core/avisos.py`, o módulo do "Para revisar"; a 9d mexe em `core/analise.py` e
   `core/pipeline.py`, não neste): o aviso de uma folha cujas páginas foram todas conferidas sai da "Antes de
   processar". Não muda imagem nem PDF.
3. **Os avisos de folha agora contam e aparecem**, então o número subiu onde eles existiam (no "La vida eterna", 10 →
   18 ao abrir: "Lombada incerta" das folhas 4 e 5 e "Qualidade baixa" de algumas folhas). Eles já existiam e só apareciam no
   fim, na "Antes de processar" — é o "356 depois de nada pendente".
4. **O aviso da divisão ("Lombada incerta") aparece também na página**, fora do Dividir, com o botão "aceitar o corte";
   ali a linha não se vê (o clique no cartão dele leva ao Dividir, D-501). Pergunta 2.
5. **Os botões só no cartão da página da vez** (o clique num cartão leva até a página, e ali eles aparecem). Pergunta 3.
6. **D-497 depende de a 9d entrar com `core.pipeline.medir_o_em_branco(doc, projeto, pagina) -> bool`** (o nome e a
   forma do ramo `obra-etapa9d-2026-10-26`); a tela chama a função se ela existir. Como a da 9d pede, a conta mexe no
   projeto da tela por trás (só nos avisos da página).
7. **Testes que falham sem ser desta etapa:** P-094 (falha igual no código antigo com o mesmo `-k`).

## Perguntas para o Samuel (com recomendação; nenhuma trava a etapa)

1. **O contador no Dividir conta folhas** ("1 de 180 conferidas", ao lado de "folha 1 de 180"), porque ali se confere a
   folha; nas outras ferramentas, páginas ("1 de 360"). Foi o jeito de o contador subir no Dividir sem dizer que as
   páginas foram conferidas. *Recomendo deixar assim; a outra opção é contar como conferidas as duas páginas da folha.*
2. **"Lombada incerta" na página** (fora do Dividir): hoje aparece na faixa da página com "aceitar o corte", e o
   "está certo" da página dá aquela página por vista, sem ver a linha. Quer que, fora do Dividir, esse aviso só apareça
   no Dividir (e não conte na página), ou que fique como está? *Recomendo como está: nada escondido, e o clique no
   cartão leva ao Dividir.*
3. **Botões em todos os cartões ou só no da página da vez?** Hoje só no da vez (o clique leva até a página e os botões
   aparecem nela e no cartão). *Recomendo só no da vez (com centenas de páginas o painel ficaria enorme).*
4. **O contador cortado na barra de baixo com painel aberto** (ressalva 1): quer que algo saia da barra de baixo, ou o
   contador vá para outro lugar (por exemplo o cabeçalho "PÁGINAS" das miniaturas)? *Recomendo levar à etapa 11 (nomes
   e textos) ou ao agente de layout com essa pergunta; nesta etapa só fiz o nome encolher primeiro.*
5. **A frase da janela de salvar** continua "Ainda há N páginas que você não conferiu", agora contando as páginas com
   aviso pendente (D-285). Quer trocar a frase (por exemplo "com aviso que você ainda não olhou")? *Recomendo deixar até
   a etapa 11 (nomes e textos).*
6. **O protótipo da rodada 13 mostrava, ao "está certo", um aviso curto** ("Página N: conferida. Saiu do 'Para
   revisar'."). Não fiz (não está no Livro; regra 7). Quer? *Recomendo não: o tique, o contador e a troca de página já
   respondem.*

## Trocas que outra área precisa

- **Etapa 9d (D-497, D-522):** ao juntar, conferir que a função da 9d se chama `medir_o_em_branco(doc, projeto,
  pagina)` e devolve `True` quando o aviso mudou (é o que a tela chama); a D-522 aparece sozinha na linha da D-521 quando
  `LIMIAR_DO_LIVRO_LIGADO` for ligado.
- **Etapa 11 (nomes):** os botões parecidos ("aceitar o corte", "está certo", "está bom assim", "está bom: todas", "está
  bom em tudo"), a frase da janela de salvar (pergunta 5), "folha" × "página" (5.4).
- **Agente de layout / gerente:** a barra de baixo cheia a 1280 com painel aberto (pergunta 4).

## Commits (ramo `obra-etapa7-2026-10-26`)

COMMITS_AQUI

## Escolhas novas no Livro

Nenhuma D-xxx nova (regra 7): onde o Livro não respondia fiz o mínimo para o pedido funcionar e pus cada ponto como
pergunta (1 a 6). Atualizei só a situação de D-255, D-259, D-268, D-284, D-285, D-497, D-521, D-522 e D-543.
