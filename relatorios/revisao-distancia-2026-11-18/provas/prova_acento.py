# Prova (so leitura, nada do programa): o mesmo jeito de mandar texto ao PowerShell
# que _senha_cifrada_pelo_windows usa (stdin, text=True, sem encoding), com um texto
# de exemplo que NAO e senha. O PowerShell devolve os codigos das letras que recebeu.
import subprocess, sys, locale
texto = "maçã-Ação"
script = "$s = [Console]::In.ReadLine(); [Console]::Out.Write((($s.ToCharArray() | ForEach-Object { [int]$_ }) -join ','))"
saida = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                       input=texto, capture_output=True, text=True, check=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
recebido = "".join(chr(int(c)) for c in saida.stdout.strip().split(","))
print("python", sys.version.split()[0], "| codificacao do Python:", locale.getpreferredencoding(False))
print("mandado :", texto, [ord(c) for c in texto])
print("recebido:", recebido, [ord(c) for c in recebido])
print("IGUAL" if recebido == texto else "DIFERENTE")
