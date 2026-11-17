# Etapa 5: a lista do que conferir no PC do Samuel (preparada em 17/11/2026)

**O que é.** A etapa 5 é a conferência por quem não construiu. No PC do Samuel ela instala o programa do zero, testa a
atualização de mentira, liga e desliga os testes à distância, desinstala e, no fim, desfaz tudo e mostra a lista do que
foi desfeito (D-722). Esta lista foi preparada antes de o código ficar pronto: **nada dela foi rodado** além da foto do
Windows de 17/11 (só leitura).

**Quem usa esta lista.** O agente verificador da etapa 5. Os comandos de cada passo estão em `comandos.md`, com o
mesmo número. As fotos do Windows saem do `fotografo.py` e se comparam com o `comparar.py`.

**Palavras desta lista.**
- "Pergunta do Windows" = a janela "Deseja permitir que este aplicativo faça alterações no seu dispositivo?" (UAC).
- "Área escondida" = uma área de trabalho do Windows criada só para o teste (`CreateDesktop`), que nunca aparece no
  monitor do Samuel. É onde o programa abre e onde saem os prints (ver a parte E).
- "Ajudante" = a tarefa do Windows que roda como o sistema e troca a versão sem perguntar (D-733).
- `$TRAB` = `D:\programas\EditorImpressao\saida_teste\etapa5` (tudo do teste fica no D:, nunca no C:).
- `$E5` = a pasta destes programinhas dentro da cópia (worktree) da etapa 5.

---

## Parte A. Antes de começar (pré-requisitos)

Nenhum destes muda o Windows. Se faltar um, a etapa 5 não começa: pergunte à gerente.

- **A1. O código final.** Os dois trabalhos de 17/11 juntos num ramo só, com a rodada do GitHub passando:
  a atualização ao abrir o programa (D-732 a D-736) e a desinstalação que tira os testes à distância com os
  defeitos B2, B3 e B4 (D-731). A etapa 5 roda numa cópia nova desse ramo, nunca nas cópias dos construtores.
- **A2. Os nomes de verdade.** Ler o ONDE-PAREI e o relatório dos dois construtores e copiar aqui, antes de rodar:
  - o nome do ajudante (tarefa do Windows) e da tarefa "desfazer", se houver;
  - o comando "atualizar" de longe (D-736);
  - **como o programa instalado procura numa pasta de teste em vez do GitHub.** Sem isso, a atualização de mentira
    só sairia publicando no GitHub de verdade: **não fazer** sem o "sim" do Samuel. Hoje (código de 16/11) a pasta
    de teste (`--fonte`) só vale nos modos escondidos, não na abertura normal;
  - se a versão que o programa mostra vem do Velopack ou do `versao.py` (decide se dá para reaproveitar a mesma
    pasta empacotada para várias versões de mentira; ver C2);
  - onde o Velopack grava os pacotes baixados quando a pasta do programa não aceita gravação (o plano da D-732 diz
    "numa pasta do `LocalAppData`"; o nome exato não se achou). Se for dentro de `%LOCALAPPDATA%\EditorImpressao`
    (a pasta dos projetos), **pare e avise a gerente**: desinstalar poderia apagar junto.
- **A3. O Samuel avisado e presente.** A pergunta do Windows aparece no monitor dele umas 8 vezes (ver a parte E e
  as perguntas). Só ele pode clicar "Sim". Marcar o horário com ele.
- **A4. Disco.** C: com pelo menos 20 GB livres (a foto de 17/11 mostrou 45,6 GB). Todo `pytest` com
  `--basetemp` no D:, e `TEMP`/`TMP` no D: nos comandos de empacotar (o `vpk` usa a pasta temporária).
- **A5. O Tailscale do Samuel não é tocado.** Na foto de 17/11 ele está **parado** ("Tailscale is stopped"), e o
  endereço guardado é o 100.81.145.27. Nenhum `tailscale up`, `down`, `login` ou `logout` na etapa 5.
