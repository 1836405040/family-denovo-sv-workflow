#!/usr/bin/env python3
from pathlib import Path

ROOT = Path('${PROJECT_ROOT}/results/formal_chm13/innovation/pedsv_ml/pilot_v1')
OUT = ROOT / 'hg002_trio_nocutesv_v1' / 'joint_input'
SPECS = [
    ('sniffles2', ROOT / 'hg002_trio_nocutesv_v1/callers/sniffles2/HG002.child_only.minisv.vcf'),
    ('longcallD', ROOT / 'hg002_trio_nocutesv_v1/callers/longcallD/HG002.child_only.minisv.vcf'),
    ('trgtdn', ROOT / 'hg002_trio_nocutesv_v1/trgt_adapter_xx_v1/HG002.TRGTdenovo.minisv.vcf'),
]

def iv(x, default=0):
    try: return int(str(x).split(',', 1)[0])
    except (TypeError, ValueError): return default

def parse_info(s):
    out = {}
    for item in s.split(';'):
        if '=' in item:
            k, v = item.split('=', 1); out[k] = v
    return out

def read(path, caller):
    rows = []
    with path.open() as fh:
        for line in fh:
            if line.startswith('#'): continue
            f = line.rstrip('\n').split('\t')
            if len(f) < 8: continue
            d = parse_info(f[7]); typ = d.get('SVTYPE', '')
            if typ not in {'INS','DEL','INV','DUP','CNV'}: continue
            pos = iv(f[1]); end = iv(d.get('END', pos), pos)
            svlen = iv(d.get('SVLEN', 0)); length = abs(svlen) or abs(end-pos)
            if length < 50: continue
            reads = {x for x in d.get('RNAMES', '').split(',') if x not in {'', '.', 'NA'}}
            rows.append({'chrom': f[0], 'typ': typ, 'pos': pos, 'end': end,
                         'length': length, 'reads': reads, 'callers': {caller},
                         'source_ids': [f[2]]})
    return rows

def close(a, b):
    return (a['chrom'] == b['chrom'] and a['typ'] == b['typ'] and
            abs(a['pos'] - b['pos']) <= 100 and
            abs(a['length'] - b['length']) <= 50)

def main():
    merged = []
    for caller, path in SPECS:
        for row in read(path, caller):
            for item in merged:
                if close(row, item):
                    item['reads'] |= row['reads']; item['callers'] |= row['callers']; item['source_ids'] += row['source_ids']; break
            else: merged.append(row)
    merged.sort(key=lambda x: (x['chrom'], x['pos'], x['typ'], x['length']))
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / 'HG002.joint_threecaller_nocutesv.minisv.vcf'
    with out.open('w') as fh:
        fh.write('##fileformat=VCFv4.2\n##source=HG002_Sniffles2_LongcallD_TRGTdenovo_union_no_cuteSV\n')
        fh.write('##INFO=<ID=SOURCE_CALLERS,Number=.,Type=String,Description="Input callers">\n')
        fh.write('##INFO=<ID=SOURCE_IDS,Number=.,Type=String,Description="Input record IDs">\n')
        fh.write('##INFO=<ID=RNAMES,Number=.,Type=String,Description="Supporting read names">\n')
        fh.write('##INFO=<ID=SUPPORT,Number=1,Type=Integer,Description="Supporting read count">\n')
        fh.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n')
        for i, x in enumerate(merged, 1):
            svlen = x['length'] if x['typ'] == 'INS' else -x['length'] if x['typ'] == 'DEL' else x['length']
            end = x['pos'] if x['typ'] == 'INS' else x['end']
            info = [f'SVTYPE={x["typ"]}', f'SVLEN={svlen}', f'END={end}',
                    f'SOURCE_CALLERS={",".join(sorted(x["callers"]))}',
                    f'SOURCE_IDS={",".join(x["source_ids"])}',
                    f'RNAMES={",".join(sorted(x["reads"]))}', f'SUPPORT={len(x["reads"])}']
            fh.write(f'{x["chrom"]}\t{x["pos"]}\tJOINT3_HG002.{i}\tN\t<{x["typ"]}>\t.\tPASS\t' + ';'.join(info) + '\n')
    print(f'events={len(merged)} output={out}')

if __name__ == '__main__': main()
