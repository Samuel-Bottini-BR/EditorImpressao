# Quadrados brancos: o conserto C (D-668) no programa

**Agente de conserto, 10/11/2026.** Ramo `quadrados-c-2026-11-10` (a partir do `obra-2026-10-26`, `58806f81`).
Tudo sem janela (`QT_QPA_PLATFORM=offscreen`), em cópia, com dados num `LOCALAPPDATA` à parte; acervo só lido.
Teste de **máquina** (medidas, provas em `tests/`) e preparado para o **olho** do Samuel (imagens).

## Em uma frase

**O Melhorar e o Mágico pro não fazem mais buracos brancos nas pinturas, e o "i" e o "t" finos voltam inteiros.**
O programa consertado sai igual, ponto por ponto, à simulação C que o Samuel escolheu (página 13, prévia e PDF).

Decisão (D-668, Central `quadrados-qual`: "Roxo: o conserto C (recomendo)"; chat: "c").

## O que mudou no programa

1. **Uma regra só para os três filtros** (D-667: "se mudou a ferramenta, muda em todos os lugares"). A caixinha
   "Respeitar as gravuras achadas" marcada, num filtro escolhido à mão, faz a página procurar a gravura no Preto e
   branco, no Melhorar e no Mágico pro. Antes, só no Preto e branco (D-659). A lista dos três filtros fica num lugar
   só (`core/filtros.py`, `FILTROS_QUE_RESPEITAM_AS_GRAVURAS`) e serve às duas perguntas da caixinha: "marcada, procura?"
   (`core/etapas.respeitar_procura`) e "desmarcada, o que a máquina achou sai do filtro?"
   (`core/pipeline.marcacao_que_o_filtro_usa`, que já valia para os três). No Preto e branco nada muda.
2. **A limpeza do papel do Melhorar e do Mágico pro ganhou uma quarta pergunta: "em volta também é papel?"**
   (`core/filtros.py`, `_em_volta_e_papel`, chamada no fim de `_limpar_o_papel_de_verdade`, fora da gravura). Vale
   com a caixinha marcada ou desmarcada (o print 10).
3. Nada mudou na tela (`ui/`), nem no Original, nem na correção do "magic color" (CLAUDE.md §9), nem no papel de
   dentro da gravura (bug 202).

## As medidas: antes e depois

"Antes" = o código do `obra-2026-10-26` (`58806f81`). "Depois" = este ramo. Livro novo, filtro escolhido à mão
(Melhorar "bem forte", Mágico pro "bem fraco", os ajustes dos prints 09 e 10), página dividida, endireitada e
cortada como o programa faz, como sai no PDF (300 DPI).

### Página 13 do *Na escola de Jesus* (Jonas e a baleia)

{PAGINA13}

### O livro inteiro (*Na escola de Jesus*, 199 páginas)

{LIVRO}

### Livro de Horas 47 e as páginas do gabarito do assunto

{GABARITO}

### Tempo

{TEMPO}

## O que piorou em algum número (CLAUDE.md §5: os dois resultados)

{PIOROU}

## Imagens (no modelo do girar: azul = antes, verde = depois, o que olhar circulado em vermelho)

- `imagens/1-resumo-pagina-13.png` — resumo: página 13, Melhorar.
- `imagens/2-melhorar.png` e `imagens/3-magico-pro.png` — água (Escola 13), céu (Escola 97), "Vivia" (Escola 13) e o
  prédio (Horas 47).
- `imagens/4-print-10-respeitar-desmarcada.png` — o print 10 (Mágico pro, "Respeitar" desmarcada).
- `imagens/5-o-que-ja-estava-bom.png` — mancha do verso (Boécio 33), xilogravura (Boécio 3), retrato (Palatino 5) e o
  anjo (Escola 35).

## Provas e testes

{TESTES}

## Ressalvas

{RESSALVAS}
