"""Mutacoes de quem tenta quebrar (24/11/2026): cada protecao do atualizador novo que o script do implementador NAO
desliga, desligada uma por vez, rodando TODOS os arquivos de teste do atualizador (nao so o teste escolhido).

Roda numa COPIA do ramo (git archive), nunca no worktree: a copia e o primeiro argumento. Para cada mutacao: troca o
trecho (que tem de aparecer uma vez so), roda os arquivos de teste e devolve o arquivo como estava.
"SOBREVIVEU" = nenhum teste falhou com a protecao desligada (D-811 a D-813, D-827: protecao sem teste).
Uso: python mutacoes_qtq.py <copia do ramo>"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1])
A, W, F = "atualizacao.py", "core/windows.py", "core/fases_da_atualizacao.py"
TESTES = ["tests/test_atualizador_novo.py", "tests/test_fases_da_atualizacao.py",
          "tests/test_windows_preparo_do_computador.py", "tests/test_decisoes_atualizacao.py",
          "tests/test_decisoes_ajudante_da_atualizacao.py", "tests/test_decisoes_preparo_d749.py",
          "tests/test_velopack_de_verdade.py"]

MUTACOES = [
    ("Q1 motor: sem a conferencia do espaco livre", A, "            if tem < precisa:", "            if False:"),
    ("Q2 motor: o motor aberto nao e conferido antes do nome final", A,
     "        problemas = ocr_kraken.conferir_motor(chegando)\n", "        problemas = []\n"),
    ("Q3 motor: nunca poe o motor e diz que esta no lugar", A,
     "    if not ocr_kraken.conferir_motor(destino):\n        return True\n", "    if True:\n        return True\n"),
    ("Q4 motor: 'esta no lugar' sempre sim", A,
     "    return not ocr_kraken.conferir_motor(ocr_kraken.pasta_do_motor_instalado(raiz))", "    return True"),
    ("Q5 preparado?: so olha se a pasta existe (como o os.access)", A,
     "    caminho = Path(raiz) / ARQUIVO_DO_TESTE_DE_GRAVAR\n", "    return Path(raiz).is_dir()\n"),
    ("Q6 licenca da pasta: nao cobra a linha de Usuarios Modificar", W,
     "    if not any(li.sid == SID_USUARIOS and li.tipo == \"permite\" and not li.herdada",
     "    if False and not any(li.sid == SID_USUARIOS and li.tipo == \"permite\" and not li.herdada"),
    ("Q7 licenca da pasta: nao confere o arquivo de dentro (manifesto)", W, "    if manifesto.is_file():",
     "    if False:"),
    ("Q8 Visual C++: roda o instalador que uma conta comum pode trocar", W,
     "        if problemas:\n            return -1, \"o instalador pode ser trocado",
     "        if False:\n            return -1, \"o instalador pode ser trocado"),
    ("Q9 o aviso de falha: mostra de novo a cada abertura", A, "            if ef.nome in ler_vistos():",
     "            if False:"),
    ("Q10 o disco: a versao que falhou nao entra em 'nao tentar'", A,
     "    nao_tentar = sorted(set(estado.get(\"nao_tentar\") or []) | ({falhou} if falhou else set()))",
     "    nao_tentar = sorted(set(estado.get(\"nao_tentar\") or []))"),
    ("Q11 Inno: nao espera a chave sumir", W, "    while ler() is not None:", "    while False:"),
    ("Q12 Inno: aceita a pasta antiga que contem a pasta dos projetos", A,
     "    if dados and (pasta == Path(dados).resolve()", "    if False and (pasta == Path(dados).resolve()"),
    ("Q13 raiz da instalacao: aceita fora de Arquivos de Programas", W,
     "    if raiz == programas or not raiz.is_relative_to(programas):", "    if False:"),
    ("Q14 troca: o Windows nao deu a lista de processos e troca mesmo assim", A, "        if outras is None:",
     "        if False:"),
    ("Q15 processos: o que nao deixa ler o caminho nao conta", W, "        elif nome.lower() in nomes:",
     "        elif False:"),
    ("Q16 a linha de comando da reabertura vale mais que a anotacao", A,
     "                de, para, volta = argumentos[i + 1], argumentos[i + 2], False", "                pass"),
    ("Q17 a anotacao velha (de outra versao) nao e apagada", F,
     "                                                 f\"versão ({e.versao}): anotação velha, apagada\"),\n"
     "                                       AnotarOk(e.versao)]",
     "                                                 f\"versão ({e.versao}): anotação velha, apagada\")]"),
]


def main() -> int:
    sobreviveram = 0
    for nome, arquivo, de, para in MUTACOES:
        caminho = RAIZ / arquivo
        original = caminho.read_bytes()
        texto = original.decode("utf-8")
        if "\r\n" in texto:
            de, para = de.replace("\n", "\r\n"), para.replace("\n", "\r\n")
        if texto.count(de) != 1:
            print(f"[ERRO DA MUTACAO] {nome}: o trecho aparece {texto.count(de)} vezes", flush=True)
            continue
        try:
            caminho.write_bytes(texto.replace(de, para).encode("utf-8"))
            feito = subprocess.run([sys.executable, "-m", "pytest", *TESTES, "-q", "-p", "no:cacheprovider",
                                    f"--basetemp={RAIZ.parent / 'mut-tmp'}"],
                                   cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace")
        finally:
            caminho.write_bytes(original)
        falhas = [l for l in feito.stdout.splitlines() if l.startswith("FAILED") or l.startswith("ERROR")]
        ultima = (feito.stdout.strip().splitlines() or [""])[-1]
        if feito.returncode == 0:
            sobreviveram += 1
            print(f"[SOBREVIVEU - nenhum teste acusa] {nome} | {ultima}", flush=True)
        else:
            print(f"[acusada] {nome} | {ultima} | {falhas[:2]}", flush=True)
    print(f"\n{sobreviveram} de {len(MUTACOES)} mutacoes sobreviveram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
