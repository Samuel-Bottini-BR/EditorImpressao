# ONDE PAREI: gravura procurada no Preto e branco escolhido à mão (D-659)

Ramo `gravura-a-mao-2026-11-09` (saiu de `obra-2026-10-26`, ponta `a0c99cc7`). Worktree
`D:\programas\EditorImpressao\.claude\worktrees\gravura-a-mao`. Agente: implementador.

## O defeito (Samuel, 09/11/2026, sessão 4)

Livro novo, que nunca passou pelo Automático. Na área de trabalho, painel "Filtro da página", ele
escolhe Preto e branco na página 8 (gravura grande em cima, texto embaixo), com "Respeitar as gravuras
achadas" e "Gravuras em tons de cinza" marcadas. A gravura sai em manchas pretas (a página inteira
vira preto e branco). Na janela do Automático, a mesma página sai certa (gravura em tons de cinza).
Palavras dele: "isso é um grande erro". Prints: `relatorios/testes-guiados/2026-11-09-sessao-4/prints/`
01 (errado) e 02 (certo), no `fase-1`.

Causa (conferida por mim em 09/11, com o código do `a0c99cc7`): `core/etapas.marca_sozinho` devolve
`False` na primeira linha quando "Limpar a folha" está desligado (`limpa_sozinho`), antes de chegar em
`procura_por_dentro`. Então `core/pipeline.garantir_selecao` devolve só a marcação feita à mão (vazia)
e nenhuma gravura é procurada. Conferido: com a página em Preto e branco à mão e o cinza marcado,
`cinza_procura` = True, `marca_sozinho` = False. Por que passou: as provas de
`tests/test_decisoes_gravuras_cinza.py` e `tests/test_decisoes_respeitar_gravuras.py` começam todas
com `_depois_do_automatico` (Limpar a folha ligado).

## Decisões que esta tarefa precisa cumprir

- **D-659 (09/11/2026)**: "1- ele vai procurar a gravura quando eu selecionar a opção ali no filtro né? e
  ai se eu selecionar para o livro todo ou para varias paginas, ele vai procurar nas paginas
  especificas, não precisa procurar em todas." e "2- No caso de a opção ter sido selecionada sim, vai
  procuar na pagina que está ou nas paginas que foram selecionadas entendeu?"
  Na prática: no Preto e branco escolhido à mão (sem o Automático), "Respeitar as gravuras achadas",
  "Gravuras em tons de cinza" e "Só as letras", quando marcadas, fazem o programa procurar a gravura
  sozinho, só nas páginas onde a opção vale. A etapa 5 do Automático ("Gravuras e fotos") continua
  desmarcada.
- **Esclarecimento da D-659 (09/11/2026, pela gerente)**: "se estamos no manual e eu estou fazendo
  ajustes em uma pagina, ele vai procurar só naquela pagina se eu optar para que ele faça aquele ajuste
  em varias paginas ai sim o programa vai ler as outras paginas, entendeu? isso para as duas opções."
  (as duas opções = "Respeitar as gravuras achadas" e "Gravuras em tons de cinza"). Nada de procurar
  no livro todo por conta própria (nem por trás, nem antecipado). O "Só as letras" segue a mesma regra
  (D-589, "procura as figuras por dentro"). Prova pedida: contar quantas páginas foram procuradas em
  cada caso.
- **D-583 (29/10)**: "Precisamos da opção de jogar o filtro em cima de outro filtro ou só substituir o
  filtro que está colocado em cima." → "c" (caixinha que diz se o filtro respeita ou não as gravuras
  achadas). A D-659 muda a D-583 só no "Depois do Automático": agora também sem ele.
- **D-586 (29/10)**: "A" — caixinha "Respeitar as gravuras achadas", ligada de fábrica; "Desligada, o
  filtro vale na página inteira"; "Vale com o "Aplicar em"".
- **D-588 (01/11) e conserto de 02/11**: "Gravuras em tons de cinza" — "Marcada, toda gravura achada sai
  cinza"; "por gravuras em tons de cinza sozinho já deveria resolver o problema." → "sim pode" ("ela acha
  as gravuras sozinha e pinta de cinza, com o "Respeitar" ligado ou desligado").
