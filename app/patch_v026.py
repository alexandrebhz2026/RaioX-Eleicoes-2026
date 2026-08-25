import patch_v025
from pathlib import Path
import json


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing v0.3.26 target: {label} in {path}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Voice + official Xis visual imports.
replace_once(
    'AppV020.js',
    "import {VideoView,useVideoPlayer} from 'expo-video';",
    "import {VideoView,useVideoPlayer} from 'expo-video';\nimport * as Speech from 'expo-speech';\nimport {ExpoSpeechRecognitionModule,useSpeechRecognitionEvent} from 'expo-speech-recognition';",
    'voice imports',
)

# Official full-body Xis sent and approved by the user.
replace_once(
    'AppV020.js',
    "function Detective({size=92,rounded=22}){const s=useStyles();return <View style={[s.detectiveFrame,{width:size,height:size*1.16,borderRadius:rounded}]}><Image source={{uri:XIS_DETECTIVE}} style={{width:'100%',height:'100%'}} resizeMode=\"cover\"/></View>}",
    "function Detective({size=92,rounded=22}){const s=useStyles();return <View style={[s.detectiveFrame,{width:size,height:size*1.16,borderRadius:rounded}]}><Image source={{uri:XIS_DETECTIVE}} style={{width:'100%',height:'100%'}} resizeMode=\"cover\"/></View>}\nfunction XisOfficial({height=108}){return <Image source={require('./assets/xis-oficial-v026.webp')} style={{height,width:height*.8}} resizeMode=\"contain\"/>}",
    'official Xis helper',
)

old_assistant = '''function XisAssistant({tab,selected,onGo,onRaioX}){const s=useStyles();const [open,setOpen]=useState(false),[question,setQuestion]=useState(''),[messages,setMessages]=useState([]),[busy,setBusy]=useState(false),[remaining,setRemaining]=useState(null);const float=useRef(new Animated.Value(0)).current;useEffect(()=>{const loop=Animated.loop(Animated.sequence([Animated.timing(float,{toValue:-4,duration:1100,useNativeDriver:true}),Animated.timing(float,{toValue:0,duration:1100,useNativeDriver:true})]));loop.start();return()=>loop.stop()},[float]);const openChat=()=>{if(!messages.length)setMessages([{id:`h-${Date.now()}`,role:'xis',text:xisContextHelp(tab,selected),source:'local'}]);setOpen(true)};const ask=async()=>{const raw=question.trim();if(!raw||busy)return;setQuestion('');setBusy(true);setMessages(m=>[...m,{id:`u-${Date.now()}`,role:'user',text:raw}].slice(-16));try{let session=null;try{const saved=await SecureStore.getItemAsync(SESSION_KEY);session=saved?JSON.parse(saved):null}catch{}const result=await askXis(raw,{tab,selected,session});if(result.type==='action'){setBusy(false);setOpen(false);if(result.action==='compare')onGo('Comparar');else if(result.action==='search')onGo('Busca');else if(result.action==='raiox')onRaioX(result.query||raw);return}setRemaining(result.remaining||null);setMessages(m=>[...m,{id:`x-${Date.now()}`,role:'xis',text:result.text||'Não encontrei uma resposta segura para isso.',source:result.source||'local'}].slice(-16))}catch{setMessages(m=>[...m,{id:`e-${Date.now()}`,role:'xis',text:'Não consegui concluir essa pergunta agora. Posso continuar ajudando com os dados oficiais do app.',source:'local'}].slice(-16))}finally{setBusy(false)}};return <><TouchableOpacity style={s.xisFloat} onPress={openChat} activeOpacity={.9}><Animated.View style={{transform:[{translateY:float}]}}><Detective size={40} rounded={20}/></Animated.View><View style={s.onlineDot}/></TouchableOpacity><Modal visible={open} animationType="slide" onRequestClose={()=>setOpen(false)}><SafeAreaView style={s.chatSafe} edges={['top','left','right','bottom']}><View style={s.chatTop}><TouchableOpacity onPress={()=>setOpen(false)}><Text style={s.backArrow}>‹</Text></TouchableOpacity><Detective size={44} rounded={22}/><View style={{flex:1}}><Text style={s.chatTitle}>Xis — Assistente</Text><Text style={s.chatOnline}>● Online</Text></View><TouchableOpacity onPress={()=>setOpen(false)}><Text style={s.closeX}>×</Text></TouchableOpacity></View><ScrollView style={{flex:1}} contentContainerStyle={s.chatMessages}>{messages.map(m=><View key={m.id} style={[s.message,m.role==='user'?s.userMessage:s.xisMessage]}>{m.role==='xis'?<Text style={s.messageSource}>{sourceLabel(m.source)}</Text>:null}<Text style={s.messageText}>{m.text}</Text></View>)}{busy?<View style={[s.message,s.xisMessage]}><Text style={s.messageSource}>XIS VERIFICANDO</Text><Text style={s.messageText}>Primeiro estou procurando nos dados locais, TSE e cache...</Text></View>:null}</ScrollView>{remaining?<Text style={s.remaining}>IA disponível: {remaining.hour??'—'}/h • {remaining.day??'—'}/dia</Text>:null}<View style={s.chatInputRow}><TextInput value={question} onChangeText={setQuestion} onSubmitEditing={ask} returnKeyType="send" placeholder="Digite sua pergunta..." placeholderTextColor={s._muted} style={s.chatInput}/><TouchableOpacity style={s.send} onPress={ask}><Text style={s.sendText}>›</Text></TouchableOpacity></View></SafeAreaView></Modal></>}'''

