"""O mesmo PDF, com o caminho escrito de outro jeito, e o MESMO livro.

Bug GRAVE achado pelo verificador em 29/09/2026 (Lista de bugs; print
relatorios/conferir/fase1-2026-09-29-1826/verificador/t11-abrir-perdeu-o-trabalho.jpg):
abrindo o PDF pela associacao de arquivo do Windows (caminho com `\\`) e
depois pela caixa "Abrir" ou arrastando (caminho com `/`), aparecia "Voce
mudou as opcoes desde a ultima vez..." sem nada ter mudado, e o trabalho
salvo sumia. Causa: `projetos.combina_com` comparava o TEXTO do caminho.

O que se cobra aqui (teste de maquina):

    - `projetos.mesmo_arquivo` reconhece o mesmo arquivo com `\\` ou `/`,
      maiusculas diferentes, caminho relativo, `..` e letra de unidade
      minuscula; e NAO confunde dois arquivos diferentes;
    - `combina_com` aceita o trabalho salvo do mesmo livro escrito de outro
      jeito (e continua recusando livro de outro tamanho);
    - na janela de verdade: projeto salvo de um jeito e aberto de outro volta
      com paginas, filtros, alertas, conferidas e o Historico de acoes, sem o
      aviso "Voce mudou as opcoes...". Nos dois sentidos (`\\` -> `/` e
      `/` -> `\\`), e tambem por maiuscula diferente;
    - o Historico de trabalhos concluidos (historico.json) nao ganha linha
      repetida para o mesmo PDF de saida escrito de outro jeito.

Pasta de dados propria: LOCALAPPDATA aponta para uma pasta dentro de
saida_teste\\, para NAO criar projetos na pasta de dados real do Samuel.
Cada teste usa a sua subpasta, apagada no fim (foi criada pelo proprio teste).
"""

from __future__ import annotations

import os
import shutil
import time
import uuid
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

import historico  # noqa: E402
import projetos  # noqa: E402
from core import pipeline  # noqa: E402
from core.filtros import MAGICO_PRO, PRETO_E_BRANCO  # noqa: E402
from modelos import Acao, ConfigFolha, ConfigPagina, Projeto  # noqa: E402

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
PASTA_DOS_TESTES = RAIZ_DO_PROJETO / "saida_teste" / "pytest_mesmo_livro"

# Um alerta qualquer, que a analise nao poe nem tira sozinha (o "conferir o
# fundo tirado" seria tirado ao abrir, porque a pagina nao esta nesse filtro).
ALERTA_DE_TESTE = "alerta de teste: conferir esta pagina"


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def pasta(monkeypatch):
    """Pasta propria do teste em saida_teste\\, com LOCALAPPDATA apontando
    para ela: projetos, historico.json e configuracoes nascem ali."""
    aqui = PASTA_DOS_TESTES / uuid.uuid4().hex[:10]
    (aqui / "dados").mkdir(parents=True)
    monkeypatch.setenv("LOCALAPPDATA", str(aqui / "dados"))
    monkeypatch.delenv("APPDATA", raising=False)
    assert projetos.pasta_dos_projetos().is_relative_to(aqui)
    yield aqui
    # Limpeza do que o proprio teste criou. No Windows nao se apaga a pasta
    # em que o programa "esta" (o teste do caminho relativo entra nela) nem
    # arquivo que uma tarefa de fundo ainda fecha: sai dela e tenta de novo.
    if Path.cwd().is_relative_to(aqui):
        os.chdir(RAIZ_DO_PROJETO)
    # O servidor de paginas (core/paginas_em_outro_processo.py) pode estar com
    # o PDF do teste aberto (fecha sozinho em meio segundo): solta ja.
    from core.paginas_em_outro_processo import soltar_livro

    soltar_livro(None)
    for _tentativa in range(30):
        shutil.rmtree(aqui, ignore_errors=True)
        if not aqui.exists():
            break
        QApplication.processEvents()
        time.sleep(0.1)
    try:
        PASTA_DOS_TESTES.rmdir()             # so se ficou vazia
    except OSError:
        pass


