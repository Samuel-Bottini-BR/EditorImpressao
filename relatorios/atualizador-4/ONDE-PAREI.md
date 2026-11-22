# Os 4 consertos do atualizador para a primeira entrega ao Kaique (D-824, 21/11/2026)

Implementador. Ramo `atualizador-4-consertos-2026-11-21`, cópia `.claude/worktrees/atualizador-4`, saiu de `4a775ba8`
(a versão de teste `obra-2026-10-26`). Este ONDE-PAREI é também o formulário da entrega (D-792). Pacote de regras:
`anexos/pacote.md` (montado com `python -m regras_dos_agentes pacote`, como o passo 2).

## Pedido

- Papel: implementador
- Commit de partida: 4a775ba8
- Ramo: atualizador-4-consertos-2026-11-21

## Arquivos que vou mexer

- `atualizacao.py`
- `core/ocr_kraken.py`
- `ui/testes_a_distancia_ui.py`
- `configuracoes.py`
- `tests/test_decisoes_ajudante_da_atualizacao.py`
- `tests/conferencias_excecoes.json`
- `tests/test_atualizador_4.py` (novo)
- `relatorios/atualizador-4/`

(Arquivos de `core/` e `ui/` que o plano nomeia, D-796: `core/ocr_kraken.py` e `ui/testes_a_distancia_ui.py`. Fora:
`core/windows.py` (uso só o que já existe: `pedir_licenca`, `passo_script`, `ler_tarefa`, `lancar_powershell_solto`),
`core/_testes_a_distancia_windows.py` (fica para os testes à distância, passo 4), `main.py`, `ui/aviso_de_atualizacao.py`,
`empacotar.py`. `tests/test_decisoes_ajudante_da_atualizacao.py` só no teste que a D-774 autoriza; os outros testes
antigos estão listados abaixo e esperam o "sim" do Samuel, um por um. `configuracoes.py`: só tirar a marca que deixa de
ser usada, e só se o teste antigo dela for autorizado.)

## Onde parei

- 21/11, noite: leitura feita (o meu arquivo de agente, CLAUDE.md, memória: índice, `geral/atualizador.md` do `fase-1`,
  regras de trabalho, lições, catálogo dos erros; plano-v3 peças 1, 4, 9, passo 3, §6.1, §8; Lista de bugs de 18/11;
  revisão do atualizador de 18/11; estudo do Kraken de 18/11; ONDE-PAREI dos passos 1 e 2; o código de hoje; o
  código do Velopack 1.2.161 que usamos). Pacote montado (`anexos/pacote.md`).
- Plano escrito (`bcc57104`). A gerente conferiu ("não muda nenhuma decisão do Samuel") e mandou seguir. Respostas do
  Samuel na D-825 (21/11): os 16 testes antigos da lista podem mudar (só esses); pergunta 1, opção B (a senha não liga
  os testes nesta entrega).
- Conserto 1 `85590fe4`; conserto 2 `f32eab48`; conserto 3 `77a05d2e`; conserto 4 (commit em "Commit"). Cada um com
  commit e push, e com o teste de reversão rodado no código de antes dele (anexos/reversao-conserto*-codigo-antigo.txt).
- Rodada do GitHub 44975834257: success (2ª tentativa). 
- Volta 2 (relatório 1: 3 médios; o que mudou nas seções de cima está em "O que o agente que tentou quebrar achou", que vale sobre elas): médio 1 `f5d73572`, médio 2 `ebc4891e`, médio 3 `9979419d`, item 4 `6efa58d7`, item 5 `f523ec2e`. Rodada do GitHub 44982726269.
- **Volta 3 (22/11, escritor novo pela D-815; D-826 e D-827):** ver a seção "Volta 3" no fim deste arquivo, que vale
  sobre as de cima onde diferir. Situação: ver "Volta 3 > Onde parei".
- **Volta 4 (22/11, escritor novo pela D-815; D-828, depois da prova à vista):** ver a seção "Volta 4" no fim deste
  arquivo, que vale sobre as de cima onde diferir. Situação: ver "Volta 4 > Onde parei".

## Decisões que esta tarefa precisa cumprir

(Palavras copiadas do Livro, `docs/plano/DECISOES.md` da versão de teste; o pacote tem a linha inteira de cada uma.)

- **D-718** "Sim, e tem que avisar a gente de alguma maneira". Aqui: a volta da versão que falha continua como está.
- **D-719** "1". Aqui: a frase da falha não muda.
- **D-724** "gratis, mas o que é essa assinatura e é segura?". Aqui: a assinatura antes de baixar não muda; o motor que
  vem no instalador só vai para o lugar se a soma dele for a do motor-exigido.json, que vem dentro do pacote assinado.
- **D-727** "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né". Aqui: o motor do
  instalador é posto no lugar sem baixar nada.
- **D-732** "não, faz quando o programa é aberto". Aqui: a procura ao abrir não muda.
- **D-733** "1- sim / VAI CONSEGUIR FAZER OS TESTS A DISTANCIA NÉ?". Aqui: a pergunta da primeira abertura continua
  criando o ajudante; muda só quem pede a licença (a peça única). Com a senha digitada, ver a D-825.
- **D-734** "quando ele abrir o programa de novo". Aqui: continua valendo nesta entrega (a D-769/D-794 ficam para
  depois); conserto 3 faz essa abertura funcionar.
- **D-735** "Sim". Aqui: a pergunta aparece sempre, com ou sem a senha.
- **D-741** "Sim". Aqui: depois do "Não", a pergunta volta a cada abertura; quem decide passa a ser o Windows lido, não
  a marca.
- **D-749** "Sim". Aqui: erro no meio da preparação → conta como não feita e a pergunta volta; quem decide é o relatório
  da peça e a leitura do Windows (tarefas, Visual C++, Inno), não o preparo.txt.
- **D-763** "ok, pode fazer". Aqui: o nome do pacote não muda; o motor fica em `...\EditorImpressaoPrograma\motor-kraken\1`.
- **D-767** "não faça mais nada escodindo ou de mentira". Aqui: os testes automáticos só provam a lógica; a prova que
  vale é a sessão à vista da gerente com o Samuel.
- **D-774** "ok". Aqui: só o teste do `DETACHED_PROCESS` e o da marca nas Configurações mudam por ela; o resto vai ao
  Samuel um por um.
- **D-779** "ta vamos continuar com ele, mas o que fazemos para ele não dar defeito e porque nossa peças em voltadele
  deram defeito?". Aqui: Velopack 1.2.161 continua; a proteção (o socorro) fica para depois.
- **D-788** "1". Aqui: conserto 4.
- **D-796** "1, mas tem que ser explissito o pedido né". Aqui: só os arquivos da lista acima.
- **D-805** "a". Aqui: quem pede é o próprio programa, e a pergunta mostra "EditorImpressao.exe".
- **D-806** "então pode ser opção A". Aqui: conserto 2.
- **D-809** "ok". Aqui: nada de comando que mude o `.git` inteiro; nenhuma junção criada.
- **D-810** "ok". Aqui: os testes novos comparam conta pelo número e não supõem o estado do computador.
- **D-811**, **D-812**, **D-814** "ok". Aqui: as seções do formulário.
- **D-813** "ok". Aqui: a comparação do caminho do programa na tarefa é pela coisa de verdade (caminho normalizado).
- **D-815** "ok". Aqui: sou o escritor da volta 1.
- **D-819** "nova regra, sempre se deve se ver se é a coisa mais simples, ou melhor de se fazer". Aqui: cada conserto
  diz o jeito mais simples e por que foi escolhido (ou não).
- **D-824** "Sim, mas como vai ser feito esses 4 consertos, preciso que isso seja feito de forma rapida" · "vamos fazer
  com um só, uma coisa de cade vez.". Aqui: os 4, nessa ordem, um commit cada.
- **D-825** "porque tem que fazer teste?" · "você vai trocar os testes e fazer a opção B?" · "ok". Aqui: os 16 testes
  da lista mudaram (só esses), cada um falhando no código de antes; com a senha digitada, nenhum passo dos testes à
  distância roda; uma pergunta do Windows só, sempre.

## O que já está escolhido e testado aqui

- Testes que já existem para os arquivos que vou tocar: `tests/test_decisoes_ajudante_da_atualizacao.py`,
  `tests/test_decisoes_atualizacao.py`, `tests/test_decisoes_preparo_d749.py`, `tests/test_decisoes_testes_a_distancia.py`,
  `tests/test_decisoes_desinstalar.py`, `tests/test_decisoes_desinstalar_pasta.py`, `tests/test_decisoes_brasao.py`
  (a janelinha da D-742/D-748 e o `primeira_vez_se_preciso(janela)`), `tests/test_ocr_kraken.py`,
  `tests/test_ocr_diagnostico.py`, `tests/test_pasta_das_ferramentas.py`, `tests/test_windows_peca.py`,
  `tests/test_nome_do_pacote.py`, `tests/test_conferencias_*.py` (o porteiro e a lista de exceções).
- Escolhas que não mudam: D-734 (com "Depois", a troca na abertura seguinte, com a janelinha); a janelinha da D-742/D-748
  igual, letra por letra; "Reiniciar agora" grava antes de fechar; nenhuma pergunta do Windows por atualização; a
  assinatura antes de baixar; a conta de testes não pergunta nada (D-736); pelo código nada acontece (D-728); a janela da
  senha igual (D-824: "não mexa nela"); o `schtasks /Run` num lugar só (o teste conta `"/Run"` uma vez).
- O porteiro: 40 lugares da lista de exceções estão nos meus arquivos. Não renomeio nem movo `ao_desinstalar` e
  `criar_as_tarefas` (passo 5). Linha nova com palavra de conversa com o Windows (`Start-Process`, `schtasks`,
  `Update.exe`, `powershell`...) em `atualizacao.py` é erro novo: o código novo chama a peça; as linhas antigas que ficam
  não mudam de texto nem de função. Os lugares que eu consertar saem com `excecoes --diminuir`, no mesmo commit.

## Como fica para quem usa e no livro

O livro (o PDF) não muda em nada: nenhum dos 4 mexe no processamento das páginas.

**Primeira abertura depois de instalar** (o Kaique clica "Agora não" na senha, como combinado):
- Hoje: depois do "Agora não", a pergunta do Windows ("Deseja permitir...?") pode vir só piscando na barra; a janela
  fica parada ("Não está respondendo") enquanto o computador é preparado; se ele clicar "Não", o programa anota
  "preparado" e nunca mais pergunta; sem o ajudante, nenhuma versão entra.
- Depois: a pergunta vem logo depois do clique, com a janela do programa na frente (no meio da tela); mostra
  "EditorImpressao.exe" (D-805). A janela continua respondendo enquanto o computador é preparado (ele pode abrir um
  livro). "Não" → nada muda e a pergunta volta na próxima abertura. "Sim" → só conta como feito depois de o programa ler
  no Windows que o ajudante existe e aponta para o programa, que o Visual C++ e a instalação antiga estão certos. Nada de
  texto novo na tela.
- Se ele digitar a senha em vez de "Agora não" (D-825, opção B): a janela fecha como sempre, a mesma pergunta do
  Windows vem (uma só), e os testes à distância não ligam nesta entrega; nenhum aviso novo.
- Conferido na entrega: só por máquina (os testes). Clicar no programa instalado e ver a pergunta é da sessão à vista
  da gerente com o Samuel (eu não abro janela nem pergunta do Windows na tela dele). Problema novo que eu tenha visto:
  nenhum; os riscos estão em "Ressalvas".

**Aberturas seguintes, se ainda não deu "Sim"**: a janela abre como sempre; um ou dois segundos depois (o tempo de ler o
Windows por trás) vem a pergunta. Se ele já trocou de janela nesse meio-tempo, ela pisca na barra; se ninguém
responder, conta como "Não" e volta na próxima abertura.

**Aberturas seguintes, já preparado**: igual a hoje; por trás, o programa lê o Windows (um processo a mais, sem atrasar
a janela). Novo: se o ajudante sumiu (ex.: reinstalou), a pergunta volta sozinha (hoje nunca voltaria).

**"Reiniciar agora"**: hoje o programa fecha e não volta. Depois: o programa fecha gravando, a troca acontece por trás
(alguns minutos, sem nada na tela: a janelinha em toda troca é da D-770, fica para depois) e o programa volta sozinho na
versão nova. Se a troca não conseguir nem começar, o programa fecha gravado como hoje e a versão entra na próxima
abertura (D-734).

**"Depois"**: hoje, com uma versão esperando, o programa não abre. Depois: ao abrir, aparece a janelinha "Atualizando o
programa, espere um pouco..." e o programa abre na versão nova; se a troca não começar, ele abre na versão de hoje e o
aviso de versão nova aparece de novo.

**O detector de linhas do Kraken**: nenhuma tela usa hoje (D-164). Depois da primeira abertura com "Sim", o ajudante põe
o motor em `C:\Program Files\EditorImpressaoPrograma\motor-kraken\1` por trás (uns minutos, prioridade baixa, nada na
tela); a atualização não o apaga; o programa o acha ali. A versão nova só entra com o motor no lugar.

## A causa, a regra e todos os caminhos

### Conserto 1. O pedido de licença do atualizador pela peça única

- **Causa.** O pedido da primeira abertura (`atualizacao.preparar_na_primeira_abertura`) vai pelo executor dos testes à
  distância (`core.testes_a_distancia.executor_atual()` → `ExecutorWindows.aplicar` →
  `core/_testes_a_distancia_windows.aplicar_no_windows` → `_rodar_elevado`). `_rodar_elevado` lê o erro com
  ctypes.get_last_error() numa biblioteca aberta sem `use_last_error=True`: sempre 0. O "Não" (1223) vira código 0,
  `Resultado(True)`, e `preparo_deu_certo` cai em "vale o resultado da pergunta inteira" (o passo nem rodou, o
  preparo.txt não tem a marca desta vez) → grava a marca nas Configurações → nunca mais pergunta. Segunda causa: o
  "preparado" é uma anotação (a marca nas Configurações e o preparo.txt), não o que o Windows tem.
- **A regra, num lugar só:**
  - pedir a licença: `core.windows.pedir_licenca` (a peça; já provada à vista em 19/11), com um passo só,
    `windows.passo_script`, que roda este programa com `--preparar-o-computador` e falha se ele terminar com erro;
  - "o computador está preparado?": uma função nova, `atualizacao.o_que_falta_no_computador()` (vazia = preparado),
    que **lê o Windows**: o ajudante existe e aponta para este programa (`windows.ler_tarefa`: comando = o .exe desta
    instalação, argumentos = `--procurar-atualizacao`, roda como o sistema); a tarefa "desfazer" existe
    (`windows.ler_tarefa`); o Visual C++ do pacote está instalado (`_ler_versao_do_visual_c` + `precisa_do_visual_c`, as
    de hoje); a instalação antiga do Inno não está mais (`achar_instalacao_do_inno` + `comando_para_tirar_o_inno`, as
    de hoje; a que o programa recusa tirar de propósito não conta, como hoje). É o que o `--preparar-o-computador` faz,
    lido de volta (D-749 ao pé da letra, sem anotação);
  - `falta_a_pergunta_do_windows()` passa a ser `bool(o_que_falta_no_computador())`; a marca das Configurações e o
    preparo.txt saem (`preparo_deu_certo`, `arquivo_do_preparo`).
- **Todos os caminhos** (grep por `preparar_na_primeira_abertura`, `falta_a_pergunta_do_windows`,
  `CHAVE_PERGUNTA_DO_WINDOWS_RESPONDIDA`, `preparo_deu_certo`, `passo_de_preparar_o_computador`, `_rodar_elevado`):
  1. primeira abertura com "Agora não" → `ui.primeira_vez_se_preciso` → `preparar_na_primeira_abertura("")`: hoje pelo
     executor antigo; passa à peça;
  2. primeira abertura com a opção dos testes desligada (sem janela da senha): o mesmo caminho;
  3. primeira abertura com a senha digitada: hoje `td.ligar` com o executor "acrescido" do preparo, numa pergunta;
     D-825 (opção B): a senha não liga os testes nesta entrega; a pergunta leva só o preparo;
  4. aberturas seguintes depois do "Não" (D-741) → `primeira_vez_se_preciso` → `falta_a_pergunta_do_windows()` →
     `preparar_na_primeira_abertura("")`: passa a ler o Windows;
  5. `--preparar-o-computador` (`preparar_como_administrador`, dentro da pergunta): **não muda** (cria as tarefas, Visual
     C++, Inno; devolve 0 só com tudo certo, D-749);
  6. o ajudante (`rodar_ao_ligar` → `preparar_o_computador`): não muda;
  7. `ui/tela_configuracoes`/`testes_a_distancia_ui.pedir_senha_e_ligar` (o botão das Configurações): é dos testes à
     distância, continua no executor antigo (passo 4); não passa por aqui.
- **Jeito mais simples (D-819) e por que este.** O mais simples seria só consertar a leitura do erro dentro de
  `_rodar_elevado` (uma linha). Não é o escolhido: deixaria duas peças pedindo licença (contra §11.12.1), o pedido
  continuaria abrindo o PowerShell com licença (a pergunta mostra "Windows PowerShell", contra a D-805), sem a janela do
  programa como dona (o defeito do conserto 2) e sem a caixa de erro escondida; e o `_rodar_elevado` é dos testes à
  distância (passo 4). A peça já existe, foi provada à vista e é o que o pedido manda. Para "preparado", o mais simples
  seria manter a marca e só gravá-la depois de ler o Windows uma vez; não é o escolhido porque a marca sobrevive a
  desinstalar e reinstalar (defeito 7 da revisão de 18/11: reinstalado, nunca mais pergunta e nunca mais atualiza) e o
  pedido diz "nunca de uma anotação".
- **Onde roda (regra "a janela nunca congela", CLAUDE.md §3, no pacote):** a leitura do Windows, a pergunta e a
  preparação rodam num fio por trás, iniciado por `primeira_vez_se_preciso`; a janela continua usável. (Como ficou no
  código: o aviso "Sem a senha..." aparece antes, no fio da tela, e o ajudante é chamado do próprio fio de trás; nada
  volta ao fio da tela, nem por sinal do Qt.) O fio é "daemon": se o Kaique fechar o programa no meio, ele morre junto, e o trabalho
  com licença (outro processo) termina sozinho; a próxima abertura lê o Windows. O mais simples (deixar no fio da tela,
  como hoje) congela a janela por minutos (Visual C++, Inno) e atrasaria cada abertura em 0,5 a 7 s (medido aqui: a
  leitura da tarefa levou 6,7 s a frio e 0,5 s depois), contra as regras do §3 e de não ficar mais lento.

### Conserto 2. A pergunta no meio da tela

