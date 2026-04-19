@echo off
echo === 1. ASAMA: Paketler Guncelleniyor ===
python -m pip install --upgrade yt-dlp
python -m pip install customtkinter
python -m pip install Pillow
python -m pip install pyinstaller

echo.
echo === 2. ASAMA: Gerekli Dosyalar Kontrol Ediliyor ===
if not exist "ffmpeg.exe" (echo HATA: ffmpeg.exe dosyasi programin yaninda yok! & pause & exit)
if not exist "logo.jpg" (echo HATA: logo.jpg dosyasi eksik veya adi logo.jpg.jpg olmus! & pause & exit)
if not exist "ikon.ico" (echo HATA: ikon.ico dosyasi programin yaninda yok! & pause & exit)
if not exist "indirici.py" (echo HATA: indirici.py dosyasi bulunamadi! & pause & exit)

echo.
echo === 3. ASAMA: Paketleme Basliyor (Lutfen Bekleyin) ===
python -m PyInstaller ^
--onefile ^
--noconsole ^
--icon=ikon.ico ^
--add-binary "ffmpeg.exe;." ^
--add-data "logo.jpg;." ^
--add-data "ikon.ico;." ^
--name="Nuklon Medya Merkezi" ^
indirici.py

echo.
echo === ISLEM TAMAMLANDI! ===
echo Lutfen 'dist' klasorunu kontrol edin.
pause