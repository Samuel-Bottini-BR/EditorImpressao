# Quadro azul na página certa, janela "Antes de processar" menor e miniaturas que ficam como você deixou

**PRONTO PARA CONFERIR, com ressalvas (a principal: o "Mostrar" da janela "Antes de processar" corta o motivo mais comprido).**

As três funcionam na janela de verdade, pilotada com cliques e teclas do Windows, em 1280 x 657 e maximizada, com o Graduale, o Palatino e o Boécio.

Quadro azul: em "Duas lado a lado", indo à página 301, o quadro azul de "Todas as páginas" agora marca a 301 (antes marcava a 300). A 300 e o modo "Uma página" continuam certos.

"Antes de processar": a janela ficou menor (de 79 % para 61 % da altura da tela do Kaique), com a frase em duas linhas e os botões em duas filas; nenhum botão saiu e nenhum nome mudou. Mas o "Mostrar" agora corta o motivo mais comprido ("Endireitar: as contas discordam (12)" aparece sem o número), e cabem 7 linhas à vista em vez de 10.

Miniaturas: o lugar, abertas ou fechadas e "Ver em pares" ficam guardados de um livro para o outro, fechando e abrindo o programa de verdade. Um valor estranho no arquivo volta ao de fábrica, sem erro.

Testes no GitHub: 2196 passaram, 0 falharam (rodada 39843764387); 2188 passaram, 0 falharam (rodada 39843769308); botões 216 e 228 ações, 0 falhas. O teste do quadro azul falha no código de antes e passa no novo.

Conferido por **olho** (prints da janela de verdade, abertos um por um) e por **máquina** (testes de reversão no código antigo, rodadas do GitHub, conferências automáticas dos roteiros).

## 1. "Todas as páginas" em "Duas lado a lado": o quadro azul na página da vez

O que você está olhando: o Graduale aberto em "Duas lado a lado". Digitei 301 na pílula de baixo (teclas do Windows) e cliquei em "Ver todas as páginas". Caminho: o livro como está, sem processar (é a tela do livro aberto).

O quadro azul tem de estar na página que a pílula diz.

**O que olhar:** Se o quadro azul está na 301, a mesma da pílula.

Depois: a 301 em 1280 x 657 e maximizada; a 300 e o modo "Uma página" também certos (14 de 14). Antes: em 1280 x 657 o azul ficava na 300 com a pílula dizendo 301; maximizada acertava por acaso (12 de 14). No livro aberto, o contorno fino passa da página da esquerda para a da direita.

**Selo:** Bom. **Ressalva:** Só testei indo à página pela pílula; folhear com as setas leva sempre à primeira do par, como antes.

**Antes, 1280 x 657: pílula na 301, quadro azul na 300**

![Antes, 1280 x 657: pílula na 301, quadro azul na 300](img/1_antes_1280_duas_301_todas.jpg)

**Depois, 1280 x 657: quadro azul na 301**

![Depois, 1280 x 657: quadro azul na 301](img/1_depois_1280_duas_301_todas.jpg)

**Antes: no livro, o contorno na página da esquerda (300)**

![Antes: no livro, o contorno na página da esquerda (300)](img/1_antes_1280_duas_301_livro.jpg)

**Depois: o contorno na página da direita (301)**

![Depois: o contorno na página da direita (301)](img/1_depois_1280_duas_301_livro.jpg)

**Depois: indo à 300, o azul na 300**

![Depois: indo à 300, o azul na 300](img/1_depois_1280_duas_300_todas.jpg)

**Depois, "Uma página" na 301: igual a antes**

![Depois, "Uma página" na 301: igual a antes](img/1_depois_1280_uma_301_todas.jpg)

**Antes, maximizada: acertava por acaso**

![Antes, maximizada: acertava por acaso](img/1_antes_max_duas_301_todas.jpg)

**Depois, maximizada: azul na 301**

![Depois, maximizada: azul na 301](img/1_depois_max_duas_301_todas.jpg)

