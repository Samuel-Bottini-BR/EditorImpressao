# Revisão dos nomes — levantamento (28/10/2026)

Pedido: D-374 (22/10, `dv-pr-antes`): "os nomes dos botões são horriveis, na verdade em todo o programa [...] revisarmos
todos os nomes de botão com um novo agente" — **ele decide um por um**. Regra 7 do `CLAUDE.md` §11 (27/10): "é só para
fazer o que eu já tinha mandado". Por isso **nada foi mudado no programa**: só o levantamento e as perguntas.

- Código lido: worktree `obra-juncao`, ramo `obra-2026-10-26`, commit `7f25e86` (só leitura). Os números de linha são
  desse commit. A tela antiga "Marque o que você quer fazer" (`ui/tela_opcoes.py`) não abre mais (D-488): textos que só
  existem lá ficaram de fora.
- Conferido contra: `docs/plano/DECISOES.md`, o rascunho do layout ("O que fica decidido" das rodadas), a Central
  (`docs/plano/central/conferencias/`), a lista única de 23/10 (seção 5), o teste do Kaique de 26/10, os
  `relatorios/obra-etapa*/ONDE-PAREI.md` e a auditoria de 27/10.
- Perguntas para a Central: `relatorios/obra-etapa11/nomes-28-10.json` (20 perguntas, na ordem do caminho de todo dia).
- **Contagem:** 98 textos levantados nas seções 1 a 4 (82 com problema e em pergunta, 3 de acento já decididos, 13 de
  detalhe sem pergunta); mais 31 grupos de nomes já aprovados, deixados de fora (seção 5).

---

## 1. Em pergunta na Central (82 textos, 20 perguntas)

### `nm-esta-bom` — os botões parecidos

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "está certo" | `ui/tela_conferir.py:856` (faixa) | Parece igual a "está bom assim" e "aceitar o corte" (Kaique, 26/10) | fica | D-259 (05/10, "Aprovado"); D-374 |
| "está bom assim" | `core/analise.py:204` e em quase todo aviso (`:213`…`:441`) | Parece igual a "está certo" | fica | D-269 (`pr-sem-conteudo` "Está bom"); D-272 |
| "aceitar o corte" | `core/analise.py:341` (aviso "Lombada incerta") | Faz o mesmo que "está bom assim" (ação `revisar`), com outro nome | "está bom assim" | D-374 |
| "está bom: todas" / "está bom" | `ui/widgets/paineis.py:1043` | Aparece embaixo de cada motivo sem dizer qual; Kaique: "sem dizer de qual motivo é" | "está bom nas 8 (Parece em branco)" | D-272 (08/10; 21/10 "Está bom") |
| "está bom em tudo" | `ui/widgets/paineis.py:918` | "fácil apertar sem querer e aprovar 54 páginas" (Kaique) | "está bom nos 54 avisos" | D-272 |

### `nm-antes-de-processar` — janela "Antes de processar"

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "Selecionar todas" / "Nenhuma" | `ui/janela_dos_avisos.py:145`, `:150` | Foi nesta janela que ele disse "os nomes dos botões são horriveis" | "marcar todas" / "desmarcar todas" | D-374 (22/10) |
| "está bom nas marcadas" | `ui/janela_dos_avisos.py:166` | Família "está bom" | segue a resposta de `nm-esta-bom` | D-272 |
| "ver" | `ui/janela_dos_avisos.py:173` | Não diz que fecha a janela e vai à página | "ir para a página" | D-274 (08/10 "Fica assim"); D-374 (mais nova) |
| "continuar assim mesmo" | `ui/janela_dos_avisos.py:179` | Não diz que processa | "processar assim mesmo" | D-274; D-374 |

