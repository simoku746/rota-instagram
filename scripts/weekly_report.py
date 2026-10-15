"""Haftalık Instagram raporu: takipçi değişimi, gönderilerin beğeni/yorum sayıları, otomatik DM sayıları.

Takipçi geçmişi state/takipci.json'da tutulur (her çalıştırmada bir satır). Rapor reports/YYYY-MM-DD.md
dosyasına yazılır; iş akışı aynı metinle bir GitHub "issue" açar, böylece GitHub e-postayla bildirir.
Erişim (reach) gibi ayrıntılı ölçümler için instagram_business_manage_insights izni varsa onlar da eklenir.
"""
import datetime as dt, json, os, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from comment_dm import api, TOKEN

ROOT = pathlib.Path(__file__).resolve().parent.parent
HIST = ROOT / 'state' / 'takipci.json'
LOG = ROOT / 'state' / 'dm-log.json'


def main():
    if not TOKEN:
        raise SystemExit('IG_TOKEN yok')
    simdi = dt.datetime.now(dt.timezone.utc)
    hafta_once = simdi - dt.timedelta(days=7)
    me = api('GET', 'me', {'fields': 'username,followers_count,follows_count,media_count'})
    gecmis = json.loads(HIST.read_text()) if HIST.exists() else []
    onceki = next((g for g in reversed(gecmis) if dt.datetime.fromisoformat(g['t']) <= simdi - dt.timedelta(days=6)), gecmis[0] if gecmis else None)
    gecmis.append({'t': simdi.isoformat(timespec='seconds'), 'takipci': me.get('followers_count', 0)})
    HIST.parent.mkdir(exist_ok=True)
    HIST.write_text(json.dumps(gecmis[-200:], indent=0))

    medya = api('GET', 'me/media', {'fields': 'id,caption,timestamp,permalink,like_count,comments_count,media_type', 'limit': 25}).get('data', [])
    bu_hafta = [m for m in medya if dt.datetime.fromisoformat(m['timestamp'].replace('+0000', '+00:00')) >= hafta_once]
    for m in bu_hafta:
        try:
            ins = api('GET', f"{m['id']}/insights", {'metric': 'reach,saved,shares'}).get('data', [])
            m['_ins'] = {i['name']: (i.get('values') or [{}])[0].get('value', i.get('total_value', {}).get('value')) for i in ins}
        except RuntimeError:
            m['_ins'] = {}

    log = json.loads(LOG.read_text()) if LOG.exists() else []
    dm_hafta = [x for x in log if dt.datetime.fromisoformat(x['t']) >= hafta_once]
    yorum_dm = sum(1 for x in dm_hafta if x['tur'] == 'yorum')
    karsilama = sum(1 for x in dm_hafta if x['tur'] == 'karsilama')

    takipci = me.get('followers_count', 0)
    fark = (takipci - onceki['takipci']) if onceki else None
    satirlar = [
        f"# @{me.get('username')} · haftalık rapor ({simdi.date().isoformat()})", '',
        f"- **Takipçi:** {takipci}" + (f" ({'+' if fark >= 0 else ''}{fark} bu hafta)" if fark is not None else ' (ilk ölçüm; değişim gelecek hafta görünür)'),
        f"- **Takip edilen:** {me.get('follows_count', 0)} · **Toplam gönderi:** {me.get('media_count', 0)}",
        f"- **Bu hafta paylaşılan:** {len(bu_hafta)} gönderi",
        f"- **Otomatik DM:** yorumdan {yorum_dm}, gelen mesaja karşılama {karsilama}", '',
    ]
    if bu_hafta:
        satirlar += ['| Tarih | Gönderi | Beğeni | Yorum | Erişim | Kaydetme |', '|---|---|---|---|---|---|']
        for m in sorted(bu_hafta, key=lambda m: m['timestamp']):
            ad = (m.get('caption') or '').split('\n')[0][:50].replace('|', '/')
            i = m.get('_ins', {})
            satirlar.append(f"| {m['timestamp'][:10]} | [{ad or m['media_type']}]({m['permalink']}) | {m.get('like_count', 0)} | {m.get('comments_count', 0)} | {i.get('reach', '–')} | {i.get('saved', '–')} |")
        enco = max(bu_hafta, key=lambda m: m.get('like_count', 0) + 3 * m.get('comments_count', 0))
        satirlar += ['', f"**En çok etkileşim alan:** [{(enco.get('caption') or '').split(chr(10))[0][:60]}]({enco['permalink']})"]
    satirlar += ['', '_Deneme hesabı kayıtlarının hangilerinin Instagram\'dan geldiğini platform panelindeki "kaynak" sütununda `ig-dm` olarak görebilirsiniz._']
    metin = '\n'.join(satirlar)
    out = ROOT / 'reports' / f'{simdi.date().isoformat()}.md'
    out.parent.mkdir(exist_ok=True)
    out.write_text(metin + '\n', encoding='utf-8')
    print(metin)
    gh = os.environ.get('GITHUB_OUTPUT')
    if gh:
        with open(gh, 'a') as fh:
            fh.write(f'dosya={out.relative_to(ROOT).as_posix()}\nbaslik=Instagram haftalık rapor · {simdi.date().isoformat()}\n')


if __name__ == '__main__':
    main()