def _pdf(pasta: Path, folhas: int = 4) -> Path:
    """Um PDF pequeno de verdade, com texto (a analise precisa abrir)."""
    (pasta / "livros").mkdir(exist_ok=True)
    caminho = pasta / "livros" / "Livro de Teste.pdf"
    doc = fitz.open()
    for i in range(folhas):
        pagina = doc.new_page(width=400, height=560)
        pagina.insert_text((40, 60), f"folha {i}", fontsize=14)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _com_barra(caminho: Path) -> str:
    """O caminho como a caixa "Abrir" do Qt e o arrastar entregam: com `/`."""
    return str(caminho).replace("\\", "/")


def _com_contrabarra(caminho: Path) -> str:
    """O caminho como a associacao de arquivo do Windows entrega: com `\\`."""
    return str(caminho).replace("/", "\\")


def _projeto(caminho: str, paginas: int = 4) -> Projeto:
    p = Projeto(caminho_entrada=caminho, nome=Path(caminho).stem)
    p.folhas = [ConfigFolha(indice=i) for i in range(paginas)]
    p.paginas = [ConfigPagina(indice=i, folha=i) for i in range(paginas)]
    return p


# --- mesmo_arquivo ------------------------------------------------------------------


def test_barra_e_contrabarra_sao_o_mesmo_arquivo(pasta):
    livro = _pdf(pasta)
    assert projetos.mesmo_arquivo(_com_contrabarra(livro), _com_barra(livro))


@pytest.mark.skipif(os.name != "nt", reason="so o Windows ignora maiusculas")
def test_maiusculas_diferentes_sao_o_mesmo_arquivo(pasta):
    livro = str(_pdf(pasta))
    assert projetos.mesmo_arquivo(livro, livro.upper())
    assert projetos.mesmo_arquivo(livro, livro.lower())


@pytest.mark.skipif(os.name != "nt", reason="letra de unidade e do Windows")
def test_letra_de_unidade_minuscula_e_o_mesmo_arquivo(pasta):
    livro = str(_pdf(pasta))
    trocada = livro[0].swapcase() + livro[1:]
    assert trocada != livro
    assert projetos.mesmo_arquivo(livro, trocada)


def test_caminho_relativo_e_o_mesmo_arquivo(pasta, monkeypatch):
    livro = _pdf(pasta)
    monkeypatch.chdir(pasta)
    assert projetos.mesmo_arquivo(str(livro), os.path.join("livros", livro.name))


def test_caminho_com_ponto_ponto_e_o_mesmo_arquivo(pasta):
    livro = _pdf(pasta)
    (pasta / "outra").mkdir()
    volta = str(pasta / "outra" / ".." / "livros" / livro.name)
    assert projetos.mesmo_arquivo(str(livro), volta)


def test_arquivos_diferentes_nao_sao_o_mesmo(pasta):
    livro = _pdf(pasta)
    outro = pasta / "livros" / "Outro.pdf"
    shutil.copy(livro, outro)
    assert not projetos.mesmo_arquivo(str(livro), str(outro))
    assert not projetos.mesmo_arquivo(str(livro), "")
    assert not projetos.mesmo_arquivo("", str(livro))


def test_arquivo_que_nao_existe_ainda_compara_pela_forma(pasta):
    """Sem o arquivo no disco (livro que sumiu) ainda se compara a forma."""
    sumido = pasta / "livros" / "sumiu.pdf"
    assert projetos.mesmo_arquivo(_com_contrabarra(sumido), _com_barra(sumido))
    assert not projetos.mesmo_arquivo(str(sumido), str(pasta / "livros" / "outro.pdf"))


# --- combina_com ----------------------------------------------------------------------


def test_combina_com_o_mesmo_livro_escrito_com_a_outra_barra(pasta):
    livro = _pdf(pasta)
    salvo = _projeto(_com_contrabarra(livro))
    agora = _projeto(_com_barra(livro))
    assert projetos.combina_com(salvo, agora)
    assert projetos.combina_com(agora, salvo)


@pytest.mark.skipif(os.name != "nt", reason="so o Windows ignora maiusculas")
def test_combina_com_o_mesmo_livro_em_maiusculas(pasta):
    livro = str(_pdf(pasta))
    assert projetos.combina_com(_projeto(livro), _projeto(livro.upper()))


