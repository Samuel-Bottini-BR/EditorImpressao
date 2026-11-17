"""O aviso da versao nova e o aviso da atualizacao que falhou, com o programa aberto.

Etapa 3 da frente do notebook do Kaique (16/11/2026). Decisoes do Samuel:
- D-715: "ele dá um aviso se o programa estiver aberto, um aviso para salvar o
  trabalho atual e reinicializar o programa";
- D-720: "Sim" - o aviso tem "Reiniciar agora" e "Depois";
- D-734 (17/11/2026, substitui o "quando o computador ligar" da D-720): com
  "Depois", a versao nova entra na proxima vez que o Kaique abrir o programa,
  com uma espera curta antes da janela (atualizacao.trocar_antes_de_abrir);
  fechar o programa nao troca nada;
- D-732 (17/11/2026): a versao nova e procurada quando o programa abre:
  ligar_na_janela chama o ajudante (atualizacao.procurar_ao_abrir);
- D-736 (17/11/2026): na conta dos testes a distancia nada disso roda (nem a
  procura nem o aviso); so a marca de "programa aberto", para o ajudante nao
  trocar a versao no meio de um teste;
- D-719: na tela, "A atualização não deu certo. O programa voltou para a
  versão anterior e continua funcionando. Avise o Samuel." (uma vez por falha).

O que decide O QUE mostrar e atualizacao.o_que_avisar (a mesma conta que a
tarefa do Windows usa, atualizacao.situacao); aqui so se mostra. Os textos
estao em atualizacao.py (um lugar so). As caixas sao as de ui/perguntas.py
(botoes escritos por nos, em portugues).

Como liga: main.py chama ligar_na_janela(janela) uma vez, depois de abrir a
janela. Pelo codigo (.venv) e nos testes nao faz nada: so o programa
instalado pelo Velopack tem atualizacao.

"Reiniciar agora": fecha a janela pelo caminho de sempre (closeEvent, que
GRAVA o trabalho e para as threads) e so depois pede a troca e a reabertura
(atualizacao.aplicar_agora_e_reabrir -> trocar_e_reabrir: quem troca e o
ajudante, sem pergunta do Windows, D-733). Se a janela nao fechou, nada e
trocado. "Depois": nada muda agora; o aviso nao volta nesta abertura do
programa; a versao entra na proxima abertura (D-734).

Seguro mudar: INTERVALO_MS. Arriscado: fechar a janela por outro caminho que
nao o close() (o trabalho deixaria de ser gravado antes da troca).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QMessageBox, QWidget

import atualizacao
from ui import perguntas

# De quanto em quanto tempo a janela olha se chegou versao nova (a tarefa do
# Windows baixa por tras; aqui so se le um arquivo pequeno).
INTERVALO_MS = 5 * 60 * 1000
# A primeira olhada, logo depois de abrir (mostra a falha da ultima vez).
PRIMEIRA_OLHADA_MS = 4000


def _arquivo_dos_vistos() -> Path:
    """As falhas ja mostradas NESTA conta do Windows (para mostrar uma vez so)."""
    from historico import pasta_de_dados

    return pasta_de_dados() / "atualizacao-avisos-vistos.json"


def ler_vistos() -> set[str]:
    try:
        return set(json.loads(_arquivo_dos_vistos().read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):
        return set()


def gravar_visto(identificador: str) -> None:
    try:
        vistos = ler_vistos() | {identificador}
        _arquivo_dos_vistos().write_text(json.dumps(sorted(vistos)), encoding="utf-8")
    except OSError:
        pass


class VigiaDaAtualizacao(QObject):
    """Olha, de tempos em tempos, se ha aviso para mostrar e mostra.

    Tudo o que fala com o mundo de fora entra pelos argumentos (os testes
    trocam): ler_estado, versao_atual, perguntar, avisar, aplicar.
    """

    def __init__(self, janela: QWidget,
                 ler_estado: Callable[[], dict] = atualizacao.ler_estado,
                 versao_atual: Callable[[], str] = atualizacao.versao_que_roda,
                 perguntar: Callable[..., bool] = perguntas.perguntar,
                 avisar: Callable[..., None] = perguntas.avisar,
                 aplicar: Callable[[], bool] = atualizacao.aplicar_agora_e_reabrir):
        super().__init__(janela)
        self.janela = janela
        self._ler_estado = ler_estado
        self._versao_atual = versao_atual
        self._perguntar = perguntar
        self._avisar = avisar
        self._aplicar = aplicar
        self._depois: set[str] = set()   # versoes em que ele ja disse "Depois" nesta abertura
        self._mostrando = False
        self.relogio = QTimer(self)
        self.relogio.setInterval(INTERVALO_MS)
        self.relogio.timeout.connect(self.olhar)

    def comecar(self) -> None:
        self.relogio.start()
        QTimer.singleShot(PRIMEIRA_OLHADA_MS, self.olhar)

    def olhar(self) -> None:
        """Uma olhada: decide pelo atualizacao.o_que_avisar e mostra, se for o caso."""
        if self._mostrando:
            return
        try:
            aviso = atualizacao.o_que_avisar(self._ler_estado(), self._versao_atual(), ler_vistos())
        except Exception as erro:  # noqa: BLE001 - o aviso nunca derruba a janela
            atualizacao.registrar(f"aviso da atualização: {type(erro).__name__}: {erro}")
            return
        if aviso is None:
            return
        o_que, detalhe = aviso
        self._mostrando = True
        try:
            if o_que == "falhou":
                gravar_visto(detalhe)
                self._avisar(self.janela, atualizacao.TITULO_DA_FALHA, atualizacao.FRASE_DA_FALHA,
                             icone=QMessageBox.Information)
            elif o_que == "versao-nova" and detalhe not in self._depois:
                self._perguntar_reiniciar(detalhe)
        finally:
            self._mostrando = False

    def _perguntar_reiniciar(self, versao_nova: str) -> None:
        """D-715/D-720: "Reiniciar agora" ou "Depois" (o Enter fica no "Depois")."""
        reiniciar = self._perguntar(self.janela, atualizacao.TITULO_DA_VERSAO_NOVA,
                                    atualizacao.FRASE_DA_VERSAO_NOVA,
                                    sim=atualizacao.BOTAO_REINICIAR, nao=atualizacao.BOTAO_DEPOIS)
        if not reiniciar:
            self._depois.add(versao_nova)
            atualizacao.registrar(f"versão {versao_nova} pronta; o Kaique escolheu \"Depois\"")
            return
        # Fecha pelo caminho de sempre: o closeEvent grava o trabalho. Se a
        # janela recusou fechar, nada e trocado (o trocar_e_reabrir espera
        # este processo sair e trocaria com o programa ainda aberto).
        self.relogio.stop()
        if self.janela.close() is False:
            atualizacao.registrar("\"Reiniciar agora\": a janela não fechou; nada foi trocado")
            self.relogio.start()
            return
        if not self._aplicar():
            # Nada foi trocado: o programa fechou gravado; abre-se de novo a mao,
            # e a versao nova entra na proxima abertura (como no "Depois", D-734).
            atualizacao.registrar("\"Reiniciar agora\": a troca não começou; fica para a próxima abertura")


def ligar_na_janela(janela: QWidget, instalado: Callable[[], bool] = atualizacao.instalado_pelo_velopack,
                    conta_de_testes: Callable[[], bool] | None = None,
                    procurar: Callable[[], bool] | None = None) -> VigiaDaAtualizacao | None:
    """main.py chama uma vez, depois de abrir a janela. Pelo codigo, nao faz nada.

    No programa instalado: marca "programa aberto", manda o ajudante procurar
    a versao nova (D-732) e liga o vigia do aviso. Na conta dos testes a
    distancia (D-736): so a marca. `conta_de_testes` e `procurar` vem como
    parametro so para os testes (o padrao e o de atualizacao.py).
    """
    if not instalado():
        return None
    atualizacao.marcar_programa_aberto()
    if (conta_de_testes or atualizacao.e_a_conta_de_testes)():
        return None
    (procurar or atualizacao.procurar_ao_abrir)()
    vigia = VigiaDaAtualizacao(janela)
    vigia.comecar()
    janela._vigia_da_atualizacao = vigia  # segura o objeto enquanto a janela vive
    return vigia
