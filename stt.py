# -*- coding: utf8 -*-
"""
Конвертация wav/ogg -> текст
"""
import json
import os
import subprocess
from datetime import datetime

from vosk import KaldiRecognizer, Model  # оффлайн-распознавание от Vosk


class STT:
    """
    Класс для распознования аудио через Vosk и преобразования его в текст.
    Поддерживаются форматы аудио: wav, ogg
    """
    default_init = {
        "model_path": "models/vosk/model",  # путь к папке с файлами STT модели Vosk
        "sample_rate": 16000,
        "ffmpeg_path": "models/vosk"  # путь к ffmpeg
    }

    def __init__(self,
                 model_path=None,
                 sample_rate=None,
                 ffmpeg_path=None
                 ) -> None:
        """
        Настройка модели Vosk для распознования аудио и
        преобразования его в текст.

        :arg model_path:  str  путь до модели Vosk
        :arg sample_rate: int  частота выборки, обычно 16000
        :arg ffmpeg_path: str  путь к ffmpeg
        """
        self.model_path = model_path if model_path else STT.default_init["model_path"]
        self.sample_rate = sample_rate if sample_rate else STT.default_init["sample_rate"]
        self.ffmpeg_path = ffmpeg_path if ffmpeg_path else STT.default_init["ffmpeg_path"]

        self._check_model()

        model = Model(self.model_path)
        self.recognizer = KaldiRecognizer(model, self.sample_rate)
        self.recognizer.SetWords(True)

    def _check_model(self):
        """
        Проверка наличия модели Vosk на нужном языке в каталоге приложения
        """
        if not os.path.exists(self.model_path):
            raise Exception(
                "Vosk: сохраните папку model в папку vosk\n"
                "Скачайте модель по ссылке https://alphacephei.com/vosk/models"
                            )

        isffmpeg_here = False
        for file in os.listdir(self.ffmpeg_path):
            if file.startswith('ffmpeg'):
                isffmpeg_here = True

        if not isffmpeg_here:
            raise Exception(
                "Ffmpeg: сохраните ffmpeg.exe в папку ffmpeg\n"
                "Скачайте ffmpeg.exe по ссылке https://ffmpeg.org/download.html"
                            )
        self.ffmpeg_path = self.ffmpeg_path + '/ffmpeg'

    def audio_to_text(self, audio_file_name=None) -> str:
        """
        Offline-распознавание аудио в текст через Vosk
        :param audio_file_name: str путь и имя аудио файла
        :return: str распознанный текст
        """
        if audio_file_name is None:
            raise Exception("Укажите путь и имя файла")
        if not os.path.exists(audio_file_name):
            raise Exception("Укажите правильный путь и имя файла")

        # Конвертация аудио в wav и результат в process.stdout
        process = subprocess.Popen(
            [self.ffmpeg_path,
             "-loglevel", "quiet",
             "-i", audio_file_name,          # имя входного файла
             "-ar", str(self.sample_rate),   # частота выборки
             "-ac", "1",                     # кол-во каналов
             "-f", "s16le",                  # кодек для перекодирования, у нас wav
             "-"                             # имя выходного файла нет, тк читаем из stdout
             ],
            stdout=subprocess.PIPE
                                   )

        # Чтение данных кусками и распознование через модель
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if self.recognizer.AcceptWaveform(data):
                pass

        # Возвращаем распознанный текст в виде str
        result_json = self.recognizer.FinalResult()  # это json в виде str
        result_dict = json.loads(result_json)    # это dict
        return result_dict["text"]               # текст в виде str


if __name__ == "__main__":
    # Распознование аудио
    start_time = datetime.now()
    stt = STT()
    print(stt.audio_to_text("test-1.ogg"))
    print("Время выполнения:", datetime.now() - start_time)
