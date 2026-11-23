# Partes 2 e 3: o atualizador e os testes à distância

Pesquisador, 23/11/2026. Só leitura: nenhum código, teste ou documento existente mudou, nada rodou no Windows.
Código lido: ramo `atualizador-4-consertos-2026-11-21`, ponta de código `aa1963b7` (relatórios em `046c0271`; os dois
estão no GitHub, conferido com `git branch -r --contains`). Livro de decisões: ramo `obra-2026-10-26`, `0f58346a`.
Histórico e CLAUDE.md: `fase-1`, `47394b4a`. Todos os links abaixo são fixos nesses commits.

Abreviações dos links: **A** = `atualizacao.py`, **W** = `core/windows.py`, **T** = `core/testes_a_distancia.py`,
**TW** = `core/_testes_a_distancia_windows.py`. "Fato" = lido no código, no documento ou na fonte de fora citada.
"Dedução" = minha leitura, marcada. A opinião fica só na última seção.

**Tamanho, para dar a escala (fato, `git show <commit>:<arquivo> | wc -l`):** `atualizacao.py` tinha 935 linhas na
etapa 3 (`16c838a7`, 16/11), 1.681 no começo deste ramo (`4a775ba8`, 21/11), 1.892 depois da volta 2, 1.942 depois da
volta 3 e **2.314** na volta 4 (`aa1963b7`). `core/windows.py` (a "peça única", nascida em 19/11) tem 2.813.
`core/testes_a_distancia.py` tem 877. Os dois arquivos de teste deste ramo somam 1.855 linhas.

---

# Parte 2. O atualizador

## 2.1 O que o Samuel pediu

- **D-706** (16/11): "vamos adicionar uma forma de atualizar o aplicativo via internet quando ele achar algum problema e
  precisarmos arrumar, as atualizaçõpes não podem estar ligadas via api". [Livro L996](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L996)
- **D-723**: "velopack" (contra o tufup). [L1013](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1013)
- **D-718/D-719**: se falhar, volta para a anterior e avisa: "Sim, e tem que avisar a gente de alguma maneira" · "1".
  [L1008](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1008)
- **D-715/D-720**: com o programa aberto, aviso "Reiniciar agora" / "Depois". **D-734**: com "Depois", "quando ele abrir
  o programa de novo". D-715 em L1005, D-720 em L1010, D-734 em [L1024](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1024)
- **D-732**: procurar "quando ele abre o programa né? assim como todo aplicativo faz". [L1022](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1022)
- **D-733** (a escolha que gera o ajudante): entre (1) uma pergunta do Windows só na primeira abertura, (2) uma pergunta
  a cada versão, (3) instalar só na conta do Kaique, "os testes de longe deixam de funcionar": **"1- sim / VAI CONSEGUIR
  FAZER OS TESTS A DISTANCIA NÉ?"**. [L1023](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1023)
- **D-735/D-741/D-749**: a pergunta aparece sempre; depois do "Não" volta a cada abertura; preparação pela metade conta
  como não feita. D-735 em L1025, D-749 em L1039, D-741 em [L1031](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1031)
- **D-736**: "Se tiver nova versão eu quero poder mandar atualizar aqui pelo meu pc". [L1026](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1026)
- **D-742/D-748**: a janelinha "Atualizando o programa, espere um pouco..." no "Depois", que some quando o brasão aparece.
- **D-767** (18/11): "não faça mais nada escodindo ou de mentira" · "não quero fazer consertos quero que funcione".
  [L1057](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1057)
- **D-779**: "ta vamos continuar com ele, mas o que fazemos para ele não dar defeito e porque nossa peças em voltadele
  deram defeito?" (Velopack 1.2.161 com "a nossa proteção"; situação no Livro: "decidida, não construída").
  [L1069](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1069)
- **D-806**: a licença pedida "no mesmo instante do clique do Kaique [...] enquanto a janela do programa ainda está na
  frente" ("então pode ser opção A"). [L1096](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1096)
- **D-824** (21/11): entrega em duas vezes, primeiro só "os 4 consertos"; "vamos fazer com um só, uma coisa de cade vez.".
  Ficam para depois: "Atualizar agora?" ao fechar (D-769/D-794), a janelinha em toda troca (D-770), os testes à distância.
  [L1114](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1114)
- **D-828** (22/11): "foi eu, pode consertar essas coisas": o "Reiniciar agora" troca de verdade, "o nosso programa
  garante que o programa terminou de fechar", abrir pelo atalho no meio não estraga; a pergunta no meio da tela; refazer a
  preparação dá certo. [L1118](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1118)

## 2.2 Como funciona hoje, passo a passo (fato, do código e do cabeçalho de `atualizacao.py`)

Instalação: `.msi` do Velopack, por máquina, em `C:\Program Files\EditorImpressaoPrograma\current`. O gancho de instalar
só anota, porque o `.msi` roda os ganchos **sem** licença de administrador (achado B1, [A:20-23](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L20)).

