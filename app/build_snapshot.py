import csv, io, json, os, re, time, unicodedata, urllib.request, zipfile
from collections import defaultdict

BASE='https://cdn.tse.jus.br/estatistica/sead'
DATASET='https://dadosabertos.tse.jus.br/dataset/candidatos-2026'
URLS={
 'cand':BASE+'/odsele/consulta_cand/consulta_cand_2026.zip',
 'supp':BASE+'/odsele/consulta_cand_complementar/consulta_cand_complementar_2026.zip',
 'assets':BASE+'/odsele/bem_candidato/bem_candidato_2026.zip',
 'social':BASE+'/odsele/consulta_cand/rede_social_candidato_2026.zip',
}
HEADERS={'User-Agent':'Mozilla/5.0 (RAIO-X Eleicoes 2026; dados publicos)','Accept':'application/zip,*/*','Referer':DATASET}
BAD={'','#NULO','#NE','NULO','NULL'}

def norm(v):
 s=unicodedata.normalize('NFD',str(v or ''))
 return ''.join(c for c in s if unicodedata.category(c)!='Mn').upper().strip()

def good(v):
 s=str(v or '').strip()
 return bool(s) and s.upper() not in BAD and not s.startswith('#')

def pick(*vals):
 for v in vals:
  if good(v): return str(v).strip()
 return ''

def download(url,optional=False):
 last=None
 for attempt in range(1,6):
  try:
   req=urllib.request.Request(url,headers=HEADERS)
   with urllib.request.urlopen(req,timeout=180) as r: data=r.read()
   if len(data)<100: raise RuntimeError('download pequeno')
   print('download ok',url,len(data),'attempt',attempt)
   return data
  except Exception as e:
   last=e; print('download fail',attempt,url,repr(e)); time.sleep(min(10,attempt*2))
 if optional:
  print('optional skipped',url,repr(last)); return None
 raise SystemExit(f'falha download {url}: {last!r}')

def rows_from_zip(data,needle):
 out=[]
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  names=[n for n in z.namelist() if n.lower().endswith('.csv') and needle in n.lower()]
  if not names: names=[n for n in z.namelist() if n.lower().endswith('.csv')]
  for name in names:
   raw=z.read(name); text=None
   for enc in ('latin-1','utf-8-sig','cp1252'):
    try: text=raw.decode(enc); break
    except UnicodeDecodeError: pass
   if text is None: continue
   rd=csv.DictReader(io.StringIO(text),delimiter=';')
   if not rd.fieldnames or 'SQ_CANDIDATO' not in rd.fieldnames: continue
   out.extend(rd)
 return out

def merge_by_candidate(rows):
 out={}
 for r in rows:
  cid=(r.get('SQ_CANDIDATO') or '').strip()
  if not cid: continue
  cur=out.setdefault(cid,{})
  for k,v in r.items():
   if good(v): cur[k]=v.strip() if isinstance(v,str) else v
 return out

cand_rows=rows_from_zip(download(URLS['cand']),'consulta_cand_2026')
supp_rows=rows_from_zip(download(URLS['supp']),'consulta_cand_complementar_2026')
asset_rows=rows_from_zip(download(URLS['assets']),'bem_candidato_2026')
social_rows=rows_from_zip(download(URLS['social']),'rede_social_candidato_2026')
main=merge_by_candidate(cand_rows); supp=merge_by_candidate(supp_rows)

assets=defaultdict(list); seen_assets=set()
for r in asset_rows:
 cid=(r.get('SQ_CANDIDATO') or '').strip()
 if not cid: continue
 order=pick(r.get('NR_ORDEM_CANDIDATO'),r.get('NR_ORDEM'))
 kind=pick(r.get('CD_TIPO_BEM_CANDIDATO'),r.get('DS_TIPO_BEM_CANDIDATO'),r.get('DS_TIPO_BEM'))
 desc=pick(r.get('DS_BEM_CANDIDATO')); raw=pick(r.get('VR_BEM_CANDIDATO')) or '0'
 key=(cid,'ord',order) if order else (cid,kind,desc,raw)
 if key in seen_assets: continue
 seen_assets.add(key)
 try: value=float(raw.replace('.','').replace(',','.'))
 except ValueError: value=0.0
 assets[cid].append({'type':pick(r.get('DS_TIPO_BEM_CANDIDATO'),r.get('DS_TIPO_BEM')),'description':desc,'value':value,'ordinal':order})

