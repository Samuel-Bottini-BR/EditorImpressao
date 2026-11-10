# Auditoria das escolhas da gerente e das mudanças da obra (27/10/2026)

**Em uma frase:** das 78 escolhas e mudanças da obra conferidas, **6 mudam ou deixam de fazer algo que o Samuel já
tinha decidido (C)**, **17 acrescentam coisas que ele não pediu (B)** e **55 só fazem funcionar o que ele mandou (A)**.

Por que esta auditoria existe: Samuel, 27/10/2026 (D-549, `CLAUDE.md` §11 regra 7): "os agentes estão mudando coisas
que eu já tinha definido, é só para fazer o que eu já tinha mandado, fazer as ferramentas que colocamos no programa
funcionem como deveriam e como eu tinha escolhido."

**Como conferi (só leitura, nada mudado):** Livro de decisões (`docs/plano/DECISOES.md`, ramo `obra-2026-10-26`
`1e9abb7`), os 10 `relatorios/obra-*/ONDE-PAREI.md`, o plano da obra aprovado (D-471), o rascunho do layout
(`EditorImpressao-arquivos/plano-24-09-2026/layout/Plano de layout (rascunho).md`), a lista única de 23/10 e o código
da obra quando o relatório não bastava (grep e `git log fase-1..obra-2026-10-26`). **Conferido por leitura, não por
máquina nem por olho:** não rodei testes, não abri o programa, não tirei prints.

**Legenda:** **A** cumpre o que ele mandou (detalhe técnico) · **B** acrescenta o que ele não pediu · **C** muda ou
contradiz (ou deixa de fazer) o que ele decidiu. Recomendação: manter / desfazer / perguntar. Pela regra 7, todo B vai
como **perguntar** (o Livro não responde, então fica como pergunta na Central); quando acho que manter é seguro, digo.

---

## C — muda ou contradiz o que ele decidiu (6)