1. **Primeira abertura (conta do Kaique).** A janela da senha → "Agora não" → um fio solto (daemon) chama
   `preparar_ao_abrir` → `preparar_na_primeira_abertura` ([A:2088](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2088)).
   Espera a janela estar na frente (`esperar_a_janela_na_frente`, [A:2042](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2042)),
   depois `core.windows.pedir_licenca` ([W:2760](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2760)):
   grava `trabalho.json` numa pasta de troca e abre **o próprio `EditorImpressao.exe`** com `ShellExecuteExW` "runas"
   (o UAC; `hwnd` = a janela dona, [W:2724](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2724)).
   Esse processo elevado (administrador, sessão do Kaique) roda um passo de PowerShell que abre **de novo** o `.exe` com
   `--preparar-o-computador` e espera ([A:1906](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1906)).
   Esse terceiro processo cria o **ajudante** (`schtasks /Create` com XML: roda como SYSTEM, `--procurar-atualizacao`,
   contas autenticadas podem mandar rodar, [A:1457](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1457), `QUEM_PODE_MANDAR_RODAR` [A:164](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L164)),
   a tarefa "desfazer" (pelo caminho dos testes à distância, Parte 3), o Visual C++ e tira o Inno antigo. Depois, na conta
   do Kaique, `ler_o_computador` lê as duas tarefas no Agendador e decide se a pergunta volta ([A:1953](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1953)).
2. **Toda abertura comum (conta do Kaique).** `main.py` → `atender_linha_de_comando` ([A:2260](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2260)):
   se há troca acontecendo (`troca_em_andamento`, [A:2286](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2286)), sai em silêncio;
   se há versão esperando do "Depois", troca antes da janela (`trocar_antes_de_abrir`, [A:1267](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1267)).
   Senão a janela abre, segura o mutex `Global\EditorImpressao-programa-aberto` e manda o ajudante rodar com
   `schtasks /Run` (`procurar_ao_abrir`, [A:1409](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1409)).
3. **O ajudante (SYSTEM, sessão 0, é o próprio `EditorImpressao.exe` de `current`).** `rodar_ao_ligar` ([A:813](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L813)):
   Visual C++/Inno, motor do Kraken, resultado da última troca, e `procurar_e_preparar` ([A:617](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L617)):
   `check_for_updates` → assinatura Ed25519 antes de baixar → motor no lugar → `download_updates` → "programa aberto?"
   (mutex **e** lista de processos de `current`, até 30 s, [A:907](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L907)).
   Aberto: grava `"pendente"` em `C:\ProgramData\EditorImpressao\atualizacao\estado.json`; a tela, que lê esse arquivo
   4 s depois de abrir e de 5 em 5 min, mostra o aviso. Fechado: grava `"aplicando"` e pede a troca.
4. **O pedido de troca** passa sempre por `GerenteComAMarcaDaTroca.wait_exit_then_apply_updates` ([A:552](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L552)):
   só chama o Velopack se o mutex `Global\EditorImpressao-trocando` estiver seguro (`segurar_a_marca_da_troca`,
   [A:1307](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1307)).
   O Velopack lança o `Update.exe` (SYSTEM), que espera o ajudante sair, extrai, fecha à força o que roda da pasta,
   renomeia `current` e reabre `EditorImpressao.exe --conferir-a-versao-nova` (SYSTEM, escondido): teste rápido num
   subprocesso; passou → `"ok"` e refaz o ajudante ([A:2226](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2226)); falhou → baixa o pacote inteiro da anterior, confere a assinatura e chama `Update.exe apply --package` direto ([A:750](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L750), [A:779](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L779)).
5. **Caminho COM o script** ("Reiniciar agora", ou "Depois" + nova abertura). A janela fecha gravando; `trocar_e_reabrir`
   ([A:1232](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1232))
   lança pela peça um PowerShell solto **na conta do Kaique** ([A:1120](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1120)),
   com pasta de trabalho System32 e sinal de vida. Linha 1: pega as marcas da troca e de reabrir. Depois: `Wait-Process`
   do programa (120 s), `schtasks /Run` do ajudante (passo 3, agora com o programa fechado), laço lendo `estado.json` e o
   estado da tarefa a cada 2 s até 900 s, mais 60 s se a nova falhou no teste, e `Start-Process` do programa com
   `--depois-da-troca`. No "Depois", o mesmo script abre ainda a janelinha (Windows Forms num runspace STA, [A:968](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L968)).
6. **Caminho SEM o script** (o Kaique fechou o programa durante o download; ou o Samuel mandou de longe pela conta de
   testes, `ssh ... schtasks /Run`, [A:1430](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1430)).
   O ajudante vê "fechado" e, antes de pedir a troca, lança o **vigia** (PowerShell, SYSTEM, [A:1091](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1091)),
   que segura a marca da troca enquanto a fase for "aplicando". Ninguém reabre o programa (SYSTEM não abre janela na tela
   do Kaique), salvo se ele clicar no atalho no meio: aí `abrir_quando_a_troca_acabar` ([A:1362](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1362))
   lança o script "só de reabrir" (conta do Kaique), que espera a marca sumir e abre.

