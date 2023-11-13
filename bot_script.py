import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
from google.cloud import speech_v1 as speech
from google.oauth2 import service_account
import os
import io

# Включите логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Установите ключ API OpenAI
openai.api_key = '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'

# Установите токены, полученные от BotFather и OpenAI
TELEGRAM_TOKEN = '6758491343:AAHXfNdqdNMLDqNG-g_pXCWdJiyrJ6Fc54M'

# Вставьте содержимое файла учетных данных JSON непосредственно в код
google_credentials = {
  "type": "service_account",
  "project_id": "api-bot-gpt",
  "private_key_id": "f3b4e09aedda4d378e26ac21fefab914f710b080",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCbq/FQ4yEKD8o6\nUYyBM9tmSIt8Fww3jZjEQQRhrVYDj/XTBvdrHmicyTrj+vf+pzdpzHzfRrnc6cUI\nzqC5VVCnNbJM0WDdV7bus8B2sDAjgCtpn2iDuCQtkuUV+aXj0wR3RYFT6Gh2TeGI\ntvs1o8LzVAxg93JxfT/rrH+ZWffkJuUHVnktL+sUdjKQqlNz36lBgwIzqyP4unjT\n2QHqgdfvamQXLbarbiY+ECuLAHhmbSND4Q7JYvs9QqKIlVthW6JMtHtl0uTVlCOF\nuN5Hq48exA3B4S9F7F26SX7kQ2MTPantmP15i86xpNIM74+FfLdSW30xMoTh+vrg\no71lswt7AgMBAAECggEAOTt1XH4ssvTMLjW2GPhWRNwOACC/GpuB20FmGX0vPt8K\nCzwn8ad74YywDIpD68lRe6G1FSd9BMWjbZH+EDVYEimRNGHUIXxyon7OlzQ+dobU\nLyBuveKQ1nqHo9UlUsXNggY5Pn6XDUujy+4uHHHpJimz5WCEIEpimkRQozIrC6NY\nLBPHyCKdoz+hE+lS2wQsDKpfrcdiofzW0+cGIEa9uwSamFoZuupTInU2rhvOWx2K\nfrA4nfvIHdc1+NXz/hiJxJQSVGJf2ICFVW2myLrKKSDsSwoRwGZc+rk70v286nSN\n70e4pdgYs72GnBRlcIDwXdsxA3Yz8AqY4JHA/pGjaQKBgQDQQeiSeYKD1Y8mZf8V\ntyDwg1b+7lXVFgfElVce7TPdCgGPpbt0q+CIeEaEQfZ/jU2uj9EzoGY7PrQ9mS0c\nIlDCVbVMJJlqbnTVhf8eoGu2SzfuK++eMlnYs4kNoVAciFOt1vh5AGzUt4ThGD8d\nUU5En3qheRYIFeqemktqluSmCQKBgQC/W+jHYtWHx8eGhvD5cqhjNvYNCI77DTlo\nW+shccERcyxN5sDE5WDadWmXx77a2YnQiAZoSZ4DOhw4ydwfj/+AnyWod/jcXBm2\nY3CVc+d0cZ4NucxvZWSYV2Wx+vSt1HLjCA8ITM67YJU5m3eXqalXbqqT0GMAEHdZ\nCapLGfWmYwKBgCUOJSCy6Csm+6KccWfevsisxfT0WWdh1R4AaJEDKcBBwIdbuOAI\nmRoPNJTh28dUUCcoRdQGzUnrXUy8jY8899usPmb++CE86CL6BavgZWn5Nkl1ndwr\nH1t0joVTV5rMEv+SiYGWNscepFEc7FX+GowRSFOk5OupYqa304VytdppAoGAKAsB\nkQebi0hA9mOydWCK4AgWQO/zi5Fe2/mwIFV/gzlIohyRZiJhvBUpvXss8vrmnd55\nCMWu7Rnx4ehLyccGPlIPPUutpd8X+lSgsIWKf5Fu84xXvU/IVyCixTWwkdeNGvkK\nvD/mWsuBLobb5b65EvSzeS74KIFJmDYvjnumLeUCgYAP2o77ZEo8c8ns3uUbJg5f\nGURKYYTxXC34wyahoyu1v2vJM0x9TS2x0p7+RkO653tqf95lmNkjY5+VgIa+xKTi\ntKAPvI5yJqK+4afLYgyQw5LbnUnJRZHRolJsccxrHMhzOBLYP9aP8tF9V+mWZhRG\n6+NmvVQWnhw6aO/7x/1Qcg==\n-----END PRIVATE KEY-----\n",
  "client_email": "bot-bot-tg@api-bot-gpt.iam.gserviceaccount.com",
  "client_id": "116378021009839537523",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bot-bot-tg%40api-bot-gpt.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Инициализация клиента Google Cloud Speech-to-Text с учетными данными напрямую из кода
credentials = service_account.Credentials.from_service_account_info(google_credentials)
speech_client = speech.SpeechClient(credentials=credentials)

# Функция обработчика команды start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот, который использует GPT-3 для ответов на ваши вопросы.')

# Функция для отправки запроса к модели GPT-3.5 Turbo
def ask_gpt(question: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return "Извините, произошла ошибка при обработке вашего запроса."

# Функция обработчика эхо-сообщений
def handle_message(update: Update, context: CallbackContext) -> None:
    message = update.message
    if message.chat.type == "private" or (message.chat.type in ["group", "supergroup"] and message.text and '@GPT_643_bot' in message.text):
        # Удаляем упоминание бота из сообщения в групповых чатах
        question = message.text.replace('@GPT_643_bot', '').strip() if message.chat.type in ["group", "supergroup"] else message.text
        answer = ask_gpt(question)
        update.message.reply_text(answer)

# Функция обработки ошибок
def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Функция обработчика голосовых сообщений
def handle_voice_message(update: Update, context: CallbackContext) -> None:
    voice_message = update.message.voice
    voice_file = context.bot.getFile(voice_message.file_id)
    voice_file_path = os.path.join('temp', f"{voice_message.file_id}.ogg")
    voice_file.download(voice_file_path)

    with io.open(voice_file_path, 'rb') as audio_file:
        audio_content = audio_file.read()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=16000,
        language_code='ru-RU'
    )

    logger.info(f"Handling voice message: {voice_file_path}")

    try:
        response = speech_client.recognize(config=config, audio=audio)

        logger.info(f"Full recognition response: {response}")

        # Проверяем, есть ли результаты и не пустой ли результат
        if not response.results or not response.results[0].alternatives:
            update.message.reply_text('Не удалось расшифровать ваше сообщение.')
            return
        
        # Берем первую альтернативу лучшего результата
        transcript = response.results[0].alternatives[0].transcript
        logger.info(f"Transcript: {transcript}")  # Логирование расшифрованного текста
        answer = ask_gpt(transcript)
        update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"Exception during speech recognition: {e}")
        update.message.reply_text('Произошла ошибка при обработке вашего голосового сообщения.')
    finally:
        # Удаляем временный файл после использования
        os.remove(voice_file_path)

# Основная функция
def main() -> None:
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Создаем папку temp для временного хранения файлов голосовых сообщений
    if not os.path.exists('temp'):
        os.makedirs('temp')

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()