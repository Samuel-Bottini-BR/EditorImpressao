"""O trabalho salvo nunca se perde de vez.

Bug GRAVE achado pelo implementador em 29/09/2026 (Lista de bugs; decisao da
gerente, commit 2856987): livro que mudou de pasta (ou copia do mesmo PDF em
outra pasta) perdia o trabalho de vez. O projeto era achado pela assinatura
do arquivo, mas `projetos.combina_com` via o caminho antigo e o novo como
livros diferentes; aparecia "Voce mudou as opcoes... outro numero de
paginas" (falso) e o `projeto.json` era regravado na hora, sem copia.

O que se cobra aqui (teste de maquina):

    - rede de seguranca: antes de a conferencia recomecar por cima de um
      projeto salvo, o projeto.json antigo (e o acoes.jsonl e o posicao.json)
      e guardado ao lado, com data e hora no nome, sem nunca sobrescrever
      copia anterior;
    - o livro que mudou de pasta, achado pelo "Abrir", pelo "continuar"
      (religado sozinho) ou apontado a mao, e a copia do mesmo PDF em outra
      pasta, voltam com o trabalho (paginas, filtros, corte, alertas,
      conferidas, Historico), e o caminho novo passa a ser o gravado;
    - o caso contrario: outro PDF, mesmo nome e mesmo numero de paginas, em
      outra pasta, NAO recebe o trabalho do primeiro;
    - a mensagem do recomeco diz o motivo de verdade (outro livro, outro
      numero de folhas, outro numero de paginas) e onde esta a copia do
      trabalho anterior - ou que a copia nao pode ser feita.

Pasta de dados propria em saida_teste\\ (LOCALAPPDATA trocado): nada e criado
na pasta de dados real do Samuel. Os ajudantes e as fixtures vem de
tests/test_mesmo_livro_outro_caminho.py.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

import projetos  # noqa: E402
from historico_acoes import ARQUIVO_ACOES, ARQUIVO_POSICAO  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _conferir_que_o_trabalho_voltou,
    _pdf,
    _trabalhar_e_fechar,
    app,
    janela,
    pasta,
)


def _copias(pasta_do_projeto: Path, prefixo: str) -> list[Path]:
    return sorted(pasta_do_projeto.glob(f"{prefixo}.antigo-*"))


# --- a copia, direto ------------------------------------------------------------------


def test_sem_projeto_salvo_nao_ha_o_que_copiar(pasta):
    resumo = projetos.Resumo(pasta=str(pasta / "vazio"))
    assert projetos.guardar_copia_do_trabalho(resumo) is None


def test_a_copia_leva_o_trabalho_e_o_historico(pasta):
    projeto = pasta / "proj"
    projeto.mkdir()
    (projeto / projetos.ARQUIVO_ESTADO).write_text('{"trabalho": 1}', encoding="utf-8")
    (projeto / ARQUIVO_ACOES).write_text('{"acao": 1}\n', encoding="utf-8")
    (projeto / ARQUIVO_POSICAO).write_text('{"aplicadas": 1}', encoding="utf-8")
    resumo = projetos.Resumo(pasta=str(projeto))

    copia = projetos.guardar_copia_do_trabalho(resumo, agora=datetime(2026, 9, 29, 19, 30))
    assert copia == projeto / "projeto.antigo-2026-09-29-1930.json"
    assert copia.read_text(encoding="utf-8") == '{"trabalho": 1}'
    assert (projeto / "acoes.antigo-2026-09-29-1930.jsonl").read_text(
        encoding="utf-8") == '{"acao": 1}\n'
    assert (projeto / "posicao.antigo-2026-09-29-1930.json").is_file()
    # nada e apagado nem mudado
    assert (projeto / projetos.ARQUIVO_ESTADO).read_text(encoding="utf-8") == '{"trabalho": 1}'
    assert (projeto / ARQUIVO_ACOES).is_file()


def test_a_copia_nunca_sobrescreve_outra(pasta):
    projeto = pasta / "proj"
    projeto.mkdir()
    resumo = projetos.Resumo(pasta=str(projeto))
    agora = datetime(2026, 9, 29, 19, 30)

    (projeto / projetos.ARQUIVO_ESTADO).write_text("primeiro", encoding="utf-8")
    primeira = projetos.guardar_copia_do_trabalho(resumo, agora=agora)
    (projeto / projetos.ARQUIVO_ESTADO).write_text("segundo", encoding="utf-8")
    segunda = projetos.guardar_copia_do_trabalho(resumo, agora=agora)   # mesmo minuto

    assert primeira != segunda
    assert primeira.read_text(encoding="utf-8") == "primeiro"
    assert segunda.read_text(encoding="utf-8") == "segundo"
    assert segunda.name == "projeto.antigo-2026-09-29-1930-2.json"


def test_so_o_que_existe_e_copiado(pasta):
    """Projeto sem acoes gravadas: so o projeto.json vai para a copia."""
    projeto = pasta / "proj"
    projeto.mkdir()
    (projeto / projetos.ARQUIVO_ESTADO).write_text("{}", encoding="utf-8")
    projetos.guardar_copia_do_trabalho(projetos.Resumo(pasta=str(projeto)))
    assert len(_copias(projeto, "projeto")) == 1
    assert not _copias(projeto, "acoes")


# --- na janela de verdade: o recomeco guarda a copia -------------------------------------


def _estado(janela) -> Path:
    return Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO


def test_recomecar_a_conferencia_guarda_o_trabalho_antigo(janela, pasta):
    """O trabalho salvo nao serve (aqui: uma pagina a menos, como quando se
    muda "Dividir folhas ao meio"); a conferencia recomeca, e o trabalho
    antigo fica guardado ao lado, igualzinho."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    estado = _estado(janela)
    dados = json.loads(estado.read_text(encoding="utf-8"))
    dados["paginas"] = dados["paginas"][:3]
    estado.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    antes = estado.read_bytes()
    acoes_antes = (estado.parent / ARQUIVO_ACOES).read_bytes()

    janela.abrir_livro(str(livro))
    _analisar(janela)

    assert janela.avisos, "recomecou sem avisar"
    copias = _copias(estado.parent, "projeto")
    assert len(copias) == 1, "o trabalho antigo nao foi guardado"
    assert copias[0].read_bytes() == antes
    assert _copias(estado.parent, "acoes")[0].read_bytes() == acoes_antes
    # o projeto.json agora e o da conferencia nova (4 paginas)
    assert len(json.loads(estado.read_text(encoding="utf-8"))["paginas"]) == 4


