# Opinião do verificador: consertos de "trabalho salvo", 2ª rodada (29/09/2026)

Commits conferidos: `7bb3905`, `4c01fa6`, `f0abd32`, `39200f3` (ramo `fase-1`).

> **Aviso (decisão do Samuel, 28/09): moldura dourada e iluminura são defeito conhecido** até a Fase 1 ficar pronta (itens 1.2, 1.4 e 1.5). Esta conferência não é de imagem; o aviso vale para a fase.

## Veredito

**NÃO ESTÁ PRONTO.** Os quatro consertos fazem o que prometem, na janela de verdade: os dois caminhos graves da rodada anterior (outro PDF com o mesmo nome; fechar antes do fim da análise) **não apagam mais nada**, o livro reaberto pelo "Abrir" ou pelo Windows volta com as opções salvas, e o "D:" não fica mais sozinho na mensagem. Tudo o que já tinha passado continua passando.

**Mas achei um caminho novo em que trabalho se perde sem cópia e sem aviso, e ele nasceu do próprio conserto `4c01fa6`:** com um livro já em conferência, a pessoa volta para "Marque o que você quer fazer", clica "Conferir" e depois **"cancelar"** na tela "Olhando o livro...". O programa volta para a conferência com o trabalho na tela, parece normal, mas **daí em diante nada mais é gravado**. Tudo o que for feito depois some quando o programa for fechado. O trabalho de antes fica inteiro; o que se perde é o trabalho novo.

Quem decide é o Samuel. Isto não é aprovação.

## Ainda existe caminho em que o Samuel perde trabalho sem cópia?

**Sim, um: depois de "cancelar" na tela "Olhando o livro..." de um livro que já tem trabalho, tudo o que ele fizer até fechar o programa se perde, sem aviso.** Enquanto isso não for consertado, os cuidados são:

1. **Não usar "cancelar" em "Olhando o livro..." num livro que já tem trabalho.** Se usar, clicar "Conferir" de novo e deixar a análise terminar antes de continuar (a análise completa volta a gravar normalmente). Fechar e abrir o programa também resolve.
2. Os cuidados da rodada anterior **não são mais necessários**: pode ter dois PDFs diferentes com o mesmo nome, e pode fechar o programa em qualquer momento depois de abrir um livro, que o trabalho salvo não é mais apagado.
3. Continuam valendo, mas **perguntam antes**: "começar de novo" apaga o trabalho sem guardar cópia; "Tirar da lista" apaga a pasta inteira, inclusive as cópias `projeto.antigo-*`.
4. Pequeno: o que se muda na tela "O que fazer" de um livro com trabalho se perde se o programa for fechado antes de clicar "Conferir" (é o preço do conserto `4c01fa6`, e está escrito na Tentativa 36).

## O que foi feito (máquina ou olho)

| O quê | Tipo | Resultado |
|---|---|---|
| `pytest tests -q` inteiro (com pasta de dados própria) | máquina | **1123 passaram, 1 pulado, nenhum falhou** (os dois instáveis conhecidos passaram) |
| As três reproduções da rodada anterior, em cópia, com pasta de dados própria | máquina | **as três agora dão certo** (abaixo) |
| Sonda nova sem janela: "cancelar" a análise e dois projetos do mesmo PDF | máquina | achou o caminho novo; ver "Bug novo" |
| Janela real, 26 prints no relatório (e outros de trabalho), **todos olhados** | olho | tabela abaixo |
| Comparação byte a byte do trabalho salvo (`projeto.json`, `acoes.jsonl`, `posicao.json`) contra uma cópia de referência, a cada passo | máquina | tabela abaixo |
| Pasta de dados real do Samuel: lista de todos os arquivos com data e tamanho antes e depois | máquina | **igual** (nada ganho, nada perdido) |
| Velocidade | — | **Não rodei** (ordem da gerente) |

