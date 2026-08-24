import React, {useEffect, useState} from 'react';
import {Platform, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View} from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';

const NAVY='#061329', CARD='#0B1D3A', BORDER='#214D80', BLUE='#287DFF', CYAN='#20D0F2', WHITE='#F7FBFF', MUTED='#B4C2D7';
const BIO_KEY='raiox.biometric.enabled';
const SESSION_KEY='raiox.auth.session.v1';
const API_KEY='AIzaSyAmnbDT48iQW8SpxUZyTQh__HwM0yWgOwY';
const PROJECT_ID='raioxeleicoes2026';
const GOOGLE_WEB_CLIENT_ID='982564347981-84aee90mkmb27e7f4bv1m7g6nkeqlkmq.apps.googleusercontent.com';
const APP_VERSION='0.3.6';

function firebaseErrorMessage(payload, fallback='Não foi possível concluir a autenticação.') {
  const code=String(payload?.error?.message || payload?.message || '').split(' : ')[0];
  const map={
    EMAIL_EXISTS:'Este e-mail já está cadastrado.',
    EMAIL_NOT_FOUND:'Não encontramos uma conta com este e-mail.',
    INVALID_PASSWORD:'Senha incorreta.',
    INVALID_LOGIN_CREDENTIALS:'E-mail ou senha incorretos.',
    USER_DISABLED:'Esta conta está desativada.',
    OPERATION_NOT_ALLOWED:'Este método de login ainda não está liberado no Firebase.',
    TOO_MANY_ATTEMPTS_TRY_LATER:'Muitas tentativas. Aguarde um pouco e tente novamente.',
    INVALID_IDP_RESPONSE:'O Google não retornou uma credencial válida.',
    NETWORK_REQUEST_FAILED:'Falha de conexão. Verifique a internet e tente novamente.'
  };
  return map[code] || code || fallback;
}

async function postJson(url, body) {
  const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data=await response.json().catch(()=>({}));
  if(!response.ok) throw new Error(firebaseErrorMessage(data));
  return data;
}

function makeSession(data, provider) {
  const expires=Number(data.expiresIn || data.expires_in || 3600);
  return {
    uid:data.localId || data.user_id || '',
    idToken:data.idToken || data.id_token || '',
    refreshToken:data.refreshToken || data.refresh_token || '',
    expiresAt:Date.now() + Math.max(300,expires-60)*1000,
    email:data.email || '',
    name:data.displayName || data.fullName || '',
    photoURL:data.photoUrl || '',
    provider,
    createdAt:new Date().toISOString()
  };
}

async function saveSession(session) {
  await SecureStore.setItemAsync(SESSION_KEY,JSON.stringify(session));
}

async function clearSession() {
  await SecureStore.deleteItemAsync(SESSION_KEY);
}

async function refreshFirebaseSession(session) {
  if(!session?.refreshToken) return null;
  if(session.expiresAt && session.expiresAt>Date.now()+120000) return session;
  const body=`grant_type=refresh_token&refresh_token=${encodeURIComponent(session.refreshToken)}`;
  const response=await fetch(`https://securetoken.googleapis.com/v1/token?key=${API_KEY}`,{
    method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body
  });
  const data=await response.json().catch(()=>({}));
  if(!response.ok) throw new Error(firebaseErrorMessage(data,'Sua sessão expirou. Entre novamente.'));
  const next={...session,idToken:data.id_token,refreshToken:data.refresh_token||session.refreshToken,expiresAt:Date.now()+Math.max(300,Number(data.expires_in||3600)-60)*1000,uid:data.user_id||session.uid};
  await saveSession(next);
  return next;
}

function fsValue(value) {
  if(typeof value==='boolean') return {booleanValue:value};
  if(typeof value==='number') return {integerValue:String(value)};
  return {stringValue:value==null?'':String(value)};
}

async function syncUserProfile(session) {
  if(!session?.uid || !session?.idToken) return;
  const now=new Date().toISOString();
  const fields={
    uid:fsValue(session.uid),
    name:fsValue(session.name||''),
    email:fsValue(session.email||''),
    photoURL:fsValue(session.photoURL||''),
    provider:fsValue(session.provider||'unknown'),
    platform:fsValue(Platform.OS),
    appVersion:fsValue(APP_VERSION),
    createdAt:{timestampValue:session.createdAt||now},
    lastAccessAt:{timestampValue:now},
    updatedAt:{timestampValue:now}
  };
  const url=`https://firestore.googleapis.com/v1/projects/${PROJECT_ID}/databases/(default)/documents/users/${encodeURIComponent(session.uid)}`;
  const response=await fetch(url,{method:'PATCH',headers:{'Content-Type':'application/json','Authorization':`Bearer ${session.idToken}`},body:JSON.stringify({fields})});
  if(!response.ok){
    const data=await response.json().catch(()=>({}));
    console.warn('RAIO-X profile REST sync failed',data?.error?.message||response.status);
  }
}

