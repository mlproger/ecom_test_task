FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
		postgresql-client \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
		pip install --no-cache-dir uv

COPY pyproject.toml /app/

RUN uv pip install . --system


COPY . /app

COPY app/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# ENTRYPOINT делает предварительную работу (миграции, ожидание БД)
ENTRYPOINT ["/app/entrypoint.sh"]

# CMD — команда по умолчанию, которая будет выполнена через exec "$@"
CMD ["uv", "run", "-m", "app.api_v1.main"]