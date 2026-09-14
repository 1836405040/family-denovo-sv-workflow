#!/usr/bin/env python3
import argparse, csv, glob, re
from pathlib import Path

def info(s):
    d={}
    for x in s.split(';'):
        if '=' in x:
            k,v=x.split('=',1); d[k]=v
    return d

def val(d,k,default=0):
    try: return int(str(d.get(k,default)).split(',')[0])
    except: return default

def read_vcf(path, sample, hap):
    rows=[]
    for line in open(path, errors='replace'):
        if line.startswith('#'): continue
        f=line.rstrip().split('\t')
        if len(f)<8: continue
        d=info(f[7]); typ=d.get('SVTYPE','')
        pos=int(f[1]); ref,alt=f[3],f[4]
        # paftools.js call emits ordinary REF/ALT records without SVTYPE or
        # SVLEN. Infer indel type/length from allele strings and retain only
        # structural-scale events (>=50 bp).
        if not typ:
            if alt.startswith('<'):
                typ=alt.strip('<>')
            elif len(alt)>len(ref): typ='INS'
            elif len(ref)>len(alt): typ='DEL'
            else: typ='SNV'
        if typ not in {'INS','DEL','DUP','INV','CNV'}: continue
        if 'SVLEN' in d: svlen=val(d,'SVLEN')
        elif typ=='INS': svlen=len(alt)-len(ref)
        elif typ=='DEL': svlen=-(len(ref)-len(alt))
        else: svlen=val(d,'END',pos)-pos
        if abs(svlen)<50: continue
        end=val(d,'END',pos+abs(svlen) if typ=='DEL' else pos)
        rows.append({'sample':sample,'hap':hap,'id':f[2],'chrom':f[0], 'pos':pos, 'end':end,
                     'svtype':typ,'svlen':svlen,'source':str(path)})
    return rows

def match(a,b,pos_tol=100,len_tol=50):
    if a['chrom']!=b['chrom'] or a['svtype']!=b['svtype']: return False
    if abs(a['pos']-b['pos'])>pos_tol: return False
    # For insertions END is often POS; compare absolute event lengths.
    return abs(abs(a['svlen'])-abs(b['svlen']))<=len_tol

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    root=Path(a.root); vdir=root/'hg002_trio_nocutesv_v1'/'assembly_derived_v1'/'vcf'
    allrows=[]
    for s in ('HG002','HG003','HG004'):
        for h in (1,2):
            p=vdir/f'{s}.hap{h}.asm5.vcf'
            if p.exists(): allrows += read_vcf(p,s,h)
    child=[x for x in allrows if x['sample']=='HG002']
    parents=[x for x in allrows if x['sample'] in ('HG003','HG004')]
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    fields=['child_sample','child_hap','child_id','chrom','pos','end','svtype','svlen','child_hap_support','parent_match_count','parent_matches','assembly_derived_class','independent_of_minisv']
    with out.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t'); w.writeheader()
        for x in child:
            pm=[p for p in parents if match(x,p)]
            # A candidate is de novo only when both child haplotypes support it
            # and no parental haplotype matches. One-haplotype calls are retained
            # as lower-confidence candidates for manual review.
            samechild=[c for c in child if c['svtype']==x['svtype'] and c['chrom']==x['chrom'] and abs(c['pos']-x['pos'])<=100 and abs(abs(c['svlen'])-abs(x['svlen']))<=50]
            both=(len({c['hap'] for c in samechild})==2)
            cls='putative_DNM_both_child_haps' if both and not pm else ('child_only_one_hap_no_parent_match' if not pm else 'inherited_or_parent_match')
            w.writerow({'child_sample':'HG002','child_hap':x['hap'],'child_id':x['id'],'chrom':x['chrom'],'pos':x['pos'],'end':x['end'],'svtype':x['svtype'],'svlen':x['svlen'],'child_hap_support':int(both),'parent_match_count':len(pm),'parent_matches':';'.join(f"{p['sample']}.hap{p['hap']}:{p['id']}" for p in pm),'assembly_derived_class':cls,'independent_of_minisv':'YES'})
    # Event-level deduplication across the two child haplotypes. This is the
    # preferred table for downstream comparison; the row-level table above
    # preserves every paftools record for auditability.
    evout=out.with_name('assembly_derived_dnm_events.tsv')
    clusters=[]
    for x in child:
        placed=False
        for cl in clusters:
            r=cl[0]
            if match(x,r): cl.append(x); placed=True; break
        if not placed: clusters.append([x])
    ef=['chrom','pos','end','svtype','svlen','child_haps','parent_match_count','parent_matches','assembly_derived_class','independent_of_minisv']
    with evout.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=ef,delimiter='\t'); w.writeheader()
        for cl in clusters:
            r=cl[0]; pm=[p for p in parents if match(r,p)]; hs=sorted({x['hap'] for x in cl})
            both=len(hs)==2
            cls='putative_DNM_both_child_haps' if both and not pm else ('child_only_one_hap_no_parent_match' if not pm else 'inherited_or_parent_match')
            w.writerow({'chrom':r['chrom'],'pos':r['pos'],'end':r['end'],'svtype':r['svtype'],'svlen':r['svlen'],'child_haps':','.join(map(str,hs)),'parent_match_count':len(pm),'parent_matches':';'.join(f"{p['sample']}.hap{p['hap']}:{p['id']}" for p in pm),'assembly_derived_class':cls,'independent_of_minisv':'YES'})
    from collections import Counter
    c=Counter()
    for r in csv.DictReader(open(out),delimiter='\t'): c[r['assembly_derived_class']]+=1
    ec=Counter(r['assembly_derived_class'] for r in csv.DictReader(open(evout),delimiter='\t'))
    print('child_records=%d row_classes=%s event_count=%d event_classes=%s' % (len(child),dict(c),len(clusters),dict(ec)))

if __name__=='__main__': main()
