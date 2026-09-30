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
from core.filtros import MAGICO_PRO  # noqa: E402
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
    # (o sinal invisivel U+2060 segura a letra da unidade no resto do caminho)
    assert str(copia) in aviso.replace("\u2060", ""), "nao disse onde esta a copia"
    assert all(ord(c) < 0x2000 for c in aviso if c not in "\u201c\u201d\u2060")   # sem emoji


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


# --- fechar antes do fim da analise nao grava por cima (parecer do verificador, bug 2) ---
#
# GRAVE, antigo: abrir um livro salvo e fechar o programa na tela "O que
# fazer" (ou em "Olhando o livro...") gravava o projeto ainda vazio (0
# paginas) por cima do salvo, sem copia e sem aviso na proxima vez
# (closeEvent -> _salvar_agora). Reproducao: reproducoes/
# reproduz_fechar_no_o_que_fazer.py; prints p18-p20.


def test_abrir_livro_salvo_e_fechar_no_o_que_fazer_nao_apaga_o_trabalho(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    estado = _estado(janela)
    antes = estado.read_bytes()
    resumo_antes = projetos.ler_resumo(janela.resumo.pasta)

    janela.abrir_livro(str(livro))             # fica em "O que fazer"
    janela.close()

    assert estado.read_bytes() == antes, "fechar no 'O que fazer' apagou o trabalho"
    resumo = projetos.ler_resumo(janela.resumo.pasta)
    assert resumo.conferidas == resumo_antes.conferidas == 3, "o cartao perdeu as conferidas"

    janela.abrir_livro(str(livro))
    _analisar(janela)
    _conferir_que_o_trabalho_voltou(janela, str(livro))


def test_fechar_durante_a_analise_do_continuar_nao_apaga_o_trabalho(janela, pasta,
                                                                    monkeypatch):
    """"continuar" e fechar em "Olhando o livro..." (a analise nao acabou)."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    antes = _estado(janela).read_bytes()
    monkeypatch.setattr(janela, "analisar", lambda: None)      # analise "rodando"

    janela._continuar_projeto(projetos.achar_por_assinatura(str(livro)))
    janela._salvar_agora()                     # o relogio de salvar dispara
    janela.close()

    assert _estado(janela).read_bytes() == antes


def test_fechar_no_meio_de_uma_nova_analise_nao_grava_o_projeto_pela_metade(janela, pasta,
                                                                          monkeypatch):
    """Voltou da conferencia para "O que fazer" e clicou "Conferir" de novo: a
    analise refaz as paginas no proprio projeto. Fechar no meio nao grava."""
    import ui.janela_principal as modulo

    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    antes = _estado(janela).read_bytes()

    class AnaliseQueNaoAcaba:
        def __init__(self, projeto):
            from unittest.mock import MagicMock
            self.progresso = self.concluida = self.falhou = MagicMock()
            projeto.paginas = []                # a analise mexeu no projeto

        def start(self):
            pass

        def isRunning(self):
            return False

    monkeypatch.setattr(modulo, "TarefaAnalise", AnaliseQueNaoAcaba)
    janela.abrir_livro(str(livro))
    janela.analisar()
    janela.close()
    assert _estado(janela).read_bytes() == antes


def test_livro_novo_fechado_no_o_que_fazer_guarda_as_opcoes_como_antes(janela, pasta):
    """Livro sem trabalho salvo: fechar no "O que fazer" continua gravando o
    projeto vazio com as opcoes escolhidas (o "continuar" as traz de volta)."""
    janela.abrir_livro(str(_pdf(pasta)))
    janela.projeto.dividir_folhas = False
    janela.close()
    salvo = projetos.carregar_estado(janela.resumo)
    assert salvo is not None and salvo.paginas == []
    assert salvo.dividir_folhas is False


def test_projeto_ilegivel_nao_e_regravado_ao_fechar_antes_da_analise(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    _estado(janela).write_text("{ quebrado", encoding="utf-8")
    janela.abrir_livro(str(livro))
    janela.close()
    assert _estado(janela).read_text(encoding="utf-8") == "{ quebrado"


def test_depois_da_analise_fechar_grava_normalmente(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro))
    _analisar(janela)
    janela.projeto.paginas[0].filtro = "melhorar"
    janela.close()
    assert projetos.carregar_estado(janela.resumo).paginas[0].filtro == "melhorar"


# --- reabrir traz as opcoes salvas na tela "O que fazer" (parecer do verificador, bug 3) ---
#
# Livro conferido com "Dividir folhas ao meio" desmarcado e reaberto pelo
# "Abrir", arrastando ou pelo Windows (todos passam por abrir_livro): a opcao
# voltava marcada, a conferencia recomecava e a mensagem dizia que a pessoa
# tinha mudado a opcao. Pelo "continuar" nao acontecia (so ele trazia as
# opcoes salvas). Reproducao: reproducoes/reproduz_dividir_desmarcado_abrir.py;
# prints p25, p26. Resolve tambem "reabrindo pelo 'Abrir', 'O que fazer'
# mostra o filtro do livro em Original" (print t10 da rodada de 18:26).


def _pdf_deitado(pasta: Path) -> Path:
    """3 folhas deitadas com a lombada no meio: com "Dividir folhas ao meio",
    viram 6 paginas; sem, 3."""
    (pasta / "livros").mkdir(exist_ok=True)
    caminho = pasta / "livros" / "Deitado.pdf"
    doc = fitz.open()
    for i in range(3):
        pagina = doc.new_page(width=800, height=560)
        pagina.insert_text((40, 60), f"esquerda {i}", fontsize=14)
        pagina.insert_text((440, 60), f"direita {i}", fontsize=14)
        pagina.draw_line((400, 0), (400, 560), width=3)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _conferir_deitado_sem_dividir(janela, caminho: str) -> None:
    """Abre, desmarca "Dividir folhas ao meio" e escolhe Melhorar para o
    livro, pela tela "O que fazer"; confere, mexe e fecha."""
    janela.abrir_livro(caminho)
    janela.tela_opcoes.cx_dividir.setChecked(False)
    janela.tela_opcoes.radios_de_filtro["melhorar"].setChecked(True)
    _analisar(janela)
    assert len(janela.projeto.paginas) == 3
    janela.projeto.paginas[1].filtro = MAGICO_PRO
    janela.projeto.paginas[1].revisada = True
    janela._salvar_agora()
    janela.previas.parar()
    janela.previas = None
    janela.tela_opcoes.folhear.fechar()


def test_reabrir_pelo_abrir_traz_as_opcoes_salvas_e_nao_recomeca(janela, pasta):
    livro = _pdf_deitado(pasta)
    _conferir_deitado_sem_dividir(janela, str(livro))

    janela.abrir_livro(str(livro).replace("\\", "/"))       # pelo "Abrir"
    opcoes = janela.tela_opcoes
    assert not opcoes.cx_dividir.isChecked(), "'Dividir folhas ao meio' voltou marcada"
    assert opcoes.radios_de_filtro["melhorar"].isChecked(), "o filtro do livro voltou a Original"
    assert janela.projeto.dividir_folhas is False
    assert janela.projeto.filtro_padrao == "melhorar"

    _analisar(janela)
    assert not janela.avisos, janela.avisos
    assert len(janela.projeto.paginas) == 3
    assert janela.projeto.paginas[1].filtro == MAGICO_PRO
    assert not _copias(Path(janela.resumo.pasta), "projeto")


def test_as_caixinhas_do_livro_anterior_nao_contaminam_as_salvas(janela, pasta):
    """Bug das caixinhas (Lista de bugs, 29/09), no caso que importa aqui: ao
    carregar, cada caixinha que mudava gravava no projeto o estado das outras
    ainda com o valor do livro anterior."""
    livro = _pdf_deitado(pasta)
    _conferir_deitado_sem_dividir(janela, str(livro))     # salvo: limpar ligado

    janela.abrir_livro(str(_pdf(pasta)))                   # outro livro...
    janela.tela_opcoes.cx_limpar.setChecked(False)         # ...com "Limpar" desligado
    janela.tela_opcoes.cx_endireitar.setChecked(False)
    janela.tela_opcoes.folhear.fechar()

    janela.abrir_livro(str(livro))
    opcoes = janela.tela_opcoes
    assert opcoes.cx_limpar.isChecked() and janela.projeto.limpar
    assert opcoes.cx_endireitar.isChecked() and janela.projeto.endireitar
    assert not opcoes.cx_dividir.isChecked() and not janela.projeto.dividir_folhas
    assert janela.projeto.filtro_padrao == "melhorar"


def test_continuar_continua_trazendo_as_opcoes_salvas(janela, pasta, monkeypatch):
    livro = _pdf_deitado(pasta)
    _conferir_deitado_sem_dividir(janela, str(livro))
    monkeypatch.setattr(janela, "analisar", lambda: None)
    janela._continuar_projeto(projetos.achar_por_assinatura(str(livro)))
    assert not janela.tela_opcoes.cx_dividir.isChecked()
    _analisar(janela)
    assert not janela.avisos
    assert janela.projeto.paginas[1].filtro == MAGICO_PRO


def test_livro_novo_abre_com_as_opcoes_de_fabrica(janela, pasta):
    janela.abrir_livro(str(_pdf_deitado(pasta)))
    assert janela.tela_opcoes.cx_dividir.isChecked()
    assert janela.projeto.filtro_padrao == "original"


# --- o caminho da copia nao quebra a linha depois de "D:" (parecer do verificador, bug 4) ---


def _linhas_da_caixa(janela, texto: str) -> list[str]:
    """Mostra a caixa de aviso de verdade (a mesma de JanelaPrincipal.avisar,
    com a folha de estilo do programa) e devolve as linhas em que o texto se
    quebra nela, com a regra de quebra do Qt (QTextLayout, na fonte e na
    largura do rotulo)."""
    from PySide6.QtGui import QTextLayout, QTextOption
    from PySide6.QtWidgets import QApplication, QLabel, QMessageBox

    caixa = QMessageBox(janela)
    caixa.setText(texto)
    caixa.addButton("entendi", QMessageBox.AcceptRole)
    caixa.show()
    QApplication.processEvents()
    try:
        rotulo = next(r for r in caixa.findChildren(QLabel) if r.text() == texto)
        linhas = []
        for paragrafo in texto.split("\n"):
            layout = QTextLayout(paragrafo, rotulo.font())
            opcao = QTextOption()
            opcao.setWrapMode(QTextOption.WrapMode.WordWrap)
            layout.setTextOption(opcao)
            layout.beginLayout()
            while True:
                linha = layout.createLine()
                if not linha.isValid():
                    break
                linha.setLineWidth(rotulo.contentsRect().width())
                linhas.append(paragrafo[linha.textStart():linha.textStart() + linha.textLength()])
            layout.endLayout()
        return linhas
    finally:
        caixa.close()


def test_caminho_da_copia_nao_deixa_a_letra_da_unidade_sozinha(janela):
    """Print p23: "D:" sozinho numa linha e o resto do caminho embaixo."""
    copia = Path(r"D:\programas\EditorImpressao\saida_teste\verificador_trabalho_salvo"
                 r"\dados\EditorImpressao\projetos\Modelo Siebmacher"
                 r"\projeto.antigo-2026-09-29-2033.json")
    frase = janela._frase_do_recomeco(
        "o trabalho salvo tinha 13 páginas e agora o livro tem 7. Isso acontece quando "
        "se muda a opção “Dividir folhas ao meio”", copia)
    linhas = [linha.strip().replace("\u2060", "") for linha in _linhas_da_caixa(janela, frase)]
    assert "D:" not in linhas, linhas
    # o caminho continua la, inteiro (tirando o sinal invisivel que segura a
    # letra da unidade junto do resto)
    assert str(copia) in frase.replace("\u2060", "")


# --- "cancelar" a analise nao desliga o salvamento (parecer do verificador, 2a rodada) ---
#
# GRAVE, nascido do 4c01fa6: livro com trabalho, na conferencia -> "Voltar
# para as opcoes" -> "Conferir" -> "cancelar" em "Olhando o livro...". A
# janela voltava para a conferencia, mas trabalho_carregado ficava falso e
# nada mais era gravado ate fechar, sem aviso (prints q21-q23;
# reproducoes/sonda_cancelar_e_dois_projetos.py, parte P1).


def _esperar_a_tarefa(janela) -> None:
    from PySide6.QtWidgets import QApplication

    if janela.tarefa is not None:
        janela.tarefa.wait(60000)
    for _ in range(5):
        QApplication.processEvents()


def _voltar_conferir_e_cancelar(janela, monkeypatch=None) -> None:
    """Da conferencia para "O que fazer", "Conferir" e "cancelar"."""
    janela._sair_da_conferencia()
    janela.analisar()
    janela.cancelar()


def _mexer_e_conferir_que_gravou(janela) -> None:
    janela.projeto.paginas[2].filtro = "melhorar"
    janela._salvar_agora()
    assert projetos.carregar_estado(janela.resumo).paginas[2].filtro == "melhorar", (
        "depois do cancelar, o programa parou de gravar")
    janela.projeto.paginas[3].filtro = "preto_e_branco"
    janela.close()                                   # e ao fechar tambem
    assert projetos.carregar_estado(janela.resumo).paginas[3].filtro == "preto_e_branco"


def test_cancelar_a_analise_volta_a_conferencia_e_continua_gravando(janela, pasta):
    """Com a analise de verdade (em segundo plano), cancelada logo."""
    from ui.janela_principal import CONFERIR

    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))          # trabalho carregado na tela
    _voltar_conferir_e_cancelar(janela)
    _esperar_a_tarefa(janela)

    assert janela.telas.currentIndex() == CONFERIR
    assert janela.projeto.paginas[1].filtro == MAGICO_PRO, "o trabalho sumiu da tela"
    _mexer_e_conferir_que_gravou(janela)


def test_cancelar_quando_a_analise_ja_tinha_acabado_nao_poe_paginas_em_branco(janela, pasta):
    """O cancelar chega depois de a analise terminar (resultado na fila): o
    resultado e ignorado e o projeto da tela continua com o trabalho."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela._sair_da_conferencia()
    janela.analisar()
    janela.tarefa.wait(60000)                        # acabou; o resultado esta na fila
    janela.cancelar()
    _esperar_a_tarefa(janela)
    assert janela.projeto.paginas[1].filtro == MAGICO_PRO
    assert [p.revisada for p in janela.projeto.paginas] == [True, True, True, False]
    _mexer_e_conferir_que_gravou(janela)


def test_erro_na_analise_nao_desliga_o_salvamento(janela, pasta, monkeypatch):
    import ui.janela_principal as modulo

    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))

    class AnaliseQueFalha:
        foi_cancelada = False

        def __init__(self, projeto):
            from unittest.mock import MagicMock
            self.progresso = self.concluida = self.falhou = MagicMock()

        def start(self):
            pass

        def isRunning(self):
            return False

        def cancelar(self):
            pass

    monkeypatch.setattr(modulo, "TarefaAnalise", AnaliseQueFalha)
    janela._sair_da_conferencia()
    janela.analisar()
    janela._falhou_na_analise("Não consegui ler o livro.")
    assert janela.avisos == ["Não consegui ler o livro."]
    _mexer_e_conferir_que_gravou(janela)


