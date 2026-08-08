# Desempenho

Medido em 08/08/2026 as 00:58.

As metas sao as da Etapa 5 do protocolo. Onde houver projecao, ela sai
do custo real por folha medido nos nove livros, multiplicado por 500 -
nenhum livro do acervo tem 500 paginas.

| O que | Medido | Meta | Passou? |
|---|---|---|---|
| Abrir o programa | 0.6 s | 10 s | sim |
| Primeiras miniaturas na tela | 0.5 s | 5 s | sim |
| Analisar 500 folhas | 177.0 s | 180 s | sim |
| Exportar 500 paginas a 300 DPI | 799.0 s | 1200 s | sim |
| Pico de memoria | 1441.6 MB | 2048 MB | sim |

## Custo por pagina, que e de onde as projecoes saem

- Analisar uma folha: 354 milissegundos
- Exportar uma pagina a 300 DPI: 1598 milissegundos

## Quanto tempo cada filtro leva por pagina

| Filtro | Tempo |
|---|---|
| Original | 3 ms |
| Preto e branco | 2525 ms |
| Melhorar | 3264 ms |
| Mágico pro | 3810 ms |

## Memoria, livro a livro

O que importa aqui e o pico **nao acompanhar** o tamanho do livro. Se
acompanhasse, um livro grande estouraria a memoria da maquina do
Kaique.

| Livro | Folhas | Pico |
|---|---|---|
| Marial de sermoens - Frei Balthasar Paez | 907 | 948 MB |
| Graduale - Saeculum XIV | 750 | 1415 MB |
| Rhetorica Christiana -  Fray Diego Valad | 446 | 864 MB |
| Na escola de Jesus - Catecismo explicado | 199 | 882 MB |
| Livro de Horas - Luís XIV | 191 | 1442 MB |
| Giovambattista Palatino cittadino romano | 134 | 782 MB |
| Schön Neues Modell Buch - Johann Siebmac | 134 | 788 MB |
| POINTS d´ANCIENNES BRODERIES ANGLAISES - | 92 | 823 MB |
| Sobre a Consolação da Filosofia - Severi | 50 | 790 MB |

## Em que maquina isto foi medido

- Windows 11, 16 nucleos, 15 GB de memoria

> Esta maquina e mais forte que a do Kaique. Os tempos la serao
> maiores. A conferencia num computador de verdade esta em
> `conferencia-outro-computador.pdf`.
