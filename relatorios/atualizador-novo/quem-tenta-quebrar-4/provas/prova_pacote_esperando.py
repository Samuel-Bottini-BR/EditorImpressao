"""Quem tenta quebrar 4 (24/11/2026): sem internet, com a versão nova já baixada (D-859). EXECUTADO com a biblioteca
do Velopack de verdade.

Pergunta: o Kaique disse "Não" ao fechar (a 1.2.0 ficou em packages\\). Na abertura seguinte não há internet. O aviso
volta? A pergunta ao fechar vem? E com o GitHub de verdade inalcançável (um proxy que não existe, só neste processo),
a assinatura é "recusada" (a frase 2) ou "sem rede" (nada)?

De verdade: a biblioteca `velopack` 1.2.161 (`get_update_pending_restart`, `check_for_updates`, `download_updates`
com o arquivo já no lugar), a peça `core.conversa_com_o_velopack`, a regra, o executor, o disco, as assinaturas (chave
de prova); a falta de internet (para a fonte de pasta: a pasta não existe; para o GitHub: um proxy que não existe, só
neste processo). De mentira: a lista de processos (nenhuma outra janela), o teste rápido. O PROGRAMDATA e o LOCALAPPDATA
trocados DENTRO do Python e conferidos.
Uso: python prova_pacote_esperando.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
R = RAMO / "saida_teste" / "qtq4" / "pacote-esperando"
if R.exists():
    shutil.rmtree(R)
(R / "LocalAppData").mkdir(parents=True)
os.environ["PROGRAMDATA"] = str(R / "ProgramData")
os.environ["LOCALAPPDATA"] = str(R / "LocalAppData")
os.environ["USERNAME"] = "Kaique"
sys.path.insert(0, str(RAMO))

import atualizacao  # noqa: E402
import velopack  # noqa: E402
import versao  # noqa: E402
from core import conversa_com_o_velopack as conversa  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402
from tests.ajudante_do_atualizador import PUBLICA, WindowsFalso, _publicar, pacote_de_prova  # noqa: E402

assert str(atualizacao.pasta_do_estado()).startswith(str(R))
PACOTE = versao.ID_DO_PACOTE
RAIZ, FONTE = R / "instalado", R / "fonte"
LOC = velopack.VelopackLocatorConfig(RAIZ, RAIZ / "Update.exe", RAIZ / "packages", RAIZ / "current" / "sq.version",
                                     RAIZ / "current", False)


class VelopackDeVerdade:
    def procurar(self, endereco):
        return conversa.procurar(endereco, LOC)

    def pendente(self, endereco):
        return conversa.pendente(endereco, LOC)

    def baixar(self, endereco, v):
        return conversa.baixar(endereco, v, LOC)

    def pacote_da_versao(self, *a):
        return conversa.pacote_da_versao(*a)

    def trocar(self, endereco, v, reabrir, argumentos):
        self.trocou = (v.versao, list(argumentos))      # a troca de verdade está nas provas da volta 4


def pacote_com_manifesto(v: str) -> bytes:
    """Um pacote de prova que o Velopack de verdade reconhece (o manifesto .nuspec dentro, como o vpk põe) e com o
    motor-exigido.json (como o nosso publicar põe)."""
    import io
    import zipfile

    dados = io.BytesIO()
    with zipfile.ZipFile(dados, "w") as z:
        z.writestr(f"{PACOTE}.nuspec", f'<?xml version="1.0"?><package><metadata><id>{PACOTE}</id><version>{v}'
                   '</version><title>E</title><authors>x</authors><description>x</description>'
                   '<mainExe>EditorImpressao.exe</mainExe></metadata></package>')
        z.writestr("lib/app/motor-exigido.json", json.dumps({"versao": 1}))
    return dados.getvalue()


def executor(fonte: str) -> tuple[atualizacao.Atualizacao, VelopackDeVerdade]:
    vp = VelopackDeVerdade()
    w = WindowsFalso()
    w._pasta_de_troca = R / "troca"
    return atualizacao.Atualizacao(windows=w, velopack=vp, raiz=RAIZ, fonte=atualizacao.Fonte(fonte),
                                   por_tras=lambda t: t(), pasta_grava=lambda r: True,
                                   garantir_motor=lambda: True, motor_no_lugar=lambda m=None: True,
                                   teste=lambda: (True, ""), chave_publica=PUBLICA), vp


def texto(ef) -> str:
    if isinstance(ef, fases.MostrarFalha):
        return "[Atualização] " + atualizacao.frase_da_falha(ef.tipo, ef.motivo_da_tela)
    return type(ef).__name__


def uma_abertura(fonte: str, nome: str, resultado: dict) -> None:
    a, vp = executor(fonte)
    a.abrir([])
    tela: list = []
    a.ligar_a_tela(tela.append)
    if a.estado.fase is fases.Fase.PRONTA:
        a.evento(fases.Escolheu(False))
    a.evento(fases.Fechando())
    pergunta = a.estado.fase is fases.Fase.PERGUNTANDO
    if pergunta:
        a.evento(fases.RespondeuAoFechar(True))
    resultado[nome] = {"tela": [texto(e) for e in tela], "a pergunta ao fechar veio": pergunta,
                       "o Sim pediu a troca": getattr(vp, "trocou", None),
                       "registro (fim)": atualizacao.caminho_do_registro().read_text(encoding="utf-8").splitlines()[-4:]}


def main() -> None:
    resultado: dict = {}
    (RAIZ / "current").mkdir(parents=True)
    (RAIZ / "packages").mkdir()
    (RAIZ / "current" / "sq.version").write_text(
        f'<?xml version="1.0"?><package><metadata><id>{PACOTE}</id><version>1.1.0</version><title>E</title>'
        '<authors>x</authors><description>x</description><mainExe>EditorImpressao.exe</mainExe></metadata>'
        '</package>', encoding="utf-8")
    (RAIZ / "Update.exe").write_bytes(b"MZ")
    c12 = pacote_com_manifesto("1.2.0")
    _publicar(FONTE, "1.2.0", c12)
    (FONTE / atualizacao.nome_do_pacote("1.2.0")).write_bytes(c12)
    indice = json.loads((FONTE / "releases.win.json").read_text(encoding="utf-8"))
    for item in indice["Assets"]:
        item["SHA1"] = hashlib.sha1((FONTE / item["FileName"]).read_bytes()).hexdigest()
    (FONTE / "releases.win.json").write_text(json.dumps(indice), encoding="utf-8")
    versao.VERSAO = "1.1.0"
    # 1. Com "internet" (a pasta da fonte existe): acha, confere (guarda a assinatura que chega), baixa; "Não" ao fechar.
    a, vp = executor(str(FONTE))
    a.abrir([])
    a.ligar_a_tela(lambda e: None)
    a.evento(fases.Escolheu(False))
    a.evento(fases.Fechando())
    a.evento(fases.RespondeuAoFechar(False))
    resultado["1. com a fonte: baixou, Não ao fechar"] = {
        "packages": sorted(p.name for p in (RAIZ / "packages").iterdir()),
        "ultima-boa": sorted(p.name for p in atualizacao.pasta_da_ultima_boa(RAIZ).iterdir()),
        "pendente pelo Velopack de verdade": conversa.pendente(str(FONTE), LOC)}
    # 2. Sem internet: a fonte some (a pasta muda de nome).
    FONTE.rename(R / "fonte-longe")
    uma_abertura(str(FONTE), "2. sem a fonte (sem internet), com a 1.2.0 esperando", resultado)
    # 3. O GitHub de verdade inalcançável (proxy que não existe, só neste processo): a assinatura de uma versão.
    os.environ["HTTPS_PROXY"] = os.environ["HTTP_PROXY"] = "http://127.0.0.1:9"
    try:
        atualizacao.Fonte.padrao().ler("1.0.0", "x.assinatura")
        resultado["3. GitHub sem internet: Fonte.ler"] = "leu (não devia)"
    except FileNotFoundError as erro:
        resultado["3. GitHub sem internet: Fonte.ler"] = f"FileNotFoundError (seria a frase 2): {erro}"
    except OSError as erro:
        resultado["3. GitHub sem internet: Fonte.ler"] = f"{type(erro).__name__} (sem rede, nada na tela): {erro}"
    t = json.dumps(resultado, ensure_ascii=False, indent=1, default=str)
    Path(__file__).with_name("prova_pacote_esperando-resultado.txt").write_text(t, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(t)


if __name__ == "__main__":
    main()
