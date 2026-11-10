# Quadrados brancos no Melhorar e no Mágico pro — investigação

**Verificador, 10/11/2026.** Só investigação: nenhuma linha do programa foi mudada. Tudo rodou
sem janela, em cópia, pela mesma conta do programa (a prévia da tela e o PDF final).

Pedido do Samuel (10/11): "anotar erro do filtro melhorar, ele deixa a imagem pixelada, olha esses
quadrados brancos. também acontece no automatico e no magico pro, pode colocar um agente para
investigar isso." · depois: "o erro não aparece só na pagina 13, aparece em varias."

## Em uma frase

**O defeito é real e sai também no PDF, não só na tela.** O último passo do Melhorar e do Mágico pro
("o que não é letra e tem cor de papel vira branco") confunde a água, o céu e as roupas claras das
pinturas com papel, e pinta de branco; os blocos aparecem porque o arquivo do livro guarda a cor em
quadradinhos, e a resposta "é papel / não é papel" muda de um quadradinho para o outro.

Opinião: **dá para consertar sem mexer no que já foi aprovado**, mas é mudança de filtro e precisa
do "sim" do Samuel. O conserto proposto (simulado, não aplicado) some com os quadrados nas 199
páginas do *Na escola de Jesus*; no Livro de Horas ele melhora mas não resolve tudo (ressalva 2).

Imagens (no modelo de print, resumo primeiro):

- `imagens/1-resumo-pagina-13.png` — página 13: Original, como sai hoje (Melhorar e Mágico pro) e como sairia consertado.
- `imagens/2-previa-igual-ao-pdf.png` — a prévia da tela e o PDF têm os mesmos quadrados.
- `imagens/3-livro-escola-melhorar.png` e `imagens/4-livro-escola-magico-pro.png` — oito páginas do livro, nas três situações.
- `imagens/5-outro-livro-horas-47.png` — outro livro do acervo (Livro de Horas, página 47).

## 1. Reprodução na página 13 (Jonas e a baleia)

Livro novo, aberto como a tela abre (sem o Automático), página 13, desenhada pelos dois caminhos do
programa: a prévia da tela (`core.pipeline.renderizar_com_filtro`, 150 DPI) e o PDF
(`core.pipeline._pagina_pronta`, 300 DPI). Conferido por **máquina** (medida) e por **olho** (imagens).

| como | quadrados? | quanto da gravura vira branco puro (PDF) |
|---|---|---|
| Original | não | — |
| Melhorar "bem forte", "Respeitar" marcada (print 09) | **sim, na tela e no PDF** | 25% |
| Melhorar "bem forte", "Respeitar" desmarcada | **sim** — imagem idêntica ponto a ponto à de cima | 25% |
| Mágico pro "bem fraco", "Respeitar" desmarcada, no painel | **sim** | 26% |
| Mágico pro "bem fraco", "Respeitar" desmarcada, com "Limpar a folha" do Automático (print 10) | **sim** — idêntica ponto a ponto à do painel | 26% |
| Melhorar ou Mágico pro com o Automático, "Respeitar" marcada e a gravura achada | não | 0,6% |
| Melhorar e Mágico pro no ajuste do meio ("normal") | **sim** — o ajuste não muda nada | 25% |

