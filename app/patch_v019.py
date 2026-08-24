from pathlib import Path
import re

app_path=Path('App.js')
auth_path=Path('AuthGate.js')
app=app_path.read_text(encoding='utf-8')
auth=auth_path.read_text(encoding='utf-8')

if "const XIS_AVATAR=require('./assets/xis-avatar.jpg');" not in app:
    anchor="import {askXis,xisContextHelp} from './XisEngine';\n"
    if anchor not in app:
        raise SystemExit('XisEngine import anchor not found')
    app=app.replace(anchor,anchor+"const XIS_AVATAR=require('./assets/xis-avatar.jpg');\n",1)

visual=r'''function XisFace({large=false}){
  const width=large?112:64, height=large?134:76;
  return <View style={{width,height,borderRadius:large?24:18,overflow:'hidden',backgroundColor:'#F7FBFF',borderWidth:2,borderColor:CYAN,shadowColor:'#20D0F2',shadowOpacity:.32,shadowRadius:10,elevation:8}}><Image source={XIS_AVATAR} style={{width:'100%',height:'100%'}} resizeMode="cover"/></View>;
}

function XisHero(){
  const enter=useRef(new Animated.Value(0)).current, float=useRef(new Animated.Value(0)).current;
  useEffect(()=>{Animated.spring(enter,{toValue:1,useNativeDriver:true,friction:7,tension:42}).start();const loop=Animated.loop(Animated.sequence([Animated.timing(float,{toValue:-5,duration:1050,useNativeDriver:true}),Animated.timing(float,{toValue:0,duration:1050,useNativeDriver:true})]));loop.start();return()=>loop.stop();},[enter,float]);
  return <View style={[s.xisHero,{padding:12,backgroundColor:'#081A33',borderColor:'#1B6EA2'}]}><Animated.View style={{opacity:enter,transform:[{translateY:float},{scale:enter}]}}><XisFace large/></Animated.View><View style={s.xisHeroBubble}><Text style={[s.xisHeroName,{fontSize:20}]}>Oi! Eu sou o Xis.</Text><Text style={s.xisHeroText}>Seu investigador do RAIO-X. Eu navego pelo app, explico dados, encontro candidatos e comparo informações. Primeiro uso dados locais e do TSE; IA só entra quando realmente precisa.</Text><View style={{flexDirection:'row',flexWrap:'wrap',gap:6,marginTop:9}}><Text style={{color:GREEN,fontSize:10,fontWeight:'900'}}>✓ DADOS OFICIAIS</Text><Text style={{color:CYAN,fontSize:10,fontWeight:'900'}}>✓ IMPARCIAL</Text></View></View></View>;
}'''
app,n=re.subn(r"function XisFace\(\{large=false\}\)\{.*?\n\}\n\nfunction XisHero\(\)\{.*?\n\}",visual,app,count=1,flags=re.S)
if n!=1:
    raise SystemExit('Xis visual block not replaced')

