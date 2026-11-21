#!/usr/bin/env bash
# O juiz do porteiro na rodada do GitHub (passo 0 do plano da parte do Windows; R2 e R3 da terceira volta de quem
# tentou quebrar). PARA A GERENTE COPIAR para `.github/scripts/porteiro_juiz.sh` no ramo claude/list-server-files-gkos8v.
#
# Roda DEPOIS do trocar_codigo.sh (a pasta de trabalho já tem o código do ramo pedido). Busca a versão de teste, tira
# dela o pacote regras_dos_agentes/ e a lista de exceções para uma pasta à parte ($RUNNER_TEMP/juiz) e roda, de lá,
# `python -m regras_dos_agentes juiz --conferido "$GITHUB_WORKSPACE"`: é o código da versão de teste julgando o ramo.
# Nada do ramo conferido decide com que versão se compara: o nome vem de VERSAO_DE_TESTE, escrito no workflow.
#
# Saída: a linha "PORTEIRO: CONFERIDO", "PORTEIRO: BARROU" ou "PORTEIRO: NAO CONFERIDO (motivo)" (a K21 do formulário
# procura essa linha no registro da rodada). BARROU faz o passo falhar. NAO CONFERIDO não falha a rodada, mas vira
# aviso visível no topo da rodada e no resumo; com PORTEIRO_LIGADO=1, "a versão de teste não tem o porteiro" falha.
#
# Seguro mudar: as mensagens. Arriscado: buscar o código de outro lugar que não a versão de teste, ou rodar o juiz de
# dentro da pasta de trabalho (aí o `python -m` pegaria o regras_dos_agentes do ramo conferido).
set -uo pipefail

VERSAO="${VERSAO_DE_TESTE:?o workflow tem de dizer VERSAO_DE_TESTE}"
LIGADO="${PORTEIRO_LIGADO:-0}"
JUIZ="${RUNNER_TEMP:-/tmp}/juiz"

avisar() {   # $1 = nível do GitHub (warning/error), $2 = frase
  echo "$2"
  echo "::$1 title=Porteiro::$2"
  [ -n "${GITHUB_STEP_SUMMARY:-}" ] && echo "## $2" >> "$GITHUB_STEP_SUMMARY"
}

# `--depth=1` só quando a cópia já é rasa (a do GitHub, tirada com o último commit). Numa cópia inteira (a do PC, ou
# uma worktree dela, que divide a mesma pasta .git), `--depth=1` a deixa rasa e corta a história do repositório do
# Samuel, mesmo quando o ramo buscado já estava em dia (aconteceu em 19/11/2026: o script rodado à mão na cópia do
# agente deixou o repositório do PC raso, e o `git merge` da gerente recusou). É a mesma regra de
# `regras_dos_agentes/conversa_com_o_git.py::buscar_ramo` (este script não pode importar o pacote: ele ainda não tem
# o código da versão de teste); `tests/test_conferencias_copia_inteira.py` cobra as duas. Arriscado: voltar o
# `--depth=1` fixo.
PROFUNDIDADE=""
[ "$(git rev-parse --is-shallow-repository)" = "true" ] && PROFUNDIDADE="--depth=1"
if ! git fetch -q $PROFUNDIDADE origin "+refs/heads/$VERSAO:refs/remotes/origin/$VERSAO"; then
  avisar error "PORTEIRO: NAO CONFERIDO (não deu para buscar a versão de teste $VERSAO)"
  exit 1
fi
BASE="$(git rev-parse "refs/remotes/origin/$VERSAO")"

if ! git cat-file -e "$BASE:regras_dos_agentes/__main__.py" 2>/dev/null; then
  if [ "$LIGADO" = "1" ]; then
    avisar error "PORTEIRO: NAO CONFERIDO (a versão de teste $VERSAO não tem o porteiro, e ele devia estar lá)"
    exit 1
  fi
  avisar warning "PORTEIRO: NAO CONFERIDO (a versão de teste $VERSAO ainda não tem o porteiro)"
  exit 0
fi

# A pasta do juiz é apagada com tudo dentro: antes, confere que ela não é atalho de pasta (junção ou link) (D-809; a
# pasta modelos/ esvaziada em 18/11). O que foi provado no Git Bash 5.2.37 (msys), em 20/11, numa junção de prova:
# `rm -rf "$JUIZ"` SEM barra no fim tira só o atalho; `rm -rf "$JUIZ/"` COM barra no fim apaga o conteúdo da pasta de
# verdade; `[ -L ]` e `[ -h ]` dão sim para a junção (sem barra no fim). A conferência fica porque nada garante que
# ninguém vai acrescentar a barra. Arriscado: tirar esta conferência, ou escrever `$JUIZ/` nela ou no `rm`.
if [ -L "$JUIZ" ] || [ -h "$JUIZ" ]; then
  avisar error "PORTEIRO: NAO CONFERIDO (a pasta do juiz $JUIZ é um atalho de pasta: não apago o que está nela)"
  exit 1
fi
rm -rf "$JUIZ" && mkdir -p "$JUIZ"
# O tar recebe o arquivo pela entrada e escreve na pasta atual: um caminho com "C:" no tar seria lido como outra
# máquina (o RUNNER_TEMP do GitHub é "D:\a\_temp").
( cd "$JUIZ" && git -C "$GITHUB_WORKSPACE" archive "$BASE" regras_dos_agentes tests/conferencias_excecoes.json | tar -x ) || {
  avisar error "PORTEIRO: NAO CONFERIDO (não deu para tirar o porteiro da versão de teste)"
  exit 1
}
cd "$JUIZ" && python -m regras_dos_agentes juiz --conferido "$GITHUB_WORKSPACE"
