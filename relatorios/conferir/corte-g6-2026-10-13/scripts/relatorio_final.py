"""Monta o relatorio da conferencia (corte-g6.md, .html e .pdf) a partir do
dados.json, da classificacao.json, do projeto-antigo.json e do que o
verificador viu nas imagens (o dicionario OLHO, escrito a mao depois de abrir
todas). Usa relatorio.gravar, que grava os tres formatos.

USO   python relatorio_final.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent
RAIZ = PASTA.parents[2]
sys.path.insert(0, str(RAIZ))

import relatorio  # noqa: E402

# O que o verificador viu, pagina por pagina (so as que giram no livro novo).
# classe pelo OLHO: piorou / leve / conhecido / empate / falso / mudou / melhorou / igual
OLHO = {
    "matematica_p032__inteira": ("piorou", "Faixa preta larga do scanner à direita, que a ordem antiga cortava. A folha fica 4,4 cm mais larga só de preto. (O preto de baixo sobra nas duas ordens.)"),
    "cursus_p003__inteira": ("piorou", "Faixa preta de 1,6 cm à direita e de 0,6 cm embaixo, que a ordem antiga cortava. A linha preta da esquerda fica nas duas."),
    "antiphon_p260__inteira": ("piorou", "A faixa preta de baixo passa de 2,1 cm para 4,9 cm."),
    "antiphon_p088__inteira": ("piorou", "A faixa preta da direita passa de 0,9 cm para 2,8 cm. (Há preto em volta nas duas ordens.)"),
    "escola_p197__inteira": ("piorou", "O corte come os números 1, 2 e 3 dos itens, na margem esquerda. Na ordem antiga eles saíam inteiros."),
    "camoes_p104__inteira": ("leve", "Aparece um fio escuro de 2 mm à esquerda e de menos de 1 mm à direita, que a ordem antiga não deixava."),
    "escola_p007__inteira": ("conhecido", "O título fica a 1 mm da borda de cima (na ordem antiga sobravam 18 mm de papel, com um risco do scanner no alto). Nada impresso se perde. Já está anotado no plano (12/10) como \"título colado na borda de cima\"."),
    "camoes_p006__inteira": ("empate", "Quase igual. Aparece um fio escuro de 1,3 mm em cima; o da esquerda já existia."),
    "camoes_p066__inteira": ("empate", "Troca: somem as cunhas brancas dos cantos e o fio escuro de baixo; aparece um fio escuro de 1,4 mm à esquerda."),
    "horas_p011__inteira": ("falso", "Ao olho as duas são iguais (na nova somem as cunhas brancas). A conta contou como \"faixa\" a pintura da moldura, que chega perto da beirada."),
    "rariora_p155__inteira": ("mudou", "A folha fica 3,5 cm mais curta: o papel em branco de baixo foi cortado e a moldura da gravura fica a 1 mm da borda. Nada impresso se perde. Para o Samuel olhar."),
    "rhetorica_p073__inteira": ("melhorou", "O fio da moldura, à esquerda e embaixo, sai inteiro (na antiga saía cortado)."),
    "graduale_p221__inteira": ("melhorou", "O número da folha (\"Cvij\") sai inteiro; na antiga o giro cortava o fim dele. Somem as cunhas brancas de cima e de baixo."),
    "graduale_p223__inteira": ("melhorou", "O número da folha (\"Cviij\") sai inteiro; na antiga saía cortado."),
    "graduale_p588__inteira": ("melhorou", "Mais margem em volta; os enfeites de pena da inicial saem inteiros. Fica uma cunha branca fina à direita."),
    "boecio_p022__inteira": ("melhorou", "O título deixa de ficar colado na borda de cima."),
    "horas_p013__inteira": ("melhorou", "Somem as cunhas brancas; mais papel embaixo."),
    "siebmacher_p009__direita": ("melhorou", "Um pouco menos de preto em cima. Fica uma cunha branca fina à direita."),
    "egenloff_p003__inteira": ("melhorou", "Um pouco menos de preto e de cunha branca à esquerda. Quase igual."),
    "antiphonal1547_p252__inteira": ("igual", "Mais margem em cima; cunha branca fina em cima e à direita."),
    "boecio_p008__inteira": ("igual", "Somem as cunhas brancas da esquerda; aparece uma fina à direita."),
    "escola_p035__inteira": ("igual", "Igual."),
    "rariora_p365__inteira": ("igual", "Igual (o \"mi-Flosculoso\" da margem esquerda sai encostado na borda nas duas)."),
}
NOME_DA_CLASSE = {"piorou": "PIOROU", "leve": "piorou pouco", "conhecido": "piorou (já conhecido)",
                  "empate": "quase igual", "falso": "igual (a conta errou)", "mudou": "mudou muito",
                  "melhorou": "melhorou", "igual": "igual"}


def nome(base: str) -> str:
    livro, resto = base.split("_p")
    pagina, metade = resto.split("__")
    nomes = {"antiphonal1547": "Antiphonal 1547", "opusmajus": "Opus Majus", "ljs47": "LJS 47",
             "matematica": "Matemática", "boecio": "Boécio", "camoes": "Camões"}
    texto = f"{nomes.get(livro, livro.capitalize())} {int(pagina)}"
    return texto if metade == "inteira" else f"{texto} ({metade})"


def br(valor: float, casas: int = 1) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def tamanho(r: dict) -> str:
    return f"{br(r['tamanho_mm'][0], 0)} × {br(r['tamanho_mm'][1], 0)}"


def main() -> int:
    dados = json.loads((PASTA / "dados.json").read_text(encoding="utf-8"))
    classes = json.loads((PASTA / "classificacao.json").read_text(encoding="utf-8"))
    antigo = json.loads((PASTA / "projeto-antigo.json").read_text(encoding="utf-8"))
    total = len(dados)
    giram = [b for b in dados if abs(dados[b]["C"]["angulo"]) >= 0.1]
    identicas = [b for b in dados if classes[b]["so_a_ordem"]["identica"]]
    gabarito = [b for b in dados if dados[b]["no_gabarito"]]
    por_olho: dict[str, list[str]] = {}
    for b in giram:
        por_olho.setdefault(OLHO.get(b, ("igual", ""))[0], []).append(b)
    comp = antigo["comparacao"]
    iguais_antigo = sum(1 for v in comp.values() if v["identica_ponto_por_ponto"])

    def linha_da_tabela(b: str) -> str:
        d, c = dados[b], classes[b]["so_a_ordem"]
        return (f"| {nome(b)} | {NOME_DA_CLASSE[OLHO[b][0]]} | {OLHO[b][1]} | "
                f"{br(100 * d['B']['beirada_escuro'])}% → {br(100 * d['C']['beirada_escuro'])}% | "
                f"{br(100 * d['B']['tinta_perdida'], 2)}% → {br(100 * d['C']['tinta_perdida'], 2)}% | "
                f"{tamanho(d['B'])} → {tamanho(d['C'])} | {'sim' if d['no_gabarito'] else 'não'} |")

    def figura(b: str, o_que_olhar: str) -> str:
        return (f"### {nome(b)}\n\n**O que olhar:** {o_que_olhar}\n\n"
                f"![{nome(b)}: ordem antiga à esquerda, ordem nova à direita](img/lado-{b}.jpg)\n\n"
                f"*{nome(b)}: ordem antiga à esquerda, ordem nova (livro novo) à direita; embaixo, os quatro cantos ampliados.*\n")

    piores = ["matematica_p032__inteira", "cursus_p003__inteira", "antiphon_p260__inteira",
              "antiphon_p088__inteira", "escola_p197__inteira", "camoes_p104__inteira"]
    outras = ["escola_p007__inteira", "camoes_p006__inteira", "camoes_p066__inteira",
              "horas_p011__inteira", "rariora_p155__inteira"]
    melhores = ["rhetorica_p073__inteira", "graduale_p221__inteira", "graduale_p588__inteira",
                "boecio_p022__inteira", "siebmacher_p009__direita"]

    t: list[str] = []
    t.append("# O corte depois do \"endireitar antes de cortar\" (G6): onde piorou\n")
    t.append("Conferência do verificador, 13/10/2026. Investigação: **nada do programa foi mudado.** "
             "Quem decide o que fazer é o Samuel.\n")
    t.append("## Em uma frase\n")
    t.append(f"**No livro novo o corte ficou pior em 6 das {total} páginas conferidas: em 4 sobra uma faixa preta larga "
             "do scanner que antes era cortada (de 1,6 a 4,4 cm a mais), em 1 o corte come os números dos itens na "
             "margem, e em 1 sobra um fio escuro de 2 mm.** As 5 graves estão todas fora das páginas-gabarito, por isso "
             "não apareceram na aprovação de 12/10.\n")
    t.append(f"Das {total} páginas, {len(identicas)} saem idênticas nas duas ordens (o programa não gira a página, então "
             f"a ordem não muda nada). Das {len(giram)} que giram: {len(por_olho.get('piorou', []))} pioraram de verdade, "
             f"{len(por_olho.get('leve', []))} piorou pouco, {len(por_olho.get('conhecido', []))} piorou num ponto já "
             f"anotado no plano (Escola 7), {len(por_olho.get('melhorou', []))} melhoraram, "
             f"{len(por_olho.get('mudou', []))} mudou muito sem perder nada (Rariora 155) e as outras "
             f"{len(por_olho.get('igual', [])) + len(por_olho.get('empate', [])) + len(por_olho.get('falso', []))} "
             "ficaram iguais ou quase iguais.\n")
    t.append(f"**Projeto antigo: não tem o defeito.** Em {iguais_antigo} de {len(comp)} casos conferidos, o projeto gravado "
             "pelo programa de antes do G6 sai, no programa de hoje, idêntico ponto por ponto.\n")

    t.append("## As páginas em que piorou\n")
    t.append("\"Faixa escura\" é quanto da página é mancha escura encostada na beirada (a mesma conta do aviso "
             "\"Faixa escura na beirada\"). \"Tinta de fora\" é quanto do que está impresso fica fora do corte. "
             "Sempre ordem antiga → ordem nova. Tamanho em milímetros.\n")
    t.append("| Página | Veredito (olho) | O que mudou | Faixa escura | Tinta de fora | Tamanho da folha | No gabarito |")
    t.append("|---|---|---|---|---|---|---|")
    for b in piores + outras:
        t.append(linha_da_tabela(b))
    t.append("")
    t.append("Como ler: as seis primeiras linhas são as que pioraram. A Escola 7 já está anotada no plano. "
             "Camões 6 e 66 a conta acusou, mas ao olho é troca de um defeito pequeno por outro. "
             "Horas 11 a conta errou. Rariora 155 a conta deu \"igual\", mas a folha mudou muito de tamanho.\n")

    t.append("## As imagens das que pioraram\n")
    t.append("Todas sem filtro (só o corte e o giro), a 300 DPI, na mesma escala dos dois lados.\n")
    olhar = {
        "matematica_p032__inteira": "A faixa preta à direita, que só existe na ordem nova.",
        "cursus_p003__inteira": "A faixa preta à direita e a de baixo, que só existem na ordem nova. É a página do achado.",
        "antiphon_p260__inteira": "A faixa preta de baixo, bem mais alta na ordem nova.",
        "antiphon_p088__inteira": "A faixa preta da direita, mais larga na ordem nova.",
        "escola_p197__inteira": "A margem esquerda: os números 1, 2 e 3 somem na ordem nova (só fica o travessão).",
        "camoes_p104__inteira": "O fio escuro colado na borda esquerda, só na ordem nova.",
        "escola_p007__inteira": "O título no alto: colado na borda na ordem nova.",
        "camoes_p006__inteira": "O fio escuro no alto, só na ordem nova. O resto é igual.",
        "camoes_p066__inteira": "Os cantos: cunha branca na antiga, fio escuro à esquerda na nova.",
        "horas_p011__inteira": "As duas são iguais ao olho; a conta errou aqui.",
        "rariora_p155__inteira": "A parte de baixo: na ordem nova o papel em branco foi cortado.",
    }
    for b in piores:
        t.append(figura(b, olhar[b]))
        if b == "escola_p197__inteira":
            t.append("![Escola 197, margem esquerda de perto: antiga à esquerda, nova à direita](img/zoom-escola_p197-margem-esquerda.jpg)\n\n"
                     "*Escola 197, a margem esquerda de perto. À esquerda a ordem antiga (com os números); à direita a nova (sem eles).*\n")
    t.append("## As outras cinco que a conta ou o olho separaram\n")
    for b in outras:
        t.append(figura(b, olhar[b]))

    t.append("## As que mais melhoraram (para comparar)\n")
    t.append("| Página | O que melhorou | Tinta de fora | Tamanho da folha |")
    t.append("|---|---|---|---|")
    for b in [x for x in giram if OLHO.get(x, ("", ""))[0] == "melhorou"]:
        d = dados[b]
        t.append(f"| {nome(b)} | {OLHO[b][1]} | {br(100 * d['B']['tinta_perdida'], 2)}% → "
                 f"{br(100 * d['C']['tinta_perdida'], 2)}% | {tamanho(d['B'])} → {tamanho(d['C'])} |")
    t.append("")
    for b in melhores:
        t.append(figura(b, OLHO[b][1]))

    t.append("## A causa\n")
    t.append("São duas causas diferentes. Nenhuma foi consertada.\n")
    t.append("### Causa 1: o branco do giro esconde a borda preta do scanner (Cursus 3, Matemática 32, Antiphon 88 e 260, Camões 104)\n")
    t.append("Na ordem nova o programa gira a página inteira e **só depois** procura o corte nela. O giro mantém o tamanho "
             "da folha e pinta de **branco** as cunhas que sobram nos cantos e nas beiradas. Esse branco fica entre a beirada "
             "da imagem e a borda preta do scanner. A busca do corte foi feita para a borda preta **encostada** na beirada, "
             "e deixa de reconhecê-la:\n")
    t.append("- `core/pipeline.py`, função `_geometria_endireitando_antes`, linhas 759 a 761: "
             "`reta = rotacionar(em_cinza(), angulo)` e logo `recorte = detectar_bordas(reta, dpi=dpi).tupla`.\n"
             "- `core/endireitar.py`, função `rotacionar`, linhas 120 a 134: `borderMode=cv2.BORDER_CONSTANT, borderValue=borda` "
             "(branco, 255).\n"
             "- `core/recortar.py`, função `_apagar_bordas_solidas`, linhas 745 a 779: anda **a partir da coluna de fora** "
             "enquanto a coluna for 80% escura ou mais (`while x < limite_x and limpa[:, x].mean() >= FRACAO_BORDA_SOLIDA`). "
             "Com a cunha branca, a coluna de fora já não chega a 80% e o laço para na primeira: a faixa preta não é apagada "
             "e passa a contar como conteúdo.\n"
             "- `core/recortar.py`, `_faixa_com_a_tinta`, linhas 198 a 212: onde o fundo preto é liso (Antiphon), a cunha "
             "branca em cima do preto cria \"tinta\" nova bem na beirada, e a caixa do corte vai até o fim da folha.\n"
             "- Na ordem antiga havia ainda uma trava que a nova não usa: `alargar_para_o_giro` com `_parar_no_escuro` "
             "(`core/recortar.py`, linhas 602 e 685), que nunca deixava a folga do giro trazer o fundo escuro.\n")
    t.append("Os números, medidos na máscara de tinta que o próprio corte usa (`causa.json`):\n")
    t.append("| Página | Lado | Página como veio | Página já endireitada |")
    t.append("|---|---|---|---|")
    t.append("| Cursus 3 | direita | coluna de fora 100% escura; 45 colunas apagadas como borda | coluna de fora 73%; nenhuma apagada |")
    t.append("| Matemática 32 | direita | coluna de fora 100% escura; 100 colunas apagadas | coluna de fora 71%; nenhuma apagada |")
    t.append("| Camões 104 | esquerda | coluna de fora 89%; 12 colunas apagadas | coluna de fora 76%; nenhuma apagada |")
    t.append("| Antiphon 260 | embaixo | 0% de tinta nas 8 linhas de fora | cerca de 40% de tinta nas 8 linhas de fora |")
    t.append("| Antiphon 88 | direita | 0% de tinta nas 8 colunas de fora | cerca de 40% de tinta nas 8 colunas de fora |")
    t.append("")
    t.append("![Cursus 3: a máscara de tinta do corte, como veio e já endireitada](img/causa-cursus_p003__inteira.jpg)\n\n"
             "*Cursus 3, o que o corte enxerga. Preto = tinta que conta; cinza = o que ele jogou fora; vermelho = o corte. "
             "À esquerda (página como veio) a faixa da direita está cinza, jogada fora. À direita (já endireitada) ela "
             "está preta, contando como conteúdo, e o corte vai até a beirada.*\n")
    t.append("![Antiphon 260: a máscara de tinta do corte](img/causa-antiphon_p260__inteira.jpg)\n\n"
             "*Antiphon 260. Na página já endireitada aparece um risco de tinta na beirada de baixo (o encontro do preto "
             "com a cunha branca), e o corte desce até o fim.*\n")
    t.append("![Matemática 32: a máscara de tinta do corte](img/causa-matematica_p032__inteira.jpg)\n\n"
             "*Matemática 32. A faixa da direita: cinza (jogada fora) na página como veio, preta (conteúdo) na endireitada.*\n")
    t.append("Achado ao lado, na mesma imagem do Cursus 3: com a faixa preta contando como tinta, várias **linhas de texto** "
             "passam a ser apagadas da máscara como se fossem \"risca de dobra\" (as tiras cinza em cima do texto, à "
             "direita). Nesta página isso não mudou o corte, mas é um risco: `_apagar_riscas_de_dobra`, "
             "`core/recortar.py`, linhas 782 a 826. Não vi isso cortar texto em nenhuma das páginas conferidas.\n")
    t.append("**Prova de que a causa é essa (experiência, não é conserto):** medi o corte de novo girando a página com a "
             "cunha preenchida pela própria beirada, em vez de branco, só para a medida. A faixa some nas cinco páginas: "
             "Cursus 3 de 7,4% para 1,0% (antiga 0,5%); Matemática 32 de 31,5% para 18,7% (antiga 18,4%); Antiphon 260 "
             "de 7,6% para 3,5% (antiga 3,2%); Antiphon 88 de 12,6% para 8,7% (antiga 8,5%); Camões 104 de 2,7% para "
             "1,1% (antiga 0,5%). **Mas essa troca simples piora outras páginas** (Camões 66, Boécio 3 e Graduale 221 "
             "perdem mais tinta; Egenloff 3 ganha preto; Graduale 222 muda muito de largura), então não serve como está. "
             "Números em `experiencia-cunha.json`; não abri imagens dessa experiência.\n")
    t.append("### Causa 2: a página reta faz o corte jogar fora os números da margem (Escola 197)\n")
    t.append("Aqui não há borda preta. O corte descarta, de cada lado, os primeiros 0,2% da tinta da página, para a sujeira "
             "da margem não segurar o corte (`core/recortar.py`, `SOBRA_DE_TINTA = 0.002`, linha 175, usada em "
             "`_faixa_com_a_tinta`, linhas 198 a 212). Os três números (\"1\", \"2\", \"3\") somam **0,197%** da tinta da "
             "página, logo abaixo do limite. Na página torta eles se espalham por 8 colunas e o limite cai no meio deles; "
             "aí a regra de \"não partir peça\" (`_nao_partir_pecas`, linha 537) puxa o corte e eles entram. Na página reta "
             "eles ficam alinhados em 7 colunas, cabem inteiros nos 0,2% descartados, e a peça que está inteira do lado de "
             "fora não puxa o corte. A fraqueza é da regra dos 0,2%, e existe nas duas ordens; a ordem antiga escapava "
             "por um triz.\n")
    t.append("A Escola 7 (título a 1 mm do alto) é parecida: na página reta o risco do scanner do alto é apagado inteiro, "
             "e o corte encosta no título com a folga mínima de 1 mm (`FOLGA_MM`).\n")

    t.append("## Projeto antigo\n")
    t.append(f"**Não aparece.** Conferido por máquina de dois jeitos:\n")
    t.append(f"1. Rodei o programa de **antes** do G6 (commit `7485e1b`, tirado do git para uma pasta temporária) em 20 "
             "páginas, incluindo todas as que pioraram, de duas formas (endireitar pela conta do ScanTailor e pela conta "
             "do programa), e gravei cada projeto como aquele programa gravava, sem o campo `ordem_do_preparo`. Abri esses "
             f"projetos no programa de hoje: a ordem volta \"cortar_antes\" e a página sai **idêntica ponto por ponto em "
             f"{iguais_antigo} de {len(comp)}** (`projeto-antigo.json`).\n"
             "2. Nas 89 páginas, o preparo antigo (colunas A e B do `dados.json`) não tem a faixa: Cursus 3 fica em 0,5%.\n")
    t.append("Ressalva: conferi pela conta do programa (`Projeto.de_dicionario` e `renderizar_pagina`), não abrindo o "
             "projeto pela janela.\n")

    t.append("## O que sugiro (sem fazer)\n")
    t.append("1. **Não desfazer o G6 inteiro.** Ele conserta coisas de verdade (números de folha do Graduale inteiros, "
             "cunhas brancas que somem, fio de moldura inteiro). O defeito é só em página torta **com borda preta de "
             "scanner**, e num caso de número pequeno na margem.\n"
             "2. **Passar a causa 1 ao implementador como bug que impede**: livro novo com borda preta sai com faixa preta "
             "larga. O conserto é dele; a experiência acima mostra onde está o problema e que a troca mais simples não basta.\n"
             "3. **Causa 2 (números da margem):** pôr na Lista de bugs. É da regra dos 0,2%, não da ordem; pode ser o caso "
             "de esperar a caixa do conteúdo do ScanTailor (itens 2.5 e 2.13), que substitui essa busca.\n"
             "4. **Teste de máquina que falta:** página torta com borda preta, na ordem nova. Hoje "
             "`tests/test_ordem_do_preparo.py` não tem nenhum caso com borda preta.\n"
             "5. **Gabarito do corte:** as 5 páginas graves estão fora das 32. Sugiro incluir Cursus 3, Matemática 32, "
             "Antiphon 260 e Escola 197.\n"
             "6. **Enquanto não consertar:** o aviso \"Faixa escura na beirada\" do \"Para revisar\" pega esses casos "
             "(pegou o Cursus 3), e o corte à mão na aba Bordas resolve página a página.\n")

    t.append("## Como foi conferido\n")
    t.append("| O quê | Máquina ou olho | Como |")
    t.append("|---|---|---|")
    t.append(f"| Medidas das {total} páginas nas duas ordens | máquina | O programa de verdade (`renderizar_pagina`), 300 DPI, sem filtro, três preparos: A = antigo (corta antes, conta do programa), B = corta antes com o ângulo do livro novo, C = livro novo. A comparação B → C isola a ordem. |")
    t.append("| Separar em melhorou, igual, piorou | máquina, depois olho | A conta separou 10 pioras e 7 melhoras; o olho corrigiu (ver tabela). |")
    t.append(f"| Imagens lado a lado | olho | Abri as 23: as 10 que a conta acusou, as 7 que ela deu como melhora e mais 6 que as folhas de contato mostraram diferentes. |")
    t.append(f"| As {len(giram)} páginas que giram, todas | olho | 11 folhas de contato (antiga e nova lado a lado, pequenas): abri todas. |")
    t.append("| Causa | máquina + olho | Passo a passo do corte na página como veio e na endireitada (`causa.py`), em 8 páginas; abri 3 das imagens. |")
    t.append("| Projeto antigo | máquina | Programa de antes do G6 contra o de hoje, 40 casos. |")
    t.append("")

    t.append("## O que não conferi\n")
    t.append(f"- **Só {total} páginas soltas** (de 1 a 10 por livro, 19 livros). Não rodei nenhum livro inteiro, então não sei em quantas "
             "páginas de um livro com borda preta o defeito aparece. Pelo que vi, toda página torta com borda preta larga "
             "encostada na beirada está sujeita.\n"
             "- **Não abri a janela do programa.** Tudo foi por linha de comando, a 300 DPI (a resolução do PDF). A prévia "
             "da tela usa o mesmo corte guardado, mas não conferi na tela.\n"
             "- **Não rodei a suíte de testes nem o teste de velocidade:** não mudei código.\n"
             "- **Os outros filtros.** Medi sem filtro. A conta \"faixa no Preto e branco\" do `dados.json` usa o Preto e "
             "branco de fábrica direto, sem a marcação de gravura do programa.\n"
             "- **A conta de \"tinta de fora\" é minha**, feita na página reduzida a 2000 pontos (erro de uns 0,2 mm). "
             "Conta como conteúdo qualquer tinta que não encosta na beirada, inclusive risco de scanner (foi o que fez a "
             "Escola 7 parecer perder 1,7%: era o risco do alto, não texto).\n"
             "- **Rariora 155:** não investiguei por que a ordem antiga guardava o papel em branco de baixo.\n"
             "- **Diferenças que vêm da conta do ângulo, e não da ordem** (colunas A → C: Horas 16 e Egenloff 3 mudam "
             "porque o ScanTailor mede outro ângulo): fora desta tarefa, não olhei.\n"
             "- **A experiência da cunha** foi medida em cópias JPEG das páginas, só por número.\n"
             "- Das imagens de causa, abri Cursus 3, Antiphon 260 e Matemática 32; as outras cinco estão na pasta sem eu "
             "ter aberto.\n")

    t.append(f"## As {len(giram)} páginas que giram no livro novo, uma por uma\n")
    t.append(f"As outras {len(identicas)} páginas não giram e saem idênticas. \"Conta\" é o que a máquina separou; "
             "\"olho\" é o que vi.\n")
    t.append("| Página | Giro | Conta | Olho | Faixa escura | Tinta de fora | Tamanho (mm) | Gabarito |")
    t.append("|---|---|---|---|---|---|---|---|")
    for b in sorted(giram):
        d, c = dados[b], classes[b]["so_a_ordem"]
        olho = OLHO.get(b, ("igual", ""))[0]
        t.append(f"| {nome(b)} | {br(d['C']['angulo'], 2)}° | {c['classe']} | {NOME_DA_CLASSE[olho]} | "
                 f"{br(100 * d['B']['beirada_escuro'])}% → {br(100 * d['C']['beirada_escuro'])}% | "
                 f"{br(100 * d['B']['tinta_perdida'], 2)}% → {br(100 * d['C']['tinta_perdida'], 2)}% | "
                 f"{tamanho(d['B'])} → {tamanho(d['C'])} | {'sim' if d['no_gabarito'] else 'não'} |")
    t.append("")
    t.append(f"Das {len(gabarito)} páginas do gabarito (32 folhas; o Siebmacher 7 e 9 contam duas cada), "
             f"{sum(1 for b in gabarito if b in giram)} giram no livro novo; em nenhuma delas a faixa preta cresceu "
             "(o Siebmacher 9 tem preto em volta nas duas ordens; a Horas 11 a conta acusou e o olho não confirmou).\n")
    t.append("As folhas de contato com todas elas: `img/contato-01.jpg` a `img/contato-11.jpg`.\n")

    t.append("## Arquivos\n")
    t.append("- `dados.json`: as medidas dos três preparos (A, B, C) de cada página.\n"
             "- `classificacao.json`: a separação pela conta (B → C e A → C).\n"
             "- `causa.json`: o passo a passo do corte em 8 páginas.\n"
             "- `projeto-antigo.json`: o programa de antes do G6 contra o de hoje.\n"
             "- `experiencia-cunha.json`: a experiência da cunha repetida.\n"
             "- `img/`: `lado-*.jpg` (lado a lado), `contato-*.jpg`, `causa-*.jpg`, `zoom-*.jpg`.\n"
             "- `scripts/`: `medir.py`, `classificar.py`, `montar.py`, `folhas_de_contato.py`, `causa.py`, "
             "`projeto_antigo.py`, `experiencia_cunha.py`, `relatorio_final.py`.\n")

    saida = relatorio.gravar("\n".join(t), PASTA / "corte-g6",
                             titulo="O corte depois do G6: onde piorou")
    for chave, caminho in saida.items():
        print(chave, caminho, caminho.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
