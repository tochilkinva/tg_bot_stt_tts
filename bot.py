"""
Telegram бот для конвертации голосового/аудио сообщения в текст и
создания аудио из текста.
"""
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.input_file import InputFile
from dotenv import load_dotenv

from stt import STT
from tts import TTS

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)  # Объект бота
dp = Dispatcher(bot)  # Диспетчер для бота
tts = TTS()
stt = STT()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    filename="bot.log",
)


# Хэндлер на команду /start , /help
@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет! Это Бот для конвертации голосового/аудио сообщения в текст"
        " и создания аудио из текста."
    )


# Хэндлер на команду /test
@dp.message_handler(commands="test")
async def cmd_test(message: types.Message):
    """
    Обработчик команды /test
    """
    await message.answer("Test")


# Хэндлер на получение текста
@dp.message_handler(content_types=[types.ContentType.TEXT])
async def cmd_text(message: types.Message):
    """
    Обработчик на получение текста
    """
    await message.reply("Текст получен")

    out_filename = tts.text_to_ogg(message.text)

    # Отправка голосового сообщения
    path = Path("", out_filename)
    voice = InputFile(path)
    await bot.send_voice(message.from_user.id, voice,
                         caption="Ответ от бота")

    # Удаление временного файла
    os.remove(out_filename)


# Хэндлер на получение голосового и аудио сообщения
@dp.message_handler(content_types=[
    types.ContentType.VOICE,
    types.ContentType.AUDIO,
    types.ContentType.DOCUMENT
    ]
)
async def voice_message_handler(message: types.Message):
    """
    Обработчик на получение голосового и аудио сообщения.
    """
    if message.content_type == types.ContentType.VOICE:
        file_id = message.voice.file_id
    elif message.content_type == types.ContentType.AUDIO:
        file_id = message.audio.file_id
    elif message.content_type == types.ContentType.DOCUMENT:
        file_id = message.document.file_id
    else:
        await message.reply("Формат документа не поддерживается")
        return

    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"{file_id}.tmp")
    await bot.download_file(file_path, destination=file_on_disk)
    await message.reply("Аудио получено")

    text = stt.audio_to_text(file_on_disk)
    if not text:
        text = "Формат документа не поддерживается"
    await message.answer(text)

    os.remove(file_on_disk)  # Удаление временного файла


if __name__ == "__main__":
    # Запуск бота
    print("Запуск бота")
    try:
        executor.start_polling(dp, skip_updates=True)
    except (KeyboardInterrupt, SystemExit):
        pass
