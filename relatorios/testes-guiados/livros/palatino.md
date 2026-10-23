# Palatino — "Giovambattista Palatino cittadino romano" (134 folhas, 9 MB)

Percurso inteiro na janela de verdade, numa cópia do PDF. `roteiros/configs/palatino.json`.

**O livro:** uma página por folha, papel amarelado, molduras em volta do texto, alfabetos e gravuras em madeira
(página 74: letras brancas sobre fundo escuro), capa marmorizada. **Caixinhas:** sem "Dividir"; "Endireitar";
"Cortar as bordas"; "Limpar a folha" com **Preto e branco** (o Samuel quer papel branco, R1: "Palatino p. 5, 7 e 9");
"Achar gravuras e fotos" marcada (há gravuras).

**Ao abrir**, o programa perguntou: "Este livro tem fundo separado. Quer tirar o fundo?" — respondi **"Sim, tirar o
fundo"** (é o que o Kaique faria: ele quer o papel branco). Depois escolhi o Preto e branco, como planejado.

**Como foi:** "Conferir" (**57 s**) → Cortar, Endireitar e filtros nas páginas 1–6, 10, 67, 74, 98 e 134 → arrastar e
desfazer no Cortar e no Endireitar → **Retângulo** na página 74 (gravura) e desfazer → "Para revisar": páginas 2, 3 e
4 ("Deixar em branco", desfazer, "Deixar em branco", "está bom assim") → "está certo" → processar (**3 min 31 s**) →
134 páginas, 24 MB → montar em A4 (**41 s**: 68 páginas, 34 folhas, 7 cadernos). **Foi até o fim.** 134 entraram, 134
saíram.

## Problemas

| # | O que fiz | O que esperava | O que aconteceu | Tipo | Print | Gravidade |
|---|---|---|---|---|---|---|
| P-1 | Processei a página 74 (gravura em madeira, letras brancas sobre fundo escuro) com o Preto e branco do livro e "Achar gravuras" ligada | A gravura sair inteira, como no original | O fundo escuro virou **chuvisco preto e branco**, com manchas pretas grandes nas letras A, K e no canto, e um **bloco preto retangular** entre o D e o G. O programa marcou a página como gravura (quase inteira em salmão no Retângulo), mas ela saiu estragada mesmo assim | erro | ![](prints/palatino/a-p74-gravura.jpg) *Página 74: original e pronta* | atrapalha |
| P-2 | Página 74: escolhi o Retângulo, marquei um retângulo em cima da gravura e cliquei no desfazer de baixo | A marcação que eu fiz some | "Marcado: 4 de gravura" virou **5** com o retângulo e **continuou 5** depois do desfazer (as áreas da página: 9 → 10 → 10). O desfazer não tirou a marcação, e nada na tela avisou | erro | ![](prints/palatino/b-marcar-retangulo-p74.jpg) *Antes e depois do retângulo: a mesma tela, só o "Marcado: 4" virou "5"* | atrapalha |
| P-3 | Marquei um retângulo numa página que o programa já tinha marcado quase inteira como gravura | Ver onde ficou o meu retângulo | **Nada muda na tela**: o retângulo novo some dentro do salmão; só o número "Marcado: 5 de gravura" mostra que houve algo | confuso | ![](prints/palatino/b-marcar-retangulo-p74.jpg) | detalhe |
| P-4 | Página 4 (folha em branco no começo do livro) | Um aviso: "parece em branco" | **Três avisos** na mesma folha branca: "as contas discordam" (inclinação de uma folha sem texto), "inclinação diferente das outras" e "parece em branco". O "está bom assim" tira um, aparece o outro (B-5 do Boécio de novo, agora em folha vazia) | confuso | — (`log.txt` bruto) | atrapalha |

**A conferir (de novo, como no Boécio):** o clique do Windows em "Confirmar e processar" não abriu nada em 30 s; o
clique pelo Qt abriu na hora.

**Já conhecido, só confirmado:** as contagens de dúvidas não batem (ponto 9 do mapa), aqui com diferença grande: alto
**29**, rodapé **17**, "Antes de processar" **22 páginas / 29 avisos**.

**O que funcionou bem:** texto e molduras saíram limpos e brancos (páginas 10, 13, 49, 67, 98 — R1 do Palatino), o
retrato da página 5 saiu bom, "Deixar em branco" e o desfazer dele funcionaram, contagem de páginas certa, cadernos
certos.
