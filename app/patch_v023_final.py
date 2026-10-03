import patch_v023
from pathlib import Path
import re


def replace_once(path, old, new, label):
    p=Path(path); text=p.read_text(encoding='utf-8')
    if old not in text: raise SystemExit(f'Missing final v0.3.23 target: {label} in {path}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')


def regex_once(path, pattern, replacement, label):
    p=Path(path); text=p.read_text(encoding='utf-8')
    new,n=re.subn(pattern,replacement,text,count=1,flags=re.S)
    if n!=1: raise SystemExit(f'Missing final v0.3.23 regex target: {label} in {path} ({n})')
    p.write_text(new,encoding='utf-8')

# Embed official TSE photos for all MG federal/state deputies, preserving major-office photos.
replace_once('build_snapshot.py',
    "targets={c['id']:c for c in base if norm(c['office']) in major}",
    "targets={c['id']:c for c in base if norm(c['office']) in major or (c['uf']=='MG' and norm(c['office']) in {'DEPUTADO FEDERAL','DEPUTADO ESTADUAL'})}",
    'MG deputy photo targets')

# Browse uses a virtualized FlatList and exposes only 15 additional candidates per scroll batch.
replace_once('AppV020.js',
    "import {Animated,Image,Linking,Modal,ScrollView,StatusBar,StyleSheet,Switch,Text,TextInput,TouchableOpacity,View} from 'react-native';",
    "import {Animated,FlatList,Image,Linking,Modal,ScrollView,StatusBar,StyleSheet,Switch,Text,TextInput,TouchableOpacity,View} from 'react-native';",
    'FlatList import')
replace_once('AppV020.js',
    "const SESSION_KEY='raiox.auth.session.v1';",
    "const SESSION_KEY='raiox.auth.session.v1';\nconst BATCH_SIZE=15;",
    '15 candidate batch constant')
replace_once('AppV020.js',
    "return src?<Image source={src} style={{width:size,height:size,borderRadius:size/2,backgroundColor:s._surface2}} resizeMode=\"cover\"/>",
    "return src?<Image source={src} style={{width:size,height:size,borderRadius:size/2,backgroundColor:s._surface2}} resizeMode=\"cover\" fadeDuration={0}/>",
    'fast local photo render')

new_browse=r'''function Browse({onSelect}){const s=useStyles();const [office,setOffice]=useState('PRESIDENTE'),[uf,setUf]=useState('MG'),[query,setQuery]=useState(''),[visibleCount,setVisibleCount]=useState(BATCH_SIZE);const president=office==='PRESIDENTE';const results=useMemo(()=>candidates.filter(c=>normalize(c.office)===office).filter(c=>president||normalize(c.uf)===normalize(uf).slice(0,2)).filter(c=>!query||normalize(c.name).includes(normalize(query))||String(c.number||'').includes(query.trim())).sort((a,b)=>String(a.name).localeCompare(String(b.name),'pt-BR')),[office,uf,query,president]);useEffect(()=>setVisibleCount(BATCH_SIZE),[office,uf,query]);const visible=results.slice(0,visibleCount);const loadMore=()=>{if(visibleCount<results.length)setVisibleCount(v=>Math.min(v+BATCH_SIZE,results.length))};const header=<View><Text style={s.pageTitle}>Busca de candidatos</Text><Text style={s.pageSub}>Escolha o cargo e, quando necessário, a UF.</Text><ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8,paddingBottom:12}}>{OFFICES.map(o=><TouchableOpacity key={o.code} style={[s.pill,office===o.code&&s.pillActive]} onPress={()=>setOffice(o.code)}><Text style={[s.pillText,office===o.code&&s.pillTextActive]}>{o.label}</Text></TouchableOpacity>)}</ScrollView>{!president&&<TextInput value={uf} onChangeText={v=>setUf(v.toUpperCase().replace(/[^A-Z]/g,'').slice(0,2))} maxLength={2} placeholder="UF" placeholderTextColor={s._muted} style={s.input}/>}<TextInput value={query} onChangeText={setQuery} placeholder="Filtrar por nome ou número" placeholderTextColor={s._muted} style={s.input}/><View style={s.listHeader}><Text style={s.listCount}>{results.length} candidato{results.length===1?'':'s'}</Text><Text style={s.sourceTag}>TSE 2026</Text></View></View>;return <FlatList data={visible} keyExtractor={item=>item.id} renderItem={({item})=><CandidateCard candidate={item} onPress={()=>onSelect(item)}/>} ListHeaderComponent={header} ListFooterComponent={visibleCount<results.length?<Text style={s.batchFooter}>Mostrando {visible.length} de {results.length} • mais 15 ao rolar</Text>:null} contentContainerStyle={s.content} keyboardShouldPersistTaps="handled" onEndReached={loadMore} onEndReachedThreshold={0.55} initialNumToRender={BATCH_SIZE} maxToRenderPerBatch={BATCH_SIZE} updateCellsBatchingPeriod={35} windowSize={5}/>;}'''
regex_once('AppV020.js',r"function Browse\(\{onSelect\}\)\{.*?\}\n\nfunction Dossier",new_browse+'\n\nfunction Dossier','15-at-a-time virtualized browse')

replace_once('AppV020.js',
    "chatSafe:{flex:1,backgroundColor:t.bg}",
    "batchFooter:{color:t.muted,fontSize:11,textAlign:'center',paddingVertical:14},chatSafe:{flex:1,backgroundColor:t.bg}",
    'batch footer style')

print('RAIO-X v0.3.23 FINAL DE TESTE: 15-card batches + MG deputy photos applied')
