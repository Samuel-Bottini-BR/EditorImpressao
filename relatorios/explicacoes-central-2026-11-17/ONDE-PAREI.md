# ONDE-PAREI — explicações com provas para a Central (17/11/2026)

Verificador. Tarefa: refazer 11 respostas que o Samuel não entendeu (9 do pedido + 2 extras: au-d-484 e
au-d-492), com prints do caso real, no modelo do girar. **Nenhuma linha do programa mudou.** Nada foi
gravado na Central (a gerente grava). Ramo `explicacoes-central-2026-11-17`, a partir de `obra-2026-10-26`
(`a9d81030`), worktree `.claude/worktrees/explicacoes-central`.

**Situação: PRONTO (todas as 11 respostas e os prints abaixo).**

## Decisões que esta tarefa precisa cumprir

- **§11.13 (Samuel, 13/11/2026)** — "precisa ajeitar para isso como regra [...] para responder e fazer
  perguntas". Começar pelo que é e onde fica; sem palavra de dentro; print que prova, no modelo do girar;
  caso real conferido; caminho e se é defeito ou escolha; "O que você escolhe"; curto; controle; origem;
  situação. Depois de "Ainda não entendi": mudar o jeito, não só as palavras.
- **§10 modelo de print (Samuel, 10/11/2026)** — "o jeito como você mostrou o o girar pagina ficou muito
  bom, pode colocar ele como exemplo de como deve ser feito os prints de uma mensagem explicativa".