def test_projeto_ilegivel_tambem_e_guardado_antes_de_ser_regravado(janela, pasta):
    """Um projeto.json que nao da para ler e regravado ao abrir: o que estava
    la fica guardado (pode ser recuperado a mao)."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    estado = _estado(janela)
    estado.write_text("{ isto nao e json", encoding="utf-8")

    janela.abrir_livro(str(livro))
    _analisar(janela)

    copias = _copias(estado.parent, "projeto")
    assert len(copias) == 1
    assert copias[0].read_text(encoding="utf-8") == "{ isto nao e json"


def test_abrir_o_mesmo_livro_sem_mudar_nada_nao_faz_copia(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro))
    _analisar(janela)
    assert not janela.avisos
    assert not _copias(Path(janela.resumo.pasta), "projeto")


def test_livro_novo_nao_faz_copia(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    _analisar(janela)
    assert not _copias(Path(janela.resumo.pasta), "projeto")


# --- o livro que mudou de pasta (commit 2 do conserto) -----------------------------------
#
# O projeto e achado pela assinatura do arquivo (projetos.achar_por_assinatura),
# mas combina_com via o caminho antigo (que nao existe mais) e o novo como
# livros diferentes: o trabalho ia embora. Agora combina_com tambem aceita a
# assinatura do arquivo recem-aberto igual a do projeto (resumo.assinatura).


def _mover(livro: Path, pasta_nova: Path) -> Path:
    pasta_nova.mkdir(parents=True, exist_ok=True)
    novo = pasta_nova / livro.name
    livro.rename(novo)
    return novo


def _gravado(janela) -> tuple[str, str]:
    """(caminho no resumo, caminho no projeto.json) como estao no disco."""
    resumo = projetos.ler_resumo(janela.resumo.pasta)
    return resumo.caminho_entrada, projetos.carregar_estado(resumo).caminho_entrada


def test_livro_movido_de_pasta_aberto_pelo_abrir_mantem_o_trabalho(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    novo = _mover(livro, pasta / "pasta nova")

    janela.abrir_livro(str(novo))
    _analisar(janela)

    _conferir_que_o_trabalho_voltou(janela, str(novo))
    assert _gravado(janela) == (str(novo), str(novo)), "o caminho novo nao foi gravado"
    assert not _copias(Path(janela.resumo.pasta), "projeto"), "recomecou a conferencia"


def test_continuar_depois_de_religar_o_livro_movido_mantem_o_trabalho(janela, pasta,
                                                                    monkeypatch):
    """Tela inicial: o livro saiu do lugar, o programa acha numa pasta ja
    usada ("religa sozinho") e o "continuar" devolve o trabalho."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    novo = _mover(livro, pasta / "pasta nova")
    monkeypatch.setattr(projetos, "_pastas_conhecidas", lambda: [novo.parent])
    monkeypatch.setattr(janela, "analisar", lambda: None)

    resumo = projetos.listar()[0]
    assert projetos.procurar_o_livro(resumo) == (projetos.RELIGADO, str(novo))
    janela.tela_inicio.pedir_para_continuar(resumo)
    _analisar(janela)

    _conferir_que_o_trabalho_voltou(janela, str(novo))
    assert _gravado(janela) == (str(novo), str(novo))


