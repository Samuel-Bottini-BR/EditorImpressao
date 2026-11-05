# Verificação das seis entregas de 04/11/2026 (verificador separado)

Feito em 05/11/2026, de madrugada, por um verificador que não construiu nada disto. Conferi do zero: cada entrega
contra as palavras do Samuel no Livro de decisões (cópia de `D:\programas\EditorImpressao-arquivos\plano-24-09-2026`,
04/11 22:53), os testes antigos com `git diff`, e a **janela de verdade** de cada cópia, aberta com um livro **do
acervo** (cópia de trabalho; o acervo só foi lido), sem projeto preparado, clicando por mensagens do Windows.

Nenhuma linha do programa foi mudada. Nada aqui é "aprovado": o máximo é **PRONTO PARA CONFERIR**.

## Resumo em uma linha por entrega

| entrega | decisões | situação | o que achei |
|---|---|---|---|
| 1. girar-pagina | D-618 | **cumpre** — PRONTO PARA CONFERIR | só a página da tela gira, inteira; a folha inteira gira como foto; o PDF sai igual à tela |
| 2. mover-lado | D-612, D-622, D-611 | **cumpre em parte** | tudo funciona nos pares; mas no "antes / depois" a ferramenta age no lado escrito **"antes"** (os rótulos estão trocados desde a obra) |
| 3. painel-livro | D-619, D-620 | **cumpre** — PRONTO PARA CONFERIR | quadro "Já feito no livro todo" nos três; setinha da qualidade em todas as ferramentas |
| 4. memoria-pdf | D-591 | **cumpre** — PRONTO PARA CONFERIR | frase palavra por palavra, "tentar de novo" e "entendi"; PDF antigo continua inteiro |
| 5. desfazer-pagina | D-621, D-623 | **cumpre** — PRONTO PARA CONFERIR, com um defeito pequeno | página posta em branco + "voltar a página": a tela mostra a página vizinha e diz "Original", o PDF sai branco |
| 6. caderno-numeros | D-604 | **cumpre** — PRONTO PARA CONFERIR | números certos nos três lugares; no "Montar para imprimir" a linha da frente quebra e começa com ":" |

**Para juntar as seis:** girar-pagina e mover-lado mexem na mesma linha de `ui/tela_conferir.py` (a tira de
miniaturas): o `git merge-tree` acusa **um conflito** ali. As duas linhas têm de ficar (o giro da miniatura, da D-618,
e o número/par da miniatura, da D-611). As outras combinações juntam sem conflito. Depois de juntar, a tira precisa ser
testada com as duas coisas juntas (giro + par pela folha).

## Como conferi (máquina e olho)

- **Máquina:** `git diff obra-2026-10-26..<ponta> -- tests/` em cada uma; rodadas do GitHub lidas (todas nas pontas,
  depois delas só mudaram documentos); **reversão**: copiei os testes novos para uma cópia do código da obra
  (`git archive obra-2026-10-26`, no scratchpad) e rodei: os testes de reversão **falham todos** lá, como devem.
- **Olho, na janela de verdade (1536 × 824, a tela do Samuel):** um piloto por entrega, prints em `prints/<n>-<nome>/`
  com as anotações (`anotacoes.txt`). Livros do acervo: Siebmacher (folhas deitadas; o único do acervo que serve para
  o Dividir — **o acervo não tem livro de folhas duplas**), Palatino, Rhetorica Christiana e Boécio.
- **Limite do jeito de pilotar:** com o menu fora da tela, o clique por mensagem num **item comum de menu** fecha o menu
  sem escolher (o agente do desfazer anotou o mesmo). Nesses casos escolhi o item pelas setas + Enter na janelinha do
  menu. Não é defeito do programa.

---

## 1. girar-pagina (ramo girar-pagina-2026-11-04, ponta d7bea265) — D-618

