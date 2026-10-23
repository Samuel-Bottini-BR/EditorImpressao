# Verificador tp23: o papel da área "manter a cor da tinta" (item 2.18), com os ajustes 10 e 11

**PRONTO PARA CONFERIR, com ressalvas pequenas.** Com "papel como o resto da página", o retângulo branco some no Original e no Melhorar. No Preto e branco, as duas opções de papel agora saem iguais, sem a linha preta em volta da letra (sua resposta 10). O botão se chama "manter a cor da tinta" (sua resposta 11). O "papel branco" de fábrica sai igual ao de antes, ponto por ponto. Nunca "aprovado": quem marca é o Samuel.

Suas respostas: tc23-1 "As duas: escolher o papel em cada área ('papel branco' ou 'papel como o resto da página')"; 10 "No Preto e branco, tirar a linha preta: as duas opções de papel saem iguais, com a letra limpa"; 11: o nome do botão é "manter a cor da tinta".
Código: ramo `fase2-ferramentas-2026-10-22`, commits `b0af839` e `3e95076`; ajustes 10 e 11 em `f8691be` e `c95ba9e` (ponta `d4c820b`). O "antes" do papel é o `639136a`; o "antes" dos ajustes é o `3e95076`.

## Os ajustes das respostas 10 e 11 (23/10)

| O que | Como | Resultado |
|---|---|---|
| De fábrica nada mudou | máquina: somas dos PDFs, 4 páginas x 3 filtros x (A, B, várias áreas juntas com "tirar"), `3e95076` x `d4c820b` | 36 de 36 iguais (e as 36 diferentes entre si) |
| Preto e branco: "papel como o resto da página" = "papel branco" | máquina: somas dos 5 jeitos x 3 filtros x 4 páginas, antes x agora | 60 de 60 como esperado: no Preto e branco, com A e com B, sai igual ao papel branco (8 de 8); Original e Melhorar sem nenhuma mudança (40 de 40); sem área e papel branco iguais (12 de 12) |
| A linha preta sumiu | máquina + olho: pontos do papel da área que ficavam escuros | Horas 13: 7.342 -> 0; Escola 7: 5.421 -> 0; Opus Majus 3: 784 -> 0; Graduale 221: 21.198 -> 0 |
| Projeto gravado antes abre igual | máquina: projeto.json do código antigo, aberto no `d4c820b` | 4 de 4: abre "papel branco" e sai igual |
| Teste novo do implementador | máquina | 11 passam no `d4c820b`; no `3e95076`, 4 falham (a linha preta, a chamada direta, o nome do botão, a linha "Marcado:") e 7 passam (são as guardas do que não podia mudar) |
| Janela de verdade (fora da tela, cliques do Windows, WM_CLOSE) | olho + máquina | 31 de 31 (livro novo); 8 de 8 (aberto de novo). O botão diz "manter a cor da tinta"; o aviso diz "Área escolhida: manter a cor da tinta."; a linha diz "Marcado: 2 de gravura ou foto, 2 de letra e traço, 8 de papel e 3 de manter a cor da tinta." |
| Suíte no GitHub | lida | rodada 39889891066 (`c95ba9e`, mesmo código de `d4c820b`): 2206 passaram, 0 falharam |
| Velocidade | lida | rodada 39886669584 (`0acf2c7` -> `f8691be`, mesmo código do programa): nada mais lento; Mágico pro -2,7% e Preto e branco -3,3% (a medida que vale é a do seu PC no fim da fase) |

Fotos de antes e agora: `img/d4c_<página>-pb-letra-antes-e-agora.jpg`. Coluna 1: antes do ajuste, com "papel como o resto da página" (a linha preta). Coluna 2: agora, com "papel como o resto da página". Coluna 3: "papel branco", o de fábrica. Em cima "cor como no livro", embaixo "cor escurecida".

## O que foi conferido antes (22/10, código `3e95076`)

| O que | Resultado |
|---|---|
| "Papel branco" igual ao de antes (`639136a` x `3e95076`) | 36 de 36 iguais |
| "Papel como o resto da página" no Original e no Melhorar | o papel da área fica 100% igual ao da página; no Original, com A, a página sai igual a sem área |
| As quatro combinações com A e B | a tinta sai 100% igual à do "papel branco"; fora da área, 0 pontos diferentes |
| A área de cima manda / o "tirar" do pincel | 36 de 36 faixas certas / 6 de 6 |

## O que vi em cada página (agora)

As fotos foram tiradas pelo caminho inteiro: girar 0 -> dividir não (de fábrica) -> endireitar sim -> cortar as bordas sim -> filtro -> área marcada à mão.

- **Escola 7, Preto e branco:** a linha preta grossa em volta de "DES" sumiu; a coluna 2 é igual à 3.
- **Horas 13, Preto e branco:** os pontinhos pretos na beirada da letra azul sumiram.
- **Graduale 221, Preto e branco:** os tracinhos pretos em volta da pauta vermelha sumiram.
- **Opus Majus 3, Preto e branco:** já quase não tinha linha; agora nenhuma.
- **Janela (Horas 13):** o botão, o aviso e a linha "Marcado:" usam o nome novo. As três áreas voltam com o jeito delas depois de fechar e abrir.

## Ressalvas

1. **No Preto e branco, dentro da área, o papel fica branco puro** (igual ao "papel branco", como você pediu). O resto da página tem uns pontinhos cinza que o filtro deixa; dentro da área eles somem (Escola 7: 4,5% do papel da área; nas outras, menos de 2%). Nas fotos não se nota retângulo.
2. **Algumas fotos de 22/10** (quadros 1 a 4) ainda escrevem "tinta com a cor" na legenda; o que mostram não mudou. As com o nome novo estão no quadro 0.
3. **No Melhorar,** "cor como no livro" põe na letra a cor do livro, não a do Melhorar. Com o papel da página, a letra fica um pouco mais apagada que a de fora da área. É o combinado, mas dá para notar.
4. **A B escurece tudo o que é tinta dentro da área,** inclusive a pauta vermelha do Graduale e a moldura dourada. Já era assim antes (pergunta 8).
5. **Graduale 221 em Preto e branco:** com qualquer área por cima, a faixa escura da beirada esquerda sai um pouco diferente de sem área (77.787 pontos). Igual nos quatro jeitos, antes e agora; não é desta mudança.
6. **Defeito antigo da tela:** os botões do "Marcar como" aparecem por um instante como janelinhas soltas (21 vezes, igual a antes dos ajustes). Para a Lista de bugs.
7. **Meu roteiro da janela** de 22/10 contava só uma das duas listas em que o programa grava a área. Consertado: agora as duas conferem (8 de 8).
8. **Não testei** a roda do mouse, o Mágico pro, nem o "tirar" pela janela (o "tirar" foi conferido nas contas).

## Perguntas

Nenhuma pergunta nova.
