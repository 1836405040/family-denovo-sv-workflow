#!/usr/bin/env bash
set -euo pipefail
BASE=${PROJECT_ROOT}/results/formal_chm13
ROOT=$BASE/innovation/pedsv_ml/pilot_v1
RAW=$ROOT/hg002_trio_nocutesv_v1/callers_raw
OUT=$ROOT/hg002_trio_nocutesv_v1/callers
PY=/opt/tools/conda-envs/minisv312/bin/python
mkdir -p "$OUT/sniffles2" "$OUT/longcallD"

"$PY" "$ROOT/config/make_child_only_sv_vcf.py" --child "$RAW/sniffles2/HG002.vcf" --father "$RAW/sniffles2/HG003.vcf" --mother "$RAW/sniffles2/HG004.vcf" --window 100 --min-length-ratio 0.5 --output "$OUT/sniffles2/HG002.child_only.vcf" --audit "$OUT/sniffles2/HG002.child_only.audit.tsv"
"$PY" "$ROOT/config/prepare_minisv_compatible_vcf.py" "$OUT/sniffles2/HG002.child_only.vcf" "$OUT/sniffles2/HG002.child_only.minisv.vcf" --audit "$OUT/sniffles2/HG002.child_only.minisv.audit.tsv" --caller HG002_Sniffles2

"$PY" "$ROOT/config/make_child_only_sv_vcf.py" --child "$RAW/longcallD/HG002/HG002.longcallD.raw.vcf" --father "$RAW/longcallD/HG003/HG003.longcallD.raw.vcf" --mother "$RAW/longcallD/HG004/HG004.longcallD.raw.vcf" --window 100 --min-length-ratio 0.5 --output "$OUT/longcallD/HG002.child_only.vcf" --audit "$OUT/longcallD/HG002.child_only.audit.tsv"
"$PY" "$ROOT/config/prepare_minisv_compatible_vcf.py" "$OUT/longcallD/HG002.child_only.vcf" "$OUT/longcallD/HG002.child_only.minisv.vcf" --audit "$OUT/longcallD/HG002.child_only.minisv.audit.tsv" --caller HG002_LongcallD
printf 'COMPLETE\n' > "$ROOT/status/HG002_TRIO_CHILDONLY_V1"
