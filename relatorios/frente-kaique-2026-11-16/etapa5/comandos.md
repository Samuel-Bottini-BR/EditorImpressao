# Etapa 5: os comandos, fase por fase (escritos em 17/11/2026, NENHUM rodado)

Os números das fases são os da `lista.md` (parte B). Cada bloco tem uma marca:

- **[SÓ LÊ]**: pode rodar a qualquer hora; não muda nada.
- **[SÓ NO D:]**: cria ou apaga só dentro de `$TRAB` ou da cópia da etapa 5.
- **[MUDA O WINDOWS]**: só na etapa 5, com o Samuel avisado e presente. Quase todos fazem a pergunta do Windows.

O que está entre `< >` vem do ONDE-PAREI dos construtores (lista, A2) e tem de ser preenchido antes. Comando com
`< >` sem preencher **não roda**.

PowerShell (o do Windows, 5.1). Variáveis do começo de toda sessão:

```powershell
$PY   = "D:\programas\EditorImpressao\.venv\Scripts\python.exe"
$PY12 = "C:\Users\fotog\AppData\Local\Programs\Python\Python312\python.exe"   # tem o pywinauto
$COPIA = "D:\programas\EditorImpressao\.claude\worktrees\etapa5"             # cópia nova do ramo final (A1)
$E5   = "$COPIA\relatorios\frente-kaique-2026-11-16\etapa5"
$TRAB = "D:\programas\EditorImpressao\saida_teste\etapa5"
$SSH  = "C:\Windows\System32\OpenSSH\ssh.exe"                                 # o do Windows, não o do Git
$INSTALADO = "C:\Program Files\EditorImpressao"
```

---

## Fase 0. Antes de tudo

**0.1 [SÓ NO D:] Pastas do teste**
```powershell
New-Item -ItemType Directory -Force "$TRAB\fotos","$TRAB\dados","$TRAB\temp","$TRAB\servidor","$TRAB\segredo","$TRAB\livros","$TRAB\prints","$TRAB\registros","$TRAB\pilotos","$TRAB\escrita-da-conta-de-testes" | Out-Null
git -C $COPIA show kaique-etapa2-2026-11-16:relatorios/frente-kaique-2026-11-16/etapa2/scripts/lancar.py     | Set-Content -Encoding utf8 "$TRAB\pilotos\lancar.py"
git -C $COPIA show kaique-etapa2-2026-11-16:relatorios/frente-kaique-2026-11-16/etapa2/scripts/piloto_uia.py | Set-Content -Encoding utf8 "$TRAB\pilotos\piloto_uia.py"
```

**0.2 [SÓ LÊ] Foto sem administrador**
```powershell
& $PY -I "$E5\fotografo.py" "$TRAB\fotos\foto-0-antes.json"
# a foto de 17/11 fica fora do git (tem nomes de contas e a lista de programas do PC; o projeto é público)
& $PY -I "$E5\comparar.py" "$TRAB\fotos\foto-antes-preparo-17-11.json" "$TRAB\fotos\foto-0-antes.json"
```

**0.3 [SÓ LÊ, mas pede a pergunta do Windows] Foto com administrador**
```powershell
Start-Process powershell -Verb RunAs -Wait -ArgumentList "-NoProfile -Command & '$PY' -I '$E5\fotografo.py' '$TRAB\fotos\foto-0-antes-adm.json'"
```

**0.4 [SÓ NO D:] Cópia de reserva da pasta dos projetos (a origem não muda)**
```powershell
robocopy "$env:LOCALAPPDATA\EditorImpressao" "$TRAB\reserva-dados-do-samuel" /E /COPY:DAT /DCOPY:T /R:0 /W:0 /NP /LOG:"$TRAB\registros\reserva.log"
```

**0.5 [SÓ NO D:] Testes de máquina, um arquivo por vez, com a pasta temporária no D:**
```powershell
Set-Location $COPIA
foreach ($t in "test_decisoes_atualizacao.py","test_decisoes_testes_a_distancia.py","test_decisoes_desinstalar.py","test_empacotar.py","test_decisoes.py") {
  & $PY -m pytest "tests\$t" -q --basetemp "$TRAB\pytest\$($t -replace '\.py','')"
}
```
O conjunto inteiro: a rodada do GitHub do ramo final (lista, A1), não no PC.

---

## Fase 1. As versões de mentira (o agente sozinho)

**1.1 [SÓ NO D:] Empacotar a pasta do programa, com a pasta temporária no D:**
```powershell
$env:TEMP = "$TRAB\temp"; $env:TMP = "$TRAB\temp"; $env:DOTNET_ROOT = "C:\Program Files\dotnet"
Set-Location $COPIA
& $PY empacotar.py --modo pasta          # uns 11 minutos; dist\EditorImpressao
```

