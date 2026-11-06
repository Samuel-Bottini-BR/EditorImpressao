# ONDE-PAREI — memória nos 9 livros do acervo (verificador, 04/11/2026)

Pedido do Samuel (04/11/2026): "o teste foi feito com um pdf só?" — foi (só o Rhetorica). Aceitou medir nos
9 livros do acervo: "pode".

## Decisões que esta tarefa precisa cumprir

- **CLAUDE.md §3:** "Uma página por vez na memória. O pico não pode crescer com o tamanho do livro; há livro de
  300 MB no acervo. Nunca montar lista com todas as páginas processadas."
- **D-304:** "o tamanho do arquivo depois não importa" — o PDF sai sem perda; o conserto não pode mudar a imagem.
- **D-605 (03/11):** "nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está escolhido
  e testado, coisas novas não podem criar novos problemas" — por isso o PDF novo tem de sair igual ao antigo.
- Acervo somente leitura; nada de código do programa mudado (sou verificador).

## O que já está escolhido e testado aqui

- As medidas do Rhetorica (30, 90, 270 folhas) em `../medidas/`, feitas com `../medir_memoria.py`.
- `tests/test_memoria_nao_cresce_com_o_livro.py` (máquina, livros sintéticos).

## Como estou medindo

- `medir_livro.py`: o mesmo caminho do `medir_memoria.py` (modo processar, de fábrica, 1 trabalhador), com a
  cópia do código escolhida por `--raiz`, a página anotada em cada amostra (pico por quarto do livro) e o PDF
  guardado quando é para comparar.
- Código novo: esta cópia (ponta 45005116). Código antigo: `f06e0c15` (a obra que entrou na junção b99f385a,
  logo antes do conserto), numa cópia à parte `.claude/worktrees/memoria-pdf-antes` (criada por mim).
- `comparar_pdfs.py`: número de páginas; todas as páginas (imagens byte a byte e desenho); amostra de 12
  páginas espalhadas pixel a pixel (página desenhada a 150 dpi e cada imagem na resolução dela).
- Sondas de 20 folhas (código novo): Graduale 8,2 s por página e 22 MB por página (o livro inteiro levaria
  ~1 h 45 e daria ~16 GB) → pedaço de 300 folhas. Marial 4,3 s por página (~1 h 15 inteiro) → pedaço de 500.

## Andamento

- [x] Scripts e ensaio de 5 folhas (Boécio, novo e antigo: iguais).
- [x] Código novo, 9 livros (`rodar_novo.sh`, 04-05/11, 23:59 a 02:49): os 9 terminaram, páginas certas.
  Marial em pedaço de 500 de 907 folhas, Graduale de 300 de 750. Memória de base sobe 24 a 69 MB no livro todo.
- [x] Código antigo em 5 livros (Boécio, Pesel, Siebmacher, Palatino; `rodar_antigo.sh`) e no Na escola de Jesus
  (PDF de 1,2 GB; `rodar_antigo_grande.sh`): os 5 PDFs iguais ao novo (todas as páginas byte a byte nas
  imagens, 12 páginas pixel a pixel). Prova do comparador: Palatino x Siebmacher, tudo diferente.
- [x] Relatório nos três formatos em `../nove-livros/relatorio.(md|html|pdf)`.

## Como cumpri cada decisão

- **CLAUDE.md §3 (o pico não pode crescer com o livro):** medido nos 9 livros (tabela "começo contra fim" do
  relatório). Cumprida no processar, uma página por vez.
- **D-304 / D-605 (sem perda; o novo não muda o testado):** PDF novo igual ao antigo em 5 livros.
- Acervo só lido; nenhum código do programa mudado. Os PDFs de saída ficam em `trabalho/` (fora do git, por
  `*.pdf`); a cópia `.claude/worktrees/memoria-pdf-antes` (código antigo) foi criada por mim.

## Perguntas para o Samuel

(nenhuma)
