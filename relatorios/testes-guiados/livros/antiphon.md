# Antiphon_25 — antifonário iluminado (305 folhas, 84 MB) — **trecho: folhas 1 a 120**

O livro inteiro passaria muito de 20 min no processar (as 120 folhas já levaram **33 min**); fiz o percurso inteiro numa
**cópia só com as folhas 1 a 120**. `roteiros/configs/antiphon.json`.

**O livro:** antifonário em pergaminho, pautas vermelhas, iniciais azuis e vermelhas pintadas, fotografado aberto
sobre fundo preto, com a **página vizinha** à vista; capa de couro com cravos. **Caixinhas:** "Cortar a beirada da folha
vizinha", "Achar a página dentro da borda preta do scanner", "Endireitar", "Cortar as bordas", "Limpar a folha" com
**Mágico pro**, "Achar gravuras e fotos". Ao abrir, "fundo separado" → "Sim".

**Como foi:** "Conferir" (68 s) → Cortar, Endireitar e filtros nas páginas 1–4, 29, 56, 84, 112 e 120 → arrastar e desfazer
→ Retângulo na página 56 e desfazer → "Para revisar" ("usar o corte alargado" na 1 e desfazer, de novo na 1, na 2,
"Deixar em branco" na 3) → "está certo" → processar (**33 min 29 s**) → 120 páginas, **1.590 MB** → montar em A4 (1 min
54 s, 60 páginas, 6 cadernos). **Foi até o fim**; 120 entraram, 120 saíram.

## Problemas

| # | O que fiz | O que esperava | O que aconteceu | Tipo | Print | Gravidade |
|---|---|---|---|---|---|---|
| A-1 | Página 56: marquei um Retângulo no meio da página e cliquei no desfazer (áreas 31 → 32 → **32**, P-2) e depois processei | Sem marca nenhuma no PDF | Ficou no PDF um **retângulo cinza** atrás de duas linhas de texto, exatamente onde marquei: a marca que o desfazer não tirou **foi impressa** (o bloco preto entre o D e o G do Palatino 74, P-1, também está onde marquei) | erro | ![](prints/antiphon/b-p56.jpg) *Página 56: o retângulo cinza no meio, onde ficou a marcação* | atrapalha |
| A-2 | Página 2 (guarda manchada), aviso "O corte ... deixou de fora um pedaço impresso": cliquei "usar o corte alargado" | Um corte **maior**, que pega o que ficou de fora | O corte ficou **menor**: a página virou uma tira estreita (do meio para a direita; recorte 40 % → 92 % da largura) e perdeu a metade esquerda | erro | ![](prints/antiphon/a-p2-corte-alargado.jpg) *Página 2: original e depois do botão* | atrapalha |
| A-3 | Olhei o PDF pronto | Algo perto do original | **1.590 MB para 120 páginas** (o livro inteiro passaria de 4 GB) | erro | — | atrapalha |
| A-4 | Janela "Confirmar e processar" | Nome de arquivo sem acento (`CLAUDE.md` §3: "caminhos de disco sem acento") | Nome sugerido **"antiphon-trecho - mágico pro.pdf"** (o mesmo "mágico pro" com acento no Pesel, ljs47, Escola, Graduale) | erro | — | detalhe |
| A-5 | Página 56 pronta | Pergaminho branco | Sobraram **pontinhos laranja** das manchas do pergaminho na margem da direita | erro | ![](prints/antiphon/b-p56.jpg) | detalhe |
| A-6 | Abri a conferência e folheei | Dúvidas paradas, avisos que ajudam | **66 → 75** dúvidas só de folhear; quase toda página com "O corte que segue o conteúdo deixou de fora um pedaço impresso" (é a página vizinha) e "as contas discordam" (B-3, B-5) | confuso | — | atrapalha |

**Tempo (não conto como problema; velocidade é da Fase 5):** 33 min 29 s para 120 páginas no Mágico pro; o livro inteiro
levaria quase 1 h 30 min. A tela mostra "faltam cerca de N minutos".

**A conferir (de novo):** o clique do Windows em "Confirmar e processar" não abriu nada em 30 s.

**O que funcionou bem:** as iniciais azuis e vermelhas e as pautas saíram com cor fiel; a página 3 (em branco) saiu
branca com "Deixar em branco"; a página vizinha e o fundo preto foram tirados.
