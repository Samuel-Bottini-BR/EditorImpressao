"""A tela da atualização: o aviso da versão nova, a pergunta ao fechar e o aviso da atualização que falhou.

Atualizador novo (23/11/2026, D-830). Esta parte SÓ transforma o clique em evento e o efeito em caixa; quem decide o
que mostrar e o que vem depois é a regra (`core/fases_da_atualizacao.py`), rodada pelo executor (`atualizacao.py`,
`Atualizacao`). Nenhuma conta aqui.

O que aparece (decisões do Samuel, palavras combinadas, textos em `atualizacao.py`, um lugar só):
- D-715/D-720: a versão nova chegou com o programa aberto: "Reiniciar agora" / "Depois" (o Enter fica no "Depois");
  a última frase do aviso é a da D-835: "Se escolher "Depois", você pode atualizar quando fechar o programa."
- D-769/D-794/D-831/D-835: com "Depois", ao fechar o programa: "Atualizar agora?" / "Quer atualizar o programa agora,
  ao fechar?" / "Sim" / "Não". Com "Sim" a janela some, o programa grava e sai, e o Velopack troca (com a janelinha
  dele, D-832); nada abre na tela depois. Com "Não", fecha sem trocar; o aviso volta na próxima abertura.
- D-719/D-778/D-839: uma falha, uma vez por falha nesta conta, com a frase do caso (`atualizacao.FRASES_DA_FALHA`;
  a troca que não aconteceu: "O programa continua na versão de antes e funcionando.").
- D-840: "Reiniciar agora" com outra janela do programa aberta: "Feche a outra janela do programa e clique de novo."
  (`atualizacao.FRASE_DA_OUTRA_JANELA`); nada fecha e a pergunta vem ao fechar.

COMO LIGA. main.py chama `ligar_na_janela(janela)` uma vez, depois de abrir a janela; e o fechar da janela principal
(`ui/janela_principal.py`, `closeEvent`) chama `ao_fechar(janela)` depois de gravar o trabalho e parar as tarefas.
Pelo código (.venv), no portátil e na conta dos testes à distância não há executor (`atualizacao.da_abertura()` é
None) e nada aparece.

O FIO. O executor manda os efeitos de qualquer fio (a procura e o download rodam por trás). A `PonteDaTela` os recebe
por um sinal do Qt: vindo de outro fio, o Qt o entrega no fio da tela; vindo do fio da tela (o fechar), na hora.

Seguro mexer: nada de texto aqui (os textos moram em atualizacao.py). Arriscado: fechar a janela por outro caminho que
não o `close()` no "Reiniciar agora" (o trabalho deixaria de ser gravado antes da troca); mandar o evento antes de a
caixa ter resposta; esconder a janela no "Não".
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox, QWidget

import atualizacao
from core import fases_da_atualizacao as fases
from ui import perguntas


class PonteDaTela(QObject):
    """Entre o executor da atualização e a janela: recebe os efeitos de tela e devolve o que a pessoa escolheu.

    `perguntar` e `avisar` vêm como parâmetro só para os testes (o padrão são as caixas de ui/perguntas.py, com os
    botões escritos por nós, em português)."""

    chegou = Signal(object)

    def __init__(self, janela: QWidget, atual: "atualizacao.Atualizacao",
                 perguntar: Callable[..., bool] = perguntas.perguntar,
                 avisar: Callable[..., None] = perguntas.avisar) -> None:
        super().__init__(janela)
        self.janela, self.atual = janela, atual
        self._perguntar, self._avisar = perguntar, avisar
        self.chegou.connect(self._mostrar)

    def receber(self, efeito) -> None:
        """O executor chama (de qualquer fio)."""
        self.chegou.emit(efeito)

    def _mostrar(self, ef) -> None:
        """No fio da tela: mostra a caixa do efeito e manda a resposta como evento."""
        if isinstance(ef, fases.MostrarVersaoNova):
            reiniciar = self._perguntar(self.janela, atualizacao.TITULO_DA_VERSAO_NOVA,
                                        atualizacao.FRASE_DA_VERSAO_NOVA,
                                        sim=atualizacao.BOTAO_REINICIAR, nao=atualizacao.BOTAO_DEPOIS)
            self.atual.evento(fases.Escolheu(bool(reiniciar)))
        elif isinstance(ef, fases.FecharJanela):
            # Fecha pelo caminho de sempre: o closeEvent grava o trabalho e para as tarefas.
            fechou = self.janela.close()
            self.atual.evento(fases.JanelaFechou(fechou is not False))
        elif isinstance(ef, fases.PerguntarAoFechar):
            sim = bool(self._perguntar(self.janela, atualizacao.TITULO_AO_FECHAR, atualizacao.FRASE_AO_FECHAR,
                                       sim=atualizacao.BOTAO_SIM_AO_FECHAR, nao=atualizacao.BOTAO_NAO_AO_FECHAR))
            if sim:
                self.janela.hide()        # a conferência do pacote leva uns segundos: a janela não fica parada na tela
            self.atual.evento(fases.RespondeuAoFechar(sim))
        elif isinstance(ef, fases.MostrarFalha):
            self._avisar(self.janela, atualizacao.TITULO_DA_FALHA,
                         atualizacao.FRASES_DA_FALHA.get(ef.tipo, atualizacao.FRASE_DA_FALHA),
                         icone=QMessageBox.Information)
        elif isinstance(ef, fases.PedirParaFecharAOutraJanela):
            # D-840: o "Reiniciar agora" não trocou porque há outra janela do programa aberta; esta continua aberta
            # (a regra já a deixou como no "Depois": a pergunta vem ao fechar).
            self._avisar(self.janela, atualizacao.TITULO_DA_VERSAO_NOVA, atualizacao.FRASE_DA_OUTRA_JANELA,
                         icone=QMessageBox.Information)

    def ao_fechar(self) -> None:
        """O Kaique fechou o programa (o trabalho já foi gravado)."""
        self.atual.evento(fases.Fechando())


def ligar_na_janela(janela: QWidget, atual: "atualizacao.Atualizacao | None" = None) -> PonteDaTela | None:
    """main.py chama uma vez, depois de abrir a janela. Sem executor (pelo código, portátil, conta de testes): nada.
    `atual` só muda nos testes (o padrão é o executor desta abertura)."""
    atual = atual if atual is not None else atualizacao.da_abertura()
    if atual is None:
        return None
    ponte = PonteDaTela(janela, atual)
    janela._ponte_da_atualizacao = ponte  # segura o objeto enquanto a janela vive
    atual.ligar_a_tela(ponte.receber)
    return ponte


def ao_fechar(janela: QWidget) -> None:
    """O fechar da janela principal chama, depois de gravar e antes de aceitar o fechar. Sem a ponte: nada. Nunca
    levanta (o fechar nunca pode quebrar)."""
    ponte = getattr(janela, "_ponte_da_atualizacao", None)
    if ponte is None:
        return
    try:
        ponte.ao_fechar()
    except Exception as erro:  # noqa: BLE001
        atualizacao.registrar(f"fechar o programa: {type(erro).__name__}: {erro}")
