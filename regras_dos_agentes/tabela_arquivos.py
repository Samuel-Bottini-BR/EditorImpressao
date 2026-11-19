"""A tabela "arquivos que o trabalho mexe → etiquetas das regras" (D-784; veio do esboço da proposta das regras).

Palavras do Samuel (D-784, 18/11): "ok, mas como vai saber que regras enviar para o agente?" · "ok". A resposta é esta
tabela, montada por programa, não pela memória da gerente.

Regras:
  1. Um arquivo recebe as etiquetas de TODAS as linhas cujo padrão casa com ele (não só a primeira).
  2. Linha de reserva (`RESERVA`: `core/*`, `*.md`, `docs/plano/*`, `teste_*.py`, `relatorios/*`) só vale quando
     nenhuma linha mais própria casou: assim `core/windows.py` é só Windows, e `core/filtros.py` é imagem.
  3. Além do nome, o conteúdo: se o arquivo (ou o pedido, para arquivo novo) tem uma das `PALAVRAS_DE_WINDOWS`, ganha
     WIN, mesmo que a tabela não diga (ex.: um script novo que chama o PowerShell).
  4. Arquivo que não casa com nenhuma linha recebe TODAS as etiquetas e a gerente é avisada (a tabela está atrasada).
     Um teste (`tests/test_conferencias_pacote.py`) cobra que todo arquivo do git tem linha.

Linhas novas do plano da parte do Windows (plano-v3, 19/11): o mostrador da troca (peça 11), os testes do publicar
(passo 2), as janelas de prova e o servidor das versões de prova (peça 10; o nome do arquivo ainda não existe, então o
padrão pega qualquer nome com "janela_de_prova" ou "servidor_das_versoes"), e os arquivos do próprio passo 0 (o pacote,
o gancho, as provas do porteiro e a lista de exceções), mais a pasta `.github/` que o teste do GitHub põe na cópia.

Seguro mexer: acrescentar linha. Arriscado: tirar linha ou etiqueta (o agente deixa de receber regra que precisa).
"""

from fnmatch import fnmatch
from pathlib import Path

from . import conversa_com_o_git as git

