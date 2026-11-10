"""Verificador, 09/11/2026: o aviso "Páginas mexidas à mão" (D-004) com mudanças à mão e
com rodadas anteriores do Automático (pedido do Samuel, 09/11: "só verifica se ele vai
perguntar quando eu tiver feito mudanças no manual ou até em outras rodadas de automatico" ·
"pq as vezes eu rodo automatico em só algumas paginas de filtro e depois que montar caderno
em todas, o automatico tem que funcionar certo e não dar erro nessa parte.").

Só testa e anota (não muda o programa). Cada teste grava o que viu em resultados.json, ao
lado deste arquivo; as poucas afirmações (assert) são só do que o Livro já decidiu.

Como rodar (sem janela na tela: o conftest dos testes põe o Qt em offscreen e a pasta de
dados numa pasta de mentira):

    .venv\\Scripts\\python.exe -m pytest relatorios/automatico-mexidas-2026-11-09 -p tests.conftest -q

Caminho de verdade: a janela principal (offscreen), o painel do Automático
(estado_do_automatico), janela.rodar_o_automatico e a pergunta trocada por uma resposta
fixa (monkeypatch de _perguntar_mexidas), como tests/test_decisoes_automatico.py.
"""

from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402
from core import etapas  # noqa: E402
from core.cadernos import montar_ordem  # noqa: E402
from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from core.pipeline import processar  # noqa: E402

AQUI = Path(__file__).resolve().parent
RESULTADOS = AQUI / "resultados.json"
DPI = 150
AMARELADO = (170, 215, 235)            # BGR: papel velho
ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
BOECIO = ACERVO / "Sobre a Consolação da Filosofia - Severino Boécio.pdf"
NOME = {ORIGINAL: "Original", PRETO_E_BRANCO: "Preto e branco", MELHORAR: "Melhorar",
        MAGICO_PRO: "Mágico pro"}


def _anotar(chave: str, valor) -> None:
    dados = {}
    if RESULTADOS.exists():
        dados = json.loads(RESULTADOS.read_text(encoding="utf-8"))
    dados[chave] = valor
    RESULTADOS.write_text(json.dumps(dados, ensure_ascii=False, indent=1, default=str),
                          encoding="utf-8")


# --- o livro de teste: cada página com o seu número em quadradinhos -----------------------

def _pagina(numero: int = 0, giro: float = 0.0, largura: int = 600, altura: int = 840) -> np.ndarray:
    """Papel amarelado com linhas de "texto"; embaixo, `numero` quadradinhos pretos (para
    achar a página dentro do caderno)."""
    img = np.full((altura, largura, 3), AMARELADO, np.uint8)
    for y in range(140, altura - 160, 40):
        img[y:y + 12, 110:largura - 110] = 25
    for k in range(numero):
        x = 60 + 20 * k
        img[730:742, x:x + 12] = 20
    if giro:
        m = cv2.getRotationMatrix2D((largura / 2, altura / 2), giro, 1.0)
        img = cv2.warpAffine(img, m, (largura, altura), borderValue=AMARELADO)
    return img


def _pdf(caminho: Path, imagens) -> str:
    doc = fitz.open()
    for img in imagens:
        ok, buffer = cv2.imencode(".png", img)
        assert ok
        largura, altura = img.shape[1] / DPI * 72, img.shape[0] / DPI * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _livro_do_caso_1(tmp_path: Path) -> str:
    """4 folhas: 1) duas páginas lado a lado (para dividir), 2) página torta 3 graus,
    3) e 4) páginas retas."""
    dupla = np.concatenate([_pagina(1), _pagina(2)], axis=1)
    return _pdf(tmp_path / "caso1.pdf", [dupla, _pagina(3, giro=3.0), _pagina(4), _pagina(5)])


def _livro_de_24(tmp_path: Path, nome: str = "livro24.pdf") -> str:
    """24 páginas soltas; a página n tem n quadradinhos embaixo."""
    caminho = tmp_path / nome
    if not caminho.exists():
        _pdf(caminho, [_pagina(n + 1) for n in range(24)])
    return str(caminho)


def _imagens(caminho: str, dpi: int = DPI) -> list[np.ndarray]:
    with fitz.open(caminho) as doc:
        saida = []
        for pagina in doc:
            pix = pagina.get_pixmap(dpi=dpi, colorspace=fitz.csRGB)
            saida.append(np.frombuffer(pix.samples, np.uint8).reshape(
                pix.height, pix.width, pix.n)[..., :3].copy())
        return saida


