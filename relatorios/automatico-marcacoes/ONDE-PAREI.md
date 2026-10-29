# Automático: botão "marcações" na barra de baixo (D-578, D-580) — ONDE PAREI

Ramo `automatico-marcacoes-2026-10-29` (saiu de `obra-2026-10-26`, commit `ac0b9ec`).
Worktree `D:\programas\EditorImpressao\.claude\worktrees\auto-marcacoes`. Agente de tela, 29/10/2026.

## Decisões que esta tarefa precisa cumprir

(escrito antes de começar a mexer no código)

- **D-578** (29/10/2026): "um bug que acontece quando nós usamos o automatico, de vez as paginas mudarem, elas
  continuam iguais, mas o que aparece são as marcações feitas no pdf, de gravura e de letras, tem que ter um jeito de
  aparecer e desaparecer essas marcações nas paginas." · "não tem nenhuma opção de marcação escolhida, está o zoom
  escolhido". Na prática: depois do Automático, a página deve aparecer como vai sair, não coberta de cores.
- **D-580** (29/10/2026): "A" — "A — Na barra de baixo, começando escondido. O botão "marcações" fica ao lado de "Uma
  página / Duas lado a lado / antes / depois". Com qualquer ferramenta, até com o Zoom, a página aparece limpa, como vai
  sair. Um clique mostra as cores e outro esconde." Na prática: botão de ligar/desligar chamado "marcações" na barra de
  baixo, mesmo estilo dos vizinhos; de fábrica desligado; desligado = sem o colorido e sem o contorno das feitas à mão,
  com qualquer ferramenta; ligado = como hoje. Vale enquanto o programa está aberto (todas as páginas e livros); volta a
  desligado ao abrir o programa; nada gravado no projeto, nada muda no PDF.
  Detalhes fixados pela gerente: o traço que está sendo desenhado continua aparecendo; o contorno laranja da caixinha
  "Mostrar as áreas achadas" e o laranja das páginas do "Para revisar" continuam com as regras deles; a caixa da área
  escolhida pela ferramenta Ajustar continua.
- **D-237** (06/10 e 08/10/2026): "mas quando eu quiser ver as areas achadas, deve ter um botão ou aba para eu fazer
  isso, apertar nele e mostrar as areas achadas delineadas, no para revisar, elas já vão aparecer laranjas [...]" —
  não pode quebrar: o laranja continua aparecendo, com "marcações" ligado ou desligado.
- **D-278 / D-279** (09/10/2026): o lugar onde sumiu já marcado em laranja no aviso do "Para revisar" — não pode quebrar.
- **D-010** (26/10/2026): "eu acho que o botão tem que ser provado que ele faz o que se diz que se faz, e não só se ele
  muda algo na tela." — o botão novo ganha promessa escrita em `tests/promessas/promessas.md` e prova em
  `tests/test_promessas.py`.
- **D-001** (25/09/2026): "Estrutura: Photoshop puro, sem abas. Uma única tela com todas as ferramentas." — nada sai
  de vista; o botão novo só acrescenta à barra de baixo.
- **D-584** (29/10/2026, resposta "a" à pergunta 1 deste ONDE-PAREI): "A — O botão liga sozinho ao escolher uma
  ferramenta de marcar (Retângulo, Laço, Pincel, Varinha...) e desliga sozinho ao voltar para o Zoom ou a Mão. Quem
  marca sempre vê o que está marcando; quem só olha a página vê ela limpa." Detalhes da gerente: o clique no botão
  continua valendo a qualquer hora (desligado com o Pincel na mão, fica desligado até trocar de ferramenta de novo);
  ao abrir o programa/livro continua desligado. (Escrito antes de mexer no código, na segunda rodada.)
- **§11 regra 7** ("Só o que ele mandou"): nada além do nome "marcações" e de um balão de uma frase. Sem atalho, sem
  menu, sem aviso.

## O que mudou

- `ui/widgets/editor_selecao.py` (a vista da página: Zoom, Mão e as ferramentas de marcar)
  - `EditorSelecao.__init__`: `mostrar_marcacao` passa a começar **desligado** (era sempre ligado e ninguém mudava).
  - `definir_mostrar_marcacao(mostrar)` (nova): liga/desliga e repinta.
  - `paintEvent`: o colorido e o contorno das feitas à mão (`_pintar_marcacao`) só com "marcações" ligado; o laranja
    das áreas achadas e a caixa da área escolhida (`_pintar_achadas_e_escolhida`) saíram de dentro de
    `_pintar_marcacao` e são pintados sempre que as regras deles pedem; as marcas do aviso do "Para revisar" e o traço em
    andamento já ficavam fora e continuam.
