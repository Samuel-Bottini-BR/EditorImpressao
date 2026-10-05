# Consertos de 05/10 (3): a linha "Pedaço:" não espreme mais os botões, o ajuste só vale para figura, e o "Tirar o fundo" obedece ao pedaço

Ramo `pedaco-e-salvo-2-2026-10-05` (worktree `consertos3`), a partir do `38f327d` (parecer do verificador). Os itens 1 e 2 do parecer (página em Original e o "(2)") não foram mexidos. O implementador não junta nada ao `fase-1`.

| O quê | Commit | Tipo de teste |
|---|---|---|
| "Tirar o fundo" obedece ao "só neste pedaço" (conferência 14, FUNDO) | `1088e6b` | máquina + olho (Palatino 5, 9 e 10) |
| O ajuste só vale para figura, e um pedaço por vez (defeito 2 do verificador) | `479d4ad` | máquina (38 pedaços do gabarito) |
| A linha "Pedaço:" não espreme os botões; pedaço de texto explica o botão apagado (defeitos 1 e 2, na tela) | `50b9319` | máquina + prints da janela |

## 1. A linha "Pedaço:" espremia os botões (defeito 1)

**Por que acontecia:** a faixa de botões embaixo da página tem uma altura fixa, medida quando se troca de aba. A linha "Pedaço:" só aparece depois, quando se desenha o pedaço. As três linhas de botões ficavam espremidas na altura antiga, em qualquer tamanho de janela.

**O conserto (o mais simples):** quando a linha aparece ou some, a faixa é medida de novo. Quem cede o espaço é a área da página, que encolhe a altura de uma linha (43 pontos). A frase do aviso ficou mais curta e numa linha só, ao lado do botão; a explicação inteira está na dica do mouse. Não pus rolagem no painel porque ela esconderia botões, e a linha mais compacta não bastava sozinha: a faixa continuaria com a altura antiga.

**Na janela de verdade** (a janela principal inteira, fora da tela, com as fontes do Windows), Escola de Jesus 7:

| Tamanho | Sem pedaço | Com a linha "Pedaço:" | Altura dos botões (tem / precisa) |
|---|---|---|---|
| 1280 × 657 pontos, a 150% (o notebook do Kaique) | página 301 pontos | página 258 pontos | todos 39 / 39 |
| 1920 × 1040 pontos, a 100% | página 684 pontos | página 641 pontos | todos 39 / 39 |

Antes, o botão novo tinha 24 pontos de altura e precisava de 39.

![1280 × 657: a pintura com folga, aviso e botão aceso](prints/1280x657-b-pintura-com-folga.png)

![1280 × 657: o bloco de texto, botão apagado com a frase](prints/1280x657-c-pedaco-de-texto.png)

![1920 × 1040: a pintura com folga](prints/1920x1040-b-pintura-com-folga.png)

Os outros prints: `prints/1280x657-a-sem-pedaco.png`, `prints/1920x1040-a-sem-pedaco.png`, `prints/1920x1040-c-pedaco-de-texto.png`. As alturas medidas: `prints/alturas-1280x657.json` e `prints/alturas-1920x1040.json`.

## 2. Num pedaço de texto, o aviso dizia 47% e o botão cortava o texto (defeito 2)

**(a) O aviso e o botão só valem para figura.** Cada pedaço é medido: que parte da tinta dele está na **maior mancha contínua**. Figura (pintura, foto, gravura) é uma mancha só, e a maior mancha tem quase toda a tinta. Texto é feito de letras soltas, e a maior delas tem uma parte pequena.

- **Num pedaço de texto:** nada de aviso. O botão fica apagado, e ao lado dele aparece *"Pedaço de texto: o ajuste é só para figura."* A dica do mouse explica que ele cortaria linhas e letras, e que o pedaço fica como foi desenhado.
- **Na pintura da Escola 7:** continua igual. O aviso diz 17%, e o botão ajusta justo na pintura, sem a linha de texto e sem as legendas.

![À esquerda, o bloco de texto da Escola 7: o ajuste não muda nada (azul = laranja). À direita, a pintura com folga (laranja) e o ajuste (azul)](prints/escola7-texto-e-pintura.jpg)

**Medido em 38 pedaços de 14 páginas do gabarito**, na imagem que a aba Marcar usa (`figura-texto.json`):

