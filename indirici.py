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
from PIL import Image 

# --- GÜNCEL LİNKLER ---
GITHUB_LINK = "https://github.com/cf6inside/Nuklon-Media-Station"
VIDEO_LINK = "https://youtu.be/1Ee060Gl4GU"

def kaynak_yolunu_bul(dosya_adi):
    """ .exe içine gömülü dosyaların geçici yolunu (MEIPASS) bulur """
    try:
        temel_yol = sys._MEIPASS
    except Exception:
        temel_yol = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(temel_yol, dosya_adi)

# Yollar
MEVCUT_KLASOR = kaynak_yolunu_bul("") 
IKON_YOLU = kaynak_yolunu_bul("ikon.ico")
LOGO_YOLU = kaynak_yolunu_bul("logo.jpg")
FFMPEG_YOLU = kaynak_yolunu_bul("ffmpeg.exe")

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class NuklonApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- UYGULAMA VE GÜNCELLEME DEĞİŞKENLERİ ---
        self.MEVCUT_SURUM = 1.7  # Sürümü V1.7 yaptık!
        self.GITHUB_VERSION_URL = "https://raw.githubusercontent.com/cf6inside/Nuklon-Media-Station/main/version.txt"
        self.GITHUB_EXE_URL = "https://github.com/cf6inside/Nuklon-Media-Station/releases/latest/download/Nuklon_Medya_Merkezi.exe"
        
        # --- DİL SİSTEMİ (Sözlük Yapısı) ---
        self.current_lang = "tr"
        self.texts = {
            "tr": {
                "title": "Nüklon Medya İstasyonu V1.7",
                "sidebar_download": "⬇️ Video İndirici",
                "sidebar_converter": "🔄 Format Dönüştürücü",
                "sidebar_notes": "📝 Güncelleme Notları",
                "sidebar_support": "🆘 Destek / Hakkında",
                "lang_switch": "English Language",
                "check_url": "Bağlantıyı Kontrol Et",
                "start_download": "İndirmeyi Başlat",
                "save_path": "Kayıt Yeri:",
                "change_path": "📁 Klasör Değiştir",
                "support_text": "Yardıma ihtiyacınız olursa aşağıdaki bağlantıları kullanabilirsiniz.",
                "github_btn": "🌐 GitHub Sayfası (Yeni Sürüm)",
                "status_ready": "Bekleniyor...",
                "update_found": "Yeni Sürüm Bulundu!",
                "update_msg": "Nüklon Medya Merkezi V{} yayınlandı! Şimdi güncellensin mi?",
                "placeholder_url": "Video veya oynatma listesi URL'si yapıştırın...",
                "chk_playlist": "Bu link bir oynatma listesi",
                "conv_title": "Format Dönüştürücü",
                "conv_select_file": "📁 Bilgisayardan Dosya Seç",
                "conv_target": "Hedef Format:",
                "conv_btn": "Dönüştür"
            },
            "en": {
                "title": "Nuklon Media Station V1.7",
                "sidebar_download": "⬇️ Video Downloader",
                "sidebar_converter": "🔄 Format Converter",
                "sidebar_notes": "📝 Release Notes",
                "sidebar_support": "🆘 Support / About",
                "lang_switch": "Türkçe Dil",
                "check_url": "Check Link",
                "start_download": "Start Download",
                "save_path": "Save Path:",
                "change_path": "📁 Change Folder",
                "support_text": "If you need help, you can use the links below.",
                "github_btn": "🌐 GitHub Page (New Version)",
                "status_ready": "Ready...",
                "update_found": "New Version Found!",
                "update_msg": "Nuklon Media Station V{} is available! Update now?",
                "placeholder_url": "Paste video or playlist URL here...",
                "chk_playlist": "This link is a playlist",
                "conv_title": "Format Converter",
                "conv_select_file": "📁 Select File From Computer",
                "conv_target": "Target Format:",
                "conv_btn": "Convert"
            }
        }

        # Pencere Ayarları
        self.title(self.texts[self.current_lang]["title"])
        self.geometry("950x650")
        self.minsize(850, 600)
        if os.path.exists(IKON_YOLU):
            self.iconbitmap(IKON_YOLU)
            
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

        self.secilen_dosya_yolu = ""
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")

        # --- ARAYÜZ KURULUMU ---
        self.setup_sidebar()
        self.setup_downloader_frame()
        self.setup_converter_frame()
        self.setup_notes_frame()
        self.setup_support_frame()

        self.select_frame_by_name("indirici")
        self.check_auto_update()
        self.check_app_update()

    def toggle_language(self):
        """Dili değiştirir ve tüm UI metinlerini günceller."""
        self.current_lang = "en" if self.current_lang == "tr" else "tr"
        self.update_ui_texts()

    def update_ui_texts(self):
        """UI üzerindeki tüm metinleri seçili dile göre yeniler."""
        t = self.texts[self.current_lang]
        self.title(t["title"])
        self.btn_indirici.configure(text=t["sidebar_download"])
        self.btn_donusturucu.configure(text=t["sidebar_converter"])
        self.btn_notlar.configure(text=t["sidebar_notes"])
        self.btn_destek.configure(text=t["sidebar_support"])
        self.lang_btn.configure(text=t["lang_switch"])
        
        # İndirici Sekmesi
        self.lbl_indirici_title.configure(text=t["sidebar_download"].replace("⬇️ ", ""))
        self.url_entry.configure(placeholder_text=t["placeholder_url"])
        self.check_playlist.configure(text=t["chk_playlist"])
        self.btn_check_url.configure(text=t["check_url"])
        self.btn_start_download.configure(text=t["start_download"])
        self.lbl_path_title.configure(text=t["save_path"])
        self.btn_select_path.configure(text=t["change_path"])
        
        # Dönüştürücü Sekmesi
        self.lbl_conv_title.configure(text=t["conv_title"])
        self.btn_select_file.configure(text=t["conv_select_file"])
        self.lbl_target_format.configure(text=t["conv_target"])
        self.btn_convert.configure(text=t["conv_btn"])

        # Destek Sekmesi
        self.lbl_destek_title.configure(text=t["sidebar_support"])
        self.support_info_lbl.configure(text=t["support_text"])
        self.github_nav_btn.configure(text=t["github_btn"])

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1) 

        if os.path.exists(LOGO_YOLU):
            try:
                img_data = Image.open(LOGO_YOLU)
                self.logo_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(180, 100))
                self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=self.logo_image, text="")
                self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))
            except: pass

        self.btn_indirici = ctk.CTkButton(self.sidebar_frame, text=self.texts[self.current_lang]["sidebar_download"], font=self.font_main, corner_radius=12, fg_color="transparent", text_color=self.text_main, hover_color=("gray70", "gray30"), command=lambda: self.select_frame_by_name("indirici"))
        self.btn_indirici.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.btn_donusturucu = ctk.CTkButton(self.sidebar_frame, text=self.texts[self.current_lang]["sidebar_converter"], font=self.font_main, corner_radius=12, fg_color="transparent", text_color=self.text_main, hover_color=("gray70", "gray30"), command=lambda: self.select_frame_by_name("donusturucu"))
        self.btn_donusturucu.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.btn_notlar = ctk.CTkButton(self.sidebar_frame, text=self.texts[self.current_lang]["sidebar_notes"], font=self.font_main, corner_radius=12, fg_color="transparent", text_color=self.text_main, hover_color=("gray70", "gray30"), command=lambda: self.select_frame_by_name("notlar"))
        self.btn_notlar.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.btn_destek = ctk.CTkButton(self.sidebar_frame, text=self.texts[self.current_lang]["sidebar_support"], font=self.font_main, corner_radius=12, fg_color="transparent", text_color=self.text_main, hover_color=("gray70", "gray30"), command=lambda: self.select_frame_by_name("destek"))
        self.btn_destek.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        # DİL DEĞİŞTİRME BUTONU
        self.lang_btn = ctk.CTkButton(self.sidebar_frame, text=self.texts[self.current_lang]["lang_switch"], font=("Roboto", 12), fg_color=self.card_color, text_color=self.text_main, command=self.toggle_language)
        self.lang_btn.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.theme_switch = ctk.CTkSwitch(self.sidebar_frame, text="Koyu Tema", font=("Roboto", 12), command=self.change_theme)
        self.theme_switch.grid(row=7, column=0, padx=20, pady=10, sticky="w")
        self.theme_switch.select()

        self.version_label = ctk.CTkLabel(self.sidebar_frame, text=f"Sürüm V{self.MEVCUT_SURUM} Stable", font=("Roboto", 11), text_color=self.text_muted)
        self.version_label.grid(row=8, column=0, padx=20, pady=(5, 20), sticky="w")
        
        self.btn_update_download = ctk.CTkButton(self.sidebar_frame, text="⬇️ Yeni Sürümü İndir", font=("Roboto", 11, "bold"), fg_color="#ff9800", height=25, command=lambda: webbrowser.open(GITHUB_LINK))

    def setup_downloader_frame(self):
        self.frame_indirici = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_indirici.grid_columnconfigure(0, weight=1)
        t = self.texts[self.current_lang]

        self.lbl_indirici_title = ctk.CTkLabel(self.frame_indirici, text=t["sidebar_download"].replace("⬇️ ", ""), font=self.font_title)
        self.lbl_indirici_title.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")

        self.url_entry = ctk.CTkEntry(self.frame_indirici, placeholder_text=t["placeholder_url"], font=self.font_main, height=45, corner_radius=12, fg_color=self.card_color)
        self.url_entry.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        
        self.playlist_var = ctk.BooleanVar(value=False)
        self.check_playlist = ctk.CTkCheckBox(self.frame_indirici, text=t["chk_playlist"], variable=self.playlist_var, font=self.font_main)
        self.check_playlist.grid(row=2, column=0, padx=40, pady=5, sticky="w")

        self.btn_check_url = ctk.CTkButton(self.frame_indirici, text=t["check_url"], font=self.font_bold, height=40, corner_radius=12, command=self.check_url_logic)
        self.btn_check_url.grid(row=3, column=0, padx=40, pady=15, sticky="w")

        self.info_card_frame = ctk.CTkFrame(self.frame_indirici, corner_radius=12, fg_color=self.card_color)
        self.info_card_frame.grid_columnconfigure(1, weight=1)
        
        self.lbl_thumbnail = ctk.CTkLabel(self.info_card_frame, text="▶️", font=("Roboto", 40), width=100, height=80, fg_color=("gray70", "gray20"), corner_radius=8)
        self.lbl_thumbnail.grid(row=0, column=0, rowspan=2, padx=15, pady=15)
        
        self.lbl_video_title = ctk.CTkLabel(self.info_card_frame, text="...", font=self.font_bold, wraplength=400, justify="left")
        self.lbl_video_title.grid(row=0, column=1, padx=10, pady=(15, 0), sticky="nw")
        
        self.lbl_video_channel = ctk.CTkLabel(self.info_card_frame, text="...", font=self.font_main, text_color=self.text_muted)
        self.lbl_video_channel.grid(row=1, column=1, padx=10, pady=(5, 15), sticky="sw")

        self.options_frame = ctk.CTkFrame(self.frame_indirici, fg_color="transparent")
        self.options_frame.grid_columnconfigure(0, weight=1)
        
        opt_inner = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        opt_inner.grid(row=0, column=0, sticky="w")
        
        self.format_combo = ctk.CTkComboBox(opt_inner, values=["En İyi Kalite (Orijinal)", "1080p", "720p", "480p", "Sadece Ses (MP3)"], font=self.font_main, width=200)
        self.format_combo.grid(row=0, column=0, padx=(0, 15), pady=10)
        
        self.btn_start_download = ctk.CTkButton(opt_inner, text=t["start_download"], font=self.font_bold, fg_color=self.accent_color, text_color="black", command=self.start_download_logic)
        self.btn_start_download.grid(row=0, column=1, pady=10)

        path_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        path_frame.grid(row=1, column=0, sticky="w", pady=(5, 15))
        
        self.lbl_path_title = ctk.CTkLabel(path_frame, text=t["save_path"], font=self.font_bold)
        self.lbl_path_title.grid(row=0, column=0, padx=(0, 10))
        self.lbl_path = ctk.CTkLabel(path_frame, text=self.download_path, font=("Roboto", 12), text_color=self.text_muted, width=250, anchor="w")
        self.lbl_path.grid(row=0, column=1)
        
        self.btn_select_path = ctk.CTkButton(path_frame, text=t["change_path"], font=("Roboto", 12), width=120, command=self.select_download_path)
        self.btn_select_path.grid(row=0, column=2, padx=10)

        self.progress_bar = ctk.CTkProgressBar(self.options_frame, corner_radius=12, height=10, progress_color=self.accent_color)
        self.progress_bar.set(0)
        self.lbl_progress_details = ctk.CTkLabel(self.options_frame, text=t["status_ready"], font=("Roboto", 12), text_color=self.text_muted)

    def setup_converter_frame(self):
        self.frame_donusturucu = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_donusturucu.grid_columnconfigure(0, weight=1)
        t = self.texts[self.current_lang]

        self.lbl_conv_title = ctk.CTkLabel(self.frame_donusturucu, text=t["conv_title"], font=self.font_title)
        self.lbl_conv_title.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")

        self.file_card = ctk.CTkFrame(self.frame_donusturucu, corner_radius=12, fg_color=self.card_color)
        self.file_card.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        
        self.btn_select_file = ctk.CTkButton(self.file_card, text=t["conv_select_file"], font=self.font_bold, height=45, command=self.select_file_logic)
        self.btn_select_file.pack(pady=(20, 10))
        
        self.lbl_selected_file = ctk.CTkLabel(self.file_card, text="...", text_color=self.text_muted)
        self.lbl_selected_file.pack(pady=(0, 20))

        self.conv_options = ctk.CTkFrame(self.frame_donusturucu, fg_color="transparent")
        self.conv_options.grid(row=2, column=0, padx=40, pady=20, sticky="ew")
        
        self.lbl_target_format = ctk.CTkLabel(self.conv_options, text=t["conv_target"], font=self.font_bold)
        self.lbl_target_format.grid(row=0, column=0, padx=(0, 10), sticky="w")
        self.conv_combo = ctk.CTkComboBox(self.conv_options, values=["mp3", "mp4", "wav", "avi", "mkv", "gif", "flac"], font=self.font_main)
        self.conv_combo.grid(row=0, column=1, padx=10)
        
        self.btn_convert = ctk.CTkButton(self.conv_options, text=t["conv_btn"], font=self.font_bold, fg_color=self.accent_color, text_color="black", command=self.start_convert_logic)
        self.btn_convert.grid(row=0, column=2, padx=10)

        self.conv_progress = ctk.CTkProgressBar(self.frame_donusturucu, corner_radius=12, height=10, progress_color=self.accent_color)
        self.conv_progress.set(0)
        self.lbl_conv_status = ctk.CTkLabel(self.frame_donusturucu, text="", font=("Roboto", 12))

    def setup_notes_frame(self):
        self.frame_notlar = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_notlar.grid_columnconfigure(0, weight=1)
        self.frame_notlar.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_notlar, text=self.texts[self.current_lang]["sidebar_notes"], font=self.font_title).grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")
        
        self.textbox_notlar = ctk.CTkTextbox(self.frame_notlar, font=self.font_main, corner_radius=12, fg_color=self.card_color)
        self.textbox_notlar.grid(row=1, column=0, padx=40, pady=(0, 40), sticky="nsew")
        
        metin = f"""=== NÜKLON MEDYA İSTASYONU V1.7 ===
YENİLİKLER (V1.7):
+ İngilizce Dil Seçeneği (English Language Support) eklendi.
+ Google Drive bağlantıları tamamen GitHub üzerine taşındı.
+ Otonom güncelleme sistemi V1.7 ile stabilize edildi.
------------------------------------------------
V1.6 - Otonom Güncelleme & GitHub Entegrasyonu:
+ Uygulamaya otonom güncelleme (Auto-Updater) motoru eklendi.
+ Proje GitHub Releases üzerine taşındı.
------------------------------------------------
V1.5 - Modern Nesne Yönelimli Mimari
+ Arayüz tamamen class yapısıyla (OOP) sıfırdan kodlandı.
+ "Aşamalı Gösterim" ve "Gömülü Dosya" mimarisi eklendi.
"""
        self.textbox_notlar.insert("0.0", metin)
        self.textbox_notlar.configure(state="disabled") 

    def setup_support_frame(self):
        self.frame_destek = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_destek.grid_columnconfigure(0, weight=1)
        t = self.texts[self.current_lang]

        self.lbl_destek_title = ctk.CTkLabel(self.frame_destek, text=t["sidebar_support"], font=self.font_title)
        self.lbl_destek_title.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")
        
        card = ctk.CTkFrame(self.frame_destek, corner_radius=12, fg_color=self.card_color)
        card.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        
        self.support_info_lbl = ctk.CTkLabel(card, text=t["support_text"], font=self.font_main, justify="center")
        self.support_info_lbl.pack(pady=30, padx=20)
        
        self.github_nav_btn = ctk.CTkButton(card, text=t["github_btn"], font=self.font_bold, height=45, fg_color="#333", command=lambda: webbrowser.open(GITHUB_LINK))
        self.github_nav_btn.pack(pady=10)
        
        ctk.CTkButton(card, text="▶️ YouTube", font=self.font_bold, height=45, fg_color="#FF0000", command=lambda: webbrowser.open(VIDEO_LINK)).pack(pady=(10, 30))

    # --- LOJİK METOTLAR (V1.6 İLE AYNI) ---
    def select_download_path(self):
        klasor = filedialog.askdirectory()
        if klasor:
            self.download_path = klasor
            self.lbl_path.configure(text=klasor if len(klasor) < 35 else "..." + klasor[-32:])

    def check_url_logic(self):
        url = self.url_entry.get()
        if not url: return
        self.btn_check_url.configure(state="disabled")
        threading.Thread(target=self._fetch_video_info, args=(url,), daemon=True).start()

    def _fetch_video_info(self, url):
        try:
            ydl_opts = {'quiet': True, 'noplaylist': not self.playlist_var.get()}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            self.after(0, lambda: self.lbl_video_title.configure(text=info.get('title', 'Unknown')))
            self.after(0, lambda: self.lbl_video_channel.configure(text=f"Kanal: {info.get('uploader', 'Unknown')}"))
            self.after(0, lambda: self.info_card_frame.grid(row=4, column=0, padx=40, pady=20, sticky="ew"))
            self.after(0, lambda: self.options_frame.grid(row=5, column=0, padx=40, pady=0, sticky="ew"))
        except: pass
        finally: self.after(0, lambda: self.btn_check_url.configure(state="normal"))

    def start_download_logic(self):
        url = self.url_entry.get()
        self.btn_start_download.configure(state="disabled")
        self.progress_bar.grid(row=2, column=0, sticky="ew", pady=5)
        self.lbl_progress_details.grid(row=3, column=0, sticky="w")
        threading.Thread(target=self._download_thread, args=(url, self.format_combo.get(), self.playlist_var.get()), daemon=True).start()

    def _download_thread(self, url, res, pl):
        try:
            def hook(d):
                if d['status'] == 'downloading':
                    p = d.get('_percent_str', '0%').replace('%','')
                    self.after(0, lambda: self.progress_bar.set(float(p)/100))
            
            opts = {'progress_hooks': [hook], 'ffmpeg_location': MEVCUT_KLASOR, 'outtmpl': f'{self.download_path}/%(title)s.%(ext)s'}
            with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
            self.after(0, lambda: self.lbl_progress_details.configure(text="✅ Done!", text_color="green"))
        except: pass
        finally: self.after(0, lambda: self.btn_start_download.configure(state="normal"))

    def select_file_logic(self):
        yol = filedialog.askopenfilename()
        if yol:
            self.secilen_dosya_yolu = yol
            self.lbl_selected_file.configure(text=os.path.basename(yol))

    def start_convert_logic(self):
        if not self.secilen_dosya_yolu: return
        self.btn_convert.configure(state="disabled")
        threading.Thread(target=self._convert_thread, args=(self.conv_combo.get(),), daemon=True).start()

    def _convert_thread(self, fmt):
        try:
            cikti = os.path.splitext(self.secilen_dosya_yolu)[0] + f"_new.{fmt}"
            subprocess.run([FFMPEG_YOLU, "-y", "-i", self.secilen_dosya_yolu, cikti], creationflags=subprocess.CREATE_NO_WINDOW)
            self.after(0, lambda: self.lbl_conv_status.configure(text="✅ Success!", text_color="green"))
        except: pass
        finally: self.after(0, lambda: self.btn_convert.configure(state="normal"))

    # --- OTONOM GÜNCELLEME SİSTEMİ ---
    def check_app_update(self):
        threading.Thread(target=self._app_update_thread, daemon=True).start()

    def _app_update_thread(self):
        try:
            with urllib.request.urlopen(self.GITHUB_VERSION_URL, timeout=5) as res:
                ver = res.read().decode('utf-8').strip()
            if float(ver) > self.MEVCUT_SURUM:
                self.after(0, lambda: self._show_update_dialog(ver))
        except: pass

    def _show_update_dialog(self, ver):
        t = self.texts[self.current_lang]
        if messagebox.askyesno(t["update_found"], t["update_msg"].format(ver)):
            threading.Thread(target=self._download_and_apply_update, daemon=True).start()

    def _download_and_apply_update(self):
        try:
            self.after(0, lambda: self.version_label.configure(text="Downloading...", text_color="orange"))
            urllib.request.urlretrieve(self.GITHUB_EXE_URL, "Nuklon_Yeni.exe")
            self._create_and_run_updater_bat()
        except: pass

    def _create_and_run_updater_bat(self):
        bat = f'@echo off\ntimeout /t 2 /nobreak >nul\ndel "Nuklon Medya Merkezi.exe"\nren "Nuklon_Yeni.exe" "Nuklon Medya Merkezi.exe"\nstart "" "Nuklon Medya Merkezi.exe"\ndel "%~f0"'
        with open("update.bat", "w") as f: f.write(bat)
        subprocess.Popen(["update.bat"], creationflags=subprocess.CREATE_NO_WINDOW)
        os._exit(0)

    def check_auto_update(self):
        threading.Thread(target=self._yt_dlp_check, daemon=True).start()

    def _yt_dlp_check(self):
        try:
            with urllib.request.urlopen("https://pypi.org/pypi/yt-dlp/json", timeout=5) as res:
                data = json.loads(res.read())
                if yt_dlp.version.__version__ < data["info"]["version"]:
                    self.after(0, lambda: self.version_label.configure(text="⚠️ Altyapı Eski!", text_color="orange"))
                    self.after(0, lambda: self.btn_update_download.grid(row=9, column=0, padx=20, pady=(0, 20), sticky="w"))
        except: pass

    def select_frame_by_name(self, name):
        for btn in [self.btn_indirici, self.btn_donusturucu, self.btn_notlar, self.btn_destek]: btn.configure(fg_color="transparent")
        for frame in [self.frame_indirici, self.frame_donusturucu, self.frame_notlar, self.frame_destek]: frame.grid_forget()
        if name == "indirici": 
            self.btn_indirici.configure(fg_color=("gray75", "gray25"))
            self.frame_indirici.grid(row=0, column=1, sticky="nsew")
        elif name == "donusturucu":
            self.btn_donusturucu.configure(fg_color=("gray75", "gray25"))
            self.frame_donusturucu.grid(row=0, column=1, sticky="nsew")
        elif name == "notlar":
            self.btn_notlar.configure(fg_color=("gray75", "gray25"))
            self.frame_notlar.grid(row=0, column=1, sticky="nsew")
        elif name == "destek":
            self.btn_destek.configure(fg_color=("gray75", "gray25"))
            self.frame_destek.grid(row=0, column=1, sticky="nsew")

    def change_theme(self):
        ctk.set_appearance_mode("Dark" if self.theme_switch.get() == 1 else "Light")

if __name__ == "__main__":
    app = NuklonApp()
    app.mainloop()