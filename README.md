# 🤖 Telegram AI İlan Uygunluk Botu

İş/staj arayışında olan kişiler için geliştirilmiş bu Telegram botu, Youthall üzerindeki ilanları analiz eder ve kullanıcının bilgilerine uygun olanları otomatik olarak iletir.

## 🚀 Özellikler

- 🧠 Yerel çalışan **LLaMA3** modeli ile ilan analizleri
- 🌐 **Youthall** üzerinden otomatik ilan tarama (Selenium ile)
- 🤖 Telegram bot arayüzü ile etkileşimli kullanım
- 📬 Sadece size uygun ilanları filtreleyerek paylaşır

## 🛠️ Gereksinimler

### 🧠 Ollama Model Kurulumu (LLaMA3)

API erişimi sınırlı olabileceği için dil modeli yerel olarak çalıştırılmaktadır.

1. Ollama'yı indir:  
   👉 [https://ollama.com/download](https://ollama.com/download)



pip install -r requirements.txt
requirements.txt içeriği:


python-telegram-bot
selenium
webdriver-manager
ollama
 Kullanılan Kütüphaneler 
Kütüphane	Amaç
python-telegram-bot	Telegram botu oluşturmak ve mesajları yönetmek
selenium	Youthall sitesinden ilanları otomatik olarak çekmek
webdriver-manager	ChromeDriver'ı yönetmek ve otomatik olarak yüklemek
ollama	LLaMA3 modelini çalıştırmak ve ilan analizlerini yapmak


Gerekli kütüphaneleri kurun:


pip install -r requirements.txt
Ollama modelini çalıştırın:


ollama serve
Botu başlatın:


python bot.py
Bot çalışmaya başladıktan sonra, Telegram üzerinden botunuza /kontrol komutunu girerek iş ilanlarını analiz etmeye başlayabilirsiniz.
