# Nuklon-Media-Station
A video downloader which made with yt-dlp and ffmpeg
# 🌌 Nüklon Medya İstasyonu (Nuklon Media Station)

Nüklon Medya İstasyonu, internet üzerindeki medyaları yüksek kalitede bilgisayarınıza indirmenizi ve elinizdeki medya dosyalarının formatlarını değiştirmenizi sağlayan modern, hızlı ve kullanıcı dostu bir masaüstü uygulamasıdır. 

Proje, tamamen **Nesne Yönelimli Programlama (OOP)** mimarisiyle Python üzerinde inşa edilmiş olup, gücünü `yt-dlp` ve `FFmpeg` altyapılarından almaktadır.

## ✨ Öne Çıkan Özellikler

* **Modern ve Şık Arayüz:** CustomTkinter ile tasarlanmış, karanlık/aydınlık tema destekli akıcı kullanıcı deneyimi.
* **Gelişmiş İndirme Motoru:** `yt-dlp` altyapısı sayesinde oynatma listeleri (playlist) desteği ve istenilen çözünürlükte (1080p, 720p, Sadece MP3 vb.) indirme imkanı.
* **Toplu Format Dönüştürücü (Batch Processing):** `FFmpeg` ve `FFprobe` entegrasyonu ile birden fazla dosyayı aynı anda seçip saniyelik okuma yapan ilerleme çubuğu eşliğinde mp4, mp3, mkv, gif, wav gibi formatlara çevirme.
* **Akıllı Altyapı Kontrolü:** Uygulama açılışında yt-dlp sürümünü kontrol eder ve eskiyse kullanıcıyı yeni sürüme yönlendirir.
* **Çift Dil Desteği:** Tek tıkla anında değişebilen 🇹🇷 Türkçe ve 🇬🇧 İngilizce (English) dil arayüzü.

## 🛠️ Kullanılan Teknolojiler

* **Dil:** Python 3.x
* **Arayüz (GUI):** CustomTkinter, Tkinter, Pillow
* **Arka Plan Motorları:** yt-dlp (İndirme), FFmpeg & FFprobe (Dönüştürme ve Süre Ölçümü)
* **Paketleme:** PyInstaller

## 🚀 Kurulum ve Kullanım

### Son Kullanıcılar İçin (Kurulumsuz Kullanım)
Uygulamayı herhangi bir Python modülü kurmadan doğrudan kullanmak isterseniz:
1. Sağ taraftaki **Releases** sekmesine gidin.
2. En güncel `Nuklon_Medya_Merkezi.exe` dosyasını indirin.
3. İndirdiğiniz dosyaya çift tıklayarak uygulamayı hemen kullanmaya başlayın.

### Geliştiriciler İçin (Kaynak Koddan Çalıştırma)
Projeyi kendi bilgisayarınızda derlemek veya geliştirmek isterseniz:
1. Depoyu bilgisayarınıza klonlayın:
   ```bash
   git clone [https://github.com/cf6inside/Nuklon-Media-Station.git](https://github.com/cf6inside/Nuklon-Media-Station.git)
