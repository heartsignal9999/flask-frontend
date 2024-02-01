from pydub import AudioSegment
import os

def convert_to_wav(source_path, target_path):
    """
    Converts an audio file to WAV format.

    :param source_path: Path to the source audio file.
    :param target_path: Path to save the converted WAV file.
    """
    # PyDub를 사용하여 오디오 파일을 WAV 형식으로 변환합니다.
    audio = AudioSegment.from_file(source_path)
    audio.export(target_path, format='wav')