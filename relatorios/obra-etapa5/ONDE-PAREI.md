# Obra de 26/10/2026 — etapa 5 (Mover e redimensionar como ferramenta própria): ONDE PAREI

Ramo `obra-etapa5-2026-10-26` (base `obra-2026-10-26` = `7fb3e4a`, com as etapas 1, 2, 3, 4, 9a, 9c e 10a),
worktree `.claude/worktrees/obra-etapa5`. Agente: layout + implementador. Ordem do Samuel (D-014): fazer até o fim sem
pausas; ele confere tudo no fim.

**Situação: começando** (27/10/2026).

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

- [ ] núcleo (folha, aviso, pipeline)
- [ ] visualizador
- [ ] ferramenta na tela (trilha, menu, letra, Propriedades)
- [ ] usar em todas + conferência por trás
- [ ] provas e testes antigos
- [ ] promessas, teste_botoes
- [ ] reversão, somas, prints, GitHub, ONDE-PAREI final

## Perguntas para o Samuel

(nenhuma ainda)
