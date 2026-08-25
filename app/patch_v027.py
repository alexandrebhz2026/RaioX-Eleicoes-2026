import patch_v026
from pathlib import Path
import json


def replace_once(path, old, new, label):
    p=Path(path)
    text=p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing v0.3.27 target: {label} in {path}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')

# Use the exact full-body Xis image supplied by the user, preserving the whole portrait.
replace_once(
    'AppV020.js',
    "function XisOfficial({height=108}){return <Image source={require('./assets/xis-oficial-v026.webp')} style={{height,width:height*.8}} resizeMode=\"contain\"/>}",
    "function XisOfficial({height=108}){return <Image source={require('./assets/xis-oficial-full-v027.webp')} style={{height,width:height*.8}} resizeMode=\"contain\"/>}",
    'full body Xis asset',
)
replace_once(
    'AppV020.js',
    '<XisOfficial height={118}/>',
    '<XisOfficial height={150}/>',
    'larger Xis in voice stage',
)

# Larger, clearer voice button.
replace_once(
    'AppV020.js',
    "<Text style={[s.micText,recognizing&&s.micTextActive]}>{recognizing?'■':'●'}</Text><Text style={[s.micLabel,recognizing&&s.micTextActive]}>{recognizing?'PARAR':'FALAR'}</Text>",
    "<Text style={[s.micText,recognizing&&s.micTextActive]}>{recognizing?'■':'🎙️'}</Text><Text style={[s.micLabel,recognizing&&s.micTextActive]}>{recognizing?'PARAR':'FALAR'}</Text>",
    'microphone icon',
)
replace_once(
    'AppV020.js',
    "voiceStage:{margin:12,marginBottom:0,minHeight:132,borderRadius:20,borderWidth:1,borderColor:t.border,backgroundColor:t.surface,flexDirection:'row',alignItems:'center',paddingHorizontal:12,paddingVertical:7,gap:9},",
    "voiceStage:{margin:12,marginBottom:0,minHeight:174,borderRadius:22,borderWidth:1,borderColor:t.border,backgroundColor:t.surface,flexDirection:'row',alignItems:'center',paddingHorizontal:12,paddingVertical:9,gap:10},",
    'larger voice stage',
)
replace_once(
    'AppV020.js',
    "mic:{width:50,height:48,borderRadius:14,borderWidth:1,borderColor:t.blue,backgroundColor:t.surface,alignItems:'center',justifyContent:'center'},micActive:{backgroundColor:t.blue},micText:{color:t.blue,fontSize:11,fontWeight:'900'},micTextActive:{color:'#fff'},micLabel:{color:t.blue,fontSize:7,fontWeight:'900',marginTop:2},chatInput:{flex:1,height:48,borderRadius:14,borderWidth:1,borderColor:t.border,backgroundColor:t.input,color:t.text,paddingHorizontal:13},",
    "mic:{width:82,height:64,borderRadius:20,borderWidth:2,borderColor:t.blue,backgroundColor:t.surface,alignItems:'center',justifyContent:'center'},micActive:{backgroundColor:t.blue},micText:{color:t.blue,fontSize:21,fontWeight:'900',lineHeight:24},micTextActive:{color:'#fff'},micLabel:{color:t.blue,fontSize:10,fontWeight:'900',marginTop:2},chatInput:{flex:1,height:56,borderRadius:16,borderWidth:1,borderColor:t.border,backgroundColor:t.input,color:t.text,paddingHorizontal:13},",
    'larger microphone button',
)

# Candidate-list questions should be answered inside the Xis chat, not treated as navigation.
replace_once(
    'XisEngine.js',
    "import * as SecureStore from 'expo-secure-store';",
    "import * as SecureStore from 'expo-secure-store';\nimport candidates from './tse_candidates_2026.json';",
    'candidate dataset import',
)

