"""Quando a conferencia recomeca sozinha, o Ctrl+Z recomeca vazio (Lista de bugs, 06/10/2026).

O defeito (parecer do verificador dos consertos de 06/10, item 5): a
conferencia recomeca sozinha quando o trabalho salvo nao combina com o livro
(a pessoa mudou "Dividir folhas ao meio", o PDF foi trocado, o projeto.json
nao da para ler...). O programa guardava a copia do trabalho, mas o historico
do desfazer continuava o da conferencia anterior: num PDF de 12 paginas que
ficou com 6, o primeiro Ctrl+Z pos a pagina 1 em Preto e branco, uma acao
feita antes na METADE esquerda da folha 1 (outra pagina). Causa:
ui/janela_principal.py, _analise_pronta, chamava self.acoes.carregar() mesmo
quando o trabalho nao combinava (e, na mesma sessao, o historico em memoria
nem era trocado).

O que se cobra aqui (teste de maquina):
  - na janela, pelo caminho do verificador (mudar "Dividir folhas ao meio" e
    clicar Conferir): o Ctrl+Z (o item Desfazer do menu) nao faz nada no
    livro recomecado, e o refazer tambem nao;
  - o historico antigo nao se perde: fica junto da copia do trabalho
    (acoes.antigo-<data>.jsonl ao lado do projeto.antigo-<data>.json),
    byte a byte, e sai do acoes.jsonl;
  - o mesmo ao abrir um livro cujo trabalho salvo nao combina, e com o
    projeto.json ilegivel;
  - depois do recomeco, o historico novo funciona e volta ao reabrir, sem as
    acoes antigas;
  - quando o trabalho COMBINA, o historico continua voltando (nada mudou);
  - sem a copia do trabalho, o historico antigo e guardado sozinho
    (acoes.antigo-historico-*), e sem nem isso nada e apagado.

Pasta de dados propria em saida_teste\\ (fixture `pasta`, LOCALAPPDATA
trocado): nada e criado na pasta de dados real do Samuel.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

import projetos  # noqa: E402
from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from historico_acoes import (  # noqa: E402
    ARQUIVO_ACOES, ARQUIVO_POSICAO, HistoricoAcoes, aplicar, montar_acao)
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _pdf,
    _trabalhar_e_fechar,
    app,
    janela,
    pasta,
)


def _pdf_de_folhas_duplas(pasta: Path, folhas: int = 6) -> Path:
    """Um PDF de folhas deitadas (duas paginas por folha), como o do
    verificador: 6 folhas, 12 paginas com "Dividir folhas ao meio"."""
    (pasta / "livros").mkdir(exist_ok=True)
    caminho = pasta / "livros" / "Folhas Duplas.pdf"
    doc = fitz.open()
    for i in range(folhas):
        pagina = doc.new_page(width=800, height=560)
        pagina.insert_text((40, 60), f"esquerda {i}", fontsize=14)
        pagina.insert_text((440, 60), f"direita {i}", fontsize=14)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _linhas(caminho: Path) -> list[str]:
    if not caminho.is_file():
        return []
    return [json.loads(linha)["descricao"]
            for linha in caminho.read_text(encoding="utf-8").splitlines() if linha.strip()]


def _copias(pasta_do_projeto: Path, prefixo: str) -> list[Path]:
    return sorted(pasta_do_projeto.glob(f"{prefixo}.antigo-*"))


def _ctrl_z(janela) -> None:
    """O Ctrl+Z da tela: o item Desfazer do menu Editar (o mesmo da tecla)."""
    janela.menu.acoes["desfazer"].trigger()


def _refazer(janela) -> None:
    janela.menu.acoes["refazer"].trigger()


def _conferir_com_o_livro_dividido_e_mexer(janela, livro: Path) -> None:
    """Passo 1 do verificador: livro de 12 paginas, gira a folha 1 e poe a
    pagina 1 em Preto e branco e depois em Melhorar."""
    janela.abrir_livro(str(livro))
    assert janela.projeto.dividir_folhas, "o padrao de fabrica divide as folhas"
    _analisar(janela)
    assert len(janela.projeto.paginas) == 12
    conferir = janela.tela_conferir
    conferir._ir_para(0)
    conferir._girar_folhas(90)
    conferir._escolher_filtro(PRETO_E_BRANCO)
    conferir._escolher_filtro(MELHORAR)
    assert len(janela.acoes.feitas) == 3
    assert janela.projeto.folhas[0].rotacao == 90
    assert janela.projeto.paginas[0].filtro == MELHORAR


def _desmarcar_dividir_e_conferir(janela) -> None:
    """Passos 2 e 3: volta as opcoes, desmarca "Dividir folhas ao meio" e
    clica Conferir (sem a tarefa em segundo plano)."""
    janela._sair_da_conferencia()
    janela.tela_opcoes.cx_dividir.setChecked(False)
    assert janela.projeto.dividir_folhas is False
    _analisar(janela)


# --- 1. na janela, pelo caminho do verificador -----------------------------------------


def test_mudar_dividir_recomeca_o_ctrl_z_vazio(janela, pasta):
    livro = _pdf_de_folhas_duplas(pasta)
    _conferir_com_o_livro_dividido_e_mexer(janela, livro)
    _desmarcar_dividir_e_conferir(janela)

    assert janela.avisos and "Comecei a conferência" in janela.avisos[-1]
    paginas = janela.projeto.paginas
    assert len(paginas) == 6
    assert all(p.filtro == ORIGINAL for p in paginas)
    assert janela.projeto.folhas[0].rotacao == 0

    assert not janela.acoes.pode_desfazer, (
        "o Ctrl+Z do livro recomecado ainda tem acoes da conferencia anterior: "
        + janela.acoes.descricao_desfazer())
    assert not janela.acoes.pode_refazer

    # O que o verificador viu: o primeiro Ctrl+Z pos a pagina 1 em Preto e
    # branco. Agora nada muda.
    _ctrl_z(janela)
    assert janela.projeto.paginas[0].filtro == ORIGINAL
    assert all(p.filtro == ORIGINAL for p in janela.projeto.paginas)
    assert janela.projeto.folhas[0].rotacao == 0
    _refazer(janela)
    assert all(p.filtro == ORIGINAL for p in janela.projeto.paginas)


def test_o_historico_antigo_fica_junto_da_copia_do_trabalho(janela, pasta):
    livro = _pdf_de_folhas_duplas(pasta)
    _conferir_com_o_livro_dividido_e_mexer(janela, livro)
    pasta_do_projeto = Path(janela.resumo.pasta)
    acoes_antes = (pasta_do_projeto / ARQUIVO_ACOES).read_bytes()
    posicao_antes = (pasta_do_projeto / ARQUIVO_POSICAO).read_bytes()

    _desmarcar_dividir_e_conferir(janela)

    copia = janela.copia_do_trabalho
    assert copia is not None and copia.is_file()
    sufixo = copia.name[len("projeto.antigo-"):-len(".json")]
    acoes_da_copia = pasta_do_projeto / f"acoes.antigo-{sufixo}.jsonl"
    posicao_da_copia = pasta_do_projeto / f"posicao.antigo-{sufixo}.json"
    assert acoes_da_copia.read_bytes() == acoes_antes, "o historico antigo se perdeu"
    assert posicao_da_copia.read_bytes() == posicao_antes
    assert len(_linhas(acoes_da_copia)) == 3
    # e saiu do historico da conferencia nova
    assert _linhas(pasta_do_projeto / ARQUIVO_ACOES) == []
    # nenhuma copia a mais (a do historico ja esta junto da do trabalho)
    assert not list(pasta_do_projeto.glob("*.antigo-historico-*"))


def test_depois_do_recomeco_o_historico_novo_funciona_e_volta_ao_reabrir(janela, pasta):
    livro = _pdf_de_folhas_duplas(pasta)
    _conferir_com_o_livro_dividido_e_mexer(janela, livro)
    _desmarcar_dividir_e_conferir(janela)

    conferir = janela.tela_conferir
    conferir._ir_para(2)
    conferir._escolher_filtro(PRETO_E_BRANCO)
    assert [a.descricao for a in janela.acoes.feitas] == [
        "Filtro da página 3: Original para Preto e branco"]
    pasta_do_projeto = Path(janela.resumo.pasta)
    assert _linhas(pasta_do_projeto / ARQUIVO_ACOES) == [
        "Filtro da página 3: Original para Preto e branco"]

    # fecha e abre de novo: so a acao da conferencia nova volta
    janela._salvar_agora()
    janela.abrir_livro(str(livro))
    _analisar(janela)
    assert len(janela.projeto.paginas) == 6
    assert [a.descricao for a in janela.acoes.feitas] == [
        "Filtro da página 3: Original para Preto e branco"]
    _ctrl_z(janela)
    assert janela.projeto.paginas[2].filtro == ORIGINAL
    assert not janela.acoes.pode_desfazer
    assert all(p.filtro == ORIGINAL for p in janela.projeto.paginas)


# --- 2. os outros caminhos de recomeco ---------------------------------------------------


def test_abrir_livro_cujo_trabalho_nao_combina_recomeca_o_ctrl_z_vazio(janela, pasta):
    """O caminho do "Abrir" (e do "continuar"): o trabalho salvo tem outro
    numero de paginas (como depois de mudar "Dividir" e fechar)."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    estado = Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO
    dados = json.loads(estado.read_text(encoding="utf-8"))
    dados["paginas"] = dados["paginas"][:3]
    estado.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    acoes_antes = (estado.parent / ARQUIVO_ACOES).read_bytes()

    janela.abrir_livro(str(livro))
    _analisar(janela)

    assert janela.avisos, "recomecou sem avisar"
    assert not janela.acoes.pode_desfazer and not janela.acoes.pode_refazer
    _ctrl_z(janela)
    assert all(p.filtro == ORIGINAL for p in janela.projeto.paginas)
    assert _copias(estado.parent, "acoes")[0].read_bytes() == acoes_antes
    assert _linhas(estado.parent / ARQUIVO_ACOES) == []


