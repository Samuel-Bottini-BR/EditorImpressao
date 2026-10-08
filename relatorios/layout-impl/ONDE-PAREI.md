# Onde parei: o layout no programa (08/10/2026)

O Samuel parou o trabalho em 08/10 para continuar depois, numa sessão do Claude na nuvem.

- Ramo: `layout-impl-2026-10-08`, criado a partir do `fase-1`.
- Worktree: `.claude/worktrees/layout-impl`.
- Regras: só mexer em `ui/`; mexer em `tests/` só no que depende das abas; testes um arquivo por vez, com 3 GB de memória livre; push só neste ramo, nunca no `fase-1`.

Fontes das decisões:
- A página "Layout do Editor de Impressão": coleção `decisoes`, todas com status "decidida", rodadas até a 11.
- O plano de layout, em `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\`.

## Etapa 1: temas (pronta, commit 7ebbc04)

Os três temas, com o cinza de fábrica. A troca fica no menu Ver > Tema e vale na hora. A escolha fica guardada em `tema.json`, na pasta de dados.

A gerente vai juntar esta etapa ao `fase-1` e pôr a chave "tema" nos PADROES do `configuracoes.py`. Quando isso chegar ao `fase-1`:
- trocar o `tema.json` pela configuração (em `ui/estilo.py`: `tema_guardado` e `_gravar_o_tema`);
- apagar o arquivo extra.

## Etapa 2: tela de trabalho sem abas (EM ANDAMENTO)

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
- **FALTA:** rodar de novo pelo menos estes, um por vez:
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

### Ainda falta na etapa 2

1. Rodar os testes acima.
2. Trazer o `fase-1` novo, quando a junção do Ctrl+Z, do endireitar (commit a742bf4) e dos nomes entrar. A aba Endireitar nova chega com:
   - a segunda linha: "inclinação:" com setas de 0,1°, o número em graus e "aplicar em";
   - "não endireitar esta" e "voltar ao automático", que seguem o "aplicar em";
   - "conta:" com os dois ângulos;
   - a alça, a grade e a linha-guia na página.

   Eles ficam na ferramenta Endireitar, na fila de botões embaixo da faixa, até a etapa 4. Atenção: a lista "aplicar em" do girar conta folhas e a do endireitar conta páginas, e as duas vão estar na mesma tela.
3. Conferir na janela de verdade, em 1000 x 600, que a fila de botões da ferramenta Cortar cabe. Em 1280 x 657 cabe; a etapa 4 resolve de vez.
4. Relatório da etapa 2 para a gerente, com os prints, e o commit final da etapa (este é um commit "EM ANDAMENTO").

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