def test_livro_achado_a_mao_mantem_o_trabalho(janela, pasta, monkeypatch):
    """Tela inicial: o livro sumiu de tudo que o programa conhece; a pessoa
    aponta onde ele esta ("procurar de novo") e o trabalho volta."""
    from PySide6.QtWidgets import QFileDialog

    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    novo = _mover(livro, pasta / "pen drive")
    monkeypatch.setattr(projetos, "_pastas_conhecidas", lambda: [])
    monkeypatch.setattr(QFileDialog, "getOpenFileName",
                        staticmethod(lambda *a, **k: (str(novo).replace("\\", "/"), "")))
    monkeypatch.setattr(janela, "analisar", lambda: None)

    janela.tela_inicio.pedir_para_continuar(projetos.listar()[0])
    _analisar(janela)

    _conferir_que_o_trabalho_voltou(janela, str(novo).replace("\\", "/"))


def test_copia_do_livro_em_outra_pasta_mantem_o_trabalho(janela, pasta):
    """O mesmo PDF copiado para outra pasta (o original continua la) e o
    mesmo livro: o trabalho volta, e o projeto passa a apontar para a copia."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    (pasta / "copia").mkdir()
    copia = pasta / "copia" / livro.name
    shutil.copy2(livro, copia)

    janela.abrir_livro(str(copia))
    _analisar(janela)

    _conferir_que_o_trabalho_voltou(janela, str(copia))
    assert _gravado(janela) == (str(copia), str(copia))


def test_outro_pdf_com_o_mesmo_nome_em_outra_pasta_nao_recebe_o_trabalho(janela, pasta):
    """O caso contrario: outro livro, mesmo nome e mesmo numero de paginas,
    em outra pasta. E outro projeto, e o trabalho do primeiro fica intacto."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    pasta_do_primeiro = Path(janela.resumo.pasta)
    antes = (pasta_do_primeiro / projetos.ARQUIVO_ESTADO).read_bytes()

    (pasta / "outro").mkdir()
    outro = pasta / "outro" / livro.name
    doc = fitz.open()
    for i in range(4):
        doc.new_page(width=400, height=560).insert_text((40, 60), f"OUTRO {i}", fontsize=14)
    doc.save(str(outro))
    doc.close()
    assert projetos.assinatura_do_arquivo(outro) != projetos.assinatura_do_arquivo(livro)

    janela.abrir_livro(str(outro))
    _analisar(janela)

    assert Path(janela.resumo.pasta) != pasta_do_primeiro
    assert [p.filtro for p in janela.projeto.paginas] == ["original"] * 4
    assert (pasta_do_primeiro / projetos.ARQUIVO_ESTADO).read_bytes() == antes


# --- combina_com, direto ----------------------------------------------------------------


def _projeto_de(caminho: str, paginas: int = 4, folhas: int | None = None):
    """Projeto de `folhas` folhas (o padrao: uma por pagina) e `paginas`
    paginas (mais paginas que folhas = folhas divididas ao meio)."""
    from modelos import ConfigFolha, ConfigPagina, Projeto

    folhas = paginas if folhas is None else folhas
    p = Projeto(caminho_entrada=caminho, nome="x")
    p.folhas = [ConfigFolha(indice=i) for i in range(folhas)]
    p.paginas = [ConfigPagina(indice=i, folha=min(i, folhas - 1)) for i in range(paginas)]
    return p


def test_combina_pela_assinatura_quando_o_caminho_antigo_nao_existe_mais(pasta):
    livro = _pdf(pasta)
    assinatura = projetos.assinatura_do_arquivo(livro)
    salvo = _projeto_de(str(pasta / "sumiu" / livro.name))
    assert projetos.combina_com(salvo, _projeto_de(str(livro)), assinatura=assinatura)
    # sem a assinatura (projeto muito antigo), nao ha como saber: nao combina
    assert not projetos.combina_com(salvo, _projeto_de(str(livro)))
    assert not projetos.combina_com(salvo, _projeto_de(str(livro)), assinatura="")