### `nm-folha-pagina` — folha × página

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "{N} páginas · aberto …" (alto do livro aberto) | `ui/tela_inicio.py:918` | Em cima 360 páginas, embaixo conta 180 | "180 folhas, 360 páginas" | D-367 (12/10) |
| "página 1 de 180" (pílula do livro aberto) | `ui/tela_inicio.py:976` | Conta folhas do PDF e diz "página" | "folha 1 de 180" | D-367 |
| "folha anterior" / "próxima folha" | `ui/tela_inicio.py:768` | Ao lado de "página N de" | fica | D-367 |
| "Ver todas as páginas" — dica "Todas as folhas do livro, em grade" | `ui/tela_inicio.py:691` | Nome diz página, dica diz folha | dica coerente com o que a grade mostra | D-343 |
| "tamanho da folha..." / "Tamanho da folha" / "Tamanho final da folha impressa:" | `ui/tela_conferir.py:1960`, `:1666`; `ui/dialogo_tamanho_da_folha.py:56`, `:69` | "folha" com um 3º sentido (tamanho final da página) | "tamanho final da página..." | D-314 (14/10: folha = papel da impressora) |
| "Folha menor que o corte" (aviso) | `core/analise.py:438` | Idem | "Tamanho final menor que o corte" | D-314 |
| "A folha escolhida (…)" / "Área branca" (Mover) | `ui/tela_conferir.py:2070`, `:2074`, `:1955` | Idem | acompanha a resposta | D-314 |
| "Endireitar folhas tortas — corrige páginas inclinadas" (etapa) | `core/automatico.py:82`, `:91` | Endireita páginas; o subtítulo já diz página | "Endireitar páginas tortas" | D-367 |
| "Página 9" no "Para revisar" (leva à folha 5) | `ui/widgets/paineis.py:1007` | "A conta folha ↔ página não é mostrada" (Kaique) | "Página 9 (folha 5)" | D-367 |

### `nm-nao-esta` — "não … esta" × "deixar como veio"

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "não dividir esta" | `ui/tela_conferir.py:1627`, `:4369`; `core/analise.py:346` | O Endireitar trocou o igual ("não endireitar esta") por "deixar como veio" | "deixar como veio" | D-368 (12/10) |
| "não cortar esta" | `ui/tela_conferir.py:1655`; `core/analise.py:382` | Idem | "deixar como veio" | D-368 |
| "voltar como veio" (Mover) | `ui/tela_conferir.py:1980` | Quase igual a "deixar como veio", outra palavra | "deixar como veio" | D-368 |

### `nm-limpar-a-folha` — a etapa do filtro e o painel do filtro

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "Limpar a folha — tira o amarelado" (etapa do Automático) | `core/automatico.py:84`, `:93` | De fábrica vem Original, que não limpa nada (lista 5.11) | "Filtro do livro — hoje: Original (não mexe na página)" | nenhuma sobre o nome; D-366 é do "Limpar a sujeira" |
| "Este livro não passa pelos filtros: a etapa “Limpar a folha” está desligada." | `ui/widgets/paineis.py:1714` | Segue o nome da etapa | acompanha | — |
| "Filtro da página" (painel) | `ui/widgets/paineis.py:92`; `ui/barra_de_menu.py:311` | Tem "todas" embaixo: muda o livro inteiro (Kaique) | fica (opção 2: "Filtro") | D-059 (painel aprovado; a palavra não foi perguntada) |

### `nm-scantailor` — "ScanTailor" em nomes não aprovados

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "Cortar seguindo o conteúdo (como o ScanTailor)" | `ui/automatico.py:831`; `ui/tela_conferir.py:1708` | Kaique não sabe o que é ScanTailor (lista 5.8) | "Cortar seguindo o conteúdo" | — |
| "Cortar a beirada da folha vizinha — o corte da sobra do ScanTailor" | `ui/automatico.py:829-830`; `core/pipeline.py:4882` | Idem | "Cortar a beirada da folha vizinha" | — |
| "fica no mesmo lugar (como o ScanTailor)" | `ui/automatico.py:95`; `ui/tela_configuracoes.py:266` | Idem | "fica no mesmo lugar" | D-093 (aprovou "Fica no mesmo lugar") |
| "Endireitar: as contas discordam" + "A conta do ScanTailor e a do Editor acharam inclinações diferentes…" | `core/analise.py:293-294` | Em 9 de 50 páginas do Boécio, 69 de 135 do Righetti | "Endireitar: dois ângulos diferentes" + frase sem os nomes | D-369/D-370 aprovaram "ScanTailor/Editor" só na linha e na lista do Endireitar |

