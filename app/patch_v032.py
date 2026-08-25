import patch_v031
from pathlib import Path
import json


def replace_once(path, old, new, label):
    p=Path(path); text=p.read_text(encoding='utf-8')
    if old not in text: raise SystemExit(f'Missing v0.3.32 target: {label} in {path}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')

p=Path('AppV020.js'); text=p.read_text(encoding='utf-8')

# Replace comparison card with a dynamic, premium version that works for President and Governor.
start=text.find('function PollComparison(')
end=text.find('\nfunction PollsScreen(){',start)
if start<0 or end<0: raise SystemExit('Missing PollComparison block')
comparison=r'''function PollComparison({polls,office='PRESIDENTE',uf='BR'}){
  const s=useStyles();
  const df=(polls||[]).find(p=>p.institute==='Datafolha'),qu=(polls||[]).find(p=>p.institute==='Quaest');
  if(!df||!qu)return null;
  const candidateRows=(df.results||[]).filter(r=>r[1]).slice(0,4);
  const names=candidateRows.map(r=>r[0]);
  const get=(poll,name)=>poll?.results?.find(r=>r[0]===name)?.[2]??0;
  const title=office==='GOVERNADOR'?`Comparativo — Governador ${uf}`:'Comparativo Nacional';
  return <View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:22,padding:16,shadowColor:'#00152F',shadowOpacity:.07,shadowRadius:16,shadowOffset:{width:0,height:6},elevation:3}}>
    <View style={{flexDirection:'row',alignItems:'center',justifyContent:'space-between',gap:10}}><View style={{flex:1}}><Text style={{color:s._text,fontSize:18,fontWeight:'900'}}>{title} — Datafolha × Quaest</Text><Text style={{color:s._muted,fontSize:9,marginTop:3}}>Comparação visual das duas fontes mais recentes</Text></View><View style={{width:38,height:38,borderRadius:13,backgroundColor:'rgba(20,120,255,.10)',alignItems:'center',justifyContent:'center'}}><Text style={{color:s._blue,fontSize:20,fontWeight:'900'}}>▥</Text></View></View>
    <View style={{flexDirection:'row',gap:12,marginTop:16}}>
      {[df,qu].map(poll=><View key={poll.institute} style={{flex:1,minWidth:0}}><View style={{flexDirection:'row',alignItems:'center',gap:8,marginBottom:11}}><View style={{width:31,height:31,borderRadius:16,backgroundColor:poll.institute==='Quaest'?'#6F2DBD':s._blue,alignItems:'center',justifyContent:'center'}}><Text style={{color:'#fff',fontWeight:'900'}}>{poll.institute==='Datafolha'?'D':'Q'}</Text></View><View style={{flex:1}}><Text style={{color:s._text,fontSize:12,fontWeight:'900'}}>{poll.institute}</Text><Text style={{color:s._muted,fontSize:8}}>{poll.published}</Text></View></View>{names.map((name,i)=>{const row=poll.results.find(r=>r[0]===name),pct=get(poll,name);return <View key={`${poll.institute}-${name}`} style={{marginTop:i?10:0}}><View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center',gap:5}}><Text style={{color:s._text,fontSize:9,fontWeight:i===0?'900':'700',flex:1}} numberOfLines={1}>{name}{row?.[1]?` (${row[1]})`:''}</Text>{i===0?<View style={{paddingHorizontal:5,paddingVertical:2,borderRadius:6,borderWidth:1,borderColor:s._blue}}><Text style={{color:s._blue,fontSize:6,fontWeight:'900'}}>LIDERA</Text></View>:null}<Text style={{color:s._blue,fontSize:12,fontWeight:'900',width:28,textAlign:'right'}}>{pct}%</Text></View><View style={{height:7,borderRadius:4,backgroundColor:'rgba(110,125,145,.13)',overflow:'hidden',marginTop:4}}><View style={{height:'100%',width:`${Math.min(100,pct*2.25)}%`,backgroundColor:s._blue,borderRadius:4,opacity:poll.institute==='Quaest'?.72:1}}/></View></View>})}</View>)}
    </View>
    <Text style={{color:s._muted,fontSize:8,lineHeight:12,marginTop:15}}>Pesquisas podem ter períodos de campo e amostras diferentes. Os percentuais não devem ser somados.</Text>
  </View>
}'''
text=text[:start]+comparison+text[end:]