def test_cancelar_livro_recem_aberto_continua_sem_gravar_por_cima(janela, pasta):
    """Livro com trabalho salvo recem-aberto (projeto vazio na tela): o
    cancelar volta ao "O que fazer" e continua sem gravar por cima."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    antes = _estado(janela).read_bytes()
    janela.abrir_livro(str(livro))
    janela.analisar()
    janela.cancelar()
    _esperar_a_tarefa(janela)
    janela.close()
    assert _estado(janela).read_bytes() == antes


def test_trocar_de_livro_no_meio_da_analise_nao_mistura_os_livros(janela, pasta):
    """O resultado da analise do livro de antes, que chega depois de abrir
    outro livro, e ignorado."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    pasta_um = Path(janela.resumo.pasta)
    antes = (pasta_um / projetos.ARQUIVO_ESTADO).read_bytes()
    janela._sair_da_conferencia()
    janela.analisar()
    janela.tarefa.wait(60000)                        # resultado do livro 1 na fila

    outro = _outro_livro_de_mesmo_nome(pasta, livro)
    janela.abrir_livro(str(outro))                   # troca de livro
    _esperar_a_tarefa(janela)                        # a fila anda

    assert projetos.mesmo_arquivo(janela.projeto.caminho_entrada, str(outro))
    assert janela.projeto.paginas == [], "o resultado do livro 1 entrou no livro 2"
    janela.close()
    assert (pasta_um / projetos.ARQUIVO_ESTADO).read_bytes() == antes


