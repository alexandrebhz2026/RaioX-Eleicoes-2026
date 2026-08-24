import React, {useEffect, useState} from 'react';
import {Platform, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View} from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';
import {GoogleSignin} from '@react-native-google-signin/google-signin';
import {createUserWithEmailAndPassword, GoogleAuthProvider, onAuthStateChanged, signInWithCredential, signInWithEmailAndPassword, signOut} from 'firebase/auth';
import {doc, serverTimestamp, setDoc} from 'firebase/firestore';
import {auth, db, firebaseReady} from './firebaseConfig';

const NAVY='#061329', CARD='#0B1D3A', BORDER='#214D80', BLUE='#287DFF', CYAN='#20D0F2', WHITE='#F7FBFF', MUTED='#B4C2D7';
const BIO_KEY='raiox.biometric.enabled';
const GOOGLE_WEB_CLIENT_ID='982564347981-84aee90mkmb27e7f4bv1m7g6nkeqlkmq.apps.googleusercontent.com';

let googleConfigured=false;
function configureGoogle(){
  if(googleConfigured) return;
  GoogleSignin.configure({webClientId:GOOGLE_WEB_CLIENT_ID,offlineAccess:false});
  googleConfigured=true;
}

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
      appVersion: '0.3.5',
      lastAccessAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    }, {merge: true});
  } catch (e) {
    console.warn('RAIO-X profile sync failed', e?.message || e);
  }
}

function LoginScreen(){
  const [mode,setMode]=useState('login');
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [message,setMessage]=useState('');
  const [googleBusy,setGoogleBusy]=useState(false);

  useEffect(()=>{
    try{configureGoogle();}catch(e){console.warn('Google config failed',e?.message||e);}
  },[]);

  async function googleLogin(){
    if(googleBusy) return;
    setGoogleBusy(true);
    setMessage('');
    try{
      configureGoogle();
      await GoogleSignin.hasPlayServices({showPlayServicesUpdateDialog:true});
      await GoogleSignin.signIn();
      const tokens=await GoogleSignin.getTokens();
      if(!tokens?.idToken) throw new Error('O Google não retornou um token de acesso válido.');
      const result=await signInWithCredential(auth,GoogleAuthProvider.credential(tokens.idToken));
      await saveUserProfile(result.user,'google.com');
    }catch(e){
      const msg=e?.message||'Não foi possível entrar com Google.';
      if(!String(msg).toLowerCase().includes('cancel')) setMessage(msg);
    }finally{setGoogleBusy(false);}
  }

  async function emailAction(){
    setMessage('');
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
    <Text style={s.tag}>Entre rápido para salvar favoritos, alertas e sincronizar seus dados.</Text>
    <View style={s.card}>
      <TouchableOpacity style={s.social} onPress={googleLogin} disabled={googleBusy}>
        <Text style={s.socialText}>{googleBusy?'Conectando ao Google...':'Continuar com Google'}</Text>
      </TouchableOpacity>
      <View style={[s.social,s.socialDisabled]}><Text style={s.socialText}>Continuar com Facebook</Text><Text style={s.pending}>em preparação</Text></View>
      {Platform.OS==='ios' && <View style={[s.social,s.socialDisabled]}><Text style={s.socialText}>Continuar com Apple</Text><Text style={s.pending}>em preparação</Text></View>}
      <View style={s.div}><View style={s.line}/><Text style={s.or}>ou</Text><View style={s.line}/></View>
      <TextInput value={email} onChangeText={setEmail} placeholder="E-mail" placeholderTextColor={MUTED} autoCapitalize="none" keyboardType="email-address" style={s.input}/>
      <TextInput value={password} onChangeText={setPassword} placeholder="Senha" placeholderTextColor={MUTED} secureTextEntry style={s.input}/>
      <TouchableOpacity style={s.primary} onPress={emailAction}><Text style={s.primaryText}>{mode==='register'?'Criar conta':'Entrar com e-mail'}</Text></TouchableOpacity>
      <TouchableOpacity onPress={()=>{setMode(mode==='login'?'register':'login');setMessage('')}}><Text style={s.switch}>{mode==='login'?'Não tenho conta — criar agora':'Já tenho conta — entrar'}</Text></TouchableOpacity>
      {!!message && <Text style={s.msg}>{message}</Text>}
    </View>
    <Text style={s.privacy}>O RAIO-X não associa silenciosamente suas pesquisas políticas à sua identidade. Dados de conta e preferências sensíveis são tratados separadamente.</Text>
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

  if(!firebaseReady) return <SafeAreaView style={s.safe}><View style={s.center}><Text style={s.brand}>RAIO-X</Text><Text style={s.msg}>Configuração do Firebase indisponível nesta compilação.</Text></View></SafeAreaView>;
  if(user===undefined) return <SafeAreaView style={s.safe}/>;
  if(!user) return <LoginScreen/>;
  return <BiometricGate onLogout={()=>signOut(auth)}>{children}</BiometricGate>;
}

const s=StyleSheet.create({
 safe:{flex:1,backgroundColor:NAVY},wrap:{padding:22,paddingTop:56,paddingBottom:50},center:{flex:1,padding:24,justifyContent:'center'},brand:{color:WHITE,fontSize:30,fontWeight:'900'},tag:{color:MUTED,fontSize:16,lineHeight:23,marginTop:8,marginBottom:22},card:{backgroundColor:CARD,borderWidth:1,borderColor:BORDER,borderRadius:22,padding:16},social:{borderWidth:1,borderColor:'#335f91',backgroundColor:'#0f2445',paddingVertical:15,borderRadius:15,alignItems:'center',marginBottom:10},socialDisabled:{opacity:.55},socialText:{color:WHITE,fontWeight:'800',fontSize:16},pending:{color:MUTED,fontSize:10,marginTop:3},div:{flexDirection:'row',alignItems:'center',gap:10,marginVertical:8},line:{height:1,backgroundColor:'#244b78',flex:1},or:{color:MUTED,fontSize:12},input:{borderWidth:1,borderColor:'#335f91',backgroundColor:'#091a34',color:WHITE,borderRadius:15,paddingHorizontal:15,paddingVertical:14,fontSize:16,marginBottom:10},primary:{backgroundColor:BLUE,borderRadius:15,paddingVertical:16,alignItems:'center',marginTop:2},primaryText:{color:WHITE,fontSize:16,fontWeight:'900'},switch:{color:CYAN,textAlign:'center',fontWeight:'800',marginTop:16},msg:{color:'#FFD166',lineHeight:19,marginTop:14},privacy:{color:MUTED,fontSize:11,lineHeight:16,marginTop:18}
});