### `nm-tirada` — "apagada" × "Tirar do livro"

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| ", e 1 foi apagada" / ", e N foram apagadas" | `ui/janela_confirmar.py:172` | O botão é "Tirar do livro"; "apagada" parece perdida de vez | "; 1 foi tirada do livro" | D-046, D-269 ("Tirar do livro") |
| "  -  N apagadas" (contador) | `ui/tela_conferir.py:4425` | Idem | "N tiradas" | idem |
| "apagada" (miniatura e grade) | `ui/widgets/tira_miniaturas.py:174`; `ui/widgets/todas_as_paginas.py:254` | Idem | "tirada" | idem |
| "(apagada)" (escolher páginas) | `ui/dialogo_escolher_paginas.py:73` | Idem | "(tirada)" | idem |
| "Não sobrou nenhuma página para gerar. Restaure alguma página apagada." | `core/pipeline.py:4364` | Idem; "Restaure" não é o nome de botão nenhum ("trazer de volta") | "Traga de volta alguma página tirada do livro" | idem |

### `nm-frase-salvar` — janela de salvar

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "Ainda há N páginas que você não conferiu. Dá para processar assim mesmo, mas…" | `ui/janela_confirmar.py:211-213` | Conta as páginas com aviso pendente, mas diz "não conferiu" (etapa 7 deixou para cá) | "Ainda há N páginas com aviso que você não olhou." | D-285 (21/10) |

### `nm-historico` — nomes antigos no Histórico

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "Voltar ao corte automático na página N" | `ui/tela_conferir.py:4989` | O botão é "usar o corte do programa" | "usar o corte do programa — página N" | D-368 |
| "Voltar ao endireitar automático na página N / em N páginas" | `ui/tela_conferir.py:5480`, `:5482` | O botão é "usar o ângulo do programa" | "usar o ângulo do programa — página N" | D-368 |
| "Não endireitar a página N" / "Não endireitar N páginas" | `ui/tela_conferir.py:5377-5378` | O botão é "deixar como veio" | "deixar como veio — página N" | D-368 |
| "Algoritmo do Preto e branco na página N: …" | `ui/tela_conferir.py:5528` | Palavra técnica; na tela é "Jeito do preto e branco" | "Jeito do preto e branco da página N: …" | D-374 |
| "Conferir a pagina N" | `ui/tela_conferir.py:6505` | Sem acento; o botão é "está certo" | "está certo — página N" | D-365 (acento), D-259 |
| "Linha de corte da folha N" / "de todas as N folhas" | `ui/tela_conferir.py:4648`, `:4659` | É a linha azul de dividir, não de cortar | "linha de dividir da folha N" | D-374 |
| "Posição/tamanho do conteúdo na página N" | `ui/tela_conferir.py:5042` | Barra no meio do nome | "lugar e tamanho do conteúdo na página N" | — |
| "Corte de borda da página N" / "Não cortar a borda da página N" | `ui/tela_conferir.py:4943`, `:4951` | O botão é "não cortar esta" (ou o que ele escolher em `nm-nao-esta`) | nome do botão | D-368 |

### `nm-dois-mover` — duas ferramentas "Mover"

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "Mover e redimensionar" (F) | `ui/widgets/trilha_agrupada.py:85` | Quase igual ao da tecla A | "Mover a página" | D-008 ("redimensionar" é palavra dele); D-540 (gerente) |
| "Mover e mudar o tamanho da área" (A) | `ui/widgets/editor_selecao.py:118`; `ui/tela_conferir.py:2584`, `:2618` | Idem | "Mover a área marcada" | — |
| "Para mover ou mudar o tamanho do conteúdo na folha, use a ferramenta Mover (tecla F)." | `ui/tela_conferir.py:1683` | Acompanha o nome | acompanha | D-544 |

### `nm-menu-marcar`

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "Procurar de novo" (menu Marcar) | `ui/barra_de_menu.py:199` | Mesma ação do botão "detectar automaticamente"; mesmo nome do "procurar de novo" do cartão do livro | "Procurar de novo nesta página" | — |
| "detectar automaticamente" (+ "Nada marcado ainda. Clique em \"detectar automaticamente\"…") | `ui/tela_conferir.py:2487`, `:3772` | Dois nomes para a mesma ação | "Procurar de novo nesta página" | — |
| "Limpar tudo" (+ "Tirei tudo. O filtro volta a tratar a folha inteira igual.") | `ui/barra_de_menu.py:200`; `ui/tela_conferir.py:2690` | "Limpar" já é filtro e pontinhos | "Tirar todas as marcações" | — |
| "Deixar a folha em branco" (menu Marcar) + "Esta folha vai sair em branco…" | `ui/barra_de_menu.py:202`; `ui/tela_conferir.py:2711` | Quase igual a "Deixar esta página em branco" (menu Página); folha × página | "Marcar a página inteira como papel" | D-200 (06/08) |