# --- o "continuar" de um cartao abre exatamente aquele projeto (verificador, 2a rodada) ---
#
# Dois projetos do mesmo PDF (o segundo nasce com "(2)" no nome): o
# "continuar" do cartao mais antigo abria o mais recente, porque abrir_livro
# achava o projeto pela assinatura (o mais recente). Prints q24 e q25.


def _dois_projetos_do_mesmo_livro(janela, pasta: Path):
    """Projeto A (o mais antigo, pagina 2 em Magico pro) e projeto B (o mais
    recente, tudo em Preto e branco), do MESMO PDF. Devolve (livro, A, B)."""
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    resumo_a = projetos.ler_resumo(janela.resumo.pasta)

    estado_a = json.loads((Path(resumo_a.pasta) / projetos.ARQUIVO_ESTADO).read_text(
        encoding="utf-8"))
    from modelos import Projeto

    resumo_b = projetos.criar(Projeto(caminho_entrada=str(livro), nome=livro.stem), 4)
    for pagina in estado_a["paginas"]:
        pagina["filtro"] = "preto_e_branco"
    (Path(resumo_b.pasta) / projetos.ARQUIVO_ESTADO).write_text(
        json.dumps(estado_a, ensure_ascii=False), encoding="utf-8")
    # datas diferentes de proposito: A e o cartao mais antigo
    for resumo, quando in ((resumo_a, "2026-09-01T10:00:00"), (resumo_b, "2026-09-20T10:00:00")):
        caminho = Path(resumo.pasta) / projetos.ARQUIVO_RESUMO
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        dados["mexido_em"] = quando
        caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    assert [r.pasta for r in projetos.listar()] == [resumo_b.pasta, resumo_a.pasta]
    return livro, projetos.ler_resumo(resumo_a.pasta), projetos.ler_resumo(resumo_b.pasta)


