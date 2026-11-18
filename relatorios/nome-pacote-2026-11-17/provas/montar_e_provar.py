r"""Repete a prova de 17/11 (pasta de reserva do Velopack e desinstalar) com o nome NOVO do pacote (D-763).

Uso (cada etapa separada, na ordem; tudo sem administrador, sem janela):
    python -I montar_e_provar.py nomes      os nomes da prova, tirados da regra do programa
    python -I montar_e_provar.py montar     ProvaNome.exe (PyInstaller) + pacotes 1.0.0 e 1.0.1 (vpk 1.2.161)
    python -I montar_e_provar.py caso-a     pasta da instalacao TRANCADA (como Arquivos de Programas para o Kaique)
                                            + desinstalar (C1)
    python -I montar_e_provar.py caso-b     pasta da instalacao ABERTA + desinstalar (C2)
    python -I montar_e_provar.py limpar     apaga o que a prova criou fora de D:\agente_temp_testes\nome-pacote

OS NOMES SAEM DA MESMA REGRA DO PROGRAMA (nunca escritos a mao):
- pacote de mentira = versao.ID_DO_PACOTE + "Prova"          (o programa: versao.ID_DO_PACOTE)
- pasta dos dados de mentira = historico.pasta_de_dados().name + "Prova"   (o programa: historico.pasta_de_dados)
e a prova confere, antes de tudo, a mesma regra de tests/test_nome_do_pacote.py: os dois nunca sao iguais.
Assim a prova mostra o que acontece com a relacao de verdade ("pacote" ao lado de "pasta dos dados") sem nunca
usar o nome da pasta de verdade dos projetos.

O pacote e montado por empacotar.comando_do_vpk (o MESMO comando do programa), com tres trocas so da prova:
o nome do pacote (acima), o .exe (ProvaNome.exe) e "--instLocation Either" no lugar de "PerMachine" (o .msi
"para todo o computador" pede administrador; o "Either" instala so para a conta, sem pergunta do Windows, como em
17/11). Sem atalhos (--shortcuts ""), titulo "Prova do nome do pacote".

A PASTA DE VERDADE DOS PROJETOS (%LOCALAPPDATA%\EditorImpressao) so e OLHADA: os nomes do primeiro nivel, antes e
depois. Nada e gravado, mudado ou apagado nela. LocalAppData aqui e o do Windows (SHGetKnownFolderPath), o mesmo que
o Velopack usa.
"""
from __future__ import annotations

import ctypes
import json
import os
import shutil
import subprocess
import sys
from ctypes import wintypes
from pathlib import Path

WT = Path(r"D:\programas\EditorImpressao\.claude\worktrees\nome-pacote")
BASE = Path(r"D:\agente_temp_testes\nome-pacote\prova")
PY = Path(r"D:\programas\EditorImpressao\.venv\Scripts\python.exe")
CHAVE = Path(r"D:\agente_temp_testes\velopack-pasta\chave-de-mentira")
VERSOES = BASE / "versoes"
FOTOS = BASE / "fotos"
TRANCADA = BASE / "instalado-trancado"
ABERTA = BASE / "instalado-aberta"
SEM_JANELA = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def local_app_data_do_windows() -> Path:
    """O mesmo que o Velopack usa: SHGetKnownFolderPath(FOLDERID_LocalAppData)."""
    class GUID(ctypes.Structure):
        _fields_ = [("a", wintypes.DWORD), ("b", wintypes.WORD), ("c", wintypes.WORD), ("d", ctypes.c_ubyte * 8)]
    g = GUID(0xF1B32785, 0x6FBA, 0x4FCF, (ctypes.c_ubyte * 8)(0x9D, 0x55, 0x7B, 0x8E, 0x7F, 0x15, 0x70, 0x91))
    p = ctypes.c_wchar_p()
    ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(g), 0, None, ctypes.byref(p))
    v = p.value
    ctypes.windll.ole32.CoTaskMemFree(p)
    return Path(v)


def nomes() -> dict:
    # historico.pasta_de_dados() cria a pasta: so na pasta de mentira (nunca toca a de verdade);
    # depois a variavel volta, para os comandos (msiexec, vpk) rodarem como sempre.
    verdadeira = os.environ.get("LOCALAPPDATA")
    os.environ["LOCALAPPDATA"] = str(BASE / "localappdata-do-montador")
    sys.path.insert(0, str(WT))
    import historico
    import versao

    dados, pacote = historico.pasta_de_dados().name, versao.ID_DO_PACOTE
    if verdadeira is not None:
        os.environ["LOCALAPPDATA"] = verdadeira
    assert pacote.casefold() != dados.casefold(), "a regra do programa falhou"
    n = {"pacote_de_verdade": pacote, "dados_de_verdade": dados,
         "pacote_de_mentira": pacote + "Prova", "dados_de_mentira": dados + "Prova"}
    assert n["pacote_de_mentira"].casefold() != n["dados_de_mentira"].casefold()
    assert "editorimpressao" not in (n["pacote_de_mentira"].casefold(), n["dados_de_mentira"].casefold())
    return n