- **D-589 (31/10) e P4 de 02/11**: "Com 'Só as letras' marcada, o programa procura as figuras por
  dentro, só para deixar elas coloridas." / "tem que ter certeza que o programa vai procurar as figuras
  mesmo com a opção desmarcada e que não vai remarcar ela de novo na caixinha" / P4: "A: o cinza procura
  as figuras por conta própria, só para pintá-las de cinza, e a etapa 5 continua desmarcada." → "a".
- **D-009 (26/10)**: "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo
  manualmente." (a marcação feita à mão vale com o automático desligado).
- **D-605 (03/11)**: "nenhuma função nova, ou nova escolha dentro do programa pode alterar o que já está
  escolhido e testado, coisas novas não podem criar novos problemas".
- **D-637 (05/11)**: "pensar na experiencia do usario e no resultado final do livro dentro do programa,
  quando vai mudar algo, deixe isso anotado."

## O que já está escolhido e testado aqui (D-605)

Arquivo que vou tocar: `core/etapas.py` (`marca_sozinho`, `procura_por_dentro`, uma função nova para a
"Respeitar"). Ninguém mais muda: `core/pipeline.py` já pergunta tudo a `etapas` (não pretendo mexer).
`ui/` não muda.

- Com "Limpar a folha" ligado (o Automático rodado, no livro ou só na página): a procura acontece com
  "Procurar gravura e letra" (`detectar_regioes`) ou com "Só as letras"/cinza procurando por dentro.
  Provas: `tests/test_decisoes_respeitar_gravuras.py` (D-583/D-586/D-587, todas depois do Automático),
  `tests/test_decisoes_gravuras_cinza.py` (D-588 e conserto de 02/11), `tests/test_decisoes_montar_cadernos.py`
  (D-589 e P4: etapa 5 desmarcada, "Só as letras"/cinza procuram; sem eles a página sai toda em P&B),
  `tests/test_decisoes_so_as_letras.py`.
  **Isso não pode mudar**: a função nova só vale com "Limpar a folha" desligado.
- Filtro escolhido à mão sem "Limpar a folha" (D-009): o filtro vale; a marcação à mão vale.
  Provas: `tests/test_decisoes.py` (`test_d009_*`, inclusive `test_d009_filtro_da_pagina_com_limpar_a_folha_desligado_sai_no_pdf`
  e `test_d009_filtro_do_livro_trocado_depois_nao_filtra_com_limpar_desligado`), `tests/test_decisoes_nucleo.py`.
- Projeto antigo (gravado antes da obra, `feito_a_mao_sempre_vale` False, sem as marcas): sai igual
  (`tests/test_decisoes.py`, `_como_projeto_antigo`; `test_d586_projeto_antigo_abre_ligado_e_sai_identico`;
  `test_d588_projeto_antigo_abre_desmarcado_e_sai_identico`).
- "Respeitar" desligada = filtro na página inteira (D-586): continua (a página desligada não é
  procurada, e `pipeline.marcacao_que_o_filtro_usa` já tira o que a máquina achou).
- A "corrida com a tela" (`pipeline.garantir_selecao`): marcação à mão feita durante a procura vale; a
  marcação à mão volta por cima. Não mexo nessa função.
- Livro novo de fábrica, sem nada escolhido (D-009/D-284, prova "Desligado de fábrica"): página no
  Original, sem a marca FILTRO → `filtro_que_vale` = Original → nenhuma procura. Continua.
- A etapa 5 do Automático continua desmarcada (`core/automatico.ligada_no_livro` lê só `detectar_regioes`).

## Como fica para quem usa e no livro (D-637, §11.9)

O Kaique abre um livro novo (sem rodar o Automático), vai à página 8, abre o painel "Filtro da página"
e clica em Preto e branco. A caixinha "Respeitar as gravuras achadas" já vem marcada (de fábrica).
- Agora: o programa procura a gravura **só nessa página** (leva cerca de um segundo, igual ao
  Automático; a prévia aparece primeiro e é trocada pela definitiva por trás, como já acontece depois do
  Automático) e a gravura sai como no Automático (print 02). Com "Gravuras em tons de cinza", a gravura
  sai cinza; com "Só as letras", a gravura sai como no original.
- Se ele clicar em "todas" ou "daqui em diante", as outras páginas recebem o Preto e branco com as
  caixinhas, e cada uma é procurada **quando for desenhada** (ao aparecer na tela ou ao gerar o PDF);
  páginas fora do "Aplicar em" nunca são procuradas.
