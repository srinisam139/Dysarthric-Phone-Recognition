import librosa
import numpy as np
import librosa.display
import soundfile as sf
from scipy.io import wavfile

audio_directory = "/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/matrix/audio/"
a1_person_name = 'M01'
a1_session_name = 'Session2'
a1_file_number = '0020'

a2_person_name = 'MC01'
a2_session_name = 'Session1'
a2_file_number = '0010'

y1, sr1 = librosa.load(f'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Dataset/M/{a1_person_name}/{a1_session_name}/wav_headMic/{a1_file_number}.wav')

start_time = 0.559
end_time = 1.105
# Trim the audio
y_trimmed = y1[int(start_time * sr1):int(end_time * sr1)]

sf.write(audio_directory+f"{a1_person_name}_{a1_session_name}_{a1_file_number}_trimmed_audio.wav", y_trimmed, sr1)

y2, sr2 = librosa.load(f'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Dataset/MC/{a2_person_name}/{a2_session_name}/wav_headMic/{a2_file_number}.wav')

start_time = 1.6425
end_time = 1.8825
# Trim the audio
y_trimmed = y1[int(start_time * sr1):int(end_time * sr1)]

sf.write(audio_directory+f"{a2_person_name}_{a2_session_name}_{a2_file_number}_trimmed_audio.wav", y_trimmed, sr1)

x_fn = audio_directory+f"{a1_person_name}_{a1_session_name}_{a1_file_number}_trimmed_audio.wav"
f_s, x = wavfile.read(x_fn)
print(f_s)
# Mel-scale spectrogram
n_fft = int(0.025*f_s)
win_length = int(0.015*1000) # 15 ms
hop_length = int(0.05*1000) # 5 ms
n_mels = 100

mel_spec_x = librosa.feature.melspectrogram(
    y=x/1.0, sr=f_s, n_mels=40,
    n_fft=n_fft, hop_length=hop_length, win_length=win_length
    )
log_mel_spec_x = np.log(mel_spec_x)