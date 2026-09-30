"""Monta todas as imagens do formulario relatorios/conferir-aqui-2.html (segunda conferencia, 30/09/2026).

Uso (no .venv do programa; nao muda o programa, nao roda OCR, so desenha):
    .venv\\Scripts\\python.exe relatorios\\conferencia-2-2026-09-30\\scripts\\montar_imagens.py

Grava em relatorios/conferencia-2-2026-09-30/:
- zonas/      antes x depois das zonas do OCR (zona contornada por cima da pagina ORIGINAL);
- decisoes/   um recorte para cada decisao D1-D7;
- fotos-pb/   P1: cada opcao de foto no Preto e branco ao lado do original (PNG, sem perder os pontinhos);
- pb-novo/    original x antes x agora do Preto e branco com a regra de 30/09;
- vermelho/   a pergunta dos titulos vermelhos (simulacao da conversao para cinza, ver simular_vermelho.py);
- refazer/    F6, B4 e B6 explicados de novo;
- gravuras/   opcoes de Gravuras e fotos (item 1.2, rodada relatorios/conferir/fase1-1.2-opcoes-2026-09-30);
              os prints da tela vem de print_o_que_fazer.py (rodar antes).

Le (somente leitura): gabarito/ocr-zonas.json e a copia antiga, as imagens de trabalho do 1.3
(saida_teste/ocr-1.3/imagens), gabarito/paginas/*.png, e imagens prontas de relatorios/conferir/.
Seguro mudar: recortes, textos dos rotulos, tamanhos. Nada aqui mexe em numero da regua.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "relatorios" / "fase1-1.3-comparacao-ocr-2026-09-28" / "scripts"))

import comum as C  # noqa: E402
import util_imagens as U  # noqa: E402

SAIDA = AQUI.parent
CONF = RAIZ / "relatorios" / "conferir"
Z_ANTES = json.loads((RAIZ / "gabarito" / "ocr-zonas.antes-2026-09-30.json").read_text(encoding="utf-8"))["paginas"]
Z_DEPOIS = json.loads((RAIZ / "gabarito" / "ocr-zonas.json").read_text(encoding="utf-8"))["paginas"]
ESC_ANTIGA = RAIZ / "relatorios" / "fase1-1.3-comparacao-ocr-2026-09-28" / "zonas"


def ler_rgb(caminho: Path) -> np.ndarray:
    bgr = cv2.imread(str(caminho), cv2.IMREAD_COLOR)
    if bgr is None:
        raise FileNotFoundError(caminho)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def px(ret, img):
    h, w = img.shape[:2]
    return (int(ret[0] * w), int(ret[1] * h), int(ret[2] * w), int(ret[3] * h))


def recorte(img, ret):
    x0, y0, x1, y1 = px(ret, img)
    return img[y0:y1, x0:x1]


def com_zonas(pagina: str, Z: dict) -> np.ndarray:
    img = C.ler_imagem(pagina)
    zm = C.mascaras_zonas(Z[pagina], img.shape[:2])
    return U.zonas_por_cima(img, zm)


def com_zonas_finas(pagina: str, Z: dict) -> np.ndarray:
    """Para os detalhes ampliados: linha fina (a grossa esconderia a letra)."""
    img = C.ler_imagem(pagina)
    zm = C.mascaras_zonas(Z[pagina], img.shape[:2])
    return U.zonas_por_cima(img, zm, esp=1, veu=0.10)


# --------------------------------------------------------------------------- zonas
def antes_depois_zonas(pagina: str, nome: str, detalhes: list[tuple], arquivo: str,
                       titulo_antes="ANTES (zona antiga)", titulo_depois="DEPOIS (zona corrigida)") -> None:
    """Pagina inteira antes x depois, com o lugar de cada detalhe marcado; embaixo, os detalhes."""
    a, d = com_zonas(pagina, Z_ANTES), com_zonas(pagina, Z_DEPOIS)
    for i, (ret, _rot) in enumerate(detalhes):
        texto = f"detalhe {i + 1}" if len(detalhes) > 1 else "detalhe"
        a = U.marcar(a, px(ret, a), texto=texto)
        d = U.marcar(d, px(ret, d), texto=texto)
    alt = 1000
    a, d = U.na_altura(a, alt), U.na_altura(d, alt)
    topo = U.lado_a_lado([U.rotulo(a, titulo_antes, fundo=(90, 90, 90)),
                          U.rotulo(d, titulo_depois, fundo=(0, 110, 0))])
    partes = [U.rotulo(topo, f"{nome}: zonas contornadas por cima da página original", fundo=(30, 42, 54),
                       sub=U.LEGENDA_ZONAS + " · retângulo rosa = onde fica o detalhe ampliado embaixo")]
    af, df = com_zonas_finas(pagina, Z_ANTES), com_zonas_finas(pagina, Z_DEPOIS)
    for i, (ret, rot) in enumerate(detalhes):
        ra, rd = recorte(af, ret), recorte(df, ret)
        larg = 900
        ra, rd = U.na_largura(ra, larg), U.na_largura(rd, larg)
        n = f"DETALHE {i + 1}" if len(detalhes) > 1 else "DETALHE"
        par = U.lado_a_lado([U.rotulo(U.moldura(ra), f"{n} · ANTES", fundo=(90, 90, 90)),
                             U.rotulo(U.moldura(rd), f"{n} · DEPOIS", fundo=(0, 110, 0))])
        partes.append(U.rotulo(par, rot, fundo=(80, 60, 0)))
    U.gravar(U.um_embaixo_do_outro(partes, espaco=30), SAIDA / "zonas" / arquivo, largura_max=1900)


def imagem_antiga_x_nova(pagina: str, nome: str, arquivo: str, explicacao: str) -> None:
    """A imagem da conferencia anterior (so a tinta pintada) x a zona contornada na pagina original."""
    antiga = ler_rgb(ESC_ANTIGA / f"{pagina}.jpg")
    metade = antiga[:, antiga.shape[1] // 2 + 6:]   # o painel da direita (tinta pintada)
    nova = com_zonas(pagina, Z_DEPOIS)
    alt = 1000
    metade, nova = U.na_altura(metade, alt), U.na_altura(nova, alt)
    par = U.lado_a_lado([
        U.rotulo(U.moldura(metade), "O QUE VOCÊ VIU NA CONFERÊNCIA PASSADA", fundo=(90, 90, 90),
                 sub="só aparece o risco escuro; pintura e dourado ficam brancos e parecem 'fora'"),
        U.rotulo(nova, "A ZONA DE VERDADE", fundo=(0, 110, 0),
                 sub="contornada por cima da página original, nada escondido")])
    U.gravar(U.rotulo(par, nome, sub=explicacao), SAIDA / "zonas" / arquivo, largura_max=1900)


def zonas() -> None:
    antes_depois_zonas("horas_p013", "Horas 13", [
        ((0.54, 0.56, 0.84, 0.86), "canto de baixo à direita: a moldura dourada agora fica inteira dentro do vermelho"),
        ((0.10, 0.10, 0.80, 0.30), "o alto: 'TABLE', 'DE CE QUI EST' e 'CONTENU EN CE LIVRE.' estão dentro do verde (antes também estavam)"),
    ], "z-horas13.jpg")
    imagem_antiga_x_nova("horas_p013", "Horas 13: por que parecia que a zona apagava o subtítulo e a moldura", "z-horas13-explica.jpg",
                         "A imagem da direita, na conferência passada, só mostrava o risco escuro: as letras vermelhas saíam ralas e o ouro quase sumia. A zona já pegava o subtítulo; a moldura foi ajustada para abraçar o ouro inteiro.")
    antes_depois_zonas("horas_p026", "Horas 26", [
        ((0.19, 0.62, 0.46, 0.86), "canto de baixo à esquerda: antes a linha de dentro do vermelho cortava o ouro; agora pega a faixa inteira"),
    ], "z-horas26.jpg")
    imagem_antiga_x_nova("horas_p026", "Horas 26: por que parecia que a moldura e letras ficavam de fora", "z-horas26-explica.jpg",
                         "Na imagem antiga só aparecia o risco escuro: o ouro virava tracinhos e as letras douradas ('A') ficavam ralas. As letras estavam na zona; a moldura foi ajustada.")
    antes_depois_zonas("horas_p027", "Horas 27", [
        ((0.55, 0.40, 0.81, 0.66), "lado direito: antes o verde (texto) entrava na faixa dourada; agora o ouro é vermelho e só a letra que encosta (o 't.' de 'Brabant.') fica verde"),
    ], "z-horas27.jpg")
    antes_depois_zonas("horas_p047", "Horas 47", [
        ((0.02, 0.01, 0.40, 0.30), "canto de cima à esquerda: o vermelho agora tem folga em volta de toda a pintura"),
    ], "z-horas47.jpg")
    imagem_antiga_x_nova("horas_p047", "Horas 47: a zona pega a gravura inteira", "z-horas47-explica.jpg",
                         "Na imagem antiga só o risco escuro da pintura aparecia em vermelho; as cenas pintadas pareciam de fora. A zona cobre tudo; ganhou uma folga em volta.")
    antes_depois_zonas("opusmajus_p256", "Opus Majus 256", [
        ((0.78, 0.66, 1.0, 0.93), "canto de baixo à direita: a última coluna, a borda direita da tabela e a borda de baixo agora estão dentro do verde"),
    ], "z-opus256.jpg")
    antes_depois_zonas("rhetorica_p018", "Rhetorica 18", [
        ((0.80, 0.06, 0.975, 0.20), "lado direito: antes a faixa cinza (não conta) cobria o fim das linhas ('fortaſſis', 'quæ', 'ex-'); agora o cinza é só o fio da moldura"),
        ((0.08, 0.72, 0.30, 0.86), "lado esquerdo, embaixo: a nota de margem e o começo das linhas ('Ind', 'illis') ficam inteiros no verde"),
    ], "z-rhetorica18.jpg")
    # a confirmar
    imagem_antiga_x_nova("escola_p007", "Escola 7: a zona pega a gravura inteira?", "c-escola7.jpg",
                         "Resposta: sim. O vermelho contorna a gravura inteira (céu, figuras, leão). Na imagem da conferência passada só aparecia o risco escuro.")
    antes_depois_zonas("escola_p035", "Escola 35", [
        ((0.05, 0.37, 0.42, 0.47), "embaixo da gravura: antes ficava de fora uma tirinha do pé da pintura (em cima da legenda); agora entra"),
    ], "c-escola35.jpg")
    imagem_antiga_x_nova("escola_p035", "Escola 35: a zona pega a gravura inteira?", "c-escola35-explica.jpg",
                         "Resposta: sim (depois de um ajuste de 1 mm embaixo). O pontilhado vermelho da imagem antiga era só o risco escuro.")
    antes_depois_zonas("horas_p011", "Horas 11", [
        ((0.30, 0.0, 0.70, 0.13), "o alto: o vermelho agora sobe até a ponta do enfeite de cima"),
        ((0.22, 0.26, 0.76, 0.72), "o oval do meio: o buraco (onde ficam os títulos) ficou um pouco menor, para a moldura do oval ficar toda no vermelho"),
    ], "c-horas11.jpg")
    imagem_antiga_x_nova("horas_p011", "Horas 11: o pontilhado vermelho está em toda a gravura?", "c-horas11-explica.jpg",
                         "Resposta: a zona (à direita, contorno vermelho) cobre a iluminura inteira. O pontilhado da imagem antiga era só o risco escuro da pintura.")
    antes_depois_zonas("opusmajus_p165", "Opus Majus 165", [
        ((0.62, 0.30, 0.86, 0.56), "Figura 7: as caixinhas cinzas agora pegam só as letras (a, e, f, b, c, l, h, d); as linhas do desenho ficam no vermelho, e o 'd' de baixo não sai mais pela metade"),
        ((0.60, 0.65, 0.86, 0.87), "Figura 8: idem, uma caixinha justa para cada letra a, b, c, d"),
    ], "c-opus165.jpg")
    for pg, det in (("graduale_p221", ((0.10, 0.465, 0.46, 0.545), "linha 4: as caixas verdes agora pegam as letras inteiras, com as hastes e as pernas")),
                    ("graduale_p222", ((0.20, 0.565, 0.56, 0.645), "linha 5: a palavra vermelha e a letra grande 'I' agora ficam inteiras no verde")),
                    ("graduale_p223", ((0.10, 0.565, 0.50, 0.655), "linha 5: 'mine. com Aduersum...' com as pontas das letras inteiras"))):
        antes_depois_zonas(pg, "Graduale " + pg[-3:].lstrip("0"), [det], f"c-{pg.replace('_p', '')}.jpg")


# --------------------------------------------------------------------------- decisoes
def cartao_decisao(pagina: str, nome: str, ret_det, texto_det: str, arquivo: str, extra=None) -> None:
    pag = com_zonas(pagina, Z_DEPOIS)
    pag = U.marcar(pag, px(ret_det, pag), texto="olhe aqui")
    pag = U.na_altura(pag, 900)
    det = U.na_largura(recorte(com_zonas_finas(pagina, Z_DEPOIS), ret_det), 1000)
    if extra is not None:
        det = extra(det)
    par = U.lado_a_lado([U.rotulo(pag, f"{nome}: página inteira", fundo=(60, 60, 60)),
                         U.rotulo(U.moldura(det), "DETALHE AMPLIADO", fundo=(80, 60, 0), sub=texto_det)])
    U.gravar(U.rotulo(par, nome, sub=U.LEGENDA_ZONAS), SAIDA / "decisoes" / arquivo, largura_max=1900)


def decisoes() -> None:
    cartao_decisao("palatino_p057", "D1 · Palatino 57", (0.08, 0.04, 0.84, 0.46),
                   "em cima, os laços em volta de 'Lettera Notaresca' estão no VERMELHO (figura); "
                   "embaixo, o floreio no fim do texto (setinha) está no VERDE (texto)",
                   "d1-palatino57.jpg",
                   extra=lambda im: U.seta(im, (im.shape[1] * 0.30, im.shape[0] * 0.97), (im.shape[1] * 0.47, im.shape[0] * 0.90)))
    # D2: duas capitulares lado a lado
    q = recorte(com_zonas_finas("palatino_p009", Z_DEPOIS), (0.08, 0.22, 0.46, 0.47))
    g = recorte(com_zonas_finas("graduale_p221", Z_DEPOIS), (0.33, 0.37, 0.58, 0.56))
    alt = 700
    par = U.lado_a_lado([
        U.rotulo(U.moldura(U.na_altura(q, alt)), "Palatino 9: o Q GRAVADO", fundo=(170, 0, 0),
                 sub="capitular gravada em madeira, com desenho dentro: VERMELHO (figura)"),
        U.rotulo(U.moldura(U.na_altura(g, alt)), "Graduale 221: o A A PENA", fundo=(90, 90, 90),
                 sub="capitular desenhada a mão, no meio das palavras: CINZA (não conta)")])
    U.gravar(U.rotulo(par, "D2 · Capitulares", sub=U.LEGENDA_ZONAS), SAIDA / "decisoes" / "d2-capitulares.jpg")
    cartao_decisao("escola_p007", "D3 · Escola 7", (0.10, 0.90, 0.97, 1.0),
                   "no pé da página, o endereço 'http://alexandriacatolica...' está no VERDE (conta como texto)",
                   "d3-escola7-site.jpg")
    cartao_decisao("opusmajus_p003", "D4 · Opus Majus 3", (0.30, 0.50, 0.60, 0.70),
                   "o emblema da editora, no meio da página, está no VERMELHO (figura), mesmo com letras dentro",
                   "d4-opus3-emblema.jpg")
    cartao_decisao("opusmajus_p165", "D5 · Opus Majus 165", (0.62, 0.30, 0.86, 0.56),
                   "as letrinhas do diagrama (a, e, f, b, c, l, h, d) estão em caixinhas CINZAS (não contam); as linhas do desenho estão no VERMELHO",
                   "d5-opus165-letrinhas.jpg")
    cartao_decisao("rhetorica_p018", "D6 · Rhetorica 18", (0.80, 0.03, 0.975, 0.20),
                   "o fio fino que corre ao lado do texto (o filete) está numa tira CINZA (não conta); as letras encostadas nele ficam no VERDE",
                   "d6-rhetorica-filetes.jpg")
    # D7: pauta fora de zona (hoje) x proposta (pauta vermelha)
    pg = "graduale_p222"
    img = C.ler_imagem(pg)
    zm = C.mascaras_zonas(Z_DEPOIS[pg], img.shape[:2])
    hoje = U.zonas_por_cima(img, zm, esp=1)
    prop = dict(Z_DEPOIS[pg])
    prop["nao_pode"] = [{"ret": [0.16, y0, 0.97, y1]} for y0, y1 in
                        ((0.055, 0.155), (0.19, 0.26), (0.295, 0.366), (0.40, 0.477), (0.515, 0.588),
                         (0.625, 0.703), (0.74, 0.82))]
    zp = C.mascaras_zonas(prop, img.shape[:2])
    propo = U.zonas_por_cima(img, zp, esp=1)
    ret = (0.12, 0.02, 0.98, 0.42)
    a, b = U.na_largura(recorte(hoje, ret), 900), U.na_largura(recorte(propo, ret), 900)
    par = U.lado_a_lado([
        U.rotulo(U.moldura(a), "COMO ESTÁ (decisão D7)", fundo=(0, 110, 0),
                 sub="só as palavras cantadas estão no verde; pauta e notas ficam sem zona (não contam)"),
        U.rotulo(U.moldura(b), "OUTRA OPÇÃO (não aplicada)", fundo=(170, 0, 0),
                 sub="pauta e notas no vermelho: aí uma linha do OCR em cima da música contaria como erro")])
    U.gravar(U.rotulo(par, "D7 · Graduale 222: pauta e notas", sub=U.LEGENDA_ZONAS),
             SAIDA / "decisoes" / "d7-graduale-pauta.jpg")


# --------------------------------------------------------------------------- P1 fotos
FOTOS = CONF / "fotos-no-preto-e-branco-2026-09-30"
OPCOES = [("3-tons-de-cinza", "CINZA (tons de cinza)"),
          ("4-pontilhado-floyd-steinberg", "PONTILHADO espalhado (Floyd-Steinberg)"),
          ("5-pontilhado-ordenado-bayer", "PONTILHADO em grade (Bayer)"),
          ("6-meio-tom-jornal-60-linhas", "MEIO-TOM de jornal (60 linhas)")]


def fotos_pb() -> None:
    o_or = ler_rgb(FOTOS / "opus20-1-original-ampliado.jpg")[:, 76:926]
    e_or = ler_rgb(FOTOS / "escola35-1-original-ampliado.jpg")[150:1250, 500:1400]
    for cod, nome in OPCOES:
        o = ler_rgb(FOTOS / f"opus20-{cod}-ampliado.png")[:, 76:926]
        e = ler_rgb(FOTOS / f"escola35-{cod}-ampliado.png")[150:1250, 500:1400]
        cima = U.lado_a_lado([U.rotulo(o_or, "ORIGINAL", fundo=(60, 60, 60)), U.rotulo(o, nome, fundo=(0, 70, 140))])
        baixo = U.lado_a_lado([U.rotulo(e_or, "ORIGINAL", fundo=(60, 60, 60)), U.rotulo(e, nome, fundo=(0, 70, 140))])
        tudo = U.um_embaixo_do_outro([U.rotulo(cima, "Opus Majus 20: a estátua (ampliada 3 vezes)"),
                                      U.rotulo(baixo, "Escola 35: o anjo (ampliado 3 vezes)")], espaco=40)
        caminho = SAIDA / "fotos-pb" / f"p1-{cod}.png"
        caminho.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(caminho), cv2.cvtColor(tudo, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_PNG_COMPRESSION, 9])


# --------------------------------------------------------------------------- Preto e branco novo
PB = CONF / "pb-regra-30-09" / "depois" / "1.2-2026-09-30-1031" / "paineis"


def pb_novo() -> None:
    casos = [("01-horas_p011", "Horas 11", "a iluminura em volta: antes colorida; agora vira desenho preto e branco. Veja se o desenho sai inteiro e se o título do meio continua legível."),
             ("03-horas_p026", "Horas 26", "a moldura dourada: antes ficava dourada; agora vira traço preto. Veja se ela aparece como uma moldura inteira ou em pedaços."),
             ("04-horas_p027", "Horas 27", "a moldura dourada: antes ficava dourada; agora vira traço preto. Veja se ela aparece como uma moldura inteira ou em pedaços."),
             ("02-horas_p013", "Horas 13", "a moldura dourada e o alto da página. Atenção: os títulos vermelhos 'TABLE' e 'CONTENU EN CE LIVRE.' somem (é a pergunta do cartão seguinte)."),
             ("12-graduale_p222", "Graduale 222", "a pauta e as notas: tudo em preto; veja se a música fica legível e se as linhas da pauta aparecem inteiras.")]
    for base, nome, olhar in casos:
        ims = [ler_rgb(PB / f"{base}-{k}.jpg") for k in ("1-original", "2-anterior", "3-resultado")]
        ims = [U.na_altura(i, 1000) for i in ims]
        rot = ["ORIGINAL", "ANTES (regra antiga, 10h04)", "AGORA (regra de 30/09)"]
        cores = [(60, 60, 60), (90, 90, 90), (0, 110, 0)]
        linha = U.lado_a_lado([U.rotulo(U.moldura(i), r, fundo=c) for i, r, c in zip(ims, rot, cores)])
        dets = [ler_rgb(PB / f"{base}-{k}-detalhe.jpg") for k in ("1-original", "2-anterior", "3-resultado")]
        dets = [U.na_largura(dd, 640) for dd in dets]
        linha2 = U.lado_a_lado([U.rotulo(U.moldura(dd), f"DETALHE · {r}", fundo=c) for dd, r, c in zip(dets, rot, cores)])
        U.gravar(U.um_embaixo_do_outro([U.rotulo(linha, f"{nome} no Preto e branco",
                                                 sub="retângulo rosa = o pedaço ampliado embaixo. O que olhar: " + olhar),
                                        linha2], espaco=30),
                 SAIDA / "pb-novo" / f"pb-{base[3:].replace('_p', '')}.jpg", largura_max=1950)


# --------------------------------------------------------------------------- vermelho
def vermelho() -> None:
    sim = SAIDA / "vermelho" / "simulacao"
    blocos = []
    # Simulacao pelo caminho inteiro do programa (simular_vermelho.py). O original tem outro
    # enquadramento (o programa corta e endireita), por isso dois recortes: ret_o no original,
    # ret no resultado. Medido: Graduale 221 e 222 saem IGUAIS nas duas contas (a pauta ja sai
    # preta hoje); muda so a rubrica (Horas 13, Graduale 223).
    for pg, ret_o, ret, nome in (
            ("horas_p013", (0.08, 0.10, 0.82, 0.33), (0.05, 0.08, 0.80, 0.29), "Horas 13: títulos vermelhos 'TABLE' e 'CONTENU EN CE LIVRE.'"),
            ("graduale_p223", (0.08, 0.22, 0.90, 0.34), (0.05, 0.20, 0.95, 0.32), "Graduale 223: a palavra vermelha no meio do canto (2ª linha de texto)")):
        o = cv2.imread(str(RAIZ / "gabarito" / "paginas" / f"{pg}.png"))
        o = cv2.cvtColor(o, cv2.COLOR_BGR2RGB)
        hoje = cv2.cvtColor(cv2.imread(str(sim / f"{pg}-hoje.png"), 0), cv2.COLOR_GRAY2RGB)
        muda = cv2.cvtColor(cv2.imread(str(sim / f"{pg}-vermelho-preto.png"), 0), cv2.COLOR_GRAY2RGB)
        ims = [U.na_largura(recorte(i, r), 620) for i, r in ((o, ret_o), (hoje, ret), (muda, ret))]
        rot = [("ORIGINAL", (60, 60, 60)), ("HOJE: o vermelho some", (170, 0, 0)), ("SE MUDAR: o vermelho sai preto", (0, 110, 0))]
        blocos.append(U.rotulo(U.lado_a_lado([U.rotulo(U.moldura(i), r, fundo=c) for i, (r, c) in zip(ims, rot)]), nome))
    U.gravar(U.um_embaixo_do_outro(blocos, espaco=40), SAIDA / "vermelho" / "vermelho-titulos-e-pauta.jpg", largura_max=1950)
    # o resultado do programa de hoje (Horas 13 inteira), com o lugar dos titulos marcado.
    # Usa as imagens em tamanho cheio (os paineis prontos ja tem um retangulo rosa desenhado).
    # O lugar dos titulos no resultado foi achado casando 'DE CE QUI EST' (escala 1,04 sobre
    # o resultado reduzido a 1/4); se a rodada mudar, refazer essa conta.
    o = ler_rgb(RAIZ / "gabarito" / "paginas" / "horas_p013.png")
    r = ler_rgb(PB.parent / "resultado" / "horas_p013.png")
    o = U.marcar(o, px((0.13, 0.14, 0.75, 0.275), o), texto="títulos vermelhos", esp=5)
    r = U.marcar(r, px((0.12, 0.125, 0.76, 0.265), r), cor=U.VERMELHO, texto="'TABLE' e 'CONTENU...' sumiram", esp=18, tam=110)
    par = U.lado_a_lado([U.rotulo(U.na_altura(o, 900), "ORIGINAL", fundo=(60, 60, 60)),
                         U.rotulo(U.na_altura(r, 900), "PROGRAMA DE HOJE (Preto e branco)", fundo=(170, 0, 0))])
    U.gravar(U.rotulo(par, "Horas 13 inteira, como sai hoje"), SAIDA / "vermelho" / "horas13-hoje.jpg")


# --------------------------------------------------------------------------- F6, B4, B6
def refazer() -> None:
    # F6
    t03 = ler_rgb(CONF / "fase1-2026-09-29-1826" / "verificador" / "t03-cinco-cartoes-alerta-mas-para-revisar-vazio.jpg")
    t03 = U.marcar(t03, (140, 234, 412, 892), cor=U.AZUL, texto="1º cartão: Original")
    t03 = U.marcar(t03, (1226, 234, 1500, 892), texto="5º cartão: Tirar o fundo", texto_embaixo=True)
    t15 = ler_rgb(CONF / "fase1-2026-09-29-1826" / "verificador" / "t15-comparar-mostra-tirar-fundo-de-verdade.jpg")
    t15 = U.marcar(t15, (90, 106, 827, 1024), cor=U.AZUL, texto="esquerda: Original", texto_embaixo=True, tam=40)
    t15 = U.marcar(t15, (834, 106, 1570, 1024), texto="direita: Tirar o fundo", texto_embaixo=True, tam=40)
    t15 = U.marcar(t15, (1280, 46, 1408, 104), cor=U.AMARELO, esp=5)
    t15 = U.seta(t15, (1100, 75), (1270, 75), cor=U.AMARELO)
    U.gravar(U.um_embaixo_do_outro([
        U.rotulo(t03, "1. Aba Filtro: a mesma página em cinco cartões",
                 sub="Compare o 1º cartão (azul) com o 5º (rosa): no 5º o papel já aparece branco, sem o amarelado. É isso que vai para o PDF?"),
        U.rotulo(t15, "2. Botão 'comparar' (na tela de ver de perto)",
                 sub="Com o botão 'comparar' ligado (seta amarela), a esquerda mostra o original e a direita o 'Tirar o fundo' de verdade.")], espaco=30),
        SAIDA / "refazer" / "f6-cartao-tirar-o-fundo.jpg", largura_max=1800)
    # B4
    antes = ler_rgb(CONF / "fase1-2026-09-28-1844" / "resultado" / "marial_p007.png")
    depois = ler_rgb(CONF / "fase1-2026-09-28-2058" / "resultado" / "marial_p007.png")
    faixa = (0.93, 0.0, 1.0, 1.0)
    pa = U.marcar(antes, px((0.935, 0.005, 0.998, 0.995), antes), texto="a faixa escura ficava aqui", esp=14, tam=90)
    pd = U.marcar(depois, px((0.935, 0.005, 0.998, 0.995), depois), texto="aqui", esp=14, tam=90)
    topo = U.lado_a_lado([U.rotulo(U.na_altura(pa, 1000), "ANTES do conserto", fundo=(90, 90, 90)),
                          U.rotulo(U.na_altura(pd, 1000), "DEPOIS do conserto", fundo=(0, 110, 0))])
    ret = (0.80, 0.00, 1.0, 0.30)
    da = U.na_altura(recorte(antes, ret), 800)
    dd = U.na_altura(recorte(depois, ret), 800)
    da = U.seta(da, (da.shape[1] * 0.35, da.shape[0] * 0.45), (da.shape[1] * 0.93, da.shape[0] * 0.45), esp=8)
    baixo = U.lado_a_lado([U.rotulo(U.moldura(da), "ANTES · borda direita, em cima", fundo=(90, 90, 90), sub="faixa cinza-escura (fundo do scanner)"),
                           U.rotulo(U.moldura(dd), "DEPOIS · o mesmo lugar", fundo=(0, 110, 0), sub="a faixa sumiu; fica a beirada da folha")])
    U.gravar(U.um_embaixo_do_outro([
        U.rotulo(topo, "Marial 7 no Mágico pro: a borda direita da página",
                 sub="Num conserto do corte (28/09) passou a sobrar, na borda direita, uma faixa escura do fundo do scanner. Este conserto tira a faixa."),
        baixo], espaco=30), SAIDA / "refazer" / "b4-marial7-borda-direita.jpg", largura_max=1800)
    # B6
    v2 = ler_rgb(CONF / "fase1-2026-09-28-2058-3" / "ampliacoes" / "v2-escola7-previas-e-pdf.jpg")
    y0 = 30
    paineis = [v2[y0:, 0:600], v2[y0:, 612:1171], v2[y0:, 1182:1741]]
    antiga = U.marcar(paineis[0], (4, 4, 596, 60), cor=U.VERMELHO, texto="título colado no alto", texto_embaixo=True)
    nova = U.marcar(paineis[1], (4, 4, 555, 120), texto="margem de cima", texto_embaixo=True)
    pdf = U.marcar(paineis[2], (4, 4, 555, 120), texto="margem de cima", texto_embaixo=True)
    linha = U.lado_a_lado([
        U.rotulo(U.moldura(antiga), "ANTES: o que a TELA mostrava", fundo=(170, 0, 0), sub="cortava o alto e o pé"),
        U.rotulo(U.moldura(nova), "AGORA: o que a TELA mostra", fundo=(0, 110, 0), sub="o mesmo corte do PDF"),
        U.rotulo(U.moldura(pdf), "O PDF que sai", fundo=(0, 70, 140), sub="o que vai para a impressão")])
    U.gravar(U.rotulo(linha, "Escola 7: prévia da tela × PDF",
                      sub="Antes a tela mostrava um corte e o PDF saía com outro (o PDF tinha mais margem em cima). Agora os dois são iguais."),
             SAIDA / "refazer" / "b6-previa-igual-pdf.jpg", largura_max=1800)


# --------------------------------------------------------------------------- Gravuras e fotos (1.2)
OPC = CONF / "fase1-1.2-opcoes-2026-09-30"
LIG = CONF / "fase1-1.2-ligacao-2026-09-30"
ORDEM_GRAVURA = ["original", "antigo", "A", "B", "C", "D", "E", "F", "G", "H", "I"]


def painel_da_folha(pagina: str, chave: str) -> np.ndarray:
    """Um quadro da folha 'gravura' da rodada de opcoes (rodada_opcoes_gravura.py: celulas de
    520 px + 12 de espaco, 4 por linha, faixa de rotulo de 56 px em cima). Sem o rotulo antigo."""
    folha = ler_rgb(OPC / "folhas" / f"{pagina}-gravura.jpg")
    k = ORDEM_GRAVURA.index(chave)
    linhas = (len(ORDEM_GRAVURA) + 3) // 4
    alt = (folha.shape[0] - 12 * linhas) // linhas
    x, y = (k % 4) * 532, (k // 4) * (alt + 12)
    cel = folha[y + 56:y + alt, x:x + 520]
    # corta o branco que sobra embaixo (quadros mais baixos que a linha)
    cheio = np.where(cel.min(axis=(1, 2)) < 250)[0]
    return cel[: cheio.max() + 1] if len(cheio) else cel


def livre_antes_do_conserto(pagina: str) -> np.ndarray:
    """O quadro 'ScanTailor livre' (3o de 4) da mascara da rodada de ligacao (30/09, antes do conserto)."""
    m = ler_rgb(LIG / "mascaras" / f"{pagina}.jpg")
    w = m.shape[1] // 4
    return m[34:, 2 * w + 4:3 * w - 4]


def gravuras() -> None:
    d = SAIDA / "gravuras"
    # 1. a tela "O que fazer" (prints de print_o_que_fazer.py)
    fab = ler_rgb(d / "o-que-fazer-fabrica.png")
    fot = ler_rgb(d / "o-que-fazer-tem-fotos.png")
    grupo = (62, 294, 862, 462)
    fab_m = U.marcar(fab, grupo, texto="grupo 'Gravuras e fotos'", texto_embaixo=True, tam=30)
    det = U.na_largura(fot[grupo[1]:grupo[3], grupo[0]:grupo[2]], 1400)
    U.gravar(U.um_embaixo_do_outro([
        U.rotulo(fab_m, "Tela 'O que fazer' (de fábrica)", sub="retângulo rosa = o grupo novo 'Gravuras e fotos'"),
        U.rotulo(U.moldura(det), "O GRUPO AMPLIADO, com 'Este livro tem fotos' marcada",
                 sub="a Sensibilidade só fica ligada quando 'Este livro tem fotos' está marcada")], espaco=30),
        d / "g1-o-que-fazer.jpg", largura_max=1500)
    # 2. Opus Majus 20: sem fotos (A) x com fotos (E), Magico pro
    o = ler_rgb(RAIZ / "gabarito" / "paginas" / "opusmajus_p020.png")
    a = ler_rgb(OPC / "resultado" / "opusmajus_p020-magico_pro-A.png")
    e = ler_rgb(OPC / "resultado" / "opusmajus_p020-magico_pro-E.png")
    ret = (0.20, 0.18, 0.95, 0.62)
    ret_o = (0.32, 0.23, 0.855, 0.565)  # o mesmo lugar no original, que tem margem em volta da foto
    ims = [U.na_altura(i, 900) for i in (o, a, e)]
    ims = [U.marcar(im, px(r, im), texto="a estátua", esp=4, tam=26) for im, r in zip(ims, (ret_o, ret, ret))]
    topo = U.lado_a_lado([U.rotulo(ims[0], "ORIGINAL", fundo=(60, 60, 60)),
                          U.rotulo(ims[1], "SEM 'tem fotos' (fábrica)", fundo=(170, 0, 0)),
                          U.rotulo(ims[2], "COM 'Este livro tem fotos'", fundo=(0, 110, 0))])
    dets = [U.na_largura(recorte(i, r), 560) for i, r in ((o, ret_o), (a, ret), (e, ret))]
    baixo = U.lado_a_lado([U.rotulo(U.moldura(dd), t, fundo=c) for dd, t, c in zip(
        dets, ("DETALHE · ORIGINAL", "DETALHE · SEM 'tem fotos'", "DETALHE · COM 'tem fotos'"),
        ((60, 60, 60), (170, 0, 0), (0, 110, 0)))])
    U.gravar(U.um_embaixo_do_outro([U.rotulo(topo, "Opus Majus 20 no Mágico pro: a estátua",
                                              sub="sem 'tem fotos' a estátua sai lavada e o fundo escuro pontilhado; com 'tem fotos' fica quase igual ao original"),
                                     baixo], espaco=30), d / "g2-opus20-tem-fotos.jpg", largura_max=1900)
    # 3. Graduale 222: a pauta nao e mais gravura
    zz = [U.na_altura(i, 800) for i in (livre_antes_do_conserto("graduale_p222"), painel_da_folha("graduale_p222", "A"))]
    zona = U.lado_a_lado([U.rotulo(U.moldura(zz[0]), "ANTES: onde o programa achava gravura", fundo=(170, 0, 0), sub="vermelho = gravura: pedaços da pauta"),
                          U.rotulo(U.moldura(zz[1]), "AGORA", fundo=(0, 110, 0), sub="nenhuma gravura: a pauta é tratada como escrita")])
    mp_a = ler_rgb(LIG / "2-depois-magico-pro" / "1.2-2026-09-30-0023" / "resultado" / "graduale_p222.png")
    mp_d = ler_rgb(OPC / "resultado" / "graduale_p222-magico_pro-A.png")
    pb_a = ler_rgb(LIG / "4-depois-preto-e-branco" / "1.2-2026-09-30-0034" / "resultado" / "graduale_p222.png")
    pb_d = ler_rgb(OPC / "resultado" / "graduale_p222-preto_e_branco-A.png")
    retg = (0.55, 0.40, 1.0, 0.68)
    cel = []
    for img, t, c in ((mp_a, "MÁGICO PRO · ANTES", (170, 0, 0)), (mp_d, "MÁGICO PRO · AGORA", (0, 110, 0)),
                      (pb_a, "PRETO E BRANCO · ANTES", (170, 0, 0)), (pb_d, "PRETO E BRANCO · AGORA", (0, 110, 0))):
        cel.append(U.rotulo(U.moldura(U.na_largura(recorte(img, retg), 440)), t, fundo=c))
    U.gravar(U.um_embaixo_do_outro([
        U.rotulo(zona, "Graduale 222: a pauta não é mais gravura"),
        U.rotulo(U.lado_a_lado(cel, espaco=12), "Detalhe do lado direito, no meio da página",
                 sub="antes, os pedaços de pauta tomados por gravura saíam diferentes do resto. "
                     "O Preto e branco AGORA também já tem a regra de 30/09 (pauta preta).")], espaco=30),
        d / "g3-graduale222-pauta.jpg", largura_max=1900)
    # 4. Horas 13: a moldura inteira
    antes_z, agora_z = livre_antes_do_conserto("horas_p013"), painel_da_folha("horas_p013", "A")
    zz = [U.na_altura(i, 900) for i in (antes_z, agora_z)]
    par = U.lado_a_lado([U.rotulo(U.moldura(zz[0]), "ANTES do conserto", fundo=(170, 0, 0), sub="vermelho = gravura: só um fio; boa parte do ouro fica de fora"),
                         U.rotulo(U.moldura(zz[1]), "AGORA", fundo=(0, 110, 0), sub="a faixa dourada inteira")])
    dz = [U.na_largura(recorte(i, (0.55, 0.62, 1.0, 1.0)), 620) for i in (antes_z, agora_z)]
    dpar = U.lado_a_lado([U.rotulo(U.moldura(dz[0]), "DETALHE · ANTES", fundo=(170, 0, 0)),
                          U.rotulo(U.moldura(dz[1]), "DETALHE · AGORA", fundo=(0, 110, 0))])
    U.gravar(U.um_embaixo_do_outro([
        U.rotulo(par, "Horas 13: onde o programa acha a gravura (vermelho)",
                 sub="olhe a moldura dourada: agora ela é pega inteira. Sobra um triângulo pequeno sobre 'pag. 54' (canto de baixo à direita)."),
        U.rotulo(dpar, "Canto de baixo à direita, ampliado")], espaco=30), d / "g4-horas13-moldura.jpg", largura_max=1900)
    # 5. "Procurar tambem imagens claras": o que ela estraga
    blocos = []
    for pg, nome, frase in (("marial_p153", "Marial 153 (página só de texto)", "marca 13% da página, com texto, como gravura"),
                            ("palatino_p009", "Palatino 9", "marca a moldura e o papel (24% da página) como gravura")):
        ims = [U.na_altura(painel_da_folha(pg, k), 800) for k in ("A", "B")]
        blocos.append(U.rotulo(U.lado_a_lado([
            U.rotulo(U.moldura(ims[0]), "DESMARCADA (fábrica)", fundo=(0, 110, 0)),
            U.rotulo(U.moldura(ims[1]), "MARCADA: 'Procurar também imagens claras'", fundo=(170, 0, 0), sub=frase)]),
            nome, sub="vermelho = onde o programa acha gravura"))
    U.gravar(U.um_embaixo_do_outro(blocos, espaco=40), d / "g5-imagens-claras.jpg", largura_max=1900)


if __name__ == "__main__":
    etapas = sys.argv[1:] or ["zonas", "decisoes", "fotos_pb", "pb_novo", "vermelho", "refazer", "gravuras"]
    for e in etapas:
        globals()[e]()
        print("feito:", e)
