import os
import io
from google.cloud import speech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\makem\\ProjectHcb\\Gesture-Generation-from-Trimodal-Context\\scripts\\airy-shuttle-361110-4d39350b7ac6.json'

def align_words():
    # resample audio to 8K

    client = speech.SpeechClient()

    with io.open('./temp.wav', 'rb') as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000,
        language_code="en-US",
        enable_word_time_offsets=True,
    )

    response = client.recognize(config=config, audio=audio)

    words_with_timestamps = []

    for result in response.results:
        alternative = result.alternatives[0]

        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            words_with_timestamps.append([word, start_time.total_seconds(), end_time.total_seconds()])

    return words_with_timestamps

print(align_words())