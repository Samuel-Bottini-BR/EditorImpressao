"""Prova EXECUTADA (quem tenta quebrar 3, 24/11/2026): a guarda da última boa (D-844/D-851) e a volta pelo pacote
guardado, no disco de verdade, com as funções de verdade do ramo (`atualizacao.guardar_ultima_boa`,
`Atualizacao._guardar`, `Atualizacao._voltar`, `ler_ultima_boa`) e, na volta, a BIBLIOTECA DO VELOPACK DE VERDADE
copiando e conferindo o pacote (só o pedido final ao `Update.exe` é anotado, não feito: ele está provado na
`prova_volta_recusada.py`, parte C).

O que é de mentira, e só isto: a chave do Samuel (uma chave de prova, a mesma dos testes); o "disco cheio" (sem licença
de administrador não dá para criar um disco pequeno: um arquivo que levanta "sem espaço" depois de 8 MB); a peça do
Windows na conferência da troca (nenhum outro programa aberto); o motor do Kraken (dado como no lugar). "Sem internet":
o processo inteiro com um proxy que não existe (HTTPS_PROXY/HTTP_PROXY = 127.0.0.1:9), que o Python e o Velopack usam.

Tudo em `saida_teste\\qtq3\\guarda`. Uso: python prova_guarda_e_volta.py (saída em prova_guarda_e_volta-resultado.txt)
"""
from __future__ import annotations

import ctypes
import errno
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAMO))
sys.path.insert(0, str(RAMO / "tests"))
os.environ["PROGRAMDATA"] = str(RAMO / "saida_teste" / "qtq3" / "programdata-falso")
os.environ["HTTPS_PROXY"] = os.environ["HTTP_PROXY"] = "http://127.0.0.1:9"     # sem internet neste processo
R = RAMO / "saida_teste" / "qtq3" / "guarda"

import assinatura  # noqa: E402
import atualizacao  # noqa: E402
import versao  # noqa: E402
from ajudante_do_atualizador import CHAVE, OUTRA_CHAVE, PUBLICA  # noqa: E402
from core import conversa_com_o_velopack as conversa  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402

PACOTE = versao.ID_DO_PACOTE
TAMANHO = 120 * 1024 * 1024        # 120 MB (o de verdade tem 460 MB: o tamanho só muda o tempo)


def nupkg(v: str, tamanho: int = TAMANHO) -> bytes:
    """Um .nupkg que o Velopack sabe ler (manifesto + motor-exigido.json) com um enchimento até `tamanho`."""
    dados = io.BytesIO()
    with zipfile.ZipFile(dados, "w", zipfile.ZIP_STORED) as z:
        z.writestr(f"{PACOTE}.nuspec", f'<?xml version="1.0"?><package><metadata><id>{PACOTE}</id><version>{v}'
                   '</version><title>Editor</title><authors>x</authors><description>x</description>'
                   '<mainExe>EditorImpressao.exe</mainExe></metadata></package>')
        z.writestr("lib/app/motor-exigido.json", json.dumps({"versao": 1}))
        z.writestr("lib/app/enchimento.bin", os.urandom(tamanho))
    return dados.getvalue()


def assinar(v: str, dados: bytes, chave: bytes = CHAVE) -> str:
    nome = atualizacao.nome_do_pacote(v)
    return assinatura.escrever_assinatura(chave, assinatura.VersaoAssinada(PACOTE, v, nome,
                                                                           hashlib.sha256(dados).hexdigest()))


def nova_instalacao(caso: str, rodando: str = "1.2.0") -> Path:
    raiz = R / caso
    if raiz.exists():
        shutil.rmtree(raiz)
    (raiz / "current").mkdir(parents=True)
    (raiz / "packages").mkdir()
    (raiz / "current" / "sq.version").write_text(
        f'<?xml version="1.0"?><package><metadata><id>{PACOTE}</id><version>{rodando}</version><title>E</title>'
        '<authors>x</authors><description>x</description><mainExe>EditorImpressao.exe</mainExe></metadata>'
        '</package>', encoding="utf-8")
    (raiz / "Update.exe").write_bytes(b"MZ")        # a biblioteca só confere que existe; nada aqui o roda
    return raiz


PACOTES: dict[str, bytes] = {}


