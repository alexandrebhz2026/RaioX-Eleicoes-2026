import patch_v024
from pathlib import Path
import json


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing v0.3.25 target: {label} in {path}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Video player for the approved Xis introduction.
replace_once(
    'AppV020.js',
    "import * as SecureStore from 'expo-secure-store';",
    "import * as SecureStore from 'expo-secure-store';\nimport {VideoView,useVideoPlayer} from 'expo-video';",
    'expo-video import',
)
replace_once(
    'AppV020.js',
    "import {XIS_ACCESS_APPROVED} from './XisAccessApproved';\n",
    "",
    'remove static welcome image import',
)

old_welcome = '''function XisWelcome({visible,onDismiss}){const s=useStyles();const pulse=useRef(new Animated.Value(0)).current;useEffect(()=>{if(!visible)return;const loop=Animated.loop(Animated.sequence([Animated.timing(pulse,{toValue:-5,duration:900,useNativeDriver:true}),Animated.timing(pulse,{toValue:0,duration:900,useNativeDriver:true})]));loop.start();return()=>loop.stop()},[visible,pulse]);return <Modal visible={visible} transparent animationType="fade" onRequestClose={onDismiss}><View style={s.welcomeBackdrop}><View style={s.welcomeCard}><Animated.View style={[s.welcomeXis,{transform:[{translateY:pulse}]}]}><Image source={{uri:XIS_ACCESS_APPROVED}} style={s.welcomeXisImage} resizeMode="cover"/></Animated.View><Text style={s.welcomeTitle}>Oi! Eu sou o <Text style={{color:s._blue}}>Xis.</Text></Text><Text style={s.welcomeText}>Seu assessor pessoal dentro do RAIO-X. Posso te ajudar a pesquisar candidatos, comparar informações, entender dados oficiais e navegar pelo app.</Text><View style={s.welcomeHint}><Text style={s.welcomeHintIcon}>✦</Text><Text style={s.welcomeHintText}>Sempre que precisar, é só me chamar pelo botão flutuante.</Text></View><TouchableOpacity style={s.welcomeButton} onPress={onDismiss}><Text style={s.welcomeButtonText}>Ok, obrigado</Text></TouchableOpacity></View></View></Modal>}'''
new_welcome = '''function XisWelcome({visible,onDismiss}){const s=useStyles();const player=useVideoPlayer(require('./assets/xis-intro-v9.mp4'),p=>{p.loop=false;p.muted=false;p.volume=1});useEffect(()=>{let timer=null;try{if(visible){player.currentTime=0;player.play();timer=setTimeout(onDismiss,9000)}else player.pause()}catch{}return()=>{if(timer)clearTimeout(timer)}},[visible,player,onDismiss]);return <Modal visible={visible} transparent animationType="fade" onRequestClose={onDismiss}><View style={s.welcomeBackdrop}><View style={s.welcomeVideoCard}><VideoView player={player} style={s.welcomeVideo} nativeControls={false} contentFit="contain" allowsFullscreen={false} allowsPictureInPicture={false}/><TouchableOpacity style={s.welcomeClose} onPress={onDismiss} accessibilityLabel="Fechar apresentação do Xis"><Text style={s.welcomeCloseText}>×</Text></TouchableOpacity></View></View></Modal>}'''
replace_once('AppV020.js', old_welcome, new_welcome, 'Xis welcome image to video')

# Bump the intro key so existing v0.3.24 users see the new approved video once.
replace_once('AppV020.js', 'raiox.xis.intro.v1.${raw}', 'raiox.xis.intro.v2.${raw}', 'intro seen key read')
replace_once('AppV020.js', 'raiox.xis.intro.v1.${raw}', 'raiox.xis.intro.v2.${raw}', 'intro seen key write')

replace_once(
    'AppV020.js',
    "welcomeXis:{width:220,height:236,borderRadius:30,overflow:'hidden',backgroundColor:'#fff',marginTop:-2},welcomeXisImage:{width:'100%',height:'100%'},",
    "welcomeVideoCard:{width:'100%',maxWidth:300,aspectRatio:9/16,borderRadius:26,overflow:'hidden',backgroundColor:'#071426',borderWidth:1,borderColor:t.borderSoft,shadowColor:t.shadow,shadowOpacity:.28,shadowRadius:22,elevation:16},welcomeVideo:{width:'100%',height:'100%'},welcomeClose:{position:'absolute',right:10,top:10,width:34,height:34,borderRadius:17,backgroundColor:'rgba(0,0,0,.55)',alignItems:'center',justifyContent:'center'},welcomeCloseText:{color:'#fff',fontSize:25,lineHeight:28,fontWeight:'700'},",
    'welcome video styles',
)
replace_once('AppV020.js', "const VERSION='0.3.24';", "const VERSION='0.3.25';", 'visible app version')
replace_once('AuthGateV020.js', "const APP_VERSION='0.3.24';", "const APP_VERSION='0.3.25';", 'auth version')

# App config / package versioning. Preserve package/signing line so the APK installs over v0.3.24.
app_path = Path('app.json')
app = json.loads(app_path.read_text(encoding='utf-8'))
expo = app['expo']
expo['version'] = '0.3.25'
expo['android']['versionCode'] = 29
expo.setdefault('extra', {})['xisIntro'] = 'video-v9-first-login-per-user-v025'
expo['extra']['release'] = 'xis-video-intro-v025'
app_path.write_text(json.dumps(app, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

pkg_path = Path('package.json')
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '0.3.25'
pkg['dependencies']['expo-video'] = '~56.1.2'
pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

video = Path('assets/xis-intro-v9.mp4')
if not video.exists() or video.stat().st_size < 90_000:
    raise SystemExit('Approved Xis intro video is missing or incomplete')

print('RAIO-X v0.3.25: approved Xis video intro + update-safe Android version applied')