**Depois, maximizada: o livro na 301**

![Depois, maximizada: o livro na 301](img/1_depois_max_duas_301_livro.jpg)

## 2. A janela "Antes de processar", mais clara e menor

O que você está olhando: o Palatino com os ajustes de fábrica (o programa girou, endireitou e cortou sozinho), 25 avisos. Cliquei em "Confirmar e processar" e a janela abriu. Seu pedido: "ficou meio embolado, deve ficar mais claro e não tão grande."

Antes e depois na mesma página e no mesmo tamanho de tela.

**O que olhar:** Se ficou mais clara e cabe bem, e se o "Mostrar" lê inteiro.

Ficou menor (522 x 400 contra 560 x 520; 61 % da altura em vez de 79 % em 1280 x 657) e mais arrumada: a frase forte em cima, a pergunta mais fraca embaixo, "Selecionar todas" e "Nenhuma" pequenos ao lado do "Mostrar", e uma fila só embaixo com "ver" em azul. Os mesmos sete controles, com os mesmos nomes. Pelo Windows: a caixinha marca, "Selecionar todas" marca as 25, "Nenhuma" desmarca, "está bom nas marcadas" tira a linha e a janela volta com 24, "ver" fecha sem processar, e o "Mostrar" filtra. O que piorou: escolhendo o motivo mais comprido, o "Mostrar" corta o texto e some o número; e cabem 7 linhas à vista em vez de 10.

**Selo:** Bom, com ressalva. **Ressalva:** O "Mostrar" corta "Endireitar: as contas discordam (12)". A mesma janela pelo "Para revisar" também mudou. A foto por cima do programa é montagem das duas janelas.

**Antes, 1280 x 657 (montagem): a janela ocupa quase toda a altura**

![Antes, 1280 x 657 (montagem): a janela ocupa quase toda a altura](img/2_antes_1280.jpg)

**Depois, 1280 x 657 (montagem): menor**

![Depois, 1280 x 657 (montagem): menor](img/2_depois_1280.jpg)

**Antes: só a janela**

![Antes: só a janela](img/2_antes_janela.jpg)

**Depois: só a janela**

![Depois: só a janela](img/2_depois_janela.jpg)

**Antes: "Mostrar" com o motivo mais comprido, inteiro**

![Antes: "Mostrar" com o motivo mais comprido, inteiro](img/2_antes_mostrar_comprido.jpg)

**Depois: o mesmo motivo cortado, sem o (12)**

![Depois: o mesmo motivo cortado, sem o (12)](img/2_depois_mostrar_comprido.jpg)

**Depois: "Selecionar todas" pelo Windows**

![Depois: "Selecionar todas" pelo Windows](img/2_depois_todas_marcadas.jpg)

**Depois: "está bom nas marcadas" e a janela volta com 24**

![Depois: "está bom nas marcadas" e a janela volta com 24](img/2_depois_depois_do_esta_bom.jpg)

**Antes, maximizada (montagem)**

![Antes, maximizada (montagem)](img/2_antes_max.jpg)

**Depois, maximizada (montagem)**

![Depois, maximizada (montagem)](img/2_depois_max.jpg)

**Antes: a mesma janela pelo "Para revisar"**

![Antes: a mesma janela pelo "Para revisar"](img/2_antes_para_revisar.jpg)

**Depois: pelo "Para revisar" (frase em duas linhas, botão "fechar")**

![Depois: pelo "Para revisar" (frase em duas linhas, botão "fechar")](img/2_depois_para_revisar.jpg)

## 3. Miniaturas lembradas para todos os livros

O que você está olhando: a tela de trabalho, na página 21, com os ajustes de fábrica ("Cortar as bordas"). No Boécio arrastei as miniaturas para a direita e liguei "Ver em pares"; fechei o programa; abri o programa de novo com o Palatino; fechei as miniaturas pela seta; fechei e abri de novo.

Cada abertura é o programa fechado e aberto de verdade. Sua resposta: "Sim, lembrar para todos os livros".

