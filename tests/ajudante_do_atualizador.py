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

    def __init__(self, licenca: str = "disse_nao", depois_do_sim=None, outras=None, troca_em_curso=False,
                 pasta_de_troca: Path | None = None):
        self.licenca, self.depois_do_sim, self.outras = licenca, depois_do_sim, [] if outras is None else outras
        self.troca_em_curso = troca_em_curso        # o que "o atualizador do Velopack está rodando?" responde
        self.pedidos: list[list[str]] = []
        self.perguntas_de_processos: list = []
        self.reaberturas: list[list[str]] = []
        self.perguntas_do_atualizador: list[Path] = []
        self.reabrir_da_certo = True
        self._pasta_de_troca = pasta_de_troca

    def atualizador_do_velopack_rodando(self, raiz):
        self.perguntas_do_atualizador.append(Path(raiz))
        return self.troca_em_curso

    caminho_conferido = staticmethod(windows.caminho_conferido)      # a leitura de verdade (volta 3, M7)

    def criar_pasta_de_troca(self):
        self._pasta_de_troca.mkdir(parents=True, exist_ok=True)
        return self._pasta_de_troca

    def apagar_pasta_de_troca(self, pasta):
        return True

    def lancar_solto(self, comando, sinal, espera_s=30):
        self.reaberturas.append([str(c) for c in comando])
        return windows.Resposta(windows.DEU_CERTO if self.reabrir_da_certo else windows.FALHOU, "sem sinal de vida")

    def comecar_pedido_de_licenca(self, passos):
        self.pedidos.append([p.tipo for p in passos])
        return PedidoFalso(self.licenca, self.depois_do_sim)

    def programas_rodando_de(self, pasta, menos_a_familia_de=None, nomes=None):
        self.perguntas_de_processos.append((Path(pasta), menos_a_familia_de))
        return self.outras

    def numero_deste_processo(self):
        return 4242


class VelopackFalso:
    """A peça do Velopack de mentira: anota cada chamada; `baixar` põe o pacote em <raiz>\\packages, como o Velopack."""

    def __init__(self, raiz: Path, publicada=None, erro_ao_procurar: str = "", conteudo: dict | None = None,
                 pendente: str = ""):
        self.raiz, self.publicada, self.erro = raiz, publicada, erro_ao_procurar
        self.conteudo = conteudo or {}
        self.chamadas: list[tuple] = []
        self.versao_pendente = pendente
        self.leituras: list[tuple] = []
        self.trocar_levanta: Exception | None = None

    def procurar(self, endereco):
        self.chamadas.append(("procurar",))
        if self.erro:
            raise conversa.ErroDoVelopack(self.erro)
        return self.publicada

    def pendente(self, endereco):
        """Só lê (o pacote esperando): anotado em `leituras`, não em `chamadas` (que são os pedidos que mudam algo)."""
        self.leituras.append(("pendente",))
        return self.versao_pendente

    def baixar(self, endereco, v):
        """Como o Velopack: se o arquivo já está em `packages`, nada (manager.rs 413-416); com uma PASTA de endereço
        (a fonte de pasta, a volta pela última boa), copia de lá e confere tamanho e soma (sources/file.rs, manager.rs
        537-561); senão "baixa" o conteúdo publicado."""
        self.chamadas.append(("baixar", v.versao, str(endereco)))
        destino = self.raiz / "packages" / v.arquivo
        destino.parent.mkdir(parents=True, exist_ok=True)
        if destino.exists():
            return
        local = Path(str(endereco)) / v.arquivo
        if local.is_file():
            dados = local.read_bytes()
            if len(dados) != v.tamanho or hashlib.sha256(dados).hexdigest() != v.sha256.lower():
                raise conversa.ErroDoVelopack("o pacote da pasta não confere (tamanho ou soma)")
            destino.write_bytes(dados)
            return
        if not str(endereco).startswith("http") and not Path(str(endereco)).is_dir():
            raise conversa.ErroDoVelopack("a fonte não está acessível (como sem internet)")    # volta 3
        destino.write_bytes(self.conteudo[v.versao])

    def pacote_da_versao(self, pacote, v, arquivo, sha256, sha1, tamanho):
        self.chamadas.append(("pacote_da_versao", v))
        return conversa.VersaoDoVelopack(pacote, v, arquivo, sha256, tamanho)

    def trocar(self, endereco, v, reabrir, argumentos):
        self.chamadas.append(("trocar", v.versao, reabrir, tuple(argumentos)))
        if self.trocar_levanta is not None:
            raise self.trocar_levanta

    def nomes(self):
        return [c[0] for c in self.chamadas]


# ---------------------------------------------------------------------------------------------------------------------
# A montagem de cada prova
# ---------------------------------------------------------------------------------------------------------------------

