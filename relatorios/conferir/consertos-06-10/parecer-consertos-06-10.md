# Parecer do verificador: consertos de 06/10/2026 (histórico, girar, pasta dos testes)

**PRONTO PARA JUNTAR, com ressalvas.** Os três commits fazem o que prometem. Pilotei a janela real. Depois de fechar e reabrir, o Ctrl+Z desfaz a ação certa, e o "refazer" não traz mais de volta a ação que a pessoa tinha desfeito. "Só as pares" numa folha ímpar agora avisa e não gira nada. Os scripts de teste não tocam mais na pasta de dados de verdade.

Há **duas coisas para o Samuel saber** antes de juntar:

- três livros dele vão abrir com o Ctrl+Z encurtado (o livro em si não perde nada);
- num livro dividido, o aviso de girar fala em "folha ímpar" enquanto a tela mostra a página 2.

A **suspeita do implementador se confirmou só em parte.** O "começar de novo" do cartão limpa o histórico direito. Mas quando o programa recomeça a conferência sozinho (a pessoa mudou "Dividir folhas ao meio"), o histórico da conferência anterior volta, e o Ctrl+Z mexe no livro novo. Isso já acontece no `fase-1`; não foi este ramo que trouxe.

**Não é "aprovado":** só o Samuel marca.

> **Defeito conhecido (decisão do Samuel, 28/09):** moldura dourada e iluminura continuam sendo defeito conhecido da Fase 1. Estes commits não mexem na imagem das páginas.

**O que foi conferido:**

- o ramo `consertos-06-10`, na cópia `.claude\worktrees\consertos`;
- os commits `3427299` (histórico), `27a0498` (girar) e `9b4d87d` (pasta dos testes), sobre o `fase-1` em `782d5ef`.

**Como foi conferido:**

- a janela real foi aberta fora da tela, em 1600×821 px;
- ela foi pilotada só com mouse e teclado nativos (mensagens do Windows mandadas para a janela de teste);
- cada rodada teve uma pasta de dados própria, com cópias de livros: o Boécio do acervo, e um PDF de 6 folhas duplas feito a partir dele;
- para criar o "livro antigo com o arquivo errado", usei o código do `fase-1` (`782d5ef`), extraído numa cópia `git archive`.

## Veredito por item

| Item | Como | Resultado |
|---|---|---|
| 1. Histórico depois de reabrir | janela real + máquina | **Bom.** Fiz 6 sequências diferentes, cada uma fechando e reabrindo o programa. Em todas, o Ctrl+Z desfez na ordem certa, e o refazer nunca trouxe uma ação descartada |
| 1b. Livro antigo com o arquivo errado | janela real + máquina | **Bom, com ressalva.** Só a última ação volta. As cópias ficaram idênticas byte a byte, e o `projeto.json` não mudou. Um caso raro não é percebido (ressalva R2) |
| 2. Girar "só as pares" numa folha ímpar | janela real + olho | **Bom.** O aviso aparece pelo botão, pelo menu e pelas teclas. Nada girou e nada entrou no histórico. "Todas", "daqui em diante", "só esta" e "só as pares" numa folha par continuam girando |
| 3. Pasta de dados dos scripts | máquina | **Bom.** Rodei quatro scripts e a bateria inteira. O `erros.log` real continua com 440660 bytes, das 16:18. A lista de livros do Samuel não ganhou nada |
| 4. Testes de máquina | máquina | **Bom.** 98 arquivos de teste, um por vez: 1757 passaram, 59 pularam e 0 falharam. O `teste_botoes.py` fez 159 ações, com 0 falhas |
| 5. Suspeita do "começar de novo" | janela real | **Confirmada em parte**, e já existia no `fase-1`. Ver a seção 5 |

## 1. Histórico depois de reabrir (`3427299`)

Cada sequência foi feita na janela real e terminou fechando o programa (mensagem de fechar do Windows) e abrindo outra vez pelo "continuar" do cartão. As ações foram:

- girar ¼ à direita (botão em cima da página);
- trocar o filtro da página 1 (teclas 2, 3 e 4, na aba Filtro).

Depois de cada passo, conferi três coisas: o que o programa tinha na memória, o `acoes.jsonl` e o `posicao.json`.