**1.2 [SÓ NO D:] Publicar cada versão no servidor de mentira** (mudar `VERSAO` no `versao.py` da cópia, sem commit,
antes de cada uma; ver lista C2)
```powershell
# 1.1.0 (dela sai o .msi), 1.1.1, 1.1.2, 1.1.5: boas
& $PY publicar_versao_kaique.py --pasta "$TRAB\servidor" --pasta-pronta "$COPIA\dist\EditorImpressao"
# 1.1.3: estragada (uma cópia da pasta sem o tesseract.exe)
robocopy "$COPIA\dist\EditorImpressao" "$TRAB\estragada" /E /NP /NFL /NDL
Remove-Item "$TRAB\estragada\tesseract\tesseract.exe"
& $PY publicar_versao_kaique.py --pasta "$TRAB\servidor" --pasta-pronta "$TRAB\estragada"
# 1.1.4: assinada com outra chave (a chave falsa nasce em $TRAB\segredo).
# NUNCA "publicar_versao_kaique.py --criar-chave" sem destino: esse é o lugar da chave do Samuel.
& $PY -c "import sys; sys.path.insert(0, r'$COPIA'); import publicar_versao_kaique as p; p.criar_chave(r'$TRAB\segredo\chave-falsa.txt')"
& $PY publicar_versao_kaique.py --pasta "$TRAB\servidor" --pasta-pronta "$COPIA\dist\EditorImpressao" --chave "$TRAB\segredo\chave-falsa.txt"
```
Atenção ao `--chave`: o publicar confere a chave contra a pública do programa e **recusa** a falsa. Se recusar,
assinar a 1.1.4 com a função `assinar_pacote` e a chave falsa, como fez o ensaio da etapa 3
(`relatorios/frente-kaique-2026-11-16/etapa3/ensaio_velopack.py`, passo C). Nunca mexer na chave do Samuel em
`C:\Users\fotog\AppData\Roaming\EditorImpressao-publicar\`.

**1.3 [SÓ LÊ] Conferir o servidor**
```powershell
Get-ChildItem "$TRAB\servidor" | Select-Object Name, Length
```

---

## Fase 2. Instalar (o Samuel por perto: 1 pergunta do Windows)

**2.1 [MUDA O WINDOWS] Instalar o .msi da 1.1.0 dentro da área escondida**
```powershell
$MSI = (Get-ChildItem "$TRAB\servidor","$COPIA\build\publicar" -Recurse -Filter *.msi | Select-Object -First 1).FullName
& $PY12 "$TRAB\pilotos\lancar.py" EditorTesteEtapa5 "$TRAB\registros\lancar-msi.log" msiexec /i "$MSI" /passive /l*v "$TRAB\registros\msi-instalar.log"
```

**2.2 [SÓ LÊ] Depois de instalar**
```powershell
& $PY -I "$E5\fotografo.py" "$TRAB\fotos\foto-2-instalado.json"
& $PY -I "$E5\comparar.py" "$TRAB\fotos\foto-0-antes.json" "$TRAB\fotos\foto-2-instalado.json"
Get-Content "$INSTALADO\current\sq.version" -ErrorAction SilentlyContinue
Get-Content "C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log" -Tail 30 -ErrorAction SilentlyContinue   # B1
Get-ChildItem "$env:LOCALAPPDATA\velopack" | Select-Object Name, Length, LastWriteTime
Select-String -Path "$INSTALADO\current\*.exe","$INSTALADO\current\_internal\*.pyc" -Pattern "ghp_","github_pat_" -List -ErrorAction SilentlyContinue   # D-713
```

**2.3 [SÓ NO D:] D-728: pelo código, nada aparece** (abre a janela na área escondida, com os dados trocados)
```powershell
# o piloto_uia.lancar_exe troca LOCALAPPDATA e TEMP; aqui o .exe é o pythonw do .venv com main.py
& $PY12 "$TRAB\pilotos\lancar.py" EditorTesteEtapa5 "$TRAB\registros\dev.log" `
  cmd /c "set LOCALAPPDATA=$TRAB\dados-dev&& set TEMP=$TRAB\temp&& D:\programas\EditorImpressao\.venv\Scripts\pythonw.exe D:\programas\EditorImpressao\main.py"
# esperar 60 s, print pelo piloto, fechar com WM_CLOSE
```

---

## Fase 3. Primeira abertura (1 pergunta do Windows)

