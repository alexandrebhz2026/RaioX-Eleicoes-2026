import React, {useEffect, useMemo, useState} from 'react';
import {Platform, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View} from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';
import * as AppleAuthentication from 'expo-apple-authentication';
import * as WebBrowser from 'expo-web-browser';
import * as Google from 'expo-auth-session/providers/google';
import * as Facebook from 'expo-auth-session/providers/facebook';
import {makeRedirectUri} from 'expo-auth-session';
import {createUserWithEmailAndPassword, FacebookAuthProvider, GoogleAuthProvider, OAuthProvider, onAuthStateChanged, signInWithCredential, signInWithEmailAndPassword, signOut} from 'firebase/auth';
import {doc, serverTimestamp, setDoc} from 'firebase/firestore';
import {auth, db, firebaseReady} from './firebaseConfig';

WebBrowser.maybeCompleteAuthSession();

const NAVY='#061329', CARD='#0B1D3A', BORDER='#214D80', BLUE='#287DFF', CYAN='#20D0F2', WHITE='#F7FBFF', MUTED='#B4C2D7';
const BIO_KEY='raiox.biometric.enabled';

async function saveUserProfile(user, provider) {
  if (!db || !user) return;
  await setDoc(doc(db, 'users', user.uid), {
    uid: user.uid,
    name: user.displayName || '',
    email: user.email || '',
    photoURL: user.photoURL || '',
    provider: provider || user.providerData?.[0]?.providerId || 'unknown',
    platform: Platform.OS,
    appVersion: '0.3.3',
    lastAccessAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
  }, {merge: true});
}

