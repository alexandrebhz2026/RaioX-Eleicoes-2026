import patch_v022
from pathlib import Path
import re


def replace_once(path, old, new, label):
    p=Path(path); text=p.read_text(encoding='utf-8')
    if old not in text: raise SystemExit(f'Missing v0.3.23 patch target: {label} in {path}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')


def regex_once(path, pattern, replacement, label):
    p=Path(path); text=p.read_text(encoding='utf-8')
    new,n=re.subn(pattern,replacement,text,count=1,flags=re.S)
    if n!=1: raise SystemExit(f'Missing v0.3.23 regex target: {label} in {path} ({n})')
    p.write_text(new,encoding='utf-8')

# ---------- Auth / Xis owns the secure access screen ----------
replace_once('AuthGateV020.js',
    "import React,{useEffect,useMemo,useState} from 'react';",
    "import React,{useEffect,useMemo,useRef,useState} from 'react';",
    'auth useRef')
replace_once('AuthGateV020.js',
    "import {Image,Platform,ScrollView,StatusBar,StyleSheet,Text,TextInput,TouchableOpacity,View} from 'react-native';",
    "import {Animated,Image,Platform,ScrollView,StatusBar,StyleSheet,Text,TextInput,TouchableOpacity,View} from 'react-native';",
    'auth Animated')
replace_once('AuthGateV020.js',
    "import {FINGERPRINT_APPROVED} from './FingerprintApproved';",
    "import {FINGERPRINT_APPROVED} from './FingerprintApproved';\nimport {XIS_ACCESS_APPROVED} from './XisAccessApproved';",
    'approved access Xis import')
replace_once('AuthGateV020.js',
    "function XisMini(){const s=useStyles();return <View style={s.xisMini}><Image source={{uri:XIS_DETECTIVE}} style={{width:'100%',height:'100%'}} resizeMode=\"cover\"/></View>}",
    "function XisMini(){const s=useStyles();return <View style={s.xisMini}><Image source={{uri:XIS_DETECTIVE}} style={{width:'100%',height:'100%'}} resizeMode=\"cover\"/></View>}\nfunction authMethodLabel(types=[]){const face=types.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION);return Platform.OS==='ios'&&face?'Face ID':'biometria'}\nfunction authQuestion(label){return label==='Face ID'?'Quer usar o Face ID?':'Quer usar a biometria?'}",
    'auth method helpers')

new_gate = r'''function BiometricGate({children,onLogout}){const {theme,effective}=useTheme();const s=useStyles();const [locked,setLocked]=useState(false),[checking,setChecking]=useState(true),[types,setTypes]=useState([]);const float=useRef(new Animated.Value(0)).current;useEffect(()=>{const loop=Animated.loop(Animated.sequence([Animated.timing(float,{toValue:-7,duration:1050,useNativeDriver:true}),Animated.timing(float,{toValue:0,duration:1050,useNativeDriver:true})]));loop.start();return()=>loop.stop()},[float]);useEffect(()=>{(async()=>{try{const [enabled,supported]=await Promise.all([SecureStore.getItemAsync(BIO_KEY),LocalAuthentication.supportedAuthenticationTypesAsync().catch(()=>[])]);setTypes(supported||[]);setLocked(enabled==='1')}catch{}finally{setChecking(false)}})()},[]);const method=authMethodLabel(types);async function unlock(){try{const result=await LocalAuthentication.authenticateAsync({promptMessage:`Entrar no RAIO-X com ${method}`,cancelLabel:'Usar outra forma'});if(result.success)setLocked(false)}catch{}}if(checking)return <SafeAreaView style={s.safe} edges={['top','left','right','bottom']}/>;if(locked)return <SafeAreaView style={s.safe} edges={['top','left','right','bottom']}><StatusBar barStyle={effective==='light'?'dark-content':'light-content'} backgroundColor={theme.bg}/><ScrollView contentContainerStyle={s.bioWrap} showsVerticalScrollIndicator={false}><Logo/><Text style={s.bioTitle}>Acesso seguro</Text><Text style={s.bioSub}>Desbloqueie com {method} para continuar.</Text><View style={s.bioCard}><View style={s.xisAccessRow}><Animated.View style={[s.xisAccessFrame,{transform:[{translateY:float}]}]}><Image source={{uri:XIS_ACCESS_APPROVED}} style={s.xisAccessImage} resizeMode="cover"/></Animated.View><View style={s.bioSpeech}><Text style={s.bioSpeechText}>{authQuestion(method)}</Text></View></View><View style={s.secureLine}><Text style={s.secureIcon}>◇</Text><Text style={s.secureText}>Seu acesso é individual e protegido por <Text style={{color:s._blue,fontWeight:'900'}}>criptografia</Text>.</Text></View><TouchableOpacity style={s.primary} onPress={unlock}><Text style={s.primaryText}>{method==='Face ID'?'◉  Usar Face ID':'◉  Usar biometria'}</Text></TouchableOpacity><TouchableOpacity style={s.secondary} onPress={onLogout}><Text style={s.secondaryText}>Entrar de outra forma</Text></TouchableOpacity></View><Text style={s.bioPrivacy}>Seus dados biométricos não são armazenados pelo RAIO-X nem enviados para nossos servidores.</Text></ScrollView></SafeAreaView>;return children}'''
regex_once('AuthGateV020.js', r"function BiometricGate\(\{children,onLogout\}\)\{.*?;return children\}", new_gate, 'biometric Xis hero screen')

