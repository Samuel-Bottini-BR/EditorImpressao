# Conferência da caixa do conteúdo (2.5, 2.13, 2.14) — verificador, 22/10/2026 — ONDE PAREI

**TERMINADO em 22/10/2026: PRONTO PARA CONFERIR, com ressalvas** (estava pausado a pedido do Samuel; retomado e terminado). Entrega: `conferencia.json` nesta pasta (id `cx22`; as imagens em `img/`, referidas como `cx22/img/...`). Nenhuma janela do programa foi aberta; nenhum processo ficou rodando.
Nenhuma rodada do GitHub foi disparada por mim.

Código conferido: ramo `fase2-caixa-conteudo` em `49d1ed3` (o último código é `5bc5b33`; `4b37fc0` e `49d1ed3` só têm
imagens e ONDE-PAREI). "Antes" = `c66f28d`. Meu ramo: `verif-caixa-2026-10-22` (sai de `49d1ed3`).

Worktrees (com junções `modelos` e `gabarito\paginas`; **não apagar com Remove-Item -Recurse**):
`.claude/worktrees/vcx22-novo` (meu ramo), `vcx22-antes` (`c66f28d`), `vcx22-04b` (`04bcda2`).

## Já conferido (máquina)

| O quê | Resultado |
|---|---|
| GitHub 39788341137 (vale para `5bc5b33`, o código não mudou depois) | **2234 passaram, 0 falharam, 104 pulados**, 123 arquivos; botões e prints verdes. Filtro de velocidade 39788346337 (`c66f28d` x `5bc5b33`, opções desligadas): "igual (dentro do vai-e-vem)" |
| Reversão da etiqueta (`test_regressao_egenloff3_...`) | passa no novo; **falha no `c66f28d`**: corte termina em y 4683, no meio da etiqueta (4431–4807) |
| Reversão da passada (`test_regressao_a_passada_guarda_a_geometria_...`) | passa no novo; **falha no `04bcda2`** (geometria não guardada) |
| `tests/test_borda_preta.py` no novo | 29 passaram |
| "Só o preto" antes x depois em páginas de verdade a 300 DPI (14 Egenloff + 25 Marial, cor e cinza; `scripts/so_o_preto_igual.py`) | **0 diferenças em 78 contas**; 33,9 s → 8,8 s (**3,9×**; o implementador mediu 4,6×) |
| Velocidade no PC, alternado, um processo por vez, sem outros python rodando (`scripts/rodar_tempos.sh`, `tempo_total.py`; duas opções ligadas, até a moldura, Original, 300 DPI; passada + geração do PDF) | **Egenloff 14:** antes 118,1 e 85,6 s → depois 47,4 e 30,7 s. **Marial 100:** antes 312,7 e 307,3 s → depois 145,1 e 138,8 s (**~2,2× mais rápido**; passada 129 → 94–96 s, geração 178–183 → 45–49 s). Números em `dados/tempo_*.json` |
| PDFs antes x depois (`scripts/comparar_pdfs.py`) | tamanhos iguais nos dois (Egenloff miolo 252,5 x 379 mm; Marial 224 x 302,7 mm). **Egenloff: mudaram as págs. 3 e 12. Marial: mudaram 32 de 100** (4, 6, 7, 8, 16, 22, 23, 25, 28, 30, 32, 33, 36, 37, 40, 43, 45, 47, 50, 51, 64, 66, 71, 75, 78, 85, 86, 87, 88, 95, 96, 99 — contando de 1). Confirma o número do implementador |
| Passo 1: a captura bate com o PDF (`scripts/captura_bate.py`) | sim, nas 38 capturas dos dois lados: diferença média 0,8 a 5,6 (de 0 a 255, a 60 DPI); contra a página vizinha 14 a 42, contra o outro lado (antes x depois) 3 a 32. A proporção bate (0,998 a 1,0) |
| Aviso novo no Marial | a página que ganhou "Corte deixou algo de fora" é a **8 contando de 1** (o implementador escreveu "p. 7": provavelmente contou de 0; conferir na janela) |

## Passo 2: as fotos, uma linha por página (olho; todas abertas)