def test_continuar_o_cartao_mais_antigo_abre_ele_e_nao_o_mais_recente(janela, pasta,
                                                                    monkeypatch):
    _livro, resumo_a, resumo_b = _dois_projetos_do_mesmo_livro(janela, pasta)
    estado_b = (Path(resumo_b.pasta) / projetos.ARQUIVO_ESTADO).read_bytes()
    monkeypatch.setattr(janela, "analisar", lambda: None)

    janela.tela_inicio.pedir_para_continuar(resumo_a)          # o cartao de A
    _analisar(janela)

    assert janela.resumo.pasta == resumo_a.pasta, "abriu o outro projeto"
    assert [p.filtro for p in janela.projeto.paginas][:2] == ["original", MAGICO_PRO]
    janela.projeto.paginas[0].filtro = "melhorar"
    janela.close()
    assert projetos.carregar_estado(resumo_a).paginas[0].filtro == "melhorar"
    assert (Path(resumo_b.pasta) / projetos.ARQUIVO_ESTADO).read_bytes() == estado_b


def test_continuar_o_cartao_mais_recente_abre_ele(janela, pasta, monkeypatch):
    _livro, resumo_a, resumo_b = _dois_projetos_do_mesmo_livro(janela, pasta)
    monkeypatch.setattr(janela, "analisar", lambda: None)
    janela.tela_inicio.pedir_para_continuar(resumo_b)
    _analisar(janela)
    assert janela.resumo.pasta == resumo_b.pasta
    assert {p.filtro for p in janela.projeto.paginas} == {"preto_e_branco"}


def test_comecar_de_novo_limpa_e_abre_aquele_projeto(janela, pasta):
    """O "comecar de novo" do cartao de A apaga o trabalho de A (depois de
    perguntar) e abre A limpo - e nao o B."""
    _livro, resumo_a, resumo_b = _dois_projetos_do_mesmo_livro(janela, pasta)
    estado_b = (Path(resumo_b.pasta) / projetos.ARQUIVO_ESTADO).read_bytes()
    janela._recomecar_projeto(resumo_a)
    assert janela.resumo.pasta == resumo_a.pasta
    janela.close()
    assert (Path(resumo_b.pasta) / projetos.ARQUIVO_ESTADO).read_bytes() == estado_b


def test_abrir_pelo_abrir_continua_achando_o_mais_recente(janela, pasta):
    """O "Abrir" (sem cartao) continua o projeto mais recente do livro, como
    sempre fez."""
    livro, _resumo_a, resumo_b = _dois_projetos_do_mesmo_livro(janela, pasta)
    janela.abrir_livro(str(livro))
    assert janela.resumo.pasta == resumo_b.pasta


# --- a pergunta do fundo: uma vez por livro, inclusive nos que ja existem (item 1.1) ------
#
# Decisao do Samuel (29/09, Registro de mudancas): a pergunta "Este livro tem
# fundo separado. Quer tirar o fundo?" aparece UMA VEZ POR LIVRO, INCLUSIVE
# NOS QUE ELE JA TEM: na proxima vez que abrir (por qualquer caminho), e
# depois nao pergunta mais. Antes so aparecia em projeto novo. O projeto
# guarda que ja perguntou (Projeto.perguntou_fundo; projeto antigo sem o
# campo = ainda nao perguntou). "Nao" (e Esc, e X) tambem conta. Projeto
# antigo nunca vem com o fundo tirado sem a pessoa dizer "Sim".