new_assistant = '''function XisAssistant({tab,selected,onGo,onRaioX}){const s=useStyles();const [open,setOpen]=useState(false),[question,setQuestion]=useState(''),[messages,setMessages]=useState([]),[busy,setBusy]=useState(false),[remaining,setRemaining]=useState(null),[recognizing,setRecognizing]=useState(false),[speaking,setSpeaking]=useState(false),[voiceConversation,setVoiceConversation]=useState(false);const float=useRef(new Animated.Value(0)).current,voiceRef=useRef(null),askRef=useRef(null);useEffect(()=>{const loop=Animated.loop(Animated.sequence([Animated.timing(float,{toValue:-4,duration:1100,useNativeDriver:true}),Animated.timing(float,{toValue:0,duration:1100,useNativeDriver:true})]));loop.start();return()=>loop.stop()},[float]);useEffect(()=>()=>{try{ExpoSpeechRecognitionModule.abort()}catch{};Speech.stop()},[]);useSpeechRecognitionEvent('start',()=>setRecognizing(true));useSpeechRecognitionEvent('end',()=>setRecognizing(false));useSpeechRecognitionEvent('result',e=>{const heard=String(e?.results?.[0]?.transcript||'').trim();if(!heard)return;setQuestion(heard);if(e?.isFinal){setRecognizing(false);setTimeout(()=>askRef.current?.(heard,true),80)}});useSpeechRecognitionEvent('error',e=>{setRecognizing(false);if(e?.error&&e.error!=='aborted'&&e.error!=='no-speech')setMessages(m=>[...m,{id:`ve-${Date.now()}`,role:'xis',text:'Não consegui entender pelo microfone. Você pode tocar nele e tentar de novo ou escrever normalmente.',source:'local'}].slice(-16))});const pickVoice=async()=>{if(voiceRef.current)return voiceRef.current;try{const voices=await Speech.getAvailableVoicesAsync();const pt=voices.filter(v=>String(v.language||'').toLowerCase().startsWith('pt-br'));const preferred=pt.find(v=>/male|masc|pt-br-x-(?:afb|ptd|sfs)/i.test(`${v.name||''} ${v.identifier||''}`))||pt.find(v=>String(v.quality||'').toLowerCase().includes('enhanced'))||pt[0];voiceRef.current=preferred?.identifier||null}catch{}return voiceRef.current};const speakXis=async text=>{const clean=String(text||'').replace(/[*_#`]/g,'').trim();if(!clean)return;try{await Speech.stop();const voice=await pickVoice();Speech.speak(clean,{language:'pt-BR',voice:voice||undefined,rate:.96,pitch:.88,onStart:()=>setSpeaking(true),onDone:()=>setSpeaking(false),onStopped:()=>setSpeaking(false),onError:()=>setSpeaking(false)})}catch{setSpeaking(false)}};const stopSpeaking=async()=>{try{await Speech.stop()}catch{}setSpeaking(false)};const openChat=()=>{if(!messages.length)setMessages([{id:`h-${Date.now()}`,role:'xis',text:xisContextHelp(tab,selected),source:'local'}]);setOpen(true)};const ask=async(rawOverride,fromVoice=false)=>{const raw=String(typeof rawOverride==='string'?rawOverride:question).trim();if(!raw||busy)return;if(fromVoice)setVoiceConversation(true);setQuestion('');setBusy(true);setMessages(m=>[...m,{id:`u-${Date.now()}`,role:'user',text:raw}].slice(-16));try{let session=null;try{const saved=await SecureStore.getItemAsync(SESSION_KEY);session=saved?JSON.parse(saved):null}catch{}const result=await askXis(raw,{tab,selected,session});if(result.type==='action'){setBusy(false);setOpen(false);if(result.action==='compare')onGo('Comparar');else if(result.action==='search')onGo('Busca');else if(result.action==='raiox')onRaioX(result.query||raw);return}const answer=result.text||'Não encontrei uma resposta segura para isso.';setRemaining(result.remaining||null);setMessages(m=>[...m,{id:`x-${Date.now()}`,role:'xis',text:answer,source:result.source||'local'}].slice(-16));if(fromVoice||voiceConversation)speakXis(answer)}catch{const fallback='Não consegui concluir essa pergunta agora. Posso continuar ajudando com os dados oficiais do app.';setMessages(m=>[...m,{id:`e-${Date.now()}`,role:'xis',text:fallback,source:'local'}].slice(-16));if(fromVoice||voiceConversation)speakXis(fallback)}finally{setBusy(false)}};askRef.current=ask;const listen=async()=>{if(busy)return;if(recognizing){try{ExpoSpeechRecognitionModule.stop()}catch{}return}if(speaking)await stopSpeaking();try{const permission=await ExpoSpeechRecognitionModule.requestPermissionsAsync();if(!permission?.granted){setMessages(m=>[...m,{id:`vp-${Date.now()}`,role:'xis',text:'Para conversar comigo por voz, permita o uso do microfone. A digitação continua funcionando normalmente.',source:'local'}].slice(-16));return}setVoiceConversation(true);setQuestion('');ExpoSpeechRecognitionModule.start({lang:'pt-BR',interimResults:true,maxAlternatives:1,continuous:false,requiresOnDeviceRecognition:false,addsPunctuation:true,contextualStrings:['RAIO-X','TSE','presidente','governador','senador','deputado','candidato']})}catch{setRecognizing(false);setMessages(m=>[...m,{id:`vx-${Date.now()}`,role:'xis',text:'O reconhecimento de voz não ficou disponível agora. Você ainda pode escrever sua pergunta.',source:'local'}].slice(-16))}};return <><TouchableOpacity style={s.xisFloat} onPress={openChat} activeOpacity={.9}><Animated.View style={{transform:[{translateY:float}]}}><XisOfficial height={48}/></Animated.View><View style={s.onlineDot}/></TouchableOpacity><Modal visible={open} animationType="slide" onRequestClose={()=>setOpen(false)}><SafeAreaView style={s.chatSafe} edges={['top','left','right','bottom']}><View style={s.chatTop}><TouchableOpacity onPress={()=>setOpen(false)}><Text style={s.backArrow}>‹</Text></TouchableOpacity><XisOfficial height={48}/><View style={{flex:1}}><Text style={s.chatTitle}>Xis — Assistente</Text><Text style={s.chatOnline}>{recognizing?'● Ouvindo...':speaking?'● Falando...':'● Online'}</Text></View>{speaking?<TouchableOpacity style={s.voiceStopTop} onPress={stopSpeaking}><Text style={s.voiceStopTopText}>■</Text></TouchableOpacity>:null}<TouchableOpacity onPress={()=>setOpen(false)}><Text style={s.closeX}>×</Text></TouchableOpacity></View>{(voiceConversation||recognizing||speaking)&&<View style={s.voiceStage}><XisOfficial height={118}/><View style={{flex:1}}><Text style={s.voiceStageTitle}>{recognizing?'Pode falar. Estou ouvindo você.':speaking?'Estou te respondendo.':'Converse comigo'}</Text><Text style={s.voiceStageSub}>{recognizing?(question||'Fale naturalmente em português.'):'Toque no microfone para perguntar por voz. Você também pode continuar digitando.'}</Text></View></View>}<ScrollView style={{flex:1}} contentContainerStyle={s.chatMessages}>{messages.map(m=><View key={m.id} style={[s.message,m.role==='user'?s.userMessage:s.xisMessage]}>{m.role==='xis'?<Text style={s.messageSource}>{sourceLabel(m.source)}</Text>:null}<Text style={s.messageText}>{m.text}</Text>{m.role==='xis'?<TouchableOpacity style={s.listenAnswer} onPress={()=>speakXis(m.text)}><Text style={s.listenAnswerText}>▶ Ouvir Xis</Text></TouchableOpacity>:null}</View>)}{busy?<View style={[s.message,s.xisMessage]}><Text style={s.messageSource}>XIS VERIFICANDO</Text><Text style={s.messageText}>Primeiro estou procurando nos dados locais, TSE e cache...</Text></View>:null}</ScrollView>{remaining?<Text style={s.remaining}>IA disponível: {remaining.hour??'—'}/h • {remaining.day??'—'}/dia</Text>:null}<View style={s.chatInputRow}><TouchableOpacity style={[s.mic,recognizing&&s.micActive]} onPress={listen} accessibilityLabel={recognizing?'Parar de ouvir':'Falar com o Xis'}><Text style={s.micText}>{recognizing?'■':'●'}</Text><Text style={s.micLabel}>{recognizing?'PARAR':'FALAR'}</Text></TouchableOpacity><TextInput value={question} onChangeText={setQuestion} onSubmitEditing={()=>ask()} returnKeyType="send" placeholder={recognizing?'Estou ouvindo...':'Digite ou fale sua pergunta...'} placeholderTextColor={s._muted} style={s.chatInput}/><TouchableOpacity style={s.send} onPress={()=>ask()}><Text style={s.sendText}>›</Text></TouchableOpacity></View></SafeAreaView></Modal></>}'''
replace_once('AppV020.js', old_assistant, new_assistant, 'voice-enabled Xis assistant')

