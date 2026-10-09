"""Resume os .json do teste_velocidade.py num texto curto, para ler no log.

Usado pelo .github/workflows/velocidade-windows.yml. Nao e parte do programa.

    python .github/scripts/resumir_velocidade.py <pasta>            (um resultado)
    python .github/scripts/resumir_velocidade.py --comparar <pasta> (todos, lado a lado)

O que imprime: para cada medida do resumo do teste (abrir o livro, trocar de
pagina, processar 10 paginas em Magico pro e em Preto e branco), a mediana das
rodadas e cada rodada, e o tempo POR PAGINA (abrir: por folha do livro;
processar: por pagina processada; trocar: ja e por troca). Com --comparar,
uma linha por medicao (ramo e repeticao, tirados do nome da pasta
velocidade-<ramo>-<repeticao>), e a variacao entre repeticoes do mesmo ramo:
a margem de ruido da maquina do GitHub.

Seguro mudar: o formato. Arriscado: comparar numeros de VERSAO_DO_TESTE
diferentes, ou de maquinas de tipos diferentes (o script mostra o processador
de cada medicao para isso ser conferido).
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

MEDIDAS = (
    ("abrir_total_s", "abrir o livro (total)", "folhas"),
    ("abrir_analise_s", "  so a analise", "folhas"),
    ("troca_media_s", "trocar de pagina (media)", None),
    ("troca_pior_s", "trocar de pagina (pior)", None),
    ("processar_magico_pro_s", "processar em Magico pro", "paginas_processadas"),
    ("processar_preto_e_branco_s", "processar em Preto e branco", "paginas_processadas"),
)


def ler(pasta: Path) -> list[tuple[str, dict]]:
    """(nome da pasta, resultado) de cada .json de medicao dentro de `pasta`."""
    achados = []
    for arquivo in sorted(pasta.rglob("*.json")):
        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(dados, dict) and "resumo" in dados:
            achados.append((arquivo.parent.name, dados))
    return achados


def divisor(resultado: dict, por: str | None) -> int:
    """Quantas folhas/paginas dividir para ter o tempo por pagina."""
    if por == "folhas":
        return int(resultado.get("livro", {}).get("folhas") or 1)
    if por == "paginas_processadas":
        conf = resultado.get("configuracao", {})
        return int(conf.get("paginas_processadas") or conf.get("paginas") or 10)
    return 1


def um(nome: str, r: dict) -> list[str]:
    """As linhas de uma medicao."""
    maq = r.get("maquina", {})
    linhas = [f"== {nome}  (teste v{r.get('versao_do_teste')}, rapido={r.get('rapido')}, "
              f"{maq.get('processador')}, {r.get('duracao_total_s', 0):.0f} s no total)",
              f"   livro: {r.get('livro', {}).get('folhas')} folhas; configuracao: "
              f"{json.dumps(r.get('configuracao', {}), ensure_ascii=False)[:200]}"]
    for chave, texto, por in MEDIDAS:
        m = r["resumo"].get(chave)
        if not m:
            continue
        d = divisor(r, por)
        rod = ", ".join(f"{v:.2f}" for v in m["rodadas"])
        extra = f"  = {m['mediana'] / d:.3f} s por {'folha' if por == 'folhas' else 'pagina'}" if d > 1 else ""
        linhas.append(f"   {texto:32s} mediana {m['mediana']:8.2f} s  (rodadas: {rod}){extra}")
    mem = r.get("memoria", {})
    linhas.append(f"   memoria maxima: {mem.get('pico_mb')} MB ({mem.get('onde')})")
    return linhas


def comparar(achados: list[tuple[str, dict]]) -> list[str]:
    """Tabela: medida x medicao, e o ruido entre repeticoes do mesmo ramo."""
    linhas = ["", "== COMPARACAO (medianas, em segundos) =="]
    nomes = [n for n, _ in achados]
    linhas.append(f"{'medida':32s} " + " ".join(f"{n[-28:]:>28s}" for n in nomes))
    for chave, texto, _por in MEDIDAS:
        vals = [r["resumo"].get(chave, {}).get("mediana") for _, r in achados]
        linhas.append(f"{texto:32s} " + " ".join(
            f"{v:28.2f}" if v is not None else f"{'-':>28s}" for v in vals))
    # ruido: entre repeticoes do mesmo ramo (nome velocidade-<ramo>-<rep>)
    grupos: dict[str, list[dict]] = {}
    for nome, r in achados:
        ramo = nome.rsplit("-", 1)[0]
        grupos.setdefault(ramo, []).append(r)
    linhas.append("")
    linhas.append("== MEDIA POR RAMO e variacao entre as repeticoes (max-min, em % da media) ==")
    for ramo, rs in grupos.items():
        partes = []
        for chave, texto, _por in MEDIDAS:
            vals = [r["resumo"][chave]["mediana"] for r in rs if chave in r["resumo"]]
            if not vals:
                continue
            media = statistics.mean(vals)
            var = (max(vals) - min(vals)) / media * 100 if media else 0
            partes.append(f"{texto.strip()}: {media:.2f} s (+-{var:.0f}%, n={len(vals)})")
        linhas.append(f"{ramo}:")
        linhas += [f"   {p}" for p in partes]
    return linhas


def main() -> int:
    """Imprime o resumo de uma pasta, ou a comparacao de todas."""
    args = sys.argv[1:]
    modo_comparar = bool(args) and args[0] == "--comparar"
    pasta = Path(args[-1] if args else ".")
    achados = ler(pasta)
    if not achados:
        print(f"nenhum resultado do teste de velocidade em {pasta}")
        return 1
    linhas: list[str] = []
    for nome, r in achados:
        linhas += um(nome, r)
    if modo_comparar:
        linhas += comparar(achados)
    print("\n".join(linhas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
