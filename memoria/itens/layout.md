# layout — A obra do layout (tela "como o Photoshop")

Fase 4 · **etapas 1 a 3 no programa; rodadas 14 e 14b DECIDIDAS (20/10/2026); etapas 4 a 7 PRONTAS no ramo `layout-etapas4a7-2026-10-19` (`2eeec20`), nada juntado; aba 5 publicada, etapas 6-7 montadas e NÃO publicadas** · ficha montada em 20/10/2026 · o que manda: [PLANO-DEFINITIVO, Fase 4](../../docs/plano/PLANO-DEFINITIVO.md)

O item "Fase 4" do plano (atalhos editáveis "a aperfeiçoar") tem ficha própria: [4.md](4.md). Esta ficha é a obra
inteira do layout: o plano feito com o Samuel, as 13 rodadas de escolhas e as etapas já construídas.

## Situação

- **Atualização de 22-23/10/2026 ([PARTE -19](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)); vale sobre os pontos abaixo:** livro aberto como no UPDF e tela cheia **APROVADOS** (`lyupdf`); três melhorias (quadro azul `eae91cb`, "Antes de processar" `138e425` no ramo `layout-antes-de-processar-2026-10-22`, miniaturas lembradas `edc6143`) **APROVADAS** (`lm22`), entram depois da junção com o conserto do "Mostrar" cortado. Lista de espera: revisar os nomes de todos os botões com um agente novo; painel da aba Marcar bagunçado; ferramenta primeiro, forma depois (como no Photoshop).

- **Atualização de 22/10/2026 (tarde):** layout 6 e 7 aprovado; o agente de layout refaz o livro aberto como no UPDF e completa a tela cheia dos filtros (ver Registro 22/10/2026).

- **Atualização de 22/10/2026:** Etapas 4 e 5 aprovadas pelo Samuel em 21/10/2026; 22/10/2026: conferência das etapas 6 e 7 publicada na Central (aba Conferência > Layout 6 e 7). O layout 4 a 7 entra no programa na junção final.

- **Atualização de 21/10/2026 ([PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)); vale sobre os pontos de 20/10 abaixo:** ramo `layout-etapas4a7-2026-10-19` em **`2eeec20`**. **Etapas 4 e 5 PRONTAS**; a **aba 5** da página de conferência (layout etapas 4-5 + rodada 14, decisão `ly-4a5`) está **publicada, sem resposta**. **Etapas 6 e 7 PRONTAS**; conferência montada em `verif-layout-4a5-2026-10-21` (`5650a1c`), **não publicada**. A grade ficou nítida depois, em `2eeec20` (a suíte 39629275637 não foi lida e o verificador não mediu de novo). **Rodada 14 e 14b respondidas** em 20/10/2026 (abaixo). Nada juntado ao `fase-1`. A página de layout está com 500 arquivos (limite de 511 por versão).
- **No programa (`fase-1`):**
  - **Etapa 1, os três temas** (escuro, cinza, claro; cinza de fábrica): commit `7ebbc04`, juntado em 08/10/2026
    (merge `5ecc4dc`). Troca provisória em Ver > Tema.
  - **Etapas 2 e 3 + painel Propriedades + textos das rodadas 12 e 13:** aprovados pelo Samuel em 13/10/2026 na página
    de conferência (14 quadros "Está bom", decisão `layout3` "Aprovado") e juntados ao `fase-1` em 14/10/2026
    (`ccc84aa`, junção do ramo `juntar-layout3-2026-10-13`, `f35bcaf`; ramo de trabalho `layout-impl-2026-10-08`,
    último commit `e94fe8c`).
- **Em andamento hoje (20/10/2026):** o agente de layout liberado pelo Samuel em 19/10 ("Agente de layout - ok") trabalha
  no ramo `layout-etapas4a7-2026-10-19` (worktree `.claude/worktrees/layout-4a7`). O `ONDE-PAREI.md` dele
  (`ramo layout-etapas4a7-2026-10-19: relatorios/layout-4a7/ONDE-PAREI.md`, 20/10, 04:32) diz: "Tarefa 1: rodada 14 de
  perguntas — Situação: começando." e "Tarefa 2: etapas 4 a 7 — Situação: não começada."
