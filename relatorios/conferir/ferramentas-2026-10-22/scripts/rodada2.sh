#!/bin/bash
# Verificador 22/10: 2.6 (livro de verdade + montagens + dobra), 2.16 (1 x N trabalhadores, e velocidade
# antes x depois alternados, um processo por vez) e 2.18 (áreas à mão).
export PYTHONIOENCODING=utf-8
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
W=/d/programas/EditorImpressao/.claude/worktrees
V=$W/vfr22-novo/relatorios/conferir/ferramentas-2026-10-22
S=$V/scripts
T=$V/trabalho
log() { echo "$(date +%H:%M:%S) $*" >> $T/rodada2.log; }
M="D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/Marial de sermoens - Frei Balthasar Paez. (1).pdf"
PAGS=(); for n in $(seq 11 33); do PAGS+=("$M:$n"); done

# 2.6: o livro (Original, de fabrica) e as montagens
log "2.6 livro"
$PY $S/caminho.py --raiz $W/vfr22-novo livro --saida $T/2.6/marial23.pdf "${PAGS[@]}" >> $T/rodada2.log 2>&1
L=$T/2.6/marial23.pdf
mont() { log "2.6 montar $1"; $PY $S/impressao26.py montar --raiz $W/vfr22-novo --livro $L --saida $T/2.6/$1.pdf --opcoes "$2" >> $T/rodada2.log 2>&1
         $PY $S/impressao26.py conferir --livro $L --saida $T/2.6/$1.pdf --por-caderno ${3:-20} >> $T/rodada2.log 2>&1; }
mont livreto-fabrica '{}'
mont livreto-esq90-p5-80 '{"escala_esquerda": 90, "excecoes": {"5": 80}}'
mont livreto-8-por-caderno '{"paginas_por_caderno": 8}' 8
mont livreto-escala120 '{"escala": "personalizada", "escala_percentual": 120}'
mont livreto-sem-margens '{"margens": false}'
log "2.6 pagina inteira"; $PY $S/impressao26.py montar --raiz $W/vfr22-novo --livro $L --saida $T/2.6/pagina-inteira.pdf --opcoes '{"formato": "pagina_inteira"}' >> $T/rodada2.log 2>&1
for lado in antes novo; do log "2.6 velho $lado"; $PY $S/impressao26.py velho --raiz $W/vfr22-$lado --livro $L --saida $T/2.6/velho-$lado.pdf >> $T/rodada2.log 2>&1
  $PY $S/impressao26.py conferir --livro $L --saida $T/2.6/velho-$lado.pdf >> $T/rodada2.log 2>&1; done

# 2.18
log "2.18"; $PY $S/zonas218.py --raiz $W/vfr22-novo --saida $T/2.18 >> $T/rodada2.log 2>&1

# 2.16 e velocidade: Preto e branco, 23 paginas, alternado
for rep in 1 2; do
  log "vel antes $rep"; $PY $S/caminho.py --raiz $W/vfr22-antes livro --saida $T/2.16/antes-$rep.pdf --campos '{"filtro_padrao": "preto_e_branco"}' "${PAGS[@]}" >> $T/rodada2.log 2>&1
  log "vel novo1 $rep"; VFR_TRABALHADORES=1 $PY $S/caminho.py --raiz $W/vfr22-novo livro --saida $T/2.16/novo1-$rep.pdf --campos '{"filtro_padrao": "preto_e_branco"}' "${PAGS[@]}" >> $T/rodada2.log 2>&1
  log "vel novo3 $rep"; VFR_TRABALHADORES=3 $PY $S/caminho.py --raiz $W/vfr22-novo livro --saida $T/2.16/novo3-$rep.pdf --campos '{"filtro_padrao": "preto_e_branco"}' "${PAGS[@]}" >> $T/rodada2.log 2>&1
done
$PY $S/somas_pdf.py $T/2.16/antes-1.pdf $T/2.16/novo1-1.pdf $T/2.16/novo3-1.pdf $T/2.16/antes-2.pdf $T/2.16/novo3-2.pdf >> $T/rodada2.log 2>&1
log "FIM"
