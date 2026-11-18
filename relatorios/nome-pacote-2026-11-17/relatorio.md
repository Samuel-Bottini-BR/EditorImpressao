# Conserto: o nome interno do pacote deixa de ser o da pasta dos projetos

17/11/2026, implementador. Cópia `.claude\worktrees\nome-pacote`, ramo `nome-pacote-2026-11-17`, a partir de `59678e22`.
Pedido: D-763 (Samuel, 17/11: "ok, pode fazer"). Teste de máquina.

## Em uma frase

**O nome interno que a peça de atualização usa passou de `EditorImpressao` para `EditorImpressaoPrograma`, e agora nada
que essa peça grava ou apaga ao abrir e ao desinstalar cai na pasta dos projetos.** O Kaique não vê diferença nenhuma.

- **Achado novo na prova repetida:** o desinstalador do Velopack 1.2.161 não apaga a pasta do **nome** do pacote; apaga a
  do **título** ("Editor de Impressão"). Em 17/11 os dois eram iguais no programa de mentira, por isso pareceu ser o nome.
  O título já era diferente da pasta dos projetos e não muda; a prova nova cobra os dois.
- **Um teste antigo acusa erro** com o nome novo e **não foi mudado**: ele confere o nome do arquivo da assinatura escrito
  à mão. Vai como pergunta ao Samuel (no fim).

## O que mudou

| Arquivo | O quê |
|---|---|
| `versao.py` | `ID_DO_PACOTE = "EditorImpressaoPrograma"` e o comentário da regra (por que pode trocar agora e nunca mais depois da primeira instalação) |
| `atualizacao.py` | só o comentário do topo: a frase falsa "Os projetos do Kaique nunca são tocados" agora diz onde o Velopack grava e o que o desinstalador apaga |
| `empacotar.py` | `VERSAO_DO_VPK = "1.2.161"` e `COMO_INSTALAR_O_VPK` (o "instale com" diz `--version 1.2.161`), com o aviso de repetir a prova antes de subir |
| `publicar_versao_kaique.py` | o "instale com" usa `empacotar.COMO_INSTALAR_O_VPK`; comentário |
| `assinatura.py` | só comentários (os exemplos de nome de arquivo) |
| `requirements.txt` | `velopack==1.2.161` já estava preso; ganhou o aviso de repetir a prova |
| `tests/test_nome_do_pacote.py` | **novo**, 5 testes |

**A regra num lugar só:** o nome mora em `versao.ID_DO_PACOTE`; todo o resto lê dali (lista "caminho → de onde lê" no
`ONDE-PAREI.md`). Nenhum lugar do programa tem o nome escrito à mão.

## A prova nova (`tests/test_nome_do_pacote.py`)

