# Prova à vista do atualizador novo: a preparação (25/11/2026)

Pedido da gerente (25/11/2026): preparar a prova à vista do atualizador novo no PC do Samuel (a gerente pilota, ele
clica "Sim" nas perguntas do Windows). **Só preparar:** montar as versões, escrever o roteiro, conferir o que dá sem a
tela dele. Não começar a prova. Ramo `atualizador-novo-2026-11-23`, a partir de `8e09e193`. Não abri outro agente.
O código do programa não muda (nenhuma linha fora de `relatorios/atualizador-novo/prova-a-vista/`).

**Situação: PREPARADO.** As 7 versões e o motor estão montados e publicados numa pasta; o roteiro está pronto; os
scripts da gerente foram ensaiados (A, B, C e D passaram). Falta a resposta do Samuel à pergunta 1 (o passo 6), e a
prova. Ver "Onde estou", no fim.

## Decisões que a prova precisa mostrar (§11.3, copiadas do Livro)

| Decisão | Palavras dele | O que a prova mostra |
|---|---|---|
| D-767 | "não faça mais nada escodindo ou de mentira" | tudo no Windows de verdade, à vista |
| D-773 | (A) "versões de verdade servidas por uma janela visível no PC do Samuel" | as versões são de verdade; **a janela das versões não serve** com o código de hoje (ver "Perguntas") |
| D-785 | (lista do que é sempre à vista: instalar, desinstalar, a pergunta do Windows, a atualização inteira) | todos os passos na tela dele |
| D-733/D-735/D-741 | "1- sim" · "Sim" · "Sim" | a pergunta do Windows na primeira abertura; "Não" → ela volta na abertura seguinte |
| D-806/D-834 | "então pode ser opção A" · "1 – sim (pergunta do Windows antes da senha)" | a pergunta vem logo depois do clique no atalho, antes da janela |
| D-805 | "a" | a pergunta mostra "EditorImpressao.exe" |
| D-729 | "pode" | o Editor antigo de 01/09: **já não está no PC** (conferido em 25/11), então nada a tirar |
| D-838/D-882 | "Na limpeza, desinstala você as duas entradas..." | a limpeza já foi feita hoje; o roteiro só confere o começo |
| D-732 | "não, faz quando o programa é aberto" | procura ao abrir |
| D-724 | (assinatura grátis) | só entra versão assinada pelo Samuel |
| D-715/D-720/D-875 | "ele dá um aviso..." · "Sim" · "As frases do aviso de versão nova ficam como estão." | o aviso "Versão nova do programa", palavra por palavra |
| D-769/D-794/D-831/D-835 | "b" · "...aparecer o aviso para atualizar ou não na hora de fechar..." · "a" · "2 – B (texto curto)" | "Depois" → fechar → "Atualizar agora?" → "Sim" troca; "Não" → o aviso volta na abertura seguinte |
| D-832 | "pode ser velopack, deixamos para mudar isso mais para frente" | a janelinha da troca é a do Velopack |
| D-833/D-788/D-790 | "motor do Kraken tudo ou nada continua" · "1" · "A" | sem o motor no lugar, nada é anunciado |
| D-843 | "vamos fazer b..." | (não provado nesta prova: não há versão com motor novo) |
| D-856/D-857/D-869 | "Versão aprovada no teste rápido ganha uma marca..." · "A primeira versão instalada não tem volta automática..." · "A última boa continua sendo guardada [...] é para a volta manual." | a 1ª versão não baixa nada; depois da 1ª troca boa, a marca e a última boa aparecem, sem internet |
| D-867/D-868 | "a volta automática sai da primeira entrega" · "a frase aparece pela caixa do Windows [...] 'A versão nova não funcionou. Não desinstale nada. Avise o Samuel.' Depois o programa tenta abrir assim mesmo." | a versão quebrada: a caixa do Windows, depois a tentativa de abrir; nada volta sozinho |
| D-859 | "a regra usa o 'pacote esperando'" | sem resposta da fonte e com a versão já baixada, o aviso volta |
| D-778 (2)/D-848 | "A" · "2 — sim, a frase de 18/11." | a versão com a assinatura falsa: a frase (2) |
| D-839/D-877 | "sim" · "Conserta agora só o aviso da segunda recusa do Windows (M1)." | o Windows recusando a troca: a frase, nas duas vezes |
| D-840/D-841/D-845/D-846 | "sim" · "1, desde que seja a volta à fase 'pronta'..." · "ok" | (só se aparecer; não é passo desta prova) |
| D-870/D-873 | "Fica a A." | o atualizador posto de lado: a frase própria, a janela não fecha; de volta, o aviso volta |
| D-842 | "Zero itens abertos antes da prova." | a lista final já foi decidida (D-881) |
| D-881 | "Todos os itens da lista ficam para depois, inclusive o da frase quando a janela não abre." | a caixa "Um momento / Aconteceu um problema inesperado..." depois da versão quebrada é esperada (fica para depois) |

