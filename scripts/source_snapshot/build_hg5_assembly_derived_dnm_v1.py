#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path('${PROJECT_ROOT}/results/formal_chm13/innovation/pedsv_ml/pilot_v1')
OUT = ROOT / 'hg5_assembly/assembly_derived_dnm_v1'
SAMPLES = ['NA12879', 'NA12881', 'NA12882', 'NA12885', 'NA12886']
PARENTS = ['NA12877', 'NA12878']

def info(s):
    d = {}
    for x in s.split(';'):
        if '=' in x:
            k, v = x.split('=', 1); d[k] = v
    return d

def iv(v, default=0):
    try: return int(str(v).split(',', 1)[0])
    except (TypeError, ValueError): return default

def read_vcf(path, sample, hap):
    rows = []
    if not path.exists(): return rows
    with path.open(errors='replace') as fh:
        for line in fh:
            if line.startswith('#'): continue
            f = line.rstrip('\n').split('\t')
            if len(f) < 8: continue
            d = info(f[7]); typ = d.get('SVTYPE', '')
            pos = iv(f[1]); end = iv(d.get('END', pos), pos)
            if typ not in {'INS','DEL','DUP','INV','CNV'}:
                if f[4].startswith('<'): typ = f[4].strip('<>')
                elif len(f[4]) > len(f[3]): typ = 'INS'
                elif len(f[3]) > len(f[4]): typ = 'DEL'
                else: continue
            svlen = iv(d.get('SVLEN', 0))
            if not svlen:
                svlen = len(f[4]) - len(f[3]) if typ == 'INS' else (-(len(f[3])-len(f[4])) if typ == 'DEL' else end-pos)
            if abs(svlen) < 50: continue
            rows.append({'sample':sample,'hap':hap,'id':f[2],'chrom':f[0],'pos':pos,'end':end,'svtype':typ,'svlen':svlen})
    return rows

def match(a, b):
    return (a['chrom'] == b['chrom'] and a['svtype'] == b['svtype'] and
            abs(a['pos'] - b['pos']) <= 100 and
            abs(abs(a['svlen']) - abs(b['svlen'])) <= 50)

def main():
    vdir = OUT / 'vcf'
    parent = []
    for s in PARENTS:
        for h in (1, 2): parent += read_vcf(vdir / f'{s}.hap{h}.asm5.vcf', s, h)
    summary = []
    for s in SAMPLES:
        child = []
        for h in (1, 2): child += read_vcf(vdir / f'{s}.hap{h}.asm5.vcf', s, h)
        clusters = []
        for x in child:
            for cl in clusters:
                if match(x, cl[0]): cl.append(x); break
            else: clusters.append([x])
        rows = []
        classes = {'putative_DNM_both_child_haps':0,'child_only_one_hap_no_parent_match':0,'inherited_or_parent_match':0}
        for cl in clusters:
            x = cl[0]; hs = sorted({z['hap'] for z in cl}); pm = [p for p in parent if match(x, p)]
            if len(hs) == 2 and not pm: cls = 'putative_DNM_both_child_haps'
            elif not pm: cls = 'child_only_one_hap_no_parent_match'
            else: cls = 'inherited_or_parent_match'
            classes[cls] += 1
            rows.append({'sample':s,'chrom':x['chrom'],'pos':x['pos'],'end':x['end'],'svtype':x['svtype'],'svlen':x['svlen'],'child_haps':','.join(map(str,hs)),'parent_match_count':len(pm),'parent_matches':';'.join(f"{z['sample']}.hap{z['hap']}:{z['id']}" for z in pm),'assembly_derived_class':cls,'independent_of_minisv':'YES'})
        sdir = OUT / s; sdir.mkdir(parents=True, exist_ok=True)
        fields = ['sample','chrom','pos','end','svtype','svlen','child_haps','parent_match_count','parent_matches','assembly_derived_class','independent_of_minisv']
        with (sdir / 'assembly_derived_dnm_events.tsv').open('w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=fields, delimiter='\t'); w.writeheader(); w.writerows(rows)
        summary.append({'sample':s,'child_records':len(child),'event_count':len(rows),**classes})
    OUT.mkdir(parents=True, exist_ok=True)
    sf = ['sample','child_records','event_count','putative_DNM_both_child_haps','child_only_one_hap_no_parent_match','inherited_or_parent_match']
    with (OUT / 'assembly_derived_summary.tsv').open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=sf, delimiter='\t'); w.writeheader(); w.writerows(summary)
    print(OUT / 'assembly_derived_summary.tsv')

if __name__ == '__main__': main()
