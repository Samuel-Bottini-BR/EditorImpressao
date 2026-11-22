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
- Rodada do GitHub 44975834257: success (2ª tentativa). Próximo: a gerente manda a um agente novo que tenta quebrar.

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
  preparação rodam num fio por trás, iniciado por `primeira_vez_se_preciso`; a janela continua usável. O fim (o aviso
  da senha, quando houver, e mandar o ajudante rodar uma vez, como hoje acontece logo depois da pergunta) volta ao fio
  da tela por um sinal do Qt. O fio é "daemon": se o Kaique fechar o programa no meio, ele morre junto, e o trabalho
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
`anexos/reversao-conserto4-codigo-antigo.txt`.)
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

## Arquivos criados ou alterados

- `atualizacao.py` (os 4 consertos)
- `core/ocr_kraken.py` (conserto 4: `pasta_do_motor_instalado`, `lugares_do_motor`)
- `ui/testes_a_distancia_ui.py` (consertos 1 e 2: `primeira_vez_se_preciso`, `_rodar_por_tras`, `numero_da_janela`)
- `configuracoes.py` (saiu a marca `atualizacao_computador_preparado`)
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

## Perguntas para o Samuel

Nenhuma aberta. A pergunta 1 (a senha digitada na primeira abertura) foi respondida na D-825: opção B, "ok".

## Decisões procuradas antes de cada pergunta

Não se aplica: nenhuma pergunta aberta (a pergunta 1 foi respondida, D-825).

## Commit

- Plano: `bcc57104`. Conserto 1: `85590fe4`. Conserto 2: `f32eab48`. Conserto 3: `77a05d2e`. Conserto 4: `75cfa928`.
- Último commit do código e dos testes: `dd06e85f` (as docstrings dos testes e este formulário).
- GitHub: rodada 44975834257 (ramo `atualizador-4-consertos-2026-11-21`, commit `dd06e85f`): success na 2ª tentativa. A 1ª caiu na parte 1: `test_promessas.py` saiu com 3221225477 (o Qt quebrando, "cannot get C stack"), sem nenhum teste falhado antes; na repetição, as 5 partes, os botões e o porteiro passaram. No PC, `test_promessas.py` inteiro deu 269 passados e 1 falhado (`test_p082_filtros_em_tela_cheia`, a tela cheia dos filtros), que passou sozinho em seguida (2 de 2): instável com o PC carregado, sem ligação com estes consertos.

## O que o agente que tentou quebrar achou

(ainda não: a gerente manda a um agente novo)

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
