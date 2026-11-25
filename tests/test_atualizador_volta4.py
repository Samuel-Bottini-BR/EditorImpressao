"""Volta 4 do atualizador novo (24/11/2026): as três regras do Samuel no lugar de oito consertos (D-855, D-856, D-857),
o "Sim" ao fechar com a frase (D-858, D-864), o pacote esperando (D-859), os quatro testes do M7 (D-860), a rede que não
responde na assinatura, e os leves L1 e L5 do terceiro "quem tenta quebrar"
(`relatorios/atualizador-novo/quem-tenta-quebrar-3/relatorio.md`; a tabela das falhas no topo do ONDE-PAREI).

Cada teste diz o que cobra e de onde veio. Os que cobram comportamento novo FALHAM no código de `1d01aaf9` (a saída lá:
`relatorios/atualizador-novo/volta4-testes-no-codigo-antigo.txt`); os quatro do M7 PASSAM lá (as proteções existiam;
faltava o teste que as acusa: a prova é a rodada de mutações). Para a falha lá ser pelo comportamento, eles usam o que
os dois códigos têm (a `Prova`, o executor) e montam a pasta da última boa à mão.

Só a borda é de mentira (`tests/ajudante_do_atualizador.py`). O que é de verdade no Windows e no Velopack (a volta
recusada de verdade, com o atualizador do Velopack e um programa de prova) está em
`relatorios/atualizador-novo/volta4-provas/`.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import assinatura
import atualizacao
import versao
from core import fases_da_atualizacao as fases
from tests.ajudante_do_atualizador import (ANTERIOR, ATUAL, NOVA, PACOTE, PUBLICA, Prova, VelopackFalso,  # noqa: F401
                                          _ate_o_aviso, _estado, _registro, programdata_de_prova)

RAIZ_DO_REPOSITORIO = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _programdata(programdata_de_prova):
    """O estado, o registro e as frases vistas numa pasta de prova."""


def _guardar_a_mao(p: Prova, v: str) -> Path:
    """O pacote e a assinatura da versão `v` em `<raiz>/ultima-boa`, como a guarda deixa."""
    pasta = p.raiz / "ultima-boa"
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / f"{PACOTE}-{v}-full.nupkg").write_bytes(p.vp.conteudo[v])
    nome = assinatura.nome_do_arquivo_da_assinatura(PACOTE, v)
    (pasta / nome).write_bytes((p.fonte_pasta / nome).read_bytes())
    return pasta


class ContaDoTeste:
    """O teste rápido de mentira que conta quantas vezes rodou."""

    def __init__(self, passa: bool):
        self.passa, self.vezes = passa, 0

    def __call__(self):
        self.vezes += 1
        return self.passa, "o teste de prova"


def _outra_abertura(p: Prova, teste: "ContaDoTeste", vp=None, fonte=None) -> atualizacao.Atualizacao:
    """Outro processo do programa na MESMA instalação de prova."""
    return atualizacao.Atualizacao(
        windows=p.win, velopack=vp or VelopackFalso(p.raiz, p.vp.publicada, "", p.vp.conteudo),
        raiz=p.raiz, fonte=fonte or p.atual.fonte, por_tras=lambda trabalho: trabalho(),
        pasta_grava=lambda raiz: True, garantir_motor=lambda: True, motor_no_lugar=lambda m=None: True,
        teste=teste, chave_publica=PUBLICA)


def _na_tela(atual) -> list:
    tela: list = []
    atual.ligar_a_tela(tela.append)
    return tela


# ---------------------------------------------------------------------------------------------------------------------
# Regra 1 (D-855, D-863): a volta tenta uma vez e nunca fica em laço
# ---------------------------------------------------------------------------------------------------------------------


def test_d863_a_volta_que_nem_pode_ser_pedida_tambem_nao_se_repete(tmp_path):
    """D-863: a volta que não pôde ser pedida (o pacote guardado não confere) mostra a frase (3) e não se repete na
    abertura seguinte (nem o teste)."""
    p = Prova(tmp_path, teste=(False, "código 1"))
    pasta = _guardar_a_mao(p, ANTERIOR)
    (pasta / f"{PACOTE}-{ANTERIOR}-full.nupkg").write_bytes(b"estragado")
    p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL)
    assert "trocar" not in p.vp.nomes()
    teste = ContaDoTeste(passa=False)
    assert _outra_abertura(p, teste).abrir([]) is None and teste.vezes == 0


# ---------------------------------------------------------------------------------------------------------------------
# Regra 2 (D-856): versão aprovada não é testada de novo; a cópia que não cabe não se repete
# ---------------------------------------------------------------------------------------------------------------------

def test_d856_a_versao_aprovada_nao_e_testada_de_novo_e_sem_espaco_nada_e_copiado(tmp_path, monkeypatch):
    """D-856 ("Versão aprovada no teste rápido ganha uma marca no disco e não é testada de novo. Se a cópia da última
    boa não couber, a anterior continua valendo; conferir espaço antes de copiar, pela mesma função do motor."): com o
    disco sem espaço, a versão nova passa no teste, NADA é copiado, a última boa de antes continua, e a abertura seguinte
    não testa. Em `1d01aaf9` a cópia ia até o fim (não conferia o espaço) e o teste se repetia (o M4)."""
    import shutil

    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL)
    real = shutil.disk_usage
    monkeypatch.setattr(shutil, "disk_usage", lambda caminho: real(caminho)._replace(free=1024))
    p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL)
    pasta = atualizacao.pasta_da_ultima_boa(p.raiz)
    assert atualizacao.ler_ultima_boa(p.raiz) == ANTERIOR
    assert not list(pasta.glob("*.chegando")) and not (pasta / f"{PACOTE}-{ATUAL}-full.nupkg").exists()
    teste = ContaDoTeste(passa=True)
    _outra_abertura(p, teste).abrir([])
    assert teste.vezes == 0


def test_d856_o_espaco_e_a_mesma_conta_do_motor(tmp_path, monkeypatch):
    """D-856 ("pela mesma função do motor"): o motor do Kraken e a guarda da última boa perguntam o espaço livre pela
    MESMA função (`espaco_livre_basta`); não há outra conta de espaço no arquivo (lido pela árvore: só ela chama o
    `disk_usage`)."""
    arvore = ast.parse((RAIZ_DO_REPOSITORIO / "atualizacao.py").read_text(encoding="utf-8"))
    quem = {f.name for f in ast.walk(arvore) if isinstance(f, ast.FunctionDef)
            for n in ast.walk(f) if isinstance(n, ast.Attribute) and n.attr == "disk_usage"}
    assert quem == {"espaco_livre_basta"}
    perguntas = []
    original = atualizacao.espaco_livre_basta
    monkeypatch.setattr(atualizacao, "espaco_livre_basta",
                        lambda pasta, precisa, livre=None: perguntas.append(Path(pasta)) or original(pasta, precisa, livre))
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL)
    atualizacao.guardar_ultima_boa(p.raiz, ATUAL, p.atual.fonte, PUBLICA)
    assert perguntas == [atualizacao.pasta_da_ultima_boa(p.raiz)]


# ---------------------------------------------------------------------------------------------------------------------
# Regra 3 (D-857): a primeira versão instalada não tem volta automática; sem última boa, a falha mostra a (3) e para
# ---------------------------------------------------------------------------------------------------------------------

def test_d857_a_primeira_versao_do_msi_nao_e_testada_nem_baixa_nada(tmp_path):
    """D-857 ("A primeira versão instalada não tem volta automática. Sem baixar 460 MB na primeira abertura."): sem
    última boa e sem o pacote da versão em `packages` (o .msi não o põe lá), nada é testado nem baixado. Em
    `1d01aaf9`: o teste por trás e o download de 460 MB."""
    p = Prova(tmp_path, publicar_nova=False)
    p.conteudo_de(ATUAL)                                # publicada (o código de antes a baixaria)
    teste = ContaDoTeste(passa=True)
    atual = _outra_abertura(p, teste, vp=p.vp)
    atual.abrir([])
    assert teste.vezes == 0 and ("baixar", ATUAL) not in [c[:2] for c in p.vp.chamadas]
    assert atualizacao.ler_ultima_boa(p.raiz) == ""


def test_d857_d868_sem_ultima_boa_a_versao_que_falha_mostra_a_frase_e_abre(tmp_path):
    """D-857 ("Sem última boa, a atualização acontece assim mesmo; se a versão nova falhar no teste, aparece a frase
    (3) da D-778 e para.") com a D-868 (25/11/2026: a "frase (3)" da D-857 passa a ser a da D-868, "Depois o programa
    tenta abrir assim mesmo"): a primeira atualização depois do .msi (o pacote dela em `packages`, nenhuma última boa)
    falha no teste: a frase da D-868, a versão fica reprovada, e a abertura segue (o motor e a procura). Era
    `test_d857_sem_ultima_boa_a_versao_que_falha_mostra_a_frase_3_e_para` (lista da D-836, volta 5)."""
    p = Prova(tmp_path, teste=(False, "código 1"))
    p.pacote_em_packages(ATUAL)
    assert p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL) is None
    p.ligar_a_tela()
    assert [e.tipo for e in p.tela if isinstance(e, fases.MostrarFalha)] == [fases.FALHA_REPROVADA]
    assert "procurar" in p.vp.nomes() and ATUAL in (_estado().get("reprovadas") or [])
    assert "trocar" not in p.vp.nomes()


def test_d857_sem_o_pacote_em_packages_nada_e_baixado_e_a_anterior_vale(tmp_path):
    """D-857 (a D-851 mudou: sai o "baixar se não estiver lá"): a versão passa no teste mas o pacote dela não está em
    `packages`: nada é baixado, a última boa de antes continua."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.conteudo_de(ATUAL)
    p.abrir(atualizacao.ARG_CONFERIR_NOVA, ANTERIOR, ATUAL)
    assert ("baixar", ATUAL) not in [c[:2] for c in p.vp.chamadas]
    assert atualizacao.ler_ultima_boa(p.raiz) == ANTERIOR


# ---------------------------------------------------------------------------------------------------------------------
# D-858, D-864: o "Sim" ao fechar que não troca mostra a frase na abertura seguinte
# ---------------------------------------------------------------------------------------------------------------------

def test_d858_d864_sim_ao_fechar_com_outra_janela_mostra_a_frase_na_abertura_seguinte(tmp_path):
    """D-858 ("o 'Sim' ao fechar que não troca ganha a mesma frase do 'Reiniciar agora', na abertura seguinte") e D-864
    ("Não deu para atualizar agora: havia outra janela do programa aberta. Tente ao fechar o programa."). Em
    `1d01aaf9`: nada, nem depois (o M3)."""
    p = _ate_o_aviso(tmp_path, outras=[(7, r"C:\Program Files\EditorImpressaoPrograma\current\EditorImpressao.exe")])
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(True))
    assert "trocar" not in p.vp.nomes()
    seguinte = _outra_abertura(p, ContaDoTeste(passa=True))
    seguinte.abrir([])
    # Volta 5 (D-868, lista da D-836): a frase da abertura seguinte vem antes da janela: pela caixa do Windows.
    assert [texto for _, texto in p.win.caixas] == [
        "Não deu para atualizar agora: havia outra janela do programa aberta. Tente ao fechar o programa."]
    assert not [e for e in _na_tela(seguinte) if isinstance(e, fases.MostrarFalha)]


# ---------------------------------------------------------------------------------------------------------------------
# D-859: sem internet, o pacote esperando
# ---------------------------------------------------------------------------------------------------------------------

def test_d859_sem_internet_o_pacote_ja_baixado_e_anunciado(tmp_path):
    """D-859 ("Sem internet, com a versão nova já baixada, o aviso volta e a pergunta ao fechar aparece."): uma
    abertura baixa a versão nova (e guarda a assinatura dela ao conferir) e fecha com "Não"; a seguinte, sem internet,
    mostra o aviso de novo. Em `1d01aaf9`: nada (o M6)."""
    p = _ate_o_aviso(tmp_path)
    p.atual.evento(fases.Escolheu(False))
    p.atual.evento(fases.Fechando())
    p.atual.evento(fases.RespondeuAoFechar(False))
    sem_internet = VelopackFalso(p.raiz, None, "sem internet", p.vp.conteudo, pendente=NOVA)
    seguinte = _outra_abertura(p, ContaDoTeste(passa=True), vp=sem_internet,
                               fonte=atualizacao.Fonte(str(tmp_path / "sem-internet")))
    seguinte.abrir([])
    tela = _na_tela(seguinte)
    assert [type(e).__name__ for e in tela] == ["MostrarVersaoNova"]
    seguinte.evento(fases.Escolheu(False))
    seguinte.evento(fases.Fechando())
    assert type(tela[-1]).__name__ == "PerguntarAoFechar"


# ---------------------------------------------------------------------------------------------------------------------
# A rede que não responde na conferência da assinatura (achado da tabela da volta 4)
# ---------------------------------------------------------------------------------------------------------------------

def test_a_rede_que_nao_responde_na_assinatura_nao_e_recusada(tmp_path):
    """Achado ao montar a tabela da volta 4 (Conferir × sem internet): a procura achou a versão nova e a internet caiu
    antes de ler a assinatura. Em `1d01aaf9` isso virava "recusada" e a tela mostrava a frase (2) ("não tem a assinatura
    do Samuel"), que é falsa. Agora: só o registro; a frase (2) fica para a assinatura que não existe ou não confere."""
    p = Prova(tmp_path)
    p.atual.fonte = atualizacao.Fonte(str(tmp_path / "sem-internet"))
    p.abrir()
    p.ligar_a_tela()
    assert p.tela == [] and "baixar" not in p.vp.nomes()
    q = Prova(tmp_path / "q")
    (q.fonte_pasta / assinatura.nome_do_arquivo_da_assinatura(PACOTE, NOVA)).unlink()      # não existe: recusada
    q.abrir()
    q.ligar_a_tela()
    assert [e.tipo for e in q.tela if isinstance(e, fases.MostrarFalha)] == [fases.FALHA_RECUSADA]


# ---------------------------------------------------------------------------------------------------------------------
# D-860: os quatro testes do M7 (Q1, Q2, Q9, Q13)
# ---------------------------------------------------------------------------------------------------------------------

def test_m7_q1_a_guarda_nao_apaga_a_assinatura_da_versao_que_esta_chegando(tmp_path):
    """Q1 (D-860): guardar a última boa não apaga a assinatura de uma versão MAIS NOVA que já foi conferida e está
    chegando (sem ela, essa versão precisaria de internet para virar a última boa depois)."""
    p = Prova(tmp_path, publicar_nova=True, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL)
    pasta = atualizacao.pasta_da_ultima_boa(p.raiz)
    chegando = [pasta / assinatura.nome_do_arquivo_da_assinatura(PACOTE, NOVA),
                pasta / (assinatura.nome_do_arquivo_da_assinatura(PACOTE, NOVA) + ".chegando")]
    for arquivo in chegando:
        arquivo.write_bytes((p.fonte_pasta / assinatura.nome_do_arquivo_da_assinatura(PACOTE, NOVA)).read_bytes())
    assert atualizacao.guardar_ultima_boa(p.raiz, ATUAL, p.atual.fonte, PUBLICA) is None
    assert all(arquivo.exists() for arquivo in chegando)


def test_m7_q2_com_duas_na_pasta_a_ultima_boa_e_a_mais_nova(tmp_path):
    """Q2 (D-860): com duas versões guardadas (a limpeza não conseguiu apagar a velha), a última boa é a MAIS NOVA."""
    p = Prova(tmp_path, publicar_nova=False)
    _guardar_a_mao(p, ANTERIOR)
    p.pacote_em_packages(ATUAL)
    pasta = atualizacao.pasta_da_ultima_boa(p.raiz)
    (pasta / f"{PACOTE}-{ATUAL}-full.nupkg").write_bytes(p.conteudo_de(ATUAL))
    nome = assinatura.nome_do_arquivo_da_assinatura(PACOTE, ATUAL)
    (pasta / nome).write_bytes((p.fonte_pasta / nome).read_bytes())
    assert atualizacao.ler_ultima_boa(p.raiz) == max(ANTERIOR, ATUAL, key=versao.numeros)


def test_m7_q9_a_mesma_frase_noutro_dia_aparece_de_novo(tmp_path, monkeypatch):
    """Q9 (D-860): a frase guardada para a próxima abertura leva a hora no nome; a mesma frase guardada noutra hora
    tem outro nome e aparece de novo (a tela mostra cada nome uma vez)."""
    nomes = []
    for hora in ("2026-11-24T10:00:00", "2026-11-25T10:00:00"):
        monkeypatch.setattr(atualizacao, "_agora", lambda hora=hora: hora)
        atualizacao.guardar_frase(fases.NAO_DEU_AGORA, NOVA, fases.MOTIVO_SEM_LISTA)
        nomes.append(atualizacao.frase_do_bilhete(atualizacao.ler_estado())[1])
    assert nomes[0] != nomes[1]


def test_m7_q13_a_copia_com_a_soma_errada_nao_fica_no_disco(tmp_path):
    """Q13 (D-860): a cópia da guarda cuja soma não é a assinada é apagada (não sobram 460 MB no disco)."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL).write_bytes(b"conteudo trocado")
    assert "soma" in (atualizacao.guardar_ultima_boa(p.raiz, ATUAL, p.atual.fonte, PUBLICA) or "")
    assert not list(atualizacao.pasta_da_ultima_boa(p.raiz).glob("*.chegando"))


# ---------------------------------------------------------------------------------------------------------------------
# Os leves L1 e L5
# ---------------------------------------------------------------------------------------------------------------------

def test_l1_a_guarda_que_falha_nunca_faz_a_pasta_dizer_a_nova(tmp_path):
    """L1 do terceiro "quem tenta quebrar": um pacote velho no nome final e uma guarda que falha não podem fazer a pasta
    dizer que a última boa é a nova (a assinatura da última boa só nasce depois do pacote conferido no lugar). Em
    `1d01aaf9` a assinatura era gravada antes da cópia, e a pasta passava a dizer a nova."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL).write_bytes(b"conteudo trocado")          # a cópia vai falhar na soma
    pasta = atualizacao.pasta_da_ultima_boa(p.raiz)
    (pasta / f"{PACOTE}-{ATUAL}-full.nupkg").write_bytes(b"pacote velho")   # um arquivo velho no nome final
    assert atualizacao.guardar_ultima_boa(p.raiz, ATUAL, p.atual.fonte, PUBLICA) is not None
    assert atualizacao.ler_ultima_boa(p.raiz) == ANTERIOR


def test_l1_com_o_nome_final_preso_a_pasta_nao_diz_a_nova(tmp_path):
    """L1, o caso que o terceiro "quem tenta quebrar" EXECUTOU (G8): um arquivo velho no nome final, preso por outro
    programa (aqui, aberto por este processo: o Windows não deixa pôr outro arquivo por cima). A cópia certa não consegue
    o nome final; a guarda diz que não deu, a cópia some, e a pasta continua dizendo a anterior. Cobra a regra única
    (a assinatura da última boa é gravada POR ÚLTIMO, depois do pacote no lugar): em `1d01aaf9` a pasta passava a dizer
    a nova, com o pacote velho."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL)                                             # o pacote certo
    pasta = atualizacao.pasta_da_ultima_boa(p.raiz)
    velho = pasta / f"{PACOTE}-{ATUAL}-full.nupkg"
    velho.write_bytes(b"pacote velho")
    with velho.open("rb"):                                                  # preso
        motivo = atualizacao.guardar_ultima_boa(p.raiz, ATUAL, p.atual.fonte, PUBLICA)
    assert motivo is not None and "não consegui guardar" in motivo
    assert atualizacao.ler_ultima_boa(p.raiz) == ANTERIOR
    assert not (pasta / assinatura.nome_do_arquivo_da_assinatura(PACOTE, ATUAL)).exists()
    assert not list(pasta.glob("*.nupkg.chegando"))


def test_l1_a_assinatura_que_chega_nao_faz_a_pasta_dizer_a_nova(tmp_path):
    """L1 no outro passo que escreve na pasta: a conferência da versão que chega guarda a assinatura dela com OUTRO nome
    (`.assinatura.chegando`). Com um arquivo velho no nome final do pacote dela, a pasta continua dizendo a anterior; e
    a assinatura fica guardada para a guarda de depois (D-852)."""
    p = Prova(tmp_path, ultima_boa=ANTERIOR)
    pasta = atualizacao.pasta_da_ultima_boa(p.raiz)
    (pasta / f"{PACOTE}-{NOVA}-full.nupkg").write_bytes(b"pacote velho")
    import hashlib
    from types import SimpleNamespace

    alvo = SimpleNamespace(pacote=PACOTE, versao=NOVA, arquivo=f"{PACOTE}-{NOVA}-full.nupkg",
                           sha256=hashlib.sha256(p.vp.conteudo[NOVA]).hexdigest())
    assert atualizacao.conferir_assinatura_do(p.atual.fonte, alvo, PUBLICA, guardar_em=pasta) is None
    assert atualizacao.ler_ultima_boa(p.raiz) == ANTERIOR
    assert atualizacao.assinatura_guardada(p.raiz, NOVA) is not None


def test_a_copia_interrompida_nunca_fica_com_o_nome_do_pacote(tmp_path, monkeypatch):
    """A guarda interrompida no meio da cópia (desligou, o processo morreu) nunca deixa um pacote pela metade com o nome
    do pacote (§11.12 ponto 3: nada pela metade com cara de pronto): a cópia vai para `<nome>.chegando` e só ganha o
    nome com a soma conferida."""
    p = Prova(tmp_path, publicar_nova=False, ultima_boa=ANTERIOR)
    p.pacote_em_packages(ATUAL)

    class Morreu(Exception):
        pass

    original = assinatura.soma_sha256

    def copia_que_morre(origem, copiar_para=None):
        if copiar_para is None:
            return original(origem)
        Path(copiar_para).write_bytes(Path(origem).read_bytes()[:10])
        raise Morreu()

    monkeypatch.setattr(assinatura, "soma_sha256", copia_que_morre)
    with pytest.raises(Morreu):
        atualizacao.guardar_ultima_boa(p.raiz, ATUAL, p.atual.fonte, PUBLICA)
    assert not (atualizacao.pasta_da_ultima_boa(p.raiz) / f"{PACOTE}-{ATUAL}-full.nupkg").exists()


def test_l5_a_soma_do_pacote_e_uma_conta_so(tmp_path):
    """L5 do terceiro "quem tenta quebrar" (§11.12): a soma SHA256 de um arquivo é calculada num lugar só
    (`assinatura.soma_sha256`); o `atualizacao.py` não tem a sua (lido pela árvore: não usa `hashlib`)."""
    arvore = ast.parse((RAIZ_DO_REPOSITORIO / "atualizacao.py").read_text(encoding="utf-8"))
    usa = [n for n in ast.walk(arvore) if isinstance(n, (ast.Import, ast.ImportFrom))
           and any(a.name == "hashlib" for a in n.names)]
    assert usa == []
    origem = tmp_path / "a.bin"
    origem.write_bytes(b"x" * 10_000_000)
    copia = tmp_path / "b.bin"
    assert assinatura.soma_sha256(origem, copiar_para=copia) == assinatura.soma_sha256(origem)
    assert copia.read_bytes() == origem.read_bytes()