def _gerar(janela, tmp_path: Path, nome: str, cadernos: bool | None = None) -> str:
    """O PDF do livro aberto, como o "Confirmar e processar" grava. `cadernos=False`: o
    mesmo livro sem montar os cadernos (para conferir o filtro de cada página)."""
    projeto = copy.copy(janela.projeto)
    if cadernos is not None:
        projeto.montar_cadernos = cadernos
    projeto.caminho_saida = str(tmp_path / f"{nome}.pdf")
    return processar(projeto)


def _quadradinhos(img: np.ndarray) -> int:
    """Quantos quadradinhos pretos há na faixa de baixo da página (o número dela)."""
    altura = img.shape[0]
    faixa = img[int(altura * 0.85):int(altura * 0.90)]
    escuro = (faixa.mean(axis=2) < 110).astype(np.uint8)
    n, _rotulos, stats, _c = cv2.connectedComponentsWithStats(escuro, connectivity=8)
    return int(sum(1 for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= 20))


def _papel(img: np.ndarray) -> float:
    altura, largura = img.shape[:2]
    return float(img[int(altura * 0.06):int(altura * 0.11), int(largura * 0.4):int(largura * 0.6), 2].mean())


def _ordem_dos_cadernos(caminho: str, total: int, por_caderno: int) -> dict:
    """Lê o PDF dos cadernos: para cada lado, o número da página da esquerda e da direita
    (pelos quadradinhos; 0 = em branco) e compara com a conta da dobra."""
    lados = _imagens(caminho, dpi=100)
    esperado = [((l.esquerda + 1) if l.esquerda is not None else 0,
                 (l.direita + 1) if l.direita is not None else 0)
                for l in montar_ordem(total, por_caderno)]
    lido = []
    for img in lados:
        meio = img.shape[1] // 2
        lido.append((_quadradinhos(img[:, :meio]), _quadradinhos(img[:, meio:])))
    numeros = sorted(n for par in lido for n in par if n)
    return {"folhas_do_pdf": len(lados), "esperado": esperado, "lido": lido,
            "na_ordem_certa": lido == esperado,
            "todas_as_paginas_uma_vez": numeros == list(range(1, total + 1))}


# --- a janela -------------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    import projetos

    projetos_dir = tmp_path / "projetos"
    projetos_dir.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: projetos_dir)
    return tmp_path


class _Vigia:
    """O que o programa mostrou: as perguntas da D-004, os avisos, os erros (excepthook e
    erros.log da pasta de dados de mentira)."""

    def __init__(self, janela, monkeypatch, resposta):
        import registro

        self.perguntas: list = []
        self.avisos: list = []
        self.erros: list = []
        self.resposta = resposta
        self.log = registro.caminho_do_log()
        self.log_antes = self.log.read_text(encoding="utf-8") if self.log.exists() else ""

        def perguntar(quantas, juntadas=0):
            from ui.janela_principal import texto_das_mexidas

            self.perguntas.append({"quantas": quantas, "texto": texto_das_mexidas(quantas, juntadas)})
            return self.resposta

        monkeypatch.setattr(janela, "_perguntar_mexidas", perguntar)
        monkeypatch.setattr(janela, "avisar",
                            lambda mensagem, titulo="Um momento": self.avisos.append((titulo, mensagem)))
        antigo = sys.excepthook
        monkeypatch.setattr(sys, "excepthook", lambda *a: (self.erros.append(repr(a[1])), antigo(*a)))

    def log_novo(self) -> str:
        agora = self.log.read_text(encoding="utf-8") if self.log.exists() else ""
        return agora[len(self.log_antes):]


@pytest.fixture
def janela(app, pasta):
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    yield janela
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    janela.close()


def _rodar(janela, etapas_marcadas, alcance="livro", escolhidas=None, opcoes=None, pagina=0) -> bool:
    """O que o Kaique faz no painel Automático: marca as etapas, escolhe onde e roda."""
    from ui.automatico import NAS_ESCOLHIDAS

    estado = janela.estado_do_automatico
    estado.marcadas = set(etapas_marcadas)
    estado.opcoes.update(opcoes or {})
    if alcance == NAS_ESCOLHIDAS:
        estado.escolhidas = list(escolhidas or [])
    estado.alcance = alcance
    janela.tela_conferir.ir_para_pagina(pagina)
    return janela.rodar_o_automatico(esperar=True)


