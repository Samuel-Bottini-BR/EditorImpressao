"""Quem tenta quebrar 4 (24/11/2026): a frase (3) depende de a janela abrir. EXECUTADO com o main.py de verdade.

Pergunta: a versão nova não passou no teste rápido e não pôde voltar (o Windows recusou a volta, D-855; ou não há
última boa, D-857). A regra manda a frase (3) "e abre". Mas o teste rápido reprova justamente a versão que NÃO ABRE
(ele importa a janela). Se a janela dela não abre, a frase (3) aparece?

Como: uma instalação de prova (numa pasta minha), o executor de verdade (`atualizacao.Atualizacao`), a regra de verdade,
o disco de verdade (as marcas, o bilhete, os "vistos"), e o `main.main()` de verdade, com a janela principal quebrada
(o import dela falha, como numa versão que perdeu uma peça). De mentira: a peça do Windows e a do Velopack (as do
`tests/ajudante_do_atualizador.py`, que só anotam) e o teste rápido (devolve "não passou"). O PROGRAMDATA e o
LOCALAPPDATA trocados DENTRO do Python, conferidos antes. QT_QPA_PLATFORM=offscreen (nada na tela).

Casos (cada um num processo à parte, porque o main() cria o QApplication):
  A. a volta recusada (o Velopack reabriu a 1.2.0 com `--voltando 1.2.0 1.1.0`), e depois a abertura seguinte
  B. a primeira atualização depois do instalador (sem última boa, o pacote da 1.2.0 em packages\\), e a seguinte
Uso: python prova_janela_que_nao_abre.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

RAMO = Path(__file__).resolve().parents[4]
BASE = RAMO / "saida_teste" / "qtq4" / "janela"
PY = sys.executable


def preparar(caso: str) -> Path:
    import shutil

    pasta = BASE / caso
    if pasta.exists():
        shutil.rmtree(pasta)
    (pasta / "ProgramData").mkdir(parents=True)
    (pasta / "LocalAppData").mkdir()
    return pasta


def um_caso(caso: str, abertura: str) -> dict:
    """Roda dentro do processo filho."""
    pasta = BASE / caso
    os.environ["PROGRAMDATA"] = str(pasta / "ProgramData")
    os.environ["LOCALAPPDATA"] = str(pasta / "LocalAppData")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["USERNAME"] = "Kaique"
    sys.path.insert(0, str(RAMO))
    import assinatura
    import atualizacao
    import versao
    from tests.ajudante_do_atualizador import CHAVE, PACOTE, PUBLICA, VelopackFalso, WindowsFalso

    assert str(atualizacao.pasta_do_estado()).startswith(str(BASE)), atualizacao.pasta_do_estado()
    import historico

    assert str(historico.pasta_de_dados()).startswith(str(BASE)), historico.pasta_de_dados()

    versao.VERSAO = "1.2.0"
    raiz = pasta / "raiz"
    if abertura == "primeira":
        (raiz / "current").mkdir(parents=True)
        (raiz / "packages").mkdir()
        if caso == "A":
            ub = atualizacao.pasta_da_ultima_boa(raiz)
            ub.mkdir()
            dado = b"pacote de prova 1.1.0"
            nome = atualizacao.nome_do_pacote("1.1.0")
            (ub / nome).write_bytes(dado)
            (ub / assinatura.nome_do_arquivo_da_assinatura(PACOTE, "1.1.0")).write_text(
                assinatura.escrever_assinatura(CHAVE, assinatura.VersaoAssinada(
                    PACOTE, "1.1.0", nome, hashlib.sha256(dado).hexdigest())), encoding="utf-8")
            atualizacao.gravar_estado({"reprovadas": ["1.2.0"]})
            argumentos = ["--voltando", "1.2.0", "1.1.0"]
        else:
            (raiz / "packages" / atualizacao.nome_do_pacote("1.2.0")).write_bytes(b"pacote da 1.2.0")
            argumentos = []
    else:
        argumentos = []
    testes: list = []
    vp = VelopackFalso(raiz, None, "sem internet", {})
    a = atualizacao.Atualizacao(windows=WindowsFalso(), velopack=vp, raiz=raiz,
                                fonte=atualizacao.Fonte(str(pasta / "sem-fonte")), por_tras=lambda t: t(),
                                pasta_grava=lambda r: True, garantir_motor=lambda: True,
                                motor_no_lugar=lambda m=None: True,
                                teste=lambda: testes.append(1) or (False, "erro ao abrir: ImportError (de prova)"),
                                chave_publica=PUBLICA)
    saida = a.abrir(argumentos)
    atualizacao._DESTA_ABERTURA = a
    na_fila = [atualizacao.frase_da_falha(e.tipo, e.motivo_da_tela) for e in a._fila_da_tela
               if type(e).__name__ == "MostrarFalha"]
    # A janela principal desta versão não abre (o import dela falha).
    sys.modules["ui.janela_principal"] = None
    import core.aquecimento
    import core.paginas_em_outro_processo
    import ui.perguntas

    core.aquecimento.aquecer_em_segundo_plano = lambda: None
    core.paginas_em_outro_processo.iniciar_em_segundo_plano = lambda: None
    vistos_na_tela: list = []
    ui.perguntas.avisar = lambda janela, titulo, texto, **kw: vistos_na_tela.append(f"[{titulo}] {texto}")
    import main

    erro = ""
    if saida is None:
        try:
            main.main()
        except BaseException:  # noqa: BLE001 - é o que o Python faz no topo: chama o excepthook e sai
            tipo, valor, rastro = sys.exc_info()
            erro = f"{tipo.__name__}: {valor}"
            sys.excepthook(tipo, valor, rastro)
    return {"caso": caso, "abertura": abertura, "linha de comando": argumentos, "saida do executor": saida,
            "testes rapidos rodados": len(testes), "pedidos ao Velopack": vp.nomes(),
            "frases na fila da tela (esperando a janela)": na_fila,
            "o main.main() parou com": erro,
            "o que apareceu na tela (caixas)": vistos_na_tela,
            "marca de sem volta no disco": atualizacao.tem_marca(raiz, atualizacao.MARCA_SEM_VOLTA, "1.2.0"),
            "frases marcadas como vistas": sorted(atualizacao.ler_vistos()),
            "bilhete": atualizacao.ler_estado()}


def main_da_prova() -> None:
    resultado = []
    for caso in ("A", "B"):
        preparar(caso)
        for abertura in ("primeira", "seguinte"):
            r = subprocess.run([PY, "-I", __file__, caso, abertura], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", cwd=str(RAMO))
            linhas = [l for l in r.stdout.splitlines() if l.startswith("RESULTADO ")]
            resultado.append(json.loads(linhas[-1][10:]) if linhas else {"caso": caso, "abertura": abertura,
                                                                         "falhou": r.stderr[-3000:]})
    texto = json.dumps(resultado, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_janela_que_nao_abre-resultado.txt").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) == 3:
        print("RESULTADO " + json.dumps(um_caso(sys.argv[1], sys.argv[2]), ensure_ascii=False))
    else:
        main_da_prova()
