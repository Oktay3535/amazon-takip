import os
import smtplib
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

# --- AYARLAR ---
# BU SEFER DAHA KISA VE GARANTİ BİR ARAMA YAPIYORUZ
ARAMA_KEYWORD = "Finish Ultimate 85 Kapsül" 
#ARAMA_KEYWORD = "Iphone 17 pro 256gb gümüş"

URL_UYUMLU_KEYWORD = quote_plus(ARAMA_KEYWORD)
AMAZON_ARAMA_URL = f"https://www.amazon.com.tr/s?k={URL_UYUMLU_KEYWORD}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}

GONDEREN_MAIL = os.environ.get('MAIL_ADRESI')
MAIL_SIFRESI = os.environ.get('MAIL_SIFRESI')
ALICI_MAIL = os.environ.get('ALICI_MAIL')

def eposta_gonder(bulunan_urun_linki):
    if not all([GONDEREN_MAIL, MAIL_SIFRESI, ALICI_MAIL]):
        return "HATA: E-posta bilgileri (ortam değişkenleri) ayarlanmamış!"
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=GONDEREN_MAIL, password=MAIL_SIFRESI)
            konu = f"Stok Bildirimi: {ARAMA_KEYWORD} Stokta!"
            mesaj = f"Merhaba,\n\nTakip ettigin '{ARAMA_KEYWORD}' Amazon'da stoklara girdi ve saticisi Amazon.\n\nHemen satin almak icin linke git: {bulunan_urun_linki}".encode('utf-8')
            connection.sendmail(
                from_addr=GONDEREN_MAIL,
                to_addrs=ALICI_MAIL,
                msg=f"Subject:{konu}\n\n{mesaj.decode('utf-8')}"
            )
        return "E-posta başarıyla gönderildi!"
    except Exception as e:
        return f"E-posta gönderilirken hata oluştu: {e}"

def urun_sayfasini_kontrol_et(urun_url):
    try:
        sayfa = requests.get(urun_url, headers=HEADERS)
        sayfa.raise_for_status()
        soup = BeautifulSoup(sayfa.content, "html.parser")
        stok_durumu = soup.find(id="add-to-cart-button")
        satici_elementi = soup.select_one('#merchant-info a')
        satici_adi = satici_elementi.get_text(strip=True) if satici_elementi else "Bulunamadı"
        if stok_durumu and "Amazon.com.tr" in satici_adi:
            return True, f"Stok: VAR, Satıcı: {satici_adi}"
        return False, f"Stok: {'VAR' if stok_durumu else 'YOK'}, Satıcı: {satici_adi}"
    except Exception as e:
        return False, f"Ürün sayfası kontrol hatası: {e}"

def arama_yap_ve_kontrol_et():
    try:
        aranacak_kelimeler = ARAMA_KEYWORD.lower().split()
        arama_sayfasi = requests.get(AMAZON_ARAMA_URL, headers=HEADERS)
        arama_sayfasi.raise_for_status()
        soup = BeautifulSoup(arama_sayfasi.content, "html.parser")
        sonuclar = soup.find_all("div", {"data-component-type": "s-search-result"})
        
        if not sonuclar:
            return "Arama sonucunda ürün bulunamadı veya sayfa yapısı değişmiş."

        for urun in sonuclar:
            urun_basligi_elementi = urun.select_one('h2 a span')
            if not urun_basligi_elementi: continue
            
            urun_basligi = urun_basligi_elementi.get_text(strip=True).lower()
            
            # --- HATA AYIKLAMA İÇİN EKLENDİ ---
            print(f"- Kontrol edilen başlık: {urun_basligi}")

            if all(kelime in urun_basligi for kelime in aranacak_kelimeler):
                urun_link_elementi = urun.select_one('h2 a')
                if urun_link_elementi and urun_link_elementi.has_attr('href'):
                    tam_urun_linki = "https://www.amazon.com.tr" + urun_link_elementi['href']
                    sonuc, mesaj = urun_sayfasini_kontrol_et(tam_urun_linki)
                    print(f"Uygun başlık bulundu. Detaylar: {mesaj}")
                    if sonuc:
                        eposta_mesaji = eposta_gonder(tam_urun_linki)
                        return f"!!! HEDEF BULUNDU !!! Link: {tam_urun_linki} | E-posta Durumu: {eposta_mesaji}"
        
        return f"Hedef ürün bu aramada bulunamadı. {len(sonuclar)} ürün kontrol edildi."
    except Exception as e:
        return f"Beklenmedik bir arama hatası oluştu: {e}"

@app.route('/')
def home():
    return "Amazon takip betiği aktif. Kontrol için /check adresini ziyaret edin."

@app.route('/check')
def trigger_check():
    print("Kontrol tetiklendi...")
    result = arama_yap_ve_kontrol_et()
    print(result)
    return result
