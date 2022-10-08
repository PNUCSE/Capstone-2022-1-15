# Imports the Google Cloud client library
import os
from google.cloud import speech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'json 경로'

# Instantiates a client
client = speech.SpeechClient()

# The name of the audio file to transcribe
# wav 파일도 지원 가능
# google cloud storage 버킷에 올린 경로
gcs_uri= "파일 경로"

audio = speech.RecognitionAudio(uri=gcs_uri)

config = speech.RecognitionConfig(
    # 오디오 인코딩 체계 선택, FLAC 및 WAV 파일의 경우 encoding은 필수가 아닌 선택 사항
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    # 오디오 샘플링 레이트를 지정, FLAC 및 WAV 파일의 경우 encoding은 필수가 아닌 선택 사항
    # 8000Hz ~ 48000Hz 사이의 샘플링 레이트가 지원, 16000Hz로 오디오 캡처하는 것을 권장
    sample_rate_hertz=8000,
    # 제공된 오디오의 음성 인식에 사용할 언어와 리전/지역을 포함
    language_code="en-US",
    # 타임스탬프를 찍을 수 있게 허용
    enable_word_time_offsets=True,
)

# Detects speech in the audio file
response = client.recognize(config=config, audio=audio)

for result in response.results:
    print(result)
    alternative = result.alternatives[0]
    print("Transcript: {}".format(alternative.transcript))

    for word_info in alternative.words:
        word = word_info.word
        start_time = word_info.start_time
        end_time = word_info.end_time

        print(
            f"Word: {word}, start_time: {start_time.total_seconds()}, end_time: {end_time.total_seconds()}"
        )