# (padrão, etiquetas, por quê) — padrões no jeito do fnmatch, com "/" mesmo no Windows.
TABELA = [
    # --- Windows, instalador, atualizador, publicar, testes à distância ---
    ("core/windows.py", ["WIN"], "o porteiro do Windows (arquivo novo do plano da parte do Windows)"),
    ("core/_testes_a_distancia_windows.py", ["WIN"], "pede licença ao Windows"),
    ("core/testes_a_distancia.py", ["WIN"], "planos de comandos do ligar, desligar e desfazer"),
    ("atualizacao.py", ["WIN"], "atualizador, ajudante, tarefas do Windows, desinstalar"),
    ("publicar_versao_kaique.py", ["WIN"], "publicar no GitHub com o Velopack"),
    ("empacotar.py", ["WIN"], "monta o pacote do Velopack e o instalador"),
    ("empacotar_teste_velocidade.py", ["WIN", "TESTE"], "empacota a medida de velocidade"),
    ("instalador.iss", ["WIN"], "instalador antigo (Inno Setup)"),
    ("assinatura.py", ["WIN"], "assinatura da versão para o Kaique"),
    ("versao.py", ["WIN"], "número da versão e nome do pacote (lugar único)"),
    ("montar_motor_kraken.py", ["WIN", "IMG"], "monta o Python à parte do Kraken"),
    ("motor_kraken/*", ["WIN", "IMG"], "o motor do Kraken"),
    ("main.py", ["TELA", "WIN"], "o começo do programa: primeira abertura, troca antes de abrir"),
    ("ui/aviso_de_atualizacao.py", ["TELA", "WIN"], "aviso de versão nova"),
    ("ui/testes_a_distancia_ui.py", ["TELA", "WIN"], "janela da senha dos testes à distância"),
    ("ui/tela_configuracoes.py", ["TELA", "WIN"], "Configurações, inclusive os testes à distância"),
    ("ui/tela_de_carregamento.py", ["TELA", "WIN"], "abre processo à parte (o brasão)"),
    ("compilar_*.py", ["IMG", "WIN"], "compila DLL do ScanTailor (chama o compilador)"),
    ("core/nativo/*", ["IMG", "WIN"], "DLLs compiladas: peça de fora"),
    ("core/paginas_em_outro_processo.py", ["IMG", "WIN"], "lança processo à parte"),
    ("core/ocr_*.py", ["IMG", "WIN"], "chama programas de fora (Tesseract, Kraken)"),
    ("ui/mostrador_da_troca.py", ["TELA", "WIN"], "o mostrador da troca de versão (plano-v3, peça 11)"),
    ("*janela_de_prova*", ["WIN", "TESTE"], "as janelas de prova do plano da parte do Windows (plano-v3, peça 10a)"),
    ("*servidor_das_versoes*", ["WIN", "TESTE"], "o servidor das versões de prova (plano-v3, peça 10b)"),
    # --- tela ---
    ("ui/*", ["TELA"], "telas"),
    ("ui/widgets/*", ["TELA"], "peças de tela"),
    ("atalhos.py", ["TELA"], "registro único dos atalhos de teclado"),
    ("brasao.py", ["TELA"], "medidas do brasão"),
    ("gerar_brasao.py", ["TELA"], "desenha o ícone e o giro"),
    ("recursos/*", ["TELA"], "imagens do programa"),
    ("arte/*", ["TELA"], "arte do brasão"),
    # --- processamento e imagem ---
    ("core/*", ["IMG"], "processamento do livro (o que não estiver acima)"),
    ("modelos.py", ["IMG", "TELA"], "modelo de dados: ConfigFolha e ConfigPagina (mexer pede pergunta, §6)"),
    ("projetos.py", ["IMG", "WIN"], "projetos salvos em %LOCALAPPDATA%"),
    ("historico.py", ["IMG", "TELA"], "lista de projetos da tela de início"),
    ("historico_acoes.py", ["IMG", "TELA"], "desfazer e refazer (mexer pede pergunta, §6)"),
    ("configuracoes.py", ["TELA", "WIN"], "preferências; hoje também marcas do atualizador"),
    ("registro.py", ["TODO"], "arquivo de log"),
    ("avaliar.py", ["IMG", "TESTE"], "a régua dos filtros"),
    ("avaliar_selecao.py", ["IMG", "TESTE"], "a régua da seleção"),
    ("montar_misto.py", ["IMG"], "monta o Misto"),
    ("rodada_*.py", ["IMG", "TESTE", "PERG"], "rodadas de comparação para o Samuel"),
    ("conferir_gravura_scantailor.py", ["IMG", "TESTE"], "confere a gravura contra o ScanTailor"),
    ("gabarito/*", ["IMG", "TESTE"], "páginas fixas de conferência (fora do git; junções!)"),
    ("terceiros/*", ["IMG", "PESQ"], "código de fora (ScanTailor): ler a licença"),
    # --- conferência e relatórios para o Samuel ---
    ("conferencia.py", ["IMG", "PERG"], "página de antes/depois"),
    ("conferir.py", ["IMG", "PERG"], "conferir amostras falando"),
    ("montar_para_conferir.py", ["IMG", "PERG"], "relatorios/para-conferir.html"),
    ("gerar_prints.py", ["IMG", "PERG"], "prints para o Samuel"),
    ("relatorio.py", ["PERG"], "grava os três formatos"),
    ("docs/plano/central/*", ["PERG", "GER"], "fonte da Central (só a gerente grava)"),
    ("docs/plano/para_a_*.py", ["PERG", "GER"], "scripts que alimentam as páginas"),
    # --- testes ---
    ("tests/*", ["TESTE"], "testes de máquina"),
    ("tests/conftest.py", ["TESTE", "TODO"], "vale para todos os testes: avisar a gerente"),
    ("tests/test_decisoes*.py", ["TESTE"], "provas das decisões (D-605: teste antigo não muda)"),
    ("tests/*atualizacao*", ["TESTE", "WIN"], ""),
    ("tests/*ajudante*", ["TESTE", "WIN"], ""),
    ("tests/*desinstalar*", ["TESTE", "WIN"], ""),
    ("tests/*testes_a_distancia*", ["TESTE", "WIN"], ""),
    ("tests/*empacotar*", ["TESTE", "WIN"], ""),
    ("tests/*assinatura*", ["TESTE", "WIN"], ""),
    ("tests/*nome_do_pacote*", ["TESTE", "WIN"], ""),
    ("tests/*windows*", ["TESTE", "WIN"], ""),
    ("tests/*publicar*", ["TESTE", "WIN"], "testes do publicar (plano-v3, passo 2)"),
    ("tests/test_conferencias_*", ["TESTE", "GER"], "as provas do porteiro (D-791)"),
    ("tests/conferencias_excecoes.json", ["TESTE", "GER"],
     "a lista de exceções: só diminui; item novo só com o 'sim' do Samuel, pela gerente (D-791)"),
    ("tests/*na_tela*", ["TESTE", "TELA"], ""),
    ("tests/*tela*", ["TESTE", "TELA"], ""),
    ("tests/*botoes*", ["TESTE", "TELA"], ""),
    ("tests/*menu*", ["TESTE", "TELA"], ""),
    ("tests/*paineis*", ["TESTE", "TELA"], ""),
    ("tests/*janela*", ["TESTE", "TELA"], ""),
    ("tests/promessas/*", ["TESTE", "TELA"], "promessas dos botões (D-010)"),
    ("teste_botoes.py", ["TESTE", "TELA"], "clica em botões de verdade"),
    ("teste_interface.py", ["TESTE", "TELA"], "dirige a lógica da tela"),
    ("teste_velocidade.py", ["TESTE", "IMG"], "medida de velocidade"),
    ("teste_*.py", ["TESTE", "IMG"], "testes soltos da raiz (geram relatório e imagem)"),
    ("rodar_suite_por_arquivo.py", ["TESTE"], "roda a suíte um arquivo por vez"),
    ("pasta_de_dados_dos_scripts.py", ["TESTE"], "pasta de dados dos scripts de teste"),
    ("requirements.txt", ["TODO", "PESQ"], "trocar ou acrescentar biblioteca pede pergunta (§6)"),
    # --- o pacote de regras, o porteiro e os testes no GitHub ---
    ("regras_dos_agentes/*", ["TESTE", "GER"], "o pacote de regras, o porteiro e o formulário (D-784, D-791, D-792)"),
    ("ganchos/*", ["TESTE", "GIT", "GER"], "a conferência antes do commit (a gerente liga, core.hooksPath)"),
    (".github/*", ["TESTE", "GIT"], "os testes no GitHub (a pasta vem do ramo dos testes e entra na cópia testada)"),
    # --- regras, plano, memória, git ---
    (".claude/agents/*", ["GER"], "regras dos agentes: só com o 'sim' do Samuel"),
    (".claude/skills/*", ["GER"], "skills do projeto"),
    (".claude/*", ["GER"], "outros arquivos do Claude Code (ex.: m.txt, settings)"),
    ("CLAUDE.md", ["GER"], "regras: só com o 'sim' do Samuel"),
    ("docs/plano/DECISOES.md", ["GER"], "o Livro: só a gerente escreve"),
    ("docs/plano/PLANO-DEFINITIVO.md", ["GER"], "o plano: só o Samuel muda"),
    ("docs/plano/*", ["GER", "PERG"], "plano e estado"),
    ("docs/pesquisa/*", ["PESQ"], "pesquisas"),
    ("memoria/*", ["GIT"], "memória do projeto (conferir_memoria.py depois)"),
    ("historico/*", ["GIT", "GER"], "handoff: só com pedido do Samuel"),
    ("velhos/*", ["GIT"], "histórico"),
    ("relatorios/*", ["PERG"], "relatórios (três formatos)"),
    ("ONDE-PAREI.md", ["GIT"], ""),
    ("PEDIDOS.md", ["GER"], "histórico desde 24/09"),
    ("PLANO-RETOMADA.md", ["GER"], "histórico"),
    ("LEIAME.md", ["GIT"], ""),
    (".gitignore", ["GIT", "GER"], "nunca desfazer sem avisar"),
    ("*.md", ["PERG"], "documento solto"),
]