**3.1 [MUDA O WINDOWS] Abrir o programa instalado na área escondida, com os dados trocados**
Um script `$TRAB\pilotos\fase3.py` (rodar com `$PY12`, dentro da área escondida pelo `lancar.py`), que usa o
`piloto_uia.py`: `lancar_exe("$INSTALADO\current\EditorImpressao.exe", dados="$TRAB\dados", temp="$TRAB\temp")`;
espera a janela "Testes à distância"; print; clica "Agora não"; **o Samuel clica "Sim" na pergunta do Windows**;
abre as Configurações; print; fecha com `WM_CLOSE`.

**3.2 [SÓ LÊ]**
```powershell
& $PY -I "$E5\fotografo.py" "$TRAB\fotos\foto-3-primeira-abertura.json"
& $PY -I "$E5\comparar.py" "$TRAB\fotos\foto-2-instalado.json" "$TRAB\fotos\foto-3-primeira-abertura.json"
Get-Content "C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log" -Tail 30
schtasks /Query /TN "<NOME_DO_AJUDANTE>" /V /FO LIST     # pode precisar de administrador: ver 7.3
```

---

## Fases 4 a 6. As atualizações de mentira (nenhuma pergunta do Windows esperada)

Antes de cada uma, deixar no servidor só as versões até a da fase (mover as outras para `$TRAB\servidor-espera`).
O programa tem de procurar no servidor de mentira: **`<COMO_APONTAR_PARA_A_PASTA_DE_TESTE>`** (lista, A2).

**4.1 [SÓ NO D:, troca a versão instalada] "Reiniciar agora" (1.1.1)** — piloto: abrir com o projeto de teste
(cópia de um livro do acervo em `$TRAB\livros`), esperar o aviso, print, "Reiniciar agora", esperar reabrir, print,
fechar. Anotar com o Samuel se apareceu alguma pergunta do Windows.

**5.1 "Depois" (1.1.2)** — piloto: abrir, aviso, print, "Depois", mexer no projeto, fechar; ler `sq.version`; abrir de
novo; print da espera e do programa; ler `sq.version`.

**6.1 Estragada (1.1.3)** e **6.2 Assinatura errada (1.1.4)** — piloto: abrir, esperar, fechar, abrir de novo, print do
aviso da falha; abrir uma terceira vez (o aviso não volta).

**4-6 [SÓ LÊ] Depois de cada uma**
```powershell
Get-Content "$INSTALADO\current\sq.version"
Get-Content "C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log" -Tail 40
Get-Content "C:\ProgramData\EditorImpressao\atualizacao\estado.json"
Get-Content "$env:LOCALAPPDATA\velopack\velopack_EditorImpressao.log" -Tail 60 -ErrorAction SilentlyContinue
& $PY -I "$E5\fotografo.py" "$TRAB\fotos\foto-6-atualizacoes.json"
```

---

## Fase 7. Ligar os testes à distância e entrar por SSH (1 + 1 perguntas do Windows)

**7.1 [SÓ NO D:] A senha de teste (aleatória, só letras e números) e o ajudante da SSH**
```powershell
$senha = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
Set-Content -Encoding ascii "$TRAB\segredo\senha.txt" $senha
Set-Content -Encoding ascii "$TRAB\segredo\askpass.cmd" "@type `"$TRAB\segredo\senha.txt`""
Remove-Variable senha
```

**7.2 [MUDA O WINDOWS] Pôr a senha pelas Configurações** — piloto: abrir o programa, Configurações > Testes à
distância > "Pôr a senha dos testes", digitar a senha lida de `senha.txt` (pelo leitor de tela, `set_edit_text`),
"OK"; **o Samuel clica "Sim"**; esperar a frase "Ligado"; print. Instalar o OpenSSH pode levar até 15 minutos.

**7.3 [SÓ LÊ, com administrador: 1 pergunta do Windows] A conferência com administrador** (um script só, para uma
pergunta só): `$TRAB\pilotos\conferencia-adm.ps1` com:
```powershell
& $PY -I "$E5\fotografo.py" "$TRAB\fotos\foto-7-ligado-adm.json"
Get-Content C:\ProgramData\ssh\sshd_config | Set-Content "$TRAB\registros\sshd_config-fase7.txt"
foreach ($u in "EditorTestes","fotog","WsiAccount") {
  & C:\Windows\System32\OpenSSH\sshd.exe -T -C "user=$u,host=localhost,addr=127.0.0.1" | Select-String "allowusers|passwordauthentication|maxauthtries" | Out-File -Append "$TRAB\registros\sshd-T-fase7.txt"
}
Get-WinEvent -LogName "OpenSSH/Operational" -MaxEvents 50 | Format-List TimeCreated, Message | Out-File "$TRAB\registros\openssh-eventos-fase7.txt"
Get-ScheduledTask -TaskPath "\EditorImpressao\*" | ForEach-Object { Export-ScheduledTask -TaskName $_.TaskName -TaskPath $_.TaskPath } | Out-File "$TRAB\registros\tarefas-fase7.xml"
Get-Content "C:\ProgramData\EditorImpressao\testes-a-distancia\antes.json" | Out-File "$TRAB\registros\antes-fase7.json"
Get-MpThreatDetection | Out-File "$TRAB\registros\antivirus-fase7.txt"     # D-725
```
Rodar com: `Start-Process powershell -Verb RunAs -Wait -ArgumentList "-NoProfile -File $TRAB\pilotos\conferencia-adm.ps1"`
(o script define `$PY`, `$E5` e `$TRAB` no começo).

**7.4 [SÓ LÊ] Entrar por SSH pelo próprio PC (127.0.0.1), com a senha pelo ajudante, sem mexer no known_hosts do Samuel**
```powershell
$env:SSH_ASKPASS = "$TRAB\segredo\askpass.cmd"; $env:SSH_ASKPASS_REQUIRE = "force"
$op = @("-o","UserKnownHostsFile=$TRAB\segredo\known_hosts","-o","StrictHostKeyChecking=accept-new",
        "-o","PubkeyAuthentication=no","-o","PreferredAuthentications=password","-o","NumberOfPasswordPrompts=1")
