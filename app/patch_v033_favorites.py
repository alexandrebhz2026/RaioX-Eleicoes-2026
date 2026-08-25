import patch_v033
from pathlib import Path

p=Path('AppV020.js'); text=p.read_text(encoding='utf-8')

# Persistent favorites key.
if "const FAVORITES_KEY=" not in text:
    text=text.replace("const SESSION_KEY='raiox.auth.session.v1';","const SESSION_KEY='raiox.auth.session.v1';\nconst FAVORITES_KEY='raiox.favorites.v033';",1)

# Favorite button: works from candidate cards and dossier, persisted locally.
anchor='function CandidateCard({candidate,onPress})'
start=text.find(anchor)
end=text.find('\nfunction DirectSearch(',start)
if start<0 or end<0: raise SystemExit('Missing CandidateCard block for favorites')
fav_components=r'''async function readFavoriteIds(){try{const raw=await SecureStore.getItemAsync(FAVORITES_KEY);const ids=JSON.parse(raw||'[]');return Array.isArray(ids)?ids.map(String):[]}catch{return []}}
async function writeFavoriteIds(ids){try{await SecureStore.setItemAsync(FAVORITES_KEY,JSON.stringify([...new Set(ids.map(String))]))}catch{}}
function FavoriteButton({candidate,compact=false,onChange}){const s=useStyles();const [fav,setFav]=useState(false);useEffect(()=>{let active=true;(async()=>{const ids=await readFavoriteIds();if(active)setFav(ids.includes(String(candidate?.id)))})();return()=>{active=false}},[candidate?.id]);const toggle=async()=>{const id=String(candidate?.id||'');if(!id)return;const ids=await readFavoriteIds();const next=ids.includes(id)?ids.filter(x=>x!==id):[...ids,id];await writeFavoriteIds(next);setFav(next.includes(id));onChange?.(next.includes(id))};return <TouchableOpacity onPress={toggle} style={{minWidth:compact?34:118,height:compact?34:40,paddingHorizontal:compact?8:12,borderRadius:compact?17:14,borderWidth:1,borderColor:fav?'#F0A020':s._border,backgroundColor:fav?'rgba(240,160,32,.10)':s._surface2,alignItems:'center',justifyContent:'center',flexDirection:'row',gap:6}}><Text style={{fontSize:compact?18:16,color:fav?'#F0A020':s._muted}}>{fav?'★':'☆'}</Text>{compact?null:<Text style={{color:fav?'#B56E00':s._text,fontSize:9,fontWeight:'900'}}>{fav?'FAVORITO':'FAVORITAR'}</Text>}</TouchableOpacity>}
function CandidateCard({candidate,onPress}){const s=useStyles();return <TouchableOpacity activeOpacity={.84} onPress={onPress}><Card style={s.candidateCard}><CandidatePhoto candidate={candidate}/><View style={{flex:1,minWidth:0}}><Text style={s.candidateName} numberOfLines={1}>{candidate.name}</Text><Text style={s.candidateMeta} numberOfLines={1}>{candidate.number||'—'} • {candidate.office}</Text><Text style={s.candidateMeta} numberOfLines={1}>{candidate.party||'Partido não informado'} • {candidate.uf||'BR'}</Text><View style={s.statusChip}><Text style={s.statusChipText}>{clean(candidate.status,'Registro TSE')}</Text></View></View><View style={{alignItems:'center',gap:5}}><FavoriteButton candidate={candidate} compact/><Text style={s.chevron}>›</Text></View></Card></TouchableOpacity>}'''
text=text[:start]+fav_components+text[end:]

# Add favorite control to dossier profile.
start=text.find('function Dossier({candidate,onBack})')
end=text.find('\nfunction Metric(',start)
if start<0 or end<0: raise SystemExit('Missing Dossier block for favorites')
block=text[start:end]
needle='<View style={s.profileStatus}><Text style={s.profileStatusText}>{clean(candidate.status,\'Registro TSE\')}</Text></View></View></Card>'
if needle not in block: raise SystemExit('Missing dossier profile target')
block=block.replace(needle,"<View style={s.profileStatus}><Text style={s.profileStatusText}>{clean(candidate.status,'Registro TSE')}</Text></View><View style={{marginTop:10,alignSelf:'flex-start'}}><FavoriteButton candidate={candidate}/></View></View></Card>",1)
text=text[:start]+block+text[end:]

