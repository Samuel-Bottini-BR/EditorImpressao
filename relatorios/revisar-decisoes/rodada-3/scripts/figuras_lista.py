"""As imagens da rodada 3 (ver figuras.py). As das 30 paginas sao acrescentadas
em paginas_lista.py; aqui ficam as de apoio."""

from comum import TRABALHO

M = str(TRABALHO / "marcar")

FIGURAS = [
    dict(tipo="lado", arquivo="graduale588-proposta", quadros=[
        ("graduale_p588__inteira", "original", (0.0, 0.26, 0.42, 0.56), [], "Original"),
        ("graduale_p588__inteira", M + r"\graduale588-S-gravura__a__marcado.jpg",
         (0.0, 0.26, 0.42, 0.56), [], "Hoje: marcada como 'gravura ou foto'"),
        ("graduale_p588__inteira", M + r"\graduale588-S-cor-papel-branco.jpg",
         (0.0, 0.26, 0.42, 0.56), [], "Proposta (simulação): cor + papel branco"),
    ], legendas=[
        "No meio, o que dá hoje: o retângulo inteiro fica como no original (papel amarelado, pautas vermelhas).",
        "À direita, uma SIMULAÇÃO da zona 'Tinta com a cor original, papel branco' (decidida em 05/10, ainda não feita):",
        "a letra fica azul e vermelha e o papel em volta vai a branco. Ressalva: as notas dentro do retângulo ficam marrons.",
    ]),
]

try:
    from paginas_lista import FIGURAS_PAGINAS
    FIGURAS += FIGURAS_PAGINAS
except ImportError:
    pass
