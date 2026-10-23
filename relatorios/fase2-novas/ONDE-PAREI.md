# Onde parei: Fase 2, as 7 ferramentas que faltam (Implementador B)

Pedido da gerente em 22/10/2026. Ramo `fase2-ferramentas-2026-10-22`, criado do `origin/fase-1` em `9804b98`.
Worktree `D:\programas\EditorImpressao\.claude\worktrees\fase2-novas`, com as junções `modelos`,
`gabarito\paginas` e `gabarito\scantailor-24-09` (nunca `Remove-Item -Recurse` nelas; desfazer com
`(Get-Item <junção>).Delete()`).

Worktrees de apoio criadas por mim (só para as provas de "sai igual"; podem ser removidas pela gerente
depois de tirar as junções `modelos` e `gabarito\paginas`):
- `.claude\worktrees\fase2-novas-antes` (destacada em `9804b98`, o `fase-1` de partida);
- `.claude\worktrees\fase2-novas-prova` (destacada no commit que está sendo provado).

Regras que valem aqui: igual ao ScanTailor com os ajustes de fábrica dele, desligado de fábrica quando muda a
imagem (prova com somas iguais nas páginas-gabarito); testes seguem a ordem das etapas (dividir → endireitar →
cortar → filtro) e só com páginas que vão ser impressas; um arquivo de teste por vez no PC; suíte e velocidade
no GitHub, lidas uma vez no fim de cada item; nunca juntar ao `fase-1`; no máximo "PRONTO PARA CONFERIR".

## Os 7 itens, na ordem (estado em 22/10/2026, fim do trabalho)

Todos **PRONTO PARA CONFERIR** (falta verificador e Samuel). Relatório da entrega (três formatos):
`relatorios/fase2-novas/conferencia/entrega-2026-10-22.*`. Antes/depois (fora do git):
`relatorios/conferir/fase2-novas/<item>/`.

| # | Item | Commits | Prova / GitHub |
|---|---|---|---|
| 1 | 2.4 margens iguais + alinhamento | `c180af3` | 96/96 somas iguais (`c31489c`) |
| 2 | 2.6 arquivo para impressão (+ último caderno menor) | `cac76b0`, `f41201a`, `c31489c`, `4990e13` | 96/96; reversão do último caderno: 14 falham no antigo |
| 3 | 2.16 todos os núcleos | `14a7f97` | PDF igual com 1 e 4 trabalhadores (teste) |
| 4 | 2.17 igualar a luz e suavizar | `5f5c2e3` (DLL v8), `fa269d9` | 96/96 (`c9f3335`) |
| 5 | 2.18 mudar à mão as áreas | `bfad304`, `578c1a5`, `d652248` | 96/96 (`c9f3335`) |
| 6 | 2.19 unidades e receitas | `2d0a850` | 96/96 (`c9f3335`) |
| 7 | 2.10 + 1.6 duas camadas | `c9f3335` | 96/96 (`c9f3335`) |

GitHub: suíte `39787683890` (`fa269d9`) 2150/0, botões 222/0; suíte `39791078658` (`4990e13`) 2171 passaram, 2
falharam (trilha antiga com 9 ferramentas, consertado em `d652248`); suíte `39794419960` (`d652248`) e velocidade
`39787700625` (`9804b98`→`fa269d9`), `39791117352` (`9804b98`→`4990e13`): ver a entrega à gerente.

## Provas de "sai igual de fábrica"

Script: `relatorios/fase2-novas/scripts/rodada_processar.py` (cada página-gabarito vira um livro novo e passa
pelo `core.pipeline.processar` inteiro: dividir → endireitar → cortar → filtro; soma de cada página do PDF em
Original, Preto e branco e Melhorar). `somas_todas.sh <raiz> <saida.json>` roda as 32, uma por processo.
- Código antigo (`9804b98`): `relatorios/fase2-novas/somas-antigo-9804b98.json` — 96 somas.
- **Lição (22/10):** a prova do "novo" tem de rodar numa worktree parada no commit (`fase2-novas-prova`),
  nunca na worktree em que eu estou mexendo: mudei o `core/st_ferramentas.py` no meio de uma rodada e tive
  de jogar a rodada fora.
