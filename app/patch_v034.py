import patch_v033_favorites
from pathlib import Path
import json


def replace_between(text, start_marker, end_marker, new_block, label):
    start = text.find(start_marker)
    end = text.find(end_marker, start)
    if start < 0 or end < 0:
        raise SystemExit(f'Missing v0.3.35 block: {label}')
    return text[:start] + new_block + text[end:]


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing v0.3.35 target: {label}')
    return text.replace(old, new, 1)


p = Path('AppV020.js')
text = p.read_text(encoding='utf-8')

# Primary navigation: Apuracao is a fixed bottom tab. Comparar remains in drawer.
old_nav = "const items=[['Início','⌂'],['Busca','⌕'],['Pesquisas','▥'],['Raio-X','X'],['Comparar','⇄']];"
if old_nav in text:
    text = text.replace(old_nav, "const items=[['Início','⌂'],['Busca','⌕'],['Raio-X','X'],['Pesquisas','▥'],['Apuração','◉']];", 1)
elif "const items=[['Início','⌂'],['Busca','⌕'],['Raio-X','X'],['Pesquisas','▥'],['Apuração','◉']];" not in text:
    raise SystemExit('Missing bottom navigation source')

# Home favorites shortcut remains functional.
if "function Home({count,onRaioX,onSearch,onCompare})" in text:
    text = text.replace("function Home({count,onRaioX,onSearch,onCompare})", "function Home({count,onRaioX,onSearch,onCompare,onFavorites})", 1)
if '<Quick icon="☆" label={\'Favoritos\'} onPress={()=>{}}/>' in text:
    text = text.replace('<Quick icon="☆" label={\'Favoritos\'} onPress={()=>{}}/>', '<Quick icon="☆" label={\'Favoritos\'} onPress={onFavorites}/>', 1)
text = text.replace("<Home count={candidates.length} onRaioX={goRaioX} onSearch={()=>go('Busca')} onCompare={()=>go('Comparar')}/>", "<Home count={candidates.length} onRaioX={goRaioX} onSearch={()=>go('Busca')} onCompare={()=>go('Comparar')} onFavorites={()=>go('Favoritos')}/>")

poll_bar = r'''function PollBar({name,party,pct,leader=false,favorite=false}){
  const s=useStyles();
  const value=Number(pct||0);
  return <View style={{marginTop:12,padding:favorite?9:0,borderRadius:14,backgroundColor:favorite?'rgba(229,162,26,.08)':'transparent',borderWidth:favorite?1:0,borderColor:'rgba(229,162,26,.28)'}}>
    <View style={{flexDirection:'row',alignItems:'center',justifyContent:'space-between',gap:10}}>
      <View style={{flex:1,flexDirection:'row',alignItems:'center',gap:6,minWidth:0}}>
        <Text style={{color:s._text,fontSize:13,fontWeight:'800',flexShrink:1}} numberOfLines={1}>{name}{party?` (${party})`:''}</Text>
        {favorite?<View style={{paddingHorizontal:6,paddingVertical:2,borderRadius:8,backgroundColor:'rgba(229,162,26,.15)'}}><Text style={{color:'#B77700',fontSize:7,fontWeight:'900'}}>★ FAVORITO</Text></View>:leader?<View style={{paddingHorizontal:6,paddingVertical:2,borderRadius:8,borderWidth:1,borderColor:s._blue}}><Text style={{color:s._blue,fontSize:7,fontWeight:'900'}}>LIDERA</Text></View>:null}
      </View>
      <Text style={{color:favorite?'#B77700':s._blue,fontSize:15,fontWeight:'900'}}>{value}%</Text>
    </View>
    <View style={{height:7,borderRadius:4,backgroundColor:s._surface2,overflow:'hidden',marginTop:6}}><View style={{height:'100%',width:`${Math.min(100,Math.max(value>0?2:0,value*2.15))}%`,backgroundColor:favorite?'#E5A21A':s._blue,borderRadius:4}}/></View>
  </View>
}'''
text = replace_between(text, 'function PollBar(', '\nfunction PollCard(', poll_bar, 'PollBar')

