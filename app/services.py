# main.py
import os
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

# Mel 범위로 변환
def get_mel_spectrogram(wave_form, sample_rate, n_mels=96, frame_length=0.025, frame_stride=0.01):
    """
    Convert an audio waveform to a Mel spectrogram.

    :param wave_form: NumPy array of audio waveform.
    :param sample_rate: Sampling rate of the audio.
    :param n_mels: Number of Mel bands to generate.
    :param frame_length: Length of each frame in seconds.
    :param frame_stride: Stride between successive frames in seconds.
    :return: Mel spectrogram (2D NumPy array).
    """
    # Calculate the number of samples per frame and stride
    win_length = int(round(sample_rate * frame_length))
    hop_length = int(round(sample_rate * frame_stride))

    # Calculate the number of FFT components (n_fft) as the next power of two from win_length
    n_fft = 2 ** int(np.ceil(np.log2(win_length)))

    # Compute the Mel spectrogram
    mel_spectrogram = librosa.feature.melspectrogram(y=wave_form, sr=sample_rate, n_fft=n_fft,
                                                     hop_length=hop_length, win_length=win_length,
                                                     n_mels=n_mels)
    return mel_spectrogram

# 스펙트로그램 그리고 저장하기
def draw_mel_square_spec_and_save(mel, sample_rate, frame_stride, save_path, filename):
    """
    Draw a square Mel spectrogram and save it to a file.

    :param mel: Mel spectrogram (2D NumPy array).
    :param sample_rate: Sampling rate of the original audio.
    :param frame_stride: Stride between successive frames in seconds.
    :param save_path: Path to save the spectrogram image.
    :param filename: Filename for saving the image.
    """
    # Convert Mel spectrogram to Decibel scale
    S_dB = librosa.power_to_db(mel, ref=np.max)

    # Calculate hop length for time alignment
    hop_length = int(round(sample_rate * frame_stride))

    # Calculate the total duration of the audio in seconds
    total_duration_sec = mel.shape[1] * frame_stride

    # Calculate the width of the figure (1 inch per second)
    fig_width = total_duration_sec  # 1 second = 1 inch

    # Create a figure with a fixed height of 3 inches and a variable width
    fig, ax = plt.subplots(figsize=(fig_width, 3), dpi=95)  # 3 inches tall, variable width

    # Display the Mel spectrogram
    librosa.display.specshow(S_dB, sr=sample_rate, hop_length=hop_length)
    ax.set_aspect('auto')

    # Save and display the spectrogram image
    print(f"{filename} spectrogram saved")
    plt.tight_layout()
    full_save_path = os.path.join(save_path, filename)
    plt.savefig(full_save_path, bbox_inches='tight', pad_inches=0)
    plt.colorbar(format='%+2.0f dB')
    plt.show()
