"""Prova EXECUTADA (volta 3, segunda parte, 24/11/2026; D-851): onde o Velopack deixa o pacote da versão que roda.

Pergunta (Samuel): "a última versão boa deve ser guardada copiando o pacote que já está na pasta packages\\ do
programa (o instalador e cada troca deixam ele lá) [...] O agente confere isso, não supõe."

Tudo numa pasta minha (`saida_teste\\prova-packages`), com um programa de prova de outro nome (`ProvaPacotesEditor`,
nunca o nosso: nada encosta na instalação do Samuel), montado pelo `vpk` 1.2.161 DE VERDADE com as mesmas opções do
nosso publicar (`--delta None`, `--msi --instLocation PerMachine`). NADA é instalado: o .msi só é LIDO (as tabelas,
pela biblioteca do Windows Installer, em modo de leitura); nenhuma janela aparece (a troca roda com `--silent`), nada
vai para o registro do Windows (a instalação de prova é "portátil": o Velopack pula o registro e os atalhos,
`apply_windows_impl.rs`, "Skipping uninstall entry for portable app").

  1. o .msi põe algum arquivo em `packages\\`? (as tabelas File/Component/Directory dele);
  2. o pacote portátil (a mesma pasta que o .msi instala, `WindowsPackCommandRunner.cs` 230-243) traz `packages\\`?;
  3. a biblioteca do Velopack de verdade baixa a versão nova para `packages\\` (com que nome) e apaga a velha;
  4. o atualizador do Velopack de verdade (`Update.exe apply`) troca e deixa o pacote novo em `packages\\`.
Uso: python prova_packages.py   (a saída vai para prova_packages-resultado.txt)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RAMO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAMO))
R = Path(r"D:\programas\EditorImpressao\saida_teste\prova-packages")
ID = "ProvaPacotesEditor"
VPK = Path(os.environ["USERPROFILE"]) / ".dotnet" / "tools" / "vpk.exe"


def rodar(comando: list, **kw) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in comando], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", **kw)


def montar(v: str) -> dict:
    """O `vpk pack` de verdade de uma versão do programa de prova."""
    pasta = R / f"programa-{v}"
    pasta.mkdir(parents=True)
    shutil.copy(Path(os.environ["SystemRoot"]) / "System32" / "whoami.exe", pasta / f"{ID}.exe")
    (pasta / "versao.txt").write_text(v, encoding="utf-8")
    feito = rodar([VPK, "pack", "--packId", ID, "--packVersion", v, "--packDir", pasta, "--mainExe", f"{ID}.exe",
                   "--packTitle", "Prova", "--outputDir", R / "saida", "--runtime", "win-x64", "--delta", "None",
                   "--msi", "--instLocation", "PerMachine", "--skip-updates"])
    return {"codigo": feito.returncode, "fim": (feito.stdout + feito.stderr)[-600:]}


def tabelas_do_msi(msi: Path) -> dict:
    """As tabelas do .msi, só lidas (modo 0 = só leitura), pela biblioteca do Windows Installer."""
    script = (
        "$i = New-Object -ComObject WindowsInstaller.Installer;"
        f"$d = $i.GetType().InvokeMember('OpenDatabase','InvokeMethod',$null,$i,@('{msi}',0));"
        "function Q($s){$v=$d.GetType().InvokeMember('OpenView','InvokeMethod',$null,$d,@($s));"
        "$v.GetType().InvokeMember('Execute','InvokeMethod',$null,$v,$null);$o=@();"
        "while($r=$v.GetType().InvokeMember('Fetch','InvokeMethod',$null,$v,$null)){"
        "$o+=($r.GetType().InvokeMember('StringData','GetProperty',$null,$r,1)+'|'+"
        "$r.GetType().InvokeMember('StringData','GetProperty',$null,$r,2)+'|'+"
        "$r.GetType().InvokeMember('StringData','GetProperty',$null,$r,3))};$o};"
        "'DIR'; Q 'SELECT Directory, Directory_Parent, DefaultDir FROM Directory';"
        "'FILE'; Q 'SELECT File, Component_, FileName FROM File';"
        "'COMP'; Q 'SELECT Component, Directory_, KeyPath FROM Component'")
    feito = rodar(["powershell", "-NoProfile", "-NonInteractive", "-Command", script])
    linhas = feito.stdout.splitlines()
    partes: dict[str, list[str]] = {"DIR": [], "FILE": [], "COMP": []}
    atual = None
    for linha in linhas:
        if linha in partes:
            atual = linha
        elif atual:
            partes[atual].append(linha)
    pacotes = [d.split("|")[0] for d in partes["DIR"] if d.split("|")[2].endswith("packages")]
    componentes_em_pacotes = {c.split("|")[0] for c in partes["COMP"] if c.split("|")[1] in pacotes}
    return {"diretorio packages no msi": pacotes,
            "arquivos do msi dentro de packages": [f for f in partes["FILE"] if f.split("|")[1] in componentes_em_pacotes],
            "algum .nupkg no msi": [f for f in partes["FILE"] if "nupkg" in f.lower()],
            "quantos arquivos o msi tem": len(partes["FILE"]), "erros": feito.stderr[-400:]}


def main() -> None:
    if R.exists():
        shutil.rmtree(R)
    R.mkdir(parents=True)
    resultado: dict = {"vpk 1.0.0": montar("1.0.0"), "vpk 1.0.1": montar("1.0.1")}
    saida = R / "saida"
    resultado["o que o vpk produziu"] = sorted(p.name for p in saida.iterdir())
    msi = next(saida.glob("*.msi"))
    resultado["1. o .msi"] = tabelas_do_msi(msi)
    # O NOSSO .msi de verdade (o da 1.1.0, guardado pelo Samuel numa prova antiga): só lido, em modo de leitura.
    nosso = Path(r"D:\programas\EditorImpressao-arquivos\prova-atualizador-4\estado-1.1.0\v1.1.0"
                 r"\EditorImpressaoPrograma-1.1.0-win.msi")
    if nosso.is_file():
        resultado["1b. o nosso .msi da 1.1.0 (só lido)"] = tabelas_do_msi(nosso)
    portatil = next(saida.glob("*1.0.0*Portable.zip"), None) or next(saida.glob("*Portable.zip"))
    with zipfile.ZipFile(portatil) as z:
        nomes = z.namelist()
    resultado["2. o portátil (a pasta que o .msi instala)"] = {
        "arquivo": portatil.name, "tem packages\\": [n for n in nomes if n.lower().startswith("packages")],
        "o que tem na raiz": sorted({n.split("/")[0] for n in nomes})}

    # 3 e 4: uma instalação de prova portátil da 1.0.0 (o vpk gera o portátil da última versão montada; a 1.0.0 vem
    # do pacote dela, aberto na pasta current\\, como o instalador faria).
    raiz = R / "instalado"
    with zipfile.ZipFile(portatil) as z:
        z.extractall(raiz)
    shutil.rmtree(raiz / "current")
    with zipfile.ZipFile(saida / f"{ID}-1.0.0-full.nupkg") as z:
        for n in z.namelist():
            if n.startswith("lib/app/"):
                destino = raiz / "current" / n[len("lib/app/"):]
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(z.read(n))
        nuspec = [n for n in z.namelist() if n.endswith(".nuspec")][0]
        (raiz / "current" / "sq.version").write_bytes(z.read(nuspec))
    (raiz / "packages").mkdir(exist_ok=True)
    import velopack

    from core import conversa_com_o_velopack as conversa

    localizador = velopack.VelopackLocatorConfig(raiz, raiz / "Update.exe", raiz / "packages",
                                                 raiz / "current" / "sq.version", raiz / "current", True)
    antes = sorted(p.name for p in (raiz / "packages").iterdir())
    # como o Setup.exe deixa (install.rs): o pacote da versão instalada em packages\\
    shutil.copy(saida / f"{ID}-1.0.0-full.nupkg", raiz / "packages" / f"{ID}-1.0.0-full.nupkg")
    achada = conversa.procurar(str(saida), localizador)
    conversa.baixar(str(saida), achada, localizador)
    depois_de_baixar = sorted(p.name for p in (raiz / "packages").iterdir())
    pendente = conversa.pendente(str(saida), localizador)
    resultado["3. baixar pela biblioteca"] = {
        "packages antes (portátil, como o .msi)": antes,
        "packages com o da 1.0.0 posto como o Setup.exe põe": f"{ID}-1.0.0-full.nupkg",
        "achada": [achada.versao, achada.arquivo], "packages depois de baixar": depois_de_baixar,
        "pendente pelo Velopack": pendente}
    troca = rodar([raiz / "Update.exe", "apply", "--silent", "--norestart", "--package",
                   raiz / "packages" / f"{ID}-1.0.1-full.nupkg", "--root", raiz])
    resultado["4. a troca pelo Update.exe de verdade (--silent, --norestart)"] = {
        "codigo": troca.returncode, "versao em current depois": (raiz / "current" / "versao.txt").read_text(
            encoding="utf-8") if (raiz / "current" / "versao.txt").exists() else "?",
        "packages depois da troca": sorted(p.name for p in (raiz / "packages").iterdir()),
        "pendente depois da troca": conversa.pendente(str(saida), localizador),
        "fim do registro do Update.exe": (troca.stdout + troca.stderr)[-1500:]}
    texto = json.dumps(resultado, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_packages-resultado.txt").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
