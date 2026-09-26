"""Empacotamento do teste de velocidade (item 0.6): o que tem resposta certa.

O PyInstaller em si nao roda aqui (leva minutos); o proprio
empacotar_teste_velocidade.py confere o pacote que gera. Aqui fica o que
protege as decisoes que nao sao gosto: pacote em pasta e com janela preta, o
modelo no lugar em que o codigo o procura, as mesmas opcoes do programa de
verdade, o .bat e as instrucoes coerentes com o que o teste escreve na tela.

O .bat se reabre na janela preta classica (decisao do Samuel, 25/09/2026; ver
TEXTO_DO_BAT): o texto dele e conferido linha a linha, e ele tambem RODA de
verdade aqui, nos caminhos que nao abrem janela (sem o conhost, o relancado e
sem o .exe), numa pasta com espaco, acento, &, parenteses e %. O relancamento
em si, que abre a janela classica, foi conferido a mao (ver o relatorio da
tarefa); teste automatico nenhum abre janela.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import empacotar
import empacotar_teste_velocidade as ep
import teste_velocidade as tv


def _valor_de(comando: list[str], opcao: str) -> list[str]:
    return [comando[i + 1] for i, item in enumerate(comando) if item == opcao]


def test_pacote_em_pasta_e_com_janela_preta():
    """Arquivo unico se desempacota a cada abertura (o tempo entraria na
    medicao) e quebra o 'Aperte Enter' do fim; sem console nao ha progresso."""
    comando = ep.comando_do_pyinstaller()

    assert "--onedir" in comando and "--console" in comando
    assert "--onefile" not in comando and "--windowed" not in comando
    assert "--noconsole" not in comando


def test_modelo_vai_para_onde_o_codigo_empacotado_procura():
    """core/detectar_regioes.py procura o modelo em <pasta acima de core>/
    modelos/. Empacotado, core/ mora em _internal/, entao o modelo tem de ir
    para _internal/modelos/ - que e o que '--add-data ...;modelos' faz."""
    from core import detectar_regioes

    raiz_do_codigo = Path(detectar_regioes.__file__).resolve().parent.parent
    assert detectar_regioes.CAMINHO_MODELO == raiz_do_codigo / "modelos" / ep.MODELO.name

    dados = _valor_de(ep.comando_do_pyinstaller(), "--add-data")
    assert f"{ep.MODELO}{';' if sys.platform == 'win32' else ':'}modelos" in dados
    assert _valor_de(ep.comando_do_pyinstaller(), "--contents-directory") == [ep.INTERNO]


def test_mesmas_opcoes_do_programa_de_verdade():
    comando = ep.comando_do_pyinstaller()

    assert set(empacotar.EXCLUIR) <= set(_valor_de(comando, "--exclude-module"))
    assert set(empacotar.OCULTOS) <= set(_valor_de(comando, "--hidden-import"))
    assert "scipy" not in _valor_de(comando, "--exclude-module"), (
        "o programa precisa do scipy (o .spec velho tirava)")


def test_caminhos_absolutos_no_comando():
    """Com --specpath, o PyInstaller le caminho relativo a partir da pasta do
    .spec: o script ou o modelo sumiriam."""
    comando = ep.comando_do_pyinstaller()

    assert Path(comando[-1]).is_absolute() and comando[-1].endswith("teste_velocidade.py")
    assert ep.MODELO.is_absolute()


def test_o_livro_do_pacote_e_o_que_o_teste_procura():
    assert ep.LIVRO.name == tv.NOME_DO_LIVRO


def test_bat_so_tem_acento_depois_do_chcp():
    """Antes do 'chcp 65001' o cmd le o arquivo na pagina de codigo antiga:
    acento ali sairia estragado."""
    linhas = ep.TEXTO_DO_BAT.splitlines()
    chcp = next(i for i, linha in enumerate(linhas) if linha.startswith("chcp 65001"))

    assert all(linha.isascii() for linha in linhas[:chcp])
    assert not ep.TEXTO_DO_BAT.startswith("﻿")
    assert linhas[0] == "@echo off"


def test_bat_roda_o_exe_certo_passa_as_opcoes_e_segura_a_janela():
    """As opcoes escritas depois do nome do .bat (ex.: --rapido) chegam ao
    .exe pela variavel, e nao por %* direto: no .bat reaberto, %* e so a
    marca (ver TEXTO_DO_BAT)."""
    texto = ep.TEXTO_DO_BAT

    assert f"set {ep.VARIAVEL_DAS_OPCOES}=%*" in _linhas_do_bat()
    assert f'"%~dp0{ep.NOME}.exe" %{ep.VARIAVEL_DAS_OPCOES}%' in _linhas_do_bat()
    assert texto.count("pause") >= 2, "no fim normal e quando falta o programa"
    assert "Extrair tudo" in texto


# ---------------------------------------------------------------------------
# o .bat se reabre na janela classica (decisao do Samuel, 25/09/2026)
# ---------------------------------------------------------------------------

# As duas conferencias do comeco do .bat, na ordem em que devem vir.
_CONFERE_O_EXE = f'if not exist "%~dp0{ep.NOME}.exe" goto sem_programa'
_CONFERE_A_MARCA = f'if "%~1"=="{ep.MARCA_DA_JANELA_CLASSICA}" goto medir'


def _linhas_do_bat() -> list[str]:
    return ep.TEXTO_DO_BAT.splitlines()


def _linha_do_start() -> str:
    """A linha que reabre o .bat pelo conhost: uma so."""
    linhas = [linha for linha in _linhas_do_bat() if linha.startswith("start ")]
    assert len(linhas) == 1, "um relancamento so"
    return linhas[0]


def _onde(linha: str) -> int:
    """Em que linha do .bat esta `linha` (a linha inteira, exata)."""
    return _linhas_do_bat().index(linha)


def test_bat_se_reabre_pelo_conhost_e_sai():
    """O conhost.exe chamado com uma linha de comando abre sempre a janela
    classica: ele nunca a passa para o Terminal novo. Depois de reabrir, esta
    janela sai (exit /b 0: na configuracao de fabrica, o Terminal novo fecha
    sozinho quando o programa sai com 0)."""
    start = _linha_do_start()

    assert ep.CONHOST == r"%SystemRoot%\System32\conhost.exe"
    assert start.startswith(f'start "" "{ep.CONHOST}" cmd.exe /c ')
    assert _linhas_do_bat()[_onde(start) + 1] == "exit /b 0"


def test_bat_reaberto_nao_se_reabre_de_novo():
    """A marca vem antes do relancamento: sem ela, cada janela nova abriria
    outra, sem fim. E e a mesma marca que o relancamento manda."""
    assert _onde(_CONFERE_A_MARCA) < _onde(_linha_do_start())
    assert _linha_do_start().split(" || ")[0].endswith(f" {ep.MARCA_DA_JANELA_CLASSICA}")
    assert ":medir" in _linhas_do_bat()


def test_nada_do_que_vai_ao_conhost_muda_quando_ele_refaz_as_aspas():
    """O conhost separa a linha que recebe em pedacos e refaz as aspas de
    cada um do jeito dos programas em C (EscapeArgument, com barras), que o
    cmd nao entende: um caminho com espaco chegaria estragado. Por isso, depois
    do conhost.exe, so pedacos sem espaco, sem aspas e sem barra, que ele
    repassa como estao. O caminho do .bat e as opcoes vao em variaveis."""
    start = _linha_do_start()
    depois_do_conhost = start.split(f'"{ep.CONHOST}"', 1)[1].split(" || ")[0].split()

    assert depois_do_conhost == ["cmd.exe", "/c", f"%%{ep.VARIAVEL_DO_BAT}%%",
                                 ep.MARCA_DA_JANELA_CLASSICA]
    assert ep.MARCA_DA_JANELA_CLASSICA.isascii()
    for pedaco in ("%~f0", "%~dp0", "%0", "%*"):
        assert pedaco not in start, pedaco


def test_caminho_do_bat_vai_para_a_variavel_ja_com_as_aspas():
    """As aspas vao DENTRO da variavel: o cmd reaberto olha as aspas da linha
    antes de abrir a variavel, e o caminho (espaco, acento, parenteses, &)
    chega inteiro, entre aspas."""
    assert _onde(f'set {ep.VARIAVEL_DO_BAT}="%~f0"') < _onde(_linha_do_start())


def test_bat_reaberto_usa_as_opcoes_da_primeira_janela():
    """As opcoes sao guardadas so na primeira janela (depois da marca): no
    .bat reaberto, %* e a marca, e ela nao pode ir para o .exe."""
    guarda = f"set {ep.VARIAVEL_DAS_OPCOES}=%*"

    assert _onde(_CONFERE_A_MARCA) < _onde(guarda) < _onde(_linha_do_start())


def test_plano_b_mede_na_janela_em_que_estiver():
    """Sem o conhost.exe, ou se o start falhar, mede ali mesmo, sem cair. O
    "||" fica na MESMA linha do start, e nunca um "if errorlevel" depois dele:
    o start que da certo nao zera o ERRORLEVEL (visto no PC do Samuel,
    25/09/2026), e o teste rodaria nas duas janelas ao mesmo tempo."""
    start = _linha_do_start()

    assert _onde(f'if not exist "{ep.CONHOST}" goto medir') < _onde(start)
    assert start.endswith(" || goto medir")
    assert not any("errorlevel" in linha.lower() and linha.lower().startswith("if ")
                   for linha in _linhas_do_bat())


def test_bat_confere_o_exe_antes_de_se_reabrir():
    """Sem o .exe nao ha o que medir: o aviso de extrair o .zip sai na janela
    que abriu, sem reabrir (aberto de dentro do .zip, sem extrair, o Windows
    copia so o .bat para uma pasta temporaria)."""
    assert _onde(_CONFERE_O_EXE) < _onde(_CONFERE_A_MARCA) < _onde(_linha_do_start())


def test_bat_sem_bloco_entre_parenteses():
    """O cmd le um bloco entre parenteses inteiro de uma vez, e um ")" que
    venha do nome da pasta ("TesteVelocidade-notebook-do-Kaique (1)", quando o
    .zip e baixado duas vezes) fecharia o bloco no meio. Sem bloco nenhum,
    esse risco nao existe. Comentario (rem) pode ter parenteses."""
    for linha in _linhas_do_bat():
        if linha.lower().startswith("rem "):
            continue
        assert "(" not in linha and ")" not in linha, linha


# ---------------------------------------------------------------------------
# o .bat de verdade, sem abrir janela nenhuma
# ---------------------------------------------------------------------------

so_no_windows = pytest.mark.skipif(sys.platform != "win32", reason="o .bat so roda no Windows")

# Espaco, acento, &, parenteses e %: o que o nome do usuario e uma pasta
# extraida duas vezes podem trazer.
_CAMINHO_DIFICIL = ("Kaíque Silva", "Área de Trabalho", "TesteVelocidade & Cia 100% (1)")


def _pasta_extraida(tmp_path: Path, monkeypatch, com_exe: bool = True) -> Path:
    """A pasta como o Kaique a extrai, num caminho dificil, com o .bat
    gravado por escrever_os_textos (o mesmo do pacote). No lugar do
    TesteVelocidade.exe vai uma copia do cmd.exe, que nao mede nada: so faz o
    que as opcoes mandarem (echo, exit). Devolve o caminho do .bat."""
    pasta = tmp_path.joinpath(*_CAMINHO_DIFICIL)
    pasta.mkdir(parents=True)
    monkeypatch.setattr(ep, "PASTA", pasta)
    monkeypatch.setattr(ep, "DIST", tmp_path)
    bat, _instrucoes = ep.escrever_os_textos()
    if com_exe:
        shutil.copy2(Path(os.environ["SystemRoot"]) / "System32" / "cmd.exe",
                     pasta / f"{ep.NOME}.exe")
    return bat


def _sem_conhost(tmp_path: Path, **variaveis: str) -> dict:
    """O ambiente com um SystemRoot onde nao ha conhost.exe: o .bat cai no
    plano B, e NENHUMA janela abre, mesmo que algo errado tente reabrir."""
    ambiente = {nome: valor for nome, valor in os.environ.items()
                if nome.upper() != "SYSTEMROOT"}
    ambiente["SystemRoot"] = str(tmp_path / "Windows-sem-conhost")
    ambiente.update(variaveis)
    return ambiente


def _rodar(comando: str, ambiente: dict) -> tuple[int, str]:
    """Roda sem janela (CREATE_NO_WINDOW), com um Enter para o pause.
    Devolve (codigo de saida, o que saiu na tela). A tela sai em UTF-8 porque
    o proprio .bat troca a pagina de codigo (chcp 65001)."""
    feito = subprocess.run(comando, env=ambiente, input=b"\r\n", capture_output=True,
                           timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
    return feito.returncode, feito.stdout.decode("utf-8", "replace")


@so_no_windows
def test_bat_de_verdade_sem_conhost_mede_ali_mesmo_com_as_opcoes(tmp_path, monkeypatch):
    bat = _pasta_extraida(tmp_path, monkeypatch)

    codigo, tela = _rodar(f'cmd.exe /d /c ""{bat}" /d /c echo OPCOES-CHEGARAM "com espaço""',
                          _sem_conhost(tmp_path))

    assert 'OPCOES-CHEGARAM "com espaço"' in tela
    assert codigo == 0


@so_no_windows
def test_bat_de_verdade_sai_com_o_codigo_do_exe(tmp_path, monkeypatch):
    bat = _pasta_extraida(tmp_path, monkeypatch)

    codigo, _tela = _rodar(f'cmd.exe /d /c ""{bat}" /d /c exit 7"', _sem_conhost(tmp_path))

    assert codigo == 7


@so_no_windows
def test_bat_reaberto_de_verdade_acha_o_caminho_e_as_opcoes(tmp_path, monkeypatch):
    """A linha que o conhost repassa ao cmd, tirada do proprio .bat e rodada
    como o conhost a roda: o caminho dificil chega inteiro pela variavel, a
    marca impede outro relancamento e as opcoes sao as da primeira janela.
    (Se a marca falhasse, o .exe receberia a marca no lugar das opcoes.)"""
    bat = _pasta_extraida(tmp_path, monkeypatch)
    linha_do_conhost = (_linha_do_start().split(f'"{ep.CONHOST}" ', 1)[1]
                        .split(" || ")[0].replace("%%", "%"))
    ambiente = _sem_conhost(tmp_path, **{
        ep.VARIAVEL_DO_BAT: f'"{bat}"',
        ep.VARIAVEL_DAS_OPCOES: '/d /c echo OPCOES-DA-PRIMEIRA-JANELA "com espaço"',
    })

    codigo, tela = _rodar(linha_do_conhost, ambiente)

    assert 'OPCOES-DA-PRIMEIRA-JANELA "com espaço"' in tela
    assert codigo == 0


@so_no_windows
def test_bat_de_verdade_sem_o_exe_avisa_para_extrair_o_zip(tmp_path, monkeypatch):
    bat = _pasta_extraida(tmp_path, monkeypatch, com_exe=False)

    codigo, tela = _rodar(f'cmd.exe /d /c ""{bat}""', _sem_conhost(tmp_path))

    assert "Extraia o .zip inteiro primeiro" in tela
    assert codigo == 1


def test_instrucoes_citam_a_frase_que_o_teste_mostra_no_fim():
    """Se a frase do programa mudar, as instrucoes tem de mudar junto: o
    Kaique procura exatamente o que o papel manda procurar."""
    assert tv.mensagem_do_fim(0) in ep.TEXTO_DAS_INSTRUCOES


def test_instrucoes_mantem_o_aviso_de_nao_clicar_na_janela_preta():
    """O teste desliga a edicao rapida da janela preta (um clique comum nao
    pausa mais a medicao), mas o aviso fica: ha jeitos de pausar que o teste
    nao impede (ver edicao_rapida_desligada em teste_velocidade.py)."""
    assert "não clique dentro da janela preta" in ep.TEXTO_DAS_INSTRUCOES


def test_instrucoes_avisam_que_uma_janela_pode_piscar_antes():
    """O .bat se reabre na janela classica: a janela em que ele abriu pisca e
    fecha (ver TEXTO_DO_BAT). O Kaique le isso no passo de dar os dois
    cliques, para nao achar que deu errado."""
    texto = ep.TEXTO_DAS_INSTRUCOES
    passo = texto[texto.index("\n6. "):texto.index("\n7. ")]

    assert "RODAR O TESTE" in passo
    assert "pisca" in passo and "fecha" in passo and "normal" in passo


def test_instrucoes_tem_os_passos_combinados():
    texto = ep.TEXTO_DAS_INSTRUCOES

    for pedaco in (ep.ZIP.name, "Área de Trabalho", "Extrair tudo", "pendrive",
                   "tomada", "Melhor desempenho", "RODAR O TESTE",
                   "O Windows protegeu o computador", "Mais informações",
                   "Executar assim mesmo", "não use o notebook", "resultados",
                   "não instala nada"):
        assert pedaco.lower() in texto.lower(), pedaco
    assert ep.PASTA_EXTRAIDA == "TesteVelocidade-notebook-do-Kaique"
    assert max(len(linha) for linha in texto.splitlines()) <= 80, "cabe no Bloco de Notas"


def test_textos_gravados_com_a_codificacao_certa(tmp_path, monkeypatch):
    """O .bat sem BOM (quebraria o @echo off), as instrucoes com BOM (o Bloco
    de Notas de qualquer Windows le o acento), os dois com fim de linha do
    Windows."""
    monkeypatch.setattr(ep, "PASTA", tmp_path / "TesteVelocidade")
    monkeypatch.setattr(ep, "DIST", tmp_path)
    ep.PASTA.mkdir()

    bat, instrucoes = ep.escrever_os_textos()

    dados_bat = bat.read_bytes()
    assert dados_bat.startswith(b"@echo off\r\n")
    assert b"\r\n" in dados_bat and b"\n" not in dados_bat.replace(b"\r\n", b"")
    assert len(instrucoes) == 2
    for caminho in instrucoes:
        dados = caminho.read_bytes()
        assert dados.startswith(b"\xef\xbb\xbf")
        assert b"\n" not in dados.replace(b"\r\n", b"")
        assert "Área de Trabalho" in dados.decode("utf-8-sig")


def test_nao_apaga_resultados_de_um_teste_que_ja_rodou(tmp_path, monkeypatch):
    monkeypatch.setattr(ep, "PASTA", tmp_path / "TesteVelocidade")
    resultado = ep.PASTA / "resultados" / "velocidade-NOTEBOOK.md"
    resultado.parent.mkdir(parents=True)
    resultado.write_text("medido", encoding="utf-8")

    with pytest.raises(ep.ErroNoPacote):
        ep.limpar_o_anterior()
    assert resultado.read_text(encoding="utf-8") == "medido"


def _dll_do_python() -> Path | None:
    """A DLL do Python desta instalacao (python314.dll), que pede o Visual
    C++. Nao serve o python3.dll: ele so repassa chamadas e nao pede nada."""
    dll = Path(sys.base_prefix) / f"python{sys.version_info.major}{sys.version_info.minor}.dll"
    return dll if dll.is_file() else None


def test_le_as_dlls_que_um_executavel_de_verdade_pede():
    """A DLL do Python pede o vcruntime140.dll: e o que prova que a leitura
    funciona (se ela devolvesse vazio, a conferencia passaria sempre)."""
    python_dll = _dll_do_python()
    if python_dll is None:
        pytest.skip("sem a DLL do Python nesta instalacao")

    assert "vcruntime140.dll" in ep._dlls_que_o_arquivo_pede(python_dll)


def test_visual_c_pedidas_inclui_as_tres_e_quem_pede(tmp_path):
    import shutil

    python_dll = _dll_do_python()
    if python_dll is None:
        pytest.skip("sem a DLL do Python nesta instalacao")
    shutil.copy2(python_dll, tmp_path / python_dll.name)
    (tmp_path / "leia-me.txt").write_text("nao e executavel", encoding="utf-8")

    pedidas = ep.dlls_do_visual_c_pedidas(tmp_path)

    assert set(ep.DLLS_DO_VISUAL_C) <= set(pedidas)
    assert pedidas["vcruntime140.dll"] == [python_dll.name]


def test_caminho_mais_longo(tmp_path):
    fundo = tmp_path / "a" / "bb" / "ccc.txt"
    fundo.parent.mkdir(parents=True)
    fundo.write_text("x", encoding="utf-8")

    letras, qual = ep.caminho_mais_longo(tmp_path)

    assert qual == str(Path("a") / "bb" / "ccc.txt")
    assert letras == len(qual)
