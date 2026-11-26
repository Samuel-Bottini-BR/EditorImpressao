"""Prova de quem tenta quebrar (24/11/2026): a licenca da pasta "pega" num arquivo aberto por outro processo sem
compartilhar nada? (ressalva 2 do plano: "nao conferi que o Windows muda a licenca de um arquivo em uso").

Roda a funcao de verdade `core.windows.dar_licenca_aos_usuarios` (o icacls de verdade) numa pasta de prova MINHA,
passada na linha de comando (nunca em Arquivos de Programas). Um arquivo de dentro fica aberto, sem compartilhar
leitura, gravacao nem apagar, durante o passo.
Uso: python prova_licenca_arquivo_em_uso.py <raiz do worktree> <pasta de prova vazia>"""
import ctypes
import sys
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from core import windows  # noqa: E402

pasta = Path(sys.argv[2])
raiz = pasta / "EditorImpressaoProva"
(raiz / "current" / "sub").mkdir(parents=True)
(raiz / "current" / "sq.version").write_text("<versao/>", encoding="utf-8")
preso = raiz / "current" / "sub" / "preso.dll"
preso.write_bytes(b"MZ" + b"0" * 1000)
(raiz / "current" / "sub" / "zz_depois.txt").write_text("depois do preso", encoding="utf-8")

k = ctypes.WinDLL("kernel32", use_last_error=True)
k.CreateFileW.restype = wintypes.HANDLE
k.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
                          wintypes.DWORD, wintypes.HANDLE]
GENERIC_READ, OPEN_EXISTING = 0x80000000, 3
alca = k.CreateFileW(str(preso), GENERIC_READ, 0, None, OPEN_EXISTING, 0, None)   # share = 0: nada compartilhado
print("arquivo preso aberto:", bool(alca) and alca != wintypes.HANDLE(-1).value)
try:
    r = windows.dar_licenca_aos_usuarios(raiz)
    print("desfecho:", r.desfecho, "|", r.motivo)
    for f in (raiz, raiz / "current" / "sq.version", preso, raiz / "current" / "sub" / "zz_depois.txt"):
        try:
            print(f"  Usuarios modificam {f.name}: {windows.usuarios_modificam(windows.ler_licencas(f))}")
        except OSError as erro:
            print(f"  {f.name}: nao deu para ler ({erro})")
    print("saida do icacls:", (r.dados.get("saida") or r.detalhe or "")[-600:])
finally:
    k.CloseHandle(alca)
