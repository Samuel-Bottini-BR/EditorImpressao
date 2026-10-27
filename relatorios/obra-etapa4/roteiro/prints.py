"""A janela de VERDADE, fora da tela, no caminho do Kaique do zero (obra de 26/10/2026, etapa 4:
dividir à mão folha por folha): abrir o Righetti (escaneado de lado) sem nada marcado → girar
todas as folhas ¼ à esquerda → Automático só com "Dividir" → a página, uma por vez (D-007) →
ferramenta Dividir na folha 96 (a folha inteira com a linha, para consertar) → "não dividir
esta" → "dividir esta" à mão (a faixa preta da tampa sai: D-495) → de volta à página, uma por
vez. Cliques e teclas por mensagens nativas do Windows (PostMessage), prints por PrintWindow
(relatorios/obra-etapa3/roteiro/base.py, do verificador de 22-23/10). Dados e TEMP numa pasta
de saida_teste/, nunca a pasta de dados do Samuel; o livro é uma CÓPIA (o acervo só é lido).
Guarda o PID e fecha só a própria janela (WM_CLOSE).

Uso (na worktree):
    .venv\\Scripts\\python.exe relatorios\\obra-etapa4\\roteiro\\prints.py <worktree> <prefixo>
<worktree> = o código a abrir (esta worktree, ou a cópia do código antigo para o "antes");
<prefixo> = nome dos prints ("depois" ou "antes"). Prints em relatorios/obra-etapa4/prints/.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
sys.path.insert(0, str(RAIZ / "relatorios" / "obra-etapa3" / "roteiro"))
import base  # noqa: E402

WORKTREE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RAIZ
PREFIXO = sys.argv[2] if len(sys.argv) > 2 else "depois"
PRINTS = RAIZ / "relatorios" / "obra-etapa4" / "prints"
TRAB = RAIZ / "saida_teste" / "obra-etapa4" / f"janela-{PREFIXO}"
RIGHETTI = "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf"
FOLHA = 95            # a folha 96 (D-495)


def _p(widget, nome: str):
    return base.print_window(widget, PRINTS / f"{PREFIXO}-{nome}.png")


def _esperar_ate(condicao, segundos=60.0) -> bool:
    for _ in range(int(segundos / 0.2)):
        if condicao():
            return True
        base.esperar(0.2)
    return condicao()


def _letra(janela, letra: str) -> None:
    vk = base.user32.VkKeyScanW(ord(letra.lower())) & 0xFF
    base.tecla(janela, vk)


def _clique_na_trilha(janela, tela, ferramenta: str) -> bool:
    trilha = tela.trilha
    for indice, ret in trilha.retangulos().items():
        if trilha.a_vista(indice) == ferramenta:
            base.clique(janela, trilha, ret.center())
            return True
    return False


def main() -> None:
    (RAIZ / "saida_teste" / "obra-etapa4").mkdir(parents=True, exist_ok=True)
    (RAIZ / "saida_teste" / "obra-etapa4" / f"pid-prints-{PREFIXO}.txt").write_text(str(os.getpid()))
    print("PID deste processo:", os.getpid(), flush=True)
    base.preparar(str(WORKTREE), str(TRAB))
    from ui.tela_conferir import ABA_CORTE

    livro = base.copia(RIGHETTI, "Righetti.pdf")
    janela = base.nova_janela(1280, 657)
    _p(janela, "00-tela-dos-livros")
    janela.abrir_livro(str(livro))
    base.esperar(2.0)
    tela = janela.tela_conferir
    _esperar_ate(lambda: getattr(janela, "medida_ao_abrir", None) is None
                 or not janela.medida_ao_abrir.isRunning(), 180)
    base.esperar(1.0)
    projeto = janela.projeto
    base.conferir(not projeto.dividir_folhas and len(projeto.paginas) == len(projeto.folhas),
                  "abrir sem nada marcado: uma página por folha, nada dividido")
    _p(janela, "01-abrir-o-righetti-de-lado")

    # girar: o bloco "Girar a folha" do Propriedades, "aplicar em: todas", "¼ à esquerda"
    from core.girar import ALCANCE_TODAS, GIRO_ESQUERDA

    tela.paineis.abrir("props")
    base.esperar(0.8)
    barra = tela.barra_girar
    barra.combo_alcance.setCurrentIndex(barra.combo_alcance.findData(ALCANCE_TODAS))
    base.esperar(0.3)
    base.clique(janela, barra.botoes_de_giro[GIRO_ESQUERDA])
    base.esperar(2.5)
    base.conferir(all(f.rotacao == GIRO_ESQUERDA for f in projeto.folhas),
                  "girar ¼ à esquerda em todas: as 135 folhas giradas")
    _p(janela, "02-girado-todas-as-folhas")

    if not hasattr(__import__("core"), "dividir_a_mao") and not (WORKTREE / "core" / "dividir_a_mao.py").exists():
        # o código antigo: na ferramenta Dividir, "dividir esta" fica cinza na folha girada
        _letra(janela, "d")
        base.esperar(1.5)
        tela._ir_para(FOLHA)
        base.esperar(2.0)
        base.conferir(not tela.botao_nao_dividir.isEnabled(),
                      "código antigo: 'dividir esta' cinza na folha girada (lista única 3.1)")
        _p(janela, "03-dividir-esta-cinza")
        base.fechar(janela)
        base.gravar_resultados(TRAB)
        return

    # o Automático: só "Dividir", no livro todo
    from core import automatico as A

    tela.paineis.abrir("automatico")
    base.esperar(0.8)
    painel = tela.paineis.automatico
    lista = painel.lista
    item = next((lista.item(i) for i in range(lista.count())
                 if lista.item(i).data(0x0100) == A.DIVIDIR), None)
    if item is None:            # a lista guarda a etapa em outro papel: pelo texto
        item = next(lista.item(i) for i in range(lista.count())
                    if lista.item(i).text().startswith(A.NOMES[A.DIVIDIR]))
    ret = lista.visualItemRect(item)
    from PySide6.QtCore import QPoint

    base.clique(janela, lista.viewport(), QPoint(ret.left() + 14, ret.center().y()))
    base.esperar(0.8)
    base.conferir(painel.estado.marcadas == {A.DIVIDIR}, "Automático: só 'Dividir' marcado, pelo clique")
    _p(janela, "03-automatico-so-dividir")
    base.clique(janela, painel.botao_rodar)
    _esperar_ate(lambda: projeto.dividir_folhas and len(janela.projeto.paginas) > 200, 300)
    base.esperar(3.0)
    tela = janela.tela_conferir
    projeto = janela.projeto
    divididas = sum(1 for f in projeto.folhas if f.dividir)
    base.conferir(divididas >= 130, f"o Automático dividiu {divididas} de {len(projeto.folhas)} folhas")
    base.conferir(tela.aba_atual != ABA_CORTE and not tela.trabalha_com_folhas,
                  "D-007: depois de dividir, a tela mostra uma página por vez")
    tela.paineis.abrir("props")
    tela.ir_para_pagina(2 * FOLHA + 1)
    base.esperar(4.0)
    _p(janela, "04-dividido-uma-pagina-por-vez")

    # consertar: a ferramenta Dividir (tecla D), a folha 96 inteira com a linha
    _letra(janela, "d")
    base.esperar(1.5)
    tela._ir_para(FOLHA)
    base.esperar(4.0)
    base.conferir(tela.trabalha_com_folhas and tela.indice_folha == FOLHA,
                  "D-007: no Dividir, a folha inteira com a linha (para consertar)")
    base.conferir(tela.botao_nao_dividir.isEnabled() and tela.botao_nao_dividir.text() == "não dividir esta",
                  "o botão diz 'não dividir esta' e está aceso")
    _p(janela, "05-dividir-folha-96-para-consertar")
    base.clique(janela, tela.botao_nao_dividir)
    base.esperar(3.0)
    base.conferir([p.metade for p in projeto.paginas if p.folha == FOLHA] == ["inteira"],
                  "'não dividir esta': a folha 96 virou uma página só (as outras não mudaram)")
    base.conferir(tela.botao_nao_dividir.isEnabled() and tela.botao_nao_dividir.text() == "dividir esta",
                  "'dividir esta' aceso")
    _p(janela, "06-nao-dividir-esta")
    base.clique(janela, tela.botao_nao_dividir)
    base.esperar(4.0)
    folha = projeto.folhas[FOLHA]
    base.conferir(folha.dividir and len(folha.tampa_do_scanner or []) == 5,
                  "'dividir esta' à mão: dividida de novo e a tampa do scanner achada (D-495)")
    _p(janela, "07-dividir-esta-a-mao")

    # de volta à página (a Mão da trilha): a página 192 (direita da folha 96), sem a faixa
    if not _clique_na_trilha(janela, tela, "mao"):
        tela.escolher_ferramenta("mao")
    base.esperar(1.0)
    base.conferir(not tela.trabalha_com_folhas, "a Mão: de volta à página, uma por vez")
    tela.ir_para_pagina(next(p.indice for p in projeto.paginas
                             if p.folha == FOLHA and p.metade == "direita"))
    base.esperar(5.0)
    _p(janela, "08-pagina-da-folha-96-sem-a-faixa")
    tela.ir_para_pagina(next(p.indice for p in projeto.paginas
                             if p.folha == FOLHA - 1 and p.metade == "direita"))
    base.esperar(5.0)
    _p(janela, "09-pagina-da-folha-95-pelo-automatico")
    base.fechar(janela)
    base.gravar_resultados(TRAB)


if __name__ == "__main__":
    main()