**Palavras do Samuel:** "quando ele gira a pagina ele faz ela caber no A4, ele deveria girar o conteudo só que é da
pagina cortada, mas ele gira a pagina verdadeira do scan. tanto que quando você vai girando ele cai na folha branca. Ele
gira as duas folhas ao mesmo tempo, faz uma confusão com as paginas." · correção: "não a folha inteira não continua
girando como hoje, pois hoje quando gira a folha altera a proporção dela para girar ela, e eu não quero que aconteça
isso" → "girar - sim" (gira como uma foto).

**Opinião: cumpre.** PRONTO PARA CONFERIR.

O que vi na janela (Siebmacher; folha 3 dividida pelo "dividir esta"; Cortar; página 3 = metade esquerda) — 13 de 13
conferências certas:

- "¼ à esquerda" do Propriedades: **só a página 3 deitou, inteira**, sem cair na folha branca (proporção 1,021 → 0,979,
  o inverso exato). A página 4 ficou **idêntica** (mesma imagem na tela) e a linha da divisão não mudou; a folha 3 ficou
  sem giro. Print `prints/1-girar/04` (antes) e `06` (depois).
- Mais um ¼, o canto "¼ à direita" e Ctrl+Seta: volta a 0; 3 Ctrl+Z e mais um voltam passo a passo. A miniatura da
  página 3 gira junto (conferido ampliando a tira).
- **Folha inteira (página 6):** gira como foto, sem esticar: 1,293 → 0,773 (o inverso exato). No Mover também
  (`14-folha-inteira-girada-mover.png`). Ctrl+Z desgira.
- **No PDF** (D-637, processado de verdade, `prints/1b-girar-no-pdf/pdf-paginas-3-a-7.png`): página 3 deitada (0,979),
  página 4 igual à de antes (0,271), página 6 em pé com a proporção certa (0,774); 135 páginas.
- Ao redor: Dividir em "Duas lado a lado" continua mostrando a folha inteira com a linha (print `16`).

**Testes antigos:** só os dois autorizados — o ajudante (linha 126) e a linha 170 de `test_recomeco_limpa_o_historico.py`,
cada um com comentário citando a D-618. **Reversão:** os testes de reversão de `test_decisoes_girar_pagina.py` falham na
obra (19 de 20 falham; alguns de guarda falham lá só porque o campo novo não existe). GitHub 41948211799: passou.

**Ressalvas:**

1. **Pergunta 1 do agente continua aberta e é importante:** numa folha dividida o bloco ainda se chama **"Girar a
   folha"** e a lista diz **"aplicar em: só esta folha"**, mas gira só a página. E "todas as folhas", "daqui em diante",
   "só as pares/ímpares" **continuam girando folhas inteiras** — numa folha dividida isso ainda faz a confusão do a-70.
   Precisa da resposta do Samuel.
2. A tecla do Endireitar é **I** (a E é a Mão); só anoto porque um print meu ("15-...-endireitar") saiu na Mão.

## 2. mover-lado (ramo mover-lado-2026-11-04, ponta fd2eee9e) — D-612, D-622, D-611

**Palavras do Samuel:** D-612 "1 - ele tem que funcionar com paginas lado a lado também" · "1- sim" (Cortar, Endireitar
e marcar também) · "Ok, pode ser assim o antes e depois" (as ferramentas agem no depois; o antes fica só para olhar).
D-622 "quando eu clicar fora da folha ele desseleciona o que está selecionado [...] como no photoshop." D-611 "SIm, mas
tem que verificar se vai ficar assim em todo os lugares né? a miniatura corresponder com o numero real".

**Opinião: cumpre em parte.** Nos pares está tudo certo; no "antes / depois" a ferramenta age no lado que a tela chama
de **"antes"**.

O que vi (Palatino; depois Siebmacher para o Dividir) — 17 das 19 conferências certas; as 2 "falhas" analisadas abaixo:

- Mover + "Duas lado a lado": **a vista não muda sozinha**. Um aperto na **outra** página do par (5) a escolhe e já
  arrasta (deslocamento 0,18); a 4 não anda. Ctrl+Z desfaz. Prints `prints/2-mover-lado/02`, `03`.
