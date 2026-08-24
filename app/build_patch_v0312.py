from pathlib import Path

path = Path('App.js')
text = path.read_text(encoding='utf-8')

text = text.replace("const APP_VERSION='0.3.11';", "const APP_VERSION='0.3.12';")
text = text.replace(
    'O app abre sem autenticação. Google e e-mail só são acionados nesta tela.',
    'Valide sua conta para acessar o RAIO-X. Entre com Google ou use e-mail e senha.'
)
text = text.replace('v0.3.11', 'v0.3.12')

marker = "  const openFromCompare=c=>{setSelected(c);setTab('Raio-X')};"
gate = "  if(!session)return <SafeAreaView style={s.safe} edges={['top','left','right','bottom']}><StatusBar barStyle=\"light-content\" backgroundColor={NAVY}/><View style={s.topbar}><Text style={s.logo}>RAIO-X <Text style={{color:CYAN}}>ELEIÇÕES 2026</Text></Text><Text style={s.version}>v0.3.12</Text></View><View style={{flex:1}}><Account session={session} setSession={setSession}/></View></SafeAreaView>;\n"

if marker not in text:
    raise SystemExit('Mandatory auth marker not found')
if 'if(!session)return <SafeAreaView' not in text:
    text = text.replace(marker, gate + marker, 1)

path.write_text(text, encoding='utf-8')

checks = [
    'if(!session)return <SafeAreaView',
    'Valide sua conta para acessar o RAIO-X',
    'Continuar com Google',
    'Carregar mais',
    'v0.3.12',
]
for item in checks:
    if item not in text:
        raise SystemExit(f'Missing required v0.3.12 marker: {item}')
print('v0.3.12 mandatory authentication gate applied')
