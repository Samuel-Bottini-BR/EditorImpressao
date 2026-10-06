"""Monta o relatorio "Misto: desenho claro apagado" (06/10/2026) e grava nos tres
formatos (relatorio.gravar). Le trabalho/comparar.json e trabalho/tempo.json,
copia as imagens de olhar para imagens/ (fora do git pelo .gitignore de
relatorios/conferir) e escreve o texto com o veredito de cada pagina, que foi
dado OLHANDO as imagens (o dicionario VEREDITO abaixo).

Uso: python gerar_relatorio.py
"""

from __future__ import annotations

import json
import shutil

import comum
from recorte import recortar

T = comum.TRABALHO
PASTA = comum.PASTA
IMAGENS = PASTA / "imagens"

# o veredito de cada pagina que mudou, dado olhando as imagens (Original | hoje
# | consertado | Preto e branco puro | onde mudou), e onde olhar
VEREDITO = {
    "palatino_p076__inteira": ("melhorou", "a capitular S gravada voltou inteira, como no Preto e branco puro",
                               "Olhe a letra S no alto à esquerda: no Misto de hoje só sobravam a moldura e um arco; no consertado, a letra e a paisagem atrás dela estão de volta."),
    "palatino_p067__inteira": ("melhorou", "o fundo desenhado da capitular M voltou",
                               "Olhe dentro do quadrado da letra M: as folhas e figuras do fundo, que tinham sumido, voltaram."),
    "palatino_p066__inteira": ("melhorou", "a letra ornamental M do rodapé voltou inteira; a moldura ganhou o pontilhado do Preto e branco",
                               "Olhe o \"M.\" à esquerda no rodapé: no Misto de hoje estava pela metade; no consertado está inteiro, como no Preto e branco puro."),
    "ljs47_p103__inteira": ("melhorou (em parte)", "os arcos do diagrama vermelho voltaram mais inteiros; as linhas horizontais continuam picotadas",
                            "Olhe os arcos à direita do diagrama: mais inteiros. As linhas horizontais compridas continuam com falhas (no Preto e branco puro elas saem quase inteiras)."),
    "boecio_p003__inteira": ("melhorou", "a hachura do carimbo da biblioteca voltou",
                             "Olhe o escudo dentro do carimbo redondo (à direita): os tracinhos do escudo voltaram."),
    "opusmajus_p003__inteira": ("melhorou", "a hachura do fundo do selo da editora voltou",
                                "Olhe o fundo riscado atrás do retrato no selo: voltou como no Preto e branco puro."),
    "palatino_p009__inteira": ("melhorou", "a gravura dentro da capitular Q ganhou os traços claros",
                               "Olhe o cavaleiro dentro da letra Q: mais traços do desenho, como no Preto e branco puro."),
    "palatino_p113__inteira": ("melhorou", "o contorno claro do pergaminho enrolado do título voltou",
                               "Olhe o rolo de pergaminho no alto: o contorno e as dobras que faltavam voltaram."),
    "rhetorica_p129__inteira": ("melhorou", "o pontilhado do fundo da gravura de página inteira voltou",
                                "Olhe o fundo atrás da ave: o pontilhado do original voltou."),
    "siebmacher_p007__esquerda": ("melhorou", "a faixa de ornamentos ficou mais cheia, como no Preto e branco puro",
                                  "Olhe a faixa de ornamentos: pedaços claros dos arabescos voltaram."),
    "siebmacher_p009__esquerda": ("melhorou", "a coluna de ornamentos ficou mais cheia",
                                  "Olhe o meio da coluna de ornamentos: pedaços dos arabescos voltaram."),
    "rhetorica_p073__inteira": ("melhorou (pouco)", "o fio vertical da moldura ficou sem a falha",
                                "Olhe o fio vertical à direita do texto: a falha no meio dele fechou."),
    "antiphon_p088__inteira": ("melhorou (pouco)", "uma linha da pauta que estava apagada voltou",
                               "Olhe a linha de cima da quarta pauta (e o começo da quinta): estava faltando no Misto de hoje."),
    "rhetorica_p160__inteira": ("igual", "o fio de baixo ficou um pouco mais cheio; não se nota",
                                "Olhe o fio de baixo: diferença de poucos pontos."),
    "palatino_p104__inteira": ("igual", "poucos pontos no fio da tabela; não se nota",
                               "Olhe o fio vertical da tabela: diferença de poucos pontos."),
    "ljs47_p026__inteira": ("piorou (leve)", "voltaram pedaços da sombra da dobra perto da beirada direita",
                            "Olhe a faixa vertical perto da beirada direita: pedaços da sombra da dobra voltaram, como no Preto e branco puro."),
    "siebmacher_p009__direita": ("piorou (leve)", "voltaram linhas finas da beirada da folha, ao lado da faixa preta que já existia",
                                 "Olhe a beirada direita e a de baixo: linhas finas da borda da folha voltaram ao lado da faixa preta (que já existia no Misto de hoje)."),
}

