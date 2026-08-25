import patch_v032
from pathlib import Path
import json


def replace_once(path, old, new, label):
    p=Path(path); text=p.read_text(encoding='utf-8')
    if old not in text: raise SystemExit(f'Missing v0.3.32 location target: {label} in {path}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')

# Expo Location is only used after the user explicitly accepts the Xis prompt in Governador.
replace_once(
    'AppV020.js',
    "import * as SecureStore from 'expo-secure-store';",
    "import * as SecureStore from 'expo-secure-store';\nimport * as Location from 'expo-location';",
    'expo-location import'
)

replace_once(
    'AppV020.js',
    "  const [office,setOffice]=useState('PRESIDENTE'),[uf,setUf]=useState('MG'),[source,setSource]=useState('Todas');",
    """  const [office,setOffice]=useState('PRESIDENTE'),[uf,setUf]=useState('MG'),[source,setSource]=useState('Todas');
  const [locationPrompt,setLocationPrompt]=useState(false),[statePicker,setStatePicker]=useState(false),[locationBusy,setLocationBusy]=useState(false),[prefsReady,setPrefsReady]=useState(false),[locationDecision,setLocationDecision]=useState('');
  const UFS=[['AC','Acre'],['AL','Alagoas'],['AP','Amapá'],['AM','Amazonas'],['BA','Bahia'],['CE','Ceará'],['DF','Distrito Federal'],['ES','Espírito Santo'],['GO','Goiás'],['MA','Maranhão'],['MT','Mato Grosso'],['MS','Mato Grosso do Sul'],['MG','Minas Gerais'],['PA','Pará'],['PB','Paraíba'],['PR','Paraná'],['PE','Pernambuco'],['PI','Piauí'],['RJ','Rio de Janeiro'],['RN','Rio Grande do Norte'],['RS','Rio Grande do Sul'],['RO','Rondônia'],['RR','Roraima'],['SC','Santa Catarina'],['SP','São Paulo'],['SE','Sergipe'],['TO','Tocantins']];
  const UF_BY_NAME=Object.fromEntries(UFS.map(([code,name])=>[normalize(name),code]));
  const LOCATION_UF_KEY='raiox.polls.uf.v032',LOCATION_DECISION_KEY='raiox.polls.location.decision.v032';""",
    'location states and UF map'
)

# Insert privacy-first state detection helpers immediately before effects.
p=Path('AppV020.js'); text=p.read_text(encoding='utf-8')
anchor="  useEffect(()=>{let active=true;(async()=>{for(const k of ['PRESIDENTE:BR','GOVERNADOR:MG'])"
if anchor not in text: raise SystemExit('Missing v0.3.32 location effect anchor')
helpers=r'''  const markLocationDecision=async value=>{setLocationDecision(value);try{await SecureStore.setItemAsync(LOCATION_DECISION_KEY,value)}catch{}};
  const selectUf=async code=>{if(!UFS.some(([c])=>c===code))return;setUf(code);setStatePicker(false);setLocationPrompt(false);await markLocationDecision('manual');try{await SecureStore.setItemAsync(LOCATION_UF_KEY,code)}catch{};refresh('GOVERNADOR',code)};
  const detectState=async()=>{
    if(locationBusy)return;setLocationBusy(true);
    try{
      const permission=await Location.requestForegroundPermissionsAsync();
      if(permission.status!=='granted'){
        await markLocationDecision('denied');setLocationPrompt(false);
        setScopes(prev=>({...prev,[scopeKey('GOVERNADOR',uf)]:{...(prev[scopeKey('GOVERNADOR',uf)]||{polls:[],updatedAt:null}),note:'Localização não autorizada. Escolha o estado manualmente.'}}));
        return;
      }
      const pos=await Location.getCurrentPositionAsync({accuracy:Location.Accuracy.Low});
      const places=await Location.reverseGeocodeAsync({latitude:pos.coords.latitude,longitude:pos.coords.longitude});
      const place=places?.[0]||{};
      const country=normalize(place.isoCountryCode||place.country||'');
      let region=normalize(place.region||place.subregion||'').replace(/^ESTADO DE /,'').replace(/^STATE OF /,'');
      const detected=UF_BY_NAME[region]||(UFS.some(([c])=>c===region)?region:'');
      if(!detected||!(country==='BR'||country==='BRA'||country==='BRASIL'||country==='BRAZIL')){
        await markLocationDecision('granted');setLocationPrompt(false);setStatePicker(true);
        setScopes(prev=>({...prev,[scopeKey('GOVERNADOR',uf)]:{...(prev[scopeKey('GOVERNADOR',uf)]||{polls:[],updatedAt:null}),note:'Não consegui identificar uma UF brasileira. Escolha o estado.'}}));
        return;
      }
      setUf(detected);setLocationPrompt(false);setStatePicker(false);await markLocationDecision('granted');
      try{await SecureStore.setItemAsync(LOCATION_UF_KEY,detected)}catch{}
      await refresh('GOVERNADOR',detected);
    }catch{
      setLocationPrompt(false);setStatePicker(true);
      setScopes(prev=>({...prev,[scopeKey('GOVERNADOR',uf)]:{...(prev[scopeKey('GOVERNADOR',uf)]||{polls:[],updatedAt:null}),note:'Não foi possível detectar o estado agora. Escolha a UF manualmente.'}}));
    }finally{setLocationBusy(false)}
  };
'''
text=text.replace(anchor,helpers+anchor,1)
p.write_text(text,encoding='utf-8')

