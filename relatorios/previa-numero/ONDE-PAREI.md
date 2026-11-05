# ONDE PAREI — D-617, escrever o número da folha na prévia do Automático

Ramo `previa-numero-2026-11-04` (saiu de `obra-2026-10-26`), cópia `.claude/worktrees/previa-numero`.
Mexo só no contador da prévia (`ui/automatico.py`, `PaginaAntesEDepois`). Outro agente mexe na etapa
Dividir do `ui/automatico.py`, em outra cópia.

## Decisões que esta tarefa precisa cumprir

- **D-617** (04/11/2026), print a-63 ("página 30 de 70" circulado): "queria poder escrever o numero da
  folha aqui para ir direto." No Livro: o número em "página N de 70" pode ser escrito: digita o número,
  Enter, e a prévia vai direto para essa folha. As setas < > continuam como estão.
  Pedido da gerente: número fora do intervalo ou vazio volta ao número atual, sem mensagem de erro; as
  setas do teclado continuam como hoje na janela; o visual segue os outros números editáveis do programa.
- **D-605 / CLAUDE.md §11.8** (03/11/2026): "nenhuma função nova, ou nova escolha dentro do programa
  pode alterar o que já está escolhido e testado, coisas novas não podem criar novos problemas".

## O que já está escolhido e testado aqui

- **D-577** (testada pelo Samuel em 01/11, "está funcionando"): a prévia "A página, antes e depois" da
  janela grande; antes cru, depois com as etapas marcadas, a linha, bolinha, "tela cheia" com zoom,
  folhear e "comparar". Testes: `tests/test_decisoes_automatico_ver_como_fica.py` (inclui
  `test_d577_folhear_e_zoom_continuam`: `"página 2 de 3" in painel.contador.text()`, e o tela cheia:
  `tela.contador.text()`, seta Esquerda e Esc no tela cheia).
- **D-614** (04/11, feita, a testar pelo Samuel): com o Dividir marcado, o depois é uma página por vez e
  as setas < > andam pelas metades; o contador não muda nas duas metades ("página 1 de 3"). Testes:
  `tests/test_decisoes_previa_dividida.py` (`painel.contador.text() == "página 1 de 3"` exato).
- **D-600** (Shift + roda anda para os lados na prévia e no comparar): `tests/test_decisoes_shift_todas_as_telas.py`.
- **D-599** zoom no ponteiro: `tests/test_zoom_no_ponteiro.py`.
- **D-603 / D-574** (folhas do caderno na etapa 7, o lado direito troca): `tests/test_caderno_segue_as_etapas.py`.
- Provas gerais do Automático: `tests/test_decisoes_automatico.py`.
- Teclado hoje: `PaginaAntesEDepois.keyPressEvent` (setas e Page Up/Down viram a página quando a prévia
  tem o foco); `TelaCheiaDoAntesEDepois.keyPressEvent` (o mesmo, Esc fecha).

Consequência para o código: `self.contador` continua existindo e o `.text()` dele continua dando
exatamente "página N de M" (os testes antigos leem assim). O tela cheia não muda (o pedido é a prévia).

## O teclado hoje, medido na janela de verdade (Gradus, `piloto.py base`, `anotacoes-base.txt`)

- Ao abrir o Automático, o foco está numa caixa de escolha (QComboBox): Direita/Esquerda não mudam a página.
- Depois de clicar o ">" com o mouse: o foco fica no botão; Direita/Esquerda passam o foco entre os botões
  ("tela cheia", "–"), sem mudar a página.
- Depois de clicar na imagem: o foco vai para a área da imagem, que come as setas; a página não muda.
- Ou seja: hoje as setas do teclado não viram a página dentro da janela grande (só no "tela cheia").
  "Continuar como hoje" = o campo novo não entra na fila do Tab nem na das setas (só pega o foco com o
  clique) e o foco ao abrir continua o mesmo.
- Achado: o "Rodar" é o botão padrão da janela. Um Enter que o campo deixasse passar apertaria o
  "Rodar". O campo segura o Enter dele.

## Andamento

- [x] teste novo que falha antes (`tests/test_decisoes_previa_numero.py`, 5 falham em `945505b2`)
- [x] código (`fa32c0a0`)
- [x] testes da prévia, um arquivo por vez (todos passaram)
- [x] janela de verdade com o Gradus (13 de 13; prints `prints/novo-*`)
- [x] GitHub: rodada 41884336233 passou (23 min)
- [x] relatório (`relatorio.md`)

## Perguntas para o Samuel

(nenhuma até agora)

---

# Parte 2 (04/11/2026): com o Dividir marcado, o número é o da página como o livro vai sair

Samuel, testando a D-617 (já juntada na obra): "funciona , mas com o dividir marcado o numero de
pagina tem que corresponder com a pagina que está sendo passada." Pedido da gerente: com o Dividir
marcado, a metade da esquerda da folha 68 aparece como "página 135 de 140" e a da direita como "136 de
140"; escrever o número leva a essa página; sem o Dividir, tudo como está; o número segue a ordem do
livro como vai sair (D-615, a ordem mudada à mão, e D-616, a capa aberta: capa = "página 1"); o "tela
cheia" mostra o mesmo número.

Obra juntada no ramo antes de começar (`git merge obra-2026-10-26`, avanço direto até `2499bd28`).

## O que já está escolhido e testado aqui (parte 2)

- D-617 parte 1 (testada: "funciona"): `tests/test_decisoes_previa_numero.py` (5).
- D-614: `tests/test_decisoes_previa_dividida.py`. **Conflito:** as linhas 76, 84, 89 e 137 pedem
  "página 1 de 3" nas duas metades com o Dividir marcado. A gerente autorizou trocar só essas 4
  linhas e a frase da docstring, num commit separado, com comentário citando a D-617 de 04/11
  (o pedido novo substitui a parte do contador da D-614). As linhas 176 e 180 (livro já dividido)
  não mudam.
- D-615 (`tests/test_decisoes_ordem_folhas.py`) e D-616 (`tests/test_decisoes_capa_aberta.py`): a ordem
  vem de `core/automatico.paginas_do_pdf_depois`, a mesma lista das setas (`_passos`) e do caderno.
- D-577 sem o Dividir: "página N de M" com N = a página do livro, igual.

## Andamento (parte 2)

- [x] teste novo que falha antes (3 provas; falham na parte 1)
- [x] código (`667fc94f`)
- [x] testes antigos autorizados: D-614 (`9ad1d87c`), D-617 parte 1 (`3007f97d`)
- [x] arquivos de teste no PC, um por vez: todos passaram (também D-615 e D-616)
- [x] janela de verdade com o Gradus: 11 de 11 (`anotacoes-dividir.txt`, prints `dividir-*`)
- [x] GitHub 41913269201: só o test_d148 por tempo; no PC passou (5 de 5)
- [x] relatório (`relatorio.md`/`.html`/`.pdf`, parte 2 no fim)