- **Causa.** `_rodar_elevado` pede sem a janela do programa como dona (`hwnd` vazio) e sem trazê-la para a frente; a
  Microsoft diz que o Windows usa essa janela para decidir se a pergunta é "da frente" ou "de fundo" (de fundo = só
  pisca na barra). Em 18/11 as janelas estavam fora da frente; em 19/11, com o navegador na frente, piscou (D-806).
- **A regra:** `pedir_licenca(..., janela=<a janela principal>)` (a peça já traz a janela para a frente, confere se
  conseguiu e põe a janela como dona). Quem passa a janela: `primeira_vez_se_preciso(parent)` pega `int(parent.winId())`
  no fio da tela e entrega a `preparar_na_primeira_abertura(senha, janela=...)`. O instante: na primeira abertura, logo
  depois do clique em "Agora não"/"OK" (sem ler o Windows antes: nesta conta nunca houve "Sim"); nas seguintes, logo
  depois da leitura que diz que falta (o clique foi no atalho, segundos antes).
- **Caminhos:** os mesmos 1, 2 e 4 do conserto 1 (o 3, pela D-825, é o mesmo caminho). Não há outro pedido de licença no atualizador.
- **Jeito mais simples:** é este (passar a janela; a peça faz o resto). Esperar a janela ficar ativa antes de pedir
  (quando o Kaique trocou de janela) seria comportamento novo, não pedido; fica como ideia.

### Conserto 3. "Reiniciar agora" volta

- **Causa.** `_lancar_escondido` abre o PowerShell com `CREATE_NO_WINDOW | DETACHED_PROCESS`; a Microsoft diz que
  `CREATE_NO_WINDOW` é ignorado junto com `DETACHED_PROCESS`, e o PowerShell sem console sai sem rodar (provado na
  etapa 5). `trocar_e_reabrir` dá como feito porque o `Popen` não deu erro. Com "Depois", a mesma função: o programa sai
  para trocar e o script não roda → com versão esperando, ele nunca abre.
- **A regra:** o lançar solto da peça, `windows.lancar_powershell_solto` (sem a bandeira proibida, num grupo novo, com o
  sinal de vida: o script grava "comecei" na primeira linha e a peça espera até 30 s; sem sinal, fecha o lançado e diz
  "falhou"). `trocar_e_reabrir` só devolve True com o sinal de vida. O script da troca (`script_de_trocar_e_reabrir`)
  não muda de texto, a não ser o limite de espera (abaixo). Sai `_lancar_escondido`.
- **Caminhos** (grep por `trocar_e_reabrir`, `_lancar_escondido`, `aplicar_agora_e_reabrir`): (a) "Reiniciar agora" →
  `ui/aviso_de_atualizacao.VigiaDaAtualizacao._perguntar_reiniciar` → `aplicar_agora_e_reabrir` → `trocar_e_reabrir`;
  (b) abertura depois do "Depois" → `atender_linha_de_comando` → `trocar_antes_de_abrir` → `trocar_e_reabrir(janelinha=True)`.
  Os dois passam a lançar pela peça. Fora: a volta para a anterior (`_aplicar_pacote_quando_sair`, o Update.exe com a
  mesma bandeira) funcionou na etapa 5 (não é PowerShell) e a peça ainda não tem função para o Update.exe (ele está na
  lista dos que a peça recusa no lançar genérico): fica para o socorro do passo 3 inteiro; ressalva.
- **O limite de espera** (`LIMITE_DA_TROCA_S`, 300 s): sobe para 900 s (limiar, CLAUDE.md §6). Por quê: o script reabre
  o programa ao fim do limite mesmo com a troca no meio; o Velopack então fecha à força o programa aberto e a troca é
  anotada como falha, e a versão fica riscada (defeito 3 e 4 da revisão de 18/11). Sem o motor, a troca deve levar 2 a
  3 min (conta do estudo), mais o teste rápido; no notebook do Kaique não se sabe. O script continua parando antes,
  assim que o estado sai de "pendente"/"aplicando". A janelinha do "Depois" acompanha (o limite dela vem deste).
- **Jeito mais simples:** só tirar a bandeira `DETACHED_PROCESS` da linha (é o que a etapa 5 provou que roda). Não é o
  escolhido: continuaria sem conferir que o script começou (§11.12.2) e com uma segunda peça de lançar solto
  (§11.12.1); a peça já faz as duas coisas e foi provada à vista.

### Conserto 4. O motor do Kraken depois da atualização

- **Causa.** O publicar novo (passo 2) manda a atualização sem o motor; o instalador leva o motor como um arquivo só em
  current\instalar\motor-kraken-1.zip (D-788). Ninguém tira o motor de lá: o programa o procura em
  `current\motor-kraken` (`core/ocr_kraken.lugares_do_motor`, "ao lado do .exe"), e o teste rápido depois da troca exige
  `current\motor-kraken\python\python.exe` (`atualizacao.teste_rapido`). Resultado: depois do .msi o Kraken não é achado,
  e a primeira atualização falharia no teste rápido e voltaria (a troca leva o `current\instalar` embora, e com ele o
  único arquivo do motor).