N = nomes()
LAD = local_app_data_do_windows()
RESERVA = LAD / N["pacote_de_mentira"]
DADOS_DE_MENTIRA = LAD / N["dados_de_mentira"]
DADOS_DE_VERDADE = LAD / N["dados_de_verdade"]
TITULO_DA_PROVA = "Prova do nome do pacote"
PASTA_DO_TITULO = LAD / TITULO_DA_PROVA
TEMP_DO_TITULO = Path(os.environ["TEMP"]) / f"velopack_{TITULO_DA_PROVA}"


def arvore(raiz: Path, linhas: list, limite=60) -> None:
    if not raiz.exists():
        linhas.append(f"  (nao existe) {raiz}")
        return
    n = 0
    for dirpath, dirs, files in os.walk(raiz):
        rel = Path(dirpath).relative_to(raiz)
        dirs.sort()
        if "_internal" in dirs:
            dirs.remove("_internal")
            linhas.append(f"  {rel / '_internal'}/ (nao listado)")
        for f in sorted(files):
            try:
                t = (Path(dirpath) / f).stat().st_size
            except OSError:
                t = -1
            linhas.append(f"  {rel / f}  {t} bytes")
            n += 1
            if n >= limite:
                linhas.append("  ...")
                return
        for d in dirs:
            if not any((Path(dirpath) / d).iterdir()):
                linhas.append(f"  {rel / d}/ (vazia)")


def foto(nome: str, instalada: Path) -> str:
    """So le. Grava fotos/<nome>.txt."""
    linhas = [f"FOTO {nome}", f"LocalAppData do Windows (SHGetKnownFolderPath): {LAD}"]
    linhas.append(f"[1] {RESERVA} (LocalAppData + nome do pacote de mentira: a pasta de reserva esperada)")
    arvore(RESERVA, linhas)
    linhas.append(f"[2] {DADOS_DE_MENTIRA} (LocalAppData + nome da pasta dos dados de mentira: os 'projetos')")
    arvore(DADOS_DE_MENTIRA, linhas)
    linhas.append(f"[3] {instalada} (a pasta instalada)")
    arvore(instalada, linhas)
    linhas.append(f"[4] {DADOS_DE_VERDADE} (pasta de VERDADE dos projetos: so os nomes do primeiro nivel)")
    linhas.append("  " + (", ".join(sorted(p.name for p in DADOS_DE_VERDADE.iterdir()))
                          if DADOS_DE_VERDADE.exists() else "(nao existe)"))
    linhas.append(f"[2b] {PASTA_DO_TITULO} (LocalAppData + TITULO do pacote de mentira)")
    arvore(PASTA_DO_TITULO, linhas)
    linhas.append(f"[2c] {TEMP_DO_TITULO} (Temp + velopack_ + TITULO)")
    arvore(TEMP_DO_TITULO, linhas)
    novo = LAD / N["pacote_de_verdade"]
    linhas.append(f"[5] {novo} (a pasta de reserva do programa de verdade: nunca deve aparecer nesta prova)")
    linhas.append("  existe" if novo.exists() else "  (nao existe)")
    vlog = LAD / "velopack"
    linhas.append(f"[6] {vlog} (logs do Velopack)")
    linhas.append("  " + (", ".join(sorted(p.name for p in vlog.iterdir())) if vlog.exists() else "(nao existe)"))
    linhas.append(f"[7] {BASE / 'localappdata-de-mentira'} (a VARIAVEL LOCALAPPDATA que o app de mentira recebe)")
    arvore(BASE / "localappdata-de-mentira", linhas, 20)
    texto = "\n".join(linhas) + "\n"
    FOTOS.mkdir(parents=True, exist_ok=True)
    (FOTOS / f"{nome}.txt").write_text(texto, encoding="utf-8")
    print(texto)
    return texto


def rodar(comando: list, rotulo: str) -> int:
    feito = subprocess.run([str(c) for c in comando], capture_output=True, text=True, creationflags=SEM_JANELA,
                           errors="replace")
    with open(BASE / "comandos.txt", "a", encoding="utf-8") as f:
        f.write(f"--- {rotulo}: {' '.join(str(c) for c in comando)}\n    codigo={feito.returncode}\n")
        for nome, saida in (("saida", feito.stdout), ("erro", feito.stderr)):
            if saida.strip():
                f.write("    " + nome + ": " + saida.strip().replace("\n", "\n      ") + "\n")
    print(f"{rotulo}: codigo {feito.returncode}")
    return feito.returncode


