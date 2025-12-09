# Social Scheduler Desktop

Kurumsal ölçekte içerik planlama ve paylaşım için geliştirilen Windows masaüstü uygulaması. Instagram ve YouTube hesaplarıyla OAuth/ token mantığına göre çalışır, içerikleri planlayıp zamanlayıcıyla otomatik gönderir. "Uygulama Geliştiricisi: Burak BEKER" bilgisi Hakkında ekranında yer alır.

## Mimari ve Teknoloji Tercihi
- **Stack:** Python 3.11 + PySide6 (Qt) + APScheduler + PyInstaller + Inno Setup.
- **Neden?**
  - PySide6: Yerel Windows deneyimi, modern ve responsive arayüz, tek kod tabanıyla görsel bileşenler.
  - APScheduler: Kararlı zamanlayıcı, GUI thread'inden bağımsız çalışma.
  - PyInstaller + Inno Setup: Tek EXE ve ardından tek setup (.exe/.msi eşleniği) üretimi; son kullanıcı için "ileri-ileri-bitir" akışı.
  - python-dotenv + cryptography: OAuth bilgilerini ve erişim tokenlarını şifreli/konfigüre edilebilir şekilde saklama.

## Proje Dosya Yapısı
```
.
├─ .env.example           # OAuth client id/secret ve uygulama gizli anahtar örneği
├─ README.md              # Bu dokümantasyon
├─ requirements.txt       # Uygulama bağımlılıkları
├─ build_exe.cmd          # Windows'ta PyInstaller için toplu betik
├─ build_exe.ps1          # PowerShell betiği (alternatif)
├─ src/
│  ├─ main.py             # Uygulama giriş noktası
│  ├─ app.py              # QApplication/ana pencere başlatıcısı
│  ├─ config.py           # Ortam değişkenleri, veri yolları, sabitler
│  ├─ auth.py             # OAuth URL üretimi ve (demo) login yönetimi
│  ├─ models.py           # Platform, içerik planı ve log veri sınıfları
│  ├─ storage.py          # Şifreli token saklama ve JSON state yönetimi
│  ├─ platform_clients.py # Instagram/YouTube istemci iskeleti, gönderim simülasyonu
│  ├─ scheduler_engine.py # APScheduler tabanlı görev planlayıcı
│  └─ ui/
│     ├─ about_dialog.py  # Hakkında ekranı (“Uygulama Geliştiricisi: Burak BEKER”)
│     ├─ dashboard_widget.py # Özet kartları
│     ├─ log_widget.py    # Gönderim logları tablosu
│     ├─ main_window.py   # Sidebar + sayfa yığını
│     ├─ planner_widget.py# İçerik planlama formu/listesi
│     └─ session_widget.py# Instagram/YouTube oturum yönetimi
```

## Önemli Modüller için Kod Örnekleri
### UI İskeleti (MainWindow)
```python
# src/ui/main_window.py
self.sidebar.addItem(QListWidgetItem("Dashboard"))
self.sidebar.addItem(QListWidgetItem("Oturumlar"))
self.sidebar.addItem(QListWidgetItem("Planlama"))
self.sidebar.addItem(QListWidgetItem("Loglar"))
self.sidebar.addItem(QListWidgetItem("Hakkında"))
self.stack.addWidget(self.dashboard)
self.stack.addWidget(self.sessions)
self.stack.addWidget(self.planner)
self.stack.addWidget(self.logs)
self.stack.addWidget(self.about)
```

### Instagram / YouTube Auth Akışı (placeholder + OAuth URL)
```python
# src/auth.py
if platform == Platform.INSTAGRAM:
    return (
        "https://api.instagram.com/oauth/authorize"
        f"?client_id={INSTAGRAM_CLIENT_ID}&redirect_uri={INSTAGRAM_REDIRECT_URI}&response_type=code&scope=user_profile,user_media"
    )
# YouTube OAuth URL benzeri
```
Demo/test için `connect_with_fake_token` fonksiyonu sahte token üretir. Gerçek senaryoda OAuth callback kodunu alıp token takası yapmanız yeterli.

