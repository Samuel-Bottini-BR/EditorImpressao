"""O desfazer continua certo depois de reabrir o livro (Lista de bugs, 06/10/2026).

O defeito (parecer do verificador-3 dos consertos do girar, 06/10): a pessoa
faz A, faz B, desfaz B e faz C. Na memoria o historico fica [A, C], mas o
acoes.jsonl ficava [A, B, C] (o "refazer" B so era descartado na memoria) e
o posicao.json dizia "2 feitas de 2". Ao reabrir, o programa lia as duas
primeiras linhas: [A, B] feitas e C no "refazer". O Ctrl+Z desfazia B (que
ja tinha sido desfeita) e a ultima acao, C, ia parar no "refazer".

Aqui (historico_acoes.HistoricoAcoes):
  1. a acao nova depois de um desfazer descarta o "refazer" no ARQUIVO
     tambem (o acoes.jsonl e regravado inteiro, com seguranca);
  2. o livro antigo que ja esta com o arquivo errado (mais linhas que o
     posicao.json conta) abre certo: so a ultima acao, que e a unica que se
     sabe com certeza onde esta, fica no historico; o arquivo de antes e
     guardado ao lado (acoes.antigo-historico-*.jsonl), nunca apagado.
"""

from __future__ import annotations

import json
from pathlib import Path

from historico_acoes import ARQUIVO_ACOES, ARQUIVO_POSICAO, HistoricoAcoes, aplicar, montar_acao
from modelos import ConfigFolha, ConfigPagina, Projeto