### `nm-manter-cor-tinta`

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "manter a cor da tinta" | `ui/widgets/paineis.py:1234` | Nome provisório; "esse botão ainda é bem confuso" | "tinta colorida" | D-375 (22/10, volta na revisão de nomes); D-229 |

### `nm-montar-dois`

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "Montar cadernos — para imprimir, dobrar ao meio e costurar (no tamanho do scan)" (+ "Monta os cadernos no tamanho do scan (sem A4, sem margem)…") | `core/automatico.py:87`, `:96`; `ui/automatico.py:971` | Parecido com o botão de A4 (lista 5.12) | "PDF já em cadernos (tamanho do scan, sem margem)" | D-330 ("Deixar os dois") |
| "montar para imprimir em A4 (com margens)..." | `ui/tela_final.py:201` | Idem | fica | D-330 |

### `nm-montar-nomes` — janela "Montar para imprimir"

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "Ordem de páginas:" (Frente e verso / Só a frente / Só o verso) | `ui/dialogo_impressao.py:467` | É o lado do papel; no "imprimir agora" se chama "Lados do papel:" (`:972`) | "Lados do papel:" | D-315 (nomes do UPDF) |
| "Folhas de (0 = todas):" → "todas até todas" | `ui/dialogo_impressao.py:469`, `:251`, `:261` | Lê "todas até todas" (9b-1 mandou para cá) | "Só as folhas: da … até a …" | D-315 |
| "Páginas do livro de (0 = todas):" | `ui/dialogo_impressao.py:528` | Idem | "Só as páginas: da … até a …" | D-315 |
| "Escala personalizada:" / "Escala personalizada (%)" | `ui/dialogo_impressao.py:451`; `core/impressao.py:112` | Técnico (Kaique) | "Escala:" (9a) | D-315, D-317 |
| "Páginas por caderno:" | `ui/dialogo_impressao.py:459` | — | "Cada caderno:" (9a) | D-315 |
| "Encadernação: Esquerda / Direita" | `ui/dialogo_impressao.py:461-463` | Não diz que é o lado da costura | "costura à esquerda / à direita" (9a) | D-315 |
| "Rotação automática" | `ui/dialogo_impressao.py:519` | — | "Girar sozinho a página deitada" (9a) | D-331 |
| "Centralizar automático" | `ui/dialogo_impressao.py:522` | — | "Centralizar sozinho" (9a) | D-315 |
| "Reverter páginas" | `ui/dialogo_impressao.py:534` | Técnico (Kaique) | "Ordem invertida" (9a) | D-315 |
| "Agrupar" | `ui/dialogo_impressao.py:550` | Técnico (Kaique) | "Agrupar as cópias" (9a) | D-325 |

### `nm-montar-frases` — frases novas da etapa 9a

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "O PDF do livro não muda: aqui só se arrumam as folhas para a impressora." | `ui/dialogo_impressao.py:389` | Texto que ele não pediu (regra 7) | fica | `fr-26` (22/10) |
| As 4 frases dos formatos ("Duas páginas de cada lado de uma folha A4 deitada…" etc.) | `ui/dialogo_impressao.py:110-114` | Idem | ficam | `fr-26` |
| "Ligada de fábrica: sem ela pode sair algo errado." | `ui/dialogo_impressao.py:530` | Idem; vaga | fica | D-326 ("Precisa: sem ela sai algo errado") |
| "Sai o livro inteiro, depois o livro inteiro de novo." | `ui/dialogo_impressao.py:551` | Idem; não fala de cópias | "Com 2 cópias: sai o livro inteiro, e depois a segunda cópia inteira." | — |
| "Ao gravar, os passos para imprimir e dobrar aparecem aqui." | `ui/dialogo_impressao.py:693` | Idem | fica | `fr-26` |

