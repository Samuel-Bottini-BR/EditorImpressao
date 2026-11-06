# Memória ao processar: os 9 livros do acervo

Pedido do Samuel (04/11/2026): "o teste foi feito com um pdf só?". Foi, só com o Rhetorica. Ele aceitou medir
nos 9 livros do acervo: "pode". Verificador, 04 e 05/11/2026. **Teste de máquina** (medida e comparação de
arquivos; ninguém precisa olhar imagem para decidir isto).

## A resposta, em português simples

**A memória ficou parada nos 9 livros.** Do começo ao fim de cada livro, a memória do programa subiu no máximo
uns 70 MB, e isso não acompanha o tamanho do livro: no Graduale, com um PDF de 6,4 GB, subiu 40 MB; no Boécio,
com 115 MB, subiu 48 MB. No código antigo, a memória subia junto com o PDF: no Na escola de Jesus subiu 888 MB.

**Nenhum livro caiu.** Os 9 terminaram, e o PDF de cada um tem exatamente o número de páginas que o programa
planejou.

**Os PDFs saíram iguais aos do código antigo**, nos 5 livros em que rodei os dois. Todas as páginas têm as
mesmas imagens, byte a byte. Em 12 páginas espalhadas de cada livro, a página desenhada é igual pixel a pixel.

## Os 9 livros, com o código novo

| Livro | Folhas | Pico do programa | PDF | Tempo | Terminou? | Igual ao antigo? |
|---|---|---|---|---|---|---|
| Marial de sermoens | 500 de 907 (pedaço) | 1.938 MB | 2,5 GB | 37 min 19 s | sim | não comparado |
| Graduale - Saeculum XIV | 300 de 750 (pedaço) | 2.238 MB | 6,4 GB | 54 min 30 s | sim | não comparado |
| Rhetorica Christiana | 446 | 1.693 MB | 1,4 GB | 25 min 20 s | sim | não comparado |
| Na escola de Jesus | 199 | 1.748 MB | 1,2 GB | 13 min 10 s | sim | sim (199 páginas; 12 páginas pixel a pixel) |
| Livro de Horas - Luís XIV | 191 | 2.493 MB | 1,9 GB | 22 min 36 s | sim | não comparado |
| Palatino | 134 | 1.645 MB | 368 MB | 3 min 34 s | sim | sim (134 páginas; 12 páginas pixel a pixel) |
| Siebmacher | 134 | 1.656 MB | 293 MB | 5 min 29 s | sim | sim (134 páginas; 12 páginas pixel a pixel) |
| Pesel (broderies anglaises) | 92 | 1.729 MB | 238 MB | 5 min 15 s | sim | sim (92 páginas; 12 páginas pixel a pixel) |
| Boécio | 50 | 1.572 MB | 115 MB | 1 min 14 s | sim | sim (50 páginas; 12 páginas pixel a pixel) |

"Pico do programa" é a memória mais alta que o programa usou no livro inteiro (análise, processar e gravar).
Cada livro rodou sozinho, um depois do outro, do maior para o menor.

## A memória sobe com o livro? Começo contra fim

Cada livro foi dividido em quatro partes iguais de páginas. A "memória de base" é a mediana da memória durante
aquela parte: se o programa guardasse o livro na memória, ela subiria parte a parte.

| Livro | Pico no 1º quarto | no 4º quarto | Memória "de base" no 1º quarto | no 4º quarto | Páginas: esperadas / no PDF |
|---|---|---|---|---|---|
| Marial de sermoens | 1.905 MB | 1.938 MB | 1.674 MB | 1.743 MB | 500 / 500 |
| Graduale - Saeculum XIV | 2.203 MB | 2.238 MB | 1.793 MB | 1.833 MB | 300 / 300 |
| Rhetorica Christiana | 1.669 MB | 1.693 MB | 1.589 MB | 1.618 MB | 446 / 446 |
| Na escola de Jesus | 1.728 MB | 1.748 MB | 1.624 MB | 1.648 MB | 199 / 199 |
| Livro de Horas - Luís XIV | 2.244 MB | 2.493 MB | 1.809 MB | 1.865 MB | 191 / 191 |
| Palatino | 1.619 MB | 1.645 MB | 1.548 MB | 1.585 MB | 134 / 134 |
| Siebmacher | 1.608 MB | 1.656 MB | 1.530 MB | 1.572 MB | 134 / 134 |
| Pesel (broderies anglaises) | 1.699 MB | 1.729 MB | 1.540 MB | 1.605 MB | 92 / 92 |
| Boécio | 1.524 MB | 1.558 MB | 1.488 MB | 1.536 MB | 50 / 50 |

O pico absoluto muda de um livro para outro porque depende do tamanho da página (Graduale e Livro de Horas têm
páginas muito maiores), não do número de páginas.

**Livro de Horas:** o pico do último quarto (2.493 MB) vem das 5 últimas páginas (187 a 191), que são muito mais
altas que as outras: até 5.558 pontos de altura, contra cerca de 1.400 no resto do livro. A memória de base não
subiu: 1.809 MB no começo e 1.865 MB no fim.

