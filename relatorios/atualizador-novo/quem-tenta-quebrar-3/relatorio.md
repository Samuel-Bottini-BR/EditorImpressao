# Quem tenta quebrar, volta 3: o atualizador novo

24/11/2026. Terceiro agente que tenta quebrar (D-775, D-815): não escrevi este código e não o conserto. Ramo
`atualizador-novo-2026-11-23`, commit `847cf2aa` (o GitHub estava verde nele, rodada 45471388274). Nada do programa nem
dos testes do ramo foi mudado. Nenhuma janela na tela do Samuel, nenhuma pergunta do Windows, nada instalado, nada no
programa instalado do Samuel nem em `%LOCALAPPDATA%\EditorImpressao`. Tudo o que rodei está em `provas/` (os scripts e
a saída de cada um).

## Em uma frase

**NÃO ESTÁ PRONTO para a prova à vista.** A volta pelo pacote guardado funciona de verdade (sem internet, em segundos,
e o atualizador do Velopack de verdade aplica e reabre), e a guarda da última boa não deixa nada pela metade em oito dos
nove casos que rodei. Mas achei **1 grave e 7 médios**. O grave: se a versão nova falha no teste e o Windows não deixa
o programa voltar (um arquivo da pasta preso por outro programa), o programa entra num laço sozinho, testa, pede a
volta, o atualizador falha e reabre a versão estragada, e assim de novo; o Kaique fica sem o programa e nenhuma frase
aparece. Pela D-853 ("Se achar médio, para e me avisa — não há volta 4 sem o Fable"), **tudo para aqui** e o Samuel é
avisado.

## Como classifiquei (D-842)

- **grave**: o Kaique fica sem o programa, ou com o programa errado, e a tela não diz o que aconteceu.
- **médio**: o Kaique veria (frase errada ou que falta, clique sem resposta, segundos sem nada na tela, versão
  estragada sem aviso), ou uma decisão do Livro que o código não cumpre.
- **leve**: só aparece lendo o código; o Kaique nunca veria.

Cada achado diz **EXECUTADO** (rodei neste Windows) ou **LIDO** (só li o código), e o que é de mentira em cada prova.

## O que rodei de verdade neste Windows