def pacote_de_prova(texto: str, motor: int | None = 1) -> bytes:
    """Um pacote (.nupkg) de prova: um zip com o `motor-exigido.json` dentro (o motor que a versão pede), como o
    publicar põe (volta 2, M2). `motor=None`: sem o arquivo."""
    import io
    import zipfile

    dados = io.BytesIO()
    with zipfile.ZipFile(dados, "w") as z:
        z.writestr("lib/app/leia.txt", texto)
        if motor is not None:
            z.writestr(getattr(atualizacao, "CAMINHO_DO_MOTOR_EXIGIDO_NO_PACOTE", "lib/app/motor-exigido.json"),
                       json.dumps({"versao": motor}))
    return dados.getvalue()


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
                 erro_ao_procurar: str = "", motores: dict | None = None, motores_no_lugar: set | None = None,
                 troca_em_curso=False, ultima_boa: str | None = None, pendente: str = ""):
        """`motores`: o motor que cada versão pede (padrão: 1 nas duas). `motores_no_lugar`: os motores que estão no
        lugar (padrão: todos, ou nenhum com `motor=False`). `troca_em_curso`: o que a peça responde sobre o
        atualizador do Velopack. `ultima_boa` (volta 3): a versão (ANTERIOR ou a ATUAL) cujo pacote e assinatura já
        estão guardados em `<raiz>/ultima-boa` (None = nenhuma). `pendente`: o que o Velopack diz que está esperando."""
        self.raiz, self.fonte_pasta = tmp / "raiz", tmp / "fonte"
        (self.raiz / "current").mkdir(parents=True)
        self.grava = {"agora": grava}
        self.motor = {"no_lugar": motor}
        motores = {NOVA: 1, ANTERIOR: 1, **(motores or {})}
        self.motores_no_lugar = motores_no_lugar
        conteudos = {NOVA: pacote_de_prova("pacote da versao nova", motores[NOVA]),
                     ANTERIOR: pacote_de_prova("pacote da versao anterior", motores[ANTERIOR])}
        nova = _publicar(self.fonte_pasta, NOVA, conteudos[NOVA], chave_da_nova) if publicar_nova else None
        _publicar(self.fonte_pasta, ANTERIOR, conteudos[ANTERIOR])
        self.win = WindowsFalso(licenca, depois_do_sim=lambda: self.grava.update(agora=True), outras=outras,
                                troca_em_curso=troca_em_curso, pasta_de_troca=tmp / "troca")
        self.vp = VelopackFalso(self.raiz, nova, erro_ao_procurar, conteudos, pendente)
        self.conteudos = conteudos
        if ultima_boa is not None:
            self.guardar(ultima_boa)
        self.tela: list = []
        self.atual = atualizacao.Atualizacao(
            windows=self.win, velopack=self.vp, raiz=self.raiz, fonte=atualizacao.Fonte(str(self.fonte_pasta)),
            por_tras=lambda trabalho: trabalho(), pasta_grava=lambda raiz: self.grava["agora"],
            garantir_motor=lambda: self.motor["no_lugar"], motor_no_lugar=self._motor_no_lugar,
            teste=lambda: teste, chave_publica=PUBLICA)

    def conteudo_de(self, v: str) -> bytes:
        """O pacote de prova de uma versão (a ATUAL ganha um, se ainda não tem)."""
        if v not in self.conteudos:
            self.conteudos[v] = pacote_de_prova(f"pacote da versao {v}")
            _publicar(self.fonte_pasta, v, self.conteudos[v])
        return self.conteudos[v]

    def guardar(self, v: str) -> Path:
        """Põe em `<raiz>/ultima-boa` o pacote e a assinatura da versão `v`, como `guardar_ultima_boa` deixa."""
        pasta = atualizacao.pasta_da_ultima_boa(self.raiz)
        pasta.mkdir(parents=True, exist_ok=True)
        conteudo = self.conteudo_de(v)
        (pasta / atualizacao.nome_do_pacote(v)).write_bytes(conteudo)
        nome = assinatura.nome_do_arquivo_da_assinatura(PACOTE, v)
        (pasta / nome).write_bytes((self.fonte_pasta / nome).read_bytes())
        return pasta

    def pacote_em_packages(self, v: str) -> Path:
        """Põe o pacote da versão `v` em `<raiz>/packages`, como o Velopack deixa o da versão que roda."""
        destino = self.raiz / "packages" / atualizacao.nome_do_pacote(v)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(self.conteudo_de(v))
        return destino

    def _motor_no_lugar(self, versao_do_motor=None):
        if self.motores_no_lugar is not None:
            return versao_do_motor in self.motores_no_lugar
        return self.motor["no_lugar"]

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
    """O estado.json e o registro vão para uma pasta de prova; a conta não é a de testes. Volta 3: a pasta de dados da
    conta também é desta prova (as frases "já vistas" moram lá); sem isso, uma frase mostrada num teste ficava "vista"
    para o teste seguinte da mesma rodada, e o resultado dependia da ordem dos arquivos (achado ao rodar as mutações
    com todos os arquivos juntos)."""
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "LocalAppData"))
    monkeypatch.setenv("USERNAME", "Kaique")



def _ate_o_aviso(tmp_path, **kw) -> Prova:
    p = Prova(tmp_path, **kw)
    p.abrir()
    p.ligar_a_tela()
    assert p.tipos_na_tela() == ["MostrarVersaoNova"]
    return p
