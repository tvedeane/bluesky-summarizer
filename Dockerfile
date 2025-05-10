# Wybierz oficjalny obraz Pythona jako bazę
FROM python:3.11-slim

# Ustaw zmienne środowiskowe
ENV POETRY_VERSION=1.8.2 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Zainstaluj Poetry
RUN pip install --upgrade pip \
    && pip install poetry==$POETRY_VERSION

# Utwórz katalog na aplikację
WORKDIR /app

# Skopiuj pliki projektu
COPY pyproject.toml poetry.lock* /app/

# Zainstaluj zależności (bez środowiska wirtualnego)
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Skopiuj resztę plików projektu
COPY . /app

# Otwórz port aplikacji Flask
EXPOSE 5000

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=5000"]

