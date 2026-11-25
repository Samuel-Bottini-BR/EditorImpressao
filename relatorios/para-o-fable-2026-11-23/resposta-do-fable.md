# Resposta do Fable — auditoria externa do Editor de Impressão

23/11/2026. Fable 5.1 (claude.ai), a pedido do Samuel. Li o `relatorio-para-o-fable.md` inteiro (981 linhas) e conferi o código nos objetos git dos commits citados: `0f58346a` (programa) e `aa1963b7` (atualizador). Arquivos extras abertos: `modelos.py`, `core/girar.py`, `core/automatico.py`, `ui/tela_ampliada.py`, `ui/desfazer_nesta_pagina.py`, `core/windows.py` (cabeçalho), `core/_testes_a_distancia_windows.py`, `tests/test_atualizador_volta4.py`, `regras_dos_agentes/porteiro.py`, `tests/conferencias_excecoes.json`.

Regra desta resposta: nada de regra nova no CLAUDE.md, checklist ou documento. Só estrutura de código, desenho e travas mecânicas (código/teste que impossibilita o erro).

## Decisão do Samuel (23/11/2026, 18:50)

> "refazer"

O atualizador será **refeito no desenho simples antes de entregar ao Kaique**, e não a volta 4 consertada. A D-765 continua valendo para o programa até a entrega.

---

## Achado que o relatório não trazia

**Certeza.** Os testes do atualizador testam texto, não comportamento. `tests/test_atualizador_volta4.py` faz `assert "MarcaExiste" in lancados[0]`: confere que a string do PowerShell contém uma palavra. Por isso o relatório 3 pôde trocar `catch { return $true }` por `return $false` e os 55 testes passaram. Enquanto for assim, "os testes passam" não diz nada sobre o atualizador.

---

## Pergunta 1 — Atualizador e testes à distância

**Certeza (código):**
- `atualizacao.py`: 2.314 linhas; 256 linhas são literais de string montando PowerShell; 3 mutexes globais; `estado.json` como canal entre contas; `MarcaExiste` (L1085) devolve `$true` no `catch` — confirmado.
- Quem troca é o próprio `EditorImpressao.exe` de `current`, como SYSTEM. Disso decorrem o `--waitPid` esperar o processo errado, a lista de processos (30 s), o vigia, a marca de reabrir e o script de reabrir.
- `core/_testes_a_distancia_windows.py` L94-95: `runas` próprio com `ctypes.windll` e `get_last_error()` sem `use_last_error` — o "Não" do UAC vira 0. A peça `core/windows.py` já tem `pedir_licenca`, `passo_criar_pasta_segura`, `passo_gravar_na_pasta_segura`, `passo_criar_tarefa`; ligar/desligar nunca passaram por ela.

**Veredito: refazer.** Os 5 médios moram em peças que só existem para proteger outras.

**Desenho (palpite forte; 1 experimento pendente), mantendo D-733 e D-736:**

Princípio: nenhum processo nosso roda fora da sessão do Kaique. O único ato privilegiado acontece uma vez, na primeira abertura, e é dar à pasta do programa a licença que uma instalação por usuário já teria.

1. **Primeira abertura — o único UAC (D-733, jeito 1).** Pela peça (`passo_*`), nunca à mão: Users (`S-1-5-32-545`) com Modificar `(OI)(CI)M` na raiz da instalação do Velopack; VC++; tirar o Inno; tarefa "desfazer". Sem ajudante SYSTEM, sem `--preparar-o-computador`, sem exe elevado que abre PowerShell que abre exe.
2. **Só ao abrir o programa (D-732: "quando ele abre o programa, assim como todo aplicativo faz"; o "de 5 em 5 min" era o código antigo, não decisão do Samuel — corrigido 23/11 20:42), dentro do programa:** `check_for_updates` → assinatura Ed25519 → `download_updates`. Programa aberto: "Reiniciar agora / Depois" (D-715/D-720).
3. **"Reiniciar agora":** `apply_updates_and_restart`, na sessão do Kaique; o `Update.exe` espera o PID, troca `current` e reabre na conta certa. **"Depois":** `wait_exit_then_apply_updates` ao fechar (D-734). Teste rápido e volta à anterior (D-718) continuam, chamados pelo próprio programa em `--conferir-a-versao-nova` antes de abrir a janela.
4. **D-736 (mandar atualizar de longe):** o Samuel publica e, por SSH como `EditorTestes` (conta Users), roda `EditorImpressao.exe --baixar-atualizacao`: baixa e deixa pronto; a troca acontece na próxima abertura do Kaique ou no "Reiniciar agora". Forçar troca com o programa aberto já contradizia D-715.

