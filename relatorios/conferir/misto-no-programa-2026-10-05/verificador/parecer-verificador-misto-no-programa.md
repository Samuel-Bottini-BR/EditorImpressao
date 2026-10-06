# Parecer do verificador: modo Misto ligado ao programa (05/10/2026)

Ramo `fase2-misto`, worktree `misto`, commits `06d6678` (campos), `ee56ba4` (processamento), `618cb1d` (tela), base `ace15b2`. Não é aprovação: quem marca é o Samuel.

## Veredito em uma frase

**PRONTO PARA CONFERIR, com dois defeitos do próprio Misto para consertar antes de chegar ao Kaique** (o alerta "Esta página tem cor" continua com "Só as letras" ligada, e o cartão "Preto e branco" da aba Filtro mostra o Preto e branco sem Misto). O que a tela promete funciona: os três botões, a caixinha das molduras cinza, o "Mais opções", o "só nesta página" com desfazer e refazer, a prévia que muda, o PDF igual à prévia do programa, as páginas sem "Só as letras" idênticas ao `ace15b2` e o projeto antigo abrindo com o Misto desligado.

## Máquina ou olho, item por item

| Item | Como foi conferido | Resultado |
|---|---|---|
| (a) pytest | máquina, arquivo por arquivo (74 arquivos), numa cópia `git archive` do `618cb1d` | **1439 passaram, 59 pularam, 0 falhas.** Nada precisou ser repetido. Os 59 pulados são dos testes de leitores de texto (OCR), que se pulam sozinhos |
| (a) `teste_botoes.py` | máquina, na mesma cópia, com `saida_teste` própria | **132 ações, 0 falhas.** Ressalva: ele não clica em nada do Misto (nenhuma ação com "Só as letras") |
| (b) tela "O que fazer" | olho, janela real 1600 × 821 px (1280 × 657 pontos), mouse nativo | funciona (detalhes abaixo) |
| (b) aba Filtro, "só nesta", desfazer/refazer | olho e máquina (valor gravado na página, chave da prévia) | funciona |
| (b) janela não congela | máquina (mensagem nativa à janela a cada 100 ms) | não congelou nas medidas com o PC parado; uma vez, com o PC carregado, ficou 6,2 s parada ao abrir o projeto (ver Tempos) |
| (b) PDF = prévia | máquina (pixel a pixel) e olho | o PDF da janela é **idêntico, ponto por ponto**, ao mesmo projeto processado sem janela; a prévia de 110 DPI segue o PDF, com a perda de detalhe que a prévia "Rápida" já tinha antes |
| (b) páginas sem "Só as letras" = `ace15b2` | máquina | **4 de 4 idênticas** (pixel a pixel) |
| (c) dois bugs anotados | olho, janela real | **os dois confirmados** |
| (d) "Para revisar" | máquina e olho | 0 de 4 no livro 1; 3 de 8 no livro 2 |
| (e) projeto gravado pelo `ace15b2` | olho e máquina | abre com o Misto desligado; PDF idêntico ao do `ace15b2` |

## Defeitos conhecidos (lembrete obrigatório)

Moldura dourada e iluminura continuam como **defeito conhecido** até a Fase 1 ser fechada pelo Samuel. Nada aqui muda isso.

## Como foi feito

- Livro 1 (`livro-misto.pdf`): Escola de Jesus 7, Opus Majus 20, Horas 11, Palatino 5, copiadas de `gabarito\paginas` (só lidas). "Dividir folhas ao meio" desligado, Preto e branco, "Só as letras" ligada no livro.
- Livro 2 (`livro-revisar.pdf`), para os itens (c) e (d): Escola 7, Palatino 9, Graduale 222, Boécio 7 e 8, Palatino 7, Opus 11, Rhetorica 73. Foi preciso porque, no livro 1, 3 das 4 páginas têm cor, e o programa transforma o alerta de cor em "observação do livro" (que nunca aparece na tela, bug antigo); com a cor só em algumas páginas, o alerta aparece.
- Instância própria do programa (cópia `git archive` do `618cb1d`), pasta de dados própria na minha pasta temporária, janela fora da tela, cliques e teclas por mensagem nativa, prints com `PrintWindow`. Fechada com `WM_CLOSE` todas as vezes. Uma segunda cópia, do `ace15b2`, para o item (e) e para comparar.
- **Problema meu, já resolvido:** o meu lançador (que põe as caixas fora da tela) gerou 9 caixas "Aconteceu um problema inesperado" na primeira sessão, por mexer num botão que o Qt já tinha apagado. Não é do programa: os 9 registros do `erros.log` apontam para o meu `lancador.py`. Consertei o lançador, reabri, e nas outras sessões o `erros.log` ficou vazio.

