#!/usr/bin/env python3
from pathlib import Path
import csv

ROOT = Path('${PROJECT_ROOT}/results/formal_chm13/innovation/pedsv_ml/pilot_v1')
REPORT = ROOT / 'reports'

def records(path):
    try:
        with path.open() as fh:
            return sum(1 for line in fh if not line.startswith('#'))
    except FileNotFoundError:
        return None

def caller_counts(base):
    out = {}
    for key, d in [('sniffles2', 'sniffles2_c2c3_defaultbase'),
                   ('longcallD', 'longcallD_c2c3_defaultbase'),
                   ('trgtdn', 'trgtdn_c2c3_defaultbase_xx')]:
        p = base / d
        out[key] = [records(p / 'sniffles2_l+s_2_filtered.vcf'),
                     records(p / 'sniffles2_l+s_3_filtered.vcf')]
    return out

def five_counts(s):
    base = ROOT / 'hg5_triofilter_c2c3_defaultbase_20260911'
    out = {}
    for key in ['sniffles2', 'longcallD', 'trgtdn']:
        p = base / s / key
        out[key] = [records(p / 'sniffles2_l+s_2_filtered.vcf'),
                    records(p / 'sniffles2_l+s_3_filtered.vcf')]
    p = ROOT / 'hg5_triofilter_c2c3_defaultbase_20260911_retry_joint3' / s / 'joint3'
    out['joint3'] = [records(p / 'sniffles2_l+s_2_filtered.vcf'),
                     records(p / 'sniffles2_l+s_3_filtered.vcf')]
    return out

def ad_counts(path):
    result = {'both_haps': 0, 'one_hap_no_parent': 0, 'parent_match': 0, 'total': 0}
    try:
        with path.open() as fh:
            for row in csv.DictReader(fh, delimiter='\t'):
                result['total'] += 1
                cls = row.get('assembly_derived_class', '')
                if cls == 'putative_DNM_both_child_haps': result['both_haps'] += 1
                elif cls == 'child_only_one_hap_no_parent_match': result['one_hap_no_parent'] += 1
                elif cls == 'inherited_or_parent_match': result['parent_match'] += 1
    except FileNotFoundError:
        return None
    return result

def fmt(x):
    return '—' if x is None else str(x)

