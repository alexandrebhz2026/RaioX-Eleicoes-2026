import patch_v023_final
from pathlib import Path


def replace_once(path, old, new, label):
    p=Path(path); text=p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing v0.3.24 target: {label} in {path}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')

# Final dossier polish: age/assets are compact; patrimônio owns more horizontal space
# and is forced to one line with tabular numerals / automatic font fitting.
replace_once('AppV020.js',
    "<View style={s.metrics}><Metric label=\"IDADE\" value={age??'—'}/><Metric label=\"BENS\" value={candidate.assetCount??'—'}/><Metric label=\"PATRIMÔNIO\" value={candidate.assetTotal!=null?money(candidate.assetTotal):'—'} small/></View>",
    "<View style={s.metrics}><Metric label=\"IDADE\" value={age??'—'} compact/><Metric label=\"BENS\" value={candidate.assetCount??'—'} compact/><Metric label=\"PATRIMÔNIO\" value={candidate.assetTotal!=null?money(candidate.assetTotal):'—'} moneyValue/></View>",
    'compact age/assets and wide patrimonio')

replace_once('AppV020.js',
    "function Metric({label,value,small=false}){const s=useStyles();return <View style={s.metric}><Text style={s.metricLabel}>{label}</Text><Text style={[s.metricValue,small&&{fontSize:13}]} numberOfLines={2} adjustsFontSizeToFit>{String(value)}</Text></View>}",
    "function Metric({label,value,compact=false,moneyValue=false}){const s=useStyles();return <View style={[s.metric,compact&&s.metricCompact,moneyValue&&s.metricMoney]}><Text style={s.metricLabel}>{label}</Text><Text style={[s.metricValue,compact&&s.metricValueCompact,moneyValue&&s.metricValueMoney]} numberOfLines={1} adjustsFontSizeToFit minimumFontScale={.62}>{String(value)}</Text></View>}",
    'metric component formatting')

replace_once('AppV020.js',
    "metrics:{flexDirection:'row',gap:8},metric:{flex:1,minHeight:72,borderWidth:1,borderColor:t.border,backgroundColor:t.surface,borderRadius:14,padding:10,justifyContent:'space-between'},metricLabel:{color:t.muted,fontSize:9,fontWeight:'900'},metricValue:{color:t.text,fontSize:22,fontWeight:'900'},",
    "metrics:{flexDirection:'row',gap:8,alignItems:'stretch'},metric:{flex:1,minHeight:78,borderWidth:1,borderColor:t.border,backgroundColor:t.surface,borderRadius:14,paddingHorizontal:11,paddingVertical:10,justifyContent:'space-between'},metricCompact:{flex:.72},metricMoney:{flex:1.72},metricLabel:{color:t.muted,fontSize:9,fontWeight:'900',letterSpacing:.25},metricValue:{color:t.text,fontSize:21,fontWeight:'900',fontVariant:['tabular-nums']},metricValueCompact:{fontSize:18},metricValueMoney:{fontSize:20,letterSpacing:-.35},",
    'metric card proportions')

replace_once('AppV020.js', "const VERSION='0.3.23';", "const VERSION='0.3.24';", 'visible version')
replace_once('AuthGateV020.js', "const APP_VERSION='0.3.23';", "const APP_VERSION='0.3.24';", 'auth version')

print('RAIO-X v0.3.24 FINAL: dossier metric formatting and final visual polish applied')