poll_card = r'''function PollCard({poll}){
  const s=useStyles();
  const {matchesName}=useFavorites();
  const institute=String(poll.institute||'Pesquisa');
  const badge=institute.slice(0,1).toUpperCase();
  const purple=institute==='Quaest';
  const labels={PRESIDENTE:'Presidente · 1º turno',GOVERNADOR:`Governador · ${poll.uf}`,SENADOR:`Senador · ${poll.uf}`,DEPUTADO_FEDERAL:`Deputado Federal · ${poll.uf}`,DEPUTADO_ESTADUAL:`Deputado Estadual · ${poll.uf}`,DEPUTADO_DISTRITAL:'Deputado Distrital · DF'};
  return <View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:22,padding:16,overflow:'hidden'}}>
    <View style={{flexDirection:'row',alignItems:'center',gap:10}}>
      <View style={{width:40,height:40,borderRadius:20,backgroundColor:purple?'#6F2DBD':s._blue,alignItems:'center',justifyContent:'center'}}><Text style={{color:'#fff',fontSize:19,fontWeight:'900'}}>{badge}</Text></View>
      <View style={{flex:1,minWidth:0}}><Text style={{color:s._text,fontSize:18,fontWeight:'900'}} numberOfLines={1}>{institute}</Text><Text style={{color:s._muted,fontSize:9,marginTop:1}}>{labels[poll.office]||'Pesquisa eleitoral'}</Text></View>
      <Text style={{color:s._blue,fontSize:9,fontWeight:'900'}}>{poll.published||'—'}</Text>
    </View>
    <View style={{marginTop:12,paddingVertical:10,borderTopWidth:1,borderBottomWidth:1,borderColor:s._border}}>
      {poll.mode?<Text style={{color:s._blue,fontSize:8,fontWeight:'900',marginBottom:4}}>{String(poll.mode).toUpperCase()}</Text>:null}
      {poll.question?<Text style={{color:s._text,fontSize:10,lineHeight:15,marginBottom:6}}>{poll.question}</Text>:null}
      <Text style={{color:s._muted,fontSize:9,lineHeight:15}}>Campo: {poll.field||'—'}</Text>
      <Text style={{color:s._muted,fontSize:9,lineHeight:15}}>Amostra: {Number(poll.sample||0).toLocaleString('pt-BR')}   ·   Margem: ±{poll.margin||0} p.p.</Text>
      <Text style={{color:s._muted,fontSize:9,lineHeight:15}}>Registro TSE: {poll.registry||'—'}</Text>
    </View>
    <View>{(poll.results||[]).map(([n,p,v],i)=><PollBar key={`${poll.id}-${n}`} name={n} party={p} pct={v} leader={i===0} favorite={matchesName(n,poll.office,poll.uf)}/>)}</View>
    {poll.sourceUrl?<TouchableOpacity onPress={()=>Linking.openURL(poll.sourceUrl)} style={{marginTop:14,paddingTop:12,borderTopWidth:1,borderTopColor:s._border,alignItems:'center'}}><Text style={{color:s._text,fontSize:10,fontWeight:'900'}}>Ver detalhes  ›</Text></TouchableOpacity>:null}
  </View>
}'''
text = replace_between(text, 'function PollCard({poll})', '\nfunction PollComparison(', poll_card, 'PollCard')

