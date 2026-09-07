"""Bateria de conferencia: tudo que o programa faz, em imagens, num lugar so.

    .venv\\Scripts\\python.exe teste_completo.py

Grava uma pasta em TESTES EDITOR DE IMPRESSAO com quatro partes:

  1 FILTROS SOZINHOS      os quatro filtros, sem selecao nenhuma
  2 SELECAO SOZINHA       o que o programa marca, sem filtro nenhum
  3 OS DOIS JUNTOS        o filtro lendo a marcacao
  4 AS FERRAMENTAS        cor, filtro por pedaco, folha em branco, capa

Separar importa: quando os dois erram juntos, nao da para saber de quem e a
culpa. Sozinhos, da.

As paginas vem de saida-avaliacao/paginas, o cache da regua da selecao. Para
enche-lo, rode antes o avaliar_selecao.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import relatorio  # noqa: E402
from core import filtros as F  # noqa: E402
from core.cadernos import conferir_sequencia  # noqa: E402
from core.detectar_regioes import detectar  # noqa: E402
from core.selecao import (  # noqa: E402
    GRAVURA,
    LETRA,
    MAO,
    PAPEL,
    RETANGULO,
    Regiao,
    Selecao,
)

PAGINAS = RAIZ / "saida-avaliacao" / "paginas"

# Uma pagina de cada tipo dificil, cobrindo os nove livros. O texto e o que se
# deve olhar - escrito olhando a pagina, nao o resultado.
CASOS = [
    ("Sobre_a_Consolacao_da_Filoso-p33.png", "Boecio", 33,
     "amarelada com a mancha do verso atravessando",
     "A mancha do verso tem de sumir. Era o caso mais dificil do Kaique."),
    ("Sobre_a_Consolacao_da_Filoso-p17.png", "Boecio", 17,
     "texto impresso em papel amarelado", "Papel branco, letra preta e redonda."),
    ("Rhetorica_Christiana_-__Fray-p223.png", "Rhetorica", 223,
     "texto com notas de margem e mancha de papel velho",
     "A mancha tem de sumir sem virar gravura, e as notas tem de sobreviver."),
    ("Rhetorica_Christiana_-__Fray-p112.png", "Rhetorica", 112,
     "xilogravura emoldurada embaixo de um bloco de texto",
     "A hachura da gravura tem de sobreviver; o texto tem de ficar preto."),
    ("Na_escola_de_Jesus_-_Catecis-p199.png", "Catecismo", 199,
     "estampa colorida de pagina inteira, sem uma letra",
     "A cor tem de ficar viva. No Preto e branco ela NAO pode ser binarizada."),
    ("Graduale_-_Saeculum_XIV-p376.png", "Graduale", 376,
     "partitura manuscrita com letra ocre e pautas vermelhas",
     "Veja se as pautas vermelhas viram barra preta no Preto e branco."),
    ("Graduale_-_Saeculum_XIV-p126.png", "Graduale", 126,
     "partitura manuscrita, a que o detector confunde com desenho",
     "Esta e a pagina que o programa marca errado. Ela avisa da duvida."),
    ("Marial_de_sermoens_-_Frei_Ba-p756.png", "Marial", 756,
     "texto de letra grossa, o oposto do Boecio",
     "Letra grossa: o traco nao pode afinar nem a barriga do 'o' entupir."),
    ("Marial_de_sermoens_-_Frei_Ba-p454.png", "Marial", 454,
     "texto de letra grossa em duas colunas",
     "Mesma coisa: o traco tem de aguentar."),
    ("POINTS_d_ANCIENNES_BRODERIES-p73.png", "Pesel", 73,
     "foto de bordado com titulo impresso e quatro legendas",
     "A foto e gravura; o titulo e as legendas sao texto."),
    ("Schon_Neues_Modell_Buch_-_Jo-p133.png", "Siebmacher", 133,
     "prancha de padrao de bordado", "O padrao nao pode virar mancha preta."),
    ("Livro_de_Horas_-_Luis_XIV-p3.png", "Horas", 3,
     "capa de couro verde com fechos dourados",
     "A capa tem de sair inteira nos quatro filtros."),
    ("Giovambattista_Palatino-p1.png", "Palatino", 1,
     "capa de madeira com veio", "Idem: capa nunca vira folha branca."),
    ("Sobre_a_Consolacao_da_Filosofia-p50.png", "Boecio", 50,
     "pergaminho da encadernacao, sem uma marca",
     "Foi a pagina do bug antigo: sem marcacao nenhuma, saia como folha branca. "
     "Tem de sair inteira - e para transformar em branco existe a ferramenta."),
    ("Sobre_a_Consolacao_da_Filoso-p9.png", "Boecio", 9,
     "rosto do livro, letra grande e vinheta",
     "A vinheta e gravura; o titulo e letra."),
    ("Sobre_a_Consolacao_da_Filoso-p41.png", "Boecio", 41,
     "texto corrido em papel amarelado", "Papel branco sem comer a letra."),
    ("Rhetorica_Christiana-p446.png", "Rhetorica", 446,
     "texto com iniciais gravadas",
     "As iniciais sao gravura dentro de um bloco de texto."),
    ("Graduale_-_Saeculum_XIV-p750.png", "Graduale", 750,
     "partitura manuscrita, folha escura",
     "Pergaminho escuro: o Preto e branco costuma sujar aqui."),
    ("Graduale_-_Saeculum_XIV-p1.png", "Graduale", 1,
     "capa do manuscrito", "Capa: sai inteira, nao vira folha branca."),
    ("POINTS_d_ANCIENNES_BRODERIES-p16.png", "Pesel", 16,
     "foto de bordado em meio-tom", "Meio-tom nao pode virar mancha preta."),
    ("POINTS_d_ANCIENNES_BRODERIES-p46.png", "Pesel", 46,
     "foto de bordado com legenda", "A legenda tem de ficar legivel."),
    ("POINTS_d_ANCIENNES_BRODERIES-p76.png", "Pesel", 76,
     "prancha de bordado clara", "O fio claro nao pode sumir no branco."),
    ("POINTS_d_ANCIENNES_BRODERIES-p92.png", "Pesel", 92,
     "prancha de bordado escura", "O fundo escuro nao pode entupir o desenho."),
    ("POINTS_d_ANCIENNES_BRODERIES-p1.png", "Pesel", 1,
     "capa do album", "Capa."),
    ("Schon_Neues_Modell_Buch_-_Jo-p45.png", "Siebmacher", 45,
     "prancha de padrao com quadriculado fino",
     "O quadriculado e o que mais entope. Olhe de perto."),
    ("Schon_Neues_Modell_Buch_-_Jo-p89.png", "Siebmacher", 89,
     "prancha de padrao", "Idem."),
    ("Schon_Neues_Modell_Buch_-_Jo-p177.png", "Siebmacher", 177,
     "prancha de padrao com moldura", "A moldura tem de fechar."),
    ("Schon_Neues_Modell_Buch_-_Jo-p221.png", "Siebmacher", 221,
     "prancha de padrao com rampa de iluminacao",
     "Foi a pagina que reprovava por 1,6% de sombra na regua."),
    ("Schon_Neues_Modell_Buch_-_Jo-p268.png", "Siebmacher", 268,
     "prancha de padrao no fim do livro", "Idem."),
    ("Schon_Neues_Modell_Buch_-_Jo-p1.png", "Siebmacher", 1,
     "capa", "Capa."),
    ("Marial_de_sermoens_-_Frei_Ba-p1.png", "Marial", 1,
     "capa de couro", "Capa."),
    ("Giovambattista_Palatino_citt-p132.png", "Palatino", 132,
     "folha quase em branco, com marca-d'agua e uma anotacao a lapis",
     "Tem de ir a branco. A anotacao a lapis no pe da folha nao pode sumir."),
    ("Livro_de_Horas_-_Luis_XIV-p1.png", "Horas", 1,
     "capa do livro de horas", "Capa."),
]


def _rotular(img: np.ndarray, texto: str, altura: int = 460) -> np.ndarray:
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    h, w = img.shape[:2]
    nova = cv2.resize(img, (max(1, int(w * altura / h)), altura),
                      interpolation=cv2.INTER_AREA)
    tela = np.full((altura + 28, nova.shape[1], 3), 255, np.uint8)
    tela[28:, :] = nova
    cv2.putText(tela, texto, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.48,
                (0, 0, 0), 1, cv2.LINE_AA)
    return tela


def _lado_a_lado(pedacos: list[np.ndarray]) -> np.ndarray:
    largura = sum(p.shape[1] for p in pedacos) + 10 * (len(pedacos) - 1)
    altura = max(p.shape[0] for p in pedacos)
    tela = np.full((altura, largura, 3), 255, np.uint8)
    x = 0
    for p in pedacos:
        tela[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1] + 10
    return tela


def _marcado(img: np.ndarray, selecao) -> np.ndarray:
    altura, largura = img.shape[:2]
    saida = img.copy()
    for tipo, cor in ((GRAVURA, (60, 60, 200)), (LETRA, (200, 90, 40))):
        onde = selecao.mascara(altura, largura, tipo) > 0
        if onde.any():
            camada = np.zeros_like(saida)
            camada[onde] = cor
            saida = cv2.addWeighted(saida, 0.6, camada, 0.4, 0)
    return saida


def parte_1_filtros_sozinhos(destino: Path) -> list[str]:
    """Os quatro filtros SEM selecao. Culpa do filtro, e de mais ninguem."""
    pasta = destino / "1 - filtros sozinhos"
    pasta.mkdir(parents=True, exist_ok=True)
    notas = []
    for arquivo, livro, pagina, o_que_e, o_que_olhar in CASOS:
        caminho = PAGINAS / arquivo
        if not caminho.exists():
            notas.append(f"- {livro} {pagina} - faltou a pagina no cache")
            continue
        img = cv2.imread(str(caminho), cv2.IMREAD_COLOR)
        pedacos = [_rotular(img, "original")]
        for filtro in (F.PRETO_E_BRANCO, F.MELHORAR, F.MAGICO_PRO):
            saida, mono = F.aplicar_filtro(img.copy(), filtro)
            pedacos.append(_rotular(
                saida, F.NOMES_AMIGAVEIS[filtro] + (" (1 bit)" if mono else "")))
        cv2.imwrite(str(pasta / f"{livro} {pagina} - {o_que_e[:40]}.png"),
                    _lado_a_lado(pedacos))
        notas.append(f"- **{livro} {pagina}** ({o_que_e}) - {o_que_olhar}")
    return notas


def parte_2_selecao_sozinha(destino: Path) -> list[str]:
    """O que o programa marca, sem filtro nenhum por cima."""
    pasta = destino / "2 - selecao sozinha"
    pasta.mkdir(parents=True, exist_ok=True)
    notas = []
    for arquivo, livro, pagina, o_que_e, _o in CASOS:
        caminho = PAGINAS / arquivo
        if not caminho.exists():
            continue
        img = cv2.imread(str(caminho), cv2.IMREAD_COLOR)
        selecao = detectar(img)
        altura, largura = img.shape[:2]
        gravura = selecao.mascara(altura, largura, GRAVURA).mean()
        letra = selecao.mascara(altura, largura, LETRA).mean()
        duvida = getattr(selecao, "em_duvida", False)
        marca = " - EM DUVIDA" if duvida else ""
        cv2.imwrite(str(pasta / f"{livro} {pagina}{marca}.png"),
                    _lado_a_lado([_rotular(img, "original"),
                                  _rotular(_marcado(img, selecao),
                                           f"gravura {gravura:.0%}, letra {letra:.0%}")]))
        notas.append(
            f"- **{livro} {pagina}** ({o_que_e}) - gravura {gravura:.0%}, "
            f"letra {letra:.0%}{', **o programa avisou que nao tem certeza**' if duvida else ''}")
    return notas


def parte_3_os_dois_juntos(destino: Path) -> list[str]:
    """O filtro lendo a marcacao - que e como o programa roda de verdade."""
    pasta = destino / "3 - filtro lendo a selecao"
    pasta.mkdir(parents=True, exist_ok=True)
    notas = []
    for arquivo, livro, pagina, o_que_e, _o in CASOS:
        caminho = PAGINAS / arquivo
        if not caminho.exists():
            continue
        img = cv2.imread(str(caminho), cv2.IMREAD_COLOR)
        selecao = detectar(img)
        pedacos = [_rotular(img, "original"),
                   _rotular(_marcado(img, selecao), "o que o programa marcou")]
        for filtro in (F.PRETO_E_BRANCO, F.MELHORAR, F.MAGICO_PRO):
            saida, mono = F.aplicar_filtro_com_selecao(
                img.copy(), filtro, selecao)
            pedacos.append(_rotular(
                saida, F.NOMES_AMIGAVEIS[filtro] + (" (1 bit)" if mono else "")))
        cv2.imwrite(str(pasta / f"{livro} {pagina}.png"), _lado_a_lado(pedacos))
        notas.append(f"- **{livro} {pagina}** ({o_que_e})")
    return notas


def parte_4_ferramentas(destino: Path) -> list[str]:
    """As ferramentas de marcar a mao."""
    pasta = destino / "4 - as ferramentas"
    pasta.mkdir(parents=True, exist_ok=True)
    notas = []

    from PySide6.QtWidgets import QApplication

    from ui.widgets.editor_selecao import (
        FERRAMENTA_COR,
        FERRAMENTA_VARINHA,
        EditorSelecao,
    )

    QApplication.instance() or QApplication([])

    caminho = PAGINAS / "Graduale_-_Saeculum_XIV-p126.png"
    if caminho.exists():
        img = cv2.imread(str(caminho), cv2.IMREAD_COLOR)
        altura, largura = img.shape[:2]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        vermelho = (hsv[:, :, 1] > 110) & ((hsv[:, :, 0] < 12) | (hsv[:, :, 0] > 168))
        ys, xs = np.nonzero(vermelho)
        ponto = (xs[len(xs) // 2] / largura, ys[len(ys) // 2] / altura)
        pedacos = [_rotular(img, "original")]
        for ferramenta, rotulo in ((FERRAMENTA_VARINHA, "varinha comum"),
                                   (FERRAMENTA_COR, "pegar tudo desta cor")):
            editor = EditorSelecao()
            editor.definir_imagem(img)
            editor.definir_ferramenta(ferramenta)
            editor.definir_tipo(GRAVURA)
            if ferramenta == FERRAMENTA_VARINHA:
                editor._varinha(ponto)
            else:
                editor._tudo_desta_cor(ponto)
            onde = editor.selecao.mascara(altura, largura, GRAVURA)
            pedacos.append(_rotular(_marcado(img, editor.selecao),
                                    f"{rotulo} - {onde.mean():.1%}"))
        cv2.imwrite(str(pasta / "escolher por cor.png"), _lado_a_lado(pedacos))
        notas.append("- **escolher por cor** - a varinha comum vaza pelo "
                     "pergaminho e leva a folha toda; a nova pega so o vermelho.")

    caminho = PAGINAS / "Rhetorica_Christiana_-__Fray-p112.png"
    if caminho.exists():
        img = cv2.imread(str(caminho), cv2.IMREAD_COLOR)
        selecao = Selecao()
        selecao.acrescentar(Regiao(
            tipo=GRAVURA, forma=RETANGULO, pontos=[(0.06, 0.36), (0.94, 0.93)],
            origem=MAO, filtro=F.ORIGINAL))
        saida, _mono = F.aplicar_filtro_com_selecao(
            img.copy(), F.PRETO_E_BRANCO, selecao)
        cv2.imwrite(str(pasta / "filtro so no pedaco.png"), _lado_a_lado([
            _rotular(img, "original"),
            _rotular(saida, "folha em Preto e branco, gravura no Original")]))
        notas.append("- **filtro so no pedaco** - o texto binarizado e a "
                     "gravura em tom continuo, na mesma folha.")

    caminho = PAGINAS / "Sobre_a_Consolacao_da_Filoso-p1.png"
    if caminho.exists():
        img = cv2.imread(str(caminho), cv2.IMREAD_COLOR)
        protegida, _m = F.aplicar_filtro_com_selecao(
            img.copy(), F.PRETO_E_BRANCO, detectar(img))
        so_papel = Selecao()
        so_papel.acrescentar(Regiao(tipo=PAPEL, forma=RETANGULO,
                                    pontos=[(0.0, 0.0), (1.0, 1.0)], origem=MAO))
        branca, _m2 = F.aplicar_filtro_com_selecao(
            img.copy(), F.PRETO_E_BRANCO, so_papel)
        cv2.imwrite(str(pasta / "capa protegida ou em branco.png"), _lado_a_lado([
            _rotular(img, "original"),
            _rotular(protegida, "sozinho: a capa sai inteira"),
            _rotular(branca, "marcada papel: sai em branco")]))
        notas.append("- **capa protegida ou em branco** - sozinho o programa "
                     "protege a capa; marcando a folha como papel ela sai branca.")
    return notas


def parte_5_bugs(destino: Path) -> tuple[list[str], bool]:
    """Os casos de falha: o programa nao pode fechar nem perder trabalho."""
    import subprocess

    saida = subprocess.run(
        [sys.executable, str(RAIZ / "teste_robustez_completo.py")],
        capture_output=True, text=True, timeout=1800, cwd=str(RAIZ))
    texto = (saida.stdout or "") + (saida.stderr or "")
    (destino / "5 - testes de falha.txt").write_text(texto, encoding="utf-8")

    # A tabela sai com uma linha por caso e TRES COLUNAS no fim: sim/nao, ok ou
    # falhou, sim/nao. So essas tres contam. O nome do caso nao pode ser lido
    # como resultado - havia um caso chamado "Arquivo que nao e PDF", e o "nao"
    # do nome fazia a bateria inteira aparecer como reprovada.
    casos, falhas = [], []
    for linha in texto.splitlines():
        colunas = linha.split()
        if len(colunas) < 4 or colunas[-2] not in ("ok", "falhou"):
            continue
        casos.append(linha)
        if colunas[-3:] != ["sim", "ok", "sim"]:
            falhas.append(linha)
    placar = next((linha.strip() for linha in reversed(texto.splitlines())
                   if " de " in linha and "passaram" in linha), "")
    notas = [f"- {placar or f'{len(casos) - len(falhas)} de {len(casos)} passaram'}"]
    notas += [f"- **falhou: {linha.strip()}**" for linha in falhas]
    return notas, not falhas and bool(casos)


def main() -> int:
    if not PAGINAS.is_dir() or not any(PAGINAS.glob("*.png")):
        print(f"Nao achei as paginas em {PAGINAS}.")
        print("Rode antes: .venv\\Scripts\\python.exe avaliar_selecao.py")
        return 2

    from datetime import datetime

    # Tudo numa pasta so, na raiz, porque esta bateria nao e de um filtro so -
    # e do programa inteiro, e o Samuel pediu que ficasse tudo junto.
    destino = (Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO")
               / f"{datetime.now():%Y-%m-%d %Hh%M} - CONFERENCIA COMPLETA")
    destino.mkdir(parents=True, exist_ok=True)
    print(f"Pasta: {destino}")

    print("  1 - filtros sozinhos...")
    n1 = parte_1_filtros_sozinhos(destino)
    print("  2 - selecao sozinha...")
    n2 = parte_2_selecao_sozinha(destino)
    print("  3 - os dois juntos...")
    n3 = parte_3_os_dois_juntos(destino)
    print("  4 - as ferramentas...")
    n4 = parte_4_ferramentas(destino)
    print("  5 - os casos de falha...")
    try:
        n5, tudo_certo = parte_5_bugs(destino)
    except Exception as exc:  # noqa: BLE001
        n5, tudo_certo = [f"- nao consegui rodar: {exc}"], False

    _certo, recado = conferir_sequencia(199, 20)

    L = ["# Conferencia completa", ""]
    L.append("Quatro partes, e a separacao e o ponto: quando o filtro e a")
    L.append("marcacao erram juntos, nao da para saber de quem e a culpa.")
    L.append("Sozinhos, da.")
    L.append("")
    L.append("Abra as imagens uma a uma - de preferencia com `conferir.py`, que")
    L.append("mostra uma por vez e aceita ditado pelo Win+H.")
    L.append("")
    L.append("## 1 - Os filtros sozinhos, sem marcacao nenhuma")
    L.append("")
    L.append("Aqui a culpa e do filtro e de mais ninguem.")
    L.append("")
    L += n1
    L.append("")
    L.append("## 2 - A marcacao sozinha, sem filtro nenhum")
    L.append("")
    L.append("**Vermelho e gravura, azul e letra, sem cor e papel.**")
    L.append("")
    L += n2
    L.append("")
    L.append("## 3 - O filtro lendo a marcacao")
    L.append("")
    L.append("E assim que o programa roda de verdade.")
    L.append("")
    L += n3
    L.append("")
    L.append("## 4 - As ferramentas de marcar a mao")
    L.append("")
    L += n4
    L.append("")
    L.append("## 5 - Os casos de falha")
    L.append("")
    L.append("PDF corrompido, protegido por senha, arquivo que some no meio,")
    L.append("disco cheio, livro de mil paginas, cancelar no meio. O que se cobra")
    L.append("e sempre o mesmo: o programa nao fecha e nao perde trabalho.")
    L.append("")
    L += n5
    L.append("")
    L.append("## 6 - A sequencia dos cadernos")
    L.append("")
    L.append(f"{recado}")
    L.append("")
    L.append("## 7 - O programa pronto para instalar")
    L.append("")
    L.append("Nesta mesma pasta esta o `EditorImpressao-Setup.exe`. Dois cliques,")
    L.append("avancar, e o programa aparece no Menu Iniciar e na Area de Trabalho.")
    L.append("Nao precisa instalar Python nem nada antes.")
    L.append("")
    L.append("## O que ainda esta errado, e nao escondo")
    L.append("")
    L.append("- A pagina 126 do Graduale sai marcada como desenho, sendo texto.")
    L.append("  A pagina fica laranja avisando da duvida, e da para consertar na")
    L.append("  aba Marcar em dois cliques.")
    L.append("- A rubricacao vermelha vira preta no Preto e branco.")
    L.append("- O titulo impresso do Pesel e as legendas do Siebmacher nao viram")
    L.append("  letra.")
    L.append("- A limpeza do papel so entra em pagina de TEXTO. Numa prancha ou")
    L.append("  numa estampa o fundo continua como veio, de proposito: ali entre")
    L.append("  os tracos esta a obra, e branquear aquilo a arruina.")

    instalador = RAIZ / "dist" / "EditorImpressao-Setup.exe"
    if instalador.exists():
        import shutil

        shutil.copy2(instalador, destino / instalador.name)
        print(f"  instalador copiado ({instalador.stat().st_size // 1048576} MB)")

    escritos = relatorio.gravar("\n".join(L), destino / "o que foi testado",
                                titulo="Conferencia completa")
    imagens = len(list(destino.rglob("*.png")))
    print(f"Relatorio: {escritos['md']}")
    print(f"Imagens:   {imagens}")
    print(f"Casos de falha: {'todos passaram' if tudo_certo else 'HA FALHA'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