function LoginScreen({onTestMode}) {
  const [mode,setMode]=useState('login');
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [message,setMessage]=useState('');
  const redirectUri=makeRedirectUri({scheme:'raiox2026'});

  const [googleRequest, googleResponse, googlePrompt] = Google.useAuthRequest({
    androidClientId: process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID || 'missing.apps.googleusercontent.com',
    iosClientId: process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID || 'missing.apps.googleusercontent.com',
    webClientId: process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID || 'missing.apps.googleusercontent.com',
    redirectUri,
  });
  const [facebookRequest, facebookResponse, facebookPrompt] = Facebook.useAuthRequest({
    clientId: process.env.EXPO_PUBLIC_FACEBOOK_APP_ID || '0',
    redirectUri,
  });

  useEffect(()=>{
    if (!firebaseReady || googleResponse?.type!=='success') return;
    const token=googleResponse.authentication?.idToken;
    if (!token) return;
    signInWithCredential(auth, GoogleAuthProvider.credential(token))
      .then(({user})=>saveUserProfile(user,'google.com'))
      .catch(e=>setMessage(e.message));
  },[googleResponse]);

  useEffect(()=>{
    if (!firebaseReady || facebookResponse?.type!=='success') return;
    const token=facebookResponse.authentication?.accessToken;
    if (!token) return;
    signInWithCredential(auth, FacebookAuthProvider.credential(token))
      .then(({user})=>saveUserProfile(user,'facebook.com'))
      .catch(e=>setMessage(e.message));
  },[facebookResponse]);

  async function emailAction(){
    if(!firebaseReady){setMessage('Firebase ainda não configurado nesta versão de teste.');return;}
    if(!email || password.length<6){setMessage('Informe um e-mail válido e senha com pelo menos 6 caracteres.');return;}
    try{
      const result=mode==='register'
        ? await createUserWithEmailAndPassword(auth,email.trim(),password)
        : await signInWithEmailAndPassword(auth,email.trim(),password);
      await saveUserProfile(result.user,'password');
    }catch(e){setMessage(e.message);}
  }

  async function appleLogin(){
    if(!firebaseReady){setMessage('Firebase ainda não configurado nesta versão de teste.');return;}
    try{
      const credential=await AppleAuthentication.signInAsync({requestedScopes:[AppleAuthentication.AppleAuthenticationScope.FULL_NAME,AppleAuthentication.AppleAuthenticationScope.EMAIL]});
      const provider=new OAuthProvider('apple.com');
      const firebaseCredential=provider.credential({idToken:credential.identityToken,rawNonce:undefined});
      const result=await signInWithCredential(auth,firebaseCredential);
      await saveUserProfile(result.user,'apple.com');
    }catch(e){if(e.code!=='ERR_REQUEST_CANCELED') setMessage(e.message);}
  }

  return <SafeAreaView style={s.safe}><ScrollView contentContainerStyle={s.wrap} keyboardShouldPersistTaps="handled">
    <Text style={s.brand}>RAIO-X <Text style={{color:CYAN}}>ELEIÇÕES 2026</Text></Text>
    <Text style={s.tag}>Entre rápido para salvar favoritos, alertas e sincronizar seus dados.</Text>
    <View style={s.card}>
      <TouchableOpacity style={s.social} disabled={!googleRequest} onPress={()=>googlePrompt()}><Text style={s.socialText}>Continuar com Google</Text></TouchableOpacity>
      <TouchableOpacity style={s.social} disabled={!facebookRequest} onPress={()=>facebookPrompt()}><Text style={s.socialText}>Continuar com Facebook</Text></TouchableOpacity>
      {Platform.OS==='ios' && <TouchableOpacity style={s.social} onPress={appleLogin}><Text style={s.socialText}>Continuar com Apple</Text></TouchableOpacity>}
      <View style={s.div}><View style={s.line}/><Text style={s.or}>ou</Text><View style={s.line}/></View>
      <TextInput value={email} onChangeText={setEmail} placeholder="E-mail" placeholderTextColor={MUTED} autoCapitalize="none" keyboardType="email-address" style={s.input}/>
      <TextInput value={password} onChangeText={setPassword} placeholder="Senha" placeholderTextColor={MUTED} secureTextEntry style={s.input}/>
      <TouchableOpacity style={s.primary} onPress={emailAction}><Text style={s.primaryText}>{mode==='register'?'Criar conta':'Entrar com e-mail'}</Text></TouchableOpacity>
      <TouchableOpacity onPress={()=>{setMode(mode==='login'?'register':'login');setMessage('')}}><Text style={s.switch}>{mode==='login'?'Não tenho conta — criar agora':'Já tenho conta — entrar'}</Text></TouchableOpacity>
      {!!message && <Text style={s.msg}>{message}</Text>}
    </View>
    {!firebaseReady && <View style={s.test}><Text style={s.testTitle}>Versão de teste</Text><Text style={s.testText}>Os provedores reais ainda aguardam as credenciais do Firebase. Este botão existe somente para você testar o restante do aplicativo.</Text><TouchableOpacity style={s.testButton} onPress={onTestMode}><Text style={s.testButtonText}>Entrar no modo de teste</Text></TouchableOpacity></View>}
    <Text style={s.privacy}>O RAIO-X não associa silenciosamente suas pesquisas políticas à sua identidade. Dados de conta e preferências sensíveis são tratados separadamente.</Text>
  </ScrollView></SafeAreaView>;
}

function BiometricGate({children,user,onLogout}){
  const [locked,setLocked]=useState(false);
  const [checking,setChecking]=useState(true);
  useEffect(()=>{(async()=>{const enabled=await SecureStore.getItemAsync(BIO_KEY);setLocked(enabled==='1');setChecking(false);})();},[]);
  async function unlock(){
    const result=await LocalAuthentication.authenticateAsync({promptMessage:'Entrar no RAIO-X',cancelLabel:'Usar senha'});
    if(result.success) setLocked(false);
  }
  if(checking) return <SafeAreaView style={s.safe}/>;
  if(locked) return <SafeAreaView style={s.safe}><View style={s.center}><Text style={s.brand}>RAIO-X</Text><Text style={s.tag}>Desbloqueie com biometria para continuar.</Text><TouchableOpacity style={s.primary} onPress={unlock}><Text style={s.primaryText}>Usar biometria</Text></TouchableOpacity><TouchableOpacity onPress={onLogout}><Text style={s.switch}>Entrar de outra forma</Text></TouchableOpacity></View></SafeAreaView>;
  return children;
}

