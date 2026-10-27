"""Yorum anahtar kelimesine otomatik DM (Instagram API with Instagram Login, "private reply").

Son gönderilere yapılan yorumlarda anahtar kelime (DENEME, DEMO, BİLGİ, LİNK…) geçiyorsa yorumu yazan
kişiye bir kez DM gönderir ve yoruma kısa bir herkese açık yanıt bırakır. Instagram kuralı gereği
yorumdan sonraki 7 gün içinde ve her yoruma en fazla bir özel yanıt gönderilebilir.

Gönderilen yorumların kimlikleri state/dm-yanitlanan.json dosyasında tutulur (iş akışı commit eder).

Kullanım: python3 scripts/comment_dm.py            # çalıştır
          python3 scripts/comment_dm.py test       # hiçbir şey göndermeden tara, izinleri sına
Env: IG_TOKEN (gerekli; publish.py ile aynı gizli ayarlar), IG_API_VERSION (isteğe bağlı)
"""
import datetime as dt, json, os, pathlib, sys, urllib.error, urllib.parse, urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from publish import _pick  # aynı gizli ayar mantığı

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / 'state' / 'dm-yanitlanan.json'
TOKEN, _ = _pick()
VER = os.environ.get('IG_API_VERSION', '').strip('/') or 'v23.0'
API = f'https://graph.instagram.com/{VER}'
TEST = len(sys.argv) > 1 and sys.argv[1] == 'test'

ANAHTAR = ('deneme', 'demo', 'bilgi', 'link', 'fiyat', 'kokpit')
DM_METNI = (
    "Merhaba! ROTA'ya ilginiz için teşekkürler 🙌\n\n"
    "Hesap açmadan, örnek verilerle hemen gezebilirsiniz: https://rotasigns.com/?utm_source=instagram&utm_medium=dm\n\n"
    "Kendi atölyenizle denemek için 14 gün ücretsiz hesap (kredi kartı gerekmez):\n"
    "https://rota-bulutt.vercel.app/kayit?kaynak=ig-dm\n\n"
    "Sorunuz olursa buradan yazın ya da WhatsApp: 0543 311 53 47"
)
GENEL_YANIT = "Bağlantıyı DM'den gönderdik, kutunuza bakabilirsiniz 🙌"


LOG = ROOT / 'state' / 'dm-log.json'


def log_ekle(tur):
    """Haftalık rapor için gönderim kaydı: [{"t": ISO zaman, "tur": "yorum"|"karsilama"}]."""
    kayit = json.loads(LOG.read_text()) if LOG.exists() else []
    kayit.append({'t': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'tur': tur})
    LOG.parent.mkdir(exist_ok=True)
    LOG.write_text(json.dumps(kayit[-2000:], indent=0))


def norm(t):
    return (t or '').replace('İ', 'i').replace('I', 'ı').lower()


def api(method, path, params=None, body=None):
    params = dict(params or {}, access_token=TOKEN)
    url = f'{API}/{path}?' + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={'Content-Type': 'application/json'} if data else {})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'{e.code} {method} {path}: {e.read().decode("utf-8", "replace")[:300]}')


def main():
    if not TOKEN:
        raise SystemExit('IG_TOKEN yok')
    me = api('GET', 'me', {'fields': 'user_id,username'})
    uid, kendim = me['user_id'], norm(me.get('username'))
    yanitlanan = set(json.loads(STATE.read_text())) if STATE.exists() else set()
    simdi = dt.datetime.now(dt.timezone.utc)
    medya = api('GET', 'me/media', {'fields': 'id,timestamp', 'limit': 25}).get('data', [])
    aday = toplam = 0
    for m in medya:
        try:
            yorumlar = api('GET', f"{m['id']}/comments", {'fields': 'id,text,username,timestamp', 'limit': 100}).get('data', [])
        except RuntimeError as e:
            print(f'::error::Yorumlar okunamadı (izin eksik olabilir: instagram_business_manage_comments): {e}')
            raise SystemExit(1)
        for c in yorumlar:
            toplam += 1
            if c['id'] in yanitlanan or norm(c.get('username')) == kendim:
                continue
            if not any(k in norm(c.get('text')) for k in ANAHTAR):
                continue
            ts = dt.datetime.fromisoformat(c['timestamp'].replace('+0000', '+00:00'))
            if simdi - ts > dt.timedelta(days=7):
                continue
            aday += 1
            if TEST:
                print(f"TEST: @{c.get('username')} yorumuna DM gönderilecekti: {c.get('text')[:60]!r}")
                continue
            try:
                api('POST', f'{uid}/messages', body={'recipient': {'comment_id': c['id']}, 'message': {'text': DM_METNI}})
            except RuntimeError as e:
                print(f"::warning::@{c.get('username')} için DM gönderilemedi: {e}")
                continue
            yanitlanan.add(c['id'])
            log_ekle('yorum')
            print(f"::notice::DM gönderildi: @{c.get('username')}")
            try:
                api('POST', f"{c['id']}/replies", {'message': GENEL_YANIT})
            except RuntimeError as e:
                print(f'::warning::Yoruma yanıt yazılamadı: {e}')
    print(f'::notice::{len(medya)} gönderi, {toplam} yorum tarandı; anahtar kelimeli yeni yorum: {aday}')
    if not TEST:
        STATE.parent.mkdir(exist_ok=True)
        STATE.write_text(json.dumps(sorted(yanitlanan), indent=0))


if __name__ == '__main__':
    main()
