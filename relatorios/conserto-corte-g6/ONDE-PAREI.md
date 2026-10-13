# Onde parei — conserto do corte do G6 (implementador, 13/10/2026)

Ramo `conserto-corte-g6-2026-10-13` (worktree `.claude/worktrees/conserto-corte-g6`, saído do `fase-1` em `b5b12da`).
**Não juntado ao `fase-1`.**

## O defeito

No livro novo (endireitar antes de cortar, G6) a página é girada inteira e o giro pinta de branco as
cunhas das beiradas. Esse branco esconde a borda preta do scanner da busca do corte: sobra faixa preta
larga em página torta com borda preta (Matemática 32, Cursus 3, Antiphon 88 e 260, Camões 104).
Relatório do verificador: ramo `verif-corte-g6-2026-10-13`, `relatorios/conferir/corte-g6-2026-10-13/`.

## Feito

- [x] Worktree com as junções (`modelos`, `gabarito\paginas`, `gabarito\scantailor-24-09`) e `_tmp\` (fora do git).
- [x] Cópia do `medir.py` do verificador (`scripts/medir.py`; só mudaram caminhos e três variáveis de ambiente) e
      dos dados dele (`dados-verificador.json`).
- [x] **Medida de antes** com o código de hoje, as 89 páginas nos três preparos, com o md5 de cada página
      pronta: `dados-antes.json`.
- [x] Causa confirmada e variantes do conserto medidas nas 43 páginas que giram (`scripts/experiencia.py`,
      `experiencia.json`; resumo com `scripts/comparar_exp.py`).

## A variante escolhida (ainda só na experiência): "bUa"

O apagar de hoje fica inteiro, e a máscara de tinta da página endireitada perde MAIS duas coisas:

1. as linhas e colunas de borda sólida achadas contando os 80% de escuro **só nos pontos que são imagem
   de verdade** (a cunha do giro não conta nem a favor nem contra);
2. a "tinta" que **só existe por causa do degrau branco da cunha** e está em fundo escuro do scanner
   (some quando a cunha é preenchida com a vizinha; caso do fundo preto liso do Antiphon).

Números da experiência (cópias JPEG das páginas; faixa escura, ordem antiga → nova de hoje → consertada):

| Página | antiga | hoje | consertada |
|---|---|---|---|
| Matemática 32 | 18,45% | 31,51% | 16,81% |
| Cursus 3 | 0,48% | 7,44% | 0,98% |
| Antiphon 260 | 3,20% | 7,61% | 3,38% |
| Antiphon 88 | 8,48% | 12,65% | 7,26% |
| Camões 104 | 0,53% | 2,74% | 0,87% |

Das 43 páginas que giram, o corte muda em 8: as cinco acima, Pesel 21 (47,3% → 35,4%), e 1 mm em
Graduale 223 e Antiphonal 252. Nenhuma perde tinta. As outras 35 ficam idênticas às de hoje.

## Falta

- [ ] Escrever no programa (`core/recortar.py`; uma linha em `core/pipeline.py`).
- [ ] Teste de máquina novo (página torta com borda preta na ordem nova).
- [ ] Medida de depois com o programa (`dados-depois.json`) e a comparação das três colunas.
- [ ] Custo por página.
- [ ] `relatorios/melhorias.md` (tudo o que foi tentado) e o relatório.
