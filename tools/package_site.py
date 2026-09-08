#!/usr/bin/env python3
"""Assemble only public runtime files for static hosting; never publish tooling or tests."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'_site'
if out.exists():shutil.rmtree(out)
out.mkdir()
for name in ['index.html','airport.html','bayline.html','sitemap.xml','robots.txt','site-inventory.json','.nojekyll','LICENSE','CNAME']:
    p=root/name
    if p.exists():shutil.copy2(p,out/name)
for name in ['assets','worlds','guides','about','privacy','monitor','zh','tools/campaign-builder']:
    p=root/name
    if p.exists():shutil.copytree(p,out/name)
assert not (out/'.git').exists()
assert not (out/'site-config.json').exists()
assert not list(out.rglob('*.py'))
print('Packaged',len(list(out.rglob('*'))),'entries in _site')
