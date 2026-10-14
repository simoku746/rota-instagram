"""ROTA Instagram stüdyosu: spec.json -> 1080x1350 JPEG görseller + post.json.

Kullanım:  python3 studio/render.py queue/<NNN-slug> [queue/<...> ...]
Her klasörde bir spec.json olmalı. Çıktı: 1.jpg, 2.jpg, ... ve post.json (aynı klasöre).

spec.json alanları (hepsinde):  date (YYYY-AA-GG), caption (Instagram metni, en fazla 5 hashtag), kind
kind = "ozellik":    tag, kicker, title, title_orange, body, screen
kind = "istatistik": tag, intro, number, unit, boxes [[değer, açıklama] x3], note, footer
kind = "cagri":      title_orange, title, bullets [3 madde], button, footer
kind = "sohbet":     tag, title, title_orange, group, members, messages [[kişi|null, metin, saat]],
                     card {label, title, lines [[anahtar, değer]]}
kind = "karusel":    tag, cover {big, title, title_orange, body}, slides [{title, problem, fix, screen}] (2-7),
                     cta {title, title_orange, body}
screen: studio/assets içindeki bir ekran görüntüsünün adı (ör. "ekran-kokpit.jpg").
Metinlerde <br> ile satır kırılabilir. Görseller Instagram API'si için JPEG üretilir.
"""
import html, json, pathlib, sys, glob

ST = pathlib.Path(__file__).resolve().parent
ASSETS = ST / 'assets'
MARK = (ASSETS / 'mark-white.svg').read_text()
FONTS = (ST / 'fonts').as_uri()
W, H = 1080, 1350

def e(s):  # escape but keep <br>
    return html.escape(str(s)).replace('&lt;br&gt;', '<br>')

CSS = f"""
@font-face{{font-family:Manrope;src:url({FONTS}/manrope-latin-ext-wght-normal.woff2) format('woff2');font-weight:200 800;unicode-range:U+0100-02AF,U+1E00-1EFF}}
@font-face{{font-family:Manrope;src:url({FONTS}/manrope-latin-wght-normal.woff2) format('woff2');font-weight:200 800;unicode-range:U+0000-00FF,U+2000-206F,U+20AC,U+2122,U+2190-21FF}}
@font-face{{font-family:Inter;src:url({FONTS}/inter-latin-ext-wght-normal.woff2) format('woff2');font-weight:100 900;unicode-range:U+0100-02AF,U+1E00-1EFF}}
@font-face{{font-family:Inter;src:url({FONTS}/inter-latin-wght-normal.woff2) format('woff2');font-weight:100 900;unicode-range:U+0000-00FF,U+2000-206F,U+20AC,U+2122,U+2190-21FF}}
*{{box-sizing:border-box}}html,body{{margin:0}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:#0A111E;color:#F3F5F9;font-family:Inter,sans-serif;position:relative}}
.d{{font-family:Manrope,sans-serif;font-weight:800;letter-spacing:-.045em;line-height:.98}}
.o{{color:#FF6B16}}
.mono{{font-family:Inter,sans-serif;font-weight:700;letter-spacing:.16em;text-transform:uppercase}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px);background-size:54px 54px;mask-image:radial-gradient(circle at 70% 30%,#000 0,transparent 75%)}}
.glow{{position:absolute;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,#FF6B1633 0,transparent 62%)}}
.top{{position:absolute;left:72px;right:72px;top:64px;display:flex;align-items:center;justify-content:space-between}}
.brand{{display:flex;align-items:center;gap:14px;font-family:Manrope;font-weight:800;font-size:30px;letter-spacing:.04em}}
.brand svg{{width:44px;height:auto}}
.tag{{font-size:17px;color:#FF8A4C;border:1.5px solid #FF6B1655;border-radius:999px;padding:9px 18px}}
.bottom{{position:absolute;left:72px;right:72px;bottom:60px;display:flex;align-items:center;justify-content:space-between;font-size:24px;color:#A9B4C4}}
.bottom b{{color:#fff;font-weight:700}}
.pill{{display:inline-flex;align-items:center;gap:12px;background:#FF6B16;color:#0A111E;font-weight:800;font-family:Manrope;border-radius:999px;padding:18px 30px;font-size:28px;letter-spacing:-.01em}}
.frame{{border-radius:22px;overflow:hidden;border:2px solid #26324A;background:#0E1626;box-shadow:0 50px 90px -30px #000c,0 0 0 10px #ffffff06}}
.frame .bar{{height:34px;background:#141E30;display:flex;gap:9px;align-items:center;padding:0 16px}}
.frame .bar i{{width:11px;height:11px;border-radius:50%;background:#33415A}}
.frame img{{display:block;width:100%;height:calc(100% - 34px);object-fit:cover;object-position:top left}}
.num{{font-family:Manrope;font-weight:800;color:#FF6B16}}
.dots{{display:flex;gap:10px}}.dots i{{width:12px;height:12px;border-radius:50%;background:#33415A}}.dots i.on{{background:#FF6B16;width:34px;border-radius:6px}}
"""

