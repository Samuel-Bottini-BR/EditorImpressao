"""A janela de prova da peça do Windows (plano da parte do Windows, versão 3, peça 10a; passo 1, sessão A).

O QUE É
    Uma janela pequena e visível, para a prova à vista na tela do Samuel (a gerente pilota; o Samuel clica "Sim" ou
    "Não" quando ela pedir). Uma linha por prova, cada uma com um botão: ao clicar, a prova roda **o código de
    verdade da peça** (`core/windows.py`, importado do programa, nunca copiado), e a janela mostra o que o Windows
    respondeu, lido de novo por fora (a tarefa existe? a pasta tem quais licenças? esta conta consegue gravar lá?).
    Tudo o que aparece vai também para um registro em texto (`--registro`, ou
    `relatorios/janela-de-prova/registro-<data>.txt`), que é a prova escrita da sessão.

    NÃO é parte do programa do Kaique (fica na raiz do projeto e o empacotador não a leva). Não fala com o Windows
    por conta própria: toda conversa passa pela peça (o porteiro barra o contrário).

AS PROVAS (sessão A do passo 1)
    1. Lançar solto: um processo lança um script solto e fecha; o script diz a hora em que rodou e se quem o lançou
       já tinha fechado. 0 perguntas do Windows.
    2. Pergunta 1, "Sim": a pasta segura de prova nasce (com as licenças que a janela lê e mostra), uma tarefa de
       prova é criada, roda como o sistema e diz quem é; esta conta lê a pasta e não consegue gravar; um segredo de
       prova com acento chega igual do outro lado (comparado pela soma, nunca mostrado); um texto com acento dentro
       do script chega igual.
    3. Pergunta 2, "Não": "você disse Não; nada mudou", conferido (a tarefa que seria criada não existe).
    4. Pergunta 3, com o navegador na frente, "Sim": a janela espera 10 segundos (para o Samuel clicar no navegador)
       e pede; mostra se a janela conseguiu vir para a frente; esse "Sim" apaga a tarefa e a pasta de prova, e a
       leitura diz "não existe" (a lista do que foi desfeito).
    5. Pedido para um programa que não existe: frase em português, sem caixa do Windows. 0 perguntas.
    6. A resposta do Windows com acento: manda a tarefa de prova rodar e mostra a resposta ("ÊXITO"). 0 perguntas.

COMO ABRIR
    `.venv\\Scripts\\python.exe janela_de_prova.py --programa "C:\\<pasta do programa montada>\\EditorImpressao.exe"`
    O programa indicado é o que a pergunta do Windows abre com a licença (montado deste mesmo commit, para ter a
    entrada do trabalho de administrador). Sem `--programa`, abre o próprio Python com o `main.py` (a pergunta
    mostra o Python, não o Editor: serve só para ensaiar).

Seguro mexer: os textos, a ordem das linhas. Arriscado: escrever aqui qualquer conversa com o Windows (tem de ir
para a peça); usar nomes de pasta ou de tarefa que não sejam os de prova (a pergunta 3 apaga o que a pergunta 1
criou, e só isso).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from core import windows  # noqa: E402

TAREFA_DE_PROVA = "EditorImpressao\\Prova da peca do Windows"
TAREFA_DO_NAO = "EditorImpressao\\Prova da peca do Windows (Nao)"
PASTA_DE_PROVA = windows.NOME_DA_PASTA_SEGURA_DE_PROVA
SCRIPT_DA_TAREFA = "tarefa-de-prova.ps1"
RODOU = "tarefa-rodou.txt"
SEGREDO_DE_PROVA = "Prova: senha com acento çÃõ€ e espaço"      # nunca a senha dos testes; nunca mostrado
TEXTO_COM_ACENTO = "Ação, ÊXITO, coração, € 10"
ESPERA_ANTES_DA_PERGUNTA_3_S = 10


def _agora() -> str:
    """A hora de agora, para cada linha do registro."""
    return datetime.now().strftime("%H:%M:%S")


# ---------------------------------------------------------------------------------------------------------------------
# O que cada prova faz (sem tela: recebe `dizer`, que escreve uma linha na janela e no registro)
# ---------------------------------------------------------------------------------------------------------------------

def _xml_de_prova() -> str:
    """O desenho da tarefa de prova: roda como o sistema o script da pasta segura de prova; a conta comum pode
    mandar rodar (o mesmo descritor do ajudante do programa, lido do lugar único dele)."""
    import atualizacao

    script = windows.pasta_segura(PASTA_DE_PROVA) / SCRIPT_DA_TAREFA
    return windows.xml_da_tarefa_do_sistema(str(windows.caminho_do_powershell()),
                                            windows.argumentos_do_powershell(script),
                                            "Editor de Impressão: tarefa de prova da peça do Windows (pode apagar).",
                                            atualizacao.QUEM_PODE_MANDAR_RODAR, limite="PT10M")


_SCRIPT_DA_TAREFA = (
    "$quem = [System.Security.Principal.WindowsIdentity]::GetCurrent()\n"
    "$texto = $quem.User.Value + '|' + $quem.Name + '|' + (Get-Date -Format 'HH:mm:ss')\n"
    f"[System.IO.File]::WriteAllText((Join-Path $PSScriptRoot '{RODOU}'), $texto, "
    "(New-Object System.Text.UTF8Encoding $false))\n"      # a tarefa roda o script direto, sem a cabeça da peça
)

_SCRIPT_DA_SOMA = (
    "$s = [Console]::In.ReadLine()\n"
    "$h = [System.Security.Cryptography.SHA256]::Create().ComputeHash($__utf8.GetBytes($s))\n"
    f"[Console]::Out.Write('{TEXTO_COM_ACENTO}' + '|' + (($h | ForEach-Object {{ $_.ToString('x2') }}) -join ''))\n"
)


def _dizer_resposta(dizer: Callable[[str], None], resposta: windows.Resposta) -> None:
    """Escreve o desfecho, o motivo e cada passo do relatório."""
    dizer(f"Resposta: {resposta.desfecho.upper()}" + (f" — {resposta.motivo}" if resposta.motivo else ""))
    if "janela_na_frente" in resposta.dados:
        dizer("A janela do programa estava na frente quando pediu: "
              + ("sim" if resposta.dados["janela_na_frente"] else "NÃO (a pergunta deve ter piscado na barra de "
                                                                   "tarefas)"))
    for passo in resposta.dados.get("passos", []):
        dizer(f"   passo \"{passo.get('descricao')}\": {passo.get('resultado')}"
              + (f" — {passo.get('motivo')}" if passo.get("motivo") else ""))
    if resposta.detalhe:
        dizer(f"   (técnico: {resposta.detalhe[:300]})")


def _ler_tarefa(dizer: Callable[[str], None], nome: str) -> windows.Tarefa:
    """Lê a tarefa pelo Windows e diz o que ele respondeu."""
    t = windows.ler_tarefa(nome)
    if t.existe is False:
        dizer(f"Lido no Windows: a tarefa \"{nome}\" não existe.")
    elif t.existe is None:
        dizer(f"Lido no Windows: não deu para saber se a tarefa existe ({t.motivo}).")
    elif not t.lida:
        dizer(f"Lido no Windows: a tarefa existe, mas não deu para ler ({t.motivo}).")
    else:
        quem = "o sistema" if t.usuario == windows.SID_SISTEMA else t.usuario
        dizer(f"Lido no Windows: a tarefa existe; roda como {quem}; comando: {t.comando} {t.argumentos}")
    return t


def _ler_pasta(dizer: Callable[[str], None]) -> windows.Resposta:
    """Lê a pasta segura de prova pelo Windows e diz as licenças que ela tem."""
    r = windows.conferir_pasta_segura(PASTA_DE_PROVA)
    if r.dados.get("existe") is False:
        dizer(f"Lido no Windows: a pasta segura de prova não existe ({r.dados.get('caminho')}).")
        return r
    dizer(f"Lido no Windows: a pasta segura de prova {'CONFERE' if r.deu_certo else 'NÃO CONFERE'}"
          + ("" if r.deu_certo else f" — {r.motivo}") + f" ({r.dados.get('caminho')}). Licenças:")
    for linha in r.dados.get("licencas", []):
        dizer(f"   {linha}")
    return r


def prova_lancar_solto(dizer: Callable[[str], None], _programa: list[str] | None, _janela: int | None) -> None:
    """Prova 1: um processo à parte lança um script solto e fecha; o script diz quando rodou e se o outro já tinha
    fechado."""
    resultado = windows.criar_pasta_de_troca() / "resultado-do-solto.txt"
    dizer("Abrindo um processo à parte que lança o script solto e fecha logo em seguida...")
    r = windows.rodar_e_esperar([sys.executable, str(Path(__file__).resolve()), "--lancador", str(resultado)],
                                limite_s=120, letras="utf-8")
    dizer(f"O processo que lançou terminou: {r.dados.get('saida') or r.motivo}")
    fim = time.monotonic() + 90
    while time.monotonic() < fim and not resultado.exists():
        time.sleep(0.3)
    if resultado.exists():
        time.sleep(0.3)
        dizer("O script solto escreveu: " + resultado.read_text(encoding="utf-8-sig"))
    else:
        dizer("FALHOU: o script solto não escreveu nada em 90 segundos.")
    windows.apagar_pasta_de_troca(resultado.parent)


def _lancador(resultado: str) -> int:
    """O processo à parte da prova 1: lança o script solto (pela peça) e sai na hora."""
    sys.stdout.reconfigure(encoding="utf-8")            # quem lê esta resposta lê em UTF-8
    pai = os.getpid()
    r = windows.lancar_powershell_solto(
        f"$pai = {pai}\n"
        "try { [System.Diagnostics.Process]::GetProcessById($pai).WaitForExit(60000) | Out-Null } catch { }\n"
        "$fechou = 'sim'\n"
        "try { [System.Diagnostics.Process]::GetProcessById($pai) | Out-Null; $fechou = 'NÃO' } catch { }\n"
        f"[System.IO.File]::WriteAllText({windows.aspas_do_powershell(resultado)}, ('o script solto rodou às ' + "
        "(Get-Date -Format 'HH:mm:ss') + '; quem o lançou (processo ' + $pai + ') já tinha fechado: ' + $fechou), "
        "$__utf8)\n")
    print(f"lançado: {r.desfecho} {r.motivo} (às {_agora()})")
    return 0 if r.deu_certo else 1


def prova_pergunta_1(dizer: Callable[[str], None], programa: list[str] | None, janela: int | None) -> None:
    """Prova 2 (pergunta 1, "Sim"): pasta segura de prova, tarefa de prova, segredo e texto com acento."""
    dizer("Vai aparecer a pergunta do Windows. A gerente pede: clique SIM.")
    passos = [windows.passo_criar_pasta_segura(PASTA_DE_PROVA),
              windows.passo_gravar_na_pasta_segura(PASTA_DE_PROVA, SCRIPT_DA_TAREFA, _SCRIPT_DA_TAREFA),
              windows.passo_criar_tarefa(TAREFA_DE_PROVA, _xml_de_prova()),
              windows.passo_script("conferir o segredo e o texto com acento", _SCRIPT_DA_SOMA, com_segredo=True,
                                   limite_s=120)]
    r = windows.pedir_licenca(passos, segredo=SEGREDO_DE_PROVA, janela=janela, programa=programa)
    _dizer_resposta(dizer, r)
    for passo in r.dados.get("passos", []):
        if passo.get("descricao") == "conferir o segredo e o texto com acento" and "|" in str(passo.get("saida")):
            texto, soma = str(passo["saida"]).split("|", 1)
            certa = hashlib.sha256(SEGREDO_DE_PROVA.encode("utf-8")).hexdigest()
            dizer("O segredo de prova com acento chegou do outro lado: "
                  + ("IGUAL (a soma confere; o segredo não é mostrado)" if soma == certa else "DIFERENTE"))
            dizer(f"O texto com acento dentro do script chegou: {texto!r} — "
                  + ("igual" if texto == TEXTO_COM_ACENTO else "DIFERENTE"))
    dizer("--- Lido de novo, por fora, depois da pergunta ---")
    pasta = _ler_pasta(dizer)
    _ler_tarefa(dizer, TAREFA_DE_PROVA)
    if pasta.dados.get("existe"):
        caminho = Path(pasta.dados["caminho"])
        try:
            dizer(f"Esta conta lê a pasta: sim ({len(list(caminho.iterdir()))} arquivo(s) lá dentro).")
        except OSError as erro:
            dizer(f"Esta conta lê a pasta: NÃO ({erro}).")
        tentativa = caminho / "tentativa-da-conta-comum.txt"
        try:
            tentativa.write_text("x", encoding="utf-8")
            dizer("Esta conta conseguiu GRAVAR na pasta segura: ERRADO (apagando o arquivo).")
            tentativa.unlink(missing_ok=True)
        except OSError:
            dizer("Esta conta tentou gravar na pasta segura e o Windows não deixou: certo.")
    t = windows.ler_tarefa(TAREFA_DE_PROVA)
    if t.existe:
        rodar = windows.rodar_tarefa(TAREFA_DE_PROVA)
        dizer(f"Esta conta mandou a tarefa rodar; o Windows respondeu: {rodar.dados.get('saida') or rodar.motivo}")
        rodou = windows.pasta_segura(PASTA_DE_PROVA) / RODOU
        fim = time.monotonic() + 60
        while time.monotonic() < fim and not rodou.exists():
            time.sleep(0.5)
        if rodou.exists():
            sid, nome, hora = rodou.read_text(encoding="utf-8-sig").split("|")
            dizer(f"A tarefa rodou às {hora} como {nome} ({sid})"
                  + (": é o sistema, certo." if sid == windows.SID_SISTEMA else ": NÃO é o sistema."))
        else:
            dizer("A tarefa não escreveu que rodou em 60 segundos.")


def prova_pergunta_2(dizer: Callable[[str], None], programa: list[str] | None, janela: int | None) -> None:
    """Prova 3 (pergunta 2, "Não"): a resposta é "disse Não" e nada mudou (a tarefa que seria criada não existe)."""
    dizer("Vai aparecer a pergunta do Windows. A gerente pede: clique NÃO.")
    r = windows.pedir_licenca([windows.passo_criar_tarefa(TAREFA_DO_NAO, _xml_de_prova())], janela=janela,
                              programa=programa)
    _dizer_resposta(dizer, r)
    dizer("--- Lido de novo, por fora ---")
    t = _ler_tarefa(dizer, TAREFA_DO_NAO)
    if r.desfecho == windows.DISSE_NAO:
        dizer("Nada mudou: " + ("conferido (a tarefa não existe)." if t.existe is False else "NÃO CONFERE."))


def prova_pergunta_3(dizer: Callable[[str], None], programa: list[str] | None, janela: int | None) -> None:
    """Prova 4 (pergunta 3, com o navegador na frente, "Sim"): apaga a tarefa e a pasta de prova e confere."""
    for falta in range(ESPERA_ANTES_DA_PERGUNTA_3_S, 0, -1):
        dizer(f"Clique agora no navegador (ou em outra janela). A pergunta vem em {falta} s...")
        time.sleep(1)
    dizer("Pedindo agora. A gerente pede: clique SIM (na pergunta, ou no escudo piscando na barra de tarefas).")
    r = windows.pedir_licenca([windows.passo_apagar_tarefa(TAREFA_DE_PROVA),
                               windows.passo_apagar_tarefa(TAREFA_DO_NAO),
                               windows.passo_apagar_pasta_segura(PASTA_DE_PROVA)], janela=janela, programa=programa)
    _dizer_resposta(dizer, r)
    dizer("--- O que foi desfeito, lido de novo por fora ---")
    _ler_tarefa(dizer, TAREFA_DE_PROVA)
    _ler_tarefa(dizer, TAREFA_DO_NAO)
    _ler_pasta(dizer)


def prova_programa_que_nao_existe(dizer: Callable[[str], None], _programa: list[str] | None,
                                  janela: int | None) -> None:
    """Prova 5: pedido para um programa que não existe: frase em português, nenhuma caixa do Windows."""
    r = windows.pedir_licenca([windows.passo_script("nada", "")], janela=janela,
                              programa=["C:\\Esta pasta nao existe\\EditorImpressao.exe"])
    _dizer_resposta(dizer, r)


def prova_resposta_com_acento(dizer: Callable[[str], None], _programa: list[str] | None, _janela: int | None) -> None:
    """Prova 6: manda a tarefa de prova rodar (sem licença) e mostra a resposta do Windows, com acento."""
    r = windows.rodar_tarefa(TAREFA_DE_PROVA)
    dizer(f"O Windows respondeu ({r.desfecho}): {r.dados.get('saida') or r.motivo}")


PROVAS: list[tuple[str, str, Callable]] = [
    ("1. Lançar solto", "0 perguntas do Windows", prova_lancar_solto),
    ("2. Pergunta 1: clique Sim", "1 pergunta do Windows", prova_pergunta_1),
    ("3. Pergunta 2: clique Não", "1 pergunta do Windows", prova_pergunta_2),
    ("4. Pergunta 3: navegador na frente, clique Sim", "1 pergunta do Windows; apaga o que a 1 criou",
     prova_pergunta_3),
    ("5. Programa que não existe", "0 perguntas do Windows", prova_programa_que_nao_existe),
    ("6. Resposta do Windows com acento", "0 perguntas; depois da pergunta 1", prova_resposta_com_acento),
]


# ---------------------------------------------------------------------------------------------------------------------
# A janela
# ---------------------------------------------------------------------------------------------------------------------

def montar_janela(programa: list[str] | None, registro: Path):
    """Monta a janela de prova (PySide6). Cada botão roda a sua prova num fio à parte: a janela nunca para."""
    from PySide6.QtCore import QThread, Signal
    from PySide6.QtWidgets import (QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget)

    class Trabalho(QThread):
        """Roda uma prova fora do fio da tela; cada linha dita vira um sinal para a janela."""

        linha = Signal(str)

        def __init__(self, funcao: Callable, janela: int | None):
            """Guarda a prova e a janela dona da pergunta."""
            super().__init__()
            self.funcao, self.janela = funcao, janela

        def run(self) -> None:
            """Roda a prova; qualquer erro vira uma linha (nunca derruba a janela)."""
            try:
                self.funcao(self.linha.emit, programa, self.janela)
            except Exception as erro:  # noqa: BLE001
                self.linha.emit(f"ERRO INESPERADO NA PROVA: {erro!r}")

    class Janela(QWidget):
        """A janela pequena: o programa usado, uma linha por prova e o que o Windows respondeu."""

        def __init__(self) -> None:
            """Monta os textos de cima, os botões e a área de respostas."""
            super().__init__()
            self.setWindowTitle("Janela de prova — peça do Windows")
            self.resize(900, 640)
            self.trabalhos: list[Trabalho] = []
            caixa = QVBoxLayout(self)
            usado = programa or windows.programa_deste_processo()
            caixa.addWidget(QLabel(f"Programa que a pergunta abre: {usado[0]}"
                                   + ("" if Path(usado[0]).is_file() else "  (NÃO EXISTE)")))
            caixa.addWidget(QLabel(f"Nome do arquivo (o que a pergunta deve mostrar, pela leitura): "
                                   f"{Path(usado[0]).name}"))
            caixa.addWidget(QLabel(f"Esta conta tem a licença de administrador agora: "
                                   f"{'sim' if windows.tem_licenca_de_administrador() else 'não'}   ·   "
                                   f"Registro: {registro}"))
            self.botoes: list[QPushButton] = []
            for titulo, perguntas, funcao in PROVAS:
                linha = QHBoxLayout()
                botao = QPushButton(titulo)
                botao.setMinimumWidth(380)
                botao.clicked.connect(lambda _=False, f=funcao, t=titulo: self.rodar(t, f))
                linha.addWidget(botao)
                linha.addWidget(QLabel(perguntas))
                linha.addStretch(1)
                caixa.addLayout(linha)
                self.botoes.append(botao)
            self.respostas = QPlainTextEdit()
            self.respostas.setReadOnly(True)
            caixa.addWidget(self.respostas, 1)

        def dizer(self, texto: str) -> None:
            """Uma linha na janela e no registro, com a hora."""
            linha = f"{_agora()}  {texto}"
            self.respostas.appendPlainText(linha)
            try:
                with registro.open("a", encoding="utf-8") as arquivo:
                    arquivo.write(linha + "\n")
            except OSError:
                pass

        def rodar(self, titulo: str, funcao: Callable) -> None:
            """Roda uma prova num fio à parte, com os botões desligados até ela acabar."""
            for b in self.botoes:
                b.setEnabled(False)
            self.dizer(f"===== {titulo} =====")
            trabalho = Trabalho(funcao, int(self.winId()))
            trabalho.linha.connect(self.dizer)
            trabalho.finished.connect(self.acabou)
            self.trabalhos.append(trabalho)
            trabalho.start()

        def acabou(self) -> None:
            """A prova acabou: os botões voltam."""
            self.dizer("(fim)")
            for b in self.botoes:
                b.setEnabled(True)

    return Janela()


def principal(argumentos: list[str]) -> int:
    """Abre a janela de prova (ou, com `--lancador`, faz o papel do processo à parte da prova 1)."""
    leitor = argparse.ArgumentParser(description="Janela de prova da peça do Windows")
    leitor.add_argument("--programa", help="o EditorImpressao.exe montado que a pergunta abre com a licença")
    leitor.add_argument("--registro", help="arquivo onde cada linha da janela fica escrita")
    leitor.add_argument("--lancador", help=argparse.SUPPRESS)
    args = leitor.parse_args(argumentos)
    if args.lancador:
        return _lancador(args.lancador)
    registro = Path(args.registro) if args.registro else (
        RAIZ / "relatorios" / "janela-de-prova" / f"registro-{datetime.now():%Y-%m-%d-%H%M%S}.txt")
    registro.parent.mkdir(parents=True, exist_ok=True)
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv[:1])
    janela = montar_janela([args.programa] if args.programa else None, registro)
    janela.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(principal(sys.argv[1:]))
