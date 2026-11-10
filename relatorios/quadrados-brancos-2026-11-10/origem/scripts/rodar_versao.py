"""Quadrados brancos, origem (10/11/2026): desenha paginas como saem no PDF com UMA versao do
programa (a pasta de uma copia do git), sem janela e sem mudar nada do programa.

    python rodar_versao.py <raiz da versao> <livro.pdf> <paginas "13,18" ou "todas"> <filtro> <saida>

<filtro>: melhorar (Clareza "bem forte", 100) ou magico_pro (Intensidade "bem fraco", 0), as mesmas
escolhas dos prints 09 e 10 e do relatorio do verificador.

Como o livro e aberto, em cada versao:
  - versao que abre o livro novo pela "passada leve" (core.automatico.livro_leve chamada pela
    janela: desde e2321b16, etapa 3 da obra, 26/10): a mesma passada, e o filtro escolhido A MAO
    na pagina (marca FILTRO), como no painel. "Respeitar as gravuras achadas" marcada (de fabrica).
  - versao de antes (a tela "O que fazer"): o livro novo com as opcoes de fabrica daquela versao
    ("Limpar a folha" e "Procurar gravura e letra" ligadas), e o filtro trocado na pagina. Para as
    paginas sairem no MESMO enquadramento em todas as versoes, dividir, endireitar, cortar,
    margens e cadernos ficam desligados (o filtro nao depende deles).
Ambiente:
  LIMPAR=0      versao de antes: "Limpar a folha" desmarcada no livro (so para a prova da etapa 1)
  PROCURAR=0    versao de antes: "Procurar gravura e letra" desmarcada no livro
  DESFAZER=1    versao de hoje: so a mudanca da etapa 1 desfeita (a procura da gravura volta a
                depender so de "Procurar gravura e letra", como antes de 175addb7). So neste processo.
  CONSERTO_C=1  versao de hoje com o conserto C do verificador (so para comparar).
Grava <saida>/<filtro>_pNNN.png (pagina inteira, 300 DPI), <saida>/<filtro>_pNNN.jpg (1/4) e
<saida>/<filtro>.json (gravuras achadas, segundos)."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
TRABALHO = Path(r"D:\programas\EditorImpressao\.claude\worktrees\qo-trabalho")
DADOS = TRABALHO / "dados" / RAIZ.name
(DADOS / "temp").mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(DADOS)            # nada do Samuel e tocado
os.environ["TEMP"] = os.environ["TMP"] = str(DADOS / "temp")
os.environ["QT_QPA_PLATFORM"] = "offscreen"          # nunca abre janela
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)
try:                                                  # prioridade baixa: o PC do Samuel trava facil
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:  # noqa: BLE001
    pass

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import pipeline  # noqa: E402
from core.pdf_io import abrir_pdf, info_paginas  # noqa: E402
import modelos  # noqa: E402
from modelos import Projeto  # noqa: E402

AJUSTE = {"melhorar": 100, "magico_pro": 0}


def janela_usa_livro_leve() -> bool:
    texto = (RAIZ / "ui" / "janela_principal.py").read_text(encoding="utf-8", errors="replace")
    return "livro_leve" in texto


def instalar_desfazer() -> None:
    """So a mudanca da etapa 1 (175addb7) desfeita: em garantir_selecao e _vai_detectar a
    pergunta "procura a gravura?" volta a ser so "Procurar gravura e letra" do livro
    (Projeto.detectar_regioes, que no livro novo vem ligado), como em ddd4d74a."""
    from core import etapas

    original = etapas.marca_sozinho

    def antiga(projeto, pagina=None):
        return bool(getattr(projeto, "detectar_regioes", False))

    def com_a_pergunta_antiga(funcao):
        def envolta(*args, **kwargs):
            etapas.marca_sozinho = antiga
            try:
                return funcao(*args, **kwargs)
            finally:
                etapas.marca_sozinho = original
        return envolta

    pipeline.garantir_selecao = com_a_pergunta_antiga(pipeline.garantir_selecao)
    pipeline._vai_detectar = com_a_pergunta_antiga(pipeline._vai_detectar)


def instalar_conserto_c() -> None:
    """O conserto C do relatorio do verificador (10/11, secao 8), so neste processo e so para
    comparar: a regra "em volta e papel" (scripts/candidato.py dele, o A) mais a procura da
    gravura no Melhorar e no Magico pro a mao com "Respeitar" marcada (o B, instalar_b dele:
    a mesma conta de core.etapas.respeitar_procura, como se fosse Preto e branco)."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    import candidato                                   # o A do verificador
    candidato.instalar()
    from core import etapas
    from core.filtros import MAGICO_PRO, MELHORAR, PRETO_E_BRANCO

    original = etapas.respeitar_procura

    def respeitar_procura_b(projeto, pagina=None):
        if pagina is not None and getattr(pagina, "filtro", None) in (MELHORAR, MAGICO_PRO):
            filtro = pagina.filtro
            pagina.filtro = PRETO_E_BRANCO
            try:
                return original(projeto, pagina)
            finally:
                pagina.filtro = filtro
        return original(projeto, pagina)

    etapas.respeitar_procura = respeitar_procura_b