def etapa_nomes() -> None:
    print(json.dumps(N, indent=2, ensure_ascii=False))
    for p in (RESERVA, DADOS_DE_MENTIRA, LAD / N["pacote_de_verdade"]):
        print(f"{p}: {'JA EXISTE' if p.exists() else 'nao existe'}")
    BASE.mkdir(parents=True, exist_ok=True)
    (BASE / "nomes.json").write_text(json.dumps(N, indent=2, ensure_ascii=False), encoding="utf-8")


def etapa_montar() -> None:
    app = BASE / "app"
    app.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).with_name("ProvaNome.py"), app / "ProvaNome.py")
    ocultos = ["velopack", "atualizacao", "assinatura", "versao", "configuracoes",
               "core.testes_a_distancia", "core._testes_a_distancia_windows"]
    fora = ["PySide6", "numpy", "cv2", "fitz", "pymupdf", "PIL", "scipy", "onnxruntime", "skimage", "hf_xet",
            "huggingface_hub", "pypdfium2", "pypdfium2_raw", "torch", "doxapy", "matplotlib", "pandas",
            "sqlite3", "tkinter"]
    comando = [PY, "-m", "PyInstaller", "--noconfirm", "--windowed", "--name", "ProvaNome",
               "--distpath", app / "dist", "--workpath", app / "build", "--specpath", app, "--paths", WT]
    for m in ocultos:
        comando += ["--hidden-import", m]
    for m in fora:
        comando += ["--exclude-module", m]
    assert rodar(comando + [app / "ProvaNome.py"], "pyinstaller") == 0
    pasta = app / "dist" / "ProvaNome"
    assert (pasta / "ProvaNome.exe").is_file()

    sys.path.insert(0, str(WT))
    import assinatura
    import empacotar
    import publicar_versao_kaique as pub
    import versao

    versao.ID_DO_PACOTE = N["pacote_de_mentira"]          # a regra: pacote = o do programa + "Prova"
    vpk = empacotar.achar_vpk()
    VERSOES.mkdir(parents=True, exist_ok=True)
    for numero in ("1.0.0", "1.0.1"):
        comando = empacotar.comando_do_vpk(vpk, pasta, VERSOES, numero)
        comando[comando.index("--mainExe") + 1] = "ProvaNome.exe"
        comando[comando.index("--packTitle") + 1] = TITULO_DA_PROVA
        comando[comando.index("--instLocation") + 1] = "Either"
        comando += ["--shortcuts", ""]
        assert rodar(comando, f"vpk pack {numero}") == 0
        nupkg = empacotar.nupkg_inteiro(VERSOES, numero)
        assert nupkg.is_file(), nupkg
        if numero == "1.0.0":
            (BASE / "msi-1.0.0").mkdir(exist_ok=True)
            msi = next(VERSOES.glob("*.msi"))
            shutil.copy2(msi, BASE / "msi-1.0.0" / msi.name)
    etapa_assinar()


def etapa_assinar() -> None:
    """Assina a 1.0.1 com a chave de MENTIRA de 17/11 (64 letras hexadecimais), pelo mesmo assinar_pacote do
    publicar_versao_kaique.py, com o nome do pacote de mentira."""
    sys.path.insert(0, str(WT))
    import assinatura
    import empacotar
    import publicar_versao_kaique as pub
    import versao

    versao.ID_DO_PACOTE = N["pacote_de_mentira"]
    publica = (CHAVE / "publica.txt").read_text().strip()
    chave = bytes.fromhex((CHAVE / "privada.txt").read_text().strip())
    assert assinatura.secret_to_public(chave).hex() == publica
    arquivo = pub.assinar_pacote(chave, empacotar.nupkg_inteiro(VERSOES, "1.0.1"), "1.0.1", publica)
    print("assinada:", arquivo.name)
    print("pacotes:", sorted(p.name for p in VERSOES.iterdir()))


def _msi() -> Path:
    return next((BASE / "msi-1.0.0").glob("*.msi"))


def _projeto_de_mentira(raiz: Path) -> None:
    p = raiz / "projetos" / "livro-de-mentira"
    p.mkdir(parents=True, exist_ok=True)
    (p / "projeto.json").write_text('{"de_mentira": true}', encoding="utf-8")
    (raiz / "configuracoes.json").write_text("{}", encoding="utf-8")
    (raiz / "historico.json").write_text("[]", encoding="utf-8")


