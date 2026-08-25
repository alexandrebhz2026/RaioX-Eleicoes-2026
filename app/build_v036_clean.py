from pathlib import Path
import patch_v033_favorites

# v0.3.36 intentionally starts from the stable v0.3.33 feature base.
# It does not execute the v0.3.34/v0.3.35 UI layers that caused overlapping modals.
code = Path('build_v036.py').read_text(encoding='utf-8')
code = code.replace('import patch_v034\n', '', 1)
code = code.replace(
    "text = replace_between(text, 'function PollComparison(', '\\nfunction LocationConsentModal(', comparison, 'PollComparison')",
    "# comparison replacement is combined below with the new dedicated location screens",
    1,
)
code = code.replace(
    "text = replace_between(text, 'function LocationConsentModal(', '\\nfunction PollsScreen(){', location_helpers, 'location screens')",
    "text = replace_between(text, 'function PollComparison(', '\\nfunction PollsScreen(){', comparison + '\\n\\n' + location_helpers, 'PollComparison + location screens')",
    1,
)
code = code.replace(
    "text = replace_once(text, \"const VERSION='0.3.35';\", \"const VERSION='0.3.36';\", 'visible version')",
    "text = replace_once(text, \"const VERSION='0.3.33';\", \"const VERSION='0.3.36';\", 'visible version')",
    1,
)
code = code.replace(
    "at = replace_once(at, \"const APP_VERSION='0.3.35';\", \"const APP_VERSION='0.3.36';\", 'AuthGate version')",
    "at = replace_once(at, \"const APP_VERSION='0.3.33';\", \"const APP_VERSION='0.3.36';\", 'AuthGate version')",
    1,
)
code = code.replace(
    "xt = replace_once(xt, \"'X-App-Version':'0.3.35'\", \"'X-App-Version':'0.3.36'\", 'Xis header version')",
    "xt = replace_once(xt, \"'X-App-Version':'0.3.33'\", \"'X-App-Version':'0.3.36'\", 'Xis header version')",
    1,
)
exec(compile(code, 'build_v036.py', 'exec'), {'__name__': '__main__'})

# Replace the entire bottom navigation structurally, independent of old text literals.
p = Path('AppV020.js')
text = p.read_text(encoding='utf-8')
nav_start = text.find('function BottomNav(')
nav_end = text.find('\n\nexport default function AppV020', nav_start)
if nav_start < 0 or nav_end < 0:
    raise SystemExit('Missing BottomNav component for v0.3.36')
nav = r'''function BottomNav({tab,onGo}){const s=useStyles();const items=[['Início','⌂'],['Busca','⌕'],['Raio-X','X'],['Pesquisas','▥'],['Apuração','◉']];return <View style={s.bottomNav}>{items.map(([label,icon])=><TouchableOpacity key={label} style={s.navItem} onPress={()=>onGo(label)}><Text style={[s.navIcon,tab===label&&s.navActive]}>{icon}</Text><Text style={[s.navLabel,tab===label&&s.navActive]}>{label}</Text></TouchableOpacity>)}</View>}'''
text = text[:nav_start] + nav + text[nav_end:]

# Keep the existing Favorites quick action functional without relying on an older UI patch.
if 'function Home({count,onRaioX,onSearch,onCompare})' in text:
    text = text.replace('function Home({count,onRaioX,onSearch,onCompare})', 'function Home({count,onRaioX,onSearch,onCompare,onFavorites})', 1)
if '<Quick icon="☆" label={\'Favoritos\'} onPress={()=>{}}/>' in text:
    text = text.replace('<Quick icon="☆" label={\'Favoritos\'} onPress={()=>{}}/>', '<Quick icon="☆" label={\'Favoritos\'} onPress={onFavorites}/>', 1)
text = text.replace(
    "<Home count={candidates.length} onRaioX={goRaioX} onSearch={()=>go('Busca')} onCompare={()=>go('Comparar')}/>",
    "<Home count={candidates.length} onRaioX={goRaioX} onSearch={()=>go('Busca')} onCompare={()=>go('Comparar')} onFavorites={()=>go('Favoritos')}/>",
)
p.write_text(text, encoding='utf-8')
print('RAIO-X v0.3.36 clean builder: stable v0.3.33 base + final Pesquisas UI')