def test_projeto_ilegivel_tambem_recomeca_o_ctrl_z_vazio(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    estado = Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO
    estado.write_text("{ isto nao e json", encoding="utf-8")
    acoes_antes = (estado.parent / ARQUIVO_ACOES).read_bytes()

    janela.abrir_livro(str(livro))
    _analisar(janela)

    assert not janela.acoes.pode_desfazer
    assert _copias(estado.parent, "acoes")[0].read_bytes() == acoes_antes


def test_quando_o_trabalho_combina_o_historico_continua_voltando(janela, pasta):
    """O caminho normal nao muda: reabrir sem mexer em nada traz o Ctrl+Z."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro))
    _analisar(janela)
    assert not janela.avisos
    assert janela.acoes.pode_desfazer
    assert "pagina 2" in janela.acoes.descricao_desfazer()
    assert not _copias(Path(janela.resumo.pasta), "acoes")


def test_mudar_dividir_e_voltar_como_estava_nao_recomeca(janela, pasta):
    """Desmarcar e marcar de novo antes do Conferir: o trabalho combina, e o
    historico fica (inclusive o que estava so na memoria)."""
    livro = _pdf_de_folhas_duplas(pasta)
    _conferir_com_o_livro_dividido_e_mexer(janela, livro)
    janela._sair_da_conferencia()
    janela.tela_opcoes.cx_dividir.setChecked(False)
    janela.tela_opcoes.cx_dividir.setChecked(True)
    _analisar(janela)
    assert not janela.avisos
    assert len(janela.acoes.feitas) == 3
    _ctrl_z(janela)
    assert janela.projeto.paginas[0].filtro == PRETO_E_BRANCO


# --- 3. HistoricoAcoes.recomecar, direto ----------------------------------------------


def _historico_com_tres_acoes(pasta_do_projeto: Path) -> tuple[HistoricoAcoes, Projeto]:
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.folhas = [ConfigFolha(indice=i) for i in range(2)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i) for i in range(2)]
    historico = HistoricoAcoes(pasta_do_projeto)
    for nome, giro in (("A", 90), ("B", 180), ("C", 270)):
        acao = montar_acao(projeto, "girar", "folha", [0], {"rotacao": giro}, nome)
        aplicar(projeto, acao, acao.depois)
        historico.registrar(acao)
    historico.desfazer(projeto)                     # C fica no refazer
    return historico, projeto


def test_recomecar_com_a_copia_do_trabalho_tira_o_historico_do_arquivo(tmp_path):
    historico, _ = _historico_com_tres_acoes(tmp_path)
    (tmp_path / projetos.ARQUIVO_ESTADO).write_text("{}", encoding="utf-8")
    acoes_antes = (tmp_path / ARQUIVO_ACOES).read_bytes()
    copia = projetos.guardar_copia_do_trabalho(projetos.Resumo(pasta=str(tmp_path)))

    assert historico.recomecar(copia) is True
    assert not historico.pode_desfazer and not historico.pode_refazer
    assert not (tmp_path / ARQUIVO_ACOES).exists()
    assert not (tmp_path / ARQUIVO_POSICAO).exists()
    assert _copias(tmp_path, "acoes")[0].read_bytes() == acoes_antes
    reaberto = HistoricoAcoes(tmp_path)
    reaberto.carregar()
    assert not reaberto.pode_desfazer and not reaberto.pode_refazer


def test_recomecar_sem_a_copia_do_trabalho_guarda_o_historico_sozinho(tmp_path):
    """Sem projeto.json (nao ha copia do trabalho), o historico antigo vai
    para acoes.antigo-historico-*, inteiro."""
    historico, _ = _historico_com_tres_acoes(tmp_path)
    acoes_antes = (tmp_path / ARQUIVO_ACOES).read_bytes()
    posicao_antes = (tmp_path / ARQUIVO_POSICAO).read_bytes()

    assert historico.recomecar(None) is True
    assert not historico.pode_desfazer
    assert not (tmp_path / ARQUIVO_ACOES).exists()
    [acoes] = tmp_path.glob("acoes.antigo-historico-*.jsonl")
    [posicao] = tmp_path.glob("posicao.antigo-historico-*.json")
    assert acoes.read_bytes() == acoes_antes
    assert posicao.read_bytes() == posicao_antes


def test_recomecar_com_copia_diferente_do_arquivo_nao_confia_nela(tmp_path):
    """A copia do trabalho nao bate com o historico (copia de outro momento):
    o historico e guardado sozinho, para nada se perder."""
    historico, _ = _historico_com_tres_acoes(tmp_path)
    (tmp_path / projetos.ARQUIVO_ESTADO).write_text("{}", encoding="utf-8")
    copia = projetos.guardar_copia_do_trabalho(projetos.Resumo(pasta=str(tmp_path)))
    acoes_agora = b'{"mudou": 1}\n'
    (tmp_path / ARQUIVO_ACOES).write_bytes(acoes_agora)

    assert historico.recomecar(copia) is True
    [guardado] = tmp_path.glob("acoes.antigo-historico-*.jsonl")
    assert guardado.read_bytes() == acoes_agora


def test_recomecar_sem_poder_guardar_nao_apaga_nada(tmp_path, monkeypatch):
    """Nem a copia nem o guardar deram certo: o arquivo fica como estava, e
    o historico desta conferencia fica so na memoria (nao se mistura com o
    antigo no arquivo)."""
    historico, projeto = _historico_com_tres_acoes(tmp_path)
    acoes_antes = (tmp_path / ARQUIVO_ACOES).read_bytes()
    posicao_antes = (tmp_path / ARQUIVO_POSICAO).read_bytes()

    def recusar(*_a, **_k):
        raise OSError("sem permissao")

    monkeypatch.setattr(Path, "rename", recusar)
    assert historico.recomecar(None) is False
    assert not historico.pode_desfazer
    assert (tmp_path / ARQUIVO_ACOES).read_bytes() == acoes_antes
    assert (tmp_path / ARQUIVO_POSICAO).read_bytes() == posicao_antes
    # a acao nova nao vai para o fim do arquivo antigo
    acao = montar_acao(projeto, "girar", "folha", [1], {"rotacao": 90}, "D")
    aplicar(projeto, acao, acao.depois)
    historico.registrar(acao)
    assert historico.descricao_desfazer() == "Desfazer: D"
    assert (tmp_path / ARQUIVO_ACOES).read_bytes() == acoes_antes


def test_recomecar_sem_historico_no_disco_nao_cria_nada(tmp_path):
    historico = HistoricoAcoes(tmp_path)
    assert historico.recomecar(None) is True
    assert list(tmp_path.iterdir()) == []