- O PC está com pouca memória livre (≈2 GB; o Samuel joga e outro agente mede velocidade): a rodada espera
  2,5 GB livres antes de cada página, então anda devagar.

## Escolhas de tela (para o agente de layout e o Samuel revisarem)

- **2.4:** caixinha "Margens iguais em todas as páginas" na tela "O que fazer", logo abaixo de "Cortar as
  bordas" (é opção do livro inteiro, e as opções do livro moram ali; o "Para o livro todo" do Propriedades do
  Cortar manda para lá). Marcada, mostra as quatro margens em mm (de fábrica 10/5/10/5, as do ScanTailor) e
  dois "onde a página menor fica" (de cima a baixo / de um lado ao outro: em cima, no meio, embaixo, o
  programa escolhe, onde estava na página). Desmarcada de fábrica. Provisório.
- **2.4:** aviso novo "Página bem maior que as outras" (vai para o "Para revisar" da página).
- **2.6:** botão "montar para imprimir..." na tela "Ficou pronto!", ao lado do "imprimir agora" (o lugar da
  impressão: a janela de salvar/processar). Abre a janela "Montar para imprimir" com todas as opções da janela
  do UPDF em grupos (Como vai sair · Escala de cada lado · Livreto · Várias por folha · Pôster · Outras opções ·
  Impressora) e dois botões: "gravar o arquivo para imprimir" e "mandar para a impressora". As escolhas ficam
  guardadas (como a "Última configuração" do UPDF). O botão fica apagado quando o PDF já saiu com o
  "Montar cadernos" antigo. Provisório: a aparência é do agente de layout.
- **2.6:** a exceção de "uma página só" é digitada como "12=90; 15=85" (página = %). Provisório; pede um jeito
  melhor (clicar na página na prévia?).
- **2.16:** Configurações ganhou a parte "Velocidade", com "Páginas ao mesmo tempo" (Todos os núcleos (N) · Uma
  página por vez (como antes) · 2 · 4 · 8). Provisório.

## Perguntas para o Samuel (via gerente)

1. **2.4 x explicação de 14/10:** fiz as margens iguais como o ScanTailor (na edição, para o PDF do livro),
   desligadas de fábrica, porque a ficha 2.4 e a gerente mandaram. A explicação de 14/10 diz que margem é só na
   impressão. As duas convivem (a de 2.4 deixa todas as páginas do mesmo tamanho, o que ajuda o "Ajustar" do
   livreto a dar a mesma escala em todas), mas falta ele dizer se quer as duas.
2. **2.4:** a tela de conferir não mostra as margens iguais (só o PDF tem). Mostrar na prévia?
3. **2.6:** o "Montar cadernos" antigo (folha com o dobro da largura) continua existindo ao lado da montagem nova
   em A4. Tirar o antigo, ou deixar os dois?
4. **2.6, rotação automática:** a página deitada gira no sentido anti-horário (o alto da tabela fica à
   esquerda). É o que ele quer?
5. **2.6, imprimir direto:** testei mandando para um PDF (sem papel). Na impressora de verdade não testei; e
   neste PC o Windows leva ~50 s só para "falar" com a impressora de fábrica (a EPSON ET-3750 da rede), antes de
   imprimir.

## Ressalvas até aqui

- 2.4 usa como "conteúdo" a página já cortada pelo programa (a caixa do conteúdo do ScanTailor, item 2.5, está
  no ramo `fase2-caixa-conteudo`, fora do `fase-1`). Sem "Cortar as bordas", o conteúdo é a página inteira.