replace_once('AuthGateV020.js',
    "const result=await LocalAuthentication.authenticateAsync({promptMessage:'Ativar entrada rápida por biometria?',cancelLabel:'Agora não'});",
    "const types=await LocalAuthentication.supportedAuthenticationTypesAsync().catch(()=>[]);const method=authMethodLabel(types);const result=await LocalAuthentication.authenticateAsync({promptMessage:`Ativar entrada rápida por ${method}?`,cancelLabel:'Agora não'});",
    'dynamic first biometric prompt')
replace_once('AuthGateV020.js', "const APP_VERSION='0.3.22';", "const APP_VERSION='0.3.23';", 'auth version')

# Replace obsolete fingerprint layout with the approved Xis-led layout.
regex_once('AuthGateV020.js',
    r"fingerprintCircle:\{.*?\},fingerprintApproved:\{.*?\},secureLine:",
    "xisAccessRow:{width:'100%',flexDirection:'row',alignItems:'center',justifyContent:'center',gap:8,marginTop:3,marginBottom:3},xisAccessFrame:{width:190,height:222,borderRadius:28,overflow:'hidden',backgroundColor:'#fff'},xisAccessImage:{width:'100%',height:'100%'},bioSpeech:{flex:1,minHeight:100,maxWidth:155,borderRadius:24,borderWidth:1.5,borderColor:'#A9D3FF',backgroundColor:t.surface,alignItems:'center',justifyContent:'center',paddingHorizontal:12,shadowColor:t.shadow,shadowOpacity:.08,shadowRadius:8,elevation:2},bioSpeechText:{color:t.text,fontSize:20,lineHeight:26,fontWeight:'900',textAlign:'center'},secureLine:",
    'Xis access styles')
replace_once('AuthGateV020.js', "bioCard:{width:'100%',maxWidth:420,backgroundColor:t.surface,borderWidth:1,borderColor:t.border,borderRadius:22,padding:16,alignItems:'center'}", "bioCard:{width:'100%',maxWidth:440,backgroundColor:t.surface,borderWidth:1,borderColor:t.border,borderRadius:24,padding:14,alignItems:'center'}", 'larger Xis card')
replace_once('AuthGateV020.js', "bioWrap:{flexGrow:1,paddingHorizontal:22,paddingTop:22,paddingBottom:28,alignItems:'center'}", "bioWrap:{flexGrow:1,paddingHorizontal:20,paddingTop:20,paddingBottom:24,alignItems:'center'}", 'access screen spacing')
replace_once('AuthGateV020.js', "bioTitle:{color:t.text,fontSize:28,fontWeight:'900',marginTop:22}", "bioTitle:{color:t.text,fontSize:29,fontWeight:'900',marginTop:20}", 'access title')
replace_once('AuthGateV020.js', "bioSub:{color:t.muted,fontSize:14,marginTop:6,marginBottom:16,textAlign:'center'}", "bioSub:{color:t.muted,fontSize:14,marginTop:6,marginBottom:14,textAlign:'center'}", 'access subtitle')

# ---------- First login: Xis personal-assessor introduction on Home ----------
replace_once('AppV020.js',
    "import {XIS_DETECTIVE} from './XisAssets';",
    "import {XIS_DETECTIVE} from './XisAssets';\nimport {XIS_ACCESS_APPROVED} from './XisAccessApproved';",
    'intro Xis import')
replace_once('AppV020.js', "const VERSION='0.3.22';", "const VERSION='0.3.23';", 'visible version')

