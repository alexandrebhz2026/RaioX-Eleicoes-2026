from pathlib import Path
import json
import re
import build_v036_clean

p=Path('AppV020.js')
text=p.read_text(encoding='utf-8')

# Android hardware back must navigate inside the app instead of closing it from feature screens.
m=re.search(r"import \{([^}]*)\} from 'react-native';",text)
if not m: raise SystemExit('Missing react-native import')
imports=m.group(1)
if 'BackHandler' not in imports:
    text=text[:m.start(1)]+'BackHandler,'+imports+text[m.end(1):]

# Stronger TSE candidate/photo matching. Prefer exact name + office + UF + party,
# but allow the official TSE name/civil/social name to resolve poll spelling variations.
start=text.find('function pollCandidateFor(')
end=text.find('\nfunction PollCard({poll})',start)
if start<0 or end<0: raise SystemExit('Missing poll candidate/photo block')
photo_block=r'''function pollCandidateFor(name,party,office,uf){
  const n=normalize(name||''),p=normalize(party||''),o=normalize(String(office||'').replace(/_/g,' ')),u=normalize(uf||'');
  if(!n||['BRANCO/NULO','INDECISOS','NAO SABE','NÃO SABE','OUTROS','NAO VAI VOTAR'].some(x=>n.includes(normalize(x))))return null;
  const tokens=n.split(/\s+/).filter(x=>x.length>2);
  const score=c=>{
    const names=[c?.name,c?.civilName,c?.socialName].map(normalize).filter(Boolean),co=normalize(c?.office),cu=normalize(c?.uf),cp=normalize(c?.party);
    let s=0;
    if(names.some(x=>x===n))s+=120;
    else if(names.some(x=>x.includes(n)||n.includes(x)))s+=75;
    else {const best=Math.max(0,...names.map(x=>tokens.filter(t=>x.includes(t)).length));if(best<Math.max(1,Math.min(2,tokens.length)))return -1;s+=best*18}
    if(o&&co===o)s+=35;else if(o&&co!==o)s-=25;
    if(o==='PRESIDENTE'||!u||u==='BR'||cu===u)s+=16;else s-=10;
    if(p&&cp===p)s+=14;
    if(candidatePhotos?.[c?.id])s+=8;
    return s;
  };
  let best=null,bestScore=-1;
  for(const c of candidates||[]){const s=score(c);if(s>bestScore){bestScore=s;best=c}}
  return bestScore>=55?best:null;
}

function PollCandidatePhoto({name,party,office,uf,size=96}){
  const s=useStyles();
  const candidate=pollCandidateFor(name,party,office,uf);
  const src=candidate?candidatePhotos?.[candidate.id]:null;
  if(src)return <Image source={src} style={{width:size,height:Math.round(size*1.12),borderRadius:18,backgroundColor:s._surface2,borderWidth:1,borderColor:s._border}} resizeMode="cover"/>;
  return <View style={{width:size,height:Math.round(size*1.12),borderRadius:18,backgroundColor:s._surface2,borderWidth:1,borderColor:s._border,alignItems:'center',justifyContent:'center',padding:8}}><Text style={{color:s._muted,fontSize:11,fontWeight:'900',textAlign:'center'}}>FOTO OFICIAL\nINDISPONÍVEL</Text></View>;
}

function PollTopTwo({poll}){
  const s=useStyles();
  const top=(poll.results||[]).filter(r=>r?.[1]&&Number.isFinite(Number(r?.[2]))).slice(0,2);
  if(!top.length)return null;
  return <View style={{marginTop:18}}><Text style={{color:s._muted,fontSize:12,fontWeight:'900',letterSpacing:.4,marginBottom:11}}>1º E 2º COLOCADOS</Text><View style={{flexDirection:'row',gap:10}}>{top.map(([name,party,pct],i)=><View key={`${poll.id}-top-${name}`} style={{flex:1,minWidth:0,borderRadius:20,borderWidth:1,borderColor:i===0?'rgba(30,126,245,.42)':s._border,backgroundColor:i===0?'rgba(30,126,245,.05)':s._surface2,padding:13,alignItems:'center'}}><View style={{position:'relative'}}><PollCandidatePhoto name={name} party={party} office={poll.office} uf={poll.uf} size={96}/><View style={{position:'absolute',left:-7,top:-7,minWidth:32,height:32,paddingHorizontal:7,borderRadius:16,backgroundColor:i===0?s._blue:'#667789',alignItems:'center',justifyContent:'center',borderWidth:2,borderColor:s._surface}}><Text style={{color:'#fff',fontSize:13,fontWeight:'900'}}>{i+1}º</Text></View></View><Text style={{color:s._text,fontSize:15,fontWeight:'900',lineHeight:19,textAlign:'center',marginTop:10}} numberOfLines={2}>{name}</Text><Text style={{color:s._muted,fontSize:12,fontWeight:'800',marginTop:3}}>{party}</Text><Text style={{color:s._blue,fontSize:29,fontWeight:'900',marginTop:5}}>{Number(pct||0)}%</Text></View>)}</View></View>;
}
'''
text=text[:start]+photo_block+text[end:]