def por_a_ultima_boa(raiz: Path, v: str) -> None:
    """A última boa de antes (pacote + assinatura) em <raiz>\\ultima-boa, como a guarda deixa."""
    pasta = atualizacao.pasta_da_ultima_boa(raiz)
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / atualizacao.nome_do_pacote(v)).write_bytes(PACOTES[v])
    (pasta / assinatura.nome_do_arquivo_da_assinatura(PACOTE, v)).write_bytes(assinar(v, PACOTES[v]).encode())


def foto(raiz: Path) -> dict:
    pasta = atualizacao.pasta_da_ultima_boa(raiz)
    return {"ultima-boa\\": sorted(f"{p.name} ({p.stat().st_size // 2**20} MB)" for p in pasta.iterdir())
            if pasta.exists() else [], "packages\\": sorted(p.name for p in (raiz / "packages").iterdir()),
            "ler_ultima_boa": atualizacao.ler_ultima_boa(raiz)}


def guardar(raiz: Path, v: str = "1.2.0", fonte: str = "https://github.com/Samuel-Bottini-BR/EditorImpressao"):
    inicio = time.time()
    motivo = atualizacao.guardar_ultima_boa(raiz, v, atualizacao.Fonte(fonte), PUBLICA)
    return {"devolveu": motivo or "None (guardado e conferido)", "segundos": round(time.time() - inicio, 1),
            **foto(raiz)}


def segurar_sem_compartilhar(caminho: Path, segundos: int) -> subprocess.Popen:
    """OUTRO processo abre o arquivo sem deixar ninguém mais abrir (como um antivírus examinando)."""
    codigo = ("import ctypes,sys,time;k=ctypes.windll.kernel32;k.CreateFileW.restype=ctypes.c_void_p;"
              f"h=k.CreateFileW(r'{caminho}',0x80000000,0,None,3,0x80,None);print(h,flush=True);"
              f"time.sleep({segundos})")
    p = subprocess.Popen([sys.executable, "-c", codigo], stdout=subprocess.PIPE, text=True)
    p.stdout.readline()
    return p


class VelopackDeVerdade:
    """A peça do Velopack do ramo, com a biblioteca de verdade, apontada para a instalação de prova (o localizador). O
    pedido final ao Update.exe (`trocar`) só é anotado."""

    def __init__(self, raiz: Path):
        import velopack
        self.loc = velopack.VelopackLocatorConfig(raiz, raiz / "Update.exe", raiz / "packages",
                                                  raiz / "current" / "sq.version", raiz / "current", False)
        self.trocas: list = []

    def pacote_da_versao(self, *a):
        return conversa.pacote_da_versao(*a)

    def baixar(self, endereco, v):
        return conversa.baixar(endereco, v, self.loc)

    def pendente(self, endereco):
        return conversa.pendente(endereco, self.loc)

    def trocar(self, endereco, v, reabrir, argumentos):
        self.trocas.append((v.versao, reabrir, list(argumentos)))


class WindowsSemOutros:
    def programas_rodando_de(self, pasta, menos_a_familia_de=None, nomes=None):
        return []

    def numero_deste_processo(self):
        return os.getpid()

    def caminho_conferido(self, c):
        return True


def voltar(raiz: Path) -> dict:
    vp = VelopackDeVerdade(raiz)
    a = atualizacao.Atualizacao(windows=WindowsSemOutros(), velopack=vp, raiz=raiz, chave_publica=PUBLICA,
                                motor_no_lugar=lambda *_: True, por_tras=lambda t: t())
    inicio = time.time()
    r = a._voltar(fases.Voltar("1.2.0", "1.1.0", reabrir=True))
    return {"VoltaPedida": [r.certa, r.motivo], "segundos": round(time.time() - inicio, 1),
            "pedido ao Update.exe (anotado)": vp.trocas, **foto(raiz)}