# Replace PollCard so the visual and labels match the approved dashboard and work for either office.
start=text.find('function PollCard({poll})')
end=text.find('\nfunction PollComparison(',start)
if start<0 or end<0: raise SystemExit('Missing PollCard block')
pollcard=r'''function PollCard({poll}){
  const s=useStyles();const badge=poll.institute==='Datafolha'?'D':'Q';const purple=poll.institute==='Quaest';
  const officeLabel=poll.office==='GOVERNADOR'?`Governador · ${poll.uf}`:'Presidente · 1º turno';
  return <View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:22,padding:16,shadowColor:'#00152F',shadowOpacity:.06,shadowRadius:14,shadowOffset:{width:0,height:5},elevation:2}}>
    <View style={{flexDirection:'row',alignItems:'center',justifyContent:'space-between',gap:8}}><View style={{flexDirection:'row',alignItems:'center',gap:9,flex:1}}><View style={{width:36,height:36,borderRadius:18,backgroundColor:purple?'#6F2DBD':s._blue,alignItems:'center',justifyContent:'center'}}><Text style={{color:'#fff',fontSize:18,fontWeight:'900'}}>{badge}</Text></View><View style={{flex:1}}><Text style={{color:s._text,fontSize:18,fontWeight:'900'}}>{poll.institute}</Text><Text style={{color:s._muted,fontSize:9,marginTop:1}}>{officeLabel}</Text></View></View><Text style={{color:s._blue,fontSize:9,fontWeight:'900'}}>{poll.published}</Text></View>
    <View style={{marginTop:13,paddingVertical:10,borderTopWidth:1,borderBottomWidth:1,borderColor:s._border}}><Text style={{color:s._muted,fontSize:9,lineHeight:15}}>▣ Campo: {poll.field}</Text><Text style={{color:s._muted,fontSize:9,lineHeight:15}}>♟ Amostra: {Number(poll.sample||0).toLocaleString('pt-BR')}     ◉ Margem: ±{poll.margin} p.p.</Text><Text style={{color:s._muted,fontSize:9,lineHeight:15}}>▤ Registro TSE: {poll.registry}</Text></View>
    <View style={{marginTop:2}}>{(poll.results||[]).map(([n,p,v],i)=><PollBar key={`${poll.id}-${n}`} name={n} party={p} pct={v} leader={i===0}/>)}</View>
    {poll.sourceUrl?<TouchableOpacity onPress={()=>Linking.openURL(poll.sourceUrl)} style={{marginTop:14,paddingTop:11,borderTopWidth:1,borderTopColor:s._border,alignItems:'center'}}><Text style={{color:s._text,fontSize:10,fontWeight:'800'}}>Ver detalhes   ›</Text></TouchableOpacity>:null}
  </View>
}'''
text=text[:start]+pollcard+text[end:]

