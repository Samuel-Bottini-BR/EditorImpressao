"""O ensaio dos scripts da prova à vista, rodado ANTES da prova, numa pasta de ensaio (nada na tela, nenhuma licença,
nada na instalação do Samuel, que nem existe agora). NÃO é parte do programa.

    python ensaio_dos_scripts.py            as partes A, B e C (sem as versões montadas)
    python ensaio_dos_scripts.py --velopack a parte D (com as versões montadas no estoque)

A  fonte_da_prova: liberar, tirar, sem-resposta, com-resposta, refazer, conferir, com publicações de mentira pequenas
   (o desenho do DestinoPasta), e o índice juntado na ordem certa; os arquivos da fonte são o MESMO arquivo da servida.
B  por_de_lado: o atualizador e o motor de lado e de volta numa "instalação" de ensaio; o segurar-a-pasta num processo
   à parte (aberto por este ensaio) e a prova de que, enquanto ele segura, o Windows NÃO deixa trocar o nome de
   `current` (o erro 32, o mesmo que o Velopack recebe); e que, solto, deixa.
C  vigiar_janelas: um processo (sem janela) que roda de dentro da "instalação" de ensaio aparece e some no registro.
D  com as versões de verdade: a biblioteca do Velopack 1.2.161 de verdade, numa instalação de ensaio (só o manifesto
   1.9.0, um Update.exe de dois bytes: a troca NUNCA é pedida), lendo a fonte de verdade: com só a 1.9.0 servida, nada a
   procurar; com a 1.9.1 servida, acha a 1.9.1, a assinatura do Samuel confere (a função do programa) e o Velopack
   BAIXA o pacote (confere tamanho e soma); com a 1.9.5 servida, acha a 1.9.5 e a assinatura é RECUSADA. No fim, a
   servida volta a ter só a 1.9.0 (o começo da prova), conferido.

Sai com 0 só se tudo conferiu; cada falha é impressa.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENSAIO = Path(r"C:\EditorImpressaoProva\prova-a-vista-25-11\ensaio")
PYTHON = Path(r"D:\programas\EditorImpressao\.venv\Scripts\python.exe")
FALHAS: list[str] = []
SEM_JANELA = subprocess.CREATE_NO_WINDOW       # nenhum processo do ensaio abre janela de console


def cobra(condicao: bool, texto: str) -> None:
    """Anota o resultado de uma conferência."""
    print(("  ok   " if condicao else "  FALHOU ") + texto, flush=True)
    if not condicao:
        FALHAS.append(texto)


def _ambiente(base: Path, programa: Path) -> dict:
    """O ambiente dos processos do ensaio: os dois lugares trocados (prova_comum lê estas variáveis)."""
    return dict(os.environ, PROVA_ENSAIO_BASE=str(base), PROVA_ENSAIO_PROGRAMA=str(programa), PYTHONIOENCODING="utf-8")


def _rodar(script: str, *argumentos: str, base: Path, programa: Path) -> subprocess.CompletedProcess:
    """Roda um script da prova num processo à parte, com os lugares do ensaio."""
    return subprocess.run([str(PYTHON), str(AQUI / script), *argumentos], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=_ambiente(base, programa), timeout=120,
                          creationflags=SEM_JANELA)


def parte_a() -> None:
    """fonte_da_prova com publicações pequenas de mentira."""
    print("A. fonte_da_prova", flush=True)
    base = ENSAIO / "A"
    shutil.rmtree(base, ignore_errors=True)
    for v in ("1.0.1", "1.0.2", "1.0.3"):
        pasta = base / "estoque" / f"v{v}"
        pasta.mkdir(parents=True)
        nome = f"EditorImpressaoPrograma-{v}-full.nupkg"
        (pasta / nome).write_bytes(b"x" * 100)
        (pasta / f"EditorImpressaoPrograma-{v}.assinatura").write_text("assinatura de mentira", encoding="utf-8")
        (pasta / "releases.win.json").write_text(json.dumps({"Assets": [
            {"PackageId": "EditorImpressaoPrograma", "Version": v, "Type": "Full", "FileName": nome, "Size": 100,
             "SHA1": "", "SHA256": ""}]}), encoding="utf-8")
    programa = base / "programa"
    r = _rodar("fonte_da_prova.py", "liberar", "1.0.1", base=base, programa=programa)
    r = _rodar("fonte_da_prova.py", "liberar", "1.0.2", base=base, programa=programa)
    cobra(r.returncode == 0 and "conferido: tudo certo" in r.stdout, f"liberar 1.0.1 e 1.0.2: {r.stdout.strip()}")
    indice = json.loads((base / "fonte" / "releases.win.json").read_text(encoding="utf-8"))
    cobra([a["Version"] for a in indice["Assets"]] == ["1.0.2", "1.0.1"], "o índice da fonte: a mais nova primeiro")
    um = "EditorImpressaoPrograma-1.0.2-full.nupkg"
    cobra(os.path.samefile(base / "fonte" / um, base / "servida" / "v1.0.2" / um), "o arquivo da fonte é o mesmo da servida")
    cobra(not (base / "fonte" / "EditorImpressaoPrograma-1.0.3-full.nupkg").exists(), "o que está só no estoque não vai à fonte")
    r = _rodar("fonte_da_prova.py", "tirar", "1.0.2", base=base, programa=programa)
    indice = json.loads((base / "fonte" / "releases.win.json").read_text(encoding="utf-8"))
    cobra([a["Version"] for a in indice["Assets"]] == ["1.0.1"] and not (base / "fonte" / um).exists()
          and (base / "estoque" / "v1.0.2" / um).is_file(), "tirar 1.0.2: sai da fonte, volta ao estoque inteira")
    _rodar("fonte_da_prova.py", "sem-resposta", base=base, programa=programa)
    cobra(not (base / "fonte" / "releases.win.json").exists(), "sem-resposta: a fonte fica sem índice")
    _rodar("fonte_da_prova.py", "liberar", "1.0.3", base=base, programa=programa)
    cobra(not (base / "fonte" / "releases.win.json").exists()
          and (base / "fonte" / "releases.win.json.sem-resposta").is_file(),
          "liberar com a fonte sem resposta: continua sem resposta (o índice novo fica guardado)")
    r = _rodar("fonte_da_prova.py", "com-resposta", base=base, programa=programa)
    indice = json.loads((base / "fonte" / "releases.win.json").read_text(encoding="utf-8"))
    cobra([a["Version"] for a in indice["Assets"]] == ["1.0.3", "1.0.1"], f"com-resposta: o índice volta, com a 1.0.3: {r.stdout.strip()}")
    shutil.rmtree(base, ignore_errors=True)


def parte_b() -> None:
    """por_de_lado numa instalação de ensaio."""
    print("B. por_de_lado", flush=True)
    base = ENSAIO / "B"
    shutil.rmtree(base, ignore_errors=True)
    programa = base / "programa"
    (programa / "current").mkdir(parents=True)
    (programa / "current" / "um-arquivo.txt").write_text("x", encoding="utf-8")
    (programa / "motor-kraken" / "1").mkdir(parents=True)
    (programa / "motor-kraken" / "1" / "motor.json").write_text("{}", encoding="utf-8")
    (programa / "Update.exe").write_bytes(b"MZ")
    for comando, onde, deve in (("atualizador-de-lado", base / "de-lado" / "Update.exe", True),
                                ("atualizador-de-volta", programa / "Update.exe", True),
                                ("motor-de-lado", base / "de-lado" / "motor-kraken-1", True),
                                ("motor-de-volta", programa / "motor-kraken" / "1", True)):
        r = _rodar("por_de_lado.py", comando, base=base, programa=programa)
        cobra(r.returncode == 0 and onde.exists() == deve, f"{comando}: {r.stdout.strip().splitlines()[:2]}")
    segurando = subprocess.Popen([str(PYTHON), str(AQUI / "por_de_lado.py"), "segurar-a-pasta", "60"],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                 env=_ambiente(base, programa), creationflags=SEM_JANELA)
    try:
        for _ in range(40):
            if (base / "de-lado" / "segurando.txt").exists():
                break
            time.sleep(0.25)
        cobra((base / "de-lado" / "segurando.txt").exists(), "segurar-a-pasta: começou a segurar")
        try:
            os.rename(programa / "current", programa / "current-outro-nome")
            recusou, erro = False, ""
            os.rename(programa / "current-outro-nome", programa / "current")
        except OSError as e:
            recusou, erro = True, f"{e.winerror} {e.strerror}"
        cobra(recusou and erro.startswith("32"), f"enquanto segura, o Windows recusa trocar o nome de current ({erro})")
        r = _rodar("por_de_lado.py", "soltar", base=base, programa=programa)
        saida, _ = segurando.communicate(timeout=30)
        cobra(segurando.returncode == 0 and "soltei" in saida, f"soltar: o segurar saiu sozinho ({saida.strip()})")
    finally:
        if segurando.poll() is None:            # só o processo que ESTE ensaio abriu
            segurando.kill()
    try:
        os.rename(programa / "current", programa / "current-outro-nome")
        os.rename(programa / "current-outro-nome", programa / "current")
        cobra(True, "solto, o Windows deixa trocar o nome de current")
    except OSError as e:
        cobra(False, f"solto, o Windows ainda recusa ({e})")
    shutil.rmtree(base, ignore_errors=True)


def parte_c() -> None:
    """vigiar_janelas vê um processo da instalação de ensaio começar e terminar."""
    print("C. vigiar_janelas", flush=True)
    base = ENSAIO / "C"
    shutil.rmtree(base, ignore_errors=True)
    programa = base / "programa"
    programa.mkdir(parents=True)
    (base / "registros").mkdir(parents=True)
    ping = programa / "ping.exe"
    shutil.copy2(Path(os.environ["SystemRoot"]) / "System32" / "PING.EXE", ping)
    vigia = subprocess.Popen([str(PYTHON), str(AQUI / "vigiar_janelas.py"), "30"], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, encoding="utf-8", env=_ambiente(base, programa),
                             creationflags=SEM_JANELA)
    try:
        time.sleep(2)
        subprocess.run([str(ping), "-n", "3", "127.0.0.1"], capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
        time.sleep(1.5)
        (base / "registros" / "parar-a-vigia").write_text("parar", encoding="utf-8")
        saida, _ = vigia.communicate(timeout=30)
    finally:
        if vigia.poll() is None:
            vigia.kill()
    cobra("PROCESSO COMEÇOU" in saida and "ping.exe" in saida and "PROCESSO TERMINOU" in saida
          and "a vigia parou" in saida, "a vigia anotou o processo começar e terminar, e parou pelo arquivo")
    print("    " + saida.strip().replace("\n", "\n    "))
    shutil.rmtree(base, ignore_errors=True)


def parte_d() -> None:
    """A biblioteca do Velopack de verdade lendo a fonte de verdade (ver o topo)."""
    print("D. o Velopack de verdade lendo a fonte da prova", flush=True)
    # nada do ensaio grava no ProgramData de verdade (o registro da atualização): trocado aqui dentro, conferido
    os.environ["PROGRAMDATA"] = str(ENSAIO / "D-ProgramData")
    sys.path.insert(0, str(AQUI))
    import prova_comum as comum

    sys.path.insert(0, str(comum.RAMO))
    import velopack

    import atualizacao
    from core import conversa_com_o_velopack as conversa

    assert str(atualizacao.pasta_do_estado()).startswith(str(ENSAIO)), atualizacao.pasta_do_estado()

    def fonte(*argumentos: str) -> str:
        r = subprocess.run([str(PYTHON), str(AQUI / "fonte_da_prova.py"), *argumentos], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=300, creationflags=SEM_JANELA)
        return r.stdout.strip()

    servidas = sorted(p.name for p in comum.SERVIDA.iterdir()) if comum.SERVIDA.is_dir() else []
    cobra(servidas == ["v1.9.0"], f"o começo: a servida tem só a 1.9.0 ({servidas})")
    base = ENSAIO / "D"
    shutil.rmtree(base, ignore_errors=True)
    raiz = base / "instalado"
    (raiz / "current").mkdir(parents=True)
    (raiz / "packages").mkdir()
    (raiz / "Update.exe").write_bytes(b"MZ")
    (raiz / "current" / "sq.version").write_text(
        '<?xml version="1.0"?><package><metadata><id>EditorImpressaoPrograma</id><version>1.9.0</version>'
        '<title>Editor de Impressão</title><authors>x</authors><mainExe>EditorImpressao.exe</mainExe></metadata>'
        '</package>', encoding="utf-8")
    loc = velopack.VelopackLocatorConfig(raiz, raiz / "Update.exe", raiz / "packages", raiz / "current" / "sq.version",
                                         raiz / "current", False)
    endereco = str(comum.FONTE)
    try:
        cobra(conversa.procurar(endereco, loc) is None, "só a 1.9.0 servida: nada mais novo")
        print("    " + fonte("liberar", "1.9.1"))
        achada = conversa.procurar(endereco, loc)
        cobra(achada is not None and achada.versao == "1.9.1", f"com a 1.9.1 servida, acha {achada and achada.versao}")
        if achada is not None:
            motivo = atualizacao.conferir_assinatura_do(atualizacao.Fonte(endereco), achada)
            cobra(motivo is None, f"a assinatura da 1.9.1 confere (a função do programa): {motivo}")
            inicio = time.time()
            conversa.baixar(endereco, achada, loc)
            baixado = raiz / "packages" / achada.arquivo
            cobra(baixado.is_file() and baixado.stat().st_size == achada.tamanho,
                  f"o Velopack baixou a 1.9.1 da fonte ({time.time() - inicio:.1f} s, tamanho e soma conferidos por ele)")
            cobra(conversa.pendente(endereco, loc) == "1.9.1", "o Velopack diz: a 1.9.1 espera a troca")
            # o --somar do conferir_instalacao (o 1º passo da volta à mão), numa "última boa" de ensaio
            boa = raiz / atualizacao.PASTA_DA_ULTIMA_BOA
            boa.mkdir()
            os.link(baixado, boa / baixado.name)
            nome_ass = f"EditorImpressaoPrograma-1.9.1.assinatura"
            shutil.copy2(comum.FONTE / nome_ass, boa / nome_ass)
            r = subprocess.run([str(PYTHON), str(AQUI / "conferir_instalacao.py"), "1", "--somar"], capture_output=True,
                               text=True, encoding="utf-8", errors="replace", timeout=300, creationflags=SEM_JANELA,
                               env=_ambiente(comum.BASE, raiz))
            cobra("a última boa (lida como o programa lê): 1.9.1" in r.stdout and
                  "confere com a assinatura do Samuel: SIM" in r.stdout, "--somar: a última boa 1.9.1 confere (SIM)")
        print("    " + fonte("liberar", "1.9.5"))
        achada = conversa.procurar(endereco, loc)
        cobra(achada is not None and achada.versao == "1.9.5", f"com a 1.9.5 servida, acha {achada and achada.versao}")
        if achada is not None:
            motivo = atualizacao.conferir_assinatura_do(atualizacao.Fonte(endereco), achada)
            cobra(motivo is not None, f"a assinatura da 1.9.5 é RECUSADA: {motivo}")
            # o --somar com a falsa: a pasta diria "1.9.5", e a conferência tem de dizer NÃO
            boa = raiz / atualizacao.PASTA_DA_ULTIMA_BOA
            if boa.is_dir():
                os.link(comum.FONTE / achada.arquivo, boa / achada.arquivo)
                shutil.copy2(comum.FONTE / "EditorImpressaoPrograma-1.9.5.assinatura",
                             boa / "EditorImpressaoPrograma-1.9.5.assinatura")
                r = subprocess.run([str(PYTHON), str(AQUI / "conferir_instalacao.py"), "1", "--somar"],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
                                   creationflags=SEM_JANELA, env=_ambiente(comum.BASE, raiz))
                cobra("confere com a assinatura do Samuel: NÃO" in r.stdout, "--somar: a 1.9.5 falsa NÃO confere")
        print("    " + fonte("sem-resposta"))
        try:
            conversa.procurar(endereco, loc)
            cobra(False, "sem resposta: procurar devia dar erro")
        except conversa.ErroDoVelopack as erro:
            cobra(True, f"sem resposta: procurar dá erro, como sem internet ({str(erro)[:90]})")
        print("    " + fonte("com-resposta"))
    finally:
        for v in ("1.9.5", "1.9.1"):
            if (comum.SERVIDA / f"v{v}").is_dir():
                print("    " + fonte("tirar", v))
        shutil.rmtree(base, ignore_errors=True)
    servidas = sorted(p.name for p in comum.SERVIDA.iterdir())
    cobra(servidas == ["v1.9.0"], f"o fim: a servida voltou a ter só a 1.9.0 ({servidas})")
    print("    " + fonte("estado").replace("\n", "\n    "))


def main(argumentos: list[str]) -> int:
    """As partes pedidas."""
    ENSAIO.mkdir(parents=True, exist_ok=True)
    if "--velopack" in argumentos:
        parte_d()
    else:
        parte_a()
        parte_b()
        parte_c()
    print("TUDO CONFERIU" if not FALHAS else f"FALHARAM {len(FALHAS)}: " + " | ".join(FALHAS))
    return 0 if not FALHAS else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