def _pdf_com_fundo(pasta: Path, paginas: int = 3) -> Path:
    from tests.test_tirar_fundo_no_programa import _pdf_camadas

    (pasta / "livros").mkdir(exist_ok=True)
    return Path(_pdf_camadas(pasta / "livros", "Com Fundo.pdf", paginas=paginas))


def _responder(janela, sim: bool) -> None:
    caixa = janela.aviso_do_fundo
    assert caixa is not None, "nao perguntou"
    texto = "Sim, tirar o fundo" if sim else "Não, deixar como está"
    next(b for b in caixa.buttons() if b.text() == texto).click()
    assert janela.aviso_do_fundo is None


def _fechar_a_conferencia(janela) -> None:
    if janela.previas is not None:
        janela.previas.parar()
        janela.previas = None
    janela.tela_opcoes.folhear.fechar()


def _projeto_antigo_com_trabalho(janela, livro: Path) -> Path:
    """Um projeto como os que o Samuel ja tem: trabalho feito (pagina 2 em
    Magico pro, conferida), gravado ANTES do campo perguntou_fundo existir."""
    janela.abrir_livro(str(livro))
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    _analisar(janela)
    janela.projeto.paginas[1].filtro = MAGICO_PRO
    janela.projeto.paginas[1].revisada = True
    janela._salvar_agora()
    _fechar_a_conferencia(janela)
    estado = _estado(janela)
    dados = json.loads(estado.read_text(encoding="utf-8"))
    dados.pop("perguntou_fundo", None)                     # como antes de 29/09
    estado.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    return estado


def test_livro_novo_com_camadas_pergunta_uma_vez_so(janela, pasta):
    livro = _pdf_com_fundo(pasta)
    janela.abrir_livro(str(livro))
    _responder(janela, sim=False)
    janela.tela_opcoes.folhear.fechar()
    janela.abrir_livro(str(livro))                         # de novo, sem conferir
    assert janela.aviso_do_fundo is None, "perguntou de novo"
    _analisar(janela)
    _fechar_a_conferencia(janela)
    janela.abrir_livro(str(livro).replace("\\", "/"))      # pelo "Abrir"
    assert janela.aviso_do_fundo is None


def test_projeto_antigo_pergunta_na_proxima_abertura_e_nao_mais(janela, pasta):
    livro = _pdf_com_fundo(pasta)
    _projeto_antigo_com_trabalho(janela, livro)

    janela.abrir_livro(str(livro))
    assert janela.aviso_do_fundo is not None, "o projeto antigo nao perguntou"
    _responder(janela, sim=False)
    _analisar(janela)
    assert [p.filtro for p in janela.projeto.paginas] == ["original", MAGICO_PRO, "original"]
    _fechar_a_conferencia(janela)

    janela.abrir_livro(str(livro))
    assert janela.aviso_do_fundo is None, "perguntou de novo"
    _fechar_a_conferencia(janela)
    janela.close()
    assert projetos.carregar_estado(janela.resumo).perguntou_fundo is True


def test_projeto_antigo_pelo_continuar_tambem_pergunta(janela, pasta, monkeypatch):
    livro = _pdf_com_fundo(pasta)
    _projeto_antigo_com_trabalho(janela, livro)
    monkeypatch.setattr(janela, "analisar", lambda: None)
    janela._continuar_projeto(projetos.listar()[0])
    assert janela.aviso_do_fundo is not None
    _responder(janela, sim=False)
    janela.tela_opcoes.folhear.fechar()
    janela._continuar_projeto(projetos.listar()[0])
    assert janela.aviso_do_fundo is None


@pytest.mark.parametrize("como", ["nao", "esc", "x"])
def test_projeto_antigo_nao_esc_e_x_nao_mudam_nada(janela, pasta, como):
    livro = _pdf_com_fundo(pasta)
    estado = _projeto_antigo_com_trabalho(janela, livro)
    paginas_antes = json.loads(estado.read_text(encoding="utf-8"))["paginas"]

    janela.abrir_livro(str(livro))
    if como == "nao":
        _responder(janela, sim=False)
    elif como == "esc":
        janela.aviso_do_fundo.reject()
    else:
        janela.aviso_do_fundo.done(0)
    assert janela.aviso_do_fundo is None
    assert janela.projeto.filtro_padrao == "original"
    _analisar(janela)
    assert not janela.avisos
    janela.close()
    depois = json.loads(estado.read_text(encoding="utf-8"))
    assert depois["paginas"] == paginas_antes, "o trabalho mudou sem a pessoa dizer Sim"
    assert depois["perguntou_fundo"] is True, "Esc/X/Nao nao contou como perguntado"