- **Marca no plano:** a Fase 4 não tem itens numerados com marca; a única linha marcável é "[ ] Tela de Configurações
  com atalhos de teclado editáveis" (ver [4.md](4.md)). Nada da obra do layout está marcado `[x]` no plano; a aprovação
  de 13/10 está no Registro de mudanças.
- **Conferido pelo Samuel:** etapas 2 e 3 + Propriedades "Aprovado" (13/10/2026). A etapa 1 (temas) entrou no
  `fase-1` em 08/10 sem conferência própria ("Nada disso foi marcado `[x]`: cada item continua a conferir", Registro
  08/10/2026).

## O que vale hoje

**Regras da obra**
- Só o agente de layout mexe na tela (`ui/`), na própria cópia e no próprio ramo; quem junta é a gerente
  ([CLAUDE.md §10](../../CLAUDE.md); [.claude/agents/layout.md](../../.claude/agents/layout.md)).
- **"C — tudo livre, como o Photoshop"** é a **última parte** da Fase 4: primeiro o padrão funcionando, depois as
  trocas (rodada 3, 05/10: "A — primeiro o padrão funcionando, depois as trocas"; confirmação do Samuel em 05/10/2026:
  "confirmo"; Registro 05/10/2026).
- **Botão ou função nova entra com aparência provisória** e vai para a lista do agente de layout (conferência 15,
  06/10/2026, M1): "acho que você pode ir colocando os botões e as funcionalidades e depois eu resolvo com o agente de
  layout, mas é bom que seja listado tudo para o agente de layout para ele ter ideia desses botões e funcionalidades."
  Lista: `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\Botoes e funcoes para o layout.md` (fora do
  git; última mudança 06/10). Cada botão novo entra nela quando é juntado ao `fase-1`.
- **Fase 2 (regra de 13/10/2026):** "o botão vai para o lugar que o layout já decidido manda (painel Propriedades ou
  painel Filtro), sem rodada nova de perguntas" (PLANO-DEFINITIVO, Fase 2).