## (b) O que vi em cada passo (prints em `prints/`)

1. **01** Preto e branco escolhido na tela "O que fazer". A bolinha do filtro escolhido continua invisível (é o O1, antigo e ainda não feito).
2. **02** "Só as letras" marcada: aparecem os três botões, **"Guardar a tinta forte" escolhido (azul)**, a frase do que ele faz e "Mais opções". A caixinha "No Preto e branco, molduras e iluminuras também em preto e branco" fica **cinza**, ela e a frase.
3. **03** Teste do "volta como estava": desmarquei "Só as letras", marquei a caixinha das molduras, marquei "Só as letras" (a caixinha fica cinza **com o visto aparecendo**), desmarquei "Só as letras": a caixinha volta ativa **e marcada**. Depois a desmarquei. Certo, como a decisão P5.
4. **04** "Mais opções" abre "Papel de dentro das gravuras: branco" e "Letras dentro de molduras e iluminuras: com a cor delas e papel branco atrás" (os padrões que o Samuel escolheu). "Menos opções" fecha. Nada cortado. Para ver os botões é preciso rolar a coluna; a rolagem funciona.
5. **05** Aba Filtro, página 1: "Só as letras" marcada (herdada do livro), "Guardar a tinta forte" escolhido. Cabe em 1280 × 657.
6. **06 a 08** "Tudo em preto e branco" **só na página 1**: o valor vai só para a página 1 (as outras continuam seguindo o livro), o Histórico ganha "Só as letras na pági…", a prévia nova chega em 0,9 s. **Desfazer** (menu Editar) volta para "Guardar a tinta forte" e a página volta a seguir o livro; **Refazer** volta para B. A prévia de B depois do refazer é igual, ponto por ponto, à de B de antes.
   - Na Escola 7, A e B quase não diferem (9 pontos na prévia): fora do texto quase só há tinta forte. A diferença entre os botões aparece nas páginas com moldura de filetes, música e diagramas.
7. **12** "Mais opções" da aba Filtro: as duas listas ficam na linha da caixinha, à direita. Cabe, nada cortado.
8. **13** PDF gerado: "Ficou pronto!", 4 páginas, **32 MB** (sem Misto: 26,5 MB; a Horas 11 sozinha é grande nos dois).
9. **16** Projeto do `ace15b2` aberto pelo programa novo: "Só as letras" desmarcada, sem os botões.

## (b) As páginas do PDF (uma linha por página; imagens 20 a 23: sem Misto | PDF com Misto | prévia)

- **Escola 7 (B só nesta página):** a pintura sai **com a cor**, o texto em preto e branco, com a pontuação toda. No Preto e branco sem Misto a pintura sai cinza. Bom.
- **Opus Majus 20 (A):** a foto da estátua sai com o tom creme do original, a legenda em preto e branco e inteira. Bom.
- **Horas 11 (A):** o oval sai com as letras na cor delas (vermelho e azul) e papel branco atrás; a moldura em cor. Sem Misto, as letras do oval saem pretas. Sobram uns tracinhos pretos na beirada esquerda (bem menos que sem Misto).
- **Palatino 5 (A):** o retrato com o traço marrom e o papel branco dentro da gravura (P2). Fica mais claro e "sujo" que o Preto e branco puro, como o implementador avisou.

**Prévia × PDF:** o PDF da janela é idêntico ao do mesmo projeto processado sem janela. A prévia "Rápida" (110 DPI) perde detalhe pequeno: some vírgula e pingo de "i" na Escola 7, e **na Opus 20 a legenda "ROGER BACON / The Hope-Pinker Statue…" quase some na prévia** (imagem 24), enquanto sai inteira no PDF. Conferi que isso **já acontecia** no Preto e branco sem Misto, com o código novo e com a mesma resolução (imagem 25): não é do Misto. Mas é ruim para o Kaique escolher entre A, B e C olhando a prévia, porque ele pode trocar de botão por um defeito que o PDF não tem.

