# ONDE-PAREI — Dividir: "Uma página" mostra só a metade (D-601, 02/11/2026)

Cópia: `.claude/worktrees/dividir-metade`, ramo `dividir-metade-2026-11-02` (saiu de `obra-2026-10-26`, `110976f`).
Só `ui/` (e os testes). Outro construtor mexe ao mesmo tempo na faixa de baixo depois do "está certo"
(`_atualizar_faixa`, `_texto_tranquilo`), ramo `esta-certo-2026-11-02`: não mexo nessas funções.

## Decisões que esta tarefa precisa cumprir

- **D-601 (02/11/2026)** — Testando o Dividir no Gradus Primus: "eu dividi a pagina não era para ela virar só uma na
  hora que eu dividi, como funciona no scantailor?" · "ele não cortou, porque como pode ver as duas paginas ainda
  estão juntas, deveria então aparecer só metdade da pagina que era dupla, e eu pode mudar a opção lá embaixo de uma
  pagina, para pagina dupla." · pergunta: ""Uma página" (de fábrica): depois de dividir, aparece só a metade, uma
  página de cada vez, e as setas andam pelas páginas. "Duas lado a lado": aparece a folha inteira, com a linha azul
  para arrastar, como hoje. Pode ser assim?" → "ok, pode botar um agente para fazer isso".
  **Na ferramenta Dividir, com "Uma página" (de fábrica), a folha dividida mostra só uma metade (uma página por
  vez, as setas andam pelas páginas); com "Duas lado a lado", a folha inteira com a linha azul para arrastar.**
  Muda a D-007 só dentro do Dividir. Prova: Gradus Primus folha 1 dividida → "Uma página" mostra só a contracapa;
  seta → capa; "Duas lado a lado" → folha inteira com a linha.
- **D-601, acréscimo de 02/11/2026 (pela gerente)** — Samuel: "quando cortar as paginas lá embaxio que foram
  cortadas vão aparecer como uma só e nas paginas que não foram cortadas ainda vão aparecer duplas ainda, mas para
  ver as paginas que foram cortadas vão ter que apertar uma folha só ali embaixo no aplicativo." · gerente: "Na tira
  de baixo do Dividir: a folha 1 foi cortada, então na tira ela aparece como duas miniaturas separadas (a contracapa
  e a capa); as folhas 2 a 70 ainda não foram cortadas, então continuam como uma miniatura dupla cada; na página
  grande de cima, para ver só a metade de uma folha cortada, você aperta "Uma página" no rodapé. É isso?" → "isso".
  **Tira de baixo do Dividir: folha dividida = duas miniaturas (uma por metade); não dividida = uma miniatura da
  folha inteira; clicar numa miniatura de metade vai para aquela página.**
- **D-007 (26/10)** — "quando eu escolher para começar no automatico e dividir as folhas o livro tem que aparecer em
  uma pagina por vez para mim." Fora do Dividir continua igual (uma página por vez). Dentro do Dividir muda pela
  D-601.
- **D-501 (27/10)** — o livro nunca abre no Dividir; o Automático que divide estando no Dividir leva à página.
  Não muda.
- **D-006 / D-015** — "Uma página / Duas lado a lado" na barra de baixo (e no menu Ver); o lado a lado é opção,
  não padrão; de fábrica "Uma página". Não muda (só passa a valer também dentro do Dividir, pela D-601).
- **D-046** — "deixar em branco" / "tirar do livro" em qualquer página ("Esta página" no Propriedades do Dividir).
  Não muda (age na página da vez).
- **D-051** — Propriedades do Dividir em "Só nesta folha" / "Para o livro todo". Não muda.
- **D-074 / D-080** — não dividir folha de uma página só; dividir só quando o Kaique pede. Não muda (folha não
  dividida continua a folha inteira, como hoje).
