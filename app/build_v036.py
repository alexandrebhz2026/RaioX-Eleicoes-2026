import patch_v034
from pathlib import Path
import json


def replace_between(text, start_marker, end_marker, new_block, label):
    start = text.find(start_marker)
    end = text.find(end_marker, start)
    if start < 0 or end < 0:
        raise SystemExit(f'Missing v0.3.36 block: {label}')
    return text[:start] + new_block + text[end:]


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing v0.3.36 target: {label}')
    return text.replace(old, new, 1)


p = Path('AppV020.js')
text = p.read_text(encoding='utf-8')

poll_bar = r'''function PollBar({name,party,pct,leader=false,favorite=false}){
  const s=useStyles();
  const value=Number(pct||0);
  return <View style={{marginTop:15,padding:favorite?10:0,borderRadius:15,backgroundColor:favorite?'rgba(229,162,26,.08)':'transparent',borderWidth:favorite?1:0,borderColor:'rgba(229,162,26,.30)'}}>
    <View style={{flexDirection:'row',alignItems:'flex-start',justifyContent:'space-between',gap:10}}>
      <View style={{flex:1,flexDirection:'row',alignItems:'center',gap:7,minWidth:0,flexWrap:'wrap'}}>
        <Text style={{color:s._text,fontSize:15,fontWeight:'900',lineHeight:20,flexShrink:1}} numberOfLines={2}>{name}{party?` (${party})`:''}</Text>
        {favorite?<View style={{paddingHorizontal:7,paddingVertical:3,borderRadius:8,backgroundColor:'rgba(229,162,26,.15)'}}><Text style={{color:'#B77700',fontSize:9,fontWeight:'900'}}>★ FAVORITO</Text></View>:leader?<View style={{paddingHorizontal:7,paddingVertical:3,borderRadius:8,borderWidth:1,borderColor:s._blue}}><Text style={{color:s._blue,fontSize:9,fontWeight:'900'}}>LIDERA</Text></View>:null}
      </View>
      <Text style={{color:favorite?'#B77700':s._blue,fontSize:19,fontWeight:'900',lineHeight:22}}>{value}%</Text>
    </View>
    <View style={{height:9,borderRadius:5,backgroundColor:s._surface2,overflow:'hidden',marginTop:8}}><View style={{height:'100%',width:`${Math.min(100,Math.max(value>0?2:0,value*2.15))}%`,backgroundColor:favorite?'#E5A21A':s._blue,borderRadius:5}}/></View>
  </View>
}'''
text = replace_between(text, 'function PollBar(', '\nfunction PollCard(', poll_bar, 'PollBar')

