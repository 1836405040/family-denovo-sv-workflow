# Script inventory

The files below are the exact local/server implementation snapshots that produced the previous two-family table. They are listed for review before conversion to configuration-driven public scripts.

| Public workflow stage | Source file | Publication status |
|---|---|---|
| HG002 assembly | `run_hg002_trio_hifiasm_v1.sh` | snapshot; replace paths |
| Five-child assembly | `run_five_children_hifiasm_v1.sh` | snapshot; replace paths |
| HG002 assembly-derived | `run_assembly_derived_sv_v1.sh` + `build_assembly_derived_dnm_v1.py` | snapshot; add QC |
| Five-child assembly-derived | `run_hg5_assembly_derived_dnm_v1.sh` + `build_hg5_assembly_derived_dnm_v1.py` | snapshot; add QC |
| HG002 callers | `run_hg002_trio_callers_v1.sh` | snapshot; replace paths |
| TRGT-denovo | `run_hg002_trgt_denovo_v1.sh` | snapshot; replace paths |
| Child-only | `build_hg002_trio_childonly_v1.sh` | snapshot; expose config |
| Two-caller union | `build_hg002_trio_minisv_union_v1.py` | snapshot; expose config |
| Three-caller union | `build_hg002_threecaller_union.py` | snapshot; expose config |
| Minisv C2/C3 | `run_hg002_trio_minisv_triofilter_v1.sh` and `run_hg002_threecaller_c2c3_defaultbase.sh` | snapshot; separate run specs |
| Summary | `build_two_pedigree_results_report.py` | snapshot; add anomaly audit |


