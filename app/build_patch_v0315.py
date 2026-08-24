from pathlib import Path

app=Path('App.js')
text=app.read_text(encoding='utf-8')

text=text.replace("const APP_VERSION='0.3.14';", "const APP_VERSION='0.3.15';")
text=text.replace('v0.3.14','v0.3.15')

old_dossier="""function Dossier({candidate,onBack}){\n  if(!candidate)return <ScrollView contentContainerStyle={s.content}><Text style={s.pageTitle}>Raio-X</Text><Card><Text style={s.infoTitle}>Escolha um candidato</Text><Text style={s.line}>Abra a Busca e toque em um candidato.</Text></Card></ScrollView>;"""
new_dossier="""function Dossier({candidate,onBack,onSelect}){\n  const [quickQuery,setQuickQuery]=useState('');\n  const quickMatches=useMemo(()=>{\n    const q=normalize(quickQuery);\n    if(!q)return [];\n    return candidates.filter(c=>normalize(c.name).includes(q)||normalize(c.civilName).includes(q)||normalize(c.party).includes(q)||String(c.number||'').includes(q)).slice(0,12);\n  },[quickQuery]);\n  if(!candidate)return <ScrollView contentContainerStyle={s.content} keyboardShouldPersistTaps=\"handled\"><Text style={s.pageTitle}>Raio-X</Text><Text style={s.subtitle}>Digite o nome, número ou partido e abra o dossiê completo diretamente.</Text><TextInput value={quickQuery} onChangeText={setQuickQuery} placeholder=\"Ex.: Kalil, 13, União...\" placeholderTextColor={MUTED} style={s.input}/>{quickQuery.trim()?<>{quickMatches.length?quickMatches.map(c=><CandidateCard key={c.id} candidate={c} onPress={()=>onSelect&&onSelect(c)}/>):<Card><Text style={s.infoTitle}>Nenhum candidato encontrado</Text><Text style={s.line}>Tente outro nome, número ou partido.</Text></Card>}</>:<><Card><Text style={s.infoTitle}>O Raio-X começa aqui</Text><Text style={s.line}>Encontre um candidato e veja identidade, candidatura, patrimônio, chapa, perfil e fontes oficiais.</Text></Card><TouchableOpacity style={s.secondaryButton} onPress={onBack}><Text style={s.secondaryText}>Ver lista completa de candidatos</Text></TouchableOpacity></>}</ScrollView>;"""
if old_dossier not in text:
    raise SystemExit('Dossier empty-state insertion point not found')
text=text.replace(old_dossier,new_dossier,1)

old_screen="""  const openFromCompare=c=>{setSelected(c);setTab('Raio-X')};\n  let screen;if(tab==='Busca')screen=<Search state={searchState} setState={setSearchState} onSelect={c=>{setSelected(c);setTab('Raio-X')}}/>;else if(tab==='Raio-X')screen=<Dossier candidate={selected} onBack={()=>setTab('Busca')}/>;else if(tab==='Comparar')screen=<Compare state={compareState} setState={setCompareState} onOpen={openFromCompare}/>;else if(tab==='Radar')screen=<Placeholder title=\"Radar 2026\" text=\"Mudanças detectadas nas fontes oficiais aparecerão aqui.\"/>;else if(tab==='Conta')screen=<Account session={session} setSession={setSession}/>;else screen=<Home count={candidates.length} goSearch={()=>setTab('Busca')} goCompare={()=>setTab('Comparar')} goAccount={()=>setTab('Conta')} session={session}/>;\n  const nav=[['⌂','Início'],['⌕','Busca'],['X','Raio-X'],['⇄','Comparar'],['◉','Radar']];"""
new_screen="""  const openFromCompare=c=>{setSelected(c);setTab('Raio-X')};\n  const openFromRaiox=c=>{setSelected(c);setTab('Raio-X')};\n  let screen;if(tab==='Busca')screen=<Search state={searchState} setState={setSearchState} onSelect={c=>{setSelected(c);setTab('Raio-X')}}/>;else if(tab==='Raio-X')screen=<Dossier candidate={selected} onBack={()=>{setSelected(null);setTab('Busca')}} onSelect={openFromRaiox}/>;else if(tab==='Comparar')screen=<Compare state={compareState} setState={setCompareState} onOpen={openFromCompare}/>;else if(tab==='Conta')screen=<Account session={session} setSession={setSession}/>;else screen=<Home count={candidates.length} goSearch={()=>setTab('Busca')} goCompare={()=>setTab('Comparar')} goAccount={()=>setTab('Conta')} session={session}/>;\n  const nav=[['⌂','Início'],['⌕','Busca'],['X','Raio-X'],['⇄','Comparar']];"""
if old_screen not in text:
    raise SystemExit('Navigation insertion point not found')
text=text.replace(old_screen,new_screen,1)

if "'Radar'" in text or '>Radar<' in text or "Radar 2026" in text:
    raise SystemExit('Radar still present after patch')

app.write_text(text,encoding='utf-8')

p=Path('PremiumAuthGate.js')
ptext=p.read_text(encoding='utf-8')
ptext=ptext.replace("const APP_VERSION='0.3.14';", "const APP_VERSION='0.3.15';")
ptext=ptext.replace('v0.3.14','v0.3.15')
p.write_text(ptext,encoding='utf-8')

checks=[
    "const APP_VERSION='0.3.15'",
    "Digite o nome, número ou partido",
    "onSelect={openFromRaiox}",
    "const nav=[['⌂','Início'],['⌕','Busca'],['X','Raio-X'],['⇄','Comparar']]",
]
combined=app.read_text(encoding='utf-8')+'\n'+p.read_text(encoding='utf-8')
for item in checks:
    if item not in combined:
        raise SystemExit('missing v0.3.15 item: '+item)
print('v0.3.15 no-radar/direct-raiox patch applied')
