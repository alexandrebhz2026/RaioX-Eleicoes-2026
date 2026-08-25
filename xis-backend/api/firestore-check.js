const API_KEY='AIzaSyAmnbDT48iQW8SpxUZyTQh__HwM0yWgOwY';
const PROJECT_ID='raioxeleicoes2026';

function send(res,status,body){res.statusCode=status;res.setHeader('Content-Type','application/json; charset=utf-8');res.setHeader('Cache-Control','no-store');res.end(JSON.stringify(body))}

export default async function handler(req,res){
  if(req.method!=='GET')return send(res,405,{ok:false,error:'METHOD_NOT_ALLOWED'});
  const email=`raiox-admin-check-${Date.now()}-${Math.random().toString(36).slice(2)}@example.invalid`;
  const password=`Rx!${Math.random().toString(36).slice(2)}A9`;
  let idToken='';
  try{
    const sign=await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=${API_KEY}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password,returnSecureToken:true})});
    const auth=await sign.json().catch(()=>({}));
    if(!sign.ok||!auth?.idToken)return send(res,200,{ok:false,phase:'auth',status:sign.status,message:auth?.error?.message||'TEMP_AUTH_FAILED'});
    idToken=auth.idToken;
    const url=`https://firestore.googleapis.com/v1/projects/${PROJECT_ID}/databases/(default)/documents/users?pageSize=2`;
    const read=await fetch(url,{headers:{Authorization:`Bearer ${idToken}`,Accept:'application/json'}});
    const data=await read.json().catch(()=>({}));
    return send(res,200,{ok:true,firestoreStatus:read.status,canList:read.ok,count:Array.isArray(data?.documents)?data.documents.length:0,error:data?.error?.status||null,message:data?.error?.message||null});
  }catch(e){return send(res,200,{ok:false,phase:'exception',message:String(e?.message||e).slice(0,200)});
  }finally{
    if(idToken){try{await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:delete?key=${API_KEY}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({idToken})})}catch{}}
  }
}