def brand(tag=''):
    t = f'<div class="tag mono">{e(tag)}</div>' if tag else ''
    return f'<div class="top"><div class="brand">{MARK}ROTA</div>{t}</div>'

def bottom(left='<b>rotasigns.com</b>', right='15 gün ücretsiz'):
    return f'<div class="bottom"><span>{left}</span><span>{right}</span></div>'

def frame(img, style):
    p = ASSETS / img
    if not p.exists():
        raise SystemExit(f'Ekran görüntüsü yok: {img}. Seçenekler: {sorted(x.name for x in ASSETS.glob("*.jpg"))}')
    return f'<div class="frame" style="{style}"><div class="bar"><i></i><i></i><i></i></div><img src="{p.as_uri()}"></div>'

def page(body):
    return f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'

def dots(i, n):
    return '<div class="dots">' + ''.join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(n)) + '</div>'

def k_ozellik(s):
    return [page(f'''<div class="grid"></div><div class="glow" style="left:-400px;top:-260px"></div>{brand(s.get('tag', 'Özellik'))}
<div style="position:absolute;left:72px;right:72px;top:190px">
  {f'<div class="mono o" style="font-size:20px;margin-bottom:26px">{e(s["kicker"])}</div>' if s.get('kicker') else ''}
  <div class="d" style="font-size:104px">{e(s['title'])}<br><span class="o">{e(s['title_orange'])}</span></div>
  <p style="font-size:32px;line-height:1.4;color:#C7D0DD;margin:34px 0 0;max-width:880px">{e(s['body'])}</p>
</div>
{frame(s['screen'], 'position:absolute;left:72px;right:72px;top:720px;height:540px')}
{bottom()}''')]

def k_istatistik(s):
    boxes = ''.join(f'<div style="background:#111A2B;border:1.5px solid #1E2A3D;border-radius:20px;padding:24px"><div class="num" style="font-size:58px">{e(v)}</div><div style="font-size:23px;color:#A9B4C4;margin-top:6px">{e(k)}</div></div>' for v, k in s['boxes'])
    return [page(f'''<div class="grid"></div>{brand(s.get('tag', 'Küçük hesap'))}
<div style="position:absolute;left:72px;right:72px;top:200px">
  <div class="d" style="font-size:78px;color:#C7D0DD">{e(s['intro'])}</div>
  <div style="display:flex;align-items:baseline;gap:22px;margin-top:46px"><span class="num" style="font-size:300px;line-height:.82;letter-spacing:-.07em">{e(s['number'])}</span><span class="d" style="font-size:72px">{e(s['unit'])}</span></div>
  <div style="margin-top:60px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px">{boxes}</div>
  <p style="font-size:28px;line-height:1.45;color:#A9B4C4;margin:38px 0 0">{e(s['note'])}</p>
</div>
{bottom(s.get('footer', 'Kendi hesabınız: <b>rotasigns.com</b>'), '')}''')]