- **D-498** — "não dividir esta" junta as duas páginas; "dividir esta" devolve as duas como estavam. Não muda.
- **D-528** — marcações da folha inteira vão para a metade em que estão. Não muda (só a tela).
- **D-558** — "dividir" na grade "Todas as páginas". Não muda.
- **D-590** — "juntar todas" ao lado de "não dividir esta". Não muda.
- **D-568** — roda: sem zoom troca de página; com zoom anda pela página; Ctrl + roda dá zoom. No Dividir com
  "Uma página", a roda sem zoom passa a andar pelas páginas (D-601: "as setas andam pelas páginas").
- **D-599 / D-600** — Ctrl + roda dá zoom para onde está o mouse; Shift + roda para os lados com zoom. Não muda.
- **CLAUDE.md §11 item 7** — nenhum botão, aviso ou texto novo além do decidido.

## Andamento

- [x] Mudança em `ui/tela_conferir.py` (`cd36c4d`)
- [x] Prova (`tests/test_decisoes_dividir_metade.py`) + reversão no `110976f` (falha)
- [x] Testes antigos que mediam a linha com "Uma página" (comportamento que a D-601 trocou) (`06c0150`)
- [x] Prints antes/depois (cópia do Gradus Primus em `_tmp/`)
- [x] GitHub da 1ª parte: rodada 41549443337 verde (3398 passaram, 0 falharam; botões 369 ações, 0 falhas)
- [x] Acréscimo da tira (`3b098c9`): prova (2 testes) + reversão no `110976f` (falha) + prints `*-4-*`
- [ ] Testes no PC e GitHub da versão final

## O que mudou (só `ui/tela_conferir.py`)

- `_atualizar_previa` (parte do Dividir): com "Uma página" e a folha dividida, a vista recebe só a metade da página
  da vez, partida na linha com a mesma conta do programa (`core.dividir.dividir_imagem`), e a linha some (não se
  arrasta). Folha não dividida, ou "Duas lado a lado": a folha inteira, com a linha na dividida, como antes.
- `_navegar` (setas da barra de baixo, ← → do teclado, roda sem zoom): no Dividir com "Uma página", anda pelas
  páginas (`_passos_do_dividir`: a esquerda, a direita, a próxima folha; folha não dividida é um passo só). Com
  "Duas lado a lado", de folha em folha, como antes.