def main():
    rows = []
    hg5_ad = ROOT / 'hg5_assembly/assembly_derived_dnm_v1'
    for s in ['NA12879', 'NA12881', 'NA12882', 'NA12885', 'NA12886']:
        c = five_counts(s); a = ad_counts(hg5_ad / s / 'assembly_derived_dnm_events.tsv')
        rows.append(('五子代', s, c, a))
    hg002_base = ROOT / 'hg002_trio_nocutesv_v1/minisv_triofilter'
    c = caller_counts(hg002_base)
    p = hg002_base / 'HG002_threecaller_c2c3_defaultbase'
    c['joint3'] = [records(p / 'sniffles2_l+s_2_filtered.vcf'), records(p / 'sniffles2_l+s_3_filtered.vcf')]
    a = ad_counts(ROOT / 'hg002_trio_nocutesv_v1/assembly_derived_v1/assembly_derived_dnm_events.tsv')
    rows.append(('HG002 家系', 'HG002', c, a))

    REPORT.mkdir(parents=True, exist_ok=True)
    md = REPORT / 'two_pedigrees_minisv_assembly_derived_results.md'
    with md.open('w', encoding='utf-8') as fh:
        fh.write('# 两个家系 Minisv triofilter 与 assembly-derived 结果汇总\n\n')
        fh.write('统计口径：VCF 非注释行数；C2/C3 分别对应 `sniffles2_l+s_2_filtered.vcf` 与 `sniffles2_l+s_3_filtered.vcf`。\n\n')
        fh.write('| 家系 | 子代 | Sniffles2 C2/C3 | LongcallD C2/C3 | TRGT-denovo C2/C3 | 三 caller 联合 C2/C3 | assembly-derived 双 hap、无父母匹配 | 单 hap、无父母匹配 | 父母匹配 | assembly-derived 总事件 |\n|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n')
        for pedigree, sample, c, a in rows:
            def pair(k):
                v = c.get(k, [None, None]); return f'{fmt(v[0])}/{fmt(v[1])}'
            aa = a or {'both_haps': None, 'one_hap_no_parent': None, 'parent_match': None, 'total': None}
            fh.write(f'| {pedigree} | {sample} | {pair("sniffles2")} | {pair("longcallD")} | {pair("trgtdn")} | {pair("joint3")} | {fmt(aa["both_haps"])} | {fmt(aa["one_hap_no_parent"])} | {fmt(aa["parent_match"])} | {fmt(aa["total"])} |\n')
        fh.write('\n## 结果路径与参数\n\n')
        fh.write('- 五子代独立 caller：`hg5_triofilter_c2c3_defaultbase_20260911/<sample>/{sniffles2,longcallD,trgtdn}`。\n')
        fh.write('- 五子代三 caller 联合：`hg5_triofilter_c2c3_defaultbase_20260911_retry_joint3/<sample>/joint3`。\n')
        fh.write('- HG002 独立 caller：`hg002_trio_nocutesv_v1/minisv_triofilter/{sniffles2_c2c3_defaultbase,longcallD_c2c3_defaultbase,trgtdn_c2c3_defaultbase_xx}`。\n')
        fh.write('- HG002 三 caller 联合：`hg002_trio_nocutesv_v1/minisv_triofilter/HG002_threecaller_c2c3_defaultbase`。联合输入先按染色体、SV 类型、断点 ±100 bp、长度差 ±50 bp 去重；三个 caller 的合并输入为 5,141 个事件（Sniffles2 3,040、LongcallD 1,866、TRGT-denovo 633；原始合计 5,539，去除 398 个重复记录）。\n')
        fh.write('- 五子代 assembly-derived 汇总：`hg5_assembly/assembly_derived_dnm_v1/assembly_derived_summary.tsv`。\n')
        fh.write('- HG002 assembly-derived：`hg002_trio_nocutesv_v1/assembly_derived_v1/assembly_derived_dnm_events.tsv`。\n')
        fh.write('- Minisv 统一筛选：`svlen=100`，坐标窗口 ±100 bp，绝对 SV 长度差 ±50 bp，`-c 2 --uc 3 -g 5 -w 500 -m 0.6 --max_diff_len 1000`。\n')
        fh.write('- assembly-derived 独立于 Minisv：minimap2 `asm5 --cs` + `paftools.js call`；保留绝对长度 ≥50 bp；父母排除窗口为坐标 ±100 bp、长度 ±50 bp；子代双 hap 支持列为严格候选。该设置适合当前 CHM13 HiFi/hifiasm 的初筛，但属于宽松候选筛选，不是最终金标准；详见参数审查说明。\n')
        fh.write('- HG002 的 TRGT-denovo 使用正确的 HG004 `XX` 流程；HG002 本身沿用男性 `XY` 数据。adapter 保留 633 个候选，之后 Minisv 得到表中 C2/C3。\n')
        fh.write('\n> 注意：assembly-derived 的“单 hap、无父母匹配”是候选证据，不等同于已确认 DNM；“双 hap、无父母匹配”是本表中更严格的 assembly-derived DNM 候选层。\n')
    tsv = REPORT / 'two_pedigrees_minisv_assembly_derived_results.tsv'
    with tsv.open('w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t'); w.writerow(['pedigree','sample','sniffles2_C2','sniffles2_C3','longcallD_C2','longcallD_C3','trgtdn_C2','trgtdn_C3','joint3_C2','joint3_C3','assembly_both_haps_no_parent','assembly_one_hap_no_parent','assembly_parent_match','assembly_total'])
        for pedigree, sample, c, a in rows:
            aa = a or {}
            w.writerow([pedigree, sample, *c['sniffles2'], *c['longcallD'], *c['trgtdn'], *c['joint3'], aa.get('both_haps'), aa.get('one_hap_no_parent'), aa.get('parent_match'), aa.get('total')])
    print(md); print(tsv)

if __name__ == '__main__': main()