**Some:** ajudante SYSTEM, 2 scripts PowerShell, vigia, 3 mutexes, `estado.json` entre contas, lista de processos, `GerenteComAMarcaDaTroca`, `FASES_EM_QUE_HA_TROCA`, esperar-a-janela-na-frente (a pergunta do UAC passa a ser feita antes de montar a janela, como a D-806 descreve). Estimativa: `atualizacao.py` em 300-400 linhas.

**Experimento que decide (passo 1, abaixo):** com a ACL acima, uma conta padrão consegue rodar `Update.exe apply` (renomear `current`)? Falta confirmar que o `Update.exe` 1.2.161 tem manifesto `asInvoker` e que `.velopack_lock` não exige elevação. **Plano B** se falhar: tarefa SYSTEM que chama só `Update.exe apply --waitPid <pid>` (nunca o nosso exe) e reabertura por uma tarefa interativa da conta do Kaique — ainda zero PowerShell, zero mutex.

**Travas mecânicas:**
- Teste de AST em `tests/`: `ctypes`, `subprocess`, `winreg`, `os.startfile` importados somente em `core/windows.py`. Binário, sem lista de exceções.
- Teste: nenhum literal de string fora de `core/windows.py` contém `powershell`, `-Command` ou `.ps1`. Script que sobrar vira arquivo `.ps1` executado no `windows-latest` do CI.
- Máquina de estados da atualização como função pura `proxima_fase(estado, evento) -> (estado, efeitos)`, sem I/O, com teste exaustivo das transições.

Testes à distância: ligar/desligar pela peça com os `passo_*` existentes; a tela mostra o que o Windows responde (`ler_tarefa`, serviço, conta); `CHAVE_PRONTO` apagada.

---

## Pergunta 2 — Por que o ciclo se repete

**Certeza:** o código é o mecanismo que transforma "pedido por caso" em divergência:
- `TelaConferir`: 398 métodos. A lista "o que vai junto" está à mão em `_campos_do_aplicar_em` (L9133), `CAMPOS_DA_PAGINA` (`core/automatico.py` L149), `MARCAS_DA_PAGINA` (L10152), perfis e chave das prévias. `claro_no_escuro` está em duas e falta na terceira.
- A ação do desfazer é montada em 4 lugares: `tela_conferir.py` L2266, L5955 (`_registrar`), L9512 e `ui/desfazer_nesta_pagina.py`. `_registrar` carrega regra de domínio (`_com_a_marca_mexida_a_mao`, `_com_os_avisos_de_agora`, invalidar prévias) dentro da UI.
- Girar: 14 métodos na tela; `(rotacao + giro) % 360` à mão em L7322 e L7382 enquanto `girar.nova_rotacao` existe (`core/girar.py` L170).
- Três renderizações do "como fica": `_filtrar_a_pagina` (pipeline L3437), `filtro_com_as_caixinhas` (L3546), `_imagem_do_outro_filtro` (`tela_ampliada.py` L304, sem `selecao` nem "Só as letras").

