#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=${PROJECT_ROOT}/results/formal_chm13
PROJECT=$ROOT/innovation/pedsv_ml/pilot_v1
REF=${PROJECT_ROOT}/refs/CHM13/chm13v2.0.fa
CAT=$PROJECT/truth/chm13v2.0_maskedY_rCRS.platinumTRs-v1.0.trgt.bed.gz
TRGT=$PROJECT/software/trgt-v5.1.0/trgt-v5.1.0-x86_64-unknown-linux-gnu/trgt
DN=$PROJECT/software/trgt-denovo-v0.3.0/trgt-denovo-v0.3.0-x86_64-unknown-linux-gnu/trgt-denovo
BCF=/opt/tools/conda-envs/minisv312/bin/bcftools
SAM=/usr/bin/samtools
OUT=$PROJECT/candidates/trgt/hg002_trio_full_catalog_v1
LOG=$PROJECT/logs/hg002_trgt_denovo_v1.log
mkdir -p "$OUT" "$PROJECT/logs" "$PROJECT/status"
exec >> "$LOG" 2>&1
printf 'RUNNING\n' > "$PROJECT/status/HG002_TRGT_DENOVO_V1"
declare -A BAM=(
 [HG002]=/opt/tools/HG002_trio_CHM13/HG002_PacBio-HiFi-Revio_20231031_48x_CHM13v2.0.bam
 [HG003]=/opt/tools/HG002_trio_CHM13/HG003_PacBio-HiFi-Revio_20231031_46x_CHM13v2.0.bam
 [HG004]=/opt/tools/HG002_trio_CHM13/HG004_PacBio-HiFi-Revio_20231031_36x_CHM13v2.0.bam
)
for s in HG002 HG003 HG004; do
  "$TRGT" genotype --genome "$REF" --reads "${BAM[$s]}" --repeats "$CAT" --output-prefix "$OUT/$s" --sample-name "$s" --karyotype XY --threads 32 --output-type z
  "$BCF" sort -Oz -o "$OUT/$s.sorted.vcf.gz" "$OUT/$s.vcf.gz"; "$BCF" index -t "$OUT/$s.sorted.vcf.gz"
  "$SAM" sort -@ 16 -o "$OUT/$s.spanning.sorted.bam" "$OUT/$s.spanning.bam"; "$SAM" index "$OUT/$s.spanning.sorted.bam"
done
"$DN" trio --reference "$REF" --bed "$CAT" --out "$OUT/HG002.trgt_denovo.tsv" -@ 32 --father "$OUT/HG003" --mother "$OUT/HG004" --child "$OUT/HG002"
printf 'COMPLETE\n' > "$PROJECT/status/HG002_TRGT_DENOVO_V1"