# Styles for voice interaction and official Xis presence.
replace_once(
    'AppV020.js',
    "chatMessages:{padding:14,paddingBottom:24},message:{maxWidth:'86%',borderRadius:15,padding:11,marginBottom:9,borderWidth:1},",
    "voiceStage:{margin:12,marginBottom:0,minHeight:132,borderRadius:20,borderWidth:1,borderColor:t.border,backgroundColor:t.surface,flexDirection:'row',alignItems:'center',paddingHorizontal:12,paddingVertical:7,gap:9},voiceStageTitle:{color:t.text,fontSize:16,fontWeight:'900'},voiceStageSub:{color:t.muted,fontSize:11,lineHeight:16,marginTop:4},voiceStopTop:{width:34,height:34,borderRadius:17,borderWidth:1,borderColor:t.border,alignItems:'center',justifyContent:'center'},voiceStopTopText:{color:t.blue,fontSize:13,fontWeight:'900'},chatMessages:{padding:14,paddingBottom:24},message:{maxWidth:'86%',borderRadius:15,padding:11,marginBottom:9,borderWidth:1},",
    'voice stage styles',
)
replace_once(
    'AppV020.js',
    "messageText:{color:t.mode==='light'?t.text:'#fff',fontSize:13,lineHeight:19},remaining:{color:t.muted,fontSize:9,textAlign:'center',paddingBottom:5},chatInputRow:{flexDirection:'row',gap:8,paddingHorizontal:12,paddingTop:10,paddingBottom:12,borderTopWidth:1,borderTopColor:t.borderSoft,backgroundColor:t.bg},chatInput:{flex:1,height:48,borderRadius:14,borderWidth:1,borderColor:t.border,backgroundColor:t.input,color:t.text,paddingHorizontal:13},",
    "messageText:{color:t.mode==='light'?t.text:'#fff',fontSize:13,lineHeight:19},listenAnswer:{alignSelf:'flex-start',marginTop:8,paddingVertical:4,paddingHorizontal:7,borderRadius:8,backgroundColor:t.surface2},listenAnswerText:{color:t.blue,fontSize:9,fontWeight:'900'},remaining:{color:t.muted,fontSize:9,textAlign:'center',paddingBottom:5},chatInputRow:{flexDirection:'row',gap:8,paddingHorizontal:12,paddingTop:10,paddingBottom:12,borderTopWidth:1,borderTopColor:t.borderSoft,backgroundColor:t.bg,alignItems:'center'},mic:{width:50,height:48,borderRadius:14,borderWidth:1,borderColor:t.blue,backgroundColor:t.surface,alignItems:'center',justifyContent:'center'},micActive:{backgroundColor:t.blue},micText:{color:t.blue,fontSize:11,fontWeight:'900'},micLabel:{color:t.blue,fontSize:7,fontWeight:'900',marginTop:2},chatInput:{flex:1,height:48,borderRadius:14,borderWidth:1,borderColor:t.border,backgroundColor:t.input,color:t.text,paddingHorizontal:13},",
    'voice controls styles',
)

