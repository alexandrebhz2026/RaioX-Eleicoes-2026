import * as SecureStore from 'expo-secure-store';

// Hotfix v0.3.16: this module must be safe to load on Android/Hermes.
// Do not import google-services.json here. The Firebase Web API key is a public
// client configuration value and is intentionally the same one already used by AuthGate.
const FIREBASE_API_KEY='AIzaSyAmnbDT48iQW8SpxUZyTQh__HwM0yWgOwY';
const XIS_API='https://raiox-xis-ai.vercel.app/api/xis';
const HOURLY_LIMIT=10;
const DAILY_LIMIT=25;
const CACHE_MAX=12;
const SESSION_KEY='raiox.auth.session.v1';
const USAGE_PREFIX='raiox.xis.ai.usage.v1.';
const CACHE_INDEX_PREFIX='raiox.xis.ai.cache.index.v1.';
const CACHE_PREFIX='raiox.xis.ai.cache.v1.';

function norm(value=''){
  try{return String(value).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().replace(/\s+/g,' ').trim()}
  catch{return String(value).toUpperCase().replace(/\s+/g,' ').trim()}
}
function money(value){
  const n=Number(value);
  try{return Number.isFinite(n)?n.toLocaleString('pt-BR',{style:'currency',currency:'BRL'}):'não informado'}
  catch{return Number.isFinite(n)?`R$ ${n.toFixed(2)}`:'não informado'}
}
function dayKey(d=new Date()){
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}
function hash(text=''){
  let h=5381;
  for(let i=0;i<text.length;i++)h=((h<<5)+h)^text.charCodeAt(i);
  return (h>>>0).toString(36);
}
async function readJson(key,fallback){
  try{const raw=await SecureStore.getItemAsync(key);return raw?JSON.parse(raw):fallback}catch{return fallback}
}
async function writeJson(key,value){
  try{await SecureStore.setItemAsync(key,JSON.stringify(value));return true}catch{return false}
}
function userKey(session){return String(session?.uid||session?.email||'anonymous').replace(/[^a-zA-Z0-9_.@-]/g,'_').slice(0,120)}

async function ensureFreshSession(session){
  if(!session)return null;
  if(session.idToken&&session.expiresAt&&session.expiresAt>Date.now()+120000)return session;
  if(!session.refreshToken)return session;
  try{
    const body=`grant_type=refresh_token&refresh_token=${encodeURIComponent(session.refreshToken)}`;
    const response=await fetch(`https://securetoken.googleapis.com/v1/token?key=${FIREBASE_API_KEY}`,{
      method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body
    });
    const data=await response.json().catch(()=>({}));
    if(!response.ok||!data.id_token)return session;
    const next={...session,idToken:data.id_token,refreshToken:data.refresh_token||session.refreshToken,expiresAt:Date.now()+Math.max(300,Number(data.expires_in||3600)-60)*1000,uid:data.user_id||session.uid};
    await SecureStore.setItemAsync(SESSION_KEY,JSON.stringify(next));
    return next;
  }catch{return session}
}

export function xisContextHelp(tab,selected){
  if(tab==='Início')return 'Aqui eu posso abrir um Raio-X, levar você à busca por cargo ou explicar como o app funciona.';
  if(tab==='Busca')return 'Aqui você escolhe cargo e UF para navegar pela lista oficial do TSE. Se quiser investigar uma pessoa específica, peça um Raio-X pelo nome ou número.';
  if(tab==='Raio-X'&&selected)return `Você está no Raio-X de ${selected.name}. Posso explicar os dados desta ficha, procurar outro candidato ou levar você para a comparação.`;
  if(tab==='Raio-X')return 'Digite o nome, parte do nome ou o número do candidato. Eu procuro na base oficial e abro o Raio-X.';
  if(tab==='Comparar')return 'Aqui você compara candidatos lado a lado. Eu posso explicar qualquer campo sem dizer quem é melhor ou pior.';
  return 'Pode me perguntar como usar o app, pedir um Raio-X ou tirar dúvidas sobre os dados eleitorais.';
}