| | Parte da tinta na maior mancha |
|---|---|
| Blocos de texto (Escola 7 e 35, Opus 165, Palatino 5, 9 e 10, Siebmacher 7, Boécio 8, Horas 47, Rhetorica 18) | 0,01 a 0,07 |
| Título da Escola 7 / partitura do Graduale 221 | 0,09 / 0,11 |
| Texto com a moldura preta do Palatino 9 | 0,07 a 0,15 |
| Título do Boécio 3 (pega o selo) / título no oval da Horas 11 | 0,31 / 0,39 |
| **Corte: 0,45** | |
| Inicial gravada do Palatino 9 | 0,51 |
| Fig. 7 e 8 da Opus 165 (desenho de traço) | 0,83 e 0,88 |
| Gravura do Boécio 3, retrato do Palatino 5, pinturas e fotos | 0,95 a 1,00 |

**Dois erros em 38, os dois sem estrago:**

- O **ornamento de baixo do Siebmacher 7** (cachos soltos numa página pequena) deu 0,29 e passa por texto. O botão fica apagado, com a frase. Erra para o lado seguro.
- **Texto da Horas 47 com um pouco da moldura dourada** deu 0,61 e passa por figura. Mas o ajuste não muda nada ali, porque a moldura segura o retângulo. Não aparece aviso.

**Por que não usei a medida do detector de gravura** (letras do tamanho de glifo): na resolução da aba Marcar ela erra para o lado perigoso. O título da Escola 7, numa faixa de uma linha, passaria por figura, e a gravura do Boécio sairia como texto.

**(b) O botão ajusta um pedaço só: o último desenhado em volta de uma figura.** Pedaço de texto nunca é ajustado, em qualquer ordem. Com o texto e a pintura da Escola 7 na mesma página, o botão ajusta só a pintura. Se houver dois pedaços de figura com folga, cada clique ajusta um, do mais novo para o mais antigo, e cada um se desfaz sozinho. Não escolhi "o pedaço selecionado" porque a aba Marcar não tem jeito de selecionar um pedaço.

## 3. O "Tirar o fundo" também obedece ao "só neste pedaço" (conferência 14, FUNDO)

**O pedido (Samuel):** "FUNDO: Sim, do mesmo jeito (só muda se alguém marcar um pedaço)". É do mesmo jeito do Original (`294cb91`). O pedaço obedece inteiro ao filtro dele, e o resto da página fica como o "Tirar o fundo" deixou. O comentário que dizia que a gerente ainda estava perguntando saiu.

- O pedaço é calculado na **página como veio**. Um pedaço em "Original" mostra o papel de verdade, e não o branco do fundo tirado.
- A **página sem pedaço sai idêntica**, e nada a mais é desenhado (o tempo não muda).
- A prévia e o PDF passam pela mesma função.
- Sem "Procurar gravura e letra" o pedaço não vale, como no Original. Sem ele a aba Marcar nem aparece.

**Testado com o Palatino do gabarito (PDF com camadas)**, pelo caminho do PDF (`pipeline.processar`), com o `38f327d` e com este ramo (`comparacao-fundo.json`):

| Página | O que o "Tirar o fundo" decidiu | Sem pedaço, antes × agora | Pedaço em Original na figura | Pedaço em Preto e branco no texto |
|---|---|---|---|---|
| Palatino 5 | página intacta (sai como veio) | idêntica | nada muda (a página já é a original) | só preto e branco dentro; fora, idêntica |
| Palatino 9 | fundo tirado ("conferir") | idêntica | a capitular com o papel como veio; fora, idêntica | só preto e branco dentro; fora, idêntica |
| Palatino 10 | fundo tirado | idêntica | o papel como veio dentro; fora, idêntica | só preto e branco dentro; fora, idêntica |

Antes, o pedaço era ignorado nos 6 casos com pedaço (a página saía igual à sem pedaço).

![Palatino 9, fundo tirado: à esquerda sem pedaço, à direita a capitular em "Original"](prints/fundo-palatino_p009-figura-em-original.jpg)

![Palatino 10, fundo tirado: o bloco de cima em "Preto e branco"](prints/fundo-palatino_p010-texto-em-pb.jpg)

![Palatino 5 (página intacta): o título em "Preto e branco"](prints/fundo-palatino_p005-texto-em-pb.jpg)

Na Palatino 10, o retângulo que eu desenhei passa no meio da última linha, e a metade de cima dela sai em preto e branco. Não é defeito: a borda é a desenhada, como no Original.

## 4. As páginas sem pedaço não mudaram

