"""O juiz da rodada do GitHub: o porteiro DA VERSÃO DE TESTE julgando o ramo do agente (R2 e R3 da terceira volta).

Por que existe: os testes em `tests/` rodam o código do próprio ramo conferido. Quem tentou quebrar provou que o ramo
podia escolher com que versão se comparar (o nome da versão de teste vinha do código do ramo) e afrouxar o porteiro
pelo uso (tirar o `re.I`, deixar uma pasta de fora e rodar `--diminuir`) sem nenhum teste acusar. O juiz resolve pela
estrutura: o código e os dados que julgam vêm de fora do ramo.

Como roda (a rodada do GitHub; a mudança exata do workflow está no ONDE-PAREI do passo 0, e quem aplica é a gerente):
1. o workflow (que mora no ramo dos testes, não no ramo do agente) troca o código pelo do ramo pedido, como hoje
   (`trocar_codigo.sh`);
2. busca a versão de teste (`obra-2026-10-26`, nome escrito no workflow) e tira dela, numa pasta à parte, este pacote
   (`regras_dos_agentes/`) e a lista de exceções (`tests/conferencias_excecoes.json`);
3. roda, de dentro dessa pasta, `python -m regras_dos_agentes juiz --conferido <cópia do ramo>`: é este arquivo, da
   versão de teste, julgando a cópia do ramo.

O que o juiz confere:
- a lista do ramo contra a da versão de teste (`porteiro_mudancas.mudancas_na_lista`): nenhum item novo, "quantas"
  maior, passo, situação ou "sim" mudados (R1);
- se a lista da versão de teste já vale (o Samuel disse "sim" e a gerente ligou lá): o porteiro da versão de teste no
  código do ramo, comparado com a lista do ramo. Erro novo barra; lugar tirado da lista que o porteiro da versão de
  teste ainda acha barra (R3: afrouxar o porteiro do ramo não tira nada da lista); item que o código já não tem pede
  para tirar.

O que ele diz, sempre numa linha com a marca (a K21 do formulário procura a marca no registro da rodada):
- `PORTEIRO: CONFERIDO`: passou;
- `PORTEIRO: BARROU`: há o que consertar (a rodada falha);
- `PORTEIRO: NAO CONFERIDO (motivo)`: não julgou o código (ex.: a lista da versão de teste ainda espera o "sim"). A
  rodada não falha por isso, mas a marca aparece no resumo da rodada, num aviso do GitHub, e a K21 trata como "não
  conferido" (código 3), nunca como "passou".

Seguro mexer: as frases. Arriscado: o que é comparado com o quê (a lista de confiança é sempre a da pasta do juiz,
nunca a do ramo) e as marcas (a K21 e o workflow dependem delas).
"""

from __future__ import annotations

import os
from pathlib import Path

from . import excecoes, porteiro
from .porteiro_mudancas import mudancas_na_lista

MARCA_CONFERIDO = "PORTEIRO: CONFERIDO"
MARCA_BARROU = "PORTEIRO: BARROU"
MARCA_NAO_CONFERIDO = "PORTEIRO: NAO CONFERIDO"
RAIZ_DO_JUIZ = Path(__file__).resolve().parent.parent      # a pasta de onde este código foi tirado (a versão de teste)


def julgar(conferido: Path, raiz_do_juiz: Path = RAIZ_DO_JUIZ) -> tuple[str, list[str]]:
    """(marca, frases): o julgamento da cópia `conferido` pelo porteiro e pela lista da pasta `raiz_do_juiz`."""
    conferido = Path(conferido)
    confianca_arq = raiz_do_juiz / excecoes.ARQUIVO_DA_LISTA
    if not confianca_arq.exists():
        return MARCA_NAO_CONFERIDO, ["a versão de teste não tem a lista de exceções"]
    confianca = excecoes.ler(raiz_do_juiz, confianca_arq.read_text(encoding="utf-8"))
    if not (conferido / excecoes.ARQUIVO_DA_LISTA).exists():
        return MARCA_BARROU, ["o ramo apagou a lista de exceções"]
    try:
        do_ramo = excecoes.ler(conferido)
    except excecoes.ListaErrada as erro:
        return MARCA_BARROU, [f"a lista de exceções do ramo está fora do formato: {erro}"]
    frases = mudancas_na_lista(confianca, do_ramo)
    if not confianca.vale:
        motivo = "a lista de exceções da versão de teste ainda espera o \"sim\" do Samuel: o código não foi julgado"
        return (MARCA_BARROU, frases) if frases else (MARCA_NAO_CONFERIDO, [motivo])
    _, achados = porteiro.achados_do_repositorio(conferido)
    frases += excecoes.comparar(achados, do_ramo).explicar()
    return (MARCA_BARROU, frases) if frases else (MARCA_CONFERIDO, [])


def anunciar(marca: str, frases: list[str]) -> str:
    """O texto do julgamento: a marca numa linha, as frases embaixo. No GitHub, também o aviso e o resumo da rodada."""
    detalhe = f" ({frases[0]})" if marca == MARCA_NAO_CONFERIDO and frases else ""
    linhas = [marca + detalhe] + [f"  {f}" for f in frases]
    texto = "\n".join(linhas)
    if os.environ.get("GITHUB_ACTIONS") == "true":
        nivel = {"PORTEIRO: CONFERIDO": "notice", MARCA_BARROU: "error"}.get(marca, "warning")
        print(f"::{nivel} title=Porteiro::{marca}{detalhe}")
        resumo = os.environ.get("GITHUB_STEP_SUMMARY")
        if resumo:
            with open(resumo, "a", encoding="utf-8") as saida:
                saida.write(f"## {marca}{detalhe}\n\n" + "\n".join(f"- {f}" for f in frases) + "\n")
    return texto
