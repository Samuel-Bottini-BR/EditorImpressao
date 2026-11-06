"""Montar cadernos para impressão (imposicao).

O usuario imprime frente e verso, separa as folhas em grupos e dobra cada
grupo ao meio. Para isso as páginas precisam sair fora de ordem, na ordem
certa da dobra.

A conta, para um caderno de N páginas, com a folha i comecando em zero:

    frente da folha i:  [ N - 2i ]  [ 1 + 2i ]
    verso  da folha i:  [ 2 + 2i ]  [ N - 1 - 2i ]

Confira com N = 8 (2 folhas):
    folha 0 frente: 8 1   verso: 2 7
    folha 1 frente: 6 3   verso: 4 5
Dobrando as duas juntas ao meio, a leitura sai 1,2,3,4,5,6,7,8. E o que
queremos.

O ULTIMO CADERNO (decisao do Samuel imp-4, 21/10/2026: "Ultimo caderno menor,
so com as folhas necessarias"): ate aqui o ultimo caderno saia sempre do
tamanho cheio, como no embaralhador antigo - 23 paginas em cadernos de 20
davam 17 paginas em branco (3 folhas inteiras vazias). Agora o ultimo caderno
tem so as folhas que precisa (o multiplo de 4 logo acima do que sobrou): 23
paginas = um caderno de 20 e um de 4, com 1 pagina em branco. Vale para o
"Montar cadernos" de sempre e para o arquivo de impressao novo
(core/impressao.py). Arriscado: voltar a completar o ultimo caderno (o
defeito volta; tests/test_cadernos.py::test_ultimo_caderno_sai_menor_*).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz
import numpy as np

# Multiplo obrigatorio: cada folha carrega 4 paginas (2 frente + 2 verso).
MULTIPLO = 4
PAGINAS_POR_CADERNO_PADRAO = 20


@dataclass(frozen=True)
class Lado:
    """Um lado de uma folha fisica: duas páginas do livro, lado a lado.

    Os números são indices de página comecando em zero, já no livro inteiro.
    None quer dizer página em branco (sobra do fechamento do caderno).
    """

    esquerda: int | None
    direita: int | None
    frente: bool


def paginas_por_caderno_valido(valor: int) -> int:
    """Arredonda para o múltiplo de 4 mais próximo, no mínimo 4."""
    if valor < MULTIPLO:
        return MULTIPLO
    # Arredondamento comercial: o round() do Python leva 4,5 para 4, e um
    # empate aqui deve subir (caderno um pouco maior e melhor que menor).
    return int((valor + MULTIPLO // 2) // MULTIPLO) * MULTIPLO


def ordem_do_caderno(paginas_no_caderno: int, deslocamento: int = 0) -> list[Lado]:
    """Devolve os lados de um caderno, na ordem em que devem ser impressos.

    deslocamento e o número da primeira página deste caderno no livro.
    """
    n = paginas_por_caderno_valido(paginas_no_caderno)
    lados: list[Lado] = []

    for i in range(n // 4):
        # As formulas sao 1-based (a folha 1 traz a pagina 1); por isso o -1
        # ao converter para indice de lista.
        lados.append(
            Lado(
                esquerda=deslocamento + (n - 2 * i) - 1,
                direita=deslocamento + (1 + 2 * i) - 1,
                frente=True,
            )
        )
        lados.append(
            Lado(
                esquerda=deslocamento + (2 + 2 * i) - 1,
                direita=deslocamento + (n - 1 - 2 * i) - 1,
                frente=False,
            )
        )
    return lados


def tamanhos_dos_cadernos(total_paginas: int, paginas_por_caderno: int) -> list[int]:
    """Quantas páginas (com as brancas) tem cada caderno, na ordem. Todos do
    tamanho escolhido, menos o último, que tem só o múltiplo de 4 logo acima
    do que sobrou (imp-4, 21/10/2026). Sem páginas: lista vazia."""
    n = paginas_por_caderno_valido(paginas_por_caderno)
    tamanhos: list[int] = []
    for inicio in range(0, max(0, total_paginas), n):
        resto = total_paginas - inicio
        tamanhos.append(n if resto >= n else MULTIPLO * -(-resto // MULTIPLO))
    return tamanhos


def montar_ordem(total_paginas: int, paginas_por_caderno: int) -> list[Lado]:
    """Ordem de impressão do livro inteiro, caderno por caderno.

    As páginas que passarem do total viram branco: são o arredondamento do
    último caderno, que tem só as folhas necessárias (tamanhos_dos_cadernos).
    """
    lados: list[Lado] = []

    inicio = 0
    for tamanho in tamanhos_dos_cadernos(total_paginas, paginas_por_caderno):
        for lado in ordem_do_caderno(tamanho, deslocamento=inicio):
            lados.append(
                Lado(
                    esquerda=lado.esquerda if _existe(lado.esquerda, total_paginas) else None,
                    direita=lado.direita if _existe(lado.direita, total_paginas) else None,
                    frente=lado.frente,
                )
            )
        inicio += tamanho
    return lados


def _existe(indice: int | None, total: int) -> bool:
    """Indice valido (nao None e dentro do livro)? Usado para virar branco."""
    return indice is not None and 0 <= indice < total


def contar_cadernos(total_paginas: int, paginas_por_caderno: int) -> int:
    """Quantos cadernos o livro inteiro precisa, arredondando para cima."""
    n = paginas_por_caderno_valido(paginas_por_caderno)
    return max(1, -(-total_paginas // n))  # divisao para cima


def folhas_por_caderno(paginas_por_caderno: int) -> int:
    """Quantas folhas de papel fisico formam um caderno (4 paginas por folha)."""
    return paginas_por_caderno_valido(paginas_por_caderno) // 4


def impor_pdf(
    caminho_entrada: str | Path,
    caminho_saida: str | Path,
    paginas_por_caderno: int = PAGINAS_POR_CADERNO_PADRAO,
    progresso=None,
) -> int:
    """Le um PDF em ordem normal e grava outro já imposto em cadernos.

    Cada folha de saida e uma página em paisagem com duas páginas do livro lado
    a lado - o usuario só manda imprimir frente e verso, sem configurar nada.

    A copia e feita com show_pdf_page, que preserva texto vetorial e não
    rasteriza nada. E tambem o caminho rapido do modo "só cadernos".

    Memoria (conserto de 04/11/2026, D-591): a saida e um
    core.pdf_io.PDFQueVaiParaODisco - as folhas montadas vao para o disco de
    tempos em tempos (pela conta do peso medio das paginas da entrada), e a
    memoria nao cresce com o tamanho do livro. Antes, cada folha copiava as
    imagens das suas paginas para a memoria e o livro inteiro ficava la ate o
    save do fim. O arquivo final e o mesmo (mesmo save, mesmas opcoes).
    Arriscado: guardar `saida.doc` ou uma pagina de uma folha para a outra
    (o documento da vez muda ao ir para o disco).
    """
    from core.pdf_io import PDFQueVaiParaODisco, _peso_medio_da_pagina

    entrada = fitz.open(caminho_entrada)
    saida = PDFQueVaiParaODisco(caminho_saida)

    try:
        total = entrada.page_count
        if total == 0:
            raise ValueError("PDF de entrada sem páginas")

        # Todas as folhas saem do mesmo tamanho, senao a impressora embaralha
        # as margens. Usamos a maior pagina como molde.
        largura = max(entrada[i].rect.width for i in range(total))
        altura = max(entrada[i].rect.height for i in range(total))

        lados = montar_ordem(total, paginas_por_caderno)
        peso = _peso_medio_da_pagina(entrada)

        Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
        for numero, lado in enumerate(lados):
            folha = saida.new_page(width=largura * 2, height=altura)
            _colocar(folha, entrada, lado.esquerda, fitz.Rect(0, 0, largura, altura))
            _colocar(folha, entrada, lado.direita, fitz.Rect(largura, 0, largura * 2, altura))
            del folha
            saida.acrescentou(peso * sum(1 for i in (lado.esquerda, lado.direita)
                                         if _existe(i, total)))
            if progresso is not None:
                progresso(numero + 1, len(lados))

        folhas = saida.page_count
        saida.gravar(garbage=3, deflate=True)
        return folhas
    finally:
        saida.descartar()
        entrada.close()


def _colocar(folha: fitz.Page, origem: fitz.Document, indice: int | None, area: fitz.Rect) -> None:
    """Encaixa uma página da origem na área dada. indice None deixa em branco."""
    if indice is None or not 0 <= indice < origem.page_count:
        return
    folha.show_pdf_page(area, origem, indice)


def conferir_sequencia(total_paginas: int, paginas_por_caderno: int) -> tuple[bool, str]:
    """Confere, sem ninguem olhar folha por folha, se a ordem sai certa.

    E a pergunta do Kaique: "pode dar problema na sequencia dos cadernos? como
    ter certeza que estao todas na sequencia correta sem ter que olhar folha por
    folha?". Ate aqui a resposta era so a instrucao de como dobrar - o programa
    dizia o que fazer, mas nao conferia nada.

    A conferencia simula a dobra. Empilhadas as folhas de um caderno e dobradas
    ao meio, a leitura tem de sair 1, 2, 3... ate o fim: a pagina 1 e a direita
    da frente da folha de fora, a 2 e a esquerda do verso dela, e assim por
    diante ate o miolo, voltando pelo outro lado. Se a conta da imposicao
    estiver errada em qualquer folha, a leitura sai fora de ordem e isto pega.

    Confere tambem que nenhuma pagina do livro sumiu ou saiu repetida.

    Devolve (esta certo, frase em portugues para a tela).
    """
    if total_paginas <= 0:
        return True, "Não há páginas para conferir."

    vistas: list[int] = []
    inicio = 0
    for n in tamanhos_dos_cadernos(total_paginas, paginas_por_caderno):
        lados = ordem_do_caderno(n, deslocamento=inicio)

        # Os lados saem aos pares, na ordem em que o papel entra na impressora:
        # frente da folha, verso da mesma folha, frente da proxima. Conferir
        # nessa ordem - e nao separando frentes de versos - e o que pega uma
        # folha impressa fora de lugar, que e o erro que embaralha a dobra.
        if len(lados) % 2 or any(
            not lados[i].frente or lados[i + 1].frente
            for i in range(0, len(lados), 2)
        ):
            return False, (
                "As folhas não saíram em pares de frente e verso. Não imprima "
                "assim: avise quem cuida do programa."
            )
        folhas = [(lados[i], lados[i + 1]) for i in range(0, len(lados), 2)]

        leitura: list[int | None] = []
        for frente, verso in folhas:                 # do lado de fora para o miolo
            leitura.append(frente.direita)
            leitura.append(verso.esquerda)
        for frente, verso in reversed(folhas):       # e de volta, pelo outro lado
            leitura.append(verso.direita)
            leitura.append(frente.esquerda)

        esperado = list(range(inicio, inicio + n))
        if leitura != esperado:
            return False, (
                "A ordem das páginas não fechou na conferência. Não imprima "
                "assim: avise quem cuida do programa."
            )
        vistas.extend(p for p in leitura if _existe(p, total_paginas))
        inicio += n

    if sorted(vistas) != list(range(total_paginas)):
        return False, (
            "Alguma página ficou de fora ou saiu repetida. Não imprima assim: "
            "avise quem cuida do programa."
        )

    quantas = ("1 página" if total_paginas == 1
               else f"as {total_paginas} páginas")
    brancos = sum(tamanhos_dos_cadernos(total_paginas, paginas_por_caderno)) - total_paginas
    if brancos:
        sobra = ("sobra 1 página em branco" if brancos == 1
                 else f"sobram {brancos} páginas em branco")
        return True, (
            f"Conferido: {quantas} saem na ordem certa depois de dobrar, e "
            f"{sobra} no fim do último caderno."
        )
    return True, (
        f"Conferido: {quantas} saem na ordem certa depois de dobrar, sem "
        f"nenhuma repetida nem faltando."
    )


def instrucoes_de_impressao(total_paginas: int, paginas_por_caderno: int) -> list[str]:
    """Texto em portugues para a tela final. Sem jargao."""
    n = paginas_por_caderno_valido(paginas_por_caderno)
    folhas = folhas_por_caderno(n)
    tamanhos = tamanhos_dos_cadernos(total_paginas, n)
    cadernos = max(1, len(tamanhos))
    grupos = f"Separe as folhas em grupos de {folhas}."
    if len(tamanhos) == 1:
        # um caderno só: "grupos de 5; o último grupo tem 1 folha" não faz
        # sentido (D-333, print de 22/10/2026)
        unico = tamanhos[0] // 4
        grupos = ("A folha forma um grupo só." if unico == 1
                  else f"As {unico} folhas formam um grupo só.")
    elif tamanhos and tamanhos[-1] < n:
        # imp-4 (21/10/2026): o ultimo caderno tem so as folhas necessarias
        ultimo = tamanhos[-1] // 4
        grupos = (f"Separe as folhas em grupos de {folhas}; o último grupo tem "
                  + ("1 folha." if ultimo == 1 else f"{ultimo} folhas."))
    return [
        "Imprima frente e verso, virando na borda curta.",
        grupos,
        # singular no 1 (D-333, 22/10/2026: a janela dizia "são 1 cadernos")
        ("Dobre o grupo ao meio - é 1 caderno pronto." if cadernos == 1
         else f"Dobre cada grupo ao meio - são {cadernos} cadernos prontos."),
    ]


# ---------------------------------------------------------------------------
# A folha desenhada na tela (D-574, 02/11/2026: a etapa 7 "Montar cadernos" do
# Automatico mostra as folhas do caderno, frente e verso). A MESMA conta de
# impor_pdf (montar_ordem) e o MESMO encaixe (show_pdf_page: cada pagina na sua
# metade, sem mudar a proporcao, no meio), feitos sobre as imagens das paginas.
# Quem desenha as paginas e core/automatico.folha_do_caderno. Arriscado: mudar
# o encaixe aqui sem mudar impor_pdf (a tela deixaria de ser o arquivo, D-473;
# tests/test_decisoes_caderno_tela_grande.py compara com o PDF gravado).
# ---------------------------------------------------------------------------

VAO_ENTRE_AS_METADES = 12   # o mesmo de ui/automatico (o "depois" de uma folha que vai ser dividida)


def paginas_lado_a_lado(imagens: list):
    """As paginas que uma folha vira (uma; ou duas, quando a folha inteira vai ser dividida),
    uma ao lado da outra com um vao branco - a mesma conta de ui/automatico._lado_a_lado.
    Nenhuma: None."""
    imagens = [img for img in imagens if img is not None]
    if not imagens:
        return None
    if len(imagens) == 1:
        return imagens[0]
    altura = max(img.shape[0] for img in imagens)
    pedacos = []
    for n, img in enumerate(imagens):
        img = _em_cor(img)
        if img.shape[0] < altura:
            img = np.concatenate([img, np.full((altura - img.shape[0],) + img.shape[1:], 255, img.dtype)])
        if n:
            pedacos.append(np.full((altura, VAO_ENTRE_AS_METADES, 3), 255, img.dtype))
        pedacos.append(img)
    return np.concatenate(pedacos, axis=1)


def ordem_das_folhas(total_paginas: int, paginas_por_caderno: int) -> list[tuple]:
    """As folhas de papel do livro, na ordem em que saem: (frente, verso), cada um um
    Lado com as posições (0, 1, ...) das páginas no PDF (None = branco). É a
    MESMA conta de core/cadernos.impor_pdf (montar_ordem, com o último caderno menor)."""
    lados = montar_ordem(max(0, int(total_paginas)), paginas_por_caderno)
    return [(lados[i], lados[i + 1]) for i in range(0, len(lados) - 1, 2)]


def _em_cor(img: np.ndarray) -> np.ndarray:
    if img.ndim == 2:
        return np.repeat(img[:, :, None], 3, axis=2)
    return img[:, :, :3]


def montar_o_lado(esquerda, direita, largura: int, altura: int) -> np.ndarray:
    """Um lado da folha (BGR, branco onde não há página): duas metades de `largura` x
    `altura` pontos; cada página encaixada na sua metade sem mudar a proporção, no meio dela -
    o que show_pdf_page faz em core/cadernos.impor_pdf. None = metade em branco."""
    import cv2

    folha = np.full((altura, largura * 2, 3), 255, np.uint8)
    for n, img in enumerate((esquerda, direita)):
        if img is None:
            continue
        img = _em_cor(img)
        alt, larg = img.shape[:2]
        escala = min(largura / max(1, larg), altura / max(1, alt))
        nova_l, nova_a = max(1, round(larg * escala)), max(1, round(alt * escala))
        if (nova_l, nova_a) != (larg, alt):
            jeito = cv2.INTER_AREA if escala < 1 else cv2.INTER_LINEAR
            img = cv2.resize(img, (nova_l, nova_a), interpolation=jeito)
        x = n * largura + (largura - nova_l) // 2
        y = (altura - nova_a) // 2
        folha[y:y + nova_a, x:x + nova_l] = img
    return folha


def montar_a_folha(frente, verso, imagens: dict) -> tuple[np.ndarray, np.ndarray]:
    """(frente, verso) da folha, com `imagens` = posição no PDF -> imagem da página. As duas
    faces com o mesmo tamanho de metade: o da maior página da folha. RESSALVA: impor_pdf usa a maior página do LIVRO
    inteiro; livro com páginas do mesmo tamanho sai igual."""
    usadas = [imagens[p] for p in imagens if imagens[p] is not None]
    largura = max((img.shape[1] for img in usadas), default=10)
    altura = max((img.shape[0] for img in usadas), default=14)

    def lado(l):
        return montar_o_lado(imagens.get(l.esquerda), imagens.get(l.direita), largura, altura)

    return lado(frente), lado(verso)
