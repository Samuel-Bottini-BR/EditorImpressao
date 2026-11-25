"""O "conferido por fora" da prova à vista do atualizador novo: lê, sem mudar nada, como está a instalação, o que o
programa anotou e o que a fonte oferece. NÃO é parte do programa. SÓ LÊ (nenhuma licença, nenhuma janela).

python conferir_instalacao.py [linhas do registro, padrão 15]

O que mostra, cada coisa lida agora do disco ou do Windows (pelas mesmas funções que o programa usa, nunca por conta
própria: §11.12):
  - a versão instalada (`current\\sq.version`, a que o Velopack diz) e a de "Programas e Recursos" (o registro do
    Windows; o Velopack não consegue mudar esta sem licença, então ela fica na do .msi: é esperado);
  - a licença da pasta do programa (`core.windows.ler_licencas`): se Usuários podem modificar, e se veio herdada num
    arquivo de dentro de `current`;
  - o motor do Kraken no lugar (`atualizacao.motor_esta_no_lugar`, a conferência única do motor);
  - o atualizador do Velopack (`Update.exe`) no lugar;
  - `packages\\` e `ultima-boa\\` (os pacotes, as assinaturas, as marcas de aprovada);
  - o bilhete (`estado.json`: as reprovadas e a frase guardada), as frases já vistas nesta conta, e o fim do registro
    da atualização (`atualizacao.log`);
  - o fonte-de-teste.txt (o que diz e quem é o dono: tem de ser Administradores, S-1-5-32-544);
  - quem está rodando da pasta do programa.
"""
from __future__ import annotations

import json
import os
import sys
import winreg
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import prova_comum as comum  # noqa: E402

sys.path.insert(0, str(comum.RAMO))
import atualizacao  # noqa: E402
from core import windows  # noqa: E402

USUARIOS = "S-1-5-32-545"


def _versao_do_sq(raiz: Path) -> str:
    """A versão do `current\\sq.version` (o manifesto que o Velopack lê)."""
    try:
        texto = (raiz / "current" / "sq.version").read_text(encoding="utf-8-sig")
    except OSError:
        return "(não há current\\sq.version)"
    inicio = texto.find("<version>")
    fim = texto.find("</version>")
    return texto[inicio + 9:fim] if 0 <= inicio < fim else "(não li)"


def _programas_e_recursos() -> list[str]:
    """As entradas "Editor de Impressão" de Programas e Recursos (só leitura do registro do Windows)."""
    achadas = []
    for raiz, caminho in ((winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                          (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")):
        try:
            chave = winreg.OpenKey(raiz, caminho)
        except OSError:
            continue
        with chave:
            for i in range(winreg.QueryInfoKey(chave)[0]):
                nome = winreg.EnumKey(chave, i)
                try:
                    with winreg.OpenKey(chave, nome) as sub:
                        exibido = winreg.QueryValueEx(sub, "DisplayName")[0]
                        if "editor" in str(exibido).lower() and "impress" in str(exibido).lower():
                            try:
                                v = winreg.QueryValueEx(sub, "DisplayVersion")[0]
                            except OSError:
                                v = "?"
                            achadas.append(f"{exibido} {v} ({nome})")
                except OSError:
                    continue
    return achadas


def _licenca(caminho: Path) -> str:
    """Usuários podem modificar? Herdada ou própria? (pela peça do Windows)"""
    try:
        lidas = windows.ler_licencas(caminho)
    except OSError as erro:
        return f"não deu para ler ({erro})"
    dos_usuarios = [l for l in lidas.lista if l.sid == USUARIOS and l.tipo == "permite"]
    if not dos_usuarios:
        return "Usuários: nenhuma linha"
    return "; ".join(f"Usuários: {l.direitos()}{' (herdada)' if l.herdada else ' (própria)'}" for l in dos_usuarios)


def main(argumentos: list[str]) -> int:
    """Mostra tudo (ver o topo)."""
    linhas = int(argumentos[0]) if argumentos else 15
    raiz = comum.PROGRAMA
    print(f"== {raiz}")
    if not raiz.is_dir():
        print("   não está instalado")
    else:
        print(f"   versão em current\\sq.version: {_versao_do_sq(raiz)}")
        print(f"   licença da pasta do programa: {_licenca(raiz)}")
        um = raiz / "current" / "EditorImpressao.exe"
        print(f"   licença de current\\EditorImpressao.exe: {_licenca(um)}")
        print(f"   a pasta aceita gravação desta conta agora: {atualizacao.pasta_aceita_gravacao(raiz)}")
        print(f"   motor do Kraken no lugar (conferido): {atualizacao.motor_esta_no_lugar(raiz)}")
        print(f"   atualizador do Velopack (Update.exe) no lugar: {(raiz / 'Update.exe').is_file()}")
        for pasta in ("packages", atualizacao.PASTA_DA_ULTIMA_BOA, atualizacao.PASTA_DO_QUE_SE_INSTALA):
            try:
                nomes = sorted(p.name + (f" ({p.stat().st_size // 2**20} MB)" if p.is_file() else "\\")
                               for p in (raiz / pasta).iterdir())
            except OSError:
                nomes = ["(não existe)"]
            print(f"   {pasta}\\: {', '.join(nomes) or '(vazia)'}")
        print(f"   a última boa (lida como o programa lê): {atualizacao.ler_ultima_boa(raiz) or '(nenhuma)'}")
    print(f"== Programas e Recursos: {'; '.join(_programas_e_recursos()) or '(nenhuma entrada Editor de Impressão)'}")
    print(f"== quem roda da pasta do programa: {windows.programas_rodando_de(raiz) if raiz.is_dir() else '-'}")
    fonte = comum.FONTE_DE_TESTE
    if fonte.is_file():
        print(f"== fonte-de-teste.txt: \"{fonte.read_text(encoding='utf-8-sig').strip()}\"; dono "
              f"{windows.dono_do_arquivo(fonte)} (tem de ser S-1-5-32-544, Administradores)")
    else:
        print("== fonte-de-teste.txt: não existe (sem ele o programa procuraria no GitHub)")
    bilhete = atualizacao.ler_estado()
    print(f"== bilhete (estado.json): reprovadas {list(atualizacao.reprovadas_do_bilhete(bilhete))}; frase guardada "
          f"{atualizacao.frase_do_bilhete(bilhete)}")
    print(f"== frases já vistas nesta conta: {sorted(atualizacao.ler_vistos())}")
    registro = atualizacao.caminho_do_registro()
    print(f"== as últimas {linhas} linhas de {registro}:")
    try:
        for linha in registro.read_text(encoding="utf-8", errors="replace").splitlines()[-linhas:]:
            print(f"   {linha}")
    except OSError:
        print("   (ainda não existe)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
