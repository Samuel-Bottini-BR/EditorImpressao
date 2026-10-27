# Bateria nova, parte 4: "Cada botão prova que faz o que promete" — ONDE PAREI

Verificador (`.claude/agents/verificador.md`), ramo `obra-promessas-2026-10-26` (base `obra-2026-10-26` `fdabf0d`,
com as etapas 1, 2 e 9a), worktree `.claude/worktrees/obra-promessas`. Não mexi em `ui/` nem `core/`: só testes, a lista
de promessas e este relatório. Teste de **máquina** (nenhum teste de olho nesta tarefa).

**Situação: PRONTO PARA CONFERIR** (a lista e as provas). Nunca "aprovado": quem marca é o Samuel.

## Em uma frase

Os 129 botões e ações do programa ganharam promessa escrita; o programa de hoje cumpre 110, quebra 8 (são 4 defeitos
reais, achados por esta bateria) e 11 esperam a etapa que vai construí-los.

## Decisões que esta tarefa precisa cumprir (palavras do Samuel)

| Nº | Palavras dele | O que esta tarefa faz |
|---|---|---|
| D-010 (26/10) | "eu acho que o botão tem que ser provado que ele faz o que se diz que se faz, e não só se ele muda algo na tela." | Uma promessa escrita por botão (`tests/promessas/promessas.md`), tirada do nome, da dica e do Livro; o teste (`tests/test_promessas.py`) clica e confere a promessa inteira: tela, projeto gravado e PDF gerado de verdade. Botão sem promessa reprova. |
| D-011 (26/10) | "Sim" (nova bateria de testes: teste do Kaique, tarefas, decisões, promessas, conferência em caminho) | Esta é a parte "promessas" (item 4 da bateria, plano de 26/10). |
| D-014 (26/10) | "Faça até o final sem pausas [...] pode escolher sem minha conferência" | Os detalhes foram decididos por mim (ver "Escolhas que fiz"). |
| Regra 4 do §11 | "Aparência não conta como prova." | A prova mede o `projeto.json`, o `acoes.jsonl` e o PDF que sai, não só a tela. |

## Como cumpri cada uma

| Decisão | Como ficou | Prova |
|---|---|---|
| D-010 "provado que ele faz o que se diz" | 129 promessas, cada uma com chaves (onde o botão está), dica, decisões citadas e o que acontece **na tela / no projeto / no PDF**. Cada uma tem uma prova `@prova("P-NNN")` que aperta o botão de verdade (sinal `clicked`, `trigger` do menu, clique do mouse na trilha, nos ícones da direita e nos cartõezinhos do filtro) e confere. Onde a promessa fala do PDF, o PDF é gerado pelo "Confirmar e processar" e medido (número de páginas, qual página é qual pelo bloco preto de cada folha, página branca, deitada, preto e branco, papel amarelado, tamanho em mm). | `tests/test_promessas.py`: 239 casos; rodada final no PC: **217 passaram, 11 falharam (os 4 defeitos), 11 xfail (aguardam etapa)**, 17 min 42 s |
| D-010 "Botão sem promessa reprova" | A varredura abre o programa sem janela, passa por todas as telas e estados que sabe abrir (tela dos livros vazia e com livro, livro aberto, "Todas as páginas", "O que fazer", cada ferramenta com o Propriedades, cada painel, página com aviso, "Por motivo", sanfona, miniaturas fechadas, "Só neste pedaço", "Só as letras", 5 partes das Configurações, as janelas e as caixas de pergunta) e anota a chave de cada botão à vista. | `test_todo_botao_tem_promessa` (passa: nenhum botão sem promessa) e o contrário, `test_toda_promessa_tem_botao` (promessa de botão que sumiu reprova); `test_toda_promessa_tem_prova` |
| "aguarda etapa" (pedido da gerente) | Promessa com o campo **aguarda** vira `xfail(strict=True)` com o motivo; quando a etapa fizer, o xfail estrito vira erro e obriga a tirar a marca. | 11 xfail, nenhum XPASS |
| "Aparência não é prova" | Nenhuma prova para no "mudou a tela": cada uma confere o projeto gravado (o `projeto_gravado()` força a gravação e lê o `projeto.json` do disco) e, quando a promessa diz, o PDF. Quando a promessa diz que o PDF não muda, confere que o projeto gravado não mudou (o PDF sai só do livro e do projeto). Um erro escondido de botão (o `erros.log`) também reprova. | fixture `_nenhum_erro_escondido` |

## Os defeitos reais achados (promessas quebradas)

**A. O filtro escolhido à mão não vale no PDF quando "Limpar a folha" não foi marcada.** Livro aberto sem marcar nada
(D-009: "eu deveria conseguir abrir o livro sem escolher nenhuma opção para fazer tudo manualmente"); escolho Preto e
branco numa página (pelo cartãozinho do painel, pelo menu, pela tecla, pelo botão "usar Mágico pro nesta" do aviso, pelo
"todas"): o projeto grava o filtro, mas a página sai no PDF amarelada, como no Original. Com "Limpar a folha" marcada, sai
certo (conferi). Causa: a tela não grava a marca "mexida à mão" do filtro — `core/etapas.marcar_mexida_a_mao` não é
chamada por nenhum arquivo de `ui/`; o plano de 26/10 mandou "ligar nas etapas 2/3/5" e a etapa 2 entrou sem ligar. É o
mesmo defeito da tarefa 8 do teste do Kaique ("Preto e branco" ignorado). Promessas: P-005 (o PDF depois de
"continuar"), P-080, P-081, P-109. **Sem dono certo** (etapa 3 ou 5: a gerente decide).

**B. "Deixar a folha em branco" e "pintar de branco" não chegam ao PDF numa página em Original.** A folha inteira
marcada como papel (menu Marcar > "Deixar a folha em branco") e a área "pintada de branco" ficam gravadas no projeto, mas
a página em Original (a de fábrica, D-134) sai com tudo, amarelada — mesmo com "Limpar a folha" marcada. Em Preto e
branco sai branca. D-027 está no Livro como "construída". Promessas: P-078, P-075. **Sem dono.**

