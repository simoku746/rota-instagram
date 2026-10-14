# ROTA · Instagram paylaşım sırası

- `queue/` → paylaşılmayı bekleyen gönderiler. Her klasörde `post.json` + görseller/video.
- Her gün 12:30'da (Türkiye) tarihi gelmiş **ilk** gönderi Instagram'a paylaşılır ve `posted/` klasörüne taşınır.
- Haftalık içerikler bir **Pull Request** olarak gelir. Birleştirirseniz (Merge) onaylanmış olur; birleştirmezseniz paylaşılmaz.

`post.json` örneği:
```json
{"date": "2026-10-15", "type": "carousel", "files": ["1.jpg", "2.jpg"], "caption": "Metin... #tabelacı"}
```
`type`: `image` (tek görsel, JPEG), `carousel` (2–10 JPEG), `reel` (MP4, 9:16).

Gerekli gizli ayarlar (Settings → Secrets and variables → Actions): `IG_TOKEN`, `IG_USER_ID`, `GH_PAT` (anahtar yenileme için).
Bir gönderiyi beklemeden denemek için: Actions → "Instagram'a paylaş" → Run workflow.

## Stüdyo (içerik üretimi)
`studio/render.py` bir gönderi klasöründeki `spec.json` dosyasından marka renklerinde görselleri ve `post.json`'u üretir.
Haftalık görevin izlediği adımlar: `studio/HAFTALIK-GOREV.md`.