Caminho de todas: não precisou dividir (uma página por folha) -> endireitada -> cortada (cortar pelo conteúdo + borda
preta até a moldura) -> filtro Original, 300 DPI. Fotos em `img/<livro>_pNNN__inteira.jpg` (antes | depois; preto fica,
vermelho sai). As `__perto.jpg` do `desenhar.py` saíram ilegíveis (faixas da altura inteira da página) e foram
apagadas por mim; no lugar, `img/egenloff_p003_beiradas_perto.jpg`.

**Egenloff**
- p. 3 (folha de rosto): o corte desceu 201 pontos (17 mm). **A etiqueta "1880 neu aufgelegt von George Gilbers" agora
  entra inteira** (antes era partida ao meio). Em troca o corte subiu menos em cima: **o oval do carimbo de cima ficou
  partido** (a metade de cima sai) e o lápis "Af 10" sai quase todo; o carimbo da direita ("Fachschule für angewandte
  Kunst / Schneeberg") continua partido nos dois. Ressalva já conhecida (pergunta do carimbo aberta).
- p. 12 (verso em branco com carimbo oval): o corte subiu 176 pontos; a folha continua com o carimbo inteiro, só mais
  centrado no papel. Nada impresso perdido.
- p. 2 (guarda de papel estampado com a ficha da biblioteca) e p. 6 (texto do editor): sem mudança.

**Marial** (o corte tem sempre o mesmo tamanho, 2647 x 3575 pontos; o que muda é onde ele fica)
- p. 4, 7, 16, 22, 30, 32, 37, 50, 64, 66, 71, 86, 88, 96 (e 6 e 78, abaixo): andou 5 a 30 pontos (até 2,5 mm). Não dá para ver diferença
  na página inteira; o texto fica inteiro nos dois.
- p. 6: andou 12 pontos para os lados e para baixo; frontispício (impressão do verso aparecendo) inteiro nos dois.
- p. 8: andou 36 pontos (3 mm) para a esquerda; a margem direita fica mais justa, "Vi" e o fim das linhas continuam
  dentro; é a página que ganhou o aviso (por causa de 3 pontinhos e um risco na beirada do papel, ver passo 3).
- p. 23: andou 36 para a direita e 23 para baixo; texto e notas da margem inteiros nos dois.
- p. 25, 33, 85: andaram 166 a 185 pontos (14 a 16 mm) para a direita. **Depois fica melhor**: antes o corte pegava a
  faixa escura da página vizinha à esquerda e apertava a coluna da direita contra a beirada; depois a página fica
  centrada. Notas da margem esquerda ("D.Thom.", "Vincent. Ferr.", "Cen.4.12", "Bern.") dentro nos dois.
- p. 28, 36: andaram 61 a 67 para a esquerda; texto e notas ("Eccles. 32.15", "Epiphan.") dentro nos dois.
- p. 40: 29 para a esquerda; notas "Apoc.12", "Pf.18.6", "Zen.fer." dentro.
- p. 43, 45, 47, 75, 95, 99: 42 a 70 para a direita; notas da margem direita ("Luc.1.51", "Iob.13", "Pf.28.7",
  "Pf.143.10", "Ecclesiast. 24.19", "Gen.37.7") ficam dentro, algumas bem perto da beirada (conferido ampliado: p. 75 e 99).
- p. 51: 36 para a direita; "Cant.4.9" dentro.
- p. 87: 66 pontos para cima; p. 88: 12 para baixo; título e reclamo dentro nos dois.
- p. 78: 5 pontos (não conta como mudança no desenho); a gravura do vaso inteira.
- p. 2 (contracapa por dentro, papel amassado com carimbo), 10, 50: sem mudança.

## Passo 3: o que o aviso "Corte deixou algo de fora" está contando (olho; `scripts/o_que_ficou_fora.py`)

Escutei a mesma conta do programa (`tiradas_do_corte`) e desenhei cada pedaço contado (`trabalho/fora_*`, folhas de
contato `trabalho/folha_fora_marial_*.jpg`; resumo em `img/avisos_o_que_fica_fora.jpg`).
- **Marial, as 33 páginas com aviso que olhei: nenhuma letra, título, número de página ou nota de margem ficou de
  fora.** O aviso conta: a beirada do papel e a sombra dela (às vezes grudada no texto, e aí o pedaço vira um
  retângulo enorme que atravessa a linha do corte: p. 10, 16, 22, 28, 30, 32, 33, 36, 40, 43, 45, 47, 75, 85, 86, 87,
  95, 99), pontinhos de sujeira de 0,4 a 2 mm (p. 4, 6, 7, 8, 50, 64, 96), a borda do escaneado nos cantos e manchas.
  A p. 71 não tem aviso e não tem pedaço contado (confere).
- **Egenloff:** p. 3 conta o risco de caneta do carimbo e o fim de "Schneeberg" (aviso **útil**); p. 6 conta o verso
  aparecendo por transparência junto com a faixa da biblioteca SLUB no pé do escaneado; p. 12 conta a faixa da SLUB e
  um canto do papel; p. 2 conta a borda do papel estampado.
- Conclusão: o aviso é verdadeiro na conta, mas em quase todas as páginas o que "ficou de fora" não é do livro. Vira
  pergunta ao Samuel (abaixo).

## Passo 4: janela de verdade (olho; `scripts/janela.py`, janela fora da tela, cliques nativos, fechada com WM_CLOSE)

Livro novo, "Cortar seguindo o conteúdo" e "Achar a página dentro da borda preta" (até a moldura, cortar fora)
ligados com cliques, Original. Prints em `trabalho/prints/` (todos abertos); os que vão para a Central em `img/janela_*.jpg`.
`erros.log` vazio nas três aberturas. Nenhum processo ficou rodando.
- **Marial 100:** a página que ganhou o aviso é a **8 contando de 1** (confirmado; o "p. 7" do implementador
  contava de 0). Na janela, a caixa do corte da p. 8 é a mesma da passada (186,136-2833,3708). O aviso diz "deixou
  de fora um pedaço impresso (moldura, título, número da página ou carimbo)", mas o que ficou de fora são 3
  pontinhos e um risco na beirada do papel (`img/janela_marial_p008.jpg`). A p. 25 também bate (279,157-2926,3730).
- **Egenloff 1-14, achado novo:** na **primeira vez** que a página 3 aparece (é a página em que a tela abre), a
  caixa do corte ainda é a de um livro menor (842,120-3825,4378: a etiqueta inteira ficaria de fora) e **não há
  aviso** nenhum de corte. Depois de visitar a 6 e a 12 e voltar, a caixa vira a certa (761,409-3744,4884, igual à
  do PDF) e o aviso aparece. Causa provável: o tamanho do livro vai crescendo enquanto o programa mede as páginas,
  e a página da tela não é refeita quando ele muda. Não sei se o PDF gerado direto da janela, sem voltar à
  página, sai com a caixa certa (não gerei PDF pela janela). Prints: `img/janela_egenloff_p003_primeira_vez.jpg` e
  `img/janela_egenloff_p003_ao_voltar.jpg` (a tela parece igual nas duas: ver o próximo item).
- **Na ferramenta Cortar, o retângulo verde mostra a folha inteira** (com a faixa SLUB), não o corte que segue o
  conteúdo: o Kaique não vê na tela onde o corte vai ficar. A tela não foi mexida neste trabalho (deve ser igual
  antes); fica como ressalva para a gerente.
- **O contador de avisos cresce enquanto se folheia:** Egenloff 6 -> 9 -> 11; Marial 27 -> 30 -> 31 -> 33 -> 34
  (a passada sem tela dá 83 no Marial). É o mesmo assunto da pergunta já feita `pr-medir-o-livro` (o programa só
  mede as páginas visitadas).
- A página 1 dos dois livros é a capa (couro/pergaminho): fica fora da conferência (regra 4.10); no Marial ela
  também tem o aviso de corte.

## Perguntas para o Samuel

### P1 (22/10, verificador): o aviso "Corte deixou algo de fora" aparece em quase todas as páginas

O que acontece: no Marial (100 páginas) o aviso aparece em **82**; no Egenloff (14) em **12**. Olhei 37 dessas
páginas: só na **Egenloff 3** o que ficou de fora é do livro (o carimbo). Nas outras, o aviso está contando a beirada
do papel, a sombra dela, pontinhos de sujeira, manchas, o verso aparecendo por transparência e a faixa da biblioteca no
pé do escaneado. Com aviso em quase toda página, o Kaique não vai saber qual abrir.
Foto: `img/avisos_o_que_fica_fora.jpg` (seis casos; o primeiro é o útil, os outros cinco não),
`img/egenloff_p003_beiradas_perto.jpg` (o caso útil, ampliado), `img/janela_marial_p008.jpg` (opção A) e
`img/aviso_opcao_c_pedacos_grandes.jpg` (opção C). Na Central: `pergunta_avisos` do `conferencia.json`.

- **A) Deixar como está.** Avisa tudo, inclusive sujeira. O Kaique teria de abrir 82 de 100 páginas.
- **B) O aviso só conta o que parece impresso** (recomendo): não conta o que encosta na beirada do papel ou do
  escaneado, pontinhos menores que uns 2 mm, nem o que é claro demais para ser tinta (verso por transparência). No
  Egenloff 3 o aviso continuaria (o risco do carimbo está no meio do papel); nos outros cinco casos da foto, sumiria.
  Risco: um carimbo ou número de página encostado na beirada do papel deixaria de ser avisado.
