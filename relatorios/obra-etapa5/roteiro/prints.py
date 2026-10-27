"""A janela de VERDADE, fora da tela, no caminho do Kaique do zero (obra de 26/10/2026, etapa 5:
a ferramenta "Mover e redimensionar"). O caso é o do teste do Kaique de 26/10 (tarefa 5: "O texto
dessa página está deslocado; quero mover ele para o meio da folha e aumentar um pouco."): o livro
"La vida eterna" (uma CÓPIA; o original só é lido), aberto sem nada marcado → Automático só com
"Dividir" (as folhas são de livro aberto) → página 7 → tecla F (a ferramenta Mover) → arrastar a
página com o mouse → puxar um canto (aumentar) → aumentar além da beirada (o aviso do D-017 e a
parte de fora em vermelho) → voltar a 104% → "Centralizar" → gerar o PDF (pelo processar, a mesma
conta do "Confirmar e processar") e montar a tela e a página do PDF lado a lado.

Cliques, arrastos e teclas por mensagens nativas do Windows (PostMessage), prints por PrintWindow
(relatorios/obra-etapa3/roteiro/base.py). Dados e TEMP numa pasta de saida_teste/, nunca a pasta
de dados do Samuel. Guarda o PID e fecha só a própria janela (WM_CLOSE).

Uso (na worktree):
    .venv\\Scripts\\python.exe relatorios\\obra-etapa5\\roteiro\\prints.py <worktree> <prefixo>
<worktree> = o código a abrir (esta worktree, ou a cópia do código antigo para o "antes");
<prefixo> = "depois" ou "antes". Prints em relatorios/obra-etapa5/prints/.
"""
from __future__ import annotations

import copy
import os
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

WORKTREE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RAIZ
PREFIXO = sys.argv[2] if len(sys.argv) > 2 else "depois"
PRINTS = RAIZ / "relatorios" / "obra-etapa5" / "prints"
TRAB = RAIZ / "saida_teste" / "obra-etapa5" / f"janela-{PREFIXO}"
LIVRO = Path(r"D:/Livros para editar/2 - TEOLOGIA/Escatologia/La vida eterna y La profundidad del alma.pdf")
PAGINA = 6            # a página 7 (o teste do Kaique)


def _p(widget, nome: str):
    return base.print_window(widget, PRINTS / f"{PREFIXO}-{nome}.png")


def _esperar_ate(condicao, segundos=60.0) -> bool:
    for _ in range(int(segundos / 0.2)):
        if condicao():
            return True
        base.esperar(0.2)
    return condicao()


def _letra(janela, letra: str) -> None:
    vk = base.user32.VkKeyScanW(ord(letra.lower())) & 0xFF
    base.tecla(janela, vk)


def _dividir_pelo_automatico(janela, tela, projeto):
    """O Automático só com "Dividir", no livro todo, pelo clique (como na etapa 4)."""
    from PySide6.QtCore import QPoint

    from core import automatico as A

    tela.paineis.abrir("automatico")
    base.esperar(0.8)
    painel = tela.paineis.automatico
    lista = painel.lista
    item = next(lista.item(i) for i in range(lista.count())
                if lista.item(i).text().startswith(A.NOMES[A.DIVIDIR]))
    ret = lista.visualItemRect(item)
    base.clique(janela, lista.viewport(), QPoint(ret.left() + 14, ret.center().y()))
    base.esperar(0.8)
    base.conferir(painel.estado.marcadas == {A.DIVIDIR}, "Automático: só 'Dividir' marcado, pelo clique")
    base.clique(janela, painel.botao_rodar)
    _esperar_ate(lambda: janela.projeto.dividir_folhas and len(janela.projeto.paginas) > 300, 600)
    base.esperar(3.0)


def _caixa_escura(img):
    import numpy as np

    cinza = img.mean(axis=2)
    ys, xs = np.nonzero(cinza < 110)
    altura, largura = cinza.shape
    return xs.min() / largura, ys.min() / altura, (xs.max() + 1) / largura, (ys.max() + 1) / altura


