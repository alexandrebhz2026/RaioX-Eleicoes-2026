import patch_v030
from pathlib import Path
import json


def replace_once(path, old, new, label):
    p=Path(path); text=p.read_text(encoding='utf-8')
    if old not in text: raise SystemExit(f'Missing v0.3.31 target: {label} in {path}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')

p=Path('AppV020.js'); text=p.read_text(encoding='utf-8')
start=text.find('function PollsScreen(){')
end=text.find('\nfunction Settings({onLogout})',start)
if start<0 or end<0: raise SystemExit('Missing PollsScreen block for v0.3.31')
new_screen=r'''function PollsScreen(){
  const s=useStyles();
  const [office,setOffice]=useState('PRESIDENTE'),[uf,setUf]=useState('MG'),[source,setSource]=useState('Todas');
  const MG_BOOTSTRAP=[
    {id:'df-mg-gov-2108',institute:'Datafolha',office:'GOVERNADOR',uf:'MG',published:'21/08/2026',field:'18 a 20/08/2026',sample:1204,margin:3,registry:'MG-00446/2026',sourceUrl:'https://www1.folha.uol.com.br/poder/2026/08/datafolha-cleitinho-lidera-disputa-em-mg-com-32-patrus-e-kalil-tem-12-cada.shtml',results:[['Cleitinho Azevedo','Republicanos',32],['Patrus Ananias','PT',12],['Alexandre Kalil','PDT',12],['Mateus Simões','PSD',4],['Flávio Roscoe','PL',4],['Gabriel Azevedo','MDB',4],['Branco/Nulo','',14],['Indecisos','',13]]},
    {id:'quaest-mg-gov-2807',institute:'Quaest',office:'GOVERNADOR',uf:'MG',published:'28/07/2026',field:'22 a 26/07/2026',sample:1482,margin:3,registry:'MG-03490/2026',sourceUrl:'https://quaest.com.br/pesquisa-genial-quaest-eleicoes-em-minas-e-pernambuco/',results:[['Cleitinho Azevedo','Republicanos',35],['Alexandre Kalil','PDT',12],['Patrus Ananias','PT',10],['Mateus Simões','PSD',6],['Gabriel Azevedo','MDB',4],['Indecisos','',15],['Branco/Nulo/Não vai votar','',13]]}
  ];
  const initialScopes={'PRESIDENTE:BR':{polls:POLL_SNAPSHOT,updatedAt:null,note:''},'GOVERNADOR:MG':{polls:MG_BOOTSTRAP,updatedAt:null,note:'Última carga verificada; buscando atualização'}};
  const [scopes,setScopes]=useState(initialScopes),[syncingKey,setSyncingKey]=useState('');
  const appState=useRef(AppState.currentState),inFlight=useRef(new Set());
  const scopeKey=(o=office,u=uf)=>o==='GOVERNADOR'?`GOVERNADOR:${String(u||'MG').toUpperCase().slice(0,2)}`:'PRESIDENTE:BR';
  const cacheKey=k=>`${POLLS_CACHE_KEY}.${k}`;
  const currentKey=scopeKey(),current=scopes[currentKey]||{polls:[],updatedAt:null,note:''};

  const saveScope=async(k,value)=>{try{await SecureStore.setItemAsync(cacheKey(k),JSON.stringify(value))}catch{}};
  const loadScope=async(k)=>{try{const raw=await SecureStore.getItemAsync(cacheKey(k));if(!raw)return null;const v=JSON.parse(raw);return Array.isArray(v?.polls)&&v.polls.length?v:null}catch{return null}};
  const setScope=async(k,polls,at,note)=>{if(!Array.isArray(polls)||!polls.length)return false;const value={polls,updatedAt:at||new Date().toISOString(),note:note||''};setScopes(prev=>({...prev,[k]:value}));await saveScope(k,value);return true};
  const refresh=async(nextOffice=office,nextUf=uf)=>{
    const o=nextOffice==='GOVERNADOR'?'GOVERNADOR':'PRESIDENTE',u=o==='GOVERNADOR'?String(nextUf||'MG').toUpperCase().slice(0,2):'BR',k=scopeKey(o,u);
    if(inFlight.current.has(k))return;
    inFlight.current.add(k);setSyncingKey(k);
    setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),note:'Atualizando…'}}));
    try{
      const response=await fetch(`${LIVE_POLLS_API}?office=${encodeURIComponent(o)}&uf=${encodeURIComponent(u)}&t=${Date.now()}`,{headers:{Accept:'application/json','Cache-Control':'no-cache'}});
      const data=await response.json().catch(()=>null);
      if(response.ok&&data?.ok&&Array.isArray(data.polls)&&data.polls.length){
        await setScope(k,data.polls,data.fetchedAt,data.fresh?'Atualizado agora':'Sem pesquisa nova; última carga válida mantida');
        return;
      }
      throw new Error('EMPTY');
    }catch{
      const cached=await loadScope(k);
      if(cached)setScopes(prev=>({...prev,[k]:{...cached,note:'Sem conexão; última carga válida mantida'}}));
      else setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),note:'Sem conexão com as fontes'}}));
    }finally{inFlight.current.delete(k);setSyncingKey(v=>v===k?'':v)}
  };

  useEffect(()=>{let active=true;(async()=>{for(const k of ['PRESIDENTE:BR','GOVERNADOR:MG']){const c=await loadScope(k);if(active&&c)setScopes(prev=>({...prev,[k]:c}))}if(active)refresh('PRESIDENTE','BR')})();return()=>{active=false}},[]);
  useEffect(()=>{const sub=AppState.addEventListener('change',next=>{if(appState.current.match(/inactive|background/)&&next==='active')refresh(office,uf);appState.current=next});return()=>sub.remove()},[office,uf]);
  useEffect(()=>{refresh(office,uf)},[office,uf]);

  const rows=(current.polls||[]).filter(p=>source==='Todas'||p.institute===source);
  const stamp=current.updatedAt?new Date(current.updatedAt):null;
  const stampText=stamp&&!Number.isNaN(stamp.getTime())?stamp.toLocaleString('pt-BR',{hour:'2-digit',minute:'2-digit',day:'2-digit',month:'2-digit'}):'carga local verificada';
  const syncing=syncingKey===currentKey;

  return <ScrollView contentContainerStyle={s.content} keyboardShouldPersistTaps="handled">
    <View style={{flexDirection:'row',alignItems:'flex-start',justifyContent:'space-between',gap:10}}><View style={{flex:1}}><Text style={s.pageTitle}>Pesquisas</Text><Text style={s.pageSub}>Resultados publicados por institutos, com data, metodologia e registro para conferência no TSE.</Text></View><TouchableOpacity onPress={()=>refresh(office,uf)} disabled={syncing} style={{marginTop:3,paddingHorizontal:10,paddingVertical:8,borderRadius:12,borderWidth:1,borderColor:s._border,backgroundColor:s._surface2}}><Text style={{color:s._blue,fontSize:10,fontWeight:'900'}}>{syncing?'ATUALIZANDO…':'↻ ATUALIZAR'}</Text></TouchableOpacity></View>
    <View style={{flexDirection:'row',alignItems:'center',gap:7,marginTop:-2}}><View style={{width:8,height:8,borderRadius:4,backgroundColor:syncing?'#F0A020':'#20B779'}}/><Text style={{color:s._muted,fontSize:10}}>Última atualização: {stampText}</Text></View>{current.note?<Text style={{color:s._muted,fontSize:9,marginTop:-6}}>{current.note}</Text>:null}
    <View style={{flexDirection:'row',gap:8}}><TouchableOpacity style={[s.pill,office==='PRESIDENTE'&&s.pillActive]} onPress={()=>setOffice('PRESIDENTE')}><Text style={[s.pillText,office==='PRESIDENTE'&&s.pillTextActive]}>Presidente</Text></TouchableOpacity><TouchableOpacity style={[s.pill,office==='GOVERNADOR'&&s.pillActive]} onPress={()=>setOffice('GOVERNADOR')}><Text style={[s.pillText,office==='GOVERNADOR'&&s.pillTextActive]}>Governador</Text></TouchableOpacity></View>
    {office==='GOVERNADOR'?<TextInput value={uf} onChangeText={v=>setUf(v.toUpperCase().replace(/[^A-Z]/g,'').slice(0,2))} placeholder='UF' placeholderTextColor={s._muted} style={s.input}/>:null}
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8,paddingVertical:2}}>{['Todas','Datafolha','Quaest'].map(x=><TouchableOpacity key={x} style={[s.pill,source===x&&s.pillActive]} onPress={()=>setSource(x)}><Text style={[s.pillText,source===x&&s.pillTextActive]}>{x}</Text></TouchableOpacity>)}</ScrollView>
    {rows.length?<>{source==='Todas'&&rows.length>1?<PollComparison polls={rows}/>:null}{rows.map(p=><PollCard key={p.id} poll={p}/>)}</>:<Card><Text style={s.cardTitle}>{syncing?'Buscando pesquisas…':`Nenhuma pesquisa carregada para ${office==='GOVERNADOR'?`Governador - ${uf}`:'este filtro'}`}</Text><Text style={s.cardSub}>{syncing?'Consultando as fontes agora.':'Quando uma pesquisa confiável estiver disponível, ela aparecerá automaticamente.'}</Text></Card>}
    <TouchableOpacity style={s.secondary} onPress={()=>Linking.openURL(TSE_POLLS)}><Text style={s.secondaryText}>ABRIR PESQUISAS ELEITORAIS NO TSE</Text></TouchableOpacity>
    <Text style={{color:s._muted,fontSize:9,lineHeight:14,textAlign:'center'}}>Pesquisa é um retrato do momento, não previsão do resultado. Cada cargo e UF mantém sua própria última carga válida.</Text>
  </ScrollView>
}
'''
p.write_text(text[:start]+new_screen+text[end:],encoding='utf-8')

replace_once('AppV020.js',"const VERSION='0.3.30';","const VERSION='0.3.31';",'visible version')
replace_once('AuthGateV020.js',"const APP_VERSION='0.3.30';","const APP_VERSION='0.3.31';",'auth version')
replace_once('XisEngine.js',"'X-App-Version':'0.3.30'","'X-App-Version':'0.3.31'",'Xis header')

app_path=Path('app.json'); app=json.loads(app_path.read_text(encoding='utf-8')); expo=app['expo'];expo['version']='0.3.31';expo['android']['versionCode']=35;expo.setdefault('extra',{})['polls']='scoped-cache-and-concurrent-refresh-v031';expo['extra']['release']='polls-mg-fix-v031';app_path.write_text(json.dumps(app,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pkg_path=Path('package.json');pkg=json.loads(pkg_path.read_text(encoding='utf-8'));pkg['version']='0.3.31';pkg_path.write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RAIO-X v0.3.31: poll cache isolated per office/UF; MG governor bootstrap included; concurrent refresh safe')