# Load only the previously saved UF/decision. Coordinates are never persisted.
replace_once(
    'AppV020.js',
    "  useEffect(()=>{let active=true;(async()=>{for(const k of ['PRESIDENTE:BR','GOVERNADOR:MG']){const c=await loadScope(k);if(active&&c)setScopes(prev=>({...prev,[k]:c}))}if(active)refresh('PRESIDENTE','BR')})();return()=>{active=false}},[]);",
    """  useEffect(()=>{let active=true;(async()=>{try{const savedUf=await SecureStore.getItemAsync(LOCATION_UF_KEY),decision=await SecureStore.getItemAsync(LOCATION_DECISION_KEY);if(active&&savedUf&&UFS.some(([c])=>c===savedUf))setUf(savedUf);if(active)setLocationDecision(decision||'')}catch{}finally{if(active)setPrefsReady(true)}for(const k of ['PRESIDENTE:BR','GOVERNADOR:MG']){const c=await loadScope(k);if(active&&c)setScopes(prev=>({...prev,[k]:c}))}if(active)refresh('PRESIDENTE','BR')})();return()=>{active=false}},[]);
  useEffect(()=>{if(prefsReady&&office==='GOVERNADOR'&&!locationDecision)setLocationPrompt(true)},[prefsReady,office,locationDecision]);""",
    'load saved UF and prompt once'
)

# Replace free-form UF typing by a state selector plus explicit approximate-location shortcut.
replace_once(
    'AppV020.js',
    "    {office==='GOVERNADOR'?<View style={{flexDirection:'row',alignItems:'center',gap:8}}><Text style={{color:s._muted,fontSize:9,fontWeight:'800'}}>UF</Text><TextInput value={uf} onChangeText={v=>setUf(v.toUpperCase().replace(/[^A-Z]/g,'').slice(0,2))} placeholder='MG' placeholderTextColor={s._muted} style={[s.input,{flex:0,width:86,height:42,paddingVertical:8,textAlign:'center',fontWeight:'900'}]}/></View>:null}",
    """    {office==='GOVERNADOR'?<View style={{flexDirection:'row',alignItems:'center',gap:8,flexWrap:'wrap'}}><TouchableOpacity onPress={()=>setStatePicker(true)} style={{height:42,paddingHorizontal:14,borderRadius:15,borderWidth:1,borderColor:s._border,backgroundColor:s._surface,flexDirection:'row',alignItems:'center',gap:7}}><Text style={{color:s._muted,fontSize:9,fontWeight:'800'}}>ESTADO</Text><Text style={{color:s._text,fontSize:13,fontWeight:'900'}}>{uf}</Text><Text style={{color:s._blue,fontSize:12}}>⌄</Text></TouchableOpacity><TouchableOpacity onPress={detectState} disabled={locationBusy} style={{height:42,paddingHorizontal:13,borderRadius:15,borderWidth:1,borderColor:'rgba(30,126,245,.28)',backgroundColor:'rgba(30,126,245,.06)',flexDirection:'row',alignItems:'center',gap:6}}><Text style={{color:s._blue,fontSize:14}}>⌖</Text><Text style={{color:s._blue,fontSize:9,fontWeight:'900'}}>{locationBusy?'LOCALIZANDO…':'MEU ESTADO'}</Text></TouchableOpacity></View>:null}""",
    'state selector UI'
)

