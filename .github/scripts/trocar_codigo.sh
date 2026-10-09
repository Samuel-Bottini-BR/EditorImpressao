#!/usr/bin/env bash
# Troca o codigo do programa pelo de OUTRO ramo, mantendo a .github/ deste.
#
# Usado pelo .github/workflows/testes-windows.yml quando a rodada pede um ramo
# (workflow_dispatch com "ramo" preenchido). Nao e parte do programa.
#
#     bash .github/scripts/trocar_codigo.sh <ramo-ou-commit>
#
# O que faz, dentro da copia de trabalho do job (nunca no GitHub):
#   1. busca o ramo pedido (so o ultimo commit);
#   2. tira tudo o que o git conhece, MENOS a .github/ (o workflow, os scripts
#      e as versoes travadas continuam os deste ramo);
#   3. poe no lugar os arquivos do ramo pedido, MENOS a .github/ dele;
#   4. grava em $GITHUB_ENV quem foi testado: TESTADO_RAMO e TESTADO_SHA.
# Sem ramo pedido, so grava o proprio commit em TESTADO_*.
#
# Nao grava nada em ramo nenhum: nao faz commit nem push.
# Seguro mudar: a profundidade da busca. Arriscado: trazer a .github/ do outro
# ramo (os scripts de la podem nao existir ou ser outros), ou trocar o codigo
# DEPOIS de copiar o gabarito/modelos (a lista.json do outro ramo sobrescreveria
# a ordem das coisas; a troca tem de vir primeiro).
set -euo pipefail
RAMO="${1:-}"
if [ -z "$RAMO" ]; then
  echo "TESTADO_RAMO=${GITHUB_REF_NAME}" >> "$GITHUB_ENV"
  echo "TESTADO_SHA=${GITHUB_SHA}" >> "$GITHUB_ENV"
  echo "testando o proprio commit ${GITHUB_SHA}"
  exit 0
fi
git fetch --depth=1 origin "$RAMO"
SHA="$(git rev-parse FETCH_HEAD)"
git rm -rq --cached --ignore-unmatch -- . ':(exclude).github' > /dev/null
# apaga do disco o que era do programa deste ramo (o .gitignore protege o resto)
git clean -fdq -- . ':(exclude).github'
git checkout FETCH_HEAD -- . ':(exclude).github'
echo "TESTADO_RAMO=${RAMO}" >> "$GITHUB_ENV"
echo "TESTADO_SHA=${SHA}" >> "$GITHUB_ENV"
echo "codigo trocado pelo de ${RAMO} (${SHA}); .github/ continua a deste ramo"
git status --short | head -20