def _estado_da_pagina(janela, pagina) -> dict:
    projeto = janela.projeto
    return {"filtro": pagina.filtro, "filtro_que_vale": etapas.filtro_que_vale(projeto, pagina),
            "recorte": pagina.recorte, "angulo_manual": pagina.angulo_manual,
            "escala": pagina.conteudo_escala, "deslocamento": list(pagina.conteudo_deslocamento),
            "regioes_a_mao": len([r for r in (pagina.selecao or [])
                                  if isinstance(r, dict) and r.get("origem") == "mao"]),
            "mexida_a_mao": list(pagina.mexida_a_mao or []),
            "automatico_so_nela": list(pagina.automatico or []),
            "rotacao_da_folha": janela.projeto.folhas[pagina.folha].rotacao,
            "folha_dividida": bool(janela.projeto.folhas[pagina.folha].dividir),
            "linha_da_folha": janela.projeto.folhas[pagina.folha].posicao_corte,
            "marcas_da_folha": list(janela.projeto.folhas[pagina.folha].mexida_a_mao or [])}


# =========================================================================================
# CASO 1: mudança à mão, uma etapa por vez
# =========================================================================================

def _mexer(janela, etapa: str):
    """Mexe à mão pela tela (os mesmos métodos que os botões chamam). Devolve a página
    (objeto) mexida."""
    from core import dividir_a_mao, girar
    from core.selecao import GRAVURA, Regiao

    tela, projeto = janela.tela_conferir, janela.projeto
    if etapa in ("filtro", "filtro_pb"):
        tela.ir_para_pagina(2)
        tela._escolher_filtro(MELHORAR if etapa == "filtro" else PRETO_E_BRANCO)
        if etapa == "filtro_pb":                   # e a força do preto mexida, como no painel
            tela._registrar("mudar_forca", "pagina", [2], {"forca_preto": 70},
                            "Força do preto da página 3: 70")
        return projeto.paginas[2]
    if etapa == "cortar":
        tela.ir_para_pagina(2)
        tela._mover_recorte((0.1, 0.1, 0.9, 0.9))
        return projeto.paginas[2]
    if etapa == "endireitar":
        tela.ir_para_pagina(1)
        tela._gravar_angulo(1, 1.5)
        return projeto.paginas[1]
    if etapa == "marcar":
        tela.ir_para_pagina(2)
        regiao = Regiao(tipo=GRAVURA, pontos=[(0.2, 0.2), (0.6, 0.5)])
        tela._registrar("marcar", "pagina", [2], {"selecao": [regiao.para_dicionario()]},
                        "Marcação da página 3")
        return projeto.paginas[2]
    if etapa == "mover":
        tela.ir_para_pagina(2)
        tela._gravar_o_conteudo(0.8, (0.05, 0.0), "Tamanho do conteúdo da página 3: 80%")
        return projeto.paginas[2]
    if etapa == "dividir":
        tela.escolher_ferramenta("dividir")
        tela._ir_para(0)
        tela._registrar("dividir_a_mao", "folha", [0],
                        dividir_a_mao.campos_para_dividir(projeto, 0, 0.47), "Folha 1: dividir")
        return projeto.paginas[0]
    if etapa == "girar":
        tela.ir_para_pagina(3)
        tela._girar_folhas(girar.GIRO_DIREITA)
        return projeto.paginas[3]
    raise ValueError(etapa)


