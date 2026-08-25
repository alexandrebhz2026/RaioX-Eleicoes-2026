import patch_v027
from pathlib import Path
import json


def replace_once(path, old, new, label):
    p=Path(path)
    text=p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Missing v0.3.28 target: {label} in {path}')
    p.write_text(text.replace(old,new,1),encoding='utf-8')

# Election-poll questions must stay inside Xis chat. Never interpret "pesquisa(s)" as candidate navigation.
replace_once(
    'XisEngine.js',
    "if(/RAIO|PROCUR|BUSC|PESQUIS|ABRIR|ABRA/.test(q)){",
    "if(/RAIO[- ]?X|ABRIR.*RAIO|ABRA.*RAIO|PROCUR(?:E|AR)?.*CANDIDAT|BUSC(?:A|AR)?.*CANDIDAT/.test(q)){",
    'restrict candidate navigation intent',
)

anchor="function localDecision(raw,{tab,selected}){\n  const q=norm(raw);\n  if(!q)return {type:'answer',text:'Escreva sua dúvida e eu tento resolver sem usar IA.'};"
replacement="function localDecision(raw,{tab,selected}){\n  const q=norm(raw);\n  if(!q)return {type:'answer',text:'Escreva sua dúvida e eu tento resolver sem usar IA.'};\n  if(/PESQUISAS? ELEITORAIS?|INTENCAO DE VOTO|INTENÇÃO DE VOTO|QUEM LIDERA|LIDERA AS PESQUISAS|CENARIO ELEITORAL|CENÁRIO ELEITORAL/.test(q))return {type:'answer',text:'Entendi: você está perguntando sobre pesquisa eleitoral, não pedindo para procurar um candidato. Esta versão do Xis ainda não consulta pesquisas de opinião atualizadas em tempo real. Por isso eu não vou inventar um líder nem jogar sua frase no Raio-X. Posso continuar a conversa normalmente e, numa próxima atualização, ligar uma fonte específica de pesquisas com instituto, data, amostra e cenário.',source:'local'};"
replace_once('XisEngine.js',anchor,replacement,'poll question stays in chat')

# Versioning.
replace_once('AppV020.js',"const VERSION='0.3.27';","const VERSION='0.3.28';",'visible app version')
replace_once('AuthGateV020.js',"const APP_VERSION='0.3.27';","const APP_VERSION='0.3.28';",'auth version')
replace_once('XisEngine.js',"'X-App-Version':'0.3.27'","'X-App-Version':'0.3.28'",'Xis API header')

app_path=Path('app.json')
app=json.loads(app_path.read_text(encoding='utf-8'))
expo=app['expo']
expo['version']='0.3.28'
expo['android']['versionCode']=32
expo.setdefault('extra',{})['xisIntent']='poll-question-chat-v028'
expo['extra']['release']='xis-intent-fix-v028'
app_path.write_text(json.dumps(app,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

pkg_path=Path('package.json')
pkg=json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version']='0.3.28'
pkg_path.write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

print('RAIO-X v0.3.28: election-poll questions remain inside Xis chat; candidate navigation requires explicit intent')
