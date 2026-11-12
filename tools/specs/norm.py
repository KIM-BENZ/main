import json
d=json.load(open('all.json'))
def ranges_from_hdr(r):
    n=len(r['trims']); rows={}
    for t,a,b,y in r.get('spec_hdr',[]): rows.setdefault(y,[]).append((t,a,b))
    for y in sorted(rows,reverse=True):
        cs=sorted(rows[y],key=lambda x:x[1])
        cs=[c for c in cs if c[1]>=0]
        if len(cs)==n and n>0: return [(a,b) for _,a,b in cs]
        if len(cs)==1 and n>1 and cs[0][1]==0 and cs[0][2]>=r['nval']: return [(0,r['nval'])]*n
    return None
def norm(r):
    n=len(r['trims']); m=r['nval']; spec=r['spec']
    if not spec: return [],'nospec'
    rg=None; st='ok'
    if m==n: rg=[(k,k+1) for k in range(n)]
    else:
        rg=ranges_from_hdr(r)
        if rg: st='hdr'
        elif n>1 and all(len(set(v for v in s['vals'] if v))<=1 for s in spec):
            rows=[dict(g=s['g'],label=s['label'],vals=[next((v for v in s['vals'] if v),'')]*n) for s in spec]
            return rows,'replicated'
        else: return [], f'MISMATCH nval={m} n={n}'
    rows=[]
    for s in spec:
        vals=[]
        for a,b in rg:
            seg=[v for v in s['vals'][a:b] if v]
            u=[]
            [u.append(v) for v in seg if v not in u]
            vals.append(' '.join(u))
        rows.append(dict(g=s['g'],label=s['label'],vals=vals))
    return rows,st
out={}
for p,r in d.items():
    if 'error' in r: out[p]=r; print(p,'ERROR'); continue
    r['spec_n'],r['spec_status']=norm(r); out[p]=r
    if r['spec_status'] not in ('ok',): print(p,r['spec_status'],r['nval'],len(r['trims']), [h[:3] for h in r['spec_hdr']][:6])
json.dump(out,open('norm.json','w'),ensure_ascii=False)