- 2.4 custa uma passada a mais no livro quando ligado (só mede; o corte fica guardado para a segunda).
- 2.6 "Imprimir como imagem" de fábrica ligado (imp-6) deixa o arquivo de impressão grande (cada folha é uma
  imagem sem perda a 300 DPI) e a montagem mais lenta.
- 2.16: com pouca memória livre o programa usa 1 trabalhador (igual a antes); o ganho só aparece com memória.
- DLL versão 8: os ramos `fase2-caixa-conteudo` (4) e `fase2-scantailor-itens-2026-10-19` (5 a 7) também mudam
  a DLL; quem juntar recompila com tudo. A minha cola `luz.cpp` tem uma classe com o nome
  `output::OutputGenerator::Processor` (como a `st_gravura.cpp`); se o ramo dos itens tiver outra com o mesmo
  nome na mesma DLL, dá conflito na hora de juntar.

## Escolhas de tela feitas depois

- **2.17:** linha na aba Filtro (bloco AJUSTE): "Igualar a luz da página", "Suavizar as letras" (só no Preto e
  branco) e "Tirar o chuvisco: [0-100]". "Todas"/"daqui em diante" levam os três.
- **2.18:** ferramenta nova "Mover e mudar o tamanho da área" (tecla A) na trilha, depois de "Pegar pela cor";
  linha "Área:" embaixo da página na ferramenta de marcar ("Mostrar as áreas achadas", apagar a área, pintar de
  branco, copiar, colar); "Marcar como" com seis tipos e o botão "cor de pintar".
- **2.19:** linha "Receita:" no alto da tela "O que fazer"; em Configurações "Medidas em" e "Receita de todo livro novo".
- **2.10/1.6:** caixinha "Gravar em duas camadas..." na janela "Confirmar e processar".
- **2.6:** parte "Impressão" em Configurações (margem 10 mm e o que a impressora não imprime, 3 mm).

## Perguntas novas (do olho nos antes/depois)

6. **2.17:** igualar a luz antes do Melhorar/Mágico pro deixa a tinta lavada (Graduale 221, Horas 47). Deixar o
   "igualar" só no Preto e branco e no Original?
7. **2.17:** "tirar o chuvisco" acima de ~20 borra a letra. Limitar a escala?
8. **2.18:** a "tinta com a cor" numa página em Preto e branco deixa a letra cinza (a cor do original). É isso?

## Os dois "defeitos" do 2.18 que a gerente viu (22/10/2026): conferidos, não são do código

Medi ponto a ponto o "antes" contra o "depois" das duas páginas (150 DPI): fora da área marcada só mudam 905
pontos (Horas 13) e 109 (Marial 7), todos na beirada da área (arredondamento); a página não andou.
1. **Horas 13, faixa preta:** a área [(0,2;0,3),(0,8;0,6)] pegava a moldura dourada do lado direito; a moldura é
   tinta, e "tinta preta" a pinta de preto (antes, as 12 colunas antes da borda da área: 84, 81, 97... = o
   dourado). O fundo "esverdeado" é o creme do papel original, que é o que "fundo original" pede. Refeito com a
   área só no texto [(0,25;0,3),(0,72;0,6)]: sem faixa.
2. **Marial 7:** a área [(0,75;0),(1;0,12)] era a do canto de cima à direita (eu escolhi mal: a mancha é à
   esquerda); ela cobria o começo da 1ª linha ("Padre Pro...") e por isso o texto sumiu ali. A linha preta vertical
   é a borda do scanner, que existe no "Hoje" também (abaixo da área). Refeito com a área na mancha da esquerda
   [(0;0),(0,11;0,28)]: a mancha sai; a área retangular pega também o começo das linhas que estão dentro dela.
Sem conserto de código, sem teste de reversão (não houve bug). Imagens novas em `relatorios/conferir/fase2-novas/2.18/`.

## Velocidade e suíte final (22/10/2026)