- **§4.10 (Samuel, 21/10/2026)** — caminho inteiro, só páginas que vão ser impressas ("não faça mais testes
  com lombadas de livros").
- **§11.12 (Samuel, 13/11/2026)** — "o agente não pode fazer gambiarras [...] funcionava de maneira
  diferente em vários lugares" (para au-d-487: procurar conta própria/desvio no botão direito da grade).
- **D-605 (03/11)** — nada novo muda o já testado (aqui: nada muda; só prints e texto).
- **Não abrir na tela dele** — janela fora da tela (-32000, PrintWindow), nunca na tela do Samuel.
- **D-374 (04/11)** — "o agente não vai escolher os nomes ele pode sugerir opções".
- Decisões citadas nas perguntas (linhas inteiras conferidas no Livro da versão de teste): D-501, D-500
  (e D-560, já respondida por ele em 27/10), D-489, D-541, D-487, D-484, D-492, D-335, D-274/D-283, D-367.

## O que já está escolhido e testado aqui

Nada foi mexido: tarefa só de prints e texto. Provas que já existem e que rodei no PC (um arquivo):
`tests/test_decisoes_dividir.py -k bug_9c` → **3 passaram** (as do La vida eterna de verdade, D-500).

## Como fica para quem usa e no livro

Nada muda no programa nem no PDF. Os prints mostram a versão de teste. Onde um print mostra um nome novo,
ele tem o carimbo amarelo **SIMULAÇÃO** (texto trocado só naquele print).

## Como foi feito (o caminho de cada print)

- Janela de verdade (`JanelaPrincipal` da worktree), **fora da tela** (-32000), cliques e teclas por
  mensagens do Windows, prints por PrintWindow (`relatorios/obra-etapa3/roteiro/base.py`). Dados, projetos
  e TEMP no scratchpad. Os livros são **cópias** (o original só é lido):
  - **La vida eterna** (`D:/Livros para editar/.../La vida eterna y La profundidad del alma.pdf`), as 12
    primeiras folhas (24 páginas), aberto do zero e dividido pelo **Automático só com "Dividir"** (motor
    de corte de fábrica, o do ScanTailor), filtro Original.
  - **Palatino** (acervo), folhas 20 a 31 (páginas de texto). Na abertura o programa pergunta do fundo
    separado: respondido "Não, deixar como está".
- Pilotos: `piloto_dividir.py` (501, 500), `piloto_grade.py` (492, 484, 487), `piloto_trabalho.py` (541,
  jeito-pb, antes-de-processar, folha-pagina), `piloto_livros.py` (tela-livros, folha-pagina, 489),
  `piloto_extra.py` (menu Marcar, botão direito na miniatura). Montagem: `montar.py` + `montar_mais.py`.
  Prints crus em `crus/`, prontos em `prints/<item>/`. **Abri e conferi todas as imagens prontas.**
- O que foi chamado por função (não por clique), e por quê: o clique no cartão do "Para revisar"
  (`_ir_do_para_revisar`, o mesmo que o cartão chama); marcar a etapa "Limpar a folha" e o Preto e branco
  dela na janela grande do Automático (as caixinhas da janela); o "remover da lista", "renomear" e
  "começar de novo" do menu do cartão (pelo `trigger` do item do menu, que é o clique nele). O resto foi
  clique de verdade.
- **Não cliquei em "procurar de novo"**: abre a janela do Windows de escolher arquivo, que apareceria na
  tela do Samuel.

## Achados para a gerente (não vão para o Samuel assim; são ressalvas e defeitos)

1. **Defeito de desenho no "Para revisar"** (visto nos dois testes): depois de clicar no cartão da página
   2 e depois no da página 7, os botões laranja do cartão da página 2 ("Deixar em branco", "Tirar do
   livro", "está bom assim") ficam desenhados por cima do cartão da página 7, cobrindo o texto e o
   "aceitar o corte". Print: `crus/dividir/07-cartao-pagina-7.png`. Nos prints do Samuel o painel foi
   cortado para não distrair. Vai para a Lista de bugs, se a gerente concordar.
2. **Remendos na grade "Todas as páginas" (§11.12), achados no código** (`ui/tela_conferir.py`):
   - girar: `_acao_nas_escolhidas` tem conta própria (`(rotacao + giro) % 360`, escrita em dois lugares,
     linhas 7322 e 7382) e um desvio "se alguma escolhida é metade de folha, vai por
     `_girar_as_escolhidas_que_sao_metade`; senão, pelo caminho de antes". O Girar da página usa
     `girar.campos_do_giro`/`campos_do_giro_das_paginas` (todas viradas como a da vez, D-035); a grade
     gira cada uma ¼ a partir de onde está. Resultado diferente para o mesmo pedido (uma já deitada + uma
     em pé: na grade terminam diferentes).
   - "trazer de volta" da grade grava `{"apagada": False, "em_branco": False}`; o "trazer de volta" da
     página (`apagar_pagina`) só desfaz o "tirada" (o "em branco" tem o seu "voltar a página").
   - "deixar em branco" e "tirar do livro": o mesmo resultado, mas a lista de campos está escrita de novo
     na grade (`_acao_nas_escolhidas`) em vez de chamar `_deixar_em_branco`/`apagar_pagina`.
   - "dividir" usa a conta do "dividir esta" (core/dividir_a_mao) e "rodar o automático nelas" usa o mesmo
     caminho do "escolher páginas..." (`escolhidas_para_o_automatico`): sem remendo.
   - A grade **não tem botão direito** (`_Quadro.mousePressEvent` ignora o botão direito).
3. **Dois caminhos para o mesmo "ir ao aviso" (§11.12)**: o clique no cartão do "Para revisar"
   (`_ir_do_para_revisar`, olha só o PRIMEIRO aviso da página e usa `avisos_do_livro.DA_DIVISAO`) e o
   "ver" da lista (`_ir_para_o_aviso`, olha o aviso escolhido e tem a sua própria lista
   `(NAO_PARECE_DUPLA, LOMBADA_INCERTA)`). Também levam a ferramentas diferentes para um aviso de página
   (cartão → Mão; "ver" → Filtro). Ex.: página 9 tem "Parece em branco · Lombada incerta": o cartão leva à
   página; o "ver" da linha "Lombada incerta" leva ao Dividir.
4. **D-489 diz "quando o PDF mudou"; o programa não faz isso pelo cartão**: PDF trocado por outro no mesmo
   lugar → "Este não é o mesmo livro", não abre (não recomeça). O recomeço foi visto com o trabalho salvo
   estragado. A resposta ao Samuel diz o que o programa faz de verdade.
5. **D-492 cita "Tirar o fundo" na lista do menu**; o menu Filtro tem Original, Preto e branco, Melhorar e
   Mágico pro. Página em "Tirar o fundo" fica sem tique (dito na resposta).
6. **nm-folha-pagina**: o "livro aberto" da tela dos livros diz "página 3 de 12" e mostra a FOLHA 3
   inteira (duas páginas) — a confusão continua na versão de teste (print `folha-2`).
7. **D-500 já foi respondida** por ele: D-560, 27/10, "Manter (recomendo)". A resposta cita isso.
8. **nm-tela-livros**: o aviso de PDF trocado diz "procurar de novo"; o livro aberto de um livro perdido
   diz "Use “Mais...” > “procurar o livro”" (visto na 1ª rodada do piloto; o print final usa só o aviso).
9. **D-541, limites de tamanho (5% a 4 vezes) não testados**: os prints mostram 126% e 80%; os limites
   vêm só do Livro. A resposta ao Samuel não cita os números.
10. Memória do PC baixa durante o trabalho (um jogo e o CapCut abertos); um piloto falhou uma vez por isso e
   a janela de teste chegou a ser minimizada pelo Windows; o piloto passou a pô-la de volta FORA da tela
   antes de cada clique e print (`comum.normal`). Nada apareceu na tela dele.

## Andamento

- [x] au-d-501 · [x] au-d-500 · [x] au-d-489 · [x] au-d-541 · [x] au-d-487 · [x] nm-folha-pagina ·
  [x] nm-jeito-pb · [x] nm-tela-livros · [x] nm-antes-de-processar · [x] au-d-484 · [x] au-d-492

## Como cumpri cada decisão

- §11.13: cada resposta abaixo começa pelo que é e onde fica, responde a frase dele repetida, não tem
  código nem número de decisão no meio (só no fim, entre parênteses), diz caminho, defeito ou escolha,
  "O que você escolhe" com "Só comentário" e a sugestão, controle, origem e situação. Conferida a lista
  dos 10 pontos item a item (tabela no fim).
- §10 modelo do girar: todo item tem `*-0-resumo.png` primeiro, faixas com cor e título grande (azul = como
  é hoje; verde = depois do clique ou opção sugerida; laranja = outra opção/cuidado), uma frase em cada,
  o que olhar circulado em vermelho, e as imagens de cada passo separadas.
- §4.10: livro aberto do zero, Automático pelo caminho do Kaique, só páginas de texto (nenhuma capa ou
  lombada); cada faixa diz livro, página e o que foi ligado.
- §11.12: procurado no código (achados 2 e 3).
- Não abrir na tela dele: tudo fora da tela; "procurar de novo" não clicado.
- D-374: nos itens de nome, opções sugeridas, quem escolhe é ele; espaço para ele escrever outro nome.

---

## Respostas para a Central

Caminho dos prints: `relatorios/explicacoes-central-2026-11-17/prints/<item>/` (o `*-0-resumo.png` vai
primeiro; os outros, na ordem do número).

### au-d-501 — Dividir: para onde a tela vai

**Do que se trata.** A ferramenta Dividir (primeiro ícone da barra da esquerda, ou tecla D) mostra a foto
do scan inteira, com a linha azul no meio. Aqui é: para onde a tela vai em três momentos.

**O que acontece hoje** (versão de teste; La vida eterna, cópia, dividido pelo Automático):
1. Ao abrir um livro já dividido, ele abre na página 1, uma página por vez (ferramenta Mão). Nunca no
   Dividir.
2. Se você está no Dividir e roda o Automático com "Dividir folhas ao meio", a tela sai sozinha do Dividir
   e mostra a página, uma por vez.
3. No "Para revisar", clicar num aviso comum (ex.: "Parece em branco") leva à página. Clicar num aviso da
   divisão ("Lombada incerta", "Não parece dupla") leva ao Dividir, naquela folha, para conferir a linha.

O Dividir continua a um clique (ícone ou tecla D) para consertar uma folha.

**Sua dúvida:** "o jeito como foi feito a explicação, tudo junto, fica uma forma muito confusa" → Agora é
uma coisa por vez: um print para cada momento. Em vermelho, o nome da ferramenta (no alto) e o contador
(embaixo).

**De onde veio:** escolha da gerente (27/10) para cumprir o seu pedido de 26/10: "quando eu escolher para
começar no automatico e dividir as folhas o livro tem que aparecer em uma pagina por vez para mim".
**Situação:** já está na versão de teste; você já marcou "Concordo".

**O que você escolhe:** se os três momentos ficam assim.
- **Continua: concordo** — nada muda.
- **Quero diferente** — diga qual dos três momentos; entra na fila.
- **Só comentário.**
Sugestão: continua.

Prints: `au-d-501/501-0-resumo.png`, `501-1-abrir-o-livro.png`, `501-2-automatico-no-dividir.png`,
`501-3-clicar-no-aviso.png`. (Para consulta: D-501, D-007.)

### au-d-500 — A linha do Dividir quando cai na beirada

**Do que se trata.** Na ferramenta Dividir, o programa põe a linha que separa as duas páginas de cada foto
do scan. Ele usa a conta do ScanTailor.

**O que acontece hoje.** Quando a conta do ScanTailor põe a linha na beirada da foto (longe do meio), o
programa não usa essa linha: corta perto do meio, pela conta dele, e põe o aviso "Lombada incerta" para
alguém conferir.

**Sua dúvida:** "Eu preciso de provas disso" → Prova no La vida eterna (cópia), folha 4 do scan (páginas 8
e 9 do livro), páginas como saem no PDF:
- **Laranja — se valesse a linha do ScanTailor:** a linha cairia a 10% da largura, antes da linha escura da
  beirada do livro. A página 7 sairia uma tira fina em branco e a página 8 sairia com as duas páginas do
  livro juntas.
- **Verde — como é hoje:** a linha fica a 53%; a página 7 sai com a página 8 do livro e a página 8 com a
  9. A folha ganha o aviso "Lombada incerta".
- Nas outras 10 folhas do teste o ScanTailor acerta o meio e nada muda.

**É defeito ou escolha?** É uma proteção contra um erro da conta do ScanTailor, achado no teste de 27/10
neste livro. **Você continua no controle:** na folha com aviso, "Duas lado a lado" mostra a linha; dá para
arrastá-la e clicar "aceitar o corte".

**Situação:** você já respondeu isto em 27/10, na pergunta da troca sozinha da lombada: "Manter
(recomendo)". Aqui está só a prova que faltava.

**O que você escolhe:**
- **Continua como você escolheu em 27/10.**
- **Quero diferente** — por exemplo, usar sempre a linha do ScanTailor, mesmo na beirada.
- **Só comentário.**
Sugestão: continua.

Prints: `au-d-500/500-0-resumo.png`, `500-1-linha-do-scantailor.png`, `500-2-como-e-hoje.png`,
`500-3-o-aviso-no-programa.png`. (Para consulta: D-500, D-560.)

### au-d-489 — Quando a conferência começa de novo

**Do que se trata.** "Começar a conferência de novo" é quando o programa deixa de lado o que você já fez
num livro e o abre como novo.

**O que acontece hoje** (La vida eterna, cópia, testado na janela):
1. **Mudar uma etapa no Automático nunca recomeça.** Dividi, pus a página 3 em Preto e branco à mão,
   depois rodei o Automático com "Endireitar": a página 3 continua em Preto e branco e o Histórico mostra
   as três coisas. Ctrl+Z desfaz só o Automático.
2. **PDF trocado por outro no mesmo lugar: o programa não abre o trabalho.** Avisa "Este não é o mesmo
   livro" e pede para apontar o PDF certo. O trabalho fica guardado.
3. **"começar de novo"** (botão direito no cartão do livro, ou "Mais..."): só quando você pede. Pergunta
   antes e abre o livro como novo.
4. **Trabalho salvo estragado** (ex.: o computador desligou no meio da gravação): começa de novo sozinho,
   avisa e guarda uma cópia do trabalho antigo.

**Sua dúvida:** "Sua mensagem não ficou clara." → A mensagem queria dizer: mudar o Automático nunca apaga o
que você fez; o programa só começa de novo quando você pede (3) ou quando o trabalho salvo estragou (4).
Cada caso tem o seu print. Um acerto: a frase antiga falava em "quando o PDF mudou". No teste, com o PDF
trocado o programa não começa de novo: ele se recusa a abrir (caso 2).

**De onde veio:** escolha da gerente (27/10), por causa do defeito de 29/09 (o trabalho salvo voltava por
cima e se perdia o que você tinha mudado). **Situação:** na versão de teste; você ainda não testou.

**O que você escolhe:** se é assim que quer.
- **Concordo** — fica assim.
- **Quero diferente** — diga qual dos quatro casos; entra na fila.
- **Só comentário.**
Sugestão: concordo.

Prints: `au-d-489/489-0-resumo.png`, `489-1-mudar-etapa.png`, `489-2-pdf-trocado.png`,
`489-3-comecar-de-novo.png`, `489-4-trabalho-estragado.png`. (Para consulta: D-489, D-002.)

### au-d-541 — Como a ferramenta Mover mexe

**Do que se trata.** A ferramenta "Mover e redimensionar" (ícone da cruz na barra da esquerda, ou tecla F)
muda o lugar e o tamanho do que está impresso dentro da página.

**O que acontece hoje** (La vida eterna, cópia, página 3; em cada faixa, a tela e a página como sai no PDF):
1. **Arrastar** em cima da página: ela anda com o mouse. O que passa da beirada fica riscado de vermelho e
   fica de fora no PDF.
2. **Puxar um dos 4 quadradinhos dos cantos:** cresce ou diminui por igual, sem esticar. Se passar da
   beirada, a página ganha um aviso; o programa não diminui sozinho.
3. **Escrever o número** em "Tamanho do conteúdo (%)": faz o mesmo (80 = menor, no meio, com margem).
4. **Arrastar muito:** o programa para quando o meio do conteúdo chega na beirada, para a página não sumir
   da vista.
O PDF sai igual à tela. Ctrl+Z desfaz cada mexida.

**Sua dúvida:** "Isso não é um print da ferramenta mover [...] não tenho exemplo concreto" → Tem razão: o
print antigo era do Endireitar. Agora são prints da própria ferramenta Mover, um por mexida, com o PDF ao
lado.

**De onde veio:** seus pedidos de 22/09 e 26/10 ("como é no photoshope, que você arrasta a hora que quiser
e aumenta a hora que quiser"). Os detalhes (o meio não sai da página, o menor e o maior tamanho) são
escolha da gerente (27/10). **Situação:** na versão de teste; você ainda não testou.

**O que você escolhe:** se o Mover fica assim.
- **Concordo** — fica assim.
- **Quero diferente** — ex.: deixar arrastar para fora além do meio; outro limite de tamanho.
- **Vou testar antes.**
- **Só comentário.**
Sugestão: concordo.

Prints: `au-d-541/541-0-resumo.png`, `541-1-M0.png` (a ferramenta), `541-2-M1.png` (arrastar),
`541-3-M2.png` (canto), `541-4-M3.png` (número), `541-5-M4.png` (até a beirada). (Para consulta: D-541,
D-008, D-017.)

### au-d-487 — A grade "Todas as páginas" com várias escolhidas

**Do que se trata.** A grade "Todas as páginas" (botão "ver todas", em cima das miniaturas) mostra o livro
inteiro; nela se escolhem várias páginas e se faz uma coisa em todas de uma vez.

**O que acontece hoje** (Palatino, cópia): escolhem-se as páginas com "marcar várias" (ou o quadradinho do
canto, ou Ctrl+clique). Os botões ficam na faixa de cima: girar ¼ ←, girar ¼ →, dividir, deixar em branco,
tirar do livro, trazer de volta, extrair..., rodar o automático nelas...

**Sua dúvida 1:** "Eu não testei o botão direito nessa grade" → A grade não tem botão direito: clicar com
o botão direito numa página da grade não abre nada (print 2). O botão direito que existe é o das miniaturas
de baixo e da página grande ("Desfazer nesta página", "adicionar página em branco"); esse você testou em
09/11 ("pagina em branco funciona").

**Sua dúvida 2:** "tem que ver se não tem gambiarra ai" → Procurei no programa. Achei três lugares em que
a grade faz a conta à parte, em vez de usar a mesma das outras ferramentas:
- **Girar:** na grade, cada página gira ¼ a partir de onde está. No girar da página (com "aplicar em"),
  todas ficam viradas igual à página da vez. Com uma página já deitada e outra em pé, na grade elas
  terminam diferentes; no girar da página, iguais.
- **"trazer de volta":** na grade, desfaz o "em branco" e o "tirar do livro" de uma vez. Na página sozinha,
  "trazer de volta" só desfaz o "tirar do livro".
- **"deixar em branco" e "tirar do livro":** dão o mesmo resultado, mas a regra está escrita duas vezes.
"dividir" e "rodar o automático nelas" usam a mesma regra das outras ferramentas.
É o tipo de remendo da sua regra de 13/11. Nada foi mexido (eu só confiro).

**Sua dúvida 3:** "não ficou claro o que você quer que eu concorde ou descorde" → Se a grade fica com estes
botões, deste jeito, e o que fazer com os remendos.

**De onde veio:** seu pedido de 24/09 (grade como o "Organizar páginas" do UPDF: várias escolhidas, girar,
apagar, extrair, inserir, dividir); o resto foi escolha da gerente (27/10). **Situação:** na versão de
teste.

**O que você escolhe:**
- **Os botões ficam; mandar consertar os remendos** — uma regra só para girar, e "trazer de volta" igual ao
  da página. Antes, a gerente confere se isso muda o girar da grade que você aprovou em 05/11.
- **Os botões ficam como estão, sem mexer.**
- **Quero também o botão direito na grade** — coisa nova; entra na fila.
- **Só comentário.**
Sugestão: os botões ficam e os remendos são consertados.

Prints: `au-d-487/487-0-resumo.png`, `487-1-botoes-da-grade.png`, `487-2-botao-direito.png`. (Para
consulta: D-487, D-334, D-636, D-623.)

### au-d-484 — Rodar o Automático só em algumas páginas

**Do que se trata.** O Automático (painel ou "janela grande") roda as etapas no livro todo, só na página da
tela, ou só nas páginas que você escolher.

**Sua dúvida:** "se você ler bem, eu falei: no livro, nas escolhidas e em uma pagina só, o que não dá para
fazer hoje, ele só roda em todas as paginas de uma vez, e eu não consigo ir na tela grande selecionar
paginas e rodar automatico só nelas." → Na versão de teste dá, por dois caminhos. Testei os dois na janela
de verdade (Palatino, cópia, etapa "Limpar a folha" em Preto e branco, para ver no PDF o que mudou):
1. **Pelo Automático:** painel Automático > "abrir em janela grande" > "escolher páginas..." > a grade abre
   > clique nas páginas 5 e 7 > "usar estas 2 páginas" > a janela volta dizendo "Rodar: nas páginas
   escolhidas (2)" > "Rodar". **Só as páginas 5 e 7 mudaram.**
2. **Pela grade:** "ver todas" > "marcar várias" > clique nas páginas 9 e 11 > "rodar o automático
   nelas..." > o Automático abre com "nas páginas escolhidas (2)" > "Rodar". **Só a 9 e a 11 mudaram.**
A lista "Rodar" tem também "só nesta página". Ela fica embaixo, perto do botão "Rodar", e começa em "no
livro todo". Gravuras e fotos, Margens iguais e Montar cadernos rodam sempre no livro todo (são do livro).

Se você testou e não conseguiu, diga onde travou que eu refaço o teste do seu jeito.

**Situação:** na versão de teste (atalho de desenvolvimento); você ainda não testou depois de 29/10.

**O que você escolhe:**
- **É isso que eu queria** — fica assim.
- **Quero diferente** — diga o quê.
- **Vou testar antes.**
- **Só comentário.**
Sugestão: testar pelo caminho 2 (a grade).

Prints: `au-d-484/484-0-resumo.png`, `484-1-janela-grande.png`, `484-2-grade-marcar.png`,
`484-3-janela-nas-escolhidas.png`, `484-4-resultado-5-e-7.png`, `484-5-grade-rodar-nelas.png`,
`484-6-painel-nas-escolhidas.png`, `484-7-resultado-9-e-11.png`. (Para consulta: D-484, D-002.)

### au-d-492 — O tique do menu Filtro

**Do que se trata.** O tique (a marquinha ao lado do nome) no menu Filtro, na barra do alto do programa.

**Sua dúvida:** "Mas esse tique só vai aparecer se eu clicar na aba lá de cima filtros né?" → Sim. O tique
só aparece com o menu Filtro aberto (clique em "Filtro", na barra do alto). Ele fica no filtro da página
que está na tela: página em Original → tique em "Original"; página em Preto e branco → tique em "Preto e
branco" (Palatino, cópia, páginas 1, 2 e 3).
Fora do menu, o filtro aparece de outro jeito, sem tique: no painel "Filtro da página" (borda azul no
filtro escolhido) e na frase de baixo ("Esta página vai sair em Preto e branco"). A marquinha verde nas
miniaturas é outra coisa: quer dizer "página conferida".
Um detalhe: o menu não tem "Tirar o fundo"; numa página em "Tirar o fundo", nenhum item fica com tique.

**De onde veio:** escolha da gerente (27/10), como nos menus do Windows. **Situação:** na versão de teste.

**O que você escolhe:**
- **Concordo** — fica assim.
- **Quero diferente** — diga o quê.
- **Só comentário.**
Sugestão: concordo.

Prints: `au-d-492/492-0-resumo.png`, `492-1-menu-filtro.png`, `492-2-fora-do-menu.png`. (Para consulta:
D-492.)

### nm-folha-pagina — "Folha" e "página"

**Do que se trata.** As palavras "folha" e "página" na tela. **Folha** = a foto que o scanner tirou (num
livro escaneado aberto, duas páginas numa foto). **Página** = cada página do livro que sai no PDF. No La
vida eterna, a folha 4 do scan vira as páginas 7 e 8 (print 1).

**O que acontece hoje.** Em alguns lugares a palavra está trocada. O pior é o livro aberto (tela dos
livros, um clique no cartão): em cima diz "24 páginas", embaixo diz "página 3 de 12" e mostra a folha 3
inteira. O número de baixo conta folhas, mas a palavra é "página".

**Sua dúvida:** "Gostei da segunda opção, mas não ficou claro, como essa mudança vai funcionar." → Com a
segunda opção só mudam as palavras de dois lugares:
1. **Livro aberto:** "24 páginas" vira "12 folhas, 24 páginas"; "página 3 de 12" vira "folha 3 de 12"
   (print 3, simulação).
2. **"Para revisar":** "Página 7" vira "Página 7 (folha 4)" (print 4, simulação).
Ficam como hoje: o botão "tamanho da folha..." do Mover e a etapa "Endireitar folhas tortas" do Automático
(print 5). O que os botões fazem não muda, nem o PDF.

**De onde veio:** sua regra de 12/10 (girar = folha, endireitar = página). **Situação:** só pergunta; o nome
escolhido entra com a arrumação nova do layout, como você pediu em 04/11.

**O que você escolhe:**
- **Segunda opção, como nos prints** — livro aberto e "Para revisar".
- **Primeira opção** — a segunda e mais: "tamanho final da página..." e "Endireitar páginas tortas".
- **Deixar como está.**
- **Só comentário.**
Sugestão: a segunda opção (a que você gostou).

Prints: `nm-folha-pagina/folha-0-resumo.png`, `folha-1-folha-e-pagina.png`, `folha-2-livro-aberto-hoje.png`,
`folha-3-livro-aberto-segunda-opcao.png`, `folha-4-para-revisar.png`, `folha-5-o-que-nao-muda.png`. (Para
consulta: D-367, D-314, D-374.)

### nm-jeito-pb — Os nomes da lista "Jeito do preto e branco"

**Do que se trata.** Numa página em Preto e branco: painel "Filtro da página" (à direita) > "Mais ajustes"
> lista "Jeito do preto e branco". Cada item é uma maneira de o programa decidir o que vira preto e o que
vira branco.

**O que acontece hoje.** Os 4 primeiros itens se chamam "Automático", "Sauvola (padrão)", "Otsu (letra
grossa/gótica)" e "Wolf (scan de baixo contraste)". Sauvola, Otsu e Wolf são sobrenomes de quem inventou
cada conta: não dizem para que servem.

**Sua dúvida:** "Certo, mas o que eu estou escolhendo aqui?" → Só as palavras escritas nesses 4 itens. O
que cada item faz com a página não muda. O print 2 mostra a lista aberta hoje e como ficaria em cada opção
(simulação). A troca vale nos três lugares onde a lista aparece: painel Filtro, Automático ("Limpar a
folha") e "Filtros em tela cheia". Os dez "do ScanTailor" ficam como estão (você mandou assim em 21/10).

**Situação:** só pergunta; entra com a arrumação nova do layout (04/11).

**O que você escolhe:**
- **Opção 1, pelo uso:** "o programa escolhe" · "letra fina" · "letra grossa ou gótica" · "scan apagado".
- **Opção 2:** só tirar o "(padrão)" do Sauvola.
- **Deixar como está.**
- **Escrever no comentário os nomes que você quiser.**
- **Só comentário.**
Sugestão: opção 1 (o Kaique escolhe pelo tipo de letra que está vendo).

Prints: `nm-jeito-pb/jeito-0-resumo.png`, `jeito-1-onde-fica.png`, `jeito-2-os-nomes.png`. (Para consulta:
D-374.)

### nm-tela-livros — Tela dos livros: três coisas com dois nomes

**Do que se trata.** A primeira tela do programa ("Seus livros", um cartão por livro).

**Sua dúvida:** "tem nomes diferentes e fazem a mesma cosia?" → Sim. São três coisas, cada uma com dois
nomes, e cada par faz exatamente a mesma coisa (testado na janela):
1. **Tirar o livro da lista.** No menu do cartão (botão direito ou "Mais...") o item se chama "remover da
   lista"; ele abre a janela "Tirar da lista?", com o botão "Tirar da lista". É o mesmo caminho. O PDF não
   é apagado.
2. **Achar o PDF que mudou de pasta.** O botão do cartão diz "procurar de novo"; o menu do mesmo cartão diz
   "procurar o livro". Os dois abrem a mesma janela do Windows. Cuidado: no menu Marcar da área de
   trabalho, "Procurar de novo" é outra coisa (procura as gravuras de novo).
3. **"Livro" ou "projeto".** O programa diz "livro" em tudo, menos na busca ("Nenhum projeto com 'horas' no
   nome.") e no renomear ("Nome deste projeto:").

**Sua dúvida:** "Eu quero pode escolher os nomes" → Sim, quem escolhe é você. Para cada coisa, um nome só
(ou escreva outro no comentário):
- **1:** A "tirar da lista" (o nome que você deu em 29/09) · B "remover da lista" · C "tirar desta tela".
- **2:** A "procurar o livro" · B "procurar de novo" · C "achar o PDF".
- **3:** A "livro" também na busca e no renomear · B deixar "projeto" nesses dois lugares.

**Situação:** só pergunta; entra com a arrumação nova do layout (04/11). O que os botões fazem não muda.

**O que você escolhe:** uma letra para cada coisa (ex.: "1A 2A 3A"), ou os nomes que você quiser, ou **Só
comentário**. Sugestão: 1A, 2A, 3A.

Prints: `nm-tela-livros/livros-0-resumo.png`, `livros-1-tirar-da-lista.png`, `livros-2-procurar-o-livro.png`,
`livros-3-procurar-de-novo-do-marcar.png`, `livros-4-livro-ou-projeto.png`. (Para consulta: D-335, D-374.)

### nm-antes-de-processar — Os nomes dos botões da janela "Antes de processar"

**Do que se trata.** A janela "Antes de processar", que abre quando você clica "Confirmar e processar" e
ainda há páginas com aviso.

**O que acontece hoje.** Os botões são "Selecionar todas", "Nenhuma", "está bom nas marcadas", "ver" e
"continuar assim mesmo".

**Sua dúvida:** "Quero mais opções, até agora eu gostei mais da segunda opção." → Três opções novas, na
mesma linha da segunda: só os dois botões de baixo, à direita, mudam; os outros três ficam. Cada uma está
num print (simulação):
- **Segunda (a de antes):** "ir para a página" · "processar com os avisos".
- **Nova A:** "ver a página" · "processar mesmo assim".
- **Nova B:** "abrir esta página" · "processar sem olhar".
- **Nova C:** "conferir a página" · "processar agora".
O que cada botão faz não muda.

**De onde veio:** a janela é sua (08/10; menor em 21-22/10). Em 22/10 você escreveu: "os nomes dos botões
são horriveis". **Situação:** só pergunta; entra com a arrumação nova do layout (04/11).

**O que você escolhe:** um dos quatro pares, ou misturar (ex.: o botão de cima de uma e o de baixo de
outra), ou escrever outro nome; ou **Só comentário**. Sugestão: a segunda ("ir para a página" ·
"processar com os avisos"): diz para onde cada botão leva.

Prints: `nm-antes-de-processar/antes-0-resumo.png`, `antes-1-hoje.png`, `antes-2-segunda.png`,
`antes-3-nova-1.png`, `antes-4-nova-2.png`, `antes-5-nova-3.png`. (Para consulta: D-274, D-283, D-374.)

---

### Conferência contra a lista do §11.13 (feita item a item)

| item | 1 o que é/onde | 2 sem código | 3 print modelo | 4 caso real conferido | 5 caminho/defeito ou escolha | 6 o que escolhe + só comentário + sugestão | 7 curto, responde a frase | 8 controle/onde aparece | 9 origem | 10 situação |
|---|---|---|---|---|---|---|---|---|---|---|
| au-d-501 | sim | sim | sim | sim | sim | sim | sim | sim (Dividir a um clique) | sim | sim |
| au-d-500 | sim | sim | sim | sim | sim (proteção contra erro) | sim | sim | sim (arrastar a linha) | sim | sim (já respondido 27/10) |
| au-d-489 | sim | sim | sim | sim | sim | sim | sim | sim | sim | sim |
| au-d-541 | sim | sim | sim | sim | sim | sim | sim | sim (Ctrl+Z) | sim | sim |
| au-d-487 | sim | sim | sim | sim | sim (remendos) | sim | sim (3 dúvidas, na ordem) | sim | sim | sim |
| au-d-484 | sim | sim | sim | sim | sim | sim | sim | sim (3 jeitos de rodar) | — (pedido dele) | sim |
| au-d-492 | sim | sim | sim | sim | sim | sim | sim | sim (onde aparece) | sim | sim |
| nm-folha-pagina | sim | sim | sim | sim | sim | sim | sim | sim (só palavras) | sim | sim |
| nm-jeito-pb | sim | sim | sim | sim | sim | sim | sim | sim (3 lugares) | sim | sim |
| nm-tela-livros | sim | sim | sim | sim | sim | sim | sim | sim | sim | sim |
| nm-antes-de-processar | sim | sim | sim | sim | sim | sim | sim | sim | sim | sim |