# Correct active mic text contrast without another component branch.
replace_once(
    'AppV020.js',
    "<Text style={s.micText}>{recognizing?'■':'●'}</Text><Text style={s.micLabel}>{recognizing?'PARAR':'FALAR'}</Text>",
    "<Text style={[s.micText,recognizing&&s.micTextActive]}>{recognizing?'■':'●'}</Text><Text style={[s.micLabel,recognizing&&s.micTextActive]}>{recognizing?'PARAR':'FALAR'}</Text>",
    'active microphone contrast',
)
replace_once(
    'AppV020.js',
    "micText:{color:t.blue,fontSize:11,fontWeight:'900'},micLabel:{color:t.blue,fontSize:7,fontWeight:'900',marginTop:2},",
    "micText:{color:t.blue,fontSize:11,fontWeight:'900'},micTextActive:{color:'#fff'},micLabel:{color:t.blue,fontSize:7,fontWeight:'900',marginTop:2},",
    'active microphone text style',
)

replace_once('AppV020.js', "const VERSION='0.3.25';", "const VERSION='0.3.26';", 'visible app version')
replace_once('AuthGateV020.js', "const APP_VERSION='0.3.25';", "const APP_VERSION='0.3.26';", 'auth app version')
# Clean up the stale Xis backend client header while we are versioning this release.
replace_once('XisEngine.js', "'X-App-Version':'0.3.16'", "'X-App-Version':'0.3.26'", 'Xis API app header')