# Favorites tracking screen. Polls are refreshed on open; live result polling only continues every 20s while TSE says any favorite race is active.
insert_at=text.find('\nfunction Settings({onLogout})')
if insert_at<0: raise SystemExit('Missing Settings anchor for FavoritesScreen')
favorites=r'''
function FavoritesScreen({onSelect}){
  const s=useStyles();const [items,setItems]=useState([]),[tracking,setTracking]=useState({}),[busy,setBusy]=useState(true),[live,setLive]=useState(false);
  const officeCode=c=>{const o=normalize(c?.office);if(o==='PRESIDENTE')return 'PRESIDENTE';if(o==='GOVERNADOR')return 'GOVERNADOR';if(o==='SENADOR')return 'SENADOR';if(o==='DEPUTADO FEDERAL')return 'DEPUTADO_FEDERAL';if(o==='DEPUTADO DISTRITAL')return 'DEPUTADO_DISTRITAL';return 'DEPUTADO_ESTADUAL'};
  const matchName=(a,b)=>{const x=normalize(a),y=normalize(b);return x&&y&&(x===y||x.includes(y)||y.includes(x))};
  const load=async()=>{setBusy(true);const ids=await readFavoriteIds();const favs=candidates.filter(c=>ids.includes(String(c.id)));setItems(favs);if(!favs.length){setTracking({});setLive(false);setBusy(false);return}const groups={};for(const c of favs){const office=officeCode(c),uf=office==='PRESIDENTE'?'BR':String(c.uf||'MG').toUpperCase();const k=`${office}:${uf}`;(groups[k]||(groups[k]={office,uf,candidates:[]})).candidates.push(c)}const next={};let anyLive=false;await Promise.all(Object.values(groups).map(async g=>{let polls=null,results=null;try{const r=await fetch(`${LIVE_POLLS_API}?office=${g.office}&uf=${g.uf}&t=${Date.now()}`,{headers:{Accept:'application/json'}});polls=await r.json().catch(()=>null)}catch{}try{const r=await fetch(`${LIVE_RESULTS_API}?office=${g.office}&uf=${g.uf}&t=${Date.now()}`,{headers:{Accept:'application/json','Cache-Control':'no-cache'}});results=await r.json().catch(()=>null)}catch{}if(results?.active)anyLive=true;for(const c of g.candidates){let pollHit=null;for(const poll of Array.isArray(polls?.polls)?polls.polls:[]){const row=(poll.results||[]).find(x=>matchName(x?.[0],c.name)||matchName(x?.[0],c.civilName));if(row){pollHit={institute:poll.institute,published:poll.published,mode:poll.mode,percent:row[2],question:poll.question};break}}const resultHit=(results?.candidates||[]).find(x=>matchName(x?.name,c.name)||matchName(x?.name,c.civilName));next[String(c.id)]={poll:pollHit,result:resultHit||null,resultActive:Boolean(results?.active),percentSections:results?.totals?.percentSections||0,tseUpdatedAt:results?.tseUpdatedAt||'',resultMessage:results?.message||'Apuração ainda não iniciada.'}}}));setTracking(next);setLive(anyLive);setBusy(false)};
  useEffect(()=>{load()},[]);
  useEffect(()=>{if(!live)return;const id=setInterval(load,20000);return()=>clearInterval(id)},[live]);
  return <ScrollView contentContainerStyle={[s.content,{paddingBottom:110}]}><View style={{flexDirection:'row',alignItems:'flex-start',justifyContent:'space-between',gap:10}}><View style={{flex:1}}><Text style={s.pageTitle}>Favoritos</Text><Text style={s.pageSub}>Acompanhe seus candidatos nas pesquisas e, quando começar, na apuração oficial.</Text></View><TouchableOpacity onPress={load} style={{paddingHorizontal:12,paddingVertical:9,borderRadius:14,borderWidth:1,borderColor:s._border,backgroundColor:s._surface}}><Text style={{color:s._blue,fontSize:9,fontWeight:'900'}}>{busy?'ATUALIZANDO…':'↻ ATUALIZAR'}</Text></TouchableOpacity></View>{!items.length&&!busy?<Card><Text style={s.cardTitle}>Nenhum favorito ainda</Text><Text style={s.cardSub}>Abra qualquer candidato e toque em ☆ Favoritar. Ele aparecerá aqui automaticamente.</Text></Card>:items.map(c=>{const t=tracking[String(c.id)]||{};return <View key={c.id} style={{gap:8}}><CandidateCard candidate={c} onPress={()=>onSelect(c)}/><View style={{flexDirection:'row',gap:8}}><View style={{flex:1,backgroundColor:s._surface,borderWidth:1,borderColor:s._border,borderRadius:16,padding:12}}><Text style={{color:s._blue,fontSize:8,fontWeight:'900'}}>PESQUISAS</Text>{t.poll?<><Text style={{color:s._text,fontSize:20,fontWeight:'900',marginTop:4}}>{t.poll.percent}%</Text><Text style={{color:s._text,fontSize:10,fontWeight:'800'}}>{t.poll.institute} · {t.poll.published}</Text><Text style={{color:s._muted,fontSize:8,marginTop:3}}>{t.poll.mode||'Pesquisa publicada'}</Text></>:<Text style={{color:s._muted,fontSize:10,lineHeight:15,marginTop:6}}>Não apareceu em pesquisa verificável carregada para este cargo.</Text>}</View><View style={{flex:1,backgroundColor:s._surface,borderWidth:1,borderColor:t.resultActive?'#20B779':s._border,borderRadius:16,padding:12}}><Text style={{color:t.resultActive?'#20B779':s._muted,fontSize:8,fontWeight:'900'}}>{t.resultActive?'● APURAÇÃO AO VIVO':'APURAÇÃO'}</Text>{t.result?<><Text style={{color:s._text,fontSize:18,fontWeight:'900',marginTop:4}}>{Number(t.result.votes||0).toLocaleString('pt-BR')} votos</Text><Text style={{color:s._blue,fontSize:11,fontWeight:'900'}}>{Number(t.result.percent||0).toLocaleString('pt-BR')}%</Text><Text style={{color:s._muted,fontSize:8,marginTop:3}}>{t.percentSections}% das seções</Text></>:<Text style={{color:s._muted,fontSize:10,lineHeight:15,marginTop:6}}>{t.resultMessage||'Apuração ainda não iniciada.'}</Text>}</View></View></View>})}<Text style={{color:s._muted,fontSize:8,lineHeight:13,textAlign:'center'}}>Favoritos ficam salvos neste aparelho. Durante apuração ativa, esta tela atualiza a cada 20 segundos enquanto estiver aberta.</Text></ScrollView>
}
'''
text=text[:insert_at]+favorites+text[insert_at:]

# Drawer Favorites becomes functional.
old='<DrawerItem icon="☆" label="Favoritos" onPress={onClose}/>'
new='<DrawerItem icon="☆" label="Favoritos" onPress={()=>{onGo(\'Favoritos\');onClose()}}/>'
if old not in text: raise SystemExit('Missing drawer favorites target')
text=text.replace(old,new,1)

# Router Favorites screen before Settings.
old=":tab==='Configurações'?<Settings onLogout={onLogout}/>"
new=":tab==='Favoritos'?<FavoritesScreen onSelect={c=>{setSelected(c);setTab('Dossiê')}}/>:tab==='Configurações'?<Settings onLogout={onLogout}/>"
if old not in text: raise SystemExit('Missing router settings target')
text=text.replace(old,new,1)

p.write_text(text,encoding='utf-8')
print('RAIO-X v0.3.33: persistent favorites + polls/results tracking applied')
