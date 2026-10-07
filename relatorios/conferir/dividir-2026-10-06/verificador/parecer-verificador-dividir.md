# Parecer do verificador: item 2.1, dividir a folha (o do programa × o do ScanTailor), 06/10/2026

**NÃO ESTÁ PRONTO PARA JUNTAR. Falta um conserto pequeno, mas grave: em dois casos, uma folha some do PDF.**

O caso de verdade aconteceu num projeto do próprio Samuel, o Gradus Primus. Lá, a folha 2 tinha a página da esquerda apagada e "não dividir esta". No `fase-1`, o PDF sai com 139 páginas. Neste ramo, sai com 138: some a **página de rosto** ("Curso Básico de Latim, Gradus Primus", imagem b1). O mesmo acontece num livro novo quando a pessoa apaga a página da esquerda e depois aperta "não dividir esta".

O resto funciona como prometido:

- o código do ScanTailor é o original;
- o livro novo não divide sozinho;
- os dois jeitos e a troca numa folha funcionam na janela;
- o "não dividir esta" não repete mais a folha;
- o projeto antigo sai igual, ponto a ponto, fora a folha que some.

**Achado para a pergunta ao Samuel.** No livro aberto de verdade, **o do programa corta letras** em muitas folhas, e o implementador não viu: ele olhou 6 folhas do Hugon e 2 do Penido. Eu passei os dois jeitos nas 471 folhas do Hugon e nas 180 do Penido.

- O do programa corta o fim das linhas da página da esquerda, ou o começo das linhas da direita. No Penido 109, corta **no meio do texto** (imagens v1 a v5).
- O do ScanTailor ficou na dobra em todas as folhas que eu conferi.

Isso já acontecia no programa de antes, então não é defeito novo. Mas pesa na escolha do jeito de fábrica.

**Não é "aprovado":** só o Samuel marca.

> **Defeito conhecido (decisão do Samuel, 28/09):** moldura dourada e iluminura continuam sendo defeito conhecido. Este item não mexe no filtro: as prévias e o PDF do projeto antigo saíram idênticos aos do `fase-1`.

**O que foi conferido:** ramo `fase2-dividir`, commit `c936d81` (commits `977bf43` a `c936d81`). Comparei com:

- o `fase-1` (`a5ac122`);
- o ramo de antes, `fase2-misto-opcoes` (`a755087`).

Cada um rodou numa cópia `git archive`, com pasta de dados só de teste.

## Veredito, item por item