### `nm-atalhos`

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "Ctrl+Return" | `ui/barra_de_menu.py:133` | Inglês (lista 5.10; promessa P-027) | "Ctrl+Enter" | D-365 |
| "Ctrl+Left" / "Ctrl+Right" | `ui/barra_de_menu.py:238-239` | Inglês | "Ctrl+seta para a esquerda / direita" | D-365 |
| "Del" / "Shift+Del" | `ui/barra_de_menu.py:253-254` | Inglês | "Delete" / "Shift+Delete" | D-365 |
| "Show Details..." (botão do Qt na "Lista de atalhos") | `ui/janela_principal.py:673` (`setDetailedText`); a tradução do Qt (`ui/dialogos_de_arquivo.traduzir_o_qt`) não é chamada no `main.py` | Lista escondida atrás de botão em inglês | lista à vista, sem o botão | D-365 |

### `nm-codigos`

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "… (D-068: toda função automática liga e desliga). O Desfazer traz de volta." | `ui/automatico.py:532` | Número interno na dica | tirar "(D-068: …)" | — |
| "D-094: a mesma escolha existe nas Configurações…" | `ui/automatico.py:825` | Idem | tirar "D-094:" | — |
| "Livro novo não divide sozinho: só quando esta etapa roda (G2)…" | `ui/automatico.py:814` | Idem | tirar "(G2)" | — |

### `nm-tela-livros`

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "remover da lista" (menu "Mais...") × "Tirar da lista?" / "Tirar da lista" (janela) | `ui/tela_inicio.py:617`; `:421-422` | Dois nomes para a mesma ação | "tirar da lista" | D-335 ("Tirar da lista") |
| "procurar de novo" (cartão) × "procurar o livro" ("Mais...") | `ui/tela_inicio.py:512`, `:608`, `:335`, `:942` | Dois nomes; e "Procurar de novo" do menu Marcar é outra coisa | "procurar o livro" | — |
| "projeto" ("Nenhum projeto com … no nome", "Nome deste projeto:", "livro deste projeto") | `ui/tela_inicio.py:266`, `:392`, `:335`, `:366` | O resto do programa diz "livro" | "livro" | — |

### `nm-desligar-marcadas`

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "desligar as marcadas" / "Desligar as marcadas" | `ui/automatico.py:530`, `:715` | "marcadas" pode ser páginas; desliga o que está marcado | "desligar estas etapas" | D-068 (regra); D-484 (nome da gerente) |

### `nm-jeito-pb`

| Texto atual | Onde no código | Problema | Proposta (recomendada) | Decisão dele que toca |
|---|---|---|---|---|
| "Sauvola (padrão)" | `core/filtros.py:320` | Diz "padrão", mas o de fábrica é "Automático"; nome técnico (`CLAUDE.md` §1) | "letra fina" (Sauvola na dica) | — |
| "Otsu (letra grossa/gótica)" | `core/filtros.py:321` | Nome técnico | "letra grossa ou gótica" | — |
| "Wolf (scan de baixo contraste)" | `core/filtros.py:322` | Nome técnico | "scan apagado" | — |
| "Automático" (item da lista "Jeito do preto e branco") | `ui/tela_conferir.py:2979`; `ui/widgets/filtros_tela_cheia.py:434` | Mesmo nome do painel Automático | "o programa escolhe" | — |

---

## 2. Acento — já decidido, sem pergunta (3)

D-365 (18/07): "Corrija TODOS os textos da interface para português correto". Fica para quem for consertar (etapa 11),
sem perguntar de novo.

| Texto atual | Onde no código | Problema | Proposta | Decisão |
|---|---|---|---|---|
| "mantem a cor" (subtítulo do Melhorar no painel) | `ui/tela_conferir.py:344` | Sem acento | "mantém a cor" | D-365 |
| "Não consegui gravar o arquivo. Verifique se ha espaço em disco." | `ui/tarefas.py:90` | Sem acento | "há espaço" | D-365 |
| "Conferir a pagina N" (Histórico) | `ui/tela_conferir.py:6505` | Sem acento (também está em `nm-historico`) | "página" | D-365 |

---

## 3. Detalhe sem pergunta (13) — fica anotado; vira pergunta se ele quiser