Num "Reiniciar agora" que dá certo, contei (dedução, seguindo o código) **sete processos em duas contas**: o PowerShell
do script (Kaique), `schtasks`, o ajudante (SYSTEM), o `Update.exe` (SYSTEM), o `--conferir-a-versao-nova` (SYSTEM), o
teste rápido (SYSTEM) e o programa reaberto (Kaique). O único canal entre as duas contas é `estado.json` e três mutexes.

## 2.3 As peças, uma ficha cada

"Por causa de outra peça nossa?": **fato** quando o próprio comentário do código diz; **dedução** quando é minha.

| Peça | Onde | O que faz | Problema que tentou resolver | Origem | Se sair | Por causa de outra peça nossa? |
|---|---|---|---|---|---|---|
| Ajudante (tarefa SYSTEM) | [A:1457](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1457) | troca em Arquivos de Programas sem UAC | trocar sem pergunta a cada versão; trocar de longe | **D-733** (Samuel, 17/11), commit `73dc4122` | um UAC por versão (o jeito 2 que ele recusou) e sem "mandar atualizar de longe" (D-736) | não: vem de o programa morar em Arquivos de Programas |
| Pergunta da primeira abertura (exe elevado → PowerShell → exe de novo) | [A:1906](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1906), [W:2760](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2760) | um UAC cria as tarefas, VC++, tira Inno | o "Não" lido como "Sim" (defeito 2 da etapa 5) | D-733/D-735/D-805; peça de `9e2268cc` (19/11), usada desde o conserto 1 `85590fe4` | sem ajudante não há o que criar | **sim (fato)**: só existe para criar o ajudante; o salto duplo vem de a peça só aceitar passos de uma lista fechada ([W:54-70](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L54)) |
| "Preparado?" lido no Windows | [A:1953](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1953) | lê as 2 tarefas; vazio = não pergunta | a marca nas Configurações dizia "preparado" sem estar | conserto 1 `85590fe4`; ajustes `9979419d` (volta 2), `ce728693`/`ebd4197e`/`f15863b8` (volta 3, D-826) | volta a anotação que mente (§11.12 ponto 2) | **sim (dedução)**: só existe porque o ajudante existe |
| Esperar a janela na frente | [A:2042](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2042), [W:1942](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L1942) | sem limite, lê a cada 0,3 s quem está na frente | a pergunta piscando na barra (prova nº 1) | volta 4 `1e5ea67d`; **leitura da gerente** da D-806 (o relatório 3 e a PARTE -44 dizem isso) | volta a piscar | **sim (fato, [A:2052-2054](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2052))**: o pedido sai 17-20 s depois do clique porque o programa primeiro carrega e monta a janela |
| Script da troca (PowerShell, conta do Kaique) | [A:1120](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1120) | espera fechar, chama o ajudante, espera, reabre | o .exe tem de sair; SYSTEM não abre janela | D-720/D-734, `73dc4122` (17/11) | "Reiniciar agora" não reabre | **sim (fato, docstring [A:1123-1127](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1123))**: "Por que nao o ajudante: ele roda como SYSTEM" |
| Lançar solto com sinal de vida e pasta System32 | [W:1662](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L1662), `cwd` [W:1689](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L1689) | lança o script e confere que começou | `DETACHED_PROCESS` (o PowerShell saía sem rodar); a pasta de trabalho prendia `current` | peça `9e2268cc`; usada no conserto 3 `77a05d2e`; `cwd` na volta 4 `b756ddc2` | o script não roda ou prende a pasta | **sim (dedução)**: existe para o script da troca |
| Mutex "programa aberto" | [A:864](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L864) | a janela segura; o ajudante lê | o ajudante (outra sessão) saber se o programa está aberto | etapa 3 `16c838a7` | o ajudante trocaria com o programa aberto | **sim (dedução)**: só porque quem troca é outro processo |
| Lista de processos de `current`, até 30 s | [A:907](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L907), [W:1855](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L1855) | confere que nada roda de `current` | o mutex some antes de o processo terminar de gravar | volta 4 `3adea01f`; D-828 "garante que o programa terminou de fechar" | o Velopack fecha à força o que ainda grava | **sim (dedução)**: o `--waitPid` do Velopack espera o **ajudante**, não a janela |
| Marca da troca + `troca_em_andamento` | [A:196](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L196), [A:1344](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1344) | clique no atalho durante a troca sai em silêncio | o clique às 14h34min58 da prova nº 1 | volta 4 `586b483f`; D-828 | o clique estraga a troca | não conferi se o atalho do Velopack (`stub.rs`) já faz algo parecido |
| `FASES_EM_QUE_HA_TROCA` | [A:206](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L206) | só lê o mutex nessas fases | não carregar a peça (~30 ms) em toda abertura | volta 4 `586b483f`, escolha do escritor | 30 ms por abertura | **sim (fato, comentário)**: atalho de velocidade da marca da troca |
| Vigia da troca (PowerShell, SYSTEM) | [A:1091](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1091) | segura a marca na troca sem script | o clique no meio da troca sem script | volta 4 `586b483f`; **resposta 4 da gerente**, não do Samuel ([ONDE-PAREI L1428](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/ONDE-PAREI.md#L1428)) | volta a ressalva que o escritor propunha deixar | **sim (fato)**: existe só para a marca da troca no caminho sem script; e porque o ajudante (que é o `.exe` de `current`) tem de sair antes da troca |
| `GerenteComAMarcaDaTroca` + `segurar_a_marca` + `TrocaSemAMarca` | [A:552](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L552), [A:1307](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1307) | embrulha o `UpdateManager`; sem marca, não troca; lança o vigia e espera 10 s o mutex | "toda troca com a marca" | volta 4 `586b483f` | uma troca sem marca | **sim (fato)**: força a marca da troca e lança o vigia |
| Marca de reabrir + script "só de reabrir" | [A:200](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L200), [A:1167](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1167) | depois do clique engolido, alguém reabre, uma vez só | o clique engolido não abria nada | volta 4 `586b483f` | o Kaique clica e nada abre | **sim (fato)**: existe porque a marca da troca engole o clique e o vigia não reabre |
| Janelinha + mutex da janelinha | [A:968](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L968), [A:187](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L187) | avisa durante a espera do "Depois" | o Kaique achar que não abriu | **D-742, D-748** (Samuel, 17/11), `1a42dfb0`, `5a407a6f` | contra a decisão dele | sim (dedução): existe porque a troca do "Depois" é fora do programa |
| Voltar para a anterior | [A:750](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L750), [A:779](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L779) | teste rápido; falhou → baixa a anterior e `Update.exe apply --package` | versão nova estragada | **D-718** (Samuel), etapa 3 `16c838a7` | contra a decisão dele | não; mas fica **fora** da peça e do pedido único de troca (baixo 1 do relatório 3) |
| Refazer o ajudante depois da troca | [A:2226](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2226) | recria a tarefa como SYSTEM | o gancho de atualizar não tem licença (B1) | `73dc4122` | XML de versão velha | sim (dedução): por causa do ajudante |
| Motor do Kraken à parte | [A:1766](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1766) | põe o motor em `<raiz>\motor-kraken\1`; sem ele, não anuncia versão | não baixar 370 MB a cada versão | **D-768/D-788/D-790** (Samuel), conserto 4 `75cfa928`, volta 2 | o motor some na troca | não |
| `estado.json` + gravar com 30 tentativas | [A:285](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L285), leitura [A:1059](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1059) | o canal entre SYSTEM e Kaique | duas contas precisam combinar a fase | etapa 3; o "tenta de novo" e o `-ErrorAction Stop` na volta 4 (`5a1aa6b2`) | sem canal | **sim (dedução)**: por causa do ajudante e dos scripts |
| Pasta segura | [W:2287-2385](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2287) | pasta em Arquivos de Programas com as licenças de fábrica | a tranca à mão (`icacls /T`) deixava arquivos sem licença | peça `9e2268cc` (plano-v3); usada nos testes à distância na volta 4 `929195b4` | volta a tranca à mão | sim (fato): substitui a nossa tranca de 18/11 |

## 2.4 O que o Windows e o Velopack fazem de difícil

| Comportamento | Fonte | Lido por mim? |
|---|---|---|
| O `Update.exe` fecha à força todo processo cujo `.exe` está dentro da raiz (`PROCESS_TERMINATE`), menos ele mesmo | Velopack 1.2.161, [`util_windows.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/shared/util_windows.rs) (`get_processes_running_in_directory`, `_force_stop_package`) | sim, hoje |
| Renomeia `current` com 10 tentativas, 1 s cada; se não der: "Unable to start the update, because one or more running processes prevented it"; se falhar a **segunda** troca de nome, "the app was left in a broken state" (a volta está comentada no código) | [`apply_windows_impl.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/commands/apply_windows_impl.rs) | sim, hoje |
| `WaitExitThenApplyUpdates` "wait for 60 seconds before proceeding. If your app has not exited within 60 seconds it will be killed" | [docs.velopack.io/integrating/overview](https://docs.velopack.io/integrating/overview) | sim, hoje |
| A tranca do Velopack (`packages\.velopack_lock`) é segurada também durante o download; o atalho passa `AllowSetForegroundWindow` e abre com `current` como pasta de trabalho | `manager.rs:406`, `stub.rs:39-41`, segundo o escritor ([ONDE-PAREI L1376](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/ONDE-PAREI.md#L1376)) | **não conferi** |
| O processo filho herda a pasta de trabalho do pai, e uma pasta que é pasta de trabalho não se renomeia (erro 32) | `CreateProcessW`, `lpCurrentDirectory` (citado pelo escritor) e experimento no PC (`anexos/volta4-experimentos.txt`) | a documentação não reabri; o experimento não refiz |
| O Windows tira de um programa o direito de vir para a frente "the next time the user generates input"; o UAC usa a janela dona | `AllowSetForegroundWindow`, `SetForegroundWindow` (citados pelo escritor) | não reabri |
| O `.msi` "PerMachine" roda os ganchos sem administrador (`Impersonate="yes"`) | achado B1, [A:20-23](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L20) | não reabri o WiX |
| PowerShell 5.1 lê `.ps1` sem BOM como ANSI: "Without the BOM, Windows PowerShell misinterprets your script as being encoded in the legacy "ANSI" codepage" | [about_Character_Encoding (5.1)](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1) | sim, hoje |
| PowerShell 5.1 com `DETACHED_PROCESS` sai sem rodar | provado na etapa 5 ([revisão 18/11 §1.1](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/8cf8358aaf310a726c4833cbd951f1c133e8f086/relatorios/revisao-atualizador-2026-11-18/relatorio.md#L50)) | não refiz |
| `ctypes.get_last_error()` sem `use_last_error=True` devolve sempre 0: o "Não" do UAC (1223) virava sucesso | [W:45](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L45) e o conserto 1 | doc do Python não reabri |
| `icacls /inheritance:r /grant:r ... /T` deixa os arquivos já existentes com a lista de licenças vazia, e devolve 0 | provado em 18/11 ([revisão distância](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/77848768818c294f9b0e95029b2827dd78ac4600/relatorios/revisao-distancia-2026-11-18/relatorio.md#L21)) | não refiz |
| `Start-Process` 5.1: o documento diz que a pasta padrão é a do executável; o experimento mediu a do PowerShell | baixo 2 do [relatório 3](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L106) | não |

## 2.5 A história das voltas

- **16 a 18/11.** Etapa 3 escrita com o Velopack. Na etapa 5 (18/11, PC do Samuel), 7 defeitos no Windows de verdade; as
  revisões só lendo acharam mais 13 no atualizador e 4 causas de estrutura nos testes à distância. Frase central da
  revisão: "o que o programa lembra não é prova; prova é o que o Windows responde" ([revisão atualizador](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/8cf8358aaf310a726c4833cbd951f1c133e8f086/relatorios/revisao-atualizador-2026-11-18/relatorio.md#L29)).
  Nasce a regra §11.12 ampliada ([CLAUDE.md L712](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/47394b4a5d7d4f9d461d6987676d235254910d9f/CLAUDE.md#L712)) e a peça única (19/11).
- **Volta 1 (21/11, escritor A).** Os 4 consertos: o "Não" pela peça; a janela como dona; "Reiniciar agora" sem
  `DETACHED_PROCESS`; o motor à parte. **Relatório 1:** NÃO ESTÁ PRONTO, 3 médios (motor estragado engolido, "versão
  nova" sem fim sem o motor, a pergunta voltando depois do "Sim") e 10 baixos ([R1 L8](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-1.md#L8)).
- **Volta 2 (escritor A).** Os 3 médios consertados. **Relatório 2:** PRONTO PARA CONFERIR, 6 baixos e uma pergunta
  ([R2 L8](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-2.md#L8)).
  Samuel: "então o agente fez um codigo novo para arrumar outro e criou 6 problemas novos?" → D-826, D-827.
- **Volta 3 (escritor B).** Os 2 baixos de código e os testes das proteções. Não achei relatório de "quem quebrou" desta
  volta na pasta.
- **Prova à vista nº 1 (22/11, 13h52-14h39).** Funcionou: o "Não", o "Sim" lido do Windows, a conta comum lê as tarefas,
  o motor, o aviso, a volta com a frase da falha. Falhou: o "Reiniciar agora" não troca (erro 32 em 10 tentativas), a
  pergunta pisca na barra, a segunda preparação dá "acesso negado" ([PARTE -44 §3](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/47394b4a5d7d4f9d461d6987676d235254910d9f/historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md#L70)).
- **Volta 4 (escritor C).** A causa do erro 32 (a pasta de trabalho), a lista de processos, a marca da troca, o vigia,
  o só de reabrir, a espera pela janela na frente, a pasta segura. D-829 autoriza 3 testes. **Relatório 3:** NÃO ESTÁ
  PRONTO, 5 médios ([R3 L12](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L12)).
  Ele diz que "a causa principal saiu" e que "nenhum pede para refazer a volta".

## 2.6 Os 5 médios do relatório 3, com o código

**Médio 1. Sem o script, "está aberto?" vem antes da marca** ([R3 L31](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L31)).
[A:676-685](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L676):
```python
    if programa_aberto():                      # 676: pergunta primeiro
        ...
    gravar_estado({"fase": "aplicando", **base})
    try:
        gerente.wait_exit_then_apply_updates(...)   # 684: só aqui o vigia nasce e a marca aparece (até 10 s)
```
Um clique no atalho entre a pergunta e a marca abre o programa; o Velopack o fecha à força e ninguém reabre.

**Médio 2. O script da troca zera a fase antes de ler** ([R3 L48](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L48)).
[A:1189-1196](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1189):
```python
        "    $fase = ''; $tipo = ''",
        "    " + _linha_de_ler_a_fase(estado),       # uma leitura que falha deixa $fase vazia
        ...
        "    if ($fase -ne 'pendente' -and $fase -ne 'aplicando') { break }",
```
O vigia não zera (a regra "só muda a fase se leu", [A:1059](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1059)). O verificador provou no Windows: com o arquivo
travado, o laço saiu em 1 s. O script então reabre o programa no meio da troca.

**Médio 3. "Sem licença para abrir a marca" = "existe", sem teste** ([R3 L65](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L65)).
[A:1085-1086](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1085):
```python
        "  try { if ([System.Threading.Mutex]::TryOpenExisting($nome, [ref]$m)) { $m.Dispose(); return $true }"
        " ; return $false } catch { return $true }",
```
Trocando o `catch` por `return $false`, os 55 testes passam.

**Médio 4. A janela da frente vira a dona, sem teste** ([R3 L76](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L76)).
[A:2106-2111](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L2106):
```python
        dona = esperar_a_janela_na_frente(janela)
        if dona is None:
            ...
        janela = dona                                # trocar por `pass`: os 55 testes passam
```

**Médio 5. A pasta segura criada e gravada por fora da peça, e conferida depois** ([R3 L84](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/046c0271a4227848809eb2ed38d7541d5cdf7859/relatorios/atualizador-4/quem-quebrou/relatorio-3.md#L84)).
[T:378-379](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L378) (repetido em [T:290](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L290)) e [T:869-872](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L869):
```python
    return (f"$pasta = '{pasta_dos_testes()}';"
            f" if (-not (Test-Path -LiteralPath $pasta)) {{ New-Item -ItemType Directory -Path $pasta -Force | Out-Null }}")
    ...
        resultado = executor.aplicar_ja_como_administrador(plano_de_preparar_o_desfazer())  # já gravou desfazer.ps1 e a tarefa
        ...
        conferida = executor.conferir_a_pasta_dos_testes()                                  # só agora confere
```
A peça já tem `criar_pasta_segura` (cria, confere, apaga se não confere) e `gravar_na_pasta_segura` (confere antes,
lê de volta), [W:2320](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2320) e [W:2361](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2361), e os passos `passo_criar_pasta_segura`, `passo_gravar_na_pasta_segura`, `passo_criar_tarefa` ([W:2394-2414](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/windows.py#L2394)).

---

# Parte 3. Os testes à distância

## 3.1 O que é e o que ele pediu

O Samuel entra de longe no notebook do Kaique para rodar testes (velocidade e outros) e mandar atualizar.
- **D-705**: "vamos colocar uma api no programa para que eu possa fazer chamadas dentro do proprio pc do kaique para
  fazer testes de velocidade e outras coisas" → escolhido o Servidor OpenSSH do Windows, só pela rede do Tailscale, sem
  porta dentro do programa. [L995](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L995)
- **D-711** "liga sozinho com o windows, eu vou fazer uma senha, e não vai sr chave"; **D-712** ligado de fábrica, botão
  nas Configurações; **D-717** conta separada, sem administrador, escondida ("sim"); **D-721** janela da senha na primeira
  abertura; **D-731** desinstalar desfaz tudo ("ok"); **D-736** mandar atualizar de longe.
- Decididas e **não construídas**: **D-771** ligar é "tudo ou nada" ("A"); **D-780** duas trancas, firewall e dentro do
  próprio OpenSSH; **D-781** dois campos de senha. [L1061](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1061), [L1070](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1070)
- **D-824/D-825**: ficam para uma entrega depois; nesta, a senha digitada não liga nada ("opção B").
  [L1115](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/0f58346ae3c49f10a07ec5abc8411d9f441da946/docs/plano/DECISOES.md#L1115)

## 3.2 Como funciona hoje, e as peças

- **Ligar** (botão das Configurações, [ui/tela_configuracoes.py:389](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/ui/tela_configuracoes.py#L389)) → `ligar(senha)` ([T:802](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L802)) →
  `plano_de_ligar` (9 passos, [T:408](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L408)) →
  `ExecutorWindows.aplicar` → `TW.aplicar_no_windows` ([TW:103](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/_testes_a_distancia_windows.py#L103)):
  script em `tempfile.mkdtemp`, senha cifrada por DPAPI, e `_rodar_elevado`, um `runas` **próprio**, fora da peça única.
- **Desligar**: o mesmo caminho, com outro UAC. **Desfazer**: a tarefa SYSTEM "Desfazer testes a distancia" roda
  `desfazer.ps1` da pasta segura; o gancho de desinstalar só manda rodar (`schtasks /Run`, [T:840](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L840)).
  A primeira abertura cria essa tarefa pelo `aplicar_ja_como_administrador_no_windows`, que abre o `powershell.exe` direto
  e grava o script em UTF-8 **sem BOM** ([TW:148-152](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/_testes_a_distancia_windows.py#L148)).
- **`core/_testes_a_distancia_windows.py` não mudou desde `b74a94e2`** (a base das revisões de 18/11): `git diff
  b74a94e2 aa1963b7` vazio. A linha que lia o "Não" como "Sim" continua no caminho do ligar:
  `return ctypes.get_last_error()` com `ctypes.windll` ([TW:94-95](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/_testes_a_distancia_windows.py#L94)). Isso já está anotado como lembrete no relatório 1 (L119-L121).

| Peça | Onde | O que faz | Origem | Se sair | Por causa de outra peça nossa? |
|---|---|---|---|---|---|
| Conta `EditorTestes` (Usuários, escondida) | [T:408](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L408) | quem entra de longe | D-717 (Samuel) | entra com a conta do Kaique | não |
| OpenSSH + bloco no `sshd_config` (`AllowUsers`, `PasswordAuthentication yes`, `MaxAuthTries 3`) | [T:120](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L120) | a porta de entrar | D-705, D-711 | não há teste à distância | não |
| Regra do firewall só para 100.64.0.0/10 e a placa Tailscale | [T:88](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L88) | tranca de rede | D-705 | porta aberta à rede da casa | não |
| Caderninho `antes.json` | [T:268](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L268) | o que o PC já tinha, para desfazer só o nosso | D-731, `65303058` | o desfazer tiraria o OpenSSH do dono | não |
| Tarefa "desfazer" (SYSTEM; nega a conta de testes; AU pode mandar rodar) | [T:306](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L306), [T:334](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L334) | desfaz ao desinstalar, apaga também o ajudante | D-731/D-733, `77be80ff` | desinstalar deixa tudo (o gancho não tem licença) | **sim (fato)**: o gancho do `.msi` roda sem administrador (B1) |
| `Executor` / `ExecutorWindows` | [T:669-760](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L669) | os testes trocam por um de mentira | etapa 4 `59aa8049` | nada | não; mas é a segunda "peça do Windows" do programa (dedução) |
| `CHAVE_PRONTO` nas Configurações | [T:158](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L158) | anota "ligado" | etapa 4 | — | é a anotação que a §11.12 (ponto 2) proíbe como prova (dedução) |

## 3.3 O que dá para fazer no PC do Kaique, e os riscos

Fato do código: pelo `ssh EditorTestes@<endereço>` o Samuel roda comandos como uma conta comum; pode mandar o ajudante
rodar (`comando_de_longe_para_atualizar`, [A:1430](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1430)) e ler `atualizacao.log` no ProgramData ([A:1445](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/atualizacao.py#L1445)).
O ajudante só roda o `.exe` fixo com o argumento fixo; mudar a tarefa pede administrador (`GRGX` só lê e executa).

Riscos (fato, salvo onde marcado):
- **Senha por senha**, com 3 tentativas por conexão; a única tranca de rede é o firewall (a segunda, D-780, não existe):
  o bloco do `sshd_config` não tem `Match Address`. Desligado o firewall, a porta 22 aceita qualquer rede (dedução).
- **Ligar pela metade:** o script do ligar para no primeiro erro e não desfaz ([T:619-660](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L619)):
  pode ficar o OpenSSH, a regra, a conta. D-771 ("tudo ou nada") não está construída.
- **O "Não" do UAC pode virar "ligado"** no caminho das Configurações (TW:95, acima): `CHAVE_PRONTO = True` sem nada feito.
- **Senha com acento** trocada no caminho (provado na [revisão de 18/11](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/77848768818c294f9b0e95029b2827dd78ac4600/relatorios/revisao-distancia-2026-11-18/relatorio.md#L25)); o arquivo não mudou depois, então continua (dedução).
- **Desfazer:** roda como SYSTEM o `desfazer.ps1` da pasta segura (contas comuns só leem). Com o médio 5, numa pasta que
  já existia com outras licenças, o script é gravado e a tarefa aponta para ele mesmo assim.
- O que fica se falhar no meio do desfazer: os passos seguem depois de erro e a tarefa só se apaga se tudo deu certo
  ([T:524](https://github.com/Samuel-Bottini-BR/EditorImpressao/blob/aa1963b76ca2dc343bcd06b6e33166cb712f6fa8/core/testes_a_distancia.py#L524)): dá para rodar de novo.

## 3.4 A situação de agora

Não entra na primeira entrega ao Kaique (D-824, D-825). O que existe no código é o de 16 a 17/11, mais a pasta segura
da volta 4. O ligar e o desligar nunca passaram pela peça única. As decisões de 18/11 (D-771, D-780, D-781) estão só no
Livro. Na prova de 18/11 (etapa 5), os testes à distância deram os defeitos que a revisão daquele dia descreve.

---

# Opinião do agente

Tudo aqui é opinião. Marco **certeza** quando decorre direto do código lido, e **palpite** quando não.

**1. As peças que parecem existir só para proteger outra.** Certeza, pelo próprio comentário do código: o vigia existe
para a marca da troca no caminho sem script; a marca de reabrir e o script "só de reabrir" existem porque a marca da
troca engole o clique e o vigia não reabre; o `GerenteComAMarcaDaTroca` existe para obrigar a marca; `FASES_EM_QUE_HA_TROCA`
existe para a marca não custar 30 ms. As quatro nasceram juntas na volta 4 (`586b483f`), e três dos cinco médios moram
nelas (1, 3 e, em parte, 2). Num nível abaixo, quase todo o resto é consequência de uma escolha só: **quem troca é um
processo SYSTEM que é o próprio `.exe` de `current`**. Por isso ele tem de sair antes da troca; por isso alguém de fora
precisa segurar o estado (script, vigia, `estado.json`, mutexes); por isso o `--waitPid` do Velopack espera o processo
errado e foi preciso a lista de processos.

**2. O desenho mais simples do atualizador (palpite).**
- *Só o Velopack:* instalar por usuário (`%LOCALAPPDATA%`), procurar e baixar no próprio programa, `apply_updates_and_restart`
  no "Reiniciar agora" e `wait_exit_then_apply_updates` (ou a troca do próprio Velopack ao abrir) no "Depois". O Velopack
  espera o programa sair, fecha o que sobrou, troca e reabre na conta certa. Somem o ajudante, a pergunta da primeira
  abertura, os dois scripts, o vigia, as três marcas, a lista de processos e o `estado.json`. **Perde-se:** o jeito 1 da
  D-733 (era o jeito 3 que ele não quis, "os testes de longe deixam de funcionar") e o "mandar atualizar de longe" da
  D-736; o Visual C++ e tirar o Inno ainda pediriam uma licença. Em Arquivos de Programas sem ajudante, seria um UAC por
  versão (o jeito 2, também recusado).
- *Mantendo a D-733:* um ajudante que **não mora em `current`** (um `.exe` pequeno na pasta segura, ou a tarefa chamando o
  `Update.exe` direto), que segura ele mesmo a marca do começo ao fim, espera o programa do Kaique pelo número do
  processo e faz o teste rápido e a volta. Sumiriam o vigia, o `GerenteComAMarcaDaTroca`, a espera de 10 s pela marca e a
  duplicação "script lê o estado / vigia lê o estado". Ficaria um script do lado do Kaique só para reabrir (SYSTEM não
  abre janela na sessão dele sem um caminho mais complicado). Não conferi no Velopack 1.2.161 se a tarefa pode chamar o
  `Update.exe` assim.

**3. O desenho mais simples dos testes à distância (palpite).** Ligar e desligar pela peça única, com os passos que ela
já tem (`passo_criar_pasta_segura`, `passo_gravar_na_pasta_segura`, `passo_criar_tarefa`, `passo_script`), e apagar o
`runas` próprio de `_testes_a_distancia_windows.py`. Isso cumpre o ponto 1 da §11.12 e leva junto o "Não" lido como "Sim"
e o médio 5. A tela mostraria o que o Windows tem (o serviço, a conta, a regra), não `CHAVE_PRONTO`.

**4. Quais dos 5 médios somem se a peça sair.**
- Médio 1: some se o ajudante nunca trocar sem o script (certeza: o defeito só existe nesse caminho). O preço: a troca
  de longe e a do "fechou durante o download" esperariam a próxima abertura (mexe na D-736).
- Médio 2: não depende de peça a mais. É a mesma leitura escrita duas vezes, uma certa e uma errada (certeza). Some
  apagando a linha `$fase = ''`, ou se o script esperasse a marca em vez de ler o JSON (palpite).
- Médio 3: some se o vigia e o "só de reabrir" saírem (certeza), porque a marca SYSTEM lida da conta comum só acontece
  entre os dois.
- Médio 4: some se a espera pela janela sair (certeza). A pergunta volta a piscar, a não ser que ela seja feita antes de
  o programa carregar, o jeito que a D-806 descreve ("no mesmo instante do clique") e que o escritor recusou (palpite meu
  de que é o mais simples; ele argumentou que o brasão não toma a frente).
- Médio 5: some se o desfazer for preparado pela peça (certeza: a peça já cria, confere e grava).

**5. Resposta curta à pergunta do Samuel (palpite com base nos fatos acima).** Sim, em parte. As voltas 1 a 3 consertaram
causas de verdade e não empilharam proteção. A volta 4 consertou a causa principal com um conserto pequeno (`b756ddc2`: 19 linhas de código, o `cwd` do lançado solto) e depois
acrescentou de uma vez quatro peças que só protegem outra, e foi ali que o relatório 3 achou três dos cinco médios. O que
não é "proteção da proteção" é o custo da escolha do ajudante SYSTEM (D-733), que foi do Samuel e tem motivo.

---

## Fontes consultadas (23/11/2026)

- Código e relatórios do repositório, nos commits dos links.
- Velopack 1.2.161: [apply_windows_impl.rs](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/commands/apply_windows_impl.rs),
  [util_windows.rs](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/shared/util_windows.rs) (licença MIT,
  D-723); [docs.velopack.io/integrating/overview](https://docs.velopack.io/integrating/overview).
- Microsoft: [about_Character_Encoding, PowerShell 5.1](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1).
- O resto das fontes de fora (CreateProcessW, AllowSetForegroundWindow, CreateMutexW, `manager.rs`, `stub.rs`) é citado
  pelo escritor da volta 4 e **não foi reaberto por mim**.
