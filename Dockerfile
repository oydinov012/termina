# ==============================================================================
# Python-ning barqaror va yengil build tizimidan foydalanamiz
# ==============================================================================
FROM python:3.12-slim

# Terminal loglarini real vaqtda ko'rish va .pyc fayllar yaratmaslik sozlamalari
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Tizim uchun kerakli paketlarni o'rnatamiz
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Birinchi requirements.txt o'zini o'rnatamiz (Docker keshlashidan unumli foydalanish uchun)
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Loyihaning kodlarini (src papkasini) konteyner ichiga nusxalaymiz
COPY src/ /app/

# Static va Media fayllar uchun papkalar yaratib qo'yamiz
RUN mkdir -p /app/staticfiles /app/media
