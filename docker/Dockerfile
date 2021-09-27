FROM python:3.6
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.1.12/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=048b95b48b708983effb2e5c935a1ef8483d9e3e
    PYTHONUNBUFFERED=1
# hadolint ignore=DL3008
RUN mkdir /backend && mkdir -p /var/log/aka && \
apt-get update && apt-get install -y --no-install-recommends \
 gettext wkhtmltopdf libxmlsec1-dev gpg\
 && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -fsSLO "$SUPERCRONIC_URL" \
 && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
 && chmod +x "$SUPERCRONIC" \
 && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
 && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic
COPY docker/crontab /crontab
COPY backend/requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir -r /backend/requirements.txt
COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./backend /backend
WORKDIR /backend
RUN django-admin compilemessages
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn","-b","0.0.0.0:8000","project.wsgi:application","-w 4","--timeout 240", "--error-logfile", "-","--capture-output"]