home=r'''function Home({count,goRaioX}){return <ScrollView contentContainerStyle={s.content}><View style={{marginTop:3,marginBottom:12}}><Text style={{color:GREEN,fontSize:11,fontWeight:'900',letterSpacing:1.4}}>RAIO-X ELEIÇÕES 2026</Text><Text style={[s.homeTitle,{fontSize:28,lineHeight:34,marginTop:6}]}>O que você quer descobrir hoje?</Text><Text style={s.subtitleSmall}>O Xis ajuda você a investigar candidatos com dados oficiais e sem dizer em quem votar.</Text></View><XisHero/><Card style={s.homeMain}><Text style={s.homeKicker}>INVESTIGUE UM CANDIDATO</Text><Text style={[s.homeTitle,{fontSize:22,lineHeight:28}]}>Nome ou número. O resto deixa com o Xis.</Text><Text style={s.line}>Abra o dossiê completo, confira patrimônio, candidatura, partido, chapa e a fonte oficial.</Text><TouchableOpacity style={[s.primary,{marginTop:16,marginBottom:2}]} onPress={goRaioX}><Text style={s.primaryText}>FAZER RAIO-X</Text></TouchableOpacity></Card><Card><View style={{flexDirection:'row',alignItems:'center',gap:14}}><Text style={{color:CYAN,fontSize:28,fontWeight:'900'}}>{count.toLocaleString('pt-BR')}</Text><View style={{flex:1}}><Text style={{color:WHITE,fontSize:15,fontWeight:'900'}}>registros oficiais carregados</Text><Text style={{color:MUTED,fontSize:11,lineHeight:16,marginTop:2}}>Base organizada a partir do Portal de Dados Abertos do TSE.</Text></View></View></Card><View style={{flexDirection:'row',justifyContent:'space-around',paddingVertical:4}}><Text style={{color:MUTED,fontSize:10,fontWeight:'800'}}>DADOS OFICIAIS</Text><Text style={{color:MUTED,fontSize:10,fontWeight:'800'}}>FONTES</Text><Text style={{color:MUTED,fontSize:10,fontWeight:'800'}}>IMPARCIALIDADE</Text></View></ScrollView>}'''
app,n=re.subn(r"function Home\(\{count,goRaioX\}\)\{.*?\nfunction Placeholder",home+"\nfunction Placeholder",app,count=1,flags=re.S)
if n!=1:
    raise SystemExit('Home block not replaced')

