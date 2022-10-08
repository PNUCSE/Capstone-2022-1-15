from gtts import gTTS 

def speak(text): 
	tts = gTTS(text=text, lang='ko') 
	tts.save('voice.mp3') 

speak("안녕하세요, 우리는 세상을 바꾸는 시간 15분을 학습 데이터 셋으로 쓸려고 합니다.")