def test_projeto_antigo_sim_troca_so_as_paginas_em_original_e_da_para_desfazer(janela, pasta):
    """Decisao do Samuel (29/09, f94f69b): o "Sim" num livro antigo troca SO
    as paginas que estao em "Original"; as que ele pos em outro filtro ficam.
    O desfazer devolve tambem o filtro do livro (print s17 do verificador)."""
    from core.filtros import TIRAR_FUNDO

    livro = _pdf_com_fundo(pasta)
    _projeto_antigo_com_trabalho(janela, livro)
    janela.abrir_livro(str(livro))
    _responder(janela, sim=True)
    _analisar(janela)

    assert [p.filtro for p in janela.projeto.paginas] == [TIRAR_FUNDO, MAGICO_PRO, TIRAR_FUNDO]
    assert janela.projeto.filtro_padrao == TIRAR_FUNDO
    assert janela.projeto.paginas[1].revisada, "o resto do trabalho se perdeu"
    assert not janela.avisos
    janela.tela_conferir.desfazer()                        # pelo Historico
    assert [p.filtro for p in janela.projeto.paginas] == ["original", MAGICO_PRO, "original"]
    assert janela.projeto.filtro_padrao == "original", "o desfazer nao devolveu o filtro do livro"
    janela.tela_conferir.refazer()
    assert janela.projeto.filtro_padrao == TIRAR_FUNDO
    janela.close()
    salvo = projetos.carregar_estado(janela.resumo)
    assert [p.filtro for p in salvo.paginas] == [TIRAR_FUNDO, MAGICO_PRO, TIRAR_FUNDO]
    assert salvo.filtro_padrao == TIRAR_FUNDO
    assert salvo.perguntou_fundo is True


def test_desfazer_o_sim_depois_de_reabrir_devolve_o_filtro_do_livro(janela, pasta):
    """O Historico vem do disco: desfazer o "Sim" numa sessao seguinte tambem
    devolve o filtro do livro."""
    livro = _pdf_com_fundo(pasta)
    _projeto_antigo_com_trabalho(janela, livro)
    janela.abrir_livro(str(livro))
    _responder(janela, sim=True)
    _analisar(janela)
    _fechar_a_conferencia(janela)
    janela.abrir_livro(str(livro))
    _analisar(janela)
    janela.tela_conferir.desfazer()
    assert janela.projeto.filtro_padrao == "original"
    assert [p.filtro for p in janela.projeto.paginas] == ["original", MAGICO_PRO, "original"]


def test_sim_respondido_durante_a_analise_do_continuar_vale(janela, pasta, monkeypatch):
    """Pelo "continuar", a analise comeca com a pergunta aberta: o "Sim"
    chega antes do trabalho carregar, e vale quando ele carrega."""
    from core.filtros import TIRAR_FUNDO

    livro = _pdf_com_fundo(pasta)
    _projeto_antigo_com_trabalho(janela, livro)
    monkeypatch.setattr(janela, "analisar", lambda: None)
    janela._continuar_projeto(projetos.listar()[0])
    _responder(janela, sim=True)
    _analisar(janela)
    assert [p.filtro for p in janela.projeto.paginas] == [TIRAR_FUNDO, MAGICO_PRO, TIRAR_FUNDO]


# Parecer do verificador, 3a rodada (30/09): pelo "continuar", a resposta dada
# DEPOIS do fim da analise era jogada fora (o projeto da tela ja era outro
# objeto), e o "Sim" seguido de fechar/voltar/cancelar antes de "Conferir" se
# perdia (so existia na memoria) e a pergunta nao voltava.


@pytest.mark.parametrize("sim", [True, False])
def test_resposta_depois_do_fim_da_analise_do_continuar_vale_e_fica_anotada(janela, pasta,
                                                                          monkeypatch, sim):
    from core.filtros import TIRAR_FUNDO

    livro = _pdf_com_fundo(pasta)
    _projeto_antigo_com_trabalho(janela, livro)
    monkeypatch.setattr(janela, "analisar", lambda: None)
    janela._continuar_projeto(projetos.listar()[0])
    _analisar(janela)                                      # a analise acaba antes
    _responder(janela, sim=sim)                            # da resposta (s19-s21)

    esperado = [TIRAR_FUNDO, MAGICO_PRO, TIRAR_FUNDO] if sim else ["original", MAGICO_PRO, "original"]
    assert [p.filtro for p in janela.projeto.paginas] == esperado
    janela.close()
    salvo = projetos.carregar_estado(janela.resumo)
    assert salvo.perguntou_fundo is True, "a resposta nao ficou anotada"
    assert [p.filtro for p in salvo.paginas] == esperado
    janela.abrir_livro(str(livro))
    assert janela.aviso_do_fundo is None, "perguntou de novo"


@pytest.mark.parametrize("como", ["fechar", "voltar", "cancelar"])
def test_sim_e_sair_antes_de_conferir_faz_a_pergunta_voltar(janela, pasta, como):
    """Projeto antigo: "Sim" e depois fechar, voltar para o inicio ou
    cancelar a analise, antes de o trabalho carregar. O "Sim" nao foi aplicado:
    nada muda no trabalho e a pergunta volta na proxima abertura (s23)."""
    livro = _pdf_com_fundo(pasta)
    estado = _projeto_antigo_com_trabalho(janela, livro)
    antes = json.loads(estado.read_text(encoding="utf-8"))

    janela.abrir_livro(str(livro))
    _responder(janela, sim=True)
    if como == "fechar":
        janela.close()
    elif como == "voltar":
        janela.tela_opcoes.voltar.emit()
    else:
        janela.analisar()
        janela.cancelar()
        _esperar_a_tarefa(janela)
    janela.tela_opcoes.folhear.fechar()

    depois = json.loads(estado.read_text(encoding="utf-8"))
    assert depois["paginas"] == antes["paginas"]
    assert not depois.get("perguntou_fundo"), "o Sim nao aplicado ficou como respondido"
    janela.abrir_livro(str(livro))
    assert janela.aviso_do_fundo is not None, "a pergunta nao voltou"


