import patch_v029
from pathlib import Path


def replace_once(path, old, new, label):
    p=Path(path)
    text=p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing v0.3.29 final target: {label} in {path}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')

# Expand verified first-round results with the published breakdowns.
replace_once(
    'AppV020.js',
    "results:[['Lula','PT',39],['Flavio Bolsonaro','PL',33],['Ronaldo Caiado','PSD',5],['Renan Santos','Missao',4],['Romeu Zema','Novo',3]]",
    "results:[['Lula','PT',39],['Flavio Bolsonaro','PL',33],['Ronaldo Caiado','PSD',5],['Renan Santos','Missao',4],['Romeu Zema','Novo',3],['Augusto Cury','Avante',2],['Branco/Nulo','',8],['Nao sabe','',3]]",
    'Datafolha full visible breakdown'
)
replace_once(
    'AppV020.js',
    "results:[['Lula','PT',38],['Flavio Bolsonaro','PL',31],['Renan Santos','Missao',4],['Ronaldo Caiado','PSD',4]]",
    "results:[['Lula','PT',38],['Flavio Bolsonaro','PL',31],['Renan Santos','Missao',4],['Ronaldo Caiado','PSD',4],['Augusto Cury','Avante',2],['Romeu Zema','Novo',2],['Samara Martins','UP',1],['Branco/Nulo','',8],['Indecisos','',10]]",
    'Quaest full visible breakdown'
)

# Bottom navigation order matching the approved mockup.
replace_once(
    'AppV020.js',
    "const items=[['Início','⌂'],['Busca','⌕'],['Pesquisas','▥'],['Raio-X','X'],['Comparar','⇄']];",
    "const items=[['Início','⌂'],['Busca','⌕'],['Raio-X','X'],['Comparar','⇄'],['Pesquisas','▥']];",
    'approved bottom nav order'
)

# Premium bars with large values and leader badge.
replace_once(
    'AppV020.js',
    "function PollBar({name,party,pct}){const s=useStyles();return <View style={{marginTop:10}}><View style={{flexDirection:'row',justifyContent:'space-between',gap:8}}><Text style={{color:s._text,fontWeight:'800',fontSize:12,flex:1}} numberOfLines={1}>{name}{party?` (${party})`:''}</Text><Text style={{color:s._blue,fontWeight:'900',fontSize:13}}>{pct}%</Text></View><View style={{height:7,borderRadius:4,backgroundColor:s._surface2,overflow:'hidden',marginTop:4}}><View style={{height:'100%',width:`${Math.min(100,pct*2)}%`,backgroundColor:s._blue,borderRadius:4}}/></View></View>}",
    "function PollBar({name,party,pct,leader=false}){const s=useStyles();const neutral=!party;return <View style={{marginTop:11,padding:leader?10:0,borderRadius:13,backgroundColor:leader?'rgba(30,126,245,.09)':'transparent',borderWidth:leader?1:0,borderColor:leader?s._blue:'transparent'}}><View style={{flexDirection:'row',alignItems:'center',gap:8}}><View style={{flex:1,minWidth:0}}><View style={{flexDirection:'row',alignItems:'center',gap:6}}><Text style={{color:s._text,fontWeight:leader?'900':'800',fontSize:12,flexShrink:1}} numberOfLines={1}>{name}</Text>{party?<View style={{paddingHorizontal:6,paddingVertical:2,borderRadius:7,backgroundColor:s._surface2}}><Text style={{color:s._muted,fontSize:8,fontWeight:'900'}}>{party}</Text></View>:null}{leader?<View style={{paddingHorizontal:7,paddingVertical:3,borderRadius:8,backgroundColor:s._blue}}><Text style={{color:'#fff',fontSize:8,fontWeight:'900'}}>LIDERA</Text></View>:null}</View><View style={{height:9,borderRadius:5,backgroundColor:'rgba(127,127,127,.16)',overflow:'hidden',marginTop:6}}><View style={{height:'100%',width:`${Math.min(100,pct*2.25)}%`,backgroundColor:neutral?'#617087':s._blue,borderRadius:5}}/></View></View><Text style={{color:neutral?s._text:s._blue,fontWeight:'900',fontSize:leader?20:15,minWidth:42,textAlign:'right'}}>{pct}%</Text></View></View>}",
    'premium poll bar'
)
replace_once(
    'AppV020.js',
    "{poll.results.map(([n,p,v])=><PollBar key={`${poll.id}-${n}`} name={n} party={p} pct={v}/>)}",
    "{poll.results.map(([n,p,v],i)=><PollBar key={`${poll.id}-${n}`} name={n} party={p} pct={v} leader={i===0}/>)}",
    'leader badge mapping'
)