- **D-622:** clique no cinza tira a seleção (cantos e quadro azul somem; `04`); clique na página escolhe de novo
  (`05`). Na Mão, o clique no cinza não tira a escolha (como antes).
- Cortar nos pares: puxar a beirada da página 5 corta a 5 (recorte 1,0 → 0,85; `06`). Retângulo nos pares marca na
  página 4 (`07`). Endireitar fica nos pares (`08`). "Uma página": o Mover arrasta como antes (`11`).
- **D-611 no Dividir:** a tira junta **pela folha** (2-3, 4-5, 6-7 = folhas 2, 3, 4 divididas à mão) e cada miniatura
  tem o número real da página (1 a 135). Clicar na miniatura 5 leva à página 5 (o rodapé do Dividir diz "folha 3 de
  134", que é a folha dela: a minha conferência esperava "página 5" e estava errada). Fora do Dividir os pares são os do
  livro aberto, como antes. Prints `14`, `15`, `16`.

**Defeito (grave para a D-612, mas herdado da obra) — os rótulos do "antes / depois" estão trocados.**
Com o "antes / depois" ligado, o lado **esquerdo** da linha mostra o **depois** (a página com o filtro, e onde o Mover,
o Cortar e o Endireitar agem), mas o rótulo em cima dele diz **"antes: Original"**; o lado **direito** mostra o
**original** e o rótulo diz **"depois: Preto e branco"**. Resultado: o Samuel vai arrastar no lado escrito "depois" e
**nada acontece**; o arrasto só funciona no lado escrito "antes".
- Como reproduzir: Palatino, página 9, Filtro Preto e branco, apertar "antes / depois": à esquerda da linha azul a
  página sai em preto e branco com o rótulo "antes: Original" (`prints/2b-antes-depois/02-filtro-antes-depois.png`).
  Ferramenta Mover, arrastar à direita da linha: não move; arrastar à esquerda: move (`04-mover-depois-de-arrastar-a-esquerda.png`).
- **Já era assim na obra** (mesmo teste no código da obra: `prints/2c-antes-depois-na-obra/02-obra-filtro-antes-depois.png`).
  Não foi o mover-lado que causou; mas ele passou a usar esse lado para as ferramentas. O agente levantou isso como a
  **pergunta 4** dele ("o rótulo 'antes: Original' fica em cima do lado onde a ferramenta age").
- Sugestão para a gerente levar ao Samuel: trocar os rótulos de lado (o que a tela mostra fica como está). É mudança
  de tela: precisa do "sim" dele.

**Testes antigos:** só a parte do Dividir de `test_decisoes_tira_em_pares.py` e `test_decisoes_tira_pares_juntas.py`
(autorizada, comentário citando a D-611). **Reversão:** `test_decisoes_d622_clicar_fora` (3), `par_escolhe_e_arrasta`
(3 de 4), `tira_numero_real` (2 de 3), `antes_depois_da_ferramenta` (4 de 5) falham na obra. GitHub 41948184684:
passou na 2ª tentativa da parte 4 (a 1ª caiu por um travamento do Python, sem teste falhando — ressalva do agente).

**Ressalvas:** (1) no Dividir o título da tira é "FOLHAS" mas os números embaixo são de **página** e o rodapé diz
"folha 3": já era assim, mas mistura as duas palavras (`15`); (2) o conflito com o girar-pagina (acima).

## 3. painel-livro (ramo painel-livro-2026-11-04, ponta 41120c0b) — D-619, D-620

**Palavras do Samuel:** "para o livro todo, não entendi essa mensagem, elas não deveriam ser opções para se escolher,
essa opção de qualidade não deveria ser para todas as ferramentas?" → "1- B" (D-619) e "2- Pode" (D-620); e depois:
"não tem como colocar só uma setinha e quando aperta nela aparece as opções de qualidade?"

**Opinião: cumpre.** PRONTO PARA CONFERIR. 25 de 25 na janela (Rhetorica Christiana).

- **D-619:** no Cortar, no Dividir e no Endireitar o quadro diz **"JÁ FEITO NO LIVRO TODO"**; o título antigo saiu; o
  "mudar no Automático..." ficou; no Cortar a caixinha "Margens iguais" (D-554) ficou e a "Qualidade da prévia" saiu do
  painel. Prints `prints/3-painel-livro/02`, `03`, `04`.
- **D-620:** a setinha aparece na barra de baixo em **todas** as ferramentas que testei (Cortar, Dividir, Endireitar,
  Mover, Retângulo, Mão, Zoom, Filtro). Abre "Rápida / Média / Alta" com a escolhida marcada (`06`); escolhendo "Alta",
  fica gravada para o programa todo e vale no Endireitar, no Mover e no Dividir (300 DPI; balão "Qualidade da prévia:
  Alta").
- Ao redor: "Uma página / Duas lado a lado", "antes / depois", zoom e "ajustar à tela" continuam na barra.

**Testes antigos:** além das promessas novas (só acréscimo), **três linhas de `tests/test_paineis_na_tela.py`** trocam
"PARA O LIVRO TODO" por "JÁ FEITO NO LIVRO TODO" (linhas 255, 378, 425), com comentário citando a D-619. O ONDE-PAREI
diz "Opção A autorizada" pela gerente — **mas essa exceção não estava na lista que a gerente me passou**: a gerente
precisa confirmar que autorizou. **Reversão:** os 9 testes de `test_decisoes_painel_livro.py` falham na obra.
**GitHub 41949243543 terminou "falhou"** por 1 teste: `test_decisoes_so_as_letras::test_d148` ("não aconteceu a tempo"),
o instável conhecido. No PC, com outro agente usando a máquina: o arquivo inteiro passou 2 de 3 vezes e o `test_d148`
sozinho 6 de 6 (no painel-livro, 8 das 9 voltas); na cópia da obra, 9 de 9. Na própria obra ele já tinha caído por tempo
no GitHub (commit bf13683b, rodada 41913269201). Não vejo o painel-livro como causa, mas fica a ressalva: rodar de novo
na rodada do PC da gerente (a cópia da obra que usei não tem a pasta dos modelos, então o tempo das duas não se compara).

**Ressalvas:** (1) em 1366 de largura com o Propriedades aberto a conta encolhe para "0 de 446 c..." (inteira no
balão) — já era apertado antes; (2) a setinha é bem pequena: o Samuel decide se acha.

## 4. memoria-pdf (ramo memoria-pdf-2026-11-04, ponta 45005116) — D-591

Não medi memória (outro agente mede nos 9 livros). Conferi só a D-591 e o código.

**Palavras do Samuel:** escolheu "Frase certa + botão "tentar de novo" (recomendo)": "Faltou memória no computador:
outros programas abertos estão usando quase toda a memória. Feche o que não estiver usando. Nada do seu trabalho no livro
se perdeu.", com "tentar de novo" (processa de novo, mesmo nome e lugar) e "entendi".

**Opinião: cumpre.** PRONTO PARA CONFERIR. 11 de 11 na janela (Boécio).

Como testei: processei uma vez (PDF antigo); depois processei de novo escolhendo **"substituir o antigo"**, com uma falta
de memória **forçada por mim** no meio (um `MemoryError` levantado de dentro do processar de verdade na página 3).
- O aviso: título "Um momento", **a frase palavra por palavra**, botões **"tentar de novo"** e **"entendi"**
  (`prints/4-memoria-pdf/06-caixa.png`).
- "entendi": fica na área de trabalho; **o PDF antigo ficou idêntico** e nenhum arquivo de trabalho sobrou na pasta.
- "tentar de novo": processa outra vez **sem perguntar o destino**, no mesmo nome e lugar; o PDF novo saiu com as 50
  páginas e nada sobrou.

Código: `ui/tarefas.FRASE_FALTOU_MEMORIA` é a frase exata; `faltou_memoria()` reconhece `MemoryError` e os textos de
falta de memória do OpenCV e do MuPDF. **Testes antigos:** nenhum mudou. **Reversão:** 14 dos 15 de
`test_decisoes_aviso_de_memoria.py` falham na obra. GitHub 41951184818 passou; filtro de velocidade 41951188321 "igual".

**Ressalvas:** (1) a falta de memória foi simulada, não real; (2) a frase nova também aparece (só com o "entendi" de
sempre) quando falta memória no Automático, no Dividir e no ler linhas, porque essas tarefas usam o mesmo tradutor de
erro — a D-591 fala do processar; não é contra ela, mas a gerente pode querer contar ao Samuel; (3) os dois achados do
agente para a Lista de bugs ("Imprimir agora" e "Extrair as páginas escolhidas" copiam o livro inteiro para a memória)
continuam abertos.

## 5. desfazer-pagina (ramo desfazer-pagina-2026-11-04, ponta e9f19653) — D-621, D-623

**Palavras do Samuel:** D-621 "eu quero um botão para desfazer ajustes em uma pagina só [...] eu quero poder clicar e
falar quais coisas eu quero que sejam tirar [...] e eu quero fazer só em uma." · "com o botão direito clicando na pagina
eu posso escolher a opção desfazer tudo" · "A2". D-623 "eu queria conseguir com botão direito apertando no meio das
paginas aperece opção de adicionar folha em branco."

**Opinião: cumpre.** PRONTO PARA CONFERIR, com um defeito pequeno de tela.

O que vi (Siebmacher; folha 3 dividida à mão; **Automático de verdade** no livro todo: Endireitar, Cortar, Limpar em
Preto e branco, 175 s):
- Botão direito na página 3 → "Desfazer nesta página" → as 5 caixinhas (Mover e Gravuras apagadas porque não mexeram;
  `prints/5-desfazer-pagina/04`). Marquei Corte e Filtro → "desfazer": a página 3 ficou sem corte e em Original, o
  Endireitar ficou, **a página 4 (a outra metade da folha) não mudou nada**, a folha continua dividida, **uma ação só**
  no Histórico. Ctrl+Z volta, Ctrl+Y refaz (`06`, `07`).
- Na miniatura o menu tem o mesmo "Desfazer nesta página" e, embaixo, "adicionar página em branco antes/depois" (`08`).
- Em "Duas lado a lado", o botão direito na **outra** página do par abre o menu **dela** (`prints/5b-.../02`, `03`).
- Página em branco depois da 5 e antes da 1: entram (134 → 135 → 136); Ctrl+Z tira, Ctrl+Y põe; "tirar do livro" a
  tira. **No PDF ela sai branca** (`prints/5c-...`, tinta 0%).
- Ao redor: o botão direito no Mover continua abrindo o menu das linhas de apoio.

**Defeito pequeno (D-623 + D-637: a tela e o PDF discordam).** A página posta em branco, no Cortar, mostra a **imagem
da página vizinha** (de quem ela copia o tamanho) com a faixa "Esta página vai sair em branco" e o botão **"voltar a
página"**. Se o Kaique apertar "voltar a página", a tela passa a mostrar a página vizinha como se fosse a nova, e a faixa
diz **"Esta página vai sair em Original"** — mas o PDF continua saindo **branco** (o processar sempre deixa branca a
página posta à mão).
- Como reproduzir: Boécio, botão direito na miniatura 5 → "adicionar página em branco depois" → ir à página 6 no Cortar
  (`prints/5c-pagina-em-branco-voltar/02`) → "voltar a página" (`03`: a página 5 aparece no lugar da 6) → Filtros
  (`04`: "vai sair em Original") → processar: a página 6 do PDF é branca.
- O que a decisão não diz: o que a página posta deve mostrar no Cortar e se "voltar a página" faz sentido nela. Pergunta
  para o Samuel, ou o programa esconder o "voltar a página" nessa página (é mudança de tela: perguntar antes).

**Testes antigos:** nenhum mudou. **Reversão:** na obra falham os 14 de `test_decisoes_desfazer_pagina.py` e os 9 de
`test_decisoes_pagina_em_branco.py`. GitHub 41955321135 passou; filtro de velocidade
41949515821 "igual".

## 6. caderno-numeros (ramo caderno-numeros-2026-11-04, ponta 23d2b157) — D-604

**Palavras do Samuel:** "o verso da folha 1 e 19 não podem ter a numeração de folha 1 - e 19 tem que dizer a numeração
que elas realmente teriam." · "Folha 1 de 19, frente: páginas 20 e 1 [...] verso: páginas 2 e 19 [...] É isso?" →
"acredito que sim" · "é melhor colocar a numeração das paginas verdadeiras aqui".

**Opinião: cumpre.** PRONTO PARA CONFERIR. 13 de 13 na janela (Boécio, 50 páginas, 20 por caderno).

Fiz a conta da dobra **à mão** (fora do programa) e comparei:
- **Etapa 7 do Automático:** folha 1 "Folha 1 de 13 — frente: páginas 20 e 1" / "verso: páginas 2 e 19"; folha 2 "18
  e 3" / "4 e 17", trocando **logo depois do clique**; folha 6 (começo do 2º caderno) "40 e 21" / "22 e 39"; folhas 12
  e 13 certas. O desenho bate: página 20 à esquerda e a capa (página 1) à direita (`prints/6-caderno-numeros/01`).
- **Tela grande de caderno:** as mesmas palavras nas folhas 1 e 2 (`06`, `07`).
- **"Montar para imprimir"** pelo caminho de verdade (processar → tela final → "montar para imprimir em A4"): folhas 1 e
  2 certas (`11`, `12`).

**Testes antigos:** nenhum mudou. **Reversão:** os 7 de `test_decisoes_caderno_numeros.py` falham na obra. GitHub 41958485208 passou.

**Ressalvas:** (1) no "Montar para imprimir", na tela do Samuel, a linha da **frente** quebra e a de baixo começa com
dois-pontos: "Folha 1 de 13 — frente" / **": páginas 20 e 1"**, enquanto a do verso cabe numa linha (`11`). Não está
errado, mas fica estranho; o agente anotou (pergunta 3 dele); (2) a pergunta 1 do agente ("páginas em branco e 61")
continua aberta; (3) o "Folha 2 de 32" continua (D-574); o comentário do Samuel na D-631 ("Porque que é folha 2 de 32?")
ainda não foi respondido.

---

## Onde está o piloto

Os scripts que pilotaram a janela estão em `piloto/` (um por entrega; `comum.py` e `base.py` são os ajudantes). Rodar
com `D:\programas\EditorImpressao\.venv\Scripts\python.exe piloto\p1_girar.py` (cada um abre a cópia da entrega,
copia o livro do acervo para uma pasta de trabalho e grava os prints em `prints/`). As pastas de trabalho apontam para o
scratchpad desta sessão: para rodar de novo, trocar o caminho em `comum.py`.

## Ressalvas gerais

1. **Regra nova D-637 (05/11):** as seis entregas são de antes dela; **nenhum ONDE-PAREI tem a seção "Como fica para
   quem usa e no livro"**. Conferi o PDF onde a entrega mexe nele (girar, página em branco, D-591, cadernos).
2. **Junção:** um conflito entre girar-pagina e mover-lado em `ui/tela_conferir.py` (a linha da tira); as duas linhas
   ficam. Testar a tira depois de juntar.
3. **Acervo sem folha dupla:** o Dividir foi testado com folhas do Siebmacher divididas à mão. O caso exato do Samuel
   (Gradus, página 14) não está no acervo; os agentes usaram o Gradus.
4. **Defeitos:** os rótulos trocados do "antes / depois" (herdado da obra, pesa na D-612) e a página posta em branco +
   "voltar a página" (D-623). Os dois são de tela: precisam da palavra do Samuel antes de mexer.
5. A conferência inteira no PC (§4.6, com os outros agentes parados) **não** foi feita por mim: é da gerente antes do
   `fase-1`. As rodadas do GitHub de cada ramo foram lidas.
