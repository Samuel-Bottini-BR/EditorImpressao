# Opinião do verificador: trabalho salvo, 3ª rodada, e a pergunta do fundo (29-30/09/2026)

Commits conferidos: `8cbbfdf`, `86725ee`, `6996ae9`, `4bca0fa`. Testei na cópia limpa do commit `179afce` (`.claude\worktrees\verificador`), não na pasta principal, que tem mudanças do processamento pela metade.

> **Aviso (decisão do Samuel, 28/09): moldura dourada e iluminura são defeito conhecido** até a Fase 1 ficar pronta (itens 1.2, 1.4 e 1.5). Esta conferência não é de imagem; o aviso vale para a fase.

## Veredito

**NÃO ESTÁ PRONTO**, por causa da pergunta do fundo. O conserto grave está bom: **o "cancelar" em "Olhando o livro..." não faz mais o programa parar de gravar.** Cancelei uma vez, duas vezes, cancelei e troquei de livro, cancelei e fechei: tudo o que fiz depois ficou gravado. O "continuar" de cada cartão abre o projeto certo. E os testes automáticos não mexem mais na pasta de dados de verdade.

**A pergunta do fundo tem dois defeitos:**

1. **Pelo "continuar", a resposta dada depois do fim da análise é jogada fora sem aviso.** O "Sim" não muda nada, nada fica anotado, e a pergunta volta toda vez que o livro é aberto. Num livro pequeno a análise acaba em cerca de 1 segundo, antes de dar tempo de ler a pergunta. Por isso, nesses livros, pelo "continuar", o "Sim" nunca funciona.
2. **"Sim" e fechar o programa antes de "Conferir": o "Sim" se perde.** A pergunta não volta mais, e as páginas continuam como estavam.

Além disso, o "Sim" troca **todas** as páginas para "Tirar o fundo". O Samuel já corrigiu isso em 29/09: o "Sim" deve trocar **só as que estão em Original**. Então essa parte do `4bca0fa` ainda precisa mudar.

Quem decide é o Samuel. Isto não é aprovação.

## Ainda existe caminho de perda de trabalho sem cópia? O Samuel já pode usar o "cancelar"?

**Não achei nenhum caminho em que trabalho se perca sem cópia, e o Samuel já pode usar o "cancelar"**, com um cuidado:

- **Se ele mudou uma opção na tela "O que fazer" (principalmente "Dividir folhas ao meio"), clicou "Conferir" e depois "cancelar", ele deve pôr a opção de volta como estava antes de continuar.** Se não puser, a conferência volta com as páginas de antes, mas o projeto guarda a opção nova. Na próxima vez que o livro abrir, a conferência **recomeça do zero**, e o trabalho daquele dia fica só na cópia `projeto.antigo-*.json`. O programa avisa e guarda a cópia, mas não tem botão para trazer o trabalho de volta (prints s34 a s36). Não se perde de vez, mas para quem usa é como perder.
- Raro: clicar "Conferir" **no mesmo instante** do "cancelar" (menos de um décimo de segundo) faz o programa **sumir da tela**. Esse defeito é antigo: acontece também no código de antes destes consertos. Com o mouse, na prática, não dá tempo de clicar tão rápido. No teste nada se perdeu, porque tudo já estava gravado.

## O que foi feito (máquina ou olho)