- Tela desenhada para **1280 × 657** (notebook do Kaique a 150%, o pior caso); janela mínima 1000 × 600.
- Quem decide: o Samuel, na página **"Layout do Editor de Impressão"** (https://claude.ai/artifact/QuzVaghq2tz2WVwJ1AyMWu);
  conferência das etapas na página de conferência (https://claude.ai/artifact/J8AwcyyUwrZ2n7kSevyGvX). Pergunta nova
  começa por "O que você está escolhendo:", texto curto, a parte que muda ampliada, sempre "Ainda não entendi"
  ([histórico, PARTE -15 §6](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)).

**A tela decidida** (tela-alvo: `prototipo\21-rodada13-base.html`, prints `imagens\21-rodada13-tela-decidida*.png`, na
pasta `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\`)
- Photoshop puro, **sem abas**; painel **Automático** no lugar da tela "O que fazer", com receitas, ordem livre
  arrastando e a pergunta de pular páginas mexidas à mão (decisões 1, 2, 2a, 2b de 25 e 28/09).
- Ao abrir: **ícones na borda direita, tudo fechado**, com seta; área de trabalho 1 como opção (R7 203 D). Painel
  **empurra a página** (R9 401 A).
- **Trilha de ferramentas agrupada** como no Photoshop, com a letra do atalho ao passar o mouse (R8 302 C); **barra de
  opções na linha dos menus** (R8 303 B), **só com o nome da ferramenta** e os ajustes (R12 702 C).
- **Miniaturas** com cabeçalho "PÁGINAS" (seta, três pontinhos, alça de arrastar), sem botões esquerda/direita (R7 204,
  205; R8 301 A); botão de "Todas as páginas" no cabeçalho delas (R13 808 A).
- **"Ver lado a lado"** sobre as páginas, canto direito, pares rolando — opção, não padrão (R7 201 B, 202 A; página de
  escolhas 06/10).
- **Propriedades conforme a ferramenta** (R9 402 C), com duas partes "Só nesta página" e "Para o livro todo" (R12 706 B),
  que **abre sozinho** ao escolher Cortar, Endireitar ou Dividir (R13 802 A).
- **Girar:** bloco no alto do Propriedades e botões pequenos no canto da página (R12 703, "Quero a opção  B e D"); a
  lista "aplicar em" só no painel; o canto gira só esta folha (R13 803 B).
- **Filtro:** fila de filtros + partes que abrem e fecham (R9 403 B); escolhas em **menu com amostra** (R10 502 B);
  **tela cheia** = "um grande" com a chave "Comparar com o Original", aberta pelo ícone no título do painel (R10 503,
  R11 601 A).
- **Nomes do conjunto 2** (R10 501 B): "Limpar a sujeira" = Sem limpeza · Limpeza bruta · Limpeza cuidadosa: leve ·
  média · forte; "Só as letras" = **Guardar a tinta forte** · Guardar tudo · Guardar só o texto.
- **Histórico** = botões + lista (R9 405 C). **"Para revisar"** com abas "Por página | Por motivo", abrindo sempre em
  "Por página" (R10 504 A; R11 602 A).
- **"Confirmar e processar"** ao lado das miniaturas (R12 704 A); desce para a barra de baixo, canto direito, quando as
  miniaturas estão fechadas ou de lado (R13 801 A).
- **"Ficou pronto!"** na janela inteira, como hoje (R12 708 A).
- **Nomes do Endireitar e Cortar:** "deixar como veio", "usar o ângulo do programa", "usar o corte do programa"
  (R12 710 B); listas "aplicar em" dizem folha ou página (R12 709 B); "daqui em diante" em todos (R13 806 B); a conta
  antiga do Endireitar se chama "Editor" (R13 805 C).
- **Configurações** com a lista das partes à esquerda (R13 807 B); tema no menu Ver e nas Configurações (R12 707 C).
- **Livro novo:** aviso embaixo da página convidando a rodar o automático (R13 804 B).
- **"Marcar como"** com cinco jeitos (R12 705 A): mexe no processamento, está na Lista de espera (12/10/2026) — ver
  [3.1.md](3.1.md).
- **Tela inicial:** cartões; cartão "+" no começo da grade (página de escolhas, 06/10); livro aberto em tela cheia com
  páginas rolando + coluna de miniaturas ("Sim, fica assim", 06/10).
- Cores de referência do handoff: fundo #1E1F22, painel #26282C, azul #2F6FE0, laranja de aviso #F0A55C.

**O que falta (decidido e não construído)** — fonte: `ramo layout-impl-2026-10-08: relatorios/layout-impl/ONDE-PAREI.md`
(13/10), seção "O que ainda falta"; a cópia em W é [relatorios/layout-impl/ONDE-PAREI.md](../../relatorios/layout-impl/ONDE-PAREI.md):
- **Etapa 4:** o resto do Propriedades (botões de Marcar: detectar, "Esta página tem foto", "Ajustar o pedaço à
  figura", "usar em todas", "daqui em diante") e o **painel Filtro** novo (R9 403 B) com os nomes do conjunto 2 e os
  menus com amostra; sai o botão provisório "Os quatro filtros".
- **Etapa 5:** miniaturas (cabeçalho "PÁGINAS", seta, três pontinhos, alça), com 801 A e 808 A.
- **Etapa 6:** tela cheia dos filtros (R11 601 A).
- **Etapa 7:** tela inicial.
- Decidido na rodada 13 e sem etapa: aviso de livro novo (804 B: só faz sentido quando o livro abrir direto na tela de
  trabalho, etapa 7); Configurações em partes com o tema (807 B + 707 C).
- Sem etapa marcada (para a gerente decidir): na barra de baixo, "antes / depois", o zoom "– 78% +" e "ajustar à tela".
  **Atualização de 27/10/2026:** feitos na etapa 6 da obra (ramo `obra-etapa6-2026-10-26`), junto do "Uma página /
  Duas lado a lado" da barra de baixo e do menu Ver (D-015, D-058); PRONTO PARA CONFERIR
  (`relatorios/obra-etapa6/ONDE-PAREI.md`).
- **Rodada 14 (perguntas a fazer):** qual vista de "Todas as páginas" vem de fábrica; onde se escolhe a "área de
  trabalho 1" e os quatro jeitos do menu da direita; a lista dos painéis no menu Ver e o resto dos menus; se o Dividir
  ("o do programa / o do ScanTailor") muda de palavra como a conta do Endireitar. Da PARTE -15 §4 item 8: o nome "o
  mesmo da página" e a frase nova do aviso "Confira na aba Marcar".
- Pendências sem dono achadas na conferência de 12/10/2026 (Registro): receitas, ordem arrastando e "pular as páginas
  mexidas" do Automático; tela inicial sem barra de menus; onde se escolhe a área de trabalho 1.
- Os três controles do retângulo do corte do G6 (Configurações, livro, página: "quero a b e c juntas.", 09/10/2026)
  "entram depois da etapa 2 do layout" (Registro 09/10/2026) e ainda não existem na tela (Registro 12/10/2026).

**Rodada 14 (20/10/2026), decididas:** `r14-todas-fabrica` "A — Uma a uma"; `r14-lado-direito-onde` "C — Nos dois lugares"; `r14-menu-paineis` "B — Um menu novo, “Painéis”"; `r14-menus-novas` "A — Sim, no menu Ver"; `r14-aviso-marcar` "C — Diz onde fica o “letra e traço”"; `r14-dividir-palavra` "B — “o do Editor”".

**Rodada 14, sem opção, com comentário** (fixado na página; perguntas refeitas pelo agente de layout): `r14-mesmo-da-pagina` "Ainda não entendi" + "ficou muito confuso, por favor explique melhor. Não seria mais fácil só usar o original ?"; `r14-endireitar-a-mao` "não gostei de nenhuma opção. e mesmo que coloque a mão tem que continuar aparecendo o angulo".

**Rodada 14b (20/10/2026), decididas:** `r14b-mesmo-da-pagina` "B — Sem o botão de cima, nenhum aceso"; `r14b-endireitar-a-mao` "A — Os dois ângulos e, embaixo, o seu", com o comentário: "a opção 1, podia aparecer só na hora que passasse o mouse em cima, os angulos continuam embaixo mas a mensagem só aparece quando bota o mouse em cima".

**Lição de tela (PARTE -17 §4):** no Qt com a escala do Windows em 125%, imagem guardada no tamanho certo e pintada com `pix.scaled(tamanho lógico)` fica borrada; é preciso reduzir nos pixels de verdade (`razao_do_pintor`). O teste tem de medir o que é **pintado**.

## Mudou em

- 25/09/2026 — antes: abas por etapa + trilha e painéis ao mesmo tempo → ficou: "Photoshop puro, sem abas" (decisão 1
  do rascunho de layout); tela "O que fazer" → painel Automático (decisão 2).
- 28/09/2026 — antes: tema a escolher → ficou: tema escolhível (decisão 3); rodadas por bloco e 5 etapas (decisão 6).
- 05/10/2026 — antes: "o Cowork faz os HTMLs" (decisão 7 do rascunho) → ficou: o agente de layout no Claude Code faz os
  HTMLs e mostra ao Samuel (handoff de 05/10; Registro 05/10/2026).
- 05/10/2026 — antes: formulário `ABRA-AQUI.html` com "Copiar minhas respostas" → ficou: página do claude.ai com banco
  de dados (pedido do Samuel na rodada 6: "esse arquivo html está cheio de coisa, não está organizado está acumulando
  respostas, isso precisa ser salvo em outro lugar"); em 06/10 a página só do layout ("porque o agente de layout não me
  mandou mais nada para escolher, podemos ter um artefato só para o layout?").
- 07/10/2026 — antes: "Guardar o que é escuro" (conjunto 2) → ficou: **"Guardar a tinta forte"** ("guardar tinta forte
  estava bom ao invez de guardar o que é escuro, mude esse.", rodada 10).
- 12/10/2026 — antes: a rodada 12 de 09/10 (sessão na nuvem) com fotos do programa no meio da obra → ficou: rodada 12
  refeita na tela decidida, depois da queixa "cade o layout que tinhamos feito novo, as perguntas do layout estão
  usando o layout antigo, e nós já tinhamos feito varias escolhas, da uma olhada." (Registro 12/10/2026). Nas
  perguntas 701, 706 e 708 as letras das opções mudaram de sentido.
- 12/10/2026 — antes: R12 recomendava "Propriedades só com a página" (706 A) e girar na barra de baixo (703 C) → ficou:
  706 B (duas partes) e 703 B + D.
- 12/10/2026 — a conferência da etapa 2 (aba 2 da página de conferência) foi dada por desatualizada ("no relatorio do
  editor de impressão tem uma aba do layout que eu acredito que não esteja atualizada com as escolhas passadas") e
  trocada pela conferência da etapa 3 (13/10).
- 13/10/2026 — leitura da gerente, mostrada na conferência e não contestada: a lista "Conta" passou a dizer "a do
  Editor" também no painel Automático, no Histórico e na tela "O que fazer" (a escolha 805 C era só sobre a linha dos
  dois ângulos).

- 20/10/2026 — antes: rodada 14 "ainda não feita"/"não publicada" → ficou: publicada (8 perguntas `r14-*`) e respondida; 6 decididas, 2 sem opção e refeitas como rodada 14b, que também foi respondida no mesmo dia.
- 20/10/2026 — antes: telas clicáveis das rodadas 7, 8 e 9 na página de layout → ficou: fora da página (limite de 511 arquivos; originais em `layout\prototipo\`). A [PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §3 diz rodadas 7 a 10; o Registro diz 7, 8 e 9: não conferi qual está certa.

## Tentado e descartado

- Abas por etapa (After Effects) e dois modos simples/completo: recusados em 25/09 (decisão 1 do rascunho).
- Tela inicial: as quatro primeiras (telas 1 a 4) recusadas; as telas 6 e 7 da rodada 4 "Não gosto" (só a página vazia
  da 6 e o painel aberto da 7 ficaram); proposta 3 da rodada 6 "Não gosto" (rascunho, rodadas 4 a 6).
- Menu da direita em sanfona: "não agradou, principalmente o 'Para revisar'" (rodada 1, 05/10).
- Botões "esquerda/direita" das miniaturas: "ocupam espaço desnecessario" (R7 204).
- Nomes "o nosso" e "limpar pontinhos": o Kaique não entende (R9 404; histórico PARTE -12 §4).
- Opções da rodada 12 tiradas por contradizer o decidido (fila do Cortar por baixo do painel; "continua só na tela O que
  fazer"; "O que fazer só na primeira vez") — rascunho, "Opções da rodada 12 que saíram".
- Publicar conferência sem comparar as fotos com as escolhas: a aba da etapa 2 saiu desatualizada; agora um conferente
  abre todas as fotos contra as decisões antes de publicar ([histórico, PARTE -15 §5](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)).
- Perguntas sem imagem de cada opção: ele não entende (PARTE -13 §4).

- **Pôr as 53 fotos da rodada 14 na página de layout sem tirar nada** (20/10/2026): o limite é de **511 arquivos por versão**; saíram as telas clicáveis já decididas (PARTE -17 §3).
- **Imagem guardada no tamanho certo e pintada com `scaled(tamanho lógico)`** no Windows a 125%: fica borrada (ver "O que vale hoje").

## Ramos e commits

| Ramo / commit | Data | O que fez | No `fase-1`? |
|---|---|---|---|
| `7ebbc04` (ramo `layout-impl-2026-10-08`), merge `5ecc4dc` | 08/10/2026 | Etapa 1: três temas, cinza de fábrica | sim |
| `62d01e8`, merge `d5b562d` (ramo `nomes-rodada10-2026-10-07`) | 07–08/10/2026 | Nomes da rodada 10 na tela ("Limpar a sujeira", "Guardar a tinta forte"…); códigos do projeto não mudam | sim |
| `a783bd9` | 09/10/2026 | Etapa 2: tela de trabalho sem abas, trilha agrupada, opções na linha dos menus, faixa do conferir, barra de baixo | sim (via `ccc84aa`) |
| `6c54817`, `84871de` | 12–13/10/2026 | Etapa 3: coluna de ícones e painéis; Propriedades | sim (via `ccc84aa`) |
| `35eb5a6`, `e94fe8c` | 13/10/2026 | Acertos de 13/10 ("a do Editor", um girar só no Dividir, três textos de `core/analise.py` autorizados pela gerente) | sim (via `ccc84aa`) |
| `f35bcaf` (ramo `juntar-layout3-2026-10-13`) | 13/10/2026 | Junção numa cópia; suíte no GitHub rodada 38469423649: success | sim |
| `ccc84aa` | 14/10/2026 | Layout juntado ao `fase-1` | sim |
| `a1d796c` (ramo `layout-etapas4a7-2026-10-19`) | 20/10/2026 | Começo do ONDE-PAREI da rodada 14 e etapas 4 a 7 | **não** (em andamento) |

Pasta dos desenhos e respostas (fora do git): `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\`
(`Plano de layout (rascunho).md`, cópia anterior `...antes-2026-10-12.md`, `prototipo\`, `imagens\`, `rodadaN-escolhas.json`,
`respostas-rodada12-2026-10-12\`, `banco-antes-2026-10-12\`, `ABRA-AQUI*.html`). Fontes das páginas do claude.ai:
[docs/plano/para_a_pagina_de_layout.py](../../docs/plano/para_a_pagina_de_layout.py) e `docs/plano/paginas-claude-ai/`.

- `layout-etapas4a7-2026-10-19`: **`2eeec20`** (21/10/2026; a grade nítida). Verificação `verif-layout-4a5-2026-10-21` `5650a1c`. Nada juntado ao `fase-1`.

## Testes que cobrem

Testes de tela (rodam sem janela, `tests/conftest.py`):
- [tests/test_paineis.py](../../tests/test_paineis.py) (33) e [tests/test_paineis_na_tela.py](../../tests/test_paineis_na_tela.py)
  (21): coluna de ícones, painéis, Propriedades.
- [tests/test_trilha_agrupada.py](../../tests/test_trilha_agrupada.py) (16; inclui as setinhas que mudam com o tema),
  [tests/test_trilha_e_opcoes.py](../../tests/test_trilha_e_opcoes.py) (ainda testa a trilha antiga: Lista de bugs, 09/10/2026).
- [tests/test_girar_na_tela.py](../../tests/test_girar_na_tela.py), [tests/test_endireitar_na_tela.py](../../tests/test_endireitar_na_tela.py),
  [tests/test_dividir_na_tela.py](../../tests/test_dividir_na_tela.py), [tests/test_barra_de_menu.py](../../tests/test_barra_de_menu.py),
  [tests/test_misto_na_tela.py](../../tests/test_misto_na_tela.py), [tests/test_opcoes_da_gravura_na_tela.py](../../tests/test_opcoes_da_gravura_na_tela.py),
  [tests/test_janela_cabe_na_tela.py](../../tests/test_janela_cabe_na_tela.py) (janela cabe a 150%), [tests/test_tela_inicio.py](../../tests/test_tela_inicio.py).
- Clique de verdade: [teste_botoes.py](../../teste_botoes.py) (221 ações, 0 falhas em 13/10 no ramo) e o roteiro de
  prints da janela real (`saida_teste/prints_etapa3.py`, fora do git: 49 de 49 e depois 51 de 51).
- Testes de reversão dos bugs de tela de 13/10 (regra de 19/10/2026, CLAUDE.md §4.7): **não achados** (nenhum desses bugs
  foi consertado ainda).

- Suíte do GitHub 39629275637 (grade nítida, `2eeec20`): **não lida**; o verificador não mediu de novo a nitidez ([PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §2).

## Velocidade medida

- Etapas 2 e 3 juntadas, PC do Samuel, Marial de 300 folhas, 3 rodadas alternadas de cada (14/10/2026): **ficou igual**
  — abrir 55,2 → 55,6 s; trocar de página 2,36 → 2,31 s; Mágico pro 10 páginas 57,0 → 55,2 s; Preto e branco 26,0 →
  26,4 s; mesmo PDF de saída ([relatorios/velocidade-layout3-2026-10-14/velocidade.html](../../relatorios/velocidade-layout3-2026-10-14/velocidade.html)).
  Ressalva: memória livre mínima baixada de 3 para 2,5 GB para começar.
- Etapa 1 (temas): não medida à parte (entrou no `fase-1` de 08/10, suíte 1960 passaram).

## Páginas de teste e livros

- O protótipo usa o [Boécio](../livros/boecio.md), página 5, como livro de exemplo em todas as telas-base.
- Os prints da etapa 3 foram tirados numa cópia do Boécio (ONDE-PAREI do ramo `layout-impl-2026-10-08`).

## Conferências

- Rodadas 1 a 6 (05/10/2026): respondidas no `ABRA-AQUI.html` e copiadas literais no rascunho.
- Rodadas 7 a 13 (06 a 12/10/2026): página de layout, literais no rascunho.
- **Etapa 3 + Propriedades (13/10/2026): "Aprovado"**, 14 quadros "Está bom", quatro comentários
  ([relatorios/conferencia-samuel-2026-10-13.md](../../relatorios/conferencia-samuel-2026-10-13.md)):
  - `layout3-filtros`: "o que é  " o mesmo da página?""
  - `layout3-historico`: "a gente poderia mostrar o horario que a ação foi feita ou desfeita." (foi para a Lista de
    espera, 13/10/2026)
  - `layout3-janela-pequena-e-temas`: "não entendi porque a primeira está com tema escuro e no propriedades tem
    endireitar e na terceira foto o tema escuro está com propriedades e não tem o endireitar - qual é a versão final,
    não entendi. o propriedades é referente a ferramenta que está sendo usada?"
  - `layout3-para-revisar`: "no por motivo, quando eu aperto no motivo, vai abrir as abas com as paginas dentro dele?"
  Os quatro foram respondidos na própria página.
- Ver também [../conferencias.md](../conferencias.md).

- 20/10/2026 — rodadas 14 e 14b (página de layout), respondidas; ver [conferencias](../conferencias.md).
- 21/10/2026 — aba 5 (layout etapas 4-5 + rodada 14, decisão `ly-4a5`) publicada, **sem resposta**; etapas 6-7 montadas, não publicadas.

## Perguntas abertas

- **[Respondida em 20/10/2026 — atualização de 26/10/2026, etapa 0:]** as rodadas 14 e 14b foram publicadas e
  respondidas em 20/10 (901 A, 902 C, 903 B, 904 A, 906 C, 907 B, 909 B, 910 A; rascunho do layout, "Rodada 14 —
  respostas" e "Rodada 14b — respostas"; Livro de decisões `docs/plano/DECISOES.md`). Texto antigo:
  Rodada 14 (ainda não publicada em 20/10/2026): as quatro do fim do rascunho (vista de fábrica de "Todas as páginas";
  área de trabalho 1 e os quatro jeitos do menu da direita; menus e lista dos painéis no menu Ver; palavra do Dividir).
- Para a gerente decidir: em que etapa entram "antes / depois", o zoom e "ajustar à tela" na barra de baixo.
- Escala do notebook do Kaique (125% ou 150%): "Isso pode ser resolvido depois" (Samuel, 05/10/2026; Registro 05/10/2026).
- Frase nova para o aviso de `core/analise.py` "Confira na aba Marcar - se for escrita, marque como letra." ("a decidir
  com o Samuel", Lista de bugs 13/10/2026).

- (21/10/2026) Decisão `ly-4a5` da aba 5, sem resposta.
- No chat, sem resposta: "O programa deve **lembrar** onde você deixou as miniaturas (lugar, abertas, em pares) de um livro para o outro?" ([PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §5).

## De onde veio

- Plano de 24/09/2026, seção 3 ("Layout em paralelo: a Fase 1 roda no Claude Code enquanto o Samuel discute o plano do
  layout numa conversa separada no projeto do claude.ai") e Fase 4 ([PLANO-DEFINITIVO](../../docs/plano/PLANO-DEFINITIVO.md)).
- Conversa de layout no claude.ai, de 25/09 a 28/09/2026, e no Cowork até 05/10 (rascunho, "O que foi conversado").
  Inventário de telas de 02/10: [relatorios/layout-inventario-2026-10-02/inventario-telas-e-funcoes.md](../../relatorios/layout-inventario-2026-10-02/inventario-telas-e-funcoes.md).
- **Handoff de 05/10/2026** (só leitura, fora do git):
  `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\HANDOFF para o Claude Code - layout (05-10-2026).md`.
- **Rascunho com as rodadas 1 a 13** (só leitura, fora do git): `...\layout\Plano de layout (rascunho).md`.
- Lista de espera (seção 6 do plano), ideias de layout: 24/09/2026 "Ver todas as páginas do livro em grade, como o
  'Organizar páginas' do UPDF" e "Layout limpo como o do UPDF" (imagens em [docs/plano/referencias-layout/](../../docs/plano/referencias-layout/updf-tela-de-leitura.jpg));
  29/09/2026 cartões e "comparar" mostrarem o "Tirar o fundo" (Fase 4) e "Tirar o fundo" no menu Filtro (Fase 1 ou 4);
  30/09/2026 pergunta do fundo dentro do programa (Fase 1 ou 4); 05/10/2026 "Para o layout" (G1 e PADRAO); 06/10/2026
  lista de botões e funções; 12/10/2026 "Marcar como" com iluminura e moldura (etapa 4, Propriedades); 13/10/2026
  horário no Histórico.
- Lista de bugs de tela de 13/10/2026 (agente de layout e verificador): Menu Ver > "Painel: …" sem efeito; "Conferir a
  pagina 5" sem acento e nomes antigos no Histórico; Zoom com "%" sem número; "Só neste pedaço" sem proteção num livro
  sem as ferramentas de marcar; aviso "Confira na aba Marcar"; no Endireitar a linha da conta some sem explicação; em
  1280×657 o nome do filtro fica por cima da miniatura. De 09/10/2026: `test_trilha_e_opcoes.py` testa a trilha antiga;
  "retangulo" sem acento na faixa do Cortar (consertado na etapa 3). De 12/10/2026: "mantem a cor" sem acento.
- Histórico: [PARTE -11 §2, PARTE -12 §3, PARTE -13 §3, PARTE -15 §3 e §4 item 8/8a, PARTE -16 §1](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md).
- **Registro de mudanças:** 25/09/2026 (Configurações/atalhos "a aperfeiçoar" na Fase 4); 05/10/2026 (respostas do
  checkpoint de 03/10: escala do notebook "Isso pode ser resolvido depois"; handoff do layout; "C — tudo livre"
  confirmado); 06/10/2026 (conferência 15, regra dos botões; "Como abrir um livro novo?"; "O livro aberto fica
  assim?"; ramo `pedaco-e-salvo-2` com os botões listados; rodadas 7 e 8; rodada 9; regra das páginas que salvam e
  abrem sozinhas); 07/10/2026 (rodadas 10 e 11); 08/10/2026 (`fase-1` com os nomes da rodada 10 e a etapa 1; "Tudo no
  GitHub", `layout-impl-2026-10-08`); 09/10/2026 (sessão na nuvem, etapa 2 terminada; `g6-retangulo-onde`, os três
  controles depois da etapa 2); 12/10/2026 (rodada 12 refeita; respondida; toda decidida; rodada 13 publicada; agentes
  postos a trabalhar; rodada 13 decidida; conferência da etapa 2 desatualizada); 13/10/2026 (etapa 3 PRONTA PARA
  CONFERIR; layout APROVADO; suíte da junção passou; regra da Fase 2 sobre o lugar dos botões); 14/10/2026 (layout
  JUNTADO, velocidade igual); 19/10/2026 (agente de layout liberado: "rodada 14 e etapas 4 a 7 do layout").

- 20/10/2026 — Registro "Layout, rodada 14" e "Conserto do corte ... JUNTADO" (rodada 14b); 21/10/2026 — Registro "Pausa pedida pelo Samuel"; [PARTE -17](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) §2, §3, §4, §5.
