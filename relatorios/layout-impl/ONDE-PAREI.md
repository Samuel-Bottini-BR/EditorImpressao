# Onde parei: o layout no programa (atualizado em 12/10/2026)

- Ramo: `layout-impl-2026-10-08`, criado a partir do `fase-1`.
- Worktree: `.claude/worktrees/layout-impl`.
- Regras: só mexer em `ui/` e nos testes de tela; testes um arquivo por vez, com 3 GB de memória livre; push só neste ramo, nunca no `fase-1` (quem junta é a gerente).

Fontes das decisões:
- A página "Layout do Editor de Impressão" (rodadas 7 a 12, todas decididas; a 13 está aberta).
- O plano de layout, em `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\` (`Plano de layout (rascunho).md`, com as palavras do Samuel). A tela-alvo é `prototipo\21-rodada13-base.html` (prints `imagens\21-rodada13-tela-decidida*.png`).

## Etapa 1: temas (pronta, commit 7ebbc04)

Os três temas, com o cinza de fábrica. A troca fica no menu Ver > Tema e vale na hora. A escolha fica na chave "tema" do `configuracoes.json` (5280490).

**Para a gerente:** o comentário da chave "tema" em `configuracoes.py` (raiz, fora de `ui/`) ainda diz "a tela ainda guarda a escolha no tema.json"; ficou desatualizado.

**Falta (decidido na rodada 12, 707 C):** a troca de tema também nas Configurações (o desenho da tela de Configurações está na rodada 13, pergunta 807).

## Etapa 2: tela de trabalho sem abas (PRONTA PARA CONFERIR desde 09/10, commit a783bd9; o Samuel ainda não respondeu)

- As abas sumiram da tela (a `barra_abas` continua por dentro, escondida, e guarda a "aba" da vez).
- Trilha agrupada à esquerda (`ui/widgets/trilha_agrupada.py`): Dividir, Cortar, Endireitar; Formas; Contornar; Pincel; Pegar pela cor; Zoom; Mão; e "Os quatro filtros", PROVISÓRIO até o painel Filtro novo.
- Linha dos menus: os menus, um traço, a barra de opções da ferramenta e a barrinha de girar.
- Faixa do conferir embaixo da página; barra de baixo com "‹ página N de M ›", desfazer, refazer, o botão do Histórico, o livro e quantas faltam.
- "Confirmar e processar" ao lado das miniaturas (rodada 12, 704 A: fica assim).

## Etapa 3: a coluna de ícones da direita e os painéis (PRONTA PARA CONFERIR, 12/10)

Decisões seguidas: rodada 7, 203 D (ícones na borda, tudo fechado, com a seta); rodada 9, 401 A (empurra a página), 402 C (Propriedades conforme a ferramenta) e 405 C (Histórico: os dois); rodadas 10 e 11, 504 A e 602 A ("Para revisar" com as abas, abrindo sempre em "Por página").

### O que faz

- **Coluna de ícones na borda direita** (44 px), com a seta no alto que esconde e mostra os ícones. De fábrica: ícones à vista, nenhum painel aberto. O ícone do painel aberto fica azul; o "Para revisar" leva a bolinha laranja com quantas páginas têm dúvida. O mouse vira mãozinha em cima de cada ícone e o balão diz o nome.
- **O painel aberto fica ao lado da página** (300 px), nunca por cima; a página encolhe. Um por vez. Fecha clicando de novo no ícone ou no "x" do painel.
- **Para revisar:** abas "Por página | Por motivo"; abre sempre em "Por página". Por página: uma linha por página com dúvida, na ordem do livro, com o motivo e a frase do aviso (os textos vêm de `core/analise.descrever`; nada do conteúdo dos avisos foi reescrito); a página da vez fica destacada; clicar leva até ela. Por motivo: o que o painel já fazia (um botão por motivo, com a contagem; clicar leva à primeira).
- **Automático:** SÓ O QUE EXISTE HOJE. Mostra as etapas do livro (ligada ou desligada) com a escolha do livro de cada uma (jeito de dividir, conta do endireitar, beirada da folha vizinha, filtro do livro) e o botão "Voltar para as opções", que leva à tela "O que fazer" (o mesmo do menu Arquivo).
- **Propriedades:** muda conforme a ferramenta (ver "Propriedades", abaixo).
- **Filtro da página:** o conteúdo de antes (nome do filtro, a tecla, o deslizante e "só neste pedaço"), no painel novo. O painel Filtro decidido (fila de filtros e partes: rodada 9, 403 B) é a próxima etapa.
- **Histórico:** os botões Desfazer e Refazer em cima e a lista embaixo (até as 40 ações mais recentes). A ação desfeita continua na lista, apagada, com "(desfeita)"; clicar nela refaz até ali. Os botões de desfazer e refazer da barra de baixo continuam sempre à mão, e o botão do relógio abre e fecha este painel.

### Propriedades do Cortar, do Endireitar e do Dividir (rodada 12, 701 A e 706 B)

Os botões das três ferramentas **saíram da fila embaixo da página** (onde a do Cortar não cabia em 1280 x 657) e moram no painel Propriedades. São os mesmos botões, com as mesmas ações. Cada painel tem duas partes: "Só nesta página" (ou "Só nesta folha", no Dividir) e "Para o livro todo".

- **Cortar:** "não cortar esta", "usar o corte do programa", "usar em todas", "tamanho..."; as caixinhas "Espelhado (tecla M)", "Proporção travada (tecla T)" e "Mover conteúdo"; "Qualidade da prévia".
- **Endireitar:** as setas de 0,1 grau e o número; "aplicar em"; "deixar como veio"; "usar o ângulo do programa"; "Conta" com os dois ângulos medidos.
- **Dividir:** a lista "jeito:", "não dividir esta", "usar em todas" e "girar".
- **Para o livro todo:** mostra a escolha do livro (jeito de dividir, conta do endireitar, beirada da folha vizinha) e o botão "mudar nas opções do livro...", que leva à tela "O que fazer". Mudar a escolha do livro sem sair da página **não existe ainda no programa** (pede refazer a conferência do livro) e não foi inventado.
- **A faixa do conferir ganhou os três botões do desenho:** a sugestão laranja do aviso (quando o aviso tem uma), "está certo" e "próxima dúvida". O "está certo" e a sugestão que cada fila tinha são agora esses, iguais em todas as ferramentas.
- **Continuam embaixo da página (provisório):** os botões de Marcar (detectar automaticamente, foto, pedaço) e os dos quatro filtros. Com as ferramentas de marcar, o Propriedades mostra o "Marcar como" (que era um painel à parte).

### Mudanças só de texto (rodada 12)

- **710 B:** no Endireitar, "deixar como veio" (era "não endireitar esta") e "usar o ângulo do programa" (era "voltar ao automático"); no Cortar, "usar o corte do programa" (era "voltar ao automático"). As ações são as mesmas.
- **709 B:** a lista "aplicar em" do girar diz "só esta folha" e "todas as folhas"; a do endireitar, "só esta página" e "todas as páginas". O menu Página > "Aplicar o giro em" usa as palavras do girar. Os códigos de dentro (`core/girar.ALCANCES`) não mudaram.
- **702 C:** a linha dos menus mostra só o nome da ferramenta e os ajustes. A frase do que fazer está no balão da ferramenta, na trilha; a dica de cada ajuste ("a roda do mouse também muda...") está no balão do próprio ajuste.
- Conserto de acento na faixa do Cortar: "Arraste o retângulo" (estava "retangulo"; achado da rodada 12).

**Não mudou de propósito:** as frases gravadas no histórico de ações ("Não endireitar a página 3", "Voltar ao corte automático na página 3") e os códigos gravados no projeto.

### Arquivos

- `ui/widgets/paineis.py` (refeito): `ColunaDeIcones`, `ColunaDePaineis`, `Painel` e os cinco painéis.
- `ui/tela_conferir.py`: a faixa com os botões, o conteúdo do Propriedades das três ferramentas, a ligação dos painéis.
- `ui/estilo.py`: as cores e medidas dos painéis nos três temas.
- `ui/widgets/barra_girar.py` (`nomes_dos_alcances`), `ui/widgets/barra_opcoes.py`, `ui/widgets/trilha_agrupada.py`, `ui/barra_de_menu.py`: os textos.
- Testes: `tests/test_paineis.py` (refeito), `tests/test_paineis_na_tela.py` (novo), `tests/test_trilha_agrupada.py`, `tests/test_trilha_e_opcoes.py` e `tests/test_girar_na_tela.py` (acertados para o lugar novo e as palavras novas; nenhum deixou de conferir o que conferia).
- `teste_botoes.py` (raiz): passou a abrir o painel Propriedades e a clicar nos botões e caixinhas dele, nos da faixa e em cada ícone da coluna da direita. **Para a gerente:** é o único arquivo fora de `ui/` e `tests/` que mexi; sem isso o roteiro deixava de clicar nos botões do Cortar, do Endireitar e do Dividir.

### Testes e prints

(preenchido abaixo, em "Conferência da etapa 3")

## O que ainda falta (na ordem da obra)

4. **Painel Propriedades, o resto:**
   - os botões de Marcar (detectar automaticamente, "Esta página tem foto", "Ajustar o pedaço à figura", "usar em todas", "só nas próximas") ainda estão embaixo da página;
   - o bloco "Girar a folha" no alto do Propriedades e os botões pequenos no canto de cima da área da página (rodada 12, 703 B e D). **Hoje o girar continua na ponta da linha dos menus** (lugar provisório da etapa 2). Não foi mexido porque a rodada 13 (803) ainda pergunta se a lista "aplicar em" aparece nos dois lugares;
   - "Marcar como" com "iluminura ou pintura" e "moldura" (705 A): depende do processamento (Lista de espera do PLANO-DEFINITIVO).
   **Painel Filtro (R9 403 B):** os filtros numa fila, partes que abrem e fecham, escolhas em menu com amostra (R10 502 B), os nomes do conjunto 2 (R10 501) e o ícone da tela cheia no título. Nesta etapa sai o botão provisório "Os quatro filtros" da trilha e a fila de botões dele.
5. **Miniaturas (R8 301 A e R7 204/205):** cabeçalho "PÁGINAS" com a seta, os três pontinhos e a alça para arrastar.
6. **Tela cheia dos filtros (R11 601 A).**
7. **Tela inicial** (cartões, livro aberto em tela inteira, "Ver lado a lado").

**No Automático, não existe no programa e não foi construído:** receitas, ordem das etapas arrastando, "Rodar N etapas", "escolher páginas…", "ajustar ›" de cada etapa e a janela grande.
**No Para revisar:** a miniatura da página em cada linha e "ver as N em tela cheia"; na aba "Por motivo", os números de cada página (hoje o botão do motivo leva à primeira e o balão lista as páginas).
**No Propriedades:** "Onde dividir" com bolinhas (hoje é a lista "jeito:" de antes); "Retângulo do corte" (G6) e "Folga do corte" (não existem neste ramo); mudar a escolha "do livro todo" sem sair da página.
**Decididas, mas grandes, para depois das 7:** "Todas as páginas" em grade; a janela grande do Automático; os quatro jeitos do menu da direita e a área de trabalho 1 como opção; "Tudo livre".

## O que depende da rodada 13 (aberta; NADA disto foi construído)

- **801:** para onde vai o "Confirmar e processar" com as miniaturas fechadas ou de lado (hoje ele fica ao lado das miniaturas, 704 A).
- **802:** se o painel Propriedades abre sozinho ao escolher Cortar, Endireitar ou Dividir. **Hoje não abre:** de fábrica os painéis vêm fechados, e os botões dessas três ferramentas só aparecem depois de clicar no ícone do Propriedades. É a consequência mais visível desta etapa.
- **803:** a lista "aplicar em" do girar nos dois lugares ou só no painel (por isso o girar não saiu da linha dos menus).
- **804:** convite para rodar o automático num livro novo.
- **805:** a palavra "programa" na linha da conta do Endireitar ("ScanTailor +0,0° · programa −0,2°"), que agora aparece junto do botão "usar o ângulo do programa".
- **806:** um nome só para "daqui em diante" e "só nas próximas" (não mexidos).
- **807:** a tela de Configurações em partes (e o tema nas Configurações, 707 C).
- **808:** o botão de "Todas as páginas".

## Ressalvas e achados

(preenchido abaixo, em "Conferência da etapa 3")
