"""O executor do atualizador novo (atualizacao.py, 23/11/2026, D-830) pelos caminhos de verdade, com as duas peças de
fora de mentira SÓ NA BORDA.

O que é de mentira aqui (e por quê, D-767): a peça do Windows (`WindowsFalso`: a pergunta do Windows, a lista de
processos) e a peça do Velopack (`VelopackFalso`: procurar, baixar, trocar). Cada uma só ANOTA o que lhe pediram e
devolve o que o teste manda. Todo o resto é o de verdade: a regra (`core/fases_da_atualizacao.py`), o executor, o
`estado.json` e o registro no disco (numa pasta de prova), as assinaturas (com uma chave de prova, pela conferência
única `assinatura.conferir_versao`), a soma do pacote baixado, os textos da tela. O que mexe no Windows de verdade só
conta como pronto na prova à vista com o Samuel (ONDE-PAREI, "O que ficou para a prova à vista").

As proteções do plano (seção 11), uma prova cada, que FALHA quando a proteção é desligada (o nome diz qual):
(1) sem licença não procura; (2) a assinatura antes de baixar; (3) a soma do arquivo baixado antes de trocar; (4) o
motor antes de anunciar e antes de trocar; (5) a licença é o último passo; (6) o ajudante antigo sai antes da licença;
(7) a conta de testes não procura nem pergunta; (8) a versão que falhou não é tentada de novo; (9) outra janela aberta
não troca; (10) a troca só depois de a janela fechar; (11) a volta só com pacote assinado; (12) pelo código nada roda;
(13) só `trocar_para` chama a troca do Velopack.
"""

from __future__ import annotations

import ast
import json
import sys
import warnings
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
    sha = __import__("hashlib").sha256(conteudo).hexdigest()
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


@pytest.fixture(autouse=True)
def _programdata_de_prova(tmp_path, monkeypatch):
    """O estado.json e o registro vão para uma pasta de prova; a conta não é a de testes."""
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setenv("USERNAME", "Kaique")


def _estado() -> dict:
    return atualizacao.ler_estado()


def _registro() -> str:
    try:
        return atualizacao.caminho_do_registro().read_text(encoding="utf-8")
    except OSError:
        return ""


# ---------------------------------------------------------------------------------------------------------------------
# A primeira abertura e a pergunta do Windows
# ---------------------------------------------------------------------------------------------------------------------

def test_protecao_1_sem_licenca_pergunta_ao_windows_e_nao_procura(tmp_path):
    """D-735/D-741/D-806/D-834: a pasta do programa não aceita gravação → a pergunta do Windows é feita DENTRO da
    abertura (antes de `abrir` voltar, isto é, antes do brasão e da janela, que o main.py só abre depois), e com o
    "Não" nada é procurado nem baixado. Desligar a proteção (procurar sem a licença) faria `procurar` aparecer."""
    p = Prova(tmp_path, grava=False, licenca="disse_nao")
    assert p.abrir() is None
    assert p.win.pedidos == [["apagar_tarefa", "instalar_visual_c", "tirar_instalacao_do_inno",
                              "dar_licenca_aos_usuarios"]]
    assert p.vp.chamadas == []
    assert p.atual.estado.fase is fases.Fase.PARADO
    assert "disse Não" in _registro()


def test_d741_depois_do_nao_a_pergunta_volta_na_proxima_abertura(tmp_path):
    """D-741 ("Sim": a pergunta volta a cada abertura até o "Sim"): duas aberturas com a pasta sem a licença, duas
    perguntas. Nada é anotado como "preparado": o que vale é o teste de gravar de cada abertura."""
    p = Prova(tmp_path, grava=False, licenca="disse_nao")
    p.abrir()
    p.atual = atualizacao.Atualizacao(windows=p.win, velopack=p.vp, raiz=p.raiz,
                                      fonte=atualizacao.Fonte(str(p.fonte_pasta)), por_tras=lambda t: t(),
                                      pasta_grava=lambda r: False, chave_publica=PUBLICA)
    p.abrir()
    assert len(p.win.pedidos) == 2


