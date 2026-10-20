#!/usr/bin/env bash
# Poe numa pasta propria o programa de um ramo ou commit (para o filtro de
# velocidade, job "velocidade_ab" do .github/workflows/testes-windows.yml).
# Nao e parte do programa.
#
#     bash .github/scripts/preparar_versao.sh <ramo-ou-commit> <pasta> <ANTES|DEPOIS>
#
# O que faz, dentro da copia de trabalho do job (nunca no GitHub):
#   1. busca so o ultimo commit do ramo pedido (git fetch --depth=1);
#      commit abreviado (ex.: 1d37f8f) nao se busca assim: pergunta o commit
#      inteiro a API do GitHub (precisa de GH_TOKEN) e busca esse;
#   2. cria a <pasta> com aquele commit (git worktree, sem ramo: --detach);
#   3. grava em $GITHUB_ENV: VERSAO_<ANTES|DEPOIS>_SHA (commit inteiro).
# Nao grava nada em ramo nenhum: nao faz commit nem push.
#
# Seguro mudar: a profundidade da busca. Arriscado: trocar o worktree por um
# checkout por cima da pasta do job (as duas versoes tem de existir ao mesmo
# tempo, lado a lado, para alternar sem reinstalar nada).
set -euo pipefail
REF="${1:?falta o ramo ou commit}"
DESTINO="${2:?falta a pasta}"
NOME="${3:?falta ANTES ou DEPOIS}"

if git fetch --depth=1 origin "$REF" 2>/dev/null; then
  SHA="$(git rev-parse FETCH_HEAD)"
else
  # commit abreviado (ou ramo que o fetch nao achou): pergunta a API
  SHA="$(gh api "repos/${GITHUB_REPOSITORY}/commits/${REF}" --jq .sha)"
  git fetch --depth=1 origin "$SHA"
fi
git worktree add --detach "$DESTINO" "$SHA"
echo "VERSAO_${NOME}_SHA=${SHA}" >> "$GITHUB_ENV"
echo "versao ${NOME}: ${REF} = ${SHA} em ${DESTINO}"
git -C "$DESTINO" log -1 --format='  %h %ad %s' --date=short