- **C) O aviso só aparece quando o pedaço de fora é grande** (por exemplo, mais de 5 mm). Mais simples, mas a sombra
  da beirada grudada no texto é grande e continuaria avisando (Marial 10, 28, 43).

## O que falta, passo a passo

1. ~~FEITO~~ Conferir que a captura bate com o PDF: `trabalho/cap_<livro>_<lado>_pNNN_saida.png` contra a página do
   `trabalho/saida_<livro>_<lado>.pdf` (antes, a captura do `c66f28d` foi refeita com `_guardar_geometria`, como a
   geração do PDF faz; Egenloff 3 antes deu 849,207–3832,4683, igual ao do implementador).
   As capturas (`capturar_corte.py`) já estão feitas para Egenloff 2, 3, 6, 12 e Marial 2, 4, 6, 7, 8, 10 e as 32
   que mudaram, nos dois lados (pastas `trabalho/`, fora do git; caixas em `dados/cap_*_info.json`).
2. ~~FEITO~~ Desenhar as fotos: `scripts/desenhar.py trabalho <egenloff|marial> <pág> "<título>" "<caminho e opções>" img/<nome>`
   (dá `__perto.jpg` e `__inteira.jpg`; preto = fica, vermelho = tirado, amarelo = parte ampliada). Fazer para
   Egenloff 3 e 12 e para as 32 do Marial; abrir TODAS (folha de contato se preciso) e escrever uma linha por página.