photo_helpers = r'''function pollCandidateFor(name,office,uf){
  const n=normalize(name||'');
  if(!n||['BRANCO/NULO','INDECISOS','NAO SABE','NÃO SABE','OUTROS'].some(x=>n.includes(normalize(x))))return null;
  const officeName=normalize(String(office||'').replace(/_/g,' '));
  const pool=(candidates||[]).filter(c=>normalize(c.office)===officeName).filter(c=>office==='PRESIDENTE'||!uf||normalize(c.uf)===normalize(uf));
  return pool.find(c=>normalize(c.name)===n)||pool.find(c=>normalize(c.civilName)===n)||pool.find(c=>normalize(c.name).includes(n)||n.includes(normalize(c.name)))||null;
}

function PollCandidatePhoto({name,office,uf,size=82}){
  const s=useStyles();
  const candidate=pollCandidateFor(name,office,uf);
  const src=candidate?candidatePhotos?.[candidate.id]:null;
  if(src)return <Image source={src} style={{width:size,height:Math.round(size*1.14),borderRadius:16,backgroundColor:s._surface2,borderWidth:1,borderColor:s._border}} resizeMode="cover"/>;
  const initials=String(name||'?').split(/\s+/).filter(Boolean).slice(0,2).map(x=>x[0]).join('').toUpperCase();
  return <View style={{width:size,height:Math.round(size*1.14),borderRadius:16,backgroundColor:s._surface2,borderWidth:1,borderColor:s._border,alignItems:'center',justifyContent:'center'}}><Text style={{color:s._blue,fontSize:24,fontWeight:'900'}}>{initials||'?'}</Text><Text style={{color:s._muted,fontSize:8,fontWeight:'700',marginTop:4}}>FOTO OFICIAL</Text></View>;
}

function PollTopTwo({poll}){
  const s=useStyles();
  const top=(poll.results||[]).filter(r=>r?.[1]&&Number.isFinite(Number(r?.[2]))).slice(0,2);
  if(!top.length)return null;
  return <View style={{marginTop:15}}><Text style={{color:s._muted,fontSize:11,fontWeight:'900',letterSpacing:.4,marginBottom:10}}>1º E 2º COLOCADOS</Text><View style={{flexDirection:'row',gap:10}}>{top.map(([name,party,pct],i)=><View key={`${poll.id}-top-${name}`} style={{flex:1,minWidth:0,borderRadius:18,borderWidth:1,borderColor:i===0?'rgba(30,126,245,.38)':s._border,backgroundColor:i===0?'rgba(30,126,245,.05)':s._surface2,padding:12,alignItems:'center'}}><View style={{position:'relative'}}><PollCandidatePhoto name={name} office={poll.office} uf={poll.uf} size={82}/><View style={{position:'absolute',left:-6,top:-6,minWidth:30,height:30,paddingHorizontal:6,borderRadius:15,backgroundColor:i===0?s._blue:'#667789',alignItems:'center',justifyContent:'center',borderWidth:2,borderColor:s._surface}}><Text style={{color:'#fff',fontSize:12,fontWeight:'900'}}>{i+1}º</Text></View></View><Text style={{color:s._text,fontSize:14,fontWeight:'900',lineHeight:18,textAlign:'center',marginTop:9}} numberOfLines={2}>{name}</Text><Text style={{color:s._muted,fontSize:11,fontWeight:'800',marginTop:3}}>{party}</Text><Text style={{color:s._blue,fontSize:26,fontWeight:'900',marginTop:5}}>{Number(pct||0)}%</Text></View>)}</View></View>;
}

function PollCard({poll}){
  const s=useStyles();
  const {matchesName}=useFavorites();
  const institute=String(poll.institute||'Pesquisa');
  const purple=institute==='Quaest';
  const labels={PRESIDENTE:'Presidente · 1º turno',GOVERNADOR:`Governador · ${poll.uf}`,SENADOR:`Senador · ${poll.uf}`,DEPUTADO_FEDERAL:`Deputado Federal · ${poll.uf}`,DEPUTADO_ESTADUAL:`Deputado Estadual · ${poll.uf}`,DEPUTADO_DISTRITAL:'Deputado Distrital · DF'};
  return <View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:24,padding:18,overflow:'hidden'}}>
    <View style={{flexDirection:'row',alignItems:'center',gap:12}}><View style={{width:46,height:46,borderRadius:23,backgroundColor:purple?'#6F2DBD':s._blue,alignItems:'center',justifyContent:'center'}}><Text style={{color:'#fff',fontSize:22,fontWeight:'900'}}>{institute.slice(0,1).toUpperCase()}</Text></View><View style={{flex:1,minWidth:0}}><Text style={{color:s._text,fontSize:22,fontWeight:'900'}} numberOfLines={1}>{institute}</Text><Text style={{color:s._muted,fontSize:12,fontWeight:'700',marginTop:2}}>{labels[poll.office]||'Pesquisa eleitoral'}</Text></View><Text style={{color:s._blue,fontSize:12,fontWeight:'900'}}>{poll.published||'—'}</Text></View>
    <View style={{marginTop:14,paddingVertical:13,borderTopWidth:1,borderBottomWidth:1,borderColor:s._border}}>{poll.mode?<Text style={{color:s._blue,fontSize:11,fontWeight:'900',marginBottom:5}}>{String(poll.mode).toUpperCase()}</Text>:null}{poll.question?<Text style={{color:s._text,fontSize:14,lineHeight:20,fontWeight:'700',marginBottom:8}}>{poll.question}</Text>:null}<Text style={{color:s._muted,fontSize:12,lineHeight:19}}>Campo: <Text style={{color:s._text,fontWeight:'800'}}>{poll.field||'—'}</Text></Text><Text style={{color:s._muted,fontSize:12,lineHeight:19}}>Amostra: <Text style={{color:s._text,fontWeight:'800'}}>{Number(poll.sample||0).toLocaleString('pt-BR')}</Text>   ·   Margem: <Text style={{color:s._text,fontWeight:'800'}}>±{poll.margin||0} p.p.</Text></Text><Text style={{color:s._muted,fontSize:12,lineHeight:19}}>Registro TSE: <Text style={{color:s._text,fontWeight:'800'}}>{poll.registry||'—'}</Text></Text></View>
    <PollTopTwo poll={poll}/>
    <View style={{marginTop:4}}>{(poll.results||[]).map(([n,p,v],i)=><PollBar key={`${poll.id}-${n}`} name={n} party={p} pct={v} leader={i===0} favorite={matchesName(n,poll.office,poll.uf)}/>)}</View>
    {poll.sourceUrl?<TouchableOpacity onPress={()=>Linking.openURL(poll.sourceUrl)} style={{marginTop:17,paddingTop:14,borderTopWidth:1,borderTopColor:s._border,alignItems:'center'}}><Text style={{color:s._blue,fontSize:13,fontWeight:'900'}}>VER DETALHES  ›</Text></TouchableOpacity>:null}
  </View>
}'''
text = replace_between(text, 'function PollCard({poll})', '\nfunction PollComparison(', photo_helpers, 'PollCard and candidate photo helpers')

