import React, {useEffect, useState} from 'react';
import {Platform, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View} from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';
import {createUserWithEmailAndPassword, onAuthStateChanged, signInWithEmailAndPassword, signOut} from 'firebase/auth';
import {doc, serverTimestamp, setDoc} from 'firebase/firestore';
import {auth, db, firebaseReady} from './firebaseConfig';

const NAVY='#061329', CARD='#0B1D3A', BORDER='#214D80', BLUE='#287DFF', CYAN='#20D0F2', WHITE='#F7FBFF', MUTED='#B4C2D7';
const BIO_KEY='raiox.biometric.enabled';

async function saveUserProfile(user, provider) {
  if (!db || !user) return;
  try {
    await setDoc(doc(db, 'users', user.uid), {
      uid: user.uid,
      name: user.displayName || '',
      email: user.email || '',
      photoURL: user.photoURL || '',
      provider: provider || user.providerData?.[0]?.providerId || 'unknown',
      platform: Platform.OS,
      appVersion: '0.3.4',
      lastAccessAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    }, {merge: true});
  } catch (e) {
    console.warn('RAIO-X profile sync failed', e?.message || e);
  }
}

function SocialPlaceholder({label}) {
  return <View style={[s.social,s.socialDisabled]}><Text style={s.socialText}>{label}</Text><Text style={s.pending}>ativação após credenciais</Text></View>;
}

function TestLoginScreen({onTestMode}) {
  return <SafeAreaView style={s.safe}><ScrollView contentContainerStyle={s.wrap}>
    <Text style={s.brand}>RAIO-X <Text style={{color:CYAN}}>ELEIÇÕES 2026</Text></Text>
    <Text style={s.tag}>Acesso rápido e seguro.</Text>
    <View style={s.card}>
      <SocialPlaceholder label="Continuar com Google"/>
      <SocialPlaceholder label="Continuar com Facebook"/>
      {Platform.OS==='ios' && <SocialPlaceholder label="Continuar com Apple"/>}
      <View style={s.test}><Text style={s.testTitle}>Versão de teste v0.3.4</Text><Text style={s.testText}>Os provedores sociais não são inicializados enquanto o Firebase e as credenciais oficiais não estiverem configurados. Assim você consegue testar o restante do aplicativo sem risco de falha na abertura.</Text><TouchableOpacity style={s.testButton} onPress={onTestMode}><Text style={s.testButtonText}>Entrar no modo de teste</Text></TouchableOpacity></View>
    </View>
    <Text style={s.privacy}>O RAIO-X não associa silenciosamente suas pesquisas políticas à sua identidade.</Text>
  </ScrollView></SafeAreaView>;
}

function EmailLoginScreen() {
  const [mode,setMode]=useState('login');
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [message,setMessage]=useState('');

  async function emailAction(){
    if(!email || password.length<6){setMessage('Informe um e-mail válido e senha com pelo menos 6 caracteres.');return;}
    try{
      const result=mode==='register'
        ? await createUserWithEmailAndPassword(auth,email.trim(),password)
        : await signInWithEmailAndPassword(auth,email.trim(),password);
      await saveUserProfile(result.user,'password');
    }catch(e){setMessage(e?.message || 'Não foi possível entrar.');}
  }

  return <SafeAreaView style={s.safe}><ScrollView contentContainerStyle={s.wrap} keyboardShouldPersistTaps="handled">
    <Text style={s.brand}>RAIO-X <Text style={{color:CYAN}}>ELEIÇÕES 2026</Text></Text>
    <Text style={s.tag}>Entre para salvar favoritos, alertas e sincronizar seus dados.</Text>
    <View style={s.card}>
      <TextInput value={email} onChangeText={setEmail} placeholder="E-mail" placeholderTextColor={MUTED} autoCapitalize="none" keyboardType="email-address" style={s.input}/>
      <TextInput value={password} onChangeText={setPassword} placeholder="Senha" placeholderTextColor={MUTED} secureTextEntry style={s.input}/>
      <TouchableOpacity style={s.primary} onPress={emailAction}><Text style={s.primaryText}>{mode==='register'?'Criar conta':'Entrar com e-mail'}</Text></TouchableOpacity>
      <TouchableOpacity onPress={()=>{setMode(mode==='login'?'register':'login');setMessage('')}}><Text style={s.switch}>{mode==='login'?'Não tenho conta — criar agora':'Já tenho conta — entrar'}</Text></TouchableOpacity>
      {!!message && <Text style={s.msg}>{message}</Text>}
      <Text style={s.pendingBlock}>Google, Facebook e Apple serão ativados quando as credenciais oficiais forem adicionadas.</Text>
    </View>
  </ScrollView></SafeAreaView>;
}

