# Opinião do verificador: consertos de "perda de trabalho salvo" (29/09/2026)

Commits conferidos: `144d29f`, `e04f408`, `3cfb682`, `bd44929`, `766395f` (ramo `fase-1`).

> **Aviso (decisão do Samuel, 28/09): moldura dourada e iluminura são defeito conhecido** até a Fase 1 ficar pronta (itens 1.2, 1.4 e 1.5). Esta conferência não é de imagem; o aviso vale para a fase.

## Veredito

**NÃO ESTÁ PRONTO.** Os cinco consertos fazem o que prometem: na janela de verdade, o trabalho voltou inteiro com o caminho escrito com `\`, com `/` e em maiúsculas; com o livro mudado de pasta (pelo "Abrir", pelo "procurar de novo" e pelo "continuar"); e na cópia do PDF em outra pasta. O recomeço de verdade guarda uma cópia idêntica do trabalho, e a mensagem nova é clara. O "Para revisar" agora conta o alerta que chega pela prévia.

**Mas achei dois caminhos antigos, e graves, em que o trabalho ainda se perde de vez, sem cópia e sem aviso nenhum.** Um deles é exatamente o caso que a gerente mandou testar: **outro PDF com o mesmo nome e o mesmo número de páginas**. Ele não recebe o trabalho do primeiro, mas **basta fechar o programa com ele aberto para o trabalho do primeiro ser apagado**. O outro: abrir um livro salvo e fechar o programa na tela "Marque o que você quer fazer" (ou antes de a análise acabar) apaga o trabalho.

Quem decide é o Samuel. Isto não é aprovação.

## É seguro o Samuel mover os PDFs de pasta?

**Mover, sim: em todas as formas que testei, o livro movido voltou com o trabalho inteiro e o caminho novo ficou gravado.** Mas, enquanto os dois defeitos abaixo não forem consertados, ele precisa de dois cuidados, que valem com ou sem mudança de pasta:

1. **Não ter, ao mesmo tempo, dois PDFs *diferentes* com o mesmo nome de arquivo** (por exemplo, uma versão nova e uma velha do mesmo livro, com o mesmo nome, em pastas diferentes). Cópia idêntica não tem problema; o perigo é arquivo diferente com nome igual.
2. **Depois de abrir um livro que já tem trabalho, não fechar o programa antes de clicar em "Conferir" e ver as páginas aparecerem.**

## O que foi feito (máquina ou olho)

| O quê | Tipo | Resultado |
|---|---|---|
| Testes automáticos (`pytest tests -q`) | máquina | **1082 passaram, 1 pulado, nenhum falhou** (os instáveis conhecidos passaram) |
| Os dois arquivos de teste novos e o teste do "Para revisar" | máquina | 41 passaram |
| Leitura das mensagens dos commits, das Tentativas 28 a 33 e do código de `projetos.py` e `ui/janela_principal.py` | olho no código | ver "Bugs" |
| Janela real do programa, 29 prints, todos olhados | olho | ver "A janela, passo a passo" |
| Comparação do trabalho salvo em disco, antes e depois de cada passo (filtro, conferida, alerta, corte e linha de corte de cada página e folha) | máquina | ver a tabela |
| Três reproduções sem janela dos defeitos novos | máquina | `reproducoes/` nesta pasta |
| Velocidade | — | **Não rodei** (ordem da gerente) |

Como pilotei: instância nova (`pythonw`), pasta de dados própria (`LOCALAPPDATA` trocado para `saida_teste\verificador_trabalho_salvo\dados`), janela fora da tela, cliques por mensagem nativa, prints com `PrintWindow`, fechamento com `WM_CLOSE`. O "Abrir" e o "procurar de novo" foram feitos pela caixa de verdade do Windows. O livro de teste é uma **cópia** montada com 6 folhas duplas do Siebmacher (páginas 7 a 12) e 1 página do Palatino (a 9, que dá o alerta do "tirar o fundo"): 7 folhas, 13 páginas. O "outro livro" é montado do mesmo jeito com outras páginas (Siebmacher 20 a 25 e Palatino 7): **mesmo nome de arquivo, mesmo número de folhas e de páginas, conteúdo diferente**. Nenhum PDF do acervo foi aberto pelo programa; a pasta de dados real do Samuel não foi tocada (só li a lista de nomes das pastas, ver "Bugs").

**O trabalho montado** (p01 a p03): linha de corte da folha 1 arrastada e "está certo"; página 1 e 13 em "Tirar o fundo", páginas 2 e 8 em Mágico pro, 3 em Preto e branco, 5 em Melhorar (6 páginas conferidas); página 13 com o alerta "Conferir o fundo tirado" e "está bom assim"; 9 ações no Histórico. Essa foi a referência de todas as comparações.

## A janela, passo a passo

| Passo | Resultado | Print |
|---|---|---|
| Trabalho montado, livro aberto pela linha de comando (caminho com `\`) | Certo | p01, p02, p03 |
| **Caso t03:** alerta que chega pela prévia (página 13 posta em "Tirar o fundo") | **Consertado.** "Para revisar 1 – Conferir o fundo tir..." aparece antes de as outras prévias chegarem, sem virar a página | p02 |
| **Caso t03 de novo, igual à rodada de 18:26:** livro novo, "Sim, tirar o fundo", aba Filtro na página 1 | **Consertado.** Em até 4 segundos o quadro diz "Para revisar 1", sem virar a página | p11, p12 |
| **Caso t11:** salvo com `\`, reaberto pelo "Abrir" (o programa recebe `/`) | **Consertado.** Nenhuma mensagem; filtros, corte, conferidas, alerta e Histórico iguais | p04 |
| Reaberto pela linha de comando com `\` (depois de salvo com `/`) | Trabalho igual | p05 |
| Reaberto com tudo em maiúsculas | Trabalho igual. O nome aparece em maiúsculas na tela "O que fazer" ("MODELO SIEBMACHER.PDF"), só aparência | p06 |
| PDF **movido** para pasta nova: tela inicial | Cartão "o PDF saiu do lugar / procurar de novo". Certo | p07 |
| Movido, reaberto pelo "Abrir" | Trabalho igual; caminho novo gravado no resumo e no projeto | p08 |
| Movido de novo, "procurar de novo" apontando o arquivo | Trabalho igual; caminho novo gravado | p09 |
| Movido para uma pasta que o programa já conhece: cartão | "continuar", religado sozinho (a outra pasta conhecida tem um arquivo de mesmo nome e outro conteúdo, e ele não foi confundido) | p28 |
| "continuar" do livro religado | Trabalho igual; caminho novo gravado | p29 |
| **Cópia** do mesmo PDF em outra pasta, aberta pelo "Abrir" | O trabalho vem (é o mesmo projeto); o caminho do projeto passa a ser o da cópia. Ver ressalva 3 | p21 |
| **Outro PDF, mesmo nome e mesmo número de páginas**, aberto pelo "Abrir" | Pergunta do fundo (é livro novo), projeto novo "Modelo Siebmacher (2)", tudo em Original, Histórico vazio. **Certo nesse momento** | p10 |
| **...e depois de fechar o programa com esse outro livro aberto** | **O trabalho do primeiro livro foi apagado**, sem cópia; o cartão continua dizendo "6 de 13 conferidas"; ao continuar, tudo em Original, **nenhuma mensagem**; o Histórico ainda lista as ações antigas; e as linhas de corte das folhas passam a ser as do outro livro. **Bug 1** | p15, p16, p17 (e p14, a primeira vez que aconteceu, sem eu perceber a causa) |
| **Recomeço de verdade:** "Dividir folhas ao meio" desmarcado | Mensagem nova (abaixo); 13 páginas viram 7 | p22, p23, p24 |
| A cópia `projeto.antigo-*` do recomeço | **Existe e é igual byte a byte** ao trabalho de antes: `projeto.json`, `acoes.jsonl` e `posicao.json` | — |
| Reabrir pelo "Abrir" sem mexer em nada, depois desse recomeço | A opção "Dividir folhas ao meio" volta **marcada** sozinha, e a conferência **recomeça de novo**, com a mensagem "Isso acontece quando se muda a opção..." — mas a pessoa não mudou nada. Há cópia. **Bug 3** | p25, p26 |
| Abrir livro salvo e fechar o programa na tela "Marque o que você quer fazer" | **O trabalho some**: o `projeto.json` fica com 0 páginas, sem cópia; o cartão passa a "0 de 13 conferidas"; ao continuar, tudo em Original e **nenhuma mensagem** (a cópia feita nessa hora é de um projeto vazio). **Bug 2** | p18, p19, p20 |
| Fechar durante "Olhando o livro..." (depois do "continuar") | Neste livro pequeno a análise acabou antes do meu fechar (o trabalho ficou). Sem janela, com a análise parada, apaga do mesmo jeito que o Bug 2 | — |

**A mensagem nova do recomeço** (p23), em português comum, com o motivo certo:

> Comecei a conferência deste livro de novo: o trabalho salvo tinha 13 páginas e agora o livro tem 7. Isso acontece quando se muda a opção "Dividir folhas ao meio".
>
> O trabalho anterior não foi apagado. Guardei uma cópia dele, que pode ser recuperada:
> D:\programas\...\projetos\Modelo Siebmacher\projeto.antigo-2026-09-29-2033.json

Dois reparos pequenos: o caminho quebra a linha logo depois de "D:" (fica "D:" sozinho numa linha); e "pode ser recuperada" promete algo que o programa não faz sozinho (não há botão para recuperar; está na Lista de espera, 29/09).

## Os caminhos em que o trabalho ainda se perde sem cópia (pergunta 3 da gerente)

1. **Bug 1 (grave, antigo, 18/07): dois PDFs diferentes com o mesmo nome de arquivo.** Ao fechar o programa, `closeEvent` chama `historico.salvar_projeto(self.projeto)`, que grava o `projeto.json` numa pasta escolhida **pelo nome do livro** (`historico.pasta_do_projeto(projeto.nome)`), e não na pasta do projeto (`resumo.pasta`). O segundo livro mora em "Modelo Siebmacher (2)", mas é gravado também em "Modelo Siebmacher", **por cima do trabalho do primeiro**. O `processar` (Confirmar e processar) chama a mesma função. O conserto `3cfb682` piora o sintoma: antes, ao reabrir o primeiro livro, aparecia a mensagem de recomeço; agora a assinatura bate com o arquivo aberto e o estado do *outro* livro é aceito calado, com as linhas de corte dele. Reproduzido na janela real e sem janela (`reproducoes/reproduz_mesmo_nome.py`: livro 1 nem sai do lugar e perde tudo).
2. **Bug 2 (grave, antigo): fechar o programa entre abrir o livro e o fim da análise.** Depois de abrir um livro salvo (Abrir, arrastar, abrir pelo Windows, "continuar"), o projeto em memória ainda está vazio; o `closeEvent` grava esse projeto vazio por cima do salvo (`_salvar_agora`), sem cópia. Na próxima vez não aparece mensagem nenhuma. Reproduzido na janela real ("O que fazer") e sem janela ("continuar" com a análise parada): `reproducoes/reproduz_fechar_no_o_que_fazer.py`.
3. **"começar de novo" do cartão:** confirmado no código (`_recomecar_projeto`): apaga `projeto.json`, `acoes.jsonl` e `posicao.json` sem cópia, depois de perguntar. É pedido da pessoa; a Lista de espera já pede cópia também aqui.
4. **"Tirar da lista" do cartão:** apaga a pasta inteira do projeto, **inclusive as cópias `projeto.antigo-*`**. Também pergunta antes. Vale saber que a rede de segurança some junto.
5. **Bug 3 (não perde de vez, mas recomeça sem motivo):** livro conferido com "Dividir folhas ao meio" desmarcado e reaberto pelo "Abrir", arrastando ou pelo Windows: a tela "O que fazer" volta com a opção marcada, a conferência recomeça e a mensagem diz que a pessoa mudou a opção. Há cópia. Pelo "continuar" não acontece. É da mesma família do bug já registrado "as caixinhas perdem o que se muda". `reproducoes/reproduz_dividir_desmarcado_abrir.py`.

## Ressalvas

1. **Velocidade não medida** (ordem da gerente).
2. **Roda do mouse e arrastar o PDF para a janela** não testados (arrastar de fora exige o mouse do Samuel). Arrastar entrega o caminho com `/`, igual ao "Abrir", que foi testado.
3. **Cópia do mesmo PDF em outra pasta:** as duas cópias viram um só projeto, e o caminho gravado passa a ser o da última aberta. Se depois a pessoa apagar essa cópia, o cartão diz "o PDF saiu do lugar" (a outra pasta pode não ser conhecida). Não perde trabalho; é só um "procurar de novo" a mais.
4. **Histórico depois do recomeço:** as ações antigas continuam listadas no Histórico da conferência nova (o `acoes.jsonl` não é recomeçado). Não testei clicar nelas; pode desfazer coisas que não existem mais na conferência nova.
5. **A pasta de dados real do Samuel (só olhei os nomes, sem abrir nem mudar nada):** as pastas "Giovambattista Palatino cittadino romano" e "Rhetorica Christiana -  Fray Diego Valadés" têm **só** um `projeto.json`, gravado uma fração de segundo depois do projeto verdadeiro ("... (2)" e "... Valades"). São as cópias-sombra do Bug 1. Hoje elas não têm projeto verdadeiro dentro, então **não achei trabalho real do Samuel perdido por isso**; e explicam o bug já registrado "alguns projetos não aparecem na lista". Mas mostram que o Bug 1 acontece no uso real.
6. Um incidente meu: a caixa "Abrir" do Windows recusou o caminho com `/` digitado e mostrou um aviso ("O nome do arquivo não é válido", p27) que ficou **na tela** por cerca de um minuto antes de eu tirá-lo de lá. Se o Samuel viu uma janelinha "Escolha o PDF do livro" entre 20:10 e 20:11, era minha.
7. Os prints ficam alguns segundos atrasados quando a janela está fora da tela (o primeiro print depois de trocar de tela às vezes mostrava a tela anterior); por isso cada print foi tirado duas vezes e conferido contra o estado do programa.
8. A pasta de teste `saida_teste\verificador_trabalho_salvo\` (cópias dos PDFs e a pasta de dados de teste) foi criada por mim e ficou como prova; pode ser apagada.

## Bugs para a Lista de bugs (29/09/2026)

| Data | Bug | Onde | Print |
|---|---|---|---|
| 29/09 | **GRAVE, antigo (18/07): fechar o programa com um livro aberto grava o trabalho dele também na pasta de outro projeto de mesmo nome, apagando o trabalho desse outro sem cópia e sem aviso.** `closeEvent` e `processar` chamam `historico.salvar_projeto`, que escolhe a pasta pelo nome do livro. Dois PDFs diferentes com o mesmo nome de arquivo: fechar com o segundo aberto apaga o primeiro. Depois do `3cfb682`, o primeiro livro ainda aceita calado o estado do segundo (linhas de corte do outro livro). Também cria as pastas-sombra sem `resumo.json` na pasta real do Samuel (Palatino, Rhetorica). | `historico.salvar_projeto` / `pasta_do_projeto`; `ui/janela_principal.py` (`closeEvent`, `processar`) | `p15`, `p16`, `p17` (esta pasta) |
| 29/09 | **GRAVE, antigo: abrir um livro salvo e fechar o programa antes do fim da análise (na tela "O que fazer" ou em "Olhando o livro...") apaga o trabalho, sem cópia e sem aviso na próxima vez.** O `closeEvent` grava o projeto ainda vazio por cima do salvo. | `ui/janela_principal.py` (`closeEvent` → `_salvar_agora`) | `p18`, `p19`, `p20` |
| 29/09 | Livro conferido com "Dividir folhas ao meio" desmarcado e reaberto pelo "Abrir"/arrastar/Windows: a opção volta marcada, a conferência recomeça (com cópia) e a mensagem diz que a pessoa mudou a opção. | `ui/janela_principal.py` (`abrir_livro` usa as opções padrão; só o "continuar" traz as salvas) | `p25`, `p26` |
| 29/09 | Pequeno: na mensagem do recomeço, o caminho da cópia quebra a linha depois de "D:". | `ui/janela_principal.py` (`_frase_do_recomeco`) | `p23` |

## Arquivos

- Prints: `relatorios/conferir/fase1-2026-09-29-trabalho-salvo/verificador/p01...p29.jpg`
- Reproduções sem janela (pasta de dados própria em `saida_teste\`): `reproducoes/reproduz_mesmo_nome.py`, `reproduz_fechar_no_o_que_fazer.py`, `reproduz_dividir_desmarcado_abrir.py` (rodar com `.venv\Scripts\python.exe`).
