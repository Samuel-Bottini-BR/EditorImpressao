"""Monta `relatorios/para-conferir.html`: os nove prints e a comparação 2b.

    .venv\\Scripts\\python.exe montar_para_conferir.py

Cada quadro traz o print, o que ele prova, e - nas duas telas que têm desenho
aprovado - o desenho ao lado, para comparar região por região.

As legendas foram escritas DEPOIS de abrir cada imagem. Onde a imagem entrega
menos do que o desenho pede, quem cede é a legenda, e a diferença fica dita.
"""

from __future__ import annotations

import base64
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PRINTS = RAIZ / "relatorios" / "prints"
DESENHOS = Path(r"C:\Users\fotog\Desktop\pasta do prompt")
SAIDA = RAIZ / "relatorios" / "para-conferir.html"


def _embutir(caminho: Path) -> str:
    """A imagem vai DENTRO do html: o arquivo tem de abrir sozinho."""
    if not caminho.is_file():
        return ""
    dados = base64.b64encode(caminho.read_bytes()).decode()
    return f"data:image/png;base64,{dados}"


QUADROS = [
    {
        "n": "1",
        "titulo": "A tela de trabalho, com um livro aberto",
        "imagens": ["1 - tela de trabalho.png"],
        "desenho": "layout-tela-de-trabalho.png",
        "prova": """A página ocupa <b>489 px de 768</b> — 64% da janela, contra
        os 18% de antes. O critério pedia pelo menos 60%.""",
        "regioes": [
            ("barra de menu, 32 px", "confere",
             "Arquivo · Editar · Marcar · Filtro · Página · Ver · Ajuda, na ordem."),
            ("barra de opções, 38 px", "confere",
             "mostra a ferramenta na mão, e somar/tirar à direita."),
            ("trilha, 42 px", "confere",
             "as nove, com a letra embaixo e o traço separando as de navegar."),
            ("painéis, 172 px", "confere",
             "Para revisar · Marcar como · Filtro da página · Histórico, nessa ordem."),
            ("tira de páginas, 58 px", "confere",
             "e o Confirmar e processar no canto direito da faixa."),
            ("área da página", "difere",
             """o desenho dá 612 px; aqui são 489. Os 123 px que faltam são a
             barra de abas (42), a faixa de alerta (41 — o desenho quer 28 numa
             faixa de estado) e as margens. As abas só somem quando Onde
             cortar, Bordas e Endireitar virarem modo da própria página, e isso
             mexe no arrasto das alças de corte — que é queixa do Kaique já
             resolvida. Fica anotado como melhoria, e não foi arriscado por 3%
             de altura."""),
            ("faixa de estado", "falta",
             """o desenho põe página, livro, zoom e "ajustar à tela" numa faixa
             de 28 px sob a página. Hoje a faixa de alerta ocupa esse lugar com
             41 px."""),
        ],
    },
    {
        "n": "2",
        "titulo": "A barra de opções muda conforme a ferramenta",
        "imagens": ["2.1 - barra de opcoes - cor.png",
                    "2.2 - barra de opcoes - pincel.png",
                    "2.3 - barra de opcoes - zoom.png"],
        "prova": """Três ferramentas, três faixas diferentes. <b>Pegar tudo
        desta cor</b> traz a variação e o aviso da roda do mouse; o <b>Pincel</b>
        traz o tamanho; o <b>Zoom</b> traz a porcentagem e "ajustar à tela".
        Somar e tirar aparecem nas duas primeiras e somem no Zoom — não há o
        que somar ao aproximar a página.""",
    },
    {
        "n": "3",
        "titulo": "O painel Histórico, e uma ação sendo desfeita",
        "imagens": ["3.1 - painel Historico - com acoes.png",
                    "3.2 - painel Historico - uma acao desfeita.png"],
        "prova": """À esquerda, três ações da sessão, a mais recente embaixo e
        destacada. À direita, depois de desfazer: a última saiu da lista.
        Clicar numa ação volta o trabalho até ali. Usa o mesmo arquivo de
        desfazer que já existia — não há um segundo histórico ao lado.""",
    },
    {
        "n": "4",
        "titulo": "O painel Para revisar, agrupado por tipo",
        "imagens": ["4 - painel Para revisar - agrupado por tipo.png"],
        "prova": """Agrupado <b>por tipo de alerta</b>, com a contagem de cada
        um — e não uma lista de "página 3, página 17, página 40", que não diz o
        que há de errado. Clicar leva à primeira daquele tipo. Este painel a
        especificação original pedia, e nunca tinha sido feito.""",
    },
    {
        "n": "5",
        "titulo": "A tela inicial, com cartões",
        "imagens": ["5 - tela inicial - cartoes.png"],
        "desenho": "layout-tela-inicial.png",
        "prova": """Miniatura da primeira página, nome, páginas e data em
        linguagem comum, barra de progresso e a frase de onde o trabalho parou.""",
        "regioes": [
            ("barra de menu", "falta",
             """o desenho põe Arquivo · Ver · Ajuda também aqui. A barra existe
             e fica com esses três de pé, mas ela pertence à janela — e este
             print é só da tela, sem a janela em volta."""),
            ("faixa de arrastar, 62 px", "confere",
             "uma linha, ícone à esquerda e as duas frases ao lado."),
            ('"Continuar de onde parou" + busca', "confere",
             "título à esquerda, campo de procurar à direita."),
            ("quatro cartões de 304×220", "confere",
             "quatro por linha, com a área de capa de 112 px."),
            ("cartão laranja", "confere",
             'o do PDF fora do lugar, com "procurar de novo".'),
        ],
    },
    {
        "n": "6",
        "titulo": "Um cartão de PDF que saiu do lugar",
        "imagens": ["6 - cartao de PDF que saiu do lugar.png"],
        "prova": """Cartão inteiro em laranja, dizendo <b>o que houve</b> e
        oferecendo "procurar de novo". Nunca um botão apagado sem explicação —
        era a queixa do print antigo. Se o arquivo apontado não for o mesmo
        livro, o programa recusa: aplicar ajustes de um livro em outro
        estragaria o trabalho sem aparecer.""",
    },
    {
        "n": "7",
        "titulo": "Fechar no meio do trabalho, e reabrir",
        "imagens": ["7.1 - antes de fechar.png", "7.2 - depois de reabrir.png"],
        "prova": """À esquerda, antes de fechar: página 24, filtro Mágico pro,
        marcada como conferida. À direita, depois de fechar o programa e abrir o
        mesmo livro de novo: <b>voltou na página 24, com o mesmo filtro, no
        mesmo projeto</b>. Nenhum diálogo "quer salvar?" em ponto nenhum.""",
    },
    {
        "n": "8",
        "titulo": "A janela de confirmação",
        "imagens": ["8 - janela de confirmacao.png"],
        "prova": """Pasta, nome do arquivo e o aviso de páginas não conferidas —
        que a especificação pedia e nunca tinha sido verificado. Quando o
        arquivo já existe, aparece um segundo aviso de que ele será substituído.
        "Salvar em" e "Nome do arquivo" saíram da tela de trabalho e vivem aqui
        e no menu Arquivo: eles importam num momento só, o de gravar.""",
    },
    {
        "n": "9",
        "titulo": "A mesma tela em 150%",
        "imagens": ["1 - tela de trabalho - 150%.png"],
        "prova": """Em escala de 150% a janela cabe em 680 px de altura, e a
        página fica com <b>401 px — 59%</b>. Tudo continua legível: as nove
        ferramentas na trilha, os quatro painéis, a tira e o botão de processar.
        A trilha se aperta sozinha até caber, e rola com a roda se não couber.
        <br><br>Dito com franqueza: 59% fica um ponto abaixo do critério de 60%,
        que foi medido em 100%. Em 150% a janela inteira tem menos altura, e as
        faixas de cima e de baixo não encolhem junto.""",
    },
]


