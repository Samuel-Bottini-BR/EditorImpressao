# Passo 0 do plano da parte do Windows: terceira conferência de quem tentou quebrar (19/11/2026)

Esta é a terceira volta do mesmo verificador, que não escreveu nada do passo 0. Conferi os consertos do segundo
relatório (N1 a N9) e dos achados 6, 7 e 8, tentei quebrar de novo pelos caminhos que a gerente pediu e recontei a
lista. Não mexi no código entregue. As provas rodaram na cópia temporária, fora do projeto.

## Pedido

- Papel: quebrador
- Commit de partida: 6b29185e
- Ramo: passo0-porteiro-2026-11-19

## Arquivos que vou mexer

- `relatorios/passo0-2026-11-19/quem-quebrou/`

## Veredito

**NÃO ESTÁ PRONTO.**

**O que fechou:**
- A recontagem bate: 189 lugares em 176 itens.
- O print do caso real agora existe.
- O N4, o N5, o N7, o N8 e o N9 estão fechados.
- O N2 está fechado, mas com falsos alarmes novos.

**Dois furos graves continuam na proteção da lista:**
- **O "sim" do Samuel ainda é forjável.** Basta copiar um trecho de 12 letras ou mais da D-791, da D-799 ou da D-800,
  que já estão no Livro da versão de teste (R1).
- **O próprio ramo do agente escolhe com que versão se compara.** Se o nome da versão de teste for trocado no código,
  o teste do GitHub fica parado em vez de barrar (R2).

**Mais três problemas:**
- O porteiro ainda pode ser afrouxado pelo uso sem nenhum teste acusar (R3).
- O teste de velocidade inteiro foi para "depois da entrega", como se fosse escolha do Samuel. As palavras dele na D-800
  tratam de 5 lugares (R4).
- O jeito novo de seguir o apelido da biblioteca do Windows acusa linhas que não conversam com o Windows (R5).

## O que li

- O `relatorios/passo0-2026-11-19/ONDE-PAREI.md` na ponta `6b29185e`: "Como ficou cada achado da segunda volta",
  "Ressalvas" e "Perguntas para o Samuel".
- O código mudado de `dc0a5fc9` a `8a1f56d8`:
  - `livro.py` (o Livro da versão de teste);
  - `excecoes.py` (`problema_do_sim`);
  - `protecao.py` (os exemplos de cada palavra e o Livro da versão de teste);
  - `porteiro.py` (as 48 palavras e o seguir do apelido, `_apelidos_do_windows`);
  - `tabela_arquivos.py` e `texto_para_o_samuel.py`.
- Os testes `tests/test_conferencias_*.py` e a lista `tests/conferencias_excecoes.json`.
- O texto `lista-de-excecoes-para-o-samuel.md`, o `.pdf` e o print `prints/caso-real-reiniciar-agora.png`.
- A linha da D-800 no Livro.
- A rodada 44468529235 do GitHub: "success".

## O que conferi nas falhas, nas peças de fora e nos caminhos

### A recontagem: bate

- Meu script independente acha 124 linhas de conversa com o Windows pelas palavras. A lista tem mais 47 que só
  aparecem por um apelido da biblioteca. São 171 nessa conferência.
- Com 2 de `DETACHED_PROCESS`, 2 de licença de pasta e 14 números de decisão, dá **189**.
- Por passo: o plano conserta 113 (1, 41, 53 e 18); 58 ficam "depois da entrega"; 18 estão "fora do plano, a
  perguntar".

### O "sim" do Samuel (N1): não fechado

O Livro agora é o da versão de teste, e isso está certo. Mas a conferência aceita:
- qualquer decisão cuja linha tenha "lista de exceç" em algum lugar (hoje são três: D-791, D-799 e D-800);
- qualquer trecho de 12 letras ou mais da coluna das palavras daquela decisão. Essa coluna inclui o texto da própria
  gerente (por exemplo, "Chat, pergunta 2 da proposta").

Provei na cópia que estes quatro "sim" passam:
- D-791 com "não sei do que você está falando";
- D-791 com "as conferências automáticas";
- D-800 com "esses consertos deixa para depois";
- D-799 com `Aprova o plano?" → "ok`.

E provei o caso inteiro: um erro novo em `atualizacao.py` e o item na lista com o primeiro "sim" acima.
- O gancho sai com código 0.
- `protecao.comparar` contra a ponta do passo 0 não acha nada.

Sem internet, o gancho barra com código 3. Isso está certo.

### O nome da versão de teste: o agente controla

