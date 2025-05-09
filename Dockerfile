FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    gcc \
    python3-dev \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libasound-dev \
    wget \
    make \
    unzip && \
    rm -rf /var/lib/apt/lists/*

# Build and install PortAudio from source
RUN wget http://www.portaudio.com/archives/pa_stable_v190700_20210406.tgz && \
    tar -xzf pa_stable_v190700_20210406.tgz && \
    cd portaudio && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    cd .. && \
    rm -rf portaudio pa_stable_v190700_20210406.tgz

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

ENV TESSERACT_PATH=/usr/bin/tesseract

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
