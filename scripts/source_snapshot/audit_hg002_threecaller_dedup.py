from pathlib import Path
from collections import defaultdict
ROOT=Path('${PROJECT_ROOT}/results/formal_chm13/innovation/pedsv_ml/pilot_v1')
specs=[('sniffles2',ROOT/'hg002_trio_nocutesv_v1/callers/sniffles2/HG002.child_only.minisv.vcf'),('longcallD',ROOT/'hg002_trio_nocutesv_v1/callers/longcallD/HG002.child_only.minisv.vcf'),('trgtdn',ROOT/'hg002_trio_nocutesv_v1/trgt_adapter_xx_v1/HG002.TRGTdenovo.minisv.vcf')]
def iv(x):
 try:return int(str(x).split(',',1)[0])
 except:return 0
def info(s):return {x.split('=',1)[0]:x.split('=',1)[1] for x in s.split(';') if '=' in x}
def close(a,b):return a[0]==b[0] and a[1]==b[1] and abs(a[2]-b[2])<=100 and abs(a[4]-b[4])<=50
allrows=[]
for caller,p in specs:
 rows=[]
 for line in p.open():
  if line.startswith('#'):continue
  f=line.rstrip().split('\t'); d=info(f[7]); typ=d.get('SVTYPE',''); pos=iv(f[1]); end=iv(d.get('END',pos)); ln=abs(iv(d.get('SVLEN',0))) or abs(end-pos)
  if typ in {'INS','DEL','INV','DUP','CNV'} and ln>=50: rows.append((f[0],typ,pos,end,ln))
 print(caller,'raw_qualified',len(rows))
 allrows += [(x,caller) for x in rows]
clusters=[]
for x,caller in allrows:
 for cl in clusters:
  if close(x,cl[0][0]):cl.append((x,caller));break
 else:clusters.append([(x,caller)])
print('raw_total',len(allrows),'clusters',len(clusters),'removed',len(allrows)-len(clusters))
print('cluster_caller_cardinality', {k:sum(1 for cl in clusters if len({c for _,c in cl})==k) for k in (1,2,3)})
