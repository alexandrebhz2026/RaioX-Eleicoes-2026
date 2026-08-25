import patch_v033
from pathlib import Path

p=Path('AppV020.js')
text=p.read_text(encoding='utf-8')

# Shared persistent favorites store. Only candidate identifiers/snapshots stay on this device.
anchor='function useStyles(){'
if anchor not in text: raise SystemExit('Missing useStyles anchor')
favorites_code=r'''const FAVORITES_KEY='raiox.favorites.v1';
let favoriteMemory=null;
const favoriteListeners=new Set();
function favoriteId(c){return String(c?.id||`${c?.office||''}|${c?.uf||''}|${c?.number||''}|${c?.name||''}`)}
function notifyFavorites(){for(const fn of favoriteListeners)try{fn([...(favoriteMemory||[])])}catch{}}
async function ensureFavorites(){if(Array.isArray(favoriteMemory))return favoriteMemory;try{const raw=await SecureStore.getItemAsync(FAVORITES_KEY);const parsed=raw?JSON.parse(raw):[];favoriteMemory=Array.isArray(parsed)?parsed:[]}catch{favoriteMemory=[]}notifyFavorites();return favoriteMemory}
function useFavorites(){
  const [favorites,setFavorites]=useState(Array.isArray(favoriteMemory)?favoriteMemory:[]);
  useEffect(()=>{const fn=v=>setFavorites(v);favoriteListeners.add(fn);ensureFavorites();return()=>favoriteListeners.delete(fn)},[]);
  const isFavorite=c=>favorites.some(f=>favoriteId(f)===favoriteId(c));
  const matchesName=(name,office,uf)=>{const n=normalize(name);if(!n)return false;const o=normalize(String(office||'').replace(/_/g,' ')),u=normalize(uf||'');return favorites.some(f=>{const fn=normalize(f.name||f.civilName||'');if(!fn)return false;const fo=normalize(String(f.office||'').replace(/_/g,' ')),fu=normalize(f.uf||'');const nameMatch=fn===n||(fn.length>5&&n.length>5&&(fn.includes(n)||n.includes(fn)));const officeMatch=!o||!fo||fo===o;const ufMatch=o==='PRESIDENTE'||!u||!fu||fu===u;return nameMatch&&officeMatch&&ufMatch})};
  const toggle=async c=>{await ensureFavorites();const id=favoriteId(c),exists=(favoriteMemory||[]).some(f=>favoriteId(f)===id);if(exists)favoriteMemory=favoriteMemory.filter(f=>favoriteId(f)!==id);else favoriteMemory=[...(favoriteMemory||[]),{id:c?.id||id,name:c?.name||'',civilName:c?.civilName||'',number:c?.number||'',office:c?.office||'',uf:c?.uf||'',party:c?.party||''}];try{await SecureStore.setItemAsync(FAVORITES_KEY,JSON.stringify(favoriteMemory))}catch{}notifyFavorites()};
  return {favorites,isFavorite,matchesName,toggle};
}

'''
text=text.replace(anchor,favorites_code+anchor,1)

# Candidate cards get a real interactive star.
start=text.find('function CandidateCard(')
end=text.find('\n\nfunction DirectSearch',start)
if start<0 or end<0: raise SystemExit('Missing CandidateCard block')
candidate_card=r'''function CandidateCard({candidate,onPress}){const s=useStyles();const {isFavorite,toggle}=useFavorites(),fav=isFavorite(candidate);return <TouchableOpacity activeOpacity={.84} onPress={onPress}><Card style={s.candidateCard}><CandidatePhoto candidate={candidate}/><View style={{flex:1,minWidth:0}}><Text style={s.candidateName} numberOfLines={1}>{candidate.name}</Text><Text style={s.candidateMeta} numberOfLines={1}>{candidate.number||'—'} • {candidate.office}</Text><Text style={s.candidateMeta} numberOfLines={1}>{candidate.party||'Partido não informado'} • {candidate.uf||'BR'}</Text><View style={s.statusChip}><Text style={s.statusChipText}>{clean(candidate.status,'Registro TSE')}</Text></View></View><TouchableOpacity onPress={e=>{e?.stopPropagation?.();toggle(candidate)}} style={{width:40,height:40,borderRadius:20,alignItems:'center',justifyContent:'center',backgroundColor:fav?'rgba(255,180,0,.14)':s._surface2}}><Text style={{fontSize:22,color:fav?'#F0A000':s._muted}}>{fav?'★':'☆'}</Text></TouchableOpacity><Text style={s.chevron}>›</Text></Card></TouchableOpacity>}'''
text=text[:start]+candidate_card+text[end:]