**Como pilotei:** instância nova (`pythonw main.py`), `LOCALAPPDATA` trocado para `saida_teste\verificador_trabalho_salvo_2\dados`, janela fora da tela, cliques e teclas por mensagem nativa (sem tocar no mouse nem no teclado do Samuel), prints com `PrintWindow`, fechamento com `WM_CLOSE`. Um vigia movia para fora da tela toda janela nova do programa de teste. O "Abrir" foi feito pela caixa de verdade do Windows. Livros de teste: **cópias** montadas de páginas do acervo (o acervo só foi lido), iguais às da rodada anterior: "Modelo Siebmacher.pdf" (Siebmacher 7 a 12 + Palatino 9: 7 folhas, 13 páginas) e outro "Modelo Siebmacher.pdf" em outra pasta, **mesmo nome, mesmo número de páginas, conteúdo diferente** (Siebmacher 20 a 25 + Palatino 7). O PDF processado foi gravado em `saida_teste\...\saida_pdf`, não na pasta Documentos.

**O trabalho montado** (q01): linha de corte da folha 1 arrastada e "está certo"; página 1 e 13 em "Tirar o fundo", 2 e 8 em Mágico pro, 3 em Preto e branco, 5 em Melhorar; página 13 com o alerta "Conferir o fundo tirado" e "está bom assim"; 6 de 13 conferidas; 9 ações no Histórico. Guardei cópia dos três arquivos como referência.

## As reproduções da rodada anterior

| Script | Antes do conserto | Agora |
|---|---|---|
| `reproduz_mesmo_nome.py` | livro 1 perdia tudo ao fechar com o livro 2 aberto | livro 1 intacto (`magico_pro` nas 4 páginas), livro 2 na pasta dele, nenhum aviso |
| `reproduz_fechar_no_o_que_fazer.py` | `projeto.json` ficava com 0 páginas | 4 páginas, filtros e conferidas intactos; o "continuar" traz tudo; nenhum aviso |
| `reproduz_dividir_desmarcado_abrir.py` | "Dividir" voltava marcado e a conferência recomeçava | "Dividir" continua desmarcado, 3 páginas, filtros intactos, nenhum aviso |

## A janela, passo a passo

