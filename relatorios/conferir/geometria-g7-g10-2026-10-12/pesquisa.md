# Perguntas G7 a G10: o que o ScanTailor faz, o que o programa faz, o que já está decidido

**Data:** 12/10/2026 · **Quem:** agente pesquisador · **Pedido:** gerente (preparar as perguntas dos itens 2.13, 2.5, 2.4 e 2.6 para a página "Escolhas do Editor de Impressão").

**Nada no programa foi mexido e nada foi publicado.** Li o código do ScanTailor Advanced **v1.2.1** (commit `5eaac18`, cópia em `D:\programas\EditorImpressao-arquivos\ferramentas\scantailor-advanced-v1.2.1\`) e rodei as contas de verdade dele com um programa de teste pequeno (`scripts/caixas.cpp`), ligado na biblioteca que o teste de 01/10 já tinha compilado (`...\pesquisa-fase2-2026-10-01\build\Release\st_tudo.lib`). Não há ScanTailor de janela nem de linha de comando instalado neste PC (só o código-fonte); as saídas de 24/09 são do modo Misto e não mostram corte nem margens.

Legenda: **[lido]** = está no código; **[medido]** = rodei e olhei; **[dedução]** = conclusão minha.

## 1. A resposta em cinco frases

1. As quatro perguntas antigas do plano de geometria (G7 a G10) **já tinham sido respondidas em 05/10** (conferência 9); o que faltava eram as escolhas que apareceram depois, e ficaram **seis perguntas** (`escolhas-g7-g10.json`).
2. **Borda preta (2.13):** a busca de página do ScanTailor só tira faixa preta que vai reta de ponta a ponta; no Siebmacher 7 e 9 ela quase não corta, e quem tira o preto ali é a **caixa do conteúdo** [medido].
3. **Caixa do conteúdo (2.5):** acerta em muitas páginas, mas deixa de fora a moldura dourada e o título (Horas 14) e o número de página sozinho no pé (Opus Majus 137), e o resultado **muda com o DPI que se diz** da página [medido; números revistos em 13/10, seção 7].
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
- **Medido:** acerta a moldura na Horas 26 e no Siebmacher 7. Erra, **com o DPI que o programa diz** (seção 7): Horas 14 (a moldura dourada inteira e o título "TABLE" ficam de fora: a caixa vai de 253 a 932 e de 225 a 1211, e a moldura de 225 a 953 e de 163 a 1236), Horas 13 (a caixa fica por dentro da moldura: 119 a 775, com a moldura de 96 a 804) e Opus Majus 137 (o número "[ 115 ]", sozinho no pé, fica de fora: a caixa acaba em 1851 de 3576). **DPI:** em 12/10 medi com o DPI que o PDF diz (72 no Horas), e aí a Horas 14 perdia só a barra da esquerda (249 a 955) e a Horas 13 ficava quase na folha inteira (104 a 1006 de 1024).
- **Guias** [lido, `page_layout/ImageView.cpp`, README]: linhas horizontais e verticais que a pessoa põe com o botão direito na etapa das margens; valem para o projeto inteiro (guardadas em mm); duplo clique no conteúdo gruda na guia mais próxima. As nossas (`ui/widgets/visualizador.py`, `guias_ativas`, `encaixar_no_ima`) são automáticas: centro e beiradas da folha.

### 2.4 Margens iguais e alinhamento

- **ScanTailor** [lido, `page_layout/Utils.cpp`, `Settings.cpp`, `Alignment.*`, `DefaultParams.cpp`]: margens fixas em mm em volta da caixa do conteúdo (10, 5, 10, 5: esquerda, cima, direita, baixo). O "tamanho do livro" é a maior largura e a maior altura (conteúdo + margens) entre as páginas que estão com "Match size with other pages". Cada página cresce até esse tamanho, e a sobra vai conforme o alinhamento: em cima / meio / embaixo, esquerda / meio / direita, "auto" (vai para o lado em que a sobra original era 3 vezes menor) ou "original" (a mesma posição que tinha na folha). De fábrica: meio e meio. "Auto Margins" mede a margem que a página já tinha. Margens diferentes por lado: "Apply to... every other page", à mão.
- **Folha muito maior:** entra na conta; para tirar, a pessoa desmarca o "Match size" naquela página. As "páginas diferentes" (`DeviationProvider`) só marcam com asterisco.
- **Nosso:** não iguala nada entre páginas; `core/folha.compor_na_folha` centraliza o recorte na folha escolhida, página por página.

### 2.6 Tamanho final

- **ScanTailor** [lido]: não tem papel-alvo; a saída é conteúdo + margens.
- **Nosso** [lido]: `ConfigPagina.tamanho_folha_cm` é **por página** (botão "tamanho..." da aba Bordas, A4/A5/Carta); se o conteúdo não cabe, `compor_na_folha` devolve sem mudar e a tela avisa; `conteudo_escala` e `conteudo_deslocamento` já existem ("Mover conteúdo"). `core/cadernos.impor_pdf` põe duas páginas lado a lado numa folha com **o dobro da largura** da maior página: página A4 vira folha A3.

## 4. As imagens: o que é de verdade e o que é simulação

- **De verdade:** o corte de hoje (`core.recortar.detectar_bordas`), as caixas do ScanTailor (código original; desde 13/10 pela função do programa, `core.caixas_scantailor.achar_na_pagina`, com o DPI que o programa diz), as páginas.
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

Da raiz da worktree: `scripts\rodar.ps1 passo0_paginas_extras.py`, `passo1b_dpi_do_programa.py`, `passo2_imagens.py`, `montar_json.py`. O `passo1_dados.py` (com `compilar_caixas.ps1`) só é preciso para refazer as medidas de 12/10 (`dados\caixas-12-10.json`), de onde o passo 1b tira o corte de hoje. Os rascunhos ficam em `saida_teste\geometria-perguntas\` (fora do git). Os números estão em `dados\`.

## 7. Nota de 13/10/2026: as caixas refeitas com o DPI do programa

**Por quê.** Em 12/10 eu disse ao ScanTailor o DPI que o PDF diz. No Livro de Horas, no Graduale e no Marial o PDF diz 72, que não é a resolução de verdade. O programa diz outro número às ferramentas do ScanTailor (`core.caixas_scantailor.dpi_para_as_caixas`, a mesma conta do limpar pontinhos, do endireitar e da gravura): 138 a 142 no Horas, 129 a 131 no Graduale, 93 no Marial. O implementador apontou que com esse número as caixas são outras (`relatorios/caixa-conteudo-impl/ONDE-PAREI.md`, ressalva 2).

**O que fiz.** Juntei o ramo `fase2-caixa-conteudo` (`19e8e56`) ao meu e refiz as caixas com a função do programa (`scripts/passo1b_dpi_do_programa.py`, que grava `dados/caixas.json`; as de 12/10 ficaram em `dados/caixas-12-10.json` e, dentro do arquivo novo, em `scantailor_12_10`). `dados/mudou-com-o-dpi.json` lista as 14 páginas em que a caixa do conteúdo andou mais de 2 pontos. Refiz todas as imagens; **5 mudaram** (as outras 31 saíram idênticas, byte a byte).

| Página | DPI dito: antes → agora | Caixa do conteúdo: antes → agora (pontos) | O que muda no que se vê |
|---|---|---|---|
| Siebmacher 7 e 9 | 400 → 400 | igual | nada |
| Palatino, Opus Majus (inclusive a 137) | 400 → 400 | igual | nada |
| Horas 14 | 72 → 141 | 249–955 × 172–1231 → 253–932 × 225–1211 | antes só a barra dourada da esquerda ficava de fora; agora a moldura inteira e o título "TABLE" |
| Horas 13 | 72 → 138 | 104–1006 × 37–1435 → 119–775 × 221–1149 | antes quase a folha inteira; agora por dentro da moldura (a moldura fica de fora) |
| Horas 26 | 72 → 142 | 228–967 × 162–1262 → 227–970 × 161–1263 | nada (continua abraçando a moldura) |
| Horas 27 | 72 → 139 | 85–862 × 159–1214 → 85–802 × 160–1215 | melhora: a direita passa a parar na moldura |
| Horas 47 | 72 → 141 | 10–892 × 14–1416 → 30–893 × 57–1417 | fica mais justa na pintura (não olhei de perto) |
| Graduale 221 | 72 → 129 | 78–877 × 72–1350 → 84–961 × 43–1196 | melhora: pega o número da folha à direita e para na última linha |
| ljs47, página 46 | 150 → 279 | caixa da **página**: 137–2155 × 113–2649 → 156–2156 × 134–2650 | quase nada na caixa da página (a que a imagem mostra); a caixa do conteúdo muda muito (139–1966 × 135–2649 → 636–1931 × 305–2219), mas nenhuma pergunta a usa |

**As histórias das perguntas.** Só a da pergunta `g8-moldura-tinta-fora` mudou, e ficou mais forte: na Horas 14 o corte do ScanTailor perde a moldura inteira e o título, não só uma barra. O texto e duas legendas foram acertados; a pergunta e as opções são as mesmas. O exemplo do número da página (Opus Majus 137, 400 DPI) e o exemplo em que o corte acerta (Horas 26) continuam valendo. Nas outras cinco perguntas nada mudou: usam páginas de 400 DPI (Siebmacher, Palatino, Opus Majus) ou, na `g10-ajustar-todas`, caixas que não dependem desse DPI (o corte de hoje na página cheia; na pequena, a caixa alargada até a moldura, que deu a mesma).

**Ressalvas novas.**
- O DPI dito depende do DPI em que a página é desenhada. Usei, como o implementador, o PNG do gabarito (do tamanho do scan). No programa a página é desenhada na qualidade do projeto (por exemplo 300), e qual imagem vai à DLL (prévia ou PDF final) ainda não foi decidido (ressalva 3 dele): a caixa pode andar alguns pontos.
- No ljs47 (o PDF diz 96 DPI) o programa diz 279, e a caixa do **conteúdo** encolhe muito. Não olhei se ela corta texto; quem ligar o "até a moldura" em livro de folha grande precisa conferir.
- "Alarga sozinho" na Horas 14 agora junta 7 peças (a moldura e as letras do título), em vez de 1; o resultado é o mesmo retângulo de 12/10, com 3 pontos a menos à direita.