def livro_novo(pdf: str):
    projeto = Projeto(caminho_entrada=pdf, nome=Path(pdf).stem)
    doc = abrir_pdf(pdf)
    try:
        tamanhos = [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)]
    finally:
        doc.close()
    leve = janela_usa_livro_leve()
    if leve:
        from core import automatico
        automatico.livro_leve(projeto, tamanhos)
    else:
        from core.filtros import ORIGINAL
        from modelos import METADE_INTEIRA, ConfigFolha, ConfigPagina
        for campo in ("dividir_folhas", "endireitar", "cortar_bordas", "margens_iguais",
                      "montar_cadernos"):
            if hasattr(projeto, campo):
                setattr(projeto, campo, False)
        if os.environ.get("LIMPAR") == "0":
            projeto.limpar = False
        if os.environ.get("PROCURAR") == "0":       # "Procurar gravura e letra" desmarcada
            projeto.detectar_regioes = False
        projeto.folhas = [ConfigFolha(indice=i, dividir=False, posicao_corte=0.5)
                          for i in range(len(tamanhos))]
        projeto.paginas = [ConfigPagina(indice=i, folha=i, metade=METADE_INTEIRA, filtro=ORIGINAL)
                           for i in range(len(tamanhos))]
    return projeto, leve


def escolher_filtro(projeto, pag, filtro: str, leve: bool) -> None:
    pag.filtro = filtro
    if filtro == "melhorar":
        pag.clareza_melhorar = AJUSTE[filtro]
    else:
        pag.intensidade_magico = AJUSTE[filtro]
    if hasattr(pag, "respeitar_gravuras_achadas"):
        pag.respeitar_gravuras_achadas = True
    try:
        from core import etapas
        etapas.marcar_mexida_a_mao(pag, etapas.FILTRO)     # escolhido a mao no painel
    except (ImportError, AttributeError):
        pass                                               # versao de antes da etapa 1


def main() -> None:
    pdf, quais, qual_filtro, saida = sys.argv[2], sys.argv[3], sys.argv[4], Path(sys.argv[5])
    filtros = ["melhorar", "magico_pro"] if qual_filtro == "ambos" else [qual_filtro]
    saida.mkdir(parents=True, exist_ok=True)
    if os.environ.get("DESFAZER") == "1":
        instalar_desfazer()
    if os.environ.get("CONSERTO_C") == "1":
        instalar_conserto_c()
    projeto, leve = livro_novo(pdf)
    paginas = (list(range(1, len(projeto.paginas) + 1)) if quais == "todas"
               else [int(v) for v in quais.split(",")])
    como = {"raiz": str(RAIZ), "livro_leve": leve, "limpar": bool(projeto.limpar),
            "detectar_regioes": bool(getattr(projeto, "detectar_regioes", False)),
            "desfazer": os.environ.get("DESFAZER") == "1",
            "conserto_c": os.environ.get("CONSERTO_C") == "1"}
    todos = {}
    for filtro in filtros:
        arq = saida / f"{filtro}.json"
        todos[filtro] = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
        todos[filtro]["_como"] = como
    doc = abrir_pdf(pdf)
    try:
        for numero in paginas:
            # os dois filtros na mesma pagina, um depois do outro: a gravura achada no primeiro
            # fica guardada na pagina (como no programa) e nao e procurada de novo
            for filtro in filtros:
                res = todos[filtro]
                if str(numero) in res and (saida / f"{filtro}_p{numero:03d}.jpg").exists():
                    continue
                t = time.monotonic()
                pag = projeto.paginas[numero - 1]
                escolher_filtro(projeto, pag, filtro, leve)
                folha = projeto.folhas[pag.folha]
                if hasattr(pipeline, "_pagina_pronta"):
                    img, _ = pipeline._pagina_pronta(projeto, doc, folha, pag, pipeline._FolhaDaVez(), 0)
                else:   # versao de setembro: o mesmo corpo do processar (preparar_metade + filtro)
                    img, _ = pipeline.renderizar_pagina(doc, projeto, pag, dpi=projeto.qualidade_dpi)
                if img.ndim == 2:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                sel = pag.selecao or []
                tipos = [(r.get("tipo"), r.get("origem")) for r in sel if isinstance(r, dict)]
                if quais != "todas":
                    cv2.imwrite(str(saida / f"{filtro}_p{numero:03d}.png"), img)
                pequena = cv2.resize(img, (img.shape[1] // 4, img.shape[0] // 4),
                                     interpolation=cv2.INTER_AREA)
                cv2.imwrite(str(saida / f"{filtro}_p{numero:03d}.jpg"), pequena,
                            [cv2.IMWRITE_JPEG_QUALITY, 90])
                res[str(numero)] = {"gravuras_achadas": sum(1 for a, _ in tipos if a == "gravura"),
                                    "regioes": tipos, "segundos": round(time.monotonic() - t, 2),
                                    "forma": list(img.shape)}
                print(numero, filtro, res[str(numero)]["gravuras_achadas"], res[str(numero)]["segundos"],
                      flush=True)
                (saida / f"{filtro}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                                     encoding="utf-8")
    finally:
        doc.close()


if __name__ == "__main__":
    main()