# a etapa do Automático que corresponde a cada mexida ("marcada"), e uma rodada SEM ela
# ("desmarcada"). Girar, Marcar e Mover não têm etapa igual no Automático: a "marcada" é a
# etapa que mais chega perto (Gravuras e fotos, Margens iguais; no girar, todas as da página).
MARCADA = {
    "filtro": ([A.LIMPAR], {"filtro_padrao": PRETO_E_BRANCO}),
    "filtro_pb": ([A.LIMPAR], {"filtro_padrao": MELHORAR}),
    "cortar": ([A.CORTAR], {}),
    "endireitar": ([A.ENDIREITAR], {}),
    "marcar": ([A.LIMPAR, A.GRAVURAS], {"filtro_padrao": PRETO_E_BRANCO}),
    "mover": ([A.MARGENS], {}),
    "dividir": ([A.DIVIDIR], {}),
    "girar": ([A.DIVIDIR, A.ENDIREITAR, A.CORTAR, A.LIMPAR], {"filtro_padrao": PRETO_E_BRANCO}),
}
DESMARCADA = {
    "filtro": ([A.ENDIREITAR, A.CORTAR], {}),
    "filtro_pb": ([A.ENDIREITAR, A.CORTAR], {}),
    "cortar": ([A.ENDIREITAR, A.LIMPAR], {"filtro_padrao": PRETO_E_BRANCO}),
    "endireitar": ([A.CORTAR, A.LIMPAR], {"filtro_padrao": PRETO_E_BRANCO}),
    "marcar": ([A.ENDIREITAR, A.CORTAR], {}),
    "mover": ([A.ENDIREITAR, A.CORTAR, A.LIMPAR], {"filtro_padrao": PRETO_E_BRANCO}),
    "dividir": ([A.ENDIREITAR, A.CORTAR, A.LIMPAR], {"filtro_padrao": PRETO_E_BRANCO}),
    "girar": ([A.CADERNOS], {}),
}
# o que tem de continuar igual na página mexida, por etapa
GUARDA = {
    "filtro": ("filtro",), "filtro_pb": ("filtro",), "cortar": ("recorte",),
    "endireitar": ("angulo_manual",), "marcar": ("regioes_a_mao",),
    "mover": ("escala", "deslocamento"), "dividir": ("linha_da_folha", "folha_dividida"),
    "girar": ("rotacao_da_folha",),
}


@pytest.mark.parametrize("modo", ["marcada_pular", "marcada_rodar_tambem", "desmarcada"])
@pytest.mark.parametrize("etapa", list(MARCADA))
def test_caso1_mexida_a_mao(janela, tmp_path, monkeypatch, etapa, modo):
    resposta = {"marcada_pular": True, "marcada_rodar_tambem": False, "desmarcada": True}[modo]
    vigia = _Vigia(janela, monkeypatch, resposta)
    janela.abrir_livro(_livro_do_caso_1(tmp_path))
    pagina = _mexer(janela, etapa)
    antes = _estado_da_pagina(janela, pagina)
    pdf_antes = _imagens(_gerar(janela, tmp_path, "antes", cadernos=False))
    lugar_antes = janela.projeto.paginas.index(pagina)

    marcadas, opcoes = (MARCADA if modo != "desmarcada" else DESMARCADA)[etapa]
    rodou = _rodar(janela, marcadas, opcoes=opcoes)
    projeto = janela.projeto
    viva = pagina if pagina in projeto.paginas else next(
        (p for p in projeto.paginas if p.folha == pagina.folha), None)
    depois = _estado_da_pagina(janela, viva)
    lugar_depois = projeto.paginas.index(viva)
    pdf_depois = _imagens(_gerar(janela, tmp_path, "depois", cadernos=False))
    igual_no_pdf = (pdf_antes[lugar_antes].shape == pdf_depois[lugar_depois].shape
                    and bool(np.array_equal(pdf_antes[lugar_antes], pdf_depois[lugar_depois])))
    ficou = all(_json(antes[c]) == _json(depois[c]) for c in GUARDA[etapa])
    _anotar(f"caso1/{etapa}/{modo}", {
        "etapas_rodadas": marcadas, "opcoes": opcoes, "rodou": rodou,
        "perguntas": vigia.perguntas, "avisos": vigia.avisos,
        "antes": antes, "depois": depois, "o_feito_a_mao_ficou": ficou,
        "pagina_igual_no_pdf": igual_no_pdf,
        "paginas_do_pdf": [len(pdf_antes), len(pdf_depois)],
        "erros_log_novo": vigia.log_novo(), "excecoes": vigia.erros})
    assert rodou
    assert not vigia.erros and not vigia.log_novo().strip()


def _json(v):
    return json.dumps(v, sort_keys=True, default=str)