- **A6. Os programinhas de print da etapa 2** (`lancar.py` e `piloto_uia.py`, no ramo `kaique-etapa2-2026-11-16`,
  pasta `relatorios/frente-kaique-2026-11-16/etapa2/scripts/`) copiados para `$TRAB\pilotos\` com `git show`. Eles
  usam o Python 3.12 do sistema, que tem o `pywinauto`.

---

## Parte B. A ordem segura (as fases)

Cada fase diz os itens da parte C que ela prova. Depois de cada fase, uma foto sem administrador
(`foto-<fase>.json`), que é de graça, e o `comparar.py` com a foto anterior: assim a lista "o que o teste pôs no
Windows" se monta sozinha, fase por fase.

| Fase | O que se faz | Itens | Perguntas do Windows |
|---|---|---|---|
| 0 | Fotografar o Windows (sem e com administrador); cópia de reserva dos projetos; testes de máquina | C1, D-722, D-730 | 1 (foto com administrador) |
| 1 | Empacotar as versões 1.1.0 a 1.1.5 e montar o servidor de mentira no D: | C2, D-724, D-727 | 0 |
| 2 | Instalar o `.msi` 1.1.0 | D-723, D-727, B1, D-712, D-728 | 1 |
| 3 | Primeira abertura: a janela da senha com "Agora não" e a pergunta do Windows | D-733, D-735, D-721, D-729, D-711 | 1 |
| 4 | Atualização de mentira com o programa aberto: "Reiniciar agora" | D-732, D-714, D-715, D-720, D-706 | 0 (se aparecer, é defeito) |
| 5 | "Depois" e a próxima abertura | D-734, D-720 | 0 |
| 6 | Versão estragada (volta) e versão com a assinatura errada (recusa) | D-718, D-719, D-724 | 0 |
| 7 | Ligar os testes à distância pelas Configurações e entrar por SSH, pelo próprio PC (127.0.0.1) | D-705, D-711, D-712, D-716, D-717, D-721, B2 | 1 (ligar) + 1 (conferência com administrador) |
| 8 | Provar que a conta de testes não enxerga a pasta do Samuel nem muda o Windows | D-717 | 0 |
| 9 | O comando "atualizar" de longe, e o teste de longe que não procura versão | D-736 | 0 |
| 10 | Desligar e ligar de novo | B3, B4, D-705 | 2 |
| 11 | Desinstalar | D-731, D-722 | 1 (talvez 2, conforme o código final) |
| 12 | Fotografar de novo (sem e com administrador), comparar, desfazer o que sobrou, lista do que foi desfeito | D-722, D-729, D-730 | 1 (+1 se precisar desfazer à mão) |

**Regras que valem em todas as fases.**
- O programa instalado abre **sempre na área escondida**, com `LOCALAPPDATA` e `TEMP` trocados para `$TRAB\dados` e
  `$TRAB\temp` (assim as Configurações e os projetos de teste nunca caem na pasta do Samuel). Ver E1.
- Fechar o programa só pelo `WM_CLOSE`, nunca à força.
- Se uma janela do programa aparecer no monitor do Samuel (fora da área escondida), parar, fechar com `WM_CLOSE` e
  anotar: é achado.
- Uma fase só começa quando a anterior deu certo. Se algo falhar, pare, anote e decida com a gerente se continua.
  Em qualquer parada no meio, vá direto para as fases 11 e 12 (desfazer).
- Toda frase ou print do Samuel durante o teste vai na hora para o relatório da etapa 5.

---

## Parte C. Os itens

Formato de cada item: **Fazer** (passo a passo) · **Tem que acontecer** · **Provar** · **Desfazer**.
"Máquina" = prova por comando ou registro. "Olho" = print aberto e olhado.

### C1. A foto do Windows de antes (fase 0)
- **Fazer:** rodar o `fotografo.py` duas vezes: sem administrador (`foto-0-antes.json`) e num PowerShell de
  administrador (`foto-0-antes-adm.json`, uma pergunta do Windows). Fazer a cópia de reserva de
  `%LOCALAPPDATA%\EditorImpressao` para `$TRAB\reserva-dados-do-samuel` (só copia; a origem não muda).
- **Tem que acontecer:** as duas fotos gravadas. Comparar com `foto-antes-preparo-17-11.json`: o que mudou entre
  17/11 e o dia da etapa 5 é do uso normal do PC, e não do teste. (A foto de 17/11 está em
  `$TRAB\fotos\` e na pasta destes programinhas, **fora do git**: ela tem os nomes das contas, a lista de programas
  e as regras do firewall do PC do Samuel, e o projeto no GitHub é público. As fotos da etapa 5 também ficam fora.)
- **Provar:** os dois `.json` e a saída do `comparar.py`.
- **Desfazer:** nada a desfazer (só leitura). A cópia de reserva se apaga no fim, depois de comparar (é do teste).

### C2. Empacotar as versões de mentira (fase 1)
- **Fazer:** numa cópia nova do ramo final (A1), empacotar a pasta do programa uma vez (`empacotar.py --modo pasta`,
  uns 11 minutos) e publicar no servidor de mentira `$TRAB\servidor` (`publicar_versao_kaique.py --pasta`):
  - 1.1.0: a que se instala (dela sai o `.msi`);
  - 1.1.1: boa (fase 4, "Reiniciar agora");
  - 1.1.2: boa (fase 5, "Depois");
  - 1.1.3: estragada de propósito: a mesma pasta sem o `tesseract\tesseract.exe` (o teste rápido cobra esse
    arquivo), para provar a volta (fase 6);
  - 1.1.4: boa, mas assinada com uma chave que não é a do Samuel (fase 6);
  - 1.1.5: boa (fase 9, "atualizar" de longe).
  O número de cada versão muda só no `versao.py` **da cópia da etapa 5, sem commit**. Se A2 disser que a versão
  vem do `versao.py` de dentro do pacote, empacotar a pasta de novo a cada versão (uns 11 minutos cada).
- **Tem que acontecer:** `$TRAB\servidor` com os 6 pacotes, os arquivos de assinatura e o `.msi` da 1.1.0.
- **Provar:** a lista da pasta; a conferência do `empacotar.py` ("tudo dentro": modelos, DLLs do ScanTailor, motor
  do Kraken, Tesseract com 6 idiomas, Visual C++).
- **Desfazer:** apagar `$TRAB\servidor`, `build\` e `dist\` da cópia da etapa 5 (tudo criado pelo teste), no fim.
  A chave falsa da 1.1.4 fica em `$TRAB\segredo\` e sai junto. A chave do Samuel nunca é copiada nem mexida.

### D-705. Testes à distância pelo OpenSSH do Windows, só pelo Tailscale, sem porta no programa (fases 7 e 10)
- **Fazer:** nas Configurações (área escondida), conferir a caixinha "Deixar o Samuel fazer testes neste computador
  (pela rede do Tailscale)" e pôr a senha pelo botão "Pôr a senha dos testes" (fase 7). Depois desmarcar a caixinha
  (fase 10).
- **Tem que acontecer:** com a senha: o serviço `sshd` existe, liga sozinho e está rodando; a regra larga
  `OpenSSH-Server-In-TCP` está desligada; a regra `EditorImpressao-Testes` aceita só a porta 22, só da faixa do
  Tailscale (100.64.0.0/10 e fd7a:115c:a1e0::/48) e só pela placa "Tailscale". O programa não abre porta nenhuma.
  Desmarcando: o `sshd` para e fica desligado, a regra nossa sai, a conta fica desativada.
- **Provar (máquina):** a foto da fase (serviços e regras, com o detalhe dos endereços e da placa); `netstat -ano`
  mostrando que nenhuma porta é do `EditorImpressao.exe`. **Limite:** pelo próprio PC não dá para provar que "só o
  Tailscale entra": a ligação para 127.0.0.1 ou para o próprio endereço do Tailscale não passa pelo filtro da placa.
  A prova é a regra lida do Windows; a prova de fora fica para a etapa 6 (ver perguntas).
- **Desfazer:** fases 11 e 12.

### D-711. Liga sozinho com o Windows e entra com senha, não com chave (fase 7)
- **Fazer:** depois de ligar, ler o modo de partida do `sshd` e o `sshd_config`; tentar entrar por SSH com
  `PubkeyAuthentication=no` e a senha de teste.
- **Tem que acontecer:** `sshd` em "Automático"; no `sshd_config`, `PasswordAuthentication yes` e
  `AllowUsers EditorTestes` valendo para todas as contas (ver B2); a entrada com senha funciona.
- **Provar (máquina):** foto (StartMode Auto); `sshd -T` na conferência com administrador; a saída do `whoami` pela
  SSH ("samuel-pc\editortestes"). **Não religar o PC do Samuel** para provar o "liga com o Windows": o modo
  Automático lido do Windows basta (ver perguntas, se a gerente quiser mais).
- **Desfazer:** fases 11 e 12.

### D-712. A opção vem ligada de fábrica; o instalador não pergunta nada (fases 2 e 3)
- **Fazer:** instalar o `.msi` com `/passive` (fase 2) e guardar o registro do instalador; abrir as Configurações na
  primeira abertura (fase 3).
- **Tem que acontecer:** o instalador não mostra nada sobre testes à distância; na primeira abertura, a caixinha está
  marcada, com a frase "Falta a senha" (porque foi "Agora não").
- **Provar:** print das Configurações (olho); o registro do `msiexec` sem nenhuma tela de pergunta (máquina).
- **Desfazer:** fase 11.

### D-713. O projeto continua público; nenhum token dentro do programa (fase 2)
- **Fazer:** procurar, na pasta instalada, os textos `ghp_`, `github_pat_` e `token` nos arquivos do programa
  (só ler); conferir que a fonte de fábrica é o endereço público do projeto.
- **Tem que acontecer:** nenhum token; a fonte é `https://github.com/Samuel-Bottini-BR/EditorImpressao`.
- **Provar (máquina):** a saída da busca; o teste `test_d719_nenhum_token_dentro_do_programa` na rodada final.
- **Desfazer:** nada.