| Decisão / mudança | O que foi feito | Classe | Decisão dele que toca (data e palavras) | Recomendação |
|---|---|---|---|---|
| **D-531 + JPEG 92 da etapa 10b** (achado 4.5 "PDF gigante", da lista única de 23/10) | Página de cor e de cinza passou a ir ao PDF em JPEG 92 (com perda: 1 a 14 tons de diferença da tela); a D-531 ainda ia guardar a página com no máximo 2× a resolução do scan. | **C** | **D-304**, 01/10 (P3): "Eu quero ter a opção 1.6, mas eu quero poder deixar como está também, **o tamanho do arquivo depois não importa**". O 4.5 é achado de agente. | **desfazer** — já mandado na D-549. Atenção: o código da obra **ainda** tem `core/pdf_io.py:379 QUALIDADE_DO_JPEG = 92`, e 4 testes foram afrouxados para "PDF = prévia a poucos tons" (`test_gravar_pdf_sem_parar_a_janela`, `test_tirar_fundo_no_programa::test_pdf_final_sai_igual_a_previa`, `test_so_neste_pedaco_no_tirar_o_fundo::test_pdf_com_pedaco_sai_igual_a_previa`, `test_ajustar_pedaco_na_folha_girada::test_tirar_o_fundo_com_pedaco_na_folha_girada`): têm de voltar a "igual ponto a ponto". |
| **Lado direito com 2 dos 4 jeitos** (etapa 2, escolha 5 do agente) | Ver > "Lado direito" e Configurações > Aparência só têm "Ícones na borda" e "Sanfona (a área de trabalho 1)". O agente escreveu que "abas no alto" e "painel solto" "não foram pedidos" (`ui/barra_de_menu.py:274`, `ui/widgets/paineis.py:96`). | **C** | **D-033**, 05/10 (R2 nº 9): "Quer **os quatro jeitos** no app, escolhendo dentro dele: sanfona, abas no alto, ícones na borda, painel flutuante" · 20/10, 902: "**C — Nos dois lugares**"; o rascunho registra "a troca do lado direito (ícones na borda, sanfona/área de trabalho 1, abas no alto, painel solto) fica no menu Ver e nas Configurações". | **desfazer a omissão**: construir "abas no alto" e "painel solto" (D-033 tem dono: etapa 2). |
| **Nomes da janela "Montar para imprimir" trocados** (etapa 9a, "rótulos encurtados") | "Ordem de páginas"→"Imprimir", "Páginas por caderno"→"Cada caderno", "Rotação automática"→"Girar sozinho a página deitada", "Centralizar automático"→"Centralizar sozinho", "Reverter páginas"→"Ordem invertida", "Agrupar"→"Agrupar as cópias", "Esquerda/Direita"→"costura à esquerda/à direita", "cancelar"→"parar" (`ui/dialogo_impressao.py`, conferido contra o `fase-1`). | **C** | `fr-26`, 22/10: "Está bom" + "**Só tem que melhorar esse layout**, cheio de letras uma em cima da outra" (pediu arrumar, não renomear) · **D-315**, 14/10: as opções "que aparecem nos prints do PDF que mandei" (UPDF) · **D-374**, 22/10: "revisarmos todos os nomes de botão com um novo agente" — ele decide um por um. | **desfazer os nomes** e levar as sugestões à revisão de nomes (etapa 11). A nova disposição em duas colunas fica (é o pedido do `fr-26`, ver A). |
| **D-496** (etapa 9c) | "Endireitar: as contas discordam" não avisa mais quando as duas contas dão a página a até 0,3° do reto, **mesmo discordando mais de 0,3°** (ex.: +0,25 e −0,1). Boécio: 12 avisos → 8 (`core/endireitar_scantailor.ANGULO_QUASE_ZERO`). Construída. | **C** | **D-082**, 05/10 (G4): "O do ScanTailor de fábrica; **quando os dois discordarem mais de 0,3 grau, a página fica marcada 'conferir'**". | **desfazer e perguntar** (mostrar as 4 páginas do Boécio que perderam o aviso). |
| **D-476** (fase de "Marcar como: iluminura / moldura") | A gerente pôs o "Marcar como" com "iluminura ou pintura" e "moldura" na Fase 1.5, depois da obra. Nada no programa mudou. | **C** | **D-242**, 12/10 (705): "A — Sim, os dois" — no Livro, dono "Lista de espera (12/10), **fase a definir por ele**" · **D-388**: "O Samuel decide em que fase ela entra." | **perguntar** a fase. |
| **D-529 + "Inserir" fora da grade** (etapas 3 e 4) | "Dividir" na grade "Todas as páginas" foi para a Lista de espera (depois da obra) e "Inserir página" não foi feito (D-487: muda o modelo de dados). A grade só "roda o automático nelas". | **C** (deixa de fazer) | **D-334**, 24/09 (paráfrase): "como o 'Organizar páginas' do UPDF: seleção múltipla, girar, apagar, extrair, **inserir, dividir**." O plano aprovado (D-471) pôs "inserir" na etapa 3. | **perguntar** se pode esperar. E perguntar o que é "dividir": no UPDF é **partir o PDF em arquivos**, não dividir a folha (o agente entendeu dividir a folha). |

---

## B — acrescenta o que ele não pediu (17)

