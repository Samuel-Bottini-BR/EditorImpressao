# Experimento do passo 1: preparado para a gerente e o Samuel rodarem

23/11/2026. Pesquisador. Só leitura: nada foi mudado no Windows, no programa instalado, no código, nos testes nem no git.
Nada rodou na instalação de verdade. Os comandos do Python foram conferidos numa **instalação falsa no rascunho**
(só a procura; nada baixado, nada trocado), e não deixaram nada fora do rascunho.

Pedido: preparar o "Passo 1 — Experimento" da resposta do Fable (D-830, Samuel 23/11: "refazer"). Dar à pasta
`C:\Program Files\EditorImpressaoPrograma` a licença de Modificar para Usuários (`S-1-5-32-545`) e ver se uma conta
comum baixa, troca `current` e reabre com o Velopack, sem pergunta do Windows (UAC).

"**Fato**" = lido no código do Velopack 1.2.161, nos bytes do arquivo instalado, num registro ou no Windows (comando só
de leitura). "**Palpite**" = dedução minha. "**Não conferi**" = não deu para ver.

---

## A resposta curta

1. **O `Update.exe` instalado não pede administrador** (fato: o manifesto embutido diz `asInvoker`). Ele só pede a
   licença por conta própria quando acha que **não consegue gravar** na pasta do programa. Com a licença nova, ele
   consegue, e então não pergunta nada.
2. **Fora da pasta, a troca só tenta mexer numa coisa que a conta comum não alcança:** o número da versão em "Programas
   e Recursos" (registro da máquina). Ela falha em silêncio, só com um aviso no registro do Velopack, e a troca segue.
   A tranca (`packages\.velopack_lock`) é só um arquivo dentro da pasta. Os atalhos do `.msi` não são tocados e
   continuam valendo.
3. **Dá para rodar os passos 2 a 4 sem mudar o `atualizacao.py` e sem arquivo de script:** chamando, no Python do
   `.venv`, as próprias funções do Velopack 1.2.161 (`check_for_updates`, `download_updates`,
   `apply_updates_and_restart`, `wait_exit_then_apply_updates`) apontadas para a instalação. Os comandos estão no
   roteiro (seção 6).
4. **Há versões prontas, nada a montar:** está instalada a 1.1.0; a 1.1.1 e a 1.1.2 já estão montadas e assinadas em
   `C:\EditorImpressaoProva\versoes 3\`. Passo 2: 1.1.0 → 1.1.2. Passo 4: 1.1.2 → 1.1.1 (volta permitida).
5. **Antes, é preciso desligar o ajudante SYSTEM e tirar do caminho o `estado.json`:** hoje o `estado.json` diz
   "1.1.1 esperando". Se a 1.1.0 for aberta pelo atalho, o programa começa a troca pelo caminho antigo antes da janela.
   Uma pergunta do Windows prepara tudo, outra desfaz. Tempo total: cerca de 30 minutos.

| O que é | Licença | Roda aqui? | Roda no notebook do Kaique? |
|---|---|---|---|
| Velopack 1.2.161 (`Update.exe`, o atalho e a biblioteca do Python `velopack`, a mesma versão do `.venv`) | MIT (pode usar e mudar; manter o aviso de copyright) | sim (já instalado) | sim, é a mesma instalação. Palpite: lá ninguém precisa do `.venv`, porque o programa novo chamaria as mesmas funções de dentro dele |
| `icacls` e `schtasks` (do Windows) | parte do Windows | sim | sim |
| Python do `.venv` (só para o experimento) | PSF | sim (3.14) | não precisa |

---

## 1. As duas dúvidas que o Fable deixou

### 1a. O `Update.exe` 1.2.161 pede administrador? **Não.**

- **Fato (bytes do arquivo instalado).** `C:\Program Files\EditorImpressaoPrograma\Update.exe`: versão do arquivo
  1.2.161, produto "Velopack", 64 bits. O manifesto embutido tem um só `requestedExecutionLevel`:
  `<requestedExecutionLevel level="asInvoker" uiAccess="false" />`, com o comentário `<!-- No UAC needed-->`.
  O atalho `Editor de Impressão.exe` e o `current\EditorImpressao.exe` também são `asInvoker`.
- **Fato (código).** O manifesto vem de [`src/bins/app.manifest`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/app.manifest),
  embutido por [`src/bins/build.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/build.rs)
  (`set_manifest_file("app.manifest")`). Bate com os bytes.
- **Palpite (Windows).** Como o manifesto declara o nível, o Windows não aplica o "detector de instalador", que pediria
  licença a um `.exe` com "update" no nome.
