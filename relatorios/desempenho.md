# Desempenho

Medido em 05/08/2026 as 16:13.

As metas sao as da Etapa 5 do protocolo. Onde houver projecao, ela sai
do custo real por folha medido nos nove livros, multiplicado por 500 -
nenhum livro do acervo tem 500 paginas.

| O que | Medido | Meta | Passou? |
|---|---|---|---|
| Abrir o programa | 0.5 s | 10 s | sim |
| Primeiras miniaturas na tela | 0.5 s | 5 s | sim |
| Analisar 500 folhas | 186.5 s | 180 s | NAO |
| Exportar 500 paginas a 300 DPI | 349.5 s | 1200 s | sim |
| Pico de memoria | 1450.3 MB | 2048 MB | sim |

## Custo por pagina, que e de onde as projecoes saem

- Analisar uma folha: 373 milissegundos
- Exportar uma pagina a 300 DPI: 699 milissegundos

## Quanto tempo cada filtro leva por pagina

| Filtro | Tempo |
|---|---|
| Original | 4 ms |
| Preto e branco | 1737 ms |
| Melhorar | 3451 ms |
| Mágico pro | 3919 ms |

## Memoria, livro a livro

O que importa aqui e o pico **nao acompanhar** o tamanho do livro. Se
acompanhasse, um livro grande estouraria a memoria da maquina do
Kaique.

| Livro | Folhas | Pico |
|---|---|---|
| Marial de sermoens - Frei Balthasar Paez | 907 | 960 MB |
| Graduale - Saeculum XIV | 750 | 1414 MB |
| Rhetorica Christiana -  Fray Diego Valad | 446 | 843 MB |
| Na escola de Jesus - Catecismo explicado | 199 | 861 MB |
| Livro de Horas - Luís XIV | 191 | 1450 MB |
| Giovambattista Palatino cittadino romano | 134 | 760 MB |
| Schön Neues Modell Buch - Johann Siebmac | 134 | 796 MB |
| POINTS d´ANCIENNES BRODERIES ANGLAISES - | 92 | 837 MB |
| Sobre a Consolação da Filosofia - Severi | 50 | 798 MB |

## Em que maquina isto foi medido

- Windows 11, 16 nucleos, 15 GB de memoria

> Esta maquina e mais forte que a do Kaique. Os tempos la serao
> maiores. A conferencia num computador de verdade esta em
> `conferencia-outro-computador.pdf`.