function BiometricGate({children,onLogout}){
  const [locked,setLocked]=useState(false);
  const [checking,setChecking]=useState(true);
  useEffect(()=>{(async()=>{try{const enabled=await SecureStore.getItemAsync(BIO_KEY);setLocked(enabled==='1');}catch{}finally{setChecking(false);}})();},[]);
  async function unlock(){
    try{
      const result=await LocalAuthentication.authenticateAsync({promptMessage:'Entrar no RAIO-X',cancelLabel:'Usar senha'});
      if(result.success) setLocked(false);
    } catch {}
  }
  if(checking) return <SafeAreaView style={s.safe}/>;
  if(locked) return <SafeAreaView style={s.safe}><View style={s.center}><Text style={s.brand}>RAIO-X</Text><Text style={s.tag}>Desbloqueie com biometria para continuar.</Text><TouchableOpacity style={s.primary} onPress={unlock}><Text style={s.primaryText}>Usar biometria</Text></TouchableOpacity><TouchableOpacity onPress={onLogout}><Text style={s.switch}>Entrar de outra forma</Text></TouchableOpacity></View></SafeAreaView>;
  return children;
}

export default function AuthGate({children}){
  const [testMode,setTestMode]=useState(false);
  const [user,setUser]=useState(firebaseReady?undefined:null);
  const [askedBio,setAskedBio]=useState(false);

  useEffect(()=>{
    if(!firebaseReady){setUser(null);return undefined;}
    try {
      return onAuthStateChanged(auth, async current=>{setUser(current||null);if(current) await saveUserProfile(current);});
    } catch (e) {
      console.warn('RAIO-X auth init failed', e?.message || e);
      setUser(null);
      return undefined;
    }
  },[]);

  useEffect(()=>{
    if(!firebaseReady || !user || askedBio) return;
    setAskedBio(true);
    (async()=>{
      try {
        const existing=await SecureStore.getItemAsync(BIO_KEY); if(existing!==null) return;
        const has=await LocalAuthentication.hasHardwareAsync();
        const enrolled=await LocalAuthentication.isEnrolledAsync();
        if(!has||!enrolled){await SecureStore.setItemAsync(BIO_KEY,'0');return;}
        const result=await LocalAuthentication.authenticateAsync({promptMessage:'Ativar entrada rápida por biometria?',cancelLabel:'Agora não'});
        await SecureStore.setItemAsync(BIO_KEY,result.success?'1':'0');
      } catch {}
    })();
  },[user,askedBio]);

  if(testMode) return children;
  if(!firebaseReady) return <TestLoginScreen onTestMode={()=>setTestMode(true)}/>;
  if(user===undefined) return <SafeAreaView style={s.safe}/>;
  if(!user) return <EmailLoginScreen/>;
  return <BiometricGate onLogout={()=>signOut(auth)}>{children}</BiometricGate>;
}

const s=StyleSheet.create({
 safe:{flex:1,backgroundColor:NAVY},wrap:{padding:22,paddingTop:56,paddingBottom:50},center:{flex:1,padding:24,justifyContent:'center'},brand:{color:WHITE,fontSize:30,fontWeight:'900'},tag:{color:MUTED,fontSize:16,lineHeight:23,marginTop:8,marginBottom:22},card:{backgroundColor:CARD,borderWidth:1,borderColor:BORDER,borderRadius:22,padding:16},social:{borderWidth:1,borderColor:'#335f91',backgroundColor:'#0f2445',paddingVertical:13,borderRadius:15,alignItems:'center',marginBottom:10},socialDisabled:{opacity:.72},socialText:{color:WHITE,fontWeight:'800',fontSize:16},pending:{color:MUTED,fontSize:10,marginTop:3},pendingBlock:{color:MUTED,fontSize:11,lineHeight:16,textAlign:'center',marginTop:18},input:{borderWidth:1,borderColor:'#335f91',backgroundColor:'#091a34',color:WHITE,borderRadius:15,paddingHorizontal:15,paddingVertical:14,fontSize:16,marginBottom:10},primary:{backgroundColor:BLUE,borderRadius:15,paddingVertical:16,alignItems:'center',marginTop:2},primaryText:{color:WHITE,fontSize:16,fontWeight:'900'},switch:{color:CYAN,textAlign:'center',fontWeight:'800',marginTop:16},msg:{color:'#FFD166',lineHeight:19,marginTop:14},test:{borderWidth:1,borderColor:'#8a6d22',backgroundColor:'#2b2512',borderRadius:18,padding:15,marginTop:8},testTitle:{color:'#FFD166',fontWeight:'900',fontSize:16},testText:{color:WHITE,lineHeight:19,marginTop:6},testButton:{borderWidth:1,borderColor:'#FFD166',borderRadius:13,paddingVertical:12,alignItems:'center',marginTop:12},testButtonText:{color:'#FFD166',fontWeight:'900'},privacy:{color:MUTED,fontSize:11,lineHeight:16,marginTop:18}
});