- **Fato (código; é aqui que o UAC pode aparecer).** Em [`apply_windows_impl.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/commands/apply_windows_impl.rs),
  antes de trocar, o Velopack testa se a pasta do programa aceita gravação (`is_directory_writable`: tenta criar
  `<raiz>\.velopack_dir_test`, que se apaga ao fechar). **Se não aceita**, e o processo não é administrador, ele
  **se reabre como administrador** (`run_process_as_admin`, "Re-launching as administrator to update in ..."), e é
  isso que faz o UAC aparecer. Se aceita, segue sem pedir nada.
- **Fato (registro de 22/11 na conta do Samuel,** `%LOCALAPPDATA%\velopack\velopack_EditorImpressaoPrograma.log`**).**
  Hoje, sem a licença, toda abertura pelo atalho registra `Failed to open directory for writing ...\.velopack_dir_test:
  Acesso negado (os error 5)` e `Root directory ... writable: false`. O teste de gravação é exatamente o que a
  licença nova muda.

**Achado que muda a leitura do problema (fato, [`locator.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/lib-rust/src/locator.rs) `new_with_manifest`, e o mesmo registro):**
o Velopack 1.2.161 já tem um jeito próprio para instalação por máquina. Quando a raiz não aceita gravação, ele usa
`%LOCALAPPDATA%\EditorImpressaoPrograma\packages` e uma cópia do `Update.exe` ali ("Using fallback directory"). Na
conta do Samuel essa pasta já existe desde 22/11, com o `Update.exe` copiado e `packages` vazia. Nesse jeito, o
download não pede nada, mas **cada troca pede o UAC** (a reabertura como administrador acima). É o "jeito 2" que o
Samuel recusou na D-733. Com a licença nova, a raiz passa a aceitar gravação e esse desvio não é usado: o pacote vai
para `<raiz>\packages`.

### 1b. O `apply` e a tranca mexem em algo fora da pasta? Uma conta comum consegue?

Tudo o que a troca faz, lido em [`apply_windows_impl.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/commands/apply_windows_impl.rs),
[`registry.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/windows/registry.rs),
[`shortcuts.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/windows/shortcuts.rs),
[`lockfile.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/lib-rust/src/lockfile.rs) e
[`manager.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/lib-rust/src/manager.rs):

| O que a troca faz | Onde | Conta comum, com a licença nova | Fonte |
|---|---|---|---|
| Tranca | `packages\.velopack_lock`: só um arquivo aberto para leitura e gravação. Sem registro, sem marca global do Windows. O download também segura a tranca (`manager.rs`, começo de `download_updates`). | **sim** (hoje o arquivo dá só leitura aos Usuários; com `/T` passa a Modificar) | fato |
| Baixar | `packages\<nome>.partial` → renomeia → apaga os `.nupkg` antigos → **reescreve `<raiz>\Update.exe`** com o do pacote (`Squirrel.exe`) | sim (tudo dentro da pasta) | fato |
| Pré-requisitos (Visual C++ etc. do manifesto) | só se o pacote declarar `runtimeDependencies` | **nada a fazer:** o `.nuspec` da 1.1.1 e da 1.1.2 não declara nenhuma (fato, lido dentro do pacote). Com uma dependência declarada, o Velopack tentaria instalá-la e aí haveria UAC (palpite) | fato + palpite |
| Ganchos | roda `current\EditorImpressao.exe --veloapp-obsolete` (antes) e `--veloapp-updated` (depois), na conta de quem trocou | sim. No código instalado (`93d9e3b8`), o `ao_atualizar` não faz nada e o `--veloapp-obsolete` só entra e sai | fato |
| Fechar à força | o que roda de dentro da raiz | sim, para os processos da própria conta | fato |
| Trocar | renomeia `current` → `packages\VelopackTemp\tmp_*` e a nova → `current` | sim (Modificar inclui apagar) | fato |
| "Programas e Recursos" | instalação `.msi` (há `<raiz>\.msi-installed`): só tenta mudar `DisplayVersion` em `HKCU`, senão em `HKLM\...\Uninstall\MSI:EditorImpressaoPrograma` | **não consegue:** a chave do `HKLM` dá só leitura aos Usuários (lido agora). Falha, fica uma linha "Failed to update uninstall entry" no registro do Velopack, e a troca **segue** (o código ignora a falha). Efeito: "Programas e Recursos" continua dizendo 1.1.0. O texto da falha diz "Could not find MSI uninstall registry key", mas a causa real é a falta de licença: o código cai nesse texto em qualquer erro ao abrir a chave (palpite) | fato + palpite |
| Atalhos | só procura e atualiza atalhos nas pastas **da própria conta** (Área de Trabalho, Menu Iniciar, Inicializar, fixados). Atalho novo só nasce se a versão nova pedir um lugar que a anterior não tinha; a 1.1.0, a 1.1.1 e a 1.1.2 pedem os mesmos (`Desktop,StartMenuRoot`) | sim; e não há nada a mudar | fato |
| Atalhos do `.msi` | `C:\Users\Public\Desktop\Editor de Impressão.lnk` e `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Editor de Impressão.lnk` apontam para `<raiz>\Editor de Impressão.exe`, que não muda de lugar | não são tocados e continuam valendo | fato (lido agora) |
| Atalho `Editor de Impressão.exe` | reescrito na raiz no fim da troca (`extract_stubs_to_dir`; erro ignorado) | sim | fato |
| Registro do Velopack | `%LOCALAPPDATA%\velopack\velopack_EditorImpressaoPrograma.log`, da conta que roda | sim | fato |
| Desinstalar pelo `.msi` | o gancho de desinstalar roda na conta da pessoa (`Impersonate="yes"`). Só a limpeza que apaga a pasta roda como SYSTEM, e ela não executa nada da pasta | não é parte do experimento | fato ([`MsiTemplate.hbs`](https://github.com/velopack/velopack/blob/1.2.161/src/vpk/Velopack.Packaging.Windows/Msi/Templates/MsiTemplate.hbs)) |

**Resposta:** fora da pasta, a conta comum só não consegue mudar o número da versão em "Programas e Recursos", e isso
não impede a troca. Palpite forte: com Modificar na raiz inteira, `download_updates` e `apply` passam inteiros, sem
UAC. É o que o experimento confirma.

---

## 2. Como rodar os passos 2 a 4 sem mudar o `atualizacao.py` e sem script nosso

**O que o programa instalado faz hoje (fato, `atualizacao.py` em `93d9e3b8`, o commit da 1.1.0 instalada):**
- a janela nunca chama o Velopack para trocar (`set_auto_apply_on_startup(False)`);
- ao abrir, manda o ajudante SYSTEM rodar (`procurar_ao_abrir` → `schtasks /Run`);
- se o `estado.json` diz "versão nova esperando", troca **antes da janela** pelo caminho antigo (`trocar_antes_de_abrir`
  → PowerShell → ajudante).

Por isso o programa instalado não serve para exercitar o fluxo simples.

**Os comandos que o `Update.exe` 1.2.161 tem (fato, [`update.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/update.rs)):**
`apply` (`--package`, `--waitPid`, `--norestart`, `-- <argumentos>`), `start`, `patch`, `uninstall` e
`update-self` (escondido). Opções gerais: `--silent`, `--rootDir`, `--packageDir`, `--log`, `--verbose`. **Não há
comando de procurar nem de baixar**: isso só existe na biblioteca.