- `ui/tela_conferir.py` (barra de baixo)
  - `_montar_o_ver_da_barra_de_baixo`: botão `botao_marcacoes`, texto "marcações", logo depois do "antes / depois",
    mesmo jeito dos vizinhos (`objectName` `jeitoDaBarraDeBaixo`, marcável, sem foco, cursor de mão). Balão: "Mostra ou
    esconde as cores das marcações (gravura, letras, papel) por cima da página."
  - `_alternar_marcacoes` (nova): passa o estado do botão para o editor. Nada é gravado (nem projeto, nem histórico,
    nem configurações): o botão é um só enquanto o programa está aberto e volta a desligado ao abrir o programa.
  - `_montar_aba_marcar` (2ª rodada): o editor da página **nasce de novo a cada livro aberto**; agora ele já nasce
    seguindo o botão. Na 1ª rodada eu tinha escrito que "a tela é uma só", e por isso o estado valia para os livros:
    estava errado. No `abbb0d3`, com o botão aceso, o livro seguinte abria sem as cores embaixo do botão aceso. Achei
    na 2ª rodada; a prova é `test_d580_d584_abrir_outro_livro_o_editor_novo_segue_o_botao`.
  - `escolher_ferramenta` -> `_marcacoes_pela_ferramenta` (nova, D-584): escolher uma ferramenta de marcar acende o
    botão; o Zoom ou a Mão apagam. `escolher_ferramenta` é o ponto único de troca (trilha, menu Ferramentas, letras do
    teclado e o nome antigo `_escolher_ferramenta` passam por ele). As ferramentas de página (Dividir, Cortar...) não
    mexem no botão. Abrir um livro não passa por ali (a ferramenta de partida vai direto para o editor), então ao abrir
    o botão fica como estava.
- `ui/widgets/editor_selecao.py` (2ª rodada): `FERRAMENTAS_DE_MARCAR` = todas as `FERRAMENTAS` menos as de navegação
  (Retângulo, Elipse, Laço, Polígono, Pincel, Varinha, Escolher por cor, Ajustar).
- `tests/test_decisoes_marcacoes.py` (novo): as provas (abaixo).
- `tests/promessas/promessas.md`: promessa **P-197** · "marcações" (barra de baixo). `tests/test_promessas.py`:
  `test_p197_marcacoes`.
- `tests/test_decisoes_9b2.py` (`test_lista_1_9_...`): a prova da lista 1.9 (o contorno da área feita à mão) agora liga
  "marcações" antes de olhar, porque desde a D-580 esse contorno só aparece com o botão ligado. A conferência dela não
  mudou.

## Como cumpri cada uma