def test_d749_sim_com_a_pasta_ainda_sem_gravar_conta_como_nao_feito(tmp_path):
    """D-749 ("Sim": a preparação pela metade conta como não feita): disse Sim, o trabalho com licença terminou, mas
    a pasta continua sem aceitar gravação (um passo falhou) → nada é procurado; a próxima abertura pergunta de novo."""
    p = Prova(tmp_path, grava=False, licenca="comecou")
    p.win.depois_do_sim = None                       # o preparo não deixou a pasta gravável
    p.abrir()
    assert p.vp.chamadas == []
    assert p.atual.estado.fase is fases.Fase.PARADO


def test_d733_com_o_sim_prepara_e_procura_sem_outra_pergunta(tmp_path):
    """D-733 ("1": uma pergunta só, na primeira abertura): com o "Sim" e a pasta aceitando gravação depois, o motor,
    a procura, a assinatura e o download seguem sozinhos, por trás, sem outra pergunta; o aviso vai para a janela."""
    p = Prova(tmp_path, grava=False, licenca="comecou")
    assert p.abrir() is None
    assert len(p.win.pedidos) == 1
    assert p.vp.nomes() == ["procurar", "baixar"]
    p.ligar_a_tela()
    assert p.tipos_na_tela() == ["MostrarVersaoNova"]


def test_protecoes_5_e_6_a_ordem_dos_passos_da_pergunta(tmp_path):
    """D-838 e o plano 4.4: o ajudante antigo (a tarefa que rodava como o sistema um programa desta pasta) sai PRIMEIRO,
    antes de a pasta aceitar gravação de Usuários (6); a licença da pasta é o ÚLTIMO passo (5, D-749: a peça para no
    primeiro passo que falha, então a pasta só fica gravável se tudo antes deu certo)."""
    passos = atualizacao.passos_do_preparo()
    assert [p.tipo for p in passos] == ["apagar_tarefa", "instalar_visual_c", "tirar_instalacao_do_inno",
                                        "dar_licenca_aos_usuarios"]
    assert passos[0].dados == {"nome": atualizacao.NOME_DA_TAREFA} == {"nome": "EditorImpressao\\Procurar versao nova"}


def test_protecao_7_conta_de_testes_nao_pergunta_nem_procura(tmp_path, monkeypatch):
    """D-736/D-741: aberto na conta dos testes à distância, nada pergunta e nada procura (e a janela não recebe nada)."""
    monkeypatch.setenv("USERNAME", "EditorTestes")
    p = Prova(tmp_path, grava=False)
    assert p.abrir() is None
    assert p.win.pedidos == [] and p.vp.chamadas == []
    assert p.atual.estado.fase is fases.Fase.FORA


def test_o_portatil_nao_pergunta_nem_procura(tmp_path):
    """O pacote portátil do ensaio (o `.portable` na raiz, como o Velopack o reconhece) não mexe no computador."""
    p = Prova(tmp_path, grava=False)
    (p.raiz / ".portable").write_text("", encoding="utf-8")
    p.abrir()
    assert p.win.pedidos == [] and p.vp.chamadas == []


# ---------------------------------------------------------------------------------------------------------------------
# Procurar, a assinatura, o motor, baixar
# ---------------------------------------------------------------------------------------------------------------------

def test_protecao_2_assinatura_errada_nao_baixa_e_avisa_com_a_frase_2(tmp_path):
    """D-724 e D-778 (frase 2): a versão publicada sem a assinatura do Samuel não é baixada; fica anotada (não é
    tentada de novo) e a janela mostra "Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura
    do Samuel..."."""
    p = Prova(tmp_path, chave_da_nova=OUTRA_CHAVE)
    p.abrir()
    p.ligar_a_tela()
    assert p.vp.nomes() == ["procurar"]
    assert NOVA in _estado()["nao_tentar"] and _estado()["falha"]["tipo"] == "recusada"
    assert [(type(e).__name__, getattr(e, "tipo", "")) for e in p.tela] == [("MostrarFalha", "recusada")]
    assert atualizacao.FRASES_DA_FALHA["recusada"] == atualizacao.FRASE_DA_FALHA_SEM_ASSINATURA


