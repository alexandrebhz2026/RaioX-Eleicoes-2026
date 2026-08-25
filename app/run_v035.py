from pathlib import Path

path=Path('patch_v035.py')
code=path.read_text(encoding='utf-8')
old='import patch_v034\n'
new='import run_v034\n'
if old not in code:
    raise SystemExit('Unable to prepare v0.3.35 patch chain')
code=code.replace(old,new,1)
exec(compile(code,'patch_v035.py','exec'),{'__name__':'__main__'})
