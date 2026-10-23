# Verificador tp23: o papel da área "tinta com a cor" (item 2.18)

**PRONTO PARA CONFERIR, com ressalvas.** Com "papel como o resto da página", o retângulo branco some. O "papel branco" de fábrica sai igual ao de antes, ponto por ponto. A principal ressalva é o contorno preto que aparece no Preto e branco (pergunta b-10, ainda aberta). Nunca "aprovado": quem marca é o Samuel.

Sua resposta (tc23-1): "As duas: escolher o papel em cada área ('papel branco' ou 'papel como o resto da página')".
Código: ramo `fase2-ferramentas-2026-10-22`, commits `b0af839` e `3e95076`. O "antes" é o `639136a`.

## O que foi conferido, e como

| O que | Como | Resultado |
|---|---|---|
| "Papel branco" (de fábrica) igual ao de antes | máquina: somas dos PDFs, 4 páginas x 3 filtros x (A, B, várias áreas juntas com "tirar"), código antigo x novo | 36 de 36 iguais (e as 36 diferentes entre si) |
| Projeto antigo abre como "papel branco" | máquina: projeto.json gravado pelo código antigo, aberto no novo | 4 de 4: sem o campo, abre "papel branco" e sai igual |
| "Papel como o resto da página" no Original e no Melhorar | máquina + olho, 4 páginas | o papel da área fica 100% igual ao da página; no Original, com A, a página sai igual a sem área |
| As quatro combinações com A e B | máquina + olho | a tinta sai 100% igual à do "papel branco", no A e no B; fora da área, 0 pontos diferentes |
| A área de cima manda | máquina + olho, 12 casos | 36 de 36 faixas certas |
| O "tirar" do pincel | máquina + olho, 6 casos | onde passou, a página volta 100% à sem área; o resto da área não muda |
| Teste novo do implementador | máquina, um arquivo por vez | 10 passam no novo; 10 falham no antigo |
| Janela de verdade (fora da tela, cliques do Windows, WM_CLOSE) | olho + máquina | 28 de 28 (livro novo); 7 de 7 (aberto de novo, uma conferida à mão); 11 de 11 (código antigo) |
| Suíte no GitHub | lida, código igual | rodada 39877466484 (`4c4cc52`, mesmo código de `3e95076`): 2195 passaram, 0 falharam; botões 234 ações, 0 falhas |
| Velocidade | lida | rodada 39876068685 (`639136a` -> `b0af839`; o `3e95076` só muda a tela): igual. Abrir 40,0 -> 39,7 s; trocar de página 3,54 -> 3,55 s; Mágico pro 47,5 -> 47,5 s; Preto e branco 28,8 -> 28,7 s |

## O que vi em cada página

As fotos foram tiradas pelo caminho inteiro: girar 0 -> dividir não (de fábrica) -> endireitar sim -> cortar as bordas sim -> filtro -> área "tinta com a cor" marcada à mão.

- **Horas 13:** no Original, o retângulo branco some e as linhas do verso voltam a aparecer dentro da área, como no resto da página. Com B, só o título escurece. No Preto e branco, de perto, ficam pontinhos pretos na beirada das letras (b-10).
- **Escola 7:** no Original, o título fica no papel rosado da página, sem faixa branca. No Preto e branco, o contorno preto é bem visível de perto (b-10).
- **Opus Majus 3:** no Original, sem retângulo branco; o vermelho fica vermelho e o preto, escuro. No Preto e branco, quase não há contorno.
- **Graduale 221:** no Original e no Melhorar, sem retângulo branco. A B escurece também as linhas vermelhas da pauta, como já fazia antes. No Preto e branco, há pontinhos pretos na pauta.
- **Janela (Horas 13):** os quatro botões aparecem e o segundo do papel cabe inteiro. No "Ver de perto", só a área com "papel branco" faz retângulo. As áreas continuam iguais depois de fechar e abrir o programa.

## Ressalvas

1. **Preto e branco com "papel como o resto da página":** aparece um contorno preto fino em volta da letra colorida. Contei os pontos do papel da área que ficam escuros: Graduale 21.198, Horas 13 7.342, Escola 7 5.421, Opus Majus 784. É a pergunta b-10; não decidi.
2. **O nome do tipo** continua "tinta com a cor, papel branco", mesmo com "papel como o resto da página" escolhido. A linha "Marcado:" também diz "3 de tinta com a cor original, papel branco" quando duas das três áreas são do papel da página. É a pergunta b-11; não decidi.
3. **No Melhorar,** "cor como no livro" põe na letra a cor do livro, não a do Melhorar. Com o papel da página, a letra fica um pouco mais apagada que a de fora da área. É o que foi combinado, mas dá para notar.
4. **A B escurece tudo o que é tinta dentro da área,** inclusive a pauta vermelha do Graduale e a moldura dourada. Já era assim antes (pergunta 8).
5. **Graduale 221 em Preto e branco:** com qualquer área por cima, a faixa escura da beirada esquerda sai um pouco diferente de sem área (77.787 pontos). É igual nos quatro jeitos e já acontecia no código antigo.
6. **Defeito antigo da tela:** os botões do "Marcar como" aparecem por um instante como janelinhas soltas (21 vezes no roteiro novo, 7 no antigo). Para a Lista de bugs.
7. **Erro meu no roteiro da janela:** uma conferência "falhou" porque o programa grava cada área em duas listas (`selecao` e `zonas_na_folha`) e eu contei só uma. Conferi à mão, e as três áreas estão gravadas com o jeito certo.
8. **Não testei** a roda do mouse, o Mágico pro, nem o "tirar" pela janela (o "tirar" foi conferido nas contas).

## Perguntas

Nenhuma pergunta nova. As abertas b-10 (contorno preto) e b-11 (nome do tipo) não são minhas; os casos estão nos quadros 1 e 3.
