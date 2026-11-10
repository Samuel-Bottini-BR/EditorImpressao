# ONDE-PAREI — quadrados brancos no Melhorar e no Mágico pro (verificador, 10/11/2026)

Só investigação: nenhuma linha do programa foi mudada. Acervo só lido; tudo roda em
cópia, sem janela (`QT_QPA_PLATFORM=offscreen`), dados num `LOCALAPPDATA` à parte.

## Decisões que esta tarefa precisa cumprir

- Pedido do Samuel (10/11): "anotar erro do filtro melhorar, ele deixa a imagem pixelada, olha esses
  quadrados brancos. também acontece no automatico e no magico pro, pode colocar um agente para
  investigar isso." · depois: "o erro não aparece só na pagina 13, aparece em varias."
- Regra do resultado da Fase 1 (28/09): "todo o papel totalmente branco, inclusive o papel dentro da
  gravura" e "só pintura de verdade mantém a cor", "sem quadradinhos" (bug 202, roupa do anjo da Escola 35).
- CLAUDE.md §9: a correção do "magic color" (fundo relativo ao papel, peso, curva de ombro) não se desfaz.
- D-586 / D-583: "Respeitar as gravuras achadas" ligada = filtro respeita a marcação; desligada = o
  filtro vale na página inteira.
- D-659: no Preto e branco à mão, "Respeitar" marcada faz o programa procurar a gravura (só Preto e branco).
- D-605: o novo não estraga o já escolhido e testado.
- Não abrir janela na tela do Samuel (09/11).

## O que já está escolhido e testado aqui

- `core/filtros.py`, `_limpar_o_papel_de_verdade` (mancha do verso, queixas "não tirou a mancha do
  verso" e "fundo meio amarelado"); o caminho de dentro da gravura (`_so_o_papel_da_gravura`, tentativa
  20, bug 202, `tests/test_papel_dentro_da_gravura.py`).
- `tests/test_decisoes_respeitar_gravuras.py`, `tests/test_decisoes_gravura_a_mao.py` (D-659).

## Como fica para quem usa e no livro

O Kaique abre um livro novo, escolhe Melhorar ou Mágico pro (no painel ou no Automático) e a pintura
sai com buracos brancos quadrados — na tela e no PDF. Ver o relatório.

## Andamento

- [x] reproduzir na página 13 (prévia e PDF)
- [x] causa medida
- [x] livro inteiro (Melhorar "bem forte" e Mágico pro "bem fraco")
- [x] outro livro do acervo
- [x] conserto candidato medido (não aplicado)
- [x] imagens no modelo de print
- [x] relatório nos três formatos, commit e push

## Como cumpri cada uma

- Pedido do Samuel: reproduzido na página 13 (prévia e PDF) e medido nas 199 páginas do livro e no
  Livro de Horas — `relatorio.html`, imagens 1 a 5.
- Regra da Fase 1 / bug 202: o defeito é o bug 202 voltando pelo caminho sem marcação (seção 2 do relatório).
- CLAUDE.md §9: o conserto proposto não toca a correção do "magic color" (seção 4).
- D-586 / D-583 / D-659: conferido no código e na imagem que "Respeitar" não muda nada no Melhorar/Mágico
  à mão sem o Automático (imagens idênticas ponto a ponto); a saída "estender a D-659" ficou como pergunta.
- D-605: o conserto muda resultado já visto: vai como pergunta ao Samuel, nada aplicado.
- Sem janela na tela dele: tudo offscreen.

## Perguntas para o Samuel

1. Pode consertar o último passo do Melhorar e do Mágico pro (a limpeza do papel deixa de pintar de branco
   o meio das pinturas)? Muda as pinturas das páginas sem gravura marcada (deixam de ter buracos brancos).
2. (À parte) Quer que o Melhorar e o Mágico pro escolhidos à mão também procurem a gravura quando
   "Respeitar" está marcada, como o Preto e branco (D-659)?

Entregue à gerente em 10/11/2026.
