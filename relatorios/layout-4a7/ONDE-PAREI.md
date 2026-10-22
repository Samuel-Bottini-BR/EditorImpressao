# Onde parei: rodada 14 e etapas 4 a 7 do layout (começado em 20/10/2026)

- Ramo: `layout-etapas4a7-2026-10-19`, a partir do `origin/fase-1` (`b8e9af7`).
- Worktree: `.claude/worktrees/layout-4a7` (junções: `modelos`, `gabarito\paginas`, `gabarito\scantailor-24-09`;
  nunca `Remove-Item -Recurse` nelas).
- Só mexo em `ui/` (e nos testes de tela). Outro agente (Fase 2, ramo `fase2-scantailor-itens-2026-10-19`) pode pôr
  controles mínimos nos painéis Filtro e Propriedades e listá-los em `layout\Botoes e funcoes para o layout.md`: ler a
  lista quando ele publicar e não desfazer.
- Fontes: `Plano de layout (rascunho).md` e `prototipo\21-rodada13-base.html` (pasta
  `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\`); a lista do que falta é o `ONDE-PAREI.md` do ramo
  `layout-impl-2026-10-08`.

## Tarefa 1: rodada 14 de perguntas

Situação: **pronta para a gerente publicar** (20/10).
- `rodada14-escolhas.json` + 53 imagens `22-rodada14-*.png` em `relatorios/layout-4a7/rodada14/` e também na pasta
  do HD (`...\plano-24-09-2026\layout\` e `\imagens\`, só arquivos novos). Seção "Rodada 14" acrescentada no fim do
  `Plano de layout (rascunho).md` (cópia de antes: `...antes-2026-10-20.md`).
- 8 perguntas (901 a 908): Todas as páginas de fábrica; onde troca o lado direito; painéis nos menus; peças novas
  no menu Ver; "o mesmo da página"; frase do aviso "desenho ou escrita"; "o do Editor" no Dividir; a "Conta" com o
  ângulo à mão.
- Fotos: programa de verdade (`saida_teste/prints_r14.py`, cópia em `rodada14/`), renderizado num QPixmap a 2,4 x
  (num QImage as cores da página saíam trocadas; com QT_SCALE_FACTOR=2 o Windows encolhia a janela para 1000 x 600).
- Falta na página (fora de `ui/`): grupo "22" em `docs/plano/para_a_pagina_de_layout.py`.

## Rodada 14: respostas (20/10) e rodada 14b

- Decididas (literais no fim do `Plano de layout (rascunho).md`): 901 A uma a uma; 902 C menu Ver e Configurações;
  903 B menu novo "Painéis"; 904 A peças novas no menu Ver; 906 C a frase que diz onde fica o "letra e traço";
  907 B "o do Editor". **A construir** (ainda não feitas): 903/904 (menus), 907 (Dividir), 902 (com a etapa da
  área de trabalho 1 e das Configurações), 901 (com "Todas as páginas").
- **906 e a junção:** o texto do aviso mora em `core/analise.py` (linhas 80-81). O Implementador 5 já trocou, no
  ramo `fase2-para-revisar`, para "Confira: se for escrita, marque como letra." (provisório). **Na junção vale a
  frase da 906 C:** "Não tenho certeza se esta página é desenho ou escrita. Confira: se for escrita, marque a área e
  escolha “letra e traço” no painel Propriedades." Não mexi em `core/` (fora da minha área): a gerente aplica.
- Refeitas como 909 (`r14b-mesmo-da-pagina`) e 910 (`r14b-endireitar-a-mao`): `relatorios/layout-4a7/rodada14b/` e
  na pasta do HD (`rodada14b-escolhas.json`, `imagens-rodada14b-*`). Esperam resposta: não construir.

## Tarefa 2: etapas 4 a 7

### Etapa 4: PRONTA PARA CONFERIR (20/10)
- Passo 1 (`871d7e7`): botões de marcar no Propriedades ("Marcação desta página", "Foto", "Pedaço"); fila de baixo
  vazia; painéis não espremem mais (NaoEspreme).
- Passo 2 (`f25c2e9`): painel "Filtro da página" decidido (fila dos filtros com a página pequena e a tecla; partes
  Ajuste, Só as letras, Limpar a sujeira, Mais ajustes, Só neste pedaço; "apagar página" depois de um risco; pé
  "Aplicar em"); listas com amostra (`ui/widgets/menu_com_amostra.py`); o `seletor_algoritmo_pb` continua com o
  mesmo nome e as mesmas linhas (para a junção com o ramo do agente da Fase 2).
- Passo 3 (`969a3a9`): itens de menu mortos ligados (Aproximar, Afastar, Ajustar à tela, Mostrar o histórico,
  Restaurar página apagada, Modo comparar, Livros recentes); teste de reversão
  `tests/test_menus_que_nao_faziam_nada.py` (falhou no código de antes: 6 itens sem ação).
- Acertos da janela de verdade (`d1f92a0`).
- GitHub: rodada 39472904661 (`969a3a9`) e **39476824315 (`d1f92a0`)**: 115 arquivos, 2055 passaram, 0 falharam,
  72 pulados; `teste_botoes` 215 ações, 0 falhas; `erros.log` vazio.
- Janela de verdade (`relatorios/layout-4a7/etapa4/`, roteiro `prints_etapa4.py`): 19 de 19 conferências.
- **Ainda antigo / fora desta etapa:** miniaturas (etapa 5); ícone da tela cheia dos filtros no título e a ferramenta
  provisória "Os quatro filtros" na trilha (etapa 6); "Na área marcada" (não existe no programa); "Marcar como" com 3
  jeitos (705 depende do processamento); "Mais ajustes" sem "Letra clara em fundo escuro" e "Letras com a cor delas"
  (não existem); "o mesmo da página" (espera 909); os 4 "Painel: …" do menu Ver (viram o menu "Painéis", 903 B, a
  construir); "Limpeza cuidadosa" em 3 itens da lista (no desenho da rodada 11 era um item com "leve·média·forte");
  tela "O que fazer" com o "Só as letras" ainda em botões; barra de baixo sem "antes/depois" e zoom.

### Rodada 14 construída (21/10): PRONTA PARA CONFERIR
- `aa5fe9d`: fase-1 (`31a9253`) juntado ao ramo.
- `8c28641`: 907 B ("o do Editor" no Dividir, "Para o livro todo", Histórico e tela "O que fazer");
  909 B ("Só neste pedaço" sem o botão de cima, nenhum aceso; clicar no aceso apaga); 910 A (a linha dos ângulos
  continua com o giro à mão; a frase vai para o balão do mouse da linha e da lista "Conta").
- `f228cd9`: 903 B (menu "Painéis": os cinco, "Fechar o painel", "Ícones da direita"; saíram os quatro "Painel: …"
  do Ver) e 904 A ("Miniaturas" e "Ícones da direita" no menu Ver). "Ver lado a lado", "Todas as páginas" e
  "Filtros em tela cheia" entram no Ver quando essas telas existirem.
- `e1ef0d3`: 910 com a página já medida (procura as medidas sem o ângulo à mão); prints em
  `relatorios/layout-4a7/rodada14-feita/` (4 de 4 conferências). GitHub 39554220929: 2081 passaram, 0 falharam; teste_botoes 213 ações, 0 falhas.
- 906 C: só na junção com o "Para revisar" (texto em `core/analise.py`, da gerente).

### Etapa 5 (21/10): construída, `744292d`
- `ui/widgets/miniaturas.py` (cabeçalho PÁGINAS/FOLHAS: alça, seta, três pontinhos com "Ver em pares", "Lugar",
  "Fechar"; "ver todas"); a tira em grade (`tira_miniaturas.definir_arranjo`: fila ou coluna, em pares como no livro
  aberto); `ui/widgets/todas_as_paginas.py` (grade "uma a uma" de fábrica, "em pares", "só as que precisam de
  atenção", clique vai à página). Lugares de encaixe com contorno azul ao arrastar a alça. 801 A e 808 A.
- Janela de verdade: 15 de 15 (`relatorios/layout-4a7/etapa5/`); testes de tela um por vez: 37 arquivos passaram;
  `tests/test_miniaturas_novas.py` novo.
- GitHub 39557719615: 118 arquivos, 2085 passaram, 0 falharam; teste_botoes 215 ações, 0 falhas; erros.log vazio. PRONTA PARA CONFERIR.
- Não feito: lembrar o lugar/aberta/em pares entre sessões (não decidido); clicar num par abrir as duas lado a lado
  (depende do "Ver lado a lado", que não existe); soltar a barra em qualquer lugar (a "C — tudo livre", para o fim).

### Etapa 6 (21/10): `dc51dec`, PRONTA PARA CONFERIR
- `ui/widgets/filtros_tela_cheia.py`: fila à esquerda, o escolhido grande, opções à direita (o ajuste do filtro),
  "Comparar com o Original" (desligada de começo) com a linha que se arrasta; "Aplicar em" e "Fechar sem mudar" /
  "Usar <filtro>" embaixo; teclas 1-4, setas, Esc. Abre pelo ícone no título do painel Filtro e pelo menu Ver.
  Escolher só mostra; "Usar" grava com desfazer. Janela: 8 de 8; GitHub 39561681378: success.
- Ressalvas: o ajuste mexido na tela cheia mostra só o filtro (sem o "Só as letras") até "Usar"; os outros ajustes
  do Preto e branco ficam no painel; o antes e depois não tem zoom.

### Etapa 7 (21/10): `60a0a3d` (Configurações em partes, 807 B + 707 C) e `e7a3843` (tela dos livros e livro aberto)
- Tela dos livros sem barra de menus (as teclas continuam), cartão "+" no começo, página vazia da tela 6, cartões
  menores (196 x 244), um clique abre o livro na tela inteira, duplo clique continua. Livro aberto: Voltar (Esc),
  Mais..., Continuar, Rodar o automático... (= tela "O que fazer" deste livro), Ver todas as páginas, Confirmar e
  processar... (continua e pede a confirmação), Onde está; folhas rolando (`ui/widgets/paginas_rolando.py`, só as
  visíveis, no máximo 40 guardadas) com a coluna de miniaturas, a pílula e "Ver lado a lado".
- Acertos do verificador (`verif-layout-4a5-2026-10-21`): "Melhorar" cortado na fila (letra 11 e margens menores);
  grade "Todas as páginas" borrada (folha guardada maior, 48 DPI, no máximo 160 guardadas).
- Janela: 12 de 12. GitHub 39564648498: success; 39566066549 (`448299e`, com o acerto do resumo): 121 arquivos, 2095 passaram, 0 falharam; teste_botoes 216 ações, 0 falhas; erros.log vazio.
- Acerto 3 do verificador (`448299e`): a linha-resumo da tela "O que fazer" dizia "(jeito: o do programa)"; troca feita na tela (`ui/tela_opcoes._com_o_nome_do_editor`), com teste de reversão (falhou no código de antes). O texto nasce em `core/pipeline.resumo_em_portugues` (fora da minha área).
- Filtro de velocidade 39559946683 (`31a9253` x `744292d`, etapa 5): igual em tudo (abrir -0,2%, trocar de página -0,4%, Mágico pro +0,0%, P&B +0,2%). Não mede a grade "Todas as páginas" nem o livro aberto (o teste não abre essas telas).
- Não feito: "Para revisar" e "Receita usada" no livro aberto (sem dado no resumo / receitas não existem); 804 B (aviso
  do livro novo: o livro ainda não abre direto na tela de trabalho); Configurações sem "Para todos os livros" e
  "Lado direito" (não existem).
- Ressalva: `test_girar_cartoes_e_previas.py` caiu uma vez no PC ("cannot get C stack") na rodada um-por-vez; repetido
  duas vezes, passou (23). Parecido com o "access violation" já anotado em `janela_principal` (06/10).

### Acertos do verificador de 21/10 (2ª leva, `8451256`)
- Livro aberto, uma página por vez, borrado: a folha passa a ser desenhada no DPI que dá a largura em pixels que ela
  ocupa na tela (escala do Windows incluída; 40 a 220 DPI); ao desligar o lado a lado, as pequenas são refeitas.
- "Todas as páginas" mole: cada folha no DPI que dá a altura do quadro em pixels (até 160 DPI; no máximo 120 guardadas).
- Testes de reversão em `tests/test_livro_aberto.py` (os dois falham no código de antes).
- "Algoritmo:" sem nada no Melhorar: esse rótulo não existe neste ramo (o painel Filtro diz "Jeito do preto e branco",
  em "Mais ajustes", só no Preto e branco). Ele existe no `fase-1` e no ramo `fase2-scantailor-itens-2026-10-19`
  (`QLabel("Algoritmo:")` na fila antiga): cuidado na junção para não voltar. Teste em `tests/test_filtros_tela_cheia.py`.

- GitHub 39621726467 (`f963cfd`): 121 arquivos, 2098 passaram, 0 falharam; teste_botoes 216 ações, 0 falhas; erros.log vazio. Janela: etapa 7 12 de 12, etapa 5 15 de 15.

### Acerto da grade (3ª leva do verificador, 21/10): PRONTO PARA CONFERIR
- Causa: a imagem guardada tinha o tamanho certo em pixels, mas era reduzida ao tamanho em PONTOS ao pintar e o Qt
  aumentava pela escala do Windows. Agora a redução é nos pixels de verdade do aparelho que pinta
  (`todas_as_paginas.razao_do_pintor` / `_reduzir_para_a_tela`); o mesmo nas miniaturas da tira, nos cartões grandes
  dos filtros e na capa dos cartões dos livros.
- Teste que mede o PINTADO: `tests/test_livro_aberto.py::test_a_grade_pinta_nitida_na_escala_do_windows` (listras de 1
  pixel pintadas a 2 pixels por ponto; falha no `f963cfd` com contraste 0, passa no novo).
- Janela: etapa 5 15 de 15; print ampliado `relatorios/layout-4a7/etapa5/7-todas-uma-a-uma-ampliado.png`.
- **Parado aqui a pedido do Samuel (21/10).** Nada começado depois disto.

## 22/10/2026: livro aberto refeito "como o UPDF" (conferência: "Está pior")
Pedido: "Eu não consigo ver a página direito, e elas estão de maneira muito ruim, da uma na internet como o updf
faz. Tem uma pagina maior que outra ali".
- `82175b4` e `d76b79e`: barra de baixo do livro aberto (`ui/tela_inicio.LivroAberto`) com "Uma página" (de
  fábrica) / "Duas lado a lado" (o "Ver lado a lado" de antes, que saiu do canto de cima), "Rolar sem parar" (ligado
  de fábrica), "Caber a página" (de fábrica) / "Caber a altura" / "Caber a largura" / "Tamanho real", e a pílula
  "página N de M · ir para" à direita (antes ficava por cima e cobria a folha). Escolha lembrada em
  `configuracoes.json` ("livro_aberto"; chave nova em `configuracoes.PADROES`, fora de `ui/`, só a preferência).
- `ui/widgets/paginas_rolando.py` refeito: as páginas de uma linha com a MESMA altura; folha desenhada no tamanho
  exato em pixels de onde é pintada e pintada 1 para 1 (com o dobro e redução por área quando o scan permite).
- Grade "Todas as páginas": guardada na altura exata, pintada 1 para 1 num pixel inteiro, folga de 3 pontos na
  margem, e desenha primeiro perto da página da vez.
- Medidas (janela de verdade, Graduale folhas 301-303, a 125%): par 545 e 528 pixels → iguais (570 / 769); nitidez
  da grade 0,69 → 0,99 (1600x821 antes: ainda cinza depois de 28 s); livro aberto 0,98 → 0,99-1,05 (o antigo já era
  nítido na janela; o defeito era o tamanho fixo de 615 pixels de altura, mesmo maximizada). Prints:
  `relatorios/layout-4a7/livro-updf/antes|depois` (`medidas.txt`). UPDF não está instalado no PC: sem print lado a lado.
- Testes de reversão em `tests/test_livro_aberto.py` (5 falham no `2eeec20`): par da mesma altura, livro aberto
  nítido a 125%, grade nítida a 125% (2 formatos), grade começa perto. 13 passam no novo.
- Cópia do código antigo usada para provar (`saida_teste/antigo`, worktree do `2eeec20` e depois do `d285b48`): removida no fim (sem junções).

## 22/10/2026: junção da Fase 2 (até `25504fb`) e filtros em tela cheia com todas as opções
Pedido (quadro l67-tela-cheia): "esse aqui é para mostrar só o antes e depois? mas no programa vai aparecer as opções
dos filtros né? o agente de layout fez já as opções de preto e branco que trouxemos do scan?" e "faça o recomendado".
- `d285b48`: `git merge 25504fb` (2.8, 2.9, 2.11, 2.15 e o conserto dos cartões; nada do 2.12). Um conflito, em
  `ui/tela_conferir.py` (a aba Filtro antiga virou o painel). **Onde cada controle foi parar** (painel "Filtro da
  página", parte "Mais ajustes"): os dez do ScanTailor (2.8) na lista "Jeito do preto e branco" (a mesma
  `seletor_algoritmo_pb`, só no Preto e branco); "Letra clara em fundo escuro" (2.9, todo filtro com ajuste); "Letras
  com a cor delas" (2.11, só no Preto e branco) e "Reduzir cores" (2.11, todo filtro com ajuste). "Mais ajustes"
  aparece agora em todo filtro com ajuste. O "Algoritmo:" antigo não voltou.
- `40df242`: tela cheia (`ui/widgets/filtros_tela_cheia.py`) com as mesmas opções do painel, com os mesmos nomes
  (rola à direita); a página grande pelo mesmo caminho do PDF (`renderizar_com_filtro`) numa cópia com o mexido;
  "Usar" grava cada opção pelo caminho do controle no painel (`TelaConferir._gravar_opcao_da_tela_cheia`).
- Testes em `tests/test_filtros_tela_cheia.py` (11 passam): opções por filtro; página da tela cheia = a gerada com as
  mesmas opções = a página depois de "Usar"; fechar sem mudar; livro já começado sai igual; reversão do ajuste
  mexido (falha no `d285b48`).
- Janela de verdade (`relatorios/layout-4a7/tela-cheia-opcoes/`, Boécio folha 7): 8 de 8 conferências.
- Achado do `core` (não mexi): a primeira vez que uma página é desenhada sai umas dezenas de pixels diferente das
  seguintes (grava a `geometria_das_zonas` e pode acertar um alerta do endireitar na primeira).
- GitHub 39797331030 (`b496573`): 130 arquivos, 2194 passaram, 0 falharam, 73 pulados; teste_botoes 216 ações, 0
  falhas; erros.log vazio. **PRONTO PARA CONFERIR** (livro aberto como o UPDF; tela cheia com as opções). Parado aqui.