# recortes feitos a mao (fracao da pagina) para as paginas do defeito
RECORTES = {
    "palatino_p076__inteira": (0.05, 0.12, 0.45, 0.42),
    "palatino_p067__inteira": (0.03, 0.33, 0.48, 0.62),
    "palatino_p066__inteira": (0.05, 0.78, 0.55, 0.95),
    "ljs47_p103__inteira": (0.25, 0.52, 0.8, 0.85),
}

NOMES = {"antiphon": "Antiphon", "boecio": "Boécio", "cursus": "Cursus", "escola": "Escola",
         "graduale": "Graduale", "horas": "Horas", "ljs47": "ljs47", "marial": "Marial",
         "matematica": "Matemática", "opusmajus": "Opus majus", "palatino": "Palatino",
         "pesel": "Pesel", "rhetorica": "Rhetorica", "siebmacher": "Siebmacher"}


def br(valor: float, casas: int) -> str:
    """Numero com virgula decimal, como se escreve no Brasil."""
    return f"{valor:.{casas}f}".replace(".", ",")


def nome(st: str) -> str:
    pid, metade = st.split("__")
    livro, pag = pid.split("_p")
    texto = f"{NOMES.get(livro, livro)} p. {int(pag)}"
    return texto + (f" ({metade})" if metade != "inteira" else "")