| # | O que | Como | Resultado |
|---|---|---|---|
| 1 | Código do ScanTailor sem mudança | máquina | **Bom.** Baixei o git do ScanTailor Advanced e conferi o `v1.2.1` (`5eaac18`). Os 50 arquivos novos são **idênticos byte a byte** ao original, e os 128 de `src/` também. A "cola" `adviseNumberOfLogicalPages` é igual às linhas 205-214 do `ProjectPages.cpp` original. As três linhas de montagem (`FilterData`, `otsuThreshold`, `estimatePageLayout`) são as mesmas do ScanTailor. Recompilei a DLL a partir das fontes da cópia, numa pasta só minha. Em 416 chamadas do dividir e 52 do limpar pontinhos, a DLL recompilada deu o mesmo resultado que a DLL enviada |
| 1b | Limpar pontinhos e detector de gravura iguais ao ramo de antes | máquina | **Bom.** O limpar pontinhos deu o mesmo resultado, ponto a ponto, nas 192 combinações (32 páginas-gabarito × 3 forças × 2 DPI). O detector de gravura deu as mesmas 32 máscaras. A `st_gravura.dll` é o mesmo arquivo (mesma soma) no ramo, no ramo de antes e no `fase-1` |
| 2 | Projeto antigo idêntico | máquina + janela | **Bom, menos uma coisa grave (ver Bugs).** Usei 3 projetos antigos: a cópia do Gradus Primus do Samuel e um Hugon e um Siebmacher montados pelo `fase-1`. Os três abrem com a mesma divisão. Comparando ponto a ponto com o `fase-1`, foram iguais **210 prévias e 210 páginas do PDF**. Na janela, o Gradus saiu com as mesmas 138 páginas que o `fase-1`, iguais a 72 e a 150 DPI. A diferença: a página que era só a metade direita de uma folha não dividida sai do PDF. No Siebmacher e no Hugon, isso é o conserto (a folha saía **repetida** no `fase-1`). No Gradus do Samuel, **a folha some** |
| 3 | Na janela real | janela (mensagens nativas) | **Bom, com 3 falhas.** Livro novo vem sem dividir: 8 folhas viram 8 páginas, sem a aba Onde cortar. Marcar "Dividir" mostra "Jeito de dividir"; escolher "o do ScanTailor" muda o resumo. Na aba Onde cortar funcionaram: trocar o jeito da folha (Siebmacher 74% → 57%; Hugon 121 53% → 46,5% e volta), "não dividir esta" na tabela do Opus, Ctrl+Z e Ctrl+Y. A folha que entrou inteira tem o botão apagado e mostra a dica. O PDF do livro de 8 folhas saiu com 12 páginas, **sem nenhuma repetida** (cada página casada com a folha de origem, imagem t2). **Falhas:** a folha que some (b3); o contador "N páginas vão para o PDF" errado; e o aviso ao trocar o jeito do livro (ver Bugs) |
| 3b | "Cortar a beirada da folha vizinha" | janela + olho | **Funciona, e come letra, como o implementador disse.** Saiu desmarcada. Num livro de 4 páginas, marquei, conferi e processei. O PDF saiu com a Escola 35 cortada dos dois lados, o "Cvij" e o fim das pautas do Graduale 221 cortados, e a Escola 7 rente à direita. O Livro de Horas saiu bem (imagem s1) |
| 4 | Olho nas imagens do implementador | olho | Abri as 31 imagens dele (27 + 4 do modo forçado). Concordo com o que ele viu, com duas correções. (a) No Hugon 1, o do programa corta a **44%**, não a 46%. (b) "Hugon: os dois dividem sem cortar letra" **não vale para o livro inteiro** (ver "O que eu achei a olho") |
| 5 | Tempo | máquina, alternando | **Abrir com o do ScanTailor ficou 50% mais lento: +35 s no Hugon.** O do programa e o "sem dividir" ficaram iguais ao programa de antes. Ver a tabela |
| 6 | Testes | máquina | **pytest arquivo por arquivo (102 arquivos): 1825 passaram, 59 pularam, 0 falharam.** **`teste_botoes.py`** (cópia `git archive`, `saida_teste` própria): **166 ações, 0 falhas** |

## Bugs (para a Lista de bugs)

### 1. Grave: uma folha some do PDF

**Quando acontece:** a página da esquerda está apagada e a folha está como "não dividir esta".

Novo em `modelos.Projeto.paginas_ativas` / `metade_sobrando`: a metade da direita de uma folha não dividida sai sempre da lista. Mas, se a da esquerda estava apagada, a da direita era a **única** página da folha, e a folha some. Isso acontece de dois jeitos.

- **Projeto antigo.** No Gradus Primus do Samuel (cópia), a folha 2 tem a página 3 (esquerda) apagada e "não dividir". No `fase-1`, o PDF tem **139** páginas; neste ramo, **138**. Some a página de rosto (b1). Na tela, a folha diz "Esta folha não vai ser dividida." e não avisa nada (b2).
- **Livro novo.** Na aba Filtro, "Apagar esta página" na página da esquerda da folha 4. Depois, na aba Onde cortar, "não dividir esta": a página da direita também fica apagada, e a folha 4 inteira some do PDF (b3; o PDF da janela saiu sem a folha 4).

### 2. Médio: a janela "Confirmar e processar" conta errado

Ela diz "139 páginas vão para o PDF, e 1 foram apagadas", mas o PDF saiu com 138. O contador não usa `paginas_ativas`.

### 3. Pequeno: dica errada no botão "dividir esta"

