# Haftalık Instagram içeriği: çalışma talimatı

Bu dosya, her pazartesi çalışan zamanlanmış görevin izleyeceği adımlardır.

## Marka
- **ROTA** (rotasigns.com): tabela, reklam ve üretim atölyeleri için tarayıcıdan çalışan iş takip programı.
- Modüller: teklif listesi (kabul edilen teklif tek adımda işe dönüşür), görev yönetimi (kart sürüklenince iş devredilir, sorumlu bildirim alır), müşteri onayı/revizyon kartta (onay gelmeden üretime geçilmez), haftalık üretim ve montaj planı, depo/stok (hareketlerden hesaplanır, kritik stok uyarısı), kasa/banka/tahsilat (montaj bitince muhasebe haberdar olur), roller (yönetici, tasarım, üretim, montaj, muhasebe).
- Teklif: 14 gün ücretsiz deneme hesabı, kredi kartı gerekmez, en fazla 5 kullanıcı, hesap örnek verilerle hazır gelir, istenince kendi verine geçilir. Hesap açmadan örnek verilerle gezinti de var (sitedeki "Hesap açmadan gezin" düğmesi). Çağrılarda yalnızca rotasigns.com adresini ver. WhatsApp: 0543 311 53 47.
- Asla yazma: "kullanıcı sınırı yok", "15 gün", "kurulumu birlikte yapıyoruz", "rotasigns.com/demo".
- Ton: pratik, sahayı bilen, sakin, açık sözlü. "Devrim", "sektör lideri", "kusursuz" yok.
- **Asla uydurma:** müşteri adı, referans, yorum, istatistik, fiyat, entegrasyon. Örnek hesaplar açıkça "örnek" diye yazılır. Sohbetlerdeki kişi ve firma adları kurgusal ve sıradan olmalı (Ayşe, Murat, "Ege Mobilya" gibi), gerçek bir firmayı çağrıştırmamalı.

## Adımlar
1. `queue/` ve `posted/` içindeki `post.json` ve `spec.json` dosyalarını oku. Son 4 haftada işlenen konuları tekrar etme. Tema sırası: son paylaşılan/kuyruktaki son bloğun temasına bak, yeni bloklar açık/koyu dönüşümle devam etsin; her blok 3 gönderi.
2. **Tarihler:** `queue/` içindeki en geç tarih+saat ile bugünün büyük olanını al; ardından **günde 2 gönderi** (`"time": "12:30"` ve `"time": "20:30"`). Haftada **15 gönderi** (5 tam blok), son blok bir sonraki güne taşabilir.
3. **Klasör numarası:** `queue/` ve `posted/` içindeki en büyük `NNN` + 1'den devam et. Klasör adı: `NNN-kisa-konu` (Türkçe karakter yok).
4. **Haftalık karışım (15 gönderi, 27.10 planı):** ürün en fazla ~%20.
   - 3 `ozellik` (ürün; her biri farklı modül ve ekran)
   - 5 pratik ipucu: `karusel` ya da liste (kontrol listesi, hesap, şablon, hazır mesaj; ekran görüntüsü şart değil, kaydetmeye değer olsun)
   - 4 tabelacı hayatı / mizah: `sohbet` skeçleri, müşteri cümleleri, sözlük, "söylenmeyecek cümleler" (gönderilmeye/paylaşılmaya değer olsun)
   - 2 topluluk: soru, tartışma ("siz kapora kaç alıyorsunuz?"), yorumlardan gelen sorular
   - 1 `cagri` (deneme / hesap açmadan gezin)
   Ürünü içeriğin **sonunda** göster: önce tabelacının derdi, sonra çözüm.