def test_combina_com_continua_recusando_livro_de_outro_tamanho(pasta):
    livro = _pdf(pasta)
    salvo = _projeto(_com_contrabarra(livro), paginas=4)
    agora = _projeto(_com_barra(livro), paginas=8)
    assert not projetos.combina_com(salvo, agora)


def test_combina_com_continua_recusando_outro_arquivo(pasta):
    livro = _pdf(pasta)
    outro = pasta / "livros" / "Outro.pdf"
    shutil.copy(livro, outro)
    assert not projetos.combina_com(_projeto(str(livro)), _projeto(str(outro)))


# --- na janela de verdade --------------------------------------------------------------


@pytest.fixture
def janela(app, pasta, monkeypatch):
    """A janela principal, com a pasta de dados do teste e os avisos anotados
    numa lista (em vez da caixa modal, que pararia o teste)."""
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.avisos = []
    monkeypatch.setattr(janela, "avisar",
                        lambda mensagem, titulo="": janela.avisos.append(mensagem))
    yield janela
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    if janela.previas is not None:
        janela.previas.parar()
    janela.tela_opcoes.folhear.fechar()
    janela.close()


def _analisar(janela) -> None:
    """O que o "Conferir" faz, sem a tarefa em segundo plano."""
    janela.projeto.detectar_regioes = False
    janela._analise_pronta(pipeline.analisar_projeto(janela.projeto))


def _trabalhar_e_fechar(janela, caminho: str) -> None:
    """Abre o livro por `caminho`, confere, mexe e grava - como o Kaique."""
    janela.abrir_livro(caminho)
    _analisar(janela)
    paginas = janela.projeto.paginas
    assert len(paginas) == 4
    paginas[1].filtro = MAGICO_PRO
    paginas[1].intensidade_magico = 80
    paginas[2].filtro = PRETO_E_BRANCO
    paginas[2].recorte = (0.1, 0.1, 0.8, 0.8)
    paginas[3].alertas = [ALERTA_DE_TESTE]
    for pagina in paginas[:3]:
        pagina.revisada = True
    janela.acoes.registrar(Acao.nova(
        "filtro", "pagina", [1], {"filtro": "original"}, {"filtro": MAGICO_PRO},
        "Trocar o filtro da pagina 2"))
    janela._salvar_agora()
    janela.previas.parar()
    janela.previas = None
    # Como ao fechar o programa (closeEvent): a tira de miniaturas para, e
    # nada mais fica com o PDF aberto (o teste move e copia o arquivo).
    janela.tela_conferir.tira.parar()
    janela.tela_opcoes.folhear.fechar()


def _conferir_que_o_trabalho_voltou(janela, caminho_aberto: str) -> None:
    paginas = janela.projeto.paginas
    assert not janela.avisos, janela.avisos      # nem "recomecei a conferência"
    assert paginas[1].filtro == MAGICO_PRO, "o filtro salvo se perdeu"
    assert paginas[1].intensidade_magico == 80
    assert paginas[2].filtro == PRETO_E_BRANCO
    assert paginas[2].recorte == (0.1, 0.1, 0.8, 0.8), "o corte salvo se perdeu"
    assert ALERTA_DE_TESTE in paginas[3].alertas, "o alerta salvo se perdeu"
    assert [p.revisada for p in paginas] == [True, True, True, False]
    assert janela.acoes.pode_desfazer, "o Historico de acoes se perdeu"
    assert "pagina 2" in janela.acoes.descricao_desfazer()
    # O projeto passa a apontar para o caminho que acabou de ser aberto (que
    # existe e funciona agora), e nao para a forma antiga.
    assert janela.projeto.caminho_entrada == caminho_aberto
    assert len(projetos.listar()) == 1, "abriu um projeto novo ao lado do antigo"