| Sequência | Depois de reabrir, o Ctrl+Z desfez | O refazer trouxe |
|---|---|---|
| A, B, desfazer B, C | C, depois A, depois nada | A, depois C; **B nunca** |
| A, B, C, D, desfazer D e C, E | E, B, A | só o que foi desfeito agora; D e C nunca |
| A, B, desfazer B e A (até o começo), C | C, depois nada | C; A e B nunca |
| A, B, desfazer B, fechar sem fazer nada | A (B ficou no refazer, como deve) | B. Depois, uma ação nova descartou B também no arquivo |
| A, B, desfazer B, C, desfazer C, D, E, desfazer E | D, A | A, D e E (E tinha sido desfeito antes de fechar, e ficou no refazer, como deve); B e C nunca |
| A, B, C, voltar até A **pelo painel Histórico**, D | D, A | D; B e C nunca |

Em todas as sequências:

- o arquivo ficou só com o histórico que vale, sem as ações descartadas;
- o livro reaberto ficou igual ao de antes de fechar (giro e filtro das folhas e páginas mexidas).

Não sobrou arquivo `.novo` na pasta do projeto que conferi.

![Livro reaberto depois de A, B, desfazer B, C: a página 1 em Melhorar e a folha girada](imagens/i0-reaberto.jpg)

### 1b. Livro antigo com o arquivo errado

Criei o defeito com o código do `fase-1`: A, B, desfazer B, C. O arquivo ficou com A, B e C, e o `posicao.json` dizia "2 de 2". Depois abri esse mesmo livro no ramo:

- **Última coisa feita era uma ação (A, B, desfazer B, C).** Voltou só C. O Ctrl+Z desfez C, e depois não havia mais nada. O refazer trouxe C de volta e nunca trouxe B. A folha continuou girada (A não sumiu do livro).
- **Última coisa feita era um desfazer (A, B, desfazer B, C, desfazer C).** O histórico abriu vazio. O Ctrl+Z não fez nada, e o livro ficou como estava (folha girada, página em Original).
- **As cópias de segurança** (`acoes.antigo-historico-2026-10-06-2025.jsonl` e `posicao.antigo-historico-2026-10-06-2025.json`, e as de 20:29 no segundo caso) ficaram **idênticas, byte a byte**, aos arquivos de antes.
- **O `projeto.json`** ficou idêntico byte a byte ao de antes, logo ao abrir. Ficou idêntico também no fim, depois de Ctrl+Z e refazer.

Também copiei o `acoes.jsonl` e o `posicao.json` dos 8 livros reais do Samuel para uma pasta de teste. Abri as cópias com o código do ramo. A pasta real não foi tocada:

| Livro (cópia) | Linhas no arquivo | Histórico que vale | Abre com |
|---|---|---|---|
| Sobre a Consolacao da Filosofia (sem acento) | 291 | 289 | só a última ação ("Corte de borda da página 4") |
| Sobre a Consolação da Filosofia (com acento) | 17 | 11 | só a última ação ("Linha de corte da folha 9") |
| gradus-primus | 230 | 212 | só a última ação ("Apagar a página 3") |
| Palatino (2), Rhetorica, Siebmacher | igual | igual | sem mudança |

Nos três livros com o arquivo errado, as cópias de segurança saíram idênticas aos originais.

## 2. Girar "só as pares" numa folha ímpar (`27a0498`)

Escolhi "só as pares" na caixinha "aplicar em", com a folha 1 na tela. Tentei girar por todos os caminhos:

- os botões "¼ à direita", "¼ à esquerda" e "meia volta", em cima da página;
- o botão "girar", da aba Onde cortar;
- o menu Página, nos três giros;
- as teclas Ctrl+Direita e Ctrl+Esquerda.

Em todos apareceu a caixa "Um momento" com a frase pedida. Nenhuma folha girou, e o histórico não ganhou nada, nem na memória nem no arquivo. O menu "Aplicar o giro em" acompanhou a caixinha.

![O aviso de "só as pares" numa folha ímpar](imagens/i1-aviso-pares-na-impar.jpg)

Com "só as ímpares" na folha 2, aconteceu o mesmo, com a frase das ímpares. Testei pelo botão, pela meia volta, pelo menu e pela tecla.

![O aviso de "só as ímpares" numa folha par](imagens/i2-aviso-impares-na-par.jpg)

**Os outros casos continuam como antes**, conferidos folha por folha (giro das folhas 1 a 8):