# Palavras que, no conteúdo do arquivo, mostram conversa com o Windows ou com programa de fora.
PALAVRAS_DE_WINDOWS = [
    "subprocess", "ctypes", "ShellExecute", "runas", "powershell", "schtasks", "icacls", "Update.exe",
    "velopack", "winreg", "os.startfile", "CreateProcess", "DETACHED_PROCESS", "netsh", "sc.exe", "urllib", "requests.",
]

# Linhas "de reserva": só valem se nenhuma linha mais própria casou.
RESERVA = {"core/*", "*.md", "docs/plano/*", "teste_*.py", "relatorios/*"}

TODAS = ["TODO", "TELA", "WIN", "IMG", "PERG", "TESTE", "GIT", "PESQ"]


def etiquetas_do_arquivo(caminho: str, conteudo: str = "") -> tuple[set, list]:
    """As etiquetas de um arquivo e as linhas da tabela que casaram. Sem linha nenhuma: todas, e aviso."""
    caminho = caminho.replace("\\", "/")
    especificas = [(p, t) for p, t, _ in TABELA if p not in RESERVA and fnmatch(caminho, p)]
    reserva = [(p, t) for p, t, _ in TABELA if p in RESERVA and fnmatch(caminho, p)]
    # A linha de reserva (ex.: "core/*") só vale quando nenhuma linha própria casou: assim core/windows.py é só
    # Windows, e não Windows + imagem.
    casou = especificas or reserva
    tags = {t for _, ts in casou for t in ts}
    if any(p in conteudo for p in PALAVRAS_DE_WINDOWS):
        tags.add("WIN")
    if not casou:
        return set(TODAS), []
    return tags, [p for p, _ in casou]


