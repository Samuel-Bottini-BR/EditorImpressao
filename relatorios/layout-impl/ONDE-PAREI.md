# Onde parei: o layout no programa (atualizado em 09/10/2026)

O Samuel parou o trabalho em 08/10. Em 09/10 a etapa 2 foi retomada numa sessão do Claude na nuvem (Linux, sem Windows, sem DLLs do ScanTailor, sem gabarito, sem acervo). Ver "Retomada de 09/10" abaixo.

- Ramo: `layout-impl-2026-10-08`, criado a partir do `fase-1`.
- Worktree: `.claude/worktrees/layout-impl`.
- Regras: só mexer em `ui/`; mexer em `tests/` só no que depende das abas; testes um arquivo por vez, com 3 GB de memória livre; push só neste ramo, nunca no `fase-1`.

Fontes das decisões:
- A página "Layout do Editor de Impressão": coleção `decisoes`, todas com status "decidida", rodadas até a 11.
- O plano de layout, em `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\`.

## Etapa 1: temas (pronta, commit 7ebbc04)

Os três temas, com o cinza de fábrica. A troca fica no menu Ver > Tema e vale na hora.

**Feito em 09/10 (commit 5280490):** a escolha passou do `tema.json` para a chave "tema" do `configuracoes.json` (`ui/estilo.py`: `tema_guardado` e `_gravar_o_tema`). O `tema.json` antigo é lido uma vez só, para quem já tinha escolhido um tema não voltar ao cinza; nunca mais é gravado, e não é apagado. **Para a gerente:** o comentário da chave "tema" em `configuracoes.py` (raiz, fora de `ui/`) ainda diz "a tela ainda guarda a escolha no tema.json"; ficou desatualizado.

## Etapa 2: tela de trabalho sem abas (PRONTA PARA CONFERIR, falta a conferência no Windows)

### O que já faz

- **As abas sumiram da tela.** A `barra_abas` continua existindo por dentro, escondida, e guarda qual é a "aba" da vez. Assim tudo o que dependia da aba continua igual.
- **A trilha agrupada substitui a trilha antiga** (`ui/widgets/trilha_agrupada.py`):
  - **Ferramentas, de cima para baixo:**
    - Dividir a folha, Cortar as bordas e Endireitar (eram abas);
    - Formas: Retângulo, Oval;
    - Contornar: Laço, Ponto a ponto;
    - Pincel;
    - Pegar pela cor: Varinha mágica, Pegar tudo desta cor;
    - Zoom e Mão;
    - "Os quatro filtros", PROVISÓRIO: é a antiga aba Filtro e sai na etapa 4.
  - **Como funciona:** o grupo abre segurando o botão ou com o botão direito. O balão do mouse mostra a letra do atalho, também a das ferramentas escondidas no mesmo botão (pedido do Samuel na rodada 8). Só aparecem as ferramentas que o livro usa.
  - **Teclas:** escolher uma ferramenta de marcar, na trilha ou pela letra, leva para o modo de marcar.
- **Linha dos menus:** os menus, um traço, a barra de opções da ferramenta e a barrinha de girar.
  - As ferramentas que eram abas mostram o nome e a frase do que fazer.
  - A barrinha de girar fica só com os ícones quando a frase não cabe.
  - O lugar da barrinha de girar é provisório: ainda não foi decidido.
- **Faixa do conferir:** mais fina, logo embaixo da página.
- **Botões de cada ferramenta:** continuam embaixo da faixa, mais enxutos. É PROVISÓRIO; na etapa 4 eles vão para o painel Propriedades.
- **Barra de baixo:**
  - "‹ página N de M ›" (ou "folha" no Dividir); as setas "<" ">" dos lados da página ficaram escondidas;
  - desfazer, refazer e o botão do Histórico, que abre o painel;
  - o nome do livro, quantas foram conferidas e quantas têm dúvida.
- **"Confirmar e processar"** continua ao lado das miniaturas, porque o lugar dele não foi decidido.

### Testes

- **Arquivo novo:** `tests/test_trilha_agrupada.py`, com 14 testes, todos passando.
- **Arquivo mudado:** `tests/test_girar_na_tela.py`. Dois testes conferiam a barrinha "na linha das abas". Agora conferem que ela mora na linha dos menus, que os menus não são espremidos e a mesma regra de "só ícones". Nenhum deixou de conferir o que conferia.
- **`tests/test_trilha_e_opcoes.py`:** continua passando, mas a parte da trilha agora testa a trilha ANTIGA (`ui/widgets/trilha_ferramentas.py`), que não aparece mais na tela. Dizer isso à gerente; o arquivo pode sair numa limpeza futura.
- **Bateria (08/10, depois das mudanças principais):** os 39 arquivos de teste de tela passaram, um por vez (`saida_teste/rodar_testes_de_tela.py`).
- **Depois da bateria vieram dois ajustes pequenos:**
  - a dica da barra de opções ganhou espaço (`ui/widgets/barra_opcoes.py`);
  - o ícone de refazer passou a ser desenhado sem a função velha do Qt (`ui/tela_conferir.py`).
- **(feito em 09/10, na nuvem; ver "Retomada de 09/10")** rodar de novo pelo menos estes, um por vez:
  - `test_trilha_agrupada.py`
  - `test_girar_na_tela.py`
  - `test_trilha_e_opcoes.py`
  - `test_janela_cabe_na_tela.py`
  - `test_barra_de_menu.py`
  - o ideal é a bateria inteira de tela.

### Os 44 avisos do test_girar_na_tela

- **O que eram:** 44 avisos "DeprecationWarning: QImage.mirrored", e outros 12 iguais no `test_trilha_agrupada`.
- **A causa:** foram causados pela etapa 2. O ícone de "refazer" da barra de baixo era o de "desfazer" espelhado com uma função que o Qt 6 marcou como velha.
- **Conserto:** agora o espelho é feito com QTransform. Na bateria seguinte os dois arquivos passaram sem aviso nenhum.
- **Os outros avisos da bateria** (editor_selecao 85, trilha_e_opcoes 1, visualizador 9) já existiam na etapa 1. Vêm dos próprios testes (um jeito velho de criar o clique do mouse), não do programa.

### Prints

Ficam em `relatorios/layout-impl/etapa2/` (janela de verdade, cópia do Boécio, 1280 x 657, e 1000 x 600 no 9). Os 1 a 9 foram refeitos depois do último ajuste da barra de opções:

- `1-filtros-provisorio.png`
- `2-marcar-retangulo.png`
- `3-cortar.png`
- `4-endireitar.png`
- `5-dividir.png`
- `6-grupo-contornar-aberto.png`
- `7-marcar-laco.png`
- `8-marcar-laco-escuro.png`
- `8-marcar-laco-claro.png`
- `9-janela-minima-1000x600.png`

### Retomada de 09/10 (nuvem): o que foi feito

1. **O `fase-1` (4bf3888) foi juntado** (merge e8dd1fe). Um conflito só, no fim de `ui/tela_conferir.py` (os dois lados acrescentaram um bloco); ficaram os dois.
2. **Os controles do endireitar G5 estão na ferramenta Endireitar.** Como a junção trouxe tudo dentro de `_montar_aba_angulo`, eles caíram sozinhos no lugar provisório (a fila de botões embaixo da faixa): primeira linha "está certo · não endireitar esta · voltar ao automático · conta: [lista] [os dois ângulos]"; segunda linha "inclinação: [0,1°] [número] [0,1°] aplicar em: [lista]". A alça, a grade e a linha-guia aparecem na página. Testes novos em `tests/test_trilha_agrupada.py` conferem que eles aparecem só com a ferramenta Endireitar.
3. **Tema no `configuracoes.json`** (ver Etapa 1).
4. **Consertos achados nos prints:**
   - `escolher_ferramenta` com Dividir/Cortar/Endireitar/Filtros acendia o ícone e deixava a tela em Marcar (nenhum caminho do programa fazia isso, só o roteiro de prints; consertado e testado, f544f42);
   - a caixa do número do ângulo ficava com o número invisível (o campo de dentro tinha 1 pixel) no Qt 6.12 com a folha dos temas; agora a caixa tem as setinhas próprias com largura zero pela folha (`ui/estilo.py`, `campo_angulo`) em vez do `NoButtons` (5cc3737). No Qt 6.11 do PC do Samuel pode ser que o defeito nem aconteça; o contorno vale nos dois;
   - as setinhas dos botões de 0,1° não mudavam de cor ao trocar de tema (no claro sumiam); agora são redesenhadas (a079970);
   - a frase do Endireitar na linha dos menus ainda falava do jeito antigo ("Arraste sobre a página") e depois ficou longa demais; agora é "Gire pela bolinha azul ou pela linha laranja." A frase inteira continua na faixa.
5. **Testes (nuvem, Python 3.13, PySide6 6.12, offscreen, um arquivo por vez):** os 47 arquivos de teste que usam a tela. 43 passaram inteiros. Os outros 4, por ambiente:
   - `test_mesmo_livro_outro_caminho` (8 falhas): caminhos com barra invertida, só no Windows;
   - `test_gravura_no_processamento` (3 falhas): a DLL do detector de gravura, só no Windows;
   - `test_ocr_kraken` (1 falha): leitor de DLL, só no Windows;
   - `test_dialogo_tamanho_da_folha`: os 5 passam, mas o Python cai ao fechar (erro de memória do Qt no Linux). Acontece igual no `fase-1` puro, sem o layout.
6. **Prints da nuvem** em `/tmp/claude-0/prints-layout/` (fora do repositório, livro inventado; a letra do Linux é mais larga que a do Windows).

### Windows do GitHub (09/10, à noite)

- Rodada de cbc432a (da gerente): tudo passou, mas os prints mostraram os menus centralizados na tela inicial e no "O que fazer". Consertado em e306e1c (mola de peso zero no fim da linha dos menus) e conferido na rodada https://github.com/Samuel-Bottini-BR/EditorImpressao/actions/runs/37986429190: os 7 trabalhos terminaram com sucesso; nos prints, os menus ficam à esquerda nas telas 01 a 04 e no conferir.
- **Cortar em 1280 x 657, no Windows a 100%:** faltam uns 45 a 50 px. No fase-1 a fila ia de lado a lado da janela. Na etapa 2 ela fica entre a trilha (44 px) e o painel da direita (172 px), que vão de cima a baixo, como na base decidida (área de trabalho 2; "o painel empurra a página"). Em 08/10 só "cabia" porque o PC do Samuel amplia a tela em 125%. Sem decisão não há folga segura; as opções foram levadas à gerente: apertar espaços, segunda linha, fila passando por baixo do painel, letra menor nessa fila ou esperar a etapa 4.

### Ainda falta na etapa 2

1. **Conferir no Windows** (GitHub ou PC do Samuel): a bateria de tela e a janela de verdade.
2. **A fila de botões do Cortar não cabe** nos prints da nuvem, nem em 1280 x 657 ("voltar ao automático", "proporção travada" e "Mover conteúdo" cortados; em 1000 x 600 quase todos). No Windows, em 08/10, cabia em 1280 x 657. Conferir lá em 1000 x 600; a etapa 4 (painel Propriedades) resolve de vez. Se não couber, o provisório mais simples é a mesma segunda linha que o Endireitar já tem.
3. **As frases de Dividir e Cortar na linha dos menus** são cortadas sem reticências na nuvem ("...onde a folha di", "...corte da b"). Conferir no Windows; se cortarem lá também, encurtar como a do Endireitar.
4. Relatório da etapa 2 para a gerente e o commit final da etapa.

## Etapas seguintes (o plano aprovado pela gerente)

3. **Coluna de ícones na borda direita,** com a seta que esconde os ícones e tudo fechado de fábrica (R7 203 D). O painel aberto empurra a página (R9 401 A). Painéis:
   - "Para revisar" com as abas "Por página | Por motivo", sempre aberto em "Por página" (R10 504 A e R11 602);
   - Automático;
   - Histórico (R9 405 C).
4. **Painel Propriedades conforme a ferramenta (R9 402 C):** recebe os botões de Marcar, Cortar, Endireitar e Dividir que hoje estão embaixo da faixa.
   **Painel Filtro (R9 403 B):** os filtros numa fila, partes que abrem e fecham, escolhas em menu com amostra (R10 502 B) e os nomes do conjunto 2 (R10 501). O ícone da tela cheia fica no título do painel. Nesta etapa sai o botão provisório "Os quatro filtros" da trilha.
5. **Miniaturas (R8 301 A e R7 204/205):** cabeçalho "PÁGINAS" com a seta de abrir e fechar, os três pontinhos (Ver em pares, Lugar) e a alça para arrastar embaixo, à esquerda ou à direita junto da página.
6. **Tela cheia dos filtros (R11 601 A):** a fila dos quatro à esquerda, a página grande, as opções à direita e a chave "Comparar com o Original" com a linha arrastável. Embaixo, "Aplicar em", "Fechar sem mudar" e "Usar <filtro>"; teclas 1 a 4, setas de página e Esc.
7. **Tela inicial:**
   - cartões, o cartão "+" no começo da grade e a página vazia;
   - um clique abre o livro na tela inteira, com as páginas rolando e a coluna de miniaturas;
   - o botão "Ver lado a lado" sobre as páginas, no canto direito, que liga pares rolando com as miniaturas em pares.

**Decididas, mas grandes, para depois das 7:**
- "Todas as páginas" em grade.
- "Ver as N em tela cheia" das páginas a conferir.
- Janela grande do Automático, com "escolher páginas…".
- Os quatro jeitos do menu da direita e a área de trabalho 1 como opção.
- "Tudo livre", que fica para o fim da Fase 4.

## Perguntas para a próxima rodada de layout (não decididas, não entraram)

1. Onde ficam os botões de girar e o "aplicar em" do girar? Hoje estão na ponta da linha dos menus.
2. Onde fica "Confirmar e processar"? Hoje está ao lado das miniaturas.
3. A troca de tema fica no menu Ver ou nas Configurações?
4. "Marcar como" ganha iluminura ou pintura e moldura?
5. O que vai dentro de Propriedades para Dividir, Cortar e Endireitar, além dos botões que já existem?
6. Endireitar: onde ficam a segunda linha ("inclinação" e "aplicar em"), o "conta:" com os dois ângulos, e o "Conta do endireitar:" da tela "O que fazer"? Como diferenciar as duas listas "aplicar em" (a do girar conta folhas, a do endireitar conta páginas)?
7. As telas "O que fazer", "Ficou pronto!" e Configurações no layout novo.
8. Fundo atrás da página: o Samuel confere nos prints da etapa 1 se o fundo escuro do cinza está bom.
9. (09/10) A segunda linha do Endireitar custa uns 45 px de altura da página, e a fila do Cortar não cabe: a etapa 4 resolve, mas até lá vale a segunda linha também no Cortar?
10. (09/10) A frase da ferramenta na linha dos menus é cortada quando falta espaço: cortar com "…", encurtar as frases, ou deixar só o nome da ferramenta (a frase inteira já está na faixa do conferir)?
