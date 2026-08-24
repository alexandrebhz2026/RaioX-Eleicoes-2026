from pathlib import Path

path = Path('App.js')
text = path.read_text(encoding='utf-8')

text = text.replace("const APP_VERSION='0.3.11';", "const APP_VERSION='0.3.12';")
text = text.replace(
    'O app abre sem autenticação. Google e e-mail só são acionados nesta tela.',
    'Valide sua conta para acessar o RAIO-X. Entre com Google ou use e-mail e senha.'
)
text = text.replace('v0.3.11', 'v0.3.12')

needle = "  useEffect(()=>{const sub=BackHandler.addEventListener('hardwareBackPress',()=>{if(tab==='Raio-X'&&selected){setTab('Busca');return true}if(tab!=='Início'){setTab('Início');return true}return false});return()=>sub.remove()},[tab,selected]);\n  const openFromCompare=c=>{setSelected(c);setTab('Raio-X')};"
replacement = "  useEffect(()=>{const sub=BackHandler.addEventListener('hardwareBackPress',()=>{if(tab==='Raio-X'&&selected){setTab('Busca');return true}if(tab!=='Início'){setTab('Início');return true}return false});return()=>sub.remove()},[tab,selected]);\n  if(!session)return <SafeAreaView style={s.safe} edges={['top','left','right','bottom']}><StatusBar barStyle=\"light-content\" backgroundColor={NAVY}/><View style={s.topbar}><Text style={s.logo}>RAIO-X <Text style={{color:CYAN}}>ELEIÇÕES 2026</Text></Text><Text style={s.version}>v0.3.12</Text></View><View style={{flex:1}}><Account session={session} setSession={setSession}/></View></SafeAreaView>;\n  const openFromCompare=c=>{setSelected(c);setTab('Raio-X')};"

if needle not in text:
    raise SystemExit('Mandatory auth insertion point not found')
text = text.replace(needle, replacement, 1)

path.write_text(text, encoding='utf-8')

if 'if(!session)return <SafeAreaView' not in text:
    raise SystemExit('Mandatory auth gate was not applied')
if 'Valide sua conta para acessar o RAIO-X' not in text:
    raise SystemExit('Mandatory auth copy was not applied')
print('v0.3.12 mandatory authentication gate applied')
