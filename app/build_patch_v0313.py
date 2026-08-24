from pathlib import Path
import re

path=Path('App.js')
text=path.read_text(encoding='utf-8')

if "./PremiumAuthGate" not in text:
    text=text.replace("import {signInWithGoogle} from './GoogleLogin';", "import {signInWithGoogle} from './GoogleLogin';\nimport PremiumAuthGate,{disableQuickAccess} from './PremiumAuthGate';")

text=text.replace("const APP_VERSION='0.3.12';", "const APP_VERSION='0.3.13';")
text=text.replace('v0.3.12','v0.3.13')

old_photo="function Photo({candidate,compact=false}){const src=candidatePhotos?.[candidate?.id];const style=compact?s.photoCompact:s.photoLarge;if(src)return <Image source={src} style={style} resizeMode=\"cover\"/>;return <View style={[style,s.photoFallback]}><Text style={s.photoX}>X</Text><Text style={s.photoFallbackText}>Foto oficial indisponível</Text></View>}"
new_photo="function Photo({candidate,compact=false}){const bundled=candidatePhotos?.[candidate?.id];const [remoteFailed,setRemoteFailed]=useState(false);const style=compact?s.photoCompact:s.photoLarge;useEffect(()=>setRemoteFailed(false),[candidate?.id]);const remote=candidate?.id&&candidate?.uf?{uri:`https://divulgacandcontas.tse.jus.br/divulga/rest/arquivo/img/20322002026/${candidate.id}/${candidate.uf}`} : null;const src=bundled||(!remoteFailed?remote:null);if(src)return <Image source={src} style={style} resizeMode=\"cover\" onError={()=>{if(!bundled)setRemoteFailed(true)}}/>;return <View style={[style,s.photoFallback]}><Text style={s.photoX}>X</Text><Text style={s.photoFallbackText}>Foto oficial indisponível</Text></View>}"
if old_photo not in text:
    raise SystemExit('Photo component insertion point not found')
text=text.replace(old_photo,new_photo,1)

old_gate='''  if(!session){\n    return <SafeAreaView style={s.safe} edges={[\'top\',\'left\',\'right\',\'bottom\']}><StatusBar barStyle="light-content" backgroundColor={NAVY}/><View style={s.topbar}><Text style={s.logo}>RAIO-X <Text style={{color:CYAN}}>ELEIÇÕES 2026</Text></Text><Text style={s.version}>v0.3.13</Text></View><View style={{flex:1}}><Account session={session} setSession={setSession}/></View></SafeAreaView>;\n  }'''
new_gate="  if(!session)return <PremiumAuthGate setSession={setSession}/>;"
if old_gate not in text:
    raise SystemExit('Mandatory gate insertion point not found')
text=text.replace(old_gate,new_gate,1)

text=text.replace('onPress={()=>setSession(null)}><Text style={s.secondaryText}>Sair da conta</Text>', 'onPress={async()=>{await disableQuickAccess();setSession(null)}}><Text style={s.secondaryText}>Sair da conta</Text>')

path.write_text(text,encoding='utf-8')

checks=[
    "PremiumAuthGate setSession={setSession}",
    "const APP_VERSION='0.3.13'",
    "divulgacandcontas.tse.jus.br/divulga/rest/arquivo/img/20322002026",
    "disableQuickAccess();setSession(null)",
]
for item in checks:
    if item not in text:
        raise SystemExit('missing expected patch: '+item)
print('v0.3.13 premium auth/photo patch applied')
