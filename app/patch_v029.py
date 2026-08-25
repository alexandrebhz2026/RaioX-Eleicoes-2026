import patch_v028
from pathlib import Path
import json


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing v0.3.29 target: {label} in {path}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')

replace_once(
    'AppV020.js',
    "const TSE_DATASET='https://dadosabertos.tse.jus.br/dataset/candidatos-2026';",
    "const TSE_DATASET='https://dadosabertos.tse.jus.br/dataset/candidatos-2026';\nconst TSE_POLLS='https://dadosabertos.tse.jus.br/dataset/pesquisas-eleitorais-2026';\nconst POLL_SNAPSHOT=[{id:'df-br-2108',institute:'Datafolha',published:'21/08/2026',field:'18 a 19/08/2026',sample:2058,margin:2,registry:'BR-04496/2026',sourceUrl:'https://www1.folha.uol.com.br/poder/2026/08/datafolha-lula-marca-39-no-1o-turno-e-flavio-bolsonaro-tem-33.shtml',results:[['Lula','PT',39],['Flavio Bolsonaro','PL',33],['Ronaldo Caiado','PSD',5],['Renan Santos','Missao',4],['Romeu Zema','Novo',3]]},{id:'quaest-br-1408',institute:'Quaest',published:'14/08/2026',field:'10 a 13/08/2026',sample:2004,margin:2,registry:'BR-06773/2026',sourceUrl:'https://quaest.com.br/relatorios/pesquisa-de-intencao-de-voto-para-presidente-1ot-rodada-1-14-08-2026/',results:[['Lula','PT',38],['Flavio Bolsonaro','PL',31],['Renan Santos','Missao',4],['Ronaldo Caiado','PSD',4]]}];",
    'poll constants'
)