| Decisão | Como ficou | Prova |
|---|---|---|
| D-578 | Depois do Automático a página aparece limpa: as cores não cobrem mais a página. | `tests/test_decisoes_marcacoes.py::test_d578_d580_o_botao_marcacoes_da_barra_de_baixo` (livro aberto de verdade, ferramenta Zoom, conta os pixels coloridos pintados na página); print `marcacoes-1-desligado-de-fabrica.jpg` |
| D-580: botão "marcações" na barra de baixo, ao lado de "antes / depois", mesmo estilo | Botão "marcações" logo depois do "antes / depois", mesmo jeito dele (mesmo `objectName`, marcável). | o mesmo teste confere texto, lugar (mesmo pai do "antes / depois") e estilo; prints |
| D-580: começa escondido, com qualquer ferramenta, até o Zoom | De fábrica desligado; Zoom, Mão, Pincel, Retângulo, Varinha, Ajustar: página sem cores e sem o contorno das feitas à mão. | `test_d578_d580_com_o_zoom_...` e `test_d580_com_qualquer_ferramenta_a_pagina_aparece_limpa[mao/pincel/retangulo/varinha/ajustar]` (pixels) |
| D-580: um clique mostra, outro esconde; vale para todas as páginas; nada gravado | Ligado = como antes; desligado = limpa. Mudar de página mantém. A marcação das páginas e o projeto gravado não mudam. | `test_d578_d580_o_botao_...` (liga, muda de página, desliga, compara a marcação); P-197 em `test_promessas.py` (compara o `projeto.json` gravado antes e depois); print `marcacoes-2-ligado.jpg` |
| Detalhe da gerente: o traço em andamento continua | Continua (é pintado fora da chave). | `test_d580_o_traco_em_andamento_e_o_laranja_das_achadas_continuam` |
| D-237 / D-278 / D-279 | O laranja da caixinha "Mostrar as áreas achadas" aparece com "marcações" desligado; as marcas do aviso do "Para revisar" não passam pela chave. | `test_d237_com_marcacoes_desligado_a_caixinha_ainda_mostra_o_laranja` e o teste do traço (pixels laranja); `tests/test_para_revisar_na_tela.py` 26 passaram |
| D-010 | Promessa P-197 escrita e provada. | `tests/test_promessas.py`: 261 passaram, 1 xfail (o que já estava como "aguarda"); `test_todo_botao_tem_promessa` passou com o botão novo |
| D-001 | Nada saiu de vista. | `tests/test_decisoes_tela.py`: 35 passaram |
| D-584: ferramenta de marcar acende, Zoom/Mão apagam | Escolher qualquer uma das 8 de marcar acende o botão e mostra as cores; Zoom ou Mão apagam. O clique no botão continua: desligado com o Pincel, fica desligado (até mudando de página) até trocar de ferramenta. | `test_d584_pincel_liga_zoom_desliga_e_o_clique_ainda_esconde` (pixels), `test_d584_toda_ferramenta_de_marcar_liga_e_a_mao_desliga[8 ferramentas]`; P-197 atualizada e provada; print `marcacoes-3-pincel-acende-sozinho.jpg` |
| D-584: ao abrir, desligado | Abrir o programa: desligado. Abrir outro livro: o botão fica como estava, e o editor novo segue o botão. | `test_d578_d580_o_botao_...` (abre desligado); `test_d580_d584_abrir_outro_livro_o_editor_novo_segue_o_botao` |
| §11 regra 7 | Só o nome "marcações" e o balão de uma frase. Sem atalho, sem menu, sem aviso. O balão não mudou na D-584. | o diff (`git show f9a5a6e`, `git show e08623b`) |

### Teste de reversão (§4.7)
Rodado numa cópia temporária do código antigo (`git worktree add --detach _tmp/antigo ac0b9ec`, só com o arquivo de
teste novo copiado; a cópia foi apagada depois): **9 falharam** (saída em `reversao-no-codigo-antigo-ac0b9ec.txt`).
O principal: "com o Zoom a página aparece pintada (76500 pixels coloridos; D-578)". No código novo: **9 passaram**.

### Teste de reversão da D-584 (2ª rodada)
Cópia temporária de `abbb0d3` (a entrega da 1ª rodada) com o arquivo de teste novo copiado (apagada depois): **10
falharam, 9 passaram** (as 9 da D-578/D-580). Saída em `reversao-d584-no-codigo-abbb0d3.txt`. As falhas: "escolher o
Pincel não acendeu o botão (D-584)", as 8 ferramentas de marcar, e "o editor do livro novo não segue o botão". No
código novo (`e08623b`): **19 passaram**.

### Testes da 2ª rodada (D-584), no `e08623b`, um arquivo por vez
- test_decisoes_marcacoes: 19 passed · test_editor_selecao: 17 passed · test_editar_zonas: 10 passed
- test_decisoes_tela: 35 passed · test_decisoes_9b2: 30 passed · test_para_revisar_na_tela: 26 passed
- test_trilha_e_opcoes: 29 passed · test_promessas -k "p197 or todo_botao": 2 passed

### Testes rodados no código novo da 1ª rodada (um arquivo por vez, sem janela na tela)
- test_decisoes_marcacoes: 9 passed · test_editor_selecao: 17 passed · test_editar_zonas: 10 passed
- test_decisoes_tela: 35 passed · test_decisoes_9b2: 30 passed · test_decisoes_9b1: 22 passed, 3 skipped
- test_decisoes_ver: 11 passed · test_decisoes_mover: 13 passed · test_para_revisar_na_tela: 26 passed
- test_tinta_escurecida: 8 passed · test_tinta_papel_da_pagina: 10 passed · test_trilha_e_opcoes: 29 passed
- test_menus_que_nao_faziam_nada: 5 passed · test_marcacao_por_tras: 4 passed
- test_promessas: 261 passed, 1 xfailed (11 min)

