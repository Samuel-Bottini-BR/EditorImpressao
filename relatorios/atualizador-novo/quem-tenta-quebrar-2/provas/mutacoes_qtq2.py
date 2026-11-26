"""Mutações de quem tenta quebrar, volta 2 (24/11/2026): as proteções que a volta 2 e a volta 2b ACRESCENTARAM (e as
que ficaram em volta delas), desligadas uma por vez, rodando TODOS os arquivos de teste do atualizador.

Roda numa CÓPIA do ramo (git archive), nunca no worktree: a cópia é o primeiro argumento. Para cada mutação: troca o
trecho (que tem de aparecer uma vez só), roda os arquivos de teste e devolve o arquivo como estava.
"SOBREVIVEU" = nenhum teste falhou com a proteção desligada (D-811 a D-813, D-827).
Uso: python mutacoes_qtq2.py <cópia do ramo> [--so-contar]
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1])
A, W, F, U = "atualizacao.py", "core/windows.py", "core/fases_da_atualizacao.py", "ui/aviso_de_atualizacao.py"
P = "regras_dos_agentes/porteiro.py"
TESTES = ["tests/test_atualizador_novo.py", "tests/test_atualizador_volta2.py", "tests/test_fases_da_atualizacao.py",
          "tests/test_windows_preparo_do_computador.py", "tests/test_decisoes_atualizacao.py",
          "tests/test_decisoes_ajudante_da_atualizacao.py", "tests/test_decisoes_preparo_d749.py",
          "tests/test_velopack_de_verdade.py", "tests/test_porteiro_licenca_que_acrescenta.py",
          "tests/test_decisoes_testes_a_distancia.py", "tests/test_windows_peca.py"]

MUTACOES = [
    ("V1 G1: 'não deu para saber' conta como 'a troca acabou' (anota falha)", F,
     "e.troca_em_curso is not False:", "e.troca_em_curso is True:"),
    ("V2 G1: em curso abre a janela em vez de sair", F,
     "                Sair(0)]\n        return _abertura_comum(novo, e, [Registrar(\"não deu para saber",
     "                ]\n        return _abertura_comum(novo, e, [Registrar(\"não deu para saber"),
    ("V3 G1: o Update.exe cujo caminho não deu para ler não conta", W,
     " or c.endswith(\"(o caminho não deu para ler)\")", ""),
    ("V4 G1: o executor nunca pergunta se o Velopack roda", A,
     "            em_curso = self.windows.atualizador_do_velopack_rodando(self.raiz)",
     "            em_curso = False"),
    ("V5 G1: o executor pergunta também na reabertura com linha de comando", A,
     "        if para and ARG_CONFERIR_NOVA not in argumentos and versao.VERSAO == de",
     "        if para and versao.VERSAO == de"),
    ("V6 M1: a conferência antes de fechar sempre diz 'pode'", A,
     "            self.evento(self.conferencia_da_troca(self._achada))",
     "            self.evento(fases.TrocaConferida(True))"),
    ("V7 M1: a troca que falha depois de fechar não reabre", F,
     "[ReabrirOPrograma()] if estado.trocando_com_janela else []", "[]"),
    ("V8 M1: o sinal de vida não é dado", A,
     "                Path(argumentos[i + 1]).write_bytes(b\"\")", "                pass"),
    ("V9 M1: o reabrir dá como feito sem o sinal (olha só se lançou)", A,
     "            registrar(\"o programa foi aberto de novo\" if r.deu_certo",
     "            registrar(\"o programa foi aberto de novo\" if True"),
    ("V10 M2: pacote sem o motor-exigido.json conta como motor no lugar (anunciar)", A,
     "motor_da_nova=motor is not None and bool(self._motor_no_lugar(motor))",
     "motor_da_nova=motor is None or bool(self._motor_no_lugar(motor))"),
    ("V11 M2: pacote sem o motor-exigido.json pode trocar", A,
     "        if motor is None:\n            return fases.TrocaConferida(False, f\"o pacote da versão",
     "        if False:\n            return fases.TrocaConferida(False, f\"o pacote da versão"),
    ("V12 M2: a troca confere o motor do programa que roda, não o da versão que entra", A,
     "        if not self._motor_no_lugar(motor):\n            return fases.TrocaConferida(False, f\"o motor",
     "        if not self._motor_no_lugar(None):\n            return fases.TrocaConferida(False, f\"o motor"),
    ("V13 M2: o número do motor aceita texto e booleano", A,
     "        return int(numero) if isinstance(numero, int) and not isinstance(numero, bool) else None",
     "        return int(numero)"),
    ("V14 M4: a troca é pedida mesmo sem a anotação gravada", A,
     "        if not anotar_tentativa(de, para, volta):\n            return False,",
     "        if anotar_tentativa(de, para, volta) and False:\n            return False,"),
    ("V15 M4: o estado sempre 'aceita gravação'", A,
     "    return gravar_estado(ler_estado())", "    return True"),
    ("V16 M4: sem o estado gravando, procura mesmo assim", F,
     "        if e.no_lugar and not estado.estado_grava:", "        if False:"),
    ("V17 leve 3: a família sem a hora em que cada um nasceu", W,
     "                if filho in criados and pai in criados and criados[filho] < criados[pai]:\n                    continue",
     "                if False:\n                    continue"),
    ("V18 leve 2: a leitura de volta aceita linha a mais", W,
     "        if not veio_de_antes(nova) and not (e_a_nova(nova)",
     "        if False and not veio_de_antes(nova) and not (e_a_nova(nova)"),
    ("V19 D-839: a falha 'troca' volta a usar a frase (1)", A,
     "fases.FALHA_TROCA: FRASE_DA_FALHA_SEM_TROCA", "fases.FALHA_TROCA: FRASE_DA_FALHA"),
    ("V20 D-840: outra janela sem a frase", F,
     "                \"janela e o aviso de novo\"), PedirParaFecharAOutraJanela(), MostrarVersaoNova(estado.nova)]",
     "                \"janela e o aviso de novo\"), MostrarVersaoNova(estado.nova)]"),
    ("V21 D-841: outra janela sem o aviso de novo", F,
     "                \"janela e o aviso de novo\"), PedirParaFecharAOutraJanela(), MostrarVersaoNova(estado.nova)]",
     "                \"janela e o aviso de novo\"), PedirParaFecharAOutraJanela()]"),
    ("V22 D-840: 'não deu para saber' (sem a lista) também mostra a frase da outra janela", A,
     "            return fases.TrocaConferida(False, \"não deu para saber se há outra janela do programa aberta\")",
     "            return fases.TrocaConferida(False, \"não deu para saber se há outra janela do programa aberta\", "
     "outra_janela=True)"),
    ("V23 a falha aparece toda vez (sem o 'já vista')", A,
     "            if ef.nome in ler_vistos():\n                return", "            if False:\n                return"),
    ("V24 a ponte da tela: 'Reiniciar agora' manda 'Depois'", U,
     "            self.atual.evento(fases.Escolheu(bool(reiniciar)))", "            self.atual.evento(fases.Escolheu(False))"),
    ("V25 a ponte: a frase da outra janela não aparece", U,
     "            self._avisar(self.janela, atualizacao.TITULO_DA_VERSAO_NOVA, atualizacao.FRASE_DA_OUTRA_JANELA,",
     "            (lambda *a, **k: None)(self.janela, atualizacao.TITULO_DA_VERSAO_NOVA, atualizacao.FRASE_DA_OUTRA_JANELA,"),
    ("V26 a falha de teste não põe a versão em 'não tentar'", F,
     "        return (replace(estado, fase=Fase.VOLTANDO, nao_tentar=_com_mais(estado.nao_tentar, estado.nova)),",
     "        return (replace(estado, fase=Fase.VOLTANDO),"),
]


def main() -> int:
    so_contar = "--so-contar" in sys.argv
    sobreviveram = 0
    linhas = []
    for nome, arquivo, de, para in MUTACOES:
        caminho = RAIZ / arquivo
        original = caminho.read_bytes()
        texto = original.decode("utf-8")
        if "\r\n" in texto:
            de, para = de.replace("\n", "\r\n"), para.replace("\n", "\r\n")
        n = texto.count(de)
        if n != 1:
            linhas.append(f"[ERRO DA MUTAÇÃO] {nome}: o trecho aparece {n} vezes")
            print(linhas[-1], flush=True)
            continue
        if so_contar:
            continue
        try:
            caminho.write_bytes(texto.replace(de, para).encode("utf-8"))
            feito = subprocess.run([sys.executable, "-m", "pytest", *TESTES, "-q", "-p", "no:cacheprovider", "-x",
                                    f"--basetemp={RAIZ.parent / 'mut2-tmp'}"],
                                   cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                   # um teste dos testes à distância escreve no registro de verdade do ProgramData
                                   # (achado L1 deste relatório): aqui o ProgramData vai para uma pasta minha
                                   env={**__import__("os").environ, "PROGRAMDATA": str(RAIZ.parent / "mut2-pd")})
        finally:
            caminho.write_bytes(original)
        fim = (feito.stdout.strip().splitlines() or ["?"])[-1]
        falhou = [l for l in feito.stdout.splitlines() if l.startswith("FAILED")][:1]
        if feito.returncode == 0:
            sobreviveram += 1
            linhas.append(f"SOBREVIVEU  {nome} | {fim}")
        else:
            linhas.append(f"acusada     {nome} | {fim} | {falhou[0][:150] if falhou else ''}")
        print(linhas[-1], flush=True)
    linhas.append(f"{sobreviveram} de {len(MUTACOES)} sobreviveram")
    print(linhas[-1])
    if not so_contar:
        Path(__file__).with_name("mutacoes_qtq2-resultado.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
