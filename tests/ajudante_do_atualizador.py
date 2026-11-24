"""As peças de mentira e a montagem das provas do atualizador novo (23/11/2026), num lugar só para os arquivos de teste
que as usam (`tests/test_atualizador_novo.py` e as provas antigas adaptadas pela D-836).

O que é de mentira (D-767): só a borda. `WindowsFalso` (a pergunta do Windows e a lista de processos) e `VelopackFalso`
(procurar, baixar, trocar) só ANOTAM o que lhes pediram e devolvem o que a prova manda. A regra, o executor, o disco
(numa pasta de prova), as assinaturas (com uma chave de prova) e as somas são os de verdade. `Prova` monta uma abertura
do programa instalado numa pasta de prova. Quem usa precisa trocar o PROGRAMDATA por uma pasta de prova (a fixture
`programdata_de_prova` daqui, que cada arquivo liga com `autouse`).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import assinatura
import atualizacao
import versao
from core import conversa_com_o_velopack as conversa
from core import fases_da_atualizacao as fases
from core import windows

RAIZ_DO_REPOSITORIO = Path(__file__).resolve().parent.parent
PACOTE = versao.ID_DO_PACOTE
ATUAL = versao.VERSAO              # a versão que "roda" (a do versao.py)
NOVA = "9.9.0"
ANTERIOR = "0.1.0"
CHAVE = assinatura.nova_chave_privada()
PUBLICA = assinatura.secret_to_public(CHAVE).hex()
OUTRA_CHAVE = assinatura.nova_chave_privada()


# ---------------------------------------------------------------------------------------------------------------------
# As peças de mentira (só a borda)
# ---------------------------------------------------------------------------------------------------------------------

class PedidoFalso:
    """O que `windows.comecar_pedido_de_licenca` devolve: "comecou" (disse Sim) ou a resposta da pergunta."""

    def __init__(self, desfecho: str, depois=None):
        self.comecou = desfecho == "comecou"
        self.resposta_da_pergunta = None if self.comecou else windows.Resposta(
            windows.DISSE_NAO if desfecho == "disse_nao" else windows.FALHOU, "motivo de prova")
        self._depois = depois

    def esperar(self):
        if self._depois:
            self._depois()
        return windows.Resposta(windows.DEU_CERTO)


class WindowsFalso:
    """A peça do Windows de mentira: anota os pedidos; `outras` é o que a lista de processos responde."""

    DISSE_NAO = windows.DISSE_NAO

    def __init__(self, licenca: str = "disse_nao", depois_do_sim=None, outras=None):
        self.licenca, self.depois_do_sim, self.outras = licenca, depois_do_sim, [] if outras is None else outras
        self.pedidos: list[list[str]] = []
        self.perguntas_de_processos: list = []

    def comecar_pedido_de_licenca(self, passos):
        self.pedidos.append([p.tipo for p in passos])
        return PedidoFalso(self.licenca, self.depois_do_sim)

    def programas_rodando_de(self, pasta, menos_a_familia_de=None):
        self.perguntas_de_processos.append((Path(pasta), menos_a_familia_de))
        return self.outras

    def numero_deste_processo(self):
        return 4242


class VelopackFalso:
    """A peça do Velopack de mentira: anota cada chamada; `baixar` põe o pacote em <raiz>\\packages, como o Velopack."""

    def __init__(self, raiz: Path, publicada=None, erro_ao_procurar: str = "", conteudo: dict | None = None):
        self.raiz, self.publicada, self.erro = raiz, publicada, erro_ao_procurar
        self.conteudo = conteudo or {}
        self.chamadas: list[tuple] = []

    def procurar(self, endereco):
        self.chamadas.append(("procurar",))
        if self.erro:
            raise conversa.ErroDoVelopack(self.erro)
        return self.publicada

    def baixar(self, endereco, v):
        self.chamadas.append(("baixar", v.versao))
        destino = self.raiz / "packages" / v.arquivo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(self.conteudo[v.versao])

    def pacote_da_versao(self, pacote, v, arquivo, sha256, sha1, tamanho):
        self.chamadas.append(("pacote_da_versao", v))
        return conversa.VersaoDoVelopack(pacote, v, arquivo, sha256, tamanho)

    def trocar(self, endereco, v, reabrir, argumentos):
        self.chamadas.append(("trocar", v.versao, reabrir, tuple(argumentos)))

    def nomes(self):
        return [c[0] for c in self.chamadas]


# ---------------------------------------------------------------------------------------------------------------------
# A montagem de cada prova
# ---------------------------------------------------------------------------------------------------------------------

def _publicar(fonte: Path, v: str, conteudo: bytes, chave: bytes = CHAVE) -> conversa.VersaoDoVelopack:
    """Põe na pasta da fonte a assinatura (com `chave`) e o índice de uma versão; devolve o que o Velopack acharia."""
    nome = f"{PACOTE}-{v}-full.nupkg"
    sha = hashlib.sha256(conteudo).hexdigest()
    fonte.mkdir(parents=True, exist_ok=True)
    (fonte / assinatura.nome_do_arquivo_da_assinatura(PACOTE, v)).write_text(
        assinatura.escrever_assinatura(chave, assinatura.VersaoAssinada(PACOTE, v, nome, sha)), encoding="utf-8")
    indice = fonte / atualizacao.NOME_DO_INDICE_PUBLICADO
    lido = json.loads(indice.read_text(encoding="utf-8")) if indice.exists() else {"Assets": []}
    lido["Assets"].append({"PackageId": PACOTE, "Version": v, "Type": "Full", "FileName": nome, "SHA1": "",
                           "SHA256": sha, "Size": len(conteudo)})
    indice.write_text(json.dumps(lido), encoding="utf-8")
    return conversa.VersaoDoVelopack(PACOTE, v, nome, sha, len(conteudo))


class Prova:
    """Uma abertura do programa instalado, numa pasta de prova (a raiz da instalação, a fonte, o ProgramData)."""

    def __init__(self, tmp: Path, *, grava: bool = True, licenca: str = "disse_nao", motor: bool = True,
                 teste=(True, ""), outras=None, chave_da_nova: bytes = CHAVE, publicar_nova: bool = True,
                 erro_ao_procurar: str = ""):
        self.raiz, self.fonte_pasta = tmp / "raiz", tmp / "fonte"
        (self.raiz / "current").mkdir(parents=True)
        self.grava = {"agora": grava}
        self.motor = {"no_lugar": motor}
        conteudos = {NOVA: b"pacote da versao nova", ANTERIOR: b"pacote da versao anterior"}
        nova = _publicar(self.fonte_pasta, NOVA, conteudos[NOVA], chave_da_nova) if publicar_nova else None
        _publicar(self.fonte_pasta, ANTERIOR, conteudos[ANTERIOR])
        self.win = WindowsFalso(licenca, depois_do_sim=lambda: self.grava.update(agora=True), outras=outras)
        self.vp = VelopackFalso(self.raiz, nova, erro_ao_procurar, conteudos)
        self.tela: list = []
        self.atual = atualizacao.Atualizacao(
            windows=self.win, velopack=self.vp, raiz=self.raiz, fonte=atualizacao.Fonte(str(self.fonte_pasta)),
            por_tras=lambda trabalho: trabalho(), pasta_grava=lambda raiz: self.grava["agora"],
            garantir_motor=lambda: self.motor["no_lugar"], motor_no_lugar=lambda: self.motor["no_lugar"],
            teste=lambda: teste, chave_publica=PUBLICA)

    def abrir(self, *argumentos: str):
        saida = self.atual.abrir(list(argumentos))
        return saida

    def ligar_a_tela(self):
        self.atual.ligar_a_tela(self.tela.append)

    def tipos_na_tela(self):
        return [type(e).__name__ for e in self.tela]


def _estado() -> dict:
    return atualizacao.ler_estado()


def _registro() -> str:
    try:
        return atualizacao.caminho_do_registro().read_text(encoding="utf-8")
    except OSError:
        return ""



@pytest.fixture
def programdata_de_prova(tmp_path, monkeypatch):
    """O estado.json e o registro vão para uma pasta de prova; a conta não é a de testes."""
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setenv("USERNAME", "Kaique")



def _ate_o_aviso(tmp_path, **kw) -> Prova:
    p = Prova(tmp_path, **kw)
    p.abrir()
    p.ligar_a_tela()
    assert p.tipos_na_tela() == ["MostrarVersaoNova"]
    return p
