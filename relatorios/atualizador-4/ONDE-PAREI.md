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
- **Plano escrito (este arquivo). Parado, esperando a gerente conferir.** Nenhuma linha do programa mudou.
- Próximo, depois do "pode seguir": conserto 1, commit e push; conserto 2; conserto 3; conserto 4; rodada do GitHub.

## Decisões que esta tarefa precisa cumprir

(Palavras copiadas do Livro, `docs/plano/DECISOES.md` da versão de teste; o pacote tem a linha inteira de cada uma.)

- **D-718** "Sim, e tem que avisar a gente de alguma maneira". Aqui: a volta da versão que falha continua como está.
- **D-719** "1". Aqui: a frase da falha não muda.
- **D-724** "gratis, mas o que é essa assinatura e é segura?". Aqui: a assinatura antes de baixar não muda; o motor que
  vem no instalador só vai para o lugar se a soma dele for a do `motor-exigido.json`, que vem dentro do pacote assinado.
- **D-727** "pode, se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador né". Aqui: o motor do
  instalador é posto no lugar sem baixar nada.
- **D-732** "não, faz quando o programa é aberto". Aqui: a procura ao abrir não muda.
- **D-733** "1- sim / VAI CONSEGUIR FAZER OS TESTS A DISTANCIA NÉ?". Aqui: a pergunta da primeira abertura continua
  criando o ajudante; muda só quem pede a licença (a peça única). Ver a pergunta 1 para o Samuel (com a senha digitada).
- **D-734** "quando ele abrir o programa de novo". Aqui: continua valendo nesta entrega (a D-769/D-794 ficam para
  depois); conserto 3 faz essa abertura funcionar.
- **D-735** "Sim". Aqui: a pergunta aparece sempre, com ou sem a senha.
- **D-741** "Sim". Aqui: depois do "Não", a pergunta volta a cada abertura; quem decide passa a ser o Windows lido, não
  a marca.
- **D-749** "Sim". Aqui: erro no meio da preparação → conta como não feita e a pergunta volta; quem decide é o relatório
  da peça e a leitura do Windows (tarefas, Visual C++, Inno), não o `preparo.txt`.
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
  `ctypes.get_last_error()` numa biblioteca aberta sem `use_last_error=True`: sempre 0. O "Não" (1223) vira código 0,
  `Resultado(True)`, e `preparo_deu_certo` cai em "vale o resultado da pergunta inteira" (o passo nem rodou, o
  `preparo.txt` não tem a marca desta vez) → grava a marca nas Configurações → nunca mais pergunta. Segunda causa: o
  "preparado" é uma anotação (a marca nas Configurações e o `preparo.txt`), não o que o Windows tem.
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
    `preparo.txt` saem (`preparo_deu_certo`, `arquivo_do_preparo`).
- **Todos os caminhos** (grep por `preparar_na_primeira_abertura`, `falta_a_pergunta_do_windows`,
  `CHAVE_PERGUNTA_DO_WINDOWS_RESPONDIDA`, `preparo_deu_certo`, `passo_de_preparar_o_computador`, `_rodar_elevado`):
  1. primeira abertura com "Agora não" → `ui.primeira_vez_se_preciso` → `preparar_na_primeira_abertura("")`: hoje pelo
     executor antigo; passa à peça;
  2. primeira abertura com a opção dos testes desligada (sem janela da senha): o mesmo caminho;
  3. primeira abertura com a senha digitada: hoje `td.ligar` com o executor "acrescido" do preparo, numa pergunta;
     ver a pergunta 1 para o Samuel;
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
- **Caminhos:** os mesmos 1, 2 e 4 do conserto 1 (o 3, ver a pergunta 1). Não há outro pedido de licença no atualizador.
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
  `current\instalar\motor-kraken-1.zip` (D-788). Ninguém tira o motor de lá: o programa o procura em
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
    senão pega `current\instalar\motor-kraken-<v>.zip`, confere a soma contra o `current\motor-exigido.json` (dentro do
    pacote assinado), confere o espaço livre, abre em `motor-kraken\.chegando-<v>`, confere com `conferir_motor` e só
    então dá o nome final; erro → apaga o `.chegando` e registra. Roda no ajudante (como o sistema, por trás), no começo
    de `rodar_ao_ligar`, logo depois de `preparar_o_computador`;
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

