"""A peça única do Velopack: o único arquivo do programa que importa a biblioteca `velopack` (atualizador novo, 23/11/2026).

POR QUE UMA PEÇA SÓ (CLAUDE.md §11.12, ponto 1): o Velopack é uma peça de fora que mexe na pasta do programa. Quem
procura, baixa e troca chama estas funções; ninguém mais cria o `UpdateManager`. A trava dos donos
(`tests/test_trava_windows.py`, capacidade "Velopack") cobra que nenhum outro arquivo do programa importa `velopack`, e
um teste lê a árvore e cobra que só `trocar` chama a troca (`wait_exit_then_apply_updates`).

O QUE CADA FUNÇÃO FAZ NO VELOPACK 1.2.161 (lido no código da etiqueta `1.2.161`, commit `92d6a1c`; o caminho é o do
repositório do Velopack; a seção "Leitura das peças de fora" do ONDE-PAREI tem o resto):
- `atender_ganchos`: `VelopackApp.run()` (`src/lib-rust/src/app.rs`, `run`): com `--veloapp-install`/`-updated`/
  `-obsolete`/`-uninstall` na linha de comando chama o gancho e o processo sai; senão cria o localizador (que testa se a
  raiz grava, `locator.rs` 152-176), põe o nome do programa na barra de tarefas e limpa pacotes velhos. Com
  `set_auto_apply_on_startup(False)` NUNCA troca sozinho na abertura (sem isso, um "Não" ao fechar trocaria na abertura
  seguinte: `app.rs` 180-191).
- `procurar`: `check_for_updates` lê o índice publicado; levanta sem internet. No GitHub lê só os 10 "Releases" mais
  novos (`sources/github.rs` 80, `per_page=10`).
- `baixar`: `download_updates` pega a tranca do Velopack (`.velopack_lock` em `packages\\`; falha se outra janela do
  programa está baixando, `manager.rs` 406), baixa para `<nome>.partial`, confere o TAMANHO e a soma SHA256 do índice
  (`verify_package_checksum`, `manager.rs` 537-561), dá o nome final, tira o `Update.exe` novo de dentro do pacote e
  apaga os pacotes velhos de `packages\\`. ATENÇÃO: se o arquivo final já existe, NÃO baixa nem confere nada
  (`manager.rs` 413-416). Por isso quem troca confere a soma assinada do arquivo antes (`atualizacao.trocar_para`).
- `pendente`: `get_update_pending_restart` (manager.rs 272-281): o pacote completo mais novo de `packages\\` que é
  maior que a versão que roda; só disco.
- `pacote_da_versao`: monta, sem rede, o pedido de uma versão escolhida por nós (o pacote esperando, sem internet,
  D-859): `VelopackAsset` e `UpdateInfo` se montam pelo Python (`__init__.pyi`). (Volta 5: a volta pela última boa, que
  também o usava, saiu com a volta automática, D-867.)
- O pacote da versão que roda fica em `packages\\`: a abertura (`VelopackApp.run`) apaga os outros e guarda o da
  versão atual e o que está esperando (`app.rs`, `cleanup_old_packages_from_list`). O `Setup.exe` põe o primeiro
  (`bins/src/commands/install.rs`, "Copying nupkg to packages directory"); o .msi, o NOSSO instalador, não põe nada em
  `packages\\` (o .msi instala a pasta portátil: `WindowsPackCommandRunner.cs` 230-243; lido nas tabelas do nosso .msi
  da 1.1.0). É dali que a última boa é copiada; sem ele lá, nada é baixado (D-857: a primeira versão do .msi não é
  testada nem guardada).
- `trocar`: `wait_exit_then_apply_updates` (`manager.rs` 602-675): confere que o pacote está em `packages\\` e abre o
  atualizador do Velopack com `apply --package <arquivo> --waitPid <este processo>` (e `--norestart` se não for para
  reabrir; os `argumentos` vão depois de `--`) e VOLTA LOGO. O atualizador espera este processo sair (no máximo 60 s,
  depois segue: `bins/src/shared/util_common.rs` 14-26), fecha à força o que ainda roda da pasta, renomeia `current`
  (10 tentativas; se não der, desiste antes de mexer e reabre a versão de antes com os mesmos argumentos:
  `apply_windows_impl.rs` 159-163 e `apply.rs` 56-60), põe a nova no lugar e reabre na conta de quem pediu. A janelinha
  "Atualizando para a versão X, aguarde..." é a dele (sem `--silent`; D-832). Se a raiz não grava, ele pede licença ao
  Windows (`apply_windows_impl.rs` "Re-launching as administrator"): o programa nunca pede a troca nesse caso.

O QUE É SEGURO E O QUE É ARRISCADO MUDAR
    Seguro: as frases de `ErroDoVelopack`. Arriscado: ligar a troca automática na abertura; pedir a troca com
    `silent=True` (some a janelinha, D-832); chamar `wait_exit_then_apply_updates` fora de `trocar` (a troca deixaria
    de passar pela conferência única de `atualizacao.trocar_para`); importar `velopack` em outro arquivo (a trava
    acusa).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


class ErroDoVelopack(RuntimeError):
    """O Velopack não fez o que foi pedido (sem internet, a tranca de outra janela, disco cheio, pacote que não está
    em `packages\\`...). A mensagem é a técnica, para o registro; nunca vai para a tela."""


@dataclass(frozen=True)
class VersaoDoVelopack:
    """Uma versão que o Velopack sabe baixar e trocar: o que ele leu (`pedido`, o `UpdateInfo` dele) e o que a
    assinatura do Samuel tem de afirmar (pacote, versão, nome do arquivo, soma SHA256, tamanho)."""

    pacote: str
    versao: str
    arquivo: str
    sha256: str
    tamanho: int
    pedido: Any = None


def _velopack():
    """A biblioteca (importada só aqui, e só quando é preciso: pelo código e nos testes nada a carrega)."""
    import velopack

    return velopack


def _fonte(endereco: str):
    """O que se passa ao `UpdateManager`: o GitHub do projeto (público, sem senha, D-713) ou uma pasta (o ensaio)."""
    vp = _velopack()
    if str(endereco).startswith("https://github.com/"):
        return vp.GithubSource(str(endereco))
    return str(endereco)


def _gerente(endereco: str, localizador=None):
    """O `UpdateManager` para esta fonte (lugar único). `localizador`: onde está a instalação (um
    `velopack.VelopackLocatorConfig`); None = a deste programa, achada pelo próprio Velopack. Só as provas passam um (a
    instalação de prova numa pasta). Sem o `Update.exe` no lugar, a biblioteca nem cria o gerente (`locator.rs` 114-117:
    "Update.exe does not exist in the expected path"): é o que `atualizacao.tem_o_atualizador` confere antes da troca.
    Volta 5: o "aceitar versão mais velha" (`AllowVersionDowngrade`) saiu com a volta automática (D-867); ele só era
    lido por `check_for_updates` (`manager.rs` 294), e baixar e trocar nunca o olharam, então tirá-lo não muda nada do
    que fica."""
    vp = _velopack()
    opcoes = vp.UpdateOptions(AllowVersionDowngrade=False, MaximumDeltasBeforeFallback=10)
    return vp.UpdateManager(_fonte(endereco), opcoes, localizador)


def _da_resposta(pedido) -> VersaoDoVelopack:
    """A versão lida de um `UpdateInfo` do Velopack."""
    alvo = pedido.TargetFullRelease
    return VersaoDoVelopack(str(alvo.PackageId), str(alvo.Version), str(alvo.FileName), str(alvo.SHA256 or ""),
                            int(alvo.Size or 0), pedido)


def atender_ganchos(ao_instalar: Callable[[str], None], ao_atualizar: Callable[[str], None],
                    ao_desinstalar: Callable[[str], None]) -> None:
    """Os ganchos de instalar, atualizar e desinstalar do Velopack (o processo sai depois deles) e, no resto, volta
    logo, SEM troca automática na abertura. Levanta `ErroDoVelopack` se a biblioteca não iniciou."""
    try:
        (_velopack().App()
         .set_auto_apply_on_startup(False)
         .on_after_install_fast_callback(ao_instalar)
         .on_after_update_fast_callback(ao_atualizar)
         .on_before_uninstall_fast_callback(ao_desinstalar)
         .run())
    except Exception as erro:  # noqa: BLE001 - qualquer erro da biblioteca vira um só
        raise ErroDoVelopack(f"o Velopack não iniciou: {type(erro).__name__}: {erro}") from erro


def procurar(endereco: str, localizador=None) -> VersaoDoVelopack | None:
    """A versão publicada mais nova que a instalada, ou None. Levanta `ErroDoVelopack` (sem internet etc.)."""
    try:
        pedido = _gerente(endereco, localizador=localizador).check_for_updates()
    except Exception as erro:  # noqa: BLE001
        raise ErroDoVelopack(f"procurar: {type(erro).__name__}: {erro}") from erro
    return None if pedido is None else _da_resposta(pedido)


def baixar(endereco: str, versao: VersaoDoVelopack, localizador=None) -> None:
    """Baixa a versão para `packages\\` (o Velopack confere tamanho e soma). Levanta `ErroDoVelopack`."""
    try:
        _gerente(endereco, localizador=localizador).download_updates(versao.pedido)
    except Exception as erro:  # noqa: BLE001
        raise ErroDoVelopack(f"baixar a {versao.versao}: {type(erro).__name__}: {erro}") from erro


def pendente(endereco: str, localizador=None) -> str:
    """A versão baixada que espera a troca ("" = nenhuma): `get_update_pending_restart` (manager.rs 272-281: o pacote
    completo mais novo de `packages\\` cuja versão é maior que a que roda). Volta 3 (emenda do Fable): é uma das três
    coisas que a abertura olha, no lugar de uma anotação nossa. Não usa a rede. Levanta `ErroDoVelopack`."""
    try:
        achado = _gerente(endereco, localizador=localizador).get_update_pending_restart()
    except Exception as erro:  # noqa: BLE001
        raise ErroDoVelopack(f"ler o pacote esperando: {type(erro).__name__}: {erro}") from erro
    return "" if achado is None else str(achado.Version)


def pacote_da_versao(pacote: str, versao: str, arquivo: str, sha256: str, sha1: str, tamanho: int) -> VersaoDoVelopack:
    """O pedido de uma versão escolhida por nós, montado sem rede (o pacote esperando, sem internet, D-859: o arquivo
    já está em `packages\\`). Levanta `ErroDoVelopack`. Se `packages\\<arquivo>` já existe, o `baixar` seguinte não
    copia nem confere (manager.rs 413-416): a conferência única da troca soma o arquivo de novo."""
    try:
        vp = _velopack()
        alvo = vp.VelopackAsset(pacote, versao, "Full", arquivo, sha1 or "", sha256, int(tamanho), "", "")
        pedido = vp.UpdateInfo(alvo, [], True)
    except Exception as erro:  # noqa: BLE001
        raise ErroDoVelopack(f"montar o pedido da {versao}: {type(erro).__name__}: {erro}") from erro
    return VersaoDoVelopack(pacote, versao, arquivo, sha256, int(tamanho), pedido)


def trocar(endereco: str, versao: VersaoDoVelopack, reabrir: bool, argumentos: list[str]) -> None:
    """A ÚNICA chamada da troca: pede ao atualizador do Velopack que espere este processo sair, troque para `versao` e,
    se `reabrir`, abra o programa com `argumentos`. Volta logo; quem chamou tem de sair. Com a janelinha do Velopack
    (nunca `silent`, D-832). Só `atualizacao.trocar_para` chama esta (depois da conferência única). Levanta
    `ErroDoVelopack` (o pacote não está em `packages\\`, o atualizador não abriu)."""
    try:
        _gerente(endereco).wait_exit_then_apply_updates(
            versao.pedido, silent=False, restart=bool(reabrir), restart_args=[str(a) for a in argumentos])
    except Exception as erro:  # noqa: BLE001
        raise ErroDoVelopack(f"trocar para a {versao.versao}: {type(erro).__name__}: {erro}") from erro