def test_assinatura_diferente_nao_combina(pasta):
    livro = _pdf(pasta)
    salvo = _projeto_de(str(pasta / "sumiu" / livro.name))
    assert not projetos.combina_com(salvo, _projeto_de(str(livro)), assinatura="0" * 32)


def test_assinatura_igual_com_outro_numero_de_paginas_nao_combina(pasta):
    livro = _pdf(pasta)
    assinatura = projetos.assinatura_do_arquivo(livro)
    salvo = _projeto_de(str(pasta / "sumiu" / livro.name), paginas=4)
    agora = _projeto_de(str(livro), paginas=8)
    assert not projetos.combina_com(salvo, agora, assinatura=assinatura)


# --- a mensagem do recomeco diz o motivo de verdade (commit 3 do conserto) ------------------
#
# Antes: "Voce mudou as opcoes desde a ultima vez, e o livro ficou com outro
# numero de paginas..." para QUALQUER motivo (inclusive o livro que mudou de
# pasta, sem opcao nenhuma mudada), e sem dizer que havia copia. Quando ela
# aparece nao mudou: so o texto.


def test_motivo_outro_numero_de_paginas(pasta):
    livro = str(_pdf(pasta))
    motivo = projetos.motivo_para_nao_combinar(_projeto_de(livro, 3, folhas=3),
                                               _projeto_de(livro, 4, folhas=3))
    assert "3 páginas" in motivo and "4" in motivo
    assert "Dividir folhas ao meio" in motivo


def test_motivo_outro_numero_de_folhas(pasta):
    from modelos import ConfigFolha

    livro = str(_pdf(pasta))
    salvo, agora = _projeto_de(livro, 4), _projeto_de(livro, 4)
    agora.folhas.append(ConfigFolha(indice=4))
    motivo = projetos.motivo_para_nao_combinar(salvo, agora)
    assert "4 folhas" in motivo and "5" in motivo


def test_motivo_outro_livro(pasta):
    livro = _pdf(pasta)
    salvo = _projeto_de(str(pasta / "sumiu" / livro.name))
    motivo = projetos.motivo_para_nao_combinar(salvo, _projeto_de(str(livro)),
                                               assinatura="0" * 32)
    assert "não é o mesmo livro" in motivo


def test_sem_motivo_quando_combina(pasta):
    livro = str(_pdf(pasta))
    assert projetos.motivo_para_nao_combinar(_projeto_de(livro), _projeto_de(livro)) == ""


def test_uma_pagina_no_singular(pasta):
    livro = str(_pdf(pasta))
    motivo = projetos.motivo_para_nao_combinar(_projeto_de(livro, 1, folhas=1),
                                               _projeto_de(livro, 2, folhas=1))
    assert "1 página " in motivo or motivo.endswith("1 página")