# Dossier gets a favorite control in the profile header.
start=text.find('function Dossier(')
end=text.find('\nfunction Metric(',start)
if start<0 or end<0: raise SystemExit('Missing Dossier block')
block=text[start:end]
block=block.replace("function Dossier({candidate,onBack}){const s=useStyles();const age=ageAtElection(candidate);", "function Dossier({candidate,onBack}){const s=useStyles();const {isFavorite,toggle}=useFavorites(),fav=isFavorite(candidate);const age=ageAtElection(candidate);")
needle="<View style={s.profileStatus}><Text style={s.profileStatusText}>{clean(candidate.status,'Registro TSE')}</Text></View></View></Card>"
repl="<View style={s.profileStatus}><Text style={s.profileStatusText}>{clean(candidate.status,'Registro TSE')}</Text></View></View><TouchableOpacity onPress={()=>toggle(candidate)} style={{width:48,height:48,borderRadius:24,alignItems:'center',justifyContent:'center',backgroundColor:fav?'rgba(255,180,0,.14)':s._surface2}}><Text style={{fontSize:27,color:fav?'#F0A000':s._muted}}>{fav?'★':'☆'}</Text></TouchableOpacity></Card>"
if needle not in block: raise SystemExit('Missing Dossier favorite insertion point')
block=block.replace(needle,repl,1)
text=text[:start]+block+text[end:]

# Poll bars visibly identify favorite candidates.
start=text.find('function PollBar(')
end=text.find('\nfunction PollCard(',start)
if start<0 or end<0: raise SystemExit('Missing PollBar block')
pollbar=r'''function PollBar({name,party,pct,leader=false,favorite=false}){const s=useStyles();return <View style={{marginTop:10,padding:favorite?8:0,borderRadius:12,backgroundColor:favorite?'rgba(240,160,0,.08)':'transparent',borderWidth:favorite?1:0,borderColor:'rgba(240,160,0,.28)'}}><View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center',gap:6}}><View style={{flex:1,flexDirection:'row',alignItems:'center',gap:5}}><Text style={{color:s._text,fontWeight:'800',fontSize:11,flexShrink:1}} numberOfLines={1}>{name}{party?` (${party})`:''}</Text>{favorite?<View style={{paddingHorizontal:5,paddingVertical:2,borderRadius:7,backgroundColor:'rgba(240,160,0,.14)'}}><Text style={{color:'#D88E00',fontSize:6,fontWeight:'900'}}>★ FAVORITO</Text></View>:leader?<View style={{paddingHorizontal:5,paddingVertical:2,borderRadius:6,borderWidth:1,borderColor:s._blue}}><Text style={{color:s._blue,fontSize:6,fontWeight:'900'}}>LIDERA</Text></View>:null}</View><Text style={{color:favorite?'#D88E00':s._blue,fontWeight:'900',fontSize:13}}>{pct}%</Text></View><View style={{height:7,borderRadius:4,backgroundColor:s._surface2,overflow:'hidden',marginTop:4}}><View style={{height:'100%',width:`${Math.min(100,pct*2.25)}%`,backgroundColor:favorite?'#E7A21A':s._blue,borderRadius:4}}/></View></View>}'''
text=text[:start]+pollbar+text[end:]

start=text.find('function PollCard({poll})')
end=text.find('\nfunction PollComparison(',start)
if start<0 or end<0: raise SystemExit('Missing PollCard block')
pollcard=text[start:end]
pollcard=pollcard.replace("const s=useStyles();const badge=", "const s=useStyles();const {matchesName}=useFavorites();const badge=",1)
pollcard=pollcard.replace("<PollBar key={`${poll.id}-${n}`} name={n} party={p} pct={v} leader={i===0}/>", "<PollBar key={`${poll.id}-${n}`} name={n} party={p} pct={v} leader={i===0} favorite={matchesName(n,poll.office,poll.uf)}/>")
text=text[:start]+pollcard+text[end:]

# Favorites menu screen.
insert_at=text.find('\nfunction Compare()')
if insert_at<0: raise SystemExit('Missing Compare insertion point')
fav_screen=r'''
function FavoritesScreen({onSelect}){const s=useStyles();const {favorites}=useFavorites();const resolved=favorites.map(f=>candidates.find(c=>String(c.id)===String(f.id))||f);return <ScrollView contentContainerStyle={[s.content,{paddingBottom:118}]}><Text style={[s.pageTitle,{fontSize:34}]}>Favoritos</Text><Text style={s.pageSub}>Acompanhe os candidatos que você marcou. Eles ficam destacados automaticamente nas pesquisas e na apuração.</Text>{resolved.length?<><View style={s.listHeader}><Text style={s.listCount}>{resolved.length} favorito{resolved.length===1?'':'s'}</Text><Text style={s.sourceTag}>★ ACOMPANHANDO</Text></View>{resolved.map(c=><CandidateCard key={favoriteId(c)} candidate={c} onPress={()=>onSelect?.(c)}/>)}</>:<View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:22,padding:20,alignItems:'center'}}><Text style={{fontSize:34,color:'#F0A000'}}>☆</Text><Text style={{color:s._text,fontSize:18,fontWeight:'900',marginTop:8}}>Nenhum favorito ainda</Text><Text style={{color:s._muted,fontSize:11,lineHeight:17,textAlign:'center',marginTop:6}}>Abra qualquer candidato e toque na estrela. Quando ele aparecer em pesquisas ou na apuração, o RAIO-X destacará automaticamente.</Text></View>}</ScrollView>}
'''
text=text[:insert_at]+fav_screen+text[insert_at:]

