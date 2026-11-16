"""Etapa 2, item 3: cria um projeto de verdade com o programa de 28/10 (cópia `kaique-etapa2-antigo`,
HEAD solta em 3961fbff), pelo código, numa área de trabalho escondida do Windows (nunca na tela do Samuel),
com pasta de dados própria. Depois processa o PDF ("antes").

O que o projeto leva (o que o Kaique faria):
  - livro: cópia das 14 primeiras folhas do Righetti (duas páginas deitadas por folha, com borda preta);
  - girar 1/4 à esquerda todas as folhas (aplicar em "todas");
  - Automático no livro todo: Dividir, Endireitar, Cortar, Limpar (Preto e branco), Montar cadernos;
  - à mão: filtro Mágico pro numa página, corte à mão noutra, uma gravura marcada à mão noutra,
    e uma página tirada do livro;
  - processar o PDF.

Tudo pelas funções da própria tela de 28/10 (rodar_o_automatico, _girar_esquerda, _escolher_filtro,
_mover_recorte, editor de marcação + _selecao_mudou, apagar_pagina, _comecar_a_processar), que gravam
no projeto.json e no acoes.jsonl como o clique gravaria.

Rodar (de dentro da área escondida; ver lancar.py):
  .venv\\Scripts\\python.exe projeto_antigo.py <cópia antiga> <pasta de trabalho>
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
import traceback
from pathlib import Path

ANTIGA = Path(sys.argv[1])
TRAB = Path(sys.argv[2])
DADOS = TRAB / "antigo" / "dados"
SAIDA = TRAB / "antigo" / "saida"
PRINTS = TRAB / "antigo" / "prints"
LIVRO = TRAB / "livros" / "righetti-14-folhas.pdf"
LOG = TRAB / "antigo" / "anotacoes.txt"

for p in (DADOS, SAIDA, PRINTS):
    p.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(DADOS)
os.environ["TEMP"] = os.environ["TMP"] = str(TRAB / "antigo")
os.chdir(ANTIGA)
sys.path.insert(0, str(ANTIGA))
sys.path.insert(0, str(ANTIGA / "relatorios" / "obra-etapa3" / "roteiro"))

_log = open(LOG, "w", encoding="utf-8")


def anotar(chave, valor=None):
    linha = f"{time.strftime('%H:%M:%S')} {chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    _log.write(linha + "\n"); _log.flush()


def main() -> int:
    from PySide6.QtWidgets import QApplication
    import base
    base.app = QApplication.instance() or QApplication(sys.argv)
    base.TRAB = TRAB / "antigo"
    from core import automatico as A
    from core import girar
    from core.selecao import Regiao, Selecao, GRAVURA, RETANGULO, MAO
    from ui.janela_principal import CONFERIR, FINAL, PROGRESSO
    import configuracoes
    configuracoes.escrever("ultima_pasta_de_saida", str(SAIDA))

    j = base.nova_janela(1536, 824)
    j.abrir_livro(str(LIVRO))
    t0 = time.time()
    while time.time() - t0 < 300 and not (j.telas.currentIndex() == CONFERIR and j.tela_conferir._pronta()
                                           and j.trabalho_carregado):
        base.esperar(0.3)
    base.esperar(2)
    anotar("abriu", {"segundos": round(time.time() - t0, 1), "folhas": len(j.projeto.folhas),
                     "paginas": len(j.projeto.paginas)})
    base.print_window(j, PRINTS / "01-aberto.png", so_cliente=False)
    tela = j.tela_conferir

    # girar todas as folhas 1/4 à esquerda (aplicar em "todas")
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    tela._girar_esquerda()
    base.esperar(1)
    anotar("girou", [f.rotacao for f in j.projeto.folhas])

    # Automático no livro todo
    pedido = A.Pedido(etapas=[A.DIVIDIR, A.ENDIREITAR, A.CORTAR, A.LIMPAR, A.CADERNOS],
                      opcoes={"filtro_padrao": "preto_e_branco"})
    ok = j.rodar_o_automatico(pedido=pedido, esperar=True, perguntar=False)
    base.esperar(3)
    anotar("automatico", {"ok": ok, "paginas": len(j.projeto.paginas),
                          "dividir": [f.dividir for f in j.projeto.folhas]})
    base.print_window(j, PRINTS / "02-depois-do-automatico.png", so_cliente=False)

    def ir(i):
        tela.ir_para_pagina(i)
        base.esperar(1.5)

    # página 6 (índice 5): Mágico pro à mão
    ir(5); tela._escolher_filtro("magico_pro")
    # página 8 (índice 7): corte à mão
    ir(7); tela._mover_recorte((0.08, 0.06, 0.92, 0.95))
    # página 10 (índice 9): uma gravura marcada à mão (retângulo no meio da página)
    ir(9)
    sel = Selecao(regioes=[Regiao(tipo=GRAVURA, forma=RETANGULO, origem=MAO,
                                  pontos=[(0.20, 0.30), (0.80, 0.60)])])
    tela.editor_selecao.selecao = sel
    tela._selecao_mudou()
    # página 2 (índice 1): tirada do livro
    ir(1); tela.apagar_pagina()
    base.esperar(1)
    j._salvar_agora()
    base.esperar(2)
    ir(9); base.print_window(j, PRINTS / "03-pagina-10-marcada.png", so_cliente=False)
    anotar("a_mao", {"p6_filtro": j.projeto.paginas[5].filtro, "p8_recorte": j.projeto.paginas[7].recorte,
                     "p10_marcacoes": len(j.projeto.paginas[9].selecao),
                     "p2_apagada": j.projeto.paginas[1].apagada,
                     "cadernos": j.projeto.montar_cadernos, "pasta": str(j.resumo.pasta)})

    # processar
    from modelos import nome_de_saida_sugerido
    destino = SAIDA / f"{nome_de_saida_sugerido(j.projeto)}"
    if destino.suffix.lower() != ".pdf":
        destino = destino.with_suffix(".pdf")
    t1 = time.time()
    # o destino escolhido sem a janela de confirmação (é só ela que fica de fora; o resto é o processar
    # de 28/10, o mesmo do botão "Confirmar e processar")
    j._resolver_destino = lambda: destino
    j.processar()
    while time.time() - t1 < 1800 and j.telas.currentIndex() in (PROGRESSO,):
        base.esperar(0.5)
    base.esperar(2)
    anotar("processou", {"segundos": round(time.time() - t1, 1), "tela": j.telas.currentIndex(),
                         "final": j.telas.currentIndex() == FINAL, "pdf": str(destino),
                         "existe": destino.exists()})
    base.print_window(j, PRINTS / "04-pronto.png", so_cliente=False)
    j.close()
    base.esperar(2)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:
        anotar("ERRO", traceback.format_exc())
        raise SystemExit(3)