def main() -> None:
    R.mkdir(parents=True, exist_ok=True)
    for v in ("1.1.0", "1.2.0"):
        PACOTES[v] = nupkg(v)
    res: dict = {}

    # G1: o caso de toda troca: o pacote da 1.2.0 em packages\\, a assinatura guardada ao conferir; sem internet.
    raiz = nova_instalacao("g1")
    por_a_ultima_boa(raiz, "1.1.0")
    (raiz / "packages" / atualizacao.nome_do_pacote("1.2.0")).write_bytes(PACOTES["1.2.0"])
    pasta = atualizacao.pasta_da_ultima_boa(raiz)
    (pasta / assinatura.nome_do_arquivo_da_assinatura(PACOTE, "1.2.0")).write_bytes(assinar("1.2.0", PACOTES["1.2.0"]).encode())
    res["G1 presente em packages, sem internet"] = guardar(raiz)

    # G2: o pacote não está em packages (o caso do .msi), sem internet (o executor tenta baixar)
    raiz = nova_instalacao("g2")
    por_a_ultima_boa(raiz, "1.1.0")
    a = atualizacao.Atualizacao(windows=WindowsSemOutros(), velopack=VelopackDeVerdade(raiz), raiz=raiz,
                                chave_publica=PUBLICA, por_tras=lambda t: t())
    eventos = []
    a.evento = lambda e: eventos.append(e)          # só o resultado do efeito, sem seguir a regra
    a._guardar("1.2.0")
    res["G2 ausente de packages, sem internet (Atualizacao._guardar)"] = {"evento": repr(eventos), **foto(raiz)}

    # G3: o pacote em packages incompleto (cortado no meio)
    raiz = nova_instalacao("g3")
    por_a_ultima_boa(raiz, "1.1.0")
    (raiz / "packages" / atualizacao.nome_do_pacote("1.2.0")).write_bytes(PACOTES["1.2.0"][: TAMANHO // 2])
    (atualizacao.pasta_da_ultima_boa(raiz) / assinatura.nome_do_arquivo_da_assinatura(PACOTE, "1.2.0")).write_bytes(
        assinar("1.2.0", PACOTES["1.2.0"]).encode())
    res["G3 incompleto em packages"] = guardar(raiz)

    # G4: a assinatura guardada é de outra chave; G5: assinatura certa, mas de outro conteúdo
    for caso, texto in (("g4", assinar("1.2.0", PACOTES["1.2.0"], OUTRA_CHAVE)),
                        ("g5", assinar("1.2.0", PACOTES["1.2.0"] + b"x"))):
        raiz = nova_instalacao(caso)
        por_a_ultima_boa(raiz, "1.1.0")
        (raiz / "packages" / atualizacao.nome_do_pacote("1.2.0")).write_bytes(PACOTES["1.2.0"])
        (atualizacao.pasta_da_ultima_boa(raiz) / assinatura.nome_do_arquivo_da_assinatura(PACOTE, "1.2.0")).write_bytes(
            texto.encode())
        res[{"g4": "G4 assinatura de outra chave", "g5": "G5 assinatura que não bate com o pacote"}[caso]] = guardar(raiz)

    def preparar(caso: str) -> Path:
        raiz = nova_instalacao(caso)
        por_a_ultima_boa(raiz, "1.1.0")
        (raiz / "packages" / atualizacao.nome_do_pacote("1.2.0")).write_bytes(PACOTES["1.2.0"])
        (atualizacao.pasta_da_ultima_boa(raiz) / assinatura.nome_do_arquivo_da_assinatura(PACOTE, "1.2.0")).write_bytes(
            assinar("1.2.0", PACOTES["1.2.0"]).encode())
        return raiz

    # G6: disco cheio (simulado: o arquivo de destino levanta "sem espaço" depois de 8 MB)
    raiz = preparar("g6")
    original = Path.open
    escrito = {"bytes": 0}

    class Cheio(io.FileIO):
        def write(self, b):
            escrito["bytes"] += len(b)
            if escrito["bytes"] > 8 * 2**20:
                raise OSError(errno.ENOSPC, "Espaço insuficiente no disco (simulado)")
            return super().write(b)

    def abrir(self, *a, **k):
        modo = k.get("mode", a[0] if a else "r")
        if modo == "wb" and self.name.endswith(".chegando"):
            return Cheio(str(self), "wb")
        return original(self, *a, **k)

    Path.open = abrir
    try:
        res["G6 disco cheio (simulado)"] = guardar(raiz)
    finally:
        Path.open = original

    # G7: o pacote de packages\\ preso por outro processo, sem compartilhar
    raiz = preparar("g7")
    p = segurar_sem_compartilhar(raiz / "packages" / atualizacao.nome_do_pacote("1.2.0"), 30)
    try:
        res["G7 origem presa por outro processo"] = guardar(raiz)
    finally:
        p.kill()
        p.wait()

    # G8: o nome final da última boa já existe (a mesma versão guardada antes) e está preso por outro processo
    raiz = preparar("g8")
    destino = atualizacao.pasta_da_ultima_boa(raiz) / atualizacao.nome_do_pacote("1.2.0")
    destino.write_bytes(b"velho")
    p = segurar_sem_compartilhar(destino, 30)
    try:
        res["G8 destino preso por outro processo"] = guardar(raiz)
    finally:
        p.kill()
        p.wait()

    # G9: desligar no meio da cópia (o processo que guarda morre à força), e a guarda refeita depois
    raiz = preparar("g9")
    codigo = (f"import sys,os;sys.path.insert(0,r'{RAMO}');sys.path.insert(0,r'{RAMO / 'tests'}');"
              f"os.environ['PROGRAMDATA']=r'{os.environ['PROGRAMDATA']}';"
              "import atualizacao;from ajudante_do_atualizador import PUBLICA;"
              f"atualizacao.guardar_ultima_boa(r'{raiz}','1.2.0',atualizacao.Fonte('x'),PUBLICA)")
    # a chave de prova é a do processo que a gerou: no filho ela é outra; a assinatura guardada é desta chave, então
    # o filho a recusaria antes de copiar. Para a cópia acontecer no filho, a chave do filho tem de ser esta:
    chave_txt = R / "chave-de-prova.txt"
    chave_txt.write_text(PUBLICA, encoding="utf-8")
    codigo = codigo.replace("from ajudante_do_atualizador import PUBLICA;",
                            f"PUBLICA=open(r'{chave_txt}').read();")
    filho = subprocess.Popen([sys.executable, "-c", codigo])
    chegando = atualizacao.pasta_da_ultima_boa(raiz) / (atualizacao.nome_do_pacote("1.2.0") + ".chegando")
    for _ in range(400):
        if chegando.exists() and chegando.stat().st_size > 30 * 2**20:
            break
        time.sleep(0.02)
    ctypes.windll.kernel32.TerminateProcess(ctypes.c_void_p(int(filho._handle)), 9)
    filho.wait()
    depois_de_desligar = foto(raiz)
    res["G9 desligar no meio da cópia"] = {"logo depois de morrer": depois_de_desligar,
                                           "a guarda refeita (próxima abertura)": guardar(raiz)}

    # V1: a volta pelo pacote guardado, sem internet, com a biblioteca de verdade
    raiz = nova_instalacao("v1")
    por_a_ultima_boa(raiz, "1.1.0")
    (raiz / "packages" / atualizacao.nome_do_pacote("1.2.0")).write_bytes(PACOTES["1.2.0"])
    res["V1 volta sem internet (Velopack de verdade copia e confere)"] = voltar(raiz)

    # V2: o pacote guardado estragado (cortado)
    raiz = nova_instalacao("v2")
    por_a_ultima_boa(raiz, "1.1.0")
    guardado = atualizacao.pasta_da_ultima_boa(raiz) / atualizacao.nome_do_pacote("1.1.0")
    guardado.write_bytes(PACOTES["1.1.0"][: TAMANHO // 3])
    res["V2 pacote guardado estragado"] = voltar(raiz)

    # V3: a assinatura guardada faltando (apagada)
    raiz = nova_instalacao("v3")
    por_a_ultima_boa(raiz, "1.1.0")
    (atualizacao.pasta_da_ultima_boa(raiz) / assinatura.nome_do_arquivo_da_assinatura(PACOTE, "1.1.0")).unlink()
    res["V3 assinatura guardada faltando: a volta"] = voltar(raiz)
    # ... e o que a ABERTURA faz nesse disco, com a 1.2.0 (que falha no teste) rodando: a regra de verdade
    e, efs = fases.proxima_fase(fases.Estado(), fases.Abriu(True, False, False, True, "1.2.0",
                                                               ultima_boa=atualizacao.ler_ultima_boa(raiz)))
    todos = list(efs)
    e, efs = fases.proxima_fase(e, fases.TesteRapido(False, "código 1"))
    todos += efs
    res["V3 ... a abertura com esse disco (a regra de verdade)"] = {
        "ultima boa lida": atualizacao.ler_ultima_boa(raiz), "efeitos": [repr(x) for x in todos],
        "frase na tela?": any(isinstance(x, (fases.MostrarFalha, fases.GuardarFrase)) for x in todos)}

    texto = json.dumps(res, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_guarda_e_volta-resultado.txt").write_text(texto, encoding="utf-8")
    print(texto)
    shutil.rmtree(R)                                # tudo o que esta prova criou (só os arquivos de 120 MB)


if __name__ == "__main__":
    main()
