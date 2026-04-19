import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import os
import threading
import subprocess
import sys
import urllib.request
import json
import yt_dlp.version
import webbrowser
from PIL import Image # Resimli logo için eklendi

# --- KENDİ LİNKLERİNİ BURAYA YAPIŞTIR ---
DRIVE_LINK = "https://drive.google.com/drive/u/0/folders/1mU0McXN5MA-fKKzRs0bWV9K9Cp9zL46z"
VIDEO_LINK = "https://youtu.be/1Ee060Gl4GU"

# --- YENİ SİHİRLİ DOSYA YOLU ÇÖZÜCÜ (GÖMÜLÜ DOSYALAR İÇİN) ---
def kaynak_yolunu_bul(dosya_adi):
    """ .exe içine gömülü dosyaların geçici yolunu (MEIPASS) bulur """
    try:
        # PyInstaller çalışırken dosyaları bu geçici yola çıkarır
        temel_yol = sys._MEIPASS
    except Exception:
        # Geliştirme aşamasında (.py olarak) çalışırken normal klasörü kullanır
        temel_yol = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(temel_yol, dosya_adi)

# Yollar artık geçici hayalet klasörden çekilecek
MEVCUT_KLASOR = kaynak_yolunu_bul("") # yt-dlp için klasör yolu
IKON_YOLU = kaynak_yolunu_bul("ikon.ico")
LOGO_YOLU = kaynak_yolunu_bul("logo.jpg")
FFMPEG_YOLU = kaynak_yolunu_bul("ffmpeg.exe")