def _chamadas(instalada: Path, prefixo: str, apagar_reserva_antes: bool) -> None:
    exe = instalada / "current" / "ProvaNome.exe"
    for modo in ("prova-app-run", "prova-versao", "prova-portatil", "prova-procurar-ao-abrir"):
        if apagar_reserva_antes and RESERVA.exists():
            shutil.rmtree(RESERVA)        # a pasta do pacote de mentira (criada pela prova), para ver quem a cria
        rodar([exe, modo], f"{prefixo} {modo}")
        foto(f"{prefixo}-{modo}", instalada)
    if apagar_reserva_antes and RESERVA.exists():
        shutil.rmtree(RESERVA)
    rodar([exe, "--procurar-atualizacao", "--fonte", VERSOES], f"{prefixo} --procurar-atualizacao")
    foto(f"{prefixo}-procurar-e-baixar", instalada)


def _desinstalar(rotulo: str, log: str) -> None:
    rodar(["msiexec", "/x", _msi(), "/qn", "/l*v", BASE / log], rotulo)


def etapa_caso_a() -> None:
    usuario = os.environ["USERNAME"]
    _projeto_de_mentira(DADOS_DE_MENTIRA)
    foto("00-antes-de-tudo", TRANCADA)
    assert rodar(["msiexec", "/i", _msi(), "/qn", f"VELOPACK_INSTALLDIR={TRANCADA}", "/l*v",
                  BASE / "msi-instalar-trancada.log"], "instalar (trancada)") == 0
    assert rodar(["icacls", TRANCADA, "/deny", f"{usuario}:(WD,AD)"], "trancar a raiz") == 0
    _chamadas(TRANCADA, "A", apagar_reserva_antes=True)
    # antes de desinstalar: um projeto de mentira tambem DENTRO da pasta do pacote (para ver quem o desinstalador limpa)
    _projeto_de_mentira(RESERVA)
    foto("C1-antes-de-desinstalar", TRANCADA)
    assert rodar(["icacls", TRANCADA, "/remove:d", usuario], "destrancar a raiz") == 0
    _desinstalar("desinstalar (trancada)", "msi-desinstalar-trancada.log")
    foto("C1-depois-de-desinstalar", TRANCADA)


def etapa_caso_b() -> None:
    # O que o caso A deixou na pasta do pacote de mentira (o desinstalador nao limpou: ver C1) sai antes,
    # para ver se o caso B a cria.
    if RESERVA.exists():
        shutil.rmtree(RESERVA)
    assert rodar(["msiexec", "/i", _msi(), "/qn", f"VELOPACK_INSTALLDIR={ABERTA}", "/l*v",
                  BASE / "msi-instalar-aberta.log"], "instalar (aberta)") == 0
    _chamadas(ABERTA, "B", apagar_reserva_antes=False)
    _projeto_de_mentira(RESERVA)
    # Achado do caso A (17/11, esta prova): o .msi do vpk 1.2.161 passa a limpeza o TITULO do pacote
    # (RustAppId = {{AppTitle}} no modelo do WiX), e nao o nome. Para ver o que ele apaga: uma marca em
    # LocalAppData\<titulo> e outra em Tempelopack_<titulo>.
    _projeto_de_mentira(PASTA_DO_TITULO)
    TEMP_DO_TITULO.mkdir(parents=True, exist_ok=True)
    (TEMP_DO_TITULO / "marca.txt").write_text("prova", encoding="utf-8")
    foto("C2-antes-de-desinstalar", ABERTA)
    _desinstalar("desinstalar (aberta)", "msi-desinstalar-aberta.log")
    foto("C2-depois-de-desinstalar", ABERTA)


def etapa_limpar() -> None:
    """So o que esta prova criou fora de D:\\agente_temp_testes\\nome-pacote."""
    for p in (DADOS_DE_MENTIRA, RESERVA, PASTA_DO_TITULO, TEMP_DO_TITULO):
        if p.exists():
            print("apagando", p, sorted(str(q.relative_to(p)) for q in p.rglob("*")))
            shutil.rmtree(p)
    log = LAD / "velopack" / f"velopack_{N['pacote_de_mentira']}.log"
    if log.exists():
        print("apagando", log)
        log.unlink()
    foto("99-depois-de-limpar", ABERTA)


if __name__ == "__main__":
    {"nomes": etapa_nomes, "montar": etapa_montar, "assinar": etapa_assinar, "caso-a": etapa_caso_a, "caso-b": etapa_caso_b,
     "limpar": etapa_limpar}[sys.argv[1]]()
