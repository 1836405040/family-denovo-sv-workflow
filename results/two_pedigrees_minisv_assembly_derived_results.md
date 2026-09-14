# 两个家系 Minisv triofilter 与 assembly-derived 结果汇总

统计口径：VCF 非注释行数；C2/C3 分别对应 `sniffles2_l+s_2_filtered.vcf` 与 `sniffles2_l+s_3_filtered.vcf`。

| 家系 | 子代 | Sniffles2 C2/C3 | LongcallD C2/C3 | TRGT-denovo C2/C3 | 三 caller 联合 C2/C3 | assembly-derived 双 hap、无父母匹配 | 单 hap、无父母匹配 | 父母匹配 | assembly-derived 总事件 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 五子代 | NA12879 | 23/16 | 11/6 | 19/2 | 53/24 | 306 | 5043 | 7994 | 13343 |
| 五子代 | NA12881 | 26/21 | 14/3 | 40/12 | 80/37 | 260 | 4101 | 7550 | 11911 |
| 五子代 | NA12882 | 22/19 | 10/4 | 30/7 | 61/30 | 199 | 3645 | 7608 | 11452 |
| 五子代 | NA12885 | 35/32 | 6/1 | 42/13 | 83/46 | 110 | 3282 | 7507 | 10899 |
| 五子代 | NA12886 | 42/39 | 9/6 | 24/6 | 74/50 | 333 | 5445 | 8123 | 13901 |
| HG002 家系 | HG002 | 131/97 | 150/97 | 73/32 | 344/218 | 84 | 3091 | 7992 | 11167 |

## 结果路径与参数

- 五子代独立 caller：`hg5_triofilter_c2c3_defaultbase_20260911/<sample>/{sniffles2,longcallD,trgtdn}`。
- 五子代三 caller 联合：`hg5_triofilter_c2c3_defaultbase_20260911_retry_joint3/<sample>/joint3`。
- HG002 独立 caller：`hg002_trio_nocutesv_v1/minisv_triofilter/{sniffles2_c2c3_defaultbase,longcallD_c2c3_defaultbase,trgtdn_c2c3_defaultbase_xx}`。
- HG002 三 caller 联合：`hg002_trio_nocutesv_v1/minisv_triofilter/HG002_threecaller_c2c3_defaultbase`。
- 联合去重审计：三个 caller 的合格原始记录为 Sniffles2 3,040、LongcallD 1,866、TRGT-denovo 633，共 5,539 条；按染色体、SV 类型、断点 ±100 bp、绝对长度差 ±50 bp 聚类后保留 5,141 个事件，去除 398 条重复记录。三个 caller 同时支持的事件为 0，两个 caller 重叠的事件为 333。
- 五子代 assembly-derived 汇总：`hg5_assembly/assembly_derived_dnm_v1/assembly_derived_summary.tsv`。
- HG002 assembly-derived：`hg002_trio_nocutesv_v1/assembly_derived_v1/assembly_derived_dnm_events.tsv`。
- Minisv 统一筛选：`svlen=100`，坐标窗口 ±100 bp，绝对 SV 长度差 ±50 bp，`-c 2 --uc 3 -g 5 -w 500 -m 0.6 --max_diff_len 1000`。
- assembly-derived 独立于 Minisv：minimap2 `asm5 --cs` + `paftools.js call`；保留绝对长度 ≥50 bp；父母排除窗口为坐标 ±100 bp、长度 ±50 bp；子代双 hap 支持列为严格候选。
- assembly-derived 参数审查：当前设置适合 CHM13 HiFi/hifiasm 的第一轮高召回筛选，但不宜直接称为最终金标准。`asm5`、±100 bp 断点和 ±50 bp 长度差能容忍组装/比对误差；≥50 bp 过滤与 Minisv 的研究范围一致。后续确认阶段建议加入最小比对质量/唯一比对、双 hap 一致性、父母四 hap 均无匹配、序列级别比对（例如 dipcall/PAV 或局部 assembly）以及人工复核，以降低重复序列和组装断裂导致的假阳性。
- HG002 的 TRGT-denovo 使用正确的 HG004 `XX` 流程；HG002 本身沿用男性 `XY` 数据。adapter 保留 633 个候选，之后 Minisv 得到表中 C2/C3。

> 注意：assembly-derived 的“单 hap、无父母匹配”是候选证据，不等同于已确认 DNM；“双 hap、无父母匹配”是本表中更严格的 assembly-derived DNM 候选层。
