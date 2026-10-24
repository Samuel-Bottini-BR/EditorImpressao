# Escola de Jesus — "Na escola de Jesus, catecismo explicado com imagens" (199 folhas, 48 MB)

Percurso inteiro na janela de verdade, numa cópia do PDF. `roteiros/configs/escola.json`.

**O livro:** catecismo de 1950 com **quadros coloridos** em quase toda página, texto em duas cores, papel rosado
amarelado, o endereço de um site no pé de cada página. **Caixinhas:** sem "Dividir"; "Endireitar"; "Cortar as bordas";
"Limpar a folha" com **Mágico pro** ("cor viva": os quadros são o livro); "Achar gravuras e fotos" e "Este livro tem
fotos".

**Como foi:** "Conferir" (18 s) → Cortar, Endireitar e filtros nas páginas 1, 7, 19, 55, 183 e 199 → arrastar e desfazer
→ Retângulo no quadro da página 19 → "Para revisar" ("usar mais fraco" e desfazer, "está bom assim") → "está certo" →
processar (**11 min 7 s**) → 199 páginas, **907 MB** → montar em A4 (1 min 56 s, 100 páginas, 10 cadernos). **Foi até
o fim**; 199 entraram, 199 saíram.

## Problemas

| # | O que fiz | O que esperava | O que aconteceu | Tipo | Print | Gravidade |
|---|---|---|---|---|---|---|
| E-1 | Conferi pelo rodapé e pelo "Para revisar" | Os mesmos avisos que vão me cobrar no fim | Rodapé: **"1 com dúvida"**; "Para revisar": **2 páginas**. Ao processar, "Antes de processar": **"Ainda tem 166 páginas que eu não tive certeza"**, quase todas "Alinhamento duvidoso" — um aviso que **não aparece no painel nem no rodapé** (só no número do alto, "167 páginas para você olhar"). O Kaique acha que está tudo conferido e é surpreendido no fim (é a explicação do ponto 9 do mapa: o alto conta os avisos de folha, o rodapé e o painel não) | erro | ![](prints/escola/b-antes-de-processar-166.jpg) *A janela do fim com 166 "Alinhamento duvidoso" que o painel não mostrava* | atrapalha |
| E-2 | Página 1, aviso "Ficou muito escura. Tente mais fraco na força do preto": cliquei "usar mais fraco" | A página clareia e o aviso sai | **Nada mudou**: o aviso continuou na faixa, só o botão sumiu, e a contagem ficou igual (2). "Força do preto" de novo numa página Mágico pro (PE-4 do Pesel) | erro | — (`log.txt`) | atrapalha |
| E-3 | Olhei o PDF pronto | Algo perto do original (48 MB) | **907 MB** para 199 páginas (19 vezes maior) | erro | — | atrapalha |
| E-4 | Página 19: Retângulo e desfazer | A marcação some | Áreas 19 → 20 → **20** (P-2 do Palatino de novo) | erro | — | atrapalha |

**A conferir (de novo):** o clique do Windows em "Confirmar e processar" não abriu nada em 30 s.

**Já conhecido:** o endereço "http://alexandriacatolica.blogspot.com.br" continua no pé de todas as páginas (R8 do
ESTADO-ATUAL: "apagar em todas as páginas um texto repetido" — ainda não existe no programa).

**O que funcionou bem:** os quadros coloridos saíram com cor boa e o papel ficou branco (R1 e R6 nesse livro); o texto
ficou nítido; nenhuma página faltando.
