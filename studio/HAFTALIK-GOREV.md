# Haftalık Instagram içeriği: çalışma talimatı

Bu dosya, her pazartesi çalışan zamanlanmış görevin izleyeceği adımlardır.

## Marka
- **ROTA** (rotasigns.com): tabela, reklam ve üretim atölyeleri için tarayıcıdan çalışan iş takip programı.
- Modüller: teklif listesi (kabul edilen teklif tek adımda işe dönüşür), görev yönetimi (kart sürüklenince iş devredilir, sorumlu bildirim alır), müşteri onayı/revizyon kartta (onay gelmeden üretime geçilmez), haftalık üretim ve montaj planı, depo/stok (hareketlerden hesaplanır, kritik stok uyarısı), kasa/banka/tahsilat (montaj bitince muhasebe haberdar olur), roller (yönetici, tasarım, üretim, montaj, muhasebe).
- Teklif: 15 gün ücretsiz deneme, kredi kartı yok, kullanıcı sınırı yok. Canlı demo: rotasigns.com/demo. WhatsApp: 0543 311 53 47.
- Ton: pratik, sahayı bilen, sakin, açık sözlü. "Devrim", "sektör lideri", "kusursuz" yok.
- **Asla uydurma:** müşteri adı, referans, yorum, istatistik, fiyat, entegrasyon. Örnek hesaplar açıkça "örnek" diye yazılır. Sohbetlerdeki kişi ve firma adları kurgusal ve sıradan olmalı (Ayşe, Murat, "Ege Mobilya" gibi), gerçek bir firmayı çağrıştırmamalı.

## Adımlar
1. `queue/` ve `posted/` içindeki `post.json` ve `spec.json` dosyalarını oku. Son 4 haftada işlenen konuları tekrar etme.
2. **Tarihler:** `queue/` içindeki en geç tarih ile bugünün büyük olanını al; sonraki gün başlayarak **7 gün**, günde 1 gönderi.
3. **Klasör numarası:** `queue/` ve `posted/` içindeki en büyük `NNN` + 1'den devam et. Klasör adı: `NNN-kisa-konu` (Türkçe karakter yok).
4. **Haftalık karışım:** 1 `karusel` (eğitici, 3–5 slayt), 3 `ozellik`, 1 `sohbet`, 1 `istatistik` (yalnızca açık örnek hesap), 1 `cagri`. Her `ozellik` farklı modülü ve farklı ekran görüntüsünü kullansın.
5. **Konu havuzu (dön dolaş):** keşiften teklife; teklifi işe çevirme; revizyon ve müşteri onayı; kutu harf üretim adımları; montaj günü kontrol listesi; stok ve kritik malzeme; tahsilat ve kapora takibi; rol ve yetkiler; atölyede günlük 10 dakikalık toplantı; Excel ve WhatsApp'tan geçiş; yoğun sezonda planlama; yeni eleman alıştırma.
6. Her gönderi için `queue/NNN-.../spec.json` yaz (alanlar `studio/render.py` başında). Ekran adları: `studio/assets/` içindeki `ekran-*.jpg` dosyaları.
7. **Açıklama metni (caption):** açılış cümlesi tanıdık bir atölye durumu, 2–4 kısa paragraf, tek çağrı (demo ya da ücretsiz deneme), **en fazla 5 hashtag**. Hashtag havuzu: #tabelacı #reklamatölyesi #iştakipprogramı #kutuharf #ledtabela #üretimplanlama #reklamcılar #ROTA.
8. Çalıştır: `python3 studio/render.py queue/NNN-... queue/NNN+1-...` (hepsini tek seferde).
9. **Kontrol:** üretilen JPEG'lerin hepsine bak (küçültülmüş bir temas sayfası yapıp aç). Taşan metin, kesilen başlık, boş kalan alan varsa metni kısaltıp tekrar üret.
10. **Onaya gönder:**
    - Yeni dal: `hafta-YYYY-AA-GG` (ilk gönderinin tarihi).
    - Yalnızca yeni klasörleri commit'le, `main` dalına **doğrudan push etme**.
    - Pull request aç: başlık "Instagram · <ilk tarih> haftası", gövdede günlere göre tablo (tarih, tür, başlık).
11. Kullanıcıya Türkçe kısa mesaj gönder: haftanın konuları, temas sayfası görseli ve PR linki. Not: "Onaylıyorsanız GitHub'da (telefondaki uygulamadan da olur) **Merge** deyin; birleştirmezseniz hiçbir şey paylaşılmaz."