# Add comparison card inspired by the approved preview.
anchor="function PollsScreen(){const s=useStyles();"
insert="""function PollComparison(){const s=useStyles();const df=POLL_SNAPSHOT.find(p=>p.institute==='Datafolha'),qu=POLL_SNAPSHOT.find(p=>p.institute==='Quaest');const top=['Lula','Flavio Bolsonaro'];const get=(poll,name)=>poll?.results.find(r=>r[0]===name)?.[2]||0;return <Card style={{padding:16}}><View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center'}}><View><Text style={{color:s._muted,fontSize:9,fontWeight:'900',letterSpacing:1}}>COMPARATIVO NACIONAL</Text><Text style={{color:s._text,fontSize:19,fontWeight:'900',marginTop:3}}>Datafolha × Quaest</Text></View><View style={{width:36,height:36,borderRadius:12,backgroundColor:s._surface2,alignItems:'center',justifyContent:'center'}}><Text style={{color:s._blue,fontSize:18,fontWeight:'900'}}>▥</Text></View></View>{top.map((name,idx)=>{const a=get(df,name),b=get(qu,name);return <View key={name} style={{marginTop:16,paddingTop:idx?14:0,borderTopWidth:idx?1:0,borderTopColor:s._border}}><View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center'}}><Text style={{color:s._text,fontSize:13,fontWeight:'900'}}>{name}</Text>{idx===0?<View style={{paddingHorizontal:7,paddingVertical:3,borderRadius:8,borderWidth:1,borderColor:s._blue}}><Text style={{color:s._blue,fontSize:8,fontWeight:'900'}}>LIDERA NAS DUAS</Text></View>:null}</View><View style={{flexDirection:'row',alignItems:'center',gap:8,marginTop:9}}><Text style={{color:s._muted,fontSize:9,width:58}}>Datafolha</Text><View style={{flex:1,height:10,borderRadius:6,backgroundColor:'rgba(127,127,127,.16)',overflow:'hidden'}}><View style={{height:'100%',width:`${Math.min(100,a*2.25)}%`,backgroundColor:s._blue,borderRadius:6}}/></View><Text style={{color:s._blue,fontSize:14,fontWeight:'900',width:38,textAlign:'right'}}>{a}%</Text></View><View style={{flexDirection:'row',alignItems:'center',gap:8,marginTop:6}}><Text style={{color:s._muted,fontSize:9,width:58}}>Quaest</Text><View style={{flex:1,height:10,borderRadius:6,backgroundColor:'rgba(127,127,127,.16)',overflow:'hidden'}}><View style={{height:'100%',width:`${Math.min(100,b*2.25)}%`,backgroundColor:s._blue,borderRadius:6,opacity:.68}}/></View><Text style={{color:s._blue,fontSize:14,fontWeight:'900',width:38,textAlign:'right'}}>{b}%</Text></View></View>})}<View style={{marginTop:14,paddingTop:11,borderTopWidth:1,borderTopColor:s._border}}><Text style={{color:s._muted,fontSize:9,lineHeight:14}}>Pesquisas com datas de campo diferentes. O comparativo é visual; os resultados não devem ser somados.</Text></View></Card>}
"""
p=Path('AppV020.js')
text=p.read_text(encoding='utf-8')
if anchor not in text: raise SystemExit('Missing PollsScreen anchor')
p.write_text(text.replace(anchor,insert+anchor,1),encoding='utf-8')

# Transform Xis reading card into the approved hero-style summary and place comparison below it.
replace_once(
    'AppV020.js',
    "<Card style={{backgroundColor:s._surface2}}><Text style={{color:s._text,fontWeight:'900',fontSize:14}}>Leitura do Xis</Text><Text style={s.cardSub}>Nas duas pesquisas nacionais carregadas, Lula aparece numericamente à frente de Flavio Bolsonaro. Compare sempre instituto, data e margem de erro; pesquisas diferentes não devem ser somadas.</Text></Card>{rows.map(p=><PollCard key={p.id} poll={p}/>)}",
    "<Card style={{backgroundColor:s._surface2,padding:14}}><View style={{flexDirection:'row',alignItems:'center',gap:12}}><XisOfficial height={92}/><View style={{flex:1}}><Text style={{color:s._text,fontWeight:'900',fontSize:18}}>Resumo do Xis</Text><Text style={[s.cardSub,{marginTop:6}]}>Nas pesquisas mais recentes carregadas, Lula aparece numericamente à frente de Flavio Bolsonaro. Compare sempre instituto, data e margem de erro.</Text></View></View></Card><PollComparison/>{rows.map(p=><PollCard key={p.id} poll={p}/>)}",
    'approved Xis summary and comparison'
)

# Make research cards more dashboard-like.
replace_once(
    'AppV020.js',
    "function PollCard({poll}){const s=useStyles();return <Card><View style={{flexDirection:'row',justifyContent:'space-between',gap:8}}><View><Text style={{color:s._blue,fontSize:11,fontWeight:'900'}}>{poll.institute.toUpperCase()}</Text><Text style={s.cardTitle}>Presidente - 1º turno</Text></View><Text style={s.sourceTag}>{poll.published}</Text></View><Text style={s.cardSub}>Campo: {poll.field} - {poll.sample.toLocaleString('pt-BR')} entrevistas - margem +/- {poll.margin} p.p.</Text>",
    "function PollCard({poll}){const s=useStyles();const badge=poll.institute==='Datafolha'?'D':'Q';return <Card style={{padding:16}}><View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center',gap:8}}><View style={{flexDirection:'row',alignItems:'center',gap:9}}><View style={{width:34,height:34,borderRadius:17,backgroundColor:s._blue,alignItems:'center',justifyContent:'center'}}><Text style={{color:'#fff',fontSize:17,fontWeight:'900'}}>{badge}</Text></View><View><Text style={{color:s._text,fontSize:17,fontWeight:'900'}}>{poll.institute}</Text><Text style={{color:s._muted,fontSize:9,marginTop:1}}>Presidente · 1º turno</Text></View></View><Text style={s.sourceTag}>{poll.published}</Text></View><View style={{marginTop:12,paddingVertical:10,borderTopWidth:1,borderBottomWidth:1,borderColor:s._border}}><Text style={{color:s._muted,fontSize:10,lineHeight:16}}>Campo: {poll.field}</Text><Text style={{color:s._muted,fontSize:10,lineHeight:16}}>Amostra: {poll.sample.toLocaleString('pt-BR')} · Margem: ±{poll.margin} p.p.</Text><Text style={{color:s._muted,fontSize:10,lineHeight:16}}>Registro TSE: {poll.registry}</Text></View>",
    'dashboard poll card header'
)

print('RAIO-X v0.3.29 final: approved premium Pesquisas UI + verified poll data applied')
