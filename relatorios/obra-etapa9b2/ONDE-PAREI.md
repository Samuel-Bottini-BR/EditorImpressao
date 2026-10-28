# Obra de 26/10/2026 — etapa 9b-2 (a área de trabalho): ONDE PAREI

Ramo `obra-etapa9b2-2026-10-26` (base `obra-2026-10-26` = `27b4c52`), worktree `.claude/worktrees/obra-etapa9b2`.
Agente: layout + implementador. Ao mesmo tempo, a etapa 9b-1 mexe em menus, impressão e janelas
(`ui/janela_principal.py`, `ui/barra_de_menu.py`, `ui/dialogo_impressao.py`, `ui/janela_confirmar.py`,
`ui/widgets/paineis.py`, `modelos.nome_de_saida_sugerido`): evito esses arquivos.

Regra 7 (Samuel, 27/10/2026): "é só para fazer o que eu já tinha mandado, fazer as ferramentas que colocamos no
programa funcionem como deveriam e como eu tinha escolhido."

**Situação: em andamento** (começada em 27/10/2026).

## Decisões que esta tarefa precisa cumprir (número + palavras dele)

| Nº | Palavras dele | O que tem de ficar no programa |
|---|---|---|
| D-558 (27/10) | `ac-grade-inserir`: "quando falei dividir é dividir a pagina, usando a funcionalidade do scantailor que colocamos no aplicativo, é isso que deveria ser feito." | "Dividir" na grade "Todas as páginas", nas folhas escolhidas, com a função de dividir do ScanTailor do programa (a mesma do "dividir esta"), com andamento. Sai a D-529. |
| D-334 (24/09) | (paráfrase) "Ver todas as páginas do livro em grade [...]: seleção múltipla, girar, apagar, extrair, inserir, dividir." | (o "dividir" é a D-558; o "inserir" ficou para depois, D-567) |
| D-559 (27/10) | `ac-tampa`: "Como eu decidi: sumir em todo o livro, e o Kaique escolhe por livro cortar ou pintar de branco (recomendo)" | A faixa preta da tampa do scanner some em todo o livro, também no Automático; por livro, cortar ou pintar de branco. Substitui D-495/D-499 (só à mão). |
| D-097 (13-21/10) | "É para sumir totalmente." · "tem que ficar rente a folha de papel, não pode ter preto ali." | Nada de preto da tampa no PDF. |
| D-092 (09/10) | `rv5-pag-egenloff-047`: "O Kaique escolhe por livro" | A escolha cortar / pintar de branco é do livro. |
| D-547 (27/10) | (escolha da gerente sobre D-066: "precisamos que o pdf saia que nem está na tela") | Todas as telas e miniaturas mostram a página movida/redimensionada como sai no PDF. |
| D-473 / D-066 / D-064 | D-066: "precisamos que o pdf saia que nem está na tela" · D-064: "é só colocar uma bolinha de carregamento, pode ter uma pro livro inteiro e outra para a pagina que estamos, quando passsamos o mouse em cima mostra a mensagem de porcentagem e quantas paginas carregaram já." | Quando a medida no tamanho do PDF termina, a tela troca pela imagem do PDF reduzida (troca da 10b, `ui/tarefas.py`). |
| D-568 (27/10) | `v-roda`: "Como ficou: sem zoom troca de página; Ctrl + roda dá zoom" | Com zoom, a roda anda pela página. |
| D-570 (27/10) | `v-zoom-pares`: "Sim, zoom também no lado a lado" | O "– N% +" vale no "Duas lado a lado". |
| D-571 (27/10) | `v-100`: "A página inteira cabendo na tela (recomendo)" | Conferir: 100% = página inteira cabendo. |
| D-554 / D-494 / D-075 | `ac-margens-iguais`: "Também na tela do corte" · D-075: "Mas eu vou conseguir alterar isso né?" | Caixinha "Margens iguais" também na tela do Cortar, ligada ao mesmo valor do Automático. |
| D-563 (27/10) | `ac-desentortar-texto`: "Tirar, voltar como era antes (recomendo)" | Sai a conta "desentortar só o bloco do texto" (D-493/D-530), com os testes dela. |
| D-564 (27/10) | `ac-gravura-cinza`: "Não fazer: gravura continua em preto e branco (recomendo)" | Sai a chave `GRAVURA_ESCURA_EM_CINZA` (D-532), com os testes dela. |
| D-020 (18/07) + P-129 | "13. Ctrl+Z desfaz qualquer alteração, sem limite de quantidade, e Ctrl+Shift+Z refaz" | O desfazer tira a marcação do Retângulo (lista 1.3, 1.9, 4.6); o aviso volta (1.6); o desfazer não desfaz o que não está à vista (1.7). |
| D-090 / D-091 + P-061 | "eu devo conseguir abrir uma aba para selecionar as que eu quero ( as paginas) ou também simplismente apertar num botão e selecionar todas." · "'Selecionar todas' e 'Nenhuma'" | "usar em todas" (Bordas e Dividir) abre a lista com as exceções desmarcadas e nunca apaga exceção. |
| D-156 (01/10) | "espero ter a escolha de conseguir deixar a foto em original, caso precise." | "Só neste pedaço" vale também no Preto e branco / sem "Limpar a folha". |
| Lista de bugs 12/10 | (bug) "letra e traço" marcado à mão não protege a tinta do "Só as letras" | A marcação à mão protege a tinta. |
| Lista de bugs 22/10 | (bug) botões que aparecem por um instante como janelinhas soltas ao abrir | Não piscam. |
| Lista de espera 29/09 | "Recuperar o trabalho anterior" no menu do cartão (ideia de agente, "a definir") | Não é decisão do Samuel no Livro: fica como está, vira pergunta. |
| Lista única 1.2, 5.9, 1.4, 1.5, 1.10, 1.11, 1.13, 3.2, 2.3, 2.6, 5.3, 5.6, 5.7 | (ver `relatorios/testes-guiados/lista-unica-2026-10-23/lista.md`) | Conferir o que as etapas anteriores já resolveram; fazer só o que falta, como o Livro decide. |

## Andamento (27/10, noite)

Feitos, com prova em `tests/test_decisoes_9b2.py` (commits no ramo): D-563, D-564, D-554, D-568, D-570, D-571,
D-558, D-559, D-547 + a troca da 10b (D-473/D-064, bolinhas), desfazer da marcação (P-129; lista 1.3, 1.6, 1.7,
1.9, 4.6), "usar em todas" do Dividir (D-090, P-061), "letra e traço" à mão (bug 12/10), "só neste pedaço"
(D-156: já consertado antes, só a prova), botões que piscavam (bug 22/10).
Falta: lista única (1.2/5.9, 1.4, 1.5, 1.10, 1.11, 1.13, 3.2, 2.3, 2.6, 5.3, 5.6, 5.7), reversão no código antigo,
somas, prints, GitHub, relatório final.
