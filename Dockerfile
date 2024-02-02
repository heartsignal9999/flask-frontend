# 기본 이미지로 Python 3.9를 사용
FROM python:3.9

# 작업 디렉토리를 /app으로 설정
WORKDIR /app

# 호스트의 현재 디렉토리를 컨테이너의 /app 디렉토리로 복사
COPY . /app

# 필요한 Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# Flask 애플리케이션 실행 명령어
CMD ["python", "main.py"]