intro_component = r'''
function XisWelcome({visible,onDismiss}){const s=useStyles();const pulse=useRef(new Animated.Value(0)).current;useEffect(()=>{if(!visible)return;const loop=Animated.loop(Animated.sequence([Animated.timing(pulse,{toValue:-5,duration:900,useNativeDriver:true}),Animated.timing(pulse,{toValue:0,duration:900,useNativeDriver:true})]));loop.start();return()=>loop.stop()},[visible,pulse]);return <Modal visible={visible} transparent animationType="fade" onRequestClose={onDismiss}><View style={s.welcomeBackdrop}><View style={s.welcomeCard}><Animated.View style={[s.welcomeXis,{transform:[{translateY:pulse}]}]}><Image source={{uri:XIS_ACCESS_APPROVED}} style={s.welcomeXisImage} resizeMode="cover"/></Animated.View><Text style={s.welcomeTitle}>Oi! Eu sou o <Text style={{color:s._blue}}>Xis.</Text></Text><Text style={s.welcomeText}>Seu assessor pessoal dentro do RAIO-X. Posso te ajudar a pesquisar candidatos, comparar informações, entender dados oficiais e navegar pelo app.</Text><View style={s.welcomeHint}><Text style={s.welcomeHintIcon}>✦</Text><Text style={s.welcomeHintText}>Sempre que precisar, é só me chamar pelo botão flutuante.</Text></View><TouchableOpacity style={s.welcomeButton} onPress={onDismiss}><Text style={s.welcomeButtonText}>Ok, obrigado</Text></TouchableOpacity></View></View></Modal>}
'''
replace_once('AppV020.js', "function BottomNav({tab,onGo})", intro_component+"\nfunction BottomNav({tab,onGo})", 'Xis welcome component')

replace_once('AppV020.js',
    "const {theme,effective}=useTheme();const s=useStyles();const [tab,setTab]=useState('Início'),[selected,setSelected]=useState(null),[raioQuery,setRaioQuery]=useState(''),[drawer,setDrawer]=useState(false);",
    "const {theme,effective}=useTheme();const s=useStyles();const [tab,setTab]=useState('Início'),[selected,setSelected]=useState(null),[raioQuery,setRaioQuery]=useState(''),[drawer,setDrawer]=useState(false),[xisWelcome,setXisWelcome]=useState(false);useEffect(()=>{let alive=true,timer=null;(async()=>{const raw=String(session?.uid||session?.email||'local').replace(/[^A-Za-z0-9._-]/g,'_').slice(0,80);const key=`raiox.xis.intro.v1.${raw}`;try{const seen=await SecureStore.getItemAsync(key);if(alive&&seen!=='1')timer=setTimeout(()=>alive&&setXisWelcome(true),450)}catch{}})();return()=>{alive=false;if(timer)clearTimeout(timer)}},[session?.uid,session?.email]);const dismissXisWelcome=async()=>{setXisWelcome(false);const raw=String(session?.uid||session?.email||'local').replace(/[^A-Za-z0-9._-]/g,'_').slice(0,80);try{await SecureStore.setItemAsync(`raiox.xis.intro.v1.${raw}`,'1')}catch{}};",
    'per-user first login Xis intro state')
replace_once('AppV020.js',
    "<Drawer visible={drawer} onClose={()=>setDrawer(false)} session={session} onGo={go} onLogout={onLogout}/></SafeAreaView>",
    "<Drawer visible={drawer} onClose={()=>setDrawer(false)} session={session} onGo={go} onLogout={onLogout}/><XisWelcome visible={xisWelcome} onDismiss={dismissXisWelcome}/></SafeAreaView>",
    'render Xis welcome after login')

# Add welcome styles before chat styles.
replace_once('AppV020.js',
    "chatSafe:{flex:1,backgroundColor:t.bg}",
    "welcomeBackdrop:{flex:1,backgroundColor:'rgba(4,16,34,.62)',alignItems:'center',justifyContent:'center',padding:22},welcomeCard:{width:'100%',maxWidth:430,borderRadius:28,backgroundColor:t.surface,borderWidth:1,borderColor:t.border,padding:18,alignItems:'center',shadowColor:t.shadow,shadowOpacity:.28,shadowRadius:22,elevation:16},welcomeXis:{width:220,height:236,borderRadius:30,overflow:'hidden',backgroundColor:'#fff',marginTop:-2},welcomeXisImage:{width:'100%',height:'100%'},welcomeTitle:{color:t.text,fontSize:29,fontWeight:'900',marginTop:12,textAlign:'center'},welcomeText:{color:t.muted,fontSize:15,lineHeight:22,textAlign:'center',marginTop:10},welcomeHint:{flexDirection:'row',alignItems:'center',gap:9,width:'100%',paddingHorizontal:8,marginTop:16,marginBottom:16},welcomeHintIcon:{color:t.blue,fontSize:25},welcomeHintText:{color:t.muted,fontSize:13,lineHeight:18,flex:1},welcomeButton:{width:'100%',height:56,borderRadius:16,backgroundColor:t.blue,alignItems:'center',justifyContent:'center'},welcomeButtonText:{color:'#fff',fontSize:18,fontWeight:'900'},chatSafe:{flex:1,backgroundColor:t.bg}",
    'Xis welcome styles')

print('RAIO-X v0.3.23 dynamic biometric/Face ID + first-login Xis intro patch applied')
