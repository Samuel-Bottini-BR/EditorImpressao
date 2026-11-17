"""Compara duas fotografias do Windows (fotografo.py) e diz, em portugues simples,
o que sobrou, o que sumiu e o que mudou.

SO LE as duas fotos. Nao mexe no Windows.

Uso:
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe -I comparar.py <antes.json> <depois.json>

Codigo de saida: 0 = o Windows ficou igual (fora o que e so informativo, como o
espaco livre no disco e o que ja se esperava); 1 = ha diferencas a explicar.

"Esperado" quer dizer: combinado com o Samuel antes (o Editor de Impressao
antigo, de 01/09, sai na etapa 5; o registro do Velopack fica na pasta dele).
Cada diferenca esperada aparece mesmo assim, marcada, para o verificador
conferir e por na lista do que foi desfeito.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# O que ja se sabe que sai na etapa 5 (combinado com o Samuel em 16/11).
SINAIS_DO_EDITOR_ANTIGO = ("editor de impressao\\editorimpressao.exe", "{7c4e1b92-3a5d-4f18-9b6c-2e8a5d0f3c71}_is1",
                           "c:\\program files\\editor de impressao", "editor de impressao.lnk")
EXPLICACAO_DO_ANTIGO = "esperado: o Editor de Impressão antigo, de 01/09, sai (combinado com o Samuel)"


class Relatorio:
    def __init__(self) -> None:
        self.linhas: list[str] = []
        self.diferencas = 0
        self.esperadas = 0

    def secao(self, titulo: str) -> None:
        self.linhas.append("")
        self.linhas.append(f"== {titulo}")

    def diz(self, tipo: str, texto: str, esperado: str = "") -> None:
        if esperado:
            self.esperadas += 1
            self.linhas.append(f"  {tipo}: {texto}  ({esperado})")
        else:
            self.diferencas += 1
            self.linhas.append(f"  {tipo}: {texto}")

    def info(self, texto: str) -> None:
        self.linhas.append(f"  (só para saber) {texto}")

    def igual(self) -> None:
        self.linhas.append("  igual")


def _erro(valor) -> str | None:
    if isinstance(valor, dict) and "__erro" in valor:
        return str(valor["__erro"]).strip()
    return None


def _lista(valor) -> list:
    if valor is None or _erro(valor):
        return []
    if isinstance(valor, dict):
        return [valor]
    return list(valor)


def _esperado_do_antigo(texto: str) -> str:
    baixo = texto.lower()
    return EXPLICACAO_DO_ANTIGO if any(s in baixo for s in SINAIS_DO_EDITOR_ANTIGO) else ""


def comparar_por_chave(rel: Relatorio, titulo: str, antes, depois, chave, rotulo, campos, nome_do_item: str,
                       esperado=lambda _texto: "") -> None:
    rel.secao(titulo)
    for foto, valor in (("antes", antes), ("depois", depois)):
        if _erro(valor):
            rel.info(f"na foto de {foto} não deu para ler ({_erro(valor)[:120]})")
    a = {chave(x): x for x in _lista(antes) if isinstance(x, dict)}
    d = {chave(x): x for x in _lista(depois) if isinstance(x, dict)}
    mexeu = False
    for k in sorted(set(d) - set(a)):
        texto = f"{nome_do_item} {rotulo(d[k])}"
        rel.diz("SOBROU", f"{texto} (não existia antes)", esperado(texto))
        mexeu = True
    for k in sorted(set(a) - set(d)):
        texto = f"{nome_do_item} {rotulo(a[k])}"
        rel.diz("SUMIU", f"{texto} (existia antes)", esperado(texto))
        mexeu = True
    for k in sorted(set(a) & set(d)):
        for campo in campos:
            if a[k].get(campo) != d[k].get(campo):
                texto = f"{nome_do_item} {rotulo(a[k])}: {campo} era {a[k].get(campo)!r}, agora {d[k].get(campo)!r}"
                rel.diz("MUDOU", texto, esperado(texto))
                mexeu = True
    if not mexeu:
        rel.igual()


def comparar_pasta(rel: Relatorio, titulo: str, antes: dict, depois: dict, esperado=lambda _t: "") -> None:
    rel.secao(titulo)
    if antes.get("existe") != depois.get("existe"):
        if depois.get("existe"):
            rel.diz("SOBROU", f"a pasta {depois['caminho']} (não existia antes)", esperado(depois["caminho"]))
        else:
            rel.diz("SUMIU", f"a pasta {antes['caminho']} (existia antes)", esperado(antes["caminho"]))
    aa, da = antes.get("arquivos", {}), depois.get("arquivos", {})
    mexeu = antes.get("existe") != depois.get("existe")
    for nome in sorted(set(da) - set(aa)):
        rel.diz("SOBROU", f"o arquivo {nome} em {depois['caminho']}", esperado(nome))
        mexeu = True
    for nome in sorted(set(aa) - set(da)):
        rel.diz("SUMIU", f"o arquivo {nome} de {antes['caminho']}", esperado(nome))
        mexeu = True
    for nome in sorted(set(aa) & set(da)):
        if aa[nome] != da[nome]:
            rel.diz("MUDOU", f"o arquivo {nome} em {antes['caminho']} (tamanho ou data)", esperado(nome))
            mexeu = True
    for nome in sorted(set(depois.get("pastas", [])) - set(antes.get("pastas", []))):
        rel.diz("SOBROU", f"a subpasta {nome} em {depois['caminho']}", esperado(nome))
        mexeu = True
    for nome in sorted(set(antes.get("pastas", [])) - set(depois.get("pastas", []))):
        rel.diz("SUMIU", f"a subpasta {nome} de {antes['caminho']}", esperado(nome))
        mexeu = True
    for nome in sorted(set(antes.get("textos", {})) | set(depois.get("textos", {}))):
        if antes.get("textos", {}).get(nome) != depois.get("textos", {}).get(nome):
            rel.diz("MUDOU", f"o texto de {nome} em {antes['caminho']}", esperado(nome))
            mexeu = True
    if depois.get("sem_licenca"):
        rel.info(f"sem licença de ler na foto de depois: {len(depois['sem_licenca'])} itens")
    if not mexeu:
        rel.igual()


def comparar(antes: dict, depois: dict) -> Relatorio:
    rel = Relatorio()
    rel.linhas.append(f"Foto de antes:  {antes.get('quando')} (administrador: {'sim' if antes.get('com_administrador') else 'não'})")
    rel.linhas.append(f"Foto de depois: {depois.get('quando')} (administrador: {'sim' if depois.get('com_administrador') else 'não'})")
    if antes.get("com_administrador") != depois.get("com_administrador"):
        rel.linhas.append("ATENÇÃO: uma foto foi tirada com administrador e a outra sem. O que só o administrador vê "
                          "(o recurso OpenSSH, a pasta ssh, as tarefas do sistema) pode parecer que sobrou ou sumiu. "
                          "Tire as duas do mesmo jeito.")

    comparar_por_chave(rel, "Serviços do Windows (sshd e parecidos)", antes.get("servicos"), depois.get("servicos"),
                       lambda x: x.get("Name"), lambda x: x.get("Name"), ("State", "StartMode", "PathName"),
                       "o serviço")
    comparar_por_chave(rel, "Recurso do Windows OpenSSH", antes.get("openssh_recurso"), depois.get("openssh_recurso"),
                       lambda x: x.get("Name"), lambda x: x.get("Name"), ("State",), "o recurso")
    rel.secao("Arquivos do OpenSSH em System32")
    if antes.get("openssh_arquivos") != depois.get("openssh_arquivos"):
        rel.diz("MUDOU", f"era {antes.get('openssh_arquivos')}, agora {depois.get('openssh_arquivos')}")
    else:
        rel.igual()
    comparar_por_chave(rel, "Regras do firewall (todas)", antes.get("firewall_todas"), depois.get("firewall_todas"),
                       lambda x: x.get("Name"), lambda x: f"{x.get('Name')} ({x.get('DisplayName')})",
                       ("Enabled", "Direction", "Action"), "a regra")
    comparar_por_chave(rel, "Regras do firewall do ssh e do Editor (detalhe)", antes.get("firewall_detalhe"),
                       depois.get("firewall_detalhe"), lambda x: x.get("Name"), lambda x: x.get("Name"),
                       ("Enabled", "RemoteAddress", "InterfaceAlias", "LocalPort"), "a regra")
    comparar_por_chave(rel, "Contas do Windows", antes.get("contas"), depois.get("contas"),
                       lambda x: x.get("Name"), lambda x: x.get("Name"), ("Enabled", "Description", "SID"), "a conta")
    comparar_por_chave(rel, "Grupo Administradores", antes.get("administradores"), depois.get("administradores"),
                       lambda x: x.get("SID"), lambda x: x.get("Name"), (), "no grupo Administradores, a conta")
    comparar_por_chave(rel, "Grupo Usuários", antes.get("usuarios_grupo"), depois.get("usuarios_grupo"),
                       lambda x: x.get("SID"), lambda x: x.get("Name"), (), "no grupo Usuários, a conta")
    comparar_por_chave(rel, "Perfis das contas (pastas em C:\\Users)", antes.get("perfis"), depois.get("perfis"),
                       lambda x: x.get("SID"), lambda x: x.get("LocalPath"), ("LocalPath",), "o perfil")
    rel.secao("Contas escondidas da tela de entrada (UserList)")
    ua, ud = antes.get("userlist"), depois.get("userlist")
    if ua != ud:
        if ua is None:
            rel.diz("SOBROU", f"a chave UserList, com {ud} (não existia antes)")
        elif ud is None:
            rel.diz("SUMIU", "a chave UserList (existia antes)")
        else:
            rel.diz("MUDOU", f"a chave UserList era {ua}, agora {ud}")
    else:
        rel.igual()
    rel.secao("Pasta da conta de testes (C:\\Users\\EditorTestes)")
    if antes.get("perfil_da_conta_de_testes_existe") != depois.get("perfil_da_conta_de_testes_existe"):
        rel.diz("SOBROU" if depois.get("perfil_da_conta_de_testes_existe") else "SUMIU", "a pasta C:\\Users\\EditorTestes")
    else:
        rel.igual()

    comparar_pasta(rel, "C:\\ProgramData\\ssh", antes.get("programdata_ssh", {}), depois.get("programdata_ssh", {}))
    comparar_pasta(rel, "C:\\ProgramData\\EditorImpressao", antes.get("programdata_editor", {}),
                   depois.get("programdata_editor", {}))
    comparar_por_chave(rel, "Tarefas do Windows com EditorImpressao", antes.get("tarefas"), depois.get("tarefas"),
                       lambda x: (x.get("TaskPath"), x.get("TaskName")),
                       lambda x: f"{x.get('TaskPath')}{x.get('TaskName')}", ("State", "UserId", "Acoes"), "a tarefa")
    comparar_por_chave(rel, "Programas instalados", antes.get("programas_instalados"),
                       depois.get("programas_instalados"), lambda x: (x.get("onde"), x.get("chave")),
                       lambda x: f"\"{x.get('nome')}\" {x.get('versao')} [{x.get('chave')}] {x.get('pasta')}",
                       ("nome", "versao", "pasta"), "o programa", _esperado_do_antigo)
    comparar_por_chave(rel, "Atalhos com \"Editor\" no nome", antes.get("atalhos"), depois.get("atalhos"),
                       lambda x: x.get("caminho"), lambda x: f"{x.get('caminho')} -> {x.get('alvo', '')}",
                       ("alvo", "argumentos"), "o atalho", _esperado_do_antigo)

    rel.secao("Os projetos do Samuel (%LOCALAPPDATA%\\EditorImpressao)")
    pa, pd = antes.get("pasta_dos_projetos", {}), depois.get("pasta_dos_projetos", {})
    if pa.get("impressao_digital") == pd.get("impressao_digital"):
        rel.linhas.append(f"  igual: os mesmos {pd.get('quantos_arquivos')} arquivos, com os mesmos tamanhos e datas")
    else:
        rel.linhas.append("  ATENÇÃO: a pasta dos projetos mudou. Conferir um por um abaixo e, se for preciso, "
                          "devolver a cópia de reserva.")
        comparar_pasta(rel, "  (detalhe da pasta dos projetos)", pa, pd)
        rel.diferencas += 1

    for chave, titulo in (("programa_antigo", "O Editor antigo (C:\\Program Files\\Editor de Impressao)"),
                          ("programa_novo", "O Editor novo (C:\\Program Files\\EditorImpressao)")):
        rel.secao(titulo)
        a, d = antes.get(chave, {}), depois.get(chave, {})
        esp = EXPLICACAO_DO_ANTIGO if chave == "programa_antigo" else ""
        if a.get("existe") and not d.get("existe"):
            rel.diz("SUMIU", f"a pasta {a.get('caminho')} ({a.get('arquivos')} arquivos)", esp)
        elif d.get("existe") and not a.get("existe"):
            rel.diz("SOBROU", f"a pasta {d.get('caminho')} ({d.get('arquivos')} arquivos)")
        elif a.get("arquivos") != d.get("arquivos") or a.get("bytes") != d.get("bytes"):
            rel.diz("MUDOU", f"a pasta {a.get('caminho')}: {a.get('arquivos')} -> {d.get('arquivos')} arquivos")
        else:
            rel.igual()

    comparar_pasta(rel, "%LOCALAPPDATA%\\velopack (registro e pacotes do Velopack)",
                   antes.get("localappdata_velopack", {}), depois.get("localappdata_velopack", {}))

    rel.secao("Pastas novas ou sumidas no primeiro nível")
    mexeu = False
    for lugar in sorted(set(antes.get("primeiro_nivel", {})) | set(depois.get("primeiro_nivel", {}))):
        a = antes.get("primeiro_nivel", {}).get(lugar) or []
        d = depois.get("primeiro_nivel", {}).get(lugar) or []
        a, d = (a if isinstance(a, list) else []), (d if isinstance(d, list) else [])
        for nome in sorted(set(d) - set(a)):
            rel.diz("SOBROU", f"{lugar}\\{nome}", _esperado_do_antigo(f"c:\\program files\\{nome}"))
            mexeu = True
        for nome in sorted(set(a) - set(d)):
            rel.diz("SUMIU", f"{lugar}\\{nome}", _esperado_do_antigo(f"c:\\program files\\{nome}")
                    if lugar.lower() == "c:\\program files" else "")
            mexeu = True
    if not mexeu:
        rel.igual()

    rel.secao("Só para saber (não conta como diferença)")
    for chave, nome in (("tailscale", "a placa do Tailscale"), ("uac", "o jeito da pergunta do Windows"),
                        ("antivirus", "o antivírus"), ("disco_livre_gb", "o espaço livre (GB)")):
        if antes.get(chave) != depois.get(chave):
            rel.info(f"{nome}: era {antes.get(chave)}, agora {depois.get(chave)}")
        else:
            rel.info(f"{nome}: igual")

    rel.linhas.append("")
    if rel.diferencas == 0:
        rel.linhas.append(f"RESULTADO: o Windows ficou como antes ({rel.esperadas} diferença(s) esperada(s), marcadas acima).")
    else:
        rel.linhas.append(f"RESULTADO: {rel.diferencas} diferença(s) a explicar e {rel.esperadas} esperada(s).")
    return rel


def main() -> int:
    if len(sys.argv) != 3:
        print("uso: python -I comparar.py <antes.json> <depois.json>")
        return 2
    antes = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    depois = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    rel = comparar(antes, depois)
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(rel.linhas))
    return 0 if rel.diferencas == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