def _projeto() -> Projeto:
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.folhas = [ConfigFolha(indice=i) for i in range(3)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i // 2) for i in range(6)]
    return projeto


def _fazer(projeto: Projeto, historico: HistoricoAcoes, nome: str, rotacao: int,
           folha: int = 0) -> None:
    """Uma acao de verdade: gira a folha `folha` e registra com o nome dado."""
    acao = montar_acao(projeto, "girar", "folha", [folha], {"rotacao": rotacao}, nome)
    aplicar(projeto, acao, acao.depois)
    historico.registrar(acao)


def _nomes(acoes) -> list[str]:
    return [a.descricao for a in acoes]


def _linhas(pasta: Path) -> list[str]:
    texto = (pasta / ARQUIVO_ACOES).read_text(encoding="utf-8")
    return [json.loads(linha)["descricao"] for linha in texto.splitlines() if linha.strip()]


def _reabrir(pasta: Path) -> HistoricoAcoes:
    historico = HistoricoAcoes(pasta)
    historico.carregar()
    return historico


# --- 1. o defeito, como o verificador reproduziu --------------------------

def test_acao_nova_depois_de_desfazer_sobrevive_a_reabrir(tmp_path):
    projeto = _projeto()
    historico = HistoricoAcoes(tmp_path)
    _fazer(projeto, historico, "A", 90)
    _fazer(projeto, historico, "B", 180)
    historico.desfazer(projeto)                    # desfaz B
    _fazer(projeto, historico, "C", 270)
    assert _nomes(historico.feitas) == ["A", "C"]

    reaberto = _reabrir(tmp_path)
    assert _nomes(reaberto.feitas) == ["A", "C"]
    assert not reaberto.pode_refazer, "B foi descartada: nao volta no refazer"


def test_ctrl_z_depois_de_reabrir_desfaz_a_ultima_acao(tmp_path):
    """O que o Samuel viu na janela: o Ctrl+Z nao desfazia o que ele tinha
    acabado de fazer."""
    projeto = _projeto()
    historico = HistoricoAcoes(tmp_path)
    _fazer(projeto, historico, "A", 90)
    _fazer(projeto, historico, "B", 180)
    historico.desfazer(projeto)
    _fazer(projeto, historico, "C", 270)
    assert projeto.folhas[0].rotacao == 270

    reaberto = _reabrir(tmp_path)
    desfeita = reaberto.desfazer(projeto)
    assert desfeita is not None and desfeita.descricao == "C"
    assert projeto.folhas[0].rotacao == 90, "volta ao giro de A, nao ao de B"
    reaberto.desfazer(projeto)
    assert projeto.folhas[0].rotacao == 0


def test_o_arquivo_tambem_descarta_o_refazer(tmp_path):
    projeto = _projeto()
    historico = HistoricoAcoes(tmp_path)
    for nome, rotacao in (("A", 90), ("B", 180), ("C", 270)):
        _fazer(projeto, historico, nome, rotacao)
    historico.desfazer(projeto)                    # desfaz C
    historico.desfazer(projeto)                    # desfaz B
    _fazer(projeto, historico, "D", 180)
    assert _linhas(tmp_path) == ["A", "D"]
    posicao = json.loads((tmp_path / ARQUIVO_POSICAO).read_text(encoding="utf-8"))
    assert posicao == {"aplicadas": 2, "total": 2}
    assert not list(tmp_path.glob("*.novo")), "o arquivo de passagem nao fica"
    assert not list(tmp_path.glob("*.antigo-*")), "nada de copia no caminho normal"


def test_desfazer_e_refazer_sem_acao_nova_continuam_no_refazer(tmp_path):
    """O que ja funcionava: desfazer e reabrir mantem o refazer."""
    projeto = _projeto()
    historico = HistoricoAcoes(tmp_path)
    _fazer(projeto, historico, "A", 90)
    _fazer(projeto, historico, "B", 180)
    historico.desfazer(projeto)

    reaberto = _reabrir(tmp_path)
    assert _nomes(reaberto.feitas) == ["A"]
    assert _nomes(reaberto.desfeitas) == ["B"]
    assert not list(tmp_path.glob("*.antigo-*"))


def test_refazer_e_acao_nova_so_acrescentam(tmp_path):
    """Sem nada no refazer, a acao nova continua indo para o fim do arquivo
    (o caminho barato de sempre)."""
    projeto = _projeto()
    historico = HistoricoAcoes(tmp_path)
    _fazer(projeto, historico, "A", 90)
    historico.desfazer(projeto)
    historico.refazer(projeto)
    _fazer(projeto, historico, "B", 180)
    assert _linhas(tmp_path) == ["A", "B"]
    assert _nomes(_reabrir(tmp_path).feitas) == ["A", "B"]


def test_sem_poder_gravar_o_desfazer_continua_na_memoria(tmp_path, monkeypatch):
    """Disco que recusa a gravacao nao derruba o programa (como antes)."""
    import projetos

    projeto = _projeto()
    historico = HistoricoAcoes(tmp_path)
    _fazer(projeto, historico, "A", 90)
    _fazer(projeto, historico, "B", 180)
    historico.desfazer(projeto)

    def recusar(*_args, **_kwargs):
        raise OSError("disco cheio")

    monkeypatch.setattr(projetos, "_escrever_e_trocar", recusar)
    _fazer(projeto, historico, "C", 270)
    assert _nomes(historico.feitas) == ["A", "C"]
    assert historico.desfazer(projeto).descricao == "C"


# --- 2. livros que ja estao com o arquivo errado --------------------------

def _livro_com_o_arquivo_errado(pasta: Path, aplicadas: int, total: int) -> bytes:
    """Monta o que o programa antigo deixava depois de A, B, desfazer B, C:
    as tres linhas no arquivo e o posicao.json contando so duas."""
    projeto = _projeto()
    linhas = []
    for nome, rotacao in (("A", 90), ("B", 180), ("C", 270)):
        acao = montar_acao(projeto, "girar", "folha", [0], {"rotacao": rotacao}, nome)
        if nome == "C":
            acao.antes = {"rotacao": {"0": 90}}    # C foi feita depois de B desfeita
        linhas.append(json.dumps(acao.para_dicionario(), ensure_ascii=False))
    conteudo = ("\n".join(linhas) + "\n").encode("utf-8")
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / ARQUIVO_ACOES).write_bytes(conteudo)
    (pasta / ARQUIVO_POSICAO).write_text(
        json.dumps({"aplicadas": aplicadas, "total": total}), encoding="utf-8")
    return conteudo


