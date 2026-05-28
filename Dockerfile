FROM python:3.13-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/dora226/Heroku-Fixed /app
WORKDIR /app
RUN pip install --no-cache-dir --break-system-packages -U pip setuptools wheel && \
    pip install --no-cache-dir --break-system-packages -r requirements.txt

EXPOSE 8888 8080
CMD ["python3", "-m", "heroku", "--no-web"]
