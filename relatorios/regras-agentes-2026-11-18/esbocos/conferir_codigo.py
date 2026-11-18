"""ESBOÇO (18/11/2026, proposta regras-agentes): conferências por busca no código (camada 1 da proposta).

NÃO está ligado em nada. Se for aprovado, viraria um teste em tests/ (roda no GitHub em toda entrega, ninguém pula)
e a mesma função seria chamada por uma conferência antes do commit (rápida, só nos arquivos mudados).

Cada conferência: o código (K..), a regra do catálogo que ela cobra, onde procura, o que procura, e as exceções.
As exceções têm data e motivo: são os lugares de hoje que o plano da parte do Windows vai mudar. Elas só podem
diminuir; a gerente tira cada uma quando o lugar mudar.

Uso (esboço, só lê): python conferir_codigo.py <pasta da cópia>
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

PORTEIRO = "core/windows.py"   # a peça única do plano da parte do Windows (ainda não existe)
CODIGO = ["core", "ui", "."]      # pastas do programa; "." = só os .py da raiz
FORA = {"tests", "terceiros", "relatorios", "docs", "memoria", "historico", "velhos", "dist", "build", ".venv", "motor_kraken"}

# Conversa com o Windows que só o porteiro pode ter (regra R113; caso da etapa 5).
COISAS_DO_PORTEIRO = re.compile(
    r"ShellExecute|['\"]runas['\"]|schtasks|icacls|Set-Acl|Update\.exe|DETACHED_PROCESS|netsh|New-NetFirewallRule|"
    r"Add-WindowsCapability|sc\.exe|windll\.shell32|['\"]powershell(\.exe)?['\"]", re.I)
# Proibido em qualquer lugar, até no porteiro (D-774 e o plano: "nenhum comando de licença à mão").
PROIBIDO = {
    "K02": (re.compile(r"DETACHED_PROCESS"), "R113 e D-774: o PowerShell lançado assim sai sem rodar (etapa 5, defeito 1)"),
    "K03": (re.compile(r"/inheritance:r|/setowner|icacls", re.I), "R113 e plano, peça 2: nenhum comando de licença à mão (etapa 5, defeito 4)"),
}
# Exceções de hoje (a lista só diminui). Formato: arquivo -> (conferências, motivo, data)
EXCECOES = {
    "atualizacao.py": ({"K01", "K02"}, "vai para o porteiro no passo 3 do plano da parte do Windows", "18/11/2026"),
    "core/_testes_a_distancia_windows.py": ({"K01"}, "vira chamadas do porteiro no passo 1", "18/11/2026"),
    "core/testes_a_distancia.py": ({"K01", "K03"}, "passo 4 do plano; K03 sai com a pasta segura (peça 2)", "18/11/2026"),
}
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF☀-➿⬀-⯿️]")
NUMERO_DE_DECISAO = re.compile(r"\bD-\d{3}\b")


def arquivos(raiz: Path):
    """Os .py do programa (core/, ui/ e a raiz), sem testes, terceiros e pastas de dados."""
    for p in raiz.rglob("*.py"):
        rel = p.relative_to(raiz).as_posix()
        if rel.split("/")[0] in FORA or "/." in "/" + rel:
            continue
        if "/" in rel and rel.split("/")[0] not in ("core", "ui"):
            continue
        yield rel, p


def textos_do_codigo(arvore: ast.AST):
    """As strings do código, sem as docstrings (comentário e docstring podem falar de tudo)."""
    docs = set()
    for no in ast.walk(arvore):
        if isinstance(no, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and no.body:
            primeiro = no.body[0]
            if isinstance(primeiro, ast.Expr) and isinstance(getattr(primeiro, "value", None), ast.Constant):
                docs.add(id(primeiro.value))
    for no in ast.walk(arvore):
        if isinstance(no, ast.Constant) and isinstance(no.value, str) and id(no) not in docs:
            yield no.lineno, no.value


def conferir(raiz: Path) -> list[tuple[str, str, int, str]]:
    """(conferência, arquivo, linha, o que achou). Lista vazia = passa."""
    achados = []
    for rel, p in arquivos(raiz):
        fonte = p.read_text(encoding="utf-8", errors="replace")
        try:
            arvore = ast.parse(fonte)
        except SyntaxError as erro:
            achados.append(("K00", rel, erro.lineno or 0, "não deu para ler o arquivo"))
            continue
        isento = EXCECOES.get(rel, (set(), "", ""))[0]
        # K09: core/ não importa ui/ (R049).
        if rel.startswith("core/"):
            for no in ast.walk(arvore):
                nomes = [a.name for a in no.names] if isinstance(no, ast.Import) else \
                        [no.module or ""] if isinstance(no, ast.ImportFrom) else []
                for n in nomes:
                    if n == "ui" or n.startswith("ui."):
                        achados.append(("K09", rel, no.lineno, f"core/ importa {n}"))
        # K10: nada de tkinter (R015).
        for no in ast.walk(arvore):
            if isinstance(no, (ast.Import, ast.ImportFrom)):
                nomes = [a.name for a in no.names] if isinstance(no, ast.Import) else [no.module or ""]
                if any(n.split(".")[0] in ("tkinter", "customtkinter") for n in nomes):
                    achados.append(("K10", rel, no.lineno, "importa tkinter"))
        for linha, texto in textos_do_codigo(arvore):
            # K01: conversa com o Windows fora do porteiro (R113).
            if rel != PORTEIRO and "K01" not in isento and COISAS_DO_PORTEIRO.search(texto):
                achados.append(("K01", rel, linha, f"fala com o Windows fora da peça única: {COISAS_DO_PORTEIRO.search(texto).group(0)}"))
            for k, (padrao, porque) in PROIBIDO.items():
                if k not in isento and padrao.search(texto):
                    achados.append((k, rel, linha, porque))
            # K08: emoji em texto de tela (R019).
            if (rel.startswith("ui/") or rel == "main.py") and EMOJI.search(texto):
                achados.append(("K08", rel, linha, f"emoji em texto: {texto[:40]!r}"))
            # K46: número de decisão em texto que a pessoa vê (R120; Lista de bugs de 17/11).
            if (rel.startswith("ui/") or rel in ("main.py", "atualizacao.py") or "testes_a_distancia" in rel) and \
                    NUMERO_DE_DECISAO.search(texto):
                achados.append(("K46", rel, linha, f"número de decisão em texto: {texto[:50]!r}"))
        # K02 também em nome solto (subprocess.DETACHED_PROCESS não é string).
        if "K02" not in isento and re.search(r"\bDETACHED_PROCESS\b", fonte):
            for n, l in enumerate(fonte.splitlines(), 1):
                if "DETACHED_PROCESS" in l and not l.lstrip().startswith("#"):
                    achados.append(("K02", rel, n, "DETACHED_PROCESS no código"))
    # K11: caminho com acento nos arquivos do programa (R020).
    for p in list((raiz / "core").rglob("*")) + list((raiz / "ui").rglob("*")) + list(raiz.glob("*")):
        if any(ord(c) > 127 for c in p.name):
            achados.append(("K11", p.relative_to(raiz).as_posix(), 0, "nome de arquivo com acento"))
    return achados


if __name__ == "__main__":
    raiz = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    achados = conferir(raiz)
    for k, rel, linha, oque in sorted(set(achados)):
        print(f"{k}  {rel}:{linha}  {oque}")
    print(f"\n{len(set(achados))} achados; exceções em vigor: {len(EXCECOES)}")
