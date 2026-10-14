"""Publish the next due post from queue/ to Instagram (Instagram API with Instagram Login).

queue/<NNN>-<slug>/post.json:
  {"date": "2026-10-15", "type": "image" | "carousel" | "reel",
   "files": ["1.jpg", ...], "caption": "...", "cover": "kapak.jpg" (reel only, optional)}

A post is due when its date is today or earlier (Europe/Istanbul). One post per run.
After publishing, the folder is moved to posted/ by the workflow (see publish.yml).

Env: IG_TOKEN (required), IG_USER_ID (default "me"), MEDIA_BASE_URL (public URL of the repo
root, e.g. GitHub Pages), IG_API_VERSION (optional, e.g. "v23.0"), DRY_RUN=1 to only print.
"""
import datetime as dt, json, os, pathlib, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / 'queue'
def _pick():
    """Accept IG_TOKEN / IG_USER_ID, or any extra secrets (SECRET_A/B): numbers = user id, long text = token."""
    tok, uid = os.environ.get('IG_TOKEN', '').strip(), os.environ.get('IG_USER_ID', '').strip()
    for k in ('SECRET_A', 'SECRET_B'):
        v = os.environ.get(k, '').strip()
        if not v:
            continue
        if v.isdigit():
            uid = uid or v
        elif len(v) > 40:
            tok = tok or v
    return tok, uid or 'me'


TOKEN, UID = _pick()
BASE = os.environ.get('MEDIA_BASE_URL', '').rstrip('/')
VER = os.environ.get('IG_API_VERSION', '').strip('/')
API = 'https://graph.instagram.com' + (f'/{VER}' if VER else '')
DRY = os.environ.get('DRY_RUN') == '1'


def today_tr():
    return (dt.datetime.utcnow() + dt.timedelta(hours=3)).date()


def call(method, path, **params):
    if DRY:
        print('DRY', method, path, {k: v for k, v in params.items() if k != 'caption'})
        return {'id': f'dry-{abs(hash(str(params))) % 10**6}', 'status_code': 'FINISHED'}
    params['access_token'] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f'{API}/{path}'
    req = urllib.request.Request(url + ('?' + data.decode() if method == 'GET' else ''),
                                 data=None if method == 'GET' else data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')
        msg = f'Instagram API error {e.code} on {method} {path}: {body}'
        print(f'::error::{msg}')
        raise SystemExit(msg)


def wait_ready(cid, timeout=900):
    t0 = time.time()
    while True:
        st = call('GET', cid, fields='status_code').get('status_code')
        if st == 'FINISHED':
            return
        if st in ('ERROR', 'EXPIRED'):
            raise SystemExit(f'Container {cid} failed: {st}')
        if time.time() - t0 > timeout:
            raise SystemExit(f'Container {cid} not ready after {timeout}s (last: {st})')
        time.sleep(10)


def url_for(folder, name):
    rel = folder.relative_to(ROOT).as_posix()
    return f'{BASE}/{urllib.parse.quote(rel)}/{urllib.parse.quote(name)}'


def publish(folder, post):
    kind, files, cap = post['type'], post['files'], post.get('caption', '')
    if kind == 'image':
        cid = call('POST', f'{UID}/media', image_url=url_for(folder, files[0]), caption=cap)['id']
    elif kind == 'carousel':
        if not 2 <= len(files) <= 10:
            raise SystemExit('carousel needs 2-10 files (API limit 10)')
        kids = [call('POST', f'{UID}/media', image_url=url_for(folder, f), is_carousel_item='true')['id'] for f in files]
        for k in kids:
            wait_ready(k)
        cid = call('POST', f'{UID}/media', media_type='CAROUSEL', children=','.join(kids), caption=cap)['id']
    elif kind == 'reel':
        p = dict(media_type='REELS', video_url=url_for(folder, files[0]), caption=cap, share_to_feed='true')
        if post.get('cover'):
            p['cover_url'] = url_for(folder, post['cover'])
        cid = call('POST', f'{UID}/media', **p)['id']
    else:
        raise SystemExit(f'unknown type {kind}')
    wait_ready(cid)
    res = call('POST', f'{UID}/media_publish', creation_id=cid)
    return res.get('id')


def check():
    def kind(v):
        v = (v or '').strip()
        return 'boş' if not v else ('sayı (' + str(len(v)) + ' hane)' if v.isdigit() else 'metin (' + str(len(v)) + ' karakter)')
    print('::notice::Gizli ayarlar: ' + ', '.join(f'{k}={kind(os.environ.get(k))}' for k in ('IG_TOKEN', 'IG_USER_ID', 'SECRET_A', 'SECRET_B')))
    if not TOKEN:
        print('::error::Erişim anahtarı bulunamadı (uzun metin içeren bir gizli ayar yok).')
        raise SystemExit(1)
    me = call('GET', 'me', fields='user_id,username,account_type')
    print(f"::notice::Bağlantı tamam: @{me.get('username')} ({me.get('account_type')})")
    print(f"Bağlantı tamam: @{me.get('username')} ({me.get('account_type')}), user_id={me.get('user_id')}, kullanılan id={UID}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        return check()
    if not DRY and (not TOKEN or not BASE):
        raise SystemExit('IG_TOKEN and MEDIA_BASE_URL must be set')
    due = []
    for d in sorted(p for p in QUEUE.iterdir() if p.is_dir()) if QUEUE.exists() else []:
        f = d / 'post.json'
        if f.exists():
            post = json.loads(f.read_text(encoding='utf-8'))
            if dt.date.fromisoformat(post['date']) <= today_tr():
                due.append((d, post))
    if not due:
        print('Nothing due today.')
        return
    folder, post = due[0]
    media_id = publish(folder, post)
    print(f'PUBLISHED {folder.name} -> media {media_id}')
    out = os.environ.get('GITHUB_OUTPUT')
    if out:
        with open(out, 'a') as fh:
            fh.write(f'folder={folder.name}\nmedia_id={media_id}\n')


if __name__ == '__main__':
    main()
