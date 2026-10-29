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
    nem configurações): a tela é uma só enquanto o programa está aberto, então o estado vale para todas as páginas e
    livros e volta a desligado ao abrir o programa.
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
| §11 regra 7 | Só o nome "marcações" e o balão de uma frase. Sem atalho, sem menu, sem aviso. | o diff (`git show f9a5a6e`) |

### Teste de reversão (§4.7)
Rodado numa cópia temporária do código antigo (`git worktree add --detach _tmp/antigo ac0b9ec`, só com o arquivo de
teste novo copiado; a cópia foi apagada depois): **9 falharam** (saída em `reversao-no-codigo-antigo-ac0b9ec.txt`).
O principal: "com o Zoom a página aparece pintada (76500 pixels coloridos; D-578)". No código novo: **9 passaram**.

### Testes rodados no código novo (um arquivo por vez, sem janela na tela)
- test_decisoes_marcacoes: 9 passed · test_editor_selecao: 17 passed · test_editar_zonas: 10 passed
- test_decisoes_tela: 35 passed · test_decisoes_9b2: 30 passed · test_decisoes_9b1: 22 passed, 3 skipped
- test_decisoes_ver: 11 passed · test_decisoes_mover: 13 passed · test_para_revisar_na_tela: 26 passed
- test_tinta_escurecida: 8 passed · test_tinta_papel_da_pagina: 10 passed · test_trilha_e_opcoes: 29 passed
- test_menus_que_nao_faziam_nada: 5 passed · test_marcacao_por_tras: 4 passed
- test_promessas: 261 passed, 1 xfailed (11 min)

### Prints (1280 x 657, sem janela na tela)
`marcacoes-1-desligado-de-fabrica.jpg` e `marcacoes-2-ligado.jpg`: "Na escola de Jesus", página 12 de 199,
ferramenta Zoom, "Uma página". Feitos com `print_marcacoes.py` sobre uma CÓPIA do projeto da pasta de dados de teste
(em `_tmp`, apagada no fim).

## Ressalvas

1. **Os prints mostram a página em Original, não em Preto e branco como o print a-01 dele.** Quando copiei o projeto
   (14:09), a pasta de dados de teste já tinha sido regravada às 14:06 pelo próprio programa do Samuel (ele está
   testando): o livro estava como "ainda não passou pelo automático", todas as páginas em Original, mas com a marcação
   da máquina (35 áreas na página 12). Por isso a faixa "Livro novo" aparece nos prints. Experimentei pôr Preto e branco
   só na página 12, mas como as opções de gravura do livro não estavam mais ligadas, a gravura saía preta, o que
   confundiria; deixei a página como estava. O que o print prova é o botão: desligado, a página sem cores; ligado, as
   cores por cima.
2. **Desligado, o que a pessoa marca à mão some da vista ao soltar o mouse** (fica marcado, mas só aparece com
   "marcações" ligado). É o que a decisão diz ("Com qualquer ferramenta [...] a página aparece limpa"); enquanto arrasta,
   o traço aparece. Pode surpreender o Kaique na primeira vez: ver a pergunta 1.
3. **O botão fica sempre aceso**, mesmo no Dividir, no "Duas lado a lado" e no "antes / depois", onde a vista da página
   com as marcações não está na tela. Ali clicar não muda nada na hora; vale quando voltar à "Uma página". Não pus
   balão de motivo nem apaguei o botão, para não acrescentar comportamento (regra 7).
4. A prova da lista 1.9 (`tests/test_decisoes_9b2.py`) ganhou uma linha: liga "marcações" antes de olhar o contorno
   das feitas à mão. A conferência dela é a mesma.
5. Clique simulado do Qt e `grab()` sem janela na tela: não pilotei a janela real com mouse nativo (o PC está em uso).

## Perguntas para o Samuel

1. Com "marcações" desligado, quando o Kaique marca uma área à mão (Retângulo, Pincel...), ao soltar o mouse o que ele
   marcou some da vista (fica marcado). Está bom assim, ou o que ele acabou de marcar deve aparecer mesmo com o botão
   desligado? (Hoje fiz exatamente o "A": tudo escondido, só o traço enquanto arrasta.)