comparison = r'''function PollComparison({polls,office='PRESIDENTE',uf='BR'}){
  const s=useStyles();
  const df=(polls||[]).find(p=>p.institute==='Datafolha'),qu=(polls||[]).find(p=>p.institute==='Quaest');
  if(!df||!qu)return null;
  const officeNames={PRESIDENTE:'Presidente',GOVERNADOR:`Governador · ${uf}`,SENADOR:`Senador · ${uf}`,DEPUTADO_FEDERAL:`Deputado Federal · ${uf}`,DEPUTADO_ESTADUAL:`Deputado Estadual · ${uf}`,DEPUTADO_DISTRITAL:'Deputado Distrital · DF'};
  const names=[...new Set([...(df.results||[]).filter(r=>r[1]).slice(0,4).map(r=>r[0]),...(qu.results||[]).filter(r=>r[1]).slice(0,4).map(r=>r[0])])].slice(0,4);
  const get=(poll,name)=>Number(poll?.results?.find(r=>r[0]===name)?.[2]||0);
  return <View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:22,padding:16}}>
    <View style={{flexDirection:'row',alignItems:'center',justifyContent:'space-between',gap:10}}><View style={{flex:1}}><Text style={{color:s._text,fontSize:17,fontWeight:'900'}}>Comparativo — {officeNames[office]||office}</Text><Text style={{color:s._muted,fontSize:9,marginTop:2}}>Datafolha × Quaest</Text></View><Text style={{color:s._blue,fontSize:20}}>▥</Text></View>
    <View style={{flexDirection:'row',gap:12,marginTop:14}}>{[df,qu].map(poll=><View key={poll.institute} style={{flex:1,minWidth:0}}><View style={{flexDirection:'row',alignItems:'center',gap:7,marginBottom:5}}><View style={{width:28,height:28,borderRadius:14,backgroundColor:poll.institute==='Quaest'?'#6F2DBD':s._blue,alignItems:'center',justifyContent:'center'}}><Text style={{color:'#fff',fontSize:12,fontWeight:'900'}}>{poll.institute[0]}</Text></View><View style={{flex:1}}><Text style={{color:s._text,fontSize:10,fontWeight:'900'}}>{poll.institute}</Text><Text style={{color:s._muted,fontSize:7}}>{poll.published||'—'}</Text></View></View>{names.map(name=>{const value=get(poll,name);return <View key={`${poll.institute}-${name}`} style={{marginTop:8}}><View style={{flexDirection:'row',justifyContent:'space-between',gap:5}}><Text style={{color:s._text,fontSize:8,fontWeight:'700',flex:1}} numberOfLines={1}>{name}</Text><Text style={{color:s._blue,fontSize:10,fontWeight:'900'}}>{value}%</Text></View><View style={{height:5,borderRadius:3,backgroundColor:s._surface2,overflow:'hidden',marginTop:3}}><View style={{height:'100%',width:`${Math.min(100,Math.max(value>0?2:0,value*2.15))}%`,backgroundColor:s._blue,borderRadius:3}}/></View></View>})}</View>)}</View>
    <Text style={{color:s._muted,fontSize:7,lineHeight:11,marginTop:12}}>Pesquisas diferentes têm datas e metodologias próprias. Compare os números sem somá-los.</Text>
  </View>
}'''
text = replace_between(text, 'function PollComparison(', '\nfunction PollsScreen(){', comparison, 'PollComparison')