**O que olhar:** Se o outro livro abre com as miniaturas como você deixou.

Depois: o Palatino abriu com elas à direita e em pares; fechadas pela seta, abriram fechadas na vez seguinte, com "Ver > Miniaturas" desmarcado e o "Confirmar e processar" na barra de baixo. Antes: o outro livro voltava sempre embaixo, uma a uma, abertas. Estraguei o arquivo de três jeitos (valores sem sentido, texto no lugar, arquivo quebrado): nos três o programa abriu normal, com as de fábrica (embaixo, abertas, uma a uma).

**Selo:** Bom. **Ressalva:** O "Ver em pares" foi escolhido no menu pelas teclas do Windows (o clique no item fora da tela não pegou).

**Boécio: à direita e em pares**

![Boécio: à direita e em pares](img/3_depois_f1_1280_boecio_direita_em_pares.jpg)

**O menu dos três pontinhos**

![O menu dos três pontinhos](img/3_depois_f1_menu_dos_pontinhos.jpg)

**Antes: Palatino, programa aberto de novo: embaixo, uma a uma**

![Antes: Palatino, programa aberto de novo: embaixo, uma a uma](img/3_antes_f2_1280_palatino_reaberto.jpg)

**Depois: Palatino aberto de novo: à direita, em pares**

![Depois: Palatino aberto de novo: à direita, em pares](img/3_depois_f2_1280_palatino_reaberto.jpg)

**Depois, maximizada**

![Depois, maximizada](img/3_depois_f2_max_palatino_reaberto.jpg)

**Antes: fechadas pela seta, voltam abertas embaixo**

![Antes: fechadas pela seta, voltam abertas embaixo](img/3_antes_f3_1280_reaberto_fechadas.jpg)

**Depois: abrem fechadas, à direita**

![Depois: abrem fechadas, à direita](img/3_depois_f3_1280_reaberto_fechadas.jpg)

**Depois, maximizada, fechadas**

![Depois, maximizada, fechadas](img/3_depois_f3_max_reaberto_fechadas.jpg)

**Arquivo com valor estranho: volta ao de fábrica**

![Arquivo com valor estranho: volta ao de fábrica](img/3_depois_f4_1280_valor_estranho.jpg)

## Ressalvas

- Antes de processar: o "Mostrar" ficou estreito e corta "Endireitar: as contas discordam (12)" (some o número). Antes cabia inteiro. É defeito a consertar, não escolha.
- Antes de processar: cabem 7 linhas à vista em vez de 10 (a lista rola). A mudança vale também para a mesma janela aberta pelo "Para revisar" > "ver a lista…" (frase em duas linhas, "ver" em azul).
- Antes de processar: a página com dois motivos continua em duas linhas ("Página 69 - Alinhamento duvidoso" e "Página 69 - Endireitar…"); o agente não mexeu porque mudaria as caixinhas.
- Antes de processar: "continuar assim mesmo" não foi clicado (processaria o livro inteiro); os outros cinco botões, a caixinha da linha e o "Mostrar" foram clicados pelo Windows.
- Antes de processar: a foto da janela por cima do programa é uma montagem (as duas janelas fotografadas fora da tela e juntadas, com a janela no meio, onde ela abre).
- Miniaturas: o menu dos três pontinhos foi aberto com clique do Windows, mas o "Ver em pares" foi escolhido com as teclas do Windows (seta e Enter): o clique no item do menu fora da tela não pegou.
- Achado à parte, que já existia antes destas mudanças: ao abrir o programa, quatro botões ("Guardar a tinta forte", "Guardar tudo", "Guardar só o texto" e "ver todas") aparecem por um instante como janelinhas soltas, antes de entrarem no lugar. Não vi se isso pisca na tela; é para a Lista de bugs.
- Uma foto maximizada saiu preta pela metade uma vez em três (falha da foto, não do programa: repetida duas vezes, saiu certa).
- Roda do mouse não testada (não funciona sem foco).