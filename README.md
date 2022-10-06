# tg_bot_stt_tts
Telegram bot with voice message recognition and generation

### Описание
Telegram-бот с распознаванием и генерацией голосовых сообщений

### Алгоритм работы
- Распознавание аудио и голосовых сообщений: кидаем боту аудио или голосовое сообщение, получаем текст.
- Генерация аудио сообщений: кидаем боту текст, получаем аудио сообщение.

### Команды
- /start - Появляется при первом старте бота
- /help - Повторяет сообщение при первом старте бота

### Технологии
aiogram, torch, vosk, silero, num2words, ffmpeg

### Запуск проекта

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/tochilkinva/tg_bot_stt_tts.git
cd tg_bot_stt_tts
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
. env/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Создайте файл .env и укажите необходимые данные.
Пример есть в .env_example.

#### Скачайте модели
vosk, silero ffmpeg - дописать




Затем просто запустите код bot.py в Python.

### Процесс создания бота в телеграмм
Добавить описание

### Автор
Валентин
