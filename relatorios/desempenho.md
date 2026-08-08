# Desempenho

Medido em 08/08/2026 as 02:43.

As metas sao as da Etapa 5 do protocolo. Onde houver projecao, ela sai
do custo real por folha medido nos nove livros, multiplicado por 500 -
nenhum livro do acervo tem 500 paginas.

| O que | Medido | Meta | Passou? |
|---|---|---|---|
| Abrir o programa | 0.4 s | 10 s | sim |
| Primeiras miniaturas na tela | 0.4 s | 5 s | sim |
| Analisar 500 folhas | 164.5 s | 180 s | sim |
| Exportar 500 paginas a 300 DPI | 472.0 s | 1200 s | sim |
| Pico de memoria | 1457.5 MB | 2048 MB | sim |

## Custo por pagina, que e de onde as projecoes saem

- Analisar uma folha: 329 milissegundos
- Exportar uma pagina a 300 DPI: 944 milissegundos

## Quanto tempo cada filtro leva por pagina

| Filtro | Tempo |
|---|---|
| Original | 3 ms |
| Preto e branco | 2105 ms |
| Melhorar | 3911 ms |
| Mágico pro | 4409 ms |

## Memoria, livro a livro

O que importa aqui e o pico **nao acompanhar** o tamanho do livro. Se
acompanhasse, um livro grande estouraria a memoria da maquina do
Kaique.

| Livro | Folhas | Pico |
|---|---|---|
| Marial de sermoens - Frei Balthasar Paez | 907 | 969 MB |
| Graduale - Saeculum XIV | 750 | 1458 MB |
| Rhetorica Christiana -  Fray Diego Valad | 446 | 867 MB |
| Na escola de Jesus - Catecismo explicado | 199 | 868 MB |
| Livro de Horas - Luís XIV | 191 | 1448 MB |
| Giovambattista Palatino cittadino romano | 134 | 778 MB |
| Schön Neues Modell Buch - Johann Siebmac | 134 | 800 MB |
| POINTS d´ANCIENNES BRODERIES ANGLAISES - | 92 | 848 MB |
| Sobre a Consolação da Filosofia - Severi | 50 | 797 MB |

## Em que maquina isto foi medido

- Windows 11, 16 nucleos, 15 GB de memoria

> Esta maquina e mais forte que a do Kaique. Os tempos la serao
> maiores. A conferencia num computador de verdade esta em
> `conferencia-outro-computador.pdf`.
