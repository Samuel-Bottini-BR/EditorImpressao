"""Lê o Livro de decisões (docs/plano/DECISOES.md da versão de teste) em linhas: {D-xxx: campos}."""
from __future__ import annotations
import re
from pathlib import Path
LIVRO = Path(r"D:\programas\EditorImpressao\.claude\worktrees\central-reescrita\docs\plano\DECISOES.md")
CAMPOS = ["num", "data", "palavras", "quer_dizer", "onde", "prova", "situacao", "dono", "fonte"]

def ler():
    linhas = {}
    texto = LIVRO.read_text(encoding="utf-8")
    for linha in texto.splitlines():
        m = re.match(r"^\|\s*(D-\d+)\s*\|", linha)
        if not m:
            continue
        partes = [p.strip() for p in linha.strip().strip("|").split(" | ")]
        if len(partes) < 7:
            continue
        d = dict(zip(CAMPOS, partes))
        d["linha"] = linha
        linhas.setdefault(m.group(1), d)     # a primeira (a tabela principal); a 2a é o resumo
    return linhas, texto

def mencoes(texto, num):
    """Linhas do Livro (fora a da própria decisão) que citam `num` e falam de teste do Samuel."""
    achadas = []
    for linha in texto.splitlines():
        if re.search(rf"\b{num}\b", linha) and not re.match(rf"^\|\s*{num}\s*\|", linha):
            if re.search(r"testad|Samuel.*(funciona|\"ok\"|“ok”)", linha, re.I):
                achadas.append(linha)
    return achadas
