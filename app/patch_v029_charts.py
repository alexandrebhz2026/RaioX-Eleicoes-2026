from pathlib import Path


def replace_once(path, old, new, label):
    p=Path(path)
    text=p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing charts target: {label} in {path}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')

# Replace the simple poll bar with a more premium, card-like chart row.
replace_once(
    'AppV020.js',
    "function PollBar({name,party,pct}){const s=useStyles();return <View style={{marginTop:10}}><View style={{flexDirection:'row',justifyContent:'space-between',gap:8}}><Text style={{color:s._text,fontWeight:'800',fontSize:12,flex:1}} numberOfLines={1}>{name}{party?` (${party})`:''}</Text><Text style={{color:s._blue,fontWeight:'900',fontSize:13}}>{pct}%</Text></View><View style={{height:7,borderRadius:4,backgroundColor:s._surface2,overflow:'hidden',marginTop:4}}><View style={{height:'100%',width:`${Math.min(100,pct*2)}%`,backgroundColor:s._blue,borderRadius:4}}/></View></View>}",
    "function PollBar({name,party,pct,leader=false}){const s=useStyles();return <View style={{marginTop:12,padding:12,borderRadius:14,backgroundColor:leader?'rgba(24,119,242,.10)':s._surface2,borderWidth:leader?1:0,borderColor:leader?s._blue:'transparent'}}><View style={{flexDirection:'row',alignItems:'center',gap:8}}><View style={{flex:1}}><View style={{flexDirection:'row',alignItems:'center',gap:6}}><Text style={{color:s._text,fontWeight:'900',fontSize:13,flexShrink:1}} numberOfLines={1}>{name}</Text>{party?<View style={{paddingHorizontal:6,paddingVertical:2,borderRadius:7,backgroundColor:s._surface2}}><Text style={{color:s._muted,fontSize:9,fontWeight:'900'}}>{party}</Text></View>:null}{leader?<View style={{paddingHorizontal:7,paddingVertical:3,borderRadius:8,backgroundColor:s._blue}}><Text style={{color:'#fff',fontSize:8,fontWeight:'900'}}>LIDERA</Text></View>:null}</View><View style={{height:10,borderRadius:6,backgroundColor:'rgba(127,127,127,.18)',overflow:'hidden',marginTop:8}}><View style={{height:'100%',width:`${Math.min(100,pct*2.2)}%`,backgroundColor:s._blue,borderRadius:6}}/></View></View><Text style={{color:s._blue,fontWeight:'900',fontSize:22,minWidth:48,textAlign:'right'}}>{pct}%</Text></View></View>}",
    'premium poll bars'
)

replace_once(
    'AppV020.js',
    "{poll.results.map(([n,p,v])=><PollBar key={`${poll.id}-${n}`} name={n} party={p} pct={v}/>)}",
    "{poll.results.map(([n,p,v],i)=><PollBar key={`${poll.id}-${n}`} name={n} party={p} pct={v} leader={i===0}/>)}",
    'leader highlight'
)

# Add a modern comparison panel between the two national polls.
anchor="function PollsScreen(){const s=useStyles();"
insert="""function PollComparison(){const s=useStyles();const df=POLL_SNAPSHOT.find(p=>p.institute==='Datafolha'),qu=POLL_SNAPSHOT.find(p=>p.institute==='Quaest');const names=['Lula','Flavio Bolsonaro'];const get=(poll,name)=>poll?.results.find(r=>r[0]===name)?.[2]||0;return <Card style={{padding:16}}><View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center'}}><View><Text style={{color:s._muted,fontSize:10,fontWeight:'900',letterSpacing:.8}}>COMPARATIVO NACIONAL</Text><Text style={{color:s._text,fontSize:18,fontWeight:'900',marginTop:2}}>Datafolha × Quaest</Text></View><View style={{paddingHorizontal:9,paddingVertical:5,borderRadius:10,backgroundColor:s._surface2}}><Text style={{color:s._blue,fontSize:9,fontWeight:'900'}}>1º TURNO</Text></View></View>{names.map(name=>{const a=get(df,name),b=get(qu,name);return <View key={name} style={{marginTop:16}}><Text style={{color:s._text,fontSize:12,fontWeight:'900',marginBottom:7}}>{name}</Text><View style={{flexDirection:'row',alignItems:'center',gap:8}}><Text style={{color:s._muted,fontSize:9,width:55}}>Datafolha</Text><View style={{flex:1,height:9,borderRadius:6,backgroundColor:'rgba(127,127,127,.16)',overflow:'hidden'}}><View style={{height:'100%',width:`${Math.min(100,a*2.2)}%`,backgroundColor:s._blue,borderRadius:6}}/></View><Text style={{color:s._text,fontSize:12,fontWeight:'900',width:34,textAlign:'right'}}>{a}%</Text></View><View style={{flexDirection:'row',alignItems:'center',gap:8,marginTop:5}}><Text style={{color:s._muted,fontSize:9,width:55}}>Quaest</Text><View style={{flex:1,height:9,borderRadius:6,backgroundColor:'rgba(127,127,127,.16)',overflow:'hidden'}}><View style={{height:'100%',width:`${Math.min(100,b*2.2)}%`,backgroundColor:s._blue,borderRadius:6,opacity:.65}}/></View><Text style={{color:s._text,fontSize:12,fontWeight:'900',width:34,textAlign:'right'}}>{b}%</Text></View></View>})}<Text style={{color:s._muted,fontSize:9,lineHeight:14,marginTop:14}}>Comparação visual apenas. As pesquisas têm datas de campo diferentes e não devem ser somadas.</Text></Card>}
"""
p=Path('AppV020.js'); text=p.read_text(encoding='utf-8')
if anchor not in text: raise SystemExit('Missing PollsScreen anchor')
p.write_text(text.replace(anchor,insert+anchor,1),encoding='utf-8')

replace_once(
    'AppV020.js',
    "<Card style={{backgroundColor:s._surface2}}><Text style={{color:s._text,fontWeight:'900',fontSize:14}}>Leitura do Xis</Text><Text style={s.cardSub}>Nas duas pesquisas nacionais carregadas, Lula aparece numericamente à frente de Flavio Bolsonaro. Compare sempre instituto, data e margem de erro; pesquisas diferentes não devem ser somadas.</Text></Card>{rows.map(p=><PollCard key={p.id} poll={p}/>)}",
    "<Card style={{backgroundColor:s._surface2}}><Text style={{color:s._text,fontWeight:'900',fontSize:14}}>Leitura do Xis</Text><Text style={s.cardSub}>Nas duas pesquisas nacionais carregadas, Lula aparece numericamente à frente de Flavio Bolsonaro. Compare sempre instituto, data e margem de erro; pesquisas diferentes não devem ser somadas.</Text></Card><PollComparison/>{rows.map(p=><PollCard key={p.id} poll={p}/>)}",
    'comparison panel placement'
)

print('RAIO-X v0.3.29 charts: premium poll bars + comparison panel applied')