- Filtro de velocidade `39787700625` (`9804b98` → `fa269d9`, 2.4 + 2.6 + 2.16 + 2.17): **"parece mais rápido"** -
  abrir o livro 61,3 → 36,0 s (−41%); Mágico pro 10 páginas 75,2 → 44,8 s (−40%); Preto e branco 10 páginas
  41,3 → 29,1 s (−30%); trocar de página 4,59 → 4,23 s ("igual"). É o 2.16 (várias folhas ao mesmo tempo).
- Filtro `39791117352` (`9804b98` → `4990e13`, os 7 itens): ainda rodando ao entregar.
- Suíte `39794419960` (`d652248`): 2173 passaram, 0 falharam; botões 234 ações, 0 falhas.

## Respostas do Samuel (22/10/2026, via gerente) e o que foi feito

- **Pergunta 8 (2.18, "tinta com a cor"):** fotos novas em `relatorios/conferir/fase2-novas/pergunta-8/`. As fotos
  são da Horas 13 (título vermelho e azul) e da Escola 7, em 4 painéis: Original · Preto e branco · A (o programa)
  · B (escurecida, SIMULADA). O script é `scripts/pergunta8.py`. **Não mexer até a resposta.**
- **Pergunta 3 (montagem antiga): "Deixar os dois".** Ficam os dois, com nomes novos:
  - "Montar cadernos no tamanho do scan (sem A4, sem margem)", a caixinha antiga da tela "O que fazer" e do painel
    "Automático";
  - "montar para imprimir em A4 (com margens)...", o botão da tela "Ficou pronto!".
- **2.4: "Ficam as duas"** (a do ScanTailor como opção desligada e a da impressão): nada a mudar.
- **2.4: "Sim, a tela mostra igual ao que sai".** Os cartões da aba Filtro (a página da vez nos filtros) aparecem com as
  margens iguais quando ligadas.
  - A tela mede as páginas por trás (`ui/tarefas.TarefaMedirAsMargens`, só números por página, cache
    `core.pipeline._TAMANHOS_PRONTOS`).
  - Enquanto mede, mostra sem margem; o processar reaproveita a medida (não desenha de novo).
  - Ressalva: a tela ampliada ("comparar") ainda mostra sem margem.
- **2.6:** página deitada com o alto à esquerda, como está. O "Falando com a impressora (pode demorar um pouco)" já
  aparece ao mandar imprimir.
- **2.17:** "Igualar a luz" em todos os filtros, com aviso no Melhorar e no Mágico pro; "Tirar o chuvisco" de 0 a 100,
  com aviso acima de 20. Os textos estão em `core/luz_scantailor.py`, e a frase aparece embaixo da linha da luz na
  aba Filtro.
- GitHub depois dos ajustes: suíte `39807401594` (`7d13a5f`): 2177 passaram, 0 falharam; botões 234, 0 falhas.
  Velocidade `39791117352` (`9804b98` → `4990e13`, os 7 itens): "parece mais rápido" - abrir −43%, Mágico pro −41%,
  Preto e branco −27%.

## Pergunta 8 respondida: "As duas: A e B como opções separadas" (22/10/2026, feito)

Resposta do Samuel à `b-8-tinta-com-cor` (Central, 22/10): **"As duas: A e B como opções separadas"**.

- **O que mudou:** a área "Tinta com a cor original, papel branco" agora tem dois jeitos.
  - **A, "cor como no livro"** (o de fábrica, igual ao de antes ponto por ponto);
  - **B, "cor escurecida"**: a mesma tinta mais escura (brilho pela metade) e com a cor 25% mais forte, os números da
    simulação que ele viu.
- **Na tela (nome escolhido):** quando "tinta com a cor, papel branco" é a escolhida no "Marcar como", aparecem logo
  abaixo, lado a lado, dois botões: **"cor como no livro"** e **"cor escurecida"**. Vale para a próxima área marcada;
  a área já marcada guarda o jeito dela. Sem emoji. Provisório até o agente de layout.
