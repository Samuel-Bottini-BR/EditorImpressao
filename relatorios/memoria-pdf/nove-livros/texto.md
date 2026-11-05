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

{tabela}

"Pico do programa" é a memória mais alta que o programa usou no livro inteiro (análise, processar e gravar).
Cada livro rodou sozinho, um depois do outro, do maior para o menor.

## A memória sobe com o livro? Começo contra fim

Cada livro foi dividido em quatro partes iguais de páginas. A "memória de base" é a mediana da memória durante
aquela parte: se o programa guardasse o livro na memória, ela subiria parte a parte.

{detalhe}

O pico absoluto muda de um livro para outro porque depende do tamanho da página (Graduale e Livro de Horas têm
páginas muito maiores), não do número de páginas.

**Livro de Horas:** o pico do último quarto (2.493 MB) vem das 5 últimas páginas (187 a 191), que são muito mais
altas que as outras: até 5.558 pontos de altura, contra cerca de 1.400 no resto do livro. A memória de base não
subiu: 1.809 MB no começo e 1.865 MB no fim.

## Código antigo contra o novo (os mesmos livros)

Código antigo: a obra logo antes do conserto (`f06e0c15`). Código novo: ramo `memoria-pdf-2026-11-04`
(`45005116`). Entre os dois, só mudou o conserto da memória (`core/pdf_io.py`, `core/cadernos.py`,
`core/impressao.py` e o aviso na tela).

{antigo}

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