async function emailFirebaseAuth(email,password,register) {
  const endpoint=register?'signUp':'signInWithPassword';
  const data=await postJson(`https://identitytoolkit.googleapis.com/v1/accounts:${endpoint}?key=${API_KEY}`,{email:email.trim(),password,returnSecureToken:true});
  return makeSession(data,'password');
}

async function googleFirebaseAuth() {
  // Carregamento tardio: se o módulo nativo do Google tiver qualquer problema,
  // o RAIO-X continua abrindo e o erro aparece somente ao tocar neste botão.
  let GoogleSignin;
  try {
    ({GoogleSignin}=require('@react-native-google-signin/google-signin'));
  } catch (e) {
    throw new Error('Login Google indisponível nesta instalação. Use e-mail e senha por enquanto.');
  }
  try {
    GoogleSignin.configure({webClientId:GOOGLE_WEB_CLIENT_ID,offlineAccess:false});
    await GoogleSignin.hasPlayServices({showPlayServicesUpdateDialog:true});
    await GoogleSignin.signIn();
    const tokens=await GoogleSignin.getTokens();
    if(!tokens?.idToken) throw new Error('O Google não retornou uma credencial válida.');
    const data=await postJson(`https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key=${API_KEY}`,{
      postBody:`id_token=${encodeURIComponent(tokens.idToken)}&providerId=google.com`,
      requestUri:'http://localhost',
      returnIdpCredential:true,
      returnSecureToken:true
    });
    return makeSession(data,'google.com');
  } catch (e) {
    const text=String(e?.message||e||'');
    if(text.toLowerCase().includes('cancel')) throw new Error('Login cancelado.');
    throw e;
  }
}

function LoginScreen({onAuthenticated}){
  const [mode,setMode]=useState('login');
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [message,setMessage]=useState('');
  const [busy,setBusy]=useState('');

  async function finish(session){
    await saveSession(session);
    await syncUserProfile(session);
    onAuthenticated(session);
  }

  async function googleLogin(){
    if(busy) return;
    setBusy('google');setMessage('');
    try{await finish(await googleFirebaseAuth());}
    catch(e){setMessage(e?.message||'Não foi possível entrar com Google.');}
    finally{setBusy('');}
  }

  async function emailAction(){
    if(busy) return;
    setMessage('');
    if(!email || password.length<6){setMessage('Informe um e-mail válido e senha com pelo menos 6 caracteres.');return;}
    setBusy('email');
    try{await finish(await emailFirebaseAuth(email,password,mode==='register'));}
    catch(e){setMessage(e?.message||'Não foi possível entrar.');}
    finally{setBusy('');}
  }

  return <SafeAreaView style={s.safe}><ScrollView contentContainerStyle={s.wrap} keyboardShouldPersistTaps="handled">
    <Text style={s.brand}>RAIO-X <Text style={{color:CYAN}}>ELEIÇÕES 2026</Text></Text>
    <Text style={s.tag}>Entre rápido para salvar favoritos, alertas e sincronizar seus dados.</Text>
    <View style={s.card}>
      <TouchableOpacity style={s.social} onPress={googleLogin} disabled={!!busy}>
        <Text style={s.socialText}>{busy==='google'?'Conectando ao Google...':'Continuar com Google'}</Text>
      </TouchableOpacity>
      <View style={[s.social,s.socialDisabled]}><Text style={s.socialText}>Continuar com Facebook</Text><Text style={s.pending}>em preparação</Text></View>
      {Platform.OS==='ios' && <View style={[s.social,s.socialDisabled]}><Text style={s.socialText}>Continuar com Apple</Text><Text style={s.pending}>em preparação</Text></View>}
      <View style={s.div}><View style={s.line}/><Text style={s.or}>ou</Text><View style={s.line}/></View>
      <TextInput value={email} onChangeText={setEmail} placeholder="E-mail" placeholderTextColor={MUTED} autoCapitalize="none" keyboardType="email-address" style={s.input}/>
      <TextInput value={password} onChangeText={setPassword} placeholder="Senha" placeholderTextColor={MUTED} secureTextEntry style={s.input}/>
      <TouchableOpacity style={s.primary} onPress={emailAction} disabled={!!busy}><Text style={s.primaryText}>{busy==='email'?'Aguarde...':mode==='register'?'Criar conta':'Entrar com e-mail'}</Text></TouchableOpacity>
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
  async function unlock(){try{const result=await LocalAuthentication.authenticateAsync({promptMessage:'Entrar no RAIO-X',cancelLabel:'Usar senha'});if(result.success)setLocked(false);}catch{}}
  if(checking) return <SafeAreaView style={s.safe}/>;
  if(locked) return <SafeAreaView style={s.safe}><View style={s.center}><Text style={s.brand}>RAIO-X</Text><Text style={s.tag}>Desbloqueie com biometria para continuar.</Text><TouchableOpacity style={s.primary} onPress={unlock}><Text style={s.primaryText}>Usar biometria</Text></TouchableOpacity><TouchableOpacity onPress={onLogout}><Text style={s.switch}>Entrar de outra forma</Text></TouchableOpacity></View></SafeAreaView>;
  return children;
}

