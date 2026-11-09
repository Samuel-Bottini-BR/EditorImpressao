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
- [ ] Provas novas (`tests/test_decisoes_gravura_a_mao.py`).
- [ ] Reversão no `a0c99cc7`.
- [ ] Conserto.
- [ ] Testes no PC, um arquivo por vez.
- [ ] GitHub (suíte) e filtro de velocidade.
- [ ] Imagens do livro dele (cópia) e relatório.
- [ ] Prints da janela real.

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