polls_screen = r'''function LocationConsentModal({visible,busy,onUse,onChoose,onLater}){
  const s=useStyles();
  return <Modal visible={visible} transparent statusBarTranslucent presentationStyle="overFullScreen" animationType="fade" onRequestClose={onLater}>
    <View style={{flex:1,backgroundColor:'rgba(3,14,31,.72)',alignItems:'center',justifyContent:'center',paddingHorizontal:24,paddingVertical:34}}>
      <View style={{width:'100%',maxWidth:420,backgroundColor:s._surface,borderRadius:26,padding:20,borderWidth:1,borderColor:s._border}}>
        <View style={{width:52,height:52,borderRadius:18,backgroundColor:'rgba(30,126,245,.10)',alignItems:'center',justifyContent:'center',alignSelf:'center'}}><Text style={{color:s._blue,fontSize:25}}>⌖</Text></View>
        <Text style={{color:s._text,fontSize:22,fontWeight:'900',textAlign:'center',marginTop:12}}>Pesquisas do seu estado</Text>
        <Text style={{color:s._muted,fontSize:12,lineHeight:18,textAlign:'center',marginTop:8}}>Posso usar sua localização aproximada para selecionar automaticamente a UF?</Text>
        <View style={{marginTop:14,padding:12,borderRadius:14,backgroundColor:s._surface2}}><Text style={{color:s._text,fontSize:9,lineHeight:14,textAlign:'center'}}>Usamos a localização somente para descobrir o estado. As coordenadas não são enviadas ao servidor nem ficam salvas.</Text></View>
        <TouchableOpacity disabled={busy} onPress={onUse} style={{height:50,borderRadius:16,backgroundColor:s._blue,alignItems:'center',justifyContent:'center',marginTop:16,opacity:busy?.7:1}}><Text style={{color:'#fff',fontSize:11,fontWeight:'900'}}>{busy?'LOCALIZANDO…':'USAR MEU ESTADO'}</Text></TouchableOpacity>
        <TouchableOpacity disabled={busy} onPress={onChoose} style={{height:48,borderRadius:16,borderWidth:1,borderColor:s._border,alignItems:'center',justifyContent:'center',marginTop:9}}><Text style={{color:s._text,fontSize:10,fontWeight:'900'}}>ESCOLHER ESTADO</Text></TouchableOpacity>
        <TouchableOpacity disabled={busy} onPress={onLater} style={{alignItems:'center',justifyContent:'center',paddingVertical:13,marginTop:1}}><Text style={{color:s._muted,fontSize:10,fontWeight:'700'}}>Agora não</Text></TouchableOpacity>
      </View>
    </View>
  </Modal>
}

function StatePickerModal({visible,uf,states,onSelect,onClose}){
  const s=useStyles();
  return <Modal visible={visible} transparent statusBarTranslucent presentationStyle="overFullScreen" animationType="slide" onRequestClose={onClose}>
    <View style={{flex:1,backgroundColor:'rgba(3,14,31,.66)',justifyContent:'flex-end'}}>
      <View style={{maxHeight:'78%',backgroundColor:s._surface,borderTopLeftRadius:28,borderTopRightRadius:28,paddingTop:18,paddingHorizontal:18,paddingBottom:22,borderWidth:1,borderColor:s._border}}>
        <View style={{flexDirection:'row',alignItems:'center',justifyContent:'space-between',gap:12,marginBottom:14}}><View style={{flex:1}}><Text style={{color:s._text,fontSize:21,fontWeight:'900'}}>Escolha o estado</Text><Text style={{color:s._muted,fontSize:10,marginTop:3}}>Você pode trocar quando quiser.</Text></View><TouchableOpacity onPress={onClose} style={{width:38,height:38,borderRadius:19,backgroundColor:s._surface2,alignItems:'center',justifyContent:'center'}}><Text style={{color:s._text,fontSize:20}}>×</Text></TouchableOpacity></View>
        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{flexDirection:'row',flexWrap:'wrap',gap:8,paddingBottom:12}}>{states.map(([code,name])=><TouchableOpacity key={code} onPress={()=>onSelect(code)} style={{width:'31%',minHeight:60,borderRadius:15,borderWidth:1,borderColor:uf===code?s._blue:s._border,backgroundColor:uf===code?'rgba(30,126,245,.09)':s._surface2,padding:10,justifyContent:'center'}}><Text style={{color:uf===code?s._blue:s._text,fontSize:14,fontWeight:'900'}}>{code}</Text><Text style={{color:s._muted,fontSize:8,marginTop:3}} numberOfLines={2}>{name}</Text></TouchableOpacity>)}</ScrollView>
      </View>
    </View>
  </Modal>
}

function PollsScreen(){
  const s=useStyles();
  const STATES=[['AC','Acre'],['AL','Alagoas'],['AP','Amapá'],['AM','Amazonas'],['BA','Bahia'],['CE','Ceará'],['DF','Distrito Federal'],['ES','Espírito Santo'],['GO','Goiás'],['MA','Maranhão'],['MT','Mato Grosso'],['MS','Mato Grosso do Sul'],['MG','Minas Gerais'],['PA','Pará'],['PB','Paraíba'],['PR','Paraná'],['PE','Pernambuco'],['PI','Piauí'],['RJ','Rio de Janeiro'],['RN','Rio Grande do Norte'],['RS','Rio Grande do Sul'],['RO','Rondônia'],['RR','Roraima'],['SC','Santa Catarina'],['SP','São Paulo'],['SE','Sergipe'],['TO','Tocantins']];
  const REGION_TO_UF=Object.fromEntries(STATES.map(([code,name])=>[normalize(name),code]));
  const PREF_KEY='raiox.polls.preference.v035',OLD_UF_KEY='raiox.polls.uf.v032',OLD_DECISION_KEY='raiox.polls.location.decision.v032';
  const [category,setCategory]=useState('PRESIDENTE'),[deputyKind,setDeputyKind]=useState('FEDERAL'),[uf,setUf]=useState('MG'),[source,setSource]=useState('Todas');
  const [locationPrompt,setLocationPrompt]=useState(false),[statePicker,setStatePicker]=useState(false),[locationBusy,setLocationBusy]=useState(false),[prefsReady,setPrefsReady]=useState(false),[locationChoice,setLocationChoice]=useState('');
  const MG_BOOTSTRAP=[{id:'df-mg-gov-2108',institute:'Datafolha',office:'GOVERNADOR',uf:'MG',published:'21/08/2026',field:'18 a 20/08/2026',sample:1204,margin:3,registry:'MG-00446/2026',sourceUrl:'https://www1.folha.uol.com.br/poder/2026/08/datafolha-cleitinho-lidera-disputa-em-mg-com-32-patrus-e-kalil-tem-12-cada.shtml',mode:'Estimulada',question:'Governador de Minas Gerais - 1º turno',results:[['Cleitinho Azevedo','Republicanos',32],['Patrus Ananias','PT',12],['Alexandre Kalil','PDT',12],['Mateus Simões','PSD',4],['Flávio Roscoe','PL',4],['Gabriel Azevedo','MDB',4],['Branco/Nulo','',14],['Indecisos','',13]]}];
  const [scopes,setScopes]=useState({'PRESIDENTE:BR':{polls:POLL_SNAPSHOT,updatedAt:null,note:''},'GOVERNADOR:MG':{polls:MG_BOOTSTRAP,updatedAt:null,note:'Última carga verificada; buscando atualização'}}),[syncingKey,setSyncingKey]=useState('');
  const appState=useRef(AppState.currentState),inFlight=useRef(new Set());
  const office=category==='DEPUTADOS'?(deputyKind==='FEDERAL'?'DEPUTADO_FEDERAL':uf==='DF'?'DEPUTADO_DISTRITAL':'DEPUTADO_ESTADUAL'):category;
  const needsState=office!=='PRESIDENTE';
  const scopeKey=(o=office,u=uf)=>o==='PRESIDENTE'?'PRESIDENTE:BR':`${o}:${String(u||'MG').toUpperCase().slice(0,2)}`;
  const cacheKey=k=>`${POLLS_CACHE_KEY}.${k}`;
  const currentKey=scopeKey(),current=scopes[currentKey]||{polls:[],updatedAt:null,note:''};
  const saveScope=async(k,value)=>{try{await SecureStore.setItemAsync(cacheKey(k),JSON.stringify(value))}catch{}};
  const loadScope=async(k)=>{try{const raw=await SecureStore.getItemAsync(cacheKey(k));if(!raw)return null;const value=JSON.parse(raw);return Array.isArray(value?.polls)&&value.polls.length?value:null}catch{return null}};
  const savePreference=async(nextUf,nextChoice)=>{const value={uf:nextUf||uf,locationChoice:nextChoice??locationChoice};try{await SecureStore.setItemAsync(PREF_KEY,JSON.stringify(value))}catch{};return value};
  const setScope=async(k,polls,at,note)=>{if(!Array.isArray(polls)||!polls.length)return false;const value={polls,updatedAt:at||new Date().toISOString(),note:note||''};setScopes(prev=>({...prev,[k]:value}));await saveScope(k,value);return true};
  const refresh=async(nextOffice=office,nextUf=uf)=>{const o=nextOffice||'PRESIDENTE',u=o==='PRESIDENTE'?'BR':String(nextUf||'MG').toUpperCase().slice(0,2),k=scopeKey(o,u);if(inFlight.current.has(k))return;inFlight.current.add(k);setSyncingKey(k);setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),note:'Atualizando…'}}));try{const r=await fetch(`${LIVE_POLLS_API}?office=${encodeURIComponent(o)}&uf=${encodeURIComponent(u)}&t=${Date.now()}`,{headers:{Accept:'application/json','Cache-Control':'no-cache'}});const data=await r.json().catch(()=>null);if(r.ok&&data?.ok&&Array.isArray(data.polls)&&data.polls.length){await setScope(k,data.polls,data.fetchedAt,data.fresh?'Atualizado agora':'Última carga válida mantida');return}setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),updatedAt:data?.fetchedAt||prev[k]?.updatedAt||null,note:data?.warning||'Nenhuma pesquisa registrada e verificável encontrada.'}}))}catch{const cached=await loadScope(k);if(cached)setScopes(prev=>({...prev,[k]:{...cached,note:'Sem conexão; última carga válida mantida'}}));else setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),note:'Sem conexão com as fontes'}}))}finally{inFlight.current.delete(k);setSyncingKey(v=>v===k?'':v)}};
  const chooseState=async code=>{if(!STATES.some(([c])=>c===code))return;setUf(code);setStatePicker(false);setLocationPrompt(false);setLocationChoice('manual');await savePreference(code,'manual')};
  const dismissLocation=async()=>{setLocationPrompt(false);setLocationChoice('dismissed');await savePreference(uf,'dismissed')};
  const detectState=async()=>{if(locationBusy)return;setLocationBusy(true);try{const permission=await Location.requestForegroundPermissionsAsync();if(permission.status!=='granted'){setLocationPrompt(false);setLocationChoice('denied');await savePreference(uf,'denied');return}const pos=await Location.getCurrentPositionAsync({accuracy:Location.Accuracy.Low});const places=await Location.reverseGeocodeAsync({latitude:pos.coords.latitude,longitude:pos.coords.longitude});const place=places?.[0]||{};const country=normalize(place.isoCountryCode||place.country||'');let region=normalize(place.region||place.subregion||'').replace(/^ESTADO DE /,'').replace(/^STATE OF /,'');const detected=REGION_TO_UF[region]||(STATES.some(([c])=>c===region)?region:'');if(!detected||!['BR','BRA','BRASIL','BRAZIL'].includes(country)){setLocationPrompt(false);setStatePicker(true);setLocationChoice('manual');await savePreference(uf,'manual');return}setUf(detected);setLocationPrompt(false);setStatePicker(false);setLocationChoice('granted');await savePreference(detected,'granted')}catch{setLocationPrompt(false);setStatePicker(true)}finally{setLocationBusy(false)}};
  useEffect(()=>{let active=true;(async()=>{let savedUf='MG',savedChoice='';try{const raw=await SecureStore.getItemAsync(PREF_KEY);if(raw){const pref=JSON.parse(raw);if(STATES.some(([c])=>c===pref?.uf))savedUf=pref.uf;if(pref?.locationChoice)savedChoice=pref.locationChoice}else{const legacyUf=await SecureStore.getItemAsync(OLD_UF_KEY),legacyDecision=await SecureStore.getItemAsync(OLD_DECISION_KEY);if(legacyUf&&STATES.some(([c])=>c===legacyUf))savedUf=legacyUf;if(legacyDecision)savedChoice=legacyDecision==='granted'?'granted':legacyDecision==='manual'?'manual':legacyDecision==='denied'?'denied':'';await savePreference(savedUf,savedChoice)}}catch{}if(active){setUf(savedUf);setLocationChoice(savedChoice);setPrefsReady(true)}for(const k of ['PRESIDENTE:BR',`GOVERNADOR:${savedUf}`]){const cached=await loadScope(k);if(active&&cached)setScopes(prev=>({...prev,[k]:cached}))}if(active)refresh('PRESIDENTE','BR')})();return()=>{active=false}},[]);
  useEffect(()=>{if(prefsReady&&needsState&&!locationChoice)setLocationPrompt(true)},[prefsReady,needsState,locationChoice]);
  useEffect(()=>{refresh(office,uf)},[office,uf]);
  useEffect(()=>{const sub=AppState.addEventListener('change',next=>{if(appState.current.match(/inactive|background/)&&next==='active')refresh(office,uf);appState.current=next});return()=>sub.remove()},[office,uf]);
  const rows=(current.polls||[]).filter(p=>source==='Todas'||p.institute===source);
  const stamp=current.updatedAt?new Date(current.updatedAt):null,stampText=stamp&&!Number.isNaN(stamp.getTime())?stamp.toLocaleString('pt-BR',{hour:'2-digit',minute:'2-digit',day:'2-digit',month:'2-digit'}):'carga local verificada';
  const syncing=syncingKey===currentKey;
  const leaders=rows.filter(p=>p.results?.length).map(p=>p.results[0][0]),unique=[...new Set(leaders)];
  const summary=leaders.length?(unique.length===1?`${unique[0]} aparece numericamente à frente nos levantamentos exibidos.`:'Os levantamentos exibidos têm resultados diferentes. Compare instituto, data e margem de erro.'):'Ainda não encontrei levantamento registrado e verificável para este filtro.';
  const officeLabel={PRESIDENTE:'Presidente',GOVERNADOR:'Governador',SENADOR:'Senador',DEPUTADO_FEDERAL:'Deputado Federal',DEPUTADO_ESTADUAL:'Deputado Estadual',DEPUTADO_DISTRITAL:'Deputado Distrital'}[office]||office;
  return <>
    <ScrollView contentContainerStyle={[s.content,{paddingBottom:126}]} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>
      <View style={{flexDirection:'row',alignItems:'flex-start',justifyContent:'space-between',gap:12}}><View style={{flex:1}}><Text style={[s.pageTitle,{fontSize:34,letterSpacing:-1,marginBottom:4}]}>Pesquisas</Text><Text style={[s.pageSub,{fontSize:13,lineHeight:19}]}>Levantamentos eleitorais com fonte, data e metodologia.</Text></View><TouchableOpacity onPress={()=>refresh(office,uf)} disabled={syncing} style={{width:44,height:44,borderRadius:15,borderWidth:1,borderColor:s._border,backgroundColor:s._surface,alignItems:'center',justifyContent:'center',opacity:syncing?.65:1}}><Text style={{color:s._blue,fontSize:18,fontWeight:'900'}}>↻</Text></TouchableOpacity></View>
      <View style={{flexDirection:'row',alignItems:'center',gap:7,marginTop:4}}><View style={{width:8,height:8,borderRadius:4,backgroundColor:syncing?'#F0A020':'#20B779'}}/><Text style={{color:s._muted,fontSize:9}}>Última atualização: {stampText}{syncing?' · atualizando…':''}</Text></View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8,paddingVertical:3}}>{[['PRESIDENTE','Presidente'],['GOVERNADOR','Governador'],['SENADOR','Senador'],['DEPUTADOS','Deputados']].map(([key,label])=><TouchableOpacity key={key} onPress={()=>setCategory(key)} style={{paddingVertical:11,paddingHorizontal:16,borderRadius:20,borderWidth:1,borderColor:category===key?s._blue:s._border,backgroundColor:category===key?s._blue:s._surface}}><Text style={{color:category===key?'#fff':s._text,fontSize:10,fontWeight:'900'}}>{label}</Text></TouchableOpacity>)}</ScrollView>
      {needsState?<View style={{flexDirection:'row',alignItems:'center',gap:10,flexWrap:'wrap'}}><TouchableOpacity onPress={()=>setStatePicker(true)} style={{height:48,paddingHorizontal:16,borderRadius:16,borderWidth:1,borderColor:s._border,backgroundColor:s._surface,flexDirection:'row',alignItems:'center',gap:8}}><Text style={{color:s._muted,fontSize:8,fontWeight:'900'}}>ESTADO</Text><Text style={{color:s._text,fontSize:14,fontWeight:'900'}}>{uf}</Text><Text style={{color:s._blue,fontSize:12}}>⌄</Text></TouchableOpacity><TouchableOpacity onPress={detectState} disabled={locationBusy} style={{height:48,paddingHorizontal:16,borderRadius:16,borderWidth:1,borderColor:'rgba(30,126,245,.30)',backgroundColor:'rgba(30,126,245,.06)',flexDirection:'row',alignItems:'center',gap:7}}><Text style={{color:s._blue,fontSize:15}}>⌖</Text><Text style={{color:s._blue,fontSize:9,fontWeight:'900'}}>{locationBusy?'LOCALIZANDO…':'MEU ESTADO'}</Text></TouchableOpacity></View>:null}
      {category==='DEPUTADOS'?<View style={{flexDirection:'row',gap:8}}>{[['FEDERAL','Federal'],['ESTADUAL',uf==='DF'?'Distrital':'Estadual']].map(([key,label])=><TouchableOpacity key={key} onPress={()=>setDeputyKind(key)} style={{paddingVertical:9,paddingHorizontal:16,borderRadius:17,borderWidth:1,borderColor:deputyKind===key?s._blue:s._border,backgroundColor:deputyKind===key?'rgba(30,126,245,.08)':s._surface}}><Text style={{color:deputyKind===key?s._blue:s._text,fontSize:9,fontWeight:'900'}}>{label}</Text></TouchableOpacity>)}</View>:null}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8}}>{['Todas','Datafolha','Quaest'].map(item=><TouchableOpacity key={item} onPress={()=>setSource(item)} style={{paddingVertical:10,paddingHorizontal:18,borderRadius:18,borderWidth:1,borderColor:source===item?s._blue:s._border,backgroundColor:source===item?s._blue:s._surface}}><Text style={{color:source===item?'#fff':s._text,fontSize:9,fontWeight:'900'}}>{item}</Text></TouchableOpacity>)}</ScrollView>
      <View style={{borderRadius:22,borderWidth:1,borderColor:'rgba(30,126,245,.22)',backgroundColor:'rgba(30,126,245,.035)',padding:14}}><View style={{flexDirection:'row',alignItems:'center',gap:13}}><View style={{width:92,alignItems:'center',justifyContent:'center'}}><XisOfficial height={92}/></View><View style={{flex:1,minWidth:0}}><Text style={{color:s._text,fontWeight:'900',fontSize:19}}>Resumo do Xis</Text><Text style={{color:s._muted,fontSize:10,lineHeight:16,marginTop:5}}>{summary}</Text></View></View></View>
      {rows.length?<View style={{gap:12}}>{source==='Todas'?<PollComparison polls={rows} office={office} uf={uf}/>:null}{rows.map(poll=><PollCard key={poll.id} poll={poll}/>)}</View>:<View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:22,padding:18}}><Text style={{color:s._text,fontSize:18,fontWeight:'900'}}>{syncing?'Buscando pesquisas…':'Nenhuma pesquisa verificável encontrada'}</Text><Text style={{color:s._muted,fontSize:10,lineHeight:16,marginTop:6}}>{syncing?'Consultando as fontes agora.':`Não encontramos levantamento publicado e verificável para ${officeLabel}${office==='PRESIDENTE'?'':` · ${uf}`}. Quando houver, aparecerá automaticamente.`}</Text></View>}
      <TouchableOpacity style={[s.secondary,{borderRadius:16}]} onPress={()=>Linking.openURL(TSE_POLLS)}><Text style={s.secondaryText}>ABRIR PESQUISAS NO TSE</Text></TouchableOpacity>
      <Text style={{color:s._muted,fontSize:8,lineHeight:13,textAlign:'center'}}>Pesquisa é um retrato do momento, não previsão do resultado. Em cargos proporcionais, preservamos o tipo original do levantamento.</Text>
    </ScrollView>
    <LocationConsentModal visible={locationPrompt} busy={locationBusy} onUse={detectState} onChoose={()=>{setLocationPrompt(false);setStatePicker(true)}} onLater={dismissLocation}/>
    <StatePickerModal visible={statePicker} uf={uf} states={STATES} onSelect={chooseState} onClose={()=>setStatePicker(false)}/>
  </>
}'''
text = replace_between(text, 'function PollsScreen(){', '\nfunction ResultsScreen(){', polls_screen, 'PollsScreen')