anchor = "function Settings({onLogout})"
insert = '''function PollBar({name,party,pct}){const s=useStyles();return <View style={{marginTop:10}}><View style={{flexDirection:'row',justifyContent:'space-between',gap:8}}><Text style={{color:s._text,fontWeight:'800',fontSize:12,flex:1}} numberOfLines={1}>{name}{party?` (${party})`:''}</Text><Text style={{color:s._blue,fontWeight:'900',fontSize:13}}>{pct}%</Text></View><View style={{height:7,borderRadius:4,backgroundColor:s._surface2,overflow:'hidden',marginTop:4}}><View style={{height:'100%',width:`${Math.min(100,pct*2)}%`,backgroundColor:s._blue,borderRadius:4}}/></View></View>}
function PollCard({poll}){const s=useStyles();return <Card><View style={{flexDirection:'row',justifyContent:'space-between',gap:8}}><View><Text style={{color:s._blue,fontSize:11,fontWeight:'900'}}>{poll.institute.toUpperCase()}</Text><Text style={s.cardTitle}>Presidente - 1º turno</Text></View><Text style={s.sourceTag}>{poll.published}</Text></View><Text style={s.cardSub}>Campo: {poll.field} - {poll.sample.toLocaleString('pt-BR')} entrevistas - margem +/- {poll.margin} p.p.</Text>{poll.results.map(([n,p,v])=><PollBar key={`${poll.id}-${n}`} name={n} party={p} pct={v}/>)}<Text style={{color:s._muted,fontSize:10,marginTop:12}}>Registro TSE: {poll.registry}</Text><View style={{flexDirection:'row',gap:8,marginTop:10}}><TouchableOpacity style={{flex:1,borderWidth:1,borderColor:s._blue,borderRadius:10,paddingVertical:9,alignItems:'center'}} onPress={()=>Linking.openURL(poll.sourceUrl)}><Text style={{color:s._blue,fontSize:10,fontWeight:'900'}}>ABRIR FONTE</Text></TouchableOpacity><TouchableOpacity style={{flex:1,borderWidth:1,borderColor:s._border,borderRadius:10,paddingVertical:9,alignItems:'center'}} onPress={()=>Linking.openURL(TSE_POLLS)}><Text style={{color:s._text,fontSize:10,fontWeight:'900'}}>VALIDAR NO TSE</Text></TouchableOpacity></View></Card>}
function PollsScreen(){const s=useStyles();const [office,setOffice]=useState('PRESIDENTE'),[uf,setUf]=useState('MG'),[source,setSource]=useState('Todas');const rows=POLL_SNAPSHOT.filter(p=>source==='Todas'||p.institute===source);return <ScrollView contentContainerStyle={s.content}><Text style={s.pageTitle}>Pesquisas</Text><Text style={s.pageSub}>Resultados publicados por institutos, com data, metodologia e registro para conferência no TSE.</Text><View style={{flexDirection:'row',gap:8}}><TouchableOpacity style={[s.pill,office==='PRESIDENTE'&&s.pillActive]} onPress={()=>setOffice('PRESIDENTE')}><Text style={[s.pillText,office==='PRESIDENTE'&&s.pillTextActive]}>Presidente</Text></TouchableOpacity><TouchableOpacity style={[s.pill,office==='GOVERNADOR'&&s.pillActive]} onPress={()=>setOffice('GOVERNADOR')}><Text style={[s.pillText,office==='GOVERNADOR'&&s.pillTextActive]}>Governador</Text></TouchableOpacity></View>{office==='GOVERNADOR'?<><TextInput value={uf} onChangeText={v=>setUf(v.toUpperCase().replace(/[^A-Z]/g,'').slice(0,2))} placeholder='UF' placeholderTextColor={s._muted} style={s.input}/><Card><Text style={s.cardTitle}>Governador - {uf||'UF'}</Text><Text style={s.cardSub}>A estrutura por estado está pronta. Nesta primeira carga da v0.3.29, Datafolha e Quaest foram ativadas para Presidente. As pesquisas estaduais serão adicionadas gradualmente com o mesmo padrão de validação.</Text></Card></>:<><ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{gap:8,paddingVertical:2}}>{['Todas','Datafolha','Quaest'].map(x=><TouchableOpacity key={x} style={[s.pill,source===x&&s.pillActive]} onPress={()=>setSource(x)}><Text style={[s.pillText,source===x&&s.pillTextActive]}>{x}</Text></TouchableOpacity>)}</ScrollView><Card style={{backgroundColor:s._surface2}}><Text style={{color:s._text,fontWeight:'900',fontSize:14}}>Leitura do Xis</Text><Text style={s.cardSub}>Nas duas pesquisas nacionais carregadas, Lula aparece numericamente à frente de Flavio Bolsonaro. Compare sempre instituto, data e margem de erro; pesquisas diferentes não devem ser somadas.</Text></Card>{rows.map(p=><PollCard key={p.id} poll={p}/>)}</>}<TouchableOpacity style={s.secondary} onPress={()=>Linking.openURL(TSE_POLLS)}><Text style={s.secondaryText}>ABRIR PESQUISAS ELEITORAIS NO TSE</Text></TouchableOpacity><Text style={{color:s._muted,fontSize:9,lineHeight:14,textAlign:'center'}}>Snapshot do app atualizado em 25/08/2026. Pesquisa é um retrato do momento, não previsão do resultado.</Text></ScrollView>}

'''
p = Path('AppV020.js')
text = p.read_text(encoding='utf-8')
if anchor not in text:
    raise SystemExit('Missing Settings anchor')
p.write_text(text.replace(anchor, insert + anchor, 1), encoding='utf-8')