comparison = r'''function PollComparison({polls,office='PRESIDENTE',uf='BR'}){
  const s=useStyles();
  const df=(polls||[]).find(p=>p.institute==='Datafolha'),qu=(polls||[]).find(p=>p.institute==='Quaest');
  if(!df||!qu)return null;
  const officeNames={PRESIDENTE:'Presidente',GOVERNADOR:`Governador · ${uf}`,SENADOR:`Senador · ${uf}`,DEPUTADO_FEDERAL:`Deputado Federal · ${uf}`,DEPUTADO_ESTADUAL:`Deputado Estadual · ${uf}`,DEPUTADO_DISTRITAL:'Deputado Distrital · DF'};
  return <View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:24,padding:18}}><Text style={{color:s._text,fontSize:21,fontWeight:'900'}}>Comparativo — {officeNames[office]||office}</Text><Text style={{color:s._muted,fontSize:12,marginTop:3}}>Cada coluna mostra os próprios líderes do instituto.</Text><View style={{flexDirection:'row',gap:14,marginTop:16}}>{[df,qu].map(poll=>{const rows=(poll.results||[]).filter(r=>r?.[1]).slice(0,4);return <View key={poll.institute} style={{flex:1,minWidth:0}}><View style={{flexDirection:'row',alignItems:'center',gap:8,marginBottom:8}}><View style={{width:34,height:34,borderRadius:17,backgroundColor:poll.institute==='Quaest'?'#6F2DBD':s._blue,alignItems:'center',justifyContent:'center'}}><Text style={{color:'#fff',fontSize:15,fontWeight:'900'}}>{poll.institute[0]}</Text></View><View style={{flex:1}}><Text style={{color:s._text,fontSize:13,fontWeight:'900'}}>{poll.institute}</Text><Text style={{color:s._muted,fontSize:10,marginTop:1}}>{poll.published||'—'}</Text></View></View>{rows.map(([name,party,pct])=>{const value=Number(pct||0);return <View key={`${poll.institute}-${name}`} style={{marginTop:10}}><View style={{flexDirection:'row',justifyContent:'space-between',gap:6}}><Text style={{color:s._text,fontSize:12,fontWeight:'800',lineHeight:16,flex:1}} numberOfLines={2}>{name}</Text><Text style={{color:s._blue,fontSize:14,fontWeight:'900'}}>{value}%</Text></View><View style={{height:7,borderRadius:4,backgroundColor:s._surface2,overflow:'hidden',marginTop:5}}><View style={{height:'100%',width:`${Math.min(100,Math.max(value>0?2:0,value*2.15))}%`,backgroundColor:s._blue,borderRadius:4}}/></View></View>})}</View>})}</View><Text style={{color:s._muted,fontSize:10,lineHeight:15,marginTop:15}}>Pesquisas diferentes têm datas, amostras e metodologias próprias. Compare sem somar os percentuais.</Text></View>;
}'''
text = replace_between(text, 'function PollComparison(', '\nfunction LocationConsentModal(', comparison, 'PollComparison')