- Se desmarcar as três, a página sai como hoje: toda em preto e branco.
- Melhorar, Mágico pro e Original escolhidos à mão: nada muda.
- No PDF: a página sai igual à tela (o mesmo caminho do desenho).
- A caixinha "Gravuras e fotos" do Automático continua desmarcada.

## Plano do conserto

1. Função nova em `core/etapas.py`, `respeitar_procura(projeto, pagina)`: página em Preto e branco
   escolhido à mão (marca FILTRO), "Limpar a folha" desligado nela, e "Respeitar as gravuras achadas"
   marcada.
2. `procura_por_dentro` passa a incluir `respeitar_procura`.
3. `marca_sozinho`: com "Limpar a folha" desligado, em vez de `False`, devolve `procura_por_dentro`
   (só com a página; sem a página, `False` como hoje).
Com "Limpar a folha" ligado nada muda (a função nova exige ele desligado; o "Só as letras" e o cinza já
valiam com ele ligado).

## Andamento

- [x] Causa conferida (09/11).
- [x] Provas novas (`tests/test_decisoes_gravura_a_mao.py`, 15), commit `ca7d2468`.
- [x] Reversão: com `core/` igual ao `a0c99cc7`, 11 falham e 4 ("nada muda") passam
  (`reversao-no-a0c99cc7.txt`).
- [x] Conserto, commit `88731637` (`core/etapas.py`; e `core/pipeline.py`, o defeito da tela achado no caminho).
- [x] Testes no PC, um arquivo por vez (lista abaixo).
- [x] GitHub: suítes 42698444393 e 42703188133 vermelhas só no `test_promessas.py` (ver abaixo). Filtro de
  velocidade 42698450173 "igual" (mediu o `88731637`, antes da correção da corrida).
- [x] Corrida "procura sem resolução" (achada no GitHub), commit `f3b97c03`.
- [x] Autorização do Samuel (09/11, "1- sim") às duas propostas: `ui/tarefas.py` (`45d56991`, com prova) e
  `test_p195` (`0f947c0a`). No PC, sem janela: `test_promessas.py` 268 passaram; `test_decisoes_gravura_a_mao.py`
  17; `test_marcacao_por_tras.py` 4; `test_decisoes_9b2.py` 30.
- [x] GitHub depois da autorização (ramo em `59bc58d7`): **suíte 42723078970 verde** (as 5 partes e os botões).
  **Filtro de velocidade 42723083592: "igual"** (`a0c99cc7` x ramo; trocar de página -1,3%, Preto e branco 10
  páginas +0,6%, Mágico pro -1,5%, abrir -0,5%; tudo dentro do vai-e-vem).
- **PARADO aqui** (09/11): falta só a resposta do Samuel à pergunta 1. Não junto nada à obra (é da gerente).
- [x] Prova da pergunta 2 (sem janela), commit `5e43ab04`: ver "Prova da pergunta 2" abaixo.
- [x] Imagens do livro dele (cópia, sem janela) e relatório (`relatorio.md`/`.html`/`.pdf`), commit `a99e0a51`.
- [-] Prints da janela real: **tirados do pedido** (ordem do Samuel, 09/11: "não é para abrir na minha tela").
  O script abriu a janela duas vezes por volta das 17h, antes da ordem (só o print da página 8 no Original saiu).
  Os dois processos terminaram sozinhos; o script e o print foram apagados. Os testes do pytest sempre rodaram
  sem janela (`tests/conftest.py` põe `QT_QPA_PLATFORM=offscreen`; `EDITOR_TESTES_COM_TELA` não está definida).

## O que mudou no código

1. `core/etapas.py`:
   - `respeitar_procura` (nova): Preto e branco escolhido à mão, "Limpar a folha" desligado e "Respeitar" marcada.
   - `procura_por_dentro` passa a incluir a nova.
   - `marca_sozinho`: sem "Limpar a folha", devolve `procura_por_dentro` da página (antes, `False`). Com
     "Limpar a folha", a conta de antes.
2. `core/pipeline.py`, `acertar_no_tamanho_do_pdf`: no caso "só trocar a marcação provisória", a folha crua tem
   nome próprio (`crua`) e não é mais devolvida como "a imagem do PDF". Defeito do `4f881001` (etapa 9b-2): o nome
   `grande` era usado duas vezes, e a tela trocava a prévia certa pela folha crua, sem corte nem filtro. Ele
   impedia a tarefa: com o conserto, o clique no Preto e branco deixava a tela no Original. Atingia também
   páginas depois do Automático com o cinza e a etapa 5 desmarcada (P4). A docstring sempre disse "ou None
   nas outras". Prova: `test_d659_a_tela_nao_troca_a_previa_pela_folha_crua`.