## (c) Os dois bugs anotados pelo implementador

1. **Confirmado.** No livro 2, a Escola 7 com "Só as letras" ligada mostra a faixa "**Esta página tem cor - o preto e branco vai perder a ilustração.**" e o botão laranja "usar Mágico pro nesta" (imagem 14). No Misto a ilustração **não** se perde (imagem 20). O "Para revisar" conta 3 "Tem cor" que, com o Misto, são alarmes falsos; as três páginas ficam laranjas na tira. O alerta é decidido uma vez, ao analisar o livro (`core/analise.py`, `analisar_pagina`), sem olhar o "Só as letras".
2. **Confirmado.** Página 2 (Opus 20) com o filtro Original: o cartão "Preto e branco" mostra a estátua em **preto e branco duro, sem a foto** (imagem 09). Ao clicar nele, a página sai com a **foto em cor** (Misto A; imagem 10). Quem olha o cartão escolhe às cegas. Os cartões são feitos por `aplicar_filtro` puro (`ui/tarefas.py`, `_TarefaCartoes`), sem gravura nem Misto. (Os cartões Melhorar e Mágico pro da Opus 20 também saem estourados pelo mesmo motivo; isso é antigo.)

## (d) "Para revisar" com "Tinta forte fora do texto"

- **Livro 1: 0 de 4.** **Livro 2: 3 de 8** (Palatino 9, Graduale 222, Rhetorica 73), como a lista do implementador previa. A faixa diz "Sobrou bastante tinta forte fora do texto que eu achei (pode ser música, letra grande, desenho ou mancha escura). Confira se ficou certo." e o botão é "está bom assim" (imagem 15).
- Somado ao alerta de cor falso, o livro 2 ficou com **4 de 8 páginas laranjas e 6 avisos** no "Para revisar".
- **Minha opinião:** com o A (padrão), a tinta forte é **guardada**; o aviso, nessas páginas, quase sempre vai mandar o Kaique olhar uma página que saiu certa (moldura de filetes, pauta, chaves). Num livro de 300 páginas com molduras em todas, seriam centenas de "está bom assim", e o aviso deixaria de ser lido (o próprio comentário no código diz isso). Onde ele importa é no **C** ("Só o texto achado"), que joga essa tinta fora. Sugiro, para o Samuel decidir: deixar o aviso só no C; ou, no A, só quando passar de um número bem maior; ou transformar em "observação do livro" quando cair em quase todas as páginas, como já acontece com a cor. E consertar o alerta de cor antes, porque os dois juntos dobram a lista.

## (e) Projeto antigo

- Projeto gravado na janela pelo `ace15b2` (livro 1, Preto e branco) aberto pelo programa novo: "Só as letras" desmarcada no livro e nas páginas, o leitor de texto **não** é aberto (não gasta memória), prévia em 2,9 s, janela sem travar.
- PDF gerado pela janela nova com esse projeto: **4 de 4 páginas idênticas** ao `ace15b2` processando o mesmo projeto.
- Também: o mesmo projeto com os campos novos do Misto (desligados), lido pelo `ace15b2`, sai idêntico (o programa antigo ignora os campos que não conhece).

## Tempos

| O quê | Tempo |
|---|---|
| "Conferir" na tela "O que fazer" até a 1ª prévia do Misto A (PC carregado, pytest rodando) | **17,4 s** (o leitor abriu aos 16 s); pior resposta da janela 0,16 s |
| "continuar" o projeto com Misto, PC carregado (outro verificador rodando, pouca memória) | 34,8 s até a prévia A; **uma parada de 6,2 s da janela** logo no começo |
| "continuar" o projeto com Misto, PC parado, rodada 1 / 2 | **10,8 s / 6,0 s**; pior resposta 0,16 s (não travou) |
| `ace15b2`, "continuar" (sem Misto) | 2,4 s; pior resposta 0,10 s |
| Programa novo abrindo o projeto do `ace15b2` (sem Misto) | 2,9 s; pior resposta 0,13 s |
| Trocar A → B só na página | 0,9 s |
| Desfazer / Refazer pelo menu (inclui andar no menu pelo teclado) | 3,8 s / 4,2 s |
| Gerar o PDF de 4 páginas com Misto (janela) | 17,1 s |
| Processar sem janela, mesmo livro: sem Misto 21,6 s (novo) × 18,5 s (`ace15b2`); com Misto 29,4 s | |

