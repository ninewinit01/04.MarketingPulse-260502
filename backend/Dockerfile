FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        pkg-config \
        default-libmysqlclient-dev \
        default-mysql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install \
        "django>=5.0,<5.2" \
        "djangorestframework>=3.15" \
        "django-cors-headers>=4.3" \
        "django-filter>=24.2" \
        "mysqlclient>=2.2" \
        "httpx>=0.27" \
        "python-dotenv>=1.0" \
        "gunicorn>=22" \
        "whitenoise>=6.7" \
        "colorlog>=6.8"

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