- O nome do ramo com que se compara (`VERSAO_DE_TESTE`, em `regras_dos_agentes/livro.py:21`) vem do código do próprio
  ramo.
- Troquei para `"fase-1"`, um ramo que existe e não tem a lista. `protecao.comparar` devolveu `None`, e o teste do
  GitHub trata `None` como "a versão de teste ainda não tem o porteiro" e fica parado
  (`tests/test_conferencias_protecao.py:58`).
- Apontar para um ramo do próprio agente, com um Livro inventado, vai pelo mesmo caminho.
- Esse nome não está entre os dados protegidos. Mesmo que estivesse, a comparação é feita com a versão que o próprio
  código escolhe.

### Afrouxar pelo uso (N3): pela metade

- Os exemplos tirados da lista da versão de teste pegam a palavra apagada da linha que junta as palavras (o caso do
  `msiexec`).
- Mas dois outros jeitos passam pela proteção:
  1. **Tirar a busca sem diferença de maiúscula** (o `re.I`, em `regras_dos_agentes/porteiro.py:251`). Os exemplos
     são todos em minúscula, então a proteção não acha nada. E `PowerShell.exe` deixa de ser achado.
  2. **Deixar os arquivos `core/testes*` de fora da conferência** (em `k01`, `regras_dos_agentes/porteiro.py:432`) e
     rodar `--diminuir`. A lista cai de 189 para 144, e os 45 lugares saem sem conserto. Os quatro arquivos de teste do
     porteiro passam (58, 17, 10 e 19 testes passando), e a proteção também.
- Só a conferência das mudanças rodada pela gerente pegaria, porque os arquivos do porteiro estão entre os que só a
  gerente muda. Isso já está nas ressalvas dele, mas o "N3 fechado" do ONDE-PAREI promete mais do que isso.

### O apelido da biblioteca do Windows (N2): consertado, com falsos alarmes

- `return kernel32, ...` é seguido, e `CDLL`, `getattr` e `creationflags` com o número numa variável agora são acusados.
- Mas uma função que devolve o **resultado** de uma chamada feita pela biblioteca vira "devolve a biblioteca", e quem
  a chama passa a contar. Isso contradiz o docstring (`regras_dos_agentes/porteiro.py:414`).
- Também conta o segundo nome de `kernel32, entrada = ...` e o método de mesmo nome de outra classe.
- Na lista de hoje, são pelo menos dois falsos:
  - `atualizacao.py:748`, `if _MARCA is not None or sys.platform != "win32":`. O `_MARCA` é o resultado de uma
    chamada da biblioteca, a marca que diz que o programa está aberto.
  - `teste_velocidade.py:2317`, em `despedir`, que chama `_sozinho_no_console()`. Essa função devolve um sim ou não.

### O teste de velocidade inteiro em "depois da entrega": não bate com a D-800

- A D-800 trata de "os 5 lugares", entre eles "o teste de velocidade lendo placa de vídeo e disco pelo PowerShell
  [...] 2". A prova escrita na linha da D-800 é "A lista de exceções do fim do plano tem só esses 5".
- Dos 54 lugares do teste de velocidade, uns 10 são essa leitura: `_placas_de_video` 5, `tipo_do_disco` 2,
  `_powershell` 1 e `_caminho_do_powershell` 2.
- Os outros 44 são coisas que ninguém explicou ao Samuel:
  - a memória do processo (`_pico_pelo_windows` 7, `_memoria_gb` 1);
  - a janela preta (17);
  - impedir o computador de dormir (`_pedir_ao_windows` 4);
  - a classe da janela (4);
  - o registro (3).

### O texto para o Samuel (achado 8 e N6): o print fechou, o resto não

- O print é de verdade: a janela de versão nova de 18/11, com "Reiniciar agora" circulado e três frases em vermelho e
  preto.
- A primeira linha diz o que é e onde fica, e o texto diz o que a conferência não faz.
- Mas o texto diz "como você escolheu em 19/11 (58 lugares, nos mesmos três pedaços [...] a memória, a janela preta)".
  Isso apresenta como escolha dele o que ele não escolheu (R4).
- E 5 dos 18 lugares da pergunta nova são programas abertos "sem janela preta" (`CREATE_NO_WINDOW`), que não mudam
  nada no Windows (R6).

### Os outros: fechados de verdade

- **N4:** o rótulo de pronto em `relatorios/outro/quem-quebrou/` e em `relatorios/quem-quebrou/` agora é barrado; na
  pasta do próprio trabalho, passa.