| Decisão / mudança | O que foi feito | Classe | Decisão dele que toca (data e palavras) | Recomendação |
|---|---|---|---|---|
| **D-532** (não construída, etapa 9d) | Gravura de fundo escuro (Palatino 70 e 74, fotos de retícula do Righetti) no Preto e branco sairia em tons de cinza, não em 1 bit. | **B** | **D-147**, 30/09: P1a "Cinza (tons de cinza): BOM" · pontilhados "RUIM" (fala de **foto e pintura**, não de gravura). Ele nunca disse que gravura de traço vai em cinza. | **perguntar** (com as fotos da conferência da 10b); não construir antes. |
| **D-530** (com a D-493) | O desentortar "seguindo só o bloco do texto" vira **opção nova da página** no painel do desentortar (desligada). A D-493 (ligar para todo livro) não foi ligada: entortava a Marial 41. | **B** | **D-113**, 23/10: "o primeiro passo [...] seria **tirar essa moldura preta** [...] ai o desentortador não iria confundir as letras com moldura preta" (isso foi feito na 10a; a conta "só o bloco" é ideia do agente). | **perguntar** (é botão novo). |
| **D-495 + D-499** (etapa 4) | A faixa preta da tampa do scanner (Righetti 96) só é tirada quando a pessoa divide ou acerta a linha **à mão**; o Automático nunca tira; a faixa é **pintada de branco**, não cortada (regra nova de 8 mm / 97% da folha). | **B** | **D-097**, 13-21/10: "É para sumir totalmente." · "tem que ficar rente a folha de papel, não pode ter preto ali." · **D-092**, 09/10: tarja e moldura do scanner — "**O Kaique escolhe por livro**" entre cortar e pintar de branco. | **perguntar** (já vai à conferência final como pergunta 2 da etapa 4, prints `depois-08`/`depois-09`). |
| **D-500** (etapa 4) | Quando o ScanTailor corta a folha fora de 20%–80% da largura, o programa **troca sozinho** para a conta do Editor naquela folha e põe "Lombada incerta". | **B** | **D-080**, 05/10 (G2): "escolhendo 'o do programa' ou 'o do ScanTailor', e **trocando numa folha se um ficar ruim**" (a troca era do Kaique) · **D-089**: "O do ScanTailor". | **perguntar** (o "La vida eterna" folhas 4 e 5 é o exemplo; recomendo manter — é a regra do próprio ScanTailor — mas ele decide). |
| **D-494** (pela metade) | A caixinha "Margens iguais" ficaria à vista **também na tela do corte** (ela já mora no Automático, Saída). | **B** | **D-075**, 05/10 (G9): caixinha "Margens iguais" desmarcada de fábrica, "Mas eu vou conseguir alterar isso né?" (o lugar na tela nunca foi escolhido por ele). | **perguntar** o lugar (a parte "não forçar o mesmo tamanho" é A: é como já era). |
| **D-481** (etapa 3) | Letras novas: **D** = Dividir, **X** = Cortar, **I** = Endireitar. | **B** | R8 302, 06/10: "quando eu passar em cima da agrupada tem que mostrar a letra dela de atalho" (não escolheu letras). O agente da etapa 2 tinha perguntado e escrito: "Não inventei: fica como está até ele dizer." | **perguntar** (mostrar as letras; trocar é barato, são remapeáveis). |
| **D-540** (etapa 5) | Letra **F** = "Mover e redimensionar" (o V do Photoshop já é a Varinha aqui). | **B** | idem (R8 302). | **perguntar** junto com a D-481. |
| **Shift+Del = "Tirar esta página do livro"** (etapa 2, escolha 3) | Tecla nova no menu Página. | **B** | **D-046**, 07 e 09/10: "Dois botões; **a tecla Delete deixa em branco**" (não deu tecla ao "Tirar do livro"). | **perguntar** junto com as letras. |
| **Menu novo "Ferramentas"** (etapa 2, escolha 2) | Menu entre Editar e Marcar com Dividir, Cortar, Endireitar, as de marcar, Zoom e Mão. | **B** | Ele escolheu os menus nas rodadas 12-14 (903 B: menu novo "Painéis"; 904 A: itens do Ver). O plano aprovado (D-471) pedia "menus com Endireitar/Cortar/Dividir" (achado do teste do Kaique feito por agente), não um menu novo. | **perguntar** (mostrar o print `relatorios/obra-etapa2/prints/depois-05-menu-ferramentas.png`). |
| **D-475** (não construída, etapa 11) | Texto novo do aviso "só as pares" num livro dividido: "A página 2 fica na folha 1, que é ímpar. Para girar só as folhas pares, vá para a folha 2 (páginas 3 e 4)." | **B** | **D-036**, 06/10: "O programa avisa: 'vá a uma folha par'" (aviso aprovado: "Você está numa folha ímpar. Para girar só as pares, vá a uma folha par e gire de lá."). | **perguntar** na revisão de nomes (D-374). |
| **"mandar para a impressora" do "Montar para imprimir" agora pergunta antes** (etapa 9a) | Janela de confirmação a mais (impressora, lados, cópias, folhas) antes de mandar. | **B** | **D-325**, 21/10 (`imp-5`): "Também manda direto para a impressora". (A D-012 pede confirmação só no "imprimir agora".) | **perguntar** (recomendo manter: é segurança, como a D-012). |
| **Frase nova na "Ficou pronto!"** (etapa 9a, lista única 5.12) | "Para imprimir em cadernos, use 'montar para imprimir em A4' [...]" embaixo dos botões. | **B** | **D-330**, 22/10: "Deixar os dois" (os dois botões, sem frase). 5.12 é achado de agente. | **perguntar**. |
| **Aviso "o que está impresso fica CORTADO"** na impressão acima de 100% (etapa 10a, lugar 8 da D-104) | Aviso novo na janela de imprimir. | **B** | **D-466**, 22/10: "Primeiro provar em páginas de verdade, **depois decidir**" — ele decide vendo. Já havia o aviso de margem (D-319). | **perguntar** (mostrar Escola 7 a 140%, `relatorios/obra-etapa10a/conferencia/img/imprimir140.jpg`). |
| **Caixinha "Usar esta receita no aviso de todo livro novo"** (etapa 3, caixa da receita) | Opção nova na caixa de salvar receita (escolhe a "receita de sempre" do aviso do livro novo). | **B** | Decisão 2, 25/09: "salvar como **receita** com nome e reusar" · `fr-219`: "pode melhorar a caixa de como escolhemos o que vai dentro da receita". A "receita de sempre" vem da D-018 (escolha da gerente). | **perguntar**. |
| **Nome do PDF sugerido sem acento** (etapa 9a, lista 5.15; etapa 9c, item 2) | "Ofício da Imaculada Conceição - mágico pro.pdf" passa a ser sugerido como "Oficio da Imaculada Conceicao - magico pro.pdf" (também o "- para imprimir"). | **B** | **D-365**, 18/07: "Corrija TODOS os textos da interface para **português correto**". A regra citada pelo agente (`CLAUDE.md` §3, "caminhos de disco sem acento") é técnica, do código; o nome do livro é do Kaique. 5.15 é achado de agente. | **perguntar** (recomendo voltar ao nome com acento até ele dizer). |
| **D-478** (fase; nada no programa) | Espaços "Limpo / Completo" viram arranjos salvos com nome dentro do "tudo livre", na Fase 4. | **B** | Decisão 4, 28/09 (rascunho): "Espaços de trabalho Limpo / Completo mostrados [...]. **Aprovação: a confirmar**" — "a decidir pelo Samuel". | **perguntar** quando chegar a Fase 4. |
| **D-480** (fase; nada no programa) | Item 7.3: os manuscritos entram na transcrição da Fase 7 (Kraken, CREMMA). | **B** | Plano 7.3 (D-208): "**decidir** se os manuscritos entram" (decisão dele); apoio: D-132, "OCR de manuscrito desde o começo". | **perguntar** quando chegar a Fase 7 (a própria linha já diz "ele confirma"). |

