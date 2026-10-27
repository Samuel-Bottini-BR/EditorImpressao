# Obra de 26/10/2026 — etapa 5 (Mover e redimensionar como ferramenta própria): ONDE PAREI

Ramo `obra-etapa5-2026-10-26` (base `obra-2026-10-26` = `7fb3e4a`, com as etapas 1, 2, 3, 4, 9a, 9c e 10a),
worktree `.claude/worktrees/obra-etapa5`. Agente: layout + implementador. Ordem do Samuel (D-014): fazer até o fim sem
pausas; ele confere tudo no fim.

**Situação: PAUSADO** (27/10/2026) — ver a seção "PAUSA" abaixo.

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| Pedido da etapa 5 (sessão 1, 26/10, 1-7 e 1-9) | "essa folha eu não precisava endireitar ela, eu precisava conseguir mover ela dentro da area branca e redimensionar." · "mover deveria se poder fazer sem ter que ir em cortar bordas e poder ser feito como é no photoshope, que você arrasta a hora que quiser e aumenta a hora que quiser. a ferramenta de mover não deveria estar vinculada ao corte de bordas, deveriam ser duas coisas independentes" | Ferramenta "Mover e redimensionar" própria na trilha, sempre ativa; sem tamanho de folha a área branca é a própria página; arrastar move, puxar um canto aumenta/diminui mantendo a proporção; atalho de letra e item no menu Ferramentas; grava a marca "mexida à mão". |
| D-008 (22/09 e 26/10) | "quero conseguir redimensionar o conteudo tambem" · "a ferramenta de mover não deveria estar vinculada ao corte de bordas, deveriam ser duas coisas independentes" · "como é no photoshope, que você arrasta a hora que quiser e aumenta a hora que quiser" · `fr-24` (22/10): "Mas se eu quiser redimensionar isso dentro do programa eu vou conseguir né?" | Mover e redimensionar o conteúdo: ferramenta própria, sempre ativa, e o resultado sai no PDF. Prova: mover e aumentar sem escolher tamanho de folha → PDF com o conteúdo no lugar e no tamanho novos. |
| Teste do Kaique (26/10, tarefa 5) | "O texto dessa página está deslocado; quero mover ele para o meio da folha e aumentar um pouco." → não conseguiu: o "Mover conteúdo" não chegou ao PDF (margens 15 × 53), o retângulo não passa da borda e o texto não aumenta, sem "centralizar". | O que a tela mostra = o que sai no PDF; aumentar aumenta de verdade; botão Centralizar. Teste de reversão. |
| D-473 (escolha da gerente, apoiada em D-066: "precisamos que o pdf saia que nem está na tela") | "Tela e PDF saem da mesma conta [...] Tela e PDF diferentes é defeito, nunca escolha." | A ferramenta Mover mostra a página composta pela mesma conta do PDF (`core/folha.compor_na_folha` com a marca mexida à mão); posição e tamanho medidos no PDF batem com a tela. |
| D-017 (escolha da gerente, D-014, sobre G10 05/10 e `g10-ajustar-todas` 13/10) | G10: "(b) Avisar e não reduzir - avisar para eu reduzir manualmente, e ter uma opção para passar isso para todas as folhas, porque eu posso cortar uma folha ou as vezes diminuir o conteúdo que tem dentro dela. [...] então isso ai não pode interferir nisso." | Aumentar além da beirada não corta nada escondido: a página fica do mesmo tamanho, o que passa da beirada aparece marcado na tela e a página ganha aviso no "Para revisar" ("parte do que está impresso vai ficar de fora"). O programa não reduz sozinho. |
| D-303 (12/09) | "o programa tem que conseguir perceber quando aumentar margem do lado direito e do lado esquerdo" · "precisamos centralizar" | Botão "Centralizar" (o impresso no meio da área branca, nas duas direções). (A costura par/ímpar é da impressão, já feita.) |
| D-056 `g8-guias` (13/10) + D-025 | "As duas" + "Mas ele vai poder tirar a automatica a hora que ele quiser." · "a Etapa 5 leva as guias à ferramenta Mover" | Na ferramenta Mover: linhas de apoio à mão (botão direito; valem no livro todo) e automáticas (meio e beiradas), com caixinha para desligar. |
| D-314 (14/10) | "1. Na edição — Cada página ocupa a folha inteira. [...] (Mexer na escala do conteúdo — aumentar/diminuir — também existe aqui dentro, mas na prática só vou me preocupar com isso na hora de imprimir.)" | O mover/aumentar é da edição, por página; formato e margens da encadernação continuam só em "Montar para imprimir". Sem tamanho de folha, a página não muda de tamanho. |
| G10 (05/10) + D-090/D-091 | "ter uma opção para passar isso para todas as folhas" · D-090: "usar em todas" abre a lista das páginas com as exceções desmarcadas e nunca apaga exceção · D-091: "'Selecionar todas' e 'Nenhuma'" | "usar em todas..." na ferramenta Mover, com a janela "Em quais páginas?" (as páginas já mexidas vêm desmarcadas). |
| D-016 (09/10) | `g6-endireitar-antes` + "Ordem obrigatória" | A montagem continua endireitar → cortar → filtro; o mover vem depois (a página pronta é que anda). |
| D-001 (25/09) | "Estrutura: Photoshop puro, sem abas. Uma única tela com todas as ferramentas." | A ferramenta nova está sempre na trilha e no menu Ferramentas, em qualquer livro. |
| D-041 / D-042 / D-048 | "Agrupadas, como no Photoshop" + "quando eu passar em cima da agrupada tem que mostrar a letra dela de atalho." · barra na linha dos menus, só o nome | Balão com nome, letra e o que faz; a linha dos menus diz o nome. |
| D-044 / D-051 / D-052 | Propriedades "Muda conforme a ferramenta (como no Photoshop)", "Só nesta página"/"Para o livro todo", "Abre sozinho" | Os botões do Mover no painel Propriedades, que abre ao escolher a ferramenta. |
| D-481 (escolha da gerente) | "Atalhos de letra: D = Dividir, X = Cortar, I = Endireitar" | Uma letra livre para o Mover, remapeável nas Configurações. |
| D-004 / D-485 / D-009 | "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas mexidas." · "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo manualmente." | Mover grava a marca "mexida à mão" (MOVER) e vale no PDF com tudo do automático desligado. |
| D-019 / D-043 | "NÃO usar setGeometry, move() nem widget flutuando sobre o visualizador." · "Empurra a página" | O aviso do Mover fica no painel e na faixa de baixo, nunca por cima da página. |
| D-068 | "Toda função automática tem botão de ligar e desligar." | O ímã das linhas automáticas tem caixinha. |
| D-329 (`b-2-margens-na-tela`) | "Sim, a tela mostra igual ao que sai (recomendado)" | Com as margens iguais ligadas, a área branca do Mover já mostra as margens, como no PDF. |
| D-010 | "eu acho que o botão tem que ser provado que ele faz o que se diz que se faz, e não só se ele muda algo na tela." | Promessa escrita e prova de cada botão novo (`tests/promessas/promessas.md`). |
| D-020 | "Ctrl+Z desfaz qualquer alteração" | Cada arrasto, cada "Centralizar" e cada "usar em todas" é uma ação do desfazer. |