| Prova (`provas/`) | De verdade | De mentira |
|---|---|---|
| `prova_volta_recusada.py` | o `vpk` 1.2.161 montando a 1.1.0 e a 1.2.0 de um programa de prova SEM JANELA (feito com o PyInstaller; só anota com que argumentos foi aberto); o `Update.exe` do Velopack aplicando a volta e a troca, com um arquivo de `current\` preso por outro processo e sem nada preso; a regra do ramo | o programa (é o de prova, não o nosso de 460 MB); `--silent` no lugar da janelinha |
| `prova_guarda_e_volta.py` | `guardar_ultima_boa`, `Atualizacao._guardar` e `Atualizacao._voltar` do ramo, no disco, com pacotes de 120 MB; a biblioteca do Velopack de verdade copiando e conferindo o pacote guardado; outro processo de verdade prendendo o arquivo; o processo que guarda morto à força no meio da cópia; "sem internet" de verdade para o processo (um proxy que não existe) | a chave do Samuel (a de prova dos testes); o disco cheio (simulado: sem licença de administrador não dá para criar um disco pequeno); o pedido final ao `Update.exe` (só anotado: a troca de verdade está na prova de cima); o motor (dado como no lugar) |
| `prova_guarda_dois_processos.py` | dois processos de verdade guardando o mesmo pacote de 200 MB ao mesmo tempo, 5 rodadas | a chave |
| `prova_volta_com_outro_processo.py` | a lista de processos do Windows pela peça do ramo, um processo de verdade aberto de dentro de `current\` (uma cópia do `ping.exe`, sem janela), a volta do executor e a biblioteca do Velopack copiando | o pedido final ao `Update.exe`, a chave |
| `prova_regra.py` | a regra do ramo (`proxima_fase`) nos caminhos que olhei | o resto (é só a lógica) |
| a biblioteca do Velopack sem o `Update.exe` | o `UpdateManager` de verdade numa instalação de prova sem o `Update.exe` | — |
| `mutacoes_qtq3.py` | 14 proteções desligadas uma a uma numa CÓPIA do ramo (`git archive`), com 12 arquivos de teste do atualizador, um por vez | — |
| os testes do ramo | 78 arquivos, um por vez | — |

---

## Achado grave

### G1. A volta recusada pelo Windows vira um laço: o programa não abre e nenhuma frase aparece

- **O que o Kaique veria.** A versão nova entra, não passa no teste rápido e o programa pede a volta para a anterior.
  Se nesse instante um arquivo da pasta do programa está preso por outro programa (o caso da D-839, agora na volta), o
  atualizador do Velopack não consegue trocar e reabre a versão que falhou. Ela testa de novo, falha de novo, pede a
  volta de novo, e assim sem parar. A janela do programa nunca abre; o que aparece é a janelinha do atualizador
  ("Atualizando...") de novo e de novo. A frase (3) da D-778 ("não conseguiu voltar sozinho") nunca aparece.
- **EXECUTADO (`prova_volta_recusada.py`):**
  - Parte A, a volta (o pedido sem argumento nenhum, como `_voltar` faz): com `current\versao.txt` preso por outro
    processo, o `Update.exe` tentou 10 vezes ("Acesso negado"), desistiu em 10,9 s e **reabriu a versão 1.2.0 (a que
    falhou) com os argumentos vazios** (`args []`, `VELOPACK_RESTART=true`).
  - Parte D, a regra do ramo com o disco que fica (rodando 1.2.0, última boa 1.1.0 lida da pasta de verdade, 1.2.0
    reprovada no bilhete, linha de comando vazia): três aberturas seguidas, as três dão `RodarTesteRapido(antes da
    janela)` → `Reprovar` → `Voltar` → `Sair`, **nenhuma frase**.
  - Parte C, a mesma volta sem nada preso: deu certo em 1,5 s e reabriu a 1.1.0.
- **A causa.** Na troca normal, o pedido leva `--conferir-a-versao-nova <de> <para>`, e é assim que a versão reaberta
  sabe que a troca não aconteceu (D-839; a parte B provou de verdade que funciona). Na volta, o pedido vai **sem
  argumento nenhum** (`trocar_para(..., volta=True)`: `argumentos = []`). A versão estragada reaberta não tem como saber
  que acabou de tentar voltar, e o disco diz o mesmo de antes ("rodando a nova, última boa a anterior"): testa e volta
  de novo. A lista das falhas do ONDE-PAREI (§11.12 ponto 3) não tem o caso "a volta foi pedida e o Windows não deixou
  trocar"; só "o Velopack recusa a cópia".
- **Quanto dura.** Enquanto o arquivo estiver preso. Uma trava de segundos (um antivírus lendo) custa uma volta a mais
  e depois dá certo. Uma trava que fica (outra conta do Windows com o programa aberto, que o atualizador não consegue
  fechar) deixa o laço até reiniciar o computador. A cada volta do laço o atualizador abre o pacote inteiro (460 MB)
  numa pasta provisória antes de desistir (lido: `apply_windows_impl.rs` 138-163).
- **Se o atualizador ainda estiver saindo quando a versão estragada reabre**, a abertura vê "o atualizador está
  rodando" e sai sem janela (lido: `atualizacao.py` 1292-1296): o programa também não abre, só que sem laço.
- **Fere:** D-778 ("a volta forçada a falhar mostra a (3)"), D-718 ("volta sozinho para a versão anterior e avisa"),
  CLAUDE.md §11.12 pontos 2 e 3.
- **Por que grave e não médio:** o Kaique fica sem o programa e a tela não diz nada. Raro: precisa de uma versão que
  falhe no teste e de um arquivo preso no instante da volta.

---

## Achados médios

### M1. Dois cliques no atalho nos segundos sem nada na tela: nenhuma das duas aberturas volta, e as duas abrem a versão estragada dizendo "não conseguiu voltar sozinho"

- **O que o Kaique veria.** Depois de uma troca, a versão nova faz o teste rápido antes da janela, com nada na tela
  (nem o brasão: a atualização roda antes dele). Se ele clica no atalho de novo nesses segundos, há duas aberturas
  testando. Se a versão falhou, as duas pedem a volta, cada uma vê a outra aberta e desiste: as duas abrem na versão
  estragada com "A atualização não deu certo e o programa não conseguiu voltar sozinho. Não desinstale nada. Avise o
  Samuel." Na próxima abertura (um clique só), a volta acontece e aparece a frase (1), "voltou para a versão anterior",
  o contrário do que ele leu antes.
- **EXECUTADO (`prova_volta_com_outro_processo.py`):** com um processo de verdade aberto de dentro de `current\`, a
  peça do Windows o viu, a volta deu `VoltaPedida(False, "há outra janela do programa aberta")`, a regra mandou a frase
  (3) e **não mandou sair** (a janela abre na versão estragada). Que as duas aberturas se veem é leitura (cada uma é
  "outra janela" para a outra).
- **A causa.** A volta usa a conferência da troca, e "outra janela aberta" é motivo para não trocar; os dois testes
  rodam ao mesmo tempo. É o leve 12 da volta 1 ("um segundo clique abre outra abertura que também roda o teste") e a
  ressalva 10 do implementador ("um deles pode não conseguir"), nenhum dos dois com decisão do Samuel; o efeito de
  verdade é pior do que a ressalva diz (nenhuma das duas volta). Não é a D-850 (aquela é o bilhete anotado por duas
  janelas).
- **Fere:** D-718, D-842 (frase que não corresponde ao que acontece em seguida).

### M2. Sem última boa guardada, a versão nova entra mesmo assim; se ela falhar no teste, nada aparece e ela não é reprovada

- **O que o Kaique veria.** Nada: o programa abre na versão estragada (o teste rápido falhou, isto é, falta alguma peça
  que o programa precisa), sem frase nenhuma, e ela continua sendo a versão dele.
- **Quando acontece.** A primeira versão depois do `.msi` não tem o pacote em `packages\` (D-851, conferido pelo
  implementador); a guarda dela precisa baixar 460 MB. Se essa descida falha (internet que cai, a versão retirada do
  GitHub) e na mesma abertura a procura acha a versão nova e a baixa (ela vem depois da guarda), a troca acontece sem
  nada guardado. Também se a pasta `ultima-boa` for apagada (um programa de limpeza, outra conta: a pasta é de
  Usuários: Modificar), ou se a assinatura guardada sumir.
- **EXECUTADO:** `prova_regra.py` R2: rodando a 1.2.0 sem última boa, reaberta pelo "Reiniciar agora", reaberta pelo
  "Sim" ao fechar, e aberta pelo atalho: o teste roda por trás (ou nem roda, na reabertura sem janela), falha, e a regra
  só registra "não há versão guardada para voltar"; nenhuma frase, nenhuma reprovação. `prova_guarda_e_volta.py` V3: com
  a assinatura guardada apagada, `ler_ultima_boa` dá "" e a abertura segue o mesmo caminho, sem frase.
- **A causa.** A regra trata "não há última boa" como "não há o que fazer", e a troca não confere se há para onde
  voltar antes de trocar.
- **Fere:** D-779 ("antes de trocar, o programa guarda a versão que funciona fora da pasta que é trocada e volta
  sozinho se a troca estragar"), D-718, D-778 (3).

### M3. "Sim" ao fechar que não pode trocar: o programa fecha sem atualizar e nada diz por quê, nem depois

- **O que o Kaique veria.** Responde "Sim" ao "Atualizar agora?", o programa fecha, e a versão não muda. Nenhuma frase
  agora nem na próxima abertura. O caso comum: ele tem duas janelas do programa abertas e fecha uma.
- **EXECUTADO (`prova_regra.py` R1):** nos seis "não pode" (outra janela, o pacote sumiu, o motor, a lista do Windows, o
  pacote trocado, o atualizador que não começou), depois do "Sim" só vem uma linha no registro; nada na tela nem guardado
  para a próxima abertura.
- **A causa.** A D-845 ("nenhum clique fica sem resposta") foi feita só para o "Reiniciar agora". O primeiro "quem
  tenta quebrar" viu ("No 'Sim' ao fechar [...] só a troca não acontece, calada") e chamou de efeito menor; ninguém
  levou ao Samuel.
- **Fere:** D-842 ("um clique sem resposta" nunca é pequeno). Precisa de decisão (consertar ou deixar para depois).

### M4. Se a guarda falha depois de uma troca, toda abertura tem segundos sem nada na tela, e sem espaço no disco a cópia enche o disco até o fim a cada abertura

- **O que o Kaique veria.** A versão nova passou no teste, mas não deu para guardar o pacote dela (o disco sem 460 MB
  livres, por exemplo). Daí em diante, **toda** abertura roda o teste rápido antes da janela (nada na tela, nem o
  brasão) e tenta copiar os 460 MB de novo por trás, enquanto ele trabalha. Sem espaço, a cópia escreve até o disco
  acabar, falha e apaga, em toda abertura: nesse instante, qualquer gravação do programa (o projeto dele) encontra o
  disco cheio.
- **EXECUTADO:** `prova_regra.py` R3 (três aberturas: `RodarTesteRapido(antes_da_janela=True)` em todas);
  `prova_guarda_e_volta.py` G6 (o disco cheio simulado: a guarda devolve o motivo, apaga a cópia e deixa a última boa
  de antes, certo). **LIDO:** `guardar_ultima_boa` não confere o espaço livre antes de copiar; o motor confere
  (`garantir_o_motor`, `FOLGA_DO_MOTOR_BYTES`): a mesma pergunta resolvida de dois jeitos.
- **Medido:** o teste rápido (os imports dele) leva 3,6 s com o disco frio e 0,6 s quente neste PC, sem contar abrir o
  programa empacotado duas vezes; no notebook só a prova à vista mede.
- **O ONDE-PAREI diz outra coisa:** a ressalva 3 ("o teste rápido roda por trás a cada abertura até dar") só vale sem
  última boa nenhuma; com uma última boa de antes, o teste é antes da janela.
- **Fere:** CLAUDE.md §11.12 ponto 3 (a falha "disco cheio" pensada pela metade), D-842 (segundos sem nada na tela).

### M5. A D-851 parte de uma premissa que não vale para o nosso instalador, e o "tentar de novo a cada abertura" que ela substituiu continua

- **O que é.** O Samuel decidiu: "a última versão boa deve ser guardada copiando o pacote que já está na pasta
  `packages\` do programa (o instalador e cada troca deixam ele lá), sem internet [...] O agente confere isso, não
  supõe." O implementador conferiu, de verdade, que **o nosso `.msi` não deixa o pacote lá** (só a troca deixa). O Livro
  diz que a D-851 "substitui a sugestão do agente de tentar de novo, por trás, a cada abertura até ter internet", e a
  prova dela é "Primeira abertura sem internet → a última boa fica guardada mesmo assim". O código continua tentando de
  novo a cada abertura (precisa baixar), e a prova da D-851 não passa. O ONDE-PAREI pôs isso como ressalva 1, não como
  pergunta.
- **EXECUTADO (`prova_guarda_e_volta.py` G2):** sem o pacote em `packages\` e sem internet, `_guardar` devolve "o
  pacote da 1.2.0 não está em packages e o índice publicado não deu para ler" e nada é guardado.
- **O efeito para o Kaique:** até a primeira guarda dar certo, não há volta possível (é o M2).
- **Fere:** D-851 (a prova dela), CLAUDE.md §11.6 ("na dúvida, parar e perguntar — nunca fazer diferente em
  silêncio"). Precisa da palavra dele.

### M6. O pacote baixado esperando não é oferecido de novo sem internet, e a frase "Tente ao fechar o programa" pode não levar a nada

- **O que o Kaique veria.** Depois de um "Não" ao fechar, de um desligar no meio da troca, ou da reabertura que mostra
  "Não deu para atualizar agora: [motivo]. Tente ao fechar o programa.", se a abertura seguinte está sem internet o
  aviso não volta e, ao fechar, a pergunta não vem, mesmo com a versão nova inteira em `packages\`. A frase disse
  "Tente ao fechar o programa" e fechar não pergunta nada.
- **EXECUTADO (`prova_regra.py` R5 e R6):** com a frase guardada e a procura sem internet, o fechar não pergunta; com
  `pendente="1.2.0"` e sem internet, nem o aviso nem a pergunta. A regra recebe o `pendente` e não o usa em lugar
  nenhum (só a abertura o usa para decidir se pergunta se o atualizador roda).
- **A causa.** A emenda do Fable manda derivar o estado de três coisas, uma delas "se há pacote baixado esperando
  (`get_update_pending_restart`)"; a regra só usa duas. A D-769 diz "a troca tenta de novo depois": sem internet, não.
- **Raro** (precisa de estar sem internet na abertura seguinte).

### M7. Quatro proteções novas sem teste (D-827)

A guarda que preserva a assinatura da versão que chega, a escolha da última boa MAIS NOVA, a hora no nome da frase
guardada e o apagar do `.chegando` na soma errada: desligadas, nenhum teste reclama. Detalhe no item 7 abaixo.
EXECUTADO. A D-827 diz que proteção sem teste nunca é pequena.

---

## Achados leves (só aparecem no código)

1. **Uma guarda que falha pode deixar a pasta dizendo "última boa = a nova".** A guarda grava a assinatura da versão
   ANTES de o pacote ficar conferido, e `ler_ultima_boa` só olha se os dois arquivos existem. EXECUTADO (G8): com um
   arquivo velho no nome final, preso por outro processo, a guarda devolveu "não consegui guardar" e `ler_ultima_boa`
   passou a dizer 1.2.0 (com um pacote de 5 bytes). Não achei como esse arquivo velho nasce no uso normal; uma volta
   para ele seria recusada pelo Velopack (a soma) e mostraria a frase (3). §11.12 ponto 2.
2. **A guarda confere a soma do que leu de `packages\`, não do que ficou escrito.** EXECUTADO com dois processos
   guardando ao mesmo tempo, 5 rodadas: o pacote final ficou certo nas 5 (o Windows não deixa renomear um arquivo
   aberto, e o último a fechar dá o nome); em 4 das 5 um dos dois registrou "não consegui guardar" e o outro "guardado".
   Nenhum defeito para o Kaique; o registro que a gerente lê fica confuso.
3. **A volta com o pacote guardado estragado deixa um `.partial` em `packages\`** (EXECUTADO, V2: 40 MB no teste, até
   460 MB de verdade), até o próximo download.
4. **Sobras pequenas:** o campo `Abriu.pendente` que a regra não usa (M6); o texto `MOTIVOS_DA_TELA[outra_janela]`
   que nunca aparece (a outra janela tem a frase da D-840); `tests/test_velopack_de_verdade.py::test_a_volta_baixa_a_
   anterior_e_o_velopack_confere_a_soma` e o topo do arquivo ainda falam da volta antiga ("o pedido da anterior (a
   volta) é montado pela peça"), mas o que o teste prova (a peça monta o pedido e a biblioteca confere) é usado pela
   guarda de hoje. Pela D-853 não é caminho morto (nenhuma função nem ramo), é texto velho.
5. **A soma SHA256 do pacote é calculada em dois lugares** (`assinatura.soma_sha256` na conferência da troca e
   `_copiar_somando` na guarda). Cada um tem o porquê (a guarda soma e copia numa leitura só), mas é a mesma conta
   escrita duas vezes (§11.12).
6. **A licença `/T` da pasta do registro** confere antes que não há arquivo ligado a outro lugar dentro, e então roda o
   `icacls`; entre as duas coisas outra conta poderia criar um (LIDO; risco não provado, milissegundos). É a mesma
   conferência da raiz, que já existia.
7. **Dois testes de fora do atualizador falharam uma vez com o PC ocupado pelas minhas provas** e passaram sozinhos:
   `test_windows_peca.py::test_o_programa_nasce_parado_e_so_roda_dentro_do_grupo` (é um teste de tempo, com 3 s de
   espera de propósito) e `test_decisoes_desfazer_pagina.py::test_d621_botao_direito_na_pagina_abre_a_lista_e_o_desfazer_funciona`.

---

## As perguntas do Fable

### 1. O `estado.json` decide alguma coisa além de "versões reprovadas" e "frase uma vez"?

**Não.** EXECUTADO por leitura do código inteiro: o bilhete é lido num lugar só (`Atualizacao.abrir`, `ler_estado`) e
só saem dele as reprovadas (`reprovadas_do_bilhete`) e a frase (`frase_do_bilhete`); é escrito num lugar só
(`mudar_o_bilhete`), que joga fora qualquer outra chave. As reprovadas decidem duas coisas, as duas na regra que o Fable
escreveu: a versão reprovada não é baixada de novo, e a frase (1) é derivada ("rodando a última boa e há reprovação de
uma mais nova"). Nenhum outro arquivo de controle novo decide sozinho: a assinatura guardada da versão que chega só
vale junto com o pacote (D-852). O bilhete não voltou a ser juiz.

**Sobrou caminho morto da volta por download?** **Não sobrou função, fase, ramo de `if` nem teste da volta antiga.**
Procurei todo nome de função de `atualizacao.py`, `core/fases_da_atualizacao.py` e `core/conversa_com_o_velopack.py`
que o programa não chama: nenhum. A leitura do índice publicado e o download moram só em `_baixar_a_que_roda`, que é o
caso 2 da D-851 (vivo). Sobrou só texto velho num teste (leve 4).

**O que cresceu é necessário?** Quase tudo vem de uma decisão: a pasta da última boa e a guarda (D-844/D-851), a fase
GUARDANDO (a guarda tem resultado conferido), a conferência por trás (M2), as frases e os motivos (D-845 a D-848), a
leitura byte a byte da assinatura (o defeito que a N27 achou). O que não é necessário: o campo `pendente` da regra
(entra e não é usado) e o texto do motivo da outra janela (nunca aparece). E falta uma coisa que deveria ter crescido: a
marca da volta no pedido ao Velopack (G1).

### 2. O ReabrirOPrograma: em quantos caminhos?

**Um lugar só na regra**: a troca do "Reiniciar agora" que não pôde ser pedida **depois** de a janela fechar
(`TrocaPedida(certa=False)` com a janela fechada e sem outra janela aberta). EXECUTADO (`prova_regra.py` R4): dos oito
"não deu" possíveis nesse instante, sete reabrem (o pacote trocado, o pacote sumiu, o motor, sem a lista do Windows,
sem conferir, o atualizador que não começou, erro inesperado) e um não (outra janela, M5 da volta 2). **Não é usado com
frequência:** a mesma conferência roda segundos antes, com a janela aberta; seis desses sete só acontecem se algo
mudar nesses segundos.

**O caso que escapa da conferência antes de fechar:** o atualizador do Velopack (`Update.exe`) que sumiu ou não abre.
A conferência não olha o `Update.exe`; a biblioteca recusa sem ele. EXECUTADO: o `UpdateManager` de verdade numa
instalação sem o `Update.exe` levanta "This application is not properly installed: Update.exe does not exist". Quando
acontece: o download da versão nova regrava o `Update.exe` da raiz (lido: `manager.rs` 463-471); um antivírus que o
ponha de lado entre o download e o clique faz a janela fechar e reabrir com "Não deu para atualizar agora: o
atualizador do programa não começou." Raro.

---

## Os itens do pedido, um por um

### 3. A guarda da última boa (D-851), no disco de verdade

| Caso | O que deu | Certo? |
|---|---|---|
| G1 o pacote em `packages\` (toda troca), sem internet | guardado e conferido em 2,4 s (120 MB); a última boa de antes saiu | sim |
| G2 o pacote não está em `packages\` (o `.msi`), sem internet | "não está em packages e o índice publicado não deu para ler"; nada guardado; a última boa de antes fica | sim (mas ver M5) |
| G3 o pacote de `packages\` cortado no meio | "a cópia do pacote não tem a soma assinada pelo Samuel"; o `.chegando` apagado; a de antes fica | sim |
| G4 a assinatura de outra chave | "a assinatura não confere com a chave do Samuel"; nada copiado | sim |
| G5 a assinatura certa, mas de outro conteúdo | "a cópia do pacote não tem a soma assinada"; nada fica | sim |
| G6 o disco cheio (simulado) | "não consegui guardar o pacote ([Errno 28] ...)"; o `.chegando` apagado; a de antes fica | sim (mas ver M4) |
| G7 o pacote de `packages\` preso por outro processo | "não consegui guardar o pacote (Permission denied)"; nada fica | sim |
| G8 o nome final preso por outro processo, com um arquivo velho | "não consegui guardar", mas `ler_ultima_boa` passou a dizer a nova | **não** (leve 1) |
| G9 o processo morto à força no meio da cópia | sobra o `.chegando` (32 MB) e a última boa continua a de antes; a guarda seguinte dá certo e o apaga | sim |

A sobra que fica depois de G3 a G7: a assinatura da versão nova em `ultima-boa\` (sem o pacote não decide nada).

### 4. A volta com o pacote guardado

| Caso | O que deu | Certo? |
|---|---|---|
| V1 sem internet (o processo sem rede), pela biblioteca de verdade | o Velopack copiou e conferiu o pacote guardado em 2,4 s (120 MB) e a troca foi pedida, sem argumento | sim |
| V2 o pacote guardado estragado (cortado) | o Velopack recusou ("Checksum did not match"); a frase (3) | sim (sobra o `.partial`, leve 3) |
| V3 a assinatura guardada faltando | a volta recusa; e a abertura passa a achar que não há última boa (M2) | pela metade |
| a troca da volta de verdade pelo `Update.exe` | sem nada preso: 1,5 s, reabre a anterior; com um arquivo preso: o laço do G1 | **não** (G1) |

### 5. Cada falha do ONDE-PAREI, e as frases

- As falhas listadas que rodei (desligar no meio da guarda, sem o pacote, a assinatura que não confere, o disco cheio, a
  cópia recusada pelo Velopack, sem internet na volta) fazem o que está escrito. **Faltam na lista:** a volta pedida que
  o Windows não deixa trocar (G1); outra abertura testando junto na volta (M1); a troca sem última boa (M2); o "Sim" ao
  fechar que não pode (M3). **Está escrito diferente do que o código faz:** a ressalva 3 (M4).
- As frases conferidas palavra por palavra com o Livro (LIDO, e as que a regra manda nas provas): a (1), a (2) e a (3)
  da D-778; a da D-839; a da D-840; a da D-843; a da D-845 com os nove motivos da D-847, letra por letra; o título
  "Atualização" da D-846; a pergunta ao fechar da D-835. **Todas batem.** O aviso da versão nova: a última frase é a da
  D-835; o título "Versão nova do programa" e as duas primeiras frases vêm de 16/11 e não estão escritas no Livro (para
  a gerente confirmar se o Samuel já as viu).

### 6. Uma peça só

- `core/conversa_com_o_velopack.py` é o **único arquivo do programa que importa `velopack`** (EXECUTADO: busca no
  código; fora dele só testes); a trava dos donos passa (42 casos).
- A K03 continua a aprovada da D-837: a mesma função, a mesma linha do `icacls ... /grant "*S-1-5-32-545:(OI)(CI)M" /T`;
  só mudou o nome da variável (`raiz` → `pasta`) porque a mesma função agora serve também à pasta do registro, no mesmo
  passo (a "uma linha a mais" da emenda). Só `_fazer_passo` a chama; o porteiro passa (14 casos).
- Peça duplicada: nenhuma conversa com o Windows ou com o Velopack escrita duas vezes. Só a soma do pacote em dois
  lugares (leve 5).

### 7. Mutações (proteções desligadas numa cópia)

EXECUTADO (`provas/mutacoes_qtq3.py`, saída em `mutacoes_qtq3-resultado.txt`): numa cópia do ramo feita com
`git archive` (o ramo nunca foi mexido), 14 proteções que eu escolhi, uma de cada vez, com 12 arquivos de teste do
atualizador rodados um por vez. Sem mutação, os 12 passam na cópia.

- **Acusadas (8):** Q3 a volta sem conferir a assinatura guardada; Q4 a frase da D-839 na troca que deu certo; Q6 a
  reabertura que pergunta se o atualizador roda; Q7 a frase 2 da D-848 só uma vez; Q10 a frase de abertura em toda
  abertura; Q11 a frase da D-845 no lugar da D-840; Q12 a janela que não fechou sem frase; Q14 a volta com os argumentos
  da troca normal.
- **Sobreviveram (6), e o que cada uma quer dizer:**
  - **Q1** a guarda apaga também a assinatura da versão mais nova que está chegando: **proteção de verdade sem teste.**
    Sem ela, a versão nova, depois do teste, precisaria de internet para virar a última boa (e cai no M4).
  - **Q2** `ler_ultima_boa` escolhe a MAIS VELHA quando há duas: **proteção de verdade sem teste.** Duas versões na
    pasta acontecem quando a limpeza da guarda não consegue apagar a velha (arquivo preso); com a mais velha, a volta
    iria para a versão errada e o teste rodaria em toda abertura.
  - **Q9** a frase guardada sem a hora no nome: **proteção de verdade sem teste.** Sem ela, a mesma frase noutro dia
    não aparece (o próprio comentário do código diz que a hora existe para isso).
  - **Q13** a cópia com a soma errada não apaga o `.chegando`: **proteção de verdade sem teste** (460 MB que ficam no
    disco até a próxima guarda dar certo).
  - Q5 a frase guardada "mostrada" na reabertura sem janela: **não é sobrevivente de verdade** (mutação equivalente: sem
    janela, a frase só entra na fila da tela e nunca é marcada vista; ela continua no bilhete e aparece na próxima
    abertura com janela).
  - Q8 trocar sem a assinatura conferida nesta abertura: proteção que o caminho de hoje nunca alcança (o aviso só vem
    depois da assinatura certa); sem ela o código quebra por dentro em vez de recusar.

Estas quatro (Q1, Q2, Q9, Q13) são o **M7**. A D-827: "proteção sem teste [...] nunca é 'baixo': volta para conserto na hora". As quatro são
desta volta (a guarda da última boa e a frase guardada) e ficaram fora das 100 mutações do implementador. Fere D-811,
D-827.

### 8. O que já funcionava ao redor

EXECUTADO, um arquivo por vez, no ramo, com a pasta temporária no D:: os 14 arquivos do atualizador e da peça do Windows
e **todos os 64 `tests/test_decisoes*.py`**. **78 arquivos: 3519 casos passam, 13 pulados, 2 falharam uma vez** e
passaram rodados sozinhos logo depois (os dois de fora do atualizador; leve 7). Do atualizador:
`test_fases_da_atualizacao` 2171, `test_atualizador_volta3` 36, `test_atualizador_d851` 6, `test_atualizador_novo` 35,
`test_atualizador_volta2` 32, `test_atualizador_volta3_de_verdade` 4 (+1 pulado), `test_decisoes_atualizacao` 42,
`test_decisoes_ajudante_da_atualizacao` 22, `test_decisoes_preparo_d749`, `test_velopack_de_verdade` 3,
`test_windows_preparo_do_computador` 19 (+1), `test_porteiro_licenca_que_acrescenta` 14, `test_trava_windows` 42 (+3),
`test_conferencias_pacote` 26, `test_conferencias_codigo` 122, `test_conferencias_excecoes` 14: todos passam. O
conjunto inteiro fica com a rodada do GitHub (verde em `847cf2aa`, 45471388274). Não abri o programa na tela (pedido da
gerente: nada na tela do Samuel); a tela do atualizador só aparece no programa instalado, que é a prova à vista.

---

## O que eu fiz fora das minhas pastas (para a gerente saber)

- **Um erro meu: 7 linhas no registro de verdade `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log`**, às
  16:38:33 a 16:38:49 ("teste rápido da versão instalada: falta ...\modelos\..."), quando medi o tempo do teste rápido.
  Eu tinha mudado o `PROGRAMDATA` pelo Git Bash, e o Windows não deixou (a variável dele se escreve `ProgramData`; a do
  Git Bash ficou outra). Não apaguei (fora do projeto). Depois disso, toda prova minha muda a variável dentro do Python,
  que funciona (conferido).
- O `vpk` e o PyInstaller podem ter deixado arquivos na pasta temporária da conta (`%TEMP%`, o WiX não: não montei
  `.msi`). Não apaguei nada fora do projeto.
- O clone do Velopack (só lido) é o da pasta de rascunho desta sessão, o mesmo dos agentes anteriores.
- Dentro do projeto, só criei `saida_teste\qtq3\` (apaguei o que as provas criaram nela) e esta pasta do relatório.

## O que só a prova à vista pode mostrar

- O laço do G1 com o programa de verdade (a janelinha do atualizador de novo e de novo; quanto tempo cada volta leva com
  460 MB).
- Quantos segundos ficam sem nada na tela no teste antes da janela, no notebook (M1, M4).
- A guarda de 460 MB por trás enquanto o Kaique trabalha (tempo e disco).

## A minha opinião, com as ressalvas

Este relatório está **PRONTO PARA CONFERIR**. Não é aprovação: só o Samuel marca.

A minha opinião: **o atualizador NÃO ESTÁ PRONTO para a prova à vista.** A emenda do Fable funcionou no que ela mirava:
o bilhete deixou de ser juiz, a volta pelo pacote guardado é local e rápida (rodei com o Velopack de verdade, sem
internet), a troca recusada da D-839 funciona de verdade (o atualizador reabre a versão de antes com o pedido), e a
guarda da última boa é cuidadosa (nada pela metade em oito de nove casos de disco). Os achados de agora não são remendos
nem peça duplicada; são casos que o desenho não pensou, quase todos em volta da volta e da última boa:

- o G1 é o mesmo mecanismo da D-839 que faltou na volta (o pedido sem marca);
- o M1 e o M2 são a volta que não acontece (outra abertura testando junto; nenhuma última boa guardada), e nos dois a
  tela diz pouco ou nada;
- o M3 é o "nenhum clique sem resposta" feito só no "Reiniciar agora";
- o M4 e o M5 são a guarda: o que acontece quando ela falha depois de uma troca, e a premissa da D-851 que não vale
  para o `.msi`;
- o M6 é a terceira coisa do disco (o pacote esperando) que a regra recebe e não usa;
- o M7 são quatro proteções novas da guarda e da frase guardada que nenhum teste acusa.

Pela D-853, com médios achados, isto para e vai ao Samuel e ao Fable antes de qualquer volta 4.

**Ressalvas minhas:**

1. O G1 não rodou com o programa de verdade (460 MB): rodou com o atualizador do Velopack de verdade e um programa de
   prova, e com a regra de verdade. Quanto tempo cada volta do laço leva no notebook, só a prova à vista mede.
2. O "disco cheio" foi simulado (sem licença de administrador não dá para criar um disco pequeno); o "não confere o
   espaço antes" é leitura do código.
3. As provas da volta usaram `--silent` (sem a janelinha do atualizador); o programa pede com a janelinha. A diferença é
   só a janela.
4. Que as duas aberturas do M1 se veem uma à outra é leitura (rodei com uma).
5. A cópia das mutações não tem o git do ramo; por isso o `test_trava_windows.py` ficou fora delas (nenhuma mutação
   minha é da trava; ele passa no ramo, um por vez).
6. Pus 7 linhas no registro de verdade do `C:\ProgramData` por engano (seção acima).