def main() -> None:
    (RAIZ / "saida_teste" / "obra-etapa5").mkdir(parents=True, exist_ok=True)
    (RAIZ / "saida_teste" / "obra-etapa5" / f"pid-prints-{PREFIXO}.txt").write_text(str(os.getpid()))
    print("PID deste processo:", os.getpid(), flush=True)
    base.preparar(str(WORKTREE), str(TRAB))
    PRINTS.mkdir(parents=True, exist_ok=True)
    livro = TRAB / "La vida eterna.pdf"
    shutil.copy2(LIVRO, livro)                     # o original só é lido
    janela = base.nova_janela(1280, 657)
    _p(janela, "00-tela-dos-livros")
    janela.abrir_livro(str(livro))
    base.esperar(2.0)
    tela = janela.tela_conferir
    _esperar_ate(lambda: getattr(janela, "medida_ao_abrir", None) is None
                 or not janela.medida_ao_abrir.isRunning(), 240)
    base.esperar(1.0)
    projeto = janela.projeto
    base.conferir(not projeto.dividir_folhas and not projeto.cortar_bordas and not projeto.limpar,
                  "abrir sem nada marcado")
    _p(janela, "01-abrir-o-livro")
    _dividir_pelo_automatico(janela, tela, projeto)
    projeto = janela.projeto
    tela.ir_para_pagina(PAGINA)
    base.esperar(4.0)
    _p(janela, "02-pagina-7-o-texto-deslocado")

    if not (WORKTREE / "tests" / "test_decisoes_mover.py").exists():
        # o código antigo: a tecla F não faz nada; o "Mover conteúdo" mora no Cortar, cinza
        _letra(janela, "f")
        base.esperar(1.0)
        base.conferir(tela.aba_atual != "mover", "código antigo: não há ferramenta Mover (a tecla F não faz nada)")
        _letra(janela, "x")
        base.esperar(3.0)
        tela.paineis.abrir("props")
        base.esperar(1.0)
        base.conferir(not tela.botao_mover_conteudo.isEnabled(),
                      "código antigo: 'Mover conteúdo' cinza no Cortar (só com tamanho de folha)")
        _p(janela, "03-mover-conteudo-cinza-no-cortar")
        base.fechar(janela)
        base.gravar_resultados(TRAB)
        return

    # a ferramenta Mover pela tecla F
    _letra(janela, "f")
    base.esperar(4.0)
    vis = tela.visualizadores["mover"]
    _esperar_ate(lambda: vis._pixmap is not None and getattr(tela, "_mover_da_vez", None), 60)
    base.esperar(1.0)
    base.conferir(tela.aba_atual == "mover" and tela.paineis.propriedades.conteudo == "mover",
                  "tecla F: a ferramenta Mover, com o Propriedades dela aberto")
    base.conferir(projeto.paginas[PAGINA].tamanho_folha_cm is None
                  and vis._folha_do_mover == vis.tamanho_da_pagina_px(),
                  "sem tamanho de folha: a área branca é a própria página")
    _p(janela, "03-ferramenta-mover")

    # arrastar a página para a esquerda e para cima (o texto estava à direita e embaixo)
    from PySide6.QtCore import QPoint

    base.esperar(0.5)
    centro = vis._area.center()
    base.arrastar(janela, vis, centro, QPoint(centro.x() - int(vis._area.width() * 0.07),
                                              centro.y() - int(vis._area.height() * 0.04)))
    base.esperar(1.0)
    pagina = projeto.paginas[PAGINA]
    base.conferir(pagina.conteudo_deslocamento[0] < -0.03, f"arrastar: o conteúdo andou "
                  f"{pagina.conteudo_deslocamento}")
    _p(janela, "04-arrastada")

    # puxar o canto de baixo à direita: aumentar
    base.esperar(0.5)
    canto = vis._alcas(vis._area_do_conteudo())["se"]
    base.arrastar(janela, vis, canto, QPoint(canto.x() + int(vis._area.width() * 0.04),
                                             canto.y() + int(vis._area.height() * 0.04)))
    base.esperar(1.5)
    base.conferir(pagina.conteudo_escala > 1.03, f"puxar o canto: aumentou para {pagina.conteudo_escala:.3f}")
    _p(janela, "05-aumentada-pelo-canto")

    # aumentar além da beirada: o aviso do D-017 e a parte de fora em vermelho
    from core import analise

    tela.campo_tamanho_do_conteudo.setValue(125)
    base.esperar(2.0)
    base.conferir(analise.IMPRESSO_DE_FORA in pagina.alertas_pendentes and tela.aviso_de_fora.isVisible(),
                  "125%: aviso 'Parte do impresso fica de fora' e a frase vermelha no painel")
    _p(janela, "06-alem-da-beirada-aviso")

    # 104% e Centralizar
    tela.campo_tamanho_do_conteudo.setValue(104)
    base.esperar(1.5)
    base.clique(janela, tela.botao_centralizar)
    base.esperar(2.0)
    base.conferir(analise.IMPRESSO_DE_FORA not in pagina.alertas, "104%: o aviso saiu")
    _p(janela, "07-centralizada")

    # o PDF (a mesma conta do "Confirmar e processar") e a página 7 dele ao lado da tela
    import fitz
    import numpy as np
    from PIL import Image

    from core.pipeline import processar

    saida = copy.copy(projeto)
    saida.caminho_saida = str(TRAB / "saida.pdf")
    caminho = processar(saida)
    with fitz.open(caminho) as doc:
        indice = sum(1 for p in projeto.paginas[:PAGINA] if not p.apagada)
        pix = doc[indice].get_pixmap(dpi=60, colorspace=fitz.csRGB)
        pdf = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).copy()
    x0, y0, x1, y1 = _caixa_escura(pdf)
    base.conferir(abs(x0 - (1 - x1)) < 0.03 and abs(y0 - (1 - y1)) < 0.03,
                  f"no PDF, o impresso no meio: esquerda {x0:.3f} direita {1 - x1:.3f}, "
                  f"cima {y0:.3f} baixo {1 - y1:.3f}")
    tela_png = PRINTS / f"{PREFIXO}-07-centralizada.png"
    if tela_png.exists():
        tela_img = Image.open(tela_png).convert("RGB")
        pdf_img = Image.fromarray(pdf)
        escala = tela_img.height / pdf_img.height
        pdf_img = pdf_img.resize((max(1, int(pdf_img.width * escala)), tela_img.height))
        lado = Image.new("RGB", (tela_img.width + pdf_img.width + 20, tela_img.height), (60, 60, 60))
        lado.paste(tela_img, (0, 0))
        lado.paste(pdf_img, (tela_img.width + 20, 0))
        lado.save(PRINTS / f"{PREFIXO}-08-tela-e-pagina-do-pdf.png")
    Image.fromarray(pdf).save(PRINTS / f"{PREFIXO}-09-pagina-7-do-pdf.png")
    base.fechar(janela)
    base.gravar_resultados(TRAB)


if __name__ == "__main__":
    main()
