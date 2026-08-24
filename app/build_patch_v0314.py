from pathlib import Path
import re

app=Path('App.js')
text=app.read_text(encoding='utf-8')
text=text.replace("const APP_VERSION='0.3.13';", "const APP_VERSION='0.3.14';")
text=text.replace('v0.3.13','v0.3.14')
app.write_text(text,encoding='utf-8')

p=Path('PremiumAuthGate.js')
text=p.read_text(encoding='utf-8')
text=text.replace("import React,{useEffect,useState} from 'react';", "import React,{useEffect,useRef,useState} from 'react';")
text=text.replace("import {Platform,ScrollView,StatusBar,StyleSheet,Text,TextInput,TouchableOpacity,View} from 'react-native';", "import {Animated,Easing,Platform,ScrollView,StatusBar,StyleSheet,Text,TextInput,TouchableOpacity,View} from 'react-native';")
text=text.replace("const APP_VERSION='0.3.13';", "const APP_VERSION='0.3.14';")
text=text.replace('v0.3.13','v0.3.14')

pattern=r"function XisMascot\(\{small=false,heart=false\}\)\{.*?\}\nfunction TrustRow"
replacement='''function XisMascot({small=false,heart=false}){
 const floatY=useRef(new Animated.Value(0)).current;
 const pulse=useRef(new Animated.Value(1)).current;
 useEffect(()=>{
  const floating=Animated.loop(Animated.sequence([
   Animated.timing(floatY,{toValue:-8,duration:1100,easing:Easing.inOut(Easing.sin),useNativeDriver:true}),
   Animated.timing(floatY,{toValue:0,duration:1100,easing:Easing.inOut(Easing.sin),useNativeDriver:true}),
  ]));
  const breathing=Animated.loop(Animated.sequence([
   Animated.timing(pulse,{toValue:1.035,duration:900,easing:Easing.inOut(Easing.quad),useNativeDriver:true}),
   Animated.timing(pulse,{toValue:1,duration:900,easing:Easing.inOut(Easing.quad),useNativeDriver:true}),
  ]));
  floating.start(); breathing.start();
  return()=>{floating.stop();breathing.stop();};
 },[floatY,pulse]);
 const scale=small?0.72:1;
 return <Animated.View style={[s.xisWrap,{transform:[{translateY:floatY},{scale}],marginVertical:small?-12:0}]}>
  <Animated.View style={[s.xisGlow,{transform:[{scale:pulse}]}]}/>
  <View style={s.xisHelmet}><View style={s.xisFace}><View style={s.xisEyeOpen}><View style={s.xisEyeCore}/></View><View style={s.xisWink}/><View style={s.xisSmile}/></View></View>
  <View style={s.xisBody}><Text style={s.xisX}>X</Text></View><View style={s.xisArmLeft}/><View style={s.xisThumb}><Text style={s.thumbText}>👍</Text></View>{heart?<Text style={s.heart}>♥</Text>:null}
 </Animated.View>;
}
function TrustRow'''
text2,n=re.subn(pattern,replacement,text,count=1,flags=re.S)
if n!=1:
 raise SystemExit('XisMascot animation insertion point not found')
p.write_text(text2,encoding='utf-8')

checks=[
 "const APP_VERSION='0.3.14'",
 'Animated.loop',
 'translateY:floatY',
 'Continuar com Google',
 'Ativar acesso rápido',
]
combined=app.read_text(encoding='utf-8')+'\n'+p.read_text(encoding='utf-8')
for item in checks:
 if item not in combined:
  raise SystemExit('missing v0.3.14 patch item: '+item)
print('v0.3.14 icon/animation/version patch applied')