## Código antigo contra o novo (os mesmos livros)

Código antigo: a obra logo antes do conserto (`f06e0c15`). Código novo: ramo `memoria-pdf-2026-11-04`
(`45005116`). Entre os dois, só mudou o conserto da memória (`core/pdf_io.py`, `core/cadernos.py`,
`core/impressao.py` e o aviso na tela).

| Livro | PDF | Pico antigo | Pico novo | Base antiga 1º → 4º quarto | Base nova 1º → 4º quarto |
|---|---|---|---|---|---|
| Na escola de Jesus | 1.198 MB | 2.871 MB | 1.748 MB | 1.727 → 2.615 MB (+888) | 1.624 → 1.648 MB (+24) |
| Palatino | 368 MB | 1.967 MB | 1.645 MB | 1.584 → 1.869 MB (+285) | 1.548 → 1.585 MB (+37) |
| Siebmacher | 293 MB | 1.879 MB | 1.656 MB | 1.554 → 1.795 MB (+241) | 1.530 → 1.572 MB (+42) |
| Pesel (broderies anglaises) | 238 MB | 1.900 MB | 1.729 MB | 1.560 → 1.774 MB (+214) | 1.540 → 1.605 MB (+65) |
| Boécio | 115 MB | 1.640 MB | 1.572 MB | 1.506 → 1.611 MB (+105) | 1.488 → 1.536 MB (+48) |

Os 5 PDFs de saída são iguais nos dois códigos:

- mesmo número de páginas;
- em **todas** as páginas, as mesmas imagens (os dados, byte a byte, com o mesmo tamanho e as mesmas cores) e o
  mesmo desenho da página;
- em 12 páginas espalhadas de cada livro (a primeira, a última e as do meio), a página desenhada a 150 dpi é igual
  pixel a pixel, e cada imagem da página, aberta na resolução dela, também.

Para saber se a comparação acusa diferença quando ela existe, comparei o Palatino com o Siebmacher (os dois
com 134 páginas). Todas as páginas saíram diferentes, como devia.

## Ressalvas

- **Dois livros foram medidos em pedaço.** Ensaio de 20 folhas: o Graduale inteiro levaria cerca de 1 h 45 e
  daria um PDF de cerca de 16 GB. O Marial inteiro levaria cerca de 1 h 15. Medi o **Graduale com 300 de 750
  folhas** (6,4 GB) e o **Marial com 500 de 907 folhas** (2,5 GB): as primeiras folhas, pelo mesmo caminho.
- **Os tempos não são de confiança, a memória é.** O PC estava com outros agentes trabalhando, e pode haver um
  verificador separado pilotando a janela ao mesmo tempo. Durante o Rhetorica o Windows chegou a ficar com só
  22 MB livres. Isso muda os tempos, mas não a memória que o próprio programa usa.
- **A medida é das funções do programa, sem a janela,** como o `medir_memoria.py` do Rhetorica: "Confirmar e
  processar" de fábrica, **uma página por vez**. Com várias páginas ao mesmo tempo (o de fábrica no programa),
  o pico é maior, porque cada trabalhador tem a sua página; isso não foi medido aqui.
- **A memória de base ainda sobe um pouco** (24 a 69 MB no livro inteiro). Essa subida não acompanha o tamanho do
  livro: o maior PDF (6,4 GB) subiu menos que o menor (115 MB). Por isso não é o livro se acumulando na memória.
  Não investiguei de onde vem.
- **Os quatro livros maiores (Marial, Graduale, Rhetorica e Horas) não foram rodados com o código antigo.** O
  antigo já caiu no Rhetorica com 270 folhas (medida anterior); no Na escola de Jesus (PDF de 1,2 GB) ele terminou,
  com 2.871 MB, porque desta vez havia memória livre.
- Só medi o "Confirmar e processar". "Montar cadernos" e o livreto não foram medidos nos 9 livros (só no
  Rhetorica, no relatório anterior).
- **Observação fora do pedido:** em agosto, o Siebmacher saía com 268 páginas (cada folha dividida em duas).
  Hoje, de fábrica, sai com 134. O PDF bate com o que o próprio programa planejou. Não investiguei por quê.
- "Memória do programa" é a do processo principal. O servidor de páginas (o outro processo do programa) fica
  à parte, entre 1.100 e 1.580 MB, e também não cresceu.

## Onde estão as coisas

Na cópia `memoria-pdf` (ramo `memoria-pdf-2026-11-04`), pasta `relatorios/memoria-pdf/`:

- `medidas-9-livros/medir_livro.py`: mede um livro, com o código novo ou o antigo;
- `medidas-9-livros/comparar_pdfs.py`: compara os PDFs;
- `medidas-9-livros/rodar_novo.sh`, `rodar_antigo.sh` e `rodar_antigo_grande.sh`: a ordem dos livros;
- `medidas-9-livros/medidas/`: uma medida por livro e uma comparação por livro;
- `nove-livros/gerar_relatorio.py` e `texto.md`: este relatório.

Os PDFs de saída não entram no git.