- **Dados:** campo novo e opcional `Regiao.tinta_escurecida` (padrão `False` = A). Projeto antigo abre sem a chave e
  sai A; programa antigo que abrir projeto novo descarta a chave e mostra A.
- **Código:** `core/selecao.py`, `core/editar_zonas.py` (`escurecida`, `_mascara_escurecida`), `ui/widgets/paineis.py`,
  `ui/widgets/editor_selecao.py`, `ui/tela_conferir.py`. Commit `8226f33`.
- **Testes:** `tests/test_tinta_escurecida.py` (8 passaram). Prova que livro novo, livro já começado (sem a chave) e a
  conta antiga saem iguais ponto por ponto; testa a B, a área de cima mandando onde duas se cruzam, o "tirar" e a tela.
  Também passaram aqui `test_editar_zonas.py` (10), `test_paineis.py` (33), `test_selecao.py` (24) e `test_editor_selecao.py` (17).
- **Prova "A igual ao de antes" em páginas de verdade:** `scripts/tinta_a_e_b.py somas-a`, Horas 13, Escola 7 e Opus
  Majus 3 com a área A, código antigo (`f26407c`, worktree `fase2-novas-prova`) e novo (`8226f33`): **3 de 3 PDFs iguais**
  (`somas-tinta-a-antigo-f26407c.json`, `somas-tinta-a-novo-8226f33.json`).
- **Antes/depois:** `relatorios/conferir/fase2-novas/tinta-a-e-b/` (fora do git), feito por `scripts/tinta_a_e_b.py fotos`.
  Caminho de cada foto: girar (0°, a análise não girou) → dividir (não, de fábrica) → endireitar (sim) → cortar as
  bordas (sim) → Preto e branco → área "Tinta com a cor" A ou B. Quatro painéis: Original · Preto e branco · A · B.
  - Horas 13: o vermelho e o azul do título voltam (A); na B ficam vermelho-escuro e azul-marinho. Brilho da tinta
    134 → 68. A moldura dourada que cai dentro da área também escurece na B (a ressalva que já estava na pergunta).
  - Escola 7: o título cinza-marrom claro (A) fica marrom-escuro na B, quase tão forte quanto o Preto e branco. 112 → 56.
  - Opus Majus 3 (folha de rosto): "OPUS MAJUS" e "ROGER BACON" vermelhos (A) ficam vermelho-escuro (B); "THE" e "OF"
    pretos continuam escuros. 124 → 74. Um pedaço do carimbo roxo da biblioteca que cai na área volta em pontinhos
    coloridos na A e na B (é a A de sempre, não mudou).
  - Fora da área: igual entre A e B (0 a 121 pontos diferentes, só na beirada da área).

## Perguntas para o Samuel (via gerente)

9. **Onde aparecem os dois botões:** a gerente disse "quando a página está em Preto e branco". Eu fiz os dois botões
   aparecerem sempre que "tinta com a cor, papel branco" é escolhida, em qualquer filtro, porque o "Marcar como" não muda
   com o filtro da página e a B funciona igual no Original e no Melhorar (o papel vai a branco e a tinta escurece).
   Fica assim, ou esconder os dois botões quando a página não está em Preto e branco?
   Foto: `relatorios/conferir/fase2-novas/tinta-a-e-b/horas_p013-titulo-ampliado.jpg` (A e B no Preto e branco).

GitHub da tinta A e B: suíte `39850503362` (`41fa7bc`): 2185 passaram, 0 falharam; botões 234 ações, 0 falhas.
Velocidade `39849559789` (`f26407c` → `8226f33`): **"igual (dentro do vai-e-vem)"** - abrir 36,5 → 36,6 s (+0,4%); trocar de página 4,26 → 4,32 s (+1,3%); Mágico pro 45,3 → 45,0 s (−0,7%); Preto e branco 29,0 → 29,0 s (+0,1%). O caminho de fábrica não passa pela conta nova.