- **N5:** `creationflags=0`, "self-service" e "hku:" não acusam mais.
- **N7:** o f-string comum com `{}` não esconde mais o número de decisão.
- **N8:** um arquivo novo de `core/` recebe todas as regras, e a gerente é avisada.
- **N9:** conferido.
- **Os vizinhos de antes:** `sc` numa lista, `net stop`, `taskkill`, `-ComObject`, `Get-PhysicalDisk` e `importlib`
  com `winreg` agora são acusados.
- **O que ainda escapa e não é defeito**, porque o texto diz "escrito com as palavras que ela conhece": `vssadmin`,
  `setx`, `bitsadmin`, `wscript` e textos montados em pedaços.

### O resto

- Nada mudou fora de `regras_dos_agentes/`, `ganchos/`, `tests/test_conferencias_*`, da lista e de
  `relatorios/passo0-2026-11-19/`.
- O porteiro inteiro leva 16 s (antes, 11 s).

## Caminhos que o outro não listou

- O nome da versão de teste e o caso "a versão de teste não tem a lista": hoje, os dois desligam a proteção (R2).
- Afrouxar pelo uso:
  - tirar o `re.I`;
  - mudar o que fica de fora em `k01` ou em `e_programa`, e depois rodar `--diminuir` (R3).
- O "sim" com um trecho do texto da gerente, dentro da coluna das palavras (R1).

## Falhas não pensadas e resultado não conferido

- **Resultado não conferido:** a proteção dá `None` e o teste para, com o motivo "ainda não tem o porteiro". Isso
  acontece também quando o ramo do agente aponta para o lugar errado (R2). Ficar parado parece com "passou", e não é.
- **Falha não pensada:** `--diminuir` aceita qualquer diminuição. Se a regra encolheu, os lugares saem da lista sem
  conserto, e nenhum teste do GitHub percebe (R3).
- **Texto que não bate com o código:** os itens 2 e 12 de "Como ficou cada achado (primeira volta)" no ONDE-PAREI
  ainda dizem "125", "conta só a linha onde a biblioteca é pega" e "o título do pedido dá a etiqueta". O código de hoje
  faz diferente (R7).

## As regras que conferi

- **CLAUDE.md §11.12:**
  - ponto 2, nada dado como feito sem conferir: pela metade (R1, R2);
  - ponto 3, a lista do que pode falhar: faltaram os casos de R2 e R3;
  - ponto 1, uma peça só: cumprida.
- **CLAUDE.md §11.13**, no texto para o Samuel:
  - regra 3, print que prova: cumprida;
  - regras 1, 2, 7 e 9: cumpridas;
  - regra 10 e a regra 7 do §11 (só o que ele mandou): não cumpridas para os 44 lugares do teste de velocidade (R4);
  - regra 6: uma parte da pergunta trata de bandeira que não é erro (R6).
- **Cada decisão tocada:**
  - D-791: pela metade (R1, R2, R3);
  - D-800: não cumprida no alcance (R4);
  - D-796, D-798, D-792 e D-784: cumpridas;
  - D-605: cumprida (nada fora dos arquivos do pedido mudou);
  - D-767, D-785, D-786, D-787 e D-797: cumpridas.

## Achados

Os números começam com "R" (terceira volta). Os achados antigos que continuam abertos ficam assim:
- 6 e N3: pela metade (R2, R3);
- 7 e N1: não fechados (R1);
- 8 e N6: pela metade (R4).

1. **R1, grave: o "sim" do Samuel continua forjável** (`regras_dos_agentes/excecoes.py:135`, `regras_dos_agentes/livro.py:21`).
   - Qualquer trecho de 12 letras ou mais da coluna das palavras da D-791, da D-799 ou da D-800 passa. Isso inclui o
     texto da própria gerente.
   - Provado: um item novo com `{"decisao": "D-791", "palavras": "não sei do que você está falando"}` passa no gancho
     (código 0) e na proteção (nenhum achado).
   - O próprio ONDE-PAREI diz "A D-791 de hoje não serve sozinha", mas o código aceita.
   - Destino: consertar. O "sim" tem de apontar para uma decisão que registre aquele "sim" e nomeie o que ele abre:
     para um item novo, o arquivo e o texto do item; para a lista inteira, quantos lugares e o commit lido. As decisões
     que só falam da lista em geral (D-791, D-799, D-800) não podem valer.