# --- TEMA VE GENEL AYARLAR ---
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class NuklonApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- PENCERE AYARLARI ---
        self.title("Nüklon Medya İstasyonu V1.6")
        self.geometry("950x650")
        self.minsize(850, 600)
        
        # --- UYGULAMA VE GÜNCELLEME DEĞİŞKENLERİ ---
        self.MEVCUT_SURUM = 1.6
        # version.txt dosyasını okuyacağımız ham (raw) link:
        self.GITHUB_VERSION_URL = "https://raw.githubusercontent.com/cf6inside/Nuklon-Media-Station/main/version.txt"
        # Yeni .exe dosyasını indireceğimiz link (Release sekmesinden çekeceğiz):
        self.GITHUB_EXE_URL = "https://github.com/cf6inside/Nuklon-Media-Station/releases/latest/download/Nuklon_Medya_Merkezi.exe"
        
        if os.path.exists(IKON_YOLU):
            self.iconbitmap(IKON_YOLU)
            
        # Dinamik Renk Paletleri ("Açık Tema Rengi", "Koyu Tema Rengi")
        self.bg_color = ("gray95", "#121212")
        self.card_color = ("gray85", "#1E1E1E")
        self.sidebar_color = ("gray85", "#1A1A1A")
        self.accent_color = "#00D4FF" 
        self.text_main = ("black", "white")
        self.text_muted = ("gray40", "gray60")
        
        self.font_main = ("Roboto", 14)
        self.font_bold = ("Roboto", 15, "bold")
        self.font_title = ("Roboto", 24, "bold")
        
        self.configure(fg_color=self.bg_color)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Değişkenler
        self.secilen_dosya_yolu = ""
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads") # Varsayılan klasör

        # --- ARAYÜZ KURULUMU ---
        self.setup_sidebar()
        self.setup_downloader_frame()
        self.setup_converter_frame()
        self.setup_notes_frame()
        self.setup_support_frame()

        # Başlangıç
        self.select_frame_by_name("indirici")
        # Başlangıç kontrolleri
        self.check_auto_update() # Mevcut yt-dlp kontrolün
        self.check_app_update()  # YENİ: Uygulama güncelleme kontrolümüz

    # ==========================================
    # YAN MENÜ (SIDEBAR)
    # ==========================================
    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1) 

        # Logo Alanı (Resim varsa resmi, yoksa yazıyı yükler)
        if os.path.exists(LOGO_YOLU):
            try:
                img_data = Image.open(LOGO_YOLU)
                aspect_ratio = img_data.height / img_data.width
                new_width = 180
                new_height = int(new_width * aspect_ratio)
                self.logo_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(new_width, new_height))
                self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=self.logo_image, text="")
                self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))
            except Exception:
                self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="NÜKLON\nMedya Merkezi", font=self.font_title, text_color=self.accent_color)
                self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))
        else:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="NÜKLON\nMedya Merkezi", font=self.font_title, text_color=self.accent_color)
            self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        self.btn_indirici = ctk.CTkButton(self.sidebar_frame, text="⬇️ Video İndirici", font=self.font_main, corner_radius=12, fg_color="transparent", text_color=self.text_main, hover_color=("gray70", "gray30"), command=lambda: self.select_frame_by_name("indirici"))
        self.btn_indirici.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_donusturucu = ctk.CTkButton(self.sidebar_frame, text="🔄 Format Dönüştürücü", font=self.font_main, corner_radius=12, fg_color="transparent", text_color=self.text_main, hover_color=("gray70", "gray30"), command=lambda: self.select_frame_by_name("donusturucu"))
        self.btn_donusturucu.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_notlar = ctk.CTkButton(self.sidebar_frame, text="📝 Güncelleme Notları", font=self.font_main, corner_radius=12, fg_color="transparent", text_color=self.text_main, hover_color=("gray70", "gray30"), command=lambda: self.select_frame_by_name("notlar"))
        self.btn_notlar.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_destek = ctk.CTkButton(self.sidebar_frame, text="🆘 Destek / Hakkında", font=self.font_main, corner_radius=12, fg_color="transparent", text_color=self.text_main, hover_color=("gray70", "gray30"), command=lambda: self.select_frame_by_name("destek"))
        self.btn_destek.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.theme_switch = ctk.CTkSwitch(self.sidebar_frame, text="Koyu Tema", font=("Roboto", 12), text_color=self.text_main, command=self.change_theme)
        self.theme_switch.grid(row=7, column=0, padx=20, pady=(10, 10), sticky="w")
        self.theme_switch.select()

        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="Sürüm V1.5 Stable\nSürüm Kontrol Ediliyor...", font=("Roboto", 11), text_color=self.text_muted)
        self.version_label.grid(row=8, column=0, padx=20, pady=(5, 20), sticky="w")
        
        self.btn_update_download = ctk.CTkButton(self.sidebar_frame, text="⬇️ Yeni Sürümü İndir", font=("Roboto", 11, "bold"), fg_color="#ff9800", text_color="white", hover_color="#e68a00", height=25, command=lambda: webbrowser.open(DRIVE_LINK))

    # ==========================================
    # 1. VİDEO İNDİRİCİ
    # ==========================================
    def setup_downloader_frame(self):
        self.frame_indirici = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_indirici.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.frame_indirici, text="Video İndirici", font=self.font_title, text_color=self.text_main).grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")

        self.url_entry = ctk.CTkEntry(self.frame_indirici, placeholder_text="Video veya oynatma listesi URL'si yapıştırın...", font=self.font_main, height=45, corner_radius=12, fg_color=self.card_color, text_color=self.text_main)
        self.url_entry.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        
        self.playlist_var = ctk.BooleanVar(value=False)
        self.check_playlist = ctk.CTkCheckBox(self.frame_indirici, text="Bu link bir oynatma listesi (Tümünü indir)", variable=self.playlist_var, font=self.font_main, text_color=self.text_main)
        self.check_playlist.grid(row=2, column=0, padx=40, pady=5, sticky="w")

        self.btn_check_url = ctk.CTkButton(self.frame_indirici, text="Bağlantıyı Kontrol Et", font=self.font_bold, height=40, corner_radius=12, command=self.check_url_logic)
        self.btn_check_url.grid(row=3, column=0, padx=40, pady=15, sticky="w")

        # --- GİZLİ ALAN: VİDEO BİLGİ KARTI ---
        self.info_card_frame = ctk.CTkFrame(self.frame_indirici, corner_radius=12, fg_color=self.card_color)
        self.info_card_frame.grid_columnconfigure(1, weight=1)
        
        self.lbl_thumbnail = ctk.CTkLabel(self.info_card_frame, text="▶️", font=("Roboto", 40), width=100, height=80, fg_color=("gray70", "gray20"), corner_radius=8)
        self.lbl_thumbnail.grid(row=0, column=0, rowspan=2, padx=15, pady=15)
        
        self.lbl_video_title = ctk.CTkLabel(self.info_card_frame, text="Yükleniyor...", font=self.font_bold, text_color=self.text_main, wraplength=400, justify="left")
        self.lbl_video_title.grid(row=0, column=1, padx=10, pady=(15, 0), sticky="nw")
        
        self.lbl_video_channel = ctk.CTkLabel(self.info_card_frame, text="Kanal: -- | Süre: --", font=self.font_main, text_color=self.text_muted)
        self.lbl_video_channel.grid(row=1, column=1, padx=10, pady=(5, 15), sticky="sw")

        # --- GİZLİ ALAN: İNDİRME SEÇENEKLERİ ---
        self.options_frame = ctk.CTkFrame(self.frame_indirici, fg_color="transparent")
        self.options_frame.grid_columnconfigure(0, weight=1)
        
        # Seçenekler ve İndirme Butonu
        opt_inner = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        opt_inner.grid(row=0, column=0, sticky="w")
        
        self.format_combo = ctk.CTkComboBox(opt_inner, values=["En İyi Kalite (Orijinal)", "1080p", "720p", "480p", "Sadece Ses (MP3)"], font=self.font_main, corner_radius=12, width=200, fg_color=self.card_color, text_color=self.text_main)
        self.format_combo.grid(row=0, column=0, padx=(0, 15), pady=10)
        
        self.btn_start_download = ctk.CTkButton(opt_inner, text="İndirmeyi Başlat", font=self.font_bold, corner_radius=12, fg_color=self.accent_color, text_color="black", hover_color="#00AACC", command=self.start_download_logic)
        self.btn_start_download.grid(row=0, column=1, pady=10)

        # KLASÖR SEÇME ALANI
        path_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        path_frame.grid(row=1, column=0, sticky="w", pady=(5, 15))
        
        ctk.CTkLabel(path_frame, text="Kayıt Yeri:", font=self.font_bold, text_color=self.text_main).grid(row=0, column=0, padx=(0, 10))
        self.lbl_path = ctk.CTkLabel(path_frame, text=self.download_path, font=("Roboto", 12), text_color=self.text_muted, width=250, anchor="w")
        self.lbl_path.grid(row=0, column=1)
        
        self.btn_select_path = ctk.CTkButton(path_frame, text="📁 Klasör Değiştir", font=("Roboto", 12), corner_radius=8, width=120, fg_color=self.card_color, text_color=self.text_main, hover_color=("gray70", "gray30"), command=self.select_download_path)
        self.btn_select_path.grid(row=0, column=2, padx=10)

        # İlerleme Çubuğu
        self.progress_bar = ctk.CTkProgressBar(self.options_frame, corner_radius=12, height=10, progress_color=self.accent_color)
        self.progress_bar.set(0)
        self.lbl_progress_details = ctk.CTkLabel(self.options_frame, text="Bekleniyor...", font=("Roboto", 12), text_color=self.text_muted)

    def select_download_path(self):
        klasor = filedialog.askdirectory(title="İndirme Klasörünü Seçin")
        if klasor:
            self.download_path = klasor
            gosterilen = klasor if len(klasor) < 35 else "..." + klasor[-32:]
            self.lbl_path.configure(text=gosterilen)

    def check_url_logic(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Eksik", "Lütfen bir link girin!")
            return
            
        self.btn_check_url.configure(text="Bilgiler Çekiliyor...", state="disabled")
        threading.Thread(target=self._fetch_video_info, args=(url,), daemon=True).start()

    def _fetch_video_info(self, url):
        try:
            ydl_opts = {'quiet': True, 'noplaylist': not self.playlist_var.get()}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            title = info.get('title', 'Bilinmeyen Başlık')
            channel = info.get('uploader', 'Bilinmeyen Kanal')
            duration = info.get('duration_string', '--:--')
            
            if 'entries' in info: 
                title = f"[Oynatma Listesi] {title}"
                channel = f"{len(info['entries'])} Video"
            
            self.after(0, lambda: self.lbl_video_title.configure(text=title))
            self.after(0, lambda: self.lbl_video_channel.configure(text=f"Kanal: {channel}  |  Süre: {duration}"))
            
            self.after(0, lambda: self.info_card_frame.grid(row=4, column=0, padx=40, pady=20, sticky="ew"))
            self.after(0, lambda: self.options_frame.grid(row=5, column=0, padx=40, pady=0, sticky="ew"))
            self.after(0, lambda: self.progress_bar.grid_forget())
            self.after(0, lambda: self.lbl_progress_details.grid_forget())
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Hata", f"Video bilgileri alınamadı:\n{str(e)[:100]}"))
        finally:
            self.after(0, lambda: self.btn_check_url.configure(text="Bağlantıyı Kontrol Et", state="normal"))

    def start_download_logic(self):
        url = self.url_entry.get()
        secilen = self.format_combo.get()
        is_playlist = self.playlist_var.get()
        
        self.btn_start_download.configure(state="disabled")
        self.progress_bar.grid(row=2, column=0, sticky="ew", pady=(5, 5))
        self.lbl_progress_details.grid(row=3, column=0, sticky="w")
        self.progress_bar.set(0)
        self.lbl_progress_details.configure(text="İndirme başlatılıyor...", text_color=self.text_muted)
        
        threading.Thread(target=self._download_thread, args=(url, secilen, is_playlist), daemon=True).start()

    def _download_thread(self, url, secilen_cozunurluk, playlist_mi):
        try:
            # Artık kullanıcının seçtiği klasörü kullanıyoruz
            indirme_klasoru = self.download_path
            
            if secilen_cozunurluk == "En İyi Kalite (Orijinal)": format_ayari = 'bestvideo+bestaudio/best'
            elif secilen_cozunurluk == "1080p": format_ayari = 'bestvideo[height<=1080]+bestaudio/best'
            elif secilen_cozunurluk == "720p": format_ayari = 'bestvideo[height<=720]+bestaudio/best'
            elif secilen_cozunurluk == "480p": format_ayari = 'bestvideo[height<=480]+bestaudio/best'
            elif secilen_cozunurluk == "Sadece Ses (MP3)": format_ayari = 'bestaudio/best'
            
            def ilerleme_kancasi(d):
                if d['status'] == 'downloading':
                    yuzde_metni = d.get('_percent_str', '0.0%').strip()
                    hiz = d.get('_speed_str', '0 B/s').strip()
                    kalan = d.get('_eta_str', '--:--').strip()
                    
                    try:
                        temiz_sayi = float(yuzde_metni.replace('%', '')) / 100.0
                        self.after(0, lambda: self.progress_bar.set(temiz_sayi))
                    except: pass
                    
                    self.after(0, lambda: self.lbl_progress_details.configure(text=f"Hız: {hiz}  |  Kalan: {kalan}  |  Durum: {yuzde_metni}"))
                    
                elif d['status'] == 'finished':
                    self.after(0, lambda: self.lbl_progress_details.configure(text="İndirme bitti, birleştiriliyor... Lütfen bekleyin."))
                    self.after(0, lambda: self.progress_bar.set(1.0))

            ydl_opts = {
                'outtmpl': f'{indirme_klasoru}/%(playlist_index)s - %(title)s.%(ext)s' if playlist_mi else f'{indirme_klasoru}/%(title)s.%(ext)s',
                'format': format_ayari,
                'noplaylist': not playlist_mi,
                'nocolor': True,
                'progress_hooks': [ilerleme_kancasi],
                'ffmpeg_location': MEVCUT_KLASOR 
            }
            if secilen_cozunurluk == "Sadece Ses (MP3)":
                ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.after(0, lambda: self.lbl_progress_details.configure(text=f"✅ İşlem Tamamlandı! Dosya kaydedildi.", text_color="green"))
            
        except Exception as e:
            self.after(0, lambda: self.lbl_progress_details.configure(text=f"❌ Hata: {str(e)[:50]}...", text_color="red"))
        finally:
            self.after(0, lambda: self.btn_start_download.configure(state="normal"))

    # ==========================================
    # 2. FORMAT DÖNÜŞTÜRÜCÜ
    # ==========================================
    def setup_converter_frame(self):
        self.frame_donusturucu = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_donusturucu.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.frame_donusturucu, text="Format Dönüştürücü", font=self.font_title, text_color=self.text_main).grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")

        self.file_card = ctk.CTkFrame(self.frame_donusturucu, corner_radius=12, fg_color=self.card_color)
        self.file_card.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        
        self.btn_select_file = ctk.CTkButton(self.file_card, text="📁 Bilgisayardan Dosya Seç", font=self.font_bold, height=45, corner_radius=12, command=self.select_file_logic)
        self.btn_select_file.pack(pady=(20, 10))
        
        self.lbl_selected_file = ctk.CTkLabel(self.file_card, text="Henüz bir dosya seçilmedi.", text_color=self.text_muted)
        self.lbl_selected_file.pack(pady=(0, 20))

        self.conv_options = ctk.CTkFrame(self.frame_donusturucu, fg_color="transparent")
        self.conv_options.grid(row=2, column=0, padx=40, pady=20, sticky="ew")
        
        ctk.CTkLabel(self.conv_options, text="Hedef Format:", font=self.font_bold, text_color=self.text_main).grid(row=0, column=0, padx=(0, 10), sticky="w")
        self.conv_combo = ctk.CTkComboBox(self.conv_options, values=["mp3", "mp4", "wav", "avi", "mkv", "gif", "flac", "aac", "ogg", "mov"], font=self.font_main, corner_radius=12, fg_color=self.card_color, text_color=self.text_main)
        self.conv_combo.grid(row=0, column=1, padx=10)
        
        self.btn_convert = ctk.CTkButton(self.conv_options, text="Dönüştür", font=self.font_bold, fg_color=self.accent_color, text_color="black", hover_color="#00AACC", corner_radius=12, command=self.start_convert_logic)
        self.btn_convert.grid(row=0, column=2, padx=10)

        self.conv_progress = ctk.CTkProgressBar(self.frame_donusturucu, corner_radius=12, height=10, progress_color=self.accent_color)
        self.conv_progress.set(0)
        self.lbl_conv_status = ctk.CTkLabel(self.frame_donusturucu, text="", font=("Roboto", 12))

    def select_file_logic(self):
        yol = filedialog.askopenfilename(title="Dönüştürülecek Dosyayı Seçin")
        if yol:
            self.secilen_dosya_yolu = yol
            isim = os.path.basename(yol)
            self.lbl_selected_file.configure(text=f"Seçilen: {isim}", text_color=self.text_main)

    def start_convert_logic(self):
        if not self.secilen_dosya_yolu:
            messagebox.showwarning("Eksik", "Lütfen önce bir dosya seçin!")
            return
        if not os.path.exists(FFMPEG_YOLU):
            messagebox.showerror("Hata", "ffmpeg.exe programın yanında bulunamadı!")
            return

        hedef = self.conv_combo.get()
        self.btn_convert.configure(state="disabled")
        
        self.conv_progress.grid(row=3, column=0, padx=40, pady=(10, 5), sticky="ew")
        self.lbl_conv_status.grid(row=4, column=0, padx=40, sticky="w")
        self.conv_progress.set(0)
        self.lbl_conv_status.configure(text="Dönüştürme başlatılıyor...", text_color=self.text_muted)
        
        threading.Thread(target=self._convert_thread, args=(hedef,), daemon=True).start()

    def _convert_thread(self, hedef_format):
        try:
            klasor = os.path.dirname(self.secilen_dosya_yolu)
            eski_isim = os.path.splitext(os.path.basename(self.secilen_dosya_yolu))[0]
            yeni_yol = os.path.join(klasor, f"{eski_isim}_donusturuldu.{hedef_format}")
            
            komut = [FFMPEG_YOLU, "-y", "-i", self.secilen_dosya_yolu, yeni_yol]
            
            gizleme = subprocess.STARTUPINFO()
            gizleme.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            process = subprocess.Popen(komut, stderr=subprocess.PIPE, universal_newlines=True, startupinfo=gizleme)
            toplam_sure_sn = 0
            
            for satir in process.stderr:
                if "Duration" in satir and toplam_sure_sn == 0:
                    try:
                        sure_str = satir.split("Duration:")[1].split(",")[0].strip()
                        h, m, s = sure_str.split(':')
                        toplam_sure_sn = int(h)*3600 + int(m)*60 + float(s)
                    except: pass
                
                if "time=" in satir and toplam_sure_sn > 0:
                    try:
                        zaman_str = satir.split("time=")[1].split(" ")[0].strip()
                        h, m, s = zaman_str.split(':')
                        suanki_sn = int(h)*3600 + int(m)*60 + float(s)
                        yuzde = min((suanki_sn / toplam_sure_sn), 1.0)
                        
                        self.after(0, lambda y=yuzde: self.conv_progress.set(y))
                        self.after(0, lambda y=yuzde: self.lbl_conv_status.configure(text=f"İşleniyor: %{int(y*100)}", text_color=self.text_main))
                    except: pass
                        
            process.wait()
            
            if process.returncode == 0:
                self.after(0, lambda: self.conv_progress.set(1.0))
                self.after(0, lambda: self.lbl_conv_status.configure(text="✅ Dönüştürme Tamamlandı! Orijinal dosyanın yanına kaydedildi.", text_color="green"))
            else:
                raise Exception("Bilinmeyen FFmpeg hatası.")
                
        except Exception as e:
             self.after(0, lambda: self.lbl_conv_status.configure(text=f"❌ Hata oluştu: {str(e)[:50]}", text_color="red"))
        finally:
             self.after(0, lambda: self.btn_convert.configure(state="normal"))

    # ==========================================
    # 3. GÜNCELLEME NOTLARI
    # ==========================================
    def setup_notes_frame(self):
        self.frame_notlar = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_notlar.grid_columnconfigure(0, weight=1)
        self.frame_notlar.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_notlar, text="Güncelleme Notları", font=self.font_title, text_color=self.text_main).grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")
        
        self.textbox_notlar = ctk.CTkTextbox(self.frame_notlar, font=self.font_main, corner_radius=12, fg_color=self.card_color, text_color=self.text_main)
        self.textbox_notlar.grid(row=1, column=0, padx=40, pady=(0, 40), sticky="nsew")
        
        metin = """=== NÜKLON MEDYA İSTASYONU V1.6 ===
yt-dlp tabanlı olarak Google Gemini Yardımı ile hazırlanmıştır. Can Ö. (2026)

YENİLİKLER (V1.6 - ffmpeg Entegrasyonu):
+ ffmpeg ve uygulama entegre edildi. Artık aynı klasörde iki farklı uygulama barındırmaya gerek yok.
------------------------------------------------
YENİLİKLER (V1.5 - MODERN UI YÜKSELTMESİ):
+ Arayüz, modern nesne yönelimli (OOP) mimariyle sıfırdan yazıldı.
+ İndirilen dosyaların nereye kaydedileceğini seçme imkanı (Klasör Seçimi) eklendi.
+ Uygulama logosu resimli yeni versiyonuyla (Nüklon Medya Merkezi) değiştirildi.
+ Açık ve Koyu Tema arasındaki geçişteki renk uyumsuzlukları giderildi.
+ İndirme işleminde "Aşamalı Gösterim" (Progressive Disclosure) uygulandı. Video küçük resmi, başlığı ve süresi link onayından sonra ekrana gelir.
------------------------------------------------
YENİLİKLER (11.04.2026) (V1.4):
- Kullanım kolaylığı için "Destek" sekmesi oluşturuldu.
- Destek sekmesine Google Drive ve YouTube Video rehber linkleri eklendi.
- Arka plan güncelleme motoru, yeni bir sürüm bulduğunda artık direkt olarak indirme butonu çıkartıyor.
- Kullanıcıların gerekli güncellemelerden haberdar olması için "Akıllı Sürüm Kontrol" sistemi eklendi.
- Program artık açılışta güncel yt-dlp sürümünü kontrol edip uyarı veriyor.
------------------------------------------------
V1.3 - Akıllı Sürüm Kontrolü
- Program açılışta güncel yt-dlp sürümünü kontrol edip uyarı veriyor.
------------------------------------------------
V1.2 - Tasarım Güncellemesi
- Video linki giriş kutusuna "Sağ Tık (Kes/Kopyala/Yapıştır)" menüsü eklendi.
- "Koyu Tema (Dark Mode)" motoru sekmelerindeki hata düzeltildi.
------------------------------------------------
V1.1 - Format Dönüşüm Aracı
- Çok formatlı dönüştürücü motoru kuruldu.
- Koyu Tema Eklendi
------------------------------------------------
V1.0 - Temel Sürüm
- YouTube'dan video/müzik indirme altyapısı kuruldu.

"""
        self.textbox_notlar.insert("0.0", metin)
        self.textbox_notlar.configure(state="disabled") 

    # ==========================================
    # 4. DESTEK SEKME
    # ==========================================
    def setup_support_frame(self):
        self.frame_destek = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_destek.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.frame_destek, text="Destek & Hakkında", font=self.font_title, text_color=self.text_main).grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")
        
        card = ctk.CTkFrame(self.frame_destek, corner_radius=12, fg_color=self.card_color)
        card.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        
        ctk.CTkLabel(card, text="Nüklon Medya Merkezi'ni kullanırken yardıma ihtiyacınız olursa\nveya yeni bir güncelleme geldiğini görürseniz aşağıdaki bağlantıları kullanabilirsiniz.", justify="center", font=self.font_main, text_color=self.text_main).pack(pady=30, padx=20)
        
        ctk.CTkButton(card, text="📁 Yeni Sürümü İndir (Google Drive)", font=self.font_bold, height=45, fg_color="#4285F4", hover_color="#2c6cd6", corner_radius=12, command=lambda: webbrowser.open(DRIVE_LINK)).pack(pady=10)
        ctk.CTkButton(card, text="▶️ Kullanım Videosunu İzle (YouTube)", font=self.font_bold, height=45, fg_color="#FF0000", hover_color="#cc0000", corner_radius=12, command=lambda: webbrowser.open(VIDEO_LINK)).pack(pady=(10, 30))

    # ==========================================
    # UI VE SÜRÜM KONTROL METOTLARI
    # ==========================================
    def select_frame_by_name(self, name):
        self.btn_indirici.configure(fg_color=("gray75", "gray25") if name == "indirici" else "transparent")
        self.btn_donusturucu.configure(fg_color=("gray75", "gray25") if name == "donusturucu" else "transparent")
        self.btn_notlar.configure(fg_color=("gray75", "gray25") if name == "notlar" else "transparent")
        self.btn_destek.configure(fg_color=("gray75", "gray25") if name == "destek" else "transparent")

        self.frame_indirici.grid_forget()
        self.frame_donusturucu.grid_forget()
        self.frame_notlar.grid_forget()
        self.frame_destek.grid_forget()

        if name == "indirici": self.frame_indirici.grid(row=0, column=1, sticky="nsew")
        elif name == "donusturucu": self.frame_donusturucu.grid(row=0, column=1, sticky="nsew")
        elif name == "notlar": self.frame_notlar.grid(row=0, column=1, sticky="nsew")
        elif name == "destek": self.frame_destek.grid(row=0, column=1, sticky="nsew")

    def change_theme(self):
        if self.theme_switch.get() == 1: 
            ctk.set_appearance_mode("Dark")
        else: 
            ctk.set_appearance_mode("Light")

    def check_auto_update(self):
        threading.Thread(target=self._auto_update_thread, daemon=True).start()
    # ==========================================
    # OTONOM GÜNCELLEME (AUTO-UPDATER) SİSTEMİ
    # ==========================================
    def check_app_update(self):
        """Uygulamanın sürümünü arka planda kontrol eder."""
        threading.Thread(target=self._app_update_thread, daemon=True).start()

    def _app_update_thread(self):
        try:
            # GitHub'daki version.txt dosyasını oku
            req = urllib.request.Request(self.GITHUB_VERSION_URL)
            with urllib.request.urlopen(req, timeout=5) as response:
                en_guncel_surum_str = response.read().decode('utf-8').strip()
                en_guncel_surum = float(en_guncel_surum_str)
            
            # Eğer GitHub'daki sürüm bizdekinden büyükse
            if en_guncel_surum > self.MEVCUT_SURUM:
                self.after(0, lambda: self._show_update_dialog(en_guncel_surum_str))
        except Exception as e:
            print("Uygulama güncelleme kontrolü başarısız:", e)

    def _show_update_dialog(self, yeni_surum):
        """Yeni sürüm bulunduğunda kullanıcıya sorar."""
        cevap = messagebox.askyesno(
            "Yeni Sürüm Bulundu!", 
            f"Nüklon Medya Merkezi V{yeni_surum} yayınlandı!\n\nŞu anki sürümünüz: V{self.MEVCUT_SURUM}\n\nŞimdi arka planda indirilip güncellenmesini ister misiniz?"
        )
        if cevap:
            threading.Thread(target=self._download_and_apply_update, daemon=True).start()

    def _download_and_apply_update(self):
        """Yeni sürümü indirir ve Nöbet Değişimi betiğini çalıştırır."""
        try:
            self.after(0, lambda: self.version_label.configure(text="Yeni sürüm indiriliyor... (Lütfen programı kapatmayın)", text_color="#ff9800"))
            
            yeni_exe_yolu = "Nuklon_Yeni.exe"
            
            # 1. Yeni EXE'yi indir
            urllib.request.urlretrieve(self.GITHUB_EXE_URL, yeni_exe_yolu)
            
            self.after(0, lambda: self.version_label.configure(text="İndirme tamamlandı! Yeniden başlatılıyor...", text_color="green"))
            
            # 2. Nöbet Değişimi (.bat) dosyasını oluştur ve çalıştır
            self._create_and_run_updater_bat()
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Güncelleme Hatası", f"Dosya indirilemedi. Lütfen internet bağlantınızı kontrol edin.\n\nDetay: {e}"))
            self.after(0, lambda: self.version_label.configure(text=f"Sürüm V{self.MEVCUT_SURUM}", text_color=self.text_muted))

    def _create_and_run_updater_bat(self):
        """Eski programı silip yenisini başlatan geçici bir .bat oluşturur."""
        bat_icerik = """@echo off
:: Mevcut programin kapanmasi icin 2 saniye bekle
timeout /t 2 /nobreak >nul

:: Eski programi sil
del "Nuklon Medya Merkezi.exe"

:: Yeni programin adini orijinale cevir
ren "Nuklon_Yeni.exe" "Nuklon Medya Merkezi.exe"

:: Yeni programi baslat
start "" "Nuklon Medya Merkezi.exe"

:: Bu bat dosyasini (kendini) yok et
del "%~f0"
"""
        bat_yolu = "guncelleme_yardimcisi.bat"
        with open(bat_yolu, "w", encoding="utf-8") as f:
            f.write(bat_icerik)
            
        # Bat dosyasını konsol penceresi göstermeden (gizli) çalıştır
        gizleme = subprocess.STARTUPINFO()
        gizleme.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen([bat_yolu], startupinfo=gizleme)
        
        # Mevcut programı anında kapat
        os._exit(0)
    def _auto_update_thread(self):
        try:
            req = urllib.request.Request("https://pypi.org/pypi/yt-dlp/json")
            with urllib.request.urlopen(req, timeout=5) as response:
                veri = json.loads(response.read())
                en_guncel = veri["info"]["version"]
                
            mevcut = yt_dlp.version.__version__
            m_list = [int(s) for s in mevcut.split('.')]
            g_list = [int(s) for s in en_guncel.split('.')]
            
            if m_list < g_list:
                self.after(0, lambda: self.version_label.configure(text="⚠️ Yeni Altyapı Çıktı!", text_color="#ff9800"))
                self.after(0, lambda: self.btn_update_download.grid(row=9, column=0, padx=20, pady=(0, 20), sticky="w"))
            else:
                self.after(0, lambda: self.version_label.configure(text=f"✅ Altyapı Güncel ({mevcut})", text_color="green"))
        except:
            self.after(0, lambda: self.version_label.configure(text="⚠️ Sürüm Kontrolü Başarısız", text_color="orange"))

if __name__ == "__main__":
    app = NuklonApp()
    app.mainloop()