export default function AuthGate({children}){
  const [session,setSession]=useState(undefined);
  const [askedBio,setAskedBio]=useState(false);

  useEffect(()=>{(async()=>{
    try{
      const raw=await SecureStore.getItemAsync(SESSION_KEY);
      if(!raw){setSession(null);return;}
      const restored=await refreshFirebaseSession(JSON.parse(raw));
      if(!restored){await clearSession();setSession(null);return;}
      setSession(restored);
      syncUserProfile(restored).catch(()=>{});
    }catch(e){console.warn('RAIO-X session restore failed',e?.message||e);await clearSession().catch(()=>{});setSession(null);}
  })();},[]);

  useEffect(()=>{
    if(!session || askedBio) return;
    setAskedBio(true);
    (async()=>{try{
      const existing=await SecureStore.getItemAsync(BIO_KEY);if(existing!==null)return;
      const has=await LocalAuthentication.hasHardwareAsync();
      const enrolled=await LocalAuthentication.isEnrolledAsync();
      if(!has||!enrolled){await SecureStore.setItemAsync(BIO_KEY,'0');return;}
      const result=await LocalAuthentication.authenticateAsync({promptMessage:'Ativar entrada rápida por biometria?',cancelLabel:'Agora não'});
      await SecureStore.setItemAsync(BIO_KEY,result.success?'1':'0');
    }catch{}})();
  },[session,askedBio]);

  async function logout(){
    await clearSession().catch(()=>{});
    await SecureStore.deleteItemAsync(BIO_KEY).catch(()=>{});
    setAskedBio(false);setSession(null);
  }

  if(session===undefined) return <SafeAreaView style={s.safe}><View style={s.center}><Text style={s.brand}>RAIO-X</Text><Text style={s.tag}>Inicializando acesso seguro...</Text></View></SafeAreaView>;
  if(!session) return <LoginScreen onAuthenticated={setSession}/>;
  return <BiometricGate onLogout={logout}>{children}</BiometricGate>;
}

const s=StyleSheet.create({
 safe:{flex:1,backgroundColor:NAVY},wrap:{padding:22,paddingTop:56,paddingBottom:50},center:{flex:1,padding:24,justifyContent:'center'},brand:{color:WHITE,fontSize:30,fontWeight:'900'},tag:{color:MUTED,fontSize:16,lineHeight:23,marginTop:8,marginBottom:22},card:{backgroundColor:CARD,borderWidth:1,borderColor:BORDER,borderRadius:22,padding:16},social:{borderWidth:1,borderColor:'#335f91',backgroundColor:'#0f2445',paddingVertical:15,borderRadius:15,alignItems:'center',marginBottom:10},socialDisabled:{opacity:.55},socialText:{color:WHITE,fontWeight:'800',fontSize:16},pending:{color:MUTED,fontSize:10,marginTop:3},div:{flexDirection:'row',alignItems:'center',gap:10,marginVertical:8},line:{height:1,backgroundColor:'#244b78',flex:1},or:{color:MUTED,fontSize:12},input:{borderWidth:1,borderColor:'#335f91',backgroundColor:'#091a34',color:WHITE,borderRadius:15,paddingHorizontal:15,paddingVertical:14,fontSize:16,marginBottom:10},primary:{backgroundColor:BLUE,borderRadius:15,paddingVertical:16,alignItems:'center',marginTop:2},primaryText:{color:WHITE,fontSize:16,fontWeight:'900'},switch:{color:CYAN,textAlign:'center',fontWeight:'800',marginTop:16},msg:{color:'#FFD166',lineHeight:19,marginTop:14},privacy:{color:MUTED,fontSize:11,lineHeight:16,marginTop:18}
});