2. **R2, grave: a versão com que se compara é escolhida pelo código do próprio ramo, e "não achei a lista lá" vira
   teste parado** (`regras_dos_agentes/livro.py:21`, `regras_dos_agentes/protecao.py:138`,
   `tests/test_conferencias_protecao.py:58`).
   - Provado: com `VERSAO_DE_TESTE = "fase-1"`, `protecao.comparar` dá `None`.
   - Destino: consertar.
     - O nome da versão de teste vem de fora do ramo do agente. Por exemplo, do workflow do GitHub, no ramo dos testes.
     - Depois que o passo 0 for juntado, "a versão de teste não tem a lista" vira falha, nunca teste parado. Por
       exemplo, com uma marca no workflow que a gerente liga ao juntar.
3. **R3, médio: o porteiro ainda pode ser afrouxado pelo uso sem nenhum teste acusar** (`regras_dos_agentes/porteiro.py:251`
   e `regras_dos_agentes/porteiro.py:432`).
   - Provado de dois jeitos: tirando o `re.I`, `PowerShell.exe` deixa de ser achado; e deixando `core/testes*` de fora
     da conferência e rodando `--diminuir`, a lista cai de 189 para 144.
   - Nos dois casos, os quatro arquivos de teste do porteiro e a proteção passam.
   - Destino: consertar. A proteção roda o porteiro da versão de teste (código em que se confia, buscado de lá) neste
     ramo e compara com a lista. Assim, nenhum lugar sai da lista enquanto o porteiro de lá ainda o acha. Ou, no mínimo,
     escrever nas ressalvas que o "N3" só cobre as palavras, e não o resto do código do porteiro.
4. **R4, médio: o teste de velocidade inteiro (54 lugares) foi para "depois da entrega (D-800)", mas a decisão do
   Samuel trata de 5 lugares** (`regras_dos_agentes/excecoes.py:63`).
   - A D-800 diz "o teste de velocidade lendo placa de vídeo e disco pelo PowerShell [...] 2", e a prova escrita nela
     é "A lista de exceções do fim do plano tem só esses 5".
   - Uns 10 lugares são essa leitura. Os outros 44 (a memória do processo, a janela preta, impedir o computador de
     dormir, a classe da janela, o registro) nunca foram explicados a ele.
   - E o texto para ele diz "como você escolheu" (`relatorios/passo0-2026-11-19/lista-de-excecoes-para-o-samuel.md:20`).
   - Destino: vira pergunta. Os 44 vão para a pergunta dos lugares fora do plano, ou a gerente pergunta direto se a
     escolha de 19/11 vale para o teste de velocidade inteiro. Até ele responder, o texto não diz "como você escolheu"
     sobre eles.
5. **R5, baixo: o seguir do apelido acusa linhas que não conversam com o Windows** (`regras_dos_agentes/porteiro.py:414`).
   - Uma função que devolve o resultado de uma chamada da biblioteca vira "devolve a biblioteca", e quem a chama passa
     a contar. O mesmo vale para o segundo nome de uma tupla e para um método de mesmo nome em outra classe.
   - Na lista: `atualizacao.py:748` e `teste_velocidade.py:2317`.
   - Provado num exemplo, com 4 linhas falsas.
   - Destino: consertar. Uma função só "devolve a biblioteca" quando o `return` traz o apelido em si, não uma chamada
     feita por ele. A tupla vira apelido só na posição certa. Depois, recontar a lista.
6. **R6, baixo: "abrir sem janela preta" (`CREATE_NO_WINDOW`) conta como conversa com o Windows**
   (`regras_dos_agentes/porteiro.py:251`).
   - São 5 dos 18 lugares da pergunta nova: o Tesseract, o Kraken, as páginas em outro processo e a tela de
     carregamento (`core/ocr_tesseract.py`, `core/paginas_em_outro_processo.py:112`).
   - Essa bandeira só esconde a janela de um programa aberto. Não muda o Windows, e o plano não a chama de erro.
   - Destino: pergunta à gerente sobre o alcance. Sugestão: só o número do `DETACHED_PROCESS` e as bandeiras que soltam
     o processo contam, não a que esconde a janela.
7. **R7, baixo: texto do ONDE-PAREI que não bate com o código**
   (`relatorios/passo0-2026-11-19/ONDE-PAREI.md:93`). Os itens 2 e 12 da primeira volta descrevem o comportamento
   antigo. Destino: consertar o texto.

## Para a gerente: o que ficou fora do projeto

Na cópia temporária (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\848d7b72-406b-4bfe-aabf-f5b3005d7b22\scratchpad\quebrar\copia`)
ficaram mais estes ramos de prova: `prova3-sim`, `prova3-uso`, `prova3-core`, e `prova3-k10`. Ficou
também o pacote `pac3.md`. Nada foi apagado.