def main() -> None:
    from relatorio import gravar

    c = json.loads((T / "comparar.json").read_text(encoding="utf-8"))
    tempo = json.loads((T / "tempo.json").read_text(encoding="utf-8"))
    conta = json.loads((T / "tempo_conta.json").read_text(encoding="utf-8"))["_resumo"]
    IMAGENS.mkdir(exist_ok=True)
    mudaram = [k for k, v in c.items() if not v["identica"]]
    faltando = set(mudaram) ^ set(VEREDITO)
    assert not faltando, f"veredito faltando ou sobrando: {faltando}"

    contagem = {}
    for k in mudaram:
        chave = VEREDITO[k][0].split(" ")[0]
        contagem[chave] = contagem.get(chave, 0) + 1
    iguais = len(c) - len(mudaram)
    total = tempo["_total"]

    partes = [TEXTO_TOPO.format(
        melhorou=contagem.get("melhorou", 0), igual=contagem.get("igual", 0),
        piorou=contagem.get("piorou", 0), identicas=iguais, mudaram=len(mudaram),
        t_antes=br(total["antes"], 1), t_depois=br(total["depois"], 1),
        t_pct=("+" if total["aumento_pct"] >= 0 else "") + br(total["aumento_pct"], 1),
        conta_max=br(conta["maior_s"], 2), conta_med=br(conta["mediana_s"], 3))]

    ordem = ["melhorou", "melhorou (em parte)", "melhorou (pouco)", "igual", "piorou (leve)"]
    partes.append("\n## 3. As páginas que mudaram, uma por uma\n\nCada imagem tem cinco quadros lado a "
                  "lado: **Original · Misto de hoje · Misto consertado · Preto e branco puro · Onde "
                  "mudou**. O quinto quadro é uma cópia clara do original com o que mudou pintado de "
                  "azul; nada foi desenhado por cima dos quatro primeiros.\n")
    primeiro = list(RECORTES)       # as quatro paginas do defeito vem primeiro
    for k in sorted(mudaram, key=lambda s: (s not in primeiro, primeiro.index(s) if s in primeiro else 0,
                                           ordem.index(VEREDITO[s][0]), s)):
        veredito, resumo, onde = VEREDITO[k]
        destino = IMAGENS / f"{k}.jpg"
        if k in RECORTES:
            recortar(k, *RECORTES[k], saida=str(destino))
        else:
            shutil.copy(T / "imagens" / f"{k}__detalhe.jpg", destino)
        partes.append(f"### {nome(k)} - {veredito}\n\n{resumo[0].upper() + resumo[1:]}. **{onde}**\n\n"
                      f"![{nome(k)}](imagens/{destino.name})\n")

    linhas = ["\n## 4. A tabela das 59 páginas\n",
              "\"Idêntica\" = a imagem do Misto consertado é ponto a ponto igual à de hoje (soma da "
              "diferença = 0). \"Pontos que voltaram\" = pontos de tinta que o Misto de hoje mandava "
              "para o branco e o consertado guarda (entre parênteses, em relação a toda a tinta da "
              "página). Tempo = o Misto inteiro da página, mediana de 3 voltas alternadas antes/depois "
              "no mesmo programa. A máquina estava sendo usada por outro agente: diferenças de até 1 s, "
              "para mais ou para menos, são ruído (a conta nova sozinha custa no máximo 0,18 s; item 5 "
              "do topo).\n",
              "| Página | Resultado | Pontos que voltaram | Tempo antes (s) | Tempo depois (s) |",
              "|---|---|---|---|---|"]
    for k in sorted(c):
        v = c[k]
        res = VEREDITO[k][0] if k in VEREDITO else "idêntica"
        volta = "-" if v["identica"] else f"{v['pontos_que_voltaram']} ({br(100 * v['voltou_da_tinta'], 2)}%)"
        linhas.append(f"| {nome(k)} | {res} | {volta} | {br(tempo[k]['antes'], 2)} | {br(tempo[k]['depois'], 2)} |")
    partes.append("\n".join(linhas) + "\n")
    partes.append(TEXTO_FIM)
    texto = "\n".join(partes)
    feitos = gravar(texto, PASTA / "misto-desenho-apagado", titulo="Misto: o desenho claro não some mais")
    print({k: str(v) for k, v in feitos.items()})


