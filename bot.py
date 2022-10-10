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

from stt_tts import STT, TTS

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FILE_EXTENTION = [".ogg", ".wav"]

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
    text = message.text
    print(f"text: {text}")

    out_filename = tts.text_to_ogg(text)
    print(out_filename)

    # Отправка голосового сообщения
    path = Path("", out_filename)
    voice = InputFile(path)

    await bot.send_voice(message.from_user.id, voice,
                         caption="ответ от бота")   # ответ от самого бота
    # await bot.send_voice(chat_id=message.chat.id, voice=voice,
    #                      caption="ответ в чат")     # ответ в чат

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
    if isinstance(message.content_type, types.ContentType.VOICE):
        file_id = message.voice.file_id
    elif isinstance(message.content_type, types.ContentType.AUDIO):
        file_id = message.audio.file_id
    elif isinstance(message.content_type, types.ContentType.DOCUMENT):
        file_id = message.document.file_id
    else:
        await message.reply("Формат документа не поддерживается")
        return

    file = await bot.get_file(file_id)
    file_path = file.file_path

    destination = Path("", f"{file_id}.tmp")
    await bot.download_file(file_path, destination=destination)
    await message.reply("Аудио получено")

    text = stt.audio_to_text(destination)
    if not text:
        text = "Формат не поддерживается"

    await message.answer(text)

    os.remove(destination)  # Удаление временного файла


if __name__ == "__main__":
    # Запуск бота
    print("Запуск бота")
    try:
        executor.start_polling(dp, skip_updates=True)
    except (KeyboardInterrupt, SystemExit):
        pass
