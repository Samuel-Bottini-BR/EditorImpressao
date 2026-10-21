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

### Próximas
- Etapa 5 (miniaturas: cabeçalho "PÁGINAS", seta, três pontinhos, alça de arrastar, 801 A, 808 A).