def test_protecao_4a_motor_fora_do_lugar_nada_e_procurado_nem_anunciado(tmp_path):
    """D-790/D-833 ("motor do Kraken tudo ou nada continua"): sem o motor no lugar, nada é procurado nem anunciado."""
    p = Prova(tmp_path, motor=False)
    p.abrir()
    p.ligar_a_tela()
    assert p.vp.chamadas == [] and p.tela == []


def test_protecao_8_a_versao_que_falhou_nao_e_baixada_de_novo(tmp_path):
    """D-718: a versão que já falhou (anotada em "não tentar") é achada, mas não é conferida nem baixada de novo."""
    atualizacao.gravar_estado({"nao_tentar": [NOVA]})
    p = Prova(tmp_path)
    p.abrir()
    assert p.vp.nomes() == ["procurar"]


def test_sem_internet_nao_e_falha_e_nao_avisa(tmp_path):
    """Sem internet (o Velopack não consegue procurar): só uma linha no registro; nada na tela, nada anotado."""
    p = Prova(tmp_path, erro_ao_procurar="sem internet")
    p.abrir()
    p.ligar_a_tela()
    assert p.tela == [] and "falha" not in _estado()
    assert "sem internet" in _registro()


# ---------------------------------------------------------------------------------------------------------------------
# "Reiniciar agora", "Depois" e o fechar
# ---------------------------------------------------------------------------------------------------------------------

def _ate_o_aviso(tmp_path, **kw) -> Prova:
    p = Prova(tmp_path, **kw)
    p.abrir()
    p.ligar_a_tela()
    assert p.tipos_na_tela() == ["MostrarVersaoNova"]
    return p


def test_d720_reiniciar_agora_fecha_a_janela_e_so_depois_troca(tmp_path):
    """D-715/D-720/D-828 e a proteção 10: "Reiniciar agora" → a janela fecha pelo caminho de sempre (grava) → só
    então a troca, com a janelinha do Velopack e a reabertura na versão nova (o teste rápido antes da janela)."""
    p = _ate_o_aviso(tmp_path)
    ordem = []

    def tela(ef):
        if isinstance(ef, fases.FecharJanela):
            ordem.append("janela fechou")
            p.atual.evento(fases.JanelaFechou(True))

    p.atual.ligar_a_tela(tela)
    p.vp.trocar = lambda e, v, reabrir, args: ordem.append(("trocar", v.versao, reabrir, tuple(args)))
    p.atual.evento(fases.Escolheu(True))
    assert ordem == ["janela fechou", ("trocar", NOVA, True,
                                       (atualizacao.ARG_CONFERIR_NOVA, ATUAL, NOVA, atualizacao.ARG_FONTE,
                                        str(p.fonte_pasta)))]
    assert _estado()["tentando"] == {"de": ATUAL, "para": NOVA, "volta": False, "quando": _estado()["tentando"]["quando"]}


def test_protecao_10_a_janela_que_nao_fecha_nao_troca(tmp_path):
    """A janela recusou fechar no "Reiniciar agora": nada é trocado; ao fechar depois, a pergunta "Atualizar agora?"."""
    p = _ate_o_aviso(tmp_path)
    vistos = []

    def tela(ef):
        vistos.append(type(ef).__name__)
        if isinstance(ef, fases.FecharJanela):
            p.atual.evento(fases.JanelaFechou(False))

    p.atual.ligar_a_tela(tela)
    p.atual.evento(fases.Escolheu(True))
    assert "trocar" not in p.vp.nomes()
    p.atual.evento(fases.Fechando())
    assert vistos == ["FecharJanela", "PerguntarAoFechar"]


