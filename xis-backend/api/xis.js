import crypto from 'node:crypto';

const MODEL='gpt-5.4-nano';
const PROJECT_ID='raioxeleicoes2026';
const HOURLY_LIMIT=10;
const DAILY_LIMIT=25;
const MAX_QUESTION=1200;
const MAX_OUTPUT_TOKENS=220;

const root=globalThis;
if(!root.__raioxXisRate) root.__raioxXisRate=new Map();
const rate=root.__raioxXisRate;

function json(res,status,body){
  res.statusCode=status;
  res.setHeader('Content-Type','application/json; charset=utf-8');
  res.setHeader('Cache-Control','no-store');
  res.end(JSON.stringify(body));
}
function clean(v,max=MAX_QUESTION){return String(v??'').replace(/[\u0000-\u001F\u007F]/g,' ').replace(/\s+/g,' ').trim().slice(0,max)}
function b64url(s){return Buffer.from(String(s).replace(/-/g,'+').replace(/_/g,'/').padEnd(Math.ceil(String(s).length/4)*4,'='),'base64')}

async function verifyFirebase(idToken){
  if(!idToken) throw new Error('AUTH_REQUIRED');
  const parts=String(idToken).split('.');
  if(parts.length!==3) throw new Error('AUTH_INVALID');
  let header,payload;
  try{
    header=JSON.parse(b64url(parts[0]).toString('utf8'));
    payload=JSON.parse(b64url(parts[1]).toString('utf8'));
  }catch{throw new Error('AUTH_INVALID')}
  if(header.alg!=='RS256'||!header.kid) throw new Error('AUTH_INVALID');
  const now=Math.floor(Date.now()/1000);
  if(payload.aud!==PROJECT_ID||payload.iss!==`https://securetoken.google.com/${PROJECT_ID}`||!payload.sub||Number(payload.exp||0)<=now||Number(payload.iat||0)>now+60) throw new Error('AUTH_INVALID');
  const response=await fetch('https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com');
  const certs=await response.json();
  const cert=certs[header.kid];
  if(!cert) throw new Error('AUTH_INVALID');
  const verifier=crypto.createVerify('RSA-SHA256');
  verifier.update(`${parts[0]}.${parts[1]}`);
  verifier.end();
  if(!verifier.verify(cert,b64url(parts[2]))) throw new Error('AUTH_INVALID');
  return {uid:String(payload.sub),email:String(payload.email||'')};
}
function nowDay(t=Date.now()){
  return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(t));
}
function consume(uid){
  const now=Date.now(),hourAgo=now-3600000,today=nowDay(now);
  const events=(rate.get(uid)||[]).filter(t=>Number(t)>now-86400000);
  const hour=events.filter(t=>Number(t)>=hourAgo).length;
  const day=events.filter(t=>nowDay(Number(t))===today).length;
  if(hour>=HOURLY_LIMIT)return {ok:false,kind:'hour',remaining:{hour:0,day:Math.max(0,DAILY_LIMIT-day)}};
  if(day>=DAILY_LIMIT)return {ok:false,kind:'day',remaining:{hour:Math.max(0,HOURLY_LIMIT-hour),day:0}};
  events.push(now);rate.set(uid,events.slice(-40));
  return {ok:true,remaining:{hour:Math.max(0,HOURLY_LIMIT-hour-1),day:Math.max(0,DAILY_LIMIT-day-1)}};
}
function rollback(uid){const events=rate.get(uid)||[];if(events.length){events.pop();rate.set(uid,events)}}
function compactContext(input){
  const c=input&&typeof input==='object'?input:{};
  const cand=c.candidate&&typeof c.candidate==='object'?c.candidate:null;
  return {screen:clean(c.screen,40),dataSource:'TSE 2026',candidate:cand?{
    id:clean(cand.id,40),name:clean(cand.name,100),civilName:clean(cand.civilName,120),number:clean(cand.number,10),office:clean(cand.office,60),uf:clean(cand.uf,2),party:clean(cand.party,30),partyName:clean(cand.partyName,100),status:clean(cand.status,160),assetTotal:Number.isFinite(Number(cand.assetTotal))?Number(cand.assetTotal):null,assetCount:Number.isFinite(Number(cand.assetCount))?Number(cand.assetCount):null,occupation:clean(cand.occupation,100),education:clean(cand.education,100),birthDate:clean(cand.birthDate,20),federation:clean(cand.federation,120),coalition:clean(cand.coalition,180),reelection:clean(cand.reelection,30)
  }:null};
}
function extractText(data){
  if(typeof data?.output_text==='string'&&data.output_text.trim())return data.output_text.trim();
  const parts=[];
  for(const item of Array.isArray(data?.output)?data.output:[]){
    if(item?.type!=='message')continue;
    for(const c of Array.isArray(item.content)?item.content:[]){if((c?.type==='output_text'||c?.type==='text')&&c.text)parts.push(c.text)}
  }
  return parts.join('\n').trim();
}

