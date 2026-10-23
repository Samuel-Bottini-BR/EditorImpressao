# Pesel — "Points d'anciennes broderies anglaises" (92 folhas, 12 MB)

Percurso inteiro na janela de verdade, numa cópia do PDF. `roteiros/configs/pesel.json`.

**O livro:** pranchas coloridas de bordado (foto colorida colada num cartão marrom, com texto embaixo), muitas folhas
marrons vazias (o verso das pranchas, com um carimbo), capa de tecido. **Caixinhas, como o Kaique pensaria:** sem
"Dividir"; "Endireitar"; "Cortar as bordas"; "Limpar a folha" com **Mágico pro** ("cor viva e texto nítido": as cores do
bordado têm de ficar); "Achar gravuras e fotos" e **"Este livro tem fotos"** (as pranchas são fotos).

**Como foi:** "Conferir" (**79 s**) → Cortar, Endireitar e filtros nas páginas 1, 3, 4, 5, 8, 9, 51, 59, 84 e 92 →
arrastar e desfazer → Retângulo na prancha da página 51 → "Para revisar" ("usar mais escuro" e desfazer, "Deixar em
branco" ×2) → "está certo" → processar (**6 min 50 s**) → 92 páginas, **208 MB** → montar em A4 (52 s, 46 páginas, 5
cadernos). **Foi até o fim**; 92 entraram, 92 saíram.

## Problemas

| # | O que fiz | O que esperava | O que aconteceu | Tipo | Print | Gravidade |
|---|---|---|---|---|---|---|
| PE-1 | Processei as pranchas (51, 59, 67, 75) no Mágico pro | Bordado com a cor certa e o cartão em volta igual (ou todo claro) | O bordado ficou bom, mas o cartão virou um **remendo**: o título e cada bloco de texto ganharam um **retângulo branco** por cima do marrom, com a letra engrossada, e o resto ficou marrom; sobrou uma tira branca torta na beirada esquerda | erro | ![](prints/pesel/a-p51.jpg) *Página 51: original e pronta — os retângulos brancos no título e no texto* | atrapalha |
| PE-2 | Olhei o tamanho do PDF pronto | Algo perto do original (12 MB) | **208 MB** para 92 páginas (17 vezes maior) — pesado para guardar e mandar para a gráfica (ponto 22 do mapa, aqui com o Mágico pro) | erro | — | atrapalha |
| PE-3 | Página 1, aviso "O texto quase sumiu. Tente mais escuro": cliquei "usar mais escuro" e depois o desfazer de baixo | O aviso volta | O aviso **não voltou** (dúvidas 37 → 36 → 36), como no B-1 do Boécio | erro | — (`log.txt`) | atrapalha |
| PE-4 | Página 51 (prancha no Mágico pro) | Aviso com o nome do controle desta página | "Ficou muito escura. **Tente mais fraco na força do preto**" — "Força do preto" é do Preto e branco; no Mágico pro o controle se chama "Intensidade". O Kaique vai procurar um controle que não está ali | confuso | — | atrapalha |
| PE-5 | Página 51: Retângulo e desfazer | A marcação some | Áreas 14 → 15 → **15** (P-2 do Palatino de novo) | erro | — | atrapalha |

**A conferir (de novo):** o clique do Windows em "Confirmar e processar" não abriu nada em 30 s.

**Já conhecido:** contagens diferentes (alto 37–41, rodapé 33, "Antes de processar" 37 páginas / 53 avisos); "as contas
discordam" de novo.

**O que funcionou bem:** as cores dos bordados (vermelho, azul, verde) ficaram vivas e o pano da prancha ficou claro;
as folhas marrons vazias ficaram como eram (a cor é do cartão); "Deixar em branco" funcionou.