## Papel da "tinta com a cor" em dois jeitos (tc23-1, 22/10/2026, feito)

Resposta do Samuel à `tc23-1` (o retângulo branco no papel creme do Original): "eu posso ter as duas opções?" e
**"As duas: escolher o papel em cada área ('papel branco' ou 'papel como o resto da página')"**.

- **O que mudou:** embaixo dos dois botões da cor aparecem mais dois, para o papel: **"papel branco"** (o de fábrica,
  igual ao de hoje) e **"papel como o resto da página"** (o papel dentro da área fica como o filtro da página o deixou;
  só a tinta segue o A ou o B). Os dois do papel ficam um sob o outro: lado a lado o segundo saía cortado
  ("papel como o resto da pág...") no painel de 300 px. Em qualquer filtro, como os da cor (b-9). Sem emoji.
  Provisório até o layout. O botão do tipo continua "tinta com a cor, papel branco" (não mudei nome de controle).
- **Dados:** campo novo e opcional `Regiao.papel_da_pagina` (padrão `False` = papel branco). Projeto antigo sai papel branco.
- **Código:** `core/selecao.py`, `core/editar_zonas.py` (`_mascara_do_jeito`; o papel só mexe no que não é tinta),
  `ui/widgets/paineis.py`, `ui/widgets/editor_selecao.py`, `ui/tela_conferir.py`. Commits `b0af839`, `3e95076`.
- **Testes:** `tests/test_tinta_papel_da_pagina.py` (10 passaram; os 10 falham no código antigo, que não tem o campo).
  Também passaram `test_tinta_escurecida.py` (8), `test_editar_zonas.py` (10), `test_selecao.py` (24),
  `test_paineis.py` (33), `test_editor_selecao.py` (17).
- **Prova "de fábrica igual" em páginas de verdade:** `scripts/tinta_papel.py somas`, Horas 13, Escola 7 e Opus Majus 3,
  área "papel branco" com A e com B, em Original, Preto e branco e Melhorar, código antigo (`639136a`) e novo (`3e95076`),
  os dois na worktree parada `fase2-novas-prova`: **18 de 18 PDFs iguais** (`somas-tinta-papel-antigo-639136a.json`,
  `somas-tinta-papel-novo-3e95076.json`).
- **Antes/depois:** `relatorios/conferir/fase2-novas/tinta-papel/` (fora do git), feito por `scripts/tinta_papel.py fotos`.
  Caminho de cada foto: girar (0°) → dividir (não, de fábrica) → endireitar (sim) → cortar as bordas (sim) → Original ou
  Preto e branco → área "tinta com a cor". Cinco painéis: sem área · A + papel branco · A + papel da página · B + papel
  branco · B + papel da página. "papel branco" = o de antes (somas iguais).
  - Horas 13, Original: o retângulo branco some; com A a página sai igual a sem área (0 pontos diferentes); com B só o
    título escurece (e a moldura dourada que cai na área, a ressalva de sempre). O "TABLE" e as linhas do verso que
    transparecem no papel voltam a aparecer dentro da área (são do papel da página).
  - Escola 7 e Opus Majus 3, Original: o mesmo (A = 0 pontos diferentes de sem área; B só a tinta).
  - Preto e branco: quase igual nas duas; mas o papel da página do Preto e branco traz o contorno preto que o filtro
    pôs em volta da letra (pergunta 10).
  - Painel (`antes_painel_de_fabrica.png`, `depois_painel_de_fabrica.png`, `depois_painel_papel_da_pagina.png`).
- **Velocidade:** filtro do GitHub `39876068685` (`639136a` → `b0af839`; o `3e95076` só muda a tela): **"igual (dentro do vai-e-vem)"** - abrir 40,0 → 39,7 s (−0,8%); trocar de página 3,54 → 3,55 s (+0,1%); Mágico pro 47,5 → 47,5 s (−0,1%); Preto e branco 28,8 → 28,7 s (−0,3%).
- **Suíte do GitHub** `39877466484` (`4c4cc52`): 2195 passaram, 0 falharam; botões 234 ações, 0 falhas.