& $SSH @op EditorTestes@127.0.0.1 "whoami"
# D-716: prioridade baixa e normal
& $SSH @op EditorTestes@127.0.0.1 "start `"`" /belownormal /wait powershell -NoProfile -Command `"(Get-Process -Id `$PID).PriorityClass`""
& $SSH @op EditorTestes@127.0.0.1 "powershell -NoProfile -Command `"(Get-Process -Id `$PID).PriorityClass`""
# B2: tentativa como fotog SEM senha (BatchMode não pede senha; só gera a linha no registro do OpenSSH)
& $SSH -o BatchMode=yes -o "UserKnownHostsFile=$TRAB\segredo\known_hosts" fotog@127.0.0.1 "whoami"
```

---

## Fase 8. A conta de testes não enxerga a pasta do Samuel (pela SSH)

**8.1 [SÓ LÊ, fora uma escrita em $TRAB]**
```powershell
$cmd = 'powershell -NoProfile -Command "' +
  'try { Get-ChildItem C:\Users\fotog -ErrorAction Stop | Out-Null; ''VE C:\Users\fotog'' } catch { ''NAO VE C:\Users\fotog: '' + $_.Exception.GetType().Name };' +
  'try { Get-ChildItem C:\Users\fotog\AppData\Local\EditorImpressao -ErrorAction Stop | Out-Null; ''VE os projetos'' } catch { ''NAO VE os projetos: '' + $_.Exception.GetType().Name };' +
  '''administrador: '' + ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator);' +
  '''D:\programas visivel: '' + (Test-Path D:\programas);' +
  'Set-Content ''D:\programas\EditorImpressao\saida_teste\etapa5\escrita-da-conta-de-testes\prova.txt'' ''escrito pela conta de testes'';' +
  '''escreveu no D: '' + (Test-Path ''D:\programas\EditorImpressao\saida_teste\etapa5\escrita-da-conta-de-testes\prova.txt'');' +
  '''log da atualizacao legivel: '' + (Test-Path C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log)"'
& $SSH @op EditorTestes@127.0.0.1 $cmd
& $SSH @op EditorTestes@127.0.0.1 "net session"        # tem de dar erro 5 (Acesso negado)
```

---

## Fase 9. O "atualizar" de longe (D-736)

**9.1 [SÓ LÊ] Teste leve de longe, que não procura versão**
```powershell
$antes = (Get-Content "C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log").Count
& $SSH @op EditorTestes@127.0.0.1 "`"$INSTALADO\current\EditorImpressao.exe`" --teste-rapido & echo codigo %ERRORLEVEL%"
(Get-Content "C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log").Count - $antes   # tem de ser 0 linhas de procura
```

**9.2 [MUDA a versão instalada] O comando "atualizar" de longe, com a 1.1.5 no servidor**
```powershell
& $SSH @op EditorTestes@127.0.0.1 "<COMANDO_ATUALIZAR_DE_LONGE>"
Get-Content "$INSTALADO\current\sq.version"
Get-Content "C:\ProgramData\EditorImpressao\atualizacao\atualizacao.log" -Tail 20
```

---

## Fase 10. Desligar e ligar de novo (2 perguntas do Windows)

**10.1 [MUDA O WINDOWS]** — piloto: Configurações > desmarcar a caixinha; **"Sim"**; print; foto
`foto-10-desligado.json`. Depois marcar de novo e pôr a senha; **"Sim"**; print; foto `foto-10-religado.json`;
`& $SSH @op EditorTestes@127.0.0.1 "whoami"`; contar as linhas-marca do `sshd_config` (na conferência com
administrador da fase 12, ou repetindo a 7.3).

---

## Fase 11. Desinstalar (1 pergunta do Windows, talvez 2)

**11.1 [MUDA O WINDOWS]**
```powershell
$prod = (Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\* | Where-Object { $_.DisplayName -like "Editor de Impress*" -and $_.UninstallString -like "MsiExec*" }).PSChildName
& $PY12 "$TRAB\pilotos\lancar.py" EditorTesteEtapa5 "$TRAB\registros\lancar-msi-x.log" msiexec /x $prod /passive /l*v "$TRAB\registros\msi-desinstalar.log"
# esperar o que o código final disser (tarefa "desfazer" ou segunda pergunta); depois:
& $PY -I "$E5\fotografo.py" "$TRAB\fotos\foto-11-desinstalado.json"
& $PY -I "$E5\comparar.py" "$TRAB\fotos\foto-0-antes.json" "$TRAB\fotos\foto-11-desinstalado.json"
Get-Content "C:\ProgramData\EditorImpressao\testes-a-distancia\o-que-foi-desfeito.txt" -ErrorAction SilentlyContinue
```

---

## Fase 12. Fotografar de novo, comparar e desfazer o que sobrou

**12.1 [SÓ LÊ, com administrador]**
```powershell
Start-Process powershell -Verb RunAs -Wait -ArgumentList "-NoProfile -Command & '$PY' -I '$E5\fotografo.py' '$TRAB\fotos\foto-12-depois-adm.json'"
& $PY -I "$E5\fotografo.py" "$TRAB\fotos\foto-12-depois.json"
& $PY -I "$E5\comparar.py" "$TRAB\fotos\foto-0-antes-adm.json" "$TRAB\fotos\foto-12-depois-adm.json" | Tee-Object "$TRAB\registros\comparacao-final.txt"
```

**12.2 [MUDA O WINDOWS] Desfazer à mão SÓ o que o comparador disser que sobrou** (um script só, num PowerShell de
administrador; uma linha por "SOBROU"; cada linha só roda se a coisa existe e é do teste):
```powershell
# conta de testes (só se a descrição é a nossa)
$c = Get-LocalUser -Name EditorTestes -ErrorAction SilentlyContinue
if ($c -and $c.Description -eq "Conta so para os testes a distancia") {
  Get-CimInstance Win32_UserProfile | Where-Object { $_.SID -eq $c.SID.Value } | Remove-CimInstance
  Remove-LocalUser -Name EditorTestes }
# o valor UserList; a chave só se ficou vazia (ela não existia em 17/11)
$ul = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList"
Remove-ItemProperty -Path $ul -Name EditorTestes -ErrorAction SilentlyContinue
if ((Test-Path $ul) -and -not (Get-Item $ul).Property) { Remove-Item $ul; if (-not (Get-Item (Split-Path $ul)).GetSubKeyNames()) { Remove-Item (Split-Path $ul) } }
# regras do firewall
Remove-NetFirewallRule -Name EditorImpressao-Testes -ErrorAction SilentlyContinue
Remove-NetFirewallRule -Name OpenSSH-Server-In-TCP -ErrorAction SilentlyContinue      # não existia em 17/11
# tarefas do programa
Get-ScheduledTask -TaskPath "\EditorImpressao\*" -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false
# o OpenSSH servidor (não existia em 17/11): parar e tirar
Stop-Service sshd -ErrorAction SilentlyContinue
Remove-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
# C:\ProgramData\ssh EXISTIA (vazia): NUNCA apagar a pasta; só os arquivos que nasceram nela, conferidos um por um
Get-ChildItem C:\ProgramData\ssh -Force -Recurse | Select-Object FullName   # olhar e decidir arquivo por arquivo
```
Depois, foto e comparação de novo (12.1) até "o Windows ficou como antes".

**12.3 [SÓ NO D:] Limpeza do que o teste criou** (no fim, depois de guardar fotos, registros e prints no relatório,
e só com o "ok" da gerente)
```powershell
Remove-Item "$TRAB\segredo" -Recurse -Force          # a senha e a chave falsa
# $TRAB inteiro e a cópia da etapa 5: só com a gerente (CLAUDE.md, regra de apagar)
```