assistant=r'''function XisAssistant({tab,selected,onGo,onRaioX}){
  const [open,setOpen]=useState(false), [question,setQuestion]=useState(''), [messages,setMessages]=useState([]), [busy,setBusy]=useState(false), [remaining,setRemaining]=useState(null);
  const float=useRef(new Animated.Value(0)).current;
  useEffect(()=>{const loop=Animated.loop(Animated.sequence([Animated.timing(float,{toValue:-5,duration:950,useNativeDriver:true}),Animated.timing(float,{toValue:0,duration:950,useNativeDriver:true})]));loop.start();return()=>loop.stop();},[float]);
  const contextHelp=xisContextHelp(tab,selected);
  const openXis=()=>{if(messages.length===0)setMessages([{id:`hello-${Date.now()}`,role:'xis',text:contextHelp,source:'local'}]);setOpen(true)};
  const ask=async()=>{
    const raw=question.trim();if(!raw||busy)return;
    setQuestion('');setBusy(true);
    setMessages(m=>[...m,{id:`u-${Date.now()}`,role:'user',text:raw}].slice(-14));
    try{
      let session=null;try{const saved=await SecureStore.getItemAsync(SESSION_KEY);session=saved?JSON.parse(saved):null}catch{}
      const result=await askXis(raw,{tab,selected,session});
      if(result.type==='action'){
        setBusy(false);setOpen(false);
        if(result.action==='compare')onGo('Comparar');else if(result.action==='search')onGo('Busca');else if(result.action==='raiox')onRaioX(result.query||raw);
        return;
      }
      setRemaining(result.remaining||null);
      setMessages(m=>[...m,{id:`x-${Date.now()}`,role:'xis',text:result.text||'Não encontrei uma resposta segura para isso.',source:result.source||'local'}].slice(-14));
    }catch(e){setMessages(m=>[...m,{id:`e-${Date.now()}`,role:'xis',text:'Não consegui concluir essa pergunta agora. Eu continuo disponível para navegar e consultar os dados oficiais do app.',source:'local'}].slice(-14))}
    finally{setBusy(false)}
  };
  return <><TouchableOpacity activeOpacity={.9} style={s.xisFloating} onPress={openXis}><Animated.View style={{transform:[{translateY:float}]}}><XisFace/></Animated.View><View style={s.xisHelpDot}><Text style={s.xisHelpDotText}>?</Text></View></TouchableOpacity>
  <Modal visible={open} transparent animationType="slide" onRequestClose={()=>setOpen(false)}><View style={s.modalShade}><View style={s.xisPanel}><View style={s.xisPanelTop}><XisFace/><View style={{flex:1}}><Text style={s.xisPanelTitle}>Fala com o Xis</Text><Text style={s.xisPanelSub}>Pergunte sobre esta tela, um candidato ou qualquer dado do RAIO-X.</Text></View><TouchableOpacity onPress={()=>setOpen(false)} style={s.closeBtn}><Text style={s.closeText}>×</Text></TouchableOpacity></View><ScrollView style={{maxHeight:310}} contentContainerStyle={{paddingBottom:8}} keyboardShouldPersistTaps="handled">{messages.map(m=><View key={m.id} style={{alignSelf:m.role==='user'?'flex-end':'stretch',maxWidth:m.role==='user'?'86%':'100%',backgroundColor:m.role==='user'?'#123A69':CARD,borderWidth:1,borderColor:m.role==='user'?'#2E6097':BORDER,borderRadius:16,padding:11,marginBottom:9}}>{m.role==='xis'?<Text style={{color:m.source==='ai'?YELLOW:m.source==='tse'?GREEN:m.source==='cache'?CYAN:MUTED,fontSize:9,fontWeight:'900',marginBottom:5}}>{sourceLabel(m.source)}</Text>:null}<Text style={{color:WHITE,fontSize:14,lineHeight:20}}>{m.text}</Text></View>)}{busy?<View style={{backgroundColor:CARD,borderWidth:1,borderColor:BORDER,borderRadius:16,padding:11,marginBottom:9}}><Text style={{color:CYAN,fontSize:10,fontWeight:'900',marginBottom:5}}>XIS VERIFICANDO</Text><Text style={{color:WHITE,fontSize:14,lineHeight:20}}>Primeiro estou procurando uma resposta sem gastar IA...</Text></View>:null}</ScrollView>{remaining?<Text style={s.xisRemaining}>IA disponível: {remaining.hour ?? '—'}/h • {remaining.day ?? '—'}/dia</Text>:null}<View style={s.quickRow}><TouchableOpacity style={s.quickBtn} onPress={()=>{setOpen(false);onRaioX('')}}><Text style={s.quickText}>Raio-X</Text></TouchableOpacity><TouchableOpacity style={s.quickBtn} onPress={()=>{setOpen(false);onGo('Busca')}}><Text style={s.quickText}>Cargos</Text></TouchableOpacity><TouchableOpacity style={s.quickBtn} onPress={()=>{setOpen(false);onGo('Comparar')}}><Text style={s.quickText}>Comparar</Text></TouchableOpacity></View><TextInput value={question} onChangeText={setQuestion} onSubmitEditing={ask} returnKeyType="send" editable={!busy} placeholder="Pergunte ao Xis..." placeholderTextColor={MUTED} style={s.input}/><TouchableOpacity style={[s.primary,busy&&{opacity:.6}]} onPress={ask} disabled={busy}><Text style={s.primaryText}>{busy?'VERIFICANDO...':'PERGUNTAR AO XIS'}</Text></TouchableOpacity><Text style={s.xisEconomy}>Local, TSE e cache são ilimitados. A IA só é usada no último caso: máximo de 10/h e 25/dia por usuário.</Text></View></View></Modal></>;
}'''
app,n=re.subn(r"function XisAssistant\(\{tab,selected,onGo,onRaioX\}\)\{.*?\n\}\n\nexport default function App",assistant+"\n\nexport default function App",app,count=1,flags=re.S)
if n!=1:
    raise SystemExit('XisAssistant block not replaced')

app=app.replace("useEffect(()=>{if(initialQuery){setQuery(initialQuery);setSearched(true)}},[initialQuery]);","useEffect(()=>{setQuery(initialQuery);setSearched(Boolean(initialQuery))},[initialQuery]);")
app=app.replace('<Text style={s.version}>v0.3.15</Text>','<Text style={s.version}>v0.3.19</Text>')
if 'v0.3.19</Text>' not in app:
    raise SystemExit('visible version not patched')

auth=auth.replace("const APP_VERSION='0.3.6';","const APP_VERSION='0.3.19';")
if "const APP_VERSION='0.3.19';" not in auth:
    raise SystemExit('AuthGate version not patched')

app_path.write_text(app,encoding='utf-8')
auth_path.write_text(auth,encoding='utf-8')
print('v0.3.19 UI patch applied')
