## 1. 프로젝트 소개

### 프로젝트 명

> 하이브리드 지능형 가상 캐릭터 동작 생성 개발

### 개요

하이브리드 지능형 가상 캐릭터란 음성, 텍스트 등의 대화 상황을 인지하여 얻은 데이터를 학습된 모델에 적용해 자연스러운 대화 상황을 위한 음성 및 동작을 생성하고 오류 상황 검출 시 컨트롤 주체를 변경할 수 있는 캐릭터를 의미한다. 이를 구현하기 위해서는 텍스트 분석을 통한 대화 모델, 텍스트 기반 동작 생성 모델, 오류 상황 발생 시 이를 검출할 수 있는 모델까지 총 3가지 해결과제가 존재하는데 이 중 텍스트 기반 동작 생성 모델을 해결하려고 한다.

이번 과제를 통해 사용자-캐릭터 간의 상호작용 수준을 높여 가상환경상에서의 실재감과 응용서비스에 대한 사용성을 높이고자 한다. 이는 언택트 시대 주목받고 있는 가상공간에서의 자연스러운 상호작용에 이바지할 수 있을 것으로 기대한다.

### 목적

본 졸업 과제는 하이브리드 지능형 가상 캐릭터의 한글 텍스트 기반 동작 생성을 개발하는 것을 목표로 둔다.

확인할 수 있었던 텍스트 기반 동작 생성 모델 중 한글 텍스트 기반 동작 생성 모델은 찾아볼 수 없었다. 여기서 차별점을 두어 한글 텍스트 기반 동작 생성을 수행할 수 있도록 개선하여 과제를 해결하고자 한다.

## 2. 팀 소개

| 이름   | 이메일                 | 역할                                                                     |
| ------ | ---------------------- | ------------------------------------------------------------------------ |
| 박현성 | gustjd0808@pusan.ac.kr | - 학습 데이터 셋 생성에 필요한 데이터 수집<br>- 한글 Word Embedding 적용 |
| 최우창 | choiwchang@pusan.ac.kr | - 한글 텍스트 기반 TTS, STT 적용<br>- 모델 학습에 필요한 데이터 셋 생성  |
| 황원식 | fhan90521@pusan.ac.kr  | - 개발 가상환경 관리<br>- 3D Pose Estimate 기법 개발                     |

## 3. 구성도

![과제 구성도](https://user-images.githubusercontent.com/78212016/194705598-b2a33c25-5ff3-4467-b56a-17b2628795ac.png)

한글 텍스트 데이터 셋을 통해 모델을 새로 학습시키는 과정이 필요하다. 데이터 셋 구축을 위해 유튜브 영상을 활용한다. 한글을 사용하고 학습시키기에 적절한 데이터를 얻을 수 있는 유튜브 채널에서 영상과 자막을 얻는다.

인간 자세 예측(Human Pose Estimate)의 한 분야로 사진 또는 영상에서 실시간으로 사람들의 동작 포인트를 추출하는 OpenPose 라이브러리를 이용하여 2차원 Pose를 추출한다. 이후 비디오의 샷 변경을 감지하고 비디오를 별도의 클립으로 자동 분할하는 파이썬 라이브러리인 PySceneDetect를 이용해 영상을 적절한 단위 시간의 클립으로 분할한다. 학습에 있어 유효한 데이터를 만들어 내는 것이 중요하기에 분할한 클립 중 부적절한 데이터는 제거하는 과정이 필요하다.

2차원 Pose로는 입체적이고 생동감 있는 제스처를 표현하기에는 부족하기에 3차원 Pose로 표현해야 한다. 2차원 Pose를 3차원 Pose로 변환하고 해당 데이터를 모델에 학습하여 한글 텍스트 입력에 대한 제스처를 생성해보고자 한다.

![모델 구성도](https://user-images.githubusercontent.com/78212016/194705735-86af53e2-4f96-4301-9c28-e2ea7a658bc9.png)

영어 텍스트 기반이 아닌 한글 텍스트 기반으로 동작함에 있다. Text Encoding전 Word Embedding을 진행할 때 FastText Pre-Trained 한국어 모델을 사용한다.

Model에서는 Speaker ID, Speech Text Feature를 통해 Feature Vector를 생성한다. Speaker ID의 Feature와 Text의 Feature를 합쳐 하나의 Feature Vector가 만들어지는데 Speaker ID는 개별적으로 고유한 값이기에 각각의 값이 Feature가 될 수 있다.

## 4. 시연 영상

![시연 영상](https://user-images.githubusercontent.com/78212016/194741191-80ea634e-b6d0-49e3-8bd7-3ea44428e0fb.gif)

[![15조 하이브리드 지능형 가상 캐릭터 동작 생성 개발](https://img.youtube.com/vi/Ag0yV7VycPQ/0.jpg)](https://www.youtube.com/watch?v=Ag0yV7VycPQ)

## 5. 사용법

### 1. Google STT API 설정 및 Key 생성

`Google-Speech-To-Text` 디렉토리의 `README` 파일을 참고하여 Google STT API 설정 및 Key를 생성하고 생성한 키를 `Gesture-Generation-from-Multimodal-Context`의 `scripts/synthesize.py`에 환경변수로 해당 Key를 등록한다.

### 2. Model Download

`Gesture-Generation-from-Multimodal-context/data`의 디렉토릭인 `fasttext`, `h36m` README 파일 링크를 통해 모델을 다운로드합니다.

또한 `output`의 디렉토리인 `trian_h36m_gesture_autoencoder`, `train_multimodal_context`, `train_seq2seq` README 파일 링크를 통해 모델을 다운로드합니다.

### 3. 가상환경 설정

`Gesture-Generation-from-Multimodal-Context` 프로젝트 실행을 위해 필요한 파이썬 패키지들을 설치한다.

```shell
pip install -r requirements.txt
```

추가적으로 `ffmpeg` 패키지를 설치한다.

```shell
conda install -c conda-forge ffmpeg
```

### 4. 실행 및 결과 확인

`Gesture-Generation-from-Multimodal-Context`의 `scripts/synthesize.py`파일에서 examples 리스트에 동작 생성을 원하는 텍스트를 입력한다.

```
python scripts/synthesize.py from_text [trained model path] {en-male, en-female}
```

위의 명령어 실행을 통해 동작 생성 결과를 `mp4` 형식으로 얻을 수 있다. 해당 결과는 `output/generation_results` 디렉토리에서 확인할 수 있다.
