# Resultados-alvo R1 a R9: o que o Samuel quer ver no livro, e quanto já se chegou

Montado em 20/10/2026 pelo ajudante C da memória (pedido do Samuel de 19/10/2026, CLAUDE.md §4.9). "Hoje" = 20/10/2026; programa de referência: ramo `fase-1` em `b8e9af7`.

## Como ler

- **R1 a R9** são os nove resultados que o Samuel quer ver num livro restaurado. A tabela oficial está no [ESTADO-ATUAL, §2](../docs/plano/ESTADO-ATUAL.md) ("O resultado que o Samuel quer (fonte: "Vamos recapitular...", 12/09/2026)").
- **O plano manda.** Os itens que fazem cada resultado estão no [PLANO-DEFINITIVO](../docs/plano/PLANO-DEFINITIVO.md); quando este arquivo e o plano discordarem, vale o plano e a entrada mais nova do Registro de mudanças.
- Cada seção traz: a frase do resultado e a frase literal do Samuel de onde ele veio; as páginas de exemplo (as originais e as que valem desde 25/09/2026); os itens do plano; as páginas de teste; e **quanto já foi atingido** (o que o Samuel aprovou, com as palavras dele; o que está pronto em ramo; o que falta; o que se sabe que não dá).
- "Aprovado" aqui é só o que o Samuel marcou ou disse ("BOM", "Aprovado", "Está bom", `[x]`). Opinião de verificador é "pronto para conferir", nunca aprovado (CLAUDE.md §4.3).

## De onde vieram os nove resultados

**O documento.** Em 12-13/09/2026 o Samuel mandou o documento "Vamos recapitular o que o Editor de Impressão precisa fazer para restaurar um livro" ([histórico, PARTE -3, "O replanejamento"](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md), linha 2448): "recapitulando os requisitos originais e mostrando, livro a livro, o resultado que quer (usando imagens geradas por IA generativa **só como referência visual** de comparação — nunca para o programa em si, que continua proibido de gerar pixel, regra inalterada)".