## Perguntas para o Samuel (via gerente)

10. **Preto e branco com "papel como o resto da página": letra com contorno preto.** No Preto e branco, o papel "da
    página" é o resultado do filtro, e o filtro pinta de preto a beirada de cada letra um pouco além do que o programa
    chama de "tinta com a cor". Com "papel branco" essa beirada some (fica branca); com "papel como o resto da página"
    ela fica, e a letra colorida sai com um contorno preto fino. No Original não acontece (lá o papel é o do livro).
    Na Escola 7 dá para ver; na Opus Majus 3 e na Horas 13 quase não se vê.
    - (a) Fica assim: "papel como o resto da página" é o filtro da página, com o contorno preto.
    - (b) No Preto e branco, "papel como o resto da página" sai igual a "papel branco" (sem contorno); muda só nos
      filtros com cor.
    Fotos: `relatorios/conferir/fase2-novas/tinta-papel/escola_p007-preto_e_branco-letra-de-perto.jpg` (em cima papel
    branco, embaixo papel da página, ampliado 3 vezes), `escola_p007-preto_e_branco-titulo-ampliado.jpg` e, para
    comparar com o Original, `horas_p013-original-titulo-ampliado.jpg`.
11. **O nome do tipo:** o botão do "Marcar como" ainda diz "tinta com a cor, papel branco", mesmo quando se escolhe
    "papel como o resto da página". Trocar para só "tinta com a cor"? (Não mudei: nome de controle é com ele.)
    Foto: `relatorios/conferir/fase2-novas/tinta-papel/depois_painel_papel_da_pagina.png`.

## Perguntas 10 e 11 respondidas (Central, 23/10/2026) — em andamento

- **10, a linha preta em volta da letra no Preto e branco:** "No Preto e branco, tirar a linha preta: as duas opções de
  papel saem iguais, com a letra limpa". Ele perguntou "Isso vai alterar alguma coisa, tirar essa linha preta?"; a
  resposta dada: só muda a página em Preto e branco com uma área "papel como o resto da página", em que a letra sai
  igual a "papel branco". Nada mais muda.
  - **Feito:** `core/editar_zonas.aplicar_por_cima` ganhou `preto_e_branco` (de fábrica False); `core/pipeline` passa
    `pagina.filtro == PRETO_E_BRANCO`. No Preto e branco o passo do "papel da página" não roda: sai idêntico ao "papel
    branco". Original e Melhorar como antes. Commit `f8691be`.
- **11, o nome do botão:** "manter a cor da tinta". Rótulo do "Marcar como" trocado (era "tinta com a cor, papel
  branco"); `core/selecao.NOMES_AMIGAVEIS` (o aviso "Área escolhida: ..." e o resumo "Marcado: ...") também.
  O código gravado no projeto.json continua `tinta_cor`. Commit `f8691be`.
  - **Para a revisão futura dos nomes de botão:** o Samuel disse "esse botão ainda é bem confuso, mas por enquanto
    pode ficar assim."
- **Testes:** `tests/test_tinta_papel_preto_e_branco.py` (10 passaram aqui; no código antigo `0acf2c7` 3 falham: o
  contorno preto, 3839 pontos a mais; a chamada direta; o nome do botão).
  - Achado: o `test_no_pipeline_original_sem_retangulo_branco` (meu, de `b0af839`) usava `detectar_regioes=False`, com
    que o pipeline não usa marcação nenhuma: passava sem testar nada. Trocado para True (continua passando).
- Somas (Horas 13, Escola 7, Opus Majus 3; 45 PDFs por código) rodando em `fase2-novas-prova`; velocidade
  `39886669584` (`0acf2c7` → `f8691be`) rodando.
