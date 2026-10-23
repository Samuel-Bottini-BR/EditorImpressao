"""Antes/depois dos itens 2.4, 2.6, 2.10, 2.17 e 2.18 (implementador B, 22/10/2026).

Regra do Samuel (21/10/2026): toda página passa pelo caminho inteiro do
programa, na ordem do livro novo (dividir → endireitar → cortar → filtro), com
os ajustes de fábrica, até a ferramenta testada (core.pipeline.analisar_projeto
+ core.pipeline.processar), e cada imagem diz por onde passou e com quais
opções. Só páginas que vão ser impressas (o gabarito não tem capa nem lombada).

USO (da worktree; um item por processo):
    python relatorios\\fase2-novas\\scripts\\antes_depois.py --raiz <worktree> 2.4
    ... 2.6 | 2.10 | 2.17 | 2.18
Saída: relatorios/conferir/fase2-novas/<item>/ (fora do git; os .md ficam).
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve()
sys.path.insert(0, str(AQUI.parent))
import rodada_processar as rp  # noqa: E402

SAIDA = AQUI.parents[3] / "relatorios" / "conferir" / "fase2-novas"

LIVROS_2_4 = {
    "graduale": ["graduale_p221", "graduale_p222", "graduale_p223"],
    "horas": ["horas_p011", "horas_p013", "horas_p014", "horas_p026", "horas_p027", "horas_p047"],
    "boecio": ["boecio_p003", "boecio_p007", "boecio_p008", "boecio_p022"],
    "opusmajus": ["opusmajus_p003", "opusmajus_p011", "opusmajus_p020", "opusmajus_p165",
                  "opusmajus_p256"],
    "palatino": ["palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010"],
}


def _fonte(tamanho=18, negrito=False):
    from PIL import ImageFont

    return ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf" if negrito
                              else r"C:\Windows\Fonts\segoeui.ttf", tamanho)


def _faixa(img, linhas):
    """Põe linhas de texto (com acento) em cima da imagem BGR."""
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw

    altura = 10 + 26 * len(linhas)
    faixa = Image.new("RGB", (img.shape[1], altura), "white")
    desenho = ImageDraw.Draw(faixa)
    for i, linha in enumerate(linhas):
        desenho.text((6, 4 + 26 * i), linha, fill="black", font=_fonte(18, negrito=(i == 0)))
    return np.vstack([cv2.cvtColor(np.asarray(faixa), cv2.COLOR_RGB2BGR), img])


def _paginas_do_pdf(caminho, dpi=None):
    """As páginas do PDF como imagens BGR (na resolução da imagem dentro, ou dpi)."""
    import cv2
    import fitz
    import numpy as np

    imagens = []
    with fitz.open(str(caminho)) as doc:
        for pagina in doc:
            pix = pagina.get_pixmap(dpi=dpi or 150, alpha=False)
            img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
            imagens.append(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    return imagens


def item_2_4(raiz):
    pasta = SAIDA / "2.4"
    resumo = {}
    for nome, pids in LIVROS_2_4.items():
        resumo[nome] = rp.livro(pids, raiz, pasta, nome, {"margens_iguais": True}, {})
    (pasta / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")


def _processar_pagina(raiz, pid, pasta, rotulo, campos_livro=None, campos_pagina=None, selecao=None):
    """Uma página do gabarito pelo caminho inteiro; devolve (imagem, frase, caminho do PDF)."""
    from core.pipeline import processar

    entrada = rp._gabarito(raiz, pid)
    pdf = pasta / f"{pid}-{rotulo}.pdf"
    projeto = rp._projeto_de_fabrica(entrada, pdf)
    for k, v in (campos_livro or {}).items():
        setattr(projeto, k, v)
    for pagina in projeto.paginas:
        for k, v in (campos_pagina or {}).items():
            setattr(pagina, k, v)
    if selecao is not None:
        # a marcacao que o programa acha sozinho primeiro (o mesmo caminho da
        # previa), e a area a mao POR CIMA dela, como a pessoa faria na tela;
        # no "antes" a mesma conta, sem a area (so ela muda)
        from core.pdf_io import abrir_pdf
        from core.pipeline import renderizar_pagina

        doc = abrir_pdf(projeto.caminho_entrada)
        try:
            for pagina in projeto.paginas_ativas:
                renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
                marcacao = pagina.obter_selecao()
                for regiao in selecao.regioes:
                    marcacao.acrescentar(regiao)
                pagina.guardar_selecao(marcacao)
        finally:
            doc.close()
    processar(projeto)
    frase = rp._por_onde_passou(projeto)
    extras = ", ".join(f"{k}={v}" for k, v in (campos_pagina or {}).items())
    return _paginas_do_pdf(pdf, dpi=300)[0], frase + (f" → página: {extras}" if extras else ""), pdf


def _lado_a_lado(colunas, altura=1100):
    import cv2
    import numpy as np

    pedacos = []
    for titulo, img, frase in colunas:
        escala = altura / img.shape[0]
        pequena = cv2.resize(img, (max(1, int(img.shape[1] * escala)), altura), interpolation=cv2.INTER_AREA)
        pequena = cv2.copyMakeBorder(pequena, 0, 0, 0, 12, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        pedacos.append(_faixa(pequena, [titulo] + _quebrar(frase, pequena.shape[1])))
    alto = max(p.shape[0] for p in pedacos)
    pedacos = [cv2.copyMakeBorder(p, 0, alto - p.shape[0], 0, 0, cv2.BORDER_CONSTANT,
                                  value=(255, 255, 255)) for p in pedacos]
    return np.hstack(pedacos)


def _quebrar(frase, largura, por_letra=9):
    palavras, linhas, atual = frase.split(" "), [], ""
    limite = max(20, largura // por_letra)
    for p in palavras:
        if len(atual) + len(p) + 1 > limite:
            linhas.append(atual)
            atual = p
        else:
            atual = (atual + " " + p).strip()
    return linhas + [atual] if atual else linhas


def _recorte_onde_muda(a, b, lado=420):
    import cv2
    import numpy as np

    ca = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY) if a.ndim == 3 else a
    cb = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY) if b.ndim == 3 else b
    if ca.shape != cb.shape:
        return (0, 0)
    dif = (cv2.absdiff(ca, cb) > 24).astype(np.float32)
    if not dif.any():
        return ((a.shape[0] - lado) // 2, (a.shape[1] - lado) // 2)
    soma = cv2.boxFilter(dif, -1, (lado, lado), normalize=False)
    y, x = np.unravel_index(int(np.argmax(soma)), soma.shape)
    return (int(np.clip(y - lado // 2, 0, max(0, a.shape[0] - lado))),
            int(np.clip(x - lado // 2, 0, max(0, a.shape[1] - lado))))


def item_2_17(raiz):
    import cv2

    from core.filtros import MELHORAR, PRETO_E_BRANCO

    pasta = SAIDA / "2.17"
    pasta.mkdir(parents=True, exist_ok=True)
    casos = [
        ("marial_p007", PRETO_E_BRANCO, {"luz_igualar": True}, "Igualar a luz"),
        ("marial_p007", PRETO_E_BRANCO, {"luz_suavizar": True}, "Suavizar as letras"),
        ("boecio_p007", PRETO_E_BRANCO, {"luz_suavizar": True}, "Suavizar as letras"),
        ("graduale_p221", MELHORAR, {"luz_igualar": True}, "Igualar a luz"),
        ("horas_p047", MELHORAR, {"luz_igualar": True}, "Igualar a luz"),
        ("escola_p035", MELHORAR, {"luz_chuvisco": 50}, "Tirar o chuvisco 50"),
        ("boecio_p022", MELHORAR, {"luz_chuvisco": 50}, "Tirar o chuvisco 50"),
    ]
    numeros = {}
    for pid, filtro, campos, nome in casos:
        antes, frase_a, _ = _processar_pagina(raiz, pid, pasta, "antes",
                                              {"filtro_padrao": filtro}, {"filtro": filtro})
        depois, frase_d, _ = _processar_pagina(raiz, pid, pasta, "depois",
                                               {"filtro_padrao": filtro}, {"filtro": filtro, **campos})
        base = f"{pid}-{nome.replace(' ', '_')}"
        cv2.imwrite(str(pasta / f"{base}-pagina.jpg"),
                    _lado_a_lado([("Hoje", antes, frase_a), (nome, depois, frase_d)]),
                    [cv2.IMWRITE_JPEG_QUALITY, 88])
        y, x = _recorte_onde_muda(antes, depois)
        lado = 420
        cv2.imwrite(str(pasta / f"{base}-recorte.png"),
                    _lado_a_lado([("Hoje (ampliado)", antes[y:y + lado, x:x + lado], ""),
                                  (nome + " (ampliado)", depois[y:y + lado, x:x + lado], "")], altura=700))
        numeros[base] = {"pontos_diferentes": int((cv2.absdiff(antes, depois) > 24).any(axis=-1).sum())
                         if antes.shape == depois.shape else None,
                         "recorte_yx": [y, x]}
    (pasta / "numeros.json").write_text(json.dumps(numeros, ensure_ascii=False, indent=1), encoding="utf-8")


def item_2_18(raiz):
    import cv2

    from core.filtros import PRETO_E_BRANCO
    from core.selecao import MAO, PINTAR, TINTA_COR, TINTA_PRETA, Regiao, Selecao

    pasta = SAIDA / "2.18"
    pasta.mkdir(parents=True, exist_ok=True)
    casos = [
        ("escola_p007", "Tinta com a cor, papel branco (no título)",
         Regiao(tipo=TINTA_COR, pontos=[(0.05, 0.02), (0.95, 0.2)], origem=MAO)),
        ("horas_p013", "Tinta preta, fundo original (no texto)",
         Regiao(tipo=TINTA_PRETA, pontos=[(0.25, 0.3), (0.72, 0.6)], origem=MAO)),
        ("marial_p007", "Pintar por cima de branco (a mancha da esquerda)",
         Regiao(tipo=PINTAR, pontos=[(0.0, 0.0), (0.11, 0.28)], origem=MAO, cor="#ffffff")),
    ]
    for pid, nome, regiao in casos:
        antes, frase_a, _ = _processar_pagina(raiz, pid, pasta, "antes",
                                              {"filtro_padrao": PRETO_E_BRANCO}, {"filtro": PRETO_E_BRANCO},
                                              selecao=Selecao())
        depois, frase_d, _ = _processar_pagina(raiz, pid, pasta, "depois",
                                               {"filtro_padrao": PRETO_E_BRANCO}, {"filtro": PRETO_E_BRANCO},
                                               selecao=Selecao([regiao]))
        cv2.imwrite(str(pasta / f"{pid}-pagina.jpg"),
                    _lado_a_lado([("Hoje", antes, frase_a),
                                  (nome, depois, frase_d + f" → área marcada à mão: {regiao.pontos}")]),
                    [cv2.IMWRITE_JPEG_QUALITY, 88])


def item_2_10(raiz):
    import cv2

    from core.filtros import MAGICO_PRO, MELHORAR, PRETO_E_BRANCO

    pasta = SAIDA / "2.10"
    pasta.mkdir(parents=True, exist_ok=True)
    casos = [("horas_p011", PRETO_E_BRANCO), ("horas_p013", PRETO_E_BRANCO), ("horas_p047", MAGICO_PRO),
             ("escola_p007", MAGICO_PRO), ("graduale_p221", MELHORAR), ("palatino_p005", MAGICO_PRO)]
    numeros = {}
    for pid, filtro in casos:
        antes, frase_a, pdf_a = _processar_pagina(raiz, pid, pasta, "uma", {"filtro_padrao": filtro},
                                                  {"filtro": filtro})
        depois, frase_d, pdf_d = _processar_pagina(raiz, pid, pasta, "duas",
                                                   {"filtro_padrao": filtro, "pdf_em_duas_camadas": True},
                                                   {"filtro": filtro})
        mb_a, mb_d = pdf_a.stat().st_size / 2 ** 20, pdf_d.stat().st_size / 2 ** 20
        numeros[pid] = {"filtro": filtro, "uma_camada_mb": round(mb_a, 2), "duas_camadas_mb": round(mb_d, 2)}
        cv2.imwrite(str(pasta / f"{pid}-pagina.jpg"),
                    _lado_a_lado([(f"Uma camada (hoje): {mb_a:.2f} MB", antes, frase_a),
                                  (f"Duas camadas: {mb_d:.2f} MB", depois, frase_d + " → PDF em duas camadas")]),
                    [cv2.IMWRITE_JPEG_QUALITY, 88])
        if antes.shape == depois.shape:
            y, x = _recorte_onde_muda(antes, depois, 400)
            cv2.imwrite(str(pasta / f"{pid}-recorte.png"),
                        _lado_a_lado([("Uma camada (ampliado)", antes[y:y + 400, x:x + 400], ""),
                                      ("Duas camadas (ampliado)", depois[y:y + 400, x:x + 400], "")],
                                     altura=700))
    (pasta / "numeros.json").write_text(json.dumps(numeros, ensure_ascii=False, indent=1), encoding="utf-8")


def item_2_6(raiz):
    """O livro de 6 páginas da Horas, processado de fábrica e montado como
    livreto A4 (as opções de fábrica da impressão) e com o lado direito a 90%.
    As linhas vermelhas (margem mínima) e azul (dobra) só existem nesta imagem."""
    import cv2
    import fitz

    from core import impressao as imp
    from core.pipeline import processar

    pasta = SAIDA / "2.6"
    pasta.mkdir(parents=True, exist_ok=True)
    entrada = rp._livro(LIVROS_2_4["horas"], raiz, pasta / "horas-entrada.pdf")
    livro_pdf = pasta / "horas-livro.pdf"
    projeto = rp._projeto_de_fabrica(entrada, livro_pdf)
    processar(projeto)
    frase = rp._por_onde_passou(projeto)
    numeros = {}
    for nome, campos in (("livreto-de-fabrica", {}),
                         ("livreto-direita-90", {"escala_direita": 90.0}),
                         ("livreto-pagina-3-a-80", {"excecoes": {3: 80.0}}),
                         ("pagina-inteira", {"formato": imp.PAGINA_INTEIRA})):
        opcoes = imp.OpcoesDeImpressao(paginas_por_caderno=8, como_imagem=False)
        for k, v in campos.items():
            setattr(opcoes, k, v)
        saida = pasta / f"{nome}.pdf"
        resultado = imp.montar_para_impressao(livro_pdf, saida, opcoes)
        numeros[nome] = {"folhas": resultado.folhas_de_papel, "paginas": resultado.paginas_do_arquivo,
                         "avisos": [a.texto for a in resultado.avisos], "instrucoes": resultado.instrucoes}
        largura, altura = imp.tamanho_do_papel_pt(opcoes)
        folhas = _paginas_do_pdf(saida, dpi=100)
        k = 100 / 72
        for i, img in enumerate(folhas[:4]):
            fora = int(imp.mm_para_pt(13) * k)
            dobra = int(imp.mm_para_pt(10) * k)
            vermelho, azul = (0, 0, 220), (220, 120, 0)
            a, l = img.shape[:2]
            if opcoes.formato == imp.LIVRETO:
                meio = l // 2
                cv2.line(img, (meio, 0), (meio, a), azul, 1)
                for x0, x1 in ((fora, meio - dobra), (meio + dobra, l - fora)):
                    cv2.rectangle(img, (x0, fora), (x1, a - fora), vermelho, 1)
            else:
                cv2.rectangle(img, (fora, fora), (l - fora, a - fora), vermelho, 1)
            cv2.imwrite(str(pasta / f"{nome}-folha{i + 1}.png"),
                        _faixa(img, [f"{nome}, lado {i + 1} (A4)",
                                     f"o livro: {frase}",
                                     "na impressão: " + (", ".join(f"{k}={v}" for k, v in campos.items())
                                                         or "tudo de fábrica"),
                                     "vermelho = margem mínima (1,3 cm do papel / 1 cm da dobra); azul = dobra"]))
    (pasta / "numeros.json").write_text(json.dumps(numeros, ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--raiz", type=Path, default=rp.RAIZ_PADRAO)
    analisador.add_argument("item", choices=["2.4", "2.6", "2.10", "2.17", "2.18"])
    opcoes = analisador.parse_args()
    rp._preparar(opcoes.raiz.resolve())
    {"2.4": item_2_4, "2.6": item_2_6, "2.10": item_2_10, "2.17": item_2_17,
     "2.18": item_2_18}[opcoes.item](opcoes.raiz)
    print("ok", opcoes.item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