# Add Xis consent and manual state picker modals to the approved Pesquisas screen.
replace_once(
    'AppV020.js',
    "    <Text style={{color:s._muted,fontSize:8,lineHeight:13,textAlign:'center'}}>Pesquisa é um retrato do momento, não previsão do resultado. Cada cargo e UF mantém sua própria última carga válida.</Text>\n  </ScrollView>",
    """    <Text style={{color:s._muted,fontSize:8,lineHeight:13,textAlign:'center'}}>Pesquisa é um retrato do momento, não previsão do resultado. Cada cargo e UF mantém sua própria última carga válida.</Text>
    <Modal visible={locationPrompt} transparent animationType="fade" onRequestClose={()=>setLocationPrompt(false)}><View style={{flex:1,backgroundColor:'rgba(1,12,29,.72)',justifyContent:'center',padding:20}}><View style={{backgroundColor:s._surface,borderRadius:26,padding:20,borderWidth:1,borderColor:s._border,alignItems:'center'}}><XisOfficial height={126}/><Text style={{color:s._text,fontSize:22,fontWeight:'900',textAlign:'center',marginTop:4}}>Pesquisas do seu estado</Text><Text style={{color:s._muted,fontSize:12,lineHeight:18,textAlign:'center',marginTop:9}}>Posso usar sua localização aproximada para selecionar automaticamente o estado nas pesquisas para governador?</Text><View style={{marginTop:14,padding:12,borderRadius:14,backgroundColor:'rgba(30,126,245,.06)',borderWidth:1,borderColor:'rgba(30,126,245,.18)',width:'100%'}}><Text style={{color:s._text,fontSize:10,fontWeight:'800',textAlign:'center'}}>Privacidade: usamos a localização somente para descobrir a UF. As coordenadas não são enviadas ao nosso servidor nem ficam salvas.</Text></View><TouchableOpacity disabled={locationBusy} onPress={detectState} style={{width:'100%',marginTop:16,paddingVertical:14,borderRadius:16,backgroundColor:s._blue,alignItems:'center'}}><Text style={{color:'#fff',fontSize:11,fontWeight:'900'}}>{locationBusy?'LOCALIZANDO…':'USAR MEU ESTADO'}</Text></TouchableOpacity><TouchableOpacity onPress={()=>{setLocationPrompt(false);setStatePicker(true)}} style={{width:'100%',marginTop:9,paddingVertical:13,borderRadius:16,borderWidth:1,borderColor:s._border,alignItems:'center'}}><Text style={{color:s._text,fontSize:10,fontWeight:'900'}}>ESCOLHER ESTADO</Text></TouchableOpacity><TouchableOpacity onPress={async()=>{setLocationPrompt(false);await markLocationDecision('denied')}} style={{paddingVertical:12,paddingHorizontal:18}}><Text style={{color:s._muted,fontSize:10,fontWeight:'700'}}>Agora não</Text></TouchableOpacity></View></View></Modal>
    <Modal visible={statePicker} transparent animationType="slide" onRequestClose={()=>setStatePicker(false)}><View style={{flex:1,backgroundColor:'rgba(1,12,29,.66)',justifyContent:'flex-end'}}><View style={{maxHeight:'78%',backgroundColor:s._surface,borderTopLeftRadius:28,borderTopRightRadius:28,padding:18,borderWidth:1,borderColor:s._border}}><View style={{flexDirection:'row',alignItems:'center',justifyContent:'space-between',marginBottom:12}}><View><Text style={{color:s._text,fontSize:20,fontWeight:'900'}}>Escolha o estado</Text><Text style={{color:s._muted,fontSize:10,marginTop:3}}>Você pode trocar quando quiser.</Text></View><TouchableOpacity onPress={()=>setStatePicker(false)} style={{width:36,height:36,borderRadius:18,backgroundColor:s._surface2,alignItems:'center',justifyContent:'center'}}><Text style={{color:s._text,fontSize:18}}>×</Text></TouchableOpacity></View><ScrollView contentContainerStyle={{flexDirection:'row',flexWrap:'wrap',gap:8,paddingBottom:24}}>{UFS.map(([code,name])=><TouchableOpacity key={code} onPress={()=>selectUf(code)} style={{width:'31%',minHeight:58,borderRadius:14,borderWidth:1,borderColor:uf===code?s._blue:s._border,backgroundColor:uf===code?'rgba(30,126,245,.09)':s._surface2,padding:9,justifyContent:'center'}}><Text style={{color:uf===code?s._blue:s._text,fontSize:13,fontWeight:'900'}}>{code}</Text><Text style={{color:s._muted,fontSize:8,marginTop:2}} numberOfLines={2}>{name}</Text></TouchableOpacity>)}</ScrollView></View></View></Modal>
  </ScrollView>""",
    'location consent and state picker modals'
)

# Native dependency and permission copy.
app_path=Path('app.json');app=json.loads(app_path.read_text(encoding='utf-8'));expo=app['expo'];plugins=expo.setdefault('plugins',[])
if not any((isinstance(x,str) and x=='expo-location') or (isinstance(x,list) and x and x[0]=='expo-location') for x in plugins):
    plugins.append(['expo-location',{'locationWhenInUsePermission':'Permita ao RAIO-X usar sua localização aproximada para selecionar automaticamente seu estado nas pesquisas. As coordenadas não são armazenadas.'}])
expo.setdefault('extra',{})['pollsLocation']='approximate-state-only-no-coordinate-storage-v032'
app_path.write_text(json.dumps(app,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

pkg_path=Path('package.json');pkg=json.loads(pkg_path.read_text(encoding='utf-8'));pkg.setdefault('dependencies',{})['expo-location']='~56.0.23';pkg_path.write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

print('RAIO-X v0.3.32: approved layout + approximate location state detection + manual UF selector applied')
