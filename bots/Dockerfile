FROM python:3.11-slim

WORKDIR /app

# Install ffmpeg and required libraries for audio playback
RUN apt-get update && \
    apt-get install -y ffmpeg libffi-dev python3-dev git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Verify ffmpeg installation
    ffmpeg -version

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY akatsuki_bot.py .
COPY akatsuki_theme.mp3 .

CMD ["python", "-u", "akatsuki_bot.py"]