- O histórico **não copia** as frases do documento; só o descreve. As frases literais abaixo foram lidas do próprio documento (só o texto do `.docx`, sem as imagens), que fica **fora do git**: `D:\programas\EditorImpressao-arquivos\explicacoes-do-samuel\Vamos recapitular o que o Editor de Impressão precisa fazer para restaurar um livro.docx` (e `.pdf`; cópia também em `D:\programas\EditorImpressao-arquivos\Contexto para Claude (24-09-2026)\03 - Documentos do Samuel e do Kaique\`). Os arquivos têm data de 11/09/2026 (21:21 o `.docx`, 22:05 o `.pdf`); o ESTADO-ATUAL dá 12/09/2026, o dia em que a sessão o recebeu.
- O começo do documento, literal: "Para isso precisamos de: Um ocr que detecte as palavras / Um selecionador de gravuras / Um selecionador que detecte letras e trabalhe junto com ocr / Um selecionador de cores. / Criador de margem branca ( borda) centralizando o texto / Alinhar textos horizontalmente girando as paginas em alguns graus / Pode aplicar filtro só em uma parte do texto. / Essas ferramentas vão servir para criar mascaras, como usamos no photoshop para selecionar gravuras e letras e deixar as paginas em branco, mas manter as gravuras e letras intactas."
- E o pedido de lembrar o resto: "OS: essa lista do que precisamos não está completa, tem coisas que já havia mencionado e falado durante a criação do programa e provavelmente estão na conversa e que não coloquei na lista [...] Por favor, me ajude a relembrar todas essas elas individualmente." (os pedidos antigos estão em [pedidos.md](pedidos.md)).
- **R9** não vem desse documento: vem do "TESTE 1" do Boécio, de 16/09/2026 (fora do git, `D:\programas\EditorImpressao-arquivos\explicacoes-do-samuel\TESTE BOÉCIO 1 -- 16-09-2026\TESTE 1.docx`).

**As páginas que valem desde 25/09/2026.** Os números do documento não batiam com as páginas dos prints. No Registro de mudanças, 25/09/2026: "Gabarito: páginas escolhidas conferindo com os prints do "Vamos recapitular": Palatino 67 (o print marcado "76"), Siebmacher 9 (o marcado "7"), Marial 7 (no lugar da 862) [...] Escola = p. 35 do PDF ("37" impresso). O ESTADO-ATUAL guarda a tabela original e ganhou uma linha com as páginas que valem." A lista completa, por item, está em [`gabarito/lista.json`](../gabarito/lista.json) (campos `para_que` de cada página e `itens`; explicação em [`gabarito/LEIA-ME.md`](../gabarito/LEIA-ME.md)). A numeração é a **página no PDF**, começando em 1.

## O resultado-alvo do plano (§2) e o critério final

Antes de R1 a R9, o plano diz qual é a régua de tudo ([plano, §2](../docs/plano/PLANO-DEFINITIVO.md), aprovado em 24/09/2026):

- "**O Mágico Pro do CamScanner, que o Kaique usa hoje.** Nas palavras do Kaique: "removeu o amarelado do fundo, manteve apenas as letras e imagens preservando suas cores originais, e alinhou a página que estava inclinada"". A frase do Kaique só foi achada no plano e no handoff de 25/09 (`D:\programas\EditorImpressao-arquivos\plano-24-09-2026\HANDOFF-EDITOR-DE-IMPRESSAO-25-09-2026.md`, fora do git); a fonte original (áudio ou mensagem dele) não foi achada (procurei no histórico, no repositório e na pasta do plano).
- **Critério do Samuel** ([CLAUDE.md §1](../CLAUDE.md); pedido 22, 01/08/2026 18:06): "Eu quero que o papel saia branco, e o desenho também saia perfeito." (no pedido literal: "eu quero que o papel saia branco, e o desenho também saia perfeito.").
- **Fotos do CamScanner de 24/09** (plano §2: "As fotos do CamScanner enviadas pelo Samuel em 24/09 (calendário Novembre/Decembre e "Na escola de Jesus" p. 37) são gabarito de comparação"). Registro 25/09/2026: "O calendário é do **Livro de Horas de Luís XIV, páginas 26 (NOVEMBRE) e 27 (DECEMBRE)**; a outra é a página 37 da "Na escola de Jesus"" (= página 35 do PDF). Estão em `gabarito/camscanner/` (fora do git). Item do plano: [6.7](itens/6.7.md) ("Comparação final com o CamScanner: o programa já substitui?"); páginas no `lista.json`, item `6.7`: `horas_p026`, `horas_p027`, `escola_p035`. Página de teste com ficha: [escola-035](paginas-de-teste/escola-035.md).
- **Quanto já foi atingido:** a comparação final (6.7) **não foi feita**; é a pergunta aberta desde 18/07/2026 ("o programa já substitui o CamScanner para o trabalho do Kaique? Sim, não, ou ainda não.", histórico, PARTE 5 §6). Partes das páginas do CamScanner já foram aprovadas pelo Samuel:
  - 30/09/2026 (`relatorios/conferencia-samuel-2026-09-30.md`): "B1 Escola 35 - o corte das bordas: BOM"; "B3 Escola 35 - roupa e céu do anjo: BOM"; "G2 Horas 26 - moldura dourada: BOM".
  - 01/10/2026 (conferência 5, `relatorios/conferencia-samuel-2026-10-01.md`): "F2 Escola 35: o anjo: BOM"; "MP2 Horas 26: o dourado da moldura: BOM"; mas "M2 Horas 26: a moldura: RUIM - As letras ainda estão saindo com alguns pedaços cinzas dentro delas" e "M3 Horas 27: a moldura: RUIM - Temos uma falha no canto superior esquerdo da imagem".
  - 02/10/2026 (conferência 6, `relatorios/conferencia-samuel-2026-10-02.md`): "M2 Horas 26: 'NOVEMBRE.' e a coluna de letrinhas: BOM"; "M3 Horas 27: a barra de cima da moldura, perto do canto esquerdo: BOM"; "N3 Escola 35 no Preto e branco: BOM"; "N4 Escola 35 no Mágico pro: BOM".
  - Ainda aberto: o título "NOVEMBRE." da Horas 26 tomado por gravura vai para o [1.5](itens/1.5.md) (decisão de 30/09/2026).

---

## R1 — Papel branco, letras e gravura intactas (nada de amarelado)

**Frase do resultado** (ESTADO-ATUAL §2): "Papel branco, **letras e gravura intactas** (nada de amarelado)".

**De onde veio** ("Vamos recapitular", Livro 1, Palatino), literal:
- "Pagina 5 [...] Você pode ver que a página está amarelada, precisamos deixar a pagina branca, mantendo a gravura e as letras intactas."
- "Pagina 7 – Nesta pagina podemos ver que a folha está amarela, queremos deixar a folha branca e manter as letras intactas, deixar elas exatamente como estão."
- "Pagina 9 [...] queremos manter a gravura e as letras inalteradas e deixar somente o papel branco, não pode ficar nenhum resquício de amarelado." e: "Pagina 9 feita com IA esse é o resultado aproximado que eu quero que o programa chegue, pois a IA do gemini é generativa, então como pode ver ela mudou o desenho da pagina, criou um novo, e eu não quero que isso aconteça."

**Páginas.** Originais: Palatino p. 5, 7 e 9. Valem (iguais): `palatino_p005`, `palatino_p007`, `palatino_p009` (`lista.json`, item `fase1`; `para_que`: "R1: papel branco, letras e gravura (retrato) intactas"; "R1: papel branco, letras intactas; tem mancha de outra página"; "R1: papel branco, letras e gravura intactas; borda preta em volta do texto"). Páginas obrigatórias da Fase 1 desde 28/09/2026: Palatino 5, Escola 35, Horas 11, 13, 26, 27 e Opus Majus 20 (plano, Fase 1).

**Itens do plano:** [1.1](itens/1.1.md), [1.2](itens/1.2.md), [1.3](itens/1.3.md), [1.4](itens/1.4.md), [1.5](itens/1.5.md), [1.6](itens/1.6.md); [2.8](itens/2.8.md) (tipos de preto e branco); regras do resultado da Fase 1 (Samuel, 28/09/2026: "Gravura e letras intactas, e todo o papel totalmente branco, inclusive o papel dentro da gravura (ex.: o fundo do retrato do Palatino 5)").

**Páginas de teste:** [palatino-005](paginas-de-teste/palatino-005.md), [escola-035](paginas-de-teste/escola-035.md), [opusmajus-020](paginas-de-teste/opusmajus-020.md). Palatino 7 e 9 ainda sem ficha. Livro: [palatino](livros/palatino.md).

**Quanto já foi atingido: aprovado em parte.**
- **Aprovado pelo Samuel:**
  - Itens 1.1, 1.2 e 1.3, em 02/10/2026 (`relatorios/decisoes-samuel-2026-10-02.md`): "M1 Item 1.1: "Tirar o fundo" (PDF que já vem com camadas): [x] Aprovado"; "M2 Item 1.2: detector de gravura do ScanTailor: [x] Aprovado"; "M3 Item 1.3: os OCRs (só achar onde há texto): [x] Aprovado".
  - 30/09/2026 (`relatorios/conferencia-samuel-2026-09-30.md`): "B2 Palatino 5 - fundo do retrato e barba: BOM".
  - 02/10/2026 (conferência 6): "N1 Palatino 5 no Preto e branco: BOM"; "N2 Palatino 5 no Mágico pro: BOM".
- **Pronto em ramo:** os dez jeitos de preto e branco do ScanTailor (2.8) começaram em 20/10/2026 no ramo `fase2-scantailor-itens-2026-10-19` (em andamento, `relatorios/fase2-itens/ONDE-PAREI.md` no ramo).
- **Falta:**
  - [1.4](itens/1.4.md) máscara de tinta com a cor original e [1.5](itens/1.5.md) juntar os detectores ("papel branco, letra com a cor original, gravura intacta, página endireitada", plano).
  - Papel ainda cinza-claro dentro de gravura pequena de traço (caixa "PAVLVS PAPA III" do Palatino 7; Lista de bugs de 28/09, vai para o 1.5).
  - No "Tirar o fundo", "o Palatino 5 fica intacto e amarelo (regra do 1.1 certa, regra da Fase 1 não: fica para o 1.5)" (Registro 29/09/2026).
  - Lista de espera 30/09/2026, "Melhorar o contorno das letras" (Palatino 67): "quero poder melhorar o contorno das letras, mas isso seria uma nova funcionalidade".
- **Não possível:** nada declarado para estas páginas.

## R2 — Sumir com a mancha do verso

**Frase do resultado:** "**Sumir com a mancha do verso** (texto da folha de trás)".

**De onde veio** ("Vamos recapitular"), literal:
- "Pagina 10 Aqui nós temos uma folha só com letras, mas podemos ver atrás das letras a sombra da folha de trás atrapalhando a leitura. Queremos deixar a folha branca e as letras pretas, e conteúdo que está atras, temos que fazer ele sumir."
- Livro 4 (o Marial; o documento não diz o nome), página 7: "Vemos que a pagina de trás da pagina 7 está aparecendo as letras e por isso o programa pode se confundir ao selecionar as letras pretas realmente escritas na pagina 7."
- É também o caso 4 do Kaique no pedido 14 (18/07/2026): "a folha é tão antiga que ela já está quase transparente, então as letras da parte de trás acabam aparecendo. Esses filtros no scanner, ele remove." ([pedidos.md](pedidos.md), pedido 14).

**Páginas.** Originais: Palatino p. 10 e Marial p. 862. Valem: `palatino_p010` e `marial_p007` (`lista.json`, item `6.1`). A 862 "veio de uma lista de 18/07" (ESTADO-ATUAL §2); trocada pela 7 em 25/09/2026.

**Itens do plano:** [6.1](itens/6.1.md) ("Mancha do verso (subtrair usando a frente e o verso da mesma folha)").

**Páginas de teste:** [marial-007](paginas-de-teste/marial-007.md), [boecio-022](paginas-de-teste/boecio-022.md) (escrita do verso na margem, usada na conferência 8). Palatino 10 sem ficha. Livros: [palatino](livros/palatino.md), [marial](livros/marial.md).

**Quanto já foi atingido: nada aprovado.**
- **O que o Samuel disse:**
  - 30/09/2026, sobre a faixa cinza ao lado da moldura do Palatino 10 no "Tirar o fundo": "F4 Palatino 10 - ao lado da moldura: NÃO SEI - Na do meio em preto e branco, é aceitavel. Na ultima se puder tirar esse cinza, é melhor, mas não seria um grande problema."
  - 05/10/2026, conferência 8 do modo Misto (`relatorios/conferencia-samuel-2026-10-05-f.md`): "M7 Marial 7: a margem direita e as beiradas: Nenhuma - o original ainda fica melhor para ler. Nesta folha o original continua guanhando, mas acredito que é porque tem um teto que o programa consegue atingir, gostaria de continuar proceguindo com testes para melhorar, mas não quero ficar preso nisso." A mesma frase vale para "B22 Boécio 22: a escrita do verso na margem direita".
- **Pronto em ramo:** nada.
- **Falta:** todo o 6.1 (Fase 6). "A mancha do verso é o defeito mais grave aberto. O Preto e branco não a remove — ele a escurece" (CLAUDE.md §9). Solução recomendada lá: "o acervo tem as duas faces da mesma folha; espelhar o verso, alinhar sobre a frente e subtrair." As letras raspadas do Graduale 221 "têm o tom da mancha do verso: depende do 6.1" (Lista de bugs, 30/09).
- **Não possível:** nada declarado. O Samuel falou em "um teto que o programa consegue atingir" (05/10/2026), sem descartar.

## R3 — Margens iguais em todas as folhas, pensando na costura

**Frase do resultado:** "**Margens iguais em todas as folhas** / centralizar o texto, pensando na costura. Esquerda e direita diferentes".

**De onde veio** ("Vamos recapitular"), literal:
- "Pagina 57 Aqui vemos uma página que está descentralizada as coisa estão mais a esquerda, nós queremos poder escolher o tamanho da margem a partir do que está escrito ou a partir da espécie de quadro que alguns livros tem como esse tem [...] precisamos que todas as folhas tenham o mesmo tamanho de margem em branco, para que quando o livro seja encadernado, a costura não fique em cima das primeiras letras. [...] temos que ter um jeito eficiente de deixar todas as folhas iguais( no casso a centralização do texto)."
- Graduale: "Pagina 222 Queremos aumentar o tamanho da margem do lado direito da olha" e "Pagina 223 [...] ela está precisando de mais margem do lado esquerdo, então o programa tem que conseguir perceber quando aumentar margem do lado direito e do lado esquerdo."
- Horas: "Pagina 14 Aqui nós precisamos centralizar, a margem está muito a esquerda." (e na p. 13: "centralizar no meio da folha").

**Páginas.** Originais: Palatino p. 57, Graduale p. 222-223, Horas p. 14. Valem (iguais): `palatino_p057`, `graduale_p222`, `graduale_p223`, `horas_p014` (`lista.json`, item `2.4`).

**Itens do plano:** [2.4](itens/2.4.md) (margens iguais + alinhamento), [2.5](itens/2.5.md) (caixa da página e guias), [2.13](itens/2.13.md) (página dentro da borda preta), [2.6](itens/2.6.md) (tamanho final e impressão); "Aba Bordas e margens", a aperfeiçoar na Fase 2.

**Páginas de teste:** nenhuma das quatro tem ficha ainda. Ligadas ao corte da borda preta: [cursus-003](paginas-de-teste/cursus-003.md), [matematica-032](paginas-de-teste/matematica-032.md), [antiphon-260](paginas-de-teste/antiphon-260.md), [antiphon-088](paginas-de-teste/antiphon-088.md), [camoes-104](paginas-de-teste/camoes-104.md), [pesel-021](paginas-de-teste/pesel-021.md), [escola-197](paginas-de-teste/escola-197.md). Livros: [palatino](livros/palatino.md), [graduale](livros/graduale.md), [horas](livros/horas.md).

**Quanto já foi atingido: em parte** (o corte foi aprovado; as margens ainda não existem).
- **Aprovado pelo Samuel:**
  - Corte com 1 mm de papel depois da última letra. 01/10/2026 (conferência 5, P2): "Sim, 1 mm (o corte das 32 páginas muda um pouco)". 02/10/2026 (conferência 6): "C1 Escola 7 ('CRISTÃ'): a folga depois da última letra: BOM"; "C2 Escola 35: a folga dos lados: BOM"; "C3 Palatino 67: a moldura de fios: BOM"; "C4 Rhetorica 73: o fio da direita: BOM".
- **Decidido (ainda não construído):**
  - 05/10/2026 (conferência 9, `relatorios/conferencia-samuel-2026-10-05-g.md`): "G9 Margens de fábrica: (a) As do ScanTailor (10 mm dos lados, 5 mm em cima e embaixo) - Mas eu vou conseguir alterar isso né?"; "G9b Todas as páginas do tamanho da maior: Sim"; G10 (b), "Avisar e não reduzir" (ver R7).
  - 13/10/2026 (página de escolhas; Registro 13/10/2026): `g8-guias` "As duas" ("Mas ele vai poder tirar a automatica a hora que ele quiser."); `g8-moldura-tinta-fora` "Só avisa" ("ele avisa e da opção e de mudar o corte e mostrar ele alargado com o que foi tirado."); `g9-pagina-muito-maior` "O programa deixa essa folha de fora sozinho, e avisa".
  - **Mudança de 14/10/2026:** a margem saiu da edição e foi para a hora de imprimir. Literal (`relatorios/conferencia-samuel-2026-10-14/explicacao-da-impressao.md`): "1. Na edição Cada página ocupa a folha inteira. Aqui eu só me preocupo em deixar legível, a folha branca, os desenhos certos, endireitar. Não penso em tamanho final, formato nem margem." e "Margens (só nesta fase, por causa da encadernação clássica): - Contadas na página A5, não na folha A4 inteira. - Mínimo de 1 cm em cada um dos quatro lados [...] - O lado de dentro (costura) também é 1 cm: página par → direita, página ímpar → esquerda." Isso responde à "costura" do R3, agora no [2.6](itens/2.6.md). Leitura deste ajudante, a confirmar pelo Samuel: as margens G9 (10 e 5 mm) do 2.4 continuam valendo para a página na tela, e as margens de 1 cm valem para o arquivo de impressão; o plano não diz como as duas se juntam.
- **Pronto em ramo:**
  - `fase2-caixa-conteudo`: a conta original do ScanTailor que acha a página e a caixa do conteúdo (base de 2.5 e 2.13). PRONTO PARA CONFERIR por máquina, **não ligada a nada** (Registro 13/10/2026). Ligar o corte só depois da resposta da `g7-borda-ate-onde` (Registro 19/10/2026).
  - `conserto-corte-g6-2026-10-13`: o conserto da faixa preta que o G6 trouxe; Samuel em 13/10/2026: "Melhorar"; acerto do Pesel 21 **em andamento em 20/10/2026** (`relatorios/conserto-corte-g6/ONDE-PAREI.md` no ramo).
- **Falta:** construir 2.4, 2.5, 2.6 e 2.13. Perguntas abertas em 19/10/2026: `g7-borda-ate-onde` e `g9-folha-maior-impressao` (Registro 19/10/2026).
- **Não possível:** nada declarado. Atenção (Lista de bugs, 28/09 e 01/10): o número da folha "Cvii" do Graduale 221 e 223 "já vem cortado no próprio escaneamento".

## R4 — Tirar manchas sem mexer no título

**Frase do resultado:** "Tirar manchas (vermelhas, marrons) **sem mexer no título**".

**De onde veio** ("Vamos recapitular"), literal:
- "Pagina 66 Nessa pagina vemos manchas vermelhas além do papel ser amarelado, queremos poder remover a mancha sem mexer no titulo."
- "Pagina 76 Mesmo problema da anterior, marquei as manchas no papel amarelado com laranja(circulei a mancha)"
- Livro 4 (Marial), página 7: "vemos também uma mancha amarronzada na parte de baixo do livro do lado direito que sobe até quase em cima do livro."

**Páginas.** Originais: Palatino p. 66 e 76. Valem: `palatino_p066` e `palatino_p067` (`lista.json`, item `6.2`): "o print marcado "76" do Palatino é a página 67 do PDF" (ESTADO-ATUAL §2; Registro 25/09/2026).

**Itens do plano:** [6.2](itens/6.2.md) ("Manchas vermelhas e marrons sem mexer no título (Palatino 66, 76)"); Lista de espera 05/10/2026 ("Tirar as manchas que o detector toma por gravura", Marial 7, → [2.18](itens/2.18.md)).

**Páginas de teste:** [marial-007](paginas-de-teste/marial-007.md). Palatino 66 e 67 ainda sem ficha. Livros: [palatino](livros/palatino.md), [marial](livros/marial.md), [pesel](livros/pesel.md).

**Quanto já foi atingido: nada aprovado** (o título é preservado; as manchas, não).
- **O que o Samuel disse:**
  - 30/09/2026 (`relatorios/conferencia-samuel-2026-09-30.md`), sobre o título no "Tirar o fundo": "F3 Palatino 66 - o título: NÃO SEI - sai quase, cheio, ainda não está perfeito, mas está no caminho."
  - Sobre o Palatino 67: "G3 Palatino 67 - caixa cinza: BOM - Mas o resultado ainda não saiu do jeito que eu quero, quero pode melhorar o contorno das letras, mas isso seria uma nova funcionalidade, e o resultado está aceitavel."
  - Sobre o Marial 7, conferência 10 (05/10/2026, Registro 05/10/2026): "Temos que ter uma opção para retirar essas manchas".
- **Pronto em ramo:** nada específico de mancha.
- **Feito, a conferir:** no Preto e branco, a mancha cor de ferrugem do Palatino 66 deixou de virar borrão preto (consertado em 01/10/2026, `5953b0a`; Lista de bugs, 01/10).
- **Falta:** o 6.2 inteiro (Fase 6). A ferrugem rosada da Pesel 2 espera decisão: "Pela regra R4 talvez o certo seja a mancha sumir, não mudar de cor: decisão do Samuel" (Lista de bugs, 29/09).
- **Não possível:** nada declarado.

## R5 — Endireitar linhas tortas

**Frase do resultado:** "Endireitar linhas tortas".

**De onde veio** ("Vamos recapitular"), literal:
- "Pagina 221 Aqui temos uma partitura de canto gregoriano, queremos manter as linhas vermelhas, os neumas e endireitar a o conteúdo, pois a partitura está torta."
- Escola, "Pagina: 7 Aqui nós temos linhas tortas, precisamos endireitar a folha e dar mais margem na esquerda".
- Boécio: "Pagina 8 refeita com IA [...] vai ver que essa as linhas estão retas, e a folha está totalmente branca."

**Páginas.** Originais: Graduale p. 221, Escola de Jesus p. 7. Valem (iguais): `graduale_p221`, `escola_p007` (`lista.json`, item `2.2`).

**Itens do plano:** [2.2](itens/2.2.md) (endireitar do ScanTailor; G6 endireitar antes de cortar), [2.3](itens/2.3.md) (girar), [2.12](itens/2.12.md) (desentortar página curva perto da lombada).

**Páginas de teste:** [graduale-221](paginas-de-teste/graduale-221.md). Escola 7 ainda sem ficha. Livros: [graduale](livros/graduale.md), [escola](livros/escola.md).

**Quanto já foi atingido: aprovado em parte.**
- **Aprovado pelo Samuel:**
  - G6 em 12/10/2026 (`relatorios/conferencia-samuel-2026-10-12.md`): trabalho inteiro "**Aprovado**" ("Pode entrar no programa."), 13 quadros "Está bom", entre eles "Graduale 221 (`g6-graduale221`) | Está bom", "Graduale 222", "Escola de Jesus 7", "Escola de Jesus 35" e "Boécio 8". Juntado ao `fase-1` em 12/10/2026 (`4a7f288`).
  - Antes, 05/10/2026 (conferência 9, Registro 05/10/2026), sobre usar o do ScanTailor: "ajeitar não é criar outro, até porque em todos os testes ele se saiu melhor que o nosso".
  - O endireitar do ScanTailor (G4, C1, G5) foi juntado em 08/10/2026 "com o ok do Samuel para atualizar o programa"; **o 2.2 não está marcado `[x]`** no plano ("cada item continua a conferir", Registro 08/10/2026).
- **Pronto em ramo:** conserto do corte que o G6 piorou, `conserto-corte-g6-2026-10-13` (ver R3).
- **Falta:**
  - Consertar depois: "moldura e título colados na borda de cima (Siebmacher 9, Escola 7) e cunhas brancas quando o corte vai até a beirada da folha (Boécio 8, Marial 7, Graduale 221)" (Registro 12/10/2026).
  - Os três controles do retângulo ("Fica no mesmo lugar" / "Acompanha o texto") nas Configurações, no livro e na página ainda não existem na tela (Registro 12/10/2026).
  - [2.12](itens/2.12.md) desentortar página curva: não começado (ramo `fase2-scantailor-itens-2026-10-19`, 20/10/2026).
  - Aviso "as contas discordam" em página reta, com só 0,2° de diferença (Lista de bugs, 09/10); "Consertar exige escolha do Samuel".
- **Não possível:** nada declarado.

## R6 — Manter cores de verdade (rubricação, iluminura, borda dourada)

**Frase do resultado:** "Manter cores de verdade (rubricação, iluminura, borda prata)". O documento diz "borda prata"; o `lista.json` corrige: "a borda dourada (o documento chama de 'borda prata')".

**De onde veio** ("Vamos recapitular", Livro de Horas e Graduale), literal:
- "Pagina 11 Vemos que eu marquei a as letras bem no meio da gravura, risquei em volta em roxo. Queremos conseguir manter as letras em suas cores originais e deixar o papel branco e manter a gravura intacta, além de conseguir colocar mais margem ou até tirar margem."
- "Pagina 13 Aqui nós gostaríamos de manter o texto e suas cores e também a borda prata, mas centralizar no meio da folha, e deixar a folha toda branca, sem que se perca nenhum conteúdo das letras e nem cor."
- "Pagina 47 Aqui nós temos gravura e texto, precisamos conseguir deixar branco o que não é nem gravura e nem texto, no caso a folha de papel. [...] Não podemos perder qualidade de imagem ao aplicar essas mudanças."
- Graduale p. 221: "queremos manter as linhas vermelhas, os neumas".

**Páginas.** Originais: Horas p. 11, 13 e 47; Graduale p. 221. Valem (iguais): `graduale_p221`, `horas_p011`, `horas_p013`, `horas_p047` (`lista.json`, item `6.3`).

**Itens do plano:** [1.2](itens/1.2.md), [1.4](itens/1.4.md), [1.5](itens/1.5.md), [6.3](itens/6.3.md) ("Tinta vermelha não virar preto (Graduale, Horas)"), [6.6](itens/6.6.md) (chapas vermelho/preto); regras do resultado da Fase 1 (iluminura intacta; moldura dourada mantida; regra do Preto e branco de 30/09/2026 e emendas).

**Páginas de teste:** [horas-047](paginas-de-teste/horas-047.md), [graduale-221](paginas-de-teste/graduale-221.md), [antiphon-260](paginas-de-teste/antiphon-260.md) (iluminura chapada no "Só as letras", Lista de bugs 13/10). Horas 11 e 13 ainda sem ficha. Livros: [horas](livros/horas.md), [graduale](livros/graduale.md).

**Quanto já foi atingido: aprovado em parte.**
- **Aprovado pelo Samuel:**
  - 30/09/2026 (conferência 2, `relatorios/conferencia-samuel-2026-09-30-b.md`): "V1 No Preto e branco, o que é vermelho (títulos, rubrica) sai preto?: BOM".
  - 01/10/2026 (conferência 5): "V1 Horas 13: 'TABLE' e 'CONTENU EN CE LIVRE.': BOM"; "V3 Graduale 223: as palavras vermelhas: BOM"; "I1 Horas 11: a iluminura: BOM"; "G1 Graduale 222: a pauta e as notas: BOM"; "MP1 Horas 13: o dourado da moldura: BOM"; "MP3 Horas 47: a faixa cinza embaixo de 'pitié de nous': BOM"; "MP4 Horas 11: a iluminura: BOM"; "P1 No Preto e branco, a iluminura também mantém a cor original?: Sim, mantém a cor".
  - 02/10/2026 (conferência 6): "A2 Horas 11: o miolo das letras douradas agora branco: BOM"; "P4 Horas 11: o título dentro do oval: BOM"; "M1 Horas 13: a barra de baixo da moldura, perto de 'pag. 54': BOM".
- **Recusado pelo Samuel:** Horas 47 no Preto e branco. 02/10/2026: "A1 Horas 47: os dois 'JESUS' e o 'C' de 'C'est' agora inteiros: RUIM - Ainda está apagando as letras, o original está muito melhor para ler". 05/10/2026 (`relatorios/conferencia-samuel-2026-10-05.md`): "A1 Horas 47 no Preto e branco: as letras da página inteira: RUIM - ainda pode melhorar, mas está quase perfeito." e "A1b [...] RUIM - Nenhuma está grossa demais, mas continuam apresentando falhas, pixels apagados no meio das letras." Está na Lista de bugs (05/10). Também (Lista de bugs, 05/10): "Conferência 8, H13: letras cortadas no Preto e branco".
- **Pronto em ramo:** os jeitos de preto e branco do ScanTailor (2.8, em andamento; ver R1).
- **Falta:** [1.4](itens/1.4.md) (tinta com a cor original; Samuel na rodada 4 do "Para revisar", 08/10/2026: "mas temos que melhorar o reconhecimento de tintas, para não sair falhado assim, não precisar usar sempre o reforço."); [1.5](itens/1.5.md); o botão de manter ou tirar a moldura; "Marcar como" com "iluminura ou pintura" e "moldura" (Lista de espera 12/10/2026); [6.3](itens/6.3.md) e [6.6](itens/6.6.md).
- **Atenção, duas decisões que parecem se cruzar:** o item 6.3 diz "Tinta vermelha não virar preto"; a decisão V1 de 30/09/2026 diz que **no Preto e branco** o vermelho sai preto. Leitura deste ajudante: o V1 vale para o filtro Preto e branco (decisão mais nova); o 6.3 vale para os outros filtros e para as chapas de duas cores (6.6). O plano não diz isso com todas as letras: pergunta para o Samuel.
- **Não possível:** nada declarado.

## R7 — Tamanho final A4, com margem certa para encadernar

**Frase do resultado:** "Tamanho final A4, com margem certa para encadernar".

**De onde veio** ("Vamos recapitular", Siebmacher), literal: "Pagina: 7 Precisamos deixar a folha branca e colocar esse texto e margem numa proporção de folha A4, além de melhorar a margem para um tamanho adequado para encadernação, lembrando que cada pagina vai precisar de adequação diferente por serem lados diferentes (esquerdo e direito) e por nem sempre quando se escaneia uma folha elas saem na mesma direção."

**Páginas.** Original: Siebmacher p. 7. Vale: `siebmacher_p009` (`lista.json`, item `2.6`): "o marcado "7" do Siebmacher é a página 9 do PDF" (ESTADO-ATUAL §2). A `siebmacher_p007` continua no gabarito como página do teste do ScanTailor de 24/09.

**Itens do plano:** [2.6](itens/2.6.md) (tamanho final e a fase de impressão), [2.4](itens/2.4.md), [6.5](itens/6.5.md) (cadernos), [2.19](itens/2.19.md) (cm/mm).

**Páginas de teste:** [siebmacher-009](paginas-de-teste/siebmacher-009.md). Livro: [siebmacher](livros/siebmacher.md). Pesquisa: [referencias/embaralhador.md](referencias/embaralhador.md), [referencias/updf.md](referencias/updf.md).

**Quanto já foi atingido: nada aprovado** (as decisões estão tomadas; nada construído).
- **Decidido pelo Samuel:**
  - 05/10/2026 (conferência 9): "G10 Quando o conteúdo não cabe na folha: (b) Avisar e não reduzir - avisar para eu reduzir manualmente, e ter uma opção para passar isso para todas as folhas [...] Segundo o kaique ele faz encardenações manuais então tu sabe dizer que geralmente as folhas são impressas com 4 paginas cada uma, entendeu? então isso ai não pode interferir nisso."
  - 14/10/2026, a explicação da impressão (literal em `relatorios/conferencia-samuel-2026-10-14/explicacao-da-impressao.md`): "2. Na hora de gerar o arquivo para impressão É só nesta fase que se decide o formato de saída. Eu quero poder escolher: - Livreto na horizontal (A4 deitada com duas páginas A5 lado a lado, embaralhadas na ordem de caderno — imposição), ou - Página inteira A4 na vertical, ou - todas as outras opções que aparecem nos prints do PDF que mandei. Quero TODAS essas opções dentro do programa, para ter bastante escolha." e "Aviso: o programa precisa avisar quando o corte deixar qualquer margem abaixo de 1 cm, porque o livro vai ser encadernado (encadernação clássica) e tem que sobrar espaço nos quatro lados."
  - 14/10/2026 (página de escolhas; Registro 14/10/2026): `g10-papel-ou-pagina` decidida pela explicação; `g10-ajustar-todas` "Cada página até encher a folha" ("Porque essa opção voltou ? eu já não tinha respondido?"); `g11-margem-impressora` "1 cm a partir de onde a impressora imprime (1,3 cm do papel)"; `g12-diminuir-um-lado` "Em todas, e dá para mudar uma folha só".
  - **Isso muda o R7:** o "A4" deixou de ser o tamanho da página na edição; é uma das saídas da impressão (livreto A4 deitada com duas A5, ou A4 em pé).
- **Já no programa (sem aprovação):** a aba Bordas com "tamanho da folha (A4/A5/Carta), moldura e margem branca" (feito de 17 a 23/09, "a aperfeiçoar" na Fase 2, Registro 25/09/2026); a montagem dos cadernos com a conferência da dobra (`core/cadernos.py`).
- **Pronto em ramo:** a pesquisa da fase de impressão, ramo `pesquisa-impressao-2026-10-19`, **no começo** em 20/10/2026 (`docs/pesquisa/ONDE-PAREI-impressao.md` no ramo: achado o embaralhador antigo; falta pesquisar as opções do UPDF).
- **Falta:** construir o 2.6 inteiro. Aberta: `g9-folha-maior-impressao` (como sai impressa a folha muito maior, ex. a tabela do Opus Majus 256; Registro 19/10/2026).
- **Não possível:** nada declarado.

## R8 — Apagar em todas as páginas um texto repetido

**Frase do resultado:** "Apagar em todas as páginas um texto repetido (ex.: endereço de site)".

**De onde veio** ("Vamos recapitular", Escola de Jesus), literal: "Quero conseguir tirar esse endereço de html de todas as paginas do livro." (a frase seguinte do documento termina cortada: "Precisamos").

**Páginas.** Original: Escola de Jesus p. 7. Vale (igual): `escola_p007` (`lista.json`, item `6.4`).

**Itens do plano:** [6.4](itens/6.4.md) ("Apagar texto repetido em todas as páginas (endereço de site, Escola de Jesus 7)").

**Páginas de teste:** [escola-035](paginas-de-teste/escola-035.md) (o pé do endereço do site "vai ser apagado no item 6.4", Lista de bugs, 28/09). Escola 7 ainda sem ficha. Livro: [escola](livros/escola.md).

**Quanto já foi atingido: nada.**
- **Aprovado:** nada.
- **Pronto em ramo:** nada.
- **Falta:** o 6.4 inteiro (Fase 6). Hoje o corte ainda parte pedaços do endereço do site na Escola 35 (Lista de bugs, 28/09 e 01/10), o que deixa de importar quando o 6.4 apagar o endereço.
- **Não possível:** nada declarado.

## R9 — Seleção de letra, gravura e cor que funcione de verdade

**Frase do resultado:** "Seleção de letra / gravura / cor que funcione de verdade".

**De onde veio:** o "TESTE 1" do Boécio, de 16/09/2026 (fora do git), literal:
- "1 - Quando eu for colocar as bordas eu preciso saber quantos cm vai para cada lado, hoje não tem como eu saber."
- "2 - Hoje o marcador não está funcionando corretamente, ele não consegue selecionar exatamente as letras."
- "3- Quando eu tento aumentar o tamanho da margem ele não aumenta para o lado direito, só aumentar para o lado esquerdo"
- "4- Quero conseguir ver a parte de cima do papel Exemplo do canva, de como ele mostra a folha sendo editada. Ele mostra ela inteira e eu posso ver os lados."
- "5- No preto e branco as letras estão perdendo muita qualidade."

E o começo do "Vamos recapitular": "Um selecionador de gravuras / Um selecionador que detecte letras e trabalhe junto com ocr / Um selecionador de cores." e "Eu quero que as ferramentas de seleção ajudem a diferenciar texto de folha e folha de gravura, assim podemos aplicar filtro somente em uma parte do texto ou esbranquiçar somente".

**Páginas.** Original: "TESTE 1 (Boécio)". Valem: `boecio_p003`, `boecio_p007`, `boecio_p008`, `boecio_p022` (`lista.json`, item `fase3`; `para_que`: p. 3 "o marcador não separa direito letra e gravura (item 2 do TESTE 1)"; p. 7 "a margem não aumenta para o lado direito; ver a parte de cima do papel (itens 3 e 4)"; p. 8 "letras perdendo qualidade no preto e branco (item 5)"; p. 22 "quantos cm vão para cada lado da borda (item 1) e marcador que não seleciona exatamente as letras (item 2)").

**Itens do plano:** Fase 3, [3.1](itens/3.1.md) a [3.9](itens/3.9.md) ("Seleção manual no nível do Photoshop"); [1.2](itens/1.2.md), [1.3](itens/1.3.md), [1.5](itens/1.5.md); [2.18](itens/2.18.md) (edição manual das zonas); item 1 do TESTE 1 → aba Bordas ("medidas em cm enquanto arrasta", a aperfeiçoar na Fase 2) e [2.19](itens/2.19.md); item 3 → [2.4](itens/2.4.md); item 4 → [layout](layout.md); item 5 → [2.8](itens/2.8.md).

**Páginas de teste:** [boecio-022](paginas-de-teste/boecio-022.md). Boécio 3, 7 e 8 ainda sem ficha. Livro: [boecio](livros/boecio.md).

**Quanto já foi atingido: aprovado em parte.**
- **Aprovado pelo Samuel:**
  - O detector de gravura do ScanTailor (1.2) e os OCRs que acham o texto (1.3), em 02/10/2026 (ver R1).
  - 30/09/2026 (conferência 2): as opções do detector, "O1 A tela "O que fazer": o grupo "Gravuras e fotos": BOM" a "O5 "Procurar também imagens claras": desmarcada de fábrica?: BOM".
  - 05/10/2026 (conferência 13, `relatorios/conferencia-samuel-2026-10-05-e.md`), o filtro só numa parte: "S1 Escola de Jesus 7: a pintura do Paraíso: BOM"; "S2 Opus Majus 20: a foto da estátua: BOM".
  - 06/10/2026 (conferência 15, `relatorios/conferencia-samuel-2026-10-06.md`): "M1 A aba Marcar com a linha nova: Bom".
  - Nenhuma aprovação achada para os itens 1, 3 e 4 do TESTE 1 (ver "Falta").
  - O modo "Só as letras" (Misto) entrou no `fase-1` em 06/10/2026; na conferência 8 (05/10/2026) a opção A foi a melhor no Graduale 222, Opus 165, Horas 11 e 13, a B no Palatino 9 (Registro 05/10/2026).
- **Pronto em ramo:** `fase2-para-revisar` (`ce2b835`, PRONTO PARA CONFERIR, não juntado): "Trazer de volta nesta página" com o lugar marcado em laranja, e as áreas achadas da aba Marcar acertadas sozinhas (Registro 13/10/2026). A segunda conferência do verificador foi retomada em 20/10/2026 (ramo `verif-para-revisar-2026-10-13`).
- **Falta:**
  - A Fase 3 inteira (3.1 a 3.9).
  - O detector mais certeiro e o delineado: "Para revisar", rodada 4 (08/10/2026): "Ficou bom, mas podemos melhorar, mas o programa já pode ir assim, ele tem que ser mais acertivo para achar as figuras e para selecionar coisas que não foram apagadas."; rodada 5 (09/10/2026): "Fica no plano (1.5 e 2.18)".
  - Mudar o tamanho das áreas, "Os dois" (quadradinhos e pincel), no [2.18](itens/2.18.md).
  - Marcar uma área como "letra e traço" à mão ainda não protege a tinta no "Só as letras" (Lista de bugs, 12/10).
  - Os itens 1, 3 e 4 do TESTE 1 foram trabalhados em 17/09/2026 ([histórico, PARTE -5](../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md), §1): "Bug da margem direita (Bordas) — corrigido" (`ui/widgets/visualizador.py`, `_mover_recorte`); medidas em cm "enquanto arrasta"; "Moldura ao redor da página (Problema 4)". Esse trabalho de 17 a 23/09 ficou no programa "a aperfeiçoar" na Fase 2 (Registro 25/09/2026), **sem aprovação do Samuel** ("Zero testado por ele ao vivo ainda", PARTE -5). Conteúdo dentro da folha (escala e posição, com guias) **não foi ligado na tela** (PARTE -5, §1, item 4).
- **Não possível:** "**Scan de baixa resolução não se recupera.** As páginas do Boécio já nascem fora da faixa saudável — 4 MB para 50 folhas. O remédio é reescanear. É o único ponto do projeto em que "até ficar perfeito" não se aplica." (CLAUDE.md §9). O Samuel, sobre o Boécio 22 (05/10/2026): "acredito que é porque tem um teto que o programa consegue atingir".

---

## Tabela-resumo

| | Resultado | Itens do plano | Páginas que valem | Atingido | O que falta |
|---|---|---|---|---|---|
| R1 | Papel branco, letras e gravura intactas | 1.1–1.6, 2.8 | Palatino 5, 7, 9 (+ obrigatórias da Fase 1) | **aprovado em parte** (1.1, 1.2, 1.3 `[x]` em 02/10/2026; Palatino 5 BOM) | 1.4, 1.5; papel dentro de gravura pequena; contorno das letras |
| R2 | Sumir com a mancha do verso | 6.1 | Palatino 10, Marial 7 | **nada** | o 6.1 inteiro (subtrair frente e verso) |
| R3 | Margens iguais, pensando na costura | 2.4, 2.5, 2.6, 2.13 | Palatino 57, Graduale 222, 223, Horas 14 | **em parte** (corte com 1 mm aprovado em 02/10/2026; decisões G9, g8, g11, g12) | construir margens e caixa do conteúdo; `g7` e `g9-folha-maior-impressao` abertas |
| R4 | Tirar manchas sem mexer no título | 6.2, 2.18 | Palatino 66, 67 | **nada** | o 6.2 inteiro; decisão da ferrugem (Pesel 2) |
| R5 | Endireitar linhas tortas | 2.2, 2.3, 2.12 | Graduale 221, Escola 7 | **aprovado em parte** (G6 "Aprovado" em 12/10/2026, juntado) | 2.2 sem `[x]`; cunhas e bordas coladas; três controles do retângulo; 2.12 |
| R6 | Manter cores de verdade | 1.2, 1.4, 1.5, 6.3, 6.6 | Graduale 221, Horas 11, 13, 47 | **aprovado em parte** (vermelho e iluminura, dourado: BOM de 30/09/2026 a 02/10/2026) | Horas 47 no Preto e branco (RUIM, 05/10/2026); 1.4, 1.5; botão da moldura; 6.3/6.6 |
| R7 | Tamanho final A4 e margem para encadernar | 2.6, 2.4, 6.5, 2.19 | Siebmacher 9 | **nada** (decisões de 05/10/2026 e 14/10/2026 tomadas) | construir a fase de impressão; `g9-folha-maior-impressao` aberta |
| R8 | Apagar texto repetido em todas as páginas | 6.4 | Escola 7 | **nada** | o 6.4 inteiro |
| R9 | Seleção de letra, gravura e cor | Fase 3, 1.2, 1.5, 2.18 | Boécio 3, 7, 8, 22 | **aprovado em parte** (1.2 `[x]`; "só neste pedaço" BOM em 05/10/2026) | Fase 3; 2.18; detector mais certeiro; o Boécio tem limite de scan |
| alvo | Mágico Pro do CamScanner | 6.7 | Horas 26, 27, Escola 35 | **em parte** (peças BOM de 30/09/2026 a 02/10/2026) | a comparação final e o veredito (6.7) |
