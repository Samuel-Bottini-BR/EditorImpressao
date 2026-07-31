# Melhorias tentadas

Uma entrada por mudança, aceita ou revertida. As revertidas ficam registradas
de propósito: saber o que não funcionou vale tanto quanto saber o que funcionou.

Cada entrada diz qual número a mudança queria melhorar, o que aconteceu com
todos os outros, e a decisão.

---

## Tentativa 1 — o contraste local deixa de agir no papel

**Data:** 30/07/2026
**Situação:** aguardando decisão do Samuel
**Número atacado:** ruído de fundo do Mágico pro, o pior da linha de base
(2,25 no original contra 8,04 depois do filtro)

### O que estava acontecendo

O Mágico pro aplica realce de contraste local (CLAHE) na folha inteira. Onde a
folha é só papel não há o que realçar, então ele pega o grão do escâner e o
amplia. De quebra, puxa o papel para baixo — no filtro que deveria justamente
embranquecê-lo.

Foi medido desligando um passo por vez, em cinco páginas:

| Variante | Ruído | Fundo (255 = branco) |
|---|---|---|
| Como estava | 13,57 | 196,8 |
| **Sem o contraste local** | **6,35** | **219,3** |
| Sem a nitidez | 10,10 | 196,8 |
| Sem a saturação | 13,46 | 201,4 |
| Sem o empurrão para o branco | 13,10 | 195,5 |

O contraste local responde por mais da metade do ruído e por todo o
escurecimento. A saturação e o empurrão para o branco não têm nada a ver.

### O que foi mudado

O realce de contraste local passou a ser pesado em vez de aplicado por igual:
cheio no conteúdo escuro, nenhum no papel. A rampa começa em 80% do nível do
papel. Esse valor foi escolhido medindo: abaixo dele não há mais ganho, só
perda de contraste nas gravuras.

Nada mudou na tela. Nenhum controle novo, nenhum nome diferente.

### O que aconteceu no acervo inteiro

| Número (Mágico pro) | Antes | Depois | |
|---|---|---|---|
| Ruído do fundo | 8,04 | **3,68** | melhorou 54% |
| Nível do fundo | 209,9 | **215,4** | melhorou |
| Nitidez | 3044 | 3144 | melhorou |
| Vazios internos | 5218 | 3263 | ver observação |
| Transição da borda | 2,24 | 1,39 | **piorou** |

Ocorrências de defeito, no acervo todo:

| Defeito | Antes | Depois |
|---|---|---|
| O fundo ficou mais sujo | 57 | **32** |
| O fundo escureceu | 15 | 13 |
| O traço afinou demais | 3 | **1** |
| A borda das letras borrou | 2 | **0** |
| As letras entupiram | 5 | 5 |
| A borda virou degrau (serrilhado) | 5 | **13** |
| **Total** | **68** | **51** |

### Observação sobre os vazios internos

A queda de 5218 para 3263 parece perda, mas não é. O filtro antigo inventava
buracos a partir do grão amplificado. Em toda página de texto o número novo se
aproxima do original, em vez de se afastar dele:

| Página | Original | Antes | Depois |
|---|---|---|---|
| Marial p1 | 229 | 7491 | 645 |
| Graduale p251 | 88 | 771 | 177 |
| Marial p605 | 1216 | 5282 | 2386 |

E o critério que olha página por página, "as letras entupiram", ficou em 5
antes e 5 depois. Nenhuma página perdeu miolo de letra de verdade.

### A piora é real

O serrilhado subiu de 5 para 13 páginas. Foi verificado se não era vício da
medida — a régua contava como rampa qualquer pixel de tom intermediário da
página, e papel ruidoso enche isso. Medindo só junto do contorno da letra, a
contaminação some, **mas a piora continua**: a rampa cai de 0,86 para 0,49
pixel. Segurar o contraste local deixa o papel liso ao redor da letra, e a
borda fica mais dura.

Também foi testado se a causa era o empurrão para o branco. Não é: tirá-lo
piora ainda mais a rampa.

### Decisão

Em aberto. O ganho é grande e vale para os nove livros; a perda é localizada e
tem caminho conhecido — a nitidez é o segundo maior gerador de ruído e é ela
que estreita a rampa.

---

## Pendência da régua

A medida de transição conta pixels de tom intermediário em toda a página, e
papel ruidoso infla o número. Deve passar a contar só junto do contorno da
letra. Não muda o veredito da Tentativa 1, mas muda a magnitude
(1,32 → 0,60 pela medida atual; 0,86 → 0,49 pela medida limpa) e vai
contaminar comparações futuras.
