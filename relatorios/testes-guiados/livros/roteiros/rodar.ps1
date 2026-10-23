# Roda o percurso de um livro (verificador, 23/10/2026) e guarda o PID do processo que ESTE
# script abriu (só esse pode ser fechado; nunca python.exe em geral).
# Uso: powershell -File rodar.ps1 <curto>
param([string]$curto)
$wt = "D:\programas\EditorImpressao\.claude\worktrees\livros"
$rot = "$wt\relatorios\testes-guiados\livros\roteiros"
$r = "D:\programas\EditorImpressao-arquivos\testes-livros-saida\$curto"
New-Item -ItemType Directory -Force $r | Out-Null
$p = Start-Process -FilePath "D:\programas\EditorImpressao\.venv\Scripts\python.exe" `
  -ArgumentList "-X utf8 `"$rot\percurso.py`" `"$wt`" `"$rot\configs\$curto.json`"" `
  -RedirectStandardOutput "$r\saida.txt" -RedirectStandardError "$r\erros.txt" -WindowStyle Hidden -PassThru
"$($p.Id)" | Out-File "$r\pid.txt"
"PID $($p.Id)"
$p.WaitForExit()
"saiu com $($p.ExitCode)"
