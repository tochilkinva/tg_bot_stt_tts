"""
Бот
"""
import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.input_file import InputFile
from dotenv import load_dotenv
from pathlib import Path
from stt_tts import STT, TTS

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = Bot(token=TELEGRAM_TOKEN)  # Объект бота
dp = Dispatcher(bot)  # Диспетчер для бота
tts = TTS()
stt = STT()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    filename='bot.log',
)


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.reply("Привет! Это CrazyBot! Давай веселиться!")


# Хэндлер на команду /test
@dp.message_handler(commands="test")
async def cmd_test(message: types.Message):
    """
    Обработчик команды /test
    """
    # out_filename = ogg_to_wav(in_filename=r'.\voices\habr.ogg')
    # out_filename = wav_to_ogg(in_filename=r'.\voices\test_000.wav')

    # # отправка голосового сообщения
    # path = Path("", out_filename)
    # voice = InputFile(path)
    # await bot.send_voice(message.from_user.id, voice)
    # # os.remove(out_filename)

    # await message.reply("Test")


@dp.message_handler(content_types=[types.ContentType.TEXT])
async def cmd_text(message: types.Message):
    """
    Обработчик на получение текста
    """
    await message.reply("Текст получен")
    text = message.text
    print(f'text: {text}')

    out_filename = tts.text_to_ogg(text)
    print(out_filename)

    # отправка голосового сообщения
    path = Path("", out_filename)
    voice = InputFile(path)
    await bot.send_voice(message.from_user.id, voice)
    # os.remove(out_filename)


@dp.message_handler(content_types=[types.ContentType.VOICE])
async def voice_message_handler(message: types.Message):
    """
    Обработчик на получение голосового сообщения.
    """
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    destination = Path("tmp", f"{file_id}.ogg")
    await bot.download_file(file_path, destination=destination)
    await message.reply("Голосовое получено и сохранено")
    text = stt.audio_to_text(destination)
    await message.answer(text)


@dp.message_handler(content_types=[types.ContentType.AUDIO])
async def audio_message_handler(message: types.Message):
    """
    Обработчик на получение аудио.
    """
    file_id = message.audio.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    print('file_path ', file_path)

    destination = Path("tmp", f"{file_id}.tmp")
    await bot.download_file(file_path, destination=destination)
    await message.reply("Аудио получено и сохранено")
    text = stt.audio_to_text(destination)
    await message.answer(text)


@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def document_message_handler(message: types.Message):
    """
    Обработчик на получение аудио.
    """
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    print('file_path ', file_path)

    destination = Path("tmp", f"{file_id}.tmp")
    await bot.download_file(file_path, destination=destination)
    await message.reply("Документ получено и сохранено")
    text = stt.audio_to_text(destination)
    await message.answer(text)

if __name__ == "__main__":
    # Запуск бота
    print("Запуск бота")
    try:
        executor.start_polling(dp, skip_updates=True)
    except (KeyboardInterrupt, SystemExit):
        pass
