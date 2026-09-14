#!/usr/bin/env bash
set -euo pipefail
BASE=${PROJECT_ROOT}/results/formal_chm13
ROOT=$BASE/innovation/pedsv_ml/pilot_v1
DATA=/opt/tools/HG002_trio_CHM13
export PATH=/opt/tools/conda-envs/minisv312/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}
MINISV=/opt/tools/conda-envs/minisv312/bin/minisv
REF=${PROJECT_ROOT}/refs/CHM13/chm13v2.0.fa
P=$ROOT/hg002_trio_nocutesv_v1/assembly
OUT=$ROOT/hg002_trio_nocutesv_v1/minisv_triofilter
V=$ROOT/hg002_trio_nocutesv_v1/joint_input/HG002.joint_nocutesv.minisv.vcf
mkdir -p "$OUT"
[[ -s "$V" && -s "$DATA/HG002_PacBio-HiFi-Revio_20231031_48x_CHM13v2.0.bam" && -s "$DATA/HG002_PacBio-HiFi-Revio_20231031_48x_CHM13v2.0.bam.bai" ]]
[[ -s "$P/HG003/hap1.p_ctg.fa" && -s "$P/HG003/hap2.p_ctg.fa" && -s "$P/HG004/hap1.p_ctg.fa" && -s "$P/HG004/hap2.p_ctg.fa" ]]
W=$OUT/HG002_c2c3
[[ ! -e "$W" ]] || { echo "refusing existing workdir: $W" >&2; exit 3; }
mkdir -p "$W"
"$MINISV" sv-trio-filter --name HG002_nocutesv_c2c3 --platform hifi --svlen 50 --ratio 0.6 -c 2 --uc 3 -g 5 -w 100 -m 0.6 --max_diff_len 50 \
  --mm2 /opt/tools/conda-envs/minisv312/bin/minimap2 --mg /opt/tools/conda-envs/minisv312/bin/minigraph \
  --vcf "$V" --readid_tsv "$V" "$DATA/HG002_PacBio-HiFi-Revio_20231031_48x_CHM13v2.0.bam" "$REF" \
  "$P/HG003/hap1.p_ctg.fa" "$P/HG003/hap2.p_ctg.fa" "$P/HG004/hap1.p_ctg.fa" "$P/HG004/hap2.p_ctg.fa" "$W"
printf 'sample\tHG002\nbreakpoint_window_bp\t100\nmax_indel_length_difference_bp\t50\nstatus\tCOMPLETE\n' > "$OUT/completion_audit.tsv"
