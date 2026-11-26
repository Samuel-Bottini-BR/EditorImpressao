"""A foto da pasta de dados do Samuel (os projetos), antes e depois da prova à vista. NÃO é parte do programa. SÓ LÊ.

    python projetos_antes_e_depois.py tirar antes        grava <BASE>\\registros\\projetos-antes.json
    python projetos_antes_e_depois.py tirar depois
    python projetos_antes_e_depois.py comparar antes depois

A pasta é `%LOCALAPPDATA%\\EditorImpressao` (historico.pasta_de_dados: a mesma do atalho "(desenvolvimento)" dele). O
programa instalado usa ESTA mesma pasta, como sempre: na prova ele grava ali o que sempre grava ao abrir e fechar
(`configuracoes.json`, o `erros.log` se houver erro, `atualizacao-avisos-vistos.json` com as frases já vistas, a pasta
`troca\\` da reabertura). O que importa provar: **nada dentro de `projetos\\` muda e nada some** (D-729, D-882).
A comparação separa as duas coisas.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import prova_comum as comum  # noqa: E402

PASTA = Path(os.environ["LOCALAPPDATA"]) / "EditorImpressao"


def foto() -> dict[str, list]:
    """{caminho relativo: [tamanho, data]} de todo arquivo da pasta (só leitura)."""
    saida = {}
    for raiz, _pastas, arquivos in os.walk(PASTA):
        for nome in arquivos:
            p = Path(raiz) / nome
            try:
                s = p.stat()
                saida[str(p.relative_to(PASTA))] = [s.st_size, round(s.st_mtime, 3)]
            except OSError:
                saida[str(p.relative_to(PASTA))] = [-1, -1]
    return saida


def main(argumentos: list[str]) -> int:
    """A linha de comando (ver o topo)."""
    if len(argumentos) == 2 and argumentos[0] == "tirar":
        destino = comum.REGISTROS / f"projetos-{argumentos[1]}.json"
        destino.parent.mkdir(parents=True, exist_ok=True)
        dados = foto()
        destino.write_text(json.dumps(dados, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"{len(dados)} arquivos em {PASTA}; foto em {destino}")
        return 0
    if len(argumentos) == 3 and argumentos[0] == "comparar":
        a = json.loads((comum.REGISTROS / f"projetos-{argumentos[1]}.json").read_text(encoding="utf-8"))
        b = json.loads((comum.REGISTROS / f"projetos-{argumentos[2]}.json").read_text(encoding="utf-8"))
        sumiram = sorted(a.keys() - b.keys())
        novos = sorted(b.keys() - a.keys())
        mudaram = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
        nos_projetos = [k for k in sumiram + novos + mudaram if k.lower().startswith("projetos" + os.sep)]
        print(f"sumiram: {sumiram or 'nada'}")
        print(f"novos: {novos or 'nada'}")
        print(f"mudaram: {mudaram or 'nada'}")
        print("DENTRO DE projetos\\: " + ("NADA MUDOU, nada sumiu" if not nos_projetos else f"MUDOU: {nos_projetos}"))
        return 0 if not nos_projetos and not sumiram else 1
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
