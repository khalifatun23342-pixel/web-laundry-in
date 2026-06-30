FROM python:3.11-slim

WORKDIR /app

# Instal dependensi sistem dasar yang dibutuhkan Reflex
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Salin requirements dan instal semua library Python proyekmu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh file kodinganmu dari laptop ke dalam server cloud
COPY . .

# Kompilasi tampilan Frontend Reflex
RUN reflex export --frontend-only --no-zip

# Jalankan aplikasi secara simultan di port standar Hugging Face (7860)
CMD ["reflex", "run", "--env", "prod", "--frontend-port", "7860", "--backend-port", "8000"]