def test_d831_depois_e_sim_ao_fechar_troca_sem_janela(tmp_path):
    """D-769/D-794/D-831: "Depois" → nada agora; ao fechar, "Atualizar agora?" → "Sim" → a troca é pedida com a
    reabertura SEM janela (só o teste rápido; nada abre na tela depois)."""
    p = _ate_o_aviso(tmp_path)
    p.atual.evento(fases.Escolheu(False))
    assert "trocar" not in p.vp.nomes()
    p.atual.evento(fases.Fechando())
    assert p.tipos_na_tela()[-1] == "PerguntarAoFechar"
    p.atual.evento(fases.RespondeuAoFechar(True))
    troca = [c for c in p.vp.chamadas if c[0] == "trocar"]
    assert troca == [("trocar", NOVA, True, (atualizacao.ARG_CONFERIR_NOVA, ATUAL, NOVA, atualizacao.ARG_SEM_JANELA,
                                             atualizacao.ARG_FONTE, str(p.fonte_pasta)))]


def test_d794_nao_ao_fechar_fecha_sem_trocar(tmp_path):
    """D-794: "Não" ao fechar → fecha sem trocar; o aviso volta na próxima abertura (a versão continua publicada)."""
    p = _ate_o_aviso(tmp_path)
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(False))
    assert "trocar" not in p.vp.nomes() and "tentando" not in _estado()


def test_fechar_sem_versao_pronta_nao_pergunta(tmp_path):
    """Sem versão pronta (nenhuma publicada), fechar não pergunta nada."""
    p = Prova(tmp_path, publicar_nova=False)
    p.abrir()
    p.ligar_a_tela()
    p.atual.evento(fases.Fechando())
    assert p.tela == []


def test_protecao_3_pacote_trocado_depois_de_baixar_nao_troca(tmp_path):
    """D-724 (a soma do arquivo baixado, logo antes de trocar): com a pasta aceitando gravação de Usuários, outra conta
    poderia trocar o pacote em `packages\\` depois do download; a soma dele não é a assinada → não troca e fica
    anotado ("recusada")."""
    p = _ate_o_aviso(tmp_path)
    (p.raiz / "packages" / f"{PACOTE}-{NOVA}-full.nupkg").write_bytes(b"trocado por outra conta")
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert "trocar" not in p.vp.nomes()
    assert _estado()["falha"]["tipo"] == "recusada" and NOVA in _estado()["nao_tentar"]


def test_protecao_4b_motor_fora_do_lugar_na_hora_de_trocar_nao_troca(tmp_path):
    """D-790/D-833: o motor saiu do lugar entre o aviso e a troca → não troca (sem a versão nova perder o motor)."""
    p = _ate_o_aviso(tmp_path)
    p.motor["no_lugar"] = False
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert "trocar" not in p.vp.nomes()


def test_protecao_9_outra_janela_aberta_nao_troca(tmp_path):
    """Outra janela do programa aberta (o Velopack a fecharia à força, com o que estivesse nela): não troca. A lista de
    processos é pedida deixando de fora este processo e os que ele abriu."""
    p = _ate_o_aviso(tmp_path, outras=[(7, "C:\\Arquivos\\current\\EditorImpressao.exe")])
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert "trocar" not in p.vp.nomes()
    assert p.win.perguntas_de_processos == [(p.raiz / "current", 4242)]
    assert "outra janela" in _registro()


# ---------------------------------------------------------------------------------------------------------------------
# A reabertura pelo Velopack, o teste rápido e a volta
# ---------------------------------------------------------------------------------------------------------------------

def test_d718_reaberto_na_versao_nova_que_passa_no_teste(tmp_path):
    """D-718: reaberto na versão nova (`--conferir-a-versao-nova <de> <para>`), o teste rápido roda antes da janela;
    passou → a anotação da troca sai e a abertura segue (o motor, a procura)."""
    atualizacao.anotar_tentativa(ANTERIOR, ATUAL, False)
    p = Prova(tmp_path, publicar_nova=False)
    assert p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL) is None
    assert "tentando" not in _estado()
    assert p.vp.nomes() == ["procurar"]


