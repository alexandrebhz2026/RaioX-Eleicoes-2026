import patch_v030
from pathlib import Path

p=Path('AppV020.js')
text=p.read_text(encoding='utf-8')
old="  const applyPayload=async(data,label)=>{const next=Array.isArray(data?.polls)?data.polls:[];if(!next.length)return false;setPolls(next);const at=data?.fetchedAt||data?.updatedAt||new Date().toISOString();setUpdatedAt(at);await saveCache(next,at);setSyncNote(label||'Pesquisas atualizadas');return true};"
new="  const applyPayload=async(data,label,scopeOffice=office,scopeUf=uf)=>{const next=Array.isArray(data?.polls)?data.polls:[];if(!next.length)return false;const incoming=new Set(next.map(p=>String(p.institute||'')));const scope=scopeOffice==='GOVERNADOR'?'GOVERNADOR':'PRESIDENTE';const stateUf=scope==='GOVERNADOR'?String(scopeUf||'MG').toUpperCase().slice(0,2):'BR';const merged=[...(polls||[]).filter(p=>{const sameScope=scope==='PRESIDENTE'?String(p.office||'PRESIDENTE')==='PRESIDENTE':String(p.office||'')==='GOVERNADOR'&&String(p.uf||'').toUpperCase()===stateUf;return !sameScope||!incoming.has(String(p.institute||''))}),...next];setPolls(merged);const at=data?.fetchedAt||data?.updatedAt||new Date().toISOString();setUpdatedAt(at);await saveCache(merged,at);setSyncNote(label||'Pesquisas atualizadas');return true};"
if old not in text:
    raise SystemExit('Missing applyPayload target')
text=text.replace(old,new,1)
text=text.replace("await applyPayload(data,data.fresh?'Atualizado agora':'Sem pesquisa nova; última carga válida mantida')","await applyPayload(data,data.fresh?'Atualizado agora':'Sem pesquisa nova; última carga válida mantida',scopeOffice,scopeUf)",1)
text=text.replace("if(response.ok&&await applyPayload(data,'Feed remoto verificado; última carga válida mantida'))return;","if(response.ok&&await applyPayload(data,'Feed remoto verificado; última carga válida mantida',scopeOffice,scopeUf))return;",1)
p.write_text(text,encoding='utf-8')
print('RAIO-X v0.3.30b: incoming poll institutes replace only themselves; other valid institutes are preserved')
