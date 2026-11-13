"""Quadrados na capa (13/11/2026): monta as imagens do relatorio, no modelo do girar
(scripts/pecas_imagem.py), a partir do que rodar_capa.py, pb_da_versao.py e misto_da_versao.py
gravaram em _trabalho/.

    python montar.py
Grava em imagens/ e escreve imagens/legendas.json (uma frase por imagem: o que olhar)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import pecas_imagem as P  # noqa: E402

R = AQUI.parent
T = R / "_trabalho"
SAIDA = R / "imagens"
LEG: dict = {}

# a caixa do defeito no alto da capa do Gradus (fracoes da pagina dupla), e o pedaco ampliado
ALVO_13_01 = (0.64, 0.0, 0.90, 0.12)
ALVO_13_02 = (0.755, 0.0, 0.86, 0.085)
ZOOM = (0.55, 0.0, 0.97, 0.30)


def no_zoom(caixa, zoom=ZOOM):
    zx0, zy0, zx1, zy1 = zoom
    x0, y0, x1, y1 = caixa
    return ((x0 - zx0) / (zx1 - zx0), (y0 - zy0) / (zy1 - zy0),
            (x1 - zx0) / (zx1 - zx0), (y1 - zy0) / (zy1 - zy0))


def faixa_gradus(rotulo, cor, legenda, arquivo: Path, alvo, circular=True):
    """Uma faixa: a pagina dupla inteira (pequena) e o alto da capa ampliado, com o circulo."""
    img = P.abrir(arquivo)
    inteira = P.caber(img, 640, 460)
    if circular:
        inteira = P.circular(inteira, alvo, folga=0.25, espessura=5)
    pedaco = P.caber(P.recorte(img, ZOOM), 780, 460)
    if circular:
        pedaco = P.circular(pedaco, no_zoom(alvo), folga=0.2)
    linha = P.lado_a_lado([P.com_titulo(inteira, "a capa aberta (página 1)"),
                           P.com_titulo(pedaco, "o alto da capa, ampliado", vermelho=circular)])
    return P.empilhar([P.cabeca(rotulo, cor, legenda), linha], espaco=6)


def imagem_13_01():
    partes = [P.cabeca("13-01 — Preto e branco, \"Respeitar\" desmarcada", P.CINZA,
                       "Gradus Primus, página 1 (a capa aberta), livro novo, Preto e branco escolhido à "
                       "mão, \"Respeitar as gravuras achadas\" desmarcada (o filtro vale na página "
                       "inteira, D-586). Olhe o alto da capa azul, circulado.")]
    partes.append(faixa_gradus(
        "ANTES da obra (programa de 26/10)", P.AZUL,
        "A capa sai toda preta, com as letras brancas. Sem retângulos brancos.",
        T / "pbversoes" / "obra-etapa1-antes.png", ALVO_13_01))
    partes.append(faixa_gradus(
        "HOJE (versão de teste)", P.LARANJA,
        "Como no seu print 13-01: a capa preta com retângulos brancos no alto (perto de \"PAU\"), "
        "degraus pretos e a beirada da direita branca.",
        T / "hoje" / "pb+samuel+resp0" / "pdf.png", ALVO_13_01))
    partes.append(faixa_gradus(
        "HOJE sem o passo da \"sombra\" (simulação)", P.VERDE,
        "Só o passo novo de 27/10 (a sombra da foto de celular) tirado: a capa volta a sair preta e "
        "lisa, como antes. O resto do programa igual.",
        T / "sem_quadros" / "pb+samuel+resp0" / "pdf.png", ALVO_13_01))
    img = P.empilhar(partes, espaco=10)
    P.salvar(img, SAIDA / "1-print-13-01.png")
    LEG["1-print-13-01.png"] = ("13-01: os retângulos brancos no alto da capa só existem na faixa "
                                "laranja (hoje); antes da obra e sem o passo da sombra, a capa é preta lisa.")


def imagem_13_02():
    partes = [P.cabeca("13-02 — Preto e branco com \"Só as letras\"", P.CINZA,
                       "Gradus Primus, página 1, Preto e branco com \"Só as letras\" ligado (\"Guardar "
                       "a tinta forte\", de fábrica). Olhe a caixa sobre \"RÓNAI\", circulada.")]
    partes.append(faixa_gradus(
        "ANTES da obra (programa de 26/10)", P.AZUL,
        "A capa fica azul, mas já havia uma caixa PRETA sobre \"ÓNAI\" (o buraco já existia; só a cor "
        "mudou).",
        T / "mistoversoes" / "obra-etapa1-antes.png", ALVO_13_02))
    partes.append(faixa_gradus(
        "HOJE (versão de teste)", P.LARANJA,
        "Como no seu print 13-02: a mesma caixa, agora BRANCA, com um pedacinho preto embaixo.",
        T / "hoje" / "pb+samuel+resp0+letras1" / "pdf.png", ALVO_13_02))
    partes.append(faixa_gradus(
        "HOJE sem o passo da \"sombra\" (simulação)", P.VERDE,
        "Sem o passo de 27/10 a caixa volta a ser PRETA: o passo da sombra explica a cor branca, "
        "mas não o buraco.",
        T / "sem_quadros" / "pb+samuel+resp0+letras1" / "pdf.png", ALVO_13_02))
    c = T / "matriz" / "quadrados-c" / "gradus" / "pb+samuel+resp0+letras1" / "pdf.png"
    if not c.exists():
        c = T / "mistoversoes" / "quadrados-c.png"
    partes.append(faixa_gradus(
        "Conserto C (D-668, ainda fora da versão de teste)", P.ROXO,
        "Igual a hoje: o conserto C não mexe no Preto e branco.", c, ALVO_13_02))
    img = P.empilhar(partes, espaco=10)
    P.salvar(img, SAIDA / "2-print-13-02.png")
    LEG["2-print-13-02.png"] = ("13-02: a caixa sobre \"ÓNAI\" era preta antes da obra e ficou branca "
                                "hoje; tirando o passo da sombra ela volta a ser preta; o conserto C não muda.")


def imagem_marcacao():
    img = P.abrir(T / "marcacao_samuel.png")
    inteira = P.circular(P.caber(img, 900, 640), ALVO_13_02, folga=0.3, espessura=5)
    pedaco = P.circular(P.caber(P.recorte(img, ZOOM), 520, 640), no_zoom(ALVO_13_02), folga=0.2)
    linha = P.lado_a_lado([P.com_titulo(inteira, "o que o programa achou (página 1)"),
                           P.com_titulo(pedaco, "o alto da capa", vermelho=True)])
    partes = [P.cabeca("De onde vem o buraco do 13-02", P.CINZA,
                       "A marcação guardada no seu projeto (cópia), desenhada sobre o original. Verde: a "
                       "gravura achada (a capa). Vermelho: os pedaços que o programa achou como LETRA. "
                       "No alto da capa, o pedaço \"ÓNAI\" de \"PAULO RÓNAI\" foi achado como letra e "
                       "recortado da gravura (o degrau no contorno verde)."), linha,
              P.texto("Com \"Só as letras\", tudo o que é letra vira preto e branco. Por isso esse "
                      "retângulo sai do preto e branco, no meio da capa colorida. A regra que faz a letra "
                      "ganhar da gravura é de 30/09 (item 1.2, feita para as legendas sobre o cartão "
                      "colorido da Pesel).")]
    P.salvar(P.empilhar(partes, espaco=10), SAIDA / "3-de-onde-vem-o-buraco.png")
    LEG["3-de-onde-vem-o-buraco.png"] = ("O pedaço \"ÓNAI\" achado como letra (vermelho) fura a gravura da "
                                         "capa (verde): é ali que o 13-02 abre a caixa.")


def imagem_tela_cartao_pdf():
    partes = [P.cabeca("Tela, cartão do filtro e PDF", P.CINZA,
                       "Os mesmos dois casos desenhados como a tela (prévia), o cartão do painel Filtro e o "
                       "PDF. O defeito aparece nos três (a mesma conta, D-473).")]
    for rotulo, cor, var in (("13-01 (Respeitar desmarcada)", P.LARANJA, "pb+samuel+resp0"),
                             ("13-02 (Só as letras)", P.LARANJA, "pb+samuel+resp0+letras1")):
        alvo = ALVO_13_01 if var.endswith("resp0") else ALVO_13_02
        cel = []
        for nome, titulo in (("previa", "tela (prévia)"), ("cartao", "cartão / miniatura"),
                             ("pdf", "PDF")):
            img = P.abrir(T / "hoje" / var / f"{nome}.png")
            cel.append(P.com_titulo(P.circular(P.caber(P.recorte(img, ZOOM), 440, 330),
                                               no_zoom(alvo), folga=0.2, espessura=5), titulo,
                                    vermelho=True))
        partes.append(P.empilhar([P.cabeca(rotulo, cor, ""), P.lado_a_lado(cel)], espaco=6))
    P.salvar(P.empilhar(partes, espaco=10), SAIDA / "4-tela-cartao-pdf.png")
    LEG["4-tela-cartao-pdf.png"] = ("O mesmo retângulo branco na tela, no cartão do filtro e no PDF: não é "
                                    "diferença de tela, sai assim no livro.")


def main():
    SAIDA.mkdir(exist_ok=True)
    imagem_13_01()
    imagem_13_02()
    imagem_marcacao()
    imagem_tela_cartao_pdf()
    try:
        import montar_matriz
        montar_matriz.montar(T, SAIDA, LEG)
    except ImportError:
        pass
    (SAIDA / "legendas.json").write_text(json.dumps(LEG, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ok", sorted(LEG))


if __name__ == "__main__":
    main()