- "só as pares" na folha 2: as 25 pares giraram, e as ímpares não. Testei pelo botão, pelo menu e pela tecla;
- "só as ímpares" na folha 3: as ímpares ficaram em meia volta;
- "todas", na folha 3: as 50 folhas ficaram como a folha 3;
- "daqui em diante", na folha 3: as folhas 3 a 50 mudaram, e as folhas 1 e 2 não;
- "só esta": só a folha 3 girou;
- o Ctrl+Z voltou cada giro.

**A tecla R não gira**, nem com "só esta". Não é defeito deste ramo: desde o item 2.3 a R é só do Retângulo, e o código diz isso.

## 3. Pasta de dados dos scripts (`9b4d87d`)

Antes de começar, fotografei a pasta de dados real (`%LOCALAPPDATA%\EditorImpressao`):

- o `erros.log` com 440660 bytes, das 16:18:46 de 06/10;
- o `historico.json`, o `configuracoes.json` e os 29 arquivos dos 8 projetos, com tamanho e hora.

Conferi de novo depois de cada script e no fim de tudo. **Nada mudou**: o mesmo tamanho, a mesma hora e a mesma impressão digital (`a107330b…`) do `erros.log`, e a lista de livros igual.

| Script | Resultado do script | Pasta real |
|---|---|---|
| `teste_velocidade.py --rapido` | terminou em 44 s; relatório gravado | intocada |
| `teste_pipeline.py` | OK | intocada |
| `teste_medidor.py` (sem tela) | 0 problemas | intocada |
| `teste_criterios.py` | 9 critérios passaram, 0 falharam | intocada |
| `teste_interface.py` (sem tela) | **quebra no meio** (ver ressalva R5) | intocada |
| bateria do pytest, os 98 arquivos | 0 falhas | intocada |

## 4. Testes de máquina