def test_mensagem_do_recomeco_diz_o_motivo_e_onde_esta_a_copia(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    estado = _estado(janela)
    dados = json.loads(estado.read_text(encoding="utf-8"))
    dados["paginas"] = dados["paginas"][:3]
    estado.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")

    janela.abrir_livro(str(livro))
    _analisar(janela)

    assert len(janela.avisos) == 1
    aviso = janela.avisos[0]
    assert "Você mudou as opções" not in aviso           # nao acusa quem nao mudou nada
    assert "3 páginas" in aviso and "4" in aviso           # o motivo de verdade
    assert "não foi apagado" in aviso
    copia = _copias(estado.parent, "projeto")[0]
    assert str(copia) in aviso, "nao disse onde esta a copia"
    assert all(ord(c) < 0x2000 for c in aviso if c not in "“”")   # sem emoji


def test_mensagem_sem_copia_nao_promete_copia(janela, pasta, monkeypatch):
    """Se a copia falhou (disco cheio, sem permissao), a mensagem nao diz que
    guardou: diz que nao conseguiu."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    estado = _estado(janela)
    dados = json.loads(estado.read_text(encoding="utf-8"))
    dados["paginas"] = dados["paginas"][:3]
    estado.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(projetos, "guardar_copia_do_trabalho", lambda *a, **k: None)

    janela.abrir_livro(str(livro))
    _analisar(janela)

    assert len(janela.avisos) == 1
    assert "não foi apagado" not in janela.avisos[0]
    assert "Não consegui guardar uma cópia" in janela.avisos[0]


# --- todo salvamento vai para a pasta do projeto aberto (parecer do verificador, bug 1) ---
#
# GRAVE, antigo (18/07): closeEvent, processar e _processamento_pronto
# chamavam historico.salvar_projeto, que escolhia a pasta pelo NOME do livro.
# Dois PDFs diferentes com o mesmo nome de arquivo: fechar o programa com o
# segundo aberto gravava o estado dele por cima do trabalho do primeiro, sem
# copia e sem aviso (e, depois do 3cfb682, o primeiro aceitava calado).
# Reproducao do verificador: relatorios/conferir/fase1-2026-09-29-trabalho-
# salvo/verificador/reproducoes/reproduz_mesmo_nome.py (prints p15-p17).


def _outro_livro_de_mesmo_nome(pasta: Path, livro: Path) -> Path:
    """Outro PDF (conteudo diferente), mesmo nome, mesmo numero de paginas."""
    (pasta / "outro").mkdir(exist_ok=True)
    outro = pasta / "outro" / livro.name
    doc = fitz.open()
    for i in range(4):
        doc.new_page(width=400, height=560).insert_text((40, 60), f"OUTRO {i}", fontsize=14)
    doc.save(str(outro))
    doc.close()
    return outro


def _pastas_de_projeto() -> list[str]:
    return sorted(p.name for p in projetos.pasta_dos_projetos().iterdir() if p.is_dir())


def test_fechar_com_outro_livro_de_mesmo_nome_nao_apaga_o_primeiro(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    pasta_um = Path(janela.resumo.pasta)
    antes = (pasta_um / projetos.ARQUIVO_ESTADO).read_bytes()

    outro = _outro_livro_de_mesmo_nome(pasta, livro)
    janela.abrir_livro(str(outro))
    _analisar(janela)
    pasta_dois = Path(janela.resumo.pasta)
    assert pasta_dois != pasta_um
    janela.projeto.paginas[0].filtro = "melhorar"
    janela.close()                                   # closeEvent de verdade

    assert (pasta_um / projetos.ARQUIVO_ESTADO).read_bytes() == antes, (
        "fechar com o outro livro aberto gravou por cima do trabalho do primeiro")
    # o trabalho do segundo foi para a pasta DELE
    salvo_dois = projetos.carregar_estado(projetos.ler_resumo(pasta_dois))
    assert salvo_dois.paginas[0].filtro == "melhorar"
    assert projetos.mesmo_arquivo(salvo_dois.caminho_entrada, str(outro))
    # e nenhuma pasta-sombra nasceu ao lado
    assert _pastas_de_projeto() == sorted([pasta_um.name, pasta_dois.name])


def test_primeiro_livro_reaberto_depois_de_fechar_o_outro_volta_com_o_trabalho(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    outro = _outro_livro_de_mesmo_nome(pasta, livro)
    janela.abrir_livro(str(outro))
    _analisar(janela)
    janela.close()

    janela.abrir_livro(str(livro))
    _analisar(janela)
    assert not janela.avisos, janela.avisos
    assert janela.projeto.paginas[1].filtro == "magico_pro"
    assert [p.revisada for p in janela.projeto.paginas] == [True, True, True, False]


def test_processar_grava_na_pasta_do_projeto_e_nao_pelo_nome(janela, pasta, monkeypatch):
    """"Confirmar e processar" e o fim do processamento gravavam pelo nome."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    pasta_um = Path(janela.resumo.pasta)
    antes = (pasta_um / projetos.ARQUIVO_ESTADO).read_bytes()
    outro = _outro_livro_de_mesmo_nome(pasta, livro)
    janela.abrir_livro(str(outro))
    _analisar(janela)
    pasta_dois = Path(janela.resumo.pasta)

    saida = pasta / "saida" / "pronto.pdf"
    saida.parent.mkdir()
    doc = fitz.open()
    doc.new_page()
    doc.save(str(saida))
    doc.close()
    monkeypatch.setattr(janela, "_resolver_destino", lambda: saida)

    class TarefaQueNaoRoda:
        def __init__(self, *_a):
            from unittest.mock import MagicMock
            self.progresso = self.concluida = self.falhou = self.cancelada = MagicMock()

        def start(self):
            pass

        def isRunning(self):          # o closeEvent do fim do teste pergunta
            return False

    import ui.janela_principal as modulo
    monkeypatch.setattr(modulo, "TarefaProcessar", TarefaQueNaoRoda)
    janela.processar()
    janela._processamento_pronto(str(saida))

    assert (pasta_um / projetos.ARQUIVO_ESTADO).read_bytes() == antes
    salvo_dois = projetos.carregar_estado(projetos.ler_resumo(pasta_dois))
    assert projetos.mesmo_arquivo(salvo_dois.caminho_saida, str(saida))
    assert _pastas_de_projeto() == sorted([pasta_um.name, pasta_dois.name])
