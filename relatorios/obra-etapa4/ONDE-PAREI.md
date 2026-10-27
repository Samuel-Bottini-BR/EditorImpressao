# Obra de 26/10/2026 — etapa 4 (dividir à mão folha por folha): ONDE PAREI

Ramo `obra-etapa4-2026-10-26` (base `obra-2026-10-26` = `427e3ae`, com as etapas 1, 2, 3, 9a, 9c, 10a e a bateria de
promessas), worktree `.claude/worktrees/obra-etapa4`. Agente: layout + implementador. Ordem do Samuel (D-014): fazer até
o fim sem pausas; ele confere tudo no fim.

**Situação: em andamento** (começada em 27/10/2026).

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| Pedido da etapa 4 (sessão 1, 26/10, print `s1-10`) | "quando a tela está assim no dividir, é bom para mudar folhas que sairam erradas, eu posso entrar ali e mudar a marcação de folhas erradas, mas quando eu escolher para começar no automatico e dividir as folhas o livro tem que aparecer em uma pagina por vez para mim." | "dividir esta" sempre aceso (livro sem "Dividir", folha girada); dividir, não dividir e mover a linha mexem só nas páginas daquela folha, sem recomeçar e sem perder o feito nas outras; marca "mexida à mão". Promessa P-059. |
| D-007 (26/10) | a mesma frase acima | A folha inteira com a linha só dentro da ferramenta Dividir (para consertar); fora dela, livro dividido aparece uma página por vez. |
| D-080 (05/10) | G2: "(a) Só quando o Kaique pedir, livro a livro, escolhendo 'o do programa' ou 'o do ScanTailor', e trocando numa folha se um ficar ruim" · "Tem livros que não tem que dividir folha, e ai como faz? [...] se um ficar ruim, ele usa o outro." | Livro novo não divide; dividir à mão numa folha (etapa 4). |
| D-074 (24/09) | (paráfrase) dividir a folha sabendo quando é uma página só; bug "Righetti não girado nem dividido" (PD l.400) | Folha de uma página só não é dividida sozinha; o Righetti girado divide. |
| Lista única 3.1 (23/10) | "Não dá para girar o livro antes de dividir: livro escaneado de lado não divide" (trava o trabalho) | Girar o livro/folhas e então dividir, no Automático e à mão; a conta da lombada na folha girada. Prova no Righetti. |
| D-495 (27/10, escolha da gerente D-014) | "Righetti 96: a faixa preta da tampa do scanner sai quando a folha é girada e dividida à mão (dividir à mão, etapa 4), não por regra geral." | Righetti 96 girada e dividida à mão → sem faixa preta em cima no PDF; livro com moldura impressa preta não perde a moldura. |
| Bug da etapa 9c (27/10) | (Lista de bugs) "Dividir do ScanTailor erra no 'La vida eterna' (folhas 4 e 5): divide a 10% da largura, na linha vertical escura da beirada" | A linha escura da beirada do livro não é tomada por lombada. Teste de reversão. |
| D-016 (09/10) | `g6-endireitar-antes` + "Ordem obrigatória" | A montagem da página segue a ordem obrigatória (girar → dividir → endireitar → cortar); o dividir à mão não muda isso. |
| D-334 (24/09) | "Ver todas as páginas do livro em grade [...]: seleção múltipla, girar, apagar, extrair, inserir, dividir." | A grade continua; dividir em várias = "rodar o automático nelas" (ver ressalvas). |
| D-488 (27/10) | (escolha da gerente) a tela "O que fazer" sai do caminho | Nada do dividir leva de volta a ela. |
| D-489 (27/10) | (escolha da gerente) recomeço só quando o PDF mudou, o projeto.json não lê ou falta página | Dividir/não dividir à mão nunca recomeça; toda folha continua com página. |
| D-004 / D-009 | "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas mexidas." · "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo manualmente." | A divisão à mão grava a marca "mexida à mão" e vale no PDF com o Dividir do livro desligado. |
| D-046 | dois botões ("Deixar em branco" / "Tirar do livro") | Página tirada ou em branco não volta sozinha ao dividir/juntar. |

## Plano

1. Núcleo (`core/dividir_a_mao.py`, novo): dividir e juntar UMA folha mexendo só nas páginas dela (uma ação do
   desfazer, leve: só as páginas daquela folha); guardar as metades ao juntar e devolvê-las ao dividir de novo; achar a
   faixa da tampa do scanner na folha girada (D-495).
2. `historico_acoes`: a troca das páginas de uma folha (desfazer/refazer).
3. `core/pipeline`: a linha da beirada não é lombada (bug da 9c); a faixa da tampa pintada de branco na etapa
   "dividir".
4. Tela: "dividir esta" sempre aceso; D-007 (a folha inteira só no Dividir); avisos de folha.
5. Provas em `tests/test_decisoes_dividir.py`; promessa P-059; testes antigos.
6. Prints da janela de verdade com o Righetti; somas de fábrica; GitHub.