def test_livro_antigo_com_o_arquivo_errado_abre_com_a_ultima_acao(tmp_path):
    original = _livro_com_o_arquivo_errado(tmp_path, aplicadas=2, total=2)
    reaberto = _reabrir(tmp_path)
    assert _nomes(reaberto.feitas) == ["C"], "so a ultima acao e certa"
    assert not reaberto.pode_refazer

    projeto = _projeto()
    projeto.folhas[0].rotacao = 270               # o livro como ficou (A e C)
    assert reaberto.desfazer(projeto).descricao == "C"
    assert projeto.folhas[0].rotacao == 90, "o Ctrl+Z desfaz C, nao B"

    # o arquivo de antes fica guardado, byte a byte; o novo esta acertado
    copias = list(tmp_path.glob("acoes.antigo-historico-*.jsonl"))
    assert len(copias) == 1 and copias[0].read_bytes() == original
    assert len(list(tmp_path.glob("posicao.antigo-historico-*.json"))) == 1
    assert _linhas(tmp_path) == ["C"]


def test_livro_antigo_acertado_continua_certo_nas_proximas_vezes(tmp_path):
    _livro_com_o_arquivo_errado(tmp_path, aplicadas=2, total=2)
    projeto = _projeto()
    projeto.folhas[0].rotacao = 270
    historico = _reabrir(tmp_path)
    _fazer(projeto, historico, "D", 0, folha=1)

    de_novo = _reabrir(tmp_path)
    assert _nomes(de_novo.feitas) == ["C", "D"]
    assert len(list(tmp_path.glob("acoes.antigo-historico-*.jsonl"))) == 1, \
        "a copia e feita uma vez so"


def test_livro_antigo_errado_com_desfazer_no_fim_abre_sem_historico(tmp_path):
    """Se a ultima coisa foi um desfazer, nao se sabe com certeza o que esta
    feito: melhor nao oferecer o Ctrl+Z do que desfazer a acao errada. O
    livro (projeto.json) nao muda."""
    _livro_com_o_arquivo_errado(tmp_path, aplicadas=1, total=2)
    reaberto = _reabrir(tmp_path)
    assert not reaberto.pode_desfazer and not reaberto.pode_refazer
    assert len(list(tmp_path.glob("acoes.antigo-historico-*.jsonl"))) == 1


def test_livro_antigo_certo_nao_ganha_copia(tmp_path):
    """Arquivo com as mesmas linhas que o posicao.json conta: nada muda."""
    projeto = _projeto()
    historico = HistoricoAcoes(tmp_path)
    _fazer(projeto, historico, "A", 90)
    _fazer(projeto, historico, "B", 180)
    antes = (tmp_path / ARQUIVO_ACOES).read_bytes()
    reaberto = _reabrir(tmp_path)
    assert _nomes(reaberto.feitas) == ["A", "B"]
    assert (tmp_path / ARQUIVO_ACOES).read_bytes() == antes
    assert not list(tmp_path.glob("*.antigo-*"))


def test_linha_cortada_no_fim_continua_como_antes(tmp_path):
    """Queda de energia no meio da ultima linha (menos linhas que o
    posicao.json conta): continua so contando a linha perdida."""
    projeto = _projeto()
    historico = HistoricoAcoes(tmp_path)
    _fazer(projeto, historico, "A", 90)
    _fazer(projeto, historico, "B", 180)
    caminho = tmp_path / ARQUIVO_ACOES
    caminho.write_bytes(caminho.read_bytes()[:-20])
    reaberto = _reabrir(tmp_path)
    assert _nomes(reaberto.feitas) == ["A"]
    assert reaberto.linhas_perdidas == 1
    assert not list(tmp_path.glob("*.antigo-*"))