Numa folha que entrou inteira **com o livro já marcado para dividir** (Escola 7 no livro misto), a dica diz "volte e marque 'Dividir folhas ao meio'". Mas a caixinha já está marcada.

### 4. Pequeno: aviso errado ao trocar o jeito do livro

Trocar o jeito do livro depois de conferir pode mudar o número de páginas. No Livro de dividir, foram 15 → 14, porque o Opus deixa de ser dividido. Aí a conferência recomeça, com cópia do trabalho. O aviso diz "Isso acontece quando se muda a opção 'Dividir folhas ao meio'", mas o que mudou foi o jeito. O trabalho feito à mão se perde: o jeito da folha, "não dividir esta" e as páginas apagadas ficam só na cópia.

### Já existia no `fase-1`, não é deste item

Depois de "não dividir esta", a linha azul "arraste" continua desenhada na folha.

## O que eu achei a olho: o do programa corta letras no livro aberto

Passei os dois jeitos em **todas** as folhas de 4 livros, a 150 DPI, como a análise faz. Para cada corte, contei as letras que a linha atravessa: peças do tamanho de letra com tinta dos dois lados da linha. Depois olhei as faixas em volta do corte.

| Livro | Folhas | O do programa: folhas com letra atravessada | O do ScanTailor |
|---|---|---|---|
| Hugon (livro aberto, 471) | 471 | **58 folhas, 203 letras**. Olhei as 58 a olho: em mais de 40, a linha passa no fim das linhas da página da esquerda ou dentro do texto (v5) | 9 suspeitas, de 1 letra cada. Olhando, são **as 9 na sombra da dobra**, sem letra cortada (v6) |
| Penido (xerox, 180) | 180 | 139 com "suspeita". A medida se engana com a sujeira da xerox. Olhei 24 folhas: em várias, a linha corta **no começo das linhas da página da direita**. Na 109, corta **no meio do texto da esquerda** (v3, v4) | As suspeitas são a faixa escura da xerox; o corte fica dentro dela |
| Gradus (do Samuel, 70) | 70 | 15 (no máximo 7 letras) | 4 |
| Siebmacher (134, página deitada) | 134 | 64 | 36. Os dois partem a página; o certo é não dividir |

- **Hugon 119** (v1): o do programa (46%) corta a última letra de cada linha da página 232: "sempe|r", "Exempt|o", "es|t". O do ScanTailor (50%) corta no meio da dobra, e as duas páginas ficam inteiras.
- **Hugon 221** (v2): o do programa corta o fim das linhas ("Christu|s", "quæs|-"). O do ScanTailor fica na dobra.
- **Penido 109** (v3): o do programa corta a **43%**, no meio da página da esquerda. Metade de cada linha vai para a outra página ("As vir-" / "ultr|apassa"). O do ScanTailor (52%) fica na dobra.
- **Penido 113** (v4): o do programa (58%) leva a primeira letra de cada linha da página da direita. O do ScanTailor (53%) fica na dobra.

O defeito do do programa vem de antes: ele corta na borda esquerda da sombra da dobra. Quando o texto chega perto da dobra (no meio do Hugon, folhas 110 a 280), a linha cai no texto. **Isso pesa na pergunta ao Samuel:** hoje "o do programa" é o jeito de fábrica quando se marca "Dividir" (o implementador já marcou isso como pergunta).

## As imagens do implementador

