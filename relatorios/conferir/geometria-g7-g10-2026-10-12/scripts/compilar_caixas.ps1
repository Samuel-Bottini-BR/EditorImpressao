# Compila scripts\caixas.cpp (teste do pesquisador, 12/10/2026). NAO faz parte do programa.
# Liga na biblioteca do ScanTailor que o teste de 01/10 ja compilou (st_tudo.lib): so compila
# um arquivo pequeno. O rascunho fica em saida_teste\geometria-perguntas\build-caixas (fora do git).
# Uso (da raiz da worktree):  powershell -File relatorios\conferir\geometria-g7-g10-2026-10-12\scripts\compilar_caixas.ps1
$ErrorActionPreference = 'Stop'
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$raiz = (Resolve-Path "$aqui\..\..\..\..").Path
$rascunho = "$raiz\saida_teste\geometria-perguntas\build-caixas"
$tmp = "$raiz\saida_teste\geometria-perguntas\tmp"
New-Item -ItemType Directory -Force -Path $rascunho, $tmp | Out-Null
$env:TEMP = $tmp; $env:TMP = $tmp
$cmake = 'C:\Program Files\CMake\bin\cmake.exe'
$qt = 'D:/programas/EditorImpressao-arquivos/ferramentas/qt/6.11.1/msvc2022_64'
& $cmake -S $aqui -B $rascunho -G 'Visual Studio 17 2022' -A x64 "-DCMAKE_PREFIX_PATH=$qt"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $cmake --build $rascunho --config Release
exit $LASTEXITCODE
