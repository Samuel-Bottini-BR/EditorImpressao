"""O salvamento automático, ligado no programa de verdade.

O módulo `projetos` já tinha teste. Este cobre o que faltava: que a **janela**
chama esse módulo. Um sistema de projetos que ninguém chama protege exatamente
zero páginas — quem conferir 80 e fechar perde tudo igual a antes.

O caso que manda em todos: **fechar no meio da conferência e reabrir devolve o
trabalho.**
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

import projetos  # noqa: E402
from historico_acoes import HistoricoAcoes  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    monkeypatch.setattr(projetos.historico, "carregar", lambda: [])
    return pasta


@pytest.fixture
def livro(tmp_path):
    caminho = tmp_path / "livro.pdf"
    doc = fitz.open()
    for i in range(8):
        pagina = doc.new_page(width=400, height=560)
        pagina.insert_text((40, 60), f"folha {i}", fontsize=14)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _projeto(caminho, paginas: int = 8) -> Projeto:
    p = Projeto(caminho_entrada=str(caminho), nome=caminho.stem)
    p.folhas = [ConfigFolha(indice=i) for i in range(paginas)]
    p.paginas = [ConfigPagina(indice=i, folha=i) for i in range(paginas)]
    return p


# --- o caso que manda em todos ---------------------------------------------


def test_fechar_no_meio_e_reabrir_devolve_o_trabalho(raiz, livro):
    """Conferiu, mexeu no filtro, cortou, apagou uma - e fechou."""
    projeto = _projeto(livro)
    resumo = projetos.criar(projeto, total_paginas=8)

    projeto.paginas[2].filtro = "magico_pro"
    projeto.paginas[2].intensidade_magico = 80
    projeto.paginas[3].recorte = (0.1, 0.1, 0.8, 0.8)
    projeto.paginas[4].angulo_manual = -1.5
    projeto.paginas[5].apagada = True
    for pagina in projeto.paginas[:6]:
        pagina.revisada = True

    projetos.salvar_estado(resumo, projeto)
    projetos.atualizar(resumo, projeto, pagina_atual=5)

    # --- o programa fecha e abre de novo ---
    de_volta = projetos.ler_resumo(resumo.pasta)
    salvo = projetos.carregar_estado(de_volta)

    assert salvo is not None, "o trabalho não voltou"
    assert salvo.paginas[2].filtro == "magico_pro"
    assert salvo.paginas[2].intensidade_magico == 80
    assert salvo.paginas[3].recorte == (0.1, 0.1, 0.8, 0.8)
    assert salvo.paginas[4].angulo_manual == -1.5
    assert salvo.paginas[5].apagada is True
    assert sum(1 for p in salvo.paginas if p.revisada) == 6
    assert de_volta.pagina_atual == 5, "não voltou na página em que parou"


def test_a_marcacao_da_pagina_tambem_volta(raiz, livro):
    from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao

    projeto = _projeto(livro)
    resumo = projetos.criar(projeto, total_paginas=8)

    selecao = Selecao()
    selecao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO,
                               pontos=[(0.1, 0.2), (0.9, 0.7)], origem=MAO))
    projeto.paginas[1].guardar_selecao(selecao)
    projetos.salvar_estado(resumo, projeto)

    salvo = projetos.carregar_estado(resumo)
    voltou = salvo.paginas[1].obter_selecao()
    assert not voltou.vazia, "a marcação feita à mão se perdeu"
    assert voltou.regioes[0].tipo == GRAVURA


# --- a trava que impede estragar o trabalho ---------------------------------


def test_trabalho_salvo_nao_e_aplicado_num_livro_de_outro_tamanho(raiz, livro):
    """Trocar "dividir folhas ao meio" muda quais páginas existem."""
    salvo = _projeto(livro, paginas=8)
    agora = _projeto(livro, paginas=16)          # dividiu as folhas ao meio
    assert not projetos.combina_com(salvo, agora)


def test_trabalho_salvo_combina_com_o_mesmo_livro(raiz, livro):
    assert projetos.combina_com(_projeto(livro), _projeto(livro))


def test_abrir_o_mesmo_livro_de_novo_acha_o_projeto(raiz, livro):
    projeto = _projeto(livro)
    resumo = projetos.criar(projeto, total_paginas=8)
    achado = projetos.achar_por_assinatura(str(livro))
    assert achado is not None and achado.pasta == resumo.pasta


def test_livro_diferente_nao_acha_projeto_nenhum(raiz, livro, tmp_path):
    projetos.criar(_projeto(livro), total_paginas=8)
    outro = tmp_path / "outro.pdf"
    outro.write_bytes(b"Z" * 300_000)
    assert projetos.achar_por_assinatura(str(outro)) is None


# --- a gravacao nao pode corromper -----------------------------------------


def test_gravar_por_cima_nao_deixa_o_projeto_pela_metade(raiz, livro):
    """Grava num arquivo ao lado e só então troca."""
    projeto = _projeto(livro)
    resumo = projetos.criar(projeto, total_paginas=8)
    projetos.salvar_estado(resumo, projeto)

    from pathlib import Path

    caminho = Path(resumo.pasta) / projetos.ARQUIVO_ESTADO
    antes = caminho.read_text(encoding="utf-8")

    projeto.paginas[0].filtro = "melhorar"
    projetos.salvar_estado(resumo, projeto)

    assert caminho.read_text(encoding="utf-8") != antes
    assert not (Path(resumo.pasta) / (projetos.ARQUIVO_ESTADO + ".novo")).exists(), \
        "sobrou o arquivo temporário"


def test_estado_ilegivel_nao_derruba_a_abertura(raiz, livro):
    from pathlib import Path

    resumo = projetos.criar(_projeto(livro), total_paginas=8)
    (Path(resumo.pasta) / projetos.ARQUIVO_ESTADO).write_text(
        "{ isto nao e json", encoding="utf-8")
    assert projetos.carregar_estado(resumo) is None


# --- a janela chama mesmo o modulo ------------------------------------------


def test_a_tela_de_conferir_avisa_quando_o_trabalho_muda(app, raiz, livro):
    """Se este sinal parar de sair, o salvamento morre em silêncio."""
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    projeto = _projeto(livro)
    resumo = projetos.criar(projeto, total_paginas=8)

    tela = TelaConferir()
    previas = GerenciadorPrevias(str(livro), projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(resumo.pasta), previas)

    avisos = []
    tela.trabalho_mudou.connect(lambda: avisos.append(1))
    tela.atualizar()
    previas.parar()

    assert avisos, "a tela mudou e ninguém foi avisado - o trabalho não seria gravado"


def test_a_janela_liga_o_salvamento_na_tela(app):
    """A ligação em si: sem ela, projetos.py protege zero páginas."""
    import inspect

    from ui.janela_principal import JanelaPrincipal

    fonte = inspect.getsource(JanelaPrincipal)
    assert "trabalho_mudou.connect" in fonte, "a tela avisa e ninguém escuta"
    assert "salvar_estado" in inspect.getsource(JanelaPrincipal._salvar_agora)
    assert "_salvar_agora" in inspect.getsource(JanelaPrincipal.closeEvent), \
        "fechar a janela não grava"


def test_nao_ha_pergunta_de_salvar_em_lugar_nenhum():
    """Nenhum diálogo "quer salvar?" - critério 13.

    Olha só o que chega ao usuário: os textos entre aspas. Comentário e
    docstring ficam de fora de propósito - há comentário no código explicando
    justamente que esta pergunta não existe, e ele não é um diálogo.
    """
    import ast
    from pathlib import Path

    raiz = Path(__file__).resolve().parent.parent
    frases = ("quer salvar", "deseja salvar", "salvar antes de sair",
              "salvar alterações", "salvar as alterações")

    suspeitas = []
    for arquivo in list((raiz / "ui").rglob("*.py")) + [raiz / "main.py"]:
        try:
            arvore = ast.parse(arquivo.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:  # pragma: no cover
            continue
        # Docstring e um texto solto, sozinho numa instrucao. Nao vai para
        # tela nenhuma, e ha docstring no codigo explicando justamente que
        # esta pergunta nao existe.
        docstrings = {
            id(no.value) for no in ast.walk(arvore)
            if isinstance(no, ast.Expr) and isinstance(no.value, ast.Constant)
        }
        for no in ast.walk(arvore):
            if not (isinstance(no, ast.Constant) and isinstance(no.value, str)):
                continue
            if id(no) in docstrings:
                continue
            texto = no.value.lower()
            for frase in frases:
                if frase in texto:
                    suspeitas.append(f"{arquivo.name}:{no.lineno}: {frase}")
    assert not suspeitas, f"pergunta de salvar encontrada: {suspeitas}"
