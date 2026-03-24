[app]

# (str) Uygulama Adı
title = HEDEF TAKIP YES

# (str) Paket Adı
package.name = hedef_takip_yes

# (str) Paket Alan Adı
package.domain = org.yusufvarkal

# (str) Kaynak kodun bulunduğu dizin
source.dir = .

# (list) Dahil edilecek dosya uzantıları
source.include_exts = py,png,jpg,kv,atlas,db

# (str) Uygulama versiyonu
version = 0.1

# (list) Uygulama gereksinimleri (KRİTİK GÜNCELLEME)
# Matplotlib ve Numpy için hostpython3 eklenmiştir.
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,matplotlib,numpy,hostpython3,sqlite3

# (list) Desteklenen yönelim
orientation = portrait

#
# Android specific
#

# (bool) Tam ekran modu
fullscreen = 0

# (list) İzinler (Veritabanı ve dosya işlemleri için)
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (int) Hedef Android API (Modern telefonlar için 33 idealdir)
android.api = 33

# (int) Minimum API desteği
android.minapi = 21

# (int) Android NDK API (Genellikle minapi ile aynı olur)
android.ndk_api = 21

# (bool) AndroidX desteğini etkinleştir (KivyMD için zorunludur)
android.enable_androidx = True

# (bool) Lisansları otomatik kabul et
android.accept_sdk_license = True

# (str) Uygulama mimarisi
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log seviyesi (Hataları detaylı görmek için 2 kalsın)
log_level = 2

# (int) Root uyarısı
warn_on_root = 1