def test_sim_e_cancelar_e_conferir_de_novo_aplica_o_sim(janela, pasta):
    from core.filtros import TIRAR_FUNDO

    livro = _pdf_com_fundo(pasta)
    _projeto_antigo_com_trabalho(janela, livro)
    janela.abrir_livro(str(livro))
    _responder(janela, sim=True)
    janela.analisar()
    janela.cancelar()
    _esperar_a_tarefa(janela)
    _analisar(janela)
    assert [p.filtro for p in janela.projeto.paginas] == [TIRAR_FUNDO, MAGICO_PRO, TIRAR_FUNDO]


def test_livro_novo_sim_e_fechar_antes_de_conferir_guarda_o_sim(janela, pasta):
    """Livro novo (sem trabalho): o "Sim" vira o filtro do livro, gravado com
    as opcoes; fechar antes de "Conferir" nao o perde, e nao pergunta de novo."""
    from core.filtros import TIRAR_FUNDO

    livro = _pdf_com_fundo(pasta)
    janela.abrir_livro(str(livro))
    _responder(janela, sim=True)
    janela.close()
    janela.tela_opcoes.folhear.fechar()

    janela.abrir_livro(str(livro))
    assert janela.aviso_do_fundo is None
    assert janela.projeto.filtro_padrao == TIRAR_FUNDO
    _analisar(janela)
    assert [p.filtro for p in janela.projeto.paginas] == [TIRAR_FUNDO] * 3