location_helpers = r'''function LocationPermissionScreen({busy,onUse,onChoose,onLater}){
  const s=useStyles();
  return <ScrollView style={{flex:1,backgroundColor:s._bg}} contentContainerStyle={{flexGrow:1,justifyContent:'center',padding:24,paddingBottom:120}}><View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:28,padding:24}}><View style={{width:66,height:66,borderRadius:22,backgroundColor:'rgba(30,126,245,.10)',alignItems:'center',justifyContent:'center',alignSelf:'center'}}><Text style={{color:s._blue,fontSize:31}}>⌖</Text></View><Text style={{color:s._text,fontSize:28,fontWeight:'900',textAlign:'center',marginTop:16}}>Pesquisas do seu estado</Text><Text style={{color:s._muted,fontSize:15,lineHeight:22,textAlign:'center',marginTop:10}}>Podemos usar sua localização aproximada somente para identificar a UF e mostrar as pesquisas do seu estado.</Text><View style={{marginTop:18,padding:15,borderRadius:16,backgroundColor:s._surface2}}><Text style={{color:s._text,fontSize:12,lineHeight:18,textAlign:'center',fontWeight:'700'}}>As coordenadas não são enviadas ao servidor e não ficam salvas. Guardamos somente a UF escolhida.</Text></View><TouchableOpacity disabled={busy} onPress={onUse} style={{height:56,borderRadius:17,backgroundColor:s._blue,alignItems:'center',justifyContent:'center',marginTop:20,opacity:busy?.65:1}}><Text style={{color:'#fff',fontSize:15,fontWeight:'900'}}>{busy?'LOCALIZANDO…':'USAR MEU ESTADO'}</Text></TouchableOpacity><TouchableOpacity disabled={busy} onPress={onChoose} style={{height:54,borderRadius:17,borderWidth:1,borderColor:s._border,alignItems:'center',justifyContent:'center',marginTop:10}}><Text style={{color:s._text,fontSize:14,fontWeight:'900'}}>ESCOLHER ESTADO</Text></TouchableOpacity><TouchableOpacity disabled={busy} onPress={onLater} style={{height:48,alignItems:'center',justifyContent:'center',marginTop:4}}><Text style={{color:s._muted,fontSize:13,fontWeight:'800'}}>Agora não</Text></TouchableOpacity></View></ScrollView>;
}

function StatePickerScreen({uf,states,onSelect,onBack}){
  const s=useStyles();
  return <ScrollView style={{flex:1,backgroundColor:s._bg}} contentContainerStyle={{padding:22,paddingBottom:120}}><TouchableOpacity onPress={onBack} style={{alignSelf:'flex-start',paddingVertical:6,paddingRight:18,marginBottom:8}}><Text style={{color:s._blue,fontSize:14,fontWeight:'900'}}>‹ VOLTAR</Text></TouchableOpacity><Text style={{color:s._text,fontSize:30,fontWeight:'900'}}>Escolha o estado</Text><Text style={{color:s._muted,fontSize:14,lineHeight:20,marginTop:5,marginBottom:18}}>A UF fica salva no aparelho e você pode trocar quando quiser.</Text><View style={{flexDirection:'row',flexWrap:'wrap',gap:10}}>{states.map(([code,name])=><TouchableOpacity key={code} onPress={()=>onSelect(code)} style={{width:'48%',minHeight:76,borderRadius:18,borderWidth:1,borderColor:uf===code?s._blue:s._border,backgroundColor:uf===code?'rgba(30,126,245,.08)':s._surface,padding:13,justifyContent:'center'}}><Text style={{color:uf===code?s._blue:s._text,fontSize:18,fontWeight:'900'}}>{code}</Text><Text style={{color:s._muted,fontSize:12,lineHeight:16,marginTop:4}}>{name}</Text></TouchableOpacity>)}</View></ScrollView>;
}
'''
text = replace_between(text, 'function LocationConsentModal(', '\nfunction PollsScreen(){', location_helpers, 'location screens')