- **A regra, num lugar só:**
  - onde o motor mora no programa instalado: `core/ocr_kraken.pasta_do_motor_instalado()` (nova) =
    `<raiz da instalação>\motor-kraken\<VERSAO_DO_MOTOR>`; `lugares_do_motor()` a usa como único lugar quando o programa
    é o instalado pelo Velopack (a regra de "instalado" é `atualizacao.instalado_pelo_velopack`, a de sempre); portátil
    e pelo código, os lugares de hoje;
  - "o motor está no lugar": `ocr_kraken.conferir_motor(pasta_do_motor_instalado())` (a conferência única do passo 2);
  - pôr no lugar: `atualizacao.garantir_o_motor()` (nova), o único que mexe em `motor-kraken\`: se já confere, nada;
    senão pega `current\instalar\motor-kraken-<v>.zip`, confere o espaço livre, abre em `motor-kraken\.chegando-<v>`,
    confere com `conferir_motor` e só então dá o nome final; erro → apaga o `.chegando` e registra. Roda no ajudante
    (como o sistema, por trás), no começo de `rodar_ao_ligar`, logo depois de `preparar_o_computador`;
  - **mudou do plano, no código:** a conferência da soma do arquivo contra o current\motor-exigido.json saiu. O nome e
    o formato desse arquivo moram só no `empacotar.py` (que não está na lista do pedido); ler o arquivo daqui seria
    copiar o formato (contra §11.12) ou pôr o empacotador dentro do programa do Kaique. A integridade fica com o que já
    existe num lugar só: a soma interna de cada arquivo do zip (o Python recusa o arquivo errado ao abrir) e a
    conferência única do motor (`conferir_motor`: a ficha e o tamanho de cada arquivo) antes do nome final. O arquivo do
    motor que vem no .msi não passa pela assinatura de qualquer jeito (o .msi é entregue à mão). Ressalva;
  - a troca não acontece sem o motor: em `procurar_e_preparar`, com o programa fechado e antes de pedir a troca ao
    Velopack, se o motor não confere, não troca (fica "pendente", registra; tenta na próxima vez);
  - o teste rápido usa a mesma conferência do motor (sai o caminho escrito à mão), e o `--conferir-ocr` já usa
    `achar_pasta_do_motor` (vem junto).
- **Caminhos** (grep por `motor-kraken`, `lugares_do_motor`, `achar_pasta_do_motor`, `conferir_motor`, `NOME_DA_PASTA`):
  `MotorKraken` (pela `achar_pasta_do_motor`), `core/ocr_diagnostico` (`--conferir-ocr`), `atualizacao.teste_rapido`,
  o ajudante (`rodar_ao_ligar`), `procurar_e_preparar`; o empacotador e o publicar (`empacotar.LUGARES_DO_MOTOR`,
  `conferir_motor` no publicar) não mudam.
- **Motor novo pela internet (D-790): não é necessário para a primeira entrega.** Todas as versões desta entrega pedem o
  motor 1. Se alguém publicar uma versão que peça o motor 2 antes da D-790, a versão nova falha no teste rápido (que lê
  a versão de motor da versão nova) e volta para a anterior (D-718): seguro, mas com o aviso de falha ao Kaique.
  Ressalva: não publicar motor novo antes da D-790.
- **Jeito mais simples:** abrir o motor do zip direto no `--preparar-o-computador` (dentro da pergunta). Não é o
  escolhido: a janela esperaria a abertura de 34 mil arquivos (minutos) e a pergunta ficaria mais longa; o estudo do
  Kraken (§2.1) já indica o ajudante, por trás. Outro mais simples ainda: o instalador já pôr o motor solto no lugar
  final; não dá: o .msi instala só o que o Velopack empacota, dentro de `current` (o passo 2 escolheu o arquivo único
  de propósito, D-788).

## O que pode falhar e o que o programa faz

Conserto 1 e 2 (a pergunta da primeira abertura):
- **"Não"** (ou fechar a pergunta pelo X): a peça devolve "você disse Não; nada mudou" (código 1223, lido com
  `use_last_error`). Registro anotado; a próxima abertura lê o Windows (falta o ajudante) e pergunta de novo (D-741).
- **Conta do Kaique sem administrador** (o Windows pede a senha de outro): sem ela, o Windows devolve o mesmo
  "cancelado" → como o "Não".
- **Ninguém responde / a pergunta só pisca e cai** (~90 s, visto em 18/11): "cancelado" → como o "Não". A janela não
  fica parada (o pedido está no fio de trás).
- **A janela não está na frente** (ele trocou de janela): a peça tenta trazê-la, diz que não conseguiu
  (`janela_na_frente`); a pergunta pisca na barra; registro anotado.
- **O programa a abrir com licença não existe / disco cheio para o pedido:** a peça devolve "falhou" com o motivo,
  sem a caixa crua do Windows; registro; a pergunta volta na próxima abertura.
- **A preparação dá erro no meio** (Visual C++, Inno, uma das tarefas): o `--preparar-o-computador` termina com 1, o
  passo do script falha, a peça devolve "falhou"; e a leitura do Windows diz o que falta → a pergunta volta (D-749).
  O que foi feito naquela vez fica (é o mesmo de hoje: uma tarefa criada, o Inno tirado) e é refeito na próxima.
- **O trabalho com licença passa do limite** (60 min): a peça devolve "falhou: pode continuar" e deixa a pasta de troca;
  a próxima abertura lê o Windows como estiver.
- **Desligar ou fechar o programa no meio:** o fio de trás morre com o programa; o trabalho com licença (outro processo)
  segue ou para com o Windows; a próxima abertura lê o Windows (nunca uma anotação).
- **A conta comum não consegue ler a tarefa** (o Windows diz "existe" e "acesso negado"): conta como "falta" (não dá
  para conferir que aponta para o programa) → a pergunta voltaria toda vez. A licença do ajudante dá leitura às contas
  comuns (`QUEM_PODE_MANDAR_RODAR`, "GRGX" para AU); a sessão à vista confere. Se falhar lá, paro e pergunto.
- **O Windows não responde à leitura** (PowerShell bloqueado, tempo esgotado): `ler_tarefa` devolve "não deu para
  saber" → conta como "falta" → pergunta. Melhor perguntar de novo que dar como preparado sem saber.
- **Política ou antivírus bloqueiam o PowerShell com licença:** o passo falha → "falhou" → volta.
- **Sem internet:** a pergunta e a preparação não usam a rede; nada muda.
- **Arquivo preso** (outro programa segura a pasta de troca ou o desinstalador antigo): a peça diz o que ficou; o
  preparo que não terminou dá "falhou" e a pergunta volta (D-749).

Conserto 3 ("Reiniciar agora" e "Depois"):
- **O script não dá sinal de vida em 30 s** (antivírus, política, PowerShell que não roda): a peça fecha o lançado e diz
  "falhou"; `trocar_e_reabrir` devolve False. "Reiniciar agora": o programa já fechou gravado (como hoje no "não
  começou"); a versão entra na próxima abertura. "Depois": o programa abre na versão de hoje e o aviso aparece de novo
  (nada de sair sem janela).
- **O programa está preso a um grupo do Windows que mataria o lançado:** a peça recusa antes ("falhou") → o mesmo.
  (Lido no Velopack: o atalho de partida abre o programa com `CreateProcessW` comum, sem grupo.)
- **O ajudante não existe** (sem "Sim"): o script não consegue mandar rodar e reabre logo, na versão de hoje (como hoje).
- **A troca passa do limite** (900 s): o script reabre o programa; se a troca ainda estiver no meio, o Velopack o fecha
  e a troca fica anotada como falha (como hoje com 300 s, só que mais raro).
- **A troca falha** (Velopack): o Velopack reabre a versão anterior com `--conferir-a-versao-nova` (lido em `apply.rs`);
  o que vem depois é o de hoje (ver "Ideias e bugs": essa falha não fica anotada).
- **O programa reaberto não vem para a frente** (quem abre é um processo de fundo): ele aparece, talvez atrás; à vista.
- **Disco cheio para o script:** a peça diz "falhou" → como o primeiro caso.
- **Sem internet:** o lançar não usa a rede; a troca usa o pacote já baixado; sem internet o ajudante não acha versão
  nova e nada troca (como antes).
- **Sem licença:** nada aqui pede licença (o ajudante roda como o sistema; o script, na conta do Kaique).
- **Arquivo preso** (o antivírus segura um arquivo do programa na troca): o Velopack tenta de novo 10 a 30 vezes; se
  não der, a troca falha como antes.

Conserto 4 (o motor):
- **Sem o arquivo do motor em `instalar\` e sem motor no lugar:** registra "falta o motor"; a versão nova não troca
  (fica "pendente"); o Kaique continua na versão de hoje. (Acontece se o instalador foi feito sem o motor.)
- **Um arquivo do zip com a soma interna errada, ou faltando um arquivo da ficha:** o abrir ou a conferência acusa;
  o provisório é apagado; registra; não troca.
- **Disco sem espaço** (o tamanho aberto do motor mais uma folga, conferido antes): não começa; registra; tenta depois.
  Enche no meio: o erro apaga o `.chegando`.
- **Desligar no meio:** sobra só o `.chegando-<v>`, nunca o nome final; a próxima vez o apaga e recomeça.
- **Antivírus segura ou tira um arquivo (arquivo preso):** abrir ou conferir falha → apaga o `.chegando`, registra, tenta
  depois.
- **Sem internet:** o motor vem do arquivo do instalador; nada é baixado.
- **Sem licença:** só o ajudante (o sistema) põe o motor; a janela do Kaique nunca tenta.
- **Motor no lugar, mas estragado:** a conferência acusa; se o arquivo do motor ainda está em `instalar\`, o estragado é
  posto de lado e o novo entra; se não, registra e não troca.
- **O Kaique abre o programa enquanto o motor chega:** sem problema (nome final só no fim; nenhuma tela usa o Kraken).
- **A atualização:** o Velopack só renomeia `current` e põe a nova no lugar; `motor-kraken\` ao lado fica (lido no
  código). Ele fecha à força o motor se estiver aberto (o programa está fechando).
- **A volta para a anterior:** o motor continua no lugar dele.
- **Pelo código e no portátil:** nada muda (os lugares de hoje; o `garantir_o_motor` não roda no portátil).
- **Desinstalar:** o .msi apaga a pasta da instalação inteira, com o motor (lido no estudo); a limpeza que confere é do
  passo 5.

## Cada proteção e o teste que falha sem ela

(Cada teste falha no código de antes do seu conserto: `anexos/reversao-conserto1-codigo-antigo.txt` a
`anexos/reversao-conserto4-codigo-antigo.txt`. Os itens P01 a P71 no fim são a volta 3 (D-827): a lista inteira refeita no código de agora, cada proteção desligada sozinha numa cópia, `anexos/mutacoes-volta3.txt`, com o script `anexos/mutar3.py.txt`: 60 de 60 acusadas.)
- O "Não" da peça não vira preparado: `tests/test_atualizador_4.py::test_conserto1_o_nao_do_windows_nao_vira_preparado`, `tests/test_decisoes_ajudante_da_atualizacao.py::test_d733_disse_nao_fica_anotado_e_nada_quebra`.
- "Sim" só conta com o Windows mostrando o ajudante: `tests/test_atualizador_4.py::test_conserto1_sim_so_conta_com_o_windows_mostrando_o_ajudante`.
- O ajudante de outro programa conta como falta: `tests/test_atualizador_4.py::test_conserto1_ajudante_de_outro_programa_conta_como_falta`.
- O caminho do ajudante comparado como arquivo (D-813): `tests/test_atualizador_4.py::test_conserto1_o_mesmo_caminho_escrito_diferente_e_o_mesmo_ajudante`.
- "Não deu para ler" conta como falta: `tests/test_atualizador_4.py::test_conserto1_nao_deu_para_ler_o_ajudante_conta_como_falta`.
- Preparação parada no meio volta (D-749): `tests/test_decisoes_preparo_d749.py::test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta`.
- O passo falha quando o preparo falha: `tests/test_decisoes_preparo_d749.py::test_d749_o_passo_anota_como_o_preparo_terminou`, `tests/test_decisoes_ajudante_da_atualizacao.py::test_d733_o_passo_de_preparar_roda_este_exe_escondido_e_nao_para_a_pergunta`.
- Anotação velha não conta: `tests/test_decisoes_preparo_d749.py::test_d749_uma_anotacao_velha_nao_conta`.
- A marca das Configurações saiu: `tests/test_decisoes_ajudante_da_atualizacao.py::test_d741_a_marca_e_de_fabrica_falsa_e_gravada_so_pelo_sim`.
- Reinstalado sem o ajudante, a pergunta volta: `tests/test_atualizador_4.py::test_conserto1_reinstalado_sem_o_ajudante_a_pergunta_volta`.
- Visual C++ e Inno pela mesma regra de quem faz: `tests/test_atualizador_4.py::test_conserto1_visual_c_e_inno_sao_a_mesma_regra_de_quem_instala_e_tira`.
- O Inno que não se tira de propósito não falta: `tests/test_atualizador_4.py::test_conserto1_a_instalacao_antiga_que_o_programa_nao_tira_de_proposito_nao_falta`.
- O pedido de verdade não pergunta nada sob os testes: `tests/test_atualizador_4.py::test_conserto1_o_pedido_de_verdade_nao_pergunta_nada_sob_os_testes`.
- A pergunta roda por trás, não no fio da tela: `tests/test_atualizador_4.py::test_conserto1_a_tela_roda_a_pergunta_por_tras_e_nao_no_fio_da_tela`.
- O fio de trás é solto: `tests/test_atualizador_4.py::test_conserto1_o_fio_de_tras_e_solto`.
- Erro no fio de trás vira falta: `tests/test_atualizador_4.py::test_conserto1_um_erro_inesperado_no_fio_de_tras_conta_como_falta`.
- A senha não liga nenhum passo dos testes (D-825): `tests/test_atualizador_4.py::test_d825_a_senha_digitada_nao_liga_nenhum_passo_dos_testes`, `tests/test_decisoes_testes_a_distancia.py::test_d721_primeira_vez_pede_a_senha_e_liga`, `tests/test_decisoes_testes_a_distancia.py::test_d728_instalado_primeira_vez_pede_a_senha`.
- A janela vai como dona da pergunta: `tests/test_atualizador_4.py::test_conserto2_a_janela_do_programa_vai_como_dona_da_pergunta`; a janela entregue à peça: `tests/test_atualizador_4.py::test_conserto2_o_pedido_de_verdade_entrega_a_janela_a_peca` (este passa no código do conserto 1, que já a entregava; falha no código de partida).
- A janela fora da frente fica anotada: `tests/test_atualizador_4.py::test_conserto2_a_janela_que_nao_veio_para_a_frente_fica_anotada`.
- O lançar da troca pela peça, só com o sinal de vida, sem a bandeira proibida: `tests/test_decisoes_ajudante_da_atualizacao.py::test_d733_o_script_escondido_vai_codificado_e_solto`.
- "Reiniciar agora" pela peça: `tests/test_atualizador_4.py::test_conserto3_reiniciar_agora_lanca_a_troca_pela_peca`.
- "Depois" sem sinal de vida abre o programa: `tests/test_atualizador_4.py::test_conserto3_depois_com_a_troca_que_nao_comeca_o_programa_abre`.
- O limite de 900 s chega ao script e à janelinha: `tests/test_atualizador_4.py::test_conserto3_o_limite_da_troca_chega_ao_script_e_a_janelinha`.
- O motor posto e conferido, sem refazer: `tests/test_atualizador_4.py::test_conserto4_o_ajudante_poe_o_motor_do_instalador_no_lugar_dele`.
- Sem espaço, não começa: `tests/test_atualizador_4.py::test_conserto4_sem_espaco_nao_comeca`.
- O nome final nunca pela metade: `tests/test_atualizador_4.py::test_conserto4_motor_estragado_no_arquivo_nunca_fica_com_o_nome_final`.
- O estragado é trocado: `tests/test_atualizador_4.py::test_conserto4_motor_estragado_no_lugar_e_trocado_pelo_do_instalador`.
- Sem nada, diz e não finge: `tests/test_atualizador_4.py::test_conserto4_sem_o_arquivo_e_sem_o_motor_diz_e_nao_finge`.
- A troca não acontece sem o motor: `tests/test_atualizador_4.py::test_conserto4_a_troca_nao_acontece_sem_o_motor_no_lugar`.
- A mesma conferência do motor: `tests/test_atualizador_4.py::test_conserto4_o_motor_no_lugar_e_a_mesma_conferencia`.
- O ajudante põe o motor antes de procurar, nunca no portátil: `tests/test_atualizador_4.py::test_conserto4_o_ajudante_poe_o_motor_antes_de_procurar_e_nunca_no_portatil`.
- O instalado procura o motor só no lugar dele, e o teste rápido usa a mesma busca: `tests/test_atualizador_4.py::test_conserto4_o_programa_instalado_procura_o_motor_so_no_lugar_dele`.

- P01 o ajudante que nao existe deixa de faltar (V07) → `tests/test_atualizador_4.py::test_conserto1_o_nao_do_windows_nao_vira_preparado`, `tests/test_atualizador_4.py::test_conserto1_sim_so_conta_com_o_windows_mostrando_o_ajudante`
- P02 'nao deu para saber' do ajudante deixa de faltar (volta 3, item 1) → `tests/test_atualizador_4.py::test_conserto1_nao_deu_para_ler_o_ajudante_conta_como_falta`, `tests/test_atualizador_4.py::test_volta3_item1_depois_do_sim_com_o_windows_que_nao_deixa_ler_a_pergunta_volta`
- P03 'nao deu para saber' do desfazer deixa de faltar (volta 3, item 1) → `tests/test_atualizador_4.py::test_volta3_item1_depois_do_sim_com_o_windows_que_nao_deixa_ler_a_pergunta_volta`
- P04 o desfazer que nao existe deixa de faltar (M06, V11) → `tests/test_decisoes_preparo_d749.py::test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta`
- P05 'existe mas nao le' vira falta (V13) → `tests/test_atualizador_4.py::test_conserto1_nao_deu_para_ler_o_ajudante_conta_como_falta`
- P06 sem a conferencia da peca (V09) → `tests/test_atualizador_4.py::test_conserto1_ajudante_de_outro_programa_conta_como_falta`, `tests/test_atualizador_4.py::test_conserto1_o_mesmo_caminho_escrito_diferente_e_o_mesmo_ajudante`
- P07 a licenca ilegivel vira falta (V08) → `tests/test_atualizador_4.py::test_volta3_item2_o_que_nao_deu_para_conferir_fica_dito_e_nada_e_dado_como_preparado`, `tests/test_atualizador_4.py::test_volta3_item3_com_a_licenca_ilegivel_o_resto_do_ajudante_ainda_e_conferido`
- P08 a licenca ilegivel pula o resto (volta 3, item 3) → `tests/test_atualizador_4.py::test_volta3_item3_com_a_licenca_ilegivel_o_resto_do_ajudante_ainda_e_conferido`
- P09 a licenca lida nao e conferida → `tests/test_atualizador_4.py::test_volta2_item4_a_conferencia_do_ajudante_e_a_da_peca_com_a_licenca`
- P10 os argumentos do ajudante nao sao comparados (M05) → `tests/test_atualizador_4.py::test_volta3_item3_com_a_licenca_ilegivel_o_resto_do_ajudante_ainda_e_conferido`, `tests/test_atualizador_4.py::test_volta3_m05_o_ajudante_com_outros_argumentos_ou_outra_conta_falta`
- P11 a conta do ajudante nao e comparada (M05) → `tests/test_atualizador_4.py::test_volta3_item3_com_a_licenca_ilegivel_o_resto_do_ajudante_ainda_e_conferido`, `tests/test_atualizador_4.py::test_volta3_m05_o_ajudante_com_outros_argumentos_ou_outra_conta_falta`
- P12 o comando do ajudante nao e comparado → `tests/test_atualizador_4.py::test_conserto1_ajudante_de_outro_programa_conta_como_falta`, `tests/test_atualizador_4.py::test_conserto1_o_mesmo_caminho_escrito_diferente_e_o_mesmo_ajudante`
- P13 o 'deu certo' da peca basta (M09) → `tests/test_atualizador_4.py::test_conserto1_sim_so_conta_com_o_windows_mostrando_o_ajudante`, `tests/test_atualizador_4.py::test_volta3_item2_o_que_nao_deu_para_conferir_fica_dito_e_nada_e_dado_como_preparado`
- P14 o passo engole o codigo de saida (M10) → `tests/test_decisoes_preparo_d749.py::test_d749_o_passo_anota_como_o_preparo_terminou`
- P15 a abertura seguinte nao le o Windows (M11) → `tests/test_atualizador_4.py::test_conserto1_reinstalado_sem_o_ajudante_a_pergunta_volta`, `tests/test_atualizador_4.py::test_conserto2_a_janela_do_programa_vai_como_dona_da_pergunta`
- P16 o ajudante nao roda depois do Sim (M12) → `tests/test_atualizador_4.py::test_conserto1_preparado_nao_pergunta_e_depois_do_sim_o_ajudante_roda`
- P17 o ajudante roda mesmo faltando (volta 3, item 2) → `tests/test_atualizador_4.py::test_volta3_item1_depois_do_nao_com_o_windows_que_nunca_deixa_ler_a_pergunta_volta_a_cada_abertura`, `tests/test_atualizador_4.py::test_volta3_item2_o_que_nao_deu_para_conferir_fica_dito_e_nada_e_dado_como_preparado`
- P18 o 'Nao' volta a dizer a consequencia sem ler (volta 3, item 2) → `tests/test_atualizador_4.py::test_volta3_item2_sem_sim_o_registro_diz_o_que_a_leitura_mostrou`
- P19 o que nao deu para conferir vira 'preparado' (volta 3, item 2) → `tests/test_atualizador_4.py::test_volta3_item2_o_que_nao_deu_para_conferir_fica_dito_e_nada_e_dado_como_preparado`
- P20 o desfecho sem o Sim volta a supor o que faltou (volta 3, item 2) → `tests/test_atualizador_4.py::test_volta3_item2_sem_sim_o_registro_diz_o_que_a_leitura_mostrou`
- P21 a janela fora da frente nao fica anotada → `tests/test_atualizador_4.py::test_conserto2_a_janela_que_nao_veio_para_a_frente_fica_anotada`
- P22 o passo de preparar nao roda o --preparar-o-computador → `tests/test_atualizador_4.py::test_conserto1_a_pergunta_vai_pela_peca_unica_com_um_passo_so`, `tests/test_decisoes_ajudante_da_atualizacao.py::test_d733_com_a_senha_preparo_e_testes_numa_pergunta_so`
- P23 a senha liga os testes (M13) → `tests/test_atualizador_4.py::test_d825_a_senha_digitada_nao_liga_nenhum_passo_dos_testes`, `tests/test_decisoes_ajudante_da_atualizacao.py::test_d733_com_a_senha_preparo_e_testes_numa_pergunta_so`
- P24 sem a janela dona (M14) → `tests/test_atualizador_4.py::test_conserto2_a_janela_do_programa_vai_como_dona_da_pergunta`
- P25 a pergunta no fio da tela (M15) → `tests/test_atualizador_4.py::test_conserto1_a_tela_roda_a_pergunta_por_tras_e_nao_no_fio_da_tela`
- P26 o fio de tras nao e solto (M16) → `tests/test_atualizador_4.py::test_conserto1_o_fio_de_tras_e_solto`
- P27 as aberturas seguintes nao perguntam de novo → `tests/test_atualizador_4.py::test_conserto2_a_janela_do_programa_vai_como_dona_da_pergunta`, `tests/test_decisoes_ajudante_da_atualizacao.py::test_d741_nao_a_pergunta_volta_na_proxima_abertura_e_sim_ela_nao_volta_mais`
- P30 lancar sem conferir o sinal de vida (M17) → `tests/test_atualizador_4.py::test_conserto3_depois_com_a_troca_que_nao_comeca_o_programa_abre`, `tests/test_decisoes_ajudante_da_atualizacao.py::test_d733_o_script_escondido_vai_codificado_e_solto`
- P31 o limite da troca volta a 300 s (M18) → `tests/test_atualizador_4.py::test_conserto3_o_limite_da_troca_chega_ao_script_e_a_janelinha`
- P32 a troca que nao comecou devolve True → `tests/test_atualizador_4.py::test_conserto3_depois_com_a_troca_que_nao_comeca_o_programa_abre`, `tests/test_decisoes_ajudante_da_atualizacao.py::test_d733_o_script_escondido_vai_codificado_e_solto`
- P33 o 'Depois' sem a janelinha → `tests/test_atualizador_4.py::test_conserto3_depois_com_a_troca_que_nao_comeca_o_programa_abre`, `tests/test_decisoes_ajudante_da_atualizacao.py::test_d742_quem_pede_a_janelinha`
- P40 o motor aberto nao e conferido (M19) → `tests/test_atualizador_4.py::test_conserto4_motor_estragado_no_arquivo_nunca_fica_com_o_nome_final`
- P41 o espaco nao e conferido (M20) → `tests/test_atualizador_4.py::test_conserto4_sem_espaco_nao_comeca`
- P42 o motor aberto direto no nome final (M21) → `tests/test_atualizador_4.py::test_conserto4_o_ajudante_poe_o_motor_do_instalador_no_lugar_dele`, `tests/test_atualizador_4.py::test_conserto4_motor_estragado_no_lugar_e_trocado_pelo_do_instalador`
- P43 o erro nao apaga o provisorio (M22) → `tests/test_atualizador_4.py::test_conserto4_motor_estragado_no_arquivo_nunca_fica_com_o_nome_final`, `tests/test_atualizador_4.py::test_volta2_medio1_arquivo_do_motor_estragado_de_qualquer_jeito_e_apagado_e_registrado`
- P44 a troca sem o motor no lugar (M23, V03) → `tests/test_atualizador_4.py::test_conserto4_a_troca_nao_acontece_sem_o_motor_no_lugar`, `tests/test_atualizador_4.py::test_volta2_medio2_sem_o_motor_a_versao_nao_e_anunciada_nem_trocada`
- P45 o ajudante nao poe o motor (M24) → `tests/test_atualizador_4.py::test_conserto4_o_ajudante_poe_o_motor_antes_de_procurar_e_nunca_no_portatil`
- P46 o motor tambem no portatil (M25) → `tests/test_atualizador_4.py::test_conserto4_o_ajudante_poe_o_motor_antes_de_procurar_e_nunca_no_portatil`
- P47 o instalado procura no lugar antigo (M26) → `tests/test_atualizador_4.py::test_conserto4_o_programa_instalado_procura_o_motor_so_no_lugar_dele`
- P48 o teste rapido nao confere o motor (M27) → `tests/test_atualizador_4.py::test_volta3_m27_o_teste_rapido_recusa_o_motor_estragado`
- P49 o motor ja no lugar nao e conferido (M28) → `tests/test_atualizador_4.py::test_conserto4_motor_estragado_no_lugar_e_trocado_pelo_do_instalador`
- P50 o estragado nao e posto de lado (M29) → `tests/test_atualizador_4.py::test_conserto4_motor_estragado_no_lugar_e_trocado_pelo_do_instalador`
- P51 garantir_o_motor volta a pegar so alguns erros (V01) → `tests/test_atualizador_4.py::test_volta2_medio1_arquivo_do_motor_estragado_de_qualquer_jeito_e_apagado_e_registrado`
- P52 o ajudante sem o try do motor (V02) → `tests/test_atualizador_4.py::test_volta2_medio1_um_erro_no_motor_nao_impede_o_ajudante_de_procurar`
- P53 o 'pendente' de antes nao vira 'esperando-o-motor' (V04) → `tests/test_atualizador_4.py::test_volta2_medio2_sem_o_motor_a_versao_nao_e_anunciada_nem_trocada`
- P54 a tela le 'esperando-o-motor' como versao nova (V05) → `tests/test_atualizador_4.py::test_volta2_medio2_sem_o_motor_a_versao_nao_e_anunciada_nem_trocada`
- P55 baixa antes de conferir o motor (V14) → `tests/test_atualizador_4.py::test_volta2_medio2_sem_o_motor_a_versao_nao_e_anunciada_nem_trocada`
- P56 'o motor esta no lugar' sem conferir → `tests/test_atualizador_4.py::test_conserto4_o_motor_no_lugar_e_a_mesma_conferencia`
- P60 o ajudante nao completa o Visual C++ e a instalacao antiga (M07, M08) → `tests/test_atualizador_4.py::test_volta3_m07_m08_o_ajudante_completa_o_visual_c_e_a_instalacao_antiga_toda_vez_que_roda`
- P61 a preparacao nao instala o Visual C++ (M07) → `tests/test_decisoes_preparo_d749.py::test_d749_visual_c_ou_inno_que_falham_contam_como_erro`, `tests/test_decisoes_atualizacao.py::test_d723_instalacao_de_verdade_prepara_o_computador`
- P62 a preparacao nao tira a instalacao antiga (M08) → `tests/test_decisoes_atualizacao.py::test_d723_instalacao_de_verdade_prepara_o_computador`
- P63 o Visual C++ que falhou conta como certo → `tests/test_decisoes_preparo_d749.py::test_d749_visual_c_ou_inno_que_falham_contam_como_erro`
- P64 a instalacao antiga que nao saiu conta como certa → `tests/test_decisoes_preparo_d749.py::test_d749_visual_c_ou_inno_que_falham_contam_como_erro`
- P65 o Visual C++ instalado sem faltar → `tests/test_atualizador_4.py::test_conserto1_visual_c_e_inno_sao_a_mesma_regra_de_quem_instala_e_tira`, `tests/test_decisoes_atualizacao.py::test_d727_o_visual_c_so_roda_se_faltar`
- P66 a preparacao com erro devolve 0 (D-749) → `tests/test_decisoes_preparo_d749.py::test_d749_o_modo_preparar_devolve_erro_quando_algo_falha_no_meio`
- P67 a tarefa desfazer que nao nasceu conta como certa (M06, na criacao) → `tests/test_atualizador_4.py::test_volta3_m06_a_preparacao_so_da_certo_com_as_duas_tarefas_criadas`
- P68 a preparacao com o Visual C++ falhando devolve certo → `tests/test_decisoes_preparo_d749.py::test_d749_visual_c_ou_inno_que_falham_contam_como_erro`
- P69 o Inno tirado sem conferir o caminho → `tests/test_decisoes_atualizacao.py::test_d723_o_comando_que_tira_o_inno`
- P70 o Visual C++ volta para a pergunta (V12; contra a D-826 (1)) → `tests/test_atualizador_4.py::test_volta2_medio3_visual_c_mais_novo_numa_versao_nova_nao_traz_a_pergunta_de_volta`
- P71 a instalacao antiga volta para a pergunta (contra a D-826 (1)) → `tests/test_atualizador_4.py::test_conserto1_a_instalacao_antiga_que_o_programa_nao_tira_de_proposito_nao_falta`, `tests/test_atualizador_4.py::test_volta2_medio3_visual_c_mais_novo_numa_versao_nova_nao_traz_a_pergunta_de_volta`

## De onde vem cada dado que a conferência usa

- "Preparado": o Agendador do Windows (`ler_tarefa`, pelo COM do Windows), o registro do Windows (Visual C++ e Inno) e
  o arquivo instalar\vc_redist.versao.txt do pacote. Nada que o programa anota.
- O desfecho da pergunta: o relatório que o programa com licença escreve na pasta de troca, conferido pela peça (dono e
  licença da pasta; o relatório decide junto com o código de saída), e depois a leitura do Windows, que é o que vale.
- O "começou" da troca: o arquivo de sinal que o próprio script lançado grava (prova só que ele começou; o resto é a
  troca, conferida pelo estado que o ajudante grava como o sistema, como antes).
- O motor: a soma interna de cada arquivo do zip (o Python confere ao abrir) e a ficha motor.json com o tamanho de
  cada arquivo no disco (`conferir_motor`). (A soma contra o motor-exigido.json saiu do plano; ver o conserto 4.)
- Nos testes: o Windows de mentira (`WindowsDeMentira`), que prova só a lógica em volta (D-767).

## O que li da peça de fora e onde

- **Pedir licença (`ShellExecuteExW`, verbo "runas"):** o erro vem de `GetLastError`; "ERROR_CANCELLED" quando a pessoa
  cancela; `hwnd` é a janela dona; `SEE_MASK_FLAG_NO_UI` esconde a caixa de erro
  (https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecuteexw e .../ns-shellapi-shellexecuteinfow).
  Só com `use_last_error=True` o ctypes.get_last_error() traz o erro da chamada (https://docs.python.org/3/library/ctypes.html).
  "The UAC elevation mechanism uses the HWND as part of determining whether the elevation is a background or foreground
  elevation"; "Background applications will automatically prompt the user for elevation on the taskbar"
  (https://learn.microsoft.com/en-us/previous-versions/bb756922(v=msdn.10)). "An application cannot force a window to
  the foreground while the user is working with another window" (.../winuser/nf-winuser-setforegroundwindow). Lido pelo
  passo 1 e conferido no código da peça (`_abrir_com_licenca`, `trazer_para_a_frente`, `o_que_houve_ao_abrir`).
- **O que a peça faz em cada caso** (lido em core/windows.py:2554, core/windows.py:2631, core/windows.py:2296, core/windows.py:1710, core/windows.py:1966): DISSE_NAO só para 1223; FALHOU para todo outro erro;
  DEU_CERTO só com o relatório completo, os mesmos passos e código 0; passou do limite → FALHOU e a pasta fica.
  `passo_script`: o lado com licença roda o texto pelo `rodar_powershell` (cabeça com `$ErrorActionPreference = 'Stop'`,
  marca de UTF-8): um `throw` no texto faz o passo dar "falhou". `lancar_powershell_solto`: arquivo com marca de UTF-8,
  sem a bandeira proibida, sinal de vida em 30 s, senão fecha o lançado; recusa se o grupo mataria o lançado.
  `ler_tarefa`: "não existe" (0x80070002/3), "existe sem leitura" (0x80070005), "não deu para saber" (outro).
- **`DETACHED_PROCESS` com `CREATE_NO_WINDOW`:** "CREATE_NO_WINDOW... This flag is ignored if the application is not a
  console application, or if it is used with either CREATE_NEW_CONSOLE or DETACHED_PROCESS"
  (https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags); provado na etapa 5
  (o registro das variantes do lançar, na pasta saida_teste da etapa 5, fora do git).
- **Velopack 1.2.161, a troca** (https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/commands/apply_windows_impl.rs e https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/shared/util_windows.rs, lidos em 21/11): extrai
  a versão nova numa pasta temporária, fecha à força tudo o que roda dentro da raiz (`force_stop_package(root)`, que
  pula só ele mesmo), renomeia `current` para a temporária velha (10 tentativas de 1 s) e a nova para `current` (30
  tentativas); depois só o registro de desinstalar, atalhos, `Update.exe` e o atalho de partida da raiz. Nada mais da
  raiz é apagado: `motor-kraken\` ao lado fica. Na segunda renomeação que falha, pode ficar sem `current` (defeito
  conhecido, D-779). Os processos achados são os cujo arquivo está dentro da raiz (`util_windows.rs`,
  `get_processes_running_in_directory`): o PowerShell do Windows (em System32) não é fechado.
- **Velopack, o reinício** (https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/commands/apply.rs): com `restart`, depois de trocar abre a versão nova com
  os mesmos argumentos (`start_package`); se a troca falhar, abre a versão de antes com os mesmos argumentos e devolve o
  erro.
- **Velopack, como abre o programa** (https://github.com/velopack/velopack/blob/1.2.161/src/lib-rust/src/process_win.rs, `run_process`, linha 352): `CreateProcessW` com
  `CREATE_UNICODE_ENVIRONMENT` (com janela) ou mais `CREATE_NO_WINDOW`, sem grupo de processos, e
  `AllowSetForegroundWindow` para o aberto; não espera. Então o programa aberto pelo atalho não está num grupo que mate
  os filhos, e pode tomar a frente.
- **Velopack, a pasta fora de `current`** (https://github.com/velopack/velopack/blob/1.2.161/docs/integrating/preserved-files.mdx): "If you want to create settings that persist through updates, but are erased
  when the app is uninstalled, on Windows you should store them one level up (`..\`) outside of the `current` dir"
  (`docs/integrating/preserved-files.mdx`, citado no estudo do Kraken §1, ramo `kraken-separado-2026-11-18`).
- **`zipfile` (Python 3.14, https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile.extract):** ao abrir, nome com caminho absoluto perde a unidade e as barras do começo, e todo ".."
  sai (documentação de `ZipFile.extract`); arquivo com a soma interna errada dá "Bad CRC-32". A entrada que aceita: o
  zip do motor (um arquivo só, `versao.arquivo_do_motor`, em `current\instalar\`). Não aceito outro nome nem outro lugar.
- **`os.rename` no Windows (https://docs.python.org/3/library/os.html#os.rename):** se o destino existe, `FileExistsError` sempre (documentação do `os`); por isso o nome
  final só é dado depois de o destino não existir (o estragado é posto de lado antes), e no mesmo disco.
- **`shutil.rmtree` no Windows (https://docs.python.org/3/library/shutil.html#shutil.rmtree):** desde o Python 3.8 não apaga o que está do outro lado de um atalho de pasta (junção),
  só o atalho (documentação do `shutil`). Só é chamado em `motor-kraken\.chegando-<v>` e `.estragado-<v>-...`.
- **`shutil.disk_usage` (https://docs.python.org/3/library/shutil.html#shutil.disk_usage):** total, usado e livre do disco do caminho (documentação do `shutil`).
- **PowerShell `Start-Process -Wait -PassThru` (https://learn.microsoft.com/powershell/module/microsoft.powershell.management/start-process):** devolve o processo e espera; o `ExitCode` é o do programa. O mesmo
  jeito de antes (`passo_de_preparar_o_computador`), provado na etapa 5 (a preparação rodou e tirou o Inno às 09:02:07).
- **Python `threading.Thread(daemon=True)` (https://docs.python.org/3/library/threading.html#thread-objects):** o fio solto não segura a saída do programa (documentação do `threading`:
  "the entire Python program exits when only daemon threads are left").
- **Deduzido, a provar à vista** (a licença do ajudante: atualizacao.py:156, `QUEM_PODE_MANDAR_RODAR`; a peça que traz a janela: core/windows.py:1819): que a conta comum lê a tarefa do ajudante e a do desfazer (pela licença delas); que a
  pergunta vem no meio da tela com a janela dona e na frente; que o programa reaberto pelo script aparece.

## O que foi feito

1. **Conserto 1** (`85590fe4`): a pergunta da primeira abertura vai pela peça única (`atualizacao.pedir_licenca_ao_windows`
   → `core.windows.pedir_licenca`), com um passo de script que roda `--preparar-o-computador` e falha se ele falhar
   (`passo_de_preparar_o_computador`). "Preparado" é lido do Windows (`o_que_falta_no_computador`: o ajudante existe e
   aponta para este programa, a tarefa desfazer, o Visual C++, a instalação antiga); saíram a marca das Configurações e o
   preparo.txt. A pergunta e a preparação rodam num fio solto por trás (`ui/testes_a_distancia_ui._rodar_por_tras`,
   `atualizacao.preparar_ao_abrir`). Depois de um "Sim" que deixa tudo no lugar, o ajudante roda uma vez. D-825 (B): a
   senha digitada não liga nada (só o registro anota que foi digitada; ela não é guardada nem enviada). "Falta o Visual
   C++?" e "falta tirar o Inno?" viraram uma regra só para quem faz e quem confere (`visual_c_que_falta`,
   `inno_que_falta_tirar`).
2. **Conserto 2** (`f32eab48`): a janela principal (o número dela, `ui/testes_a_distancia_ui.numero_da_janela`) vai ao
   pedido; a peça a traz para a frente e a põe como dona da pergunta. Se ela não veio para a frente, o registro anota.
3. **Conserto 3** (`77a05d2e`): `trocar_e_reabrir` lança o script pela peça (`_lancar_pela_peca` →
   `core.windows.lancar_powershell_solto`) e só dá como começado com o sinal de vida; saiu `_lancar_escondido`. O limite
   de espera da troca sobe de 300 para 900 s.
4. **Conserto 4** (`75cfa928`): o motor mora em `<raiz>\motor-kraken\<versão>` (`core/ocr_kraken.pasta_do_motor_instalado`);
   `atualizacao.garantir_o_motor` o põe lá, no ajudante, a partir do arquivo do instalador; a troca não acontece sem ele
   (`motor_esta_no_lugar`, em `procurar_e_preparar`); o programa instalado procura só ali e o teste rápido usa a mesma
   busca e conferência.

**Como a senha deixou de ligar (D-825):** em `primeira_vez_se_preciso`, com a senha digitada, o código só anota no
registro que ela foi digitada; não chama `td.ligar`, não passa a senha a ninguém. Com "Agora não", continua o
`td.ligar("")` de sempre (não toca o Windows; só o aviso "Sem a senha..."). O resto da janela da senha e os testes à
distância (o botão das Configurações) não mudaram. Prova: `test_d825_a_senha_digitada_nao_liga_nenhum_passo_dos_testes`
(a peça dos testes à distância e o `ligar` fazem o teste falhar se forem chamados; a senha não aparece no pedido; uma
pergunta só).

5. **Volta 3** (D-826, D-827): ver "Volta 3 > O que foi feito (volta 3)" no fim.

## Arquivos criados ou alterados

- `atualizacao.py` (os 4 consertos)
- `core/ocr_kraken.py` (conserto 4: `pasta_do_motor_instalado`, `lugares_do_motor`)
- `ui/testes_a_distancia_ui.py` (consertos 1 e 2: `primeira_vez_se_preciso`, `_rodar_por_tras`, `numero_da_janela`)
- `configuracoes.py` (saiu a marca `atualizacao_computador_preparado`)
- `empacotar.py` (volta 2, item 5: só o comentário de `NOME_DO_MOTOR_EXIGIDO`, a pedido da gerente)
- `tests/test_atualizador_4.py` (novo)
- `tests/test_decisoes_ajudante_da_atualizacao.py` (só os da D-825/D-774)
- `tests/test_decisoes_preparo_d749.py` (só os da D-825)
- `tests/test_decisoes_testes_a_distancia.py` (só os da D-825)
- `tests/conferencias_excecoes.json` (a lista do porteiro diminuiu: 175 → 168)
- `relatorios/atualizador-4/` (este formulário, o pacote e as provas de reversão)

## Como cumpri cada uma

- D-718/D-719: a volta e a frase não mudaram (`tests/test_decisoes_atualizacao.py` passa inteiro).
- D-724: a assinatura antes de baixar não mudou (`test_d724_*` passam).
- D-727: o motor do instalador vai para o lugar sem baixar nada (`test_conserto4_o_ajudante_poe_o_motor_do_instalador_no_lugar_dele`).
- D-732: a procura ao abrir não mudou (`test_d732_*` passam).
- D-733/D-735: uma pergunta só, sempre, com o preparo (`test_d733_com_a_senha_...`, `test_d735_*`).
- D-734: "Depois" troca na abertura seguinte; se a troca não começa, o programa abre (`test_conserto3_depois_...`, `test_d734_*`).
- D-741: "Não" → volta; "Sim" → nunca mais (`test_d741_*`), lido no Windows.
- D-749: preparação pela metade → volta (`test_d749_*`).
- D-763: o nome do pacote não mudou (`tests/test_nome_do_pacote.py`, no GitHub).
- D-767: os testes são de lógica; a prova que vale é a sessão à vista (ver "A prova de verdade").
- D-774: o teste do `DETACHED_PROCESS` e o da marca mudaram para cobrar o jeito certo (falham no código de antes).
- D-779: Velopack 1.2.161, sem mexer nele.
- D-788: o motor em `...\motor-kraken\1`, fora do que a atualização troca (conserto 4).
- D-796: só os arquivos da lista (o porteiro K13 confere).
- D-805: quem pede é o próprio programa (a peça abre `EditorImpressao.exe`).
- D-806: a janela vai como dona e o pedido sai logo depois do clique (conserto 2).
- D-809: nada de comando no `.git` inteiro; nenhuma junção criada. As cópias do código de antes, para a reversão, foram
  tiradas com `git archive` numa pasta da cópia e apagadas no fim.
- D-810: os testes não supõem o computador (o Windows de mentira; o PowerShell só no teste do passo, como antes).
- D-811/D-812/D-814: seções acima.
- D-813: o caminho do ajudante é comparado como arquivo (`_mesmo_caminho`; teste).
- D-815: sou o escritor da volta 1.
- D-819: o jeito mais simples de cada conserto está no plano, com o porquê.
- D-824: os 4, um commit cada, nesta ordem.
- D-825: os 16 testes mudaram, cada um falha no código de antes e passa no novo (anexos de reversão); a senha não liga
  nada (prova acima).
- D-826 e D-827 (volta 3): ver "Volta 3 > Como cumpri cada uma (volta 3)".

## Testes

- No PC (um arquivo por vez): `test_atualizador_4.py` 34 passaram; `test_decisoes_ajudante_da_atualizacao.py` 37;
  `test_decisoes_preparo_d749.py` 9; `test_decisoes_testes_a_distancia.py` 13; `test_decisoes_atualizacao.py` 38;
  `test_decisoes_desinstalar.py` 46; `test_decisoes_brasao.py` 22; `test_ocr_kraken.py` 28 (5 pulados: o motor de
  verdade não está nesta cópia, defeito antigo nº 330); `test_ocr_diagnostico.py` 6; `test_pasta_das_ferramentas.py`
  17; `test_conferencias_codigo.py` 122; `test_conferencias_excecoes.py` 14. O porteiro: "nada novo", 168 lugares.
- Reversão: os 16 testes mudados e os novos de cada conserto falham no código de antes daquele conserto
  (`anexos/reversao-conserto1-codigo-antigo.txt` a `anexos/reversao-conserto4-codigo-antigo.txt`; o conserto 1 rodado contra `4a775ba8`: 36 falham). Só
  `test_conserto2_o_pedido_de_verdade_entrega_a_janela_a_peca` passa no código do conserto 1 (ver acima).
- GitHub: rodada 44975834257 (a 44975331433 foi cancelada: testava o commit antes das docstrings); o resultado em "Commit".

**Volta 3:** ver "Volta 3 > Testes (volta 3)"; GitHub: rodada 44992797990: success na 1ª tentativa (a 44991980992 foi cancelada por mim: testava o commit antes das docstrings dos testes).

## Caminho e função

- Primeira abertura, "Agora não" / opção desligada / senha digitada → `ui.primeira_vez_se_preciso` →
  `atualizacao.preparar_ao_abrir(janela, primeira_vez=True)` → `preparar_na_primeira_abertura` →
  `pedir_licenca_ao_windows` (→ `core.windows.pedir_licenca`) e `o_que_falta_no_computador`.
- Aberturas seguintes (D-741) → `ui.primeira_vez_se_preciso` → `preparar_ao_abrir(janela, primeira_vez=False)` →
  `o_que_falta_no_computador`; se falta, o mesmo de cima.
- "Preparado?" (todos) → `o_que_falta_no_computador` (`falta_a_pergunta_do_windows` chama a mesma).
- Dentro da pergunta → `--preparar-o-computador` → `preparar_como_administrador` (não mudou).
- "Reiniciar agora" → `ui/aviso_de_atualizacao.VigiaDaAtualizacao._perguntar_reiniciar` → `aplicar_agora_e_reabrir`
  → `trocar_e_reabrir` → `_lancar_pela_peca` → `core.windows.lancar_powershell_solto`.
- Abertura depois do "Depois" → `atender_linha_de_comando` → `trocar_antes_de_abrir` → `trocar_e_reabrir(janelinha=True)`
  → o mesmo.
- Motor: o ajudante (`rodar_ao_ligar`, também o de longe, D-736) → `garantir_o_motor`; a troca → `procurar_e_preparar`
  → `motor_esta_no_lugar`; o programa (`MotorKraken`, `--conferir-ocr`, `teste_rapido`) → `ocr_kraken.achar_pasta_do_motor`
  → `lugares_do_motor` → `pasta_do_motor_instalado`; a conferência em todos → `ocr_kraken.conferir_motor`.
- As provas que cobram o mesmo resultado pelos caminhos: a pergunta pela primeira abertura e pelas seguintes, com a
  mesma janela e o mesmo "preparado" (`tests/test_atualizador_4.py::test_conserto2_a_janela_do_programa_vai_como_dona_da_pergunta`,
  `tests/test_decisoes_ajudante_da_atualizacao.py::test_d741_nao_a_pergunta_volta_na_proxima_abertura_e_sim_ela_nao_volta_mais`);
  a troca pelo "Reiniciar agora" e pelo "Depois", pela mesma peça (`tests/test_atualizador_4.py::test_conserto3_reiniciar_agora_lanca_a_troca_pela_peca`,
  `tests/test_atualizador_4.py::test_conserto3_depois_com_a_troca_que_nao_comeca_o_programa_abre`); o motor pela mesma
  pasta e conferência no ajudante, na troca e no programa (`tests/test_atualizador_4.py::test_conserto4_o_motor_no_lugar_e_a_mesma_conferencia`,
  `tests/test_atualizador_4.py::test_conserto4_o_programa_instalado_procura_o_motor_so_no_lugar_dele`).
- Fora (de propósito): a volta para a anterior (`_aplicar_pacote_quando_sair`, o Update.exe) e o botão dos testes à
  distância nas Configurações (`pedir_senha_e_ligar`, peça antiga, passo 4).
- Volta 3: ver "Volta 3 > Caminho e função (volta 3)".

## Máquina ou olho

Máquina: os testes acima (a lógica em volta). Olho e à vista (D-767): a pergunta no meio da tela, o "Não", o "Sim",
o "Reiniciar agora", o "Depois", o motor posto no lugar e a atualização de verdade: só na sessão da gerente com o Samuel.

## Os 16 testes antigos mudados (D-774 e D-825)

Mudados com a autorização da D-825 (Samuel, 21/11: "ok") e da D-774; os nomes ficaram os mesmos. Cada um falha no
código de antes e passa no novo (conferido: `anexos/reversao-conserto1-codigo-antigo.txt` e `anexos/reversao-conserto3-codigo-antigo.txt`).

- **D-774 cobre:**
  1. `test_decisoes_ajudante_da_atualizacao.py::test_d733_o_script_escondido_vai_codificado_e_solto` (cobra o
     `DETACHED_PROCESS`; passa a cobrar o lançar pela peça com o sinal de vida). Plano-v3 §8, item 1.
  2. `test_decisoes_ajudante_da_atualizacao.py::test_d741_a_marca_e_de_fabrica_falsa_e_gravada_so_pelo_sim` (cobra a
     marca nas Configurações; passa a cobrar a leitura do Windows). Plano-v3 §8, item 5.
- **Autorizados pela D-825** (todos cobravam o pedido antigo, pela peça dos testes à distância, ou a anotação):
  3. `test_d733_com_a_senha_preparo_e_testes_numa_pergunta_so` (preparo e testes numa pergunta só pelo pedido antigo;
     depende da pergunta 1);
  4. `test_d735_sem_a_senha_a_pergunta_do_windows_aparece_assim_mesmo` (o preparo pelo pedido antigo);
  5. `test_d735_agora_nao_na_senha_nao_pula_a_pergunta_do_windows` (idem, e espera a pergunta acontecer antes de a
     função voltar; agora ela roda por trás);
  6. `test_d735_com_a_opcao_desligada_a_pergunta_do_windows_aparece` (idem);
  7. `test_d733_disse_nao_fica_anotado_e_nada_quebra` (o "Não" do pedido antigo);
  8. `test_d733_o_passo_de_preparar_roda_este_exe_escondido_e_nao_para_a_pergunta` (cobra o passo antigo, que engolia o
     erro com `catch { }`; o novo falha quando o preparo falha);
  9. `test_d741_nao_a_pergunta_volta_na_proxima_abertura_e_sim_ela_nao_volta_mais` (pedido antigo e a marca);
  10. `test_d741_sim_na_primeira_abertura_nao_volta_mais` (idem);
  11. `test_d741_na_conta_de_testes_nada_pergunta_mesmo_depois_de_um_nao` (idem);
  12. `test_decisoes_preparo_d749.py::test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta` (o preparo.txt);
  13. `test_decisoes_preparo_d749.py::test_d749_uma_anotacao_velha_nao_conta` (o preparo.txt);
  14. `test_decisoes_preparo_d749.py::test_d749_o_passo_anota_como_o_preparo_terminou` (o preparo.txt);
  15. `test_decisoes_testes_a_distancia.py::test_d721_primeira_vez_pede_a_senha_e_liga` (com a senha; depende da
      pergunta 1; e espera a pergunta antes de a função voltar);
  16. `test_decisoes_testes_a_distancia.py::test_d728_instalado_primeira_vez_pede_a_senha` (idem).
  Cada um passa a cobrar o mesmo comportamento da decisão (D-733, D-735, D-741, D-749) pelo jeito novo: a pergunta pela
  peça, o "preparado" lido do Windows; os de senha (3, 15, 16) cobram a D-825 (a senha não liga os testes). Nenhum
  outro teste antigo mudou nem quebrou no PC (os arquivos rodados estão em "Testes"); a rodada do GitHub confere o
  resto.

## Ressalvas

- O teste automático não prova a pergunta do Windows, a troca nem o motor de verdade (D-767): é a sessão à vista.
- **A volta para a anterior continua com o lançar antigo do Update.exe**, como a gerente mandou. As linhas exatas
  (`atualizacao.py`, função `_aplicar_pacote_quando_sair`, linhas 697 a 700 do commit `75cfa928`):
  `subprocess.Popen([str(update_exe()), "apply", "--silent", "--norestart",` /
  `"--waitPid", str(os.getpid()), "--package", str(arquivo)],` /
  `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` / `| getattr(subprocess, "DETACHED_PROCESS", 0))`; e o
  caminho do Update.exe em `update_exe` (linha 496: `return pasta_do_programa().parent / "Update.exe"`). **Já estão na
  lista de exceções do porteiro** (K01 duas vezes e K02 uma em `_aplicar_pacote_quando_sair`, K01 em `update_exe`, de
  19/11, passo 3): o porteiro não barrou, e nenhum item novo foi posto na lista.
- A soma do arquivo do motor contra o motor-exigido.json saiu do plano (ver o conserto 4). Se a gerente quiser essa
  trava, é preciso pôr o nome e o formato do motor-exigido.json num lugar que o programa e o empacotador leiam (mexe
  no `empacotar.py`, fora da lista).
- Não publicar uma versão que peça um motor novo antes da D-790: ela entraria, falharia no teste rápido e voltaria.
- A troca que o Velopack não consegue fazer reabre a versão de antes, que se dá como "ok" (já na Lista de bugs).
- Uma leitura do Windows a cada abertura (dois PowerShell por trás: o ajudante e o desfazer). Não atrasa a janela; a
  primeira leitura depois de ligar o computador levou 6,7 s aqui.
- Se a conta comum não conseguir ler o ajudante ou o desfazer no Windows de verdade, a pergunta voltaria toda vez: a
  sessão à vista confere (nunca rodou de verdade).
- O programa reaberto depois do "Reiniciar agora" pode aparecer atrás de outra janela (quem o abre é um processo de
  fundo); à vista.
- "Reiniciar agora" fica sem nada na tela durante a troca (a janelinha em toda troca é da D-770, fica para depois).
- Com a senha digitada nesta entrega, nada avisa o Kaique que ela não ligou os testes (o mínimo da D-825; nenhum texto
  novo).
- O pacote portátil do ensaio nunca é dado como "falta preparar" (e_portatil), como antes.
- Volta 3: ver "Volta 3 > Ressalvas (volta 3)".

## Velocidade

Não se aplica: nenhum dos 4 mexe no processamento das páginas (o filtro de velocidade é da gerente, se ela quiser). A
abertura da janela não ganha espera: as leituras novas rodam por trás. O caminho do livro não usa o Kraken (D-164).

## Ideias e bugs

- **Bug (21/11, lido no código, não impede):** quando o Velopack não consegue trocar, ele reabre a versão de antes com
  `--conferir-a-versao-nova` (`apply.rs`); `conferir_e_refazer_o_ajudante` roda o teste rápido nela, passa, e grava
  "ok" com a versão de antes como "nova": a falha da troca some. A gerente: já está na Lista de bugs.
- **Ideia:** se a janela não está na frente, esperar o Kaique voltar a ela para pedir a licença (em vez de piscar).
- **Ideia:** `atualizacao.xml_da_tarefa` e `core.windows.xml_da_tarefa_do_sistema` desenham o mesmo XML (o passo 3
  inteiro junta); e `atualizacao._aspas_do_powershell` repete `core.windows.aspas_do_powershell`.
- Volta 3: ver "Volta 3 > Ideias e bugs (volta 3)".

## Perguntas para o Samuel

Nenhuma aberta. A pergunta 1 (a senha digitada na primeira abertura) foi respondida na D-825: opção B, "ok".

## Decisões procuradas antes de cada pergunta

Não se aplica: nenhuma pergunta aberta (a pergunta 1 foi respondida, D-825).

## Commit

- Plano: `bcc57104`. Conserto 1: `85590fe4`. Conserto 2: `f32eab48`. Conserto 3: `77a05d2e`. Conserto 4: `75cfa928`.
- Último commit do código e dos testes: `dd06e85f` (as docstrings dos testes e este formulário).
- GitHub: rodada 44975834257 (ramo `atualizador-4-consertos-2026-11-21`; testou o commit `70ceaf61`, o mesmo código de `dd06e85f`): success na 2ª tentativa. A 1ª caiu na parte 1: `test_promessas.py` saiu com 3221225477 (o Qt quebrando, "cannot get C stack"), sem nenhum teste falhado antes; na repetição, as 5 partes, os botões e o porteiro passaram. No PC, `test_promessas.py` inteiro deu 269 passados e 1 falhado (`test_p082_filtros_em_tela_cheia`, a tela cheia dos filtros), que passou sozinho em seguida (2 de 2): instável com o PC carregado, sem ligação com estes consertos.

- Volta 2: médio 1 `f5d73572`, médio 2 `ebc4891e`, médio 3 `9979419d`, item 4 `6efa58d7`, item 5 `f523ec2e` (último do código e dos testes).
- GitHub da volta 2: rodada 44982726269 (commit `f523ec2e`): success na 2ª tentativa (testou `f523ec2e`, conferido no registro da rodada). A 1ª caiu na parte 2: `test_decisoes_gravura_a_mao.py::test_d659_g_outros_filtros_a_mao_nada_e_procurado_e_sai_igual_ao_de_antes[original]` ("procurou: [0]", o detector de gravura), que não usa nada destes consertos; no PC, o arquivo inteiro passou (15 de 15).

- Volta 3: plano `1e8518cf`; item 1 `ce728693`; item 2 `ebd4197e`; item 3 `f15863b8`; item 4 `126f01d0`; as docstrings das peças de mentira dos testes novos `b897efb7` (último do código e dos testes). GitHub da volta 3: rodada 44992797990: success na 1ª tentativa (a 44991980992 foi cancelada por mim: testava o commit antes das docstrings dos testes).

## O que o agente que tentou quebrar achou

**Relatório 1** (`quem-quebrou/relatorio-1.md`, commit `6b7eeddd`): NÃO ESTÁ PRONTO, 3 médios, nenhum grave. Volta 2
(o mesmo escritor, a segunda e última volta dele, D-815). Cada conserto com commit e push, e com teste que falha no
código de antes dele, por comportamento (`anexos/reversao-volta2-medio1.txt`, `anexos/reversao-volta2-medio2.txt`,
`anexos/reversao-volta2-medio3.txt`, `anexos/reversao-volta2-item4.txt`).

- **Médio 1, o arquivo do motor estragado** (`f5d73572`): `garantir_o_motor` pega qualquer erro (o `zlib.error` do
  pedaço comprimido inválido, o `EOFError` do arquivo cortado, um erro inesperado): apaga o provisório, registra
  "motor do Kraken: não deu para pôr no lugar" e devolve False, como a docstring promete. `rodar_ao_ligar` nunca deixa um
  erro do motor impedir a procura da versão nova. Testes: `tests/test_atualizador_4.py::test_volta2_medio1_arquivo_do_motor_estragado_de_qualquer_jeito_e_apagado_e_registrado`
  (com o zip estragado de verdade, dos dois jeitos) e `tests/test_atualizador_4.py::test_volta2_medio1_um_erro_no_motor_nao_impede_o_ajudante_de_procurar`.
- **Médio 2, sem o motor no lugar** (`ebc4891e`): a regra única (`procurar_e_preparar`) confere o motor ANTES de baixar.
  Sem ele, não baixa nem anuncia: devolve "sem-motor"; um "pendente" de antes vira "esperando-o-motor", que `situacao`
  lê como "nada" (a tela não mostra "Chegou uma versão nova", a abertura não tenta trocar, o "Reiniciar agora" de um
  aviso que já estava na tela reabre logo na mesma versão e o aviso não volta). Registra; o ajudante tenta de novo da
  próxima vez. **Nenhum texto novo na tela.** Teste: `tests/test_atualizador_4.py::test_volta2_medio2_sem_o_motor_a_versao_nao_e_anunciada_nem_trocada`
  (com o programa aberto e fechado). O meu teste da volta 1 `test_conserto4_a_troca_nao_acontece_sem_o_motor_no_lugar`,
  que cobrava o "pendente", passa a cobrar o "sem-motor" (é deste trabalho, não dos 16 antigos).
- **Médio 3, a pergunta que voltava depois do "Sim"** (`9979419d`). Como ficou cada caso:
  - *Versão nova com um Visual C++ mais novo:* a pergunta não volta. A regra única (`o_que_falta_no_computador`) lê só o
    que só a pergunta faz: as tarefas do ajudante e do desfazer. O Visual C++ e a instalação antiga o próprio ajudante
    completa, como o sistema, sem perguntar, toda vez que roda (`preparar_o_computador`, como antes). Teste:
    `tests/test_atualizador_4.py::test_volta2_medio3_visual_c_mais_novo_numa_versao_nova_nao_traz_a_pergunta_de_volta`.
  - *O Windows não deixa ler as tarefas:* "não deu para saber" não traz a pergunta de volta; o registro diz "não deu para
    ler ...; não pergunto de novo por isso". "Existe, mas esta conta não lê" conta como existe. Teste:
    `tests/test_atualizador_4.py::test_volta2_medio3_windows_que_nao_deixa_ler_nao_traz_a_pergunta_de_volta`.
  - Depois de um "Não" (as tarefas não existem), a pergunta continua voltando (D-741):
    `tests/test_atualizador_4.py::test_volta2_medio3_depois_do_nao_a_pergunta_continua_voltando`.
  - **O que isto muda na D-749 (para a gerente ver):** "Sim" com a preparação parada ANTES de criar as tarefas continua
    trazendo a pergunta de volta (o teste da D-749 continua passando). Mas se as tarefas nasceram e o que falhou foi o
    Visual C++ ou a instalação antiga, a pergunta não volta: o ajudante completa sozinho, sem perguntar, e o registro diz
    isso. É o único jeito de cumprir a D-741/D-735 no caso do Visual C++ novo sem uma anotação do programa (os dois
    casos têm a mesma leitura no Windows). Se a gerente ou o Samuel quiserem a pergunta de volta nesse caso, é preciso
    escolher entre as duas decisões.
  - Também ao contrário do que era: depois de um "Não", se o Windows não deixar ler, a pergunta não aparece naquela
    abertura (só numa em que der para ler). Saiu a `inno_que_falta_tirar` (ninguém mais a usava). Dois testes meus da
    volta 1 mudaram junto (`test_conserto1_nao_deu_para_ler_o_ajudante_conta_como_falta`, cujo nome ficou, e
    `test_conserto1_visual_c_e_inno_sao_a_mesma_regra_de_quem_instala_e_tira`).
- **Item 4, a conta duplicada** (`6efa58d7`): "o ajudante é o deste programa?" usa a conferência da peça única,
  `core.windows.problemas_da_tarefa_criada` (a mesma da criação: o comando, os argumentos, quem roda e quem pode mandar
  rodar). Saiu `_mesmo_caminho`. Um ajudante que a conta do Kaique não pode chamar agora conta como falta. A licença que
  não deu para ler segue a regra do médio 3 (não pergunta; registra). `core/windows.py` não mudou. Teste:
  `tests/test_atualizador_4.py::test_volta2_item4_a_conferencia_do_ajudante_e_a_da_peca_com_a_licenca`.
- **Item 5, texto** (`f523ec2e`): os comentários de `core/ocr_kraken.conferir_motor` e de `empacotar.NOME_DO_MOTOR_EXIGIDO`
  dizem a verdade (a soma assinada é conferida na montagem, não no notebook). `empacotar.py` não estava na lista do
  pedido: só o comentário, a pedido da gerente. No formulário: a rodada testou `70ceaf61`; e "nada volta ao fio da tela
  por sinal do Qt". Sem teste (só texto).

**Testes nesta volta (no PC, um arquivo por vez):** `test_atualizador_4.py` 43; `test_decisoes_ajudante_da_atualizacao.py`
37; `test_decisoes_preparo_d749.py` 9; `test_decisoes_testes_a_distancia.py` 13; `test_decisoes_atualizacao.py` 38.
Porteiro: "nada novo", 168 lugares. Nenhum dos 16 testes antigos mudou de novo; nenhum outro teste antigo mudou.
**GitHub:** rodada 44982726269 (ver "Commit").

### Baixos para a lista do depois

(Do relatório 1; não consertados nesta volta, pela regra da D-824.)
1. Proteções sem teste que acuse quando são desligadas: M05 (não comparar os argumentos e a conta do ajudante; hoje é a
   peça, mas sem teste em que só isso muda), M06 (não conferir a tarefa desfazer), M27 (o teste rápido conferir só a
   forma do motor). (M07 e M08, Visual C++ e Inno, deixaram de existir na volta 2.) Cada item precisa de um teste em que só
   ele falta.
2. O motor é conferido inteiro (34 mil arquivos) a cada vez que o ajudante roda, e de novo antes de trocar e no teste
   rápido: 53 s na primeira vez e 10 s depois, no PC (medido por quem quebrou). Bastaria a leve a cada abertura e a
   inteira só antes de trocar.
3. No pacote portátil do Velopack o programa procuraria o motor num lugar que ninguém enche (as regras de "instalado" e
   "portátil" deviam ser uma). Hoje o publicar não faz o portátil.
4. O motor não é gravado no disco antes do nome final (o `zipar_motor` usa `windows.gravar_no_disco`; aqui não).
5. Uma pasta `.estragado-...` que não sai inteira (arquivo preso) fica para sempre.
6. Com "Agora não", o aviso "Sem a senha..." vem antes da pergunta do Windows (antes vinha depois).
7. "Na dúvida, é portátil" vira "nada falta" sem ler o Windows (`e_portatil`).
8. Na segunda conta do Windows no mesmo notebook, a pergunta vem sem ler o Windows antes.
9. A janelinha do "Depois" pode ficar até 18 min na tela se o ajudante travar (o limite de 900 s; antes eram 8 min).
10. A volta para a anterior (`_aplicar_pacote_quando_sair`) também dá como feita sem conferir.
11. O botão das Configurações (e a frase "pode pôr depois, em Configurações") ainda liga os testes pelo pedido antigo.

**Relatório 2** (`quem-quebrou/relatorio-2.md`, commit `9e2497b5`): os 3 médios consertados; 6 baixos e uma pergunta. A gerente levou ao Samuel (D-826, D-827, 22/11): o caso raro volta a perguntar a cada abertura; os baixos 1 e 2 consertados agora; toda proteção sem teste ganha teste. **Volta 3** (escritor novo): ver a seção "Volta 3" no fim. Os baixos 3 a 6 do relatório 2 e os baixos do relatório 1 que não são proteção sem teste continuam na lista do depois ("Baixos para a lista do depois", acima); o item 1 dessa lista (as proteções sem teste) foi feito na volta 3.

## A prova de verdade

(é da gerente, numa sessão com o Samuel, depois de quem tenta quebrar) Roteiro sugerido, com o programa instalado pelo
.msi do publicar novo: primeira abertura, "Agora não", a pergunta vem no meio da tela, "Não" → fechar e abrir → a
pergunta volta; "Sim" com o navegador na frente logo depois de abrir; ler no Windows que o ajudante existe; ver
`C:\Program Files\EditorImpressaoPrograma\motor-kraken\1` nascer; publicar uma versão nova; "Reiniciar agora" → o
programa volta na versão nova; outra versão, "Depois", fechar e abrir → a janelinha e a versão nova; `--conferir-ocr`
acha o motor depois da atualização.

## Perguntas do Windows que o Samuel vê

- Nesta entrega (código e testes automáticos): 0 (o pedido de verdade se recusa sob o pytest; nada pediu licença).
- Na sessão à vista: a da primeira abertura, umas três vezes ("Não", "Não" com o navegador na frente ou "Sim"); o
  número exato vai no roteiro da gerente.

## O print que prova

Não há print desta etapa: nenhuma tela mudou de aparência, e a prova à vista é da gerente com o Samuel. As provas de
máquina estão em `anexos/reversao-conserto1-codigo-antigo.txt` a `anexos/reversao-conserto4-codigo-antigo.txt`.

## Páginas em que foi conferido

Não se aplica: nenhuma página de livro passa por estes consertos (0 páginas; nenhum mexe em imagem nem no PDF).

## Volta 3 (22/11/2026, escritor novo; D-826 e D-827)

Escritor novo da volta 3 (D-815). Pedido da gerente: os 3 consertos da D-826 (um de cada vez, commit e push em cada
um) e a D-827 (toda proteção sem teste ganha teste agora, provado por mutação numa cópia).

### Onde parei (volta 3)

- 22/11: leitura feita (o meu arquivo de agente, CLAUDE.md §11.8/§11.12/§11.13, memória: índice e
  `geral/atualizador.md` do `fase-1`; este ONDE-PAREI inteiro; os relatórios 1 e 2 de quem tentou quebrar; as
  decisões D-733, D-735, D-741, D-749, D-767, D-811, D-824 a D-827 do Livro da versão de teste; o código de hoje:
  `o_que_falta_no_computador`, `preparar_na_primeira_abertura`, `preparar_ao_abrir`, `rodar_ao_ligar`,
  `preparar_o_computador`, `teste_rapido`, e na peça `ler_tarefa` e `problemas_da_tarefa_criada`). Plano abaixo.
- Plano `1e8518cf`. Item 1 `ce728693`; item 2 `ebd4197e`; item 3 `f15863b8` (cada um com commit e push e o teste
  rodado no código de antes dele: `anexos/reversao-volta3-item1.txt` a `-item3.txt`). Próximo: item 4 (as proteções
  sem teste, mutações numa cópia `git worktree add --detach` no meu rascunho).
- Item 4 `126f01d0` (60 de 60 proteções acusadas; a cópia foi tirada). GitHub: rodada 44992797990: success na 1ª tentativa (a 44991980992 foi cancelada por mim: testava o commit antes das docstrings dos testes). Entregue à gerente.

### Decisões que esta tarefa precisa cumprir (volta 3)

- **D-826** "porque a regra não funcionou?" · "2 - mas isso não estpa nas regras?" · "Sim, mas dai para arrumar esses 6
  problemas novos? vai ter que fazer novos remendos ou refazer tudo?". Aqui: (1) "Sim" com as tarefas prontas e só o
  Visual C++ ou a instalação antiga falhando: a pergunta não volta, o ajudante completa (fica como a volta 2 fez); as
  tarefas não prontas: a pergunta volta (D-749). **No caso raro em que o Windows não deixa ler as tarefas, a pergunta
  volta a cada abertura (D-741), não pula.** (2) Consertar os 2 problemas de código da volta 2 (o registro que diz o
  que não é; a conferência da tarefa que pula o resto quando a licença não é lida) e dar teste às proteções sem teste.
- **D-827** (regra de trabalho): "proteção sem teste nunca é 'baixo'"; "quando uma conferência é trocada por outra,
  antes se lista o que a antiga cobria, e só se troca quando a nova cobre tudo, com teste".
- **D-741** "Sim": depois do "Não", a pergunta volta a cada abertura, até o "Sim"; depois do "Sim", nunca mais.
- **D-749** "Sim": preparação com erro no meio conta como não feita (ajustada pela D-826 no caso do Visual C++ e da
  instalação antiga).
- **D-733** "1- sim / VAI CONSEGUIR FAZER OS TESTS A DISTANCIA NÉ?" e **D-735** "Sim": uma pergunta do Windows na
  primeira abertura, sempre, que cria o ajudante; nas atualizações seguintes, nenhuma pergunta.
- **D-767** "não faça mais nada escodindo ou de mentira": os testes daqui provam só a lógica em volta (Windows de
  mentira); a prova que vale é a sessão à vista.
- **D-811** "ok": a lista "cada proteção → o teste que falha quando ela é desligada, provado numa cópia".
- **D-824** "vamos fazer com um só, uma coisa de cade vez.": um conserto por commit, nesta ordem.
- **D-825** "ok": só os 16 testes antigos da lista podem mudar (e só nos casos do item 1, se precisar); a senha não
  liga os testes.
- **D-815** "ok": sou o escritor da volta 3 (agente novo).

### O que já está escolhido e testado aqui (volta 3)

- Os arquivos que vou tocar: `atualizacao.py` (só `o_que_falta_no_computador`, `preparar_na_primeira_abertura` e,
  para o item 3, `xml_da_tarefa`) e `tests/test_atualizador_4.py`. Testes que já existem para eles:
  `tests/test_atualizador_4.py` (43), `tests/test_decisoes_ajudante_da_atualizacao.py` (37),
  `tests/test_decisoes_preparo_d749.py` (9), `tests/test_decisoes_atualizacao.py` (38),
  `tests/test_decisoes_testes_a_distancia.py` (13), `tests/test_windows_peca.py` (71), `tests/test_conferencias_*.py`.
- O que não muda: a D-826 (1), o Visual C++ e a instalação antiga fora da pergunta (o ajudante completa); "existe, mas
  esta conta não lê" conta como existe (a mutação V13 do relatório 2 é acusada e continua); o "Sim" com tudo no lugar
  grava "o computador está preparado (lido no Windows)" (a prova à vista procura essa frase); "disse \"Não\"" e "não
  ficou preparado" no registro (testes antigos procuram); `core/windows.py` não muda; nenhuma frase nova na tela.
- Dos meus testes, mudam só os que cobram o contrário da D-826: `test_volta2_medio3_windows_que_nao_deixa_ler_nao_traz_a_pergunta_de_volta`
  e o caso `[None-False]` de `test_conserto1_nao_deu_para_ler_o_ajudante_conta_como_falta` (são deste trabalho, item 1
  do pedido). Nenhum dos 16 antigos precisa mudar (conferido por busca: nenhum usa "não deu para saber").

### Como fica para quem usa e no livro (volta 3)

O livro (o PDF) não muda: nada aqui mexe nas páginas. Nenhuma frase nova na tela.
- **Caso raro: o Windows não deixa ler as tarefas** (ex.: um antivírus que barra o PowerShell). Hoje: depois de um
  "Não", a pergunta do Windows não volta naquela abertura; se a leitura falha sempre, nunca mais volta, e nenhuma
  versão chega. Depois: a pergunta volta a cada abertura, como depois de qualquer "Não". Também depois de um "Sim"
  (o programa não tem como saber, sem ler, que o "Sim" já foi dado; nunca uma anotação): o Kaique vê a pergunta a
  cada abertura, enquanto o Windows não deixar ler. As versões novas continuam chegando nesse caso, porque a abertura
  chama o ajudante de qualquer jeito (`ui/aviso_de_atualizacao.ligar_na_janela` → `procurar_ao_abrir`).
- **O registro da atualização** (`C:\ProgramData\EditorImpressao\atualizacao\`), que só o Samuel lê: passa a dizer o
  que o programa leu no Windows, e não o que ele supôs pela resposta. Ex.: um "Não" com as tarefas já no Windows (a
  segunda conta do Windows no mesmo notebook) hoje grava "o ajudante não foi criado; a pergunta volta" e "o que faltou
  o ajudante completa"; depois, grava que ele disse "Não", que as tarefas já estavam no Windows e que a pergunta não
  volta.
- **Licença do ajudante ilegível** (raro): hoje uma tarefa com o mesmo nome que rode outro programa passaria como
  "preparado" (a pergunta não voltaria e o programa chamaria outro programa). Depois: o programa, os argumentos e a
  conta são conferidos; tarefa errada → a pergunta volta e, no "Sim", a preparação refaz a tarefa certa.
- Testes novos (item 4): nada muda para quem usa.

### A causa, a regra e todos os caminhos (volta 3)

**Item 1. O Windows que não deixa ler.**
- Causa: na volta 2, o "não deu para saber" passou a não contar como falta para a pergunta não voltar depois do "Sim"
  (médio 3). Mas, sem uma anotação, "depois do Sim" e "depois do Não" têm a mesma leitura; então o "Não" com a leitura
  falhando também deixou de voltar.
- A regra, num lugar só: `o_que_falta_no_computador` (a leitura única). "Não deu para saber" (`existe is None`) volta a
  contar como falta, nas duas tarefas (ajudante e desfazer). "Existe, mas esta conta não lê" continua contando como
  existe.
- Caminhos (grep por `o_que_falta_no_computador`, `falta_a_pergunta_do_windows`, `preparar_na_primeira_abertura`,
  `preparar_ao_abrir`): a primeira abertura (`ui.primeira_vez_se_preciso` → `preparar_ao_abrir(primeira_vez=True)` →
  `preparar_na_primeira_abertura` → a leitura); as aberturas seguintes (`preparar_ao_abrir(primeira_vez=False)` → a
  leitura e, se falta, a pergunta); `falta_a_pergunta_do_windows` (chama a mesma leitura). Todos passam pela mesma
  função; nenhum tem conta própria.

**Item 2. O registro que diz o que não é.**
- Causa: as frases do registro sobre a consequência ("o ajudante não foi criado; a pergunta volta", "as tarefas estão
  no Windows; o que faltou o ajudante completa") são escolhidas pela resposta da pergunta ou por "nada falta?", antes ou
  sem olhar o que a leitura conferiu de verdade.
- A regra, num lugar só: a leitura única passa a devolver também o que ela não conseguiu conferir
  (`ler_o_computador` → o que falta e o que existe sem dar para conferir; `o_que_falta_no_computador` devolve só a
  primeira parte, como hoje). `preparar_na_primeira_abertura` anota a resposta só como fato ("disse Não", "não terminou
  bem") e escreve UMA frase de desfecho, tirada da leitura: falta → "não ficou preparado... a pergunta volta"; nada
  falta e tudo conferido com "Sim" → "o computador está preparado (lido no Windows)"; nada falta sem "Sim" → as tarefas
  já estavam no Windows (lidas agora) e a pergunta não volta; o que não deu para conferir fica dito. O ajudante só é
  chamado quando a leitura mostra que ele existe (já é assim com o item 1: "nada falta" só com o ajudante lido).
- Caminhos: só `preparar_na_primeira_abertura` escreve essas frases (grep por "primeira abertura:"); `preparar_ao_abrir`
  escreve a sua ("abrir o programa: falta preparar o computador") a partir da mesma leitura.

**Item 3. A licença ilegível pulava o resto.**
- Causa: o item 4 da volta 2 trocou a conferência própria pela da peça (`problemas_da_tarefa_criada`), que, sem a
  licença lida, acusaria "não deu para ler a licença"; para isso não trazer a pergunta de volta, o ramo da licença
  ilegível passou a não chamar a peça, e com isso também deixou de conferir o programa, os argumentos e a conta.
- **O que a conferência antiga cobria (D-827), antes de trocar:** volta 1 (conta própria): existe e foi lida; o
  comando (caminho normalizado); os argumentos; a conta (o sistema). Volta 2 (a peça): o mesmo (o comando pelo texto)
  e mais a licença "quem pode mandar rodar"; mas, com a licença ilegível, nada. **Volta 3:** com a licença lida, a peça
  inteira (como a volta 2); com a licença ilegível, a mesma peça confere o comando, os argumentos e a conta, e só a
  licença fica de fora (anotada). Cobre tudo o que a volta 1 cobria, em todos os casos.
- A regra, num lugar só: continua a peça, `core.windows.problemas_da_tarefa_criada`, sem mudar `core/windows.py`. Ela
  só confere a licença quando o desenho pedido tem uma (`if esperado["quem_pode"]`); com a licença ilegível, o
  programa lhe dá o desenho do ajudante sem a licença (o mesmo `xml_da_tarefa`, com a licença vazia). Nada de conta
  copiada nem de filtrar o texto do problema.
- Jeito mais simples (D-819) e por que este: um parâmetro "não confira a licença" na peça seria mais claro de ler, mas
  muda `core/windows.py` (a gerente pediu para parar antes); filtrar a frase "não deu para ler a licença" da lista da
  peça seria mais curto, mas depende do texto da frase (quebra calado se o texto mudar). O desenho sem a licença usa a
  regra que a peça já tem e não muda nada fora de `atualizacao.py`.
- Caminhos: só `o_que_falta_no_computador` (a leitura única) confere o ajudante lido; a criação (`criar_tarefa` e
  `core.windows.criar_tarefa`) não muda e continua pedindo a licença.

**Item 4. As proteções sem teste.** A lista do relatório 1 (M05 argumentos e conta do ajudante; M06 a tarefa desfazer;
M07 o Visual C++; M08 a instalação antiga; M27 o motor no teste rápido) e as que o relatório 2 diz que continuam sem
teste (M05, M27). Desde a volta 2, o Visual C++ e a instalação antiga não são lidos pela pergunta: a proteção que ficou
é "o ajudante completa os dois toda vez que roda" (`rodar_ao_ligar` → `preparar_o_computador`). Para cada uma: um teste
em que só ela falta, e a prova por mutação numa cópia minha (`git worktree add --detach`), com todas as mutações dos
relatórios 1 e 2 refeitas no código de agora (lista completa em "Cada proteção e o teste que a acusa (volta 3)").

### O que pode falhar e o que o programa faz (volta 3)

- O Windows não responde à leitura (PowerShell barrado, tempo esgotado): falta → a pergunta volta (D-826); o registro
  diz "não deu para ler ... no Windows (motivo)". Nunca "preparado" sem ler.
- O Windows responde "existe, mas esta conta não lê": conta como existe (a tarefa só nasce com licença de
  administrador); o registro diz que não deu para conferir o conteúdo.
- A licença do ajudante não vem: o programa, os argumentos e a conta são conferidos; o registro diz que a licença não
  foi conferida.
- A pergunta é respondida com "Não", "falhou" ou "Sim": a frase de desfecho vem da leitura feita depois; nunca uma
  consequência que a leitura não confirmou.
- Um erro inesperado na leitura ou na pergunta: como hoje, `preparar_ao_abrir` anota e conta como falta (a pergunta
  volta).
- Sem internet, sem licença, disco cheio, desligar no meio: nada disso é novo aqui (a leitura não usa a rede nem
  grava nada além do registro).

### O que li da peça de fora e onde (volta 3)

- Nenhuma peça de fora nova. Uso a peça única de sempre: `core.windows.ler_tarefa` (core/windows.py:1966: não existe
  → `existe=False`; acesso negado → `existe=True, lida=False`; qualquer outra resposta ou o PowerShell que não
  responde → `existe=None`) e `core.windows.problemas_da_tarefa_criada` (core/windows.py:2000: sem `existe`/`lida` →
  um problema; compara comando, argumentos e conta pelo texto; a licença só se o pedido tiver uma, e então "não deu
  para ler a licença" vira problema).

### O que foi feito (volta 3)

1. **Item 1** (`ce728693`): na leitura única (`o_que_falta_no_computador`), "não deu para saber" (o Windows não
   respondeu) volta a contar como falta, nas duas tarefas. Depois de um "Não", com a leitura falhando, a pergunta volta
   a cada abertura (D-826, D-741). "Existe, mas esta conta não lê" continua contando como existe.
2. **Item 2** (`ebd4197e`): a leitura única virou `ler_o_computador` (devolve o que falta e o que existe sem dar para
   conferir); `o_que_falta_no_computador` é a mesma regra de sempre em cima dela. `preparar_na_primeira_abertura`
   anota a resposta só como fato e escreve uma frase de desfecho tirada da leitura: "não ficou preparado... a pergunta
   volta" · "as tarefas existem, mas não deu para conferir tudo (...)" · "o computador está preparado (lido no
   Windows)" · "as tarefas já estão no Windows (lidas agora); a pergunta não volta". O ajudante só é chamado quando a
   leitura o mostra.
3. **Item 3** (`f15863b8`): com a licença do ajudante ilegível, a mesma peça (`problemas_da_tarefa_criada`) confere o
   comando, os argumentos e a conta, com o desenho do ajudante sem a licença (`xml_da_tarefa(exe, quem_pode="")`); só a
   licença fica dita como não conferida. `core/windows.py` não mudou.
4. **Item 4** (`126f01d0`): testes novos para as proteções que nenhum teste acusava; todas as mutações dos relatórios 1 e
   2 refeitas no código de agora, numa cópia minha (lista abaixo e `anexos/mutacoes-volta3.txt`).

### Arquivos criados ou alterados (volta 3)

- `atualizacao.py` (itens 1 a 3: `ler_o_computador`, `o_que_falta_no_computador`, `preparar_na_primeira_abertura`,
  `preparar_ao_abrir` (só a docstring), `xml_da_tarefa`)
- `tests/test_atualizador_4.py` (os testes dos itens 1 a 4; dois testes meus da volta 2 mudaram, item 1)
- `relatorios/atualizador-4/ONDE-PAREI.md` e `relatorios/atualizador-4/anexos/` (as provas)
- Nenhum outro: `core/windows.py`, `core/ocr_kraken.py`, `ui/testes_a_distancia_ui.py`, `configuracoes.py` e os 16
  testes antigos não mudaram.

### Como cumpri cada uma (volta 3)

- **D-826 (1), o caso raro:** com o Windows sem deixar ler as tarefas, a pergunta volta a cada abertura, depois do
  "Não" e depois do "Sim" (`tests/test_atualizador_4.py::test_volta3_item1_depois_do_nao_com_o_windows_que_nunca_deixa_ler_a_pergunta_volta_a_cada_abertura`,
  `tests/test_atualizador_4.py::test_volta3_item1_depois_do_sim_com_o_windows_que_nao_deixa_ler_a_pergunta_volta`).
  Falham no código de antes (`anexos/reversao-volta3-item1.txt`).
- **D-826 (1), o Visual C++ e a instalação antiga:** não mudou: a pergunta não volta por eles
  (`tests/test_atualizador_4.py::test_volta2_medio3_visual_c_mais_novo_numa_versao_nova_nao_traz_a_pergunta_de_volta`)
  e o ajudante os completa toda vez que roda, antes de procurar
  (`tests/test_atualizador_4.py::test_volta3_m07_m08_o_ajudante_completa_o_visual_c_e_a_instalacao_antiga_toda_vez_que_roda`).
  As tarefas não prontas trazem a pergunta (D-749:
  `tests/test_decisoes_preparo_d749.py::test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta`).
- **D-826 (2), o registro:** `tests/test_atualizador_4.py::test_volta3_item2_sem_sim_o_registro_diz_o_que_a_leitura_mostrou`,
  `tests/test_atualizador_4.py::test_volta3_item2_o_que_nao_deu_para_conferir_fica_dito_e_nada_e_dado_como_preparado`
  (falham no código de antes: `anexos/reversao-volta3-item2.txt`).
- **D-826 (2), a licença ilegível:** `tests/test_atualizador_4.py::test_volta3_item3_com_a_licenca_ilegivel_o_resto_do_ajudante_ainda_e_conferido`
  (o programa, os argumentos e a conta; falha no código de antes: `anexos/reversao-volta3-item3.txt`).
- **D-826 (2) e D-827, as proteções sem teste:** 60 proteções desligadas numa cópia, 60 acusadas (lista abaixo;
  `anexos/mutacoes-volta3.txt`). Antes dos testes novos, 3 não eram acusadas (M27, M07/M08, M06 do lado de quem cria).
- **D-827, a troca de conferência:** a única troca é a do item 3, e a lista do que a antiga cobria está escrita antes
  dela (em "A causa, a regra e todos os caminhos (volta 3)", item 3, e no comentário do código). A nova cobre tudo o
  que a da volta 1 cobria, com teste.
- **D-741:** "Não" → a pergunta volta (`tests/test_atualizador_4.py::test_volta2_medio3_depois_do_nao_a_pergunta_continua_voltando`);
  "Sim" → não volta (`tests/test_decisoes_ajudante_da_atualizacao.py::test_d741_nao_a_pergunta_volta_na_proxima_abertura_e_sim_ela_nao_volta_mais`).
- **D-733/D-735:** uma pergunta só, pela peça única (`tests/test_atualizador_4.py::test_conserto1_a_pergunta_vai_pela_peca_unica_com_um_passo_so`).
- **D-767:** só o Windows de mentira nos testes; nada pediu licença, nada abriu janela na tela do Samuel; nenhuma
  mutação tirou a recusa de perguntar sob o pytest.
- **D-811:** a lista "proteção → teste" abaixo, provada por mutação numa cópia (`git worktree add --detach` no meu
  rascunho, tirada no fim; nada mais foi apagado).
- **D-824:** um commit por item, com push (`ce728693`, `ebd4197e`, `f15863b8`, `126f01d0`).
- **D-825:** nenhum dos 16 testes antigos mudou nesta volta (o `git diff` da volta 3 mexe só em `atualizacao.py`,
  `tests/test_atualizador_4.py` e no relatório); dos meus testes, só os dois do item 1 (são deste trabalho).
- **D-815:** sou o escritor da volta 3, agente novo.
- **Nenhuma frase nova na tela:** os textos novos vão só para o registro da atualização.

### Cada proteção e o teste que a acusa (volta 3)

Cada uma desligada numa cópia minha, sozinha; os arquivos de teste rodados um por vez (o script:
`anexos/mutar3.py.txt`; os resultados: `anexos/mutacoes-volta3.txt`). Os nomes M.. e V.. são os dos relatórios 1 e 2
de quem tentou quebrar.

Está na seção "Cada proteção e o teste que falha sem ela", acima (os itens P01 a P71, 60 de 60 acusadas). Antes dos testes novos desta volta, 55 de 58 (as 3 que faltavam: P48 = M27, P60 = M07/M08, P67 = M06 do lado de quem cria); P70 e P71 foram acrescentadas depois e são acusadas.

### Caminho e função (volta 3)

- "A pergunta volta?" em todos os caminhos (primeira abertura, aberturas seguintes, `falta_a_pergunta_do_windows`) →
  `o_que_falta_no_computador` → `ler_o_computador` (a leitura única) → `core.windows.ler_tarefa` e
  `core.windows.problemas_da_tarefa_criada`.
- A frase de desfecho do registro na pergunta → `preparar_na_primeira_abertura` → `ler_o_computador` (a mesma leitura).
- O ajudante lido com a licença ilegível → `ler_o_computador` → a mesma peça, com `xml_da_tarefa(exe, quem_pode="")`.
- Criar o ajudante (dentro da pergunta) → `criar_tarefa` → `xml_da_tarefa(exe)` (a licença de fábrica; não mudou).
- As provas que cobram o mesmo resultado pelos caminhos: a leitura que falha traz a pergunta pela primeira abertura e
  pelas seguintes (`tests/test_atualizador_4.py::test_volta3_item1_depois_do_nao_com_o_windows_que_nunca_deixa_ler_a_pergunta_volta_a_cada_abertura`)
  e pela regra direta (`tests/test_atualizador_4.py::test_conserto1_nao_deu_para_ler_o_ajudante_conta_como_falta`).

### Testes (volta 3)

- No PC, um arquivo por vez: `tests/test_atualizador_4.py` 57 passaram; `tests/test_decisoes_ajudante_da_atualizacao.py`
  37; `tests/test_decisoes_preparo_d749.py` 9; `tests/test_decisoes_atualizacao.py` 38;
  `tests/test_decisoes_testes_a_distancia.py` 13; `tests/test_windows_peca.py` 69 (2 pulados, como antes, pelo ambiente).
  Porteiro: "nada novo", 168 lugares; tabela: 0 arquivos sem linha.
- Reversão: os testes de cada item falham no código de antes dele, por comportamento
  (`anexos/reversao-volta3-item1.txt` a `-item3.txt`).
- Mutações: 60 de 60 acusadas (acima).
- GitHub: rodada 44992797990: success na 1ª tentativa (a 44991980992 foi cancelada por mim: testava o commit antes das docstrings dos testes).

### Ressalvas (volta 3)

- **O "Sim" com a leitura falhando sempre** (D-826 aceitou): a pergunta volta a cada abertura, mesmo depois do "Sim".
  Logo depois desse "Sim" o ajudante não é chamado na hora (a leitura não o mostra); as versões chegam assim mesmo,
  porque cada abertura chama o ajudante (`ui/aviso_de_atualizacao.ligar_na_janela`).
- **"Existe, mas esta conta não lê" (acesso negado) continua contando como existe**, sem conferir o conteúdo: uma
  tarefa com o mesmo nome, na pasta do programa no Agendador, que rodasse outra coisa passaria. Só o administrador cria
  tarefas ali, e a peça confere essa pasta ao criar. Fica dito no registro ("existe, mas não deu para ler o que ele
  faz"). Não mudei porque o pedido manteve esse caso e a D-826 fala só do "não deixa ler".
- **O item 3 depende de uma regra da peça:** ela só confere a licença quando o desenho pedido tem uma. Se essa regra
  mudar em `core/windows.py`, a licença ilegível voltaria a trazer a pergunta; os testes do item 3 e do item 4 da volta
  2 acusariam (o primeiro caso do teste do item 3 cobra "a tarefa certa sem a licença lida não falta").
- **O registro ganha uma linha** a cada abertura em que algo existe sem dar para conferir ("...; não pergunto de novo
  por isso"); já era assim com a licença ilegível.
- Os testes são de lógica, com o Windows de mentira (D-767). A prova que vale é a sessão à vista; o roteiro do
  relatório 2 continua valendo, e o passo 2 dele ("Não pode aparecer 'não deu para ler o ajudante' nem 'não deu para
  ler a licença'") ganhou uma terceira frase a procurar: "existe, mas não deu para ler o que ele faz".
- No PC rodei só os arquivos ligados a este trabalho, um por vez (pouca memória); as provas de todas as decisões
  (`tests/test_decisoes*.py`) e o resto rodam no GitHub.
- O formulário do programa ainda acusa "O print que prova" sem .png: nenhuma tela mudou e eu não abro janela na tela do
  Samuel (como na volta 1).

### Ideias e bugs (volta 3)

- **Bug (22/11, não impede):** `tests/test_atualizador_4.py` tem 4 docstrings com barra invertida de caminho do
  Windows (`\c`, `\m`, `\.`; linhas 429, 452, 565 e 597 de hoje, escritas nas voltas 1 e 2) que o Python 3.14 avisa
  como "SyntaxWarning: invalid escape sequence" (aparece ao rodar o porteiro); numa versão futura do Python vira erro e o
  arquivo não carrega. Conserto: docstrings com `r"""`. Sem print (é aviso de texto).
- **Ideia:** um parâmetro "conferir a licença" em `core.windows.problemas_da_tarefa_criada` diria a intenção do item 3
  com mais clareza que o desenho sem a licença (muda `core/windows.py`; a gerente decide).
- **Ideia:** o script de mutações (`anexos/mutar3.py.txt`) como ferramenta fixa do pacote de regras, para quem escreve
  rodar antes de entregar (D-811, D-827).

### Perguntas para o Samuel (volta 3)

Nenhuma. A D-826 e a D-827 responderam o que esta volta precisava.

### Commit (volta 3)

- Plano `1e8518cf`; item 1 `ce728693`; item 2 `ebd4197e`; item 3 `f15863b8`; item 4 `126f01d0`; docstrings das peças de mentira
  dos testes novos `b897efb7` (último do código e dos testes; K12 do formulário). Depois só o ONDE-PAREI.
- GitHub: 44992797990: success na 1ª tentativa (a 44991980992 foi cancelada por mim: testava o commit antes das docstrings dos testes).

### Resumo (volta 3)

1. O caso raro voltou ao que o Samuel decidiu: se o Windows não deixa ler as tarefas, a pergunta volta a cada abertura.
2. O registro diz o que o programa leu no Windows, não o que supôs pela resposta; o ajudante só é chamado se o Windows o
   mostra.
3. Com a licença do ajudante ilegível, o programa, os argumentos e a conta da tarefa continuam conferidos (só a licença
   fica de fora).
4. 60 proteções desligadas uma a uma numa cópia: 60 acusadas por algum teste (3 só depois dos testes novos desta volta).
5. Tudo em `atualizacao.py` e `tests/test_atualizador_4.py`; `core/windows.py`, a tela e os 16 testes antigos não mudaram.
6. Nenhuma frase nova na tela; nada pediu licença nem abriu janela.
7. Ressalvas principais: o "Sim" com a leitura falhando sempre faz a pergunta voltar a cada abertura (aceito na D-826);
   "existe, mas não lê" continua contando como existe, sem conferir o conteúdo.

## Volta 4 (22/11/2026, escritor novo; D-828)

Escritor novo da volta 4 (D-815). Pedido da gerente: os 3 defeitos da prova à vista de 22/11 (D-828), pela causa,
num lugar só, um de cada vez, com commit e push em cada um. Antes do código, este plano; paro e devolvo à gerente.

### Onde parei (volta 4)

- 22/11, tarde: leitura feita (o meu arquivo de agente; CLAUDE.md §11.8, §11.12 com os 6 pontos, §11.13; memória:
  índice e `geral/atualizador.md` do `fase-1`; este ONDE-PAREI inteiro; os relatórios 1 e 2 de quem tentou quebrar; as
  decisões D-718, D-719, D-731, D-733, D-735, D-741, D-749, D-767, D-770, D-774, D-779, D-806, D-811, D-819, D-824 a
  D-828; a Lista de bugs de 22/11; os três registros da prova; o código do Velopack 1.2.161 que usamos).
- Experimentos no PC, sem licença e sem janela (`anexos/volta4-experimentos.txt` e os scripts `anexos/volta4-exp*.py.txt`).
- Plano abaixo. **Parado, esperando a gerente** (ela confere e manda seguir). Há 4 pontos para ela decidir
  (em "Para a gerente decidir (volta 4)").

### Decisões que esta tarefa precisa cumprir (volta 4)

- **D-828** "foi eu, pode consertar essas coisas": (1) o "Reiniciar agora" troca de verdade; o programa garante que
  terminou de fechar antes de a troca começar; abrir pelo atalho no meio da troca não estraga a troca; (2) a pergunta
  do Windows da primeira abertura vem no meio da tela; (3) refazer a preparação (depois de uma que falhou, ou ao
  reinstalar) dá certo. Nenhuma frase nova na tela sem o "sim" dele.
- **D-806** "então pode ser opção A": a licença é pedida com a janela do programa na frente, para vir no meio da tela;
  nada de aviso novo ("clique no escudo piscando" não foi escolhido).
- **D-770** "a": a janelinha em toda troca fica para depois (o pedido: nada de frase nova agora).
- **D-733** "1- sim / VAI CONSEGUIR FAZER OS TESTS A DISTANCIA NÉ?", **D-735** "Sim", **D-741** "Sim": uma pergunta
  do Windows na primeira abertura; depois do "Não", volta a cada abertura; depois do "Sim", nunca mais.
- **D-749** "Sim" (ajustada pela **D-826**): a preparação que falha no meio conta como não feita.
- **D-731** "ok": a tarefa "desfazer" existe sempre e desfaz o que o programa pôs; os projetos do Kaique nunca.
- **D-718** "Sim, e tem que avisar a gente de alguma maneira", **D-719** "1": a volta e a frase da falha não mudam.
- **D-767** "não faça mais nada escodindo ou de mentira": os testes daqui provam só a lógica; o que eu puder provar no
  Windows de verdade sem licença e sem janela, provo (os experimentos); a prova que vale é a sessão à vista.
- **D-774** "ok": os testes antigos que cobram o jeito errado mudam para o certo (entre eles "o do lugar da pasta
  `C:\ProgramData\EditorImpressao\testes-a-distancia`" e "os dois da tranca da pasta `/inheritance:r`, `/setowner`").
- **D-779** "ta vamos continuar com ele, mas o que fazemos para ele não dar defeito...": o Velopack 1.2.161 fica.
- **D-811** "ok" e **D-827**: cada proteção nova com o teste que a acusa desligada; toda conferência trocada, antes a
  lista do que a antiga cobria.
- **D-819** "nova regra, sempre se deve se ver se é a coisa mais simples, ou melhor de se fazer": cada item abaixo diz
  o jeito mais simples e por que foi escolhido (ou não).
- **D-824** "vamos fazer com um só, uma coisa de cade vez.": um conserto por commit, nesta ordem.
- **D-825** "ok": dos testes antigos, só os 16 da lista (e os da D-774) podem mudar.
- **D-605** (CLAUDE.md §11.8): o novo não estraga o que já está escolhido e testado.

### O que já está escolhido e testado aqui (volta 4)

- Testes que já existem para o que vou tocar: `tests/test_atualizador_4.py` (57), `tests/test_decisoes_ajudante_da_atualizacao.py`
  (37; entre eles a janelinha D-742 "letra por letra", o texto do script da troca e a ordem Wait-Process < schtasks <
  Start-Process), `tests/test_decisoes_atualizacao.py` (38), `tests/test_decisoes_preparo_d749.py` (9),
  `tests/test_decisoes_testes_a_distancia.py` (13), `tests/test_decisoes_desinstalar.py` e `_pasta.py` (a tarefa
  desfazer, o caderninho, a tranca), `tests/test_decisoes_brasao.py` (D-748: o brasão e a janelinha nunca juntos),
  `tests/test_windows_peca.py` (o lançar solto, trazer para a frente, a pasta segura), `tests/test_conferencias_*.py`
  (o porteiro e a lista de exceções: só diminui; item novo só com o "sim" do Samuel).
- O que não muda: o texto e a ordem do script da troca (só ganha a marca no começo e o lugar de onde reabre, ver o
  item 1); a janelinha D-742 e a regra D-748; a frase da falha; a assinatura antes de baixar; nenhuma pergunta do
  Windows por atualização; o "Não"/"Sim" lidos como estão (provados à vista em 22/11); o motor no lugar dele.

### Como fica para quem usa e no livro (volta 4)

O livro (o PDF) não muda: nada aqui mexe nas páginas. Nenhuma frase nova na tela.
- **"Reiniciar agora"** (hoje: o programa fecha, a troca desiste e o programa volta na versão velha com o aviso "A
  atualização não deu certo"). Depois: o programa fecha, a troca acontece por trás (alguns minutos, sem nada na tela,
  como hoje), e o programa volta sozinho na versão nova.
- **O Kaique clica no atalho no meio da troca** (hoje: o programa abre na versão velha e estraga a troca). Depois:
  o clique não abre nada naquele momento (o programa sai sozinho, em silêncio, antes do brasão); quando a troca
  termina, o programa abre sozinho, como no "Reiniciar agora". Ele pode clicar quantas vezes quiser: nada estraga.
  (Sem frase na tela: a janelinha "Atualizando" é a D-770, para depois.)
- **"Depois" e abrir de novo**: igual ao de cima, com a janelinha D-742 que já existe.
- **A pergunta do Windows** (hoje: pisca na barra de tarefas quando a janela do programa não está na frente). Depois:
  ela só é feita quando a janela do programa está na frente; se o Kaique estiver noutra janela, ela espera, sem aviso,
  e aparece no meio da tela no instante em que ele volta ao programa (um clique na janela ou no botão da barra).
- **Refazer a preparação** (hoje: a segunda vez falha com "acesso negado" e a pergunta volta em toda abertura).
  Depois: dá certo quantas vezes for refeita; as contas comuns continuam só lendo a pasta.

### A causa, a regra e todos os caminhos (volta 4)

**Item 1. A troca do "Reiniciar agora".**
- **Causa, lida nos registros e provada num experimento.** O que o Velopack fez (registro do sistema): esperou o
  ajudante (pid 5648) sair; extraiu a versão nova (9 s); rodou o gancho `--veloapp-obsolete` (0,6 s, esperou ele
  terminar); fechou à força tudo o que roda de dentro da raiz (às 14:34:56 achou só ele mesmo); tentou renomear
  `current` 10 vezes, de 14:34:56 a 14:35:05, com o erro 32 ("O arquivo já está sendo usado por outro processo"), e
  desistiu. Às 14:34:56 nenhum programa nosso rodava de dentro da raiz, e o Samuel só clicou às 14:34:58. Quem
  segurava a pasta era **o PowerShell da troca** (lançado às 14:34:19 pelo "Reiniciar agora", vivo até reabrir o
  programa): ele mora no System32 (o Velopack não o fecha), mas nasceu com a **pasta de trabalho** do programa, que é
  `current` (o Velopack abre o programa com `current` como pasta de trabalho; a peça lança o solto sem dizer a pasta,
  e o Windows dá ao filho a pasta de quem lançou). Uma pasta que é a pasta de trabalho de um processo não pode ser
  renomeada: no PC, um PowerShell com a pasta de trabalho dentro dela dá exatamente o erro 32; com o System32, renomeia
  (`anexos/volta4-experimentos.txt`, exp1; com a peça de verdade, exp1b). O clique do Samuel às 14:34:58 abriu o
  programa de `current` no meio das tentativas: segurava também, mas não foi o primeiro.
- **O "Acesso negado" do WaitPid não é a causa.** O Velopack abre o processo só com a licença de esperar, espera, e
  depois pede o código de saída, que essa licença não dá: "acesso negado" DEPOIS de o processo ter saído (exp2 no PC
  dá o mesmo: a espera volta 0, o código de saída dá erro 5). A espera funcionou (1 s, o ajudante saindo).
- **A regra, num lugar só:**
  1. **Na peça** (`core/windows._lancar_solto`, o único lançar solto): todo processo lançado solto nasce com a pasta
     de trabalho na pasta do Windows (`pasta_do_sistema()`), nunca na de quem lançou. Motivo: ele continua depois de
     quem chamou, e não pode prender a pasta dele. O script da troca, antes de reabrir o programa, faz
     `Set-Location` para a pasta do programa: o programa reaberto nasce com a mesma pasta de trabalho de quando o
     Velopack o abre (o `Set-Location` não prende a pasta: exp4). Nenhuma linha que o porteiro conhece muda de texto.
  2. **"O programa está aberto?" passa a ser conferido de verdade** (`atualizacao.ha_programa_aberto`, o lugar único
     que o ajudante usa antes de trocar): além da marca da janela, a peça lê no Windows os processos cujo programa está
     dentro de `current` (função nova na peça, `programas_rodando_de(pasta)`: a lista de processos do Windows e o
     caminho de cada um). Sem a marca mas com algo ainda rodando de `current` (o programa terminando de fechar, um
     clique no atalho), o ajudante espera até 30 s; se continuar, não troca (fica "pendente", o registro diz o que
     roda) e o script reabre o programa como hoje. "Não deu para ler a lista" conta como "aberto" (não troca).
  3. **Abrir no meio da troca**: o script da troca segura, do começo ao fim, uma marca nova
     (`Local\EditorImpressao-trocando`, um "mutex" do Windows, que some sozinho quando o script termina, até se ele
     cair). Na abertura comum (`atender_linha_de_comando`, antes do brasão e da janela; nunca nos modos escondidos, nos
     ganchos do Velopack nem no `--depois-da-troca`), se a marca existe, o programa sai em silêncio: o script o reabre
     quando a troca acaba. A marca nasce na primeira linha do script, antes de a peça ver o sinal de vida, então
     existe antes de o programa que pediu a troca sair.
- **Todos os caminhos** (grep por `lancar_powershell_solto`, `_lancar_solto`, `ha_programa_aberto`,
  `programa_aberto`, `trocar_e_reabrir`, `atender_linha_de_comando`): o lançar solto: o script da troca
  (`_lancar_pela_peca`, "Reiniciar agora" e "Depois") e a janela de prova (`janela_de_prova.prova_lancar_solto`): os
  dois passam a lançar com a pasta do Windows. "Está aberto?": só o ajudante (`rodar_ao_ligar` →
  `procurar_e_preparar(..., ha_programa_aberto)`), chamado pela abertura, pelo script da troca e de longe; todos pela
  mesma função. "Troca em andamento?": uma função nova, `troca_em_andamento()`, usada só pela abertura comum.
- **Jeito mais simples (D-819) e por que não.** (a) Uma linha no começo do script mudando a pasta de trabalho dele
  (`SetCurrentDirectory`): resolve só este script e deixa a peça prendendo a pasta de quem lança em todo outro uso
  (é o "consertar só onde apareceu" do §11.12); escolhido o da peça. (b) Usar a tranca do próprio Velopack
  (`packages\.velopack_lock`) como sinal de "trocando": lido no código, o Velopack a segura também enquanto BAIXA
  (`manager.rs`, `download_updates`): o clique no atalho seria engolido durante todo o download (minutos). Descartado.
  (c) Não conferir os processos e deixar o Velopack fechar à força o que achar: fecharia o programa do Kaique no meio
  de gravar; o pedido manda conferir de verdade.
- **O que fica de fora, e é ressalva:** a troca que o ajudante faz SEM o script (o Kaique abre e fecha o programa
  enquanto a versão nova baixa; ou o Samuel manda de longe): não há script segurando a marca; se o Kaique abrir o
  programa nos ~20 s críticos dessa troca, o Velopack o fecha à força ou a troca falha, como hoje. Ver "Para a gerente
  decidir", ponto 4.

**Item 2. A pergunta do Windows piscando.**
- **Causa (lida no código e nos registros; o Windows não deixa provar sem abrir janela, fica para a sessão à vista).**
  Nas duas vezes era uma abertura seguinte (depois do "Não"): o clique no atalho foi às 14:02:33 e 14:24:56, e o
  pedido saiu 17 a 20 s depois (14:02:50 e 14:25:16): o programa primeiro carrega tudo e monta a janela, depois lê o
  Windows e pergunta. A regra do Windows: o programa aberto por um clique ganha o direito de vir para a frente (o
  atalho do Velopack passa esse direito adiante: `stub.rs` e `start_windows_impl.rs`, `AllowSetForegroundWindow`), mas
  perde esse direito "na próxima vez que a pessoa mexer em outra coisa" (documentação de `AllowSetForegroundWindow`).
  Nesses 17 a 20 s nada nosso fica na frente (o brasão aparece de propósito sem tomar a frente,
  `WA_ShowWithoutActivating`), então qualquer clique ou tecla noutra janela tira o direito; a janela aparece sem vir
  para a frente, a peça tenta trazê-la, o Windows recusa (o registro diz "não estava na frente") e a pergunta vai para
  a barra. Na primeira abertura com a janela da senha isso não acontece: o "Agora não" é um clique na nossa janela.
- **A regra, num lugar só:** a pergunta da primeira abertura (`atualizacao.preparar_na_primeira_abertura`, o único
  pedido de licença do atualizador) só sai com uma janela do programa na frente. Antes de perguntar: uma tentativa de
  trazer a janela (como hoje); se o Windows não deixar, espera em silêncio, lendo a cada 0,3 s qual janela está na
  frente (leitura nova na peça, `janela_do_programa_na_frente(janela)`: a da frente, se for a janela do programa ou um
  aviso dela), e pergunta no instante em que ela vier para a frente (o clique do Kaique de volta no programa), com a
  janela da frente como dona. Se a janela fechar antes, não pergunta (a próxima abertura lê o Windows e pergunta de
  novo, D-741). Sem limite de tempo: o fio de trás é solto e morre com o programa.
- **Caminhos:** a primeira abertura com a senha ou "Agora não" e as aberturas seguintes passam todas por
  `preparar_ao_abrir` → `preparar_na_primeira_abertura` (grep por `pedir_licenca_ao_windows`: não há outro). O pedido
  dos testes à distância (Configurações) não passa por aqui (passo 4).
- **Jeito mais simples (D-819):** perguntar logo no começo, antes de carregar (o clique ainda vale): a pergunta
  sairia sem janela nossa na frente (o brasão não toma a frente) e antes de saber se precisa (a leitura leva 0,5 a 7 s);
  ou fazer o brasão tomar a frente e passá-la à janela: mexe em `ui/` (fora do pedido) e ainda falha se o Kaique
  clicar noutra janela durante o carregamento. Forçar a janela para a frente com truques do Windows: é contra a regra
  do Windows e seria gambiarra. Escolhido esperar a janela vir para a frente: é o que a D-806 pede ("enquanto a janela
  do programa ainda está na frente") sem aviso novo. Ver "Para a gerente decidir", ponto 2.

**Item 3. A pasta trancada na segunda preparação.**
- **Causa (provada em 18/11, Lista de bugs "Causa provada da tranca"; o registro de 22/11 mostra o mesmo):** o
  `icacls ... /inheritance:r /grant:r ...(OI)(CI)... /T` passa também nos arquivos que já estão na pasta e os deixa
  com a lista de licenças vazia. Na primeira preparação a pasta estava vazia; na segunda, o `desfazer.ps1` da primeira
  ficou sem licença nenhuma e o `WriteAllText` deu "acesso negado".
- **O porteiro:** o `icacls`, o `/inheritance` e o `/setowner` são barrados em todo arquivo do programa, até na peça
  (K01 e K03: "comando de licença de pasta à mão"); as duas linhas de hoje só passam por estarem na lista de exceções,
  pelo texto exato, com o motivo "os testes à distância passam a usar a peça única e a pasta segura". Mudar o texto
  delas (ou pôr outra) é item novo na lista, e item novo só com o "sim" do Samuel.
- **Duas saídas (ver "Para a gerente decidir", ponto 3):**
  - **A (a mais simples no código, mesma pasta do ProgramData):** o `/grant` só na pasta (sem `/T`; os arquivos
    passam a herdar dela), um `/reset` nos arquivos que já estão dentro (conserta os que a versão de antes trancou),
    cada `icacls` com o código conferido (hoje só o último), e depois a leitura das licenças pela peça. Precisa de 2 a 3
    itens novos na lista do porteiro (o "sim" do Samuel) e continua sendo licença à mão, que o plano tira.
  - **B (a sugerida; a do plano, peça 2, e a que a D-774 previu):** a pasta dos testes à distância passa a ser a pasta
    segura da peça (`C:\Program Files\EditorImpressaoAjudante`, `core.windows.pasta_segura()`), que herda as licenças
    de fábrica de Arquivos de Programas (lidas no PC: o sistema e os administradores gravam; os Usuários só leem e
    executam). Nenhum comando de licença: nada mais tranca nada, então refazer a preparação (ou reinstalar) sempre
    regrava o `desfazer.ps1`. As 2 linhas do `icacls` e os 4 itens delas saem da lista do porteiro (a lista diminui).
    Depois de preparar, o programa lê as licenças de verdade (`core.windows.conferir_pasta_segura`, a conferência que
    já existe: dono, quem grava, quem lê, não é atalho); se não conferir, a preparação dá "falhou" (D-749). O que muda
    em `core/testes_a_distancia.py`: `PASTA_DOS_TESTES` vira a pasta segura (lida na hora, para não carregar a peça em
    toda abertura do programa); `_comando_proteger_a_pasta` sai; `_comando_criar_e_proteger_a_pasta` vira só "criar
    a pasta, se falta"; o `_comando_anotar_o_antes` do ligar perde o pedaço do `icacls` (a mesma regra, D-667); o
    `preparar_o_desfazer` confere a pasta depois. O XML da tarefa desfazer passa a apontar para o script na pasta
    nova. Os 3 testes antigos que a D-774 nomeou mudam: `test_d731_o_caderninho_fica_onde_o_plano_diz` (o lugar),
    a linha do `icacls` em `test_d731_ligar_anota_o_antes_primeiro_e_so_na_primeira_vez` e
    `test_d731a_a_pasta_do_desfazer_fica_protegida` (a tranca). Nenhum outro.
- **O que B deixa de lado (ressalva):** no computador que já ligou os testes pela versão de antes (só o PC do Samuel,
  na etapa 5), o caderninho velho fica no ProgramData e o desfazer novo não o vê (o OpenSSH daquela vez não seria
  tirado ao desinstalar). No notebook do Kaique nunca houve. A pasta velha do ProgramData fica (a limpeza é do passo 5).

### O que pode falhar e o que o programa faz (volta 4)

Item 1:
- A pasta do Windows não é achada (a peça não sabe onde fica): o lançar solto diz "falhou" (como hoje com o disco
  cheio); "Reiniciar agora" fecha gravado e a versão entra na próxima abertura (D-734).
- A lista de processos não é lida (o Windows nega, erro inesperado): conta como "aberto"; não troca; registro.
- Um processo nosso não deixa ler o caminho: conta como nosso se o nome do programa é o de um programa de `current`.
- Ainda roda algo de `current` depois de 30 s (um processo preso): não troca; o registro diz qual; o script reabre o
  programa na versão de hoje; o aviso de versão nova volta.
- Outro programa de fora segura a pasta (antivírus, o Explorador aberto em `current`): o Velopack tenta 10 vezes; se
  não der, a troca falha como hoje (D-718). Não dá para conferir antes (o Windows não diz quem segura uma pasta).
- O script cai no meio: a marca some sozinha (o Windows a apaga com o processo); a próxima abertura abre normal.
- A marca não é lida (erro do Windows): a abertura segue normal (como hoje), nunca fica sem abrir.
- O script passa do limite (até ~20 min, os limites de hoje): o clique no atalho fica sem abrir nada até lá (sem
  frase na tela, D-770 para depois). Ressalva.
- Sem internet, sem licença, disco cheio: nada novo (a troca usa o pacote já baixado; nada aqui pede licença).

Item 2:
- A janela nunca volta para a frente: nada é perguntado nesta abertura; a próxima pergunta de novo (D-741). Registro.
- A janela fecha antes: não pergunta; registro.
- O Kaique está num aviso nosso (uma caixa do programa): conta como "na frente"; a dona da pergunta é o aviso.
- A leitura da janela da frente falha: conta como "não está na frente" e espera (nunca pergunta para piscar).
- "Não", "Sim", ninguém responde: como hoje (provados à vista em 22/11).

Item 3 (saída B):
- A pasta segura não existe e não dá para criar (sem licença, disco cheio): o passo falha; "falhou"; a pergunta volta.
- A pasta segura existe mas não confere (alguém mudou as licenças, é um atalho): a preparação dá "falhou" e o
  registro diz o que não confere; não grava nada nela.
- O `desfazer.ps1` preso por outro programa: o passo falha; "falhou"; a pergunta volta (as tarefas, D-826).
- Desinstalar: a tarefa desfazer roda o script da pasta nova (igual a hoje, no lugar novo).

### O que li da peça de fora e onde (volta 4)

- **Velopack 1.2.161, a troca** (https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/commands/apply_windows_impl.rs):
  extrai, roda o gancho `--veloapp-obsolete` (espera até 15 s), `force_stop_package(root)`, depois
  `retry_io_ex(|| fs::rename(&current_dir, &temp_path_old), 1000, 10)` com a mensagem "Unable to start the update,
  because one or more running processes prevented it"; com `restart`, reabre a versão de antes se falhar (`apply.rs`).
- **Velopack, o fechar à força** (`src/bins/src/shared/util_windows.rs`, `get_processes_running_in_directory`): só os
  processos cujo programa está dentro da raiz, abertos com `PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_TERMINATE`;
  os que não abrem são pulados; ele mesmo é pulado. O PowerShell (System32) nunca é fechado.
- **Velopack, a espera do WaitPid** (`src/lib-rust/src/process_win.rs`, `wait_for_pid_to_exit`): `OpenProcess(PROCESS_SYNCHRONIZE)`,
  `WaitForSingleObject`, depois `GetExitCodeProcess`, que precisa de outra licença: "acesso negado" depois da espera
  (exp2). `operation_wait` só avisa e segue (`src/bins/src/shared/util_common.rs`).
- **Velopack, a tranca dele** (`src/lib-rust/src/locator.rs`, `try_get_exclusive_lock`; `lockfile.rs`, `share_mode(0)`):
  `packages\.velopack_lock`, segurada na troca E no `download_updates` (`manager.rs:406`). Por isso não serve de sinal.
- **Velopack, o atalho** (`src/bins/src/stub.rs:39-41`; `start_windows_impl.rs`, `start_regular`): abre o Update.exe e
  o programa com `AllowSetForegroundWindow` e com `current` como pasta de trabalho (`cmd.current_dir(&current)`).
- **Windows, a pasta de trabalho do filho:** "If this parameter is NULL, the new process will have the same current
  drive and directory as the calling process" (CreateProcessW, `lpCurrentDirectory`,
  https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw); o
  `subprocess.Popen(cwd=...)` do Python é esse parâmetro (https://docs.python.org/3/library/subprocess.html#popen-constructor).
  Que a pasta de trabalho impede renomear: provado no PC (exp1, exp1b), erro 32.
- **PowerShell 5.1:** `Start-Process` sem `-WorkingDirectory` abre o programa na localização atual do PowerShell
  (exp3); `Set-Location` muda só essa localização, não prende a pasta (exp4)
  (https://learn.microsoft.com/powershell/module/microsoft.powershell.management/start-process?view=powershell-5.1).
- **Windows, a marca com nome (mutex):** "The system closes the handle automatically when the process terminates. The
  mutex object is destroyed when its last handle has been closed" (CreateMutexW,
  https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createmutexw); `Local\` é a sessão do
  usuário (https://learn.microsoft.com/en-us/windows/win32/termserv/kernel-object-namespaces). O .NET
  `System.Threading.Mutex(bool, string)` cria ou abre a de mesmo nome (o script da janelinha já usa).
- **Windows, a lista de processos:** `CreateToolhelp32Snapshot` + `Process32FirstW/NextW` dão o número e o nome de
  todos os processos sem abrir nenhum; `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` + `QueryFullProcessImageNameW`
  dão o caminho (https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot,
  https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-queryfullprocessimagenamew). Como o sistema
  (o ajudante), abre os processos da conta do Kaique.
- **Windows, a frente:** `AllowSetForegroundWindow`: "the process specified by dwProcessId loses the ability to set
  the foreground window the next time the user generates input, unless the input is directed at that process"
  (https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-allowsetforegroundwindow);
  `SetForegroundWindow`: as condições e "An application cannot force a window to the foreground while the user is
  working with another window" (.../nf-winuser-setforegroundwindow); `GetForegroundWindow` e `GetAncestor(GA_ROOTOWNER)`
  (.../nf-winuser-getancestor); o UAC usa a janela dona para decidir se pergunta na frente ou na barra
  (https://learn.microsoft.com/en-us/previous-versions/bb756922(v=msdn.10)).
- **Arquivos de Programas, as licenças de fábrica** (lidas no PC com `icacls "C:\Program Files"`, só leitura): o
  sistema e os Administradores com tudo para o que nasce dentro; Usuários "(OI)(CI)(IO)(GR,GE)"; Proprietário Criador
  tudo; TrustedInstaller. A peça já cria e confere a pasta segura assim (`core/windows.py`, `criar_pasta_segura`,
  `conferir_pasta_segura`, `problemas_da_pasta_segura`).

### Para a gerente decidir (volta 4)

1. **`core/windows.py` precisa mudar** (três pedaços pequenos, todos conversa com o Windows, que só a peça pode ter):
   a pasta de trabalho do lançar solto (item 1, a causa); ler os processos que rodam de uma pasta (item 1, "conferido
   de verdade"); ler qual janela está na frente (item 2). Posso?
2. **A pergunta espera a janela do programa vir para a frente** (sem limite, sem aviso), em vez de perguntar e piscar.
   É a leitura que faço da D-806. Posso?
3. **A pasta trancada: saída B** (a pasta segura em Arquivos de Programas, sem comando de licença; 3 testes antigos que
   a D-774 nomeou mudam) ou **A** (mesma pasta, `icacls` consertado; precisa do "sim" do Samuel para itens novos no
   porteiro). Sugiro B.
4. **A troca sem o script** (o ajudante troca porque o Kaique fechou o programa durante o download, ou o Samuel mandou
   de longe) fica sem a proteção do clique no atalho. Fica como ressalva nesta entrega? (Fechar também pediria um
   vigia do lado do sistema, ou trocar só pelo script, o que mexe no atualizar de longe da D-736.)

### Perguntas para o Samuel (volta 4)

Nenhuma por enquanto: os 4 pontos acima são da gerente (o ponto 3, se for a saída A, precisa do "sim" dele para o
porteiro).
