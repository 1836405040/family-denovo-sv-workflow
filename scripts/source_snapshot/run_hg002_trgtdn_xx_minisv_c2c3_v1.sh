#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=${PROJECT_ROOT}/results/formal_chm13/innovation/pedsv_ml/pilot_v1
TR=$ROOT/candidates/trgt/hg002_trio_full_catalog_xx_v1
AD=$ROOT/hg002_trio_nocutesv_v1/trgt_adapter_xx_v1
OUT=$ROOT/hg002_trio_nocutesv_v1/minisv_triofilter/trgtdn_c2c3_defaultbase_xx
REF=${PROJECT_ROOT}/refs/CHM13/chm13v2.0.fa
mkdir -p "$AD" "$OUT" "$ROOT/logs"
exec >> "$ROOT/logs/HG002_trgtdn_c2c3_defaultbase_xx.nohup" 2>&1
until [[ -s "$TR/HG002.trgt_denovo.tsv" && -s "$TR/HG004.spanning.sorted.bam" ]]; do sleep 30; done
/opt/tools/conda-envs/minisv312/bin/python "$ROOT/scripts/40_build_trgt_caller_derived_minisv_adapter_v2_support_contract.py" \
  --signal-tsv "$TR/HG002.trgt_denovo.tsv" --spanning-bam "$TR/HG002.spanning.sorted.bam" \
  --reference "$REF" --sample HG002 --min-svlen 100 \
  --output-vcf "$AD/HG002.TRGTdenovo.minisv.vcf" --output-readids "$AD/HG002.TRGTdenovo.minisv.readids.tsv" \
  --output-audit "$AD/HG002.TRGTdenovo.minisv.audit.tsv" --output-exclusions "$AD/HG002.TRGTdenovo.minisv.exclusions.tsv"
export PATH=/opt/tools/conda-envs/minisv312/bin:/usr/local/bin:/usr/bin:/bin:$PATH
minisv sv-trio-filter --name HG002_trgtdn_defaultbase_c2c3_xx --platform hifi --svlen 100 --ratio 0.8 -c 2 --uc 3 -g 5 -w 500 -m 0.6 --max_diff_len 1000 \
  --mm2 /opt/tools/conda-envs/minisv312/bin/minimap2 --mg /opt/tools/conda-envs/minisv312/bin/minigraph \
  --vcf "$AD/HG002.TRGTdenovo.minisv.vcf" --readid_tsv "$AD/HG002.TRGTdenovo.minisv.vcf" \
  /opt/tools/HG002_trio_CHM13/HG002_PacBio-HiFi-Revio_20231031_48x_CHM13v2.0.bam "$REF" \
  "$ROOT/hg002_trio_nocutesv_v1/assembly/HG003/hap1.p_ctg.fa" "$ROOT/hg002_trio_nocutesv_v1/assembly/HG003/hap2.p_ctg.fa" \
  "$ROOT/hg002_trio_nocutesv_v1/assembly/HG004/hap1.p_ctg.fa" "$ROOT/hg002_trio_nocutesv_v1/assembly/HG004/hap2.p_ctg.fa" "$OUT"
printf 'COMPLETE_XX\n' > "$ROOT/status/HG002_TRGTDN_MINISV_XX_V1"