### Planlama Scheduler Mantığı
```python
# src/scheduler_engine.py
self.scheduler.add_job(
    self._run_job,
    "date",
    run_date=plan.scheduled_for,
    args=[plan, platform],
    id=f"{plan.id}-{platform.value}",
    replace_existing=True,
)
```
Görev çalıştığında `dispatch_plan` ile ilgili platform istemcisine çağrı yapılır, durum/log güncellenir.

### Veri Modelleri
- **ContentPlan**: id, title, description, hashtags, youtube_tags, media_path, thumbnail_path, scheduled_for, platforms, status, last_error.
- **PlatformAccount**: platform, username, access_token (şifreli saklanır), refresh_token, expires_at, connected_at.
- **LogEntry**: timestamp, platform, content_id, status, message.

## Uygulamayı Çalıştırmak için Adım Adım Komutlar
1. Depoyu klonla / indir:
   ```bash
   git clone <repo-url>
   cd Captain-Hook
   ```
2. Python 3.11+ kurulu olduğundan emin ol.
3. Bağımlılıkları yükle:
   ```bash
   pip install -r requirements.txt
   ```
4. .env oluştur (örnekten kopyala):
   ```bash
   copy .env.example .env   # Windows PowerShell/cmd
   ```
   `APP_SECRET_KEY` ve OAuth client bilgilerini doldur.
5. Geliştirme modunda çalıştır:
   ```bash
   python -m src.app
   ```

## İndirme / Kurulum Paketi Nerede?
- Bu depo şu anda yalnızca kaynak kodunu içeriyor; hazır kurulum paketi yayınlanmış değil.
- Kendi setup dosyanızı üretmek için aşağıdaki "Build & Setup Üretim Adımları" bölümünü izleyin. Komutlar tamamlandığında kurulum dosyası `dist/social_scheduler_setup.exe` (veya Inno Setup çıktınız) olarak oluşur ve bu dosyayı dağıtarak yükleme yapılabilir.

## Build & Setup Üretim Adımları
1. Tek dosya EXE oluştur (Windows):
   ```cmd
   build_exe.cmd
   ```
   Çıktı: `dist/social_scheduler.exe`
2. Tek setup üretmek için Inno Setup (ya da benzeri) kullan:
   - Yeni bir Inno Setup Script açın, kaynak olarak `dist/social_scheduler.exe` seçin.
   - Masaüstü kısayolu ve Başlat menüsü girişi ekleyin.
   - Çıktı tek `.exe` setup dosyası olacaktır.

## Son Kullanıcı Kurulum Senaryosu
1. Setup dosyasını indir, çift tıkla, ileri-ileri-bitir adımlarını takip et.
2. Masaüstüne ve Başlat menüsüne “Social Scheduler Desktop” kısayolu eklenir.
3. İlk açılışta splash/dashbord görünecek, ardından **Oturumlar** sekmesinden Instagram ve YouTube girişini yapabilirsiniz (OAuth tarayıcı açar). Test için "Test Modu: Fake Token" butonu da mevcuttur.
4. **Planlama** sekmesinden görsel/video, açıklama, hashtag ve tarih-saat seçerek plan ekleyin; gönderi zamanı geldiğinde uygulama otomatik paylaşımı tetikler ve **Loglar** sekmesinde sonucu görebilirsiniz.

## Güvenlik ve Ayarlar
- OAuth client id/secret bilgilerini `.env` dosyasında saklayın, kodda hardcode etmeyin.
- Erişim tokenları `cryptography` ile şifrelenmiş olarak kullanıcı profilinde (`~/.social_scheduler/app_state.json`) tutulur.
- Ayarlar/varsayılan metinler `.env` veya kod içi sabitlerle yönetilebilir.

## Onboarding (kullanıcıya hızlı rehber)
1. Uygulamayı başlatın, Dashboard sonrası **Oturumlar** sekmesine geçin.
2. Instagram/YouTube için “OAuth ile bağlan”ı tıklayın ve tarayıcıdaki yetkilendirme adımlarını tamamlayın.
3. **Planlama** sekmesinden yeni içerik planı oluşturun: medya seçin, açıklamaları yazın, tarih-saat ve platformları belirleyin, “Planı Kaydet” deyin.
4. **Loglar** sekmesinden gönderim durumunu izleyin; sorun çıkarsa hata mesajını görün.
5. **Hakkında** sekmesinde uygulama bilgisi ve “Uygulama Geliştiricisi: Burak BEKER” ibaresi yer alır.