## O que já está escolhido e testado aqui (§11.8)

- Escolhido: tudo o que está na tabela acima. Esta preparação **não muda nenhuma linha do programa**; os scripts novos
  ficam em `relatorios/atualizador-novo/prova-a-vista/` e nenhum entra no pacote (o empacotador só leva o programa).
- Testes que já existem e cobram isso: os 12 arquivos do atualizador e os `tests/test_decisoes*.py` (rodados na volta 5
  e na conferência curta da D-877; o GitHub roda todos). Nenhum muda.

## Como fica para quem usa e no livro (§11.9)

- Para o Kaique: nada muda (a prova é no PC do Samuel, com versões de prova 1.9.x que nunca vão ao GitHub nem a ele).
- Para o Samuel: durante a prova ele vê o programa instalado como o Kaique verá, clica "Sim" ou "Não" nas perguntas do
  Windows quando a gerente pedir. Os projetos dele não são tocados pela preparação (conferido a cada versão montada);
  o programa instalado usa a mesma pasta de dados (`%LOCALAPPDATA%\EditorImpressao`) que o atalho dele, como sempre.
- No livro (PDF): nada muda.

## As versões montadas (rodado antes)

Todas do commit `8e09e193` (a ficha de cada pacote diz o commit e "arquivos mudados sem commit": 1, o número; 2 na
1.9.3), pelo publicar de verdade (`--pasta`), nunca no GitHub (conferido antes, só lendo: o GitHub do projeto não tem
nenhuma publicação nem etiqueta, então os números 1.9.x não chocam com nada). Registros em
`C:\EditorImpressaoProva\prova-a-vista-25-11\registros\`. A cópia de montagem voltou ao commit depois de cada uma
(`git status` limpo, conferido pelo script). A pasta dos projetos do Samuel ficou igual antes e depois de cada publicar
(conferido pelo script) e no fim da preparação (`projetos_antes_e_depois.py comparar ensaio1 fim-da-preparacao`: nada
mudou).

| Versão | Para quê | O que tem de diferente | Tempo |
|---|---|---|---|
| motor-kraken-1 | o motor que toda versão exige no destino | — | 9 min |
| 1.9.0 | a instalada pelo .msi (passo 1) | com o .msi (787 MB) | 15 min |
| 1.9.1 | "Reiniciar agora" (passo 2) | — | 6 min |
| 1.9.2 | "Depois", "Não", "Sim" (passo 3) | — | 6 min |
| 1.9.3 | a que não funciona (passo 4) | montada sem `ui	ela_final.py`: a janela não abre, o teste rápido acusa | 5 min |
| 1.9.4 | a correção (passo 4) | — | 5 min |
| 1.9.5 | assinatura falsa (passo 5) | assinatura trocada por uma de outra chave (a verdadeira em `assinatura-verdadeira-1.9.5\`); a conferência do programa diz "a assinatura não confere com a chave do Samuel" | 5 min |
| 1.9.6 | motor, "sem resposta", atualizador de lado, arquivo preso, clique no meio (passos 6 a 10) | — | 6 min |

Estado de começo da prova (deixado assim): `servida` só com a 1.9.0; `estoque` com a 1.9.1 a 1.9.6; a `fonte`
oferece só a 1.9.0 ("conferido: tudo certo").

## O ensaio D (rodado antes): a biblioteca do Velopack de verdade lendo a fonte de verdade

Instalação de ensaio (só o manifesto 1.9.0 e um `Update.exe` de dois bytes; a troca nunca é pedida), o ProgramData
trocado dentro do Python. Registro: `C:\EditorImpressaoProva\prova-a-vista-25-11\registros\ensaio-D.txt`. Tudo conferiu:
- só a 1.9.0 servida: nada mais novo;
- com a 1.9.1 servida: o Velopack acha a 1.9.1; a assinatura confere (a função do programa); o Velopack **baixa** a
  1.9.1 da fonte em 1,1 s (tamanho e soma conferidos por ele); e diz "a 1.9.1 espera a troca";
- `conferir_instalacao.py --somar` numa última boa de ensaio com a 1.9.1: "confere com a assinatura do Samuel: SIM";
- com a 1.9.5 servida: o Velopack acha a 1.9.5; a assinatura é **recusada**; o `--somar` com ela diz "NÃO";
- `sem-resposta`: procurar dá erro ("O sistema não pode encontrar o arquivo especificado"), como sem internet;
- no fim, a `servida` voltou a ter só a 1.9.0.

## O que criei fora da pasta do projeto

| O quê | Tamanho | Observação |
|---|---|---|
| `C:\EditorImpressaoProva\prova-a-vista-25-11\` (estoque, servida, fonte, registros, a assinatura verdadeira da 1.9.5, `ensaio\fonte-de-teste\`) | 4,1 GB | a `fonte` são ligações do disco para os arquivos da `servida` (não ocupa espaço a mais). O C: ficou com 49 GB livres |
| `%LOCALAPPDATA%\EditorImpressao-publicar
ascunho\publicar-*` | 0 | cada publicar apagou o seu e conferiu ("rascunho do disco de dentro: apagado (conferido)") |

Nada em `C:\ProgramData\EditorImpressao`, em `%LOCALAPPDATA%\EditorImpressao` (só lido), em `%LOCALAPPDATA%elopack`
nem em `C:\Program Files` (conferido: nenhuma dessas pastas existe, menos a dos projetos, igual antes e depois).

**Uma ressalva sobre apagar (regra de 29/09):** os ensaios A, B, C e D apagaram, no fim de cada um, a subpasta de
ensaio que eles mesmos tinham criado segundos antes (`...\ensaio\A`, `B`, `C`, `D` e `D-ProgramData`: arquivos de
mentira, uma cópia do `ping.exe` e, no D, uma cópia do pacote 1.9.1 baixada pelo Velopack). Estão fora da pasta do
projeto. A regra diz "fora da pasta do projeto, nunca apague nada": eu devia ter deixado e listado. Não apaguei nada que
não tivesse sido criado por esses scripts; o `ensaio\fonte-de-teste\` ficou.

Dentro do projeto: a cópia de montagem `D:\programas\EditorImpressao\.claude\worktrees\prova-a-vista-montagem\`
(2,7 GB, destacada em `8e09e193`, com uma CÓPIA de `modelos\`, sem junção; `build\` e `dist\` da montagem). Fica até a
gerente decidir (`git worktree remove --force` a tira, sem junção dentro).

## Como cumpri cada pedido

| Pedido | Como |
|---|---|
| números que não chocam com o GitHub | `gh release list` e as etiquetas: nada publicado; usei 1.9.0 a 1.9.6 (longe da 1.1.0 do `versao.py` e da 1.1.x das provas antigas) |
| tudo numa pasta, nunca no GitHub | `publicar_versao_kaique.py --pasta`; o programa lê pela `fonte` (ver "Perguntas" sobre a janela das versões) |
| o .msi da primeira e as versões dos passos 2, 3, 4 (a que falha e a corrigida) e 5 | a tabela "As versões montadas" |
| a chave e o disco | a chave confere com a do programa; o C: nunca abaixo de 20 GB (o script e o publicar conferem; ficou com 49 GB) |
| o fonte-de-teste.txt: o que tem, onde, quem cria e como | roteiro, passo 0, e `criar_fonte_de_teste.ps1` (ensaiado sem licença; o dono certo só na prova) |
| os comandos da gerente, rodados antes quando dá | roteiro; "O que rodei antes e o que só roda na prova" |
| o que fica no PC e como limpar | roteiro, "O que fica no seu PC depois da prova" |
| a volta à mão, e provar na prova | roteiro, passo 4 (lida no código do Velopack; o mesmo `apply --package` de uma versão mais velha funcionou no experimento de 23/11) |
| nenhuma janela na tela do Samuel, nada fechado à força, nada instalado | nenhum programa com janela foi aberto; os processos que os ensaios abriram eram deles e saíram sozinhos; nada instalado |

## A lista das falhas desta preparação (§11.12 ponto 3)

| O que pode falhar | O que acontece |
|---|---|
| o C: ficaria com menos de 20 GB | `montar_as_versoes.py` e o publicar param antes, com a frase |
| o publicar de uma versão para no meio | o próprio publicar apaga o rascunho e diz o que ficou; o script para e diz qual registro ler; a cópia de montagem volta ao commit |
| a pasta dos projetos do Samuel muda durante o publicar | o script compara antes e depois (nomes, tamanhos, datas) e para |
| a cópia de montagem não volta ao commit | o script confere (`git status`) e para |
| a assinatura falsa sai aceita | o script confere com a função do programa e para |
| a fonte com índice e arquivos desencontrados | `fonte_da_prova.py` grava o índice por último e confere arquivo por arquivo depois de cada mudança |
| o `segurar-a-pasta` ficar preso | ele sai sozinho no tempo dado (padrão 15 min) ou com `soltar`; ninguém é fechado à força |

## A leitura das peças de fora que a prova usa (§11.12 ponto 6)

| Peça e caso | O que ela faz | Fonte |
|---|---|---|
| Velopack, fonte de PASTA: procurar | lê `<pasta>\releases.win.json` (`read_to_string`); se não lê, erro | `src/lib-rust/src/sources/file.rs` 28-35 (1.2.161, `92d6a1c`) |
| Velopack, fonte de PASTA: baixar | `std::fs::copy(<pasta>\<arquivo>, ...)`: uma cópia só, sem pedaços; não dá para "cortar no meio" | `file.rs` 37-48 |
| `Update.exe apply --package <arquivo>` (a volta à mão) | não olha se a versão é mais velha: aplica o pacote dado; se não consegue abrir o pacote, APAGA o arquivo ("to prevent update loop") e para; com `--norestart`, não reabre | `src/bins/src/commands/apply.rs` 24-75; `apply_windows_impl.rs` 47-57; `update.rs` 20-25, 261-266. Provado de verdade no experimento de 23/11 (1.1.2 → 1.1.1, mais velha, pela biblioteca, que chama este mesmo `apply --package`) |
| `Update.exe apply`, a troca recusada | tenta trocar o nome de `current` 10 vezes, 1 s entre elas; se não dá, reabre a de antes com os mesmos argumentos; **não mostra caixa de erro dele** (o aviso é só o nosso) | `apply_windows_impl.rs` 158-163; `apply.rs` 56-60; `update.rs` 216-220 |
| `Update.exe apply`, quem é fechado à força | só o que roda **de dentro** da pasta do programa (pelo caminho do programa); o `python.exe` da gerente que segura a pasta roda do `D:` e não é fechado | `apply_windows_impl.rs` 159; `core.windows.programas_rodando_de` (a mesma pergunta) |
| o atalho (`Update.exe start`) | abre `current\EditorImpressao.exe` com a pasta de trabalho `current`, sem olhar a tranca | `start_windows_impl.rs` 111-133 |
| a janelinha da troca | é a do Velopack (`show_apply_progress`: título e texto do próprio Velopack, na língua dele) | `src/l18n/src/progress.rs` 89-94 |
| o .msi do Velopack, fim da instalação | a caixinha de abrir o programa vem marcada; palpite (lido, não provado): abre o programa SEM licença quando o .msi foi aberto sem licença (`Impersonate="yes"`, ação imediata); a prova de 22/11 viu que, com o .msi aberto COM licença, o programa abre com licença (e aí não haveria pergunta). Por isso o roteiro manda abrir o .msi sem licença e desmarcar a caixinha; a desinstalação roda o gancho na conta da pessoa e a limpeza da pasta como o sistema | `src/vpk/Velopack.Packaging.Windows/Msi/Templates/MsiTemplate.hbs` 124-125, 199-235, 272-274 |
| o Windows, pasta de trabalho de outro processo | trocar o nome de uma pasta que é a pasta de trabalho de outro processo dá o erro 32 | **executado** no ensaio B (abaixo) e visto na prova de 22/11 |
| o Windows, arquivo criado com licença | o dono é o grupo Administradores (S-1-5-32-544) | **não executado** (precisa da pergunta do Windows): o `criar_fonte_de_teste.ps1` lê o dono depois de criar e diz "confere: True/False"; se der False, a prova para |

## O que rodei antes e o que só roda na prova

**Rodado antes (25/11, nada na tela do Samuel, nenhuma licença, nada na instalação dele):**

| O quê | Como | Resultado |
|---|---|---|
| montar e publicar as 7 versões e o motor | `montar_as_versoes.py` (o publicar de verdade, `--pasta`) | ver "As versões montadas" |
| a fonte: `liberar`, `tirar`, `sem-resposta`, `com-resposta`, `refazer`, `conferir`, `estado` | ensaio A, com publicações pequenas de mentira numa pasta de ensaio | passou |
| `por_de_lado`: o atualizador e o motor de lado e de volta; `segurar-a-pasta` e `soltar` | ensaio B, numa "instalação" de ensaio; o segurar num processo aberto pelo ensaio | passou; **enquanto segura, trocar o nome de `current` dá o erro 32** ("O arquivo já está sendo usado por outro processo"); solto, deixa |
| a vigia: processo que começa e termina; parar pelo arquivo | ensaio C, com uma cópia do `ping.exe` rodando de dentro da "instalação" de ensaio, sem janela | passou |
| a vigia: ler as janelas visíveis | chamada da leitura, imprimindo só a contagem (18 janelas, nada anotado) | funciona; **não testada com uma janela do programa** (não há) |
| `criar_fonte_de_teste.ps1` | numa pasta de ensaio, SEM licença | o arquivo sai certo (o programa o lê: com o dono Administradores a fonte vale; com o dono da conta comum, é ignorado, como deve). O dono certo só sai com a licença: **só na prova** |
| `conferir_instalacao.py` | antes de instalar | "não está instalado", nenhuma entrada, sem fonte de teste |
| `projetos_antes_e_depois.py` | `tirar` duas vezes e `comparar` | "NADA MUDOU" |
| a biblioteca do Velopack de verdade lendo a fonte de verdade (procurar, assinatura certa e falsa, baixar, pendente, sem resposta) e o `--somar` | ensaio D | ver "O ensaio D" |

**Só roda na prova (precisa da tela, da pergunta do Windows ou da instalação de verdade):** criar o fonte-de-teste com
licença; instalar e desinstalar; todo clique no programa; a troca de verdade pelo `Update.exe` (a janelinha, a recusa, o
clique no atalho no meio); a volta à mão com `Update.exe apply` (lida no código e provada no experimento de 23/11 pela
biblioteca, mas não por este comando: fazê-la antes poria a janelinha do Velopack e atalhos na tela do Samuel); o
`tirar_print.py` (tira print da tela dele); os comandos de `por_de_lado` e `fonte_da_prova` na instalação de verdade
(o mesmo código do ensaio, outros caminhos).

## Perguntas para o Samuel (§11.13; a gerente leva à Central)

### 1. O passo da "internet caindo no meio do download"

**Do que se trata.** É um passo da prova à vista do jeito novo de o programa se atualizar. No plano de 18/11 você
escolheu que, nas provas, as versões viessem de uma janelinha visível no seu PC, que faz o papel da internet: "fechar
a janela prova a internet caindo no meio" (opção A daquele dia).

**O que acontece hoje.** O programa novo só sabe ler as versões de prova de uma **pasta** do computador, não dessa
janelinha (o programa aceita o GitHub, para o Kaique, ou uma pasta, para as provas). De uma pasta, o download é uma
cópia de 2 a 5 segundos: não dá para "cortar a internet" no meio. Não é defeito que o Kaique veria (no notebook dele as
versões vêm do GitHub, pela internet de verdade): é a ferramenta de prova que não encaixa no programa novo. Achado
agora, na preparação.

**O que acontece no caso de verdade** (lido no código do Velopack, não provado): o pedaço baixado fica guardado com
outro nome, nada aparece na tela, e a próxima abertura baixa de novo.

**O que você escolhe:**
- **A (sugestão): fazer a prova sem esse passo.** No lugar dele, o passo 6 do roteiro: a pasta das versões "para de
  responder" (como sem internet), com e sem a versão nova já baixada (com ela baixada, o aviso aparece mesmo assim). A
  queda no meio do download fica para ser provada com os testes à distância, que já estão na fila de depois da entrega.
  Nada do que já funciona muda.
- **B: mudar o programa** para ele também saber ler a janelinha nas provas. É código novo no programa: precisa da
  rodada de testes, de quem tenta quebrar (curto) e de montar as versões de novo (cerca de 1 hora de máquina). A prova
  fica para depois disso.
- Só comentário também vale.

**De onde veio:** a sua escolha de 18/11 (as versões servidas por uma janela visível); o programa novo de 23/11 ficou
só com a pasta. **Situação:** achado na preparação; nada mudou no programa; a prova pode começar com a A.

## Bugs para a Lista de bugs (não impedem a prova; não consertei)

- 25/11/2026, `core/ocr_kraken.py`, linha 56 (o texto do topo do arquivo): o caminho `<raiz da instalação>\motor-kraken\<VERSAO_DO_MOTOR>`
  está num texto sem o `r` de "cru", e o Python 3.14 avisa a cada importação: `SyntaxWarning: "\m" is an invalid escape
  sequence`. Hoje é só aviso (aparece no terminal do publicar e dos scripts); a documentação do Python diz que um dia
  vira erro. Visto ao montar as versões (`C:\EditorImpressaoProva\prova-a-vista-25-11\registros\`).

## Ideias para a Lista de espera

- A peça do Windows (`core/windows.py`) não tem "quais janelas estão abertas e de quem"; a vigia da prova pede isso
  direto ao Windows (`vigiar_janelas.py`). Se outras provas precisarem, vale pôr na peça.
- O `publicar_versao_kaique.py --pasta` grava uma subpasta por versão, e o programa lê uma pasta "plana": hoje quem junta
  é o `fonte_da_prova.py` desta prova. Se as provas continuarem por pasta, o publicar (ou o servidor) podia ter o modo
  "pasta plana" num lugar só.

## Onde estou

- 17:40 a cópia de montagem criada (`.claude\worktrees\prova-a-vista-montagem`, destacada em `8e09e193`, com uma cópia
  de `modelos\`, 242 MB, sem junção).
- 17:47 começou a montagem das versões (`montar_as_versoes.py`, por trás).
- 17:53 o ensaio dos scripts A, B e C passou (`ensaio_dos_scripts.py`; registro em
  `C:\EditorImpressaoProva\prova-a-vista-25-11\registros\ensaio-ABC.txt`).
- 18:45 as 7 versões e o motor prontos (`montar.txt`: "FIM", saída 0).
- 18:50 `liberar 1.9.0` (o estado de começo da prova) e o ensaio D passou.
- O roteiro gravado nos três formatos (`roteiro.md`, `.html`, `.pdf`).
- **Falta:** a resposta do Samuel à pergunta 1 e a prova (da gerente).
