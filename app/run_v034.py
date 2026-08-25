from pathlib import Path

path=Path('patch_v034.py')
code=path.read_text(encoding='utf-8')
old='text=replace_once(text,"const items=[[\'Início\',\'⌂\'],[\'Busca\',\'⌕\'],[\'Pesquisas\',\'▥\'],[\'Raio-X\',\'X\'],[\'Comparar\',\'⇄\']];","const items=[[\'Início\',\'⌂\'],[\'Busca\',\'⌕\'],[\'Raio-X\',\'X\'],[\'Pesquisas\',\'▥\'],[\'Apuração\',\'◉\']];",\'bottom navigation\')'
new='''nav_start=text.find("function BottomNav(")\nnav_end=text.find("\\n\\nexport default function AppV020",nav_start)\nif nav_start<0 or nav_end<0: raise SystemExit("Missing BottomNav component")\nnav=r\'\'\'function BottomNav({tab,onGo}){const s=useStyles();const items=[[\'Início\',\'⌂\'],[\'Busca\',\'⌕\'],[\'Raio-X\',\'X\'],[\'Pesquisas\',\'▥\'],[\'Apuração\',\'◉\']];return <View style={s.bottomNav}>{items.map(([label,icon])=><TouchableOpacity key={label} style={s.navItem} onPress={()=>onGo(label)}><Text style={[s.navIcon,tab===label&&s.navActive]}>{icon}</Text><Text style={[s.navLabel,tab===label&&s.navActive]}>{label}</Text></TouchableOpacity>)}</View>}\'\'\'\ntext=text[:nav_start]+nav+text[nav_end:]'''
if old not in code:
    raise SystemExit('Unable to prepare v0.3.34 bottom-nav hotfix')
code=code.replace(old,new,1)
exec(compile(code,'patch_v034.py','exec'),{'__name__':'__main__'})