polls_screen = r'''function PollsScreen(){
  const s=useStyles();
  const STATES=[['AC','Acre'],['AL','Alagoas'],['AP','Amapá'],['AM','Amazonas'],['BA','Bahia'],['CE','Ceará'],['DF','Distrito Federal'],['ES','Espírito Santo'],['GO','Goiás'],['MA','Maranhão'],['MT','Mato Grosso'],['MS','Mato Grosso do Sul'],['MG','Minas Gerais'],['PA','Pará'],['PB','Paraíba'],['PR','Paraná'],['PE','Pernambuco'],['PI','Piauí'],['RJ','Rio de Janeiro'],['RN','Rio Grande do Norte'],['RS','Rio Grande do Sul'],['RO','Rondônia'],['RR','Roraima'],['SC','Santa Catarina'],['SP','São Paulo'],['SE','Sergipe'],['TO','Tocantins']];
  const UF_BY_NAME=Object.fromEntries(STATES.map(([code,name])=>[normalize(name),code]));
  const PREF_KEY='raiox.polls.preference.v036',OLD_PREF_KEY='raiox.polls.preference.v035',OLD_UF_KEY='raiox.polls.uf.v032',OLD_DECISION_KEY='raiox.polls.location.decision.v032';
  const [category,setCategory]=useState('PRESIDENTE'),[deputyKind,setDeputyKind]=useState('FEDERAL'),[uf,setUf]=useState('MG'),[source,setSource]=useState('Todas');
  const [locationPrompt,setLocationPrompt]=useState(false),[statePicker,setStatePicker]=useState(false),[locationBusy,setLocationBusy]=useState(false),[prefsReady,setPrefsReady]=useState(false),[locationChoice,setLocationChoice]=useState('');
  const MG_BOOTSTRAP=[{id:'df-mg-gov-2108',institute:'Datafolha',office:'GOVERNADOR',uf:'MG',published:'21/08/2026',field:'18 a 20/08/2026',sample:1204,margin:3,registry:'MG-00446/2026',sourceUrl:'https://www1.folha.uol.com.br/poder/2026/08/datafolha-cleitinho-lidera-disputa-em-mg-com-32-patrus-e-kalil-tem-12-cada.shtml',mode:'Estimulada',question:'Governador de Minas Gerais - 1º turno',results:[['Cleitinho Azevedo','Republicanos',32],['Patrus Ananias','PT',12],['Alexandre Kalil','PDT',12],['Mateus Simões','PSD',4],['Flávio Roscoe','PL',4],['Gabriel Azevedo','MDB',4],['Branco/Nulo','',14],['Indecisos','',13]]}];
  const [scopes,setScopes]=useState({'PRESIDENTE:BR':{polls:POLL_SNAPSHOT,updatedAt:null,note:''},'GOVERNADOR:MG':{polls:MG_BOOTSTRAP,updatedAt:null,note:'Última carga verificada; buscando atualização'}}),[syncingKey,setSyncingKey]=useState('');
  const inFlight=useRef(new Set()),appState=useRef(AppState.currentState);
  const office=category==='DEPUTADOS'?(deputyKind==='FEDERAL'?'DEPUTADO_FEDERAL':uf==='DF'?'DEPUTADO_DISTRITAL':'DEPUTADO_ESTADUAL'):category;
  const scopeKey=(o=office,u=uf)=>o==='PRESIDENTE'?'PRESIDENTE:BR':`${o}:${String(u||'MG').toUpperCase().slice(0,2)}`;
  const currentKey=scopeKey(),cacheKey=k=>`${POLLS_CACHE_KEY}.${k}`,current=scopes[currentKey]||{polls:[],updatedAt:null,note:''};
  const saveScope=async(k,value)=>{try{await SecureStore.setItemAsync(cacheKey(k),JSON.stringify(value))}catch{}};
  const loadScope=async k=>{try{const raw=await SecureStore.getItemAsync(cacheKey(k));if(!raw)return null;const value=JSON.parse(raw);return Array.isArray(value?.polls)&&value.polls.length?value:null}catch{return null}};
  const setScope=async(k,polls,at,note)=>{if(!Array.isArray(polls)||!polls.length)return;const value={polls,updatedAt:at||new Date().toISOString(),note:note||''};setScopes(prev=>({...prev,[k]:value}));await saveScope(k,value)};
  const refresh=async(nextOffice=office,nextUf=uf)=>{const o=nextOffice||'PRESIDENTE',u=o==='PRESIDENTE'?'BR':String(nextUf||'MG').toUpperCase().slice(0,2),k=scopeKey(o,u);if(inFlight.current.has(k))return;inFlight.current.add(k);setSyncingKey(k);setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),note:'Atualizando…'}}));try{const r=await fetch(`${LIVE_POLLS_API}?office=${encodeURIComponent(o)}&uf=${encodeURIComponent(u)}&t=${Date.now()}`,{headers:{Accept:'application/json','Cache-Control':'no-cache'}});const data=await r.json().catch(()=>null);if(r.ok&&data?.ok&&Array.isArray(data.polls)&&data.polls.length){await setScope(k,data.polls,data.fetchedAt,data.fresh?'Atualizado agora':'Última carga válida mantida')}else setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),updatedAt:data?.fetchedAt||prev[k]?.updatedAt||null,note:data?.warning||'Nenhuma pesquisa registrada e verificável encontrada.'}}))}catch{const cached=await loadScope(k);if(cached)setScopes(prev=>({...prev,[k]:{...cached,note:'Sem conexão; última carga válida mantida'}}));else setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),note:'Sem conexão com as fontes'}}))}finally{inFlight.current.delete(k);setSyncingKey(v=>v===k?'':v)}};
  const savePreference=async(nextUf,nextChoice)=>{try{await SecureStore.setItemAsync(PREF_KEY,JSON.stringify({uf:nextUf,choice:nextChoice}))}catch{}};
  const chooseUf=async code=>{if(!STATES.some(([c])=>c===code))return;setUf(code);setLocationChoice('manual');setStatePicker(false);setLocationPrompt(false);await savePreference(code,'manual')};
  const later=async()=>{setLocationChoice('skipped');setLocationPrompt(false);await savePreference(uf,'skipped')};
  const detectState=async()=>{if(locationBusy)return;setLocationBusy(true);try{const permission=await Location.requestForegroundPermissionsAsync();if(permission.status!=='granted'){setLocationChoice('denied');setLocationPrompt(false);await savePreference(uf,'denied');return}const pos=await Location.getCurrentPositionAsync({accuracy:Location.Accuracy.Low});const places=await Location.reverseGeocodeAsync({latitude:pos.coords.latitude,longitude:pos.coords.longitude});const place=places?.[0]||{},country=normalize(place.isoCountryCode||place.country||'');let region=normalize(place.region||place.subregion||'').replace(/^ESTADO DE /,'').replace(/^STATE OF /,'');const detected=UF_BY_NAME[region]||(STATES.some(([c])=>c===region)?region:'');if(!detected||!(country==='BR'||country==='BRA'||country==='BRASIL'||country==='BRAZIL')){setLocationPrompt(false);setStatePicker(true);return}setUf(detected);setLocationChoice('location');setLocationPrompt(false);setStatePicker(false);await savePreference(detected,'location')}catch{setLocationPrompt(false);setStatePicker(true)}finally{setLocationBusy(false)}};
  useEffect(()=>{let active=true;(async()=>{let pref=null;try{const raw=await SecureStore.getItemAsync(PREF_KEY);if(raw)pref=JSON.parse(raw)}catch{}if(!pref){try{const raw=await SecureStore.getItemAsync(OLD_PREF_KEY);if(raw)pref=JSON.parse(raw)}catch{}}if(!pref){try{const oldUf=await SecureStore.getItemAsync(OLD_UF_KEY),oldDecision=await SecureStore.getItemAsync(OLD_DECISION_KEY);if(oldUf&&STATES.some(([c])=>c===oldUf))pref={uf:oldUf,choice:oldDecision||'manual'}}catch{}}if(active&&pref?.uf&&STATES.some(([c])=>c===pref.uf)){setUf(pref.uf);setLocationChoice(pref.choice||'manual');await savePreference(pref.uf,pref.choice||'manual')}if(active)setPrefsReady(true)})();return()=>{active=false}},[]);
  useEffect(()=>{let active=true;(async()=>{const cached=await loadScope(currentKey);if(active&&cached)setScopes(prev=>({...prev,[currentKey]:cached}));if(active)refresh(office,uf)})();return()=>{active=false}},[office,uf]);
  useEffect(()=>{if(prefsReady&&category!=='PRESIDENTE'&&!locationChoice&&!statePicker)setLocationPrompt(true)},[prefsReady,category,locationChoice,statePicker]);
  useEffect(()=>{const sub=AppState.addEventListener('change',next=>{if(appState.current.match(/inactive|background/)&&next==='active')refresh(office,uf);appState.current=next});return()=>sub.remove()},[office,uf]);
  if(locationPrompt)return <LocationPermissionScreen busy={locationBusy} onUse={detectState} onChoose={()=>{setLocationPrompt(false);setStatePicker(true)}} onLater={later}/>;
  if(statePicker)return <StatePickerScreen uf={uf} states={STATES} onSelect={chooseUf} onBack={()=>setStatePicker(false)}/>;
  const rows=(current.polls||[]).filter(p=>source==='Todas'||p.institute===source),stamp=current.updatedAt?new Date(current.updatedAt):null,stampText=stamp&&!Number.isNaN(stamp.getTime())?stamp.toLocaleString('pt-BR',{hour:'2-digit',minute:'2-digit',day:'2-digit',month:'2-digit'}):'carga local verificada',syncing=syncingKey===currentKey;
  const officeLabel={PRESIDENTE:'Presidente',GOVERNADOR:'Governador',SENADOR:'Senador',DEPUTADO_FEDERAL:'Deputado Federal',DEPUTADO_ESTADUAL:'Deputado Estadual',DEPUTADO_DISTRITAL:'Deputado Distrital'}[office]||office;
  return <ScrollView contentContainerStyle={[s.content,{paddingBottom:125}]} keyboardShouldPersistTaps="handled"><View style={{flexDirection:'row',alignItems:'flex-start',justifyContent:'space-between',gap:12}}><View style={{flex:1}}><Text style={[s.pageTitle,{fontSize:36,letterSpacing:-1.2}]}>Pesquisas</Text><Text style={[s.pageSub,{fontSize:16,lineHeight:23}]}>Levantamentos eleitorais com fonte, data e metodologia.</Text></View><TouchableOpacity onPress={()=>refresh(office,uf)} disabled={syncing} style={{marginTop:2,width:52,height:52,borderRadius:18,borderWidth:1,borderColor:s._border,backgroundColor:s._surface,alignItems:'center',justifyContent:'center'}}><Text style={{color:s._blue,fontSize:22,fontWeight:'900'}}>↻</Text></TouchableOpacity></View><View style={{flexDirection:'row',alignItems:'center',gap:8,marginTop:6,marginBottom:4}}><View style={{width:10,height:10,borderRadius:5,backgroundColor:syncing?'#F0A020':'#20B779'}}/><Text style={{color:s._muted,fontSize:12,lineHeight:17}}>Última atualização: {stampText}{syncing?' · atualizando…':''}</Text></View>
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:9,paddingVertical:3}}>{[['PRESIDENTE','Presidente'],['GOVERNADOR','Governador'],['SENADOR','Senador'],['DEPUTADOS','Deputados']].map(([k,label])=><TouchableOpacity key={k} onPress={()=>setCategory(k)} style={{paddingVertical:13,paddingHorizontal:18,borderRadius:22,borderWidth:1,borderColor:category===k?s._blue:s._border,backgroundColor:category===k?s._blue:s._surface}}><Text style={{color:category===k?'#fff':s._text,fontSize:13,fontWeight:'900'}}>{label}</Text></TouchableOpacity>)}</ScrollView>
    {category!=='PRESIDENTE'?<View style={{flexDirection:'row',alignItems:'center',gap:10,flexWrap:'wrap'}}><TouchableOpacity onPress={()=>setStatePicker(true)} style={{height:52,paddingHorizontal:16,borderRadius:18,borderWidth:1,borderColor:s._border,backgroundColor:s._surface,flexDirection:'row',alignItems:'center',gap:8}}><Text style={{color:s._muted,fontSize:10,fontWeight:'900'}}>ESTADO</Text><Text style={{color:s._text,fontSize:17,fontWeight:'900'}}>{uf}</Text><Text style={{color:s._blue,fontSize:13}}>⌄</Text></TouchableOpacity><TouchableOpacity onPress={()=>setLocationPrompt(true)} style={{height:52,paddingHorizontal:16,borderRadius:18,borderWidth:1,borderColor:'rgba(30,126,245,.28)',backgroundColor:'rgba(30,126,245,.05)',flexDirection:'row',alignItems:'center',gap:7}}><Text style={{color:s._blue,fontSize:17}}>⌖</Text><Text style={{color:s._blue,fontSize:11,fontWeight:'900'}}>MEU ESTADO</Text></TouchableOpacity></View>:null}
    {category==='DEPUTADOS'?<View style={{flexDirection:'row',gap:9}}>{[['FEDERAL','Federal'],['ESTADUAL',uf==='DF'?'Distrital':'Estadual']].map(([k,l])=><TouchableOpacity key={k} onPress={()=>setDeputyKind(k)} style={{flex:1,paddingVertical:12,borderRadius:18,borderWidth:1,borderColor:deputyKind===k?s._blue:s._border,backgroundColor:deputyKind===k?'rgba(30,126,245,.08)':s._surface,alignItems:'center'}}><Text style={{color:deputyKind===k?s._blue:s._text,fontSize:13,fontWeight:'900'}}>{l}</Text></TouchableOpacity>)}</View>:null}
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:9,paddingVertical:2}}>{['Todas','Datafolha','Quaest'].map(x=><TouchableOpacity key={x} onPress={()=>setSource(x)} style={{paddingVertical:12,paddingHorizontal:20,borderRadius:20,borderWidth:1,borderColor:source===x?s._blue:s._border,backgroundColor:source===x?s._blue:s._surface}}><Text style={{color:source===x?'#fff':s._text,fontSize:12,fontWeight:'900'}}>{x}</Text></TouchableOpacity>)}</ScrollView>
    {rows.length?<>{source==='Todas'?<PollComparison polls={rows} office={office} uf={uf}/>:null}<View style={{gap:14}}>{rows.map(poll=><PollCard key={poll.id} poll={poll}/>)}</View></>:<View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:22,padding:20}}><Text style={{color:s._text,fontSize:21,fontWeight:'900'}}>{syncing?'Buscando pesquisas…':'Nenhuma pesquisa verificável encontrada'}</Text><Text style={{color:s._muted,fontSize:13,lineHeight:20,marginTop:7}}>{syncing?'Consultando as fontes agora.':`Não encontramos levantamento publicado e verificável para ${officeLabel}${office==='PRESIDENTE'?'':` · ${uf}`}. Quando houver, aparecerá automaticamente.`}</Text></View>}
    <TouchableOpacity style={[s.secondary,{borderRadius:17,minHeight:52}]} onPress={()=>Linking.openURL(TSE_POLLS)}><Text style={[s.secondaryText,{fontSize:12}]}>ABRIR PESQUISAS NO TSE</Text></TouchableOpacity><Text style={{color:s._muted,fontSize:10,lineHeight:15,textAlign:'center'}}>Pesquisa é um retrato do momento, não previsão do resultado.</Text></ScrollView>;
}'''
text = replace_between(text, 'function PollsScreen(){', '\nfunction ResultsScreen(){', polls_screen, 'PollsScreen')

# Bump release identity.
text = replace_once(text, "const VERSION='0.3.35';", "const VERSION='0.3.36';", 'visible version')
p.write_text(text, encoding='utf-8')

a = Path('AuthGateV020.js')
at = a.read_text(encoding='utf-8')
at = replace_once(at, "const APP_VERSION='0.3.35';", "const APP_VERSION='0.3.36';", 'AuthGate version')
a.write_text(at, encoding='utf-8')

x = Path('XisEngine.js')
xt = x.read_text(encoding='utf-8')
xt = replace_once(xt, "'X-App-Version':'0.3.35'", "'X-App-Version':'0.3.36'", 'Xis header version')
x.write_text(xt, encoding='utf-8')

app_path = Path('app.json')
app = json.loads(app_path.read_text(encoding='utf-8'))
app['expo']['version'] = '0.3.36'
app['expo']['android']['versionCode'] = 40
app['expo'].setdefault('extra', {})['release'] = 'pesquisas-readable-photos-location-screen-v036'
app_path.write_text(json.dumps(app, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

pkg_path = Path('package.json')
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '0.3.36'
pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print('RAIO-X v0.3.36: readable polls + top-two photos + dedicated location screens applied')
