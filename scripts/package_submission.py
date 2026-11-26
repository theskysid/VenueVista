"""Create source-only and complete submission archives without caches or live data."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'submission';OUT.mkdir(exist_ok=True)
skip_dirs={'.git','.agents','.aws','.codex','node_modules','dist','.angular','target','data','__pycache__','rendered','screenshot-qa','tmp','report-qa'}
skip_files={'docker-build.log','preview-api.log'}
files=[]
for path in ROOT.rglob('*'):
    rel=path.relative_to(ROOT)
    if not path.is_file() or any(p in skip_dirs for p in rel.parts):continue
    if path.suffix=='.zip' or path.name in skip_files or path.name=='.env' or path.name.startswith('.~lock.'):continue
    if rel.parts[0]=='submission' and path.suffix not in {'.pdf','.docx'}:continue
    files.append(path)
for name,complete in [('VenueVista-Code.zip',False),('VenueVista-Submission.zip',True)]:
    with ZipFile(OUT/name,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for path in sorted(files):
            rel=path.relative_to(ROOT)
            if not complete and rel.parts[0] in {'submission','screenshots','verification'}:continue
            z.write(path,Path('VenueVista')/rel)
    with ZipFile(OUT/name) as z:assert z.testzip() is None
    print(name, (OUT/name).stat().st_size, 'bytes')
with (OUT/'SHA256SUMS.txt').open('w') as f:
    for path in sorted(OUT.iterdir()):
        if path.suffix in {'.zip','.pdf','.docx'}:f.write(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name+'\n')