- **Bateria:** os 98 arquivos de `tests\`, rodados um por vez: **1757 passaram, 59 pularam, 0 falharam**. Os testes novos passaram todos:
  - `test_historico_depois_de_reabrir`: 11;
  - `test_girar`: 53;
  - `test_girar_na_tela`: 22;
  - `test_pasta_de_dados_dos_scripts`: 14;
  - `test_teste_velocidade`: 147.
- **`teste_botoes.py`:** rodou numa cópia `git archive` do ramo (`9b4d87d`), com a própria `saida_teste`: **159 ações, 0 falhas**.
- **Velocidade:** só rodei o `--rapido`, e os números dele não valem como medição. Estes commits não mexem no processamento das páginas, só no histórico, no aviso de girar e nos scripts. Por isso não fiz a medição completa (ver ressalva R6).

## 5. A suspeita: o histórico da conferência anterior volta no Ctrl+Z

**O "começar de novo" do cartão está certo.** Testei em dois jeitos:

- com o livro aberto antes na mesma sessão (voltar à tela inicial, botão direito no cartão, "começar de novo");
- logo depois de abrir o programa.

Nos dois, o `acoes.jsonl` e o `posicao.json` foram apagados, e o Ctrl+Z e o refazer não fizeram nada no livro limpo.

**O defeito existe em outro caminho: o recomeço automático.** Quando o trabalho salvo não combina com o livro, o programa recomeça a conferência sozinho e avisa "Comecei a conferência deste livro de novo". Isso acontece, por exemplo, quando a pessoa muda "Dividir folhas ao meio".

Nesse caso, ele guarda a cópia do trabalho, mas **não esvazia o histórico**. A conferência nova abre com as 3 ações da anterior no Ctrl+Z. Testei assim, num PDF de 6 folhas duplas (12 páginas):

1. Girei a folha 1 e mudei o filtro da página 1 para Preto e branco, e depois para Melhorar.
2. Voltei às opções, desmarquei "Dividir folhas ao meio" e cliquei em Conferir.
3. Apareceu o aviso de recomeço, e o livro ficou com 6 páginas, todas em Original.
4. **O primeiro Ctrl+Z pôs a página 1 em Preto e branco.** A "página 1" de antes era só a metade da esquerda da folha 1. A de agora é a folha inteira. Ou seja, o Ctrl+Z mexe na página errada de um livro que a pessoa acabou de recomeçar.

![O aviso de recomeço](imagens/i4-recomeco-aviso.jpg)

![Logo depois do recomeço: página 1 em Original](imagens/i5-recomeco-pagina-1-original.jpg)

![Depois de um Ctrl+Z: a página 1 virou Preto e branco, uma ação da conferência anterior](imagens/i6-recomeco-um-ctrl-z.jpg)

**No `fase-1` (`782d5ef`) acontece igual.** Repeti a mesma sequência, e o primeiro Ctrl+Z também pôs a página 1 em Preto e branco. Este ramo não mexe nesse caminho (`ui/janela_principal.py`, `_analise_pronta`, que chama `self.acoes.carregar()` mesmo quando o trabalho salvo não combina). Só relato; não consertei. É candidato à Lista de bugs.

## Ressalvas

- **R1. Três livros do Samuel vão abrir com o Ctrl+Z curto.** São os dois "Consolação da Filosofia" e o gradus-primus. Na próxima vez que abrirem, o Ctrl+Z só alcança a última ação. Antes, alcançava 289, 11 e 212 ações, só que na ordem errada. O livro em si não perde nada, e o histórico de antes fica guardado ao lado. Vale avisar o Samuel, para ele não estranhar.
- **R2. Um caso de livro antigo não é percebido.** É o livro com o arquivo errado que já foi reaberto no programa antigo e recebeu um desfazer (ou um refazer) lá. O "total" do `posicao.json` passa a bater com o tamanho do arquivo, e o conserto acha que está tudo certo.
  - Testei: no ramo, o refazer desse livro trouxe de volta "Filtro da página 1: Original para Preto e branco", uma ação que a pessoa tinha desfeito.
  - Pelo arquivo não dá para saber se um livro está assim. Nos livros do Samuel, nenhum mostra esse sinal. Mas um livro que, depois disso, teve tudo refeito também ficaria com cara de certo.
  - É um resto do defeito antigo, não um defeito novo. Não impede juntar.
- **R3. Livro dividido: o aviso fala de "folha ímpar" com a página 2 na tela.** Num livro dividido, a tira de baixo e a página mostram "2", mas a folha é a 1. "Só as pares" ali avisa "Você está numa folha ímpar". A frase está certa, porque a barra é "Girar a folha", mas pode confundir o Kaique, que vê "2". **Pergunta para o Samuel:** a frase deve dizer o número da folha, por exemplo "a página 2 é da folha 1, que é ímpar"?

  ![Livro dividido, página 2 na tela, "só as pares": o aviso diz folha ímpar](imagens/i3-livro-dividido-pagina-2.jpg)

- **R4. Teclas.** As teclas de girar (Ctrl+Seta) só funcionaram depois de eu mandar o foco para a janela de teste. Ao fechar a caixa "Um momento", a janela fora da tela perde o foco. Isso é do jeito de pilotar, não do programa. Com foco, as teclas avisaram como deviam.
- **R5. `teste_interface.py` quebra no meio**, com o erro "TelaConferir não tem `destino`". O script está desatualizado, e a mesma linha está no `fase-1`; não foi este ramo. Mesmo quebrando, ele não gravou nada na pasta real. A pasta dele em `saida_teste\dados_dos_scripts` foi apagada no fim, porque não havia `erros.log`.
- **R6. Velocidade completa não medida.** Só rodei o `--rapido`. Estes commits não tocam no processamento das páginas. O histórico só regrava o `acoes.jsonl` inteiro numa ação feita logo depois de um desfazer: é um arquivo de centenas de bytes.
- **R7. Uma janela pequena de queda de energia** (antiga, não deste ramo). O `acoes.jsonl` e o `posicao.json` são gravados um depois do outro. Uma queda exatamente entre os dois pode deixar o refazer com uma ação a mais ou a menos. Isso já era assim antes.
- **R8. Do meu piloto, não do programa.** Numa rodada, o meu lançador tentou mover para fora da tela um botão que o Qt já tinha apagado, e apareceu uma caixa "Aconteceu um problema inesperado". O erro estava no meu script (corrigido). A rodada foi refeita do zero e não entrou nos resultados.

## Onde estão as coisas

- Este parecer: `relatorios\conferir\consertos-06-10\parecer-consertos-06-10.html` (e `.md`, `.pdf`).
- As imagens ficam em `relatorios\conferir\consertos-06-10\imagens\`.
- Os registros de cada rodada (passo a passo, memória e disco) ficaram na pasta temporária do verificador. Não entram no git.
