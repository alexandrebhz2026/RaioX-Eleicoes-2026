import patch_v029_final
from pathlib import Path
import json


def replace_once(path, old, new, label):
    p=Path(path)
    text=p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing v0.3.30 target: {label} in {path}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')

# AppState import: v0.3.21 moved SafeAreaView to react-native-safe-area-context,
# so patch the current react-native import without relying on the old full line.
p=Path('AppV020.js')
text=p.read_text(encoding='utf-8')
lines=text.splitlines()
changed=False
for i,line in enumerate(lines):
    if "from 'react-native';" in line and line.startswith('import {'):
        if 'AppState' not in line:
            lines[i]=line.replace('import {Animated,','import {Animated,AppState,',1)
        changed=True
        break
if not changed:
    raise SystemExit('Missing v0.3.30 target: react-native import in AppV020.js')
p.write_text('\n'.join(lines)+'\n',encoding='utf-8')

replace_once(
    'AppV020.js',
    "const TSE_POLLS='https://dadosabertos.tse.jus.br/dataset/pesquisas-eleitorais-2026';",
    "const TSE_POLLS='https://dadosabertos.tse.jus.br/dataset/pesquisas-eleitorais-2026';\nconst LIVE_POLLS_API='https://raiox-xis-ai.vercel.app/api/polls';\nconst REMOTE_POLLS_FEED='https://raw.githubusercontent.com/alexandrebhz2026/RaioX-Eleicoes-2026/v0.3.30-polls-auto-refresh/app/polls_live.json';\nconst POLLS_CACHE_KEY='raiox.polls.cache.v030';",
    'live polls constants'
)

replace_once(
    'AppV020.js',
    "function PollComparison(){const s=useStyles();const df=POLL_SNAPSHOT.find(p=>p.institute==='Datafolha'),qu=POLL_SNAPSHOT.find(p=>p.institute==='Quaest');",
    "function PollComparison({polls}){const s=useStyles();const df=(polls||[]).find(p=>p.institute==='Datafolha'),qu=(polls||[]).find(p=>p.institute==='Quaest');",
    'dynamic comparison source'
)

# Replace the complete Pesquisas screen with online-first sync, remote fallback and persistent cache.
p=Path('AppV020.js')
text=p.read_text(encoding='utf-8')
start=text.find('function PollsScreen(){')
end=text.find('\nfunction Settings({onLogout})',start)
if start<0 or end<0:
    raise SystemExit('Missing PollsScreen block')