# Apuracao gets automatic favorite highlighting while retaining the 20-second live-only refresh.
start=text.find('function ResultsScreen(){')
end=text.find('\nfunction Settings({onLogout})',start)
if start<0 or end<0: raise SystemExit('Missing ResultsScreen block')
results=r'''function ResultsScreen(){
  const s=useStyles();const {matchesName}=useFavorites();const [office,setOffice]=useState('PRESIDENTE'),[uf,setUf]=useState('MG'),[data,setData]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState('');const timer=useRef(null),app=useRef(AppState.currentState);
  const load=async()=>{if(busy)return;setBusy(true);try{const r=await fetch(`${LIVE_RESULTS_API}?office=${encodeURIComponent(office)}&uf=${encodeURIComponent(office==='PRESIDENTE'?'BR':uf)}&t=${Date.now()}`,{headers:{Accept:'application/json','Cache-Control':'no-cache'}});const j=await r.json().catch(()=>null);if(r.ok&&j?.ok){setData(j);setError('')}else throw new Error('SOURCE')}catch{setError('Não consegui consultar a fonte oficial agora.')}finally{setBusy(false)}};
  useEffect(()=>{load()},[office,uf]);
  useEffect(()=>{if(timer.current)clearInterval(timer.current);timer.current=null;if(data?.active)timer.current=setInterval(load,20000);return()=>{if(timer.current)clearInterval(timer.current)}},[data?.active,office,uf]);
  useEffect(()=>{const sub=AppState.addEventListener('change',next=>{if(app.current.match(/inactive|background/)&&next==='active')load();app.current=next});return()=>sub.remove()},[office,uf]);
  const candidatesRows=data?.candidates||[],pct=Number(data?.totals?.percentSections||0),live=Boolean(data?.active),scopeUf=office==='PRESIDENTE'?'BR':uf;
  return <ScrollView contentContainerStyle={[s.content,{paddingBottom:118}]}><View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'flex-start',gap:10}}><View style={{flex:1}}><Text style={[s.pageTitle,{fontSize:34}]}>Apuração</Text><Text style={s.pageSub}>Resultados oficiais do TSE. Quando a totalização começar, esta tela entra automaticamente em modo ao vivo.</Text></View><View style={{paddingHorizontal:10,paddingVertical:7,borderRadius:13,backgroundColor:live?'rgba(27,185,110,.12)':'rgba(240,160,32,.12)',borderWidth:1,borderColor:live?'#1BB96E':'#F0A020'}}><Text style={{color:live?'#1BB96E':'#F0A020',fontSize:9,fontWeight:'900'}}>{live?'● AO VIVO':'○ AGUARDANDO'}</Text></View></View>
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8}}>{[['PRESIDENTE','Presidente'],['GOVERNADOR','Governador'],['SENADOR','Senador'],['DEPUTADO_FEDERAL','Dep. Federal'],[uf==='DF'?'DEPUTADO_DISTRITAL':'DEPUTADO_ESTADUAL',uf==='DF'?'Dep. Distrital':'Dep. Estadual']].map(([k,l])=><TouchableOpacity key={k} onPress={()=>setOffice(k)} style={{paddingVertical:10,paddingHorizontal:14,borderRadius:19,borderWidth:1,borderColor:office===k?s._blue:s._border,backgroundColor:office===k?s._blue:s._surface}}><Text style={{color:office===k?'#fff':s._text,fontSize:9,fontWeight:'900'}}>{l}</Text></TouchableOpacity>)}</ScrollView>
    {office!=='PRESIDENTE'?<TextInput value={uf} onChangeText={v=>setUf(v.toUpperCase().replace(/[^A-Z]/g,'').slice(0,2))} maxLength={2} placeholder="UF" placeholderTextColor={s._muted} style={[s.input,{width:90,textAlign:'center',fontWeight:'900'}]}/>:null}
    <View style={{backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:22,padding:18}}><View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center'}}><View><Text style={{color:s._muted,fontSize:9,fontWeight:'900'}}>TOTALIZAÇÃO DAS SEÇÕES</Text><Text style={{color:s._text,fontSize:32,fontWeight:'900',marginTop:3}}>{live?`${pct.toFixed(2).replace('.',',')}%`:'—'}</Text></View><TouchableOpacity onPress={load} disabled={busy} style={{paddingHorizontal:12,paddingVertical:9,borderRadius:14,borderWidth:1,borderColor:s._border}}><Text style={{color:s._blue,fontSize:9,fontWeight:'900'}}>{busy?'ATUALIZANDO…':'↻ ATUALIZAR'}</Text></TouchableOpacity></View><View style={{height:10,borderRadius:6,backgroundColor:s._surface2,overflow:'hidden',marginTop:12}}><View style={{height:'100%',width:`${Math.max(0,Math.min(100,pct))}%`,backgroundColor:s._blue,borderRadius:6}}/></View><Text style={{color:s._muted,fontSize:9,lineHeight:14,marginTop:10}}>{data?.message||error||'Consultando se a apuração de 2026 já começou.'}</Text>{data?.tseUpdatedAt?<Text style={{color:s._muted,fontSize:8,marginTop:5}}>Última atualização do TSE: {data.tseUpdatedAt}</Text>:null}</View>
    {live&&candidatesRows.length?<View style={{gap:10}}>{candidatesRows.slice(0,40).map((c,i)=>{const fav=matchesName(c.name,office,scopeUf);return <View key={`${c.number}-${c.name}`} style={{backgroundColor:fav?'rgba(240,160,0,.07)':s._surface,borderWidth:1,borderColor:fav?'rgba(240,160,0,.45)':s._border,borderRadius:18,padding:14}}><View style={{flexDirection:'row',alignItems:'center',gap:10}}><Text style={{color:fav?'#D88E00':s._muted,fontSize:12,fontWeight:'900',width:24}}>{fav?'★':`${i+1}º`}</Text><View style={{flex:1}}><View style={{flexDirection:'row',alignItems:'center',gap:6}}><Text style={{color:s._text,fontSize:14,fontWeight:'900',flexShrink:1}} numberOfLines={1}>{c.name}</Text>{fav?<Text style={{color:'#D88E00',fontSize:7,fontWeight:'900'}}>FAVORITO</Text>:null}</View><Text style={{color:s._muted,fontSize:9,marginTop:2}}>{c.number}{c.party?` · ${c.party}`:''}</Text></View><View style={{alignItems:'flex-end'}}><Text style={{color:fav?'#D88E00':s._blue,fontSize:18,fontWeight:'900'}}>{Number(c.percent||0).toFixed(2).replace('.',',')}%</Text><Text style={{color:s._muted,fontSize:8}}>{Number(c.votes||0).toLocaleString('pt-BR')} votos</Text></View></View></View>})}</View>:<View style={{borderRadius:22,borderWidth:1,borderColor:'rgba(30,126,245,.22)',backgroundColor:'rgba(30,126,245,.04)',padding:18,alignItems:'center'}}><XisOfficial height={120}/><Text style={{color:s._text,fontSize:18,fontWeight:'900',marginTop:6}}>Tudo pronto para o dia da eleição</Text><Text style={{color:s._muted,fontSize:11,lineHeight:17,textAlign:'center',marginTop:7}}>Antes da apuração, não exibimos números fictícios. Assim que o TSE publicar votos totalizados, o modo AO VIVO será ativado e esta tela passará a atualizar a cada 20 segundos enquanto estiver aberta. Seus favoritos serão destacados automaticamente.</Text></View>}
    <Text style={{color:s._muted,fontSize:8,lineHeight:13,textAlign:'center'}}>Fonte exclusiva da apuração: Tribunal Superior Eleitoral (TSE). O RAIO-X apenas organiza a exibição dos dados oficiais.</Text></ScrollView>
}'''
text=text[:start]+results+text[end:]

# Activate existing Favorites drawer entry and route through the normal Raio-X dossier flow.
old='<DrawerItem icon="☆" label="Favoritos" onPress={onClose}/>'
new='<DrawerItem icon="☆" label="Favoritos" onPress={()=>{onGo(\'Favoritos\');onClose()}}/>'
if old not in text: raise SystemExit('Missing Favorites drawer placeholder')
text=text.replace(old,new,1)
old=":tab==='Pesquisas'?<PollsScreen/>:tab==='Apuração'?<ResultsScreen/>:tab==='Comparar'?<Compare/>"
new=":tab==='Pesquisas'?<PollsScreen/>:tab==='Apuração'?<ResultsScreen/>:tab==='Favoritos'?<FavoritesScreen onSelect={c=>{setSelected(c);setTab('Raio-X')}}/>:tab==='Comparar'?<Compare/>"
if old not in text: raise SystemExit('Missing favorites router anchor')
text=text.replace(old,new,1)

p.write_text(text,encoding='utf-8')
print('RAIO-X v0.3.33: persistent Favorites + highlights in Pesquisas and Apuracao applied')
