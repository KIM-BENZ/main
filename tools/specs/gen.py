import json,re,pdfplumber
d=json.load(open('norm.json')); models=json.load(open('models.json'))
pdf=pdfplumber.open('/tmp/claude-0/spec.pdf')
def price(t):
    t=t.replace(' ','').replace('원','')
    m=re.match(r'^(?:(\d+)억)?(?:([\d,]+)만)?$',t)
    if not m or not (m.group(1) or m.group(2)): return None
    return int(m.group(1) or 0)*10000+int((m.group(2) or '0').replace(',',''))
ABBR=[(r'\b4M\+','4MATIC+'),(r'\b4M\b','4MATIC'),(r'\bAV\b','AVANTGARDE'),(r'\bCP\b','Coupé'),(r'\bCoupe\b','Coupé'),
      (r'\bEX\b','EXCLUSIVE'),(r'\bamg line\b','AMG Line'),(r'\bAMG LINE\b','AMG Line'),(r'\bprogressive\b','Progressive'),
      (r'\blong\b','Long'),(r'\(MY2\d\)',''),(r'\bExclusive\b','EXCLUSIVE'),(r'\bMM\b','Maybach'),(r'AMG-GT','AMG GT'),(r'^MAYBACH','Maybach'),(r'\bA220\b','A 220'),(r'^G63\b','AMG G 63'),(r'^GLC (43|53)\b',r'AMG GLC \1'),
      (r'Maybach S(\d{3})',r'Maybach S \1'),(r'^SL (43|63)',r'AMG SL \1'),(r'EQ-Technology','EQ Technology'),(r'\bE Performance','E PERFORMANCE'),(r'\bHybrid\b','HYBRID')]
def tname(t):
    for a,b in ABBR: t=re.sub(a,b,t)
    t=re.sub(r'(\d)([dD])\b',r'\1 d',t) if re.search(r'\b[EG]?\s?\d{3}d\b',t) else t
    return re.sub(r'\s+',' ',t).strip()
def sim(a,b):
    A=set(re.findall(r'\w+',a.lower())); B=set(re.findall(r'\w+',b.lower()))
    return len(A&B)
def page_date(p):
    m=re.search(r'20\d\d-\d\d-\d\d', pdf.pages[p-1].extract_text() or ''); return m.group(0) if m else ''
OVR={31:[7750,8100]}
GROUPS=[('치수',('전장','전폭','축거','승차','트렁크','프렁크','적재','휠베이스','전고')),
        ('파워트레인',('연료','엔진','배기량','최고출력','최대토크','변속','모터','배터리','충전','시스템','출력','토크')),
        ('구동',('굴림','구동','서스펜션','브레이크','타이어')),
        ('연비 · 전비',('연비','도심','복합','고속','연료탱크','전비','주행','시내','에너지','CO2','1회')),
        ('성능',('공차','중량','가속','제로백','최고속도','최고 속도','0-100'))]
def canon(label):
    L=label.replace(' ','')
    if L.startswith('최고속도'): return '성능'
    for name,keys in GROUPS:
        if any(L.startswith(k.replace(' ','')) for k in keys): return name
    return ''
def build(p):
    r=d[str(p)]; n=len(r['trims'])
    trims=[]
    for i,t in enumerate(r['trims']):
        pr=price(t['price'])
        if p in OVR: pr=OVR[p][i]
        trims.append([tname(t['name']) or f'트림 {i+1}', pr])
    if p==45: trims[1][0]='Maybach GLS 600 4MATIC MANUFAKTUR'
    spec=[]; lastg=''
    for s in r['spec_n']:
        lab=re.sub(r'\s+',' ',s['label']).strip()
        G=canon(lab)
        if not G and s['g'] and canon(s['g']):
            if not lab.replace(' ','').startswith(s['g'].replace(' ','')): lab=s['g']+' '+lab
            G=canon(lab) or canon(s['g'])
        g=G or lastg or s['g']; lastg=g
        vals=[v if v else '-' for v in s['vals']]
        if all(v=='-' for v in vals) and not lab: continue
        spec.append([g,lab,vals[0] if len(set(vals))==1 else vals])
    order=[n for n,_ in GROUPS]
    spec.sort(key=lambda r_: order.index(r_[0]) if r_[0] in order else 99)
    opts=[]
    for o in r['opts']:
        g,vals,raw=o[0],o[1],o[2]; reds=o[3] if len(o)>3 else [False]*n
        txt=[v for v in vals if v]
        if not txt: continue
        if all(v.strip() in ('옵션','option','OPTION') for v in txt): continue
        # trim-name header rows
        headerish = (not g) or len(set(vals))>1
        if headerish and all((max([sim(v,t['name']) for t in r['trims']]+[0])>=2 and len(v)<32) or v in ('AMG Line','MANUFAKTUR') for v in txt): continue
        if all(re.sub(r'\s','',v) in {re.sub(r'\s','',t['name']) for t in r['trims']} for v in txt): continue
        if headerish and all(any(t['name'].replace(' ','').lower().endswith(v.replace(' ','').lower()) for t in r['trims']) for v in txt): continue
        if any('EoQpSt' in v for v in txt): continue
        g={' 옵션':'주요 옵션','옵션':'주요 옵션','실내편의 옵션':'실내 편의 옵션','외장편의 옵션':'외장 편의 옵션'}.get(g,g)
        if not g and any(o_[0] and o_[0]!='참고' for o_ in opts): g='참고'
        vals=[v if v else '-' for v in vals]
        red=''.join('1' if x else '0' for x in reds)
        if '안전' in g and len(set(vals))>1: g='시트 · 기타 안내'
        row=[g, vals[0] if len(set(vals))==1 else vals]
        if '1' in red: row.append(red if len(set(red))>1 else '1')
        opts.append(row)
    return dict(p=p,d=page_date(p),tr=trims,s=spec,o=opts)
out={}
for m in models:
    if not m.get('pages'): continue
    out[m['name']+'|'+m['my']]=[build(p) for p in m['pages']]
js=('/* =========================================================\n'
    '   차종별 웹용 제원·옵션표 데이터 (models.html에서 사용)\n'
    '   - 키: \'차종명|연식\' (models.html MODELS 목록과 같아야 함)\n'
    '   - 섹션 = 제원표 1장: p(이미지 번호) d(기준일) tr(트림·가격) s(제원) o(옵션)\n'
    '   - 값이 문자열 하나면 전 트림 공통, 배열이면 트림별. \'-\' = 미적용\n'
    '   - o의 세 번째 값: 원본에서 빨간 글씨(강조)였던 칸 (1=강조)\n'
    '   - 원본: 2026-10-20 제원표 PDF에서 자동 추출\n'
    '========================================================= */\n'
    'var SPEC_DETAIL = '+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';\n')
open('/home/claude/main/specs-data.js','w',encoding='utf-8').write(js)
print(len(out),'models', len(js)//1024,'KB')
# summary of trims per section
for k,secs in out.items():
    print(k, ' || '.join(', '.join(f'{t[0]}:{t[1]}' for t in s['tr']) for s in secs))
