"""Prova EXECUTADA (quem tenta quebrar, volta 2): o estado.json e o atualizacao.log que a conta do Kaique só consegue LER.

Quando acontece de verdade: a primeira abertura feita com a licença de administrador (o "Iniciar" do fim do .msi aberto
por uma janela com licença: prova nº 1 de 22/11) roda `Atualizacao.abrir`, que grava o estado.json logo de saída
(`estado_aceita_gravacao`) e escreve no registro. O arquivo nasce do grupo Administradores e herda da pasta
C:\\ProgramData só "ler" para Usuários (a licença da pasta foi lida com o `icacls` só lendo, sem mudar nada).

Aqui, numa pasta MINHA no D:, a mesma licença é imitada com o `icacls` de verdade: a pasta deixa criar arquivo novo e
ler; o estado.json e o atualizacao.log que já existem só deixam ler. Então o executor de verdade abre três vezes
(com a versão nova publicada). No fim a licença da pasta é devolvida ao normal (`icacls /reset`).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RAMO = Path(r"D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo")
R = Path(r"D:\programas\EditorImpressao\rascunho-qtq2\outra-conta")
os.environ["PROGRAMDATA"] = str(R / "pd")
os.environ["LOCALAPPDATA"] = str(R / "local")
sys.path.insert(0, str(RAMO))
import atualizacao  # noqa: E402
import versao  # noqa: E402

versao.VERSAO = "1.1.0"
EU = os.environ["USERNAME"]
pasta = atualizacao.pasta_do_estado()
pasta.mkdir(parents=True, exist_ok=True)
(R / "local" / "EditorImpressao").mkdir(parents=True, exist_ok=True)
atualizacao.gravar_estado({})
atualizacao.registrar("criado pela abertura com licença (imitada)")


def icacls(*args):
    r = subprocess.run(["icacls", *map(str, args)], capture_output=True, text=True, encoding="oem", errors="replace")
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:]


saida = {"licencas": [
    icacls(pasta, "/inheritance:r", "/grant:r", f"{EU}:(CI)(WD,AD,WEA,WA)", f"{EU}:(OI)(CI)(RX)",
           "*S-1-3-0:(OI)(CI)(IO)(F)"),
    icacls(pasta / "estado.json", "/inheritance:r", "/grant:r", f"{EU}:(RX)"),
    icacls(pasta / "atualizacao.log", "/inheritance:r", "/grant:r", f"{EU}:(RX)"),
]}


class Achada:
    pacote, versao, arquivo, sha256, tamanho = "EditorImpressaoPrograma", "1.2.0", "x-1.2.0-full.nupkg", "ab" * 32, 1


class Velopack:
    procuras = 0

    @classmethod
    def procurar(cls, endereco):
        cls.procuras += 1
        return Achada()


aberturas = []
try:
    for i in range(3):
        a = atualizacao.Atualizacao(windows=None, velopack=Velopack, raiz=R / "raiz", por_tras=lambda f: f(),
                                    pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                    motor_no_lugar=lambda v: True, chave_publica=None)
        a.abrir([])
        aberturas.append({"fase": a.estado.fase.value, "procurou": Velopack.procuras,
                          "para a tela": [type(e).__name__ for e in a._fila_da_tela]})
finally:
    devolvida = icacls(R, "/reset", "/T", "/C")
saida["aberturas"] = aberturas
saida["licenca devolvida"] = devolvida
saida["atualizacao.log (o que a gerente le de longe)"] = (pasta / "atualizacao.log").read_text(encoding="utf-8")
erros = R / "local" / "EditorImpressao" / "erros.log"
saida["erros.log da conta"] = erros.read_text(encoding="utf-8") if erros.exists() else ""
texto = json.dumps(saida, ensure_ascii=False, indent=1)
Path(__file__).with_name("prova_estado_de_outra_conta-resultado.txt").write_text(texto, encoding="utf-8")
print(texto)