### D-714. Publicada de propósito; o "procurar ao ligar o computador" SAIU (fases 2 a 5)
- **Fazer:** depois da instalação e da primeira abertura, listar as tarefas do Windows com EditorImpressao (na
  conferência com administrador) e ler o XML delas.
- **Tem que acontecer:** nenhuma tarefa com gatilho "ao ligar o computador" (`BootTrigger`) — a D-732 substituiu essa
  parte; a versão nova só chega porque foi publicada no servidor de mentira (ninguém publica sozinho).
- **Provar (máquina):** o XML das tarefas; o registro da atualização mostrando que a procura só acontece ao abrir.
- **Desfazer:** fases 11 e 12.

### D-715. Versão nova com o programa aberto: aviso para salvar e reiniciar (fase 4)
- **Fazer:** com a 1.1.1 publicada, abrir o programa na área escondida com um projeto de teste (cópia de um livro de
  teste em `$TRAB\livros`, nunca o original); esperar o aviso.
- **Tem que acontecer:** aparece "Chegou uma versão nova do Editor de Impressão. Salve o seu trabalho e reinicie o
  programa para usar a versão nova." com "Reiniciar agora" e "Depois". **Atenção:** a frase de 16/11 ainda diz
  "na próxima vez que o computador ligar"; com a D-734 ela tem de falar da próxima abertura. Se continuar falando do
  computador, é defeito.
- **Provar:** print do aviso (olho), modelo do girar; o texto lido pelo leitor de tela do Windows (máquina).
- **Desfazer:** nada além da fase 11.

### D-716. Prioridade baixa ou normal, a cada teste (fase 7)
- **Fazer:** pela SSH, rodar o mesmo comando curto duas vezes: com `start "" /belownormal /wait ...` e sem; dentro
  dele, ler a prioridade do próprio processo.
- **Tem que acontecer:** "BelowNormal" no primeiro, "Normal" no segundo.
- **Provar (máquina):** a saída dos dois.
- **Desfazer:** nada (os processos terminam sozinhos).

### D-717. Conta separada, sem administrador, escondida; não enxerga a pasta do Samuel (fases 7 e 8)
- **Fazer:** depois de ligar, ler a conta e os grupos; olhar a tela de entrada pelo valor `UserList`; pela SSH, como
  `EditorTestes`, tentar **só ler** a pasta do Samuel e conferir se é administrador.