app_path = Path('app.json')
app = json.loads(app_path.read_text(encoding='utf-8'))
expo = app['expo']
expo['version'] = '0.3.26'
expo['android']['versionCode'] = 30
expo.setdefault('extra', {})['xisVoice'] = 'native-stt-tts-ptbr-v026'
expo['extra']['xisVisual'] = 'official-full-body-v026'
expo['extra']['release'] = 'xis-voice-conversation-v026'
plugins = expo.setdefault('plugins', [])
if not any((p == 'expo-speech-recognition') or (isinstance(p, list) and p and p[0] == 'expo-speech-recognition') for p in plugins):
    plugins.append([
        'expo-speech-recognition',
        {
            'microphonePermission': 'Permita que o RAIO-X use o microfone para você conversar com o Xis.',
            'speechRecognitionPermission': 'Permita que o RAIO-X reconheça sua fala para conversar com o Xis.',
            'androidSpeechServicePackages': ['com.google.android.googlequicksearchbox'],
        },
    ])
app_path.write_text(json.dumps(app, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

pkg_path = Path('package.json')
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '0.3.26'
pkg['dependencies']['expo-speech'] = '~56.0.3'
pkg['dependencies']['expo-speech-recognition'] = '56.0.1'
pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

asset = Path('assets/xis-oficial-v026.webp')
if not asset.exists() or asset.stat().st_size < 8_000:
    raise SystemExit('Official Xis full-body asset missing')

print('RAIO-X v0.3.26: Xis voice conversation + official full-body visual applied')
