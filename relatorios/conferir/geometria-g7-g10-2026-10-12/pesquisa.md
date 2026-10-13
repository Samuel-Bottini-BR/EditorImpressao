# Perguntas G7 a G10: o que o ScanTailor faz, o que o programa faz, o que já está decidido

**Data:** 12/10/2026 · **Quem:** agente pesquisador · **Pedido:** gerente (preparar as perguntas dos itens 2.13, 2.5, 2.4 e 2.6 para a página "Escolhas do Editor de Impressão").

**Nada no programa foi mexido e nada foi publicado.** Li o código do ScanTailor Advanced **v1.2.1** (commit `5eaac18`, cópia em `D:\programas\EditorImpressao-arquivos\ferramentas\scantailor-advanced-v1.2.1\`) e rodei as contas de verdade dele com um programa de teste pequeno (`scripts/caixas.cpp`), ligado na biblioteca que o teste de 01/10 já tinha compilado (`...\pesquisa-fase2-2026-10-01\build\Release\st_tudo.lib`). Não há ScanTailor de janela nem de linha de comando instalado neste PC (só o código-fonte); as saídas de 24/09 são do modo Misto e não mostram corte nem margens.

Legenda: **[lido]** = está no código; **[medido]** = rodei e olhei; **[dedução]** = conclusão minha.

## 1. A resposta em cinco frases

1. As quatro perguntas antigas do plano de geometria (G7 a G10) **já tinham sido respondidas em 05/10** (conferência 9); o que faltava eram as escolhas que apareceram depois, e ficaram **seis perguntas** (`escolhas-g7-g10.json`).
2. **Borda preta (2.13):** a busca de página do ScanTailor só tira faixa preta que vai reta de ponta a ponta; no Siebmacher 7 e 9 ela quase não corta, e quem tira o preto ali é a **caixa do conteúdo** [medido].
3. **Caixa do conteúdo (2.5):** acerta em muitas páginas, mas deixa de fora barra de moldura (Horas 14) e número de página sozinho no pé (Opus Majus 137), e o resultado **muda com o DPI declarado** da página [medido].
4. **Margens (2.4):** as contas são pequenas e claras; uma única folha muito maior (tabela dobrável) aumenta o tamanho de todas, e no ScanTailor é a pessoa que tira essa folha da conta [lido].
5. **Tamanho final (2.6):** o ScanTailor não tem papel-alvo; no nosso, o tamanho vale por página e a montagem dos cadernos dobra a largura, então "A4" hoje vira folha A3 [lido no nosso código].

| O que é | Licença | Roda aqui? | Roda no notebook do Kaique? |
|---|---|---|---|
| ScanTailor Advanced v1.2.1 (`select_content`, `page_layout`) | GPL-3.0 (obriga a distribuir com o código-fonte; liberado pelo Samuel em 17/09) | Sim [medido] | Sim, é só processador [dedução] |
| Qt 6.11 | LGPL-3 | Sim | Sim |
| Boost 1.78 (cabeçalhos) | BSL-1.0 | Sim | Não precisa |
| Scripts desta pasta: OpenCV (Apache-2.0), numpy (BSD), Pillow (HPND), PyMuPDF (AGPL-3) | as de cada um | Sim | não se aplica |

## 2. O que já estava decidido (não foi perguntado de novo)

| Item | Decisão | Onde está |
|---|---|---|
| 2.13 | "(a) Sim, desligada de fábrica; testar com o Siebmacher e os livros que eu indicar" | `relatorios/conferencia-samuel-2026-10-05-g.md`, G7 |
| 2.13 | "O programa sugere, o Kaique aceita" + "nós podemos alterar o corte sugerido, ou fazer um corte e mandar para todas as paginas e alterar em algumas paginas só [...] abrir uma aba para selecionar as que eu quero [...] ou também simplismente apertar num botão e selecionar todas" | `relatorios/revisar-decisoes/rodada-4/respostas-samuel.md`, `rv4-conserto-faixa` |
| 2.13 | Seletor só com "'Selecionar todas' e 'Nenhuma'"; tarja e moldura: "O Kaique escolhe por livro" (cortar ou pintar de branco); linhas pretas da beirada: "aviso no livro basta" | rodada 5 (`rv5-conserto-faixa`, `rv5-pag-egenloff-047`), rodada 4 (`rv4-pag-camoes-066`) |
| 2.5 | "(a) Trazer como opção 'seguir a moldura / o papel', desligada - eu quero pode escolher dentro do programa" | conferência 9, G8 |
| 2.5 | Corte comum com 1 mm de papel; folga ajustável para o livro + aviso onde o corte encosta em tinta; "eu tenho como configurar esse corte para todas as paginas e o programa me avisar onde o corte pode ter ficado ruim" | Registro de 01/10 e 05/10 (CORTE (a)); conferência 9, S2 |
| 2.4 | "(a) As do ScanTailor (10 mm dos lados, 5 mm em cima e embaixo) - Mas eu vou conseguir alterar isso né?"; "Todas as páginas do tamanho da maior: Sim" | conferência 9, G9 e G9b |
| 2.4 | Margem do lado da costura diferente, e o programa é que troca o lado: "o programa tem que conseguir perceber quando aumentar margem do lado direito e do lado esquerdo"; "cada pagina vai precisar de adequação diferente por serem lados diferentes (esquerdo e direito)" | "Vamos recapitular" (12/09), Graduale 223 e Siebmacher |
| 2.4 | Texto no meio da folha: "precisamos centralizar" (Horas 14), "centralizar no meio da folha" (Horas 13) | "Vamos recapitular" (é também o padrão do ScanTailor) |
| 2.6 | "(b) Avisar e não reduzir - avisar para eu reduzir manualmente, e ter uma opção para passar isso para todas as folhas [...] geralmente as folhas são impressas com 4 paginas cada uma [...] isso ai não pode interferir nisso" | conferência 9, G10 |
| 2.6 | "colocar esse texto e margem numa proporção de folha A4" | "Vamos recapitular", Siebmacher |

## 3. Item por item

### 2.13 Página dentro da borda preta

- **ScanTailor** [lido, `select_content/PageFinder.cpp`]: reduz a página a 150 DPI, passa para preto e branco e anda de cada beirada para dentro enquanto a linha inteira (95% do lado) for preta; para quando acha 10 linhas seguidas que não são. "Fine Tune Page Corners" empurra cada canto em diagonal enquanto ele estiver no preto. Dá para dizer o tamanho esperado da página em mm (ele escolhe, entre cinco jeitos de preto e branco, o que chega mais perto). Desligado de fábrica. "Aplicar em": esta, todas, esta e as seguintes, selecionadas, alternadas.
- **Medido:** Siebmacher 7 (2217 × 1712 pontos): caixa da página de 0 a 2195 na largura e de 27 a 1696 na altura; o preto da direita continua dentro, porque a folha é torta e o preto não chega a 95% do lado. Com o ajuste dos cantos: 0 a 2072 e 99 a 1645, que corta o enfeite de cima da moldura (a caixa do conteúdo começa em 67). No ljs47 (preto em volta toda) acha a página. Tempo: junto com as caixas do conteúdo, 0,5 s (Siebmacher) a 11 s (página de 2742 × 3750).
- **Nosso** [lido, `core/recortar.py`]: o corte procura a tinta, não o papel; tira borda sólida colada na beirada (`_apagar_bordas_solidas`, 80% da linha) e não deixa a folga trazer o escuro (`_parar_no_escuro`). No Siebmacher 7 e 9 o corte de hoje fica quase na folha inteira [medido], porque a beirada das outras folhas e o preto contam como tinta que não pode ser partida.
- **Quem resolve o Siebmacher** [medido]: a caixa do conteúdo do ScanTailor (109 a 1747 e 67 a 1435 no Siebmacher 7: a moldura justa). No 9 ela não para na moldura: desce até os pontinhos de sujeira do papel (até 1627 de 1712).

### 2.5 Caixa do conteúdo e guias

- **ScanTailor** [lido, `ContentBoxFinder.cpp`, `select_content/Task.cpp`]: a 150 DPI, tira como "sombra" o que tem risco comprido (200 × 14 pontos deitado, 14 × 300 em pé, mais o que encosta neles), limpa pontinhos, procura os maiores vazios, joga fora o que encosta na beirada, estima onde há texto e apara lado a lado. Roda **dentro** da caixa da página e é cortada por ela. Modos: automático, à mão, desligado.
- **Medido:** acerta a moldura na Horas 26 e no Siebmacher 7. Erra: Horas 14 (a barra dourada da esquerda fica de fora: a caixa começa em 249 e a moldura em 225) e Opus Majus 137 (o número "[ 115 ]", sozinho no pé, fica de fora: a caixa acaba em 1851 de 3576). **DPI:** na Horas 13 (moldura de 96 a 804 na largura), com 72 DPI declarados a caixa fica quase na folha inteira (104 a 1006 de 1024); com 150, fica por dentro da moldura (121 a 775). O implementador tem de passar o DPI certo e testar com os dois.
- **Guias** [lido, `page_layout/ImageView.cpp`, README]: linhas horizontais e verticais que a pessoa põe com o botão direito na etapa das margens; valem para o projeto inteiro (guardadas em mm); duplo clique no conteúdo gruda na guia mais próxima. As nossas (`ui/widgets/visualizador.py`, `guias_ativas`, `encaixar_no_ima`) são automáticas: centro e beiradas da folha.

### 2.4 Margens iguais e alinhamento

- **ScanTailor** [lido, `page_layout/Utils.cpp`, `Settings.cpp`, `Alignment.*`, `DefaultParams.cpp`]: margens fixas em mm em volta da caixa do conteúdo (10, 5, 10, 5: esquerda, cima, direita, baixo). O "tamanho do livro" é a maior largura e a maior altura (conteúdo + margens) entre as páginas que estão com "Match size with other pages". Cada página cresce até esse tamanho, e a sobra vai conforme o alinhamento: em cima / meio / embaixo, esquerda / meio / direita, "auto" (vai para o lado em que a sobra original era 3 vezes menor) ou "original" (a mesma posição que tinha na folha). De fábrica: meio e meio. "Auto Margins" mede a margem que a página já tinha. Margens diferentes por lado: "Apply to... every other page", à mão.
- **Folha muito maior:** entra na conta; para tirar, a pessoa desmarca o "Match size" naquela página. As "páginas diferentes" (`DeviationProvider`) só marcam com asterisco.
- **Nosso:** não iguala nada entre páginas; `core/folha.compor_na_folha` centraliza o recorte na folha escolhida, página por página.

### 2.6 Tamanho final

- **ScanTailor** [lido]: não tem papel-alvo; a saída é conteúdo + margens.
- **Nosso** [lido]: `ConfigPagina.tamanho_folha_cm` é **por página** (botão "tamanho..." da aba Bordas, A4/A5/Carta); se o conteúdo não cabe, `compor_na_folha` devolve sem mudar e a tela avisa; `conteudo_escala` e `conteudo_deslocamento` já existem ("Mover conteúdo"). `core/cadernos.impor_pdf` põe duas páginas lado a lado numa folha com **o dobro da largura** da maior página: página A4 vira folha A3.

## 4. As imagens: o que é de verdade e o que é simulação

- **De verdade:** o corte de hoje (`core.recortar.detectar_bordas`), as caixas do ScanTailor (código original), as páginas.
- **Simulação com conta minha:** "tira só o preto" (anda da beirada enquanto o meio do lado é escuro) e "alarga sozinho" (junta à caixa do ScanTailor as peças de tinta que o nosso corte já conhece e que a caixa atravessa, ou que estão sozinhas acima ou abaixo dela).
- **Contas do ScanTailor refeitas em Python:** margens e "tamanho da maior" (pergunta da tabela dobrável), com as caixas de verdade.
- **Desenhos em escala:** folhas impressas (A4, A5, A3) e linhas de apoio. Não são a tela do programa.
- As folhas brancas usam a página filtrada pelo Mágico pro do programa, só para o papel sair branco.

## 5. O que ficou em aberto ou não deu para confirmar

- Não rodei o ScanTailor de janela: as imagens mostram o resultado das contas, não a tela dele.
- A pergunta do papel parte de um palpite meu: que o Kaique imprime os cadernos em papel A4 dobrado ao meio. Está escrito na pergunta.
- "Alarga sozinho" foi testado só em três páginas (Horas 14, Horas 13, Opus Majus 137); falta rodar no gabarito inteiro antes de confiar.
- Borda preta em página torta ou curva (Matemática, Antiphon): não testei um jeito de "seguir o papel"; as duas opções da pergunta são retângulos.
- Não medi velocidade no programa (`teste_velocidade.py`); os tempos acima são do teste, com outras tarefas rodando no PC.

## 6. Como refazer

Da raiz da worktree: `scripts\compilar_caixas.ps1` (compila o teste), depois `scripts\rodar.ps1 passo0_paginas_extras.py`, `passo1_dados.py`, `passo2_imagens.py`, `montar_json.py`. Os rascunhos ficam em `saida_teste\geometria-perguntas\` (fora do git). Os números estão em `dados\`.
