FROM python:3.12-slim
WORKDIR /app
COPY services/api/requirements.lock.txt /app/requirements.lock.txt
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY services/api /app/services/api
COPY data/seeds /app/data/seeds
COPY data/library /app/data/library
ENV PYTHONPATH=/app/services/api KHOHOC_MODE=development KHOHOC_DATABASE_URL=sqlite:////tmp/khohoc-preview.db PYTHONDONTWRITEBYTECODE=1
RUN useradd --create-home --uid 10001 preview
USER preview
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn khohoc.phone_preview:create_preview --factory --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --no-access-log"]