**C. Pelo menu Arquivo > "Confirmar e processar" (Ctrl+Enter) o programa não mostra a janela "Antes de processar".**
Com avisos pendentes, o botão da área de trabalho mostra a lista (D-274: "quando alguém tentar imprimir sem ver os
alertas o programa para e mostra os alertas"); o menu e a tecla vão direto para o destino, porque chamam
`JanelaPrincipal.processar` sem passar por `TelaConferir._pedir_processamento`. Promessa P-127 (só o caso do menu
falha). **Sem dono.**

**D. O menu Filtro tem tique, mas o tique não acompanha a página.** Escolhido o Preto e branco, o menu continua sem
marca; e o tique de um clique no menu fica lá ao passar para uma página em Original. P-085. É uma promessa minha (tirada de
os itens serem de marcar, como os do menu Painéis, em que "a marca acompanha", D-057) — **a conferir com o Samuel** se ele
quer o tique ou itens sem tique. **Sem dono.**

As 8 promessas quebradas ficam vermelhas no teste de propósito, cada uma com o campo **defeito** na lista. Para o
`obra-2026-10-26` juntar sem vermelho, a gerente dá dono a cada defeito e troca **defeito** por **aguarda** (a prova vira
xfail estrito e passa a ser exigida quando a etapa consertar).

## As que aguardam etapa (11, xfail estrito)

| Promessa | Aguarda |
|---|---|
| P-012 "Rodar o automático..." abre o Automático, sem a tela "O que fazer" | etapa 3 (D-002/D-018) |
| P-137 aviso de livro novo ("Rodar o automático…" / "agora não") | etapa 3 (D-005/D-018) |
| P-139 painel Automático de verdade (rodar em todas/escolhidas/uma página, uma etapa só) | etapa 3 (D-002/D-003/D-004) |
| P-059 "dividir esta" numa folha que entrou como uma página só (livro aberto sem "Dividir": hoje o botão fica apagado) | etapa 4 |
| P-136 "Ver lado a lado" na área de trabalho (barra de baixo e menu Ver) | etapa 6 (D-015/D-058) |
| P-095 "ver as N em tela cheia" no Para revisar | etapa 7 (D-259) |
| P-101 "está certo" com resposta (vai para a próxima dúvida) | etapa 7 (lista única 1.1) |
| P-061 "usar em todas" do Dividir abre a lista com as exceções | etapa 9 (D-090) |
| P-125 Desfazer apagado sem nada para desfazer (barra de baixo e menu) | etapa 9 |
| P-129 o Desfazer desfaz também a marcação ("Limpar tudo", Retângulo) | etapa 9 (lista única 1.3 e 4.6) |
| P-027 a lista de atalhos em português (hoje "Ctrl+Return", "Left", "Del") | etapa 11 (lista única 5.10) |

## Escolhas que fiz (D-014)

- **Lista em `.md`** (`tests/promessas/promessas.md`), não `.yaml`: o PyYAML não está no `requirements.txt`; o formato
  `### P-NNN · título` + `- **campo:** texto` é lido por `ler_promessas()`.
- **Uma entrada por botão, ou por ação que mora em vários lugares** (ex.: "Girar ¼ à direita" no painel, no canto da
  página e no menu é a P-050, com as três chaves; a prova aperta as três).
- **Chave = `tela/lugar/rótulo`**, com os números trocados por N; os lugares da área de trabalho saem de
  `lugares_da_area_de_trabalho()` (um lugar desconhecido vira "?" e reprova até ganhar lugar e promessa).
- **Os botões dos avisos** entram pelo catálogo `core/analise.ALERTAS`, pela correção (`aviso/em_branco`,
  `aviso/apagar`…), porque cada um só aparece na página que tem aquele aviso.
- **Caixinhas (QCheckBox) e bolinhas (QRadioButton) ficaram fora da varredura** desta leva: são opções, não botões.
  As listas (combos) também. Fica para a próxima leva (ressalva abaixo).
- **O livro do teste abre sem nenhuma caixinha** (como vai abrir depois da etapa 3, D-002/D-009). Tudo isso mora num
  ajudante só, `abrir_livro_para_teste()` (`tests/promessas/ajudantes.py`), para a gerente ajustar quando a etapa 3 mudar
  o caminho de abrir.
- **Livro sintético** (papel amarelado, um bloco preto numa altura diferente em cada folha, para saber no PDF qual página
  é qual), sem lombada nem capa (regra de 21/10). A medida é de lugar, cor e tamanho, não de qualidade de imagem.
- **A tela "O que fazer"**: as promessas dos botões dela dizem "sai na: etapa 3"; as provas pulam sozinhas quando a tela
  sair.
- **Achado no caminho:** a caixa "Lista de atalhos" mostrava "Show Details..." nos testes porque o teste não carregava a
  tradução do Qt que o `main.py` carrega (etapa 9a). O teste agora carrega igual ao programa (`traduzir_o_qt`) e lá
  aparece "Mostrar detalhes...".

## Ressalvas (o que não está provado)

1. **Clique simulado, não mouse de verdade.** As provas usam `botao.click()`, `acao.trigger()` e `QTest.mouseClick` —
   passam pelo sinal e pelo evento do Qt, mas não pelo mouse do Windows. O verificador já viu (22/09) o `QTest` passar
   enquanto o uso real falhava em arrastar; para clique de botão o risco é menor, mas a prova com a janela de verdade é
   o teste do Kaique.
2. **Caixinhas, bolinhas e listas não estão na varredura** (ex.: "Esta página tem foto", "Só as letras", "Limpar a
   sujeira", "Mostrar as áreas achadas", as caixinhas da tela "O que fazer", a lista do jeito do "Só as letras"). Algumas
   aparecem dentro de provas (P-074, P-083, P-084), mas não há promessa para cada uma.
3. **A varredura só vê o que ela sabe abrir.** Botão que só aparece num estado que ela não monta não reprova. Os conhecidos
   "fora da varredura": "Ajustar o pedaço à figura" (P-076, a prova monta o caso). As caixas de pergunta entram pelas
   ações que as abrem (Começar de novo?, Renomear, Tirar da lista?, Já existe um arquivo, Ir para a página, Nome do
   arquivo, Lista de atalhos, Mandar para a impressora?); a "Este livro tem fundo separado?" (PDF com camadas) não.
4. **Algumas provas são mais fracas que a promessa:** P-110 ("usar o corte alargado": o livro sintético não tem corte
   alargado medido; a prova só vê que o clique entrou no histórico), P-111 e P-113 (só o projeto), P-062/P-138/P-143
   (vão para a tela "O que fazer", que sai na etapa 3), P-151 e P-161 (a impressora é trocada por uma que anota o que
   recebeu: nada vai para a EPSON — D-332 continua pedindo a folha de verdade).
5. **Avisos postos à mão.** Para mostrar o botão de um aviso, a prova põe o aviso na página e redesenha a faixa; ao trocar
   de página, o programa refaz os avisos que ele mesmo mede (o "contas discordam" de mentira sai), por isso a prova põe
   o aviso depois de chegar na página.
6. **Tempo:** o arquivo leva ~15 a 18 min no PC (gera ~60 PDFs pequenos). Não rodei o conjunto inteiro nem o GitHub
   (regra: um arquivo por vez no PC; o conjunto é da gerente). A rodada do GitHub vai mostrar os 11 vermelhos dos 4
   defeitos até eles ganharem dono.
7. **P-085 (tique do menu Filtro)** é promessa minha, sem decisão do Samuel: pergunta abaixo.

## Perguntas para o Samuel (a gerente leva à Central)

1. **Menu Filtro:** os itens têm tique, mas o tique não mostra o filtro da página. Prefere (a) o tique acompanhando o
   filtro da página da vez, ou (b) itens sem tique? (defeito D, P-085)

## O que mudou (arquivos)

- `tests/promessas/promessas.md` — a lista das 129 promessas (novo).
- `tests/promessas/ajudantes.py` — livro sintético, abrir/gravar/gerar, medidas do PDF, varredura (novo).
- `tests/promessas/__init__.py` (novo).
- `tests/test_promessas.py` — a varredura e as provas (novo).
- `relatorios/obra-promessas/roteiro/explorar.py` (exploração inicial dos botões) e `tabela.py` (monta a tabela abaixo
  a partir de uma rodada com `--junitxml`).

## Commits

- `0412dd9` Promessas: provas ajustadas; 4 defeitos reais anotados na lista (filtro à mão fora do PDF, folha em branco no Original, menu processar sem 'Antes de processar', menu Filtro sem tique)
- `ee146f2` Promessas: provas de todas as promessas (tela, projeto e PDF), primeira rodada de ajustes
- `7fbe4a6` Promessas dos botões: lista, varredura de todos os botões e primeiras provas (D-010)
- (o último commit, com este relatório: ver `git log` do ramo)

## Tabela: botão | promessa | cumpre / quebra / aguarda etapa

Rodada final no PC (27/10/2026): `pytest tests\test_promessas.py` → 217 passaram, 11 falharam, 11 xfail. "QUEBRA" = ao
menos um caso da promessa falhou (ex.: P-080 falha só no PDF do Preto e branco pelo painel; menu e teclas gravam certo).

| Promessa | Botão (onde) | O que promete (resumo) | Situação |
|---|---|---|---|
| P-001 | "+" (abrir um PDF novo) — `início/livros/+ (abrir um PDF)`, `menu/abrir` | nada ainda. nasce o projeto do livro escolhido (pasta com `projeto.json`, `caminho_entrada` = o PDF). abre a janela de escolher o arquivo; e… | cumpre |
| P-002 | Configurações — `início/livros/Configurações`, `menu/configuracoes` | nada muda. **no PDF:** nada muda. abre a janela Configurações, com a lista das partes à esquerda. | cumpre |
| P-003 | Ajuda (a lista de atalhos) — `início/livros/Ajuda`, `menu/atalhos`, `caixa “Lista de atalhos”/fechar` … | nada muda. **no PDF:** nada muda. abre "Lista de atalhos" com os atalhos tirados dos próprios menus (ex.: "Desfazer — Ctrl+Z"), em português… | cumpre |
| P-027 | a lista de atalhos em português — `menu/atalhos` | as teclas aparecem com nome em português ("Ctrl+Enter", "Ctrl+Seta para a esquerda", "Delete"), sem "Return", "Left", "Right", "Del". | aguarda etapa 11 (revisão dos nomes: lista única 5.10) |
| P-004 | clique no cartão do livro — `início/livros/(clique no cartão)` | nada muda. o livro abre na tela inteira (nome, páginas para folhear), sem os outros cartões. | cumpre |
| P-005 | "continuar" (cartão, livro aberto e menu do livro) — `início/livros/continuar`, `início/livro aberto/Continuar`, `início/menu do livro/continuar` … | o PDF gerado depois de continuar sai com o trabalho de antes. o trabalho volta igual (nada se perde). a área de trabalho do livro, com o que… | **QUEBRA** (defeito A) |
| P-006 | "começar de novo" (menu do livro) — `início/menu do livro/começar de novo`, `início/livro aberto/Mais... começar de novo`, `caixa “Começar de novo?”/Começar de novo` … | depois de "Começar de novo", o PDF sai sem o trabalho antigo. com "Começar de novo" o trabalho de antes sai do projeto (a página em Preto e … | cumpre |
| P-007 | "renomear" (menu do livro) — `início/menu do livro/renomear`, `início/livro aberto/Mais... renomear`, `caixa “Renomear”/OK` … | o nome novo fica gravado (aparece de novo ao reabrir a tela dos livros). O PDF do livro não muda. pede o nome; com OK o cartão passa a mostr… | cumpre |
| P-008 | "abrir a pasta de saída" / "abrir a pasta" — `início/menu do livro/abrir a pasta de saída`, `início/livro aberto/Mais... abrir a pasta de saída`, `início/livros/abrir a pasta` … | nada muda. **no PDF:** nada muda. abre o Explorador do Windows na pasta onde o PDF pronto foi gravado. | cumpre |
| P-009 | "remover da lista" (Tirar da lista) — `início/menu do livro/remover da lista`, `início/livro aberto/Mais... remover da lista`, `caixa “Tirar da lista?”/Tirar da lista` … | o PDF do livro (a entrada) continua onde estava, intacto. a pasta do projeto sai da lista (as cópias de segurança vão para `copias-de-segura… | cumpre |
| P-010 | "Voltar para os livros" (Esc) — `início/livro aberto/Voltar para os livros` | volta aos cartões, com o cartão deste livro marcado. | cumpre |
| P-011 | "Rodar o automático..." (livro aberto), como é hoje — `início/livro aberto/Rodar o automático...` | nada muda até confirmar. abre as escolhas do automático deste livro, com as que ele já tinha. | cumpre |
| P-012 | "Rodar o automático..." abre o Automático de verdade — `início/livro aberto/Rodar o automático...` | abre o livro na área de trabalho com o Automático (painel ou janela grande), não a tela "O que fazer". | aguarda etapa 3, D-002/D-018 |
| P-013 | "Ver todas as páginas" (livro aberto) — `início/livro aberto/Ver todas as páginas` | a grade com todas as páginas, em "uma a uma". **no projeto:** nada muda. | cumpre |
| P-014 | "Confirmar e processar..." (livro aberto) — `início/livro aberto/Confirmar e processar...` | o PDF sai com todas as páginas do livro. abre o trabalho e mostra a janela de confirmar o destino; confirmado, gera. | cumpre |
| P-015 | "Uma página" / "Duas lado a lado" (livro aberto) — `início/livro aberto/Uma página`, `início/livro aberto/Duas lado a lado` | nada muda (a escolha vai para as configurações do programa). mostra uma página por vez, ou as páginas em pares; a escolha fica para o próxim… | cumpre |
| P-016 | "Rolar sem parar" (livro aberto) — `início/livro aberto/Rolar sem parar` | ligado, as páginas rolam uma atrás da outra; desligado, uma de cada vez. Lembrado. | cumpre |
| P-017 | "Caber a página" / "Caber a altura" / "Caber a largura" / "Tamanho real" (livro aberto) — `início/livro aberto/Caber a página`, `início/livro aberto/Caber a altura`, `início/livro aberto/Caber a largura` … | o tamanho da página na tela muda como diz o nome; o botão escolhido fica aceso; lembrado. | cumpre |
| P-018 | "‹" / "›" (folha anterior / próxima, no livro aberto) — `início/livro aberto/‹`, `início/livro aberto/›` | vai para a folha de antes / a de depois. | cumpre |
| P-019 | "Todas as páginas": "uma a uma" / "em pares" / "todas" / "só as que precisam de atenção" — `início/todas as páginas/uma a uma`, `início/todas as páginas/em pares`, `início/todas as páginas/todas` … | nada muda. a grade mostra uma a uma, em pares, todas ou só as que têm aviso (a contagem entre parênteses bate com as páginas com aviso). | cumpre |
| P-020 | "voltar ao livro" / "voltar ao trabalho" (Todas as páginas) — `início/todas as páginas/voltar ao livro`, `área de trabalho/todas as páginas/voltar ao trabalho` | sai da grade e volta na mesma página em que estava. | cumpre |
| P-026 | "Mais..." (livro aberto) — `início/livro aberto/Mais...` | nada muda só por abrir o menu. abre o menu do livro (continuar, começar de novo, renomear, abrir a pasta de saída, remover da lista). | cumpre |
| P-021 | "Conferir" — `o que fazer/Conferir` | as escolhas da tela ficam gravadas no projeto. leva à área de trabalho, mesmo sem nenhuma caixinha marcada. | cumpre |
| P-022 | "voltar" (tela "O que fazer") — `o que fazer/voltar` | volta para a tela dos livros, sem abrir a área de trabalho. | cumpre |
| P-023 | receitas: "pôr neste livro" / "guardar" / "apagar" — `o que fazer/pôr neste livro`, `o que fazer/guardar`, `o que fazer/apagar` | a receita fica gravada nas configurações do programa. "guardar" guarda as caixinhas de agora com o nome digitado (aparece na lista); "pôr ne… | cumpre |
| P-024 | "Mais opções" (tela "O que fazer") — `o que fazer/Mais opções` | abre as opções a mais daquele grupo (abre e fecha). | cumpre |
| P-025 | folhear o PDF: "<", ">", "tela cheia" (tela "O que fazer") — `o que fazer/<`, `o que fazer/>`, `o que fazer/tela cheia` | a página mostrada passa para a de antes / a de depois; "tela cheia" abre a página grande. | cumpre |
| P-030 | Dividir a folha — `trilha/dividir`, `menu/usar_dividir` | nada muda só por escolher a ferramenta. **no PDF:** nada muda. a ferramenta fica escolhida (marcada na trilha e no menu Ferramentas); a folh… | cumpre |
| P-031 | Cortar as bordas — `trilha/cortar`, `menu/usar_cortar` | nada muda. **no PDF:** nada muda. a ferramenta fica escolhida; o Propriedades abre com os botões do Cortar. | cumpre |
| P-032 | Endireitar — `trilha/endireitar`, `menu/usar_endireitar` | nada muda. **no PDF:** nada muda. a ferramenta fica escolhida; o Propriedades abre com os botões do Endireitar. | cumpre |
| P-033 | ferramentas de marcar (Retângulo, Oval, Laço, Ponto a ponto, Pincel, Varinha, Pegar tudo desta cor, Mover e mudar o tamanho da área) — `trilha/retangulo`, `menu/usar_retangulo`, `trilha/elipse` … | nada muda só por escolher. **no PDF:** nada muda. a ferramenta fica escolhida (trilha, menu Ferramentas e o editor de marcar com ela); o Pro… | cumpre |
| P-034 | Zoom e Mão — `trilha/zoom`, `menu/usar_zoom`, `trilha/mao` … | nada muda. **no PDF:** nada muda. a ferramenta fica escolhida; o Propriedades diz que ela só serve para olhar. | cumpre |
| P-040 | ícone de cada painel / menu Painéis — `ícones da direita/revisar`, `ícones da direita/automatico`, `ícones da direita/props` … | nada muda. abre o painel (um por vez), ao lado da página, nunca por cima; o ícone e o menu Painéis marcam o aberto; clicar de novo no ícone … | cumpre |
| P-041 | seta dos ícones / "Ícones da direita" — `ícones da direita/seta`, `menu/icones` | esconde os ícones da direita (sobra a seta) e mostra de novo; o item do menu acompanha. | cumpre |
| P-042 | "fechar o painel" / "Fechar o painel" / "esconder os painéis" — `área de trabalho/para revisar/fechar o painel`, `área de trabalho/automático/fechar o painel`, `área de trabalho/propriedades/fechar o painel` … | o painel aberto fecha e a página ganha o lugar dele. | cumpre |
| P-043 | "Lado direito": ícones na borda / sanfona (área de trabalho 1) — `menu/lado_icones`, `menu/lado_sanfona` | troca o jeito do lado direito; fica guardado para a próxima vez que o programa abrir. | cumpre |
| P-050 | Girar ¼ à direita — `área de trabalho/girar a folha/¼ à direita`, `área de trabalho/girar do canto/Girar ¼ à direita`, `menu/girar` | a página sai deitada (mais larga que alta) e o conteúdo girado. a folha fica com giro de 90° gravado (uma ação no histórico). a folha aparec… | cumpre |
| P-051 | Girar ¼ à esquerda — `área de trabalho/girar a folha/¼ à esquerda`, `área de trabalho/girar do canto/Girar ¼ à esquerda`, `menu/girar_esquerda` |  | cumpre |
| P-052 | Girar meia volta — `área de trabalho/girar a folha/meia volta`, `área de trabalho/girar do canto/Girar meia volta`, `menu/girar_meia_volta` | giro de 180° gravado. **no PDF:** a página sai de cabeça para baixo (em pé). | cumpre |
| P-053 | "Aplicar o giro em" (só esta / todas / daqui em diante / ímpares / pares) — `menu/giro_em_esta`, `menu/giro_em_todas`, `menu/giro_em_daqui_em_diante` … | o próximo giro do menu e do painel vale para as folhas escolhidas. | cumpre |
| P-054 | "deixar em branco" (Esta página, painel Filtro, menu Página, tecla Delete) — `área de trabalho/esta página/deixar em branco`, `área de trabalho/filtro da página/deixar em branco`, `menu/deixar_em_branco` | o PDF tem o MESMO número de páginas, e essa página sai toda branca, no mesmo lugar. a página fica com `em_branco` gravado (uma ação no histó… | cumpre |
| P-055 | "voltar a página" (depois do "deixar em branco") — `área de trabalho/esta página/voltar a página`, `área de trabalho/faixa do aviso/voltar a página` | a página deixa de sair em branco. **no PDF:** a página sai com o conteúdo dela de novo. | cumpre |
| P-056 | "tirar do livro" (Esta página, painel Filtro, menu Página, Shift+Delete) — `área de trabalho/esta página/tirar do livro`, `área de trabalho/filtro da página/tirar do livro`, `menu/tirar_do_livro` | a página some do PDF: uma página a menos, e as outras saem na ordem, sem ela. a página fica `apagada` (uma ação no histórico). | cumpre |
| P-057 | "trazer de volta" / "Trazer de volta a página tirada" — `área de trabalho/esta página/trazer de volta`, `menu/restaurar` | a página tirada volta. **no PDF:** ela volta ao PDF, no lugar dela. | cumpre |
| P-059 | "dividir esta" numa folha que entrou como uma página só — `área de trabalho/dividir/dividir esta` | num livro aberto sem "Dividir", "dividir esta" fica aceso e põe a linha na folha. | aguarda etapa 4 (dividir à mão folha por folha) |
| P-060 | "não dividir esta" / "dividir esta" (folha já dividida) — `área de trabalho/dividir/não dividir esta`, `área de trabalho/dividir/dividir esta` | a folha não dividida sai como UMA página (a folha inteira, deitada). a folha deixa de ser dividida (e volta, com "dividir esta"). o botão tr… | cumpre |
| P-061 | "usar em todas" (Dividir) — `área de trabalho/dividir/usar em todas` | só as folhas marcadas recebem a linha; a folha com linha própria (exceção) fica com a dela. abre a lista das folhas para escolher. | aguarda etapa 9, D-090 ("Usar em todas" que apaga exceções; no Dividir ainda aplica em todas sem seletor) |
| P-062 | "mudar nas opções do livro..." (Dividir, Cortar, Endireitar) — `área de trabalho/dividir/mudar nas opções do livro...`, `área de trabalho/cortar/mudar nas opções do livro...`, `área de trabalho/endireitar/mudar nas opções do livro...` | nada muda só por ir. leva às escolhas do livro inteiro, sem perder o trabalho feito. | cumpre |
| P-063 | "não cortar esta" — `área de trabalho/cortar/não cortar esta`, `aviso/sem_recorte` | a página sai no tamanho inteiro do scan. a página fica sem corte (o corte dela é a página inteira). | cumpre |
| P-064 | "usar o corte do programa" — `área de trabalho/cortar/usar o corte do programa` | o corte à mão desta página sai; vale o do programa. **no PDF:** a página sai como antes do ajuste. | cumpre |
| P-065 | "usar em todas" (Cortar) — `área de trabalho/cortar/usar em todas` | as páginas marcadas saem com o tamanho do corte desta página. as páginas marcadas ficam com o corte desta; a que tem corte próprio (exceção)… | cumpre |
| P-066 | "tamanho..." (Cortar) — `área de trabalho/cortar/tamanho...`, `tamanho da folha/A4`, `tamanho da folha/A5` … | a página sai no tamanho de folha escolhido (ex.: A5 = 148 × 210 mm). com OK, a página fica com o tamanho de folha escolhido; o corte dela nã… | cumpre |
| P-067 | "0,1°" anti-horário e horário (Endireitar) — `área de trabalho/endireitar/N,N° — Gira a página 0,1 grau no sentido anti-horário`, `área de trabalho/endireitar/N,N° — Gira a página 0,1 grau no sentido horário` | a página sai endireitada com esse ângulo. o ângulo da página muda 0,1° (para um lado ou para o outro), gravado como ângulo à mão. | cumpre |
| P-068 | "deixar como veio" (Endireitar) — `área de trabalho/endireitar/deixar como veio`, `aviso/angulo_zero` | ângulo 0 nesta página. **no PDF:** a página sai sem girar. | cumpre |
| P-069 | "usar o ângulo do programa" (Endireitar) — `área de trabalho/endireitar/usar o ângulo do programa` | o ângulo à mão sai. **no PDF:** a página sai com o ângulo do programa. | cumpre |
| P-070 | "Marcar como": gravura ou foto / letra e traço / papel / pintar por cima / manter a cor da tinta / tinta preta, fundo original — `área de trabalho/marcar/gravura ou foto`, `área de trabalho/marcar/letra e traço`, `área de trabalho/marcar/papel` … | "papel" na página inteira deixa a página branca (D-200); "gravura ou foto" guarda a cor da área. a área desenhada depois fica gravada com es… | cumpre |
| P-071 | "cor de pintar" — `área de trabalho/marcar/cor de pintar` | abre a escolha da cor do "pintar por cima". **no projeto:** a área pintada usa a cor escolhida. | cumpre |
| P-072 | "detectar automaticamente" / menu "Procurar de novo" — `área de trabalho/marcar/detectar automaticamente`, `menu/procurar_de_novo` | o que foi marcado à mão continua na página. | cumpre |
| P-073 | "usar em todas" / "daqui em diante" (marcação desta página) — `área de trabalho/marcar/usar em todas — Copia a marcação desta página (gravura, letra, papel)`, `área de trabalho/marcar/daqui em diante — Copia a marcação desta página para esta e` | o mesmo que a marcação faz na página dela (a folha inteira como papel sai branca: P-078). a marcação desta página fica gravada em todas as p… | cumpre |
| P-074 | "usar em todas" / "daqui em diante" (Esta página tem foto) — `área de trabalho/marcar/usar em todas — Leva o "Esta página tem foto" desta página`, `área de trabalho/marcar/daqui em diante — Leva o "Esta página tem foto" desta página` | o "Esta página tem foto" desta página fica igual em todas (ou desta em diante). | cumpre |
| P-075 | "apagar a área" / "pintar de branco" / "copiar" / "colar" — `área de trabalho/marcar/apagar a área`, `área de trabalho/marcar/pintar de branco`, `área de trabalho/marcar/copiar` … | a área pintada de branco sai branca. "apagar a área" tira a área; "pintar de branco" a troca por papel; "copiar" + "colar" (noutra página) p… | **QUEBRA** (defeito B) |
| P-076 | "Ajustar o pedaço à figura" — `área de trabalho/marcar/Ajustar o pedaço à figura` | o retângulo do pedaço encolhe até a figura (uma ação no histórico); sem clicar, nada muda. | cumpre |
| P-077 | menu Marcar > "Limpar tudo" — `menu/limpar_marcacao` | a marcação da página da vez sai (o desfazer dela é a P-129). | cumpre |
| P-129 | Desfazer (Ctrl+Z, menu Editar, barra de baixo) desfaz também a marcação — `menu/desfazer` | depois de "Limpar tudo" (ou de desenhar uma área), o Desfazer traz a marcação de antes. | aguarda etapa 9 (desfazer e Retângulo: lista única 1.3 e 4.6) |
| P-078 | menu Marcar > "Deixar a folha em branco" — `menu/folha_em_branco` | a folha inteira fica marcada como papel. **no PDF:** a página sai toda branca, no mesmo lugar. | **QUEBRA** (defeito B) |
| P-080 | os quatro filtros (painel, menu Filtro, teclas 1 a 4) — `área de trabalho/filtro da página/cartão Original`, `área de trabalho/filtro da página/cartão Preto e branco`, `área de trabalho/filtro da página/cartão Melhorar` … | essa página sai no filtro (Preto e branco: só preto e branco, sem amarelo); as outras continuam como estavam (amareladas no Original). a pág… | **QUEBRA** (defeito A) |
| P-085 | o menu Filtro marca o filtro da página da vez — `menu/filtro_original`, `menu/filtro_preto_e_branco`, `menu/filtro_melhorar` … | o menu Filtro mostra marcado o filtro da página que está na tela, e acompanha ao trocar de página. | **QUEBRA** (defeito D) |
| P-084 | "Só neste pedaço": os quatro filtros do pedaço — `área de trabalho/filtro da página/só neste pedaço: Original`, `área de trabalho/filtro da página/só neste pedaço: Preto e branco`, `área de trabalho/filtro da página/só neste pedaço: Melhorar` … | o pedaço sai no filtro dele (Preto e branco numa página em Original: o papel do pedaço fica branco). a área desenhada depois fica gravada co… | cumpre |
| P-081 | "só nesta" / "todas" / "daqui em diante" (painel Filtro) — `área de trabalho/filtro da página/só nesta`, `área de trabalho/filtro da página/todas`, `área de trabalho/filtro da página/daqui em diante` | com "todas", todas as páginas saem em Preto e branco. "todas" leva o filtro desta página a todas; "daqui em diante" a esta e às seguintes (a… | **QUEBRA** (defeito A) |
| P-082 | ícone "Ver os filtros em tela cheia" / menu Ver > "Filtros em tela cheia" — `área de trabalho/filtro da página/Ver os filtros em tela cheia`, `menu/filtros_tela_cheia` | abre os filtros em tela cheia, na página da vez. **no projeto:** nada muda até "Usar". | cumpre |
| P-083 | os jeitos do "Só as letras" (Guardar a tinta forte / Guardar tudo / Guardar só o texto) e "Mais opções" — `área de trabalho/filtro da página/Mais opções`, `área de trabalho/filtro da página/Menos opções`, `o que fazer/Guardar a tinta forte` … | o jeito escolhido (na lista da área de trabalho, ou nos botões da tela "O que fazer") fica gravado nesta página. "Mais opções" abre as escol… | cumpre |
| P-090 | "Por página" / "Por motivo" — `área de trabalho/para revisar/Por página`, `área de trabalho/para revisar/Por motivo` | troca a lista; a mesma dúvida aparece nas duas. **no projeto:** nada muda. | cumpre |
| P-091 | botão do motivo ("Por motivo") — `área de trabalho/para revisar/motivo (o botão do grupo)` | vai para a primeira página com aquele motivo. **no projeto:** nada muda. | cumpre |
| P-092 | "está bom: todas" (um motivo, em todas as páginas) — `área de trabalho/para revisar/está bom: todas` | as páginas saem iguais. o aviso fica dado por visto nessas páginas (gravado); nada mais muda nas páginas. o motivo sai da lista e o número d… | cumpre |
| P-093 | "está bom em tudo" — `área de trabalho/para revisar/está bom em tudo` | o painel fica em 0. **no projeto:** nenhum aviso pendente; um Ctrl+Z traz todos de volta. | cumpre |
| P-094 | "ver a lista…" e a lista dos avisos — `área de trabalho/para revisar/ver a lista…`, `lista dos avisos/ver`, `lista dos avisos/fechar` … | só as marcadas ficam dadas por vistas. abre a lista grande; "ver" leva à página; "Selecionar todas"/"Nenhuma" marcam e desmarcam; "está bom … | cumpre |
| P-095 | "ver as N em tela cheia" (só as páginas com dúvida) — `área de trabalho/para revisar/ver as N em tela cheia` | abre a tela cheia só com as páginas com dúvida. | aguarda etapa 7, D-259 |
| P-100 | "está certo" (o que já vale hoje) — `área de trabalho/faixa do aviso/está certo` | a página sai igual. a página fica conferida (`revisada`), numa ação do histórico; os avisos dela ficam dados por vistos. o aviso da página s… | cumpre |
| P-101 | "está certo" com resposta (tique, contador, próxima dúvida) — `área de trabalho/faixa do aviso/está certo` | a miniatura ganha o tique, o contador de conferidas sobe, e a tela vai para a próxima página com dúvida. | aguarda etapa 7 (lista única 1.1) |
| P-102 | "próxima dúvida" — `área de trabalho/faixa do aviso/próxima dúvida` | vai para a próxima página que ainda tem aviso. **no projeto:** nada muda. | cumpre |
| P-103 | aviso: "está bom assim" — `aviso/revisar`, `área de trabalho/faixa do aviso/está bom assim` | a página sai igual. só este motivo desta página fica dado por visto; a página não muda. | cumpre |
| P-104 | aviso: "Deixar em branco" — `aviso/em_branco`, `área de trabalho/faixa do aviso/Deixar em branco` |  | cumpre |
| P-105 | aviso: "Tirar do livro" — `aviso/apagar`, `área de trabalho/faixa do aviso/Tirar do livro` |  | cumpre |
| P-106 | aviso: "Trazer de volta nesta página" — `aviso/misto_fora:tudo`, `aviso/misto_fora:rede` | o jeito do "Só as letras" desta página passa a ser o que guarda o que sumiu ("Guardar tudo" ou "Guardar a tinta forte"); só nela. | cumpre |
| P-107 | aviso: "usar mais escuro" / "usar mais fraco" — `aviso/forca:mais_escuro`, `aviso/forca:mais_fraco` | a página em Preto e branco sai com mais (ou menos) tinta. a força do preto desta página fica mais escura (ou mais fraca), só nela. | cumpre |
| P-108 | aviso: "Desfazer" (força do preto escurecida) — `aviso/desfazer_reforco` | a força volta à que a página tinha antes de o programa escurecer. | cumpre |
| P-109 | aviso: "usar Mágico pro nesta" — `aviso/filtro:magico_pro` | esta página fica no Mágico pro. **no PDF:** esta página sai no Mágico pro. | **QUEBRA** (defeito A) |
| P-110 | aviso: "usar o corte alargado" — `aviso/corte_alargado` | o corte desta página passa a ser o alargado (como corte à mão), com desfazer. | cumpre |
| P-111 | aviso: "Desentortar aumentando a página" / "Desfazer" do aumento — `aviso/desentortar_aumentando`, `aviso/desentortar_desfazer_aumento` | liga (ou desliga) o "desentortar aumentando" só nesta página. | cumpre |
| P-112 | aviso: "não dividir esta" — `aviso/nao_dividir` | a folha deixa de ser dividida. **no PDF:** a folha sai como uma página só. | cumpre |
| P-113 | aviso: "alinhar com as outras" — `aviso/alinhar_com_as_outras` | o ângulo desta página passa a ser o das outras. | cumpre |
| P-120 | seta das miniaturas ("Fechar as miniaturas" / "Abrir as miniaturas") e menu Ver > "Miniaturas" — `área de trabalho/miniaturas/Fechar as miniaturas`, `área de trabalho/miniaturas/Abrir as miniaturas`, `área de trabalho/miniaturas/… Fechar as miniaturas` … | nada muda (a escolha vai para as configurações do programa). a tira de miniaturas fecha (o cabeçalho fica) e abre; o menu Ver acompanha. | cumpre |
| P-121 | "Mais opções das miniaturas" (⋯): "Ver em pares" e "Lugar" — `área de trabalho/miniaturas/Mais opções das miniaturas`, `área de trabalho/miniaturas/… Ver em pares`, `área de trabalho/miniaturas/… Lugar > embaixo` … | "Ver em pares" junta as miniaturas em pares; "Lugar" põe a tira embaixo, à esquerda ou à direita. | cumpre |
| P-122 | "ver todas" / menu Ver > "Todas as páginas" — `área de trabalho/miniaturas/ver todas`, `menu/todas_as_paginas` | abre a grade "Todas as páginas" em "uma a uma", com a página da vez marcada. | cumpre |
| P-123 | "‹" / "›" (página anterior / próxima, barra de baixo) — `área de trabalho/barra de baixo/‹`, `área de trabalho/barra de baixo/›` | vai para a página de antes / de depois; "página N de M" acompanha. **no projeto:** nada muda. | cumpre |
| P-124 | Desfazer / Refazer (barra de baixo, painel Histórico, menu Editar) — `área de trabalho/barra de baixo/Desfazer`, `área de trabalho/barra de baixo/Refazer`, `área de trabalho/histórico/Desfazer` … | depois do desfazer, o PDF sai como antes da mudança. o projeto gravado volta a ser o de antes da mudança; o `acoes.jsonl` acompanha. volta a… | cumpre |
| P-125 | Desfazer aceso sem nada para desfazer — `área de trabalho/barra de baixo/Desfazer`, `menu/desfazer` | num livro recém-aberto, sem nada feito, o Desfazer fica apagado (barra de baixo e menu). | aguarda etapa 9 (Desfazer ligado sem nada) |
| P-126 | botão do Histórico (barra de baixo) / menu Editar > "Mostrar o histórico" — `área de trabalho/barra de baixo/Abrir ou fechar o painel Histórico`, `menu/historico` | abre (e fecha) o painel Histórico, com a lista do que foi feito. | cumpre |
| P-128 | linhas do painel Histórico (cada ação feita ou desfeita) — `área de trabalho/histórico/ação feita (volta até aqui)`, `área de trabalho/histórico/ação desfeita (refaz até aqui)` | sai como o trabalho naquele ponto. clicar numa ação de antes desfaz tudo o que veio depois dela; clicar numa desfeita refaz até ela. | cumpre |
| P-127 | "Confirmar e processar" (área de trabalho e menu Arquivo) — `área de trabalho/processar/Confirmar e processar`, `menu/processar` | o PDF é gravado no destino, com uma página por página do livro, na ordem. o destino do PDF fica gravado. com avisos pendentes, mostra antes … | **QUEBRA** (defeito C) |
| P-130 | "Antes de processar": "ver" / "continuar assim mesmo" / "está bom nas marcadas" / "Selecionar todas" / "Nenhuma" — `antes de processar/ver`, `antes de processar/continuar assim mesmo`, `antes de processar/está bom nas marcadas` … | com "continuar assim mesmo" o PDF sai; com "ver", nenhum PDF. "ver" leva à página e NÃO processa; "continuar assim mesmo" processa; "está bo… | cumpre |
| P-131 | "Confirmar e processar" (a janela): "Escolher pasta" / "Processar" / "voltar" — `confirmar e processar/Escolher pasta`, `confirmar e processar/Processar`, `confirmar e processar/voltar` | "Processar" grava o PDF na pasta e com o nome mostrados; "voltar" não grava nada. "Escolher pasta" troca a pasta mostrada; "Processar" segue… | cumpre |
| P-132 | "Já existe um arquivo com esse nome": "substituir o antigo" / "salvar como (2)" / "cancelar" — `caixa “Já existe um arquivo com esse nome”/substituir o antigo`, `caixa “Já existe um arquivo com esse nome”/salvar como pronto (N).pdf`, `caixa “Já existe um arquivo com esse nome”/cancelar` | "substituir" troca o arquivo antigo pelo novo; "salvar como (2)" grava o novo ao lado e não toca no antigo; "cancelar" não grava nada e o an… | cumpre |
| P-133 | lista de páginas ("usar em todas" do Cortar): "Selecionar todas" / "Nenhuma" / "Aplicar" / "Cancelar" — `escolher as páginas/Selecionar todas`, `escolher as páginas/Nenhuma`, `escolher as páginas/Aplicar` … | "Aplicar" leva o corte só às marcadas; "Cancelar" não muda nada. "Selecionar todas" marca todas, "Nenhuma" desmarca todas. | cumpre |
| P-134 | "Filtros em tela cheia": "‹" / "›" / "Fechar" / "Fechar sem mudar" / "Usar <filtro>" / "só nesta" / "todas" / "daqui em diante" — `filtros em tela cheia/‹`, `filtros em tela cheia/›`, `filtros em tela cheia/Fechar` … | a página sai no filtro usado. "Usar <filtro>" grava o filtro nesta página (com "todas", em todas; "daqui em diante", desta em diante), com d… | cumpre |
| P-135 | menu Ver > "Modo comparar" (abre a página ampliada comparando) — `menu/comparar` | abre a página grande com dois filtros lado a lado. **no projeto:** nada muda. | cumpre |
| P-148 | página ampliada: os filtros (Original / Preto e branco / Melhorar / Mágico pro) — `página ampliada/Original`, `página ampliada/Preto e branco`, `página ampliada/Melhorar` … | a página sai nesse filtro. a página da vez fica com esse filtro (o mesmo caminho do painel Filtro, com desfazer). a página grande passa a mo… | cumpre |
| P-149 | página ampliada: "<" / ">" / "+" / "-" / "ajustar à tela" / "comparar" / "X" — `página ampliada/<`, `página ampliada/>`, `página ampliada/+` … | nada muda. "<"/">" passam de página (a área de trabalho acompanha); "+"/"-" aproximam e afastam; "ajustar à tela" volta a caber; "comparar" … | cumpre |
| P-136 | "Ver lado a lado" na área de trabalho — `menu/lado_a_lado`, `área de trabalho/barra de baixo/Duas lado a lado` | as páginas em pares rolando, na barra de baixo e no menu Ver. | aguarda etapa 6, D-015/D-058 |
| P-137 | aviso de livro novo: "Rodar o automático…" / "agora não" — `área de trabalho/aviso de livro novo/Rodar o automático…`, `área de trabalho/aviso de livro novo/agora não` | livro novo mostra o aviso; "Rodar o automático…" abre a janela grande com a receita de sempre marcada; "agora não" fecha o aviso. | aguarda etapa 3, D-005/D-018 |
| P-138 | painel Automático: "Voltar para as opções" — `área de trabalho/automático/Voltar para as opções` | leva às escolhas do automático do livro, sem perder o trabalho. | cumpre |
| P-139 | painel Automático de verdade (rodar em todas / escolhidas / numa página, uma etapa só, ordem arrastando) — `área de trabalho/automático/Rodar` |  | aguarda etapa 3, D-002/D-003/D-004 |
| P-140 | Arquivo > "Livros recentes" — `menu/livros recentes` | lista os livros abertos antes; clicar num abre aquele livro. | cumpre |
| P-141 | Arquivo > "Escolher a pasta de saída..." — `menu/pasta_de_saida` | o próximo PDF vai para essa pasta. abre a escolha da pasta; a pasta escolhida aparece na próxima janela "Confirmar e processar". | cumpre |
| P-142 | Arquivo > "Nome do arquivo..." — `menu/nome_do_arquivo`, `caixa “Nome do arquivo”/OK`, `caixa “Nome do arquivo”/Cancelar` | o nome escolhido fica no destino gravado. **no PDF:** o próximo PDF sai com esse nome. pede o nome; OK guarda, Cancelar não muda. | cumpre |
| P-143 | Arquivo > "Voltar para as opções" — `menu/voltar` | leva à tela "O que fazer" do livro, sem perder o trabalho. | cumpre |
| P-144 | Arquivo > "Sair" — `menu/sair` | fecha o programa. **no projeto:** o trabalho fica gravado antes de fechar (nada se perde). | cumpre |
| P-145 | Página > "Ir para a página..." (Ctrl+G) — `menu/ir_para_pagina`, `caixa “Ir para a página”/OK`, `caixa “Ir para a página”/Cancelar` | pede o número; OK vai para a página; Cancelar fica onde está. | cumpre |
| P-146 | Ver > "Aproximar" / "Afastar" / "Ajustar à tela" — `menu/mais_zoom`, `menu/menos_zoom`, `menu/ajustar` | a página aumenta / diminui / volta a caber na tela. **no projeto:** nada muda. | cumpre |
| P-147 | Ver > "Tema": Escuro / Cinza / Claro — `menu/tema_escuro`, `menu/tema_cinza`, `menu/tema_claro` | as cores mudam na hora; fica guardado para a próxima vez. **no projeto:** nada muda. | cumpre |
| P-150 | "cancelar" (processando) — `processando/cancelar` | nenhum PDF pela metade fica no destino; se havia um antigo, fica igual. para o processamento e volta à área de trabalho. | cumpre |
| P-151 | "imprimir agora..." — `ficou pronto/imprimir agora...`, `imprimir agora/imprimir N páginas`, `imprimir agora/cancelar` … | NÃO manda nada à impressora no clique: abre a confirmação (impressora, páginas, cópias). | cumpre |
| P-152 | "montar para imprimir em A4 (com margens)..." — `ficou pronto/montar para imprimir em A4 (com margens)...` | o PDF do livro não muda. abre a janela "Montar para imprimir" sobre o PDF que acabou de sair. | cumpre |
| P-153 | "fazer outro" — `ficou pronto/fazer outro` | volta para a tela dos livros, com o cartão deste livro dizendo que o PDF foi gerado. | cumpre |
| P-160 | "gravar o arquivo para imprimir" — `montar para imprimir/gravar o arquivo para imprimir` | grava um PDF novo para a impressora (no livreto: folhas A4 deitadas, cada uma com duas páginas A5, na ordem da dobra); o PDF do livro não mu… | cumpre |
| P-161 | "mandar para a impressora..." — `montar para imprimir/mandar para a impressora...`, `caixa “Mandar para a impressora?”/mandar`, `caixa “Mandar para a impressora?”/cancelar` | pergunta antes ("Mandar para a impressora?"). | cumpre |
| P-162 | "parar" / "fechar" (Montar para imprimir) — `montar para imprimir/parar`, `montar para imprimir/fechar` | "parar" interrompe a montagem (nada fica pela metade); "fechar" fecha a janela sem gravar. | cumpre |
| P-170 | "Fechar" (Configurações) — `configurações/Aparência/Fechar`, `configurações/Atalhos de teclado/Fechar`, `configurações/Velocidade/Fechar` … | fecha a janela; o que foi mudado continua valendo. **no projeto:** nada muda. | cumpre |
| P-171 | "Restaurar todos os padrões" (Atalhos de teclado) — `configurações/Atalhos de teclado/Restaurar todos os padrões` | nada muda; as configurações do programa ficam sem atalho mudado. todos os atalhos voltam aos de fábrica (e o menu mostra a tecla de fábrica)… | cumpre |

Total: 129 · cumpre: 110 · quebra: 8 · aguarda etapa: 11 · não testada: 0