export default function AuthGate({children}){
  const [user,setUser]=useState(firebaseReady?undefined:null);
  const [testMode,setTestMode]=useState(false);
  const [askedBio,setAskedBio]=useState(false);
  useEffect(()=>{
    if(!firebaseReady){setUser(null);return;}
    return onAuthStateChanged(auth, async current=>{setUser(current||null);if(current) await saveUserProfile(current);});
  },[]);
  useEffect(()=>{
    if(!user || askedBio) return;
    setAskedBio(true);
    (async()=>{
      const existing=await SecureStore.getItemAsync(BIO_KEY); if(existing!==null) return;
      const has=await LocalAuthentication.hasHardwareAsync(); const enrolled=await LocalAuthentication.isEnrolledAsync(); if(!has||!enrolled){await SecureStore.setItemAsync(BIO_KEY,'0');return;}
      const result=await LocalAuthentication.authenticateAsync({promptMessage:'Ativar entrada rápida por biometria?',cancelLabel:'Agora não'});
      await SecureStore.setItemAsync(BIO_KEY,result.success?'1':'0');
    })();
  },[user,askedBio]);

  const content=useMemo(()=>children,[children]);
  if(testMode) return content;
  if(user===undefined) return <SafeAreaView style={s.safe}/>;
  if(!user) return <LoginScreen onTestMode={()=>setTestMode(true)}/>;
  return <BiometricGate user={user} onLogout={()=>signOut(auth)}>{content}</BiometricGate>;
}

const s=StyleSheet.create({
 safe:{flex:1,backgroundColor:NAVY},wrap:{padding:22,paddingTop:56,paddingBottom:50},center:{flex:1,padding:24,justifyContent:'center'},brand:{color:WHITE,fontSize:30,fontWeight:'900'},tag:{color:MUTED,fontSize:16,lineHeight:23,marginTop:8,marginBottom:22},card:{backgroundColor:CARD,borderWidth:1,borderColor:BORDER,borderRadius:22,padding:16},social:{borderWidth:1,borderColor:'#335f91',backgroundColor:'#0f2445',paddingVertical:15,borderRadius:15,alignItems:'center',marginBottom:10},socialText:{color:WHITE,fontWeight:'800',fontSize:16},div:{flexDirection:'row',alignItems:'center',gap:10,marginVertical:8},line:{height:1,backgroundColor:'#244b78',flex:1},or:{color:MUTED,fontSize:12},input:{borderWidth:1,borderColor:'#335f91',backgroundColor:'#091a34',color:WHITE,borderRadius:15,paddingHorizontal:15,paddingVertical:14,fontSize:16,marginBottom:10},primary:{backgroundColor:BLUE,borderRadius:15,paddingVertical:16,alignItems:'center',marginTop:2},primaryText:{color:WHITE,fontSize:16,fontWeight:'900'},switch:{color:CYAN,textAlign:'center',fontWeight:'800',marginTop:16},msg:{color:'#FFD166',lineHeight:19,marginTop:14},test:{borderWidth:1,borderColor:'#8a6d22',backgroundColor:'#2b2512',borderRadius:18,padding:15,marginTop:16},testTitle:{color:'#FFD166',fontWeight:'900',fontSize:16},testText:{color:WHITE,lineHeight:19,marginTop:6},testButton:{borderWidth:1,borderColor:'#FFD166',borderRadius:13,paddingVertical:12,alignItems:'center',marginTop:12},testButtonText:{color:'#FFD166',fontWeight:'900'},privacy:{color:MUTED,fontSize:11,lineHeight:16,marginTop:18}
});
