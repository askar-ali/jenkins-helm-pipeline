FROM python:3.12-slim

ARG APP_VERSION=dev
ARG VCS_REF=unknown
LABEL org.opencontainers.image.title="sample" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}"

ENV PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION}

RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
WORKDIR /srv
COPY app/server.py .
USER 10001
EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/healthz').status==200 else 1)"

CMD ["python", "server.py"]
