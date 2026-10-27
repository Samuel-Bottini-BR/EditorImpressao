# Obra de 26/10/2026 — etapa 6 (ver o livro na área de trabalho): ONDE PAREI

Ramo `obra-etapa6-2026-10-26` (base `obra-2026-10-26` = `3e112f9`, com as etapas 1-5, 9a, 9c, 10a, 10b), worktree
`.claude/worktrees/obra-etapa6`. Agente: layout. Ordem do Samuel (D-014): fazer até o fim sem pausas; ele confere tudo
no fim. Regra nova da gerente (27/10, palavras do Samuel: "é só para fazer o que eu já tinha mandado, fazer as
ferramentas que colocamos no programa funcionem como deveriam e como eu tinha escolhido"): só o que está no Livro e no
pedido; onde o Livro não responde, perguntar (seção "Perguntas").

**Situação: PRONTO PARA CONFERIR** (começada e terminada em 27/10/2026). Ramo enviado ao GitHub.

## Em uma frase

Agora, na área de trabalho, a barra de baixo tem "Uma página / Duas lado a lado" (como no livro aberto aprovado) e o
menu Ver tem "Ver lado a lado": o livro aparece em pares rolando, com as páginas já divididas e como vão sair, a capa
sozinha à direita; o livro abre sempre uma página por vez; a barra de baixo ganhou "antes / depois", o zoom "– 100% +"
e "ajustar à tela"; e a roda do mouse troca de página (sem zoom), Page Up/Down pulam 10 páginas e Home/End vão ao
começo e ao fim.

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| D-015 (22/10, mais recente que 06/10) | Livro aberto como no UPDF aprovado: "Uma página / Duas lado a lado" na barra de baixo · 20/10, 904 A: "A — Sim, no menu Ver" | Na área de trabalho, a barra de baixo tem "Uma página / Duas lado a lado" e o menu Ver também. |
| D-006 (06/10) | "eu não quero padrão eu quero como opção um botão que eu clique e veja pagina lado a lado" · 201 B / 202 A · 26/10: "eu tinha escolhido para poder trocar de duas paginas para duas" | Opção (não padrão); pares rolando (202 A), também na área de trabalho. O lugar (201 B) foi trocado pela D-015. |
| D-058 (20/10) | `r14-menus-novas`: "A — Sim, no menu Ver" · `ly-ver`: "Está bom" | O menu Ver ganha "Ver lado a lado" (o 5º item que faltava). |
| D-007 (26/10) | "quando eu escolher para começar no automatico e dividir as folhas o livro tem que aparecer em uma pagina por vez para mim." | Dividido, o livro aparece uma página por vez (de fábrica "Uma página"); a folha inteira só no Dividir. |
| D-501 (etapa 4) | (escolha da gerente) como a D-007 fica na tela | Continua valendo. |
| D-343 (05/10) | "Na opção 2 (pares), clicar abre as duas páginas lado a lado, como vai ser impresso." | Na grade "Todas as páginas" em pares, clicar num par abre as duas lado a lado. |
| D-347 (22/10, `lyupdf`, `lu-par`) | "da uma na internet como o updf faz. Tem uma pagina maior que outra ali" | No par as duas ficam da mesma altura; a 1 (capa) sozinha à direita (o mesmo `paginas_rolando.py`). |
| D-021 (29/07, paráfrase) | navegação: roda do mouse, Page Up/Down, Home/End | Na área de trabalho: roda troca de página (sem zoom); Page Up/Down pulam 10 (PEDIDOS.md l.290: "Pula 10 páginas de cada vez"); Home/End vão ao começo e ao fim. |
| D-026 (24/09 e 28/09, paráfrase) | 3.8: consertar o zoom que às vezes não funciona | Não piorar o zoom; a roda no zoom é da etapa 6 (ver "Contradições"). |
| Desenho decidido (rodada 13, `21-rodada13-base.html`) | barra de baixo à direita: "antes / depois", "– 78% +", "ajustar à tela" | Os três na barra de baixo. "antes / depois" = o Original × como vai sair (o "Comparar com o Original" da tela cheia, R11 601 A). |
| Troca da etapa 4 | "a página da vez agora fica na mesma folha quando a lista muda (`lista_de_paginas_mudou`); quem fizer o 'Ver lado a lado' deve usar o mesmo cuidado." | O lado a lado acompanha a lista nova e fica na mesma folha. |
| D-010 | "o botão tem que ser provado que ele faz o que se diz que se faz" | Promessas dos botões novos, com prova; P-136 sem "aguarda". |
| Regra fixa da gerente | não trocar o que vem do ScanTailor nem módulos inteiros que funcionam (reaproveitar `ui/widgets/paginas_rolando.py`) | O lado a lado é o mesmo `PaginasRolando`, com a página que vem das prévias. |

## Contradições achadas (vale a mais recente, D-014) — qual venceu

- **D-015 (22/10) × D-006/201 B (06/10)**, o lugar do botão: **venceu a D-015** (barra de baixo e menu Ver). Nada "em
  cima das páginas, canto direito". Os pares rolando de 202 A continuam (a D-015 não os muda).
- **Roda do mouse: a prova anotada na D-026 ("a roda do mouse sempre dá zoom") × D-021 e o pedido desta etapa (27/10:
  "roda do mouse troca de página (quando não está com zoom)")**: **venceu o pedido de 27/10** (o mais recente). As
  palavras do Samuel na D-026 são só "consertar o zoom que às vezes não funciona"; a frase da roda é a prova escrita
  pela gerente. Ficou: sem zoom a roda troca de página; com zoom a roda continua dando zoom como antes; Ctrl+roda dá
  zoom sempre (senão o zoom pela roda sumiria). Pergunta 2.

## Como cumpri cada uma

| Decisão | O que ficou no programa | Prova (`tests/test_decisoes_ver.py`, salvo dito) | Print |
|---|---|---|---|
| D-015 | Barra de baixo, à direita: "Uma página" / "Duas lado a lado" (os nomes e os balões do livro aberto aprovado), aceso no azul como lá. "Duas lado a lado" põe no lugar da página os pares rolando; "Uma página" volta à ferramenta, na mesma página. | `test_d015_duas_lado_a_lado_na_barra_de_baixo_com_os_pares_do_livro`; P-136 | `depois-02` (Uma página), `depois-03` (Duas lado a lado) × `antes-02` (barra sem os botões) |
| D-006 / 202 A / D-347 | É o `PaginasRolando` do livro aberto (não reescrito), com uma troca só: a página vem da PRÉVIA da área de trabalho (girada, dividida, endireitada, cortada, com o filtro), em `ui/widgets/paginas_lado_a_lado.py`. Os pares são os do PDF que vai sair (`Projeto.paginas_ativas`): a 1 sozinha à direita, depois 2-3, 4-5...; as duas do par na mesma altura. A página da vez tem o quadro azul; rolar ou clicar numa página muda a página da vez (a barra de baixo e as miniaturas acompanham). | o teste acima mede os pares, a capa na metade da direita, a mesma altura, e que cada lugar recebe a prévia da SUA página (em pé = dividida; o número de quadradinhos de cada página); `test_pares_sao_os_do_livro_que_vai_sair` | `depois-03`, `depois-04` (rolando) |
| D-058 | Ver > "Ver lado a lado" (marcável, entre "Ícones da direita" e "Todas as páginas", a ordem da 904); anda junto com a barra de baixo. | `test_d058_menu_ver_tem_ver_lado_a_lado_e_anda_com_a_barra`; P-136 (pelo menu) | `depois-09-menu-ver` |
| D-007 / D-501 | Todo livro abre em "Uma página" (o lado a lado é opção, não padrão; D-006). Depois do Automático com "Dividir", uma página por vez (a etapa 4 já fazia; continua). No Dividir a folha inteira fica (para consertar): ali os botões do ver ficam apagados, com o balão "No Dividir a tela mostra a folha inteira, com a linha; escolha outra ferramenta para ver as páginas." | `test_d007_todo_livro_abre_uma_pagina_por_vez`, `test_no_dividir_a_folha_inteira_continua`; as da etapa 4 (`test_d007_*` em `test_decisoes_dividir.py`) continuam passando | `depois-02` |
| D-343 | Na grade "Todas as páginas" em pares, o clique num par volta ao trabalho com "Duas lado a lado" nele (uma a uma, como sempre, uma página). | `test_d343_clicar_num_par_da_grade_abre_lado_a_lado` | — |
| Troca da etapa 4 | Quando a lista muda (dividir/juntar uma folha, tirar do livro, desfazer), os pares são refeitos e ficam na página da vez, que a etapa 4 já mantém na mesma folha. | `test_troca_da_etapa_4_lista_muda_e_o_lado_a_lado_fica_na_mesma_folha` | — |
| Desenho: "antes / depois" | Botão marcável: a página da vez com o Original à esquerda da linha e como vai sair à direita, a linha arrasta (a mesma peça `VistaAntesDepois` da tela cheia dos filtros). Página em Original: "Escolha outro filtro para comparar com o Original." (a frase da tela cheia). | `test_antes_depois_mostra_o_original_e_como_vai_sair` (mede o papel: amarelado no antes, branco no depois); P-195 | `depois-05` (página em Original), `depois-06` (Preto e branco) |
| Desenho: "– N% +" e "ajustar à tela" | O mesmo zoom do menu Ver (Aproximar, Afastar, Ajustar à tela); o número mostra o zoom da página (100% = a página inteira cabendo, como o "Zoom: N%" que a ferramenta de marcar já dizia). No lado a lado e no antes/depois ficam apagados (ali a página cabe na tela). | `test_zoom_da_barra_de_baixo`; P-146 (menu e barra) | `depois-07-zoom-156` |
| D-021 roda | Sem zoom, a roda em cima da página troca de página (no Dividir, de folha); com zoom dá zoom, como antes; Ctrl+roda dá zoom sempre. Na ferramenta de marcar com o Pincel ou a Varinha a roda continua mudando espessura/tolerância (como antes). Nos pares, a roda rola. | `test_d021_roda_troca_de_pagina_sem_zoom_e_da_zoom_com_zoom` (falha no antigo por asserção: a roda só dava zoom) | — (a roda não chega pela mensagem do Windows com a janela fora da tela: ressalva 4) |
| D-021 Page Up/Down, Home/End | Page Down/Up andam 10 páginas (10 folhas no Dividir), Home à primeira, End à última. | `test_d021_page_down_pula_10_e_home_end` (falha no antigo por asserção) | `depois-08` (Page Down: da página 7 para a 17) |
| D-010 | P-136 sem "aguarda" e com prova de verdade (barra e menu); P-146 com as chaves da barra; P-195 nova ("antes / depois"). | `tests/test_promessas.py` | — |

## Causa (por que não existia)

O "Ver lado a lado" só tinha sido construído no livro aberto (`ui/tela_inicio.py`, a barra de baixo do UPDF) e na grade
"Todas as páginas" ("em pares"); a área de trabalho só sabia mostrar a página da ferramenta. A barra de baixo da área de
trabalho estava "sem 'antes / depois' e zoom", à espera de etapa (rascunho do layout, rodada 13). As teclas Page
Up/Down e Home/End só existiam no livro aberto; na área de trabalho a roda só dava zoom.

## O que mudou (por arquivo)

- `ui/widgets/paginas_lado_a_lado.py` (novo): `PaginasLadoALado`, filha do `PaginasRolando` (que não mudou): a fonte
  das páginas são as prévias, os pares das páginas que saem, a proporção acertada quando a prévia chega sem a tela
  pular, o clique que escolhe a página da vez.
- `ui/tela_conferir.py`: o lugar da página virou uma pilha (a ferramenta, os pares, o antes e depois:
  `vista_da_pagina`, `_acertar_a_vista_da_pagina`); a barra de baixo ganhou os botões (`_montar_o_ver_da_barra_de_baixo`);
  `definir_mostrar`, `_alternar_antes_depois`, `_mostrar_antes_depois`, `_acertar_o_lado_a_lado`, `_tamanhos_estimados`,
  `_previa_do_lado_a_lado`, `_pagina_do_lado_a_lado`; o zoom (`_vista_com_zoom`, `_acertar_o_zoom_da_barra`); a roda
  (`_roda_na_pagina`, pelo `eventFilter`); Page Up/Down, Home/End em `tratar_tecla`; D-343 em `_voltar_das_todas`; todo
  livro abre em "Uma página" (`carregar`).
- `ui/barra_de_menu.py`: Ver > "Ver lado a lado" (`lado_a_lado`). `ui/janela_principal.py`: liga o item e o mantém
  igual à barra. `ui/estilo.py`: o tamanho e o aceso dos botões novos (`jeitoDaBarraDeBaixo`).
  `ui/widgets/todas_as_paginas.py`: só o comentário (o "abrir lado a lado" do par agora existe).
- Testes: `tests/test_decisoes_ver.py` (novo, 11), `tests/test_promessas.py` (P-136, P-146, P-195),
  `tests/promessas/promessas.md`, `teste_botoes.py` (`testar_o_ver_da_barra_de_baixo`: clica os botões e confere a
  promessa).
- `docs/plano/DECISOES.md`: situação de D-006, D-015, D-021, D-058, D-343. `memoria/itens/layout.md`: a barra de baixo.
- `core/`: nada.

## Testes (no PC, um arquivo por vez, TEMP e --basetemp em `_tmp/`)

- `tests/test_decisoes_ver.py`: **11 passaram**. **Reversão** no código antigo (`3e112f9`, cópia em `_tmp/antigo`):
  **os 11 falham** (`relatorios/obra-etapa6/reversao-no-codigo-antigo.txt`). Ressalva honesta: 9 falham porque o botão
  ou o item não existe lá; os 2 da navegação (`test_d021_*`) falham por asserção (a roda só dava zoom; Page Down não
  andava).
- `test_decisoes.py` 28 · `test_decisoes_tela.py` 35 · `test_decisoes_dividir.py` 19 · `test_decisoes_automatico.py` 24
  · `test_decisoes_mover.py` 13 · `test_decisoes_impressao.py` 22 · `test_decisoes_nucleo.py` 36 ·
  `test_trabalho_nao_se_perde.py` 82 · `test_janela_cabe_na_tela.py` 2 · `test_barra_de_menu.py` 20 ·
  `test_livro_aberto.py` 14 · `test_atalhos.py` 15 · `test_visualizador.py` 70 · `test_paineis_na_tela.py` 22 ·
  `test_paineis.py` 34 · `test_miniaturas_novas.py` 5 · `test_dividir_na_tela.py` 9 · `test_girar_na_tela.py` 22 ·
  `test_endireitar_na_tela.py` 5 · `test_tela_inicio.py` 15 · `test_misto_na_tela.py` 14: **todos passam**.
- `test_promessas.py -k "lado or pares or zoom or ver or p12 or p13 or p14 or p195 or todo_botao or toda_promessa"`:
  64 passaram, 3 xfail, **1 falha que já falha no código antigo** (P-127 pelo menu, conferido no `3e112f9`). Depois do
  acerto do estilo: P-136 (2), P-146 (2), P-195 e as três da varredura (todo botão tem promessa, toda promessa tem botão
  e prova): 8 passaram.
- `teste_botoes.py`: **337 ações, 0 falhas** (com a parte nova "o ver da barra de baixo": cada botão e a promessa
  dele).

## GitHub

- **40588991790** (commit `3031157`): o `teste_botoes.py` tinha um erro de sintaxe meu (uma quebra de linha no meio de
  um texto, ao escrever o arquivo) — quebrou o "Botões" e a coleta de `test_pasta_de_dados_dos_scripts.py`.
  Consertado em `bd7ed19`.
- **40592137706** (commit `bd7ed19`, a final): **partes 3, 4 e 5 e "Botões e prints da janela real" passam**; parte 1
  com P-085, P-092 e P-127; parte 2 com `test_paginas_diferentes.py::test_na_analise_a_pagina_torta_ganha_o_aviso`.
  Nenhuma é desta etapa: P-085 e P-127 são as da base (etapas 4 e 5); P-092 falha também no código antigo (no PC,
  `3e112f9`; no PC, no código novo, passa); a das páginas diferentes é a instável que a etapa 5 já anotou (falha às
  vezes no código antigo).

## Prints da janela de verdade (1280×657 lógicos, a 125% deste PC = 1600×821; fora da tela; `relatorios/obra-etapa6/prints/`)

Roteiro `relatorios/obra-etapa6/roteiro/prints.py` (cliques e teclas por mensagens do Windows; a base é a da etapa 3),
caminho do Kaique do zero, sem nada marcado: "La vida eterna" (cópia) → Automático só "Dividir" (clique na caixinha) →
Rodar → página 7 → "Duas lado a lado" → rolar → "Uma página" → "antes / depois" (página em Original) → clique na página,
tecla 2 (Preto e branco) → "antes / depois" → "+" duas vezes → "ajustar à tela" → Page Down → menu Ver.

- **Depois (16 de 16 conferências):** `depois-00` livros · `-01` aberto, nada marcado · `-02` dividido, uma página
  por vez, a barra de baixo com "Uma página" aceso · `-03` "Duas lado a lado": as páginas 6 e 7 do livro (o quadro azul
  na 7), a mesma altura · `-04` rolando os pares · `-05` antes/depois numa página em Original (a frase) · `-06`
  antes Original × depois Preto e branco, com a linha · `-07` zoom 156% · `-08` Page Down: página 17 · `-09` menu Ver
  com "Ver lado a lado".
- **Antes (código `3e112f9`, 5 de 5):** `antes-00` a `antes-02`: a barra de baixo sem nenhum dos botões; o menu Ver sem
  "Ver lado a lado".
- Abri e olhei todos. Visto nos prints e consertado: os botões novos saíam com a letra grande dos "‹ ›" e sem o aceso
  da escolha (passaram para o tamanho e o azul do livro aberto); na primeira rodada a tecla 2 e o Page Down não
  chegavam porque o foco estava na lista do Automático (o roteiro agora clica na página antes, como o Kaique; ressalva 3).

## Ressalvas

1. **Os pares seguem a ordem do PDF, com a 1 sozinha à direita (D-347).** No "La vida eterna" a numeração impressa do
   livro faz a página ímpar impressa cair à esquerda (o PDF começa na folha de rosto, que é a "5"). É a regra
   decidida; vai na pergunta 6.
2. **O lado a lado mostra a prévia (a qualidade da prévia escolhida nas Configurações, "Rápida" de fábrica), não o
   PDF final.** Cada página aparece primeiro como um quadro cinza com o número e, em seguida, a prévia (desenhada por
   trás, a mesma das ferramentas). Página tirada do livro não aparece nos pares (não está no PDF). Página movida na
   ferramenta Mover aparece sem o movimento (é a D-547, etapa 9b).
3. **As teclas vão para quem tem o foco.** Depois de usar o painel Automático, o foco fica na lista dele e as teclas
   (Page Down, os números dos filtros) vão para ela até o Kaique clicar na página. Já era assim (etapa 5 viu o mesmo
   com a tecla F); não mexi.
4. **A roda do mouse de verdade não foi provada na janela fora da tela** (o Qt não aceita a roda por mensagem do
   Windows com a janela inativa: ficha 3.8, "Tentado e descartado"). A prova é o evento da roda do Qt
   (`test_d021_roda_*`); vale o Samuel conferir com o mouse.
5. **"antes / depois" e zoom não valem no lado a lado** (ali a página cabe na tela) e o antes/depois mostra uma página
   só (a da vez). Pergunta 3.
6. **Testes que falham sem ser desta etapa:** P-127 ("Antes de processar" pelo menu) falha igual no código antigo
   (conferido no `3e112f9`); P-092 falha no antigo também (no PC); P-085 e P-090 aparecem nas rodadas do GitHub do
   ramo-base (etapas 4 e 5).

## Perguntas para o Samuel (com recomendação; nenhuma trava a etapa)

1. **Lembrar "Uma página / Duas lado a lado" de um livro para o outro?** Hoje todo livro abre em "Uma página" (D-007 e
   D-006 "não quero padrão"); o livro aberto lembra a escolha (D-347). *Recomendo deixar como está: abrir sempre em
   "Uma página".*
2. **A roda do mouse com zoom:** hoje, com a página aumentada, a roda continua aumentando/diminuindo (como antes), e
   Ctrl+roda dá zoom sempre. Quer, com zoom, que a roda **ande pela página** (para cima e para baixo, como no UPDF e
   no Acrobat)? *Recomendo sim (como o UPDF); fica para a etapa que o Samuel escolher.*
3. **Zoom e "antes / depois" no lado a lado:** hoje ficam apagados ali (as páginas cabem na tela; "antes / depois" é
   de uma página). Quer zoom também nos pares (como o "Caber a altura / largura" do livro aberto)? *Recomendo não por
   agora.*
4. **O número do zoom:** o desenho mostra "78%"; o programa mostra 100% quando a página inteira cabe na tela (como a
   ferramenta de marcar já dizia "Zoom: 100%"). Quer que 100% seja o "tamanho real" da página (como o "Tamanho real"
   do livro aberto)? *Recomendo deixar 100% = a página inteira (o Kaique entende "voltar a 100%" = ver a página toda).*
5. **"antes" = o Original da página** (girada, dividida, endireitada e cortada, só sem o filtro), como a tela cheia dos
   filtros. Ou quer o "antes" = a folha como veio do scanner? *Recomendo o de agora (é o que a tela cheia já mostra).*
6. **Os pares:** a 1 sozinha à direita e depois 2-3, 4-5 (D-347). Num livro cujo PDF começa no meio da numeração
   (o "La vida eterna"), a página ímpar impressa cai à esquerda. Quer um jeito de escolher "a 1 junto da 2"? *Recomendo
   esperar: o "Montar cadernos" é que manda na impressão.*

## Trocas que outra área precisa

- **Etapa 9b (D-547):** quando as telas mostrarem a página movida, o lado a lado e o antes/depois mostram junto (eles
  usam a mesma prévia, `GerenciadorPrevias.pegar`).
- **Gerente (Lista de bugs):** o foco preso na lista do Automático (ressalva 3).

## Commits (ramo `obra-etapa6-2026-10-26`)

- `15d8ec1` ONDE-PAREI com as decisões que a tarefa precisa cumprir
- `4d147bc` Uma página / Duas lado a lado na barra de baixo e no menu Ver (pares das prévias), antes / depois, zoom,
  roda, Page Up/Down, Home/End; provas e promessas
- `3031157` teste_botoes confere o ver da barra de baixo; reversão; situação no Livro; roteiro dos prints
- `bd7ed19` botões da barra de baixo no tamanho e no aceso do livro aberto; teste_botoes sem o erro de sintaxe; prints
- (este ONDE-PAREI final)

## Escolhas novas no Livro

Nenhuma D-580+: pela regra nova da gerente, onde o Livro não respondia não criei escolha; fiz o mínimo para o pedido
funcionar e pus cada ponto como pergunta (1 a 6). Atualizei só a situação de D-006, D-015, D-021, D-058 e D-343.