export default async function handler(req,res){
  if(req.method!=='POST')return json(res,405,{ok:false,error:'METHOD_NOT_ALLOWED'});
  if(!process.env.OPENAI_API_KEY)return json(res,503,{ok:false,error:'OPENAI_NOT_CONFIGURED'});
  const body=req.body&&typeof req.body==='object'?req.body:{};
  if(body.needsAI!==true)return json(res,400,{ok:false,error:'AI_NOT_NEEDED',answer:'Use primeiro as respostas locais do Xis.'});
  const question=clean(body.question);
  if(!question)return json(res,400,{ok:false,error:'EMPTY_QUESTION'});

  const bearer=String(req.headers.authorization||'').replace(/^Bearer\s+/i,'').trim();
  let user;
  try{user=await verifyFirebase(bearer)}catch(e){return json(res,401,{ok:false,error:String(e.message||'AUTH_INVALID')})}

  const slot=consume(user.uid);
  if(!slot.ok){
    const answer=slot.kind==='hour'?'Você atingiu o limite de 10 análises por IA nesta hora. O Xis continua funcionando com dados oficiais, ajuda local e cache.':'Você atingiu o limite diário de 25 análises por IA. O Xis continua funcionando com dados oficiais, ajuda local e cache.';
    return json(res,429,{ok:false,error:'AI_RATE_LIMIT',answer,remaining:slot.remaining});
  }

  const context=compactContext(body.context);
  const system='Você é Xis, assistente neutro do aplicativo brasileiro RAIO-X Eleições 2026. Responda em português do Brasil, de modo claro e curto. Use somente os fatos presentes no contexto fornecido para afirmações sobre o candidato. Não invente fatos, processos, propostas, notícias, patrimônio, histórico ou posicionamentos. Quando o contexto não contiver a informação necessária, diga explicitamente que os dados disponíveis no app não bastam para afirmar. Nunca recomende em quem votar, nunca classifique candidato como melhor ou pior e não faça propaganda política. Diferencie fato oficial de explicação geral. A fonte de dados estruturados do candidato é TSE 2026. Responda em no máximo cerca de 120 palavras.';
  const prompt=`Pergunta do usuário: ${question}\n\nContexto do app: ${JSON.stringify(context)}`;
  try{
    const response=await fetch('https://api.openai.com/v1/responses',{
      method:'POST',
      headers:{'Content-Type':'application/json','Authorization':`Bearer ${process.env.OPENAI_API_KEY}`},
      body:JSON.stringify({model:MODEL,input:[{role:'system',content:system},{role:'user',content:prompt}],max_output_tokens:MAX_OUTPUT_TOKENS,store:false})
    });
    const data=await response.json().catch(()=>({}));
    if(!response.ok){rollback(user.uid);return json(res,502,{ok:false,error:'OPENAI_ERROR',detail:clean(data?.error?.message||response.status,300)})}
    const answer=extractText(data);
    if(!answer){rollback(user.uid);return json(res,502,{ok:false,error:'EMPTY_MODEL_RESPONSE'})}
    return json(res,200,{ok:true,answer:answer.slice(0,1400),model:MODEL,remaining:slot.remaining,usage:data.usage||null});
  }catch(e){
    rollback(user.uid);
    return json(res,502,{ok:false,error:'OPENAI_UNAVAILABLE',detail:clean(e?.message||e,240)});
  }
}