5. **Konu havuzu (dön dolaş):** keşiften teklife; teklifi işe çevirme; revizyon ve müşteri onayı; kutu harf üretim adımları; montaj günü kontrol listesi; stok ve kritik malzeme; tahsilat ve kapora takibi; rol ve yetkiler; atölyede günlük 10 dakikalık toplantı; Excel ve WhatsApp'tan geçiş; yoğun sezonda planlama; yeni eleman alıştırma.
6. Her gönderi için `queue/NNN-.../spec.json` yaz (alanlar `studio/render.py` başında). Ekran adları: `studio/assets/` içindeki `ekran-*.jpg` dosyaları.
7. **Açıklama metni (caption):**
   - İlk cümle aranabilir ve doğal olsun, konunun anahtar kelimesini içersin (ör. "Kutu harf teklifi hazırlarken en sık unutulan 7 kalem: tabelacılar için kontrol listesi."). Instagram araması ve Google bu metni okur.
   - 2–4 kısa paragraf, **tek çağrı**. Hepsini birden isteme.
   - "Bağlantıyı DM'den göndermemiz için yorumlara DENEME yazın 👇" yalnızca ürün gönderilerinde ve **haftada en fazla 2 kez** (yorum yazana otomatik DM gider, bkz. scripts/comment_dm.py).
   - Diğer çağrılar: ipucunda "Kaydedin, ekibinize gönderin", mizahta "Bir ustaya gönderin", toplulukta "Yorumlara yazın", üründe "Hesap açmadan, örnek verilerle gezin: profildeki bağlantı → rotasigns.com".
   - **En fazla 5 hashtag**, her gönderide aynısı değil; konuya göre bir set seç:
     - Kutu harf / üretim / montaj: `#kutuharf #tabelaimalatı #tabelacı #ışıklıtabela #rotasigns`
     - Neon: `#neontabela #ledneon #tabela #reklamatölyesi #rotasigns`
     - Ürün / iş yönetimi: `#iştakipprogramı #tabelacı #reklamajansı #kobi #rotasigns`
     - Finans / tahsilat: `#önmuhasebe #iştakipprogramı #tabelacı #kobi #rotasigns`
     - Stok / depo: `#stoktakibi #tabelaimalatı #tabelacı #reklamatölyesi #rotasigns`
     - Mizah / hayat: `#tabelacılar #tabelacıhayatı #reklamcı #esnaf #rotasigns`
8. Çalıştır: `python3 studio/render.py queue/NNN-... queue/NNN+1-...` (hepsini tek seferde).
9. **Kontrol:** üretilen JPEG'lerin hepsine bak (küçültülmüş bir temas sayfası yapıp aç). Taşan metin, kesilen başlık, boş kalan alan varsa metni kısaltıp tekrar üret.
10. **Onaya gönder:**
    - Yeni dal: `hafta-YYYY-AA-GG` (ilk gönderinin tarihi).
    - Yalnızca yeni klasörleri commit'le, `main` dalına **doğrudan push etme**.
    - Pull request aç: başlık "Instagram · <ilk tarih> haftası", gövdede günlere göre tablo (tarih, tür, başlık).
11. Kullanıcıya Türkçe kısa mesaj gönder: haftanın konuları, temas sayfası görseli ve PR linki. Not: "Onaylıyorsanız GitHub'da (telefondaki uygulamadan da olur) **Merge** deyin; birleştirmezseniz hiçbir şey paylaşılmaz."

## Profil düzeni ve tema kuralları (21.10.2026)

- **Her 3 ardışık paylaşım aynı temada** (profil ızgarasında bir satır). Temalar ROTA'nın görünüm temalarıdır:
  Rota İmza (kırık beyaz + turuncu), Gece Rotası (koyu lacivert), Finans Merkezi (açık gri + lacivert), Sessiz Ofis (yumuşak gri + adaçayı), Kokpit (krem + turuncu).
- Satırlar açık/koyu dönüşümlü: açık tema → Gece Rotası → başka bir açık tema → Gece Rotası…
- Her temanın kendi animasyon karakteri var: İmza kayarak, Gece bulanıklıktan netleşerek, Finans soldan sağa perde açılarak, Sessiz yumuşak solarak, Kokpit zıplayarak gelir.
- Sıra `scratchpad/reels3/themes.py` içindeki `SIRA` listesinde. Yeni içerik eklerken 3'lü blok olarak ekleyin; bir paylaşım kaçarsa ya da silinirse satırlar kayar.
- **Kaydırmalı gönderiler** tek geniş tuval olarak çizilip dilimlenir; en az bir öğe (büyük rakam, çizgi, ok) 1. ve 2. fotoğrafın sınırından geçer, böylece kaydırınca devam eder.
- Reels'lerin kapağı 2.3. saniyedeki kanca karesidir (`kapak.jpg`), ızgarada okunaklı görünür.

## 27.10.2026 planı (özet)
- Kaynak: kullanıcının "@rotasigns Instagram Büyüme ve Etkileşim Planı" belgesi. Tempo kullanıcı kararıyla **günde 2** (planın önerisi günde 1'di).
- Hedef: tabelacı topluluğunun hesabı gibi davranmak; ürün içeriğin ~%20'si.
- Otomatik takip / takipten çıkma, toplu yorum ya da beğeni botu **kullanılmaz**. Topluluk rutini (atölyelere yorum, collab mesajları) kullanıcının elle yaptığı iştir.
- Atölye/saha videoları (kutu harf yapımı, montaj, "ışık yandı") partner atölyelerden gelecek; gelene kadar görsel skeç ve ipucu içerikleri kullanılır.
