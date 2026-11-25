"""Quem tenta quebrar 5 (25/11/2026), M2 (D-870, D-873): o atualizador do Velopack (`Update.exe`) que some, com a
biblioteca `velopack` 1.2.161 DE VERDADE numa instalação de prova minha. Roda pelo `rodar_escondido.py` (o processo
nasce numa área de trabalho separada, com a guarda da tela normal).

Casos (os que o escritor não rodou):
- MEIO: o `Update.exe` está no lugar no clique "Reiniciar agora" e na conferência; some nos segundos entre a
  conferência e o pedido (um antivírus). O pedido vai à biblioteca de verdade, que recusa. O que o programa reaberto
  mostra, e o que acontece ao fechar?
- PALAVRA: a frase da tela, palavra por palavra, contra a D-873.
- DE NOVO: com o `Update.exe` faltando, um segundo "Reiniciar agora" na mesma abertura é possível? (o aviso volta?)
- VOLTA: o `Update.exe` volta; com internet (a fonte de pasta) e sem internet (a fonte some: o pacote esperando).

De verdade: a biblioteca do Velopack (procurar, pendente, baixar e o PEDIDO DA TROCA, `wait_exit_then_apply_updates`,
sempre sem o `Update.exe` no lugar, então ela recusa antes de abrir qualquer programa), a peça
`core.conversa_com_o_velopack` (as mesmas funções, com o localizador da instalação de prova), a regra, o executor, o
disco, as assinaturas (chave de prova), a lista de processos do Windows. De mentira: a caixa do Windows (só anota o
texto; a de verdade está em `prova_caixa.py`), o reabrir do programa, o teste rápido.
O PROGRAMDATA e o LOCALAPPDATA trocados DENTRO do Python e conferidos com assert antes de tudo.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
R = RAMO / "saida_teste" / "qtq5" / "update-exe"
if R.exists():
    shutil.rmtree(R)
(R / "LocalAppData").mkdir(parents=True)
os.environ["PROGRAMDATA"] = str(R / "ProgramData")
os.environ["LOCALAPPDATA"] = str(R / "LocalAppData")
os.environ["USERNAME"] = "Kaique"
sys.path.insert(0, str(RAMO))

import atualizacao  # noqa: E402
import historico  # noqa: E402
import velopack  # noqa: E402
import versao  # noqa: E402
from core import conversa_com_o_velopack as conversa  # noqa: E402
from core import fases_da_atualizacao as fases  # noqa: E402
from core import windows  # noqa: E402
from tests.ajudante_do_atualizador import PUBLICA, WindowsFalso, _publicar, pacote_de_prova  # noqa: E402

assert str(atualizacao.pasta_do_estado()).startswith(str(R)), atualizacao.pasta_do_estado()
assert str(historico.pasta_de_dados()).startswith(str(R)), historico.pasta_de_dados()
assert str(atualizacao.caminho_do_registro()).startswith(str(R))
PACOTE = versao.ID_DO_PACOTE
RAIZ, FONTE, FONTE_FORA = R / "instalado", R / "fonte", R / "fonte-sumiu"
UPD = RAIZ / "Update.exe"
LOC = velopack.VelopackLocatorConfig(RAIZ, UPD, RAIZ / "packages", RAIZ / "current" / "sq.version",
                                     RAIZ / "current", False)
D873 = ("Não deu para atualizar: o atualizador do programa sumiu do computador. O programa continua funcionando. "
        "Avise o Samuel.")


class VelopackDeVerdade:
    """A peça de verdade com o localizador da instalação de prova. No pedido da troca, `some_antes` tira o
    `Update.exe` logo antes (o antivírus nos segundos entre a conferência e o pedido)."""

    def __init__(self, some_antes=False):
        self.pedidos: list[str] = []
        self.some_antes = some_antes

    def procurar(self, endereco):
        self.pedidos.append("procurar")
        return conversa.procurar(endereco, LOC)

    def pendente(self, endereco):
        self.pedidos.append("pendente")
        return conversa.pendente(endereco, LOC)

    def baixar(self, endereco, v):
        self.pedidos.append("baixar")
        return conversa.baixar(endereco, v, LOC)

    def pacote_da_versao(self, *a):
        return conversa.pacote_da_versao(*a)

    def trocar(self, endereco, v, reabrir, argumentos):
        if self.some_antes and UPD.exists():
            UPD.unlink()
        assert not UPD.exists(), "segurança da prova: a troca de verdade só é pedida sem o Update.exe"
        self.pedidos.append("trocar (à biblioteca de verdade)")
        try:  # o mesmo pedido da peça (conversa.trocar), com o localizador da instalação de prova
            conversa._gerente(endereco, LOC).wait_exit_then_apply_updates(
                v.pedido, silent=False, restart=bool(reabrir), restart_args=[str(a) for a in argumentos])
        except Exception as erro:  # noqa: BLE001
            self.pedidos.append(f"a biblioteca recusou: {type(erro).__name__}: {str(erro)[:140]}")
            raise conversa.ErroDoVelopack(f"trocar para a {v.versao}: {erro}") from erro
        self.pedidos.append("A BIBLIOTECA ACEITOU (não devia)")


class WindowsMeio(WindowsFalso):
    programas_rodando_de = staticmethod(windows.programas_rodando_de)
    numero_deste_processo = staticmethod(windows.numero_deste_processo)
    atualizador_do_velopack_rodando = staticmethod(windows.atualizador_do_velopack_rodando)

    def __init__(self):
        super().__init__(pasta_de_troca=R / "troca")
        self.caixas: list[str] = []
        self.reaberturas = 0

    def mostrar_caixa_do_windows(self, titulo, texto):
        self.caixas.append(f"[{titulo}] {texto}")
        return windows.Resposta(windows.DEU_CERTO)

    def lancar_solto(self, comando, sinal, espera_s=30):
        self.reaberturas += 1
        return windows.Resposta(windows.DEU_CERTO)


def pacote_com_manifesto(v: str) -> bytes:
    """O pacote de prova que o Velopack de verdade reconhece (o .nuspec dentro, como o vpk põe) e com o
    motor-exigido.json (como o publicar põe). Copiado de `quem-tenta-quebrar-4/provas/prova_pacote_esperando.py`:
    sem o manifesto, o "pacote esperando" da biblioteca não o vê (a primeira rodada desta prova errou nisso)."""
    import io
    import zipfile

    dados = io.BytesIO()
    with zipfile.ZipFile(dados, "w") as z:
        z.writestr(f"{PACOTE}.nuspec", f'<?xml version="1.0"?><package><metadata><id>{PACOTE}</id><version>{v}'
                   '</version><title>E</title><authors>x</authors><description>x</description>'
                   '<mainExe>EditorImpressao.exe</mainExe></metadata></package>')
        z.writestr("lib/app/motor-exigido.json", json.dumps({"versao": 1}))
    return dados.getvalue()


def abertura(fonte=FONTE, some_antes=False):
    win, vp = WindowsMeio(), VelopackDeVerdade(some_antes)
    a = atualizacao.Atualizacao(windows=win, velopack=vp, raiz=RAIZ, fonte=atualizacao.Fonte(str(fonte)),
                                por_tras=lambda t: t(), pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                motor_no_lugar=lambda m=None: True, teste=lambda: (True, ""), chave_publica=PUBLICA)
    a.abrir([])
    tela: list = []
    a.ligar_a_tela(tela.append)
    return a, win, vp, tela


def texto(ef) -> str:
    if isinstance(ef, fases.MostrarFalha):
        return "[Atualização] " + atualizacao.frase_da_falha(ef.tipo, ef.motivo_da_tela)
    return type(ef).__name__


def main() -> None:
    res: dict = {}
    (RAIZ / "current").mkdir(parents=True)
    (RAIZ / "packages").mkdir()
    (RAIZ / "current" / "sq.version").write_text(
        f'<?xml version="1.0"?><package><metadata><id>{PACOTE}</id><version>1.1.0</version><title>E</title>'
        '<authors>x</authors><description>x</description><mainExe>EditorImpressao.exe</mainExe></metadata>'
        '</package>', encoding="utf-8")
    UPD.write_bytes(b"MZ")
    c11, c12 = pacote_com_manifesto("1.1.0"), pacote_com_manifesto("1.2.0")
    _publicar(FONTE, "1.1.0", c11)
    _publicar(FONTE, "1.2.0", c12)
    for v, c in (("1.1.0", c11), ("1.2.0", c12)):
        (FONTE / atualizacao.nome_do_pacote(v)).write_bytes(c)
    indice = json.loads((FONTE / "releases.win.json").read_text(encoding="utf-8"))
    for item in indice["Assets"]:
        item["SHA1"] = hashlib.sha1((FONTE / item["FileName"]).read_bytes()).hexdigest()
    (FONTE / "releases.win.json").write_text(json.dumps(indice), encoding="utf-8")
    versao.VERSAO = "1.1.0"

    # MEIO
    a, win, vp, tela = abertura(some_antes=True)
    res["MEIO 1. a abertura (o Update.exe no lugar)"] = {"tela": [texto(e) for e in tela], "pedidos": vp.pedidos}
    tela.clear()
    a.evento(fases.Escolheu(True))
    res["MEIO 2. Reiniciar agora: a conferência"] = {"tela": [texto(e) for e in tela], "fase": a.estado.fase.value,
                                                     "Update.exe no lugar": UPD.exists()}
    a.evento(fases.JanelaFechou(True))                 # a janela fechou (o trabalho gravado); o pedido vai
    res["MEIO 3. o pedido da troca (o Update.exe some logo antes)"] = {
        "pedidos": vp.pedidos, "fase": a.estado.fase.value, "reaberto": win.reaberturas,
        "bilhete": atualizacao.ler_estado()}
    b, win_b, vp_b, tela_b = abertura()
    caixa_b = list(win_b.caixas)
    b.evento(fases.Fechando())
    res["MEIO 4. o programa reaberto"] = {"caixas do Windows (antes da janela)": caixa_b,
                                          "na janela": [texto(e) for e in tela_b], "pedidos": vp_b.pedidos,
                                          "fechar perguntou?": "PerguntarAoFechar" in [texto(e) for e in tela_b]}
    res["PALAVRA a frase igual à D-873"] = bool(caixa_b) and caixa_b[0] == f"[Atualização] {D873}"

    # DE NOVO: o Update.exe volta, o aviso; some de novo; dois cliques seguidos na mesma abertura
    UPD.write_bytes(b"MZ")
    c, win_c, vp_c, tela_c = abertura()
    UPD.unlink()
    antes = [texto(e) for e in tela_c]
    tela_c.clear()
    c.evento(fases.Escolheu(True))
    primeiro = [texto(e) for e in tela_c]
    tela_c.clear()
    c.evento(fases.Escolheu(True))                     # o aviso não está mais na tela; um clique fora de hora
    c.evento(fases.Fechando())
    res["DE NOVO"] = {"a abertura com ele de volta": antes, "Reiniciar agora sem ele": primeiro,
                      "fase": c.estado.fase.value, "depois (um clique a mais e fechar)": [texto(e) for e in tela_c]}

    # VOLTA, sem internet: a fonte some; o pacote 1.2.0 já está em packages (baixado na abertura MEIO)
    UPD.write_bytes(b"MZ")
    d, win_d, vp_d, tela_d = abertura(fonte=FONTE_FORA)
    res["VOLTA sem internet (o pacote esperando)"] = {"tela": [texto(e) for e in tela_d], "pedidos": vp_d.pedidos,
                                                      "caixas": win_d.caixas}
    res["o registro (as últimas linhas)"] = atualizacao.caminho_do_registro().read_text(
        encoding="utf-8").splitlines()[-16:]
    t = json.dumps(res, ensure_ascii=False, indent=1, default=str)
    Path(__file__).with_name("prova_update_exe-resultado.txt").write_text(t, encoding="utf-8")


if __name__ == "__main__":
    main()
