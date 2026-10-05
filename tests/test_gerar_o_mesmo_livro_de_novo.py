"""Gerar o mesmo livro de novo nao pode travar a janela "Confirmar e processar".

Bug da Lista de bugs do plano (02/10/2026, achado na janela real; o Samuel
autorizou consertar em 05/10): depois de gerar o PDF uma vez, o
`projeto.caminho_saida` guarda o caminho do ARQUIVO (`...\\saida\\pronto.pdf`,
gravado em `JanelaPrincipal.processar`). A janela "Confirmar e processar"
(ui/janela_confirmar.py) passava esse caminho de arquivo para
`SeletorDestino.definir`, que espera a PASTA. Resultado: "Salvar em:" mostrava
o caminho do PDF antigo, aparecia "Esse caminho nao e uma pasta." e o botao
"Processar" ficava apagado; so destravava com "Escolher pasta".

Pior, escondido: se o PDF ainda nao existia (processamento cancelado depois
de o caminho ja estar gravado), `configuracoes.pode_gravar_em` CRIAVA uma
pasta chamada `pronto.pdf` no lugar do arquivo.

O que se cobra aqui:

    - livro ja gerado: a janela vem com a pasta do PDF antigo e o mesmo nome,
      "Processar" aceso, e a faixa "Ja existe um arquivo..." aparece (a caixa
      "substituir / salvar como (2)" continua sendo a que decide);
    - caminho gravado sem PDF (processamento cancelado): mesma pasta, mesmo
      nome, "Processar" aceso e nenhuma pasta `pronto.pdf` criada;
    - livro nunca gerado: pasta sugerida e nome sugerido, como sempre;
    - a pasta do PDF antigo sumiu: volta a pasta sugerida (como
      configuracoes.pasta_de_saida_sugerida faz com a ultima pasta), o nome
      fica, e a pasta sumida nao e recriada;
    - projeto antigo que guardou uma PASTA no caminho_saida: ela vale como
      pasta, com o nome sugerido;
    - o caminho inteiro, na janela de verdade: gerar, reabrir o mesmo livro,
      gerar de novo -> "Processar" aceso, a caixa "Ja existe..." aparece e o
      "salvar como (2)" gera `pronto (2).pdf` sem tocar no antigo.

Nada aparece na tela (tests/conftest.py). Pasta de dados propria em
saida_teste\\ (fixtures de tests/test_mesmo_livro_outro_caminho.py).
"""

from __future__ import annotations

from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QDialog  # noqa: E402

import configuracoes  # noqa: E402
from tests.test_ja_existe_arquivo_com_esse_nome import (  # noqa: E402
    _esperar_o_fim,
    _escolher_na_caixa,
    _livro_conferido,
    _paginas,
    _pdf_antigo,
)
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _pdf,
    app,
    janela,
    pasta,
)


def _projeto_de_uma_pagina(pasta: Path):
    from modelos import ConfigFolha, ConfigPagina, Projeto

    projeto = Projeto(caminho_entrada=str(pasta / "x.pdf"), nome="x")
    projeto.folhas = [ConfigFolha(indice=0)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0, revisada=True)]
    return projeto


def _janela_de_confirmar(projeto, nome_sugerido: str = "sugerido.pdf"):
    from ui.janela_confirmar import JanelaConfirmar

    return JanelaConfirmar(projeto, nome_sugerido)


# --- a janela "Confirmar e processar", sozinha ----------------------------------


def test_livro_ja_gerado_vem_com_a_pasta_e_processar_aceso(app, pasta):
    antigo = pasta / "saida" / "pronto.pdf"
    _pdf_antigo(antigo, "o antigo")
    projeto = _projeto_de_uma_pagina(pasta)
    projeto.caminho_saida = str(antigo)

    janela = _janela_de_confirmar(projeto)

    assert janela.destino.pasta == antigo.parent, "a pasta nao e a do PDF antigo"
    assert janela.destino.nome == "pronto.pdf", "o nome escolhido antes se perdeu"
    assert janela.botao_processar.isEnabled(), janela.botao_processar.toolTip()
    assert "não é uma pasta" not in janela.destino.aviso.text()
    # a faixa "ja existe" continua avisando; quem decide e a caixa seguinte
    assert janela.aviso_existe.isVisibleTo(janela)
    assert "pronto.pdf" in janela.aviso_existe.rotulo.text()
    assert janela.caminho == antigo
    assert antigo.is_file(), "o PDF antigo foi mexido"


def test_caminho_gravado_sem_pdf_nao_vira_pasta(app, pasta):
    """Processamento cancelado: o caminho ficou gravado, o PDF nao existe."""
    nao_gerado = pasta / "saida" / "pronto.pdf"
    nao_gerado.parent.mkdir(parents=True)
    projeto = _projeto_de_uma_pagina(pasta)
    projeto.caminho_saida = str(nao_gerado)

    janela = _janela_de_confirmar(projeto)

    assert janela.destino.pasta == nao_gerado.parent
    assert janela.destino.nome == "pronto.pdf"
    assert janela.botao_processar.isEnabled(), janela.botao_processar.toolTip()
    assert not janela.aviso_existe.isVisibleTo(janela)
    assert not nao_gerado.exists(), "nasceu uma PASTA com o nome do PDF"