def test_d718_teste_que_falha_volta_para_a_anterior_assinada(tmp_path):
    """D-718/D-778 (frase 1): a versão nova não passou no teste rápido → anota "teste", busca a anterior PELA
    BIBLIOTECA (nenhum programa do Velopack à mão), com a assinatura conferida, baixa, troca pela troca única e sai
    sem abrir a janela (o Velopack abre a anterior)."""
    p = Prova(tmp_path, teste=(False, "código 1"))
    saida = p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL)
    assert saida == 0
    assert p.vp.nomes() == ["pacote_da_versao", "baixar", "trocar"]
    assert p.vp.chamadas[-1] == ("trocar", ANTERIOR, True, (atualizacao.ARG_FONTE, str(p.fonte_pasta)))
    assert _estado()["falha"]["tipo"] == "teste" and ATUAL in _estado()["nao_tentar"]
    assert _estado()["tentando"]["volta"] is True


def test_protecao_11_a_volta_sem_a_assinatura_nao_troca_e_avisa_com_a_frase_3(tmp_path):
    """D-724/D-778 (frase 3): a anterior publicada sem a assinatura certa → não baixa nem troca; anota "volta" e a
    janela (a da versão nova, que abre se conseguir) mostra "A atualização não deu certo e o programa não conseguiu
    voltar sozinho..."."""
    p = Prova(tmp_path, teste=(False, "código 1"))
    _publicar(p.fonte_pasta, ANTERIOR, b"pacote da versao anterior", OUTRA_CHAVE)   # a assinatura passa a ser outra
    saida = p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL)
    p.ligar_a_tela()
    assert saida is None
    assert "baixar" not in p.vp.nomes() and "trocar" not in p.vp.nomes()
    assert _estado()["falha"]["tipo"] == "volta"
    assert [getattr(e, "tipo", "") for e in p.tela if isinstance(e, fases.MostrarFalha)] == ["volta"]


def test_a_troca_que_nao_aconteceu_avisa_uma_vez(tmp_path):
    """O Velopack não conseguiu trocar (arquivo preso) e reabriu a versão de antes com os mesmos argumentos: anota
    "troca", mostra a frase (1) uma vez; na abertura seguinte não mostra de novo."""
    p = Prova(tmp_path, publicar_nova=False)
    p.abrir(atualizacao.ARG_CONFERIR_NOVA, ATUAL, NOVA)
    p.ligar_a_tela()
    assert [getattr(e, "tipo", "") for e in p.tela] == ["troca"]
    assert NOVA in _estado()["nao_tentar"]
    q = Prova(tmp_path / "outra", publicar_nova=False)
    q.abrir()
    q.ligar_a_tela()
    assert q.tela == []


def test_d769_reabertura_sem_janela_que_passa_sai_sem_janela(tmp_path):
    """D-769: depois do "Sim" ao fechar, o Velopack reabre com `--sem-janela`: o teste passa e o processo sai (0) sem
    abrir a janela; a próxima abertura já é na versão nova."""
    p = Prova(tmp_path)
    assert p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL, atualizacao.ARG_SEM_JANELA) == 0
    assert p.vp.chamadas == []


def test_a_tarefa_antiga_do_ajudante_so_anota_e_sai():
    """O ajudante antigo (se sobrar num computador) chama o programa com `--procurar-atualizacao`: o programa novo
    anota e sai, sem procurar nada."""
    assert atualizacao.atender_linha_de_comando(["EditorImpressao.exe", atualizacao.ARG_PROCURAR]) == 0
    assert "ajudante antigo" in _registro()


# ---------------------------------------------------------------------------------------------------------------------
# A tela recebe só o que deve, uma vez
# ---------------------------------------------------------------------------------------------------------------------