| O quê | Tipo | Resultado |
|---|---|---|
| `pytest tests -q` inteiro, na cópia limpa, **sem** trocar a pasta de dados à mão (para provar o `conftest.py`) | máquina | **1060 passaram, 86 pulados, nenhum falhou.** Os 86 pulados dependem de arquivos que não existem na cópia limpa: `gabarito/`, os resultados dos OCRs em `saida_teste/ocr-*` e o motor do Kraken. Na cópia há 1146 testes; na pasta principal há 1181. A diferença de 35 é o arquivo de testes da outra frente, que ainda não tem commit (`tests/test_gravura_no_processamento.py`). Por isso a conta da entrega foi 1180 |
| Pasta de dados real: lista de todos os arquivos, com tamanho e data, antes e depois do `pytest` | máquina | **Igual.** O `conftest.py` funciona |
| As 4 reproduções da rodada 2 (cancelar/dois projetos, mesmo nome, fechar no "O que fazer", "Dividir" desmarcado), na cópia, com pasta de dados própria | máquina | **As 4 dão certo.** Depois do "cancelar", o trabalho é gravado. O "continuar" do cartão antigo abre o antigo |
| Sonda nova, sem janela (`sonda3_cancelar_e_fundo.py`, 39 conferências) | máquina | 34 certas. As 5 que falharam estão explicadas abaixo (1 teórica, 4 da pergunta do fundo) |
| Sondas dirigidas (`sonda3_f5b.py`, `sonda3_opcao_e_cancelar.py`, `sonda3_thread.py`, `sonda3_demora.py`) | máquina | Confirmam os defeitos listados |
| Janela real: 70 prints de trabalho e 36 no relatório, **todos olhados** | olho | Tabela abaixo |
| Comparação byte a byte do `projeto.json` com cópias de referência, a cada passo | máquina | Tabela abaixo |
| Velocidade | — | **Não rodei** (ordem da gerente) |

**Como pilotei a janela:** abri instâncias novas da **cópia limpa**, com `LOCALAPPDATA` apontando para `saida_teste\verificador_trabalho_salvo_3\dados`. Cliques e teclas foram por mensagem nativa, sem tocar no mouse nem no teclado do Samuel. Os prints foram feitos com `PrintWindow` e o fechamento com `WM_CLOSE`. **Nada apareceu na tela do Samuel.** Um lançador meu (`lancador.py`, que não muda o código do programa) coloca cada janela do programa fora da tela **antes** de ela ser desenhada, e sem tirar o foco do Samuel. Isso vale para a janela principal, as perguntas, os avisos e os menus. Um vigia olhava a cada 30 ms, só como segurança, e **não precisou mover nenhuma janela** (`vigia.log`). A caixa "Abrir" do Windows **foi simulada**: o lançador devolve o caminho com `/`, igual à caixa de verdade, que já tinha sido pilotada na rodada 2. Os livros de teste são **cópias** montadas com páginas do acervo; o acervo só foi lido.

## A janela, passo a passo