**Refatoração mínima (ordem; ~3 dias, palpite):**
1. **Metadados no modelo (meio dia).** Cada campo de `ConfigPagina`/`ConfigFolha` ganha `field(metadata={"etapa": ..., "aplicar_em": ..., "a_mao": ...})`. As listas à mão são apagadas e derivadas de `dataclasses.fields()`. **Trava:** teste que falha se algum campo não tiver `etapa`.
2. **Porta única em `core/comandos.py` (2 dias).** `executar(projeto, acoes, comando) -> Efeitos`; comandos `Girar`, `AplicarEm`, `Dividir`, `DesfazerNaPagina`... O corpo de `_registrar` vai para lá; a tela só constrói o comando e redesenha pelos `Efeitos`. **Trava:** teste de AST — `montar_acao`/`historico_acoes.aplicar` chamados em exatamente um arquivo.
3. **Uma renderização (meio dia).** `filtro_com_as_caixinhas` e `_imagem_do_outro_filtro` chamam `_filtrar_a_pagina` com `img` injetada. **Trava:** teste de pixels — página-fixture com marcação + "Só as letras" + fundo tirado, os três caminhos devolvem o mesmo array.

---

## Pergunta 3 — Peso do jeito de trabalhar

**Palpite.** Converter cada regra da §11 que pode virar teste em teste e apagar o texto (a §11.12 inteira vira as três travas acima). O "quem tenta quebrar" é o mecanismo que funcionou; a versão mecânica é mutação automática (`mutmut`) sobre `core/windows.py`, `core/comandos.py` e a máquina de estados, em todo push. Manter as provas por decisão (`test_decisoes*`): são o Livro executável; o agente não precisa das 804 decisões em prosa.

## Pergunta 4 — Porteiro

**Certeza:** K01 é lista de regex (`PALAVRAS_DO_WINDOWS`, `porteiro.py` L225); listas de palavras vazam por construção (`New-Item`). 164 exceções em 4 arquivos.
**Recomendação:** conferência estrutural (AST de imports; zero PowerShell fora da peça), binária, sem exceções; as 164 somem ao conformar os 4 arquivos (as 52 de `teste_velocidade.py` saem movendo o script para fora do escopo ou para a peça). Gate rápido no CI (core sem Qt, < 2 min) antes das 2 h do Windows.

## Pergunta 5 — Os 16 remendos

**Certeza:** 10 dos 16 são "regra em mais de um lugar": A1-A4, M1, M2, M5, M6, M7, M9. Consertá-los antes da refatoração 1-3 cria mais caminhos.
**Ordem:** (a) atualizador refeito e entregue; (b) antes do primeiro conserto de programa pós-entrega, as refatorações 1-3; (c) só então M3, M4, M8, B1, B3, B4, que são independentes.

## Pergunta 6 — O que não perguntaram

- **Certeza:** 1.206 commits e +29.584 linhas de `core/`+`ui/` no `obra-2026-10-26` fora do `fase-1`: merge de 29 mil linhas adiado. O `obra` é o tronco de fato; declará-lo tronco (o `fase-1` só para documentos) ou fazer merges contínuos.
- **Certeza:** 200 worktrees em `.claude/worktrees/` dentro do repositório: lentidão (um `grep -r` na raiz estourou 120 s) e ramos que nunca fecham.
- **Palpite:** a trava "core não importa ui" está certa mas incompleta; falta a inversa: `ui/` não monta `campos`. Depois da refatoração 2, teste de AST que proíbe método de `ui/` de construir dict com chaves que sejam nomes de campos de `ConfigPagina`.

---

## O plano, na ordem

### Passo 1 — Experimento de 10 minutos (decide o desenho do atualizador)

**Onde:** PC do Samuel, programa instalado pelo `.msi` em `C:\Program Files\EditorImpressaoPrograma`.

