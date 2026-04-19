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
import re
from PIL import Image 

# --- GÜNCEL LİNKLER ---
DRIVE_LINK = "https://drive.google.com/drive/u/0/folders/1mU0McXN5MA-fKKzRs0bWV9K9Cp9zL46z"
VIDEO_LINK = "https://youtu.be/1Ee060Gl4GU"

def kaynak_yolunu_bul(dosya_adi):
    """ .exe içine gömülü dosyaların geçici yolunu (MEIPASS) bulur """
    try:
        temel_yol = sys._MEIPASS
    except Exception:
        temel_yol = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(temel_yol, dosya_adi)

MEVCUT_KLASOR = kaynak_yolunu_bul("") 
IKON_YOLU = kaynak_yolunu_bul("ikon.ico")
LOGO_YOLU = kaynak_yolunu_bul("logo.jpg")
FFMPEG_YOLU = kaynak_yolunu_bul("ffmpeg.exe")
FFPROBE_YOLU = kaynak_yolunu_bul("ffprobe.exe") # Süre ölçümü için eklendi

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class NuklonApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- UYGULAMA DEĞİŞKENLERİ ---
        self.MEVCUT_SURUM = 1.7  
        
        # --- DİL SİSTEMİ (Sözlük Yapısı) ---
        self.current_lang = "tr"
        self.texts = {
            "tr": {
                "title": "Nüklon Medya İstasyonu V1.7",
                "sidebar_download": "⬇️ Video İndirici",
                "sidebar_converter": "🔄 Format Dönüştürücü",
                "sidebar_notes": "📝 Güncelleme Notları",
                "sidebar_support": "🆘 Destek / Hakkında",
                "check_url": "Bağlantıyı Kontrol Et",
                "start_download": "İndirmeyi Başlat",
                "save_path": "Kayıt Yeri:",
                "change_path": "📁 Klasör Değiştir",
                "support_text": "Yardıma ihtiyacınız olursa aşağıdaki bağlantıları kullanabilirsiniz.",
                "drive_btn": "☁️ Google Drive (Sürümler)",
                "status_ready": "Bekleniyor...",
                "placeholder_url": "Video veya oynatma listesi URL'si yapıştırın...",
                "chk_playlist": "Bu link bir oynatma listesi",
                "conv_title": "Format Dönüştürücü",
                "conv_select_file": "📁 Dosya/Dosyalar Seç",
                "conv_target": "Hedef Format:",
                "conv_btn": "Dönüştür",
                "btn_drive_dl": "⬇️ Drive'dan Yeni Sürüm İndir",
                "ytdlp_checking": "yt-dlp: Kontrol ediliyor...",
                "ytdlp_uptodate": "✅ yt-dlp: Güncel",
                "ytdlp_outdated": "⚠️ yt-dlp: Eski Sürüm!",
                "ytdlp_error": "yt-dlp: Bağlantı Hatası",
                "files_selected": "{} dosya seçildi",
                "conv_batch_status": "Dönüştürülüyor ({}/{})... Lütfen Bekleyin",
                "conv_all_success": "✅ Tüm Dosyalar Başarıyla Dönüştürüldü!"
            },
            "en": {
                "title": "Nuklon Media Station V1.7",
                "sidebar_download": "⬇️ Video Downloader",
                "sidebar_converter": "🔄 Format Converter",
                "sidebar_notes": "📝 Release Notes",
                "sidebar_support": "🆘 Support / About",
                "check_url": "Check Link",
                "start_download": "Start Download",
                "save_path": "Save Path:",
                "change_path": "📁 Change Folder",
                "support_text": "If you need help, you can use the links below.",
                "drive_btn": "☁️ Google Drive (Versions)",
                "status_ready": "Ready...",
                "placeholder_url": "Paste video or playlist URL here...",
                "chk_playlist": "This link is a playlist",
                "conv_title": "Format Converter",
                "conv_select_file": "📁 Select File(s)",
                "conv_target": "Target Format:",
                "conv_btn": "Convert",
                "btn_drive_dl": "⬇️ Download Update from Drive",
                "ytdlp_checking": "yt-dlp: Checking...",
                "ytdlp_uptodate": "✅ yt-dlp: Up to date",
                "ytdlp_outdated": "⚠️ yt-dlp: Outdated!",
                "ytdlp_error": "yt-dlp: Connection Error",
                "files_selected": "{} files selected",
                "conv_batch_status": "Converting ({}/{})... Please Wait",
                "conv_all_success": "✅ All Files Converted Successfully!"
            }
        }

        self.title(self.texts[self.current_lang]["title"])
        self.geometry("950x700") 
        self.minsize(850, 650)
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

        self.secilen_dosyalar = [] # Artık liste tutuyoruz
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")

        self.setup_sidebar()
        self.setup_downloader_frame()
        self.setup_converter_frame()
        self.setup_notes_frame()
        self.setup_support_frame()

        self.select_frame_by_name("indirici")
        self.check_auto_update() 

    def change_language_from_menu(self, choice):
        if "Türkçe" in choice:
            self.current_lang = "tr"
        else:
            self.current_lang = "en"
        self.update_ui_texts()

    def update_ui_texts(self):
        t = self.texts[self.current_lang]
        self.title(t["title"])
        self.btn_indirici.configure(text=t["sidebar_download"])
        self.btn_donusturucu.configure(text=t["sidebar_converter"])
        self.btn_notlar.configure(text=t["sidebar_notes"])
        self.btn_destek.configure(text=t["sidebar_support"])
        
        self.lbl_indirici_title.configure(text=t["sidebar_download"].replace("⬇️ ", ""))
        self.url_entry.configure(placeholder_text=t["placeholder_url"])
        self.check_playlist.configure(text=t["chk_playlist"])
        self.btn_check_url.configure(text=t["check_url"])
        self.btn_start_download.configure(text=t["start_download"])
        self.lbl_path_title.configure(text=t["save_path"])
        self.btn_select_path.configure(text=t["change_path"])
        
        self.lbl_conv_title.configure(text=t["conv_title"])
        self.btn_select_file.configure(text=t["conv_select_file"])
        self.lbl_target_format.configure(text=t["conv_target"])
        self.btn_convert.configure(text=t["conv_btn"])

        self.lbl_destek_title.configure(text=t["sidebar_support"])
        self.support_info_lbl.configure(text=t["support_text"])
        self.drive_nav_btn.configure(text=t["drive_btn"])
        
        self.btn_dl_drive.configure(text=t["btn_drive_dl"])
        
        guncel_metin = self.ytdlp_status_label.cget("text")
        if "✅" in guncel_metin:
            self.ytdlp_status_label.configure(text=t["ytdlp_uptodate"])
        elif "⚠️" in guncel_metin:
            self.ytdlp_status_label.configure(text=t["ytdlp_outdated"])
        elif "Hata" in guncel_metin or "Error" in guncel_metin:
            self.ytdlp_status_label.configure(text=t["ytdlp_error"])
        else:
            self.ytdlp_status_label.configure(text=t["ytdlp_checking"])
            
        if self.secilen_dosyalar:
            if len(self.secilen_dosyalar) > 1:
                self.lbl_selected_file.configure(text=t["files_selected"].format(len(self.secilen_dosyalar)))

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

        self.lang_var = ctk.StringVar(value="🇹🇷 Türkçe")
        self.lang_menu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["🇹🇷 Türkçe", "🇬🇧 English"],
            variable=self.lang_var,
            command=self.change_language_from_menu,
            font=("Roboto", 13),
            fg_color=self.card_color,
            button_color=("gray75", "gray25"),
            button_hover_color=("gray70", "gray30"),
            text_color=self.text_main
        )
        self.lang_menu.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.theme_switch = ctk.CTkSwitch(self.sidebar_frame, text="Koyu Tema", font=("Roboto", 12), command=self.change_theme)
        self.theme_switch.grid(row=7, column=0, padx=20, pady=10, sticky="w")
        self.theme_switch.select()

        self.ytdlp_status_label = ctk.CTkLabel(self.sidebar_frame, text=self.texts[self.current_lang]["ytdlp_checking"], font=("Roboto", 12, "bold"), text_color=self.text_muted)
        self.ytdlp_status_label.grid(row=8, column=0, padx=20, pady=(5, 5), sticky="w")
        
        self.btn_dl_drive = ctk.CTkButton(self.sidebar_frame, text=self.texts[self.current_lang]["btn_drive_dl"], font=("Roboto", 11, "bold"), fg_color="#ff9800", text_color="black", hover_color="#e68a00", height=28, command=lambda: webbrowser.open(DRIVE_LINK))

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
        self.conv_progress.grid(row=3, column=0, padx=40, pady=(10, 0), sticky="ew") 
        
        self.lbl_conv_status = ctk.CTkLabel(self.frame_donusturucu, text="", font=("Roboto", 12))
        self.lbl_conv_status.grid(row=4, column=0, padx=40, pady=(5, 20), sticky="w") 

    def setup_notes_frame(self):
        self.frame_notlar = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_notlar.grid_columnconfigure(0, weight=1)
        self.frame_notlar.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_notlar, text=self.texts[self.current_lang]["sidebar_notes"], font=self.font_title).grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")
        
        self.textbox_notlar = ctk.CTkTextbox(self.frame_notlar, font=self.font_main, corner_radius=12, fg_color=self.card_color)
        self.textbox_notlar.grid(row=1, column=0, padx=40, pady=(0, 40), sticky="nsew")
        
        metin = f"=== NÜKLON MEDYA İSTASYONU V1.7 ===\nYENİLİKLER (V1.7):\n+ Siyah açılış ekranı (CMD) tamamen gizlendi.\n+ Dönüştürücüye Toplu Dosya (Batch) desteği ve saniyelik okuma yapan FFprobe ilerleme yüzdesi eklendi.\n+ Uluslararası, bayraklı ve açılır menülü (Dropdown) dil seçici eklendi.\n+ Akıllı yt-dlp durum göstergesi sol menüye entegre edildi.\n------------------------------------------------\nV1.6 - İngilzce Dil Seçeneği Eklendi.\n------------------------------------------------\nV1.5 - Modern Nesne Yönelimli Mimari\n+ Arayüz tamamen class yapısıyla (OOP) sıfırdan kodlandı."
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
        
        self.drive_nav_btn = ctk.CTkButton(card, text=t["drive_btn"], font=self.font_bold, height=45, fg_color="#4285F4", hover_color="#2c6cd6", command=lambda: webbrowser.open(DRIVE_LINK))
        self.drive_nav_btn.pack(pady=10)
        
        ctk.CTkButton(card, text="▶️ YouTube", font=self.font_bold, height=45, fg_color="#FF0000", hover_color="#cc0000", command=lambda: webbrowser.open(VIDEO_LINK)).pack(pady=(10, 30))

    # --- LOJİK METOTLAR ---
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
        except Exception as e: 
            self.after(0, lambda: messagebox.showerror("Hata", f"Link kontrol edilemedi:\n{e}"))
        finally: 
            self.after(0, lambda: self.btn_check_url.configure(state="normal"))

    def start_download_logic(self):
        url = self.url_entry.get()
        res = self.format_combo.get()
        pl = self.playlist_var.get()
        
        self.btn_start_download.configure(state="disabled")
        self.progress_bar.grid(row=2, column=0, sticky="ew", pady=5)
        self.progress_bar.set(0)
        self.lbl_progress_details.configure(text="İndirme başlatılıyor...", text_color=self.text_muted)
        self.lbl_progress_details.grid(row=3, column=0, sticky="w")
        
        threading.Thread(target=self._download_thread, args=(url, res, pl), daemon=True).start()

    def _download_thread(self, url, res, pl):
        try:
            def hook(d):
                if d['status'] == 'downloading':
                    p_str = d.get('_percent_str', '0%').replace('%', '').strip()
                    p_str = re.sub(r'\x1b[^m]*m', '', p_str) 
                    try:
                        oran = float(p_str) / 100.0
                        self.after(0, lambda: self.progress_bar.set(oran))
                        self.after(0, lambda: self.lbl_progress_details.configure(text=f"İndiriliyor: %{p_str}"))
                    except: pass
                elif d['status'] == 'finished':
                    self.after(0, lambda: self.lbl_progress_details.configure(text="Dosyalar birleştiriliyor (Lütfen bekleyin)..."))
            
            fmt_str = "bestvideo+bestaudio/best"
            if res == "1080p": fmt_str = "bestvideo[height<=1080]+bestaudio/best"
            elif res == "720p": fmt_str = "bestvideo[height<=720]+bestaudio/best"
            elif res == "480p": fmt_str = "bestvideo[height<=480]+bestaudio/best"
            elif res == "Sadece Ses (MP3)": fmt_str = "bestaudio/best"

            opts = {
                'progress_hooks': [hook], 
                'ffmpeg_location': MEVCUT_KLASOR, 
                'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
                'noplaylist': not pl,
                'nocolor': True, 
                'format': fmt_str
            }
            
            if res == "Sadece Ses (MP3)":
                opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]

            with yt_dlp.YoutubeDL(opts) as ydl: 
                ydl.download([url])
                
            self.after(0, lambda: self.lbl_progress_details.configure(text="✅ İndirme Tamamlandı!", text_color="green"))
            self.after(0, lambda: self.progress_bar.set(1))
            
        except Exception as e:
            self.after(0, lambda e=e: self.lbl_progress_details.configure(text=f"❌ Hata: {str(e)[:50]}...", text_color="red"))
        finally: 
            self.after(0, lambda: self.btn_start_download.configure(state="normal"))

    # --- YENİ ÇOKLU SEÇİM VE FFPROBE ENTEGRASYONU ---
    def select_file_logic(self):
        # askopenfilename yerine askopenfilenames (çoğul) kullanıyoruz
        yollar = filedialog.askopenfilenames()
        if yollar:
            self.secilen_dosyalar = list(yollar)
            t = self.texts[self.current_lang]
            
            if len(self.secilen_dosyalar) == 1:
                self.lbl_selected_file.configure(text=os.path.basename(self.secilen_dosyalar[0]))
            else:
                self.lbl_selected_file.configure(text=t["files_selected"].format(len(self.secilen_dosyalar)))

    def _get_duration(self, dosya_yolu):
        """ ffprobe ile medya dosyasının toplam süresini saniye cinsinden bulur """
        try:
            cmd = [FFPROBE_YOLU, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", dosya_yolu]
            sonuc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return float(sonuc.stdout.strip())
        except:
            return 0.0

    def start_convert_logic(self):
        if not self.secilen_dosyalar: return
        self.btn_convert.configure(state="disabled")
        self.conv_progress.configure(mode="determinate")
        self.conv_progress.set(0)
        
        threading.Thread(target=self._convert_batch_thread, args=(self.conv_combo.get(),), daemon=True).start()

    def _convert_batch_thread(self, fmt):
        t = self.texts[self.current_lang]
        toplam_dosya = len(self.secilen_dosyalar)
        
        # Seçilen tüm dosyaları sırayla işlemek için döngü (Batch Processing)
        for index, dosya in enumerate(self.secilen_dosyalar):
            # Durum metnini (1/3) dönüştürülüyor şeklinde güncelle
            self.after(0, lambda i=index+1: self.lbl_conv_status.configure(text=t["conv_batch_status"].format(i, toplam_dosya), text_color=self.text_muted))
            self.after(0, lambda: self.conv_progress.set(0))
            
            # 1. Dosyanın toplam süresini bul
            sure = self._get_duration(dosya)
            cikti = os.path.splitext(dosya)[0] + f"_new.{fmt}"
            
            # 2. FFmpeg ile dönüştürme işlemini canlı okuma (pipe) modunda başlat
            cmd = [FFMPEG_YOLU, "-y", "-i", dosya, cikti]
            try:
                process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True, encoding='utf-8', errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                
                # FFmpeg'in anlık çıktılarını (stderr) satır satır oku
                for line in process.stderr:
                    if "time=" in line and sure > 0:
                        # "time=00:01:23.45" gibi metinden zamanı ayıkla
                        match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
                        if match:
                            h, m, s = match.groups()
                            gecen_sure = float(h)*3600 + float(m)*60 + float(s)
                            oran = min(gecen_sure / sure, 1.0)
                            self.after(0, lambda o=oran: self.conv_progress.set(o))
                process.wait()
            except Exception as e:
                self.after(0, lambda err=e: print(f"Dönüştürme Hatası: {err}"))
                continue
                
        # Tüm döngü bittiğinde
        self.after(0, lambda: self.lbl_conv_status.configure(text=t["conv_all_success"], text_color="green"))
        self.after(0, lambda: self.conv_progress.set(1))
        self.after(0, lambda: self.btn_convert.configure(state="normal"))

    def check_auto_update(self):
        threading.Thread(target=self._yt_dlp_check, daemon=True).start()

    def _yt_dlp_check(self):
        try:
            with urllib.request.urlopen("https://pypi.org/pypi/yt-dlp/json", timeout=5) as res:
                data = json.loads(res.read())
                en_guncel = data["info"]["version"]
                mevcut = yt_dlp.version.__version__
                
                m_list = [int(x) for x in mevcut.replace("-", ".").split(".") if x.isdigit()]
                g_list = [int(x) for x in en_guncel.replace("-", ".").split(".") if x.isdigit()]
                
                if m_list < g_list:
                    t = self.texts[self.current_lang]
                    self.after(0, lambda: self.ytdlp_status_label.configure(text=t["ytdlp_outdated"], text_color="#ff9800"))
                    self.after(0, lambda: self.btn_dl_drive.grid(row=9, column=0, padx=20, pady=(0, 20), sticky="ew"))
                else:
                    t = self.texts[self.current_lang]
                    self.after(0, lambda: self.ytdlp_status_label.configure(text=t["ytdlp_uptodate"], text_color="green"))
        except Exception as e: 
            t = self.texts[self.current_lang]
            self.after(0, lambda: self.ytdlp_status_label.configure(text=t["ytdlp_error"], text_color="red"))

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