| Passo | Resultado | Print |
|---|---|---|
| Livro novo com camadas ("Modelo Siebmacher", 13 páginas), aberto como o Windows abre (caminho com `\`) | A pergunta aparece uma vez. Respondi "Não" | s01 |
| Trabalho montado: linha de corte arrastada, "está certo", páginas 1 e 2 em Mágico pro, 3 em Preto e branco, 5 em Melhorar | Gravado. Guardei uma cópia de referência | s02 |
| **O bug q21-q23:** "Voltar para as opções" → "Conferir" → "cancelar" em "Olhando o livro..." | Volta para a conferência com o trabalho | s03, s04 |
| ...mudei as páginas 12 e 11 | **Consertado:** o `projeto.json` mudou no disco na hora | s05 |
| **Cancelar duas vezes seguidas** e mudar a página 10 | Gravado | — |
| **Cancelar, mudar a página 9 e fechar em seguida** | Gravado ao fechar. Reaberto pelo "continuar", sem pergunta, com o trabalho inteiro | s06, s07 |
| **Cancelar e trocar de livro** (Arquivo → Abrir: outro PDF com o mesmo nome) | Livro 1 igual. O outro vira projeto novo (com a pergunta, por ser livro novo) | — |
| **Trocar de livro no meio da análise** (abrir o livro 1 enquanto o outro era analisado) | O resultado atrasado do outro livro foi ignorado. A tela ficou em "O que fazer" do livro 1, e o "Conferir" trouxe o trabalho dele. O outro continua com 0 páginas | s08, s09 |
| **Fechar durante a análise** (vindo da conferência) | O `projeto.json` ficou **igual byte a byte** | — |
| **Dois projetos do mesmo PDF** (copiei a pasta e pus tudo em Preto e branco, com data mais velha) | **Consertado:** o "continuar" de "Siebmacher antigo" abre o antigo (Preto e branco), e o do outro abre o outro (Mágico pro na página 9). Cada um só mexe na própria data | s10, s11, s12 |
| **Projeto antigo com camadas** (Modelo Palatino, trabalho montado, sem o campo novo, como um projeto gravado antes do `4bca0fa`), aberto pelo "Abrir" | A pergunta aparece na próxima abertura | s13 |
| ..."Sim" → "Conferir" | As 8 páginas vão para "Tirar o fundo" numa ação só do Histórico ("Tirar o fundo em 8 páginas"). Corte, conferidas e alertas ficaram iguais. **As páginas que eu tinha posto em Mágico pro, Preto e branco e Melhorar também foram trocadas** (o Samuel já pediu para mudar isso) | s14, s15 |
| ...Editar → Desfazer | Os filtros voltam. **O filtro do livro continua "Tirar o fundo"**, e a tela "O que fazer" continua dizendo "tirar o fundo de todas as páginas" | s16, s17 |
| ...reabrir | Não pergunta mais | s17 |
| Projeto antigo: **"Não"** | Só o campo "já perguntou" mudou no disco. Nada mais mudou, e não pergunta mais | s18 |
| **Projeto antigo pelo "continuar", respondendo depois do fim da análise** | **Defeito:** a análise de 8 folhas acaba em cerca de 1 s, atrás da pergunta. O "Sim" não mudou nada, o disco ficou com "ainda não perguntou", e a pergunta voltou na abertura seguinte | s19, s20, s21 |
| ...respondendo "Sim" em 0,8 s (antes do fim da análise) | Funciona: as 8 páginas em "Tirar o fundo" | s22 |
| **"Sim" e fechar antes de "Conferir"** | **Defeito:** ao reabrir, não pergunta mais e os filtros estão como antes. O "Sim" se perdeu | s23 |
| Livro **sem camadas** (Boécio, 6 folhas): aberto e depois pelo "continuar" | Nunca pergunta | s24 |
| **"Começar de novo"** (menu do cartão) | A pergunta volta. Obs.: os botões da confirmação estão em inglês ("Yes"/"No") | s25, s26 |
| **"Dividir" desmarcado** (recomeço de verdade) | Aviso com o motivo certo e a cópia. A cópia é **igual byte a byte** ao trabalho de antes | s27, s28 |
| ...reaberto pelo "Abrir" (caminho com `/`) | "Dividir" continua desmarcado. O "Conferir" dá 7 páginas, **sem recomeçar e sem aviso** | s29, s30 |
| **Livro movido** de pasta | O cartão diz "o PDF saiu do lugar". Aberto no lugar novo, o trabalho volta (só o caminho mudou) | s31, s32 |
| **Opção mudada + cancelar** (projeto com 13 páginas: desmarquei "Dividir", "Conferir", "cancelar", trabalhei e fechei) | Gravou 13 páginas com "Dividir" desmarcado. Na abertura seguinte, o "Conferir" **recomeçou a conferência** (7 páginas), com cópia e aviso | s34, s35, s36 |
| "cancelar" e "Conferir" com 20 ms de diferença (livro novo de 40 folhas) | Na 2ª tentativa **o programa sumiu**, sem mensagem e sem nada no `erros.log` | s33 |

## Os defeitos, em detalhe

**1. Pergunta do fundo pelo "continuar": a resposta atrasada é ignorada (nasceu no `4bca0fa`).** No "continuar", a pergunta abre por cima da tela e a análise começa ao mesmo tempo. Quando a análise acaba, o projeto da tela vira outro objeto (o salvo). Aí o `_resposta_do_aviso_do_fundo` compara `projeto is not self.projeto` e sai **antes de anotar qualquer coisa**. O "Sim" não faz nada, o "Não" não fica anotado, e a pergunta volta toda vez. Pela sonda sem janela, com "Sim" e com "Não": nada muda, o disco fica com `perguntou_fundo: false` e reabrir pergunta de novo. Nos livros grandes do Samuel (134 a 446 folhas) a análise demora mais e a resposta costuma chegar antes. Nos pequenos, quase nunca. Onde: `ui/janela_principal.py`, `_perguntar_se_tira_o_fundo`/`_resposta_do_aviso_do_fundo`.

**2. "Sim" antes de "Conferir", e depois fechar (ou voltar, ou cancelar): o "Sim" se perde.** A resposta é anotada como "já perguntou" na hora, mas a troca das páginas espera o fim da análise (`_fundo_pendente`, que só existe na memória). Se o programa fechar antes, o filtro do livro também não é gravado (a trava do `4c01fa6` não grava por cima de trabalho salvo). A pergunta não volta, e as páginas ficam como estavam. Sem janela (F4, F4b) e na janela (s23).

**3. Opção mudada + "cancelar" → a conferência recomeça no dia seguinte (a perda é com cópia; o defeito é antigo).** A tela "O que fazer" muda as opções direto no projeto aberto. O "cancelar" devolve a conferência com as páginas de antes, mas as opções novas ficam. Daí em diante tudo é gravado assim (13 páginas com "Dividir" desmarcado). Na abertura seguinte, a opção salva manda recomeçar. O programa guarda a cópia e avisa, mas não tem como trazer o trabalho de volta pela tela. Na rodada 2 isto estava escondido pelo defeito que não gravava. Antes do `4c01fa6` já acontecia. Sugestão para o implementador pesar: o "cancelar" da análise devolver as opções de antes da análise (ou voltar para "O que fazer", e não para a conferência, quando uma opção mudou). Sonda: `sonda3_opcao_e_cancelar.py`.

**4. Programa some ao "Conferir" logo depois do "cancelar" (antigo).** A análise cancelada ainda roda por cerca de 0,1 s. Se nesse intervalo começar outra análise, a de antes perde a última referência, e o Qt derruba o processo quando ela termina (`QThread` destruída rodando). Reproduzido sem janela no código novo e também no código de antes (`0c6031e`), e na janela real. Na prática precisa de dois cliques em menos de 0,1 s em botões de lugares diferentes. Onde: `ui/janela_principal.py`, `analisar` (a `TarefaAnalise` antiga não fica guardada até acabar).

**5. Pequenos:**
- Todo livro novo com camadas ganha um `projeto.antigo-*.json` de 0 páginas, que não serve para nada (nasceu no `4bca0fa`). A resposta à pergunta grava um `projeto.json` só com as opções, e o fim da análise o trata como "trabalho que não combina" e guarda uma cópia. Não aparece mensagem.
- Depois de desfazer o "Sim", o filtro do livro continua "Tirar o fundo" (s17).
- `abrir_livro` não grava antes de trocar de livro: uma mudança feita há menos de 0,6 s se perde (sonda C2). Pela tela não dá para chegar nisso: a caixa "Abrir" dá tempo de o relógio de 0,6 s gravar. Anoto como teórico.
- A confirmação de "Começar de novo?" tem os botões em inglês ("Yes"/"No") (s25). É antigo.
- O resumo do outro livro ficou com a "página atual" da conferência do livro de antes (8). É cosmético.

## Minha opinião sobre as duas decisões do implementador na pergunta do fundo

- **"Sim" troca todas as páginas: discordo, e o Samuel já corrigiu (29/09, `f94f69b`): só as páginas em "Original".** Trocar tudo apaga as escolhas feitas página por página (na janela, a página em Mágico pro, a de Preto e branco e a de Melhorar foram para "Tirar o fundo"). Dá para desfazer numa ação só, mas quem não olhar o Histórico não percebe. Junto com a correção, sugiro que o desfazer devolva também o filtro do livro.
- **A pergunta volta depois de "começar de novo": concordo (o Samuel também).** O "começar de novo" apaga tudo e deixa o livro como novo. Perguntar de novo é coerente, e ele confirma antes de apagar.

## Ressalvas

1. **Velocidade não medida** (ordem da gerente).
2. **A caixa "Abrir" foi simulada** (devolve o caminho com `/`, como a de verdade). **Arrastar o PDF** e a **roda do mouse** não foram testados.
3. **A pasta de dados real do Samuel mudou durante esta tarefa, mas não por mim.** Antes e depois do `pytest` estava igual (conferido às 23h3x). Na conferência final, feita às 00h16 de 30/09 (o registro de "antes" é das 23h2x de 29/09):
   - às 23h40 **sumiram** as pastas `projetos\camadas`, `projetos\comum` e `projetos\teste de aplicativo`;
   - às 23h44 **ganharam `resumo.json`** as pastas `pdfcoffee.com_gradus-primus...`, `Schön Neues Modell Buch - Johann Siebmacher` e `Sobre a Consolação da Filosofia - Severino Boécio` (a com acento).

   Todos os meus processos (pytest, sondas, janela) usaram outra pasta de dados, e nenhum código desta cópia cria `resumo.json` para projeto antigo. **Se não foi a gerente nem o Samuel, precisa ser investigado**, porque apagar `teste de aplicativo` é apagar um projeto antigo. As listas estão em `saida_teste\verificador_trabalho_salvo_3\pasta_real_antes.txt` e `pasta_real_depois.txt`.
4. Os 86 testes pulados dependem de dados que não estão na cópia limpa. Não rodei esses testes com o código da pasta principal, porque ela tem mudanças do processamento pela metade.
5. Nos prints, as bolinhas dos filtros da tela "O que fazer" continuam aparecendo vazias (ressalva da rodada 2). Depois do recomeço, o Histórico ainda lista as ações antigas (já relatado).
6. A tela "O que fazer" do Palatino diz "Vou dividir as 8 folhas em 16 páginas" antes da análise, e ela depois não divide. É a estimativa de antes da análise, não é deste item.
7. O "Ver de perto" abriu sozinho num clique num cartão de filtro (já relatado). Desta vez abriu fora da tela, e eu o fechei.
8. Material de teste criado por mim, que pode ser apagado: `saida_teste\verificador_trabalho_salvo_3\` (livros copiados, pasta de dados de teste, cópia do código de `0c6031e` para a comparação, scripts). **Não apaguei a cópia `.claude\worktrees\verificador` nem a junção `modelos`.**

## Bugs para a Lista de bugs (30/09/2026)

| Data | Bug | Onde | Print |
|---|---|---|---|
| 30/09 | **Pergunta do fundo pelo "continuar": resposta dada depois do fim da análise é ignorada** ("Sim" não troca nada, nada é anotado, pergunta volta sempre). Em livro pequeno é o caso comum | `ui/janela_principal.py` (`_resposta_do_aviso_do_fundo`: `projeto is not self.projeto`) | s19, s20, s21; `sonda3_f5b.py` |
| 30/09 | "Sim" da pergunta e fechar (ou voltar, ou cancelar) antes de "Conferir": o "Sim" se perde e a pergunta não volta | `ui/janela_principal.py` (`_fundo_pendente` só na memória) | s23 |
| 30/09 | "Sim" troca todas as páginas; o Samuel pediu só as de "Original". O desfazer não devolve o filtro do livro | `ui/janela_principal.py` (`_tirar_o_fundo_do_livro_inteiro`) | s15, s16, s17 |
| 30/09 | Opção mudada em "O que fazer" + "cancelar": a conferência antiga volta, mas a opção nova é gravada; na abertura seguinte a conferência recomeça (com cópia) | `ui/janela_principal.py` (`cancelar`) / `ui/tela_opcoes.py` (`_mudou` mexe no projeto aberto) | s34, s35, s36; `sonda3_opcao_e_cancelar.py` |
| 30/09 | (antigo) "Conferir" em menos de 0,1 s depois do "cancelar": o programa some sem mensagem | `ui/janela_principal.py` (`analisar` troca `self.tarefa` com a antiga ainda rodando) | s33; `sonda3_thread.py` |
| 30/09 | Livro novo com camadas ganha um `projeto.antigo-*.json` vazio | `_resposta_do_aviso_do_fundo` + `_analise_pronta` | — |
| 30/09 | "Começar de novo?" com botões em inglês | `ui/tela_inicio.py` (`pedir_para_recomecar`) | s25 |

## Arquivos

- Prints: `relatorios/conferir/fase1-2026-09-29-trabalho-salvo-3/verificador/s01...s36.jpg`
- Scripts (sondas, lançador, piloto, vigia): `relatorios/conferir/fase1-2026-09-29-trabalho-salvo-3/verificador/reproducoes/`
- Material de teste, pasta de dados de teste e todos os prints de trabalho: `saida_teste\verificador_trabalho_salvo_3\`

## Os prints

![s01 livro novo: a pergunta aparece uma vez](s01-livro-novo-pergunta-uma-vez.jpg)
![s02 trabalho montado](s02-trabalho-montado.jpg)
![s03 Olhando o livro](s03-olhando-o-livro.jpg)
![s04 cancelou: volta para a conferência](s04-cancelou-volta-a-conferencia.jpg)
![s05 trabalho depois do cancelar: gravado](s05-trabalho-depois-do-cancelar-gravado.jpg)
![s06 cancelou, mudou a página 9 e fechou](s06-cancelou-mudou-e-fechou.jpg)
![s07 reaberto: o trabalho todo volta](s07-reaberto-trabalho-todo-volta.jpg)
![s08 trocou de livro no meio da análise: resultado atrasado ignorado](s08-trocou-de-livro-no-meio-da-analise.jpg)
![s09 livro 1 de volta, intacto](s09-livro1-de-volta-intacto.jpg)
![s10 dois projetos do mesmo PDF](s10-dois-projetos-do-mesmo-pdf.jpg)
![s11 continuar do antigo abre o antigo (Preto e branco)](s11-continuar-do-antigo-abre-o-antigo.jpg)
![s12 continuar do recente abre o recente (Mágico pro)](s12-continuar-do-recente-abre-o-recente.jpg)
![s13 projeto antigo: pergunta na próxima abertura](s13-projeto-antigo-pergunta.jpg)
![s14 antigo, Sim: tela O que fazer](s14-antigo-sim-o-que-fazer.jpg)
![s15 antigo, Sim: todas em Tirar o fundo](s15-antigo-sim-todas-no-tirar-o-fundo.jpg)
![s16 desfazer volta os filtros](s16-desfazer-volta-os-filtros.jpg)
![s17 reaberto: não pergunta, mas o filtro do livro ficou Tirar o fundo](s17-reaberto-nao-pergunta-filtro-do-livro-ficou.jpg)
![s18 antigo, Não: nada mudou](s18-antigo-nao-nada-mudou.jpg)
![s19 continuar: a análise já acabou atrás da pergunta](s19-continuar-analise-acabou-atras-da-pergunta.jpg)
![s20 DEFEITO: Sim depois da análise, nada mudou](s20-BUG-sim-depois-da-analise-ignorado.jpg)
![s21 DEFEITO: a pergunta volta](s21-BUG-pergunta-de-novo.jpg)
![s22 Sim durante a análise funciona](s22-sim-durante-a-analise-funciona.jpg)
![s23 DEFEITO: Sim e fechar antes de Conferir, perdido](s23-BUG-sim-e-fechar-antes-de-conferir-perdido.jpg)
![s24 livro sem camadas nunca pergunta](s24-sem-camadas-nunca-pergunta.jpg)
![s25 Começar de novo: botões em inglês](s25-comecar-de-novo-botoes-em-ingles.jpg)
![s26 depois do começar de novo, a pergunta volta](s26-comecar-de-novo-pergunta-volta.jpg)
![s27 Dividir desmarcado](s27-dividir-desmarcado.jpg)
![s28 aviso do recomeço com a cópia](s28-aviso-do-recomeco.jpg)
![s29 Abrir: Dividir continua desmarcado](s29-abrir-dividir-continua-desmarcado.jpg)
![s30 Conferir sem recomeço](s30-conferir-sem-recomeco.jpg)
![s31 livro movido: cartão](s31-livro-movido-cartao.jpg)
![s32 livro movido: o trabalho volta](s32-livro-movido-trabalho-volta.jpg)
![s33 análise de 40 folhas, antes do programa sumir](s33-antes-do-programa-sumir.jpg)
![s34 DEFEITO: desmarcou Dividir](s34-BUG-desmarcou-dividir.jpg)
![s35 DEFEITO: cancelou e voltou a conferência antiga (13 páginas)](s35-BUG-cancelou-conferencia-antiga.jpg)
![s36 DEFEITO: na abertura seguinte, recomeçou sem ter pedido](s36-BUG-recomecou-no-dia-seguinte.jpg)