function selectedFact(q,c){
  if(!c)return null;
  const name=c.name||'este candidato';
  if(/PARTIDO|SIGLA/.test(q))return `${name} está registrado por ${c.party||'partido não informado'}${c.partyName?` — ${c.partyName}`:''}.`;
  if(/NUMERO|NÚMERO/.test(q))return `O número eleitoral de ${name} é ${c.number||'não informado'}.`;
  if(/CARGO/.test(q))return `${name} concorre ao cargo de ${c.office||'cargo não informado'}${c.uf?` em ${c.uf}`:''}.`;
  if(/PATRIMON|BENS|DINHEIRO|DECLAR/.test(q))return `O patrimônio declarado nesta carga oficial para ${name} é ${money(c.assetTotal)}${Number.isFinite(Number(c.assetCount))?`, distribuído em ${Number(c.assetCount)} bem(ns) declarado(s)`:''}. Patrimônio declarado é o valor informado pelo próprio candidato à Justiça Eleitoral e não é uma avaliação do patrimônio atual.`;
  if(/SITUAC|REGISTRO|CANDIDATURA/.test(q))return `A situação exibida para ${name} é: ${c.status||'sem descrição pública nesta carga do TSE'}.`;
  if(/REELEI/.test(q))return `No registro atual, o campo de reeleição de ${name} está como ${c.reelection||'não informado'}.`;
  if(/FEDERAC/.test(q))return `Federação informada para ${name}: ${c.federation||'não informada nesta carga'}.`;
  if(/COLIGAC/.test(q))return `Coligação informada para ${name}: ${c.coalition||'não informada nesta carga'}.`;
  if(/OCUPAC|PROFISS/.test(q))return `Ocupação declarada por ${name}: ${c.occupation||'não informada'}.`;
  if(/ESCOLAR|INSTRU|FORMAC/.test(q))return `Grau de instrução declarado por ${name}: ${c.education||'não informado'}.`;
  if(/NASC|IDADE/.test(q))return `${name} informou nascimento em ${c.birthDate||'data não informada'}${c.birthCity?`, em ${c.birthCity}${c.birthUf?`/${c.birthUf}`:''}`:''}.`;
  return null;
}

function glossary(q){
  if(/PATRIMONIO DECLARADO|PATRIMÔNIO DECLARADO/.test(q))return 'Patrimônio declarado é a soma dos bens e valores que o candidato informa à Justiça Eleitoral no registro da candidatura. O RAIO-X mostra esses dados como declaração oficial, sem presumir que representem o valor de mercado atual.';
  if(/FEDERACAO|FEDERAÇÃO/.test(q))return 'Federação partidária é uma união formal de partidos que atua de maneira conjunta pelo período definido em lei. No RAIO-X, o campo é mostrado conforme o registro oficial.';
  if(/COLIGACAO|COLIGAÇÃO/.test(q))return 'Coligação é a composição eleitoral registrada para uma disputa majoritária quando aplicável. O RAIO-X exibe a informação oficial sem interpretar se ela é positiva ou negativa.';
  if(/TSE|TRIBUNAL SUPERIOR ELEITORAL/.test(q))return 'TSE é o Tribunal Superior Eleitoral. A base principal do RAIO-X usa dados públicos oficiais do TSE para identificação, candidatura, chapa, patrimônio e outros campos eleitorais.';
  if(/PRIMEIRO TURNO|1 TURNO/.test(q))return 'O primeiro turno das Eleições 2026 está marcado para 4 de outubro de 2026. Onde houver segundo turno para presidente ou governador, ele será em 25 de outubro de 2026.';
  if(/ORDEM.*VOT|URNA/.test(q))return 'Em 2026, a ordem de votação é: deputado federal, deputado estadual ou distrital, senador 1, senador 2, governador e presidente.';
  if(/QUAIS CARGOS|CARGOS.*2026/.test(q))return 'Nas Eleições 2026 serão escolhidos presidente e vice, governadores e vices, dois senadores por estado/DF, deputados federais e deputados estaduais ou distritais.';
  return null;
}

function candidateIntent(raw,q){
  const cleaned=raw.replace(/^(FAÇA|FACA|ABRA|QUERO|MOSTRE|ME MOSTRE|RAIO[- ]?X|RAIO X|DO|DA|DE)+\s*/i,'').trim();
  const digits=cleaned.match(/\b\d{2,5}\b/);
  if(/RAIO|CANDIDAT|QUEM E|QUEM É|PROCUR|BUSC/.test(q)){
    if(digits)return digits[0];
    const words=cleaned.replace(/\b(CANDIDATO|CANDIDATA|QUEM|É|E|O|A|DO|DA|DE|RAIO|X)\b/gi,' ').replace(/\s+/g,' ').trim();
    if(words.length>=3)return words;
  }
  return null;
}

function localDecision(raw,{tab,selected}){
  const q=norm(raw);
  if(!q)return {type:'answer',text:'Escreva sua dúvida e eu tento resolver sem usar IA.'};
  if(/COMPAR/.test(q))return {type:'action',action:'compare',text:'Abrindo a comparação.'};
  if(/BUSCA POR CARGO|LISTAR|ESCOLHER CARGO|PESQUISA POR CARGO/.test(q))return {type:'action',action:'search',text:'Abrindo a busca por cargo.'};
  if(/COMO.*(USA|USAR)|AJUDA|ESSA TELA|ESTA TELA|O QUE POSSO FAZER/.test(q))return {type:'answer',text:xisContextHelp(tab,selected),source:'local'};
  const fact=selectedFact(q,selected);if(fact)return {type:'answer',text:fact,source:'tse'};
  const gloss=glossary(q);if(gloss)return {type:'answer',text:gloss,source:'local'};
  const candidateQuery=candidateIntent(raw,q);if(candidateQuery)return {type:'action',action:'raiox',query:candidateQuery,text:'Abrindo o Raio-X.'};
  return null;
}