anchor="function candidateIntent(raw,q){"
insert=r'''const STATE_NAME_TO_UF={
  'ACRE':'AC','ALAGOAS':'AL','AMAPA':'AP','AMAZONAS':'AM','BAHIA':'BA','CEARA':'CE','DISTRITO FEDERAL':'DF','ESPIRITO SANTO':'ES',
  'GOIAS':'GO','MARANHAO':'MA','MATO GROSSO':'MT','MATO GROSSO DO SUL':'MS','MINAS GERAIS':'MG','PARA':'PA','PARAIBA':'PB',
  'PARANA':'PR','PERNAMBUCO':'PE','PIAUI':'PI','RIO DE JANEIRO':'RJ','RIO GRANDE DO NORTE':'RN','RIO GRANDE DO SUL':'RS',
  'RONDONIA':'RO','RORAIMA':'RR','SANTA CATARINA':'SC','SAO PAULO':'SP','SERGIPE':'SE','TOCANTINS':'TO'
};
function parseUf(q=''){
  const m=q.match(/\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b/);
  if(m)return m[1];
  for(const [name,abbr] of Object.entries(STATE_NAME_TO_UF))if(q.includes(name))return abbr;
  return null;
}
function parseOffice(q=''){
  if(/PRESIDENTE/.test(q))return 'PRESIDENTE';
  if(/GOVERNADOR/.test(q))return 'GOVERNADOR';
  if(/SENADOR/.test(q))return 'SENADOR';
  if(/DEPUTAD[OA].*FEDERAL/.test(q))return 'DEPUTADO FEDERAL';
  if(/DEPUTAD[OA].*(ESTADUAL|ESTADO)/.test(q))return 'DEPUTADO ESTADUAL';
  if(/DEPUTAD[OA].*DISTRITAL/.test(q))return 'DEPUTADO DISTRITAL';
  return null;
}
function candidateListAnswer(raw){
  const q=norm(raw),office=parseOffice(q),uf=parseUf(q);
  const isQuestion=/(QUAIS|LISTE|LISTAR|MOSTRE|QUEM SAO|QUEM SÃO|QUEM ESTAO|QUEM ESTÃO|TODOS)/.test(q)&&/(CANDIDAT|CONCORR|DISPUT)/.test(q);
  if(!office||!isQuestion)return null;
  if(office!=='PRESIDENTE'&&!uf)return {type:'answer',text:'Posso listar. Diga também o estado ou a UF, por exemplo: “quais são os candidatos a governador de MG?”',source:'local'};
  const list=candidates.filter(c=>norm(c.office)===office).filter(c=>office==='PRESIDENTE'||norm(c.uf)===uf).sort((a,b)=>String(a.name||'').localeCompare(String(b.name||''),'pt-BR'));
  if(!list.length)return {type:'answer',text:`Não encontrei candidatos para ${office.toLowerCase()}${office==='PRESIDENTE'?'':` em ${uf}`} nesta carga oficial do TSE.`,source:'tse'};
  const shown=list.slice(0,18);
  const lines=shown.map((c,i)=>`${i+1}. ${c.name||'Nome não informado'}${c.party?` — ${c.party}`:''}${c.number?` — nº ${c.number}`:''}`);
  const tail=list.length>shown.length?`\n\nHá mais ${list.length-shown.length} registro(s). Posso abrir a busca completa se você quiser.`:'\n\nSe quiser, posso fazer o Raio-X de qualquer um deles.';
  return {type:'answer',text:`Na base oficial do TSE encontrei ${list.length} candidato${list.length===1?'':'s'} a ${office.toLowerCase()}${office==='PRESIDENTE'?'':` em ${uf}`}:\n\n${lines.join('\n')}${tail}`,source:'tse'};
}

'''
p=Path('XisEngine.js'); text=p.read_text(encoding='utf-8')
if anchor not in text: raise SystemExit('Missing candidateIntent anchor')
p.write_text(text.replace(anchor,insert+anchor,1),encoding='utf-8')

replace_once(
    'XisEngine.js',
    "if(/RAIO|CANDIDAT|QUEM E|QUEM É|PROCUR|BUSC/.test(q)){",
    "if(/RAIO|PROCUR|BUSC|PESQUIS|ABRIR|ABRA/.test(q)){",
    'only explicit navigation should open Raio-X',
)
replace_once(
    'XisEngine.js',
    "if(!q)return {type:'answer',text:'Escreva sua dúvida e eu tento resolver sem usar IA.'};\n  if(/COMPAR/.test(q))",
    "if(!q)return {type:'answer',text:'Escreva sua dúvida e eu tento resolver sem usar IA.'};\n  const listAnswer=candidateListAnswer(raw);if(listAnswer)return listAnswer;\n  if(/COMPAR/.test(q))",
    'candidate list answer priority',
)
replace_once(
    'XisEngine.js',
    "if(/BUSCA POR CARGO|LISTAR|ESCOLHER CARGO|PESQUISA POR CARGO/.test(q))",
    "if(/BUSCA POR CARGO|ESCOLHER CARGO|PESQUISA POR CARGO/.test(q))",
    'do not navigate just because user said listar',
)

# Versioning.
replace_once('AppV020.js', "const VERSION='0.3.26';", "const VERSION='0.3.27';", 'visible app version')
replace_once('AuthGateV020.js', "const APP_VERSION='0.3.26';", "const APP_VERSION='0.3.27';", 'auth version')
replace_once('XisEngine.js', "'X-App-Version':'0.3.26'", "'X-App-Version':'0.3.27'", 'Xis API header')

app_path=Path('app.json'); app=json.loads(app_path.read_text(encoding='utf-8')); expo=app['expo']; expo['version']='0.3.27'; expo['android']['versionCode']=31; expo.setdefault('extra',{})['xisVisual']='official-full-body-exact-v027'; expo['extra']['xisVoice']='chat-answer-first-v027'; expo['extra']['release']='xis-voice-fix-v027'; app_path.write_text(json.dumps(app,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pkg_path=Path('package.json'); pkg=json.loads(pkg_path.read_text(encoding='utf-8')); pkg['version']='0.3.27'; pkg_path.write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
asset=Path('assets/xis-oficial-full-v027.webp')
if not asset.exists() or asset.stat().st_size<12000: raise SystemExit('Exact full-body Xis v0.3.27 asset missing')
print('RAIO-X v0.3.27: voice answer stays in chat + exact full-body Xis + larger talk button')
