# TTS-by-PHS
GTTS: 구글에서 제공하는 무료 TTS 모듈 서비스

1. 먼저 모듈을 설치해줘야 한다
``` pip install gtts ```

2. 다음과 같이 코드를 작성해서 사용한다.
```python
from gtts import gTTS

def speak(text):
	tts = gTTS(text=text, lang='ko')
	tts.save('voice.mp3')

speak("안녕하세요, 우리는 세상을 바꾸는 시간 15분을 학습 데이터 셋으로 쓸려고 합니다.")
```




참고 사이트:
* https://info-lab.tistory.com/234
* https://gtts.readthedocs.io/en/latest/index.html <- gtts 공식 문서