1. Como administrador, uma vez: `icacls "C:\Program Files\EditorImpressaoPrograma" /grant *S-1-5-32-545:(OI)(CI)M /T`.
2. Como conta comum, com uma versão nova publicada: fluxo normal do Velopack dentro do programa — `check_for_updates` → `download_updates` → `apply_updates_and_restart`.
3. Registrar: (a) o download gravou em `packages\`? (b) o `Update.exe` renomeou `current` sem UAC? (c) o programa reabriu na conta do usuário?
4. Repetir o passo 2 com o programa fechado, com `wait_exit_then_apply_updates`.

**Regras:** nenhuma linha do `atualizacao.py` muda. Nenhum script. Resultado: "funcionou / não funcionou em qual passo", com a mensagem exata do Windows se falhou.

### Em paralelo ao passo 1 (não depende dele)
- Escrever a primeira trava: teste em `tests/` — `ctypes`, `subprocess`, `winreg`, `os.startfile` só em `core/windows.py`. Vai falhar hoje; a lista de falhas é a lista de trabalho do passo 2.

### Passo 2 — Refazer o atualizador (decisão do Samuel: antes de entregar)
Ramo novo, do zero, no desenho da Pergunta 1 (ou plano B se o experimento falhar). Com as duas travas. Testes à distância pela peça única. Entregar ao Kaique.

### Passo 3 — Depois da entrega: estrutura do programa
Refatorações 1, 2 e 3 da Pergunta 2, nesta ordem, com a suíte rodando a cada passo. Nenhum conserto de sintoma antes.

### Passo 4 — Os 6 remendos independentes e a fila de bugs.

## O que isto resolve e o que não resolve

Resolve o retrabalho "consertei aqui, quebrou ao lado" (Girar 9 voltas, figurinhas 5, volta 4). Resolve pela metade o do atualizador (depende do experimento). **Não resolve** dois tipos: pedido que muda depois de pronto (descoberta normal de produto; a estrutura só garante que o conserto seja feito uma vez) e agente que dá como feito o que não conferiu (só teste que falha antes e passa depois, rodando sem depender do agente). Risco real: a refatoração 2 mexe em 10 mil linhas; por isso vem depois da entrega, começando pelo passo pequeno (1) e com os 4.668 testes a cada passo.


## Correção (23/11/2026, 20:42)

- A procura de versão nova é **só ao abrir** (D-732). O "de 5 em 5 minutos" citado antes era o comportamento do código antigo, não decisão do Samuel; ele lembrou que já tinha dito que não era bom. Nada roda por trás enquanto o Kaique trabalha. O "mandar de longe" (D-736) continua: publicou com o programa aberto, entra na próxima abertura (D-734).
- Resultado do experimento (23/11, 20:20): **funcionou**. Com Usuários:(OI)(CI)(M) na raiz, como conta comum, `apply_updates_and_restart` trocou 1.1.0→1.1.2 com o programa aberto e reabriu na conta do usuário; `wait_exit_then_apply_updates` trocou 1.1.2→1.1.1 com o programa fechado. Nenhum UAC. Única falha, cosmética: "Failed to update uninstall entry" (Programas e Recursos continua mostrando a versão antiga; decidir depois da entrega se o UAC único dá licença nessa chave do registro). O desenho simples está liberado; o plano B não é necessário.

## Revisão contra o Livro de decisões (23/11/2026, 20:50)

Conferi o desenho da Pergunta 1 contra as palavras do Samuel em D-705 a D-825 (as que tocam atualizador e testes à distância). Três correções ao que escrevi acima:

1. **"Depois" entra ao fechar, não na próxima abertura.** Eu citei a D-734 (17/11), mas ela foi superada pela **D-769** (18/11, "b": ao fechar o programa) e pela **D-794** (ao fechar, aviso "Atualizar agora?"). A D-824 adiou as duas para uma segunda entrega porque no desenho antigo eram caras; no desenho novo "ao fechar" é `wait_exit_then_apply_updates`, provado no experimento. **Escolha pendente do Samuel:** (a) fazer já como decidido em 18/11 (recomendado); (b) manter o adiamento e entregar com "próxima abertura".
2. **A janelinha "Atualizando o programa..." (D-742, D-748, D-770: em toda troca) é obrigatória** e eu não a listei. No desenho novo quem troca é o `Update.exe`, depois que o programa fechou; a janelinha tem de ser a tela de progresso do próprio Velopack. **A confirmar pelo agente:** se ela aparece no `apply`, e se aceita o nosso texto e o brasão. Se não, a janelinha volta a ser nossa, sem script.
3. **O motor do Kraken, "tudo ou nada" (D-768, D-788, D-789, D-790),** não foi citado: a versão nova só é anunciada com o motor dela no lugar. Já existe (conserto 4 da volta 1) e passa inteiro para o desenho novo.

Confirmados: um UAC só (D-733); procura só ao abrir (D-732/D-740); "mandar de longe" baixa por SSH e o programa não procura fora da abertura (D-736, texto completo: "mas o programa não precisa procurar versão nova"); pergunta volta até o "Sim" e preparação pela metade conta como não feita (D-741/D-749 — no desenho novo "preparado?" é lido da licença da pasta, não de anotação); volta à anterior com aviso na tela e registro lido de longe (D-718/D-719); pergunta antes de montar a janela (D-806); desinstalar desfaz tudo (D-731); senha dos testes na primeira abertura e botão nas Configurações (D-721/D-712) não mudam.

### Decisões do Samuel sobre a revisão (23/11/2026, 20:48)

1. **"a"** — "Depois" entra ao fechar, com o aviso "Atualizar agora?" ao fechar (D-769/D-794), já nesta entrega. O adiamento da D-824 para esses dois itens cai.
2. **"pode ser velopack, deixamos para mudar isso mais para frente"** — a janelinha da troca é a tela de progresso do próprio Velopack. Texto e brasão nossos ficam para depois.

## Plano do atualizador novo — parecer do Fable e respostas do Samuel (23/11/2026, 23:27–23:42)

Plano lido: `relatorios/atualizador-novo/plano-do-atualizador-novo.md` (seções 1, 3, 4, 5, 7, 10, 11, 12 e ressalvas por inteiro; 2 por amostra; 6, 8, 9 não lidas). **Parecer: liberar para código**, com as respostas abaixo e duas observações.

**Pontos em que o plano foi além do pedido, corretamente:** apagar a tarefa SYSTEM antiga *antes* de dar Modificar a Usuários (senão qualquer conta trocaria o `.exe` que roda como sistema); "preparado?" = teste de gravar na raiz, o mesmo do Velopack, sem anotação; volta à anterior pela biblioteca, sem `Update.exe` à mão; máquina de estados pura com tabela exaustiva e 13 proteções cada uma com teste que falha ao ser desligada; D-736 deixada para a entrega dos testes à distância, com o lugar pronto.

**Observações para a gerente antes do "pode":**
1. Passo 4 (licença): um caminho só, o provado no experimento (`icacls /grant ... /T` pela peça), não `SetNamedSecurityInfoW` com o provado de reserva. Com a resposta à pergunta 6, a K03 passa a permitir só essa função da peça, só para acrescentar.
2. Ressalva 7 é risco de entrega: conferir **antes** de mandar o `.msi` se a conta do Kaique é administradora. Se for padrão, o único UAC pede senha de administrador que ele não tem — ou o Samuel está presente na primeira abertura, ou a conta vira administrador antes.

**Respostas do Samuel às perguntas do plano (seção 12):**
- Pergunta 1 (ordem na primeira abertura): **"sim"** — a pergunta do Windows antes da senha dos testes.
- Pergunta 2 (textos): **"B"** — pergunta ao fechar curta ("Quer atualizar o programa agora, ao fechar?", botões "Sim"/"Não"). Para o aviso de versão nova, não escolheu entre A e B; o Fable sugere B ("você pode atualizar quando fechar o programa"), por casar com a pergunta curta.
- Pergunta 3 (ícone perto do relógio): já respondida às 20:48 — janelinha do Velopack; ícone para a lista de espera.
- Pergunta 4 (avisos de falha): já decidida em 18/11 (D-778) — as três frases entram.
- Pergunta 5 (testes antigos): **"Não quero [ver antes], mas quero que ele passe a lista para você verificar"** — a lista teste por teste (apagado / adaptado / passou a cobrar o que vale hoje, com a decisão que cada um protege) vem na entrega e é conferida pelo Fable antes do "quem tenta quebrar".
- Pergunta 6 (porteiro e licença): opção (1) — só a função da peça, só para acrescentar.
- Pergunta 7 (limpeza do PC do Samuel): opção (1) — desinstalar pelo Windows; a gerente lista o que sobrou; o Samuel aprova o que apagar.

## Emenda ao desenho do atualizador — depois do segundo "quem tenta quebrar" (24/11/2026, 11:30)

Relatório lido na íntegra: `relatorios/atualizador-novo/quem-tenta-quebrar-2/relatorio.md` (1 grave, 9 médios, 4 leves; rodado no Windows de verdade). Terceiro ciclo: parei para olhar o desenho, como combinado com o Samuel.

**Veredito.** O desenho grande está certo (nenhum processo nosso fora da sessão do Kaique, zero script, uma peça para o Velopack; o grave de 22/11 está resolvido com o `Update.exe` de verdade). O erro está em **duas peças que o plano manteve do atualizador antigo** (seção 5 do plano, "Fica": `ler_estado`/`gravar_estado` e `voltar_para_a_anterior`). É onde G1, M1, M2, M3, M4 e M5 se concentram. Erro meu: aceitei o "Fica" sem perguntar por que essas duas ficavam.

**A causa em uma frase:** o programa confia num bilhete (`estado.json`) em vez de olhar o que existe, e a volta à anterior é um segundo atualizador (internet, 460 MB, minutos) — a janela em que desligar deixa o Kaique na versão estragada.

### A. A verdade vem do disco, não do bilhete

A cada abertura o programa deriva o estado de três coisas que existem: (1) a versão que está rodando (`versao.VERSAO`); (2) a **última versão que passou no teste rápido** ("última boa", guardada com o pacote dela); (3) se há pacote baixado esperando (`get_update_pending_restart` do Velopack).

- Rodando ≠ última boa → versão ainda não aprovada → roda o teste rápido **nesta abertura**, em toda abertura até passar. Passou → vira a última boa (e o pacote dela é guardado). Falhou → volta (B). Mata o G1: uma volta interrompida é refeita na abertura seguinte, porque o disco ainda diz "rodando 1.2.0, última boa 1.1.0".
- Troca que não aconteceu (desligou, arquivo preso, Windows recusou) **não é falha de versão**: o pacote continua em `packages\`, o aviso volta. Só o teste rápido reprovado põe uma versão em "não tentar" (M1).
- O bilhete fica só com "versões reprovadas no teste" e "frase a mostrar uma vez". Se não puder ser gravado, o programa **continua atualizando** e registra o motivo; nunca para calado (M4, M5). A pasta do bilhete e do registro (`%ProgramData%\EditorImpressao\atualizacao`) é criada no UAC único com Usuários: Modificar (OI)(CI), uma linha a mais no passo que já existe, pela peça.
- Frases: a (1) "voltou para a anterior" só quando rodando == última boa **e** há reprovação registrada da versão seguinte — derivado, nunca anotado antes de acontecer.

### B. A volta é instantânea e sem internet

Quando uma versão passa no teste rápido, o programa guarda o pacote dela (`ultima-boa.nupkg`). A volta passa a ser `apply` desse arquivo local (pela biblioteca, com a soma conferida contra a assinatura guardada): segundos, sem rede. É a proteção da D-779 que estava na lista de espera. Custo: ~460 MB no notebook. **Decisão do Samuel pendente (recomendo sim).**

### O resto

- **M2** (janela parada até 8 s): a conferência da troca sai do fio da tela e vai para o fio de trás que já existe; a janela fecha quando a conferência termina. Linha movida, não peça nova.
- **M3** (clique sem resposta): frase genérica para todo "não deu agora": "Não deu para atualizar agora: [motivo em português]. Tente ao fechar o programa." **Decisão do Samuel pendente (recomendo sim).**
- **M6** (motor novo): **decisão do Samuel, 24/11 11:28: "vamos fazer b e colocamos isso no plano"** — (b) nesta entrega, quando uma versão pedir motor que não está no lugar, o programa mostra uma vez "Esta versão precisa de um motor novo. Avise o Samuel." e registra; **o download do motor pela internet é o primeiro trabalho depois da entrega ao Kaique**, antes de qualquer conserto do programa. Entra no plano com esse lugar.
- **M7, M9, leves 1–4:** consertos normais, cada um com teste que acusa o código de hoje.
- **M8** (título da caixa): escolha do Samuel; sugestão "Atualização".

### Quem faz

**Escritor novo** (D-815: o atual já deu duas voltas). Não é reescrever: é trocar o juiz (a abertura deriva o estado) e a volta (arquivo local). A máquina de estados fica e **perde** fases (`VOLTANDO` encurta; `TROCANDO` deixa de depender do bilhete). Sinal de gambiarra para a gerente conferir na entrega: arquivo novo, espera, cadeado, ou o `estado.json` voltando a ser consultado para decidir alguma coisa além de "não tentar" e "frase uma vez".

Depois: GitHub → quem tenta quebrar (novo) → lista com "consertado"/"deixo para depois" do Samuel (D-842) → prova à vista.

## Depois do terceiro "quem tenta quebrar" — encolher a volta automática (24/11/2026, 18:05)

Relatório lido na íntegra (`quem-tenta-quebrar-3/relatorio.md`: 1 grave, 7 médios). As duas perguntas do Fable passaram (o bilhete só decide reprovadas e frase; não sobrou volta por download). Os 8 achados estão todos em volta da **volta automática** e da **última boa** — a camada mais nova. Não é o loop antigo (nada que funcionava quebrou), mas é sinal de que a volta automática é a parte mais complicada do atualizador. Em vez de 8 consertos separados, **três regras**, aprovadas pelo Samuel ("Ok", 18:05):

1. **A volta tenta uma vez e nunca fica em laço.** O pedido de volta leva marca (`--voltando <de> <para>`), como a troca normal leva `--conferir-a-versao-nova` (D-839). A versão reaberta com essa marca **não testa de novo**: mostra a frase (3) da D-778 e abre o que der. Mata G1 e o laço do M1.
2. **Versão aprovada não é testada de novo.** Passou no teste rápido → marca no disco (`aprovada-<versao>`, ao lado da última boa) → nenhuma abertura seguinte refaz o teste. Se a guarda da nova não couber (disco), **a última boa anterior continua valendo**; nada se repete a cada abertura; conferir espaço livre antes de copiar pela mesma função que o motor usa (M4).
3. **Sem última boa, a primeira atualização acontece assim mesmo; se falhar o teste, frase (3) e para.** A primeira versão instalada pelo `.msi` **não tem volta automática** (o `.msi` não deixa o pacote em `packages\`; baixar 460 MB na primeira abertura foi a origem de M4/M5). A partir da primeira atualização que der certo, o pacote é copiado de `packages\`, sem internet, para sempre. A D-851 muda nesse sentido. (M2, M5)

Mais: **M3** — o "Sim" ao fechar que não pode trocar ganha a mesma frase do "Reiniciar agora", mostrada na abertura seguinte (D-845 vale para os dois). **M6** — a regra passa a usar o "pacote esperando" (`get_update_pending_restart`), que recebe e ignora. **M7** — os quatro testes. **M1 (dois cliques rápidos)**: com a regra 1 deixa de ser laço e vira uma frase; o resto, **"deixo para depois" do Samuel**.

**Antes de uma linha de código (volta 4, mesmo escritor, a segunda dele):** a tabela passos × jeitos de dar errado — passos: procurar, baixar, conferir, trocar, testar, guardar, voltar; jeitos: desliga no meio, Windows nega, disco cheio, sem internet, clique repetido, arquivo some, sem licença — com "o que o Kaique vê" em cada casinha. É a outra metade das colunas do teste exaustivo da máquina de estados. O "quem tenta quebrar" 4 confere a tabela contra o código.

Previsão do Fable: a rodada 4 ainda acha coisa pequena (frases, tempos). Grave e médio, com as três regras, não deveria.

## Depois do quarto "quem tenta quebrar" — a volta automática sai da primeira entrega (25/11/2026, 09:38)

Relatório lido (`quem-tenta-quebrar-4/relatorio.md`: 1 grave, 6 médios). As três regras funcionam no que miravam; os achados estão, de novo, todos na volta automática (o grave: a frase (3) depende da janela do programa, que é justamente o que a versão reprovada não abre; e a marca "sem volta" é gravada antes de a frase ser vista). Três rodadas seguidas com os defeitos na mesma funcionalidade: o custo dela não cabe na primeira entrega. O Fable reconhece que duas das peças (última boa, "uma vez só") foram emendas suas.

**Decisão do Samuel (09:34, por voz): opção A** — "é melhor a opção A; os aplicativos geralmente usam isso; a resposta fica para o Windows dar e não para o aplicativo".

### O que muda (volta 5, escritor novo — regra D-815)

1. **Sai a volta automática** desta entrega: a marca "sem volta", o "uma vez só", a segunda tentativa, o pedido `--voltando`, a fase de volta. A tabela perde a linha "Voltar" inteira.
2. **O teste rápido fica.** Se reprovar: a versão vai para "reprovadas" (bilhete) e aparece a frase **pela caixa do próprio Windows, pela peça (`MessageBoxW`)**, nunca pela janela do programa: "A versão nova não funcionou. Não desinstale nada. Avise o Samuel." Depois, o programa tenta abrir mesmo assim. **Toda frase do atualizador que pode aparecer antes da janela existir passa a ter esse caminho.**
3. **A última boa continua sendo guardada** (copiada de `packages\` depois de cada troca que passa no teste; sem internet; a primeira versão instalada não tem). Nada automático depende dela: é para a volta manual do Samuel (reinstalar, ou por SSH quando os testes à distância vierem).
4. Consertar o que sobra: **M1** (a frase "havia outra janela" não pode aparecer depois de a troca ter dado certo), **M2** (`Update.exe` que some: frase própria, sem "tente ao fechar", e o pacote é oferecido de novo quando ele voltar), **M5** (os dois testes).
5. Os testes da volta automática saem com ela; a D-718 fica no Livro como "decidida, adiada para depois da entrega", com a prova de que o programa **avisa** quando a versão nova falha.

### Fila pós-entrega (ordem a confirmar com o Samuel)
1. Download do motor do Kraken pela internet (já decidido como primeiro).
2. Volta automática (D-718), com a última boa que já existe.
3. Estrutura do programa (refatorações 1–3) e os remendos.

### Por que não se viu antes (registro, não regra)
Ninguém questionou o pedido, só o jeito de cumprir; cada peça era o mínimo honesto para "volta sozinho", então a regra contra remendos não pegava; o contador de ciclos parou no quinto em vez de no décimo. A pergunta que faltou no terceiro ciclo, e que vale quando o contador disparar de novo: **os defeitos estão sempre na mesma funcionalidade? O que o Kaique perde se ela ficar para depois?**

Contexto de mercado dado ao Samuel: Chrome, VS Code, Discord e os programas com Velopack/Squirrel não desfazem sozinhos uma versão ruim; testam antes, liberam em etapas e publicam a correção por cima. Volta automática é coisa de sistema operacional (Windows Update, Android A/B), onde não há como publicar nada se o sistema não sobe.