- **Sai no PDF final**, não só na prévia (imagem 2). Na prévia 25,7% da gravura, no PDF 25,0%.
- **O ajuste ("bem forte", "bem fraco", "normal") não importa**: o passo que pinta de branco não usa o ajuste.
- **Na página 13 a caixinha "Respeitar as gravuras achadas" não muda nada** no Melhorar e no Mágico pro
  escolhidos à mão sem o Automático: o programa não procura a gravura nesse caso (a D-659 vale só no
  Preto e branco: `core/etapas.py`, `respeitar_procura`, "Melhorar e Magico pro a mao nao procuram: a
  decisao fala do Preto e branco"). Sem gravura achada, não há o que respeitar.
- No print 10 a caixinha está desmarcada: pela D-586, "o filtro vale na página inteira", e cai no mesmo caminho.
- Quando a gravura é achada e respeitada, os quadrados somem: o conserto de 28/09 (bug 202, "quadradinhos
  na roupa do anjo") funciona **dentro da gravura marcada**. O defeito de hoje é o mesmo bug, voltando
  pelo caminho **sem marcação**.

## 2. A causa

**Arquivo e função:** `core/filtros.py`, `_limpar_o_papel_de_verdade` — o último passo de
`filtro_melhorar` e de `filtro_magico_pro` (e por isso do Automático com esses filtros).

Ele pinta de branco puro todo ponto que responde "sim" a três perguntas:

1. está longe de letra (o Sauvola não achou tinta perto)?
2. não é escuro (mais claro que 45% da luz do papel)?
3. tem cor de papel (pouca cor, saturação até 25, ou o tom amarelado do papel)?

A água e o céu da pintura são cinza-azulados, sem letra perto, nem claros nem escuros: passam nas três.
O passo foi feito para a mancha do verso numa página de texto, e numa página de texto isso está certo;
numa pintura sem marcação, não.

**Por que em quadrados:** o livro guarda cada página como JPEG, e o JPEG guarda a COR em quadradinhos de
16 por 16 pontos (24 por 24 no PDF a 300 DPI). Na pergunta 3 ("tem cor de papel?"), um quadradinho
passa e o vizinho não, inteiro. Já estava escrito no código em 28/09 ("decidir ponto a ponto sobre a cor
crua era o que fazia os quadradinhos"), mas a correção só entrou no caminho de dentro da gravura.

**As provas (medidas na página 13, PDF):**

- **Tirando só esse passo, os quadrados somem:** 25% da gravura vira branco hoje; sem o passo, 0,5%.
- **O que vira branco não é papel:** os pontos pintados dentro da gravura têm luz entre 49% e 66% do
  papel (metade dos casos); o papel de verdade da página, entre 94% e 101%.
- **As bordas caem na grade do JPEG:** a borda da pergunta "tem cor de papel?" cai na grade de 24 pontos
  em 34% das vezes; ao acaso seria 12,5%. A pergunta "não é escuro" (que não depende da cor) cai em 14,6%,
  perto do acaso. Na imagem pronta, 25,6% das bordas do branco estão na grade (o dobro do acaso), e há
  37 blocos brancos grandes (mais de meio quadrado de 24×24) dentro da gravura.
- **A miniatura de 400 pontos (a pista do CLAUDE.md §7) não é a causa:** o fundo estimado nela é liso
  por construção; com ele intacto e só o último passo desligado, os quadrados somem.

## 3. O livro inteiro e outro livro

### *Na escola de Jesus*, 199 páginas, livro novo, filtro escolhido à mão

Medida: pontos que viraram branco onde o original era pintura de tom médio (fora a beirada do scan),
sobre a página pronta. Calibrei olhando as 199 páginas em folhas de contato: a partir de 1% os buracos
se veem de longe; de 0,25% a 1% se veem ao olhar a pintura; de 0,1% a 0,25% são poucos pontos.

**Melhorar "bem forte": 110 páginas com quadrados (79 bem visíveis).**

- muito (32): 8, 13, 18, 24, 27, 29, 30, 36, 50, 51, 52, 53, 55, 65, 66, 67, 73, 74, 77, 78, 79, 101, 110, 119, 120, 121, 131, 143, 147, 153, 160, 175
- visível (47): 9, 10, 23, 25, 32, 33, 39, 40, 42, 46, 56, 57, 58, 60, 61, 68, 69, 84, 88, 96, 97, 98, 99, 103, 106, 112, 116, 118, 126, 128, 132, 134, 136, 144, 145, 146, 148, 151, 165, 174, 177, 179, 181, 186, 192, 194, 196
- poucos pontos (31): 11, 16, 19, 26, 37, 43, 45, 47, 49, 54, 64, 70, 72, 80, 86, 93, 95, 100, 102, 109, 122, 125, 140, 142, 158, 159, 168, 170, 172, 182, 184
- nada (89): as páginas só de texto, as capas e as páginas com pintura escura ou grande demais, em que a limpeza não roda (trava "tinta demais").

**Mágico pro "bem fraco": 112 páginas com quadrados (84 bem visíveis)** — praticamente as mesmas
(muito 34, visível 50, poucos 28, nada 87; a mais: 146 e 179 sobem para "muito", 16, 26, 72, 100, 125 e 142 para "visível"; a 42 desce para "poucos pontos").

### Outro livro: Livro de Horas (Luís XIV)

Páginas do gabarito 11, 13, 14, 26, 27 e 47, Melhorar e Mágico pro. **O defeito aparece na página 47**
(a pintura das bodas de Caná, com colunas e prédio claros atrás das figuras): o prédio, o céu e riscos
nas colunas e roupas claras viram branco puro (imagem 5). Nas outras, quase nada: são tabelas e
calendários dentro de moldura dourada.

## 4. O que consertaria (não aplicado)

**Proposta:** no último passo (`_limpar_o_papel_de_verdade`, só no caminho da página, o de fora da
gravura marcada), acrescentar uma quarta pergunta: **"em volta deste ponto é papel?"**. O ponto só vai a
branco se a luz do meio da vizinhança (mediana numa janela de uns 2% da página, medida na miniatura de
400 pontos, como o fundo dos filtros) passa de 80% do nível do papel **ou** se a área é de traço sobre
papel (a medida da tentativa 20, `_peso_de_traco`: xilogravura, tabela, letra). Na mancha do verso e no
vão entre as letras, a vizinhança é papel: continua indo a branco como hoje. No meio de uma pintura, a
vizinhança é a própria pintura: fica como o Melhorar a deixou.

Resultado da simulação (o mesmo programa, só com esse passo trocado, num processo à parte):

- **Página 13:** 25% da gravura em branco → 0,9% (o que sobra é a espuma, que já é branca no original).
- **Livro inteiro, Melhorar e Mágico pro:** de 110 e 112 páginas com quadrados → **nenhuma** (a pior fica em 0,08%, abaixo do "poucos pontos").
- **Páginas sem quadrados hoje:** mudam pouco, e para melhor: roupas e lençóis brancos das pinturas (páginas 163, 71) passam a guardar a sombra em vez de virar branco chapado.
- **Boécio (mancha do verso, páginas 3, 7, 8, 22 e 33):** muda de 0% a 0,4% da página; a mancha do verso some igual. A primeira versão do conserto (sem o "ou traço") deixava a xilogravura da página 3 mais cinza; a versão com o "ou traço" não.
- **Livro de Horas 47:** melhora mas não resolve: o prédio volta, ficam riscos brancos nas colunas e na roupa clara da esquerda (a miniatura tem traço fino, e o "ou traço" deixa limpar ali).
- **Velocidade:** o último passo ficou uns 0,05 s mais lento por página a 300 DPI (Melhorar inteiro ≈ 0,9 s). Medido de forma simples no PC; precisa do filtro de velocidade do GitHub.

**O que isso mexe do que já foi aprovado:**

- A correção do "magic color" (CLAUDE.md §9: fundo relativo ao papel, peso, curva de ombro) **não é tocada**: a mudança é só no último passo.
- A limpeza da mancha do verso e do "fundo meio amarelado" (o motivo desse passo existir) continua; nas páginas de texto medidas não muda nada no miolo.
- Pela D-605, é uma mudança que altera resultado já visto (as pinturas sem marcação deixam de ir a branco): **pergunta para o Samuel antes**.

**Outra saída (decisão dele, não substitui a de cima):** estender a D-659 ao Melhorar e ao Mágico pro —
com "Respeitar" marcada, o programa procuraria a gravura também nesses filtros escolhidos à mão. Resolveria
o print 09, mas **não o print 10** (lá a caixinha está desmarcada e, pela D-586, o filtro vale na página
inteira) nem a página com a gravura que o programa não acha.

**Risco do conserto proposto:** (a) a beirada da pintura que encosta na margem branca ainda pode ganhar
manchas brancas numa faixa de uns 2 a 3 mm (visto nas páginas 27 e 74); (b) na faixa escura de scanner
na beirada da página, um pouco menos de branco (até 0,8% da página, só nos 6% da beirada); (c) pinturas com
traço fino (Livro de Horas) continuam com riscos brancos; (d) os números 80% e 2% são meus, escolhidos
nesta investigação, sem rodar as 32 páginas do gabarito.

## 5. Ressalvas

1. **O conserto é simulação**: trocado só dentro de um processo de teste (`scripts/candidato.py`), sem teste em `tests/`, sem rodada do GitHub, sem o gabarito inteiro. Antes de entrar no programa: teste de reversão (página 13: falha hoje, passa com o conserto), as provas das decisões (`tests/test_decisoes*.py`), o gabarito e o filtro de velocidade.
2. **Livro de Horas 47 fica pela metade** com o conserto proposto (ver acima).
3. **A medida do livro inteiro é feita na miniatura da página pronta (75 DPI)**: serve para separar páginas com e sem buracos (calibrada olhando as 199 páginas), não para comparar números finos.
4. **Achado à parte, não investigado:** no Livro de Horas, Melhorar "bem forte", a margem de fora da moldura sai com manchas cinza e brancas misturadas (imagem 5, página inteira à esquerda). Parece da mesma família (a limpeza decidindo por pedaços), mas o defeito é o contrário: papel que fica cinza. O conserto proposto não muda isso.
5. Não abri o programa na tela do Samuel: tudo pela conta do programa, sem janela (`QT_QPA_PLATFORM=offscreen`), com dados num `LOCALAPPDATA` à parte. O que a tela mostra é desenhado por essa mesma conta (`renderizar_com_filtro`), mas não pilotei a janela.
6. Os scripts em `scripts/` gravam os dados de teste numa pasta `dados/` ao lado deles; foram rodados de uma cópia fora do projeto.

## 6. Para a Lista de bugs

- **10/11/2026 — Quadrados brancos nas pinturas no Melhorar e no Mágico pro sem gravura marcada** (livro
  novo com filtro à mão, ou "Respeitar" desmarcada). Sai também no PDF. *Na escola de Jesus*: 110 de 199
  páginas; Livro de Horas: página 47. Causa: `core/filtros.py`, `_limpar_o_papel_de_verdade` (cor
  decidida sobre a cor crua do JPEG, em blocos de 16×16). Mesmo bug do 202 (28/09), pelo caminho sem
  marcação. Prints: `relatorios/testes-guiados/2026-11-10-sessao-5/prints/09-...` e `10-...`; imagens
  deste relatório.

## 7. Como medir de novo

`scripts/reproduzir.py` (página e variantes, prévia e PDF), `scripts/medir.py` (blocos e grade),
`scripts/partes.py` (as três perguntas), `scripts/varrer.py` (livro inteiro), `scripts/medir_miniaturas.py`
(a medida por página), `scripts/candidato.py` (o conserto simulado; `CANDIDATO=1`), `scripts/montar.py`
(as imagens). As medidas por página estão em `medidas/`.