replace_once('AppV020.js', "_blue:t.blue,_muted:t.muted,_surface2:t.surface2,_border:t.border,_danger:t.danger,", "_blue:t.blue,_muted:t.muted,_surface2:t.surface2,_border:t.border,_danger:t.danger,_text:t.text,", 'style helper')
replace_once('AppV020.js', '<DrawerItem icon="⇄" label="Comparar candidatos" onPress={()=>{onGo(\'Comparar\');onClose()}}/>', '<DrawerItem icon="▥" label="Pesquisas" onPress={()=>{onGo(\'Pesquisas\');onClose()}}/><DrawerItem icon="⇄" label="Comparar candidatos" onPress={()=>{onGo(\'Comparar\');onClose()}}/>', 'drawer polls')
replace_once('AppV020.js', "const items=[['Início','⌂'],['Busca','⌕'],['Raio-X','X'],['Comparar','⇄']];", "const items=[['Início','⌂'],['Busca','⌕'],['Pesquisas','▥'],['Raio-X','X'],['Comparar','⇄']];", 'bottom nav polls')
replace_once('AppV020.js', ":tab==='Comparar'?<Compare/>:tab==='Configurações'?<Settings onLogout={onLogout}/>", ":tab==='Pesquisas'?<PollsScreen/>:tab==='Comparar'?<Compare/>:tab==='Configurações'?<Settings onLogout={onLogout}/>", 'router polls')
replace_once('AppV020.js', "source==='limit'?'LIMITE DE IA':'XIS — LOCAL'", "source==='limit'?'LIMITE DE IA':source==='polls'?'PESQUISAS - FONTES VERIFICADAS':'XIS — LOCAL'", 'poll source label')

old_poll = "if(/PESQUISAS? ELEITORAIS?|INTENCAO DE VOTO|INTENÇÃO DE VOTO|QUEM LIDERA|LIDERA AS PESQUISAS|CENARIO ELEITORAL|CENÁRIO ELEITORAL/.test(q))return {type:'answer',text:'Entendi: você está perguntando sobre pesquisa eleitoral, não pedindo para procurar um candidato. Esta versão do Xis ainda não consulta pesquisas de opinião atualizadas em tempo real. Por isso eu não vou inventar um líder nem jogar sua frase no Raio-X. Posso continuar a conversa normalmente e, numa próxima atualização, ligar uma fonte específica de pesquisas com instituto, data, amostra e cenário.',source:'local'};"
new_poll = "if(/PESQUISAS? ELEITORAIS?|INTENCAO DE VOTO|INTENÇÃO DE VOTO|QUEM LIDERA|LIDERA AS PESQUISAS|CENARIO ELEITORAL|CENÁRIO ELEITORAL/.test(q)){if(/PRESIDENT/.test(q)||!/(GOVERNADOR|GOVERNO DO|GOVERNO DE)/.test(q))return {type:'answer',text:'Nas duas pesquisas nacionais carregadas no app, Lula aparece numericamente à frente de Flavio Bolsonaro: Datafolha publicada em 21/08 mostra 39% a 33% (margem +/-2 p.p.; registro BR-04496/2026) e Quaest publicada em 14/08 mostra 38% a 31% (margem +/-2 p.p.; registro BR-06773/2026). Sao pesquisas de datas diferentes e nao devem ser somadas. Confira os detalhes no menu Pesquisas.',source:'polls'};return {type:'answer',text:'Para governador, abra o menu Pesquisas e escolha a UF. A estrutura estadual ja esta pronta e as cargas por estado serao adicionadas com instituto, data, margem e registro TSE.',source:'polls'};}"
replace_once('XisEngine.js', old_poll, new_poll, 'Xis poll answer')

replace_once('AppV020.js', "const VERSION='0.3.28';", "const VERSION='0.3.29';", 'visible version')
replace_once('AuthGateV020.js', "const APP_VERSION='0.3.28';", "const APP_VERSION='0.3.29';", 'auth version')
replace_once('XisEngine.js', "'X-App-Version':'0.3.28'", "'X-App-Version':'0.3.29'", 'Xis API header')

app_path = Path('app.json')
app = json.loads(app_path.read_text(encoding='utf-8'))
expo = app['expo']
expo['version'] = '0.3.29'
expo['android']['versionCode'] = 33
expo.setdefault('extra', {})['polls'] = 'datafolha-quaest-tse-v029'
expo['extra']['release'] = 'polls-menu-v029'
app_path.write_text(json.dumps(app, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

pkg_path = Path('package.json')
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '0.3.29'
pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print('RAIO-X v0.3.29: Pesquisas menu + Datafolha/Quaest + TSE validation applied')
