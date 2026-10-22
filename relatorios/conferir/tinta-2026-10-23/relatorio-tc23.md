# Conferência tc23: "Tinta com a cor original" em dois jeitos (item 2.18)

Verificador, 23/10/2026. Ramo conferido: `fase2-ferramentas-2026-10-22` (código em `8226f33` e `41fa7bc`, ponta
`639136a`); antes = `f26407c`. Ramo do verificador: `verif-tinta-2026-10-23`.

## Veredito

**PRONTO PARA CONFERIR.** O jeito A ("cor como no livro") sai igual ao de antes, ponto por ponto; o B ("cor
escurecida") deixa a tinta mais escura e com a cor mais forte, só dentro da área; os dois botões aparecem na janela de
verdade e cada área guarda o seu jeito, inclusive fechando e abrindo o programa. Ressalvas abaixo.

## Máquina ou olho, item por item

| O que | Como | Resultado |
|---|---|---|
| A igual ao de antes | máquina: soma de cada PDF, código antigo x novo, caminho inteiro | 25 de 25 iguais (5 páginas × Preto e branco, Original e Melhorar; uma área só e quatro áreas juntas: duas "tinta com a cor" que se cruzam, uma "tinta preta" e um "pintar por cima") |
| Projeto antigo sem `tinta_escurecida` | máquina: `projeto.json` gravado pelo código antigo, aberto no novo | 4 de 4: as áreas abrem como A e o PDF sai igual ao do antigo |
| Fora da área nada muda | máquina: ponto a ponto, A x B e sem área x B, 200 DPI | 0 pontos diferentes fora da área nas 10 (5 páginas × 2 filtros); uma exceção antiga no Graduale, ver ressalvas |
| B como prometido | máquina + olho | brilho da tinta cai para 52 a 65 % do A; a cor sobe 10 a 23 % (medido no PDF); o papel da área continua branco |
| Duas áreas que se cruzam | máquina | manda a última desenhada, nos dois sentidos (2 de 2) |
| Os dois botões na janela | janela de verdade (fora da tela, cliques do Windows, WM_CLOSE) | 24 de 24 (livro novo) e 5 de 5 (programa fechado e aberto de novo) |
| Código de antes na janela | janela de verdade | 9 de 9: lá não existem os dois botões (confere que a foto do "antes" é do antigo) |
| Teste novo `test_tinta_escurecida.py` | máquina | 8 passam no novo; no antigo 7 falham e 1 passa (o "livro novo sai igual", que tem de passar nos dois) |
| Suíte e velocidade | GitHub (lidas; o código não mudou depois de `41fa7bc`) | suíte 39850503362: 2185 passaram, 0 falharam, botões 234 ações sem falha; velocidade 39849559789: "igual" (abrir +0,4 %, trocar de página +1,3 %, Mágico pro −0,7 %, Preto e branco +0,1 %) |

As áreas são minhas, não as do Implementador B, para a prova não depender das dele.

## Caminho de cada foto

Livro novo de cada página-gabarito, ajustes de fábrica: girar (0°, a análise não precisou) → dividir (não, de
fábrica) → endireitar (sim) → cortar as bordas (sim) → filtro (Preto e branco ou Original) → área marcada à mão como
"tinta com a cor, papel branco", jeito A ou B. Só páginas que vão ser impressas.

## O que vi em cada página

- **Livro de Horas 13** (título "TABLE / DE CE QUI EST / CONTENU EN CE LIVRE", vermelho e azul): A traz de volta o
  vermelho e o azul claros do livro; B fica vermelho-escuro e azul-marinho, bem legível. No Original, a área vira um
  retângulo branco sobre o creme.
- **Na Escola de Jesus 7** (título cinza-marrom): A fica claro como no livro, mais fraco que o Preto e branco; B fica
  marrom-escuro, quase tão forte quanto o Preto e branco.
- **Opus Majus 3** (folha de rosto, parte de baixo: "UNIVERSITY OF PENNSYLVANIA PRESS" e "MCMXXVIII" em vermelho):
  A vermelho como no livro; B vermelho-escuro; "PHILADELPHIA" e "LONDON..." (pretos) ficam pretos.
- **Livro de Horas 11** (folha de rosto, escolhida por mim: título vermelho e azul dentro da moldura oval): A como no
  livro; B vermelho-escuro e azul-marinho. **Os cantos da moldura laranja e o dourado das letras de "LOUIS" que caem
  dentro do retângulo também escurecem na B** (o dourado vira oliva-escuro). O "L" de "LOUIS" ficou fora da minha área
  e saiu preto (escolha minha da área, não defeito).
- **Graduale 221** (a mais, rubricas vermelhas no meio do texto): A traz o vermelho das rubricas e das linhas da pauta,
  com a tinta marrom clara; B deixa o vermelho escuro e a tinta marrom-escura.

## Na janela

Livro de Horas 13 (cópia do gabarito), o programa de verdade fora da tela. Cliquei no cartão Preto e branco,
escolhi o Retângulo na trilha, abri o Propriedades pelo ícone e cliquei em "tinta com a cor, papel branco": aparecem,
logo abaixo, "cor como no livro" (escolhido de fábrica) e "cor escurecida". Cliquei em "cor escurecida", arrastei um
retângulo no título (saiu B); cliquei em "cor como no livro", arrastei outro (saiu A, e a primeira continuou B). O
"Ver de perto" mostra as duas áreas lado a lado no mesmo título. Troquei a página para Original: os dois botões
continuam aparecendo e as áreas guardam o jeito. Escolhendo "letra e traço", os botões somem; voltando, o último
jeito escolhido continua. Fechei com WM_CLOSE, abri o programa de novo com o mesmo livro: as duas áreas voltaram, B e
A, e o `projeto.json` guarda o campo.

**Pergunta 9 (aberta, não decidi):** os prints mostram os dois casos, Preto e branco e Original.

## Ressalvas

1. **B escurece tudo o que for "tinta" dentro da área**, não só a letra: na Horas 11, os cantos da moldura e o dourado
   das letras. Já estava na pergunta 8 que o Samuel respondeu; continua valendo.
2. **A cor fica 10 a 23 % mais forte, não 25 %**, medida no PDF pronto (o programa multiplica por 1,25, mas a cor muito
   escura não cabe toda na tela/papel e é cortada). O brilho cai para 52 a 65 % (a conta é 50 %; a medida mistura a
   beirada clara de cada letra).
3. **Graduale 221 em Preto e branco, defeito antigo:** com qualquer área por cima (A ou B), a faixa escura da beirada
   esquerda (fora da área) sai um pouco diferente de sem área (cerca de 4.900 pontos com diferença visível, e outros
   26.000 com diferença de 1 em 255). O A é igual ao do código antigo, então já era assim; não é desta mudança.
4. **No Original, a área vira um retângulo branco** no papel creme (A e B; já era assim). Virou a pergunta tc23-1.
5. **Botões soltos por um instante:** cada vez que se escolhe um tipo no "Marcar como", os botões do painel aparecem
   por um instante como janelinhas soltas (o meu roteiro as pôs fora da tela). Acontece igual no código de antes; é o
   mesmo achado de 22/10 (vlm22), para a Lista de bugs.
6. Clicar num cartão de filtro também abre o "Ver de perto" (é assim de propósito); o roteiro fotografou e fechou com
   WM_CLOSE.
7. Não testei roda do mouse nem a Melhorar/Mágico pro na janela (as somas do Melhorar foram feitas na máquina).

## Onde está

- Fotos: `relatorios/conferir/tinta-2026-10-23/img/` (fora do git).
- Números: `maquina/somas-antigo-f26407c.json`, `maquina/somas-novo-639136a.json`,
  `maquina/projeto-antigo/abrir-antigo.json`, `maquina/cruzadas/cruzadas.json`, `img-b/numeros-b.json`,
  `maquina/janela-*/conferencias.txt`.
- Roteiros: `scripts/tinta.py`, `scripts/janela.py`, `scripts/base.py`.