| Texto atual | Onde no código | Problema | Proposta | Decisão dele que toca |
|---|---|---|---|---|
| Subtítulos dos filtros: Automático "não mexe na página / tira o amarelado, arquivo pequeno / limpa o fundo e mantém as cores / cor viva e texto nítido" × painel "sem mexer / tira o amarelado / mantem a cor / cor viva" | `ui/automatico.py:83-87`; `ui/tela_conferir.py:342-347` | O mesmo filtro descrito de dois jeitos | igualar depois da resposta de `nm-limpar-a-folha` | — |
| "tudo certo" (contador) × "nada pendente" (painel) | `ui/tela_conferir.py:1463`, `:4419`; `ui/widgets/paineis.py:946` | Dois nomes para "nenhuma dúvida" | um só | D-285 (um número só) |
| "Página muito maior" × "Página bem maior que as outras" | `core/analise.py:314`, `:333` | Dois avisos com títulos quase iguais (tamanho do livro × margens iguais) | títulos que digam a diferença | D-320 |
| "Não parece dupla" | `core/analise.py:344` | "dupla" é palavra do programa | "Parece uma página só" | — |
| "usar em todas" (Dividir aplica direto; Cortar e Mover "usar em todas..." abrem a lista) | `ui/tela_conferir.py:1628`, `:1663`, `:1984`, `:2491`, `:2518` | Mesmo nome, comportamentos diferentes | é comportamento: a D-090 manda abrir a lista também no Dividir (dono: etapa 9) | D-090 |
| "Modo comparar" (menu Ver) × "antes / depois" (barra) × "Comparar com o Original" (tela cheia) | `ui/barra_de_menu.py:275`; `ui/tela_conferir.py:1095`; `ui/widgets/filtros_tela_cheia.py:263` | Três nomes para comparar | esperar `v-antes` (Central) | D-184 |
| "imprimir agora..." (Ficou pronto!) × "mandar para a impressora..." (Montar para imprimir) | `ui/tela_final.py:191`; `ui/dialogo_impressao.py:617` | Dois botões de imprimir com nomes diferentes (o PDF como está × a montagem) | — | D-325, D-552 |
| "fazer outro" (Ficou pronto!) | `ui/tela_final.py:205` | Não diz o quê (volta aos livros) | "voltar para os livros" | — |
| "Todos os núcleos do processador (N)" | `ui/tela_configuracoes.py:208` | Termo técnico | "O máximo que o computador aguenta (N)" | D-364 |
| Dica do "Gravar em duas camadas" com "(como uma foto JPEG de qualidade alta)" | `ui/janela_confirmar.py:121` | "JPEG" técnico (o nome da caixinha é aprovado) | tirar "JPEG" | D-304 |
| Dicas "Como o ScanTailor (filtro de Wiener): …" | `core/luz_scantailor.py:58-62` | "filtro de Wiener" técnico | tirar o parêntese | D-061 (`fr22`) |
| "variação" (Pegar tudo desta cor) × "tolerância" (Varinha) | `ui/widgets/barra_opcoes.py:147`, `:153`; `ui/widgets/trilha_agrupada.py:109`, `:111` | Duas palavras para o mesmo ajuste | uma só | D-205 |
| "Ainda tem N páginas que eu não tive certeza" / "as laranjas eu não tive certeza" | `core/avisos.py:303-304`; `ui/tela_conferir.py:3360`, `:3365`; `ui/widgets/tira_miniaturas.py:257` | Falta o "de" ("de que eu não tive certeza") | — | D-283 (janela aprovada) |

Também anotados, **não são de nome** (são de comportamento, já na lista única): "Ficou muito escura. Tente mais fraco na
força do preto." em página Mágico pro/Melhorar (`core/analise.py:371`; lista 1.2 e 5.9); "Esse tamanho é menor que o
corte que você já fez (16.2 × 21.0 cm)" com os números iguais (`ui/dialogo_tamanho_da_folha.py:135`; teste do Kaique,
tarefa 5).

---

## 4. Já na Central esperando resposta (não repeti)

- `b-abas-nomes` — nomes curtos das abas no jeito "Abas no alto" ("Revisar", "Automático", "Propriedades", "Filtro",
  "Histórico"; `ui/widgets/paineis.py:120-124`).