# Keep the stable v0.3.33 apuracao implementation, only ensure the screen exists and bottom nav points to it.
if 'function ResultsScreen(){' not in text:
    raise SystemExit('Missing ResultsScreen')

# Version bump.
text = text.replace("const VERSION='0.3.34';", "const VERSION='0.3.35';", 1) if "const VERSION='0.3.34';" in text else text.replace("const VERSION='0.3.33';", "const VERSION='0.3.35';", 1)
p.write_text(text, encoding='utf-8')

# Separate versioned files.
a = Path('AuthGateV020.js')
at = a.read_text(encoding='utf-8')
at = at.replace("const APP_VERSION='0.3.34';", "const APP_VERSION='0.3.35';", 1) if "const APP_VERSION='0.3.34';" in at else at.replace("const APP_VERSION='0.3.33';", "const APP_VERSION='0.3.35';", 1)
a.write_text(at, encoding='utf-8')

x = Path('XisEngine.js')
xt = x.read_text(encoding='utf-8')
xt = xt.replace("'X-App-Version':'0.3.34'", "'X-App-Version':'0.3.35'", 1) if "'X-App-Version':'0.3.34'" in xt else xt.replace("'X-App-Version':'0.3.33'", "'X-App-Version':'0.3.35'", 1)
x.write_text(xt, encoding='utf-8')

app_path = Path('app.json')
app = json.loads(app_path.read_text(encoding='utf-8'))
app['expo']['version'] = '0.3.35'
app['expo']['android']['versionCode'] = 39
app['expo'].setdefault('extra', {})['release'] = 'pesquisas-clean-v035'
app_path.write_text(json.dumps(app, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

pkg_path = Path('package.json')
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '0.3.35'
pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print('RAIO-X v0.3.35: Pesquisas rebuilt cleanly; location consent isolated; state preference persisted; no overlapping modal UI')