socials=defaultdict(list)
for r in social_rows:
 cid=(r.get('SQ_CANDIDATO') or '').strip(); url=pick(r.get('DS_URL'),r.get('DS_REDE_SOCIAL'))
 if cid and url and url not in socials[cid]: socials[cid].append(url)

base=[]
for cid,m in main.items():
 e=supp.get(cid,{})
 goods=sorted(assets.get(cid,[]),key=lambda x:x['value'],reverse=True)
 status=pick(e.get('DS_SITUACAO_CANDIDATO_PLEITO'),e.get('DS_DETALHE_SITUACAO_CAND'),e.get('DS_SITUACAO_CANDIDATURA'),m.get('DS_SITUACAO_CANDIDATURA'))
 total_status=pick(e.get('DS_SITUACAO_CANDIDATO_TOT'),e.get('DS_SIT_TOT_TURNO'),m.get('DS_SIT_TOT_TURNO'))
 superior=pick(e.get('SQ_CANDIDATO_SUPERIOR'),m.get('SQ_CANDIDATO_SUPERIOR'))
 base.append({
  'id':cid,'superiorId':superior,
  'name':pick(m.get('NM_URNA_CANDIDATO'),m.get('NM_CANDIDATO')),'civilName':pick(m.get('NM_CANDIDATO')),'socialName':pick(m.get('NM_SOCIAL_CANDIDATO'),e.get('NM_SOCIAL_CANDIDATO')),
  'number':pick(m.get('NR_CANDIDATO')),'office':pick(m.get('DS_CARGO')),'uf':pick(m.get('SG_UF')),
  'party':pick(m.get('SG_PARTIDO')),'partyNumber':pick(m.get('NR_PARTIDO')),'partyName':pick(m.get('NM_PARTIDO')),
  'status':status,'totalizationStatus':total_status,'detailStatus':pick(e.get('DS_DETALHE_SITUACAO_CAND')),
  'coalitionId':pick(m.get('SQ_COLIGACAO'),e.get('SQ_COLIGACAO')),'coalition':pick(m.get('NM_COLIGACAO'),e.get('NM_COLIGACAO')),'coalitionComposition':pick(m.get('DS_COMPOSICAO_COLIGACAO'),e.get('DS_COMPOSICAO_COLIGACAO')),
  'federation':pick(m.get('NM_FEDERACAO'),e.get('NM_FEDERACAO')),'federationComposition':pick(m.get('DS_COMPOSICAO_FEDERACAO'),e.get('DS_COMPOSICAO_FEDERACAO')),
  'occupation':pick(m.get('DS_OCUPACAO'),e.get('DS_OCUPACAO')),'education':pick(m.get('DS_GRAU_INSTRUCAO'),e.get('DS_GRAU_INSTRUCAO')),
  'birthDate':pick(m.get('DT_NASCIMENTO'),e.get('DT_NASCIMENTO')),'gender':pick(m.get('DS_GENERO'),e.get('DS_GENERO')),'race':pick(m.get('DS_COR_RACA'),e.get('DS_COR_RACA')),'maritalStatus':pick(m.get('DS_ESTADO_CIVIL'),e.get('DS_ESTADO_CIVIL')),
  'nationality':pick(m.get('DS_NACIONALIDADE'),e.get('DS_NACIONALIDADE')),'birthCity':pick(m.get('NM_MUNICIPIO_NASCIMENTO'),e.get('NM_MUNICIPIO_NASCIMENTO')),'birthUf':pick(m.get('SG_UF_NASCIMENTO'),e.get('SG_UF_NASCIMENTO')),
  'reelection':pick(e.get('ST_REELEICAO'),m.get('ST_REELEICAO')),
  'electionDescription':pick(m.get('DS_ELEICAO'),e.get('DS_ELEICAO')),'electionDate':pick(m.get('DT_ELEICAO'),e.get('DT_ELEICAO')),
  'sourceUpdated':' '.join(x for x in [pick(m.get('DT_GERACAO'),e.get('DT_GERACAO')),pick(m.get('HH_GERACAO'),e.get('HH_GERACAO'))] if x),
  'assetTotal':round(sum(x['value'] for x in goods),2),'assetCount':len(goods),'topAssets':goods[:12],'socials':socials.get(cid,[])[:12],
 })

