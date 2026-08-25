from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing patch target: {label} in {path}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


def replace_all(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing patch target: {label} in {path}')
    p.write_text(text.replace(old, new), encoding='utf-8')


# App shell: use real Android/iOS safe-area insets and keep the Xis away from actions.
replace_once(
    'AppV020.js',
    "import {Animated,Image,Linking,Modal,SafeAreaView,ScrollView,StatusBar,StyleSheet,Switch,Text,TextInput,TouchableOpacity,View} from 'react-native';",
    "import {Animated,Image,Linking,Modal,ScrollView,StatusBar,StyleSheet,Switch,Text,TextInput,TouchableOpacity,View} from 'react-native';\nimport {SafeAreaView} from 'react-native-safe-area-context';",
    'App safe-area import',
)
replace_all('AppV020.js', '<SafeAreaView style={s.safe}>', "<SafeAreaView style={s.safe} edges={['top','left','right','bottom']}>", 'App root safe area')
replace_once('AppV020.js', '<SafeAreaView style={s.chatSafe}>', "<SafeAreaView style={s.chatSafe} edges={['top','left','right','bottom']}>", 'Xis chat safe area')
replace_once('AppV020.js', '<Detective size={54} rounded={27}/></Animated.View><View style={s.onlineDot}/>', '<Detective size={44} rounded={22}/></Animated.View><View style={s.onlineDot}/>', 'smaller floating Xis')
replace_once('AppV020.js', "content:{padding:18,paddingBottom:130,gap:12}", "content:{padding:18,paddingBottom:176,gap:12}", 'scroll bottom clearance')
replace_once('AppV020.js', "xisFloat:{position:'absolute',right:15,bottom:78,zIndex:30,borderRadius:31,backgroundColor:'#071426',padding:3,borderWidth:2,borderColor:t.blue,shadowColor:t.shadow,shadowOpacity:.3,shadowRadius:8,elevation:9}", "xisFloat:{position:'absolute',right:12,bottom:86,zIndex:30,borderRadius:26,backgroundColor:'#071426',padding:2,borderWidth:2,borderColor:t.blue,shadowColor:t.shadow,shadowOpacity:.28,shadowRadius:7,elevation:8}", 'floating Xis position')
replace_once('AppV020.js', "bottomNav:{height:68,flexDirection:'row',backgroundColor:t.nav,borderTopWidth:1,borderTopColor:t.borderSoft,paddingBottom:4}", "bottomNav:{height:72,flexDirection:'row',backgroundColor:t.nav,borderTopWidth:1,borderTopColor:t.borderSoft,paddingBottom:6}", 'bottom nav sizing')
replace_once('AppV020.js', "chatInputRow:{flexDirection:'row',gap:8,padding:10,borderTopWidth:1,borderTopColor:t.borderSoft}", "chatInputRow:{flexDirection:'row',gap:8,paddingHorizontal:12,paddingTop:10,paddingBottom:12,borderTopWidth:1,borderTopColor:t.borderSoft,backgroundColor:t.bg}", 'chat composer clearance')
replace_once('AppV020.js', "const VERSION='0.3.20';", "const VERSION='0.3.21';", 'visible version')

# Auth/biometrics: compact, scroll-safe layout with Xis still present.
replace_once(
    'AuthGateV020.js',
    "import {Image,Platform,SafeAreaView,ScrollView,StatusBar,StyleSheet,Text,TextInput,TouchableOpacity,View} from 'react-native';",
    "import {Image,Platform,ScrollView,StatusBar,StyleSheet,Text,TextInput,TouchableOpacity,View} from 'react-native';\nimport {SafeAreaView} from 'react-native-safe-area-context';",
    'Auth safe-area import',
)
replace_all('AuthGateV020.js', '<SafeAreaView style={s.safe}>', "<SafeAreaView style={s.safe} edges={['top','left','right','bottom']}>", 'Auth safe areas')
replace_once('AuthGateV020.js', '<View style={s.bioWrap}>', '<ScrollView contentContainerStyle={s.bioWrap} showsVerticalScrollIndicator={false}>', 'biometric scroll container')
replace_once('AuthGateV020.js', '</View></SafeAreaView>;return children}', '</ScrollView></SafeAreaView>;return children}', 'biometric scroll close')
replace_once('AuthGateV020.js', "const APP_VERSION='0.3.20';", "const APP_VERSION='0.3.21';", 'auth app version')
replace_once('AuthGateV020.js', "bioWrap:{flex:1,padding:24,paddingTop:44,alignItems:'center'}", "bioWrap:{flexGrow:1,paddingHorizontal:22,paddingTop:22,paddingBottom:28,alignItems:'center'}", 'biometric wrap')
replace_once('AuthGateV020.js', "bioTitle:{color:t.text,fontSize:32,fontWeight:'900',marginTop:34}", "bioTitle:{color:t.text,fontSize:28,fontWeight:'900',marginTop:22}", 'biometric title')
replace_once('AuthGateV020.js', "bioSub:{color:t.muted,fontSize:15,marginTop:7,marginBottom:22}", "bioSub:{color:t.muted,fontSize:14,marginTop:6,marginBottom:16,textAlign:'center'}", 'biometric subtitle')
replace_once('AuthGateV020.js', "bioCard:{width:'100%',maxWidth:420,backgroundColor:t.surface,borderWidth:1,borderColor:t.border,borderRadius:23,padding:18,alignItems:'center'}", "bioCard:{width:'100%',maxWidth:420,backgroundColor:t.surface,borderWidth:1,borderColor:t.border,borderRadius:22,padding:16,alignItems:'center'}", 'biometric card')
replace_once('AuthGateV020.js', "fingerprintCircle:{width:142,height:142,borderRadius:71,borderWidth:2,borderColor:t.blue,backgroundColor:t.surface2,alignItems:'center',justifyContent:'center',marginVertical:8,shadowColor:t.shadow,shadowOpacity:.2,shadowRadius:14,elevation:5}", "fingerprintCircle:{width:108,height:108,borderRadius:54,borderWidth:2,borderColor:t.blue,backgroundColor:t.surface2,alignItems:'center',justifyContent:'center',marginVertical:5,shadowColor:t.shadow,shadowOpacity:.16,shadowRadius:11,elevation:4}", 'smaller biometric fingerprint')
replace_once('AuthGateV020.js', "fingerprint:{color:t.blue,fontSize:82,lineHeight:88}", "fingerprint:{color:t.blue,fontSize:58,lineHeight:64}", 'smaller fingerprint glyph')
replace_once('AuthGateV020.js', "secureLine:{flexDirection:'row',alignItems:'center',gap:9,paddingVertical:13,paddingHorizontal:8}", "secureLine:{flexDirection:'row',alignItems:'center',gap:9,paddingVertical:10,paddingHorizontal:8}", 'secure message spacing')
replace_once('AuthGateV020.js', "xisHelp:{width:'100%',maxWidth:420,minHeight:98,borderRadius:18,borderWidth:1,borderColor:t.border,backgroundColor:t.surface,flexDirection:'row',alignItems:'center',gap:11,padding:11,marginTop:18}", "xisHelp:{width:'100%',maxWidth:420,minHeight:82,borderRadius:18,borderWidth:1,borderColor:t.border,backgroundColor:t.surface,flexDirection:'row',alignItems:'center',gap:11,padding:10,marginTop:14}", 'Xis biometric helper card')
replace_once('AuthGateV020.js', "xisMini:{width:70,height:82,borderRadius:19,overflow:'hidden',backgroundColor:'#071426',borderWidth:1,borderColor:t.border}", "xisMini:{width:56,height:65,borderRadius:16,overflow:'hidden',backgroundColor:'#071426',borderWidth:1,borderColor:t.border}", 'smaller Xis helper')
replace_once('AuthGateV020.js', "bioPrivacy:{color:t.muted,fontSize:10,lineHeight:15,textAlign:'center',marginTop:15,maxWidth:380}", "bioPrivacy:{color:t.muted,fontSize:10,lineHeight:15,textAlign:'center',marginTop:12,marginBottom:6,maxWidth:380}", 'biometric privacy spacing')

# Root safe-area provider is required by the SDK 56 safe-area implementation.
replace_once(
    'index.js',
    "import {SafeAreaView,StyleSheet,Text,View} from 'react-native';",
    "import {StyleSheet,Text,View} from 'react-native';\nimport {SafeAreaProvider,SafeAreaView} from 'react-native-safe-area-context';",
    'root safe-area imports',
)
replace_once('index.js', "function Root(){return <ThemeProvider><StartupBoundary><AuthGateV020><SafeApp/></AuthGateV020></StartupBoundary></ThemeProvider>}", "function Root(){return <SafeAreaProvider><ThemeProvider><StartupBoundary><AuthGateV020><SafeApp/></AuthGateV020></StartupBoundary></ThemeProvider></SafeAreaProvider>}", 'SafeAreaProvider root')
replace_all('index.js', '<SafeAreaView style={s.safe}>', "<SafeAreaView style={s.safe} edges={['top','left','right','bottom']}>", 'fallback safe area')

print('RAIO-X v0.3.21 layout patch applied')
