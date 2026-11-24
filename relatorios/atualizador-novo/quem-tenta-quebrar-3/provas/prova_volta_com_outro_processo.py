"""Prova EXECUTADA (quem tenta quebrar 3, 24/11/2026): a volta para a anterior quando OUTRO processo de dentro de
`current\\` está aberto (o que acontece quando o Kaique clica no atalho nos segundos sem nada na tela em que a versão
nova faz o teste rápido antes da janela: as duas aberturas testam, as duas reprovam e as duas pedem a volta).

De verdade: a peça do Windows do ramo (`core.windows.programas_rodando_de`, a lista de processos do Windows), o executor
do ramo (`Atualizacao._voltar` e a conferência única da troca), a biblioteca do Velopack copiando o pacote guardado
(sem internet) e a regra (`proxima_fase`). O "outro processo" é uma cópia do `ping.exe` do Windows posta em
`current\\EditorImpressao.exe` e aberta SEM JANELA (CREATE_NO_WINDOW), esperando 30 s. A chave do Samuel é a de prova;
o motor é dado como no lugar; o pedido final ao Update.exe só é anotado.
Uso: python prova_volta_com_outro_processo.py (saída em prova_volta_com_outro_processo-resultado.txt)
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAMO))
sys.path.insert(0, str(RAMO / "tests"))
os.environ["PROGRAMDATA"] = str(RAMO / "saida_teste" / "qtq3" / "programdata-falso")
os.environ["HTTPS_PROXY"] = os.environ["HTTP_PROXY"] = "http://127.0.0.1:9"     # sem internet neste processo
R = RAMO / "saida_teste" / "qtq3" / "outro-processo"

import assinatura  # noqa: E402
import atualizacao  # noqa: E402
import versao  # noqa: E402
from ajudante_do_atualizador import CHAVE, PUBLICA  # noqa: E402
from core import conversa_com_o_velopack as conversa  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402
from core import windows  # noqa: E402

PACOTE = versao.ID_DO_PACOTE


class VelopackDeVerdade:
    def __init__(self, raiz: Path):
        import velopack
        self.loc = velopack.VelopackLocatorConfig(raiz, raiz / "Update.exe", raiz / "packages",
                                                  raiz / "current" / "sq.version", raiz / "current", False)
        self.trocas: list = []

    def pacote_da_versao(self, *a):
        return conversa.pacote_da_versao(*a)

    def baixar(self, endereco, v):
        return conversa.baixar(endereco, v, self.loc)

    def trocar(self, endereco, v, reabrir, argumentos):
        self.trocas.append((v.versao, reabrir, list(argumentos)))


def main() -> None:
    if R.exists():
        shutil.rmtree(R)
    raiz = R / "instalado"
    (raiz / "current").mkdir(parents=True)
    (raiz / "packages").mkdir()
    (raiz / "current" / "sq.version").write_text(
        f'<?xml version="1.0"?><package><metadata><id>{PACOTE}</id><version>1.2.0</version><title>E</title>'
        '<authors>x</authors><description>x</description><mainExe>EditorImpressao.exe</mainExe></metadata>'
        '</package>', encoding="utf-8")
    (raiz / "Update.exe").write_bytes(b"MZ")
    dados = io.BytesIO()
    with zipfile.ZipFile(dados, "w") as z:
        z.writestr(f"{PACOTE}.nuspec", "x")
        z.writestr("lib/app/motor-exigido.json", json.dumps({"versao": 1}))
    pacote = dados.getvalue()
    boa = atualizacao.pasta_da_ultima_boa(raiz)
    boa.mkdir()
    nome = atualizacao.nome_do_pacote("1.1.0")
    (boa / nome).write_bytes(pacote)
    (boa / assinatura.nome_do_arquivo_da_assinatura(PACOTE, "1.1.0")).write_bytes(assinatura.escrever_assinatura(
        CHAVE, assinatura.VersaoAssinada(PACOTE, "1.1.0", nome, hashlib.sha256(pacote).hexdigest())).encode())
    shutil.copy(Path(os.environ["SystemRoot"]) / "System32" / "PING.EXE", raiz / "current" / "EditorImpressao.exe")
    # aberto por um processo intermediário que sai logo (como o atalho: quem o abriu já não existe), para não ser da
    # "família" deste processo (a conferência deixa de fora este processo e os que ele abriu)
    lancador = ("import subprocess,sys;p=subprocess.Popen([sys.argv[1],'-n','30','127.0.0.1'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,"
                "creationflags=0x08000000);print(p.pid)")
    pid = int(subprocess.run([sys.executable, "-c", lancador, str(raiz / "current" / "EditorImpressao.exe")],
                             capture_output=True, text=True).stdout.strip())
    import time
    time.sleep(1)
    try:
        vista = windows.programas_rodando_de(raiz / "current", menos_a_familia_de=windows.numero_deste_processo())
        vp = VelopackDeVerdade(raiz)
        a = atualizacao.Atualizacao(windows=windows, velopack=vp, raiz=raiz, chave_publica=PUBLICA,
                                    motor_no_lugar=lambda *_: True, por_tras=lambda t: t())
        # a regra até o Voltar (a abertura antes da janela, a 1.2.0 reprovada), e então o efeito de verdade
        e, efs = fases.proxima_fase(fases.Estado(), fases.Abriu(True, False, False, True, "1.2.0", ultima_boa="1.1.0"))
        e, efs2 = fases.proxima_fase(e, fases.TesteRapido(False, "código 1"))
        volta = a._voltar(next(x for x in efs2 if isinstance(x, fases.Voltar)))
        e, efs3 = fases.proxima_fase(e, volta)
    finally:
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
    resultado = {
        "o que a peça do Windows viu de dentro de current\\": vista,
        "a volta (VoltaPedida)": [volta.certa, volta.motivo],
        "pedido ao Update.exe": vp.trocas,
        "o que a regra manda depois": [repr(x) for x in efs3],
        "a frase que vai para a tela": [atualizacao.frase_da_falha(x.tipo) for x in efs3
                                        if isinstance(x, fases.MostrarFalha)],
        "o processo sai antes da janela?": any(isinstance(x, fases.Sair) for x in efs3),
        "a fase": e.fase.value}
    texto = json.dumps(resultado, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_volta_com_outro_processo-resultado.txt").write_text(texto, encoding="utf-8")
    print(texto)
    shutil.rmtree(R)


if __name__ == "__main__":
    main()