TEXTO_TOPO = """# Misto: o desenho claro não some mais

**06/10/2026 · conserto pedido pela gerente, a partir do estudo "Para revisar" · feito pelo
implementador, ramo `misto-desenho-apagado`.** PRONTO PARA CONFERIR (teste de **olho**: só você decide).

## Em poucas palavras

1. **O defeito:** no "Só as letras", jeito de fábrica "Guardar a tinta forte", o programa apagava a
   parte clara de um desenho que o detector de gravura não reconheceu. A capitular S do Palatino 76
   sumia quase inteira; o fundo da capitular M do Palatino 67 e a letra "M" do rodapé do Palatino 66
   ficavam pela metade; o diagrama vermelho do ljs47 p. 103 saía picotado.
2. **Por que acontecia:** fora das linhas de texto, o programa só guardava cada pedacinho de tinta que,
   **sozinho**, fosse tão escuro quanto as letras e não muito pequeno. Uma gravura de traço claro é feita
   de milhares de tracinhos claros e miúdos: cada um, sozinho, ia para o branco, e o desenho sumia.
3. **O conserto:** agora o programa olha o **conjunto**. Quando os tracinhos claros estão **amontoados
   junto de tinta forte** (a moldura da capitular, o traço escuro do desenho) e formam uma parte de
   verdade desse desenho, eles ficam, como no Preto e branco puro. A tinta clara **solta** (a escrita do
   verso na margem, sujeira longe de tudo) continua indo para o branco.
4. **Resultado nas 59 páginas do estudo:** {melhorou} melhoraram, {igual} ficaram iguais à vista,
   {piorou} pioraram de leve (voltaram linhas finas da beirada da folha), e **{identicas} saíram
   idênticas, ponto a ponto**, à de hoje. Nenhuma página ganhou mancha do verso nem fundo cinza.
5. **Tempo:** a conta nova custa no máximo {conta_max} s por página (mediana {conta_med} s), nas
   59 páginas. O Misto inteiro, medido antes e depois alternados no mesmo programa, somou {t_antes} s
   antes e {t_depois} s depois ({t_pct}%).
6. **"Para revisar" não muda:** o aviso continua medindo só a tinta forte; nas 59 páginas, o número que
   decide o aviso saiu igual antes e depois.

## 1. O que mudou no programa

Só `core/misto.py` (e um arquivo de testes novo). Nenhuma tela, nenhum botão, nada no projeto salvo. Só o
jeito de fábrica **"Guardar a tinta forte"** muda; "Tudo em preto e branco", "Só o texto achado" e o Preto
e branco sem "Só as letras" ficam exatamente como estavam.

A regra nova, em português comum: um amontoado de tinta fora do texto é **desenho comido** (e volta
inteiro, como no Preto e branco puro) quando

- tem tinta forte (a moldura, um traço escuro): é ela que diz "aqui tem um desenho";
- é grande (mais que uns três décimos de uma linha de texto ao quadrado): um pontinho ao lado do número
  da página não conta;
- o programa estava apagando **uma fatia de verdade** dele (pelo menos 4%): na pauta de música do
  Graduale, o que se apagava colado nas linhas era a mancha do verso, menos de 2,5% da pauta, e isso
  continua indo para o branco;
- não é uma faixa fina encostada na borda da imagem (a sombra da lombada, a beirada da folha);
- a página tem tons de cinza (num scan que já veio em preto e branco, como o Cursus p. 3, o escuro não
  separa desenho de sujeira: ali nada muda).

### O que foi tentado e não ficou (para ninguém repetir)

| Tentativa | O que deu |
|---|---|
| Só "colado na tinta forte e com bastante tinta apagada" (1 linha² de tinta apagada) | Consertava o Palatino 76 e 67, mas a letra "M" do Palatino 66 continuava pela metade. |
| Só "colado na tinta forte e grande" (sem a fatia mínima) | Consertava as quatro, mas trazia de volta a mancha do verso colada na pauta do Graduale 222 e 223 e a sujeira granulada do Cursus p. 3. |
| Separar pelo escuro de cada pedaço (comparado com o preto das letras) | No Graduale, metade da mancha do verso continuava voltando; no ljs47, parte do diagrama deixava de voltar. Não usado. |
| Separar pela forma (traço fino e comprido contra grão redondo) | Os números dos desenhos e da mancha se cruzam. Não usado. |
| Faixa na borda medida pela caixa (mais fina que uma linha) | A sombra inclinada do alto da Horas 27 escapava. Ficou a espessura média (tinta dividida pelo comprimento). |

## 2. Como foi medido

- As **59 páginas do estudo** (34 do gabarito do Misto e 25 do acervo, as mesmas do relatório de
  06/10), cada uma pelo caminho do programa: a página preparada, a marcação de gravura, o leitor de texto
  rápido, o Misto de fábrica de hoje e o Preto e branco puro. Depois, o Misto consertado com **as mesmas
  entradas** (mesmas linhas de texto, mesma marcação). Conferido: o Misto de hoje refeito por esse atalho
  sai ponto a ponto igual ao do programa nas 59.
- **Olhei todas as páginas que mudaram**, inteiras e de perto, com os cinco quadros. As 37 que não
  mudaram foram conferidas pela soma da diferença das imagens (zero).
- Veredito: **melhorou** (voltou desenho que o Preto e branco puro guarda), **igual** (mudança de poucos
  pontos, que não se vê), **piorou** (voltou mancha do verso, sujeira ou fundo cinza que o Misto de hoje
  tirava).
- Testes de máquina, arquivo por arquivo (números no fim).
"""