def test_livro_sem_camadas_nunca_pergunta_nem_o_antigo(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    estado = _estado(janela)
    dados = json.loads(estado.read_text(encoding="utf-8"))
    dados.pop("perguntou_fundo", None)
    estado.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    janela.abrir_livro(str(livro))
    assert janela.aviso_do_fundo is None


def test_campo_novo_vai_e_volta_do_disco_e_projeto_antigo_vem_sem_perguntar():
    from modelos import Projeto

    assert Projeto(caminho_entrada="x.pdf").perguntou_fundo is False
    assert Projeto.de_dicionario({"caminho_entrada": "x.pdf"}).perguntou_fundo is False
    p = Projeto(caminho_entrada="x.pdf")
    p.perguntou_fundo = True
    assert Projeto.de_dicionario(p.para_dicionario()).perguntou_fundo is True


# --- "cancelar" devolve as opcoes de antes (verificador, 3a rodada, s34-s36) ---------------
#
# Mudar uma opcao em "O que fazer" (ex.: desmarcar "Dividir folhas ao meio"),
# "Conferir" e "cancelar": a conferencia antiga voltava, mas a opcao nova
# ficava no projeto e era gravada com as paginas de antes; na abertura
# seguinte a conferencia recomecava (com copia). Sonda:
# reproducoes/sonda3_opcao_e_cancelar.py.


def _deitado_conferido(janela, pasta: Path) -> Path:
    """Livro de 3 folhas deitadas, conferido com "Dividir" (6 paginas)."""
    livro = _pdf_deitado(pasta)
    janela.abrir_livro(str(livro))
    _analisar(janela)
    assert len(janela.projeto.paginas) == 6
    janela.projeto.paginas[1].filtro = MAGICO_PRO
    janela.projeto.paginas[1].revisada = True
    janela._salvar_agora()
    return livro


def test_cancelar_depois_de_mudar_uma_opcao_devolve_as_opcoes_de_antes(janela, pasta):
    from ui.janela_principal import CONFERIR

    livro = _deitado_conferido(janela, pasta)
    janela._sair_da_conferencia()
    janela.tela_opcoes.cx_dividir.setChecked(False)          # a pessoa muda
    assert janela.projeto.dividir_folhas is False
    janela.analisar()
    janela.cancelar()
    _esperar_a_tarefa(janela)

    assert janela.telas.currentIndex() == CONFERIR
    assert janela.projeto.dividir_folhas is True, "a opcao nova ficou no projeto"
    assert janela.tela_opcoes.cx_dividir.isChecked(), "a tela 'O que fazer' ficou com a nova"
    janela.projeto.paginas[2].filtro = "melhorar"
    janela.close()
    assert projetos.carregar_estado(janela.resumo).dividir_folhas is True

    _fechar_a_conferencia(janela)
    janela.abrir_livro(str(livro))
    _analisar(janela)
    assert not janela.avisos, janela.avisos                    # nao recomecou
    assert len(janela.projeto.paginas) == 6
    assert [janela.projeto.paginas[i].filtro for i in (1, 2)] == [MAGICO_PRO, "melhorar"]


def test_erro_na_analise_depois_de_mudar_uma_opcao_devolve_as_opcoes(janela, pasta,
                                                                    monkeypatch):
    import ui.janela_principal as modulo

    _deitado_conferido(janela, pasta)

    class AnaliseQueFalha:
        foi_cancelada = False

        def __init__(self, projeto):
            from unittest.mock import MagicMock
            self.progresso = self.concluida = self.falhou = MagicMock()

        def start(self):
            pass

        def isRunning(self):
            return False

        def cancelar(self):
            pass

    monkeypatch.setattr(modulo, "TarefaAnalise", AnaliseQueFalha)
    janela._sair_da_conferencia()
    janela.tela_opcoes.cx_dividir.setChecked(False)
    janela.analisar()
    janela._falhou_na_analise("Não consegui ler o livro.")
    assert janela.projeto.dividir_folhas is True
    assert janela.tela_opcoes.cx_dividir.isChecked()


def test_mudar_uma_opcao_e_conferir_ate_o_fim_continua_valendo(janela, pasta):
    """Sem cancelar, a opcao nova vale (recomeco com copia e aviso, como antes)."""
    _deitado_conferido(janela, pasta)
    janela._sair_da_conferencia()
    janela.tela_opcoes.cx_dividir.setChecked(False)
    _analisar(janela)
    assert len(janela.projeto.paginas) == 3
    assert janela.projeto.dividir_folhas is False
    assert janela.avisos and "Dividir folhas ao meio" in janela.avisos[0]


# --- "Tirar da lista" nao apaga as copias de seguranca (decisao do Samuel, 29/09) --------
#
# "'Tirar da lista' nao deve apagar as copias de seguranca (projeto.antigo-*),
# ou pelo menos deve avisar antes" (Registro de mudancas, f94f69b). Antes, a
# pasta inteira do projeto ia embora, com as copias dentro.


def _projeto_com_copias(janela, pasta: Path):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    resumo = projetos.ler_resumo(janela.resumo.pasta)
    copia = projetos.guardar_copia_do_trabalho(resumo)
    assert copia is not None
    return resumo, copia


def test_tirar_da_lista_guarda_as_copias_numa_pasta_a_parte(janela, pasta):
    import historico

    resumo, copia = _projeto_com_copias(janela, pasta)
    conteudo = copia.read_bytes()
    acoes = (Path(resumo.pasta) / "acoes.jsonl").read_bytes()

    guardadas = projetos.remover_da_lista(resumo)

    assert not Path(resumo.pasta).exists(), "o projeto nao saiu da lista"
    assert guardadas is not None and guardadas.is_dir()
    assert guardadas.is_relative_to(historico.pasta_de_dados() / "copias-de-seguranca")
    assert not guardadas.is_relative_to(projetos.pasta_dos_projetos())
    assert (guardadas / copia.name).read_bytes() == conteudo
    assert (guardadas / copia.name.replace("projeto.", "acoes.").replace(".json", ".jsonl")
            ).read_bytes() == acoes
    assert (guardadas / projetos.ARQUIVO_RESUMO).is_file(), "sem o resumo, nao se sabe de que livro e"
    assert (guardadas / "LEIA-ME.txt").read_text(encoding="utf-8")
    assert projetos.listar() == []                       # nao vira cartao


def test_tirar_da_lista_sem_copias_nao_cria_pasta(janela, pasta):
    import historico

    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    resumo = projetos.ler_resumo(janela.resumo.pasta)
    assert projetos.remover_da_lista(resumo) is None
    assert not Path(resumo.pasta).exists()
    assert not (historico.pasta_de_dados() / "copias-de-seguranca").exists()


def test_tirar_da_lista_duas_vezes_o_mesmo_nome_nao_sobrescreve(janela, pasta):
    resumo, _copia = _projeto_com_copias(janela, pasta)
    primeira = projetos.remover_da_lista(resumo)
    resumo2, _copia2 = _projeto_com_copias(janela, pasta)
    segunda = projetos.remover_da_lista(resumo2)
    assert primeira != segunda and primeira.is_dir() and segunda.is_dir()


def test_se_as_copias_nao_puderem_ser_guardadas_nada_e_apagado(janela, pasta, monkeypatch):
    import shutil as modulo_shutil

    resumo, copia = _projeto_com_copias(janela, pasta)

    def falha(*_a, **_k):
        raise OSError("disco cheio")

    monkeypatch.setattr(modulo_shutil, "copy2", falha)
    assert projetos.remover_da_lista(resumo) is None
    assert copia.is_file() and Path(resumo.pasta).is_dir(), "apagou sem guardar as copias"


def test_a_pergunta_de_tirar_da_lista_avisa_das_copias_e_esta_em_portugues(janela, pasta,
                                                                          monkeypatch):
    import ui.perguntas as perguntas

    resumo, _copia = _projeto_com_copias(janela, pasta)
    vistas = []

    def perguntar(pai, titulo, texto, sim="Sim", nao="Não", padrao_sim=False):
        vistas.append((titulo, texto, sim, nao, padrao_sim))
        return False

    monkeypatch.setattr(perguntas, "perguntar", perguntar)
    janela.tela_inicio.pedir_para_remover(resumo)
    assert Path(resumo.pasta).is_dir()                     # "Nao": nada muda
    titulo, texto, sim, nao, padrao_sim = vistas[0]
    assert "cópia" in texto and "não são apagadas" in texto
    assert sim != "Yes" and nao != "No" and not padrao_sim


# --- livro novo com camadas nao ganha copia de seguranca vazia (verificador, 30/09) -----


@pytest.mark.parametrize("sim", [True, False])
def test_livro_novo_com_camadas_nao_ganha_copia_vazia(janela, pasta, sim):
    livro = _pdf_com_fundo(pasta)
    janela.abrir_livro(str(livro))
    _responder(janela, sim=sim)               # grava um projeto.json so com as opcoes
    _analisar(janela)
    assert not _copias(Path(janela.resumo.pasta), "projeto"), "copia de um projeto sem trabalho"
    assert not janela.avisos


def test_comecar_de_novo_pergunta_em_portugues(janela, pasta, monkeypatch):
    import ui.perguntas as perguntas

    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    vistas = []
    monkeypatch.setattr(perguntas, "perguntar",
                        lambda pai, titulo, texto, sim="Sim", nao="Não", padrao_sim=False:
                        vistas.append((sim, nao, padrao_sim)) or False)
    janela.tela_inicio.pedir_para_recomecar(projetos.listar()[0])
    assert vistas and vistas[0][0] not in ("Yes", "Sim") and vistas[0][1] != "No"
    assert vistas[0][2] is False                  # o "nao" no Enter
    assert projetos.tem_trabalho_salvo(projetos.listar()[0])   # "nao": nada apagado
