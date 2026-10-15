"""Gelen DM'lere ilk karşılama mesajı (Instagram API with Instagram Login).

Konuşmaları tarar; karşı taraf yazmış ve @rotasigns o konuşmada hiç mesaj göndermemişse bir kez
karşılama mesajı gönderir. Daha önce yazışılmış konuşmalara (örneğin yorum DM'inden sonra gelen
yanıtlara) dokunmaz; onlara insan cevap vermeli. Instagram kuralı: son mesajdan sonraki 24 saat içinde.

Karşılananlar state/dm-karsilanan.json, gönderim kaydı state/dm-log.json.
Kullanım: python3 scripts/dm_welcome.py [test]
"""
import datetime as dt, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comment_dm import api, norm, TOKEN, log_ekle  # aynı API yardımcıları

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / 'state' / 'dm-karsilanan.json'
TEST = len(sys.argv) > 1 and sys.argv[1] == 'test'

KARSILAMA = (
    "Merhaba, mesajınız için teşekkürler! 🙌 Ben ROTA ekibinden.\n\n"
    "ROTA; tabela, reklam ve üretim atölyeleri için iş takip programı: teklif, üretim, montaj, stok ve tahsilat tek ekranda.\n\n"
    "• Hesap açmadan örnek verilerle gezin: https://rotasigns.com\n"
    "• 14 gün ücretsiz deneyin (kredi kartı gerekmez): https://rota-bulutt.vercel.app/kayit?kaynak=ig-dm\n\n"
    "Sorunuzu buraya yazabilirsiniz, en kısa sürede dönüyoruz. Hızlı ulaşmak için WhatsApp: 0543 311 53 47"
)


def main():
    if not TOKEN:
        raise SystemExit('IG_TOKEN yok')
    me = api('GET', 'me', {'fields': 'user_id,username'})
    uid, kendim = str(me['user_id']), norm(me.get('username'))
    karsilanan = set(json.loads(STATE.read_text())) if STATE.exists() else set()
    simdi = dt.datetime.now(dt.timezone.utc)
    try:
        konusmalar = api('GET', 'me/conversations', {'platform': 'instagram', 'fields': 'id,updated_time,messages.limit(20){from,created_time}', 'limit': 25}).get('data', [])
    except RuntimeError as e:
        print(f'::error::Mesajlar okunamadı (izin eksik olabilir: instagram_business_manage_messages / "Mesajlara erişime izin ver"): {e}')
        raise SystemExit(1)
    yeni = 0
    for k in konusmalar:
        msjlar = (k.get('messages') or {}).get('data', [])
        if not msjlar or k['id'] in karsilanan:
            continue
        bizden = [m for m in msjlar if str((m.get('from') or {}).get('id')) == uid or norm((m.get('from') or {}).get('username')) == kendim]
        onlardan = [m for m in msjlar if m not in bizden]
        if bizden or not onlardan:
            continue
        son = max(dt.datetime.fromisoformat(m['created_time'].replace('+0000', '+00:00')) for m in onlardan)
        if simdi - son > dt.timedelta(hours=23):
            continue
        kime = (onlardan[0].get('from') or {})
        yeni += 1
        if TEST:
            print(f"TEST: @{kime.get('username')} karşılanacaktı")
            continue
        try:
            api('POST', f'{uid}/messages', body={'recipient': {'id': kime['id']}, 'message': {'text': KARSILAMA}})
        except RuntimeError as e:
            print(f"::warning::@{kime.get('username')} karşılanamadı: {e}")
            continue
        karsilanan.add(k['id'])
        log_ekle('karsilama')
        print(f"::notice::Karşılama gönderildi: @{kime.get('username')}")
    print(f'::notice::{len(konusmalar)} konuşma tarandı; yeni karşılama: {yeni}')
    if not TEST:
        STATE.parent.mkdir(exist_ok=True)
        STATE.write_text(json.dumps(sorted(karsilanan), indent=0))


if __name__ == '__main__':
    main()
