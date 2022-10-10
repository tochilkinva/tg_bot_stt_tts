# -*- coding: utf8 -*-
"""
Конвертация текст -> wav/ogg, wav/ogg -> текст
"""
import json  # работа с json-файлами и json-строками
import os
import re
# import torchaudio
import subprocess
from datetime import datetime

import torch
from num2words import num2words
from vosk import KaldiRecognizer, Model  # оффлайн-распознавание от Vosk


class STT:
    """
    Класс для распознования аудио через Vosk и преобразования его в текст.
    Поддерживаются форматы аудио: wav, ogg
    """
    default_init = {
        "model_path": "models/vosk/model",        # путь к STT модели Vosk
        "sample_rate": 16000,
        "ffmpeg_path": "models/vosk/ffmpeg.exe"   # путь к ffmpeg
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

        if not os.path.isfile(self.ffmpeg_path):
            raise Exception(
                "Ffmpeg: сохраните ffmpeg.exe в папку ffmpeg\n"
                "Скачайте ffmpeg.exe по ссылке https://ffmpeg.org/download.html"
                            )

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
             "-"
             ],                           # имя выходного файла нет, тк читаем из stdout
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


class TTS:
    """
    Класс для преобразования текста в аудио.
    Поддерживаются форматы аудио: wav, ogg
    """
    default_init = {
        "sample_rate": 24000,
        "device_init": "cpu",
        "threads": 4,
        "speaker_voice": "kseniya",
        "model_path": "models/silero/model.pt",     # путь к TTS модели Silero
        "ffmpeg_path": "models/silero/ffmpeg.exe"   # путь к ffmpeg
    }

    def __init__(
        self,
        sample_rate=None,
        device_init=None,
        threads=None,
        speaker_voice=None,
        model_path=None,
        ffmpeg_path=None
    ) -> None:
        """
        Настройка модели Silero для преобразования текста в аудио.

        :arg sample_rate: int       # 8000, 24000, 48000 - качество звука
        :arg device_init: str       # "cpu", "gpu"(для gpu нужно ставить другой torch)
        :arg threads: int           # количество тредов, например, 4
        :arg speaker_voice: str     # диктор "aidar", "baya", "kseniya", "xenia", "random"(генерит голос каждый раз, долго)
        :arg model_path: str        # путь до модели silero
        :arg ffmpeg_path: str       # путь к ffmpeg
        """
        self.sample_rate = sample_rate if sample_rate else TTS.default_init["sample_rate"]
        self.device_init = device_init if device_init else TTS.default_init["device_init"]
        self.threads = threads if threads else TTS.default_init["threads"]
        self.speaker_voice = speaker_voice if speaker_voice else TTS.default_init["speaker_voice"]
        self.model_path = model_path if model_path else TTS.default_init["model_path"]
        self.ffmpeg_path = ffmpeg_path if ffmpeg_path else TTS.default_init["ffmpeg_path"]

        self._check_model()

        device = torch.device(self.device_init)
        torch.set_num_threads(self.threads)
        self.model = torch.package.PackageImporter(self.model_path).load_pickle("tts_models", "model")
        self.model.to(device)

    def _check_model(self):
        """
        Проверка наличия модели Silero на нужном языке в каталоге приложения
        """
        if not os.path.isfile(self.model_path):
            torch.hub.download_url_to_file(
                "https://models.silero.ai/models/tts/ru/v3_1_ru.pt",
                self.model_path
                                           )

        if not os.path.isfile(self.ffmpeg_path):
            raise Exception(
                "Ffmpeg: сохраните ffmpeg.exe в папку ffmpeg\n"
                "Скачайте ffmpeg.exe по ссылке https://ffmpeg.org/download.html"
                            )

    def wav_to_ogg(
        self,
        in_filename: str,
        out_filename: str = "test_1.ogg"
                   ) -> str:
        """
        Конвертирует аудио в ogg формат.

        :arg in_filename:  str  # путь до входного файла
        :arg out_filename: str  # путь до выходного файла
        :return: str  # путь до выходного файла
        """
        if not in_filename:
            raise Exception("Укажите путь и имя файла in_filename")

        if os.path.exists(out_filename):
            os.remove(out_filename)

        command = [
            self.ffmpeg_path,
            "-loglevel", "quiet",
            "-i", in_filename,
            "-acodec", "libvorbis",
            out_filename
        ]
        proc = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
                                )
        proc.wait()
        return out_filename

    def ogg_to_wav(
        self,
        in_filename: str,
        out_filename: str = "test_1.wav"
                   ) -> str:
        """
        Конвертирует аудио в wav формат.

        :arg in_filename:  str  # путь до входного файла
        :arg out_filename: str  # путь до выходного файла
        :return: str  # путь до выходного файла
        """
        if not in_filename:
            raise Exception("Укажите путь и имя файла in_filename")

        if os.path.exists(out_filename):
            os.remove(out_filename)

        command = [
            self.ffmpeg_path,
            "-i", in_filename,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            out_filename
        ]
        proc = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
                                )
        proc.wait()
        return out_filename

    def _get_wav(self, text: str, speaker_voice=None, sample_rate=None) -> str:
        """
        Конвертирует текст в wav файл

        :arg text:  str  # текст до 1000 символов
        :arg speaker_voice:  str  # голос диктора
        :arg sample_rate: str  # качество выходного аудио
        :return: str  # путь до выходного файла
        """
        # Удаляем файл чтобы все хорошо работало
        if os.path.exists("test.wav"):
            os.remove("test.wav")

        if text is None:
            raise Exception("Передайте текст")

        if speaker_voice is None:
            speaker_voice = self.speaker_voice

        if sample_rate is None:
            sample_rate = self.sample_rate

        # Сохранение результата в файл test.wav
        return self.model.save_wav(
            text=text,
            speaker=speaker_voice,
            sample_rate=sample_rate
        )

    def _get_ogg(self, text: str, speaker_voice=None, sample_rate=None) -> str:
        """
        Конвертирует текст в ogg файл

        :arg text:  str  # текст до 1000 символов
        :arg speaker_voice:  str  # голос диктора
        :arg sample_rate: str  # качество выходного аудио
        :return: str  # путь до выходного файла
        """
        # Конвертируем текст в wav, возвращаем путь до wav
        wav_audio_path = self._get_wav(text, speaker_voice, sample_rate)

        # Конвертируем wav в ogg, возвращаем путь до ogg
        ogg_audio_path = self.wav_to_ogg(wav_audio_path)

        if os.path.exists(wav_audio_path):
            os.remove(wav_audio_path)

        return ogg_audio_path

    def _nums_to_text(self, text: str) -> str:
        """
        Преобразует числа в буквы: 1 -> один, 23 -> двадцать три.
        :arg text: str
        :return: str
        """
        return re.sub(
            r"(\d+)",
            lambda x: num2words(int(x.group(0)), lang="ru"),
            text)

    def _merge_audio_n_to_1(
        self,
        in_filenames: list,
        out_filename: str = "test_n_1.tmp"
                            ) -> str:
        """
        Объединит несколько файлов в один файл без перекодирования.
        Файлы должны быть одинакового формата.

        :arg in_filenames: list[str]    # список файлов для склеивания
        :arg out_filename: str          # имя выходного файла
        :return out_filename: str       # имя выходного файла
        """
        if not in_filenames:
            raise Exception("Укажите пути и имя файла in_filenames")

        if os.path.exists(out_filename):
            os.remove(out_filename)

        # Объединит несколько файлов в один файл без перекодирования
        # Пример: ffmpeg -i "concat:01.ogg|02.ogg|03.ogg" -acodec copy output.ogg
        command = [
            self.ffmpeg_path,
            "-i", "concat:" + "|".join(in_filenames),
            "-acodec", "copy",
            out_filename
        ]
        proc = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proc.wait()

        return out_filename

    def _rename_file(self, in_filename: str, out_filename: str) -> str:
        """
        Переименует in_filename файл в out_filename.

        :arg in_filename: str   # имя входного файла
        :arg out_filename: str  # имя выходного файла
        :return: str            # имя выходного файла
        """
        if in_filename is None or out_filename is None:
            raise Exception("Передайте названия входного и выходного файла")

        if os.path.exists(out_filename):
            os.remove(out_filename)
        os.rename(in_filename, out_filename)
        return out_filename

    def text_to_ogg(self, text: str, out_filename: str = None) -> str:
        """
        Конвертирует текст в файл ogg.
        Модель игнорирует латиницу, но поддерживает цифры числами.

        :arg text: str  # текст кирилицей
        :return: str    # имя выходного файла
        """
        if text is None:
            raise Exception("Передайте текст")

        # Делаем числа буквами
        text = self._nums_to_text(text)

        # Генерируем ogg если текст < 1000 символов
        if len(text) < 1000:
            # Возвращаем путь до ogg
            ogg_audio_path = self._get_ogg(text)

            if out_filename is None:
                return ogg_audio_path

            return self._rename_file(ogg_audio_path, out_filename)

        # Разбиваем текст, конвертируем и склеиваем аудио в один файл
        texts = [text[x:x+990] for x in range(0, len(text), 990)]
        files = []
        for index in range(len(texts)):
            # Конвертируем текст в ogg, возвращаем путь до ogg
            ogg_audio_path = self._get_ogg(texts[index])
            # Переименовываем чтобы не затереть файл
            new_ogg_audio_path = f"{index}_{ogg_audio_path}"
            os.rename(ogg_audio_path, new_ogg_audio_path)
            # Добавляем новый файл в список
            files.append(new_ogg_audio_path)

        # Склеиваем все ogg файлы в один
        ogg_audio_path = self._merge_audio_n_to_1(files, out_filename="test_n_1.ogg")
        # Удаляем временные файлы
        [os.remove(file) for file in files]

        if out_filename is None:
            return ogg_audio_path

        return self._rename_file(ogg_audio_path, out_filename)

    def text_to_wav(self, text: str, out_filename: str = None) -> str:
        """
        Конвертирует текст в файл wav.
        Модель игнорирует латиницу, но поддерживает цифры числами.

        :arg text: str  # текст кирилицей
        :return: str    # имя выходного файла
        """
        if text is None:
            raise Exception("Передайте текст")

        # Делаем числа буквами
        text = self._nums_to_text(text)

        # Передаем текст целиком
        if len(text) < 1000:
            # Конвертируем текст в wav, возвращаем путь до wav
            wav_audio_path = self._get_wav(text)

            if out_filename is None:
                return wav_audio_path

            return self._rename_file(wav_audio_path, out_filename)

        # Разбиваем текст, конвертируем и склеиваем аудио в один файл
        texts = [text[x:x+990] for x in range(0, len(text), 990)]
        files = []
        for index in range(len(texts)):
            # Конвертируем текст в wav, возвращаем путь до wav
            wav_audio_path = self._get_wav(texts[index])
            # Переименовываем чтобы не затереть файл
            new_wav_audio_path = f"{index}_{wav_audio_path}"
            os.rename(wav_audio_path, new_wav_audio_path)
            # Добавляем файл в список
            files.append(new_wav_audio_path)

        # Склеиваем все wav файлы в один
        wav_audio_path = self._merge_audio_n_to_1(files, out_filename="test_n_1.wav")
        # Удаляем временные файлы
        [os.remove(file) for file in files]

        if out_filename is None:
            return wav_audio_path

        return self._rename_file(wav_audio_path, out_filename)

