# tg_bot_stt_tts
Telegram bot with voice message recognition and generation

### Описание
Telegram-бот с распознаванием и генерацией голосовых сообщений. Пока протестирован и работает под Windows!

### Алгоритм работы
- Распознавание аудио и голосовых сообщений: кидаем боту аудио или голосовое сообщение, получаем текст.
- Генерация аудио сообщений: кидаем боту текст, получаем аудио сообщение.

### Команды
- /start - Приветствие, появляется при первом старте бота
- /help - Повторяет сообщение при первом старте бота
- /test - Отвечает тестовым сообщением

### Технологии
aiogram, torch, vosk, silero, num2words, ffmpeg

### Запуск проекта

Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone https://github.com/tochilkinva/tg_bot_stt_tts.git
cd tg_bot_stt_tts
```

Cоздайте и активируйте виртуальное окружение:

```
python -m venv venv
. env/Scripts/activate
```

Установите зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Создайте файл .env и укажите токен вашего бота. Пример есть в .env_example. Процесс создания телеграм бота и получения токена не описан.

Скачайте модели и поместите в необходимые папки. Где взять модели описано ниже.

После скачивания моделей запустите код bot.py в Python.

### Модели Vosk и Silero, а также FFmpeg

*Vosk* - оффлайн-распознавание аудио и получение из него текста. Модели доступны на сайте [проекта](https://alphacephei.com/vosk/models "Vosk - оффлайн-распознавание аудио"). Скачайте модель, разархивируйте и поместите папку model с файлами в папку models/vosk.
- [vosk-model-ru-0.22       - 1.5 Гб](https://alphacephei.com/vosk/models/vosk-model-ru-0.22.zip "Модель vosk-model-ru-0.22 - 1.5 Гб") - лучше распознает, но дольше и весит много.
- [vosk-model-small-ru-0.22 - 45 Мб](https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip "Модель vosk-model-small-ru-0.22 - 45 Мб") - хуже распознает, но быстрее и весит мало.

*Silero* - оффлайн-создание аудио сообщения из текста.
В классе TTS проекта указана [модель Silero v3.1 ru - 60 Мб](https://models.silero.ai/models/tts/ru/v3_1_ru.pt "Модель Silero v3.1 ru - 60 Мб"), которая сама скачается при первом запуске проекта. Остальные модели можно скачать [тут](https://github.com/snakers4/silero-models/blob/master/models.yml "Silero - оффлайн-создание аудио из текста") или на сайте [проекта](https://github.com/snakers4/silero-models "Silero - оффлайн-создание аудио из текста"). Поместите файл model.pt в папку models/silero.

*FFmpeg* - набор open-source библиотек для конвертирования аудио- и видео в различных форматах.
Скачайте набор exe файлов с сайта [проекта](https://ffmpeg.org/download.html "FFmpeg - набор open-source библиотек для конвертирования аудио- и видео в различных форматах.") и поместите файл ffmpeg.exe в папки models/vosk и models/silero.


### Автор
Валентин