3. ~~FEITO~~ Ver as páginas com aviso sem mudança (Marial 2, 10, 50; Egenloff 2, 6) para entender o excesso de avisos.
4. ~~FEITO~~ Janela de verdade: `scripts/janela.py <pdf> <rótulo> <págs>` (piloto copiado do verificador de 13/10:
   `piloto.py`, `g.py`, `v.py`, `lancador2.py`; janela fora da tela, mensagens nativas). Rodar no Marial 100
   (págs. 7, 8) e no Egenloff 1-14 (pág. 3): print do corte e do aviso, contador de avisos, erros.log. Fechar com WM_CLOSE.
5. ~~FEITO~~ Montar `conferencia.json` (formato da Central, ver pedido da gerente) com os quadros cx-etiqueta (Egenloff 3),
   cx-marial (o corte que andou; p. 8 com o aviso), cx-velocidade (números acima), cx-avisos-demais (ressalva) e,
   se for o caso, pergunta extra sobre o excesso de avisos; manter as ressalvas: carimbos do Egenloff 3 continuam
   partidos (o oval de cima e o "Fachschule" da direita; o lápis "Af 10" some), pergunta do carimbo aberta.
6. ~~FEITO~~ (GitHub lido: o código do `fase2-caixa-conteudo` continua em `49d1ed3`/`5bc5b33`, nenhuma rodada nova) Commit (`git add -f` nas imagens), push, ler o GitHub uma vez (só disparar se o código mudar), entregar à gerente.
