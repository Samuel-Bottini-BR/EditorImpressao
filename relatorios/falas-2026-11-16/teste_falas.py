"""Teste do programinha das falas (C:\\Users\\fotog\\.claude\\scripts\\falas_da_conversa.py), 16/11/2026.

Defeito que este teste pega (achado da gerente em 16/11, e o de 14/11 no handoff, PARTE -36):
as falas que o Samuel manda enquanto o Claude trabalha não saíam (o texto fica no anexo
"queued_command", na linha "remove"/"absorbed_mid_turn" e na cópia do pedido à API, não na linha
"enqueue"), e os relatórios de agentes saíam como "SAMUEL (no meio do trabalho)".

Monta uma conversa de mentira com uma linha de cada jeito de gravar e confere a saída do script.
Uso (de qualquer pasta):
    python -I teste_falas.py                       testa o script consertado
    python -I teste_falas.py --script <arquivo>    testa outro (ex.: a cópia antiga, que deve falhar)
Sai com código 0 se tudo passou e 1 se alguma conferência falhou. Não lê nem grava conversa de verdade:
o arquivo de mentira vai para uma pasta temporária e é apagado no fim.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

SCRIPT = os.path.join(os.path.expanduser("~"), ".claude", "scripts", "falas_da_conversa.py")
MARCA = "The user sent a new message while you were working:\n"
FIM = ("\n\nThis is how Claude Code surfaces messages the user sends mid-turn — within the running turn, "
       "often alongside the next tool result, rather than as a separate conversation turn.")
IMG = {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "AAAA"}}


def ts(m):
    return f"2026-11-16T10:{m:02d}:00.000Z"


def humano(m, conteudo, **extra):
    d = {"type": "user", "isSidechain": False, "timestamp": ts(m), "origin": {"kind": "human"},
         "turnOrigin": "human", "message": {"role": "user", "content": conteudo}}
    d.update(extra)
    return d


def anexo(m, texto, uuid, origem="human", imagens=0):
    prompt = [{"type": "text", "text": texto}] + [IMG] * imagens
    return {"type": "attachment", "isSidechain": False, "timestamp": ts(m),
            "attachment": {"type": "queued_command", "prompt": prompt, "source_uuid": uuid,
                           "commandMode": "prompt", "origin": {"kind": origem}, "humanTurn": origem == "human"},
            "rendered": [{"content": [{"type": "text", "text": "<system-reminder>\n" + MARCA + texto + FIM}]}]}


def remove(m, texto, uuid):
    return {"type": "queue-operation", "operation": "remove", "timestamp": ts(m), "content": texto,
            "reason": "absorbed_mid_turn", "commandUuid": uuid}


def enqueue(m, texto=None):
    d = {"type": "queue-operation", "operation": "enqueue", "timestamp": ts(m)}
    if texto is not None:
        d["content"] = texto
    return d


def blob(texto):
    return {"type": "api-request-blob", "hash": "x",
            "message": {"role": "user", "content": [
                {"tool_use_id": "t1", "type": "tool_result", "content": "ok"},
                {"type": "text", "text": MARCA + texto + FIM}]}}


def claude(m, texto):
    return {"type": "assistant", "isSidechain": False, "timestamp": ts(m),
            "message": {"role": "assistant", "content": [{"type": "text", "text": texto}]}}


AGENTE = '<agent-message from="a123">\n[Subagent hand-back] relatorio do agente que nao e fala'
TAREFA = "<task-notification>\n<task-id>b1</task-id>\n<status>completed</status>\n</task-notification>"

LINHAS = [
    humano(0, "fala normal um"),
    humano(1, [{"type": "text", "text": "<browser_instruction>[Browser disconnected]</browser_instruction>"},
               {"type": "text", "text": "1"}]),
    humano(2, [{"type": "text", "text": "olha o print"}, IMG]),
    claude(3, "resposta do claude"),
    # fala do meio do trabalho, jeito novo: enqueue vazio + anexo (com print) + remove + cópia da API
    enqueue(4),
    anexo(4, "fala do meio A", "U1", imagens=1),
    remove(4, "fala do meio A", "U1"),
    blob("fala do meio A"),
    # só a linha remove (sem anexo)
    remove(5, "fala do meio B", "U2"),
    # só a cópia da API (sem hora: vale a da linha anterior, 10:05)
    blob("fala do meio C"),
    # a cópia da API juntando duas falas já conhecidas num bloco só (como "e o 12 também\n3 agentes")
    blob("fala do meio A\nfala do meio B"),
    # e juntando uma conhecida com uma que só existe ali: sai só a nova, inteira
    blob("fala do meio B\nassim sim, fala nova G"),
    # enqueue antigo (com texto) que virou mensagem normal
    enqueue(6, "fala antiga D"),
    humano(6, "fala antiga D"),
    # duas falas da fila juntadas numa mensagem normal
    enqueue(7, "parte um"),
    enqueue(7, "parte dois"),
    humano(7, "parte um\nparte dois"),
    # enqueue antigo que nunca virou mensagem normal
    enqueue(8, "fala antiga E"),
    # relatório de agente pela fila e como mensagem
    enqueue(9, AGENTE),
    anexo(9, AGENTE, "U9", origem="peer"),
    remove(9, AGENTE, "U9"),
    {"type": "user", "isMeta": True, "timestamp": ts(9), "origin": {"kind": "peer"},
     "message": {"role": "user", "content": "Another Claude session sent a message:\n" + AGENTE}},
    # aviso de tarefa pela fila e como mensagem
    enqueue(10, TAREFA),
    remove(10, TAREFA, "U10"),
    {"type": "user", "timestamp": ts(10), "origin": {"kind": "task-notification"},
     "message": {"role": "user", "content": TAREFA}},
    # resumo de conversa, interrupção e comando
    {"type": "user", "timestamp": ts(11), "turnOrigin": "human",
     "message": {"role": "user", "content": "This session is being continued from a previous conversation."}},
    {"type": "user", "timestamp": ts(11), "message": {"role": "user", "content": "[Request interrupted by user]"}},
    humano(11, "<command-message>checkpoint</command-message>\n<command-name>/checkpoint</command-name>"),
    # fala do meio do trabalho numa mensagem user com tool_result (sem anexo)
    {"type": "user", "timestamp": ts(12), "message": {"role": "user", "content": [
        {"tool_use_id": "t2", "type": "tool_result", "content": "saida"},
        {"type": "text", "text": MARCA + "fala do meio F" + FIM}]}},
    # a mesma palavra mandada duas vezes no meio do trabalho, com ids diferentes
    anexo(13, "sim", "U3"), remove(13, "sim", "U3"),
    anexo(14, "sim", "U4"), remove(14, "sim", "U4"),
]


def rodar(script, arquivo, *opcoes):
    r = subprocess.run([sys.executable, "-I", script, "--conversa", arquivo, *opcoes],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return "ERRO: " + r.stderr
    return r.stdout


def linhas_samuel(saida):
    return [l for l in saida.splitlines() if l.startswith("[") and "] SAMUEL" in l]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default=SCRIPT)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    pasta = tempfile.mkdtemp(prefix="teste_falas_")
    arquivo = os.path.join(pasta, "conversa.jsonl")
    with open(arquivo, "w", encoding="utf-8") as f:
        for d in LINHAS:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    try:
        saida = rodar(a.script, arquivo)
        com = rodar(a.script, arquivo, "--com-respostas")
        desde = rodar(a.script, arquivo, "--desde", "2026-11-16T10:05")
    finally:
        os.remove(arquivo)
        os.rmdir(pasta)
    s = linhas_samuel(saida)
    esperadas = [
        "[2026-11-16T10:00] SAMUEL: fala normal um",
        "[2026-11-16T10:01] SAMUEL: 1",
        "[2026-11-16T10:02] SAMUEL [+1 print(s)]: olha o print",
        "[2026-11-16T10:04] SAMUEL (no meio do trabalho) [+1 print(s)]: fala do meio A",
        "[2026-11-16T10:05] SAMUEL (no meio do trabalho): fala do meio B",
        "[2026-11-16T10:05] SAMUEL (no meio do trabalho): fala do meio C",
        "[2026-11-16T10:05] SAMUEL (no meio do trabalho): assim sim, fala nova G",
        "[2026-11-16T10:06] SAMUEL: fala antiga D",
        "[2026-11-16T10:07] SAMUEL: parte um",
        "[2026-11-16T10:08] SAMUEL (no meio do trabalho): fala antiga E",
        "[2026-11-16T10:12] SAMUEL (no meio do trabalho): fala do meio F",
        "[2026-11-16T10:13] SAMUEL (no meio do trabalho): sim",
        "[2026-11-16T10:14] SAMUEL (no meio do trabalho): sim",
    ]
    conferencias = [
        ("a saida lista exatamente as falas esperadas, na ordem, sem repetir", s == esperadas),
        ("fala do meio do trabalho (anexo + remove + copia da API) sai uma vez so, com o print",
         s.count(esperadas[3]) == 1 and sum("fala do meio A" in l for l in s) == 1),
        ("fala so na linha remove sai", esperadas[4] in s),
        ("fala so na copia da API sai", esperadas[5] in s),
        ("copia da API que junta duas falas conhecidas nao repete; com uma nova, sai so a nova",
         sum("fala do meio B" in l for l in s) == 1 and esperadas[6] in s),
        ("fala numa mensagem com resultado de ferramenta sai", esperadas[10] in s),
        ("a mesma palavra mandada duas vezes sai duas vezes", s.count(esperadas[11]) == 1 and s.count(esperadas[12]) == 1),
        ("enqueue antigo que virou mensagem normal nao repete como 'meio do trabalho'",
         not any("(no meio do trabalho): fala antiga D" in l for l in s)),
        ("duas falas da fila juntadas numa mensagem nao repetem", not any("(no meio do trabalho): parte" in l for l in s)),
        ("relatorio de agente nunca sai como fala", "agent-message" not in saida and "relatorio do agente" not in saida),
        ("aviso de tarefa nunca sai como fala", "task-notification" not in saida),
        ("aviso do navegador nao sai junto da fala", "browser_instruction" not in saida),
        ("resumo de conversa, interrupcao e comando nao saem",
         "This session" not in saida and "Request interrupted" not in saida and "command-message" not in saida),
        ("sem --com-respostas, nada do Claude", "CLAUDE:" not in saida),
        ("com --com-respostas, a resposta do Claude sai", "[2026-11-16T10:03] CLAUDE: resposta do claude" in com),
        ("--desde corta o que veio antes",
         "fala normal um" not in desde and "fala do meio A" not in desde and "fala do meio B" in desde),
        ("cabecalho da conversa igual ao de antes", saida.startswith("# Conversa: ")),
    ]
    falhou = 0
    for nome, ok in conferencias:
        print(("PASSOU  " if ok else "FALHOU  ") + nome)
        falhou += not ok
    if falhou:
        print("\nSaida do script (linhas SAMUEL):")
        for l in s:
            print("   ", l)
    print(f"\n{len(conferencias) - falhou} de {len(conferencias)} conferencias passaram ({a.script}).")
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