A parada de 6,2 s apareceu uma vez, com o PC carregado pelo outro verificador; nas duas medidas com o PC parado não houve parada. Não consigo dizer se foi o leitor abrindo (ele abre numa linha à parte, mas carregar a biblioteca pode segurar o Python inteiro) ou só o PC sem memória. Fica como ressalva.

## Ressalvas e coisas estranhas

1. **Bloco AJUSTE espremido** (imagens 10 e 11): entrando na aba Filtro numa página Original e escolhendo o cartão Preto e branco, o bloco AJUSTE (com "Só as letras" e os três botões) vira uma faixa vazia e os botões "Aplicar em" ficam sem texto, até trocar de aba. **Acontece igual no `ace15b2`** (imagem 17): é o bug antigo "bloco AJUSTE sumiu", não é do Misto. Mas agora ele também esconde os botões do Misto.
2. **Cartão que fica "preparando…" para sempre** depois de trocar o filtro na mesma página: também acontece no `ace15b2` (antigo; o cache dos cartões não guarda o filtro que estava escolhido).
3. Na tela "O que fazer", "Só as letras" aparece **mesmo com o filtro Original** escolhido (só vale no Preto e branco). Pode confundir; o agente de layout decide.
4. A frase-resumo continua dizendo "**deixar tudo em preto e branco** e separar as gravuras do texto" com "Só as letras" ligada.
5. Clicar num cartão de filtro escolhe o filtro **e abre "Ver de perto"** (é de propósito, já era assim). Para quem pilota, é preciso fechar a janela antes do próximo clique.
6. Na aba Bordas, com uma faixa de alerta, os botões de baixo saem **cortados** em 1280 × 657 ("ão cortar esta", "Mágico pro n", "stá bom assin"; imagem 14 e 15). Antigo (a linha não cabe), mas o aviso novo faz aparecer em mais páginas.
7. Antes de processar: "Ainda tem 3 páginas que eu não tive certeza" enquanto o "Para revisar" dizia "nada pendente" (bug antigo, já na lista).
8. Prévia "Rápida" perde letra miúda (legenda da Opus 20): antigo, mas atrapalha escolher entre A, B e C.
9. A prévia do A da Escola 7 da primeira vez e a de depois do desfazer não são iguais ponto por ponto (vírgulas e manchinhas claras dentro da gravura); a diferença não se vê a olho. Não investiguei a causa.
10. Não testei: a roda do mouse; o C ("Só o texto achado") na janela; as listas de "Mais opções" trocadas (só abri e fechei); o Kraken; o caso de o leitor não abrir. O `teste_botoes.py` não cobre o Misto.
11. O PC estava com pouca memória no começo (1,8 GB livres, outro verificador e o pytest rodando). Os tempos com o PC carregado valem pouco; os com o PC parado estão marcados.

## Bugs para a Lista de bugs (05/10, com print)

- **Misto 1:** alerta "Esta página tem cor - o preto e branco vai perder a ilustração" (e o botão "usar Mágico pro nesta") com "Só as letras" ligada. Print 14.
- **Misto 2:** cartão "Preto e branco" da aba Filtro mostra o Preto e branco sem Misto. Print 09 × 10.
- **Antigo, agora mais visível:** bloco AJUSTE espremido depois de escolher Preto e branco numa página Original (também no `ace15b2`). Prints 10, 11, 17.
- **Antigo:** prévia "Rápida" apaga a legenda miúda da Opus 20 (PDF inteiro). Prints 24, 25.

## Onde está

- Este parecer: `relatorios/conferir/misto-no-programa-2026-10-05/verificador/parecer-verificador-misto-no-programa.html`
- Prints: `verificador/prints/` (23 imagens, 4 MB). Scripts e medidas: `verificador/scripts/` (não vão para o git).