# Every response rendered in the current scope receives its office/UF explicitly.
old="  const rows=(current.polls||[]).filter(p=>source==='Todas'||p.institute===source),stamp=current.updatedAt?new Date(current.updatedAt):null,stampText=stamp&&!Number.isNaN(stamp.getTime())?stamp.toLocaleString('pt-BR',{hour:'2-digit',minute:'2-digit',day:'2-digit',month:'2-digit'}):'carga local verificada',syncing=syncingKey===currentKey;"
new="  const normalizedPolls=(current.polls||[]).map(p=>({...p,office:p.office||office,uf:p.uf||(office==='PRESIDENTE'?'BR':uf)})),sourceOptions=['Todas',...new Set(normalizedPolls.map(p=>p.institute).filter(Boolean))],effectiveSource=source==='Todas'||sourceOptions.includes(source)?source:'Todas';\n  const rows=normalizedPolls.filter(p=>effectiveSource==='Todas'||p.institute===effectiveSource),stamp=current.updatedAt?new Date(current.updatedAt):null,stampText=stamp&&!Number.isNaN(stamp.getTime())?stamp.toLocaleString('pt-BR',{hour:'2-digit',minute:'2-digit',day:'2-digit',month:'2-digit'}):'carga local verificada',syncing=syncingKey===currentKey;"
if old not in text: raise SystemExit('Missing rows/source line')
text=text.replace(old,new,1)

old="{['Todas','Datafolha','Quaest'].map(x=><TouchableOpacity key={x} onPress={()=>setSource(x)} style={{paddingVertical:12,paddingHorizontal:20,borderRadius:20,borderWidth:1,borderColor:source===x?s._blue:s._border,backgroundColor:source===x?s._blue:s._surface}}><Text style={{color:source===x?'#fff':s._text,fontSize:12,fontWeight:'900'}}>{x}</Text></TouchableOpacity>)}"
new="{sourceOptions.map(x=><TouchableOpacity key={x} onPress={()=>setSource(x)} style={{paddingVertical:12,paddingHorizontal:20,borderRadius:20,borderWidth:1,borderColor:effectiveSource===x?s._blue:s._border,backgroundColor:effectiveSource===x?s._blue:s._surface}}><Text style={{color:effectiveSource===x?'#fff':s._text,fontSize:12,fontWeight:'900'}}>{x}</Text></TouchableOpacity>)}"
if old not in text: raise SystemExit('Missing fixed source filter')
text=text.replace(old,new,1)

# Reset institute filter whenever the user changes the main office.
text=text.replace("onPress={()=>setCategory(k)} style=", "onPress={()=>{setCategory(k);setSource('Todas')}} style=",1)

# Local verified Senate bootstrap for MG so the screen is never falsely empty while online refresh runs.
state_marker="  const [scopes,setScopes]=useState({'PRESIDENTE:BR':{polls:POLL_SNAPSHOT,updatedAt:null,note:''},'GOVERNADOR:MG':{polls:MG_BOOTSTRAP,updatedAt:null,note:'Última carga verificada; buscando atualização'}}),[syncingKey,setSyncingKey]=useState('');"
if state_marker not in text: raise SystemExit('Missing scope bootstrap marker')
senate="""  const MG_SENATE_BOOTSTRAP=[{id:'df-mg-sen-2108',institute:'Datafolha',office:'SENADOR',uf:'MG',published:'21/08/2026',field:'18 a 20/08/2026',sample:1204,margin:3,registry:'MG-00446/2026',sourceUrl:'https://www1.folha.uol.com.br/poder/2026/08/datafolha-marilia-campos-tem-11-na-disputa-ao-senado-em-mg-viana-marca-8-e-domingos-savio-6.shtml',question:'Senador por Minas Gerais - intenção de voto',mode:'Estimulada',results:[['Marília Campos','PT',11],['Carlos Viana','PSD',8],['Domingos Sávio','PL',6],['Marcelo Aro','PP',5],['Ana Luiza do MLB','UP',4],['Marco Antônio Superman','Novo',3],['Áurea Carolina','PSOL',2],['Manoel Carvalho','MDB',2],['Gustavo Galassi','PSDB',2],['Tião Pessoa','PCO',2],['Marcelo Heringer','PDT',2],['Victória Mello Vic','PSTU',2],['Indecisos','',24],['Branco/Nulo','',21]]},{id:'quaest-mg-sen-2807',institute:'Quaest',office:'SENADOR',uf:'MG',published:'28/07/2026',field:'22 a 26/07/2026',sample:1482,margin:3,registry:'MG-03490/2026',sourceUrl:'https://noticias.uol.com.br/eleicoes/2026/07/28/genialquaest-mg-senado.ghtm',question:'Senador por Minas Gerais - cenário 1',mode:'Estimulada',results:[['Marília Campos','PT',18],['Aécio Neves','PSDB',16],['Carlos Viana','PSD',11],['Marcelo Aro','PP',10],['Domingos Sávio','PL',9],['Eros Biondini','PL',8],['Áurea Carolina','PSOL',3],['Indecisos','',10],['Branco/Nulo/Não vai votar','',12]]}];\n"""
replacement=senate+"  const [scopes,setScopes]=useState({'PRESIDENTE:BR':{polls:POLL_SNAPSHOT,updatedAt:null,note:''},'GOVERNADOR:MG':{polls:MG_BOOTSTRAP,updatedAt:null,note:'Última carga verificada; buscando atualização'},'SENADOR:MG':{polls:MG_SENATE_BOOTSTRAP,updatedAt:null,note:'Última carga verificada; buscando atualização'}}),[syncingKey,setSyncingKey]=useState('');"
text=text.replace(state_marker,replacement,1)