| Página | O que vi |
|---|---|
| Siebmacher 7 | O do programa, a 57%, passa no meio do poema e da moldura. O do ScanTailor, a 74%, corta em cima da moldura da direita. O D (não dividir) fica certo |
| Siebmacher 9 | O mesmo. O do programa ainda corta a assinatura "J. Sib\|macher" no meio |
| Opus Majus 256 | O do programa não divide (certo). O do ScanTailor corta a tabela ao meio, na coluna "Tertia" |
| Escola 7 | O corte da sobra a 94% passa rente ao fim das linhas |
| Escola 35 | O corte da sobra corta o começo e o fim das linhas (10% e 87%) |
| Graduale 221 | A sobra leva o "Cvij" e o fim das pautas |
| Graduale 222 | O corte a 22% fica rente às claves e às primeiras letras, sem cortá-las |
| Horas 11 | A sobra tira só a beirada; a iluminura fica intacta |
| Palatino 5 | Nada muda |
| Hugon 1, 41, 121, 241, 361, 471 | Nestas 6, os dois acertam a dobra. O do ScanTailor fica no meio da sombra (1, 41, 361, 471) ou rente ao texto da direita (121, 241: perto, sem cortar). Mas, no livro inteiro, não é assim (ver acima) |
| Penido 3 e 91 | Os dois ficam no branco entre as páginas; a linha do endereço "obrascatolicas" é cortada nos dois |
| Modo "forçado" (4 imagens) | Concordo: no Hugon 121, o forçado joga fora uma página inteira (0 a 54%) |

## Tempo

**Medido alternando, pela mesma função que a janela usa, com pasta de dados de teste.**

O PC estava mais carregado que na medida do implementador: o "antes" deu 70 s, contra 46 s na dele. Por isso, vale a **diferença dentro de cada rodada**.

| Hugon, 471 folhas, abrir | Rodada 1 | Rodada 2 | Rodada 3 | Média | Diferença |
|---|---|---|---|---|---|
| Programa de antes (dividir marcado) | 67,1 s | 65,8 s | 77,8 s | 70,2 s | – |
| Agora, o do programa | 66,5 s | 72,4 s | 79,6 s | 72,8 s | +2,6 s (+4%, dentro da variação: −0,6 / +6,6 / +1,8) |
| Agora, sem dividir | 60,1 s | 72,7 s | 69,4 s | 67,4 s | −2,8 s |
| **Agora, o do ScanTailor** | **93,0 s** | **103,2 s** | **119,2 s** | **105,1 s** | **+35 s (+50%)**, uns 74 milésimos por folha |

| Escola, 199 folhas, abrir | Rodada 1 | Rodada 2 | Média |
|---|---|---|---|
| Programa de antes | 25,4 s | 23,9 s | 24,6 s |
| Agora, o do programa | 24,3 s | 22,7 s | 23,5 s |
| **Agora, o do ScanTailor + corte da sobra** | **60,2 s** | **56,4 s** | **58,3 s (+137%)**, uns 170 milésimos por folha |

- **Processar 10 páginas:** igual nos três jeitos (6 a 8 s). Sem dividir, leva 14 a 17 s, porque são 10 folhas inteiras, o dobro de área.
- **Trocar o jeito de uma folha** na aba Onde cortar: menos de 1,5 s, de olho no piloto.
- **A regra 6 do plano ("nenhum item pode deixar o programa mais lento")** é respeitada por quem não escolhe o ScanTailor. Quem escolhe paga uns 35 s a mais por livro de 471 folhas, ao abrir. A ideia do implementador, "calcular o do ScanTailor por trás", resolveria isso.
- **Não rodei o `teste_velocidade.py` oficial:** ele usa o Marial, que não é dividido, e agora o livro novo nem tenta dividir. A medida acima é a que mede este item.

## Ressalvas

1. **"Projeto do Samuel":** na pasta de dados dele, não há Hugon nem Siebmacher dividido. O Siebmacher dele está "sem dividir", e o PDF dele nem está mais no caminho gravado. Usei uma **cópia** do Gradus Primus dele, o único com folhas divididas (69 de 70), e montei Hugon e Siebmacher "antigos" com o código do `fase-1`. Os originais do Samuel não foram abertos pelo programa: conferi depois a soma e a data do `projeto.json` dele.
2. **Duas entradas minhas no `erros.log` de verdade do Samuel.** Dois scripts meus de imagem (não o programa pilotado) rodaram sem a pasta de dados de teste. Às 21:39:59 e às 21:40:34, cada um deixou um "servidor de páginas caiu adiantando a página…", porque o script terminou com a página seguinte sendo adiantada. Não apaguei: o arquivo é do Samuel. São as últimas linhas do arquivo (a partir da linha 7945).
3. **Apaguei uma pasta minha fora do projeto.** Na pasta de rascunho da sessão, apaguei um clone do ScanTailor que eu tinha acabado de baixar do repositório errado (`st_original`, do 4lex4). Foi segundos depois de criar, e não havia nada além do clone. A regra diz para não apagar nada fora do projeto, mesmo assim. O clone certo continua lá, em `st_original_v121`.
4. A medida de "letra atravessada" é automática e se engana com sujeira (Penido). Os números do Hugon foram conferidos a olho, nas 58 folhas (v5) e nas 9 suspeitas do ScanTailor (v6). No Penido, olhei 24 folhas.
5. A roda do mouse não foi testada (não funciona sem foco); este item não depende dela. O "comparar" e a tela ampliada não foram tocados.
6. O "dividir esta" numa folha que entrou inteira não existe. É limitação conhecida e escrita pelo implementador.

