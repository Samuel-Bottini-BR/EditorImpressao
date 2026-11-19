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
       e pede; mostra se a janela conseguiu vir para a frente; esse "Sim" apaga as tarefas e a pasta de prova e, se
       foi a prova que criou a pasta EditorImpressao do Agendador (anotado antes da pergunta 1), apaga-a também;
       vai até o fim mesmo que um passo falhe, e a leitura diz o que foi desfeito e o que ficou (D-722).
    5. (a) Pedido para um programa que não existe: a peça para antes do Windows, com a frase em português. (b) Pedido
       para um arquivo que existe e não é programa: chega ao Windows; frase em português, sem caixa. 0 perguntas.
    6. A resposta do Windows com acento: manda a tarefa de prova rodar e mostra a resposta ("ÊXITO"). 0 perguntas.

COMO ABRIR
    `.venv\\Scripts\\python.exe janela_de_prova.py --programa "C:\\<pasta do programa montada>\\EditorImpressao.exe"`
    O programa indicado é o que a pergunta do Windows abre com a licença (montado deste mesmo commit, para ter a
    entrada do trabalho de administrador). Sem `--programa`, abre o próprio Python com o `main.py` (a pergunta
    mostra o Python, não o Editor: serve só para ensaiar).

Os pedidos de cada prova saem de funções sem o Windows (`passos_da_pergunta_1` etc.), e um teste passa cada um pelas
regras da peça, para nenhum pedido errado chegar à sessão (achado 1 de quem tentou quebrar). Fechar a janela no meio
de uma prova não fecha: ela pede para esperar.

Seguro mexer: os textos, a ordem das linhas. Arriscado: escrever aqui qualquer conversa com o Windows (tem de ir
para a peça); usar nomes de pasta ou de tarefa que não sejam os de prova (a pergunta 3 apaga o que a pergunta 1
criou, e só isso).
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
# Sem parênteses: a peça só aceita letras, números, espaço, ponto, sublinhado e hífen (achado 1 de quem tentou quebrar:
# com "(Nao)" a peça recusava o pedido antes do Windows, e as perguntas 2 e 3 nunca apareciam).
TAREFA_DO_NAO = "EditorImpressao\\Prova da peca do Windows - Nao"
PASTA_DE_PROVA = windows.NOME_DA_PASTA_SEGURA_DE_PROVA
SCRIPT_DA_TAREFA = "tarefa-de-prova.ps1"
RODOU = "tarefa-rodou.txt"
SEGREDO_DE_PROVA = "Prova: senha com acento çÃõ€ e espaço"      # nunca a senha dos testes; nunca mostrado
TEXTO_COM_ACENTO = "Ação, ÊXITO, coração, € 10"
ESPERA_ANTES_DA_PERGUNTA_3_S = 10
# Como estava o Agendador antes da primeira pergunta (a pasta do programa existia?), para a pergunta 3 deixá-lo como
# estava (D-722). Gravado na primeira vez da pergunta 1 e nunca sobrescrito; apagado pela pergunta 3 quando ela desfaz.
ESTADO_DE_ANTES = RAIZ / "relatorios" / "janela-de-prova" / "agendador-antes-da-prova.json"


def _agora() -> str:
    """A hora de agora, para cada linha do registro."""
    return datetime.now().strftime("%H:%M:%S")


# ---------------------------------------------------------------------------------------------------------------------
# Os pedidos de cada prova (sem o Windows: os testes passam cada um pelas regras da peça)
# ---------------------------------------------------------------------------------------------------------------------

