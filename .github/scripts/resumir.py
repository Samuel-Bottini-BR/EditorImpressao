"""Junta os relatorios das 5 partes num resumo curto, para ler no log do GitHub.

Usado pelo job "resumo" do .github/workflows/testes-windows.yml, depois que as
partes terminam. Nao e parte do programa: nada aqui e importado por core/, ui/
ou tests/.

    python .github/scripts/resumir.py <pasta com relatorio-parte-*/ e janela-prints/>

O que imprime (e grava em resumo-geral.txt na mesma pasta):
  - por parte: arquivos, passaram, falharam, erros, pulados, segundos somados;
  - o total, para comparar com a ultima suite do PC do Samuel;
  - cada teste que falhou ou deu erro, com a primeira linha da mensagem;
  - os pulados, agrupados pelo motivo (com quantos e quais arquivos);
  - os tempos de cada arquivo em JSON (para afinar .github/tempos-dos-testes.json);
  - o que ficou na pasta de dados de verdade de cada parte (dados-reais.txt);
  - o roteiro.txt dos prints e o fim do teste_botoes.txt, se existirem.
Existe porque os "artifacts" do GitHub nao baixam de todo lugar: o log do job
sempre se le.

Seguro mudar: o formato do texto. Arriscado: esconder falha ou pulado do resumo
(quem le o resumo decide por ele).
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


def tamanho_png(arquivo: Path) -> str:
    """Largura x altura lidas do cabecalho do PNG (sem biblioteca de imagem)."""
    cabeca = arquivo.read_bytes()[:24]
    if cabeca[:8] != b"\x89PNG\r\n\x1a\n":
        return "?"
    return f"{int.from_bytes(cabeca[16:20], 'big')}x{int.from_bytes(cabeca[20:24], 'big')}"


def main() -> int:
    """Le os .xml de cada parte e imprime o resumo."""
    raiz = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    linhas: list[str] = []
    falhas: list[str] = []
    pulados: dict[str, list[str]] = defaultdict(list)
    tempos: dict[str, float] = {}
    total = defaultdict(int)
    for parte in sorted(raiz.glob("relatorio-parte-*")):
        conta = defaultdict(int)
        for xml in sorted(parte.glob("*.xml")):
            conta["arquivos"] += 1
            for caso in ET.parse(xml).getroot().iter("testcase"):
                nome = f"{caso.get('classname')}::{caso.get('name')}"
                if caso.find("failure") is not None:
                    conta["falharam"] += 1
                    msg = (caso.find("failure").get("message") or "").splitlines()
                    falhas.append(f"FALHOU {nome}: {msg[0][:300] if msg else ''}")
                elif caso.find("error") is not None:
                    conta["erros"] += 1
                    msg = (caso.find("error").get("message") or "").splitlines()
                    falhas.append(f"ERRO   {nome}: {msg[0][:300] if msg else ''}")
                elif caso.find("skipped") is not None:
                    conta["pulados"] += 1
                    motivo = (caso.find("skipped").get("message") or "").strip()[:200]
                    pulados[motivo].append(xml.stem)
                else:
                    conta["passaram"] += 1
        arquivo_tempos = parte / "tempos.json"
        if arquivo_tempos.is_file():
            t = json.loads(arquivo_tempos.read_text(encoding="utf-8"))
            tempos.update(t)
            conta["segundos"] = round(sum(t.values()))
        nao_rodou = [l for l in (parte / "resumo.txt").read_text(encoding="utf-8").splitlines()
                     if l.split()[0] not in ("0", "1", "5")] if (parte / "resumo.txt").is_file() else []
        linhas.append(f"{parte.name}: " + ", ".join(f"{k} {conta[k]}" for k in
                      ("arquivos", "passaram", "falharam", "erros", "pulados", "segundos")))
        linhas += [f"   NAO TERMINOU: {l}" for l in nao_rodou]
        for k, v in conta.items():
            total[k] += v
    linhas.append("TOTAL: " + ", ".join(f"{k} {total[k]}" for k in
                  ("arquivos", "passaram", "falharam", "erros", "pulados", "segundos")))
    linhas.append("(ultima suite completa no PC do Samuel, 08/10: 110 arquivos, 1960 passaram,"
                  " 0 falharam, 59 pulados)")
    linhas.append("\n--- falhas e erros ---")
    linhas += falhas or ["(nenhum)"]
    arquivos_com_falha = sorted({f.split("::")[0].split()[-1].split(".")[-1] for f in falhas})
    for parte in sorted(raiz.glob("relatorio-parte-*")):
        for nome in arquivos_com_falha:
            txt = parte / f"{nome}.txt"
            if txt.is_file():
                linhas.append(f"\n--- {nome}.txt (fim, {parte.name}) ---")
                linhas += txt.read_text(encoding="utf-8", errors="replace").splitlines()[-45:]
    linhas.append("\n--- pulados, por motivo ---")
    for motivo, arquivos in sorted(pulados.items(), key=lambda kv: -len(kv[1])):
        linhas.append(f"{len(arquivos):4d}  {motivo}  [{', '.join(sorted(set(arquivos)))}]")
    for parte in sorted(raiz.glob("relatorio-parte-*")):
        f = parte / "dados-reais.txt"
        if f.is_file():
            texto = f.read_text(encoding="utf-8-sig", errors="replace").splitlines()
            linhas.append(f"\n--- {parte.name}/dados-reais.txt (pasta de dados fora do basetemp) ---")
            linhas += [l for l in texto[:40] if not l.startswith("pasta de dados")]
    for nome in ("janela-prints/prints/roteiro.txt", "janela-prints/teste_botoes.txt"):
        f = raiz / nome
        if f.is_file():
            texto = f.read_text(encoding="utf-8", errors="replace").splitlines()
            linhas.append(f"\n--- {nome} (fim) ---")
            linhas += texto[-40:] if nome.endswith("roteiro.txt") else (
                [l for l in texto if l.lstrip().startswith(("FALHA", "SOBREPOS", "ORDEM", "ERRO"))] + texto[-1:])
    prints = sorted((raiz / "janela-prints" / "prints").glob("*.png"))
    linhas.append("\n--- prints ---")
    linhas += [f"{p.name}  {p.stat().st_size} bytes  {tamanho_png(p)}" for p in prints] or ["(nenhum)"]
    linhas.append("\n--- tempos por arquivo (s) ---")
    linhas.append(json.dumps(dict(sorted(tempos.items())), ensure_ascii=False))
    texto = "\n".join(linhas)
    print(texto)
    (raiz / "resumo-geral.txt").write_text(texto + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
