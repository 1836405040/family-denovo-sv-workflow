#!/usr/bin/env python3
"""Build HG002 child-only Minisv input from Sniffles2 and LongcallD."""
from pathlib import Path
import csv

ROOT = Path('${PROJECT_ROOT}/results/formal_chm13/innovation/pedsv_ml/pilot_v1')
CHILD = 'HG002'
CALLER_ROOT = ROOT / 'hg002_trio_nocutesv_v1' / 'callers'
OUT = ROOT / 'hg002_trio_nocutesv_v1' / 'joint_input'

def iv(v, default=0):
    try: return int(str(v).split(',', 1)[0])
    except (TypeError, ValueError): return default

def info(s): return {x.split('=', 1)[0]: x.split('=', 1)[1] for x in s.split(';') if '=' in x}

def read(path, caller):
    out=[]
    if not path.exists(): return out
    with path.open() as h:
        for line in h:
            if line.startswith('#'): continue
            f=line.rstrip('\n').split('\t')
            if len(f)<8: continue
            d=info(f[7]); typ=d.get('SVTYPE','')
            if typ not in {'INS','DEL','INV','DUP'}: continue
            pos=iv(f[1]); end=iv(d.get('END',pos),pos); svlen=iv(d.get('SVLEN',0)); length=abs(svlen) or abs(end-pos)
            ids={x for x in d.get('RNAMES','').split(',') if x and x not in {'.','NA'}}
            out.append(((f[0],typ,pos,end,length),f,d,ids,caller))
    return out

def main():
    specs=[('sniffles2',CALLER_ROOT/'sniffles2/HG002.child_only.minisv.vcf'),('longcallD',CALLER_ROOT/'longcallD/HG002.child_only.minisv.vcf')]
    merged={}
    for caller,path in specs:
        for key,f,d,ids,source in read(path,caller):
            m=merged.setdefault(key,{'f':f[:],'d':d.copy(),'reads':set(),'callers':set(),'source_ids':[]})
            m['reads'].update(ids); m['callers'].add(source); m['source_ids'].append(f[2])
    OUT.mkdir(parents=True,exist_ok=True); vcf=OUT/'HG002.joint_nocutesv.minisv.vcf'
    with vcf.open('w') as out:
        out.write('##fileformat=VCFv4.2\n##source=HG002_Sniffles2_LongcallD_union_no_cuteSV\n')
        out.write('##INFO=<ID=SOURCE_CALLERS,Number=.,Type=String,Description="Input callers">\n##INFO=<ID=SOURCE_IDS,Number=.,Type=String,Description="Input record IDs">\n##INFO=<ID=RNAMES,Number=.,Type=String,Description="Supporting read names">\n##INFO=<ID=SUPPORT,Number=1,Type=Integer,Description="Supporting read count">\n')
        out.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n')
        for i,(key,m) in enumerate(sorted(merged.items(),key=lambda z:(z[0][0],z[0][2],z[0][1],z[0][4])),1):
            f,d=m['f'],m['d']; d['SOURCE_CALLERS']=','.join(sorted(m['callers'])); d['SOURCE_IDS']=','.join(m['source_ids']); d['RNAMES']=','.join(sorted(m['reads'])); d['SUPPORT']=str(len(m['reads']))
            out.write('\t'.join([f[0],f[1],f'JOINT_HG002_NOCUTESV.{i}',f[3],f[4],f[5],f[6],';'.join(f'{k}={v}' for k,v in d.items())])+'\n')
    with (OUT/'joint_input_manifest.tsv').open('w',newline='') as h:
        fields=['joint_id','chrom','pos','svtype','end','svlen','support','source_callers','source_ids']; w=csv.DictWriter(h,fieldnames=fields,delimiter='\t'); w.writeheader()
        for i,(key,m) in enumerate(sorted(merged.items(),key=lambda z:(z[0][0],z[0][2],z[0][1],z[0][4])),1):
            w.writerow({'joint_id':f'JOINT_HG002_NOCUTESV.{i}','chrom':key[0],'pos':key[2],'svtype':key[1],'end':key[3],'svlen':key[4],'support':len(m['reads']),'source_callers':','.join(sorted(m['callers'])),'source_ids':','.join(m['source_ids'])})
    print(f'events={len(merged)} output={vcf}')

if __name__ == '__main__': main()