## Como cumpri cada decisão

- **D-659 e o esclarecimento**: procura só na página da opção. Provas `test_d659_a`, `_b`, `_c` contam as páginas
  procuradas: só a da tela, inclusive depois de andar pelas outras e ao gerar o PDF. `test_d659_d` ("todas" e
  "daqui em diante") procura só nas alcançadas. `test_d659_e` (página 1 e 3 escolhidas) procura só nelas. Página
  8 do livro dele: `relatorio.html`, seções 1 a 4.
- **D-586 (desligada = página inteira)**: `test_d659_f`, igual byte a byte ao código de antes, nenhuma procura.
  Imagem da seção 5 (igual ponto por ponto).
- **D-588 / conserto de 02/11 (o cinza sozinho basta)**: `test_d659_b` e a imagem da seção 2.
- **D-589 / P4 (etapa 5 não volta marcada; "Só as letras" procura por dentro)**: `test_d659_a` e `test_d659_i`
  conferem `automatico.ligada_no_livro(GRAVURAS)` desligada. `test_d659_c` e a imagem da seção 4 mostram a
  gravura como no original.
- **D-009 (marcação à mão vale)**: não mexi em `garantir_selecao` nem na corrida com a tela;
  `test_garantir_selecao_corrida.py` e `test_decisoes.py` passam.
- **D-605 (nada do testado muda)**: com "Limpar a folha" ligado, a conta é provada igual à de antes
  (`test_d659_a_conta`, `test_d659_i`). Os arquivos de teste antigos passam (lista abaixo), e a suíte roda no
  GitHub.
- **D-473 / D-020**: `test_d659_h_o_pdf_sai_como_a_tela` e `test_d659_h_ctrl_z_desfaz_e_ctrl_shift_z_refaz`.
- **D-637**: "Como fica para quem usa e no livro" (acima), conferido com as imagens e os tempos.

## Testes no PC (um arquivo por vez, sem janela)

Ver `saida_teste/gravura-a-mao/testes-no-pc.txt` (fora do git). O resumo vai no relatório à gerente.

## Ressalvas e pontos a conferir

1. **"pares / ímpares" e "escolhidas na grade" não existem para o filtro.** O "Aplicar em" do painel
   "Filtro da página" tem só "só nesta / todas / daqui em diante" (`ui/tela_conferir.py`,
   `_filtro_em_todas` e `_filtro_nas_proximas`); a tela cheia dos filtros tem "todas / daqui". A grade
   "ver todas" tem girar, dividir, deixar em branco, tirar, trazer, extrair e rodar o Automático, mas
   não "pôr filtro". Pares/ímpares existem só no girar (D-636). Pela regra "Só o que ele mandou" não
   crio botão novo. A conta nova é por página: vale para qualquer grupo de páginas que um dia receba o
   filtro. As provas (d) e (e) cobrem "todas" e "daqui em diante" pela tela e "várias escolhidas" pela
   conta (páginas postas em Preto e branco à mão uma a uma).
2. **Projetos gravados depois de 26/10 com página em Preto e branco à mão e "Respeitar" marcada** (a
   caixinha vem ligada de fábrica) passam a sair com a gravura achada ao abrir de novo: é o conserto
   (o defeito das manchas). Projeto gravado antes da obra (sem a marca FILTRO) sai igual.
3. **Página procurada à mão e depois o Automático**: a marcação achada fica guardada e acompanha o papel
   (zonas na folha, D2 de 02/10) se o Automático cortar ou endireitar. Não é procurada de novo, como toda
   página já procurada. A prova `test_d659_i` confere a conta igual à de antes. Ela não compara com um livro em
   que a página nunca foi procurada: lá o Automático procuraria do zero, no papel já cortado.