- **Tem que acontecer:**
  - a conta `EditorTestes` existe, com a descrição "Conta so para os testes a distancia", só no grupo Usuários,
    fora do grupo Administradores; `UserList\EditorTestes = 0`;
  - pela SSH: `Get-ChildItem C:\Users\fotog` e `Test-Path $env:LOCALAPPDATA`-do-Samuel dão "Acesso negado";
    `IsInRole(Administrator)` dá False; `net session` dá "Acesso negado" (erro 5);
  - os projetos de teste dessa conta ficam em `C:\Users\EditorTestes\AppData\Local\EditorImpressao`.
- **Achado já conhecido, para o relatório (17/11, só leitura):** o disco **D: do Samuel dá controle total a "Todos"**
  (`icacls D:\` → `Todos:(OI)(CI)(F)`, herdado por `D:\programas`, pelo acervo e pelas outras pastas). Então a conta
  de testes **enxerga e pode mudar tudo no D:**. A prova da fase 8 confirma isso **só lendo** (`Test-Path D:\programas`)
  e escrevendo um arquivo **só** em `$TRAB\escrita-da-conta-de-testes\`. Nunca escrever em outra pasta do D:. Isso
  vai ao relatório como "pela metade": no C: a regra vale; no D: não.
- **Também olhar (D-725):** se o antivírus (Windows Defender, na foto) reclamar da conta, anotar; não liberar nada
  sem a gerente.
- **Provar:** foto (contas, grupos, UserList); a saída dos comandos pela SSH (máquina); print da tela de entrada não
  dá (é a tela de bloqueio): a prova é o `UserList`.
- **Desfazer:** fases 11 e 12. O arquivo de `$TRAB\escrita-da-conta-de-testes\` sai no fim.

### D-718. Se a atualização falhar, volta para a anterior e avisa (fase 6)
- **Fazer:** publicar a 1.1.3 estragada; abrir o programa (área escondida), deixar entrar; abrir de novo.
- **Tem que acontecer:** a versão entra, o teste rápido falha (falta o `tesseract.exe`), o programa volta para a 1.1.2
  sozinho, **sem pergunta do Windows** (D-733), e não tenta a 1.1.3 de novo.
- **Provar (máquina):** o `sq.version` da pasta instalada antes e depois; o registro
  `C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log` com "FALHOU (teste)" e "voltando para a versão 1.1.2";
  o `estado.json` com a 1.1.3 em "não tentar".
- **Desfazer:** nada além da fase 11.

### D-719. O aviso da falha na tela e o registro que se lê de longe (fase 6, e fase 9 para o "de longe")
- **Fazer:** depois da volta, abrir o programa; mais tarde, pela SSH como `EditorTestes`, ler o registro.
- **Tem que acontecer:** aparece uma vez só "A atualização não deu certo. O programa voltou para a versão anterior e
  continua funcionando. Avise o Samuel."; na abertura seguinte, não aparece mais. A conta de testes consegue ler o
  `atualizacao.log`. Nenhuma senha dentro do programa.
- **Provar:** print do aviso (olho); `Get-Content` do registro pela SSH (máquina).
- **Desfazer:** nada além da fase 11.

### D-720. "Reiniciar agora" e "Depois" (fases 4 e 5)
- **Fazer:** fase 4: no aviso da 1.1.1, "Reiniciar agora". Fase 5: no aviso da 1.1.2, "Depois" (o resto é a D-734).
- **Tem que acontecer:** "Reiniciar agora": o programa grava o trabalho, fecha, o ajudante troca **sem pergunta do
  Windows**, e o programa reabre na 1.1.1, com o projeto igual. "Depois": nada troca agora e o aviso não volta na
  mesma abertura.
- **Provar:** prints do aviso e do programa reaberto (olho); `sq.version`; o `projeto.json` do projeto de teste antes
  e depois, comparado campo por campo (máquina). **Cuidado:** se quem reabre o programa não herdar a área escondida,
  a janela aparece no monitor do Samuel: avisá-lo antes deste passo.
- **Desfazer:** nada além da fase 11.

### D-721. A janela da senha na primeira abertura; sem senha, nada liga; a senha depois (fases 3 e 7)
- **Fazer:** fase 3: na primeira abertura, na janela "Testes à distância", clicar "Agora não". Fase 7: pôr a senha pelo
  botão das Configurações.
- **Tem que acontecer:** fase 3: a janela aparece uma vez; com "Agora não", nenhuma conta de testes e nenhum `sshd`
  (mas a pergunta do Windows aparece mesmo assim: D-735). Segunda abertura: a janela não volta. Fase 7: com a senha,
  liga.
- **Provar:** print da janela (olho); a foto da fase 3 sem `EditorTestes` e sem `sshd` (máquina).
- **Desfazer:** fases 11 e 12.

### D-722. Testar no PC do Samuel e desfazer tudo, com a lista do que foi desfeito (fases 0 e 12)
- **Fazer:** juntar as saídas do `comparar.py` de cada fase numa tabela "o que o teste pôs" e, depois da fase 12, a
  tabela "o que foi desfeito" (o mesmo item, linha por linha).
- **Tem que acontecer:** o `comparar.py` entre `foto-0-antes-adm.json` e `foto-12-depois-adm.json` termina com
  "o Windows ficou como antes", fora as diferenças esperadas (o Editor antigo de 01/09 que saiu, D-729).
- **Provar (máquina):** as duas tabelas no relatório, com a saída do comparador.
- **Desfazer:** é o próprio item.

### D-723. Velopack, Arquivos de Programas, a instalação de 28/10 (aqui, a de 01/09) sai (fases 2 e 3)
- **Fazer:** instalar o `.msi` 1.1.0 dentro da área escondida (`msiexec /i ... /passive /l*v`).
- **Tem que acontecer:** uma pergunta do Windows; o programa em `C:\Program Files\EditorImpressao` (64 bits, não
  "(x86)"); uma entrada nova nos programas instalados; o Editor antigo de 01/09 continua lá até a primeira abertura
  (ele sai na fase 3, pelo ajudante: D-729).
- **Provar (máquina):** foto da fase 2 (pasta nova, entrada nova, atalhos novos); o registro do `msiexec`.
- **Desfazer:** fase 11.

### D-724. A assinatura: versão com a assinatura errada não entra (fase 6)
- **Fazer:** publicar a 1.1.4 assinada com a chave falsa; abrir o programa.
- **Tem que acontecer:** recusada antes de baixar; nada baixado; continua a 1.1.2; o aviso da falha aparece (a frase
  única, ressalva 8 da etapa 3).
- **Provar (máquina):** o registro com "FALHOU (recusada) ... a assinatura não confere"; a pasta de pacotes do Velopack
  sem a 1.1.4; o `sq.version` igual.
- **Desfazer:** nada além da fase 11.

### D-727. Tudo dentro do instalador; nada baixado na hora de instalar (fases 1 a 3)
- **Fazer:** conferir o pacote (C2); durante a instalação e a primeira abertura, ler o registro do Velopack e o da
  atualização.
- **Tem que acontecer:** o Visual C++ oficial está dentro do pacote; nenhum download na instalação; na primeira
  abertura, "Visual C++ ...: instalado" ou "já estava" (no PC do Samuel ele já existe).
- **Provar (máquina):** os registros. **Limite:** desligar a internet do PC do Samuel não se faz; a prova sem internet
  fica como ressalva.
- **Desfazer:** se o Visual C++ for instalado pelo teste (não deve, porque já existe), anotar a versão; ele não sai
  (outros programas usam).

### D-728. Pelo atalho "(desenvolvimento)" nada aparece e nada liga (fase 2)
- **Fazer:** abrir o programa pelo código (`.venv\Scripts\pythonw.exe main.py`) na área escondida, com os dados
  trocados, e esperar 60 segundos.
- **Tem que acontecer:** nenhuma janela de senha, nenhuma pergunta do Windows, nenhum aviso de versão; o registro da
  atualização não ganha linha.
- **Provar:** print da janela (olho); a foto sem mudança (máquina); os testes `test_decisoes*` da rodada final.
- **Desfazer:** fechar com `WM_CLOSE`.

### D-729. O Editor de Impressão antigo de 01/09 sai, com os projetos intactos (fase 3)
- **Estado de 17/11 (foto):** instalado em `C:\Program Files\Editor de Impressao` (434 arquivos, 434 MB), versão
  1.0.0, com a identidade que o programa novo procura para tirar (`{7C4E1B92-3A5D-4F18-9B6C-2E8A5D0F3C71}_is1`,
  o `APPID_DO_INNO` do `atualizacao.py`), com dois atalhos:
  `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Editor de Impressao.lnk` e
  `C:\Users\Public\Desktop\Editor de Impressao.lnk`. O desinstalador dele (do instalador de 01/09, conferido no git)
  só apaga a pasta dele e o `_internal`: nunca o `%LOCALAPPDATA%`.
- **Fazer:** nada à mão: a pergunta do Windows da primeira abertura (D-733) tira o antigo pelo ajudante. Se o código
  final não tirar, tirar à mão com o desinstalador dele (`unins000.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART`),
  num PowerShell de administrador.
- **Tem que acontecer:** a pasta antiga, a entrada nos programas instalados e os dois atalhos somem; a pasta dos
  projetos tem a mesma impressão digital da foto de antes; os atalhos "(desenvolvimento)" e "(rodada de consertos)"
  continuam apontando para o mesmo lugar e abrem.
- **Provar (máquina):** o `comparar.py` marca essas saídas como "esperado"; o registro da atualização com "instalação
  antiga ... tirada (código 0)". Abrir um projeto do Samuel **numa cópia** pelo programa novo e pelo atalho
  "(desenvolvimento)" (dados trocados, área escondida): abre igual (olho, print).
- **Desfazer:** não se devolve (é a decisão do Samuel). O instalador de 01/09 não existe mais; se ele quiser de volta,
  há o de 28/10 e o `instalador.iss` (D-730).

### D-730. O instalador antigo fica de reserva (fases 0 e 12)
- **Fazer:** conferir que o `instalador.iss` e o modo `instalador` do `empacotar.py` continuam no ramo final, que os
  testes do Inno (`tests/test_empacotar.py`) passam, e que o instalador de 28/10 continua em
  `C:\Users\fotog\Desktop\Editor de Impressao - rodada de consertos para o Kaique\`.
- **Tem que acontecer:** tudo lá, sem mudança. Nada é compilado com o Inno nesta etapa.
- **Provar (máquina):** `git ls-files instalador.iss`; o resultado do `test_empacotar.py`; a lista da pasta de 28/10.
- **Desfazer:** nada. Depois da etapa 5, a gerente pergunta ao Samuel se o antigo sai.

### D-731. Desinstalar tira o OpenSSH (se foi nosso), a regra, a conta e o perfil (fase 11)
- **Fazer:** com os testes à distância ligados, desinstalar pelo `msiexec /x <código do produto> /passive /l*v`, dentro
  da área escondida (o mesmo gancho do "Configurações > Aplicativos > Desinstalar"); esperar o que o código final
  disser (tarefa "desfazer" ou segunda pergunta); tirar a foto 11.
- **Tem que acontecer (PC do Samuel, pela foto de 17/11):**
  - **sai**, porque não existia antes: o recurso OpenSSH.Server, o serviço `sshd`, a regra `OpenSSH-Server-In-TCP`,
    a regra `EditorImpressao-Testes`, a conta `EditorTestes`, o perfil `C:\Users\EditorTestes`, o valor e a chave
    `UserList` (a chave não existia), as tarefas do EditorImpressao, a pasta do programa, os atalhos novos;
  - **fica**, porque já existia: a pasta `C:\ProgramData\ssh` (existia vazia), o serviço `ssh-agent` (desligado), o
    `ssh.exe` do Windows, a conta `WsiAccount` e o perfil dela, o Tailscale;
  - **fica**, de propósito: `%LOCALAPPDATA%\EditorImpressao` (os projetos), igual ponto por ponto;
  - `C:\ProgramData\EditorImpressao` (o registro da atualização): o plano diz que fica. Se ficar, anotar e perguntar
    à gerente se sai à mão no fim.
- **Provar (máquina):** o `comparar.py` da foto 11 contra a foto 0; o `o-que-foi-desfeito.txt` do programa; o
  registro do `msiexec`.
- **Desfazer:** o que sobrar vai para a fase 12.

### D-732. A versão nova é procurada quando o programa abre (fases 4 e 5)
- **Fazer:** publicar a 1.1.1 com o programa fechado; abrir o programa.
- **Tem que acontecer:** ao abrir, a 1.1.1 é achada e baixada por trás; nada acontece só por o tempo passar ou por
  ligar o computador (não há tarefa ao ligar: D-714).
- **Provar (máquina):** o registro da atualização com a hora da abertura e a da procura; o registro do Velopack.
- **Desfazer:** nada além da fase 11.

### D-733. Uma pergunta do Windows na primeira abertura; depois, nenhuma (fases 3 a 6)
- **Fazer:** fase 3: primeira abertura (o Samuel clica "Sim"). Fases 4 a 6: três trocas de versão e uma volta.
- **Tem que acontecer:** fase 3: **uma** pergunta; depois dela, o ajudante existe (tarefa do sistema), o Visual C++
  está lá, o Editor antigo saiu. Fases 4 a 6: **nenhuma** pergunta do Windows. A conta do Samuel (no papel do Kaique,
  administrador como ele) consegue mandar o ajudante rodar.
- **Provar:** o Samuel diz quantas perguntas viu em cada fase (anotar a frase dele, com a hora); o XML e a licença do
  ajudante na conferência com administrador; o registro de cada troca (máquina). Print da pergunta: ver E2.
- **Desfazer:** o ajudante sai na fase 11; se sobrar, fase 12.

### D-734. Com "Depois", a versão entra na próxima abertura, com uma espera curta (fase 5)
- **Fazer:** com a 1.1.2 publicada, abrir; no aviso, "Depois"; trabalhar um pouco no projeto de teste; fechar
  (`WM_CLOSE`); conferir que a versão não mudou; abrir de novo.
- **Tem que acontecer:** ao fechar, nada troca (continua a 1.1.1); ao abrir de novo, uma espera curta antes da janela
  e a 1.1.2 já está; o projeto igual.
- **Provar:** `sq.version` depois de fechar e depois de abrir (máquina); print da espera, se houver janela dela, e do
  programa aberto (olho); a hora de cada passo no registro.
- **Desfazer:** nada além da fase 11.

### D-735. A pergunta do Windows da primeira abertura aparece sempre, mesmo com "Agora não" (fase 3)
- **Fazer:** é a fase 3 (o "Agora não" da D-721).
- **Tem que acontecer:** mesmo sem senha, a pergunta aparece; com o "Sim", o ajudante nasce e o Editor antigo sai;
  nenhuma conta de testes.
- **Provar:** o Samuel confirma a pergunta (frase dele); a foto da fase 3 (ajudante sim, `EditorTestes` não).
- **Se o Samuel clicar "Não" por engano:** anotar; o programa tem de abrir mesmo assim; a pergunta volta na próxima
  abertura (conferir no código final o que ele promete).
- **Desfazer:** fase 11.

### D-736. O teste de longe não procura versão; o comando "atualizar" de longe funciona (fase 9)
- **Fazer:** com a 1.1.5 publicada: pela SSH como `EditorTestes`, abrir o programa no modo de teste (um teste leve,
  sem janela) e conferir que nada é procurado; depois rodar o comando "atualizar" de longe (o nome vem de A2).
- **Tem que acontecer:** o teste de longe não gera linha de procura no registro e não baixa nada; o "atualizar" chama
  o mesmo ajudante, confere a assinatura, e a versão passa para a 1.1.5 sem pergunta (ninguém responderia).
- **Provar (máquina):** o registro antes e depois de cada comando; o `sq.version`; a pasta
  `C:\Users\EditorTestes\AppData\Local\velopack` sem registro de procura.
- **Desfazer:** nada além da fase 11.

### D-706. Como os apps: instalador só na primeira vez, depois a versão chega sozinha (fases 4 a 6)
- **Fazer:** não é passo próprio: é a soma das fases 4 a 6.
- **Tem que acontecer:** ninguém roda instalador depois da fase 2; o Velopack baixa só o que mudou (o pacote de
  diferença), salvo a primeira, que pode vir inteira (ressalva 7 da etapa 3).
- **Provar (máquina):** o registro do Velopack com o tamanho baixado em cada troca.
- **Desfazer:** nada além da fase 11.

### B1. O gancho do instalador roda sem administrador (fase 2)
- **Fazer:** logo depois de instalar (antes da primeira abertura), ler o registro da atualização.
- **Tem que acontecer (com o código final):** o gancho de instalar não tenta mais criar tarefa; nenhuma linha
  "criar a tarefa: NÃO deu certo". O ajudante só aparece depois da pergunta da fase 3.
- **Provar (máquina):** o registro; a foto 2 sem tarefa (confirmada na conferência com administrador da fase 7, que
  mostra a data de criação do ajudante, depois da instalação).
- **Desfazer:** nada.

### B2. As linhas do `sshd_config` dentro do bloco "Match Group administrators" (fase 7)
- **Fazer:** na conferência com administrador, ler o `sshd_config` inteiro e rodar `sshd -T` para três contas:
  `EditorTestes`, `fotog` (administrador) e `WsiAccount` (conta comum que já existe no PC: **só se lê a
  configuração, ninguém entra nela**). Ler o registro do OpenSSH depois de uma tentativa de entrar como `fotog`
  sem senha (`BatchMode`, que não chega a pedir senha).
- **Tem que acontecer (com o conserto):** as linhas do programa ficam antes do primeiro `Match`, entre as duas
  linhas-marca; `sshd -T` mostra `allowusers editortestes` para as três contas. Sem o conserto, `WsiAccount` sairia
  sem `allowusers` (é a prova do defeito).
- **Provar (máquina):** o `sshd_config`, a saída do `sshd -T` e a linha "not listed in AllowUsers" do registro do
  OpenSSH.
- **Desfazer:** fases 11 e 12.

### B3. Ligar de novo depois de desligar (fase 10)
- **Fazer:** desmarcar a caixinha (pergunta do Windows), marcar de novo e pôr a senha (pergunta do Windows); entrar
  pela SSH.
- **Tem que acontecer:** liga sem erro; a conta volta a estar ativa; o `sshd_config` tem **um** par de linhas-marca
  (não dois); a SSH entra.
- **Provar (máquina):** a mensagem na tela (print), a foto e o `sshd_config`.
- **Desfazer:** fases 11 e 12.

### B4. Desligar não desliga um OpenSSH que já era do dono (fase 10)
- **No PC do Samuel não dá para provar de verdade:** o OpenSSH servidor não existia antes (foto de 17/11). O que se
  prova: o caderninho `C:\ProgramData\EditorImpressao\testes-a-distancia\antes.json` diz "não existia", e por isso o
  desligar pode parar o `sshd`. O caso "já existia" fica com o teste automático do construtor (máquina) e vira
  ressalva no relatório.
- **Desfazer:** fases 11 e 12.

---

## Parte D. A fase 12: desfazer e a lista do que foi desfeito

1. Foto sem administrador e com administrador (`foto-12-depois.json`, `foto-12-depois-adm.json`).
2. `comparar.py foto-0-antes-adm.json foto-12-depois-adm.json`.
3. Para cada "SOBROU" ou "MUDOU" que não for esperado: desfazer **só o que o teste pôs**, com o comando da linha
   correspondente em `comandos.md` (passo 12), num PowerShell de administrador (uma pergunta do Windows).
   **Nunca** apagar `C:\ProgramData\ssh` (existia antes), a conta `WsiAccount`, nada do Tailscale, nada de
   `%LOCALAPPDATA%\EditorImpressao`.
4. Foto de novo e comparar de novo, até "o Windows ficou como antes".
5. A pasta dos projetos: se a impressão digital mudou, comparar arquivo por arquivo com a cópia de reserva. Se o
   Samuel usou o programa durante o teste, o `configuracoes.json` e o `historico.json` mudam por isso: perguntar a
   ele antes de devolver qualquer arquivo da reserva.
6. Apagar o que o teste criou no D: (`$TRAB`, depois de guardar as fotos, os registros e os prints no relatório) e a
   cópia da etapa 5, se a gerente mandar.
7. A lista do que foi desfeito, no relatório, nos três formatos: o item, o que o teste pôs, como saiu, a prova.

---

## Parte E. Prints sem abrir janela na tela do Samuel

**E1. As janelas do programa (aviso de versão nova, aviso da falha, janela da senha, Configurações, a espera curta).**
O jeito que serve é o da etapa 2: a **área escondida** do Windows.
- `lancar.py` cria a área (`CreateDesktop`) e abre o programa nela (`CreateProcess` com `lpDesktop`). A janela existe
  de verdade, com fonte e tamanho reais, mas nunca aparece no monitor.
- `piloto_uia.py` roda dentro da mesma área, acha os botões pelo leitor de tela do Windows (pywinauto, `uia`), clica
  por mensagens do Windows (`PostMessage`), sem tocar no mouse nem no teclado do Samuel, e tira o print com
  `PrintWindow(..., PW_RENDERFULLCONTENT)`.
- O `QT_QPA_PLATFORM=offscreen` (o dos `tests/conftest.py` e do `teste_botoes.py`) não serve aqui: ele não roda o
  programa instalado de verdade, e sem `QT_QPA_FONTDIR` o texto sai em quadradinhos.
- Mover a janela para fora da tela (-32000) também funciona, mas ela fica no mesmo desktop do Samuel e pode piscar
  ou roubar o foco ao abrir: a área escondida é mais segura.

**E2. A pergunta do Windows ("Deseja permitir...?"). Não há jeito de tirar print dela sem aparecer na tela.**
- Neste PC ela aparece na **área segura** do Windows (`PromptOnSecureDesktop = 1`, `ConsentPromptBehaviorAdmin = 5`,
  lidos em 17/11). A área segura é feita para que nenhum programa a veja nem clique nela: `PrintWindow`, cópia da
  tela e a tecla Print Screen não a pegam, e nenhum programa consegue clicar "Sim".
- Ela aparece **no monitor do Samuel mesmo quando o programa está na área escondida**: o Windows escurece a tela e
  mostra a pergunta lá.
- O que dá para fazer: (a) o Samuel clica "Sim" e, se quiser, tira uma foto do monitor com o celular; (b) a prova vem
  do Windows depois do "Sim" (o ajudante criado, o Editor antigo fora, o registro). (c) Desligar a área segura
  mudaria uma proteção do Windows dele: **não recomendado**.
- Isto é pergunta para o Samuel (ver abaixo).

---

## Parte F. Riscos e como a lista evita

1. **`C:\ProgramData\ssh` já existe (vazia).** Apagá-la apagaria algo que não é do teste. Evita: o comparador mostra
   que ela existia; a fase 12 proíbe apagá-la; só sai o que nasceu dentro dela (chaves do servidor, `sshd_config`,
   registros), conferido contra a foto 0 com administrador.
2. **O Tailscale do Samuel (parado, ligado à conta da rede do Kaique).** Se ele for ligado durante o teste, os
   aparelhos daquela rede chegariam à porta 22 do PC dele. Evita: nenhum comando no Tailscale; a SSH só por
   127.0.0.1; a senha de teste é longa e aleatória; a janela com a porta aberta dura só as fases 7 a 10; a regra e o
   `sshd` saem na fase 11.
3. **O disco C: (encheu em 16/11).** Evita: `$TRAB` no D:; `--basetemp` no D: em todo `pytest`; `TEMP`/`TMP` no D:
   ao empacotar; a foto anota o espaço livre a cada fase; parar se o C: ficar abaixo de 15 GB.
4. **A pasta dos projetos do Samuel.** Riscos: o programa instalado gravar nela; o Velopack pôr os pacotes nela (A2);
   desinstalar apagar junto. Evita: o programa abre com `LOCALAPPDATA` trocado; a cópia de reserva na fase 0; a
   impressão digital comparada em toda fase.
5. **O disco D: aberto a "Todos".** A conta de testes enxerga e pode mudar o acervo, os livros e a pasta `D:\chaves`.
   Evita: pela SSH só os comandos desta lista; escrita só em `$TRAB\escrita-da-conta-de-testes\`; a conta sai na
   fase 11. Não se mexe nas permissões do D: (é decisão do Samuel).
6. **A pergunta do Windows sem ninguém para responder.** Uma pergunta esquecida trava o passo (o Velopack espera até
   10 minutos). Evita: o Samuel presente e avisado antes de cada uma; nenhuma fase com pergunta começa sem ele.
7. **Uma janela no monitor do Samuel.** O instalador, o "Reiniciar agora" ou o ajudante podem abrir o programa fora
   da área escondida. Evita: tudo lançado de dentro da área escondida; avisar o Samuel antes das fases 2, 4 e 11;
   fechar com `WM_CLOSE` e anotar como achado.
8. **A chave de assinatura do Samuel.** Evita: só o `publicar_versao_kaique.py` a lê, no lugar dela; a chave falsa da
   1.1.4 é outra, criada em `$TRAB\segredo\`; nada com chave vai para o git.
9. **A senha da conta de testes.** Evita: gerada aleatória, só letras e números, guardada só em
   `$TRAB\segredo\` (fora do git) e apagada no fim; nunca no relatório nem na linha de comando; `known_hosts` da SSH
   num arquivo do teste, para não mexer no `C:\Users\fotog\.ssh\known_hosts` do Samuel.
10. **A conta `WsiAccount` e o Tailscale, que já existiam.** Evita: o comparador os mostra iguais; nenhum comando
    da lista cita o nome deles, fora a leitura do `sshd -T` (B2).
11. **Parar no meio.** Se o limite de uso ou um erro derrubar o agente, o Windows fica com o teste pela metade.
    Evita: um `ONDE-PAREI.md` da etapa 5 com a fase atual, e o passo 12 sempre possível a partir das fotos.
12. **O programa aberto pelo Samuel durante o teste.** O atalho "(desenvolvimento)" não marca "programa aberto" e
    não toca no instalado (conferido no código de 16/11), mas muda o `configuracoes.json` dele. Evita: pedir que ele
    não use o programa durante as fases 2 a 11, ou anotar quando usou.

---

## Parte G. Quanto tempo

- Fase 0 e 1 (o agente sozinho, sem o Samuel): **1 h 30 a 2 h** (o empacotamento leva uns 11 minutos por pasta e uns
  10 minutos por `vpk pack`; seis versões).
- Fases 2 a 11 (o Samuel por perto, para umas 8 perguntas do Windows): **2 h 30 a 3 h**. Instalar o OpenSSH pelo
  Windows pode levar de 5 a 15 minutos sozinho.
- Fase 12 e o relatório com prints: **1 h a 1 h 30**.
- **Total: de 5 a 6 horas**, de preferência num dia só, com o Samuel por perto na parte do meio.
