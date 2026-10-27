"""Preferencias que o programa lembra de uma vez para a outra.

Fica em %LOCALAPPDATA%\\EditorImpressao\\configuracoes.json. Nada aqui e
essencial: se o arquivo sumir ou vier corrompido, o programa volta aos padroes
sem reclamar.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

ARQUIVO = "configuracoes.json"

PADROES: dict[str, Any] = {
    "ultima_pasta_de_saida": "",
    "ultima_pasta_de_entrada": "",
    "atalhos": {},
    "qualidade_previa": "rapida",
    # O tema da tela (layout, etapa 1, 08/10/2026): "escuro", "cinza" ou
    # "claro"; de fabrica "cinza" (o mesmo de ui/estilo.TEMA_DE_FABRICA, que
    # nao e importado aqui para este arquivo nao depender de ui/). Por
    # enquanto a tela ainda guarda a escolha no tema.json dela (ui/estilo.py);
    # o agente de layout passa a usar esta chave na etapa seguinte. Seguro
    # mudar: nada aqui sem mudar ui/estilo.py junto. Arriscado: outro valor de
    # fabrica que nao seja um dos tres temas.
    "tema": "cinza",
    # O livro aberto na tela inteira (layout, 22/10/2026, "como o UPDF"): o
    # jeito de mostrar ("uma" ou "duas" lado a lado), se rola sem parar, e o
    # jeito de caber ("pagina", "altura", "largura" ou "real"). Lido e gravado
    # por ui/tela_inicio.LivroAberto; valor estranho volta ao de fabrica.
    "livro_aberto": {"mostrar": "uma", "rolar": True, "caber": "pagina"},
    # As miniaturas da tela de trabalho (layout, 22/10/2026; Samuel, 21/10:
    # "Sim, lembrar para todos os livros"): o lugar ("embaixo", "esquerda" ou
    # "direita"), se estao abertas e se estao em pares. Lido e gravado por
    # ui/tela_conferir.TelaConferir; valor estranho volta ao de fabrica.
    "miniaturas": {"lugar": "embaixo", "aberta": True, "em_pares": False},
    # Item 2.6: as ultimas escolhas da janela "Montar para imprimir"
    # (core/impressao.OpcoesDeImpressao.para_dicionario), como a "Predefinicao:
    # Ultima configuracao" do UPDF. Vazio = as de fabrica (as decisoes do
    # Samuel). Seguro mudar: nada (quem le corrige o que vier estranho).
    "impressao": {},
    # Item 2.16: quantas paginas ao mesmo tempo (core/nucleos.py). 0 = todos
    # os nucleos, como o ScanTailor (de fabrica); 1 = uma por vez, como antes.
    "nucleos": 0,
    # Item 2.19: a unidade das medidas na tela (core/unidades.py; de fabrica
    # "cm", o de sempre) e as receitas do livro (core/perfis.py): {nome:
    # {campo: valor}} e a de todo livro novo ("" = nenhuma, o de fabrica).
    "unidade": "cm",
    "perfis": {},
    "perfil_do_livro_novo": "",
    # O jeito do lado direito da tela de trabalho (etapa 2 da obra, 26/10/2026;
    # Samuel, rodada 7, 203 D: "Ícones na borda, tudo fechado" + "Mas eu também
    # quero ter a opção da area de trabalho 1"; rodada 14, 902 C: escolhe-se no
    # menu Ver e nas Configurações): "icones" (de fábrica) ou "sanfona" (a área
    # de trabalho 1). Lido e gravado por ui/widgets/paineis.jeito_guardado e
    # guardar_jeito; valor estranho volta ao de fábrica. Seguro mudar: nada.
    "lado_direito": "icones",
    # Obra de 26/10/2026, etapa 3 (D-093/D-094, g6-retangulo, 09/10: "Fica no
    # mesmo lugar da página (como no ScanTailor)" de fabrica, e "quero a b e c
    # juntas."): o que o corte a mao faz quando o angulo muda depois, para
    # todos os livros: "fica" (de fabrica) ou "acompanha". O livro
    # (Projeto.retangulo_do_corte) e a pagina podem trocar. Lido por
    # ui/tela_conferir._jeito_do_retangulo. Seguro mudar: nada.
    "retangulo_do_corte": "fica",
}


def _caminho() -> Path:
    """Onde o configuracoes.json mora."""
    from historico import pasta_de_dados

    return pasta_de_dados() / ARQUIVO


def carregar() -> dict[str, Any]:
    """Le o arquivo, completando com PADROES o que faltar. Se o arquivo estiver
    ausente ou corrompido, devolve so os padroes - nunca quebra o programa."""
    dados = dict(PADROES)
    try:
        arquivo = _caminho()
        if arquivo.exists():
            salvos = json.loads(arquivo.read_text(encoding="utf-8"))
            if isinstance(salvos, dict):
                dados.update({c: salvos[c] for c in PADROES if c in salvos})
    except (OSError, ValueError, TypeError):
        pass  # configuracao quebrada nao pode impedir o programa de abrir
    return dados


def salvar(dados: dict[str, Any]) -> None:
    """Grava o dicionario inteiro. Falha em silencio (config nao e essencial)."""
    try:
        arquivo = _caminho()
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        arquivo.write_text(
            json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    except OSError:
        pass


def ler(chave: str) -> Any:
    """Le uma unica chave (recarrega o arquivo inteiro - configuracao e
    pequena, nao vale a pena guardar em cache)."""
    return carregar().get(chave, PADROES.get(chave))


def escrever(chave: str, valor: Any) -> None:
    """Muda uma unica chave e regrava o arquivo inteiro."""
    dados = carregar()
    dados[chave] = valor
    salvar(dados)


# ---------------------------------------------------------------------------
# pasta de saida
# ---------------------------------------------------------------------------

def pasta_de_saida_sugerida() -> Path:
    """A última pasta usada, se ainda existir; senao Documentos/Editor de Impressão."""
    from historico import pasta_de_saida_padrao

    ultima = ler("ultima_pasta_de_saida")
    if ultima:
        caminho = Path(ultima)
        if caminho.is_dir():
            return caminho
    return pasta_de_saida_padrao()


def lembrar_pasta_de_saida(pasta: str | Path) -> None:
    """Grava a pasta como sugestao para a proxima vez, so se ela existir de verdade."""
    caminho = Path(pasta)
    if caminho.is_dir():
        escrever("ultima_pasta_de_saida", str(caminho))


def pode_gravar_em(pasta: str | Path) -> tuple[bool, str]:
    """Diz se da para gravar na pasta, e por que não, em portugues.

    Testa escrevendo de verdade um arquivo temporario. Olhar só os atributos
    engana: uma pasta pode parecer gravavel e a gravacao falhar por causa de
    permissão de rede, pendrive protegido ou pasta do sistema.
    """
    caminho = Path(pasta)

    if not caminho.exists():
        try:
            caminho.mkdir(parents=True, exist_ok=True)
        except OSError:
            return False, "Não consegui criar essa pasta. Escolha outra."

    if not caminho.is_dir():
        return False, "Esse caminho não é uma pasta."

    try:
        with tempfile.NamedTemporaryFile(dir=caminho, prefix=".editor_", suffix=".tmp"):
            pass
    except PermissionError:
        return False, (
            "Não tenho permissão para gravar nessa pasta. "
            "Tente uma pasta dentro de Documentos ou da Área de Trabalho."
        )
    except OSError:
        return False, (
            "Não consegui gravar nessa pasta. Ela pode estar cheia, "
            "protegida contra gravacao ou desconectada."
        )
    return True, ""


def espaco_livre_mb(pasta: str | Path) -> float | None:
    """Espaco livre em disco, em MB. os.statvfs primeiro (Linux/Mac - nao
    existe no Windows, cai no except), shutil.disk_usage como plano B
    (funciona em qualquer SO). None se nenhum dos dois conseguir responder."""
    try:
        return os.statvfs(pasta).f_bavail * os.statvfs(pasta).f_frsize / 1024 / 1024  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass
    try:
        import shutil

        return shutil.disk_usage(pasta).free / 1024 / 1024
    except OSError:
        return None


def caminho_sem_repetir(pasta: str | Path, nome_do_arquivo: str) -> Path:
    """Acrescenta (2), (3)... até achar um nome que ainda não existe."""
    base = Path(pasta) / nome_do_arquivo
    if not base.exists():
        return base
    caule, sufixo = base.stem, base.suffix or ".pdf"
    contador = 2
    while True:
        tentativa = Path(pasta) / f"{caule} ({contador}){sufixo}"
        if not tentativa.exists():
            return tentativa
        contador += 1