by_id={c['id']:c for c in base}
for c in base: c['ticket']=[]
for child in base:
 parent=by_id.get(child.get('superiorId'))
 if parent:
  parent['ticket'].append({'id':child['id'],'name':child['name'],'civilName':child['civilName'],'office':child['office'],'uf':child['uf'],'party':child['party'],'number':child['number']})

roles={'GOVERNADOR':{'VICE-GOVERNADOR'},'PRESIDENTE':{'VICE-PRESIDENTE'},'SENADOR':{'1O SUPLENTE','2O SUPLENTE','1º SUPLENTE','2º SUPLENTE'}}
by_key=defaultdict(list)
for c in base: by_key[(c['uf'],c['number'],c['coalitionId'])].append(c)
for c in base:
 if c['ticket']: continue
 wanted=roles.get(norm(c['office']),set())
 if not wanted: continue
 for p in by_key[(c['uf'],c['number'],c['coalitionId'])]:
  if p['id']!=c['id'] and norm(p['office']) in wanted:
   c['ticket'].append({'id':p['id'],'name':p['name'],'civilName':p['civilName'],'office':p['office'],'uf':p['uf'],'party':p['party'],'number':p['number']})

if len(base)<100: raise SystemExit('snapshot pequeno')
with open('tse_candidates_2026.json','w',encoding='utf-8') as f: json.dump(base,f,ensure_ascii=False,separators=(',',':'))

# v0.3.14: embed every MG candidate photo (including federal/state deputies) plus all major offices nationwide.
major={'PRESIDENTE','VICE-PRESIDENTE','GOVERNADOR','VICE-GOVERNADOR','SENADOR','1O SUPLENTE','2O SUPLENTE','1º SUPLENTE','2º SUPLENTE'}
targets={c['id']:c for c in base if c['uf']=='MG' or norm(c['office']) in major}
ids_by_uf=defaultdict(set)
for cid,c in targets.items(): ids_by_uf[c['uf']].add(cid)
os.makedirs('assets/candidate_photos',exist_ok=True); photo_map={}
for uf in sorted(ids_by_uf,key=lambda x:(x!='MG',x!='BR',x)):
 data=download(BASE+f'/eleicoes/eleicoes2026/fotos/foto_cand2026_{uf}_div.zip',optional=True)
 if not data: continue
 try:
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   for name in z.namelist():
    if name.endswith('/'): continue
    bn=os.path.basename(name); nums=re.findall(r'\d{10,}',bn)
    cid=next((n for n in nums if n in ids_by_uf[uf]),None)
    if not cid: continue
    path=f'assets/candidate_photos/{cid}.jpg'
    with open(path,'wb') as f: f.write(z.read(name))
    photo_map[cid]=path
 except zipfile.BadZipFile as ex: print('bad photo zip',uf,repr(ex))
with open('candidate_photos.js','w',encoding='utf-8') as f:
 f.write('export default {\n')
 for cid,path in sorted(photo_map.items()): f.write(f"  '{cid}': require('./{path}'),\n")
 f.write('};\n')

print('candidate rows',len(base),'unique assets',sum(len(v) for v in assets.values()),'photos',len(photo_map),'MG photos',sum(1 for cid in photo_map if by_id.get(cid,{}).get('uf')=='MG'))
kalil=by_id.get('130002539775')
if kalil:
 print('KALIL AUDIT',json.dumps({k:kalil.get(k) for k in ('id','name','status','totalizationStatus','reelection','assetCount','assetTotal','ticket')},ensure_ascii=False),'photo',kalil['id'] in photo_map)
 if kalil['assetCount']>=80 or kalil['assetTotal']>=10000000: raise SystemExit('bens do Kalil ainda duplicados')
 if kalil['id'] not in photo_map: raise SystemExit('foto oficial do Kalil não foi embutida')

mg_deputies=[c for c in base if c['uf']=='MG' and norm(c['office']) in {'DEPUTADO FEDERAL','DEPUTADO ESTADUAL'}]
mg_with_photo=sum(1 for c in mg_deputies if c['id'] in photo_map)
print('MG DEPUTY PHOTO AUDIT',mg_with_photo,'/',len(mg_deputies))
if mg_deputies and mg_with_photo < max(1,int(len(mg_deputies)*0.90)):
 raise SystemExit('cobertura de fotos de deputados MG abaixo de 90%')