# Replace complete screen with the approved hierarchy while preserving v0.3.31 scoped refresh/cache logic.
start=text.find('function PollsScreen(){')
end=text.find('\nfunction Settings({onLogout})',start)
if start<0 or end<0: raise SystemExit('Missing PollsScreen block')
screen=r'''function PollsScreen(){
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
  const refresh=async(nextOffice=office,nextUf=uf)=>{const o=nextOffice==='GOVERNADOR'?'GOVERNADOR':'PRESIDENTE',u=o==='GOVERNADOR'?String(nextUf||'MG').toUpperCase().slice(0,2):'BR',k=scopeKey(o,u);if(inFlight.current.has(k))return;inFlight.current.add(k);setSyncingKey(k);setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),note:'Atualizando…'}}));try{const response=await fetch(`${LIVE_POLLS_API}?office=${encodeURIComponent(o)}&uf=${encodeURIComponent(u)}&t=${Date.now()}`,{headers:{Accept:'application/json','Cache-Control':'no-cache'}});const data=await response.json().catch(()=>null);if(response.ok&&data?.ok&&Array.isArray(data.polls)&&data.polls.length){await setScope(k,data.polls,data.fetchedAt,data.fresh?'Atualizado agora':'Sem pesquisa nova; última carga válida mantida');return}throw new Error('EMPTY')}catch{const cached=await loadScope(k);if(cached)setScopes(prev=>({...prev,[k]:{...cached,note:'Sem conexão; última carga válida mantida'}}));else setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),note:'Sem conexão com as fontes'}}))}finally{inFlight.current.delete(k);setSyncingKey(v=>v===k?'':v)}};
  useEffect(()=>{let active=true;(async()=>{for(const k of ['PRESIDENTE:BR','GOVERNADOR:MG']){const c=await loadScope(k);if(active&&c)setScopes(prev=>({...prev,[k]:c}))}if(active)refresh('PRESIDENTE','BR')})();return()=>{active=false}},[]);
  useEffect(()=>{const sub=AppState.addEventListener('change',next=>{if(appState.current.match(/inactive|background/)&&next==='active')refresh(office,uf);appState.current=next});return()=>sub.remove()},[office,uf]);
  useEffect(()=>{refresh(office,uf)},[office,uf]);
  const rows=(current.polls||[]).filter(p=>source==='Todas'||p.institute===source),stamp=current.updatedAt?new Date(current.updatedAt):null,stampText=stamp&&!Number.isNaN(stamp.getTime())?stamp.toLocaleString('pt-BR',{hour:'2-digit',minute:'2-digit',day:'2-digit',month:'2-digit'}):'carga local verificada',syncing=syncingKey===currentKey;
  const leaders=rows.filter(p=>p.results?.length).map(p=>({institute:p.institute,name:p.results[0][0],pct:p.results[0][2]}));const unique=[...new Set(leaders.map(x=>x.name))];const summary=leaders.length?(unique.length===1?`${unique[0]} aparece numericamente à frente nas ${leaders.length>1?'duas pesquisas':'pesquisa'} exibidas.`:`As pesquisas exibidas têm líderes diferentes. Compare instituto, data e margem de erro.`):'Buscando pesquisas confiáveis para este filtro.';
  return <ScrollView contentContainerStyle={[s.content,{paddingBottom:118}]} keyboardShouldPersistTaps="handled">
    <View style={{flexDirection:'row',alignItems:'flex-start',justifyContent:'space-between',gap:10}}><View style={{flex:1}}><Text style={[s.pageTitle,{fontSize:34,letterSpacing:-1}]}>Pesquisas</Text><Text style={[s.pageSub,{fontSize:13,lineHeight:19}]}>Acompanhe levantamentos eleitorais de forma clara, bonita e comparável.</Text></View><TouchableOpacity onPress={()=>refresh(office,uf)} disabled={syncing} style={{marginTop:4,paddingHorizontal:11,paddingVertical:9,borderRadius:14,borderWidth:1,borderColor:s._border,backgroundColor:s._surface}}><Text style={{color:s._blue,fontSize:9,fontWeight:'900'}}>{syncing?'ATUALIZANDO…':'↻ ATUALIZAR'}</Text></TouchableOpacity></View>
    <View style={{flexDirection:'row',alignItems:'center',gap:7,marginTop:-3}}><View style={{width:8,height:8,borderRadius:4,backgroundColor:syncing?'#F0A020':'#20B779'}}/><Text style={{color:s._muted,fontSize:9}}>Última atualização: {stampText}</Text></View>{current.note?<Text style={{color:s._muted,fontSize:8,marginTop:-7}}>{current.note}</Text>:null}
    <View style={{flexDirection:'row',alignItems:'center',justifyContent:'space-between',gap:10}}><View style={{flexDirection:'row',gap:8,flex:1}}>{[['PRESIDENTE','●','Presidente'],['GOVERNADOR','♜','Governador']].map(([k,ic,label])=><TouchableOpacity key={k} style={[{flex:1,maxWidth:145,paddingVertical:12,paddingHorizontal:13,borderRadius:22,borderWidth:1,borderColor:s._border,backgroundColor:s._surface,flexDirection:'row',justifyContent:'center',alignItems:'center',gap:7},office===k&&{backgroundColor:s._blue,borderColor:s._blue}]} onPress={()=>setOffice(k)}><Text style={{color:office===k?'#fff':s._muted,fontSize:13}}>{ic}</Text><Text style={{color:office===k?'#fff':s._text,fontSize:11,fontWeight:'900'}}>{label}</Text></TouchableOpacity>)}</View></View>
    {office==='GOVERNADOR'?<View style={{flexDirection:'row',alignItems:'center',gap:8}}><Text style={{color:s._muted,fontSize:9,fontWeight:'800'}}>UF</Text><TextInput value={uf} onChangeText={v=>setUf(v.toUpperCase().replace(/[^A-Z]/g,'').slice(0,2))} placeholder='MG' placeholderTextColor={s._muted} style={[s.input,{flex:0,width:86,height:42,paddingVertical:8,textAlign:'center',fontWeight:'900'}]}/></View>:null}
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8,paddingVertical:1}}>{['Todas','Datafolha','Quaest'].map(x=><TouchableOpacity key={x} style={[{paddingVertical:10,paddingHorizontal:18,borderRadius:20,borderWidth:1,borderColor:s._border,backgroundColor:s._surface},source===x&&{backgroundColor:s._blue,borderColor:s._blue}]} onPress={()=>setSource(x)}><Text style={{color:source===x?'#fff':s._text,fontSize:10,fontWeight:'900'}}>{x}</Text></TouchableOpacity>)}</ScrollView>
    <View style={{borderRadius:22,borderWidth:1,borderColor:'rgba(30,126,245,.28)',backgroundColor:'rgba(30,126,245,.045)',overflow:'hidden',padding:14}}><View style={{flexDirection:'row',alignItems:'center',gap:13}}><View style={{width:118,alignItems:'center',justifyContent:'center'}}><XisOfficial height={118}/></View><View style={{flex:1}}><Text style={{color:s._text,fontWeight:'900',fontSize:19}}>Resumo do Xis</Text><Text style={{color:s._muted,fontSize:11,lineHeight:17,marginTop:7}}>{summary} Compare sempre instituto, data e margem de erro.</Text></View><Text style={{color:s._blue,fontSize:32,fontWeight:'900'}}>ϟ</Text></View></View>
    {rows.length?<>{source==='Todas'&&rows.length>1?<PollComparison polls={rows} office={office} uf={uf}/>:null}<View style={{gap:12}}>{rows.map(p=><PollCard key={p.id} poll={p}/>)}</View></>:<View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:22,padding:18}}><Text style={{color:s._text,fontSize:19,fontWeight:'900'}}>{syncing?'Buscando pesquisas…':`Nenhuma pesquisa carregada para ${office==='GOVERNADOR'?`Governador - ${uf}`:'este filtro'}`}</Text><Text style={{color:s._muted,fontSize:11,lineHeight:17,marginTop:7}}>{syncing?'Consultando as fontes agora.':'Quando uma pesquisa confiável estiver disponível, ela aparecerá automaticamente.'}</Text></View>}
    <TouchableOpacity style={[s.secondary,{borderRadius:17}]} onPress={()=>Linking.openURL(TSE_POLLS)}><Text style={s.secondaryText}>ABRIR PESQUISAS ELEITORAIS NO TSE</Text></TouchableOpacity>
    <Text style={{color:s._muted,fontSize:8,lineHeight:13,textAlign:'center'}}>Pesquisa é um retrato do momento, não previsão do resultado. Cada cargo e UF mantém sua própria última carga válida.</Text>
  </ScrollView>
}'''
text=text[:start]+screen+text[end:]
p.write_text(text,encoding='utf-8')

replace_once('AppV020.js',"const VERSION='0.3.31';","const VERSION='0.3.32';",'visible version')
replace_once('AuthGateV020.js',"const APP_VERSION='0.3.31';","const APP_VERSION='0.3.32';",'auth version')
replace_once('XisEngine.js',"'X-App-Version':'0.3.31'","'X-App-Version':'0.3.32'",'Xis header')
app_path=Path('app.json');app=json.loads(app_path.read_text(encoding='utf-8'));expo=app['expo'];expo['version']='0.3.32';expo['android']['versionCode']=36;expo.setdefault('extra',{})['polls']='approved-premium-layout-v032';expo['extra']['release']='pesquisas-layout-v032';app_path.write_text(json.dumps(app,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pkg_path=Path('package.json');pkg=json.loads(pkg_path.read_text(encoding='utf-8'));pkg['version']='0.3.32';pkg_path.write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RAIO-X v0.3.32: approved premium Pesquisas layout applied over v0.3.31 sync/cache logic')
