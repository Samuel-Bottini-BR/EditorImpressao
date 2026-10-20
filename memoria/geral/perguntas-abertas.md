# Perguntas abertas: o que espera o Samuel

Montado em 20/10/2026 a partir do Registro de mudanças do [plano](../../docs/plano/PLANO-DEFINITIVO.md) (até
19/10/2026), da [PARTE -16 e da PARTE -15 do histórico](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md)
e dos relatórios dos ajudantes que montaram as fichas. **Não decida no lugar dele**: enquanto a pergunta estiver
aqui, vale o que está no plano hoje.

Como manter: quando ele responder, registre no plano (as duas cópias) e na ficha do item, e **tire a pergunta
daqui** (ou mova para "Respondidas recentemente" com a data). O `conferir_memoria.py` avisa quando uma pergunta desta
lista com nome entre crases já aparece como decidida no Registro.

## 1. Na página de escolhas (https://claude.ai/artifact/EJoJq5mocxi3vbNxU8ZecV)

Abertas e sem resposta na última leitura (Registro 19/10/2026: "`g7-borda-ate-onde` e `g9-folha-maior-impressao`
continuam sem resposta").

- `g7-borda-ate-onde` — "Página com borda preta: até onde vai o corte que o programa sugere?" Opções: "Tira só o
  preto" · "Vai até a moldura (o que está impresso)" · "O Kaique escolhe por livro: só o preto, ou até a moldura"
  (sugestão, começando em "até a moldura") · "Ainda não entendi". Comentário dele de 13/10/2026: "Vai depender do
  livro, mas se tivessemos maneira de embranquecer esse preto depois poderia ser usa a busca do scantailor, hoje no
  programa temos o motor de busca só do scantailor?" (respondido na página em 14/10/2026). **Trava:** ligar o corte
  da caixa do conteúdo (Implementador 4, ramo `fase2-caixa-conteudo`) só depois desta resposta (Registro 19/10/2026).
  Itens [2.13](../itens/2.13.md), [2.5](../itens/2.5.md), [2.14](../itens/2.14.md).
- `g9-folha-maior-impressao` — "A folha muito maior (tabela dobrável): como ela sai impressa?" (qual vem de
  fábrica). Opções: "Ajustar: gira de pé e reduz até caber na página A5" (sugestão; ~73% contra ~81% das páginas
  comuns) · "Tamanho real, numa folha A4 à parte" · "Pôster" · "Divide em duas páginas" · "Ainda não entendi". A
  dúvida dele ("quando ela foi impressa a primeira vez, ela foi impressa um folha a4 inteira para uma tabela só
  né?") foi respondida na página em 14/10/2026. Itens [2.6](../itens/2.6.md), [2.4](../itens/2.4.md); página
  [opusmajus-256](../paginas-de-teste/opusmajus-256.md).

## 2. Na página de conferência (https://claude.ai/artifact/J8AwcyyUwrZ2n7kSevyGvX)

- `cg6` — conserto do corte com borda preta (defeito do G6). Marcado "Melhorar" em 13/10/2026, com a dúvida dele:
  "Só não sei se vamos fazer esse concerto agora ou deixar para depois e o corte de borda continua assim e segue
  para o aplicativo e depois arrumamos." Reaberta (opção esvaziada) em 14/10/2026 até o implementador acertar o
  Pesel 21 (tem de sair como sai hoje). Volta para ele com a sugestão de fazer agora. Itens [2.2](../itens/2.2.md),
  [2.13](../itens/2.13.md); páginas [pesel-021](../paginas-de-teste/pesel-021.md),
  [cursus-003](../paginas-de-teste/cursus-003.md).
- **"Para revisar", aba 4 da conferência (ainda por montar)** — três perguntas que o verificador escreveu (ramo
  verif-para-revisar-2026-10-13, `conferencia.json`): (1) medir o livro inteiro por trás, com andamento, na resolução
  do PDF (hoje só a página visitada é medida, e a lista "Antes de processar" mostra só o que já foi medido; Lista de
  espera 12/10/2026); (2) as três contagens que não batem (no Camões: 105 linhas, "100 páginas", 40 no painel, 6 na
  janela de salvar; Registro 13/10/2026); (3) mostrar na tela o mesmo que o PDF (a prévia de 110 DPI decide diferente
  do PDF de 300; Lista de bugs 13/10/2026, "a tela mostra o que o PDF não tem"). Ficha
  [para-revisar](../itens/para-revisar.md).

## 3. Layout: rodada 14 (ainda não publicada)

Da PARTE -15 §4 item 8 e do Registro 12/10/2026 (rodada 13):

- qual vista de "Todas as páginas" vem de fábrica;
- onde se escolhe a "área de trabalho 1" e os jeitos do menu da direita;
- os menus;
- o nome "o mesmo da página";
- a frase nova para o aviso de `core/analise.py` "Confira na aba Marcar - se for escrita, marque como letra." (as
  abas saíram; Lista de bugs 13/10/2026);
- pendências sem dono achadas em 12/10/2026: receitas, ordem arrastando e "pular as páginas mexidas" do painel
  Automático; tela inicial sem barra de menus.

Ficha [layout](../itens/layout.md).

## 4. Feitas no chat ou no Registro, sem resposta registrada

- **Pesel 21 no conserto do corte** — o cartão escuro passa a sair cortado rente (15,7 × 24,1 → 14,5 × 20,6 cm,
  legenda a 1 ou 2 mm da borda): "efeito de lado, para o Samuel decidir" (Registro 13/10/2026). Em andamento: o
  Implementador 1 foi liberado em 19/10/2026 para fazer o Pesel 21 sair como sai hoje.
- **Endireitar: aviso "as contas discordam" em página reta** (0,2° de diferença, limite 0,3°; a análise mede a 150
  DPI e a tela a 300): "Consertar exige escolha do Samuel (pergunta a montar)" (Lista de bugs, 09/10/2026). Item
  [2.2](../itens/2.2.md).
- **Girar "só as pares" num livro dividido** — com a página "2" na tela (folha 1), o aviso diz "Você está numa folha
  ímpar": certo, mas pode confundir o Kaique. "Pergunta a levar ao Samuel" (Registro 06/10/2026). Item
  [2.3](../itens/2.3.md).
- **Dividir: folha que deixou de ser dividida com uma metade apagada** — sai inteira (hoje) ou só a metade viva?
  Em 07/10/2026 ele não escolheu ("não entendi, explique melhor e com exemplos."; depois "vamos discutir mais
  isso"), e a conversa virou a página branca no lugar da apagada (Lista de espera, Fase 6). Não há registro de
  resposta à pergunta da metade. Item [2.1](../itens/2.1.md).
- **"Marcar como" iluminura/pintura e moldura** — decidido que entra, mas a fase fica "a definir pelo Samuel" (Lista
  de espera 12/10/2026). Itens [1.5](../itens/1.5.md), [layout](../itens/layout.md).
- **Escala do notebook do Kaique** — "Isso pode ser resolvido depois" (05/10/2026): "continua em aberto, a
  perguntar antes do plano de layout" (Registro 05/10/2026). Ver [kaique.md](kaique.md).
- **Ferrugem rosada na Pesel 2** (item 1.1): "Pela regra R4 talvez o certo seja a mancha sumir, não mudar de cor:
  decisão do Samuel" (Lista de bugs, 29/09/2026). Item [1.1](../itens/1.1.md).
- **Aba Filtro "a aperfeiçoar"**: a fase (Fase 2, junto de 2.7 e 2.8) foi "sugerida pela gerente, a confirmar pelo
  Samuel" (plano, Fase 2).
- **Lentidões aceitas pela gerente "a rever pelo Samuel"**: o "Só as letras" 3,4% mais lento com o conserto do
  desenho (Registro 06/10/2026, "gerente (a rever pelo Samuel)"). Pela decisão de 19/10/2026 (lentidão pequena no
  meio da fase vai para a Fase 5), provavelmente fica para a [5.1](../itens/5.1.md); não confirmado com ele.
- **Leitura da gerente "a do Editor"** na lista "Conta" do Endireitar (Registro 13/10/2026, "para o Samuel
  confirmar"); a PARTE -15 §3 diz "ele viu na conferência e não contestou".
- **Arrumação, sem resposta no chat** (PARTE -16 §4): apagar a página vazia https://claude.ai/artifact/NwYyesZwRmQGvKnToYJLfW ?
  Apagar `C:\Users\fotog\AppData\Local\Temp\p2.py` (arquivo vazio deixado por um agente)? E a pasta de rascunho
  criada fora do projeto pelo implementador do dividir (Registro 06/10/2026, "pode ser apagada?").

## 5. Respondidas recentemente (para não perguntar de novo)

- Os agentes dos itens 4 e 6 da PARTE -16 ("posso mandar os agentes...?"): liberados em 19/10/2026 ("Implementador 1
  - ok / Verificador - ok / ...", Registro 19/10/2026).
- Mágico pro +1,1% do "Para revisar": Fase 5 (19/10/2026: "vamos deixar esse concerto de lentidão para o final, para
  a fase de desempenho.").
- As cinco decisões de 19/10/2026 (testes, memória, sessões, teste de reversão, velocidade): CLAUDE.md §4.6 a §4.9.
- Impressão (14/10/2026): g10-papel-ou-pagina, g10-ajustar-todas, g11-margem-impressora ("1 cm a partir de onde a
  impressora imprime (1,3 cm do papel)"), g12-diminuir-um-lado ("Em todas, e dá para mudar uma folha só"). Ficha
  [2.6](../itens/2.6.md).
- Geometria (13 e 14/10/2026): g8-guias, g8-moldura-tinta-fora, g9-pagina-muito-maior. Fichas
  [2.5](../itens/2.5.md), [2.13](../itens/2.13.md), [2.4](../itens/2.4.md).