Conserto 4 (o motor):
- **Sem o arquivo do motor em `instalar\` e sem motor no lugar:** registra "falta o motor"; a versão nova não troca
  (fica "pendente"); o Kaique continua na versão de hoje. (Acontece se o instalador foi feito sem o motor.)
- **Soma do arquivo diferente da do `motor-exigido.json`, ou sem o `motor-exigido.json`:** não abre; registra; não troca.
- **Disco sem espaço** (o tamanho aberto do motor mais uma folga, conferido antes): não começa; registra; tenta depois.
  Enche no meio: o erro apaga o `.chegando`.
- **Desligar no meio:** sobra só o `.chegando-<v>`, nunca o nome final; a próxima vez o apaga e recomeça.
- **Antivírus segura ou tira um arquivo:** abrir ou conferir falha → apaga o `.chegando`, registra, tenta depois.
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

(Plano; os testes ficam em `tests/test_atualizador_4.py`, cada um provado desligando a proteção numa cópia.)
- "Não" da peça → não preparado e a pergunta volta: teste com o pedido de mentira devolvendo DISSE_NAO.
- "Sim" com o Windows sem o ajudante → não preparado: teste com o pedido DEU_CERTO e a leitura dizendo "não existe".
- O ajudante apontando para outro programa → falta: teste com a leitura devolvendo outro comando.
- Visual C++ faltando ou Inno ainda lá → falta (D-749): teste com os leitores trocados.
- Leitura "não deu para saber" → falta: teste.
- A janela vai ao pedido: teste que confere `janela=` com o número da janela.
- O pedido real nunca roda sob o pytest: teste que chama o pedido de verdade sob o pytest e recebe "falhou" sem
  pergunta (e o porteiro K24/nenhuma janela nos testes).
- O lançar da troca vai pela peça e só dá True com o sinal de vida: teste com a peça de mentira devolvendo "falhou".
- Nenhum `DETACHED_PROCESS` em `atualizacao.py` fora da volta: o teste da D-774 (reescrito) e o porteiro K02.
- O limite novo chega ao script: teste.
- O motor: soma errada recusa; espaço curto recusa; o nome final nunca pela metade (erro no meio deixa só o `.chegando`
  apagado); motor no lugar não é refeito; a troca não acontece sem o motor; o teste rápido acusa o motor faltando; o
  programa instalado procura só em `motor-kraken\<v>`. Cada um com zip e pastas de mentira numa pasta temporária.

## De onde vem cada dado que a conferência usa

- "Preparado": o Agendador do Windows (`ler_tarefa`, pelo COM do Windows), o registro do Windows (Visual C++ e Inno) e
  o arquivo `instalar\vc_redist.versao.txt` do pacote assinado. Nada que o programa anota.
- O desfecho da pergunta: o relatório que o programa com licença escreve na pasta de troca, conferido pela peça (ela já
  confere dono e licença da pasta; o relatório decide junto com o código de saída), e depois a leitura do Windows.
- O "começou" da troca: o arquivo de sinal que o próprio script lançado grava (prova só que ele começou; o resto é a
  troca, como hoje, conferida pelo estado que o ajudante grava como o sistema).
- O motor: a soma do arquivo calculada agora contra a do `motor-exigido.json` (dentro do pacote que o Velopack conferiu
  pela soma e que a nossa assinatura cobre); a ficha `motor.json` e o tamanho de cada arquivo no disco
  (`conferir_motor`).

## O que li da peça de fora e onde

- **Pedir licença (`ShellExecuteExW`, verbo "runas"):** o erro vem de `GetLastError`; "ERROR_CANCELLED" quando a pessoa
  cancela; `hwnd` é a janela dona; `SEE_MASK_FLAG_NO_UI` esconde a caixa de erro
  (https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecuteexw e .../ns-shellapi-shellexecuteinfow).
  Só com `use_last_error=True` o `ctypes.get_last_error()` traz o erro da chamada (https://docs.python.org/3/library/ctypes.html).
  "The UAC elevation mechanism uses the HWND as part of determining whether the elevation is a background or foreground
  elevation"; "Background applications will automatically prompt the user for elevation on the taskbar"
  (https://learn.microsoft.com/en-us/previous-versions/bb756922(v=msdn.10)). "An application cannot force a window to
  the foreground while the user is working with another window" (.../winuser/nf-winuser-setforegroundwindow). Lido pelo
  passo 1 e conferido no código da peça (`_abrir_com_licenca`, `trazer_para_a_frente`, `o_que_houve_ao_abrir`).
- **O que a peça faz em cada caso** (lido em `core/windows.py`): DISSE_NAO só para 1223; FALHOU para todo outro erro;
  DEU_CERTO só com o relatório completo, os mesmos passos e código 0; passou do limite → FALHOU e a pasta fica.
  `lancar_powershell_solto`: arquivo com marca de UTF-8, sem a bandeira proibida, sinal de vida em 30 s, senão fecha o
  lançado; recusa se o grupo mataria o lançado. `ler_tarefa`: "não existe" (0x80070002/3), "existe sem leitura"
  (0x80070005), "não deu para saber" (outro).
- **`DETACHED_PROCESS` com `CREATE_NO_WINDOW`:** "CREATE_NO_WINDOW... This flag is ignored if the application is not a
  console application, or if it is used with either CREATE_NEW_CONSOLE or DETACHED_PROCESS"
  (https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags); provado na etapa 5
  (`saida_teste/etapa5/registros/variantes-lancar-escondido.txt`).
- **Velopack 1.2.161, a troca** (`src/bins/src/commands/apply_windows_impl.rs`, etiqueta 1.2.161, lido hoje): extrai a
  versão nova numa pasta temporária, fecha à força tudo o que roda dentro da raiz (`force_stop_package(root)`, que
  pula só ele mesmo), renomeia `current` para a temporária velha (10 tentativas de 1 s) e a nova para `current` (30
  tentativas); depois só o registro de desinstalar, atalhos, `Update.exe` e o atalho de partida da raiz. Nada mais da
  raiz é apagado: `motor-kraken\` ao lado fica. Na segunda renomeação que falha, pode ficar sem `current` (defeito
  conhecido, D-779). Os processos achados são os cujo arquivo está dentro da raiz (`util_windows.rs`,
  `get_processes_running_in_directory`): o PowerShell do Windows (em System32) não é fechado.
- **Velopack, o reinício** (`src/bins/src/commands/apply.rs`): com `restart`, depois de trocar abre a versão nova com
  os mesmos argumentos (`start_package`); se a troca falhar, abre a versão de antes com os mesmos argumentos e devolve o
  erro.
- **Velopack, como abre o programa** (`src/lib-rust/src/process_win.rs`, `run_process`): `CreateProcessW` com
  `CREATE_UNICODE_ENVIRONMENT` (com janela) ou mais `CREATE_NO_WINDOW`, sem grupo de processos, e
  `AllowSetForegroundWindow` para o aberto; não espera. Então o programa aberto pelo atalho não está num grupo que mate
  os filhos, e pode tomar a frente.
- **Velopack, a pasta fora de `current`:** "If you want to create settings that persist through updates, but are erased
  when the app is uninstalled, on Windows you should store them one level up (`..\`) outside of the `current` dir"
  (`docs/integrating/preserved-files.mdx`, citado no estudo do Kraken §1, ramo `kraken-separado-2026-11-18`).
- **`zipfile` (Python 3.14):** ao abrir, nome com caminho absoluto perde a unidade e as barras do começo, e todo ".."
  sai (documentação de `ZipFile.extract`); arquivo com a soma interna errada dá "Bad CRC-32" (estudo do Kraken §3). A
  entrada que aceita: o zip do motor (um arquivo só, `versao.arquivo_do_motor`). Não aceito outro nome nem outro lugar.
- **`os.rename` no Windows:** se o destino existe, `FileExistsError` sempre (documentação do `os`); por isso o nome
  final só é dado depois de o destino não existir, e no mesmo disco.
- **`shutil.disk_usage`:** total, usado e livre do disco do caminho (documentação do `shutil`).
- **PowerShell `Start-Process -Wait -PassThru`:** devolve o processo e espera; o `ExitCode` é o do programa. O mesmo
  jeito de hoje (`passo_de_preparar_o_computador`), provado na etapa 5 (a preparação rodou e tirou o Inno às 09:02:07).
- **Deduzido, a provar à vista:** que a conta comum lê a tarefa do ajudante (pela licença GRGX); que a pergunta vem no
  meio da tela com a janela dona e na frente; que o programa reaberto pelo script aparece.

## Os testes antigos que precisariam mudar

Só listados; nenhum muda sem o "sim" (D-774 cobre os dois marcados).

- **D-774 cobre:**
  1. `test_decisoes_ajudante_da_atualizacao.py::test_d733_o_script_escondido_vai_codificado_e_solto` (cobra o
     `DETACHED_PROCESS`; passa a cobrar o lançar pela peça com o sinal de vida). Plano-v3 §8, item 1.
  2. `test_decisoes_ajudante_da_atualizacao.py::test_d741_a_marca_e_de_fabrica_falsa_e_gravada_so_pelo_sim` (cobra a
     marca nas Configurações; passa a cobrar a leitura do Windows). Plano-v3 §8, item 5.
- **Vão ao Samuel, um por um** (todos cobram o pedido antigo, pela peça dos testes à distância, ou a anotação):
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
  12. `test_decisoes_preparo_d749.py::test_d749_sim_com_a_preparacao_parada_no_meio_a_pergunta_volta` (o `preparo.txt`);
  13. `test_decisoes_preparo_d749.py::test_d749_uma_anotacao_velha_nao_conta` (o `preparo.txt`);
  14. `test_decisoes_preparo_d749.py::test_d749_o_passo_anota_como_o_preparo_terminou` (o `preparo.txt`);
  15. `test_decisoes_testes_a_distancia.py::test_d721_primeira_vez_pede_a_senha_e_liga` (com a senha; depende da
      pergunta 1; e espera a pergunta antes de a função voltar);
  16. `test_decisoes_testes_a_distancia.py::test_d728_instalado_primeira_vez_pede_a_senha` (idem).
  Cada um passa a cobrar o mesmo comportamento da decisão (D-733, D-735, D-741, D-749) pelo jeito novo: a pergunta pela
  peça, o "preparado" lido do Windows. A conferir no código antes de mudar: se mais algum quebra (a rodada do GitHub
  dirá); se quebrar, vem para esta lista, nunca muda calado.

## Ressalvas

- O teste automático não prova a pergunta do Windows, a troca nem o motor de verdade (D-767): é a sessão à vista.
- A volta para a anterior continua com o lançar antigo do Update.exe (funcionou na etapa 5).
- A troca que o Velopack não consegue fazer reabre a versão de antes, que se dá como "ok" (ver "Ideias e bugs").
- Uma leitura do Windows a cada abertura (um PowerShell por trás). Não atrasa a janela; gasta um pouco de processador.
- "Reiniciar agora" fica sem nada na tela durante a troca (a janelinha em toda troca é da D-770, fica para depois).

## Velocidade

Nenhum dos 4 mexe no processamento das páginas. A abertura da janela não ganha espera: as leituras novas rodam por
trás. O caminho do livro não usa o Kraken (D-164). A gerente decide se roda o filtro de velocidade do GitHub.

## Ideias e bugs

- **Bug (21/11, lido no código, não impede):** quando o Velopack não consegue trocar, ele reabre a versão de antes com
  `--conferir-a-versao-nova` (`apply.rs`); `conferir_e_refazer_o_ajudante` roda o teste rápido nela, passa, e grava
  "ok" com a versão de antes como "nova": a falha da troca some do registro e da tela. `atualizacao.py`
  (`conferir_versao_nova`). Para a Lista de bugs.
- **Ideia:** se a janela não está na frente, esperar o Kaique voltar a ela para pedir a licença (em vez de piscar).

## Perguntas para o Samuel

### 1. Se o Kaique digitar a senha dos testes na primeira abertura

**O que é e onde fica.** Na primeira vez que o programa abre no notebook, aparece a janelinha "Testes à distância",
que pede a senha dos testes. Logo depois vem a pergunta do Windows "Deseja permitir...?". Combinado para esta
entrega: o Kaique clica "Agora não" na senha.

**O que acontece hoje.** Com a senha digitada, as duas coisas (preparar a atualização e ligar os testes) vão numa
pergunta do Windows só, pelo jeito antigo, o que transforma o "Não" em "Sim" sem ninguém ver.

**O que muda.** A atualização passa a pedir a licença pelo jeito novo, que lê o "Não" certo. Os testes à distância só
vão ser consertados na atualização que trouxer eles. Então, se alguém digitar a senha nesta entrega, não dá mais para
ir tudo numa pergunta só.

**O que você escolhe:**
- **A (sugiro):** com a senha digitada, aparecem duas perguntas do Windows seguidas: a do programa (jeito novo) e a dos
  testes (do jeito de hoje, que ainda tem o defeito do "Não"). Com "Agora não", nada muda: uma pergunta só.
- **B:** com a senha digitada, a senha não liga os testes nesta entrega; eles ligam na atualização que trouxer os
  testes consertados. Uma pergunta só, sempre.
- **Só comentário.**

Nada do que já funciona muda nos dois casos, e o Kaique continua clicando "Agora não". (Decisões D-733 e D-824.)

## Decisões procuradas antes de cada pergunta

### 1. Se o Kaique digitar a senha dos testes na primeira abertura

Procurei D-721, D-733, D-735, D-741, D-765, D-771, D-781 e D-824. A D-733 e a D-735 dizem "a senha, se digitada, entra
na mesma pergunta"; a D-824 deixa os testes à distância para depois e diz que o Kaique clica "Agora não", mas não diz o
que acontece se a senha for digitada. Por que ainda não está respondida: a mesma pergunta só existia porque os dois
iam pelo mesmo pedido antigo; com o pedido novo só na atualização, as duas decisões não cabem juntas nesse caso.

## Commit

- Plano: este commit (só documentos).

## O que o agente que tentou quebrar achou

(ainda não: depois do código)

## A prova de verdade

(é da gerente, numa sessão com o Samuel, depois do código e de quem tenta quebrar)

## Perguntas do Windows que o Samuel vê

- Nesta etapa (plano): 0.
- No código e nos testes automáticos: 0 (o pedido de verdade se recusa sob o pytest).
- Na sessão à vista: a pergunta da primeira abertura ("Não", depois "Sim", com o navegador na frente numa delas); o
  número exato vai no roteiro.

## O print que prova

(depois do código; nesta etapa, nenhum: só documento)

## Páginas em que foi conferido

Não se aplica: nenhum dos 4 mexe em imagem nem no PDF.
