"""Rodada de antes/depois do item 1.2 (segunda etapa: o detector de gravura do
ScanTailor ligado ao processamento), pelo conferencia.py.

    .venv\\Scripts\\python.exe rodada_gravura_1_2.py [PASTA_DE_SAIDA]

O QUE FAZ
    Roda o conferencia.py (o mesmo caminho do botão "Confirmar e processar")
    nas páginas do 1.2, cinco vezes, cada uma numa subpasta de PASTA_DE_SAIDA
    (padrão: relatorios\\conferir\\fase1-1.2-ligacao-<data>\\):

      1-antes-magico-pro        detector de gravura de antes (o "antigo")
      2-depois-magico-pro       ScanTailor, forma livre (a proposta de fábrica),
                                com a coluna "Rodada anterior" = 1
      3-antes-preto-e-branco    antigo
      4-depois-preto-e-branco   ScanTailor livre, "Rodada anterior" = 3
      5-retangular-magico-pro   ScanTailor, forma retangular, "Rodada anterior" = 2

    O "antes" é o código de hoje com o detector antigo escolhido
    (core.detectar_regioes.DETECTOR_DE_GRAVURA_PADRAO = "antigo"): o caminho
    antigo é o mesmo de antes do 1.2, conta por conta (ver
    tests/test_gravura_no_processamento.py, test_o_caminho_antigo_e_o_de_sempre).

AS PÁGINAS
    As 16 do item "fase1" do gabarito (inclui as obrigatórias: Palatino 5,
    Escola 35, Horas 11, 13, 26, 27, Opus Majus 20), mais Palatino 67,
    Rhetorica 18, Graduale 222 (Lista de bugs, "sensível ao enquadramento") e
    Marial 146 e 153 (título corrido tomado por gravura). As duas do Marial não
    estão no gabarito: são copiadas do acervo (só leitura, página copiada sem
    redesenhar) para saida_teste\\gabarito_1_2\\paginas\\. O gabarito\\ não é
    alterado: a rodada usa uma lista.json provisória em saida_teste\\gabarito_1_2\\
    que aponta para os arquivos de verdade do gabarito (caminho completo).

Não é usado pelo programa. Seguro mudar: tudo (é só a rodada de conferência).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
GABARITO = RAIZ / "gabarito"
PROVISORIO = RAIZ / "saida_teste" / "gabarito_1_2"
MARIAL = (RAIZ.parent / "EditorImpressao-arquivos" / "TESTES EDITOR DE IMPRESSAO" / "LIVROS PARA TESTE"
          / "Marial de sermoens - Frei Balthasar Paez. (1).pdf")
ITEM = "1.2"
EXTRAS = ["palatino_p067", "rhetorica_p018", "graduale_p222"]
DO_MARIAL = {146: "título corrido tomado por gravura no teste de velocidade (Lista de bugs, 29/09)",
             153: "título corrido \"de Maria.\" tomado por gravura (Lista de bugs, 29/09)"}


def _absoluto(valor):
    """Caminho relativo do gabarito -> caminho completo (strings e listas)."""
    if isinstance(valor, str) and valor and not Path(valor).is_absolute():
        return str(GABARITO / valor)
    return valor


def copiar_do_marial() -> dict:
    """Copia as páginas do Marial (PDF sem redesenhar + PNG no DPI do scan)."""
    import fitz

    pasta = PROVISORIO / "paginas"
    pasta.mkdir(parents=True, exist_ok=True)
    entradas = {}
    with fitz.open(MARIAL) as livro:
        for numero, para_que in DO_MARIAL.items():
            pid = f"marial_p{numero:03d}"
            pdf, png = pasta / f"{pid}.pdf", pasta / f"{pid}.png"
            if not pdf.is_file():
                with fitz.open() as novo:
                    novo.insert_pdf(livro, from_page=numero - 1, to_page=numero - 1)
                    novo.save(pdf)
            pagina = livro[numero - 1]
            maior = max(i[2] for i in pagina.get_images())
            dpi = min(400.0, maior / (pagina.rect.width / 72))
            if not png.is_file():
                pagina.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False).save(png)
            entradas[pid] = {"livro": str(MARIAL), "pagina": numero, "pdf": str(pdf), "png": str(png),
                             "dpi_png": round(dpi), "para_que": para_que,
                             "detalhe": [0.0, 0.0, 1.0, 0.25], "origem": "rodada do 1.2 (29/09/2026)"}
    return entradas


def montar_lista() -> Path:
    """A lista.json provisória, com o item "1.2"."""
    lista = json.loads((GABARITO / "lista.json").read_text(encoding="utf-8"))
    for entrada in lista["paginas"].values():
        for campo in ("pdf", "png"):
            entrada[campo] = _absoluto(entrada.get(campo))
    for entrada in lista.get("camscanner", {}).values():
        for campo in ("original", "magico_pro"):
            entrada[campo] = _absoluto(entrada.get(campo))
    for entrada in lista.get("scantailor_24_09", {}).values():
        for campo in list(entrada):
            if campo != "pagina_gabarito":
                entrada[campo] = _absoluto(entrada[campo])
    lista["paginas"].update(copiar_do_marial())
    lista["itens"][ITEM] = list(lista["itens"]["fase1"]) + EXTRAS + [f"marial_p{n:03d}" for n in DO_MARIAL]
    lista.setdefault("nomes_dos_itens", {})[ITEM] = (
        "Item 1.2: o seletor de gravura do ScanTailor ligado ao processamento")
    PROVISORIO.mkdir(parents=True, exist_ok=True)
    caminho = PROVISORIO / "lista.json"
    caminho.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")
    return caminho


def rodar(saida: Path) -> dict[str, Path]:
    """As cinco rodadas; devolve {nome: pasta}."""
    os.environ.setdefault("LOCALAPPDATA", str(RAIZ / "saida_teste" / "localappdata_rodada_1_2"))
    Path(os.environ["LOCALAPPDATA"]).mkdir(parents=True, exist_ok=True)
    import conferencia
    from core import detectar_regioes as dr

    montar_lista()
    feitas: dict[str, Path] = {}
    plano = [
        ("1-antes-magico-pro", "antigo", "livre", "Mágico pro", None),
        ("2-depois-magico-pro", "scantailor", "livre", "Mágico pro", "1-antes-magico-pro"),
        ("3-antes-preto-e-branco", "antigo", "livre", "Preto e branco", None),
        ("4-depois-preto-e-branco", "scantailor", "livre", "Preto e branco", "3-antes-preto-e-branco"),
        ("5-retangular-magico-pro", "scantailor", "retangular", "Mágico pro", "2-depois-magico-pro"),
    ]
    # Desde 30/09 a forma vem do projeto (Projeto.gravura_forma), e o
    # conferencia.py cria o projeto sozinho: a forma da rodada entra no
    # projeto logo antes da analise (o mesmo analisar_projeto que a
    # TarefaAnalise chama).
    import ui.tarefas as tarefas
    from core import pipeline

    analisar_de_verdade = pipeline.analisar_projeto
    escolhida = {"forma": "livre"}

    def analisar_com_a_forma(projeto, *a, **k):
        projeto.gravura_forma = escolhida["forma"]
        return analisar_de_verdade(projeto, *a, **k)

    tarefas.analisar_projeto = analisar_com_a_forma
    for nome, detector, forma, filtro, anterior in plano:
        dr.DETECTOR_DE_GRAVURA_PADRAO = detector
        escolhida["forma"] = forma
        argv = [ITEM, "--filtro", filtro]
        if anterior:
            argv += ["--comparar-com", str(feitas[anterior])]
        destino = saida / nome
        print(f"\n===== {nome}: detector {detector}, forma {forma}, filtro {filtro} =====", flush=True)
        codigo = conferencia.main(argv, gabarito=PROVISORIO, destino=destino,
                                  referencias=RAIZ / "relatorios" / "conferir" / "_referencias")
        pastas = sorted(p for p in destino.iterdir() if p.is_dir())
        feitas[nome] = pastas[-1]
        print(f"  código {codigo}: {feitas[nome]}", flush=True)
    return feitas


if __name__ == "__main__":
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        RAIZ / "relatorios" / "conferir" / f"fase1-1.2-ligacao-{datetime.now():%Y-%m-%d}")
    saida.mkdir(parents=True, exist_ok=True)
    feitas = rodar(saida)
    (saida / "rodadas.json").write_text(json.dumps({k: str(v) for k, v in feitas.items()},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