@pytest.mark.parametrize("giro", ["deitada_endireitada", "em_pe_deitada"])
def test_caso1_girar_e_depois_dividir(janela, tmp_path, monkeypatch, giro):
    """Girar à mão e depois o Automático com "Dividir": o giro não entra na pergunta.
    deitada_endireitada: a folha 2 veio deitada no PDF (página escaneada de lado) e foi
    posta em pé à mão (o caso de verdade). em_pe_deitada: uma página em pé girada 1/4 (fica
    deitada, como uma folha aberta)."""
    from core import girar

    vigia = _Vigia(janela, monkeypatch, True)
    em_pe = _pagina(3)
    deitada = cv2.rotate(em_pe, cv2.ROTATE_90_CLOCKWISE)
    folha2 = deitada if giro == "deitada_endireitada" else em_pe
    janela.abrir_livro(_pdf(tmp_path / "girar.pdf", [_pagina(1), folha2, _pagina(4)]))
    tela = janela.tela_conferir
    tela.ir_para_pagina(1)
    tela._girar_folhas(girar.GIRO_ESQUERDA if giro == "deitada_endireitada" else girar.GIRO_DIREITA)
    antes = _estado_da_pagina(janela, janela.projeto.paginas[1])
    rodou = _rodar(janela, [A.DIVIDIR])
    projeto = janela.projeto
    da_folha = [p for p in projeto.paginas if p.folha == 1]
    _anotar(f"caso1/girar_e_dividir/{giro}", {
        "rodou": rodou, "perguntas": vigia.perguntas, "antes": antes,
        "depois": _estado_da_pagina(janela, da_folha[0]),
        "paginas_da_folha_girada_depois": len(da_folha), "paginas_do_livro": len(projeto.paginas),
        "paginas_do_pdf": len(_imagens(_gerar(janela, tmp_path, "girar"), dpi=20)),
        "erros_log_novo": vigia.log_novo(), "excecoes": vigia.erros})
    assert not vigia.erros and not vigia.log_novo().strip()


# =========================================================================================
# CASOS 2 a 4: rodadas do Automático (3 páginas, depois o livro todo)
# =========================================================================================

TRES = [3, 7, 11]            # as páginas 4, 8 e 12


@pytest.fixture(scope="module")
def referencias(app, tmp_path_factory):
    """O livro de 24 páginas inteiro em cada filtro (pelo Automático no livro todo), sem
    cadernos: para dizer, página por página, com que filtro uma página saiu no PDF."""
    import projetos
    from ui.janela_principal import JanelaPrincipal

    pasta = tmp_path_factory.mktemp("referencias")
    (pasta / "projetos").mkdir()
    original = projetos.pasta_dos_projetos
    projetos.pasta_dos_projetos = lambda: pasta / "projetos"
    refs = {}
    try:
        for filtro in (ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO):
            janela = JanelaPrincipal()
            janela._perguntar_mexidas = lambda *a: True
            janela.abrir_livro(_livro_de_24(pasta, f"ref_{filtro}.pdf"))
            if filtro != ORIGINAL:
                _rodar(janela, [A.LIMPAR], opcoes={"filtro_padrao": filtro})
            refs[filtro] = [cv2.resize(i, (150, 210)).astype(np.float32)
                            for i in _imagens(_gerar(janela, pasta, f"saida_{filtro}"))]
            janela._fechar_a_janela_do_automatico()
            if janela.aviso_do_fundo is not None:
                janela.aviso_do_fundo.done(0)
            janela.close()
    finally:
        projetos.pasta_dos_projetos = original
    return refs


def _filtros_no_pdf(caminho: str, refs) -> list[str]:
    """O filtro com que cada página saiu, pela referência mais parecida."""
    saida = []
    for n, img in enumerate(_imagens(caminho)):
        pequena = cv2.resize(img, (150, 210)).astype(np.float32)
        dist = {f: float(np.abs(pequena - r[n]).mean()) for f, r in refs.items()}
        melhor = min(dist, key=dist.get)
        saida.append(NOME[melhor] if dist[melhor] < 3.0 else f"?({NOME[melhor]} {dist[melhor]:.1f})")
    return saida


def _situacao(janela) -> dict:
    estado = janela.estado_do_automatico
    return {"caixinhas_marcadas_ao_voltar": sorted(estado.marcadas),
            "situacoes": {e: A.situacao(janela.projeto, e) for e in A.ETAPAS},
            "filtro_do_livro": janela.projeto.filtro_padrao, "limpar_no_livro": janela.projeto.limpar}


