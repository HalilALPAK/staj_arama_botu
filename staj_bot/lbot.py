import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import ollama
import time
import traceback


# Komut: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" Merhaba iş ilanlarını analiz etmek için /kontrol komutunu kullan.")


# Komut: /kontrol kullanıcıdan bilgi al
async def kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Lütfen bilgileri şu formatta girin:\n[Şehir], [Sınıf], [Çalışma Türü], [Yetenekler]")
    context.user_data['awaiting_info'] = True


# Kullanıcıdan gelen metinleri yönet
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_info", False):
        user_input = update.message.text
        parts = user_input.split(",")

        if len(parts) < 4:
            await update.message.reply_text("⚠️ Format hatası! Lütfen bilgileri şöyle girin:\n[Şehir], [Sınıf], [Çalışma Türü], [Yetenekler]")
            return

        city, degree, job_type, skills = [x.strip() for x in parts]
        context.user_data["awaiting_info"] = False
        await update.message.reply_text("🔍 İlanlar analiz ediliyor, lütfen bekleyin...")

        await run_job_check(update, city, degree, job_type, skills)
    else:
        await update.message.reply_text("Önce /kontrol komutunu kullanmalısınız.")


# İş ilanlarını tarar ve LLaMA3 ile uygunluk kontrolü yapar
async def run_job_check(update: Update, city, degree, job_type, skills):
    options = Options()
    # options.add_argument("--headless")  # İstersen arka planda çalıştırmak için açabilirsin
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://www.youthall.com/tr/jobs/"
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        time.sleep(5)

        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1.5)

        job_elements = driver.find_elements(By.CLASS_NAME, "l-grid__col.l-grid__col--lg-4.l-grid__col--md-4.l-grid__col--xs-12.u-gap-bottom-25")

        await update.message.reply_text(f"🔎 {len(job_elements)} iş ilanı bulundu. İlk 10 ilan kontrol edilecek.")
        found = 0

        for index, job in enumerate(job_elements[:30]):
            try:
                print(f"➡️ {index+1}. ilan kontrol ediliyor.")
                job_link = job.find_element(By.TAG_NAME, "a").get_attribute("href")
                driver.execute_script(f"window.open('{job_link}', '_blank');")
                driver.switch_to.window(driver.window_handles[1])

                wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                job_title = driver.find_element(By.TAG_NAME, "h1").text

                try:
                    job_description = driver.find_element(By.CLASS_NAME, "c-job_post_content").text.strip()
                except Exception as e:
                    job_description = "İlan açıklaması bulunamadı."
                    print(f"🟡 Açıklama alınamadı: {e}")

                # LLaMA3 ile analiz
                response = ollama.chat(
                    model='llama3',
                    messages=[{
                        'role': 'user',
                        'content': f"İlanda aranan nitelikler: {job_description}. "
                                   f"Bu ilana başvuru için şu bilgilerle uygun muyum? "
                                   f"Şehir: {city}, Sınıf: {degree}, Çalışma Türü: {job_type}, Yetenekler: {skills}. "
                                   f"Sadece 'Evet' ya da 'Hayır' şeklinde cevap ver."
                    }]
                )

                reply = response['message']['content'].lower()
                if "evet" in reply:
                    # HTML biçimi ile güvenli gönderim
                    safe_title = job_title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    message = f" <b>Uygun ilan:</b>\n<b>{safe_title}</b>\n🔗 <a href='{job_link}'>İlan Linki</a>"
                    await update.message.reply_text(message, parse_mode="HTML")
                    found += 1
                else:
                    print(f"Gecildi: {job_title}")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1.5)

            except Exception as e:
                print(f" {index+1}. ilan hatası: {e}")
                print(traceback.format_exc())
                try:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    pass
                continue

        driver.quit()

        if found == 0:
            await update.message.reply_text(" Uygun ilan bulunamadı.")
        else:
            await update.message.reply_text("Tüm uygun ilanlar gönderildi!")

    except Exception as e:
        await update.message.reply_text(f" Genel hata oluştu: {e}")
        print(traceback.format_exc())
        driver.quit()


# Botu çalıştır
if __name__ == "__main__":
    app = ApplicationBuilder().token("8080038281:AAEBzEyMaibqH1N8TipJvI6WC5j659TaxBQ").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kontrol", kontrol))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print(" Bot çalışıyor...")
    asyncio.run(app.run_polling())