## As imagens que mais mostram ao Samuel a diferença entre os jeitos

1. `imagens/v1-hugon-119-o-que-sai-de-cada-lado.jpg`: o do programa corta a última letra das linhas; o do ScanTailor corta na dobra.
2. `imagens/v3-penido-109-o-que-sai-de-cada-lado.jpg`: o do programa corta no meio do texto; o do ScanTailor fica na dobra.
3. `../imagens/hugon_f041.jpg` (do implementador): o caso comum do livro aberto, em que os dois acertam e o do ScanTailor fica mais no meio da dobra.
4. `../imagens/opusmajus_p256.jpg` (do implementador): o do ScanTailor parte a tabela; o do programa acerta (não divide).
5. `../imagens/siebmacher_p009.jpg` (do implementador): página deitada; os dois erram, e o certo é não dividir.
6. `../imagens/escola_p035.jpg` (do implementador): o corte da sobra come letra dos dois lados.

![Hugon 119](imagens/v1-hugon-119-o-que-sai-de-cada-lado.jpg)

![Hugon 221](imagens/v2-hugon-221-o-que-sai-de-cada-lado.jpg)

![Penido 109](imagens/v3-penido-109-o-que-sai-de-cada-lado.jpg)

![Penido 113](imagens/v4-penido-113-o-que-sai-de-cada-lado.jpg)

![Hugon, 20 folhas em que o do programa corta letra](imagens/v5-hugon-20-folhas-o-do-programa.jpg)

![Hugon, as 9 suspeitas do ScanTailor: todas na sombra da dobra](imagens/v6-hugon-as-9-suspeitas-do-scantailor.jpg)

![A folha que some: página de rosto do Gradus Primus](imagens/b1-gradus-folha-2-que-some-do-pdf.jpg)

![Na tela, a folha diz que não vai ser dividida, e some do PDF](imagens/b2-gradus-folha-2-na-tela.jpg)

![Livro novo: esquerda apagada + não dividir esta = a folha 4 some](imagens/b3-apagar-esquerda-e-nao-dividir.jpg)

![Tela O que fazer: Dividir marcado, jeito o do ScanTailor](imagens/t1-tela-o-que-fazer-jeito.jpg)

![Onde cortar: não dividir esta na tabela do Opus](imagens/t2-onde-cortar-nao-dividir-esta.jpg)

![Onde cortar: o jeito só desta folha](imagens/t3-onde-cortar-jeito-da-folha.jpg)

![Corte da sobra no PDF: Escola 7, Escola 35, Graduale 221, Horas 11](imagens/s1-corte-da-sobra-no-pdf.jpg)

## Arquivos

- **Parecer:** `parecer-verificador-dividir.html` (`.md`, `.pdf`).
- **Dados** (`dados/`):
  - varredura dos 4 livros: `varre_*.json`;
  - projetos antigos: `antigo/*.json`;
  - DLL enviada × recompilada: `dll_*.json`;
  - pontinhos e gravura: `somas_*.json`;
  - pytest: `pytest_partes.log`;
  - tempos: `tempos.log`;
  - PDF da janela: `pdf_gui_1.json`.
- **Scripts:** `scripts/`.
