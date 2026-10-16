"""Bir klasördeki görselleri sırayla Instagram hikâyesi olarak yayınlar (elle çalıştırılır).

Kullanım: python3 scripts/stories.py stories/one-cikan
Hikâyeler 24 saat görünür; kalıcı olmaları için uygulamada "Öne çıkanlar"a eklenir (API bunu yapamaz).
"""
import pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from publish import call, wait_ready, url_for, UID, ROOT

klasor = (ROOT / sys.argv[1]).resolve()
for f in sorted(p for p in klasor.iterdir() if p.suffix.lower() in ('.jpg', '.jpeg', '.png')):
    cid = call('POST', f'{UID}/media', media_type='STORIES', image_url=url_for(klasor, f.name))['id']
    wait_ready(cid)
    mid = call('POST', f'{UID}/media_publish', creation_id=cid).get('id')
    print(f'::notice::Hikâye yayınlandı: {f.name} -> {mid}')
    time.sleep(5)
