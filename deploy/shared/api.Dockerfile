# syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /app
COPY services/api/requirements.lock.txt /app/requirements.lock.txt
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    pip install --no-cache-dir -r requirements.lock.txt
COPY services/api/khohoc /app/services/api/khohoc
COPY data/library /app/data/library
# Read-only curriculum, source mappings and Vietnamese topic labels used at runtime.
# Copying metadata does not import, approve or publish any database content.
COPY data/seeds/textbook_units.json data/seeds/source_practice_map.json data/seeds/exams.json data/seeds/language_exams.json data/seeds/curriculum_exams.json data/seeds/subject_exams.json /app/data/seeds/
ENV PYTHONPATH=/app/services/api PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --uid 10001 --create-home api \
    && chmod -R a+rX /app/services /app/data
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "khohoc.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "172.29.111.2", "--no-access-log"]