def k_cagri(s):
    check = '<span style="width:52px;height:52px;border-radius:14px;background:#FF6B16;display:flex;align-items:center;justify-content:center"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#0A111E" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></span>'
    items = ''.join(f'<div style="display:flex;align-items:center;gap:20px;font-size:38px;font-weight:600">{check}{e(t)}</div>' for t in s['bullets'])
    return [page(f'''<div class="grid"></div><div class="glow" style="right:-300px;bottom:-300px"></div>{brand()}
<div style="position:absolute;left:72px;right:72px;top:230px">
  <div class="d" style="font-size:140px"><span class="o">{e(s['title_orange'])}</span><br>{e(s['title'])}</div>
  <div style="margin-top:60px;display:flex;flex-direction:column;gap:22px">{items}</div>
  <div style="margin-top:70px"><span class="pill">{e(s.get('button', 'rotasigns.com → Ücretsiz deneyin'))}</span></div>
</div>
{bottom(s.get('footer', '<b>0543 311 53 47</b> · WhatsApp'), '')}''')]

def k_sohbet(s):
    bub = ''.join(
        f'<div style="align-self:{"flex-start" if n else "flex-end"};max-width:78%;background:{"#1F2C3F" if n else "#005C4B"};border-radius:18px;padding:14px 18px;font-size:25px;line-height:1.35">'
        + (f'<div style="font-size:19px;font-weight:700;color:#FF8A4C;margin-bottom:4px">{e(n)}</div>' if n else '')
        + f'{e(m)}<div style="text-align:right;font-size:16px;color:#8FA0B5;margin-top:4px">{e(t)}</div></div>' for n, m, t in s['messages'])
    c = s['card']
    lines = '<br>'.join(f'{e(k)}: <b>{e(v)}</b>' for k, v in c['lines'])
    return [page(f'''<div class="grid"></div>{brand(s.get('tag', 'Tanıdık geldi mi?'))}
<div style="position:absolute;left:72px;right:72px;top:180px" class="d"><span style="font-size:86px">{e(s['title'])}<br><span class="o">{e(s['title_orange'])}</span></span></div>
<div style="position:absolute;left:72px;width:600px;top:450px;bottom:150px;border-radius:44px;border:10px solid #1A2436;background:#0B141A;padding:22px;display:flex;flex-direction:column;gap:14px;overflow:hidden">
  <div style="display:flex;align-items:center;gap:12px;padding-bottom:12px;border-bottom:1px solid #ffffff14"><div style="width:44px;height:44px;border-radius:50%;background:#FF6B16"></div><div><div style="font-weight:700;font-size:22px">{e(s.get('group', 'Atölye Grubu'))}</div><div style="font-size:16px;color:#8FA0B5">{e(s.get('members', ''))}</div></div></div>
  {bub}
</div>
<div style="position:absolute;left:640px;right:60px;top:640px;background:#F3F5F9;color:#101828;border-radius:24px;padding:26px;box-shadow:0 40px 70px -20px #000c;transform:rotate(2deg)">
  <div class="mono" style="font-size:15px;color:#FF6B16">{e(c.get('label', 'ROTA · İş kartı'))}</div>
  <div style="font-family:Manrope;font-weight:800;font-size:30px;margin:10px 0 14px;letter-spacing:-.02em">{e(c['title'])}</div>
  <div style="font-size:21px;line-height:1.7;color:#344054">{lines}</div>
</div>
{bottom('Cevap kartta. <b>rotasigns.com</b>', '')}''')]