def test_d719_a_falha_vai_para_a_janela_uma_vez_so_nesta_conta(tmp_path):
    """D-719/D-778: a falha anotada no disco chega à janela uma vez (esperando na fila até a janela abrir); a abertura
    seguinte, na mesma conta, não a mostra de novo."""
    atualizacao.anotar_falha("teste", ANTERIOR, NOVA, "prova")
    p = Prova(tmp_path, publicar_nova=False)
    p.abrir()
    assert p.tela == []                       # a janela ainda não abriu: espera na fila
    p.ligar_a_tela()
    assert [(type(e).__name__, e.tipo) for e in p.tela] == [("MostrarFalha", "teste")]
    q = Prova(tmp_path / "outra", publicar_nova=False)
    q.abrir()
    q.ligar_a_tela()
    assert q.tela == []


def test_d835_e_d778_os_textos_da_tela_palavra_por_palavra():
    """D-835 (os textos curtos) e D-778 (as três frases), palavra por palavra, e cada falha com a sua frase."""
    assert atualizacao.FRASE_DA_VERSAO_NOVA.endswith(
        "Se escolher \"Depois\", você pode atualizar quando fechar o programa.")
    assert (atualizacao.TITULO_AO_FECHAR, atualizacao.FRASE_AO_FECHAR) == (
        "Atualizar agora?", "Quer atualizar o programa agora, ao fechar?")
    assert (atualizacao.BOTAO_SIM_AO_FECHAR, atualizacao.BOTAO_NAO_AO_FECHAR) == ("Sim", "Não")
    assert (atualizacao.BOTAO_REINICIAR, atualizacao.BOTAO_DEPOIS) == ("Reiniciar agora", "Depois")
    assert atualizacao.FRASES_DA_FALHA == {
        "teste": "A atualização não deu certo. O programa voltou para a versão anterior e continua funcionando. "
                 "Avise o Samuel.",
        "troca": "A atualização não deu certo. O programa voltou para a versão anterior e continua funcionando. "
                 "Avise o Samuel.",
        "recusada": "Chegou uma versão nova, mas ela não foi instalada porque não tem a assinatura do Samuel. O "
                    "programa continua funcionando. Avise o Samuel.",
        "volta": "A atualização não deu certo e o programa não conseguiu voltar sozinho. Não desinstale nada. Avise "
                 "o Samuel."}
    assert "próxima vez que você abrir" not in atualizacao.FRASE_DA_VERSAO_NOVA     # o texto antigo saiu


# ---------------------------------------------------------------------------------------------------------------------
# Pelo código, e a troca por um lugar só
# ---------------------------------------------------------------------------------------------------------------------

def test_protecao_12_pelo_codigo_nada_roda(tmp_path, monkeypatch):
    """Pelo código (o atalho "(desenvolvimento)" e os testes): nada da atualização roda, nada é gravado no
    ProgramData, nenhum executor para a janela, e o velopack nem é importado."""
    monkeypatch.delitem(sys.modules, "velopack", raising=False)
    assert atualizacao.atender_linha_de_comando(["main.py"]) is None
    assert atualizacao.da_abertura() is None
    assert "velopack" not in sys.modules
    assert not (tmp_path / "ProgramData").exists()


