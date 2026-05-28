FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends git openssh-client curl && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/dora226/Heroku-Fixed /app
WORKDIR /app
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

EXPOSE 8888
CMD ["python", "-m", "heroku", "--root", "--port", "8888"]
