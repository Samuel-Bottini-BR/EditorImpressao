# Plano da parte do Windows: atualizador e testes à distância (18/11/2026)

Plano de um implementador, só lendo e escrevendo. **Nenhuma linha do programa nem dos testes mudou.** Nenhuma janela
na tela do Samuel, nenhuma pergunta do Windows, nada instalado, nada apagado. Ramo `plano-windows-2026-11-18`.

Junta três trabalhos de hoje: a revisão do atualizador, a revisão dos testes à distância e o estudo de publicar mais
rápido, com os 7 defeitos da instalação de verdade (etapa 5). Código lido: `obra-2026-10-26` (o mesmo que as revisões
leram; de `b74a94e2` a `0e510978` só mudou o CLAUDE.md).

## Em poucas frases

1. **Fica quase tudo.** Instalar, procurar versão, a assinatura, baixar, a troca pelo ajudante, voltar de versão
   estragada, a conta de testes, entrar por SSH com senha, a prioridade baixa, atualizar de longe e todo o resto do
   programa continuam. Os planos de comandos dos testes à distância continuam num lugar só.
2. **É refeita a conversa com o Windows**: uma peça só (o "porteiro do Windows") que todo o programa usa para pedir
   licença, lançar um processo, rodar um comando, mexer em tarefa e ler como o Windows está. Ela sempre devolve uma de
   três respostas (deu certo, a pessoa disse "Não", falhou com o motivo) e nunca diz "deu certo" sem conferir.
3. **Uma pasta segura de fábrica** substitui as duas pastas do `C:\ProgramData` (a do atualizador e a dos testes), sem
   nenhum comando de licença à mão. É a mesma proposta das duas revisões, juntada numa peça só.
4. **A tela mostra o Windows, não a anotação**; a troca de versão espera o sinal de fim em vez de um relógio; a
   janela nunca congela; desinstalar limpa como o sistema, depois que o Windows avisa que o programa saiu.
5. São **8 peças**, **12 passos de trabalho**, **3 sessões de prova à vista no PC do Samuel (umas 18 perguntas do
   Windows)** e **16 decisões dele**. Tempo: de 27 a 40 h de escrita (chute), umas 4 a 5 h de provas com ele por perto,
   1 h 15 a 1 h 45 para montar as versões de prova (somado de partes medidas) e 2 a 2 h 30 de teste de confirmação.

---

## 1. O que fica e o que muda, peça por peça

### 1.1 O que fica (provado na etapa 5 ou fora da parte do Windows)

- **Instalar pelo .msi** com uma pergunta do Windows, em Arquivos de Programas (`empacotar.comando_do_vpk`, ganchos do
  Velopack). Provado.
- **Procurar a versão nova ao abrir** pelo ajudante (D-732, D-733): `procurar_e_preparar`, `Fonte`, `fonte_da_linha`.
- **A assinatura do Samuel** (`assinatura.py`, `conferir_assinatura_do`): a 1.1.4 com chave falsa foi recusada.
- **Baixar e trocar pelo ajudante, que roda como o sistema, sem pergunta** (D-733): provado de 1.1.0 a 1.1.5.
- **Voltar de uma versão estragada** (a 1.1.3 sem o Tesseract voltou sozinha) e a lista de "nunca mais tentar".
- **A conta de testes escondida, só no grupo Usuários**, e o servidor de entrar de longe do Windows (D-705, D-711,
  D-717). Os **planos de comandos** num lugar só (`core/testes_a_distancia.plano_de_ligar`, `plano_de_desligar`,
  `plano_de_desfazer`, `montar_script`), o bloco do `sshd_config` antes do "Match", a senha fora da linha de comando.
- **Entrar por SSH com senha, prioridade baixa ou normal, atualizar de longe** (D-711, D-716, D-736): provados.
- **O aviso da versão nova** com "Reiniciar agora" e "Depois" e o texto escolhido (D-715), a janelinha (D-742), o brasão
  (D-744 a D-748), a janela da senha só no programa instalado (D-728).
- **O registro lido de longe** (D-719), `registrar_falha` e `situacao` como lugar único de cada decisão.
- **O nome interno do pacote** (D-763) e o desinstalador do Velopack que apaga a pasta do título (D-764).
- **Todo o resto do programa** (telas, filtros, processamento, PDF): nada muda.

### 1.2 O que muda: as 8 peças

Cada peça mora num lugar só (CLAUDE.md §11.12). As peças 1 e 2 são a base; as outras passam a usá-las.

**Peça 1. O porteiro do Windows (uma peça só para toda conversa com o Windows).** Arquivo novo `core/windows.py`. Junta
o `_rodar_elevado` e o `aplicar_no_windows` de `core/_testes_a_distancia_windows.py` com o `_rodar`, o
`_lancar_escondido`, o `_aplicar_pacote_quando_sair`, o `criar_tarefa`, o `apagar_tarefa`, o `rodar_tarefa_agora`, o
`comando_de_rodar_a_tarefa` e o `_marca_existe` de `atualizacao.py`, e o `rodar_a_tarefa_no_windows`. Funções:
- **pedir licença** ("Deseja permitir...?"): lê o erro do jeito certo (biblioteca aberta para guardar o erro), não deixa
  o Windows mostrar a caixa crua, leva a janela do programa como dona e a traz para a frente antes, chama o PowerShell
  pelo caminho inteiro do Windows, espera com limite e nunca no fio da tela. Devolve: deu certo, disse "Não", falhou
  (com o código e a frase em português).
- **lançar solto** (o que sobrevive ao programa fechar): sem a opção que fez o PowerShell sair sem rodar, e com um
  **sinal de vida**: o processo lançado escreve "comecei" e quem lançou espera esse sinal alguns segundos. Sem o sinal,
  devolve "falhou". Uma regra só para o PowerShell e para o Update.exe.
- **rodar e esperar**: lê a resposta das ferramentas do Windows na página de letras certa ("ÊXITO", não "ÒXITO").
- **tarefas do Agendador**: criar, apagar, mandar rodar e **conferir** (existe? aponta para o lugar certo? roda como o
  sistema?).
- **a pasta de troca**: a pasta onde o programa e o script com administrador trocam arquivos nasce do jeito comum, na
  pasta da conta (que o programa lê), e é apagada no fim, com tudo dentro.
- **ler como o Windows está, sem licença**: o serviço de entrar de longe (rodando? liga com o Windows?), a conta de
  testes (ativa?), as regras do firewall (ligadas? para quais endereços?), a porta (alguém ouve?), as tarefas, a marca
  "programa aberto" e a marca "trocando" (com "acesso negado" lido como "existe", não como "não existe").
- **escrever os scripts com a marca de UTF-8** (o PowerShell do Windows lê sem a marca como outra tabela de letras) e
  mandar a senha numa codificação só dos dois lados.
- `core/_testes_a_distancia_windows.py` deixa de ter conta própria: vira chamadas do porteiro (ou some).
- **Por quê:** os 7 defeitos da etapa 5 vieram de cada função falar com o Windows do seu jeito e só pelo caminho em que
  tudo dá certo. Consertar cada linha onde está (`use_last_error`, tirar uma opção, trocar o `mkdtemp`) seria remendo:
  a próxima função repetiria o erro.

**Peça 2. A pasta segura do programa (juntada das duas revisões).** Uma pasta própria em Arquivos de Programas, **ao
lado** da pasta do programa, nunca dentro (o Velopack troca e apaga a dele). Nome técnico a escolher, que não lembre a
pasta dos projetos (D-763). No mesmo `core/windows.py`: **uma função diz onde ela é** e **uma função a cria e confere**
(é pasta de verdade, não um atalho para outro lugar; tem só as licenças que o Windows dá ali: o sistema e os
administradores mudam, as contas comuns só leem). **Nenhum comando de licença à mão.** Quem cria: sempre a pergunta de
administrador da primeira abertura (nunca o gancho de instalar, que roda sem administrador).
- **Vai para lá:** do atualizador, o estado, o registro do ajudante, a cópia para voltar, o sinal "trocando", o socorro
  (peça 4) e a marca do preparo; dos testes à distância, o script do desfazer, o caderninho do antes e a marca "a janela
  da senha já apareceu neste computador"; o arquivo da fonte de teste (só para as provas; só vale se o dono for
  administrador, como hoje).
- **A janela do Kaique só lê ali.** O que ela anota vai para a pasta da conta dela.
- `C:\ProgramData\EditorImpressao` deixa de existir. O gancho de instalar (`atualizacao.ao_instalar`) não grava nada fora
  da pasta da conta.
- Arquivos: `core/windows.py` (novo), `atualizacao.py` (`pasta_do_estado`, `caminho_do_registro`, `registrar`,
  `arquivo_do_preparo`, `caminho_da_fonte_de_teste`, `ao_instalar`), `core/testes_a_distancia.py`
  (`caminho_do_antes`, `caminho_do_script_do_desfazer`, `caminho_do_registro_do_desfazer`,
  `_comando_criar_e_proteger_a_pasta`, `_comando_proteger_a_pasta` sai).
- **Por quê:** a tranca feita à mão deixou os arquivos sem licença nenhuma (provado: lista vazia), e a pasta do
  ProgramData deixa qualquer conta criar arquivos onde o sistema grava e roda script (licença provada). Uma chave do
  registro do Windows serviria só para dados pequenos; a cópia de 788 MB e os scripts precisam de pasta.

**Peça 3. Perguntar ao Windows como está (conferir em vez de lembrar).**
- **Atualizador:** "o computador está preparado" passa a ser a resposta do Windows: a tarefa do ajudante existe, aponta
  para o socorro certo, roda como o sistema e a pasta segura confere. Sai a marca `atualizacao_computador_preparado` das
  Configurações. Leva menos de 1 s, sem pergunta. Resolve o "Não" que vira "preparado", a pergunta que não volta
  (D-741, D-749) e o reinstalar sem ajudante.