---

## A — só faz funcionar o que ele mandou (55)

### Escolhas da gerente anotadas no Livro

| Decisão | O que foi feito | Classe | Decisão dele que cumpre | Recomendação |
|---|---|---|---|---|
| D-016 | Arrastar as etapas do Automático muda a ordem em que **rodam**; a montagem da página fica na ordem obrigatória. | A | D-003 "Ordem das etapas: livre [...] Sem cadeados" × mais recentes dele: `g6-endireitar-antes` "Pode começar" (09/10) e `a-212-desentortar` "A — cortar uma vez só, no fim" (22/10). | manter; **avisar** que arrastar não muda o PDF (a prova é "a página sai igual"). |
| D-017 | Aumentar além da beirada: página do mesmo tamanho, parte de fora marcada, aviso no "Para revisar", nada reduzido sozinho. | A | G10, 05/10: "(b) Avisar e não reduzir - avisar para eu reduzir manualmente". | manter |
| D-018 | "Rodar o automático…" do aviso abre a janela grande com a receita marcada; nada roda antes de "Rodar". | A | D-005 (R13 804 B): o aviso com "Rodar o automático…" (o "…" abre janela). | manter |
| D-473 | Tela e PDF da mesma conta; enquanto não fica pronta, prévia com bolinha. | A | D-066, 23/10: "precisamos que o pdf saia que nem está na tela" · D-064, 22/10: "é só colocar uma bolinha de carregamento". | manter |
| D-474 | A meta "menos de 10% das páginas no Para revisar" continua. | A | D-254, 18/07 (a meta é dele). | manter |
| D-477 | Ferrugem rosada da Pesel 2 deve sumir (Fase 6.2). | A | R4 do plano (manchas somem) · D-123 (manchas vermelhas e marrons). | manter |
| D-479 | "o do Editor" / "a do Editor" em todo lugar. | A | 907 B (20/10) "o do Editor" · `ly-editor` "Está bom". | manter |
| D-482 | "agora não" fecha o aviso do livro novo para aquele livro. | A | D-005 (o nome "agora não" foi do agente de layout; o que o botão faz não estava escrito). | manter |
| D-483 | A medida por trás só roda no livro novo; livro salvo volta como estava. | A | D-284 "Medir o livro inteiro por trás, depois de abrir" (o livro salvo já foi medido na conferência). | manter |
| D-484 | Gravuras, Margens iguais e Cadernos valem sempre no livro todo; "desligar" nas escolhidas deixa a etapa nas outras. | A | D-002 (livro todo / escolhidas / uma página) · D-068 (ligar e desligar). | manter |
| D-485 | Página antiga com filtro diferente do livro conta como "mexida à mão" na pergunta. | A | D-004 "o programa pergunta se quer pular as páginas mexidas". | manter |
| D-486 | A página ao lado na janela grande é a original; o antes/depois ao vivo fica para a Lista de espera. | A | D-002 "Na janela, ver a página ao lado, folhear e dar zoom" · D-070 (laboratório) já estava na Lista de espera. | manter |
| D-487 | Grade com várias escolhidas: girar, em branco, tirar, trazer de volta, extrair (as folhas como estão no PDF de entrada), rodar o automático. ("Inserir": ver C.) | A | D-334. | manter; o "extrair sem os ajustes" é detalhe a mostrar a ele. |
| D-488 | `ui/tela_opcoes.py` fica no repositório, fora do caminho. | A | D-002 · regra de apagar (D-420). | manter |
| D-489 | Recomeço só quando o PDF mudou, o projeto não lê ou falta página; mudar etapa nunca recomeça. | A | Defeito de 29/09 · D-342 ("o mesmo trabalho"). | manter |
| D-490 | O "Sim" do fundo vale na hora (só nas páginas em Original; código conferido, `ui/janela_principal.py:807`). | A | D-135 · D-136 "só as de 'Original'". | manter |
| D-491 | Retângulo do corte em Configurações, livro e página. | A | D-094 "quero a b e c juntas" · D-093. | manter |
| D-492 (não construída) | O tique do menu Filtro acompanha a página. | A | O tique já existe e engana; D-010 "o botão tem que ser provado que ele faz o que se diz". | manter |
| D-497 (não construída) | Página que fica branca depois de mudar a divisão ganha "Parece em branco" (salvo "está certo" dado antes). | A | D-271 (aviso próprio) · D-273 (o aviso acompanha o problema). | manter |
| D-498 | "não dividir esta" junta e guarda as duas páginas; "dividir esta" as devolve como estavam. | A | Pedido da etapa 4 (sessão 1, 26/10) · D-046 · D-009. | manter |
| D-501 | O livro nunca abre no Dividir; depois de dividir, uma página por vez. | A | D-007, 26/10: "o livro tem que aparecer em uma pagina por vez para mim". | manter |
| D-522 (o número) | "Muitas" páginas em branco = 40% ou mais. | A | `pd-versos-em-branco`: "Juntar num aviso só do livro quando forem muitas" (o número é detalhe). | manter |
| D-528 (não construída) | Marcações da folha inteira vão para a metade em que estão ao dividir. | A | D-009 (o feito à mão vale) · "o trabalho não se perde". | manter |
| D-541 | Como o Mover mexe (arrasta ao vivo, canto proporcional, 5% a 4×, o meio fica na área branca). | A | D-008 "como é no photoshope, que você arrasta a hora que quiser e aumenta a hora que quiser". | manter |
| D-542 | "Centralizar" e ímã pelo que está impresso. | A | D-303 "precisamos centralizar" · teste do Kaique "mover ele para o meio da folha". | manter |
| D-543 | Aviso "Parte do impresso fica de fora" (0,05%), parte de fora em vermelho, "ver no Mover" / "está bom assim". | A | G10 "Avisar e não reduzir". | manter |
| D-544 | "Mover conteúdo" sai do Cortar (o Cortar ganhou uma frase que manda para o Mover). | A | D-008 "deveriam ser duas coisas independentes". | manter (a frase no Cortar é pequena; pode ir à revisão de nomes) |
| D-545 | "usar em todas..." no Mover, com as já mexidas desmarcadas. | A | G10 "ter uma opção para passar isso para todas as folhas" · D-090 · D-091. | manter |
| D-546 | Só o Mover mostra a página na área branca (até a D-547). | A | D-473/D-066. | manter |
| D-547 (não construída) | Todas as telas e miniaturas mostram a página movida. | A | D-066 "precisamos que o pdf saia que nem está na tela". | manter |
| D-548 | O aviso não ignora o que já estava perto da beirada. | A | G10/D-017 (nada cortado sem ver). | manter |