- `a-aviso-curto` — mensagem curta ao clicar "está certo".
- `a-contador-dividir` — o contador "N de M conferidas" no Dividir (folhas × páginas).
- `v-antes` — o "antes / depois" da barra de baixo.

---

## 5. Deixados de fora: nomes que ele já aprovou (31 grupos)

| Nome(s) | Onde aprovou |
|---|---|
| "Limpar a sujeira": Sem limpeza · Limpeza bruta · Limpeza cuidadosa leve/média/forte | D-366 (07/10, R10 501) |
| "Só as letras": Guardar a tinta forte · Guardar tudo · Guardar só o texto | D-366 |
| "aplicar em:" com "só esta folha / todas as folhas" (girar) e "só esta página / todas as páginas" (Endireitar) | D-367 (12/10) |
| "deixar como veio", "usar o ângulo do programa", "usar o corte do programa" | D-368 (12/10) |
| "ScanTailor +0,0° · Editor −0,2°", "a do ScanTailor / a do Editor", "o do ScanTailor / o do Editor", "Jeito de dividir", "Conta" | D-369, D-370, D-373 |
| "daqui em diante" | D-371 |
| "Livro novo: ainda não passou pelo automático.", "Rodar o automático…", "agora não" | D-005 (R13 804) |
| "Uma página", "Duas lado a lado", "Rolar sem parar", "Caber a página / a altura / a largura", "Tamanho real" | D-015, D-347 (`lyupdf`) |
| "PÁGINAS ˅ ••• ver todas"; "Todas as páginas" com "uma a uma / em pares" e "só as que precisam de atenção" | D-040, D-054, D-343, R14 901 |
| Menu "Painéis", "Fechar o painel", "Esconder os ícones da direita"; menu "Ferramentas" | D-057; D-562 |
| "Confirmar e processar" | D-050 |
| "Só nesta página" / "Para o livro todo" | D-051 |
| "Comparar com o Original"; "Filtros em tela cheia" | D-184; D-181/D-182 |
| "Por página / Por motivo" | D-265, D-266 |
| "Deixar em branco", "Tirar do livro" | D-046, D-269, D-271 |
| "Trazer de volta nesta página" | D-278, D-279 |
| "Desentortar aumentando a página", "Desfazer / Manter assim" | D-105, D-108 |
| "Ajustar o pedaço à figura"; "Mostrar as áreas achadas" | D-232, D-236; D-237 |
| "Este livro tem fotos"; "Esta página tem foto" | D-213 |
| "tinta preta, fundo original"; "cor como no livro / cor escurecida"; "papel branco / papel como o resto da página" | D-229; `tc23`, `tp23` (D-061) |
| "Tirar o fundo"; "Este livro tem fundo separado. Quer tirar o fundo?"; "Conferir o fundo tirado" | D-134, D-135, D-256 |
| Frase do aviso "Desenho ou escrita?" | D-281 |
| "Ficou pronto!" e a frase de montar em A4; "Falando com a impressora"; "Imprimir como imagem" | D-313, D-551; D-332; D-326 |
| "Margens iguais" (também no Cortar); "Usar esta receita no aviso de todo livro novo" | D-554; D-553 |
| Aviso das pares ("Você está numa folha ímpar…"); "Lombada incerta"; "o que está impresso fica CORTADO" | D-556; D-560; D-550 |
| Teclas D, X, I, F, Shift+Del | D-561 |
| "Ícones na borda / Sanfona (a área de trabalho 1) / Abas no alto / Painel solto" | D-033 (palavras dele) |
| "Receita" (palavra dele: "salvar como receita com nome e reusar") | decisão 2 do rascunho do layout (25/09) |
| Os dez "… do ScanTailor" do "Jeito do preto e branco" | D-176 ("Pôr no programa como está") |
| Nome do PDF pronto com acento ("… - mágico pro.pdf") | D-555 |
| "Gravar em duas camadas…" (a caixinha); os quatro filtros (Original, Preto e branco, Melhorar, Mágico pro); "Força do preto" | D-304 (`fr-210`); `CLAUDE.md` §1 |

Resolvido antes desta revisão: "Os quatro filtros" saiu da trilha na etapa 2 (lista 5.13); os nomes da Luz cortados
(lista 5.14) são de largura, já decididos em D-059 ("tem que sair inteiro os inscritos").
