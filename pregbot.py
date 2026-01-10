import asyncio
import logging
import settings
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Конфигурация
API_TOKEN = settings.API_TOKEN
GROUP_ID = '-1003166538020'  # ID группы (число со знаком минус, например -100...)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def send_daily_poll():
    """Функция для создания и отправки опроса"""
    # Вычисляем даты
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    date_str = today.strftime("%d.%m")
    tomorrow_str = tomorrow.strftime("%d.%m")

    question = f"Меня можно будить в ночь с {date_str} на {tomorrow_str}"
    options = [
        "Регистратором на выезд, экипаж"
        "Регистратором на выезд, нет экипажа"
        "Регистратором на автоном"
        "Не будить"
    ]

    try:
        await bot.send_poll(
            chat_id=GROUP_ID,
            question=question,
            options=options,
            is_anonymous=False,  # Чтобы видеть, кто ответил
            allows_multiple_answers=True
        )
        logging.info(f"Опрос отправлен в {datetime.now()}")
    except Exception as e:
        logging.error(f"Ошибка при отправке опроса: {e}")


async def main():
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)

    # Настройка планировщика
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")  # Укажите ваш часовой пояс
    # Запуск задачи ежедневно в 18:00
    scheduler.add_job(send_daily_poll, 'cron', hour=4, minute=55)
    scheduler.start()

    logging.info("Бот запущен и планировщик активирован.")

    try:
        # Запуск бота
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())