function contextForAi(tab,selected){
  const c=selected?{
    id:String(selected.id||''),name:selected.name||'',civilName:selected.civilName||'',number:String(selected.number||''),office:selected.office||'',uf:selected.uf||'',
    party:selected.party||'',partyName:selected.partyName||'',status:selected.status||'',assetTotal:Number.isFinite(Number(selected.assetTotal))?Number(selected.assetTotal):null,
    assetCount:Number.isFinite(Number(selected.assetCount))?Number(selected.assetCount):null,occupation:selected.occupation||'',education:selected.education||'',
    birthDate:selected.birthDate||'',federation:selected.federation||'',coalition:selected.coalition||'',reelection:selected.reelection||''
  }:null;
  return {screen:tab,candidate:c,dataSource:'TSE 2026',policy:'neutral factual assistant; never tell user who to vote for'};
}

async function cacheGet(session,raw,selected){
  const u=userKey(session),key=hash(`${norm(raw)}|${selected?.id||''}`);
  const value=await readJson(`${CACHE_PREFIX}${u}.${key}`,null);
  if(!value||!value.text)return null;
  return {...value,source:'cache'};
}
async function cachePut(session,raw,selected,value){
  const u=userKey(session),key=hash(`${norm(raw)}|${selected?.id||''}`),storageKey=`${CACHE_PREFIX}${u}.${key}`;
  await writeJson(storageKey,{text:String(value.text||'').slice(0,1800),at:Date.now(),model:value.model||''});
  const indexKey=`${CACHE_INDEX_PREFIX}${u}`;
  let index=await readJson(indexKey,[]);
  index=[storageKey,...index.filter(x=>x!==storageKey)].slice(0,CACHE_MAX);
  await writeJson(indexKey,index);
}
async function usageStatus(session){
  const u=userKey(session),key=`${USAGE_PREFIX}${u}`,now=Date.now(),hourAgo=now-3600000,today=dayKey();
  const st=await readJson(key,{events:[]});
  const events=(Array.isArray(st.events)?st.events:[]).filter(t=>Number(t)>now-86400000);
  const hourCount=events.filter(t=>Number(t)>=hourAgo).length,dayCount=events.filter(t=>dayKey(new Date(Number(t)))===today).length;
  return {key,events,hourCount,dayCount,hourRemaining:Math.max(0,HOURLY_LIMIT-hourCount),dayRemaining:Math.max(0,DAILY_LIMIT-dayCount)};
}
async function markAiUse(status){await writeJson(status.key,{events:[...status.events,Date.now()].slice(-DAILY_LIMIT-5)})}

export async function askXis(raw,{tab,selected,session}){
  const local=localDecision(raw,{tab,selected});
  if(local)return local;
  const cached=await cacheGet(session,raw,selected);
  if(cached)return {type:'answer',text:cached.text,source:'cache',model:cached.model||''};

  const activeSession=await ensureFreshSession(session);
  if(!activeSession?.uid||!activeSession?.idToken)return {type:'answer',text:'Eu consigo continuar ajudando com os dados do app, mas a análise aprofundada por IA exige uma sessão autenticada.',source:'local'};

  const usage=await usageStatus(activeSession);
  if(usage.hourCount>=HOURLY_LIMIT)return {type:'answer',text:'Você atingiu o limite de 10 análises por IA nesta hora. Eu continuo funcionando normalmente com dados oficiais, ajuda local e respostas em cache. A cota de IA renova automaticamente.',source:'limit',remaining:{hour:0,day:usage.dayRemaining}};
  if(usage.dayCount>=DAILY_LIMIT)return {type:'answer',text:'Você atingiu o limite diário de 25 análises por IA. O Xis continua funcionando com TSE, ajuda local e cache; novas análises por IA ficam disponíveis no próximo dia.',source:'limit',remaining:{hour:usage.hourRemaining,day:0}};

  try{
    const response=await fetch(XIS_API,{
      method:'POST',
      headers:{'Content-Type':'application/json','Authorization':`Bearer ${activeSession.idToken}`,'X-App-Version':'0.3.16'},
      body:JSON.stringify({needsAI:true,question:String(raw).slice(0,1200),context:contextForAi(tab,selected),limits:{hourly:HOURLY_LIMIT,daily:DAILY_LIMIT}})
    });
    const data=await response.json().catch(()=>({}));
    if(response.status===429)return {type:'answer',text:data.answer||'A cota de análise por IA foi atingida. Eu continuo disponível com os dados do app e respostas locais.',source:'limit',remaining:data.remaining||null};
    if(!response.ok||!data.ok||!data.answer)throw new Error(data.error||`HTTP ${response.status}`);
    await markAiUse(usage);
    await cachePut(activeSession,raw,selected,{text:data.answer,model:data.model||'gpt-5.4-nano'});
    return {type:'answer',text:String(data.answer).slice(0,1800),source:'ai',model:data.model||'gpt-5.4-nano',remaining:data.remaining||{hour:usage.hourRemaining-1,day:usage.dayRemaining-1}};
  }catch(e){
    console.warn('Xis AI fallback unavailable',e?.message||e);
    return {type:'answer',text:'Não consegui usar a análise aprofundada agora. Posso continuar ajudando com tudo que está na base oficial do app, sem gastar IA.',source:'local-unavailable'};
  }
}

export const XIS_LIMITS={hourly:HOURLY_LIMIT,daily:DAILY_LIMIT};