## PAUSA (27/10/2026, pedido da gerente) — onde parei

**Situação: em andamento (pausado).** Nada de processo meu aberto (o roteiro dos prints fechou a janela com WM_CLOSE).

### Feito (commits no ramo, enviados)
- Ferramenta própria "Mover e redimensionar" (trilha, menu Ferramentas, tecla F, Propriedades: área branca, "tamanho da
  folha...", Tamanho do conteúdo %, Centralizar, voltar como veio, usar em todas..., linhas de apoio). "Mover conteúdo"
  saiu do Cortar. Sem folha, a área branca é a própria página. Arrastar passa da beirada (o meio fica dentro); canto
  aumenta até 4x. Parte de fora marcada em vermelho (D-017), aviso `impresso_de_fora` na tela, na conferência por trás do
  "usar em todas" e no PDF (`core/pipeline.anotar_o_impresso_de_fora`). Livro: D-540 a D-546.
- Conserto achado nos prints: `ui/widgets/editor_selecao.py` chamava `evento.matches(Qt.Key_Z)` (PySide6 6.11 recusa):
  qualquer letra com o foco na página de marcar dava "problema inesperado". Teste de reversão
  `test_letra_f_com_o_foco_na_pagina_de_marcar_chega_a_ferramenta`.
- Provas: `tests/test_decisoes_mover.py` 13 passam; reversão no código antigo (7fb3e4a): todos falham, e o caso do
  Kaique pelo caminho antigo "NAO ANDOU" (`relatorios/obra-etapa5/reversao-no-codigo-antigo.txt`).
- Testes no PC (um por vez), todos passam: test_decisoes 23, _automatico 24, _dividir 19, _impressao 22, _nucleo 36,
  _tela 35, trabalho_nao_se_perde 82, visualizador 70, previa_composta 10, paineis_na_tela 22, corte_pelo_conteudo_na_tela
  13, guias 14, folha 20, trilha_agrupada 19, trilha_e_opcoes 29, pipeline_folha 7, core 62, substituir_e_cancelar 21,
  dialogo_tamanho_da_folha 5, menu_paineis 3, paineis 34, editor_selecao 17. Promessas (-k mover/conteudo/centralizar…):
  falham só P-085 e P-127 (defeitos já conhecidos da base) e P-094 (passa sozinha; ordem). teste_botoes: 331 ações, 0
  falhas. Somas "Desligado de fábrica": 96 de 96 iguais (`somas-antes-7fb3e4a.json` × `somas-depois.json`).
- GitHub 40559025254 (commit 709abac): partes 2-5 e botões passam; parte 1 só P-085 e P-127 (as da base).

### Falta (próximo passo exato)
1. **O último ajuste da caixa do impresso (`core/folha.caixa_do_impresso` por blocos, `BLOCO_DO_IMPRESSO`/`MENOR_BLOCO`)
   ainda NÃO foi commitado antes desta pausa — vai neste commit.** Os prints mostraram, na página 7 do "La vida eterna",
   "Centralizar" a 104%: no PDF esquerda 0,035 × direita 0,151, cima 0,129 × baixo 0,044 (régua: a mesma
   `caixa_do_impresso` na página do PDF). **Investigar**: a conta na tela (prévia 110 DPI, `_mover_da_vez["caixa"]`) dá
   desloc. (-0,169; +0,106) e pelo PDF parece andar demais (desconfio do `_caixa_do_mover` guardado por `id(img)`:
   pode ser a caixa de antes do ajuste, ou de outra prévia; ou o retângulo gravado contra outra área). Rodar
   `_tmp/dbg.py` e o roteiro `relatorios/obra-etapa5/roteiro/prints.py <worktree> depois`; depois rodar de novo
   `tests/test_decisoes_mover.py`, `tests/test_folha.py`, `tests/test_promessas.py -k "p19 or p035"`.
2. Prints "antes" (código antigo: `prints.py <worktree>/_tmp/antigo antes`) e abrir todos os prints.
3. Nova rodada do GitHub depois do item 1.
4. ONDE-PAREI final ("Como cumpri cada uma", perguntas, ressalvas) em 3 formatos (`relatorio.gravar`).

### Ressalvas já vistas
- Com o foco na lista do Automático, as letras (D, X, I, F) vão para a lista (igual para todas as ferramentas).
- As outras ferramentas mostram a página sem o mover (D-546); o resto da D-473 é da etapa 10.
- A letra que já estava cortada na beirada da página não conta para o aviso do D-017 (peças coladas na beirada saem).

## Plano

1. `core/folha.py`: contas em pontos (área branca = página quando não há folha), a caixa do impresso, o que fica de
   fora, o deslocamento para centralizar. `core/analise.py`: aviso novo. `core/pipeline.py`: o aviso no PDF.
2. `ui/widgets/visualizador.py`: o modo Mover desenha a área branca e a página por cima dela ao vivo, com a parte de
   fora marcada; arrastar não prende na beirada, aumentar passa da beirada; o ímã olha o impresso.
3. Trilha, menu Ferramentas, letra; `ui/tela_conferir.py`: a ferramenta Mover com o Propriedades (área branca,
   tamanho em %, Centralizar, voltar como veio, usar em todas, linhas de apoio); o "Mover conteúdo" sai das Bordas.
4. Provas em `tests/test_decisoes_mover.py` (comportamento + PDF medido), testes antigos que provavam o comportamento
   que saiu reescritos, promessas, teste_botoes, somas, prints, GitHub.

## Passos

- [x] núcleo (folha, aviso, pipeline)
- [x] visualizador
- [x] ferramenta na tela (trilha, menu, letra, Propriedades)
- [x] usar em todas + conferência por trás
- [x] provas e testes antigos
- [ ] promessas (escritas), teste_botoes
- [ ] reversão, somas, prints, GitHub, ONDE-PAREI final

## Perguntas para o Samuel

(nenhuma ainda)