def montar() -> Path:
    partes = ["""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Editor de Impressão - para conferir</title>
<style>
 body { font-family: "Segoe UI", system-ui, sans-serif; max-width: 1180px;
        margin: 0 auto; padding: 30px 24px 60px; color: #1c1c1e;
        background: #fdfdfc; line-height: 1.55; }
 h1 { font-weight: 600; margin-bottom: 4px; }
 .sub { color: #86827c; margin-top: 0; }
 .quadro { border: 1px solid #e6e4e0; border-radius: 10px; padding: 20px 22px;
           margin: 26px 0; background: #fff; }
 .quadro h2 { font-size: 19px; font-weight: 600; margin: 0 0 10px; }
 .n { color: #86827c; font-weight: 400; margin-right: 8px; }
 img { max-width: 100%; border: 1px solid #e6e4e0; border-radius: 6px;
       display: block; margin: 10px 0; }
 .lado { display: flex; gap: 14px; flex-wrap: wrap; }
 .lado > figure { flex: 1 1 340px; margin: 0; }
 figcaption { color: #86827c; font-size: 13px; margin-top: 4px; }
 table { border-collapse: collapse; width: 100%; margin-top: 14px;
         font-size: 14px; }
 th, td { text-align: left; padding: 7px 9px; border-bottom: 1px solid #eeece7;
          vertical-align: top; }
 th { color: #86827c; font-weight: 500; }
 .confere { color: #0f6e56; font-weight: 600; }
 .difere  { color: #8a5a10; font-weight: 600; }
 .falta   { color: #a33; font-weight: 600; }
 .aviso { background: #faeeda; border: 1px solid #ef9f27; border-radius: 8px;
          padding: 12px 14px; margin: 18px 0; }
</style></head><body>
<h1>Editor de Impressão — para conferir</h1>
<p class="sub">Os nove prints da seção 6, e a comparação com os desenhos
aprovados (critério 2b). Todo print é da tela de verdade, com um livro do
acervo aberto — nenhum é montagem.</p>

<div class="aviso"><b>Antes de ler:</b> abri cada imagem e conferi a legenda
contra o que ela mostra. Onde a tela entrega menos do que o desenho pede, quem
cede é a legenda — a diferença fica dita, e não escondida. As três diferenças
estão nos quadros 1, 5 e 9.</div>
"""]

    for quadro in QUADROS:
        partes.append('<div class="quadro">')
        partes.append(f'<h2><span class="n">{quadro["n"]}</span>'
                      f'{quadro["titulo"]}</h2>')
        partes.append(f'<p>{quadro["prova"]}</p>')

        if len(quadro["imagens"]) > 1:
            partes.append('<div class="lado">')
            for nome in quadro["imagens"]:
                fonte = _embutir(PRINTS / nome)
                partes.append(f'<figure><img src="{fonte}" alt="{nome}">'
                              f'<figcaption>{nome}</figcaption></figure>')
            partes.append("</div>")
        else:
            fonte = _embutir(PRINTS / quadro["imagens"][0])
            partes.append(f'<img src="{fonte}" alt="{quadro["titulo"]}">')

        if quadro.get("desenho"):
            desenho = _embutir(DESENHOS / quadro["desenho"])
            if desenho:
                partes.append("<h3 style='font-size:15px;margin:18px 0 6px'>"
                              "O desenho aprovado, para comparar</h3>")
                partes.append(f'<img src="{desenho}" alt="desenho">')

        if quadro.get("regioes"):
            partes.append("<table><tr><th>região</th><th></th>"
                          "<th>o que a tela mostra</th></tr>")
            for regiao, estado, nota in quadro["regioes"]:
                partes.append(f'<tr><td>{regiao}</td>'
                              f'<td class="{estado}">{estado}</td>'
                              f'<td>{nota}</td></tr>')
            partes.append("</table>")
        partes.append("</div>")

    partes.append("""
<div class="quadro">
<h2><span class="n">·</span>O que ficou de fora, e por quê</h2>
<table>
<tr><th>o que</th><th>por quê</th></tr>
<tr><td>As abas viram modo da página, e a faixa de estado de 28 px</td>
    <td>São os 123 px que faltam para os 612 do desenho. Mexer nisso mexe no
    arrasto das alças de corte, e o corte de bordas é queixa do Kaique já
    resolvida — não vale arriscar por 3% de altura. Fica como melhoria.</td></tr>
<tr><td>Ícones de um conjunto de verdade</td>
    <td>Os da trilha são desenhados à mão, como o desenho previa para o
    protótipo. Trocar por um conjunto pronto é troca de biblioteca, e isso
    precisa ser perguntado antes.</td></tr>
</table>
</div>

<p class="sub">Gerado por <code>gerar_prints.py</code> e
<code>montar_para_conferir.py</code>. Para refazer, rode os dois.</p>
</body></html>""")

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text("".join(partes), encoding="utf-8")
    return SAIDA


if __name__ == "__main__":
    caminho = montar()
    print(f"Gravado: {caminho}  ({caminho.stat().st_size // 1024} KB)")