# Local Android back handling inside the state/location flow.
anchor="  useEffect(()=>{const sub=AppState.addEventListener('change',next=>{if(appState.current.match(/inactive|background/)&&next==='active')refresh(office,uf);appState.current=next});return()=>sub.remove()},[office,uf]);"
if anchor not in text: raise SystemExit('Missing PollsScreen app-state effect')
text=text.replace(anchor,anchor+"\n  useEffect(()=>{const sub=BackHandler.addEventListener('hardwareBackPress',()=>{if(statePicker){setStatePicker(false);return true}if(locationPrompt){setLocationPrompt(false);return true}return false});return()=>sub.remove()},[statePicker,locationPrompt]);",1)

# Root navigation history for Android hardware back.
go_old="  const go=next=>{setTab(next);if(next!=='Raio-X')setSelected(null)};\n  const goRaioX=q=>{setRaioQuery(q||'');setSelected(null);setTab('Raio-X')};\n  const select=c=>{setSelected(c);setTab('Raio-X')};"
if go_old not in text: raise SystemExit('Missing root navigation functions')
go_new="""  const navHistory=useRef([]);
  const remember=next=>{if(next!==tab){navHistory.current=[...navHistory.current,tab].slice(-20)}};
  const go=next=>{remember(next);setTab(next);if(next!=='Raio-X')setSelected(null)};
  const goRaioX=q=>{remember('Raio-X');setRaioQuery(q||'');setSelected(null);setTab('Raio-X')};
  const select=c=>{remember('Raio-X');setSelected(c);setTab('Raio-X')};
  useEffect(()=>{const sub=BackHandler.addEventListener('hardwareBackPress',()=>{if(drawer){setDrawer(false);return true}if(selected){setSelected(null);setRaioQuery('');return true}const prev=navHistory.current.pop();if(prev){setTab(prev);setSelected(null);return true}if(tab!=='Início'){setTab('Início');setSelected(null);return true}return false});return()=>sub.remove()},[tab,selected,drawer]);"""
text=text.replace(go_old,go_new,1)

# Release identity.
text=text.replace("const VERSION='0.3.36';","const VERSION='0.3.37';",1)
p.write_text(text,encoding='utf-8')

for path,old,new in [('AuthGateV020.js',"const APP_VERSION='0.3.36';","const APP_VERSION='0.3.37';"),('XisEngine.js',"'X-App-Version':'0.3.36'","'X-App-Version':'0.3.37'")]:
    q=Path(path);t=q.read_text(encoding='utf-8')
    if old not in t: raise SystemExit(f'Missing version marker in {path}')
    q.write_text(t.replace(old,new,1),encoding='utf-8')

app_path=Path('app.json');app=json.loads(app_path.read_text(encoding='utf-8'));app['expo']['version']='0.3.37';app['expo']['android']['versionCode']=41;app['expo'].setdefault('extra',{})['release']='polls-more-sources-senate-photos-android-back-v037';app_path.write_text(json.dumps(app,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pkg_path=Path('package.json');pkg=json.loads(pkg_path.read_text(encoding='utf-8'));pkg['version']='0.3.37';pkg_path.write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Build-time audit: the TSE snapshot must contain actual official photos for the two presidential leaders shown in the default poll.
snap=Path('build_snapshot.py');st=snap.read_text(encoding='utf-8')
st += r'''
# v0.3.37 presidential photo audit
for wanted in ('LULA','FLAVIO BOLSONARO'):
 matches=[c for c in base if norm(c.get('office'))=='PRESIDENTE' and (norm(c.get('name'))==wanted or wanted in norm(c.get('name')) or wanted in norm(c.get('civilName')))]
 print('PRESIDENT PHOTO AUDIT',wanted,[(c.get('id'),c.get('name'),c.get('id') in photo_map) for c in matches[:5]])
 if not matches or not any(c.get('id') in photo_map for c in matches): raise SystemExit('foto oficial presidencial ausente: '+wanted)
'''
snap.write_text(st,encoding='utf-8')

print('RAIO-X v0.3.37: broader sources + MG Senate + official photo matching + Android back applied')