def k_karusel(s):
    sl = s['slides']
    if not 2 <= len(sl) <= 7:
        raise SystemExit('karusel: 2-7 ara slayt olmalı (kapak + slaytlar + kapanış ≤ 10)')
    n = len(sl) + 2
    cv = s['cover']
    out = [page(f'''<div class="grid"></div><div class="glow" style="left:-420px;bottom:-420px"></div>{brand(s.get('tag', 'Atölye notları'))}
<div style="position:absolute;left:72px;right:72px;top:260px">
  {f'<div class="num" style="font-size:300px;line-height:.8;letter-spacing:-.06em">{e(cv["big"])}</div>' if cv.get('big') else ''}
  <div class="d" style="font-size:100px;margin-top:20px">{e(cv['title'])} <span class="o">{e(cv['title_orange'])}</span></div>
  <p style="font-size:34px;line-height:1.4;color:#C7D0DD;margin:40px 0 0;max-width:820px">{e(cv['body'])}</p>
</div>
<div class="bottom"><span><b>rotasigns.com</b></span><span style="display:flex;align-items:center;gap:16px">Kaydırın {dots(0, n)}</span></div>''')]
    for i, x in enumerate(sl, start=1):
        out.append(page(f'''<div class="grid"></div>{brand(f"{s.get('step_label', 'Adım')} {i}/{len(sl)}")}
<div style="position:absolute;left:72px;right:72px;top:180px">
  <div class="d" style="font-size:84px">{e(x['title'])}</div>
  <p style="font-size:30px;line-height:1.45;color:#A9B4C4;margin:28px 0 0">{e(x['problem'])}</p>
</div>
{frame(x['screen'], 'position:absolute;left:72px;right:72px;top:690px;height:470px')}
<div style="position:absolute;left:72px;right:72px;top:1105px;display:flex;gap:18px;align-items:flex-start;background:#FF6B16;color:#0A111E;border-radius:22px;padding:24px 28px">
  <div style="font-family:Manrope;font-weight:800;font-size:22px;letter-spacing:.12em;padding-top:6px">ROTA</div>
  <div style="font-size:27px;line-height:1.35;font-weight:600">{e(x['fix'])}</div>
</div>
<div class="bottom" style="bottom:42px"><span><b>rotasigns.com</b></span>{dots(i, n)}</div>'''))
    ct = s['cta']
    out.append(page(f'''<div class="grid"></div><div class="glow" style="right:-380px;top:-300px"></div>{brand()}
<div style="position:absolute;left:72px;right:72px;top:300px">
  <div class="d" style="font-size:108px">{e(ct['title'])}<br><span class="o">{e(ct['title_orange'])}</span></div>
  <p style="font-size:34px;line-height:1.4;color:#C7D0DD;margin:44px 0 54px;max-width:820px">{e(ct['body'])}</p>
  <span class="pill">rotasigns.com →</span>
</div>
<div class="bottom"><span>Kaydedin, ekibinize gönderin</span>{dots(n - 1, n)}</div>'''))
    return out

KINDS = {'ozellik': k_ozellik, 'istatistik': k_istatistik, 'cagri': k_cagri, 'sohbet': k_sohbet, 'karusel': k_karusel}

def browser(p):
    try:
        return p.chromium.launch()
    except Exception:
        exe = sorted(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome')) or ['/opt/pw-browsers/chromium']
        return p.chromium.launch(executable_path=exe[-1])

def render(folders):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = browser(p)
        for f in folders:
            d = pathlib.Path(f).resolve()
            s = json.loads((d / 'spec.json').read_text(encoding='utf-8'))
            cap = s['caption']
            if cap.count('#') > 5 or len(cap) > 2200:
                raise SystemExit(f'{d.name}: açıklama en fazla 5 hashtag ve 2200 karakter olmalı')
            pages = KINDS[s['kind']](s)
            for old in d.glob('*.jpg'):
                old.unlink()
            files = []
            for i, h in enumerate(pages, start=1):
                tmp = d / f'_{i}.html'
                tmp.write_text(h, encoding='utf-8')
                pg = b.new_page(viewport={'width': W, 'height': H})
                pg.goto(tmp.as_uri()); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(250)
                pg.screenshot(path=str(d / f'{i}.jpg'), type='jpeg', quality=92)
                pg.close(); tmp.unlink(); files.append(f'{i}.jpg')
            post = {'date': s['date'], 'type': 'carousel' if len(files) > 1 else 'image', 'files': files, 'caption': cap}
            (d / 'post.json').write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'{d.name}: {len(files)} görsel')
        b.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    render(sys.argv[1:])
