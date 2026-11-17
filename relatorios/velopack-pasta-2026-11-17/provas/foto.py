r"""Foto (so le): o que existe nas pastas que importam para a prova.

Uso: python -I foto.py <nome-da-foto> <pasta-instalada>
Grava fotos/<nome>.txt. A pasta de verdade dos projetos (%LOCALAPPDATA%\EditorImpressao)
so e OLHADA no primeiro nivel (nomes), nunca aberta para mudar.
"""
import ctypes, sys, os
from ctypes import wintypes
from pathlib import Path


def local_app_data_do_windows():
    # o mesmo que o Velopack usa: SHGetKnownFolderPath(FOLDERID_LocalAppData)
    class GUID(ctypes.Structure):
        _fields_ = [("a", wintypes.DWORD), ("b", wintypes.WORD), ("c", wintypes.WORD), ("d", ctypes.c_ubyte * 8)]
    g = GUID(0xF1B32785, 0x6FBA, 0x4FCF, (ctypes.c_ubyte * 8)(0x9D, 0x55, 0x7B, 0x8E, 0x7F, 0x15, 0x70, 0x91))
    p = ctypes.c_wchar_p()
    ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(g), 0, None, ctypes.byref(p))
    v = p.value
    ctypes.windll.ole32.CoTaskMemFree(p)
    return Path(v)


def arvore(raiz: Path, linhas, limite=60):
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
            q = Path(dirpath) / f
            try:
                t = q.stat().st_size
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


nome, instalada = sys.argv[1], Path(sys.argv[2])
lad = local_app_data_do_windows()
linhas = [f"FOTO {nome}", f"LocalAppData do Windows (SHGetKnownFolderPath): {lad}"]
linhas.append(f"[1] {lad / 'EditorImpressaoProvaPasta'} (a pasta de reserva esperada, do pacote de mentira)")
arvore(lad / "EditorImpressaoProvaPasta", linhas)
linhas.append(f"[2] {instalada} (a pasta instalada)")
arvore(instalada, linhas)
real = lad / "EditorImpressao"
linhas.append(f"[3] {real} (pasta de verdade dos projetos: so os nomes do primeiro nivel)")
linhas.append("  " + ", ".join(sorted(p.name for p in real.iterdir())) if real.exists() else "  (nao existe)")
linhas.append(f"[4] {lad / 'velopack'} (logs do Velopack)")
linhas.append("  " + ", ".join(sorted(p.name for p in (lad / 'velopack').iterdir())) if (lad / 'velopack').exists() else "  (nao existe)")
base = Path(r"D:\agente_temp_testes\velopack-pasta")
linhas.append(f"[5] {base / 'localappdata-de-mentira'} (a VARIAVEL LOCALAPPDATA que o app de mentira recebe)")
arvore(base / "localappdata-de-mentira", linhas, 20)
texto = "\n".join(linhas) + "\n"
(base / "fotos" / f"{nome}.txt").write_text(texto, encoding="utf-8")
print(texto)
