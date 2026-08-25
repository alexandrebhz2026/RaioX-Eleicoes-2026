import patch_v021
from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing v0.3.22 patch target: {label} in {path}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Home: remove the oversized dead space and keep Xis clear of bottom navigation/buttons.
replace_once('AppV020.js', "content:{padding:18,paddingBottom:176,gap:12}", "content:{padding:18,paddingBottom:72,gap:12}", 'compact home bottom spacing')
replace_once('AppV020.js', "<Detective size={44} rounded={22}/></Animated.View><View style={s.onlineDot}/>", "<Detective size={40} rounded={20}/></Animated.View><View style={s.onlineDot}/>", 'smaller floating Xis')
replace_once('AppV020.js', "xisFloat:{position:'absolute',right:12,bottom:86,zIndex:30,borderRadius:26,backgroundColor:'#071426',padding:2,borderWidth:2,borderColor:t.blue,shadowColor:t.shadow,shadowOpacity:.28,shadowRadius:7,elevation:8}", "xisFloat:{position:'absolute',right:14,bottom:118,zIndex:30,borderRadius:24,backgroundColor:'#071426',padding:2,borderWidth:2,borderColor:t.blue,shadowColor:t.shadow,shadowOpacity:.26,shadowRadius:7,elevation:8}", 'Xis safe dock above navigation')
replace_once('AppV020.js', "const VERSION='0.3.21';", "const VERSION='0.3.22';", 'visible version')

# Biometrics: use the actual fingerprint artwork cropped from the approved mockup.
replace_once('AuthGateV020.js', "import {XIS_DETECTIVE} from './XisAssets';", "import {XIS_DETECTIVE} from './XisAssets';\nimport {FINGERPRINT_APPROVED} from './FingerprintApproved';", 'approved biometric artwork import')
replace_once('AuthGateV020.js', '<Text style={s.fingerprint}>◎</Text>', '<Image source={{uri:FINGERPRINT_APPROVED}} style={s.fingerprintApproved} resizeMode="contain"/>', 'approved fingerprint image')
replace_once('AuthGateV020.js', "fingerprintCircle:{width:108,height:108,borderRadius:54,borderWidth:2,borderColor:t.blue,backgroundColor:t.surface2,alignItems:'center',justifyContent:'center',marginVertical:5,shadowColor:t.shadow,shadowOpacity:.16,shadowRadius:11,elevation:4}", "fingerprintCircle:{width:116,height:116,borderRadius:58,borderWidth:0,backgroundColor:'transparent',alignItems:'center',justifyContent:'center',marginVertical:4,shadowColor:t.shadow,shadowOpacity:.10,shadowRadius:8,elevation:2}", 'approved biometric circle')
replace_once('AuthGateV020.js', "fingerprint:{color:t.blue,fontSize:58,lineHeight:64}", "fingerprintApproved:{width:116,height:116,borderRadius:58}", 'approved fingerprint style')
replace_once('AuthGateV020.js', "primary:{height:54,borderRadius:14,backgroundColor:t.blue,alignItems:'center',justifyContent:'center',marginTop:3}", "primary:{width:'100%',height:54,borderRadius:14,backgroundColor:t.blue,alignItems:'center',justifyContent:'center',marginTop:3}", 'full width biometric primary button')
replace_once('AuthGateV020.js', "const APP_VERSION='0.3.21';", "const APP_VERSION='0.3.22';", 'auth version')

print('RAIO-X v0.3.22 exact approved visual patch applied')