4. **Depois do Automático com "Limpar a folha" e sem "Gravuras e fotos"**, a página com só a "Respeitar" volta a
   sair toda em preto e branco: é a D-589 ("sem 'Só as letras' e com Gravuras desmarcada, a página sai toda em
   preto e branco"). A D-659 fala de "sem o Automático". Não mudei isso. Pergunta abaixo.
5. **Página sem gravura com "Respeitar" (de fábrica)** também é procurada (cerca de 2 s no tamanho do PDF). Na
   página 6 do livro dele, o texto saiu igual e só uma marca do scanner no canto de baixo quase sumiu (261
   pontos de 7 milhões). É a mesma conta do Automático.
6. **No livro novo o `detectar_regioes` vem True de fábrica** (só o "Limpar a folha" é desligado pelo
   `livro_leve`). A procura nova NÃO usa esse campo sem o "Limpar a folha"; senão toda página em qualquer filtro
   seria procurada.
7. A procura no programa de verdade roda em outro processo (`core.paginas_em_outro_processo`). Na única
   execução com janela, a página 8 ficou com a gravura achada: 25 áreas, marcação definitiva.

## (RESOLVIDO em 09/11: aplicado com o "1- sim" do Samuel) Teste antigo que a D-659 quebrava

Rodadas do GitHub 42698444393 e 42703188133 (e o mesmo no PC): tudo verde, menos `tests/test_promessas.py`
(268 passavam no ramo de base, rodada 42391132998).

1. **`test_p195_antes_depois`** (falha): ele clica em Preto e branco na página 2 de um livro novo, tira a foto
   do projeto na hora e, depois de abrir e fechar o "antes / depois", compara com a de agora. No meio, a procura
   da D-659 (a "Respeitar" vem marcada) grava na página a gravura e as letras achadas (`selecao`), e a
   comparação acusa. O "antes / depois" não mudou nada. Quem mudou foi a procura, que é o que a D-659 manda.
   Proposta (NÃO aplicada): `proposta-test_p195.diff`. A foto do "antes" espera a procura terminar, e o
   resto da prova fica igual.
2. **24 a 27 erros "um botão falhou por baixo (erros.log)"** em testes que não têm nada de errado. Eles caem
   sempre no teste **seguinte** a um que pôs uma página em Preto e branco à mão. Mecanismo: a troca da marcação
   no tamanho do PDF (por trás) leva mais de 3 s na primeira vez, porque carrega o detector. O
   `GerenciadorPrevias.parar()` espera só 3 s. Quando o resultado chega, `refazer_previas` pede prévias novas
   ao gerenciador já parado, do PDF do teste anterior, que já foi apagado. O erro vai para o `erros.log` do
   teste seguinte. No programa de verdade, isso também desenha por trás páginas do livro anterior depois de
   trocar de livro, e dá erro se a pessoa moveu o PDF (caso que o próprio `parar()` já cita).
   Proposta (NÃO aplicada, é `ui/`): `proposta-ui-tarefas-parar.diff`. Depois do `parar()`, o gerenciador
   não começa nada novo. O gerenciador não é reaproveitado: `janela_principal` cria outro para cada livro.
   Experimento no PC, sem commit: ver "Resultado do experimento" abaixo.

Resultado do experimento (PC, sem janela; desfeito depois, `ui/tarefas.py` igual ao do ramo):
- `test_promessas.py` com o conserto e SEM as propostas: 1 falha (`p195`) + 24 erros (igual ao GitHub).
- Com a proposta de `ui/tarefas.py` aplicada: **1 falha (`p195`), 267 passaram, 0 erros**.
- `test_p195` com a proposta dele (numa cópia temporária do arquivo, apagada depois): **passou**.

Pergunta: posso (a) aplicar a troca do `test_p195` e (b) a mudança em `ui/tarefas.py`? Sem as duas, a suíte do
GitHub fica vermelha só no `test_promessas.py`.

## Prova da pergunta 2 (pedido da gerente, 09/11; sem janela, pela conta do programa)

Script `prova_pergunta2.py`, numa cópia do *Na escola de Jesus*, página 8. Medidas em `imagens/q2-medidas.json`.
Imagens com a página inteira e a gravura de perto, no mesmo enquadramento.
- **(A)** Preto e branco à mão, "Respeitar" marcada: a gravura em tons de cinza (`imagens/q2-a-a-mao.jpg`).
  Procurou 1 vez, 25 áreas achadas.
- **(B)** depois o Automático do print 02 (só "Limpar a folha", Preto e branco; as outras etapas desmarcadas,
  "Gravuras e fotos" incluída), respondendo **"Rodar nelas também"** à pergunta da página mexida (o Automático
  pergunta pela página 8): **manchas pretas** (`q2-b-depois-do-automatico.jpg`). A gravura achada continua
  guardada na página (25 áreas), mas não vale: "Limpar a folha" ligado, etapa 5 desligada (D-589). O
  "Rodar nelas também" tirou a marca FILTRO da página. O Automático levou 31 a 41 s (só Limpar).
- **(C)** como B, com "Gravuras em tons de cinza" marcada na página: **igual à (A), ponto por ponto**, sem
  procurar de novo (usa a gravura guardada) (`q2-c-com-cinza.jpg`).
- **(D)** como B, respondendo **"Pular"**: **NÃO sai igual à (A)**. Também sai em manchas, igual à B
  (`q2-d-pulou.jpg`, 2,18 milhões de pontos diferentes da A). Causa: o "Pular" deixa a página como estava
  (a marca FILTRO fica, o filtro fica), mas "Limpar a folha" passa a valer no livro todo, e a procura da D-659
  (`respeitar_procura`) só vale com "Limpar a folha" desligado. Com isso, a "Respeitar" volta à regra de
  depois do Automático (D-589).
- **Tempo, se a "Respeitar" sozinha também procurasse depois do Automático:** a procura leva **2,5 s por
  página** (9 páginas espalhadas, 300 DPI, PC sem outros testes; de 2,1 a 2,7 s). Em 199 páginas, cerca de
  **504 s (8,4 min) a mais**. Isso não aconteceria dentro do "Rodar" do Automático, e sim ao gerar o PDF e ao
  olhar cada página, porque a procura é feita quando a página é desenhada.

### Investigação (sem mudar código): no "Rodar nelas também", usar a gravura já achada naquela página?

Dá, mas precisa de uma marca nova na página. Hoje, depois do "Rodar nelas também", nada distingue a página 8
de uma página cuja gravura foi achada antes por um Automático com "Gravuras e fotos" ligada e depois
desligada. As duas têm a marcação da máquina guardada e a assinatura (`gravura_feita_com`). E o "Rodar nelas
também" tira a marca FILTRO (`core/automatico._ligar_na_pagina`).
- **Onde mexeria:**
  1. `core/pipeline.garantir_selecao`: ao procurar por causa da D-659 (`etapas.respeitar_procura`), gravar na
     página uma marca nova (ex.: `ConfigPagina.gravura_achada_no_filtro_a_mao = True`).
  2. `modelos.py`: o campo novo, que vai para o `projeto.json`. Isso muda o formato do arquivo de dados, o que
     pede pergunta (CLAUDE.md §6).
  3. `core/etapas.respeitar_procura`: com "Limpar a folha" ligado, valer só se a página tiver essa marca e a
     "Respeitar" marcada. Aí a marcação guardada vale (`a_marcacao_da_maquina_vale`) e `garantir_selecao`
     devolve a guardada sem procurar. Nenhuma outra página é procurada, porque nenhuma outra tem a marca.
  4. Para o "Pular" ficar igual à (A), basta o mesmo item 3 (a página pulada guarda a marca FILTRO e a
     marcação).
- **Riscos:**
  - (a) formato do `projeto.json` (campo novo; projeto antigo abre sem ele, de fábrica `False`, e sai igual);
  - (b) a D-589 ("sem 'Só as letras' e com Gravuras desmarcada, a página sai toda em preto e branco") ganha
    uma exceção para essas páginas; o Samuel precisa aceitar isso;
  - (c) a página é procurada de novo, só ela, se a marcação guardada ainda for a provisória (nunca desenhada
    no tamanho do PDF) ou se as opções de gravura mudarem (assinatura);
  - (d) se o Automático cortar ou endireitar a página, a marcação acompanha o papel (D2), como hoje;
  - (e) usar só a assinatura, sem a marca nova, mudaria o que a `test_d589_3_*` e a P4 provam (páginas com
    gravura de um Automático anterior também voltariam a guardar a cor).

## Perguntas para o Samuel

1. (Ressalva 4; a gerente está refazendo a pergunta com a prova acima, não mexer.) Você escolhe Preto e
   branco à mão na página 8 (a gravura sai certa) e **depois** roda o Automático com "Limpar a folha", mas sem
   "Gravuras e fotos". Hoje a página 8 volta a sair toda em preto e branco, como manda a D-589, tanto no
   "Rodar nelas também" quanto no "Pular" (imagens q2-b e q2-d). Com "Gravuras em tons de cinza" ela fica
   certa (q2-c).