# region Может не работать!
    # def get_ogg(self, out_filename="test_123.ogg", text=None, speaker_voice=None, sample_rate=None) -> str:
    #     """
    #     Сохранение результата в файл ogg test_123.ogg
    #     Не всегда работает!!!
    #     """
    #     if os.path.exists(out_filename):
    #         os.remove(out_filename)

    #     if text is None:
    #         text="Тест звука! Один, два, три! 4 5 6"

    #     if speaker_voice is None:
    #         speaker_voice=self.speaker_voice

    #     if sample_rate is None:
    #         sample_rate=self.sample_rate

    #     # Сохранение результата в файл ogg Не всегда работает!
    #     audio_tenzor = self.model.apply_tts(
    #         text=text,
    #         speaker=speaker_voice,
    #         sample_rate=sample_rate
    #     )
    #     torchaudio.save(
    #         out_filename,
    #         audio_tenzor.unsqueeze(0),
    #         sample_rate=sample_rate,
    #         format="ogg"
    #     )
    #     return out_filename

    # def get_bytes(self, text=None, speaker_voice=None, sample_rate=None) -> str:
    #     """
    #     Сохранение результата в io.BytesIO()
    #     Не проверял!!!
    #     """
    #     import io

    #     if text is None:
    #         text="Тест звука! Один, два, три! 4 5 6"

    #     if speaker_voice is None:
    #         speaker_voice=self.speaker_voice

    #     if sample_rate is None:
    #         sample_rate=self.sample_rate

    #     audio_tenzor = self.model.apply_tts(
    #         text=text,
    #         speaker=speaker_voice,
    #         sample_rate=sample_rate
    #     )

    #     # Сохранение результата в файл BytesIO
    #     buffer_ = io.BytesIO()
    #     torchaudio.save(buffer_,
    #                     audio_tenzor.unsqueeze(0),
    #                     sample_rate,
    #                     format="ogg")
    #     buffer_.seek(0)
    #     return buffer_
# endregion


if __name__ == "__main__":

    # Генерирование аудио из текста
    start_time = datetime.now()
    tts = TTS()
    print(tts.text_to_ogg("Привет,Хабр! Тэст 1 2 три четыре", "habr1.ogg"))
    print(tts.text_to_wav("Тэст! Как меня слышно? Пыш-пыш. Прием!", "habr2.wav"))
    print(tts.text_to_ogg("Слышу хорошо! Пыш-пыш.", "habr3.ogg"))
    print("Время выполнения:", datetime.now() - start_time)

    # Распознование аудио
    start_time = datetime.now()
    stt = STT()
    print(stt.audio_to_text("habr1.ogg"))
    print(stt.audio_to_text("habr2.wav"))
    print(stt.audio_to_text("habr3.ogg"))
    print("Время выполнения:", datetime.now() - start_time)