**Jeito escolhido (A): a biblioteca `velopack` 1.2.161 do `.venv`, apontada para a instalação.** Fato
([`__init__.pyi`](https://github.com/velopack/velopack/blob/1.2.161/src/lib-python/velopack.pyi) e o pacote do
`.venv`, versão 1.2.161): `UpdateManager(fonte, opções, locator)` aceita um `VelopackLocatorConfig` com a raiz, o
`Update.exe`, `packages`, o `sq.version` e `current`. Com ele, as quatro funções do Fable são as mesmas que o programa
refeito chamaria:
- `check_for_updates` → `download_updates` → `apply_updates_and_restart` monta `Update.exe apply --package <pacote>
  --waitPid <este processo> --root <raiz> --packageDir <raiz>\packages`, lança e sai (fato, `manager.rs`,
  `unsafe_apply_updates`);
- `wait_exit_then_apply_updates(u, silent, restart)` faz o mesmo sem sair.

São cinco linhas de Python digitadas no PowerShell, sem arquivo gravado, chamando só o Velopack. Se a gerente contar
isso como "script", sobra o jeito B.

Conferido no rascunho (instalação falsa com o `sq.version` copiado e o nome trocado): o `VelopackLocatorConfig` com
esses nomes funciona; `check_for_updates` achou a 1.1.2 a partir da 1.1.0; achou a 1.1.1 a partir da 1.1.2 com
`AllowVersionDowngrade=True` (`IsDowngrade=True`), e nada sem essa opção; o jeito de passar o código pelo PowerShell
(texto entre `@'` e `'@`) funcionou. **Não conferi** o download nem a troca: isso é o experimento. A biblioteca do
Python não grava registro em arquivo (fato: não há `init_logging` em `src/lib-python`). Do download, a prova é o
arquivo em `packages\`; da troca, o registro do `Update.exe`.

**Jeito B (só a troca, sem Python):** com o programa fechado,
`& "C:\Program Files\EditorImpressaoPrograma\Update.exe" apply --package "C:\Program Files\EditorImpressaoPrograma\packages\EditorImpressaoPrograma-1.1.1-full.nupkg"`.
O pacote da 1.1.1 já está em `packages\` desde 22/11. Isso testa (b) e (c), mas **não testa o download**. E só vale
**antes** do passo 2a, porque o download da 1.1.2 apaga esse pacote (`download_updates` apaga os `.nupkg` antigos).

**Jeito C, que não recomendo:** `current\EditorImpressao.exe --procurar-atualizacao --fonte <pasta>` na conta comum. Ele
roda o fluxo antigo: Visual C++, motor, tentar criar a tarefa SYSTEM, reabrir escondido em `--conferir-a-versao-nova`.
Mistura as peças que vão sair e não reabre a janela.

---

## 3. Para qual versão trocar

- **Instalada (fato):** `current\sq.version` = **1.1.0**; `versao-do-pacote.json` = commit `93d9e3b8` (volta 3 do
  ramo `atualizador-4-consertos-2026-11-21`), montada em 22/11 13:30. `Update.exe` 1.2.161.
- **Já em `packages\` (fato):** `EditorImpressaoPrograma-1.1.1-full.nupkg` (baixado em 22/11 pelo ajudante; a troca
  falhou com o erro 32), mais `.velopack_lock`, `.betaId` e `VelopackTemp\` vazia.
- **Prontas (fato), `C:\EditorImpressaoProva\versoes 3\`:** `v1.1.0` (pacote + `.msi`), `v1.1.1`, `v1.1.2`, cada uma
  com `releases.win.json`, pacote e `.assinatura`. A montagem conferiu as somas e a assinatura (`atualizador4-1.1.x.log`).
  A 1.1.1 e a 1.1.2 são do mesmo commit `93d9e3b8`, com 1 arquivo mudado sem commit (palpite: o `versao.py`), e não
  declaram pré-requisito.
- `C:\EditorImpressaoProva\servida\` tem só a 1.1.1 (é a "fonte de teste" do `fonte-de-teste.txt`).
- **GitHub:** `gh release list` não mostra nenhuma publicação (fato).
- **O que usar:** passo 2: **1.1.0 → 1.1.2**, fonte `C:\EditorImpressaoProva\versoes 3\v1.1.2` (download de verdade:
  460 MB copiados da pasta). Passo 4: **1.1.2 → 1.1.1**, fonte `...\v1.1.1`, com `AllowVersionDowngrade=True` (download
  de verdade de novo, porque o passo 2 apagou o pacote da 1.1.1). Passo 5 (opcional): **1.1.1 → 1.1.0**, fonte
  `...\v1.1.0`, para o programa terminar como começou. **Nada a montar.**
- A assinatura Ed25519 é coisa nossa (`atualizacao.py`). O Velopack não a confere, e o experimento não a testa (não é
  o que se quer medir).
- Fonte por endereço `http://`: o `servidor_das_versoes.py` (ramo `atualizador-4-consertos-2026-11-21`) serve a pasta,
  e o `Update.exe` faria o mesmo. Mas ele junta todas as versões num índice só, com a mais nova primeiro, e aí o
  passo 4 (voltar para a 1.1.1) não acharia nada (palpite, lendo o cabeçalho dele). A pasta basta: o que se mede é a
  gravação no disco, igual nos dois.

---

## 4. O que limpar antes e como desfazer depois

### Como está hoje (fato, lido agora)

- **Tarefas** (`schtasks /Query`), as duas "Habilitado", "Pronto", rodando como SISTEMA, só quando alguém manda:
  - `\EditorImpressao\Procurar versao nova` → `C:\Program Files\EditorImpressaoPrograma\current\EditorImpressao.exe
    --procurar-atualizacao` (rodou pela última vez em 22/11 14:35:53, resultado 0);
  - `\EditorImpressao\Desfazer testes a distancia` → `powershell.exe ... -File
    "C:\ProgramData\EditorImpressao\testes-a-distancia\desfazer.ps1"` (nunca rodou).
- **Licença da pasta** (`icacls`): só herdada de `C:\Program Files`. Usuários têm `(RX)` e `(OI)(CI)(IO)(GR,GE)`;
  Administradores, SISTEMA e TrustedInstaller têm controle total; PROPRIETÁRIO CRIADOR tem `(OI)(CI)(IO)(F)`.
  **Varri os 38.547 itens: nenhuma licença própria, nenhum item com a herança cortada, todos com dono SISTEMA.** Por
  isso "voltar a ser herdada em tudo" devolve exatamente a licença de hoje.
- **`C:\ProgramData\EditorImpressao\atualizacao\estado.json`** = `{"fase": "pendente", "nova": "1.1.1", "anterior":
  "1.1.0"}` (dono SISTEMA; Usuários só leem). Com a 1.1.0 aberta, isso é "versão nova esperando": **abrir a 1.1.0 pelo
  atalho começa a troca pelo caminho antigo antes da janela** (`trocar_antes_de_abrir`, fato no código `93d9e3b8`).
- `C:\ProgramData\EditorImpressao\fonte-de-teste.txt` aponta para `C:\EditorImpressaoProva\servida`. Pode ficar: só o
  ajudante o usa.
- Nenhum processo roda de dentro da pasta agora. Há 56 GB livres no `C:` (a troca precisa de cerca de 2 GB).
- Contas: `fotog` (o Samuel) é administrador; numa janela comum, o grupo Administradores fica "apenas para negar" e o
  nível é Médio. Para as licenças de arquivo, ela funciona como conta comum. **Não há conta padrão neste PC**
  (`EditorTestes` não existe mais).

### Desligar, não apagar, o ajudante (recomendo)

`schtasks /Change /TN "\EditorImpressao\Procurar versao nova" /DISABLE` (precisa de administrador).
- **Por que desligar, e não apagar (fato, código `93d9e3b8`).** A leitura que decide se a pergunta do Windows volta
  (`ler_o_computador` → `ler_xml_da_tarefa`) olha só o comando, os argumentos, a conta e a licença da tarefa, não se
  ela está ligada. Desligada, o programa acha que "está preparado" e **não pergunta nada** ao abrir.
- **Apagada,** o programa (1.1.x) **pede o UAC de "preparar o computador" em toda abertura** (D-735). Se alguém
  clicar "Sim", o ajudante SYSTEM é recriado e o experimento se estraga.
- Com ela desligada, o `schtasks /Run` que a janela faz ao abrir falha. O Windows devolve `SCHED_E_TASK_DISABLED`
  ([MS-TSCH, SchRpcRun](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-tsch/77f2250d-500a-40ee-be18-c82f7079c4f0)),
  e o programa só anota "não consegui chamar o ajudante" (fato: `procurar_ao_abrir` só anota). **Não conferi** o
  texto exato que o `schtasks` mostra.
- **A tarefa "Desfazer" pode ficar como está.** Ela só roda quando o gancho de desinstalar manda, e roda um script do
  `ProgramData`, não da pasta do programa.
- **Se preferirem apagar as duas:** `schtasks /Delete /TN "\EditorImpressao\Procurar versao nova" /F` e
  `schtasks /Delete /TN "\EditorImpressao\Desfazer testes a distancia" /F`. Ficam pela metade: a pasta
  `\EditorImpressao` vazia no Agendador, o `desfazer.ps1` sem uso no `ProgramData`, a pergunta do Windows a cada
  abertura (a resposta tem de ser "Não") e o desinstalar sem a limpeza dos testes à distância (que hoje não há o que
  limpar).

### Tirar o `estado.json` do caminho

`Rename-Item -LiteralPath "C:\ProgramData\EditorImpressao\atualizacao\estado.json" -NewName "estado.json.antes-do-experimento"`
(precisa de administrador; o dono é SISTEMA). Sem ele, a situação é "nada": nenhuma troca antes da janela, nenhum
aviso. Volta com o nome de antes.

### Dar a licença (o comando do Fable, escrito para o PowerShell)

`icacls "C:\Program Files\EditorImpressaoPrograma" /grant "*S-1-5-32-545:(OI)(CI)M" /T /C /Q`

- **No PowerShell, as aspas em volta de `*S-1-5-32-545:(OI)(CI)M` são obrigatórias:** sem elas, os parênteses viram
  código do PowerShell e o comando quebra.
- **Não conferi** como o `icacls` com `/T` grava em cada arquivo (licença própria em cada um ou só herdada). O
  desfazer abaixo cobre os dois casos.

### Desfazer (volta a licença e o dono ao que são hoje)

Rodar como administrador, **nesta ordem**:
```
icacls "C:\Program Files\EditorImpressaoPrograma" /setowner "*S-1-5-18" /T /C /Q
icacls "C:\Program Files\EditorImpressaoPrograma" /reset /T /C /Q
```
- `/reset` = "Replaces ACLs with default inherited ACLs for all matching files"
  ([icacls, Microsoft](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls)). Como
  hoje tudo é herdado, isso devolve a licença de hoje.
- **Por que o dono primeiro (palpite).** O que a conta comum criar na troca (o `current` novo, os pacotes) nasce com o
  Samuel de dono, e com isso ele ganha controle total pelo PROPRIETÁRIO CRIADOR. Trocando o dono para SISTEMA antes do
  `/reset`, a herança volta a dar esse controle ao SISTEMA, como hoje. **Não conferi** o `/setowner` para SISTEMA
  aqui. É o mesmo uso comum de devolver arquivos ao TrustedInstaller.
- **Conferir depois (só leitura, sem UAC, cerca de 1 a 2 minutos):** a mesma varredura feita hoje.
  ```
  $r="C:\Program Files\EditorImpressaoPrograma"; $i=@(Get-Item $r -Force)+@(Get-ChildItem $r -Recurse -Force); $e=0;$p=0;$d=@{}; foreach($x in $i){$a=Get-Acl -LiteralPath $x.FullName; if($a.AreAccessRulesProtected){$p++}; if(@($a.Access|?{-not $_.IsInherited}).Count){$e++}; $d[$a.Owner]++}; "itens $($i.Count); com licença própria $e; herança cortada $p"; $d
  ```
  O certo: "com licença própria 0; herança cortada 0", e todos com dono `AUTORIDADE NT\SISTEMA`.
- **O que não volta:** o conteúdo. O `current` fica na versão do último passo (1.1.1, ou 1.1.0 com o passo 5). "Programas
  e Recursos" segue dizendo 1.1.0 em qualquer caso. A pasta `%LOCALAPPDATA%\EditorImpressaoPrograma` (de 22/11) fica
  como está.
- **Para voltar o resto como está hoje:** `Rename-Item -LiteralPath "C:\ProgramData\EditorImpressao\atualizacao\estado.json.antes-do-experimento" -NewName "estado.json"`
  (o comando falha, sem estragar nada, se já houver um `estado.json`). Depois,
  `schtasks /Change /TN "\EditorImpressao\Procurar versao nova" /ENABLE`.
  **Ligar a tarefa só depois do `/reset`:** enquanto os Usuários podem mudar a pasta, a tarefa ligada rodaria como
  SYSTEM um `.exe` que qualquer conta pode trocar. Se o ajudante deve voltar a ser ligado, já que vai sair no desenho
  novo, é escolha da gerente com o Samuel.

---

## 5. O risco da licença (três linhas)

1. Com Modificar para Usuários, **qualquer conta do PC** (e qualquer programa ruim rodando sem administrador nela) pode
   trocar o `EditorImpressao.exe`, as bibliotecas, o `Update.exe` e o atalho. Na instalação em `%LOCALAPPDATA%`, só a
   própria conta pode.
2. Para o Kaique, o risco é igual ao da instalação na conta dele. O que muda é **entre contas e com licença**: se um
   administrador, o SYSTEM (o ajudante de hoje, se continuar ligado) ou a conta `EditorTestes` do SSH rodar algo dessa
   pasta, roda o que outra conta pôs lá.
3. Por isso o desenho do Fable só é seguro **sem nenhum processo SYSTEM ou de administrador rodando da pasta**: o
   ajudante sai, e o `.msi` já roda os ganchos na conta da pessoa (fato, `MsiTemplate.hbs`). Palpite: abrir o programa
   "como administrador" passa a ser a única porta que resta.

---

## 6. O roteiro (gerente e Samuel)

**Tempo:** cerca de 30 minutos. Os palpites: a licença em 38.547 itens leva de 1 a 3 minutos; cada download (460 MB
da própria máquina) leva menos de 1 minuto; cada troca leva de 40 a 60 segundos (em 22/11, extrair levou 9 s e apagar
o provisório, 20 s); o desfazer leva de 2 a 5 minutos.

**Regras durante o experimento:**
- nenhuma janela do Explorador aberta dentro de `C:\Program Files\EditorImpressaoPrograma`;
- a janela do PowerShell da gerente **fora** dessa pasta (uma pasta aberta impede renomear `current`: é o erro 32 de
  22/11);
- **não abrir o programa pelo atalho** antes do passo 4c;
- se aparecer **qualquer** pergunta do Windows nos passos 2 a 4, é o sinal de falha: anotar o nome do programa que a
  caixa mostra, tirar print e clicar **"Não"**.

### Passo 0 — Anotar o antes (gerente, janela comum, sem UAC)
```
Get-Content "C:\Program Files\EditorImpressaoPrograma\current\sq.version" | Select-String "<version>"
icacls "C:\Program Files\EditorImpressaoPrograma"
schtasks /Query /TN "\EditorImpressao\Procurar versao nova" /FO LIST
tasklist /FI "IMAGENAME eq EditorImpressao.exe"
```
O que deve aparecer: `1.1.0`; a licença da seção 4; a tarefa "Habilitado"; nenhum `EditorImpressao.exe` rodando.

### Passo 1 — Preparar (UAC nº 1)
A gerente abre o "Windows PowerShell" **como administrador**. **O Samuel clica "Sim"** (a caixa diz "Windows
PowerShell", Microsoft Windows). Nessa janela:
```
schtasks /Change /TN "\EditorImpressao\Procurar versao nova" /DISABLE
Rename-Item -LiteralPath "C:\ProgramData\EditorImpressao\atualizacao\estado.json" -NewName "estado.json.antes-do-experimento"
icacls "C:\Program Files\EditorImpressaoPrograma" /grant "*S-1-5-32-545:(OI)(CI)M" /T /C /Q
icacls "C:\Program Files\EditorImpressaoPrograma"
exit
```
O que deve aparecer:
- o `schtasks` responde que mudou a tarefa;
- o `icacls` termina com "falha no processamento de 0 arquivos";
- a última listagem mostra `BUILTIN\Usuários:(OI)(CI)(M)` antes das linhas `(I)`.

**Anotar:** quantos arquivos falharam (o certo é 0) e o texto inteiro de qualquer erro.

### Passo 2 — Baixar e trocar como conta comum (sem UAC)
A gerente abre um PowerShell **comum** (sem "como administrador") e confere o nível:
`whoami /groups | Select-String "S-1-16-8192"` tem de mostrar "Nível Obrigatório Médio". Se mostrar `S-1-16-12288`
(Alto), a janela está como administrador e o teste não vale.

**2a — procurar e baixar a 1.1.2:**
```
$baixar = @'
import velopack as v
R = r'C:\Program Files\EditorImpressaoPrograma'
L = v.VelopackLocatorConfig(RootAppDir=R, UpdateExePath=R + r'\Update.exe', PackagesDir=R + r'\packages', ManifestPath=R + r'\current\sq.version', CurrentBinaryDir=R + r'\current', IsPortable=False)
m = v.UpdateManager(r'C:\EditorImpressaoProva\versoes 3\v1.1.2', None, L)
u = m.check_for_updates()
print('instalada:', m.get_current_version(), '| achou:', u.TargetFullRelease.Version if u else None)
m.download_updates(u)
print('baixou:', u.TargetFullRelease.FileName)
'@
& "D:\programas\EditorImpressao\.venv\Scripts\python.exe" -I -c $baixar
Get-ChildItem "C:\Program Files\EditorImpressaoPrograma\packages" -Force | Select Name,Length,LastWriteTime
Get-Item "C:\Program Files\EditorImpressaoPrograma\Update.exe" | Select LastWriteTime
```
O que deve aparecer: "instalada: 1.1.0 | achou: 1.1.2", depois "baixou: EditorImpressaoPrograma-1.1.2-full.nupkg". Em
`packages\` fica o pacote da 1.1.2 (460.076.315 bytes) e some o da 1.1.1. O `Update.exe` tem a hora de agora.
**Anotar (a): o download gravou em `packages\`?** Se falhou, copiar a mensagem do Python inteira (ex.: "Acesso
negado", "os error 5").

**2b — trocar e reabrir (`apply_updates_and_restart`):**
```
$trocar = @'
import velopack as v
R = r'C:\Program Files\EditorImpressaoPrograma'
L = v.VelopackLocatorConfig(RootAppDir=R, UpdateExePath=R + r'\Update.exe', PackagesDir=R + r'\packages', ManifestPath=R + r'\current\sq.version', CurrentBinaryDir=R + r'\current', IsPortable=False)
m = v.UpdateManager(r'C:\EditorImpressaoProva\versoes 3\v1.1.2', None, L)
m.apply_updates_and_restart(m.check_for_updates())
'@
& "D:\programas\EditorImpressao\.venv\Scripts\python.exe" -I -c $trocar
```
O Python sai na hora. Na tela do Samuel deve aparecer a janelinha de progresso do Velopack e, depois, **o Editor de
Impressão abrindo sozinho**. **Nenhuma pergunta do Windows.**

### Passo 3 — Registrar
```
Get-Content "C:\Program Files\EditorImpressaoPrograma\current\sq.version" | Select-String "<version>"
Get-Content "$env:LOCALAPPDATA\velopack\velopack_EditorImpressaoPrograma.log" -Tail 60
tasklist /V /FI "IMAGENAME eq EditorImpressao.exe"
```
**Anotar:**
- **(b) `current` foi trocado sem UAC?** O `sq.version` diz `1.1.2`, e o registro tem `Root directory '...' writable:
  true`, `Applying package 1.1.2 to current: 1.1.0`, `Backing up current dir`, `Replacing current dir` e `Package
  version 1.1.2 applied successfully.`. A linha `Failed to update uninstall entry` é **esperada** ("Programas e
  Recursos").
- **(c) O programa reabriu na conta dele?** O `tasklist /V` mostra `EditorImpressao.exe` com "Nome de usuário"
  `SAMUEL-PC\fotog`, e o Samuel vê a janela. Também é esperado que o programa anote que não conseguiu chamar o
  ajudante (está desligado), sem pergunta nenhuma.
- **Os sinais de falha e o que querem dizer:**
  - `Re-launching as administrator` (com UAC): a pasta não ficou gravável;
  - `Unable to start the update, because one or more running processes prevented it`: algo segura o `current`
    (Explorador, antivírus, programa aberto);
  - `Acesso negado (os error 5)`: falta licença num arquivo;
  - `Unable to complete the update, and the app was left in a broken state`: a segunda troca de nome falhou; parar
    e chamar a gerente.

  Copiar a linha inteira.

### Passo 4 — De novo, com o programa fechado (`wait_exit_then_apply_updates`)
O Samuel **fecha o Editor de Impressão** (Arquivo > Sair). A gerente confere que nada roda
(`tasklist /FI "IMAGENAME eq EditorImpressao.exe"`) e, na mesma janela comum:
```
$fechado = @'
import velopack as v
R = r'C:\Program Files\EditorImpressaoPrograma'
L = v.VelopackLocatorConfig(RootAppDir=R, UpdateExePath=R + r'\Update.exe', PackagesDir=R + r'\packages', ManifestPath=R + r'\current\sq.version', CurrentBinaryDir=R + r'\current', IsPortable=False)
m = v.UpdateManager(r'C:\EditorImpressaoProva\versoes 3\v1.1.1', v.UpdateOptions(AllowVersionDowngrade=True, MaximumDeltasBeforeFallback=10), L)
u = m.check_for_updates()
print('instalada:', m.get_current_version(), '| achou:', u.TargetFullRelease.Version if u else None)
m.download_updates(u)
m.wait_exit_then_apply_updates(u, True, False)
print('Update.exe chamado: troca quando este Python sair, sem janela e sem reabrir')
'@
& "D:\programas\EditorImpressao\.venv\Scripts\python.exe" -I -c $fechado
```
- **4a.** Deve aparecer "instalada: 1.1.2 | achou: 1.1.1".
- **4b.** Esperar 1 minuto e repetir os comandos do passo 3. O certo: `1.1.1`, o registro com `Package version 1.1.1
  applied successfully.`, e **nada aberto** (pediu-se sem reabrir, como ao fechar o programa).
- **4c.** O Samuel abre pelo atalho da Área de Trabalho. A janela abre na 1.1.1, sem pergunta do Windows.
- **Anotar:** as mesmas três coisas, e a mensagem exata se falhar.

### Passo 5 (opcional) — Voltar à 1.1.0
O Samuel fecha o programa. A gerente repete o passo 4 trocando `v1.1.1` por `v1.1.0` no comando. É mais uma prova do
mesmo caminho, e o programa termina na versão em que começou.

### Passo 6 — Desfazer (UAC nº 2)
PowerShell **como administrador**; **o Samuel clica "Sim"**. Os comandos da seção 4: `/setowner`, `/reset`, renomear
o `estado.json` de volta e, se decidirem, `/ENABLE` da tarefa, **por último**. Depois, numa janela comum, a varredura
de conferência (o certo: 0, 0, todos SISTEMA) e `icacls` da raiz igual à do passo 0.

**Resultado para levar ao Fable:** "funcionou" ou "não funcionou no passo X", com as linhas do registro do Velopack e
a mensagem exata do Windows.

---

## 7. O que ficou em aberto ou não conferi

- **Não rodei nada na instalação:** nem a licença, nem o download, nem a troca. A resposta de verdade é o experimento.
- **Não conferi** como o `icacls /grant ... /T` grava em cada arquivo (licença própria ou herdada), nem o `/setowner`
  para SISTEMA. O `/reset /T` cobre os dois jeitos.
- **Não conferi** o texto que o `schtasks /Run` mostra para a tarefa desligada. O código vem do protocolo da Microsoft.
- **Conta:** o teste roda na conta `fotog` sem elevação, que para os arquivos se comporta como conta comum. Uma conta
  **padrão** de verdade (o Kaique, se a dele for padrão; **não conferi** o tipo da conta dele) só diferiria se algo
  pedisse licença: ela veria a pergunta da senha de administrador em vez de "Sim/Não". A causa de pedir seria a mesma.
- **Antivírus:** palpite. O Defender pode segurar um arquivo novo por alguns segundos; o Velopack tenta de novo 10
  vezes, uma por segundo, antes de desistir da primeira troca de nome.
- **"Programas e Recursos"** fica sempre na versão do `.msi` com a conta comum. Se isso importa ao Samuel, é decisão
  dele (não é parte do experimento).
- **Não li** o `empacotar.py` nem o `publicar_versao_kaique.py` por inteiro: só o cabeçalho e os registros da
  montagem de 22/11, que bastaram para saber quais versões estão prontas.
- **Sem ONDE-PAREI:** o pedido mandou gravar só este arquivo, então esta tarefa não tem ONDE-PAREI nem a seção de
  decisões dele. As decisões tocadas, citadas pelo pedido e pela resposta do Fable, são D-733, D-715/D-720/D-734,
  D-767 e D-830. O experimento não muda nenhuma: não mexe no programa.

## Fontes consultadas (23/11/2026)

- Velopack 1.2.161 (MIT), clonado da etiqueta `1.2.161` (commit `92d6a1c9`):
  [`src/bins/app.manifest`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/app.manifest),
  [`src/bins/build.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/build.rs),
  [`src/bins/src/update.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/update.rs),
  [`src/bins/src/commands/apply.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/commands/apply.rs),
  [`src/bins/src/commands/apply_windows_impl.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/commands/apply_windows_impl.rs),
  [`src/bins/src/windows/registry.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/windows/registry.rs),
  [`src/bins/src/windows/shortcuts.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/windows/shortcuts.rs),
  [`src/bins/src/windows/util.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/windows/util.rs),
  [`src/bins/src/shared/util_common.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/bins/src/shared/util_common.rs),
  [`src/lib-rust/src/locator.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/lib-rust/src/locator.rs),
  [`src/lib-rust/src/lockfile.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/lib-rust/src/lockfile.rs),
  [`src/lib-rust/src/manager.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/lib-rust/src/manager.rs),
  [`src/lib-rust/src/logging.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/lib-rust/src/logging.rs),
  [`src/lib-python/`](https://github.com/velopack/velopack/tree/1.2.161/src/lib-python),
  [`src/vpk/Velopack.Packaging.Windows/Msi/Templates/MsiTemplate.hbs`](https://github.com/velopack/velopack/blob/1.2.161/src/vpk/Velopack.Packaging.Windows/Msi/Templates/MsiTemplate.hbs),
  [`src/wix-dll/src/lib.rs`](https://github.com/velopack/velopack/blob/1.2.161/src/wix-dll/src/lib.rs).
- Microsoft: [icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls);
  [MS-TSCH SchRpcRun](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-tsch/77f2250d-500a-40ee-be18-c82f7079c4f0);
  [Task Scheduler error constants](https://learn.microsoft.com/en-us/Windows/win32/taskschd/task-scheduler-error-and-success-constants).
- Nosso código, só lido: `atualizacao.py` e `core/windows.py` no commit `93d9e3b8` (o da 1.1.0 instalada);
  `servidor_das_versoes.py` e `publicar_versao_kaique.py` (cabeçalhos) no ramo `atualizador-4-consertos-2026-11-21`.
- No PC, só leitura: os bytes do `Update.exe`, do atalho e do `EditorImpressao.exe`; `sq.version`,
  `versao-do-pacote.json`, `estado.json`, `atualizacao.log`, `desfazer.ps1`, `fonte-de-teste.txt`; os registros do
  Velopack em `C:\EditorImpressaoProva\registro-sistema\` (SYSTEM, 22/11 14:34) e em
  `%LOCALAPPDATA%\velopack\` (conta do Samuel); `icacls` da pasta e de `ProgramData`; a varredura `Get-Acl` dos
  38.547 itens; `schtasks /Query`; as chaves de desinstalar em `HKLM`/`HKCU`; os atalhos; `whoami /groups`;
  `Get-LocalUser`; `gh release list`; o conteúdo dos pacotes 1.1.1 e 1.1.2 (`.nuspec`, `versao-do-pacote.json`).
