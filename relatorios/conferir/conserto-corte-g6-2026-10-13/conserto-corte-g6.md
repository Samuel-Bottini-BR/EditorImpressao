# Conserto do corte do livro novo: a borda preta do scanner (13/10/2026)

Relatório do implementador. **PRONTO PARA CONFERIR.** Quem aprova é o Samuel; o verificador ainda precisa olhar as imagens.

## Em uma frase

**No livro novo, a página torta com borda preta de scanner não sai mais com a faixa preta larga dentro do corte:** nas cinco páginas que tinham piorado com o "endireitar antes de cortar", a faixa voltou para perto do que era na ordem antiga, sem perder nada impresso.

## As cinco páginas

"Faixa escura" é quanto da página é mancha escura encostada na beirada (a conta do verificador). Medido pelo programa, 300 DPI, sem filtro.

| Página | Ordem antiga | Ordem nova de hoje | Ordem nova consertada | Tamanho: antiga → hoje → consertada (mm) |
|---|---|---|---|---|
| Matemática 32 | 18,4% | 31,5% | **16,8%** | 165 × 297 → 209 × 290 → 167 × 290 |
| Cursus 3 | 0,5% | 7,5% | **1,0%** | 201 × 268 → 212 × 279 → 198 × 278 |
| Antiphon 260 | 3,2% | 7,6% | **3,4%** | 464 × 590 → 463 × 618 → 463 × 591 |
| Antiphon 88 | 8,5% | 12,6% | **7,2%** | 438 × 621 → 456 × 624 → 432 × 623 |
| Camões 104 | 0,5% | 2,7% | **0,9%** | 93 × 132 → 95 × 131 → 93 × 131 |

A tinta que fica de fora do corte é a mesma de hoje nas cinco (de 0,00% a 0,03%).

![Cursus 3: ordem antiga, ordem nova de hoje, ordem nova consertada](img/tres-cursus_p003__inteira.jpg)

![Matemática 32](img/tres-matematica_p032__inteira.jpg)

![Antiphon 260](img/tres-antiphon_p260__inteira.jpg)

![Antiphon 88](img/tres-antiphon_p088__inteira.jpg)

![Camões 104](img/tres-camoes_p104__inteira.jpg)

## O resto das 89 páginas

- **Ordem antiga (projeto antigo):** idêntica ponto por ponto nas 89 páginas, nos dois preparos antigos (md5 da página pronta, antes e depois do conserto).
- **Ordem nova:** 79 das 89 saem idênticas ponto por ponto às de hoje. Entre elas: as 46 que não giram, as 14 páginas do gabarito do G6 (Graduale 221 e 222, Escola 7 e 35, Palatino 66, Horas 11 e 27, Opus Majus 20, Boécio 8, Siebmacher 7 e 9, Marial 7) e 7 das 8 que tinham melhorado (Graduale 221 e 223, Rhetorica 73, Boécio 22, Graduale 588, Horas 13, Siebmacher 9 direita).
- **Mudam 10:** as cinco acima e mais cinco:

| Página | O que mudou | Faixa: hoje → consertada | Tinta de fora: hoje → consertada | Tamanho (mm) |
|---|---|---|---|---|
| Pesel 21 | **Para olhar.** Página de cartão escuro: o corte passa a apertar em volta do conteúdo (título, gravura, legenda). Antes ficava a folha inteira, nas duas ordens. Nada impresso fica de fora, mas a legenda fica a 1 mm da borda de baixo. | 47,3% → 35,4% | 0,03% → 0,03% | 157 × 241 → 145 × 206 |
| Egenloff 3 | 0,5 mm a menos embaixo. Uma peça do rodapé da biblioteca passa a ficar de fora. | 1,9% → 1,9% | 0,30% → 0,35% | 338 × 454 → 338 × 454 |
| Camões 66 | Some o fio escuro de cima (0,3 mm de diferença). | 0,9% → 0,8% | 0,04% → 0,04% | 92 × 130 → 92 × 130 |
| Antiphonal 1547 252 | 1 mm a menos de altura. | 0,4% → 0,4% | 0,02% → 0,02% | 65 × 100 → 65 × 99 |
| Rariora 155 | 1 mm a mais de altura. | 0,0% → 0,0% | 0,03% → 0,03% | 133 × 113 → 133 × 114 |

