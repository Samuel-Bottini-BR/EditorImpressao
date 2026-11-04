"""Piloto curto (D-612): a tecla F depois de clicar o Cortar na trilha, na janela de verdade, em
dois caminhos: (a) só "Uma página" (nunca nos pares) e (b) depois de passar o Mover pelos pares.
Serve para saber se o "F não pegou" do piloto.py é do conserto ou já era assim.

Rodar: D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\mover-lado\\piloto_tecla.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.argv = [sys.argv[0]]
_spec = importlib.util.spec_from_file_location("piloto_d612", AQUI / "piloto.py")
piloto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(piloto)          # só define as funções (main fica de fora)
piloto.LOG = open(AQUI / "anotacoes-piloto-tecla.txt", "w", encoding="utf-8")
base = piloto.base


def estado(j, nome):
    from PySide6.QtWidgets import QApplication
    t = j.tela_conferir
    foco = QApplication.focusWidget()
    piloto.anotar(nome, {"aba": t.aba_atual, "mostrar": t.mostrar,
                         "foco": type(foco).__name__ if foco else None,
                         "ativa": j.isActiveWindow()})


def main():
    base.preparar(str(piloto.RAIZ), str(piloto.SCRATCH), limpar=False)
    import projetos
    pasta = piloto.preparar_copia()
    resumo = projetos.ler_resumo(pasta)
    j = base.nova_janela(piloto.LARGURA, piloto.ALTURA)
    _p = piloto.Porteiro()
    j.abrir_livro(resumo.caminho_entrada, resumo=resumo)
    piloto.esperar_tela(j)
    # (a) só "Uma página"
    piloto.ferramenta(j, "F"); estado(j, "a-F")
    piloto.na_trilha(j, "cortar"); estado(j, "a-trilha-cortar")
    piloto.ferramenta(j, "F"); estado(j, "a-F-de-novo")
    piloto.ferramenta(j, "X"); estado(j, "a-X")
    piloto.ferramenta(j, "F"); estado(j, "a-F-depois-do-X")
    # (b) o Mover passa pelos pares
    piloto.mostrar(j, "duas"); estado(j, "b-duas")
    piloto.mostrar(j, "uma"); estado(j, "b-uma")
    piloto.na_trilha(j, "cortar"); estado(j, "b-trilha-cortar")
    piloto.ferramenta(j, "F"); estado(j, "b-F-de-novo")
    base.fechar(j)


main()