TEXTO_FIM = """
## 5. Testes de máquina

Rodados arquivo por arquivo (a máquina tem pouca memória livre):

| Arquivo | Resultado |
|---|---|
| `tests/test_misto.py` | 31 passaram |
| `tests/test_misto_desenho_claro.py` (novo) | 10 passaram |
| `tests/test_misto_consertos.py` | 25 passaram |
| `tests/test_misto_na_tela.py` | 14 passaram |
| `tests/test_misto_no_programa.py` | 23 passaram |
| `tests/test_misto_no_projeto.py` | 12 passaram |
| `tests/test_alerta_pb.py` | 5 passaram |
| `tests/test_preto_e_branco_regra_30_09.py` | 15 passaram |
| `tests/test_so_neste_pedaco_no_preto_e_branco.py` | 8 passaram |
| `tests/test_decoracao_no_preto_e_branco.py` | 12 passaram |

Total: 155 passaram, nenhum falhou. Não rodei a pasta `tests/` inteira de uma vez (pouca memória).

O arquivo novo, `tests/test_misto_desenho_claro.py` (10 testes), desenha páginas de propósito: a
capitular com hachura clara (tem de ficar), a escrita clara do verso na margem (tem de ir para o branco),
o texto das linhas (não pode mudar), o aviso "Para revisar" (continua olhando só a tinta forte), o "Só o
texto achado" (continua apagando), o pontinho ao lado do número da página, a mancha colada numa pauta
grande, a sombra da lombada na borda e o scan sem tons de cinza (nada volta). Conferido: tirando do
programa cada uma das regras novas, o teste daquela regra falha.

## 6. Minha opinião

Vale a pena. As quatro páginas do defeito (Palatino 76, 67 e 66, ljs47 p. 103) melhoraram, as três do
Palatino ficaram iguais ao Preto e branco puro no desenho, e o que o Misto existe para tirar (a mancha do
verso, o fundo cinza) não voltou em nenhuma das 59. As duas pioras são leves e do mesmo tipo: linhas finas
da beirada da folha ao lado de uma faixa preta que já existia (é assunto do corte, como o estudo de 06/10
já dizia).

## 7. Ressalvas

- **Os números da regra (4% da fatia, 0,3 linha², 1/4 de linha na borda) foram acertados nestas mesmas
  59 páginas.** Pode ter "decorado" estes livros. O certo é olhar num livro que não entrou aqui antes de
  confiar de olhos fechados.
- **O ljs47 p. 103 melhorou só em parte.** As linhas horizontais compridas do diagrama, de traço vermelho
  muito claro, continuam picotadas: os pedaços delas não encostam em tinta forte, e a regra só age onde há
  tinta forte. No Preto e branco puro elas saem quase inteiras. Consertar isso pediria outra regra
  (reconhecer linha comprida e clara), que traria o risco de trazer a sombra da dobra junto.
- **Na mesma página (ljs47 p. 103), o começo de várias linhas da coluna da esquerda sai apagado** (a
  tinta ali está desbotada no original). Acontece igual no Preto e branco puro, no Misto de hoje e no
  consertado: é do preto e branco, não do Misto, e não mudou com este conserto. Vai como sugestão para a
  Lista de bugs.
- **Página com desenho colado a uma faixa preta grande** (a beirada do Palatino 76, a moldura do Palatino
  66 e 67): a moldura ganha o mesmo pontilhado que tem no Preto e branco puro. Achei que ficou igual ou
  melhor, mas é gosto.
- **Scan que já veio em preto e branco** (Cursus): o conserto não age. Se um livro assim tiver capitular
  de traço miúdo, ela continua saindo como hoje.
- O veredito é o meu olho, nas imagens reduzidas e nos recortes ampliados. Defeito muito pequeno pode ter
  escapado.
- As imagens grandes ficaram fora do git (`trabalho/`, refazem-se pelos scripts em `scripts/`:
  `rodar_base.py`, `rodar_misto.py`, `comparar.py`, `tempo.py`, `gerar_relatorio.py`).
"""


if __name__ == "__main__":
    main()
