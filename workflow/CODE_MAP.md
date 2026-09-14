# Code and data-product map

The source scripts used for the current server analysis are mapped below. Public copies must read paths and parameters from `config/`; the current server snapshots still contain absolute paths and are not ready to run unchanged on another machine.

| Stage | Current implementation snapshot | Main product |
|---|---|---|
| HG002 trio assembly | `run_hg002_trio_hifiasm_v1.sh` | phased HG002/HG003/HG004 FASTA |
| Five-child assembly | `run_five_children_hifiasm_v1.sh`, `run_na12886_hifiasm_v1.sh` | phased child FASTA |
| HG002 assembly-derived calls | `run_assembly_derived_sv_v1.sh`, `build_assembly_derived_dnm_v1.py` | HG002 event tables |
| Five-child assembly-derived calls | `run_hg5_assembly_derived_dnm_v1.sh`, `build_hg5_assembly_derived_dnm_v1.py` | per-child event tables and summary |
| HG002 caller discovery | `run_hg002_trio_callers_v1.sh` | Sniffles2 and LongcallD raw VCF/BAM |
| TRGT-denovo | `run_hg002_trgt_denovo_v1.sh` and TRGT adapter scripts | TRGT-denovo candidates |
| Child-only normalization | `build_hg002_trio_childonly_v1.sh` | child-only VCF and audit |
| Caller union | `build_hg002_trio_minisv_union_v1.py`, `build_hg002_threecaller_union.py` | deduplicated joint VCF |
| Minisv | `run_hg002_trio_minisv_triofilter_v1.sh`, `run_hg002_threecaller_c2c3_defaultbase.sh`, TRGT Minisv scripts | C2/C3 VCF and statistics |
| Result summary | `build_two_pedigree_results_report.py` | two-family table |

## Current event rules

Assembly-derived first-pass calls use `minimap2 -x asm5 --cs` plus `paftools.js call`, retain absolute SV length at least 50 bp, and match events using the same chromosome/type, breakpoint tolerance 100 bp, and absolute length tolerance 50 bp. These values must be configurable in the public implementation.

The three-caller union retains source caller and source IDs and removes records that fall within the same chromosome/type, breakpoint tolerance 100 bp, and absolute length tolerance 50 bp cluster.

## Required additions before a final release

- Replace absolute server paths with configuration variables.
- Add an input validator and checksum manifest generator.
- Add explicit MAPQ, primary/secondary alignment, gap, contig-end, and uniqueness fields to the assembly-derived audit.
- Add a common event-level overlap script for assembly-derived versus caller/Minisv outputs.
- Add a five-child anomaly report instead of reporting only total counts.
- Record exact command lines and versions for every result directory.
