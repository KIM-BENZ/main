import pdfplumber, json, re, sys

def clean(t):
    if t is None: return ''
    t = t.replace('(cid:9)', ' ').replace('\n', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    if t.lower() not in ('option',):
        t = re.sub(r'(^|\s)(opt|tion|OPTION|option)(?=\s|$)', ' ', t).strip()
        t = re.sub(r'\s+', ' ', t)
    return t

PRICE = re.compile(r'(\d[\d,]*\s*만\s*원?$)|(\d억)|^미정$')
LABELS = ('전폭고','전장','축거','승차정원','트렁크','연료','엔진','배기량','최고출력','최대토크','변속기','굴림방식','서스펜션',
          '브레이크','타이어','복합','도심','공차중량','가속성능','제로백','최고속도','최고 속도','연료탱크','배터리','충전','주행거리','1회','모터','시내','전비','공차','에너지','구동방식','차량','휠베이스','최고','가속')

def parse_page(pdf, pno):
    pg = pdf.pages[pno-1]
    tabs = pg.find_tables()
    cells=[]
    for t in tabs:
        for (x0,y0,x1,y1) in t.cells:
            if x1-x0<1 or y1-y0<1: continue
            cr = pg.crop((x0,y0,x1,y1))
            txt = clean(cr.extract_text())
            red = False
            ch = [c for c in cr.chars if c['text'].strip()]
            if ch:
                def isred(col):
                    if not col: return False
                    col = tuple(col)
                    if len(col)==3: return col[0]>0.6 and col[1]<0.35 and col[2]<0.35
                    if len(col)==4: return col[1]>0.6 and col[2]>0.6 and col[3]<0.3 and col[0]<0.3
                    return False
                red = sum(isred(c.get('non_stroking_color')) for c in ch) > len(ch)*0.6
            cells.append(dict(x0=x0,y0=y0,x1=x1,y1=y1,t=txt,red=red))
    xs = sorted(set([c['x0'] for c in cells]+[c['x1'] for c in cells]))
    X=[]
    for x in xs:
        if not X or x-X[-1]>2.5: X.append(x)
    col=lambda x: min(range(len(X)), key=lambda i: abs(X[i]-x))
    for c in cells: c['c0']=col(c['x0']); c['c1']=col(c['x1'])
    W=pg.width
    # price cells: right half, top area
    pcs=[c for c in cells if c['x0']>W*0.3 and PRICE.search(c['t'].replace(' ','')) and c['y0']<pg.height*0.3 and len(c['t'])<45]
    if not pcs: return dict(page=pno,error='no price')
    py=min(c['y0'] for c in pcs)
    pcs=[c for c in pcs if abs(c['y0']-py)<3]
    pcs.sort(key=lambda c:c['x0'])
    bx=min(c['c0'] for c in pcs); bxe=max(c['c1'] for c in pcs)
    trims=[]
    for p in pcs:
        above=[c for c in cells if c['c0']==p['c0'] and c['c1']==p['c1'] and c['y1']<=p['y0']+1.5 and c['t']]
        above.sort(key=lambda c:-c['y1'])
        m_=re.match(r'^(.*?)\s*(\d[\d,]*\s*만\s*원?|\d억.*)$', p['t'])
        if m_ and m_.group(1) and not above:
            trims.append(dict(name=m_.group(1), price=m_.group(2), c0=p['c0'], c1=p['c1'], xc=(p['x0']+p['x1'])/2)); continue
        trims.append(dict(name=above[0]['t'] if above else '', price=p['t'], c0=p['c0'], c1=p['c1'], xc=(p['x0']+p['x1'])/2))
    tcols=[(tr['c0'],tr['c1']) for tr in trims]
    def tidxc(c): return [i for i,tr in enumerate(trims) if c['x0']-1<=tr['xc']<=c['x1']+1]
    tnames=set(tr['name'].replace(' ','') for tr in trims)
    # options: right-region cells below price row
    py1=max(c['y1'] for c in pcs)
    R=[c for c in cells if c['x0']>=X[bx]-2 and c['x1']<=X[bxe]+2 and c['y0']>=py1-0.5]
    bands={}
    for c in R: bands.setdefault(round(c['y0']*2)/2,[]).append(c)
    opts=[]; group=''
    keys=sorted(bands)
    # merge bands that are within 0.6
    for key in keys:
        cs=sorted(bands[key], key=lambda c:c['x0'])
        if not any(c['t'] for c in cs): continue
        full = len(cs)==1 and len(tidxc(cs[0]))==len(trims)
        tx=cs[0]['t']
        txn=tx.replace(' ','')
        if full and (re.search(r'옵션|option', txn, re.I) and len(txn)<=12):
            if txn.lower()!='option':
                group=re.sub(r'옵션$',' 옵션',txn).replace('  ',' ')
            continue
        if all((c['t'].replace(' ','') in tnames) or not c['t'] for c in cs): continue
        vals=['']*len(trims); reds=[False]*len(trims)
        for c in cs:
            for i in tidxc(c): vals[i]=c['t']; reds[i]=c['red']
        if not any(vals): continue
        opts.append([group, vals, [c['t'] for c in cs], reds])
    # spec
    left=[c for c in cells if c['x1']<=X[bx]+1]
    lab=[c for c in left if any(c['t'].startswith(k) for k in ('축거','전폭고','승차정원','연료','전장'))]
    if not lab: return dict(page=pno,trims=trims,opts=opts,spec=[],warn='no spec labels')
    from collections import Counter
    lc0,lc1=Counter((c['c0'],c['c1']) for c in lab).most_common(1)[0][0]
    gcells=[c for c in left if c['c1']<=lc0 and c['t']]
    vcells=[c for c in left if c['c0']>=lc1]
    labels=sorted([c for c in left if c['c0']==lc0 and c['c1']==lc1 and c['t']], key=lambda c:c['y0'])
    vmax=max([c['c1'] for c in vcells if c['t']] or [lc1+1])
    atom=list(range(lc1,vmax))
    first_lab=min(c['y0'] for c in lab)
    labels=[L for L in labels if L['y0']>=first_lab-1]
    spec=[]
    for L in labels:
        cy=(L['y0']+L['y1'])/2
        vs=['']*len(atom)
        for c in vcells:
            if c['y0']-0.5<=cy<=c['y1']+0.5 and c['t']:
                for k,a in enumerate(atom):
                    if c['c0']<=a<c['c1']: vs[k]=c['t']
        g=''
        for G in gcells:
            if G['y0']-0.5<=cy<=G['y1']+0.5: g=G['t']
        if not g and gcells:
            gl=[G for G in gcells if len(G['t'])<=6]
            if gl: g=min(gl,key=lambda G: min(abs(cy-G['y0']),abs(cy-G['y1'])))['t']
        if not any(vs) and not any(L['t'].startswith(k) for k in LABELS): continue
        if spec and spec[-1]['vals']==vs and spec[-1]['g']==g and any(vs):
            spec[-1]['label']+=' '+L['t']; continue
        spec.append(dict(g=g,label=L['t'],vals=vs))
    # spec header: cells in value cols just above first label
    hdr=[c for c in vcells if c['t'] and c['y1']<=first_lab+1 and c['y1']>=first_lab-40]
    hdr=[(c['t'],c['c0']-lc1,c['c1']-lc1,round(c['y0'])) for c in sorted(hdr,key=lambda c:(c['y0'],c['x0']))]
    return dict(page=pno,trims=trims,opts=opts,spec=spec,nval=len(atom),spec_hdr=hdr)

if __name__=='__main__':
    pdf=pdfplumber.open('/tmp/claude-0/spec.pdf')
    out={}
    for p in [int(a) for a in sys.argv[1:]]:
        try: out[p]=parse_page(pdf,p)
        except Exception as e:
            import traceback; out[p]=dict(page=p,error=traceback.format_exc()[-300:])
    print(json.dumps(out,ensure_ascii=False,indent=0))
