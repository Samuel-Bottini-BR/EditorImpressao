"""Filtro de velocidade: mede ANTES e DEPOIS na MESMA maquina, alternando.

Usado pelo job "velocidade_ab" do .github/workflows/testes-windows.yml (entrada
"velocidade_ab"). Nao e parte do programa. Decisao do Samuel de 19/10/2026
("opcao 2", CLAUDE.md 4.6): em toda mudanca de processamento roda este filtro
no Windows do GitHub; a medida que vale (regra 6 do plano) e a do PC dele, no
fim de cada fase.

POR QUE ALTERNAR NA MESMA MAQUINA: as maquinas do GitHub variam ate 70% entre
si (PARTE -14 do historico). Comparar uma maquina com outra nao diz nada. Aqui
as duas versoes rodam no MESMO job, uma depois da outra (antes, depois, antes,
depois...), e so se compara dentro do job. E o mesmo jeito da medida do PC de
14/10 (relatorios/velocidade-layout3-2026-10-14/ no fase-1: rodar_todas.ps1,
rodar_uma.ps1, juntar.py), de onde vieram os nomes das pastas e da anotacao.

DOIS USOS

    python velocidade_ab.py --antes <pasta> --depois <pasta> --livro <pdf> --saida <pasta>
                            [--rodadas 3] [--aquecer] [--rapido]
        Mede: (aquecimento --rapido em cada versao, se --aquecer) e depois
        antes-1, depois-1, antes-2, depois-2... Cada "rodada" e UMA execucao
        inteira do teste_velocidade.py DAQUELA versao (que por dentro ja faz 3
        repeticoes e da a mediana delas). Grava em <saida>/rodadas/<nome>/ e,
        no fim, junta (o mesmo que o --so-juntar).

    python velocidade_ab.py --so-juntar <saida>
        So le <saida>/rodadas/*/ (os .json do teste e a anotacao.json) e
        escreve a tabela e o veredito. Serve tambem para as pastas do PC de
        14/10 (mesmo formato), o que permite conferir a conta sem medir nada.

O QUE SAI: <saida>/filtro-velocidade.md (tabela + veredito), <saida>/
filtro-velocidade.json (os numeros), e o mesmo .md no resumo do job
($GITHUB_STEP_SUMMARY), se existir. No GitHub, o veredito tambem vira aviso
no topo da pagina da rodada (amarelo quando acusa lentidao). O job NAO fica
vermelho por lentidao: vermelho e so quando a medicao quebrou.

A CONTA DO VEREDITO (por medida):
    - mediana de cada versao = mediana das medianas de cada rodada dela;
    - diferenca % = (mediana depois / mediana antes - 1) x 100;
    - vai-e-vem de uma versao = (maior - menor) das medianas das rodadas dela,
      em % da mediana dela; o vai-e-vem que vale e o MAIOR dos dois;
    - se |diferenca| <= vai-e-vem: "igual (dentro do vai-e-vem)"; acima disso,
      "parece mais lento" ou "parece mais rapido".
    Com 1 rodada so de cada versao nao ha vai-e-vem entre rodadas: usa-se o das
    repeticoes de dentro do teste (e o texto avisa).
    Medidas que dao veredito: abrir o livro, trocar de pagina (media das 20),
    Magico pro em 10 paginas, Preto e branco em 10 paginas.

SEGURO MUDAR: textos, formato dos numeros, colunas das tabelas.
ARRISCADO MUDAR:
    - a conta do veredito (o "igual" de 14/10 no PC foi conferido com ela;
      rode --so-juntar nas pastas de 14/10 depois de mexer);
    - medir as duas versoes em maquinas diferentes ou em paralelo (perde o
      sentido: o filtro so vale dentro do mesmo job, uma rodada por vez);
    - rodar o teste de uma versao com o teste_velocidade.py da outra: cada
      versao usa o SEU (ele importa o codigo dela, ex.: ui.tela_conferir);
      se os dois forem diferentes o texto avisa;
    - tratar o --rapido como medicao (so prova que roda).
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# (chave no "resumo" do .json do teste, nome curto, casas decimais)
MEDIDAS = (
    ("abrir_total_s", "Abrir o livro", 1),
    ("troca_media_s", "Trocar de pagina (media de 20)", 2),
    ("processar_magico_pro_s", "Magico pro, 10 paginas", 1),
    ("processar_preto_e_branco_s", "Preto e branco, 10 paginas", 1),
)
# so aparece na tabela, nao da veredito
MEDIDAS_EXTRAS = (("troca_pior_s", "Trocar de pagina (a pior das 20)", 2),)

LIMITE_POR_RODADA_S = 90 * 60   # uma execucao do teste no GitHub leva 10 a 20 min


# ---------------------------------------------------------------------------
# numeros em portugues
# ---------------------------------------------------------------------------

def n(valor: float | None, casas: int = 1) -> str:
    if valor is None:
        return "-"
    return f"{valor:.{casas}f}".replace(".", ",")


def pct(valor: float | None, sinal: bool = True) -> str:
    if valor is None:
        return "-"
    return (f"{valor:+.1f}%" if sinal else f"{valor:.1f}%").replace(".", ",")


# ---------------------------------------------------------------------------
# medir
# ---------------------------------------------------------------------------

def memoria_livre_gb() -> float | None:
    try:
        import psutil
        return round(psutil.virtual_memory().available / 1024 ** 3, 2)
    except Exception:  # noqa: BLE001 - so anotacao
        return None


def carga_processador_pct() -> float | None:
    try:
        import psutil
        return psutil.cpu_percent(interval=3)
    except Exception:  # noqa: BLE001
        return None


def commit_da_pasta(pasta: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(pasta), "rev-parse", "--short=7", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return "?"


def rodar_uma(braco: str, nome: str, copia: Path, livro: Path, saida: Path,
              rapido: bool) -> int:
    """Uma execucao do teste_velocidade.py da `copia`, gravando em saida/rodadas/nome/.
    Mesmo formato da rodar_uma.ps1 do PC (14/10): terminal.txt, terminal-erros.txt,
    anotacao.json e o que o proprio teste grava (.json, .md, .html)."""
    pasta = saida / "rodadas" / nome
    if pasta.exists():
        print(f"A pasta {pasta} ja existe: parei para nao misturar rodadas.")
        return 4
    pasta.mkdir(parents=True)
    livre = memoria_livre_gb()
    carga = carga_processador_pct()
    inicio = datetime.now(timezone.utc)
    comeco = time.perf_counter()
    comando = [sys.executable, "teste_velocidade.py", str(livro), "--saida", str(pasta)]
    if rapido:
        comando.append("--rapido")
    ambiente = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    print(f"=== {nome} ({braco}, {commit_da_pasta(copia)}) comecou {inicio:%H:%M:%S} UTC, "
          f"memoria livre {n(livre, 2)} GB, processador {n(carga, 0)}%", flush=True)
    try:
        with open(pasta / "terminal.txt", "wb") as saida_padrao, \
                open(pasta / "terminal-erros.txt", "wb") as saida_erros:
            processo = subprocess.run(comando, cwd=copia, stdout=saida_padrao,
                                      stderr=saida_erros, env=ambiente,
                                      timeout=LIMITE_POR_RODADA_S)
        codigo = processo.returncode
    except subprocess.TimeoutExpired:
        codigo = 124
        print(f"   passou de {LIMITE_POR_RODADA_S // 60} minutos: parei.")
    fim = datetime.now(timezone.utc)
    anotacao = {
        "braco": braco,
        "nome": nome,
        "rapido": rapido,
        "copia": str(copia),
        "commit": commit_da_pasta(copia),
        "inicio": inicio.strftime("%Y-%m-%d %H:%M:%S"),
        "fim": fim.strftime("%Y-%m-%d %H:%M:%S"),
        "minutos": round((time.perf_counter() - comeco) / 60, 1),
        "memoria_livre_antes_gb": livre,
        "memoria_livre_depois_gb": memoria_livre_gb(),
        "processador_antes_pct": carga,
        "codigo_de_saida": codigo,
    }
    (pasta / "anotacao.json").write_text(json.dumps(anotacao, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(f"    terminou em {n(anotacao['minutos'], 1)} min, codigo {codigo}", flush=True)
    if codigo != 0:
        for arquivo in ("terminal.txt", "terminal-erros.txt"):
            texto = (pasta / arquivo).read_text(encoding="utf-8", errors="replace")
            print(f"--- fim do {arquivo} ---")
            print("\n".join(texto.splitlines()[-40:]))
    return codigo


def ordem_das_rodadas(rodadas: int, aquecer: bool) -> list[tuple[str, str, bool]]:
    """(braco, nome, rapido) na ordem em que rodam: aquecimentos, depois
    antes-1, depois-1, antes-2, depois-2... (igual a rodar_todas.ps1 de 14/10)."""
    ordem = []
    if aquecer:
        ordem += [("antes", "aquecimento-antes", True), ("depois", "aquecimento-depois", True)]
    for i in range(1, rodadas + 1):
        ordem += [("antes", f"antes-{i}", False), ("depois", f"depois-{i}", False)]
    return ordem


def medir(argumentos: argparse.Namespace) -> int:
    saida = Path(argumentos.saida).resolve()
    copias = {"antes": Path(argumentos.antes).resolve(), "depois": Path(argumentos.depois).resolve()}
    livro = Path(argumentos.livro).resolve()
    for braco, copia in copias.items():
        if not (copia / "teste_velocidade.py").is_file():
            print(f"Falta teste_velocidade.py na versao '{braco}' ({copia}).")
            return 2
    if not livro.is_file():
        print(f"Falta o livro: {livro}")
        return 2
    saida.mkdir(parents=True, exist_ok=True)
    ordem = ordem_das_rodadas(argumentos.rodadas, argumentos.aquecer)
    if argumentos.rapido:
        # so prova que o encanamento funciona: tudo em --rapido
        ordem = [(braco, nome, True) for braco, nome, _ in ordem if not nome.startswith("aquec")]
    codigo_final = 0
    for braco, nome, rapido in ordem:
        codigo = rodar_uma(braco, nome, copias[braco], livro, saida, rapido)
        if codigo != 0:
            print(f"Rodada {nome} saiu com codigo {codigo}: parei.")
            codigo_final = codigo
            break
    juntar(saida, argumentos.resumo, rotulos={"antes": argumentos.rotulo_antes,
                                              "depois": argumentos.rotulo_depois},
           avisos_extras=comparar_testes(copias))
    return codigo_final


def comparar_testes(copias: dict[str, Path]) -> list[str]:
    """Avisa se as duas versoes medem com teste_velocidade.py diferentes."""
    try:
        a = (copias["antes"] / "teste_velocidade.py").read_bytes()
        d = (copias["depois"] / "teste_velocidade.py").read_bytes()
    except OSError:
        return []
    if a == d:
        return []
    return ["O teste_velocidade.py das duas versoes NAO e igual: cada versao mediu com o seu. "
            "Se a mudanca foi no que o teste mede (VERSAO_DO_TESTE), os numeros nao se comparam."]


# ---------------------------------------------------------------------------
# juntar
# ---------------------------------------------------------------------------

def ler_rodadas(saida: Path) -> list[dict]:
    """As rodadas de medicao (sem aquecimento), na ordem em que rodaram."""
    achadas = []
    for pasta in sorted((saida / "rodadas").glob("*")):
        if not pasta.is_dir() or pasta.name.startswith("aquecimento"):
            continue
        arquivos = sorted(pasta.glob("velocidade-*.json"))
        anotacao_arq = pasta / "anotacao.json"
        anotacao = (json.loads(anotacao_arq.read_text(encoding="utf-8-sig"))
                    if anotacao_arq.is_file() else {})
        braco = anotacao.get("braco") or pasta.name.split("-")[0]
        dados = json.loads(arquivos[0].read_text(encoding="utf-8")) if arquivos else None
        achadas.append({"nome": pasta.name, "braco": braco, "dados": dados, "anotacao": anotacao})
    achadas.sort(key=lambda r: (r["anotacao"].get("inicio") or "", r["nome"]))
    return achadas


def comparar(rodadas: list[dict]) -> list[dict]:
    """A conta do veredito, por medida (ver o cabecalho)."""
    linhas = []
    for chave, nome, casas in MEDIDAS + MEDIDAS_EXTRAS:
        medianas = {"antes": [], "depois": []}
        internas = {"antes": [], "depois": []}
        for r in rodadas:
            if r["dados"] is None or r["braco"] not in medianas:
                continue
            m = r["dados"]["resumo"][chave]
            medianas[r["braco"]].append(m["mediana"])
            internas[r["braco"]].extend(m["rodadas"])
        if not medianas["antes"] or not medianas["depois"]:
            continue
        ma, md = statistics.median(medianas["antes"]), statistics.median(medianas["depois"])
        dif = (md / ma - 1) * 100

        def vaivem(braco: str, centro: float) -> tuple[float, str]:
            valores = medianas[braco] if len(medianas[braco]) >= 2 else internas[braco]
            origem = "rodadas" if len(medianas[braco]) >= 2 else "repeticoes internas"
            return (max(valores) - min(valores)) / centro * 100, origem

        va, origem_a = vaivem("antes", ma)
        vd, origem_d = vaivem("depois", md)
        limite = max(va, vd)
        if abs(dif) <= limite:
            veredito = "igual"
        elif dif > 0:
            veredito = "mais lento"
        else:
            veredito = "mais rapido"
        pares = [d - a for a, d in zip(medianas["antes"], medianas["depois"])]
        linhas.append({
            "chave": chave, "nome": nome, "casas": casas,
            "da_veredito": (chave, nome, casas) in MEDIDAS,
            "antes": medianas["antes"], "depois": medianas["depois"],
            "mediana_antes": ma, "mediana_depois": md, "diferenca_pct": dif,
            "vaivem_antes_pct": va, "vaivem_depois_pct": vd, "vaivem_pct": limite,
            "vaivem_origem": origem_a if origem_a == origem_d else f"{origem_a}/{origem_d}",
            "pares": pares, "veredito": veredito,
        })
    return linhas


def veredito_geral(linhas: list[dict]) -> str:
    """Uma frase: "igual (dentro do vai-e-vem)" / "parece mais lento: X" /
    "parece mais rapido: X". Lentidao vem primeiro (e o que a regra 6 pega)."""
    def lista(qual: str) -> str:
        return "; ".join(f"{l['nome']} {pct(l['diferenca_pct'])} (vai-e-vem {pct(l['vaivem_pct'], False)})"
                         for l in linhas if l["da_veredito"] and l["veredito"] == qual)
    lentas, rapidas = lista("mais lento"), lista("mais rapido")
    if lentas:
        frase = f"parece mais lento: {lentas}"
        if rapidas:
            frase += f" | e mais rapido em: {rapidas}"
        return frase
    if rapidas:
        return f"parece mais rapido: {rapidas}"
    return "igual (dentro do vai-e-vem)"


def montar_texto(rodadas: list[dict], linhas: list[dict], rotulos: dict[str, str],
                 avisos: list[str]) -> str:
    t: list[str] = []
    feitas = [r for r in rodadas if r["dados"] is not None]
    falhas = [r for r in rodadas if r["dados"] is None]
    commits = {b: sorted({r["anotacao"].get("commit", "?") for r in rodadas if r["braco"] == b})
               for b in ("antes", "depois")}
    t.append("# Filtro de velocidade: antes x depois na mesma maquina\n")
    if linhas:
        t.append(f"**Veredito: {veredito_geral(linhas)}**\n")
    else:
        t.append("**Sem veredito: faltam rodadas completas das duas versoes.**\n")
    for b in ("antes", "depois"):
        rot = rotulos.get(b) or ""
        t.append(f"- {b.capitalize()}: {rot + ' ' if rot else ''}(commit {', '.join(commits[b]) or '?'})")
    processadores = sorted({r["dados"]["maquina"].get("processador", "?") for r in feitas})
    t.append(f"- Maquina: {', '.join(processadores) or '?'}")
    por = {b: sum(1 for r in feitas if r["braco"] == b) for b in ("antes", "depois")}
    t.append(f"- Rodadas completas: {por['antes']} antes, {por['depois']} depois "
             "(alternadas; cada rodada = uma execucao inteira do teste_velocidade.py, "
             "que por dentro faz suas repeticoes e da a mediana)")
    minutos = sum(r["anotacao"].get("minutos") or 0 for r in rodadas)
    if minutos:
        t.append(f"- Tempo das rodadas de medicao: {n(minutos, 0)} min")
    rapidos = [r["nome"] for r in feitas if r["dados"].get("rapido")]
    versoes = sorted({r["dados"].get("versao_do_teste") for r in feitas}, key=str)
    if rapidos:
        avisos = avisos + ["Rodadas em --rapido (" + ", ".join(rapidos) + "): os numeros NAO valem como medicao."]
    if len(versoes) > 1:
        avisos = avisos + [f"VERSAO_DO_TESTE diferente entre rodadas ({versoes}): os numeros nao se comparam."]
    if falhas:
        avisos = avisos + ["Rodadas sem resultado: " + ", ".join(
            f"{r['nome']} (codigo {r['anotacao'].get('codigo_de_saida')})" for r in falhas)]
    for aviso in avisos:
        t.append(f"- **Atencao:** {aviso}")
    t.append("")
    t.append("Regra do veredito: diferenca entre as medianas maior que o vai-e-vem (a maior distancia "
             "entre rodadas da MESMA versao, em %). Dentro disso, o filtro nao distingue: \"igual\". "
             "Quem da a medida que vale (regra 6) e o PC do Samuel no fim da fase.\n")

    if linhas:
        t.append("## Antes x depois\n")
        t.append("| Medida | Mediana antes | Mediana depois | Diferenca | Vai-e-vem antes | "
                 "Vai-e-vem depois | Pares (depois - antes) | Veredito |")
        t.append("|---|---|---|---|---|---|---|---|")
        for l in linhas:
            c = l["casas"]
            pares = "; ".join(f"{p:+.{c}f}".replace(".", ",") for p in l["pares"])
            ver = l["veredito"] if l["da_veredito"] else f"({l['veredito']}, so informativo)"
            t.append(f"| {l['nome']} | {n(l['mediana_antes'], c)} s | {n(l['mediana_depois'], c)} s | "
                     f"{pct(l['diferenca_pct'])} | {pct(l['vaivem_antes_pct'], False)} | "
                     f"{pct(l['vaivem_depois_pct'], False)} | {pares} s | {ver} |")
        if any("internas" in l["vaivem_origem"] for l in linhas):
            t.append("\nCom 1 rodada so, o vai-e-vem e o das repeticoes de dentro do teste (mais "
                     "estreito que o entre rodadas: o veredito fica mais sensivel).")
        t.append("")

    t.append("## Cada rodada, na ordem em que rodou (mediana das repeticoes internas)\n")
    cab = " | ".join(nome for _c, nome, _k in MEDIDAS)
    t.append(f"| Rodada | Commit | Inicio (UTC) | {cab} | Durou |")
    t.append("|---|---|---|" + "---|" * len(MEDIDAS) + "---|")
    for r in rodadas:
        a = r["anotacao"]
        if r["dados"] is None:
            celulas = ["falhou"] * len(MEDIDAS)
        else:
            celulas = [n(r["dados"]["resumo"][c]["mediana"], k) + " s" for c, _nome, k in MEDIDAS]
        t.append(f"| {r['nome']} | {a.get('commit', '?')} | {str(a.get('inicio', ''))[11:16]} | "
                 + " | ".join(celulas) + f" | {n(a.get('minutos'), 1)} min |")
    t.append("")
    t.append("## Cada repeticao interna\n")
    t.append("| Rodada | " + cab + " |")
    t.append("|---|" + "---|" * len(MEDIDAS))
    for r in feitas:
        celulas = ["; ".join(n(v, k) for v in r["dados"]["resumo"][c]["rodadas"]) for c, _nome, k in MEDIDAS]
        t.append(f"| {r['nome']} | " + " | ".join(celulas) + " |")
    t.append("")
    return "\n".join(t)


def juntar(saida: Path, resumo: str | None, rotulos: dict[str, str] | None = None,
           avisos_extras: list[str] | None = None) -> int:
    rodadas = ler_rodadas(saida)
    if not rodadas:
        print("Nenhuma rodada encontrada em", saida / "rodadas")
        return 1
    linhas = comparar(rodadas)
    texto = montar_texto(rodadas, linhas, rotulos or {}, avisos_extras or [])
    (saida / "filtro-velocidade.md").write_text(texto, encoding="utf-8")
    (saida / "filtro-velocidade.json").write_text(json.dumps({
        "veredito": veredito_geral(linhas) if linhas else None,
        "medidas": linhas,
        "rodadas": [{"nome": r["nome"], "braco": r["braco"], "anotacao": r["anotacao"],
                     "resumo": r["dados"]["resumo"] if r["dados"] else None} for r in rodadas],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(texto)
    if os.environ.get("GITHUB_ACTIONS") == "true" and linhas:
        # aviso no topo da pagina da rodada (amarelo se acusou lentidao)
        geral = veredito_geral(linhas)
        nivel = "warning" if geral.startswith("parece mais lento") else "notice"
        print(f"::{nivel} title=Filtro de velocidade::{geral}")
    destino = resumo or os.environ.get("GITHUB_STEP_SUMMARY")
    if destino:
        with open(destino, "a", encoding="utf-8") as f:
            f.write(texto + "\n")
    return 0 if linhas else 1


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    p = argparse.ArgumentParser(description="Filtro de velocidade: antes x depois alternados.")
    p.add_argument("--so-juntar", metavar="PASTA", help="so junta as rodadas ja medidas em PASTA")
    p.add_argument("--antes", help="pasta com o programa de ANTES")
    p.add_argument("--depois", help="pasta com o programa de DEPOIS")
    p.add_argument("--livro", help="o PDF medido (marial_300.pdf)")
    p.add_argument("--saida", help="pasta onde gravar as rodadas e a tabela")
    p.add_argument("--rodadas", type=int, default=3, help="rodadas de CADA versao (padrao 3)")
    p.add_argument("--aquecer", action="store_true",
                   help="antes de medir, uma rodada --rapido de cada versao (nao entra na conta)")
    p.add_argument("--rapido", action="store_true",
                   help="tudo em --rapido: so prova que funciona, numeros NAO valem")
    p.add_argument("--rotulo-antes", default="", help="nome da versao de antes (ramo/commit pedido)")
    p.add_argument("--rotulo-depois", default="", help="nome da versao de depois")
    p.add_argument("--resumo", help="arquivo onde acrescentar a tabela (padrao: $GITHUB_STEP_SUMMARY)")
    a = p.parse_args(argv)
    if a.so_juntar:
        return juntar(Path(a.so_juntar), a.resumo,
                      rotulos={"antes": a.rotulo_antes, "depois": a.rotulo_depois})
    if not (a.antes and a.depois and a.livro and a.saida):
        p.error("para medir: --antes, --depois, --livro e --saida")
    if not 1 <= a.rodadas <= 10:
        p.error("--rodadas entre 1 e 10")
    return medir(a)


if __name__ == "__main__":
    raise SystemExit(main())