def _chamadas_de(nome: str) -> list[tuple[str, str]]:
    """(arquivo, função em volta) de cada chamada `<algo>.<nome>(...)` nos arquivos .py do programa (não os testes)."""
    achadas = []
    for caminho in RAIZ_DO_REPOSITORIO.glob("**/*.py"):
        relativo = caminho.relative_to(RAIZ_DO_REPOSITORIO).as_posix()
        if relativo.startswith((".claude/", "tests/", "velhos/", "relatorios/", "historico/", "saida_teste/",
                                ".venv/", "terceiros/")):
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")           # arquivos de outros com escape velho no texto
                arvore = ast.parse(caminho.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for funcao in [n for n in ast.walk(arvore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            for no in ast.walk(funcao):
                if isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute) and no.func.attr == nome:
                    achadas.append((relativo, funcao.name))
    return sorted(set(achadas))


def test_protecao_13_so_um_lugar_chama_a_troca_do_velopack():
    """A troca do Velopack (`wait_exit_then_apply_updates`) é chamada só em `conversa_com_o_velopack.trocar`; e a troca
    da peça (`velopack.trocar`) só em `atualizacao.Atualizacao.trocar_para`, que confere antes (a soma assinada, o
    motor, outra janela). Lido pela árvore de todo o programa."""
    assert _chamadas_de("wait_exit_then_apply_updates") == [("core/conversa_com_o_velopack.py", "trocar")]
    assert [c for c in _chamadas_de("trocar") if c[0] != "tests"] == [("atualizacao.py", "trocar_para")]


def test_os_tres_caminhos_da_troca_passam_pela_mesma_conferencia(tmp_path, monkeypatch):
    """§11.12 (regra num lugar só): o "Reiniciar agora", o "Sim" ao fechar e a volta chegam todos a `trocar_para`."""
    caminhos = []
    original = atualizacao.Atualizacao.trocar_para

    def anotar(self, v, de, para, **kw):
        caminhos.append((de, para, kw.get("sem_janela", False), kw.get("volta", False)))
        return original(self, v, de, para, **kw)

    monkeypatch.setattr(atualizacao.Atualizacao, "trocar_para", anotar)
    p = _ate_o_aviso(tmp_path / "a")
    p.atual.ligar_a_tela(lambda ef: isinstance(ef, fases.FecharJanela) and p.atual.evento(fases.JanelaFechou(True)))
    p.atual.evento(fases.Escolheu(True))
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData-b"))   # cada computador com o seu estado
    q = _ate_o_aviso(tmp_path / "b")
    q.atual.evento(fases.Escolheu(False))
    q.atual.evento(fases.Fechando())
    q.atual.evento(fases.RespondeuAoFechar(True))
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData-c"))
    r = Prova(tmp_path / "c", teste=(False, "x"))
    r.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL)
    assert caminhos == [(ATUAL, NOVA, False, False), (ATUAL, NOVA, True, False), (ATUAL, ANTERIOR, False, True)]


def test_d832_a_troca_usa_a_janelinha_do_velopack(monkeypatch):
    """D-832 ("pode ser velopack"): a peça pede a troca SEM o modo silencioso (a janelinha do Velopack aparece) e com
    os argumentos da reabertura; nunca a troca automática na abertura. A biblioteca é trocada por uma de mentira só
    para ver o pedido (a troca de verdade só na prova à vista)."""
    pedidos = []

    class Gerente:
        def __init__(self, fonte, opcoes):
            pass

        def wait_exit_then_apply_updates(self, pedido, silent, restart, restart_args):
            pedidos.append((pedido, silent, restart, list(restart_args)))

    class App:
        def __getattr__(self, nome):
            def anotar(*a):
                pedidos.append((nome, a))
                return self
            return anotar

    falso = type("vp", (), {"UpdateManager": Gerente, "UpdateOptions": lambda **k: k, "App": App,
                            "GithubSource": lambda e: e})
    monkeypatch.setattr(conversa, "_velopack", lambda: falso)
    v = conversa.VersaoDoVelopack(PACOTE, NOVA, "x.nupkg", "ab", 2, pedido="o pedido")
    conversa.trocar("C:/fonte", v, True, ["--a", "b"])
    assert pedidos == [("o pedido", False, True, ["--a", "b"])]
    pedidos.clear()
    conversa.atender_ganchos(print, print, print)
    assert ("set_auto_apply_on_startup", (False,)) in pedidos


def test_o_indice_publicado_tem_o_nome_do_empacotar():
    """O nome do índice que a volta lê é o mesmo que o publicar põe (o programa não importa o empacotar.py)."""
    import empacotar

    assert atualizacao.NOME_DO_INDICE_PUBLICADO == empacotar.NOME_DO_INDICE


def test_o_teste_de_gravar_cria_e_apaga(tmp_path):
    """O "preparado?" é o teste de gravar de verdade: numa pasta que aceita, True, e nada fica para trás; numa que não
    existe, False."""
    assert atualizacao.pasta_aceita_gravacao(tmp_path) is True
    assert list(tmp_path.iterdir()) == []
    assert atualizacao.pasta_aceita_gravacao(tmp_path / "nao-existe") is False