new_screen=r'''function PollsScreen(){
  const s=useStyles();
  const [office,setOffice]=useState('PRESIDENTE'),[uf,setUf]=useState('MG'),[source,setSource]=useState('Todas');
  const [polls,setPolls]=useState(POLL_SNAPSHOT),[syncing,setSyncing]=useState(false),[updatedAt,setUpdatedAt]=useState(null),[syncNote,setSyncNote]=useState('');
  const appState=useRef(AppState.currentState),syncRef=useRef(false);

  const saveCache=async(next,at)=>{try{await SecureStore.setItemAsync(POLLS_CACHE_KEY,JSON.stringify({polls:next,updatedAt:at}))}catch{}};
  const loadCache=async()=>{try{const raw=await SecureStore.getItemAsync(POLLS_CACHE_KEY);if(!raw)return;const c=JSON.parse(raw);if(Array.isArray(c?.polls)&&c.polls.length){setPolls(c.polls);setUpdatedAt(c.updatedAt||null)}}catch{}};
  const applyPayload=async(data,label)=>{const next=Array.isArray(data?.polls)?data.polls:[];if(!next.length)return false;setPolls(next);const at=data?.fetchedAt||data?.updatedAt||new Date().toISOString();setUpdatedAt(at);await saveCache(next,at);setSyncNote(label||'Pesquisas atualizadas');return true};
  const refresh=async(nextOffice=office,nextUf=uf)=>{
    if(syncRef.current)return;
    syncRef.current=true;setSyncing(true);setSyncNote('');
    const scopeOffice=nextOffice==='GOVERNADOR'?'GOVERNADOR':'PRESIDENTE';
    const scopeUf=scopeOffice==='GOVERNADOR'?(nextUf||'MG').toUpperCase().slice(0,2):'BR';
    try{
      const url=`${LIVE_POLLS_API}?office=${encodeURIComponent(scopeOffice)}&uf=${encodeURIComponent(scopeUf)}&t=${Date.now()}`;
      const response=await fetch(url,{headers:{Accept:'application/json','Cache-Control':'no-cache'}});
      const data=await response.json().catch(()=>null);
      if(response.ok&&data?.ok&&Array.isArray(data.polls)&&data.polls.length){await applyPayload(data,data.fresh?'Atualizado agora':'Sem pesquisa nova; última carga válida mantida');return}
      throw new Error('LIVE_EMPTY');
    }catch{
      if(scopeOffice==='PRESIDENTE'){
        try{
          const response=await fetch(`${REMOTE_POLLS_FEED}?t=${Date.now()}`,{headers:{Accept:'application/json','Cache-Control':'no-cache'}});
          const data=await response.json().catch(()=>null);
          if(response.ok&&await applyPayload(data,'Feed remoto verificado; última carga válida mantida'))return;
        }catch{}
      }
      setSyncNote('Sem conexão com as fontes; última carga válida mantida');
    }finally{syncRef.current=false;setSyncing(false)}
  };

  useEffect(()=>{let mounted=true;(async()=>{await loadCache();if(mounted)await refresh('PRESIDENTE','MG')})();return()=>{mounted=false}},[]);
  useEffect(()=>{const sub=AppState.addEventListener('change',next=>{if(appState.current.match(/inactive|background/)&&next==='active')refresh(office,uf);appState.current=next});return()=>sub.remove()},[office,uf]);
  useEffect(()=>{refresh(office,uf)},[office,uf]);

  const rows=(polls||[])
    .filter(p=>office==='PRESIDENTE'?String(p.office||'PRESIDENTE')==='PRESIDENTE':String(p.office||'')==='GOVERNADOR'&&String(p.uf||'').toUpperCase()===uf.toUpperCase())
    .filter(p=>source==='Todas'||p.institute===source);
  const stamp=updatedAt?new Date(updatedAt):null;
  const stampText=stamp&&!Number.isNaN(stamp.getTime())?stamp.toLocaleString('pt-BR',{hour:'2-digit',minute:'2-digit',day:'2-digit',month:'2-digit'}):'ainda não sincronizado';

  return <ScrollView contentContainerStyle={s.content} keyboardShouldPersistTaps="handled">
    <View style={{flexDirection:'row',alignItems:'flex-start',justifyContent:'space-between',gap:10}}><View style={{flex:1}}><Text style={s.pageTitle}>Pesquisas</Text><Text style={s.pageSub}>Resultados publicados por institutos, com data, metodologia e registro para conferência no TSE.</Text></View><TouchableOpacity onPress={()=>refresh(office,uf)} disabled={syncing} style={{marginTop:3,paddingHorizontal:10,paddingVertical:8,borderRadius:12,borderWidth:1,borderColor:s._border,backgroundColor:s._surface2}}><Text style={{color:s._blue,fontSize:10,fontWeight:'900'}}>{syncing?'ATUALIZANDO…':'↻ ATUALIZAR'}</Text></TouchableOpacity></View>
    <View style={{flexDirection:'row',alignItems:'center',gap:7,marginTop:-2}}><View style={{width:8,height:8,borderRadius:4,backgroundColor:syncing?'#F0A020':'#20B779'}}/><Text style={{color:s._muted,fontSize:10}}>Última atualização: {stampText}</Text></View>{syncNote?<Text style={{color:s._muted,fontSize:9,marginTop:-6}}>{syncNote}</Text>:null}
    <View style={{flexDirection:'row',gap:8}}><TouchableOpacity style={[s.pill,office==='PRESIDENTE'&&s.pillActive]} onPress={()=>setOffice('PRESIDENTE')}><Text style={[s.pillText,office==='PRESIDENTE'&&s.pillTextActive]}>Presidente</Text></TouchableOpacity><TouchableOpacity style={[s.pill,office==='GOVERNADOR'&&s.pillActive]} onPress={()=>setOffice('GOVERNADOR')}><Text style={[s.pillText,office==='GOVERNADOR'&&s.pillTextActive]}>Governador</Text></TouchableOpacity></View>
    {office==='GOVERNADOR'?<TextInput value={uf} onChangeText={v=>setUf(v.toUpperCase().replace(/[^A-Z]/g,'').slice(0,2))} placeholder='UF' placeholderTextColor={s._muted} style={s.input}/>:null}
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8,paddingVertical:2}}>{['Todas','Datafolha','Quaest'].map(x=><TouchableOpacity key={x} style={[s.pill,source===x&&s.pillActive]} onPress={()=>setSource(x)}><Text style={[s.pillText,source===x&&s.pillTextActive]}>{x}</Text></TouchableOpacity>)}</ScrollView>
    {rows.length?<>{office==='PRESIDENTE'?<><Card style={{backgroundColor:s._surface2,padding:14}}><View style={{flexDirection:'row',alignItems:'center',gap:12}}><XisOfficial height={92}/><View style={{flex:1}}><Text style={{color:s._text,fontWeight:'900',fontSize:18}}>Resumo do Xis</Text><Text style={[s.cardSub,{marginTop:6}]}>Os gráficos abaixo usam a carga mais recente recebida das fontes. Compare sempre instituto, data e margem de erro.</Text></View></View></Card>{source==='Todas'?<PollComparison polls={rows}/>:null}</>:null}{rows.map(p=><PollCard key={p.id} poll={p}/>)}</>:<Card><Text style={s.cardTitle}>{syncing?'Buscando pesquisas…':`Nenhuma pesquisa carregada para ${office==='GOVERNADOR'?`Governador - ${uf}`:'este filtro'}`}</Text><Text style={s.cardSub}>{syncing?'Consultando as fontes agora.':'Quando uma pesquisa confiável estiver disponível, ela aparecerá automaticamente ao abrir o app ou ao tocar em Atualizar.'}</Text></Card>}
    <TouchableOpacity style={s.secondary} onPress={()=>Linking.openURL(TSE_POLLS)}><Text style={s.secondaryText}>ABRIR PESQUISAS ELEITORAIS NO TSE</Text></TouchableOpacity>
    <Text style={{color:s._muted,fontSize:9,lineHeight:14,textAlign:'center'}}>Pesquisa é um retrato do momento, não previsão do resultado. Se a atualização online falhar, o app preserva a última carga válida.</Text>
  </ScrollView>
}
'''
p.write_text(text[:start]+new_screen+text[end:],encoding='utf-8')

replace_once('AppV020.js',"const VERSION='0.3.29';","const VERSION='0.3.30';",'visible version')
replace_once('AuthGateV020.js',"const APP_VERSION='0.3.29';","const APP_VERSION='0.3.30';",'auth version')
replace_once('XisEngine.js',"'X-App-Version':'0.3.29'","'X-App-Version':'0.3.30'",'Xis API header')

app_path=Path('app.json')
app=json.loads(app_path.read_text(encoding='utf-8'))
expo=app['expo'];expo['version']='0.3.30';expo['android']['versionCode']=34
expo.setdefault('extra',{})['polls']='auto-refresh-open-and-foreground-v030';expo['extra']['release']='polls-auto-refresh-v030'
app_path.write_text(json.dumps(app,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

pkg_path=Path('package.json')
pkg=json.loads(pkg_path.read_text(encoding='utf-8'));pkg['version']='0.3.30'
pkg_path.write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

print('RAIO-X v0.3.30: polls refresh on launch/foreground with API, remote feed and persistent cache fallback')