- **Testes à distância:** uma função "como está agora" lê o serviço, a conta, a regra e a porta e devolve uma de quatro
  situações: Desligado · Ligado · Ligado pela metade (com o que falta) · Não deu para saber. Roda ao abrir as
  Configurações e depois de cada ligar e desligar. A anotação das Configurações guarda só o que é da pessoa ("o Kaique
  quer ligado?").
- Arquivos: `atualizacao.py` (`falta_a_pergunta_do_windows`, `preparo_deu_certo`, `CHAVE_PERGUNTA_DO_WINDOWS_RESPONDIDA`),
  `core/testes_a_distancia.py` (`esta_ligado`, `esta_pronto`, `senha_ja_perguntada`, `marcar_senha_perguntada`, `ligar`,
  `desligar`), `configuracoes.py` (as chaves `testes_a_distancia_pronto` e a do preparo).

**Peça 4. A troca de versão (o jeito de chamar a troca, o socorro, os avisos).**
- **Um jeito só de pedir a troca**, para o "Reiniciar agora", o "Depois" e o atualizar de longe: a janela lança solto
  (peça 1) um PowerShell pequeno, fora da pasta do programa, que mostra a janelinha, espera a janela fechar, manda o
  ajudante rodar e **espera o sinal de fim** que o ajudante escreve na pasta segura ("troca começou / terminou bem /
  voltou / falhou"). Só então reabre o programa. O limite de segurança é medido (a troca leva 7 a 23 min), não os 5 min
  de hoje (`LIMITE_DA_TROCA_S = 300`).
- **Marca "trocando":** o ajudante a segura do começo ao fim da troca. O programa, logo ao abrir (antes de carregar
  qualquer coisa), olha essa marca; se ela existe, não abre por cima da troca (o Velopack fecharia à força): mostra a
  janelinha e abre quando a troca acaba (decisão 3).
- **Falha passageira não é falha:** sem internet, tempo esgotado, disco cheio, arquivo preso, notebook desligado no
  meio: tenta de novo na próxima vez, sem aviso e sem riscar a versão. Só riscam e avisam: assinatura que não confere,
  pacote estragado, teste rápido que falha.
- **O socorro mora fora do que é trocado:** antes de trocar, o ajudante guarda no disco a versão de hoje (o pacote que o
  Velopack já tem); a volta deixa de baixar da internet. A tarefa do ajudante passa a chamar um script pequeno na pasta
  segura, que roda o programa, confere a versão nova com limite de tempo e, se ela nem abrir, aplica a versão guardada.
  Assim uma versão que nem abre não mata a atualização.
- **O aviso diz o que aconteceu** (decisão 10): uma frase para cada caso, escolhida pelo mesmo `registrar_falha`; marcado
  como visto só depois de aparecer.
- **O aviso de versão nova aparece logo que a versão termina de baixar**, em vez de até 5 min depois (a janela olha o
  estado da pasta segura com mais frequência; é só leitura de um arquivo pequeno).
- **A janela do Kaique nunca cria o Velopack:** a versão que roda vem do arquivo de versão que o próprio pacote traz;
  "é portátil" é o arquivo que o Velopack põe ao lado do Update.exe; o Velopack só roda na janela quando a linha de
  comando traz um gancho dele. Assim não nasce `%LOCALAPPDATA%\EditorImpressaoPrograma`, e um erro do Velopack não
  desliga a atualização em silêncio.
- **Quando a versão entra com "Depois"** (decisão 2) e **a janelinha em toda troca** (decisão 3).
- Arquivos: `atualizacao.py` (`procurar_e_preparar`, `situacao`, `registrar_falha`, `o_que_avisar`,
  `conferir_assinatura_do`, `voltar_para_a_anterior`, `conferir_versao_nova`, `rodar_ao_ligar`, `script_de_trocar_e_reabrir`,
  `script_da_janelinha`, `trocar_e_reabrir`, `aplicar_agora_e_reabrir`, `trocar_antes_de_abrir`, `versao_que_roda`,
  `e_portatil`, `_rodar_o_velopack`, `xml_da_tarefa`, `conferir_e_refazer_o_ajudante`), `ui/aviso_de_atualizacao.py`,
  `main.py` (o começo).

**Peça 5. Ligar e desligar os testes à distância (tudo ou nada, relatório sempre lido).**
- **O relatório volta sempre:** o script escreve passo a passo na pasta de troca (peça 1), dá leitura à conta que pediu, e
  o programa lê e mostra, deu certo ou não. Código de saída sozinho não decide.
- **Tudo ou nada** (decisão 4): o ligar anota o que cada passo fez nesta vez; se um falha, o próprio script desfaz, de
  trás para frente, só o que fez nesta vez. O desligar tenta todos os passos e diz o que ficou.
- **A preparação da atualização e o ligar dos testes ficam separados dentro do script**: a falha de um não apaga o
  resultado do outro.
- **A senha:** a mesma codificação dos dois lados; conferida antes, sem licença, nas regras de senha do Windows daquele
  computador; e a cifra vale para o computador, num arquivo que só a conta e os administradores leem, apagado logo
  depois (assim funciona mesmo se quem disser "Sim" for outro administrador).
- **Segunda tranca no próprio servidor:** só a conta de testes, e só vinda de endereço do Tailscale (vale mesmo com o
  firewall do Windows desligado ou trocado pelo de um antivírus). O bloco vai no começo do `sshd_config`, e depois de
  reiniciar o serviço o programa confere com o próprio servidor que a regra valeu.
- **Antes de ligar:** conferir se a porta já está ocupada e dizer por qual programa; avisar que a peça vem da internet e
  pode levar até 15 min (decisão 5).
- **Os nomes dos passos sem número de decisão** (vão aparecer na tela): tira o "(D-731)" e os outros dos textos de
  passos e do registro (Lista de bugs de 17/11; D-687).
- Arquivos: `core/testes_a_distancia.py` (`plano_de_ligar`, `plano_de_desligar`, `plano_de_desfazer`,
  `plano_de_preparar_o_desfazer`, `montar_script`, `_comando_por_o_bloco`, `_comando_anotar_o_antes`,
  `_comando_preparar_o_desfazer`, `ligar`, `desligar`, `mandar_desfazer`, `ExecutorWindows`).

**Peça 6. A tela dos testes à distância e a primeira abertura sem congelar.**
- A pergunta do Windows e a preparação da primeira abertura saem de antes do laço da janela (`main.py`) e rodam por
  trás, com a janela respondendo e uma janelinha "Esperando o Windows. Isto pode levar até 15 minutos." Vale também para
  o ligar e o desligar das Configurações (hoje a janela fica parada até 14 min).
- **Configurações > Testes à distância** mostra a situação lida do Windows (peça 3), com a frase do que ficou ligado
  quando algo falha (decisão 4). Na janela da senha, os dois campos se ele quiser (decisão 13).
- Arquivos: `main.py`, `ui/testes_a_distancia_ui.py` (`primeira_vez_se_preciso`, `pedir_senha_e_ligar`, a janela da
  senha), `ui/tela_configuracoes.py` (`_mostrar_estado_dos_testes`, `_mudou_testes_a_distancia`,
  `_por_a_senha_dos_testes`).

**Peça 7. Desinstalar limpo, como o sistema.**
- Uma tarefa de limpeza nasce na primeira abertura (na mesma pergunta), roda como o sistema e é disparada pelo aviso
  do próprio Windows de que o programa foi removido. **Antes de agir, confere** que o programa saiu mesmo (se foi uma
  instalação por cima, o programa continua registrado e ela não faz nada).
- Ela roda o desfazer dos testes à distância (o servidor, se foi o programa que pôs; a regra; a conta e o perfil dela),
  apaga as tarefas do programa, a pasta segura e as sobras do Velopack em cada conta. **Nunca toca os projetos.**
  Termina conferindo, e a lista do que tirou vai para o registro de eventos do próprio Windows (que qualquer conta lê e
  não deixa arquivo no disco).
- Se o Windows segurar a pasta da conta de testes (aconteceu na etapa 5), ela tenta de novo uma vez, na próxima vez que
  o computador ligar, e depois se apaga.
- O gancho de desinstalar do Velopack (sem administrador, 30 s) deixa de ser quem limpa.
- Arquivos: `atualizacao.py` (`ao_desinstalar`, `criar_as_tarefas`, `_passos_das_nossas_tarefas` vindo de
  `core/testes_a_distancia.py`), `core/testes_a_distancia.py` (`plano_de_desfazer`, `xml_da_tarefa_do_desfazer`).
- Cumpre a D-731 como ele decidiu ("o computador fica como era antes de instalar"); não precisa de pergunta nova.

**Peça 8. Publicar (no PC do Samuel).**
- **Uma função só roda o vpk**, com a pasta de trabalho e a pasta temporária certas, chamada pelos dois caminhos que hoje
  rodam cada um do seu jeito (`publicar_versao_kaique.publicar` e `empacotar.construir_pacote_do_velopack`). Confere o
  espaço livre antes.
- **No disco de dentro** (decisão 8) e **sem o .msi e sem o zip portátil nas versões de atualização** (decisão 9).
- **Sem a diferença, ou com a diferença assinada** (decisão 1).
- **No GitHub, nunca pela metade:** sobe como rascunho, sobe a assinatura, confere lendo de volta do GitHub, e só então
  libera.
- **Um número de versão só:** recusa uma pasta pronta de outra versão, cobra o Visual C++ dentro da pasta pronta e anota
  de que commit a versão saiu.
- Arquivos: `publicar_versao_kaique.py`, `empacotar.py` (`comando_do_vpk`, `construir_pacote_do_velopack`), e
  `assinatura.py` se a decisão 1 for "diferença assinada".

### 1.3 Além do combinado (o que mexe em coisa que já funcionou, e por quê)

A gerente disse ao Samuel que fica o que funcionou e é refeita a peça que fala com o Windows, a tela dos testes à
distância e o jeito de chamar a troca. Cinco pontos do plano passam disso. Cada um está aqui separado, com o porquê.

1. **O socorro muda por onde a troca pelo ajudante entra** (peça 4). A troca pelo ajudante funcionou, mas quem confere a
   versão nova e volta é a própria versão nova. Uma versão que nem abre (nunca testada) deixaria o Kaique sem programa e
   sem atualização. E a volta hoje baixa da internet. Sem isso, o "voltar de versão estragada" só funciona quando a
   estragada ainda abre.
2. **O estado e o registro do atualizador saem do ProgramData** (peça 2). Funcionavam, mas qualquer conta (inclusive a
   de testes) pode criar arquivos onde o sistema grava. Fere a D-717 ("um teste não consegue mudar o Windows").
3. **A janela do Kaique deixa de usar o Velopack para saber a versão** (peça 4). Funcionava, mas é a causa da pasta que
   sobra na conta e do erro que desliga a atualização em silêncio.
4. **O publicar** (peça 8) não é a conversa com o Windows: é a conversa com o GitHub e o Velopack, que a regra nova
   (§11.12, ponto 1) também cobre. Entra porque um defeito dele atinge o Kaique (a versão liberada antes da assinatura
   fica recusada para sempre) e porque o Samuel pediu publicar rápido ("as atualizações deveriam ser rapidas").
5. **A assinatura** (`assinatura.py`, que funcionou) só muda se ele escolher manter a diferença assinada (decisão 1).

**O que fica de fora de propósito:** os outros lugares que abrem programas de fora (os motores de achar texto, o
servidor de páginas, o brasão girando, o `--conferir-ocr`). Pela regra nova eles também deveriam passar por uma peça
só, mas não falharam, não pedem licença nem mexem no Windows, e a D-765 deixa os consertos para depois da entrega.
Sugestão: uma leitura só de procura, depois da entrega ao Kaique.

### 1.4 Como fica para quem usa (o Kaique) e no livro

- **Primeira abertura:** a janela da senha, depois uma janelinha "Esperando o Windows..."; a pergunta do Windows aparece
  no meio da tela; a janela do programa continua respondendo. Se ele clicar "Não", aparece "Nada mudou" e a pergunta
  volta na próxima abertura (D-741).
- **Versão nova:** o aviso aparece logo que ela chega. "Reiniciar agora" mostra a janelinha até o programa voltar na
  versão nova. Clicar no atalho no meio da troca mostra a janelinha, em vez de o programa sumir.
- **Falha:** o aviso diz o que aconteceu de verdade. Falha passageira não mostra nada.
- **Configurações > Testes à distância:** a frase diz o que o computador tem de verdade.
- **Desinstalar:** o notebook fica como era; os projetos ficam.
- **Nada muda nos livros nem no PDF.**

---

## 2. A lista completa dos defeitos (sem repetição)

De onde veio: **etapa 5** (instalação de verdade), **revisão do atualizador**, **revisão dos testes**, **estudo do
publicar**, **Lista de bugs**. "Provado" = visto no Windows de verdade; "lido" = lido no código ou na documentação.
Cada um diz a peça que o resolve. Os que fecham juntos estão no mesmo número.

**Pedir licença ao Windows**
1. "Não" ou falha na pergunta do Windows vira "deu certo" e "computador preparado"; a pergunta não volta (etapa 5,
   defeito 2; as duas revisões; Lista de bugs 18/11). Provado. **Peças 1 e 3.**
2. A caixa crua do Windows "Não há suporte para o pedido" (etapa 5, fase 3.1; as duas revisões). Provado. **Peça 1.**
3. A pergunta não aparece no meio da tela quando o programa não está na frente; o pedido vai sem janela dona (etapa 5,
   defeito 7; as duas revisões). Visto; onde ela foi não está provado. **Peças 1 e 6.**
4. A janela congela enquanto o Windows trabalha (primeira abertura: 91 s; ligar: 14 min); a espera não tem limite; o
   trabalho roda antes do laço da janela, e por isso um "fechar" se perdeu (etapa 5, "o programa não terminou";
   revisão do atualizador, novo 11; revisão dos testes, N2). Lido e pelos horários. **Peças 1 e 6.**
5. O PowerShell é chamado só pelo nome, sem o caminho inteiro (revisão dos testes). Lido. **Peça 1.**
6. A pergunta mostra "Windows PowerShell", não "Editor de Impressão" (revisão dos testes, N12). É como o Windows mostra.
   **Decisão 14; peça 1.**
7. Se quem disser "Sim" for outro administrador (conta do Kaique sem poder de administrador), a senha cifrada pela conta
   dele não abre (revisão dos testes, 1.1 e 1.2). Lido; caso raro. **Peças 1 e 5.**

**Lançar um processo e ler a resposta**
8. O PowerShell lançado solto sai sem rodar: "Reiniciar agora" fecha e não volta; com uma versão esperando, o programa
   não abre (etapa 5, defeito 1; revisão do atualizador 1.1; Lista de bugs 18/11). Provado. **Peças 1 e 4.**
9. Duas regras para lançar solto (o PowerShell e o Update.exe da volta) (revisão do atualizador 1.2). Lido. **Peça 1.**
10. A resposta das ferramentas do Windows é lida na tabela de letras errada ("ÒXITO" no registro) (revisão do
    atualizador 1.3). Provado. **Peça 1.**
11. O script é gravado sem a marca de UTF-8, e o PowerShell do Windows o lê com outra tabela de letras: um texto com
    acento dentro do script pode chegar trocado (achado desta leitura). Lido, não provado. **Peça 1.**
12. As frases dos códigos do Windows Installer (1618, 1603) não vão em português para o registro (revisão do
    atualizador 1.10). Lido; menor. **Peça 1.**

**Pastas e licenças**
13. O programa não consegue ler o relatório do script com administrador (a pasta temporária do Python 3.14 nasce só para
    o dono): aviso genérico e "falta a senha" com 8 de 9 passos feitos (etapa 5, defeito 3; as duas revisões; Lista de
    bugs 18/11). Provado. **Peças 1 e 5.**
14. A tranca da pasta dos testes deixa os arquivos de dentro sem licença nenhuma; daí o último passo do ligar, o desligar
    e o desfazer falham para sempre (etapa 5, defeito 4; revisão dos testes, causa provada e N1). Provado. **Peça 2.**
15. A pasta do ProgramData deixa qualquer conta criar arquivos onde o sistema grava e roda script; a pasta-mãe é da conta
    de quem instalou (revisão do atualizador, novo 10; revisão dos testes, N11). Licença provada; o desvio é lido. **Peça 2.**
16. Cada pedido deixa no TEMP uma pasta que o Kaique não consegue apagar (revisão dos testes, N9). Provado (restos da
    etapa 5). **Peça 1.**

**O que a tela mostra**
17. Desligar diz "Desligado" sem desligar; grava "desligado" sempre, até com "Não"; não avisa nada; para no primeiro erro
    (etapa 5, defeito 5; revisão dos testes, N4 e N5; Lista de bugs 18/11). Provado. **Peças 3, 5 e 6.**
18. "Pronto" nunca volta a "não" (revisão dos testes, N8). Lido. **Peça 3.**
19. A anotação é por conta do Windows, mas o que liga é do computador inteiro: noutra conta a tela diz errado e a janela
    da senha pode trocar a senha da conta de testes (revisão dos testes, N7). Lido. **Peças 2 e 3.**
20. "Ligado, mas falta a senha" aparece para qualquer falha, mesmo com tudo ligado (etapa 5, fase 7; revisão dos
    testes 1.14). Provado. **Peças 3 e 6.**
21. Reinstalar deixa o programa sem atualização para sempre (a marca "preparado" fica nas Configurações) (revisão do
    atualizador, novo 7). Lido. **Peça 3.**
22. A preparação da atualização e o ligar dos testes vão no mesmo script: a falha de um apaga o resultado do outro
    (revisão dos testes 1.13). Lido. **Peça 5.**

**Ligar os testes à distância**
23. Ligar que falha no meio não desfaz nada nem diz o que ficou (etapa 5, fase 7; revisão dos testes, N6). Provado o
    sintoma. **Peça 5; decisão 4.**
24. Senha com acento ou cedilha vira outra senha (revisão dos testes, N3). Provado com um texto de exemplo. **Peças 1 e 5.**
25. A senha não é conferida nas regras de senha do Windows antes (revisão dos testes 1.2). Lido. **Peça 5.**
26. Uma letra errada na senha não tem como ser vista (revisão dos testes, N13). **Decisão 13.**
27. A peça de entrar de longe vem do Windows Update na hora de ligar: sem internet não liga; levou 13 min; com o Windows
    Update desligado falha (revisão dos testes 1.5). Medido o tempo. **Peça 5; decisão 5.**
28. A porta já ocupada por outro programa impede o servidor de subir (revisão dos testes 1.6). Lido. **Peça 5.**
29. Nada prova que só o Tailscale entra; sem o firewall do Windows a porta fica aberta para o Wi-Fi; a regra presa à
    placa "Tailscale" pode deixar de valer (revisão dos testes, N10 e 1.7). Lido. **Peça 5; decisão 12.**
30. Um `sshd_config` do dono com um valor antes do nosso bloco vence o nosso (só no computador que já tinha o servidor)
    (revisão dos testes 1.9). Lido. **Peça 5.**
31. A tarefa "desfazer" não é conferida depois de criada (revisão dos testes 1.10). Lido. **Peças 1 e 7.**
32. Números de decisão nos textos dos passos e do registro, que vão aparecer na tela (Lista de bugs 17/11). Lido. **Peças 4 e 5.**

**Trocar de versão**
33. "Reiniciar agora" espera só 5 min, e a troca leva de 7 a 23 (revisão do atualizador, novo 3; etapa 5, item 8).
    Medido. **Peça 4.**
34. Abrir o programa durante a troca: o Velopack o fecha à força, o programa acusa uma falha que não houve e a versão
    fica riscada (revisão do atualizador, novo 4 e 1.12). Lido. **Peça 4; decisão 3.**
35. Quem socorre é a própria versão nova: uma versão que nem abre deixa o programa sem volta e sem atualização (revisão
    do atualizador, novo 5). Lido. **Peça 4.**
36. A volta depende da internet, e o aviso diz "voltou" antes de saber (revisão do atualizador, novo 6). Lido. **Peça 4.**
37. Internet que pisca ao ler a assinatura vira "recusada para sempre" e "a atualização não deu certo" (revisão do
    atualizador, novo 1 e 1.14). Lido. **Peça 4.**
38. Falha passageira na troca (arquivo preso, notebook desligado no meio, disco cheio) vira falha para sempre (revisão
    do atualizador, novo 13). Lido. **Peça 4.**
39. Um erro do Velopack na conta do Kaique desliga a atualização em silêncio (revisão do atualizador, novo 12). Lido.
    **Peça 4.**
40. O Velopack é criado na conta do Kaique e deixa `%LOCALAPPDATA%\EditorImpressaoPrograma` depois de desinstalar
    (etapa 5; revisão do atualizador 1.11; D-764). Provado. **Peças 4 e 7.**
41. O aviso de falha tem a mesma frase em três casos e em dois ela não é verdade (revisão do atualizador). Lido.
    **Peça 4; decisão 10.**
42. O aviso de falha é marcado como visto antes de aparecer (revisão do atualizador, menores). Lido. **Peça 4.**
43. O aviso de versão nova pode levar até 5 min para aparecer (etapa 5, item 8). Medido. **Peça 4.**
44. Pela diferença ("só o que mudou"), a troca no notebook leva 22 a 23 min, contra 7,5 min pela versão inteira (estudo
    do publicar; etapa 5, item 8). Medido. **Peça 8; decisão 1.**
45. Se a segunda troca de pastas do Velopack falhar, o programa fica sem a pasta dele e não abre, não atualiza nem
    desinstala (Velopack 1.2.161; conserto só na prévia) (revisão do atualizador 1.12). Lido. **Peça 4; decisão 11.**
46. Pela diferença, a assinatura do Samuel não confere o que é instalado (estudo do publicar; revisão do atualizador;
    Lista de bugs 18/11). Lido, não provado. **Peça 8; decisão 1.**

**Desinstalar**
47. Desinstalar não tira o servidor de entrar de longe, a conta nem a regra (etapa 5, D-731 não cumprida; revisão dos
    testes, N1). Provado; a causa é o 14. **Peças 2 e 7.**
48. Desinstalar deixa as duas tarefas do Windows, uma apontando para um programa que não existe (revisão do atualizador,
    novo 8). Provado. **Peça 7.**
49. Desinstalar deixa `C:\ProgramData\EditorImpressao` (789 MB) (revisão do atualizador, novo 9). Provado. **Peças 2 e 7.**
50. O gancho de desinstalar roda sem administrador e com 30 s: "apagar a tarefa: Acesso negado" (etapa 5, fase 11;
    revisão do atualizador 1.5 e 1.13). Provado. **Peça 7.**
51. O perfil da conta de testes fica preso depois de apagar a conta (etapa 5, defeito 6). Provado. **Peça 7.**
52. Ninguém vê o resultado do desfazer (revisão dos testes 1.12). Lido. **Peça 7.**

**Publicar**
53. No GitHub, a versão é liberada antes de a assinatura subir (revisão do atualizador, novo 2). Lido. **Peça 8.**
54. A pasta pronta publica uma pasta de outra versão ("versão 1.1.0" em todas as linhas de uma 1.1.5) e não cobra o
    Visual C++ dentro dela (etapa 5; revisão do atualizador 1.16). Provado no registro. **Peça 8.**
55. Publicar leva de 70 a 93 min por versão: todo o trabalho no HD externo, a pasta copiada quatro vezes, o .msi e o
    portátil refeitos a cada versão (estudo do publicar; Lista de bugs 18/11). Medido. **Peça 8; decisões 8 e 9.**
56. Dois caminhos rodam o vpk cada um do seu jeito, e a pasta temporária foi desviada à mão (estudo do publicar). Lido.
    **Peça 8.**
57. Numa cópia do projeto, o empacotador procura o motor do Kraken e o Visual C++ numa pasta que não existe ali (etapa 5,
    "outras coisas"). Lido; só no PC do Samuel. **Peça 8.**

**Ficam fora, com o porquê**
58. O motor do Kraken (98% dos arquivos, nunca muda) entra em toda versão (estudo do publicar). Só ele encurta a troca
    de 7,5 min; é mudança grande de instalação. **Fica para depois (decisão 16).**
59. O disco D: do Samuel aberto para qualquer conta, por isso a conta de testes gravou nele (etapa 5, D-717 pela metade).
    É do disco, não do programa; já decidido (D-743: conferir os discos do Kaique antes do primeiro teste).
60. A foto da primeira pergunta do Windows não foi tirada (etapa 5, D-737). Não é defeito do programa: a pergunta fica
    na área segura do Windows e não sai em print.
61. O antivírus e as regras de proteção do Windows podem barrar um PowerShell escondido; uma política de computador de
    empresa pode proibir scripts (as duas revisões). Não se sabe no notebook do Kaique. **Riscos (seção 6).** A peça 1
    diminui o risco: script em arquivo, nada em texto codificado na linha de comando.
62. O "Controle Inteligente de Aplicativos" do Windows 11 pode bloquear o programa sem certificado pago (revisão do
    atualizador 1.17). **Decisão 15** (conferir no notebook antes).
63. A fonte de teste é uma peça de teste dentro do programa do Kaique (revisão do atualizador 1.9). Fica, documentada,
    na pasta segura; só o administrador a cria e a assinatura continua valendo.

---

## 3. A ordem do trabalho

Regras de todas as provas (D-767): no PC do Samuel, **na área de trabalho de verdade, nunca escondida, nenhuma janela
empurrada para fora da tela**; cada prova abre uma janela pequena de PowerShell visível que diz o que está fazendo e
mostra o resultado; ela roda **o código de verdade** da peça (importado do programa, não uma cópia); nada de peça de
mentira no lugar do Windows; ele clica "Sim" quando a pergunta aparece; antes de cada sessão a gerente diz a ele o que
vai aparecer. Os testes automáticos continuam para a lógica em volta, mas não contam como prova destas peças.

**Passo 0. As decisões do Samuel** (seção 5). Nada se escreve antes das decisões 1 a 7. As outras podem chegar durante a
escrita. Tempo dele: uns 20 a 30 min de leitura e resposta.

**Passo 1. Escrever o porteiro do Windows e a pasta segura** (peças 1 e 2), com a lista das falhas de cada função no
ONDE-PAREI antes (CLAUDE.md §11.12, ponto 3) e os testes da lógica em volta. Nenhum chamador muda ainda. Escrita: 5 a 7 h
(chute).

**Passo 2. Sessão de provas A, no PC do Samuel, sem o programa instalado.** Uma sentada, umas 25 a 30 min, **3 perguntas
do Windows.** Um script de prova visível chama as funções de verdade do porteiro:
- lançar solto: a janela de prova mostra "o processo lançado rodou às HH:MM:SS", também depois de quem lançou já ter
  fechado (0 perguntas);
- pergunta 1, "Sim": a janela mostra "rodou como administrador"; no mesmo "Sim", o script cria a pasta segura e mostra a
  licença que o Windows deu, sem comando de licença; cria uma tarefa de prova que roda como o sistema; a conta comum lê
  a pasta e tenta criar um arquivo ("recusado"), manda a tarefa rodar e a janela mostra "o sistema leu e gravou"; a
  conferência diz "tarefa existe: sim"; uma senha de prova com acento (não é a dos testes) chega igual do outro lado
  (comparada pela soma, nunca escrita); um texto com acento dentro do script chega igual;
- pergunta 2, "Não": a janela mostra "você disse Não; nada mudou" (o código lido certo);
- pergunta 3, com outra janela na frente (o navegador dele), "Sim": a pergunta aparece no meio da tela, não piscando na
  barra; esse "Sim" apaga a tarefa e a pasta de prova, e a conferência diz "tarefa existe: não";
- um pedido para um arquivo que não existe: frase em português, sem a caixa crua (0 perguntas);
- uma linha com resposta do Windows aparece com "ÊXITO" certo (0 perguntas).
O que ele vê: a janela de prova com uma linha por prova, e as 3 perguntas do Windows. Se a pergunta 3 não aparecer no
meio da tela, o plano para e a gerente leva o resultado a ele antes de seguir (risco 1).

**Passo 3. O atualizador passa a usar o porteiro** (peças 3 e 4): o preparado conferido no Windows, a troca com sinal de
fim e marca "trocando", o socorro fora da pasta trocada, falha passageira, os avisos, a janela sem Velopack. O socorro
leva antes um plano curto próprio, porque mexe no que o ajudante roda. Escrita: 8 a 12 h (chute).

**Passo 4. Os testes à distância e a tela passam a usar o porteiro** (peças 3, 5 e 6): tudo ou nada, relatório lido,
senha, segunda tranca, "como está agora", a primeira abertura e as Configurações sem congelar. Escrita: 6 a 9 h (chute).

**Passo 5. Desinstalar limpo** (peça 7). Escrita: 3 a 4 h (chute).

**Passo 6. Publicar** (peça 8). Prova: é o próprio passo 8 (medido) e, se ele disser sim na decisão 6, uma versão de
teste no GitHub como rascunho, lida de volta, liberada só para a prova e apagada no fim (0 perguntas). Escrita: 2 a 3 h
(chute).

**Passo 7. Testes antigos e rodada do GitHub.** Os testes antigos da seção 4.2 mudam só com o "sim" dele (decisão 7).
Rodada inteira no GitHub e as provas das decisões. Escrita e espera: 2 a 4 h (chute).

**Passo 8. Montar as versões de prova** com o publicar novo, num servidor de prova visível (decisão 6): a primeira, com
o .msi; uma boa para a troca; uma que nem abre (o programa quebrado de propósito); uma com a assinatura de uma chave
falsa (o mesmo pacote de uma boa, com outra assinatura); outra boa para o atualizar de longe. Tempo: 1 h 15 a 1 h 45
(somado das partes medidas no estudo; a soma não foi medida junta). Sem o publicar novo: uns 4 a 5 h (a etapa 5 mediu
6 h 47 para seis versões).

**Passo 9. Sessão de provas B, o atualizador, com o programa instalado.** Uma sentada, 1 h 30 a 2 h, **4 perguntas do
Windows.**
- pergunta 1: a foto do computador com administrador, e no mesmo "Sim" a fonte de teste aponta para o servidor de prova;
- pergunta 2: instalar pelo .msi, com a barra do instalador na tela;
- primeira abertura, pergunta 3, ele clica **"Não"**: aparece "Nada mudou"; a janela de prova lê do Windows "preparado:
  não"; fechar e abrir: a pergunta volta;
- pergunta 4, **"Sim"**: enquanto o Windows trabalha, ele arrasta a janela e ela responde; a janela de prova lê "preparado:
  sim" do Windows;
- versão nova, "Reiniciar agora": a janelinha aparece o tempo todo e o programa volta na versão nova; medir quanto levou
  (0 perguntas, ~10 min);
- versão nova, "Depois" (do jeito que ele escolher na decisão 2): a versão entra quando a decisão diz (0, ~10 min);
- no meio de uma troca, ele clica no atalho: a janelinha aparece, nada é fechado à força, o programa abre no fim (0, ~10 min);
- falha passageira: a janela do servidor de prova é fechada na hora de ler a assinatura (o teste avisa a hora): nenhum
  aviso; reabrir o servidor e o programa: a versão entra (0, 5 min);
- a versão que nem abre: o socorro volta para a anterior sem internet e o aviso certo aparece (0, ~15 min);
- a assinatura falsa: recusada antes de baixar, com a frase certa (0, 2 min).
O que ele vê: o instalador, o programa na tela, a janelinha, os avisos, a janela de prova com o que o Windows responde.

**Passo 10. Sessão de provas C, os testes à distância, desinstalar e reinstalar.** Uma ou duas sentadas, 1 h 45 a
2 h 15, **10 perguntas do Windows.**
- Configurações abertas: "Desligado" lido do Windows (0);
- pergunta 1: ligar com a porta ocupada de propósito por uma janela visível (uma falha de verdade do Windows, sem tirar
  a internet do PC): o programa diz qual programa usa a porta e não deixa nada ligado; a janela de prova confere (5 min);
- pergunta 2: ligar de verdade, com a senha dele digitada direto no programa; a janela não para; a janelinha diz quanto
  pode demorar; depois "Ligado" lido do Windows; ele entra pela janela de entrar de longe (15 a 20 min);
- só o Tailscale entra: do celular com o Tailscale entra; do celular só no Wi-Fi, não (só se ele disser sim na decisão
  12; 0 perguntas, 10 min);
- prioridade baixa e atualizar de longe, de novo, para conferir que nada do que funcionava mudou (D-605) (0, ~20 min com
  a troca);
- pergunta 3, desligar com **"Não"**: a tela continua "Ligado" (0 mudanças);
- pergunta 4, desligar com **"Sim"**: "Desligado" só quando o Windows confirma;
- pergunta 5: ligar de novo com uma senha nova: a nova entra, a velha não;
- pergunta 6: desinstalar pelas Configurações do Windows, como o Kaique faria, com os testes ligados; depois a janela de
  prova lista o que saiu (servidor, conta, perfil, regras, tarefas, pasta segura, sobras do Velopack) e que os projetos
  são os mesmos arquivos;
- perguntas 7 e 8: reinstalar e abrir: a pergunta do Windows volta e o ajudante nasce;
- pergunta 9: desinstalar de novo, para o PC ficar limpo;
- pergunta 10: a foto final com administrador, comparada com a do começo da sessão B.
Se ele quiser, uma prova a mais: instalar uma versão nova por cima da instalada e ver que a limpeza não age (+1
pergunta, 10 min).

**Passo 11. Relatório das provas** nos três formatos, com cada print ao lado das palavras dele da decisão, e a lista do
que foi desfeito no PC dele (D-722). Tempo: 1 h.

**Passo 12. Teste de confirmação** com a versão que vai para o Kaique: montar a versão final com o .msi (~30 min) e
repetir a etapa 5 curta, à vista: instalar, primeira abertura, uma atualização, ligar, entrar de longe, atualizar de
longe, desligar, desinstalar, foto. **5 a 6 perguntas do Windows**, 1 h 30 a 2 h.

**Juntando:** 3 sessões de prova (umas 18 perguntas do Windows) mais a confirmação (5 a 6). As revisões, somadas e
sem juntar, pediam umas 25 perguntas só nas provas; o plano junta a instalação, a foto e a fonte de teste numa
sentada só, e usa o desinstalar com os testes ligados para provar o atualizador e os testes de uma vez.

---

## 4. O que muda em decisões já tomadas e em testes antigos

### 4.1 Decisões (D-605: nada muda sem o "sim" dele)

- **D-723** ("Velopack: baixa só o que mudou, então a atualização é rápida", a explicação com que ele escolheu): o Velopack
  fica. O plano propõe publicar **sem a diferença** (o Kaique baixa a versão inteira, 826 MB) ou **com a diferença
  assinada**. Decisão 1.
- **D-734** (com "Depois", a versão entra na próxima abertura, "com uma espera curta antes da janela aparecer"): a espera
  medida é de 7,5 min (versão inteira) ou 22 min (diferença), não curta. O plano propõe escolher de novo: na próxima
  abertura, como hoje, ou ao fechar o programa. Decisão 2.
- **D-742** (a janelinha "Atualizando o programa, espere um pouco..." só na abertura depois do "Depois"; "alguns
  segundos, até 5 minutos"): o plano propõe a janelinha em toda troca (também depois do "Reiniciar agora" e quando ele
  clica no atalho no meio da troca), e o limite de 5 min trocado pelo sinal de fim. Decisão 3.
- **D-720** ("Reiniciar agora" e "Depois"): os botões e o texto ficam; só muda o que acontece depois (decisões 2 e 3).
- **D-712 e D-721** (o estado nas Configurações: "Ligado", "Ligado, mas falta a senha", "Desligado"): o plano propõe
  as frases lidas do Windows e, se algo falhar, a frase do que ficou ligado (e, na opção (b), dois botões novos).
  Decisão 4.
- **D-727** ("se tiver qualquer coisa que o kaique precise, ele tem que estar no instalador"): o servidor de entrar de
  longe hoje vem do Windows Update. Decisão 5.
- **D-719** (a frase única do aviso de falha): o plano propõe três frases. Decisão 10.
- **D-739** (a prova de que só o Tailscale entra fica para o primeiro teste no notebook do Kaique): o plano propõe
  provar antes, no PC dele, com o celular. Decisão 12.
- **D-767** (o alcance "está sendo confirmado"): o plano propõe as versões de prova num servidor de prova visível no PC
  dele, e o GitHub de verdade só para a prova do publicar, como rascunho. Decisão 6.
- **Mudam só por dentro, sem mudar o que ele decidiu:** D-733 (a tarefa do ajudante passa a chamar o socorro na pasta
  segura; continua uma pergunta só, na primeira abertura); D-741 e D-749 (a pergunta volta: agora porque o Windows
  responde "não preparado", não por uma anotação); D-719 (o registro lido de longe muda de pasta, continua lido pela
  conta de testes); D-731 (desinstalar limpa como o sistema; cumpre o "fica como era antes" que ele já decidiu, sem
  pergunta nova); D-764 (a sobra na pasta da conta deixa de nascer); D-705 e D-711 (a segunda tranca no servidor é o
  "só pela rede do Tailscale" que ele já escolheu).
- **Não mudam:** D-711, D-713, D-714 (publicada de propósito), D-715, D-716, D-717, D-718, D-722, D-724 (a não ser que a
  decisão 1 estenda a assinatura à diferença), D-728, D-729, D-730, D-732, D-735, D-736, D-743, D-744 a D-748, D-763,
  D-765, D-766.

### 4.2 Testes antigos que precisariam mudar (CLAUDE.md §11.8: só com o "sim" dele; decisão 7)

Os que já se sabe, lidos hoje:
1. `tests/test_decisoes_ajudante_da_atualizacao.py::test_d733_o_script_escondido_vai_codificado_e_solto`: **cobra a
   opção que fez o "Reiniciar agora" não voltar** (`DETACHED_PROCESS`) e o texto codificado na linha de comando. Passaria
   a cobrar o lançar solto sem essa opção e com o sinal de vida.
2. `tests/test_decisoes_desinstalar.py::test_d731_o_caderninho_fica_onde_o_plano_diz`: cobra o caminho
   `C:\ProgramData\EditorImpressao\testes-a-distancia`. Passaria a cobrar a pasta segura.
3. `tests/test_decisoes_desinstalar.py::test_d731_ligar_anota_o_antes_primeiro_e_so_na_primeira_vez`: cobra que o ligar
   roda o comando de tranca (`/inheritance:r`, `/setowner`), **o comando que estragou os arquivos**. Passaria a cobrar
   que nenhum comando de licença roda.
4. `tests/test_decisoes_desinstalar.py::test_d731a_a_pasta_do_desfazer_fica_protegida`: o mesmo comando de tranca.
   Passaria a cobrar a pasta segura de fábrica.
5. `tests/test_decisoes_ajudante_da_atualizacao.py`, a linha que cobra `configuracoes.PADROES[CHAVE_PERGUNTA_DO_WINDOWS_RESPONDIDA]`:
   a marca sai (peça 3).
6. `tests/test_decisoes_atualizacao.py`, as linhas que cobram `e_portatil` perguntando ao Velopack: passaria a cobrar o
   arquivo do Velopack ao lado do Update.exe.
7. `tests/test_decisoes_atualizacao.py`, o teste da falha da troca que fica riscada: com a falha passageira, uma troca
   interrompida não risca mais a versão.
8. Se a decisão 2 for "ao fechar": os testes do `trocar_antes_de_abrir` em `test_decisoes_ajudante_da_atualizacao.py`.
9. Se a decisão 10 for "três frases": nenhum teste antigo muda (o da frase de hoje continua valendo para o caso
   "voltou"); entram testes novos.

Os que **provavelmente** mudam, a conferir na hora de escrever (a lista exata vai no ONDE-PAREI do passo 7, e volta a
ele antes de mudar): os de `test_decisoes_testes_a_distancia.py` e `test_decisoes_ajudante_da_atualizacao.py` que cobram
`esta_pronto()` e `esta_ligado()` como anotação (passam a ler o Windows por uma leitura de prova); os de
`test_decisoes_preparo_d749.py` que leem o `preparo.txt` no ProgramData; e as preparações (`fixtures`) que apontam o
`PROGRAMDATA` para uma pasta de mentira (passam a apontar a pasta segura). Nenhum teste antigo muda para "passar": cada
um muda para cobrar o jeito certo, e falha no código de antes.

---

## 5. As decisões para o Samuel (em ordem: primeiro as que mudam mais coisas)

Cada uma no formato do CLAUDE.md §11.13. A gerente confere a lista do §11.13 antes de publicar na Central. O número da
decisão do Livro vai só no fim, para consulta.

### Decisão 1. O Kaique baixa a versão inteira ou só o que mudou?

- **Do que se trata.** É a atualização que chega sozinha no notebook do Kaique quando ele abre o programa: o programa
  baixa a versão nova e, com o programa fechado, troca uma pela outra.
- **O que acontece hoje.** Ele baixa só a diferença, uns 20 MB. Mas antes de trocar o computador remonta a versão inteira
  a partir dela. No teste do seu PC, isso levou 22 a 23 minutos; quando veio a versão inteira, 7 minutos e meio. E,
  pela leitura do código da ferramenta (ainda não provado), pelo caminho da diferença a sua assinatura não confere o
  que é instalado.
- **Sua dúvida:** "as atualizações deveriam ser rapidas" → no notebook do Kaique, a atualização "pequena" é a mais
  lenta. Quando você escolheu a ferramenta, a explicação foi "baixa só o que mudou, então é rápida"; com os 35 mil
  arquivos do nosso programa, baixar é rápido, remontar não.
- **O que você escolhe:**
  - **A versão inteira (sugestão, se a internet dele aguentar):** ele baixa 826 MB por versão (uns 2 min a 50 Mbps, uns
    11 min a 10 Mbps; conta, não medida). A troca fica em uns 7 minutos e meio mais o tempo de baixar. A assinatura
    passa a conferir tudo. Publicar fica uns 4 min mais rápido. Nada muda no programa dele, só no jeito de publicar.
  - **Só o que mudou, com a assinatura também na diferença:** ele baixa uns 20 MB; a troca continua com uns 22 min; o
    programa passa a conferir a diferença (muda o programa e a assinatura).
  - **Só comentário.** Se puder, diga a velocidade da internet do Kaique.
- **Por que a sugestão:** fica mais rápido dos dois lados e fecha a falha de segurança sem mudar o programa.
- **Situação:** ainda não decidido; o resto do plano não depende da escolha.
- **Imagem:** sim, um desenho simples com as duas barras de tempo medidas (7,5 min e 22 min) e o tamanho de cada
  download. Não há print possível: a troca acontece por trás, sem janela.
- Para consulta: D-723, D-724.

### Decisão 2. Com "Depois", quando a versão nova entra?

- **Do que se trata.** É o botão "Depois" do aviso "Chegou uma versão nova do Editor de Impressão", que aparece com o
  programa aberto.
- **O que acontece hoje.** Você escolheu em 17/11 "quando ele abrir o programa de novo", com uma espera curta. A
  explicação de então falava em "alguns segundos, até 5 minutos". Medido no seu PC, a espera é de 7 minutos e meio
  (versão inteira) a 23 minutos (só a diferença). E hoje, com uma versão esperando, o programa nem abre (defeito que o
  plano conserta de qualquer jeito).
- **O que você escolhe:**
  - **Na próxima abertura, como você decidiu:** ele clica no atalho para trabalhar e espera esse tempo olhando a
    janelinha.
  - **Ao fechar o programa (sugestão):** quando ele fecha, a troca acontece sozinha, por trás. Na próxima vez ele já abre
    na versão nova, sem esperar. Se abrir no meio da troca, aparece a janelinha até acabar (decisão 3). Se desligar o
    notebook no meio, nada se perde: a troca tenta de novo depois.
  - **Só comentário.**
- **Você continua no controle:** o "Reiniciar agora" continua trocando na hora.
- **Por que a sugestão:** a espera de 7 a 23 min cai na hora em que ele quer trabalhar; ao fechar, ninguém espera.
- **Situação:** muda uma escolha sua; nada muda sem o seu "sim".
- **Imagem:** sim, o print do aviso de hoje (`saida_teste\etapa5\prints\fase4\1-aviso.png`), com o botão "Depois"
  circulado em vermelho.
- Para consulta: D-734, D-720.

### Decisão 3. A janelinha "Atualizando o programa" em toda troca

- **Do que se trata.** É a janelinha pequena "Atualizando o programa, espere um pouco...", que você escolheu em 17/11
  para a abertura depois do "Depois".
- **O que acontece hoje.** Ela só existe nessa abertura. Depois do "Reiniciar agora", o programa fecha e nada aparece
  durante a troca (7 a 23 min): o Kaique vai achar que quebrou. E se ele clicar no atalho no meio da troca, o programa
  abre, a ferramenta de atualização o fecha à força e ele ainda mostra "a atualização não deu certo", sem ter dado
  errado (achado lendo o código).
- **O que você escolhe:**
  - **Sim (sugestão):** a mesma janelinha aparece em toda troca: depois do "Reiniciar agora" e quando ele clica no atalho
    no meio da troca. O programa abre sozinho quando a troca acaba. A janelinha espera a troca acabar de verdade, não um
    relógio de 5 minutos.
  - **Não:** fica como está.
  - **Só comentário.**
- **Por que a sugestão:** é a janelinha que você já escolheu, usada nos dois casos em que hoje não aparece nada.
- **Situação:** coisa nova sobre uma escolha sua; não dá para ligar e desligar (é o aviso da troca).
- **Imagem:** sim. A janelinha nunca foi fotografada (abri-la poria uma janela na sua tela); a gerente pede um print
  dela no passo 9, ou leva o desenho dela com o texto exato, dizendo que é desenho.
- Para consulta: D-742, D-748.

### Decisão 4. Se ligar os testes à distância der erro no meio

- **Do que se trata.** É a caixinha "Deixar o Samuel fazer testes neste computador", em Configurações > Testes à
  distância (e a mesma coisa na primeira abertura). Ligar faz nove coisas no Windows.
- **O que acontece hoje.** Se a nona falha, as oito primeiras ficam ligadas e a tela diz "Ligado, mas falta a senha".
  Foi o que aconteceu no seu PC hoje. E a tela mostra o que o programa anotou, não o que o Windows tem: ao desligar,
  disse "Desligado" com tudo ligado.
- **O que você escolhe** (nas duas opções a tela passa a mostrar o que o computador tem de verdade):
  - **(a) Desfaz tudo (sugestão):** se uma das nove falhar, o programa desfaz sozinho o que fez naquela vez, deixa o
    computador como estava e diz o que falhou. A tela diz "Desligado" e o motivo.
  - **(b) Deixa o que deu certo:** a tela diz "Ligado pela metade" e o que falta, com dois botões novos, "Tentar de novo"
    e "Desligar tudo".
  - **Só comentário.**
- **Por que a sugestão:** o computador nunca fica pela metade, e não entra botão novo na tela.
- **Situação:** é defeito e vai ser consertado de qualquer jeito; a escolha é só o que fazer com o que já foi feito.
- **Imagem:** sim, os prints da etapa 5: `saida_teste\etapa5\prints\fase-testes-ligar\3-depois.png` ("falta a senha" com
  tudo ligado) e `fase-testes-desligar\3-depois.png` ("Desligado" com tudo ligado), com a frase circulada.
- Para consulta: D-712, D-721.

### Decisão 5. A peça de entrar de longe vem da internet na hora de ligar

- **Do que se trata.** É a peça do Windows que deixa você entrar de longe no notebook do Kaique (o servidor de entrar de
  longe da Microsoft). Ela não vem no nosso instalador: o programa pede ao Windows Update na hora de ligar os testes.
- **O que acontece hoje.** No seu PC levou 13 minutos. Sem internet, não liga. Em 16/11 você decidiu: "se tiver qualquer
  coisa que o kaique precise, ele tem que estar no instalador".
- **O que você escolhe:**
  - **(a) Continua vindo do Windows Update (sugestão):** o programa avisa antes que precisa de internet e pode levar até
    15 minutos, e diz a causa se falhar. É o jeito que a Microsoft manda, e ela mantém a peça em dia.
  - **(b) Dentro do nosso instalador:** a Microsoft publica uma versão para isso; o instalador fica maior e as correções
    de segurança dela passam a vir das nossas versões.
  - **Só comentário.**
- **Por que a sugestão:** quem liga os testes é você, com o Kaique por perto e com internet; e a correção de segurança
  continua vindo da Microsoft.
- **Situação:** funciona assim hoje; a pergunta é se a sua regra de 16/11 vale também para essa peça.
- **Imagem:** não precisa.
- Para consulta: D-727.

### Decisão 6. Onde ficam as versões de prova, e uma versão de teste no GitHub

- **Do que se trata.** São as provas à vista no seu PC, antes de montar a versão do Kaique. Para provar a atualização, o
  programa instalado precisa achar versões novas em algum lugar.
- **O que acontece hoje.** Na etapa 5, as versões de mentira ficaram numa pasta do D:. Você disse "não faça mais nada
  escondido ou de mentira", e o alcance disso ainda está sendo confirmado com você.
- **O que você escolhe:**
  - **(a) Sugestão:** as versões de prova são versões de verdade do programa, servidas por uma janela pequena e visível no
    seu PC, que faz o papel do GitHub. O programa as baixa pela rede de verdade. Isso deixa provar, por exemplo, o que
    acontece se a internet cair no meio (fechando essa janela), sem tirar a internet do seu PC. Para provar o publicar
    no GitHub de verdade, uma versão de teste vai lá como rascunho (ninguém vê e nenhum programa enxerga), é liberada só
    durante a prova e apagada no fim. Ninguém tem o programa instalado ainda, então ninguém a recebe.
  - **(b) Tudo pelo GitHub de verdade:** cada versão de prova é publicada lá e apagada depois.
  - **(c) Sem GitHub:** tudo pela janela do seu PC; o publicar no GitHub fica provado só na primeira versão que for
    para o Kaique.
  - **Só comentário.**
- **Por que a sugestão:** tudo roda de verdade e à vista, e a prova do publicar não fica para o dia da entrega.
- **Situação:** precisa da resposta antes de montar as versões de prova.
- **Imagem:** não precisa.
- Para consulta: D-767, D-713.

### Decisão 7. Mudar os testes antigos que cobram o jeito errado

- **Do que se trata.** São testes automáticos que já existem e conferem o atualizador e os testes à distância.
- **O que acontece hoje.** Quatro deles cobram justamente o que estragou: um cobra o jeito de abrir o PowerShell que
  fez o "Reiniciar agora" não voltar; três cobram o comando que deixou os arquivos sem licença e o lugar inseguro da
  pasta. Mudar teste antigo precisa do seu "sim".
- **O que você escolhe:**
  - **Sim (sugestão):** cada um passa a cobrar o jeito certo e prova que falha no código de antes. Os outros que
    precisarem mudar vêm a você numa lista antes, um por um.
  - **Não:** os testes antigos ficam; o conserto não pode entrar sem quebrá-los.
  - **Só comentário.**
- **Por que a sugestão:** um teste que cobra o defeito impede o conserto.
- **Situação:** precisa da resposta antes do passo de testes.
- **Imagem:** não precisa.
- Para consulta: D-605.

### Decisão 8. Montar a versão no disco de dentro do seu PC

- **Do que se trata.** É o passo de publicar uma versão nova para o Kaique, que roda no seu PC. O Kaique não vê nada.
- **O que acontece hoje.** Leva de 70 a 93 minutos por versão. Todo o trabalho acontece no seu HD externo (o D:), e a
  ferramenta copia a pasta do programa (35 mil arquivos) quatro vezes. Medido hoje: a mesma parte que leva 20 minutos e
  meio no D: levou 3 minutos e meio no C:.
- **Sua dúvida:** "fazer tudo de novo sempre, eu acho que está errado né?" → em parte, sim: a ferramenta refaz tudo de
  propósito, mas fazer isso no HD externo é o que deixa tão lento.
- **O que você escolhe:**
  - **Sim (sugestão):** o trabalho é feito no C: e o rascunho é apagado no fim. Enquanto publica, ocupa de 6 a 10 GB do
    C: (hoje há 40 GB livres). O programa confere o espaço antes. O Kaique recebe exatamente a mesma atualização.
  - **Não:** continua no D:.
  - **Só comentário.**
- **Situação:** nada do que já funciona muda.
- **Imagem:** não precisa.

### Decisão 9. O instalador só quando você pedir

- **Do que se trata.** Quando a gente publica uma versão, saem, além da atualização, o instalador (o .msi, que o Kaique
  usa só na primeira vez) e uma versão portátil em zip. Nenhum dos dois é usado para atualizar.
- **O que acontece hoje.** Os dois são refeitos a cada versão; o .msi sozinho leva de 33 a 43 minutos no HD.
- **Sua dúvida:** "as atualizações deveriam ser rapidas" → o que demora no seu PC é refazer, a cada vez, coisas que só
  servem para instalar do zero.
- **O que você escolhe:**
  - **Sim (sugestão):** a versão de atualização sai sem o .msi e sem o zip portátil. O .msi sai na primeira entrega ao
    Kaique e sempre que você pedir. Para o Kaique, a atualização é igual. A versão portátil do programa (a pasta)
    continua existindo.
  - **Não:** tudo continua sendo refeito a cada versão.
  - **Só comentário.**
- **Com as decisões 8 e 9,** publicar cai de 70 a 93 min para uns 24 a 32 min (21 a 28 sem a diferença).
- **Imagem:** não precisa.
- Para consulta: D-300.

### Decisão 10. A frase do aviso de falha, para cada caso

- **Do que se trata.** É o aviso que aparece na tela do Kaique quando a atualização não dá certo. Hoje é sempre a frase
  que você escolheu em 16/11: "A atualização não deu certo. O programa voltou para a versão anterior e continua
  funcionando. Avise o Samuel."
- **O que acontece hoje.** Ela aparece em três casos, e em dois não é verdade: quando a versão chegou sem a sua
  assinatura e nem foi instalada (nunca saiu, não "voltou"); e quando a volta não deu certo (o programa não voltou).
- **O que você escolhe:**
  - **Três frases (sugestão):** recusada: "Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura
    do Samuel. O programa continua funcionando. Avise o Samuel." · voltou: a frase de hoje · não voltou: "A atualização
    não deu certo e o programa não conseguiu voltar sozinho. Não desinstale nada. Avise o Samuel."
  - **Uma frase só:** a de hoje em todos os casos.
  - **Quero outras palavras:** diga quais.
  - **Só comentário.**
- **Situação:** o aviso aparece uma vez por caso; o registro continua lido de longe.
- **Imagem:** sim, o print da etapa 5 em que a frase "voltou" apareceu para a versão recusada:
  `saida_teste\etapa5\prints\fase6-abrir-depois-da-falsa\1-aviso.png`, com a palavra "voltou" circulada.
- Para consulta: D-719.

### Decisão 11. A ferramenta de atualização tem dois defeitos já consertados numa versão de teste dela

- **Do que se trata.** É a ferramenta pronta que faz a atualização (a Velopack, que você escolheu em 16/11). Usamos a
  versão 1.2.161, a última final.
- **O que acontece hoje.** Os autores consertaram dois defeitos que nos atingem, mas só numa versão de teste (1.3.39):
  se a troca falhar num momento ruim, o programa pode ficar sem abrir, sem atualizar e sem desinstalar; e o desinstalar
  deixa uma pasta para trás.
- **O que você escolhe:**
  - **Ficar na 1.2.161 e nos protegermos (sugestão):** o programa guarda a versão de hoje antes de trocar e volta sozinho
    se a troca estragar; e a pasta que sobra deixa de nascer. Nada muda para o Kaique.
  - **Trocar pela versão de teste:** os consertos vêm prontos, mas é uma versão ainda em teste, e todas as provas de
    instalar e desinstalar têm de ser refeitas.
  - **Esperar a versão final dela** e trocar quando sair.
  - **Só comentário.**
- **Imagem:** não precisa.
- Para consulta: D-723.

### Decisão 12. Provar agora que só a rede do Tailscale entra

- **Do que se trata.** O programa abre a porta de entrar de longe só para a rede do Tailscale. Na prova de hoje, a
  entrada foi feita do próprio PC, e isso não prova que a porta está fechada para o Wi-Fi da casa. Em 17/11 ficou
  combinado provar no primeiro teste no notebook do Kaique.
- **O que você escolhe:**
  - **(a) Provar no seu PC, com o seu celular (sugestão):** com o Tailscale ligado no celular, entra; com o celular só no
    Wi-Fi, não entra. Precisa do Tailscale e de um aplicativo grátis de entrar de longe no celular; uns 10 minutos.
  - **(b) Deixar para o notebook do Kaique,** como estava combinado.
  - **Só comentário.**
- **Situação:** o plano põe também uma segunda tranca no próprio servidor (só a conta de testes, só vinda do Tailscale),
  que vale mesmo sem o firewall do Windows. Nada do que já funciona muda.
- **Imagem:** não precisa.
- Para consulta: D-739, D-705.

### Decisão 13. A senha dos testes digitada duas vezes

- **Do que se trata.** Na primeira vez que o programa abre no notebook do Kaique, a janela pequena "Testes à distância"
  pede a senha que você passou a ele (a mesma janela abre em Configurações > Testes à distância > "Pôr a senha dos
  testes").
- **O que acontece hoje.** Há um campo só, com pontinhos. Se ele errar uma letra, a conta de testes nasce com a senha
  errada, você não entra e nenhum dos dois sabe por quê. É um risco, não um defeito achado.
- **O que você escolhe:**
  - **(a) Dois campos, "Senha" e "Repita a senha" (sugestão);** se forem diferentes, a janela avisa e não segue.
  - **(b) Um campo só,** como hoje.
  - **Só comentário.**
- **De onde veio:** escolha de agente, sem pedido seu; o Windows e a maioria dos programas pedem a senha nova duas vezes.
- **Imagem:** sim, o print da janela de hoje (`saida_teste\etapa5\prints\fase3-visivel\1-janela-da-senha.png`), e um
  desenho da janela com os dois campos, dizendo que é desenho.

### Decisão 14. O nome que aparece na pergunta do Windows

- **Do que se trata.** Quando o programa pede licença, o Windows mostra "Deseja permitir que este aplicativo faça
  alterações no seu dispositivo?" com o nome "Windows PowerShell", e não "Editor de Impressão".
- **O que você escolhe:**
  - **(a) Deixar assim (sugestão),** e a janelinha de espera do programa diz antes: "O Windows vai perguntar se pode
    deixar o Windows PowerShell fazer alterações. Clique em Sim."
  - **(b) O próprio Editor de Impressão pedir:** o Windows mostra "Editor de Impressão" com a faixa amarela "Editor
    desconhecido" (o programa não tem o certificado pago).
  - **Só comentário.**
- **Situação:** é como o Windows mostra; não é defeito.
- **Imagem:** sim, mas não dá print (a pergunta fica na área segura do Windows): uma foto de celular, se você tirar na
  sessão de provas A, ou a imagem da página da Microsoft sobre essa pergunta.

### Decisão 15. Uma opção do Windows no notebook do Kaique

- **Do que se trata.** É uma proteção do Windows 11, o "Controle Inteligente de Aplicativos" (Segurança do Windows >
  Controle de aplicativos e navegador). Ligada, ela bloqueia programas sem certificado pago, e não dá para liberar um
  só. O nosso não tem (você escolheu a assinatura grátis).
- **O que acontece hoje.** No seu PC está desligada. No notebook do Kaique não se sabe; num Windows novo ela pode ligar
  sozinha.
- **O que você escolhe:**
  - **Sim (sugestão):** antes de mandar o programa, o Kaique olha essa tela e diz o que aparece (pode ser por telefone).
    Se estiver ligada, você decide antes de instalar.
  - **Não:** instalar e ver.
  - **Só comentário.**
- **Imagem:** sim, o print dessa tela do Windows no seu PC (só abrir a tela, sem mudar nada), com a opção circulada. A
  gerente pede antes de abrir.
- Para consulta: D-724.

### Decisão 16 (para depois). O motor do Kraken fora da atualização

- **Do que se trata.** O motor do Kraken é a parte do programa que acha as linhas de texto. Tem 1 GB e 98% dos arquivos
  do programa, e nunca muda. Mesmo assim, entra de novo em cada versão.
- **O que acontece hoje.** É ele que faz a troca no notebook levar uns 7 minutos e meio.
- **O que você escolhe:**
  - **Não agora (sugestão):** com as outras mudanças, publicar já fica em uns 21 a 32 min. Tirar o motor muda a instalação
    e o jeito de atualizar; só se estuda se ainda ficar lento.
  - **Sim, estudar:** um agente escreve o plano, e você decide antes de qualquer mudança.
  - **Só comentário.**
- **Imagem:** não precisa.

---

## 6. Riscos e o que ainda não se sabe

1. **A pergunta do Windows com o programa atrás de outra janela.** O Windows limita quem pode vir para a frente. Dar a
   janela do programa como dona e trazê-la para a frente pode não bastar em todo caso. A sessão A prova; se falhar, o
   plano para e a gerente leva a ele (talvez uma frase na janelinha: "clique no botão piscando na barra de baixo", que
   seria texto novo e precisa do "sim" dele).
2. **O socorro e a ferramenta de atualização por dentro.** Guardar a versão e reaplicá-la quando o Velopack deixar o
   programa sem a pasta dele depende de como o Update.exe da 1.2.161 se comporta nesse estado. Precisa de um plano curto
   próprio antes de escrever (passo 3) e da prova "versão que nem abre". Se o Update.exe não conseguir, o socorro tem de
   desempacotar a versão guardada ele mesmo: mais trabalho.
3. **Abrir no meio da troca.** Entre o clique no atalho e o programa ver a marca "trocando" há um instante em que a
   ferramenta pode fechá-lo. A prova da sessão B mostra se o instante importa.
4. **O aviso do Windows de "programa removido".** Ele também aparece numa instalação por cima; por isso a limpeza
   confere antes que o programa saiu. A prova de instalar por cima é opcional (+1 pergunta); sem ela, fica a conferência
   por leitura.
5. **A segunda tranca no servidor** (só a conta de testes, só do Tailscale) depende de o servidor do Windows aceitar
   endereço na regra; e o Tailscale tem também endereços do tipo novo (IPv6). A provar na sessão C.
6. **O perfil preso da conta de testes** pode precisar de o computador reiniciar. O plano tenta de novo uma vez ao ligar
   o computador.
7. **O notebook do Kaique não foi medido** (processador mais fraco): os tempos de troca e de ligar podem ser maiores. E
   a internet dele não é conhecida (pesa na decisão 1).
8. **O antivírus dele e as regras de proteção do Windows** podem barrar o PowerShell escondido ou a conta escondida
   (D-725). Só se sabe lá.
9. **A conta do Kaique é de administrador?** Não se sabe. Se não for, a pergunta pede a senha de outro administrador; o
   plano cobre a senha, mas isso nunca foi provado.
10. **O script sem a marca de UTF-8** (defeito 11) é uma leitura minha, não provada; a sessão A prova.
11. **O espaço no C:**: hoje 40 GB livres; o estudo viu o C: perder 14 GB sem explicação em uma hora. Publicar no C:
    precisa de 6 a 10 GB; o publicar confere antes.
12. **O alcance da D-767 ainda não foi confirmado** com ele (decisão 6). Se ele quiser tudo pelo GitHub, o passo 8 muda.
13. **Não existem fichas da memória** sobre o atualizador e os testes à distância (`memoria/` só tem a do instalador, a
    6.8, de 21/10). O plano se apoiou no Livro, no Plano e nos relatórios. Sugestão para a gerente: criar as fichas no
    próximo `/checkpoint`.
14. **A estimativa de escrita é chute**: nada parecido foi medido. Pode crescer se o socorro (risco 2) complicar.
15. **Dois agentes ao mesmo tempo** encurtariam a escrita (o atualizador e os testes à distância, depois do porteiro),
    mas os dois mexem no `atualizacao.py`; só a gerente decide.

## 7. Tempo total estimado

**Escrever (chute; nada parecido foi medido):** porteiro e pasta segura 5 a 7 h; scripts da sessão A 1 h; atualizador
8 a 12 h; testes à distância e tela 6 a 9 h; desinstalar 3 a 4 h; publicar 2 a 3 h; testes antigos e rodada do GitHub 2
a 4 h. **Total: 27 a 40 h de trabalho de agente.**

**Provar no PC dele (com ele por perto):** sessão A 25 a 30 min (3 perguntas); sessão B 1 h 30 a 2 h (4); sessão C 1 h
45 a 2 h 15 (10, mais 1 opcional); relatório 1 h (sem ele). **Total com ele: uns 4 a 4 h 45, umas 17 a 18 perguntas do
Windows.** Medido: a troca de 7,5 min e o ligar de 13 min (etapa 5). Chute: o resto.

**Montar a versão:** versões de prova 1 h 15 a 1 h 45 com o publicar novo (somado das partes medidas no estudo; a soma
não foi medida junta; o .msi no C: não foi medido). Sem o publicar novo: uns 4 a 5 h (medido: 6 h 47 para seis
versões). A versão final para o Kaique, com o .msi: uns 30 min (chute a partir das partes).

**Teste de confirmação:** 1 h 30 a 2 h, com 5 a 6 perguntas do Windows (chute, a partir da etapa 5, que levou de 07:23 a
12:05 com as investigações no meio).

---

## Detalhe técnico (para a gerente)

- Fontes: os três relatórios de hoje (ramos `revisao-atualizador-2026-11-18`, `revisao-distancia-2026-11-18`,
  `publicar-rapido-2026-11-18`); o relatório e o ONDE-PAREI da etapa 5 (ramo `etapa5-2026-11-17`); o Livro (D-605,
  D-700 a D-767); o Plano (Lista de bugs e Registro de 17 e 18/11); o código em `obra-2026-10-26`.
- O que as duas revisões propunham para a mesma coisa e onde ficou: "uma peça só que fala com o Windows" (revisão do
  atualizador, regra 1; revisão dos testes, as cinco obrigações) → peça 1. "O lugar seguro de fábrica" (revisão dos
  testes 1.4 e obrigação 5; revisão do atualizador 3b) → peça 2, uma pasta só em Arquivos de Programas (a chave do
  registro do Windows foi descartada: não cabe a cópia de 788 MB nem os scripts). "Conferir em vez de lembrar" (regra 2;
  obrigação 4) → peça 3. As provas P1 a P11 dos testes e 1 a 14 do atualizador → sessões A, B e C (a prova da pasta
  segura é feita uma vez só).
- Nada desta tarefa tocou o programa, os testes, o Windows ou o PC fora da cópia `plano-windows`.