| Passo | Resultado | Print |
|---|---|---|
| **Bug 1:** outro PDF, mesmo nome, aberto pelo "Abrir" | Pergunta do fundo (é livro novo), projeto novo "Modelo Siebmacher (2)", tudo em Original, Histórico vazio | q02, q03 |
| ...fiz um "está certo" nele e **fechei o programa com ele aberto** | **Consertado.** O trabalho do livro 1 ficou **igual byte a byte** à referência; nenhuma pasta-sombra; o cartão continua "6 de 13" | q04 |
| ..."continuar" do livro 1 | Trabalho inteiro, na página onde parou, nenhuma mensagem | q05 |
| **Bug 1 pelo "Confirmar e processar":** troquei para o outro livro na mesma janela (menu Arquivo → Abrir) e processei | **Consertado.** PDF gerado; livro 1 intacto (nem a data dele mudou); o outro livro gravado na pasta dele | q15, q16, q17 |
| **Bug 2:** abri o livro salvo pelo "Abrir" e fechei o programa na tela "O que fazer" | **Consertado.** Trabalho igual byte a byte; o resumo nem foi regravado; cartão "6 de 13" | q06, q07 |
| **Bug 2, outra forma:** "continuar" e fechar durante "Olhando o livro..." (28%) | **Consertado.** Trabalho igual byte a byte | q08 |
| **Recomeço de verdade:** voltar para as opções e desmarcar "Dividir folhas ao meio" | Mensagem com o motivo certo, 13 páginas viram 7; cópia `projeto.antigo-2026-09-29-2229.json` **igual byte a byte** à referência | q09, q10, q11 |
| **Mensagem do recomeço (p23)** | **Consertado.** O caminho começa inteiro depois de "recuperada:"; a linha só quebra no espaço de "Modelo Siebmacher" | q10 |
| **Bug 3:** depois do recomeço, reabri pelo "Abrir" (caminho com `/`) sem mexer em nada | **Consertado.** "Dividir folhas ao meio" vem **desmarcada**; "Conferir" dá as 7 páginas com o trabalho, **sem recomeçar e sem mensagem** | q12, q13 |
| Reaberto pela linha de comando (caminho com `\`, como o Windows) | Trabalho igual, 7 páginas (o "Dividir" desmarcado também veio por aqui) | q14 |
| Trocar de livro na mesma janela (com o livro 1 aberto na conferência, abrir o outro) | O outro livro vem com as opções **dele** ("Dividir" marcado), não as do livro 1; livro 1 não foi regravado | q15 |
| Livro **movido** de pasta: cartão | "o PDF saiu do lugar / procurar de novo" | q18 |
| Movido, aberto pelo "Abrir" no lugar novo | Trabalho igual; caminho novo gravado | q19 |
| **Cópia** do mesmo PDF em outra pasta, pelo "Abrir" | O trabalho vem (é o mesmo projeto); o caminho passa a ser o da cópia (como na rodada anterior) | q20 |
| **Dois projetos do mesmo PDF** (fiz um segundo projeto, "Siebmacher antigo", copiando a pasta e pondo tudo em Preto e branco, com data mais velha) | **Confirmado o que o implementador deduziu:** o "continuar" do cartão "Siebmacher antigo" abre o **outro** projeto (página 7 em Mágico pro, e não Preto e branco); a data do outro é que muda. O trabalho do antigo não se perde do disco, mas **não dá para chegar nele pelo cartão** | q24, q25 |
| **Bug novo:** voltar para as opções → "Conferir" → "cancelar" em "Olhando o livro..." | Volta para a conferência com o trabalho | q21 |
| ...pus a página 12 em Mágico pro e a 11 em Preto e branco | Na tela, certo. **No disco, nada mudou** (o `projeto.json` ficou igual; só o `acoes.jsonl` ganhou as 2 linhas) | q22 |
| ...fechei e abri de novo | **As duas mudanças sumiram** (página 12 em Original), sem mensagem nenhuma | q23 |

## Bug novo (grave): depois de "cancelar" a análise, nada mais é gravado

- **Como acontece:** livro com trabalho, na conferência → "Voltar para as opções" (menu Arquivo) → "Conferir" → "cancelar" na tela "Olhando o livro...". O `analisar` põe `trabalho_carregado = False`; o `cancelar` volta para a conferência (o projeto ainda tem as páginas), mas ninguém devolve `trabalho_carregado` para verdadeiro. Daí em diante o `_salvar_agora` sai sem gravar (há trabalho salvo), tanto pelo relógio quanto ao fechar e ao processar. O PDF processado sai certo (usa o projeto da memória), mas o projeto salvo não.
- **Nasceu do conserto `4c01fa6`**: antes dele, o `_salvar_agora` sempre gravava. É o preço da trava, num caminho que os testes novos não cobrem.
- **O que se perde:** tudo o que for feito depois do "cancelar", até fechar o programa, sem aviso. O trabalho de antes fica.
- **Onde:** `ui/janela_principal.py`, `cancelar` (e `analisar`). Uma ideia, para o implementador pesar: ao voltar para a conferência com o projeto já analisado, devolver `trabalho_carregado` ao valor de antes da análise (o `analisar_projeto` só troca as páginas no fim, então cancelado ele não mexe no projeto).
- Reproduzido na janela (q21 a q23) e sem janela (`reproducoes/sonda_cancelar_e_dois_projetos.py`, parte P1).

## Ressalvas

1. **Velocidade não medida** (ordem da gerente).
2. **Arrastar o PDF para a janela** e **roda do mouse** não testados (exigem o mouse do Samuel). Arrastar entrega o caminho com `/`, igual ao "Abrir", que foi testado.
3. **O filtro do livro trazido de volta** (a outra metade do `f0abd32`) **não foi conferido de olho**: nos prints, as bolinhas de escolha do filtro na tela "O que fazer" aparecem vazias em todas as opções (até em livro novo, que vem em Original), então não dá para ver qual está marcada. Pode ser só o print fora da tela ou o estilo das bolinhas; vale o Samuel olhar na tela dele. A parte do "Dividir", que se vê, está certa. O teste de máquina do implementador cobre o filtro.
4. **Dois projetos do mesmo PDF:** hoje não vi como isso nasce no uso normal (o programa reaproveita o projeto pela assinatura). A pasta real do Samuel **não tem** dois cartões do mesmo livro (as pastas-sombra do Palatino e da Rhetorica não têm `resumo.json` e não aparecem). Por dedução do código, se os dois projetos tiverem "Dividir" diferente, o "continuar" do antigo leva as opções do antigo para o projeto do mais recente e **recomeça o mais recente** (com cópia). Não testei na janela.
5. **O Histórico depois do recomeço** continua listando as ações antigas (já relatado na rodada anterior; q11).
6. **Testes automáticos escrevem na pasta de dados real do Samuel quando rodados sem trocar o `LOCALAPPDATA`**: o `erros.log` real tem entradas de 21:57 com caminhos `pytest-of-fotog\...\nao_e_pdf.pdf`; e as pastas `projetos\camadas` e `projetos\comum` (criadas às 20:00, `projeto.json` de 20:26) são dos testes de `tests/test_tirar_fundo_no_programa.py` pelo antigo `historico.salvar_projeto`. Esse caminho foi tirado no `7bb3905`, então as pastas não devem voltar; o `erros.log` continua. **Eu não apaguei nada**: são duas pastas-sombra sem `resumo.json` na pasta real, a gerente pergunta ao Samuel. Eu rodei o `pytest` com pasta de dados própria (a primeira tentativa, sem isso, eu parei a 12% antes de ela mexer em qualquer coisa: conferi a lista de arquivos).
7. **Incidentes meus, janelas na tela do Samuel:** antes de eu ligar o vigia, duas janelas do programa de teste ficaram **na tela**: a pergunta "Fundo separado" (cerca de 1 a 2 minutos, perto das 22:13) e a janela "Ver de perto", aberta sozinha por um clique meu num cartão de filtro (cerca de 2 minutos, perto das 22:17; q26). Depois das 22:18 toda janela nova foi para fora da tela em menos de meio segundo. A janela principal aparece por um instante a cada abertura, antes de ir para fora.
8. **Pequeno, de uso:** clicar num cartão de filtro da aba Filtro às vezes abre a "Ver de perto" (parece contar como clique duplo). Não é deste item; anoto porque atrapalhou o piloto.
9. A pasta `saida_teste\verificador_trabalho_salvo_2\` (livros copiados, pasta de dados de teste, PDF processado, scripts) foi criada por mim nesta tarefa e ficou como prova; pode ser apagada.
10. Os scripts de piloto (`piloto.py`, `vigia.py`, `estado.py`) estão em `reproducoes/`; eles usam a pasta onde estão, então devem ser rodados de dentro de `saida_teste\verificador_trabalho_salvo_2\`.

## Bugs para a Lista de bugs (29/09/2026)

| Data | Bug | Onde | Print |
|---|---|---|---|
| 29/09 | **GRAVE, novo (nasceu do `4c01fa6`): depois de "cancelar" na tela "Olhando o livro..." de um livro que já tem trabalho, o programa volta para a conferência, mas nada do que se faz depois é gravado**, nem ao fechar; some sem aviso. O trabalho de antes fica. | `ui/janela_principal.py` (`cancelar` não devolve `trabalho_carregado`) | `q21`, `q22`, `q23`; `reproducoes/sonda_cancelar_e_dois_projetos.py` |
| 29/09 | Dois projetos do mesmo PDF: o "continuar" do cartão mais antigo abre o mais recente (o trabalho do antigo fica no disco, mas inalcançável pelo cartão). Sem caso real hoje na pasta do Samuel. | `ui/janela_principal.py` (`_continuar_projeto` → `abrir_livro` → `achar_por_assinatura`) | `q24`, `q25` |
| 29/09 | Testes gravam na pasta de dados real quando rodados sem `LOCALAPPDATA` próprio (`erros.log`; e antes do `7bb3905`, as pastas-sombra `projetos\camadas` e `projetos\comum`, que continuam lá). | `tests/` (sem `conftest.py` que troque a pasta de dados) | — |

## Arquivos

- Prints: `relatorios/conferir/fase1-2026-09-29-trabalho-salvo-2/verificador/q01...q26.jpg`
- Reproduções e scripts: `relatorios/conferir/fase1-2026-09-29-trabalho-salvo-2/verificador/reproducoes/`
- Material de teste: `saida_teste\verificador_trabalho_salvo_2\`
