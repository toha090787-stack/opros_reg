import asyncio
from datetime import datetime, timedelta
import logging
import os
import sys
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")
# ID вашей группы
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID", "-1003166538020")

dp = Dispatcher()

# Обработчик для ручной проверки отправки опроса по командам /start или /test
@dp.message(CommandStart())
@dp.message(Command("test"))
async def test_poll_handler(message: Message):
  await send_daily_poll(message.bot)

# Функция отправки опроса
async def send_daily_poll(bot: Bot):
  if not GROUP_CHAT_ID or GROUP_CHAT_ID == "ВАШ_ID_ГРУППЫ":
    logging.error("❌ ОШИБКА: Не указан ID группы (GROUP_CHAT_ID)!")
    return

  # Получаем текущую дату по МСК и дату завтрашнего дня
  tz_moscow = ZoneInfo("Europe/Moscow")
  now = datetime.now(tz_moscow)
  tomorrow = now + timedelta(days=1)

  date_today = now.strftime("%d.%m")
  date_tomorrow = tomorrow.strftime("%d.%m")

  # Формируем заголовок с динамическими датами
  question = f"Меня можно будить в ночь с {date_today} на {date_tomorrow}"

  # Варианты ответов
  options = [
      "Регистратором СПб, экипаж",
      "Регистратором ЛО, экипаж",
      "Регистратором СПб, нет экипажа",
      "Регистратором ЛО, нет экипажа",
      "Регистратором на автоном",
      "Не будить",
  ]

  try:
    await bot.send_poll(
        chat_id=GROUP_CHAT_ID,
        question=question,
        options=options,
        is_anonymous=False,  # Открытый опрос
        allows_multiple_answers=False,  # Только один вариант
    )
    logging.info(f"✅ Ежедневный опрос успешно отправлен в группу {GROUP_CHAT_ID}")
  except Exception as e:
    logging.error(f"❌ Не удалось отправить опрос: {e}")

async def main() -> None:
  if not BOT_TOKEN or BOT_TOKEN == "ВАШ_ТОКЕН_БОТА":
    logging.error(
        "❌ ОШИБКА: Токен бота не найден! Укажите BOT_TOKEN в настройках."
    )
    return

  bot = Bot(
      token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
  )

  # Инициализируем планировщик с часовым поясом Москвы
  scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))

  # Настраиваем отправку каждый день в 18:00 МСК
  scheduler.add_job(send_daily_poll, "cron", hour=18, minute=0, args=[bot])
  scheduler.start()

  logging.info(
      "🚀 Бот запущен! Планировщик настроен на отправку опросов ежедневно в"
      " 18:00 МСК."
  )

  # Запускаем прием сообщений
  await dp.start_polling(bot)

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, stream=sys.stdout)
  try:
    asyncio.run(main())
  except (KeyboardInterrupt, SystemExit):
    logging.info("Бот остановлен.")
