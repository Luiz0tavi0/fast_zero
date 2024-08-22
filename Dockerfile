FROM python:3.12-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app/
COPY . .

RUN chmod +x /app/entrypoint.sh

RUN pip install poetry --upgrade

RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --no-dev

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "fast_zero.app:app"]