Pela regra do verificador (faixa 0,5 ponto, tinta 0,1 ponto, 2 peças), **nenhuma página piora contra hoje**.

![Pesel 21](img/tres-pesel_p021__inteira.jpg)

![Egenloff 3](img/tres-egenloff_p003__inteira.jpg)

## A causa (confirmada) e o conserto

O giro pinta de branco as cunhas das beiradas, e esse branco ficava entre a beirada da imagem e a borda preta do scanner. A busca do corte deixava de reconhecer a borda de três jeitos, e cada um ganhou o seu conserto (`core/recortar.py`, comentário "A cunha do giro"):

1. **Borda preta maciça** (Cursus 3, Matemática 32, Camões 104): a conta "80% da coluna é escura" passa a ser feita só nos pontos que são imagem de verdade.
2. **Fundo preto liso** (Antiphon 88 e 260): o degrau do branco para o preto criava "tinta" que não existe; essa tinta é jogada fora.
3. **Coisa que encostava na beirada** (Antiphon 260): o contorno da folha de baixo virava peça solta e puxava o corte 13 mm para dentro do preto; o pedaço grande colado na cunha deixa de ser peça.

O apagar de sempre fica como está. Só a página endireitada do livro novo passa pelas três contas; projeto antigo e página que não gira, não.

## Ressalvas

1. **Parte do que o G6 melhorou vem da mesma cunha branca.** O número da folha do Graduale 221 e 223 só sai inteiro porque a cunha o separa da beirada do scan. Por isso o conserto não trata a cunha como "não existe" (isso desfaria a melhora: medido). É uma melhora que depende de a página estar torta para aquele lado.
2. **O limite de 20% da regra 3** foi acertado com dois casos (o número da folha do Graduale mede 9% da largura; o contorno do Antiphon 260, 34%) e conferido nas 43 páginas que giram. É a parte mais frágil.
3. **Cursus 3:** sobra um fio escuro de uns 4 mm à direita (na ordem antiga, zero).
4. **Pesel 21** muda muito de tamanho (acima). Só há uma página desse livro no conjunto.
5. **Só 89 páginas soltas**, nenhum livro inteiro. Não abri a janela do programa.
6. **Custo:** mediana de 18 ms a mais por página que gira, uma vez por página (a busca do corte leva 27 ms). Não rodei o teste de velocidade.
7. O risco das "riscas de dobra" apagando linha de texto da máscara no Cursus 3 (achado do verificador) continua como está.

## Como foi conferido

| O quê | Máquina ou olho | Como |
|---|---|---|
| As três colunas nas 89 páginas | máquina | `relatorios/conserto-corte-g6/scripts/medir.py` (a conta do verificador, copiada) antes e depois, com md5; `comparar.py` |
| Projeto antigo | máquina | md5 dos dois preparos antigos nas 89; os 40 projetos gravados pelo programa de antes do G6 (`projeto_antigo.py`); teste `test_projeto_antigo_sai_identico_ponto_por_ponto` |
| Teste novo | máquina | `tests/test_ordem_do_preparo.py`: página torta com borda preta na ordem nova, 6 casos; falha sem o conserto, passa com ele |
| Suíte | máquina | os 39 arquivos de teste que usam a pipeline ou o corte, um por vez: todos passam |
| Imagens | olho (só as minhas) | abri Cursus 3, Antiphon 260 e Pesel 21; **as outras o verificador precisa abrir** |

As imagens das três colunas estão em `img/tres-*.jpg` (as 10 que mudaram, as 8 que tinham melhorado e o gabarito do G6).