def sem_linha(caminhos) -> list[str]:
    """Os arquivos que nenhuma linha da tabela pega (a tabela está atrasada para eles)."""
    return [c for c in caminhos if not etiquetas_do_arquivo(c)[1]]


def etiquetas_do_trabalho(arquivos: list[str], raiz: Path | str) -> tuple[set, list[str]]:
    """As etiquetas de um trabalho (a lista de arquivos do pedido) e os avisos de arquivo fora da tabela.

    Arquivo novo vem com "novo:" na frente (não há conteúdo para ler ainda). Uma pasta (termina em "/") vale por todos
    os arquivos que o git conhece nela; pasta nova vale pelo próprio nome. O lugar único dessa conta: o montador do
    pacote e o formulário da entrega chamam esta função.
    """
    raiz = Path(raiz)
    tags: set = set()
    avisos: list[str] = []
    conhecidos: list[str] | None = None
    for a in arquivos:
        novo = a.startswith("novo:")
        caminho = a.removeprefix("novo:").replace("\\", "/")
        alvos = [caminho]
        if caminho.endswith("/"):
            if conhecidos is None:
                conhecidos = git.arquivos_do_git(raiz)
            # Pasta que o git ainda não conhece (nova): vale como um arquivo qualquer dentro dela.
            alvos = [c for c in conhecidos if c.startswith(caminho)] or [caminho + "arquivo_novo"]
        for alvo in alvos:
            arquivo = raiz / alvo
            conteudo = "" if novo or not arquivo.is_file() else arquivo.read_text(encoding="utf-8", errors="replace")
            t, casou = etiquetas_do_arquivo(alvo, conteudo)
            if not casou:
                avisos.append(f"{alvo} não está na tabela: recebe todas as regras e a gerente é avisada")
            tags |= t
    tags.add("GIT")      # todo trabalho faz commit no seu ramo
    return tags, sorted(set(avisos))