- `_atualizar_barra_de_baixo`: as setas "‹ ›" acendem pela página (na folha 1 da direita a "‹" fica acesa).
- `_acertar_a_vista_da_pagina`: os botões "Uma página" / "Duas lado a lado" ficam acesos no Dividir (antes
  apagados, com o balão "No Dividir a tela mostra a folha inteira, com a linha; escolha outra ferramenta para ver as
  páginas.", que saiu por ter ficado errado). O "antes / depois" continua apagado no Dividir.
- `definir_mostrar`: no Dividir, trocar entre os dois redesenha a tela (a imagem e as setas).
- Funções novas: `_dividir_por_paginas`, `_passos_do_dividir`, `_passo_do_dividir_atual`, `_metade_no_dividir`.
- Tira do Dividir (acréscimo): `_montar_tira` monta um quadro por passo das setas (a folha dividida vira duas
  miniaturas, a metade de cada página; a não dividida, uma, a folha inteira); `_atualizar_tira_do_dividir` (novo)
  marca o "!" e o tique da folha nos quadros dela e seleciona o quadro da página da vez; `_ir_para_o_quadro_da_tira`
  (novo) faz o clique e o duplo clique numa miniatura levar àquela página; `_cortes_da_tira_do_dividir` (novo).
- `ui/widgets/tira_miniaturas.py`: `definir_cortes` (novo) — mover a linha redesenha só as miniaturas daquela folha,
  da imagem guardada, sem ler o PDF de novo (como o `definir_giros`).
- Não mexi em `_atualizar_faixa` nem `_texto_tranquilo` (são do outro construtor).

## Escolhas pelo jeito que o código já tem (anotadas)

1. **Logo depois de "dividir esta" com "Uma página": aparece a página da esquerda.** O código já punha a página da
   vez na primeira página da folha (`lista_de_paginas_mudou`, etapa 4) e ir a uma folha pela tira também vai à
   primeira página dela (`_ir_para`). No Gradus: a contracapa (print `depois-1`).
2. ~~A tira de baixo continua uma miniatura por folha~~ — **trocado pelo acréscimo de 02/11**: folha dividida = duas
   miniaturas, não dividida = uma. O título "FOLHAS" do cabeçalho da tira ficou como estava. Os números embaixo das
   miniaturas são os da posição na tira (os mesmos números das páginas nas outras ferramentas: a folha 2 do Gradus,
   depois da folha 1 dividida, aparece como "3"). O "!" e o tique de "conferida" são da folha (aparecem nas duas
   metades dela); a marca de "tirada do livro" é a da página.
3. **O rótulo continua "folha 1 de 70"** nas duas metades (o Dividir conta folhas, etapa 7 da obra: "no Dividir se
   confere a FOLHA, e o contador conta folhas"). Ver a pergunta 2.
4. **Barra de espaço ("está certo" e avança)** chama a mesma ação das setas: confere a folha e vai à próxima página
   (na esquerda, vai à direita da mesma folha). Não mexi nela (fica junto da faixa do outro construtor).
5. **Page Up/Down, Home/End** continuam de folha em folha (10 folhas; a primeira e a última), indo à página da
   esquerda. A D-601 fala das setas e da roda.
6. **Trocar de "Duas lado a lado" para "Uma página"** mostra a metade da página da vez (a que estava antes, ou a
   esquerda se a pessoa andou de folha em folha).
7. **"Esta página" (deixar em branco / tirar do livro) no Propriedades do Dividir** age na metade que está na tela
   (já agia na "página da vez").

## Perguntas para o Samuel

1. **A frase da faixa no "Uma página".** Com a folha dividida e "Uma página", a faixa de baixo continua dizendo
   "Achei a lombada e vou cortar na linha azul. Se estiver errado, arraste a linha.", mas a linha não aparece (ela
   fica no "Duas lado a lado"). Print: `relatorios/dividir-metade/depois-1-dividida-uma-pagina.png`.
   Pergunta: "No Dividir com "Uma página", a faixa diz "arraste a linha", mas a linha só aparece no "Duas lado a
   lado". Posso trocar a frase, só nesse caso, por: "Achei a lombada. Para mudar onde corta, escolha "Duas lado a
   lado" e arraste a linha."?" (sugestão: sim). Não mexi: a faixa é do outro construtor (`_texto_tranquilo`).
   **(gerente, 02/11: ainda sem resposta; deixar como está.)**
2. **"folha 1 de 70" nas duas metades.** Na "Uma página", a esquerda e a direita da folha 1 mostram as duas "folha 1
   de 70" embaixo (a seta anda, o número não). Print: `depois-1` e `depois-2`.
   Pergunta: "No Dividir com "Uma página", embaixo continua "folha 1 de 70" nas duas páginas da folha. Fica assim
   (o Dividir conta folhas), ou quer que diga a página, por exemplo "folha 1 de 70 · página 2"?" (sugestão: fica
   assim). **(gerente, 02/11: ainda sem resposta; deixar como está.)**
3. **Os números embaixo das miniaturas do Dividir.** Com a folha 1 dividida, a tira mostra 1 (contracapa), 2 (capa),
   3 (folha 2), 4 (folha 3)... e o rótulo do rodapé diz "folha 2 de 70" quando a miniatura "3" está escolhida.
   Print: `relatorios/dividir-metade/depois-4-clique-na-miniatura-2.png`.
   Pergunta: "Na tira do Dividir, depois de dividir a folha 1, as miniaturas ficam numeradas 1, 2, 3... (a folha 2
   vira o número 3, como nas outras ferramentas, que contam páginas). Fica assim?" (sugestão: fica assim; anda junto
   com a resposta da pergunta 2).