def _xml_de_prova() -> str:
    """O desenho da tarefa de prova: roda como o sistema o script da pasta segura de prova; a conta comum pode
    mandar rodar (o mesmo descritor do ajudante do programa, lido do lugar único dele)."""
    import atualizacao

    return windows.xml_da_tarefa_de_script(windows.pasta_segura(PASTA_DE_PROVA) / SCRIPT_DA_TAREFA,
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


def passos_da_pergunta_1() -> list:
    """Pergunta 1: a pasta segura de prova, o script da tarefa (o resultado da vez anterior apagado antes), a tarefa
    de prova e o script do segredo e do texto com acento."""
    return [windows.passo_criar_pasta_segura(PASTA_DE_PROVA),
            windows.passo_gravar_na_pasta_segura(PASTA_DE_PROVA, SCRIPT_DA_TAREFA, _SCRIPT_DA_TAREFA),
            windows.passo_gravar_na_pasta_segura(PASTA_DE_PROVA, RODOU, ""),
            windows.passo_criar_tarefa(TAREFA_DE_PROVA, _xml_de_prova()),
            windows.passo_script("conferir o segredo e o texto com acento", _SCRIPT_DA_SOMA, com_segredo=True,
                                 limite_s=120)]


def passos_da_pergunta_2() -> list:
    """Pergunta 2 (a que recebe "Não"): criaria uma segunda tarefa de prova."""
    return [windows.passo_criar_tarefa(TAREFA_DO_NAO, _xml_de_prova())]


def passos_da_pergunta_3(apagar_a_pasta_do_agendador: bool) -> list:
    """Pergunta 3 (o desfazer): as duas tarefas de prova, a pasta segura de prova e, se foi a prova que a criou, a
    pasta do programa no Agendador (só se ficar vazia)."""
    passos = [windows.passo_apagar_tarefa(TAREFA_DE_PROVA), windows.passo_apagar_tarefa(TAREFA_DO_NAO),
              windows.passo_apagar_pasta_segura(PASTA_DE_PROVA)]
    if apagar_a_pasta_do_agendador:
        passos.append(windows.passo_apagar_pasta_de_tarefas())
    return passos


def passos_da_prova_5() -> list:
    """Prova 5: um passo qualquer (o pedido não chega a fazer nada)."""
    return [windows.passo_script("nada", "")]


# ---------------------------------------------------------------------------------------------------------------------
# O que cada prova faz (sem tela: recebe `dizer`, que escreve uma linha na janela e no registro)
# ---------------------------------------------------------------------------------------------------------------------

def _dizer_resposta(dizer: Callable[[str], None], resposta: windows.Resposta) -> None:
    """Escreve o desfecho, o motivo, cada passo do relatório e o técnico inteiro (o registro é a prova escrita)."""
    dizer(f"Resposta: {resposta.desfecho.upper()}" + (f" — {resposta.motivo}" if resposta.motivo else ""))
    if "janela_na_frente" in resposta.dados:
        dizer("A janela do programa estava na frente quando pediu: "
              + ("sim" if resposta.dados["janela_na_frente"] else "NÃO (a pergunta deve ter piscado na barra de "
                                                                   "tarefas)"))
    for passo in resposta.dados.get("passos", []):
        dizer(f"   passo \"{passo.get('descricao')}\": {passo.get('resultado')}"
              + (f" — {passo.get('motivo')}" if passo.get("motivo") else ""))
        if passo.get("resultado") != windows.DEU_CERTO and passo.get("detalhe"):
            dizer(f"      (técnico do passo: {passo.get('detalhe')})")
    if resposta.detalhe:
        dizer(f"   (técnico: {resposta.detalhe})")


def _resposta_do_windows(r: windows.Resposta) -> str:
    """O que o Windows escreveu (a resposta ou o erro), ou o motivo."""
    return r.dados.get("saida") or r.dados.get("erros") or r.motivo


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
        dizer(f"Lido no Windows: a tarefa existe; roda como {quem}; comando: {t.comando} {t.argumentos}; "
              f"licença no Windows: {t.licenca}")
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


def _ler_pasta_do_agendador(dizer: Callable[[str], None]) -> bool | None:
    """Lê se a pasta do programa existe no Agendador e diz."""
    existe = windows.pasta_de_tarefas_existe()
    dizer("Lido no Windows: a pasta \\EditorImpressao do Agendador "
          + {True: "existe.", False: "não existe.", None: "não deu para saber se existe."}[existe])
    return existe


def prova_lancar_solto(dizer: Callable[[str], None], _programa: list[str] | None, _janela: int | None) -> None:
    """Prova 1: um processo à parte lança um script solto e fecha; o script diz quando rodou e se o outro já tinha
    fechado."""
    resultado = windows.criar_pasta_de_troca() / "resultado-do-solto.txt"
    dizer("Abrindo um processo à parte que lança o script solto e fecha logo em seguida...")
    r = windows.rodar_e_esperar([sys.executable, str(Path(__file__).resolve()), "--lancador", str(resultado)],
                                limite_s=120, letras="utf-8")
    dizer(f"O processo que lançou terminou: {_resposta_do_windows(r)}")
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


def _anotar_o_agendador_de_antes(dizer: Callable[[str], None]) -> None:
    """Antes da primeira pergunta 1: anota se a pasta do programa já existia no Agendador (uma vez só)."""
    if ESTADO_DE_ANTES.exists():
        dizer(f"Como estava o Agendador antes da prova: já anotado em {ESTADO_DE_ANTES.name}.")
        return
    existia = _ler_pasta_do_agendador(dizer)
    ESTADO_DE_ANTES.parent.mkdir(parents=True, exist_ok=True)
    ESTADO_DE_ANTES.write_text(json.dumps({"pasta_do_agendador_existia": existia, "em": _agora()}), encoding="utf-8")


def prova_pergunta_1(dizer: Callable[[str], None], programa: list[str] | None, janela: int | None) -> None:
    """Prova 2 (pergunta 1, "Sim"): pasta segura de prova, tarefa de prova, segredo e texto com acento."""
    _anotar_o_agendador_de_antes(dizer)
    dizer("Vai aparecer a pergunta do Windows. A gerente pede: clique SIM.")
    r = windows.pedir_licenca(passos_da_pergunta_1(), segredo=SEGREDO_DE_PROVA, janela=janela, programa=programa)
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
        rodou = windows.pasta_segura(PASTA_DE_PROVA) / RODOU
        marco = time.time()
        rodar = windows.rodar_tarefa(TAREFA_DE_PROVA)
        dizer(f"Esta conta mandou a tarefa rodar; o Windows respondeu: {_resposta_do_windows(rodar)}")
        # Só vale o resultado escrito DEPOIS de mandar rodar (achado 2 de quem tentou quebrar: um arquivo da vez
        # anterior enganava a prova). O passo com licença também o deixou vazio antes.
        fim = time.monotonic() + 60
        texto = ""
        while time.monotonic() < fim:
            if rodou.exists() and rodou.stat().st_mtime >= marco - 1:
                texto = rodou.read_text(encoding="utf-8-sig")
                if texto.count("|") == 2:
                    break
            time.sleep(0.5)
        if texto.count("|") == 2:
            sid, nome, hora = texto.split("|")
            dizer(f"A tarefa rodou às {hora} como {nome} ({sid})"
                  + (": é o sistema, certo." if sid == windows.SID_SISTEMA else ": NÃO é o sistema."))
        else:
            dizer("A tarefa não escreveu que rodou em 60 segundos (depois de mandar rodar).")


def prova_pergunta_2(dizer: Callable[[str], None], programa: list[str] | None, janela: int | None) -> None:
    """Prova 3 (pergunta 2, "Não"): a resposta é "disse Não" e nada mudou (a tarefa que seria criada não existe)."""
    dizer("Vai aparecer a pergunta do Windows. A gerente pede: clique NÃO.")
    r = windows.pedir_licenca(passos_da_pergunta_2(), janela=janela, programa=programa)
    _dizer_resposta(dizer, r)
    dizer("--- Lido de novo, por fora ---")
    t = _ler_tarefa(dizer, TAREFA_DO_NAO)
    if r.desfecho == windows.DISSE_NAO:
        dizer("Nada mudou: " + ("conferido (a tarefa não existe)." if t.existe is False else "NÃO CONFERE."))


def prova_pergunta_3(dizer: Callable[[str], None], programa: list[str] | None, janela: int | None) -> None:
    """Prova 4 (pergunta 3, com o navegador na frente, "Sim"): desfaz o que a pergunta 1 (e a 2, se recebeu "Sim")
    criou, indo até o fim mesmo que um passo falhe, e diz, lido de novo por fora, o que foi desfeito e o que ficou."""
    antes = json.loads(ESTADO_DE_ANTES.read_text(encoding="utf-8")) if ESTADO_DE_ANTES.exists() else {}
    existia = antes.get("pasta_do_agendador_existia")
    apagar_a_pasta = existia is False
    if existia is None:
        dizer("Não se sabe se a pasta \\EditorImpressao do Agendador existia antes da prova: ela NÃO será apagada.")
    for falta in range(ESPERA_ANTES_DA_PERGUNTA_3_S, 0, -1):
        dizer(f"Clique agora no navegador (ou em outra janela). A pergunta vem em {falta} s...")
        time.sleep(1)
    dizer("Pedindo agora. A gerente pede: clique SIM (na pergunta, ou no escudo piscando na barra de tarefas).")
    r = windows.pedir_licenca(passos_da_pergunta_3(apagar_a_pasta), janela=janela, programa=programa,
                              ate_o_fim=True)
    _dizer_resposta(dizer, r)
    dizer("--- O que foi desfeito, lido de novo por fora ---")
    _ler_tarefa(dizer, TAREFA_DE_PROVA)
    _ler_tarefa(dizer, TAREFA_DO_NAO)
    _ler_pasta(dizer)
    agora = _ler_pasta_do_agendador(dizer)
    if existia is False:
        dizer("A pasta \\EditorImpressao do Agendador não existia antes da prova: "
              + ("foi apagada, o Agendador ficou como estava." if agora is False else "ELA FICOU."))
    elif existia is True:
        dizer("A pasta \\EditorImpressao do Agendador já existia antes da prova: ficou, como estava.")
    if r.deu_certo and (agora is False or existia is True):
        ESTADO_DE_ANTES.unlink(missing_ok=True)


def pedido_para_programa_que_nao_existe(dizer: Callable[[str], None], janela: int | None) -> None:
    """Prova 5 (a): pedido para um programa que não existe: a peça para antes do Windows, com a frase em português."""
    dizer("(a) Programa que não existe:")
    _dizer_resposta(dizer, windows.pedir_licenca(passos_da_prova_5(), janela=janela,
                                                 programa=["C:\\Esta pasta nao existe\\EditorImpressao.exe"]))


def pedido_para_arquivo_que_nao_e_programa(dizer: Callable[[str], None], janela: int | None) -> None:
    """Prova 5 (b): pedido para um arquivo que existe e não é programa: CHEGA ao Windows, que não sabe pedir licença
    para ele; deve voltar a frase em português, sem caixa do Windows e sem pergunta. Só na sessão à vista (nunca nos
    testes automáticos: é o Windows de verdade)."""
    pasta = windows.criar_pasta_de_troca()
    texto = pasta / "nao-e-programa.txt"
    texto.write_text("isto não é um programa", encoding="utf-8")
    dizer("(b) Arquivo que existe e não é programa (vai ao Windows; não deve aparecer caixa nem pergunta):")
    _dizer_resposta(dizer, windows.pedir_licenca(passos_da_prova_5(), janela=janela, programa=[str(texto)]))
    windows.apagar_pasta_de_troca(pasta)


def prova_programa_que_nao_existe(dizer: Callable[[str], None], _programa: list[str] | None,
                                  janela: int | None) -> None:
    """Prova 5: as duas partes, (a) e (b)."""
    pedido_para_programa_que_nao_existe(dizer, janela)
    pedido_para_arquivo_que_nao_e_programa(dizer, janela)


def prova_resposta_com_acento(dizer: Callable[[str], None], _programa: list[str] | None, _janela: int | None) -> None:
    """Prova 6: manda a tarefa de prova rodar (sem licença) e mostra a resposta do Windows, com acento."""
    r = windows.rodar_tarefa(TAREFA_DE_PROVA)
    dizer(f"O Windows respondeu ({r.desfecho}): {_resposta_do_windows(r)}")


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

        def closeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
            """Não fecha no meio de uma prova (o registro ficaria pela metade; achado 17 de quem tentou quebrar)."""
            if any(t.isRunning() for t in self.trabalhos):
                self.dizer("Espere a prova acabar antes de fechar a janela (o registro ficaria pela metade).")
                evento.ignore()
                return
            evento.accept()

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
