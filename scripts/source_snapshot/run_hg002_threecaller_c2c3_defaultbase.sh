#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=${PROJECT_ROOT}/results/formal_chm13/innovation/pedsv_ml/pilot_v1
OUT=$ROOT/hg002_trio_nocutesv_v1/minisv_triofilter/HG002_threecaller_c2c3_defaultbase
V=$ROOT/hg002_trio_nocutesv_v1/joint_input/HG002.joint_threecaller_nocutesv.minisv.vcf
P=$ROOT/hg002_trio_nocutesv_v1/assembly
REF=${PROJECT_ROOT}/refs/CHM13/chm13v2.0.fa
BAM=/opt/tools/HG002_trio_CHM13/HG002_PacBio-HiFi-Revio_20231031_48x_CHM13v2.0.bam
MINISV=/opt/tools/conda-envs/minisv312/bin/minisv
mkdir -p "$OUT" "$ROOT/logs" "$ROOT/status"
test -s "$V" && test -s "$BAM" && test -s "$BAM.bai"
test -s "$P/HG003/hap1.p_ctg.fa" && test -s "$P/HG003/hap2.p_ctg.fa"
test -s "$P/HG004/hap1.p_ctg.fa" && test -s "$P/HG004/hap2.p_ctg.fa"
printf 'RUNNING\n' > "$ROOT/status/HG002_THREECALLER_MINISV_C2C3"
export PATH=/opt/tools/conda-envs/minisv312/bin:/usr/local/bin:/usr/bin:/bin:$PATH
"$MINISV" sv-trio-filter --name HG002_threecaller_c2c3_defaultbase --platform hifi --svlen 100 --ratio 0.8 -c 2 --uc 3 -g 5 -w 500 -m 0.6 --max_diff_len 1000 \
  --mm2 /opt/tools/conda-envs/minisv312/bin/minimap2 --mg /opt/tools/conda-envs/minisv312/bin/minigraph \
  --vcf "$V" --readid_tsv "$V" "$BAM" "$REF" \
  "$P/HG003/hap1.p_ctg.fa" "$P/HG003/hap2.p_ctg.fa" "$P/HG004/hap1.p_ctg.fa" "$P/HG004/hap2.p_ctg.fa" "$OUT"
printf 'COMPLETE\n' > "$ROOT/status/HG002_THREECALLER_MINISV_C2C3"
