FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip --no-cache-dir install poetry && poetry config virtualenvs.create false \
        && poetry install --no-interaction --no-root

COPY . .

CMD ["python","bot.py"]
