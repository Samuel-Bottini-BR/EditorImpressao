"""Registro único de todo atalho de teclado do programa.

Existe para o menu, a lista de "Ajuda -> Lista de atalhos" e a tela de
Configurações lerem sempre do mesmo lugar - duas listas separadas divergem na
primeira mudança (mesma razão de `ui/barra_de_menu.py`).

Cada parte do programa que tem um atalho fixo (menu, ferramentas de marcar,
navegação, os modos do retângulo de corte) chama `registrar()` uma vez, ao
carregar. Depois disso, `tecla_atual()` é a fonte de verdade de qual tecla
aquela ação usa - nunca comparar contra a tecla padrão direto.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Atalho:
    chave: str
    nome: str
    padrao: str
    atual: str


_registro: dict[str, Atalho] = {}


def registrar(chave: str, nome: str, padrao: str) -> None:
    """Registra uma ação com a tecla padrão dela.

    Chamar de novo com a mesma chave não faz nada - o registro é feito uma
    vez, na primeira vez que aquele código carrega (import de módulo, ou
    construção da barra de menu). Sem essa guarda, recarregar uma tela
    apagaria a tecla que o Samuel já tinha escolhido.
    """
    if chave not in _registro:
        _registro[chave] = Atalho(chave, nome, padrao, padrao)


def registrado(chave: str) -> bool:
    return chave in _registro


def tecla_atual(chave: str) -> str:
    atalho = _registro.get(chave)
    return atalho.atual if atalho else ""


def tecla_padrao(chave: str) -> str:
    atalho = _registro.get(chave)
    return atalho.padrao if atalho else ""


def todas() -> list[Atalho]:
    """Na ordem em que foram registradas - a ordem em que os menus nascem."""
    return list(_registro.values())


def conflito(chave: str, tecla_nova: str) -> str | None:
    """O nome da OUTRA ação que já usa essa tecla, se houver. Vazio nunca conflita."""
    if not tecla_nova:
        return None
    for outra in _registro.values():
        if outra.chave != chave and outra.atual == tecla_nova:
            return outra.nome
    return None


def redefinir(chave: str, tecla_nova: str) -> bool:
    """Muda a tecla de uma ação. Recusa (devolve False) se já estiver em uso."""
    if chave not in _registro:
        return False
    if conflito(chave, tecla_nova):
        return False
    _registro[chave].atual = tecla_nova
    return True


def restaurar_padrao(chave: str) -> None:
    if chave in _registro:
        _registro[chave].atual = _registro[chave].padrao


def restaurar_todos_os_padroes() -> None:
    for atalho in _registro.values():
        atalho.atual = atalho.padrao


def carregar_de(salvos: dict[str, str]) -> None:
    """Aplica teclas salvas por cima dos padrões. Chamado uma vez, ao iniciar.

    Precisa rodar DEPOIS que todo `registrar()` já aconteceu - uma chave
    salva que ainda não foi registrada é ignorada em silêncio (a ação pode
    ter sido removida numa versão mais nova do programa).
    """
    for chave, tecla in salvos.items():
        if chave in _registro and not conflito(chave, tecla):
            _registro[chave].atual = tecla


def overrides_para_salvar() -> dict[str, str]:
    """Só o que diverge do padrão - fica pequeno no configuracoes.json."""
    return {a.chave: a.atual for a in _registro.values() if a.atual != a.padrao}


def limpar_registro_para_teste() -> None:
    """Só para os testes: começar cada teste com o registro vazio."""
    _registro.clear()