### Mudanças de comportamento descritas nos relatórios das etapas

| Etapa | O que mudou | Classe | Decisão dele que cumpre | Recomendação |
|---|---|---|---|---|
| 1 | O feito à mão (corte, ângulo, filtro, marcação, mover) vale no PDF com a etapa desligada; marca "mexida à mão"; projeto antigo sai igual (96/96 e 24/24 somas). | A | D-009 · D-004 · D-342. | manter |
| 1 | Mover chega ao PDF sem tamanho de folha e com a folha arredondada (defeito do Kaique 15 × 53). | A | D-008. | manter |
| 2 | Todas as ferramentas sempre montadas, menus acesos, sem caixinha nenhuma o livro abre (na Mão). | A | D-001 "Uma única tela com todas as ferramentas" · D-009. | manter |
| 2 | Delete = "Deixar em branco"; bloco "Esta página" com "deixar em branco" / "tirar do livro" em toda ferramenta. | A | D-046. Lugar provisório permitido pela D-442. | manter |
| 2 | "Os quatro filtros" saiu da trilha (o painel Filtro faz o mesmo). | A | R9 403 B · D-181. | manter |
| 2 | Caixinhas com quadrado à vista, marcadas e desmarcadas. | A | D-028 (O1). | manter |
| 3 | Abre direto na área de trabalho (0,7 s em vez de 139 s); painel Automático e janela grande; opções da tela "O que fazer" no Automático; receitas; "Receita usada" no livro aberto; pergunta das mexidas. | A | D-002 · D-003 · D-004 · D-005 · D-068 · D-069 · D-284 · decisão 2 (receitas) · rascunho R5/R6 ("Para revisar", "Receita usada"). | manter |
| 4 | Dividir, não dividir e mover a linha de UMA folha, sem recomeçar; Righetti girado divide. | A | Pedido da sessão 1 (26/10) · D-080 · D-074 · lista 3.1. | manter |
| 9a | "imprimir agora..." pede impressora, páginas, cópias e confirmação. | A | D-012 "2" (consertar na etapa 9). | manter |
| 9a | "Montar para imprimir" em duas colunas, sem nada por cima; nenhuma opção saiu. (Os **nomes** trocados estão em C.) | A | `fr-26` "Só tem que melhorar esse layout" · D-333 · D-315. | manter (ele confere de olho) |
| 9a | A rodinha só muda número e lista depois de clicar (programa todo). | A | Teste do Kaique: o campo passou de 100% para 60% sozinho (defeito). | manter |
| 9a | Janelas de abrir/salvar em português (a do Windows; a do Qt traduzida quando a do Windows não pode). | A | D-301 (lembrar a última pasta, avisar em português). | manter |
| 9c | "Deixar a folha em branco" e "pintar de branco" saem brancos no Original. | A | D-027 · D-227. | manter |
| 9c | `projeto.json` que não dá para ler: cópia guardada e aviso. | A | D-342. | manter |
| 9c | "Parece em branco" falso some quando a página tem texto; beirada do livro não conta. | A | D-271 · D-288 · D-254. | manter |
| 9c | "Menor que o corte" com os dois números iguais não aparece mais. | A | Lista de bugs 02/10 (defeito). | manter |
| 9c | Textos do núcleo: "o do Editor", singular/plural, acentos. | A | D-479/907 · D-365. | manter |
| 10a | O corte não come a página: Cursus 3, Escola 197 (números da margem), folha quase em branco não vira tira, a caixa não parte letra, corte alargado nunca menor, "Corte encostou" medido no corte de verdade. | A | D-077 "não comer conteúdo" · D-104/D-466 · D-098. | manter (ele vê na conferência da 10a: `relatorios/obra-etapa10a/conferencia/conferencia-etapa10a.html`) |
| 10a | Fio e faixa escura da beirada saem; cunhas do giro com a cor do papel; tracejado da beirada (Horas 18) não conta. | A | D-095 (cunhas, ressalvas do G6) · D-097 "não pode ter preto ali". | manter |
| 10a | Moldura do scanner pintada de branco só na conta do desentortar. | A | D-113 "tirar essa moldura preta [...] ai o desentortador não iria confundir". | manter |
| 10b | 4.1 gravura sem blocos pretos; 4.3 folha de guarda sai branca; 4.11 mancha redonda não vira bola preta; 4.12 grão laranja some (e os pontinhos atrás da estátua do Opus 20). | A | D-118 "o papel saia branco, e o desenho também saia perfeito" · D-126 · X2 (02/10) "esses pontos estão horriveis atras da estatua". | manter |
| 10b | Sombra da lombada (Matemática 40 e 66) e sombra de foto de celular não viram mancha preta no Preto e branco. | A | D-154 "nenhuma letra some" · D-107 (fotos). | manter |
| 10b | 4.7 Pesel: o cartão em volta da gravura sai como escaneado (sem retângulos brancos). | A | Defeito (lista 4.7). Ressalva: D-126 pede "todo o papel totalmente branco"; o cartão escuro não é o papel da página. | manter; mostrar a ele de olho |
| 10b | T do Antiphonal 46 igual na tela e no PDF; tela cheia com a grossura do PDF; "Reduzir cores" não apaga letra. | A | D-278 · D-193/D-066 "precisamos que o pdf saia que nem está na tela" · D-189 "Ele está apagando as letras". | manter |

