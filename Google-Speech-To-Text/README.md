## API 설정 및 Key 생성
1. Google console에서 API 및 서비스의 라이브러리로 들어간다.
2. Google STT 검색 후 사용을 선택한다.
3. 사용자 인증 정보에 들어가서 서비스 계정을 통해 사용자 인증 정보를 생성한다.
4. 입력 사항을 입력 후 키 추가를 통해 새 키를 생성한다.
5. JSON 키를 통해 환경 변수를 설정한다.

### 맥 환경설정
```shell
vi ~/.zshrc

export GOOGLE_APPLICATION_CREDENTIALS="JSON 파일 경로"

source ~/.zshrc
```

## 가상환경 설정
- `Conda`를 사용하기 위해 프로젝트 생성 시 환경을 `Conda`로 지정
- 원하는 파이썬 버전의 가상환경을 생성하고 활성화 한 뒤 모듈을 설치한다.
```shell
pip install --upgrade google-cloud-speech
```

## 참고링크
https://cloud.google.com/speech-to-text/docs/libraries?hl=ko#client-libraries-install-python  
https://cloud.google.com/speech-to-text/docs/basics?hl=ko#sample-rates