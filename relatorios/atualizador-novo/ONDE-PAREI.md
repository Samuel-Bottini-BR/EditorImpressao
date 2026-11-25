# Volta 5, segunda rodada: a frase da segunda recusa do Windows (D-877, M1 do quinto "quem tenta quebrar") (25/11/2026)

Pedido da gerente (a minha segunda rodada, a última pela D-815). Palavras do Samuel (D-877): "Conserta agora só o aviso
da segunda recusa do Windows (M1). Os dois testes das proteções (M2) e o achado pequeno ficam para depois, com os
testes à distância." A partir de `958cf552` (o relatório do quinto "quem tenta quebrar"; o código é o de `0d9cac4e`).
Não mexo no M2 nem no leve. Só a caixa de mentira; nenhuma janela nem caixa de verdade.

## Antes de mexer (§11.12)

**O defeito (o M1 do quinto, executado por ele no caso L1 de `provas/prova_casos.py`).** O Kaique clica "Reiniciar
agora"; o Windows não deixa trocar (um arquivo preso); o Velopack reabre a versão de antes com o pedido, e aparece "A
atualização não deu certo. O programa continua na versão de antes e funcionando. Avise o Samuel." (D-839). Na SEGUNDA
recusa para a mesma versão (outro dia, ou na hora), nada aparece: um clique sem resposta.

**A causa.** A frase da D-839 nasce na abertura reaberta pelo Velopack (`fases._frases_ao_abrir` → `fases._frase` →
`MostrarFalha(tipo, id_da_falha(tipo, versão))`), com o nome `troca-<versão>`, SEM o momento. A tela mostra cada nome uma
vez só por conta (`Atualizacao._para_a_tela` → `ler_vistos`/`gravar_visto`). A segunda recusa da mesma versão gera o
mesmo nome, que já está nos "vistos": some. As frases guardadas no bilhete não têm o problema porque o nome delas leva
a hora (`guardar_frase`: "a mesma frase de novo, noutro dia, aparece de novo").

**A regra (como uma frase decide se "já foi vista").** O nome da frase é a chave: a tela mostra um nome uma vez por
conta (`_para_a_tela`). Então o nome tem de dizer O QUE se avisa:
- a frase de um **acontecimento** (algo que aconteceu agora e que pode acontecer de novo: uma troca recusada, um "Sim"
  ao fechar que não trocou) tem de levar o **momento** no nome: cada vez é outro aviso;
- a frase de um **estado** que a abertura encontra de novo a cada vez (a versão publicada sem a assinatura, a versão que
  pede um motor que não está no lugar) leva só o tipo e a versão: uma vez por versão, senão ela se repetiria a cada
  abertura (laço de avisos).

**Os caminhos que usam `id_da_falha` / os "vistos"** (busca: `grep -n "id_da_falha\|ler_vistos\|gravar_visto"` em
`atualizacao.py`, `core/fases_da_atualizacao.py`, `ui/`, `main.py`):

| Caminho | O nome hoje | Acontecimento ou estado? | Tem o problema? |
|---|---|---|---|
| a D-839 na abertura reaberta pelo Velopack (`_frases_ao_abrir` → `_frase`) | `troca-<v>` | acontecimento (cada recusa do Windows) | **SIM: o M1** |
| a D-839 na reabertura sem janela ("Sim" ao fechar) (`_frase` → `GuardarFrase` → `guardar_frase`) | `troca-<v>-<hora>` | acontecimento | não (já leva a hora) |
| a da versão reprovada (`TesteRapido` → `_frase`) | `reprovada-<v>` | acontecimento, mas que só acontece UMA vez por versão (a reprovada não é testada de novo, D-868) | não (não se repete por construção). Fica como está |
| a frase (2) da assinatura recusada na procura (`Assinatura` → `MostrarFalha(id_da_falha)`) | `recusada-<v>` | estado (a versão publicada continua sem a assinatura a cada abertura) | não: uma vez por versão é o certo (a tabela: "a frase (2), uma vez"); com o momento, ela se repetiria a cada abertura |
| a do motor (`Baixou` → `MostrarFalha(id_da_falha)`) | `motor-<v>` | estado (a cada abertura) | não, pelo mesmo motivo (D-843: "uma vez") |
| a (2) em resposta ao "Reiniciar agora" (`TrocaConferida(recusada)`, `sempre=True`) | `recusada-<v>` | resposta a um clique | não (`sempre`: aparece toda vez) |
| as guardadas no bilhete (`guardar_frase`, `guardar_frase_pelo_nome`) | `<tipo>-<v>-<hora>` | acontecimento | não |
| a frase que vai para a caixa do Windows (`_na_caixa_do_windows`) | o nome que veio | — | usa o nome que a regra deu |
| a mesma frase na janela (`_para_a_tela` → `PonteDaTela`) | o nome que veio | — | idem |

Só a D-839 da abertura reaberta tem o defeito. A da reprovada é um acontecimento também, mas não se repete; não mexo
nela (o pedido: "Só conserte além do M1 se for a mesma regra").

**O conserto, num lugar só.** Uma função na regra, `fases.id_do_acontecimento(tipo, versão, momento)` (o nome com o
momento), usada pelos DOIS lugares que dão nome a um acontecimento: a D-839 da abertura reaberta (pelo `_frase`, com o
momento da abertura) e o `guardar_frase` do bilhete (que hoje escreve a mesma conta à mão, `f"{id_da_falha(...)}-{_agora()}"`).
O momento da abertura é um dado que o executor lê na hora e manda no `Abriu` (`momento`), como os outros; a regra
continua sem relógio. Sem momento (os testes da tabela), o nome fica `troca-<v>`, como antes.

**Sem laço (§11.8).** A D-839 só nasce na abertura que o Velopack reabriu com o pedido (a linha de comando), e cada
reabertura dessas é uma recusa do Windows. A abertura seguinte pelo atalho não tem o pedido: nenhuma frase. Então ela
aparece uma vez por recusa, nunca a cada abertura.

**Como fica para quem usa (§11.9).** Antes: a segunda recusa para a mesma versão não dizia nada. Depois: cada recusa
mostra a frase da D-839 uma vez (antes da janela, pela caixa do Windows, D-868) e o aviso da versão nova volta, como na
primeira. No livro (PDF): nada muda.


## A segunda rodada: o que fiz e a prova (D-877)

- **O conserto, num lugar só:** `fases.id_do_acontecimento(tipo, versão, momento)`, a conta única do nome de uma frase
  de acontecimento. Usada pela D-839 da abertura reaberta (`_frase(..., momento=e.momento)`) e pelo `guardar_frase` do
  bilhete (que antes fazia a mesma conta à mão). O momento entra na regra pelo `Abriu.momento`, lido pelo executor
  na abertura (`_agora()`); a regra continua sem relógio. As frases de estado (a 2 na procura, a do motor) e a da
  reprovada continuam com `id_da_falha` (uma vez por versão), como a tabela de "Antes de mexer" explica.
- **Caminho → função:** a D-839 com janela → `_frases_ao_abrir` → `_frase` → `id_do_acontecimento`; a D-839 sem
  janela e toda frase do bilhete → `guardar_frase` → `id_do_acontecimento`; mostrar uma vez → `_para_a_tela`
  (`ler_vistos`/`gravar_visto`), sem mudança.
- **Teste de reversão (§4.7):** `tests/test_decisoes_atualizacao_volta5.py::test_d877_cada_recusa_do_windows_avisa_uma_vez_e_nao_se_repete`
  (o caso L1 do quinto: duas aberturas reabertas com `--conferir-a-versao-nova 7.0.0 7.0.1` na 7.0.0, na mesma conta, e
  depois uma pelo atalho; só a caixa de mentira). No código de `0d9cac4e` ele FALHA pelo comportamento (`[[frase], [],
  []]`: a segunda recusa não dizia nada; saída em `volta5-testes-no-codigo-antigo.txt`, parte 4); no novo passa
  (`[[frase], [frase], []]`: cada recusa avisa uma vez, e a abertura pelo atalho não repete).
- **Mutações (D-827):** V23 (o nome sem o momento) e V24 (a abertura não manda o momento): as duas ACUSADAS pelo teste
  da D-877 (`volta5-provas/mutacoes_volta5-resultado-V23-V24.txt`; a linha sem mutação: nenhum teste falhou).
- **Testes, um arquivo por vez:** os 12 arquivos do atualizador (todos passam: `test_decisoes_atualizacao_volta5` 23,
  `test_atualizador_volta5` 21, `test_fases_da_atualizacao` 2255, e os outros 9) e os `tests/test_decisoes*.py`
  (ver "Os testes da segunda rodada", abaixo).
- **Nenhum teste antigo mudou.** A tabela da regra continua com o nome `troca-1.2.0` (o `Abriu` dela não traz momento).
- **Não mexi** no M2 nem no leve do quinto (D-877: "ficam para depois, com os testes à distância").
- **Tamanho:** os três arquivos do atualizador, de 1352 para 1357 linhas de código (+5: a função do nome do acontecimento e o campo do momento).
- Nenhuma caixa nem janela de verdade; nenhum processo fechado; nada escrito em `C:\ProgramData\EditorImpressao`, em
  `%LOCALAPPDATA%\EditorImpressao` nem na instalação do Samuel (a cópia de `0d9cac4e` para o teste no código antigo
  está em `saida_teste\v5\d877-antigo\`, ignorada pelo git).

### Os testes da segunda rodada

RODADA_D877

# Volta 5 — a volta automática sai da primeira entrega (25/11/2026)

Implementador novo (D-815: as voltas 3 e 4 foram de outro agente). Pedido da gerente de 25/11, depois de o Samuel ler
com o Fable o relatório do quarto "quem tenta quebrar" e decidir a opção A. Ramo `atualizador-novo-2026-11-23`, a
partir de `aba7b844`. Não abri agente. Nenhuma janela na tela do Samuel: as provas com caixa de verdade rodam numa área
de trabalho separada (ver "As provas de verdade"). Nada escrito em `C:\ProgramData\EditorImpressao`, em
`%LOCALAPPDATA%\EditorImpressao` nem na instalação do Samuel.

**Situação: entregue à gerente (a rodada do GitHub é dela). Ver "Onde estou", no fim desta seção.**

## Decisões que esta tarefa precisa cumprir (§11.3)

Palavras do Samuel (chat de 25/11/2026): "Li com o Fable o relatório do quem-tenta-quebrar 4. Decidi a **opção A: a
volta automática sai da primeira entrega.**" Por voz, ao Fable: "é melhor a opção A; os aplicativos geralmente usam
isso; a resposta fica para o Windows dar e não para o aplicativo".

| Decisão | Palavras dele |
|---|---|
| D-867 | "1. Tirar a volta automática: a marca "sem volta", o "uma vez só", a segunda tentativa, o `--voltando`, a fase de volta. A tabela perde a linha "Voltar"." |
| D-868 | "2. O teste rápido fica. Se reprovar: versão vai para "reprovadas" e a frase aparece **pela caixa do Windows, pela peça (`MessageBoxW`)**, nunca pela janela do programa: "A versão nova não funcionou. Não desinstale nada. Avise o Samuel." Depois o programa tenta abrir assim mesmo. Toda frase que pode aparecer antes da janela existir usa esse caminho." |
| D-869 | "3. A última boa continua sendo guardada (de `packages\`, sem internet), mas nada automático depende dela — é para a volta manual." |
| D-870 | "4. Consertar M1 (frase "outra janela" depois da troca certa), M2 (`Update.exe` que some: frase própria, sem "tente ao fechar", e oferecer de novo quando voltar) e M5 (os dois testes)." |
| D-871 | "5. Os testes da volta automática saem com ela. A D-718 fica no Livro como "adiada para depois da entrega", com a prova de que o programa **avisa** quando a versão nova falha." |

As que continuam e não podem mudar (§11.8), copiadas do Livro:
- **D-778, frase (2):** "Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do Samuel. O
  programa continua funcionando. Avise o Samuel." (as (1) e (3) saem desta entrega: D-867, D-868).
- **D-839:** "A atualização não deu certo. O programa continua na versão de antes e funcionando. Avise o Samuel."
- **D-845, D-858, D-864:** "Não deu para atualizar agora: [motivo]. Tente ao fechar o programa.", com os nove motivos da
  D-847, o título "Atualização" (D-846), a mesma frase no "Sim" ao fechar (D-858) e o motivo "havia outra janela do
  programa aberta" (D-864).
- **D-854:** a cópia da última boa é uma cópia de verdade, ao lado do pacote do Velopack.
- **D-856:** "Versão aprovada no teste rápido ganha uma marca no disco e **não é testada de novo**. [...] conferir espaço
  antes de copiar, pela mesma função do motor." (a marca `aprovada-<versão>`; o espaço por `espaco_livre_basta`).
- **D-857:** "A primeira versão instalada não tem volta automática. Sem baixar 460 MB na primeira abertura." A "frase
  (3)" dela passa a ser a frase da D-868.
- **D-859:** "a regra usa o 'pacote esperando'."
- **D-840 / D-841:** "Feche a outra janela do programa e clique de novo." e o aviso de novo depois dela.
- **D-848 / D-849:** a frase 2 no "Reiniciar agora" com o pacote sem a assinatura; o atualizador de outra conta que não
  se consegue conferir: o programa abre normalmente.
- O bilhete só com `CHAVES_DO_BILHETE = ("reprovadas", "frase")`, escrito só por `mudar_o_bilhete`;
  `core/conversa_com_o_velopack.py` o único que importa `velopack`; a K03 (`dar_licenca_aos_usuarios`) sem mudança.
- **Para depois, não mexidas:** D-850, D-861, D-865, D-866.

Do Livro, sobre o que esta volta toca (lido de D-700 em diante): D-718 (volta sozinha: adiada, D-871), D-719 (a frase
da volta: adiada com a D-718), D-724 (só pacote assinado), D-732 (procurar só ao abrir), D-769/D-794/D-831 ("Sim" ao
fechar: nada abre na tela depois), D-806/D-834 (a pergunta do Windows antes da janela), D-833/D-843 (o motor), D-836
(a lista dos testes antigos), D-844 (a guarda da última boa; a volta com ela, adiada), D-851 (copiar de `packages`, sem
internet), D-852 (a assinatura guardada é dado).

## O que já está escolhido e testado aqui (§11.8)

Os arquivos que vou tocar: `atualizacao.py`, `core/fases_da_atualizacao.py`, `core/conversa_com_o_velopack.py`,
`core/windows.py` (só uma função nova: a caixa), o comentário do `main.py`, e os testes do atualizador.
- **Escolhido pelo Samuel e que fica igual:** todas as frases de cima, palavra por palavra; a assinatura antes de
  baixar (D-724); a procura só ao abrir (D-732); "Reiniciar agora" confere por trás antes de fechar e, com outra janela,
  a frase da D-840 e o aviso de novo (D-841); "Depois" leva à pergunta ao fechar (D-831, D-835); o "Sim" ao fechar não
  abre nada na tela (D-769); o motor (D-833, D-843); a marca de aprovada e o espaço (D-856); a primeira versão do .msi
  não é testada nem baixa nada (D-857); o pacote esperando sem internet (D-859); a guarda da última boa (D-844, D-851,
  D-852, D-854); a pergunta do Windows antes da janela (D-806, D-834); o atualizador de outra conta (D-849).
- **Testes que já existem e cobram isso** (todos passam em `aba7b844`, um arquivo por vez, rodados por mim antes de
  mexer): `test_fases_da_atualizacao.py` (a regra inteira, 2387), `test_atualizador_novo.py`, `test_atualizador_volta2.py`,
  `test_atualizador_volta3.py`, `test_atualizador_volta3_de_verdade.py`, `test_atualizador_volta4.py`,
  `test_atualizador_d851.py`, `test_decisoes_atualizacao.py`, `test_decisoes_ajudante_da_atualizacao.py`,
  `test_velopack_de_verdade.py`, `test_windows_peca.py`, `test_windows_preparo_do_computador.py`,
  `test_trava_windows.py`, `test_porteiro_licenca_que_acrescenta.py` e os 64 `tests/test_decisoes*.py`.
- **O que muda por decisão dele nesta volta (e só isso):** sai a volta (D-867) e os testes dela (D-871, pela lista da
  D-836); a frase de antes da janela vai pela caixa do Windows (D-868); a frase guardada que deixou de ser verdade não
  aparece (M1); o `Update.exe` que some tem frase própria (M2); dois testes novos (M5). Cada teste antigo que muda vai
  na lista da D-836 com o porquê; nenhum muda só para passar.

## Como fica para quem usa e no livro (§11.9)

**Uma versão nova que não passa no teste rápido** (o caso que importa):
- Antes (volta 4): o Kaique abria o programa, ficava uns segundos sem nada na tela (o teste), a janelinha do atualizador
  aparecia e o programa voltava sozinho para a versão anterior, com "A atualização não deu certo. O programa voltou para
  a versão anterior e continua funcionando. Avise o Samuel." na janela do programa. Se não desse para voltar, a frase
  (3) esperava a janela do programa, e quando a janela da versão estragada não abria, ele via só "Aconteceu um problema
  inesperado" (o G1).
- Depois: ele abre o programa; uns segundos sem nada (o teste); aparece uma **caixa do próprio Windows**, título
  "Atualização", com "A versão nova não funcionou. Não desinstale nada. Avise o Samuel." e o botão OK. Ele clica OK; o
  programa tenta abrir na versão nova (a que falhou). Se ela abrir, ele trabalha nela; se não abrir, ele vê a caixa de
  sempre do programa ("Um momento") e o programa fecha. Nas aberturas seguintes: nenhum teste, nenhuma caixa (ele já
  viu), o programa tenta abrir. Nada volta sozinho: o Samuel resolve (publica a correção, que é oferecida como qualquer
  versão nova se o programa abrir, ou reinstala à mão; a última boa continua guardada para ele).
- Se ele tinha fechado com "Sim" (a versão nova é testada sem janela, D-769): nada aparece na hora; na próxima vez que
  ele abrir, a mesma caixa do Windows, antes de tudo.

**Duas janelas e o "Sim" ao fechar (M1):** antes, depois de a segunda janela trocar de verdade, a abertura seguinte (já
na versão nova) dizia "Não deu para atualizar agora: havia outra janela do programa aberta. Tente ao fechar o
programa." Depois: essa frase só aparece se a versão que roda ainda é a de antes.

**O atualizador do Windows que some (M2):** antes, "Reiniciar agora" fechava a janela, reabria com "...o atualizador do
programa não começou. Tente ao fechar o programa." e fechar não perguntava nada. Depois: ao clicar "Reiniciar agora",
a janela não fecha e aparece a frase própria (a minha primeira sugestão, até o Samuel escolher; ver "Perguntas para o
Samuel"). Fechar não pergunta nada (não há como trocar). Quando o atualizador voltar, a abertura seguinte mostra o
aviso da versão nova de novo.

**Toda frase da atualização que aparece antes da janela do programa existir** (a da troca que o Windows não deixou, a
guardada do "Sim" ao fechar, a da versão reprovada, e a 2 e a do motor quando chegam antes de a janela abrir) passa a
aparecer na caixa do Windows, com o mesmo título "Atualização" e as mesmas palavras; depois do OK, o programa abre.
As que respondem a um clique ("Reiniciar agora") continuam na janela do programa, como hoje.

**No livro (PDF):** nada muda. A atualização não toca no processamento nem no PDF.

## A tabela das falhas, refeita para a volta 5 (antes de qualquer código)

A tabela da volta 4 (mais abaixo, "Volta 4 — a tabela das falhas"), com as decisões de 25/11: **a linha "Voltar" saiu
inteira** (D-867); toda casinha que mostrava a frase (1) ou a (3) mostra agora a frase da D-868, **pela caixa do
Windows**; o caminho novo do `Update.exe` que some (M2) e a frase guardada que deixou de ser verdade (M1) entraram.
**"muda na volta 5"** = em `aba7b844` o resultado é outro (dito entre parênteses). O quem tenta quebrar 5 confere esta
tabela contra o código.

**A regra das caixas (D-868), num lugar só (`Atualizacao._para_a_tela`):** uma frase da atualização que aparece
quando a janela do programa **ainda não existe** vai para a caixa do Windows (`core.windows.mostrar_caixa_do_windows`,
título "Atualização", botão OK); a abertura espera o OK e depois segue. Com a janela aberta, a frase vai para a caixa da
janela, como sempre. A frase só conta como vista depois do OK; se a caixa do Windows não pôde aparecer (nenhuma área de
trabalho à vista, ou o Windows recusou), ela fica guardada para a próxima abertura e o registro diz por quê.

As frases, palavra por palavra (título sempre "Atualização", D-846):
**(R, D-868)** "A versão nova não funcionou. Não desinstale nada. Avise o Samuel." · **(2)** "Chegou uma versão nova,
mas ela não foi instalada porque não tem a assinatura do Samuel. O programa continua funcionando. Avise o Samuel." ·
**(D-839)** "A atualização não deu certo. O programa continua na versão de antes e funcionando. Avise o Samuel." ·
**(D-840)** "Feche a outra janela do programa e clique de novo." · **(D-843)** "Esta versão precisa de um motor novo.
Avise o Samuel." · **(D-845)** "Não deu para atualizar agora: [motivo]. Tente ao fechar o programa.", com um dos nove
motivos da D-847 ou o da D-864 · **(M2)** a frase própria do atualizador que sumiu: a minha primeira sugestão até o
Samuel escolher, "Não deu para atualizar: o atualizador do programa sumiu do computador. O programa continua
funcionando. Avise o Samuel." (as três sugestões estão em "Perguntas para o Samuel").

### 1. Procurar (só ao abrir, por trás, com a janela abrindo)

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio | nada a desfazer: procurar só lê | nada | nada |
| Windows nega | não se aplica (procurar só fala com a rede; bloqueio de rede = sem internet) | — | — |
| disco cheio | não se aplica (procurar não grava; a linha do registro, se não couber, vai para o `erros.log`) | — | — |
| sem internet | registra; com pacote esperando (já em `packages\`, com a assinatura guardada quando foi conferido), confere a assinatura guardada e segue: o aviso (D-859) | sem pacote esperando: nada; com ele: o aviso "Reiniciar agora / Depois" | nada |
| clique repetido | duas aberturas procuram cada uma; as duas podem mostrar o aviso | o aviso em cada janela | nada |
| arquivo some: a assinatura guardada do pacote esperando | sem internet, o pacote esperando não é oferecido | nada | nada |
| arquivo some: o `Update.exe` (antivírus) | o Velopack nem começa (`locator.rs` 114-117: "Update.exe does not exist"): procurar e "pacote esperando" falham; tratado como sem internet, só o registro. **Quando ele volta**, a abertura seguinte procura de novo e o aviso aparece (o pacote já baixado é reaproveitado: `manager.rs` 413-416). **muda na volta 5** (M2; hoje igual, mas nada conferido) | nada; quando ele volta, o aviso da versão nova | nada |
| sem licença | não procura: a pergunta do Windows vem antes da janela (D-806) | a pergunta do Windows | nada |

### 2. Baixar (por trás)

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio | o Velopack deixa `<nome>.partial`; a próxima abertura baixa de novo e ele o apaga (`manager.rs` 419-481) | nada | o `.partial` até a próxima |
| Windows nega (o antivírus prende o arquivo) | o download falha; registra; a próxima abertura tenta (D-866 (d): para depois) | nada | o `.partial`, às vezes |
| disco cheio | o download falha; registra; a próxima abertura tenta (D-866 (d)) | nada | o `.partial`, às vezes |
| sem internet (cai no meio) | igual ao "desliga" | nada | o `.partial` |
| clique repetido | a segunda janela não pega a tranca do Velopack (`manager.rs` 406); registra | o aviso na que baixou | nada a mais |
| arquivo some (o pacote tirado logo depois) | a leitura do motor que ele pede falha: não é anunciado; registra | nada; a próxima abertura baixa de novo | nada |
| sem licença | não se aplica (sem licença nada é procurado) | — | — |

### 3. Conferir (a assinatura do Samuel antes de baixar; o motor da versão nova depois)

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio | nada a desfazer | nada | às vezes a assinatura que chega (dado, D-852) |
| Windows nega / disco cheio (a assinatura não fica guardada) | segue; sem internet, depois, o pacote esperando e a guarda não acham a assinatura (registro) | nada | nada |
| sem internet (cai entre procurar e conferir) | "a rede não respondeu" não é "recusada": só o registro; a próxima abertura tenta | nada | nada |
| assinatura que não existe (o GitHub responde 404) ou errada | não baixa; não vai para "não tentar"; a próxima abertura confere de novo | a frase (2), uma vez; **se a janela ainda não abriu, pela caixa do Windows** e a janela abre depois do OK. **muda na volta 5** (D-868; hoje esperava a janela) | nada |
| motor novo que não está no lugar | não anuncia nem troca (D-843) | a frase do motor, uma vez; antes da janela, pela caixa do Windows. **muda na volta 5** | o pacote em `packages\` |
| clique repetido | não se aplica | — | — |
| arquivo some | ver "Baixar, arquivo some" | — | — |
| sem licença | não se aplica | — | — |

### 4. "Reiniciar agora" (a conferência por trás, o fechar, o pedido da troca)

Toda frase desta linha responde ao clique, com a janela aberta: vai para a caixa da janela (D-846), como hoje. A única
exceção é a do programa reaberto (a janela de antes já fechou): ela aparece antes da janela nova, pela caixa do Windows.

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio | antes do pedido nada mudou; a próxima abertura mostra o aviso de novo | o aviso de novo | o pacote esperando |
| Windows nega (a lista de processos) | não troca; a pergunta vem ao fechar | "Não deu para atualizar agora: o Windows não mostrou quais programas estão abertos. Tente ao fechar o programa." | nada |
| arquivo some: o `Update.exe` (antes do clique) | **a conferência única da troca passa a olhar o `Update.exe`** (`<raiz>\Update.exe`, o que a biblioteca exige: `locator.rs` 114-117) e não fecha a janela; nada é pedido; fechar NÃO pergunta (não há como trocar). Quando ele voltar, a abertura seguinte mostra o aviso de novo. **muda na volta 5** (M2; hoje: a janela fechava por nada, reabria com "...o atualizador do programa não começou. Tente ao fechar o programa." e fechar não perguntava nada) | a frase própria (M2), na janela, e a janela continua aberta; ao fechar, nada; depois de ele voltar, o aviso da versão nova | nada |
| Windows nega (o atualizador do Velopack não começa, depois de a janela fechar) | o programa é aberto de novo; se o `Update.exe` está lá, a frase da D-845; se ele sumiu nesses segundos, a frase própria (conferido de novo no disco, não pelo texto do erro). **muda na volta 5** (M2; a frase do programa reaberto vem antes da janela dele: pela caixa do Windows, D-868) | o programa reabre: antes da janela, a caixa do Windows com "Não deu para atualizar agora: o atualizador do programa não começou. Tente ao fechar o programa." (ou a frase própria); depois do OK, a janela; com o `Update.exe` lá, o aviso de novo | a frase no bilhete, até ser vista |
| disco cheio | não se aplica ao clique | — | — |
| sem internet | não se aplica (tudo é local) | — | — |
| clique repetido (outra janela aberta) | não troca, e o aviso volta (D-840, D-841) | "Feche a outra janela do programa e clique de novo." e o aviso de novo | nada |
| arquivo some (o pacote sumiu) | não troca (antes de fechar); ou, nos segundos do fechar, reabre | "Não deu para atualizar agora: o arquivo da versão nova sumiu do computador. Tente ao fechar o programa." (no programa reaberto, pela caixa do Windows antes da janela) | nada |
| pacote trocado (a soma não é a assinada) | não troca (D-848) | a frase (2) | nada |
| sem licença | não se aplica (sem licença não há aviso) | — | — |

### 5. "Sim" ao fechar ("Atualizar agora?" → "Sim")

O programa já fechou: toda frase desta linha é guardada no bilhete e aparece **na abertura seguinte, antes da janela,
pela caixa do Windows** (D-868). **muda na volta 5** (hoje: esperava a janela).

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio | o programa já gravou e saiu; ver "Trocar" | — | — |
| Windows nega (a lista; o atualizador não começa) | não troca e guarda a frase com o motivo (D-858) | na abertura seguinte, a caixa do Windows: "Não deu para atualizar agora: [o motivo]. Tente ao fechar o programa." | a frase no bilhete |
| arquivo some: o `Update.exe` | não troca e guarda a frase própria. **muda na volta 5** (M2; hoje: "...o atualizador do programa não começou. Tente ao fechar...", que prometia o que não vinha) | na abertura seguinte, a caixa do Windows com a frase própria; fechar não pergunta (sem o `Update.exe` não há pacote esperando que o Velopack leia); quando ele voltar, o aviso | a frase no bilhete |
| disco cheio | não se aplica (nada é gravado pelo atualizador além da frase) | — | — |
| sem internet | não se aplica (local) | — | — |
| clique repetido (outra janela aberta) | não troca (o Velopack fecharia a outra à força) e guarda a frase da D-864. **Se depois a troca acontecer** (o "Sim" da segunda janela), a abertura seguinte já roda a versão nova e **a frase guardada não aparece** (ela fala de uma troca que não aconteceu, e a versão que roda mostra que aconteceu). **muda na volta 5** (M1; hoje: aparecia já na versão nova) | sem a segunda troca: a caixa do Windows com "Não deu para atualizar agora: havia outra janela do programa aberta. Tente ao fechar o programa."; com ela: nada | a frase no bilhete (fica lá, sem aparecer) |
| arquivo some (o pacote; o motor) | não troca, guarda a frase | na abertura seguinte, a caixa do Windows: "...o arquivo da versão nova sumiu do computador..." / "...falta no computador uma peça que a versão nova precisa..." | a frase no bilhete |
| pacote trocado | não troca, guarda a frase (2) | na abertura seguinte, a caixa do Windows com a frase (2) | a frase no bilhete |
| sem licença | não se aplica | — | — |

### 6. Trocar (o atualizador do Velopack, depois que o programa saiu)

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga antes de trocar o nome de `current` | nada mudou; a próxima abertura roda a versão de antes e mostra o aviso (com ou sem internet, D-859) | o aviso de novo | o pacote esperando |
| desliga entre as duas trocas de nome | o defeito do Velopack (`apply_windows_impl.rs` 174-176): o atalho não abre; reinstalar resolve (D-865: para depois) | o atalho não abre o programa | `current` faltando |
| desliga depois de trocar, antes de reabrir | a próxima abertura roda a nova, sem a marca de aprovada: o teste antes da janela | segundos sem nada, e o programa (ou a caixa da linha 7) | — |
| Windows nega (arquivo preso) | o Velopack tenta 10 vezes, desiste e reabre a de antes com o pedido (`apply.rs` 47-75); ela mostra a frase da D-839; o aviso volta. **A cada recusa** (D-877, segunda rodada): o nome da frase leva o momento da abertura reaberta, então uma segunda recusa para a mesma versão avisa de novo; a abertura seguinte pelo atalho (sem o pedido) não mostra nada | a caixa do Windows com a frase da D-839, antes da janela, **uma vez por recusa**; depois do OK, a janela e o aviso. **muda na volta 5** (D-868; hoje esperava a janela; D-877: a segunda recusa da mesma versão não dizia nada). No "Sim" ao fechar: na abertura seguinte (o nome já levava a hora) | o pacote esperando |
| disco cheio (o Velopack não abre o pacote) | igual ao "Windows nega" (lido, não rodado) | igual | o pacote esperando |
| sem internet | não se aplica | — | — |
| clique repetido (o atalho durante a troca) | a abertura vê o atualizador do Velopack rodando e sai sem janela (G1 da volta 2) | nada: o clique se perde | nada |
| arquivo some (o pacote, depois do pedido) | o Velopack não acha e reabre a de antes com o pedido | a caixa do Windows com a frase da D-839, e a janela | — |
| sem licença | não se aplica | — | — |

### 7. Testar (o teste rápido, antes da janela)

Roda só na versão que não é a última boa, não tem a marca de aprovada, **não foi reprovada antes** e não é a primeira
do .msi. **muda na volta 5** (a marca de "sem volta" saiu; "reprovada" passa a ser o que diz "não teste de novo": é o
mesmo fato que o bilhete já guarda).

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| passou | a marca de aprovada; a guarda; nenhuma abertura seguinte testa (D-856) | nada (a janela abre) | `aprovada-<versão>` |
| **não passou** (falta uma peça; a janela da versão nem abre) | **reprovada no bilhete; a frase guardada; a caixa do Windows com a frase da D-868, palavra por palavra; depois do OK, o programa tenta abrir assim mesmo.** A atualização para nesta abertura (D-857 "e para"; D-867 "nada é pedido ao Velopack"): nada é procurado, nada volta. (Corrigido depois do commit da tabela: eu tinha escrito "o motor e a procura seguem"; ver "Como cumpri".) **muda na volta 5** (D-867, D-868; hoje: a volta pela última boa, ou a frase (3) presa na fila da janela: o G1) | a caixa do Windows "A versão nova não funcionou. Não desinstale nada. Avise o Samuel."; depois do OK, a janela da versão nova, ou, se ela não abre, a caixa de sempre do programa ("Um momento") e o programa fecha | a reprovação no bilhete; o "visto" da caixa na pasta da conta |
| não passou, depois do "Sim" ao fechar (reaberto sem janela) | reprovada; a frase guardada no bilhete; sai (nada abre na tela, D-769) | nada na hora; na próxima abertura, a caixa do Windows com a frase da D-868, antes de tudo | a reprovação e a frase |
| a abertura seguinte à reprovação | não testa (reprovada), não mostra a caixa (já vista), tenta abrir; a procura volta: a correção publicada é oferecida se a janela abrir | nada além do que a versão faz ao abrir | — |
| a caixa não pode aparecer (nenhuma área de trabalho à vista: o programa aberto por uma conexão de longe; ou o Windows recusou) | não chama a caixa quando não há área de trabalho à vista (o Windows a criaria numa tela que ninguém vê, e a abertura ficaria parada esperando um OK que nunca vem); registra; a frase fica guardada para a próxima abertura e não conta como vista. **muda na volta 5** | nada agora; na próxima abertura com a tela à vista, a caixa | a frase no bilhete |
| desliga no meio | nada anotado; a próxima abertura testa de novo | segundos sem nada na tela, de novo na próxima | nada |
| desliga com a caixa na tela (antes do OK) | a reprovação e a frase já estão no bilhete (a frase é guardada ANTES de a caixa aparecer); ela não conta como vista | na próxima abertura: sem teste, a caixa de novo | a reprovação e a frase |
| Windows nega (o antivírus não deixa o teste rodar) | conta como "não passou" | como "não passou" | a reprovação |
| disco cheio | a reprovação, se não couber, não fica: a próxima abertura testa de novo (segundos); a caixa não se repete se o "visto" gravou | segundos sem nada a cada abertura, só enquanto o disco estiver cheio | nada |
| sem internet | não se aplica (local) | — | — |
| clique repetido (dois cliques nos segundos do teste) | D-861, para depois: as duas aberturas testam; cada uma reprova e pode mostrar a caixa | às vezes duas caixas iguais (sem laço) | a reprovação |
| sem licença | não se aplica: a pergunta do Windows vem antes do teste | a pergunta do Windows | — |

### 8. Guardar a última boa (logo depois de passar no teste; copiada de `packages\`, sem internet)

Nada automático depende dela para voltar (D-869): é para a volta à mão do Samuel. **muda na volta 5:** ninguém mais
a usa para voltar. A abertura continua listando os nomes da pasta para saber se a versão que roda é a última boa (a
regra de quem é testado, D-856/D-857, sem mudança); tirar essa leitura mudaria a regra e testes antigos que não são da
volta, e eu não fiz: está em "Perguntas para a gerente".

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio da cópia | a anterior vale; a marca de aprovada já está lá: nada se repete (D-856) | nada | o `<nome>.chegando` até a próxima guarda (leve 4 do quarto, não mexido) |
| Windows nega (arquivo preso) | não guarda; a anterior vale; nada se repete | nada | nada |
| disco cheio | confere o espaço antes (`espaco_livre_basta`) e não copia | nada | nada |
| sem internet | não importa: copia de `packages\`; a assinatura é a guardada | nada | nada |
| clique repetido | o pacote final fica certo (D-866 (a)) | nada | a última boa certa |
| arquivo some (o pacote não está em `packages\`) | não guarda e não baixa (D-857) | nada | nada |
| o nome final preso com um arquivo velho | a assinatura só no fim (a regra do leve 1); nada é dado como guardado | nada | nada |
| primeira versão instalada | não há o que guardar (D-857) | nada | nada |
| sem licença | não se aplica | — | — |

### 9. Voltar

**Saiu (D-867).** Nenhum caminho do programa pede a volta: a versão reprovada fica, com a caixa da D-868.

### Os achados do quarto "quem tenta quebrar", casinha por casinha

| Achado | Onde cai | O que acontece com ele |
|---|---|---|
| G1 a frase (3) presa na fila da janela que não abre; a marca de "sem volta" antes da frase | Testar × não passou | **vira a caixa do Windows** (D-868): a frase não espera a janela; a marca de "sem volta" saiu |
| M1 a frase "outra janela" depois da troca certa | "Sim" ao fechar × clique repetido | **consertado**: a frase guardada sobre uma troca só aparece se a versão que roda ainda é mais velha que a da frase |
| M2 o `Update.exe` que some | "Reiniciar agora" e "Sim" ao fechar × `Update.exe`; Procurar × `Update.exe` | **consertado**: a conferência única olha o `Update.exe`; frase própria; nada de "tente ao fechar"; o aviso volta quando ele volta |
| M3 a volta que não pôde ser pedida vira "sem volta" para sempre | (era Voltar) | **saiu com a volta** |
| M4 a volta depois do "Sim" tenta duas vezes | (era Voltar) | **saiu com a volta** |
| M5 duas proteções sem teste (X11, X18) | Conferir × 404; Procurar × sem internet com pacote esperando | **dois testes**, cada um falhando com a proteção desligada |
| M6 a marca de "sem volta" que não grava | (era Voltar) | **saiu com a volta** |

## A leitura antes de usar a peça de fora: a caixa do Windows (`MessageBoxW`) (§11.12, item 6)

Lido em 25/11/2026 na documentação da Microsoft (as frases entre aspas são de lá, traduzidas por mim):
- [MessageBoxW](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxw)
- [About Dialog Boxes](https://learn.microsoft.com/en-us/windows/win32/dlgbox/about-dialog-boxes) (seções "Message
  Boxes", "Modal Dialog Boxes", "Dialog Box Owner Window")
- [Interactive Services](https://learn.microsoft.com/en-us/windows/win32/services/interactive-services) e
  [USEROBJECTFLAGS](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-userobjectflags)
- [SetForegroundWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow)
  (o que o `MB_SETFOREGROUND` chama por dentro)

| Caso que usamos | O que a peça de fora faz | Fonte | O que o nosso código faz |
|---|---|---|---|
| deu certo | devolve o número do botão clicado; com só o OK (`MB_OK`, 0x0), devolve `IDOK` (1). "Se há um botão OK e a pessoa aperta ESC, a volta é IDOK" | MessageBoxW, "Return value" | só `IDOK` conta como "a pessoa viu" (`DEU_CERTO`); então a frase é marcada vista |
| falhou | "Se a função falha, a volta é zero. Para o erro, chame GetLastError" | MessageBoxW, "Return value" | zero vira `FALHOU` com o número do erro (lido por `_ler_erro`, `use_last_error=True`, como toda a peça); a frase NÃO conta como vista e fica guardada para a próxima abertura |
| sem janela dona (`hWnd` nulo) | "a caixa não tem janela dona"; com `MB_APPLMODAL` (o padrão) e sem dona, nada é desativado ("quando uma caixa modal não tem dona, o sistema não desativa nenhuma outra janela do programa") | MessageBoxW, "hWnd"; About Dialog Boxes, "Owner Window" | sempre sem dona: a caixa só aparece quando a janela do programa ainda não existe |
| aparece em cima? | `MB_TOPMOST` (0x40000): "criada com o estilo WS_EX_TOPMOST" (fica acima das janelas que não são "sempre em cima"); `MB_SETFOREGROUND` (0x10000): "o sistema chama SetForegroundWindow para a caixa"; mas "o sistema restringe quais processos podem tomar a frente" e, se não pode, "o Windows pisca o botão na barra de tarefas" | MessageBoxW, "uType"; SetForegroundWindow, "Remarks" | usamos `MB_OK | MB_ICONINFORMATION | MB_SETFOREGROUND | MB_TOPMOST`. O programa aberto pelo clique no atalho é "o processo que recebeu a última entrada" ou foi "aberto pelo processo da frente", então costuma poder tomar a frente; se não puder, a caixa fica em cima (TOPMOST) e o botão pisca. Ícone "i", o mesmo das caixas da janela (`QMessageBox.Information`) |
| trava a linha? | "Uma caixa de mensagem é uma caixa de diálogo modal"; "o sistema não devolve o controle da função que cria a caixa até [ela ser fechada]"; para isso "o sistema começa o próprio laço de mensagens" | About Dialog Boxes, "Message Boxes" e "Modal Dialog Boxes" | trava só a linha que chama, até o OK. Na abertura (antes do Qt existir) é o que a D-868 pede: a caixa, o OK, e então o programa tenta abrir. Se a frase vem pela linha de trás (a procura que termina antes de a janela abrir), só essa linha espera; a janela abre normalmente e a caixa fica em cima dela |
| sessão sem área de trabalho à vista | os serviços e os processos sem área de trabalho interativa usam uma "estação de janelas não interativa" e "não podem interagir com a pessoa"; o jeito de saber é "GetProcessWindowStation [...] e GetUserObjectInformation para ver se a estação tem o atributo WSF_VISIBLE" ("a estação tem superfícies de tela visíveis") | Interactive Services; USEROBJECTFLAGS | **antes de chamar a caixa**, a peça confere a estação do processo (`GetProcessWindowStation` + `GetUserObjectInformationW(UOI_FLAGS)`): sem `WSF_VISIBLE`, NÃO chama (uma caixa ali ninguém vê, e a abertura ficaria esperando um OK que nunca vem); devolve `FALHOU` ("nenhuma área de trabalho à vista"), e a frase fica guardada. Se nem der para ler a estação, também não chama (`FALHOU`) |
| o `MB_SERVICE_NOTIFICATION` | mostra na área de trabalho ativa "mesmo sem ninguém logado", e "pode pôr conteúdo numa tela bloqueada" | MessageBoxW, "uType" | NÃO usamos: o programa do Kaique não é serviço; a caixa é da sessão dele |
| a tela está bloqueada, ou a pessoa está noutra área de trabalho | a caixa é criada na área de trabalho da linha que chama; o `MB_DEFAULT_DESKTOP_ONLY` faz esperar "até a pessoa voltar à área de trabalho padrão" (não usamos) | MessageBoxW, "uType" | a caixa espera na área de trabalho do Kaique até ele voltar e clicar OK (é a área de trabalho dele: nada se perde) |
| o texto | "se o texto tem mais de uma linha, separe com CR e/ou LF"; título nulo vira "Error" | MessageBoxW, "lpText", "lpCaption" | sempre título "Atualização" (D-846) e a frase numa linha; a função é a versão Unicode (`W`), com acento |

**Onde mora:** `core/windows.py`, `mostrar_caixa_do_windows(titulo, texto) -> Resposta` (com `area_de_trabalho_a_vista()`,
a conferência da estação). Ninguém mais chama `MessageBoxW` (a busca no fim desta seção prova). O executor da
atualização a chama por um lugar só, `Atualizacao._para_a_tela`.

**As frases do atualizador que podem aparecer antes de a janela do programa existir** (todas passam por esse lugar):
1. a da versão reprovada no teste rápido (D-868), na abertura que testou;
2. a da troca que o Windows não deixou (D-839), na versão de antes reaberta pelo Velopack;
3. a frase guardada no bilhete, na abertura seguinte: a da D-845 com qualquer dos motivos (o "Sim" ao fechar que não
   trocou, D-858/D-864; o programa reaberto depois do "Reiniciar agora" que não pôde pedir a troca); a (2) do "Sim" ao
   fechar com o pacote trocado (D-848); a da D-839 e a da D-868 guardadas pela reabertura sem janela do "Sim" ao
   fechar; a frase própria do `Update.exe` que sumiu (M2);
4. a (2) da assinatura recusada e a do motor (D-843), quando a procura e o download (por trás) terminam antes de a
   janela abrir (uma corrida: depende de quanto a janela demora).
Nunca antes da janela: as respostas a um clique ("Reiniciar agora": D-840, D-845, a 2, a frase própria do M2), que
continuam na caixa da janela.

## Perguntas para o Samuel (§11.13; a gerente leva à Central)

**RESPONDIDA em 25/11/2026 (recado da gerente, palavras dele coladas do recado do Fable): "Fica a A."** A frase que já
estava construída fica: "Não deu para atualizar: o atualizador do programa sumiu do computador. O programa continua
funcionando. Avise o Samuel." (`atualizacao.FRASE_SEM_ATUALIZADOR`; o comentário dela passou a dizer que é a escolha
dele). O texto da pergunta, como foi entregue:

**1. A frase de quando o atualizador do programa some do computador.**

Do que se trata: é a caixa "Atualização" que aparece quando o Kaique clica **"Reiniciar agora"** no aviso da versão
nova (ou responde **"Sim"** ao fechar o programa) e o programa que faz a troca de versão (um arquivo do próprio
programa, que um antivírus às vezes põe de lado) não está mais no computador.

O que acontece hoje (antes desta volta): a janela fechava, reabria e dizia "Não deu para atualizar agora: o atualizador
do programa não começou. Tente ao fechar o programa." Só que, ao fechar, nada era perguntado: a frase prometia o que
não acontecia. Isso é **defeito do programa** (achado pelo agente que tenta quebrar, testado de verdade).

O que muda (o senhor já decidiu em 25/11: "frase própria, sem 'tente ao fechar', e oferecer de novo quando voltar"):
a janela não fecha, aparece a frase própria, fechar não pergunta nada, e quando o arquivo voltar (o antivírus devolver,
ou o senhor reinstalar), a próxima vez que o Kaique abrir o programa o aviso da versão nova aparece de novo. Ele
continua trabalhando normalmente o tempo todo. Nada do que já funciona muda.

Onde aparece: só nesses dois cliques. No "Reiniciar agora", na hora, na caixa da janela; no "Sim" ao fechar, na
próxima vez que ele abrir o programa, numa caixa do Windows antes da janela.

**O que o senhor escolhe: as palavras da frase.** O programa já está montado com a A, que se troca num lugar só.
- **A (sugestão):** "Não deu para atualizar: o atualizador do programa sumiu do computador. O programa continua
  funcionando. Avise o Samuel." Diz o que houve e o que fazer; o Kaique só avisa.
- **B:** "A versão nova não pode ser instalada agora porque falta o atualizador do programa no computador. O programa
  continua funcionando. Avise o Samuel." Mais longa; fala da versão nova primeiro.
- **C:** "Não deu para atualizar: falta no computador o atualizador do programa. Quando ele voltar, a versão nova
  aparece de novo. Avise o Samuel." Diz também o que vai acontecer depois; não diz que o programa continua funcionando.
- Só comentário também vale.

De onde veio: pedido seu de 25/11 (a frase própria); as palavras são sugestão do agente. Situação: construída com a A,
na versão de teste, esperando a sua escolha.

## Como cumpri cada decisão (com o teste ou a prova)

| Decisão (palavras dele) | O que fiz | Prova |
|---|---|---|
| D-867 "Tirar a volta automática: a marca "sem volta", o "uma vez só", a segunda tentativa, o `--voltando`, a fase de volta. A tabela perde a linha "Voltar"." | Saíram: `ARG_VOLTANDO` e a leitura dele na abertura; a fase `VOLTANDO`; o evento `VoltaPedida`; os efeitos `Voltar` e `MarcarSemVolta`; a marca `.sem-volta` (`MARCA_SEM_VOLTA`, e o nome dela em `_versao_do_nome`); `Atualizacao._voltar`; `_volta_que_nao_deu`; `trocar_para(volta=...)`; `Abriu.sem_volta`, `Abriu.reaberto_voltando`; `Estado.anterior` ("para onde a volta vai"); as frases (1) e (3) (`FRASE_DA_FALHA`, `FRASE_DA_FALHA_SEM_VOLTA`, `FALHA_TESTE`, `FALHA_VOLTA`, a frase (1) derivada); o `permitir_voltar` da peça do Velopack (ele só era lido pelo `check_for_updates`, `manager.rs` 294). A tabela perdeu a linha "Voltar" (commit `590eef24`) | `test_decisoes_atualizacao_volta5::test_d867_nada_da_volta_automatica_sobrou_no_programa` e `::test_d867_a_reprovada_nao_pede_nada_ao_velopack`; a busca abaixo ("O que saiu") |
| D-868 "Se reprovar: versão vai para "reprovadas" e a frase aparece pela caixa do Windows, pela peça (`MessageBoxW`), nunca pela janela do programa [...] Depois o programa tenta abrir assim mesmo. Toda frase que pode aparecer antes da janela existir usa esse caminho." | A caixa é a peça `core.windows.mostrar_caixa_do_windows` (só ela chama `MessageBoxW`). O lugar único que escolhe ONDE uma frase aparece é `Atualizacao._para_a_tela`: sem a janela ainda, toda frase vai para a caixa do Windows na hora; com a janela, para a janela. A reprovação vem antes da caixa; depois do OK a abertura devolve None e o `main.py` abre o programa | de verdade: `volta5-provas/prova_caixa_de_verdade-resultado.txt` e os prints `A-primeira-caixa-1.png`, `B-primeira-caixa-1.png`, `C-seguinte-caixa-1.png`; testes: `test_d868_*` (8 casos) em `test_decisoes_atualizacao_volta5.py` |
| D-869 "A última boa continua sendo guardada (de `packages\`, sem internet), mas nada automático depende dela" | A guarda (`guardar_ultima_boa`, a marca de aprovada, o espaço) não mudou; nenhum caminho pede volta nem lê o pacote guardado. A abertura ainda lista os NOMES da pasta para saber se a versão que roda é a última boa (regra de quem é testado, D-856/D-857, sem mudança): ver "Perguntas para a gerente" | `test_d869_a_ultima_boa_continua_guardada_e_a_reprovada_nao_mexe_nela`; os testes da guarda de antes passam sem mudança |
| D-870 M1 "frase 'outra janela' depois da troca certa" | `fases._frase_guardada_vale` (lugar único): a frase guardada sobre uma troca para a versão X só aparece enquanto a que roda é mais velha que X | `test_d870_m1_*`; `test_atualizador_volta5::test_m1_*` (8 casos); a tabela da regra (`abriu_frase_guardada_velha`) |
| D-870 M2 "`Update.exe` que some: frase própria, sem 'tente ao fechar', e oferecer de novo quando voltar" | `tem_o_atualizador` (lugar único) na conferência única da troca e no pedido da troca; a frase própria (`FRASE_SEM_ATUALIZADOR`, a minha sugestão A até o Samuel escolher) pela escolha única do texto (`frase_da_falha`); no "Reiniciar agora", PARADO (fechar não pergunta) | de verdade, com a biblioteca do Velopack: `volta5-provas/prova_update_exe_volta-resultado.txt` (passos 2 a 7: a frase própria, nada ao fechar, nada enquanto ele falta, e o aviso de novo quando ele volta); testes `test_d870_m2_*` (5) |
| D-870 M5 "os dois testes" | X11: o 404 do GitHub; X18: a assinatura guardada do pacote esperando | `test_d870_m5_x11_*`, `test_d870_m5_x18_*` (2); mutações V15 e V16 acusadas |
| D-871 "Os testes da volta automática saem com ela [...] com a prova de que o programa avisa quando a versão nova falha" | Os testes da volta saíram pela lista da D-836 (seção "Volta 5", nos três formatos); a prova do aviso é a D-868 | `test_d871_nenhum_teste_pede_a_volta_e_o_aviso_e_a_prova`; `lista-dos-testes-d836.md/.html/.pdf` |
| As que continuam (§11.8): D-778 (2), D-839, D-845/D-858/D-864 e os nove motivos, D-846, D-854, D-856, D-857, D-859, D-840/D-841, D-848/D-849, o bilhete, a peça do Velopack, a K03 | Nenhuma mudou de palavra nem de comportamento; só o lugar das frases de antes da janela (D-868). A D-857 "e para" continua: a reprovada não procura nem pede nada nesta abertura | os testes antigos delas passam (`volta5-testes-no-codigo-antigo.txt`, parte 2, e a rodada de agora); `test_d839_d867_*`, `test_d857_d868_*` |

**Uma correção na tabela das falhas, depois do commit dela:** na casinha "Testar × não passou" eu tinha escrito "o motor
e a procura seguem". Ao escrever os testes, li de novo a D-857 ("aparece a frase [...] e para") e a prova da D-867 no
Livro ("versão reprovada → nada é pedido ao Velopack"): a atualização PARA nesta abertura (o programa abre); a procura
volta nas aberturas seguintes. O código e a tabela acima seguem isso. Também acrescentei a guarda da frase ANTES de a
caixa aparecer (a casinha "desliga com a caixa na tela" prometia a caixa de novo na abertura seguinte, e o primeiro
código não cumpria: a versão reprovada não é testada de novo, então nada a traria de volta).

## O que saiu (D-867), e a busca que prova

Saiu: `ARG_VOLTANDO`, `MARCA_SEM_VOLTA`, `MarcarSemVolta`, `Voltar`, `VoltaPedida`, `Fase.VOLTANDO`, `_voltar`,
`_volta_que_nao_deu`, `Abriu.sem_volta`, `Abriu.reaberto_voltando`, `Estado.anterior`, `trocar_para(volta=)`,
`FRASE_DA_FALHA` (1), `FRASE_DA_FALHA_SEM_VOLTA` (3), `FALHA_TESTE`, `FALHA_VOLTA`, a frase (1) derivada, `permitir_voltar`.
Ficou de propósito: `pacote_da_versao` da peça do Velopack (o pacote esperando, D-859, também o usa) e
`ler_ultima_boa` (a regra de quem é testado).

A busca (25/11, em todos os `.py` do programa, fora de `tests/`, `relatorios/`, `.claude/`, `docs/`, `memoria/`,
`regras_dos_agentes/`):
`git ls-files '*.py' | grep -v -E "^(tests|relatorios|\.claude|docs|memoria|regras_dos_agentes|terceiros|velhos)/" | xargs grep -n -E "\-\-voltando|ARG_VOLTANDO|sem-volta|MARCA_SEM_VOLTA|MarcarSemVolta|VoltaPedida|Fase\.VOLTANDO|VOLTANDO =|_volta_que_nao_deu|def _voltar|reaberto_voltando|sem_volta|FALHA_VOLTA|FALHA_TESTE|FRASE_DA_FALHA_SEM_VOLTA|FRASE_DA_FALHA\b|permitir_voltar|não conseguiu voltar sozinho|voltou para a versão anterior e continua"`
achou só `core/filtros.py:2505 def _voltar(pequeno...)` e quatro `_voltar_*` da tela (`ui/tela_conferir.py`,
`ui/tela_inicio.py`), que não têm nada com a atualização. O teste `test_d867_nada_da_volta_automatica_sobrou_no_programa`
faz a mesma busca pela árvore do código.

## Os achados do quarto "quem tenta quebrar"

| Achado | O que aconteceu |
|---|---|
| G1 (a frase (3) presa na fila da janela que não abre) | **Virou a caixa do Windows** (D-868). Executado de verdade: caso A da `prova_caixa_de_verdade` (a janela da versão não abre: a caixa aparece e é vista ANTES do `main.main()`; depois vem a caixa de sempre "Um momento" e o programa fecha) |
| M1 | **Consertado** (`_frase_guardada_vale`) |
| M2 | **Consertado** (`tem_o_atualizador`, a frase própria, PARADO); executado com o Velopack de verdade |
| M3 (a volta que não pôde ser pedida vira "sem volta") | **Saiu com a volta** (não há volta nem marca) |
| M4 (a volta depois do "Sim" tenta duas vezes) | **Saiu com a volta** |
| M5 (X11, X18 sem teste) | **Dois testes** (três casos); mutações acusadas |
| M6 (a marca de "sem volta" que não grava) | **Saiu com a volta** |

Os leves. Palavras do Samuel (25/11/2026, pela gerente): "Conserta as três frases do registro agora; os outros
pequenos ficam para depois. As frases do aviso de versão nova ficam como estão. Anotar: `configuracoes.espaco_livre_mb`
é código morto — apagar depois da entrega, e rodar um caça-código-morto no programa inteiro na arrumação."
1. o registro "o teste roda de novo na próxima abertura" na guarda que falha: **consertado** (só o texto): agora "a
   última boa de antes continua, e a versão não é testada de novo (já está aprovada)" (`fases.proxima_fase`,
   `UltimaBoaGuardada`). Teste `test_atualizador_volta5::test_leve1_*` (falha em `aba7b844`); mutação V21;
2. "versão ... publicada e assinada pelo Samuel: baixando" para o pacote esperando: **consertado** (só o texto): com o
   pacote da versão já no computador, o registro diz "a versão X tem a assinatura do Samuel e o pacote dela já está no
   computador: nada a baixar"; a versão achada na publicação e ainda não baixada continua com a frase de sempre.
   Teste `test_atualizador_volta5::test_leve2_*` (falha em `aba7b844`); mutação V22. Nenhum teste antigo cobrava as
   frases antigas do registro: nenhum teste mudou por isso;
3. o texto velho da tabela ("o nome final é tirado do caminho"): **conferido**: a casinha "Guardar × o nome final preso"
   da tabela da volta 5 diz "a assinatura só no fim (a regra do leve 1); nada é dado como guardado", que é o que
   `guardar_ultima_boa` faz (o pacote conferido vai para o nome final e só então a assinatura é gravada, por último);
4. o `.chegando` que sobra depois da guarda morta: **ficou** (para depois);
5. `configuracoes.espaco_livre_mb`: **ficou**; é código morto e será apagado depois da entrega (congelamento da D-765),
   com um caça-código-morto no programa inteiro na arrumação;
6. o título e as duas primeiras frases do aviso da versão nova: **ficam como estão** (palavra dele).

## Caminho → função (§11.12)

| Caminho | A função que ele usa |
|---|---|
| a frase da versão reprovada, na abertura que testou | `fases.proxima_fase(TesteRapido)` → `MostrarFalha(reprovada)` → `Atualizacao._para_a_tela` → `_na_caixa_do_windows` → `_caixa_do_windows` → `core.windows.mostrar_caixa_do_windows` (`area_de_trabalho_a_vista`, `MessageBoxW`) |
| a frase da D-839 (o Velopack reabriu a de antes) | `fases._frases_ao_abrir` → `MostrarFalha` → `_para_a_tela` → (sem janela ainda) a caixa do Windows |
| a frase guardada no bilhete (qualquer tipo) | `ler_estado` → `frase_do_bilhete` → `Abriu.frase_guardada` → `fases._frases_ao_abrir` → `_frase_guardada_vale` → `MostrarFalha` → `_para_a_tela` → a caixa do Windows |
| a (2) e a do motor, quando a procura e o download terminam antes de a janela abrir | `proxima_fase(Assinatura/Baixou)` → `MostrarFalha` → `_para_a_tela` → a caixa do Windows |
| as mesmas, depois de a janela abrir; as respostas aos cliques (D-840, D-845, a 2, o M2) | `_para_a_tela` → `ui.aviso_de_atualizacao.PonteDaTela` (a caixa da janela) |
| o texto de TODA frase (nas duas caixas) | `atualizacao.frase_da_falha` (o título `TITULO_DA_FALHA`) |
| a frase sem janela nenhuma (a reabertura do "Sim" ao fechar) | `fases._frase` → `GuardarFrase` → `guardar_frase` → `guardar_frase_pelo_nome` → `mudar_o_bilhete` |
| a frase que vai para a caixa do Windows (guardada antes; vista só depois do OK) | `_na_caixa_do_windows` → `guardar_frase_pelo_nome` → `mudar_o_bilhete`; o OK → `gravar_visto` |
| a versão precisa do teste? | `fases.precisa_do_teste` (pela abertura, `_precisa_do_teste`) |
| a reprovação | `Reprovar` → `atualizacao.reprovar` (a única) |
| o `Update.exe` no lugar? | `atualizacao.tem_o_atualizador` ← `conferencia_da_troca` (antes de fechar) e `trocar_para` (o pedido que falhou) |
| a troca ("Reiniciar agora", "Sim" ao fechar) | `trocar_para` → `conferencia_da_troca` → `conversa_com_o_velopack.trocar` (a volta não passa mais aqui: saiu) |
| a guarda da última boa | sem mudança: `GuardarUltimaBoa` → `guardar_ultima_boa` |

A prova de que os caminhos dão o mesmo resultado: `test_d868_toda_frase_de_antes_da_janela_vai_pela_caixa_do_windows`
(os quatro caminhos de antes da janela, cada um com as palavras de sempre, na caixa do Windows, e a janela não recebe
de novo), `test_d868_com_a_janela_aberta_a_frase_vai_para_a_janela` (o caminho da janela),
`test_d870_m2_*` (o `Update.exe` pelos dois caminhos da troca) e `test_os_caminhos_da_troca_passam_pela_mesma_conferencia`.

## A lista das falhas (§11.12 ponto 3) das peças novas

A tabela inteira, casinha por casinha, está no começo desta volta. As da caixa do Windows:
- sem área de trabalho à vista (o programa aberto de longe; uma estação sem tela): a peça não chama a caixa, `FALHOU`;
  a frase já está no bilhete e aparece na próxima abertura com tela (EXECUTADO: caso C);
- não deu para ler a estação: igual (`FALHOU`, sem chamar a caixa);
- o Windows não mostra a caixa (a volta zero): `FALHOU` com o erro; a frase fica no bilhete;
- a pessoa não clica: a abertura espera (é o que a D-868 pede: a frase, e DEPOIS o programa abre); a caixa fica em
  cima de tudo (`MB_TOPMOST`);
- a tela bloqueada: a caixa espera na área de trabalho dele até ele voltar;
- o notebook desliga com a caixa na tela: a reprovação e a frase já estão no bilhete; a abertura seguinte mostra a
  caixa (teste `test_o_programa_que_morre_com_a_caixa_na_tela_mostra_a_frase_na_abertura_seguinte`);
- o bilhete não grava (disco cheio): a caixa aparece mesmo assim; se a reprovação não gravou, a próxima abertura testa
  de novo (segundos) e não mostra a caixa de novo se o "visto" gravou;
- a pasta da conta não grava o "visto": a caixa aparece de novo na abertura seguinte (a frase está no bilhete).
As do `Update.exe`: ele some antes de achar a versão (nada na tela; a procura falha como sem internet; quando ele volta,
o aviso); some entre o download e o clique (a frase própria, nada fecha); some nos segundos do pedido (a frase própria,
pelo disco, não pelo texto do erro); volta (o aviso de novo: EXECUTADO com a biblioteca de verdade).

## O que rodei de verdade (D-767) e o que só li

- **Executado, a caixa do Windows de verdade** (`volta5-provas/prova_caixa_de_verdade.py`, saída e três prints), numa
  área de trabalho separada criada pela prova (`CreateDesktopW`), que ninguém vê; o "programa" (um processo à parte,
  como o de verdade) entrou nela antes de qualquer janela; o executor, a regra, o disco e a caixa (`MessageBoxW` pela
  peça) de verdade; o `main.main()` de verdade com o Qt fora da tela:
  - A (a janela da versão não abre): 1 teste; a caixa "Atualização" / "A versão nova não funcionou. Não desinstale nada.
    Avise o Samuel." / OK, lida da própria caixa; a reprovação no bilhete antes dela; o OK; SÓ ENTÃO o `main.main()`
    começa, a janela não abre e aparece a caixa de sempre "Um momento"; nada pedido ao Velopack. A abertura seguinte:
    0 testes, nenhuma caixa, a procura roda;
  - B (a janela abre): a caixa, o OK, e a janela principal abre (`JanelaPrincipal`);
  - C (uma estação de janelas sem tela, criada pela prova): a peça leu "sem área de trabalho à vista" e NÃO chamou a
    caixa; a frase ficou no bilhete; o programa abriu; a abertura seguinte, com tela: a caixa, uma vez.
- **Executado, o `Update.exe` que some e volta** (`volta5-provas/prova_update_exe_volta.py`), com a biblioteca do
  Velopack 1.2.161 de verdade numa instalação de prova minha: o aviso; o `Update.exe` posto de lado; "Reiniciar agora":
  a frase própria e a janela continua; fechar: nada; a abertura seguinte sem ele: nada (a biblioteca recusa: "Update.exe
  does not exist"); ele volta: o aviso de novo (a biblioteca procura, o pacote já baixado é reaproveitado); "Sim" ao
  fechar sem ele: a troca não é pedida e a frase própria aparece na abertura seguinte, pela caixa.
- **Executado:** as 22 mutações desta volta (as 20 primeiras e as dos leves 1 e 2, rodadas todas de novo no código final) (`mutacoes_volta5-resultado.txt`: todas acusadas; a primeira linha, sem
  mutação, nenhum teste falhou; `git status` limpo depois); os testes novos no código antigo e os antigos no novo
  (`volta5-testes-no-codigo-antigo.txt`); os testes, um arquivo por vez (abaixo).
- **Só lido:** a documentação da Microsoft da caixa (a seção da leitura); o código do Velopack que cito (`locator.rs`
  114-117, 152-176, 372; `manager.rs` 294, 413-416, 463), do clone `1.2.161` que já estava na pasta de rascunho desta
  sessão. A caixa na tela de verdade do Kaique (o tamanho, a posição) só a prova à vista mostra.

## Tamanho (linhas de código, sem comentário, docstring nem linha em branco; `volta5-provas/contar_linhas.py`)

| Arquivo | `aba7b844` | agora |
|---|---|---|
| `atualizacao.py` | 878 | 867 |
| `core/fases_da_atualizacao.py` | 432 | 415 |
| `core/conversa_com_o_velopack.py` | 70 | 70 |
| total dos três | 1380 | **1352 (menos 28, −2,0%)** |
| `core/windows.py` (a peça; a caixa entrou nela) | 2083 | 2127 (+44: as constantes, a estrutura, duas funções, três declarações) |

Encolheu menos do que a volta saiu porque entraram a caixa do Windows no executor (a escolha do lugar, a guarda da
frase), a regra da frase velha (M1), a conferência do `Update.exe` (M2) e a frase própria.

## Perguntas para a gerente (não são para o Samuel; decido nada sozinho nelas)

1. **RESPONDIDA pela gerente em 25/11: "deixe como está. Ela só decide quem é testado, e mudar isso mexeria em testes
   antigos (§11.8)."** Fica como está. O texto da pergunta: **A abertura ainda lista os nomes da pasta da última boa** (`ler_ultima_boa`), só para saber se a versão que roda é
   a última boa (a regra de quem é testado, D-856/D-857, de antes). Nada volta para ela nem lê o pacote. O pedido dizia
   "nada automático lê dela"; tirar essa leitura (decidir só pela marca de aprovada e pelo pacote em `packages`) daria o
   mesmo resultado nas instalações de verdade, mas muda a regra de quem é testado nas montagens de prova de uns 20
   testes antigos que não são da volta (a regra de 03/11 manda não mudar teste antigo). Não fiz. Se a gerente quiser,
   é uma mudança pequena, numa função só (`fases.precisa_do_teste`), com a lista dos testes afetados.
2. **"Tenta abrir assim mesmo" e o "e para" da D-857.** Li as duas juntas: a versão reprovada para a atualização
   nesta abertura (não procura, não baixa, não pede nada ao Velopack: a prova da D-867 no Livro diz "versão reprovada →
   nada é pedido ao Velopack") e o programa abre; nas aberturas seguintes a procura volta, e uma correção publicada é
   oferecida (se a janela abrir). Se a gerente ler diferente (procurar já na mesma abertura), é uma linha.
3. **A reprovação depois do "Sim" ao fechar** (a versão nova é testada sem janela, D-769: nada abre na tela): a caixa
   só aparece na próxima vez que o Kaique abrir o programa, antes de tudo. Mostrar a caixa na hora apareceria do nada,
   com o programa já fechado; mantive a D-769.
4. **Não tive como avisar no meio** que a pergunta da frase do M2 estava escrita (só tenho a entrega final): ela está
   no ONDE-PAREI desde o commit `2b5ab642`.

## Ressalvas

1. A caixa de verdade rodou numa área de trabalho separada, com o `python.exe` da `.venv` (não o programa empacotado de
   460 MB) e o Qt fora da tela; o tamanho e a posição da caixa na tela do Kaique, e se ela vem para a frente
   (`MB_SETFOREGROUND` pode ser recusado pelo Windows; aí ela fica em cima, `MB_TOPMOST`, e o botão pisca), só a prova à
   vista mostra.
2. O OK foi clicado pela prova com a mensagem do botão (`WM_COMMAND`); o botão da caixa com só o OK tem o número 2, e a
   caixa voltou como OK (`IDOK`), como a documentação diz para essa caixa.
3. Quando a janela da versão estragada não abre, depois da caixa da D-868 o Kaique ainda vê a caixa de sempre do
   programa, "Aconteceu um problema inesperado, mas o programa continua funcionando.", e o programa fecha: essa frase
   não é verdade nesse caso. Não é do atualizador (é o `main.py`, a rede de segurança de sempre) e não mexi: está em
   "Bugs para a Lista de bugs".
4. Uma versão reprovada cuja janela não abre nunca chega a receber a correção sozinha: o processo fecha antes de a
   procura terminar. É o efeito da opção A ("a resposta fica para o Windows dar"): o Samuel reinstala ou publica e o
   Kaique reinstala; a última boa está guardada para isso (D-869).
5. Enquanto o `Update.exe` falta, as aberturas seguintes não dizem nada (a biblioteca do Velopack nem começa; tratado
   como sem internet). O Kaique viu a frase própria uma vez, no clique. Mostrar uma frase a cada abertura nesse caso
   seria coisa nova: está em "Ideias".
6. A guarda da frase no bilhete antes da caixa sobrescreve uma frase guardada que ainda não foi vista, se as duas
   chegarem na mesma abertura (a da D-839 e uma do "Sim" ao fechar, por exemplo); as duas aparecem nessa abertura, mas
   se o notebook desligar entre as duas caixas, a primeira se perde. É a D-850 (duas frases no bilhete), deixada para
   depois pelo Samuel; não mexi.
7. As provas da caixa e os testes pedem os nomes `MessageBoxW`, `CreateDesktopW` etc. direto no `ctypes` dentro de
   `relatorios/` (como as provas dos quem tenta quebrar): é ferramenta de prova, não o programa (o porteiro não olha
   `relatorios/`).
8. Rodei os testes, as mutações e as provas no meu PC um arquivo por vez; o conjunto inteiro e o `teste_botoes.py` ficam
   com a rodada do GitHub (é da gerente). Uma vez, sem mutação nenhuma, o teste de tempo
   `test_windows_peca.py::test_o_programa_nasce_parado...` já tinha falhado em voltas de antes com o PC ocupado (o leve 7
   do terceiro); nesta rodada, ver abaixo.

## Ideias para a Lista de espera

- Com o `Update.exe` faltando, a abertura poderia avisar uma vez (a frase própria) mesmo sem clique, para a atualização
  não ficar parada calada até ele voltar (hoje só o clique avisa).
- A caixa "Um momento" do programa, quando a janela nem abre, poderia dizer outra coisa (não "continua funcionando").

## Bugs para a Lista de bugs

- 25/11/2026, `main.py` (a rede de segurança `tratar`, `sys.excepthook`): quando a janela principal não abre (um módulo
  que falta na versão), a caixa diz "Aconteceu um problema inesperado, mas o programa continua funcionando." e o
  programa fecha em seguida. Visto executando (`volta5-provas/prova_caixa_de_verdade-resultado.txt`, casos A). Já
  existia antes desta volta (o G1 do quarto mostra o mesmo).

## O que criei fora da pasta do projeto (não apaguei nada fora)

- Arquivos de edição e anotações na pasta de rascunho desta sessão
  (`C:\Users\fotog\AppData\Local\Temp\claude\b9ca076ad002e817\9fb2a36a-bf39-4004-8699-2ad21c149ca2\scratchpad\`:
  `edita_*.py`, `conserta_teste_decisoes.py`, `arruma_prova.py`, `tira_g1.py`, `ws.py`, `v5_*.md`, `d836_volta5.md`).
- Objetos do Windows que somem sozinhos: a área de trabalho de prova "EditorProvaVolta5" (fechada no fim da prova) e uma
  estação de janelas sem nome no processo do caso C (some com o processo). Nada no registro do Windows, nada instalado.
- Conferido só lendo: `%LOCALAPPDATA%\velopack` sem nada novo nas últimas 3 horas; o
  `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log` com a última gravação em 24/11 16:38 (antes desta volta);
  `%LOCALAPPDATA%\EditorImpressao` sem nada novo meu. O PROGRAMDATA e o LOCALAPPDATA das provas foram trocados dentro
  do Python e conferidos com `assert`.
- Dentro do projeto: `saida_teste\v5\` (cópias `git archive`, as pastas temporárias dos testes e das provas; ignorada
  pelo git; sem junções).

## Os testes (um arquivo por vez, a pasta temporária no D:)

Rodados no meu PC, um arquivo por vez, a pasta temporária no D: (`volta5-provas/rodar_testes.sh`):
- **A rodada larga** (os arquivos do atualizador, da peça do Windows, do porteiro e da trava, e os **64
  `tests/test_decisoes*.py`**): **80 arquivos, 3511 passaram, 13 pulados, nenhum falhou.** Ela começou antes de três
  mudanças pequenas desta volta (a frase guardada antes da caixa, os leves 1 e 2 do registro, comentários); por isso
  rodei de novo, no código final, todos os arquivos que importam o atualizador:
- **A rodada final dos arquivos tocados** (21 arquivos, todos passam):

```
tests/test_atualizador_volta5.py | 21 passed, 1 warning in 4.22s
tests/test_decisoes_atualizacao_volta5.py | 22 passed, 1 warning in 5.54s
tests/test_atualizador_volta4.py | 18 passed in 2.77s
tests/test_fases_da_atualizacao.py | 2255 passed in 3.60s
tests/test_atualizador_d851.py | 3 passed in 0.97s
tests/test_atualizador_novo.py | 31 passed in 14.99s
tests/test_atualizador_volta2.py | 31 passed in 2.66s
tests/test_atualizador_volta3.py | 32 passed in 6.30s
tests/test_atualizador_volta3_de_verdade.py | 4 passed, 1 skipped in 1.36s
tests/test_decisoes_atualizacao.py | 38 passed in 4.49s
tests/test_decisoes_ajudante_da_atualizacao.py | 22 passed in 2.89s
tests/test_velopack_de_verdade.py | 3 passed in 0.78s
tests/test_windows_preparo_do_computador.py | 19 passed, 1 skipped in 3.82s
tests/test_porteiro_licenca_que_acrescenta.py | 14 passed in 2.23s
tests/test_trava_windows.py | 42 passed, 3 skipped in 8.31s
tests/test_assinatura.py | 16 passed in 0.77s
tests/test_windows_peca.py | 68 passed, 3 skipped in 59.76s
tests/test_decisoes_desinstalar.py | 45 passed in 27.13s
tests/test_decisoes_testes_a_distancia.py | 13 passed in 0.90s
tests/test_decisoes_brasao.py | 20 passed in 13.11s
tests/test_decisoes_preparo_d749.py | 3 passed in 0.92s
```
- O porteiro local (`python -m regras_dos_agentes porteiro`): "nada novo (5092 arquivos lidos)", saída 0.
- O conjunto inteiro e o `teste_botoes.py` ficam com a rodada do GitHub (da gerente). O formulário de entrega
  (`regras_dos_agentes entrega`) pede o pacote do pedido da gerente, que eu não tenho: não rodei.

## Onde estou

Feito e no ramo (commits `90748bac`, `590eef24`, `5f988f17`, `2b5ab642`, `8ccffd53`, `a3d5349b`, `2873bc96` e o
das respostas de 25/11). A frase do M2 foi respondida ("Fica a A"); os leves 1 e 2 consertados (só o texto do registro).
Falta: a rodada do GitHub e a prova à vista (da gerente).

# Volta 4 — o código (24/11/2026)

Implementador (a minha segunda volta, a última pela D-815). "Pode" da gerente depois das respostas do Samuel (D-863 a
D-866). A partir de `685785e8`. Não abri agente nem janela; nada instalado; nada escrito em `C:\ProgramData\EditorImpressao`,
em `%LOCALAPPDATA%\EditorImpressao` nem na instalação do Samuel (o PROGRAMDATA e o LOCALAPPDATA das provas trocados
dentro do Python).

**Situação: feito; os testes dos arquivos tocados passam, um arquivo por vez; mutações: a rodada inteira 123 acusadas, 6 sobreviveram (explicadas abaixo; 3 delas pediram conserto e testes, feitos); a segunda rodada, 0 sobreviventes de verdade; o juiz local
do porteiro: CONFERIDO. Falta a rodada do GitHub (é da gerente).**

## As decisões e como cumpri

| Decisão (palavras dele) | O que fiz | Prova |
|---|---|---|
| D-855 "A volta tenta uma vez e nunca fica em laço: o pedido de volta leva marca (`--voltando de para`...); a versão reaberta com a marca não testa de novo, mostra a frase (3) e abre." | `trocar_para(volta=True)` manda `--voltando <de> <para>` (a peça única do Velopack, `conversa_com_o_velopack.trocar`); a abertura reaberta com a marca: rodando a de que se voltava → não testa, a frase (3), abre | `test_atualizador_volta4.py::test_d855_*` (2); a tabela da regra (`abriu_volta_recusada`, `abriu_volta_feita`); de verdade: `volta4-provas/prova_volta_uma_vez-resultado.txt` |
| D-863 (pergunta 1, a B) "não tenta voltar de novo nas aberturas seguintes. Abre a versão que está" | a marca `<id>-<versão>.sem-volta` em `ultima-boa\` (abaixo) | `test_d855_d863_*`, `test_d863_*`; a prova de verdade (B2, B3: nenhum teste, nenhum pedido de volta) |
| D-856 "Versão aprovada no teste rápido ganha uma marca no disco e não é testada de novo. Se a cópia da última boa não couber, a anterior continua valendo; conferir espaço antes de copiar, pela mesma função do motor." | a marca `<id>-<versão>.aprovada`, posta ANTES da guarda; a guarda confere o espaço por `espaco_livre_basta`, a conta que saiu de dentro de `garantir_o_motor` (os dois a chamam; só ela chama o `disk_usage`) | `test_d856_*` (2); P6-P8 das mutações |
| D-857 "A primeira versão instalada não tem volta automática. Sem baixar 460 MB na primeira abertura..." | a primeira versão = sem última boa e sem o pacote dela em `packages\` (o .msi não põe): não testa; sem última boa mas com o pacote: testa; falhou → a frase (3) e para (com a marca de "sem volta"); sai o download (`_baixar_a_que_roda`, o índice publicado `NOME_DO_INDICE_PUBLICADO` e o teste dele) e o teste por trás | `test_d857_*` (3); P9, P10 |
| D-858 / D-864 "o 'Sim' ao fechar que não troca ganha a mesma frase do 'Reiniciar agora', na abertura seguinte" · "Não deu para atualizar agora: havia outra janela do programa aberta. Tente ao fechar o programa." | o `TrocaPedida` sem janela guarda a frase no bilhete (a da D-845 com o motivo; a 2 se o pacote não tem a assinatura); o motivo novo `MOTIVO_HAVIA_OUTRA_JANELA` com o texto da D-864 (o texto velho da outra janela, que nunca aparecia, saiu: L4) | `test_d858_d864_*`; P11, P12 |
| D-859 "a regra usa o 'pacote esperando'" | sem internet, com o pacote mais novo esperando (e não reprovado), a regra segue com ele: `ConferirAssinatura(guardada=True)` → a assinatura guardada ao conferir → o aviso | `test_d859_*` (regra e executor); P13, P14 |
| D-860 "os quatro testes" | Q1, Q2, Q9, Q13 | `test_m7_q*` (4) |
| D-861, D-865, D-866 (para depois) | nada mexido | — |
| (achado meu na tabela) a rede que não responde na assinatura não é "recusada" | `Fonte.ler`: "não existe" (404; o arquivo que falta numa pasta que existe) é `FileNotFoundError` → frase 2; o resto (sem internet; a pasta da fonte que nem existe) é "sem rede" → só o registro | `test_a_rede_que_nao_responde_na_assinatura_nao_e_recusada`; P15, P16 |
| L1, L5 (leves do terceiro "quem tenta quebrar") | L1: uma regra, escrita num lugar só (o comentário de `PASTA_DA_ULTIMA_BOA`): o nome final da assinatura só é escrito pela guarda, POR ÚLTIMO, depois do pacote conferido no nome final; a assinatura que chega tem outro nome (`.assinatura.chegando`). L5: a soma é uma conta só (`assinatura.soma_sha256`, que também copia) | `test_l1_*` (3, um deles o caso G8 que o terceiro "quem tenta quebrar" executou: o nome final preso), `test_l5_*`; P17, P18 |

## Onde mora o "já tentou voltar" (D-863), e por que não é um juiz novo

É um arquivo no disco, `<raiz>\ultima-boa\<id>-<versão>.sem-volta`, ao lado da marca de aprovada e da assinatura da
última boa, escrito por `marcar` (a única escrita das marcas) em dois momentos: (1) a versão reaberta pelo Velopack com
`--voltando` (a volta recusada pelo Windows); (2) a volta que nem pôde ser pedida, ou não havia última boa (D-857). Ela
entra na abertura como mais um fato do disco (`Abriu.sem_volta`), e a regra o usa num lugar só, `_precisa_do_teste`
("não é a última boa, não foi aprovada, não tem a marca de sem volta, e não é a primeira versão do .msi"). O
`estado.json` continua só com "reprovadas" e "frase" (`CHAVES_DO_BILHETE`; o teste `test_o_bilhete_so_guarda_as_duas_coisas`
continua passando). Uma volta interrompida ANTES de ser pedida (o notebook desligou) não deixa a marca: é refeita na
abertura seguinte, como desde a volta 2. "Volta ao normal com a próxima atualização": a versão seguinte não tem a marca.

## O que mudou no que já estava escolhido e testado (§11.8)

- O teste por trás, com a janela aberta (a primeira abertura depois do .msi e depois da pergunta do Windows), saiu (D-857).
- O download da D-851 saiu (D-857 a mudou).
- O "Sim" ao fechar deixou de ser calado (D-858).
- A assinatura que não se consegue ler por falta de rede deixou de mostrar a frase (2).
- Os testes que mudaram por isso estão na lista da D-836, seção "Volta 4". Nenhum teste de fora do atualizador mudou.

## Como fica para quem usa (§11.9)

- A primeira abertura depois de instalar: nada por trás (nem teste, nem cópia de 460 MB).
- Uma versão nova que passa no teste: daí em diante abre sem o teste (sem os segundos sem nada na tela).
- Uma versão nova que falha: volta em segundos (a frase 1); se o Windows não deixar, a frase (3) uma vez, e o programa
  abre na versão que está; nada de janelinha do atualizador a cada abertura.
- "Sim" ao fechar que não pôde: a frase com o motivo na abertura seguinte.
- Sem internet, com a versão nova já baixada: o aviso e a pergunta ao fechar aparecem.
- No livro (PDF): nada muda.

## Caminho → função (o que mudou)

| Caminho | A regra / a função |
|---|---|
| precisa do teste? | `fases._precisa_do_teste` (um lugar só) |
| a volta pedida | `Atualizacao._voltar` → `trocar_para(volta=True)` (`--voltando`) → `conversa_com_o_velopack.trocar` |
| a volta recusada, reaberta | `_ao_abrir` (rodando a de que se voltava) → `MarcarSemVolta` → `marcar` |
| a volta que não deu / sem última boa | `fases._volta_que_nao_deu` (um lugar só) → `MarcarSemVolta` + a frase (3) |
| passou no teste | `MarcarAprovada` → `marcar`; `GuardarUltimaBoa` → `guardar_ultima_boa` |
| o espaço | `espaco_livre_basta` (o motor e a guarda) |
| a soma de um arquivo | `assinatura.soma_sha256` (a conferência da troca e a guarda) |
| a assinatura guardada | `assinatura_guardada` (a guarda e o pacote esperando) |
| "Sim" ao fechar que não troca | `proxima_fase(TrocaPedida)` sem janela → `GuardarFrase` |
| sem internet, o pacote esperando | `proxima_fase(Procurou(erro))` → `ConferirAssinatura(guardada=True)` → `_conferir_assinatura_guardada` |

## O que rodei de verdade e o que só li

- **Rodado** (`volta4-provas/prova_volta_uma_vez.py`, com o `vpk` 1.2.161 e o `Update.exe` de verdade, um programa de
  prova sem janela feito com o PyInstaller, a instalação portátil do vpk numa pasta minha, `--silent`):
  - A: a volta com `--voltando 1.2.0 1.1.0` e um arquivo de `current\` preso: o Velopack desistiu (código 1) e reabriu a
    1.2.0 COM `--voltando 1.2.0 1.1.0` (o registro do programa de prova; os ganchos `--veloapp-obsolete` à parte).
  - B: o executor de verdade aberto com essa linha de comando: 0 testes, a frase (3), a marca de "sem volta" no disco;
    as duas aberturas seguintes, pelo atalho: 0 testes, nenhum pedido de volta, nenhuma frase.
  - C: a mesma volta sem nada preso: deu certo e o Velopack reabriu a 1.1.0 com `--voltando 1.2.0 1.1.0`; o executor
    nela: a frase (1), 0 testes.
- **Rodado**: os testes, um arquivo por vez: `test_atualizador_volta4` 20, `test_fases_da_atualizacao` 2387 e os
  outros 13 arquivos do atualizador (juntos, na base das mutações: 2742 passam, 8 pulados; numa de quatro vezes, o teste
  de tempo da peça do Windows falhou, o leve 7 do terceiro "quem tenta quebrar"); e, por importarem o que mudou,
  `test_assinatura` 16, `test_claro_no_escuro` 8, `test_decisoes_brasao` 20, `test_decisoes_desinstalar` 45,
  `test_decisoes_testes_a_distancia` 13, `test_pasta_das_ferramentas` 17, `test_publicar_versao` 125,
  `test_trava_windows` 42 (3 pulados). As mutações (duas rodadas). O juiz do porteiro (CONFERIDO).
- **Só lido**: o resto do Velopack que a tabela cita (as linhas estão na tabela e na leitura da volta 3); a troca com a
  janelinha do Velopack (só a prova à vista).

## Tamanho (linhas de código, sem comentário, docstring nem linha em branco)

| Arquivo | `012c849c` (antes da volta 3) | `1d01aaf9` (o terceiro "quem tenta quebrar") | agora |
|---|---|---|---|
| `atualizacao.py` | 660 | 832 | 878 |
| `core/fases_da_atualizacao.py` | 358 | 405 | 432 |
| `core/conversa_com_o_velopack.py` | 64 | 70 | 70 |
| total | 1082 | 1307 | 1380 (+5,6% sobre `1d01aaf9`) |

Saiu: o download (`_baixar_a_que_roda` e o índice publicado), o teste por trás (`antes_da_janela`, `_depois_da_licenca`,
`_com_antes`, `_na_linha_ou_por_tras` só para a guarda), a soma duplicada. Entrou: as duas marcas, a conta única do
espaço, a assinatura que chega com outro nome, o pacote esperando sem internet, a separação "não existe / sem rede", a
frase do "Sim" ao fechar. A volta automática não encolheu em linhas: ficou com menos caminhos (um teste, uma volta, sem
download, sem repetição), e cada um tem a sua prova.

## As mutações (executado, no lugar, no ramo; `volta3-provas/mutacoes_volta3.py`)

A rodada inteira (as 100 do implementador, as 17 + 26 + 14 dos três "quem tenta quebrar", as novas da volta 3 e as
P1 a P18 desta volta), com os 15 arquivos de teste do atualizador: **123 acusadas, 6 sobreviveram, 7 saíram com o
desenho** (com o porquê), 0 erros (`mutacoes_volta3-resultado.txt`). As 6, uma por uma:
- **Q4** (a frase da troca recusada também quando deu certo): erro meu na tradução da mutação para o código novo (tirei
  só metade da troca que o terceiro "quem tenta quebrar" fez; essa metade sozinha não muda nada). Traduzida inteira.
- **Q5, Q8**: as mesmas duas que o terceiro "quem tenta quebrar" já tinha dito que não são proteção sem teste (Q5:
  mutação equivalente, a frase sem janela só entra na fila e continua no bilhete; Q8: o caminho de hoje nunca chega lá).
- **P17, N4, P18**: a mesma proteção (L1) feita em camadas que se escondiam umas atrás das outras. O passo que eu tinha
  posto nesta volta ("tirar do caminho o pacote velho no nome final antes de copiar") fazia o mesmo que "a assinatura
  por último" (P17), e nenhum teste cobrava o caso da conferência da versão que chega (P18) nem o nome da cópia
  interrompida (N4). Consertado: o passo repetido saiu (a regra num lugar só, §11.12) e entraram três testes (o nome
  final preso, o caso G8 executado pelo terceiro "quem tenta quebrar"; a assinatura que chega com um pacote velho no
  nome final; a cópia interrompida nunca fica com o nome do pacote).
Segunda rodada, só essas e as que mexem na guarda: 18 acusadas, 0 sobreviveram (`mutacoes_volta3-resultado-segunda-rodada.txt`): P17, P18 e N4 agora acusadas pelos três testes novos; Q4, traduzida inteira, acusada; as que mexem na guarda (Q1, Q13, N2, N3, N26, N27, P8) continuam acusadas sem o passo que saiu. **Ressalva:** Q5 e Q8 aparecem "acusadas" na segunda rodada só pelo teste de tempo `test_windows_peca.py::test_o_programa_nasce_parado_e_so_roda_dentro_do_grupo`, que falha às vezes com o PC ocupado (o leve 7 do terceiro "quem tenta quebrar"; falhou também uma vez sem mutação nenhuma nesta volta): não contam; elas continuam o que eram (equivalente e inalcançável).

## Ressalvas

1. A volta recusada de verdade rodou com o programa de prova (não o nosso de 460 MB) e com `--silent`.
2. O "disco cheio" da guarda é simulado no teste (o `disk_usage` trocado); a conta é a de verdade.
3. Um teste chama o despachante de dentro da peça do Windows por `getattr` (a ressalva da volta 3; não mudou).
4. A marca de aprovada que não consegue ser gravada (disco cheio, sem licença): a abertura seguinte testa de novo
   (segundos sem nada na tela), só enquanto não der para gravar.
5. O teste "a cópia interrompida nunca fica com o nome do pacote" falha em `1d01aaf9` por outro motivo (lá a cópia era
   outra função, que o teste não interrompe): ele não é teste de reversão; a proteção dele existia (a prova é a mutação N4).
6. O `pyinstaller.exe` da `.venv` não abre (a prova usa `python -m PyInstaller`); é da `.venv`, não do programa.

## Perguntas para o Samuel

Nenhuma nova.

# Volta 4 — a tabela das falhas (24/11/2026)

Implementador (o mesmo da volta 3; esta é a minha segunda volta, a última pela D-815). Pedido da gerente de 24/11:
**antes de qualquer código**, a tabela "passos × jeitos de dar errado" (D-862), já com as três regras do Samuel (D-855,
D-856, D-857) e o resto do recado (D-858, D-859, D-860; D-861 fica para depois). Ramo `atualizador-novo-2026-11-23`, a
partir de `1d01aaf9`. Li inteiro: `quem-tenta-quebrar-3/relatorio.md`, a seção "Depois do terceiro 'quem tenta
quebrar' — encolher a volta automática" do `resposta-do-fable.md` e as linhas D-851 e D-855 a D-862 do Livro.

**Situação: a tabela foi entregue; o Samuel respondeu (D-863 a D-866) e a gerente deu o "pode". Atualizada abaixo
com as respostas (a casinha "Voltar × desliga" e a "Windows nega" dependiam da pergunta 1). O código está na seção de
cima, "Volta 4 — o código".**

## As palavras do Samuel que esta volta cumpre

- D-855: "A volta tenta **uma vez** e nunca fica em laço: o pedido de volta leva marca (`--voltando de para`, como a
  D-839); a versão reaberta com a marca não testa de novo, mostra a frase (3) e abre."
- D-856: "Versão aprovada no teste rápido ganha uma marca no disco e **não é testada de novo**. Se a cópia da última
  boa não couber, a anterior continua valendo; conferir espaço antes de copiar, pela mesma função do motor."
- D-857: "**A primeira versão instalada não tem volta automática.** Sem baixar 460 MB na primeira abertura. A última
  boa passa a existir a partir da primeira atualização que der certo, copiada de `packages\`, sem internet. A D-851 muda
  nesse sentido."
- D-858: "o 'Sim' ao fechar que não troca ganha a mesma frase do 'Reiniciar agora', na abertura seguinte."
- D-859: "a regra usa o 'pacote esperando'." · D-860: "os quatro testes." · D-861: "M1 (dois cliques): deixo para
  depois."

## Como as três regras ficam na abertura (o desenho que a tabela usa)

A abertura continua derivando tudo do que existe (a emenda do Fable). O que muda:

- **Marca de aprovada (D-856):** um arquivo `aprovada-<versão>` em `<raiz>\ultima-boa\`, escrito quando a versão passa
  no teste rápido, ANTES de copiar o pacote. É dado no disco, ao lado da última boa (como a assinatura, D-852); o
  `estado.json` continua só com "reprovadas" e "frase".
- **Quem testa:** só a versão que roda que **não é a última boa e não tem a marca de aprovada**, e só antes da janela.
  O teste "por trás, com a janela aberta" sai inteiro (ele só existia para a primeira versão e para depois da pergunta
  do Windows).
- **A primeira versão instalada (D-857):** é a que roda sem última boa e **sem o pacote dela em `packages\`** (o `.msi`
  não põe nada lá: conferido de verdade na volta 3). Ela não é testada, nada é baixado, não há volta. Sai o
  `_baixar_a_que_roda` (o download da D-851) e o que só servia a ele.
- **Sem última boa, mas com o pacote da versão em `packages\`** (uma atualização entrou e a última boa não existe: a
  primeira atualização depois do `.msi`, ou a pasta apagada): testa antes da janela; passou → marca e guarda (ela vira a
  primeira última boa, copiada de `packages\`, sem internet); não passou → frase (3) e para (D-857: "se a versão nova
  falhar no teste, aparece a frase (3) da D-778 e para").
- **A volta (D-855):** o pedido leva `--voltando <de> <para>` pela peça única do Velopack. Reaberta a anterior com a
  marca: a frase (1), uma vez, e a abertura comum. Reaberta a que falhou com a marca (o Windows não deixou trocar): não
  testa, a frase (3), e abre. Nunca há laço.
- **O espaço (D-856):** a guarda confere o espaço livre antes de copiar, pela mesma conta que o motor já faz
  (`garantir_o_motor`, hoje escrita dentro dele: o `shutil.disk_usage` com a `FOLGA_DO_MOTOR_BYTES`). Ela sai de dentro
  do motor para uma função só, que os dois chamam.
- **O pacote esperando (D-859):** sem internet, com o pacote da versão nova já em `packages\` e a assinatura dela
  guardada quando ela foi conferida, o aviso volta e a pergunta ao fechar aparece.
- **O "Sim" ao fechar que não troca (D-858):** guarda no bilhete a frase da D-845 com o motivo (ou a frase 2, se o
  pacote não tem a assinatura, D-848), e a abertura seguinte a mostra.

As frases, palavra por palavra do Livro (o título da caixa é sempre "Atualização", D-846):
**(1)** "A atualização não deu certo. O programa voltou para a versão anterior e continua funcionando. Avise o Samuel."
· **(2)** "Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do Samuel. O programa continua
funcionando. Avise o Samuel." · **(3)** "A atualização não deu certo e o programa não conseguiu voltar sozinho. Não
desinstale nada. Avise o Samuel." · **(D-839)** "A atualização não deu certo. O programa continua na versão de antes e
funcionando. Avise o Samuel." · **(D-840)** "Feche a outra janela do programa e clique de novo." · **(D-843)** "Esta
versão precisa de um motor novo. Avise o Samuel." · **(D-845)** "Não deu para atualizar agora: [motivo]. Tente ao fechar
o programa.", com um dos nove motivos da D-847.

## A tabela

Em cada passo, uma linha por jeito de dar errado. **"muda na volta 4"** = em `1d01aaf9` o resultado é outro (dito entre
parênteses). Os achados do terceiro "quem tenta quebrar" vão marcados onde caem (G1, M1 a M6; L1 a L7 = os leves).

### 1. Procurar (só ao abrir, por trás, com a janela aberta)

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio | nada a desfazer: procurar só lê | nada (estava por trás) | nada |
| Windows nega | não se aplica: procurar não pede nada ao Windows (só à rede; um bloqueio de rede é "sem internet") | — | — |
| disco cheio | não se aplica: procurar não grava (a linha do registro, se não couber, vai para o `erros.log`) | — | — |
| sem internet | registra; **se há pacote esperando** (o da versão nova, já em `packages\`, com a assinatura guardada quando foi conferida), confere essa assinatura e segue como se tivesse achado: o aviso. **muda na volta 4** (hoje: nada; M6) | sem pacote esperando: nada (sem internet não é falha); com ele: o aviso "Reiniciar agora / Depois" | nada |
| clique repetido | duas aberturas procuram cada uma; as duas podem mostrar o aviso | o aviso em cada janela | nada |
| arquivo some | não se aplica (procurar não usa arquivo nosso). Se a assinatura guardada do pacote esperando sumiu: sem internet, o pacote esperando não é oferecido (sem a assinatura não dá para conferir) | nada | nada |
| sem licença | não procura: a pasta do programa não aceita gravação, e a abertura faz a pergunta do Windows antes da janela (D-806) | a pergunta do Windows | nada |

### 2. Baixar (por trás)

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio | o Velopack deixa `<nome>.partial`; a próxima abertura baixa de novo e ele apaga o `.partial` (manager.rs 419-481) | nada | o `.partial` até a próxima |
| Windows nega (o antivírus prende o arquivo) | o download falha; registra; a próxima abertura tenta | nada: o aviso não aparece (ver pergunta 4) | o `.partial`, às vezes |
| disco cheio | o download falha; registra; a próxima abertura tenta | nada (ver pergunta 4) | o `.partial`, às vezes |
| sem internet (cai no meio) | igual ao "desliga" | nada | o `.partial` |
| clique repetido | a segunda janela não consegue a tranca do Velopack (manager.rs 406); registra; a primeira baixa | o aviso na que baixou; na outra, só depois, na próxima abertura | nada a mais |
| arquivo some (o antivírus tira o pacote logo depois) | a leitura do motor que ele pede falha: não é anunciado; registra | nada; a próxima abertura baixa de novo | nada |
| sem licença | não se aplica: sem licença nada é procurado | — | — |

### 3. Conferir (a assinatura do Samuel antes de baixar; o motor da versão nova depois)

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio | nada a desfazer | nada | às vezes a assinatura guardada (dado, D-852) |
| Windows nega / disco cheio (a assinatura não fica guardada em `ultima-boa\`) | segue: a assinatura guardada só serve depois (guardar sem internet, D-859) | nada; depois, sem internet, a guarda e o pacote esperando não acham a assinatura (registro) | nada |
| sem internet (cai entre procurar e conferir) | **muda na volta 4** (achado meu ao montar a tabela): hoje "não achei a assinatura" vira "recusada" e mostra a frase (2); passa a separar "o arquivo da assinatura não existe na versão publicada" (a frase 2, como hoje) de "a rede não respondeu" (só o registro; a próxima abertura tenta) | sem internet: nada (hoje: a frase (2), errada) | nada |
| assinatura errada | não baixa; não vai para "não tentar"; a próxima abertura confere de novo | a frase (2), uma vez | nada |
| motor novo que não está no lugar | não anuncia nem troca (D-843) | "Esta versão precisa de um motor novo. Avise o Samuel.", uma vez | o pacote baixado em `packages\` |
| clique repetido | não se aplica (não há clique aqui) | — | — |
| arquivo some | ver "Baixar, arquivo some" | — | — |
| sem licença | não se aplica | — | — |

### 4. "Reiniciar agora" (a conferência por trás, o fechar, o pedido da troca)

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio | antes do pedido: nada mudou; a próxima abertura mostra o aviso de novo | o aviso de novo na próxima abertura | o pacote esperando |
| Windows nega (a lista de processos) | não troca | "Não deu para atualizar agora: o Windows não mostrou quais programas estão abertos. Tente ao fechar o programa." | nada |
| Windows nega (o atualizador do Velopack não abre, depois de a janela fechar) | o programa abre de novo | a janela reabre e mostra "Não deu para atualizar agora: o atualizador do programa não começou. Tente ao fechar o programa." | a frase no bilhete, até mostrar |
| disco cheio | não se aplica ao clique (nada é gravado pelo atualizador; o fechar grava o projeto como sempre) | — | — |
| sem internet | não se aplica (tudo é local) | — | — |
| clique repetido | com outra janela aberta: não troca e o aviso volta (D-840, D-841); a conferência roda por trás, sem empilhar | "Feche a outra janela do programa e clique de novo." e o aviso de novo | nada |
| arquivo some (o pacote sumiu) | não troca (antes de fechar); ou, nos segundos do fechar, reabre | "Não deu para atualizar agora: o arquivo da versão nova sumiu do computador. Tente ao fechar o programa." | nada |
| pacote trocado (a soma não é a assinada) | não troca (D-848) | a frase (2) | nada |
| sem licença | não se aplica: sem licença não há aviso | — | — |

### 5. "Sim" ao fechar ("Atualizar agora?" → "Sim")

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio | o programa já gravou e saiu; ver "Trocar" | — | — |
| Windows nega (a lista; o atualizador não abre) | não troca e guarda a frase com o motivo. **muda na volta 4** (hoje: nada; M3, D-858) | na abertura seguinte: "Não deu para atualizar agora: [o motivo]. Tente ao fechar o programa." | a frase no bilhete |
| disco cheio | não se aplica (nada é gravado pelo atualizador) | — | — |
| sem internet | não se aplica (local) | — | — |
| clique repetido (outra janela aberta) | não troca (o Velopack fecharia a outra à força) e guarda a frase. **muda na volta 4** (M3). O motivo "outra janela" não está entre os nove da D-847: **pergunta 2** | na abertura seguinte, a frase com o motivo da pergunta 2 | a frase no bilhete |
| arquivo some (o pacote sumiu; o motor saiu) | não troca, guarda a frase. **muda na volta 4** (M3) | na abertura seguinte: "...o arquivo da versão nova sumiu do computador..." / "...falta no computador uma peça que a versão nova precisa..." | a frase no bilhete |
| pacote trocado | não troca, guarda a frase (2). **muda na volta 4** (M3, D-848) | na abertura seguinte, a frase (2) | a frase no bilhete |
| sem licença | não se aplica | — | — |

### 6. Trocar (o atualizador do Velopack, depois que o programa saiu)

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga antes de trocar o nome de `current` | nada mudou; a próxima abertura roda a versão de antes, acha o pacote esperando e mostra o aviso (com ou sem internet, D-859) | o aviso de novo | o pacote esperando |
| desliga entre as duas trocas de nome | o defeito conhecido do Velopack ("the app was left in a broken state", `apply_windows_impl.rs` 174-176): `current` fica faltando e o programa não abre; só reinstalar pelo `.msi` conserta (os projetos ficam). **Não muda na volta 4: pergunta 3** | o atalho não abre o programa | `current` faltando |
| desliga depois de trocar, antes de reabrir | a próxima abertura roda a nova, sem a marca de aprovada: teste antes da janela | segundos sem nada na tela, e o programa (ou a volta) | — |
| Windows nega (arquivo preso) | o Velopack tenta 10 vezes, desiste e reabre a de antes com o pedido (`apply.rs` 47-75); ela mostra a frase da D-839; o aviso volta quando a versão é achada (ou pelo pacote esperando) | a frase da D-839 (com janela); no "Sim" ao fechar, na abertura seguinte | o pacote esperando |
| disco cheio (o Velopack não consegue abrir o pacote numa pasta provisória) | igual ao "Windows nega" (ele desiste antes de mexer e reabre a de antes; lido, não rodado) | a frase da D-839 | o pacote esperando |
| sem internet | não se aplica (local) | — | — |
| clique repetido (o atalho durante a troca) | a abertura vê o atualizador do Velopack rodando e sai sem janela (G1 da volta 2) | nada: o clique se perde; ele clica de novo depois | nada |
| arquivo some (o pacote, ou o `Update.exe`, sumiu depois do pedido) | o Velopack não acha e reabre a de antes com o pedido | a frase da D-839 | — |
| sem licença | não se aplica: só se troca com a pasta aceitando gravação (sem ela, a abertura pergunta ao Windows e nada é procurado) | — | — |

### 7. Testar (o teste rápido, antes da janela)

Roda só na versão que não é a última boa e não tem a marca de aprovada. **muda na volta 4** (hoje: também na primeira
versão depois do `.msi`, por trás, e em toda abertura enquanto a guarda não der certo; D-856, D-857, M4).

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio | nada anotado; a próxima abertura testa de novo | segundos sem nada na tela (o leve 12 da volta 1), na próxima também | nada |
| Windows nega (o antivírus não deixa o teste rodar) | conta como "não passou" (não dá para separar): volta, ou frase (3) sem última boa | como "não passou" | a reprovação |
| disco cheio | o teste não grava; a marca de aprovada, se não couber, não fica: a próxima abertura testa de novo (segundos); registra | segundos sem nada na tela a cada abertura, só enquanto o disco estiver cheio | nada |
| sem internet | não se aplica (local) | — | — |
| clique repetido (dois cliques nos segundos do teste) | **D-861: fica para depois.** Com a D-855, nenhum laço: as duas aberturas testam; se a versão falhou, uma pede a volta e a outra pode ver "outra janela" e mostrar a frase (3) antes de o Velopack fechá-la (M1) | às vezes a frase (3) numa janela que o Velopack fecha em seguida | a reprovação |
| arquivo some (falta uma peça da versão nova) | é para isso que o teste existe: "não passou" → a volta (ou a frase 3) | ver "Voltar" | a reprovação |
| passou | a marca de aprovada; a guarda; nenhuma abertura seguinte testa de novo (D-856). **muda na volta 4** | nada (a janela abre) | `aprovada-<versão>` |
| sem licença | não se aplica: sem licença a abertura pergunta ao Windows antes de testar; depois do "Sim" vai direto ao motor (a próxima abertura testa, se precisar). **muda na volta 4** (hoje: o teste por trás logo depois do "Sim") | a pergunta do Windows | — |

### 8. Guardar a última boa (logo depois de passar no teste; copiada de `packages\`, sem internet)

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| desliga no meio da cópia | a última boa anterior continua valendo; a marca de aprovada já está lá: nada se repete (D-856). **muda na volta 4** (hoje: teste e cópia de novo em toda abertura; M4) | nada | o `<nome>.chegando` até a próxima guarda que der certo (que o apaga) |
| Windows nega (arquivo preso) | não guarda; a anterior vale; nada se repete. **muda na volta 4** (M4) | nada | nada (o `.chegando` é apagado) |
| disco cheio | confere o espaço ANTES (a mesma função do motor) e não copia; a anterior vale; nada se repete. **muda na volta 4** (hoje: copia até encher o disco, em toda abertura; M4) | nada | nada |
| sem internet | não importa: copia de `packages\`; a assinatura é a guardada quando a versão foi conferida. Sem ela, não guarda (a anterior vale). **muda na volta 4** (hoje: busca na internet e repete; M5, D-857) | nada | nada |
| clique repetido (duas aberturas guardando) | o pacote final fica certo; uma das duas registra "não consegui guardar" (L2) | nada | a última boa certa |
| arquivo some (o pacote não está em `packages\`) | não guarda e **não baixa** (D-857); a anterior vale; nada se repete. **muda na volta 4** (hoje: baixa 460 MB, ou repete sem internet; M5) | nada | nada |
| o nome final preso com um arquivo velho (L1) | **muda na volta 4:** o nome final é tirado do caminho antes de copiar; se não der, nada é feito; a pasta nunca passa a dizer que a última boa é a nova sem o pacote conferido | nada | nada |
| primeira versão instalada (sem o pacote em `packages\`) | não há o que guardar e nada é baixado (D-857). **muda na volta 4** (hoje: baixa 460 MB na primeira abertura) | nada | nada |
| sem licença | não se aplica: só se guarda com a pasta aceitando gravação | — | — |

### 9. Voltar (o pacote guardado → `packages\` → o atualizador do Velopack, com `--voltando <de> <para>`)

| Jeito | O programa faz | O Kaique vê | Fica no disco |
|---|---|---|---|
| deu certo | o Velopack reabre a anterior com a marca; ela vê que voltou | a frase (1), uma vez, e a janela | a reprovação da que falhou |
| desliga no meio (antes de o Velopack trocar) | a volta não chegou a ser pedida, e nenhuma frase apareceu: a próxima abertura roda a que falhou, sem a marca de "sem volta", e refaz a volta uma vez (o G1 da volta 2: "uma volta interrompida é refeita") | o que a volta der: a frase (1) ou a (3) | a reprovação |
| Windows nega (arquivo preso) | **G1, muda na volta 4 (D-855, D-863):** o Velopack reabre a que falhou com a marca; ela não testa, põe a marca de "sem volta" no disco, mostra a frase (3) e abre. **Nenhuma abertura seguinte testa nem tenta voltar** (D-863, a resposta B do Samuel): abre a versão que está, sem a janelinha do atualizador; volta ao normal com a próxima atualização (hoje: testa de novo, pede a volta de novo, em laço, sem frase) | a frase (3), uma vez, e a janela (na versão que falhou); nas aberturas seguintes, a janela, sem nada | a reprovação; `<id>-<versão>.sem-volta` em `ultima-boa\` |
| disco cheio (a cópia de `ultima-boa\` para `packages\` não cabe; ou o Velopack não consegue abrir o pacote) | a volta não é pedida, ou é recusada pelo Velopack (reabre com a marca): nos dois, a marca de "sem volta", a frase (3), e abre; não tenta de novo (D-863) | a frase (3) e a janela | o `.partial`, às vezes (L3, D-866: fica para depois); a marca de "sem volta" |
| sem internet | não importa (a volta é local, D-844) | — | — |
| clique repetido | **D-861, fica para depois** (M1): sem laço; às vezes a frase (3) numa das janelas | ver "Testar, clique repetido" | — |
| arquivo some (o pacote guardado, a assinatura ou a pasta `ultima-boa`) | não há última boa: a versão que falhou fica, frase (3), para (D-857), e a marca de "sem volta" (D-863: não testa de novo). **muda na volta 4** (hoje: nada na tela, e a versão nem é reprovada; M2) | a frase (3), uma vez, e a janela | a reprovação; a marca de "sem volta" |
| sem última boa (a primeira atualização depois do `.msi` falhou no teste) | frase (3) e para (D-857), e a marca de "sem volta". **muda na volta 4** (M2) | a frase (3), uma vez, e a janela | a reprovação; a marca de "sem volta" |
| sem licença | não se aplica: sem licença a abertura pergunta ao Windows antes; a volta nunca pede licença | — | — |

## Os achados do terceiro "quem tenta quebrar", casinha por casinha

| Achado | Onde cai | O que o mata |
|---|---|---|
| G1 a volta recusada vira laço | Voltar × Windows nega | a regra 1 (D-855): `--voltando`, sem teste, frase (3) |
| M1 dois cliques nos segundos do teste | Testar × clique repetido; Voltar × clique repetido | D-861: fica para depois; com a regra 1 já não há laço |
| M2 sem última boa a versão nova entra e falha calada | Voltar × arquivo some; Voltar × sem última boa | a regra 3 (D-857): frase (3) e para, e a versão fica reprovada |
| M3 "Sim" ao fechar sem resposta | a linha 5 inteira | D-858: a frase guardada para a abertura seguinte |
| M4 teste e cópia a cada abertura; disco cheio até o fim | Testar × disco cheio; Guardar × desliga, nega, disco cheio | a regra 2 (D-856): a marca de aprovada e o espaço conferido antes |
| M5 a premissa da D-851 e o "tentar de novo" | Guardar × sem internet, arquivo some; primeira versão | a regra 3 (D-857): nada é baixado; a última boa nasce da primeira atualização |
| M6 o pacote esperando não usado | Procurar × sem internet | D-859 |
| M7 quatro proteções sem teste | — (são testes) | D-860: um teste para cada (Q1, Q2, Q9, Q13), que falha quando ela é desligada |
| achado meu: "sem internet" na conferência da assinatura mostra a frase (2) | Conferir × sem internet | separar "não existe" de "a rede não respondeu" (pergunta nenhuma: a frase (2) continua só para a versão sem a assinatura) |

**Os leves:**
1. L1 (a guarda que falha deixa a pasta dizendo "a nova"): **conserto** (Guardar, linha própria).
2. L2 (dois processos guardando, o registro confuso): o pacote final fica certo; o Kaique nunca vê. **Pergunta 4.**
3. L3 (um `.partial` da volta com o pacote guardado estragado, até o próximo download): o Kaique nunca vê; ocupa até
   460 MB até a próxima atualização. **Pergunta 4.**
4. L4 (sobras): o campo `pendente` passa a ser usado (D-859); o texto do motivo "outra janela" passa a ser usado no
   "Sim" ao fechar se o Samuel aprovar (pergunta 2), senão sai; o texto velho de
   `tests/test_velopack_de_verdade.py` é corrigido (só o texto; entra na lista da D-836). **Conserto.**
5. L5 (a soma do pacote escrita em dois lugares): **conserto**: uma função só de somar (em `assinatura.py`, ao lado da
   de hoje), que a guarda usa para somar e copiar numa leitura só.
6. L6 (a licença `/T` da pasta do registro: o arquivo ligado criado nos milissegundos entre conferir e dar a licença):
   o Kaique nunca vê; a mesma conferência já vale para a raiz. **Pergunta 4.**
7. L7 (dois testes de fora do atualizador lentos com o PC ocupado): não é do atualizador; nada a mudar.

## O que a tabela já diz que muda no código, depois do "pode" (para a gerente conferir o tamanho do trabalho)

- A regra: a abertura ganha "aprovada" e "o pacote da versão em `packages\`"; sai o teste por trás; a volta leva a
  marca; o "Sim" ao fechar guarda a frase; a procura sem internet usa o pacote esperando.
- O executor: sai `_baixar_a_que_roda` (e a leitura do índice publicado, que só ele usa); a guarda escreve a marca e
  confere o espaço pela função que sai de dentro do motor; a volta passa a marca pela peça do Velopack (a mesma
  `trocar_para`).
- A tela: nada novo (as frases já existem; a do "Sim" ao fechar vem pela fila de sempre).
- Testes: os da D-851 que cobram o download saem ou mudam (lista da D-836); testes novos que falham em `1d01aaf9`; os
  quatro do M7; mutações de novo.

## Perguntas para o Samuel (§11.13) — respondidas em 24/11 ("Aceito as quatro, com a sua na 1", a da gerente)

- 1 → **D-863: B**, ao contrário da minha sugestão: depois da frase (3) o programa não tenta voltar de novo.
- 2 → **D-864:** "Não deu para atualizar agora: havia outra janela do programa aberta. Tente ao fechar o programa."
- 3 → **D-865:** o defeito do Velopack entre as duas trocas de nome fica para depois.
- 4 → **D-866:** os quatro casos (a) a (d) ficam para depois; não consertados, não mexidos.

O texto das perguntas, como foi entregue:

**1. Depois da frase "não conseguiu voltar sozinho", o programa tenta voltar de novo?** É a volta automática para a
versão anterior, quando a versão nova não passa no teste. Com a sua regra, ela tenta uma vez; se o Windows não deixar
(um arquivo preso), aparece "A atualização não deu certo e o programa não conseguiu voltar sozinho. Não desinstale nada.
Avise o Samuel." e o programa abre na versão nova (a que falhou). A dúvida é a abertura SEGUINTE, pelo atalho: o arquivo
preso pode já ter sido solto.
**O que o senhor escolhe:** (A) na abertura seguinte, tenta voltar mais uma vez, sem testar de novo (sugestão: a trava
de um arquivo costuma passar; continua sem laço, uma tentativa por abertura, e a frase aparece uma vez só); (B) não
tenta mais: fica na versão que falhou até o senhor resolver. Só comentário também vale. Nada do que já funciona muda.

**2. A frase do "Sim" ao fechar quando há outra janela do programa aberta.** Com a sua decisão de hoje, o "Sim" ao
fechar que não consegue trocar mostra, na abertura seguinte, "Não deu para atualizar agora: [motivo]. Tente ao fechar o
programa." O caso mais comum é haver outra janela do programa aberta, e esse motivo não está entre os nove que o senhor
aprovou (no "Reiniciar agora" esse caso tem a frase "Feche a outra janela do programa e clique de novo.", que não serve
para a abertura seguinte). Exemplo: o Kaique tem duas janelas, fecha uma com "Sim"; na próxima vez que abrir, aparece
a frase.
**O que o senhor escolhe:** (A) "Não deu para atualizar agora: havia outra janela do programa aberta. Tente ao fechar o
programa." (sugestão); (B) "Não deu para atualizar agora: o programa estava aberto em outra janela. Tente ao fechar o
programa."; (C) outro texto (escreva). Só comentário também vale.

**3. O defeito do próprio Velopack no meio da troca.** Se o notebook desliga no instante exato entre as duas trocas de
nome que o atualizador faz na pasta do programa (uma fração de segundo), a pasta fica sem a versão que roda e o atalho
não abre mais o programa. Só reinstalar pelo instalador conserta; os projetos do Kaique não são tocados. É do Velopack
(o senhor já tinha escolhido continuar com ele); a volta automática não alcança esse caso, porque nada do
programa roda.
**O que o senhor escolhe:** (A) deixo para depois (sugestão: raríssimo, e reinstalar resolve sem perder nada); (B)
estudar agora uma proteção (um trabalho novo, fora destas regras). Só comentário também vale.

**4. Quatro casos que o Kaique não vê.** (a) duas aberturas guardando a cópia ao mesmo tempo: a cópia fica certa, só o
registro que a gerente lê fica confuso; (b) a volta com a cópia guardada estragada deixa um arquivo provisório de até
460 MB na pasta do atualizador, até a próxima atualização; (c) uma brecha de milissegundos na licença da pasta do
registro, que só outra conta do notebook poderia usar; (d) o download que falha por disco cheio ou arquivo preso: a
atualização não chega e nada aparece na tela (a próxima abertura tenta de novo).
**O que o senhor escolhe:** (A) deixo os quatro para depois (sugestão); (B) consertar algum agora (diga qual). Só
comentário também vale.

# Volta 3, segunda parte: as respostas do Samuel (D-847 a D-853) (24/11/2026)

Pedido da gerente de 24/11 (depois da rodada verde do GitHub de `04dd0cd4`, 45449425841): conferir a D-848, fazer a
D-851 conferindo de verdade, e procurar caminho morto da volta antiga (D-853). Mesmo ramo e worktree. Não abri agente
nem janela; nada instalado; nada no programa do Samuel, no `C:\ProgramData` nem em tarefa do Windows.

**Situação: feito; testes passando no meu PC; juiz local do porteiro: CONFERIDO; mutações: 100 acusadas, 0 sobreviventes.
Falta a rodada do GitHub (é da gerente).**

## Decisões e como cumpri

| Decisão (palavras dele) | O que fiz | Prova |
|---|---|---|
| D-847 "1 — sim, os nove motivos." | nada a mudar (os textos já eram esses) | `test_m3_todo_motivo_tem_o_texto_e_nenhum_tem_codigo` |
| D-848 "2 — sim, a frase de 18/11." | conferido: no "Reiniciar agora" com o pacote trocado já aparece a frase 2 da D-778, com o título "Atualização", nos dois caminhos (antes de fechar, e depois de fechar, pela reabertura). Nada a consertar: os testes passam em `04dd0cd4` e aqui | `tests/test_atualizador_d851.py::test_d848_*` (2); mutação N32 (trocar pela frase da D-845) acusada |
| D-849 "3 — sim, abre normalmente." | nada a mudar (já era assim desde a volta 3) | `test_m7a_...` |
| D-850 "4 — sim, deixar para depois." | nada mudado | — |
| D-851 "5 — não: a última versão boa deve ser guardada copiando o pacote que já está na pasta packages\ do programa (o instalador e cada troca deixam ele lá), sem internet; baixar só se o arquivo não estiver lá. O agente confere isso, não supõe." | conferido no código do Velopack e de verdade (abaixo). **Cada troca deixa o pacote lá; o nosso instalador (.msi) NÃO deixa.** A guarda copia de `packages\` (sem internet; a assinatura é a guardada quando a versão foi conferida); só se o pacote não está lá, baixa pelo Velopack (o índice e a assinatura publicados; o Velopack confere a soma) e então a mesma cópia conferida. Saiu o ramo "sem o pacote, nem testa" da regra | `test_atualizador_d851.py::test_d851_*` (4; 3 falham em `04dd0cd4`: `volta3b-testes-no-codigo-antigo.txt`); mutações N29-N31 |
| D-852 "Arquivo da assinatura da última boa: é dado, não peça. Aprovado." | nada a mudar | — |
| D-853 (o crescimento; a volta antiga por download ao lado da nova) | procurado: não sobrou (abaixo) | — |

## A leitura do Velopack para a D-851 (§11.12 ponto 6), com a fonte, e o que rodei de verdade

Fonte: o clone da etiqueta `1.2.161` (commit `92d6a1c`) na minha pasta de rascunho (só lido).

- **O `Setup.exe` deixa o pacote completo em `packages\`**, com o nome `<id>-<versão>-full.nupkg`:
  `bins/src/commands/install.rs` 199-218 ("Copying nupkg to packages directory", `pkg.copy_bundle_to_file(&nupkg_path)`),
  o nome em `lib-rust/src/locator.rs` 199-203 (`get_ideal_local_nupkg_path`). **Só lido** (não é o nosso instalador).
- **O `.msi` (o nosso instalador, D-723) NÃO deixa:** o vpk monta o .msi com a pasta portátil (`Update.exe`,
  `current\`, o atalho, `.msi-installed`; `vpk/Velopack.Packaging.Windows/Commands/WindowsPackCommandRunner.cs`
  230-243) e o modelo do .msi só declara `packages` vazia (`Msi/Templates/MsiTemplate.hbs` 18-20) e inclui os arquivos
  dessa pasta (173). **Rodado:** as tabelas de um .msi de prova montado pelo vpk de verdade com as nossas opções, e as
  do NOSSO .msi da 1.1.0 (`EditorImpressao-arquivos\prova-atualizador-4\estado-1.1.0\v1.1.0\`, só lido): 586
  arquivos, nenhum em `packages\`, nenhum `.nupkg`.
- **Cada troca deixa o pacote novo e o velho sai:** o `download_updates` grava `<FileName>` do índice (o
  `<id>-<versão>-full.nupkg`) em `packages\` e apaga os outros `.nupkg` e `.partial` (`manager.rs` 405-481); a troca
  (`apply_windows_impl.rs` 47-...) não mexe em `packages\` (só apaga um pacote estragado, 52, 57, 145); a abertura
  guarda o da versão atual e o esperando (`app.rs` 160-245). **Rodado:** a biblioteca de verdade baixou a 1.0.1 para
  `packages\` e apagou a 1.0.0; o `Update.exe` de verdade (`apply --silent --norestart`, numa instalação portátil
  minha: sem janela, sem registro do Windows, sem atalho) trocou e deixou a 1.0.1 em `packages\`; o "pendente"
  depois da troca é nada. Não rodei a abertura do programa trocado (o `App.run`): só lido.
- **Pacote de diferença (delta):** se houvesse, o Velopack monta o completo a partir dele e grava com o nome do
  completo (`manager.rs` 486-535 e 459). Mas o nosso publicar não faz delta (`empacotar.py` 1353, `--delta None`,
  D-789): todo download é do completo. **Só lido.**
- Saída inteira: `volta3-provas/prova_packages-resultado.txt` (o script: `prova_packages.py`).

## O que o programa faz agora (a guarda da última boa)

1. O pacote da versão que passou está em `packages\` (o caso de toda troca): copia para `ultima-boa\` somando, sem
   internet; a assinatura é a guardada quando a versão foi conferida (antes de baixar). Se a soma da cópia não é a que a
   assinatura afirma: não guarda (o pedaço copiado é apagado), o registro diz, a última boa continua a de antes, e a
   próxima abertura testa e tenta de novo.
2. Não está (o caso do .msi, na primeira abertura): lê o índice e a assinatura publicados da versão, confere a
   assinatura, pede ao Velopack para baixar (ele confere tamanho e soma) e faz a cópia do passo 1. Precisa de internet.
   Sem internet, ou com a assinatura errada: não guarda, o registro diz por quê.
3. **O "tentar de novo por trás a cada abertura" continua só para o caso 2 sem internet** (e para os casos raros de
   pacote ou assinatura que não conferem). Depois de uma troca ele não acontece (o pacote está lá e a assinatura foi
   guardada). Como a procura de versão nova também precisa de internet e vem DEPOIS da guarda na mesma abertura, a
   primeira vez que houver internet para atualizar, a guarda acontece antes.

## A conferência do crescimento (D-853)

- **Não sobrou caminho da volta antiga por download.** A volta só lê `ultima-boa\` (`_voltar`). A leitura do índice
  publicado mora agora num lugar só, `_baixar_a_que_roda` (o caso 2 da D-851, que é caminho vivo). Procurei todo nome
  definido em `atualizacao.py`, `core/fases_da_atualizacao.py` e `core/conversa_com_o_velopack.py` que o programa não
  usa: só `fases.TIPOS_DE_EVENTO` (a lista que a tabela exaustiva dos testes usa; existe desde a volta 1).
- `tests/test_velopack_de_verdade.py::test_a_volta_baixa_a_anterior_e_o_velopack_confere_a_soma`: o nome é da volta
  antiga, mas ele prova a biblioteca baixando de uma fonte com índice e conferindo a soma, que é o caso 2 da D-851. Não é
  caminho morto; não mexi nele.
- **Tamanho (linhas de código, sem comentário, sem docstring e sem linha em branco):**

| Arquivo | `012c849c` (antes da volta 3) | `04dd0cd4` (volta 3) | agora |
|---|---|---|---|
| `atualizacao.py` | 660 | 806 | 832 |
| `core/fases_da_atualizacao.py` | 358 | 410 | 405 |
| `core/conversa_com_o_velopack.py` | 64 | 70 | 70 |
| total | 1082 | 1286 (+18,9%) | 1307 (+20,8%) |

  O que entrou agora: o download do caso 2 (+26 em `atualizacao.py`); o que saiu: o ramo "sem o pacote, nem testa"
  (-5 na regra).

## Testes e mutações

- Um arquivo por vez: `test_atualizador_d851` 6, `test_atualizador_volta3` 36, `test_fases_da_atualizacao` 2171,
  `test_atualizador_novo` 35, `test_atualizador_volta2` 32, `test_decisoes_atualizacao` 42; os 15 arquivos do atualizador
  juntos: na conferência sem mutação das mutações (abaixo).
- Juiz local do porteiro (de `obra-juncao`): `PORTEIRO: CONFERIDO`.
- Mutações (`volta3-provas/mutacoes_volta3.py`, com o arquivo novo na lista e N29 a N32): na rodada inteira, de novo, depois das mudanças: os 15 arquivos juntos passam sem mutação (2510 casos); 100 acusadas, 0 sobreviveram, 7 saíram com o desenho, 0 erros (as N29 a N32 da D-851 e da D-848 incluídas)
  (`volta3-provas/mutacoes_volta3-resultado.txt`).
- Lista da D-836: seção "Volta 3, segunda parte".

## Ressalvas

1. **A premissa "o instalador deixa o pacote lá" não vale para o nosso instalador (.msi).** Por isso, na primeira
   abertura depois de instalar, guardar a última boa precisa de internet (o download de uns 460 MB). Isso já estava na
   resposta dele ("baixar só se o arquivo não estiver lá").
2. **Espaço no disco:** depois do download do caso 2, o Velopack deixa o pacote em `packages\` (é o da versão que roda)
   e a cópia fica em `ultima-boa\`: uns 920 MB no total. Depois de cada troca é igual (o pacote da versão nova em
   `packages\` e a cópia dela). Ver a pergunta 1.
3. A troca de verdade pelo `Update.exe` foi rodada numa instalação portátil minha, com um programa de prova (não o nosso
   pacote de 460 MB); a do programa de verdade, só na prova à vista.
4. O vpk pode ter deixado arquivos dele na pasta temporária da conta (o WiX) ao montar o .msi de prova; fora do projeto,
   não apaguei.

## Perguntas para o Samuel (§11.13)

**1. O espaço da cópia de segurança no notebook.** É a cópia da última versão boa que o programa guarda para voltar
sozinho em segundos (a que o senhor aprovou). O programa de atualização (o Velopack) já guarda o arquivo da versão que
está rodando na pasta dele, e a nossa cópia fica ao lado: são dois arquivos iguais de uns 460 MB, uns 920 MB no
total. Existe um jeito do Windows de ter o mesmo arquivo com dois nomes sem ocupar o dobro (um "atalho de arquivo" do
disco): os 460 MB da nossa cópia deixariam de ser gastos, e se o Velopack apagar o dele na próxima troca, a nossa
continua inteira. Situação: hoje é cópia; o atalho de arquivo seria um trabalho novo, pequeno, só no lugar que guarda.
**O que o senhor escolhe:** (A) deixar a cópia (sugestão: já testado, mais simples); (B) trocar pelo atalho de arquivo
(economiza uns 460 MB; precisa de teste novo). Só comentário também vale. Nada do que já funciona muda com (A).


# Emenda do Fable (volta 3): a verdade vem do disco, a volta é o pacote guardado (24/11/2026)

Implementador novo (D-815). Pedido da gerente de 24/11: aplicar ao atualizador novo a emenda do desenho escrita pelo
Fable depois do segundo "quem tenta quebrar" (`relatorios/para-o-fable-2026-11-23/resposta-do-fable.md`, seção
"Emenda ao desenho do atualizador") e consertar os achados de `quem-tenta-quebrar-2/relatorio.md`. Ramo
`atualizador-novo-2026-11-23`, a partir de `012c849c`. Não abri agente nem janela; nada no programa instalado, no
`C:\ProgramData` nem em tarefa do Windows de verdade (as provas de verdade rodaram em pastas minhas no D:).

**Situação: feito; os testes dos arquivos que toquei passam no meu PC, um arquivo por vez (e os 14 do atualizador
juntos: 2540 casos); as mutações todas acusadas; falta a rodada do GitHub (é da gerente) e a resposta do Samuel às
perguntas do fim.**

## Decisões que esta tarefa precisa cumprir, e como cumpri cada uma

| Decisão (palavras dele) | Como cumpri | Prova |
|---|---|---|
| D-843 (M6): "vamos fazer b e colocamos isso no plano" — motor novo fora do lugar: a frase uma vez, registra, não anuncia nem troca; o download do motor não é desta entrega | `Baixou(motor_da_nova=False)` → `MostrarFalha("motor")` (uma vez por versão, nesta conta) + registro; nada anunciado; a conferência da troca continua recusando sem o motor. Nada baixa motor. | `test_atualizador_volta3::test_m6_...`; tabela da regra `baixou_sem_o_motor_da_nova` |
| D-844: "ok" (1) — guardar o pacote da última versão que passou no teste; a volta usa esse pacote, segundos, sem internet | `<raiz>\ultima-boa\` com o pacote e a assinatura; `guardar_ultima_boa` (cópia somada, nome final só com a soma assinada); a volta (`_voltar`) usa essa pasta como a fonte de pasta do Velopack | `test_d844_a_volta_funciona_sem_internet`, `test_d844_guardar_...`, `test_g_a_guarda_interrompida_...`; de verdade: `test_atualizador_volta3_de_verdade::test_d844_...` e `volta3-provas/prova_dois_processos-resultado.txt` |
| D-845: "ok" (2) — "Não deu para atualizar agora: [motivo]. Tente ao fechar o programa." | todo "não pode" do "Reiniciar agora" (menos outra janela, que tem a frase dela, e o pacote sem a assinatura, ver pergunta 2) vira `MostrarFalha(nao_deu_agora, motivo)`; a frase é montada num lugar só (`frase_da_falha`); depois de a janela fechar, vai pelo bilhete para o programa reaberto | `test_m3_...` (3 motivos), `test_m1_m3_m5_...` na tabela, `test_d840_a_frase_so_aparece_com_outra_janela_aberta` |
| D-846: "ok" (3) — o título "Atualização" | a ponte mostra toda frase com `TITULO_DA_FALHA` ("Atualização") | `test_m8_...`, `test_d840_...`, `test_d841_...` |
| D-842 — nada aberto entra na prova sem a decisão dele | todo achado do relatório 2 foi consertado (tabela "achado por achado"); o que é escolha vai em "Perguntas para o Samuel" | esta seção |
| D-839 ("sim") — troca recusada pelo Windows: "...continua na versão de antes...", nunca a (1) | o Velopack reabre a versão de antes com o pedido (apply.rs 56-60): a abertura vê `reaberto_para` mais nova que a que roda e mostra a frase (ou a guarda no bilhete, sem janela). Não vai para "não tentar" (M1) | `test_d839_...` (2), tabela `abriu_troca_recusada*` |
| D-840/D-841 ("sim"; "1, desde que seja a volta à fase 'pronta', sem espera nem peça nova") | iguais: a frase e a volta a PRONTA no mesmo evento; nenhuma espera; a conferência por trás não muda isso | `test_d840_...`, `test_d841_...`, `test_l2_...` (200 cliques) |
| D-718/D-719/D-778 (a volta; o aviso uma vez; as três frases) | a volta antes da janela, pela última boa; a frase (1) derivada; as frases iguais | `test_d718_*`, `test_d719_*`, `test_g1_*` |
| D-769 ("Se o notebook desligar no meio, nada se perde e a troca tenta de novo depois") | troca interrompida não proíbe a versão; volta e guarda interrompidas são refeitas na abertura seguinte | `test_m1_...`, `test_g1_a_volta_interrompida_...`, `prova_dois_processos` (G1 e G) |
| D-732, D-733, D-741, D-749, D-806, D-834 | iguais (a pergunta antes da janela; "preparado?" = a raiz grava; a licença da raiz é o último passo; a do ProgramData vem depois dela no mesmo passo e não decide o "preparado?") | `test_atualizador_novo::test_protecao_1..7`, `test_decisoes_preparo_d749` |
| D-790/D-833 | iguais | `test_protecao_4a/4b`, `test_m9_v10/v11` |
| D-837 (a única licença, `icacls ... /grant "*S-1-5-32-545:(OI)(CI)M" /T` pela peça) | a MESMA função (`dar_licenca_aos_usuarios`) e a MESMA linha, agora com a pasta que recebe; chamada só por `_fazer_passo`, duas vezes; a K03 só mudou o nome da variável na linha aceita (`raiz` → `pasta`) | `test_porteiro_licenca_que_acrescenta` (14), `test_m4_a_pergunta_unica_...`, `test_m4_de_verdade_...` |
| D-831/D-835/D-832 | iguais | `test_d831_*`, `test_d835_*`, `test_d832_*` |
| D-836 | a lista teste por teste, seção "Volta 3" de `lista-dos-testes-d836.md` | — |
| D-767, D-811 a D-813, D-827 | as provas de verdade (Velopack, `icacls`, dois processos) e as mutações (abaixo) | `volta3-provas/` |

## O que já estava escolhido e testado aqui, e o que mudou (§11.8)

- Escolhido por ele e **mudado pela emenda que a gerente trouxe** (não por mim): o M1 (troca que não aconteceu não é
  falha), o M4 (sem bilhete o programa continua), a volta pelo pacote guardado (D-844), a frase da D-845 e o título da
  D-846. Os testes que cobravam o jeito antigo estão na lista da D-836 ("vale hoje").
- Escolhido por ele e **igual**: as frases da D-778, D-835, D-839, D-840; a ordem da pergunta (D-834); o motor tudo ou
  nada; a janelinha do Velopack; o "Depois" ao fechar. Nenhum desses textos mudou.
- Escolhido por implementador antes e mudado (não era decisão dele): a assinatura recusada deixa de ir para "não
  tentar" (a emenda: "Só teste rápido reprovado põe versão em 'não tentar'"); o `Update.exe` sem caminho legível deixa
  de contar como "rodando" (M7 a; ver pergunta 3).
- Fora do atualizador: só `tests/conftest.py` (o PROGRAMDATA da rodada, leve 1). Nenhum teste de fora mudou.

## Como fica para quem usa e no livro (§11.9)

**No livro (PDF): nada muda.** Pelo atalho "(desenvolvimento)" e pelo código, nada muda (o programa não está instalado
pelo Velopack: nada roda).

- **Primeira abertura depois de instalar:** igual (a pergunta do Windows antes da janela). Novo, por trás, com a janela
  aberta: o teste rápido da versão instalada e a cópia do pacote dela para `ultima-boa` (uns 460 MB, segundos de
  disco). Precisa da assinatura publicada dessa versão (internet); sem internet, tenta de novo nas aberturas seguintes,
  sempre por trás (ressalva 3).
- **Abertura comum:** igual. Nada a mais na frente da janela.
- **"Reiniciar agora":** o aviso some e a janela **continua respondendo** enquanto o programa confere o pacote (antes
  ficava parada até uns 8 s); então fecha e o Velopack troca. Se não puder trocar: "Não deu para atualizar agora:
  [motivo]. Tente ao fechar o programa." (título "Atualização"); com outra janela aberta, a frase de sempre e o aviso de
  novo. Se a troca falhar depois de a janela fechar, o programa abre de novo e mostra a frase com o motivo.
- **Versão nova que não passa no teste:** volta para a anterior em segundos, sem internet, antes da janela; a anterior
  abre e mostra uma vez "A atualização não deu certo. O programa voltou para a versão anterior...". Se o notebook
  desligar no meio da volta, a próxima abertura refaz a volta (antes ficava na versão estragada com a frase errada).
- **Troca interrompida (desligou, arquivo preso):** não aparece mais "A atualização não deu certo" para quem só
  desligou; o aviso da versão nova volta. Se foi o Windows que recusou trocar, aparece a frase da D-839 uma vez e o aviso
  volta (antes a versão nunca mais chegava).
- **Versão que pede motor novo:** "Esta versão precisa de um motor novo. Avise o Samuel." uma vez (antes, nada, para
  sempre).
- **Espaço no notebook:** mais uns 460 MB (a última boa), dentro da pasta do programa; o desinstalar apaga junto.
- **Problema novo que eu vejo:** depois de cada versão nova aprovada, uma cópia de 460 MB por trás (uma vez por versão);
  no primeiro dia sem internet, o teste rápido por trás a cada abertura (ressalva 3).

## Caminho → função (§11.12)

| Caminho | Entra por | A regra | A ação |
|---|---|---|---|
| Abrir (qualquer abertura) | `main.py` → `atender_linha_de_comando` → `Atualizacao.abrir` | `proxima_fase(Abriu)`, com o que existe: `ler_ultima_boa`, `velopack.pendente`, `windows.atualizador_do_velopack_rodando` (só com troca possível e sem a linha de comando da reabertura), o bilhete (`reprovadas`, `frase`) | `PedirLicenca` / `RodarTesteRapido(antes_da_janela)` / `GarantirMotor` / `Sair` |
| Reaberto pelo Velopack depois de trocar | o mesmo, com `--conferir-a-versao-nova <de> <para>` | a versão que roda não é a última boa → teste antes da janela; é a de antes → a frase da D-839 | `RodarTesteRapido` / `MostrarFalha(troca)` ou `GuardarFrase` |
| Clique no atalho no meio da troca | o mesmo, sem a linha de comando | o atualizador do Velopack rodando → sai | `Sair(0)` |
| Teste rápido | efeito `RodarTesteRapido` → `Atualizacao._testar` → `windows.rodar_e_esperar` | passou → `GuardarUltimaBoa`; não passou e antes da janela → `Reprovar` + `Voltar` | `guardar_ultima_boa` (a única que guarda) / `reprovar` (a única que põe em "não tentar") / `_voltar` |
| A volta | efeito `Voltar` → `Atualizacao._voltar` | — | a assinatura guardada; `velopack.pacote_da_versao` + `velopack.baixar(<pasta da última boa>)`; `trocar_para` |
| "Reiniciar agora" | `ui/aviso_de_atualizacao.py` → `Escolheu(True)` | `ConferirTroca` (por trás) → `TrocaConferida` | `FecharJanela` / `MostrarFalha(nao_deu_agora, motivo)` / `MostrarFalha(recusada)` |
| Fechar com versão pronta | `closeEvent` → `ao_fechar` → `Fechando` | `PerguntarAoFechar` → `RespondeuAoFechar` | `Trocar` |
| Toda troca (Reiniciar, Sim ao fechar, volta) | efeito `Trocar` / `_voltar` | — | `trocar_para` (a ÚNICA; a conferência única `conferencia_da_troca` antes) → `conversa_com_o_velopack.trocar` |
| A troca que não foi pedida depois de fechar | `TrocaPedida(False)` com a janela | com outra janela aberta: nada; senão `GuardarFrase` + `ReabrirOPrograma` | `guardar_frase`, `windows.lancar_solto` |
| Toda frase na tela | `MostrarFalha(tipo, nome, motivo, sempre)` | — | ponte → `atualizacao.frase_da_falha` (a ÚNICA escolha do texto), título `TITULO_DA_FALHA` |
| O bilhete | `Reprovar`, `GuardarFrase` | — | `mudar_o_bilhete` (a ÚNICA escrita; só `reprovadas` e `frase`) |
| A licença das duas pastas | o passo `dar_licenca_aos_usuarios` da pergunta única | — | `windows._fazer_passo` → `dar_licenca_aos_usuarios(raiz, manifesto)` e depois `dar_licenca_aos_usuarios(<ProgramData>\EditorImpressao\atualizacao, atualizacao.log)` |
| "Outra janela?" e "o atualizador roda?" | conferência da troca; abertura | — | `windows.programas_rodando_de` + `windows.caminho_conferido` (a única leitura de "o caminho foi lido") |

Prova de que os caminhos chegam ao mesmo lugar: `test_os_tres_caminhos_da_troca_passam_pela_mesma_conferencia`,
`test_protecao_13_so_um_lugar_chama_a_troca_do_velopack` (pela árvore), a tabela exaustiva da regra e
`test_m1_so_o_teste_reprovado_poe_a_versao_em_nao_tentar` (todos os pares).

## A lista das falhas (§11.12 ponto 3), o que mudou na volta 3

- **Desligar no meio da troca** (Velopack ainda não trocou): a próxima abertura roda a de antes = última boa; o pacote
  continua esperando; procura, acha, o aviso volta. Nada proibido. (Se desligar entre as duas trocas de nome do
  Velopack, o defeito dele de "broken state" continua: ressalva antiga 6.)
- **Desligar no meio da troca, depois de o Velopack trocar e antes do teste:** a próxima abertura roda a nova, que não
  é a última boa → teste antes da janela.
- **Desligar no meio da volta:** idem (a nova continua não sendo a última boa) → teste de novo → volta de novo
  (provado com dois processos).
- **Desligar no meio da guarda da última boa:** sobra `<nome>.chegando`; a última boa continua a de antes; a próxima
  abertura testa e guarda de novo (provado).
- **O bilhete não grava** (de outra conta, preso): a atualização continua; a reprovação ou a frase que não gravou fica
  no registro ("NÃO ficou gravada"); a pasta ganha a licença no passo da pergunta única para isso não acontecer.
- **O registro não grava:** a linha vai para o `erros.log` da conta (como antes).
- **Sem internet na volta:** não importa (a volta é local).
- **Sem o pacote da última boa** (apagado à mão, antivírus): a volta não dá → a frase (3); a abertura seguinte tenta
  de novo.
- **A assinatura guardada não confere** (trocada): a volta não dá → a frase (3).
- **O Velopack recusa a cópia** (a soma não bate, disco cheio): a volta não dá → a frase (3), com o motivo no registro.
- **Sem o pacote da versão que roda em `packages`** (para guardar): a guarda não dá; registro; o teste roda de novo na
  próxima abertura (ressalva 3). Sem última boa e sem o pacote: nem testa (não há o que guardar nem para onde voltar).
- **Sem a assinatura da versão que roda** (nem guardada ao conferir, nem a internet): a guarda não dá; tenta depois.
- **Disco cheio ao guardar:** a cópia falha; o `.chegando` é apagado; tenta depois.
- **Uma pasta do registro que é um atalho, ou com um arquivo ligado a outro lugar dentro:** a licença não é dada
  nela (o passo falha com o motivo; a raiz já foi preparada, a pergunta não volta por isso).
- **Fechar o programa enquanto a conferência do "Reiniciar agora" roda por trás:** o fio de trás morre com o programa;
  nada foi pedido; o aviso volta na próxima abertura.
- **Erro fora do previsto dentro da troca:** vira "não pedida" e o programa reabre com a frase (leve 3).

## A leitura do Velopack (§11.12 ponto 6), com a fonte

Clone da etiqueta `1.2.161` (commit `92d6a1c`), numa pasta minha de rascunho, só lido; e o `__init__.pyi` da `.venv`.

- **Aplicar um pacote guardado por nós, sem remendo: dá.** `wait_exit_then_apply_updates` (`src/lib-rust/src/manager.rs`
  602-683) só aceita o pacote que está em `packages\` (`unsafe_apply_updates` monta `packages_dir.join(FileName)` e
  falha se não existe, 629-634). O caminho da biblioteca para pôr um arquivo nosso lá é o `download_updates` com uma
  fonte de PASTA: uma `str` que não é endereço da internet vira `FileSource` (`sources/mod.rs` 64-85, `AutoSource::new`);
  o `download_release_entry` da `FileSource` só copia `<pasta>\<FileName>` (`sources/file.rs` 37-48, não lê índice); o
  `download_updates` copia para `<nome>.partial`, confere o TAMANHO e a SHA256 do pedido (`verify_package_checksum`,
  537-561; com a SHA256 preenchida a SHA1 não é olhada) e só então dá o nome final (465-466). Provado de verdade:
  `test_atualizador_volta3_de_verdade::test_d844_...` (sem índice e sem SHA1; com a soma errada recusa e não deixa o
  nome final).
- **Se o arquivo já está em `packages\`, não copia nem confere** (413-416): por isso a conferência única da troca soma o
  arquivo de novo (já era assim).
- **O `download_updates` apaga os outros `.nupkg` de `packages\`** depois de baixar (419-481): na volta, o pacote da
  versão que falhou sai (provado em `prova_dois_processos`).
- **A abertura (`VelopackApp.run`) apaga de `packages\` todo pacote que não é o da versão que roda nem o esperando**
  (`app.rs` 160-194, `cleanup_old_packages_from_list` 228-245): por isso o pacote da anterior NÃO fica em `packages\`
  depois de uma troca, e a última boa tem de ser guardada em outra pasta (a `ultima-boa`).
- **O instalador põe o pacote da versão instalada em `packages\`** (`bins/src/commands/install.rs` 200-215, "Copying
  nupkg to packages directory"); no PC do Samuel, lido sem mexer, `packages\` tem o da 1.1.1 (a versão de agora).
- **`get_update_pending_restart`** (272-281): o pacote completo mais novo de `packages\` (lendo o manifesto de dentro:
  `locator.rs` 633-657) com versão maior que a que roda; só disco. Provado de verdade (`test_a_abertura_le_o_pacote_
  esperando_pelo_velopack`).
- **Quando a troca falha, o atualizador do Velopack reabre a versão de antes com os mesmos argumentos**
  (`bins/src/commands/apply.rs` 47-75): é o que a abertura usa para a frase da D-839.
- O que continua só para a prova à vista: o `Update.exe` de verdade aplicando o pacote da última boa (a volta) e a
  janelinha dele.

## Achado por achado (relatório 2): causa → conserto → o teste que falhava antes

Os testes estão em `tests/test_atualizador_volta3.py`; a saída deles em `012c849c` está em
`volta3-testes-no-codigo-antigo.txt` (23 falham lá pelo comportamento; os 8 do M9 passam lá, ver o M9).

| Achado | Causa | Conserto | Teste (falha em `012c849c`) |
|---|---|---|---|
| G1 volta interrompida → versão estragada com a frase (1) | a falha anotada antes de a volta acontecer e a anotação da troca apagada (o bilhete decidia) | a abertura deriva: rodando ≠ última boa → teste antes da janela → volta de novo; a frase (1) só rodando a última boa com a mais nova reprovada | `test_g1_a_volta_interrompida_...` (lá: `None == 0`), `test_g1_a_frase_1_so_depois_de_voltar`; de verdade: `prova_dois_processos` (G1) |
| M1 troca interrompida → "não deu certo" e versão proibida | a regra não separava versão ruim de troca que não aconteceu | só `Reprovar` (teste rápido) põe em "não tentar"; troca não acontecida → abertura comum, o aviso volta | `test_m1_a_troca_interrompida_...` (lá: `MostrarFalha` no lugar do aviso); tabela `test_m1_so_o_teste_reprovado_...` |
| M2 janela parada na conferência | a conferência rodava no fio da tela | `ConferirTroca` roda por trás; a janela fecha quando ela termina | `test_m2_...` (lá: 5,0 s parado) |
| M3 clique sem resposta | os outros "não pode" iam calados para DEPOIS | a frase da D-845 com o motivo (texto em `MOTIVOS_DA_TELA`), título D-846 | `test_m3_...` (3 casos; lá: nada na tela) |
| M4 o bilhete de outra conta para tudo, calado | a atualização dependia de o bilhete gravar; a pasta sem licença para Usuários | a atualização não depende do bilhete; a pasta do registro ganha Usuários: Modificar no passo da pergunta única, pela mesma função | `test_m4_o_bilhete_que_nao_grava_...` (lá: nada procurado), `test_m4_a_pergunta_unica_...` (lá: só a raiz); de verdade: `test_m4_de_verdade_...` |
| M5 o bilhete preso reabre sem trocar; duas janelas | a anotação feita depois de fechar; o reabrir sem olhar a outra janela | nada é anotado antes de trocar; com outra janela aberta no fechar, não reabre | `test_m5_o_bilhete_preso_...` (lá: não trocou), `test_m5_outra_janela_...` (lá: reabriu) |
| M6 motor novo calado para sempre | nada dizia; o download do motor é outro trabalho | a frase da D-843 uma vez + registro | `test_m6_...` (lá: nada na tela) |
| M7 contar pelo nome | o processo sem caminho legível contava como "rodando"/"outra janela" | `caminho_conferido` (uma leitura só): o `Update.exe` sem caminho é "não deu para saber" (a abertura segue); o processo sem caminho na conferência é "não deu para conferir" (frase da D-845), nunca "outra janela" | `test_m7a_...` (lá: `True`), `test_m7b_...` (lá: `outra_janela=True`) |
| M8 o título | sem decisão | D-846: "Atualização" | `test_m8_...` (lá: "Versão nova do programa") |
| M9 cinco proteções sem teste | falta de teste (D-827) | V3 virou o M7 a; V9, V10, V11, V13 ganharam teste | `test_m9_*` (passam lá: a proteção existia); a prova é a rodada de mutações |
| L1 testes no ProgramData de verdade | a configuração comum não trocava o PROGRAMDATA | `tests/conftest.py` troca, como o LOCALAPPDATA | `test_l1_...` (lá: o registro em `C:\ProgramData`) |
| L2 o laço da D-841 empilhava | a caixa seguinte abria por dentro da anterior | a conferência por trás: a caixa seguinte vem pela fila do Qt | `test_l2_...` (lá: parou em 138 de 200) |
| L3 erro fora do previsto não reabria | `_trocar` não pegava | vira "não pedida" → reabre com a frase | `test_l3_...` (lá: não reabriu) |
| L4 bilhete regravado em toda abertura | `estado_aceita_gravacao` e a anotação da troca | a abertura só lê; escreve só reprovação e frase, pela escrita única | `test_l4_...` (lá: 2 gravações); o resto: pergunta 4 |

## As mutações (D-827)

`volta3-provas/mutacoes_volta3.py`, numa cópia do ramo (`git archive`), com os 14 arquivos de teste do atualizador:
as do implementador (`mutacoes.py`), as 17 do primeiro "quem tenta quebrar", as 26 V do segundo e 28 novas.
Antes de tudo, sem mutação nenhuma, os 14 arquivos juntos passam (2537 casos): sem isso "acusada" não quer dizer nada.
A primeira tentativa achou que não passavam juntos (as frases "já vistas" vazavam de um teste para o outro, pela pasta
de dados da conta): consertado no ajudante dos testes, e a conferência sem mutação ficou no executor.

- **Rodada inteira** (`volta3-provas/mutacoes_volta3-resultado.txt`): **93 acusadas, 3 sobreviveram, 7 saíram com o
  desenho (cada uma com o porquê e o teste que cobra o contrário), 0 erros.** Das de antes, todas as que continuam
  existindo foram acusadas, no trecho de antes ou no equivalente do código novo (escrito ao lado de cada uma). As que
  saíram: as da anotação da troca e do "sem o bilhete nada anda" (V1, V14, V15, V16, M4 duas vezes, Q17), que a emenda
  mandou tirar. As 3 que sobreviveram eram proteções novas minhas sem teste (N26: a última boa precisa da assinatura ao
  lado; N27: a assinatura da versão que chega é guardada; N28: sem licença nem se pergunta ao Velopack).
- **A N27 achou um defeito de verdade no meu código:** a assinatura guardada era gravada como texto, e o Windows trocava
  cada fim de linha; uma assinatura publicada com fim de linha do Windows deixava de ser lida, e a versão nova não
  virava a última boa sem internet. Consertado (gravada e lida byte por byte) e com teste
  (`test_n27_a_versao_nova_vira_a_ultima_boa_sem_internet`, que falhava antes do conserto).
- **Segunda rodada, com os três testes** (`volta3-provas/mutacoes_volta3-resultado-segunda-rodada.txt`): **3 de 3
  acusadas.** No total: **96 acusadas, 0 sobreviventes.**

## Ressalvas

1. **A máquina de estados não perdeu fase; ganhou uma (GUARDANDO).** A emenda diz "perde fases". O que saiu foi a
   dependência do bilhete (TROCANDO), o embrulho `conferir_troca`, os efeitos `AnotarFalha`, `AnotarOk` e
   `PedirParaFecharAOutraJanela`, e a volta pela internet (VOLTANDO é um passo local). GUARDANDO existe porque guardar
   a última boa é um passo com resultado conferido (a soma), e o que vem depois depende dele (§11.12 ponto 2).
2. **Um arquivo novo, para a gerente conferir se é o "arquivo novo de controle" que a emenda proíbe:** a assinatura da
   versão que está chegando é guardada em `ultima-boa\` ao ser conferida (antes de baixar), para a versão virar a
   última boa depois do teste sem precisar de internet. Nada decide pela existência dela sozinha (a última boa é a
   versão com o pacote E a assinatura). Sem ela, a guarda busca a assinatura na internet. A pasta `ultima-boa` em si
   é a da emenda ("ultima-boa.nupkg").
3. **Sem a assinatura da versão instalada** (a primeira abertura depois do `.msi`, sem internet), a guarda não dá, e o
   teste rápido roda por trás a cada abertura até dar (segundos de processador, nada na tela). O mesmo se o pacote da
   versão que roda sumir de `packages\`. Ver pergunta 5.
4. **Não rodei o atualizador do Velopack de verdade aplicando a volta** (ele mexe na pasta e reabre): só a cópia e a
   conferência dele, de verdade. A troca de verdade fica para a prova à vista (D-767, D-785).
5. **A conta do Kaique e o `.msi`:** as ressalvas antigas (conta padrão; "Programas e Recursos" com a versão do
   instalador) continuam.
6. **Velocidade:** a abertura comum não ganhou trabalho na frente da janela (uma lista de pasta e a leitura do pacote
   esperando, que não usa a rede). Depois de cada versão aprovada, uma cópia de 460 MB por trás, uma vez. Não rodei o
   filtro de velocidade (é da gerente; mexi em `core/`).
7. **Os leves 8 a 12 da volta 1** (que o relatório 2 lembra que o Kaique veria) não eram desta tarefa; o leve 12 (os
   segundos sem nada na tela no teste rápido depois da troca) continua; os outros mudaram de forma com a emenda.
8. **O teste do M3 com o motor** usa o motor do programa fora do lugar (a conferência pergunta pelo motor que a versão
   pede; nos testes, a pergunta de mentira responde pelo mesmo interruptor).
9. **Um teste chama o despachante de dentro da peça** (`test_m4_a_pergunta_unica_da_a_licenca_tambem_a_pasta_do_registro`
   usa `getattr(windows, "_fazer_passo")`): é o único jeito de ver as duas pastas do passo sem a licença de
   administrador. A regra "ninguém usa o que tem sublinhado" (`test_windows_peca`) não olha o `getattr`; a gerente decide
   se isso é aceitável ou se prefere só a prova à vista para esse ponto.
10. **Dois processos testando ao mesmo tempo** (o atalho clicado nos segundos em que a reabertura sem janela testa):
   os dois reprovam a mesma versão (o bilhete fica igual) e os dois pedem a volta; um deles pode não conseguir (a
   tranca do Velopack) e mostrar a frase (3) antes de o Velopack fechá-lo. Raro; não provado; parte da pergunta 4.

## Perguntas para o Samuel (§11.13)

**1. As palavras do "Não deu para atualizar agora".** É a caixa "Atualização" que aparece quando o Kaique clica
"Reiniciar agora" e o programa não pode trocar a versão naquela hora (o texto que o senhor aprovou: "Não deu para
atualizar agora: [motivo]. Tente ao fechar o programa."). O motivo é texto de tela que o senhor ainda não viu. Situação:
já está no programa de teste, esperando o seu "sim". Os motivos, e quando cada um aparece:
- "o arquivo da versão nova sumiu do computador" (um antivírus o tirou depois de baixar);
- "o arquivo da versão nova está incompleto" (o pacote não diz que motor ele precisa);
- "falta no computador uma peça que a versão nova precisa" (o motor de leitura de texto dela saiu do lugar);
- "o Windows não mostrou quais programas estão abertos";
- "há um programa aberto que pode ser outra janela do Editor de Impressão" (o Windows não deixa conferir se é dele);
- "o programa não conseguiu fechar";
- "o atualizador do programa não começou";
- "a versão nova ainda não terminou de chegar";
- "aconteceu um erro inesperado".
Exemplo: "Não deu para atualizar agora: o Windows não mostrou quais programas estão abertos. Tente ao fechar o
programa." **O que o senhor escolhe:** (A) aprovar como estão (sugestão); (B) mudar algum (escreva qual); ou só
comentário. Nada do que já funciona muda.

**2. O arquivo baixado que não bate com a sua assinatura, no "Reiniciar agora".** Acontece se alguém (outra conta do
notebook, um vírus) trocar o arquivo da versão nova depois de baixado. Hoje aparece a frase que o senhor já aprovou para
versão sem assinatura ("Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do Samuel. O
programa continua funcionando. Avise o Samuel."), e nada é trocado. A frase do "Não deu para atualizar agora" diria
"Tente ao fechar o programa", o que não adiantaria. **O que o senhor escolhe:** (A) fica a frase da assinatura
(sugestão); (B) a do "Não deu para atualizar agora". É defeito raro, não escolha do dia a dia.

**3. Um programa de outra conta com o nome do atualizador.** Quando o Kaique abre o programa pelo atalho enquanto há uma
versão nova esperando, o programa olha se o atualizador está trocando a versão naquele instante (se estiver, ele não
abre, para não ser fechado no meio). Se aparecer um programa com o mesmo nome do atualizador que o Windows não deixa
conferir (de outra conta), antes o programa não abria, sem dizer nada, enquanto aquele rodasse; agora abre normalmente
(no pior caso, o atualizador de verdade o fecha, como já acontecia antes da volta 2). **O que o senhor escolhe:**
(A) abrir (sugestão; é o que está feito); (B) não abrir. Só comentário também vale.

**4. Dois "pedaços" do programa anotando ao mesmo tempo.** O caderninho da atualização (as versões que falharam no
teste e a frase a mostrar uma vez) agora só é escrito quando há o que anotar, e a anotação que se perdia (a da troca em
andamento) não existe mais. Sobra um caso raro: dois pedaços do programa anotando no mesmo instante; um pode apagar a
anotação do outro. O efeito para o Kaique: uma frase de aviso que não aparece, ou uma versão estragada oferecida de novo
(e devolvida de novo em segundos). Não provado. **O que o senhor escolhe:** (A) deixo para depois (sugestão); (B)
consertar agora (precisaria de uma tranca entre os pedaços, que o Fable pediu para não pôr).

**5. O teste da versão instalada sem internet no primeiro dia.** Na primeira vez que o programa abre depois de
instalado, ele testa a versão por trás e guarda uma cópia dela (para poder voltar a ela no futuro). Para guardar, ele
confere a sua assinatura, que vem da internet. Sem internet, ele repete o teste por trás a cada abertura (alguns
segundos de processador, nada na tela) até conseguir. **O que o senhor escolhe:** (A) deixo assim (sugestão; some no
primeiro dia com internet); (B) pôr a assinatura da versão dentro do instalador (mexe no publicar; outro trabalho).

## Ideias para a Lista de espera

- Pôr a assinatura da versão no instalador (resolveria a pergunta 5 de vez).

## Bugs para a Lista de bugs

- Nenhum fora do que está acima.


# Volta 2b: as frases D-839 e D-840 (24/11/2026)

Implementador. Pedido da gerente de 24/11: pôr no atualizador novo as duas frases que o Samuel decidiu (respostas às
perguntas A e B da volta 2, logo abaixo). Não abri agente nem janela. **Situação: feito; os testes dos arquivos que toquei passam no meu PC; falta a rodada do GitHub (é da gerente).**

## Decisões que esta tarefa precisa cumprir

- **D-839** (chat 24/11, à pergunta "Aceita as duas sugestões, a frase da 1 e a minha da 2?": "sim"): quando o Windows
  não deixa trocar a versão e o programa nunca saiu da de antes, a frase é "A atualização não deu certo. O programa
  continua na versão de antes e funcionando. Avise o Samuel." As três da D-778 ficam iguais; a (1) "voltou para a
  versão anterior" fica só para quando a versão nova entrou, falhou e o programa voltou.
- **D-840** (a mesma resposta, "sim"): "Reiniciar agora" com outra janela do programa aberta não troca e mostra a frase
  curta "Feche a outra janela do programa e clique de novo." O programa continua aberto; ao fechar, vem a pergunta
  "Atualizar agora?" (D-831, D-835).
- Em volta: D-778 (as três frases, iguais), D-831/D-835 (a pergunta ao fechar, igual), §11.7 (nenhum outro texto,
  botão ou comportamento), §11.8, §11.12.

## O que já está escolhido e testado aqui

- As três frases da D-778 e os textos da D-835: `test_atualizador_novo::test_d835_e_d778_os_textos_da_tela_palavra_
  por_palavra`, `test_decisoes_atualizacao::test_d719_*`. A linha "troca" desse dicionário e o
  `test_atualizador_volta2::test_leve1_a_frase_da_troca_espera_a_resposta_do_samuel` cobram a frase (1) na falha
  "troca": a D-839 mudou essa frase, então essas duas linhas passam a cobrar a frase nova (anotado na lista D-836).
- O "Reiniciar agora" que não pode trocar não fecha a janela e a pergunta vem ao fechar (volta 2, M1):
  `test_atualizador_volta2::test_m1_*`, a tabela de `test_fases_da_atualizacao.py`. Continua igual.

## Como fica para quem usa e no livro

- D-839: o Kaique vê, numa vez só, a caixa "Atualização" com a frase nova, em vez de "voltou para a versão anterior",
  quando a troca não aconteceu. Nada mais muda. O PDF não muda.
- D-840: com o programa aberto duas vezes, ele clica "Reiniciar agora" no aviso da versão nova: nada fecha e aparece
  uma caixa com "Feche a outra janela do programa e clique de novo." (botão de fechar a caixa). O programa continua
  aberto; ao fechar, vem "Atualizar agora?" como já vinha. O PDF não muda.

## Como cumpri cada uma (caminho -> função)

- **D-839.** A frase sai do dicionário único `atualizacao.FRASES_DA_FALHA` (a linha da falha "troca" passou a ser
  `FRASE_DA_FALHA_SEM_TROCA`, palavra por palavra); as três da D-778 não mudaram. Os caminhos que chegam nela:
  - a abertura com janela em que a troca não aconteceu (o Velopack reabriu a de antes, ou o atalho depois de a troca
    acabar) -> `fases._ao_abrir` -> `MostrarFalha("troca")` -> `Atualizacao._para_a_tela` -> `PonteDaTela._mostrar`
    -> `FRASES_DA_FALHA`;
  - a reabertura sem janela do "Sim" ao fechar -> `AnotarFalha("troca")` -> a abertura seguinte -> `_falha_a_mostrar`
    -> o mesmo `MostrarFalha` e o mesmo dicionário.
  A (1) continua só na falha "teste" (a versão nova entrou, não passou e voltou).
- **D-840.** A frase vem da conferência única da troca. `Atualizacao.conferencia_da_troca` (o corpo que era o
  `conferir_troca`, sem mudar uma conferência) devolve o evento `TrocaConferida`, que ganhou `outra_janela`: verdade só
  no "há outra janela do programa aberta" da lista de processos. A regra (`fases.proxima_fase`, CONFERINDO_TROCA) põe o
  efeito novo `PedirParaFecharAOutraJanela`, e a ponte da tela mostra `FRASE_DA_OUTRA_JANELA`. A fase continua DEPOIS:
  nada fecha, e a pergunta "Atualizar agora?" vem ao fechar, como já vinha. Caminhos:
  - "Reiniciar agora" -> `Escolheu(True)` -> `ConferirTroca` -> `conferencia_da_troca` -> `TrocaConferida` -> a regra
    -> a frase;
  - `trocar_para` (o "Sim" ao fechar, a volta, e a segunda conferência depois de a janela fechar) -> `conferir_troca`,
    que agora só mostra a mesma `conferencia_da_troca` como (pode, motivo, recusada). Conta própria: nenhuma.
  Nos outros "não pode trocar agora" (o Windows não deu a lista; o motor fora; o pacote não está lá) nada aparece, como
  antes (§11.7: a decisão fala de outra janela aberta).

## O teste que falhava antes

`tests/test_decisoes_atualizacao.py`: `test_d839_a_troca_que_nao_aconteceu_diz_que_continua_na_versao_de_antes`
(os dois caminhos), `test_d839_as_tres_frases_da_d778_continuam_iguais`, `test_d840_reiniciar_agora_com_outra_janela_
aberta_diz_para_fechar_e_nada_fecha`: **os 4 falham no código de `63bd8546`** (rodados antes de mexer no programa:
`relatorios/atualizador-novo/volta2b-testes-no-codigo-antigo.txt`) e passam agora. `test_d840_a_frase_so_aparece_com_
outra_janela_aberta` (2) passa nos dois: prova que os outros casos não mudaram. Rodam pela regra, pelo executor e pela
ponte da tela de verdade; só o Windows e o Velopack são de mentira (a lista de processos responde "outra janela").

Os dois testes antigos que cobravam a frase (1) na falha "troca" passaram a cobrar a frase nova (a decisão mudou; a
gerente liberou o primeiro; o segundo é a mesma linha): `test_atualizador_volta2::test_leve1_...` e a linha "troca" de
`test_atualizador_novo::test_d835_e_d778_...`. Anotados em `lista-dos-testes-d836.md`. A prova de quem tentou quebrar
(`quem-tenta-quebrar-1/provas/test_qtq_provas.py`, linha 128, fora de `tests/`) mostrava o defeito e agora falha nessa
linha, como devia; não mexi nela.

## Ressalvas

1. **"clique de novo"**: depois da frase, nesta abertura o aviso "Reiniciar agora" não volta (a decisão diz "ao fechar,
   vem a pergunta"). Então o "clique de novo" só pode ser no "Sim" da pergunta ao fechar, ou no aviso da próxima
   abertura. Fiz como a decisão diz; se o Samuel esperava o aviso de volta para clicar, é outra decisão.
2. **O título da caixa da D-840** é o do aviso da versão nova ("Versão nova do programa"), de onde veio o clique. Não é
   texto novo; a decisão não diz o título.
3. Se a outra janela for aberta nos segundos entre a conferência e o fechar, a segunda conferência (`trocar_para`)
   recusa e o programa reabre (como na volta 2, M1), sem a frase: a decisão é sobre o clique.
4. Não rodei as 32 mutações de novo (a 9, "outra janela aberta não troca", acha a mesma linha `if outras:`).
   Rodei três novas, à mão (o arquivo voltou depois de cada uma): tirar o `outra_janela` da conferência, tirar a
   frase da regra, e voltar a frase (1) na falha "troca": as três acusadas pelos testes novos.

## Os testes no meu PC (um arquivo por vez, a pasta temporária no D:)

`test_decisoes_atualizacao` 41, `test_fases_da_atualizacao` 1012, `test_atualizador_volta2` 32,
`test_atualizador_novo` 35, `test_decisoes_ajudante_da_atualizacao` 22, `test_decisoes_desinstalar` 45,
`test_decisoes_desinstalar_pasta` 6, `test_decisoes_testes_a_distancia` 13, `test_decisoes_preparo_d749` 3,
`test_decisoes_brasao` 20, `test_trava_windows` 42 + 3 pulados, `test_porteiro_licenca_que_acrescenta` 14,
`test_conferencias_codigo` 122, `test_conferencias_excecoes` 14, `test_windows_peca` 68 + 3 pulados,
`test_windows_preparo_do_computador` 19 + 1 pulado: **todos passaram**. O porteiro: "nada novo (4997 arquivos
lidos; a lista deixa 135 lugares)". O GitHub não foi disparado (pedido da gerente).

## D-841 (segunda volta, 24/11/2026)

- **A decisão** (chat 24/11, à opção "depois da frase, o aviso 'Reiniciar agora / Depois' aparece de novo"): "1, desde
  que seja a volta à fase 'pronta', sem espera nem peça nova." Era a ressalva 1 de cima.
- **Como cumpri:** na regra (`core/fases_da_atualizacao.py`, CONFERINDO_TROCA), o `TrocaConferida` com `outra_janela`
  volta à fase PRONTA no mesmo evento, com os efeitos: o registro, `PedirParaFecharAOutraJanela` (a frase) e
  `MostrarVersaoNova` (o mesmo aviso de sempre). Nenhum efeito, peça, tela, espera ou temporizador novo. Fechada a outra
  janela, o "Reiniciar agora" passa pela mesma conferência e troca; "Depois" leva à pergunta ao fechar (a fase PRONTA e
  a DEPOIS já levavam). Os outros "não pode agora" continuam em DEPOIS, sem nada na tela.
- **Como fica para quem usa:** com o programa aberto duas vezes, o Kaique clica "Reiniciar agora", lê "Feche a outra
  janela do programa e clique de novo.", fecha a caixa e o aviso da versão nova aparece de novo. Se ele fechou a outra
  janela, "Reiniciar agora" fecha esta, grava o trabalho e troca. Se não fechou, a frase volta. O PDF não muda.
- **Caminho -> função:** "Reiniciar agora" -> `Escolheu` -> `ConferirTroca` -> `conferencia_da_troca` ->
  `TrocaConferida(outra_janela)` -> `proxima_fase` -> PRONTA + a frase + `MostrarVersaoNova` -> `PonteDaTela._mostrar`
  (os dois ramos que já existiam). O segundo clique é o mesmo caminho.
- **A prova:** `tests/test_decisoes_atualizacao.py::test_d841_depois_da_frase_o_aviso_volta_e_com_a_outra_fechada_troca`
  (pela regra, pelo executor e pela ponte da tela de verdade): **falha em `4f542399`** (lá, depois da frase, o aviso não
  voltava: `relatorios/atualizador-novo/volta2b-d841-teste-no-codigo-antigo.txt`) e passa agora.
- **Testes que mudaram porque a decisão mudou** (anotados na lista D-836):
  - a linha da tabela que eu tinha posto na entrega anterior, `(CONFERINDO_TROCA, conferida_outra_janela)`: de DEPOIS
    para PRONTA com o aviso (a regra não ganhou transição nova, a minha mudou);
  - o meu `test_d840_reiniciar_agora_com_outra_janela_...`: agora espera o aviso de novo depois da frase e responde
    "Depois";
  - **um antigo:** `test_atualizador_volta2::test_m1_reiniciar_agora_que_nao_pode_trocar_nao_fecha_a_janela` cobrava a
    fase DEPOIS depois do "Reiniciar agora" com outra janela; a decisão manda PRONTA. Mudei só essa linha. O resto
    dele (não fecha, não troca, a pergunta vem ao fechar) continua igual e passa.
- **Ressalva:** se o Kaique clicar "Reiniciar agora" de novo sem fechar a outra janela, a frase e o aviso voltam, quantas
  vezes ele clicar (cada vez é um clique dele; "Depois" sai do ciclo).
- **Os testes no meu PC** (os mesmos 16 arquivos da entrega anterior, um por vez): todos passaram (test_decisoes_atualizacao 42; os outros com os mesmos números de antes). O porteiro: "nada novo (4998 arquivos lidos; a lista deixa 135 lugares)". O GitHub não foi disparado.

# Volta 2: os achados do quem tenta quebrar (24/11/2026)

Implementador. Pedido da gerente de 24/11 (D-815, segunda e última volta), sobre o relatório
`relatorios/atualizador-novo/quem-tenta-quebrar-1/relatorio.md` (commit `3065d828`): 1 grave, 5 médios, 12 leves.
Regra desta volta: para cada achado, a CAUSA, a regra que decide e todos os caminhos que chegam nela, antes do conserto;
o conserto muda a regra num lugar só. Li o relatório inteiro, as provas (`test_qtq_provas.py`, `mutacoes_qtq.py`,
`prova_porteiro_k03.py`) e, de novo, o Velopack 1.2.161 nas linhas que ele cita. Não abri agente nem janela.

**Situação: consertados G1, M1, M2, M3, M4 e os leves 2, 3 (com teste), 4 (só o texto; a decisão vai em pergunta), 6 e
7. O leve 1 (a frase da falha "troca") precisa de frase nova: PAREI e está em "Perguntas para o Samuel". M5 não é
comigo. Os leves 5 (= M3), 8, 9, 10, 11 e 12: anotados abaixo com o porquê.** Último commit: ver a mensagem de entrega.

## Os testes no meu PC depois da volta 2 (um arquivo por vez, a pasta temporária no D:)

79 arquivos: os do atualizador (os novos e os da volta 2), a trava, a peça do Windows, a janela de prova, o porteiro e
as provas dele (`test_conferencias_codigo`, `_excecoes`, `_pacote`, `_protecao`), o publicar, o motor e os 64
`test_decisoes*.py`: **2473 passaram, 17 pulados, 1 falhou uma vez**: de novo o intermitente
`test_decisoes_desfazer_pagina.py::...[marcar]` (longe do atualizador; passou nas 3 vezes seguintes; está nos "Bugs para
a Lista de bugs" da seção do código). O porteiro: "nada novo (4997 arquivos lidos; a lista deixa 135 lugares)".

## Os testes de cada achado: falham no código de antes, passam agora

`tests/test_atualizador_volta2.py` (32 testes). Rodado com os arquivos do programa de `cd4b8414` no lugar (e devolvidos
depois): **20 falham** (`relatorios/atualizador-novo/volta2-testes-no-codigo-antigo.txt`); os 12 que passam lá são os
do M3 (as proteções já existiam; os testes provam que desligá-las é acusado) e um de "nada mudou" (o G1 no caso em que a
troca acabou). No código de agora: **32 passam**.

As mutações: as minhas (`mutacoes.py`, agora 32 com as da volta 2) **32 de 32 acusadas**; as 17 dele, de novo, com os
arquivos de teste do atualizador mais os da volta 2 (`mutacoes_qtq_no_lugar.py`, a mesma lista importada do arquivo
dele): **0 de 17 sobreviveram** (`mutacoes_qtq_no_lugar-resultado.txt`; a Q4 com o trecho do código novo, porque a linha dela mudou com o conserto do M2).

---

## G1 — abrir pelo atalho no meio da troca anotava uma falha que não houve

- **Causa:** a regra lia "roda a versão de antes, com uma troca anotada" como "a troca não aconteceu", sem separar "a
  troca ainda está acontecendo". O dado do disco (`tentando`) não prova o fim da troca.
- **Como saber se a troca está em curso, com a fonte (Velopack 1.2.161):** o atualizador do Velopack (`<raiz>\Update.exe`)
  é aberto pelo pedido da troca e vive até reabrir o programa: espera o programa sair (`util_common.rs` 14-26), mostra a
  janelinha e abre o pacote, fecha à força o que roda da pasta e renomeia (`apply_windows_impl.rs` 134-176), reabre
  (`apply.rs` 47-75: na falha também, com os mesmos argumentos) e sai. O atalho só abre o `Update.exe start`, que abre
  `current\` e volta logo (`stub.rs` 32-39; `start_windows_impl.rs` 111-133: `spawn` e fim, sem esperar). Logo:
  **o atualizador do Velopack desta instalação rodando = a troca em curso.** A tranca `.velopack_lock` não serve sozinha:
  ela só é pega depois da espera pelo programa (`apply_windows_impl.rs`, depois do teste de elevação), e o clique no
  meio da espera passaria. A linha de comando da reabertura (`--conferir-a-versao-nova`) só chega depois de a troca
  acabar (`apply.rs` 47-75), então quem a tem nem pergunta.
- **A regra:** `core/fases_da_atualizacao.py`, `_ao_abrir` (o lugar único de "o que a abertura faz com uma troca anotada").
- **Os caminhos que chegam nela:** toda abertura do programa instalado (`atender_linha_de_comando` → `Atualizacao.abrir`
  → `Abriu`), com a troca vinda da linha de comando (o Velopack reabriu) ou da anotação do disco (o atalho; ou o
  Velopack que não reabriu); e as duas trocas (normal e volta).
- **O conserto (num lugar só):** `Abriu` ganha `troca_em_curso` (True / False / None), que o executor lê pela peça do
  Windows (`windows.atualizador_do_velopack_rodando`, nova, pela lista de processos de sempre) só quando a troca veio do
  disco e a versão que roda é a de antes. Na regra, antes de concluir "não aconteceu": em curso → nada anotado, sai sem
  janela (o Velopack fecharia esta à força; o Velopack reabre a nova no "Reiniciar agora"); sem saber → nada anotado, a
  abertura segue e a próxima decide; parado → como antes (falha "troca"). Vale para a troca e para a volta.
- **Testes:** `test_g1_abrir_pelo_atalho_no_meio_da_troca_nao_anota_falha_e_sai_sem_janela` (era o `test_A`),
  `test_g1_sem_saber_se_a_troca_acontece_nada_e_anotado` (era o `test_A2`), `test_g1_a_troca_que_acabou_sem_trocar_
  continua_sendo_falha` (o que já funcionava), e na tabela da regra `abriu_troca_em_curso`, `abriu_volta_em_curso`,
  `abriu_troca_sem_saber`.
- **O que fica de fora (a D-770 é de depois, D-828):** no "Sim" ao fechar, o clique no atalho no meio da troca não abre
  nada no fim (a D-769: nada abre; o clique se perde e o Kaique clica de novo depois da janelinha do Velopack). A D-770
  ("o programa abre sozinho no fim") continua "para depois", como a D-828 diz.

## M1 — "Reiniciar agora" fechava antes de conferir; se não pudesse trocar, o programa sumia calado

- **Causa:** a conferência da troca (o pacote, o motor, outra janela) só existia DENTRO do pedido (`trocar_para`), e o
  "Reiniciar agora" fechava a janela antes de chegar nele. Nada reabria o programa quando o pedido falhava depois.
- **A regra:** a conferência única da troca, agora uma função só (`Atualizacao.conferir_troca`), usada antes de fechar e
  de novo dentro de `trocar_para`; e, na regra, o que fazer quando a troca do "Reiniciar agora" não é pedida.
- **Os caminhos:** "Reiniciar agora" (`Escolheu(True)`), "Sim" ao fechar (`RespondeuAoFechar(True)`) e a volta
  (`Voltar`); os três chegam a `trocar_para`, que chama `conferir_troca`.
- **O conserto:** "Reiniciar agora" → fase nova `CONFERINDO_TROCA` → efeito `ConferirTroca` → `TrocaConferida`: pode →
  fecha a janela e troca; não pode → a janela continua aberta e vira "Depois" (a pergunta vem ao fechar); recusada (a
  soma) → a falha "recusada" com a frase 2. O que só falha DEPOIS de fechar (o Velopack recusou o pedido, ou a
  conferência mudou nos segundos do fechar) → efeito `ReabrirOPrograma`: o programa é aberto de novo pela peça do
  Windows (`lancar_solto`, que só dá certo com o sinal de vida do programa aberto: `--sinal-de-vida`, atendido antes de
  tudo em `atender_linha_de_comando`). Nenhuma frase nova, nenhum botão novo. No "Sim" ao fechar o programa ia fechar
  mesmo: só fica anotado, e o aviso volta na próxima abertura (como antes).
- **Testes:** `test_m1_reiniciar_agora_que_nao_pode_trocar_nao_fecha_a_janela` (era o `test_B` e o `test_E`),
  `test_m1_a_troca_que_falha_depois_de_fechar_reabre_o_programa`, `test_m1_o_sinal_de_vida_e_dado_antes_de_tudo`, e na
  tabela `conferida_pode`/`conferida_nao`/`conferida_recusada` e `test_m1_a_troca_do_reiniciar_que_nao_foi_pedida_
  reabre_o_programa`.
- **Pergunta (o que o Kaique vê):** com outra janela do programa aberta, o "Reiniciar agora" agora não fecha nada e não
  diz nada (a pergunta vem ao fechar). Está em "Perguntas para o Samuel" (se quer uma frase ali).

## M2 — a volta conferia o motor da versão que falhou; ninguém lia o `motor-exigido.json`

- **Causa:** "o motor está no lugar" respondia sempre pelo motor que O PROGRAMA QUE RODA pede (`VERSAO_DO_MOTOR` deste
  `.exe`), e não pelo da versão que vai entrar. O pacote de cada versão traz o `motor-exigido.json`, e nada o lia.
- **A regra:** `motor_esta_no_lugar(raiz, versao_do_motor)` (a única do "motor no lugar", agora por versão de motor) e
  `motor_exigido_pelo_pacote(arquivo)` (a única leitura do `motor-exigido.json`, de dentro do pacote já conferido pela
  soma assinada).
- **Os caminhos:** antes de anunciar (depois de baixar a versão nova: `Baixou(motor_da_nova)`), antes de trocar
  (`conferir_troca`: o "Reiniciar agora", o "Sim" ao fechar e a volta), e na abertura (`GarantirMotor`: o motor que o
  programa que roda pede, que ele mesmo precisa; não mudou).
- **O conserto:** anunciar e trocar perguntam pelo motor da versão QUE ENTRA (lido do pacote dela). Pacote sem o arquivo
  ou estragado: não se sabe, não troca. A volta para a anterior pergunta pelo motor da anterior (que continua na pasta
  dele: `garantir_o_motor` nunca apaga outra versão de motor).
- **Testes:** `test_m2_a_volta_confere_o_motor_da_anterior_e_volta` (era o `test_C`),
  `test_m2_a_versao_nova_sem_o_motor_dela_nao_e_anunciada`, `test_m2_o_motor_exigido_e_lido_de_dentro_do_pacote` (e o
  nome de dentro do pacote igual ao do `empacotar.py`), e na tabela `baixou_sem_o_motor_da_nova`.

## M3 — nove proteções que nenhum teste acusava (Q1-Q5, Q7, Q8, Q14, Q15)

- **Causa:** os testes do motor do conserto 4 (`tests/test_atualizador_4.py` do `atualizador-4`), que o plano dizia
  trazer, não vieram; e as outras proteções só tinham a peça de mentira em volta.
- **O conserto:** um teste para cada uma, em `tests/test_atualizador_volta2.py`: Q1 `test_q1_conserto4_sem_espaco_nao_
  comeca`; Q2 `test_q2_conserto4_motor_estragado_nunca_fica_com_o_nome_final`; Q3 `test_q3_conserto4_o_motor_do_
  instalador_vai_para_o_lugar_dele`; Q4 `test_q4_conserto4_o_motor_no_lugar_e_a_mesma_conferencia`; Q5 `test_q5_a_
  pasta_que_existe_e_nao_aceita_gravacao_nao_conta_como_preparada` (a pasta do sistema, de verdade; pulado com a licença
  de administrador ligada); Q7 `test_q7_a_licenca_tem_de_chegar_ao_arquivo_de_dentro`; Q8 `test_q8_o_visual_c_que_uma_
  conta_comum_pode_trocar_nao_roda`; Q14 `test_q14_sem_a_lista_de_processos_nao_troca`; Q15 `test_q15_o_processo_cujo_
  caminho_nao_da_para_ler_conta` (o "System" de verdade). Do conserto 4 vieram também `motor_estragado_no_lugar_e_
  trocado`, `sem_o_arquivo_e_sem_o_motor_diz_e_nao_finge` e os 2 do médio 1 (o arquivo do motor estragado de qualquer
  jeito). Não vieram os que cobravam o ajudante (`rodar_ao_ligar`, `procurar_e_preparar`), que saiu: o "sem motor nada
  anunciado nem trocado" está nos testes do M2 e do 4a/4b.
- **Prova:** as 17 dele, de novo (acima).

## M4 — o estado que não gravava: a troca era pedida mesmo assim, e a falha sumia

- **Causa:** `gravar_estado` devolvia se gravou, mas `anotar_tentativa`, `anotar_falha`, `anotar_ok` e
  `apagar_tentativa` não olhavam, e `trocar_para` não olhava `anotar_tentativa`.
- **A regra:** "a atualização só anda se o que ela precisa anotar fica anotado": `estado_aceita_gravacao` (o teste de
  gravar o estado, pela gravação única) na abertura, e o resultado de `anotar_tentativa` em `trocar_para`.
- **Os caminhos:** a procura (só depois do motor, na regra), toda troca (`trocar_para`), toda falha (`anotar_falha`).
- **O conserto:** a abertura lê se o estado grava (`Abriu.estado_grava`); sem gravar, nada é procurado (na regra, um
  lugar só, depois do motor). `trocar_para` não pede a troca se a anotação não gravou. As quatro funções devolvem se
  gravaram, e o registro diz quando não. (O registro que cai no `erros.log` quando o `atualizacao.log` não aceita é
  como sempre foi; ver o leve 6.)
- **Testes:** `test_m4_com_o_estado_que_nao_grava_nada_e_procurado_nem_trocado` (era o `test_F`) e, na regra,
  `abriu_estado_nao_grava` e `test_m4_sem_o_estado_gravando_nada_e_procurado`.

## M5 — não é comigo (a gerente leva ao Samuel antes da entrega dos testes à distância). Nada mudou por ele.

## Os leves

1. **A frase da falha "troca" diz "voltou".** Precisa de frase nova (a D-778 não tem uma para "não trocou"): **PAREI**,
   pergunta para o Samuel abaixo. Até a resposta, fica a frase (1); o teste `test_leve1_a_frase_da_troca_espera_a_
   resposta_do_samuel` existe para a troca não entrar calada.
2. **A exceção da K03 mais larga que a D-837 — consertado.** Causa: a exceção aceitava a ferramenta em qualquer linha da
   função, com qualquer pedido; a busca por linha não via a palavra escrita em pedaços; e ninguém olhava quem chama a
   função. Regra: `k03` do porteiro (uma função). Conserto: na função da exceção só passa a LINHA DO EXPERIMENTO
   (`LINHA_DA_LICENCA_QUE_SO_ACRESCENTA`); qualquer outro pedido de licença ali é acusado; os textos escritos em pedaços
   ("ica" "cls", "a" + "b") são juntados e buscados em todo arquivo do programa (sem contar as docstrings); a função só
   pode ser chamada por `_fazer_passo` da peça. E a leitura de volta (`problemas_da_licenca_dos_usuarios`) passou a
   recusar qualquer linha a mais (Todos com Controle total, Usuários com Controle total). Testes:
   `test_leve2_o_porteiro_acusa_o_que_a_d837_nao_deixa` (os 4 casos da prova dele que passavam),
   `test_leve2_uma_licenca_a_mais_na_pasta_e_acusada`. A prova dele (`prova_porteiro_k03.py`) agora acusa os 5 casos (o
   "controle" dele também, porque não é a linha do experimento escrita igual).
3. **A família pelo número de quem abriu, sem a hora — consertado.** `familia_de` só aceita como filho quem nasceu
   depois do pai (`GetProcessTimes`, lido junto com o caminho). Teste: `test_leve3_a_familia_respeita_a_hora_em_que_cada_
   um_nasceu`.
4. **"Nenhum PowerShell" não era verdade.** O texto do `atualizacao.py` foi corrigido. O PowerShell que sobra é o da
   peça para LER a tarefa do ajudante antigo no passo 1 (`windows.apagar_tarefa` → `ler_tarefa`, pelo COM do Agendador,
   que separa "não existe" de "acesso negado" pelo número do Windows). Tirá-lo pede trocar a leitura de tarefas da peça
   (que os testes à distância também usam) por outra que não separa os dois casos: **PAREI**, pergunta abaixo.
5. = M3 (Q5): consertado com o teste.
6. **A afirmação do ONDE-PAREI sobre o `atualizacao.log` velho estava errada** (é da conta do Samuel, não do sistema):
   corrigida na seção do código (ver lá).
7. **Comentários que citavam o que saiu — consertado** (`core/testes_a_distancia.py`, só comentários; teste
   `test_os_comentarios_do_desfazer_nao_citam_o_que_saiu`).
8. **A corrida entre o aviso e o fechar:** risco sem prova. Não mexi: a regra já não pergunta ao fechar enquanto baixa
   (`Fechando` em BAIXANDO não faz nada); o que sobra é o aviso, que vem por sinal, chegar depois de a janela fechar.
   Consertar pede mudar quem marca a falha como vista (a tela), sem prova de que acontece; fica para a prova à vista.
9. **Sem o "Sim", sem o motor do Kraken:** é a D-749 (o motor só vai para o lugar com a pasta aceitando gravação); era
   igual no `atualizador-4`. Não mexi.
10. **Falha que nunca passa vira pergunta a cada abertura, sem aviso:** é a D-749 ("a pergunta volta"); uma frase nova
    seria decisão do Samuel. Não mexi (anotado para a prova à vista).
11. **Aberto "como administrador" conta como preparado:** risco sem prova; o teste de gravar é o mesmo que o Velopack
    usa. Não mexi.
12. **Segundos sem nada na tela depois da troca:** ressalva 3 do plano; medir na prova à vista. Não mexi.

## Caminho → função, o que mudou na volta 2

| Caminho | Antes | Agora |
|---|---|---|
| "Reiniciar agora" | `Escolheu` → `FecharJanela` → `Trocar` | `Escolheu` → `ConferirTroca` (`conferir_troca`) → `FecharJanela` → `Trocar` (`trocar_para`, que confere de novo) → se falhar, `ReabrirOPrograma` |
| A abertura com troca anotada | `Abriu` → falha "troca" | `Abriu(troca_em_curso)` → em curso: sai; sem saber: segue; parado: falha "troca" |
| Anunciar a versão nova | `Baixou` → aviso | `Baixou(motor_da_nova)` → sem o motor dela: nada |
| O motor antes de trocar | o motor do programa que roda | o motor que o pacote da versão que entra pede |
| Anotar | sem olhar se gravou | sem gravar: nada procurado; a troca não é pedida |

## O que já estava escolhido e testado, e o que mudou (§11.8)

Nenhum teste fora do atualizador mudou. Mudaram testes desta entrega (os meus, de 23/11), porque a regra que eles
descrevem mudou com os consertos: a tabela de `tests/test_fases_da_atualizacao.py` (linhas novas e as do "Reiniciar
agora"), a amostra da K03 em `tests/test_porteiro_licenca_que_acrescenta.py` (a linha do experimento escrita igual) e o
ajudante das provas (os pacotes de prova passaram a ter o `motor-exigido.json`; a peça de mentira ganhou o que a peça
nova tem). Tudo na lista da D-836.

## Perguntas para o Samuel (§11.13)

**Pergunta A — A frase quando a versão nova não chegou a entrar**
- *Do que se trata:* a janelinha de aviso que aparece quando a atualização não deu certo. Hoje há três frases (você
  escolheu em 18/11). Num caso que existe de verdade nenhuma serve: o Windows não deixou trocar a versão (um arquivo
  do programa estava preso, por exemplo pelo antivírus) e o programa ficou na versão de antes, funcionando.
- *O que acontece hoje:* aparece "A atualização não deu certo. O programa voltou para a versão anterior e continua
  funcionando. Avise o Samuel." Mas o programa não voltou: ele nunca saiu da versão de antes. É escolha minha de agente,
  feita sem perguntar; não é defeito do programa.
- *O que você escolhe:* (1) **sugestão:** uma frase própria para esse caso: "A atualização não deu certo. O programa
  continua na versão de antes e funcionando. Avise o Samuel."; (2) outra frase sua; (3) não mostrar nada nesse caso
  (fica só no registro que eu leio de longe); (4) só comentário.
- *O que muda no que já funciona:* só essa frase, nesse caso. As outras três ficam iguais. Situação: na versão de teste,
  esperando a sua resposta; até lá fica a frase de hoje.

**Pergunta B — "Reiniciar agora" com outra janela do programa aberta**
- *Do que se trata:* o aviso "Reiniciar agora / Depois" quando chega versão nova. Se houver OUTRA janela do programa
  aberta (o Kaique abriu duas vezes), a troca não pode acontecer (o atualizador fecharia a outra à força, com o trabalho
  dela).
- *O que acontece agora (depois deste conserto):* o "Reiniciar agora" não fecha nada e não diz nada; o programa continua
  aberto, e ao fechar vem a pergunta "Atualizar agora?". Antes do conserto, o programa fechava e sumia.
- *O que você escolhe:* (1) **sugestão:** fica assim, sem frase (nada novo na tela); (2) uma frase curta ao clicar,
  como "Feche a outra janela do programa e clique de novo."; (3) só comentário.
- *Situação:* na versão de teste.

**Pergunta C (para a gerente decidir se leva ao Samuel) — o PowerShell do passo 1**
- *Do que se trata:* na primeira abertura, a pergunta do Windows apaga a tarefa antiga do atualizador (só existe no seu
  PC). Para saber se ela existe, a peça do Windows usa o PowerShell do próprio Windows.
- *O risco:* num computador que bloqueia o PowerShell, esse passo falharia sempre, e a pergunta voltaria a cada abertura.
  O notebook do Kaique não bloqueia (os testes à distância também usam o PowerShell).
- *O que você escolhe:* (1) **sugestão:** fica como está, e a prova à vista confere no notebook; (2) trocar a leitura da
  tarefa por outra ferramenta do Windows que não separa "não existe" de "sem licença para ler" (mudaria a peça que os
  testes à distância usam); (3) só comentário.

---

# Atualizador novo: o código (23 e 24/11/2026)

Implementador. Ramo `atualizador-novo-2026-11-23`, worktree `.claude/worktrees/atualizador-novo`. Pedido da gerente de
23/11/2026: escrever o código do plano (seção "Atualizador novo: o plano", logo abaixo), com as respostas do Samuel
(D-834 a D-838) e as da gerente. Não abri agente nenhum, não rodei o programa com janela, não gerei instalador nem
versão, não disparei o GitHub e não mexi no PC fora da pasta do projeto.

**Situação: o código está escrito e os testes dos arquivos que toquei passam no meu PC, um arquivo por vez. Falta (é
da gerente): a rodada do GitHub, a revisão do Fable da lista dos testes, quem tenta quebrar e a prova à vista com o
Samuel.** Os dois testes fora do atualizador que quebravam pela lista de exceções menor foram adaptados com o "sim" do
Samuel (só o arquivo de exemplo). Último commit: ver a mensagem de entrega.

## Os testes no meu PC (um arquivo por vez; a pasta temporária do pytest no D:, ver o bug de baixo)

- Os 64 arquivos `tests/test_decisoes*.py`: **921 passaram, 5 pulados**; 1 falhou uma vez
  (`test_decisoes_desfazer_pagina.py::test_d621_cada_etapa_sozinha_volta_so_ela_so_nesta_pagina[marcar]`, os pontos da
  gravura marcada) e passou nas três vezes seguintes (sozinho e no arquivo inteiro): intermitente, longe do atualizador
  (ver "Bugs para a Lista de bugs").
- Os novos: `test_fases_da_atualizacao.py` 807, `test_atualizador_novo.py` 35, `test_windows_preparo_do_computador.py`
  19 + 1 pulado (o de verdade; rodado à parte com `EDITOR_PROVA_DO_WINDOWS=1`: passou), `test_velopack_de_verdade.py` 3,
  `test_porteiro_licenca_que_acrescenta.py` 14.
- Os dos arquivos que toquei ou que os usam: `test_trava_windows.py` 42 + 3 pulados (as pendências), `test_windows_peca.py`
  68 + 3 pulados, `test_windows_janela_de_prova.py` 10, `test_conferencias_codigo.py` 122, `test_conferencias_excecoes.py`
  14, `test_publicar_versao.py` 125, `test_publicar_motor.py` 12, `test_empacotar.py` 43, `test_ocr_kraken.py` 28 + 5,
  `test_ocr_diagnostico.py` 6, `test_ocr_comparar.py` 16 + 23, `test_pasta_das_ferramentas.py` 17, `test_promessas.py`
  270 + 1 esperado, `test_nome_do_pacote.py` 5.
- `test_conferencias_pacote.py`: 26 passam, depois da troca do arquivo de exemplo dos 2 testes que quebravam (o "sim" do Samuel à sugestão (1), 24/11; ver "Perguntas para a gerente").
- O porteiro (`python -m regras_dos_agentes porteiro`): "nada novo (4981 arquivos lidos; a lista deixa 135 lugares)".
- As mutações: 20 de 20 acusadas (seção de baixo).

## O desenho, em uma frase

O único ato com licença é dar à pasta do programa a licença de Modificar para Usuários, uma vez, na primeira abertura,
ANTES da janela (com o ajudante antigo apagado, o Visual C++ e o Inno antes dela, na mesma pergunta). Depois, o
programa, na conta do Kaique, procura só ao abrir, confere a assinatura e o motor, baixa e pede ao Velopack para trocar;
o Velopack espera o programa sair, troca, mostra a janelinha dele e reabre. A regra é uma função pura
(`core/fases_da_atualizacao.py`); quem faz é o executor (`atualizacao.Atualizacao`); o Windows só pela peça
(`core/windows.py`); o Velopack só pela peça dele (`core/conversa_com_o_velopack.py`); a tela só traduz
(`ui/aviso_de_atualizacao.py`).

## Os arquivos

Programa: `atualizacao.py` (refeito, 2314 → ~900 linhas, sem PowerShell, sem `subprocess`, sem `ctypes`, sem `winreg`),
`core/fases_da_atualizacao.py` (novo), `core/conversa_com_o_velopack.py` (novo), `core/windows.py` (os três passos do
preparo, a licença que só acrescenta, as duas metades do pedido, a lista de processos, o dono do arquivo, as leituras
do Visual C++ e do Inno), `core/ocr_kraken.py` e `configuracoes.py` (do `atualizador-4`: o lugar do motor no instalado;
a marca do computador preparado saiu), `main.py` (só comentários), e a tela que a gerente liberou:
`ui/aviso_de_atualizacao.py` (refeito), `ui/janela_principal.py` (uma chamada no fechar e o comentário),
`ui/testes_a_distancia_ui.py` (a janela da senha não pergunta mais nada ao Windows), `ui/brasao_girando.py` (saiu a
espera da janelinha). E `janela_de_prova.py` (a janela de prova da peça usava o descritor da tarefa do ajudante,
`atualizacao.QUEM_PODE_MANDAR_RODAR`, que saiu: o mesmo texto passou a morar nela; era um bug que impedia, porque os 3
testes dela quebravam). Porteiro: `regras_dos_agentes/porteiro.py` (a única exceção da K03, D-837) e
`tests/conferencias_excecoes.json` (40 lugares tirados pelo `excecoes --diminuir`, nenhum acrescentado).

Testes novos: `tests/test_fases_da_atualizacao.py` (807 casos: toda fase com todo evento), `tests/test_atualizador_novo.py`
(35), `tests/test_windows_preparo_do_computador.py` (20; um só roda no GitHub ou com `EDITOR_PROVA_DO_WINDOWS=1`),
`tests/test_velopack_de_verdade.py` (3, a biblioteca de verdade), `tests/test_porteiro_licenca_que_acrescenta.py` (14),
`tests/ajudante_do_atualizador.py` (as peças de mentira da borda, um lugar só). As mutações:
`relatorios/atualizador-novo/mutacoes.py` e `mutacoes-resultado.txt`. Adaptados pela D-836: a lista teste por
teste em `relatorios/atualizador-novo/lista-dos-testes-d836.md` (e `.html`). A trava: `tests/test_trava_windows.py`.

## Decisões que esta tarefa precisa cumprir, e como cumpri cada uma

| Decisão | Palavras dele | Como cumpri | Prova |
|---|---|---|---|
| D-706, D-723 | "como funciona com apps" · "velopack" | o Velopack troca a pasta `current`; nada se reinstala | `test_d832_a_troca_usa_a_janelinha_do_velopack`; prova à vista |
| D-713, D-719 (token) | "não precisa ser privado" | GitHub público, só o endereço | `test_decisoes_atualizacao::test_d719_nenhum_token_dentro_do_programa` |
| D-714 | "1 - vamos seguir sua sugestão" | o publicar não mudou | `test_publicar_versao.py` (125 passam) |
| D-715, D-720 | "um aviso para salvar o trabalho atual e reinicializar" · "Sim" | o aviso com "Reiniciar agora" / "Depois", vindo da regra | `test_d715_...`, `test_d720_o_aviso_tem_reiniciar_agora_e_depois...`, `test_d720_reiniciar_agora_fecha_gravando...` |
| D-718, D-719, D-778 | "tem que avisar a gente" · "1" · "A" | teste rápido antes da janela; volta pela biblioteca com pacote assinado; as três frases, cada falha com a sua; o registro no ProgramData | `test_d718_teste_que_falha_volta_para_a_anterior_assinada`, `test_protecao_11_...`, `test_a_troca_que_nao_aconteceu_avisa_uma_vez`, `test_d835_e_d778_os_textos_da_tela_palavra_por_palavra` |
| D-724 | "o que é essa assinatura e é segura?" | assinatura antes de baixar; e a soma do arquivo baixado antes de trocar | `test_protecao_2_...`, `test_protecao_3_...`, os 4 `d724` adaptados |
| D-727 | "tudo no instalador" | o Visual C++ e o motor vêm do pacote; nada baixado na instalação | `test_d727_*` (iguais), `test_o_visual_c_confere_lendo_de_novo_depois_de_instalar` |
| D-732 | "não, faz quando o programa é aberto" | a procura nasce só da abertura; a janela não tem relógio | `test_d732_a_procura_e_so_ao_abrir_nada_roda_por_tras_depois`, a tabela da regra |
| D-733, D-735, D-741 | "1- sim" · "Sim" · "Sim" | uma pergunta só, a da abertura, com ou sem a senha; volta enquanto a pasta não aceitar gravação; nenhuma no "Reiniciar agora" | `test_protecao_1_...`, `test_d741_depois_do_nao_a_pergunta_volta...`, os `d735`/`d741` adaptados, `test_d733_reiniciar_agora_nao_pede_licenca` |
| D-736 | "o programa não precisa procurar versão nova" (conta de testes) | na conta de testes nada pergunta nem procura | `test_protecao_7_...`, `test_d736_aberto_por_teste_a_distancia...` |
| D-749 | "Sim" (pela metade = não feita) | a licença é o último passo; "preparado?" é o teste de gravar feito DE NOVO depois do trabalho, nunca o que ele disse | `test_protecoes_5_e_6_...`, `test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta` (2 casos) |
| D-763/D-764 | "ok, pode fazer" | o nome do pacote não mudou | `test_nome_do_pacote.py` (5 passam) |
| D-765 | "nenhum conserto até o .exe estar pronto" | só o atualizador mudou | o diff do ramo |
| D-767 | "não faça mais nada escondendo ou de mentira" | as peças de mentira só na borda; a biblioteca do Velopack de verdade numa instalação de prova; a licença da pasta de verdade numa pasta de prova; o resto só à vista | `test_velopack_de_verdade.py`, `test_d837_de_verdade_numa_pasta_de_prova`; "O que ficou para a prova à vista" |
| D-768/D-788/D-789, D-790, D-833 | "16" · "1" · "A" · "tudo ou nada continua" | o motor em `<raiz>\motor-kraken\<versão>` (do `atualizador-4`); sem ele, nada anunciado nem trocado | `test_protecao_4a_...`, `test_protecao_4b_...`, `test_ocr_kraken.py` (28 passam) |
| D-769, D-794, D-831 | "b" · "aparecer o aviso [...] na hora de fechar" · "a" | com "Depois", ao fechar: "Atualizar agora?"; "Sim" → esconde, troca, reabre só para conferir, sem janela; "Não" → fecha; o aviso volta | `test_d831_depois_e_sim_ao_fechar_troca_sem_janela`, `test_d794_nao_ao_fechar_fecha_sem_trocar`, `test_d769_reabertura_sem_janela_que_passa_sai_sem_janela` |
| D-805, D-806, D-834 | "a" · "opção A" · "1 – sim" | a pergunta do Windows abre o próprio `EditorImpressao.exe`, dentro de `atender_linha_de_comando`, antes do brasão e da janela; a janela da senha vem depois, com a janela aberta, e não pergunta nada ao Windows | `test_protecao_1_...` (o pedido acontece dentro de `abrir`), `test_d733_com_a_senha_nada_dos_testes_vai_na_pergunta`, `test_d721_primeira_vez_pede_a_senha_e_liga` |
| D-824, D-825 | "um só, uma coisa de cada vez" · "ok" | os testes à distância ficaram como estavam; a senha não liga nada | `test_decisoes_testes_a_distancia.py` (13 passam) |
| D-828 | "pode consertar essas coisas" | quem espera é o Velopack, pelo número do nosso processo; a troca só depois de gravar; nenhuma tranca à mão | `test_d720_reiniciar_agora_fecha_a_janela_e_so_depois_troca`, `test_protecao_10_...` |
| D-830 | "refazer" | este código | — |
| D-832 | "pode ser velopack" | a troca sem o modo silencioso; a janelinha nossa e as marcas saíram | `test_d832_...`, `test_d742_a_janelinha_da_troca_e_a_do_velopack`, `test_d748_o_brasao_nao_espera_janelinha_nenhuma` |
| D-835 | "2 – B (texto curto)" | os textos palavra por palavra | `test_d835_e_d778_os_textos_da_tela_palavra_por_palavra`, `test_d835_ao_fechar_a_pergunta_curta...` |
| D-836 | "a lista dos testes vai para o Fable" | a lista em `lista-dos-testes-d836.md` | — |
| D-837 | "6 – opção 1" + o Fable: "um caminho só" | `dar_licenca_aos_usuarios` com `icacls "<raiz>" /grant "*S-1-5-32-545:(OI)(CI)M" /T` pela peça, conferido lendo de volta; nada de `SetNamedSecurityInfoW`; o porteiro deixa só essa função, e acusa nela `/inheritance`, `/setowner`, `/remove`, `/deny`, `/reset`, `/restore`, `/substitute`, `/setintegritylevel`, `/save` e o `:r` | `test_porteiro_licenca_que_acrescenta.py` (14), `test_d837_*` da peça |
| D-838 | "7 – opção 1" | o primeiro passo da pergunta apaga o ajudante antigo (só ele); nada mais é limpo sozinho | `test_protecoes_5_e_6_...`, `test_d731_o_atualizador_novo_nao_poe_tarefa_no_windows` |
| D-605/§11.8, D-637/§11.9, §11.12, D-811 a D-813, D-827 | — | ver as seções de baixo | as mutações |

**A seção 4 do plano, corrigida (pedido da gerente):** o passo 4 tem um caminho só, o provado no experimento: o
`icacls "<raiz>" /grant "*S-1-5-32-545:(OI)(CI)M" /T`, pela peça, pelo caminho inteiro da pasta do sistema. O
`SetNamedSecurityInfoW` NÃO é usado, nem de reserva (e o porteiro continua o barrando até na função da exceção).

## O que já estava escolhido e testado aqui, e se algo mudou (§11.8)

- As decisões da tabela de cima e os testes delas (a lista do plano, seção 2). Pela D-836 (o "sim" dele para os testes
  do atualizador), os testes das peças que saíram saíram, os que cobram as mesmas decisões passaram a chamar o caminho
  novo e os das decisões mudadas cobram o que vale hoje. A lista teste por teste: `lista-dos-testes-d836.md`.
- Fora do atualizador: não mudei teste nenhum. O publicar (`test_publicar_versao.py`, 125), o empacotar (43), o motor
  (`test_ocr_kraken.py`, 28), o nome do pacote (5), a peça do Windows (68 dos 71 iguais; 2 só trocaram a constante que
  saiu pelo mesmo texto, D-836) e os 33 do desinstalar que são dos testes à distância passam.
- **Mudou sem querer: nada.** Mas dois testes do porteiro (`test_conferencias_pacote.py`, fora do atualizador) usavam o
  `atualizacao.py` como exemplo de arquivo com lugares na lista de exceções; agora ele não tem mais. Não os mexi: ver
  "Perguntas para a gerente".

## Como fica para quem usa e no livro (§11.9)

**No livro (o PDF): nada muda.** Pelo atalho "(desenvolvimento)": nada muda (o programa não está instalado pelo
Velopack; `atender_linha_de_comando` devolve None sem importar o Velopack).

- **Primeira abertura do instalado:** clique → a pergunta do Windows ("Deseja permitir...? EditorImpressao.exe") →
  "Sim" → o brasão e a janela abrem enquanto a preparação termina por trás → a janela da senha (como hoje; não liga
  nada). "Não" → a janela abre; na próxima abertura a pergunta volta, até o "Sim".
- **Abertura com versão nova:** nada atrasa; quando o download termina, o aviso "Reiniciar agora" / "Depois" (a última
  frase agora: "Se escolher "Depois", você pode atualizar quando fechar o programa.").
- **"Reiniciar agora":** a janela fecha gravando → a janelinha do Velopack → uns segundos sem nada (o teste rápido) → o
  brasão e a janela na versão nova.
- **"Depois":** nada agora. Ao fechar: "Atualizar agora?" / "Quer atualizar o programa agora, ao fechar?". "Sim" → a
  janela some, o programa grava e sai, a janelinha do Velopack aparece e some, nada abre. "Não" → fecha; o aviso volta
  na próxima abertura.
- **Falhas:** cada uma com a sua frase, uma vez por conta, na janela.
- **Não conferi clicando nem olhando o PDF**: o pedido proíbe abrir janela na tela do Samuel e o comportamento só
  existe no programa instalado pelo Velopack. O caminho da tela foi conferido pela `PonteDaTela` de verdade com caixas
  de mentira (`test_d720_*`, `test_d835_ao_fechar_*`) e o fechar da janela principal só ganhou uma chamada que, sem a
  ponte (pelo código), não faz nada. **Problema novo que pode aparecer:** a ordem da primeira abertura (a pergunta antes
  do brasão) e os segundos sem nada na tela depois da troca (ressalvas 1 e 3 do plano).

## Caminho → função (§11.12)

| Caminho | Entra por | A regra | A ação |
|---|---|---|---|
| Abrir pelo atalho | `main.py` → `atualizacao.atender_linha_de_comando` → `Atualizacao.abrir` | `proxima_fase(Abriu)` | `PedirLicenca` → `windows.comecar_pedido_de_licenca(passos_do_preparo())`; ou `GarantirMotor` → (por trás) `garantir_o_motor` → `Procurar` → `conversa_com_o_velopack.procurar` → `ConferirAssinatura` → `conferir_assinatura_do` → `Baixar` → `conversa_com_o_velopack.baixar` → `MostrarVersaoNova` |
| A espera do preparo | efeito `EsperarPreparo` (fio por trás) | `proxima_fase(PreparoTerminou)` | `PedidoDeLicenca.esperar` + `pasta_aceita_gravacao` |
| Conta de testes / pelo código / portátil | o mesmo | `Abriu` → `FORA` | nada |
| Reaberto pelo Velopack | o mesmo, `--conferir-a-versao-nova <de> <para>` (ou a anotação `tentando`) | `Abriu(troca_*)` | `RodarTesteRapido` → `windows.rodar_e_esperar([este exe, --teste-rapido])` |
| "Reiniciar agora" | `PonteDaTela._mostrar` → `Escolheu(True)` | `FECHANDO` | `FecharJanela` → `janela.close()` (o fechar grava) → `JanelaFechou` → `Trocar` → `Atualizacao.trocar_para` → `conversa_com_o_velopack.trocar` |
| "Depois" | o mesmo → `Escolheu(False)` | `DEPOIS` | nada |
| Fechar o programa | `JanelaPrincipal.closeEvent` → `aviso_de_atualizacao.ao_fechar` → `Fechando` | `PERGUNTANDO` | `PerguntarAoFechar` → `RespondeuAoFechar` → `Trocar` → `trocar_para` → `conversa_com_o_velopack.trocar` |
| A volta | `TesteRapido(False)` | `VOLTANDO` | `Voltar` → `Atualizacao._voltar` → `conversa_com_o_velopack.pacote_da_versao` + `baixar` + `trocar_para` |
| O motor | `GarantirMotor`; e dentro de `trocar_para` | `motor_esta_no_lugar` (uma só) | `garantir_o_motor` (o único que mexe em `motor-kraken\`) |
| Uma falha | `AnotarFalha` | — | `anotar_falha` (a única); a frase: `FRASES_DA_FALHA` (a única tabela) |
| Os ganchos do Velopack | `atender_linha_de_comando` → `conversa_com_o_velopack.atender_ganchos` | — | `ao_instalar` / `ao_atualizar` / `ao_desinstalar` |
| A tarefa antiga chamando `--procurar-atualizacao` | `atender_linha_de_comando` | — | anota e sai |

Provas de "um lugar só": `test_protecao_13_so_um_lugar_chama_a_troca_do_velopack` (pela árvore de todo o programa:
`wait_exit_then_apply_updates` só em `conversa_com_o_velopack.trocar`; `.trocar(` só em `Atualizacao.trocar_para`) e
`test_os_tres_caminhos_da_troca_passam_pela_mesma_conferencia` ("Reiniciar agora", "Sim" ao fechar e a volta chegam
os três a `trocar_para`). A trava cobra que só a peça do Velopack importa `velopack` (`test_velopack_so_no_dono`).

## A lista das falhas, e o que o código faz em cada uma (§11.12, ponto 3)

Regra para todas: erro técnico só no registro (`%ProgramData%\EditorImpressao\atualizacao\atualizacao.log`; se o
arquivo não aceitar, o `erros.log`); na tela, só as frases combinadas; nada dá como feito sem conferir.

**A pergunta do Windows e o preparo**
- "Não" (ou fechou a pergunta): `LicencaRespondida("disse_nao")` → nada muda, nada procurado; a pergunta volta.
- O Windows não abre o pedido / o pedido está errado / o disco não aceita a pasta de troca: "falhou" → idem.
- O ajudante antigo existe e não sai: a peça para no passo 1; a licença NÃO é dada (segurança); a pergunta volta.
- O Visual C++ falha (código de erro, ou terminou sem a versão no registro): o passo falha; a peça para; a licença não
  é dada; a pergunta volta. O instalador que uma conta comum poderia trocar não é rodado (a regra da pasta segura).
- O Inno não sai (a chave continua depois de esperar até 5 minutos): o passo falha; idem. Caminho que não parece seguro:
  não tira de propósito e segue (como antes).
- A licença não "pega" (a leitura de volta não tem a linha de Usuários, a herança ou o dono mudaram, uma linha sumiu, o
  manifesto de `current` não ficou com a licença): o passo falha; o que foi acrescentado fica (tirar licença é proibido,
  D-837); a pergunta volta se a pasta não gravar.
- O trabalho com licença disse "deu certo" mas a pasta não grava: conta como não feito (vale o teste de gravar).
- Desligar no meio: o que foi feito fica; a próxima abertura testa a pasta e decide.
- Fechar o programa no meio do preparo: o fio por trás morre; o trabalho com licença (outro processo) termina sozinho.

**Procurar, conferir, baixar**
- Sem internet / GitHub fora: só o registro; tenta na próxima abertura.
- Assinatura errada ou sem o arquivo: não baixa; falha "recusada" (frase 2), a versão em "não tentar".
- O motor fora do lugar e o arquivo dele não está no pacote, ou falta espaço: nada procurado nem anunciado.
- Disco cheio no download, a tranca de outra janela, o Velopack recusa (tamanho ou soma): só o registro.

**Trocar** (sempre por `trocar_para`)
- O arquivo em `packages\` com outra soma que a assinada (trocado depois de baixar): não troca; falha "recusada".
- A assinatura não foi conferida nesta abertura: não troca.
- O motor saiu do lugar: não troca.
- Outra janela do programa aberta (ou o Windows não deu a lista): não troca; o aviso volta na próxima abertura.
- O Velopack não aceita o pedido: a anotação da troca é apagada; o programa segue/fecha normalmente.
- A janela não fecha no "Reiniciar agora": nada trocado; vira "Depois" (pergunta ao fechar).
- O Velopack não consegue renomear (arquivo preso): ele reabre a versão de antes com os mesmos argumentos; ela vê que
  continua na de antes, falha "troca" (frase 1), a versão em "não tentar" (ressalva 5 do plano). Se ele nem reabrir, a
  anotação `tentando` faz a próxima abertura saber.
- A versão nova não passa no teste rápido: falha "teste"; a volta pela biblioteca com o pacote assinado; o Velopack abre
  a anterior, que mostra a frase 1.
- A volta não dá (sem internet, sem a assinatura, fora dos 10 "Releases" mais novos, o Velopack recusa): falha "volta"
  (frase 3); a versão nova abre se conseguir (sem janela, se era a reabertura do "Sim" ao fechar).
- A troca de volta não acontece (o Velopack reabre a quebrada): pela anotação `tentando` (volta), falha "volta".
- A anotação da troca é velha (outra versão): é apagada e a abertura segue.
- O segundo renomear do Velopack falha ("broken state"): o programa fica sem `current`; reinstalar pelo `.msi` (os
  projetos ficam). É o defeito da D-779, sem proteção nesta entrega (ressalva 6 do plano).

**Os restos do PC do Samuel (o experimento já desfeito, pela gerente):** a tarefa `\EditorImpressao\Procurar versao
nova` (desativada) é apagada pelo passo 1 da pergunta; se o Windows a rodar antes disso, o programa novo (como o
sistema) só anota e sai. O `estado.json.antes-do-experimento` não é lido (o nome é outro). A pasta
`C:\ProgramData\EditorImpressao\atualizacao\` (o `atualizacao.log` velho é da conta do Samuel, conferido por quem tentou quebrar; eu tinha escrito "do sistema", errado): a conta comum consegue CRIAR arquivo novo nela (a licença
de fábrica do ProgramData), então o `estado.json` novo nasce; o `atualizacao.log` velho (do sistema) não aceita
acréscimo, e as linhas vão para o `erros.log` (ressalva). A tarefa "Desfazer testes a distancia" não é tocada.

## A leitura das peças de fora, com a fonte (§11.12, ponto 6)

Velopack 1.2.161 (o clone na etiqueta `1.2.161`, commit `92d6a1c`; caminhos do repositório do Velopack):
- `wait_exit_then_apply_updates` (`src/lib-rust/src/manager.rs` 602-675): exige o pacote em `packages\`, abre o
  `Update.exe apply --package <arquivo> --waitPid <este processo> [--silent] [--norestart] --root ... --packageDir ...
  -- <argumentos>` com a pasta de trabalho na raiz, e volta. O Python só repassa (`src/lib-python/src/manager.rs`
  116-127).
- A espera: no máximo 60 s pelo processo, depois segue (`src/bins/src/shared/util_common.rs` 14-26).
- O apply (`src/bins/src/commands/apply_windows_impl.rs`): sem gravar na raiz, pede licença ao Windows ("Re-launching
  as administrator"; por isso nunca pedimos troca sem a licença da pasta); tranca; a janelinha
  (`show_apply_progress`); fecha à força o que roda da raiz (`force_stop_package`); renomeia `current` (10 tentativas;
  se não der, "Unable to start the update..." e nada mudou); põe a nova ("left in a broken state" se falhar); a entrada
  de "Programas e Recursos" ("Failed to update uninstall entry" não para nada); `reporter.close()` (275).
- A reabertura (`apply.rs` 47-75): com `restart`, abre a versão nova com os argumentos; se o apply falhou, abre a de
  antes com os MESMOS argumentos.
- `download_updates` (`manager.rs` 405-480, 537-561): tranca `.velopack_lock`; baixa para `.partial`; confere tamanho e
  SHA256; dá o nome final; tira o `Update.exe` novo do pacote; apaga os pacotes velhos. Se o arquivo final já existe,
  NÃO baixa nem confere (413-416).
- O localizador (`locator.rs` 140-176, 337-376): a raiz gravável → `packages` na raiz; não gravável → a reserva em
  `%LOCALAPPDATA%\<id>` (isso continua acontecendo na abertura sem a licença, pelo `App().run()`, como antes);
  `IsPortable` = `.portable` na raiz; o manifesto `current\sq.version`. O teste de gravar: `misc.rs` 72-89
  (`.velopack_dir_test` com apagar-ao-fechar).
- `App().run()` (`app.rs` 125-203): os ganchos saem do processo; sem troca automática com `set_auto_apply_on_startup(False)`.
- A fonte do GitHub (`sources/github.rs` 80, 129-138): os 10 "Releases" mais novos; acha o arquivo pelo nome. A de
  pasta (`sources/file.rs` 37-48): copia pelo nome.
- Conferido com a biblioteca de verdade numa instalação de prova (`tests/test_velopack_de_verdade.py`): procurar, baixar
  a anterior pelo pedido montado em Python, e a soma errada recusada.

Windows:
- icacls (Microsoft Learn, "icacls", atualizado em 14/10/2026): "/grant[:r] ... Not adding :r means that permissions
  are added to any previously granted explicit permissions"; "/t Performs the operation on all specified files in the
  current directory and its subdirectories"; "/c Continues the operation even if file errors occur" (sem ele, para);
  "(OI) Object inherit", "(CI) Container inherit"; "M - Modify access"; o SID numérico com "*". Conferido de verdade numa
  pasta de prova (`test_d837_de_verdade_numa_pasta_de_prova`, rodado aqui com `EDITOR_PROVA_DO_WINDOWS=1`): a raiz e o
  manifesto passam a deixar Usuários modificar, nada de antes sumiu, rodar de novo também dá certo.
- Python `os.access` no Windows só olha o atributo de só leitura (documentação do `os.access`); por isso o teste de
  gravar abre o arquivo com `os.O_TEMPORARY` (o apagar-ao-fechar).
- A lista de processos: `CreateToolhelp32Snapshot`/`Process32FirstW`/`Process32NextW` (o número de quem abriu cada
  processo, `th32ParentProcessID`) e `QueryFullProcessImageNameW` (já da volta 4).

## Cada proteção e o teste que falha quando ela é desligada (D-811 a D-813, D-827)

O script `relatorios/atualizador-novo/mutacoes.py` desliga cada uma (troca o trecho do código), roda só o teste dela e
devolve o arquivo. O resultado está em `relatorios/atualizador-novo/mutacoes-resultado.txt` (abaixo, copiado).

- **falhou (acusa)**: 1 sem licença não procura -> tests/test_atualizador_novo.py::test_protecao_1_sem_licenca_pergunta_ao_windows_e_nao_procura | 1 failed in 0.43s
- **falhou (acusa)**: 2 assinatura antes de baixar -> tests/test_atualizador_novo.py::test_protecao_2_assinatura_errada_nao_baixa_e_avisa_com_a_frase_2 | 1 failed in 0.37s
- **falhou (acusa)**: 3 soma do arquivo baixado antes de trocar -> tests/test_atualizador_novo.py::test_protecao_3_pacote_trocado_depois_de_baixar_nao_troca | 1 failed in 0.38s
- **falhou (acusa)**: 4a motor antes de anunciar -> tests/test_atualizador_novo.py::test_protecao_4a_motor_fora_do_lugar_nada_e_procurado_nem_anunciado | 1 failed in 0.41s
- **falhou (acusa)**: 4b motor antes de trocar -> tests/test_atualizador_novo.py::test_protecao_4b_motor_fora_do_lugar_na_hora_de_trocar_nao_troca | 1 failed in 0.40s
- **falhou (acusa)**: 5 a licença é o último passo -> tests/test_atualizador_novo.py::test_protecoes_5_e_6_a_ordem_dos_passos_da_pergunta | 1 failed in 0.35s
- **falhou (acusa)**: 6 o ajudante antigo sai antes da licença -> tests/test_atualizador_novo.py::test_protecoes_5_e_6_a_ordem_dos_passos_da_pergunta | 1 failed in 0.34s
- **falhou (acusa)**: 7 a conta de testes não pergunta nem procura -> tests/test_atualizador_novo.py::test_protecao_7_conta_de_testes_nao_pergunta_nem_procura | 1 failed in 0.39s
- **falhou (acusa)**: 8 a versão que falhou não é tentada de novo -> tests/test_atualizador_novo.py::test_protecao_8_a_versao_que_falhou_nao_e_baixada_de_novo | 1 failed in 0.37s
- **falhou (acusa)**: 9 outra janela aberta não troca -> tests/test_atualizador_novo.py::test_protecao_9_outra_janela_aberta_nao_troca | 1 failed in 0.39s
- **falhou (acusa)**: 10 a troca só depois de a janela fechar -> tests/test_atualizador_novo.py::test_protecao_10_a_janela_que_nao_fecha_nao_troca | 1 failed in 0.40s
- **falhou (acusa)**: 11 a volta só com pacote assinado -> tests/test_atualizador_novo.py::test_protecao_11_a_volta_sem_a_assinatura_nao_troca_e_avisa_com_a_frase_3 | 1 failed in 0.40s
- **falhou (acusa)**: 12 pelo código nada roda -> tests/test_atualizador_novo.py::test_protecao_12_pelo_codigo_nada_roda | 1 failed in 0.47s
- **falhou (acusa)**: 13 só trocar_para chama a troca -> tests/test_atualizador_novo.py::test_protecao_13_so_um_lugar_chama_a_troca_do_velopack | 1 failed in 4.07s
- **falhou (acusa)**: D-749 o preparo vale pelo teste de gravar, não pelo que o trabalho disse -> tests/test_decisoes_preparo_d749.py::test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta | 1 failed in 0.38s
- **falhou (acusa)**: D-832 a janelinha do Velopack (sem o modo silencioso) -> tests/test_atualizador_novo.py::test_d832_a_troca_usa_a_janelinha_do_velopack | 1 failed in 0.47s
- **falhou (acusa)**: D-837 a licença que só acrescenta: a herança -> tests/test_windows_preparo_do_computador.py::test_d837_o_que_tira_ou_nao_acrescenta_e_acusado | 1 failed in 0.36s
- **falhou (acusa)**: D-837 o porteiro: nada de tirar dentro da função -> tests/test_porteiro_licenca_que_acrescenta.py::test_d837_tirar_negar_trocar_dono_ou_heranca_e_acusado_ate_na_funcao | 1 failed, 1 passed in 0.30s
- **falhou (acusa)**: D-837 o porteiro: a exceção é uma função só -> tests/test_porteiro_licenca_que_acrescenta.py::test_d837_a_funcao_que_so_acrescenta_passa_so_na_peca | 1 failed in 0.30s
- **falhou (acusa)**: a trava: velopack só no dono -> tests/test_trava_windows.py::test_velopack_so_no_dono | 1 failed in 0.34s

**20 de 20 mutações acusadas.** Cada arquivo foi devolvido como estava depois de cada mutação (o `git status` limpo depois).

## O que ficou para a prova à vista (D-767, D-785)

Tudo o que mexe no Windows ou troca de versão de verdade: os 10 passos da seção 11 do plano (a pergunta no meio da
tela logo no clique; "Não" e "Sim"; a licença lida de volta na pasta de verdade; o Inno de 01/09 tirado; "Reiniciar
agora" com a janelinha do Velopack; "Depois" + fechar + "Sim"/"Não"; a versão quebrada voltando; a assinatura falsa
recusada; fechar no meio do download; sem o motor; clique no atalho durante a troca; desinstalar; as medidas de tempo).
Antes dela, a limpeza do PC do Samuel (D-838, com a gerente) e quem tenta quebrar.

## Ressalvas

1. **Não rodei o programa instalado.** Nenhuma troca de verdade, nenhuma pergunta do Windows de verdade. As provas do
   executor usam a borda de mentira; a biblioteca do Velopack e a licença da pasta rodaram de verdade só em pastas de
   prova.
2. **O Visual C++ não confere a assinatura da Microsoft no notebook** (o plano dizia que conferiria). A régua única dela
   mora no `empacotar.py`, que o programa não pode importar (a trava acusaria o `subprocess` dele) e que eu não podia
   mexer; copiar a régua seria gambiarra (§11.12). No lugar: o passo só roda o instalador se só o sistema e os
   administradores podem mudá-lo (a regra da pasta segura, que já existia). Como antes deste trabalho, o instalador vem
   dentro do pacote assinado. Ideia para a Lista de espera: levar a régua para o `core/` e o empacotar importá-la.
3. **O passo 1 (apagar o ajudante antigo) vai sempre na pergunta**, sem ler antes se a tarefa existe (o plano dizia
   "só se a leitura achou"): ler antes custaria um PowerShell de ~1 s ANTES da pergunta (D-806 quer a pergunta logo no
   clique), e o passo já não faz nada quando a tarefa não existe (`windows.apagar_tarefa`: "a tarefa já não existia").
4. **`NOME_DA_TAREFA` ficou no `atualizacao.py`** (o plano o tirava): o `core/testes_a_distancia.py`, que não é desta
   entrega, o importa para o "desfazer" apagar o ajudante antigo; e o passo 1 usa o mesmo nome.
5. **As fases e os eventos mudaram um pouco do plano** (ex.: "conferir antes de trocar" e "pode trocar" viraram uma
   coisa só, a troca única `trocar_para`, que confere e pede; "anotar a tentativa" ficou dentro dela). A ideia é a
   mesma; a tabela do teste diz cada transição.
6. **A peça do Velopack ganhou um argumento só para as provas** (`localizador`, onde está a instalação), para a
   biblioteca de verdade rodar numa instalação de prova. No programa é sempre None.
7. **O `estado.json` no PC do Samuel:** a pasta do ProgramData é do sistema; pela licença de fábrica a conta comum cria
   arquivo novo nela, mas o `atualizacao.log` velho não aceita acréscimo (vai para o `erros.log`). A limpeza da D-838
   resolve.
8. **A pergunta do Windows leva um pouco para aparecer** depois do clique: a pasta de troca do pedido carrega a pasta
   de dados do programa (~1 s, medido em 19/11 no `core/windows.py`), antes da pergunta. Não medi no instalado; a
   prova à vista mede (passo 10 da seção 11 do plano).
9. **O teste rápido roda pelo `rodar_e_esperar` da peça, com limite de 5 minutos**, sem janela; se o Windows demorar,
   conta como "não passou" e a volta começa (como antes).
10. **Dois testes do desinstalar dos testes à distância e um de pasta falham neste PC quando a pasta temporária do pytest
   fica no C:** (o próprio teste recusa comandos com "C:\"); com `--basetemp` no D: passam. Era assim antes (não é
   deste trabalho). Ver "Bugs para a Lista de bugs".
11. **A janela da senha (D-721) continua a mesma**, e a opção dos testes ligada de fábrica faz ela aparecer na
    primeira abertura, depois da janela. Nada liga (D-825).

## Ideias para a Lista de espera

- Levar a régua do Visual C++ oficial (`empacotar.vc_redist_confere`) para `core/`, para o programa instalado conferir a
  assinatura da Microsoft antes de rodar com licença (ressalva 2).
- Levar `NOME_DO_INDICE` (`releases.win.json`) para o `versao.py`, o lugar único dos nomes do pacote (hoje está escrito
  no `empacotar.py` e no `atualizacao.py`, com um teste que cobra que são iguais).
- As do plano: guardar o pacote da versão que funciona antes de trocar (D-779); a troca que falha por arquivo preso não
  pôr a versão em "não tentar"; o brasão girando durante o teste rápido.

## Bugs para a Lista de bugs

- 24/11/2026, `tests/test_decisoes_desinstalar.py` e `tests/test_decisoes_desinstalar_pasta.py`: neste PC, com a pasta
  temporária do pytest no C: (o padrão), 24 + 5 testes falham com "o comando cita o disco C: (caminho não trocado)";
  com `--basetemp` no D: todos passam. Não impede a tarefa; não consertei.

- 24/11/2026, `tests/test_decisoes_desfazer_pagina.py::test_d621_cada_etapa_sozinha_volta_so_ela_so_nesta_pagina[marcar]`:
  falhou 1 vez em 4 (os pontos da gravura marcada saíram 0,163/0,170 em vez de 0,2/0,2); passou sozinho e no arquivo
  inteiro nas outras três. Não mexe em nada do atualizador; não consertei.

## Perguntas para a gerente

- **`tests/test_conferencias_pacote.py` (2 testes) quebra.** O que é: dois testes do pacote de regras usam o
  `atualizacao.py` de verdade como exemplo de "arquivo com lugares na lista de exceções" (e a função `criar_as_tarefas`,
  com lugares do passo 5). Com o atualizador novo, o `atualizacao.py` não tem mais nenhum lugar na lista (os 40 saíram,
  como você liberou). Não mexi: são testes fora do atualizador e a regra proíbe mudar teste antigo para ele passar.
  O que você escolhe: (1) **sugestão:** você (ou quem você mandar) troca o arquivo de exemplo desses dois testes por um
  que ainda tem lugares na lista (ex.: `core/testes_a_distancia.py`), sem mudar o que eles cobram; (2) deixar como
  está até a lista ser gerada de novo.

**Respondida (24/11/2026):** o Samuel disse "sim" à sugestão (1). Feito: nos 2 testes, só o arquivo de exemplo mudou
(`atualizacao.py` → `core/testes_a_distancia.py`; no do passo, passo 3 com `criar_as_tarefas` → passo 4 com
`_passos_das_nossas_tarefas`, do passo 5). Conferido que continuam cobrando: sem a seção dos lugares no pacote, o
primeiro falha; sem a lista das funções de outros passos, o segundo falha (mudando o `montar_pacote.py` só durante a
conferência e devolvendo depois). Os 26 do arquivo passam. Anotado na lista da D-836.

## Perguntas para o Samuel

Nenhuma. Nenhuma decisão dele ficou em dúvida neste código; as duas diferenças do plano que tocam o que ele vê são só
de ordem interna (ressalvas 3 e 5) e a do Visual C++ (ressalva 2) não muda nada na tela nem no livro.

---

# Atualizador novo: o plano (23/11/2026)

Implementador. Ramo `atualizador-novo-2026-11-23`, worktree `.claude/worktrees/atualizador-novo`, ponta `732a143e`.
Pedido da gerente de 23/11/2026: **só o plano, nenhuma linha de código nem de teste.** O código só começa com o "pode"
da gerente. As voltas da trava (abaixo deste plano) ficam como estavam.

**Situação: plano escrito, esperando a gerente.** Nada do programa mudou. Li: `resposta-do-fable.md` (inteiro, com a
correção das 20:42 e a revisão das 20:50), `experimento-passo-1.md`, a Parte 2 do `relatorio-para-o-fable.md`, as
decisões D-705 a D-833 do Livro mais novo (`obra-juncao`), `atualizacao.py` e `core/windows.py` deste ramo, o
`atualizacao.py` do ramo `atualizador-4-consertos-2026-11-21`, `ui/aviso_de_atualizacao.py`, `ui/testes_a_distancia_ui.py`,
`main.py`, a trava (`tests/test_trava_windows.py`), o porteiro (`regras_dos_agentes/porteiro.py`, `excecoes.py`,
`tests/conferencias_excecoes.json`) e o código do Velopack 1.2.161 (clone na etiqueta `1.2.161`, no rascunho).

Em resumo, o desenho: **o único ato com licença é dar à pasta do programa a licença de Modificar para Usuários, uma vez,
na primeira abertura, antes da janela. Depois disso o próprio programa, na conta do Kaique, procura, confere a
assinatura, confere o motor, baixa e pede ao Velopack para trocar; o Velopack espera o programa sair, troca, mostra a
janelinha dele e reabre na conta do Kaique.** Nenhum processo nosso roda como o sistema, nenhum PowerShell, nenhuma
marca, nenhum canal entre contas.

---

## 1. Decisões que esta tarefa precisa cumprir (§11.3)

Palavras dele copiadas do Livro (`obra-juncao/docs/plano/DECISOES.md`). Quando duas se contradizem, vale a mais nova
(anotado em cada linha).

### O que o atualizador faz

| Decisão | Palavras dele | Como o desenho novo cumpre |
|---|---|---|
| D-706 | "a atualização via internet tem que ser como funciona com apps, não pode ser ele ter que baixar de novo um instalador fazer tudo de novo" | O Velopack troca a pasta `current`; o instalador só na primeira vez. |
| D-713 | "não precisa ser privado" | As versões vêm dos "Releases" do projeto público (`Fonte.padrao()`, fica). |
| D-714 | "1 - vamos seguir sua sugestão" (publicada de propósito) | Nada muda no publicar. A parte "toda vez que o pc inicializar" foi trocada pela D-732. |
| D-715 | "ele dá um aviso se o programa estiver aberto, um aviso para salvar o trabalho atual e reinicializar o programa" | Baixou com o programa aberto → aviso. "Reiniciar agora" fecha pela janela (o fechar grava) e só depois pede a troca. |
| D-718 | "Sim, e tem que avisar a gente de alguma maneira" | A versão nova reaberta roda o teste rápido antes da janela; falhou → volta para a anterior (pacote assinado) e anota. |
| D-719 | "1" (aviso na tela e registro lido de longe) | O aviso uma vez por falha; o registro fica em `%ProgramData%\EditorImpressao\atualizacao\atualizacao.log`, que outra conta do PC lê. A leitura "de longe" depende dos testes à distância (ficam para depois). |
| D-720 | "Sim" (Reiniciar agora / Depois) | Os dois botões ficam. O "Depois" muda de efeito pela D-769/D-794/D-831 (abaixo). |
| D-723 | "velopack" | Velopack 1.2.161, sem trocar (D-779). |
| D-724 | "gratis, mas o que é essa assinatura e é segura?" | A assinatura é conferida **antes de baixar** (fica) e, novo, **de novo no arquivo baixado, logo antes de trocar** (com Modificar para Usuários, outra conta poderia trocar o arquivo em `packages\`). |
| D-727 | "se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né" | O Visual C++ e o motor do Kraken continuam dentro do instalador; nada baixado na instalação. |
| D-732 | "não, faz quando o programa é aberto" | A procura roda **só ao abrir** (correção das 20:42: o "de 5 em 5 minutos" era do código antigo e sai). Nada roda por trás depois. |
| D-733 | "1- sim / VAI CONSEGUIR FAZER OS TESTS A DISTANCIA NÉ?" | Uma pergunta do Windows só, na primeira abertura; depois nenhuma, nem na volta. O programa continua em Arquivos de Programas, fora da conta do Kaique, então os testes à distância continuam possíveis depois. O "ajudante" que a D-733 descrevia era o jeito; a D-830 ("refazer") troca o jeito e mantém a escolha "1". |
| D-735 | "Sim" (a pergunta aparece sempre, com ou sem a senha) | A pergunta não depende da senha: vem antes da janela, em toda abertura em que a pasta ainda não tem a licença. |
| D-741 | "Sim" (depois do "Não", volta a cada abertura até o "Sim") | "Preparado?" = a pasta do programa aceita gravação pela conta que abriu (o mesmo teste que o Velopack faz). Sem isso, pergunta de novo. Na conta de testes, nada pergunta. |
| D-749 | "Sim" (preparação pela metade conta como não feita) | A licença da pasta é o **último** passo do pedido, e a peça para no primeiro passo que falha. Então "a pasta aceita gravação" só acontece se o Visual C++ e a retirada do Inno deram certo antes. |
| D-763/D-764 | "ok, pode fazer" · "ok" | O nome do pacote continua `versao.ID_DO_PACOTE`. Bônus: com a pasta gravável, o Velopack deixa de usar a pasta de reserva no `%LOCALAPPDATA%` (fato, `locator.rs` L152-176). |
| D-765 | "eu não quero fazer nenhum conserto até o .exe estar pronto para o kaique [...]" | Só o atualizador muda. Nada de ferramenta, filtro ou tela de trabalho. |
| D-767 | "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione" | O que mexe no Windows só conta como pronto depois da prova à vista (seção 11). |
| D-768/D-788/D-789 | "vou escolher a 16" · "1" · "A" | O motor mora em `<raiz>\motor-kraken\<versão>`, fora de `current`; a atualização vai inteira e sem o motor. |
| D-769 | "b" (com "Depois", entra ao fechar) | Mudada pela D-794 e confirmada pela D-831. |
| D-778 | "A" (três frases para as três falhas) | **Adiada pela D-824** ("os três avisos" ficam para depois). Ver pergunta 4: o desenho novo mostraria a frase errada em dois casos se continuar adiada. |
| D-779 | "ta vamos continuar com ele, mas o que fazemos para ele não dar defeito [...]" | Fica a 1.2.161. A "proteção em volta" (guardar a versão que funciona fora da pasta trocada) **fica de fora nesta entrega**: é parte do "resto do plano da parte do Windows" que a D-824 deixou para depois. Ver ressalva 6. |
| D-790 | "A" (tudo ou nada do motor) | Pela D-833, o que vem é o conserto 4 da volta 1: sem o motor no lugar, nada é anunciado nem trocado. **Baixar só o motor pela internet fica de fora**, como já estava no ramo `atualizador-4` ("Nesta entrega nao baixa motor da internet"). |
| D-794 | "eu acho que deveria aparecer o aviso para atualizar ou não na hora de fechar e se ele disser sim, o programa fecha e fica uma janelinha em segundo plano tipo esses iconizinhos, mostrando porcentagem atualizando" · "da proxima vez que ele abrir o programa" | Com versão pronta e "Depois", fechar pergunta "Atualizar agora?". Sim → o programa grava, fecha, e o Velopack troca. Não → fecha sem trocar; o aviso volta na próxima abertura. **O ícone perto do relógio: ver pergunta 3** (a D-832 diz "janelinha do Velopack"). |
| D-805 | "a" (na pergunta fica "EditorImpressao.exe") | A pergunta abre o próprio `EditorImpressao.exe` pela peça (como hoje). |
| D-806 | "então pode ser opção A" (a licença pedida no instante do clique, com o programa na frente) | A pergunta é feita **antes do brasão e da janela**, cerca de um segundo depois do clique no atalho, quando o programa ainda tem o direito de vir para a frente que o Velopack lhe passa (fato: `stub.rs` L41 e `start_windows_impl.rs` L132 chamam `AllowSetForegroundWindow` para o programa aberto). Sai a espera pela janela na frente. |
| D-824 | "vamos fazer com um só, uma coisa de cade vez." (entrega em duas vezes) | Esta entrega: o programa que se atualiza. Ficam para depois: testes à distância, os três avisos, a janelinha nossa, o desinstalar limpo dos testes. |
| D-825 | "ok" (B: a senha não liga os testes nesta entrega) | A janela da senha continua na primeira abertura; o que se digita não liga nada (como no `atualizador-4`). |
| D-826 | (a parte do "erro pequeno" **não tem resposta dele**) | No desenho novo ela some: qualquer passo que falha deixa a pasta sem a licença, e a pergunta volta (vale a D-749, que é dele). |
| D-828 | "foi eu, pode consertar essas coisas" | (1) Quem espera o programa fechar é o Velopack, pelo número do **nosso** processo (`--waitPid`), e o programa só sai depois de gravar. Um clique no atalho no meio da troca não estraga a troca: o Velopack fecha à força o que roda da pasta antes de trocar (fato, `apply_windows_impl.rs` L159). (2) A pergunta no clique (D-806). (3) Não há pasta trancada: nenhuma tranca à mão. |
| D-830 | "refazer" | Este plano. |
| D-831 | "a" (o "Depois" ao fechar, com "Atualizar agora?", já nesta entrega) | `wait_exit_then_apply_updates` ao fechar, provado no experimento de 23/11. |
| D-832 | "pode ser velopack, deixamos para mudar isso mais para frente" | A troca é chamada com a janelinha do Velopack ligada (sem `--silent`). Em português no Windows em português: "Atualização do Editor de Impressão / Instalando Atualização / Atualizando para a versão X, aguarde..." (fato, `locales/pt-BR.ftl` L2, L64-65). Nenhuma janelinha nossa. |
| D-833 | "motor do Kraken tudo ou nada continua" | `garantir_o_motor` e `motor_esta_no_lugar` vêm do `atualizador-4`, agora rodando na conta do Kaique (a pasta tem a licença). |

### Testes à distância (deixados de fora nesta entrega, D-824/D-825)

D-705, D-711, D-712, D-717, D-721, D-728, D-731, D-736, D-739, D-743, D-771, D-772, D-780, D-781:
- **Continuam como estão:** a janela da senha na primeira abertura (D-721) e o botão nas Configurações (D-712); pelo
  código nada aparece (D-728); na conta de testes nada procura nem pergunta (D-736, D-741).
- **D-736 ("Se tiver nova versão eu quero poder mandar atualizar aqui pelo meu pc, mas o programa não precisa procurar
  versão nova")** depende do comando de longe (SSH), que vem com os testes à distância. **Não é construída agora.** O
  desenho deixa o lugar: o mesmo "procurar, conferir e baixar" que a abertura usa serviria a um `--baixar-atualizacao`
  rodado de longe; a troca entraria na próxima abertura ou no "Reiniciar agora" (como o Fable descreveu).
- **D-731 ("ok": desinstalar tira junto o que os testes puseram):** nesta entrega os testes não põem nada (D-825), e o
  desenho novo não põe tarefa nenhuma no Windows. O desinstalar do `.msi` apaga a pasta inteira do programa, com o motor
  dentro. O gancho de desinstalar continua mandando rodar o "desfazer" dos testes **se** ele existir (como hoje).

### Regras de trabalho

D-605 / §11.8 (nada de mudar o que está testado sem o "sim"), D-637 / §11.9, §11.12 (uma peça só; nada dado como feito
sem conferir; a lista das falhas; ler a peça de fora), §11.13, D-775 (quem tenta quebrar antes da prova), D-785 (à
vista), D-793 / §11.11 (não abrir agente), D-809 (nada que mude o `.git` inteiro), D-811 a D-813 e D-827 (cada
proteção com o teste que a acusa), D-815, D-819 (comparar o jeito mais simples e dizer por quê).

---

## 2. O que já está escolhido e testado aqui (§11.8)

Legenda: **F** = continua igual, sem mudar uma linha. **C** = cobra a mesma decisão, mas chama o caminho novo (muda a
chamada, não a conferência). **S** = testa uma peça que sai. **M** = cobra uma decisão que ele mesmo mudou depois.
**Nenhum teste muda nem sai sem o "sim" dele** (pergunta 5). Os C marcados "D-825" já têm o "sim" de 21/11 para passar
ao "caminho novo [...], o 'preparado' lido do Windows" — a gerente confere se esse "sim" cobre a leitura da pasta (no
lugar da leitura das tarefas).

**`tests/test_decisoes_atualizacao.py` (38):**
- F: `d714_a_versao_vem_de_um_lugar_so`, `os_textos_do_aviso_sem_emoji_e_com_acento`, `pelo_codigo_o_aviso_nao_liga`,
  `d719_a_frase_da_falha_e_a_combinada`, `d719_o_erro_vai_para_o_registro_no_programdata`, `d719_nenhum_token_dentro_do_programa`,
  os 3 `d724_publicar_*`, `d724_a_chave_nunca_dentro_do_repositorio`, `d724_o_que_o_publicar_assina_o_programa_aceita`,
  `d723_o_desinstalador_do_inno_nao_apaga_os_projetos`, `d714_a_instalacao_de_verdade_nao_cria_a_tarefa`, os 2
  `d727_o_vpk_*`/`o_visual_c_vai_dentro`, `pelo_codigo_a_linha_de_comando_nao_faz_nada_nem_importa_o_velopack`,
  `o_main_chama_a_atualizacao_por_um_ponto_so`.
- C: os 4 `d724` de procurar (assinatura errada, sem arquivo, pacote trocado, já falhou: sai só o argumento "programa
  aberto?"), `d715_programa_aberto_fica_pendente_e_a_tela_avisa`, `sem_internet_nao_e_falha_e_nao_avisa`,
  `d720_reiniciar_agora_fecha_gravando_e_so_depois_troca`, `d719_a_falha_aparece_na_tela_uma_vez_so`, os 4 `d718`
  (volta, fica, troca desfeita, só pacote assinado: a versão de antes e a nova passam a vir na linha de comando da
  reabertura), `d723_o_comando_que_tira_o_inno`, `d723_o_pacote_portatil_*`, `d723_instalacao_de_verdade_prepara_o_computador`,
  `d727_o_visual_c_so_roda_se_faltar` (as três últimas: o Visual C++ e o Inno passam a ser passos da peça).
- S: `d714_a_tarefa_roda_ao_ligar_*`, `d714_criar_e_apagar_a_tarefa_pelo_schtasks`,
  `d714_programa_fechado_baixa_e_troca_e_reabre_escondido_*` (quem trocava com o programa fechado era o ajudante),
  `d723_o_portatil_nunca_cria_nem_apaga_a_tarefa`.
- M: `d720_depois_do_depois_a_tarefa_troca_quando_o_computador_liga` (já era da D-714 antiga), `d720_o_aviso_tem_reiniciar_agora_e_depois_*`
  (cobra a frase "próxima vez que você abrir o programa"; o "Depois" agora pergunta ao fechar).

**`tests/test_decisoes_ajudante_da_atualizacao.py` (37):**
- F: `b1_ao_instalar_e_ao_atualizar_nao_criam_a_tarefa`, `d736_a_conta_de_testes_e_reconhecida_pelo_nome_fixo`, os 4
  `etapa5_*` (a fonte de teste do administrador: fica; só a leitura do dono do arquivo passa para a peça).
- C: `d732_ao_abrir_o_programa_manda_o_ajudante_procurar` e `d732_a_janela_aberta_chama_o_ajudante_e_liga_o_aviso`
  (procura ao abrir, agora no próprio programa), os 3 `d735_*` (D-825), `d733_disse_nao_fica_anotado_e_nada_quebra`
  (D-825), `d733_reiniciar_agora_chama_o_ajudante_e_nao_pede_licenca` (continua sem licença, pelo Velopack),
  `d736_aberto_por_teste_a_distancia_nao_procura_nem_troca`, os 3 `d741_*` de pergunta voltar (D-825).
- S: `d732_o_ajudante_nao_roda_mais_ao_ligar_o_computador`, `d733_a_conta_comum_pode_mandar_rodar_mas_nao_mudar_o_ajudante`,
  `d733_depois_de_trocar_o_ajudante_e_refeito_como_o_sistema`, `d733_o_passo_de_preparar_roda_este_exe_escondido_*` (D-825),
  `d733_o_modo_preparar_cria_o_ajudante_e_prepara_o_computador`, `d733_a_linha_de_comando_atende_o_preparar`,
  `d733_o_script_escondido_vai_codificado_e_solto`, `d736_o_samuel_manda_atualizar_de_longe_pelo_mesmo_ajudante`,
  `regra_num_lugar_so_todos_os_caminhos_chamam_o_ajudante_pelo_mesmo_comando`, `d741_a_marca_e_de_fabrica_falsa_*` (a
  marca nas Configurações já saiu pela D-825).
- M: `d733_com_a_senha_preparo_e_testes_numa_pergunta_so` (D-825: a senha não liga), os 3 `d734_*` (entra na próxima
  abertura → ao fechar), os 6 `d742_*` (a nossa janelinha → a do Velopack, D-832).

**`tests/test_decisoes_preparo_d749.py` (5):** C: `sim_com_a_preparacao_parada_no_meio_a_pergunta_volta`,
`visual_c_ou_inno_que_falham_contam_como_erro` (D-825). S: `uma_anotacao_velha_nao_conta`, `o_modo_preparar_devolve_erro_*`,
`o_passo_anota_como_o_preparo_terminou` (o `preparo.txt` e o `--preparar-o-computador` saem; D-825).

**`tests/test_decisoes_desinstalar.py` (37):** F: os 31 dos testes à distância. C: os 3 `d731_desinstalar_*` (trocam
`atualizacao.apagar_tarefa`, que sai; o "manda rodar o desfazer" fica). S: `d731a_sem_os_testes_ligados_desinstalar_apaga_a_tarefa_da_atualizacao`,
`d731a_com_os_testes_ligados_o_desfazer_inteiro_apaga_tambem_a_tarefa_da_atualizacao`,
`d731a_a_primeira_abertura_nao_troca_o_desfazer_inteiro_pelo_curto` (a primeira abertura deixa de criar o "desfazer" e
o ajudante não existe). **`tests/test_decisoes_desinstalar_pasta.py` (4):** F.

**`tests/test_decisoes_testes_a_distancia.py` (13):** F: 11. C (D-825): `d721_primeira_vez_pede_a_senha_e_liga`,
`d728_instalado_primeira_vez_pede_a_senha`.

**`tests/test_decisoes_brasao.py` (22):** F: 19 (o `d744_o_brasao_some_quando_a_janela_principal_abre` importa
`ui.aviso_de_atualizacao`, que continua existindo). M: os 3 `d748_*` (a janelinha nossa e as duas marcas saem; o
brasão deixa de esperar a janelinha).

**`tests/test_windows_peca.py` (71):** F: 69. C: `a_licenca_da_tarefa_e_comparada_pelo_sentido_*` e
`a_tarefa_numa_pasta_do_agendador_que_mudou_no_meio_e_apagada` usam `atualizacao.QUEM_PODE_MANDAR_RODAR` como dado de
exemplo; a constante sai com o ajudante (pergunta 5: o texto vai escrito no próprio teste).

**`tests/test_nome_do_pacote.py` (5), `tests/test_publicar_*.py`:** F (o publicar não muda).

**`tests/test_trava_windows.py` (deste ramo, ainda não juntado):** a catraca muda pelo jeito previsto nela mesma (seção 10).

**`tests/test_conferencias_excecoes.py::test_o_repositorio_so_tem_os_erros_que_a_lista_deixa`:** vai falhar até a
gerente gerar a lista de novo (seção 10). Não mexo nele nem na lista.

Os testes do ramo `atualizador-4` (`test_atualizador_4.py`, `test_atualizador_volta4.py`) não existem aqui. Vêm só os
do motor (conserto 4) que cobram o que passa (seção 5).

---

## 3. Como fica para quem usa e no livro (§11.9)

**No livro (PDF): nada muda.** Só o atualizador muda. Pelo atalho "(desenvolvimento)" e pelo código, nada muda (o
programa não está instalado pelo Velopack: nada roda).

**Primeira abertura (programa recém-instalado pelo `.msi`):**
- Antes: clique → brasão → janela → janela da senha → "Agora não" → a pergunta do Windows (às vezes só piscando na
  barra) → nada na tela enquanto prepara.
- Depois: clique → **logo em seguida** a pergunta do Windows ("Deseja permitir que este aplicativo... EditorImpressao.exe",
  faixa amarela) no meio da tela → "Sim" → o brasão e a janela abrem normalmente, enquanto a preparação (Visual C++,
  tirar a instalação antiga, a licença da pasta) termina por trás, num processo separado → a janela da senha aparece
  como hoje (pergunta 1: a ordem muda). Depois da preparação, o programa põe o motor do Kraken no lugar e procura versão
  nova, por trás, sem nada na tela.

**Pergunta recusada com "Não":** a janela abre normalmente; nada é feito; na próxima abertura a pergunta aparece de
novo, logo no clique, até o "Sim". Sem o "Sim", nada se procura (se procurasse, o Velopack pediria licença a cada versão,
o jeito 2 que ele recusou).

**Abertura comum com versão nova publicada:** clique → brasão → janela (nada atrasa: a procura e o download rodam por
trás). Quando o download termina (uns 460 MB), aparece o aviso de hoje: "Reiniciar agora" / "Depois".

**"Reiniciar agora":** a janela fecha pelo caminho de sempre (grava o trabalho) → aparece a janelinha do Velopack
("Atualizando para a versão X, aguarde...") → some → uns segundos sem nada na tela (o teste rápido da versão nova) → o
brasão e a janela, já na versão nova. Ressalva 3: os segundos sem nada na tela.

**"Depois":** nada muda agora; ele continua trabalhando. Ao fechar o programa aparece "Atualizar agora?" (texto na
pergunta 2). "Sim" → o programa grava e fecha → a janelinha do Velopack aparece até a troca acabar → nada abre (D-769:
na próxima vez ele já abre na versão nova, sem esperar). "Não" → fecha sem trocar; na próxima abertura o aviso de versão
nova aparece de novo.

**Versão nova que falha no teste rápido:** depois da janelinha do Velopack, a versão nova não passa no teste; ela anota,
baixa de novo a versão anterior assinada (uns minutos, nada na tela: ressalva 4), pede a troca de volta (janelinha do
Velopack de novo) e abre a anterior, que mostra uma vez "A atualização não deu certo. O programa voltou para a versão
anterior e continua funcionando. Avise o Samuel." Essa versão não é tentada de novo; espera uma mais nova.

**Clique no atalho no meio da troca:** a troca não se estraga (o Velopack fecha à força o que abriu da pasta antes de
trocar). O clique pode se perder: ele clica de novo depois que a janelinha do Velopack sumir.

**Duas janelas do programa abertas e "Atualizar agora? Sim" numa delas:** a troca não acontece (o Velopack fecharia a
outra à força, com o que estiver nela); fica anotado, e o aviso volta na próxima abertura. Nenhum texto novo na tela.

**O que pode virar problema novo:** (a) a ordem da primeira abertura (pergunta 1); (b) "Programas e Recursos" continua
mostrando a versão do instalador (fato do experimento: "Failed to update uninstall entry"; o Fable deixou para depois da
entrega); (c) se a conta do Kaique for padrão (não administrador), a pergunta do Windows pede a senha de um
administrador (não conferi o tipo da conta dele; ressalva 7).

---

## 4. O desenho

### 4.1 As peças (uma para cada conversa com o que está fora)

| Peça | Arquivo | Só ela pode |
|---|---|---|
| A regra (máquina de estados) | `core/fases_da_atualizacao.py` (novo, puro) | decidir o que acontece: `proxima_fase(estado, evento) -> (estado, efeitos)`. Não importa nada além de `dataclasses`, `enum` e `typing` (um teste lê a árvore e cobra). |
| O Windows | `core/windows.py` (existe) | a pergunta do Windows, os passos com licença, ler licenças, dono de arquivo, registro do Windows, tarefas, rodar o teste rápido, a lista de processos. |
| O Velopack | `core/conversa_com_o_velopack.py` (novo) | `import velopack`: os ganchos, a versão, procurar, baixar, o pendente, montar o pacote da anterior, trocar. **Uma função só chama a troca** (`trocar`). |
| O executor | `atualizacao.py` (refeito) | rodar os efeitos que a regra devolve, chamando as duas peças acima; o `estado.json`, o registro, o motor, a fonte de teste, a linha de comando. |
| A tela | `ui/aviso_de_atualizacao.py` | só transforma clique em evento e efeito em caixa. Nenhuma conta. |

### 4.2 "Preparado?" (§11.12 ponto 2)

É o que o Windows responde agora: **a conta que abriu consegue criar um arquivo na raiz da instalação?** É o mesmo teste
que o próprio Velopack faz para decidir se vai pedir licença na troca (fato: `misc.rs` L73-85, `is_directory_writable`,
arquivo `.velopack_dir_test` com apagar-ao-fechar; `locator.rs` L152-176 decide por ele). Fazemos igual, com outro nome
de arquivo, em `atualizacao.py` (só o disco, sem a biblioteca do Windows: leva cerca de 1 ms; ler a licença pela peça
carregaria o `core/windows.py`, ~100 ms por abertura, medidos em 19/11).
- Por que não ler a lista de licenças (D-819, o mais simples contra o outro): o teste de gravar responde exatamente "a
  troca vai pedir licença?", inclusive com grupos e negações que uma leitura da lista teria de recalcular. A leitura da
  lista (`core.windows.ler_licencas`) fica para conferir, depois do "Sim", que a licença nova está lá e herdada (seção 7).
- `os.access` não serve: no Windows ele só olha o atributo "só leitura" (a conferir na leitura do CPython antes do código).

### 4.3 Onde mora a pergunta do Windows (D-806)

`main.py` → `atualizacao.atender_linha_de_comando` (já roda **antes** do brasão e da janela) → abertura comum do programa
instalado, fora da conta de testes, pasta sem a licença → efeito `PedirLicenca` → `core.windows.comecar_pedido_de_licenca(passos)`.
- **Mudança na peça:** hoje `pedir_licenca` pergunta e espera o trabalho com licença acabar (pode levar minutos com o
  Visual C++). Ela vira duas metades da mesma conta: `comecar_pedido_de_licenca` (prepara o pedido e faz a pergunta; volta
  logo depois da resposta: "disse Não", "falhou" ou "começou") e `PedidoDeLicenca.esperar()` (espera e lê o relatório).
  `pedir_licenca` passa a ser `comecar(...).esperar()`, sem conta copiada; quem já a usa não muda.
- A espera roda num fio de trás, depois que a janela abriu. Fechar o programa no meio não estraga: o trabalho com
  licença é outro processo e termina sozinho; a próxima abertura testa a pasta de novo.

### 4.4 Os passos do pedido, nesta ordem (a peça para no primeiro que falha)

1. **Apagar o ajudante antigo** (`passo_apagar_tarefa`, já existe), só se a leitura sem licença (`core.windows.ler_tarefa`)
   achou `\EditorImpressao\Procurar versao nova`. **Segurança:** essa tarefa roda o `.exe` da pasta como o sistema; com
   Modificar para Usuários, qualquer conta poderia trocar esse `.exe`. Por isso ela sai **antes** da licença, no mesmo
   pedido. Só existe no PC do Samuel (seção 8).
2. **Instalar o Visual C++ se faltar** — tipo novo de passo `instalar_visual_c`: o lado com licença calcula sozinho o
   caminho (`<pasta do programa>\instalar\vc_redist.x64.exe`, nunca vindo do aviso), confere a assinatura da Microsoft
   (`ler_assinatura_digital`, já na peça), roda `/install /quiet /norestart` e confere a versão lida no registro depois.
3. **Tirar a instalação antiga do Inno, se houver** — tipo novo `tirar_instalacao_do_inno`: o lado com licença lê a chave
   do Inno (AppId fixo), aceita só um desinstalador `unins*.exe` dentro da pasta que a chave diz, roda em silêncio e
   confere que a chave sumiu. Os projetos não são tocados (teste `d723_o_desinstalador_do_inno_nao_apaga_os_projetos`).
4. **Dar Modificar para Usuários na raiz** — tipo novo `dar_licenca_aos_usuarios`: o lado com licença calcula a raiz
   (a pasta acima de `current`, que tem `current\sq.version` e fica em Arquivos de Programas; nada vem do aviso),
   **acrescenta** uma linha "Usuários (`S-1-5-32-545`): Modificar, passa para pastas e arquivos" e confere lendo de volta
   (a raiz e um arquivo de dentro de `current`). Nunca tira herança, nunca troca dono, nunca apaga linha (o defeito de
   18/11 foi o `/inheritance:r`). Jeito: `SetNamedSecurityInfoW` só na raiz, porque "the system automatically propagates
   any inheritable access control entries (ACEs) to existing child objects" (Microsoft, `SetNamedSecurityInfoW`,
   Remarks). O experimento provou o `icacls ... /grant ... /T`; se a prova à vista mostrar que a herança não chegou a
   algum arquivo, o passo usa o jeito provado. **O porteiro barra isso hoje (K03): pergunta 6.**

Os passos 2 e 3 já existiam (`instalar_visual_c_se_faltar`, `comando_para_tirar_o_inno`, `atualizacao.py`), rodando dentro
do "exe elevado que abre PowerShell que abre exe". Passam para a peça como passos da lista fechada; a regra de cada um
continua num lugar só.

### 4.5 Cada momento, e o que se chama

| Momento | O que acontece | Chama |
|---|---|---|
| Abrir (qualquer abertura) | `atender_linha_de_comando`: modos escondidos; ganchos do Velopack | `conversa_com_o_velopack.atender_ganchos()` (o `velopack.App().set_auto_apply_on_startup(False)...run()` de hoje; sem troca automática, senão o "Não" ao fechar trocaria na abertura seguinte) |
| Abrir, sem licença na pasta | pergunta do Windows, antes da janela | `core.windows.comecar_pedido_de_licenca` |
| Depois do "Sim" (fio de trás) | espera; testa a pasta de novo; confere a licença lida | `PedidoDeLicenca.esperar()`, `core.windows.ler_licencas` |
| Abrir com licença (fio de trás) | motor; procurar; assinatura; baixar | `atualizacao.garantir_o_motor` (do `atualizador-4`); `conversa_com_o_velopack.procurar()` (`check_for_updates`); `atualizacao.conferir_assinatura_do`; `conversa_com_o_velopack.baixar()` (`download_updates`, que confere tamanho e SHA256: fato, `manager.rs` L537-561) |
| Baixou | aviso "Reiniciar agora"/"Depois" | efeito `MostrarVersaoNova` → `ui/aviso_de_atualizacao.py` |
| "Reiniciar agora" | fecha a janela (grava); então pede a troca e sai | `conversa_com_o_velopack.trocar(alvo, reabrir=[conferir, de, para])` → `wait_exit_then_apply_updates(alvo, silent=False, restart=True, restart_args=...)` |
| Fechar com versão pronta | "Atualizar agora?"; Sim → grava, pede a troca, sai | a mesma `trocar(alvo, reabrir=[conferir, de, para, sem janela])` |
| Reaberto pelo Velopack | versão atual = a nova → teste rápido (outro processo, sem janela); = a anterior → a troca não aconteceu (o Velopack reabre a anterior com os mesmos argumentos quando a troca falha: fato, `apply.rs` L56-60) | `core.windows.rodar_e_esperar([este exe, --teste-rapido])` |
| Teste rápido falhou | anota a falha; monta o pacote da anterior; baixa; pede a troca de volta | `conversa_com_o_velopack.pacote_da_versao(anterior)` + `baixar` + `trocar(..., reabrir=[])` |

- **Antes de toda troca** (dentro de `trocar`, um lugar só): o arquivo em `packages\` tem a soma assinada? o motor está
  no lugar? há outra janela do programa aberta (`core.windows.programas_rodando_de`, vinda do `atualizador-4`, sem os
  processos filhos deste)? Qualquer "não" → não troca e anota.
- **A volta pela biblioteca, sem `Update.exe` à mão:** fato, `sources/github.rs` L129-138: o Velopack procura o arquivo
  pelo nome em todos os "Releases" lidos; `UpdateInfo` e `VelopackAsset` se montam pelo Python (`__init__.pyi` L225, L400);
  o tamanho e a soma vêm do `releases.win.json` da versão anterior, lido pela `Fonte` (como a assinatura), e a soma tem de
  bater com a assinada. Assim nenhuma linha nossa roda o `Update.exe` (K01 continua sem exceção nova).
- **Ler a versão:** `versao.VERSAO` (o número com que o pacote foi montado, D-714) em vez de perguntar ao Velopack: não
  carrega a biblioteca na abertura. "Instalado pelo Velopack" = programa empacotado com `current\sq.version` ao lado;
  "portátil" = `.portable` na raiz (fato, `locator.rs` L376). Nenhum dos dois cita o `Update.exe`.

### 4.6 A máquina de estados (`core/fases_da_atualizacao.py`)

`proxima_fase(estado, evento) -> (estado, efeitos)`, sem I/O. O estado guarda a fase, a versão atual, a nova, a
anterior e o que veio do `estado.json` (versões que não tentar, a última falha). Fases:

`fora` (código, portátil, conta de testes) · `sem_licenca` · `preparando` · `motor` · `procurando` · `conferindo` ·
`baixando` · `pronta` · `depois` · `fechando_para_trocar` · `trocando` · `conferir_nova` · `voltando` · `parado`.

Eventos: `Abriu(instalado, conta_de_testes, portatil, pasta_grava, reaberto_de, reaberto_para, sem_janela)` ·
`LicencaRespondida(desfecho)` · `PreparoTerminou(pasta_grava, motivo)` · `MotorConferido(no_lugar)` · `Procurou(versao|None, erro)` ·
`Assinatura(certa, motivo)` · `Baixou(certo, erro)` · `Escolheu(reiniciar|depois)` · `JanelaFechou(fechou)` · `Fechando` ·
`RespondeuAoFechar(sim|nao)` · `PodeTrocar(sim, motivo)` · `TesteRapido(passou, detalhe)` · `VoltaPedida(certa, motivo)`.

Efeitos: `PedirLicenca(passos)` · `EsperarPreparo` · `GarantirMotor` · `Procurar` · `ConferirAssinatura(v)` · `Baixar(v)` ·
`MostrarVersaoNova(v)` · `FecharJanela` · `PerguntarAoFechar` · `ConferirAntesDeTrocar` · `Trocar(v, reabrir)` ·
`AnotarTentativa(de, para)` · `RodarTesteRapido` · `AnotarOk(v)` · `AnotarFalha(tipo, de, para, motivo)` ·
`Voltar(v)` · `MostrarFalha(tipo)` · `Registrar(texto)` · `AbrirJanela` · `Sair(codigo)`.

Todo par (fase, evento) tem resposta escrita; o que não faz sentido naquela fase vira `Registrar` e a fase fica (nunca
exceção). O `estado.json` (`%ProgramData%\EditorImpressao\atualizacao\`, gravado pela conta do Kaique) guarda só o que
precisa passar de uma abertura para outra: as versões que não tentar, a falha a mostrar uma vez e "tentando X a partir
de Y" (para a abertura seguinte saber, comparando com a versão que de fato roda, que uma troca não aconteceu). "Há versão
baixada esperando" não se anota: é o que o Velopack diz (`get_update_pending_restart`, fato `manager.rs` L272-281).

---

## 5. O que sai, o que fica, o que vem do `atualizador-4`

**Sai de `atualizacao.py` (deste ramo):** `NOME_DA_TAREFA`, `QUEM_PODE_MANDAR_RODAR`, `LIMITE_DA_TROCA_S`,
`ESPERA_DA_VOLTA_S`, `MARCA_DE_ABERTO`, `MARCA_DA_JANELINHA`, `TEXTO_DA_JANELINHA`, `ARG_PREPARAR`, `ARG_DEPOIS_DA_TROCA`,
`_dono_do_arquivo` (vai para a peça), `update_exe`, `criar_gerente`/`versao_que_roda` (vão para a peça do Velopack),
`rodar_ao_ligar`, `_argumentos_da_fonte`, `_aplicar_pacote_quando_sair`, `marcar_programa_aberto`, `_marca_existe`,
`ha_programa_aberto`, `ha_janelinha`, `_rodar`, `script_da_janelinha`, `_linhas_da_janelinha`, `script_de_trocar_e_reabrir`,
`_aspas_do_powershell`, `_lancar_escondido`, `trocar_e_reabrir`, `aplicar_agora_e_reabrir`, `trocar_antes_de_abrir`,
`comando_de_rodar_a_tarefa`, `procurar_ao_abrir`, `comando_de_longe_para_atualizar`, `comando_de_longe_para_ler_o_registro`,
`xml_da_tarefa`, `criar_tarefa`, `rodar_tarefa_agora`, `apagar_tarefa`, `_ler_versao_do_visual_c` e `_ler_chave_do_inno`
(vão para a peça), `instalar_visual_c_se_faltar`/`tirar_instalacao_antiga`/`comando_para_tirar_o_inno` (viram passos),
`preparar_o_computador`, `preparar_como_administrador`, `criar_as_tarefas`, `arquivo_do_preparo`,
`passo_de_preparar_o_computador`, `preparo_deu_certo`, `preparar_na_primeira_abertura`,
`CHAVE_PERGUNTA_DO_WINDOWS_RESPONDIDA`, `falta_a_pergunta_do_windows`, `conferir_e_refazer_o_ajudante`, `_rodar_o_velopack`.
`ARG_PROCURAR` fica só para ser reconhecido: a tarefa antiga que sobrar num PC chama o `.exe` novo com ele; o programa
anota e sai sem fazer nada.

**As peças de hoje, uma a uma:**

| Peça | Sai ou fica | Por quê |
|---|---|---|
| O ajudante (tarefa SYSTEM) | sai | Só existia para trocar em Arquivos de Programas sem pergunta. Com a licença da pasta, a conta do Kaique troca (experimento de 23/11). |
| Os scripts PowerShell (trocar e reabrir; janelinha; no `atualizador-4` também o vigia e o "só de reabrir") | saem | O Velopack espera o processo certo (o nosso) e reabre na conta certa (fato, `manager.rs` L602-675). |
| O vigia | sai (nem entra) | Só segurava a marca da troca no caminho sem script. |
| As marcas (programa aberto, janelinha, troca, reabrir) | saem | Ninguém em outra conta precisa saber se o programa está aberto. |
| `estado.json` entre contas | sai como canal | Fica um arquivo da conta do Kaique, só com o que passa de uma abertura para outra (4.6). |
| Lista de processos (esperar 30 s) | sai como espera | O `--waitPid` é o nosso. Fica `programas_rodando_de` só para "outra janela aberta → não troca". |
| `GerenteComAMarcaDaTroca`, `TrocaSemAMarca`, `FASES_EM_QUE_HA_TROCA` | saem (nem entram) | Existiam para a marca da troca. "Uma troca só por um lugar" passa a ser `conversa_com_o_velopack.trocar`. |
| Espera pela janela na frente | sai (nem entra) | A pergunta vem antes da janela (D-806). |
| A nossa janelinha | sai | D-832: a do Velopack. |
| `--preparar-o-computador` (exe elevado → PowerShell → exe) | sai | Os passos rodam direto no trabalho com licença da peça. |
| A tarefa "desfazer" na primeira abertura | sai desta entrega | Era para apagar o ajudante e desfazer os testes ao desinstalar; não há ajudante, e os testes não ligam nesta entrega. Volta com os testes à distância. |

**Fica:** `Fonte`, `fonte_da_linha`, `fonte_de_teste` (o dono do arquivo passa a ser lido pela peça), `registrar`,
`ler_estado`/`gravar_estado`, `registrar_falha`, `situacao`/`o_que_avisar` (adaptadas às fases), `_versao_assinada_do`,
`conferir_assinatura_do`, `teste_rapido`, `voltar_para_a_anterior` (pela biblioteca), `conferir_versao_nova` (com a
versão de antes e a nova pela linha de comando), `e_a_conta_de_testes`, `e_portatil`, `instalado_pelo_velopack`,
`ao_instalar`, `ao_atualizar`, `ao_desinstalar` (continua mandando o "desfazer" dos testes, se existir),
`atender_linha_de_comando`, os textos (`TITULO_*`, `FRASE_*`, `BOTAO_*`), as constantes do Inno e do Visual C++ (vão para
a peça, que as usa nos passos).

**Vem do `atualizador-4`:** `garantir_o_motor`, `motor_esta_no_lugar`, `_apagar_pasta_do_motor`, `FOLGA_DO_MOTOR_BYTES` e
o ramo "sem motor → nada anunciado" (D-833); `core/ocr_kraken.py`: `pasta_do_motor_instalado` e o lugar único do motor no
programa instalado; o teste rápido conferindo o motor pela `core/ocr_kraken`; `configuracoes.py` sem a marca
`atualizacao_computador_preparado`; `ui/testes_a_distancia_ui.py`: a senha não liga nada (D-825); `core/windows.py`:
`programas_rodando_de`; e os testes do conserto 4 que cobram o motor. **Não vem:** o resto da volta 2 a 4 (marca da
troca, vigia, esperar a janela, ler as tarefas, os 30 s, as 30 tentativas do `gravar_estado`).

---

## 6. Caminho → função (§11.12)

| Caminho | Entra por | A regra | A ação |
|---|---|---|---|
| Abrir pelo atalho | `main.py` → `atualizacao.atender_linha_de_comando` | `proxima_fase(Abriu)` | `PedirLicenca` → `core.windows.comecar_pedido_de_licenca`; ou `GarantirMotor`/`Procurar` no fio de trás |
| Abrir na conta de testes / pelo código / portátil | o mesmo | `proxima_fase(Abriu)` → `fora` | nada |
| Reaberto pelo Velopack | o mesmo, com os argumentos de conferir | `proxima_fase(Abriu(reaberto_*))` | `RodarTesteRapido` → `core.windows.rodar_e_esperar` |
| "Reiniciar agora" | `ui/aviso_de_atualizacao.py` → evento `Escolheu(reiniciar)` | `proxima_fase` | `FecharJanela`, depois `Trocar` → `conversa_com_o_velopack.trocar` |
| "Depois" | o mesmo → `Escolheu(depois)` | `proxima_fase` | nada agora |
| Fechar o programa | `ui/janela_principal.py` `closeEvent` → `ui/aviso_de_atualizacao.ao_fechar` → `Fechando` | `proxima_fase` | `PerguntarAoFechar` → `RespondeuAoFechar` → `Trocar` → `conversa_com_o_velopack.trocar` |
| A volta para a anterior | `proxima_fase(TesteRapido(falhou))` | `proxima_fase` | `Voltar` → `atualizacao.voltar_para_a_anterior` → `conversa_com_o_velopack.baixar` + `trocar` |
| O motor do Kraken | `proxima_fase` (antes de procurar; e dentro de `trocar`) | `motor_esta_no_lugar` (uma só) | `atualizacao.garantir_o_motor` (o único que mexe em `motor-kraken\`) |
| Os ganchos do Velopack (instalar, atualizar, desinstalar) | `atender_linha_de_comando` → `conversa_com_o_velopack.atender_ganchos` | — | `ao_instalar`/`ao_atualizar`/`ao_desinstalar` |
| A tarefa antiga chamando `--procurar-atualizacao` | `atender_linha_de_comando` | — | `Registrar` e sai |

Toda troca passa por **uma** função (`conversa_com_o_velopack.trocar`), e só ela chama `wait_exit_then_apply_updates`.
Prova: um teste que lê a árvore e cobra que esse nome aparece só ali; e um teste que passa por "Reiniciar agora", "Sim ao
fechar" e a volta e cobra que os três chegam a `trocar`, com a mesma conferência antes.

---

## 7. A lista das falhas (§11.12 ponto 3)

Regra para todas: nada fica pela metade sem a tela dizer, nunca "deu certo" sem conferir, e o erro técnico vai para o
registro, nunca para a tela.

**A pergunta do Windows e a preparação**
- A pessoa clica "Não" (ou fecha a pergunta): a peça devolve "disse Não" (erro 1223, já provado na peça). Nada muda; a
  janela abre; na próxima abertura pergunta de novo. Tela: nada.
- A conta é padrão e ninguém sabe a senha de administrador: igual ao "Não". Pergunta toda abertura (D-741). Ressalva 7.
- O Windows não abre o pedido (sem licença de rodar, programa sumiu): "falhou"; abre a janela; registra; pergunta de novo
  na próxima.
- Ninguém responde à pergunta: a abertura fica parada na pergunta (ela está no meio da tela, com o resto escurecido).
- Visual C++ falha / Inno falha: a peça para ali; a licença não é dada; a pasta continua sem gravar; a pergunta volta
  (D-749). Registro: qual passo e o motivo.
- A licença não "pega" (lida de volta sem a linha, ou um arquivo de dentro sem ela): o passo devolve "falhou" com o que
  faltou; a pergunta volta. Se a raiz já grava mas um arquivo de dentro não, a troca do Velopack falharia num arquivo:
  por isso a conferência lê também um arquivo de `current`.
- Desligar no meio da preparação: o que já foi feito fica (o Visual C++ é transacional; o Inno pode ficar pela metade e é
  tentado de novo); a licença ou foi dada ou não. A próxima abertura testa a pasta e decide.
- A tarefa antiga do ajudante existe e não dá para apagar: a peça para nesse passo; a licença **não** é dada (segurança).

**Procurar, conferir, baixar**
- Sem internet / GitHub fora do ar: `check_for_updates` levanta; registra; tela nada; tenta na próxima abertura.
- A assinatura errada ou ausente: não baixa; anota a falha ("recusada") e a versão em "não tentar"; a tela mostra o aviso
  de falha uma vez (qual frase: pergunta 4).
- O motor do Kraken não está no lugar e o arquivo dele não está em `current\instalar\`: nada é baixado nem anunciado
  (D-833); registra; tenta de novo na próxima. Disco sem espaço para o motor: confere antes (como no `atualizador-4`).
- Disco cheio no download: o Velopack falha; o arquivo `.partial` fica e é apagado no próximo download (fato, `manager.rs`
  L437-480); registra; tela nada.
- Outro download segurando a tranca do Velopack (duas janelas abertas): `download_updates` falha pela tranca (fato,
  `manager.rs` L406); registra; a outra janela segue.
- Fechar o programa no meio do download: o fio de trás morre com o programa; fica o `.partial`; nada a desfazer.

**Trocar**
- O arquivo em `packages\` não tem a soma assinada (trocado depois de baixar): não troca; anota "recusada".
- Outra janela do programa aberta: não troca; registra; o aviso volta na próxima abertura.
- A janela não fecha no "Reiniciar agora" (ela recusou fechar): nada é trocado; o aviso continua valendo.
- O programa demora mais de 60 s para sair depois de pedir a troca: o Velopack o fecha à força (fato, documentação
  `docs.velopack.io/integrating/overview`). Por isso a troca é pedida só **depois** de gravar e parar os trabalhos.
- Outro programa segura um arquivo de `current` (antivírus, Explorador aberto na pasta): o Velopack tenta 10 vezes e
  desiste antes de mexer ("Unable to start the update", fato, `apply_windows_impl.rs` L161-163); reabre a anterior com os
  nossos argumentos (fato, `apply.rs` L56-60); ela vê que continua na versão de antes, anota a falha "troca" e a tela
  avisa uma vez.
- Falha da **segunda** troca de nome ("the app was left in a broken state", fato, L174-176): `current` fica faltando; o
  programa não abre. Remédio: reinstalar pelo `.msi` (os projetos ficam). É o defeito do Velopack que a D-779 quer cercar;
  a proteção ficou para depois (ressalva 6).
- Desligar no meio da troca: o mesmo caso acima, se for entre as duas trocas de nome; senão, ou trocou ou não trocou.
- A volta precisa de internet (baixar a anterior); sem internet: anota a falha, a tela diz o que ficou (pergunta 4) e a
  versão nova abre se conseguir.
- A versão anterior não está entre os 10 "Releases" mais novos do GitHub: o Velopack não a acha (fato, `sources/github.rs`
  L80, `per_page=10`); igual a "sem internet". Só acontece se houver mais de 9 versões publicadas depois dela.

**A pasta sem a licença (instalação antiga, reinstalação):** igual à primeira abertura: pergunta. Sem o "Sim", nada se
procura (se procurasse, o Velopack usaria a pasta de reserva e pediria licença em toda troca: fato, `locator.rs` L159-176
e `apply_windows_impl.rs` "Re-launching as administrator").

---

## 8. O que o desenho antigo deixou nos PCs

- **No notebook do Kaique:** nada. O desenho antigo nunca foi instalado lá (lá há só o instalador antigo de 28/10, que o
  passo 3 tira).
- **No PC do Samuel:** as tarefas `\EditorImpressao\Procurar versao nova` (desligada no experimento) e
  `\EditorImpressao\Desfazer testes a distancia`, a pasta `\EditorImpressao` do Agendador, `C:\ProgramData\EditorImpressao\atualizacao\`
  (do sistema; a conta comum só lê; o programa novo não conseguiria gravar o registro ali), `...\testes-a-distancia\desfazer.ps1`
  e o `fonte-de-teste.txt` (fica: o programa novo continua usando nas provas).
- **O que o programa novo limpa sozinho:** só o ajudante antigo, e só por segurança (passo 1 de 4.4), na mesma pergunta,
  antes da licença. Nada mais: escrever limpeza para um estado que só existe num PC é código a mais (D-819).
- **O resto:** à mão, pela gerente, com o Samuel vendo, numa pergunta do Windows, antes da prova à vista. O jeito mais
  limpo: desinstalar a 1.1.x por "Programas e Recursos" (o gancho dela manda rodar o "desfazer", que apaga o ajudante e a
  si mesmo), conferir só lendo o que sobrou e apagar o resto com o "sim" dele (pergunta 7). Fora do projeto, eu não apago
  nada.
- **Não sei se o experimento de 23/11 foi desfeito** (o passo 6 do roteiro). Se a pasta continua com Modificar para
  Usuários e a tarefa do ajudante existe (desligada), um administrador que a ligasse rodaria como o sistema um `.exe` que
  qualquer conta pode trocar. Sugestão à gerente: conferir só lendo (`icacls` da raiz e `schtasks /Query`) e, se for o
  caso, apagar a tarefa logo.

---

## 9. Os arquivos que vou mexer

Programa:
- `atualizacao.py` (refeito; ~400 linhas).
- `core/fases_da_atualizacao.py` (novo).
- `core/conversa_com_o_velopack.py` (novo).
- `core/windows.py`: `comecar_pedido_de_licenca`/`PedidoDeLicenca` (e `pedir_licenca` por cima delas); os três tipos de
  passo novos; `ler_versao_do_visual_c`, `ler_instalacao_do_inno`, `dono_do_arquivo`; `programas_rodando_de` (do
  `atualizador-4`).
- `core/ocr_kraken.py`: o lugar do motor no instalado (do `atualizador-4`).
- `configuracoes.py`: sai a marca (do `atualizador-4`).
- `main.py`: só comentários (a ordem já é a certa).
- **Tela, precisa do "pode" explícito da gerente (o implementador não mexe em `ui/` sem isso):**
  `ui/aviso_de_atualizacao.py` (sai o relógio de 5 em 5 minutos; recebe os efeitos; o "Atualizar agora?"),
  `ui/janela_principal.py` (uma chamada no `closeEvent`, antes de aceitar o fechar), `ui/testes_a_distancia_ui.py` (a
  primeira abertura não pergunta mais nada ao Windows; a senha não liga nada), `ui/brasao_girando.py` (deixa de pôr a marca
  e de esperar a janelinha).

Testes:
- novos: `tests/test_fases_da_atualizacao.py`, `tests/test_atualizador_novo.py` (e os do motor vindos do `atualizador-4`).
- `tests/test_trava_windows.py` (catraca, seção 10).
- os antigos da seção 2, **só depois do "sim" dele** (pergunta 5).

Não mexo: `empacotar.py`, `publicar_versao_kaique.py`, `core/testes_a_distancia.py`, `core/_testes_a_distancia_windows.py`,
o porteiro e a lista de exceções. Qualquer outro arquivo, só com o "pode" da gerente.

---

## 10. As travas

**A catraca (`tests/test_trava_windows.py`):** saem da `LISTA_CONGELADA` as 12 linhas de `atualizacao.py` (o
`import subprocess`; as 5 de `_dono_do_arquivo`; as 2 de `marcar_programa_aberto`; as 2 de `_marca_existe`; a de
`_ler_versao_do_visual_c`; a de `_ler_chave_do_inno`). `TETO` desce de 46 para **34**. As 8 de
`core/_testes_a_distancia_windows.py` ficam (os testes à distância não mudam nesta entrega). Os arquivos novos não usam
`ctypes`, `subprocess`, `winreg` nem `os.startfile`. O `core/windows.py` é o dono (não entra na lista). Se no meio do
código eu precisar de um lugar novo fora dos donos, a catraca falha e eu paro.
- Proposta (só com o "pode" da gerente; não é lugar novo, é capacidade nova): "Velopack" como capacidade com dono
  `core/conversa_com_o_velopack.py`, para a trava cobrar que ninguém mais importa `velopack`.

**O porteiro (`tests/conferencias_excecoes.json`, eu não mexo):** quando `atualizacao.py` for refeito,
`tests/test_conferencias_excecoes.py::test_o_repositorio_so_tem_os_erros_que_a_lista_deixa` vai falhar com:
- **40 linhas "a lista de exceções tem um lugar que o código já não tem (sobraram 0 de 1): tire ou diminua o item ..."**,
  uma por item de `atualizacao.py`: 33 K01 (`_aplicar_pacote_quando_sair` 2, `_dono_do_arquivo` 5, `_lancar_escondido` 3,
  `_ler_chave_do_inno` 4, `_ler_versao_do_visual_c` 5, `_linhas_da_janelinha` 1, `_marca_existe` 3, `apagar_tarefa` 1,
  `comando_de_rodar_a_tarefa` 1, `criar_tarefa` 1, `marcar_programa_aberto` 1, `passo_de_preparar_o_computador` 1,
  `script_de_trocar_e_reabrir` 4, `update_exe` 1), 2 K02 e 5 K04. O comando que a mensagem sugere é o da gerente.
- **Um K03 novo em `core/windows.py`** (a função do passo `dar_licenca_aos_usuarios`): a K03 vale "em qualquer arquivo do
  programa (até na peça única)". Não há como dar a licença sem isso. Pergunta 6.
- Os arquivos novos não terão nenhuma palavra da K01 no código (nem `Update.exe`: ver 4.5) nem número de decisão em texto
  de tela ou de registro (K04).
- O juiz do GitHub usa a lista da versão de teste: a rodada vai dizer "BARROU" até a gerente juntar a lista nova.

---

## 11. Como vai provar (D-767, D-811 a D-813, D-827)

**Testes de comportamento, não de texto.** Nenhum teste confere se uma palavra está num texto de PowerShell (não haverá
PowerShell no atualizador).
- **A regra, exaustiva:** `tests/test_fases_da_atualizacao.py` passa por **todos** os pares (fase, evento) e cobra a
  fase e os efeitos de cada um, numa tabela escrita no teste; e lê a árvore do arquivo para cobrar que ele não importa
  nada que fale com o mundo de fora.
- **O executor, com as duas peças de mentira só na borda** (a de mentira anota o que pediram; a lógica em volta é a de
  verdade): abrir sem licença → o primeiro efeito é a pergunta e nenhum `procurar`; "Não" → nada procurado nem gravado;
  "Sim" com o Visual C++ falhando → a licença não é pedida (a peça de verdade para no passo; teste da peça); assinatura
  errada → nenhum `baixar`; motor fora → nada anunciado; "Reiniciar agora" → a janela fecha antes de `trocar`; "Depois" +
  fechar + "Sim" → `trocar` com "sem janela"; reaberto na anterior → falha "troca"; teste rápido falha → `voltar` com o
  pacote assinado; outra janela aberta → não troca.
- **Uma prova por proteção, que falha quando ela é desligada** (o verificador desliga cada uma numa cópia e mostra a
  falha): (1) sem licença não procura; (2) assinatura antes de baixar; (3) soma conferida no arquivo antes de trocar; (4)
  motor antes de anunciar e antes de trocar; (5) a licença é o último passo; (6) o ajudante antigo sai antes da licença;
  (7) a conta de testes não procura nem pergunta; (8) versão que falhou não é tentada de novo; (9) outra janela aberta
  não troca; (10) a troca só depois de a janela fechar; (11) a volta só com pacote assinado; (12) pelo código nada roda;
  (13) só `trocar` chama a troca do Velopack.
- **A biblioteca do Velopack de verdade**, sem trocar nada: uma instalação falsa numa pasta de prova (como a do
  pesquisador), uma fonte de pasta com duas versões: `procurar` acha a nova; o pacote da anterior é montado e **baixado**
  para a pasta de prova com o tamanho e a soma conferidos pelo próprio Velopack. Não chama `trocar` (isso roda o
  atualizador do Velopack: só à vista).
- **A peça do Windows de verdade, no GitHub** (máquina jogada fora, como os testes de tarefa de hoje; no PC do Samuel
  não roda, D-785): o passo da licença numa pasta de prova → um arquivo de dentro passa a ter Modificar herdado, nenhuma
  linha antiga sumiu, a herança não foi cortada; e o teste de gravar dá "não" antes e "sim" depois.

**Só se prova rodando de verdade, à vista, no PC do Samuel** (D-767, D-785, D-773: as versões servidas por uma janela
visível; uma conta sem a janela "como administrador"):
1. Instalar pelo `.msi`; primeira abertura: a pergunta vem no meio da tela, logo no clique (print). "Não" → abre; fechar
   e abrir → pergunta de novo. "Sim" → abre; a licença lida de volta; o motor posto; o Inno de 01/09 tirado (D-729).
2. Publicar uma versão de prova; abrir → aviso; "Reiniciar agora" → janelinha do Velopack (print) → abre na nova.
3. Outra versão; "Depois"; fechar → "Atualizar agora?" (print) → "Sim" → janelinha → abrir → já na nova, sem espera.
   "Não" → abrir → o aviso volta.
4. Uma versão quebrada de propósito → volta para a anterior → a frase (print).
5. Uma versão com assinatura falsa → recusada → a frase (print).
6. Fechar a janela das versões no meio do download → nada na tela, nada quebrado; abrir de novo → baixa.
7. Tirar o motor do lugar → nada anunciado.
8. Clicar no atalho durante a janelinha do Velopack → a troca termina.
9. Desinstalar → a pasta inteira some (com o motor); os projetos ficam.
10. Medir: quanto tempo a abertura do programa instalado leva antes e depois (o teste de gravar), e os segundos sem
    nada na tela depois da troca.

Antes da prova, quem tenta quebrar (agente novo, D-775/D-815) confere a leitura do Velopack desta seção e da 4.5 contra o
código dele.

---

## 12. Perguntas para o Samuel (§11.13; a gerente leva à Central)

Antes de cada uma procurei no Livro (D-705 a D-833) e no `resposta-do-fable.md`; o porquê de ainda estar aberta vai em
cada uma. Prints: não há tela nova ainda; os prints das perguntas 1 a 3 só existem depois do código (a gerente pode
montar um desenho da caixa com o texto antes de publicar).

**Pergunta 1 — A ordem da primeira abertura**
- *Do que se trata:* a primeira vez que o Kaique abre o programa instalado. Hoje aparece primeiro a janelinha da senha
  dos testes à distância e, depois do clique nela, a pergunta do Windows "Deseja permitir...?".
- *O que muda:* para a pergunta do Windows vir sempre no meio da tela (como você escolheu em 19/11), ela passa a vir
  **logo depois do clique no atalho, antes da janela do programa**. A janelinha da senha aparece depois, quando a janela
  já abriu. A senha continua sem ligar nada nesta versão, como você decidiu em 21/11.
- *O que você escolhe:* (1) **sugestão:** a pergunta do Windows primeiro, a senha depois; (2) a senha primeiro, e a
  pergunta do Windows depois dela, só na primeira vez (nas aberturas seguintes, depois de um "Não", ela vem antes da janela
  do mesmo jeito); (3) só comentário.
- *O que muda no que já funciona:* só a ordem das duas janelas na primeira vez. Situação: plano, nada feito.
- *Por que pergunto:* você decidiu a pergunta "no instante do clique" e a senha "na primeira vez", mas nunca a ordem
  entre as duas.

**Pergunta 2 — O texto da pergunta ao fechar e do aviso da versão nova**
- *Do que se trata:* quando chega uma versão nova com o programa aberto, aparece o aviso "Reiniciar agora / Depois". Hoje
  ele diz: "Se escolher "Depois", a versão nova entra sozinha na próxima vez que você abrir o programa." Com a sua
  escolha de 19/11, o "Depois" passa a perguntar ao fechar. Você disse que o texto da pergunta ao fechar seria decidido
  antes de construir.
- *O que você escolhe:*
  - Aviso: (A) "Se escolher "Depois", o programa pergunta de novo quando você fechar." (B) "Se escolher "Depois", você
    pode atualizar quando fechar o programa."
  - Pergunta ao fechar: (A, sugestão) título "Atualizar agora?", texto "Há uma versão nova do programa pronta. Quer
    atualizar agora, ao fechar? Leva uns 2 minutos e da próxima vez o programa já abre na versão nova.", botões
    "Atualizar agora" e "Agora não". (B) o mesmo título, texto curto "Quer atualizar o programa agora, ao fechar?",
    botões "Sim" e "Não". (C) só comentário.
- *O que muda no que já funciona:* só esses textos. Situação: plano.

**Pergunta 3 — O ícone perto do relógio**
- *Do que se trata:* em 19/11 você pediu que, no "Sim" ao fechar, aparecesse um ícone perto do relógio com a
  porcentagem. Em 23/11 você disse que a janelinha da troca é a do próprio Velopack, por enquanto. A janelinha do
  Velopack aparece no meio da tela, em português ("Atualizando para a versão X, aguarde..."), com uma barra.
- *O que você escolhe:* (1) **sugestão:** nesta versão, no "Sim" ao fechar aparece a mesma janelinha do Velopack do
  "Reiniciar agora"; o ícone perto do relógio vai para a lista de espera, junto com o texto e o brasão nossos; (2) fazer o
  ícone agora (é uma janela nossa, que precisa ficar viva depois que o programa fecha: volta parte do que o desenho novo
  tirou); (3) só comentário.

**Pergunta 4 — Os três avisos de falha**
- *Do que se trata:* em 18/11 você escolheu três frases, uma para cada falha da atualização; em 21/11 elas ficaram para
  uma atualização depois. Hoje existe só uma: "A atualização não deu certo. O programa voltou para a versão anterior e
  continua funcionando. Avise o Samuel."
- *O que acontece se continuar uma só:* em dois casos a frase diz uma coisa que não aconteceu: quando a versão chega sem
  a sua assinatura (o programa nem saiu da versão dele) e quando a volta não deu certo (ela diria "voltou").
- *O que você escolhe:* (1) **sugestão:** as três frases que você já escolheu entram agora (é só escolher a frase certa
  para cada caso; nada de tela nova); (2) continua uma frase só nesta versão; (3) só comentário.

**Pergunta 5 — Os testes antigos do atualizador**
- *Do que se trata:* o programa tem testes automáticos que conferem, a cada mudança, o que você decidiu sobre a
  atualização. Muitos conferem as peças que saem (o ajudante que rodava como o sistema, os scripts, a nossa janelinha, as
  marcas) ou decisões que você mesmo mudou depois (o "Depois" na próxima abertura virou "ao fechar"; a nossa janelinha
  virou a do Velopack).
- *O que você escolhe:* (1) **sugestão:** (a) os que conferem peças que saem saem, e cada decisão que eles cobravam e
  continua valendo ganha um teste novo pelo caminho novo; (b) os que cobram as mesmas decisões passam a chamar o caminho
  novo, com a mesma conferência; (c) os que cobram decisões que você mudou passam a cobrar o que vale hoje. A lista, teste
  por teste, vai com a entrega, e o verificador mostra cada teste novo falhando no código de antes; (2) mostrar a lista
  antes, um por um; (3) só comentário.
- *O que muda no que já funciona:* nenhum comportamento que você escolheu deixa de ser conferido.

**Pergunta 6 — O porteiro e a licença da pasta**
- *Do que se trata:* o porteiro é a conferência automática que barra código com erro já conhecido. Uma das regras
  proíbe mexer na licença de pasta em qualquer parte do programa, por causa do defeito de 18/11 (uma tranca feita à mão
  deixou arquivos sem leitura). O desenho novo precisa fazer isso uma vez: **acrescentar** "Usuários podem modificar" na
  pasta do programa, sem tirar nada.
- *O que você escolhe:* (1) **sugestão:** a regra passa a deixar só essa função da peça do Windows, e só para acrescentar
  (nunca tirar herança nem trocar dono); continua barrando em todo o resto; (2) o lugar entra na lista de exceções; (3) só
  comentário.
- *O que muda no que já funciona:* nada para o Kaique. Sem uma das duas, o trabalho não entra.

**Pergunta 7 — A limpeza do seu PC antes da prova**
- *Do que se trata:* o atualizador antigo deixou no seu PC duas tarefas do Windows, uma pasta delas no Agendador e duas
  pastas em `C:\ProgramData\EditorImpressao` (uma delas impede o programa novo de gravar o registro da atualização). No
  notebook do Kaique não há nada disso.
- *O que você escolhe:* (1) **sugestão:** antes da prova, desinstalar a versão de teste pelo "Programas e Recursos" (ela
  mesma apaga as tarefas), a gerente confere só lendo o que sobrou e mostra a lista, e o que sobrar é apagado com o seu
  "sim", com você vendo; o programa novo só apaga sozinho a tarefa antiga do ajudante, se achar, por segurança; (2) o
  programa novo apaga tudo isso sozinho, em qualquer PC; (3) só comentário.

---

## Ressalvas do plano

1. **A pergunta sem janela dona:** pedir a licença antes de existir janela confia no direito de vir para a frente que o
   Velopack passa ao programa. Li o código que dá esse direito; não provei que a pergunta vem no meio da tela assim. É o
   primeiro item da prova à vista; se piscar, a saída é perguntar com a janela já aberta (o que a espera da volta 4
   tentava resolver).
2. **A herança da licença em arquivos abertos:** não conferi que o Windows muda a licença de um arquivo em uso (o
   programa roda de `current` durante a preparação). A leitura de volta pega; a prova à vista confirma.
3. **Segundos sem nada na tela** depois da janelinha do Velopack, enquanto o teste rápido roda. Não medi.
4. **A volta baixa a anterior** (uns minutos, nada na tela; a versão quebrada fica aberta nesse tempo). É o
   comportamento do `atualizador-4`; guardar a versão que funciona (a proteção da D-779) resolveria e ficou para depois.
5. **Uma troca que falha por um arquivo preso** põe a versão em "não tentar" (como hoje), mesmo sendo passageira.
6. **O defeito do Velopack** na segunda troca de nome (programa sem `current`) continua sem proteção nesta entrega.
7. **Conta padrão:** se a do Kaique não for administradora, a pergunta pede a senha de um administrador. Não conferi.
8. **"Programas e Recursos"** fica na versão do instalador (o Fable deixou para depois).
9. **O registro no `ProgramData`** é criado pela conta do Kaique: outra conta do PC só lê, e desinstalar não o apaga.
10. **O botão das Configurações dos testes à distância** continua chamando o caminho antigo (`core/_testes_a_distancia_windows.py`,
    com o "Não" lido como 0 por falta do `use_last_error`). Não faz parte desta entrega (D-825 só tirou a senha da
    primeira abertura), mas está ao alcance do Kaique.
11. **A leitura do Velopack** foi feita no código da etiqueta `1.2.161` (clone no rascunho, `92d6a1c9`), arquivos e
    linhas citados acima; o que não citei com linha não conferi.

## Ideias para a Lista de espera

- Guardar o pacote da versão que funciona antes de trocar (volta sem internet e sem os minutos de espera; é a D-779).
- Uma troca que falha por arquivo preso não deveria pôr a versão em "não tentar".
- O brasão girando durante o teste rápido da versão nova.

---

# ONDE-PAREI — a trava dos donos, terceira volta (23/11/2026)

Implementador. Ramo `atualizador-novo-2026-11-23`, worktree `.claude/worktrees/atualizador-novo`, a partir de
`d792ebfc`. Pedido da gerente de 23/11/2026, com a revisão do Fable aos 5 pontos que não fechavam na segunda volta.

**Situação: a terceira volta está feita e esperando a gerente.** A trava passa hoje, pela catraca: 46 lugares
congelados, `TETO = 46`. Rodei `D:\programas\EditorImpressao\.venv\Scripts\python.exe -m pytest tests\test_trava_windows.py -q`:
**40 passed, 3 skipped** (as três pendências paradas). Só mudaram `tests/test_trava_windows.py` e este arquivo. As voltas
anteriores ficam abaixo, como estavam.

## Decisões que esta tarefa precisa cumprir

- **D-830 (23/11/2026):** "refazer", e a trava do Fable: cada capacidade só no seu dono, "binário, sem lista de
  exceções". Nesta volta: a catraca no lugar do `xfail`, o mapa final, os nomes proibidos ao dono das DLLs e as raízes.
- **D-765:** nenhuma linha do programa muda. Não mudou: só o teste e o ONDE-PAREI.
- **§11.8 / D-605:** nenhum teste antigo muda. Nenhum teste de fora deste arquivo foi tocado (ver a ressalva 6 sobre as
  provas da segunda volta, que são deste mesmo arquivo novo).
- **D-809:** nada de comando que mude o `.git` inteiro. Só `git ls-files` pela peça do git, e `git add`/`commit`/`push`.
- **D-793 / §11.11:** não abri outro agente. Não abri janela nem rodei o programa.
- **Do pedido:** nada no porteiro e nada no `empacotar.py`.

## Como cumpri cada uma

- D-830: a trava é binária para lugar novo (falha na hora) e sem lista de exceções que cresça (a lista congelada só
  diminui, com teto). Provas na seção "As provas".
- D-765, porteiro, `empacotar.py`: `git diff --stat` mostra só `tests/test_trava_windows.py` e este arquivo.
- §11.8: nenhum arquivo de teste além deste foi aberto para escrita.
- D-809 / D-793: só os comandos acima; nenhum agente aberto.

## O que já está escolhido e testado aqui

- A primeira e a segunda volta deste mesmo teste (só neste ramo). O desenho dos donos da segunda volta continua; o mapa
  mudou pelo pedido (o `subprocess` agora tem dois donos).
- O porteiro e a lista de exceções (`regras_dos_agentes/`): não mexi. O porteiro (`conferir_codigo`) rodado no arquivo
  novo dá 0 achados.

## Como fica para quem usa e no livro

Nada muda para o Kaique nem no PDF: nenhuma linha do programa mudou. O que muda é a rodada do GitHub: a trava agora
passa (sem `xfail`) e fica vermelha na hora em que alguém usar uma capacidade num lugar novo fora do dono, ou quando
um lugar da lista for consertado sem tirar a linha.

## O que mudou no teste

1. **Catraca no lugar do `xfail`.** A marca saiu. `LISTA_CONGELADA` tem os 46 lugares de hoje, um por linha, separados
   em grupos com comentário. `conferir_a_catraca` cobra:
   - **lugar novo:** chave acusada que não está na lista falha na hora ("LUGAR NOVO ...", com a linha onde está);
   - **lugar perdoado à toa:** chave da lista que não é mais acusada falha com "tire esta linha da lista e abaixe o
     teto";
   - **o teto:** `assert len(LISTA_CONGELADA) <= TETO`, `TETO = 46`; e linha repetida na lista também falha.
   - Falha de leitura (raiz que falta, `OCULTOS` ilegível, arquivo que não abre) nunca entra na catraca: sempre falha.
2. **A chave do lugar:** `"arquivo | função onde mora | capacidade | o que foi achado"`, sem o número da linha. Ex.:
   `atualizacao.py | _marca_existe | Windows pelo ctypes | usa ...windll`. A função vem da peça de leitura do porteiro
   (`leitura.funcao_em_volta`, com a classe na frente: `BibliotecaScanTailor._carregar`); fora de função, `(fora de
   função)`. **Por quê:** escrever código acima não muda nenhuma das quatro partes (tem prova: dez linhas novas acima,
   mesma chave, linha diferente). Quando o lugar muda de verdade (outra função, outro jeito de importar, outra
   capacidade), a chave muda, e a catraca acusa um novo e um que sumiu, que é o certo. O mesmo jeito repetido na mesma
   função é um lugar só (os doze `wintypes.DWORD` do corpo de `core/_testes_a_distancia_windows.py` são uma linha).
3. **Mapa final dos donos:** `core/windows.py` → `ctypes` (com "Windows pelo ctypes"), `winreg`, `os.startfile`,
   `subprocess`; `core/nativo_dll.py` → `ctypes` e carregar DLL; `core/processos.py` → `subprocess`. O
   `core/windows.py:91` (`import subprocess`) saiu da lista. O `explorer /select` do `historico.py` continua acusado.
4. **`os.system/popen/spawn*/exec*`:** continuam proibidos em todo lugar, inclusive nos donos. Nada mudou
   (`test_rodar_programa_pelo_os_nao_tem_dono`).
5. **Os nomes do Windows no dono das DLLs:** `windll`, `WinDLL`, `oledll`, `OleDLL`, `wintypes`, `get_last_error`,
   `FormatError`, `GetLastError` viraram a capacidade "Windows pelo ctypes", cujo único dono é `core/windows.py`. São
   acusados como atributo (pelo nome, venha de onde vier: `ctypes.windll`, `kernel32.GetLastError`), como nome importado
   (`from ctypes import windll` e o uso dele), no `import ctypes.wintypes`, no `from ctypes.wintypes import ...` e no
   `getattr(ctypes, "windll")`. Ver o ponto 2 de "O que não fechou": isso vale em todo arquivo, não só no dono das DLLs.
6. **Raízes do fechamento** (`raizes_do_programa`): `main.py`; `motor_kraken/servidor_kraken.py`, procurando os módulos
   na pasta dele (roda com `python -I servidor_kraken.py`, então a pasta do script é onde o Python procura); e os módulos
   nossos da `OCULTOS` do `empacotar.py`.
   - **A `OCULTOS` dá para ler sem rodar:** é `OCULTOS = [...]` no corpo do `empacotar.py` (linha 165), uma lista de
     textos fixos, usada só em `for modulo in OCULTOS: comando += ["--hidden-import", modulo]` (linhas 883-884). Lida
     com `ast.literal_eval`. Se um dia ela for montada por função, ganhar `append`/`+=`, outra atribuição, um
     `--hidden-import` fora do laço, ou aparecer `--collect-submodules`/`--collect-all`/`--hiddenimport`, a leitura
     falha e diz a linha. Módulo que parece nosso (`core.x`) e não tem arquivo também falha. O `empacotar.py` não mudou.
   - Os 8 módulos nossos da `OCULTOS` (`core.gravura_scantailor`, `core.st_ferramentas`, `core.ocr_comum`,
     `core.ocr_doctr`, `core.ocr_tesseract`, `core.ocr_kraken`, `core.ocr_comparar`, `core.ocr_diagnostico`) já estavam
     no fechamento do `main.py`. Os de fora (`doxapy`, `skimage.filters`, `PIL._tkinter_finder`, `onnxtr...`) ficam fora.
   - O fechamento passou de 121 para 122 arquivos: entrou só o `motor_kraken/servidor_kraken.py`.
   - **O motor do Kraken não usa nenhuma das capacidades** (nenhum lugar acusado nele). Ele só importa a biblioteca do
     Python, o numpy, o PIL, o kraken, o torch e o psutil. Não inventei dono.
7. **As duas pendências do `subprocess`**, paradas enquanto `core/processos.py` não existir (como a do `CDLL`):
   `test_pendencia_a_peca_do_windows_so_lanca_programa_da_pasta_do_windows` e
   `test_pendencia_a_peca_dos_processos_recusa_programa_da_pasta_do_windows`. Ver o ponto 1 de "O que não fechou".

## A contagem nova: 46 lugares, TETO = 46

- **(a1) Atualizador e testes à distância: 20.** `atualizacao.py` 12 (o `import subprocess`; `_dono_do_arquivo` 5;
  `marcar_programa_aberto` 2; `_marca_existe` 2; `_ler_versao_do_visual_c` e `_ler_chave_do_inno`, o `winreg`);
  `core/_testes_a_distancia_windows.py` 8 (5 no corpo do arquivo, 3 em `_rodar_elevado`, entre eles o `get_last_error`).
- **(a2) Windows de verdade em outras partes: 9.** `core/nucleos.py` 2, `core/ocr_comum.py` (`abrir_processo`) 2,
  `historico.py` 3 (o `explorer /select` e os dois `os.startfile`), `ui/brasao_girando.py` 2.
- **(b) As nossas DLLs: 12.** Os 10 `import ctypes` e os 2 `CDLL`.
- **(b) Os nossos processos: 5.** `core/ocr_comum.py`, `core/ocr_kraken.py`, `core/ocr_tesseract.py`,
  `core/paginas_em_outro_processo.py`, `ui/tela_de_carregamento.py`.
- Diferença para a segunda volta (34): sai o `core/windows.py:91` (−1); a contagem agora é por chave, e não por linha
  (não muda nada nos 33 que ficam: nenhuma chave deles se repete); e entram 13 chaves de "Windows pelo ctypes" (5 em
  `atualizacao.py`, 5 nos testes à distância, 1 em cada um de `core/nucleos.py`, `core/ocr_comum.py` e
  `ui/brasao_girando.py`). 34 − 1 + 13 = 46. Por linha seriam 61 (os `wintypes` repetidos).

## As provas (40 passam, 3 paradas)

- **Lugar novo falha:** `test_catraca_lugar_novo_falha_na_hora` (sozinho, e ao lado de um da lista). Conferido também no
  repositório de verdade, fora do teste: tirando a primeira linha da lista, a catraca diz "LUGAR NOVO ...
  atualizacao.py | (fora de função) | subprocess | import subprocess [atualizacao.py:114 ...]".
- **Lugar consertado falha pedindo para tirar da lista:** `test_catraca_lugar_consertado_pede_para_tirar_da_lista`.
  No repositório de verdade, com uma linha inventada a mais: "este lugar não é mais acusado: tire esta linha da lista e
  abaixe o teto: ...".
- **O teto:** `test_catraca_a_lista_nunca_passa_do_teto`. No de verdade, com `TETO` 45: "a lista congelada tem 46
  linhas e o TETO é 45: a lista só pode diminuir".
- **A chave não muda com código acima:** `test_catraca_a_chave_nao_muda_quando_se_escreve_codigo_acima`; e
  `test_catraca_o_mesmo_jeito_na_mesma_funcao_e_um_lugar_e_linha_repetida_na_lista_falha`.
- **Nomes proibidos no dono das DLLs:** `test_o_dono_das_dlls_nao_pode_o_windows_pelo_ctypes` (8 casos, um por nome:
  atributo, nome importado e atributo de variável; o mesmo texto em `core/windows.py` dá zero) e
  `test_o_dono_das_dlls_nao_pode_importar_o_wintypes_nem_pegar_por_getattr`.
- **Cada raiz entra no fechamento:** `test_raiz_do_hidden_import_entra_no_fechamento` (um módulo que só a `OCULTOS` põe
  é acusado; sem a raiz, escaparia), `test_raiz_do_motor_do_kraken_procura_na_pasta_dele`,
  `test_a_lista_dos_ocultos_montada_de_outro_jeito_e_falha` (7 jeitos) e `test_cada_raiz_de_verdade_entra_no_fechamento`
  (no repositório de verdade: as raízes lidas sem falha, e cada uma no fechamento).
- As provas da segunda volta continuam, três delas ajustadas ao mapa novo (ressalva 6).

## Caminho → função (§11.12)

| Caminho | O que usa |
|---|---|
| a trava (repositório) | `lugares_do_repositorio` → `raizes_do_programa` + `lugares_da_trava` → `conferir_a_catraca` |
| as provas com arquivos de exemplo | `lugares_da_trava` / `falhas_da_trava` (a mesma conta, sem ler o disco) |
| as raízes | `raizes_do_programa` → `ocultos_do_empacotar` (árvore do `empacotar.py`) |
| o fechamento | `fechamento` → `_indice` (por pasta de busca) → `modulos_pedidos` |
| as capacidades | `_usos_na_arvore` (uma só; `capacidades_usadas` é ela a partir do texto) |
| a função onde mora | `leitura.funcao_em_volta`, a do porteiro |
| ler o código / a lista do git | `leitura.arvore` / `git.arquivos_do_git`, as do porteiro |

## A peça de fora usada (§11.12.6)

- `ast.literal_eval` (https://docs.python.org/3/library/ast.html#ast.literal_eval): avalia só literais (textos, listas,
  tuplas...); com qualquer outra coisa (uma chamada de função, um nome) levanta `ValueError`. É o que transforma
  "lista montada de outro jeito" em falha. Recebe o nó, não o texto.
- `ast.For.iter` e `ast.Name.ctx` (`Load`, `Store`, `Del`): o laço do `--hidden-import` e as escritas na `OCULTOS`.
- O resto do `ast`, como na primeira volta.

## O que não fechou (não ajeitei; para a gerente decidir)

1. **A pendência "a peça do Windows só lança programa da pasta do Windows" não é o que a peça faz hoje.**
   `_caminho_do_programa` (`core/windows.py`, linha 1078) só deixa o caminho como o Windows o completa, para comparar.
   A regra do rodar genérico, `_por_que_recusa` (linha 1195), faz o contrário: recusa o programa da pasta do Windows
   (linha 1245) e deixa rodar os de fora. Hoje quem usa esse caminho para programa de fora: o `vpk`
   (`empacotar.py:1559`) e o `gh` (`publicar_versao_kaique.py:476`), pelo `rodar_em_grupo`; e o `janela_de_prova.py:209`,
   que roda o próprio Python. Os três são scripts, fora do fechamento do programa. **Escolhi parar as duas pendências
   até `core/processos.py` existir**, porque só então os de fora têm para onde ir. Se a gerente quiser outro momento,
   é uma linha em cada pendência. Também fica para decidir se o `vpk` e o `gh` vão para a peça dos processos ("os
   nossos processos" hoje são OCR, Kraken, servidor de páginas e brasão).
2. **"Windows pelo ctypes" vale em todo arquivo, não só no dono das DLLs.** O pedido diz "dentro de
   `core/nativo_dll.py`". Fiz como capacidade com um dono (`core/windows.py`), que é uma regra num lugar só. Por isso
   ela também acusa fora do dono, onde o `import ctypes` já era acusado: são 13 das 46 chaves. Ela separa sozinha o
   ctypes do Windows (vai para `core/windows.py`) do ctypes das DLLs (vai para `core/nativo_dll.py`). Acusar só dentro
   do `core/nativo_dll.py` daria 33 chaves, mas seria uma regra só para um arquivo.
3. **A catraca não impede a troca de uma linha por outra.** Quem conserta um lugar e, na mesma mudança, põe um lugar
   novo na lista no lugar dele, mantém o tamanho e passa no `<= TETO`. Só a revisão da mudança pega. Com `<=`, também
   não é obrigatório abaixar o teto ao tirar linha (a mensagem pede, mas passa sem). Pôr `==` obrigaria a abaixar e
   fecharia essa folga; não pus porque o pedido diz `<=`.

## Ressalvas

1. O mesmo jeito repetido na mesma função é um lugar só. Um segundo `windll` dentro de uma função que já tem um não é
   lugar novo. Um `windll` numa função nova é.
2. Renomear uma função muda a chave dos lugares dela: a catraca acusa um novo e um que sumiu, e a lista precisa ser
   trocada (é a troca do ponto 3 acima, por motivo bom).
3. Atributo com nome do Windows é acusado venha de onde vier (`x.GetLastError`). Hoje não dá alarme falso no programa.
   Se um dia der, aparece como lugar novo, nunca calado.
4. O motor do Kraken é lido procurando na pasta dele. Se um dia ele importar `core.x`, a trava não segue (no motor o
   `core` não vai junto, e o import quebraria lá).
5. O que a trava não pega continua escrito na docstring do teste.
6. **Três provas da segunda volta, deste mesmo arquivo, mudaram** porque o mapa mudou:
   `test_cada_dono_usa_a_sua_capacidade_e_nao_a_dos_outros` (o Windows agora pode `subprocess`),
   `test_o_mapa_dos_donos_so_usa_capacidades_que_existem` (dois donos do `subprocess`; a capacidade nova) e
   `test_acusa_cada_jeito_de_importar_e_de_usar` (dois achados a mais de "Windows pelo ctypes"). São do arquivo novo
   deste ramo, que ainda não entrou em lugar nenhum; nenhum teste de fora dele mudou.
7. Não disparei a rodada do GitHub (`[skip ci]`; o pedido manda rodar só este arquivo).

## Ideias para a Lista de espera

- Proteger a `LISTA_CONGELADA` e o `TETO` como os arquivos que só a gerente muda (a K17 do porteiro), para a troca de
  uma linha por outra (ponto 3 de "O que não fechou") não passar sem ela ver; e trocar o `<=` por `==`.

---

# Segunda volta — cabeçalho original (23/11/2026)

Implementador. Ramo `atualizador-novo-2026-11-23` (saiu de `obra-2026-10-26` em `c8531595`), worktree
`.claude/worktrees/atualizador-novo`. Pedido da gerente de 23/11/2026.

**Situação: a segunda volta (a última, D-815) está feita e esperando a gerente.** O teste continua em
`tests/test_trava_windows.py`, agora com o desenho dos donos do Fable. A trava acusa **34 lugares** e está marcada
`xfail(strict=True)`. As 14 provas passam, e a pendência do `CDLL` fica parada. A primeira volta, mais abaixo, fica como
histórico.

# Segunda volta (D-815, recado da gerente com a resposta do Fable aos 7 pontos)

## O que mudou no teste

- **A pergunta é outra.** Antes era "este import é permitido?". Agora é "quem é o dono desta capacidade?". O mapa está
  escrito uma vez, em `DONOS`, e as capacidades em `CAPACIDADES`.
  - `core/windows.py` pode `ctypes`, `winreg` e `os.startfile`.
  - `core/nativo_dll.py` pode `ctypes` e é o único que pode carregar DLL (`CDLL`, `cdll`, `PyDLL`, `pydll`).
  - `core/processos.py` pode `subprocess`.
  - "Rodar programa pelo `os`" (`os.system`, `os.popen`, `os.spawn*`, `os.exec*`) não tem dono.
  - O dono é acusado pelas capacidades que não são dele.
- **O que é programa:** o fechamento das importações a partir do `main.py` (`fechamento`). Não é lista nem a
  definição do porteiro. Hoje dá 121 arquivos, e nenhum deixou de ser lido.
  - **Importação dentro de função, de `if` e de `try`:** entra. O motivo é que o PyInstaller põe as quatro no `.exe`. A
    fonte é o PyInstaller 6.21.0 instalado, `PyInstaller/building/build_main.py`, linhas 60-77: `IMPORT_TYPES` e o
    texto "conditional: imported within an if-statement / delayed: imported within a function / optional: imported
    within a try-except-statement".
  - **`__import__("x")` e `importlib.import_module("x")` com o nome escrito por inteiro:** entram. O PyInstaller não os
    segue ("Analysis can detect nothing", https://pyinstaller.org/en/stable/when-things-go-wrong.html), mas o programa
    os carrega quando roda. O nome numa variável não se segue.
  - **Pacotes de cima** (`a/__init__.py` ao importar `a.b`) e **o `x` de `from a import x`** entram. O relativo vira
    absoluto. O que não é do repositório não entra. Ciclo não trava.
- **`CDLL`:** a trava só diz quem pode chamá-lo. O teste de execução ("todo caminho carregado está sob `core/nativo/`")
  está escrito como pendência, `test_pendencia_o_dono_das_dlls_so_carrega_dll_de_core_nativo`.
  - Ele fica parado enquanto `core/nativo_dll.py` não existe.
  - Ele falha no dia em que a peça existir sem a prova escrita.
  - A peça não foi inventada.
- **Marca:** `@pytest.mark.xfail(strict=True, reason="D-830: lista de trabalho do atualizador novo")`, só na trava.

## A nova contagem: 34 lugares

**(a1) Atualizador e testes à distância (10).** É a lista de trabalho do atualizador novo.
- `atualizacao.py`: 114 (`subprocess`), 432, 433, 750, 759 (`ctypes`), 1194, 1279 (`winreg`).
- `core/_testes_a_distancia_windows.py`: 32, 36 (`ctypes`), 34 (`subprocess`).

**(a2) Windows de verdade em outras partes (6).** Nada mudado nelas.
- `core/nucleos.py:44`: `ctypes`. A linha 78 usa o `kernel32` para ler a memória livre.
- `core/ocr_comum.py:209`: `ctypes`. A linha 211 usa `WinDLL kernel32` e o `SetDllDirectoryW`.
- `historico.py:7`: `subprocess`, para o `explorer /select`.
- `historico.py:199` e `:212`: `os.startfile`, para abrir a pasta e para imprimir.
- `ui/brasao_girando.py:223`: `ctypes`. Usa o `OpenProcess` para saber se o programa continua aberto.

**(b) DLL nossa (12).**
- Os `import ctypes`, mesmo os que só pegam os tipos: `core/caixas_scantailor.py:82`, `core/cores_scantailor.py:52`,
  `core/desentortar_scantailor.py:69`, `core/dividir_scantailor.py:45`, `core/endireitar_scantailor.py:62`,
  `core/gravura_scantailor.py:47`, `core/luz_scantailor.py:46`, `core/pontinhos_scantailor.py:63`,
  `core/preto_e_branco_scantailor.py:60` e `core/st_ferramentas.py:43`.
- Os dois `CDLL`: `core/gravura_scantailor.py:169` e `core/st_ferramentas.py:315`.

**(b) Processo nosso (5).**
- `core/ocr_comum.py:39`
- `core/ocr_kraken.py:89`
- `core/ocr_tesseract.py:87`
- `core/paginas_em_outro_processo.py:64`
- `ui/tela_de_carregamento.py:38`

**O próprio dono do Windows (1).** `core/windows.py:91`: `subprocess`. Ver o ponto 1 de "O que não fecha".

Conta: 10 + 6 + 12 + 5 + 1 = 34.

## O que saiu do escopo pela definição nova, e por quê

Saíram 31 lugares da primeira volta. Os arquivos onde eles estão não são importados a partir do `main.py`, então não
vão no `.exe`.
- `avaliar.py`: 3 lugares (26, 31 e 1655), a régua dos filtros. São a Área de Trabalho e o `python -c`.
- `teste_velocidade.py`: 17 lugares, o PowerShell, o registro e o `kernel32`.
- `compilar_detector_gravura.py`, `compilar_st_ferramentas.py`, `empacotar.py`, `empacotar_teste_velocidade.py` e
  `montar_motor_kraken.py`: os scripts de montar.
- `gerar_prints.py` e `teste_completo.py`.
- `conferencia.py` e `publicar_versao_kaique.py`.
- `teste_bateria.py` e `teste_robustez.py`.

Fora do fechamento há 45 arquivos que o porteiro conta como programa. Eles estão na lista `fora` da conferência que
rodei: os scripts da raiz, `motor_kraken/servidor_kraken.py` e três telas que nada importa (`ui/tela_opcoes.py`,
`ui/widgets/folhear_pdf.py`, `ui/widgets/trilha_ferramentas.py`). Nada entrou no fechamento que o porteiro não contasse
como programa.

## O que não fecha no desenho (não ajeitei: implementei ao pé da letra e deixo para decidir)

1. **O dono do Windows precisa rodar programas do Windows** (`schtasks`, PowerShell, `icacls`: `core/windows.py`, linhas
   1285, 1487 e 1662), mas o mapa não lhe dá `subprocess`. Ao pé da letra, ele é acusado (`core/windows.py:91`). Há
   dois caminhos: ele ganha o `subprocess`, e aí são dois donos do `subprocess`; ou ele pede ao `core/processos.py` para
   rodar, e aí "processos" deixa de ser "os nossos processos". O mesmo vale para o `explorer /select` do `historico.py`.
2. **"Rodar programa pelo `os`" não tem dono no desenho.** Ao pé da letra, ficou proibido em todo lugar, até nos três
   donos. Tem prova: `test_rodar_programa_pelo_os_nao_tem_dono`. Hoje ninguém do programa usa.
3. **O dono das DLLs pode o `ctypes` inteiro.** Então ele poderia chamar o Windows (`windll`, `WinDLL`) sem ser
   acusado. O desenho não separa "ctypes para a DLL nossa" de "ctypes para o Windows", e a trava não separa.
4. **O `.exe` não é só o `main.py`.**
   - O motor do Kraken é um programa à parte (`motor_kraken/servidor_kraken.py`, montado por `montar_motor_kraken.py`)
     e vai para o Kaique. Ele fica fora do fechamento. Hoje não usa nenhuma capacidade, mas a trava não o vigia.
   - O `empacotar.py` também põe `--hidden-import` (`OCULTOS`). Hoje todos os módulos nossos dessa lista já estão no
     fechamento. Um módulo que entrasse só ali escaparia.
5. **O `SetDllDirectoryW` do `core/ocr_comum.py:211`** é do Windows pelo desenho, mas é um passo de "abrir o nosso
   processo". Quando o código for mudado, o `core/processos.py` terá de chamar o `core/windows.py` para isso. É
   coerente, mas fica escrito.

## As provas (14 passam, 1 parada, a trava `xfail`)

Rodei `D:\programas\EditorImpressao\.venv\Scripts\python.exe -m pytest tests\test_trava_windows.py -q` em 23/11/2026.
Resultado: **14 passed, 1 skipped, 1 xfailed.**

- `test_fechamento_dentro_acusa_e_fora_nao_acusa`: o mesmo `import ctypes` é acusado em `core/usa.py`, que o
  `main.py` importa, e não é acusado em `solto.py`, que ninguém importa.
- `test_fechamento_segue_funcao_if_try_relativo_from_e_texto`: a importação dentro de função, de `if`, de `try`, a
  relativa, o `from pacote import modulo`, o `import_module("x")` e o `pacote/__init__.py` entram.
- `test_fechamento_aguenta_ciclo_e_ignora_o_que_nao_e_do_repositorio` e
  `test_fechamento_que_nao_le_e_falha_nunca_passou` (arquivo que não abre, código ilegível, falta do `main.py`).
- `test_cada_dono_usa_a_sua_capacidade_e_nao_a_dos_outros`:
  - o Windows com `ctypes`, `winreg` e `startfile` não é acusado, e com `subprocess` e `CDLL` é;
  - as DLLs com `CDLL` não são acusadas, e com `subprocess` são;
  - os processos com `subprocess` não são acusados, e com `ctypes` são.
- `test_ctypes_so_para_os_tipos_tambem_e_acusado_fora_do_dono`: o `.ctypes` do numpy não é acusado à parte.
- `test_acusa_cada_jeito_de_importar_e_de_usar`: 17 achados, cada um com a capacidade certa.
- `test_rodar_programa_pelo_os_nao_tem_dono`, `test_nao_acusa_comentario_docstring_texto_nem_nome_parecido` (inclui
  `platform.system()` e `x.exec()`), `test_cada_modulo_proibido_e_acusado` (4 módulos) e
  `test_o_mapa_dos_donos_so_usa_capacidades_que_existem`.

## Ressalvas da segunda volta

- **A trava não pega:** `multiprocessing`, `asyncio.create_subprocess_*`, `sys.modules[...]`, o nome montado em
  pedaços, `nt`/`posix`, a importação com o nome numa variável, e o que o `.exe` leva sem o `main.py` importar (ponto 4
  acima). Está escrito na docstring do teste.
- **O `xfail(strict=True)` deixa a rodada passar com a trava falhando.** Se algum lugar sair da lista, ela continua
  `xfail`. Só quando zerar ela vira "passou inesperado" e falha, pedindo para tirar a marca. Então lugar novo também não
  deixa a rodada vermelha. Isso é o efeito da marca pedida, não um defeito.
- **Não disparei a rodada do GitHub** (`[skip ci]`; o pedido manda rodar só este arquivo).

# Primeira volta (histórico; o desenho e a lista de lá foram trocados pela segunda volta)

## Decisões que esta tarefa precisa cumprir

- **D-830 (23/11/2026):** "refazer". E a mensagem do Fable que o Samuel colou: "ela pode mandar escrever a primeira trava
  (o teste que diz 'só core/windows.py fala com o Windows'). Esse teste vai falhar hoje de propósito — a lista do que
  falha é a lista de trabalho do atualizador novo". Pela resposta do Fable, a trava é um "Teste de AST em `tests/`:
  `ctypes`, `subprocess`, `winreg`, `os.startfile` importados somente em `core/windows.py`. Binário, sem lista de
  exceções."
- **D-765 (17/11):** "eu não quero fazer nenhum conserto até o .exe estar pronto para o kaique [...]". Nenhuma linha do
  programa muda nesta tarefa.
- **D-791 / D-801 / D-802:** a lista de exceções do porteiro só ganha item com o "sim" dele. Esta tarefa não põe item
  nela.
- **D-605 (§11.8):** "nenhuma função nova [...] pode alterar o que já está escolhido e testado". Nenhum teste antigo foi
  mudado, e nenhum teste antigo quebra.
- **§11.12 (uma peça só):** a trava não pode virar uma segunda conferência da mesma regra ao lado da K01.
- **D-809:** nenhum comando que mude o `.git` inteiro. O teste só lê a lista do git (`git ls-files`), pela peça única
  do git.
- **D-793 / §11.11:** não abri outro agente.

## O que já está escolhido e testado aqui

- O porteiro (`regras_dos_agentes/porteiro.py`). A K01 procura a conversa com o Windows por palavras
  (`PALAVRAS_DO_WINDOWS`, PROTEGIDA "nao_some" em `protecao.py`). A definição de programa é `e_programa`, com
  `NAO_E_PROGRAMA` PROTEGIDA "igual". A peça única é `PECA_UNICA_DO_WINDOWS`.
- `tests/test_conferencias_*.py`: as provas do porteiro. Entre elas, `test_o_repositorio_so_tem_os_erros_que_a_lista_deixa`,
  que barra qualquer achado fora da lista "valendo". Esses arquivos estão em `porteiro_mudancas.PROTEGIDOS` (K17): só a
  gerente os muda.
- O juiz do GitHub (`juiz.py`) julga o ramo com o porteiro e a lista **da versão de teste**, não com os do ramo.

## A escolha: teste à parte, e não uma conferência dentro do porteiro

**Escolhi um teste à parte, `tests/test_trava_windows.py`. Quando for juntado, ele deve substituir a parte da K01 que
procura as mesmas coisas por palavras.** Os motivos:

1. **Pôr a regra dentro do porteiro quebraria um teste antigo.** A lista de exceções está "valendo". Uma conferência
   nova (K26, ou uma K01 que lê a estrutura) acharia os 62 lugares. Nenhum deles está na lista com essa conferência,
   então `test_o_repositorio_so_tem_os_erros_que_a_lista_deixa` passaria a falhar. Para ele voltar a passar, seria
   preciso pôr 62 itens na lista, o que exige o "sim" do Samuel (D-791) e foi proibido no pedido.
2. **O juiz do GitHub nem veria a conferência nova.** Ele usa o porteiro da versão de teste. Uma K26 feita neste ramo só
   valeria depois que a gerente a juntasse.
3. **Trocar a K01 por uma versão que lê a estrutura afrouxa a proteção.** Tirar linhas de `PALAVRAS_DO_WINDOWS` (o
   `winreg`, o `os.startfile`, o `windll`) é barrado por `protecao.py` ("nao_some") e pela K17. Não contornei. É mudança
   da gerente, com o "sim" do Samuel.
4. **Uma peça só, sem definição copiada.** O teste não tem definição própria de "programa" nem de "peça única". Ele
   importa `porteiro.e_programa` e `porteiro.PECA_UNICA_DO_WINDOWS`, lê o código com `leitura_do_codigo.arvore`, que é a
   mesma leitura do porteiro, e pega a lista dos arquivos com `conversa_com_o_git.arquivos_do_git`.
   **A sobreposição que existe hoje:** a K01 acusa por palavra `winreg`, `os.startfile`, `windll`/`WinDLL`/`CDLL` de DLL
   do Windows e o apelido da biblioteca. A trava acusa por estrutura o `import` de `ctypes`, `subprocess`, `winreg` e o
   uso de `startfile`. São duas conferências da mesma regra até a gerente decidir. Sugestão para quando juntar: a parte
   de imports, `winreg` e `startfile` da K01 sai, e fica a trava. As palavras do PowerShell, do `schtasks`, do `icacls`
   etc. continuam na K01 até virarem a segunda trava do Fable ("nenhum literal de string fora de `core/windows.py`
   contém `powershell`, `-Command` ou `.ps1`").

## Como fica para quem usa e no livro

Nada muda para o Kaique nem no PDF. Nenhuma linha do programa mudou, só um teste novo em `tests/`. O que muda é a rodada
do GitHub: **ela vai falhar enquanto houver lugar na lista**. Isso é de propósito (D-830), mas tem consequência. Veja as
ressalvas.

## Caminho → função (§11.12)

| Caminho | O que usa |
|---|---|
| o teste da trava (repositório inteiro) | `falhas_do_repositorio` → `falhas_nos_arquivos` → `lugares_proibidos` |
| as provas com arquivo de exemplo | `falhas_nos_arquivos` → `lugares_proibidos` (a mesma conta, sem ler o disco) |
| o que é programa | `porteiro.e_programa` (`NAO_E_PROGRAMA`), o mesmo do porteiro |
| a peça única | `porteiro.PECA_UNICA_DO_WINDOWS` |
| ler o código | `leitura_do_codigo.arvore`, a mesma do porteiro (aceita a marca de UTF-8 e levanta `CodigoIlegivel`) |
| a lista dos arquivos | `conversa_com_o_git.arquivos_do_git` (`git ls-files`, só lê), o mesmo de `porteiro.achados_do_repositorio` |

## O que pode falhar, e o que a trava faz em cada caso

- **Arquivo do programa que não abre ou não é texto UTF-8:** vira falha `arquivo:0: não deu para ler`. Nunca passa.
- **Código que o Python 3.14 não consegue ler:** vira falha `arquivo:0: o código não pôde ser lido`.
- **O git não responde:** `GitFalhou` sobe e o teste falha com o motivo. Nunca passa calado.
- **Comentário ou docstring que fala de `ctypes`:** não conta. Não é árvore de código. Tem prova.
- **O `.ctypes` de uma imagem do numpy** (`imagem.ctypes.data_as`, usado para entregar a imagem à DLL do ScanTailor):
  não é o módulo. Não conta sozinho, mas o `import ctypes` do mesmo arquivo é acusado, então nada fica escondido. Tem
  prova. Na primeira versão da trava eu contava esse `.ctypes`. Ela deu 80 lugares, 18 deles esse alarme falso, e
  estreitei a regra: só conta o módulo pego dentro de outro módulo importado no arquivo (`windows.subprocess`).

## A peça de fora usada: o `ast` do Python (§11.12.6)

Fonte: https://docs.python.org/3/library/ast.html (Python 3.14).
- `ast.Import`: `names` é uma lista de `alias(name, asname)`, e `name` traz o nome com ponto (`ctypes.wintypes`).
- `ast.ImportFrom`: tem `module` (None em `from . import x`), `names` e `level` (0 = absoluto; 1 ou mais = relativo).
- `ast.Call`: `func` e `args`. `ast.Attribute`: `value` e `attr`. `ast.walk` passa por todos os nós e não segue ordem.
  Por isso o resultado é ordenado no fim.
- Comentário não vira nó. Docstring é um `ast.Constant` e só conta se estiver numa das formas acima, o que não acontece.
- `__import__` (https://docs.python.org/3/library/functions.html#import__) e `importlib.import_module`
  (https://docs.python.org/3/library/importlib.html) recebem o nome do módulo como texto. Só o texto escrito por inteiro
  é lido.
- `os.startfile` só existe no Windows (https://docs.python.org/3/library/os.html#os.startfile) e está em `os.__all__`
  lá. Por isso `from os import *` é acusado.

## A prova de que a trava funciona

Rodei `D:\programas\EditorImpressao\.venv\Scripts\python.exe -m pytest tests\test_trava_windows.py -q` em 23/11/2026.
Resultado: **1 failed, 11 passed**.
- **Falha hoje:** `test_so_core_windows_fala_com_o_windows` acusa 62 lugares (a lista abaixo).
- **Acusa fora da peça e não acusa dentro:** `test_acusa_import_ctypes_fora_da_peca_e_nao_acusa_dentro` usa um arquivo
  de exemplo com `import ctypes`. Em `atualizacao.py` e em `core/qualquer.py` ele é acusado. O mesmo texto em
  `core/windows.py` dá zero.
- `test_usa_a_definicao_de_programa_do_porteiro`: o que está em `tests/`, `relatorios/`, `regras_dos_agentes/` e `docs/`
  não é acusado. Pasta nova e `.pyw` são acusados.
- `test_acusa_cada_jeito_de_importar_e_de_usar`: os 12 jeitos de importar ou usar, uma linha cada.
- `test_acusa_from_os_import_estrela_que_traz_o_startfile`, `test_o_ctypes_de_uma_imagem_do_numpy_...`,
  `test_nao_acusa_comentario_docstring_texto_nem_nome_parecido`,
  `test_codigo_ilegivel_e_arquivo_que_nao_abre_sao_falha_nunca_passou` e `test_cada_modulo_proibido_e_acusado` (4
  módulos).
- O porteiro rodado no próprio `tests/test_trava_windows.py` dá zero achados. O arquivo não tem comando do git (K25) e
  todas as funções têm docstring (K12).
- Não mexi no porteiro, então `tests\test_conferencias_codigo.py` não precisou rodar.

## A lista do que falha hoje (62 lugares, arquivo:linha)

### (a) Conversa com o Windows de verdade

**(a1) O atualizador e os testes à distância: a lista de trabalho do atualizador novo (10)**
- `atualizacao.py:114` `import subprocess`. Usado no `Update.exe apply` (L671), no PowerShell (L965), nos comandos do
  Windows de `_rodar` (L789) e no teste rápido, que roda o nosso próprio exe (L632).
- `atualizacao.py:432`, `:433` `ctypes`/`wintypes`: `GetNamedSecurityInfoW`, o dono do arquivo.
- `atualizacao.py:750` `ctypes`: `CreateMutexW`, a marca de "programa aberto".
- `atualizacao.py:759` `ctypes`: `OpenMutexW`, para conferir a marca.
- `atualizacao.py:1194` `winreg`: o Visual C++ está instalado?
- `atualizacao.py:1279` `winreg`: a chave do instalador antigo (Inno).
- `core/_testes_a_distancia_windows.py:32`, `:34`, `:36`: `ShellExecuteExW` "runas", PowerShell e `schtasks`.

**(a2) Windows de verdade em outras partes. Não é do atualizador; estão na lista de exceções como "depois da entrega"
(D-800/D-802) (24)**
- `avaliar.py:26`, `:1655`: `SHGetFolderPathW`, onde fica a Área de Trabalho (régua dos filtros).
- `core/nucleos.py:44`: `GlobalMemoryStatusEx`, a memória livre.
- `historico.py:7`, `:199`, `:212`: abrir a pasta no Explorer (`explorer /select`, `os.startfile`) e imprimir
  (`os.startfile(..., "print")`).
- `teste_velocidade.py:75` (PowerShell), `:362`, `:432` (`winreg`: placa de vídeo, processador), `:476`, `:641`,
  `:642`, `:1676`, `:1736`, `:1737`, `:1755`, `:1756`, `:1903`, `:1904`, `:1918`, `:1919`, `:2230`, `:2250`
  (`kernel32`/`user32`/`psapi`: memória, não dormir, janela preta, console).
- `ui/brasao_girando.py:223`: `OpenProcess`/`WaitForSingleObject`, o programa continua aberto?

### (b) Não é o Windows: DLL nossa, processo nosso, ferramenta de montar (27)

**DLL nossa do ScanTailor (`core/nativo/st_ferramentas.dll`, `st_gravura.dll`) (10).** Sugestão: uma peça única das
nossas DLLs. Hoje duas carregam a DLL, `core/st_ferramentas.py:315` e `core/gravura_scantailor.py:169`, cada uma com o
seu `CDLL` e o seu `add_dll_directory`. As outras só usam os tipos do `ctypes`.
- `core/caixas_scantailor.py:82`, `core/cores_scantailor.py:52`, `core/desentortar_scantailor.py:69`,
  `core/dividir_scantailor.py:45`, `core/endireitar_scantailor.py:62`, `core/gravura_scantailor.py:47`,
  `core/luz_scantailor.py:46`, `core/pontinhos_scantailor.py:63`, `core/preto_e_branco_scantailor.py:60`,
  `core/st_ferramentas.py:43`.

**Processo nosso (5).** Sugestão: uma peça única para abrir os nossos processos. `core/ocr_comum.abrir_processo` já
faz isso para os OCRs.
- `core/ocr_comum.py:39`: `abrir_processo`, o `Popen` dos OCRs.
- `core/ocr_kraken.py:89`: o motor do Kraken, com `PIPE` e `TimeoutExpired`.
- `core/ocr_tesseract.py:87`: `tesseract.exe --version` e `_matar`.
- `core/paginas_em_outro_processo.py:64`: o servidor de páginas.
- `ui/tela_de_carregamento.py:38`: o brasão em outro processo (`abrir=subprocess.Popen`).

**Ferramentas de montar, publicar e testar, que ficam na raiz e não vão no programa do Kaique (8).** Sugestão:
decidir se esses scripts são "programa" para a trava. Hoje são, pela definição do porteiro.
- `compilar_detector_gravura.py:42`, `compilar_st_ferramentas.py:44`: o `cmake`.
- `empacotar.py:115`: o PyInstaller e o compilador do Inno.
- `empacotar_teste_velocidade.py:68`: o PyInstaller.
- `montar_motor_kraken.py:98`: o `python`/`pip` do motor.
- `gerar_prints.py:15`: roda a si mesmo.
- `teste_completo.py:326`: roda `teste_robustez_completo.py`.
- `avaliar.py:31`: roda `python -c` para medir a abertura.

**Import que não conversa com nada (4).** Sugestão: tirar o import, quando a D-765 deixar mexer.
- `conferencia.py:71`: só `subprocess.list2cmdline`, que monta um texto.
- `publicar_versao_kaique.py:70`: só o tipo `CompletedProcess`. O `gh` roda por outra peça.
- `teste_bateria.py:15`, `teste_robustez.py:12`: `import ctypes` sobrando, que nem é usado. A docstring diz que trocou
  para o `psutil`.

### (c) Dúvida (1)

- `core/ocr_comum.py:209`: chama o Windows de verdade (`kernel32.SetDllDirectoryW`), mas só para o OCR que roda à
  parte não herdar a pasta de DLLs do programa. É Windows, então iria para `core/windows.py`. Mas faz parte de "abrir um
  processo nosso", então iria para a peça dos processos. Precisa de decisão de desenho.

**Conta, conferida com a saída do teste linha por linha:** 10 (a1) + 24 (a2: 2 + 1 + 3 + 17 + 1) + 27 (b: 10 + 5 + 8 +
4) + 1 (c) = 62. Nenhuma linha se repete. O `core/ocr_comum.py` tem duas linhas: a 39 está em (b) e a 209 em (c).

## A mesma lista separada pela sugestão do Fable (recado da gerente, 23/11; ainda não é decisão do Livro)

A sugestão:
- **Proibido fora de `core/windows.py`:** `ctypes.windll`, `ctypes.WinDLL`, `wintypes`, `winreg`, `os.startfile`.
- **Permitido em qualquer lugar:** `ctypes.CDLL` carregando as DLLs de `core/nativo/`.
- **`subprocess`:** só numa lista fixa de arquivos: `core/windows.py`, o servidor de páginas, o lançador do Kraken e
  `empacotar.py`.

Não mudei a trava: ela continua como o pedido manda. Abaixo está só a separação. Conferi os lugares de uso lendo a
árvore de cada arquivo, não só a linha do `import`.

### Proibido, fora do atualizador (grupo à parte: não muda nada nelas)

- `core/nucleos.py:78`: `ctypes.windll.kernel32.GlobalMemoryStatusEx`, que lê a memória livre para decidir quantas
  páginas trabalham ao mesmo tempo. O import está na linha 44.
- `core/ocr_comum.py:211`: `ctypes.WinDLL("kernel32")`, `GetDllDirectoryW`/`SetDllDirectoryW`. Por um instante, tira a
  pasta de DLLs do programa para o OCR que roda à parte não herdá-la. O import está na linha 209.
- `historico.py:199`: `os.startfile(pasta)`, que abre a pasta no Explorer.
- `historico.py:212`: `os.startfile(caminho, "print")`, que manda imprimir pelo Windows.
- `avaliar.py:1655` e `:1659`: `windll`/`wintypes` e `SHGetFolderPathW`, que pergunta onde fica a Área de Trabalho
  (régua dos filtros). O `import ctypes` está na linha 26.
- `ui/brasao_girando.py:225`: `ctypes.windll.kernel32` `OpenProcess`/`WaitForSingleObject`, que confere se o programa
  continua aberto enquanto o brasão gira.
- `teste_velocidade.py`, 17 lugares de import e o uso deles:
  - `winreg` nas linhas 362 e 432 (a placa de vídeo e o processador);
  - `windll` nas linhas 479, 1678 e 2233 (a memória, "não dormir" e a lista de processos do console);
  - `WinDLL`/`wintypes` nas linhas 642 a 664, 1737 a 1759, 1904 a 1922 e 2250 a 2254 (a memória do processo, a janela
    preta e a classe da janela).

### Proibido, no atualizador e nos testes à distância (a lista de trabalho do atualizador novo)

- `atualizacao.py`:
  - `wintypes` nas linhas 433, 438 e 441;
  - `windll` nas linhas 435, 752 e 761;
  - `winreg` nas linhas 1194 e 1279.
- `core/_testes_a_distancia_windows.py`: `wintypes` nas linhas 36 e 63 a 77; `windll` nas linhas 94 a 99.

### Permitido pela sugestão

- `ctypes.CDLL` das DLLs nossas: `core/gravura_scantailor.py:169` e `core/st_ferramentas.py:315`.
- `subprocess` nos arquivos da lista: `core/paginas_em_outro_processo.py:64`, `empacotar.py:115` e, se "o lançador do
  Kraken" for `core/ocr_kraken.py`, o `:89` (ver "o que cai fora" abaixo).

### `subprocess` fora da lista de arquivos: falharia pela sugestão (16)

- **Atualizador e testes à distância:** `atualizacao.py:114` e `core/_testes_a_distancia_windows.py:34`.
- **Outras partes do programa:**
  - `core/ocr_comum.py:39`: o `abrir_processo` dos OCRs, por onde o Kraken abre de verdade;
  - `core/ocr_tesseract.py:87`: o `tesseract.exe`;
  - `historico.py:7`: o `explorer /select`;
  - `ui/tela_de_carregamento.py:38`: o brasão;
  - `teste_velocidade.py:75`: o PowerShell.
- **Scripts de apoio:**
  - `avaliar.py:31`;
  - `compilar_detector_gravura.py:42` e `compilar_st_ferramentas.py:44`;
  - `empacotar_teste_velocidade.py:68`;
  - `montar_motor_kraken.py:98`;
  - `gerar_prints.py:15`;
  - `teste_completo.py:326`;
  - `conferencia.py:71`: só `list2cmdline`;
  - `publicar_versao_kaique.py:70`: só o tipo.

### O que cai fora da sugestão (ela não diz o que fazer)

1. **"O lançador do Kraken" não é um arquivo só.** O `Popen` de verdade está em `core/ocr_comum.py`
   (`abrir_processo`, L185-219), que também abre o `tesseract.exe`. O `core/ocr_kraken.py` usa o `subprocess` para
   `PIPE`, `TimeoutExpired` e o tipo. Pela sugestão ao pé da letra, um dos dois falha, ou os dois entram na lista.
2. **O `import ctypes` só para os tipos** (`c_double`, `c_void_p`, `create_string_buffer`) nos 8 arquivos
   `core/*_scantailor.py` que chamam a DLL nossa sem carregá-la: caixas, cores, desentortar, dividir, endireitar, luz,
   pontinhos e preto e branco. A sugestão não proíbe nem permite. Pela letra dela, passam, porque não usam `windll`,
   `WinDLL` nem `wintypes`.
3. **`import ctypes` sobrando**, sem uso nenhum: `teste_bateria.py:15` e `teste_robustez.py:12`. Pela letra, passam.
4. **"CDLL carregando as DLLs de `core/nativo/`" não se confere lendo o código.** O caminho vem de uma variável
   (`ctypes.CDLL(str(self.caminho))`). Uma trava que lê a estrutura não sabe se o caminho é de `core/nativo/`. Ou ela
   aceita todo `CDLL`, e aí `CDLL("kernel32")` passa, ou só aceita o `CDLL` nos dois arquivos, o que já é uma lista de
   arquivos.
5. **Jeitos de falar com o sistema que a sugestão não lista:** `ctypes.oledll`, `ctypes.cdll.kernel32` e
   `ctypes.CDLL("kernel32")` (a K01 pega por palavra), além de `os.system`, `os.popen` e `os.spawn*`.
6. **A lista fixa de arquivos para o `subprocess`** é uma lista de lugares permitidos. Isso não bate com o "binário,
   sem lista de exceções" da primeira mensagem do Fable. Ela pode ser lida como "as peças únicas de cada coisa", desde
   que cada arquivo da lista tenha um papel escrito. Isso é decisão, não minha.
7. **Os scripts de montar** (`compilar_*`, `montar_motor_kraken.py`, `empacotar_teste_velocidade.py`) rodam `cmake`,
   PyInstaller e `pip`. A sugestão só põe o `empacotar.py` na lista. Pela letra, os outros falham.

## Perguntas para o Samuel

(A gerente adapta para a Central. Não há print, porque nada na tela muda: é uma conferência do código.)

**1. Os pedaços do programa que conversam com outras coisas que não são o Windows (grupo b).**
- *Do que se trata:* a trava nova diz "só um arquivo do programa pode rodar outro programa ou carregar uma DLL". Ela
  acusa 27 lugares que não conversam com o Windows: as ferramentas do ScanTailor que viraram DLL nossa, o leitor de
  texto (OCR) e o servidor de páginas, que rodam à parte, e os scripts de montar o instalador.
- *O que acontece hoje:* cada um faz isso por conta própria. Isso não é defeito que o Kaique vê; é jeito de escrever o
  código.
- *O que você escolhe:*
  - (1) Tudo vai para o mesmo arquivo do Windows. É simples, mas mistura as ferramentas do ScanTailor com o Windows.
  - (2) **Sugestão do implementador:** um arquivo só para as DLLs nossas e um arquivo só para os programas nossos que
    rodam à parte. A trava diz qual dos três arquivos pode fazer cada coisa e continua sem lista de exceções. Os
    scripts de montar o instalador ficam de fora da trava, porque não vão para o Kaique.
  - (3) Só comentário.
- *O que muda no que já funciona:* nada agora. A mudança só aconteceria depois da entrega ao Kaique (D-765), e o
  programa faria o mesmo de antes.

## Ressalvas

- **A rodada do GitHub vai falhar por causa deste teste**, de propósito (D-830). Enquanto ele estiver no ramo, a
  rodada inteira sai vermelha, e uma falha nova de outro teste fica misturada com esta. Sugestão técnica para a
  gerente: na hora de juntar, decidir se ele entra como `xfail(strict=True)` até o atualizador novo ficar pronto ou se
  fica falhando. Não fiz isso por conta própria: o pedido diz "vai falhar hoje de propósito".
- **Não disparei a rodada do GitHub.** O pedido manda rodar só o arquivo novo e fazer commit com `[skip ci]`. Por
  isso não há número de rodada.
- **O que a trava não pega:** `os.system`, `os.popen`, `os.spawn*`, `os.exec*`, `multiprocessing`,
  `asyncio.create_subprocess_*`, `sys.modules["ctypes"]`, o nome montado em pedaços (`__import__("ct" + "ypes")`) e um
  módulo nosso que guarda o `subprocess` com outro nome e o devolve por uma função. Está escrito na docstring do teste.
  A K01 pega `os.system` e `os.popen` por palavra.
- **A sobreposição com a K01** continua até a gerente juntar e decidir. Ver "A escolha".
- Rodei o teste no PC. Ele só lê arquivos. Nenhuma janela abriu e nada do Windows foi mexido.

## Ideias para a Lista de espera

- Duas peças carregam a mesma DLL do ScanTailor (`core/st_ferramentas.py:315` e `core/gravura_scantailor.py:169`), cada
  uma com o seu `CDLL` e o seu `add_dll_directory`. É uma regra em dois lugares (§11.12).
- A trava poderia pegar também `os.system`, `os.popen` e `os.spawn*`, para a regra "rodar outro programa" ficar inteira.
  Não estava no pedido do Fable.

## Bugs para a Lista de bugs

- 23/11/2026, `teste_bateria.py:15` e `teste_robustez.py:12`: `import ctypes` que não é usado (sobrou da troca para o
  `psutil`). Não impede nada.

## Commits

- `cdbaec25`: `tests/test_trava_windows.py` e este ONDE-PAREI, com push no ramo `atualizador-novo-2026-11-23`.