def _final(janela, tmp_path, refs, vigia, nome) -> dict:
    projeto = janela.projeto
    cad = _gerar(janela, tmp_path, f"{nome}_cadernos")
    sem = _gerar(janela, tmp_path, f"{nome}_sem_cadernos", cadernos=False)
    return {
        "filtro_de_cada_pagina_no_projeto": [NOME.get(etapas.filtro_que_vale(projeto, p), p.filtro)
                                             for p in projeto.paginas],
        "filtro_de_cada_pagina_no_pdf": _filtros_no_pdf(sem, refs),
        "paginas_do_pdf_sem_cadernos": len(_imagens(sem, dpi=20)),
        "montar_cadernos_no_livro": projeto.montar_cadernos,
        "caminho_rapido_so_cadernos": projeto.so_cadernos,
        "cadernos": _ordem_dos_cadernos(cad, len(projeto.paginas), projeto.paginas_por_caderno),
        "perguntas": vigia.perguntas, "avisos": vigia.avisos,
        "erros_log_novo": vigia.log_novo(), "excecoes": vigia.erros}


def _primeira_rodada(janela, filtro=PRETO_E_BRANCO) -> bool:
    from ui.automatico import NAS_ESCOLHIDAS

    return _rodar(janela, [A.LIMPAR], alcance=NAS_ESCOLHIDAS, escolhidas=TRES,
                  opcoes={"filtro_padrao": filtro}, pagina=TRES[0])


def test_caso2_filtro_em_3_paginas_depois_so_cadernos_no_livro_todo(janela, tmp_path, monkeypatch, referencias):
    vigia = _Vigia(janela, monkeypatch, True)
    janela.abrir_livro(_livro_de_24(tmp_path))
    assert _primeira_rodada(janela)
    perguntas_1 = list(vigia.perguntas)
    ao_voltar = _situacao(janela)
    assert _rodar(janela, [A.CADERNOS], alcance="livro")
    r = _final(janela, tmp_path, referencias, vigia, "caso2")
    r.update({"perguntas_na_1a_rodada": perguntas_1, "ao_voltar_ao_automatico": ao_voltar})
    _anotar("caso2", r)
    assert not vigia.erros and not r["erros_log_novo"].strip()


def test_caso2b_sem_desmarcar_o_limpar_que_voltou_marcado(janela, tmp_path, monkeypatch, referencias):
    """Variação: depois da 1ª rodada, a caixinha "Limpar a folha" volta marcada
    ("ligada em 3 páginas"); a pessoa só marca "Montar cadernos" e roda no livro todo."""
    vigia = _Vigia(janela, monkeypatch, True)
    janela.abrir_livro(_livro_de_24(tmp_path))
    assert _primeira_rodada(janela)
    marcadas = set(janela.estado_do_automatico.marcadas) | {A.CADERNOS}
    assert _rodar(janela, marcadas, alcance="livro")
    r = _final(janela, tmp_path, referencias, vigia, "caso2b")
    r["etapas_rodadas_na_2a"] = sorted(marcadas)
    _anotar("caso2b", r)


@pytest.mark.parametrize("resposta", [True, False])
def test_caso3_filtro_em_3_paginas_depois_outro_filtro_e_cadernos_no_livro_todo(
        janela, tmp_path, monkeypatch, referencias, resposta):
    vigia = _Vigia(janela, monkeypatch, resposta)
    janela.abrir_livro(_livro_de_24(tmp_path))
    assert _primeira_rodada(janela)
    assert _rodar(janela, [A.LIMPAR, A.CADERNOS], alcance="livro",
                  opcoes={"filtro_padrao": MELHORAR})
    r = _final(janela, tmp_path, referencias, vigia, "caso3")
    _anotar(f"caso3/{'pular' if resposta else 'rodar_tambem'}", r)
    assert not vigia.erros and not r["erros_log_novo"].strip()


