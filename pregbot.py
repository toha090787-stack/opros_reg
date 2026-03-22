import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import settings

# --- Конфигурация ---
API_TOKEN = settings.API_TOKEN
GROUP_ID = "-1003166538020"  # ID вашей группы

# ВАЖНО: укажите здесь рабочий прокси Socks5
# Если прокси не нужен, оставьте строку пустой ""
PROXY_URL = "socks5://85.198.96.242:3128" 
# Пример: PROXY_URL = "socks5://user123:pass456@192.168.1.1:1080"

# --- Логирование ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Отправка опроса ---
async def send_daily_poll(bot: Bot):
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    question = f"Меня можно будить в ночь с {today.strftime('%d.%m')} на {tomorrow.strftime('%d.%m')}"

    options = [
        "Регистратором на выезд, экипаж",
        "Регистратором на выезд, нет экипажа",
        "Регистратором на автоном",
        "Не будить",
    ]

    try:
        await bot.send_poll(
            chat_id=GROUP_ID,
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=True,
        )
        logger.info("✅ Опрос успешно отправлен.")
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке опроса: {e}")

# --- Основной цикл ---
async def main():
    logger.info("🚀 Запуск бота...")

    # Создаем бота. Если PROXY_URL не пустая, он будет использовать прокси.
    bot = Bot(token=API_TOKEN, proxy=PROXY_URL)
    dp = Dispatcher()

    # Планировщик задач
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_daily_poll, "cron", hour=21, minute=54, args=[bot])
    scheduler.start()

    # Проверка соединения с Telegram
    try:
        me = await bot.get_me()
        logger.info(f"🤖 Бот подключен как @{me.username}")
        logger.info(f"🌐 Используется прокси: {'ДА' if PROXY_URL else 'НЕТ'}")
    except Exception as e:
        logger.error(f"🚫 Критическая ошибка при подключении к Telegram: {e}")
        return # Выходим, если не удалось авторизоваться

    # Запуск бота (Polling)
    try:
        logger.info("🟢 Запускаем polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка в работе бота: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
