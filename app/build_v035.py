from pathlib import Path

# Execute the consolidated v0.3.35 UI transform without the obsolete
# literal-string bottom-nav migration. The bottom nav is rebuilt structurally below.
path=Path('patch_v034.py')
code=path.read_text(encoding='utf-8')
start=code.find('# Primary navigation:')
end=code.find('# Home favorites shortcut remains functional.',start)
if start<0 or end<0:
    raise SystemExit('Missing legacy navigation section')
code=code[:start]+code[end:]
exec(compile(code,'patch_v034.py','exec'),{'__name__':'__main__'})

app=Path('AppV020.js')
text=app.read_text(encoding='utf-8')
nav_start=text.find('function BottomNav(')
nav_end=text.find('\n\nexport default function AppV020',nav_start)
if nav_start<0 or nav_end<0:
    raise SystemExit('Missing BottomNav component')
nav=r'''function BottomNav({tab,onGo}){
  const s=useStyles();
  const items=[['Início','⌂'],['Busca','⌕'],['Raio-X','X'],['Pesquisas','▥'],['Apuração','◉']];
  return <View style={s.bottomNav}>{items.map(([label,icon])=><TouchableOpacity key={label} style={s.navItem} onPress={()=>onGo(label)}><Text style={[s.navIcon,tab===label&&s.navActive]}>{icon}</Text><Text style={[s.navLabel,tab===label&&s.navActive]}>{label}</Text></TouchableOpacity>)}</View>
}'''
text=text[:nav_start]+nav+text[nav_end:]
app.write_text(text,encoding='utf-8')
print('RAIO-X v0.3.35 source finalized with structural BottomNav rebuild')