def test_livro_nunca_gerado_usa_a_pasta_e_o_nome_sugeridos(app, pasta):
    projeto = _projeto_de_uma_pagina(pasta)
    assert not projeto.caminho_saida

    janela = _janela_de_confirmar(projeto, "Meu livro.pdf")

    assert janela.destino.pasta == configuracoes.pasta_de_saida_sugerida()
    assert janela.destino.nome == "Meu livro.pdf"


def test_pasta_do_pdf_antigo_sumiu_volta_a_sugerida(app, pasta, monkeypatch):
    sugerida = pasta / "sugerida"
    sugerida.mkdir()
    monkeypatch.setattr(configuracoes, "pasta_de_saida_sugerida", lambda: sugerida)
    sumida = pasta / "pendrive-que-saiu" / "pronto.pdf"
    projeto = _projeto_de_uma_pagina(pasta)
    projeto.caminho_saida = str(sumida)

    janela = _janela_de_confirmar(projeto)

    assert janela.destino.pasta == sugerida
    assert janela.destino.nome == "pronto.pdf"
    assert janela.botao_processar.isEnabled(), janela.botao_processar.toolTip()
    assert not sumida.parent.exists(), "a pasta que sumiu foi recriada"


def test_projeto_antigo_com_pasta_no_caminho_de_saida(app, pasta):
    """Por garantia: se algum projeto guardou a PASTA, ela vale como pasta."""
    so_a_pasta = pasta / "saida"
    so_a_pasta.mkdir()
    projeto = _projeto_de_uma_pagina(pasta)
    projeto.caminho_saida = str(so_a_pasta)

    janela = _janela_de_confirmar(projeto, "sugerido.pdf")

    assert janela.destino.pasta == so_a_pasta
    assert janela.destino.nome == "sugerido.pdf"
    assert janela.botao_processar.isEnabled()


# --- o caminho inteiro, na janela de verdade -------------------------------------


def _janela_de_confirmar_respondida(monkeypatch, vistas: list, escolher: Path | None):
    """A janela "Confirmar e processar" de verdade, sem aparecer na tela.

    Anota o que ela mostra (pasta, nome, "Processar" aceso?, aviso vermelho)
    e aperta "Processar" como o Kaique - so se o botao estiver aceso; apagado,
    o Kaique so poderia desistir. Na primeira vez, `escolher` faz o papel de
    "Escolher pasta" + digitar o nome."""
    from ui.janela_confirmar import JanelaConfirmar

    def _exec(janela_confirmar):
        if escolher is not None and not vistas:
            janela_confirmar.destino.definir(escolher.parent, escolher.name)
            janela_confirmar._reavaliar()
        vistas.append({
            "pasta": janela_confirmar.destino.pasta,
            "nome": janela_confirmar.destino.nome,
            "processar_aceso": janela_confirmar.botao_processar.isEnabled(),
            "motivo": janela_confirmar.botao_processar.toolTip(),
            "faixa_ja_existe": janela_confirmar.aviso_existe.isVisibleTo(janela_confirmar),
        })
        if janela_confirmar.botao_processar.isEnabled():
            return QDialog.Accepted
        return QDialog.Rejected

    monkeypatch.setattr(JanelaConfirmar, "exec", _exec)


def _parar_o_que_segura_o_pdf(janela) -> None:
    """Como em tests/test_mesmo_livro_outro_caminho._trabalhar_e_fechar."""
    if janela.previas is not None:
        janela.previas.parar()
        janela.previas = None
    janela.tela_conferir.tira.parar()
    janela.tela_opcoes.folhear.fechar()


def test_gerar_reabrir_e_gerar_de_novo(janela, pasta, monkeypatch):
    _livro_conferido(janela, pasta)
    pronto = pasta / "saida" / "pronto.pdf"
    vistas: list = []
    _janela_de_confirmar_respondida(monkeypatch, vistas, escolher=pronto)

    janela.processar()
    _esperar_o_fim(janela)
    assert pronto.is_file() and _paginas(pronto) == 4
    bytes_do_primeiro = pronto.read_bytes()

    # reabrir o mesmo livro (o projeto salvo volta com o caminho de saida)
    _parar_o_que_segura_o_pdf(janela)
    janela.abrir_livro(janela.projeto.caminho_entrada)
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    _analisar(janela)
    assert Path(janela.projeto.caminho_saida) == pronto

    caixas: list = []
    _escolher_na_caixa(monkeypatch, "salvar como", caixas)
    janela.processar()

    # a janela de confirmar ja respondeu (o exec e sincrono): confere antes
    # de esperar, para nao ficar 3 minutos esperando um processamento que nao
    # comecou
    segunda = vistas[1]
    assert segunda["processar_aceso"], f"'Processar' apagado: {segunda['motivo']}"
    assert segunda["pasta"] == pronto.parent
    assert segunda["nome"] == "pronto.pdf"
    assert segunda["faixa_ja_existe"], "a faixa 'Ja existe um arquivo' sumiu"
    assert caixas, "a caixa 'Ja existe um arquivo com esse nome' nao apareceu"
    _esperar_o_fim(janela)
    novo = pasta / "saida" / "pronto (2).pdf"
    assert novo.is_file() and _paginas(novo) == 4
    assert pronto.read_bytes() == bytes_do_primeiro, "o PDF antigo foi mexido"
    assert Path(janela.projeto.caminho_saida) == novo
    assert not janela.avisos, janela.avisos