### Prints (1280 x 657, sem janela na tela)
`marcacoes-1-desligado-de-fabrica.jpg` e `marcacoes-2-ligado.jpg`: "Na escola de Jesus", página 12 de 199,
ferramenta Zoom, "Uma página". `marcacoes-3-pincel-acende-sozinho.jpg` (2ª rodada, D-584): o botão desligado, a
ferramenta Zoom e depois o Pincel escolhido; "marcações" acende sozinho e as cores aparecem. Feitos com `print_marcacoes.py` sobre uma CÓPIA do projeto da pasta de dados de teste
(em `_tmp`, apagada no fim).

## Ressalvas

1. **Os prints mostram a página em Original, não em Preto e branco como o print a-01 dele.** Quando copiei o projeto
   (14:09), a pasta de dados de teste já tinha sido regravada às 14:06 pelo próprio programa do Samuel (ele está
   testando): o livro estava como "ainda não passou pelo automático", todas as páginas em Original, mas com a marcação
   da máquina (35 áreas na página 12). Por isso a faixa "Livro novo" aparece nos prints. Experimentei pôr Preto e branco
   só na página 12, mas como as opções de gravura do livro não estavam mais ligadas, a gravura saía preta, o que
   confundiria; deixei a página como estava. O que o print prova é o botão: desligado, a página sem cores; ligado, as
   cores por cima.
2. (Respondida: D-584.) Desligado, o que a pessoa marca à mão sumia da vista ao soltar o mouse. Agora escolher uma
   ferramenta de marcar acende o botão. Só continua sumindo se a pessoa apagar o botão com a ferramenta de marcar na
   mão, que foi o combinado.
3. **O botão fica sempre clicável**, mesmo no Dividir, no "Duas lado a lado" e no "antes / depois", onde a vista da página
   com as marcações não está na tela. Ali clicar não muda nada na hora; vale quando voltar à "Uma página". Não pus
   balão de motivo nem apaguei o botão, para não acrescentar comportamento (regra 7).
4. A prova da lista 1.9 (`tests/test_decisoes_9b2.py`) ganhou uma linha: liga "marcações" antes de olhar o contorno
   das feitas à mão. A conferência dela é a mesma.
6. **Ferramenta de partida ao abrir um livro (D-584):** a ferramenta que fica na mão ao abrir não é o Zoom. É o
   Retângulo, quando o livro tem "procurar gravuras" ligado, ou a Mão (`_ferramenta_de_partida`, escolha do agente de
   layout na etapa 2). Como a gerente fixou "ao abrir, continua desligado", abrir o livro não conta como "escolher":
   abre com o Retângulo na mão e as marcações escondidas, até a pessoa escolher uma ferramenta. Ver a pergunta 2.
7. Abrir outro livro com o botão aceso: o botão continua aceso (D-580, "vale para todos os livros"), mesmo que a
   ferramenta de partida do livro novo seja a Mão.
5. Clique simulado do Qt e `grab()` sem janela na tela: não pilotei a janela real com mouse nativo (o PC está em uso).

## Perguntas para o Samuel

2. (2ª rodada) Ao abrir um livro que passou pelo Automático com "procurar gravuras", a ferramenta que já vem na mão é
   o Retângulo, que é de marcar. Hoje as marcações abrem escondidas mesmo assim (a página limpa, como na D-578) e só
   acendem quando ele escolhe uma ferramenta. Está bom assim, ou abrir com o Retângulo na mão deve já acender as
   marcações? (Nesse caso, a página do Automático voltaria a abrir com as cores por cima.)

1. (Respondida em 29/10, "a" → D-584.) Com "marcações" desligado, quando o Kaique marca uma área à mão (Retângulo, Pincel...), ao soltar o mouse o que ele
   marcou some da vista (fica marcado). Está bom assim, ou o que ele acabou de marcar deve aparecer mesmo com o botão
   desligado? (Hoje fiz exatamente o "A": tudo escondido, só o traço enquanto arrasta.)