def test_salvo_com_contrabarra_e_aberto_com_barra_mantem_o_trabalho(janela, pasta):
    """O caso do verificador: associacao de arquivo, depois "Abrir"."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, _com_contrabarra(livro))
    janela.abrir_livro(_com_barra(livro))
    _analisar(janela)
    _conferir_que_o_trabalho_voltou(janela, _com_barra(livro))


def test_salvo_com_barra_e_aberto_com_contrabarra_mantem_o_trabalho(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, _com_barra(livro))
    janela.abrir_livro(_com_contrabarra(livro))
    _analisar(janela)
    _conferir_que_o_trabalho_voltou(janela, _com_contrabarra(livro))


@pytest.mark.skipif(os.name != "nt", reason="so o Windows ignora maiusculas")
def test_salvo_e_aberto_com_maiusculas_diferentes_mantem_o_trabalho(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro).upper())
    _analisar(janela)
    _conferir_que_o_trabalho_voltou(janela, str(livro).upper())


def test_continuar_depois_de_abrir_de_outro_jeito_mantem_o_trabalho(janela, pasta,
                                                                  monkeypatch):
    """Salvo com `\\`, reaberto com `/` (a forma nova vai para o resumo) e
    depois pelo "continuar" da tela inicial: o trabalho segue la."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, _com_contrabarra(livro))
    janela.abrir_livro(_com_barra(livro))
    _analisar(janela)
    janela._salvar_agora()
    janela.previas.parar()
    janela.previas = None
    janela.tela_opcoes.folhear.fechar()

    monkeypatch.setattr(janela, "analisar", lambda: None)
    janela._continuar_projeto(projetos.achar_por_assinatura(str(livro)))
    _analisar(janela)
    _conferir_que_o_trabalho_voltou(janela, _com_barra(livro))


def test_projeto_antigo_gravado_com_contrabarra_abre_com_o_trabalho(janela, pasta):
    """Os projetos reais do Samuel estao misturados (o Palatino foi gravado
    com `\\`). Um projeto.json escrito a mao, como o programa antigo gravava,
    abre pelo "Abrir" (com `/`) e o trabalho volta."""
    import json

    livro = _pdf(pasta)
    antigo = _projeto(_com_contrabarra(livro))
    for i, folha in enumerate(antigo.folhas):
        folha.indice = i
    resumo = projetos.criar(antigo, total_paginas=4)
    # O trabalho de antes, gravado com a contrabarra (formato de sempre).
    dados = pipeline.analisar_projeto(
        Projeto(caminho_entrada=_com_contrabarra(livro), nome=livro.stem,
                detectar_regioes=False)).para_dicionario()
    assert "\\" in dados["caminho_entrada"]
    dados["paginas"][1]["filtro"] = MAGICO_PRO
    dados["paginas"][1]["intensidade_magico"] = 80
    dados["paginas"][2]["filtro"] = PRETO_E_BRANCO
    dados["paginas"][2]["recorte"] = [0.1, 0.1, 0.8, 0.8]
    dados["paginas"][3]["alertas"] = [ALERTA_DE_TESTE]
    for i in range(4):
        dados["paginas"][i]["revisada"] = i < 3
    (Path(resumo.pasta) / projetos.ARQUIVO_ESTADO).write_text(
        json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    acao = Acao.nova("filtro", "pagina", [1], {"filtro": "original"},
                     {"filtro": MAGICO_PRO}, "Trocar o filtro da pagina 2")
    (Path(resumo.pasta) / "acoes.jsonl").write_text(
        json.dumps(acao.para_dicionario(), ensure_ascii=False) + "\n", encoding="utf-8")

    janela.abrir_livro(_com_barra(livro))
    _analisar(janela)
    _conferir_que_o_trabalho_voltou(janela, _com_barra(livro))


# --- historico de trabalhos concluidos --------------------------------------------------


def test_historico_nao_repete_o_mesmo_pdf_de_saida_escrito_de_outro_jeito(pasta):
    saida = pasta / "saida" / "Livro de Teste.pdf"
    saida.parent.mkdir()
    saida.write_bytes(b"%PDF-1.4 teste")
    primeiro = _projeto(str(_pdf(pasta)))
    primeiro.caminho_saida = _com_contrabarra(saida)
    historico.registrar(primeiro, 4)
    segundo = _projeto(primeiro.caminho_entrada)
    segundo.caminho_saida = _com_barra(saida)
    historico.registrar(segundo, 4)
    entradas = historico.carregar()
    assert len(entradas) == 1
    assert entradas[0].caminho_saida == _com_barra(saida)    # fica a mais nova
