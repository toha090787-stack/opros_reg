import asyncio
import logging
from datetime import datetime, timedelta

import settings
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp

# Конфигурация
API_TOKEN = settings.API_TOKEN
GROUP_ID = '-1003166538020'  # ID группы

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Настройка aiohttp-сессии с DNS-кэшем
connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)

from aiohttp_socks import ProxyConnector
from aiogram.client.session.aiohttp import AiohttpSession

PROXY_URL = "socks5://user:password@ip:port"  # или прокси без авторизации: socks5://ip:port

connector = ProxyConnector.from_url(PROXY_URL)
session = AiohttpSession(connector=connector)
bot = Bot(token=settings.API_TOKEN, session=session)
bot = Bot(token=API_TOKEN, connector=connector)
dp = Dispatcher()

async def send_daily_poll():
    """Создание и отправка опроса в чат"""
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    date_str = today.strftime("%d.%m")
    tomorrow_str = tomorrow.strftime("%d.%m")

    question = f"Меня можно будить в ночь с {date_str} на {tomorrow_str}"
    options = [
        "Регистратором на выезд, экипаж",
        "Регистратором на выезд, нет экипажа",
        "Регистратором на автоном",
        "Не будить"
    ]

    try:
        await bot.send_poll(
            chat_id=GROUP_ID,
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=True
        )
        logger.info(f"✅ Опрос отправлен в {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке опроса: {e}")

async def main():
    """Основная логика с автоматическим переподключением"""
    logger.info("🚀 Запуск бота и планировщика...")

    # Настройка планировщика задач
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # Запуск опроса ежедневно в 18:00 (укажи нужное время)
    scheduler.add_job(send_daily_poll, 'cron', hour=21, minute=10)
    scheduler.start()

    while True:
        try:
            logger.info("🤖 Бот запущен. Ожидаем события...")
            await dp.start_polling(bot)

        except TelegramNetworkError as e:
            logger.warning(f"⚠️ Сетевая ошибка Telegram: {e}. Повтор через 15 секунд...")
            await asyncio.sleep(15)

        except aiohttp.ClientConnectorError as e:
            logger.warning(f"🌐 Ошибка подключения: {e}. Повтор через 20 секунд...")
            await asyncio.sleep(20)

        except Exception as e:
            logger.error(f"❌ Неизвестная ошибка: {e}", exc_info=True)
            await asyncio.sleep(30)

if __name__ == '__main__':
    asyncio.run(main())
