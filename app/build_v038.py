from pathlib import Path
import json
import re
import build_v037

p=Path('AppV020.js')
text=p.read_text(encoding='utf-8')

# v0.3.38: one real sync routine for automatic and manual refresh.
# Manual refresh invalidates the local scope cache and explicitly bypasses HTTP/CDN cache.
pattern=r"  const refresh=async\(nextOffice=office,nextUf=uf\)=>\{.*?\};\n  const savePreference="
replacement=r'''  const refresh=async(nextOffice=office,nextUf=uf,opts={})=>{const force=Boolean(opts?.force),o=nextOffice||'PRESIDENTE',u=o==='PRESIDENTE'?'BR':String(nextUf||'MG').toUpperCase().slice(0,2),k=scopeKey(o,u);if(inFlight.current.has(k))return;inFlight.current.add(k);setSyncingKey(k);if(force){try{await SecureStore.deleteItemAsync(cacheKey(k))}catch{}setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),note:'Buscando dados novos na fonte…'}}))}else setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),note:'Atualizando…'}}));try{const nonce=`${Date.now()}-${Math.random().toString(36).slice(2)}`,r=await fetch(`${LIVE_POLLS_API}?office=${encodeURIComponent(o)}&uf=${encodeURIComponent(u)}&force=${force?'1':'0'}&t=${encodeURIComponent(nonce)}`,{headers:{Accept:'application/json','Cache-Control':'no-cache, no-store, max-age=0','Pragma':'no-cache','Expires':'0','X-RAIOX-Refresh':force?'manual-force':'automatic-live'}});const data=await r.json().catch(()=>null);if(r.ok&&data?.ok&&Array.isArray(data.polls)&&data.polls.length){await setScope(k,data.polls,data.fetchedAt,force?'Atualização manual concluída':data.fresh?'Atualizado agora':'Última carga válida confirmada agora')}else setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),updatedAt:data?.fetchedAt||prev[k]?.updatedAt||null,note:data?.warning||'Nenhuma pesquisa registrada e verificável encontrada.'}}))}catch{const cached=force?null:await loadScope(k);if(cached)setScopes(prev=>({...prev,[k]:{...cached,note:'Sem conexão; última carga válida mantida'}}));else setScopes(prev=>({...prev,[k]:{...(prev[k]||{polls:[],updatedAt:null}),note:'Não foi possível consultar as fontes agora'}}))}finally{inFlight.current.delete(k);setSyncingKey(v=>v===k?'':v)}};
  const savePreference='''
text2,count=re.subn(pattern,replacement,text,count=1,flags=re.S)
if count!=1: raise SystemExit(f'Missing refresh block, replaced={count}')
text=text2

# Automatic live refresh while the polls screen is open and app is active.
anchor="  useEffect(()=>{const sub=AppState.addEventListener('change',next=>{if(appState.current.match(/inactive|background/)&&next==='active')refresh(office,uf);appState.current=next});return()=>sub.remove()},[office,uf]);"
if anchor not in text: raise SystemExit('Missing PollsScreen app-state effect')
interval="  useEffect(()=>{const id=setInterval(()=>{if(appState.current==='active')refresh(office,uf,{force:false})},30000);return()=>clearInterval(id)},[office,uf]);"
text=text.replace(anchor,anchor+'\n'+interval,1)

# The visible refresh button must always be a hard refresh, not a cache reread.
old="onPress={()=>refresh(office,uf)} disabled={syncing}"
new="onPress={()=>refresh(office,uf,{force:true})} disabled={syncing}"
if old not in text: raise SystemExit('Missing manual refresh button')
text=text.replace(old,new,1)

# Make the status copy explicit: timestamp is a completed external check, not a screen redraw.
text=text.replace('Última atualização: {stampText}', 'Última coleta externa: {stampText}', 1)

# Release identity.
if "const VERSION='0.3.37';" not in text: raise SystemExit('Missing visible v0.3.37 marker')
text=text.replace("const VERSION='0.3.37';","const VERSION='0.3.38';",1)
p.write_text(text,encoding='utf-8')

for path,old,new in [('AuthGateV020.js',"const APP_VERSION='0.3.37';","const APP_VERSION='0.3.38';"),('XisEngine.js',"'X-App-Version':'0.3.37'","'X-App-Version':'0.3.38'")]:
    q=Path(path);t=q.read_text(encoding='utf-8')
    if old not in t: raise SystemExit(f'Missing version marker in {path}')
    q.write_text(t.replace(old,new,1),encoding='utf-8')

app_path=Path('app.json');app=json.loads(app_path.read_text(encoding='utf-8'));app['expo']['version']='0.3.38';app['expo']['android']['versionCode']=42;app['expo'].setdefault('extra',{})['release']='realtime-hard-refresh-v038';app['expo']['extra']['pollsRefreshSeconds']=30;app['expo']['extra']['manualRefresh']='force-no-cache';app_path.write_text(json.dumps(app,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pkg_path=Path('package.json');pkg=json.loads(pkg_path.read_text(encoding='utf-8'));pkg['version']='0.3.38';pkg_path.write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

print('RAIO-X v0.3.38: manual hard refresh + automatic 30s live polling applied')