---

## Fora da tabela (processo, não muda o programa)

- **Donos das 37 decisões "sem dono"** (Livro, seção "Sem dono antes desta revisão", escolha da gerente na etapa 0):
  várias foram para "depois da obra" (ex.: D-034, D-122, D-138, D-164, D-224, D-235, D-438). A maioria segue o que o
  plano já dizia, mas a D-388 diz que **só ele escolhe a fase**. Recomendo mostrar a lista a ele de uma vez, sem uma
  pergunta por item.
- **D-466 no conjunto da 10a/10b:** ele pediu "primeiro provar em páginas de verdade, depois decidir". Os agentes
  provaram e já consertaram (com a D-014 autorizando fazer e conferir no fim). Os consertos estão em A porque fazem o
  "não comer" funcionar; só o aviso novo da impressão ficou em B. A conferência da 10a e da 10b mostra as fotos.

## Ressalvas

1. Nada foi conferido por máquina nem por olho: é leitura do Livro, dos relatórios e do código. Itens A podem ainda
   estar **mal feitos** (isso é o verificador de cada etapa); aqui só se diz se a escolha **respeita** o que ele decidiu.
2. Várias decisões dele estão no Livro como paráfrase da fonte (ex.: D-033, D-334). Onde a paráfrase decide a classe
   (C do lado direito e da grade), conferi a fonte: o rascunho do layout (linhas 187, 783, 806, 814) confirma os quatro
   jeitos; a D-334 não tem as palavras literais dele.
3. As decisões D-502 a D-519 e D-533 a D-539 não existem no Livro (números pulados). A etapa 6 (D-580+) e a 9d
   (D-560+) estão em andamento e não entraram nesta auditoria.
4. O JPEG 92 da D-531 ainda está no código da obra (`core/pdf_io.py:379`); a D-549 manda desfazer na etapa 9d.