Fiz como o verificador: **6 páginas do gabarito × 4 filtros** (Escola 7, Opus Majus 20, Horas 11, Palatino 57, Graduale 221 e Siebmacher 7). Usei o caminho do "Confirmar e processar" (o `rodar_32.py`, sem mudança) e comparei uma cópia do `38f327d` com uma cópia deste ramo (`50b9319`), uma de cada vez (`comparacao-6x4.json`).

| Filtro | Idênticas, ponto a ponto | Processar as 6 (antes → agora) |
|---|---|---|
| Original | **6 de 6** | 31,5 → 40,3 s |
| Preto e branco | **6 de 6** | 32,1 → 30,1 s |
| Melhorar | **6 de 6** | 53,2 → 56,2 s |
| Mágico pro | **6 de 6** | 48,6 → 51,3 s |

**Os tempos não valem como medida.** O PC estava com outros agentes rodando e com a memória virtual livre entre 1,4 e 4 GB. Um filtro ficou mais rápido e os outros mais lentos, o que é ruído. As imagens são idênticas, e o caminho de uma página sem pedaço não ganhou nenhuma conta nova: só a leitura da marcação guardada, nas páginas no "Tirar o fundo".

![As 24 páginas deste ramo; em cada linha um filtro (Original, Preto e branco, Melhorar, Mágico pro)](prints/folha-de-contato-agora.jpg)

O "Tirar o fundo" sem pedaço também ficou idêntico nas três páginas do Palatino (item 3).

## 5. Testes de máquina

| O quê | Resultado |
|---|---|
| `pytest tests` inteiro, em 6 partes (o PC estava com pouca memória) | **1474 passaram, 0 falharam, 7 pularam.** Os 7 são os mesmos de antes: 6 do Kraken (o motor fica fora do git) e 1 que só roda com `OCR_22=1` |
| Testes novos | `tests/test_so_neste_pedaco_no_tirar_o_fundo.py` (7), `tests/test_ajustar_pedaco_so_figura.py` (11; 3 com a Escola 7 do gabarito, pulados sem a pasta) e 4 em `tests/test_ajustar_pedaco_na_aba_marcar.py`. Em `test_so_neste_pedaco_no_original.py`, o teste que cobrava que o "Tirar o fundo" ignorava o pedaço passou a cobrar o mesmo jeito do Original, e entrou um para a página sem pedaço |
| O teste da linha que espreme, sem o conserto | **Falha** ("a barra não cresceu": 62 → 62 pontos). Com o conserto, passa em 1280 × 657 e 1920 × 1040 |
| `teste_botoes.py` | **132 ações, 0 falhas.** Rodado numa cópia `git archive` do `50b9319`, com a pasta `saida_teste` própria; a `saida_teste` de verdade não foi tocada |
| 6 páginas × 4 filtros contra o `38f327d` | 24 de 24 idênticas (item 4) |
| Palatino 5, 9 e 10, "Tirar o fundo" sem pedaço, contra o `38f327d` | 3 de 3 idênticas (item 3) |

## Ressalvas

1. **A área da página encolhe 43 pontos quando a linha "Pedaço:" aparece.** Em 1280 × 657 ela já era pequena (301 → 258 pontos de altura). Fica para o plano de layout.
2. **Prints fora da tela**, na janela principal de verdade e com as fontes do Windows, mas sem clique de mouse. O pedaço foi posto direto no projeto. O caminho do mouse (desenhar → `_selecao_mudou` → `_avaliar_os_pedacos`) é o mesmo que o teste cobre.
3. **Figura ou texto é uma medida, não certeza.** Erra nos dois casos descritos acima, os dois sem estrago. Três ou mais desenhos soltos no mesmo pedaço passariam por texto, e o botão ficaria apagado. Um texto com moldura grossa só de um lado não foi medido.
4. **"Tirar o fundo" com pedaço custa um desenho a mais da folha**, só nas páginas com pedaço. O teste oficial de velocidade não foi rodado (PC sem memória, com outros agentes).
5. **O pedaço em "Original" numa página de fundo tirado** mostra o papel amarelado como veio (Palatino 9). Era o pedido ("do mesmo jeito"), mas o Samuel deve ver.
6. **Os retângulos da Palatino** foram escolhidos por mim, olhando a página. Não é um uso real do Kaique.

## Ideias para a Lista de espera

- Clicar num pedaço para escolhê-lo, para o botão ajustar um pedaço que não seja o último de figura.

## Bugs para a Lista de bugs

- Nenhum novo.
