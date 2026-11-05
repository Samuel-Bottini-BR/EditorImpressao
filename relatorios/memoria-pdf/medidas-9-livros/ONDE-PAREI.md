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
- [ ] Código novo, 9 livros (`rodar_novo.sh`), do maior para o menor.
- [ ] Código antigo em 2 livros (um pequeno, um grande que não caia) e comparação.
- [ ] Relatório nos três formatos em `../nove-livros/`, commit e push.

## Perguntas para o Samuel

(nenhuma)