1. o nome do pacote nunca é o nome da pasta dos projetos (sem diferenciar maiúsculas);
2. a pasta de reserva (`LocalAppData\<nome>`, `packages\`, `Update.exe`) não é a dos projetos nem fica dentro dela;
3. o que o desinstalador apaga (`LocalAppData\<título>` e `LocalAppData\<nome>`) não é a pasta dos projetos;
4. o `--packId` do comando do vpk é `versao.ID_DO_PACOTE` (o "um lugar só");
5. o `velopack` do pip e o `vpk` presos na mesma versão, 1.2.161.

| | Resultado |
|---|---|
| Código antigo (`59678e22`, numa cópia destacada) | **4 falharam**, 1 passou (o 4: o `--packId` já lia do lugar certo) — `provas/prova-nova-no-codigo-antigo.txt` |
| Código novo | **5 passaram** — `provas/prova-nova-no-codigo-novo.txt` |

## A prova de 17/11 repetida, com o nome novo

Programa de mentira `ProvaNome.exe` (sem janela), com o `atualizacao.py` novo, montado pelo **mesmo comando** do
programa (`empacotar.comando_do_vpk`). Os nomes saem da mesma regra, nunca escritos à mão:

- pacote de mentira = `versao.ID_DO_PACOTE` + "Prova" = **`EditorImpressaoProgramaProva`**;
- pasta dos dados de mentira = `historico.pasta_de_dados().name` + "Prova" = **`EditorImpressaoProva`**, com um projeto de
  mentira dentro (`projetos\livro-de-mentira\projeto.json`, `configuracoes.json`, `historico.json`).

Trocas só da prova: `.msi` "Either" (instala só para a conta, sem pergunta do Windows, como em 17/11), sem atalhos, título
"Prova do nome do pacote". Instalado com `msiexec /qn`. Nenhuma pergunta do Windows, nenhuma janela.

### Caso A — pasta da instalação trancada (como Arquivos de Programas para o Kaique)

A cada chamada de abertura (`App().run()`, `versao_que_roda`, `e_portatil`, `procurar_ao_abrir`) o Velopack avisou
"Acesso negado" na pasta do programa e criou **`C:\Users\fotog\AppData\Local\EditorImpressaoProgramaProva\`** com
`Update.exe` (5,4 MB) e `packages\` vazia. O "procurar e baixar" do ajudante pôs lá a versão 1.0.1 (20 MB), depois de
conferir a assinatura de mentira. A pasta dos dados de mentira ficou igual do começo ao fim. Fotos: `provas/fotos/A-*.txt`.

### Caso B — pasta da instalação aberta (como o ajudante, que roda como o sistema)

Nenhuma pasta de reserva. A 1.0.1 foi para `<instalado>\packages\`. Foto: `provas/fotos/B-procurar-e-baixar.txt`.

### Desinstalar

| | O que havia antes | O que o desinstalador apagou | O que ficou |
|---|---|---|---|
| **C1** (depois do caso A) | pasta de reserva com a 1.0.1 e um projeto de mentira; pasta dos dados de mentira | a pasta instalada | **`...\Local\EditorImpressaoProgramaProva` inteira** (Update.exe, packages, projeto de mentira) e **`...\Local\EditorImpressaoProva` inteira** |
| **C2** (depois do caso B) | projeto de mentira em `...\Local\EditorImpressaoProgramaProva`, em `...\Local\EditorImpressaoProva` e em `...\Local\Prova do nome do pacote` (o título); uma marca em `%TEMP%\velopack_Prova do nome do pacote` | a pasta instalada, **`...\Local\Prova do nome do pacote`** e **`%TEMP%\velopack_Prova do nome do pacote`** | `...\Local\EditorImpressaoProgramaProva` e **`...\Local\EditorImpressaoProva` (os "projetos")** |

- Quem apaga: a limpeza do `.msi` (`RustCleanup` → `CleanupDeferred`) recebe
  `<pasta instalada>"Prova do nome do pacote"<Temp>`, ou seja, **o título** (`provas/trechos-do-msi.txt`). No modelo do
  WiX do vpk 1.2.161: `<Property Id="RustAppId" Value="{{AppTitle}}"/>`.
- O nosso gancho `ao_desinstalar` só anotou (`provas/registro-do-app.txt`).
- **A pasta dos projetos de mentira sobreviveu às duas desinstalações.**

### O `.msi` com o título de verdade (só lido, sem instalar)

Montado pelo mesmo comando do programa (`PerMachine`, título "Editor de Impressão"), com o nome de mentira:
`RustAppId = Editor de Impressão`; a pasta em Arquivos de Programas = `Editor de Impressão` (com acento); a entrada na
lista de programas = chave `MSI:<nome>`, mostrando "Editor de Impressão" (`provas/msi-com-o-titulo-de-verdade.txt`).

**Para o programa de verdade, então:** ao abrir sem administrador, o Velopack grava em
`%LOCALAPPDATA%\EditorImpressaoPrograma`; ao desinstalar, apaga `%LOCALAPPDATA%\Editor de Impressão` e
`%TEMP%\velopack_Editor de Impressão`. Nenhuma das três é `%LOCALAPPDATA%\EditorImpressao`.

### A pasta de verdade dos projetos

Só os nomes do primeiro nível, em todas as fotos, do começo ao fim: `configuracoes.json, erros.log, historico.json,
projetos`. Nada foi gravado, mudado ou apagado nela. `%LOCALAPPDATA%\EditorImpressaoPrograma` nunca apareceu.

## Testes

- **No PC, um arquivo por vez** (código novo): `test_decisoes_atualizacao` 37 passaram, **1 falhou** (o da pergunta);
  `test_assinatura` 16; `test_decisoes_desinstalar` 46; `test_decisoes_desinstalar_pasta` 6;
  `test_decisoes_ajudante_da_atualizacao` 37; `test_decisoes_preparo_d749` 8; `test_decisoes_testes_a_distancia` 13;
  `test_empacotar` 41; `test_sem_janela_na_tela` 8; `test_nome_do_pacote` 5. Todos passaram, menos aquele um.
- **GitHub, 1ª rodada (44190676442, código de `13e897d7`):** só falhou a parte 3, e só com
  `test_d724_o_que_o_publicar_assina_o_programa_aceita` (o da pergunta). Botões e prints e as partes 2, 4 e 5 passaram.
- **GitHub, rodada final (44193535388, commit `b076169e`):** a mesma coisa. Passaram os botões e prints da janela real e as partes 1, 2, 4 e 5; a parte 3 falhou só com `test_d724_o_que_o_publicar_assina_o_programa_aceita` (1 falhou, 37 passaram nesse arquivo). Nenhum outro teste falhou.

## Como cumpri cada decisão

- **D-763:** nome trocado num lugar só (`versao.ID_DO_PACOTE`); prova nova falha no antigo e passa no novo; prova de
  17/11 repetida; o Kaique continua vendo "Editor de Impressão" (o `.msi` lido mostra).
- **D-723:** o mesmo Velopack, o mesmo comando de empacotar (`PerMachine` no programa; "Either" só na prova).
- **D-724:** a versão de mentira foi aceita só com a assinatura de mentira conferida ("publicada e assinada":
  `provas/atualizacao-de-mentira.log`). A chave do Samuel não foi usada.
- **D-731 e §7:** os projetos de mentira sobreviveram ao desinstalar; o nosso gancho não mudou.
- **D-732, D-733, D-740, D-750, D-751, D-727:** nada tocado. A tarefa ajudante continua `EditorImpressao\Procurar versao
  nova`; a pasta do Agendador continua "EditorImpressao".
- **§11.8:** nenhum teste antigo mudado. O que falha virou pergunta.

## Ressalvas

- **O desinstalar de verdade (`.msi` para todo o computador, com administrador) não foi provado.** Nele a limpeza roda
  como o sistema (`Impersonate="no"`). Pelo que se leu no arquivo da limpeza, ela usa a variável `LOCALAPPDATA` de quem
  roda, então deve apagar `C:\Windows\System32\config\systemprofile\AppData\Local\Editor de Impressão`. Não é a pasta dos
  projetos em nenhum dos dois casos, mas só a etapa 5 confirma.
- **O que a prova de 17/11 disse sobre desinstalar estava certo para o programa de mentira, não para o de verdade.** Com o
  nome antigo e o título "Editor de Impressão", o desinstalador 1.2.161 provavelmente não apagaria os projetos (apaga a
  pasta do título). O conserto continua necessário: a cada abertura o Velopack gravaria `Update.exe` e `packages\` dentro
  da pasta dos projetos, e um Velopack mais novo (limpeza `UserCleanupDeferred`) apaga `%LocalAppData%\<nome>`.
- **O `vpk` instalado não é conferido na hora de empacotar:** a versão está escrita e o teste cobra que ela bate com a do
  pip, mas quem rodar `dotnet tool update` passa a montar com outra (ideia abaixo).
- A pasta trancada só negava criar arquivos na raiz, como em 17/11.

## Bugs para a Lista de bugs (não impedem; não consertei)

- **17/11/2026: desinstalar deixa uma sobra na conta do Kaique.** O desinstalador do Velopack 1.2.161 não apaga a pasta
  de reserva `%LOCALAPPDATA%\EditorImpressaoPrograma` (o `Update.exe` de 5 MB e `packages\`): ela fica depois de
  desinstalar. Não toca nos projetos. Prova: `provas/fotos/C1-depois-de-desinstalar.txt` e `C2-depois-de-desinstalar.txt`.
- **17/11/2026: a lista da etapa 5 espera a pasta errada em Arquivos de Programas.** `lista.md` (D-723),
  `comandos.md` (`$INSTALADO`) e `fotografo.py` (`programa_novo`) esperam `C:\Program Files\EditorImpressao`; o `.msi`
  instala em `C:\Program Files\Editor de Impressão` (do título). Isso já valia antes deste conserto.

## Ideias para a Lista de espera

- `empacotar.py` recusar empacotar se o `vpk` instalado não for `VERSAO_DO_VPK` (hoje só o "instale com" diz a versão).
- O fotógrafo da etapa 5 fotografar também `%LOCALAPPDATA%\EditorImpressaoPrograma`, `%LOCALAPPDATA%\Editor de Impressão`
  e `C:\Windows\System32\config\systemprofile\AppData\Local\Editor de Impressão` antes e depois de desinstalar.

## Textos da etapa 5 que citam o nome antigo (para a gerente atualizar; não mudei)

Em `.claude\worktrees\etapa5\relatorios\frente-kaique-2026-11-16\etapa5\`:
- `lista.md:36-38` (A2): "Se for dentro de `%LOCALAPPDATA%\EditorImpressao` [...] pare e avise a gerente".
- `lista.md:54-61` (A2, a parada): "O id é `EditorImpressao`. Ou seja: `%LOCALAPPDATA%\EditorImpressao\packages` e
  `...\Update.exe`, dentro da pasta dos projetos" → agora `%LOCALAPPDATA%\EditorImpressaoPrograma`.
- `lista.md:273` (D-723): "o programa em `C:\Program Files\EditorImpressao`" → `C:\Program Files\Editor de Impressão`
  (do título; já estava errado antes).
- `lista.md:342-343` (desinstalar): acrescentar o que o desinstalador apaga (`%LOCALAPPDATA%\Editor de Impressão`,
  `%TEMP%\velopack_Editor de Impressão`) e a sobra `%LOCALAPPDATA%\EditorImpressaoPrograma`.
- `comandos.md:28-30` (a parada A2): `%LOCALAPPDATA%\EditorImpressao\packages` → `%LOCALAPPDATA%\EditorImpressaoPrograma\packages`.
- `comandos.md:41`: `$INSTALADO = "C:\Program Files\EditorImpressao"` → `"C:\Program Files\Editor de Impressão"`.
- `comandos.md:184`: `velopack_EditorImpressao.log` → `velopack_EditorImpressaoPrograma.log`.
- `fotografo.py:347`: `programa_novo` em `C:\Program Files\EditorImpressao` → `C:\Program Files\Editor de Impressão`.
- Os pacotes publicados no `$TRAB\servidor` passam a se chamar `EditorImpressaoPrograma-<versão>-full.nupkg` e
  `EditorImpressaoPrograma-<versão>.assinatura` (`lista.md:137` fala só "os 6 pacotes", sem nome: não precisa mudar).

## O que criei fora do projeto

- `D:\agente_temp_testes\nome-pacote\` (~185 MB): o programa de mentira, os pacotes, os registros do `.msi`, as fotos.
  Deixado para o verificador repetir; pode ser apagado inteiro.
- Apagados por mim no fim: `C:\Users\fotog\AppData\Local\EditorImpressaoProva` e `...\EditorImpressaoProgramaProva`, a
  cópia destacada do código antigo e as pastas temporárias do pytest.
- Tirados pelo próprio desinstalador: as duas instalações, `...\Local\Prova do nome do pacote`,
  `%TEMP%\velopack_Prova do nome do pacote` e a entrada nos programas instalados (conferido).
- `D:\Config.Msi` (do sistema, de 17/11): o Windows Installer deu de novo o erro 1926 nela. Não mexi.

## Pergunta para o Samuel (formato do CLAUDE.md §11.13)

**Do que se trata:** é a troca do nome interno da peça que atualiza o programa no notebook do Kaique, que você mandou
fazer hoje ("ok, pode fazer"). Esse nome também vai no nome de um arquivo pequeno que acompanha cada versão nova, a
"assinatura" que prova que a versão é sua. Com o nome novo, o arquivo passa de `EditorImpressao-1.2.0.assinatura` para
`EditorImpressaoPrograma-1.2.0.assinatura`.

**O que acontece hoje:** um teste antigo, de 16/11, confere esse nome escrito à mão, com o nome antigo, e por isso acusa
erro. **Não é defeito do programa:** é efeito da troca de nome. O mesmo teste continua mostrando que o programa aceita a
versão assinada.

**O que você escolhe:** posso mudar esse teste antigo para conferir o nome novo, lido do mesmo lugar que o programa usa?
- **Sim (sugiro):** o teste continua cobrando o mesmo. Nada que o Kaique vê muda.
- **Não:** o nome interno não pode trocar, e a peça de atualização continua gravando na pasta dos projetos do Kaique.
- **Só comentário.**

**Situação:** feito na cópia de teste; espera este "sim" para entrar na versão de teste. A etapa 5 espera este conserto.