@pytest.mark.parametrize("resposta", [True, False])
@pytest.mark.parametrize("ordem", ["mao_antes", "mao_numa_das_3"])
def test_caso4_mistura(janela, tmp_path, monkeypatch, referencias, resposta, ordem):
    """Uma página mexida à mão (Mágico pro escolhido à mão) + as 3 páginas da 1ª rodada
    (Preto e branco) + 2ª rodada no livro todo: Limpar (Melhorar) e Montar cadernos.
    mao_antes: a página 6 mexida à mão antes de tudo. mao_numa_das_3: a página 8 (uma das
    3) mexida à mão depois da 1ª rodada."""
    vigia = _Vigia(janela, monkeypatch, resposta)
    janela.abrir_livro(_livro_de_24(tmp_path))
    tela = janela.tela_conferir
    if ordem == "mao_antes":
        tela.ir_para_pagina(5)
        tela._escolher_filtro(MAGICO_PRO)
    assert _primeira_rodada(janela)
    if ordem == "mao_numa_das_3":
        tela.ir_para_pagina(7)
        tela._escolher_filtro(MAGICO_PRO)
    assert _rodar(janela, [A.LIMPAR, A.CADERNOS], alcance="livro",
                  opcoes={"filtro_padrao": MELHORAR})
    r = _final(janela, tmp_path, referencias, vigia, "caso4")
    _anotar(f"caso4/{ordem}/{'pular' if resposta else 'rodar_tambem'}", r)
    assert not vigia.erros and not r["erros_log_novo"].strip()


# =========================================================================================
# Livro de verdade do acervo (Boécio, 50 páginas): o caso 2 e o caso 4
# =========================================================================================

def _ordem_pela_imagem(cadernos: str, sem: str, total: int, por_caderno: int) -> dict:
    """Livro de verdade: acha cada metade de cada lado do caderno entre as páginas do PDF
    sem cadernos (a mais parecida) e compara com a conta da dobra."""
    paginas = [cv2.resize(cv2.cvtColor(i, cv2.COLOR_RGB2GRAY), (60, 86)).astype(np.float32)
               for i in _imagens(sem, dpi=40)]
    esperado = [((l.esquerda + 1) if l.esquerda is not None else 0,
                 (l.direita + 1) if l.direita is not None else 0)
                for l in montar_ordem(total, por_caderno)]
    lido = []
    for img in _imagens(cadernos, dpi=40):
        meio = img.shape[1] // 2
        par = []
        for metade in (img[:, :meio], img[:, meio:]):
            cinza = cv2.resize(cv2.cvtColor(metade, cv2.COLOR_RGB2GRAY), (60, 86)).astype(np.float32)
            if cinza.min() > 250:
                par.append(0)
                continue
            dist = [float(np.abs(cinza - p).mean()) for p in paginas]
            par.append(int(np.argmin(dist)) + 1)
        lido.append(tuple(par))
    return {"folhas_do_pdf": len(lido), "na_ordem_certa": lido == esperado,
            "lido": lido, "esperado": esperado}


@pytest.mark.skipif(not BOECIO.exists(), reason="acervo fora do lugar")
@pytest.mark.parametrize("caso", ["caso2", "caso4"])
def test_livro_do_acervo(janela, tmp_path, monkeypatch, caso):
    vigia = _Vigia(janela, monkeypatch, True)
    janela.abrir_livro(str(BOECIO))
    tela = janela.tela_conferir
    if caso == "caso4":
        tela.ir_para_pagina(5)
        tela._escolher_filtro(MAGICO_PRO)
    assert _primeira_rodada(janela)
    perguntas_1 = list(vigia.perguntas)
    if caso == "caso2":
        assert _rodar(janela, [A.CADERNOS], alcance="livro")
    else:
        assert _rodar(janela, [A.LIMPAR, A.CADERNOS], alcance="livro",
                      opcoes={"filtro_padrao": MELHORAR})
    projeto = janela.projeto
    cad = _gerar(janela, tmp_path, "boecio_cadernos")
    sem = _gerar(janela, tmp_path, "boecio_sem", cadernos=False)
    with fitz.open(str(BOECIO)) as d:
        total_entrada = d.page_count
    r = {"paginas_do_livro": total_entrada,
         "perguntas_na_1a_rodada": perguntas_1, "perguntas": vigia.perguntas,
         "filtro_de_cada_pagina_no_projeto": [NOME.get(etapas.filtro_que_vale(projeto, p), p.filtro)
                                             for p in projeto.paginas],
         "paginas_do_pdf_sem_cadernos": len(_imagens(sem, dpi=10)),
         "cadernos": _ordem_pela_imagem(cad, sem, len(projeto.paginas), projeto.paginas_por_caderno),
         "avisos": vigia.avisos, "erros_log_novo": vigia.log_novo(), "excecoes": vigia.erros}
    _anotar(f"acervo_boecio/{caso}", r)
    assert not vigia.erros and not r["erros_log_novo"].strip()
