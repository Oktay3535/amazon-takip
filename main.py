import os
import smtplib
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# --- AYARLAR ---
ARAMA_KEYWORD = "Finish Ultimate 85 Kapsül"
URL_UYUMLU_KEYWORD = quote_plus(ARAMA_KEYWORD)
AMAZON_ARAMA_URL = f"https://www.amazon.com.tr/s?k={URL_UYUMLU_KEYWORD}"

GONDEREN_MAIL = os.environ.get('MAIL_ADRESI', 'oktayersoy@gmail.com')
MAIL_SIFRESI = os.environ.get('MAIL_SIFRESI')
ALICI_MAIL = os.environ.get('ALICI_MAIL', 'oktayersoy@gmail.com')

def eposta_gonder(bulunan_urun_linki):
    if not all([GONDEREN_MAIL, MAIL_SIFRESI, ALICI_MAIL]):
        return "HATA: E-posta bilgileri ayarlanmamış!"
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as c:
            c.starttls()
            c.login(user=GONDEREN_MAIL, password=MAIL_SIFRESI)
            konu = f"Stok Bildirimi: {ARAMA_KEYWORD} Stokta!"
            mesaj = f"Merhaba,\n\n'{ARAMA_KEYWORD}' Amazon'da stoklara girdi!\n\n👉 {bulunan_urun_linki}"
            c.sendmail(from_addr=GONDEREN_MAIL,
                       to_addrs=ALICI_MAIL,
                       msg=f"Subject:{konu}\n\n{mesaj}")
        return "E-posta başarıyla gönderildi!"
    except Exception as e:
        return f"E-posta gönderilirken hata oluştu: {e}"

def arama_yap_ve_kontrol_et():
    try:
        print("Playwright başlatılıyor...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(AMAZON_ARAMA_URL, timeout=60000)
            page.wait_for_selector("div[data-component-type='s-search-result']", timeout=15000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        sonuclar = soup.find_all("div", {"data-component-type": "s-search-result"})

        if not sonuclar:
            return "Arama sonucunda ürün bulunamadı veya sayfa yapısı değişmiş."

        print(f"{len(sonuclar)} adet ürün kutusu bulundu. Başlıklar taranıyor...")

        aranacak_kelimeler = ARAMA_KEYWORD.lower().split()

        for i, urun in enumerate(sonuclar):
            urun_basligi_elementi = urun.select_one('h2 a span')
            if not urun_basligi_elementi:
                print(f"-> Ürün #{i+1} için başlık elementi bulunamadı.")
                continue

            urun_basligi = urun_basligi_elementi.get_text(strip=True).lower()
            print(f"- Başlık #{i+1}: {urun_basligi}", flush=True)

            if all(kelime in urun_basligi for kelime in aranacak_kelimeler):
                urun_link_elementi = urun.select_one('h2 a')
                if urun_link_elementi and urun_link_elementi.has_attr('href'):
                    tam_urun_linki = "https://www.amazon.com.tr" + urun_link_elementi['href']
                    print(f"[!] Uygun ürün bulundu: {tam_urun_linki}")
                    eposta_mesaji = eposta_gonder(tam_urun_linki)
                    return f"!!! HEDEF BULUNDU !!! Link: {tam_urun_linki} | E-posta Durumu: {eposta_mesaji}"

        return "Hedef ürün bu aramada bulunamadı."

    except Exception as e:
        return f"Beklenmedik bir hata oluştu: {e}"

@app.route('/')
def home():
    return "Amazon takip betiği aktif. Kontrol için /check adresini ziyaret edin."

@app.route('/check')
def trigger_check():
    print("Kontrol tetiklendi...")
    result = arama_yap_ve_kontrol_et()
    print(result)
    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
