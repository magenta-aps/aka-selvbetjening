FROM python:3.12
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.1.12/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=048b95b48b708983effb2e5c935a1ef8483d9e3e \
    PYTHONUNBUFFERED=1 \
    XDG_CACHE_HOME=/home/aka/.cache

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -fsSLO https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz && \
  tar xvf wkhtmltox*.tar.xz && \
  mv wkhtmltox/bin/wkhtmlto* /usr/bin
    
# hadolint ignore=DL3008
RUN mkdir /app &&  \
    mkdir -p /log && \
    mkdir -p /var/cache/idp && \
    groupadd -g 75080 -r aka && \
    groupadd -g 75100 -r certificate_exporter && \
    useradd --create-home --uid 75080 --no-log-init --system --gid aka --groups certificate_exporter aka && \
    chown aka:aka /log && \
    chown aka:aka /var/cache/idp && \
    chmod a+w /var/cache/idp && \
    mkdir -p /ssl/sp && \
    mkdir -p /ssl/idp && \
    chmod -R a+w /home && \
    mkdir -p /upload && \
    chown aka:aka /upload

# hadolint ignore=DL3008
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        gettext libxmlsec1-dev xmlsec1 gpg libmagic1 nano logrotate postgresql-client-common postgresql-client-16 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Font cache for pdf generation
RUN mkdir -p /home/aka/.cache/fontconfig && \
    chown -R aka /home/aka/.cache

# supercronic
RUN curl -fsSLO "$SUPERCRONIC_URL" && \
    echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - && \
    chmod +x "$SUPERCRONIC" && \
    mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" && \
    ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

ARG COMMIT_TAG
ENV COMMIT_TAG=${COMMIT_TAG:-HEAD}

COPY docker/crontab /crontab
COPY akap/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt && rm /app/requirements.txt
COPY ./docker/entrypoint.sh /entrypoint.sh
COPY --chown=aka:aka ./akap /app

# Include self-signed certificates for testing in pipeline
COPY dev-environment/cert/sp/selfsigned.* /ssl/sp/
COPY dev-environment/cert/idp/selfsigned.* /ssl/idp/

RUN mkdir /app/static && \
    chown -R aka:aka /entrypoint.sh /app/static

USER aka
WORKDIR /app
RUN django-admin compilemessages
ENV HOME=/home
VOLUME /var/cache/idp
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]

# Run collectstatic
COPY --chown=aka:aka ./dev-environment/akap.env /tmp/akap.env
# hadolint ignore=SC1091
RUN chown aka:aka /tmp/akap.env && \
    set -a && \
    source /tmp/akap.env && \
    set +a && \
    python manage.py collectstatic --no-input --clear && \
    rm /tmp/akap.env

CMD ["gunicorn","-b","0.0.0.0:8000","project.wsgi:application","-w 4","--timeout", "240", "--error-logfile", "-","--capture-output"]
