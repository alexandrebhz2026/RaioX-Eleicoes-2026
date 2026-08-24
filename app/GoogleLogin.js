const FIREBASE_API_KEY='AIzaSyAmnbDT48iQW8SpxUZyTQh__HwM0yWgOwY';
const GOOGLE_WEB_CLIENT_ID='982564347981-84aee90mkmb27e7f4bv1m7g6nkeqlkmq.apps.googleusercontent.com';

function messageFrom(payload){
  const code=String(payload?.error?.message||payload?.message||'').split(' : ')[0];
  const map={
    INVALID_IDP_RESPONSE:'O Google não retornou uma credencial válida.',
    OPERATION_NOT_ALLOWED:'O login com Google ainda não está liberado no Firebase.',
    USER_DISABLED:'Esta conta está desativada.'
  };
  return map[code]||code||'Não foi possível entrar com Google.';
}

async function postJson(url,body){
  const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data=await response.json().catch(()=>({}));
  if(!response.ok)throw new Error(messageFrom(data));
  return data;
}

export async function signInWithGoogle(){
  let GoogleSignin;
  try{
    ({GoogleSignin}=require('@react-native-google-signin/google-signin'));
  }catch(e){
    throw new Error('O módulo do Google não iniciou nesta instalação. Use e-mail e senha.');
  }
  try{
    GoogleSignin.configure({webClientId:GOOGLE_WEB_CLIENT_ID,offlineAccess:false});
    await GoogleSignin.hasPlayServices({showPlayServicesUpdateDialog:true});
    await GoogleSignin.signIn();
    const tokens=await GoogleSignin.getTokens();
    if(!tokens?.idToken)throw new Error('O Google não retornou uma credencial válida.');
    const data=await postJson(`https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key=${FIREBASE_API_KEY}`,{
      postBody:`id_token=${encodeURIComponent(tokens.idToken)}&providerId=google.com`,
      requestUri:'http://localhost',
      returnIdpCredential:true,
      returnSecureToken:true
    });
    return {
      uid:data.localId||'',
      idToken:data.idToken||'',
      refreshToken:data.refreshToken||'',
      email:data.email||'',
      name:data.displayName||'',
      photoURL:data.photoUrl||'',
      provider:'google.com',
      createdNow:!!data.isNewUser
    };
  }catch(e){
    const text=String(e?.message||e||'');
    if(text.toLowerCase().includes('cancel'))throw new Error('Login com Google cancelado.');
    throw e;
  }
}
